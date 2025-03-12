// ========================
// 1. Вспомогательные функции
// ========================

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

// Функция для отображения галочек в зависимости от статуса сообщения
function getMessageStatusIcon(status) {
    if (status === 'S') {
        return `
            <span class="message-status">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check2" viewBox="0 0 16 16">
                    <path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"/>
                </svg>
            </span>
        `; // Одна галочка
    } else if (status === 'R') {
        return `
            <span class="message-status">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check2-all" viewBox="0 0 16 16">
                    <path d="M12.354 4.354a.5.5 0 0 0-.708-.708L5 10.293 1.854 7.146a.5.5 0 1 0-.708.708l3.5 3.5a.5.5 0 0 0 .708 0l7-7zm-4.208 7-.896-.897.707-.707.543.543 6.646-6.647a.5.5 0 0 1 .708.708l-7 7a.5.5 0 0 1-.708 0z"/>
                    <path d="m5.354 7.146.896.897-.707.707-.897-.896a.5.5 0 1 1 .708-.708z"/>
                </svg>
            </span>
        `; // Две галочки
    }
    return ''; // Если статус неизвестен, ничего не отображаем
}

// Функция для форматирования даты и времени
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
    const now = new Date();

    if (date.toDateString() === now.toDateString()) {
        return date.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
    } else {
        return date.toLocaleDateString('de-DE', { year: 'numeric', month: '2-digit', day: '2-digit' });
    }
}

// ========================
// 2. Работа с чатами
// ========================

async function loadChats() {
    const apiUrl = `/api/messenger/chats/?user=${username}`;
    const chatsList = document.getElementById('chats-list');

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error('Ошибка при загрузке чатов');
        }

        const chats = await response.json();
        chatsList.innerHTML = '';

        chats.forEach(chat => {
            const chatCard = document.createElement('div');
            chatCard.className = 'chat-card';
            chatCard.dataset.chatId = chat.id;

            const chatAvatar = document.createElement('img');
            chatAvatar.src = `${chat.chat_avatar}`;
            chatAvatar.alt = 'Аватар чата';
            chatAvatar.className = 'chat-avatar';

            const chatHeader = document.createElement('div');
            chatHeader.className = 'chat-header';

            const chatInfo = document.createElement('div');
            chatInfo.className = 'chat-info';

            const chatTitle = document.createElement('h2');
            chatTitle.className = 'chat-title';

            if (chat.is_group) {
                chatTitle.textContent = chat.name || 'Групповой чат';
            } else {
                chatTitle.textContent = chat.public_name_2 || chat.username_2;
            }

            const lastMessage = document.createElement('div');
            lastMessage.className = 'last-message';

            const messageContent = document.createElement('div');
            messageContent.className = 'message-content';

            if (chat.last_message_picture) {
                const messageImagePreview = document.createElement('img');
                messageImagePreview.src = `/media/${chat.last_message_picture}`;
                messageImagePreview.className = 'message-image-preview';
                messageContent.appendChild(messageImagePreview);
            }

            const messageText = document.createElement('p');
            messageText.className = 'message-text';

            if (chat.last_message_text) {
                const truncatedText = chat.last_message_text.length > 15
                    ? chat.last_message_text.substring(0, 15) + '...'
                    : chat.last_message_text;
                messageText.textContent = truncatedText;
            } else {
                messageText.textContent = 'Изображение';
            }

            messageContent.appendChild(messageText);

            // Добавляем галочки или индикатор непрочитанного сообщения
            if (chat.last_message_author != userId && chat.last_message_status === "S") {
                const unreadIndicator = document.createElement('span');
                unreadIndicator.className = 'unread-indicator';
                messageContent.appendChild(unreadIndicator);
            } else if (chat.last_message_author == userId) {
                const statusIcon = getMessageStatusIcon(chat.last_message_status);
                messageContent.innerHTML += statusIcon; // Добавляем галочки
            }

            lastMessage.appendChild(messageContent);

            const messageTime = document.createElement('p');
            messageTime.className = 'message-time';
            messageTime.innerHTML = `<small>${formatDateTime(chat.last_message_time)}</small>`;
            lastMessage.appendChild(messageTime);

            chatInfo.appendChild(chatTitle);
            chatInfo.appendChild(lastMessage);

            chatHeader.appendChild(chatAvatar);
            chatHeader.appendChild(chatInfo);
            chatCard.appendChild(chatHeader);

            chatsList.appendChild(chatCard);

            chatCard.addEventListener('click', () => {
                showMessageForm(chat.id);
            });
        });
    } catch (error) {
        console.error('Ошибка:', error);
        chatsList.innerHTML = '<p>Не удалось загрузить чаты. Пожалуйста, попробуйте позже.</p>';
    }
}

