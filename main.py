import os, json
import pandas as pd
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
import modbus  as md


################################################################################################################################
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
