# Kui_2025_TFKAN

## Page 1

arXiv:2506.12696v1  [cs.LG]  15 Jun 2025
1
TFKAN: Time-Frequency KAN for Long-Term Time Series
Forecasting
Xiaoyan Kui, Canwei Liu, Qinsong Li∗, Zhipeng Hu, Yangyang Shi, Weixin Si, and Beiji Zou
Abstract—Kolmogorov-Arnold Networks (KANs) are highly
effective in long-term time series forecasting due to their ability
to efficiently represent nonlinear relationships and exhibit local
plasticity. However, prior research on KANs has predominantly
focused on the time domain, neglecting the potential of the fre-
quency domain. The frequency domain of time series data reveals
recurring patterns and periodic behaviors, which complement the
temporal information captured in the time domain. To address
this gap, we explore the application of KANs in the frequency
domain for long-term time series forecasting. By leveraging
KANs’ adaptive activation functions and their comprehensive
representation of signals in the frequency domain, we can more
effectively learn global dependencies and periodic patterns. To
integrate information from both time and frequency domains, we
propose the Time-Frequency KAN (TFKAN). TFKAN employs
a dual-branch architecture that independently processes features
from each domain, ensuring that the distinct characteristics of
each domain are fully utilized without interference. Additionally,
to account for the heterogeneity between domains, we introduce
a dimension-adjustment strategy that selectively upscales only
in the frequency domain, enhancing efficiency while capturing
richer frequency information. Experimental results demonstrate
that TFKAN consistently outperforms state-of-the-art (SOTA)
methods across multiple datasets. The code is available at
https://github.com/LcWave/TFKAN.
Index Terms—Time series forecasting, long-term forecasting,
Kolmogorov-Arnold networks, frequency domain, Fourier trans-
form.
I. INTRODUCTION
T
IME series forecasting (TSF) is crucial in various do-
mains, such as financial modeling, healthcare diagnostics,
and weather forecasting [1]–[4]. Accurate long-term time
series forecasting (LTSF) provides greater convenience, en-
abling more informed planning and decision-making [5], [6].
Unlike short-term forecasting, long-term forecasting cannot
rely solely on recent temporal information, such as trends,
in the time domain. In other words, stock prices do not follow
This work was supported in part by the National Natural Science Foundation
of China (Nos. U22A2034, 62177047, 62302530), High Caliber Foreign
Experts Introduction Plan funded by MOST, Key Research and Development
Programs of Department of Science and Technology of Hunan Province (No.
2024JK2135), Major Program from Xiangjiang Laboratory (No. 23XJ02005),
the Scientific Research Fund of Hunan Provincial Education Department (No.
24A0018), Hunan Provincial Natural Science Foundation (No. 2023JJ40769)
and Central South University Research Programme of Advanced Interdisci-
plinary Studies (No. 2023QYJC020). (Corresponding author: Qinsong Li)
Xiaoyan Kui, Canwei Liu, Zhipeng Hu, Yangyang Shi, and Beiji
Zou are with the School of Computer Science and Engineering, Cen-
tral South University, Changsha, 410083, China (e-mail: xykui@csu.edu.cn,
canwei liu@163.com,
244701046@csu.edu.cn,
yyshi806@csu.edu.cn,
bj-
zou@csu.edu.cn).
Qinsong Li is with the Big Data Institute, Central South University,
Changsha, 410083, China (e-mail: qinsli.cg@csu.edu.cn).
Weixin Si is with the Shenzhen Institute of Advanced Technology, Chinese
Academy of Sciences, Shenzhen, 518055, China (e-mail: wx.si@siat.ac.cn).
patterns from just the last few days, they must capture stable
periodicity within the time series. Therefore, most models
leverage the Transformer’s ability [7]–[10] to model long-term
dependencies for LTSF tasks.
Kolmogorov-Arnold Networks (KANs) [11] have recently
emerged as a promising approach for LTSF due to their effi-
cient nonlinear representation capabilities and local plasticity
[12], [13]. The local plasticity of B-Spline enables KAN to
model complex patterns while preserving previously learned
knowledge, making them particularly suitable for the LTSF.
Unlike traditional neural network models, such as Multilayer
Perceptrons (MLPs) [14] and Transformer [9], KAN miti-
gates the problem of catastrophic forgetting by leveraging
local spline-based parametrizations. This unique feature allows
KAN to adapt to new information without disrupting existing
representations, enhancing its robustness for long-term sequen-
tial learning scenarios.
The frequency domain complements the time domain by
providing insights into recurring cycles, periodicities, and
spectral distributions that are critical for understanding long-
term patterns [15]. Recent studies have shown that periodic
patterns are often more salient and interpretable in the fre-
quency domain [14], [16]. Despite these advantages, most
existing works on KAN have been restricted to time-domain
modeling [17]–[21]. Although the recent TimeKAN [22] em-
ploys FFT/IFFT to extract frequency components, the KAN
modules themselves are applied only in the time domain. This
limits their capacity to directly capture frequency-localized
patterns. To the best of our knowledge, no prior work has
explicitly applied KAN in the frequency domain. This leaves
an open gap in leveraging KAN’s potential to jointly capture
temporal dependencies and frequency-specific patterns, espe-
cially for LTSF tasks.
TABLE I
SYNTHETIC FUNCTIONS USED IN TOY EXPERIMENTS. EACH FUNCTION
CONSISTS OF A DIFFERENT COMBINATION OF SINE AND COSINE TERMS,
REPRESENTING VARYING FREQUENCY PATTERNS.
ID
Target Function
F1
sin(2πx) + 0.5 cos(4πx)
F2
sin(4πx) + 0.3 cos(8πx)
F3
sin(2πx) + cos(6πx) + 0.3 cos(10πx)
F4
sin(2πx) + sin(4πx + π
3 ) + cos(6πx)
To gauge whether the spline-based activations of KANs
are advantageous for modelling periodic structure, we first
perform a controlled function approximation study in the
time domain. In detail, we synthesise four target functions
(Table I) by summing sinusoids of different frequencies and
phases. These signals contain multiple harmonic components
and therefore mimic the mixed periodicities often encountered


---

## Page 2

2
in real LTSF tasks. Then, we compare a two-layer ReLU MLP
against a KAN with grid size s = 2 and spline order k = 1,
training both to regress each fi(x) on x ∈[0, 1]. Results in
Fig. 1 show that KAN consistently yields smoother and more
accurate reconstructions. Because a Fourier transform maps
multi-harmonic signals to sparse, localised spectral peaks,
the observed advantage suggests that KAN’s B-spline bases
naturally adapt around those peaks. This motivates us to
place KAN modules directly in the frequency domain, where
periodic information is explicit and global dependencies can
be captured with greater interpretability.
MLP
KAN
Ground Truth
0.5
0.0
-0.5
-1.0
-1.5
f(x)
0.0
0.2
0.4
0.6
0.8
1.0
(a) F1
0.0
0.2
0.4
0.6
0.8
1.0
(b) F2
0.75
0.50
0.00
0.25
-0.25
-0.50
-0.75
-1.00
-1.25
f(x)
0.0
0.2
0.4
0.6
0.8
1.0
(d) F4
2
1
0
-1
-2
-3
f(x)
0.0
0.2
0.4
0.6
0.8
1.0
(c) F3
f(x)
1.5
1.0
0.5
0.0
-0.5
-1.0
-1.5
Fig. 1. Comparison of MLP and KAN in approximating periodic functions
(F1–F4). KAN consistently achieves smoother and more accurate reconstruc-
tions, especially under high-frequency and phase-shifted conditions.
Based on these, we propose the frequency-domain KAN.
To the best of our knowledge, this is the first attempt to
directly apply KAN in the frequency domain for time series
forecasting. By leveraging KANs’ adaptive activation func-
tions and their comprehensive representation of signals in
the frequency domain, we can more effectively learn global
dependencies and periodic patterns. Furthermore, to integrate
information from both time and frequency domains, we in-
troduce the Time-Frequency Kolmogorov-Arnold Networks,
named TFKAN. This architecture features a dual-branch struc-
ture that independently processes features from each domain,
ensuring that the distinct characteristics of each domain are
fully utilized without interference. By designing specialized
KANs in each branch, TFKAN optimizes feature extraction for
both domains, enabling effective capture of domain-specific
features. Additionally, a dimension-adjustment strategy is im-
plemented to address the heterogeneity between the time
and frequency domains. Specifically, downscaling in the time
domain adapts temporal features for efficient processing, while
upscaling in the frequency domain highlights periodic patterns
for better representation, which ensures efficient utilization of
information from both domains.
The contributions of this paper are summarized as follows:
• We propose the frequency-domain KAN, a novel ap-
proach that enables the model to capture prominent
periodic patterns in the frequency domain. To the best
of our knowledge, this is the first work to directly apply
KAN in the frequency domain for time series forecasting.
• We introduce a dual-branch architecture TFKAN that
independently processes features from the time and fre-
quency domains. This design ensures the full utilization
of the unique characteristics of each domain while pre-
venting interference between them.
• We propose a dimension-adjustment strategy to address
the heterogeneity between the time and frequency do-
mains. This strategy selectively upscales only in the
frequency domain, enhancing computational efficiency
while capturing richer frequency information.
• Through extensive experiments on seven time-series
datasets, we demonstrate that TFKAN outperforms eight
SOTA methods, underscoring its superior forecasting
capabilities.
II. RELATED WORK
Recent advancements in long-term time series forecast-
ing (LTSF) can be broadly categorized into three modeling
paradigms based on their primary representation domain:
time-based, frequency-based, and hybrid approaches. This
section briefly reviews each category.
Time-Based Models. Time-domain models directly model
temporal dynamics using linear projections, MLPs, or atten-
tion mechanisms. Transformer-based methods such as Log-
Trans [23], TFT [24], and Informer [8] adapt attention-
based architectures to model long-range dependencies. More
recent developments, like PatchTST [10], PETformer [25],
and Crossformer [26], improve performance and efficiency
by partitioning inputs into patches. Meanwhile, lightweight
linear and MLP-based models offer faster inference with
fewer parameters. LTSF-Linear [16] demonstrates the sur-
prising effectiveness of a single-layer linear model, inspiring
subsequent works like LightTS [27], TiDE [28], MTS-Mixers
[29], TimeMixer [30], and HDMixer [31]. WormKAN [32]
and RMoK [17] are KAN-based methods designed for concept
drift and variable-specific modeling, respectively. TKAN [18]
as a recurrent KAN architecture marrying KAN with LSTM-
like memory. And TKAT [19] is an encoder–decoder architec-
ture that injects TKAN layers into a Transformer framework.
C-KAN [33] employs convolutional layers to extract local
temporal patterns before feeding them into a KAN layer.
However, neither leverages frequency features.
Frequency-Based Models. Frequency-domain models ex-
ploit frequency information to capture periodic patterns and
global trends. FreTS [14] enhances MLPs by applying fre-
quency decomposition with energy compaction. FEDformer
[34] integrates Fourier-based convolution with decomposition
mechanisms for better trend-seasonal modeling. FITS [35]
operates entirely in the complex frequency domain, lever-
aging interpolation over complex value’s components rather
than processing raw time-domain sequences. Although these
models benefit from frequency-domain representations, none
of them perform function learning directly on the complex
value’s components using KAN.
Hybrid Time-Frequency Models. Hybrid approaches aim
to combine the strengths of both domains. Autoformer [9]
integrates auto-correlation and progressive decomposition for
temporal and periodic pattern extraction. TimeKAN [22] incor-
porates KANs alongside FFT/IFFT operations but still applies
KANs only in the time domain. ATFNet [36] uses a dual-
branch architecture to process both domains simultaneously,


