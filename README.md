# liftes-bot

<details><summary>В разработке</summary>

- [x] Исправить функцию generate_new_key() 
- [x] Замена рекурсивных вызовов функция на циклы
- [x] Замена моно кода на модульную структуру 
- [x] Добавить ограничение на число попыток сгенирировать ключ
- [ ] Speach to text
- [ ] API для вывода ошибок

</details>


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

- Генерация ключа (необходима для шифровки данных).
  ```shell
  python3 main.py --key
  ```

- Создание базы данных:
  ```shell
  python3 main.py --create_table
  ```
