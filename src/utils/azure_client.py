from openai import AzureOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

azure_openai_model = os.getenv("AZURE_OPENAI_DEPLOYMENT")
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)