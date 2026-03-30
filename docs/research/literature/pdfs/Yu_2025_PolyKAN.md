# PolyKAN: Efficient Fused GPU Operators for Polynomial Kolmogorov-Arnold Network Variants
**Author**: Mingkun Yu; Heming Zhong; Dan Huang; Yutong Lu; Jiazhi Jiang
**Creator**: arXiv GenPDF (tex2pdf:4177c2c)

---

PolyKAN: Efficient Fused GPU Operators for

Polynomial Kolmogorov–Arnold Network Variants

Mingkun Yu

Sun Yat-sen University

Guangzhou, China

Heming Zhong

Sun Yat-sen University

Guangzhou, China

Dan Huang

Sun Yat-sen University

Guangzhou, China

Yutong Lu

Sun Yat-sen University

Guangzhou, China

Jiazhi Jiang

Sun Yat-sen University

Guangzhou, China

Abstract

Kolmogorov–Arnold Networks (KANs) promise higher ex
pressive capability and stronger interpretability than Multi
Layer Perceptron, particularly in the domain of AI for Science.

However, practical adoption has been hindered by low GPU

utilization of existing parallel implementations. To address

this challenge, we present a GPU-accelerated operator li
brary, named PolyKAN which is the first general open-source

implementation of KAN and its variants. PolyKAN fuses the

forward and backward passes of polynomial KAN layers into

a concise set of optimized CUDA kernels. Four orthogonal

techniques underpin the design: (i) lookup-table with linear

interpolation that replaces runtime expensive math-library

functions; (ii) 2D tiling to expose thread-level parallelism

with preserving memory locality; (iii) a two-stage reduction

scheme converting scattered atomic updates into a single

controllable merge step; and (iv) coefficient-layout reordering

yielding unit-stride reads under the tiled schedule. Using a

KAN variant, Chebyshev KAN, as a case-study, PolyKAN

delivers 1.2–10× faster inference and 1.4–12× faster training

than a Triton + cuBLAS baseline, with identical accuracy on

speech, audio-enhancement, and tabular-regression work
loads on both highend GPU and consumer-grade GPU.

Keywords: Kolmogorov–Arnold Networks, GPU operator

optimization, CUDA fused kernels, deep-learning accelera
tion

Multi-Layer Perceptron(MLP)

Kolmogorov-Arnold Network(KAN)

Universal Approximation Theorem

Kolmogorov-Arnold Representation Theorem

Model

Theorem

Formula

Structure

���(�) =

�=1

2�+1

��

�=1

�

��,� ��

���(�) ≈

�=1

�(�)

���(��∙�+ ��)

Fixed activation functions

on nodes

Learnable weights

on edges

Learnable activation

functions on edges

Sum operation

on nodes

Including

Basis Function

�1,1

�1,2

�1

Figure 1. Architectural and theoretical comparison between

traditional multi-layer perceptron (MLP) and Kolmogorov
Arnold Network (KAN).

1

Introduction

Deep learning (DL) has achieved remarkable progress across

domains such as computer vision, natural language process
ing, and scientific computing [14]. Multilayer perceptrons

(MLPs) [20] are foundational building blocks of deep learn
ing, yet their inherently opaque nature raises concerns about

transparency and interpretability [5, 19]. To pursue more

accuracy and higher interpretability, researchers are com
pelled to explore novel model architectures and activation

mechanisms of deep learning. As illustrated in Figure 1, tra
ditional MLP employs fixed non-linear activation functions

such as ReLU [16], Sigmoid [20] and Tanh [9]. In contrast,

Kolmogorov-Arnold Network (KAN) [15] replaces the fixed

activation functions with a linear combination of a set of

polynomial basis functions, based on Kolmogorov-Arnold

representation theorem [13]. The specific pattern of linear

combination is determined by a set of learnable coefficients.

Therefore, the process of mapping the input to the output

through the nonlinear activation function is transparent.

KANs offer improved memory capacity, interpretability,

and accuracy compared to traditional MLPs [31]. Therefore,

KANs have been successfully extended to reconstruct various

neural network modules, including convolutional [3], graph

architectures [32], even Transformer [29] and large language

models [7]. Especially in the domain of AI for Computational

Science and Engineering such as partial differential equation

[6], KAN has shown much better performance than MLP due

to its characteristics [11, 25, 30]. To adapt to different tasks,

KANs can further enhance the capability through adjusting

basis functions and parameterization configurations. This

prompts a wide spectrum of KAN variants based on Fourier

[28], Chebyshev [21], Legendre [2], and other basis functions.

Although KAN variants possess these unique advantages,

they typically suffer from 10× slower runtimes than MLPs

with comparable model and parameter sizes [15]. This ineffi
ciency stems from: (i) the use of parameterized univariate

functions as activation function substantially increases com
putational overhead, (ii) KAN basis-expansion primitives use

naive loop-based implementation, limited optimization for

parallelism strategies, such as kernel fusion, and (iii) irregu
lar memory access limits GPU concurrency. Convolutional

1

arXiv:2511.14852v1  [cs.DC]  18 Nov 2025


!!! page 2 "Yu_2025_PolyKAN"

and GEMM benefit from deeply optimized libraries (e.g.,

cuDNN [4], cuBLAS [17]). In contrast, polynomial basis ex
pansion, which uses a linear combination of basis polynomial

functions to represent complex functions, still lacks a high
performance kernel library, resulting in a major bottleneck

for practical KAN deployment.

To address this issue, we propose a systematic approach

of GPU parallel optimization for KAN and its variants, exem
plified by Chebyshev KAN (ChebyKAN). Our approach com
bines lookup-table (LUT) interpolation to alleviate the high

cost of polynomial basis expansions, 2D tiling over inputs

and outputs to improve spatiotemporal locality, two-stage

reduction to mitigate atomic contention, and coefficient
layout reordering for coalesced access. This approach of
fers a reusable operator interface for seamless integration to

prevalent deep learning frameworks, such as PyTorch. Our

main contributions are summarized as follows:

1) Systematic analysis of the core bottlenecks in KAN
type networks. We identify the issues of “multi-step

dependency” and “complex function calls” for high-order

polynomials under GPU parallelism. Furthermore, we ana
lyze how traditional, operator-by-operator concatenation

fails to fully exploit GPU potential from both computa
tional and memory-access perspectives.

2) A general, extensible fused-kernel design paradigm.

We propose a general fused-kernel paradigm that inte
grates forward/backward computations with LUT-based

evaluation, 2D tiling, two-stage reduction, and coefficient

layout reordering, significantly reducing kernel launch

overhead and atomic conflicts. This results in 1.3–2.2×

speedup and 1.3–4× throughput improvement on end-to
end tasks.

3) Generalization across KAN variants. We analyze the

computational characteristics of the KAN variant and

demonstrate the generalization of our proposed method.

The proposed fused-kernel design is independent of ba
sis function selection, supporting KAN variants based on

Chebyshev, Legendre, Fourier, etc. Additionally, the de
sign can function as a plug-in component, enabling its

seamless integration into complex model architectures

such as Convolutional Networks, Graph Neural Networks,

and Transformers.

4) A reusable operator optimization library, PolyKAN,

for polynomial/kernel approximation networks. We

implement and evaluate an open-source library, PolyKAN,

delivering substantial training and inference speedups

without accuracy loss, and providing Python APIs for

better usability in domain of AI for Science. To the best of

our knowledge, this is the first open-source, general GPU

operator library for the polynomial-based KAN variants.

The rest of the paper overviews KAN and polynomial expan
sions (§2), analyzes bottlenecks and motivation (§3), details

our optimizations (§4), and presents experiments (§5) before

concluding (§6).

2

Background and Related Work

2.1

Overview of KAN

As an alternative to traditional MLPs, KAN introduces a

novel architecture that replaces fixed node-wise activations

with learnable edge-wise univariate functions, aiming to

improve both expressive efficiency and interpretability. This

design is grounded in the idea that complex multivariate

continuous functions can be decomposed into compositions

of simpler univariate ones. The theoretical underpinning

of this decomposition is the Kolmogorov-Arnold Theorem,

which we briefly review below.

Theorem 2.1 (Kolmogorov-Arnold Theorem [13]). Let 𝑓:

[0, 1]𝑛→R be an arbitrary continuous function. Then there

exist continuous single-variable functions

𝜙0,𝜙1, . . . ,𝜙2𝑛and 𝜓𝑞,1,𝜓𝑞,2, . . . ,𝜓𝑞,𝑛

