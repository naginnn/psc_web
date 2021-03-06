import pickle
from datetime import datetime
import devices
import time
import protocol
from threading import Thread, Lock

import read_write_eeprom

dout_names_101 = {"KL1":81,"KL2":82,"KL3":83,"KL4":84,"KL5":85,"KL6":86,"KL7":87,"KL8":88,"KL9":89,"KL10":90,"KL11":91,"KL12":92,"KL13":93,"KL14":94,"KL15":95,"KL16":96}
dout_names_102 = {"KL17":81,"KL18":82,"KL19":83,"KL20":84,"KL21":85,"KL22":86,"KL23":87,"KL24":88,"KL25":89,"KL26":90,"KL27":91,"KL28":92,"KL29":93,"KL30":94,"KL31":95,"KL32":96}
dout_names_103 = {"KL33":81,"KM1":82,"KM2":83,"KM3":84,"KM4":85,"KM5":86,"KM6":87,"KM7":88,"KM8":89,"KM9":90,"KM10":91,"KM11":92,"KM14":93,"KM15":94,"KM16":95,"KM17":96}
dout_names_104 = {"KM18":81,"KM19":82,"KM12":83,"KM13":84,"KM20":85,"KM21":86,"KM22":87,"KM23":88,"reserved1":89,"reserved2":90,"reserved3":91,"reserved4":92,"KL34":93,"reserved5":94,"reserved6":95,"reserved7":96}
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
                 "KM12":"PSC 5 - входные каналы",
                 "KM13": "Прибавить 10А(коммутаторы)",
                 "KM14":"OUT1  - Коммутаторы",
                 "KM15":"OUT2  - R(реостат)",
                 "KM16":"OUT1  - Коммутаторы",
                 "KM17":"OUT2 - R(реостат)",
                 "KM18": "Коротокое замыкание на R1(реостат)",
                 "KM19": "Коротокое замыкание на R2(коммутаторы)",
                 "SF4": "Цепь IN1",
                 "SF5": "Цепь IN2",
                 "SF6": "Цепь IN3",
                 "SF7": "Цепь IN4",
                 "KL34": "Обрыв связи с датчиком",
                 "Reserved1": "Reserved",
                 "Reserved2": "Reserved",
                 "Reserved3": "Reserved",
                 "KM20": "Прибавить 20А(реостат)",
                 "KM21": "Прибавить 40А(реостат)",
                 "KM22": "Прибавить 40А(реостат)",
                 "KM23": "Прибавить 80А(реостат)",
                 }

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
    stage = ""
    serial_number = ""
    total_error = ""

    def set_total_error(self, message):
        self.total_error = message

    def get_total_error(self):
        return self.total_error

    def set_serial_number(self, serial_number):
        self.serial_number = serial_number

    def get_serial_number(self):
        return self.serial_number

    def set_stage(self, stage):
        self.stage = stage

    def get_stage(self):
        return self.stage

    def add(self, name, event, result):
        self.log = self.log + datetime.now().strftime('%H:%M:%S.%f')[:-4] + " " + name + ":" + " " + event + "\n"
        self.log_data.append(datetime.now().strftime('%H:%M:%S.%f')[:-4] + " " + name + ":" + " " + event + "\n")
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
            # амперметры
            modb_ammeter_out1 = devices.Modb()
            assert modb_ammeter_out1.getConnection("Амперметр OUT1", self.ammeter_com, 5, 19200, self.control_log)
            modb_ammeter_out2 = devices.Modb()
            assert modb_ammeter_out2.getConnection("Амперметр OUT2", self.ammeter_com, 6, 19200, self.control_log)

            config = self.settings.load("settings.cfg")
            # не забыть ввести в работу
            self.power_supply = devices.PowerSupply(config.get("ip_adress"), config.get("port"), "ЛБП",
                                                    self.control_log, 1)
            assert self.power_supply.connection()

            # заменить просто проверкой что пинг доступен добавить ассерт
            # self.router = devices.Router("192.168.1.1", "Роутер")

            self.dout_101 = devices.Dout(modb_dout_101.getСonnectivity(), dout_names_101, "DOUT_101", self.control_log,
                                         10)
            self.dout_102 = devices.Dout(modb_dout_102.getСonnectivity(), dout_names_102, "DOUT_102", self.control_log,
                                         10)
            self.dout_103 = devices.Dout(modb_dout_103.getСonnectivity(), dout_names_103, "DOUT_103", self.control_log,
                                         10)
            self.dout_104 = devices.Dout(modb_dout_104.getСonnectivity(), dout_names_104, "DOUT_104", self.control_log,
                                         10)
            self.din_201 = devices.Din(modb_din_201.getСonnectivity(), din_names_201, "DIN_201", self.control_log, 10)
            self.din_202 = devices.Din(modb_din_202.getСonnectivity(), din_names_202, "DIN_202", self.control_log, 10)
            self.ammeter_out1 = devices.Ammeter(modb_ammeter_out1.getСonnectivity(), "Амперметр OUT1", self.control_log,
                                                30)
            self.ammeter_out2 = devices.Ammeter(modb_ammeter_out2.getСonnectivity(), "Амперметр OUT2", self.control_log,
                                                30)
            self.log.set_finish(True)
        except:
            self.control_log.add(self.name, "Error #1: Ошибка инициализации модулей управления", False)
            return False


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
    u_nom = 24.0
    u_in_min = 0.0
    U_in_min_gyst = 0.0
    U_in_max_gyst = 0.0
    u_in_max = 0.0
    i_nom = 0.0
    u_in1_fact = 0.0
    u_in2_fact = 0.0
    u_in3_fact = 0.0
    u_delta = 0.0
    i_out1_fact = 0.0
    i_out2_fact = 0.0
    i_nom_difference = 0.5
    i_fact_difference = 0.0
    delta_fact_percent = 0
    u_delta_percent = 5
    i_delta_percent = 15
    temp_t1 = -255.0
    out_i_1_temp = 0.0
    out_i_2_temp = 0.0
    out_i_max = 10
    charge_level = 0.0
    discharge_level = 0.0
    charge_i_stable = 0.0
    charge_u_stable = 0.0
    # списки для будущего протокола
    check_number = {'Порядковый номер': [' ']}
    serial_number = {'Серийный номер': [' ']}
    soft_version = {'Версия ПО': [' '], 'Фактическая': [' ']}
    voltage = {'Канал, U': ['IN1', 'IN2', 'IN3'], 'Unom': ['', '', ''], 'Ufact': ['', '', ''], 'Uerror_rate_nom': ['', '', ''], 'Uerror_rate_fact': ['', '', ''], 'result': ['', '', '']}
    current = {'Канал, I': ['OUT1', 'OUT2'], 'Inom': ['', ''], 'Ifact': ['', ''], 'Ierror_rate_nom': ['', ''], 'Ierror_rate_nom': ['', ''], 'Ierror_rate_fact': ['', ''], 'result': ['', '']}
    current_difference = {'OUT1': [' '], 'OUT2': [' '], 'Idifference_nom': [' '], 'Idifference_fact': [' '], 'result': [' ']}
    voltage_threesolds = {'Пороги, U': ['min, U', 'nom, U', 'max, U', ''], 'U_IN1': ['', '', '', ''], 'ResIN1': ['', '', '', ''], 'U_IN2': ['', '', '', ''], 'ResIN2': ['', '', '', ''],
                          'U_IN3': ['', '', '', ''], 'ResIN3': ['', '', '', ''], 'ChargeBTR': ['', '', '', '']}
    switching_channels = {'Переключение каналов': [' ']}
    ten = {'Работа ТЭН': [' '], 'Работа датчика': [' ']}
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
    router = ()
    # KM2 переделать под 48 В
    power_input = {"pw24_5" : ["KL15", "KL16", "KM1"],
                    "wm24_10" : ["KL7", "KL8", "KM1"],
                    "wm24_40" : ["KL9","KL10","KM1"],
                    "mw24_67" : ["KL1","KL2","KM1"],
                    "wm48_20" : ["KL12","KL13","KM2"],
                    "wm48_67" : ["KL4","KL5","KM2"]}
    IN1 = ""
    IN2 = ""
    BTR = ""
    power_supply_voltage = 0.0
    device = [" ","KM7", "KM8", "KM9", "KM10", "KM11"]
    switches_load = ["KL18", "KL19", "KL20", "KL21", "KL22", "KL23", "KL24", "KL25", "KL27", "KL28", "KL29"]
    control_com = ""
    ammeter_com = ""
    device_com = ""
    config = {}
    eeprom = ()
    power_management = ()

    # добавляем два лога и ком-порт модулям управления и psc
    def __init__(self, name, control_log, main_log, settings):
        self.name = name
        self.control_log = control_log
        self.main_log = main_log
        self.settings = settings

    # время ожидания (перерыва)
    def wait_time(self, timeout):
        time_sec = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        self.control_log.add(self.name, "Ожидание", True)
        for t in range(timeout):
            self.control_log.log_data[len(self.control_log.log_data) - 1] = \
                time_sec + " " + self.name + \
                ": Ожидание " + str(t + 1) + " сек"
            time.sleep(1 - time.time() % 1)

    # расчет процента
    def percentage(self, percent, whole):
        return (percent * whole) / 100.0
    # расчет погрешности, передаем поданное напряжение с ЛБП и фактическое с устройства, получаем результат true/false
    # Для напряжения percent = 5%, для тока percent = 15%
    def check_error_rate(self, nom, fact, nom_percent):
        self.delta_fact_percent = abs(round((fact - nom) * 100 / nom))
        if self.delta_fact_percent == 0:
            self.delta_fact_percent = 1
        if (self.delta_fact_percent <= nom_percent):
            return True
        return False

    # Инициализация Stage 1
    def prepare(self):
        # Инициализируем модули управления
        try:
            self.control_log.add(self.name, "Инициализация модулей управления", True)
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
            # амперметры
            modb_ammeter_out1 = devices.Modb()
            assert modb_ammeter_out1 .getConnection("Амперметр OUT1", self.ammeter_com, 5, 19200, self.control_log)
            modb_ammeter_out2 = devices.Modb()
            assert modb_ammeter_out2 .getConnection("Амперметр OUT2", self.ammeter_com, 6, 19200, self.control_log)

            config = self.settings.load("settings.cfg")
            # не забыть ввести в работу
            self.power_supply = devices.PowerSupply(config.get("ip_adress"), config.get("port"), "ЛБП",self.control_log,1)
            assert self.power_supply.connection()

            # заменить просто проверкой что пинг доступен добавить ассерт
            # self.router = devices.Router("192.168.1.1", "Роутер")

            self.dout_101 = devices.Dout(modb_dout_101.getСonnectivity(), dout_names_101, "DOUT_101", self.control_log, 10)
            self.dout_102 = devices.Dout(modb_dout_102.getСonnectivity(), dout_names_102, "DOUT_102", self.control_log, 10)
            self.dout_103 = devices.Dout(modb_dout_103.getСonnectivity(), dout_names_103, "DOUT_103", self.control_log, 10)
            self.dout_104 = devices.Dout(modb_dout_104.getСonnectivity(), dout_names_104, "DOUT_104", self.control_log, 10)
            self.din_201 = devices.Din(modb_din_201.getСonnectivity(), din_names_201, "DIN_201", self.control_log, 10)
            self.din_202 = devices.Din(modb_din_202.getСonnectivity(), din_names_202, "DIN_202", self.control_log, 10)
            self.ammeter_out1 = devices.Ammeter(modb_ammeter_out1.getСonnectivity(), "Амперметр OUT1", self.control_log, 30)
            self.ammeter_out2 = devices.Ammeter(modb_ammeter_out2.getСonnectivity(), "Амперметр OUT2", self.control_log, 30)

            # правильная инициализация modbus
            modb_psc24_10 = devices.Modb()
            assert modb_psc24_10.getConnection("PSC24_10", self.device_com, 1, 115200, self.control_log)
            self.psc24_10 = devices.Psc_10(modb_psc24_10.getСonnectivity(), "PSC24_10", self.control_log, 120)
            # объект EEPROM
            self.eeprom = read_write_eeprom.ReadWriteEEprom("EEPROM", self.control_log, self.device_com, 115200, 30)

            # читаем конфигурацию assert/ получать setting getter'ом
            self.config = self.settings.load("settings.cfg")

            if self.config.get("device_name") == "psc24_10":
                self.power_supply_voltage = 24.0
            if self.config.get("device_name") == "psc48_10":
                self.power_supply_voltage = 48.0

            self.IN1 = self.power_input[config.get("power_supply_type")][0]
            self.IN2 = self.power_input[config.get("power_supply_type")][1]
            self.BTR = self.power_input[config.get("power_supply_type")][2]

            assert self.din_202.check_voltage("SF4", "ON")
            assert self.din_202.check_voltage("SF5", "ON")
            assert self.din_202.check_voltage("SF6", "ON")
            assert self.din_202.check_voltage("SF7", "ON")
            return True
        except:
            self.control_log.add(self.name, "Ошибка инициализации модулей управления", False)
            return False

    # первое включение проверка состояния Stage 2
    def first_start(self):
        self.main_log.set_stage("serial_number")
        self.control_log.add(self.name, "Подготовка к первому запуску", True)
        # подаём 3 канала с ЛБП
        try:
            # Подключаем входа
            assert self.dout_102.command("KL30", "ON")
            assert self.din_201.check_voltage("KL30", "ON")
            assert self.dout_102.command("KL31", "ON")
            assert self.din_201.check_voltage("KL31", "ON")
            assert self.dout_103.command("KL33", "ON")
            assert self.din_202.check_voltage("KL33", "ON")

            # Конфигурируем ЛБП
            assert self.power_supply.remote("ON")
            assert self.power_supply.check_remote("REMOTE")
            assert self.power_supply.output("ON")
            assert self.power_supply.check_output("ON")

            assert self.power_supply.set_voltage(self.power_supply_voltage)
            assert self.power_supply.check_voltage(self.power_supply_voltage)

            # self.wait_time(30)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1}
            # ждем включения устройства и передаем предполагаемое поведение заменить на if для
            # подробного описания ошибок
            assert self.psc24_10.check_behaviour(self.behaviour)

            # считываем серийный номер
            assert self.eeprom.read_serial_number()
            serial_number = str(self.eeprom.get_serial_number())
            # self.serial_number['Серийный номер'][0] = serial_number
            if serial_number != "4710000000":
                self.serial_number['Серийный номер'][0] = serial_number
                self.control_log.add(self.name, "Серийный номер: " + serial_number, True)
                self.main_log.set_serial_number(serial_number)
            else:
                self.serial_number['Серийный номер'][0] = "4710000000"
                self.control_log.add(self.name, "Серийный номер не записан", False)
                self.main_log.set_serial_number("4710000000")

            self.main_log.set_stage("serial_number_pass")
            self.control_log.add(self.name, "Подготовка к первому запуска завершена", True)
            return True
        except:
            self.main_log.set_stage("serial_number_fail")
            self.control_log.add(self.name, "Подготовка к первому запуску не прошла", False)
            return False

    #  считывание и проверка конфигурации Stage 3
    def configurate_check(self):
        self.main_log.set_stage("configuration")
        self.control_log.add(self.name, "Проверка и запись конфигурации", True)
        try:
            # считываем версию ПО
            assert self.eeprom.read_soft_version()
            soft_version = self.config.get("soft_version")
            self.soft_version['Версия ПО'] = soft_version
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

            # считываем настройки электропитания
            assert self.eeprom.read_power_management()
            self.power_management = self.eeprom.get_power_management()

            self.out_i_1_temp = self.power_management.get("out_i_1")
            self.out_i_2_temp = self.power_management.get("out_i_2")
            # записываем уставки по току
            assert self.eeprom.write_max_current_value(5, 5)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1}
            # проверяем состояние состояние
            assert self.psc24_10.check_behaviour(self.behaviour)
            self.main_log.set_stage("configuration_pass")
            self.control_log.add(self.name, "Проверка и запись конфигурации завершено", True)
            return True
        except:
            self.main_log.set_stage("configuration_fail")
            self.control_log.add(self.name, "Ошибка при проверке и записи конфигурации", False)
            return False

    # проверка телеизмерения Stage 4
    def measurements_check(self):
        self.main_log.set_stage("measurements")
        self.control_log.add(self.name, "Проверка измерений", True)
        try:
            ##############  IN1  ##############
            # получаем номинальное напряжение канала на устройстве
            self.u_nom = round(float(self.power_management.get("pw1_u_nom")),2)
            # устанавливаем номинальное напряжение на ЛБП
            assert self.power_supply.set_voltage(self.u_nom)
            assert self.power_supply.check_voltage(self.u_nom)
            # получаем напряжение с канала
            assert self.psc24_10.check_ti("U_IN1")
            self.u_in1_fact = self.psc24_10.get_ti()
            # записываем значение номинальное и фактическое в протокол
            self.voltage['Unom'][0] = str(self.u_nom)
            self.voltage['Ufact'][0] = str(self.u_in1_fact)
            self.voltage['Uerror_rate_nom'][0] = str(self.u_delta_percent) + '%'
            # выясняем какая погрешность, в зависимости от результата заполняем протокол
            if self.check_error_rate(self.u_nom, self.u_in1_fact, self.u_delta_percent):
                self.voltage['Uerror_rate_fact'][0] = str(self.delta_fact_percent) + '%'
                self.voltage['result'][0] = "ok"
                self.control_log.add(self.name,
                                     "IN1: Номинальное напряжение " + str(self.u_nom) + " Фактическое напряжение " + str(self.u_in1_fact) +
                                     " <= " + str(self.u_delta_percent), True)
            else:
                self.voltage['Uerror_rate_fact'][0] = str(self.delta_fact_percent) + '%'
                self.voltage['result'][0] = "bad"
                self.control_log.add(self.name,
                                     "IN1: Номинальное напряжение " + str(self.u_nom) + " Фактическое напряжение " + str(self.u_in1_fact) +
                                     " > " + str(self.u_delta_percent), False)

            ##############  IN2  ##############
            # получаем номинальное напряжение канала на устройстве
            self.u_nom = round(float(self.power_management.get("pw2_u_nom")),2)
            # устанавливаем номинальное напряжение на ЛБП
            assert self.power_supply.set_voltage(self.u_nom)
            assert self.power_supply.check_voltage(self.u_nom)
            # получаем напряжение с канала
            assert self.psc24_10.check_ti("U_IN2")
            self.u_in2_fact = self.psc24_10.get_ti()
            # записываем значение номинальное и фактическое в протокол
            self.voltage['Unom'][1] = str(self.u_nom)
            self.voltage['Ufact'][1] = str(self.u_in2_fact)
            self.voltage['Uerror_rate_nom'][1] = str(self.u_delta_percent) + '%'
            # выясняем какая погрешность, в зависимости от результата заполняем протокол
            if self.check_error_rate(self.u_nom, self.u_in2_fact, self.u_delta_percent):
                self.voltage['Uerror_rate_fact'][1] = str(self.delta_fact_percent) + '%'
                self.voltage['result'][1] = "ok"
                self.control_log.add(self.name,
                                     "IN2: Номинальное напряжение " + str(
                                         self.u_nom) + " Фактическое напряжение " + str(self.u_in1_fact) +
                                     " <= " + str(self.u_delta_percent), True)
            else:
                self.voltage['Uerror_rate_fact'][1] = str(self.delta_fact_percent) + '%'
                self.voltage['result'][1] = "bad"
                self.control_log.add(self.name,
                                     "IN2: Номинальное напряжение " + str(
                                         self.u_nom) + " Фактическое напряжение " + str(self.u_in1_fact) +
                                     " > " + str(self.u_delta_percent), False)

            ##############  IN3(АКБ)  ##############
            # получаем номинальное напряжение канала на устройстве
            self.u_nom = round(float(self.power_management.get("btr_u_nom")),2)
            # устанавливаем номинальное напряжение на ЛБП
            assert self.power_supply.set_voltage(self.u_nom)
            assert self.power_supply.check_voltage(self.u_nom)
            # получаем напряжение с канала
            assert self.psc24_10.check_ti("U_IN3")
            self.u_in3_fact = self.psc24_10.get_ti()
            # записываем значение номинальное и фактическое в протокол
            self.voltage['Unom'][2] = str(self.u_nom)
            self.voltage['Ufact'][2] = str(self.u_in3_fact)
            self.voltage['Uerror_rate_nom'][2] = str(self.u_delta_percent) + '%'
            # выясняем какая погрешность, в зависимости от результата заполняем протокол
            if self.check_error_rate(self.u_nom, self.u_in3_fact, self.u_delta_percent):
                self.voltage['Uerror_rate_fact'][2] = str(self.delta_fact_percent) + '%'
                self.voltage['result'][2] = "ok"
                self.control_log.add(self.name,
                                     "IN3 (АКБ): Номинальное напряжение " + str(
                                         self.u_nom) + " Фактическое напряжение " + str(self.u_in1_fact) +
                                     " <= " + str(self.u_delta_percent), True)
            else:
                self.voltage['Uerror_rate_fact'][2] = str(self.delta_fact_percent) + '%'
                self.voltage['result'][2] = "bad"
                self.control_log.add(self.name,
                                     "IN3 (АКБ): Номинальное напряжение " + str(
                                         self.u_nom) + " Фактическое напряжение " + str(self.u_in1_fact) +
                                     " > " + str(self.u_delta_percent), False)

            # подключаем OUT1
            assert self.dout_103.command("KM14", "ON")
            assert self.din_202.check_voltage("KM14", "ON")

            # подать токи на выхода
            # подключаем коммутатор #1
            assert self.dout_102.command("KL18", "ON")
            assert self.din_201.check_voltage("KL18", "ON")
            # проверяем состояние
            assert self.psc24_10.check_behaviour(self.behaviour)
            # подключаем коммутатор #2
            assert self.dout_102.command("KL19", "ON")
            assert self.din_201.check_voltage("KL19", "ON")

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1}
            # проверяем состояние состояние
            assert self.psc24_10.check_behaviour(self.behaviour)

            # таймаут перед опросом датчика тока №1
            self.wait_time(5)

            # получаем и рассчитываем измерения OUT1
            # получаем ТИ с OUT1
            assert self.psc24_10.check_ti("I_OUT1")
            self.i_out1_fact = self.psc24_10.get_ti()
            # получаем ТИ с Амперметра 1
            assert self.ammeter_out1.check_ti()
            self.i_nom = self.ammeter_out1.get_ti()
            # записываем значение номинальное и фактическое в протокол
            self.current['Inom'][0] = str(self.i_nom)
            self.current['Ifact'][0] = str(self.i_out1_fact)
            self.current['Ierror_rate_nom'][0] = str(self.i_delta_percent) + '%'
            # выясняем какая погрешность, в зависимости от результата заполняем протокол
            if self.check_error_rate(self.i_nom, self.i_out1_fact, self.i_delta_percent):
                self.current['Ierror_rate_fact'][0] = str(self.delta_fact_percent) + '%'
                self.current['result'][0] = "ok"
                self.control_log.add(self.name, "OUT1: Номинальный ток " + str(self.i_nom) +
                                     " Фактический ток " + str(self.i_out1_fact) +
                                     " <= " + str(self.i_delta_percent), True)
            else: # переименовать u_delta_fact-PERCENT В delta_fact_percent
                self.current['Ierror_rate_fact'][0] = str(self.delta_fact_percent) + '%'
                self.current['result'][0] = "bad"
                self.control_log.add(self.name, "OUT1: Номинальный ток " + str(self.i_nom) +
                                     " Фактический ток " + str(self.i_out1_fact) +
                                     " > " + str(self.i_delta_percent), False)

            # подать токи на выхода
            # отключаем коммутатор #1
            assert self.dout_102.command("KL18", "OFF")
            assert self.din_201.check_voltage("KL18", "OFF")
            # проверяем состояние
            assert self.psc24_10.check_behaviour(self.behaviour)
            # отключаем коммутатор #2
            assert self.dout_102.command("KL19", "OFF")
            assert self.din_201.check_voltage("KL19", "OFF")

            # отключаем OUT1
            assert self.dout_103.command("KM14", "OFF")
            assert self.din_202.check_voltage("KM14", "OFF")

            self.wait_time(10)

            # включаем OUT2
            assert self.dout_103.command("KM15", "ON")
            assert self.din_202.check_voltage("KM15", "ON")

            # подать токи на выхода
            # подключаем коммутатор #1
            assert self.dout_102.command("KL18", "ON")
            assert self.din_201.check_voltage("KL18", "ON")
            # проверяем состояние
            assert self.psc24_10.check_behaviour(self.behaviour)
            # подключаем коммутатор #2
            assert self.dout_102.command("KL19", "ON")
            assert self.din_201.check_voltage("KL19", "ON")

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1}
            # проверяем состояние состояние
            assert self.psc24_10.check_behaviour(self.behaviour)

            # таймаут перед опросом датчика тока №2
            self.wait_time(5)

            # получаем и рассчитываем измерения OUT2
            # получаем ТИ с OUT2
            assert self.psc24_10.check_ti("I_OUT2")
            self.i_out2_fact = self.psc24_10.get_ti()
            # получаем ТИ с Амперметра 2
            assert self.ammeter_out2.check_ti()
            self.i_nom = self.ammeter_out2.get_ti()
            # записываем значение номинальное и фактическое в протокол
            self.current['Inom'][1] = str(self.i_nom)
            self.current['Ifact'][1] = str(self.i_out2_fact)
            self.current['Ierror_rate_nom'][1] = str(self.i_delta_percent) + '%'
            # выясняем какая погрешность, в зависимости от результата заполняем протокол
            if self.check_error_rate(self.i_nom, self.i_out2_fact, self.i_delta_percent):
                self.current['Ierror_rate_fact'][1] = str(self.delta_fact_percent) + '%'
                self.current['result'][1] = "ok"
                self.control_log.add(self.name, "OUT2: Номинальный ток " + str(self.i_nom) +
                                     " Фактический ток " + str(self.i_out1_fact) +
                                     " <= " + str(self.i_delta_percent), True)
            else:
                self.current['Ierror_rate_fact'][1] = str(self.delta_fact_percent) + '%'
                self.current['result'][1] = "bad"
                self.control_log.add(self.name, "OUT2: Номинальный ток " + str(self.i_nom) +
                                     " Фактический ток " + str(self.i_out1_fact) +
                                     " > " + str(self.i_delta_percent), False)

            # отключаем коммутатор #1
            assert self.dout_102.command("KL18", "OFF")
            assert self.din_201.check_voltage("KL18", "OFF")

            # отключаем коммутатор #2
            assert self.dout_102.command("KL19", "OFF")
            assert self.din_201.check_voltage("KL19", "OFF")

            # подключаем OUT1
            assert self.dout_103.command("KM14", "ON")
            assert self.din_202.check_voltage("KM14", "ON")

            # подключаем коммутатор #1
            assert self.dout_102.command("KL18", "ON")
            assert self.din_201.check_voltage("KL18", "ON")

            # подключаем коммутатор #2
            assert self.dout_102.command("KL19", "ON")
            assert self.din_201.check_voltage("KL19", "ON")

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1}
            # проверяем состояние состояние
            assert self.psc24_10.check_behaviour(self.behaviour)

            # таймаут перед опросом каналов (возможно увеличить)
            self.wait_time(5)

            # получаем измерения OUT1
            assert self.psc24_10.check_ti("I_OUT1")
            self.i_out1_fact = self.psc24_10.get_ti()
            self.current_difference['OUT1'][0] = str(self.i_out1_fact)

            # получаем измерения OUT2
            assert self.psc24_10.check_ti("I_OUT2")
            self.i_out2_fact = self.psc24_10.get_ti()
            self.current_difference['OUT2'][0] = str(self.i_out2_fact)

            # проверяем разницу между OUT1 и OUT2 не более 0.5
            self.i_fact_difference = abs(round(self.i_out1_fact - self.i_out2_fact, 2))
            self.current_difference['Idifference_nom'][0] = str(self.i_nom_difference)
            self.current_difference['Idifference_fact'][0] = str(self.i_fact_difference)
            if (self.i_fact_difference <= self.i_nom_difference):
                self.current_difference['result'][0] = "ok"
                self.control_log.add(self.name, "Разница между каналами по току " + str(self.i_fact_difference) + " mA", True)
            else:
                self.current_difference['result'][0] = "bad"
                self.control_log.add(self.name, "Разница между каналами по току " + str(self.i_fact_difference) + " mA", False)

            # отключаем коммутатор #1
            assert self.dout_102.command("KL18", "OFF")
            assert self.din_201.check_voltage("KL18", "OFF")

            # отключаем коммутатор #2
            assert self.dout_102.command("KL19", "OFF")
            assert self.din_201.check_voltage("KL19", "OFF")

            # отключаем OUT1
            assert self.dout_103.command("KM14", "OFF")
            assert self.din_202.check_voltage("KM14", "OFF")

            # отключаем OUT2
            assert self.dout_103.command("KM15", "OFF")
            assert self.din_202.check_voltage("KM15", "OFF")

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1}
            # проверяем состояние состояние
            assert self.psc24_10.check_behaviour(self.behaviour)

            self.main_log.set_stage("measurements_pass")
            self.control_log.add(self.name, "Stage #4: Проверка измерений завершена", True)
            return True
        except:
            self.main_log.set_stage("measurements_fail")
            self.control_log.add(self.name, "Ошибка при проверке измерений", False)
            return False

    # Проверка порогов по напряжению работаем здесь stage 5
    def check_voltage_thresholds(self):
        self.main_log.set_stage("functional")
        self.control_log.add(self.name, "Проверка порогов по напряжению", True)
        try:
            assert self.power_supply.output("OFF")
            assert self.power_supply.check_output("OFF")

            self.wait_time(5)

            # делаем перекоммутацию IN2 с ЛБП на БП
            assert self.dout_102.command("KL31", "OFF")
            assert self.din_201.check_voltage("KL31", "OFF")

            # Отключаем ЛБП IN3
            assert self.dout_103.command("KL33", "OFF")
            assert self.din_202.check_voltage("KL33", "OFF")

            # подключаем IN2
            assert self.dout_101.command(self.IN2, "ON")
            assert self.din_201.check_voltage(self.IN2, "ON")

            # подключаем АКБ
            assert self.dout_103.command(self.BTR, "ON")
            assert self.din_202.check_voltage(self.BTR, "ON")

            assert self.power_supply.output("ON")
            assert self.power_supply.check_output("ON")

            # вход IN1=ЛБП IN2=WM IN3=BTR

            # self.wait_time(10)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1}
            # проверяем состояние состояние
            assert self.psc24_10.check_behaviour(self.behaviour)

            # получаем пороги
            self.U_in_min_gyst = float(self.power_management.get("pw1_u_min_hyst"))
            self.U_in_max_gyst = float(self.power_management.get("pw1_u_max_hyst"))
            self.u_in_min = float(self.power_management.get("pw1_u_min"))
            self.u_nom = float(self.power_management.get("pw1_u_nom"))
            self.u_in_max = float(self.power_management.get("pw1_u_max"))

            # сохраняем протокол
            self.voltage_threesolds['U_IN1'][0] = str(self.u_in_min)
            self.voltage_threesolds['U_IN1'][1] = str(self.u_nom)
            self.voltage_threesolds['U_IN1'][2] = str(self.u_in_max)
            # расчитываем погрешность для IN1 u_min
            self.u_delta = self.percentage(self.u_delta_percent, self.u_in_min)

            # установить минимальный порог на ЛБП с учетом погрешности
            assert self.power_supply.set_voltage(round(self.u_in_min - self.u_delta, 2))
            assert self.power_supply.check_voltage(round(self.u_in_min - self.u_delta, 2))

            # self.wait_time(10)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 0, "pwr2": 1, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 1, "error_pwr2": 0,
                 "error_out1": 0, "error_out2": 0}

            # определяем по поведению сработал ли порог
            if self.psc24_10.check_behaviour(self.behaviour):
                self.voltage_threesolds['ResIN1'][0] = "ok"
            else:
                self.voltage_threesolds['ResIN1'][0] = "bad"
            self.control_log.add(self.name,
                                 "Результат работы срабатывания по u_min: " + self.voltage_threesolds['ResIN1'][0],
                                 True)

            # устанавливаем номинальное напряжение
            assert self.power_supply.set_voltage(round(self.u_nom, 2))
            assert self.power_supply.check_voltage(round(self.u_nom, 2))

            # self.wait_time(10)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0, "error_pwr2": 0,
                              "error_out1": 0, "error_out2": 0}

            # проверяем состояние, убеждаемся в переключении на IN1
            # определяем по поведению сработал ли порог по u_nom
            if self.psc24_10.check_behaviour(self.behaviour):
                self.voltage_threesolds['ResIN1'][1] = "ok"
            else:
                self.voltage_threesolds['ResIN1'][1] = "bad"
            self.control_log.add(self.name,
                                 "Результат работы срабатывания по u_nom: " + self.voltage_threesolds['ResIN1'][1],
                                 True)

            # расчитываем погрешность для IN1 u_max
            self.u_delta = self.percentage(self.u_delta_percent, self.u_in_max)
            # установить максимальный порог на ЛБП с учетом погрешности
            assert self.power_supply.set_voltage(round(self.u_in_max + self.u_delta, 2))
            assert self.power_supply.check_voltage(round(self.u_in_max + self.u_delta, 2))

            # self.wait_time(10)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 0, "pwr2": 1, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 1, "error_pwr2": 0,
                              "error_out1": 0, "error_out2": 0}

            # определяем по поведению сработал ли порог по u_max
            if self.psc24_10.check_behaviour(self.behaviour):
                self.voltage_threesolds['ResIN1'][2] = "ok"
            else:
                self.voltage_threesolds['ResIN1'][2] = "bad"
            self.control_log.add(self.name,
                                 "Результат работы срабатывания по u_max: " + self.voltage_threesolds['ResIN1'][2],
                                 True)

            # устанавливаем номинальное напряжение
            assert self.power_supply.set_voltage(round(self.u_nom, 2))
            assert self.power_supply.check_voltage(round(self.u_nom, 2))

            # self.wait_time(10)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0, "error_pwr2": 0,
                              "error_out1": 0, "error_out2": 0}

            # проверяем переход на IN1
            assert self.psc24_10.check_behaviour(self.behaviour)

            assert self.power_supply.set_voltage(round(self.u_nom, 2))
            assert self.power_supply.check_voltage(round(self.u_nom, 2))

            # Конфигурируем ЛБП
            assert self.power_supply.output("OFF")
            assert self.power_supply.check_output("OFF")

            self.wait_time(10)

            # отключаем IN1
            assert self.dout_102.command("KL30", "OFF")
            assert self.din_201.check_voltage("KL30", "OFF")

            # включаем IN2 ЛБП
            # отключаем IN2 БП
            assert self.dout_101.command(self.IN2, "OFF")
            assert self.din_201.check_voltage(self.IN2, "OFF")

            assert self.dout_102.command("KL31", "ON")
            assert self.din_201.check_voltage("KL31", "ON")

            self.wait_time(10)

            # Конфигурируем ЛБП
            assert self.power_supply.output("ON")
            assert self.power_supply.check_output("ON")

            # IN1=null IN2=ЛБП IN3=АКБ
            # self.wait_time(10)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 0, "pwr2": 1, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 1, "error_pwr2": 0,
                              "error_out1": 0, "error_out2": 0}

            # проверяем переход на IN2
            assert self.psc24_10.check_behaviour(self.behaviour)

            # получаем пороги
            self.u_in_min = float(self.power_management.get("pw2_u_min"))
            self.u_nom = float(self.power_management.get("pw2_u_nom"))
            self.u_in_max = float(self.power_management.get("pw2_u_max"))

            # сохраняем протокол
            self.voltage_threesolds['U_IN2'][0] = str(self.u_in_min)
            self.voltage_threesolds['U_IN2'][1] = str(self.u_nom)
            self.voltage_threesolds['U_IN2'][2] = str(self.u_in_max)
            # расчитываем погрешность для IN2 u_min
            self.u_delta = self.percentage(self.u_delta_percent, self.u_in_min)
            # установить минимальный порог на ЛБП с учетом погрешности
            assert self.power_supply.set_voltage(round(self.u_in_min - self.u_delta, 2))
            assert self.power_supply.check_voltage(round(self.u_in_min - self.u_delta, 2))

            # self.wait_time(10)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 0, "pwr2": 0, "btr": 1, "key1": 1, "key2": 1, "error_pwr1": 1, "error_pwr2": 1,
                              "error_out1": 0, "error_out2": 0}

            # определяем по поведению сработал ли порог
            if self.psc24_10.check_behaviour(self.behaviour):
                self.voltage_threesolds['ResIN2'][0] = "ok"
            else:
                self.voltage_threesolds['ResIN2'][0] = "bad"
            self.control_log.add(self.name,
                                 "Результат работы срабатывания по u_min: " + self.voltage_threesolds['ResIN2'][0],
                                 True)

            # устанавливаем номинальное напряжение
            assert self.power_supply.set_voltage(round(self.u_nom, 2))
            assert self.power_supply.check_voltage(round(self.u_nom, 2))

            # self.wait_time(10)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 0, "pwr2": 1, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 1, "error_pwr2": 0,
                              "error_out1": 0, "error_out2": 0}

            # проверяем переход на IN2
            # определяем по поведению сработал ли порог u_nom
            if self.psc24_10.check_behaviour(self.behaviour):
                self.voltage_threesolds['ResIN2'][1] = "ok"
            else:
                self.voltage_threesolds['ResIN2'][1] = "bad"
            self.control_log.add(self.name,
                                 "Результат работы срабатывания по u_nom: " + self.voltage_threesolds['ResIN2'][1],
                                 True)

            # расчитываем погрешность для IN2 u_max
            self.u_delta = self.percentage(self.u_delta_percent, self.u_in_max)
            # установить максимальный порог на ЛБП с учетом погрешности
            assert self.power_supply.set_voltage(round(self.u_in_max + self.u_delta, 2))
            assert self.power_supply.check_voltage(round(self.u_in_max + self.u_delta, 2))

            # предполагаемое поведение
            self.behaviour = {"pwr1": 0, "pwr2": 0, "btr": 1, "key1": 1, "key2": 1, "error_pwr1": 1, "error_pwr2": 1,
                              "error_out1": 0, "error_out2": 0}

            if self.psc24_10.check_behaviour(self.behaviour):
                self.voltage_threesolds['ResIN2'][2] = "ok"
            else:
                self.voltage_threesolds['ResIN2'][2] = "bad"
            self.control_log.add(self.name,
                                 "Результат работы срабатывания по u_max: " + self.voltage_threesolds['ResIN2'][2],
                                 True)

            # устанавливаем номинальное напряжение
            assert self.power_supply.set_voltage(round(self.u_nom, 2))
            assert self.power_supply.check_voltage(round(self.u_nom, 2))

            # self.wait_time(10)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 0, "pwr2": 1, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 1, "error_pwr2": 0,
                              "error_out1": 0, "error_out2": 0}

            assert self.psc24_10.check_behaviour(self.behaviour)

            # Проверка АКБ и порогов по напряжению
            # IN1=null IN2=WM IN3=ЛБП
            # изменено для проверки АКБ (просто отключение)

            assert self.power_supply.output("OFF")
            assert self.power_supply.check_output("OFF")

            self.wait_time(10)

            # отключаем ЛБП IN2
            assert self.dout_102.command("KL31", "OFF")
            assert self.din_201.check_voltage("KL31", "OFF")
            # подключаем IN1
            assert self.dout_101.command(self.IN1, "ON")
            assert self.din_201.check_voltage(self.IN1, "ON")

            # подключаем IN2
            assert self.dout_101.command(self.IN2, "ON")
            assert self.din_201.check_voltage(self.IN2, "ON")

            # отключаем АКБ
            assert self.dout_103.command(self.BTR, "OFF")
            assert self.din_202.check_voltage(self.BTR, "OFF")

            self.wait_time(5)

            # Включить ЛБП на IN3
            assert self.dout_103.command("KL33", "ON")
            assert self.din_202.check_voltage("KL33", "ON")

            assert self.power_supply.output("ON")
            assert self.power_supply.check_output("ON")

            # IN1=WM IN2=WM IN3=ЛБП

            self.wait_time(70)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0, "error_pwr2": 0,
                              "error_out1": 0, "error_out2": 0}

            # проверяем переключения
            assert self.psc24_10.check_behaviour(self.behaviour)

            # получаем пороги
            self.u_in_min = float(self.power_management.get("btr_u_min"))
            self.u_nom = float(self.power_management.get("btr_u_nom"))
            self.u_in_max = float(self.power_management.get("btr_u_max"))

            self.charge_level = float(self.power_management.get("charge_u_max"))
            self.discharge_level = float(self.power_management.get("charge_u_min"))
            self.charge_u_stable = float(self.power_management.get("charge_u_stable"))
            self.charge_i_stable = float(self.power_management.get("charge_i_stable"))

            # сохраняем протокол
            self.voltage_threesolds['U_IN3'][0] = str(self.u_in_min)
            self.voltage_threesolds['U_IN3'][1] = str(self.u_nom)
            self.voltage_threesolds['U_IN3'][2] = str(self.u_in_max)
            # ток заряда
            # наряжение заряда

            # расчитываем погрешность и проверяем зарядку АКБ
            self.u_delta = self.percentage(self.u_delta_percent, self.discharge_level)
            # установить минимальный порог на ЛБП с учетом погрешности
            assert self.power_supply.set_voltage(self.discharge_level - self.u_delta)
            assert self.power_supply.check_voltage(self.discharge_level - self.u_delta)

            # ожидаем заряда
            self.wait_time(70)
            # добавить напряжение и ток заряда проверить

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0, "error_pwr2": 0,
                              "error_btr": 0, "error_out1": 0, "error_out2": 0, "charge_btr": 1}
            assert self.psc24_10.check_behaviour(self.behaviour)
            self.control_log.add(self.name, "Имитация процесса зарядки АКБ - исправно", True)

            # расчитываем погрешность и проверяем полный заряд АКБ
            self.u_delta = self.percentage(self.u_delta_percent, self.charge_level)
            # установить минимальный порог на ЛБП с учетом погрешности
            assert self.power_supply.set_voltage(self.charge_level + self.u_delta)
            assert self.power_supply.check_voltage(self.charge_level + self.u_delta)

            # ожидаем заряда
            self.wait_time(70)
            # добавить напряжение и ток заряда проверить

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0, "error_pwr2": 0,
                              "error_btr": 0, "error_out1": 0, "error_out2": 0, "charge_btr": 0}

            if self.psc24_10.check_behaviour(self.behaviour):
                self.control_log.add(self.name, "Имитация полного заряда АКБ - исправно", True)
                self.voltage_threesolds['ChargeBTR'][0] = "ok"
            else:
                self.control_log.add(self.name, "Имитация полного заряда АКБ - неисправно", False)
                self.voltage_threesolds['ChargeBTR'][0] = "bad"


            # расчитываем погрешность для IN3 u_max
            self.u_delta = self.percentage(self.u_delta_percent, self.u_in_max)
            # установить максимальный порог на ЛБП с учетом погрешности
            assert self.power_supply.set_voltage(self.u_in_max + self.u_delta)
            assert self.power_supply.check_voltage(self.u_in_max + self.u_delta)

            # ожидаем пропажу АКБ
            self.wait_time(70)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0, "error_pwr2": 0,
                              "error_btr": 1, "error_out1": 0, "error_out2": 0, "charge_btr": 0}

            if self.psc24_10.check_behaviour(self.behaviour):
                self.voltage_threesolds['ResIN3'][2] = "ok"
            else:
                self.voltage_threesolds['ResIN3'][2] = "bad"
            self.control_log.add(self.name,
                                 "Результат работы срабатывания по u_max: " + self.voltage_threesolds['ResIN3'][2],
                                 True)

            # устанавливаем номинальное напряжение
            assert self.power_supply.set_voltage(self.u_nom)
            assert self.power_supply.check_voltage(self.u_nom)

            # ожидаем заряда
            self.wait_time(70)
            # добавить напряжение и ток заряда проверить

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0, "error_pwr2": 0,
                              "error_btr": 0, "error_out1": 0, "error_out2": 0, "charge_btr": 1}

            # определяем по поведению сработал ли порог u_nom
            if self.psc24_10.check_behaviour(self.behaviour):
                self.voltage_threesolds['ResIN3'][1] = "ok"
            else:
                self.voltage_threesolds['ResIN3'][1] = "bad"
            self.control_log.add(self.name,
                                 "Результат работы срабатывания по u_nom: " + self.voltage_threesolds['ResIN3'][1],
                                 True)


            # расчитываем погрешность для IN3 u_min
            self.u_delta = self.percentage(self.u_delta_percent, self.u_in_min)
            # установить максимальный порог на ЛБП с учетом погрешности
            assert self.power_supply.set_voltage(self.u_in_min - self.u_delta)
            assert self.power_supply.check_voltage(self.u_in_min - self.u_delta)

            # ожидаем пропажу АКБ
            self.wait_time(70)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0, "error_pwr2": 0,
                              "error_btr": 1, "error_out1": 0, "error_out2": 0, "charge_btr": 1}

            # определяем по поведению сработал ли порог u_min
            if self.psc24_10.check_behaviour(self.behaviour):
                self.voltage_threesolds['ResIN3'][0] = "ok"
            else:
                self.voltage_threesolds['ResIN3'][0] = "bad"
            self.control_log.add(self.name,
                                 "Результат работы срабатывания по u_min: " + self.voltage_threesolds['ResIN3'][0],
                                 True)

            assert self.power_supply.output("OFF")
            assert self.power_supply.check_output("OFF")

            self.wait_time(5)

            # Выключить ЛБП на IN3
            assert self.dout_103.command("KL33", "OFF")
            assert self.din_202.check_voltage("KL33", "OFF")

            # отключаем АКБ
            assert self.dout_103.command(self.BTR, "ON")
            assert self.din_202.check_voltage(self.BTR, "ON")

            self.wait_time(70)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0, "error_pwr2": 0,
                              "error_btr": 0, "error_out1": 0, "error_out2": 0}

            # проверяем поведение
            assert self.psc24_10.check_behaviour(self.behaviour)

            self.control_log.add(self.name, "Проверка порогов по напряжению завершена", True)
            return True
        except:
            self.main_log.set_stage("functional_fail")
            self.control_log.add(self.name, "Ошибка при проверке порогов по напряжению", False)
            return False

    # проверка ТЭН'а и обрыв связи с датчиком stage 6 (готово)
    def check_ten(self):
        self.control_log.add(self.name, "Проверка работы ТЭН и обрыва связи с датчиком", True)
        try:

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0, "error_pwr2": 0,
                              "error_btr": 0, "error_out1": 0, "error_out2": 0, "ten": 0, "apts": 0}

            assert self.psc24_10.check_behaviour(self.behaviour)

            # включить ТЭН
            assert self.eeprom.sensor_on()
            self.wait_time(5)

            # проверка работы датчика
            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0, "error_pwr2": 0,
                              "error_btr": 0, "error_out1": 0, "error_out2": 0, "ten": 1, "apts": 0}

            # считываем значение датчика
            assert self.psc24_10.check_ti("T1")
            self.temp_t1 = self.psc24_10.get_ti()
            if (self.temp_t1 > -255.0 and self.psc24_10.check_behaviour(self.behaviour)):
                self.control_log.add(self.name, "Датчик считан, температура = " + str(self.temp_t1), True)
                self.ten['Работа датчика'][0] = "ok"
                self.control_log.add(self.name, "ТЭН включен", True)
                self.ten['Работа ТЭН'][0] = "ok"
            else:
                self.control_log.add(self.name, "Неудалось считать температуру или температура = " + str(self.temp_t1), False)
                self.ten['Работа датчика'][0] = "fail"
                self.control_log.add(self.name, "Неудалось включить ТЭН", False)
                self.ten['Работа ТЭН'][0] = "fail"

            self.wait_time(5)

            # обрываем связь с датчиком
            assert self.dout_104.command("KL34", "ON")
            assert self.din_202.check_voltage("KL34", "ON")

            self.wait_time(20)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0,
                              "error_pwr2": 0, "error_btr": 0, "error_out1": 0, "error_out2": 0, "ten": 0,"apts": 0}
            # проверка работы датчика
            assert self.psc24_10.check_ti("T1")
            self.temp_t1 = self.psc24_10.get_ti()
            if (self.temp_t1 == -255.0 and self.psc24_10.check_behaviour(self.behaviour)):
                self.control_log.add(self.name, "Датчик считан, температура = " + str(self.temp_t1), True)
                self.control_log.add(self.name, "ТЭН отключен ", True)
                self.control_log.add(self.name, "Обрыв - успешно ", True)
                self.ten['Работа ТЭН'][0] = "ok"
                self.ten['Работа датчика'][0] = "ok"
                self.emergency_modes['Результат'][2] = "ok"
            else:
                self.control_log.add(self.name, "Неудалось считать температуру или температура = " + str(self.temp_t1), False)
                self.control_log.add(self.name, "Неудалось отключить ТЭН", False)
                self.control_log.add(self.name, "Обрыв - не успешно ", False)
                self.ten['Работа ТЭН'][0] = "fail"
                self.ten['Работа датчика'][0] = "fail"
                self.emergency_modes['Результат'][2] = "fail"

            # восстанавливаем связь с датчиком
            assert self.dout_104.command("KL34", "OFF")
            assert self.din_202.check_voltage("KL34", "OFF")

            self.wait_time(15)
            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0, "error_pwr2": 0,
                              "error_btr": 0, "error_out1": 0, "error_out2": 0, "ten": 1, "apts": 0}
            # проверка работы датчика (восстановление)
            assert self.psc24_10.check_ti("T1")
            self.temp_t1 = self.psc24_10.get_ti()
            if (self.temp_t1 > -255.0 and self.psc24_10.check_behaviour(self.behaviour)):
                self.control_log.add(self.name, "Датчик считан, температура = " + str(self.temp_t1), True)
                self.control_log.add(self.name, "ТЭН включен", True)
                self.ten['Работа ТЭН'][0] = "ok"
                self.ten['Работа датчика'][0] = "ok"
            else:
                self.control_log.add(self.name, "Неудалось считать температуру или температура = " + str(self.temp_t1), False)
                self.control_log.add(self.name, "Неудалось включить ТЭН", False)
                self.ten['Работа ТЭН'][0] = "fail"
                self.ten['Работа датчика'][0] = "fail"

            # отключить ТЭН
            assert self.eeprom.sensor_off()
            self.wait_time(5)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0, "error_pwr2": 0,
                              "error_btr": 0, "error_out1": 0, "error_out2": 0, "ten": 0, "apts": 0}
            # проверка работы датчика
            assert self.psc24_10.check_ti("T1")
            self.temp_t1 = self.psc24_10.get_ti()
            if (self.temp_t1 > -255.0 and self.psc24_10.check_behaviour(self.behaviour)):
                self.control_log.add(self.name, "Датчик считан, температура = " + str(self.temp_t1), True)
                self.control_log.add(self.name, "ТЭН отключен", True)
                self.ten['Работа ТЭН'][0] = "ok"
                self.ten['Работа датчика'][0] = "ok"
            else:
                self.control_log.add(self.name, "Неудалось считать температуру или температура = " + str(self.temp_t1), False)
                self.control_log.add(self.name, "Неудалось отключить ТЭН", False)
                self.ten['Работа ТЭН'][0] = "fail"
                self.ten['Работа датчика'][0] = "fail"

            self.wait_time(5)
            self.control_log.add(self.name, "Stage #6 Проверка работы ТЭН и обрыва связи с датчиком завершена", True)
            return True
        except:
            self.main_log.set_stage("functional_fail")
            self.control_log.add(self.name, "Ошибка проверки работы ТЭН и обрыва связи с датчиком", False)
            return False

    # переключение каналов stage 7 (в работе добавить нагрузку и коммутатор)
    def switch_channel(self):
        self.control_log.add(self.name, "Переключение каналов (Проверка провалов по напряжению)", True)
        try:

            ##### FOR TEST
            # отключаем IN2
            assert self.dout_101.command(self.IN2, "ON")
            assert self.din_201.check_voltage(self.IN2, "ON")
            # отключаем IN1
            assert self.dout_101.command(self.IN1, "ON")
            assert self.din_201.check_voltage(self.IN1, "ON")

            assert self.dout_103.command(self.BTR, "ON")
            assert self.din_202.check_voltage(self.BTR, "ON")
            ##### FOR TEST

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0, "error_pwr2": 0,
                              "error_out1": 0, "error_out2": 0}

            # проверяем поведение
            assert self.psc24_10.check_behaviour(self.behaviour)

            # создать новый объект роутером
            self.router = devices.Router("192.168.1.1", "Роутер")
            # Включить IN1, IN2, IN3
            # Подключить нагрузку и коммутатор с роутером
            # подключаем out1/2
            assert self.dout_103.command("KM15", "ON")
            assert self.din_202.check_voltage("KM15", "ON")

            assert self.dout_103.command("KM14", "ON")
            assert self.din_202.check_voltage("KM14", "ON")

            self.wait_time(10)

            # подключаем коммутатор (для пинга)
            assert self.dout_102.command("KL26", "ON")
            assert self.din_201.check_voltage("KL26", "ON")

            # подключаем коммутатор (для нагрузки)
            assert self.dout_102.command("KL18", "ON")
            assert self.din_201.check_voltage("KL18", "ON")

            # подключаем коммутатор (для нагрузки)
            assert self.dout_102.command("KL19", "ON")
            assert self.din_201.check_voltage("KL19", "ON")

            # подключаем коммутатор (для нагрузки)
            assert self.dout_102.command("KL20", "ON")
            assert self.din_201.check_voltage("KL20", "ON")

            # подключаем коммутатор (для нагрузки)
            assert self.dout_102.command("KL21", "ON")
            assert self.din_201.check_voltage("KL21", "ON")

            self.wait_time(70)


            self.router.start_check()
            # проверяем есть ли пинг
            if self.router.get_result():
                self.control_log.add(self.name, "Связь с роутером есть пинг ОК", True)
            else:
                self.control_log.add(self.name, "Нет связи с роутером", False)
                self.switching_channels['Переключение каналов'][0] = "fail"
                assert False

            # отключаем IN2
            assert self.dout_101.command(self.IN2, "OFF")
            assert self.din_201.check_voltage(self.IN2, "OFF")
            # отключаем IN1
            assert self.dout_101.command(self.IN1, "OFF")
            assert self.din_201.check_voltage(self.IN1, "OFF")

            self.wait_time(5)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 0, "pwr2": 0, "btr": 1, "key1": 1, "key2": 1, "error_pwr1": 1, "error_pwr2": 1,
                              "error_out1": 0, "error_out2": 0}

            assert self.psc24_10.check_behaviour(self.behaviour)

            # подключаем IN2
            assert self.dout_101.command(self.IN2, "ON")
            assert self.din_201.check_voltage(self.IN2, "ON")

            self.wait_time(5)

            # подключаем IN1
            assert self.dout_101.command(self.IN1, "ON")
            assert self.din_201.check_voltage(self.IN1, "ON")

            self.wait_time(5)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0, "error_pwr2": 0,
                            "error_out1":    0, "error_out2": 0}

            assert self.psc24_10.check_behaviour(self.behaviour)

            # проверяем есть ли пинг
            if self.router.get_result():
                self.control_log.add(self.name, "Связь с роутером есть пинг ОК", True)
                self.switching_channels['Переключение каналов'][0] = "ok"
                self.router.set_result()
            else:
                self.control_log.add(self.name, "Нет связи с роутером", False)
                self.switching_channels['Переключение каналов'][0] = "bad"
                assert False

            # подключаем коммутатор
            assert self.dout_102.command("KL26", "OFF")
            assert self.din_201.check_voltage("KL26", "OFF")

            # отключаем коммутатор (для нагрузки)
            assert self.dout_102.command("KL18", "OFF")
            assert self.din_201.check_voltage("KL18", "OFF")

            # отключаем коммутатор (для нагрузки)
            assert self.dout_102.command("KL19", "OFF")
            assert self.din_201.check_voltage("KL19", "OFF")

            # подключаем коммутатор (для нагрузки)
            assert self.dout_102.command("KL20", "OFF")
            assert self.din_201.check_voltage("KL20", "OFF")

            # отключаем коммутатор (для нагрузки)
            assert self.dout_102.command("KL21", "OFF")
            assert self.din_201.check_voltage("KL21", "OFF")

            assert self.dout_103.command("KM14", "OFF")
            assert self.din_202.check_voltage("KM14", "OFF")

            assert self.dout_103.command("KM15", "OFF")
            assert self.din_202.check_voltage("KM15", "OFF")

            assert self.psc24_10.check_behaviour(self.behaviour)

            self.main_log.set_stage("functional_pass")
            self.control_log.add(self.name, "Переключение каналов (Проверка провалов по напряжению пройдена)", True)
            return True
        except:
            self.main_log.set_stage("functional_fail")
            self.switching_channels['Переключение каналов'][0] = "fail"
            self.control_log.add(self.name, "Переключение каналов (Проверка провалов по напряжению не пройдена)", False)
            return False

    # аварийные режимы работы stage 8
    def overload_mode(self):
        self.main_log.set_stage("emergency")
        self.control_log.add(self.name, "Проверка режима перегрузка", True)
        try:
            timeout = self.psc24_10.timeout
            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0,
                              "error_pwr2": 0, "error_out1": 0, "error_out2": 0}

            assert self.psc24_10.check_behaviour(self.behaviour)

            # подключаем OUT1 реостат
            assert self.dout_103.command("KM16", "ON")
            assert self.din_202.check_voltage("KM16", "ON")

            # подключаем OUT1 коммутаторы
            assert self.dout_103.command("KM14", "ON")
            assert self.din_202.check_voltage("KM14", "ON")

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0,
                              "error_pwr2": 0,  "error_out1": 0, "error_out2": 0}

            assert self.psc24_10.check_behaviour(self.behaviour)

            # записываем уставки по току out1 = 9; out2 = 1
            assert self.eeprom.write_max_current_value(9, 1)

            assert self.psc24_10.check_behaviour(self.behaviour)

            if self.config.get("device_name") == "psc24_10":
                assert self.dout_104.command("KM13", "ON")
                assert self.din_202.check_voltage("KM13", "ON")
            if self.config.get("device_name") == "psc48_10":
                assert self.dout_104.command("KM12", "ON")
                assert self.din_202.check_voltage("KM12", "ON")

            self.wait_time(15)

            # поведение перегруза
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 0, "key2": 1, "error_pwr1": 0,
                              "error_pwr2": 0, "error_out1": 1, "error_out2": 0}

            assert self.ammeter_out1.check_ti()
            self.i_nom = self.ammeter_out1.get_ti()

            if self.i_nom <= 0.0:
                self.control_log.add(self.name, "Телеизмерения out1 не достоверны " + str(self.i_nom), True)
                assert False

            self.psc24_10.set_timeout(2)
            for load in self.switches_load:
                self.control_log.add(self.name, "Ток out1 " + str(self.i_nom), True)
                if self.psc24_10.check_behaviour(self.behaviour):
                    self.control_log.add(self.name, "Out1 исправно ушел в защиту от перегрузки ", True)
                    break
                if self.i_nom > 9.5:
                    self.control_log.add(self.name, "Устройство не уходит в защиту на out1 " + str(self.i_nom), False)
                    assert False
                assert self.dout_102.command(load, "ON")
                assert self.din_201.check_voltage(load, "ON")
                self.wait_time(2)
                assert self.ammeter_out1.check_ti()
                self.i_nom = self.ammeter_out1.get_ti()

            self.psc24_10.set_timeout(timeout)

            assert self.dout_104.command("KM12", "OFF")
            assert self.din_202.check_voltage("KM12", "OFF")
            assert self.dout_104.command("KM13", "OFF")
            assert self.din_202.check_voltage("KM13", "OFF")

            for load in self.switches_load:
                assert self.dout_102.command(load, "OFF")
                assert self.din_201.check_voltage(load, "OFF")

            self.wait_time(25)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0,
                              "error_pwr2": 0, "error_out1": 0, "error_out2": 0}

            # отключаем OUT1 и подключаем OUT2

            assert self.psc24_10.check_behaviour(self.behaviour)

            # отключаем OUT1 коммутаторы
            assert self.dout_103.command("KM14", "OFF")
            assert self.din_202.check_voltage("KM14", "OFF")

            # отключаем OUT1 реостат
            assert self.dout_103.command("KM16", "OFF")
            assert self.din_202.check_voltage("KM16", "OFF")

            self.wait_time(10)

            # подключаем OUT2 реостат
            assert self.dout_103.command("KM15", "ON")
            assert self.din_202.check_voltage("KM15", "ON")

            # подключаем OUT2 коммутаторы
            assert self.dout_103.command("KM17", "ON")
            assert self.din_202.check_voltage("KM17", "ON")

            # записываем уставки по току out1 = 1; out2 = 9
            assert self.eeprom.write_max_current_value(1, 9)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0,
                              "error_pwr2": 0, "error_out1": 0, "error_out2": 0}

            assert self.psc24_10.check_behaviour(self.behaviour)

            if self.config.get("device_name") == "psc24_10":
                assert self.dout_104.command("KM13", "ON")
                assert self.din_202.check_voltage("KM13", "ON")
            if self.config.get("device_name") == "psc48_10":
                assert self.dout_104.command("KM12", "ON")
                assert self.din_202.check_voltage("KM12", "ON")

            self.wait_time(15)
                # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 0, "error_pwr1": 0,
                              "error_pwr2": 0, "error_out1": 0, "error_out2": 1}

            assert self.ammeter_out2.check_ti()
            self.i_nom = self.ammeter_out2.get_ti()

            if self.i_nom <= 0.0:
                self.control_log.add(self.name, "Телеизмерения out2 не достоверны " + str(self.i_nom), True)
                assert False

            self.psc24_10.set_timeout(2)
            for load in self.switches_load:
                self.control_log.add(self.name, "Ток out2 " + str(self.i_nom), True)
                if self.psc24_10.check_behaviour(self.behaviour):
                    self.control_log.add(self.name, "Out2 исправно ушел в защиту от перегрузки ", True)
                    break
                if self.i_nom > 10:
                    self.control_log.add(self.name, "Устройство не уходит в защиту на out1 " + str(self.i_nom), False)
                    assert False
                assert self.dout_102.command(load, "ON")
                assert self.din_201.check_voltage(load, "ON")
                self.wait_time(2)
                assert self.ammeter_out2.check_ti()
                self.i_nom = self.ammeter_out2.get_ti()

            self.psc24_10.set_timeout(timeout)

            assert self.dout_104.command("KM12", "OFF")
            assert self.din_202.check_voltage("KM12", "OFF")
            assert self.dout_104.command("KM13", "OFF")
            assert self.din_202.check_voltage("KM13", "OFF")

            for load in self.switches_load:
                assert self.dout_102.command(load, "OFF")
                assert self.din_201.check_voltage(load, "OFF")

            self.wait_time(25)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0,
                              "error_pwr2": 0, "error_out1": 0, "error_out2": 0}

            assert self.psc24_10.check_behaviour(self.behaviour)

            # отключить OUT2 коммутаторы
            assert self.dout_103.command("KM15", "OFF")
            assert self.din_202.check_voltage("KM15", "OFF")

            # отключить OUT2 реостат
            assert self.dout_103.command("KM17", "OFF")
            assert self.din_202.check_voltage("KM17", "OFF")

            # записываем уставки по току out1 = default; out2 = default
            assert self.eeprom.write_max_current_value(5, 5)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0,
                              "error_pwr2": 0, "error_out1": 0, "error_out2": 0}

            assert self.psc24_10.check_behaviour(self.behaviour)

            self.emergency_modes['Результат'][1] = "ok"
            self.control_log.add(self.name, "Проверка режима перегрузка прошла успешно", True)
            return True
        except:
            # возвращаем таймаут
            self.psc24_10.set_timeout(timeout)
            # записываем уставки по току out1 = default; out2 = default
            assert self.eeprom.write_max_current_value(5, 5)
            self.main_log.set_stage("emergency_fail")
            self.control_log.add(self.name, "Ошибка проверки режима перегрузка", False)
            self.emergency_modes['Результат'][1] = "bad"
            return False

    # аварийные режимы работы stage 9
    def short_curciut_mode(self):
        self.control_log.add(self.name, "Проверка режима короткого замыкания", True)
        try:
            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0, "error_pwr2": 0,
                              "error_btr": 0, "error_out1": 0, "error_out2": 0}

            assert self.psc24_10.check_behaviour(self.behaviour)

            # записываем уставки по току out1 = 9; out2 = 0
            assert self.eeprom.write_max_current_value(9, 1)

            # подключаем OUT1 реостат
            assert self.dout_103.command("KM16", "ON")
            assert self.din_202.check_voltage("KM16", "ON")

            # если версия 48V то подаём 6А
            # подаем нагрузку с реостата 10А
            if self.config.get("device_name") == "psc24_10":
                assert self.dout_104.command("KM13", "ON")
                assert self.din_202.check_voltage("KM13", "ON")
            if self.config.get("device_name") == "psc48_10":
                assert self.dout_104.command("KM12", "ON")
                assert self.din_202.check_voltage("KM12", "ON")

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0,
                              "error_pwr2": 0, "error_btr": 0, "error_out1": 0, "error_out2": 0}

            assert self.psc24_10.check_behaviour(self.behaviour)

            self.wait_time(10)

            assert self.psc24_10.check_ti("I_OUT1")
            self.i_out1_fact = self.psc24_10.get_ti()
            self.control_log.add(self.name, "Нагрузка на OUT1 " + str(self.i_out1_fact) + " A", True)

            # предполагаемое поведение
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0,
                              "error_pwr2": 0, "error_btr": 0, "error_out1": 0, "error_out2": 0}

            assert self.psc24_10.check_behaviour(self.behaviour)

            # КЗ на OUT1
            assert self.dout_104.command("KM19", "ON")
            assert self.din_202.check_voltage("KM19", "ON")

            self.wait_time(15)

            # предполагаемое поведение во время КЗ
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 0, "key2": 1, "error_pwr1": 0,
                              "error_pwr2": 0, "error_btr": 0, "error_out1": 1, "error_out2": 0}

            assert self.psc24_10.check_behaviour(self.behaviour)

            # снять КЗ на OUT1
            assert self.dout_104.command("KM19", "OFF")
            assert self.din_202.check_voltage("KM19", "OFF")

            self.wait_time(25)

            # предполагаемое поведение после КЗ
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0,
                              "error_pwr2": 0, "error_btr": 0, "error_out1": 0, "error_out2": 0}

            assert self.psc24_10.check_behaviour(self.behaviour)

            assert self.dout_104.command("KM12", "OFF")
            assert self.din_202.check_voltage("KM12", "OFF")
            assert self.dout_104.command("KM13", "OFF")
            assert self.din_202.check_voltage("KM13", "OFF")

            # отключаем OUT1 реостат
            assert self.dout_103.command("KM16", "OFF")
            assert self.din_202.check_voltage("KM16", "OFF")

            # записываем уставки по току out2 = 0.2; out1 = 9.7
            assert self.eeprom.write_max_current_value(1, 9)

            # подключаем OUT2 реостат
            assert self.dout_103.command("KM17", "ON")
            assert self.din_202.check_voltage("KM17", "ON")

            # если версия 48V то подаём 6А
            # подаем нагрузку с реостата 10А
            if self.config.get("device_name") == "psc24_10":
                assert self.dout_104.command("KM13", "ON")
                assert self.din_202.check_voltage("KM13", "ON")
            if self.config.get("device_name") == "psc48_10":
                assert self.dout_104.command("KM12", "ON")
                assert self.din_202.check_voltage("KM12", "ON")

            # предполагаемое поведение после подключения OUT2
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0,
                              "error_pwr2": 0, "error_btr": 0, "error_out1": 0, "error_out2": 0}

            assert self.psc24_10.check_behaviour(self.behaviour)

            assert self.psc24_10.check_ti("I_OUT2")
            self.i_out2_fact = self.psc24_10.get_ti()
            self.control_log.add(self.name, "Нагрузка на OUT2 " + str(self.i_out2_fact) + " A", True)


            # КЗ на OUT2 ПРОВЕРИТЬ!!!! out1  РАБОТАЕТ!
            assert self.dout_104.command("KM19", "ON")
            assert self.din_202.check_voltage("KM19", "ON")

            self.wait_time(15)

            # предполагаемое поведение во время КЗ
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 0, "error_pwr1": 0,
                              "error_pwr2": 0, "error_btr": 0, "error_out1": 0, "error_out2": 1}

            assert self.psc24_10.check_behaviour(self.behaviour)

            # снять КЗ на OUT2
            assert self.dout_104.command("KM19", "OFF")
            assert self.din_202.check_voltage("KM19", "OFF")

            self.wait_time(25)

            # предполагаемое поведение после КЗ
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0,
                              "error_pwr2": 0, "error_btr": 0, "error_out1": 0, "error_out2": 0}

            assert self.psc24_10.check_behaviour(self.behaviour)


            # снимаем нагрузку с реостата 10А или 6А
            assert self.dout_104.command("KM12", "OFF")
            assert self.din_202.check_voltage("KM12", "OFF")
            assert self.dout_104.command("KM13", "OFF")
            assert self.din_202.check_voltage("KM13", "OFF")

            # отключить OUT2 реостат
            assert self.dout_103.command("KM17", "OFF")
            assert self.din_202.check_voltage("KM17", "OFF")

            self.wait_time(10)

            # предполагаемое поведение после КЗ
            self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0,
                              "error_pwr2": 0, "error_btr": 0, "error_out1": 0, "error_out2": 0}

            assert self.psc24_10.check_behaviour(self.behaviour)

            # записываем уставки по току out1 = default; out2 = default
            assert self.eeprom.write_max_current_value(self.out_i_1_temp, self.out_i_2_temp)

            self.emergency_modes['Результат'][0] = "ok"
            self.main_log.set_stage("emergency_pass")
            self.control_log.add(self.name, "Проверка режима короткого замыкания прошла успешно", True)
            return True
        except:
            self.main_log.set_stage("emergency_fail")
            self.control_log.add(self.name, "Ошибка проверки режима короткоткого замыкания", False)
            self.emergency_modes['Результат'][0] = "bad"
            return False

    # сбросить все управление
    def off_all_control(self):
        try:
            assert self.dout_101.off_enabled()
            # добавить задержки
            assert self.dout_102.off_enabled()
            assert self.dout_103.off_enabled()
            assert self.dout_104.off_enabled()
            assert self.power_supply.output("OFF")
            assert self.power_supply.check_output("OFF")
            self.clear_protocol_data()
            self.wait_time(10)
            return True
        except:
            return False

    # чистка протокола и поведения
    def clear_protocol_data(self):
        # сбрасываем поведение
        self.behaviour = {"pwr1": 1, "pwr2": 0, "btr": 0, "key1": 1, "key2": 1, "error_pwr1": 0, "error_pwr2": 0,
                     "error_btr": 0,
                     "error_out1": 0, "error_out2": 0, "charge_btr": 1, "ten": 0, "apts": 0}

        # сбрасываем данные для протокола
        self.check_number = {'Порядковый номер': [' ']}
        self.serial_number = {'Серийный номер': [' ']}
        self.soft_version = {'Версия ПО': [' '], 'Фактическая': [' ']}
        self.voltage = {'Канал, U': ['IN1', 'IN2', 'IN3'], 'Unom': ['', '', ''], 'Ufact': ['', '', ''],
                   'Uerror_rate_nom': ['', '', ''], 'Uerror_rate_fact': ['', '', ''], 'result': ['', '', '']}
        self.current = {'Канал, I': ['OUT1', 'OUT2'], 'Inom': ['', ''], 'Ifact': ['', ''], 'Ierror_rate_nom': ['', ''],
                   'Ierror_rate_nom': ['', ''], 'Ierror_rate_fact': ['', ''], 'result': ['', '']}
        self.current_difference = {'OUT1': [' '], 'OUT2': [' '], 'Idifference_nom': [' '], 'Idifference_fact': [' '], 'result': [' ']}
        self.voltage_threesolds = {'Пороги, U': ['min, U', 'nom, U', 'max, U', ''], 'U_IN1': ['', '', '', ''],
                              'ResIN1': ['', '', '', ''], 'U_IN2': ['', '', '', ''], 'ResIN2': ['', '', '', ''],
                              'U_IN3': ['', '', '', ''], 'ResIN3': ['', '', '', ''], 'ChargeBTR': ['', '', '', '']}
        self.switching_channels = {'Переключение каналов': [' ']}
        self.ten = {'Работа ТЭН': [' '], 'Работа датчика': [' ']}
        self.emergency_modes = {'Аварийные режимы': ['Режим КЗ', 'Режим перегрузки', 'Обрыв связи датчика', ''],
                           'Результат': ['', '', '', '']}

    # для теста
    def for_test(self):
        try:
            modb_dout_101 = devices.Modb()
            assert modb_dout_101.getConnection("DOUT_101", self.device_com, 101, 115200, self.control_log)
            self.dout_101 = devices.Dout(modb_dout_101.getСonnectivity(), dout_names_101, "DOUT_101", self.control_log, 10)
            self.dout_101.command("KL1", "ON")
        except:
            return False

    # главная функция
    def main1(self):
        # инициализация стенда
        try:
            # for git
            self.control_log.set_start(False)
            protocol_time = str(datetime.now().strftime('%d.%m.%Y-%H-%M'))
            self.config = self.settings.load("settings.cfg")
            self.control_com = self.config.get("control_com")
            self.ammeter_com = self.config.get("ammeter_com")
            self.device_com = self.config.get("device_com")
            count_devices = int(self.config.get("checked_list"))
            time.sleep(2)
            assert self.prepare()
            assert self.off_all_control()
        except AssertionError:
            self.main_log.set_start(False)
            self.main_log.set_finish(True)
            self.control_log.add("Тестирование", "Тестирование завершено", False)
            # закончить опрос backend'a
            self.control_log.set_finish(True)
            return False

        flag = False
        # контроль сброса и аварийного сброса стенда
        off_control = False
        # результаты по ходу проверки
        ok = 0
        bad = 0
        i = 1
        while True:
            while i <= count_devices:
                try:
                    flag = True
                    off_control = False
                    self.control_log.add("Девайс номер ", str(i), True)
                    self.check_number['Порядковый номер'][0] = str(i)
                    # ОБЯЗАТЕЛЬНО В НАЧАЛЕ ЦИКЛА
                    self.main_log.set_finish(False)
                    self.main_log.set_device_count(i - 1)
                    time.sleep(2)
                    assert self.dout_103.command(self.device[i], "ON")
                    assert self.din_202.check_voltage(self.device[i], "ON")
                    self.wait_time(2)
                    assert self.first_start()
                    self.wait_time(2)
                    assert self.configurate_check()
                    self.wait_time(2)
                    assert self.measurements_check()
                    self.wait_time(2)
                    assert self.check_voltage_thresholds()
                    self.wait_time(2)
                    assert self.check_ten()
                    self.wait_time(2)
                    assert self.switch_channel()
                    self.wait_time(2)
                    assert self.overload_mode()
                    self.wait_time(2)
                    assert self.short_curciut_mode()
                    self.wait_time(10)

                    assert protocol.create_protocol(protocol_time + "_tested_" + str(count_devices), self.control_log, self.check_number, self.serial_number, self.soft_version,
                                             self.voltage, self.current, self.current_difference, self.voltage_threesolds, self.switching_channels,
                                             self.ten, self.emergency_modes)
                    self.wait_time(2)

                    # отключать все dout'ы в случае успешной проверки
                    off_control = self.off_all_control()
                    assert off_control
                    self.control_log.add(self.name, "Сброс управления выполнен", False)

                    # ОБЯЗАТЕЛЬНО В КОНЦЕ ЦИКЛА
                    self.main_log.set_start(True)
                    self.main_log.set_finish(True)
                    i = i + 1
                    self.wait_time(5)
                    # # количество хороших модулей
                    ok = ok + 1
                except AssertionError:
                    # количество плохих модулей
                    bad = bad + 1
                    protocol.create_protocol(protocol_time + "_tested_" + str(count_devices), self.control_log, self.check_number, self.serial_number, self.soft_version,
                                             self.voltage, self.current, self.current_difference,
                                             self.voltage_threesolds, self.switching_channels,
                                             self.ten, self.emergency_modes)
                    if off_control != True:
                        in_off_control = self.off_all_control()
                        if in_off_control:
                            self.control_log.add(self.name,
                                                 "Сброс управления выполнен", False)
                        else:
                            self.control_log.add(self.name,
                                                 "Неудалось сбросить модули управления, требуется ручная перезагрузка",
                                                 False)
                            break

                    # отключать все dout'ы в случае неудачи
                    self.main_log.set_start(False)
                    self.main_log.set_finish(True)
                    i = i + 1
                    time.sleep(2)
            if flag:
                self.control_log.add("Тестирование", "Тестирование завершено", True)
                # закончить опрос backend'a
                self.control_log.set_finish(True)
                # time.sleep(2)
                break



