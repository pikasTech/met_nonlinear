import { appendFileSync, cpSync, existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";

interface GpuInfo {
  index: number;
  name: string;
  memoryTotalMiB: number;
  memoryFreeMiB: number;
  freeRatio: number;
}

interface ProjectProgress {
  projectPath: string;
  epochTarget: number | null;
  currentEpoch: number | null;
  progressPercent: number | null;
  lastLoss: number | null;
  lastValLoss: number | null;
  logLineCount: number;
  trainingInfo: Record<string, unknown> | null;
  etaSeconds: number | null;
  updatedAt: string | null;
}

interface TrainJob {
  id: string;
  projectPath: string;
  status: "queued" | "running" | "succeeded" | "failed" | "canceled";
  createdAt: string;
  updatedAt: string;
  startedAt?: string;
  finishedAt?: string;
  containerName?: string;
  gpuIndex?: number;
  gpuName?: string;
  epochTarget?: number;
  exitCode?: number;
  error?: string;
  logPath?: string;
  progress?: ProjectProgress;
}

interface SchedulerState {
  version: number;
  settings: {
    maxConcurrency: number;
    targetGpuName: string;
    mlImage: string;
  };
  jobs: TrainJob[];
}

type JsonRecord = Record<string, unknown>;
type RunningProc = { proc: any; stdoutDone: Promise<void>; stderrDone: Promise<void> };

const root = process.env.MET_ROOT || "/workspace/met_nonlinear";
const dataRoot = process.env.MET_DATA_ROOT || "/data";
const hostRoot = process.env.MET_HOST_ROOT || root;
const hostDataRoot = process.env.MET_HOST_DATA_ROOT || dataRoot;
const stateDir = process.env.MET_STATE_DIR || join(root, ".state", "unidesk-met");
const logDir = process.env.MET_LOG_DIR || join(root, "logs", "unidesk-met");
const port = Number(process.env.PORT || "3288");
const defaultMlImage = process.env.MET_ML_IMAGE || "met-nonlinear-ml:tf26";
const runningProcs = new Map<string, RunningProc>();
const statePath = join(stateDir, "state.json");
const serverLogPath = join(logDir, "server.jsonl");
let schedulerTickInFlight = false;

mkdirSync(stateDir, { recursive: true });
mkdirSync(logDir, { recursive: true });

function nowIso(): string {
  return new Date().toISOString();
}

function log(level: string, event: string, detail: JsonRecord = {}): void {
  appendFileSync(serverLogPath, `${JSON.stringify({ at: nowIso(), level, event, ...detail })}\n`, "utf8");
}

function defaultState(): SchedulerState {
  return { version: 1, settings: { maxConcurrency: 1, targetGpuName: "2080 Ti", mlImage: defaultMlImage }, jobs: [] };
}

function positiveInt(value: unknown, min: number, max: number, fallback: number): number {
  const parsed = typeof value === "number" ? value : typeof value === "string" ? Number(value) : NaN;
  if (!Number.isInteger(parsed) || parsed < min || parsed > max) return fallback;
  return parsed;
}

function readState(): SchedulerState {
  if (!existsSync(statePath)) return defaultState();
  try {
    const parsed = JSON.parse(readFileSync(statePath, "utf8")) as Partial<SchedulerState>;
    return {
      version: 1,
      settings: {
        maxConcurrency: positiveInt(parsed.settings?.maxConcurrency, 1, 16, 1),
        targetGpuName: typeof parsed.settings?.targetGpuName === "string" ? parsed.settings.targetGpuName : "2080 Ti",
        mlImage: typeof parsed.settings?.mlImage === "string" ? parsed.settings.mlImage : defaultMlImage,
      },
      jobs: Array.isArray(parsed.jobs) ? parsed.jobs as TrainJob[] : [],
    };
  } catch (error) {
    log("error", "state_read_failed", { error: errorText(error) });
    return defaultState();
  }
}

function writeState(state: SchedulerState): void {
  const tmpPath = `${statePath}.tmp`;
  writeFileSync(tmpPath, `${JSON.stringify(state, null, 2)}\n`, "utf8");
  renameSync(tmpPath, statePath);
}

function updateState(mutator: (state: SchedulerState) => void): SchedulerState {
  const state = readState();
  mutator(state);
  writeState(state);
  return state;
}

function errorText(error: unknown): string {
  return error instanceof Error ? `${error.name}: ${error.message}` : String(error);
}

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(`${JSON.stringify(body, null, 2)}\n`, { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}

async function readJsonBody(req: Request): Promise<JsonRecord> {
  const text = await req.text();
  if (text.trim().length === 0) return {};
  const parsed = JSON.parse(text) as unknown;
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) throw new Error("request body must be a JSON object");
  return parsed as JsonRecord;
}

function safeProjectPath(raw: unknown): string {
  const value = String(raw || "").replace(/\\/g, "/").replace(/^\/+/, "");
  if (!/^(projects|ex_projects)\/[A-Za-z0-9_.\/-]+$/.test(value)) throw new Error(`invalid project path: ${value}`);
  if (value.includes("..")) throw new Error(`project path must not contain ..: ${value}`);
  return value;
}

function projectAbs(projectPath: string): string {
  return resolve(root, projectPath);
}

function readJsonFile(path: string): JsonRecord | null {
  if (!existsSync(path)) return null;
  try {
    const parsed = JSON.parse(readFileSync(path, "utf8")) as unknown;
    return typeof parsed === "object" && parsed !== null && !Array.isArray(parsed) ? parsed as JsonRecord : null;
  } catch {
    return null;
  }
}

function writeJsonFile(path: string, data: unknown): void {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, `${JSON.stringify(data, null, 2)}\n`, "utf8");
}

