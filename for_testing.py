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

if __name__ == "__main__":
    ser = serial.Serial('com10', 2400, timeout=0.3)
    while True:
        ser.write(0x27)
        response = ser.read(10)
        print(response)
    # router = Router()
    # router.start_check()
    # while True:
    #     if router.get_result():
    #         print("Пинг есть")
    #     else:
    #         print("Пинга нет")
    #         break
