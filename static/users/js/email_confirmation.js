$(document).ready(function() {
    $('#confirmation-form').on('submit', function(e) {
        e.preventDefault();

        var confirmation_code = $('#confirmation_code').val();

        $.ajax({
            url: '/api/account/confirm_email/',  // Путь для API подтверждения почты
            type: 'POST',
            data: {
                'confirmation_code': confirmation_code,
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            },
            success: function(response) {
                // Если подтверждение успешное, перенаправляем на страницу чатов
                window.location.href = '/chats/';
            },
            error: function(xhr) {
                // Показываем ошибку, если код неверный
                var errorMessage = xhr.responseJSON ? xhr.responseJSON.error : 'Неправильный код подтверждения';
                $('#error-message').text(errorMessage).show();
            }
        });
    });
});