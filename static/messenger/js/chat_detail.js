document.addEventListener('DOMContentLoaded', function () {
  const chatInfo = document.getElementById('chat-info');
  const chatId = chatInfo.dataset.chatId;
  const currentUsername = chatInfo.dataset.username; // Имя текущего пользователя
  const messagesListUrl = `/api/chat_messages_list/`;
  const messageForm = document.getElementById('message-form');

  // Загрузка сообщений
  fetch(`${messagesListUrl}?chat_id=${chatId}`)
    .then(response => response.json())
    .then(data => {
      const messagesList = document.getElementById('messages-list');
      data.forEach(message => {
        const listItem = document.createElement('li');
        listItem.dataset.messageId = message.id;
        listItem.innerHTML = `
          <strong>ID:</strong> ${message.id}<br>
          <strong>Text:</strong> <span class="message-text">${message.text}</span><br>
          <strong>Send Time:</strong> ${message.send_time}<br>
          <strong>Status:</strong> ${message.status}<br>
          <strong>Author:</strong> ${message.author_name}<br>
          ${message.author_name === currentUsername ? `<button class="edit-button" data-message-id="${message.id}">Редактировать</button>` : ''}
          <button class="delete-button" data-message-id="${message.id}">Удалить</button>
        `;
        messagesList.appendChild(listItem);

        // Обработчики для кнопок редактирования (если они есть)
        if (message.author_name === currentUsername) {
          listItem.querySelector('.edit-button').addEventListener('click', function () {
            const messageId = this.dataset.messageId;
            const messageTextElement = this.closest('li').querySelector('.message-text');
            const currentText = messageTextElement.textContent;

            const newText = prompt('Введите новый текст сообщения:', currentText);
            if (newText !== null && newText.trim() !== '') {
              updateMessage(messageId, newText.trim());
            }
          });
        }

        // Обработчики для кнопок удаления
        listItem.querySelector('.delete-button').addEventListener('click', function () {
          const messageId = this.dataset.messageId;
          deleteMessage(messageId);
        });
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
      .then(response => {
        if (!response.ok) {
          return response.json().then(errorData => {
            throw new Error(JSON.stringify(errorData));
          });
        }
        return response.json();
      })
      .then(data => {
        const messagesList = document.getElementById('messages-list');
        const listItem = document.createElement('li');
        listItem.dataset.messageId = data.id;
        listItem.innerHTML = `
          <strong>ID:</strong> ${data.id}<br>
          <strong>Text:</strong> <span class="message-text">${data.text}</span><br>
          <strong>Send Time:</strong> ${data.send_time}<br>
          <strong>Status:</strong> ${data.status}<br>
          <strong>Author:</strong> ${data.author_name}<br>
          ${data.author_name === currentUsername ? `<button class="edit-button" data-message-id="${data.id}">Редактировать</button>` : ''}
          <button class="delete-button" data-message-id="${data.id}">Удалить</button>
        `;
        messagesList.appendChild(listItem);

        // Обработчик для новой кнопки редактирования (если она есть)
        if (data.author_name === currentUsername) {
          listItem.querySelector('.edit-button').addEventListener('click', function () {
            const messageId = this.dataset.messageId;
            const messageTextElement = this.closest('li').querySelector('.message-text');
            const currentText = messageTextElement.textContent;

            const newText = prompt('Введите новый текст сообщения:', currentText);
            if (newText !== null && newText.trim() !== '') {
              updateMessage(messageId, newText.trim());
            }
          });
        }

        // Обработчик для новой кнопки удаления
        listItem.querySelector('.delete-button').addEventListener('click', function () {
          const messageId = this.dataset.messageId;
          deleteMessage(messageId);
        });

        messageForm.reset();
      })
      .catch(error => {
        console.error('Error sending message:', error);
        alert('Failed to send message. Please check the form and try again.');
      });
  });

  // Функция для обновления сообщения
  function updateMessage(messageId, newText) {
    const updateUrl = `/api/chat_message_update/${messageId}/`;
    const data = {
      text: newText,
    };

    fetch(updateUrl, {
      method: 'PATCH',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/json',
      },
      credentials: 'same-origin',
      body: JSON.stringify(data),
    })
      .then(response => {
        if (!response.ok) {
          return response.text().then(errorText => {
            throw new Error(errorText);
          });
        }
        return response.json();
      })
      .then(data => {
        const messageTextElement = document.querySelector(`li[data-message-id="${messageId}"] .message-text`);
        if (messageTextElement) {
          messageTextElement.textContent = data.text;
        } else {
          console.error('Message text element not found:', messageId);
        }
      })
      .catch(error => {
        console.error('Error updating message:', error);
        alert('Failed to update message. Please try again.');
      });
  }

  // Функция для удаления сообщения
  function deleteMessage(messageId) {
    const deleteUrl = `/api/chat_message_delete/${messageId}/`;
    const data = {
      text: 'Сообщение удалено',
      chat: chatId,
      is_deleted: true,
      picture: null
    };

    fetch(deleteUrl, {
      method: 'PUT',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/json',
      },
      credentials: 'same-origin',
      body: JSON.stringify(data),
    })
      .then(response => {
        if (!response.ok) {
          return response.text().then(errorText => {
            throw new Error(errorText);
          });
        }
        return response.json();
      })
      .then(data => {
        const messageItem = document.querySelector(`li[data-message-id="${messageId}"]`);
        if (messageItem) {
          messageItem.remove();
        } else {
          console.error('Message item not found:', messageId);
        }
      })
      .catch(error => {
        console.error('Error deleting message:', error);
        alert('Failed to delete message. Please try again.');
      });
  }

  // Функция для получения CSRF-токена
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
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
});