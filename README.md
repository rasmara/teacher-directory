# Teachers Directory

Django directory for searching and creating new teachers record

#### Detailed description for project attached[here in PDF](https://github.com/rasmara/teachers-directory/blob/master/tech_test_data/Tech%20Test.pdf) 

## Installation

### Pre-requisites

- **python 3.8**
- **pipenv**


### Clone the repo

```bash

git clone https://github.com/rasmara/teachers-directory.git

cd teachers-directory

```

### Install dependencies


```bash

pipenv install

pipenv shell

```
### Run migrations

```bash

python manage.py migrate --skip-checks

```

### Create superuser


```bash

export DJANGO_SUPERUSER_PASSWORD=admin123
python manage.py createsuperuser --noinput --username admin --skip-checks --email admin@admin.com

```

### Run server

```bash

python manage.py runserver

```

## Installation

- goto **http://localhost:8000/**
- Login credentials:
  - username: **admin** 
  - password: **admin123** 
- Login to **import data in bulk** / **add new record** / **view all records**
- Once data added, use search for  filter against records (first letter of last name or subject name)
- max 5 subjects is alloted for each teachers.
- Click on the view to get detailed profile view
