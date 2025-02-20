document.addEventListener('DOMContentLoaded', function () {
    const chatsList = document.getElementById('chat-items');
    const searchInput = document.getElementById('search-input');
    const username = document.getElementById('chats-list').dataset.username;

    // Функция для загрузки чатов
    async function loadChats() {
        try {
            const response = await fetch(`/api/messenger/chats/?user=${username}`);
            if (!response.ok) {
                throw new Error('Ошибка при загрузке чатов');
            }
            const chats = await response.json();
            renderChats(chats);
        } catch (error) {
            console.error('Ошибка:', error);
        }
    }

    // Функция для поиска пользователей
    async function searchUsers(query) {
        try {
            const response = await fetch(`/api/messenger/users_search/?user=${query}`);
            if (!response.ok) {
                throw new Error('Ошибка при поиске пользователей');
            }
            const users = await response.json();
            renderSearchResults(users);
        } catch (error) {
            console.error('Ошибка:', error);
        }
    }

// Функция для отображения чатов
function renderChats(chats) {
    chatsList.innerHTML = ''; // Очищаем список перед добавлением новых элементов
    chats.forEach(chat => {
        const chatItem = document.createElement('li');
        chatItem.className = 'chat-item';

        // Определяем название чата
        let chatName = chat.is_group ? chat.name || 'Групповой чат' : chat.public_name2; // Используем public_name2 для личных чатов

        // Определяем последнее сообщение
        const lastMessage = chat.last_message_text ?
            `${chat.last_message_text} ${new Date(chat.last_message_time).toLocaleString()}` :
            'Нет сообщений';

        // Аватарка чата
        const chatAvatar = chat.chat_avatar ? `<div class="chat-avatar"><img src="${chat.chat_avatar}" alt="${chatName}"></div>` : '';

        // Создаем HTML для элемента чата
        chatItem.innerHTML = `
            ${chatAvatar}
            <div class="chat-info">
                <h3>${chatName}</h3>
                ${!chat.is_group ? `<p class="username">${chat.username2}</p>` : ''}
                <p class="last-message">${lastMessage}</p>
            </div>
        `;

        // Добавляем обработчик клика для перехода к чату
        chatItem.addEventListener('click', () => {
            window.location.href = `/chat/${chat.id}/`; // Замени на свой URL для чата
        });

        chatsList.appendChild(chatItem);
    });
}

// Функция для отображения результатов поиска
function renderSearchResults(users) {
    chatsList.innerHTML = ''; // Очищаем список перед добавлением новых элементов
    users.forEach(user => {
        const userItem = document.createElement('li');
        userItem.className = 'chat-item';

        // Определяем название чата
        const chatName = user.public_name || user.username || 'Личный чат';

        // Определяем последнее сообщение (если есть)
        const lastMessage = user.last_chat_message_text ?
            `${user.last_chat_message_text} ${new Date(user.last_chat_message_time).toLocaleString()}` :
            'Нет сообщений';

        // Аватарка пользователя
        const userAvatar = user.avatar ? `<div class="chat-avatar"><img src="${user.avatar}" alt="${user.username}"></div>` : '';

        // Создаем HTML для элемента пользователя
        userItem.innerHTML = `
            ${userAvatar}
            <div class="chat-info">
                <h3>${chatName}</h3>
                <p class="username">${user.username}</p> <!-- Добавляем username -->
                <p class="last-message">${lastMessage}</p>
            </div>
        `;

        // Добавляем обработчик клика для перехода к чату
        userItem.addEventListener('click', () => {
            if (user.chat_id) {
                window.location.href = `/chat/${user.chat_id}/`; // Переход к существующему чату
            } else {
                // Создать новый чат (если нужно)
                console.log('Создать новый чат с пользователем:', user.username);
            }
        });
        chatsList.appendChild(userItem);
    });
}

    // Обработчик ввода в поле поиска
    searchInput.addEventListener('input', function (event) {
        const query = event.target.value.trim();
        if (query.length > 0) {
            searchUsers(query); // Поиск пользователей
        } else {
            loadChats(); // Загрузка чатов, если поле поиска пустое
        }
    });

    // Загружаем чаты при загрузке страницы
    loadChats();
});