# Проект Foodgram

![example workflow](https://github.com/AlisaLi1981/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Описание 

Сайт адептов кулинарного искусства и просто любителей вкусно готовить. Здесь можно найти рецепты различных блюд и поделиться своими.

## Стек технологий
- Python
- Django
- Djangorestframework
- Djoser
- Docker
- Nginx
- Gunicorn
- PostgreSQL

##  Cсылка на развернутый проект:
- https://my-foodgram.ddns.net/

## Запуск проекта

Клонировать репозиторий:

```
git clone <адрес репозитория>
```

Создать на сервере директорию для проекта, перейти в нее:

```
mkdir <имя директрии>
cd <имя директрии>
```

Запустить проект на сервере с помощью docker-compose:

```
docker compose -f docker-compose.yml up --build -d
```

Выполнить миграции:

```
docker compose -f docker-compose.yml exec backend python manage.py migrate
```

Собрать статику:

```
docker compose -f docker-compose.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.yml exec backend cp -r /app/static_backend/. /backend_static/static/
```

Загрузить базу данных ингредиентов:

```
docker compose -f docker-compose.yml exec backend python manage.py import_csv
```

## .env

В корне проекта создать файл .env и прописать в него свои данные.

Пример:

```
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
```

### Важно:
Файл docker-compose.yml используется для первичного запуска приложения именно из файлов репозитория и в процессе отладки (сборка образов происходит каждый раз). Для запусков на боевом сервере рекомендуется использовать файл docker-compose.production.yml (будут использоваться собранные образы из Docker Hub).

## Автор

Дарья Леонова [GitHub](https://github.com/AlisaLi1981)
