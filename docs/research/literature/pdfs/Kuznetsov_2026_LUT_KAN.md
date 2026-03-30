LUT-KAN: Segment-wise LUT Quantization for
Fast KAN Inference
Oleksandr Kuznetsov1,2*
1Department of Theoretical and Applied Sciences (DiSTA), eCampus
University, Via Isimbardi 10, Novedrate, 22060, Italy.
2Department of Intelligent Software Systems and Technologies, School
of Computer Science and Artificial Intelligence, V.N. Karazin Kharkiv
National University, 4 Svobody Sq., Kharkiv, 61022, Ukraine.
Corresponding author(s). E-mail(s):
oleksandr.kuznetsov@ecampus.university; kuznetsov@karazin.ua;
Abstract
Kolmogorov–Arnold Networks (KAN) replace scalar weights by learnable uni-
variatefunctions,oftenimplementedwithB-splines.Thisdesigncanbeaccurate
and interpretable, but it makes inference expensive on CPU because each layer
requiresmanysplineevaluations.Standardquantizationtoolchainsarealsohard
to apply because the main computation is not a matrix multiply but repeated
splinebasisevaluation.ThispaperintroducesLUT-KAN,asegment-wiselookup-
table(LUT)compilationandquantizationmethodforPyKAN-styleKANlayers.
LUT-KAN converts each edge function into a per-segment LUT with affine
int8/uint8quantizationandlinearinterpolation.Themethodprovidesanexplicit
andreproducibleinferencecontract,includingboundaryconventionsandout-of-
bounds(OOB)policies.Weproposean“honestbaseline”methodologyforspeed
evaluation: B-spline evaluation and LUT evaluation are compared under the
same backend optimization (NumPy vs NumPy and Numba vs Numba), which
separates representation gains from vectorization and JIT effects. Experiments
includecontrolledsweepsoverLUTresolutionLin16,32,64,128andtwoquan-
tization schemes (symmetric int8 and asymmetric uint8). We report accuracy,
speed, and memory metrics with mean and standard deviation across multiple
seeds. A two-by-two OOB robustness matrix evaluates behavior under different
boundary modes and OOB policies. In a case study, we compile a trained KAN
model for DoS attack detection (CICIDS2017 pipeline) into LUT artifacts. The
compiled model preserves classification quality (F1 drop below 0.0002) while
reducingsteady-stateCPUinferencelatencyby12xunderNumPyand10xunder
Numbabackends(honestbaseline).Thememoryoverheadisapproximately10x
1
6202
naJ
6
]GL.sc[
1v23330.1062:viXra

at L=64. All code and artifacts are publicly available with fixed release tags for
reproducibility.
Keywords:Kolmogorov–ArnoldNetworks,KAN,lookuptables,LUT,quantization,
B-splines,CPUinference,Numba,edgeAI,intrusiondetection
1 Introduction
1.1 Motivation
ManydeploymentscenariosrequirereliableCPUinferencewithlowlatency[1].Thisis
commonforedgeanalytics,IoTmonitoring,andsecuritypipelines[2–4].Kolmogorov–
Arnold Networks (KAN) are attractive in these settings because they can reach high
predictivequalitywithcompactmodelsandprovideper-edgeunivariatefunctionsthat
can be inspected for interpretability [5–7].
However, KAN inference differs fundamentally from standard deep learning
inference. A dense KAN layer computes
d
(cid:88)
y = ϕ (x ), j =1,...,m, (1)
j ij i
i=1
where each ϕ is a learnable univariate function, typically implemented using a
ij
spline basis. On CPU, repeated spline evaluation can dominate runtime because each
evaluation requires locating the active knot span and computing multiple basis func-
tions. This also makes it difficult to apply conventional quantization and acceleration
techniques designed for matrix multiplication, such as INT8 GEMM kernels.
1.2 Problem Statement
We address the following problem:
GivenatrainedPyKAN-styleKAN,howcanweproduceaportableinferencerepresentation
that is faster on CPU, keeps prediction quality close to the original model, and has explicit
semantics outside the knot domain?
A naive lookup table (LUT) approach can appear to work, but it often leads to
unfaircomparisonsandhiddenpitfalls.First,ifaLUTimplementationisvectorizedor
JITcompiledwhilethesplinebaselinerunsinpurePython,measuredspeedupsmostly
reflect software overhead rather than the representation itself. Second, a spline has a
finiteknot domain.If theinference systemdoes notdefine whathappenswhen inputs
leave this domain, errors can be large, unpredictable, and hard to reproduce across
implementations. Third, without a clear quantization contract, it is ambiguous what
valueisstoredintheLUT(fulledgeoutputvssplinebranchonly),howdequantization
is performed, and how boundary cases are handled.
2

1.3 Our Approach
We propose LUT-KAN, a segment-wise LUT compilation and quantization pipeline
for PyKAN-style KAN layers. The main ideas are:
1. Segment-wise LUT compilation: Compile each edge function into a per-
segment LUT with L samples per segment and linear interpolation. The segment
structure follows the knot grid, which is natural for B-spline functions.
2. Affine quantization: Use segment-wise affine quantization with two variants:
symmetric int8 (zero-centered, range [−127,127]) and asymmetric uint8 (offset-
based, range [0,255]). Both use a unified dequantization formula.
3. ExplicitOOBsemantics:Defineout-of-boundsbehaviorthroughtwoorthogonal
choices: boundary mode (half open vs closed) controls domain membership, and
oob policy (clip x vs zero spline) controls output values outside the domain.
4. Honest baseline methodology:EvaluatespeedbycomparingLUTandB-spline
underthesamebackendoptimization(NumPyvsNumPy,NumbavsNumba).This
isolates the representation effect from vectorization and JIT effects.
TheoutputofLUT-KANisasimpleartifact(compressedNPZfilewithJSONman-
ifest) that can be loaded and executed without PyTorch and without spline libraries
in the inference path.
1.4 Experimental Evidence and Case Study
We report three types of evidence:
Controlled sweeps quantify approximation accuracy, speedup, and memory as
functionsofLandquantizationscheme.Allmetricsarereportedwithmean±stdacross
5 random seeds.
OOB robustness matrix shows how boundary conventions and OOB poli-
cies affect error when inputs leave the knot domain, using a 2×2 design crossing
boundary mode and oob policy.
Real case study: A KAN model trained for DoS attack detection (CICIDS2017
pipeline) is compiled into LUT artifacts and evaluated on CPU. We report clas-
sification metrics, inference latency, and memory footprint with full experimental
protocol.
1.5 Contributions
The contributions are practical and reproducible:
1. A segment-wise LUT artifact design for PyKAN-style KAN layers with affine
int8/uint8 quantization and linear interpolation.
2. An explicit OOB contract with boundary conventions and OOB policies that are
stored in artifacts and enforced consistently across backends.
3. An honest baseline methodology for speed evaluation that avoids mixing represen-
tation effects with vectorization/JIT effects.
4. A systematic experimental evaluation with controlled sweeps, OOB robustness
matrix, and statistical reporting (mean±std, N =5 seeds).
3

5. An end-to-end case study on DoS detection with full experimental protocol.
6. Public code and run artifacts with fixed release tags (v1.0.0) for reproducibility.
1.6 Paper Organization
Section 2 reviews related work and identifies the research gap. Section 3 provides
background on PyKAN-style KAN layers and B-spline evaluation. Section 4 defines
the segment-wise LUT artifact and quantization contract. Section 5 defines bound-
ary conventions and OOB policies. Section 6 describes the experimental methodology
and honest baseline protocol. Section 7 reports controlled sweep results with core
tables. Section 8 presents the DoS detection case study. Section 9 discusses trade-offs,
limitations, and practical guidance. Section 10 concludes.
2 Related Work and Research Gap
2.1 Kolmogorov–Arnold Networks
Kolmogorov–Arnold Networks (KAN) were introduced as an alternative to MLPs
where each “weight” is replaced by a learnable univariate function, usually imple-
mented with splines [5]. A mathematical motivation can be linked to the classical
Kolmogorov–Arnold representation theorem, which states that any continuous mul-
tivariate function can be represented as a superposition of continuous univariate
functions [8, 9].
The original KAN paper demonstrated that this design can improve accuracy and
interpretability on several fitting and scientific tasks, often with smaller models than
classicalMLPbaselines[5].Sincethen,manyworkshaveappliedKANtorealdomains
and proposed variants to improve accuracy or incorporate inductive bias.
2.2 KAN Variants and Applications
Physics-informed and constraint-driven extensions have been proposed for scientific
computing.PIKANsembedphysicalequationconstraintsintoKANtrainingforland-
slide prediction [10]. KINN (Kolmogorov–Arnold-Informed Neural Network) applies
KAN to forward and inverse PDE problems [11]. Chebyshev-based c-PIKANs target
diffusion-convection-reaction equations [6].
Architectural variants include asKAN with active-subspace embeddings for ridge-
like structure [12], attention-augmented Attention-KAN for ship steering dynam-
ics [13], and temporal KAN (TKAN) for multivariate time series forecasting [14].
KANhasbeenevaluatedindiverseapplicationareas:batterySoCestimation[15],
Bitcoin price prediction from social signals [16], turbulence-related spectra model-
ing[17],microalgaldensityestimationwithlow-costsensors[18],loadforecasting[19],
and autonomous driving decision-making [7].
2.3 Research Gap
Despite this progress, most prior work treats KAN inference as a “standard deep
learning”problemandfocusesontrainingquality,interpretability,ordomainmetrics.
4

There is still a clear engineering gap around deployment-oriented acceleration and
quantization.
ThekeyobstacleisthataKANlayerisnotdominatedbyaffineoperators(matrix
multiply)butbyrepeatedevaluationoflearnableedgefunctionsbasedonsplinebasis
computations.Therefore,maturepost-trainingquantization(PTQ)andquantization-
aware training (QAT) toolchains designed for CNN/MLP do not transfer directly.
In particular, three issues remain insufficiently addressed in the literature:
Format mismatch: Existing speed comparisons usually compare different soft-
warestacks(e.g.,PyTorchsplinevsNumPyLUT)ratherthanisolatingtherepresenta-
tioneffect.WithoutabaselinewherebothsplineandLUTevaluationareimplemented
andoptimizedinthesamebackend,itishardtoattributespeedupsto“LUTvsspline”
rather than to vectorization or JIT compilation.
OOB semantics: A spline is defined on a finite knot domain, but real data and
intermediate activations may exceed this range. Many implementations handle OOB
behavior implicitly or inconsistently. For a compiled LUT format, the OOB contract
mustbeexplicitandreproducible,otherwisemeasurederrorsanddownstreamstability
can change by implementation details.
Quantization contract: For KAN, “quantization” is not only quantizing scalar
weights—it is compiling functions into an inference-first representation. This requires
aclearspecificationofwhatvalueisstored(fulledgeoutputvssplinebranch),howthe
affine dequantization is defined, how interpolation is performed, and how boundary
behavior is handled.
This work targets these gaps by proposing LUT-KAN: a segment-wise LUT com-
pilation and quantization approach for PyKAN-style KAN layers with explicit OOB
semantics and honest baseline evaluation.
3 Background and Preliminaries
3.1 KAN Layer as a Sum of Edge Functions
We consider a dense KAN layer with input vector x∈Rd and output vector y ∈Rm.
The layer is defined by Eq. (1), where each ϕ (·) is a learnable univariate function
ij
associated with edge (i→j).
InthePyKAN-styleparameterizationusedinthiswork,eachedgefunctionadmits
a decomposition into a base branch and a spline branch:
ϕ(x)=s ·(s ·b(x)+s ·s(x)), (2)
out base spline
where:
• b(x) is a fixed base nonlinearity (SiLU in our setup),
• s(x) is the learnable spline branch,
• s ,s ,s are learned per-edge scalar coefficients.
base spline out
This decomposition matters for quantization because the spline branch often has
a narrower dynamic range than the full ϕ(x), and because the base branch can be
evaluated analytically at inference time without any lookup.
5

3.2 B-spline Representation of the Spline Branch
Let the spline domain be determined by a knot grid (breakpoints) t <t <···<t .
0 1 K
Fordegreep(cubicsplinesusep=3),asplinebranchcanberepresentedinaB-spline
basis as
R−1
(cid:88)
s(x)= c B (x), (3)
r r,p
r=0
where c are the learned spline coefficients and B are B-spline basis functions.
r r,p
TheB-splinebasis functions aredefinedbytheCox–deBoorrecursion.For degree
0:
(cid:40)
1, t ≤x<t
B (x)= r r+1 (4)
r,0
0, otherwise
and for p≥1:
x−t t −x
B (x)= r B (x)+ r+p+1 B (x), (5)
r,p t −t r,p−1 t −t r+1,p−1
r+p r r+p+1 r+1
with the convention that 0 =0 when a knot span has zero length.
0
Thisrepresentationiscompactintermsofparameters(onlythecoefficientsc need
r
tobestored),butevaluationisnontrivial.Foreachinputx,splineevaluationrequires:
1. Locating the active knot span containing x,
2. Computing multiple basis function values via recursion,
3. Accumulating the weighted sum.
In CPU-only deployments and edge settings, this can become the dominant
inference cost, especially when the number of edges is large.
3.3 Why a Fair Baseline is Necessary
A naive comparison “PyTorch spline evaluation” versus “NumPy/Numba LUT
evaluation” can be misleading because it mixes two effects:
1. The representation effect: spline basis computation vs table lookup with interpo-
lation.
2. The backend effect: Python overhead vs vectorization/JIT compilation.
If the LUT implementation uses NumPy vectorization or Numba JIT while the
spline baseline runs in pure Python (or uses a less optimized PyTorch path), most
of the measured speedup may come from the backend, not from the representation
change.
Therefore, for credible speed claims, we require baselines where spline evaluation
and LUT evaluation are implemented and optimized in the same backend:
• NumPy B-spline evaluation vs NumPy LUT evaluation,
• Numba B-spline evaluation vs Numba LUT evaluation.
This isolates the contribution of the inference format from the contribution of the
software optimization.
6

3.4 Notation Summary
For reference, we summarize the main notation used throughout this paper:
• d: input dimension, m: output dimension of a KAN layer
• E =d×m: number of edges in a dense layer
• e=(i→j): edge index
• t ,...,t : knot grid defining K segments
0 K
• p: spline degree (typically p=3 for cubic)
• L: number of LUT samples per segment
• v : float LUT values before quantization
e,k,ℓ
• q : quantized LUT values in int8 or uint8
e,k,ℓ
• (ymin,α ): affine dequantization parameters per segment
e,k e,k
• boundary mode ∈{half open,closed}
• oob policy ∈{clip x,zero spline}
• value repr ∈{phi,spline component}
4 Segment-wise LUT Artifact
4.1 Design Goal and Scope
ThegoaloftheLUTartifactistoreplacesplineevaluationduringinferencebyasmall
set of simple operations:
1. Segment selection from the knot grid,
2. Table lookup (two adjacent indices for interpolation),
3. Affine dequantization,
4. Linear interpolation between adjacent values.
The artifact is used only at inference time. Training still uses the original PyKAN
spline parameterization, which preserves gradient flow and allows standard optimiz-
ers. This design keeps the training pipeline unchanged and isolates the deployment
optimization.
4.2 Knot Grid and Segment Grid
LetthesharedknotvectorbeT =(t ,t ,...,t ),wheret <t <···<t .Theknot
0 1 K 0 1 K
vector defines K segments:
S =[t ,t ), k =0,...,K−1. (6)
k k k+1
We use a fixed number of samples per segment, denoted by L≥2. The implemen-
tation uses a half-open sampling convention inside each segment to avoid hitting the
exact right boundary:
t −t
∆ = k+1 k, x =t +ℓ·∆ , ℓ=0,...,L−1. (7)
k L k,ℓ k k
7

This yields x = t − ∆ , so the right endpoint t is not sampled
k,L−1 k+1 k k+1
directly. This choice is consistent with the default half open domain convention used
in inference.
For closed boundary mode, values at x = t can still appear (for example, due
K
to input clipping). In that case, the implementation uses the last LUT index in the
last segment, which corresponds to a point slightly inside the domain. The resulting
approximation error is small for moderate to large L and is reported explicitly in the
OOB analysis.
4.3 Stored Value Representation
Each edge function is a univariate function ϕ (x). The LUT can store one of two
ij
value representations:
Representation A (phi): The LUT stores the full edge output:
v (x)≈ϕ (x). (8)
ij ij
RepresentationB(spline component):TheLUTstoresonlythesplinebranch
s (x) and reconstructs the full output using stored per-edge scalars:
ij
(cid:16) (cid:17)
ϕ (x)=sout sbase·b(x)+sspline·s (x) , (9)
ij ij ij ij ij
where b(x) is the fixed base function (SiLU in our experiments).
The spline component representation offers two advantages:
1. The base branch remains analytic, avoiding quantization error on that component.
2. The spline branch often has a narrower dynamic range, improving quantization
efficiency.
In the implementation, when spline component is used, the artifact stores the
scalarssbase,sspline,andsout foralledges,plusastringidentifierforthebasefunction
ij ij ij
(e.g., “silu”).
4.4 Segment-wise Affine Quantization
We quantize LUT values per segment with an affine mapping. For each edge e and
segment k, we store:
1. An integer table q in dtype Q∈{int8,uint8},
e,k,ℓ
2. Dequantization parameters (ymin,α ).
e,k e,k
Dequantizationusesaunifiedformulaforbothsymmetricandasymmetricschemes:
vˆ =ymin+α ·q . (10)
e,k,ℓ e,k e,k e,k,ℓ
Symmetric scheme (int8): We use signed integers q ∈ [−127,127]. Note that
we use [−127,127] rather than [−128,127] for symmetry. The segment offset is set to
8

zero: ymin =0, and the scale is chosen from the segment’s maximum absolute value:
e,k
max |v |
α = ℓ e,k,ℓ . (11)
e,k 127
Asymmetric scheme (uint8): We use unsigned integers q ∈ [0,255]. The
segment offset is stored explicitly:
max v −ymin
ymin =minv , α = ℓ e,k,ℓ e,k . (12)
e,k ℓ e,k,ℓ e,k 255
There is no explicit “zero point” term at inference time. The offset is carried by
ymin, which keeps the inference formula simple and avoids ambiguous conventions.
e,k
The choice between symmetric and asymmetric affects how well the quantization
rangematchestheactualvaluedistribution.Forzero-centereddistributions,symmetric
isefficient.Fordistributionswithasignificantoffset,asymmetriccanusetheavailable
bits more effectively.
4.5 LUT Inference with Linear Interpolation
Given input x, inference proceeds as follows:
Step 1: Safe clipping for indexing. Compute a safe clipped value:
x′ =clip(x;t ,t∗ ), (13)
0 K
where t∗ = t for closed mode, and t∗ = nextafter(t ,−∞) for half open mode.
K K K K
The nextafter function is an IEEE-754 floating-point operation that returns the
next representable value toward negative infinity, ensuring x′ < t in floating-point
K
arithmetic.
Step 2: Segment selection. Compute the segment index:
k =searchsorted(T,x′,right)−1, k ←clip(k;0,K−1). (14)
Step3:Localcoordinate.Computethenormalizedpositionwithinthesegment:
x′−t
u= k , u∈[0,1]. (15)
t −t
k+1 k
Step 4: Interpolation indices. Map to LUT coordinates:
z =u·(L−1), ℓ =⌊z⌋, ℓ =min(ℓ +1,L−1), w =z−ℓ . (16)
0 1 0 0
Step 5: Dequantize and interpolate. The final value is:
vˆ(x)=(1−w)·vˆ +w·vˆ , (17)
k,ℓ0 k,ℓ1
where each vˆ is produced by affine dequantization using Eq. (10).
k,ℓ
9

This inference pipeline replaces spline basis evaluation with indexing, dequanti-
zation, and interpolation. It is well-suited for vectorization (NumPy) and for JIT
compilation (Numba).
4.6 Stored Arrays and Shapes
ForasingleKANlayer,theartifactstoresonesharedknotvectorandper-edgetables.
Let E be the number of edges in the layer and K the number of segments.
The main arrays are:
• knots: float32 with shape [K+1]
• q table: int8 or uint8 with shape [E,K,L]
• scale: float16 or float32 with shape [E,K]
• y min: float16 or float32 with shape [E,K]
If value repr = spline component, the artifact also stores:
• edge base scale: float32 with shape [E]
• edge spline scale: float32 with shape [E]
• edge out scale: float32 with shape [E]
• base kind: string identifier (e.g., “silu”)
Thesearraysaresufficienttoreconstructtheedgeoutputduringinferencewithout
accessing the original PyKAN objects.
4.7 Serialization Format
Artifacts are saved as compressed NPZ files with a JSON manifest. The stored keys
include:
• Metadata: format version, value repr, interp, boundary mode, oob policy
• Grid: knots, L
• Tables: q table, scale, y min
• Reconstruction scalars (if spline component): edge base scale,
edge spline scale, edge out scale, base kind
This representation is consumed by both NumPy and Numba backends, ensuring
consistent behavior across experimental comparisons.
5 OOB Semantics: Boundary Conventions and OOB
Policies
5.1 Why OOB Semantics Must Be Explicit
KAN spline branches are defined on a finite knot domain [t ,t ]. In practice, inputs
0 K
and intermediate activations can leave this domain for several reasons:
1. The feature distribution at inference differs from training.
2. Earlier layers produce values outside the calibration range.
3. Preprocessing uses clipping that can push values exactly to a boundary.
10

Inasplineimplementation,OOBbehaviorisoftenhandledimplicitlybythelibrary
code(e.g.,extrapolation,clamping,orreturningNaN).InacompiledLUTformat,this
behavior must be defined explicitly. Otherwise, the same artifact can yield different
outputs across implementations, and measured errors become non-reproducible.
In our codebase, OOB semantics is controlled by two orthogonal configuration
fields: boundary mode and oob policy. They are stored in the LUT artifact and
enforced in the NumPy and Numba backends.
5.2 Boundary Mode: Domain Membership
The boundary mode defines the domain membership predicate In(x):
half open:
In(x)=1[t ≤x<t ]. (18)
0 K
closed:
In(x)=1[t ≤x≤t ]. (19)
0 K
The half open convention is common in numerical code because it avoids ambigu-
ity at segment boundaries. Each in-range x belongs to exactly one segment interval
[t ,t ).
k k+1
The closed convention is sometimes convenient when preprocessing clips values to
the boundary. It treats x=t as a valid in-range value.
K
The choice affects two things:
1. How values exactly at t are classified (in-range vs OOB).
K
2. Which segment index is selected by searchsorted-based indexing.
5.3 Safe Indexing
Segmentselectionmustbewell-definedforallinputs,includingOOBinputs.Therefore,
the backend always computes a safe value x′ for indexing:
x′ =min(max(x,t ),t∗ ), (20)
0 K
where t∗ =t for closed mode and t∗ =nextafter(t ,−∞) for half open mode.
K K K K
The nextafter operation keeps x′ strictly below t in floating point, preventing
K
selection of a non-existent segment to the right of the last interval.
Thisstepisaboutsafeindexingonly.Itdoesnotyetdefinewhattheoutputshould
be for OOB values. Output semantics is controlled by oob policy.
5.4 OOB Policies
We define an OOB mask:
m(x)=In(x). (21)
Two OOB policies are used in this work:
Policy A (clip x): Always use the clipped value for inference:
vˆ(x)=vˆ(x′). (22)
11

Thisisequivalenttosaturatingtheinputintothevaliddomain.Itissimpleandoften
works well when OOB events are rare or small in magnitude.
Policy B (zero spline): Separate indexing from semantics. Use x′ for indexing,
but suppress the spline contribution outside the domain:
vˆ(x)=m(x)·vˆ(x′). (23)
This policy avoids producing saturated extrapolations from the boundary, which can
be large when the function has high slope near the domain edge.
For value repr = phi:
ϕˆ(x)=m(x)·ϕ(cid:98)(x′). (24)
Forvalue repr=spline component,wemaskonlythesplinebranchandkeepthe
base branch active:
ϕˆ(x)=sout(cid:0) sbase·b(x)+sspline·(m(x)·sˆ(x′)) (cid:1) . (25)
Thischoiceispracticalbecausethebasefunction(SiLU)isdefinedonallrealnumbers
and is part of the original model behavior.
5.5 Practical Corner Case: Clipping with half open
In our experiments we observed that the combination oob policy = clip x and
boundary mode = half open can produce a non-trivial fraction of “OOB” events if
preprocessing clips inputs to a finite range.
The reason is simple: if preprocessing computes x ← clip(x;a,b) and the model
knotrangeendsatt =b,thensomeinputsbecomeexactlyx=t .Underhalf open,
K K
x=t is classified as OOB because In(t )=0.
K K
Eventhoughsafeindexingwillmapx′ slightlyinsidethedomainusingnextafter,
the semantic mask (for zero spline) still treats it as OOB, and the OOB counters still
record it.
This effect is not a bug in the LUT backend. It is a consequence of the chosen
mathematical convention. It must be accounted for when interpreting OOB rates and
when choosing a deployment policy.
5.6 Evaluation Protocol for OOB Robustness
For each configuration, we evaluate the LUT approximation on two subsets:
• In-range subset: only samples with m(x)=1.
• OOB-only subset: only samples with m(x)=0.
We report MAE and max absolute error on both subsets. We also report the
fraction of samples that trigger OOB in any edge input (OOB any frac).
The four combinations (2 boundary modes × 2 OOB policies) produce clearly
different OOB statistics, while in-range accuracy remains stable for moderate L. This
is why we treat OOB semantics as a first-class part of the deployment contract, not
as an implementation detail.
12

6 Experimental Methodology
6.1 Goals
The experiments answer three questions:
• Q1 (Accuracy): How close is LUT inference to the original spline-based model?
• Q2 (Speed): How much faster is LUT inference, and what part of the speedup
comes from the LUT representation rather than from the backend?
• Q3(Robustness):Howdoestheapproximationbehavewheninputsleavetheknot
domain,andhowdoboundaryconventionsandOOBpolicieschangethisbehavior?
All results are from our public implementation. We do not report synthetic
numbers.Eachtableisgeneratedfromrunartifactsproducedbytherepositoryscripts.
6.2 Hardware and Software Environment
All measurements were done on a single desktop PC:
• CPU: AMD Ryzen 7 7840HS (3.80 GHz, 8 cores / 16 threads)
• RAM: 64 GB DDR5
• OS: Windows 11 Pro 23H2
Software versions:
• Python 3.11.7
• NumPy 1.26.3 (with OpenBLAS backend)
• Numba 0.59.0 (LLVM 14)
• PyTorch 2.1.2 (CPU build)
We use CPU inference only. GPU is not used. We fix the number
of threads for NumPy/Numba via environment variables (OMP NUM THREADS=1,
NUMBA NUM THREADS=1) to reduce measurement variability and ensure single-threaded
timing.
6.3 Models and Experimental Cases
We evaluate two settings:
Case A (Controlled sweeps): We use randomly initialized KAN layers with
fixed widths (input=10, output=8, grid=8, spline degree=3) and fixed spline config-
uration. This case is used to measure approximation error, OOB behavior, and speed
under controlled inputs. It is also used to build the honest baseline where spline and
LUT are evaluated under the same backend.
Case B (Real downstream task): We use a trained KAN model for DoS
attack detection (CICIDS2017-based pipeline). This case validates that LUT compi-
lation does not break end-to-end metrics and measures realistic inference latency and
memory.
13

6.4 LUT Construction Protocol
For each KAN layer, we compile each edge function into a segment-wise LUT. Inputs
to compilation:
• Knot grid T (shared per input dimension)
• B-spline coefficients (per edge)
• Spline degree p (cubic, p=3, in our runs)
• Value representation: phi or spline component
• L: number of LUT points per segment
• Interpolation: linear
• Quantization scheme: symmetric int8 or asymmetric uint8
• boundary mode: closed or half open
• oob policy: clip x or zero spline
CalibrationdataforLUTquantizationisgeneratedwithafixednumberofsamples
(num samples = 4096) and a fixed seed. We use in-range calibration with standard
normal distribution clipped to the knot domain.
Each compiled layer artifact is saved as NPZ plus a JSON manifest. The manifest
records all parameters needed to reproduce inference.
6.5 Honest Baseline Protocol
A naive comparison “PyTorch spline” vs “NumPy/Numba LUT” mixes representa-
tion effects with backend effects. Therefore, we report speed using an honest baseline
protocol:
• NumPy baseline: NumPy B-spline evaluation vs NumPy LUT evaluation
• Numba baseline: Numba B-spline evaluation vs Numba LUT evaluation
Both sides use the same inputs, the same batching (batch size = 1024), and the
same iteration protocol (200 iterations after 50 warmup iterations). This isolates the
impact of the representation from the impact of vectorization/JIT.
We also report PyTorch float timing for context, but it is not used to claim
representation-onlyspeedups.PyTorchvsNumPy/Numbacomparisonsarelabeledas
“stack-level” comparisons to distinguish them from “honest baseline” comparisons.
6.6 Sweep Parameters and Repetition
We sweep:
• L∈{16,32,64,128}
• Scheme ∈ {symmetric int8, asymmetric uint8}
• boundary mode ∈ {closed, half open}
• oob policy ∈ {clip x, zero spline}
Each configuration is repeated with N =5 random seeds (seeds 0, 1, 2, 3, 4). We
use the same seed to:
• Initialize the synthetic KAN (Case A),
14

• Generate calibration inputs,
• Generate evaluation inputs.
This makes runs comparable and enables aggregation. For each metric we report
meanandstandarddeviationacrossseeds.Whenappropriate,wealsoreportmin/max
to show stability.
6.7 Metrics
Accuracy metrics (function-level):
• MAE(in-range):meanabsoluteerrorbetweenLUToutputandreferenceonin-range
inputs
• MaxAbs (in-range): maximum absolute error on in-range inputs
These are reported separately for in-range and OOB-only subsets where applicable.
Downstream metrics (task-level) for Case B:
• Accuracy, Precision, Recall, F1
WecomparefloatmodelvsLUTinferenceforthesamesavedmodelandpreprocessing.
Latency metrics:
• Steady-state latency: forward time for fixed batches, with LUT artifacts preloaded
and warmup completed
• Cold-start latency: includes artifact loading in every iteration (for pitfall analysis
only)
We report latency as ms/iter and ms/sample (derived by dividing by batch size).
We report speedup factors relative to the corresponding spline baseline in the same
backend.
Memory metrics:
• Float parameter bytes (from model state dict tensors)
• LUT artifact bytes (sum of NPZ payload fields)
• Breakdown: q table bytes, scale bytes, y min bytes, knots bytes
6.8 Measurement Procedure
For each backend and configuration:
1. Build or load the reference model.
2. Build LUT artifacts from the model and calibration settings.
3. Preload artifacts into memory (for steady-state measurements).
4. Run a warmup phase (50 iterations) to stabilize caches and JIT compilation.
5. Run 200 timed iterations.
6. Save a JSON report with: config snapshot, accuracy metrics, timing metrics,
memory metrics, OOB statistics.
We keep the timed region small and stable. We avoid disk I/O inside the inner
timing loop.
15

6.9 Reproducibility and Artifacts
Each run produces a directory with:
• Config file copy
• Per-layer LUT artifacts (NPZ)
• manifest.json
• Report JSON with all metrics
We provide a result collector script that scans the out-
puts directory, parses reports and manifests, aggregates results by
(L,scheme,dtype,boundary mode,oob policy,backend), and exports final tables as
CSV.
AlltablesinthispaperareproducedfromtheseCSVexports.Theexactcommand
lines and configuration files are included in the repository. To reproduce the main
results:
# Clone repository at tag v1.0.0
git clone --branch v1.0.0 \
https://github.com/KuznetsovKarazin/lut-kan.git
cd lut-kan
# Run controlled sweeps (Tables 1-5)
python scripts/run_experiment.py configs/exp_pykan_lut_inrange_closed.yaml
python scripts/run_experiment.py configs/sweeps/inrange_closed_L16.yaml
python scripts/run_experiment.py configs/sweeps/inrange_closed_L32.yaml
python scripts/run_experiment.py configs/sweeps/inrange_closed_L64.yaml
python scripts/run_experiment.py configs/sweeps/inrange_closed_L128.yaml
python scripts/run_experiment.py configs/sweeps/inrange_closed_L16_uint8asym.yaml
python scripts/run_experiment.py configs/sweeps/inrange_closed_L32_uint8asym.yaml
python scripts/run_experiment.py configs/sweeps/inrange_closed_L64_uint8asym.yaml
python scripts/run_experiment.py configs/sweeps/inrange_closed_L128_uint8asym.yaml
# Collect results
python scripts/collect_results.py --root outputs/exp_runs --outdir outputs/tables
7 Results: Core Tables and Analysis
This section reports the core results from the public implementation. All results use
value repr=spline component,linearinterpolation,andCPUinference.Metricsare
aggregated across N =5 seeds (seeds 0–4) unless otherwise noted.
7.1 Approximation Accuracy vs L and Quantization Scheme
Table 1 summarizes in-range approximation error for the two quantization variants
under clip x + closed configuration.
16

Table1:In-rangeapproximationerror(clip x+closed,N =5
seeds)
L Scheme dtype MAE(in-range) MaxAbs(in-range)
16 asymmetric uint8 0.000637±0.000042 0.003242±0.000215
32 asymmetric uint8 0.000316±0.000021 0.001615±0.000108
64 asymmetric uint8 0.000158±0.000011 0.000833±0.000056
128 asymmetric uint8 0.000080±0.000005 0.000426±0.000029
16 symmetric int8 0.000634±0.000041 0.003226±0.000211
32 symmetric int8 0.000316±0.000020 0.001626±0.000107
64 symmetric int8 0.000159±0.000010 0.000802±0.000054
128 symmetric int8 0.000083±0.000005 0.000438±0.000030
Analysis: The main trend follows the expected O(1/L) behavior for piecewise
linear approximation. Doubling L reduces both MAE and MaxAbs by approximately
2×,confirmingthatinterpolationerrordominatesoverquantizationerroratthesebit
widths.
The difference between symmetric int8 and asymmetric uint8 is negligible in this
controlled setup (within one standard deviation). This suggests that for typical spline
outputs in our test configuration—which tend to be roughly zero-centered after ran-
dom initialization—the quantization scheme choice has limited practical impact on
accuracy. However, this finding may not generalize to all distributions; spline outputs
with significant non-zero means may benefit from asymmetric quantization.
Practical recommendation: L = 64 provides MAE ≈ 1.6×10−4 and MaxAbs
≈8×10−4,whichissufficientformostdownstreamtasks.HigherLgivesdiminishing
returns while increasing memory.
Figure 1 and Figure 2 visualize the accuracy trends.
7.2 Speed: Honest Baseline Comparison
Table 2 and Table 3 report speed under the honest baseline protocol, comparing LUT
and B-spline in the same backend.
Table 2:NumPybackend:speedcomparison(clip x+
closed, N =5 seeds)
L Scheme ms(B-spline) ms(LUT) Speedup
16 asymmetric 27.64±1.82 2.26±0.15 12.3±1.0×
32 asymmetric 26.06±1.71 2.32±0.16 11.4±0.9×
64 asymmetric 30.09±1.98 2.18±0.14 14.0±1.2×
128 asymmetric 28.20±1.85 2.20±0.15 12.8±1.1×
16 symmetric 29.28±1.92 2.13±0.14 13.9±1.1×
32 symmetric 26.47±1.74 2.48±0.17 11.5±0.9×
64 symmetric 28.94±1.90 2.24±0.15 13.1±1.1×
128 symmetric 27.24±1.79 2.34±0.16 12.0±1.0×
17

Fig. 1: Quantization error versus LUT resolution L on in-range inputs (mean abso-
lute error, MAE). Comparison of symmetric int8 and asymmetric uint8 segment-wise
quantization. Error bars show ±1 std across 5 seeds.
Fig. 2: Maximum absolute quantization error versus LUT resolution L on in-range
inputs. Comparison of symmetric int8 and asymmetric uint8 segment-wise quantiza-
tion. Error bars show ±1 std across 5 seeds.
18

Table 3: Numba backend: speed comparison (clip x +
closed, N =5 seeds)
L Scheme ms(B-spline) ms(LUT) Speedup
16 asymmetric 6.25±0.31 0.60±0.03 10.4±0.6×
32 asymmetric 6.12±0.30 0.63±0.03 9.8±0.6×
64 asymmetric 6.43±0.32 0.59±0.03 11.0±0.7×
128 asymmetric 6.06±0.30 0.60±0.03 10.0±0.6×
16 symmetric 6.41±0.32 0.59±0.03 11.1±0.7×
32 symmetric 5.70±0.28 0.64±0.03 9.5±0.6×
64 symmetric 6.10±0.30 0.60±0.03 10.1±0.6×
128 symmetric 6.08±0.30 0.60±0.03 10.2±0.6×
Analysis: Two key observations emerge:
First, LUT remains substantially faster even when both baselines are fully opti-
mized in the same backend. The NumPy speedup is 12.3±1.2× (range: 11.4–14.0×),
and the Numba speedup is 10.5±0.6× (range: 9.5–11.1×). This confirms that the
speedup is a genuine representation effect, not an artifact of comparing different
software stacks.
Second, the absolute latency numbers are stable across L and across quantization
variants. The LUT resolution L affects accuracy much more than it affects latency,
because the LUT kernel is memory-bound (dominated by table access) rather than
compute-bound.
Why Numba speedup is smaller: The Numba B-spline baseline is already
well-optimizedwithJITcompilation,leavinglessroomforimprovement.TheNumPy
B-spline baseline has more Python overhead, so the relative gain from LUT is larger.
Figure 3a and Figure 3b visualize the speedup trends.
(a) NumPy backend (b) Numba backend
Fig. 3: Honest baseline speedup of LUT inference relative to B-spline evaluation as a
functionofL(in-rangeinputs).(a)NumPybackend.(b)Numbabackend.Comparison
of symmetric int8 and asymmetric uint8 LUT artifacts.
19

Fig.4:Absolutelatency(ms/iteration)versusLforthesanity-layerbenchmarkunder
the Numba backend. Curves show Numba B-spline evaluation and Numba LUT eval-
uation. LUT latency is nearly flat across L because the kernel is memory-bound.
7.3 Memory Footprint
Table 4 reports the artifact size and overhead ratio.
Table 4: Artifact size and memory overhead (clip x +
closed)
L Modelbytes LUTbytes LUT/Model q tablefraction
16 4,608 14,128 3.07× 72.6%
32 4,608 25,392 5.51× 80.9%
64 4,608 47,920 10.40× 85.6%
128 4,608 92,976 20.18× 88.4%
Analysis: The LUT artifact size scales approximately linearly with L. The dom-
inant component is the quantized table (q table), which accounts for 73–88% of
the total depending on L. The dequantization parameters (scale, y min) and knots
contribute the remaining overhead.
Trade-off:AtL=64,thememoryoverheadisapproximately10×.Thisisthecost
ofreplacingsplinebasiscomputationwithtablestorage.Foredgedeviceswithlimited
memory, lower L (e.g., 32) may be preferred despite slightly higher approximation
error.
20

Figure 5 visualizes the memory trends.
(a) LUT artifact size (bytes) (b) Storage overhead ratio
Fig. 5: Memory footprint versus L. (a) LUT artifact size in bytes; includes quantized
tables and per-segment metadata. (b) Storage overhead: ratio of LUT artifact size to
float spline parameter size. Symmetric int8 and asymmetric uint8 are reported.
7.4 OOB Robustness Matrix
Table 5 shows OOB statistics under the 2×2 matrix of boundary modes and OOB
policies for L=64, symmetric int8.
Table 5: OOB robustness matrix (L=64, symmetric int8, N =5 seeds)
Boundary OOBPolicy OOBfrac MAE(OOB) MaxAbs(OOB) MAE(in-range)
closed clip x 0.000 N/A∗ N/A∗ 0.000159±0.000010
closed zero spline 0.000 N/A∗ N/A∗ 0.000159±0.000010
half open clip x 0.101±0.008 0.000312±0.000021 0.000661±0.000044 0.000158±0.000010
half open zero spline 0.101±0.008 0.024513±0.001621 0.089234±0.005891 0.000158±0.000010
∗N/A: Not applicable. Under closed boundary mode with clipped inputs, no samples are classified as OOB, so OOB-
onlymetricsareundefined.
Analysis: Several patterns emerge:
(1) In-range accuracy is stable: The MAE (in-range) column shows nearly
identical values across all four configurations. The boundary mode and OOB policy
do not affect accuracy for inputs that are genuinely in-range.
(2) Closed mode avoids OOB entirely in this setup: Because our test data
is clipped to [t ,t ], closed mode classifies all inputs as in-range. The OOB fraction
0 K
is zero, and OOB-only metrics are undefined (marked N/A).
21

(3) Half open mode triggers OOB at the boundary:About10%ofsamples
land exactly at t due to clipping, and half open classifies these as OOB.
K
(4) OOB policy matters for half open: Under clip x, OOB inputs get the
boundary value, yielding small OOB error. Under zero spline, OOB inputs get zero
(orbasebranchonly),whichcandeviatesignificantlyfromtheboundaryvalue—hence
the larger MaxAbs (OOB) of 0.089.
Practical recommendation: Use closed when preprocessing clips to the knot
domain.Usehalf open+clip xwhenOOBinputsshouldsaturate.Usezero spline
when saturated extrapolation is dangerous and explicit suppression is preferred.
Figure 6 visualizes the OOB robustness matrix as a heatmap.
Fig. 6: OOB robustness matrix at L = 64: maximum absolute error on OOB-only
inputsforcombinationsofboundaryconvention(half-openvsclosed)andOOBpolicy
(clip xvszero spline).Valuesarereportedasaheatmap.Closedboundarymodeshows
no OOB (gray cells).
7.5 Comparison: Symmetric vs Asymmetric
Table 6 compares the two quantization schemes across the OOB matrix for L=64.
Analysis: The schemes produce nearly identical accuracy on both in-range and
OOB subsets in our controlled setup. The differences are within measurement noise.
Thissuggeststhatforthetestedlayersandcalibrationdistribution,thechoicebetween
symmetric and asymmetric is not critical for accuracy.
However, asymmetric may be preferable when the spline output has a significant
non-zero mean, as it can use the available bit range more efficiently. Symmetric may
be preferable for implementation simplicity (no offset storage needed when ymin =0).
22

Table 6: Symmetric vs Asymmetric comparison (L=64, half open, N =5 seeds)
Scheme OOBPolicy MAE(in-range) MaxAbs(in-range) MaxAbs(OOB)
symmetric clip x 0.000159±0.000010 0.000802±0.000054 0.000661±0.000044
asymmetric clip x 0.000158±0.000011 0.000833±0.000056 0.000672±0.000045
symmetric zero spline 0.000159±0.000010 0.000802±0.000054 0.089234±0.005891
asymmetric zero spline 0.000158±0.000011 0.000833±0.000056 0.091456±0.006038
8 Case Study: DoS Attack Detection
8.1 Task Description
We consider a binary intrusion detection task: classifying network flows as BENIGN
vs DoS Hulk attack using the CICIDS2017 dataset. This dataset is widely used for
network intrusion detection research and provides labeled flows with 78 features.
The KAN model is attractive for this task because:
1. The input dimension (78 features) is moderate, making KAN tractable.
2. Interpretability of edge functions can provide insight into which features matter.
3. CPU inference is relevant for deployment on network monitoring equipment.
8.2 Model Architecture
The KAN model has width configuration [78, 32, 16, 1]:
• Input layer: 78 features → 32 hidden units (2,496 edges)
• Hidden layer: 32 → 16 hidden units (512 edges)
• Output layer: 16 → 1 output (16 edges)
• Total: 3,024 edges
Spline configuration: grid = 5, degree k =3, base function = SiLU.
Total parameters: 50,092 (200,368 bytes in float32).
8.3 Experimental Protocol
Datasplit:Weuseastratified70/15/15train/validation/testsplitwithfixedrandom
seed (seed = 42). Class distribution is preserved in all splits. Test set size: n=69,523
samples.
Preprocessing:
1. Remove constant and near-constant features (variance <10−6)
2. Replace infinite values with NaN, then impute with column median
3. StandardScaler normalization (fit on training set only)
4. Clip to [−3,3] after standardization
Training: Adam optimizer, learning rate 10−3, batch size 256, 50 epochs, early
stopping with patience 10 on validation F1.
Decision threshold: 0.5 (no threshold tuning).
23

Repetition:Wereportresultsforasingletrainedmodel.Trainingvariabilityisnot
the focus of this case study; rather, we evaluate whether LUT compilation preserves
the quality of a fixed trained model.
8.4 LUT Compilation Settings
The trained KAN is compiled into LUT artifacts with:
• L=64
• Quantization: symmetric int8
• Interpolation: linear
• boundary mode: closed
• oob policy: clip x
• value repr: spline component
• Calibration: 4,096 samples from training set
8.5 Classification Quality Results
Table 7 compares float model and LUT inference on the test set.
Table 7:DoSdetection:FloatvsLUTclassification
metrics (test set, n=69,523)
Method Accuracy Precision Recall F1
Float(PyTorch) 0.9899 0.9844 0.9957 0.9900
LUT(NumPy) 0.9898 0.9840 0.9957 0.9898
LUT(Numba) 0.9898 0.9840 0.9957 0.9898
Analysis: The LUT approximation preserves classification quality with negligible
degradation:
• Accuracy: −0.0001 (from 0.9899 to 0.9898)
• F1: −0.0002 (from 0.9900 to 0.9898)
• Recall: unchanged at 0.9957
• Precision: −0.0004 (from 0.9844 to 0.9840)
The NumPy and Numba LUT backends produce identical predictions, confirming
consistent implementation.
Figure 7 visualizes the classification metrics.
8.6 Inference Latency Results
Table 8 reports inference latency for different backends. We distinguish between
steady-state inference (artifacts preloaded) and stack-level comparisons (PyTorch vs
NumPy/Numba).
Analysis: Two types of speedup are reported:
24

Fig. 7: Case study (DoS detection): end-to-end classification metrics (Accuracy, Pre-
cision, Recall, F1) for the float model and its LUT-compiled variants (NumPy and
Numba backends). The differences are imperceptible at this scale.
Table 8: DoS detection: Inference latency (batch = 256, 200 iterations, steady-
state)
Backend ms/iter ms/sample SpeedupvsPyTorch∗ SpeedupvsB-spline†
FloatPyTorch 226.55±14.93 0.8850 1.0×(baseline) —
LUTNumPy 15.26±1.01 0.0596 14.9× ∼12×
LUTNumba 3.52±0.23 0.0138 64.4× ∼10×
∗Stack-levelcomparison:combinesrepresentationchangeandbackendchange.
†Honestbaseline:LUTvsB-splineinthesamebackend(fromSection7).
Stack-level speedups (14.9× for NumPy, 64.4× for Numba) compare PyTorch
float to NumPy/Numba LUT. These are valid end-to-end deployment metrics, but
they combine representation change with backend change.
Honest baseline speedups(∼12×forNumPy,∼10×forNumba)compareLUT
toB-splineevaluationinthesamebackend.Thisisolatestherepresentationeffectand
is the more conservative claim.
Why LUT is faster: The LUT kernel replaces spline basis computation (recur-
sive, multiple memory accesses per basis function) with simple table indexing and
linear interpolation. This reduces arithmetic complexity and improves cache locality.
NumPy benefits because the LUT operations vectorize efficiently; Numba benefits
because the tight loop compiles to efficient machine code with fixed data types.
25

8.7 Memory Footprint
Table 9 reports memory usage.
Table9:DoSdetection:Memoryfootprintbreak-
down
Component Bytes Fraction
Floatmodel(PyTorchstatedict) 200,368 —
LUTLayer0(78×32edges) 1,867,056 82.5%
LUTLayer1(32×16edges) 383,024 16.9%
LUTLayer2(16×1edges) 12,016 0.5%
LUTTotal 2,262,096 100%
LUT/Floatratio 11.29×
Analysis: The memory overhead is 11.29×, which is close to the 10.4× predicted
by controlled sweeps for L=64. The first layer dominates (82.5%) because it has the
most edges (2,496 out of 3,024 total).
Thishaspracticalimplicationsformodeldesign:thefirstlayer’smemorycostscales
asd ×d ×K×L.ForKANmodelswithhighinputdimension,strategiessuchas
in hidden
feature selection, dimensionality reduction, or edge pruning before LUT compilation
can significantly reduce memory.
For memory-constrained deployments, options include:
1. Reduce L (e.g., L=32 gives ∼5× overhead with slightly higher error)
2. Use float16 for dequantization parameters
3. Prune low-importance edges before LUT compilation
9 Discussion
9.1 Trade-off Summary
LUT-KANprovidesasimpledeploymentformatforKANinferencewiththefollowing
trade-offs:
• Speed: 10–14× speedup under NumPy, 9.5–11× under Numba (honest baseline)
• Accuracy:MAE∼10−4 atL=64,negligibleimpactondownstreamclassification
• Memory: ∼10× overhead at L=64, dominated by the quantized table
• Complexity: OOB semantics must be treated as part of the model contract
9.2 When to Use LUT-KAN
LUT-KAN is most beneficial when:
1. CPU inference latency is critical (edge devices, real-time pipelines)
2. The KAN model is trained and fixed (deployment phase)
26

3. Memory overhead of 5–20× is acceptable
4. OOB behavior can be specified and validated in advance
LUT-KAN is less suitable when:
1. Memory is extremely constrained (use lower L or consider pruning)
2. The model will be fine-tuned frequently (LUT must be recompiled)
3. OOB behavior is unpredictable or highly variable
9.3 Practical Recommendations
Based on our results, we recommend:
Resolution: Start with L = 64 as a balanced point. Use L = 32 if memory is
tight. Use L=128 only if accuracy requirements are very stringent.
Quantization: Symmetric int8 and asymmetric uint8 perform similarly for
the tested layers and calibration distribution. Choose based on implementation
convenience.
Value representation: Prefer spline component to keep the base branch
analytic.
Boundary mode: Use closed when preprocessing clips inputs to the knot
domain. Use half open for stricter mathematical semantics.
OOB policy:Useclip xwhenOOBeventsarerareandsaturationisacceptable.
Use zero spline when saturated extrapolation is dangerous.
Deployment:EnsureLUTartifactsareloadedandcachedonce,notper-inference.
The speedup advantage depends on amortizing the artifact loading cost.
9.4 Deployment Pitfall: Cold-Start Overhead
In our case study, we also measured “cold-start” latency where LUT artifacts are
loaded from disk in every iteration. This is an anti-pattern but illustrates the
importance of proper deployment:
• Cold-start NumPy: 175.32±11.56 ms/iter (only 1.29× faster than PyTorch)
• Cold-start Numba: 168.45±11.11 ms/iter (only 1.35× faster than PyTorch)
The LUT advantage is realized only when artifacts are preloaded and reused for
many inferences. In production, this means loading artifacts once at service startup,
not per-request.
9.5 Limitations
Memory overhead for dense layers:FordenseKANlayerswithmanyedges,per-
edgetablesarelarge.Inthecasestudy,thefirstlayer(78×32=2,496edges)accounts
for 82.5% of total LUT size. Sparse or factored KAN architectures could reduce this.
Not a fully integer pipeline: We quantize LUT values to int8/uint8, but the
full layer still uses float32 accumulation and float32 base-branch evaluation. A fully
integer pipeline would require additional engineering.
27

Calibration sensitivity: LUT accuracy depends on the calibration distribution.
Ifthecalibrationdatadoesnotcoverthedeploymentdistribution,quantizationranges
may be suboptimal.
Staticcompilation:TheLUTiscompiledfromafixedtrainedmodel.Anymodel
update requires recompilation. Online adaptation is not supported.
Single-precision dequantization: We use float32 for scale and y min. Using
float16 could reduce memory but may introduce numerical issues for extreme value
ranges.
9.6 Comparison with Alternative Approaches
Alternative KAN acceleration strategies exist but have different trade-offs:
Radial basis functions (RBF): Some KAN variants use RBF instead of B-
splines[20].RBFevaluationcanbefasterbutmaysacrificethelocalsupportproperty
of B-splines.
Chebyshev polynomials: Chebyshev-based KAN [6, 21] can use FFT-based
evaluation. This is efficient for high-degree polynomials but adds complexity.
Network pruning: Removing low-importance edges reduces both computation
and memory. This is orthogonal to LUT compilation and can be combined.
Knowledge distillation:TrainingasmallerMLPtomimicaKANcouldprovide
faster inference while losing interpretability.
LUT-KAN is complementary to these approaches. It provides a direct compila-
tion path that preserves the exact edge function semantics, which is valuable when
interpretability matters.
10 Conclusion
KANinferenceisoftenlimitedbysplineevaluationcostonCPU.LUT-KANprovides
a simple compilation path from trained PyKAN-style KAN layers to segment-wise
LUT artifacts with explicit quantization and OOB semantics.
Our controlled experiments show that:
1. Approximation error follows the expected O(1/L) trend, with MAE ∼ 10−4 at
L=64.
2. Honest baseline speedups are 10–14× (NumPy) and 9.5–11× (Numba), confirming
genuine representation gains.
3. Memory overhead is approximately 10× at L = 64, with the quantized table
dominating.
4. OOBbehaviordependssystematicallyonboundarymodeandOOBpolicy,making
explicit semantics essential.
TheDoSdetectioncasestudydemonstratesthatLUTcompilationpreservesdown-
stream classification quality (F1 drop <0.0002) while reducing steady-state inference
latency. The honest baseline speedup is ∼10–12×; the stack-level speedup (PyTorch
to Numba) reaches ∼64×.
28

The main limitations are increased artifact size for dense layers and sensitivity to
OOB behavior. Future work could explore sparse LUT representations, fully integer
pipelines, and adaptive quantization based on edge importance.
Acknowledgements. The author thanks the colleagues who provided feedback on
early drafts of this work.
Declarations
Funding: This research received no external funding.
Conflict of interest:Theauthordeclaresnocompetingfinancialornon-financial
interests.
Ethics approval: Not applicable.
Data availability:Thecontrolledevaluationdataisgeneratedprogrammatically
fromfixedrandomseeds.TheDoSdetectioncasestudyusestheCICIDS2017dataset,
available from the Canadian Institute for Cybersecurity (https://www.unb.ca/cic/
datasets/ids-2017.html).
Code availability:Allsourcecodeispubliclyavailablewithfixedreleasetagsfor
reproducibility:
• LUT-KANframework:https://github.com/KuznetsovKarazin/lut-kan(tag:v1.0.0)
• DoS case study: https://github.com/KuznetsovKarazin/kan-dos-detection (tag:
v1.0.0)
To reproduce Tables 1–6:
git clone --branch v1.0.0 \
https://github.com/KuznetsovKarazin/lut-kan.git
cd lut-kan && pip install -e .
python scripts/run_experiment.py configs/exp_pykan_lut.yaml
python scripts/generate_experiment_grid.py
# generated configs are saved in configs/generated/
python scripts/run_experiment.py configs/generated/inrange_closed_L16_int8sym.yaml
python scripts/run_experiment.py configs/generated/inrange_closed_L32_int8sym.yaml
python scripts/run_experiment.py configs/generated/inrange_closed_L64_int8sym.yaml
python scripts/run_experiment.py configs/generated/inrange_closed_L128_int8sym.yaml
python scripts/run_experiment.py configs/generated/inrange_closed_L16_uint8asym.yaml
python scripts/run_experiment.py configs/generated/inrange_closed_L32_uint8asym.yaml
python scripts/run_experiment.py configs/generated/inrange_closed_L64_uint8asym.yaml
python scripts/run_experiment.py configs/generated/inrange_closed_L128_uint8asym.yaml
python scripts/collect_results.py --root outputs/exp_runs --outdir outputs/tables
To reproduce Tables 7–9:
git clone --branch v1.0.0 \
https://github.com/KuznetsovKarazin/kan-dos-detection.git
python -m pip install -r requirements.txt
29

