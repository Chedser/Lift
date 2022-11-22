$(document).ready(function(){

  var floor_dest = 7;
 
  var socket = io();
 
/* СОБЫТИЯ СОКЕТА */
 socket.on('connect', function() {

				$('#infoBlock').append("<span>Успешное подключение к сокету</span><br />");
			
			});

 socket.on('other_client_connect', function(msg) {
			
			$('#current_floor').text(msg.floor_current);
			$('#infoBlock').append("<span>" + msg.client + " подключился</span><br />");
			
			});

 socket.on('disconnect', function(msg) {
			
		$('#infoBlock').append("<span>Разрыв соединения</span><br />");
				  
    });
	
	
socket.on('other_client_disconnect', function(msg) { 

			$('#current_floor').text(msg.floor_current);
			$('#infoBlock').append("<span>" + msg.client + " отключился</span><br />");
			
			
		
    });
 
 socket.on('response', function(msg) {
			
			switch (msg.errno){
			
				case 0: $('#infoBlock').append("<span>" + msg.client.login + " подключен. " + "Этаж назначения: " + msg.client.floor_dest + "</span><br />"); break;
				case 1: $('#errorTxt').text("Ошибка подключения"); break;
				case 3: $('#errorTxt').text("Этаж уже есть в списке назначения. Ожидайте"); break;
			
			}
			 			  
    });
	
socket.on('lift_response', function(msg) { // Получаем данные от сокета
		
					
		$('#current_floor').text(msg.floor_current);
		
		switch (msg.code){
		
			case 0: $('#infoBlock').append("<span>Лифт ожидает</span><br />");break;
			case 1: $('#infoBlock').append("<span>Лифт остановлен</span><br />"); break;
			case 2: $('#infoBlock').append("<span>Лифт на этаже № " + msg.floor_current + "</span><br />"); break;
		
		}

					  
    });


/* СОБЫТИЯ НАЖАТИЙ ПОЛЬЗОВАТЕЛЯ */

$("#select_floor_dest").on("change", function() {

	floor_dest = this.querySelectorAll('option')[this.selectedIndex].getAttribute('value');

});

$("#send_btn").on("click", function() { // Посылаем данные в сокет

$('#errorTxt').text("");
	floor_dest = parseInt(floor_dest);
	
	 let data = {login:"{{login}}",
				floor_dest:floor_dest
				};
	
	console.log(floor_dest)
	
	socket.emit('request', data);

});

$("#unloginA").on("click", function() { // Разлогинимся

	document.cookie = "user={{login}}" + ";expires=Thu, 01 Jan 1970 00:00:01 GMT";
	window.location.replace("/auth");

}) 

}) // $(document).ready
