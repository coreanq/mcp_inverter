import os, sys, json
import pandas as pd

import asyncio
import streamlit as st
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, ItemHelpers
from agents.mcp import MCPServerStdio


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


# [ {user_input: {}, reponse: ""}, ... ]
user_prompt_cache = []

################################################################################################################################
DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'output.json')

json_data = None

def load_backend_data():
    # 엑셀 파일 읽기 (한 번만 로드)
    global json_data
    try:
        with open(DATABASE_FILE, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        
        logger.info(f"DATABASE 파일 '{DATABASE_FILE}' 로드 완료.")
    except FileNotFoundError:
        logger.error(f"오류: '{DATABASE_FILE}' 파일을 찾을 수 없습니다.")
        df = None
    except Exception as e:
        logger.error(f"오류: '{DATABASE_FILE}' 파일 읽기 오류 - {e}")
        df = None


################################################################################################################################
# Windows 호환성
# if sys.platform == "win32":
#     asyncio.set_event_loop_policy()

# MCP 서버 설정
async def setup_mcp_servers():
    servers = []
    
    # mcp.json 파일에서 설정 읽기
    with open('mcp.json', 'r') as f:
        config = json.load(f)
    
    # 구성된 MCP 서버들을 순회
    for server_name, server_config in config.get('mcpServers', {}).items():
        mcp_server = MCPServerStdio(
            params={
                "command": server_config.get("command"),
                "args": server_config.get("args", [])
            },
            cache_tools_list=True
        )
        await mcp_server.connect()
        servers.append(mcp_server)

    return servers


# 에이전트 설정
async def setup_agent():
    # 서버가 이미 존재하는지 확인하고, 없으면 생성
    mcp_servers = await setup_mcp_servers()
    
    agent = Agent(
        name="Assistant",
        instructions="너는 사용자의 질문을 분석해서 mcp server 를 사용해 요청사항을 수행하는 에이전트야",
        model="gpt-4o-mini",
        mcp_servers=mcp_servers,
    )
    return agent,mcp_servers


# 메시지 처리
async def process_user_message():
    agent,mcp_servers = await setup_agent()
    messages = json.dumps(user_prompt_cache, ensure_ascii=False).encode("utf-8")
    result = Runner.run_streamed(agent, input=messages)

    response_text = ""
    placeholder = st.empty()

    async for event in result.stream_events():
        # LLM 응답 토큰 스트리밍
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            response_text += event.data.delta or ""
            with placeholder.container():
                with st.chat_message("assistant"):
                    st.markdown(response_text)


        # 도구 이벤트와 메시지 완료 처리
        elif event.type == "run_item_stream_event":
            item = event.item

            if item.type == "tool_call_item":
                logger

    # 명시적 종료 (streamlit에서 비동기 처리 오류 방지)
    for server in mcp_servers:
        await server.__aexit__(None, None, None)

messages = []

async def main():
    agent,mcp_servers = await setup_agent()

    while True:
        user_input = input("\nYou: ")
        messages.append({"role": "user", "content": user_input})
        result = Runner.run_streamed(
            agent, 
            input=messages
        )
        
        response_text = '' 
        async for event in result.stream_events():
            # We'll ignore the raw responses event deltas
            if event.type == "raw_response_event":
                continue
            # When the agent updates, print that
            elif event.type == "agent_updated_stream_event":
                # print(f"Agent updated: {event.new_agent.name}")
                continue
            # When items are generated, print them
            elif event.type == "run_item_stream_event":
                if event.item.type == "tool_call_item":
                    print("-- Tool was called")
                elif event.item.type == "tool_call_output_item":
                    print(f"-- Tool output: {event.item.output}")
                elif event.item.type == "message_output_item":
                    print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
                else:
                    pass  # Ignore other event types

        print("=== Run complete ===\n\n")

if __name__ == "__main__":
    load_backend_data()
    asyncio.run(main())
    # main()
    # asyncio.run(process_user_message() )