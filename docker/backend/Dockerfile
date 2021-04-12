FROM tensorflow/tensorflow:latest-gpu

RUN apt-get update
RUN apt-get install libgl1-mesa-glx -y
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install opencv-python
RUN pip install torch==1.8.1+cu111 torchvision==0.9.1+cu111 torchaudio==0.8.1 -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install Cython
RUN pip install PyYAML
RUN python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu111/torch1.8/index.html
ENV PYTHONUNBUFFERED 1
ENV LANG en_US.UTF-8

RUN mkdir /code
WORKDIR /code/
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
