# Ullah_2026_NanoBench

NanoBench: A Multi-Task Benchmark Dataset for
Nano-Quadrotor System Identification,
Control, and State Estimation
Syed Izzat Ullah, Jos´e Baca
Department of Computer Science
Texas A&M University-Corpus Christi, Corpus Christi, TX, USA
sizzatullah@islander.tamucc.edu, jose.baca@tamucc.edu
Abstract—Existing aerial-robotics benchmarks target vehicles
from hundreds of grams to several kilograms and typically expose
only high-level state data. They omit the actuator-level signals
required to study nano-scale quadrotors, where low-Reynolds-
number aerodynamics, coreless DC motor nonlinearities, and se-
vere computational constraints invalidate models and controllers
developed for larger vehicles. We introduce NanoBench, an
open-source multi-task benchmark collected on the commercially
available Crazyflie 2.1 nano-quadrotor (takeoff weight 27 g)
in a Vicon motion capture arena. The dataset contains over
170 flight trajectories spanning hover, multi-frequency excitation,
standard tracking, and aggressive maneuvers across multiple
speed regimes. Each trajectory provides synchronized Vicon
ground truth, raw IMU data, onboard extended Kalman filter
estimates, PID controller internals, and motor PWM commands
at 100 Hz, alongside battery telemetry at 10 Hz, aligned with
sub-0.5 ms consistency. NanoBench defines standardized evalu-
ation protocols, train/test splits, and open-source baselines for
three tasks: nonlinear system identification, closed-loop controller
benchmarking, and onboard state estimation assessment. To our
knowledge, it is the first public dataset to jointly provide actuator
commands, controller internals, and estimator outputs with
millimeter-accurate ground truth on a commercially available
nano-scale aerial platform.
Dataset: https://github.com/syediu/nanobench-iros2026.git
I. INTRODUCTION
Learning-based
methods
have
substantially
advanced
quadrotor autonomy. Deep reinforcement learning policies
match professional pilots in drone racing [1], adaptive con-
trollers trained on minutes of flight data enable agile flight in
strong wind [2], and data-driven model predictive controllers
that incorporate learned residual dynamics outperform rigid-
body baselines [3]. These techniques require instrumented
datasets for training and reproducible evaluation. Most pub-
licly available datasets that support such evaluation were
collected on platforms weighing hundreds of grams to several
kilograms. For nano-scale quadrotors, platforms below 50 g,
which are widely used in embedded autonomy, safe learning,
swarm robotics, autonomous navigation and mapping, and
collision-aware trajectory planning [4]–[9], there is currently
no open benchmark that exposes the full closed-loop stack.
Nano-scale quadrotors such as the Crazyflie 2.1 (27 g
takeoff mass) operate in aerodynamic regimes that differ
qualitatively from those of larger vehicles. Propellers with di-
ameters below 50 mm generate airflows at Reynolds numbers
on the order of 104, where laminar separation bubbles and
viscous losses significantly affect thrust and torque charac-
teristics [10]. Coreless DC motors introduce deadbands and
response lags absent in brushless propulsion [11]. Proximity
to surfaces induces severe ground effect disturbances at low
altitudes [12]. Computationally, a 168 MHz Cortex-M4 mi-
crocontroller strictly limits algorithms to lightweight extended
Kalman filters [13], and therefore demands highly optimized
software architectures.
These physical and computational constraints invalidate
assumptions derived from larger vehicles, yet no standardized
benchmark exists to study nano-scale dynamics under these
constraints. Thrust models transfer poorly across Reynolds
number regimes [14]. Policies trained in simulation degrade
on physical hardware due to inaccurate thrust modeling [15],
[16]. Lightweight estimators require precisely synchronized
multi-modal recordings for proper validation [17]. Despite
this demand, no existing dataset provides actuator commands,
controller internals, and estimator outputs with external ground
truth on a commercially available nano-scale platform. Re-
searchers currently evaluate system identification, control,
and state estimation algorithms on private or synthetic data,
precluding systematic comparison [18].
This paper presents NanoBench, an open-source multi-task
benchmark that addresses this gap. The dataset is collected on
the standard Crazyflie 2.1 quadrotor inside a Vicon motion
capture arena using a data collection framework based on
direct radio communication via the cflib Python library. Our
contributions are as follows:
1) Nano-quadrotor
flight
dataset.
We
release
over
170 trajectories on the Crazyflie 2.1 covering hover,
multi-frequency excitation, standard tracking, and ag-
gressive flight across multiple speed regimes. Every tra-
jectory includes time-synchronized Vicon ground truth,
raw IMU measurements, onboard EKF state estimates,
PID controller internals, and motor PWM commands at
100 Hz, with battery telemetry at 10 Hz.
2) Cross-correlation time alignment. We develop and val-
idate a synchronization procedure that cross-correlates
onboard gyroscope angular rates with Vicon-derived
angular velocity to estimate and correct the firmware-
to-host clock offset. Across all flights, the residual
arXiv:2603.09908v1  [cs.RO]  10 Mar 2026
misalignment is below 0.5 ms.
3) Multi-task evaluation suite. We define train/test splits,
metrics, and reporting conventions for three tasks —
system identification, controller benchmarking, and state
estimation — and release open-source baseline imple-
mentations that establish reference performance levels
on each.
4) A standardized multi-task evaluation protocol. De-
fined train/test splits, metrics, and reporting conventions
for system identification, controller benchmarking, and
state estimation, with open-source baseline implementa-
tions establishing reference performance levels for each
task.
The remainder of this paper is organized as follows. Sec-
tion II positions NanoBench against prior literature. Sec-
tion III describes the hardware platform, acquisition pipeline,
synchronization procedure, trajectory design, and benchmark
task formulations. Section IV details the experimental setup,
dataset composition, and benchmark evaluations. Section V
discusses limitations and conclusions.
II. RELATED WORK
A. Aerial Robot Datasets and Benchmarks
Aerial robotics datasets can be partitioned by the down-
stream tasks they support and the platform scales they cover.
The EuRoC MAV dataset [19], UZH-FPV [20], NTU VI-
RAL [21], and INSANE [22] provide high-fidelity exterocep-
tive sensor data for visual-inertial odometry and multi-sensor
fusion. However, these benchmarks treat the vehicle as a
passive sensor carrier and omit actuator and control signals. As
a result, they cannot support closed-loop dynamics modeling,
controller evaluation, or estimator benchmarking.
Actuation-aware datasets capture the inputs necessary for
system identification. The Blackbird dataset [23] and Agili-
cious framework [24] log motor commands for agile flight
research. However, they feature quadrotors weighing near
1 kg equipped with brushless motors. These heavy platforms
exhibit rigid-body dynamics that differ fundamentally from the
coreless DC actuation and severe aerodynamic nonlinearities
of nano-quadrotors, precluding direct transfer of models or
control policies.
At the nano scale, Busetto et al. [25] recently released a
system identification dataset for a brushless Crazyflie variant
that logs motor RPM. The dataset covers only four trajectories,
omits onboard EKF and PID logs entirely, and records no
battery voltage. Table I details these gaps. These omissions
restrict the benchmark to single-task system identification on
non-standard hardware that leave multi-task evaluation on the
commercially standard Crazyflie 2.1 unaddressed.
B. System Identification for Aerial Vehicles
Quadrotor dynamics modeling ranges from calibrated
physics to fully learned representations. Forster [11] estab-
lished baseline quadratic thrust parameters via least-squares
fitting. Torrente et al. [3] and NeuroBEM [14] augmented
nominal rigid-body equations with data-driven residuals to
capture unmodeled aerodynamic effects. Neural ordinary dif-
ferential equations offer purely data-driven alternatives. Zhou
et al. [26] trained Neural ODEs for multi-step state prediction,
while KNODE-MPC [27] and O’Connell et al. [2] embedded
adapted models within predictive controllers to improve track-
ing accuracy.
Crucially, existing simulation ecosystems configure these
learned and analytical models with static coefficients [28].
This constant-parameter assumption ignores the severe thrust
degradation caused by single-cell LiPo battery discharge. No
existing benchmark provides the synchronized voltage and
kinematics data required to model this non-stationary battery
effect.
C. Control of Nano-Quadrotors
The Crazyflie serves as a primary testbed for validating con-
trol architectures. Researchers routinely implement cascaded
PID loops, geometric controllers on SE(3), and minimum-
snap trajectory trackers [29]. Safe reinforcement learning
frameworks mostly utilize the Crazyflie platform [5], with
recent studies achieving zero-shot sim-to-real transfer [16].
Song et al. [15] demonstrated that thrust calibration errors rep-
resent the dominant source of tracking degradation during this
transfer process. Open-source software ecosystems simplify
swarm coordination and simulated execution [6], [7], [28],
[30], and lower the barriers to entry for multi-agent research.
Despite this active development, each research group runs
its own private flight experiments and reports numbers against
its own reference trajectories. Without a shared dataset, dif-
ferences in results between papers reflect hardware setup as
much as algorithm design.
D. State Estimation for Micro Aerial Vehicles
State estimation on sub-50 g platforms faces extreme hard-
ware limitations. Visual-inertial odometry pipelines are sim-
ply too expensive for a 168 MHz Cortex-M4 [4], so nano-
quadrotors run lightweight EKFs with carefully characterized
IMU noise models [13], [17].
Evaluating these filters properly requires the estimator’s
internal state to be recorded alongside an external position
reference at matched timestamps. Without that pairing, it is
not possible to separate sensor noise from filter divergence or
to compare estimators across different hardware runs.
III. METHODOLOGY
A. Hardware Platform
We used the Crazyflie 2.1 nano-drone (Bitcraze AB), as
the data collection platform. The vehicle measures 92 × 92 ×
29 mm and weighs 27 g with a 250 mA h single-cell LiPo
installed. Four 7 × 16 mm coreless DC motors drive 46 mm
four-blade propellers; at full charge (4.2 V), combined peak
thrust is approximately 0.6 N, giving a thrust-to-weight ratio
of roughly 2.2. The onboard STM32F405 (168 MHz, Cortex-
M4F, 192 kB SRAM) runs a cascaded PID controller and
extended Kalman filter; a secondary nRF51822 handles radio
communication. Inertial data is provided by a Bosch BMI088
TABLE I: Comparison of aerial robotics datasets. NanoBench is the first to combine actuator-level data, onboard estimator
outputs, and controller internals on a commercially available nano-scale platform within a multi-task evaluation framework.
Feature
EuRoC [19]
Blackbird [23]
UZH-FPV [20]
Busetto et al. [25]
NanoBench (Ours)
Platform mass
∼2 kg
∼1 kg
∼0.8 kg
<50 g
∼27 g
Platform availability
Discontinued
Custom
Custom
Commercial
Commercial
Number of trajectories
11
176
27
4
170+
Ground truth system
Vicon/Leica
OptiTrack
Leica
MoCap
Vicon
Ground truth rate
200 Hz
360 Hz
200 Hz
Not specified
100 Hz
Raw IMU data
✓
✓
✓
–
✓
Motor commands
–
✓(RPM)
–
✓(RPM)
✓(PWM)
Onboard estimator output
–
–
–
–
✓
Controller internals
–
–
–
–
✓
Battery telemetry
–
–
–
–
✓
Camera data
Stereo
Synthetic
Stereo + event
–
–
Multi-task evaluation
–
–
–
SysID only
SysID + Control + Estimation
Calibration tools
–
–
–
–
✓
Open-source
✓
✓
Partial
✓
✓
TABLE II: Recorded signals and nominal sampling rates.
Signal
Source
Rate (Hz)
Position (p ∈R3), orientation (q ∈S3)
Vicon
100
Linear velocity ( ˙p ∈R3)
Vicon (derived)
100
Accelerometer (aIMU ∈R3) [G]
BMI088
100
Gyroscope (ωIMU ∈R3) [rad/s]
BMI088
100
EKF state (ˆp, ˆ˙p, ˆη)
Firmware
100
Controller setpoints (pref, ψref)
Firmware
100
PID outputs (roll, pitch, yaw, thrust)
Firmware
100
Motor PWM (u1, u2, u3, u4 ∈[0, 65535])
Firmware
100
Battery voltage Vbat [V]
Firmware
10
six-axis IMU. Motor commands are 16-bit PWM values in
[0, 65535], and the unregulated single-cell battery directly
couples state of charge to actuator performance.
Ground truth 6-DoF pose is provided by a 12-camera Vicon
system covering a 6×4×2 m volume. Retroreflective markers
(6.4 mm diameter) in an asymmetric configuration enable
unique rigid-body identification at 100 Hz with sub-millimeter
accuracy.
B. Data Acquisition Pipeline
Data collection uses a custom ROS 1 framework that com-
municates with the Crazyflie via cflib over a Crazyradio PA
USB dongle. Three concurrent data paths operate during each
flight:
Vicon
path. A vrpn_client_ros node
publishes
geometry_msgs/PoseStamped messages on a per-rigid-
body topic at 100 Hz. The ViconRecorder module sub-
scribes to this topic, computes linear velocity via first-order
backward difference, converts quaternion orientation to Euler
angles, and writes each sample to a CSV file. On every
callback, the pose is also forwarded to the Crazyflie EKF via
cflib’s send_extpose() to provide the onboard estimator
with an external position reference.
Firmware telemetry path. The CflibLogger module
configures firmware log blocks as specified in a YAML con-
figuration file. Each block declares a set of firmware variables,
their data types, and a polling frequency. The cflib library
fetches these variables over the CRTP radio protocol. Upon
reception, each sample is timestamped with both the host wall-
clock time and the Crazyflie firmware tick (milliseconds since
boot) and written to a per-block CSV file. Table II enumerates
the recorded signals.
Command path. The ExperimentRunner orchestrates
the flight sequence. High-level commands (takeoff, land)
use the firmware’s onboard trajectory planner, which gener-
ates smooth polynomial setpoints internally. During trajec-
tory execution, position setpoints are streamed at 100 Hz via
send_position_setpoint(), which bypasses the high-
level planner and feeds the PID controller directly.
C. Time Synchronization
Three clocks run independently during each flight: the Vicon
Tracker, the Crazyflie firmware tick counter, and the ROS host.
The host timestamps Vicon poses and firmware packets on
arrival, which places both streams in a shared reference frame.
Residual alignment offset arise from radio transmission latency
(typically 2 ms to 5 ms) and operating system scheduling jitter.
We estimate this offset by cross-correlating the onboard
gyroscope ωgyro(t) with the angular velocity ωvicon(t) obtained
by differentiating Vicon quaternions through a Savitzky–Golay
filter. The time offset ∆t∗is estimated as
∆t∗= arg max
∆t
X
k
ωgyro(tk) · ωvicon(tk + ∆t)
(1)
where the search range is ∆t ∈[−2, 2] s at 1 ms resolu-
tion. This formulation exploits the sharp rotational features
present during flight maneuvers to localize the offset with sub-
millisecond precision.
Once ∆t∗is found, firmware signals are shifted to the
Vicon time base and resampled onto a uniform grid by linear
interpolation. Each trajectory is then written to a single csv
file with all modalities on one time axis.
D. Trajectory Design
The trajectory taxonomy is organized into three active cate-
gories designed to collectively excite all dynamic modes of the
platform. The dataset encompasses 12 distinct trajectory types
spanning system identification excitation, geometric tracking
1.5
0.0
1.5
x (m)
1.5
0.0
1.5
y (m)
Circle
1.5
0.0
1.5
x (m)
1.5
0.0
1.5
y (m)
Figure-8
1.5
0.0
1.5
x (m)
1.5
0.0
1.5
y (m)
Oval
0.6
0.0
0.6
x (m)
0.8
0.0
0.8
y (m)
Star
0.8
0.0
0.8
x (m)
1
0
1
y (m)
Lissajous
1
0
1
x (m)
0
2
z (m)
Staircase
1
0
1
1
0
1
0
2
Trefoil
1
0
1
1
0
1
0
2
Helix
1.5
0.0
1.5
1.5
0.0
1.5
0.0
2.5
Random WP
0.5
0.0
0.5
0.5
0.0
0.5
1.5
Multisine
0.5
0.0
0.5
0.5
0.0
0.5
0.0
0.6
Linear Ramp
0.08
0.00
0.08
0.08
0.00
0.08
1
Hover
Fig. 1: All 12 NanoBench trajectory types visualized from recorded Vicon ground-truth data. Categories A (excitation), B
(geometric tracking), and C (battery-drain hover).
TABLE III: Category B: Tracking Trajectory Parameters.
Trajectory Type
Complexity Mode
Scale (m)
Speed (m/s)
Circle
Continuous yaw
r = 1.0
0.5, 0.75, 1.0
Figure-8
Direction reversal
A ∈{1.0, 1.3}
0.5, 0.75, 1.0
Oval
Asymmetric axes
1.0 × 0.4
0.5, 0.75, 1.0
Star
Sharp transients
r ∈{0.6, 1.0}
0.5, 0.75, 1.0
Lissajous (3:2)
Dense planar
A = 0.6
0.5, 0.75, 1.0
Trefoil Knot
3D oscillation
∆z = 0.15
0.5, 0.75, 1.0
Helix
Sweeping altitude
∆z = 1.0
0.5, 0.75, 1.0
Linear Ramp
1D acceleration
L = 2.0
0.5, 0.75, 1.0
Random Waypoint
Unstructured 3D
Volume bound
0.75
Staircase
Vertical steps
∆z = 0.5
0.5
at multiple speeds, and long-duration battery-drain hovers.
Fig. 1 visualizes all 12 types from recorded flight data.
Category A: System identification excitation. Multi-sine
trajectories superimpose sinusoidal position commands at log-
arithmically spaced frequencies from 0.1 Hz to 5 Hz:
x(t) =
Nf
X
n=1
A
n sin(2πfnt),
y(t) =
Nf
X
n=1
A
n cos(2πfnt + π
4 )
(2)
where A is the amplitude, fn are logarithmically spaced,
and the phase offset between axes ensures simultaneous
two-axis excitation. Category A consists of a single trajec-
tory(A1b_multisine_sysid), which executes a 60 s 3D
multi-sine at altitude ≈1.1 m with Nf = 15 components
spanning [0.1, 5] Hz, amplitudes of 0.8 m (horizontal) and
0.35 m (vertical), and smooth 2 s fade-in/out windows.
Category B: Standard trajectory tracking. Ten geometric
trajectories exercise complementary dynamic modes at multi-
ple speeds. Table III defines the parameterization for this suite.
Most shapes are parameterized symmetrically, such as the cir-
cular paths defined by x(t) = r cos(ωt) and y(t) = r sin(ωt)
where ω = v/r. Execution speeds range from 0.5 m s−1 to
1.0 m s−1, representing the practical operating envelope for
nano-quadrotors in confined environments.
Category C: Battery-drain. Two long-duration hover
flights (C4_battery_drain) provide continuous record-
ings from ≈4.2 V down to ≈3.1 V while the vehicle
holds position at ≈1.0 m, explicitly capturing voltage-related
degradation across the full discharge curve. These flights last
101–134 s and serve both the voltage-conditioned thrust model
and as battery-state benchmarks for all three tasks.
E. Benchmark Task Formulation
NanoBench establishes standardized protocols for three
distinct evaluation tasks.
Task 1: System Identification. This task requires algo-
rithms to predict the 6-DoF state trajectory ˆx(t) over horizons
h ∈{0.1, 0.5, 1.0} s given initial conditions and motor com-
mands {u(k)
i
}. Formulations must model rigid-body dynamics
in the world frame W:
m¨p = R(q)