// ========================
// 3. Работа с сообщениями
// ========================
let currentChatId = null; // Переменная для хранения ID текущего открытого чата
let currentPage = 1;
let isLoading = false;
let hasNextPage = true;

// Загрузка сообщений для конкретного чата
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

        if (page === 1) {
            messagesList.innerHTML = '';
        }

        messages.forEach(message => {
            const messageCard = document.createElement('div');
            messageCard.className = 'message-card ' + (message.author_username === username ? 'self' : 'other');
            messageCard.dataset.messageId = message.id;

            const messageBubble = document.createElement('div');
            messageBubble.className = 'message-bubble ' + (message.author_username === username ? 'self' : 'other');

            if (message.picture) {
                const messageImage = document.createElement('img');
                messageImage.src = message.picture;
                messageImage.className = 'message-image';
                messageBubble.appendChild(messageImage);
            }

            if (message.text) {
                const messageText = document.createElement('p');
                messageText.className = 'message-text';
                messageText.textContent = message.text;
                messageBubble.appendChild(messageText);
            }

            const messageTime = document.createElement('p');
            messageTime.className = 'message-time';
            messageTime.textContent = formatDateTime(message.send_time);

            messageBubble.appendChild(messageTime);

            const reactionsContainer = document.createElement('div');
            reactionsContainer.className = 'reactions-container';

            const reactions = document.createElement('div');
            reactions.className = 'reactions';

            reactionsContainer.appendChild(reactions);

            messageCard.appendChild(messageBubble);
            messageCard.appendChild(reactionsContainer);

            messageCard.addEventListener('contextmenu', (event) => {
                const isAuthor = message.author_username === username;
                showContextMenu(event, message.id, isAuthor);
            });

            messagesList.prepend(messageCard);

            loadReactions(message.id);
        });

        if (data.next) {
            currentPage = page + 1;
        } else {
            currentPage = page;
            hasNextPage = false;
        }

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

// Обработчик прокрутки для загрузки новых сообщений
function handleScroll(chatId) {
    const messagesList = document.getElementById('messages-list');
    const threshold = 100;

    if (messagesList.scrollTop < threshold && !isLoading && hasNextPage) {
        loadMessages(chatId, currentPage);
    }
}

// Отправка сообщения
async function sendMessage(chatId, text, picture) {
    let pictureUrl = null;

    if (picture) {
        const formData = new FormData();
        formData.append("picture", picture);

        try {
            const response = await fetch(`/api/messenger/upload_image/`, {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                },
            });

            if (!response.ok) {
                throw new Error("Ошибка при загрузке изображения");
            }

            const imageData = await response.json();
            pictureUrl = imageData.picture_url;
        } catch (error) {
            console.error("Ошибка:", error);
            return;
        }
    }

    const messageData = {
        message: text,
        chat_id: chatId,
        author_id: userId,
        picture_url: pictureUrl,
    };

    socket.send(JSON.stringify(messageData));
}