(for 1 ≤𝑞≤2𝑛+ 1)

such that, for all 𝑥= (𝑥1,𝑥2, . . . ,𝑥𝑛) ∈[0, 1]𝑛,

𝑓(𝑥) =

2𝑛+1

∑︁

𝑞=1

𝜙𝑞



𝑛

∑︁

𝑝=1

𝜓𝑞,𝑝(𝑥𝑝)



.

Based on the Kolmogorov-Arnold theorem, KAN adopts a

network structure that can be broadly described as follows:

for an arbitrary input vector x ∈R𝑛, each component 𝑥𝑝is

first mapped by a univariate function 𝜓𝑞,𝑝, where 𝑝indexes

the dimensions of 𝑥and 𝑞indexes channels. The results of

these mappings across all input dimensions are then summed,

and the summed value is passed through another univariate

function 𝜙𝑞. Finally, the scalar outputs from all 𝑞paths are

added together to produce the final output. The structure of

the Kolmogorov-Arnold network is shown in Figure 2.

Fitted polynomial map on edges

Sum operations

on nodes

�0(�) = 1,   �1(�) = �,

��+1(�) = 2���(�) −��−1(�).

�(�) =

�=1

�

�=0

�

�����(���ℎ(��)).

Basis

Functions

Figure 2. The structure of the Kolmogorov-Arnold network.

2.2

KAN variant: Chebyshev KAN

Chebyshev KAN [21] is a variant of KAN. The univariate

basis functions are implemented with Chebyshev polyno
mials, replacing the conventional B-spline basis or other

2


!!! page 3 "Yu_2025_PolyKAN"

activation functions. The first computation strategy for

the Chebyshev polynomial expansion is defined as follows:

𝑇𝑛(𝑥) = cos 𝑛arccos𝑥,

𝑥∈[−1, 1], 𝑛∈N.

(1)

where 𝑛denotes the order of the Chebyshev polynomial,

which governs both its shape and approximation capacity.

When a target function exhibits greater complexity, 𝑛typ
ically resorts to polynomials of higher order. Since GPUs

have high throughput on basic operators such as vector
ized addition, subtraction, multiplication and division, the

overhead of calling high-level functions such as cos(·) or

sin(·) multiple times is much higher than addition and mul
tiplication. Therefore, exploiting the trigonometric identity

cos (𝑛+1)𝜃 = 2 cos𝜃cos(𝑛𝜃) −cos (𝑛−1)𝜃, investigators

establish the second computation strategy of Chebyshev

polynomial expansion by the following recurrence formula:

𝑇0(𝑥) = 1,

𝑇1(𝑥) = 𝑥,

𝑇𝑛+1(𝑥) = 2𝑥𝑇𝑛(𝑥) −𝑇𝑛−1(𝑥). (2)

For every input dimension 𝑝, the model evaluates the

Chebyshev polynomials from 𝑇0 up to 𝑇degree. Consequently,

for each dimension 𝑝, we obtain a multi-order feature set



𝑇0(𝑥𝑝), 𝑇1(𝑥𝑝), . . . , 𝑇𝐾(𝑥𝑝)

, where 𝐾= 𝑑𝑒𝑔𝑟𝑒𝑒.

These polynomial features are subsequently combined

with a set of learnable coefficients to produce the layer’s out
put. In the original ChebyKAN implementation, all features

generated by input dimension 𝑝and polynomial order 𝐾are

concatenated to form a large feature vector:

ℎ= [𝑇0( ˜𝑥1),𝑇1( ˜𝑥1), ...,𝑇𝐾( ˜𝑥1),𝑇0( ˜𝑥2), ...,𝑇𝐾( ˜𝑥𝑛)].

(3)

Let W denote the learnable “coefficient matrix”, the map
ping can be written as: 𝑦= 𝑊· ℎ+ 𝑏, where 𝑦denotes the

output of the current layer. The network architecture of a

ChebyKAN layer is shown in Figure 3.

2.3

The characteristics of the KAN variants

Numerous KAN variants share a common computational

skeleton—generating multi-order basis functions for each

input dimension and aggregating them with learnable coeffi
cients. Trigonometric-based forms (e.g., Chebyshev, Fourier)

leverage recurrences to propagate orders without repeated

sin/cos evaluations. For instance, FourierKAN can exploit

identities such as cos (𝑘+ 1)𝑥 = cos(𝑘𝑥) cos(𝑥) −sin(𝑘𝑥)

sin(𝑥), thereby propagating between successive orders with
out invoking sin(𝑘𝑥) or cos(𝑘𝑥) for every 𝑘.

Orthogonal-polynomial and piecewise basis (e.g., Legendre,

Hermite, B-splines) exhibit similar recurrence forms. Ab
stractly, 𝛼𝑘(𝑥) 𝐵𝑘+1(𝑥) = 𝛽𝑘(𝑥) 𝐵𝑘(𝑥) −𝛾𝑘𝐵𝑘−1(𝑥), leads

to similar dataflows and memory-access patterns during ex
pansion and coefficient aggregation.

It is evident that despite differences in basis form and theo
retical origin, most of the KAN variants share the consistent

framework of multi-order basis expansion and learnable co
efficient aggregation. In the following, we take ChebyKAN

as a representative case and conduct a detailed analysis of

its performance bottlenecks.

3

Performance Analysis and Motivation

In this section, we use ChebyKAN as a representative to

analyze why KAN variant operators underutilize GPUs and

motivate our optimizations. Adopting the Roofline perspec
tive [27], we balance compute and bandwidth to identify the

dominant bottlenecks. The conclusions are also applicable

to other KAN variants.

3.1

Diagnosis of performance bottlenecks

Although both the trigonometric Eq. (1) and recurrence

Eq. (2) formulations of Chebyshev polynomials mentioned in

§2.2 are valid, the recurrence form is preferred for superior

GPU efficiency. We analyze its performance bottlenecks on

GPU hardware. The parameters and notations in this paper

are listed in Table 1.

Table 1. Configurations of ChebyKAN.

Symbol

Meaning

𝐵

Batch size of input data

𝐷𝑖𝑛

Dimension of input data

𝐷𝑜𝑢𝑡

Dimension of output data

𝑑

Maximum order of a polynomial

𝜆

Bytes per element

𝑇𝐼𝐿𝐸_𝐼𝑁

Thread-block tile size along Input

𝑇𝐼𝐿𝐸_𝑂𝑈𝑇

Thread-block tile size along Output

𝑔_𝑥

Number of input tiles, 𝑔𝑥=



𝐷in

TILE_IN



𝑔_𝑦

Number of output tiles, 𝑔𝑦=



𝐷out

TILE_OUT



As illustrated in Figure 3, the forward propagation process

of ChebyKAN can be roughly divided into two steps: calcu
lating the polynomial values of all orders and multiplying
accumulating the polynomial expansion results with the

learnable coefficient matrix.

Counting fused multiply-adds conservatively as 2 FLOPs,

the layer’s total work and main data movement scale as

𝑇= 𝑇𝑒𝑥𝑝𝑎𝑛𝑑+𝑇𝑐𝑜𝑚𝑏𝑖𝑛𝑒≈2𝐵𝐷in(𝑑+ (𝑑+1)𝐷out) ,

𝑆≈𝜆[𝐵𝐷in + 𝐵𝐷out + 2𝐵𝐷in(𝑑+1) + 𝐷in𝐷out(𝑑+1)] .

yielding arithmetic intensity:

𝐼= 𝑇

𝑆

≈

2𝐵𝐷in(𝑑+ (𝑑+1)𝐷out)

𝜆[𝐵(𝐷in+𝐷out) + 2𝐵𝐷in(𝑑+1) + 𝐷in𝐷out(𝑑+1)] .

where 𝐼scales linearly with the batch size 𝐵and the out
put dimension 𝐷𝑜𝑢𝑡. Consequently, as shown in Figure 4

ChebyKAN operates in two distinct regimes:

• Memory-bound (𝐼< 𝐼max). Arithmetic intensity be
comes too low to saturate the GPU’s compute units.

3


!!! page 4 "Yu_2025_PolyKAN"

Figure 3. Replacing a conventional feed-forward layer in deep-learning models with a ChebyKAN layer: the input 𝑋is

mapped elementwise by the Chebyshev-polynomial basis, producing the basis tensor 𝑇with entries 𝑇𝑏,𝑗,𝑑= 𝑇𝑑(𝑡𝑎𝑛ℎ(𝑋𝑏,𝑗)).