0
0
P
i Ti

−mg e3 −Dt ˙p
(3)
J ˙ω = τ −ω × Jω −Drω
(4)
where R(q) ∈SO(3) is the rotation from body to world
frame, Dt and Dr are diagonal drag matrices, and τ is the
torque vector. Training utilizes Category A data at nominal
voltage (V > 3.8 V); testing utilizes Categories B and C across
the full discharge curve.
For each rollout initialized at t ∈T , the model gener-
ates open-loop predictions ˆyt+h|t for h = 1, . . . , H. The
component-wise prediction error at horizon h is
e(c)
t,h =



x(c)
t+h −ˆx(c)
t+h|t

2 ,
c ∈{p, v, ω},
2 atan2(∥qv∥2 , qw) ,
c = R,
(5)
where x(c) denotes the corresponding Euclidean state compo-
nent and [qv qw]⊤= q−1
t+h ⊗ˆqt+h|t is the relative quaternion.
The mean absolute error at horizon h and its cumulative H-
step variant are
MAE(c)(h) =
1
|T |
X
t∈T
e(c)
t,h,
MAE(c)
1:H =
H
X
h=1
MAE(c)(h).
(6)
Task 2: Controller Benchmarking. This task evaluates
closed-loop geometric tracking performance. Controllers ex-
ecute paired Category B reference trajectories pref(t), and
all evaluation pairs are subsetted to matched initial battery
voltages (∆V
≤0.05 V) to isolate controller performance
from voltage-induced thrust variation. The position tracking
error at time step k is
ep(k) =
p(tk) −pref(tk)

