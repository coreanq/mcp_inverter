import time
from pymodbus.client import ModbusSerialClient
from pymodbus import FramerType 

# RTU 클라이언트 설정
client = ModbusSerialClient(
    port='COM7',       # 사용하는 시리얼 포트 (Windows) 또는 /dev/ttyUSB0 (Linux)
    framer=FramerType.RTU,
    baudrate=9600,     # 통신 속도
    bytesize=8,        # 데이터 비트
    parity='N',        # 패리티 ('N' - 없음, 'E' - 짝수, 'O' - 홀수)
    stopbits=1,        # 정지 비트
    timeout=1          # 타임아웃 (초)
)



def connect_modbus() -> bool:
    # 연결
    if( client.is_socket_open() == True ):
        return True
    elif not client.connect():
        print("연결 실패")
        return False
    return True


def send_modbus(address: int, value: int, slave_id: int):

    try:
        # 레지스터 값 읽기 (Modbus 함수 코드 3)
        # 슬레이브 주소 1, 레지스터 시작 주소 7, 1개의 레지스터 읽기
        # response = client.write_register( address, value, slave = slave_id)
        # if not response.isError():
        #     print(f"현재 가속 시간 값: {response.registers[0] * 0.1} 초")
        # else:
        #     print(f"읽기 오류: {response}")

        # 레지스터 값 쓰기 (Modbus 함수 코드 6)
        # 슬레이브 주소 1, 레지스터 주소 7에 값 100 쓰기 (10초)
        response = client.write_register(address=address-1, value=value, slave=slave_id)
        if not response.isError():
            print(f"레지스터 주소 {address}에 값 {value} 설정 성공")
        else:
            print(f"쓰기 오류: {response}")

    finally:
        # 연결 종료
        client.close()

if __name__ == "__main__":
    connect_modbus()
    send_modbus(address=7, value=100, slave_id=1)
