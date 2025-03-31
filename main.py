import os, json
import pandas as pd
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
import modbus  as md


import logging
from dotenv import load_dotenv
load_dotenv()  # load environment variables from .env
# ANSI 이스케이프 코드를 정의합니다.
COLOR_RED = "\033[91m"
COLOR_RESET = "\033[0m"

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        if (record.levelno >= logging.ERROR):
            record.msg = COLOR_RED + record.msg + COLOR_RESET
        return super().format(record)

# 로그 포맷을 정의합니다. 에러 메시지에 색상을 적용합니다.
formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 핸들러를 생성하고 포맷터를 설정합니다.
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO) # 필요에 따라 로그 레벨을 설정합니다.

################################################################################################################################
EXCEL_FILE_PATH = os.path.join(os.path.dirname(__file__), 'ParameterData.ods')

# 엑셀 파일 읽기 (한 번만 로드)
json_data = None
try:
    # read all sheet
    xls = pd.read_excel(EXCEL_FILE_PATH, sheet_name=None)

    # 제외할 컬럼 리스트 정의
    columns_to_exclude = ['파라미터타입', 'Title Enum', 'Title', 'At(@)Value', 'SourceDepended', '운전 중변경금지', '0 입력가능', '그래픽모드', 'Unsigned', 'maxinfo']

    # convert to json (특정 컬럼 제외)
    json_data = {
        sheet: df.drop(columns=columns_to_exclude, errors='ignore').to_dict(orient='records') 
        for sheet, df in xls.items()
    }

    # JSON 파일로 저장
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    logger.info(f"엑셀 파일 '{EXCEL_FILE_PATH}' 로드 완료.")
except FileNotFoundError:
    logger.error(f"오류: '{EXCEL_FILE_PATH}' 파일을 찾을 수 없습니다.")
    df = None
except Exception as e:
    logger.error(f"오류: 엑셀 파일 읽기 오류 - {e}")
    df = None
    

if( md.connect_modbus() == False ):
    exit()

################################################################################################################################
app = FastMCP("s300 commander", description="A server that transmits user requests as communication addresses/values to send commands.", 
              dependencies=["pandas"])
################################################################################################################################

# too much file size for llm
# @app.resource(uri="file:///s300_common_address.pdf", mime_type="application/pdf")
# def read_parameter_data() -> bytes:
#     return pdf_data

@app.resource(uri="file:///ParameterData", mime_type="application/json")
def read_parameter_text() -> str:
    return json_data

################################################################################################################################
@app.tool()
def write_parameter_data(parameter_name: str, parameter_address: int,parameter_value: int, form_msg: str, unit: str) -> str:
    """ write parameter data to parameter_address 
    that info is in json_data

    Args:
        parameter_name (str): parameter name
        parameter_address (str): parameter address
        parameter_value (str): parameter value
        form_msg (str): form message
        unit (str): unit
    Returns:
        str: success or fail
    """    
    logger.info(f"write_parameter_data: {parameter_name}, {parameter_address}, {parameter_value}")
    md.send_modbus(address=parameter_address, value=parameter_value, slave_id=1)
    return "success"



if __name__ == "__main__":
    logger.info("Hello from mcp-server!")
    app.run()
