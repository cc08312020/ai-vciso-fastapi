from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="AI vCISO Cybersecurity Tool")

class AnalysisRequest(BaseModel):
    text: str
    framework: str

@app.get("/")
def read_root():
    return {"message": "AI vCISO Cyber Tool is running"}

@app.post("/analyze-policy")
def analyze_policy(request: AnalysisRequest):
    try:
        prompt = f"""
        Evaluate this policy against the {request.framework} compliance framework.
        Identify gaps, risks, and recommendations.

        {request.text}
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a cybersecurity compliance auditor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return {"analysis": response.choices[0].message["content"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