The tensor 𝑇is then linearly contracted with the learnable coefficient tensor 𝐶to yield the output 𝑌.

Figure 4. The roofline model of the Kolmogorov-Arnold

network.

Each step of the recurrent formulation must access

and update the result from the previous order. Un
like matrix multiplication, the required data cannot be

pre-loaded and processed in one highly parallel pass.

Additionally, if the computation of small segments

is not properly batched within the same block/warp,

the kernel incurs frequent global-memory accesses or

redundant data loads.

• Compute-bound (𝐼≥𝐼max). Scaling both 𝐵and 𝐷out

pushes the arithmetic intensity 𝐼past the ridge point.

Yet the loop-carried dependencies in the recurrent

basis-function generator restrict instruction-level par
allelism. Additionally, the enlarged set of polynomials

and coefficients inflate the per-thread register foot
print, thereby lowering Streaming Multiprocessor(SM)

occupancy.

Therefore, our optimization strategy focuses on cutting

global-memory traffic and maximizing in-block data reuse.

These measures simultaneously raise arithmetic intensity in

memory-bound case and improve compute utilization when

the workload crosses into the compute-bound regime.

3.2

Related GPU optimization work

From the viewpoint of classical high-performance computing

(HPC) and numerical analysis, both industry and academia

have already undertaken extensive optimization of trigono
metric function and polynomial recurrence. Libraries

such as Intel Vector Math Library (VML) [10], the CUDA

math API [18], and other specialized vector-function pack
ages offer hand-tuned vectorization, SIMD/SIMT parallelism,

and approximation techniques that greatly reduce the la
tency of single-point or small-batch function calls. For the

aggregation phase, dense GEMM libraries such as cuBLAS

and CUTLASS attain near-peak hardware throughput. Some

recent work, such as FusedFourierKAN [8], has optimized

the performance of the KAN variant based on Fourier poly
nomial from an overall operator perspective.

However, these libraries perform well at their respective

micro-kernels, with only particular execution stages opti
mized. Traditional vector math libraries usually only map

functions like cos(𝑥) and exp(𝑥)to vectorized implementa
tions, and do not fully optimize for the large number of

intermediate steps that exist in multi-order recurrence. They

also lack a design that fuses these basis function computa
tions with the subsequent multiply-accumulate of learnable

coefficients. Although FusedFourierKAN attempts to fill this

gap, it relies on simple kernel fusion, yielding limited perfor
mance gains, and its design is tightly coupled to the Fourier

basis, which hinders extension to other polynomial bases.

This motivates the general optimization pipeline proposed

4


!!! page 5 "Yu_2025_PolyKAN"

in the present work. To our knowledge, our proposed solu
tion first provides a unified, variant-agnostic acceleration

framework for KAN-style operators.

4

Methodology

4.1

Overview

To accelerate both forward and backward propagation of

KAN operators (e.g., ChebyKAN, LegendreKAN) on mod
ern GPUs, we design a generic optimization pipeline. Its guid
ing principle is to maximize parallelism while minimizing

memory pressure without sacrificing support for different

polynomial bases. The overall design is shown in Figure 5.

The proposed pipeline consists of four orthogonal methods:

.

=0...3

Shared memory

Register

Threads

Binary-Tree Reduction

Global Memory

Coeff

Register

Sum-reduction

Threads

CPU

Partial Stage

Combine Stage

GPU

out

near stride

. ..

lane1

lane2

in

degree

out

degree

in

.. .

lane1

lane2

far stride

unit-stride

along

unit-stride

Coefficient Layout Reordering

LUT Construction

PartialOut

Degree

Sample Index

along

out

in

degree

.

.

unit-stride

along

Two–Dimensional Tiling

along the input-tile

Two-Stage Reduction

2

3

4

Lookup Table (LUT)    with Interpolation

1

...

Block Sliding

Block

Warp

=0...7

same thread

Figure 5. The overall design of the KAN variant acceleration.

1. Lookup Table (LUT) with Interpolation. The ba
sis functions of many polynomials (e.g., Chebyshev,

Legendre) can be pre-computed offline and stored in

a large LUT [1]. At run time, we obtain approxima
tions by linear (or higher-order) interpolation, elimi
nating expensive trigonometric evaluations or recur
rence formulations. Our implementation allocates the

LUT in global memory, so as to meet high-precision

requirements while alleviating constant-memory ca
pacity constraints.

2. 2D Tiling. We adopt a 2D tiling strategy by simulta
neously partitioning the input and output dimensions

into rectangular blocks of configurable size. Each GPU

thread block is assigned to process a single tile, per
forming the corresponding multiply-accumulate oper
ations locally. This design improves data access spatial

locality, which enhances cache reuse and enables fine
grained parallelism across both dimensions.

3. Two-Stage Reduction (Partial + Combine). We adopt

a two-stage scheme to avoid large-scale atomicAdd

operations on the same output location which cause

severe resource contentions. In the Partial stage, each

tile accumulates its partial sum in shared memory. The

Combine stage then merges partial results from dif
ferent tiles into the final output, reducing atomic con
tention and write-conflict overhead.

4. Coefficient Layout Reordering. The original coeffi
cient tensor is usually stored as [inputdim, outputdim,

degree + 1], which leads to large access strides inside

the kernel. We reorder it to [degree + 1, outputdim,

inputdim], enabling contiguous memory accesses and

higher bandwidth utilization.

By applying the four key optimization steps described

above, the proposed implementation significantly reduces

the number of explicit function calls, bandwidth waste, and

atomic collisions in both forward and backward propagation.

4.2

Polynomial Operators Acceleration via LUT

Many polynomial basis functions employed in the KAN vari
ants, such as Chebyshev, Legendre, and Hermite, share two

universal properties:

• Domain normalization to [−1, 1]. Each basis is ei
ther intrinsically defined on the interval [−1, 1] or can

be mapped to that interval by a simple normalization

step. For example, the input 𝑥in ChebyKAN can be

transformed by tanh(·) so as to ensure that 𝑥∈[−1, 1].

• Offline discretization and storage. The polynomial

function 𝑝𝑑(𝑥) of any KAN variant attains a deter
ministic value for fixed 𝑑𝑒𝑔𝑟𝑒𝑒and 𝑥. Therefore, we

can sample 𝑝𝑑(𝑥) on the CPU over the interval [−1, 1]

with an appropriate step size, compute the results iter
atively, and store them in a LUT.

These properties enable the LUT-interpolation strategy

and demonstrate its generality: regardless of the particular

polynomial basis, once the function can be discretized over

[−1, 1] and a LUT built for the required degree, the same

strategy is always applicable.

4.2.1

Offline construction of LUT.

We first construct the LUT on the CPU. For a prescribed max
imum degree we choose a table size LUT_SIZE and discretize

the interval [−1, 1] with the uniform step: Δ =

2

LUT_SIZE−1.

At each grid point 𝑥𝑖= −1+𝑖Δ (𝑖= 0, 1, . . . , LUT_SIZE−1)

we evaluate the sequence 𝑇0(𝑥𝑖),𝑇1(𝑥𝑖), . . . ,𝑇degree(𝑥𝑖) by ap
plying the recurrence in Eq. (2) once, and write the results

into a two-dimensional array LUT. 𝐿𝑈𝑇[𝑑,𝑖] stores the value

of the 𝑑-th basis function at the 𝑖-th sample. For other KAN

variants, one merely replaces the Chebyshev recurrence with

the corresponding polynomial relation, leaving the subse
quent interpolation logic unchanged.

After LUT has been generated on the CPU, it is uploaded

to the GPU. While storing the table in read-only on-chip

memory could reduce access latency, its size exceeds the

available capacity. Consequently, the LUT is stored in global

memory, providing every thread in the subsequent kernels

with read-only access to the precomputed polynomial values.

5


!!! page 6 "Yu_2025_PolyKAN"

4.2.2

Online interpolation from LUT.

Once a GPU thread receives an input value 𝑥∈[−1, 1],

it approximates 𝑇𝑑(𝑥) from the lookup table in two steps:

(i) calculate its normalized position in the interval [−1, 1]

based on 𝑥: 𝑝𝑜𝑠=

𝑥+1

2

 LUT_SIZE −1; (ii) perform linear

interpolation between the two neighbouring samples whose

indices are ⌊pos⌋and ⌊pos⌋+ 1.

This procedure produces a close approximation to 𝑇𝑑(𝑥)

without invoking run-time trigonometric functions or the

recurrence relation.

