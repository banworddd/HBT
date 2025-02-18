$(document).ready(function() {
    $('#login-form').on('submit', function(e) {
        e.preventDefault();

        var username = $('#username').val();
        var password = $('#password').val();

        $.ajax({
            url: '/api/account/login/',
            type: 'POST',
            data: {
                'username': username,
                'password': password,
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            },
            success: function(response) {
                window.location.href = '/chats/';
            },
            error: function(xhr) {
                var errorMessage = xhr.responseJSON ? xhr.responseJSON.detail : 'An error occurred';
                $('#error-message').text(errorMessage).show();
            }
        });
    });
});
