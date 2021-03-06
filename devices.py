import datetime
import socket
import re
import minimalmodbus
import time
from datetime import datetime
from threading import Thread, Lock
from pythonping import ping

dout_numbers = [81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96]
dout_names_101 = {"KL1":81,"KL2":82,"KL3":83,"KL4":84,"KL5":85,"KL6":86,"KL7":87,"KL8":88,"KL9":89,"KL10":90,"KL11":91,"KL12":92,"KL13":93,"KL14":94,"KL15":95,"KL16":96}
dout_names_102 = {"KL17":81,"KL18":82,"KL19":83,"KL20":84,"KL21":85,"KL22":86,"KL23":87,"KL24":88,"KL25":89,"KL26":90,"KL27":91,"KL28":92,"KL29":93,"KL30":94,"KL31":95,"KL32":96}
dout_names_103 = {"KL33":81,"KM1":82,"KM2":83,"KM3":84,"KM4":85,"KM5":86,"KM6":87,"KM7":88,"KM8":89,"KM9":90,"KM10":91,"KM11":92,"KM14":93,"KM15":94,"KM16":95,"KM17":96}
dout_names_104 = {"KM18":81,"KM19":82,"KM12":83,"KM13":84,"KM20":85,"KM21":86,"KM22":87,"KM23":88,"KL34":93}
din_names_201 = {"KL1":"MW1 - MeanWell 24-67","KL2":"MW2 - MeanWell 24-67","KL3":"MW3 - MeanWell 24-67","KL4":"MW4 - MeanWell 48-67","KL5":"MW5 - MeanWell 48-67",
                 "KL6":"WM1 - WeidMuller 24-10","KL7":"WM1 - WeidMuller 24-10","KL8":"WM2 - WeidMuller 24-10","KL9":"WM3 - WeidMuller 24-40","KL10":"WM4 - WeidMuller 24-40",
                 "KL11":"WM5 - WeidMuller 24-40","KL12":"WM6 - WeidMuller 48-20","KL13":"WM7 - WeidMuller 48-20","KL14":"WM8 - WeidMuller 48-20","KL15":"PW1 - TOPAZ PW 24-4",
                 "KL16":"PW2 - TOPAZ PW 24-4","KL17": "PW3 - TOPAZ PW 24-4", "KL18": "A7 - Коммутатор #1", "KL19": "A8 - Коммутатор #2","KL20": "A9 - Коммутатор #3",
                 "KL21": "A10 - Коммутатор #4","KL22": "A11 - Коммутатор #5", "KL23": "A12 - Коммутатор #6", "KL24": "A13 - Коммутатор #7","KL25": "A14 - Коммутатор #8",
                 "KL26": "A15 - Коммутатор #9","KL27": "A16 - Коммутатор #10", "KL28": "A17 - Коммутатор #11", "KL29": "A18 - Коммутатор #12","KL30": "ЛБП U1 - U на IN1",
                 "KL31": "ЛБП U2 - U на IN2", "KL32": "ЛБП U3 - U на IN3"
                 }
din_names_202 = {"KL33":"ЛБП U4 - U на IN4",
                 "KM1":"АКБ #1 - IN 3,4",
                 "KM2":"АКБ #2 - IN 3,4",
                 "KM3":"АКБ #3 - IN 3,4",
                 "KM4":"АКБ #4 - IN 3,4",
                 "KM5":"АКБ #5 - IN 3,4",
                 "KM6":"АКБ #6 - IN 3,4",
                 "KM7":"PSC 1 - входные каналы",
                 "KM8":"PSC 2 - входные каналы",
                 "KM9":"PSC 3 - входные каналы",
                 "KM10":"PSC 4 - входные каналы",
                 "KM11":"PSC 5 - входные каналы",
                 "KM14":"OUT1  - Коммутаторы",
                 "KM15":"OUT2  - R(реостат)",
                 "KM16":"OUT1  - Коммутаторы",
                 "KM17":"OUT2 - R(реостат)",
                 "KM18": "Коротокое замыкание на R1(реостат)",
                 "KM19": "Коротокое замыкание на R2(коммутаторы)",
                 "KM12": "Прибавить 5А(коммутаторы)",
                 "KM13": "Прибавить 10А(коммутаторы)",
                 "SF4": "Цепь IN1",
                 "SF5": "Цепь IN2",
                 "SF6": "Цепь IN3",
                 "SF7": "Цепь IN4",
                 "KM20": "Прибавить 20А(реостат)",
                 "KM21": "Прибавить 40А(реостат)",
                 "KM22": "Прибавить 40А(реостат)",
                 "KM23": "Прибавить 80А(реостат)",
                 "KL34": "Обрыв связи с датчиком"}