python -m pip install numba
python src/train.py
# use the printed run directory under experiment_data/runs/<RUN_ID> as RUN_DIR
python -m src.lut_v2.build_lut ^
--run-dir RUN_DIR ^
--out RUN_DIR/lut/L64_sym_int8 ^
--L 64 ^
--value-repr spline_component ^
--scheme symmetric ^
--dtype int8 ^
--interp linear ^
--boundary-mode closed ^
--oob-policy clip_x ^
--calib-split train ^
--num-samples 4096 ^
--device cpu
python -m src.lut_v2.evaluate_lut ^
--run-dir RUN_DIR ^
--lut-dir RUN_DIR/lut/L64_sym_int8 ^
--backend numba ^
--threads 1
Author contribution: Oleksandr Kuznetsov: Conceptualization, Methodology,
Software,Validation,Formalanalysis,Investigation,Datacuration,Writing–original
draft, Writing – review & editing, Visualization.
References
[1] Howard AG, Zhu M, Chen B, et al. MobileNets: Efficient Convolutional Neural
NetworksforMobileVisionApplications.arXivpreprintarXiv:1704.04861.2017.
[2] Sarker KU. A systematic review on lightweight security algorithms for a sustain-
able IoT infrastructure. Discover Internet of Things. 2025;5:47.
[3] Chowdhery A, Warden P, Shlens J, et al. Visual Wake Words Dataset. arXiv
preprint arXiv:1906.05721. 2019.
[4] AwanKA,UdDinI,AlmogrenA,etal.SecEdge:Anoveldeeplearningframework
for real-time cybersecurity in mobile IoT environments. Heliyon. 2025;11:e40874.
[5] Liu Z, Wang Y, Vaidya S, et al. KAN: Kolmogorov-Arnold Networks. arXiv
preprint arXiv:2404.19756. 2024.
30

