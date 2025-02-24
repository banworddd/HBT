// Функция для получения CSRF-токена из cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Функция для загрузки чатов
async function loadChats() {
    const apiUrl = `/api/messenger/chats/?user=${username}`;
    const chatsList = document.getElementById('chats-list');

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error('Ошибка при загрузке чатов');
        }

        const chats = await response.json();

        // Очищаем список чатов
        chatsList.innerHTML = '';

        // Отображаем каждый чат
        chats.forEach(chat => {
            const chatCard = document.createElement('div');
            chatCard.className = 'chat-card';
            chatCard.dataset.chatId = chat.id;

            // Аватар чата
            const chatAvatar = document.createElement('img');
            chatAvatar.src = `${chat.chat_avatar}`;
            chatAvatar.alt = 'Аватар чата';
            chatAvatar.className = 'chat-avatar';

            // Название чата
            const chatHeader = document.createElement('div');
            chatHeader.className = 'chat-header';
            const chatTitle = document.createElement('h2');

            if (chat.is_group) {
                chatTitle.textContent = chat.name || 'Групповой чат';
            } else {
                chatTitle.textContent = chat.public_name_2 || `Чат с @${chat.username_2}`;
            }

            chatHeader.appendChild(chatAvatar);
            chatHeader.appendChild(chatTitle);

            // Последнее сообщение
            const lastMessage = document.createElement('div');
            lastMessage.className = 'last-message';
            const messageText = document.createElement('p');
            messageText.innerHTML = `<strong>Последнее сообщение:</strong> ${chat.last_message_text}`;
            const messageTime = document.createElement('p');
            messageTime.innerHTML = `<small>${chat.last_message_time}</small>`;
            lastMessage.appendChild(messageText);
            lastMessage.appendChild(messageTime);

            // Собираем карточку чата
            chatCard.appendChild(chatHeader);
            chatCard.appendChild(lastMessage);
            chatsList.appendChild(chatCard);

            // Добавляем обработчик клика на чат
            chatCard.addEventListener('click', () => {
                loadMessages(chat.id);
                showMessageForm(chat.id);  // Показываем форму для выбранного чата
            });
        });
    } catch (error) {
        console.error('Ошибка:', error);
        chatsList.innerHTML = '<p>Не удалось загрузить чаты. Пожалуйста, попробуйте позже.</p>';
    }
}

// Функция для загрузки сообщений чата
async function loadMessages(chatId) {
    const apiUrl = `/api/messenger/chat_messages_list/?chat_id=${chatId}`;
    const messagesList = document.getElementById('messages-list');

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error('Ошибка при загрузке сообщений');
        }

        const data = await response.json();
        const messages = data.results;

        // Очищаем список сообщений
        messagesList.innerHTML = '';

        // Отображаем каждое сообщение
        messages.forEach(message => {
            const messageCard = document.createElement('div');
            messageCard.className = 'message-card';
            messageCard.dataset.messageId = message.id;  // Добавляем id сообщения

            // Аватар автора
            const authorAvatar = document.createElement('img');
            authorAvatar.src = `/media/${message.author_avatar}`;
            authorAvatar.alt = 'Аватар автора';
            authorAvatar.className = 'author-avatar';

            // Имя автора
            const authorName = document.createElement('p');
            authorName.textContent = message.author_name;

            // Текст сообщения
            const messageText = document.createElement('p');
            messageText.textContent = message.text;

            // Время отправки
            const messageTime = document.createElement('p');
            messageTime.textContent = message.send_time;

            // Собираем карточку сообщения
            messageCard.appendChild(authorAvatar);
            messageCard.appendChild(authorName);
            messageCard.appendChild(messageText);
            messageCard.appendChild(messageTime);

            // Добавляем кнопки "Удалить" и "Редактировать", если автор — текущий пользователь
            if (message.author_username === `${username}`) {
                const deleteButton = document.createElement('button');
                deleteButton.textContent = 'Удалить';
                deleteButton.className = 'delete-button';
                deleteButton.addEventListener('click', () => deleteMessage(message.id));
                messageCard.appendChild(deleteButton);

                const editButton = document.createElement('button');
                editButton.textContent = 'Редактировать';
                editButton.className = 'edit-button';
                editButton.addEventListener('click', () => showEditMessageForm(message.id, message.text, message.picture));
                messageCard.appendChild(editButton);
            }

            // Добавляем кнопки реакций
            const reactionsContainer = document.createElement('div');
            reactionsContainer.className = 'reactions';
            const reactions = ['👍', '👎', '❤️', '😊'];
            reactions.forEach(reaction => {
                const reactionButton = document.createElement('button');
                reactionButton.className = 'reaction-btn';
                reactionButton.textContent = reaction;
                reactionButton.dataset.reaction = reaction;
                reactionButton.addEventListener('click', () => handleReaction(message.id, reaction));
                reactionsContainer.appendChild(reactionButton);
            });
            messageCard.appendChild(reactionsContainer);

            // Добавляем список реакций
            const reactionsList = document.createElement('div');
            reactionsList.className = 'reactions-list';
            reactionsList.id = `reactions-list-${message.id}`;
            messageCard.appendChild(reactionsList);

            // Загружаем реакции для этого сообщения
            loadReactions(message.id);

            // Добавляем карточку сообщения в список
            messagesList.appendChild(messageCard);
        });
    } catch (error) {
        console.error('Ошибка:', error);
        messagesList.innerHTML = '<p>Не удалось загрузить сообщения. Пожалуйста, попробуйте позже.</p>';
    }
}

