document.addEventListener('DOMContentLoaded', function() {
    const profileContainer = document.getElementById('profile-container');
    const username = profileContainer.getAttribute('data-username');
    const profileInfo = document.getElementById('profile-info');

    // Показать индикатор загрузки
    profileInfo.innerHTML = '<p>Загрузка данных...</p>';

    fetch(`/api/profile/${username}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка сети или сервер вернул ошибку');
            }
            return response.json();
        })
        .then(data => {
            const currentUserId = profileContainer.getAttribute('data-current-user-id'); // Получаем ID текущего пользователя
            let contactButton;
            if (data.is_contact) {
                contactButton = `<button onclick="removeContact('${currentUserId}', '${username}')">Удалить из контактов</button>`;
            } else {
                contactButton = `<button onclick="addContact('${currentUserId}', '${username}')">Добавить в контакты</button>`;
            }

            profileInfo.innerHTML = `
                <p><strong>Имя пользователя:</strong> ${data.username}</p>
                <p><strong>Публичное имя:</strong> ${data.public_name}</p>
                <p><strong>Аватар:</strong> <img src="${data.avatar}" alt="Аватар" width="100"></p>
                <p><strong>Статус:</strong> ${data.status}</p>
                <p><strong>В контактах:</strong> ${data.is_contact ? 'Да' : 'Нет'}</p>
                ${contactButton}
                ${data.is_chat ? `<p><strong>Чат:</strong> <a href="/chat/${data.chat_id}/">Перейти в чат</a></p>` : ''}
                ${data.last_chat_message_text ? `<p><strong>Последнее сообщение:</strong> ${data.last_chat_message_text}</p>` : ''}
                ${data.last_chat_message_time ? `<p><strong>Время последнего сообщения:</strong> ${new Date(data.last_chat_message_time).toLocaleString()}</p>` : ''}
            `;
        })
        .catch(error => {
            console.error('Ошибка при получении данных профиля:', error);
            profileInfo.innerHTML = '<p>Ошибка при загрузке данных профиля. Пожалуйста, попробуйте позже.</p>';
        });
});

function addContact(currentUserId, username) {
    if (confirm('Вы уверены, что хотите добавить этого пользователя в контакты?')) {
        fetch(`/api/contacts_update/${currentUserId}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ contacts: username })
        })
        .then(response => response.json())
        .then(data => {
            location.reload(); // Перезагрузить страницу для обновления информации
        })
        .catch(error => {
            console.error('Ошибка при добавлении контакта:', error);
        });
    }
}

function removeContact(currentUserId, username) {
    if (confirm('Вы уверены, что хотите удалить этого пользователя из контактов?')) {
        fetch(`/api/contacts_update/${currentUserId}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ contacts: username })
        })
        .then(response => response.json())
        .then(data => {
            location.reload(); // Перезагрузить страницу для обновления информации
        })
        .catch(error => {
            console.error('Ошибка при удалении контакта:', error);
        });
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && name) {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
