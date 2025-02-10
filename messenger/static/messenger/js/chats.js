document.addEventListener('DOMContentLoaded', function() {
  const username = document.getElementById('chats-list').dataset.username;
  const apiUrl = `http://localhost:8000/api/chats/?user=${username}`;

  fetch(apiUrl)
    .then(response => response.json())
    .then(data => {
      const chatsList = document.getElementById('chats-list');
      data.forEach(chat => {
        const listItem = document.createElement('li');
        listItem.innerHTML = `
          <strong>ID:</strong> ${chat.id}<br>
          <strong>Is Group:</strong> ${chat.is_group}<br>
          ${chat.is_group ? `
            <strong>Name:</strong> ${chat.name}<br>
            <strong>Users:</strong> ${chat.users.join(", ")}<br>
            <strong>Admins:</strong> ${chat.admins.join(", ")}<br>
          ` : `
            <strong>User 1:</strong> ${chat.user_1}<br>
            <strong>User 2:</strong> ${chat.user_2}<br>
          `}
          <strong>Last Message Time:</strong> ${chat.last_message_time}<br>
        `;
        chatsList.appendChild(listItem);
      });
    })
    .catch(error => console.error('Error fetching chats:', error));
});