document.addEventListener('DOMContentLoaded', function () {
  const chatsListElement = document.getElementById('chats-list');
  const username = chatsListElement.dataset.username;
  const chatItems = document.getElementById('chat-items');
  const searchInput = document.getElementById('search-input');

  // Elements for creating a group chat
  const createGroupChatBtn = document.getElementById('create-group-chat-btn');
  const createGroupChatForm = document.getElementById('create-group-chat-form');
  const cancelCreateGroupBtn = document.getElementById('cancel-create-group');
  const groupUsersSelect = document.getElementById('group-users');
  const groupChatForm = document.getElementById('group-chat-form');
  const groupNameInput = document.getElementById('group-name');
  const groupAvatarInput = document.getElementById('group-avatar');

  // Function to fetch and display chats (unchanged)
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

  // Function to fetch contacts for group chat creation
  function fetchContacts() {
    fetch(`/api/contacts/?user=${username}`)  // Endpoint for fetching user contacts
      .then(response => response.json())
      .then(data => {
        // Clear existing options
        groupUsersSelect.innerHTML = '';

        // Add contacts to the select dropdown
        data.forEach(contact => {
          const option = document.createElement('option');
          option.value = contact.id;  // Assuming contact has an id field
          option.textContent = contact.username;
          groupUsersSelect.appendChild(option);
        });
      })
      .catch(error => console.error('Error fetching contacts:', error));
  }

  // Show group chat creation form
  createGroupChatBtn.addEventListener('click', function() {
    createGroupChatForm.style.display = 'block';
    fetchContacts();  // Fetch contacts when form is displayed
  });

  // Hide form on cancel
  cancelCreateGroupBtn.addEventListener('click', function() {
    createGroupChatForm.style.display = 'none';
  });

  // Handle form submission for creating group chat
  groupChatForm.addEventListener('submit', function(event) {
    event.preventDefault();

    const groupName = groupNameInput.value;
    const groupUsers = Array.from(groupUsersSelect.selectedOptions).map(option => option.value);
    const groupAvatar = groupAvatarInput.files[0];

    const formData = new FormData();
    formData.append('group_name', groupName);
    formData.append('users', JSON.stringify(groupUsers));
    formData.append('avatar', groupAvatar);

    // POST request to create the group chat
    fetch('/api/chats/create_group/', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        createGroupChatForm.style.display = 'none';
        fetchChats();  // Refresh the chat list
      } else {
        console.error('Error creating group chat:', data.error);
      }
    })
    .catch(error => console.error('Error creating group chat:', error));
  });

  // Initial load of chats
  fetchChats();
    // Event listener for search input (unchanged)
  searchInput.addEventListener('input', function () {
    const query = searchInput.value.trim();
    if (query) {
      fetchSearchResults(query);
    } else {
      fetchChats();
    }
  });

  // Function to fetch and display search results (unchanged)
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

  // Function to check or create chat (unchanged)
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

  // Function to create a new chat (unchanged)
  function createNewChat(searchedUsername) {
    // Implement the logic to create a new chat with the searched user
    // This might involve making a POST request to your API to create a new chat
    console.log(`Creating new chat with ${searchedUsername}`);
  }
});
