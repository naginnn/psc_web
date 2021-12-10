import socket
import re
import minimalmodbus
import engine
import time
from accessify import implements, private

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
din_names_202 = {"KL33":"ЛБП U4 - U на IN4","KM1":"АКБ #1 - IN 3,4","KM2":"АКБ #2 - IN 3,4","KM3":"АКБ #3 - IN 3,4","KM4":"АКБ #4 - IN 3,4",
                 "KM5":"АКБ #5 - IN 3,4","KM6":"АКБ #6 - IN 3,4","KM7":"PSC 1 - входные каналы","KM8":"PSC 2 - входные каналы","KM9":"PSC 3 - входные каналы",
                 "KM10":"PSC 4 - входные каналы","KM11":"PSC 5 - входные каналы","KM14":"OUT1  - R(реостат)","KM15":"OUT2  - R(реостат)","KM16":"OUT1  - Коммутаторы","KM17":"OUT2 - Коммутаторы",
                 "KM18": "Коротокое замыкание на R1(реостат)", "KM19": "Коротокое замыкание на R2(коммутаторы)","KM12": "Прибавить 5А(коммутаторы)", "KM13": "Прибавить 10А(коммутаторы)",
                 "SF4": "Цепь IN1", "SF5": "Цепь IN2", "SF6": "Цепь IN3", "SF7": "Цепь IN4","KM20": "Прибавить 20А(реостат)", "KM21": "Прибавить 40А(реостат)", "KM22": "Прибавить 40А(реостат)", "KM23": "Прибавить 80А(реостат)",
                 "KL34": "Обрыв связи с датчиком"}


def number_func(str):
    try:
        num = re.findall(r'\d*\.\d+|\d+', str)
        num = [float(i) for i in num]
        return float(num[0])
    except:
        return float(0)

class Modb:
    instrument = ()
    def getConnection(self, name, port, slave_adress, log):
        try:
            self.log = log
            self.instrument = minimalmodbus.Instrument(port, slave_adress)
            self.instrument.serial.baudrate = 115200  # Baud
            self.instrument.serial.bytesize = 8
            self.instrument.serial.stopbits = 1
            # self.instrument.serial.timeout = 0.05 # seconds
            # self.instrument.serial.timeout = 300000
            self.instrument.close_port_after_each_call = True
            self.instrument.clear_buffers_before_each_transaction = True
            self.log.add("Connection:", "Соединение с модулем " + name + " установлено", True)
            return True
        except:
            self.log.add("Connection:", "Ошибка соединения с модулем " + name, False)
            return False

    # если соединение заебато
    def getСonnectivity(self):
        return self.instrument


class Dout:
    def __init__(self, instrument,dout_names,name,log):
        self.instrument = instrument
        self.dout_names = dout_names
        self.name = name
        self.log = log

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
            dict = self.instrument.read_registers(1, 16, 3)
            if len(dict) > 0:
                self.log.add(self.name, "Телесигналы получены", True)
                return dict
            self.log.add(self.name, "Неудалось получить телесигналы", False)
            return False
        except:
            self.log.add(self.name,"Ошибка при попытке получить телесигналы", False)
            return False

    def command(self, relay, status):
        i = 0
        if status == "ON":
            self.log.add(self.name, "Команда включить на " + relay, True)
        if status == "OFF":
            self.log.add(self.name, "Команда отключить на " + relay, True)
        while True:
            try:
                if status == "ON":
                    self.instrument.write_register(self.dout_names.get(relay), 1, 4)
                    if (self.check_tu_ti(relay,status)):
                        self.log.add(self.name, "Команда включить на " + relay + " успешно подана", True)
                        return True
                    else:
                        # Прекратить попытки
                        if i == 3:
                            self.log.add(self.name, "Команда включить на " + relay + " не прошла", False)
                            return False
                        self.log.add(self.name, "Попытка подать команду " + status + " №" + str(i + 1), True)
                        time.sleep(i)
                        i = i + 1
                if status == "OFF":
                    self.instrument.write_register(self.dout_names.get(relay), 0, 4)
                    if (self.check_tu_ti(relay,status)):
                        self.log.add(self.name, "Команда отключить на " + relay + " успешно подана", True)
                        return True
                    else:
                        # Прекратить попытки
                        if i == 3:
                            self.log.add(self.name, "Команда отключить на " + relay + " не прошла", False)
                            return False
                        self.log.add(self.name, "Попытка подать команду " + status + " №" + str(i + 1), True)
                        time.sleep(i)
                        i = i + 1
            except:
                if i == 3:
                    # Прекратить попытки
                    self.log.add(self.name, "Фатальная ошибка при подачи команды: " + status + "  на " + relay, False)
                    return False
                self.log.add(self.name, "Попытка подать команду " + status + " №" + str(i + 1), True)
                time.sleep(i)
                i = i + 1
