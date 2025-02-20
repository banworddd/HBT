document.addEventListener('DOMContentLoaded', function () {
  const chatInfo = document.getElementById('chat-info');
  const chatId = chatInfo.dataset.chatId;
  const currentUsername = chatInfo.dataset.username; // Имя текущего пользователя
  const messagesListUrl = `/api/messenger/chat_messages_list/`;
  const messageForm = document.getElementById('message-form');

  // Загрузка сообщений
  fetch(`${messagesListUrl}?chat_id=${chatId}`)
    .then(response => response.json())
    .then(data => {
      data.forEach(message => {
        addMessageToDOM(message);
      });
    })
    .catch(error => console.error('Error fetching messages:', error));

  // Отправка нового сообщения
  messageForm.addEventListener('submit', function (event) {
    event.preventDefault();
    const textInput = document.getElementById('message-text');
    const imageInput = document.getElementById('message-image');

    if (!textInput.value.trim()) {
      alert('Message text cannot be empty.');
      return;
    }

    const formData = new FormData();
    formData.append('text', textInput.value);
    formData.append('chat', chatId);
    if (imageInput.files[0]) {
      formData.append('picture', imageInput.files[0]);
    }

    fetch(messagesListUrl, {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
      },
      credentials: 'same-origin',
    })
      .then(response => response.json())
      .then(data => {
        console.log('Message sent:', data);
        addMessageToDOM(data); // Добавляем новое сообщение в DOM
        loadReactions(data.id); // Загружаем реакции для нового сообщения
      })
      .catch(error => console.error('Error sending message:', error));
  });

  // Функция для добавления сообщения в DOM
  function addMessageToDOM(message) {
    const messagesList = document.getElementById('messages-list');
    const listItem = document.createElement('li');
    listItem.dataset.messageId = message.id;
    listItem.innerHTML = `
      <strong>ID:</strong> ${message.id}<br>
      <strong>Text:</strong> <span class="message-text">${message.text}</span><br>
      <strong>Send Time:</strong> ${message.send_time}<br>
      <strong>Status:</strong> ${message.status}<br>
      <strong>Author:</strong> ${message.author_name}<br>
      <div class="reactions" data-message-id="${message.id}"></div>
    `;

    // Добавляем кнопки редактирования и удаления (только если они существуют)
    if (message.author_name === currentUsername) {
      const editButton = document.createElement('button');
      editButton.textContent = 'Редактировать';
      editButton.classList.add('edit-button');
      editButton.dataset.messageId = message.id;
      editButton.addEventListener('click', function () {
        const messageTextElement = listItem.querySelector('.message-text');
        const currentText = messageTextElement.textContent;
        const newText = prompt('Введите новый текст сообщения:', currentText);
        if (newText !== null && newText.trim() !== '') {
          updateMessage(message.id, newText.trim());
        }
      });
      listItem.appendChild(editButton);
    }

    const deleteButton = document.createElement('button');
    deleteButton.textContent = 'Удалить';
    deleteButton.classList.add('delete-button');
    deleteButton.dataset.messageId = message.id;
    deleteButton.addEventListener('click', function () {
      deleteMessage(message.id);
    });
    listItem.appendChild(deleteButton);

    messagesList.appendChild(listItem);
    loadReactions(message.id); // Загружаем реакции для сообщения
  }

  // Остальные функции остаются без изменений...

  // 🔹 Функция загрузки реакций
  function loadReactions(messageId) {
    fetch(`/api/messenger/message_reactions/?message_id=${messageId}`)
      .then(response => response.json())
      .then(data => {
        const reactionsDiv = document.querySelector(`.reactions[data-message-id="${messageId}"]`);
        if (!reactionsDiv) return;
        reactionsDiv.innerHTML = '';

        const reactionCounts = {};
        const userReactions = new Set();

        data.forEach(reaction => {
          reactionCounts[reaction.reaction] = (reactionCounts[reaction.reaction] || 0) + 1;
          if (reaction.author === getCurrentUserId()) {
            userReactions.add(reaction.reaction);
          }
        });

        ['L', 'H', 'D'].forEach(reaction => {
          const count = reactionCounts[reaction] || 0;
          const reactionWrapper = document.createElement('div');
          reactionWrapper.style.display = 'inline-flex';
          reactionWrapper.style.alignItems = 'center';
          reactionWrapper.style.marginRight = '8px';

          const countSpan = document.createElement('span');
          countSpan.textContent = count > 0 ? `${count} ` : '';
          countSpan.style.marginRight = '4px';

          const button = document.createElement('button');
          button.textContent = reactionEmoji(reaction);
          button.classList.add('reaction-button');
          button.dataset.messageId = messageId;
          button.dataset.reaction = reaction;
          button.addEventListener('click', () => toggleReaction(messageId, reaction));

          if (userReactions.has(reaction)) {
            button.style.backgroundColor = '#FFD700';
            button.style.borderRadius = '5px';
          } else {
            button.style.backgroundColor = '';
          }

          reactionWrapper.appendChild(countSpan);
          reactionWrapper.appendChild(button);
          reactionsDiv.appendChild(reactionWrapper);
        });
      })
      .catch(error => console.error('Error loading reactions:', error));
  }

  // 🔹 Функция добавления/удаления реакции
  function toggleReaction(messageId, reaction) {
    fetch(`/api/messenger/message_reactions/?message_id=${messageId}`)
      .then(response => response.json())
      .then(data => {
        const existingReaction = data.find(r => r.author === getCurrentUserId() && r.reaction === reaction);

        if (existingReaction) {
          deleteReaction(existingReaction.id, messageId); // Удаляем реакцию, если она уже есть
        } else {
          addReaction(messageId, reaction); // Добавляем новую реакцию
        }
      })
      .catch(error => console.error('Error checking reactions:', error));
  }

  // 🔹 Добавление реакции
  function addReaction(messageId, reaction) {
    fetch(`/api/messenger/message_reactions/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/json',
      },
      credentials: 'same-origin',
      body: JSON.stringify({
        author: getCurrentUserId(),  // Добавляем ID текущего пользователя
        reaction: reaction,          // Правильное поле
        message: messageId           // ID сообщения
      }),
    })
      .then(response => response.json())
      .then(() => {
        loadReactions(messageId);
      })
      .catch(error => console.error('Error adding reaction:', error));
  }

  // 🔹 Удаление реакции
  function deleteReaction(reactionId, messageId) {
    fetch(`/api/messenger/message_reactions_detail/${reactionId}/`, {
      method: 'DELETE',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
      },
      credentials: 'same-origin',
    })
      .then(() => {
        loadReactions(messageId); // Обновляем UI
      })
      .catch(error => console.error('Error deleting reaction:', error));
  }

  // 🔹 Преобразование кодов реакций в эмодзи
  function reactionEmoji(reaction) {
    return { 'L': '👍', 'H': '❤️', 'D': '👎' }[reaction] || '';
  }

  // 🔹 Функция для получения CSRF-токена
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
});

function getCurrentUserId() {
  return parseInt(document.getElementById('chat-info').dataset.userId, 10);
}
