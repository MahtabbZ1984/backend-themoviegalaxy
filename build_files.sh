pip install -r requirements.txt
python manage.py makemigrations --noinput
python manage.py migrate
python manage.py collectstatic --noinput
