from src.pkg.resume_query import analyse_resume,llmstats
from src.utils.logging import setup_logging

setup_logging(output_dir="/Users/nikitha.hebbar/Documents/llm_lab_week2")
analyse_resume(
    inputfilePath="/Users/nikitha.hebbar/Documents/llm_lab_week2/resume_data/input/resume_list_2.csv",
    outputfilePath="/Users/nikitha.hebbar/Documents/llm_lab_week2/resume_data/output/resume_list_2.csv"
)

llmstats.log_summary()