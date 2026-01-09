DOCKER_NAME=seismic-ai

docker rmi $DOCKER_NAME -f

if [ $# == 0 ]
then
    docker build -t $DOCKER_NAME . 
fi

if [ $# == 1 ]
then
    docker build $1 -t $DOCKER_NAME . 
fi
