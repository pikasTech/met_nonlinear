# A Unified Frequency Domain Decomposition Framework for Interpretable and Robust Time Series Forecasting
**Author**: Cheng He; Xijie Liang; Zengrong Zheng; Patrick P. C. Lee; Xu Huang; Zhaoyi Li; Hong Xie; Defu Lian; Enhong Chen
**Creator**: arXiv GenPDF (tex2pdf:e76afa9)

---

A Unified Frequency Domain Decomposition Framework for

Interpretable and Robust Time Series Forecasting

Cheng He

cheng.he@mail.ustc.edu.cn

University of Science and Technology

of China

Hefei, China

Xijie Liang

lxjie@blackwingasset.com

Shanghai Black Wing Asset

Management Co., Ltd.

Shanghai, China

Zengrong Zheng

lxjie@blackwingasset.com

Di-Matrix(Shanghai) Information

Technology Co., Ltd.

Shanghai, China

Patrick P.C. Lee

pclee@cse.cuhk.edu.hk

The Chinese University of Hong Kong

Hong Kong, China

Xu Huang

xuhuangcs@mail.ustc.edu.cn

University of Science and Technology

of China

Hefei, China

Zhaoyi Li

lizhaoyi777@mail.ustc.edu.cn

University of Science and Technology

of China

Hefei, China

Hong Xie

xiehong2018@foxmail.com

University of Science and Technology

of China

Hefei, China

Defu Lian

liandefu@ustc.edu.cn

University of Science and Technology

of China

Hefei, China

Enhong Chen

cheneh@ustc.edu.cn

University of Science and Technology

of China

Hefei, China

Abstract

Current approaches for time series forecasting, whether in the time

or frequency domain, predominantly use deep learning models

based on linear layers or transformers. They often encode time

series data in a black-box manner and rely on trial-and-error opti
mization solely based on forecasting performance, leading to limited

interpretability and theoretical understanding. Furthermore, the dy
namics in data distribution over time and frequency domains pose

a critical challenge to accurate forecasting. We propose FIRE, a

unified frequency domain decomposition framework that provides

a mathematical abstraction for diverse types of time series, so as

to achieve interpretable and robust time series forecasting. FIRE

introduces several key innovations: (i) independent modeling of

amplitude and phase components, (ii) adaptive learning of weights

of frequency basis components, (iii) a targeted loss function, and (iv)

a novel training paradigm for sparse data. Extensive experiments

demonstrate that FIRE consistently outperforms state-of-the-art

models on long-term forecasting benchmarks, achieving superior

predictive performance and significantly enhancing interpretability

of time series representations.

1

Introduction

Time series forecasting is a critical yet challenging task in vari
ous domains such as web mining, predictive maintenance of IoT

devices, traffic prediction, weather forecasting, electricity load man
agement, and financial analysis. Recently, the attention mechanism

[31] has proven highly effective, establishing transformer-based ar
chitectures as the dominant approach for time series representation

learning in the temporal domain [7, 19, 28, 33, 36, 37, 40, 43]. These

models outperform traditional recurrent neural networks (RNNs)

and convolutional neural networks (CNNs) [1, 2, 5, 8, 9, 16, 39], par
ticularly effective in capturing long-range dependencies. However,

time series data, composed of temporally ordered scalar sequences,

often fail to capture complex underlying patterns when analyzed

solely in the temporal domain.

To effectively capture the complex patterns of time series data,

recent research has explored frequency-domain representations

for time series data using Fast Fourier Transform (FFT). Notable

approaches such as FredFormer [27], FreTS [41], and FITS [38]

leverage frequency-domain techniques, including channel-wise

attention, frequency-temporal dependency modeling, and complex
valued interpolation, while WPMixer [24] employs wavelet de
composition combined with multiplayer perceptrons (MLPs) for

long-term forecasting. Hybrid architectures, such as CDX-Net [18],

FEDformer [45], and TimeMixer++ [32], integrate temporal and

frequency-domain features to enhance the robustness and accu
racy of time series representations. Despite these advances, most

existing models encode time series representations empirically in a

black-box manner, optimized through trial-and-error based on fore
casting outcomes. This limits both interpretability and theoretical

insights into the underlying data structure.

Time series forecasting is further complicated by concept drift

[4, 10, 12, 29], where the statistical properties and patterns of time

series data shift over time. Such dynamics also imply basis evolu
tion in the frequency domain when time series data is decomposed

into frequency components via FFT [13, 14, 23, 44], where new

frequency bases appear and existing ones disappear. Basis evolu
tion complicates frequency-domain analysis, as models built on

static basis assumptions cannot readily maintain stable and accu
rate representations. Consequently, models trained on historical

data become less effective for future predictions under concept drift

and basis evolution. However, current state-of-the-art forecasting

models either overlook these phenomena or address them only

implicitly, leaving a void in interpretable and robust solutions.

We propose FIRE, a novel unified frequency domain decomposi
tion framework for interpretable and robust time series forecasting.

1

arXiv:2510.10145v1  [cs.LG]  11 Oct 2025


!!! page 2 "He_2025_FIRE"

Conference’17, July 2017, Washington, DC, USA

Cheng He, Xijie Liang, Zengrong Zheng, Patrick P.C. Lee, Xu Huang, Zhaoyi Li, Hong Xie, Defu Lian, and Enhong Chen

It provides a consistent mathematical abstraction for diverse time se
ries data under concept drift and basis evolution, thereby enabling

interpretable frequency-domain representations. It incorporates

several key features: (i) modeling amplitude and phase components

independently to capture underlying temporal dynamics in con
cept drift, (ii) learning adaptively the weights of frequency basis

components across data patches to track the evolving importance

of frequency bases, (iii) a targeted loss function that explicitly ac
counts for basis evolution, and (iv) a novel training paradigm that

integrates Huber loss with a hybrid strong and weak convergence

framework to accelerate training and improve generalization, par
ticularly when large-scale, high-quality open datasets are limited.

Our main contributions are summarized as follows:

• We propose FIRE, a unified frequency domain decomposition

framework that provides analytical modeling for diverse types of

time series. FIRE incorporates several key techniques to achieve

interpretability and robustness for time series forecasting.

• Extensive experiments demonstrate that FIRE consistently out
performs state-of-the-art baselines across various long-term fore
casting tasks, delivering cost-effective and interpretable solutions

suitable for industrial applications.

2

Preliminaries

We introduce the analytical formulation of time series data, key

concepts of concept drift and basis evolution, and the notations and

metrics used in this paper.

2.1

Analytical Formulation of Time Series Data

In mathematics and engineering, complex data can be represented

as an infinite series of basis vectors. The Fourier series, a widely

used set of basis vectors, effectively represents time series data

that satisfy specific conditions. Specifically, if a time series 𝑥(𝑡) is a

periodic signal with period 𝑇and satisfies the Dirichlet conditions

(i.e., absolutely integrable over one period, with a finite number of

discontinuities of the first kind and extrema), then the signal can

be accurately represented by a Fourier series.

We define 𝑋[𝑘] as a discrete Fourier transform (DFT) of 𝑥(𝑛) as:

𝑋[𝑘] =

𝑁−1

∑︁

𝑛=0

𝑥[𝑛] · 𝑒−𝑗2𝜋

𝑁𝑘𝑛,

(1)

where 𝑛is the time index in the temporal domain, 𝑘is the frequency

index in the frequency domain, both ranging from 0 to 𝑁−1, and

𝑗is the imaginary unit satisfying 𝑗2 = −1. Using Euler’s formula,

we can express the exponential term in trigonometric form as:

𝑒−𝑗2𝜋

𝑁𝑘𝑛= cos

 2𝜋

𝑁𝑘𝑛



−𝑗sin

 2𝜋

𝑁𝑘𝑛



(2)

Substituting Equation (2) into Equation (1), we can obtain the

real part 𝑎[𝑘] and the imaginary part 𝑏[𝑘] as:

𝑋[𝑘] =

𝑁−1

∑︁

𝑛=0

𝑥[𝑛] ·



cos

 2𝜋

𝑁𝑘𝑛



−𝑗sin

 2𝜋

𝑁𝑘𝑛



𝑎[𝑘] =

𝑁−1

∑︁

𝑛=0

𝑥[𝑛] · cos

 2𝜋

𝑁𝑘𝑛



𝑏[𝑘] = −

𝑁−1

∑︁

𝑛=0

𝑥[𝑛] · sin

 2𝜋

𝑁𝑘𝑛



𝑋[𝑘] = 𝑎[𝑘] + 𝑗· 𝑏[𝑘]

(3)

We can derive the amplitude 𝐴[𝑘] and phase 𝜙[𝑘] in the fre
quency domain as:

𝐴[𝑘] =

√︁

𝑎[𝑘]2 + 𝑏[𝑘]2

𝜙[𝑘] = arctan

𝑏[𝑘]

𝑎[𝑘]



.

(4)

The inverse DFT reconstructs the time series 𝑥(𝑡) as:

𝑥[𝑛] = 𝑎0 +

𝑁−1

∑︁

𝑘=1

𝛽𝑘𝐴[𝑘] · cos

 2𝜋

𝑁𝑘𝑛−𝜙[𝑘]



,

(5)

where 𝑎0 = 𝐴[0]

𝑁

is the DC component (intercept) corresponding to

𝑘= 0 in the frequency domain, and 𝛽𝑘is the weight of the 𝑘-th basis

component. Although the Fourier series is strictly defined for peri
odic signals, non-periodic signals can be approximated by assuming

the sequence period matches the number of time points. Thus, we

can have a uniform representation for 𝑥(𝑡) from Equation (5).

2.2

Concept Drift in Time Domain

Most machine learning algorithms assume stationary statistical

distributions between training and testing phases. However, in

practical time series applications, the underlying data distribution

often evolves, leading to distinct patterns in future data compared

to historical data. This phenomenon, termed concept drift, refers

to temporal changes in statistical properties [29]. In data stream

mining, methods like ADWIN [3] can be used to detect change

points and identify shifts in data concepts over time.

Definition 1 (Degree of concept drift). Let 𝑁change be the number

of detected change points and 𝑁total be the total number of time

points in a dataset. The degree of concept drift 𝐷drift is defined as:

𝐷drift = 𝑁change

𝑁total

(6)

A higher 𝐷drift indicates more frequent changes in the data dis
tribution, and hence greater concept drift.

2.3

Basis Evolution in Frequency Domain

Concept evolution traditionally refers to the emergence of new

classes or concepts in data streams [23], and can be extended to

changes in the underlying basis functions in frequency-domain

time series analysis. After time series data is transformed into

the frequency domain via FFT, it is segmented into patches,

each represented by a vector of 𝑁basis energies: E(𝑞)