// Функция для создания реакции
async function createReaction(messageId, reaction, userId) {
    const apiUrl = `/api/messenger/message_reactions/?message_id=${messageId}`;

    const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            reaction: reaction,
            message: messageId,
            author: userId// Только реакция, message_id передается в URL
        }),
    });
    if (!response.ok) {
        throw new Error('Ошибка при создании реакции');
    }
}

// Функция для обработки реакции
async function handleReaction(messageId, reaction) {
    try {
        const existingReaction = await checkExistingReaction(messageId, reaction);

        if (existingReaction) {
            // Если реакция уже есть, удаляем её
            await deleteReaction(existingReaction.id);
        } else {
            // Если реакции нет, создаем новую
            await createReaction(messageId, reaction, userId);
        }

        // Обновляем список реакций
        await loadReactions(messageId);
    } catch (error) {
        console.error('Ошибка при обработке реакции:', error);
        alert('Не удалось обработать реакцию. Пожалуйста, попробуйте позже.');
    }
}

// Функция для проверки существующей реакции
async function checkExistingReaction(messageId, reaction) {
    const response = await fetch(`/api/messenger/message_reactions/?message_id=${messageId}`);
    if (!response.ok) {
        throw new Error('Ошибка при загрузке реакций');
    }

    const reactions = await response.json();

    // Ищем реакцию текущего пользователя
    return reactions.find(r => r.reaction === reaction && r.author_username === username);
}

// Функция для удаления реакции
async function deleteReaction(reactionId) {
    const response = await fetch(`/api/messenger/message_reactions_detail/${reactionId}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
    });

    if (!response.ok) {
        throw new Error('Ошибка при удалении реакции');
    }
}

// Функция для загрузки и отображения реакций
async function loadReactions(messageId) {
    try {
        const response = await fetch(`/api/messenger/message_reactions/?message_id=${messageId}`);
        if (!response.ok) {
            throw new Error('Ошибка при загрузке реакций');
        }

        const reactions = await response.json();

        const reactionsList = document.getElementById(`reactions-list-${messageId}`);
        reactionsList.innerHTML = '';

        reactions.forEach(reaction => {
            const reactionElement = document.createElement('div');
            reactionElement.textContent = `${reaction.author_username}: ${reaction.reaction}`;
            reactionsList.appendChild(reactionElement);
        });
    } catch (error) {
        console.error('Ошибка при загрузке реакций:', error);
    }
}

// Функция для удаления сообщения
async function deleteMessage(messageId) {
    if (confirm('Вы уверены, что хотите удалить это сообщение?')) {
        try {
            const response = await fetch(`/api/messenger/chat_message_delete/${messageId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ is_deleted: true }),
            });

            if (!response.ok) {
                throw new Error('Ошибка при удалении сообщения');
            }

            // Обновляем список сообщений после удаления
            const chatId = document.querySelector('.chat-card.active')?.dataset.chatId;
            if (chatId) {
                loadMessages(chatId);
            }
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Не удалось удалить сообщение. Пожалуйста, попробуйте позже.');
        }
    }
}

