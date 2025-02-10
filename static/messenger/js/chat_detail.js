document.addEventListener('DOMContentLoaded', function() {
  const chatId = document.getElementById('chat-info').dataset.chatId;
  const chatInfoUrl = `http://localhost:8000/api/chat_info/${chatId}/`;
  const messagesListUrl = `http://localhost:8000/api/chat_messages_list/?chat_id=${chatId}`;

  // Получение информации о чате
  fetch(chatInfoUrl)
    .then(response => response.json())
    .then(data => {
      const chatInfoDiv = document.getElementById('chat-info');
      chatInfoDiv.innerHTML = `
        <strong>ID:</strong> ${data.id}<br>
        <strong>Is Group:</strong> ${data.is_group}<br>
        ${data.is_group ? `
          <strong>Name:</strong> ${data.name}<br>
        ` : ''}
        <strong>Last Message Time:</strong> ${data.last_message_time}<br>
        ${data.is_group ? '' : `
          <strong>User 1:</strong> ${data.user_1}<br>
          <strong>User 2:</strong> ${data.user_2}<br>
        `}
      `;
    })
    .catch(error => console.error('Error fetching chat info:', error));

  // Получение списка сообщений
  fetch(messagesListUrl)
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
          <strong>Author:</strong> ${message.author}<br>
        `;
        messagesList.appendChild(listItem);
      });
    })
    .catch(error => console.error('Error fetching messages:', error));
});