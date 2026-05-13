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
- `GET /api/projects?root=projects&limit=500` and `GET /api/projects?root=ex_projects&limit=500`: project list with config summary, training progress and enough rows for UniDesk to render the real folder tree. The backend must discover `config.json` at the true project path and must not group by model/status.
- `GET /api/projects/config?path=projects/<name>`: structured config, progress, `data/` file list, `training_state.json`, `training_info.json`, `metrics.json`, `model_info.json`, `compute_analysis.json`, model parameter summary and metrics for the UniDesk detail panel.
- `POST /api/projects/fork`: fork one or more config-only projects from an existing source Project into `projects/unidesk_forks/` or `projects/server_test/`, set `epoch_train`, force GPU training and write `unidesk_project_fork.json` metadata.
- `POST /api/queue`: add existing projects to the scheduler with `projectPaths`, `maxConcurrency`, optional `targetGpuName` and `start=false` for the UI staged queue. Default `start` remains immediate queueing for compatibility.
- `POST /api/queue/start`: transition staged jobs to queued after the operator clicks the UI `启动队列` control.
- `PUT /api/queue/settings`: update `maxConcurrency` and `targetGpuName` without adding jobs.
- `POST /api/queue/server-test`: compatibility endpoint for old scripted acceptance; it delegates to the generic fork path and is not exposed as a hard-coded frontend button.
- `GET /api/queue`: queue, all jobs with refreshed progress, `epochPerHour` speed and cached GPU status.
- `GET /api/history`: terminal jobs with exit code, duration fields, refreshed progress, `epochPerHour` speed and failure details.
- `GET /api/jobs/<id>` and `GET /api/logs?jobId=<id>`: job diagnostics, structured project detail and log tail.

## GPU Policy

- The scheduler targets the GPU whose name contains `2080 Ti` by default.
- If the target GPU free VRAM ratio is below 20%, the scheduler limits effective concurrency to 1 and starts no extra containers beyond that cap. Scheduler ticks are guarded against overlap so the queue cannot start duplicate containers or exceed the effective concurrency cap.
- GPU status is read by running `nvidia-smi` inside the cached ML image through `docker run --pull never --gpus all --entrypoint nvidia-smi met-nonlinear-ml:tf26`; this keeps WSL free of the ML environment and avoids Docker healthcheck blocking when the image is absent.

## Acceptance

Acceptance is driven from the public UniDesk frontend, not from a hard-coded test button. The operator selects an existing source Project, uses `Fork Project` to create generated projects under `projects/unidesk_forks/`, sets the training epoch count, batch size and maximum concurrency through inputs, adds the forked projects to the staged queue, and only starts training by clicking `启动队列`. A full acceptance batch can use count=10, epochs=200 and maxConcurrency=3, but that scale must remain operator-entered UI data, not a dedicated frontend button.

For API-level troubleshooting the equivalent sequence is:

```bash
cd ~/met_nonlinear
curl -fsS -X POST http://127.0.0.1:3288/api/projects/fork \
  -H 'content-type: application/json' \
  -d '{"sourceProject":"projects/FRIKANh6u6l4","count":10,"epochs":200,"prefix":"ui_acceptance"}' | python3 -m json.tool
curl -fsS -X POST http://127.0.0.1:3288/api/queue \
  -H 'content-type: application/json' \
  -d '{"projectPaths":["projects/unidesk_forks/ui_acceptance_01"],"maxConcurrency":3,"targetGpuName":"2080 Ti","start":false}' | python3 -m json.tool
curl -fsS -X POST http://127.0.0.1:3288/api/queue/start \
  -H 'content-type: application/json' \
  -d '{"maxConcurrency":3,"targetGpuName":"2080 Ti"}' | python3 -m json.tool
watch -n 5 'curl -fsS http://127.0.0.1:3288/api/queue | python3 -m json.tool | sed -n "1,160p"'
```

Acceptance requires the frontend to show staged, queued, running, completed and failure-diagnostic tabs; running rows must show progress and ETA from backend progress or from `startedAt` plus epoch progress; queue and completed rows must show `epoch/h` training speed. The project library must render `projects/` and `ex_projects/` as a path tree whose folder counts match the number of descendant Project configs. Clicking a project row must open a structured detail panel with `config.json`, `data/` training state, model parameter count, model layers and metrics; clicking a job row must open the corresponding structured job/project detail and log-tail summary. Generated fork artifacts must stay ignored by git; all acceptance jobs must reach `succeeded` for the requested `epoch_train`; the effective concurrency must not exceed the configured cap or the 2080Ti VRAM safety cap; all running jobs must target the 2080Ti GPU; and `metnl-train-*` containers must be automatically removed after completion.