=

 𝐸(𝑞)

1 , 𝐸(𝑞)

2 , . . . , 𝐸(𝑞)

𝑁

,

𝑞= 1, 2, . . . ,𝑄, where 𝐸(𝑞)

𝑘

≥0 is the en
ergy of the 𝑘-th frequency basis in patch 𝑞.

2


!!! page 3 "He_2025_FIRE"

A Unified Frequency Domain Decomposition Framework for Interpretable and Robust Time Series Forecasting

Conference’17, July 2017, Washington, DC, USA

Definition 2 (Basis evolution criterion). For each basis 𝑘, the

relative energy change between two consecutive patches 𝑞−1 and

𝑞is:

𝛿(𝑞)

𝑘

=

|𝐸(𝑞)

𝑘

−𝐸(𝑞−1)

𝑘

|

𝐸(𝑞−1)

𝑘

+ 𝜂

,

(7)

where 𝜂> 0 is a small constant to avoid division by zero. Basis 𝑘is

said to evolve at patch 𝑞if

𝛿(𝑞)

𝑘

> 𝜖,

(8)

where 𝜖> 0 is a fixed threshold.

Definition 3 (Patch-level basis evolution). A patch 𝑞is con
sidered to exhibit basis evolution if the fraction of evolving bases

exceeds a threshold 𝜏∈(0, 1]:

1

𝑁

𝑁−1

∑︁

𝑘=0

1 𝛿(𝑞)

𝑘

> 𝜖 > 𝜏,

(9)

where 1(·) is the indicator function.

Definition 4 (Degree of basis evolution). Let Q𝑒

= {𝑞|

patch 𝑞exhibits basis evolution} be the set of evolving patches.

The degree of basis evolution over 𝑄patches is:

𝐷𝑒𝑣𝑜𝑙𝑢𝑡𝑖𝑜𝑛= |Q𝑒|

𝑄

∈[0, 1].

(10)

Basis evolution reflects the non-stationary nature of time series,

as the frequency components that characterize the data evolve

over time. The non-stationary nature complicates modeling and

prediction in the frequency domain.

2.4

Strong and Weak Convergence

In statistical learning theory [30], convergence in Hilbert spaces is

categorized into strong and weak convergence [17]. Specifically, a

sequence of functions {𝑓ℎ(𝒙)}∞

ℎ=1 is said to converge strongly to a

target function 𝑓(𝒙) if:

lim

ℎ→∞∥𝑓ℎ(𝒙) −𝑓(𝒙)∥= 0,

(11)

where the norm is defined in the corresponding Hilbert space. In

contrast, {𝑓ℎ(𝒙)}∞

ℎ=1 converges weakly to 𝑓(𝒙) if:

lim

ℎ→∞⟨𝜙(𝒙), 𝑓ℎ(𝒙) −𝑓(𝒙)⟩= 0,

∀𝜙(𝒙) ∈𝐿2,

(12)

where ⟨·, ·⟩denotes the inner product in 𝐿2 space.

Strong convergence imposes stricter pointwise stability. It offers

robust theoretical guarantees, but requires large datasets and exten
sive training. In contrast, weak convergence focuses on statistical

behavior across the data distribution and imposes less restrictive re
quirements. It enables faster training and better performance with

sparse data, while maintaining rigorous mathematical foundations.

In this work, we aim to combine strong and weak convergence.

3

FIRE Design

We present FIRE’s design, aiming to address concept drift and basis

evolution.

3.1

Model Architecture

To effectively capture complex temporal dependencies and concept

drift, FIRE primarily operates in the frequency domain. Specifically,

the raw multivariate time series data is first preprocessed and trans
formed into the frequency domain via the Fast Fourier Transform

(FFT), which decomposes the signals into orthogonal sinusoidal

basis functions. This transformation, along with the resulting fre
quency domain representation, reveals rich spectral characteristics

that facilitate the design of specialized modules capable of modeling

intricate correlations and evolving patterns in the data, while adap
tively handling basis evolution. FIRE is composed of three main

components, illustrated in Figure 1:

• Embedding and transformation: This module applies Chan
nel Independent (CI) processing and Instance Normalization

(IN) to the raw input data. The normalized data is segmented

into patches and converted into the frequency domain via FFT.

These frequency-domain patches are then embedded into a high
dimensional feature space through a dedicated embedding layer,

enabling effective feature extraction.

• Frequency domain backbone: Operating on complex-valued

frequency patches, this backbone employs complex linear layers

to capture intra-patch correlations. It explicitly models amplitude

and phase components to handle concept drift, while an attention

mechanism adaptively learns weights for the sinusoidal basis to

address basis evolution. The processed features are recombined

into complex representations for subsequent processing.

• Output projection module: This module generates frequency
domain predictions by flattening and applying a linear projec
tion. The predicted signals are then transformed back to the

time domain through inverse FFT (iFFT), followed by instance

denormalization to produce the final forecasts.

• Composite loss function: To effectively handle basis evolution

and concept drift, FIRE employs a composite loss combining three

terms: a Huber loss with hybrid convergence that balances strong

and weak convergence for better generalization under sparse and

noisy data; an FFT-domain loss that directly minimizes predic
tion errors in the frequency domain, thus explicitly addressing

basis evolution; and a phase regularization term that enforces

smooth phase transitions to enhance stability and robustness of

the learned representations.

Through the integration of these components within a unified

frequency-domain framework, FIRE effectively captures both global

and local temporal dynamics, enabling interpretable and robust time

series forecasting.

3.2

Embedding and Transformation

Let X = [𝑋𝑐,𝑙: 𝑐∈[𝐶],𝑙∈[𝐿]] denote a multivariate time series in
stance with 𝐶variables and 𝐿timestamps. Each instance is first pro
cessed using Channel Independent (CI) processing and segmented

into overlapping patches following the patching scheme [25]. The

resulting patches are represented as X𝑃∈R𝑁𝑝×𝐿𝑝, where 𝑁𝑝is

the number of patches and 𝐿𝑝is the length of each patch. These

patches are then transformed into the frequency domain via FFT.

Subsequently, a linear embedding layer projects the frequency
domain patches into a higher-dimensional feature space, yielding

3


!!! page 4 "He_2025_FIRE"

Conference’17, July 2017, Washington, DC, USA

Cheng He, Xijie Liang, Zengrong Zheng, Patrick P.C. Lee, Xu Huang, Zhaoyi Li, Hong Xie, Defu Lian, and Enhong Chen

Predicted Output

(e.g., 3 channels)

Linear

Projection

Multivariate Time Series Data

(e.g., 3 channels)

iFFT

Patch Mixing

Concept drift

modeling

Basis evolution

modeling

CI +

Instance Norm

Patching

Embedding

FFT

Linear(A)

Linear(Φ )

Causal

Attention(  )

Complex

Data Reconst

Complex Linear

Embedding &

Transformation

Channel

Patch

FFT

results

Frequency

Domain Backbone

Output

Project

Instance

Denorm

Figure 1: Model architecture of FIRE. It tranforms multivari
ate time series into the frequency domain through a sequence

of steps including CI, IN, patching, and FFT. It captures intra
patch correlations using complex linear layers. It models

concept drift via linear transformations, and basis evolution

via causal attention mechanisms. It finally generates predic
tions by a flattened linear projection layer.

H𝑖∈C𝑁𝑝×𝐷, where 𝐷denotes the embedding dimension:

X𝑃= FFT(Patching(CI(X))),

H𝑖= Wembed · X𝑃.

(13)

Here, H𝑖is a complex-valued tensor capturing rich frequency fea
tures for downstream processing.

3.3

Frequency Domain Backbone

Starting from the embedded frequency-domain input H𝑖∈C𝑁𝑝×𝐷,

FIRE applies a complex-valued linear transformation to model intra
patch correlations:

H𝑃= LinearC(H𝑖) = WC · H𝑖+ bC,

(14)

where WC ∈C𝐷×𝐷and bC ∈C𝐷are learnable complex weights and

biases, and the output H𝑃∈C𝑁𝑝×𝐷retains the same dimensions as

the input.

This complex linear transformation effectively models the local
ized frequency interactions within each patch, enabling the network

to extract rich amplitude and phase information that is crucial for

representing temporal dynamics. Such frequency-domain repre
sentations naturally facilitate the characterization of concept drift,

as temporal distributional shifts manifest as variations in these

frequency components.

0

5

10

15

Frequency index

0

2

4

log10(amplitude)

Patch 1

Patch 2

(a) Amplitude variation between consecu
tive frequency patches

0

5

10

15

Frequency Index

-π

-π/2

0

π/2

π

Phase (rad)

Patch 1

Patch 2

(b) Phase variation between consecutive

frequency patches

Figure 2: Variations in amplitude and phase distributions

between consecutive frequency patches in the frequency

domain. The patches are sampled from the Weather and

Etth1 datasets, respectively.

Learning of concept drift. Concept drift refers to temporal dis
tributional shifts, which can be equivalently characterized in the

frequency domain as variations in amplitude and phase distribu
tions across localized frequency patches (Figure 2).

Lemma 3.1 (Equivalence of Concept Drift Modeling in Tempo
ral and Frequency Domains). A non-stationary time series with

time-varying distribution exhibits concept drift. Under linear time
invariant signal decomposition, modeling distributional shifts in the

temporal domain is equivalent to modeling independent changes

in amplitude and phase in the frequency domain.

Proof. Any time series can be decomposed into frequency com
ponents via the Fourier transform (see Section 2, Equation (5)).

Since the discrete Fourier transform (DFT) is a linear, invertible

mapping—and the fast Fourier transform (FFT) provides an efficient

way to compute it—it preserves all information contained in the

original time series. Consequently, any temporal changes in the

series, such as shifts in mean, variance, or other distributional prop
erties, manifest as corresponding changes in the amplitude and

phase of the frequency components. This one-to-one correspon
dence guarantees that modeling concept drift in the time domain is

fully equivalent to modeling it in the frequency domain, without

any loss of information.

□

Based on the complex linear transformation output H𝑃, we ex
tract amplitude A ∈R𝑁𝑝×𝐷and phase 𝝓∈[−𝜋, 𝜋]𝑁𝑝×𝐷compo
nents. To effectively capture concept drift, FIRE models amplitude

and phase variations across patches independently. Specifically, it

employs two separate linear layers to learn the inter-patch correla
tions for amplitude and phase:

ˆA = Linear𝐴𝑚𝑝(A) = W𝐴𝑚𝑝A + b𝐴𝑚𝑝,

ˆ𝝓= Linear𝜙(𝝓) = W𝜙𝝓+ b𝜙,

(15)

