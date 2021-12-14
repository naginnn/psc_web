import engine
import time
from datetime import datetime

def wait_time(timeout):
    time_sec = datetime.now().strftime('%H:%M:%S.%f')[:-4]
    print(time_sec," Ожидание")
    for t in range(timeout):
        print(time_sec," Ожидание " + str(t + 1) + " сек")
        time.sleep(1 - time.time() % 1)

if __name__ == "__main__":
    wait_time(10)