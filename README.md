## Homework Bot

### Автор: 
Алаткин Александр

### Описание:
Telegram bot для получение статуса ревью домашней работы на Яндекс Практикуме.

Реализовано периодическое пингование API сервиса Яндекс Практикума, и уведомление сообщением от бота в Telegram в случае изменения статуса ревью домашней работы.

### Использующиеся технологии:
```
Python 3.9
python-telegram-bot 13.7
```

### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/BulimicMimic/hw05_final
```

```
cd yatube
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```


Найти и активировать в телеграме бота:
```
https://t.me/review_inside_bot
```

Запустить проект из директории с проектом:

```
python3 homework.py
```