Linear interpolation suffices for most applications: the

grid spacing Δ = 2/(LUT_SIZE −1) is small with a large

LUT_SIZE, rendering the interpolation error negligible over

the interval. Higher-order schemes (quadratic or cubic) could

further reduce error but at the cost of additional arithmetic.

Therefore, the linear variant strikes a favorable balance be
tween simplicity and efficiency.

In both forward and backward propagation, both polyno
mial values and their derivatives can be obtained directly

from the LUT. For the derivative, we can approximate 𝑑

𝑑𝑥𝑇𝑑(𝑥)

by a finite difference between neighbouring table entries,

or store the pre-computed differences as an auxiliary LUT.

In this work, using the Chebyshev basis as an example, the

backward gradient is computed from either 𝑇approx or the

difference of adjacent samples, avoiding explicit evaluations

of the analytic derivative. §4.3 revisits this strategy when

discussing backward propagation 2.

4.3

Parallelism of 2D tiling across the input and

output dimensions

The computational workload scales with 𝐷in · 𝐷out. One
dimensional parallelization over the batch axis forces warps

to stride long distances in either dimension, leading to non
coalesced memory traffic. We therefore adopt 2D tiling: par
tition input into TILE_IN and output into TILE_OUT. Each

CUDA block is assigned a TILE_IN × TILE_OUT sub-matrix,

but it processes it using a specialized “output-aligned” warp

strategy. This design (i) improves spatial locality for both

coefficient and LUT accesses, (ii) confines atomicAdd opera
tions to localized output regions, reducing contention, and

(iii) generates a larger set of load-balanced blocks, enabling

the scheduler to saturate all SMs more effectively.

Block–grid configuration and thread mapping. Let

grid =



𝑔𝑥, 𝑔𝑦, 𝐵



, where 𝑔𝑥=



𝐷in

TILE_IN



and 𝑔𝑦=



𝐷out

TILE_OUT



.

Critically, we set the block dimensions to block = (BLOCK_

DIM_X, BLOCK_DIM_Y), where BLOCK_DIM_Y is typically

32 (a full warp) and BLOCK_DIM_X is a smaller value (e.g., 8).

A block (tileI, tileO,𝑏) processes the sub-tile (Δ𝑖, Δ𝑜) using

a different thread mapping:

• The thread’s y index, 𝑡𝑦, maps directly to the output

dimension: o = Δ𝑜.start + 𝑡𝑦. This aligns a full warp

(32 threads) along the output dimension.

...

TILE_OUT

(32)

TILE_IN (64)

t�=0...3

��=0...7

Warp

BLOCK_DIM_Y = 32

BLOCK_DIM_X = 8

BLOCK

Same Thread

Block Sliding

...

Figure 6. Visualization of the output-aligned 2D tiling strat
egy. A single BLOCK (8×32 threads) maps its ty index 1:1

to the TILE_OUT dimension. A hardware Warp is an 8×4

tile. The "Same Thread" (yellow) iterates across the TILE_IN

dimension with a stride of BLOCK_DIM_X (8).

• The thread’s x index, 𝑡𝑥, maps to the offset of the input

dimension j.

To cover the entire TILE_IN range (e.g., 64), each thread is

assigned multiple j indices to process. This iteration uses the

thread’s 𝑡𝑥index as an initial offset and a stride of BLOCK_

DIM_X. Figure 6 provides a visual representation of this block

configuration and iterative mapping.

This output-aligned configuration is a deliberate choice to

resolve a critical performance bottleneck in the LUT access.

This bottleneck arises from a fundamental trade-off between

the ideal access patterns for the LUT and Coeff tensors:

• Ideal LUT Access (1-way Broadcast): To minimize

LUT memory divergence, a warp requires as few dis
tinct j values as possible. The ideal scenario provides 1

distinct j value and allows for a perfect 1-way broad
cast from the LUT.

• Ideal Coeff Access (32-way Coalescing): To maxi
mize Coeff coalescing, a warp requires many consec
utive j values. The ideal scenario provides 32 distinct

j values for a perfect 32-way coalesced access.

These two ideal scenarios are mutually exclusive. A naive

tiling strategy (e.g., a 64×16 block mapping tx->j) would re
sult in a hardware warp containing 32 distinct j values. Since

the LUT index idx is calculated from j, this naive mapping

causes a severe 32-way memory scatter.

Our (8, 32) block design is specifically chosen to be a trade
off. A warp in this configuration is an 8 × 4 tile, containing

only 8 distinct j values (one for each𝑡𝑥). This design reduces

the LUT memory bottleneck to a much more manageable

8-way scatter when accessing the LUT.

Coefficient/LUT memory layout and coalesced ac
cesses. As established in the previous section, our (8, 32)

block configuration is designed to solve the primary bottle
neck of LUT memory by reducing it to an 8-way scatter. This

6


!!! page 7 "Yu_2025_PolyKAN"

block-level decision, in turn, dictates the optimal memory

layout for the Coeff tensor.

Given this (8, 32) block , a hardware warp is an 8 × 4

tile, and its 8 consecutive threads (e.g., ty=0, tx=0..7) are

mapped to 8 different j indices . We must choose a layout

that makes these 8 accesses efficient.

Therefore, we reorder the coefficient tensor to the [𝑑,𝑜, 𝑗]

layout , where j is the innermost dimension. With this lay
out, the same 8 consecutive threads now access contiguous

memory addresses. Therefore, the hardware executes this as

a single, efficient 8-way coalesced read. This same coalesc
ing benefit applies to the atomicAdd operations during the

backward pass. This strategy, detailed further in §4.5.

The forward and backward propagation process. In

the forward propagation, each sub-block carries out the

multiply-accumulate of polynomial values over its desig
nated Δ𝑖and Δ𝑜. The forward propagation can be summa
rized by Algorithm 1, which reflects the new outer iterative

loop over the j dimension. Each thread evaluates Cheby
shev terms via LookupCheby on tanh(𝑥𝑏,𝑗) (§4.2) and accu
mulates over the degree in registers, returning the vector

𝑇0(𝑥𝑖),𝑇1(𝑥𝑖), . . . ,𝑇degree(𝑥𝑖).

During the backward propagation, we apply the same

output-aligned 2D tiling strategy to the output gradient

𝜕L/𝜕y. Within each (Δ𝑖, Δ𝑜) sub-tile, the gradients with

respect to both the coefficients and the inputs are computed

in batch. The corresponding pseudocode is presented as Al
gorithm 2.

4.4

Two-Stage Reduction

When either the data dimensions or the batch size are large,

each CUDA block must accumulate a portion of the output

(or its gradient) within a single kernel launch. Even with 2D

tiling along the input and output axes, writing directly to the

global output or the gradient array still incurs three major

drawbacks:

• Atomic contention. Whenever multiple blocks up
date the same batch item or the same output element, a

large number of atomicAdd operations are inevitable

and quickly become a performance bottleneck.

• Write-after-read latency. Since atomic updates are

serialized by the hardware, repeated atomic writes to

the same address within one kernel stall the instruction

pipeline and introduce extra latency.

• Superfluous atomic overhead. Atomic writes are

significantly more expensive than ordinary stores. Ag
gregating partial sums in an intermediate buffer and

performing a single consolidated write-back would cut

down the total number of atomic operations.

To mitigate these issues we introduce a two-stage reduc
tion (Partial + Combine). In the Partial stage, each block

stores its results in a private, conflict-free buffer. Subse
quently, in the Combine stage, these buffers are merged into

Algorithm 1: Forward propagation (Partial Stage)

with output-aligned 2D tiling and [𝑑,𝑜, 𝑗] layout.

Input:

𝑋∈R𝐵×𝐷in, 𝐶𝑜𝑒𝑓𝑓∈R(degree+1)×𝐷out×𝐷in,

𝐿𝑈𝑇∈R(degree+1)×LUT_SIZE,

𝑡𝑖𝑙𝑒in, 𝑡𝑖𝑙𝑒out, 𝐵𝐿𝑂𝐶𝐾_𝐷𝐼𝑀_𝑋

Output: partialOut ∈R(𝑔𝑥×𝑔𝑦×𝐵×tile_out)

1 for 𝑏←0 to 𝐵−1 in parallel do

2

for 𝑡𝑖𝑙𝑒𝐼←0 to ⌈𝐷in/tile_in⌉−1 in parallel do

3

for 𝑡𝑖𝑙𝑒𝑂←0 to ⌈𝐷out/tile_out⌉−1 in

parallel do

