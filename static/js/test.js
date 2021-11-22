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
        var sumbit_type = document.querySelector('#diagnostics').disabled = true; // отключаю кнопку по началу проверки
        var log = document.querySelector('#log').value = "";
        document.querySelector('#log').innerHTML = "Нажал!";

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
                          for (let i = 0; i < data.message.length; i++){
                            if (data.result[i])
//                                let div = document.createElement('div');
//                                div.className = "alert";
//                                div.innerHTML = "<strong>Всем привет!</strong> Вы прочитали важное сообщение.";
                                res = res  + "<div>"+ data.message[i] + "</div>";
                            else
                                res = res  + "<div style=\"color:red\">"+ data.message[i] + "</div>";
                            }
//                            res = res + data.result[i] + " <br /> ";}
                          document.querySelector('#log').innerHTML = res;
                            if (data.flag) {
//                                alert("Диагностика завершена!");
//                            delay *= 2;
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