from src.pkg.mcp_resume_check import app
from fastapi_mcp import FastApiMCP
import uvicorn
from src.utils.logging import setup_logging
from dotenv import load_dotenv
import os

load_dotenv()
setup_logging(output_dir=os.getenv("BASE_DIR_PATH"))

mcp = FastApiMCP(app,include_operations=["resume_check"])
mcp.mount()
mcp.setup_server()

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
