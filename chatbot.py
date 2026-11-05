
import json
import os
import database

from dotenv import load_dotenv
from google import genai

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==========================================
# 1. CONFIGURATION
# ==========================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY) if API_KEY else None

MODEL_NAME = "gemini-3.5-flash-lite"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "legal_data.json")

DISCLAIMER = (
    "This information is for general legal awareness only "
    "and is not a substitute for professional legal advice."
)

# Initialize SQLite database
database.create_tables()


# ==========================================
# 2. LOAD LEGAL DATABASE
# ==========================================

try:
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        legal_data = json.load(file)

    if not isinstance(legal_data, list):
        raise ValueError("Legal database must contain a JSON list.")

    if not legal_data:
        raise ValueError("Legal database is empty.")

except (FileNotFoundError, json.JSONDecodeError, ValueError) as error:
    raise RuntimeError(f"Unable to load legal database: {error}")


# ==========================================
# 3. PREPARE DATA FOR NLP
# ==========================================

documents = []

for item in legal_data:

    text = " ".join([
        str(item.get("question", "")),
        " ".join(item.get("keywords", [])),
        str(item.get("category", "")),
        str(item.get("answer", "")),
        str(item.get("law", "")),
        str(item.get("section", ""))
    ])

    documents.append(text)


# ==========================================
# 4. TF-IDF MODEL
# ==========================================

vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),
    sublinear_tf=True
)

tfidf_matrix = vectorizer.fit_transform(documents)


# ==========================================
# 5. FIND RELEVANT LEGAL INFORMATION
# ==========================================

def find_answers(user_question, limit=3):

    if not user_question or not user_question.strip():
        return []

    question_vector = vectorizer.transform([user_question])

    similarities = cosine_similarity(
        question_vector,
        tfidf_matrix
    ).flatten()

    ranked_indices = similarities.argsort()[::-1]

    results = []

    for index in ranked_indices:

        score = float(similarities[index])

        if score < 0.10:
            continue

        result = legal_data[index].copy()
        result["similarity"] = round(score, 3)

        results.append(result)

        if len(results) >= limit:
            break

    return results


def find_answer(user_question):

    results = find_answers(user_question, limit=1)

    return results[0] if results else None


# ==========================================
# 6. PREPARE LEGAL CONTEXT
# ==========================================

def prepare_legal_context(results):

    context = []

    for number, item in enumerate(results, start=1):

        record = f"""
LEGAL RECORD {number}

Category: {item.get('category', 'Not specified')}

Question:
{item.get('question', 'Not specified')}

Legal Information:
{item.get('answer', 'Not available')}

Applicable Law:
{item.get('law', 'Not specified')}

Section:
{item.get('section', 'Not specified')}

Official Source:
{item.get('source', 'Not available')}

Similarity Score:
{item.get('similarity', 0)}
"""

        context.append(record)

    return "\n".join(context)


# ==========================================
# 7. SAVE CHAT HISTORY
# ==========================================

def save_conversation(user_question, bot_answer):

    try:
        database.save_chat(user_question, bot_answer)

    except Exception as error:
        print("Database saving error:", error)


# ==========================================
# 8. GENERATE LEGAL RESPONSE USING GEMINI
# ==========================================

def generate_legal_response(user_question):

    if not user_question or not user_question.strip():

        return "Please enter a legal question."

    # Retrieve relevant records
    results = find_answers(user_question, limit=3)

    # No relevant legal information found
    if not results:

        answer = (
            "I could not find sufficiently relevant information "
            "in my current legal database.\n\n"
            "Please try another question or consult an advocate "
            "or an official legal resource.\n\n"
            + DISCLAIMER
        )

        save_conversation(user_question, answer)

        return answer

    legal_context = prepare_legal_context(results)

    # Gemini API key check
    if client is None:

        first = results[0]

        answer = (
            "Gemini API key is not configured.\n\n"
            "Retrieved legal information:\n\n"
            + first.get("answer", "No information available.")
            + "\n\nApplicable Law: "
            + first.get("law", "Not specified")
            + "\nSection: "
            + first.get("section", "Not specified")
            + "\nSource: "
            + first.get("source", "Not available")
            + "\n\n" + DISCLAIMER
        )

        save_conversation(user_question, answer)

        return answer

    # Gemini prompt
    prompt = f"""
You are an AI Legal Information Assistant specialising in Indian law.

Explain legal information in simple and understandable English.

USER QUESTION:
{user_question}

RETRIEVED LEGAL DATABASE:
{legal_context}

IMPORTANT INSTRUCTIONS:

1. Understand the user's actual question.
2. Use retrieved legal records only when relevant.
3. Do not include unrelated laws or sections.
4. Explain information in simple English.
5. Use clear headings and bullet points.
6. Mention applicable law and section exactly as provided.
7. Never invent legal provisions, penalties, procedures or case laws.
8. If the database lacks information, clearly explain the limitation.
9. Do not invent practical legal steps absent from the database.
10. Do not claim to be a lawyer or guarantee legal outcomes.
11. Include only relevant official sources from retrieved records.
12. Distinguish available information from uncertainty.
13. Always include a short legal disclaimer.

RESPONSE FORMAT:

### Understanding Your Question
Briefly explain the legal issue.

### Legal Explanation
Explain the relevant information.

### Applicable Law
Mention the law and section when available.

### Official References
Include relevant official sources.

### Important Note
Mention limitations in available information.

Disclaimer:
{DISCLAIMER}
"""

    try:

        response = client.interactions.create(
            model=MODEL_NAME,
            input=prompt
        )

        explanation = response.output_text

        if not explanation:
            raise ValueError("Gemini returned an empty response.")

        save_conversation(user_question, explanation)

        return explanation

    except Exception as error:

        print("Gemini API error:", error)

        first = results[0]

        answer = (
            "Gemini is temporarily unavailable.\n\n"
            "Here is the most relevant information "
            "available in the legal database:\n\n"
            + first.get("answer", "No information available.")
            + "\n\nApplicable Law: "
            + first.get("law", "Not specified")
            + "\nSection: "
            + first.get("section", "Not specified")
            + "\nOfficial Source: "
            + first.get("source", "Not available")
            + "\n\n" + DISCLAIMER
        )

        save_conversation(user_question, answer)

        return answer


# ==========================================
# 9. TERMINAL TESTING
# ==========================================

if __name__ == "__main__":

    print("=" * 55)
    print("       AI LEGAL INFORMATION ASSISTANT")
    print("=" * 55)

    print("\nLegal database loaded successfully.")
    print("Total legal records:", len(legal_data))

    while True:

        user_input = input("\nAsk your legal question: ")

        if user_input.lower().strip() in ["exit", "quit"]:

            print("\nThank you for using AI Legal Assistant!")
            break

        answer = generate_legal_response(user_input)

        print("\nAI LEGAL ASSISTANT:")
        print("-" * 55)
        print(answer)
        print("-" * 55)