psc10_numbers_ti = {"U_IN1":257, "U_IN2":259, "U_IN3":261, "U_OUT1":263, "U_OUT2":265, "I_OUT1":267, "I_OUT2":269, "I_PWR_BTR":271, "U_PWR_BTR":273, "T1":275,
                      "T2":277, "T3":279, "T4":281, "T5":283}


def number_func(str):
    try:
        num = re.findall(r'\d*\.\d+|\d+', str)
        num = [float(i) for i in num]
        return float(num[0])
    except:
        return float(0)
# соединение modbus
class Modb:
    connect = ()
    def getConnection(self, name, port, slave_adress, baudrate, log):
        try:
            self.log = log
            self.instrument = minimalmodbus.Instrument(port, slave_adress)
            self.instrument.serial.baudrate = baudrate  # Baud
            self.instrument.serial.bytesize = 8
            self.instrument.serial.stopbits = 1
            # self.instrument.serial.timeout = 0.05 # seconds
            # self.instrument.serial.timeout = 300000
            self.instrument.close_port_after_each_call = True
            self.instrument.clear_buffers_before_each_transaction = True
            self.log.add("Connection:", "Соединение с модулем " + name + " установлено", True)
            self.connect = self.instrument
            return True
        except:
            self.log.add("Connection:", "Ошибка соединения с модулем " + name, False)
            return False

    # если соединение заебато
    def getСonnectivity(self):
        return self.connect
# функции DOUT
class Dout:
    def __init__(self, instrument, dout_names, name, log, timeout):
        self.instrument = instrument
        self.dout_names = dout_names
        self.name = name
        self.log = log
        self.timeout = timeout

    def get_key(self,value):
        for k, v in self.dout_names.items():
            if v == value:
                return k

    def check_tu_ti(self, signal, status):
        dout_signals = self.get_status()
        if (dout_signals != False):
            if (dout_signals[list(self.dout_names).index(signal)] == 1) and status == "ON":
                self.log.add(self.name, "Команда включить на " + signal + " успешно прошла", True)
                return True
            elif (dout_signals[list(self.dout_names).index(signal)] == 0) and status == "OFF":
                self.log.add(self.name, "Команда отключить на " + signal + " успешно прошла", True)
                return True
        else:
            self.log.add(self.name, "Команда на " + self.get_key(signal) + " не прошла", False)
            return False

    def get_status(self):
        try:
            signals = self.instrument.read_registers(1, 16, 3)
            if (len(signals) == 16):
                return signals
        except:
            return False

    def off_enabled(self):
        time_sec = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        self.log.add(self.name, "Сброс управления", True)
        i = 0
        for t in range(self.timeout):
            try:
                dout_signals = self.get_status()
                if (dout_signals != False):
                    for relay in dout_signals:
                        if relay == 1:
                            self.instrument.write_register(dout_numbers[i], 0, 4)
                        i = i + 1
                    self.log.add(self.name, "Сброс управления выполнен", True)
                    return True
            except:
                self.log.log_data[len(self.log.log_data) - 1] = \
                    time_sec + " " + self.name + \
                    ": Сброс управления " + str(t + 1) + " сек"
                time.sleep(1 - time.time() % 1)
                if t >= self.timeout - 1:
                    self.log.add(self.name, "Неудалось выполнить сброс управления", False)
                    return False



    def command(self, relay, status):
        time_sec = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        command = ""
        if status == "ON":
            command = "включить "
        if status == "OFF":
            command = "отключить "
        self.log.add(self.name, "Попытка подачи команды " + command + relay, True)
        for t in range(self.timeout):
            try:
                if status == "ON":
                    self.instrument.write_register(self.dout_names.get(relay), 1, 4)
                    if (self.check_tu_ti(relay,status)):
                        self.log.add(self.name, "Команда включить " + relay + " успешно подана", True)
                        return True

                if status == "OFF":
                    self.instrument.write_register(self.dout_names.get(relay), 0, 4)
                    if (self.check_tu_ti(relay,status)):
                        self.log.add(self.name, "Команда отключить " + relay + " успешно подана", True)
                        return True
            except:
                self.log.log_data[len(self.log.log_data) - 1] = \
                    time_sec + " " + self.name + \
                    ": Попытка подачи команды " + command + relay + " " + str(t + 1) + " сек"
                time.sleep(1 - time.time() % 1)
                if t >= self.timeout - 1:
                    self.log.add(self.name, "Неудалось получить телеизмерение с устройства", False)
                    return False
