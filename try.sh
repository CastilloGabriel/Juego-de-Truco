rm db.sqlite3
python manage.py syncdb --noinput
python manage.py runserver
