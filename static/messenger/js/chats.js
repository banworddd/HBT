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
                loadMessages(chat.id, 1); // Загружаем первую страницу сообщений
                showMessageForm(chat.id);  // Показываем форму для выбранного чата
            });
        });
    } catch (error) {
        console.error('Ошибка:', error);
        chatsList.innerHTML = '<p>Не удалось загрузить чаты. Пожалуйста, попробуйте позже.</p>';
    }
}

let currentPage = 1;
let isLoading = false;
let hasNextPage = true; // Флаг для отслеживания наличия следующей страницы

async function loadMessages(chatId, page = currentPage) {
    const apiUrl = `/api/messenger/chat_messages_list/?chat_id=${chatId}&page=${page}`;
    const messagesList = document.getElementById('messages-list');

    if (isLoading) return;
    isLoading = true;

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error('Ошибка при загрузке сообщений');
        }

        const data = await response.json();
        const messages = data.results;

        // Очистка списка сообщений перед добавлением новых только если это первая страница
        if (page === 1) {
            messagesList.innerHTML = '';
        }

        // Добавляем сообщения в правильном порядке
        messages.forEach(message => {
            const messageCard = document.createElement('div');
            messageCard.className = 'message-card ' + (message.author_username === username ? 'self' : 'other');
            messageCard.dataset.messageId = message.id;

            const messageBubble = document.createElement('div');
            messageBubble.className = 'message-bubble ' + (message.author_username === username ? 'self' : 'other');

            const messageText = document.createElement('p');
            messageText.className = 'message-text';
            messageText.textContent = message.text;

            const messageTime = document.createElement('p');
            messageTime.className = 'message-time';
            messageTime.textContent = formatDateTime(message.send_time);

            messageBubble.appendChild(messageText);
            messageBubble.appendChild(messageTime);
            messageCard.appendChild(messageBubble);

            if (message.author_username === username) {
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

            const reactionsContainer = document.createElement('div');
            reactionsContainer.className = 'reactions';
            messageCard.appendChild(reactionsContainer);

            const reactions = ['👍', '👎', '❤️', '😊'];
            reactions.forEach(reaction => {
                const reactionButton = document.createElement('button');
                reactionButton.className = 'reaction-btn';
                reactionButton.dataset.reaction = reaction;
                reactionButton.dataset.messageId = message.id;
                reactionButton.innerHTML = `${reaction} <span class="reaction-count">0</span>`;
                reactionButton.addEventListener('click', () => handleReaction(message.id, reaction));
                reactionsContainer.appendChild(reactionButton);
            });

            messagesList.prepend(messageCard); // Добавляем сообщения в начало списка
            loadReactions(message.id);
        });

        // Проверка, есть ли следующая страница
        if (data.next) {
            currentPage = page + 1;
        } else {
            currentPage = page;
            hasNextPage = false; // Устанавливаем флаг, что следующей страницы нет
        }

        // Прокрутка вниз при первой загрузке
        if (page === 1) {
            messagesList.scrollTop = messagesList.scrollHeight;
        }
    } catch (error) {
        console.error('Ошибка:', error);
        messagesList.innerHTML = '<p>Не удалось загрузить сообщения. Пожалуйста, попробуйте позже.</p>';
    } finally {
        isLoading = false;
    }
}


// Обработчик прокрутки
function handleScroll(chatId) {
    const messagesList = document.getElementById('messages-list');
    const threshold = 100; // Порог для начала загрузки следующей страницы

    if (messagesList.scrollTop < threshold && !isLoading && hasNextPage) {
        loadMessages(chatId, currentPage);
    }
}

// Добавьте обработчик прокрутки при открытии чата
function showMessageForm(chatId) {
    const messageForm = document.getElementById('message-form');
    messageForm.style.display = 'block';

    const form = document.getElementById('send-message-form');
    form.onsubmit = async (event) => {
        event.preventDefault();

        const text = document.getElementById('text').value;
        const picture = document.getElementById('picture').files[0];

        try {
            await sendMessage(chatId, text, picture);
            form.reset();
            loadMessages(chatId, 1); // Обновляем список сообщений, начиная с первой страницы
        } catch (error) {
            alert('Не удалось отправить сообщение. Пожалуйста, попробуйте позже.');
        }
    };

    // Загрузка первой страницы сообщений при открытии чата
    currentPage = 1;
    hasNextPage = true; // Сбрасываем флаг при загрузке нового чата
    loadMessages(chatId, 1);

    // Добавляем обработчик прокрутки
    const messagesList = document.getElementById('messages-list');
    messagesList.removeEventListener('scroll', () => handleScroll(chatId));
    messagesList.addEventListener('scroll', () => handleScroll(chatId));
}