---

## Page 3

3
(a) Dimension Ajustement 
Strategy
×
N × L
N × L× d

1 × d
(b) Frequency Branch
(c) Time Branch
KAN-based
Predictor
Frequency-domain
KAN
t

t

t

BIAS
t

t

Input
t
L
N
τ 
…
…
time dimensions
L
channel dimensions
N
N
N
Fnt
real part
complex number
imaginary part
concat
concat
Znt
1
2
t

t
t
Output
ˆt
N
τ 
…
MSE

τ 
…
t
flatten
t

…
Amplitude
Frequency (Hz)
1
2
L 
FFT
iFFT
L
Time-domain KAN
Domain
Transform
Domain
Detransform
L
L
g-k
gs+k
gs
…
…
g0
g1
…
+
time
base

time
spline

+
SiLU
nt

Fig. 2. The overall architecture of TFKAN: (a) Dimension Adjustment Strategy is used to prepare the data Ft and Tt for the Frequency and Time Branches,
separately. (b) The Frequency Branch extracts periodic patterns from the frequency domain using the Frequency-domain KAN. (c) The Time Branch captures
temporal dependencies from the time domain with the Time-Domain KAN.
featuring an extended DFT and complex-valued attention.
JTFT [37], T-FIA [38], and TFMRN [39] further demon-
strate the effectiveness of concurrent time-frequency modeling.
These methods, however, rely on predefined transformations
(e.g., DFT) or attention mechanisms, and do not incorporate
learnable function approximation in the frequency domain.
III. METHODS
In this section, the details of the proposed TFKAN frame-
work are presented. Firstly, the LTSF problem is formally
defined in Section III-A. Secondly, the prerequisites of
Kolmogorov-Arnold Networks (KAN) are provided in Sec-
tion III-B. Finally, Section III-C introduces the dual-branch
architecture of TFKAN, integrating Frequency-Domain KAN
(FreqKAN), Time-Domain KAN (TimeKAN), and a KAN-
based Predictor.
A. Problem Definition
For LTSF, the historical data is represented as X
=
[X1, . . . , XT ] ∈RN×T , where N denotes the number of vari-
ables (or features) and T represents the number of time steps.
Each Xt ∈RN contains the multivariate values of N variables
at time step t. A segment of the time series with a lookback
window of length L at timestamp t is used as the model input
denoted as Xt = [Xt−L+1, Xt−L+2, . . . , Xt] ∈RN×L. The
objective is to predict future values Yt = [Xt+1, . . . , Xt+τ] ∈
RN×τ over the next τ time steps, where τ represents the long-
term forecast horizon. This is done using a forecasting model
fθ, such that ˆYt = fθ(Xt).
B. Prerequisites
KAN [11] is grounded in the Kolmogorov-Arnold Represen-
tation Theorem, which states that any multivariate continuous
function can be represented as a finite combination of univari-
ate continuous functions. KAN builds on this foundation by
incorporating two key mechanisms: Base Transformation and
B-Spline Transformation. These mechanisms work synergisti-
cally to capture complex relationships while maintaining local
plasticity, enabling the model to adapt to new inputs without
overwriting previously learned information.
Base Transformation. The base transformation captures
primary patterns in the input data through a linear mapping
followed by a nonlinear activation. It employs a learned weight
matrix Wbase and the SiLU activation function [40]. This
transformation is defined as:
zbase = Wbase · SiLU(x),
(1)
where x represents the input data, and zbase denotes the
transformed output.
B-Spline Transformation. The B-spline transformation
performs smooth interpolation between data points, allowing
for flexible modeling of complex patterns. It leverages a
uniformly spaced grid G ∈Rs+2×k+1, where s is the grid
size, indicating the number of interpolation points, and k is
the spline order. This transformation is expressed as:
zspline =
X
i
ci · Bk
i (x),
(2)
where cis are learnable weights. In this paper, these are
denoted together with Wspline. The Bk
i represents the i-th B-
spline of degree k, and zspline is the interpolated output. The
grid G = [g−k, . . . , g0, g1 . . . , gs+k] is uniformly distributed
over [−1, 1], controlling the resolution of spline interpolation.
The B-spline bases Bk
i (x) are recursively computed as:
B0
i (x) =
(
1
if x ∈[gi, gi+1)
0
otherwise
Bk
i (x) =
x −gi
gi+k −gi
Bk−1
i
(x) +
gi+k+1 −x
gi+k+1 −gi+1
Bk−1
i+1 (x),
(3)
where B0
i (x) represents a 0-degree B-spline, and Bk
i (x)
represents a k-degree B-spline. The index i denotes the i-th
spline base.


---

## Page 4

4
Finally, the combined KAN output is defined as:
z = zbase + zspline.
(4)
C. TFKAN: Time-Frequency KAN
Building upon the strengths of KAN described above, the
dual-branch architecture of TFKAN is designed to handle the
heterogeneity of time and frequency domains. The architecture
leverages two distinct branches, a Frequency Branch and a
Time Branch, to process frequency-domain and time-domain
representations independently, ensuring optimized feature ex-
traction in each domain. The architecture, illustrated in Fig.
2, also incorporates a Dimension Adjustment Strategy and a
KAN-based Predictor.
Overview of Dual-Branch Workflow. At each time step t,
the historical input Xt is first preprocessed by the Dimension
Adjustment Strategy (Fig. 2 (a)) to prepare the data for the Fre-
quency and Time Branches (Fig. 2 (b) and (c)). The Frequency
Branch extracts spectral features using a DomainTransform
operation and processes them using the Frequency-Domain
KAN. After that, the output of the frequency-domain KAN is
processed by a DomainDetransform operation. Meanwhile, the
Time Branch directly captures temporal dependencies through
the Time-Domain KAN. Finally, the outputs of both branches
are integrated with a bias term and fed into the KAN-based
Predictor to generate the final forecast.
Dimension Adjustment Strategy. To optimize feature
extraction, the dimension adjustment strategy (Fig. 2 (a))
modifies the input data differently for the frequency and
time branches. For the frequency branch, the historical data
Xt ∈RN×L is multiplied by a learnable weight vector
W ∈R1×d, producing hidden representations Ft ∈RN×L×d,
which are enriched with frequency-specific information. In
this paper, the embedding size d is set as 128. For the time
branch, the original input remains unchanged as Tt ∈RN×L
to preserve the temporal structure and efficient processing. The
operations are formally defined as:
Ft = Xt × W
Tt = Xt.
(5)
DomainTransform/Detransform. The DomainTransform
operation converts data from the time domain to the frequency
domain using the Fast Fourier Transform (FFT). This operation
decomposes the time signal into its frequency components.
Conversely, the DomainDetransform operation employs the
Inverse Fast Fourier Transform (IFFT) to map frequency-
domain data back to the time domain. Specifically, the input of
the Frequency Branch Ft, which is treated as continuous data,
is transformed into the frequency domain, Ft ∈CN×( L
2 +1)×d,
by:
Ft(f) =
Z ∞
−∞
Ft(v)e−j2πfvdv
=
Z ∞
−∞
Ft(v) cos(2πfv)dv −j
Z ∞
−∞
Ft(v) sin(2πfv)dv,
(6)
where f denotes the frequency variable, v denotes the in-
tegral variable, and j = √−1 is the imaginary unit. Addi-
tionally, the integral
R ∞
−∞Ft(v) cos(2πfv)dv represents the
real part of Ft, denoted as Re(Ft). Similarly, the integral
R ∞
−∞Ft(v) sin(2πfv)dv represents the imaginary part of Ft,
denoted as Im(Ft). In other words, the frequency-domain
data consists of cos and sin waves with varying frequencies
and phases, and their magnitudes represent the corresponding
amplitudes.
After completing all operations in the frequency domain, the
frequency data Ft is transformed back into the time domain
as follows:
Rt(v) =
Z ∞
−∞
Ft(f)ej2πfvdf
=
Z ∞
−∞
[Re(Ft(f)) + jIm(Ft(f))] ej2πfvdf,
(7)
where f denotes the integral variable. Notably, the Domain-
Transform and DomainDetransform operations are applied
only to the frequency branch.
Frequency Branch. The Frequency Branch (Fig. 2 (b)) is
designed to learn frequency features and periodic patterns in
the frequency domain. It operates channel-wise, with each in-
put channel processed independently. Taking the n-th channel
of Ft, denoted as Fn
t ∈RL×d, as an example. The processing
steps of the Frequency Branch are as follows:
Fn
t = DomainTransform(temp)(Fn
t )
Zn
t = FreqKAN(Fn
t , Wfreq
base , Wfreq
spline)
Rn
t = DomainDetransform(temp)(Zn
t ),
(8)
where
Fn
t
∈
C1×( L
2 +1)×d
represents
the
frequency-
domain data obtained through the DomainTransform. Zn
t ∈
C1×( L
2 +1)×d refers to the processed data from the Frequency-
Domain KAN. Additionally, the matrices Wfreq
base
∈Rd×d
and Wfreq
spline
∈
Rd×d×(s+k) represent the weight matri-
ces for the base function SiLU and the B-spline func-
tion, respectively, where the s denotes grid size and the
k denotes the spline order. Finally, Rn
t
is the recon-
structed time-domain data obtained after applying the Domain-
Detransform. The operations DomainTransform(temp) and
DomainDetransform(temp) are performed along the temporal
dimension, i.e., the L-dimension.
The Frequency-Domain KAN (FreqKAN(·)) is a two-layer
KAN, the network processes the real and imaginary compo-
nents of Fn
t ∈C1×( L
2 +1)×d separately. More specifically, the
real part Re(Fn
t ) ∈R1×( L
2 +1)×d is firstly input into the two-
layer KAN to get the real output Re(Zn
t ). Then, the imaginary
part Im(Fn
t ) ∈C1×( L
2 +1)×d is input into the network to get
the imaginary output Im(Zn
t ). Due to the local plasticity of
KAN, the features captured from the real and imaginary parts
are effectively integrated. Using the same KAN network for
both the real and imaginary parts ensures consistent feature
learning and parameter sharing for meaningful signal recon-
struction. Finally, the real and imaginary outputs are combined
to form the final complex-valued representation:
Zn
t = Re(Zn
t ) + jIm(Zn
t ),
(9)
where Zn
t ∈C1×( L
2 +1)×d.


---

## Page 5

5
Time Branch. The Time Branch (Fig. 2 (c)) is designed to
capture temporal dependencies and trends directly from the
time-domain data. Unlike the Frequency Branch, no trans-
formation is applied to the input data before it is processed
by the Time-Domain KAN, ensuring efficiency. The input
data Tt ∈RN×L is passed directly to the Time-Domain
KAN, which produces temporal representations St ∈RN×L.
The operations within the Time Branch also operate on the
channel dimension. Taking the n-th channel of Tt, denoted
as T n
t
∈R1×L, as an example, the process can be formally
defined as:
Sn
t = TimeKAN(T n
t , Wtime
base , Wtime
spline),
(10)
where Sn
t
∈R1×L refers to the processed data from the
Time-Domain KAN. The weight matrices Wtime
base
∈RL×L
and Wtime
spline ∈RL×L×(s+k) are the learnable parameters in
the Time-Domain KAN, respectively.
The Time-Domain KAN (TimeKAN(·)) processes inputs to
capture temporal features and dependencies inherent in time
series data. Its structure is similar to that of the Frequency-
Domain KAN but processes inputs at one time.
Long-term Time Series Forecasting. To combine the
information from both the Frequency and Time branches, the
outputs of these branches are integrated with a bias term. The
process is mathematically formulated as follows:
BIAS = Fn
t + T n
t
Hn
t = Rn
t + Sn
t + BIAS,
(11)
where Hn
t
∈R1×L×d denotes the final integrated hidden
representation used for forecasting. Additionally, a broadcast
mechanism is employed to compute BIAS ∈R1×L×d. Sub-
sequently, Hn
t is fed into a KAN-based Predictor, to generate
the prediction ˆYn
t ∈R1×τ.
The structure of the KAN-based Predictor is also similar
to the Frequency-Domain KAN. Firstly, the input hidden
representation Hn
t
∈R1×L×d is reshaped into a flattened
vector Vn
t
∈R1×(L·d). Subsequently, the reshaped input is
fed into a KAN with an input size of L · d and an output size
of τ. These operations are formulated as:
ˆYn
t = KAN(Vn
t , Wpre
base, Wpre
spline).
(12)
Finally, the prediction
ˆYn
t
is reconstructed against the
ground truth Yn
t ∈R1×τ using the Mean Squared Error (MSE)
loss, which is computed as follows:
LMSE = 1
τ
τ
X
i=1

ˆYn
t −Yn
t [i]
2
,
(13)
where i represents the i-th variable along the τ-dimension.
IV. EXPERIMENTS
In this section, extensive experiments are presented on seven
time series datasets to answer the following research questions
(RQ):
• RQ1 (Accuracy): Does the proposed TFKAN outper-
form SOTA methods across various scenarios?
• RQ2 (Ablation): Do key components of TFKAN con-
tribute to the overall performance?
• RQ3 (Sensitivity & Effciency): How does TFKAN
perform under different hyperparameter configurations?
How about its computational efficiency?
The RQ1, RQ2, and RQ3 will be answered in Sections IV-B
and IV-C, and IV-D-IV-E, respectively.
A. Experimental Settings
Datasets. Seven time-series datasets from diverse domains,
including electricity, medical, and meteorology, are selected
for evaluation. The datasets are as follows: 1) ETT1: The se-
lected ETT dataset from ETT consists of four subsets: ETTm1,
ETTm2, ETTh1, and ETTh2. It contains data from two station
electricity transformers, including load and oil temperature
measurements. Each transformer dataset is recorded at two
resolutions: 15 minutes (denoted as ’m’) and 1 hour (denoted
as ’h’). 2) Air2: This dataset records the hourly responses of a
gas multisensor device deployed in an Italian city, along with
gas concentration references measured by a certified analyzer.
3) Weather3: Collected in 2020 from the Weather Station of
the Max Planck Biogeochemistry Institute in Germany, this
dataset includes 21 meteorological indicators such as humidity
and air temperature. The data is sampled every 10 minutes. 4)
ILI4: This dataset contains weekly records of influenza-like
illness (ILI) patient data from the Centers for Disease Control
and Prevention in the United States, spanning 2002 to 2021.
It describes the ratio of patients with ILI to the total number
of patients. To ensure consistency, all datasets are normalized
to the range [0, 1] using min-max normalization. The datasets
are split into training, validation, and test sets with a ratio of
7:2:1, except for the ILI dataset, which is divided into a 6:2:2
ratio due to its shorter sequence lengths.
Baselines. We select eight SOTA models as baselines,
covering a diverse range of design paradigms for long-term
time series forecasting (LTSF). These include time-domain
models, frequency-domain models, and hybrid architectures.
The full names and official implementations of these baselines
are provided in Table II. We briefly categorize and describe
them as follows:
• Time-domain
methods.
LTSF-Linear
[16]
is
a
lightweight,
single-layer
linear
model
designed
to
capture local temporal dependencies. TSMixer [41]
employs a fully MLP-based architecture that stacks
multiple
perceptrons
to
model
complex
temporal
patterns. Informer [8] is a Transformer-based model that
utilizes ProbSparse attention and generative decoding to
facilitate long-sequence forecasting.
• Frequency-domain
methods.
FreTS
[14]
enhances
global signal modeling by applying MLPs to frequency-
domain representations. FEDformer [34] introduces a
frequency-enhanced, decomposition-based Transformer
architecture.
1https://github.com/zhouhaoyi/ETDataset
2https://archive.ics.uci.edu/dataset/360/air+quality
3https://www.bgc-jena.mpg.de/wetter/
4https://gis.cdc.gov/grasp/fluview/fluportaldashboard.html


