from src.utils.azure_client import azure_openai_model,client
from src.utils.llm_stats import LLMStats
from pydantic import BaseModel, Field
from typing import List, Optional
import pandas as pd
import logging

llmstats = LLMStats(model_name=azure_openai_model)

class ResumeChecklist(BaseModel):
    candidate_name: Optional[str] = Field(None, description="Candidate's full name")
    skills: List[str] = Field(..., description="Technical or professional skills listed")
    experience_years: int = Field(..., description="Total number of years of professional experience")
    education_level: str = Field(..., description="Highest education level attained (e.g. Bachelor's, Master's, PhD)")
    current_job_role: str = Field(..., description="Most recent or current job title mentioned in resume")
    salary_expectation: Optional[int] = Field(None, description="Salary expectation if explicitly mentioned (annual, USD)")
    projects_count: Optional[int] = Field(None, description="Number of distinct projects mentioned or led in resume")

def analyse_resume(inputfilePath:str,outputfilePath:str):
    result = []
    df = pd.read_csv(inputfilePath)
    for row in df.itertuples():
        response = client.beta.chat.completions.parse(
            model=azure_openai_model,
            messages=[
                {"role": "system", "content": "Extract structured details from the resume provided by the user."},
                {"role": "user", "content": row.Resume_str},
            ],
            response_format=ResumeChecklist
        )
        llmstats.record_usage(row.index,response.usage)
        resume_dict = response.choices[0].message.parsed.model_dump()
        logging.info(f"Resume Analysis result for {row.Index}: {resume_dict}")
        result.append(resume_dict)
    result_df = pd.DataFrame(result)
    result_df.fillna("None", inplace=True)
    result_df.to_csv(outputfilePath, index=True)
    logging.info(f"Resume data saved to {outputfilePath}")
    
