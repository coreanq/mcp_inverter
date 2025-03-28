import os, sys
import pandas as pd
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP 

import logging
from dotenv import load_dotenv
load_dotenv()  # load environment variables from .env

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

################################################################################################################################
EXCEL_FILE_PATH = os.path.join(os.path.dirname(__file__), 'ParameterData.ods')

# 엑셀 파일 읽기 (한 번만 로드)
try:
    df = pd.read_excel(EXCEL_FILE_PATH, engine='odf')
    logger.info(f"엑셀 파일 '{EXCEL_FILE_PATH}' 로드 완료.")
except FileNotFoundError:
    logger.error(f"오류: '{EXCEL_FILE_PATH}' 파일을 찾을 수 없습니다.")
    df = None
except Exception as e:
    logger.error(f"오류: 엑셀 파일 읽기 오류 - {e}")
    df = None


################################################################################################################################
app = FastMCP("s300 commander", description="A server that transmits user requests as communication addresses/values to send commands.")

class ParameterData(BaseModel):
    parameter_name: str
    parameter_value: str

@app.resource(
        name="Parameter Data", 
        description="Parameter data",
        mime_type="text/ods"
)
def get_parameter_data():
    return df

if __name__ == "__main__":
    print("Hello from mcp-server!")
