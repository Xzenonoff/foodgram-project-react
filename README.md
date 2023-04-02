# praktikum_new_diplom
![example workflow](https://github.com/Xzenonoff/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
### Как запустить проект:

```bash
docker-compose up

docker-compose exec backend python manage.py makemigrations

docker-compose exec backend python manage.py migrate

docker-compose exec backend python manage.py createsuperuser

docker-compose exec backend python manage.py collectstatic --no-input
```

### Шаблон наполнения .env
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
