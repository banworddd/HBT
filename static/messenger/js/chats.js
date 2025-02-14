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

        // Separate users with chats and without chats
        const usersWithChats = data.filter(user => user.is_chat);
        const usersWithoutChats = data.filter(user => !user.is_chat);

        // Display users with chats first
        usersWithChats.forEach(user => {
          let listItem = document.createElement('li');
          let link = document.createElement('a');
          link.href = `/chat/${user.chat_id}/`;

          const messageText = user.last_chat_message_text ? user.last_chat_message_text : "сообщений еще нет";
          const messageTime = user.last_chat_message_time ? `(${new Date(user.last_chat_message_time).toLocaleString()})` : '';

          link.textContent = `${user.username} - ${messageText} ${messageTime}`;

          listItem.appendChild(link);
          chatItems.appendChild(listItem);
        });

        // Display users without chats
        usersWithoutChats.forEach(user => {
          let listItem = document.createElement('li');
          let link = document.createElement('a');
          link.href = `#`; // Placeholder link
          link.textContent = user.username;

          // Add click event to check for existing chat or create a new one
          link.addEventListener('click', function (event) {
            event.preventDefault();
            checkOrCreateChat(user.username);
          });

          listItem.appendChild(link);
          chatItems.appendChild(listItem);
        });
      })
      .catch(error => console.error('Error fetching search results:', error));
  }

  // Function to check for existing chat or create a new one
  function checkOrCreateChat(searchedUsername) {
    fetch(`/api/chats/?user=${username}`)
      .then(response => response.json())
      .then(data => {
        let chat = data.find(c => !c.is_group && (c.username1 === searchedUsername || c.username2 === searchedUsername));
        if (chat) {
          window.location.href = `/chat/${chat.id}/`;
        } else {
          createNewChat(searchedUsername);
        }
      })
      .catch(error => console.error('Error checking chat existence:', error));
  }

  // Function to create a new chat
  function createNewChat(searchedUsername) {
    // Implement the logic to create a new chat with the searched user
    // This might involve making a POST request to your API to create a new chat
    console.log(`Creating new chat with ${searchedUsername}`);
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
