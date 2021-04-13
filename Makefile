start:
	docker network create commnet
	docker run --net commnet --name db -e POSTGRES_USER=outletter -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=outletter -d postgres
	docker run --net commnet --gpus all --name outletter_backend_22 -p 8001:8000 outletter_backend python manage.py runserver 0:8000
	docker exec outletter_backend_22 python manage.py migrate

bash:
	docker network create commnet
	docker run --net commnet --name db -e POSTGRES_USER=outletter -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=outletter -d postgres
	docker run -it --net commnet --gpus all --name outletter_backend_22 -p 8001:8000 outletter_backend ../bin/bash

stop:
	docker stop outletter_backend_22
	docker stop db
	docker network rm commnet

migrate:
	docker exec outletter_backend_22 python manage.py makemigrations
	docker exec outletter_backend_22 python manage.py migrate

prune:
	docker container prune
	# docker image prune 
	docker network prune

copy:
	docker cp . outletter_backend_22:/code