where W𝐴𝑚𝑝, W𝜙∈R𝐷×𝐷and b𝐴𝑚𝑝, b𝜙∈R𝐷are learnable param
eters. This disentangled design enables interpretable and effective

adaptation to non-stationary time series by separately modeling

amplitude and phase drift dynamics.

Learning of basis evolution. While linear layers effectively cap
ture concept drift through amplitude and phase variations, their

capacity to model the more complex, non-linear temporal dynam
ics of frequency basis evolution is limited. In particular, traditional

frequency-domain models relying solely on linear transformations

struggle to adapt to abrupt changes or long-range dependencies in

4


!!! page 5 "He_2025_FIRE"

A Unified Frequency Domain Decomposition Framework for Interpretable and Robust Time Series Forecasting

Conference’17, July 2017, Washington, DC, USA

the spectral bases. In contrast, causal attention provides a flexible

mechanism to dynamically weight and integrate historical ampli
tude features, making it better suited to handle sudden shifts and

intricate basis evolution patterns.

FIRE leverages a causal masked attention mechanism applied

directly on the previous outputed amplitude representations ˆA ∈

R𝑁𝑝×𝐷obtained from the amplitude linear layer (Equation (15)).

This sequence of amplitude embeddings compactly represents the

frequency bases across patches 𝑝= 1, . . . , 𝑁𝑝. The causal attention

offers three key advantages over linear layers:

• Adaptive temporal weighting: It dynamically learns to weigh

historical amplitude features, focusing on the most relevant past

patches for the current basis evolution.

• Modeling long-range dependencies: Self-attention naturally

captures complex dependencies across distant patches, essential

for representing gradual or abrupt spectral changes.

• Preserving causality: The causal mask ensures that the ba
sis at patch 𝑝depends only on current and past patches ≤𝑝,

maintaining temporal consistency required for forecasting.

Formally, the amplitude features are projected into queries and

keys:

Q = ˆAW𝑄,

K = ˆAW𝐾,

(16)

where W𝑄, W𝐾∈R𝐷×𝑑are learnable parameters, and 𝑑is the

attention dimension.

The scaled dot-product attention scores are masked causally by

M ∈{0, −∞}𝑁𝑝×𝑁𝑝:

M𝑝,𝑞=

