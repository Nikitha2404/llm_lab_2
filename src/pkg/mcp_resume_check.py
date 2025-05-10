from src.utils.azure_client import azure_openai_model,client
from src.utils.llm_stats import LLMStats
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

llmstats = LLMStats(model_name=azure_openai_model)

app = FastAPI(title="Resume APP")

class ResumeChecklist(BaseModel):
    candidate_name: Optional[str] = Field(None, description="Candidate's full name; return null if nothing is specified")
    skills: List[str] = Field(..., description="Technical or professional skills listed")
    experience_years: int = Field(..., description="Total number of years of professional experience upto the year 2025")
    education_level: str = Field(..., description="Highest education level attained (e.g. Bachelor's, Master's, PhD) and also the specialisation taken")
    current_job_role: str = Field(..., description="Most recent or current job title mentioned in resume")
    projects_count: Optional[int] = Field(None, description="Number of distinct projects mentioned or led in resume")

@app.post("/resume_check",response_model=ResumeChecklist, operation_id="resume_check")
async def resume_check(input: str):
    print("resume input: ", input)

    output= extract_resume_data(input)
    if output is None:
        raise HTTPException(status_code=400, detail="Invalid resume input")
    print("resume output: ", output)
    return json.loads(output)

def extract_resume_data(input: str):
    response = client.beta.chat.completions.parse(
        model=azure_openai_model,
        messages=[
            {"role": "system", "content": "Extract structured details from the resume provided by the user."},
            {"role": "user", "content": input},
        ],
        response_format=ResumeChecklist
    )
    llmstats.record_usage(input, response.usage)
    return response.choices[0].message.parsed
    
    
