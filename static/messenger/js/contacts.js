document.addEventListener('DOMContentLoaded', async function() {
    const contactsContainer = document.getElementById('contacts-container');
    const userId = contactsContainer.dataset.userId;
    const apiUrl = `/api/contacts/${userId}/`;
    const chatCreateApiUrl = '/api/chat_create/';

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error('Ошибка сети');
        }
        const data = await response.json();
        const contactsList = document.getElementById('contacts-list');

        data.contacts.forEach((contact, index) => {
            const listItem = document.createElement('li');
            const chatId = data.chat_id[index];
            const contactUserId = data.contact_ids[index]; // Получаем ID контакта из списка
            listItem.textContent = `${contact}: `;

            const chatLink = document.createElement('a');
            chatLink.href = chatId !== null ? `/chat/${chatId}/` : '#';
            chatLink.textContent = 'Перейти в чат';

            chatLink.addEventListener('click', async function(event) {
                if (chatId === null) {
                    event.preventDefault();
                    try {
                        const createChatResponse = await fetch(chatCreateApiUrl, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCookie('csrftoken'), // Добавьте CSRF токен для безопасности
                            },
                            body: JSON.stringify({
                                user_1: userId,
                                user_2: contactUserId,
                            }),
                        });

                        if (createChatResponse.ok) {
                            const newChatData = await createChatResponse.json();
                            window.location.href = `/chat/${newChatData.id}/`;
                        } else {
                            throw new Error('Ошибка при создании чата');
                        }
                    } catch (error) {
                        console.error('Ошибка:', error);
                    }
                }
            });

            listItem.appendChild(chatLink);
            contactsList.appendChild(listItem);
        });
    } catch (error) {
        console.error('Ошибка при получении данных:', error);
    }
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && name) {
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

