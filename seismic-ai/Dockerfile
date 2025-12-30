FROM tensorflow/tensorflow:2.15.0.post1-gpu-jupyter

ADD docker/ubuntu20_sources.list /etc/apt/sources.list
ADD docker/bashrc /root/.bashrc

RUN apt-get update
RUN apt-get install -y git

ADD docker/pip.conf /root/.pip/
RUN pip install --upgrade pip
RUN pip install scikit-learn
RUN pip install matplotlib
RUN pip install pandas
RUN pip install SciencePlots

ADD docker/jupyter_notebook_config.json /root/.jupyter/jupyter_notebook_config.json

RUN apt-get install -y vim
RUN apt-get install -y dvipng texlive-latex-extra texlive-fonts-recommended cm-super
RUN git config --global --add safe.directory /tf/seismic-ai
RUN git config --global user.email "liang6516@outlook.com"
RUN git config --global user.name "lyon"

RUN pip install openpyxl
RUN apt-get install pandoc -y
RUN pip install nbconvert[webpdf]
RUN git config --global --add safe.directory /tf/seismic-ai/lib/met
RUN pip install autopep8
RUN git config --global credential.helper store

RUN apt-get install -y wget openssh-server

# install frpc
RUN cd /root && wget https://gitee.com/Lyon1998/pikapython/attach_files/1420660/download -O frp.tar.gz && \
    tar -xzvf frp.tar.gz && \
    mv frp_0.48.0_linux_amd64/frpc /usr/local/bin/frpc

RUN wget https://gitee.com/Lyon1998/pikapython/attach_files/1455187/download -O clash-linux-amd64-v1.17.0.gz
RUN gunzip clash-linux-amd64-v1.17.0.gz
RUN chmod +x clash-linux-amd64-v1.17.0
RUN mv clash-linux-amd64-v1.17.0 /etc/clash
EXPOSE 7890

RUN mkdir /etc/clash_config
RUN wget https://gitee.com/Lyon1998/pikapython/attach_files/1455209/download -O Country.mmdb
RUN mv Country.mmdb /etc/clash_config
COPY docker/config.yaml /etc/clash_config/config.yaml
ADD docker/sshd_config /etc/ssh/sshd_config
COPY docker/frpc.ini /etc/frpc.ini
COPY docker/start.sh /etc/start.sh
ADD . /tf/seismic-ai
