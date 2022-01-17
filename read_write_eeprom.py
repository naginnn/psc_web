# Предпоследний параметр в конфигураторе играет роль!

import serial
import serial.tools.list_ports
import time
import struct
import FloatToHex, cgi, sys, math
import binascii
import time
from datetime import datetime

import engine


def serial_ports():
    ports = serial.tools.list_ports.comports()
    result = []
    event = 1
    for port, desc, hwid in sorted(ports):
        try:
            if (desc.find('CP') != -1):
                # print("{}: {}".format(port, desc, hwid))
                result.append(port)
                s = serial.Serial(port)
                s.close()
        except (OSError, serial.SerialException):
            pass
    return result

register_names = {"interface": 0x01, "tsmask": 0x02, "offset": 0x03, "pw1u": 0x04,
                  "pw2u": 0x05, "btru": 0x06, "outi": 0x07, "charge": 0x08, "ten": 0x09,
                  "sensors": 0x0A, "readsensor": 0x0B, "select_pwr": 0x0C, "ty": 0x0D,
                  "error_pwr": 0x0E, "ubatlow": 0x0F, "offsetinzero": 0x10, "offset_i": 0x11,
                  "calib_i": 0x12, "versions": 0x18, "current_param": 0x32, "serial_number": 0x33}
registers_pointer = {
    0x01: {"InterfaceAdress": 0x01, "InterfaceSpeed": 0x02, "InterfaceChet": 0x03, "ProtocolType": 0x04},
    0x02: {"TsMask1": 0x01, "TsMask2": 0x02, "TsMask3": 0x03, "TiMask1": 0x04, "TiMask2": 0x05, "TiMask3": 0x06},
    0x03: {"Offset101Ts": 0x01, "Offset101Ti": 0x02, "Offset101Ty": 0x03, "Offset101Tii": 0x04, "Hueta": 0x05},
    0x04: {"pw1_u_nom": 0x01, "pw1_u_max": 0x02, "pw1_u_min": 0x03, "pw1_u_max_hyst": 0x04, "pw1_u_min_hyst": 0x05},
    0x05: {"pw2_u_nom": 0x01, "pw2_u_max": 0x02, "pw2_u_min": 0x03, "pw2_u_max_hyst": 0x04, "pw2_u_min_hyst": 0x05},
    0x06: {"btr_u_nom": 0x01, "btr_u_max": 0x02, "btr_u_min": 0x03, "btr_u_max_hyst": 0x04, "btr_u_min_hyst": 0x05},
    0x07: {"out_i_1": 0x01, "out_i_2": 0x02},
    0x08: {"charge_err_min": 0x01, "charge_u_max": 0x02, "charge_u_min": 0x03, "charge_i_stable": 0x04,
           "charge_u_stable": 0x05},
    0x09: {"limit_ten": 0x01, "sensor_select": 0x02, "ten_or_fan": 0x03, "heat_for_load": 0x04},
    0x0A: {"sensor_t1": 0x01, "sensor_t2": 0x02, "sensor_t3": 0x03, "sensor_t4": 0x04, "sensor_t5": 0x05},
    0x0B: {"read_id_t1": 0x01, "read_id_t2": 0x02, "read_id_t3": 0x03, "read_id_t4": 0x04, "read_id_t5": 0x05},
    0x0C: {"select_pw": 0x01},
    0x0D: {"tu": 0x01},
    0x0E: {"error_pwr": 0x01},
    0x0F: {"u_bat_low_set": 0x01, "u_bat_low_hyst": 0x02},
    0x10: {"offset_in_zero": 0x01, "memory_how_offset": 0x02},
    0x11: {"offset_i1": 0x01, "offset_i2": 0x02},
    0x12: {"calib_i1": 0x01, "calib_i2": 0x02},
    0x18: {"bv_major": 0x01, "bv_minor": 0x02, "sv_major": 0x03, "sv_minor": 0x04, "sv_patch": 0x05, "sv_build": 0x06,
           "dev_type": 0x07},
    0x32: {"current_param": 0x01},
    0x33: {"serial_number": 0x01}
}
device_values = {"pw1_u_nom": 0.0, "pw1_u_max": 0.0, "pw1_u_min": 0.0, "pw1_u_max_hyst": 0.0, "pw1_u_min_hyst": 0.0,
    "pw2_u_nom": 0.0, "pw2_u_max": 0.0, "pw2_u_min": 0.0, "pw2_u_max_hyst": 0.0, "pw2_u_min_hyst": 0.0,
    "btr_u_nom": 0.0, "btr_u_max": 0.0, "btr_u_min": 0.0, "btr_u_max_hyst": 0.0, "btr_u_min_hyst": 0.0,
    "out_i_1": 0.0, "out_i_2": 0.0,
    "charge_err_min": 0.0, "charge_u_max": 0.0, "charge_u_min": 0.0, "charge_i_stable": 0.0,"charge_u_stable": 0.0}
