import pickle
from datetime import datetime
import devices
import time
from threading import Thread, Lock

import read_write_eeprom

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

# чтение web конфигурации (добавить лог)
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

    def save(self, filename, data):
        # self.log.add("Сохранение", "Сохраняем конфигурацию", True)
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
    device_count = 0

    def add(self, name, event, result):
        self.log = self.log + datetime.now().strftime('%H:%M:%S.%f')[:-4] + " " + name + ":" + " " + event + "\n"
        self.log_data.append(datetime.now().strftime('%H:%M:%S.%f')[:-4] + " " +name + ":" + " " + event + "\n")
        self.log_result.append(result)

    def reset_log(self):
        self.log = str()
        self.log_data = []
        self.log_result = []
        self.start = True
        self.finish = False
        self.device_count = 0

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

    def set_device_count(self, device_count):
        self.device_count = int(device_count)

    def get_device_count(self):
        return self.device_count

# диагностика стенда (исправить, бомжатская) не будет работать другая инициализация модулей управления
# изменить цикл включения отключения
class Diagnostics:
    def __init__(self,name, log):
        self.name = name
        self.log = log

    # переделать циклы со списками
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

# Проверка устройства psc24_10
class Check_psc24_10:

    # создаем список с измерениями
    measurements = {"IN1": {"u_nom" : 0.0, "u_fact" : 0.0, "error_rate" : 0.0},
                    "IN2": {"u_nom": 0.0, "u_fact": 0.0, "error_rate": 0.0},
                    "IN3": {"u_nom": 0.0, "u_fact": 0.0, "error_rate": 0.0},
                    "U_OUT1": {"u_nom": 0.0, "u_fact": 0.0, "error_rate": 0.0},
                    "U_OUT2": {"u_nom": 0.0, "u_fact": 0.0, "error_rate": 0.0},
                    "I_OUT1": {"i_nom": 0.0, "i_fact": 0.0, "error_rate": 0.0},
                    "I_OUT2": {"i_nom": 0.0, "i_fact": 0.0, "error_rate": 0.0},
                    }
    # предполагаемое поведение
    behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0, "error_pwr2": 0, "error_btr": 0,
                 "error_out1": 0, "error_out2": 0, "charge_btr": 1, "ten": 0, "apts": 0}
    u_nom = 25.14
    i_nom = 0.0
    u_in1_fact = 0.0
    u_in2_fact = 0.0
    u_in3_fact = 0.0
    i_out1_fact = 0.0
    i_out2_fact = 0.0
    # списки для будущего протокола
    serial_number = {'Серийный номер': [' ']}
    soft_version = {'Версия ПО': ['1.2.3.8'],'Фактическая': [' ']}
    voltage = {'Канал, U': ['IN1', 'IN2', 'IN3'], 'Unom': ['', '', ''], 'Ufact': ['', '', ''], 'Uerror_rate': ['', '', '']}
    current = { 'Канал, I': ['OUT1', 'OUT2', '', ''], 'Inom': ['', '', '', ''], 'Ifact': ['', '', '', ''], 'Ierror_rate': ['', '', '', '']}
    voltage_threesolds = {'Пороги по напряжению': ['min', 'nom', 'max', ''], 'U': ['', '', '', ''], 'Результат': ['', '', '', '']}
    switching_channels = {'Переключение каналов': ['Под Imin 0A', 'Под Imax 10A', '', ''], 'Канал 1': ['', '', '', ''], 'Время, t': ['', '', '', ''], 'Канал 2': ['', '', '', '']}
    ten = {'Работа ТЭН': [' ']}
    emergency_modes = {'Аварийные режимы': ['Режим КЗ', 'Режим перегрузки', 'Обрыв связи датчика', ''], 'Результат': ['', '', '', '']}

    # объявляем модули управления
    dout_101 = ()
    dout_102 = ()
    dout_103 = ()
    dout_104 = ()
    dout_201 = ()
    dout_202 = ()
    psc24_10 = ()
    power_supply = ()
    ammeter_out1 = ()
    ammeter_out2 = ()
    IN1 = ""
    IN2 = ""
    BTR = "KM1"

    eeprom = ()
    power_management = ()
    # добавляем два лога и ком-порт модулям управления и psc
    def __init__(self, name, control_log, control_com, main_log, device_com, settings):
        self.name = name
        self.control_log = control_log
        self.main_log = main_log
        self.control_com = control_com
        self.device_com = device_com
        self.settings = settings

    # расчет процента
    def percentage(self, percent, whole):
        return (percent * whole) / 100.0

    # расчет погрешности, передаем поданное напряжение с ЛБП и фактическое с устройства, получаем результат true/false
    # Для напряжения percent = 5%, для тока percent = 15%
    def check_error_rate(self, nom, fact, percent):
        delta = self.percentage(percent, nom)
        max = round(nom + delta, 2)
        min = round(nom - delta, 2)
        if (fact >= min) and (fact <= max):
            return True
        return False

    # подготовка Stage 1
    def prepare(self):
        # Инициализируем модули управления
        try:
            self.control_log.add(self.name, "Stage 1: Инициализация модулей управления", True)
            # модули DOUT
            modb_dout_101 = devices.Modb()
            assert modb_dout_101.getConnection("DOUT_101", self.control_com, 101, 115200, self.control_log)
            modb_dout_102 = devices.Modb()
            assert modb_dout_102.getConnection("DOUT_102", self.control_com, 102, 115200, self.control_log)
            modb_dout_103 = devices.Modb()
            assert modb_dout_103.getConnection("DOUT_103", self.control_com, 103, 115200, self.control_log)
            modb_dout_104 = devices.Modb()
            assert modb_dout_104.getConnection("DOUT_104", self.control_com, 104, 115200, self.control_log)
            modb_din_201 = devices.Modb()
            # модули DIN
            assert modb_din_201.getConnection("DIN_201", self.control_com, 201, 115200, self.control_log)
            modb_din_202 = devices.Modb()
            assert modb_din_202.getConnection("DIN_202", self.control_com, 202, 115200, self.control_log)
            modb_ammeter_out1 = devices.Modb()
            # амперметры
            assert modb_ammeter_out1 .getConnection("Амперметр", self.control_com, 5, 19200, self.control_log)
            modb_ammeter_out2 = devices.Modb()
            assert modb_ammeter_out2 .getConnection("Амперметр", self.control_com, 6, 19200, self.control_log)

            config = self.settings.load("settings.cfg")
            self.power_supply = devices.PowerSupply(config.get("ip_adress"), config.get("port"), "ЛБП",self.control_log)
            assert self.power_supply.connection()

            self.dout_101 = devices.Dout(modb_dout_101.getСonnectivity(), dout_names_101, "DOUT_101", self.control_log, 10)
            self.dout_102 = devices.Dout(modb_dout_102.getСonnectivity(), dout_names_102, "DOUT_102", self.control_log, 10)
            self.dout_103 = devices.Dout(modb_dout_103.getСonnectivity(), dout_names_103, "DOUT_103", self.control_log, 10)
            self.dout_104 = devices.Dout(modb_dout_104.getСonnectivity(), dout_names_104, "DOUT_104", self.control_log, 10)
            self.din_201 = devices.Din(modb_din_201.getСonnectivity(), din_names_201, "DIN_201", self.control_log, 10)
            self.din_202 = devices.Din(modb_din_202.getСonnectivity(), din_names_202, "DIN_202", self.control_log, 10)
            self.ammeter_out1 = devices.Ammeter(modb_ammeter_out1.getСonnectivity(), "Амперметр OUT1", self.control_log, 10)
            self.ammeter_out2 = devices.Ammeter(modb_ammeter_out2.getСonnectivity(), "Амперметр OUT2", self.control_log, 10)
            return True
        except:
            self.control_log.add(self.name, "Error #1: Ошибка инициализации модулей управления", False)
            return False
    # первое включение проверка состояния Stage 2
    def first_start(self):
        self.control_log.add(self.name, "Stage 2 Подготовка к первому запуску", True)
        # подаём 3 канала с ЛБП
        try:
            # # Конфигурируем ЛБП
            # assert self.power_supply.remote("ON")
            # assert self.power_supply.check_remote("REMOTE")
            # time.sleep(1)
            # assert self.power_supply.output("ON")
            # assert self.power_supply.check_output("ON")
            # time.sleep(1)
            #
            # # Подключаем входа
            # assert self.dout_102.command("KL30", "ON")
            # assert self.din_201.check_voltage("KL30", "ON")
            # assert self.dout_102.command("KL31", "ON")
            # assert self.din_201.check_voltage("KL31", "ON")
            # assert self.dout_102.command("KL33", "ON")
            # assert self.din_201.check_voltage("KL33", "ON")
            # assert self.power_supply.connection()
            # assert self.power_supply.set_voltage(24)

            # правильная инициализация modbus
            modb_psc24_10 = devices.Modb()
            assert modb_psc24_10.getConnection("PSC24_10", self.device_com, 1, 115200, self.control_log)
            self.psc24_10 = devices.Psc_10(modb_psc24_10.getСonnectivity(), "PSC24_10", self.control_log, 30)

            # ждем включения устройства и передаем предполагаемое поведение
            assert self.psc24_10.check_behaviour(self.behaviour)
            return True
        except:
            self.control_log.add(self.name, "Error #2: Подготовка к первому запуску не прошла", False)
            return False
    #  считывание и проверка конфигурации Stage 3
    def configurate_check(self):
        self.control_log.add(self.name, "Stage 3 Проверка и запись конфигурации", True)
        try:
            self.eeprom = read_write_eeprom.ReadWriteEEprom("EEPROM", self.control_log, self.device_com, 115200, 30)
            assert self.eeprom.read_soft_version()
            config = self.settings.load("settings.cfg")
            soft_version = config.get("soft_version")
            if self.eeprom.get_soft_version() == soft_version:
                self.soft_version['Фактическая'] = [self.eeprom.get_soft_version()]
                self.control_log.add(self.name,
                                     "Версия прошивки совпадает с актуальной: " + self.eeprom.get_soft_version() + " = " + soft_version,
                                     True)
            else:
                self.soft_version['Фактическая'] = [self.eeprom.get_soft_version()]
                self.control_log.add(self.name,
                                     "Не актуальная версия прошивки: " + self.eeprom.get_soft_version() + " != " + soft_version,
                                     False)
                assert False
            # считываем серийный номер
            assert self.eeprom.read_serial_number()
            self.serial_number['Серийный номер'] = [self.eeprom.get_serial_number()]
            # читаем конфигурацию assert/ получать setting getter'ом
            config = self.settings.load("settings.cfg")
            # выбираем блоки
            if config.get("power_supply_type") == "wm24_10":
                self.IN1 = "KL7"
                self.IN2 = "KL8"
            if config.get("power_supply_type") == "pw24_5":
                self.IN1 = "KL15"
                self.IN2 = "KL16"
            assert self.eeprom.read_power_management()
            self.power_management = self.eeprom.get_power_management()
            return True
        except:
            self.control_log.add(self.name, "Error #3: Ошибка при проверке и записи конфигурации", False)
            return False

    # проверка телеизмерения Stage 4
    def measurements_check(self):
        self.control_log.add(self.name, "Stage 4 Проверка измерений", True)
        try:
            # подать нагрузку
            # проверяем на погрешности
            assert self.psc24_10.check_ti("U_IN1")
            self.u_in1_fact = self.psc24_10.get_ti()
            assert self.check_error_rate(self.u_nom, self.u_in1_fact, 5)
            self.voltage['Unom'][0] = self.u_nom
            self.voltage['Ufact'][0] = self.u_in1_fact
            self.control_log.add(self.name,
                                 "IN1: Номинальное напряжение " + str(self.u_nom) + " Фактическое " + str(self.u_in1_fact),
                                 True)

            assert self.psc24_10.check_ti("U_IN2")
            self.u_in2_fact = self.psc24_10.get_ti()
            assert self.check_error_rate(self.u_nom, self.u_in2_fact, 5)
            self.voltage['Unom'][1] = self.u_nom
            self.voltage['Ufact'][1] = self.u_in2_fact
            self.control_log.add(self.name,
                                 "IN2: Номинальное напряжение " + str(self.u_nom) + " Фактическое " + str(self.u_in2_fact),
                                 True)

            assert self.psc24_10.check_ti("U_IN3")
            self.u_in3_fact = self.psc24_10.get_ti()
            assert self.check_error_rate(self.u_nom, self.u_in3_fact, 5)
            self.voltage['Unom'][2] = self.u_nom
            self.voltage['Ufact'][2] = self.u_in3_fact
            self.control_log.add(self.name,
                                 "IN3: Номинальное напряжение " + str(self.u_nom) + " Фактическое " + str(self.u_in3_fact),
                                 True)

            # подать токи на выхода
            # и добавить второй датчик
            assert self.psc24_10.check_ti("I_OUT1")
            self.i_out1_fact = self.psc24_10.get_ti()
            assert self.ammeter.check_ti()
            self.i_nom = self.ammeter.get_ti()
            assert self.check_error_rate(self.i_nom, self.i_out1_fact, 15)
            self.current['Inom'][0] = self.i_nom
            self.current['Ifact'][0] = self.i_out1_fact
            self.control_log.add(self.name,
                                 "OUT1: Номинальный ток " + str(self.i_nom) + " Фактический " + str(self.i_out1_fact), True)

            assert self.psc24_10.check_ti("I_OUT2")
            self.i_out2_fact = self.psc24_10.get_ti()
            assert self.ammeter.check_ti()
            self.i_nom = self.ammeter.get_ti()
            assert self.check_error_rate(self.i_nom, self.i_out2_fact, 15)
            self.current['Inom'][1] = self.i_nom
            self.current['Ifact'][1] = self.i_out2_fact
            self.control_log.add(self.name,
                                 "OUT1: Номинальный ток " + str(self.i_nom) + " Фактический " + str(self.i_out2_fact), True)
        except:
            self.control_log.add(self.name, "Error #4: Ошибка при проверке измерений", False)
            return False
        # если токовые каналы в параллель то проверить, что разница между ними
        # не более 500mA
    # Проверка порогов по напряжению
    def check_voltage_thresholds(self):
        try:
            assert self.dout_102.command("KL30", "ON")
            assert self.din_201.check_voltage("KL30", "ON")
            assert self.dout_102.command("KL31", "ON")
            assert self.din_201.check_voltage("KL31", "ON")
            assert self.dout_102.command("KL33", "ON")
            assert self.din_201.check_voltage("KL33", "ON")
        except AssertionError:
            print("Boroda")

    # переключение каналов
    def switch_channel(self):
        ### Пинги управление
        print("Переключение каналов (Проверка провалов по напряжению)")

    # проверка ТЭН'а и обрыв связи с датчиком
    def check_ten(self):
        print("Проверка датчика")

    # аварийные режимы работы
    def crash_mode(self):
        print("Режим перегрузки")

    def for_test(self):
        try:
            modb_dout_101 = devices.Modb()
            assert modb_dout_101.getConnection("DOUT_101", self.control_com, 101, 115200, self.control_log)
            self.dout_101 = devices.Dout(modb_dout_101.getСonnectivity(), dout_names_101, "DOUT_101", self.control_log, 10)
            self.dout_101.command("KL1", "ON")

        except:
            return False
    # главная функция
    def main1(self):
        self.control_log.set_start(False)
        # обработать try false и добавить метод get
        config = self.settings.load("settings.cfg")
        count_devices = int(config.get("checked_list"))
        # добавить формирование протокола
        # assert self.prepare()
        # i = 1
        flag = False
        i = 1
        while True:
            while i <= count_devices:
                try:
                    if i >= count_devices:
                        flag = True
                    self.control_log.add("Девайс номер ", str(i), True)
                    # ОБЯЗАТЕЛЬНО В НАЧАЛЕ ЦИКЛА
                    self.main_log.set_finish(False)
                    self.main_log.set_device_count(i - 1)
                    time.sleep(2)
                    assert self.first_start()
                    time.sleep(2)
                    assert self.configurate_check()
                    time.sleep(2)
                    # assert self.for_test()

                    # if i == 1:
                    #     self.main_log.set_start(True)
                    # else:
                    #     self.main_log.set_start(False)


                    # ОБЯЗАТЕЛЬНО В КОНЦЕ ЦИКЛА
                    self.main_log.set_finish(True)
                    # если все успешно то True
                    self.main_log.set_start(True)
                    i = i + 1

                    time.sleep(2)
                except AssertionError:
                    self.main_log.set_start(False)
                    self.main_log.set_finish(True)
                    i = i + 1
                    time.sleep(2)
            if flag:
                self.control_log.add("Тестирование", "Тестирование завершено", False)
                # закончить опрос backend'a
                self.control_log.set_finish(True)
                # time.sleep(2)
                break


                # self.control_log.add("Тестирование", "Тестирование завершено", False)
                # # закончить опрос backend'a
                # self.control_log.set_finish(True)
                # self.control_log.add("Тестирование",
                #                      "В связи с неисправностью стенда или вспомогательных средств дальнейшая проверка невозможна",
                #                      False)
                # self.control_log.set_finish(True)
                # break
#     # внутри обернуть по три попытки
#     # проблема
#     # добавить try except возвращать true false и метод get в котором возвращать объект соединения если соединение true
#     modb_psc24_10 = devices.Modb().getConnection("PSC24_10", self.device_com, 1, self.control_log)
#     assert modb_psc24_10
#     psc24_10 = devices.Psc_10(modb_psc24_10, "PSC24_10", self.device_com)
#     if psc24_10 == False:
#         break
#     i = i + 1
# # если прошел сохранять протокол
# print(IN1)
# print(IN2)
# print(BTR)
# print(count_devices)
# assert False


# главный метод используемый в web'е, перетащить его в класс checking после тестирования
# if __name__ == "__main__":
    # check_error_rate(24.0,24.25)
    # check = Check_psc24_10()
    # check.main1()
    # print(";a;a;")