// Функция для создания реакции
async function createReaction(messageId, reaction, userId) {
    const apiUrl = `/api/messenger/message_reaction_create/?message_id=${messageId}`;

    const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            reaction: reaction,
            message: messageId,
            author: userId // Только реакция, message_id передается в URL
        }),
    });

    if (!response.ok) {
        throw new Error('Ошибка при создании реакции');
    }
}

async function handleReaction(messageId, reaction) {
    try {
        const response = await fetch(`/api/messenger/message_reactions_count/?message_id=${messageId}`);
        if (!response.ok) {
            throw new Error('Ошибка при загрузке реакций');
        }

        const reactions = await response.json();
        const reactionData = reactions.find(r => r.reaction === reaction);

        if (reactionData?.user_reacted) {
            // Если реакция уже стоит, удаляем её
            await deleteReaction(reactionData.user_reaction_id, messageId);
        } else {
            // Если реакции нет — добавляем
            await createReaction(messageId, reaction, userId);
        }

        // Обновляем отображение реакций после изменения
        await loadReactions(messageId);
    } catch (error) {
        console.error('Ошибка при обработке реакции:', error);
        alert('Не удалось обработать реакцию. Пожалуйста, попробуйте позже.');
    }
}


async function deleteReaction(reactionId, messageId) {
    const response = await fetch(`/api/messenger/message_reactions_detail/${reactionId}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
    });

    if (!response.ok) {
        throw new Error('Ошибка при удалении реакции');
    }

    // Обновляем интерфейс для конкретного сообщения
    console.log('Реакция удалена. Обновляем интерфейс для messageId:', messageId);
    await loadReactions(messageId);
}

async function loadReactions(messageId) {
    try {
        const response = await fetch(`/api/messenger/message_reactions_count/?message_id=${messageId}`);
        if (!response.ok) {
            throw new Error('Ошибка при загрузке реакций');
        }

        const reactions = await response.json();
        const reactionsContainer = document.querySelector(`.message-card[data-message-id="${messageId}"] .reactions`);

        if (!reactionsContainer) {
            return;
        }

        // Список всех возможных реакций
        const allReactions = ['👍', '👎', '❤️', '😊'];

        // Обновляем кнопки реакций
        allReactions.forEach(reaction => {
            const reactionButton = reactionsContainer.querySelector(`.reaction-btn[data-reaction="${reaction}"]`);

            if (reactionButton) {
                // Ищем данные о текущей реакции
                const reactionData = reactions.find(r => r.reaction === reaction);

                if (reactionData) {
                    // Обновляем количество реакций
                    const countElement = reactionButton.querySelector('.reaction-count');
                    if (countElement) {
                        countElement.textContent = reactionData.count;
                    }

                    // Меняем цвет кнопки, если пользователь поставил реакцию
                    if (reactionData.user_reacted) {
                        reactionButton.style.backgroundColor = 'green';
                        reactionButton.style.color = 'white';
                    } else {
                        reactionButton.style.backgroundColor = '';
                        reactionButton.style.color = '';
                    }
                } else {
                    // Если реакции нет в данных, сбрасываем её состояние
                    const countElement = reactionButton.querySelector('.reaction-count');
                    if (countElement) {
                        countElement.textContent = '0';
                    }

                    reactionButton.style.backgroundColor = '';
                    reactionButton.style.color = '';
                }
            }
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



// Функция для форматирования даты и времени в европейский формат
function formatDateTime(dateTimeString) {
    const options = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
    };
    const date = new Date(dateTimeString);
    const formattedDate = date.toLocaleDateString('de-DE', options).replace(',', ''); // 'de-DE' для европейского формата
    const formattedTime = date.toLocaleTimeString('de-DE', options);
    return `${formattedDate} ${formattedTime}`;
}
// Загружаем чаты при загрузке страницы
document.addEventListener('DOMContentLoaded', loadChats);