import os
import json
import anthropic
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory="templates")
from dotenv import load_dotenv
load_dotenv()
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
  "skills_en": ["skill1", "skill2"],
  "skills_zh": ["技能1", "技能2"],
  "interview_topics_en": ["topic1", "topic2"],
  "interview_topics_zh": ["话题1", "话题2"],
  "study_plan_7_en": ["Day 1: ...", "Day 2: ..."],
  "study_plan_7_zh": ["第1天: ...", "第2天: ..."],
  "study_plan_30_en": ["Week 1: ...", "Week 2: ..."],
  "study_plan_30_zh": ["第1周: ...", "第2周: ..."],
  "difficulty": "Easy/Medium/Hard"
}}
Job Description:
{body.jd}"""
            }
        ]
    )
    text = message.content[0].text
    print("Claude returned:", text)
    # 去掉可能的markdown标记
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    result = json.loads(text.strip())
    return result