from src.utils.azure_client import azure_openai_model,client
from src.utils.llm_stats import LLMStats
from pydantic import BaseModel, Field
from typing import List, Optional
import pandas as pd
import json
import logging

llmstats = LLMStats(model_name=azure_openai_model)

class ResumeChecklist(BaseModel):
    candidate_name: Optional[str] = Field(None, description="Candidate's full name; return null if nothing is specified")
    skills: List[str] = Field(..., description="Technical or professional skills listed")
    experience_years: int = Field(..., description="Total number of years of professional experience upto the year 2025")
    education_level: str = Field(..., description="Highest education level attained (e.g. Bachelor's, Master's, PhD) and also the specialisation taken")
    current_job_role: str = Field(..., description="Most recent or current job title mentioned in resume")
    projects_count: Optional[int] = Field(None, description="Number of distinct projects mentioned or led in resume")

def analyse_resume(inputfilePath: str, outputfilePath: str):
    df = pd.read_csv(inputfilePath)
    
    with open(outputfilePath, 'w', encoding='utf-8') as f:
        for row in df.itertuples():
            response = client.beta.chat.completions.parse(
                model=azure_openai_model,
                messages=[
                    {"role": "system", "content": "Extract structured details from the resume provided by the user."},
                    {"role": "user", "content": row.Resume_str},
                ],
                response_format=ResumeChecklist
            )
            llmstats.record_usage(row.index, response.usage)
            resume_dict = response.choices[0].message.parsed.model_dump()
            logging.info(f"Resume Analysis result for {row.Index}: {resume_dict}")
            f.write(json.dumps(resume_dict) + "\n")
    
    logging.info(f"Resume data saved to {outputfilePath}")
