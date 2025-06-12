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


from fastapi import File, UploadFile
import fitz  # PyMuPDF
import docx

def extract_text_from_file(file: UploadFile) -> str:
    contents = file.file.read()
    if file.filename.endswith(".txt"):
        return contents.decode("utf-8")
    elif file.filename.endswith(".docx"):
        doc = docx.Document(file.file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif file.filename.endswith(".pdf"):
        with fitz.open(stream=contents, filetype="pdf") as pdf:
            text = ""
            for page in pdf:
                text += page.get_text()
            return text
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

@app.post("/upload-policy")
async def upload_policy(file: UploadFile = File(...), framework: str = "NIST 800-53"):
    try:
        text = extract_text_from_file(file)
        prompt = f"""
        Evaluate this policy against the {framework} compliance framework.
        Identify gaps, risks, and recommendations.

        {text}
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
