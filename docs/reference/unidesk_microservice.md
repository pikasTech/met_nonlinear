# UniDesk Microservice

## Boundary

- UniDesk only hosts the React frontend, microservice catalog registration and the provider-gateway proxy path for this service.
- D601 WSL owns `~/met_nonlinear`, the TypeScript orchestration backend, Dockerfiles, queue state and training containers. `MET_HOST_ROOT=/home/ubuntu/met_nonlinear` and `MET_HOST_DATA_ROOT=/mnt/f/BaiduSyncdisk/data` are mandatory because the TS backend talks to the host Docker socket and Docker bind mounts must use host paths, not container-internal paths.
- WSL must not install the TensorFlow training environment; TensorFlow 2.6 and ML dependencies live only in the `met-nonlinear-ml:tf26` image.
- The data mount source is `/mnt/f/BaiduSyncdisk/data` on D601 and is mounted to `/data/data` inside training containers; `MET_DATA_BASE=/data` keeps legacy config paths such as `data/M50` resolving to `/data/data/M50`.


## Development Boundary

- Backend, Dockerfile, ML image build, GPU checks and training debug all happen on D601 through UniDesk SSH passthrough.
- The main server local workspace only develops the UniDesk React frontend and the catalog/proxy registration needed to reach this service.
- Do not copy the MET backend, training image build, or training workload to the main server for convenience.

## Services

- `met-nonlinear-ts` is the long-lived Bun TypeScript backend on D601, bound to `127.0.0.1:3288`.
- `met-nonlinear-ml:tf26` is the cached GPU training image. Training jobs use `docker run --rm` and are destroyed after completion.
- Each training job launches one container named `metnl-train-<jobId>` and runs `python cli.py -t <projectPath>` from `/workspace/met_nonlinear`.

## Deployment

```bash
cd ~/met_nonlinear

docker build -t met-nonlinear-ml:tf26 -f docker/unidesk/Dockerfile.ml .
docker compose -f docker-compose.unidesk.yml up -d --build met-nonlinear-ts
curl -fsS http://127.0.0.1:3288/health | python3 -m json.tool
```

The Docker build uses the Huawei Cloud mirror of `nvidia/cuda:11.2.2-cudnn8-runtime-ubuntu20.04`, Aliyun Ubuntu mirrors and Tsinghua PyPI mirrors. The image installs Ubuntu Python 3.8 plus `tensorflow==2.6.0`, `keras==2.6.0`, CUDA-compatible numerical dependencies, `sympy` and `openpyxl`; this avoids the Python 3.6 incompatibility of the official TensorFlow 2.6 GPU image while keeping the TF 2.6/CUDA 11.2 runtime. The build context is restricted by `.dockerignore` so code/data artifacts are not sent into the image build.

## Queue API

- `GET /health`: fast service, image and queue summary for Docker healthcheck and UniDesk health probes; it must not block on slow GPU discovery.
- `GET /api/projects?root=projects&limit=80`: project list with config summary and training progress.
- `GET /api/projects/config?path=projects/<name>`: structured config and progress.
- `POST /api/queue`: enqueue existing projects with `projectPaths`, `maxConcurrency` and optional `targetGpuName`.
- `POST /api/queue/server-test`: copy an existing project config into `projects/server_test/`, set `epoch_train`, write UniDesk metadata to `unidesk_server_test.json` instead of adding unknown fields to `config.json`, and enqueue all generated projects.
- `GET /api/queue`: queue, running jobs, history preview and cached GPU status.
- `GET /api/history`: terminal jobs with exit code, duration fields and failure details.
- `GET /api/jobs/<id>` and `GET /api/logs?jobId=<id>`: job diagnostics and log tail.

## GPU Policy

- The scheduler targets the GPU whose name contains `2080 Ti` by default.
- If the target GPU free VRAM ratio is below 20%, the scheduler limits effective concurrency to 1 and starts no extra containers beyond that cap. Scheduler ticks are guarded against overlap so the queue cannot start duplicate containers or exceed the effective concurrency cap.
- GPU status is read by running `nvidia-smi` inside the cached ML image through `docker run --pull never --gpus all --entrypoint nvidia-smi met-nonlinear-ml:tf26`; this keeps WSL free of the ML environment and avoids Docker healthcheck blocking when the image is absent.

## Acceptance

```bash
cd ~/met_nonlinear
curl -fsS -X POST http://127.0.0.1:3288/api/queue/server-test \
  -H 'content-type: application/json' \
  -d '{"sourceProject":"projects/FRIKANh6u6l4","count":10,"epochs":10,"maxConcurrency":2}' | python3 -m json.tool
watch -n 5 'curl -fsS http://127.0.0.1:3288/api/queue | python3 -m json.tool | sed -n "1,120p"'
```

Acceptance requires all ten generated `projects/server_test/` jobs to reach `succeeded` with `epoch_train=10`, no more than two simultaneous training containers, all running jobs pinned to the 2080Ti GPU, `metnl-train-*` containers automatically removed after completion, and no `projects/server_test/` generated artifacts committed to git.