4

𝑖𝑛𝑠𝑡𝑎𝑟𝑡←𝑡𝑖𝑙𝑒𝐼× tile_in

5

𝑖𝑛𝑒𝑛𝑑←min(𝑖𝑛𝑠𝑡𝑎𝑟𝑡+ tile_in, 𝐷in)

6

𝑜𝑢𝑡𝑠𝑡𝑎𝑟𝑡←𝑡𝑖𝑙𝑒𝑂× tile_out

7

𝑜𝑢𝑡𝑒𝑛𝑑←min(𝑜𝑢𝑡𝑠𝑡𝑎𝑟𝑡+ tile_out, 𝐷out)

8

𝑔𝑥←⌈𝐷in/tile_in⌉

9

smem[𝐵𝐿𝑂𝐶𝐾_𝐷𝐼𝑀_𝑌][𝐵𝐿𝑂𝐶𝐾_𝐷𝐼𝑀_𝑋]

10

for (𝑡𝑥,𝑡𝑦) ←(0..𝐵𝐿𝑂𝐶𝐾_𝐷𝐼𝑀_𝑋−

1, 0..𝐵𝐿𝑂𝐶𝐾_𝐷𝐼𝑀_𝑌−1) in parallel do

11

out ←𝑜𝑢𝑡𝑠𝑡𝑎𝑟𝑡+ 𝑡𝑦

12

sum_total ←0

13

if out < 𝑜𝑢𝑡𝑒𝑛𝑑AND 𝑏< 𝐵then

14

for 𝑗←𝑖𝑛𝑠𝑡𝑎𝑟𝑡+ 𝑡𝑥to 𝑖𝑛𝑒𝑛𝑑−1

step 𝐵𝐿𝑂𝐶𝐾_𝐷𝐼𝑀_𝑋do

15

𝑥←tanh(X[b,j])

16

Tapprox ←

LookupCheby(LUT, x, degree)

17

sum_total ←

sum_total + 𝑑𝑜𝑡(𝐶𝑜𝑒𝑓𝑓[:

, out, 𝑗], Tapprox)

18

smem[𝑡𝑦,𝑡𝑥] ←sum_total

19

WaitAndReduceOverX(smem[𝑡𝑦],𝑡𝑥)

20

if 𝑡𝑥= 0 AND out < 𝑜𝑢𝑡𝑒𝑛𝑑AND

𝑏< 𝐵then

21

gIdx ←(𝑡𝑖𝑙𝑒𝑂× 𝑔𝑥+ 𝑡𝑖𝑙𝑒𝐼) × 𝐵×

tile_out + 𝑏× tile_out + 𝑡𝑦

22

partialOut[gIdx] ←smem[𝑡𝑦, 0]

the global output, converting many fine-grained atomic up
dates into a small, well-controlled batch of writes.

4.4.1

Partial and Combine stages.

In forward propagation, each thread block writes its partial

sum to device-global workspace buffer PartialOut instead

of issuing global atomics. Every sub-block created by the

2D tiling scheme owns a dedicated segment (denoted by

subBlockID) inside this buffer, preventing write conflicts

between blocks.

7


!!! page 8 "Yu_2025_PolyKAN"

Algorithm 2: Backward propagation with output
aligned 2D tiling and [𝑑,𝑜, 𝑗] layout.

Input:

𝑋∈R𝐵×𝐷in, 𝐶𝑜𝑒𝑓𝑓∈R(degree+1)×𝐷out×𝐷in,

𝐿𝑈𝑇∈R(degree+1)×LUT_SIZE,

tilein, tileout, BLOCK_DIM_X

Output: coeff _grad ∈R(degree+1)×𝐷out×𝐷in,

x_grad ∈R𝐵×𝐷in

// The following is executed by each block

(𝑡𝑖𝑙𝑒𝐼,𝑡𝑖𝑙𝑒𝑂,𝑏) in parallel

1 instart ←tileI × tile_in

2 inend ←min(instart + tile_in, 𝐷in)

3 outstart ←tileO × tile_out

4 outend ←min(outstart + tile_out, 𝐷out)

5 smemX [BLOCK_DIM_X][BLOCK_DIM_Y]

// Shared mem for x_grad

// Each thread (𝑡𝑥,𝑡𝑦) executes in parallel

6 if 𝑏< 𝐵then

7

for 𝑗←instart + 𝑡𝑥to inend −1 step

BLOCK_DIM_X do

8

out ←outstart + 𝑡𝑦

9

x_grad_partial ←0

10

if out < outend then

11

𝑔𝑜←𝑑𝑌[𝑏, out]

12

𝑥←tanh(𝑋[𝑏, 𝑗])

13

(Tapprox, dTdx) ←

LookupChebyAndDiff(𝐿𝑈𝑇, 𝑥, degree)

14

sum_dx ←0

15

for 𝑑←0 to degree do

16

atomicAdd(coeff _grad[𝑑, out, 𝑗], 𝑔𝑜×

Tapprox[𝑑])

17

for 𝑑←1 to degree do

18

c_val ←𝐶𝑜𝑒𝑓𝑓[𝑑, out, 𝑗]

19

sum_dx ←

sum_dx + 𝑔𝑜× c_val × dTdx[𝑑]

20

x_grad_partial ←sum_dx

21

smemX [𝑡𝑥,𝑡𝑦] ←x_grad_partial

22

final_x_sum ←

BlockReduceOverY(smemX [𝑡𝑥, :])

// Syncs & sums smemX[tx][0..31]

23

if 𝑡𝑦= 0 then

24

atomicAdd(x_grad[𝑏, 𝑗], final_x_sum)

25

SyncBlock()

// Wait for all threads before next j

After completion of the Partial stage, the partial sums

generated by all sub-blocks reside in PartialOut. The sub
sequent Combine stage merges these values. This process is

typically completed within a single kernel launch, obtaining

the final output y.

Since the values can be accumulated sequentially while

iterating over the subBlockIDs, the amount of write con
tention is greatly reduced at this stage. If a fully parallel

merge is desired, hierarchical or tree-based reduction schemes

can be employed to balance efficiency against implementa
tion complexity.

4.4.2

Performance benefit analysis.

Compared to a single-kernel direct write-back, the two-stage

reduction maintains a unique-writer invariant for every in
termediate and final location, thus eliminating all global

atomics in forward. The Combine stage performs ordinary

streaming loads and a single store per (𝑏,𝑜𝑢𝑡). For gradients,

we retain a minimal set of atomics: (i)coefficient gradient

aggregates across batches on the same (𝑑, 𝑗,𝑜𝑢𝑡); (ii)input

gradient uses per-block reduction along 𝑜𝑢𝑡, followed by a

single atomic add per (𝑏, 𝑗) to merge contributions across 𝑔𝑦

output tiles. This reduces atomics from 𝐵𝐷𝑖𝑛𝐷𝑜𝑢𝑡to 𝐵𝐷𝑖𝑛𝑔𝑦.

Atomic update count (forward). A block-reduction +

atomic-write baseline performs 𝑁base

atomic,fwd = 𝐵· 𝐷𝑜𝑢𝑡· 𝑔𝑥

atomic updates. Our two-stage reduction eliminates them:

𝑁ours

atomic,fwd = 0.

Bandwidth and temporary footprint. Two-stage intro
duces a streaming intermediate 𝑆partial ≈𝜆𝐵𝐷𝑜𝑢𝑡𝑔𝑥bytes

and extra I/O 2×𝑆partial(write+read). Two-stage is beneficial

when 𝑔𝑥𝑐𝑎≳𝑔𝑥(𝑐𝑟+𝑐𝑤) +𝑐𝑤, i.e., when the per-atomic cost

𝑐𝑎dominates normal read cost 𝑐𝑟and write costs 𝑐𝑤.

Backward 𝑥-gradient. A naive design would require

𝐵· 𝐷𝑖𝑛· 𝐷𝑜𝑢𝑡atomics. With intra-block reduction along

out, ours reduces it to 𝑁ours

atomic,bwd−x = 𝐵· 𝐷𝑖𝑛· 𝑔𝑦, avoiding

fine-grained atomic contention. A further two-stage pro
cess would remove atomics at the cost of an extra buffer

of 𝜆𝐵𝐷𝑖𝑛𝑔𝑦bytes and an additional launch, which is not

cost-effective in our methodology.

4.5

Coefficient layout reordering

In typical implementations of KAN networks, the polyno
mial coefficients are stored for every input dimension j and

output dimension o. When the tensor is kept in its default

