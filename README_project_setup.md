# AI Legal Information Assistant – Project Setup and Testing

## Project files

- `app.py` – Streamlit interface and 11 navigation modules.
- `chatbot.py` – TF-IDF retrieval and Gemini response generation (existing project file).
- `database.py` – SQLite chat history and feedback (existing project file).
- `document_tools.py` – PDF text extraction and AI-summary helper.
- `legal_data.json` – starter legal information records (existing project file).
- `test_document_tools.py` – automated unit tests for PDF handling and summary integration.
- `.env` – Gemini API key; keep private and never upload to GitHub.
- `legal_assistant.db` – generated SQLite database; do not commit it.

## Setup in VS Code (Windows)

Open the project folder in VS Code. Activate your existing virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Install the updated requirements:

```powershell
python -m pip install -r requirements_updated.txt
```

Keep your existing `.env` file in the project root. It should contain:

```text
GEMINI_API_KEY=your_existing_key
```

Do not share the key or commit `.env`.

## Run the app

```powershell
streamlit run app.py
```

## Run automated tests

```powershell
python -m unittest -v test_document_tools.py
```

The tests check empty/invalid uploads, size validation, text extraction, scanned-PDF handling, blank summaries, and the chatbot-summary handoff. They mock the PDF reader/Gemini-facing chatbot call, so they do not spend API credits or require an internet connection.

## Manual application test checklist

1. Open Dashboard: confirm 11 modules and legal record count appear.
2. Open AI Legal Chatbot: ask `What is an FIR?`; confirm an answer appears and chat history is saved.
3. Open Indian Laws: search `theft`; confirm matching records appear.
4. Open PDF Legal Document Assistant: upload a small text-based PDF; preview extracted text; click Generate AI Summary; download the summary.
5. Upload a `.txt` file renamed as `.pdf`: it should be rejected as an invalid PDF.
6. Upload a scanned/image-only PDF: it should show a message that selectable text was not found.
7. Open Legal Document Generator: enter the required fields and download the draft.
8. Visit the remaining legal modules and verify their content and official-resource links render.
9. Restart Streamlit and check saved chat history again.

## PDF feature limits

- PDF must be no larger than 10 MB and contain no more than 30 pages.
- Password-protected PDFs are rejected.
- This version extracts selectable text only. OCR for scanned PDFs is not included.
- Summarization is limited to the first 18,000 extracted characters. The UI warns if the text was shortened.
- Do not upload confidential or sensitive documents unless you have permission and understand that the extracted text is sent to the configured AI service for summarization.

## Legal disclaimer

This is an academic awareness prototype, not a law firm or a substitute for an advocate. Legal information can be incomplete or outdated. Verify laws and procedures using current official sources and consult a qualified advocate for advice about an individual case.
