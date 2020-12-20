FROM tensorflow/tensorflow:latest-gpu
# RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get update
RUN apt-get install libgl1-mesa-glx -y
ENV PYTHONUNBUFFERED 1
ENV LANG en_US.UTF-8

RUN mkdir /code
WORKDIR /code/
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