function projectConfig(projectPath: string): JsonRecord | null {
  return readJsonFile(join(projectAbs(projectPath), "config.json"));
}

function trainingLogPath(projectPath: string): string {
  return join(projectAbs(projectPath), "data", "training_log.jsonl");
}

function trainingInfoPath(projectPath: string): string {
  return join(projectAbs(projectPath), "data", "training_info.json");
}

function numberOrNull(value: unknown): number | null {
  const parsed = typeof value === "number" ? value : typeof value === "string" ? Number(value) : NaN;
  return Number.isFinite(parsed) ? parsed : null;
}

function timeMs(value: unknown): number | null {
  if (typeof value !== "string") return null;
  const ms = Date.parse(value);
  return Number.isFinite(ms) ? ms : null;
}

function projectProgress(projectPath: string): ProjectProgress {
  const config = projectConfig(projectPath);
  const epochTarget = typeof config?.epoch_train === "number" ? config.epoch_train : null;
  const logPath = trainingLogPath(projectPath);
  let currentEpoch: number | null = null;
  let lastLoss: number | null = null;
  let lastValLoss: number | null = null;
  let lineCount = 0;
  let updatedAt: string | null = null;
  let etaSeconds: number | null = null;
  if (existsSync(logPath)) {
    const lines = readFileSync(logPath, "utf8").split(/\r?\n/).filter((line) => line.trim().length > 0);
    lineCount = lines.length;
    const parsedLines: JsonRecord[] = [];
    for (const line of lines.slice(-200)) {
      try {
        const item = JSON.parse(line) as unknown;
        if (typeof item === "object" && item !== null && !Array.isArray(item)) parsedLines.push(item as JsonRecord);
      } catch {}
    }
    const last = parsedLines.at(-1);
    if (last !== undefined) {
      currentEpoch = numberOrNull(last.epoch) ?? numberOrNull(last.completed_epoch);
      lastLoss = numberOrNull(last.loss);
      lastValLoss = numberOrNull(last.val_loss);
      updatedAt = typeof last.timestamp === "string" ? last.timestamp : null;
    }
    const firstEpochLine = parsedLines.find((line) => numberOrNull(line.epoch) !== null);
    if (firstEpochLine && last && epochTarget !== null && currentEpoch !== null && currentEpoch > 0) {
      const firstEpoch = numberOrNull(firstEpochLine.epoch) ?? 0;
      const firstTime = timeMs(firstEpochLine.timestamp);
      const lastTime = timeMs(last.timestamp);
      if (firstTime !== null && lastTime !== null && lastTime > firstTime && currentEpoch > firstEpoch) {
        const secondsPerEpoch = (lastTime - firstTime) / 1000 / Math.max(1, currentEpoch - firstEpoch);
        etaSeconds = Math.max(0, Math.round((epochTarget - currentEpoch) * secondsPerEpoch));
      }
    }
  }
  const trainingInfo = readJsonFile(trainingInfoPath(projectPath));
  const progressPercent = epochTarget !== null && currentEpoch !== null && epochTarget > 0 ? Math.max(0, Math.min(100, (currentEpoch / epochTarget) * 100)) : null;
  return { projectPath, epochTarget, currentEpoch, progressPercent, lastLoss, lastValLoss, logLineCount: lineCount, trainingInfo, etaSeconds, updatedAt };
}