# переделать функционал повторения при неудачной попытки подачи команды
class Din:
    def __init__(self, instrument, din_names, name, log):
        self.instrument = instrument
        self.din_names = din_names
        self.name = name
        self.log = log

    def get_key(self, value):
        for k, v in self.impact.items():
            if v == value:
                return k

    def check_voltage(self, signal, status):
        din_signals = self.get_status()
        if (din_signals != False):
            if ((din_signals[list(self.din_names).index(signal)] == 1) and (status == "ON")):
                self.log.add(self.name, "Напряжение на " + self.din_names.get(signal) + " подано", True)
                return True
            if ((din_signals[list(self.din_names).index(signal)] == 0) and (status == "OFF")):
                self.log.add(self.name, "Напряжение с " + self.din_names.get(signal) + " снято", True)
                return True
            return False
        return False

    def get_status(self):
        i = 0
        try:
            while True:
                dict = self.instrument.read_registers(1, 32, 3)
                if len(dict) > 0:
                    self.log.add(self.name, "Телесигналы получены", True)
                    return dict
                if i == 3:
                    self.log.add(self.name, "Неудалось получить телесигналы", False)
                    return False
                i = i + 1
        except:
            if i == 3:
                self.log.add(self.name, "Попытка получить телесигналы №" + str(i + 1), True)
                return False
            i = i + 1
            time.sleep(i)

