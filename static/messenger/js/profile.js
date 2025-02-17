
document.addEventListener('DOMContentLoaded', function() {
    const profileContainer = document.getElementById('profile-container');
    const username = profileContainer.getAttribute('data-username');
    const profileInfo = document.getElementById('profile-info');

    fetch(`/api/profile/${username}/`)
        .then(response => response.json())
        .then(data => {
            profileInfo.innerHTML = `
                <p><strong>Имя пользователя:</strong> ${data.username}</p>
                <p><strong>Публичное имя:</strong> ${data.public_name}</p>
                <p><strong>Аватар:</strong> <img src="${data.avatar}" alt="Аватар" width="100"></p>
                <p><strong>Статус:</strong> ${data.status}</p>
                <p><strong>В контактах:</strong> ${data.is_contact ? 'Да' : 'Нет'}</p>
                ${data.is_chat ? `<p><strong>Чат:</strong> <a href="/chat/${data.chat_id}/">Перейти в чат</a></p>` : ''}
                ${data.last_chat_message_text ? `<p><strong>Последнее сообщение:</strong> ${data.last_chat_message_text}</p>` : ''}
                ${data.last_chat_message_time ? `<p><strong>Время последнего сообщения:</strong> ${new Date(data.last_chat_message_time).toLocaleString()}</p>` : ''}
            `;
        })
        .catch(error => {
            console.error('Ошибка при получении данных профиля:', error);
            profileInfo.innerHTML = '<p>Ошибка при загрузке данных профиля.</p>';
        });
});