HIBYTE = b'\
\x00\xC0\xC1\x01\xC3\x03\x02\xC2\xC6\x06\x07\xC7\x05\xC5\xC4\x04\
\xCC\x0C\x0D\xCD\x0F\xCF\xCE\x0E\x0A\xCA\xCB\x0B\xC9\x09\x08\xC8\
\xD8\x18\x19\xD9\x1B\xDB\xDA\x1A\x1E\xDE\xDF\x1F\xDD\x1D\x1C\xDC\
\x14\xD4\xD5\x15\xD7\x17\x16\xD6\xD2\x12\x13\xD3\x11\xD1\xD0\x10\
\xF0\x30\x31\xF1\x33\xF3\xF2\x32\x36\xF6\xF7\x37\xF5\x35\x34\xF4\
\x3C\xFC\xFD\x3D\xFF\x3F\x3E\xFE\xFA\x3A\x3B\xFB\x39\xF9\xF8\x38\
\x28\xE8\xE9\x29\xEB\x2B\x2A\xEA\xEE\x2E\x2F\xEF\x2D\xED\xEC\x2C\
\xE4\x24\x25\xE5\x27\xE7\xE6\x26\x22\xE2\xE3\x23\xE1\x21\x20\xE0\
\xA0\x60\x61\xA1\x63\xA3\xA2\x62\x66\xA6\xA7\x67\xA5\x65\x64\xA4\
\x6C\xAC\xAD\x6D\xAF\x6F\x6E\xAE\xAA\x6A\x6B\xAB\x69\xA9\xA8\x68\
\x78\xB8\xB9\x79\xBB\x7B\x7A\xBA\xBE\x7E\x7F\xBF\x7D\xBD\xBC\x7C\
\xB4\x74\x75\xB5\x77\xB7\xB6\x76\x72\xB2\xB3\x73\xB1\x71\x70\xB0\
\x50\x90\x91\x51\x93\x53\x52\x92\x96\x56\x57\x97\x55\x95\x94\x54\
\x9C\x5C\x5D\x9D\x5F\x9F\x9E\x5E\x5A\x9A\x9B\x5B\x99\x59\x58\x98\
\x88\x48\x49\x89\x4B\x8B\x8A\x4A\x4E\x8E\x8F\x4F\x8D\x4D\x4C\x8C\
\x44\x84\x85\x45\x87\x47\x46\x86\x82\x42\x43\x83\x41\x81\x80\x40'
LOBYTE = b'\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40'

