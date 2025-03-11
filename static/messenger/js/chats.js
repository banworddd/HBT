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

            const chatInfo = document.createElement('div');
            chatInfo.className = 'chat-info';

            const chatTitle = document.createElement('h2');
            chatTitle.className = 'chat-title';

            if (chat.is_group) {
                chatTitle.textContent = chat.name || 'Групповой чат';
            } else {
                chatTitle.textContent = chat.public_name_2 || chat.username_2;
            }

            // Последнее сообщение
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
            lastMessage.appendChild(messageContent);

            const messageTime = document.createElement('p');
            messageTime.className = 'message-time';
            messageTime.innerHTML = `<small>${formatDateTime(chat.last_message_time)}</small>`;
            lastMessage.appendChild(messageTime);

            chatInfo.appendChild(chatTitle);
            chatInfo.appendChild(lastMessage);

            chatHeader.appendChild(chatAvatar);
            chatHeader.appendChild(chatInfo);

            // Собираем карточку чата
            chatCard.appendChild(chatHeader);
            chatsList.appendChild(chatCard);

            // Добавляем обработчик клика на чат
            chatCard.addEventListener('click', () => {
                showMessageForm(chat.id); // Открываем чат
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

            // Контейнер для реакций (теперь внутри пузырька)
            const reactionsContainer = document.createElement('div');
            reactionsContainer.className = 'reactions';

            // Собираем пузырек сообщения
            messageBubble.appendChild(messageTime);
            messageBubble.appendChild(reactionsContainer); // Добавляем реакции внутрь пузырька

            // Собираем карточку сообщения
            messageCard.appendChild(messageBubble);

            // Добавляем обработчик для правой кнопки мыши
            messageCard.addEventListener('contextmenu', (event) => {
                const isAuthor = message.author_username === username;
                showContextMenu(event, message.id, isAuthor);
            });

            messagesList.prepend(messageCard);

            // Загружаем реакции для этого сообщения
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



// Обработчик прокрутки
function handleScroll(chatId) {
    const messagesList = document.getElementById('messages-list');
    const threshold = 100; // Порог для начала загрузки следующей страницы

    if (messagesList.scrollTop < threshold && !isLoading && hasNextPage) {
        loadMessages(chatId, currentPage);
    }
}

// Функция для отображения формы сообщений и выделения чата
function showMessageForm(chatId) {
    // Обновляем URL с ID чата
    const url = new URL(window.location);
    url.searchParams.set('chat_id', chatId);
    window.history.pushState({}, '', url);

    // Сохраняем ID открытого чата в localStorage
    localStorage.setItem('openChatId', chatId);

    // Убираем выделение со всех карточек чатов
    const allChatCards = document.querySelectorAll('.chat-card');
    allChatCards.forEach(card => card.classList.remove('active'));

    // Добавляем выделение на выбранную карточку
    const selectedChatCard = document.querySelector(`.chat-card[data-chat-id="${chatId}"]`);
    if (selectedChatCard) {
        selectedChatCard.classList.add('active');
    }

    // Показываем форму отправки сообщения
    const messageForm = document.getElementById('message-form');
    messageForm.style.display = 'block';

    // Настройка обработчика отправки сообщения
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
    messagesList.removeEventListener('scroll', () => handleScroll(chatId)); // Удаляем старый обработчик
    messagesList.addEventListener('scroll', () => handleScroll(chatId)); // Добавляем новый обработчик
}

// Функция для закрытия чата
function closeChat() {
    // Сбрасываем выделение
    const allChatCards = document.querySelectorAll('.chat-card');
    allChatCards.forEach(card => card.classList.remove('active'));

    // Очищаем список сообщений и скрываем форму
    const messagesList = document.getElementById('messages-list');
    messagesList.innerHTML = '';
    const messageForm = document.getElementById('message-form');
    messageForm.style.display = 'none';

    // Удаляем ID открытого чата из localStorage
    localStorage.removeItem('openChatId');

    // Очищаем chat_id из URL
    const url = new URL(window.location);
    url.searchParams.delete('chat_id');
    window.history.pushState({}, '', url);
}

document.addEventListener('DOMContentLoaded', () => {
    // Загружаем список чатов
    loadChats();

    // Получаем ID чата из URL
    const urlParams = new URLSearchParams(window.location.search);
    const chatIdFromUrl = urlParams.get('chat_id');

    // Если в URL указан chat_id, открываем этот чат
    if (chatIdFromUrl) {
        showMessageForm(chatIdFromUrl);
    } else {
        // Если chat_id не указан в URL, проверяем localStorage
        const openChatId = localStorage.getItem('openChatId');
        if (openChatId) {
            // Удаляем сохраненный ID чата из localStorage, чтобы не открывать его автоматически в будущем
            localStorage.removeItem('openChatId');
        }
    }
});

// Обработчик изменения URL (если пользователь вручную меняет URL)
window.addEventListener('popstate', () => {
    // Получаем ID чата из URL
    const urlParams = new URLSearchParams(window.location.search);
    const chatIdFromUrl = urlParams.get('chat_id');

    // Если в URL указан chat_id, открываем этот чат
    if (chatIdFromUrl) {
        showMessageForm(chatIdFromUrl);
    } else {
        closeChat();
    }
});

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

        // Очищаем контейнер
        reactionsContainer.innerHTML = '';

        // Добавляем только те реакции, которые есть на сообщении
        reactions.forEach(reaction => {
            const reactionButton = document.createElement('button');
            reactionButton.className = 'reaction-btn';
            reactionButton.dataset.reaction = reaction.reaction;
            reactionButton.dataset.messageId = messageId;
            reactionButton.innerHTML = `${reaction.reaction} <span class="reaction-count">${reaction.count}</span>`;

            // Если пользователь поставил эту реакцию, добавляем класс
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
    const now = new Date();

    // Проверяем, было ли сообщение отправлено сегодня
    if (date.toDateString() === now.toDateString()) {
        // Если да, возвращаем только время
        return date.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
    } else {
        // Если нет, возвращаем только дату
        return date.toLocaleDateString('de-DE', { year: 'numeric', month: '2-digit', day: '2-digit' });
    }
}

// Функция для отображения контекстного меню
function showContextMenu(event, messageId, isAuthor) {
    event.preventDefault(); // Отменяем стандартное контекстное меню браузера

    const contextMenu = document.getElementById('context-menu');
    if (!contextMenu) return;

    // Показываем меню для любого сообщения
    contextMenu.style.display = 'block';
    contextMenu.style.left = `${event.pageX}px`;
    contextMenu.style.top = `${event.pageY}px`;

    // Очищаем предыдущие обработчики
    const editButton = document.getElementById('edit-message-btn');
    const deleteButton = document.getElementById('delete-message-btn');
    const reactionsContextMenu = document.querySelector('.reactions-context-menu');

    if (editButton && deleteButton && reactionsContextMenu) {
        // Убираем старые обработчики
        editButton.onclick = null;
        deleteButton.onclick = null;
        reactionsContextMenu.innerHTML = '';

        // Если сообщение свое, показываем кнопки "Удалить" и "Редактировать"
        if (isAuthor) {
            editButton.style.display = 'block';
            deleteButton.style.display = 'block';

            // Обработчик для кнопки "Редактировать"
            editButton.onclick = () => {
                const messageCard = document.querySelector(`.message-card[data-message-id="${messageId}"]`);
                const messageText = messageCard.querySelector('.message-text').textContent;
                const messagePicture = null; // Здесь можно добавить логику для получения картинки
                showEditMessageForm(messageId, messageText, messagePicture);
                hideContextMenu();
            };

            // Обработчик для кнопки "Удалить"
            deleteButton.onclick = () => {
                deleteMessage(messageId);
                hideContextMenu();
            };
        } else {
            // Если сообщение чужое, скрываем кнопки "Удалить" и "Редактировать"
            editButton.style.display = 'none';
            deleteButton.style.display = 'none';
        }

        // Добавляем реакции в контекстное меню для всех сообщений
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

// Функция для скрытия контекстного меню
function hideContextMenu() {
    const contextMenu = document.getElementById('context-menu');
    if (contextMenu) {
        contextMenu.style.display = 'none';
    }
}

// Добавляем обработчик для скрытия меню при клике вне его
document.addEventListener('click', hideContextMenu);

// Добавляем обработчик для правой кнопки мыши на сообщения
document.addEventListener('DOMContentLoaded', () => {
    const messagesList = document.getElementById('messages-list');
    if (messagesList) {
        messagesList.addEventListener('contextmenu', (event) => {
            const messageCard = event.target.closest('.message-card');
            if (messageCard) {
                const messageId = messageCard.dataset.messageId;
                const isAuthor = messageCard.classList.contains('self'); // Проверка авторства
                showContextMenu(event, messageId, isAuthor);
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const textarea = document.getElementById('text');

    textarea.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); // Предотвращаем добавление новой строки
            document.getElementById('send-message-form').dispatchEvent(new Event('submit', { cancelable: true }));
        } else if (event.key === 'Enter' && event.shiftKey) {
            // Позволяем добавить новую строку
        }
    });
});
document.addEventListener('DOMContentLoaded', () => {
    const attachBtn = document.getElementById('attach-btn');
    const fileInput = document.getElementById('picture');
    const imagePreview = document.getElementById('image-preview');

    attachBtn.addEventListener('click', () => {
        fileInput.click(); // Имитируем клик по скрытому полю выбора файла
    });

    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.src = e.target.result;
                imagePreview.style.display = 'block'; // Показываем миниатюру
            };
            reader.readAsDataURL(file);
        }
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('image-modal');
    const modalImage = document.getElementById('modal-image');
    const closeModal = document.getElementById('close-modal');

    // Обработчик клика по изображению в сообщении
    document.getElementById('messages-list').addEventListener('click', (event) => {
        if (event.target.tagName === 'IMG') {
            modalImage.src = event.target.src;
            modal.style.display = 'block';
        }
    });

    // Закрытие модального окна при клике на крестик
    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Закрытие модального окна при клике вне изображения
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});

document.addEventListener('DOMContentLoaded', loadChats);