FROM python:3.11

ENV DJANGO_SETTINGS_MODULE=bik31ProcessTask.settings.production

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y default-mysql-client

ENV MYSQL_ROOT_PASSWORD=root
ENV MYSQL_DATABASE=bik31ProcessTaskDb
ENV MYSQL_USER=itcomsqluser
ENV MYSQL_PASSWORD=CR0504slpot!a

EXPOSE 8000
EXPOSE 3306

CMD ["sh", "-c", "service mysql start && python manage.py runserver 0.0.0.0:8000"]
