$(document).ready(function(){

	$("#send_btn").on("click", function() {

	let loginVal = $("#login").val().trim();
	let passVal = $("#pass").val().trim();
	
	$('#infoBlock').empty();

		if(loginVal== "" ||
			passVal == ""){
		
			$('#infoBlock').append("<span>Пусто</span><br />");
			return;
		
		}
		
	$(this).attr("disabled", "disabled"); 

	$('#infoBlock').empty();

	let dataToSend = {
					login: loginVal,
					pass: passVal};

			$.ajax({
				url: 'handlers/auth_h',             // указываем URL и
				dataType : "json",                     // тип загружаемых данных
				data: JSON.stringify(dataToSend),                // Данные для отправки
				type: "POST",
				contentType: "application/json",
				success: function (data, textStatus) { // вешаем свой обработчик на функцию success
						if(data.errors.length == 0){
							let date = new Date(Date.now() + 86400e3);
							date = date.toUTCString();
							document.cookie = "user=" + data.login + "; expires=" + date;
							$("#login").val("");
							$("#pass").val("");
							window.location.replace("/");
						} else{
						
						if(data.errors.indexOf(1) != -1){ // Пустые поля
							
								$('#infoBlock').append("<span>Пусто</span><br />");
															
							}
							
							if(data.errors.indexOf(2) != -1){
							
								$('#infoBlock').append("<span>Неверные данные</span><br />");
							
							}
							
							if(data.errors.indexOf(3) != -1){
							
								$('#infoBlock').append("<span>Ошибка</span><br />");
							
							}
											
						}
						
						$("#send_btn").removeAttr("disabled");
						
					},
				fail: function (data, textStatus) { // вешаем свой обработчик на функцию success
						console.log("Fail");
						$("#send_btn").removeAttr("disabled");
					},
							
			});

	}); 

}) //$(document).ready