class PowerSupply:
    def __init__(self, ip_adress, port, name, log):
        self.ip_adress = ip_adress
        self.port = port
        self.name = name
        self.log = log
        self.socket = socket.socket()

    def connection(self):
        try:
            self.log.add(self.name, "Установка соединения по адресу: " + self.ip_adress + ":" + self.port, True)
            self.socket.connect((self.ip_adress, int(self.port)))
            self.socket.send("*IDN?\n".encode())
            if (str(self.socket.recv(100)).find("Elektro-Automatik") != -1):
                self.log.add(self.name, "Соединение по адресу: " + self.ip_adress + ":" + self.port + " установлено", True)
                self.socket.send("SYSTem:LOCK ON\n".encode())
                # self.socket.close()
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
        while True:
            try:
                self.socket = socket.socket()
                self.socket.connect((self.ip_adress, int(self.port)))
                self.log.add(self.name, "Переключение режима ЛБП REMOTE: " + on_off, True)
                message = "SYSTem:LOCK " + on_off + "\n"
                self.socket.send(message.encode())
                self.socket.close()
                return True
            except:
                if i == 3:
                    self.log.add(self.name, "Невозможно переключить в режим ЛБП REMOTE" + on_off, False)
                    return False
                self.log.add(self.name, "Попытка переключения режима ЛБП REMOTE №: " + str(i + 1) + on_off, True)
                i = i + 1

    def check_remote(self, on_off):
        try:
            self.socket = socket.socket()
            self.socket.connect((self.ip_adress, int(self.port)))
            i = 0.5
            while True:
                self.socket.send("SYSTem:LOCK:OWNer?".encode())
                param = str(self.socket.recv(100)).find(on_off)
                if (param != -1):
                    self.log.add(self.name, "Подача команды " + on_off + " на ЛБП успешно прошла", True)
                    self.socket.close()
                    return True
                else:
                    self.log.add(self.name, "Подача команды " + on_off + " на ЛБП не прошла", False)
                    self.socket.close()
                    return False
                i = i + 0.5
                time.sleep(i)
        except:
            self.log.add(self.name, "Подача команды " + on_off + " на ЛБП не прошла", False)
            return False

    def set_voltage(self, value):
        i = 0
        while True:
            try:
                self.socket = socket.socket()
                self.socket.connect((self.ip_adress, int(self.port)))
                voltage = str(value)
                self.log.add(self.name, "Подача команды установить напряжение " + voltage + " В", True)
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
                self.socket = socket.socket()
                self.socket.connect((self.ip_adress, int(self.port)))
                self.socket.send("MEAS:VOLT?\n".encode())
                voltage = number_func(str(self.socket.recv(10)))
                if ((round(float(voltage)) == round(value)) and round(float(voltage)) != 0):
                    self.log.add(self.name, "Напряжение " + str(value) + " В" + " установленно", True)
                    self.socket.close()
                    return True
                if ((round(float(voltage)) != round(value)) and round(float(voltage)) != 0):
                    if (i == 3):
                        self.log.add(self.name, "Значение напряжения отличается " + str(value) + " В" + " не прошла",False)
                        self.socket.close()
                        return False
                    i = i + 1
                    time.sleep(i)
            except:
                if (i == 3):
                    self.log.add(self.name, "Невозможно получить значение напряжения " + voltage + " В", False)
                    return False
                self.log.add(self.name, "Попытка получить значение напряжения " + voltage + " В №" + str(i + 1), True)
                i = i + 1
                time.sleep(i)

    def output(self, on_off):
        self.socket = socket.socket()
        self.socket.connect((self.ip_adress, int(self.port)))
        self.log.add(self.name, "Подача команды на включение выхода ЛБП", True)
        message = "OUTPut " + on_off + "\n"
        self.socket.send(message.encode())
        self.socket.close()

    def check_output(self, on_off):
        self.socket = socket.socket()
        self.socket.connect((self.ip_adress, int(self.port)))
        i = 0.5
        while True:
            self.socket.send("OUTPut?".encode())
            param = str(self.socket.recv(100)).find(on_off)
            if (param != -1):
                self.log.add(self.name, "Подача команды " + on_off + " на ЛБП успешно прошла", True)
                self.socket.close()
                return True
            else:
                self.log.add(self.name, "Подача команды " + on_off + " на ЛБП не прошла", False)
                self.socket.close()
                return False
            i = i + 0.5
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
# задать предполагаемое поведение
class Psc_10:
    psc10_names_ts = ["IN1", "IN2", "IN3", "OUT1", "OUT2", "ERROR_OUT1", "ERROR_OUT2", "ERROR_BTR", "ERROR_I_OUT1",
                      "ERROR_I_OUT2", "PWR_BTR", "TEN", "APTC"]
    psc10_names_ti = {"U_IN1":257, "U_IN2":259, "U_IN3":261, "U_OUT1":263, "U_OUT2":265, "I_OUT1":267, "I_OUT2":269, "I_PWR_BTR":271, "U_PWR_BTR":273, "T1":275,
                      "T2":277, "T3":279, "T4":281, "T5":283}

    def __init__(self, instrument, name, log):
        self.instrument = instrument
        self.name = name
        self.log = log

    def get_ti(self,name_signal):
        i = 0
        while True:
            try:
                value = self.instrument.read_float(self.psc10_names_ti.get(name_signal), 4)
                if (value != None):
                    self.log.add(self.name, "Телеизмерение " + name_signal + " = " + str(round(value, 2)) + " получено", True)
                    return round(value, 2)
                else:
                    if i == 3:
                        self.log.add(self.name, "Ошибка при попытке получения телеизмерения " + name_signal, False)
                        return False
                    i = i + 1
            except:
                if i == 3:
                    self.log.add(self.name, "Критическая ошибка при попытке получения телеизмерения " + name_signal, False)
                    return False
                i = i + 1
                time.sleep(i)

    def check_behaviour(self, behaviour):
        dict = self.get_all_ts()
        i = 0
        if (dict != False):
            for key in behaviour:
                if behaviour[key] != dict[i]:
                    self.log.add(self.name, "Состояние устройства не соответствует действительности", True)
                    return False
                i = i + 1
            self.log.add(self.name, "Состояние устройства соответствует", True)
            return True

    def get_all_ts(self):
        i = 0
        while True:
            try:
                dict = self.instrument.read_registers(1, 13, 4)
                if (len(dict) == 13):
                    self.log.add(self.name, "Состояние получено", True)
                    return dict
                if i == 3:
                    self.log.add(self.name, "Попытка получить состояние устройства №" + str(i + 1), True)
                    return False
                i = i + 1
            except:
                if i == 3:
                    self.log.add(self.name, "Невозможно получить состояние устройства", False)
                    return False
                self.log.add(self.name, "Попытка получить состояние устройства №" + str(i + 1), True)
                i = i + 1
                time.sleep(i)

