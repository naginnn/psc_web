# importing flask module fro
import os
from threading import Thread

from flask import Flask, render_template, request, jsonify
from flask import send_from_directory
import engine

settings = engine.Settings()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'protocols'
log = engine.Log()
main_log = engine.Log()
#метод диагностики стенда
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
        return jsonify({"message": log.get_log_data(),"result":log.get_log_result(), "flag": log.get_finish()})

    if request.method == 'GET':
        return render_template('diagnostics.html')

@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        if main_log.get_start():
            Thread(target=test_worker).start()
        if main_log.get_finish():
            main_log.set_start(True)
        return jsonify({"message": main_log.get_log_data(), "result": main_log.get_log_result(), "flag": main_log.get_finish()})

    if request.method == 'GET':
        data = settings.load("settings.cfg")
        print(data)
        devices = ""
        stages = []
        i = 1
        while i <= int(data.get('checked_list')):
            devices = devices + str(i)
            i = i + 1

        if (data.get('sensor') != "false"):
            stages.append("Обрыв связи с датчиком")
        if (data.get('dry_contact') != "false"):
            stages.append("Сухой контакт (ТЭН)")
        if (data.get('voltage_thresholds') != "false"):
            stages.append("Пороги по напряжению")
        if (data.get('switch_channel') != "false"):
            stages.append("Пeреключение каналов")
        if (data.get('sc_mode') != "false"):
            stages.append("Режим КЗ")
        if (data.get('overload_mode') != "false"):
            stages.append("Режим ПЕРЕГРУЗКИ")

        return render_template('test.html',devices = devices, stages = stages)

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
        device_name = request.form.get('device_name')
        power_supply_type = request.form.get('power_supply_type')

        voltage_thresholds = request.form.get('voltage_thresholds')
        switch_channel = request.form.get('switch_channel')
        warmup_time = request.form.get('warmup_time')

        min_voltage_in = request.form.get('min_voltage_in')
        max_voltage_in = request.form.get('max_voltage_in')
        min_voltage_btr = request.form.get('min_voltage_btr')
        max_voltage_btr = request.form.get('max_voltage_btr')

        overload_mode = request.form.get('overload_mode')
        om_to_enable = request.form.get('om_to_enable')
        om_ad_idle = request.form.get('om_ad_idle')
        om_under_load = request.form.get('om_under_load')

        sc_mode = request.form.get('sc_mode')
        sc_to_enable = request.form.get('sc_to_enable')
        sc_ad_idle = request.form.get('sc_ad_idle')
        sc_under_load = request.form.get('sc_under_load')

        checked_list = request.form.get('checked_list')
        dry_contact = request.form.get('dry_contact')
        sensor = request.form.get('sensor')

        data.update({"device_name":device_name,"power_supply_type":power_supply_type,"checked_list":checked_list,"warmup_time":warmup_time,
                     "overload_mode":overload_mode,"om_to_enable":om_to_enable,"om_ad_idle":om_ad_idle,"om_under_load":om_under_load,
                     "sc_mode":sc_mode,"sc_to_enable":sc_to_enable,"sc_ad_idle":sc_ad_idle,"sc_under_load":sc_under_load,"voltage_thresholds":voltage_thresholds,
                     "min_voltage_in":min_voltage_in,"max_voltage_in":max_voltage_in,"min_voltage_btr":min_voltage_btr,"max_voltage_btr":max_voltage_btr,"switch_channel":switch_channel,
                     "dry_contact":dry_contact,"sensor":sensor})
        result = settings.save("settings.cfg",data)
        #зДЕСЬ ТО ЧТО Я МОГУ ИСПОЛЬЗОВАТЬ В js
        return jsonify({"result": result})

    if request.method == 'GET':
        psc24_10 = "0"
        psc24_40 = "0"
        psc48_10 = "0"
        psc48_40 = "0"

        wm24_10 = "0"
        pw24_5 = "0"
        wm24_40 = "0"
        mw24_67 = "0"
        wm48_20 = "0"
        mw48_67 = "0"

        checked_1 = ""
        checked_2 = ""
        checked_3 = ""
        checked_4 = ""
        checked_5 = ""
        warmup_1 = ""
        warmup_5 = ""
        warmup_10 = ""
        warmup_15 = ""
        warmup_20 = ""
        overload_mode = ""
        om_to_enable = ""
        om_ad_idle = ""
        om_under_load = ""
        sc_mode = ""
        sc_to_enable = ""
        sc_ad_idle = ""
        sc_under_load = ""
        voltage_thresholds = ""
        min_voltage_in = ""
        min_voltage_in_ch = ""
        min_voltage_btr = ""
        min_voltage_btr_ch = ""
        max_voltage_in = ""
        max_voltage_in_ch = ""
        max_voltage_btr = ""
        max_voltage_btr_ch = ""
        switch_channel = ""
        dry_contact = ""
        sensor = ""
        # время прогрева сделать простым параметром
        data = settings.load("settings.cfg")
        print(data)
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

        if (data.get('warmup_time') == '1'):
            warmup_1 = "selected"
        elif (data.get('warmup_time') == '5'):
            warmup_5 = "selected"
        elif (data.get('warmup_time') == '10'):
            warmup_10 = "selected"
        elif (data.get('warmup_time') == '15'):
            warmup_15 = "selected"
        elif (data.get('warmup_time') == '20'):
            warmup_20 = "selected"

        if (data.get('overload_mode') == 'true'):
            overload_mode = "checked"
            if (data.get('om_to_enable') == 'true'):
                om_to_enable = "checked"
            if (data.get('om_ad_idle') == 'true'):
                om_ad_idle = "checked"
            if (data.get('om_under_load') == 'true'):
                om_under_load = "checked"
        else:
            om_to_enable = "disabled"
            om_ad_idle = "disabled"
            om_under_load = "disabled"

        if (data.get('sc_mode') == 'true'):
            sc_mode = "checked"
            if (data.get('sc_to_enable') == 'true'):
                sc_to_enable = "checked"
            if (data.get('sc_ad_idle') == 'true'):
                sc_ad_idle = "checked"
            if (data.get('sc_under_load') == 'true'):
                sc_under_load = "checked"
        else:
            sc_to_enable = "disabled"
            sc_ad_idle = "disabled"
            sc_under_load = "disabled"

        if (data.get('voltage_thresholds') == 'true'):
            voltage_thresholds = "checked"
            min_voltage_in = data.get('min_voltage_in')
            min_voltage_btr = data.get('min_voltage_btr')
            max_voltage_in = data.get('max_voltage_in')
            max_voltage_btr = data.get('max_voltage_btr')
        else:
            min_voltage_in = data.get('min_voltage_in')
            min_voltage_btr = data.get('min_voltage_btr')
            max_voltage_in = data.get('max_voltage_in')
            max_voltage_btr = data.get('max_voltage_btr')
            min_voltage_in_ch = "disabled"
            min_voltage_btr_ch = "disabled"
            max_voltage_in_ch = "disabled"
            max_voltage_btr_ch = "disabled"

        if (data.get('switch_channel') == 'true'):
            switch_channel = "checked"
        if (data.get('dry_contact') == 'true'):
            dry_contact = "checked"
        if (data.get('sensor') == 'true'):
            sensor = "checked"


        return render_template('configuration.html', psc24_10 = psc24_10, psc24_40 = psc24_40, psc48_10 = psc48_10, psc48_40 = psc48_40, wm24_10 = wm24_10, pw24_5 = pw24_5,
            wm24_40 = wm24_40, mw24_67 = mw24_67, wm48_20 = wm48_20, mw48_67 = mw48_67,
            checked_1 = checked_1, checked_2 = checked_2, checked_3 = checked_3, checked_4 = checked_4,checked_5 = checked_5,
            overload_mode = overload_mode,om_to_enable = om_to_enable, om_ad_idle = om_ad_idle, om_under_load = om_under_load,
            sc_mode = sc_mode, sc_to_enable = sc_to_enable, sc_ad_idle = sc_ad_idle, sc_under_load = sc_under_load, voltage_thresholds = voltage_thresholds,
            min_voltage_in_ch = min_voltage_in_ch, min_voltage_btr_ch = min_voltage_btr_ch, max_voltage_in_ch = max_voltage_in_ch, max_voltage_btr_ch = max_voltage_btr_ch,
            min_voltage_in = min_voltage_in, min_voltage_btr = min_voltage_btr, max_voltage_in = max_voltage_in, max_voltage_btr = max_voltage_btr,
            switch_channel = switch_channel, dry_contact = dry_contact, sensor = sensor, warmup_1 = warmup_1, warmup_5 = warmup_5, warmup_10 = warmup_10,
            warmup_15 = warmup_15, warmup_20 = warmup_20)

if __name__ == "__main__":
   app.run(debug=True)