class FrameCollector:
    # упаковка сетевых настроек (U8)
    def network_settings(self, param, key, value):
        frame = [0x55, 0xAA]
        frame.append(param)
        if (key == 0x01):
            frame.append(0x07)
            frame.append(0x01)
            frame.append(value)
            crc = self.crc_calculate(frame)
            frame.append(crc)
            return frame
        if (key == 0x02):
            frame.append(0x08)
            frame.append(0x02)
            if (value == 2400):
                frame.append(0x18)
                frame.append(0x00)
            if (value == 4800):
                frame.append(0x30)
                frame.append(0x00)
            if (value == 9600):
                frame.append(0x60)
                frame.append(0x00)
            if (value == 19200):
                frame.append(0xC0)
                frame.append(0x00)
            if (value == 38400):
                frame.append(0x80)
                frame.append(0x01)
            if (value == 57600):
                frame.append(0x40)
                frame.append(0x02)
            if (value == 115200):
                frame.append(0x80)
                frame.append(0x04)
            crc = self.crc_calculate(frame)
            frame.append(crc)
            return frame
        if (key == 0x03):
            frame.append(0x07)
            frame.append(0x03)
            if (value == "no"):
                frame.append(0x00)
            if (value == "even"):
                frame.append(0x01)
            if (value == "odd"):
                frame.append(0x02)
            crc = self.crc_calculate(frame)
            frame.append(crc)
            return frame
        if (key == 0x04):
            frame.append(0x07)
            frame.append(0x04)
            if (value == "modbus"):
                frame.append(0x01)
            if (value == "iec101"):
                frame.append(0x02)
            crc = self.crc_calculate(frame)
            frame.append(crc)
            return frame
        print("nothing is read!")
    # упаковка параметров питания (FLOAT32)
    def power_management(self,param, key, value):
        frame = [0x55, 0xAA]
        if (param == 0x0C):
            frame.append(0x0C)
            frame.append(0x08)
            frame.append(0x01)
            if (param == 0x00):
                frame.append(0x00)
            if (param == 0x01):
                frame.append(0x01)
            frame.append(0x00)
            crc = self.crc_calculate(frame)
            frame.append(crc)
            return frame

        if (param == 0x04 or param == 0x05 or param == 0x06 or param == 0x07 or param == 0x08 or param == 0x09
                or param == 0x84 or param == 0x85 or param == 0x86 or param == 0x87 or param == 0x88):
            frame.append(param)
            frame.append(0x0A)
            frame.append(key)
            data = self.float_to_hexfloat(value)
            for d in data:
                frame.append(d)
            crc = self.crc_calculate(frame)
            frame.append(crc)
            return frame
            print("power management is read!")
    # упаковка параметров датчиков (FLOAT32/UINT16)
    def sensor_controls(self,param, key, value):
        frame = [0x55, 0xAA]
        if (param == 0x09 and key == 0x03):
            frame.append(0x09)
            frame.append(0x08)
            frame.append(0x03)
            if (value == "ten"):
                frame.append(0x00)
            if (value == "fan"):
                frame.append(0x01)
            frame.append(0x00)
            crc = self.crc_calculate(frame)
            frame.append(crc)
            return frame
        if (param == 0x09 and key == 0x02):
            frame.append(0x09)
            frame.append(0x08)
            if (key == 0x04 and value == "on"):
                frame.append(0x04)
                frame.append(0x01)
            else:
                frame.append(0x02)
                frame.append(value)
            frame.append(0x00)
            crc = self.crc_calculate(frame)
            frame.append(crc)
            return frame
        if (param == 0x0B):
            frame.append(0x0B)
            frame.append(0x07)
            frame.append(key)
            frame.append(value)
            crc = self.crc_calculate(frame)
            frame.append(crc)
            return frame
        if (param == 0x8A):
            frame.append(0x8A)
            frame.append(0x0E)
            frame.append(key)
            frame.append(0x00)
            frame.append(0x00)
            frame.append(0x00)
            frame.append(0x00)
            frame.append(0x00)
            frame.append(0x00)
            frame.append(0x00)
            frame.append(0x00)
            crc = self.crc_calculate(frame)
            frame.append(crc)
            return frame
    # упаковка серийного номера (FLOAT)
    def serial_number(self, key, value):
        if (key == 0x33 or key == 0xB3):
            frame = [0x55, 0xAA, key, 0x09]
            temp = []
            while value > 0:
                byte = value % 0x100
                temp.append(byte)
                value //= 0x100
            while len(temp) < 4:
                temp.append(0x00)
            frame.append(temp[0])
            frame.append(temp[1])
            frame.append(temp[2])
            frame.append(temp[3])
            crc = self.crc_calculate(frame)
            frame.append(crc)
            return frame
    # расчет crc для пакетов
    def crc_calculate(self,frame):
        i = 2
        crc = 0x00
        while i < len(frame):
            crc = crc + frame[i]
            i = i + 1
        while crc > 256:
            crc = crc - 256
        return crc
    # упаковщик фрейма в модбас реализация 17 функции
    def write_modbus(self, frame):
        data = [0x01, 0x17, 0x40, 0x55, 0x00, 0x04, 0x40, 0xAA, 0x00, 0x04]
        data.append(frame[3])
        for f in frame:
            data.append(f)
        hi, lo = self.crc16(data)
        data.append(hi)
        data.append(lo)
        return data
    # расчет crc16 modbus
    def crc16(self,data):
        crchi = 0xFF
        crclo = 0xFF
        index = 0
        for byte in data:
            index = crchi ^ int(byte)
            crchi = crclo ^ LOBYTE[index]
            crclo = HIBYTE[index]
        # print("{0:02X} {1:02X}".format(crclo, crchi)),
        return crchi, crclo
    # Парсим строку из HEXFLOAT32 в FLOAT
    def hexfloat_to_float(self, response):
        d = 0
        value = "0x"
        i = len(response) - 2
        while d < 4:
            if response[i] == 0:
                value = value + "0"
            value = value + hex(response[i])[2:]
            i = i - 1
            d = d + 1

        value = int(value, 16)
        return round(FloatToHex.hextofloat(value), 2)
    # Парсим строку из HEX в FLOAT (для serial number)
    def hex_to_float(self, response):
        d = 0
        value = "0x"
        i = len(response) - 2
        while d < 4:
            if response[i] == 0:
                value = value + "0"
            value = value + hex(response[i])[2:]
            i = i - 1
            d = d + 1

        value = int(value, 16)
        return value
    # Парсим строку из FLOAT в HEXFLOAT32
    def float_to_hexfloat(self, f):
        data = []
        if f == 0:
            data.append(0)
            data.append(0)
            data.append(0)
            data.append(0)
        else:
            temp2 = hex(struct.unpack('<I', struct.pack('<f', f))[0])[2:]
            data.append(int(temp2[6:8], 16))
            data.append(int(temp2[4:6], 16))
            data.append(int(temp2[2:4], 16))
            data.append(int(temp2[0:2], 16))
        return data

