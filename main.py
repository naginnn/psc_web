# importing flask module fro
import os
from threading import Thread

from flask import Flask, render_template, request, jsonify
from flask import send_from_directory
import engine

settings = engine.Settings()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'protocols'
# лог диагностики
log = engine.Log()
# лог для управления
control_log = engine.Log()
# лог проверки
main_log = engine.Log()

#метод диагностики стенда#
def diag_worker():
    print("Начало потока")
    log.set_finish(False)
    while True:
        print("ЕДЕМ!")
        log.log_clear_data()
        log.log_clear_result()
        diagnostics = engine.Diagnostics("Диагностика", log)
        diagnostics.diagnostics("ON")
        # lock.acquire()
        if log.get_finish() is True:
            break
        # lock.release()
        # sleep(2)
    print("Стоп ")

# Изменить для тестирования!
def test_worker():
    print("Начало теста")
    control_log.set_finish(False)
    while True:
        print("ТЕСТ!")
        # control_log.log_clear_data()
        # control_log.log_clear_result()
        control_log.reset_log()
        main_log.reset_log()
        psc_test = engine.Check_psc24_10("Тестирование", control_log, main_log, settings)
        psc_test.main1()
        # lock.acquire()
        if control_log.get_finish() is True:
            break
        # lock.release()
        # sleep(2)
    print("Стоп ")

@app.route('/', methods=['GET', 'POST'])
def welcome():
    dir = os.getcwd() + "/protocols"
    list = os.listdir(dir);
    return render_template('welcome.html', lala = list)

@app.route('/protocols/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    print(app.root_path)
    full_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    print(full_path)
    return send_from_directory(full_path, filename, as_attachment=True)

@app.route('/diagnostics', methods=['GET', 'POST'])
def diagnostics():
    if request.method == 'POST':
        if log.get_start():
            Thread(target=diag_worker).start()
        if log.get_finish():
            log.set_start(True)
        return jsonify({"message": log.get_log_data(), "result":log.get_log_result(), "flag": log.get_finish()})
    if request.method == 'GET':
        return render_template('diagnostics.html')
#ddd
@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        if control_log.get_start():
            Thread(target=test_worker).start()
        if control_log.get_finish():
            control_log.set_start(True)
            # добавить сюда номер проверяемого устройства
        return jsonify({"message": control_log.get_log_data(), "result": control_log.get_log_result(), "flag": control_log.get_finish(),
                        "device_count": main_log.get_device_count(), "device_status": main_log.get_start(), "device_finish": main_log.get_finish()})

    if request.method == 'GET':
        data = settings.load("settings.cfg")
        print(data)
        devices = ""
        stages = []
        i = 1
        while i <= int(data.get('checked_list')):
            devices = devices + str(i)
            i = i + 1

        return render_template('test.html', devices = devices, stages = stages)

@app.route('/instruction')
def instruction():
   return render_template('instruction.html')

@app.route('/shemeilogic')
def shemeilogic():
   return render_template('shemeilogic.html')

@app.route('/configuration', methods=['GET', 'POST'])
def configuration():
    data = {}
    if request.method == 'POST':
        soft_version = request.form.get('soft_version')
        ip_adress = request.form.get('ip_adress')
        port = request.form.get('port')
        control_com = request.form.get('control_com')
        ammeter_com = request.form.get('ammeter_com')
        device_com = request.form.get('device_com')
        device_name = request.form.get('device_name')
        power_supply_type = request.form.get('power_supply_type')
        checked_list = request.form.get('checked_list')
        data.update({"soft_version":soft_version, "ip_adress":ip_adress, "port":port, "device_name":device_name, "power_supply_type":power_supply_type,
                     "checked_list":checked_list, "control_com":control_com, "ammeter_com":ammeter_com, "device_com":device_com})
        result = settings.save("settings.cfg",data)
        #зДЕСЬ ТО ЧТО Я МОГУ ИСПОЛЬЗОВАТЬ В js
        return jsonify({"result": result})

    if request.method == 'GET':
        soft_version = "0"
        ip_adress = "0"
        port = "0"

        control_com = "0"
        ammeter_com = "0"
        device_com = "0"

        psc24_10 = "0"
        psc24_40 = "0"
        psc48_10 = "0"
        psc48_40 = "0"

        wm24_10 = "WeidMuller 24V 10A"
        pw24_5 = "Topaz PW 24V 5A"
        wm24_40 = "WeidMuller 24V 40A"
        mw24_67 = "MeanWell 24V 67A"
        wm48_20 = "WeidMuller 48V 20A"
        mw48_67 = "MeanWell 48V 67A"

        checked_1 = ""
        checked_2 = ""
        checked_3 = ""
        checked_4 = ""
        checked_5 = ""
        # время прогрева сделать простым параметром
        data = settings.load("settings.cfg")
        print(data)

        soft_version = data.get('soft_version')
        ip_adress = data.get('ip_adress')
        port = data.get('port')

        control_com = data.get('control_com')
        ammeter_com = data.get('ammeter_com')
        device_com = data.get('device_com')


        if (data.get('device_name') == 'psc24_10'):
            psc24_10 = "selected"
        elif (data.get('device_name') == 'psc24_40'):
            psc24_40 = "selected"
        elif (data.get('device_name') == 'psc48_10'):
            psc48_10 = "selected"
        elif (data.get('device_name') == 'psc48_40'):
            psc48_40 = "selected"

        if (data.get('power_supply_type') == 'wm24_10'):
            wm24_10 = "selected"
        elif (data.get('power_supply_type') == 'pw24_5'):
            pw24_5 = "selected"
        elif (data.get('power_supply_type') == 'wm24_40'):
            wm24_40 = "selected"
        elif (data.get('power_supply_type') == 'mw24_67'):
            mw24_67 = "selected"
        elif (data.get('power_supply_type') == 'wm48_20'):
            wm48_20 = "selected"
        elif (data.get('power_supply_type') == 'mw48_67'):
            mw48_67 = "selected"

        if (data.get('checked_list') == '1'):
            checked_1 = "selected"
        elif (data.get('checked_list') == '2'):
            checked_2 = "selected"
        elif (data.get('checked_list') == '3'):
            checked_3 = "selected"
        elif (data.get('checked_list') == '4'):
            checked_4 = "selected"
        elif (data.get('checked_list') == '5'):
            checked_5 = "selected"
        return render_template('configuration.html',soft_version = soft_version, ip_adress = ip_adress, port = port,
                               control_com = control_com, ammeter_com = ammeter_com, device_com = device_com, psc24_10 = psc24_10, psc24_40 = psc24_40,
                               psc48_10 = psc48_10, psc48_40 = psc48_40, wm24_10 = wm24_10, pw24_5 = pw24_5, wm24_40 = wm24_40, mw24_67 = mw24_67, wm48_20 = wm48_20,
                               mw48_67 = mw48_67, checked_1 = checked_1, checked_2 = checked_2, checked_3 = checked_3, checked_4 = checked_4,checked_5 = checked_5)

if __name__ == "__main__":
   app.run(debug=True)