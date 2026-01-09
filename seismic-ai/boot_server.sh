git config --global --add safe.directory /home/ubuntu/seismic-ai
git config --global --add safe.directory /home/ubuntu/seismic-ai/lib/met
git pull && git submodule init && git submodule update && bash build.sh && bash gpu_run.sh