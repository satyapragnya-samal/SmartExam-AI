# FILE: exams/ai_service.py

import json
import os
from google import genai
from google.genai import types


def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


def generate_mcqs_with_ai(topic, count=5, difficulty="medium", marks=1):
    """Generates structured MCQs using gemini-2.5-flash with strict JSON output."""
    client = get_client()
    if not client:
        return None

    prompt = f"""
    You are an expert academic examiner on the SmartExam AI platform.
    Generate exactly {count} multiple choice questions on the topic: "{topic}".
    Difficulty level: {difficulty}.
    Each question must have 4 distinct options (A, B, C, D) and exactly one correct answer.
    
    Return a strictly valid JSON array of objects with the following keys:
    - question_text (string)
    - option_a (string)
    - option_b (string)
    - option_c (string)
    - option_d (string)
    - correct_answer (one of: "A", "B", "C", "D")
    - marks (integer: {marks})
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"AI Generation Error: {e}")
        return None


def generate_student_diagnostic(exam_title, total_marks, earned_marks, percentage, weak_questions):
    """Generates diagnostic feedback and study plans based on student errors."""
    client = get_client()
    if not client:
        return "AI analysis is currently unavailable. Ensure GEMINI_API_KEY is configured in your .env file."

    errors_summary = "\n".join([
        f"- Question: {q['text']}\n  Student picked: {q['selected']} | Correct: {q['correct']}"
        for q in weak_questions
    ])

    prompt = f"""
    You are the SmartExam AI academic mentor. A student just finished the exam "{exam_title}".
    Score: {earned_marks}/{total_marks} ({percentage}%).
    
    Here are the specific questions the student got wrong:
    {errors_summary if errors_summary else "The student scored 100%! No errors."}

    Provide:
    1. A brief 2-sentence diagnostic assessment of their performance.
    2. 3 actionable, specific bullet points on core topics they should revise based on their mistakes.
    3. A 1-sentence motivational closing.
    Keep the tone clear, supportive, and professional. Use clean text.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
            ),
        )
        return response.text
    except Exception as e:
        return f"Unable to generate analysis at this time: {str(e)}"


def get_doubt_bot_response(user_message, exam_context="General Examination"):
    """Powers the interactive doubt-clearing chatbot for students."""
    client = get_client()
    if not client:
        return "SmartExam AI Assistant is unavailable without an active GEMINI_API_KEY in your .env file."

    system_instruction = f"""
    You are 'SmartExam AI Tutor', an academic assistant helping students prepare for assessments and understand curriculum concepts.
    Current subject/context: {exam_context}.
    Explain concepts simply, provide clean examples where appropriate, and keep answers concise (under 120 words).
    Do NOT give out direct answers if the user asks you to solve active exam questions.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Context: {exam_context}\nStudent Question: {user_message}",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3,
            ),
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"