three-dimensional layout, GPU threads must access elements

with excessively large strides, which in turn diminishes both

coalesced memory throughput and cache efficiency.

4.5.1

Original layout and memory-access pattern.

In the baseline implementation, the coefficients are stored

in the index order (𝑗,𝑜,𝑑), i.e. as a three-dimensional array

coeff[𝐷in][ 𝐷out][ degree+1]. Although this layout is in
tuitive for CPU code — one loops over every input index 𝑗

and output index 𝑜𝑢𝑡before selecting the desired degree 𝑑,

it leads to sub-optimal access patterns on the GPU. Under

a 2D tiling scheme in which a thread block sweeps across

8


!!! page 9 "Yu_2025_PolyKAN"

𝐷in ×𝐷out and then iterates over 𝑑, two contrasting stride

behaviours emerge:

• When a single thread reads successive polynomial or
ders coeff[𝑗,𝑜,𝑑], the stride along the 𝑑-dimension is

small and cache-friendly.

• However, if threads in the same warp handle neigh
bouring (𝑗,𝑜) pairs, their memory accesses are scat
tered across the first two dimensions of the array, pro
ducing non-contiguous addresses and poor coalescing

efficiency.

4.5.2

Reordering the coefficient to the layout [𝑑,𝑜, 𝑗].

To solve the access pattern problem, we reorder the coeffi
cient tensor as coeff_rearr[𝑑,𝑜, 𝑗]. This layout is not cho
sen in isolation; it is specifically designed to work in synergy

with the (8, 32) output-aligned block strategy.

As established in §4.3, our (8, 32) block is designed to have

8 distinct j values within a warp (from 𝑡𝑥= 0..7) to solve

the LUT bottleneck. With this block shape, a hardware warp

is an 8 × 4 tile, and its 8 consecutive hardware threads (e.g.,

ty=0, tx=0..7) are mapped to 8 different but consecutive j

indices. We must choose a layout that makes these 8 simulta
neous accesses efficient. Therefore, we reorder the coefficient

tensor to the [𝑑,𝑜, 𝑗] layout, where j is the innermost di
mension. Since these threads access contiguous memory

addresses, the hardware executes this as a single, efficient

8-way coalesced read.

Additionally, this layout benefits for both forward and

backward propagations. Forward propagation reads coeff[𝑑,

𝑜, 𝑗] with coalesced loads. Backward propagation writes to

𝜕L/𝜕coeff[𝑑,𝑜, 𝑗] , which benefits equally from coalesced

atomicAdd operations, significantly reducing atomic con
tention on the memory bus.

When 𝐷in and 𝐷out are large, this new layout, combined

with our specific tiling strategy, raises effective bandwidth

and hence throughput on identical hardware.

Since this method relies only on the enumerability of the

degree + 1 axis, it is applicable to Legendre, Hermite, and

other KAN variants.

5

Experiment

This section evaluates the practical effectiveness of the

ChebyKAN optimizations. The study adopts a macro-to
micro protocol. Firstly, for three representative end-to-end

workloads, we measure epoch-level training and inference

latency as well as sample throughput for seven kernel ver
sions, including both baselines, on an NVIDIA A100 GPU.

Second, we isolate a single ChebyKAN layer under the same

three input-output-degree configurations and record forward

and backward latency to analyse operator-level scalability.

Finally, we construct a roofline model to quantify how the

proposed methodology schemes mitigate micro-architectural

bottlenecks.

Importantly, our goal is to evaluate the effectiveness of

our proposed KAN operator as an MLP replacement. Thus,

we choose ChebyKAN-dominant models to highlight the

operator’s performance gains. This approach is crucial for

isolating the acceleration of our fused kernels, ensuring that

the measured speedups are not confounded by other complex

operators (e.g., attention mechanisms, graph convolutions

or PDE residual calculations) present in larger, state-of-the
art architectures. Our ultimate aim is to validate that our

optimized operator can serve as an efficient, plug-in replace
ment for Linear layers, enabling future work to reconstruct

existing deep learning models with KAN variants.

5.1

Hardware & Software Environment

All experiments are conducted on a single NVIDIA A100
SXM4-40 GB GPU which sustains theoretical peaks of 19.5

TFLOPS FP32.

The software stack comprises Ubuntu 22.04 LTS (ker
nel 5.15), CUDA 12.6. High-level execution relies on Py
Torch 2.2.0+cu126. Micro-architectural data are gathered

with Nsight Compute 2024.1 in kernel performance-replay

mode. Timing is obtained with CUDA events placed around

each kernel, synchronising the stream before and after mea
surement; data-loader overheads are excluded.

5.2

Workloads and Baselines

5.2.1

Benchmark Suite.

Our benchmark suite comprises three distinct datasets, with

key parameters summarized in Table 2. For Google Speech

Commands v2 [26], each sample is a one-second utterance

intended for single-word classification. The VoiceBank
DEMAND [24] dataset is constructed by mixing clean ut
terances from the VoiceBank corpus with various environ
mental noise recordings from the DEMAND database. It is

repurposed for an acoustic-scene classification task. For the

Kaggle House-Prices [12] regression task, the model pre
dicts the target market price from 79 raw features. The input

is either zero-padded or truncated to a uniform dimension.

These three tasks jointly cover audio classification, speech

enhancement, and structured-data regression, and span op
erator widths from 40 to 1024, providing a representative

test bed for assessing ChebyKAN performance.

5.2.2

Baseline Implementations.

Seven kernels are evaluated. All kernels are functionally

identical (FP32 forward, FP32 gradients). The description of

each method is given in Table 3.

Baseline-1 evaluates Chebyshev basis via the trigonometric

form. Baseline-2 (cuBLAS) [22] constructs Chebyshev basis

via the recurrence form and employs the stock PyTorch im
plementation, which internally dispatches dense GEMM calls

to NVIDIA’s cuBLAS library. CuBLAS is widely regarded

as the industry-standard, vendor-tuned kernel for general
purpose matrix multiplication on GPUs. Specifically, PyTorch

9


!!! page 10 "Yu_2025_PolyKAN"

Table 2. Benchmark Suite Summary

Dataset

Description

Layer Widths

Degree

Batch Size

Google Speech Commands v2

105,872 utterances, 35 labels

40 →256 →256 →12

8

128

VoiceBank-DEMAND

28 speakers, 13 noises, 13 categories

257 →512 →512 →13

15

64

Kaggle House-Prices

1460 properties, 79 raw features

512 →1024 →1024 →1

24

32

Table 3. Kernel version of baselines and our KAN implementations.

Kernel version

Incremental Optimization Steps

Primary Bottleneck Solved

Baseline-1(BL1)

Direct evaluation of 𝑎𝑐𝑜𝑠/𝑐𝑜𝑠.

(N/A - Slowest baseline)

Baseline-2(BL2)

PyTorch + cuBLAS [17].

(N/A - Strong baseline)

V1

Chebyshev recurrence (𝑇𝑛= 2𝑥𝑇𝑛−1 −𝑇𝑛−2)

Replaces 𝑎𝑐𝑜𝑠/𝑐𝑜𝑠calls.

V2

V1 + Opt 1: LUT Interpolation.

Eliminates recurrence.

V3

V2 + Opt 2: Output-Aligned 2D Tiling.

Mitigates 32-way LUT scatter (reduces to 8-way).

V4

V3 + Opt 3: Two-Stage Reduction.

Solves forward-pass atomic contention.

V5 (PolyKAN)

V4 + Opt 4: Layout Reordering.

Solves 8-way Coeff stride (enables coalescing).

2.2 decomposes the layer into a Triton kernel [23] that ma
terializes Chebyshev basis and a GEMM core executed by

cuBLAS [17]. For small tensors Triton fuses both stages into

one kernel. Baseline2 represents the most efficient imple
mentation currently used by ChebyKAN. Versions V0 →

V5 are evaluated cumulatively. Each version inherits all

preceding optimizations.

5.3

End-to-End Evaluation

To quantify the user-perceived benefit of the proposed op
timizations, we measure the end-to-end training and infer
ence cost of all seven kernel versions on three workloads. As

the performance of Baseline-1 (BL1) is orders of magnitude

worse than the other kernel versions, including it in Figure 7

would severely distort the y-axis and make the results of the

other versions difficult to discern. Therefore, we report the

results for BL1 separately. The total single-epoch latency for

BL1 on the Speech Commands, VoiceBank, and House-Prices

tasks are 1798ms, 7193ms, and 3127ms, respectively. Figure 7

