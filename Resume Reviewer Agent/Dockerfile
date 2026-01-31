FROM python:latest

RUN apt-get update
RUN apt-get install -y poppler-utils

WORKDIR /app

COPY app/ /app/app/
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD ["python", "-m", "app.main"]
