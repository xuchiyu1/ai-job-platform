import os
import json
import anthropic
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

class JDRequest(BaseModel):
    jd: str

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/analyze")
def analyze(body: JDRequest):
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""Analyze this job description and return ONLY a JSON object with no other text:
{{
  "skills": ["skill1", "skill2", "skill3"],
  "timeline": "X days",
  "difficulty": "Easy/Medium/Hard"
}}

Job Description:
{body.jd}"""
            }
        ]
    )
    result = json.loads(message.content[0].text)
    return result