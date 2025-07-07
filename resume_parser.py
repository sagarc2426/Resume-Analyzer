import re
import spacy
from pdfminer.high_level import extract_text

nlp = spacy.load("en_core_web_md")

def extract_text_from_pdf(pdf_path):
    try:
        text = extract_text(pdf_path)
        print("✅ Extracted resume text:\n", text[:500])
        return text
    except Exception as e:
        print("❌ Failed to extract text from PDF:", e)
        return ""

def clean_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def semantic_match(resume_text, jd_text):
    if not resume_text or not jd_text:
        print("❌ One or both texts are empty!")
        return 0.0
    doc1 = nlp(resume_text)
    doc2 = nlp(jd_text)
    similarity = doc1.similarity(doc2)
    print(f"📊 Semantic similarity score: {similarity}")
    return round(similarity * 100, 2)

def extract_skills(text, keywords):
    found = []
    text = text.lower()
    for skill in keywords:
        if re.search(rf"\b{re.escape(skill.lower())}\b", text):
            found.append(skill)
    return found

SKILL_SET = {
    "Software Engineer": ["python", "flask", "sql", "git", "api", "javascript"],
    "Data Analyst": ["python", "sql", "excel", "tableau", "statistics"],
    "Machine Learning Engineer": ["python", "pandas", "sklearn", "tensorflow", "nlp"],
    "Frontend Developer": ["html", "css", "javascript", "react", "typescript"],
    "Backend Developer": ["nodejs", "express", "mongodb", "api", "docker"]
}
