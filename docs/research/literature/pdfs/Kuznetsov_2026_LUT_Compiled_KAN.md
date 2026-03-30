1
LUT-Compiled Kolmogorov-Arnold Networks for
Lightweight DoS Detection on IoT Edge Devices
Oleksandr Kuznetsov†, Member, IEEE
Abstract—Denial-of-Service(DoS)attacksposeacriticalthreat Kolmogorov-Arnold Networks (KANs) [6] offer a promis-
to Internet of Things (IoT) ecosystems, yet deploying effective ingalternativebyleveragingtheKolmogorov-Arnoldrepresen-
intrusiondetectiononresource-constrainededgedevicesremains
tation theorem [7]. Unlike Multi-Layer Perceptrons (MLPs)
challenging. Kolmogorov-Arnold Networks (KANs) offer a com-
that apply fixed activation functions at nodes, KANs place
pact alternative to Multi-Layer Perceptrons (MLPs) by placing
learnable univariate spline functions on edges rather than fixed learnable univariate functions—typically implemented as B-
activations on nodes, achieving competitive accuracy with fewer splines—on network edges. This architectural difference en-
parameters. However, runtime B-spline evaluation introduces ablesKANstoachievecompetitiveaccuracywithsignificantly
significantcomputationaloverheadunsuitableforlatency-critical
fewer parameters and enhanced interpretability [8]. Recent
IoT applications. We propose a lookup table (LUT) compila-
applications in network security [9], [10] have demonstrated
tion pipeline that replaces expensive spline computations with
precomputed quantized tables and linear interpolation, dra- KANs’ effectiveness for intrusion detection tasks.
matically reducing inference latency while preserving detection Despite their parameter efficiency, KANs suffer from a
quality.OurlightweightKANmodel(50Kparameters,0.19MB) critical deployment bottleneck: runtime B-spline evaluation
achieves99.0%accuracyontheCICIDS2017DoSdataset.After
requires iterative knot interval search, recursive basis func-
LUT compilation with resolution L = 8, the model maintains
tion computation, and coefficient aggregation for each input
98.96%accuracy(F1degradation<0.0004)whileachieving68×
speedupatbatchsize256andover5000×speedupatbatchsize dimension—operations that dominate inference time on CPU
1, with only 2× memory overhead. We provide comprehensive architectures common in IoT gateways. This computational
evaluation across LUT resolutions, quantization schemes, and overheadunderminesthepracticaladvantagesofKANs’com-
out-of-bounds policies, establishing clear Pareto frontiers for
pact representation.
accuracy-latency-memory trade-offs. Our results demonstrate
Our Contribution. We address this deployment gap by
that LUT-compiled KANs enable real-time DoS detection on
CPU-onlyIoTgatewayswithdeterministicinferencelatencyand proposing a lookup table (LUT) compilation pipeline that
minimal resource footprint. transforms trained KAN models for efficient edge inference.
Our approach:
Index Terms—Kolmogorov-Arnold Networks, Denial-of-
Service detection, IoT security, lookup table quantization, edge 1) Eliminatesruntimesplineevaluationbyprecomputing
inference, intrusion detection systems discretized spline values into quantized lookup tables
2) Replaces iterative algorithms with simple table index-
I. INTRODUCTION
ing and linear interpolation
The proliferation of Internet of Things (IoT) devices has 3) Achieves 68× speedup at batch size 256 and over
created vast attack surfaces vulnerable to Denial-of-Service 5000× at batch size 1 with minimal accuracy loss
(DoS)attacks [1].Unliketraditional computingenvironments, 4) Provides comprehensive evaluation across LUT res-
IoTecosystemscompriseheterogeneousdeviceswithstringent olutions L ∈ {2,4,8,16,32,64,128,256}, quantization
resource constraints—limited memory, CPU-only processing, schemes, and boundary handling policies
and strict power budgets—making conventional deep learning Fig. 1 illustrates the LUT-KAN architecture. Our
approaches impractical for real-time threat detection [2]. lightweight model (78 input features → [32, 16] hidden
Machine learning-based intrusion detection systems (IDS) neurons → 1 output) achieves 99.0% accuracy on the
havedemonstratedremarkableaccuracyinidentifyingnetwork CICIDS2017 DoS dataset while occupying only 0.19 MB—
anomalies [3]. However, state-of-the-art models often require suitablefordeploymentonresource-constrainedIoTgateways.
substantial computational resources: SecEdge [4] achieves
98.7% accuracy on CICIDS2017, but demands 1.1–1.7 GB
II. RELATEDWORK
memory, while ALNS-CNN [5] requires high CPU utilization
A. IoT Intrusion Detection Under Edge Constraints
for its accelerated inference. This creates a fundamental ten-
sion between detection capability and deployability on edge Deploying IDS on IoT edge devices requires balancing
devices. detection accuracy against strict resource budgets. Recent
works have explored various approaches to this challenge.
O.KuznetsoviswiththeDepartmentofTheoreticalandAppliedSciences,
SecEdge [4] proposed a hybrid deep learning architecture
eCampus University, Via Isimbardi 10, Novedrate (CO), 22060, Italy, and
alsowiththeDepartmentofIntelligentSoftwareSystemsandTechnologies, achieving 98.7% accuracy on CICIDS2017, but requires 1.1–
SchoolofComputerScienceandArtificialIntelligence,V.N.KarazinKharkiv 1.7GBmemory.ALNS-CNN[5]introducedacceleratedlearn-
National University, 4 Svobody Sq., 61022 Kharkiv, Ukraine. E-mail: olek-
ing with 99.85% accuracy, though CPU utilization remains
sandr.kuznetsov@uniecampus.it,kuznetsov@karazin.ua
†Correspondingauthor:oleksandr.kuznetsov@uniecampus.it high. NIDS-DA [11] achieved 99.97% accuracy with only
6202
naJ
21
]GL.sc[
1v44080.1062:viXra

2
LUT-KAN Architecture for DoS Detection
III. BACKGROUNDANDMOTIVATION
Input KAN Layers with LUT-compiled functions Output A. IoT Edge Inference Constraints
(78 features) (1 neuron)
Hidden 1 Hidden 2 IntrusionDetectionSystemsforIoTnetworksoperateunder
(32 neurons) (16 neurons)
tighter constraints than conventional enterprise IDS. At the
edge, inference must often run on CPU-only platforms with
limited memory, energy budget, and strict latency constraints.
In many realistic deployments, predictions are required in an
online mode (near-real-time stream processing), where the
effective batch size is small (often batch=1). In this regime,
...
models that are accurate but require heavy runtime stacks,
B-spline LUT
dynamic dispatch, or expensive non-linear primitives become
Fig.1:LUT-KANarchitectureforDoSdetection.Thenetwork
impractical.
processes78flow-levelfeaturesthroughtwoKANlayerswith
DoS attacks generate high-volume and fast-changing traffic
32 and 16 neurons respectively. Each learnable ϕ function is
patterns. The IDS must therefore provide both high detection
compiled from B-splines to precomputed lookup tables for
quality and fast inference to avoid becoming a bottleneck or
efficient edge inference.
missing time-critical events. Key requirements include:
• Latency: Sub-millisecond inference for individual flows
5K parameters through data augmentation, demonstrating that • Memory:Modelsize<10MBfordeploymentalongside
compact models can maintain high detection rates. other services
Edge deployment strategies include hybrid CNN-LSTM • Determinism: Predictable inference time without
architectures [12], ensemble methods [13], and metaheuristic garbage collection pauses
optimization [14]. However, these approaches typically target • CPU-only:GPU/TPUaccelerationunavailableontypical
MLP or CNN architectures without addressing the unique IoT hardware
computational patterns of KAN-based models.
B. KAN Architecture and B-Spline Formulation
B. Kolmogorov-Arnold Networks for Security
AKANlayertransformsinputx∈Rnin tooutputh∈Rnout
KANs [6] have recently emerged as an alternative to
through:
MLPs for various tasks. The theoretical foundation—the
Kolmogorov-Arnold representation theorem—guarantees that (cid:88)
nin
h = ϕ (x ), j =1,...,n (1)
any multivariate continuous function can be represented as j ij i out
i=1
a superposition of univariate functions. Practical implementa-
where each ϕ is a learnable univariate function. In PyKAN-
tions use B-splines to approximate these univariate functions, ij
style implementations, ϕ is modeled as a sum of a base
enabling gradient-based learning. ij
branch and a spline branch:
In security applications, DeepOKAN [15] demonstrated
KANs’ potential for operator learning in mechanics prob- ϕ (x)=α ·b(x)+β ·s (x) (2)
ij ij ij ij
lems, establishing architectural patterns applicable to network
where b(·) is a fixed nonlinear function (e.g., SiLU), s (·) is
traffic analysis. KINN [9] applied KANs to physics-informed ij
a spline, and α ,β are learned scaling factors.
learning with competitive results. Recent work explored KAN ij ij
The spline branch is represented via B-splines on a knot
applicationsinloadforecasting[16],autonomousdriving[17],
sequence. Let {t }M be an augmented knot vector and let
and computation offloading in Industrial IoT [10]. However, u u=1
{c }P be spline coefficients. The degree-k B-spline basis
noneoftheseworksaddresstheinferenceefficiencychallenge m m=1
functions B (x) are defined recursively:
critical for IoT deployment. m,k
B (x)=I[t ≤x<t ] (3)
m,0 m m+1
C. Quantization and LUT-Based Inference
x−t t −x
B (x)= m B (x)+ m+k+1 B (x)
Post-training quantization [18] reduces model size and m,k t −t m,k−1 t −t m+1,k−1
m+k m m+k+1 m+1
accelerates inference by representing weights and activa- (4)
tions with lower-precision integers. For specialized hardware,
The spline value is computed as:
LUT-based approaches have shown remarkable efficiency.
PolyLUT [19] demonstrated FPGA implementations using P
(cid:88)
s (x)= c(ij)·B (x) (5)
polynomial approximations for ultra-low latency inference. ij m m,k
NeuraLUT [20] explored hiding neural network density in m=1
Boolean synthesizable functions, achieving significant latency The full model is a composition of L layers such layers,
improvements through learned lookup tables. followed by an output activation to produce a probability:
Our work differs by targeting CPU-only IoT devices and
pˆ(x)=σ(f (x)), yˆ=I[pˆ(x)≥τ] (6)
specifically addressing KAN’s B-spline evaluation bottleneck θ
through systematic LUT compilation with comprehensive where σ(·) is the logistic function, τ is the decision threshold
trade-off analysis. (we use τ =0.5), and θ denotes all model parameters.

3
C. Computational Bottleneck Analysis
For each input x , evaluating s (x ) requires: (1) locating
i ij i
theknotintervalcontainingx ,(2)recursivelycomputingk+1
i
non-zerobasisfunctions,and(3)aggregatingwithcoefficients.
On CPU, this sequential computation dominates inference
time—particularlyat batchsize1 wherevectorizationbenefits
vanish.
ThismotivatesacompilationviewofKANinference:ifthe
learned univariate functions are fixed at deployment time, we
can precompute their values on a grid and replace runtime
spline evaluation with fast table lookup and interpolation.
D. Problem Statement
Let the trained KAN model define, for each layer ℓ and
each edge (i → j), a univariate function ϕ(ℓ)(x). Standard
ij
inference evaluates ϕ(ℓ) via B-splines at runtime. We address
ij
the following deployment problem:
Fig.2:Featurecorrelationheatmapfortop15features.Strong
Given a trained KAN-based IDS model and a target CPU-
correlations exist within packet length statistics (upper-left
only inference environment, how can we reduce inference
cluster) and inter-arrival time features (center cluster).
latency while maintaining detection quality and controlling
memory overhead?
Inaddition,practicaldeploymentrequiresrobustnesstoout-
of-domain inputs. Network telemetry may drift because of
changesintrafficdistributions,featurescalingissues,orsensor
noise. Therefore, the LUT representation must define explicit
behavior for out-of-bounds (OOB) inputs.
IV. MODELSANDMETHODS
Fig.3:Trainingdynamicsover200epochs.Left:Lossconver-
A. Dataset and Task Definition
gence showing stable optimization without overfitting. Right:
We use the CICIDS2017 dataset [21] and focus on a DoS
Accuracy progression demonstrating rapid initial learning fol-
detectionscenario.Eachrecordcorrespondstoanetworkflow
lowed by gradual refinement.
described by a vector of tabular features. The supervised task
is binary classification: benign vs. DoS. Let x ∈ Rd denote
the feature vector and y ∈{0,1} the ground-truth label. B. KAN Model Architecture and Training
Table I summarizes the dataset composition after prepro-
Ourdetectionmodelemploysatwo-layerKANarchitecture:
cessing.
Input(78)→KAN (32)→KAN (16)→Output(1) (7)
1 2
TABLE I: CICIDS2017 Wednesday DoS Dataset Statistics
Each KAN layer uses cubic B-splines (k =3) with G=5
Class Samples Percentage gridintervals,yieldingG+k =8controlpointsperspline.The
model totals 50,092 parameters (42,336 trainable) occupying
Benign 440,031 95.2%
DoSHulk 231,073 – 0.19 MB in float32 representation.
DoSGoldenEye 10,293 – TrainingProcedure.Wetrainthemodelbyminimizingthe
DoSslowloris 5,796 –
binary cross-entropy loss:
DoSSlowhttptest 5,499 –
Heartbleed 11 –
N
1 (cid:88)
TotalAttack 252,672 4.8% L(θ)=− [y logpˆ(x )+(1−y )log(1−pˆ(x ))]
N n n n n
n=1
(8)
Preprocessing.Followingestablishedprotocols[3],we:(1)
OptimizationisperformedwithAdamWoptimizer(learning
remove constant and duplicate features, (2) apply the 3σ rule
rate 10−3, weight decay 10−4) for 200 epochs with batch
for outlier removal, (3) impute missing values with median,
size 256. An 80/20 stratified train/test split ensures balanced
(4) standardize to zero mean and unit variance, and (5) bal-
evaluation. Fig. 3 shows the training dynamics.
ance classes through stratified sampling (231,073 samples per
class). The final feature set comprises 78 flow-level statistics.
C. LUT Compilation and Quantization
Fig. 2 shows the correlation heatmap for the top 15 most
correlatedfeatures,revealingdistinctclustersrelatedtopacket After training, we compile the spline branch of each ϕ
ij
timing (IAT features) and size statistics. into a lookup-table representation. For each spline segment,

4
we sample L points uniformly in the segment domain and
precompute spline values. At inference time, for an input x,
we: (i) identify the segment index, (ii) compute a normalized
position within the segment, and (iii) perform linear interpo-
lation between adjacent LUT values.
Let the segment domain be [a,b] and let {v }L−1 denote
q q=0
precomputed values at grid points x = a+q∆ with ∆ =
q
(b−a)/(L−1). For any x ∈ [a,b], define u = (x−a)/∆,
Fig. 4: Baseline model evaluation curves. Left: ROC
q =⌊u⌋, and λ=u−q. The interpolated value is:
curve with AUC=0.999. Right: Precision-Recall curve with
AP=0.999 demonstrating robust performance.
s˜ (x)=(1−λ)·v +λ·v (9)
ij q q+1
Symmetric int8 Quantization. We quantize LUT values
V. EXPERIMENTALRESULTS
per segment using:
A. Experimental Setup
(cid:16)(cid:106)v(cid:109) (cid:17)
q =clip ,−127,127 , vˆ=s·q (10) AllexperimentsexecuteonasingleAMDRyzen77840HS
s
processor (8 cores, 3.8 GHz base) with 64 GB DDR5 RAM,
where s is a segment-wise scale, and ⌊·⌉ denotes rounding to running Windows 11 with Python 3.10. We report CPU-only
nearest integer. performance to reflect IoT deployment conditions.
Asymmetric uint8 Quantization. For affine quantization: Latency Measurement Protocol. We measure infer-only
latency,whichexcludesdataloading,preprocessing,andpost-
(cid:18)(cid:22) (cid:25) (cid:19)
v−v
q =clip min ,0,255 , vˆ=v +s·q (11) processing. Each measurement consists of: (1) 10 warm-up
s min iterationstoensureJITcompilationandcachestabilization,(2)
100timediterations,(3)reportingmeanandstandarddeviation
where v and s are stored per segment.
min
across 5 independent calibration seeds. All measurements
use single-threaded execution (NUMBA_NUM_THREADS=1,
D. Out-of-Bounds Policies and Boundary Modes OMP_NUM_THREADS=1) to simulate resource-constrained
IoT environments. The baseline latency is measured using
The LUT representation must define behavior for inputs
PyKAN’s native B-spline evaluation with the same threading
outside the trained spline domain. We consider two OOB
constraints.
policies:
LUT Compilation Configuration. Un-
• clip x: clip x into the valid domain and evaluate the less stated otherwise, LUT compilation uses
boundary segment value_repr=spline_component, interp=linear,
• zero spline: return 0 for the spline branch when x is and we sweep the LUT resolution L ∈
out-of-range {2,4,8,16,32,64,128,256}. We evaluate both quantization
schemes: symmetric int8 and asymmetric uint8. Main results
We also consider two boundary modes for segment index-
use the robust setting (half_open + zero_spline).
ing: closed (inclusive boundary) and half_open (half-
open intervals), which affect how exact knot boundary values
are mapped to segments. B. Baseline Model Performance
The float KAN model achieves strong detection perfor-
mance, as shown in Table II. Fig. 4 shows the ROC and
E. Evaluation Metrics
Precision-Recall curves demonstrating near-perfect classifica-
We report thresholded classification metrics at τ = 0.5: tion capability.
Accuracy,Precision,Recall,andF1.Wealsoreportthreshold-
free metrics: ROC-AUC and PR-AUC. Let TP, FP, TN, FN TABLE II: Baseline KAN Model Performance
denote confusion matrix counts; then:
Metric Value
TP TP
Accuracy 99.0%
Precision= , Recall= (12)
TP+FP TP+FN Precision 98.4%
Recall 99.6%
2·Precision·Recall
F1= (13) F1Score 99.0%
Precision+Recall ROC-AUC 0.999
PR-AUC 0.999
Latency is reported as milliseconds per sample in two
Parameters 50,092
regimes: batch=1 and batch=256. All reported numbers are ModelSize 0.19MB
mean ± standard deviation across n = 5 calibration seeds,
with 95% CIs computed as: Fig. 5 illustrates model robustness across decision thresh-
σ olds, with stable performance over a wide operating range
CI ≈µ±t · √ , t ≈2.776 (14)
95% 0.975,4 0.975,4 (τ ∈[0.1,0.9]).
5

5
0.05
0.00
0.05
0.10
0.15
0.20
Fig. 5: Model threshold analysis. (a) Performance metrics
0.25
remain stable across decision thresholds. (b) Precision-recall
trade-off curve. 0.30
0.35
2 4 8 16 32 64 128 256
TABLE III: Detection Quality on Test Split (mean across LUT Resolution L
n = 5 runs; std < 10−4 for all configurations). Baseline:
Acc=0.9899, F1=0.9900.
L Quant. Accuracy F1 ROC-AUC ∆F1
2 symint8 0.9874 0.9874 0.9991 -0.0026
2 asymuint8 0.9873 0.9874 0.9991 -0.0026
4 symint8 0.9886 0.9887 0.9991 -0.0013
4 asymuint8 0.9886 0.9887 0.9991 -0.0013
8 symint8 0.9895 0.9896 0.9991 -0.0004
8 asymuint8 0.9895 0.9896 0.9991 -0.0004
16 symint8 0.9896 0.9897 0.9991 -0.0003
32 symint8 0.9897 0.9898 0.9991 -0.0003
64 symint8 0.9898 0.9898 0.9991 -0.0002
128 symint8 0.9899 0.9899 0.9991 -0.0001
256 symint8 0.9900 0.9900 0.9991 <0.0001
C. LUT Quality Preservation
Table III presents comprehensive detection quality across
LUT resolutions and quantization schemes. Even at L = 2
(coarsest resolution), accuracy remains above 98.7%. At L=
8, the model achieves 98.96% accuracy with F1 degradation
of only 0.0004 from the float baseline.
Fig. 6 visualizes F1 degradation across resolutions.
D. Inference Latency Analysis
Fair Baseline Comparison. To ensure valid speedup
claims, we compare backends with matched implementations.
TableIVpresentsthefairbaselinecomparisonatL=8,where
both B-spline evaluation and LUT inference use the same
Numba JIT-compiled backend. This eliminates confounding
factors from Python interpreter overhead and library differ-
ences.
The dramatic speedup difference between batch sizes re-
flects the nature of the computational bottleneck: at batch=1,
PyKAN’s B-spline evaluation suffers from Python dispatch
overheadandlackofvectorization,whileLUTlookupremains
efficient. At batch=256, vectorization partially amortizes the
B-spline overhead, reducing the relative speedup.
Table V and Table VI present inference latency with 95%
confidence intervals for batch sizes 256 and 1, respectively.
Fig.7presentsthecomprehensiveaccuracy-latency-memory
trade-off.
E. Memory Footprint Analysis
Table VII details memory consumption across resolutions.
Fig.8showstheParetofrontierforspeedupversusmemory
ratio.
)stniop
egatnecrep(
1F
F1 Score Degradation from Float Baseline
Acceptable threshold
Fig. 6: F1 score degradation from float baseline across LUT
resolutions. All configurations with L ≥ 4 remain within the
acceptable threshold.
TABLE IV: Fair Baseline Comparison at L = 8 (Numba
backend for both)
Method Batch=1 Batch=256 Speedup(bs=1) Speedup(bs=256)
NumbaB-spline 158.9ms 0.878ms 1.0× 1.0×
NumbaLUT(int8) 0.025ms 0.013ms 6333× 68×
F. Quantization Scheme Comparison
Fig.9comparessymmetricint8andasymmetricuint8quan-
tization. Both achieve nearly identical F1 scores, indicating
that for DoS detection, the dominant factor is LUT resolution
L rather than quantization scheme.
G. OOB Handling and Robustness Analysis
Real-world deployment may encounter inputs outside the
training distribution. We analyze robustness by separately
evaluating in-range and out-of-bounds (OOB) samples.
OOB Characterization. In the test set, approximately
2.3% of feature values fall outside the trained spline domain
boundaries after standardization. These OOB values arise
primarily from extreme flow statistics (e.g., unusually large
packet counts or durations).
Table VIII presents results for different boundary handling
configurationsatL=4.Thezero_splinepolicyzerosthe
spline contribution for OOB inputs while preserving the base
branch, providing graceful degradation. The clip_x policy
clamps inputs to domain boundaries, which may introduce
artifacts for extreme values.
TheminimalF1differencebetweenconfigurationsindicates
that OOB handling is not critical for CICIDS2017 due to
the low OOB rate. However, for deployment scenarios with
potential distribution drift, we recommend half_open +
zero_spline as the default robust configuration.
H. Comparative Analysis
Table IX positions our approach against recent IoT IDS
methods. Direct latency comparison requires caution due to
different hardware platforms and measurement protocols.
Our LUT-KAN achieves competitive accuracy with the
smallest memory footprint and lowest reported latency among

6
99.2
99.1
99.0
98.9
98.8
98.7
98.6
98.5
2 4 8 16 32 64 128 256
LUT Resolution L
)%(
ycaruccA
(a) Detection Accuracy
10 1
LUT-KAN
Float baseline
2 4 8 16 32 64 128 256
LUT Resolution L
)elpmas/sm(
ycnetaL
(b) Inference Latency
104
Batch=256
Batch=1
103
2 4 8 16 32 64 128 256
LUT Resolution L
)BiK(
yromeM
(c) Memory Footprint
Fig.7:Accuracy-latency-memorytrade-offacrossLUTresolutions.(a)DetectionaccuracystabilizesaboveL=8.(b)Inference
latencyshowsoptimalspeedupatL=4–8.(c)MemoryfootprintscaleslinearlywithL.GreenshadedregionindicatesPareto-
optimal configurations.
TABLE V: Infer-only Latency, Batch=256 (Numba LUT). TABLE VII: Memory Footprint by LUT Resolution. Float
Baseline: 0.878±0.097 ms/sample. model: 195.7 KB.
L Quant. ms/sample(µ±σ) CI95% Speedup L LUTSize(KiB) RatiotoFloat
2 asymuint8 0.0129±0.0032 ±0.0040 68.0× 2 195.0 1.00×
2 symint8 0.0142±0.0043 ±0.0053 61.3× 4 260.0 1.33×
4 asymuint8 0.0130±0.0006 ±0.0008 64.7× 8 390.0 1.99×
4 symint8 0.0135±0.0007 ±0.0009 61.7×
16 649.8 3.32×
8 symint8 0.0132±0.0007 ±0.0009 63.2×
8 asymuint8 0.0130±0.0007 ±0.0009 63.6× 32 1,169.6 5.98×
16 symint8 0.0137±0.0010 ±0.0013 60.6× 64 2,209.1 11.29×
32 symint8 0.0157±0.0008 ±0.0010 59.7× 128 4,288.1 21.91×
64 symint8 0.0171±0.0006 ±0.0008 58.5× 256 8,446.1 43.16×
128 symint8 0.0178±0.0006 ±0.0007 55.5×
256 symint8 0.0160±0.0005 ±0.0006 56.2×
TABLEVI:Infer-onlyLatency,Batch=1(NumbaLUT).Base-
line: 158.9±28.7 ms/sample.
60
L Quant. ms/sample(µ±σ) CI95% Speedup 58
2 symint8 0.0250±0.0051 ±0.0063 5759× 56
4 symint8 0.0250±0.0009 ±0.0011 5885× 8 symint8 0.0250±0.0008 ±0.0010 6333×
54
16 symint8 0.0260±0.0008 ±0.0010 6042×
32 symint8 0.0260±0.0008 ±0.0010 6070×
52
64 symint8 0.0310±0.0051 ±0.0063 5066×
128 symint8 0.0320±0.0050 ±0.0062 4963×
50
256 symint8 0.0310±0.0044 ±0.0054 5107×
48
46
CPU-based methods. The key advantage is deterministic, sub-
millisecond inference suitable for real-time IoT deployment. 44
100 101
Memory Ratio (LUT / Float)
VI. DISCUSSION
A. From Baseline KAN to LUT-Compiled Inference
In our baseline (non-LUT) study, we implemented a
lightweightKAN-basedIDSforDoSdetectionwithacompact
modelfootprint(50Kparameters)andstrongpredictiveperfor-
mance (99% accuracy). The key argument was that KAN can
achievehighaccuracywithasmallparameterbudget,attractive
for IoT/edge environments.
However, the baseline KAN implementation relies on run-
time B-spline evaluation and a deep-learning stack (Py-
Torch/PyKAN).ThismakesCPUinferencesensitivetoPython
)×(
pudeepS
Speedup vs Memory Trade-off (Batch=256)
L=8
Pareto Optimal L=16 L=32
L=4
L=2 L=64
L=128
L=256
Fig.8:Speedupvs.memoryratioParetofrontier(Batch=256).
Configurations with L ∈ {4,8} achieve maximum speedup
with minimal memory overhead.
overhead, operator scheduling, and library dependencies, es-
pecially in low-batch regimes. The LUT-KAN compilation
targets exactly this bottleneck: it replaces spline evaluation
by a packed, table-driven execution path (NumPy/Numba),
while preserving the trained function shape up to controlled
approximation error.

7
0.992
0.991
0.990
0.989
0.988
0.987
0.986
2 4 8 16 32 64 128 256
LUT Resolution L
erocS
1F
(a) F1 Score by Quantization Scheme
68
66
64
62
60
Asym. uint8 58
Sym. int8
Float baseline 56
2 4 8 16 32 64 128 256
LUT Resolution L
)×(
pudeepS
TABLE IX: Comparison with State-of-the-Art IoT IDS. La-
(b) Speedup by Quantization Scheme (Batch=256)
tency values from original papers; direct comparison requires Asym. uint8
Sym. int8 caution due to different platforms.
Method Acc. Size Latency Platform
SecEdge[4] 98.7% 1.1–1.7GB – GPU
ALNS-CNN[5] 99.85% – ∼15ms† CPU
NIDS-DA[11] 99.97% 5Kparams – –
EDA-GWO-XGB[14] 99.87% – – CPU
LUT-KAN(Ours) 98.96% 0.4MB 0.013ms‡ CPU
Fig. 9: Quantization scheme comparison. (a) F1 scores are
†Per-batchlatency,batchsizeunspecified.
‡Per-sampleatbatch=256,AMDRyzen77840HS,single-threaded.
indistinguishable. (b) Speedup shows minor variations.
Multi-Objective Performance Comparison
TABLE VIII: Boundary and OOB Policy Ablation at L = 4
L=2
(symint8).AllconfigurationsachieveidenticalF1onin-range ( S b p s e = e 2 d 5 u 6 p ) L=4
L=8
samples. L=32
Speedup
(bs=1)
Boundary OOBPolicy F1(all/in-range) ms/sample(bs=256) ms/sample(bs=1)
closed clip x 0.9887/0.9889 0.015±0.006 0.029±0.009 0.8 1.0
closed zero spline 0.9887/0.9889 0.013±0.001 0.025±0.001 0.6
0.4
half open clip x 0.9887/0.9889 0.013±0.000 0.027±0.005 0.2
half open zero spline 0.9887/0.9889 0.013±0.001 0.025±0.001 Accuracy
B. Accuracy-Latency-Memory Trade-offs
Memory
Efficiency
Our results establish clear guidelines for LUT resolution
selection:
L = 2–4: Suitable for extremely constrained devices. F1 F1 Score
remains above 0.987—sufficient for first-stage filtering in Fig. 10: Multi-objective performance comparison across LUT
hierarchicaldetectionsystems.LUTsizeapproximatelyequals resolutions.L=8achievesthebestbalanceacrossallmetrics.
float model size.
L=8: Recommended default. Achieves 98.96% accuracy
Reduced Dependencies. Compiled LUT models require
with only 2× memory overhead and maximum speedup (58–
onlybasicarrayindexingandlinearinterpolation—eliminating
63× at batch=256, 6000× at batch=1). The sweet spot where
dependencies on numerical libraries for spline evaluation.
further resolution increases yield diminishing returns.
Hardware Acceleration Potential. The simple operations
L ≥ 16: Unnecessary for CICIDS2017; accuracy plateaus
map efficiently to SIMD instructions and could be further
while memory grows linearly.
accelerated with custom hardware or FPGA implementation.
Fig. 10 provides a multi-objective view comparing selected
configurations.
E. Limitations and Future Work
Platform Scope. Our evaluation uses x86 hardware; ARM-
C. Interpreting Recall Changes After LUT Compilation
based IoT devices may exhibit different characteristics due to
ItispossiblethatrecallslightlyincreasesafterLUTapprox- cache hierarchies and SIMD capabilities.
imationevenifaccuracyremainsunchanged.LUTcompilation Energy Consumption. We report latency but not direct
introduces a small, structured perturbation in the decision power measurements. However, the dramatic latency reduc-
function, which can move some borderline samples across the tion (63× fewer CPU cycles at batch=256) suggests propor-
fixedthreshold.Onimbalanceddata,asmallshiftcanincrease tional energy savings, as CPU power consumption correlates
recall while slightly decreasing precision. We interpret such strongly with active instruction count on modern processors.
effectsasthresholdsensitivityratherthansystematicimprove- For battery-powered IoT devices, this latency-to-energy proxy
ment; hence we report ROC-AUC and PR-AUC in addition to indicates that LUT-KAN could extend operational lifetime
thresholded metrics. significantly compared to B-spline evaluation. Rigorous en-
ergy profiling with hardware power meters on target ARM
platforms remains important future work.
D. Deployment Implications
Single Dataset. Validation on NSL-KDD, UNSW-NB15,
The LUT compilation approach offers several practical CICDDoS2019 would strengthen generalizability claims.
advantages: Multi-class Detection. Our binary formulation could be
Deterministic Inference. Unlike float B-spline evaluation extended to distinguish attack types, though this may require
with variable recursion depth, LUT lookup performs a fixed larger KAN architectures.
number of operations regardless of input values. This enables Future work will address ARM deployment with direct
precise timing analysis critical for real-time systems. energy profiling, explore quantization-aware training for im-

8
provedlow-resolutionperformance,andinvestigatemulti-class [8] M.H.Sulaiman,Z.Mustaffa,A.I.Mohamed,A.S.Samsudin,andM.I.
KAN architectures for fine-grained attack classification. Mohd Rashid, “Battery state of charge estimation for electric vehicle
usingKolmogorov-Arnoldnetworks,”Energy,vol.311,p.133417,2024.
[9] Y. Wang, J. Sun, J. Bai, C. Anitescu, M. S. Eshaghi, X. Zhuang,
VII. CONCLUSION T.Rabczuk,andY.Liu,“Kolmogorov–Arnold-informedneuralnetwork:
A physics-informed deep learning framework for solving forward and
WepresentedLUT-compiledKolmogorov-ArnoldNetworks inverse problems based on Kolmogorov–Arnold networks,” Computer
for lightweight DoS detection on IoT edge devices. Our ap- Methods in Applied Mechanics and Engineering, vol. 433, p. 117518,
2025.
proachaddressestheB-splineevaluationbottleneckbyreplac-
[10] J. Wu, R. Du, and Z. Wang, “Deep reinforcement learning with dual-
ing runtime spline computation with precomputed quantized Q and Kolmogorov–Arnold networks for computation offloading in
lookup tables and linear interpolation. industrialIoT,”ComputerNetworks,vol.257,p.110987,2025.
[11] V.Kumar,K.Kumar,M.Singh,andN.Kumar,“NIDS-DA:Detecting
On CICIDS2017, our lightweight KAN model (50K pa-
functionallypreservedadversarialexamplesfornetworkintrusiondetec-
rameters, 0.19 MB) achieves 99.0% detection accuracy. After tionsystemusingdeepautoencoders,”ExpertSystemswithApplications,
LUT compilation with resolution L=8, the model maintains vol.270,p.126513,2025.
[12] A. Nazir, J. He, N. Zhu, S. S. Qureshi, S. U. Qureshi, F. Ullah,
98.96% accuracy while achieving 63× speedup at batch size
A. Wajahat, and M. S. Pathan, “A deep learning-based novel hybrid
256 and over 6000× at batch size 1, with only 2× memory CNN-LSTM architecture for efficient detection of threats in the IoT
overhead. ecosystem,”AinShamsEngineeringJournal,vol.15,no.7,p.102777,
2024.
The results show a clear accuracy-latency-memory trade-
[13] W.F.Urmi,M.N.Uddin,M.A.Uddin,M.A.Talukder,M.R.Hasan,
off controlled primarily by L: small values provide near- S.Paul,M.Chanda,J.Ayoade,A.Khraisat,R.Hossen,andF.Imran,
float quality with modest memory growth, while larger val- “Astackedensembleapproachtodetectcyberattacksbasedonfeature
selectiontechniques,”InternationalJournalofCognitiveComputingin
ues approach lossless approximation at higher memory cost.
Engineering,vol.5,pp.316–331,2024.
Symmetric int8 and asymmetric uint8 quantization perform [14] D.D.BikilaandJ.Cˇapek,“Machinelearning-basedattackdetectionfor
similarly, suggesting that L and OOB handling are the main theInternetofThings,”FutureGenerationComputerSystems,vol.166,
p.107630,2025.
practical deployment knobs.
[15] D.W.Abueidda,P.Pantidis,andM.E.Mobasher,“DeepOKAN:Deep
LUT-KAN makes KAN-based IDS viable for IoT/edge operatornetworkbasedonKolmogorovArnoldnetworksformechanics
settings by reducing inference latency and simplifying the ex- problems,”ComputerMethodsinAppliedMechanicsandEngineering,
vol.436,p.117699,2025.
ecution path. The deterministic latency and minimal resource
[16] M.U.DanishandK.Grolinger,“Kolmogorov–Arnoldrecurrentnetwork
footprintmakethisapproachparticularlysuitableforreal-time for short term load forecasting across diverse consumers,” Energy
threat detection at the network edge. Reports,vol.13,pp.713–727,2025.
[17] J. Huang, R. Zhou, M. Li, H. Li, Y. Liu, and X. Song, “From
black-boxtowhite-box:Interpretabledeepreinforcementlearningwith
DATAAVAILABILITY Kolmogorov-Arnoldnetworksforautonomousdriving,”Transportation
ResearchPartC:EmergingTechnologies,vol.182,p.105386,2026.
The source code, trained models, and experimental data are [18] B.Jacob,S.Kligys,B.Chen,M.Zhu,M.Tang,A.Howard,H.Adam,
publicly available at: https://github.com/KuznetsovKarazin/ and D. Kalenichenko, “Quantization and training of neural networks
for efficient integer-arithmetic-only inference,” in Proceedings of the
kan-dos-detection/tree/lut-v2
IEEE Conference on Computer Vision and Pattern Recognition, 2018,
pp.2704–2713.
ACKNOWLEDGMENT [19] M.AndronicandG.A.Constantinides,“PolyLUT:Learningpiecewise
polynomialsforultra-lowlatencyFPGALUT-basedinference,”in2023
The author thanks the anonymous reviewers for their con- InternationalConferenceonFieldProgrammableTechnology(ICFPT).
structive feedback. IEEE,2023,pp.60–68.
[20] M.AndronicandG.Constantinides,“NeuraLUT:Hidingneuralnetwork
densityinbooleansynthesizablefunctions,”in202434thInternational
REFERENCES Conference on Field-Programmable Logic and Applications (FPL).
IEEE,2024,pp.140–148.
[1] C.Kolias,G.Kambourakis,A.Stavrou,andJ.Voas,“DDoSintheIoT: [21] I.Sharafaldin,A.H.Lashkari,andA.A.Ghorbani,“Towardgeneratinga
Miraiandotherbotnets,”Computer,vol.50,no.7,pp.80–84,2017. newintrusiondetectiondatasetandintrusiontrafficcharacterization,”in
[2] A. A. Diro and N. Chilamkurti, “Distributed attack detection scheme Proceedingsofthe4thInternationalConferenceonInformationSystems
usingdeeplearningapproachforInternetofThings,”FutureGeneration SecurityandPrivacy(ICISSP),2018,pp.108–116.
ComputerSystems,vol.82,pp.761–768,2018.
[3] C. Rajathi and P. Rukmani, “Hybrid learning model for intrusion
detection system: A combination of parametric and non-parametric
classifiers,” Alexandria Engineering Journal, vol. 112, pp. 384–396,
2025.
[4] K. A. Awan, I. Ud Din, A. Almogren, A. Nawaz, M. Y. Khan, and
Oleksandr Kuznetsov holds a Doctor of Sciences
A.Altameem,“SecEdge:Anoveldeeplearningframeworkforreal-time
degree in Engineering and is a Full Professor. He
cybersecurity in mobile IoT environments,” Heliyon, vol. 11, no. 1, p.
is an Academician at the Academy of Applied
e40874,2025.
Radioelectronics Sciences and the recipient of the
[5] S. Cherfi, A. Boulaiche, and A. Lemouari, “Exploring the ALNS
Boris Paton National Prize of Ukraine in 2021.
methodforimprovedcybersecurity:Adeeplearningapproachforattack
Additionally, he serves as a Professor at the De-
detectioninIoTandIIoTenvironments,”InternetofThings,vol.28,p.
partmentofTheoreticalandAppliedSciencesatthe
101421,2024.
eCampusUniversityinItaly.HeisalsoaProfessorat
[6] Z.Liu,Y.Wang,S.Vaidya,F.Ruehle,J.Halverson,M.Soljacˇic´,T.Y.
theDepartmentofIntelligentSoftwareSystemsand
Hou, and M. Tegmark, “KAN: Kolmogorov-Arnold networks,” arXiv
TechnologiesattheV.N.KarazinKharkivNational
preprintarXiv:2404.19756,2024.
University, Ukraine. His research primarily focuses
[7] A. N. Kolmogorov, “On the representation of continuous functions of
onappliedcryptologyandcodingtheory,blockchaintechnologies,theInternet
manyvariablesbysuperpositionofcontinuousfunctionsofonevariable
ofThings(IoT),andtheapplicationofAIincybersecurity.
and addition,” Dokl. Akad. Nauk SSSR, vol. 114, no. 5, pp. 953–956,
1957.