---

## Page 6

6
TABLE II
SUMMARY OF BASELINE MODELS USED FOR COMPARISON. METHODS ARE CATEGORIZED INTO TIME-DOMAIN, FREQUENCY-DOMAIN, AND HYBRID
ARCHITECTURES. HYBRID MODELS COMBINE BOTH TIME AND FREQUENCY DOMAIN REPRESENTATIONS. ALL SOURCE CODES ARE PUBLICLY
AVAILABLE.
Method
Type
Full Name
Source Code
TimeKAN [22]
Hybrid
KAN-Based Frequency Decomposition Architecture
for Long-Term Time Series Forecasting
Code
ATFNet [36]
Hybrid
Adaptive Time-Frequency Ensembled Network for
Time Series Forecasting
Code
FreTS [14]
Frequency
Frequency-Domain MLPs for Enhanced Time Series
Forecasting
Code
LTSF-Linear [16]
Time
Simple Linear Baselines for Long-Term Time Series
Forecasting
Code
TSMixer [41]
Time
All-MLP Architecture for Time Series Forecasting
Code
FEDformer [34]
Frequency
Frequency Enhanced Decomposed Transformer for
Long-Term Forecasting
Code
Informer [8]
Time
Efficient Transformer with ProbSparse Attention for
Long Series
Code
Autoformer [9]
Hybrid
Decomposition Transformer with Auto-Correlation
Mechanism
Code
TABLE III
COMPARISON OF TFKAN AGAINST EIGHT SOTA BASELINES. THE LOOKBACK WINDOW IS FIXED AT L = 96 FOR ALL DATASETS. FOR THE ILI DATASET,
PREDICTION LENGTHS ARE τ ∈{24, 36, 48, 60}, WHILE FOR THE REMAINING DATASETS, τ ∈{96, 192, 336, 720}. THE BEST RESULTS ARE BOLDED,
AND THE SECOND-BEST ARE UNDERLINED. THE BOTTOM TWO ROWS REPORT THE NUMBER OF TIMES EACH METHOD ACHIEVES THE BEST OR
SECOND-BEST PERFORMANCE ACROSS ALL EXPERIMENTS.
Model
TFKAN
TimeKAN
ATFNet
FreTS
LTSF-Linear
TSMixer
FEDformer
Informer
Autoformer
Metrics
MAE
RMSE
MAE
RMSE
MAE
RMSE
MAE
RMSE
MAE
RMSE
MAE
RMSE
MAE
RMSE
MAE
RMSE
MAE
RMSE
ILI
24
0.146
0.211
0.151
0.223
0.149
0.216
0.157
0.228
0.167
0.236
0.231
0.306
0.184
0.251
0.241
0.344
0.205
0.273
36
0.137
0.206
0.146
0.216
0.138
0.209
0.165
0.229
0.160
0.226
0.238
0.318
0.180
0.250
0.274
0.383
0.204
0.274
48
0.139
0.206
0.147
0.216
0.147
0.217
0.166
0.230
0.161
0.226
0.251
0.340
0.186
0.257
0.274
0.384
0.200
0.270
60
0.149
0.215
0.159
0.227
0.150
0.220
0.166
0.228
0.158
0.222
0.273
0.367
0.193
0.265
0.289
0.404
0.208
0.280
ETTh1
96
0.061
0.088
0.063
0.092
0.064
0.092
0.063
0.091
0.063
0.091
0.077
0.107
0.063
0.089
0.082
0.108
0.074
0.103
192
0.067
0.093
0.067
0.097
0.073
0.101
0.069
0.096
0.067
0.096
0.089
0.121
0.067
0.096
0.115
0.146
0.078
0.109
336
0.071
0.098
0.069
0.099
0.086
0.112
0.073
0.100
0.071
0.099
0.101
0.134
0.078
0.110
0.124
0.156
0.081
0.112
720
0.082
0.109
0.080
0.110
0.116
0.150
0.084
0.111
0.083
0.111
0.119
0.150
0.086
0.117
0.125
0.159
0.086
0.119
ETTh2
96
0.036
0.052
0.045
0.068
0.035
0.051
0.038
0.052
0.036
0.051
0.090
0.114
0.052
0.076
0.051
0.067
0.052
0.075
192
0.040
0.057
0.052
0.077
0.046
0.060
0.043
0.059
0.041
0.057
0.105
0.132
0.059
0.084
0.048
0.064
0.061
0.085
336
0.041
0.058
0.058
0.083
0.067
0.087
0.044
0.060
0.042
0.058
0.117
0.148
0.068
0.093
0.060
0.079
0.065
0.089
720
0.047
0.065
0.062
0.088
0.072
0.099
0.067
0.089
0.053
0.070
0.105
0.129
0.069
0.094
0.085
0.106
0.066
0.090
ETTm1
96
0.054
0.079
0.055
0.082
0.056
0.082
0.054
0.079
0.055
0.080
0.061
0.088
0.058
0.083
0.071
0.096
0.070
0.102
192
0.058
0.085
0.057
0.085
0.061
0.088
0.058
0.085
0.060
0.087
0.067
0.094
0.064
0.090
0.073
0.101
0.071
0.100
336
0.063
0.091
0.062
0.092
0.065
0.093
0.063
0.092
0.065
0.094
0.074
0.101
0.069
0.095
0.085
0.110
0.072
0.104
720
0.069
0.096
0.070
0.098
0.072
0.100
0.069
0.098
0.071
0.100
0.082
0.111
0.073
0.104
0.096
0.122
0.075
0.110
ETTm2
96
0.029
0.041
0.033
0.051
0.030
0.042
0.032
0.044
0.029
0.041
0.065
0.083
0.038
0.056
0.031
0.043
0.039
0.058
192
0.033
0.047
0.038
0.060
0.032
0.047
0.036
0.049
0.032
0.046
0.079
0.101
0.043
0.064
0.037
0.048
0.043
0.065
336
0.037
0.052
0.045
0.068
0.038
0.053
0.040
0.055
0.039
0.054
0.094
0.121
0.048
0.072
0.044
0.059
0.046
0.070
720
0.041
0.059
0.051
0.078
0.043
0.061
0.044
0.061
0.041
0.058
0.128
0.160
0.055
0.082
0.060
0.084
0.054
0.081
Weather
96
0.038
0.076
0.038
0.077
0.039
0.080
0.040
0.083
0.041
0.081
0.045
0.077
0.052
0.085
0.070
0.102
0.059
0.094
192
0.045
0.085
0.045
0.087
0.048
0.091
0.049
0.100
0.048
0.090
0.052
0.085
0.059
0.095
0.086
0.124
0.066
0.105
336
0.052
0.096
0.053
0.097
0.055
0.099
0.059
0.141
0.057
0.099
0.058
0.093
0.068
0.105
0.091
0.133
0.068
0.107
720
0.060
0.106
0.060
0.107
0.062
0.107
0.063
0.106
0.065
0.108
0.066
0.103
0.074
0.115
0.116
0.160
0.078
0.121
Air
96
0.058
0.089
0.060
0.095
0.059
0.092
0.070
0.096
0.062
0.088
0.111
0.174
0.101
0.180
0.089
0.130
0.093
0.127
192
0.061
0.093
0.061
0.098
0.061
0.094
0.075
0.103
0.070
0.096
0.120
0.187
0.108
0.190
0.108
0.150
0.116
0.191
336
0.068
0.099
0.069
0.104
0.070
0.105
0.075
0.103
0.071
0.097
0.126
0.194
0.112
0.193
0.143
0.189
0.120
0.201
720
0.077
0.110
0.083
0.127
0.082
0.119
0.084
0.113
0.076
0.102
0.138
0.209
0.129
0.211
0.186
0.272
0.125
0.205
Num
First
21
20
9
1
3
1
2
2
6
9
0
3
1
0
0
0
0
0
Second
7
8
6
7
9
8
5
7
7
4
0
1
1
2
0
0
0
0
• Hybrid/Dual-branch
methods.
Autoformer
[9]
is
a Transformer variant that leverages auto-correlation
and series decomposition to model temporal patterns.
TimeKAN [22] integrates KAN with frequency repre-
sentations derived via FFT/IFFT but applies KAN exclu-
sively in the time domain. ATFNet [36] features a dual-
branch design that combines time- and frequency-domain
modules to capture both local and global dependencies.
Metrics. To evaluate the performance of TFKAN, two
commonly used metrics, Mean Absolute Error (MAE) and
Root Mean Squared Error (RMSE), are selected. MAE mea-
sures the average magnitude of errors, providing an intuitive
interpretation of prediction accuracy. RMSE emphasizes larger
errors, offering a more comprehensive evaluation of model
robustness.
Experimental Environment. All code is implemented in
Python using the PyTorch deep learning framework, developed
within the PyCharm IDE on a Windows 10 environment. All
experiments are conducted on a server running Ubuntu 20.04,
equipped with an NVIDIA GeForce RTX 3090 GPU (24 GB
VRAM), an Intel Xeon Gold 6230 CPU, and 128 GB of
RAM. To ensure reproducibility, random seeds are fixed across
NumPy, PyTorch, and Python’s built-in random module. The
KAN module is configured with a grid size of s = 2 and a
spline order of k = 1, with each KAN layer using a hidden size
of 258. Input data is normalized using the MinMaxScaler. We
adopt the Adam optimizer with a learning rate adjusted from
the range [10−6, 10−2], and batch sizes are adjusted from the
range [4, 64]. All models are trained for up to 10 epochs with
early stopping based on validation loss.


