#!/usr/bin/env bash

# settings
PROJECT_NAME="outletter"

# colors
BLUE="\\033[1;34m"
GREEN="\\033[1;32m"
NORMAL="\\033[0;39m"
RED="\\033[1;31m"

print_help() {
    echo -e "${BLUE}Available environments${NORMAL}"
    echo "  - DEV (default)"
    echo "  - PROD"
    echo "  - STAGING"
    echo ""
    echo -e "${BLUE}Available commands${NORMAL}"
    echo -e "  > build [:services]      Build or rebuild services"
    echo -e "  > deploy                 Make deployment for production or staging server"
    echo -e "  > django [:command]      Run Django specific command"
    echo -e "  > docker [:command]      Run a Docker command"
    echo -e "  > logs [:service]        View output from containers"
    echo -e "  > restart [:service]     Restart service"
    echo -e "  > shell                  Open Bash"
    echo -e "  > start [:services]      Create and start containers"
    echo -e "  > status                 List containers"
    echo -e "  > stop [:services]       Stop services"
}

docker_command() {
    command="docker-compose -p ${PROJECT_NAME} -f docker/docker-compose.yml "

    case ${ENV} in
        "PROD")
            file_prefix="prod"
            ;;
        "STAGING")
            file_prefix="staging"
            ;;
        *)
            file_prefix="dev"
            ;;
    esac

    command+="-f docker/docker-compose.${file_prefix}.yml ${@}"
    echo -e "${BLUE}    Command: ${NORMAL}${command}"
    echo -e ""
    eval ${command}
}

build() {
    if [ -z ${1} ]
    then
        docker_command build
    else
        docker_command build ${1}
    fi
}

deploy() {
    case ${ENV} in
        "PROD")
            echo -e "${BLUE}PRODUCTION DEPLOYMENT${NORMAL}"
            ;;
        "STAGING")
            echo -e "${BLUE}STAGING DEPLOYMENT${NORMAL}"
            ;;
        *)
            echo -e "${RED}This command is available only in PRODUCTION and STAGING environments.${NORMAL}"
            exit 1
            ;;
    esac

    echo -e "${BLUE}STEP 1: Activate Python environment.${NORMAL}"
    cd "${HOME}"
    source venv/bin/activate

    echo -e "${BLUE}STEP 3: Prepare backend.${NORMAL}"
    cd "${HOME}/zs/"
    pip install --upgrade pip
    pip install -r requirements.txt
    python manage.py migrate --noinput
    python manage.py compilemessages
    python manage.py collectstatic --noinput

    echo -e "${BLUE}STEP 4: Restart server.${NORMAL}"
    cd "${HOME}"
    sudo /etc/init.d/supervisor restart

    echo -e "${GREEN}Deployment is success.${NORMAL}"
}

django() {
    docker_command run --rm backend-shell python manage.py ${@}
}

docker() {
    docker_command ${@}
}

initdb() {
    case ${ENV} in
        "DEV")
            docker_command run --rm backend-shell python manage.py initdb
            ;;
        *)
            echo -e "${RED}This command is only available in DEV environment.${NORMAL}"
            exit 1
            ;;
    esac
}

logs() {
    docker_command logs -f --tail 50 ${@}
}

restart() {
    if [ -z ${1} ]
    then
        docker_command restart
    else
        docker_command restart ${1}
    fi
}

# runtests() {
#     test_command="'
#         coverage run manage.py test --noinput &&
#         coverage html --skip-covered
#     '"
#     docker_command run --rm backend-shell sh -c ${test_command}
# }

# shell() {
#     if [ -z ${1} ]
#     then
#         service = "backend-shell"
#     else
#         service = ${1}
#     fi
#     docker_command run --rm $service bash
# }

status() {
    docker_command ps
}

start() {
    if [ -z ${1} ]
    then
        docker_command up -d backend
    else
        docker_command up -d ${1}
    fi
}

stop() {
    if [ -z ${1} ]
    then
        docker_command stop
    else
        docker_command stop ${1}
    fi
}

if [ -z ${1} ]
then
    print_help
else
    case ${ENV} in
        "PROD")
            env_str="production"
            ;;
        "STAGING")
            env_str="staging"
            ;;
        *)
            env_str="development"
            ;;
    esac
    echo -e "${BLUE}Environment:${NORMAL} ${env_str}"
    ${@}
fi
