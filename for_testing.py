from threading import Thread, Lock

import serial

import engine
import time
from datetime import datetime
from pythonping import ping



# class Router:
#     result = True
#     def check_router(self):
#         lock = Lock()
#         packets = 0
#         while self.result:
#             # time.sleep(0.5)  # rrr
#             response_list = ping('192.168.1.1', size=1, count=1, timeout=0.020)
#             lock.acquire()
#             if (response_list.rtt_max_ms == 20.0):
#                 self.result = False
#             else:
#                 lock.release()
#             # print(response_list.rtt_max_ms)
#
#     def get_result(self):
#         return self.result
#
#     def start_check(self):
#         Thread(target=self.check_router).start()
    #
    #
    #     # если ок, разрешить дальнейшую работу потока
    #     # если bad, заблокировать поток метода check_router и свой
    #     # метод принудительной остановки потока? Или можно импользовать break?
def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')
if __name__ == "__main__":
    ser = serial.Serial('com6', 2400, timeout=0.3)
    while True:
        print("Введите команду 1 или 2: ")
        command = int(input())
        ser.write(int_to_bytes(command))
        response = ser.readline()


        print(response)
        time.sleep(0.5)
    # router = Router()
    # router.start_check()
    # while True:
    #     if router.get_result():
    #         print("Пинг есть")
    #     else:
    #         print("Пинга нет")
    #         break