# переделать функционал повторения при неудачной попытки подачи
# функции DIN
class Din:
    def __init__(self, instrument, din_names, name, log, timeout):
        self.instrument = instrument
        self.din_names = din_names
        self.name = name
        self.log = log
        self.timeout = timeout

    def get_key(self, value):
        for k, v in self.impact.items():
            if v == value:
                return k

    def check_voltage(self, signal, status):
        time_sec = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        self.log.add(self.name,"Попытка проверить состояние " + signal + " " + status, True)
        for t in range(self.timeout):
            try:
                din_signals = self.get_status()
                if (din_signals != False):
                    if ((din_signals[list(self.din_names).index(signal)] == 1) and (status == "ON")):
                        self.log.add(self.name, "Напряжение на " + self.din_names.get(signal) + " подано", True)
                        return True
                    if ((din_signals[list(self.din_names).index(signal)] == 0) and (status == "OFF")):
                        self.log.add(self.name, "Напряжение с " + self.din_names.get(signal) + " снято", True)
                        return True
                assert False
            except:
                self.log.log_data[len(self.log.log_data) - 1] = \
                    time_sec + " " + self.name + \
                    ": Попытка проверить состояние " + signal + " " + status + " " + str(t + 1) + " сек"
                time.sleep(1 - time.time() % 1)
                if t >= self.timeout - 1:
                    self.log.add(self.name, "Неудалось получить телеизмерение с устройства", False)
                    return False

    def get_status(self):
        try:
            signals = self.instrument.read_registers(1, 32, 3)
            if (len(signals) == 32):
                return signals
        except:
            return False
