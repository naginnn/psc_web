document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('#form').onsubmit = () => {
        var progressBar;
        progressBar = new ProgressBar("my-progressbar", {'width':'auto', 'height':'12px'});
        progressBar.setPercent(0);
        var request = new XMLHttpRequest();
//        var sumbit_type = document.querySelector('#save').value;
//        var device_type = document.querySelector('#device_type').value;
//        var device_name = document.querySelector(' #device_name').value;
        var device_name = document.querySelector(".room-selector > #device_name").value;
        var power_supply_type = document.querySelector('.room-selector > #power_supply_type').value;
        var checked_list = document.querySelector('#checked_list').value;
        var warmup_time = document.querySelector('#warmup_time').value;
        var overload_mode = document.querySelector('#overload_mode').checked;
        var om_to_enable = document.querySelector('#om_to_enable').checked;
        var om_ad_idle = document.querySelector('#om_ad_idle').checked;
        var om_under_load = document.querySelector('#om_under_load').checked;
        var sc_mode = document.querySelector('#sc_mode').checked;
        var sc_to_enable = document.querySelector('#sc_to_enable').checked;
        var sc_ad_idle = document.querySelector('#sc_ad_idle').checked;
        var sc_under_load = document.querySelector('#sc_under_load').checked;
        var voltage_thresholds = document.querySelector('#voltage_thresholds').checked;
        //Добавить максимальное и минимальное напряжение
        var min_voltage_in = document.querySelector('#min_voltage_in').value;
        var max_voltage_in = document.querySelector('#max_voltage_in').value;
        var min_voltage_btr = document.querySelector('#min_voltage_btr').value;
        var max_voltage_btr = document.querySelector('#max_voltage_btr').value;
        var switch_channel = document.querySelector('#switch_channel').checked;
        var dry_contact = document.querySelector('#dry_contact').checked;
        var sensor = document.querySelector('#sensor').checked;

        request.open('POST', '/configuration');

//        document.querySelector('#result').innerHTML = text;
        request.onload = () => {
            const data = JSON.parse(request.responseText);
            let  newElem = document.createElement( "div" ); // создаем новый элемент <button>
            const goodread = document.createTextNode("Конфигурация успешно записана!"); // создаем текстовое содержимое
            const badread = document.createTextNode("Ошибка записи!"); // создаем текстовое содержимое
            if (data.result) {
//                document.querySelector('#result').innerHTML = "Конфигурация успешно записана!";
	            newElem.appendChild(goodread); // добавляем текстовое содержимое элементу <button>
            } else {
                newElem.appendChild(badread);
            }
            document.body.appendChild( newElem );  // добавляем наш элемент в элемент <body>
            progressBar.setPercent(100);
      }
        const data = new FormData();
//        data.append('save', sumbit_type);
//        data.append('device_type', device_type);
        data.append('device_name', device_name);
        data.append('power_supply_type', power_supply_type);

        data.append('min_voltage_in', min_voltage_in);
        data.append('max_voltage_in', max_voltage_in);
        data.append('min_voltage_btr', min_voltage_btr);
        data.append('max_voltage_btr', max_voltage_btr);

        data.append('voltage_thresholds', voltage_thresholds);
        data.append('switch_channel', switch_channel);
        data.append('warmup_time', warmup_time);

        data.append('overload_mode', overload_mode);
        data.append('om_to_enable', om_to_enable);
        data.append('om_ad_idle', om_ad_idle);
        data.append('om_under_load', om_under_load);

        data.append('sc_mode', sc_mode);
        data.append('sc_to_enable', sc_to_enable);
        data.append('sc_ad_idle', sc_ad_idle);
        data.append('sc_under_load', sc_under_load);

        data.append('checked_list', checked_list);
        data.append('dry_contact', dry_contact);
        data.append('sensor', sensor);

//        data.append('test', test);
//        data.append('option1', option);
        request.send(data);
        return false;
    };

});










//      pace.start()

          // Инициализировать новый запрос

                // Обновите result div
//              if (data.success) {
//                  //const contents = `1 USD is equal to ${data.rate} ${currency}.`
//                  document.querySelector('#result').innerHTML = contents;
//              }
//              else {
//                  document.querySelector('#result').innerHTML = 'There was an error.';
//              }