// Обновление сообщения
async function updateMessage(messageId, text, picture, removePicture) {
    const formData = new FormData();
    if (text) {
        formData.append('text', text);
    }
    if (picture) {
        formData.append('picture', picture);
    }
    if (removePicture) {
        formData.append('picture', '');
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

// Удаление сообщения
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

function showMessageForm(chatId) {
    // Обновляем currentChatId
    currentChatId = chatId;

    // Остальной код функции showMessageForm остается без изменений
    const url = new URL(window.location);
    url.searchParams.set('chat_id', chatId);
    window.history.pushState({}, '', url);

    localStorage.setItem('openChatId', chatId);

    const allChatCards = document.querySelectorAll('.chat-card');
    allChatCards.forEach(card => card.classList.remove('active'));

    const selectedChatCard = document.querySelector(`.chat-card[data-chat-id="${chatId}"]`);
    if (selectedChatCard) {
        selectedChatCard.classList.add('active');
    }

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
            loadMessages(chatId, 1);
        } catch (error) {
            alert('Не удалось отправить сообщение. Пожалуйста, попробуйте позже.');
        }
    };

    currentPage = 1;
    hasNextPage = true;
    loadMessages(chatId, 1);

    connectWebSocket(chatId);

    const messagesList = document.getElementById('messages-list');
    messagesList.removeEventListener('scroll', () => handleScroll(chatId));
    messagesList.addEventListener('scroll', () => handleScroll(chatId));
}