async function runCommand(args: string[], timeoutMs = 10_000): Promise<{ ok: boolean; exitCode: number | null; stdout: string; stderr: string; timedOut: boolean }> {
  const proc = Bun.spawn(args, { stdout: "pipe", stderr: "pipe" });
  let timedOut = false;
  const timer = setTimeout(() => { timedOut = true; proc.kill(); }, timeoutMs);
  const [exitCode, stdout, stderr] = await Promise.all([proc.exited, new Response(proc.stdout).text(), new Response(proc.stderr).text()]);
  clearTimeout(timer);
  return { ok: exitCode === 0 && !timedOut, exitCode, stdout, stderr, timedOut };
}

function parseGpuSmiCsv(text: string): GpuInfo[] {
  return text.trim().split(/\r?\n/).filter(Boolean).map((line) => {
    const [indexText = "", name = "", totalText = "0", freeText = "0"] = line.split(",").map((part) => part.trim());
    const total = Number(totalText);
    const free = Number(freeText);
    return { index: Number(indexText), name, memoryTotalMiB: total, memoryFreeMiB: free, freeRatio: total > 0 ? free / total : 0 };
  }).filter((gpu) => Number.isInteger(gpu.index));
}

let gpuCache: { atMs: number; gpus: GpuInfo[] } | null = null;

async function gpuInfo(): Promise<GpuInfo[]> {
  const nowMs = Date.now();
  if (gpuCache !== null && nowMs - gpuCache.atMs < 15_000) return gpuCache.gpus;
  const queryArgs = ["--query-gpu=index,name,memory.total,memory.free", "--format=csv,noheader,nounits"];
  const image = readState().settings.mlImage || defaultMlImage;
  const inspect = await runCommand(["docker", "image", "inspect", image, "--format", "{{.Id}}"], 1500)
    .catch((error) => ({ ok: false, stdout: "", stderr: errorText(error), exitCode: null, timedOut: false }));
  if (!inspect.ok) {
    gpuCache = { atMs: nowMs, gpus: [] };
    return [];
  }
  const dockerResult = await runCommand(["docker", "run", "--rm", "--pull", "never", "--gpus", "all", "--entrypoint", "nvidia-smi", image, ...queryArgs], 12_000)
    .catch((error) => ({ ok: false, stdout: "", stderr: errorText(error), exitCode: null, timedOut: false }));
  const gpus = dockerResult.ok && dockerResult.stdout.trim().length > 0 ? parseGpuSmiCsv(dockerResult.stdout) : [];
  gpuCache = { atMs: nowMs, gpus };
  return gpus;
}

async function dockerImageStatus(image: string, timeoutMs = 8000): Promise<JsonRecord> {
  const result = await runCommand(["docker", "image", "inspect", image, "--format", "{{json .}}"], timeoutMs);
  if (!result.ok) return { present: false, image, error: result.stderr.trim() };
  try {
    const parsed = JSON.parse(result.stdout) as JsonRecord;
    return { present: true, image, id: parsed.Id, created: parsed.Created, sizeBytes: parsed.Size };
  } catch {
    return { present: true, image, raw: result.stdout.slice(0, 500) };
  }
}