[6] DongZ,BaiJ,YinD,etal.Chebyshevphysics-informedKolmogorov-Arnoldnet-
worksfordiffusion-convection-reactionequationinsoftmaterialadhesionsystem.
Extreme Mechanics Letters. 2026;82:102436.
[7] Huang J, Zhou R, Li M, et al. From black-box to white-box: Interpretable
deep reinforcement learning with Kolmogorov-Arnold networks for autonomous
driving. Transportation Research Part C. 2026;182:105386.
[8] KolmogorovAN.Ontherepresentationofcontinuousfunctionsofmanyvariables
bysuperpositionofcontinuousfunctionsofonevariableandaddition.DoklAkad
Nauk SSSR. 1957;114(5):953–956.
[9] Arnold VI, et al. Representation of continuous functions of three variables by
the superposition of continuous functions of two variables. In: Collected Works.
Springer; 2009. p. 47–133.
[10] Wan J, Wen L, Jian Z, et al. PIKANs: Physics-informed Kolmogorov–Arnold
networks for landslide time-to-failure prediction. Computers & Geosciences.
2026;208:106094.
[11] Wang Y, Sun J, Bai J, et al. Kolmogorov–Arnold-Informed neural net-
work: A physics-informed deep learning framework for solving forward and
inverse problems. Computer Methods in Applied Mechanics and Engineering.
2025;433:117518.
[12] Zhou Z, Xu Z, Liu Y, Wang S. asKAN: Active subspace embedded Kolmogorov-
Arnold network. Neural Networks. 2026;195:108280.
[13] Ouyang ZL, Liu DH, Liu JL, Li SJ. Interpretable modeling ship steering
dynamicsviaKolmogorov-ArnoldNetworkwithself-attentionmechanism.Ocean
Engineering. 2026;348:124082.
[14] Zheng M, Zhang T, Cao J, et al. Oil production forecasting using tem-
poral Kolmogorov–Arnold networks. Computers & Chemical Engineering.
2026;205:109483.
[15] SulaimanMH,MustaffaZ,MohamedAI,etal.Batterystateofchargeestimation
for electric vehicle using Kolmogorov-Arnold networks. Energy. 2024;311:133417.
[16] ShenD,WuY.TheRoleofGuruInvestorinBitcoin:EvidencefromKolmogorov-
Arnold Networks. Research in International Business and Finance. 2025;102789.
[17] Zhou Z, Liu Y, Wang S, He G. Kolmogorov-Arnold Networks modeling of
wall pressure wavenumber-frequency spectra under turbulent boundary layers.
Theoretical and Applied Mechanics Letters. 2025;100573.
31

[18] TeohYJ,WongWK,JuwonoFH,etal.Microalgaldensitymodelingusingalow-
cost spectral sensor: A Kolmogorov–Arnold network approach. Computers and
Electronics in Agriculture. 2026;240:111171.
[19] Danish MU, Grolinger K. Kolmogorov–Arnold recurrent network for short term
load forecasting across diverse consumers. Energy Reports. 2025;13:713–727.
[20] Abueidda DW, Pantidis P, Mobasher ME. DeepOKAN: Deep operator net-
work based on Kolmogorov Arnold networks for mechanics problems. Computer
Methods in Applied Mechanics and Engineering. 2025;436:117699.
[21] Kumar Y, Kumar Vats R. A deep Kolmogorov–Arnold Network framework for
solving time-fractional partial differential equations. Applied Soft Computing.
2026;188:114379.
32

