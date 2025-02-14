document.addEventListener('DOMContentLoaded', function () {
  const chatsListElement = document.getElementById('chats-list');
  const username = chatsListElement.dataset.username;
  const chatItems = document.getElementById('chat-items');
  const searchInput = document.getElementById('search-input');

  // Function to fetch and display chats
  function fetchChats() {
    fetch(`/api/chats/?user=${username}`)
      .then(response => response.json())
      .then(data => {
        chatItems.innerHTML = ''; // Clear previous chat items
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
  }

  // Function to fetch and display search results
  function fetchSearchResults(query) {
    fetch(`/api/users_search/?user=${query}`)
      .then(response => response.json())
      .then(data => {
        chatItems.innerHTML = ''; // Clear previous chat items
        data.forEach(user => {
          let listItem = document.createElement('li');
          listItem.textContent = user.username;
          chatItems.appendChild(listItem);
        });
      })
      .catch(error => console.error('Error fetching search results:', error));
  }

  // Initial load of chats
  fetchChats();

  // Event listener for search input
  searchInput.addEventListener('input', function () {
    const query = searchInput.value.trim();
    if (query) {
      fetchSearchResults(query);
    } else {
      fetchChats();
    }
  });
});