(

0,

𝑞≤𝑝

−∞,

𝑞> 𝑝,

where 𝑞≤𝑝indicates that attention at patch 𝑝is computed only

over patch 𝑝and all preceding patches 𝑞, ensuring causality by

excluding future patches. The attention weights W ∈R𝑁𝑝×𝑁𝑝are

computed as

W = softmax

 QK⊤

√

𝑑

+ M



.

(17)

To further refine intra-patch importance, amplitude vector ˆA is

projected by a learnable linear layer:

V = W𝑝ˆA + b𝑝,

(18)

where V ∈R𝑁𝑝×𝐷, W𝑝∈R𝐷×𝐷and b𝑝∈R𝐷. The final dynamic

weights U modulating the frequency bases are obtained by combin
ing inter-patch attention and intra-patch projections:

U = WV,

(19)

with U ∈R𝑁𝑝×𝐷. These adaptive weights U are applied element
wise to the original frequency bases B, producing the dynamically

evolved bases:

H𝑜= U ⊙B,

(20)

where H𝑜∈C𝑁𝑝×𝐷, ⊙denotes element-wise multiplication.

This causal attention-based design enables FIRE to flexibly and

effectively capture complex, non-linear, and temporally adaptive

basis evolution patterns, surpassing the representational limitations

of traditional linear layers.

3.4

Output Projection

After backbone processing, FIRE flattens the output H𝑜and passes

it through a linear projection layer to produce predictions in the

frequency domain. These are then transformed back to the time

domain using iFFT, followed by instance denormalization, to yield

the final forecasts:

X𝑜𝑢𝑡= Denorm(iFFT(WLinProj · Flatten(H𝑜)))

(21)

where Xout ∈R𝐿𝑝𝑟𝑒𝑑×𝐶, with 𝐿𝑝𝑟𝑒𝑑denoting the prediction length.

3.5

Loss Function

After the output projection module, we need to quantify the loss

between X𝑜𝑢𝑡and the ground truth X𝑡𝑟𝑢𝑒. FIRE employs a composite

loss comprising the Huber loss with hybrid convergence (L𝑤ℎ), FFT

loss (Lfft), and phase regularization (R𝜙). This loss also explicitly

guides the model to address concept drift and basis evolution in the

frequency domain, thereby providing a clear objective for parameter

optimization:

L = L𝑤ℎ+ Lfft + R𝜙.

(22)

The individual components are detailed as follows.

Huber loss with hybrid convergence. To balance strong and

weak convergence and improve generalization under sparse data

(Section 2), FIRE adopts Huber loss [15], which smoothly interpo
lates between ℓ2 and ℓ1 losses:

L𝛿(X𝑡𝑟𝑢𝑒, X𝑜𝑢𝑡) =

1

𝐿𝑝𝑟𝑒𝑑

𝐿𝑝𝑟𝑒𝑑

∑︁

𝑙=1

𝛿2

√︂

1 +

𝑥𝑡𝑟𝑢𝑒−𝑥𝑜𝑢𝑡

𝛿

2

−1

!

(23)

where 𝛿is a hyperparameter controlling the transition threshold.

To incorporate weak convergence (Equation (12)), the Huber loss

is weighted by a matrix W ∈R1×𝐵(with batch size 𝐵) that linearly

combines identity and predicate-based components:

L𝑤ℎ=

𝐵

∑︁

𝑏=1

W · L𝛿(𝑥𝑡𝑟𝑢𝑒,𝑥𝑜𝑢𝑡),

W = ˆ𝜏I + 𝜏P,

(24)

where 𝜏= 1 −ˆ𝜏balances strong and weak convergence, I is the

identity matrix, and P is the empirical covariance matrix of predi
cates:

P = 1

𝑚

𝑚

∑︁

𝑠=1

𝜓𝑠𝜓⊤

𝑠.

(25)

where 𝑚is the number of predicates. For simplicity, we use a single

predicate𝜓(𝒙) = 1 in this work. This formulation leverages statisti
cal invariants captured by weak convergence to enhance robustness

and generalization, particularly in noisy or sparse scenarios.

FFT loss. The FFT loss, Lfft, is defined as the mean absolute error

(MAE) between the predicted and ground truth sequences in the

frequency domain:

Lfft = 1

𝑁𝑓

𝑁𝑓

∑︁

𝑘=1

|FFT(X𝑡𝑟𝑢𝑒) −FFT(X𝑜𝑢𝑡)|

(26)

where 𝑁𝑓is the number of bases of the predicted sequence in the

frequency domain. This loss explicitly addresses basis evolution by

minimizing discrepancies in frequency basis vectors.

Phase regularization. To ensure smooth and stable phase tran
sitions, FIRE introduces phase regularization to constrain phase

5


!!! page 6 "He_2025_FIRE"

Conference’17, July 2017, Washington, DC, USA

Cheng He, Xijie Liang, Zengrong Zheng, Patrick P.C. Lee, Xu Huang, Zhaoyi Li, Hong Xie, Defu Lian, and Enhong Chen

changes in the predicted sequence. It formulates a first-order differ
ence penalty:

R𝜙= 𝜆

1

𝐷−1

𝐷−1

∑︁

𝑑=1



𝜙𝑑+1

𝑜𝑢𝑡−𝜙𝑑

𝑜𝑢𝑡

2

,

(27)

where 𝜆is a weighting factor, 𝐷is the model dimensionality, and

𝜙𝑑

out denotes the phase feature of the 𝑑-th dimension. This enhances

model robustness and generalizability.

3.6

Discussion

Time series forecasting in the time domain is challenging due to

complex patterns and limited information. Instead, FIRE first trans
forms the data into the frequency domain via FFT, which decom
poses the signal into multiple frequency basis components. We

choose FFT over other basis decomposition methods because it is

reversible and parameter-free, requiring no hyperparameter tuning

or prior knowledge, thus making it broadly applicable to various

time series (see Appendix A for details).

Traditional methods typically model the real and imaginary parts

of the transformed signal. However, these lack clear physical in
terpretation and make it hard to hard to connect the results back

to the original data. In contrast, FIRE converts each complex com
ponent into amplitude (indicating the strength or energy of each

basis) and phase (indicating the timing), modeling them separately

(Equation (4)). This decomposition enables the model to capture dis
tinct physical features and concept drift patterns while maintaining

a direct link to the original signal. To better capture the tempo
ral evolution of frequency bases, we introduce a causal attention

mechanism that adaptively learns how basis components change

and interact across patches (Equations (16)–(20)). After forecasting

in the frequency domain, the model converts the results back to

the time domain. Finally, a composite loss function (Equation (22))

is employed, measuring loss in both time (Equation (12)) and fre
quency domains (Equation (26)), while constraining phase shifts

(Equation (27)) to ensure smooth and robust predictions.

In summary, FIRE succeeds by extracting more interpretable and

physically meaningful features, explicitly modeling their dynamics

and interactions, and optimizing with mathematically and physi
cally grounded objectives. This design makes FIRE robust, adaptive,

and accurate across diverse real-world forecasting tasks.

4

Experiments

We extensively evaluate the performance of FIRE across a variety of

long-term forecasting tasks. We compare FIRE against state-of-the
art baselines, particularly those that emphasize frequency-domain

modeling of time series data. We also perform comprehensive ab
lation studies, hyperparameter sensitivity analyses, and targeted

experiments on handling concept drift and basis evolution.

4.1

Datasets and Baselines

We conduct experiments on seven widely used public time series

forecasting datasets [36] (see Table 1), including the Electricity

Transformer Temperature datasets at both hourly and minute-level

granularities (ETTh1, ETTh2, ETTm1, ETTm2), as well as Weather,

Traffic, and Electricity Power Consumption (ELC).

Table 1: Statistics of datasets

Dataset

Length

Dimension

Frequency

ETTh

17420

7

1 hour

ETTm

69680

7

15 min

Weather

52696

21

10 min

Electricity

26304

321

1 hour

Traffic

17544

862

1 hour

We select representative baselines for comparison. We repro
duce the results of two frequency-based models, FredFormer [27]

and WPMixer [24]. For other baselines, including TimeMixer [33],

iTransformer [21], PatchTST [25], and TimesNet [35], we report

the results as published in their respective papers.

4.2

Experimental Settings

We choose a look-back window of 96 and forecast future time points

𝑇∈{96, 192, 336, 720}. We use the mean squared error (MSE) and

mean absolute error (MAE) as the evaluation metrics and compare

the results with the best-performing results of SOTA models pre
sented in papers or reproduced from their published source codes.

We implement FIRE in PyTorch [26] and train it on a single NVIDIA

A100 40GB GPU.

4.3

Forecasting Results

Table 2 summarizes the full forecasting results, with the best perfor
mance highlighted in bold. The results show that FIRE consistently

outperforms all competitors, achieving the best results in 21 out

of 35 tasks based on MSE and 26 out of 35 based on MAE. On

average, FIRE improves MSE by 3%-8% compared to the second
best model, WPMixer, and by 20%-30% compared to the worst
performing model, TimesNet, with the largest gains observed in

certain datasets such as ETTh1 and Traffic. Similarly, for MAE,

FIRE’s relative improvements are 2%-7% over WPMixer and 15%
25% over TimesNet across various tasks. Our results demonstrate

FIRE ’s robustness and superior ability to capture complex temporal

dynamics for long-term forecasting.

4.4

Ablation Results

To comprehensively assess the effectiveness of our module design,

we report the average forecasting results across seven datasets in Ta
ble 3. Our full model, FIRE, achieves the best average MSE on 5 out

of 7 datasets and the best average MAE on 6 out of 7 datasets, con
sistently outperforming the two variants: FIRE _advanced, which

removes the basis evolution module, and FIRE _base, which sim
plifies concept drift modeling. These quantitative improvements

highlight the importance of jointly modeling both data drift and

basis evolution to capture complex temporal dynamics for accu
rate forecasting. We provide the full detailed forecasting results

in Appendix (Section B.2), which further verify that FIRE attains

superior performance in the majority of individual experiments,

demonstrating its robustness and effectiveness.

We conduct an ablation study by progressively removing compo
nents of the loss function to evaluate their individual contributions.

Specifically, FIRE _enhanced removes the phase regulation term R𝜙;

6


!!! page 7 "He_2025_FIRE"

A Unified Frequency Domain Decomposition Framework for Interpretable and Robust Time Series Forecasting

Conference’17, July 2017, Washington, DC, USA

Table 2: Long-term forecasting results for prediction lengths 𝑇∈{96, 192, 336, 720}. Best results are highlighted in bold.

Model

FIRE

Fredformer

WPMixer

TimeMixer

iTransformer

PatchTST

TimesNet

Dataset

T

MSE

MAE

MSE

MAE

MSE

MAE

MSE

MAE

MSE

MAE

MSE

MAE

MSE

MAE

96

0.365

0.390

0.373

0.392

0.375

0.393

0.375

0.400

0.386

0.405

0.460

0.447

0.384

0.402

192

0.420

0.418

0.433

0.420

0.428

0.417

0.429

0.421

0.441

0.436

0.512

0.477

0.436

0.429

ETTh1

336

0.458

0.437

0.470

0.437

0.477

0.439

0.484

0.458

0.487

0.458

0.546

0.496

0.638

0.469

720

0.456

0.454

0.467

0.456

0.460

0.454

0.498

0.482

0.503

0.491

0.544

0.517

0.521

0.500

Avg.

0.425

0.425

0.436

0.426

0.435

0.426

0.447

0.440

0.454

0.447

0.516

0.484

0.495

0.450

96

0.282

0.333

0.293

0.342

0.283

0.335

0.289

0.341

0.297

0.349

0.308

0.355

0.340

0.374

192

0.362

0.383

0.371

0.389

0.364

0.391

0.372

0.392

0.380

0.400

0.393

0.405

0.402

0.414

ETTh2

336

0.403

0.419

0.382

0.409

0.409

0.424

0.386

0.414

0.428

0.432

0.427

0.436

0.452

0.452

720

0.408

0.433

0.415

0.434

0.429

0.443

0.412

0.434

0.427

0.445

0.436

0.450

0.462

0.468

Avg.

0.364

0.392

0.365

0.394

0.371

0.398

0.364

0.395

0.383

0.407

0.391

0.411

0.414

0.427

96

0.310

0.344

0.326

0.361

0.316

0.352

0.320

0.357

0.334

0.368

0.352

0.374

0.338

0.375

192

0.356

0.375

0.363

0.380

0.362

0.376

0.361

0.381

0.377

0.391

0.390

0.393

0.374

0.387

ETTm1

336

0.385

0.397

0.395

0.403

0.387

0.396

0.390

0.404

0.426

0.420

0.421

0.414

0.410

0.411

720

0.448

0.431

0.453

0.438

0.447

0.432

0.454

0.441

0.491

0.459

0.462

0.449

0.478

0.450

Avg.

0.375

0.387

0.384

0.396

0.378

0.389

0.381

0.395

0.407

0.410

0.406

0.407

0.400

0.406

96

0.170

0.252

0.177

0.259

0.171

0.252

0.175

0.258

0.180

0.264

0.183

0.270

0.187

0.267

192

0.237

0.297

0.243

0.301

0.233

0.294

0.237

0.299

0.250

0.309

0.255

0.314

0.249

0.309

ETTm2

336

0.299

0.338

0.302

0.340

0.290

0.333

0.298

0.340

0.311

0.348

0.309

0.347

0.321

0.351

720

0.399

0.395

0.397

0.396

0.387

0.390

0.391

0.396

0.412

0.407

0.412

0.404

0.408

0.403

Avg.

0.276

0.321

0.280

0.324

0.270

0.317

0.275

0.323

0.288

0.332

0.290

0.334

0.291

0.333

96

0.162

0.204

0.163

0.207

0.162

0.204

0.163

0.209

0.174

0.214

0.186

0.227

0.172

0.220

192

0.207

0.246

0.211

0.251

0.209

0.246

0.208

0.250

0.221

0.254

0.234

0.265

0.219

0.261

Weather

336

0.263

0.287

0.267

0.292

0.263

0.287

0.251

0.287

0.278

0.296

0.284

0.301

0.246

0.337

720

0.340

0.338

0.343

0.341

0.340

0.339

0.339

0.341

0.358

0.347

0.356

0.349

0.365

0.359

Avg.

0.243

0.269

0.246

0.273

0.244

0.269

0.240

0.271

0.258

0.278

0.265

0.285

0.251

0.294

96

0.474

0.272

0.406

0.277

0.465

0.286

0.462

0.285

0.395

0.268

0.526

0.347

0.593

0.321

192

0.487

0.269

0.426

0.290

0.475

0.290

0.473

0.296

0.417

0.276

0.522

0.332

0.617

0.336

Traffic

336

0.484

0.275

0.432

0.281

0.489

0.296

0.498

0.296

0.433

0.283

0.517

0.334

0.629

0.336

720

0.531

0.295

0.463

0.300

0.527

0.318

0.506

0.313

0.467

0.302

0.552

0.352

0.64

0.35

Avg.

0.494

0.278

0.432

0.287

0.489

0.298

0.484

0.297

0.428

0.282

0.529

0.341

0.62

0.336

96

0.148

0.236

0.147

0.241

0.150

0.241

0.153

0.247

0.148

0.240

0.190

0.296

0.168

0.272

192

0.161

0.249

0.165

0.258

0.162

0.252

0.166

0.256

0.162

0.253

0.199

0.304

0.184

0.322

Elc

336

0.176

0.265

0.177

0.273

0.179

0.270

0.185

0.277

0.178

0.269

0.217

0.319

0.198

0.300

720

0.215

0.299

0.213

0.304

0.217

0.304

0.225

0.310

0.225

0.317

0.258

0.352

0.220

0.320

Avg.

0.175

0.262

0.176

0.269

0.177

0.267

0.182

0.272

0.178

0.270

0.216

0.318

0.193

0.304

Best_count

21/35

26/35

8

1

6

9

0

0

0

0

0

0

0

0

Table 3: Average results of module ablation

Model

FIRE

FIRE _adv.

FIRE _base

Dataset

MSE

MAE

MSE

MAE

MSE

MAE

ETTh1

0.425

0.425

0.431

0.430

0.434

0.427

ETTh2

0.364

0.392

0.362

0.392

0.363

0.393

ETTm1

0.375

0.387

0.375

0.391

0.376

0.390

ETTm2

0.276

0.321

0.277

0.322

0.275

0.320

Weather

0.243

0.269

0.245

0.272

0.246

0.272

Traffic

0.494

0.278

0.495

0.290

0.506

0.308

Elc

0.175

0.262

0.178

0.264

0.189

0.273

Best_Count

5/7

6/7

1/7

0/7

1/7

1/7

FIRE _advanced further removes the FFT loss L𝑓𝑒𝑞based on FIRE

_base; and FIRE _base discards all specialized loss designs, relying

solely on the Huber loss. Table 4 presents the average forecasting

results. While the full model FIRE shows slightly better average

MSE and MAE compared to FIRE _enhanced, the full detailed re
sults (see Appendix B.2) reveal that FIRE consistently outperforms

all variants on a larger number of individual experiments. This

indicates that although the average improvements appear modest,

the full model demonstrates more substantial and consistent ad
vantages in specific cases, highlighting the importance of each loss

component for robust forecasting performance.

Table 4: Average results of loss ablation

Model

FIRE

FIRE _enh.

FIRE _adv.

FIRE _base

D ataset

MSE

MAE

MSE

MAE

MSE

MAE

MSE

MAE

ETTh1

0.424 0.424 0.428

0.427

0.439

0.437

0.433

0.433

ETTh2

0.363 0.392

0.363 0.391

0.385

0.406

0.367

0.394

ETTm1

0.374 0.386 0.374 0.387

0.384

0.401

0.378

0.395

ETTm2

0.276 0.320

0.277 0.319

0.296

0.343

0.282

0.327

Weather 0.243 0.268

0.243 0.267 0.2448 0.2710 0.2450 0.2705

Traffic

0.494 0.277 0.487 0.286

0.509

0.287

0.510

0.290

Elc

0.175 0.262 0.174 0.262

0.180

0.270

0.181

0.270

Best

4/7

4/7

3/7

3/7

0

0

0

0

4.5

Concept Drift and Basis Evolution

We quantify the degree of concept drift using ADWIN (Section 2.2)

and the degree of basis evolution (Section 2.3). To evaluate the

impact of these phenomena on model performance, we select two

representative univariate time series: Weather_d11 (dimension 11)

and Traffic_d738 (dimension 738). Weather_d11 exhibits a concept

drift degree of 3.07% and a basis evolution degree of 8.39%, whereas

Traffic_d738 shows substantially lower degrees of 0.26% and 1.19%,

respectively. We apply FIRE to these datasets and compare its fore
casting accuracy against three SOTA frequency-domain models:

FredFormer, WPMixer, and FITS. As shown in Table 5, FIRE con
sistently outperforms these baselines, especially on Weather_d11

where data drift and basis evolution are more pronounced. Specif
ically, on Weather_d11, FIRE achieves an average MSE reduction

7


!!! page 8 "He_2025_FIRE"

Conference’17, July 2017, Washington, DC, USA

Cheng He, Xijie Liang, Zengrong Zheng, Patrick P.C. Lee, Xu Huang, Zhaoyi Li, Hong Xie, Defu Lian, and Enhong Chen

Table 5: Effectiveness of concept drift and basis evolution.

Model

FIRE

FredFormer

Wpmixer

FITS

Dataset

T

MSE

MAE

MSE MAE MSE

MAE

MSE MAE

96

0.110 0.237 0.131 0.260 0.111 0.239 0.127 0.257

192

0.185 0.312 0.203 0.326 0.193 0.317 0.200 0.322

Weather-d11

336

0.302 0.395 0.321 0.405 0.305 0.395 0.317 0.401

720

0.462 0.497 0.481 0.503 0.469 0.496 0.478 0.501

Avg. 0.264 0.360 0.284 0.373 0.269 0.362 0.280 0.370

96

1.854 0.687 1.882 0.742 1.871 0.690 1.921 0.741

192

1.898 0.687 1.969 0.746 1.918 0.679 1.951 0.729

Traffic-d738

336

1.809 0.665 1.879 0.720 1.815 0.645 1.846 0.705

720

1.698 0.639 1.732 0.672 1.742 0.646 1.711 0.691

Avg. 1.814 0.669 1.865 0.720 1.836 0.665 1.857 0.716

of 7.0% compared to FredFormer, 17.5% compared to WPMixer,

and 12.9% compared to FITS. In terms of MAE, FIRE improves by

about 3.5%, 7.7%, and 5.5% over FredFormer, WPMixer, and FITS,

respectively. On the more stable Traffic_d738 dataset, FIRE obtains

the best average MSE (1.814), improving by 2.3%, 1.2%, and 2.1%

over FredFormer, WPMixer, and FITS, respectively. Regarding MAE,

FIRE outperforms FredFormer and FITS by 7.1% and 6.5%, respec
tively, while WPMixer achieves a slightly better MAE (0.665) than

FIRE (0.669) by about 0.6%. These results demonstrate FIRE’s supe
rior adaptability and robustness in handling dynamic time series

forecasting scenarios.

4.6

Scalability Analysis

To investigate the scalability of FIRE, we train the model with in
creasing size from both the depth (number of layers) and width (em
bedding dimension) perspectives. Forecasting experiments are con
ducted on two datasets: Weather and Electricity. Figure 3 presents

the average forecasting results, measured by Mean Squared Error

(MSE), on both datasets for various forecasting horizons, including

𝑇∈{96, 192, 336, 720} time steps, using different numbers of layers

and embedding dimensions.

The results demonstrate that, unlike time series foundation mod
els [6, 11, 22, 34, 42], time series forecasting models are typically

trained on domain-specific datasets with limited data volume. As

shown in Figure 3, increasing model capacity—either by enlarging

the hidden dimension or stacking more layers—yields diminishing

returns after a certain point. Specifically, both the model dimension

and layer analysis plots indicate that MSE saturates as the model

size increases, and may even slightly worsen due to overfitting. This

phenomenon suggests that, for time series forecasting tasks with

constrained data, the scalability of models is fundamentally limited.

Once the model capacity matches the representational needs of the

data, further scaling does not improve performance. This is in sharp

contrast to Foundation Models, where scaling up with abundant

data often leads to continuous performance gains.

4.7

Hyper-parameter Analysis

Patch length is a crucial hyper-parameter for FIRE. We eval
uate the model’s sensitivity to different patch lengths on the

Weather and Electricity datasets, forecasting future time points

𝑇∈{96, 192, 336, 720}. Table 6 reports the forecasting results mea
sured by MSE and MAE. For the Weather dataset, the best overall

performance is achieved with a patch length of 16, yielding an aver
32

64

128

256

Dimension

0.20

0.23

0.25

0.28

MSE

Weather

Electricity

(a) Model dimension analysis

1

3

6

9

Num_layers

0.18

0.20

0.22

0.24

0.26

MSE

Weather

Electricity

(b) Model layer analysis

Figure 3: Model scalability analysis

Table 6: Forecasting results of various patch lengths

Patch Len

4

8

16

32

48

Dataset

T

MSE

MAE

MSE

MAE

MSE

MAE

MSE

MAE

MSE

MAE

96

0.163

0.205

0.163

0.204

0.162

0.203

0.163

0.202

0.163

0.204

192

0.210

0.248

0.210

0.249

0.208

0.246

0.209

0.249

0.209

0.246

Weather

336

0.266

0.288

0.267

0.290

0.266

0.290

0.268

0.289

0.268

0.292

720

0.343

0.342

0.343

0.340

0.342

0.339

0.346

0.342

0.344

0.341

Avg.

0.246

0.271

0.246

0.271

0.245

0.270

0.247

0.271

0.246

0.271

96

0.154

0.243

0.152

0.240

0.149

0.237

0.149

0.236

0.148

0.235

192

0.165

0.253

0.163

0.250

0.162

0.249

0.161

0.249

0.161

0.248

Elc

336

0.180

0.270

0.177

0.267

0.177

0.267

0.176

0.265

0.178

0.268

720

0.223

0.306

0.217

0.301

0.214

0.298

0.213

0.298

0.216

0.299

Avg.

0.181

0.268

0.177

0.265

0.176

0.263

0.175

0.262

0.176

0.263

age MSE of 0.245 and MAE of 0.270. For the Electricity dataset, the

optimal patch length is 32, with an average MSE of 0.175 and MAE

of 0.262. Notably, the differences in performance across various

patch lengths are marginal. For instance, on Weather, the worst

average MSE (0.246 at patch length 4) is only 0.001 higher than

the best (0.245 at patch length 16). Similarly, on Electricity, the

average MSE varies within 0.006 across all tested patch lengths.

This demonstrates that FIRE exhibits strong robustness and low

sensitivity to patch length selection, consistent with the scalability

analysis discussed earlier.

5

Related Work

Time series forecasting and temporal models. Time series fore
casting presents unique challenges, especially in modeling long
term dependencies and complex temporal dynamics. Transformer
based architectures [31] have recently advanced the field by leverag
ing self-attention to capture global temporal relationships, outper
forming traditional RNNs and CNNs [2, 5, 9, 16] that often struggle

with scalability and long-range modeling. Notable advancements

include Informer [43], which introduces ProbSparse attention for

efficient handling of long sequences, and Autoformer [36], which

decomposes time series into trend and seasonal components to

improve interpretability and forecasting accuracy. PatchTST [25]

restructures input sequences into patches for parallel processing

in long-term prediction. Pyraformer [20] and TimesNet [35] ex
plore hierarchical and multi-scale representations to further refine

temporal modeling.

Frequency-domain approaches. Despite various advancements,

time-domain models still fall short in capturing periodicity and spec
tral patterns inherent in many real-world time series. Frequency
domain approaches fill this void by leveraging Fourier and wavelet

transforms to extract global and periodic features. Fredformer [27]

employs frequency channel-wise attention to selectively focus on

informative spectral components, while FreTS [41] models depen
dencies across frequency channels and temporal dimensions using

MLPs. FITS [38] employs complex-valued layers for expressive

8


!!! page 9 "He_2025_FIRE"

A Unified Frequency Domain Decomposition Framework for Interpretable and Robust Time Series Forecasting

Conference’17, July 2017, Washington, DC, USA

frequency-domain transformations, and WPMixer [24] integrates

wavelet decomposition with MLPs to capture both localized and

long-term patterns. These models have demonstrated competitive

or superior performance compared to purely temporal approaches.

Hybrid temporal-frequency models. Recent studies have ex
plored hybrid approaches that combine temporal and frequency
domain information. CDX-Net [18] integrates CNNs, RNNs, and

attention mechanisms to extract and fuse multivariate features

from both domains. FEDformer [45] unifies trend-seasonal de
composition with Fourier analysis within a Transformer frame
work, enabling robust representation of multivariate time series.

TimeMixer++ [32] generates multi-scale series via temporal down
sampling, applies FFT-based periodic analysis, and employs atten
tion mechanisms to learn robust representations of seasonal and

trend components.

Limitations of existing approaches. Most frequency-domain

and hybrid models, however, operate as black-box predictors, op
timized primarily for accuracy with limited interpretability. Also,

they rarely address practical challenges, such as concept drift and

basis evolution, which undermine their robustness in dynamic en
vironments where distributional shifts are common.

6

Conclusion

We use the discrete Fourier transform to unify the formulation of

various types of time series. We propose FIRE, a new forecasting

framework that works in the frequency domain through basis de
composition. This allows FIRE to capture richer, multi-dimensional

features of temporal data. A key strength of FIRE is its explicit

and separate modeling of amplitude and phase for handling key

challenges in time series forecasting, namely concept drift and basis

evolution. FIRE combines rigorous mathematical ideas with practi
cal components, including linear transformations, causal attention,

and a composite loss function, so as to adapt dynamically and ro
bustly to changing temporal patterns, even when data are noisy

or sparse. Our experiments on diverse real-world datasets show

that FIRE consistently achieves better accuracy, improved inter
pretability, and strong robustness. It performs especially well under

severe concept drift and basis evolution, proving its effectiveness

in dynamic scenarios.

For future work, we plan to strengthen the integration of mathe
matical theory with an interpretable model design for time series

forecasting, move beyond trial-and-error methods, and develop

more principled and transparent forecasting techniques, so as to

tackle increasingly complex temporal data.

References

[1] Konstandinos Aiwansedo, Jérôme Bosche, Wafa Badreddine, Mohamed Hamza

Kermia, and Oussama Djadane. 2024. CNN-N-BEATS: Novel Hybrid Model

for Time-Series Forecasting. In Deep Learning Theory and Applications - 5th

International Conference, DeLTA 2024, Dijon, France, July 10-11, 2024, Proceedings,

Part I (Communications in Computer and Information Science, Vol. 2171), Ana

Fred, Allel Hadjali, Oleg Gusikhin, and Carlo Sansone (Eds.). Springer, 38–57.

doi:10.1007/978-3-031-66694-0_3

[2] Shaojie Bai, J. Zico Kolter, and Vladlen Koltun. 2018. An Empirical Evaluation of

Generic Convolutional and Recurrent Networks for Sequence Modeling. CoRR

abs/1803.01271 (2018). arXiv:1803.01271

[3] Albert Bifet and Ricard Gavaldà. 2007. Learning from Time-Changing Data with

Adaptive Windowing. In Proceedings of the Seventh SIAM International Conference

on Data Mining, April 26-28, 2007, Minneapolis, Minnesota, USA. SIAM, 443–448.

doi:10.1137/1.9781611972771.42

[4] Dihia Boulegane, Vitor Cerquiera, and Albert Bifet. 2022. Adaptive Model Com
pression of Ensembles for Evolving Data Streams Forecasting. In 2022 Interna
tional Joint Conference on Neural Networks (IJCNN). 1–8. doi:10.1109/IJCNN55064.

2022.9892811

[5] Jiezhu Cheng, Kaizhu Huang, and Zibin Zheng. 2020. Towards Better Forecasting

by Fusing Near and Distant Future Visions. In The Thirty-Fourth AAAI Conference

on Artificial Intelligence, AAAI 2020, The Thirty-Second Innovative Applications

of Artificial Intelligence Conference, IAAI 2020, The Tenth AAAI Symposium on

Educational Advances in Artificial Intelligence, EAAI 2020, New York, NY, USA,

February 7-12, 2020. AAAI Press, 3593–3600.

[6] Abhimanyu Das, Weihao Kong, Rajat Sen, and Yichen Zhou. 2024. A decoder
only foundation model for time-series forecasting. In Forty-first International

Conference on Machine Learning, ICML 2024, Vienna, Austria, July 21-27, 2024.

OpenReview.net. https://openreview.net/forum?id=jn2iTJas6h

[7] Wenjie Du, David Côté, and Yan Liu. 2023. SAITS: Self-attention-based imputation

for time series. Expert Syst. Appl. 219 (2023), 119619. doi:10.1016/J.ESWA.2023.

119619

[8] M. Durairaj and B. H. Krishna Mohan. 2022. A convolutional neural network

based approach to financial time series prediction. Neural Comput. Appl. 34, 16

(2022), 13319–13337. doi:10.1007/S00521-022-07143-2

[9] Valentin Flunkert, David Salinas, and Jan Gasthaus. 2017. DeepAR: Probabilistic

Forecasting with Autoregressive Recurrent Networks. CoRR abs/1704.04110

(2017). arXiv:1704.04110

[10] João Gama, Indr˙e Žliobait˙e, Albert Bifet, Mykola Pechenizkiy, and Abdelhamid

Bouchachia. 2014. A survey on concept drift adaptation. ACM computing surveys

(CSUR) 46, 4 (2014), 1–37.

[11] Mononito Goswami, Konrad Szafer, Arjun Choudhry, Yifu Cai, Shuo Li, and Artur

Dubrawski. 2024. MOMENT: A Family of Open Time-series Foundation Models.

In Forty-first International Conference on Machine Learning, ICML 2024, Vienna,

Austria, July 21-27, 2024. OpenReview.net. https://openreview.net/forum?id=

FVvf69a5rx

[12] Nuwan Gunasekara, Bernhard Pfahringer, Heitor Murilo Gomes, Albert Bifet,

and Yun Sing Koh. 2024. Recurrent concept drifts on data streams. International

Joint Conferences on Artificial Intelligence Organization.

[13] Gajendra Singh Gurjar and Sharda Chhabria. 2015. A review on concept evolution

technique on data stream. In 2015 International Conference on Pervasive Computing

(ICPC). 1–3. doi:10.1109/PERVASIVE.2015.7087172

[14] Ahsanul Haque, Latifur Khan, Michael Baron, Bhavani Thuraisingham, and Charu

Aggarwal. 2016. Efficient handling of concept drift and concept evolution over

Stream Data. In 2016 IEEE 32nd International Conference on Data Engineering

(ICDE). 481–492. doi:10.1109/ICDE.2016.7498264

[15] Peter J. Huber. 1981. Robust Statistics. Wiley. doi:10.1002/0471725250

[16] Guokun Lai, Wei-Cheng Chang, Yiming Yang, and Hanxiao Liu. 2018. Mod
eling Long- and Short-Term Temporal Patterns with Deep Neural Networks.

In The 41st International ACM SIGIR Conference on Research & Development in

Information Retrieval, SIGIR 2018, Ann Arbor, MI, USA, July 08-12, 2018, Kevyn

Collins-Thompson, Qiaozhu Mei, Brian D. Davison, Yiqun Liu, and Emine Yilmaz

(Eds.). ACM, 95–104.

[17] Chun-Na Li, Yiwei Song, and Yuan-Hai Shao. 2025. Domain Adaptation via

Learning Using Statistical Invariant. IEEE Trans. Knowl. Data Eng. 37, 7 (2025),

4023–4034. doi:10.1109/TKDE.2025.3565780

[18] Jiajia Li, Ling Dai, Feng Tan, Hui Shen, Zikai Wang, Bin Sheng, and Pengwei

Hu. 2022. CDX-NET: Cross-Domain Multi-Feature Fusion Modeling Via Deep

Neural Networks for Multivariate Time Series Forecasting in AIOps. In IEEE

International Conference on Acoustics, Speech and Signal Processing, ICASSP 2022,

Virtual and Singapore, 23-27 May 2022. IEEE, 4073–4077. doi:10.1109/ICASSP43922.

2022.9746242

[19] Jiajia Li, Feng Tan, Cheng He, Zikai Wang, Haitao Song, Lingfei Wu, and Pengwei

Hu. 2022. HigeNet: A Highly Efficient Modeling for Long Sequence Time Series

Prediction in AIOps. CoRR abs/2211.07642 (2022). arXiv:2211.07642 doi:10.48550/

ARXIV.2211.07642

[20] Shizhan Liu, Hang Yu, Cong Liao, Jianguo Li, Weiyao Lin, Alex X. Liu, and

Schahram Dustdar. 2022. Pyraformer: Low-Complexity Pyramidal Attention for

Long-Range Time Series Modeling and Forecasting. In The Tenth International

Conference on Learning Representations, ICLR 2022, Virtual Event, April 25-29, 2022.

OpenReview.net. https://openreview.net/forum?id=0EXmFzUn5I

[21] Yong Liu, Tengge Hu, Haoran Zhang, Haixu Wu, Shiyu Wang, Lintao Ma, and

Mingsheng Long. 2024. iTransformer: Inverted Transformers Are Effective for

Time Series Forecasting. In The Twelfth International Conference on Learning

Representations, ICLR 2024, Vienna, Austria, May 7-11, 2024. OpenReview.net.

https://openreview.net/forum?id=JePfAI8fah

[22] Yong Liu, Haoran Zhang, Chenyu Li, Xiangdong Huang, Jianmin Wang, and

Mingsheng Long. 2024. Timer: Generative Pre-trained Transformers Are Large

Time Series Models. In Forty-first International Conference on Machine Learning,

ICML 2024, Vienna, Austria, July 21-27, 2024. OpenReview.net. https://openreview.

net/forum?id=bYRYb7DMNo

[23] Mohammad M. Masud, Qing Chen, Latifur Khan, Charu C. Aggarwal, Jing Gao,

9


!!! page 10 "He_2025_FIRE"

Conference’17, July 2017, Washington, DC, USA

Cheng He, Xijie Liang, Zengrong Zheng, Patrick P.C. Lee, Xu Huang, Zhaoyi Li, Hong Xie, Defu Lian, and Enhong Chen

Jiawei Han, and Bhavani Thuraisingham. 2010. Addressing Concept-Evolution

in Concept-Drifting Data Streams. In ICDM 2010, The 10th IEEE International

Conference on Data Mining, Sydney, Australia, 14-17 December 2010, Geoffrey I.

Webb, Bing Liu, Chengqi Zhang, Dimitrios Gunopulos, and Xindong Wu (Eds.).

IEEE Computer Society, 929–934. doi:10.1109/ICDM.2010.160

[24] Md Mahmuddun Nabi Murad, Mehmet Aktukmak, and Yasin Yilmaz. 2025. WP
Mixer: Efficient Multi-Resolution Mixing for Long-Term Time Series Forecasting.

In AAAI-25, Sponsored by the Association for the Advancement of Artificial Intelli
gence, February 25 - March 4, 2025, Philadelphia, PA, USA, Toby Walsh, Julie Shah,

and Zico Kolter (Eds.). AAAI Press, 19581–19588. doi:10.1609/AAAI.V39I18.34156

[25] Yuqi Nie, Nam H. Nguyen, Phanwadee Sinthong, and Jayant Kalagnanam. 2023.

A Time Series is Worth 64 Words: Long-term Forecasting with Transformers.

In The Eleventh International Conference on Learning Representations, ICLR 2023,

Kigali, Rwanda, May 1-5, 2023. OpenReview.net. https://openreview.net/forum?

id=Jbdc0vTOcol

[26] Adam Paszke, Sam Gross, Francisco Massa, Adam Lerer, James Bradbury, Gre
gory Chanan, Trevor Killeen, Zeming Lin, Natalia Gimelshein, Luca Antiga,

Alban Desmaison, Andreas Köpf, Edward Z. Yang, Zachary DeVito, Martin Rai
son, Alykhan Tejani, Sasank Chilamkurthy, Benoit Steiner, Lu Fang, Junjie Bai,

and Soumith Chintala. 2019. PyTorch: An Imperative Style, High-Performance

Deep Learning Library. In Advances in Neural Information Processing Systems

32: Annual Conference on Neural Information Processing Systems 2019, NeurIPS

2019, December 8-14, 2019, Vancouver, BC, Canada, Hanna M. Wallach, Hugo

Larochelle, Alina Beygelzimer, Florence d’Alché-Buc, Emily B. Fox, and Roman

Garnett (Eds.). 8024–8035.

https://proceedings.neurips.cc/paper/2019/hash/

bdbca288fee7f92f2bfa9f7012727740-Abstract.html

[27] Xihao Piao, Zheng Chen, Taichi Murayama, Yasuko Matsubara, and Yasushi

Sakurai. 2024. Fredformer: Frequency Debiased Transformer for Time Series

Forecasting. In Proceedings of the 30th ACM SIGKDD Conference on Knowledge

Discovery and Data Mining, KDD 2024, Barcelona, Spain, August 25-29, 2024,

Ricardo Baeza-Yates and Francesco Bonchi (Eds.). ACM, 2400–2410. doi:10.1145/

3637528.3671928

[28] Junho Song, Keonwoo Kim, Jeonglyul Oh, and Sungzoon Cho. 2023. MEMTO:

Memory-guided Transformer for Multivariate Time Series Anomaly Detection.

In Advances in Neural Information Processing Systems 36: Annual Conference on

Neural Information Processing Systems 2023, NeurIPS 2023, New Orleans, LA, USA,

December 10 - 16, 2023, Alice Oh, Tristan Naumann, Amir Globerson, Kate Saenko,

Moritz Hardt, and Sergey Levine (Eds.). http://papers.nips.cc/paper_files/paper/

2023/hash/b4c898eb1fb556b8d871fbe9ead92256-Abstract-Conference.html

[29] Alexey Tsymbal. 2004. The problem of concept drift: definitions and related work.

Computer Science Department, Trinity College Dublin 106, 2 (2004), 58.

[30] Vladimir Vapnik and Rauf Izmailov. 2020. Complete statistical theory of learning:

learning using statistical invariants. In Conformal and Probabilistic Prediction

and Applications, COPA 2020, 9-11 September 2020, Virtual Event (Proceedings of

Machine Learning Research, Vol. 128), Alexander Gammerman, Vladimir Vovk,

Zhiyuan Luo, Evgueni N. Smirnov, Giovanni Cherubin, and Marco Christini

(Eds.). PMLR, 4–40. http://proceedings.mlr.press/v128/vapnik20a.html

[31] Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones,

Aidan N. Gomez, Lukasz Kaiser, and Illia Polosukhin. 2017. Attention is All you

Need. In Advances in Neural Information Processing Systems 30: Annual Conference

on Neural Information Processing Systems 2017, December 4-9, 2017, Long Beach,

CA, USA, Isabelle Guyon, Ulrike von Luxburg, Samy Bengio, Hanna M. Wallach,

Rob Fergus, S. V. N. Vishwanathan, and Roman Garnett (Eds.). 5998–6008.

[32] Shiyu Wang, Jiawei Li, Xiaoming Shi, Zhou Ye, Baichuan Mo, Wenze Lin, Sheng
tong Ju, Zhixuan Chu, and Ming Jin. 2024. TimeMixer++: A General Time Series

Pattern Machine for Universal Predictive Analysis. CoRR abs/2410.16032 (2024).

arXiv:2410.16032 doi:10.48550/ARXIV.2410.16032

[33] Shiyu Wang, Haixu Wu, Xiaoming Shi, Tengge Hu, Huakun Luo, Lintao Ma,

James Y. Zhang, and Jun Zhou. 2024. TimeMixer: Decomposable Multiscale

Mixing for Time Series Forecasting. In The Twelfth International Conference on

Learning Representations, ICLR 2024, Vienna, Austria, May 7-11, 2024. OpenRe
view.net. https://openreview.net/forum?id=7oLshfEIC2

[34] Gerald Woo, Chenghao Liu, Akshat Kumar, Caiming Xiong, Silvio Savarese,

and Doyen Sahoo. 2024. Unified Training of Universal Time Series Forecasting

Transformers. In Forty-first International Conference on Machine Learning, ICML

2024, Vienna, Austria, July 21-27, 2024. OpenReview.net. https://openreview.net/

forum?id=Yd8eHMY1wz

[35] Haixu Wu, Tengge Hu, Yong Liu, Hang Zhou, Jianmin Wang, and Mingsheng

Long. 2023. TimesNet: Temporal 2D-Variation Modeling for General Time Series

Analysis. In The Eleventh International Conference on Learning Representations,

ICLR 2023, Kigali, Rwanda, May 1-5, 2023. OpenReview.net. https://openreview.

net/forum?id=ju_Uqw384Oq

[36] Haixu Wu, Jiehui Xu, Jianmin Wang, and Mingsheng Long. 2021. Autoformer: De
composition Transformers with Auto-Correlation for Long-Term Series Forecast
ing. In Advances in Neural Information Processing Systems 34: Annual Conference

on Neural Information Processing Systems 2021, NeurIPS 2021, December 6-14, 2021,

virtual, Marc’Aurelio Ranzato, Alina Beygelzimer, Yann N. Dauphin, Percy Liang,

and Jennifer Wortman Vaughan (Eds.). 22419–22430. https://proceedings.neurips.

cc/paper/2021/hash/bcc0d400288793e8bdcd7c19a8ac0c2b-Abstract.html

[37] Jiehui Xu, Haixu Wu, Jianmin Wang, and Mingsheng Long. 2022. Anomaly

Transformer: Time Series Anomaly Detection with Association Discrepancy. In

The Tenth International Conference on Learning Representations, ICLR 2022, Virtual

Event, April 25-29, 2022. OpenReview.net.

https://openreview.net/forum?id=

LzQQ89U1qm_

[38] Zhijian Xu, Ailing Zeng, and Qiang Xu. 2024. FITS: Modeling Time Series with 10k

Parameters. In The Twelfth International Conference on Learning Representations,

ICLR 2024, Vienna, Austria, May 7-11, 2024. OpenReview.net. https://openreview.

net/forum?id=bWcnvZ3qMb

[39] Ning Xue, Isaac Triguero, Grazziela P. Figueredo, and Dario Landa-Silva. 2019.

Evolving Deep CNN-LSTMs for Inventory Time Series Prediction. In IEEE Con
gress on Evolutionary Computation, CEC 2019, Wellington, New Zealand, June

10-13, 2019. IEEE, 1517–1524. doi:10.1109/CEC.2019.8789957

[40] Yiyuan Yang, Chaoli Zhang, Tian Zhou, Qingsong Wen, and Liang Sun. 2023.

DCdetector: Dual Attention Contrastive Representation Learning for Time Se
ries Anomaly Detection. In Proceedings of the 29th ACM SIGKDD Conference on

Knowledge Discovery and Data Mining, KDD 2023, Long Beach, CA, USA, August

6-10, 2023, Ambuj K. Singh, Yizhou Sun, Leman Akoglu, Dimitrios Gunopulos,

Xifeng Yan, Ravi Kumar, Fatma Ozcan, and Jieping Ye (Eds.). ACM, 3033–3045.

doi:10.1145/3580305.3599295

[41] Kun Yi, Qi Zhang, Wei Fan, Shoujin Wang, Pengyang Wang, Hui He, Ning An,

Defu Lian, Longbing Cao, and Zhendong Niu. 2023. Frequency-domain MLPs

are More Effective Learners in Time Series Forecasting. In Advances in Neural

Information Processing Systems 36: Annual Conference on Neural Information

Processing Systems 2023, NeurIPS 2023, New Orleans, LA, USA, December 10 - 16,

2023, Alice Oh, Tristan Naumann, Amir Globerson, Kate Saenko, Moritz Hardt,

and Sergey Levine (Eds.).

http://papers.nips.cc/paper_files/paper/2023/hash/

f1d16af76939f476b5f040fd1398c0a3-Abstract-Conference.html

[42] Yunhao Zhang, Minghao Liu, Shengyang Zhou, and Junchi Yan. 2024. UP2ME:

Univariate Pre-training to Multivariate Fine-tuning as a General-purpose Frame
work for Multivariate Time Series Analysis. In Forty-first International Conference

on Machine Learning, ICML 2024, Vienna, Austria, July 21-27, 2024. OpenRe
view.net. https://openreview.net/forum?id=aR3uxWlZhX

[43] Haoyi Zhou, Shanghang Zhang, Jieqi Peng, Shuai Zhang, Jianxin Li, Hui Xiong,

and Wancai Zhang. 2021. Informer: Beyond Efficient Transformer for Long

Sequence Time-Series Forecasting. In Thirty-Fifth AAAI Conference on Artificial

Intelligence, AAAI 2021, Thirty-Third Conference on Innovative Applications of

Artificial Intelligence, IAAI 2021, The Eleventh Symposium on Educational Advances

in Artificial Intelligence, EAAI 2021, Virtual Event, February 2-9, 2021. AAAI Press,

11106–11115. doi:10.1609/AAAI.V35I12.17325

[44] Peng Zhou, Yufeng Guo, Haoran Yu, Yuanting Yan, Yanping Zhang, and Xindong

Wu. 2024. Concept Evolution Detecting over Feature Streams. ACM Transactions

on Knowledge Discovery from Data 18, 8 (2024), 1–32.

[45] Tian Zhou, Ziqing Ma, Qingsong Wen, Xue Wang, Liang Sun, and Rong Jin. 2022.

FEDformer: Frequency Enhanced Decomposed Transformer for Long-term Series

Forecasting. In International Conference on Machine Learning, ICML 2022, 17-23

July 2022, Baltimore, Maryland, USA (Proceedings of Machine Learning Research,

Vol. 162), Kamalika Chaudhuri, Stefanie Jegelka, Le Song, Csaba Szepesvári, Gang

Niu, and Sivan Sabato (Eds.). PMLR, 27268–27286. https://proceedings.mlr.press/

v162/zhou22g.html

10


!!! page 11 "He_2025_FIRE"

A Unified Frequency Domain Decomposition Framework for Interpretable and Robust Time Series Forecasting

Conference’17, July 2017, Washington, DC, USA

A

Comparison Between FFT and Wavelet

Transform

Both the Fast Fourier Transform (FFT) and Wavelet Transform

are fundamental tools for decomposing time series data from the

time domain into the frequency domain, enabling lossless forward

and inverse transformations. Despite this shared capability, they

differ significantly in their underlying principles and suitability

for general-purpose time series forecasting. In this section, we

compare their characteristics and explain why FFT is generally more

appropriate for modeling diverse time series data in forecasting

tasks.

• Parameter-free nature of FFT: FFT is a deterministic,

parameter-free transformation that decomposes a signal into

a fixed set of orthogonal frequency bases. The absence of

hyperparameters eliminates the need for domain-specific

knowledge or manual tuning during decomposition, making

FFT highly suitable for modeling diverse time series in a

general and automated manner.

• Hyperparameter dependence of Wavelet Transform:

In contrast, the Wavelet Transform requires selecting spe
cific wavelet functions and scale parameters, which act as

hyperparameters critically influencing the decomposition

results. Careful tuning of these parameters can enhance rep
resentation of time series exhibiting localized, transient, or

non-stationary behaviors. However, this reliance on domain

expertise and parameter selection limits its applicability

in universal forecasting frameworks across heterogeneous

datasets.

In summary, although both FFT and Wavelet Transform provide

lossless time-frequency analysis, FFT’s parameter-free and univer
sal nature makes it more suitable for general-purpose time series

forecasting. Conversely, the Wavelet Transform is better suited to

specialized scenarios where domain knowledge guides hyperpa
rameter tuning to effectively capture complex localized features.

B

Experimental Details

B.1

Implementation details

We use a fixed look-back window (context length) of 96 time points

to model the historical data and forecast future horizons 𝑇∈

{96, 192, 336, 720}. The patch length is varied between 8 and 48

to balance the trade-off between temporal resolution and computa
tional efficiency. Training is performed using mini-batch gradient

descent with batch sizes ranging from 32 to 256. Larger batch sizes

improve parallelism and enable more efficient utilization of GPU

resources. We adopt the ADAM optimizer for model optimization,

tuning the learning rate over the set {1×10−2, 5×10−3, 2×10−3, 1×

10−3, 5 × 10−4, 1 × 10−4} to achieve stable and efficient convergence.

Early stopping is employed based on the validation loss: if the vali
dation loss does not decrease for 8 consecutive epochs, which helps

prevent overfitting and reduces unnecessary computation. The

model is implemented in PyTorch and trained on a single NVIDIA

A100 GPU with 40GB of memory. Evaluation metrics include Mean

Squared Error (MSE) and Mean Absolute Error (MAE). We compare

our results against the best-performing state-of-the-art models re
ported in the literature or reproduced from their published source

Table 7: Full results of module ablation

model

FIRE

FIRE _adv.

FIRE _base

dataset

T

MSE

MAE

MSE

MAE

MSE

MAE

96

0.365 0.390 0.369

0.391

0.373

0.391

192

0.420 0.418 0.425

0.425

0.422

0.421

ETTh1

336

0.458 0.437 0.459

0.438

0.466

0.438

720

0.456 0.454 0.470

0.467

0.474

0.459

Avg. 0.425 0.425 0.431

0.430

0.434

0.427

96

0.282

0.333 0.280 0.331 0.281

0.333

192

0.362

0.383 0.359 0.382 0.360

0.384

ETTh2

336

0.403

0.419 0.398 0.421

0.400

0.420

720

0.408 0.433 0.412

0.433

0.409

0.433

Avg. 0.364

0.392 0.362 0.392

0.363

0.393

96

0.310 0.344 0.313

0.353

0.317

0.352

192

0.356 0.375 0.358

0.379

0.360

0.378

ETTm1

336

0.385

0.397

0.386

0.399

0.383 0.397

720

0.448

0.431 0.444

0.434 0.443 0.433

Avg. 0.375 0.387 0.375

0.391

0.376

0.390

96

0.170 0.252 0.172

0.253

0.172

0.253

192

0.237 0.297 0.238

0.298

0.237

0.297

ETTm2

336

0.299

0.338

0.300 0.338 0.296 0.334

720

0.399

0.395 0.398 0.397

0.394 0.394

Avg. 0.276

0.321

0.277

0.322 0.275 0.320

96

0.162 0.204 0.164

0.206

0.165

0.208

192

0.207 0.246 0.209

0.247

0.209

0.248

Weather

336

0.263 0.287 0.266

0.293

0.267

0.291

720

0.340 0.338 0.342

0.341

0.343

0.340

Avg. 0.243 0.269 0.245

0.272

0.246

0.272

96

0.474 0.272 0.479

0.285

0.493

0.304

192

0.487

0.269 0.480 0.286

0.486

0.299

Traffic

336

0.484 0.275 0.490

0.281

0.507

0.306

720

0.531 0.295 0.532

0.309

0.536

0.324

Avg. 0.494 0.278 0.495

0.290

0.506

0.308

96

0.148 0.236 0.151

0.239

0.162

0.249

192

0.161 0.249 0.163

0.250

0.172

0.258

Elc

336

0.176 0.265 0.179

0.267

0.189

0.275

720

0.215 0.299 0.217

0.301

0.232

0.310

Avg. 0.175 0.262 0.178

0.264

0.189

0.273

Best_Count

27/35 30/35

6/35

3/35

3/35

2/35

codes.

Summary of key hyperparameters:

• Input length (look-back window): 96

• Forecast horizons: 𝑇∈{96, 192, 336, 720}

• Patch length: 8 to 48

• Batch size: 32 to 256

• Learning rates tested: 1×10−2, 5×10−3, 2×10−3, 1×10−3, 5×

10−4, 1 × 10−4

• Optimizer: ADAM

• Early stopping: validation loss no improvement for 8 con
secutive epochs

• Hardware: NVIDIA A100 GPU with 40GB memory

B.2

Full results

Ablation results. To complement the average results reported

earlier, Table 7 presents the full forecasting performance for module

ablation. FIRE achieves the best MSE in 27 out of 35 experiments

and the best MAE in 30 out of 35. In contrast, FIRE _advanced ranks

second with only 6 and 3 best results on MSE and MAE, respectively.

These results demonstrate the critical importance of modeling both

data drift and basis evolution for improved forecasting accuracy.

11


!!! page 12 "He_2025_FIRE"

Conference’17, July 2017, Washington, DC, USA

Cheng He, Xijie Liang, Zengrong Zheng, Patrick P.C. Lee, Xu Huang, Zhaoyi Li, Hong Xie, Defu Lian, and Enhong Chen

Table 8: Full results of Loss ablation

Model

\sysname

\sysname_enh. \sysname_adv. \sysname_base

Data

T

MSE

MAE

MSE

MAE

MSE

MAE

MSE

MAE

96

0.365 0.390 0.369

0.391

0.385

0.401

0.381

0.400

192

0.420 0.418 0.423

0.420

0.432

0.434

0.426

0.429

ETTh1

336

0.458 0.437 0.462

0.438

0.465

0.447

0.458

0.441

720

0.456 0.454 0.461

0.459

0.474

0.467

0.468

0.464

Avg. 0.424 0.424 0.428

0.427

0.439

0.437

0.433

0.433

96

0.282 0.333 0.281

0.333

0.300

0.348

0.283

0.332

192

0.362 0.383 0.360

0.382

0.382

0.397

0.360

0.384

ETTh2

336

0.403 0.419 0.403

0.418

0.425

0.432

0.406

0.425

720

0.408 0.433 0.411

0.433

0.434

0.448

0.420

0.438

Avg. 0.363 0.392 0.363

0.391

0.385

0.406

0.367

0.394

96

0.310 0.344 0.312

0.349

0.325

0.368

0.316

0.357

192

0.356 0.375 0.359

0.376

0.369

0.390

0.360

0.380

ETTm1 336

0.385 0.397 0.383

0.395

0.390

0.407

0.389

0.403

720

0.448 0.431 0.442

0.430

0.453

0.442

0.448

0.441

Avg. 0.374 0.386 0.374

0.387

0.384

0.401

0.378

0.395

96

0.170 0.252 0.170

0.250

0.192

0.283

0.177

0.262

192

0.237 0.297 0.238

0.297

0.254

0.317

0.242

0.303

ETTm2 336

0.299 0.338 0.300

0.337

0.319

0.358

0.305

0.344

720

0.399 0.395 0.399

0.394

0.419

0.416

0.404

0.401

Avg. 0.276 0.320 0.277

0.319

0.296

0.343

0.282

0.327

96

0.162 0.204 0.160

0.202

0.163

0.207

0.162

0.205

192

0.207 0.246 0.206

0.244

0.208

0.249

0.207

0.247

Weather 336

0.263 0.287 0.264

0.287

0.264

0.288

0.267

0.291

720

0.340 0.338 0.342

0.338

0.344

0.34

0.344

0.339

Avg. 0.243 0.268 0.243

0.267

0.2448 0.2710 0.2450 0.2705

96

0.474 0.272 0.466

0.284

0.481

0.270

0.481

0.278

192

0.487 0.269 0.475

0.287

0.499

0.282

0.492

0.283

Traffic

336

0.484 0.275 0.482

0.278

0.509

0.289

0.516

0.293

720

0.531 0.295 0.527

0.297

0.547

0.307

0.552

0.306

Avg. 0.494 0.277 0.487

0.286

0.509

0.287

0.510

0.290

96

0.148 0.236 0.149

0.238

0.153

0.244

0.154

0.243

192

0.161 0.249 0.160

0.248

0.167

0.256

0.166

0.256

Elc

336

0.176 0.265 0.176

0.266

0.181

0.273

0.182

0.274

720

0.215 0.299 0.214

0.299

0.222

0.308

0.225

0.309

Avg. 0.175 0.262 0.174

0.262

0.180

0.270

0.181

0.270

Best

20/35 22/35 15/35

13/35

0

0

0

0

Additionally, Table 8 presents the full results of loss function

ablations across seven datasets. Our full model, FIRE, achieves the

best MSE and MAE in 20 and 22 out of all experiments, respectively,

outperforming all variants. The systematic performance degrada
tion observed when removing each loss component confirms the

essential contribution of every loss term to the overall forecasting

accuracy. This ablation study validates the design of the composite

loss in enhancing model effectiveness.

Model sensitivity to look-back window length. We evaluate

the impact of varying look-back window sizes {96, 192, 288, 384, 512}

on forecasting performance using ETTh1 and Weather datasets,

with other hyper-parameters fixed. As shown in Table 9 and Figure

4, for ETTh1, increasing the window size from 96 to 384 consis
tently reduces the average MSE from 0.439 to 0.414 and MAE from

Table 9: Forecasting results of various look back window sizes

Window size

96

192

288

384

512

Dataset

MSE

MAE

MSE

MAE

MSE

MAE

MSE

MAE

MSE

MAE

0.376

0.396

0.373

0.396

0.375

0.395

0.376

0.398

0.382

0.405

0.433

0.466

0.425

0.422

0.417

0.418

0.418

0.423

0.406

0.421

ETTh1

0.466

0.442

0.449

0.433

0.440

0.434

0.429

0.431

0.427

0.442

0.480

0.470

0.509

0.489

0.540

0.510

0.433

0.458

0.440

0.463

Avg.

0.439

0.444

0.439

0.435

0.443

0.439

0.414

0.427

0.414

0.433

0.162

0.204

0.154

0.195

0.147

0.194

0.150

0.195

0.146

0.192

0.209

0.247

0.198

0.237

0.194

0.239

0.195

0.241

0.190

0.236

Weather

0.267

0.289

0.252

0.282

0.251

0.281

0.246

0.281

0.248

0.283

0.343

0.339

0.330

0.335

0.322

0.332

0.317

0.331

0.312

0.333

Avg.

0.245

0.270

0.233

0.262

0.229

0.261

0.227

0.262

0.224

0.261

96

192

288

384

512

Look-back window length

0.42

0.43

0.44

Metric value

Avg MSE

Avg MAE

(a) ETTh1

96

192

288

384

512

Look-back window length

0.24

0.26

Metric value

Avg MSE

Avg MAE

(b) Weather

Figure 4: Average forecasting results on ETTh1 and Weather

datasets with various look back window lengths.

0.444 to 0.427, indicating improved accuracy due to more histori
cal information. However, further increasing the window to 512

leads to a slight increase in MSE (0.439) and MAE (0.433), suggest
ing diminishing returns or potential noise introduction. Similarly,

on the Weather dataset, average MSE and MAE decrease steadily

from 0.245 and 0.270 at window 96 to 0.224 and 0.261 at window

512, showing consistent gains with longer look-back windows. The

improvements are less pronounced beyond window size 384, indi
cating performance saturation.

Overall, these results demonstrate that enlarging the look-back

window generally enhances forecasting accuracy by leveraging

more temporal context, but beyond a certain length, the benefits

plateau or slightly decline, likely due to noise accumulation and

redundancy in the input data.

12

