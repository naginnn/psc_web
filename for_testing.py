import engine
import time
from datetime import datetime
from pythonping import ping

def wait_time(timeout):
    time_sec = datetime.now().strftime('%H:%M:%S.%f')[:-4]
    print(time_sec," Ожидание")
    for t in range(timeout):
        print(time_sec," Ожидание " + str(t + 1) + " сек")
        time.sleep(1 - time.time() % 1)

if __name__ == "__main__":
    while True:
        time.sleep(0.5) #rrr
        response_list = ping('192.168.3.127', size=1, count=1, timeout = 0.100)
        if (response_list.rtt_max_ms == 100.0):
            print("Провал зафиксирован")
        else:
            print("ок")
        print(response_list.rtt_max_ms)