# функции ЛБП
class PowerSupply:
    def __init__(self, ip_adress, port, name, log, timeout):
        self.ip_adress = ip_adress
        self.port = port
        self.name = name
        self.log = log
        self.socket = socket.socket()
        self.timeout = timeout
    # добавить 3 попытки
    def connection(self):
        try:
            self.log.add(self.name, "Установка соединения по адресу: " + self.ip_adress + ":" + self.port, True)
            self.socket.connect((self.ip_adress, int(self.port)))
            self.socket.send("*IDN?\n".encode())
            if (str(self.socket.recv(100)).find("Elektro-Automatik") != -1):
                self.socket.send("SYSTem:LOCK ON\n".encode())
                self.log.add(self.name, "Соединение по адресу: " + self.ip_adress + ":" + self.port + " установлено",True)
                self.socket.close()
                return True
            else:
                self.log.add(self.name, "Соединение по адресу: " + self.ip_adress + ":" + self.port + " не установлено", False)
                self.socket.close()
                return False
        except:
            self.log.add(self.name, "Соединение по адресу: " + self.ip_adress + ":" + self.port + " не установлено", False)
            self.socket.close()
            return False

    def remote(self, on_off):
        i = 0
        self.log.add(self.name, "Установка режима REMOTE: " + on_off, True)
        while True:
            try:
                self.socket = socket.socket()
                self.socket.connect((self.ip_adress, int(self.port)))
                message = "SYSTem:LOCK " + on_off + "\n"
                self.socket.send(message.encode())
                self.socket.close()
                self.log.add(self.name, "Режим REMOTE: " + on_off + " установлен", True)
                return True
            except:
                if i == 3:
                    self.log.add(self.name, "Неудалось установить режим REMOTE:" + on_off, False)
                    return False
                self.log.add(self.name, "Попытка установки режима REMOTE №: " + str(i + 1) + " " + on_off, True)
                i = i + 1

    def check_remote(self, on_off):
        i = 0
        self.log.add(self.name, "Проверка установки режима REMOTE: " + on_off, True)
        while True:
            try:
                self.socket = socket.socket()
                self.socket.connect((self.ip_adress, int(self.port)))
                self.socket.send("SYSTem:LOCK:OWNer?".encode())
                param = str(self.socket.recv(100)).find(on_off)
                if (param != -1):
                    self.log.add(self.name, "Режим REMOTE: " + on_off + " соответствует", True)
                    self.socket.close()
                    return True
                else:
                    self.log.add(self.name, "Режим REMOTE: " + on_off + " не соответствует", False)
                    self.socket.close()
                    return False
                i = i + 0.5
                time.sleep(i)
            except:
                if i == 3:
                    self.log.add(self.name, "Неудалось проверить установку режима REMOTE " + on_off, False)
                    return False
                self.log.add(self.name, "Попытка проверки установки режима REMOTE: " + on_off + " № " + str(i + 1), True)
                i = i + 1
                time.sleep(i)

    def set_voltage(self, value):
        i = 0
        voltage = str(value)
        while True:
            try:
                self.log.add(self.name, "Подача команды установить напряжение " + voltage + " В", True)
                self.socket = socket.socket()
                self.socket.connect((self.ip_adress, int(self.port)))
                message = "SOURce:VOLTage " + voltage + "\n"
                self.socket.send(message.encode())
                self.socket.recv(10)
                self.socket.close()
                self.log.add(self.name, "Команда подать напряжение успешно прошла " + voltage + " В", True)
                return True
            except:
                if (i == 3):
                    self.log.add(self.name, "Подача команды установить напряжение " + voltage + " В не прошла", False)
                    self.socket.close()
                    return False
                self.log.add(self.name, "Попытка подачи команды установить напряжение " + voltage + " В №" + str(i + 1), True)
                i = i + 1
                time.sleep(i)

    def check_voltage(self,value):
        i = 0
        while True:
            try:
                self.log.add(self.name, "Проверка установленно напряжения " + str(value) + " В", True)
                self.socket = socket.socket()
                self.socket.connect((self.ip_adress, int(self.port)))
                self.socket.send("MEAS:VOLT?\n".encode())
                voltage = number_func(str(self.socket.recv(10)))
                if ((round(float(voltage)) == round(value)) and round(float(voltage)) != 0):
                    self.socket.close()
                    self.log.add(self.name, "Установленное напряжение " + str(value) + " В" + " соответствует", True)
                    return True
                if ((round(float(voltage)) != round(value)) and round(float(voltage)) != 0):
                    if (i == 3):
                        self.socket.close()
                        self.log.add(self.name, "Значение установленного и фактического напряжения отличаются " + str(value) + " В", False)
                        return False
                    i = i + 1
                    time.sleep(i)
            except:
                if (i == 3):
                    self.log.add(self.name, "Невозможно получить значение установленного напряжения " + voltage + " В", False)
                    return False
                self.log.add(self.name, "Попытка получить значение установленного напряжения " + voltage + " В № " + str(i + 1), True)
                i = i + 1
                time.sleep(i)

    def output(self, on_off):
        i = 0
        self.log.add(self.name, "Установка режима OUTPUT: " + on_off, True)
        while True:
            try:
                self.socket = socket.socket()
                self.socket.connect((self.ip_adress, int(self.port)))
                message = "OUTPut " + on_off + "\n"
                self.socket.send(message.encode())
                self.socket.close()
                self.log.add(self.name, "Режим OUTPUT: " + on_off + " установлен", True)
                return True
            except:
                if i == 3:
                    self.log.add(self.name, "Неудалось установить режим OUTPUT:" + on_off, False)
                    return False
                self.log.add(self.name, "Попытка установки режима OUTPUT №: " + str(i + 1) + " " + on_off, True)
                i = i + 1
                time.sleep(i)

    def check_output(self, on_off):
        i = 0
        self.log.add(self.name, "Проверка установки режима OUTPUT: " + on_off, True)
        while True:
            try:
                self.socket = socket.socket()
                self.socket.connect((self.ip_adress, int(self.port)))
                self.socket.send("OUTPut?".encode())
                param = str(self.socket.recv(100)).find(on_off)
                if (param != -1):
                    self.log.add(self.name, "Режим OUTPUT: " + on_off + " соответствует", True)
                    self.socket.close()
                    return True
                else:
                    self.socket.close()
                    self.log.add(self.name, "Режим OUTPUT: " + on_off + " не соответствует", False)
                    return False
            except:
                if i == 3:
                    self.log.add(self.name, "Неудалось проверить установку режима OUTPUT: " + on_off, False)
                    return False
                self.log.add(self.name, "Попытка проверки установки режима OUTPUT: " + on_off + " № " + str(i + 1), True)
                i = i + 1
                time.sleep(i)

    # *IDN?
    # MEAS:VOLT? // текущее напряжение блока питания
    # VOLTage?
    # SOURce:VOLTage 10 // установить напряжение MIN/MAX
    # SOURce:CURRent 5 // установить ток MIN/MAX
    # OUTPut ON // включить выход
    # OUTPut OFF // отключить выход
    # MEAS:CURR? // текущий ток блока питания
    # SOUR:VOLTAGE 25 // текущее напряжение блока питания