class Psc_40:
    psc40_names_ts = ["IN1", "IN2", "IN3", "IN4", "U_OUT1", "U_OUT2", "ERROR_KEY1", "ERROR_KEY2", "ERROR_KEY3",
                      "ERROR_KEY4", "PWR_BTR", "TEN", "OVERLOAD_I", "SHORT_I", "BTR_DISCHARGED", "U_IN1", "U_IN2",
                      "U_IN3",
                      "U_IN4", "ERROR_BTR", "APTC"]
    psc40_names_ti = {"U_IN1":257, "U_IN2":259, "U_IN3":261, "U_IN4":263, "U_OUT1":265, "U_OUT2":267, "I_PWR_BTR":269, "U_OUT":271, "I_OUT":273, "T1":275, "T2":277,
                      "T3":279, "T4":281, "T5":283, "T6":285, "T7":287, "T8":289, "U_PWR_BTR":291}

    def __init__(self, instrument, name, log):
        self.instrument = instrument
        self.name = name
        self.log = log

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
# проверяем состояние устройства на соответствие

# расчет процента (только для теста, удалить отсюда)
def percentage(percent, whole):
    return (percent * whole) / 100.0

if __name__ == '__main__':
    # instrument.read_float
    log = engine.Log()
    modb_psc24_10 = Modb().getConnection("PSC24_10", 'com1', 1, log)
    # power_supply = PowerSupply("192.168.0.5", "5025", "ЛБП", log)
    # power_supply.connection()
    psc24_10 = Psc_10(modb_psc24_10, "PSC24_10", log)

    behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0, "error_pwr2": 0, "error_btr": 0,
                 "error_out1": 0, "error_out2": 0, "charge_btr": 1, "ten": 0, "apts": 0}

    print(psc24_10.check_behaviour(behaviour))
    print(log.get_log())

    u_nom = psc24_10.get_ti("U_IN1")
    u_min = u_nom - percentage(1,24)
    u_max = u_nom + percentage(1,24)
    print(24, " номинальное значение")
    print(u_nom, " измеренное значение")
    print(u_min, " минимальное значение")
    print(u_max, " максимальное значение")
    if (u_nom < u_max and u_nom > u_min):
        print("нет погрешности")
    else:
        print("есть погрешности")


    #
    # i = 0
    # while i < 10:
    #     # передать как аргумент
    #     settings = engine.Settings
    #     config = settings.load(settings,"settings.cfg")
    #     print(config)
    #     try:
    #         main_log = engine.Log()
    #         log = engine.Log()
    #         log.set_start(False)
    #         modb_dout_101 = Modb().getConnection("DOUT_101", 'com2', 101, log)
    #         modb_dout_102 = Modb().getConnection("DOUT_102", 'com2', 102, log)
    #         modb_dout_103 = Modb().getConnection("DOUT_103", 'com2', 103, log)
    #         modb_dout_104 = Modb().getConnection("DOUT_104", 'com1', 104, log)
    #         modb_din_201 = Modb().getConnection("DIN_201", 'com2', 201, log)
    #         modb_din_202 = Modb().getConnection("DIN_202", 'com2', 202, log)
    #         modb_psc24_10 = Modb().getConnection("PSC24_10", 'com1', 1, log)
    #         dout_101 = Dout(modb_dout_101, dout_names_101, "DOUT_101", log)
    #         dout_102 = Dout(modb_dout_102, dout_names_102, "DOUT_102", log)
    #         dout_103 = Dout(modb_dout_103, dout_names_103, "DOUT_103", log)
    #         dout_104 = Dout(modb_dout_104, dout_names_104, "DOUT_104", log)
    #         din_201 = Din(modb_din_201, din_names_201, "DIN_201", log)
    #         din_202 = Din(modb_din_202, din_names_202, "DIN_202", log)
    #         # instrument.read_float
    #         power_supply = PowerSupply("192.168.0.5", "5025", "ЛБП", log)
    #         psc24_10 = Psc_10(modb_psc24_10, "PSC24_10", log)
    #
    #         print(log.get_log())
    #
    #         time.sleep(1)
    #         # В зависимости от конфигурации выбираем и включаем блоки питания
    #         if (config.get('power_supply_type') == "wm24_10"):
    #             assert dout_101.command("KL7", "ON")
    #             assert din_201.check_voltage("KL7", "ON")
    #             time.sleep(1)
    #             assert dout_101.command("KL8", "ON")
    #             assert din_201.check_voltage("KL8", "ON")
    #             time.sleep(1)
    #
    #         if (config.get('power_supply_type') == "pw24_5"):
    #             assert dout_101.command("KL15", "ON")
    #             assert din_201.check_voltage("KL15", "ON")
    #             time.sleep(1)
    #             assert dout_101.command("KL16", "ON")
    #             assert din_201.check_voltage("KL16", "ON")
    #             time.sleep(1)
    #
    #         # Конфигурируем ЛБП
    #         power_supply.remote("ON")
    #         assert power_supply.check_remote("REMOTE")
    #         time.sleep(1)
    #         print(log.get_log())
    #         power_supply.output("ON")
    #         assert power_supply.check_output("ON")
    #         time.sleep(1)
    #         print(log.get_log())
    #         # Выставляем напряжение ЛБП
    #         assert power_supply.set_voltage(24)
    #         assert power_supply.check_voltage(24)
    #         time.sleep(1)
    #         print(log.get_log())
    #
    #         # Подаём IN1 с ЛБП
    #         assert dout_102.command("KL30", "ON")
    #         assert din_201.check_voltage("KL30", "ON")
    #         time.sleep(1)
    #         print(log.get_log())
    #
    #
    #         # В зависимости от конфигурации выбираем и отключаем БП IN1
    #         if (config.get('power_supply_type') == "wm24_10"):
    #             assert dout_101.command("KL7", "OFF")
    #             assert din_201.check_voltage("KL7", "OFF")
    #             time.sleep(1)
    #
    #         if (config.get('power_supply_type') == "pw24_5"):
    #             assert dout_101.command("KL15", "OFF")
    #             assert din_201.check_voltage("KL15", "OFF")
    #             time.sleep(1)
    #
    #         #Полаем вход IN1,IN2,IN3
    #         assert dout_103.command("KM7", "ON")
    #         assert din_202.check_voltage("KM7", "ON")
    #         time.sleep(1)
    #         print(log.get_log())
    #         print("Ожидаем включение устройства 25 сек")
    #         time.sleep(5)
    #
    #         print("Ожидаем включение устройства 20 сек")
    #         time.sleep(5)
    #
    #         print("Ожидаем включение устройства 15 сек")
    #         time.sleep(5)
    #
    #         print("Ожидаем включение устройства 10 сек")
    #         time.sleep(5)
    #
    #         print("Ожидаем включение устройства 5 сек")
    #         time.sleep(5)
    #
    #         # Проверяем запуск устройства без АКБ
    #         if (psc24_10.check_status("IN1", "OUT1", "OUT2", "ERROR_BTR") == True) and (psc24_10.check_status("ERROR_OUT1", "ERROR_OUT2","ERROR_I_OUT1", "ERROR_I_OUT2") == False):
    #             log.add("psc24-10 №1", "Устройство исправно", True)
    #         else:
    #             log.add("psc24-10 №1", "Устройство неисправно", True)
    #             assert False
    #         print(log.get_log())
    #         time.sleep(1)
    #
    #         # подаём АКБ на IN3
    #         assert dout_103.command("KM1", "ON")
    #         assert din_202.check_voltage("KM1", "ON")
    #         time.sleep(1)
    #         print(log.get_log())
    #
    #         # Проверяем запуск устройства с АКБ
    #         if (psc24_10.check_status("IN1", "OUT1", "OUT2") == True) and (psc24_10.check_status("ERROR_OUT1", "ERROR_OUT2", "ERROR_BTR", "ERROR_I_OUT1", "ERROR_I_OUT2") == False):
    #             log.add("psc24-10 №1", "Устройство исправно", True)
    #         else:
    #             log.add("psc24-10 №1", "Устройство неисправно", True)
    #             assert False
    #         print(log.get_log())
    #         time.sleep(1)
    #
    #         #Понижаем напряжение IN1 устройство должно быть исправно
    #         power_supply.set_voltage(21.5)
    #         time.sleep(5)
    #         assert power_supply.check_voltage(21.5)
    #
    #         print(log.get_log())
    #
    #         # Проверяем что IN1 не вышел из-строя
    #         if (psc24_10.check_status("IN1", "OUT1", "OUT2") == True) and (psc24_10.check_status("ERROR_OUT1", "ERROR_OUT2", "ERROR_BTR", "ERROR_I_OUT1", "ERROR_I_OUT2") == False):
    #             log.add("psc24-10 №1", "Устройство исправно", True)
    #         else:
    #             log.add("psc24-10 №1", "Устройство неисправно", True)
    #             assert False
    #         print(log.get_log())
    #         time.sleep(1)
    #
    #         #Понижаем напряжение IN1 до порога срабатывания U MIN
    #         power_supply.set_voltage(20)
    #         time.sleep(5)
    #         assert power_supply.check_voltage(20)
    #         print(log.get_log())
    #
    #         # Проверяем что IN1 неисправен и IN2 активный канал
    #         if (psc24_10.check_status("IN2", "OUT1", "OUT2","ERROR_OUT1") == True) and (psc24_10.check_status("IN1", "ERROR_OUT2", "ERROR_BTR", "ERROR_I_OUT1", "ERROR_I_OUT2") == False):
    #             log.add("psc24-10 №1", "Устройство исправно", True)
    #         else:
    #             log.add("psc24-10 №1", "Устройство неисправно", True)
    #             assert False
    #         print(log.get_log())
    #         time.sleep(1)
    #
    #         #Повышаем напряжение IN1 устройство должно быть исправно
    #         power_supply.set_voltage(26)
    #         time.sleep(5)
    #         assert power_supply.check_voltage(26)
    #         time.sleep(1)
    #         print(log.get_log())
    #
    #         # Проверяем что IN1 восстановился
    #         if (psc24_10.check_status("IN1", "OUT1", "OUT2") == True) and (psc24_10.check_status("ERROR_OUT1", "ERROR_OUT2", "ERROR_BTR", "ERROR_I_OUT1", "ERROR_I_OUT2") == False):
    #             log.add("psc24-10 №1", "Устройство исправно", True)
    #         else:
    #             log.add("psc24-10 №1", "Устройство неисправно", True)
    #             assert False
    #         print(log.get_log())
    #         time.sleep(1)
    #
    #         #Повышаем напряжение IN1 до порога срабатывания U MAX
    #         power_supply.set_voltage(27)
    #         time.sleep(5)
    #         assert power_supply.check_voltage(27)
    #         time.sleep(3)
    #         print(log.get_log())
    #
    #         # Проверяем что IN1 неисправен и IN2 активный канал
    #         if (psc24_10.check_status("IN2", "OUT1", "OUT2","ERROR_OUT1") == True) and (psc24_10.check_status("IN1", "ERROR_OUT2", "ERROR_BTR", "ERROR_I_OUT1", "ERROR_I_OUT2") == False):
    #             log.add("psc24-10 №1", "Устройство исправно", True)
    #         else:
    #             log.add("psc24-10 №1", "Устройство неисправно", True)
    #             assert False
    #         print(log.get_log())
    #         time.sleep(1)
    #
    #         #Регулируем ЛБП на Uном
    #         power_supply.set_voltage(24)
    #         time.sleep(5)
    #         assert power_supply.check_voltage(24)
    #         time.sleep(3)
    #         print(log.get_log())
    #
    #         #Отключаем ЛБП IN1 и включаем ЛБП IN2
    #         assert dout_102.command("KL30", "OFF")
    #         assert din_201.check_voltage("KL30", "OFF")
    #         time.sleep(1)
    #         print(log.get_log())
    #         assert dout_102.command("KL31", "ON")
    #         assert din_201.check_voltage("KL31", "ON")
    #         time.sleep(1)
    #         print(log.get_log())
    #
    #         # В зависимости от конфигурации выбираем и отключаем БП IN2
    #         if (config.get('power_supply_type') == "wm24_10"):
    #             assert dout_101.command("KL8", "OFF")
    #             assert din_201.check_voltage("KL8", "OFF")
    #             time.sleep(1)
    #
    #         if (config.get('power_supply_type') == "pw24_5"):
    #             assert dout_101.command("KL16", "OFF")
    #             assert din_201.check_voltage("KL16", "OFF")
    #             time.sleep(1)
    #
    #         # Проверяем что устройство работает с IN2
    #         if (psc24_10.check_status("IN2", "OUT1", "OUT2","ERROR_OUT1") == True) and (psc24_10.check_status("IN1", "ERROR_OUT2", "ERROR_BTR", "ERROR_I_OUT1", "ERROR_I_OUT2") == False):
    #             log.add("psc24-10 №1", "Устройство исправно", True)
    #         else:
    #             log.add("psc24-10 №1", "Устройство неисправно", True)
    #             assert False
    #         print(log.get_log())
    #         time.sleep(1)
    #
    #         # Понижаем напряжение IN2 устройство должно быть исправно
    #         power_supply.set_voltage(21.5)
    #         time.sleep(5)
    #         assert power_supply.check_voltage(21.5)
    #         time.sleep(1)
    #         print(log.get_log())
    #
    #         # Проверяем что IN2 не вышел из-строя
    #         if (psc24_10.check_status("IN2", "OUT1", "OUT2","ERROR_OUT1") == True) and (
    #                 psc24_10.check_status( "ERROR_OUT2", "ERROR_BTR", "ERROR_I_OUT1","ERROR_I_OUT2") == False):
    #             log.add("psc24-10 №1", "Устройство исправно", True)
    #         else:
    #             log.add("psc24-10 №1", "Устройство неисправно", True)
    #             assert False
    #         print(log.get_log())
    #         time.sleep(1)
    #
    #         # Понижаем напряжение IN2 до порога срабатывания U MIN
    #         power_supply.set_voltage(20)
    #         time.sleep(5)
    #         assert power_supply.check_voltage(20)
    #         time.sleep(3)
    #         print(log.get_log())
    #
    #         # Проверяем что IN2 неисправен и IN3 активный канал
    #         if (psc24_10.check_status("IN3", "OUT1", "OUT2", "ERROR_OUT1", "ERROR_OUT2") == True) and (
    #                 psc24_10.check_status("IN2", "ERROR_BTR", "ERROR_I_OUT1", "ERROR_I_OUT2") == False):
    #             log.add("psc24-10 №1", "Устройство исправно", True)
    #         else:
    #             log.add("psc24-10 №1", "Устройство неисправно", True)
    #             assert False
    #         print(log.get_log())
    #         time.sleep(1)
    #
    #         #Повышаем напряжение IN2 устройство должно быть исправно
    #         power_supply.set_voltage(26)
    #         time.sleep(5)
    #         assert power_supply.check_voltage(26)
    #         time.sleep(1)
    #         print(log.get_log())
    #
    #         # Проверяем что IN2 восстановился
    #         if (psc24_10.check_status("IN2", "OUT1", "OUT2","ERROR_OUT1",) == True) and (
    #                 psc24_10.check_status( "ERROR_OUT2", "ERROR_BTR", "ERROR_I_OUT1","ERROR_I_OUT2") == False):
    #             log.add("psc24-10 №1", "Устройство исправно", True)
    #         else:
    #             log.add("psc24-10 №1", "Устройство неисправно", True)
    #             assert False
    #         print(log.get_log())
    #         time.sleep(1)
    #
    #         #Повышаем напряжение IN2 до порога срабатывания U MAX
    #         power_supply.set_voltage(27)
    #         time.sleep(5)
    #         assert power_supply.check_voltage(27)
    #         time.sleep(3)
    #         print(log.get_log())
    #
    #         # Проверяем что IN2 неисправен и IN3 активный канал
    #         if (psc24_10.check_status("IN3", "OUT1", "OUT2", "ERROR_OUT1", "ERROR_OUT2") == True) and (psc24_10.check_status("IN2", "ERROR_BTR", "ERROR_I_OUT1", "ERROR_I_OUT2") == False):
    #             log.add("psc24-10 №1", "Устройство исправно", True)
    #         else:
    #             log.add("psc24-10 №1", "Устройство неисправно", True)
    #             assert False
    #         print(log.get_log())
    #         time.sleep(1)
    #
    #         #Регулируем ЛБП на Uном
    #         power_supply.set_voltage(24)
    #         time.sleep(5)
    #         assert power_supply.check_voltage(24)
    #         print(log.get_log())
    #
    #         # Проверяем что IN2 восстановился и зарядку АКБ
    #         if (psc24_10.check_status("IN2", "OUT1", "OUT2", "ERROR_OUT1", "PWR_BTR") == True) and (psc24_10.check_status("ERROR_OUT2", "ERROR_BTR", "ERROR_I_OUT1", "ERROR_I_OUT2") == False):
    #             log.add("psc24-10 №1", "Устройство исправно", True)
    #         else:
    #             log.add("psc24-10 №1", "Устройство неисправно", True)
    #             assert False
    #         print(log.get_log())
    #         time.sleep(1)
    #
    #         # В зависимости от конфигурации выбираем и включаем блоки питания
    #         if (config.get('power_supply_type') == "wm24_10"):
    #             assert dout_101.command("KL7", "ON")
    #             assert din_201.check_voltage("KL7", "ON")
    #             time.sleep(1)
    #             assert dout_101.command("KL8", "ON")
    #             assert din_201.check_voltage("KL8", "ON")
    #             time.sleep(1)
    #
    #         if (config.get('power_supply_type') == "pw24_5"):
    #             assert dout_101.command("KL15", "ON")
    #             assert din_201.check_voltage("KL15", "ON")
    #             time.sleep(1)
    #             assert dout_101.command("KL16", "ON")
    #             assert din_201.check_voltage("KL16", "ON")
    #             time.sleep(1)
    #
    #         # Отключаем ЛБП
    #             power_supply.remote("OFF")
    #             assert power_supply.check_output("OFF")
    #             time.sleep(1)
    #             print(log.get_log())
    #             print("Проверка успешно завершена, устройство исправно!")
    #
    #         # Проверяем запуск устройства с АКБ
    #         if (psc24_10.check_status("IN1", "OUT1", "OUT2") == True) and\
    #                 (psc24_10.check_status("ERROR_OUT1", "ERROR_OUT2", "ERROR_BTR", "ERROR_I_OUT1", "ERROR_I_OUT2") == False):
    #             log.add("psc24-10 №1", "Устройство исправно", True)
    #         else:
    #             log.add("psc24-10 №1", "Устройство неисправно", True)
    #             assert False
    #         print(log.get_log())
    #         time.sleep(1)
    #
    #         #Отключаем АКБ
    #         # Отключаем АКБ на IN3
    #         assert dout_103.command("KM1", "OFF")
    #         assert din_202.check_voltage("KM1", "OFF")
    #         time.sleep(1)
    #         print(log.get_log())
    #
    #         # В зависимости от конфигурации выбираем и отключаем блоки питания
    #         if (config.get('power_supply_type') == "wm24_10"):
    #             assert dout_101.command("KL7", "OFF")
    #             assert din_201.check_voltage("KL7", "OFF")
    #             time.sleep(1)
    #             assert dout_101.command("KL8", "OFF")
    #             assert din_201.check_voltage("KL8", "OFF")
    #             time.sleep(1)
    #
    #         if (config.get('power_supply_type') == "pw24_5"):
    #             assert dout_101.command("KL15", "OFF")
    #             assert din_201.check_voltage("KL15", "OFF")
    #             time.sleep(1)
    #             assert dout_101.command("KL16", "OFF")
    #             assert din_201.check_voltage("KL16", "OFF")
    #             time.sleep(1)
    #
    #             # Отключаем общий вход IN1,IN2,IN3
    #             assert dout_103.command("KM7", "OFF")
    #             assert din_202.check_voltage("KM7", "OFF")
    #             time.sleep(1)
    #             print(log.get_log())
    #
    #             #Отключаем ЛБП на IN2
    #             assert dout_102.command("KL31", "OFF")
    #             assert din_201.check_voltage("KL31", "OFF")
    #             time.sleep(1)
    #             print(log.get_log())
    #
    #             print("Проверка №"+str(i)+" успешно завершена!")
    #             i = i + 1
    #     except AssertionError:
    #         print(log.get_log())
    #         print('НУ и хорош!')
    #         print("Устройств было проверено ",i)
    #         break






