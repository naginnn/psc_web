import pickle
from datetime import datetime
import devices
import time
from threading import Thread, Lock
dout_names_101 = {"KL1":81,"KL2":82,"KL3":83,"KL4":84,"KL5":85,"KL6":86,"KL7":87,"KL8":88,"KL9":89,"KL10":90,"KL11":91,"KL12":92,"KL13":93,"KL14":94,"KL15":95,"KL16":96}
dout_names_102 = {"KL17":81,"KL18":82,"KL19":83,"KL20":84,"KL21":85,"KL22":86,"KL23":87,"KL24":88,"KL25":89,"KL26":90,"KL27":91,"KL28":92,"KL29":93,"KL30":94,"KL31":95,"KL32":96}
dout_names_103 = {"KL33":81,"KM1":82,"KM2":83,"KM3":84,"KM4":85,"KM5":86,"KM6":87,"KM7":88,"KM8":89,"KM9":90,"KM10":91,"KM11":92,"KM14":93,"KM15":94,"KM16":95,"KM17":96}
dout_names_104 = {"KM18":81,"KM19":82,"KM12":83,"KM13":84,"KM20":85,"KM21":86,"KM22":87,"KM23":88}
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
                 "SF4": "Цепь IN1", "SF5": "Цепь IN2", "SF6": "Цепь IN3", "SF7": "Цепь IN4","KM20": "Прибавить 10А(реостат)", "KM21": "Прибавить 20А(реостат)", "KM22": "Прибавить 40А(реостат)", "KM23": "Прибавить 40А(реостат)"
                 }

# чтение web конфигурации
class Settings:
    # def __init__(self, log):
    #     self.log = log
    data = {}
    device_type = ()
    device_name = ()
    power_supply_type = ()
    voltage_thresholds = ()
    switch_channel = ()
    warmup_time = ()

    def save(self,filename, data):
        self.log.add("Сохранение", "Сохраняем конфигурацию", True)
        try:
            with open(filename, 'wb+') as f:
                pickle.dump(data, f)
            return True
        except:
            return False

    def load(self, filename):
        try:
            with open(filename, 'rb') as f:
                while True:
                    try:
                        # self.data.append()
                        # print(self.data)
                        return pickle.load(f)
                    except EOFError:
                        return False
        except:
            print("Файла конфигурации не существует! Сначала сохраните конфигурацию!")
            return False

# лог объект
class Log:
    filename = str(datetime.now().strftime('%d.%m.%Y-%H-%M')) + ".log"
    log = str()
    log_data = []
    log_result = []
    start = True
    finish = False


    def add(self, name, event, result):
        self.log = self.log + datetime.now().strftime('%H:%M:%S.%f')[:-4] + " " + name + ":" + " " + event + "\n"
        self.log_data.append(datetime.now().strftime('%H:%M:%S.%f')[:-4] + " " +name + ":" + " " + event + "\n")
        self.log_result.append(result)

    def get_log_result(self):
        return self.log_result

    def get_log_data(self):
        return self.log_data

    def get_log(self):
        return self.log

    def get_finish(self):
        return self.finish

    def set_finish(self,finish):
        self.finish = finish

    def get_start(self):
        return self.start

    def set_start(self,start):
        self.start = start

    def log_clear_data(self):
        self.log_data.clear()

    def log_clear_result(self):
        self.log_result.clear()