2
(7)
Aggregate performance is reported as tracking RMSE and
95th-percentile deviation across all k. Control effort is reported
as
Eu = 1
N
N
X
k=1
4
X
i=1
ui(k)2
(8)
For real-flight controllers, each condition is repeated five
times, offline controllers use deterministic rollouts and are
reported without repetition.
Task 3: State Estimation. This task isolates the accuracy
of lightweight onboard estimators against Vicon ground truth.
The estimator is configured at takeoff and runs exclusively for
the duration of that flight. Estimator output ˆp(tk) is evaluated
against ground truth pgt(tk) using Absolute Trajectory Error
(ATE), computed after aligning the estimated trajectory to
ground truth via Horn’s SE(3) method:
ATE =
 
1
N
N
X
k=1
pgt(tk) −T ˆp(tk)
2
2
!1/2
(9)
where T is the rigid transformation returned by the alignment.
Additional metrics include Relative Trajectory Error (RTE)
over localized sliding windows, per-axis velocity residuals, and
attitude RMSE in Euler angles. Each condition is repeated five
times per estimator per trajectory type; results are reported as
mean ± standard deviation across runs.
IV. EXPERIMENTAL VALIDATION AND RESULTS
A. Dataset Statistics
NanoBench contains 12 fully post-processed trajectories
spanning Categories A through C, with a total aligned flight
time of approximately 97.5 min and 603,942 synchronized
samples at 100 Hz. Table IV reports per-category statistics.
Battery voltage across the dataset spans 3.08 V to 4.2 V,
which covers the full operational discharge curve of a single-
cell LiPo. The Category B tracking trajectories operate in the
mid-to-nominal voltage regime (3.8 V to 4.2 V). Category C
battery-drain hovers capture the complete discharge from ≈
4.2 V to ≈3.1 V.
TABLE IV: Trajectory categories in the NanoBench dataset.
Category
Trajectory types
Flight time
Samples
A: Excitation
Multi-sine (3D)
8.5 min
61,404
B: Tracking
Circle, figure-8, oval, star,
82.0 min
491,970
trefoil, lissajous, helix, ramp,
random waypoints, staircase
C: Battery-drain
Battery-drain hover
7.0 min
50,568
Total
97.5 min
603,942
10
20
30
40
50
Prediction horizon
0.0
0.2
0.4
0.6
Position MAE [m]
LSTM
Naive
Phys+Res
Physics
Residual
Fig. 2: Task 1: Position MAE grows monotonically with pre-
diction horizon for all models. The physics model dominates
at h = 1 but diverges beyond h = 15 steps. The hybrid model
achieves the lowest cumulative error.
The synchronization pipeline (Section III-C) was validated
across all 170 post-processed trajectories. The estimated clock
offset between the firmware and Vicon time bases has a
median of 282 ms with a standard deviation of 17.3 ms across
flights, which is within the latency of the radio link. After
correction, residual alignment precision is limited by the cross-
correlation resolution (1 ms search grid at 100 Hz) and the
peak correlation coefficient, which ranges from 0.51 (staircase
climb, low angular excitation) to 0.94 (multisine, high angular
excitation).
B. Task 1: System Identification Baselines
1) Baselines: We evaluated five baseline models of increas-
ing complexity, to benchmark Task 1. All models are trained
on the multisine excitation flight (80/20 train/validation
split) and tested on held-out Category B tracking trajectories,
listed in Table III. Below, we briefly explain the baselines for
Task 1, which are adapted from Busetto et al. [25].
Naive baseline. A constant extrapolation model that pre-
dicts ˆx(tk + h) = x(tk) for all horizons h. This serves as a
simple lower bound.
Physics model. A rigid-body dynamics model implement-
ing (3)–(4) with a quadratic motor-thrust map and fourth-
order integration at 100 Hz. The baseline airframe weighs 27 g,
with three retroreflective markers and the wireless charging
deck attached, the total flying mass is 40.85 g. All dynamics
models use the measured flying mass, and inertia and drag
parameters are taken from [25]. This model is not learned; it
uses calibrated but fixed parameters.
Residual MLP. A feedforward network operating in the
12D state space (position, velocity, SO(3) rotation vector,
angular velocity) predicts a residual ∆x on top of the current
state. The network consists of five fully connected layers with
64 hidden units and ReLU activations. It is trained to minimize
a horizon-weighted mean-squared error over 50-step prediction
windows using Adam and cosine-annealed learning rate.
Physics + residual. A hybrid model that composes the
physics baseline with the residual MLP. The physics model
is run in closed loop to obtain a normalized prediction ˆxphys,
and the residual network predicts a correction in the same
normalized space.
LSTM. A recurrent model that conditions on the initial
state x0 and the sequence of motor commands. A single-layer
LSTM with 64 hidden units processes the control sequence
and outputs per-step state increments, which are accumulated
to obtain the predicted trajectory. As in the MLP case, training
minimizes a horizon-weighted MSE over 50-step windows.
For all learned models we use batch size 256, an exponential
temporal weighting factor λ = 0.1 in the loss, and train for
500 epochs.
2) Results and Analysis: Table V reports MAE per state
component at horizons h ∈{1, 10, 50} steps and the cumula-
tive score over h = 1 . . . 50. Based on Table V and Fig. 2, we
find the following three observations:
First-principles accuracy degrades rapidly beyond short
horizons. At h=1 (10 ms), the physics model achieves sub-
millimeter position MAE (0.3 mm), significantly lower than
naive extrapolation (5.7 mm), which shows that rigid-body
dynamics accurately describe the immediate state evolution
of the platform. However, the advantage reverses sharply
at longer horizons, by h=50, physics-model position MAE
reaches 636 mm, 2.2 times worse than naive. The velocity
channel reveals the mechanism. Physics-model velocity MAE
grows from 51 mm s−1 at h=1 to 2.57 m s−1 at h=50, which
indicates that small thrust-modeling errors compound through
numerical integration and corrupt the translational state.
The hybrid architecture achieves the best cumulative
accuracy. The physics + residual model achieves the lowest
cumulative position simulation error and outperforms the pure
residual MLP (5.68 m) and the LSTM (5.92 m). The advantage
is most distinct at h=10, where it achieves 12.1 mm position
MAE, 3.7 times lower than the residual MLP and 2.7 times
lower than the LSTM. At h=50, however, the pure residual
MLP achieves the lowest position MAE (228 mm), which
suggests that the physics component eventually introduces
compounding errors that the residual correction only partially
absorbs. The crossover between these two models near h = 30
defines a practical horizon boundary for each architecture.
Translational and rotational objectives trade off under
a joint loss. The LSTM achieves competitive velocity MAE
(0.48 m s−1 at h=50, second only to naive), but its angular
velocity MAE reaches 5.15 rad s−1, an order of magnitude
above the naive baseline (0.45 rad s−1). The physics model
produces identical angular velocity predictions to naive at all
horizons because the implementation holds ˙ω ≡0, which re-
0
1
x [m]
−0.5
0.0
0.5
y [m]
40
41
42
43
44
45
Time [s]
1.00
1.02
1.04
z [m]
GT
Baseline
Physics
Residual
Phys+Res
LSTM
Fig. 3: Task 1: Predicted (colored) vs. Vicon ground-truth
(black) trajectories for each baseline on a held-out Category B
(Helix trajectory) sequence, along each axis.
flects the difficulty of modeling torque transients from coreless
DC motors without dedicated angular acceleration data.
Figure 3 visualizes the baselines predicted versus ground-
truth trajectories on Helix trajectory as a test sequence.
C. Task 2: Controller Benchmarking
1) Baselines: We benchmark five controllers across two
distinct evaluation paradigms to separate physical hardware
performance from idealized, data-driven rollout. Real-flight
controllers execute directly onboard the platform, utilizing
Vicon ground truth for state estimation: (1) PID, the default
firmware’s cascaded PID formulation; and (2) Mellinger, a
geometric tracking controller operating on SE(3) [29]. Con-
versely, Offline-learned controllers are trained from logged
flight data and evaluated via closed-loop rollouts against a
learned dynamics model: (3) BC-MLP and (4) BC-LSTM,
which are behavior cloning policies trained via supervised
imitation of the onboard PID utilizing the imitation frame-
work [31]; and (5) MPPI [32], a Model Predictive Path
Integral controller using a neural network forward model
trained on the same dataset. Given the fundamental disparity
between the physical environment and the learned simulator,
hardware and offline metrics are reported independently in
Table VI to prevent invalid direct comparisons.
2) Results and Analysis: Table VI details the position and
velocity Root Mean Square Error (RMSE), position Average
Displacement Error (ADE), heading error, and trajectory di-
vergence rate for all baselines.
On hardware, the geometric controller reduces diver-
gence at the cost of higher velocity transients. In phys-
ical flight, PID and Mellinger demonstrate nearly identical
position tracking, yet they diverge significantly in robustness
and velocity regulation. The cascaded PID exhibits a 4.20 %
TABLE V: Numerical performance at h = 1, 10, 50. The italic column reports the cumulative simulation error (sum of MAEs
over h = 1..50).
MAEp,h [m]
MAEv,h [m/s]
MAER,h [rad]
MAEω,h [rad/s]
Model
h=1
h=10
h=50
h=1:50
h=1
h=10
h=50
h=1:50
h=1
h=10
h=50
h=1:50
h=1
h=10
h=50
h=1:50
Naive
0.0057
0.0585
0.2866
7.3866
0.0085
0.0786
0.3542
9.4178
0.0033
0.0285
0.0915
2.7563
0.0402
0.2602
0.4524
17.1131
Physics
0.0003
0.0265
0.6364
10.9641
0.0511
0.5085
2.5673
65.0322
0.0019
0.0198
0.1425
3.2693
0.0402
0.2602
0.4524
17.1131
Residual
0.0045
0.0445
0.2282
5.6810
0.0121
0.1096
0.6708
16.9002
0.0084
0.1051
0.1971
8.8737
0.2043
1.1173
1.3046
54.1783
Phys+Res
0.0036
0.0121
0.2621
4.4071
0.0201
0.1370
1.0771
26.7469
0.0065
0.1359
0.1825
9.8645
0.8784
1.5799
1.1781
55.3050
LSTM
0.0058
0.0332
0.2562
5.9194
0.0199
0.1077
0.4782
11.9639
0.0162
0.1339
0.3059
9.8302
0.1256
0.8159
5.1525
118.0662
TABLE VI: Task 2: Controller Benchmarking Results
Type
Method
RMSEp↓
ADEp↓
ADEp↓
¯eψ↓
Div. (%)↓
(m)
(m)
(m/s)
(deg)
Real flight
PID
0.29±0.03
0.27±0.02
0.72±0.14
5.82±0.58
4.20±2.46
Mellinger
0.28±0.00
0.27±0.00
0.89±0.18
5.27±1.61
0.01±0.01
Offline learned
BC-MLP
0.15±0.00
0.13±0.00
0.19±0.00
1.07±0.00
0.00±0.00
BC-LSTM
0.18±0.00
0.16±0.00
0.22±0.00
0.97±0.00
0.00±0.00
MPPI
1.32±0.00
1.13±0.00
0.72±0.00
4.50±0.00
75.22±0.00
0
2
x [m]
1
0
1
y [m]
0
2
4
6
8
10
Time [s]
0
2
z [m]
GT
BC-MLP
BC-LSTM
MPPI
PID
Mellinger
Fig. 4: Task 2: Closed-loop position (xyz, m) for each baseline
vs. Ground Truth. Real-flight (PID, Mellinger) and offline
(BC-MLP, BC-LSTM, MPPI) trajectories.
(±2.46 %) trajectory divergence rate, whereas the Mellinger
controller reduces this to 0.01 %, representing a significant im-
provement. This enhanced reliability stems from the Mellinger
controller’s SE(3) formulation, which provides broader stabil-
ity guarantees that prevent the aggressive attitude divergence
occasionally observed with the PID. However, the Mellinger
controller yields a velocity RMSE (0.89 m s−1) that is 1.24×
higher than that of the PID (0.72 m s−1). This trade-off is con-
sistent with the geometric controller executing sharper attitude
corrections, which inherently induce velocity transients on a
0.7
0.8
0.9
m1
0.7
0.8
0.9
1.0
m2
0
10
20
30
Time [s]
0.7
0.8
0.9
m3
0
10
20
30
Time [s]
0.8
0.9
1.0
m4
GT
BC-MLP
BC-LSTM
Fig. 5: Task 2: Motor PWM outputs over time for each
controller baseline (normalized).
TABLE VII: Task 3: EKF state estimation accuracy on trefoil
trajectories. Mean ± std across all runs (pooled).
Speed
N
ATE RMSE (mm)
ATE Mean (mm)
RTE 1m (mm)
Vel RMSE (m/s)
Att RMSE (deg)
Slow
11
21.1 ± 3.3
16.5 ± 3.2
28.2 ± 6.8
0.069 ± 0.015
2.12 ± 0.05
Medium
10
21.8 ± 3.0
17.2 ± 1.7
30.3 ± 2.9
0.067 ± 0.013
2.71 ± 1.43
Fast
7
3142.7 ± 3936.6
2774.4 ± 3487.9
384.2 ± 400.8
7.629 ± 8.992
29.67 ± 28.52
nano-scale platform strictly bottlenecked by its 0.6 N peak
thrust authority. Heading errors remain comparable across
both PID and Mellinger. Qualitative tracking performance and
corresponding motor commands are visualized in Fig. 4 and
Fig. 5, respectively.
Offline-learned controllers are evaluated in simulation
and cannot be directly compared with real-flight re-
sults. BC-MLP and BC-LSTM achieve position RMSEs of
0.15 m and 0.18 m respectively, with zero divergence, but
these metrics reflect the idealized learned rollout plant rather
than physical flight readiness—the zero-variance confidence
intervals across all offline metrics confirm purely deterministic
evaluation. MPPI diverges on 75.22 % of trajectories (position
RMSE 1.32 m), indicating that its sampling-based optimiza-
tion is poorly matched to the narrow actuation limits of sub-
50 g platforms without domain-specific tuning.
MPPI exhibits severe performance degradation within
the nano-scale operational envelope. MPPI yields a position
RMSE of 1.32 m alongside a severe 75.22 % divergence rate.
This breakdown suggests that the receding-horizon optimizer
is either exploiting inaccuracies in the learned forward dynam-
ics model or that standard sampling parameters are ill-suited
for the exceptionally narrow actuation limits of sub-50 g vehi-
cles. The MPPI result confirms that NanoBench discriminates
between controllers suited to highly constrained platforms and
those requiring domain-specific tuning, an open challenge for
model-based predictive control on sub-50 g vehicles.
D. Task 3: State Estimation
1) Baselines: The onboard EKF runs at 100 Hz on the
STM32F405 and fuses IMU data with the Vicon pose relayed
via send_extpose() to produce the full 9-DoF state esti-
mate used during flight. It is configured at takeoff and runs for
the duration of that flight. Metrics are ATE after Horn’s SE(3)
alignment as in (9), RTE over 1 m path-length windows, per-
axis velocity residuals, and attitude RMSE in Euler angles.
2) Results and Analysis: Table VII reports EKF estimation
accuracy on trefoil knot trajectories over three speed regimes,
with all runs pooled (mean ± std across 28 trajectories).
0.0
50.0
Slow
0.0
50.0
Position error (mm)
Medium
0
20
40
60
80
100
Flight progress (%)
0
10k
Fast
Fig. 6: Task 3: EKF position error (mean ± std, all runs pooled
by speed) on trefoil trajectories. Error remains bounded at slow
and medium speeds but diverges at the fast regime.
At slow and medium speeds, the onboard EKF maintains
position tracking within 22 mm ATE RMSE (11 and 10 runs
respectively), with attitude RMSE below 3◦and velocity
RMSE below 0.07 m s−1. At the fast regime (1.0 m s−1), the
EKF exhibits divergence (ATE > 3 m across 7 runs), indicating
that the lightweight EKF on the STM32F405 cannot maintain
state consistency at the platform’s dynamic limits.
The RTE over 1 m path-length windows remains below
31 mm at slow and medium speeds, confirming local con-
sistency. Figure 6 visualizes the position error with standard
deviation bands (all runs pooled by speed).
The three tasks are linked by the same platform and
synchronized data: Task 1 open-loop dynamics error, Task 2
closed-loop tracking, and Task 3 estimator accuracy all reflect
the same underlying hardware and trajectory set. NanoBench
enables systematic comparison of baselines across the auton-
omy stack on a platform where no prior public benchmark
existed.
V. CONCLUSION
NanoBench introduces the first open-source, multi-task
benchmark for nano-scale quadrotors, collecting over 170
flight trajectories on the commercially standard Crazyflie 2.1
in a Vicon motion capture arena. It is distinguished from
prior aerial datasets by jointly providing synchronized motor
PWM commands, onboard EKF and PID controller internals,
and millimeter-accurate ground truth, signals that no existing
benchmark exposes at the nano scale.
Baseline evaluations across three tasks explained platform-
specific behaviors that larger-vehicle benchmarks cannot repli-
cate. In Task 1, rigid-body dynamics achieve sub-millimeter
one-step accuracy but diverge beyond a 100 ms horizon due
to compounding thrust-model error. In Task 2, the Mellinger
controller reduces trajectory divergence by two orders of
magnitude relative to the cascaded PID, while MPPI’s 75 %
divergence rate confirms that model-based predictive methods
require careful platform-specific tuning within the 0.6 N thrust
envelope. In Task 3, the onboard EKF maintains sub-22 mm
ATE at slow and medium speeds but loses consistency at
fast speed, marking the estimation boundary of the 168 MHz
Cortex-M4.
All data, code, and evaluation scripts are publicly available.1
REFERENCES
[1] E. Kaufmann, L. Bauersfeld, A. Loquercio, M. Mueller, V. Koltun, and
D. Scaramuzza, “Champion-level drone racing using deep reinforcement
learning,” Nature, vol. 620, pp. 982–987, 08 2023.
[2] M. O’Connell, G. Shi, X. Shi, K. Azizzadenesheli, A. Anandkumar,
Y. Yue, and S.-J. Chung, “Neural-fly enables rapid learning for agile
flight in strong winds,” Science Robotics, 2022.
[3] G. Torrente, E. Kaufmann, P. F¨ohn, and D. Scaramuzza, “Data-driven
mpc for quadrotors,” IEEE Robotics and Automation Letters, 2021.
[4] D. Palossi, N. Zimmerman, A. Burrello, F. Conti, H. Muller, L. M.
Gambardella, L. Benini, A. Giusti, and J. Guzzi, “Fully onboard ai-
powered human-drone pose estimation on ultralow-power autonomous
flying nano-uavs,” IEEE Internet of Things Journal, 2022.
[5] L. Brunke, M. Greeff, A. W. Hall, Z. Yuan, S. Zhou, J. Panerati, and
A. P. Schoellig, “Safe learning in robotics: From learning-based control
to safe reinforcement learning,” Annual Review of Control, Robotics,
and Autonomous Systems, 2022.
[6] L. Pichierri, A. Testa, and G. Notarstefano, “Crazychoir: Flying swarms
of crazyflie quadrotors in ros,” IEEE Robotics and Automation Letters,
2023.
[7] J.
A.
Preiss*,
W.
H¨onig*,
G.
S.
Sukhatme,
and
N.
Ayanian,
“Crazyswarm: A large nano-quadcopter swarm,” in IEEE International
Conference on Robotics and Automation (ICRA).
IEEE, 2017.
[8] S. I. Ullah and A. Muhammad, “Autonomous navigation and mapping
of water channels in a simulated environment using micro-aerial vehi-
cles,” in 2023 International Conference on Robotics and Automation in
Industry (ICRAI), 2023.
[9] S. Izzat Ullah, J. Baca, P. Rangel, T. Chu, and C. Rubio-Medrano,
“Pof+mader: Trajectory planner in dynamic environments with improved
collision avoidance,” IEEE Access, 2025.
[10] R. W. Deters, G. K. Ananda Krishnan, and M. S. Selig, “Reynolds
number effects on the performance of small-scale propellers,” in 32nd
AIAA applied aerodynamics conference, 2014, p. 2151.
[11] J. F¨orster, “System identification of the Crazyflie 2.0 nano quadrocopter,”
Master’s thesis, ETH Zurich, 2015, bachelor’s thesis.
[12] G. Shi, X. Shi, M. O’Connell, R. Yu, K. Azizzadenesheli, A. Anand-
kumar, Y. Yue, and S.-J. Chung, “Neural lander: Stable drone landing
control using learned dynamics,” in international conference on robotics
and automation (ICRA).
IEEE, 2019.
[13] D. Palossi, “On the autonomous navigation of nano-uavs,” Ph.D. disser-
tation, ETH Zurich, 2019.
[14] L. Bauersfeld, E. Kaufmann, P. Foehn, S. Sun, and D. Scaramuzza,
“Neurobem: Hybrid aerodynamic quadrotor model,” arXiv preprint
arXiv:2106.08015, 2021.
[15] Y. Song, A. Romero, M. Muller, V. Koltun, and D. Scaramuzza, “Reach-
ing the limit in autonomous racing: Optimal control versus reinforcement
learning,” Science Robotics, 2023.
[16] J. Eschmann, D. Albani, and G. Loianno, “Learning to fly in seconds,”
IEEE Robotics and Automation Letters, 2024.
[17] N. El-Sheimy and A. Youssef, “Inertial sensors technologies for naviga-
tion applications: State of the art and future trends,” Satellite navigation,
vol. 1, no. 1, p. 2, 2020.
[18] S. I. Ullah and J. Baca, “SynTraG: A synthetic trajectory generator for
non-cooperative dynamic obstacles in UAV navigation,” in Advances in
Automation and Robotics Research.
Springer, 2026.
[19] M. Burri, J. Nikolic, P. Gohl, T. Schneider, J. Rehder, S. Omari, M. W.
Achtelik, and R. Siegwart, “The euroc micro aerial vehicle datasets,”
The International Journal of Robotics Research, 2016.
[20] J. Delmerico, T. Cieslewski, H. Rebecq, M. Faessler, and D. Scaramuzza,
“Are we ready for autonomous drone racing? the uzh-fpv drone racing
dataset,” in 2019 International Conference on Robotics and Automation
(ICRA).
IEEE, 2019, pp. 6713–6719.
1https://github.com/syediu/nanobench-iros2026.git
[21] T.-M. Nguyen, S. Yuan, M. Cao, Y. Lyu, T. H. Nguyen, and L. Xie,
“Ntu viral: A visual-inertial-ranging-lidar dataset, from an aerial vehicle
viewpoint,” The International Journal of Robotics Research, 2022.
[22] C. Brommer, A. Fornasier, M. Scheiber, J. Delaune, R. Brockers,
J. Steinbrener, and S. Weiss, “Insane: Cross-domain uav data sets
with increased number of sensors for developing advanced and novel
estimators,” arXiv preprint arXiv:2210.09114, 2022.
[23] A. Antonini, W. Guerra, V. Murali, T. Sayre-McCord, and S. Karaman,
“The blackbird dataset: A large-scale dataset for uav perception in
aggressive flight,” in 2018 International Symposium on Experimental
Robotics (ISER), 2018. [Online]. Available: https://doi.org/10.1007/
978-3-030-33950-0 12
[24] P. Foehn, E. Kaufmann, A. Romero, R. Penicka, S. Sun, L. Bauersfeld,
T. Laengle, G. Cioffi, Y. Song, A. Loquercio, and D. Scaramuzza,
“Agilicious: Open-source and open-hardware agile quadrotor for vision-
based flight,” Science Robotics, 2022.
[25] R. Busetto, E. Cereda, M. Forgione, G. Maroni, D. Piga, and
D. Palossi, “Nonlinear system identification nano-drone benchmark,”
2025. [Online]. Available: https://arxiv.org/abs/2512.14450
[26] M. Wang, J. Zhou, X. Duan, D. Zhao, P. Cai, J. Zhai, X. Liu, and
C. Ren, “Nonlinear system identification for quadrotors with neural
ordinary differential equations,” in 2023 IEEE International Conference
on Unmanned Systems (ICUS), 2023, pp. 317–322.
[27] K. Y. Chee, T. Z. Jiahao, and M. A. Hsieh, “Knode-mpc: A knowledge-
based data-driven predictive control framework for aerial robots,” IEEE
Robotics and Automation Letters, 2022.
[28] C. Llanes, Z. Kakish, K. Williams, and S. Coogan, “Crazysim: A
software-in-the-loop simulator for the crazyflie nano quadrotor,” in IEEE
International Conference on Robotics and Automation (ICRA), 2024.
[29] D. Mellinger and V. Kumar, “Minimum snap trajectory generation
and control for quadrotors,” in 2011 IEEE international conference on
robotics and automation.
Ieee, 2011, pp. 2520–2525.
[30] J. Baca, S. I. Ullah, and P. Rangel, “Coaxial modular aerial system and
the reconfiguration applications,” in IEEE International Conference on
Robotics and Automation (ICRA), 2023.
[31] A. Gleave, M. Taufeeque, J. Rocamonde, E. Jenner, S. H. Wang,
S. Toyer, M. Ernestus, N. Belrose, S. Emmons, and S. Russell, “im-
itation: Clean imitation learning implementations,” arXiv:2211.11972v1
[cs.LG], 2022.
[32] G. Williams, N. Wagener, B. Goldfain, P. Drews, J. M. Rehg, B. Boots,
and E. A. Theodorou, “Information theoretic mpc for model-based
reinforcement learning,” in 2017 IEEE International Conference on
Robotics and Automation (ICRA), 2017.