async function markMessagesAsRead(chatId) {
    try {
        const response = await fetch(`/api/messenger/mark_message_as_read/?chat_id=${chatId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
        });

        if (!response.ok) {
            throw new Error('Ошибка при обновлении статуса сообщений');
        }

        console.log('Статус сообщений обновлен на "R"');

        // После обновления статуса обновляем список чатов
        const chatCard = document.querySelector(`.chat-card[data-chat-id="${chatId}"]`);
        if (chatCard) {
            const lastMessageText = chatCard.querySelector('.message-text').textContent;
            const lastMessageTime = chatCard.querySelector('.message-time small').textContent;

            // Создаем фиктивное сообщение для обновления интерфейса
            const fakeMessage = {
                chat_id: chatId,
                message: lastMessageText,
                send_time: lastMessageTime,
                author__username: username, // Предполагаем, что сообщение от текущего пользователя
                status: 'R', // Новый статус
            };

            updateChatList(fakeMessage);
        }
    } catch (error) {
        console.error('Ошибка при обновлении статуса сообщений:', error);
    }
}

// ========================
// 4. Работа с реакциями
// ========================

// Создание реакции
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
            author: userId
        }),
    });

    if (!response.ok) {
        throw new Error('Ошибка при создании реакции');
    }
}

// Удаление реакции
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

    await loadReactions(messageId);
}

// Загрузка реакций для сообщения
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

        reactionsContainer.innerHTML = '';

        reactions.forEach(reaction => {
            const reactionButton = document.createElement('button');
            reactionButton.className = 'reaction-btn';
            reactionButton.dataset.reaction = reaction.reaction;
            reactionButton.dataset.messageId = messageId;
            reactionButton.innerHTML = `${reaction.reaction} <span class="reaction-count">${reaction.count}</span>`;

            if (reaction.user_reacted) {
                reactionButton.classList.add('user-reacted');
            }

            reactionButton.addEventListener('click', () => handleReaction(messageId, reaction.reaction));
            reactionsContainer.appendChild(reactionButton);
        });
    } catch (error) {
        console.error('Ошибка при загрузке реакций:', error);
    }
}

// Обработка реакции
async function handleReaction(messageId, reaction) {
    try {
        const response = await fetch(`/api/messenger/message_reactions_count/?message_id=${messageId}`);
        if (!response.ok) {
            throw new Error('Ошибка при загрузке реакций');
        }

        const reactions = await response.json();
        const reactionData = reactions.find(r => r.reaction === reaction);

        if (reactionData?.user_reacted) {
            await deleteReaction(reactionData.user_reaction_id, messageId);
        } else {
            await createReaction(messageId, reaction, userId);
        }

        await loadReactions(messageId);
    } catch (error) {
        console.error('Ошибка при обработке реакции:', error);
        alert('Не удалось обработать реакцию. Пожалуйста, попробуйте позже.');
    }
}

// ========================
// 5. Контекстное меню
// ========================

// Отображение контекстного меню
function showContextMenu(event, messageId, isAuthor) {
    event.preventDefault();

    const contextMenu = document.getElementById('context-menu');
    if (!contextMenu) return;

    contextMenu.style.display = 'block';
    contextMenu.style.left = `${event.pageX}px`;
    contextMenu.style.top = `${event.pageY}px`;

    const editButton = document.getElementById('edit-message-btn');
    const deleteButton = document.getElementById('delete-message-btn');
    const reactionsContextMenu = document.querySelector('.reactions-context-menu');

    if (editButton && deleteButton && reactionsContextMenu) {
        editButton.onclick = null;
        deleteButton.onclick = null;
        reactionsContextMenu.innerHTML = '';

        if (isAuthor) {
            editButton.style.display = 'block';
            deleteButton.style.display = 'block';

            editButton.onclick = () => {
                const messageCard = document.querySelector(`.message-card[data-message-id="${messageId}"]`);
                const messageText = messageCard.querySelector('.message-text').textContent;
                const messagePicture = null;
                showEditMessageForm(messageId, messageText, messagePicture);
                hideContextMenu();
            };

            deleteButton.onclick = () => {
                deleteMessage(messageId);
                hideContextMenu();
            };
        } else {
            editButton.style.display = 'none';
            deleteButton.style.display = 'none';
        }

        const reactions = ['👍', '👎', '❤️', '😊'];
        reactions.forEach(reaction => {
            const reactionButton = document.createElement('button');
            reactionButton.className = 'reaction-btn';
            reactionButton.dataset.reaction = reaction;
            reactionButton.textContent = reaction;
            reactionButton.onclick = () => {
                handleReaction(messageId, reaction);
                hideContextMenu();
            };
            reactionsContextMenu.appendChild(reactionButton);
        });
    }
}

// Скрытие контекстного меню
function hideContextMenu() {
    const contextMenu = document.getElementById('context-menu');
    if (contextMenu) {
        contextMenu.style.display = 'none';
    }
}

// ========================
// 6. WebSocket
// ========================

let socket;

// Подключение к WebSocket
function connectWebSocket(chatId) {
    const chatUrl = `ws://${window.location.host}/ws/chat/${chatId}/`;
    socket = new WebSocket(chatUrl);

    socket.onopen = function(event) {
        console.log('WebSocket соединение установлено');
    };

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleNewMessage(data);
    };

    socket.onclose = function(event) {
        console.log('WebSocket соединение закрыто');
    };

    socket.onerror = function(error) {
        console.error('WebSocket ошибка:', error);
    };
}

// Обработка нового сообщения через WebSocket
function handleNewMessage(message) {
    const messagesList = document.getElementById('messages-list');
    const messageCard = document.createElement('div');
    messageCard.className = 'message-card ' + (message.author__username === username ? 'self' : 'other');
    messageCard.dataset.messageId = message.id;

    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble ' + (message.author__username === username ? 'self' : 'other');

    if (message.picture_url) {
        const messageImage = document.createElement('img');
        messageImage.src = message.picture_url;
        messageImage.className = 'message-image';
        messageBubble.appendChild(messageImage);
    }

    if (message.message) {
        const messageText = document.createElement('p');
        messageText.className = 'message-text';
        messageText.textContent = message.message;
        messageBubble.appendChild(messageText);
    }

    const messageTime = document.createElement('p');
    messageTime.className = 'message-time';
    messageTime.textContent = formatDateTime(message.send_time);

    messageBubble.appendChild(messageTime);

    const reactionsContainer = document.createElement('div');
    reactionsContainer.className = 'reactions-container';

    const reactions = document.createElement('div');
    reactions.className = 'reactions';

    reactionsContainer.appendChild(reactions);

    messageCard.appendChild(messageBubble);
    messageCard.appendChild(reactionsContainer);

    messagesList.appendChild(messageCard);

    messagesList.scrollTop = messagesList.scrollHeight;

    // Если чат открыт, обновляем статус всех непрочитанных сообщений на "R"
    if (currentChatId === message.chat_id) {
        markMessagesAsRead(message.chat_id);
    }

    loadReactions(message.id);
    updateChatList(message);
}

function updateChatList(message) {
    const chatCard = document.querySelector(`.chat-card[data-chat-id="${message.chat_id}"]`);

    if (chatCard) {
        // Обновляем текст последнего сообщения
        const lastMessageText = chatCard.querySelector('.message-text');
        lastMessageText.textContent = message.message ? message.message : 'Изображение';

        // Обновляем время последнего сообщения
        const messageTime = chatCard.querySelector('.message-time small');
        messageTime.textContent = formatDateTime(message.send_time);

        // Обновляем статус последнего сообщения
        const messageContent = chatCard.querySelector('.message-content');
        if (messageContent) {
            // Убираем индикатор непрочитанного сообщения
            const unreadIndicator = messageContent.querySelector('.unread-indicator');
            if (unreadIndicator) {
                unreadIndicator.remove();
            }

            // Если сообщение от текущего пользователя, обновляем галочки
            if (message.author__username === username) {
                const statusIcon = getMessageStatusIcon(message.status);
                const existingStatusIcon = messageContent.querySelector('.message-status');
                if (existingStatusIcon) {
                    existingStatusIcon.innerHTML = statusIcon;
                } else {
                    messageContent.innerHTML += statusIcon;
                }
            }
        }

        // Перемещаем чат вверх
        const chatsList = document.getElementById('chats-list');
        chatsList.prepend(chatCard);
    } else {
        // Если чата нет в списке, загружаем заново
        loadChats();
    }
}

// ========================
// 7. Инициализация
// ========================

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    loadChats();

    const urlParams = new URLSearchParams(window.location.search);
    const chatIdFromUrl = urlParams.get('chat_id');

    if (chatIdFromUrl) {
        showMessageForm(chatIdFromUrl);
    } else {
        const openChatId = localStorage.getItem('openChatId');
        if (openChatId) {
            localStorage.removeItem('openChatId');
        }
    }
});