# диагностика стенда (исправить, бомжатская)
class Diagnostics:
    def __init__(self,name, log):
        self.name = name
        self.log = log

    def diagnostics(self, key):
        self.log.set_start(False)
        self.modb_dout_101 = devices.Modb().getConnection("DOUT_101", 'com1', 101, self.log)
        self.modb_dout_102 = devices.Modb().getConnection("DOUT_102", 'com1', 102, self.log)
        self.modb_dout_103 = devices.Modb().getConnection("DOUT_103", 'com1', 103, self.log)
        self.modb_dout_104 = devices.Modb().getConnection("DOUT_104", 'com1', 104, self.log)
        self.modb_din_201 = devices.Modb().getConnection("DIN_201", 'com1', 201, self.log)
        self.modb_din_202 = devices.Modb().getConnection("DIN_202", 'com1', 202, self.log)

        self.dout_101 = devices.Dout(self.modb_dout_101, dout_names_101, "DOUT_101", self.log)
        self.dout_102 = devices.Dout(self.modb_dout_102, dout_names_102, "DOUT_102", self.log)
        self.dout_103 = devices.Dout(self.modb_dout_103, dout_names_103, "DOUT_103", self.log)
        self.dout_104 = devices.Dout(self.modb_dout_104, dout_names_104, "DOUT_104", self.log)
        self.din_201 = devices.Din(self.modb_din_201, din_names_201, "DIN_201", self.log)
        self.din_202 = devices.Din(self.modb_din_202, din_names_202, "DIN_202", self.log)
        error_code = False
        error_count = 0
        i = 0
        command_101 = list(dout_names_101.keys())
        command_102 = list(dout_names_102.keys())
        command_103 = list(dout_names_103.keys())
        command_104 = list(dout_names_104.keys())
        #dds
        if ((self.modb_dout_101 != False) and (self.modb_din_201 != False)):
            while i < len(dout_names_101):
                if self.dout_101.command(command_101[i],key):
                    self.din_201.check_voltage(command_101[i], key)
                    time.sleep(1)
                    if self.dout_101.command(command_101[i],"OFF"):
                        self.din_201.check_voltage(command_101[i], "OFF")
                    else:
                        error_code = True
                        error_count = error_count + 1
                else:
                    error_code = True
                    error_count = error_count + 1
                time.sleep(1)
                i = i + 1
        else:
            error_code = True
            error_count = error_count + 2

        i = 0
        if ((self.modb_dout_102 != False) and (self.modb_din_201 != False)):
            while i < len(dout_names_102):
                if self.dout_102.command(command_102[i],key):
                    self.din_201.check_voltage(command_102[i],key)
                    time.sleep(1)
                    if self.dout_102.command(command_102[i], "OFF"):
                        self.din_201.check_voltage(command_102[i], "OFF")
                    else:
                        error_code = True
                        error_count = error_count + 1
                else:
                    error_code = True
                    error_count = error_count + 1
                time.sleep(0.5)
                i = i + 1
        else:
            error_code = True
            error_count = error_count + 2

        i = 0
        if ((self.modb_dout_103 != False) and (self.modb_din_202 != False)):
            while i < len(dout_names_103):
                if self.dout_103.command(command_103[i],key):
                    self.din_202.check_voltage(command_103[i], key)
                    time.sleep(1)
                    if self.dout_103.command(command_103[i], "OFF"):
                        self.din_202.check_voltage(command_103[i], "OFF")
                    else:
                        error_code = True
                        error_count = error_count + 1
                else:
                    error_code = True
                    error_count = error_count + 1
                time.sleep(1)
                i = i + 1
        else:
            error_code = True
            error_count = error_count + 2

        i = 0
        if ((self.modb_dout_104 != False) and (self.modb_din_202 != False)):
            while i < len(dout_names_104):
                if self.dout_104.command(command_104[i],key):
                    self.din_202.check_voltage(command_104[i], key)
                    time.sleep(1)
                    if self.dout_104.command(command_104[i], "OFF"):
                        self.din_202.check_voltage(command_104[i], "OFF")
                    else:
                        error_code = True
                        error_count = error_count + 1
                else:
                    error_code = True
                    error_count = error_count + 1
                time.sleep(1)
                i = i + 1
        else:
            error_code = True
            error_count = error_count + 2

        if error_code:
            self.log.add(self.name, "Диагностика завершена, ошибок: " + str(error_count), True)
        else:
            self.log.add(self.name, "Диагностика завершена, нет ошибок", True)
        self.log.set_finish(True)

# Проверки устройства
class Checking:

    def __init__(self, name, log, device_log, settings):
        self.name = name
        self.control_log = log
        self.main_log = device_log
        self.settings = settings
        self.config = self.settings.load("settings.cfg")
        self.power_supply_type = self.config.get('power_supply_type')
        self.checked_list = int(self.config.get('checked_list'))
        self.device_name = self.config.get('device_name')

    # подготовка
    def prepare(self):
        print("")

    # первое включение
    def first_start(self):
        print("")

    # Проверка порогов по напряжению
    def check_voltage_thresholds(self):
        print("")

    # переключение каналов
    def switch_channel(self):
        ### Пинги управление
        print("Переключение каналов (Проверка провалов по напряжению)")

    def check_sensor(self):
        print("Проверка датчика")

    def dry_contact(self):
        print("Проверка сухого контакта")

    def overload_mode(self):
        print("Режим перегрузки")

    def sc_mode_func(self):
        print("Режим короткого замыкания")

    def check_device(self):
        print("Проверка устройства")


# главный метод используемый в web'е, перетащить его в класс checking после тестирования
if __name__ == "__main__":
    control_log = Log()

    modb_dout_101 = devices.Modb().getConnection("DOUT_101", 'com1', 101, control_log)
    modb_dout_102 = devices.Modb().getConnection("DOUT_102", 'com1', 102, control_log)
    modb_dout_103 = devices.Modb().getConnection("DOUT_103", 'com1', 103, control_log)
    modb_dout_104 = devices.Modb().getConnection("DOUT_104", 'com1', 104, control_log)
    modb_din_201 = devices.Modb().getConnection("DIN_201", 'com1', 201, control_log)
    modb_din_202 = devices.Modb().getConnection("DIN_202", 'com1', 202, control_log)

    dout_101 = devices.Dout(modb_dout_101, dout_names_101, "DOUT_101", control_log)
    dout_102 = devices.Dout(modb_dout_102, dout_names_102, "DOUT_102", control_log)
    dout_103 = devices.Dout(modb_dout_103, dout_names_103, "DOUT_103", control_log)
    dout_104 = devices.Dout(modb_dout_104, dout_names_104, "DOUT_104", control_log)
    din_201 = devices.Din(modb_din_201, din_names_201, "DIN_201", control_log)
    din_202 = devices.Din(modb_din_202, din_names_202, "DIN_202", control_log)

    device_log = Log()

