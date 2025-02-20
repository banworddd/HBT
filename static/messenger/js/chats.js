document.addEventListener('DOMContentLoaded', function () {
    const chatsList = document.getElementById('chat-items');
    const searchInput = document.getElementById('search-input');
    const username = document.getElementById('chats-list').dataset.username;
    const chatHeader = document.getElementById('chat-header');
    const messageList = document.getElementById('message-list');
    const messageForm = document.getElementById('message-form');
    const messageText = document.getElementById('message-text');
    const chatInformation = document.getElementById('chat-information');
    let currentChatId = null;
    let nextMessagesUrl = null; // Для отслеживания следующей страницы сообщений
    let previousMessagesUrl = null; // Для отслеживания предыдущей страницы сообщений

    // Функция для получения параметров из URL
    function getChatIdFromUrl() {
        const params = new URLSearchParams(window.location.search);
        return params.get('chat_id');
    }

    // После загрузки страницы проверяем наличие chat_id в URL
    const chatId = getChatIdFromUrl();
    if (chatId) {
        loadChatInfo(chatId); // Автоматически загружаем указанный чат
    }

    // Функция для загрузки чатов
    async function loadChats() {
        try {
            const response = await fetch(`/api/messenger/chats/?user=${username}`);
            if (!response.ok) {
                throw new Error('Ошибка при загрузке чатов');
            }
            const chats = await response.json();
            renderChats(chats);

            // Если есть chat_id в URL, проверяем его наличие в списке чатов
            if (chatId && !chats.some(chat => chat.id == chatId)) {
                renderErrorMessage('Чат не существует или у вас нет к нему доступа.');
            }
        } catch (error) {
            console.error('Ошибка:', error);
        }
    }

    // Функция для загрузки информации о чате и сообщений
    async function loadChatInfo(chatId) {
        currentChatId = chatId;
        try {
            const chatResponse = await fetch(`/api/messenger/chat_info/${chatId}/`);
            if (!chatResponse.ok) {
                throw new Error('Ошибка при загрузке информации о чате');
            }
            const chatData = await chatResponse.json();
            if (!chatData) {
                renderErrorMessage('Чат не существует или у вас нет к нему доступа.');
                return;
            }
            renderChatInfo(chatData);

            // Загружаем сообщения
            const messagesResponse = await fetch(`/api/messenger/chat_messages_list/?chat_id=${chatId}`);
            if (!messagesResponse.ok) {
                throw new Error('Ошибка при загрузке сообщений');
            }
            const messagesData = await messagesResponse.json();
            renderMessages(messagesData);

            // Сохраняем ссылку на следующую страницу сообщений (если она есть)
            nextMessagesUrl = messagesData.next;
            previousMessagesUrl = messagesData.previous;

            // Прокручиваем к последнему сообщению
            scrollToBottom();
        } catch (error) {
            console.error('Ошибка:', error);
            renderErrorMessage('Чат не существует или у вас нет к нему доступа.');
        }
    }

    // Функция для отображения ошибки
    function renderErrorMessage(message) {
        chatInformation.innerHTML = `<p style="text-align: center; color: red; font-size: 18px;">${message}</p>`;
    }

    // Функция для отображения информации о чате
    function renderChatInfo(chat) {
        chatHeader.innerHTML = `
            <h2>${chat.public_name2 || 'Чат'}</h2>
        `;
    }

    // Функция для отображения сообщений
    function renderMessages(messages) {
        messageList.innerHTML = ''; // Очищаем список сообщений
        messages.results.forEach(message => {
            const messageItem = document.createElement('li');
            messageItem.className = 'message-item';
            messageItem.innerHTML = `
                <p><strong>${message.author_name}</strong>: ${message.text}</p>
                <p><small>${new Date(message.send_time).toLocaleString()}</small></p>
            `;
            messageList.appendChild(messageItem);
        });

        // Убираем кнопку для загрузки больше сообщений, так как она не нужна
        const loadMoreButton = document.querySelector('.load-more-button');
        if (loadMoreButton) {
            loadMoreButton.remove();
        }

        // Прокручиваем к последнему сообщению
        scrollToBottom();
    }

    // Функция для подгрузки предыдущих сообщений при прокрутке вверх
    async function loadPreviousMessages() {
        if (previousMessagesUrl) {
            try {
                const response = await fetch(previousMessagesUrl);
                if (!response.ok) {
                    throw new Error('Ошибка при загрузке предыдущих сообщений');
                }
                const messagesData = await response.json();
                renderMessages(messagesData);
                previousMessagesUrl = messagesData.previous; // Обновляем ссылку на предыдущую страницу
            } catch (error) {
                console.error('Ошибка:', error);
            }
        }
    }

    // Функция для прокрутки списка сообщений в самый низ
    function scrollToBottom() {
        messageList.scrollTop = messageList.scrollHeight;
    }

    // Обработчик события прокрутки, чтобы загружать сообщения с предыдущих страниц
    messageList.addEventListener('scroll', function () {
        if (messageList.scrollTop === 0) {
            loadPreviousMessages();
        }
    });

    // Функция для отображения чатов
    function renderChats(chats) {
        chatsList.innerHTML = ''; // Очищаем список перед добавлением новых элементов
        chats.forEach(chat => {
            const chatItem = document.createElement('li');
            chatItem.className = 'chat-item';

            let chatName = chat.is_group ? chat.name || 'Групповой чат' : chat.public_name2;

            const lastMessage = chat.last_message_text ?
                `${chat.last_message_text} ${new Date(chat.last_message_time).toLocaleString()}` :
                'Нет сообщений';

            const chatAvatar = chat.chat_avatar ? `<div class="chat-avatar"><img src="${chat.chat_avatar}" alt="${chatName}"></div>` : '';

            chatItem.innerHTML = `
                ${chatAvatar}
                <div class="chat-info">
                    <h3>${chatName}</h3>
                    ${!chat.is_group ? `<p class="username">${chat.username2}</p>` : ''}
                    <p class="last-message">${lastMessage}</p>
                </div>
            `;

            chatItem.addEventListener('click', () => {
                loadChatInfo(chat.id); // Загружаем информацию о чате и сообщения
            });

            chatsList.appendChild(chatItem);
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

    // Функция для отображения результатов поиска
    function renderSearchResults(users) {
        chatsList.innerHTML = ''; // Очищаем список перед добавлением новых элементов
        users.forEach(user => {
            const userItem = document.createElement('li');
            userItem.className = 'chat-item';

            const chatName = user.public_name || user.username || 'Личный чат';
            const lastMessage = user.last_chat_message_text ?
                `${user.last_chat_message_text} ${new Date(user.last_chat_message_time).toLocaleString()}` :
                'Нет сообщений';

            const userAvatar = user.avatar ? `<div class="chat-avatar"><img src="${user.avatar}" alt="${user.username}"></div>` : '';

            userItem.innerHTML = `
                ${userAvatar}
                <div class="chat-info">
                    <h3>${chatName}</h3>
                    <p class="username">${user.username}</p>
                    <p class="last-message">${lastMessage}</p>
                </div>
            `;

            userItem.addEventListener('click', () => {
                if (user.chat_id) {
                    loadChatInfo(user.chat_id); // Переход к существующему чату
                } else {
                    // Создать новый чат (если нужно)
                    console.log('Создать новый чат с пользователем:', user.username);
                }
            });

            chatsList.appendChild(userItem);
        });
    }

    // Загружаем чаты при загрузке страницы
    loadChats();
});
