FROM python:3.8-slim-buster

WORKDIR /runtime
COPY requirements.txt /runtime
RUN pip3 install -r requirements.txt

COPY . /runtime
EXPOSE 8000

CMD gunicorn --bind 0.0.0.0:8000 calendarapi:app