---

## Page 7

7
B. Main Results
To address RQ1, we conduct a comprehensive evaluation
of TFKAN against eight SOTA forecasting models on seven
widely used time series datasets. The overall results are
presented in Table III. Following standard practice [9], we
set the lookback window size to L = 96 for all datasets. For
the relatively short ILI dataset, prediction lengths are chosen
as τ ∈{24, 36, 48, 60}, while for the remaining datasets, we
use τ ∈{96, 192, 336, 720}.
Overall Performance. TFKAN achieves consistently su-
perior results across all datasets and forecasting lengths,
outperforming all baseline methods in terms of both MAE
and RMSE. On the ILI dataset, TFKAN achieves the best
performance across all prediction lengths. For example, at
τ = 24, it achieves an MAE of 0.146 and an RMSE of
0.211. On ETTh2 with τ = 720, TFKAN achieves a MAE
of 0.047 and RMSE of 0.065, significantly outperforming all
other methods.
Comparison with Frequency-domain and Hybrid Base-
lines. To assess the benefits of frequency-domain modeling,
we include several strong baselines that leverage spectral infor-
mation, including Autoformer, FreTS, FEDformer, TimeKAN,
and ATFNet. These models incorporate frequency components
through various mechanisms such as spectral decomposition,
energy-based MLP design, or FFT/IFFT processing. Among
them, TimeKAN achieves competitive results on ETTh1, while
ATFNet performs strongly on ETTh2 due to its dual-branch
attention and extended DFT module. Nevertheless, TFKAN
consistently surpasses all these frequency-domain and hy-
brid models, highlighting the advantage of directly applying
KAN in the frequency domain. For instance, on ETTh2 with
τ = 336, TFKAN achieves a MAE of 0.042 and RMSE of
0.059, outperforming ATFNet (0.067/0.087) and TimeKAN
(0.058/0.083) by a significant margin.
Considering Dataset Characteristics. TFKAN demon-
strates strong adaptability across datasets of different scales
and characteristics. On smaller datasets like ILI, it shows ex-
cellent generalization and robustness. On large-scale datasets
with longer sequences, such as Weather and ETTm1, TFKAN
maintains SOTA performance by effectively capturing long-
range dependencies and periodic structures.
C. Ablation Studies
To answer RQ2, a series of ablation studies is conducted to
evaluate the effectiveness of the key components in TFKAN.
Specifically, the contributions of the KAN-based modules,
the dual-branch architecture, and the dimension adjustment
strategy are analyzed.
TFKAN vs. MLP. To investigate the contribution of KAN
modules in different parts of the architecture, we conduct com-
prehensive ablation experiments by replacing KAN with stan-
dard two-layer MLPs. Specifically, we test the following con-
figurations: MLP, where all KANs are replaced; MLP time,
MLP freq, and MLP pred, where KANs are removed only
from the time branch, frequency branch, or the predictor,
respectively; and their combinations, such as MLP time freq,
MLP pred freq, and MLP pred time. The results are reported
in Table IV, evaluated on four datasets (ILI, ETTh1, ETTh2,
and Air) across various forecasting lengths. All experiments
use a fixed lookback window size of L = 96 and are measured
in terms of MAE and RMSE. 1) Consistent effectiveness
of KAN. TFKAN achieves the best performance across all
datasets and prediction lengths in every case. For instance,
on ILI with prediction length 24, TFKAN reaches a MAE
of 0.146 and RMSE of 0.211, outperforming the fully MLP-
based model (MAE: 0.152, RMSE: 0.217). The performance
gap persists across larger prediction lengths and other datasets.
2) Each KAN branch independently contributes to per-
formance. Replacing KAN in any single module—whether
in the MLP time, MLP freq, or the MLP pred, leads to
consistent performance drops compared to the full TFKAN
model. For instance, on the ETTh2 dataset with prediction
length 720, MLP time, MLP freq, and MLP pred all show
higher MAE and RMSE than TFKAN, increasing MAE from
0.047 to 0.066, 0.060, and 0.067, respectively. Similar trends
are observed across other datasets. These results indicate
that each KAN component plays a distinct role in capturing
temporal or frequency dynamics, and none can be removed
without compromising the model’s accuracy. 3) Compound
replacements often lead to larger performance degrada-
tion. When KAN is removed from multiple components, such
as in MLP pred time or MLP pred freq, performance tends
to degrade more significantly compared to removing only
a single component. For example, on the Air dataset with
prediction length 336, MLP pred freq yields a MAE of 0.095,
which is notably worse than MLP pred at 0.073. These prove
the cumulative benefit of retaining KAN in multiple modules.
Dual-Branch vs. Single-Branch Architectures. To eval-
uate the effectiveness of the dual-branch architecture in
TFKAN, we compare it with two single-branch variants:
Only Time and Only Freq. The Only Time variant retains
only the time-domain branch, while Only Freq keeps only
the frequency-domain branch. Table V summarizes the results
across four datasets using the same experimental settings as
in the KAN ablation. 1) Dual-branch TFKAN consistently
outperforms single-branch variants. TFKAN achieves the
best performance in all datasets and prediction lengths. For
example, on the ILI dataset with τ
= 24, TFKAN ob-
tains a MAE of 0.146 and RMSE of 0.211, significantly
outperforming Only Time (MAE: 0.226, RMSE: 0.296) and
Only Freq (MAE: 0.169, RMSE: 0.236). This consistent trend
holds across longer prediction lengths and other datasets. 2)
Time-frequency integration improves generalization. Both
single-branch models exhibit inferior performance compared
to the full TFKAN, indicating that time-domain and frequency-
domain information are complementary. Notably, on ETTh2
with τ
= 720, TFKAN achieves a MAE of 0.047 and
RMSE of 0.065, while Only Time and Only Freq degrade
to 0.057 / 0.076 and 0.074 / 0.105, respectively. These results
support that integrating both domains enables more robust and
generalizable forecasting, and thus validates the architectural
design of TFKAN.
Dimension Adjustment Strategy. To evaluate the effec-
tiveness of the proposed dimension adjustment mechanism in
TFKAN, we compare the full model against three ablated vari-


