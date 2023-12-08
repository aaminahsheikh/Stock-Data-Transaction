FROM python:3.11.4

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=StockData.settings

RUN apt-get update && apt-get

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip

RUN rm -rf /root/.cache/pip
RUN pip install -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]