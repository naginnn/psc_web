var i = 1; // счетчик

function request(){
    $.ajax({
          url: 'test',
          type: 'post',
          success: function(){
          document.querySelector('#log').innerHTML = data.result;
          }});
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('#form').onsubmit = () => {
        var progressBar;
        progressBar = new ProgressBar("my-progressbar", {'width':'auto', 'height':'12px'});
        progressBar.initialMode(true);
        var request = new XMLHttpRequest();
        var sumbit_type = document.querySelector('#test').disabled = true; // отключаю кнопку по началу проверки
        var log = document.querySelector('#log').value = "";
        // document.querySelector('#log').innerHTML = "Нажал!";
        var doc = document;
        var device_type = document.getElementsByClassName('device_type');
        var quantity = document.getElementsByClassName('checked_dev');
        // var serial_number = document.getElementsByClassName('serial_number');
        var serial_number = document.getElementsByClassName('serial_number');

        var configuration = document.getElementsByClassName('configuration');
        var measurements = document.getElementsByClassName('measurements');
        var functional = document.getElementsByClassName('functional');
        var emergency = document.getElementsByClassName('emergency');

        // alert(checked);
        // alert(i);
        var color_flag = true;

        var standart_color = '#0000ff'
        // var device_color = new Array();
        // for (i = 0; i < 5; i++){
        //     colorArray[i].style.backgroundColor = standart_color;
        // }
        request.open('POST', '/test');
//        document.querySelector('#result').innerHTML = text;

        request.onload = () => {
            const data = JSON.parse(request.responseText);
//            let timerId = setInterval(() => loop(), 2000);
//            let timerId = setTimeout(function tick() { alert('tick'); timerId = setTimeout(tick, 2000); }, 2000);
            let delay = 400;
            let timerId = setTimeout(
                function lala() {
                    $.ajax({
                          url: 'test',
                          type: 'post',
                          success: function(data){
                          let res = '';
                          $(document).ready(function() {
                              $('#log').animate({
                                scrollTop: $('#log').get(0).scrollHeight
                            }, 200);
                                });




            if (data.check_stage == "serial_number") {
                quantity[parseInt(data.device_count)].style.backgroundColor = '#ced000';
                device_type[parseInt(data.device_count)].style.backgroundColor = '#ced000';
                serial_number[parseInt(data.device_count)].style.backgroundColor = '#ced000';
                configuration[parseInt(data.device_count)].style.backgroundColor = '#ced000';
                measurements[parseInt(data.device_count)].style.backgroundColor = '#ced000';
                functional[parseInt(data.device_count)].style.backgroundColor = '#ced000';
                emergency[parseInt(data.device_count)].style.backgroundColor = '#ced000';
                serial_number[parseInt(data.device_count)].innerHTML = "В работе";
            }

            if (data.check_stage == "serial_number_pass") {
                serial_number[parseInt(data.device_count)].innerHTML = data.serial_number;
                serial_number[parseInt(data.device_count)].style.backgroundColor = '#009e28';
            }
            if (data.check_stage == "serial_number_fail") {
                serial_number[parseInt(data.device_count)].innerHTML = "Не записан";
                serial_number[parseInt(data.device_count)].style.backgroundColor = '#c10005';
            }


            if (data.check_stage == "configuration")
                configuration[parseInt(data.device_count)].innerHTML = "В работе";
            if (data.check_stage == "configuration_pass") {
                configuration[parseInt(data.device_count)].innerHTML = "Соответствует";
                configuration[parseInt(data.device_count)].style.backgroundColor = '#009e28';
            }

            if (data.check_stage == "configuration_fail") {
                configuration[parseInt(data.device_count)].innerHTML = "Не соответствует";
                configuration[parseInt(data.device_count)].style.backgroundColor = '#c10005';
            }


            if (data.check_stage == "measurements")
                measurements[parseInt(data.device_count)].innerHTML = "В работе";
            if (data.check_stage == "measurements_pass") {
                measurements[parseInt(data.device_count)].innerHTML = "Соответствует";
                measurements[parseInt(data.device_count)].style.backgroundColor = '#009e28';
            }

            if (data.check_stage == "measurements_fail") {
                measurements[parseInt(data.device_count)].innerHTML = "Не соответствует";
                measurements[parseInt(data.device_count)].style.backgroundColor = '#c10005';
            }


            if (data.check_stage == "functional")
                functional[parseInt(data.device_count)].innerHTML = "В работе";
            if (data.check_stage == "functional_pass") {
                functional[parseInt(data.device_count)].innerHTML = "Соответствует";
                functional[parseInt(data.device_count)].style.backgroundColor = '#009e28';
            }

            if (data.check_stage == "functional_fail") {
                functional[parseInt(data.device_count)].innerHTML = "Не соответствует";
                functional[parseInt(data.device_count)].style.backgroundColor = '#c10005';
            }


            if (data.check_stage == "emergency")
                emergency[parseInt(data.device_count)].innerHTML = "В работе";
            if (data.check_stage == "emergency_pass") {
                emergency[parseInt(data.device_count)].innerHTML = "Соответствует";
                emergency[parseInt(data.device_count)].style.backgroundColor = '#009e28';
            }

            if (data.check_stage == "emergency_fail") {
                emergency[parseInt(data.device_count)].innerHTML = "Не соответствует";
                emergency[parseInt(data.device_count)].style.backgroundColor = '#c10005';
            }

           //  if (!data.device_finish){
           //      if (color_flag) {
           //        quantity[parseInt(data.device_count)].style.backgroundColor = '#76ff00';
           //        color_flag = false;
           //      } else {
           //        quantity[parseInt(data.device_count)].style.backgroundColor = '#ff0000';
           //        color_flag = true;
           //
           //      }
           //  } else {
           //
           //      if (data.device_status) {
           //          quantity[parseInt(data.device_count)].style.backgroundColor = '#76ff00';
           //
           //      }
           //      else {
           //          quantity[parseInt(data.device_count)].style.backgroundColor = '#ff0000';
           //
           //      }
           //
           // }
                              // обновление лога
                          for (let i = 0; i < data.message.length; i++){
                            if (data.result[i])
                                res = res  + "<div>"+ data.message[i] + "</div>";
                            else
                                res = res  + "<div style=\"color:red\">"+ data.message[i] + "</div>";
                            }
                              // выводим результат
                          document.querySelector('#log').innerHTML = res;

                          // если флаг True прекратить опрос backend'a
                            if (data.flag) {
                                clearTimeout(lala);
                                document.querySelector('#test').disabled = false;
                                progressBar.initialMode(false);
//                            return null;
                        } else{timerId = setTimeout(lala, delay);}
                          }});


                    }, delay);

//            document.querySelector('#diagnostics').disabled = false;


//            function fetchdata(flag){
//                 $.ajax({
//                  url: '/diagnostics',
//                  type: 'post',
//                  success:
//                  function(data, flag){
//                    if (data.js_loop == true) {
//                        let res = '';
//                    for (let i = 0; i < data.result.length; i++)
//                        res = res + data.result[i] + " <br /> ";
//                    document.querySelector('#log').innerHTML = res;
//                    } else {
//                       flag = false;
//                        document.querySelector('#diagnostics').disabled = false;
//                        return null;
//                    }
//                    }
////                    },
////
////                  complete:function(data, flag){
////                                    setInterval(fetchdata,500);
////                                }
//                  });
//            };
      }

        const data = new FormData();
        data.append('log', log);
        request.send(data);
        return false;
    };

});


          // включаю кнопку по окончанию проверки
//          document.querySelector('#log').innerHTML = document.querySelector('#log').innerHTML + data.result;
           // Perform operation on return value
//           let  newElem = document.createElement( "div" ); // создаем новый элемент <button>
//	       const text = document.createTextNode(data.result); // создаем текстовое содержимое
//	       newElem.appendChild( text ); // добавляем текстовое содержимое элементу <button>
//	       document.body.appendChild( newElem );  // добавляем наш элемент в элемент <body>