// Функция для отправки сообщения
async function sendMessage(chatId, text, picture) {
    const formData = new FormData();
    if (text) {
        formData.append('text', text);
    }
    formData.append('chat', chatId);
    if (picture) {
        formData.append('picture', picture);
    }

    try {
        const response = await fetch(`/api/messenger/chat_messages_list/?chat_id=${chatId}`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        });

        if (!response.ok) {
            throw new Error('Ошибка при отправке сообщения');
        }

        return await response.json();
    } catch (error) {
        console.error('Ошибка:', error);
        throw error;
    }
}

// Функция для обновления сообщения
async function updateMessage(messageId, text, picture, removePicture) {
    const formData = new FormData();
    if (text) {
        formData.append('text', text);
    }
    if (picture) {
        formData.append('picture', picture);
    }
    if (removePicture) {
        formData.append('picture', '');  // Удаляем текущую картинку
    }

    try {
        const response = await fetch(`/api/messenger/chat_message_update/${messageId}/`, {
            method: 'PATCH',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        });

        if (!response.ok) {
            throw new Error('Ошибка при обновлении сообщения');
        }

        return await response.json();
    } catch (error) {
        console.error('Ошибка:', error);
        throw error;
    }
}

// Функция для отображения формы редактирования сообщения
function showEditMessageForm(messageId, currentText, currentPicture) {
    const editForm = document.getElementById('edit-message-form');
    editForm.style.display = 'block';  // Показываем форму

    // Заполняем форму текущими данными
    document.getElementById('edit-text').value = currentText;

    // Обработчик отправки формы
    const form = document.getElementById('edit-message-form-content');
    form.onsubmit = async (event) => {
        event.preventDefault();

        const text = document.getElementById('edit-text').value;
        const picture = document.getElementById('edit-picture').files[0];
        const removePicture = document.getElementById('remove-picture').checked;

        try {
            await updateMessage(messageId, text, picture, removePicture);
            editForm.style.display = 'none';  // Скрываем форму
            const chatId = document.querySelector('.chat-card.active')?.dataset.chatId;
            if (chatId) {
                loadMessages(chatId);  // Обновляем список сообщений
            }
        } catch (error) {
            alert('Не удалось обновить сообщение. Пожалуйста, попробуйте позже.');
        }
    };

    // Обработчик отмены редактирования
    document.getElementById('cancel-edit').onclick = () => {
        editForm.style.display = 'none';  // Скрываем форму
    };
}

// Функция для отображения формы отправки сообщения
function showMessageForm(chatId) {
    const messageForm = document.getElementById('message-form');
    messageForm.style.display = 'block';  // Показываем форму

    // Обработчик отправки формы
    const form = document.getElementById('send-message-form');
    form.onsubmit = async (event) => {
        event.preventDefault();

        const text = document.getElementById('text').value;
        const picture = document.getElementById('picture').files[0];

        try {
            await sendMessage(chatId, text, picture);
            form.reset();  // Очищаем форму
            loadMessages(chatId);  // Обновляем список сообщений
        } catch (error) {
            alert('Не удалось отправить сообщение. Пожалуйста, попробуйте позже.');
        }
    };
}

// Загружаем чаты при загрузке страницы
document.addEventListener('DOMContentLoaded', loadChats);