---

## Page 8

8
TABLE IV
ABLATION STUDY COMPARING TFKAN WITH VARIANTS WHERE TWO-LAYER MLPS PARTIALLY OR FULLY REPLACE KAN MODULES. THE LOOKBACK
WINDOW SIZE IS FIXED TO L = 96. METRICS ARE MAE AND RMSE. BEST RESULTS ARE HIGHLIGHTED IN BOLD.
Model
TFKAN
MLP
MLP time
MLP freq
MLP pred
MLP time freq
MLP pred time
MLP pred freq
Metrics
MAE
RMSE
MAE
RMSE
MAE
RMSE
MAE
RMSE
MAE
RMSE
MAE
RMSE
MAE
RMSE
MAE
RMSE
ILI
24
0.146
0.211
0.152
0.217
0.152
0.216
0.152
0.217
0.159
0.220
0.157
0.222
0.162
0.225
0.163
0.227
36
0.137
0.206
0.140
0.207
0.141
0.207
0.140
0.208
0.151
0.212
0.139
0.207
0.147
0.210
0.150
0.212
48
0.139
0.206
0.141
0.207
0.143
0.208
0.141
0.208
0.157
0.220
0.148
0.213
0.153
0.217
0.165
0.228
60
0.149
0.215
0.150
0.216
0.153
0.219
0.150
0.216
0.169
0.233
0.157
0.223
0.166
0.229
0.171
0.234
ETTh1
96
0.061
0.088
0.063
0.090
0.062
0.089
0.063
0.090
0.064
0.091
0.062
0.089
0.063
0.091
0.064
0.092
192
0.067
0.093
0.068
0.094
0.069
0.094
0.068
0.094
0.070
0.097
0.068
0.094
0.070
0.097
0.070
0.097
336
0.071
0.098
0.072
0.099
0.072
0.100
0.072
0.099
0.075
0.103
0.072
0.099
0.074
0.102
0.074
0.101
720
0.082
0.109
0.084
0.111
0.083
0.110
0.084
0.111
0.087
0.115
0.083
0.110
0.087
0.115
0.085
0.113
ETTh2
96
0.036
0.052
0.038
0.053
0.038
0.054
0.038
0.053
0.038
0.053
0.038
0.053
0.039
0.055
0.037
0.053
192
0.040
0.057
0.043
0.059
0.042
0.058
0.043
0.059
0.041
0.058
0.043
0.059
0.045
0.061
0.043
0.059
336
0.041
0.058
0.047
0.064
0.047
0.064
0.047
0.064
0.046
0.062
0.050
0.066
0.047
0.064
0.047
0.065
720
0.047
0.065
0.060
0.081
0.066
0.091
0.060
0.081
0.067
0.087
0.078
0.105
0.074
0.105
0.068
0.099
Air
96
0.058
0.089
0.063
0.091
0.060
0.090
0.063
0.091
0.062
0.092
0.061
0.091
0.063
0.092
0.064
0.094
192
0.061
0.093
0.070
0.098
0.070
0.098
0.070
0.098
0.069
0.098
0.070
0.100
0.079
0.106
0.077
0.106
336
0.068
0.099
0.079
0.108
0.072
0.101
0.079
0.108
0.073
0.102
0.077
0.107
0.094
0.120
0.095
0.121
720
0.077
0.110
0.094
0.123
0.086
0.113
0.094
0.123
0.085
0.116
0.088
0.120
0.087
0.118
0.090
0.123
TABLE V
COMPARISON OF TFKAN WITH SINGLE-BRANCH ARCHITECTURES
(ONLY TIME AND ONLY FREQ) ACROSS FOUR DATASETS. THE
EVALUATION IS ALSO BASED ON MAE AND RMSE, WITH A LOOKBACK
WINDOW SIZE OF L = 96. BEST RESULTS ARE HIGHLIGHTED IN BOLD.
Model
TFKAN
Only Time
Only Freq
Metrics
MAE
RMSE
MAE
RMSE
MAE
RMSE
ILI
24
0.146
0.211
0.226
0.296
0.169
0.236
36
0.137
0.206
0.350
0.477
0.157
0.223
48
0.139
0.206
0.375
0.514
0.153
0.219
60
0.149
0.215
0.384
0.527
0.167
0.235
ETTh1
96
0.061
0.088
0.066
0.094
0.066
0.093
192
0.067
0.093
0.071
0.098
0.069
0.096
336
0.071
0.098
0.078
0.106
0.073
0.100
720
0.082
0.109
0.093
0.121
0.087
0.115
ETTh2
96
0.036
0.052
0.040
0.055
0.041
0.057
192
0.040
0.057
0.044
0.062
0.047
0.066
336
0.041
0.058
0.049
0.066
0.054
0.080
720
0.047
0.065
0.057
0.076
0.074
0.105
Air
96
0.058
0.089
0.068
0.101
0.061
0.090
192
0.061
0.093
0.071
0.104
0.071
0.098
336
0.068
0.099
0.075
0.108
0.074
0.104
720
0.077
0.110
0.086
0.118
0.085
0.117
TABLE VI
COMPARISON OF TFKAN WITH THREE DIMENSION ADJUSTMENT
VARIANTS (ALL ADJUST, NO ADJUST, AND ONLY TIME ADJUST)
ACROSS FOUR DATASETS. THE EVALUATION IS BASED ON MAE AND
RMSE WITH A LOOKBACK WINDOW SIZE OF L = 96. BEST RESULTS ARE
HIGHLIGHTED IN BOLD, WHILE THE SECOND-BEST RESULTS ARE
UNDERLINED.
Model
TFKAN
All Adjust
No Adjust
Only Time Adjust
Metrics
MAE
RMSE
MAE
RMSE
MAE
RMSE
MAE
RMSE
ILI
24
0.146
0.211
0.159
0.223
0.219
0.292
0.226
0.296
36
0.137
0.206
0.148
0.214
0.267
0.366
0.350
0.477
48
0.139
0.206
0.153
0.219
0.287
0.395
0.375
0.514
60
0.149
0.215
0.164
0.230
0.296
0.406
0.384
0.527
ETTh1
96
0.061
0.088
0.063
0.091
0.066
0.093
0.066
0.094
192
0.067
0.093
0.069
0.096
0.074
0.101
0.071
0.098
336
0.071
0.098
0.072
0.099
0.074
0.102
0.078
0.106
720
0.082
0.109
0.085
0.112
0.093
0.120
0.093
0.121
ETTh2
96
0.036
0.052
0.040
0.056
0.041
0.057
0.038
0.054
192
0.040
0.057
0.042
0.059
0.049
0.068
0.044
0.062
336
0.041
0.058
0.047
0.066
0.057
0.080
0.049
0.066
720
0.047
0.065
0.056
0.075
0.058
0.077
0.057
0.076
Air
96
0.058
0.089
0.064
0.091
0.063
0.093
0.068
0.101
192
0.061
0.093
0.068
0.097
0.066
0.097
0.071
0.104
336
0.068
0.099
0.074
0.103
0.078
0.109
0.075
0.108
720
0.077
0.110
0.091
0.126
0.086
0.118
0.083
0.116
ants: All Adjust, No Adjust, and Only Time Adjust. Specifi-
cally, All Adjust applies upscaling to all hidden dimensions in
both time and frequency branches, No Adjust omits dimension
adjustment entirely, and Only Time Adjust applies the adjust-
ment only in the time-domain branch. Table VI summarizes
the results across four datasets under the same settings as
previous ablations. 1) TFKAN consistently outperforms all
variants. Across all datasets and prediction lengths, TFKAN
achieves the lowest MAE and RMSE values, as highlighted in
bold. For example, on the ILI dataset with τ = 24, TFKAN
obtains a MAE of 0.146 and RMSE of 0.211, outperforming
All Adjust (0.159 / 0.223), No Adjust (0.219 / 0.292), and
Only Time Adjust (0.226 / 0.296). These results confirm the
effectiveness of our selective dimension adjustment strategy.
2) Selective adjustment is more effective than full or no
adjustment. Among the ablated models, All Adjust generally
performs better than both No Adjust and Only Time Adjust,
but still underperforms TFKAN. This suggests that indis-
criminately increasing dimensionality across all branches may
introduce redundancy or noise, limiting performance.
TABLE VII
COMPARISON OF TFKAN WITH TWO SEPARATE KAN (TWO FREQKAN)
FOR PROCESSING THE REAL AND IMAGINARY COMPONENTS IN THE
FREQUENCY BRANCH. RESULTS ARE REPORTED ON FOUR DATASETS WITH
MULTIPLE PREDICTION LENGTHS (LOOKBACK WINDOW L = 96). THE
BEST PERFORMANCE FOR EACH SETTING IS HIGHLIGHTED IN BOLD.
Model
TFKAN
Two FreqKAN
Metrics
MAE
RMSE
MAE
RMSE
ILI
24
0.146
0.211
0.140
0.207
36
0.137
0.206
0.137
0.205
48
0.139
0.206
0.139
0.204
60
0.149
0.215
0.154
0.220
ETTh1
96
0.061
0.088
0.061
0.088
192
0.067
0.093
0.066
0.093
336
0.071
0.098
0.071
0.098
720
0.082
0.109
0.082
0.109
ETTh2
96
0.036
0.052
0.038
0.053
192
0.040
0.057
0.040
0.057
336
0.041
0.058
0.042
0.060
720
0.047
0.065
0.058
0.077
Air
96
0.058
0.089
0.059
0.090
192
0.061
0.093
0.066
0.101
336
0.068
0.099
0.081
0.111
720
0.077
0.110
0.078
0.111