function shellQuote(value: string): string {
  return `'${value.replace(/'/g, `'"'"'`)}'`;
}

function listProjects(rootName: "projects" | "ex_projects", limit: number): JsonRecord[] {
  const base = join(root, rootName);
  const find = Bun.spawnSync(["bash", "-lc", `find ${shellQuote(base)} -mindepth 2 -maxdepth 3 -name config.json | sed -n '1,${limit}p'`]);
  const stdout = find.stdout.toString();
  return stdout.split(/\r?\n/).filter(Boolean).map((configPath) => {
    const projectPath = configPath.slice(root.length + 1, -"/config.json".length).replace(/\\/g, "/");
    const config = readJsonFile(configPath) ?? {};
    return { projectPath, useModel: config.use_model ?? null, epochTrain: config.epoch_train ?? null, stepPerEpoch: config.step_per_epoch ?? null, usingGpu: config.using_gpu ?? null, progress: projectProgress(projectPath) };
  });
}

async function createServerTestProjects(body: JsonRecord): Promise<JsonRecord> {
  const count = positiveInt(body.count, 1, 50, 10);
  const epochs = positiveInt(body.epochs, 1, 10_000, 10);
  const sourceProject = safeProjectPath(body.sourceProject || "projects/FRIKANh6u6l4");
  const sourceConfigPath = join(projectAbs(sourceProject), "config.json");
  if (!existsSync(sourceConfigPath)) throw new Error(`source config not found: ${sourceProject}`);
  const prefix = typeof body.prefix === "string" && /^[A-Za-z0-9_.-]+$/.test(body.prefix) ? body.prefix : `server_test_${Date.now()}`;
  const projectPaths: string[] = [];
  for (let index = 1; index <= count; index += 1) {
    const projectPath = `projects/server_test/${prefix}_${String(index).padStart(2, "0")}`;
    const destDir = projectAbs(projectPath);
    mkdirSync(destDir, { recursive: true });
    cpSync(sourceConfigPath, join(destDir, "config.json"));
    const config = readJsonFile(join(destDir, "config.json")) ?? {};
    config.epoch_train = epochs;
    config.resume_training = false;
    config.using_gpu = true;
    writeJsonFile(join(destDir, "config.json"), config);
    writeJsonFile(join(destDir, "unidesk_server_test.json"), { sourceProject, index, count, epochs, createdAt: nowIso() });
    projectPaths.push(projectPath);
  }
  return { ok: true, sourceProject, count, epochs, projectPaths };
}

function enqueueProjects(projectPaths: string[], body: JsonRecord): SchedulerState {
  const maxConcurrency = positiveInt(body.maxConcurrency, 1, 16, readState().settings.maxConcurrency);
  const targetGpuName = typeof body.targetGpuName === "string" ? body.targetGpuName : readState().settings.targetGpuName;
  return updateState((state) => {
    state.settings.maxConcurrency = maxConcurrency;
    state.settings.targetGpuName = targetGpuName;
    for (const projectPath of projectPaths) {
      const safePath = safeProjectPath(projectPath);
      if (!existsSync(join(projectAbs(safePath), "config.json"))) throw new Error(`project config not found: ${safePath}`);
      const config = projectConfig(safePath);
      state.jobs.push({
        id: `met_${Date.now()}_${Math.random().toString(16).slice(2, 8)}`,
        projectPath: safePath,
        status: "queued",
        createdAt: nowIso(),
        updatedAt: nowIso(),
        epochTarget: typeof config?.epoch_train === "number" ? config.epoch_train : undefined,
        logPath: join(logDir, `train_${Date.now()}_${Math.random().toString(16).slice(2, 8)}.log`),
      });
    }
  });
}