class ReadWriteEEprom:
    soft_version = ""
    serial_number = ""
    device_values = {}
    def __init__(self, name, log, com, braudrate, timeout):
        self.log = log
        self.com = com
        self.braudrate = braudrate
        self.name = name
        self.timeout = timeout
    # Считываем версию прошивки
    def read_soft_version(self):
        time_sec = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        self.log.add(self.name,"Попытка получить версию прошивки", True)
        for t in range(self.timeout):
            try:
                package = []
                read = FrameCollector()
                package.append([0x55, 0xAA, 0x98, 0x07, 0x03, 0x00, 0xA2]) # MAJOR 1.
                package.append([0x55, 0xAA, 0x98, 0x07, 0x04, 0x00, 0xA3]) # MINOR 2.
                package.append([0x55, 0xAA, 0x98, 0x07, 0x05, 0x00, 0xA4]) # PATCH 3.
                package.append([0x55, 0xAA, 0x98, 0x07, 0x06, 0x00, 0xA5]) # BUILD 8.
                ser = serial.Serial(self.com, self.braudrate, timeout=0.3)
                s = ""
                for frame in package:
                    modb_frame = read.write_modbus(frame)
                    values = bytearray(modb_frame)
                    ser.write(values)
                    response = ser.read(len(values))
                    if (len(response) == 0):
                        assert False
                    val = int(response[len(response) - 4])
                    s = s + str(val) + "."
                ser.close()
                s = s[:len(s)-1]
                self.soft_version = s
                self.log.add("EEPROM","Версия прошивки получена: " + self.soft_version ,True)
                return True
            except:
                ser.close()
                self.log.log_data[len(self.log.log_data) - 1] = \
                    time_sec + " " + self.name + \
                    ": Попытка получить версию прошивки " + str(t + 1) + " сек"
                time.sleep(1 - time.time() % 1)
                if t >= self.timeout - 1:
                    self.log.add(self.name, "Неудалось получить версию прошивки", False)
                    return False
        return False
    # Получаем версию
    def get_soft_version(self):
        return self.soft_version
    # записываем настройки электропитания
    def write_power_management(self):
        time_sec = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        self.log.add(self.name, "Попытка записать настройки электропитания", True)
        f = open('eeprom.cfg', 'r')
        params = {}
        for line in f:
            temp = line.split(':')
            for t in temp:
                par_name = t.split("=")
                params.update({par_name[0]: par_name[1]})
        for t in range(self.timeout):
            try:
                package = []
                write = FrameCollector()
                package.append(write.power_management(register_names.get("pw1u"), registers_pointer.get(0x04).get("pw1_u_nom"), float(params.get("pw1_u_nom"))))
                package.append(write.power_management(register_names.get("pw1u"), registers_pointer.get(0x04).get("pw1_u_min"), float(params.get("pw1_u_min"))))
                package.append(write.power_management(register_names.get("pw1u"), registers_pointer.get(0x04).get("pw1_u_max"), float(params.get("pw1_u_max"))))
                package.append(write.power_management(register_names.get("pw1u"), registers_pointer.get(0x04).get("pw1_u_min_hyst"), float(params.get("pw1_u_min_hyst"))))
                package.append(write.power_management(register_names.get("pw1u"), registers_pointer.get(0x04).get("pw1_u_max_hyst"), float(params.get("pw1_u_max_hyst"))))

                # управление питанием pw2
                package.append(write.power_management(register_names.get("pw2u"), registers_pointer.get(0x05).get("pw2_u_nom"), float(params.get("pw2_u_nom"))))
                package.append(write.power_management(register_names.get("pw2u"), registers_pointer.get(0x05).get("pw2_u_min"), float(params.get("pw2_u_min"))))
                package.append(write.power_management(register_names.get("pw2u"), registers_pointer.get(0x05).get("pw2_u_max"), float(params.get("pw2_u_max"))))
                package.append(write.power_management(register_names.get("pw2u"), registers_pointer.get(0x05).get("pw2_u_min_hyst"), float(params.get("pw2_u_min_hyst"))))
                package.append(write.power_management(register_names.get("pw2u"), registers_pointer.get(0x05).get("pw2_u_max_hyst"), float(params.get("pw2_u_max_hyst"))))

                # управление питанием pw3 (BTR)
                package.append(write.power_management(register_names.get("btru"), registers_pointer.get(0x06).get("btr_u_nom"), float(params.get("btr_u_nom"))))
                package.append(write.power_management(register_names.get("btru"), registers_pointer.get(0x06).get("btr_u_min"), float(params.get("btr_u_min"))))
                package.append(write.power_management(register_names.get("btru"), registers_pointer.get(0x06).get("btr_u_max"), float(params.get("btr_u_max"))))
                package.append(write.power_management(register_names.get("btru"), registers_pointer.get(0x06).get("btr_u_min_hyst"), float(params.get("btr_u_min_hyst"))))
                package.append(write.power_management(register_names.get("btru"), registers_pointer.get(0x06).get("btr_u_max_hyst"), float(params.get("btr_u_max_hyst"))))

                # управление питанием outi
                package.append(write.power_management(register_names.get("outi"), registers_pointer.get(0x07).get("out_i_1"), float(params.get("out_i_1"))))
                package.append(write.power_management(register_names.get("outi"), registers_pointer.get(0x07).get("out_i_2"), float(params.get("out_i_2"))))
                package.append(write.power_management(0x87, registers_pointer.get(0x07).get("out_i_1"),float(0)))
                package.append(write.power_management(register_names.get("outi"), registers_pointer.get(0x07).get("out_i_2"),float(0)))
                #
                # управление АКБ
                package.append(write.power_management(register_names.get("charge"), registers_pointer.get(0x08).get("charge_err_min"), float(params.get("charge_err_min"))))
                package.append(write.power_management(register_names.get("charge"), registers_pointer.get(0x08).get("charge_u_max"), float(params.get("charge_u_max"))))
                package.append(write.power_management(register_names.get("charge"), registers_pointer.get(0x08).get("charge_u_min"), float(params.get("charge_u_min"))))
                package.append(write.power_management(register_names.get("charge"), registers_pointer.get(0x08).get("charge_i_stable"), float(params.get("charge_i_stable"))))
                package.append(write.power_management(register_names.get("charge"), registers_pointer.get(0x08).get("charge_u_stable"), float(params.get("charge_u_stable"))))

                # через MODBUS
                ser = serial.Serial(self.com, self.braudrate, timeout=0.3)
                for frame in package:
                    values = bytearray(write.write_modbus(frame))
                    ser.write(values)
                    response = ser.read(len(values))
                    if (len(response) == 0):
                        assert False

                ser.close()
                self.device_values = device_values
                self.log.add("EEPROM", "Настройки электропитания записаны", True)
                return True
            except:
                ser.close()
                self.log.log_data[len(self.log.log_data) - 1] = \
                    time_sec + " " + self.name + \
                    ": Попытка записать настройки электропитания " + str(t + 1) + " сек"
                time.sleep(1 - time.time() % 1)
                if t >= self.timeout - 1:
                    self.log.add(self.name, "Неудалось записать настройки электропитания", False)
                    return False
    # Считываем настройки PSC
    def read_power_management(self):
        time_sec = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        self.log.add(self.name,"Попытка получить настройки электропитания", True)
        for t in range(self.timeout):
            try:
                package = []
                read = FrameCollector()
                package.append(read.power_management(0x84, registers_pointer.get(0x04).get("pw1_u_nom"), float(0)))
                package.append(read.power_management(0x84, registers_pointer.get(0x04).get("pw1_u_max"), float(0)))
                package.append(read.power_management(0x84, registers_pointer.get(0x04).get("pw1_u_min"), float(0)))
                package.append(read.power_management(0x84, registers_pointer.get(0x04).get("pw1_u_max_hyst"), float(0)))
                package.append(read.power_management(0x84, registers_pointer.get(0x04).get("pw1_u_min_hyst"), float(0)))

                package.append(read.power_management(0x85, registers_pointer.get(0x05).get("pw2_u_nom"), float(0)))
                package.append(read.power_management(0x85, registers_pointer.get(0x05).get("pw2_u_max"), float(0)))
                package.append(read.power_management(0x85, registers_pointer.get(0x05).get("pw2_u_min"), float(0)))
                package.append(read.power_management(0x85, registers_pointer.get(0x05).get("pw2_u_max_hyst"), float(0)))
                package.append(read.power_management(0x85, registers_pointer.get(0x05).get("pw2_u_min_hyst"), float(0)))

                package.append(read.power_management(0x86, registers_pointer.get(0x06).get("btr_u_nom"), float(0)))
                package.append(read.power_management(0x86, registers_pointer.get(0x06).get("btr_u_max"), float(0)))
                package.append(read.power_management(0x86, registers_pointer.get(0x06).get("btr_u_min"), float(0)))
                package.append(read.power_management(0x86, registers_pointer.get(0x06).get("btr_u_max_hyst"), float(0)))
                package.append(read.power_management(0x86, registers_pointer.get(0x06).get("btr_u_min_hyst"), float(0)))

                package.append(read.power_management(0x87, registers_pointer.get(0x07).get("out_i_1"), float(0)))
                package.append(read.power_management(0x87, registers_pointer.get(0x07).get("out_i_2"), float(0)))

                package.append(read.power_management(0x88, registers_pointer.get(0x08).get("charge_err_min"), float(0)))
                package.append(read.power_management(0x88, registers_pointer.get(0x08).get("charge_u_max"), float(0)))
                package.append(read.power_management(0x88, registers_pointer.get(0x08).get("charge_u_min"), float(0)))
                package.append(read.power_management(0x88, registers_pointer.get(0x08).get("charge_i_stable"), float(0)))
                package.append(read.power_management(0x88, registers_pointer.get(0x08).get("charge_u_stable"), float(0)))

                # через MODBUS
                ser = serial.Serial(self.com, self.braudrate, timeout=0.3)
                val = []
                for frame in package:
                    values = bytearray(read.write_modbus(frame))
                    ser.write(values)
                    response = ser.read(len(values))
                    if (len(response) == 0):
                        assert False
                    val.append(read.hexfloat_to_float(response[:len(response) - 2]))
                i = 0
                for key in device_values:
                    device_values[key] = val[i]
                    i = i + 1
                ser.close()
                self.device_values = device_values
                self.log.add("EEPROM", "Настройки электропитания получены", True)
                return True
            except:
                ser.close()
                self.log.log_data[len(self.log.log_data) - 1] = \
                    time_sec + " " + self.name + \
                    ": Попытка получить настройки электропитания " + str(t + 1) + " сек"
                time.sleep(1 - time.time() % 1)
                if t >= self.timeout - 1:
                    self.log.add(self.name, "Неудалось получить настройки электропитания", False)
                    return False
    # Получаем настройки электропитания
    def get_power_management(self):
        return self.device_values
    # включить ТЭН
    def sensor_on(self):
        time_sec = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        self.log.add(self.name,"Попытка включить ТЭН", True)
        for t in range(self.timeout):
            try:
                package = []
                write = FrameCollector()
                # считываем id датчика 1
                package.append(write.sensor_controls(0x0B, 0x01, 0xAA))
                package.append(write.sensor_controls(0x8A, 0x01, 0))
                # установить температуру, через функцию power_management (там реализован FLOAT32)
                package.append(write.power_management(0x09, 0x01, 50))
                # управление датчиками (режим ten или fan)
                package.append(write.sensor_controls(0x09, 0x03, "ten"))
                # включить все датчики
                package.append(write.sensor_controls(0x09, 0x02, 31))
                ser = serial.Serial(self.com,self.braudrate, timeout=0.2)
                for frame in package:
                    modb_frame = write.write_modbus(frame)
                    values = bytearray(modb_frame)
                    ser.write(values)
                    response = ser.read(len(values))
                    if (len(response) == 0):
                        assert False
                ser.close()
                self.log.add("EEPROM", "ТЭН включен", True)
                return True
            except:
                ser.close()
                self.log.log_data[len(self.log.log_data) - 1] = \
                    time_sec + " " + self.name + \
                    ": Попытка включить ТЭН " + str(t + 1) + " сек"
                time.sleep(1 - time.time() % 1)
                if t >= self.timeout - 1:
                    self.log.add(self.name, "Неудалось включить ТЭН", False)
                    return False
    # выключить ТЭН
    def sensor_off(self):
        time_sec = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        self.log.add(self.name,"Попытка отключить ТЭН", True)
        for t in range(self.timeout):
            try:
                package = []
                write = FrameCollector()
                # установить температуру, через функцию power_management (там реализован FLOAT32)
                package.append(write.power_management(0x09, 0x01, -20))
                # выключить все датчики
                package.append(write.sensor_controls(0x09, 0x02, 0))
                # linux port
                ser = serial.Serial(self.com, self.braudrate, timeout=0.3)

                for frame in package:
                    modb_frame = write.write_modbus(frame)
                    values = bytearray(modb_frame)
                    ser.write(values)
                    response = ser.read(len(values))
                    if (len(response) == 0):
                        assert False
                ser.close()
                self.log.add("EEPROM", "ТЭН отключен", True)
                return True
            except:
                ser.close()
                self.log.log_data[len(self.log.log_data) - 1] = \
                    time_sec + " " + self.name + \
                    ": Попытка включить ТЭН " + str(t + 1) + " сек"
                time.sleep(1 - time.time() % 1)
                if t >= self.timeout - 1:
                    self.log.add(self.name, "Неудалось включить ТЭН", False)
                    return False
    # прочитать серийный номер
    def read_serial_number(self):
        time_sec = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        self.log.add(self.name, "Попытка получить серийный номер", True)
        for t in range(self.timeout):
            try:
                package = []
                read = FrameCollector()
                package.append(read.serial_number(0xB3, 0))
                ser = serial.Serial(self.com, self.braudrate, timeout=0.3)
                val = 0
                for frame in package:
                    modb_frame = read.write_modbus(frame)
                    values = bytearray(modb_frame)
                    ser.write(values)
                    response = ser.read(len(values))
                    if (len(response) == 0):
                        assert False
                    val = read.hex_to_float(response[:len(response) - 2])
                ser.close()
                self.serial_number = 4710000000 + val
                if self.serial_number > 9000000000:
                    self.serial_number = 4710000000
                self.log.add(self.name, "Серийный номер устройства получен: " + str(self.serial_number), True)
                return True
            except:
                ser.close()
                self.log.log_data[len(self.log.log_data) - 1] = \
                    time_sec + " " + self.name + \
                    ": Попытка получить серийный номер " + str(t + 1) + " сек"
                time.sleep(1 - time.time() % 1)
                if t >= self.timeout - 1:
                    self.log.add(self.name, "Неудалось получить серийный номер", False)
                    return False
    # Получить серийный номер устройства
    def get_serial_number(self):
        return self.serial_number
    # записываем сетевые настройки
    def write_network_settings(self):
        time_sec = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        self.log.add(self.name, "Попытка записать сетевые настройки", True)
        f = open('eeprom.cfg', 'r')
        params = {}
        for line in f:
            temp = line.split(':')
            for t in temp:
                par_name = t.split("=")
                params.update({par_name[0]: par_name[1]})
        for t in range(self.timeout):
            try:
                package = []
                write = FrameCollector()
                # сетевые настройки
                package.append(write.network_settings(0x01, 0x01, int(params.get("InterfaceAdress"))))
                package.append(write.network_settings(0x01, 0x02, int(params.get("InterfaceSpeed"))))
                package.append(write.network_settings(0x01, 0x03, params.get("InterfaceChet")))
                package.append(write.network_settings(0x01, 0x04, params.get("ProtocolType")))

                # через MODBUS
                ser = serial.Serial(self.com, self.braudrate, timeout=0.3)
                for frame in package:
                    values = bytearray(write.write_modbus(frame))
                    ser.write(values)
                    response = ser.read(len(values))
                    if (len(response) == 0):
                        assert False

                ser.close()
                self.device_values = device_values
                self.log.add("EEPROM", "Сетевые настройки записаны", True)
                return True
            except:
                ser.close()
                self.log.log_data[len(self.log.log_data) - 1] = \
                    time_sec + " " + self.name + \
                    ": Попытка записать сетевые настройки " + str(t + 1) + " сек"
                time.sleep(1 - time.time() % 1)
                if t >= self.timeout - 1:
                    self.log.add(self.name, "Неудалось записать сетевые настройки", False)
                    return False
    # записываем уставки по току
    def write_max_current_value(self,current1, current2):
        time_sec = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        self.log.add(self.name, "Попытка записать уставки по току", True)
        f = open('eeprom.cfg', 'r')
        params = {}
        for line in f:
            temp = line.split(':')
            for t in temp:
                par_name = t.split("=")
                params.update({par_name[0]: par_name[1]})
        for t in range(self.timeout):
            try:
                package = []
                write = FrameCollector()
                # сетевые настройки
                # управление питанием outi
                package.append(write.power_management(register_names.get("outi"), registers_pointer.get(0x07).get("out_i_1"), current1))
                package.append(write.power_management(register_names.get("outi"), registers_pointer.get(0x07).get("out_i_2"), current2))

                # через MODBUS
                ser = serial.Serial(self.com, self.braudrate, timeout=0.3)
                for frame in package:
                    values = bytearray(write.write_modbus(frame))
                    ser.write(values)
                    response = ser.read(len(values))
                    if (len(response) == 0):
                        assert False

                ser.close()
                self.device_values = device_values
                self.log.add(self.name, "Уставки по току записаны", True)
                return True
            except:
                ser.close()
                self.log.log_data[len(self.log.log_data) - 1] = \
                    time_sec + " " + self.name + \
                    ": Попытка записать уставки по току " + str(t + 1) + " сек"
                time.sleep(1 - time.time() % 1)
                if t >= self.timeout - 1:
                    self.log.add(self.name, "Неудалось записать уставки по току", False)
                    return False

