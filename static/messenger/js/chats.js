document.addEventListener('DOMContentLoaded', function () {
  const chatsListElement = document.getElementById('chats-list');
  const username = chatsListElement.dataset.username;
  const chatItems = document.getElementById('chat-items');

  fetch(`/api/chats/?user=${username}`)
    .then(response => response.json())
    .then(data => {
      data.forEach(chat => {
        let listItem = document.createElement('li');
        let link = document.createElement('a');
        link.href = `/chat/${chat.id}/`;

        const messageText = chat.last_message_text ? chat.last_message_text : "сообщений еще нет";
        const messageTime = chat.last_message_time ? `(${new Date(chat.last_message_time).toLocaleString()})` : '';

        if (chat.is_group) {
          link.textContent = `${chat.name} - ${messageText} ${messageTime}`;
        } else {
          link.textContent = `${chat.username2} - ${messageText} ${messageTime}`;
        }

        listItem.appendChild(link);
        chatItems.appendChild(listItem);
      });
    })
    .catch(error => console.error('Error fetching chat data:', error));
});