async function pipeStreamToLog(stream: ReadableStream<Uint8Array> | null, logPath: string, streamName: string): Promise<void> {
  if (stream === null) return;
  const reader = stream.getReader();
  while (true) {
    const chunk = await reader.read();
    if (chunk.done) return;
    appendFileSync(logPath, chunk.value);
    appendFileSync(serverLogPath, `${JSON.stringify({ at: nowIso(), level: "debug", event: "train_output", stream: streamName, bytes: chunk.value.length, logPath })}\n`, "utf8");
  }
}

function tailFile(path: string, maxBytes: number): string {
  if (!existsSync(path)) return "";
  return readFileSync(path, "utf8").slice(-maxBytes);
}

async function startJob(job: TrainJob, gpu: GpuInfo | null, image: string): Promise<void> {
  const containerName = `metnl-train-${job.id.replace(/[^a-zA-Z0-9_-]/g, "-")}`.slice(0, 120);
  const logPath = job.logPath || join(logDir, `${containerName}.log`);
  mkdirSync(dirname(logPath), { recursive: true });
  appendFileSync(logPath, `${JSON.stringify({ at: nowIso(), event: "job_start", projectPath: job.projectPath, image, gpu })}\n`, "utf8");
  const gpuArgs = gpu === null ? ["--gpus", "all"] : ["--gpus", `device=${gpu.index}`];
  const command = `cd /workspace/met_nonlinear && export TF_FORCE_GPU_ALLOW_GROWTH=true PYTHONUNBUFFERED=1 MET_DATA_BASE=/data MET_DATA_DIR=/data/data && python cli.py -t ${shellQuote(job.projectPath)}`;
  const args = ["docker", "run", "--rm", "--name", containerName, ...gpuArgs, "-e", "TF_FORCE_GPU_ALLOW_GROWTH=true", "-e", "PYTHONUNBUFFERED=1", "-e", "MET_DATA_BASE=/data", "-e", "MET_DATA_DIR=/data/data", "-v", `${hostRoot}:/workspace/met_nonlinear`, "-v", `${hostDataRoot}:/data/data`, "-w", "/workspace/met_nonlinear", image, "bash", "-lc", command];
  const proc = Bun.spawn(args, { stdout: "pipe", stderr: "pipe" });
  const stdoutDone = pipeStreamToLog(proc.stdout, logPath, "stdout");
  const stderrDone = pipeStreamToLog(proc.stderr, logPath, "stderr");
  runningProcs.set(job.id, { proc, stdoutDone, stderrDone });
  updateState((state) => {
    const stored = state.jobs.find((item) => item.id === job.id);
    if (!stored) return;
    stored.status = "running";
    stored.startedAt = nowIso();
    stored.updatedAt = nowIso();
    stored.containerName = containerName;
    stored.gpuIndex = gpu?.index;
    stored.gpuName = gpu?.name;
    stored.logPath = logPath;
  });
  proc.exited.then(async (exitCode: number) => {
    await Promise.allSettled([stdoutDone, stderrDone]);
    runningProcs.delete(job.id);
    const progress = projectProgress(job.projectPath);
    updateState((state) => {
      const stored = state.jobs.find((item) => item.id === job.id);
      if (!stored || stored.status === "canceled") return;
      stored.exitCode = exitCode;
      stored.status = exitCode === 0 ? "succeeded" : "failed";
      stored.finishedAt = nowIso();
      stored.updatedAt = nowIso();
      stored.progress = progress;
      if (exitCode !== 0) stored.error = tailFile(logPath, 2000);
    });
    log(exitCode === 0 ? "info" : "error", "job_finished", { jobId: job.id, projectPath: job.projectPath, exitCode, logPath });
  }).catch((error: unknown) => {
    runningProcs.delete(job.id);
    updateState((state) => {
      const stored = state.jobs.find((item) => item.id === job.id);
      if (!stored) return;
      stored.status = "failed";
      stored.error = errorText(error);
      stored.finishedAt = nowIso();
      stored.updatedAt = nowIso();
    });
  });
}

