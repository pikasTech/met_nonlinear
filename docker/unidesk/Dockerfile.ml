FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/nvidia/cuda:11.2.2-cudnn8-runtime-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn \
    PYTHONUNBUFFERED=1 \
    TF_FORCE_GPU_ALLOW_GROWTH=true \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64:${LD_LIBRARY_PATH}

RUN sed -i 's|http://archive.ubuntu.com/ubuntu/|https://mirrors.aliyun.com/ubuntu/|g; s|http://security.ubuntu.com/ubuntu/|https://mirrors.aliyun.com/ubuntu/|g' /etc/apt/sources.list || true \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        python3 \
        python3-dev \
        python3-distutils \
        python3-pip \
    && ln -sf /usr/bin/python3 /usr/local/bin/python \
    && ln -sf /usr/bin/pip3 /usr/local/bin/pip \
    && python -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    && python -m pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn \
    && python -m pip install --no-cache-dir --upgrade pip==23.3.2 setuptools==68.2.2 wheel==0.41.3 -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN cat > /tmp/runtime-requirements.txt <<'EOF_REQ'
tensorflow==2.6.0
keras==2.6.0
protobuf==3.20.0
numpy==1.19.5
matplotlib==3.6.3
pandas==1.3.5
plotly==5.18.0
scikit-learn==1.0.2
tqdm==4.66.4
scipy==1.7.3
keyboard==0.13.5
portalocker==2.8.2
PyYAML==6.0.1
scienceplots==2.1.1
adjustText==0.8
sympy==1.12
openpyxl==3.1.2
EOF_REQ
RUN python -m pip install --no-cache-dir -r /tmp/runtime-requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /workspace/met_nonlinear
CMD ["python", "cli.py", "--help"]