consolidates, for each workload, the wall-clock time of a

single epoch for the remaining kernel versions into two com
ponents: forward propagation and backward propagation on

the training split.

From Baseline-1 to Baseline-2, replacing the conventional

CUDA kernels with a cuBLAS-based reference already re
duces epoch time by 7–11×. Our optimization version V5

shortens the epoch by 1.3–2.2× compared with Baseline-2.

As detailed in Table 4, V5 demonstrates significant through
put improvements across all tasks. For the Google Speech

Commands v2 workload, V5 achieves an overall speed-up of

14.8× relative to Baseline-1 and 3.9× over Baseline-2. For the

VoiceBank-DEMAND dataset, V5 outperforms Baseline-1

and Baseline-2 by factors of 15× and 2.1×, respectively. On

Forward Time

VoiceBank-DEMAND

Kaggle House-Prices

Backward Time

GSC-v2

Forward Time

Backward Time

Forward Time

Backward Time

Epoch latency (ms)

BL2

V1

V2

V3

V4

V5

0

800

600

400

200

1000

Figure 7. Epoch latency of different versions on three bench
marks.

the House-Prices regression task, V5 yields a 12.6× gain com
pared to the initial implementation and a 1.3× improvement

over the cuBLAS-optimized baseline.

5.4

Numerical Fidelity and Convergence Speed

Evaluation

A primary concern with replacing an exact mathematical

formulation (i.e., Chebyshev recurrence) with an LUT-based

interpolation is the potential loss of numerical fidelity. In

our end-to-end evaluation, we therefore explicitly compared

the final model accuracy of our optimized V5 (PolyKAN)

operator against the Baseline-2 (BL2) implementation and

MLP implementation. We conducted this analysis on the

Speech Commands and Kaggle House Prices tasks. We omit
ted the VoiceBank-DEMAND task from this comparison, as

its simplicity led all models to achieve 100% accuracy within

the first few epochs, offering no meaningful differentiation.

The results, presented in Figure 8a and 8b, confirm that

our interpolation-based optimizations preserve numerical

10


!!! page 11 "Yu_2025_PolyKAN"

fidelity. On the House Prices task, PolyKAN achieves a final

validation RMSLE comparable to or better than both MLP and

BL2. On Speech Commands task, PolyKAN not only matches

but ultimately outperforms the BL2 baseline, achieving a

higher convergence rate.

We attribute this accelerated convergence to the funda
mental difference in gradient computation. Baseline-2 (Re
currence) uses PyTorch’s autograd on the exact recurrence

formula , which produces a complex and high-frequency

“jagged” gradient landscape for high-degree polynomials.

Conversely, our V5 (PolyKAN) kernel computes an approx
imate, piecewise-constant gradient derived from the finite

difference between LUT sample points ((tR - tL) / step).

This “smoother” gradient acts as an implicit regularizer, al
lowing the Adam optimizer to find a more stable and rapid

descent path. Our fused operator thus provides a dual benefit:

not only is each training step significantly faster, but fewer

steps are required to reach the optimal model accuracy.

0.0

0.5

1.0

1.5

2.0

Train Loss

Training Loss

MLP

BaseLine 2 (BL2)

v5 (PolyKAN)

0.4

0.5

0.6

0.7

0.8

0.9

1.0

Train Accuracy

Training Accuracy

MLP

BaseLine 2 (BL2)

v5 (PolyKAN)

0

10

20

30

40

50

Epoch

0.0

0.5

1.0

1.5

Validation Loss

Validation Loss

MLP

BaseLine 2 (BL2)

v5 (PolyKAN)

0

10

20

30

40

50

Epoch

0.6

0.7

0.8

0.9

1.0

Validation Accuracy

Validation Accuracy

MLP

BaseLine 2 (BL2)

v5 (PolyKAN)

(a) Training and validation loss/accuracy on the GSC-v2 task.

0

20

40

60

80

100

Epoch

10

1

100

101

Train Loss (RMSLE)

Training Loss

MLP

BaseLine 2 (BL2)

v5 (PolyKAN)

0

20

40

60

80

100

Epoch

100

101

Validation Loss (RMSLE)

Validation Loss

MLP

BaseLine 2 (BL2)

v5 (PolyKAN)

(b) Training and validation loss (RMSLE) on the Kaggle House Price

task.

Figure 8. Comparison of convergence behavior of V5

(PolyKAN) and the recurrence-based BL2 on (a) the GSC-v2

task and (b) the Kaggle House Price task.

5.5

Operator-Level Performance Analysis

Table 5 contrasts the layer latency of the seven implementa
tions on A100 GPU. We benchmark three precisely defined

tensor configurations so that the micro-benchmarks mirror

the shapes encountered in the end-to-end experiments:

Table 4. Throughput (samples/s) across three kernels.

Workload

Baseline-1

Baseline-2

V5

Speech Commands

5538

21029

82030

VoiceBank

1451

10281

21850

House-Price

396

3721

5000

• Config. 1: a mini-batch of 128 samples with 40 features

transformed to 256 features, degree 8;

• Config. 2: a mini-batch of 64 samples with 256 features

transformed to 512 features, degree 15;

• Config. 3: a mini-batch of 32 samples with 512 features

transformed to 1024 features, degree 24.

These three shapes span the three regimes of our work
loads, ensuring that layer-level measurements are directly

comparable to the end-to-end results.

V5 (PolyKAN) achieves its most dramatic speedup in the

small-scale configuration (Config. 1), delivering a 12.5× re
duction in total latency over BL2. As problem size and com
putational density increase (Config. 2 and 3), V5 maintains a

robust 1.4–3.9×speedup over BL2. Figure 9 maps represen
tative kernels onto the roofline model, revealing a coherent

migration of the performance bottleneck that validates our

strategy. The multi-level roofline plot confirms that PolyKAN

attains a superior balance of arithmetic intensity and hard
ware utilization. By tailoring thread-level parallelism to each

stage’s resource mix, PolyKAN sustains consistently high

GPU activity.

Figure 9. Multi-Level Roofline Analysis (L1, L2, DRAM) of

Baseline Implementations vs. PolyKAN.

5.6

General Applicability Evaluation

To assess generalization, we apply our acceleration tech
niques to FourierKAN and benchmark it against the state
of-the-art FusedFourierKAN [8] accelerator. On an A100

GPU, we measured throughput and end-to-end latency on

11


!!! page 12 "Yu_2025_PolyKAN"

Table 5. Operator-level latency single layer’s forward and backward pass, measured on an NVIDIA A100 GPU.

Config. 1 (Speech-like)

Config. 2 (VoiceBank-like)

Config. 3 (HousePrice-like)

Kernel Version

Fwd (ms)

Bwd (ms)

Sum (ms)

Fwd (ms)

Bwd (ms)

Sum (ms)

Fwd (ms)

Bwd (ms)

Sum (ms)

Config. (B, Din, Dout, d)

(128, 40, 256, 8)

(64, 256, 512, 15)

(32, 512, 1024, 24)

Baseline-1 (BL1)

1.301

2.577

3.878

13.881

22.359

36.240

33.541

66.806

100.347

Baseline-2 (BL2)

0.526

1.588

2.114

1.180

4.186

5.366

2.032

6.389

8.421

V1

0.181

1.026

1.207

3.683

4.378

8.061

29.108

19.031

48.139

V2

0.185

0.414

0.599

1.659

3.003

4.662

4.666

10.971

15.637

V3

0.064

0.450

0.514

0.791

3.311

4.102

1.985

9.695

11.680

V4

0.053

0.450

0.503

0.652

3.179

3.831

1.706

9.699

11.405

V5 (PolyKAN)

0.046

0.123

0.169

0.376

1.006

1.382

1.580

4.500

6.080

Table 6. Performance Comparison: FusedFourierKAN vs.

OurFourierKAN on Speech Commands Dataset.

Model

Forward Latency

(ms/batch)

Backward Latency

(ms/batch)

Throughput

(samples/s)

FusedFourierKAN

2.76

9.63

10327

OurFourierKAN

0.52

1.84

54222

the Speech Commands task, with results presented in Table

6.

Relative to FusedFourierKAN, our general optimization

methods achieved a 5× increase in throughput while simul
taneously reducing latency by a factor of 5. In addition to

ChebyKAN and FourierKAN, applying the same optimization

methodology to other KAN variants, such as LegendreKAN,

HermiteKAN, also delivers substantial performance improve
ments. These results not only substantiate the effect of the