// Обработчик изменения URL
window.addEventListener('popstate', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const chatIdFromUrl = urlParams.get('chat_id');

    if (chatIdFromUrl) {
        showMessageForm(chatIdFromUrl);
    } else {
        closeChat();
    }
});

// ========================
// 8. Дополнительные обработчики
// ========================

// Обработчик отправки сообщения по нажатию Enter
document.addEventListener('DOMContentLoaded', () => {
    const textarea = document.getElementById('text');

    textarea.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            document.getElementById('send-message-form').dispatchEvent(new Event('submit', { cancelable: true }));
        } else if (event.key === 'Enter' && event.shiftKey) {
            // Позволяем добавить новую строку
        }
    });
});

// Обработчик для прикрепления изображений
document.addEventListener('DOMContentLoaded', () => {
    const attachBtn = document.getElementById('attach-btn');
    const fileInput = document.getElementById('picture');
    const imagePreview = document.getElementById('image-preview');

    attachBtn.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.src = e.target.result;
                imagePreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    });
});

// Обработчик для модального окна с изображением
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('image-modal');
    const modalImage = document.getElementById('modal-image');
    const closeModal = document.getElementById('close-modal');

    document.getElementById('messages-list').addEventListener('click', (event) => {
        if (event.target.tagName === 'IMG') {
            modalImage.src = event.target.src;
            modal.style.display = 'block';
        }
    });

    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});