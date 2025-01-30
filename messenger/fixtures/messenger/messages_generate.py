import json
from datetime import datetime, timedelta

# Параметры для генерации данных
chat_id = 13
author_ids = [17, 1]
status = 'S'
picture = None
send_time_base = datetime.now()
num_messages = 5000

# Генерация данных
messages = []
for i in range(num_messages):
    author_id = author_ids[i % len(author_ids)]
    send_time = send_time_base + timedelta(minutes=i)
    message = {
        "model": "messenger.message",
        "pk": i + 1,
        "fields": {
            "text": f"Message text {i + 1}",
            "author": author_id,
            "chat": chat_id,
            "send_time": send_time.isoformat(),
            "status": status,
            "picture": picture,
            "is_deleted": False
        }
    }
    messages.append(message)

# Запись данных в файл фикстуры
with open('messages.json', 'w') as f:
    json.dump(messages, f, indent=4)
