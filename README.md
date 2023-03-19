# dylive

celery -A app.task.tasks worker --loglevel=info 
celery -A app.task.tasks beat --loglevel=info