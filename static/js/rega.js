
$(document).ready(function(){

	$("#send_btn").on("click", function() {

	$('#infoBlock').empty();

	let loginVal = $("#login").val().trim();
	let passVal = $("#pass").val().trim();
	let passRepeatVal = $("#pass_repeat").val().trim();

		if(loginVal== "" ||
			passVal == "" || 
			passRepeatVal == ""){
		
			$('#infoBlock').append("<span>Пусто</span><br />");
			return;
		
		}
			
		if(passVal !== passRepeatVal){
			$('#infoBlock').append("<span>Пароли должны быть равны</span><br />");
			return;
		
		}
		
			$('#infoBlock').empty();
		    $(this).attr("disabled", "disabled"); 

	let dataToSend = {
					login: loginVal,
					pass: passVal,
					pass_repeat: passRepeatVal};

			$.ajax({
				url: 'handlers/rega_h',             // указываем URL и
				dataType : "json",                     // тип загружаемых данных
				data: JSON.stringify(dataToSend),                // Данные для отправки
				type: "POST",
				contentType: "application/json",
				success: function (data, textStatus) { // вешаем свой обработчик на функцию success
						if(data.errors.length == 0){// Все нормально
							$("#login").val("");
							$("#pass").val("");
							$("#pass_repeat").val("");
							window.location.replace("/auth");
						}else{
						
							if(data.errors.indexOf(1) != -1){ // Пустые поля
							
								$('#infoBlock').append("<span>Пусто</span><br />");
															
							}
							
							if(data.errors.indexOf(2) != -1){
							
								$('#infoBlock').append("<span>Пользователь уже есть</span><br />");
							
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