async function schedulerTick(): Promise<void> {
  const state = readState();
  const queued = state.jobs.filter((job) => job.status === "queued");
  const running = state.jobs.filter((job) => job.status === "running");
  const gpus = await gpuInfo();
  const target = gpus.find((gpu) => gpu.name.toLowerCase().replace(/\s+/g, "").includes(state.settings.targetGpuName.toLowerCase().replace(/\s+/g, ""))) ?? null;
  const gpuLimitedMax = target !== null && target.freeRatio < 0.2 ? Math.min(1, state.settings.maxConcurrency) : state.settings.maxConcurrency;
  const slots = Math.max(0, gpuLimitedMax - running.length);
  if (queued.length === 0 || slots <= 0) return;
  const imageStatus = await dockerImageStatus(state.settings.mlImage);
  if (imageStatus.present !== true) {
    log("warn", "ml_image_missing", { image: state.settings.mlImage, queued: queued.length, imageStatus });
    return;
  }
  for (const job of queued.slice(0, slots)) await startJob(job, target, state.settings.mlImage);
}

function queueSummary(state: SchedulerState): JsonRecord {
  const counts: Record<string, number> = {};
  for (const job of state.jobs) counts[job.status] = (counts[job.status] || 0) + 1;
  return { counts, maxConcurrency: state.settings.maxConcurrency, targetGpuName: state.settings.targetGpuName, mlImage: state.settings.mlImage };
}

async function statusPayload(includeGpu = true): Promise<JsonRecord> {
  const state = readState();
  const gpus = includeGpu ? await gpuInfo() : [];
  return { ok: true, service: "met-nonlinear-unidesk-ts", root, dataRoot, hostRoot, hostDataRoot, statePath, serverLogPath, queue: queueSummary(state), gpu: gpus, targetGpu: gpus.find((gpu) => gpu.name.toLowerCase().replace(/\s+/g, "").includes(state.settings.targetGpuName.toLowerCase().replace(/\s+/g, ""))) ?? null, image: await dockerImageStatus(state.settings.mlImage, includeGpu ? 8000 : 1500), updatedAt: nowIso() };
}

