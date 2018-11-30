from celery import Celery

app=Celery()
app.config_from_object('index_celery.config')