# функции амперметра
class Ammeter:
    def __init__(self, instrument, name, log, timeout):
        self.instrument = instrument
        self.name = name
        self.log = log
        self.timeout = timeout

    current = 0.0
    # получить
    def get_ti(self):
        return round(self.current, 2)

    def check_ti(self):
        time_sec = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        self.log.add(self.name,"Попытка получить телеизмерения", True)
        for t in range(self.timeout):
            try:
                self.current = self.instrument.read_float(18, 3)
                if (self.current != None):
                    self.log.add(self.name, "Телеизмерение получено", True)
                    return True
                self.log.log_data[len(self.log.log_data) - 1] = \
                    time_sec + " " + self.name + \
                    ": Попытка получить телеизмерение " + str(t + 1) + " сек"
                time.sleep(1 - time.time() % 1)
                if t >= 9:
                    self.log.add(self.name, "Неудалось получить телеизмерение с устройства", False)
                    return False
            except:
                self.log.log_data[len(self.log.log_data) - 1] = \
                    time_sec + " " + self.name + \
                    ": Попытка получить телеизмерения " + str(t + 1) + " сек"
                time.sleep(1 - time.time() % 1)
                if t >= self.timeout - 1:
                    self.log.add(self.name, "Неудалось получить телеизмерение с устройства", False)
                    return False
# функции проверяемого устройства
class Psc_10:
    psc10_names_ts = ["IN1", "IN2", "IN3", "OUT1", "OUT2", "ERROR_OUT1", "ERROR_OUT2", "ERROR_BTR", "ERROR_I_OUT1",
                      "ERROR_I_OUT2", "PWR_BTR", "TEN", "APTC"]

    psc10_measurements = {"U_IN1": 0.0, "U_IN2": 0.0, "U_IN3": 0.0, "U_OUT1": 0.0, "U_OUT2": 0.0, "I_OUT1": 0.0,
                          "I_OUT2": 0.0, "I_PWR_BTR": 0.0, "U_PWR_BTR": 0.0, "T1": 0.0,
                          "T2": 0.0, "T3": 0.0, "T4": 0.0, "T5": 0.0}
    measurement = 0.0
    device_status = False
    timeout = 0

    def __init__(self, instrument, name, log, timeout):
        self.instrument = instrument
        self.name = name
        self.log = log
        self.timeout = timeout

    def set_timeout(self, timeout):
        self.timeout = timeout

    # получить
    def get_ti(self):
        return round(self.measurement, 2)

    def check_ti(self, name):
        time_sec = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        self.log.add(self.name,"Попытка получить телеизмерения", True)
        for t in range(self.timeout):
            try:
                self.measurement = self.instrument.read_float(psc10_numbers_ti.get(name), 4)
                if (self.measurement != None):
                    self.log.add(self.name, "Телеизмерение " + name + " получено", True)
                    return True
                self.log.log_data[len(self.log.log_data) - 1] = \
                    time_sec + " " + self.name + \
                    ": Попытка получить телеизмерение " + str(t + 1) + " сек"
                time.sleep(1 - time.time() % 1)
                if t >= self.timeout - 1:
                    self.log.add(self.name, "Неудалось получить телеизмерение с устройства", False)
                    return False
            except:
                self.log.log_data[len(self.log.log_data) - 1] = \
                    time_sec + " " + self.name + \
                    ": Попытка получить телеизмерения " + str(t + 1) + " сек"
                time.sleep(1 - time.time() % 1)
                if t >= self.timeout - 1:
                    self.log.add(self.name, "Неудалось получить телеизмерение с устройства", False)
                    return False
    ### изменить или написать новую чтобы можно было передавать один или несколько тс'ов отработать в тест модуле

    def check_behaviour(self, alleged_behavior):
        time_sec = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        self.log.add(self.name, "Ожидание включения устройства", True)
        for t in range(self.timeout):
            try:
                behaviour_list = self.get_all_ts()
                if (behaviour_list != False):
                    for alleged_name in alleged_behavior:
                        if alleged_behavior[alleged_name] != behaviour_list[alleged_name]:
                            assert False
                    self.log.add(self.name, "Состояние устройства соответствует", True)
                    return True
                else:
                    assert False
            except:
                self.log.log_data[len(self.log.log_data) - 1] = \
                    time_sec + " " + self.name + \
                    ": Ожидание включения устройства " + str(t + 1) + " сек"
                time.sleep(1 - time.time() % 1)
                if t >= self.timeout - 1:
                    self.log.add(self.name, "Неудалось получить состояние устройства", False)
                    return False

    def get_all_ts(self):
        i = 0
        behaviour_list = {"pwr1": 0, "pwr2": 0, "btr": 0, "key1": 0, "key2": 0, "error_pwr1": 0, "error_pwr2": 0,
                              "error_btr": 0, "error_out1": 0, "error_out2": 0, "charge_btr": 0, "ten": 0, "apts": 0}
        try:
            behaviour = self.instrument.read_registers(1, 13, 3)
            if (len(behaviour) == 13):
                for name in behaviour_list:
                    behaviour_list[name] = behaviour[i]
                    i = i + 1
                return behaviour_list
        except:
            return False