---

## Page 9

9
Shared vs. Independent Frequency-Domain KANs. To
explore whether using separate KAN modules for the real
and imaginary parts of the frequency branch improves perfor-
mance, we compare the standard TFKAN design, which uses a
single shared KAN to process both parts, with a variant named
Two FreqKAN, where two independent KANs are used. Table
VII reports the results across four datasets. 1) Comparable
performance on most datasets. The overall results show
that Two FreqKAN yields similar or slightly improved perfor-
mance on some datasets such as ILI and ETTh1, e.g., on ILI
(τ = 24), the MAE decreases from 0.146 to 0.140. However,
in most cases, the differences are marginal. 2) Minor gains
do not justify complexity. While using two KANs for the
frequency branch can improve expressiveness, it doubles the
parameter count and computational cost for that component.
On ETTh1, both variants perform almost identically. For
example, on ETTh1 (τ = 96), both achieve MAE/RMSE of
0.061/0.088. Additionally, in the Fourier spectrum, the real
and imaginary parts’ local peaks are in the same position on
the frequency axis, but differ only in amplitude/phase. The
shared spline basis forces them to adjust synchronically at
the same node, which is equivalent to imposing a ”conjugate
consistency” regularity on the network, which can suppress
overfitting. Given the negligible accuracy gains and higher
complexity, we retain the shared KAN design in TFKAN for
its simplicity and efficiency.
D. Parameter Sensitivity Analysis
To address RQ3, parameter sensitivity studies are conducted
to analyze the impact of two key hyperparameters: the input
length L and the embedding size d. These experiments evalu-
ate how changes in L and d influence forecasting accuracy on
prediction length τ = 96 (for ILI dataset, the τ = 24), mea-
sured by MAE and RMSE, and training efficiency, measured
by average time per epoch.
(a) Air
(c) ETTh2
(b) ETTh1
(d) ILI
MAE
MAE
RMSE
RMSE
L
L
L
L
Fig. 3. Parameter sensitivity studies of the input length L.
Input Length L. The parameter sensitivity study on input
length L evaluates its effect on performance across four
datasets: ETTh1, ETTh2, ILI, and Air. The results are visu-
alized in Fig. 3. The x-axis represents the input length L,
while the orange line, green line, and blue bars represent
MSE, RMSE, and average time per epoch, respectively. 1)
Performance trends: Increasing L generally enhances fore-
casting accuracy for most datasets, as it provides the model
with more historical context. However, excessive input length
can disrupt performance, possibly due to information overload.
For instance, on the Air dataset, MAE improves from 0.064 to
0.056 when L increases from 48 to 192, but a slight decline is
observed at L = 336. 2) Dataset characteristics: On smaller
datasets like ILI, increasing L beyond 96 offers minimal
accuracy improvements, while the additional computational
overhead is negligible. However, MAE increases from 0.146
at L = 96 to 0.255 at L = 336, indicating diminishing
returns for larger input lengths. 3) Efficiency: Larger input
lengths increase computation time significantly. For example,
on ETTh1, the time per epoch rises from 12.96 seconds at
L = 48 to 28.96 seconds at L = 336. A balance between
performance and efficiency is achieved at moderate L values,
such as L = 96 or L = 192.
(a) Air
(c) ETTh2
(b) ETTh1
(d) ILI
MAE
MAE
RMSE
RMSE
d
d
d
d
Fig. 4. Parameter sensitivity studies of the embedding size d.
Embedding Size d. The sensitivity study on embedding
size d evaluates its effect on model performance and training
efficiency across the same datasets. The results are visualized
in Fig. 4. The x-axis represents embedding size d, while the
orange, green, and blue lines indicate MSE, RMSE, and time
per epoch, respectively. 1) Performance trends: Increasing d
generally improves accuracy until a certain point, after which
performance plateaus or slightly degrades. For example, on
the ILI dataset, MAE decreases from 0.177 at d = 32 to
0.146 at d = 128, but then increases to 0.179 at d = 512.
Similarly, for the Air dataset, MAE increases to 0.065 at
d = 512. 2) Dataset characteristics: Smaller datasets, such
as ILI, are more sensitive to variations in d, with performance
gains degrading as d surpasses the optimal value. In contrast,
larger datasets, such as ETTh1 and ETTh2, exhibit more stable
performance across a range of d values, with the changes
within 0.002, demonstrating greater robustness to changes in
this hyperparameter d. 3) Efficiency: Larger embedding sizes
significantly increase training times without corresponding
improvements in accuracy. For instance, on ETTh2, the time