proposed optimization paradigm but also demonstrate its

portability and general applicability across KAN variants.

5.7

Discussion

To demonstrate portability across heterogeneous hardware

platforms, we evaluate ChebyKAN on a consumer-grade

RTX 4060 GPU. The results mirror the trend observed on

A100, with our optimized kernel reducing latencies by 1.7–

2.3× across all configurations.

6

Conclusion

We propose an operator-level optimization design for accel
erating polynomial KAN variants on GPUs. Our fused-kernel

approach eliminates computational and memory bottlenecks

by integrating four techniques: LUT-based basis evaluation,

2D tiling, a two-stage reduction, and coefficient reorder
ing. Compared to the Python-based implementation and the

vendor-optimized baseline version, our method significantly

improves speed and throughput across three heterogeneous

benchmarks. The design generalizes broadly to architectures

like ChebyKAN and other polynomial architectures, serving

as a reusable component for basis function layers.

References

[1] Hans M Aus and Granino A Korn. 2006. Table-lookup/interpolation

function generation for fixed-point digital computations. IEEE Trans.

Comput. 100, 8 (2006), 745–749.

[2] Subhransu S. Bhattacharjee. 2024. TorchKAN: Simplified KAN Model

with Variations. GitHub repository. https://github.com/1ssb/torchkan

[3] Alexander Dylan Bodner, Antonio Santiago Tepsich, Jack Natan Spol
ski, and Santiago Pourteau. 2024. Convolutional kolmogorov-arnold

networks. arXiv preprint arXiv:2406.13155 (2024).

[4] Sharan Chetlur, Cliff Woolley, Philippe Vandermersch, Jonathan Co
hen, John Tran, Bryan Catanzaro, and Evan Shelhamer. 2014. cudnn:

Efficient primitives for deep learning. arXiv preprint arXiv:1410.0759

(2014).

[5] George Cybenko. 1989. Approximation by superpositions of a sig
moidal function. Mathematics of control, signals and systems 2, 4 (1989),

303–314. doi:10.1007/BF02551274

[6] Lawrence C. Evans. 2010.

Partial Differential Equations (2nd ed.).

Graduate Studies in Mathematics, Vol. 19. American Mathematical

Society. doi:10.1090/gsm/019

[7] Aditya Nalgunda Ganesh. 2024. KAN-GPT: The PyTorch implementa
tion of Generative Pre-trained Transformers (GPTs) using Kolmogorov
Arnold Networks (KANs) for language modeling. GitHub repository.

https://github.com/AdityaNG/kan-gpt version 1.0.0 (released 2024-05
09).

[8] GistNoesis. 2024. FusedFourierKAN: C++ & CUDA ops for fused

Fourier Kolmogorov-Arnold Networks. GitHub repository.

https:

//github.com/GistNoesis/FusedFourierKAN

[9] Xavier Glorot and Yoshua Bengio. 2010. Understanding the difficulty

of training deep feedforward neural networks. In Proceedings of the

thirteenth international conference on artificial intelligence and statistics.

JMLR Workshop and Conference Proceedings, 249–256.

[10] Bruce Greer, John Harrison, Greg Henry, Wei Li, and Peter Tang. 2001.

Scientific computing on the Itanium™processor. In Proceedings of the

2001 ACM/IEEE conference on Supercomputing. 41–41.

[11] Chunyu Guo, Lucheng Sun, Shilong Li, Zelong Yuan, and Chao Wang.

2024.

Physics-informed kolmogorov-arnold network with cheby
shev polynomials for fluid mechanics. arXiv preprint arXiv:2411.04516

(2024).

[12] Kaggle. 2016. House Prices: Advanced Regression Techniques. Kag
gle competition page. https://www.kaggle.com/competitions/house
prices-advanced-regression-techniques

[13] A. N. Kolmogorov. 1963. On the representation of continuous functions

of many variables by superposition of continuous functions of one

variable and addition. 55–59 pages. doi:10.1090/trans2/028/04

[14] Yann LeCun, Yoshua Bengio, and Geoffrey Hinton. 2015. Deep learning.

nature 521, 7553 (2015), 436–444.

12


!!! page 13 "Yu_2025_PolyKAN"

[15] Ziming Liu, Yixuan Wang, Sachin Vaidya, Fabian Ruehle, James Halver
son, Marin Soljačić, Thomas Y Hou, and Max Tegmark. 2024. Kan:

Kolmogorov-arnold networks. arXiv preprint arXiv:2404.19756 (2024).

[16] Vinod Nair and Geoffrey E Hinton. 2010. Rectified linear units improve

restricted boltzmann machines. In Proceedings of the 27th international

conference on machine learning (ICML-10). 807–814.

[17] NVIDIA Corporation 2025. cuBLAS Library User Guide. NVIDIA

Corporation, Santa Clara, CA.

https://docs.nvidia.com/cuda/pdf/

CUBLAS_Library.pdf

[18] NVIDIA Corporation 2025. CUDA Math API Reference Manual (release

12.9 ed.). NVIDIA Corporation, Santa Clara, CA. https://docs.nvidia.

com/cuda/pdf/CUDA_Math_API.pdf Online documentation.

[19] Cynthia Rudin. 2019. Stop explaining black box machine learning

models for high stakes decisions and use interpretable models instead.

Nature machine intelligence 1, 5 (2019), 206–215.

[20] David E. Rumelhart, Geoffrey E. Hinton, and Ronald J. Williams. 1986.

Learning representations by back-propagating errors. Nature (Oct

1986), 533–536. doi:10.1038/323533a0

[21] Sidharth SS, Keerthana AR, and Anas KP. 2024. Chebyshev polynomial
based kolmogorov-arnold networks: An efficient architecture for non
linear function approximation. arXiv preprint arXiv:2405.07200 (2024).

[22] SynodicMonth. 2024. ChebyKAN: Kolmogorov-Arnold Networks us
ing Chebyshev polynomials. GitHub repository.

Retrieved 2025
08-13 from https://github.com/SynodicMonth/ChebyKAN commit

5f7efdd18e749bcc99481bd87dc90bdeafb920d8.

[23] Philippe Tillet, Hsiang-Tsung Kung, and David Cox. 2019. Triton: an

intermediate language and compiler for tiled neural network computa
tions. In Proceedings of the 3rd ACM SIGPLAN International Workshop

on Machine Learning and Programming Languages. 10–19.

[24] Cassia Valentini-Botinhao. 2017. Noisy reverberant speech database

for training speech enhancement algorithms and TTS models. Dataset.

(2017). https://datashare.ed.ac.uk/handle/10283/2826 Online dataset.

[25] Y Wang, J Sun, J Bai, C Anitescu, MS Eshaghi, X Zhuang, T Rabczuk,

and Y Liu. 2025. A physics-informed deep learning framework for

solving forward and inverse problems based on Kolmogorov–Arnold

Networks. Computer Methods in Applied Mechanics and Engineering

433 (2025), 117518.

[26] Pete Warden. 2018.

Speech commands: A dataset for limited
vocabulary speech recognition. arXiv preprint arXiv:1804.03209 (2018).

[27] Samuel Williams, Andrew Waterman, and David Patterson. 2009.

Roofline: an insightful visual performance model for multicore ar
chitectures. Commun. ACM 52, 4 (2009), 65–76.

[28] Jinfeng Xu, Zheyu Chen, Jinze Li, Shuo Yang, Wei Wang, Xiping Hu,

and Edith C-H Ngai. 2024. FourierKAN-GCF: Fourier Kolmogorov
Arnold Network–An Effective and Efficient Feature Transformation for

Graph Collaborative Filtering. arXiv preprint arXiv:2406.01034 (2024).

[29] Xingyi Yang and Xinchao Wang. 2024. Kolmogorov-arnold transformer.

arXiv preprint arXiv:2409.10594 (2024).

[30] Yu-Sen Yang, Ling Guo, and Xiaodan Ren. 2025. Multi-Resolution

Training-Enhanced Kolmogorov-Arnold Networks for Multi-Scale PDE

Problems. arXiv preprint arXiv:2507.19888 (2025).

[31] Runpeng Yu, Weihao Yu, and Xinchao Wang. 2024. Kan or mlp: A

fairer comparison. arXiv preprint arXiv:2407.16674 (2024).

[32] Fan Zhang and Xin Zhang. 2024. Graphkan: Enhancing feature ex
traction with graph kolmogorov arnold networks. arXiv preprint

arXiv:2406.13597 (2024).

13

