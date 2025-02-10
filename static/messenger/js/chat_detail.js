document.addEventListener('DOMContentLoaded', function () {
  const chatId = document.getElementById('chat-info').dataset.chatId;
  const messagesListUrl = `/api/chat_messages_list/`;
  const messageForm = document.getElementById('message-form');

  // Получение списка сообщений
  fetch(`${messagesListUrl}?chat_id=${chatId}`)
    .then(response => response.json())
    .then(data => {
      const messagesList = document.getElementById('messages-list');
      data.forEach(message => {
        const listItem = document.createElement('li');
        listItem.innerHTML = `
          <strong>ID:</strong> ${message.id}<br>
          <strong>Text:</strong> ${message.text}<br>
          <strong>Send Time:</strong> ${message.send_time}<br>
          <strong>Status:</strong> ${message.status}<br>
          <strong>Author:</strong> ${message.author_name}<br>
        `;
        messagesList.appendChild(listItem);
      });
    })
    .catch(error => console.error('Error fetching messages:', error));

  // Обработка отправки формы
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
        listItem.innerHTML = `
          <strong>ID:</strong> ${data.id}<br>
          <strong>Text:</strong> ${data.text}<br>
          <strong>Send Time:</strong> ${data.send_time}<br>
          <strong>Status:</strong> ${data.status}<br>
          <strong>Author:</strong> ${data.author_name}<br>
        `;
        messagesList.appendChild(listItem);
        messageForm.reset();
      })
      .catch(error => {
        console.error('Error sending message:', error);
        alert('Failed to send message. Please check the form and try again.');
      });
  });

  // Функция для получения CSRF-токена из куки
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
