FROM python:3.6

RUN apt-get update
ENV PYTHONUNBUFFERED 1
ENV LANG en_US.UTF-8

RUN mkdir /code
WORKDIR /code/
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