async function route(req: Request): Promise<Response> {
  const url = new URL(req.url);
  try {
    if (url.pathname === "/health") return jsonResponse(await statusPayload(false));
    if (url.pathname === "/api/summary") {
      const state = readState();
      return jsonResponse({ ...(await statusPayload()), recentJobs: state.jobs.slice(-10).reverse() });
    }
    if (url.pathname === "/api/projects" && req.method === "GET") {
      const rootName = url.searchParams.get("root") === "ex_projects" ? "ex_projects" : "projects";
      const limit = positiveInt(url.searchParams.get("limit"), 1, 500, 80);
      return jsonResponse({ ok: true, root: rootName, projects: listProjects(rootName, limit) });
    }
    if (url.pathname === "/api/projects/config" && req.method === "GET") {
      const projectPath = safeProjectPath(url.searchParams.get("path"));
      return jsonResponse({ ok: true, projectPath, config: projectConfig(projectPath), progress: projectProgress(projectPath) });
    }
    if (url.pathname === "/api/projects/config" && req.method === "PUT") {
      const body = await readJsonBody(req);
      const projectPath = safeProjectPath(body.projectPath);
      const patch = typeof body.patch === "object" && body.patch !== null && !Array.isArray(body.patch) ? body.patch as JsonRecord : {};
      const config = projectConfig(projectPath);
      if (config === null) throw new Error(`project config not found: ${projectPath}`);
      const next = { ...config, ...patch };
      writeJsonFile(join(projectAbs(projectPath), "config.json"), next);
      return jsonResponse({ ok: true, projectPath, config: next });
    }
    if (url.pathname === "/api/server-test/create" && req.method === "POST") return jsonResponse(await createServerTestProjects(await readJsonBody(req)));
    if (url.pathname === "/api/queue" && req.method === "GET") {
      const state = readState();
      const jobs = state.jobs.map((job) => job.status === "running" ? { ...job, progress: projectProgress(job.projectPath) } : job);
      return jsonResponse({ ok: true, queue: queueSummary(state), jobs: jobs.slice().reverse(), gpu: await gpuInfo() });
    }
    if (url.pathname === "/api/queue" && req.method === "POST") {
      const body = await readJsonBody(req);
      const rawProjects = Array.isArray(body.projectPaths) ? body.projectPaths : [];
      const state = enqueueProjects(rawProjects.map(String), body);
      return jsonResponse({ ok: true, queue: queueSummary(state), jobs: state.jobs.slice(-rawProjects.length) });
    }
    if (url.pathname === "/api/queue/server-test" && req.method === "POST") {
      const body = await readJsonBody(req);
      const created = await createServerTestProjects(body);
      const projectPaths = created.projectPaths as string[];
      const state = enqueueProjects(projectPaths, body);
      return jsonResponse({ ok: true, created, queue: queueSummary(state), jobs: state.jobs.slice(-projectPaths.length) });
    }
    if (url.pathname === "/api/history") {
      const state = readState();
      return jsonResponse({ ok: true, jobs: state.jobs.filter((job) => ["succeeded", "failed", "canceled"].includes(job.status)).slice(-200).reverse() });
    }
    if (url.pathname.startsWith("/api/jobs/") && req.method === "GET") {
      const id = decodeURIComponent(url.pathname.slice("/api/jobs/".length));
      const job = readState().jobs.find((item) => item.id === id);
      if (!job) return jsonResponse({ ok: false, error: `job not found: ${id}` }, 404);
      return jsonResponse({ ok: true, job: { ...job, progress: projectProgress(job.projectPath) }, logTail: job.logPath ? tailFile(job.logPath, 4000) : "" });
    }
    if (url.pathname.startsWith("/api/jobs/") && url.pathname.endsWith("/cancel") && req.method === "POST") {
      const id = decodeURIComponent(url.pathname.slice("/api/jobs/".length, -"/cancel".length));
      const proc = runningProcs.get(id);
      let matched = false;
      updateState((state) => {
        const job = state.jobs.find((item) => item.id === id);
        if (!job) return;
        matched = true;
        if (job.status === "queued" || job.status === "running") {
          job.status = "canceled";
          job.finishedAt = nowIso();
          job.updatedAt = nowIso();
        }
      });
      if (proc) proc.proc.kill();
      return matched ? jsonResponse({ ok: true }) : jsonResponse({ ok: false, error: `job not found: ${id}` }, 404);
    }
    if (url.pathname === "/api/logs" && req.method === "GET") {
      const jobId = url.searchParams.get("jobId");
      const state = readState();
      const job = jobId ? state.jobs.find((item) => item.id === jobId) : null;
      const path = job?.logPath || serverLogPath;
      return jsonResponse({ ok: true, path, tail: tailFile(path, positiveInt(url.searchParams.get("bytes"), 1000, 200_000, 12_000)) });
    }
    if (url.pathname === "/api/images" && req.method === "GET") {
      const state = readState();
      return jsonResponse({ ok: true, mlImage: await dockerImageStatus(state.settings.mlImage), expectedBuildCommand: "docker build -t met-nonlinear-ml:tf26 -f docker/unidesk/Dockerfile.ml ." });
    }
    return jsonResponse({ ok: false, error: `not found: ${url.pathname}` }, 404);
  } catch (error) {
    log("error", "request_failed", { path: url.pathname, error: errorText(error) });
    return jsonResponse({ ok: false, error: errorText(error) }, 500);
  }
}

setInterval(() => {
  if (schedulerTickInFlight) return;
  schedulerTickInFlight = true;
  schedulerTick()
    .catch((error) => log("error", "scheduler_tick_failed", { error: errorText(error) }))
    .finally(() => { schedulerTickInFlight = false; });
}, 2500);

Bun.serve({ port, hostname: "0.0.0.0", async fetch(req) { return route(req); } });

log("info", "server_started", { port, root, dataRoot, statePath, serverLogPath });
console.log(JSON.stringify({ ok: true, service: "met-nonlinear-unidesk-ts", port, root, dataRoot, statePath, serverLogPath }));
