# Help about Python commands

## Start a new app
```{shell}
...\> py manage.py startapp <NAME_OF_APP>
```

## Database
### Create tables in DB
Include an application
```{shell}
...\> py manage.py makemigrations <NAME_OF_APP>
```

Create the tables
```{shell}
...\> py manage.py migrate
```

### Delete DB
* Delete the sqlite database file (often **db.sqlite3**) in your django project folder
* Delete everything except *__init__.py* file from migration folder in all django apps
* Make changes in your models (models.py).
* Run the command `py manage.py makemigrations <NAME_OF_APP>`
* Then run the command `py manage.py migrate`.
* Then create again superuser

## Creation of the superuser (admin)
```{shell}
...\> py manage.py createsuperuser
```