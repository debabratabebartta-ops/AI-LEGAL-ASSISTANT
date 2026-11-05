import os
import re
from datetime import date

import streamlit as st
from dotenv import load_dotenv

import chatbot
import database
import document_tools

# ============================================================
# AI LEGAL INFORMATION ASSISTANT
# Single-file Streamlit application
# ============================================================

st.set_page_config(
    page_title="AI Legal Information Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = "gemini-3.5-flash-lite"

# Starter legal information records.
# Verify and expand these records from official sources before real-world use.
LEGAL_DATA = [
    {
        "category": "Criminal Law",
        "question": "What is theft?",
        "keywords": ["theft", "stealing", "stolen property", "mobile theft"],
        "answer": (
            "Theft generally means dishonestly taking movable property "
            "out of another person's possession without consent. The facts "
            "and intention are important."
        ),
        "law": "Bharatiya Nyaya Sanhita, 2023",
        "section": "Section 303",
        "source": "https://www.indiacode.nic.in/"
    },
    {
        "category": "Criminal Procedure",
        "question": "What is an FIR?",
        "keywords": ["fir", "police complaint", "first information report", "report crime"],
        "answer": (
            "FIR means First Information Report. Section 173 of the "
            "Bharatiya Nagarik Suraksha Sanhita, 2023 deals with information "
            "relating to cognizable offences."
        ),
        "law": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section": "Section 173",
        "source": "https://www.indiacode.nic.in/"
    },
    {
        "category": "Cybercrime",
        "question": "What should I do about online financial fraud?",
        "keywords": ["online fraud", "cyber fraud", "upi fraud", "online scam", "money stolen"],
        "answer": (
            "Contact your bank or payment provider immediately. Report "
            "financial cyber fraud by calling 1930 and through the National "
            "Cyber Crime Reporting Portal. Preserve transaction details "
            "and other evidence."
        ),
        "law": "Applicable Indian cyber laws",
        "section": "Depends on the facts of the incident",
        "source": "https://cybercrime.gov.in/"
    },
    {
        "category": "Fundamental Rights",
        "question": "What is the Right to Equality?",
        "keywords": ["equality", "equal rights", "discrimination", "article 14"],
        "answer": (
            "The Right to Equality is protected by Articles 14 to 18 of "
            "the Constitution of India. Article 14 guarantees equality "
            "before the law and equal protection of the laws."
        ),
        "law": "Constitution of India",
        "section": "Articles 14 to 18",
        "source": "https://www.indiacode.nic.in/"
    },
    {
        "category": "Consumer Rights",
        "question": "What can I do if I receive a defective product?",
        "keywords": ["defective product", "consumer complaint", "refund", "replacement", "damaged product"],
        "answer": (
            "Keep the invoice, order details, photographs and communication "
            "with the seller. Raise a complaint with the seller or platform. "
            "You may also contact the National Consumer Helpline."
        ),
        "law": "Consumer Protection Act, 2019",
        "section": "Applicable provisions depend on the complaint",
        "source": "https://consumerhelpline.gov.in/"
    },
    {
        "category": "Women's Rights",
        "question": "What protection is available against domestic violence?",
        "keywords": ["domestic violence", "women protection", "abuse", "protection order"],
        "answer": (
            "The Protection of Women from Domestic Violence Act, 2005 "
            "provides civil remedies and protections for women facing "
            "domestic violence, subject to the facts and law."
        ),
        "law": "Protection of Women from Domestic Violence Act, 2005",
        "section": "Sections 17 to 23",
        "source": "https://www.indiacode.nic.in/"
    },
    {
        "category": "Legal Aid",
        "question": "How can I get free legal assistance?",
        "keywords": ["free lawyer", "free legal aid", "legal help", "lawyer assistance"],
        "answer": (
            "People who meet the eligibility requirements can seek free "
            "legal services through the Legal Services Authorities. "
            "Contact the District Legal Services Authority or NALSA."
        ),
        "law": "Legal Services Authorities Act, 1987",
        "section": "Section 12",
        "source": "https://nalsa.gov.in/"
    },
    {
        "category": "Cybercrime",
        "question": "Where can I report cybercrime?",
        "keywords": ["cybercrime complaint", "hacking", "cyberbullying", "online harassment"],
        "answer": (
            "You can report cybercrime through the National Cyber Crime "
            "Reporting Portal. For immediate assistance with financial "
            "cyber fraud, call 1930."
        ),
        "law": "Information Technology Act, 2000 and other applicable laws",
        "section": "Depends on the facts of the incident",
        "source": "https://cybercrime.gov.in/"
    }
]

# Use the expanded legal knowledge base from legal_data.json
LEGAL_DATA = chatbot.legal_data

# ============================================================
# DESIGN
# ============================================================

st.markdown("""
<style>
    :root {
        --navy: #082653;
        --navy-deep: #061b3d;
        --blue: #2678e8;
        --blue-light: #e8f2ff;
        --ink: #10264d;
        --muted: #526987;
    }
    [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
        background: linear-gradient(135deg, #f7faff 0%, #edf5ff 55%, #f8fbff 100%) !important;
        color: var(--ink) !important;
    }
    [data-testid="stHeader"] { background: rgba(247,250,255,.92) !important; }
    .block-container { padding-top: 1.65rem; padding-bottom: 2.5rem; max-width: 1380px; }
    [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li, label { color: var(--ink); }

    /* Main heading */
    .main-title {
        color: #092957; font-family: Georgia, 'Times New Roman', serif;
        font-size: clamp(25px, 3vw, 38px); font-weight: 800;
        letter-spacing: .4px; margin: 0; padding: 8px 0 2px;
    }
    .sub-title {
        color: #4e6689; font-family: Georgia, 'Times New Roman', serif;
        font-size: 16px; font-style: italic; margin: 5px 0 24px 48px;
    }
    .info-card {
        background: linear-gradient(105deg, #e3efff, #f8fbff 72%, #dcecff);
        color: #102b59; border: 1px solid #a9ccff; border-left: 7px solid #1768d5;
        padding: 19px 22px; border-radius: 15px; margin: 14px 0 24px;
        line-height: 1.7; box-shadow: 0 5px 16px rgba(20,72,140,.07);
    }
    .warning-card {
        background: #fff6e9; color: #7c3511; border: 1px solid #ffd7a3;
        border-left: 6px solid #ed8b24; padding: 16px; border-radius: 12px; margin: 10px 0;
    }

    /* Dark navy sidebar */
    section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div {
        background: linear-gradient(180deg, #0b2c5c 0%, #071d40 100%) !important;
        color: #ffffff !important; border-right: 1px solid #183e72;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #f3f7ff !important;
    }
    section[data-testid="stSidebar"] h1 {
        font-family: Georgia, 'Times New Roman', serif; font-size: 25px;
        font-weight: 700; padding-top: 10px;
    }
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: #c6d9f5 !important; }
    section[data-testid="stSidebar"] div[role="radiogroup"] { gap: 5px; }
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        background: transparent !important; padding: 10px 12px; border-radius: 10px;
        color: #f4f7ff !important; opacity: 1 !important; transition: background .2s ease;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label p,
    section[data-testid="stSidebar"] div[role="radiogroup"] label span {
        color: #f4f7ff !important; opacity: 1 !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(71,145,255,.22) !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg, #287eea, #459bff) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,.16);
    }
    section[data-testid="stSidebar"] hr { border-color: rgba(220,235,255,.35); }

    /* Dashboard metric cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #ffffff, #eef5ff) !important;
        border: 1px solid #b8d5ff; border-left: 6px solid #2d80ed;
        padding: 19px; border-radius: 15px;
        box-shadow: 0 5px 15px rgba(13,58,115,.08); min-height: 112px;
    }
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"],
    div[data-testid="stMetric"] [data-testid="stMetricValue"],
    div[data-testid="stMetric"] p { color: #102b59 !important; }
    h1, h2, h3 { color: #102d5b; font-family: Georgia, 'Times New Roman', serif; }
    .small-note { color: var(--muted); font-size: 13px; }
    .stButton button, .stFormSubmitButton button {
        border-radius: 9px; font-weight: 650; border: 1px solid #1c69d4;
        background: linear-gradient(100deg, #1768d5, #398df3); color: white;
    }
    .stButton button:hover, .stFormSubmitButton button:hover {
        background: #0b4fae; color: white; border-color: #0b4fae;
    }
    div[data-testid="stExpander"] { border: 1px solid #c7dcf8; border-radius: 12px; background: rgba(255,255,255,.7); }
    [data-testid="stChatMessage"] { background: rgba(255,255,255,.85); border: 1px solid #d8e7fa; border-radius: 12px; }
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        border-radius: 9px !important;
        border: 1px solid #b9d2f2 !important;
        background: #ffffff !important;
        color: #10264d !important;
    }

    /* Consistent readable form fields across light and dark browser themes */
    input, textarea, [data-baseweb="input"], [data-baseweb="textarea"] {
        background-color: #ffffff !important;
        color: #10264d !important;
        -webkit-text-fill-color: #10264d !important;
        caret-color: #1768d5 !important;
    }
    input::placeholder, textarea::placeholder {
        color: #71839d !important;
        -webkit-text-fill-color: #71839d !important;
        opacity: 1 !important;
    }
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stTextInput"] input {
        background: #ffffff !important;
        color: #10264d !important;
        border: 1px solid #b9d2f2 !important;
        border-radius: 10px !important;
    }

    /* Streamlit chat input is fixed at the bottom; keep its entire area light */
    div[data-testid="stBottom"],
    div[data-testid="stBottom"] > div,
    div[data-testid="stBottomBlockContainer"],
    div[data-testid="stChatInput"],
    div[data-testid="stChatInput"] > div,
    div[data-testid="stChatInput"] [data-baseweb="textarea"],
    div[data-testid="stChatInput"] textarea {
        background: #f4f8ff !important;
        color: #10264d !important;
        -webkit-text-fill-color: #10264d !important;
        border-color: #b9d2f2 !important;
    }
    div[data-testid="stChatInput"] {
        border-top: 1px solid #d5e4f8 !important;
        box-shadow: 0 -5px 18px rgba(13,58,115,.06) !important;
        padding-top: 10px !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #71839d !important;
        -webkit-text-fill-color: #71839d !important;
    }

    /* Keep the app canvas and content readable and prevent dark footer bands */
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        background: #f4f8ff !important;
        color: #10264d !important;
    }
    [data-testid="stHeader"] { background: #f4f8ff !important; }
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] span { color: #10264d !important; }
    div[data-testid="stForm"] {
        background: rgba(255,255,255,.78) !important;
        border: 1px solid #d5e4f8 !important;
        border-radius: 14px !important;
        padding: 16px !important;
    }
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] p { color: #10264d !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def find_legal_matches(query, limit=5):
    """Rank records using exact phrase, token and alias matches."""
    query = (query or "").strip().lower()
    if not query:
        return []

    tokens = {
        token for token in re.findall(r"[a-z0-9]+", query)
        if len(token) > 1
    }
    scored = []

    for item in LEGAL_DATA:
        fields = [
            item.get("category", ""),
            item.get("question", ""),
            item.get("answer", ""),
            item.get("law", ""),
            item.get("section", ""),
            " ".join(item.get("keywords", [])),
            " ".join(item.get("aliases", [])),
        ]
        searchable = " ".join(str(value) for value in fields).lower()
        score = 0

        # Exact phrase is a strong signal.
        if query in searchable:
            score += 12

        # Give more weight to law names, sections, questions and aliases.
        priority_text = " ".join([
            str(item.get("question", "")),
            str(item.get("law", "")),
            str(item.get("section", "")),
            " ".join(item.get("aliases", [])),
        ]).lower()
        for token in tokens:
            if token in priority_text:
                score += 4
            elif token in searchable:
                score += 1

        # Phrase/alias matching helps natural-language variants.
        for alias in item.get("aliases", []) + item.get("keywords", []):
            alias = str(alias).lower().strip()
            if alias and (alias == query or alias in query):
                score += 8

        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    # Avoid returning unrelated weak matches.
    return [item for score, item in scored[:limit] if score >= 2]


def render_legal_records(records):
    if not records:
        st.info(
            "No matching record was found in the starter database. "
            "Try different keywords or consult an official legal source."
        )
        return

    for item in records:
        with st.expander(item["question"]):
            st.write(item["answer"])
            st.write(f"**Category:** {item['category']}")
            st.write(f"**Law:** {item['law']}")
            st.write(f"**Section:** {item['section']}")
            st.markdown(f"[Open source]({item['source']})")


def generate_ai_answer(question):
    """Generate an answer using the shared TF-IDF + Gemini chatbot."""
    return chatbot.generate_legal_response(question)


def show_section(title, description, points=None):
    st.subheader(title)
    st.write(description)
    if points:
        for point in points:
            st.markdown(f"- {point}")


# ============================================================
# SIDEBAR AND HEADER
# ============================================================

PAGES = [
    "Dashboard",
    "AI Legal Chatbot",
    "PDF Legal Document Assistant",
    "Indian Laws",
    "Women's Legal Rights",
    "Cybercrime Assistance",
    "Consumer Rights",
    "Student Legal Rights",
    "FIR & Police Assistance",
    "Legal Document Generator",
    "Free Legal Aid"
]

st.sidebar.markdown("<div style='text-align:center;font-size:48px;margin:8px 0 0'>⚖️</div>", unsafe_allow_html=True)
st.sidebar.title("Legal Assistant")
st.sidebar.markdown("<div style='text-align:center;color:#c6d9f5;font-family:Georgia,serif;font-style:italic;margin-bottom:18px'>Indian Legal Awareness Platform</div>", unsafe_allow_html=True)
st.sidebar.divider()
page = st.sidebar.radio("Choose a module", PAGES)

st.sidebar.divider()
st.sidebar.caption("Emergency: 112")
st.sidebar.caption("Cyber financial fraud: 1930")
st.sidebar.caption("Legal aid helpline: 15100")

st.markdown(
    '<div class="main-title">⚖️ AI LEGAL INFORMATION ASSISTANT</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="sub-title">Intelligent Platform for Indian Legal Awareness and Assistance</div>',
    unsafe_allow_html=True
)
st.markdown(
    "<div class='info-card'><b>Welcome!</b> Explore Indian legal topics, ask the AI assistant, "
    "and find official support resources from one place.</div>",
    unsafe_allow_html=True
)

# ============================================================
# 1. DASHBOARD
# ============================================================

if page == "Dashboard":
    st.header("Dashboard")
    st.write("Welcome to your Indian Legal Awareness Platform.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Legal Information Records", len(LEGAL_DATA))
    c2.metric("Available Modules", 11)
    c3.metric("Application Status", "Active")

    st.markdown(
        "<div class='info-card'><b>Search Indian laws, ask a legal question, "
        "review a PDF or find an official support service.</b></div>",
        unsafe_allow_html=True
    )
    st.subheader("Quick access")
    q1, q2, q3 = st.columns(3)
    q1.markdown("**AI Legal Chatbot**\n\nAsk a question in simple language.")
    q2.markdown("**Indian Laws**\n\nFind information by topic, law or section.")
    q3.markdown("**PDF Assistant**\n\nExtract and summarize PDF text.")

# ============================================================
# 2. AI LEGAL CHATBOT
# ============================================================

elif page == "AI Legal Chatbot":
    st.header("💬 AI Legal Chatbot")
    st.write("Ask a question about Indian law.")
    st.markdown(
        "<div class='info-card'><b>How to use:</b> Enter one clear legal question in the chat box. "
        "The assistant will search the legal knowledge base and, when configured, use Gemini to prepare a response.</div>",
        unsafe_allow_html=True
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display current conversation
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Example: What is an FIR?")

    if question:
        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching legal information and preparing an answer..."):
                answer = generate_ai_answer(question)
            st.markdown(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

    col1, col2 = st.columns([1, 2])

    with col1:
        if st.button("Clear current conversation"):
            st.session_state.messages = []
            st.rerun()

    with col2:
        st.caption("Your questions and answers are saved automatically.")

    # Show previously saved conversations from SQLite
    with st.expander("🕘 View saved chat history"):
        try:
            saved_chats = database.get_chat_history(limit=50)

            if saved_chats:
                for chat_id, old_question, old_answer, created_at in saved_chats:
                    st.markdown(f"**Question:** {old_question}")
                    st.caption(f"Saved: {created_at}")
                    with st.container(border=True):
                        st.markdown(old_answer)
                    st.divider()
            else:
                st.info("No saved conversations yet.")

        except Exception as error:
            st.error(f"Unable to load chat history: {error}")

    # Collect simple user feedback
    st.subheader("Share your feedback")

    with st.form("chatbot_feedback_form"):
        rating = st.select_slider(
            "How helpful was the assistant?",
            options=[1, 2, 3, 4, 5],
            value=4,
            format_func=lambda value: {
                1: "1 - Not helpful",
                2: "2 - Slightly helpful",
                3: "3 - Okay",
                4: "4 - Helpful",
                5: "5 - Very helpful"
            }[value]
        )
        comment = st.text_area("Additional comments (optional)")
        submitted = st.form_submit_button("Submit feedback")

        if submitted:
            try:
                database.save_feedback(rating, comment)
                st.success("Thank you! Your feedback has been saved.")
            except Exception as error:
                st.error(f"Unable to save feedback: {error}")

    st.caption(
        "This chatbot uses the TF-IDF legal information retrieval system, "
        "Gemini when configured, and the project's SQLite database. "
        "It provides general legal awareness, not professional legal advice."
    )

# ============================================================
# 3. INDIAN LAWS
# ============================================================

elif page == "PDF Legal Document Assistant":
    st.header("📄 PDF Legal Document Assistant")
    st.write("Upload a text-based PDF to extract its text and request an AI-generated plain-language summary.")
    st.info("For privacy, upload only documents you are permitted to process. This prototype does not provide legal advice. Scanned/image-only PDFs may not contain extractable text.")

    uploaded_pdf = st.file_uploader("Choose a PDF document", type=["pdf"], help="Maximum size: 10 MB; maximum: 30 pages.")
    if uploaded_pdf is not None:
        try:
            pdf_bytes = uploaded_pdf.getvalue()
            extracted_text, page_count = document_tools.extract_pdf_text(pdf_bytes)
            st.success(f"Successfully read {page_count} page(s).")
            st.metric("Extracted characters", f"{len(extracted_text):,}")
            with st.expander("Preview extracted text"):
                st.text(extracted_text[:12000] + ("\n\n[Preview shortened]" if len(extracted_text) > 12000 else ""))

            if st.button("Generate AI Summary", type="primary"):
                with st.spinner("Preparing a plain-language summary..."):
                    try:
                        summary, was_truncated = document_tools.summarize_legal_document(extracted_text)
                        st.subheader("AI-generated document summary")
                        st.markdown(summary)
                        if was_truncated:
                            st.warning("The PDF text was longer than the current summarization limit. The summary uses the beginning portion of the extracted text only.")
                        st.download_button(
                            "Download Summary",
                            data=summary,
                            file_name="legal_document_summary.txt",
                            mime="text/plain"
                        )
                    except Exception as exc:
                        st.error(f"Could not generate the summary: {exc}")
        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Unable to read this PDF. Please try another valid PDF. Details: {exc}")

elif page == "Indian Laws":
    st.header("📚 Indian Laws")
    st.write("Browse verified-topic summaries or search using a law name, section, common phrase or problem description.")

    categories = sorted({item.get("category", "Other") for item in LEGAL_DATA})
    selected_category = st.selectbox("Choose a category", ["All categories"] + categories, index=0)
    query = st.text_input(
        "Search by law, section, topic or keyword",
        placeholder="Try: theft, FIR, ragging, cyber fraud, Article 14"
    )

    records = LEGAL_DATA
    if selected_category != "All categories":
        records = [item for item in records if item.get("category") == selected_category]

    if query.strip():
        ranked = find_legal_matches(query.strip(), limit=len(LEGAL_DATA))
        allowed_ids = {id(item) for item in records}
        records = [item for item in ranked if id(item) in allowed_ids]
        st.caption(f"Found {len(records)} matching record(s).")
    else:
        st.caption(f"Showing all {len(records)} record(s). Enter a keyword to filter the list.")

    render_legal_records(records)

# ============================================================
# 4. WOMEN'S LEGAL RIGHTS
# ============================================================

elif page == "Women's Legal Rights":
    st.header("👩 Women's Legal Rights")
    st.markdown("""
    <div class="warning-card">
        <b>If someone is in immediate danger, call 112.</b>
        If it is unsafe to use this device, seek help using a safe device
        or trusted person.
    </div>
    """, unsafe_allow_html=True)

    a, b, c = st.columns(3)
    a.metric("Emergency", "112")
    b.metric("Women Helpline", "181")
    c.metric("Child Helpline", "1098")

    show_section(
        "Domestic Violence",
        "The Protection of Women from Domestic Violence Act, 2005 "
        "provides civil remedies and protections in situations covered by the Act.",
        [
            "Seek emergency help if there is immediate danger.",
            "Keep records or evidence only if it is safe to do so.",
            "A Protection Officer, police station or legal services authority "
            "may be able to guide you."
        ]
    )
    show_section(
        "Workplace Sexual Harassment",
        "The Sexual Harassment of Women at Workplace (Prevention, "
        "Prohibition and Redressal) Act, 2013 provides a complaint framework.",
        [
            "Find out whether the workplace has an Internal Committee.",
            "Preserve relevant messages, emails and records safely.",
            "Check the applicable procedure and time limits with an authorised source."
        ]
    )
    show_section(
        "Dowry Harassment",
        "Dowry demands and related harassment may lead to legal remedies "
        "under applicable laws. The correct legal route depends on the facts."
    )
    show_section(
        "Constitutional Rights",
        "Articles 14, 15 and 21 of the Constitution are among the "
        "important constitutional protections relevant to equality and life."
    )

    st.subheader("Support and official information")
    st.markdown("- Emergency response: **112**")
    st.markdown("- Women Helpline: **181** (service arrangements can vary by state)")
    st.markdown("- Child Helpline: **1098**")
    st.markdown("- National Legal Aid Helpline: **15100**")
    st.markdown("[National Commission for Women](https://ncw.nic.in/)")
    st.markdown("[Women Helpline – Ministry of Women and Child Development](https://wcd.gov.in/women/help)")
    st.markdown("[Odisha Police](https://odishapolice.gov.in/)")

# ============================================================
# 5. CYBERCRIME ASSISTANCE
# ============================================================

elif page == "Cybercrime Assistance":
    st.header("🛡️ Cybercrime Assistance")
    st.markdown("""
    <div class="warning-card">
        <b>Online financial fraud?</b> Contact your bank or payment provider
        immediately and call <b>1930</b>. Report it through the official
        cybercrime portal as soon as possible.
    </div>
    """, unsafe_allow_html=True)

    a, b = st.columns(2)
    a.metric("Financial Cyber Fraud", "1930")
    b.metric("Emergency", "112")

    show_section(
        "Steps after online financial fraud",
        "Act quickly and preserve information.",
        [
            "Call 1930.",
            "Contact your bank or payment provider immediately.",
            "Report the incident at cybercrime.gov.in.",
            "Save transaction IDs, screenshots, phone numbers and messages.",
            "Do not share OTPs, UPI PINs, passwords or card details."
        ]
    )
    show_section(
        "Common cybercrime types",
        "Examples include UPI fraud, phishing, fake websites, social-media "
        "impersonation, cyberbullying, online harassment and hacking."
    )
    st.markdown("[National Cyber Crime Reporting Portal](https://cybercrime.gov.in/)")
    st.markdown("[Indian Cyber Crime Coordination Centre](https://i4c.mha.gov.in/)")

    query = st.text_input("Search cybercrime topics in the legal database")
    if query:
        render_legal_records(find_legal_matches(query))

# ============================================================
# 6. CONSUMER RIGHTS
# ============================================================

elif page == "Consumer Rights":
    st.header("🛒 Consumer Rights")
    show_section(
        "Your consumer rights",
        "The Consumer Protection Act, 2019 provides a framework for "
        "protecting consumer interests.",
        [
            "Protection against hazardous goods and services.",
            "Information about quality, quantity, price and standards.",
            "Choice among available products and services.",
            "Opportunity to be heard and seek appropriate redressal.",
            "Consumer awareness."
        ]
    )
    show_section(
        "If a product is defective",
        "Keep the invoice, order details, photographs and seller communication. "
        "Raise a complaint with the seller or platform and keep the complaint "
        "reference number. You may approach the consumer grievance system."
    )
    st.markdown("[National Consumer Helpline](https://consumerhelpline.gov.in/)")
    st.markdown("[e-Jagriti Consumer Case Portal](https://e-jagriti.gov.in/)")

    query = st.text_input("Search consumer-rights information")
    if query:
        render_legal_records(find_legal_matches(query))

# ============================================================
# 7. STUDENT LEGAL RIGHTS
# ============================================================

elif page == "Student Legal Rights":
    st.header("🎓 Student Legal Rights")
    show_section(
        "Important areas",
        "Student rights may arise from laws, education regulations and "
        "institutional policies. The correct process depends on the issue.",
        [
            "Protection against ragging under applicable anti-ragging laws and rules.",
            "Protection against harassment and unlawful discrimination.",
            "Access to institutional grievance redressal procedures.",
            "Consumer remedies for applicable education-related services.",
            "Access to public information under applicable RTI provisions."
        ]
    )
    st.subheader("Useful official resources")
    st.markdown("[National Anti-Ragging Portal](https://www.antiragging.in/)")
    st.markdown("[University Grants Commission](https://www.ugc.gov.in/)")
    st.markdown("[National Legal Services Authority](https://nalsa.gov.in/)")

    query = st.text_input("Search student-rights information")
    if query:
        render_legal_records(find_legal_matches(query))

# ============================================================
# 8. FIR & POLICE ASSISTANCE
# ============================================================

elif page == "FIR & Police Assistance":
    st.header("🚔 FIR & Police Assistance")
    show_section(
        "What is an FIR?",
        "FIR means First Information Report. Section 173 of the "
        "Bharatiya Nagarik Suraksha Sanhita, 2023 deals with information "
        "relating to cognizable offences."
    )
    show_section(
        "General steps",
        "The correct process depends on the incident and applicable law.",
        [
            "Call 112 in an emergency.",
            "Contact the appropriate police station or official reporting channel.",
            "Provide accurate information, dates, locations and evidence.",
            "Keep an acknowledgement or copy when one is provided.",
            "Seek legal help if you need advice about your options."
        ]
    )
    st.markdown("[Emergency Response Support System – 112](https://112.gov.in/)")
    st.markdown("[Odisha Police](https://odishapolice.gov.in/)")

    query = st.text_input("Search FIR or police-related information")
    if query:
        render_legal_records(find_legal_matches(query))

# ============================================================
# 9. LEGAL DOCUMENT GENERATOR
# ============================================================

elif page == "Legal Document Generator":
    st.header("📝 Legal Document Generator")
    st.warning(
        "This creates a basic educational draft, not a legally reviewed document. "
        "Have an advocate review it before submitting or sending it."
    )

    doc_type = st.selectbox(
        "Choose document type",
        [
            "General Complaint",
            "Request Letter",
            "Consumer Complaint",
            "Police Complaint"
        ]
    )
    name = st.text_input("Your full name")
    address = st.text_area("Your address (optional)", height=70)
    recipient = st.text_input("Recipient / Authority")
    subject = st.text_input("Subject")
    incident_date = st.date_input("Date", value=date.today())
    details = st.text_area("Describe the facts in chronological order", height=180)
    requested_action = st.text_area("What action are you requesting?", height=90)

    if st.button("Generate Document", type="primary"):
        if not name.strip() or not subject.strip() or not details.strip():
            st.error("Please enter your name, subject and incident details.")
        else:
            title = doc_type.upper()
            document = f"""{title}

Date: {incident_date.strftime("%d-%m-%Y")}

From:
{name}
{address}

To:
{recipient if recipient.strip() else "The Concerned Authority"}

Subject: {subject}

Respected Sir/Madam,

I, {name}, wish to bring the following matter to your attention:

FACTS OF THE MATTER:
{details}

REQUESTED ACTION:
{requested_action if requested_action.strip() else "I request you to kindly examine the matter and guide me on the appropriate next steps under applicable law."}

I confirm that the information provided above is true to the best of my knowledge.

Thank you.

Yours faithfully,

{name}
"""
            st.text_area("Generated draft – review carefully", document, height=420)
            st.download_button(
                "Download Document",
                data=document,
                file_name=f"{doc_type.lower().replace(' ', '_')}.txt",
                mime="text/plain"
            )

# ============================================================
# 10. FREE LEGAL AID
# ============================================================

elif page == "Free Legal Aid":
    st.header("🤝 Free Legal Aid")
    show_section(
        "What is free legal aid?",
        "Legal Services Authorities provide free legal services to people "
        "who satisfy the eligibility conditions under the Legal Services "
        "Authorities Act, 1987."
    )
    show_section(
        "How to seek help",
        "Contact the District Legal Services Authority (DLSA), State Legal "
        "Services Authority or NALSA and ask about eligibility and documents.",
        [
            "Explain your legal issue briefly.",
            "Ask what documents are required.",
            "Confirm your eligibility.",
            "Follow the instructions of the Legal Services Authority."
        ]
    )
    st.info("National Legal Aid Helpline: 15100")
    st.markdown("[National Legal Services Authority (NALSA)](https://nalsa.gov.in/)")
    st.markdown("[Odisha State Legal Services Authority](https://oslsa.odisha.gov.in/)")

# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption("AI Legal Information Assistant")
st.caption(
    "Disclaimer: This platform provides general legal information "
    "for awareness. It is not professional legal advice and does not create "
    "an advocate-client relationship. Legal content may be incomplete or "
    "change over time. Verify current law through official sources and "
    "consult a qualified advocate about a specific matter."
)
