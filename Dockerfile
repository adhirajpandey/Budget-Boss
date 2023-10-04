FROM python:3-alpine3.15

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 80

CMD gunicorn --bind 0.0.0.0:80 --log-level=debug wsgi:app