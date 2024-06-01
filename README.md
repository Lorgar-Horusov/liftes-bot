# liftes-bot

## Описание
Этот репозиторий содержит инструкции по созданию и активации виртуального окружения, установке зависимостей и запуску бота.

## Краткая инструкция

### 1. Создание и активация виртуального окружения

#### Linux
```shell
python3 -m venv venv
```
```shell
source venv/bin/activate 
```

#### Windows
```shell
python -m venv venv
```
```shell
venv\Scripts\activate
```

### 2. Установка зависимостей
```shell
pip install -r requirements.txt
```

### 3. Запуск CLI интерфейса

#### Linux
```shell
python3 cli_menu.py
```

#### Windows
```shell
python cli_menu.py
```

### Работа без использования интерфейса

- Запуск Бота:
  ```shell
  python3 main.py --start_bot
  ```

- Генерация соли (необходима для кеширования данных). Внимание: выполняйте команду только один раз, иначе вы потеряете все данные из базы данных:
  ```shell
  python3 main.py --salt
  ```

- Создание базы данных:
  ```shell
  python3 main.py --create_table
  ```
