# Outletter

## Technology Stack
This is a list of mostly used technologies and libraries that are used in Outletter project:

- [Python](https://www.python.org/): Python is an interpreted high-level programming language for general-purpose programming.

- [Django](https://www.djangoproject.com/): Django is a high-level Python Web framework that encourages rapid development and clean, pragmatic design.

- [Tensorflow](https://www.tensorflow.org/): Tensorflow is a ML framework specifically for Neural Network purposes.

- [Scikit](https://scikit-learn.org/stable/): Scikit is an ML library for many tasks including performance metrics.

- [Open-CV](https://opencv.org/): Open-CV is usually used for image processing purposes.

## DevOps
- Docker, Docker Compose

## Installation
We use docker to run the project.

[Download Docker](https://www.docker.com/community-edition)

Docker can't help for some devices. If the project does not work with Docker, Docker Toolbox will help you.

[Download Docker Toolbox](https://docs.docker.com/toolbox/toolbox_install_windows/#step-2-install-docker-toolbox)

Install Nvidia Container Toolkit for GPU usage for Tensorflow although you wont be able to use gpu with the ./do.sh script.

[Download Nvidia Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker)

## Without GPU

## Running django

```bash
$ ENV=DEV ./do.sh start
```

## Help will show all possible commands

```bash
$ ENV=DEV ./do.sh help
```

## Stopping django /logs
```bash
$ ./do.sh stop
$ ./do.sh logs
```

## With GPU (USE WITH CAUTION, REQUIRES MANUAL CODE TRANSFER TO CONTAINER. USE WITHOUT GPU FOR NORMAL USAGE)
## Running django

```bash
$ ENV=DEV ./do.sh build
$ make start
$ make migrate
```

## Stopping django
```bash
$ make stop
$ make prune
```

Admin user
```
toni > secret
(localhost:8000/admin/) 
```

## Maintainer
- Mian Usman Naeem Kakakhel <usman.kakakhel@ug.bilkent.edu.tr>
