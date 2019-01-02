# Benchmark Verification

## Requirements

- Microsoft Windows 10
- Python 3.7

## Preparation

### Virtual environments

#### Create

```
python -m pip install virtualenv
python -m venv venv
```

#### Use

```
venv\Scripts\activate.bat
```

#### Install python requirements

```
pip install -r requirements.txt
```

### Import benchmark information

#### Model migrates

```
python manage.py makemigrations benchmarks scans tasks
python manage.py migrate
```

#### Import benchmark json

```
python manage.py loaddata benchmark_cis_microsoft_office_2016.json
```

### Create superuser

```
python manage.py createsuperuser
```

## Test

```
python manage.py test
```

## Run

```
python manage.py runserver
``` 
