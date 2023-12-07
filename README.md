# Stock-Data-Transaction
This project will be handling StockData and Transactions.
### Clone Repository:
```
git clone https://github.com/aaminahsheikh/Stock-Data-Transaction.git
```
### Create virtual environment
```
python3 virtualenv env
```
### Activate virtual environment
```
source env/bin/activate
```
### Install requirements
```
pip install -r requirements.txt
```
### Create .env file
```
cp .env .env.sample
```
Add values of requirement variables in .env file.
### Upgrade migrations
```
python3 manage.py migrate
```
### How do I run the server?
```
python3 manage.py runserver
```
### How do I run the celery worker?
```
celery -A stock_home.celery_services.celery_services.celery_app worker --loglevel=INFO
```
### How do I run the celery flower?
```
celery -A stock_home.celery_services.celery_services.celery_app flower
```