# получить версию прошивки!!!!!!!! ДОБАВИТЬ
# добавить обработку событий!
# if __name__ == '__main__':
#     log = engine.Log()
#     # создаем объект
#     eeprom = ReadWriteEEprom("EEPROM",log, "com45", 115200, 5)
#     print(eeprom.write_current_value())
    # print(eeprom.read_soft_version())
#     print(eeprom.get_soft_version())
#     print(eeprom.read_serial_number())
#     print(eeprom.get_serial_number())
    # print(eeprom.write_power_management())
    # print(eeprom.write_network_settings())
    # print(log.get_log())
    # print(eeprom.get_soft_version())
    # print()
    # eeprom.read_serial_number()
    # print(log.get_log())
    # print(eeprom.get_serial_number())

    # # Старый тест
    # # считываем и возвращаем версию ПО
    # print("Версия ПО: ", eeprom.read_soft_version())
    # # считываем серийный номер
    # print("Серийный номер: ",4710000000 + eeprom.read_serial_number())
    # # Считываем вкладку управление питанием
    # print(eeprom.read_power_management())
    # # # считываем id датчика и меняем параметры провоцируя работу ТЭНА
    # # eeprom.sensor_on()
    # # # Проверяем ТЭН и возвращаем уставки по умолчанию
    # # eeprom.sensor_off()

