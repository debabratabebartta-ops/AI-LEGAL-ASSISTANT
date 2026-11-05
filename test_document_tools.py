import unittest
import sys
import types
from unittest.mock import MagicMock, patch

# Keep these unit tests independent of the real Gemini/chatbot module.
if "chatbot" not in sys.modules:
    chatbot_stub = types.ModuleType("chatbot")
    chatbot_stub.generate_legal_response = lambda prompt: "Mock summary"
    sys.modules["chatbot"] = chatbot_stub

import document_tools


class PDFExtractionTests(unittest.TestCase):
    def test_rejects_empty_upload(self):
        with self.assertRaisesRegex(ValueError, "empty or invalid"):
            document_tools.extract_pdf_text(b"")

    def test_rejects_non_pdf_file(self):
        with self.assertRaisesRegex(ValueError, "valid PDF"):
            document_tools.extract_pdf_text(b"not a pdf")

    def test_rejects_file_over_size_limit(self):
        with patch.object(document_tools, "MAX_PDF_BYTES", 5):
            with self.assertRaisesRegex(ValueError, "10 MB"):
                document_tools.extract_pdf_text(b"%PDF-" + b"x" * 10)

    @patch("document_tools.PdfReader")
    def test_extracts_text_from_pdf(self, reader_class):
        page1, page2 = MagicMock(), MagicMock()
        page1.extract_text.return_value = "Agreement between A and B"
        page2.extract_text.return_value = "Payment is due on the stated date"
        reader = MagicMock()
        reader.is_encrypted = False
        reader.pages = [page1, page2]
        reader_class.return_value = reader
        text, count = document_tools.extract_pdf_text(b"%PDF-1.4 test")
        self.assertEqual(count, 2)
        self.assertIn("Agreement between A and B", text)
        self.assertIn("Payment is due", text)

    @patch("document_tools.PdfReader")
    def test_rejects_scanned_or_textless_pdf(self, reader_class):
        page = MagicMock()
        page.extract_text.return_value = ""
        reader = MagicMock()
        reader.is_encrypted = False
        reader.pages = [page]
        reader_class.return_value = reader
        with self.assertRaisesRegex(ValueError, "No selectable text"):
            document_tools.extract_pdf_text(b"%PDF-1.4 test")

    @patch("document_tools.chatbot.generate_legal_response")
    def test_summary_uses_chatbot_and_returns_truncation_flag(self, generate):
        generate.return_value = "Document overview: Test summary"
        result, truncated = document_tools.summarize_legal_document("Sample legal text")
        self.assertEqual(result, "Document overview: Test summary")
        self.assertFalse(truncated)
        generate.assert_called_once()

    def test_summary_rejects_blank_text(self):
        with self.assertRaisesRegex(ValueError, "no document text"):
            document_tools.summarize_legal_document("   ")


if __name__ == "__main__":
    unittest.main(verbosity=2)
