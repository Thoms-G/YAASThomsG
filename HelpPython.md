# Help about Python commands

## Start a new app
```{shell}
...\> py manage.py startapp <NAME_OF_APP>
```

## Create tables in DB
Include an application
```{shell}
...\> py manage.py makemigrations <NAME_OF_APP>
```

Create the tables
```{shell}
...\> py manage.py migrate
```

## Creation of the superuser (admin)
```{shell}
...\> py manage.py createsuperuser
```