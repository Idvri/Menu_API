# Menu API.
REST API для работы с меню ресторана. 


### Stack:
- Python 3.10;
- FastAPI;
- PostgreSQL;
- SQLAlchemy;
- Pydantic;
- Docker;
- Pytest.


### Установка и запуск (Docker):
- git clone https://github.com/Idvri/Menu_API.git;
- docker-compose up --build - в первый раз (ждем 1-2 сек. пока БД поднимается);
- docker-compose up;
- docker-compose -f run_tests.yaml up --build - тестирование (Pytest).

### Доступность:
- http://localhost:8000.

### Функционал (http://localhost:8000/docs):
- cоздание меню/подменю/блюда;
- просмотр одного или нескольких меню/подменю/блюд;
- изменение меню/подменю/блюда;
- удаление меню/подменю/блюда.

### Дополнительно:
- в папке "postman" хранятся тесты для данного API, следуйте инструкциям на скриншоте из папки для их запуска.
