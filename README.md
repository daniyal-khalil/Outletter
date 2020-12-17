# Outletter

## Technology Stack
This is a list of mostly used technologies and libraries that are used in Outletter project:

- [Python](https://www.python.org/): Python is an interpreted high-level programming language for general-purpose programming.

- [Django](https://www.djangoproject.com/): Django is a high-level Python Web framework that encourages rapid development and clean, pragmatic design.

## DevOps
- Docker, Docker Compose

## Installation
We use docker to run the project.

[Download Docker](https://www.docker.com/community-edition)

Docker can't help for some devices. If the project does not work with Docker, Docker Toolbox will help you.

[Download Docker Toolbox](https://docs.docker.com/toolbox/toolbox_install_windows/#step-2-install-docker-toolbox)

## Running django

```bash
$ ENV=DEV ./do.sh start
```
## Run the db initialization for initializing 
## dummy data as well as a user for localhost:8000/admin

```bash
$ ENV=DEV ./do.sh initdb
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

Admin user
```
toni > secret
(localhost:8000/admin/) 
```

## Maintainer
- Mian Usman Naeem Kakakhel <usman.kakakhel@ug.bilkent.edu.tr>