---

## Page 10

10
TABLE VIII
COMPARISON OF PARAMETER COUNT AND GPU MEMORY USAGE (BATCH SIZE = 64) FOR ALL MODELS ON THE ILI DATASET UNDER DIFFERENT
PREDICTION LENGTHS.
Pred Len
TFKAN (Our)
TimeKAN
ATFNet
FreTS
LTSF-Linear
Param Count / GPU Memory (MB, batch size = 64)
24
16.33M / 250.65
31.1K / 550.99
19.20M / 1718.67
3.22M / 283.39
4.66K / 1.53
36
16.35M / 250.96
32.3K / 551.05
19.28M / 1720.12
3.22M / 283.53
6.98K / 1.96
48
16.36M / 251.27
33.5K / 551.11
19.37M / 1719.97
3.22M / 283.67
9.31K / 2.39
60
16.38M / 251.58
34.6K / 551.17
19.45M / 1721.78
3.22M / 283.81
11.6K / 2.82
Pred Len
TFKAN (Our)
TSMixer
FEDformer
Informer
Autoformer
Param Count / GPU Memory (MB, batch size = 64)
24
16.33M / 250.65
215.5K / 54.66
14.47M / 1508.79
11.33M / 1475.51
10.54M / 2019.37
36
16.35M / 250.96
216.7K / 54.77
14.86M / 1575.80
11.33M / 1535.33
10.54M / 2139.58
48
16.36M / 251.27
217.9K / 54.88
15.25M / 1641.18
11.33M / 1596.93
10.54M / 2290.05
60
16.38M / 251.58
219.0K / 55.00
15.65M / 1713.07
11.33M / 1664.20
10.54M / 2460.84
per epoch increases from 7.67 seconds at d = 128 to 20.77
seconds at d = 512. As a result, an embedding size of d = 128
strikes a balance between accuracy and efficiency for most
datasets.
E. Efficiency Analysis
Table VIII presents the parameter counts and GPU memory
usage (under batch size = 64) for TFKAN and eight baseline
models on the ILI dataset under different prediction lengths.
Despite its strong performance, TFKAN maintains a relatively
low memory footprint (approximately 251 MB across all
settings), which is significantly lower than Transformer-based
models like FEDformer, Informer, and Autoformer, whose
GPU usage exceeds 1.5 GB in most cases. In terms of pa-
rameter count, TFKAN (16.3M) is comparable to FEDformer
(14.5M–15.6M) and notably smaller than ATFNet (up to
19.4M). Compared to lightweight models such as LTSF-Linear
and TSMixer, which have only a few thousand to a few hun-
dred thousand parameters, TFKAN trades off slightly higher
complexity for substantially better accuracy, as shown in
previous sections. Overall, these results highlight that TFKAN
strikes a favorable balance between forecasting performance
and computational efficiency. Its GPU memory usage remains
moderate while delivering SOTA accuracy across datasets and
prediction lengths.
F. Predictions Visualizations
Fig. 5 visualizes the predictions and their comparison with
the ground truth on the ETTm2 dataset. The ’I/O’ notation
refers to the input and output, representing the lookback
window size L and prediction length τ, respectively.
V. CONCLUSION
In this paper, we introduce a novel frequency-domain
Kolmogorov-Arnold Network (KAN) for time series forecast-
ing. Building upon this foundation, we propose the Time-
Frequency Kolmogorov-Arnold Network (TFKAN). TFKAN
employs a dual-branch architecture, where the frequency-
domain KAN extracts frequency features and the time-domain
KAN captures temporal dependencies, enabling the effective
integration of complementary information from both domains.
To address the heterogeneity between the time and frequency
(a) I/O = 96/96
(b) I/O = 96/192
(c) I/O = 96/336
(d) I/O = 96/720
Fig. 5.
Visualizations of predictions (ground truth vs. predictions) on the
ETTm2 dataset. ’I/O’ denotes lookback window size L / prediction length τ.
branches, we introduce a dimension-adjustment mechanism,
which enhances the model’s performance and robustness. Ex-
tensive experiments on seven time-series datasets demonstrate
that TFKAN consistently outperforms eight SOTA methods,
underscoring its superior forecasting capabilities. This work
represents the first successful application of the frequency-
domain KAN to time series forecasting. Future research will
focus on optimizing TFKAN’s efficiency, particularly by re-
ducing its parameter count, to further enhance its performance.
REFERENCES
[1] Z. Shao, F. Wang, Y. Xu, W. Wei, C. Yu, Z. Zhang, D. Yao, T. Sun,
G. Jin, X. Cao, G. Cong, C. S. Jensen, and X. Cheng, “Exploring
progress in multivariate time series forecasting: Comprehensive bench-
marking and heterogeneity analysis,” IEEE Transactions on Knowledge
and Data Engineering, vol. 37, no. 1, pp. 291–305, 2025.
[2] Y. Jia, Y. Lin, X. Hao, Y. Lin, S. Guo, and H. Wan, “Witran: Water-
wave information transmission and recurrent acceleration network for
long-range time series forecasting,” Advances in Neural Information
Processing Systems, vol. 36, 2024.
[3] B. Lim and S. Zohren, “Time-series forecasting with deep learning: a
survey,” Philosophical Transactions of the Royal Society A, vol. 379,
no. 2194, p. 20200209, 2021.
[4] J. Kim, H. Kim, H. Kim, D. Lee, and S. Yoon, “A comprehensive survey
of deep learning for time series forecasting: architectural diversity and


---

## Page 11

