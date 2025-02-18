$(document).ready(function() {
    $('#registration-form').on('submit', function(e) {
        e.preventDefault();

        var username = $('#username').val();
        var email = $('#email').val();
        var password = $('#password').val();
        var password2 = $('#password2').val();

        if (password !== password2) {
            $('#error-message').text('Пароли не совпадают').show();
            return;
        }

        // Создаем объект для данных
        var data = {
            'username': username,
            'email': email,
            'password': password,
            'password2': password2
        };

        $.ajax({
            url: '/api/account/register/',  // Путь для API регистрации
            type: 'POST',
            contentType: 'application/json',  // Устанавливаем тип содержимого
            data: JSON.stringify(data),  // Сериализуем данные в формат JSON
            headers: {
                'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()  // Отправляем CSRF токен
            },
            success: function(response) {
                // Если регистрация успешна, перенаправляем на страницу подтверждения
                alert(response.message);  // Можно вывести сообщение из ответа
                window.location.href = '/account/email_confirmation/';  // Перенаправление
            },
            error: function(xhr) {
                // Показываем ошибку, если регистрация не удалась
                var errorMessage = xhr.responseJSON ? xhr.responseJSON.errors : 'An error occurred';
                $('#error-message').text(errorMessage).show();
            }
        });
    });
});
