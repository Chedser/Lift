$(document).ready(function(){

	$("#clear_btn").on("click", function() {

	$('#infoBlock').empty();

			$.ajax({
				url: 'handlers/clear_logs_h',             // указываем URL и
				dataType : "json",                     // тип загружаемых данных
				type: "POST",
				contentType: "application/json",
				success: function (data, textStatus) { // вешаем свой обработчик на функцию success

						if(data.code == 0){
						
							$('#logsBlock').empty();
							$('#logsBlock').text("Нет записей");
														
							$("#clear_btn").hide();
						
						}
							
					},
				fail: function (data, textStatus) { // вешаем свой обработчик на функцию success
						console.log("Fail");

					},
							
			});

	}); 

}) //$(document).ready