11
open challenges,” Artificial Intelligence Review, vol. 58, no. 7, pp. 1–95,
2025.
[5] L. Su, X. Zuo, R. Li, X. Wang, H. Zhao, and B. Huang, “A systematic
review for transformer-based long-term series forecasting,” Artificial
Intelligence Review, vol. 58, no. 3, p. 80, 2025.
[6] Z. Chen, M. Ma, T. Li, H. Wang, and C. Li, “Long sequence time-series
forecasting with deep learning: A survey,” Information Fusion, vol. 97,
p. 101819, 2023.
[7] Q. Wen, T. Zhou, C. Zhang, W. Chen, Z. Ma, J. Yan, and L. Sun,
“Transformers in time series: a survey,” in Proceedings of the Thirty-
Second International Joint Conference on Artificial Intelligence, 2023,
pp. 6778–6786.
[8] H. Zhou, S. Zhang, J. Peng, S. Zhang, J. Li, H. Xiong, and W. Zhang,
“Informer: Beyond efficient transformer for long sequence time-series
forecasting,” in Proceedings of the AAAI conference on artificial intel-
ligence, vol. 35, no. 12, 2021, pp. 11 106–11 115.
[9] H. Wu, J. Xu, J. Wang, and M. Long, “Autoformer: Decomposition
transformers with Auto-Correlation for long-term series forecasting,” in
Advances in Neural Information Processing Systems, 2021.
[10] Y. Nie, N. H. Nguyen, P. Sinthong, and J. Kalagnanam, “A time
series is worth 64 words: Long-term forecasting with transformers,” in
International Conference on Learning Representations, 2023.
[11] Z. Liu, Y. Wang, S. Vaidya, F. Ruehle, J. Halverson, M. Soljaˇci´c,
T. Y. Hou, and M. Tegmark, “Kan: Kolmogorov-arnold networks,” arXiv
preprint arXiv:2404.19756, 2024.
[12] K. Xu, L. Chen, and S. Wang, “Kolmogorov-arnold networks for time
series: Bridging predictive power and interpretability,” arXiv preprint
arXiv:2406.02496, 2024.
[13] C. J. Vaca-Rubio, L. Blanco, R. Pereira, and M. Caus, “Kolmogorov-
arnold networks (kans) for time series analysis,” arXiv preprint
arXiv:2405.08790, 2024.
[14] K. Yi, Q. Zhang, W. Fan, S. Wang, P. Wang, H. He, N. An, D. Lian,
L. Cao, and Z. Niu, “Frequency-domain mlps are more effective learners
in time series forecasting,” Advances in Neural Information Processing
Systems, vol. 36, 2024.
[15] D. Cao, Y. Wang, J. Duan, C. Zhang, X. Zhu, C. Huang, Y. Tong,
B. Xu, J. Bai, J. Tong et al., “Spectral temporal graph neural network
for multivariate time-series forecasting,” Advances in neural information
processing systems, vol. 33, pp. 17 766–17 778, 2020.
[16] A. Zeng, M. Chen, L. Zhang, and Q. Xu, “Are transformers effective
for time series forecasting?” in Proceedings of the AAAI conference on
artificial intelligence, vol. 37, no. 9, 2023, pp. 11 121–11 128.
[17] X. Han, X. Zhang, Y. Wu, Z. Zhang, and Z. Wu, “Kan4tsf: Are kan and
kan-based models effective for time series forecasting?” arXiv preprint
arXiv:2408.11306, 2024.
[18] R. Genet and H. Inzirillo, “Tkan: Temporal kolmogorov-arnold net-
works,” arXiv preprint arXiv:2405.07344, 2024.
[19] ——, “A temporal kolmogorov-arnold transformer for time series fore-
casting,” ArXiv, 2024.
[20] A. Bhattacharya and N. Haq, “Zero shot time series forecasting using
kolmogorov arnold networks,” arXiv preprint arXiv:2412.17853, 2024.
[21] S. Lee, J.-K. Kim, J. Kim, T. Kim, and J. Lee, “Hippo-kan: Efficient
kan model for time series analysis,” arXiv preprint arXiv:2410.14939,
2024.
[22] S. Huang, Z. Zhao, C. Li, and L. BAI, “TimeKAN: KAN-based
frequency decomposition learning architecture for long-term time
series
forecasting,”
in
The
Thirteenth
International
Conference
on
Learning
Representations,
2025.
[Online].
Available:
https:
//openreview.net/forum?id=wTLc79YNbh
[23] S. Li, X. Jin, Y. Xuan, X. Zhou, W. Chen, Y.-X. Wang, and X. Yan, “En-
hancing the locality and breaking the memory bottleneck of transformer
on time series forecasting,” Advances in neural information processing
systems, vol. 32, 2019.
[24] B. Lim, S. ¨O. Arık, N. Loeff, and T. Pfister, “Temporal fusion transform-
ers for interpretable multi-horizon time series forecasting,” International
Journal of Forecasting, vol. 37, no. 4, pp. 1748–1764, 2021.
[25] S. Lin, W. Lin, W. Wu, S. Wang, and Y. Wang, “Petformer: Long-term
time series forecasting via placeholder-enhanced transformer,” IEEE
Transactions on Emerging Topics in Computational Intelligence, 2024.
[26] Y. Zhang and J. Yan, “Crossformer: Transformer utilizing cross-
dimension dependency for multivariate time series forecasting,” in The
eleventh international conference on learning representations, 2023.
[27] T. Zhang, Y. Zhang, W. Cao, J. Bian, X. Yi, S. Zheng, and J. Li, “Less
is more: Fast multivariate time series forecasting with light sampling-
oriented mlp structures,” arXiv preprint arXiv:2207.01186, 2022.
[28] A. Das, W. Kong, A. Leach, S. Mathur, R. Sen, and R. Yu, “Long-
term forecasting with tide: Time-series dense encoder,” arXiv preprint
arXiv:2304.08424, 2023.
[29] Z. Li, Z. Rao, L. Pan, and Z. Xu, “Mts-mixers: Multivariate time series
forecasting via factorized temporal and channel mixing,” arXiv preprint
arXiv:2302.04501, 2023.
[30] S. Wang, H. Wu, X. Shi, T. Hu, H. Luo, L. Ma, J. Y. Zhang,
and J. ZHOU, “Timemixer: Decomposable multiscale mixing for
time series forecasting,” in The Twelfth International Conference
on
Learning
Representations,
2024.
[Online].
Available:
https:
//openreview.net/forum?id=7oLshfEIC2
[31] Q. Huang, L. Shen, R. Zhang, J. Cheng, S. Ding, Z. Zhou, and
Y. Wang, “Hdmixer: Hierarchical dependency with extendable patch
for multivariate time series forecasting,” in Proceedings of the AAAI
Conference on Artificial Intelligence, vol. 38, no. 11, 2024, pp. 12 608–
12 616.
[32] K. Xu, L. Chen, and S. Wang, “Are kan effective for identifying and
tracking concept drift in time series?” arXiv preprint arXiv:2410.10041,
2024.
[33] I. E. Livieris, “C-kan: A new approach for integrating convolutional
layers with kolmogorov–arnold networks for time-series forecasting,”
Mathematics, vol. 12, no. 19, p. 3022, 2024.
[34] T. Zhou, Z. Ma, Q. Wen, X. Wang, L. Sun, and R. Jin, “Fedformer:
Frequency enhanced decomposed transformer for long-term series fore-
casting,” in International conference on machine learning.
PMLR,
2022, pp. 27 268–27 286.
[35] Z.
Xu,
A.
Zeng,
and
Q.
Xu,
“FITS:
Modeling
time
series
with $10k$ parameters,” in The Twelfth International Conference
on
Learning
Representations,
2024.
[Online].
Available:
https:
//openreview.net/forum?id=bWcnvZ3qMb
[36] H. Ye, J. Chen, S. Gong, F. Jiang, T. Zhang, J. Chen, and X. Gao,
“Atfnet: Adaptive time-frequency ensembled network for long-term time
series forecasting,” arXiv preprint arXiv:2404.05192, 2024.
[37] Y. Chen, S. Liu, J. Yang, H. Jing, W. Zhao, and G. Yang, “A joint time-
frequency domain transformer for multivariate time series forecasting,”
Neural Networks, vol. 176, p. 106334, 2024.
[38] H. Yang, Y. Wang, Y. Wang, and J. Chen, “T-fia: Temporal-frequency in-
teractive attention network for long-term time series forecasting,” in Pa-
cific Rim International Conference on Artificial Intelligence.
Springer,
2024, pp. 257–268.
[39] K. Yan, C. Long, H. Wu, and Z. Wen, “Multi-resolution expansion of
analysis in time-frequency domain for time series forecasting,” IEEE
Transactions on Knowledge and Data Engineering, 2024.
[40] S. Elfwing, E. Uchibe, and K. Doya, “Sigmoid-weighted linear units
for neural network function approximation in reinforcement learning,”
Neural networks, vol. 107, pp. 3–11, 2018.
[41] S.-A. Chen, C.-L. Li, N. Yoder, S. O. Arik, and T. Pfister, “Tsmixer:
An all-mlp architecture for time series forecasting,” arXiv preprint
arXiv:2303.06053, 2023.
