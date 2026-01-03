import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq Client
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

def get_ai_insight(user_query, expense_summary):
    """
    Chatbot Logic: Answers questions based on financial data + User Profile.
    """
    if not client:
        return "⚠️ API Key missing. Please set GROQ_API_KEY in .env file."

    # Extract Profile Context
    profile = expense_summary.get('user_profile', {})
    role = profile.get('role', 'User')
    name = profile.get('full_name', 'Friend')
    occupation = profile.get('occupation', 'General')

    # Personalized System Prompt
    system_prompt = f"""
    You are 'FinBot', a smart financial advisor for {name}.
    User Context:
    - Role: {role}
    - Occupation: {occupation}
    
    ADVICE GUIDELINES:
    1. If role is 'Student': Focus on saving pocket money, affordable food, and travel.
    2. If role is 'Startup': Focus on business burn rate, tax deductions, and operational costs.
    3. If role is 'Employee': Focus on salary management, rent, investments, and monthly budgeting.

    User Financial Data Summary:
    {json.dumps(expense_summary)}

    User Query: {user_query}

    Rules:
    - Be concise, friendly, and use emojis.
    - Use Indian Rupees (₹) for currency.
    - Answer ONLY based on data provided.
    """

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": system_prompt}],
            model="llama-3.3-70b-versatile", 
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Error: {str(e)}"

def clean_receipt_with_ai(raw_text):
    """
    OCR Cleanup: Extracts structured data with Indian context.
    """
    if not client:
        return None 

    prompt = f"""
    Analyze this receipt text and extract JSON.
    Text: "{raw_text}"
    
    Extraction Rules:
    1. merchant: Name of the shop/service.
    2. date: Format MUST be YYYY-MM-DD. 
       - IMPORTANT: Input dates are likely in DD-MM-YYYY format (Indian Standard).
       - Example: "02/01/2026" is 2nd January -> Output: "2026-01-02".
       - Example: "05/04/2026" is 5th April -> Output: "2026-04-05".
       - If multiple dates exist, pick the transaction date.
    3. amount: Total numeric value (ignore currency symbols like ₹, Rs, $).
    4. category: Choose best match from [Food, Travel, Shopping, Utilities, Medical, Salary, Other].
    
    Return ONLY valid JSON. Keys: merchant, date, amount, category.
    If a field is not found, use null.
    """

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant", 
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except:
        return None