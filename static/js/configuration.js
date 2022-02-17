document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('#form').onsubmit = () => {
        var progressBar;
        progressBar = new ProgressBar("my-progressbar", {'width':'auto', 'height':'12px'});
        progressBar.setPercent(0);
        var request = new XMLHttpRequest();
//        var sumbit_type = document.querySelector('#save').value;
//        var device_type = document.querySelector('#device_type').value;
//        var device_name = document.querySelector(' #device_name').value;
        var soft_version = document.querySelector('#soft_version').value;
        var ip_adress = document.querySelector('#ip_adress').value;
        var port = document.querySelector('#port').value;
        var device_name = document.querySelector(".room-selector > #device_name").value;
        var power_supply_type = document.querySelector('.room-selector > #power_supply_type').value;
        var checked_list = document.querySelector('#checked_list').value;
        var control_com = document.querySelector('#control_com').value;
        var ammeter_com = document.querySelector('#ammeter_com').value;
        var device_com = document.querySelector('#device_com').value;


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
        data.append('soft_version', soft_version);
        data.append('ip_adress', ip_adress);
        data.append('port', port);
        data.append('control_com', control_com)
        data.append('ammeter_com', ammeter_com)
        data.append('device_com', device_com)
        data.append('device_name', device_name);
        data.append('power_supply_type', power_supply_type);
        data.append('checked_list', checked_list);
        request.send(data);
        return false;
    };

});