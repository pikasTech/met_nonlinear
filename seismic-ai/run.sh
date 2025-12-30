#!/bin/bash

# example:
# bash run.sh -s pikapython.com -p 22000 -t 961e786cc65e4a3a8333167c6557fcde968b2cd8 -r 22089 -k Liang6516. -g --gpus=all

# 解析命令行参数
while getopts ":p:s:t:r:k:g:" opt; do
  case $opt in
    p) frpc_server_port=$OPTARG;;
    s) frpc_server_addr=$OPTARG;;
    t) frpc_token=$OPTARG;;
    r) frpc_remote_port=$OPTARG;;
    k) ssh_password=$OPTARG;;
    g) gpu_option=$OPTARG;;
    \?) echo "Invalid option -$OPTARG" >&2;;
  esac
done

# 打印解析后的命令行参数
echo "frpc_server_port: $frpc_server_port"
echo "frpc_server_addr: $frpc_server_addr"
echo "frpc_token: $frpc_token"
echo "frpc_remote_port: $frpc_remote_port"
echo "ssh_password: $ssh_password"
echo "gpu_option: $gpu_option"

DOCKER_NAME="seismic-ai"
if [ -n "$frpc_remote_port" ]; then
    DOCKER_NAME+="_$frpc_remote_port"
fi

# 打印DOCKER_NAME
echo "DOCKER_NAME: $DOCKER_NAME"

# 检查是否设置了frpc_server_port参数
if [ -n "$frpc_server_port" ]; then
    # 启动frpc
    echo "Starting frpc..."
    docker rm $DOCKER_NAME -f
    echo "Removed existing Docker container $DOCKER_NAME"
    echo "Starting new Docker container $DOCKER_NAME"
    docker run -it --name $DOCKER_NAME \
    --restart always \
    -p 8888:8888 \
    $gpu_option \
    -w /tf \
    -e FRPC_REMOTE_PORT=$frpc_remote_port \
    -e FRPC_SERVER_ADDR=$frpc_server_addr \
    -e FRPC_SERVER_PORT=$frpc_server_port \
    -e FRPC_TOKEN=$frpc_token \
    -e SSH_PASSWORD=$ssh_password \
    seismic-ai \
    bash /etc/start.sh
else
    # 不启动frpc
    echo "frpc_server_port is not set. Skipping frpc startup."
    docker rm $DOCKER_NAME -f
    docker run -it --name $DOCKER_NAME \
    --restart always \
    -p 8888:8888 \
    $gpu_option \
    -w /tf \
    seismic-ai \
    bash /etc/start.sh
fi

