document.addEventListener('DOMContentLoaded', function () {
    const chatsList = document.getElementById('chat-items');
    const username = document.getElementById('chats-list').dataset.username;

    // Функция для загрузки чатов
    async function loadChats() {
        try {
            const response = await fetch(`/api/messenger/chats/?user=${username}`);
            if (!response.ok) {
                throw new Error('Ошибка при загрузке чатов');
            }
            const chats = await response.json();
            renderChats(chats);
        } catch (error) {
            console.error('Ошибка:', error);
        }
    }

    // Функция для отображения чатов
    function renderChats(chats) {
        chatsList.innerHTML = ''; // Очищаем список перед добавлением новых элементов

        chats.forEach(chat => {
            const chatItem = document.createElement('li');
            chatItem.className = 'chat-item';

            // Определяем название чата
            let chatName = '';
            if (chat.is_group) {
                chatName = chat.name || 'Групповой чат';
            } else {
                chatName = chat.username2 || chat.username1 || 'Личный чат';
            }

            // Определяем последнее сообщение
            const lastMessage = chat.last_message_text ? `
                <div class="last-message">
                    <p>${chat.last_message_text}</p>
                    <small>${new Date(chat.last_message_time).toLocaleString()}</small>
                </div>
            ` : '<div class="last-message"><p>Нет сообщений</p></div>';

            // Создаем HTML для элемента чата
            chatItem.innerHTML = `
                <div class="chat-info">
                    <h3>${chatName}</h3>
                    ${lastMessage}
                </div>
            `;

            // Добавляем обработчик клика для перехода к чату
            chatItem.addEventListener('click', () => {
                window.location.href = `/chat/${chat.id}/`; // Замени на свой URL для чата
            });

            chatsList.appendChild(chatItem);
        });
    }

    // Загружаем чаты при загрузке страницы
    loadChats();
});