# функции проверяемого устройства
class Psc_40:
    psc40_names_ts = ["IN1", "IN2", "IN3", "IN4", "U_OUT1", "U_OUT2", "ERROR_KEY1", "ERROR_KEY2", "ERROR_KEY3",
                      "ERROR_KEY4", "PWR_BTR", "TEN", "OVERLOAD_I", "SHORT_I", "BTR_DISCHARGED", "U_IN1", "U_IN2",
                      "U_IN3",
                      "U_IN4", "ERROR_BTR", "APTC"]
    psc40_names_ti = {"U_IN1":257, "U_IN2":259, "U_IN3":261, "U_IN4":263, "U_OUT1":265, "U_OUT2":267, "I_PWR_BTR":269, "U_OUT":271, "I_OUT":273, "T1":275, "T2":277,
                      "T3":279, "T4":281, "T5":283, "T6":285, "T7":287, "T8":289, "U_PWR_BTR":291}

    def __init__(self, instrument, name, log, timeout):
        self.instrument = instrument
        self.name = name
        self.log = log
        self.timeout = timeout

    def get_ti(self,name_signal):
        try:
            value = self.instrument.read_float(self.psc40_names_ti.get(name_signal), 4)
            if (value != None):
                self.log.add(self.name, "Телеизмерение " + name_signal + " = " + str(value) + " получено", True)
                return value
            else:
                self.log.add(self.name, "Ошибка при попытке получения телеизмерения " + name_signal, False)
                return False
        except:
            self.log.add(self.name, "Критическая ошибка при попытке получения телеизмерения " + name_signal, False)
            return False

    def get_ts(self,name_signal):
        try:
            signals = {}
            dict = self.instrument.read_registers(1, 21, 4)
            if (len(dict) == 21):
                i = 0
                while (i < 21):
                    signals.update({self.psc40_names_ts[i] : dict[i]})
                    i = i + 1
                value = signals.get(name_signal)
                if (value != None):
                    self.log.add(self.name, "Телесигнал " + name_signal + " = " + str(value) + " получен", True)
                    return value
                else:
                    self.log.add(self.name, "Телесигнала " + name_signal + " не существует", False)
                    return False
            else:
                self.log.add(self.name, "Ошибка при попытке получения телесигнала " + name_signal, False)
                return False
        except:
            self.log.add(self.name, "Критическая ошибка при попытке получения телесигнала " + name_signal, False)
            return False

# функции роутера
class Router:
    result = True
    def __init__(self, ip_adress, name):
        self.ip_adress = ip_adress
        self.name = name

    def check_router(self):
        lock = Lock()
        while self.result:
            # time.sleep(0.5)  # rrr
            response_list = ping(self.ip_adress, size=1, count=1, timeout=0.020)
            lock.acquire()
            if (response_list.rtt_max_ms == 20.0):
                self.result = False
            else:
                lock.release()
            # print(response_list.rtt_max_ms)

    def set_result(self):
        self.result = False

    def get_result(self):
        return self.result

    def start_check(self):
        Thread(target=self.check_router).start()






