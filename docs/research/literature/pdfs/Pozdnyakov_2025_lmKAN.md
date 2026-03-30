# Lookup multivariate Kolmogorov-Arnold Networks
**Author**: Sergey Pozdnyakov; Philippe Schwaller
**Creator**: arXiv GenPDF (tex2pdf:e76afa9)

---

Lookup multivariate Kolmogorov-Arnold

Networks

Sergey Pozdnyakov1

sergey.pozdnyakov@epfl.ch

Philippe Schwaller1,2

philippe.schwaller@epfl.ch

1 École Polytechnique Fédérale de Lausanne (EPFL)

2 National Centre of Competence in Research (NCCR) Catalysis

Abstract

High-dimensional linear mappings, or linear layers, dominate both the param
eter count and the computational cost of most modern deep-learning models.

We introduce a general-purpose drop-in replacement, lookup multivariate

Kolmogorov-Arnold Networks (lmKANs), which deliver a substantially bet
ter trade-off between capacity and inference cost. Our construction expresses

a general high-dimensional mapping through trainable low-dimensional mul
tivariate functions. These functions can carry dozens or hundreds of trainable

parameters each, and yet it takes only a few multiplications to compute them

because they are implemented as spline lookup tables. Empirically, lmKANs

reduce inference FLOPs by up to 6.0× while matching the flexibility of

MLPs in general high-dimensional function approximation. In another feed
forward fully connected benchmark, on the tabular-like dataset of randomly

displaced methane configurations, lmKANs enable more than 10× higher

H100 throughput at equal accuracy. Within frameworks of Convolutional

Neural Networks, lmKAN-based CNNs cut inference FLOPs at matched

accuracy by 1.6–2.1× and by 1.7× on the CIFAR-10 and ImageNet-1k

datasets, respectively. Our code, including dedicated CUDA kernels, is

available online at https://github.com/schwallergroup/lmkan.

104

105

106

Inference FLOPs

5 × 10

1

6 × 10

1

Mean Squared Error

6.0×

General function approximation

MLP

lmKAN

10

9

10

8

10

7

H100 seconds/molecule

(large batch size)

10

1

3 × 10

2

3 × 10

1

Test RMSE/STD

12.9×

Methane

MLP

lmKAN

105

106

3 × 105

Inference FLOPs

50

55

60

65

70

75

80

Test Accuracy (%)

2.1×

CIFAR-10

MLP CNN

lmKAN CNN

106

107

3 × 106

Inference FLOPs

40

45

50

55

60

Validation Top-5 Accuracy (%)

1.7×

1.7×

ImageNet

MLP CNN

lmKAN CNN

Figure 1: Performance summary. See Sec. 4 for details.

arXiv:2509.07103v2  [cs.LG]  17 Oct 2025


!!! page 2 "Pozdnyakov_2025_lmKAN"

1

Introduction

With a sufficient amount of training data, the capabilities of deep-learning models systemati
cally improve with the number of trainable parameters [1, 2]. However, deploying very large

models is challenging because of the associated inference cost.

In most models, high-dimensional linear mappings dominate both the parameter count and

the computational cost. Standard multilayer perceptrons (MLPs) alternate linear layers with

activations, and sometimes with a few other layers [3, 4]. If N is the width of a layer, the

parameter count and inference cost of these linear mappings scale as O(N 2), whereas most

other layers scale only as O(N). The same observation holds for many other architectures.

Transformers [5], when applied to very long sequences, are one of the few notable exceptions

because the cost of attention grows quadratically with the number of tokens. Even in that

case, however, the cost of the linear mappings remains substantial, not to mention the

potential use of fast approximations of attention [6].

The computational cost of a linear layer is proportional to the number of its parameters: at

inference, each parameter induces one multiplication per input, where the input is a whole

input object in the case of MLPs, a token in the case of Recurrent Neural Networks [7]

and Transformers [5], a node or an edge in the case of Graph Neural Networks [8], a patch

of an image in the case of Convolutional Neural Networks [9, 10], and similarly for other

architectures.

Spline lookup tables make it possible to do better than that. Consider, for example, a

one-dimensional piecewise-linear function f(x) on the interval from 0 to 1 with a uniform

grid. On each interval, it is given as f(x) = a[i]∗x+b[i], where i is the interval index. With G

intervals, the function has 2G trainable parameters, out of which G + 1 are independent once

continuity at the internal grid points is enforced. Yet the computational cost of evaluating

such a function at any given point is O(1), not depending on G. The computational pipeline

involves first determining the current grid interval as i = ⌊x ∗G⌋, and then evaluating only

one linear function as f(x) = a[i] ∗x + b[i].

Kolmogorov-Arnold Networks (KANs) [11], designed as a general alternative to MLPs, are

natural hosts for spline lookup tables as they construct a general high-dimensional mapping

through a collection of trainable univariate functions.

The main contributions of this work are the following:

• We propose lookup multivariate Kolmogorov-Arnold Networks (lmKANs) that are

built upon multivariate low-dimensional functions instead of the univariate ones

that standard KANs employ. We empirically compare the 2D version of lmKANs

with 1D FastKAN [12] and find that lmKANs are more accurate and easier to train.

• We implement the inner functions as spline lookup tables. Ignoring a non-asymptotic

O(N) term, the required inference FLOPs are only 2× those of a linear layer of the

same shape, while the number of trainable parameters can be dozens or hundreds of

times higher.

• We provide custom CUDA kernels that enable efficient inference of lmKANs on

modern GPUs. When using the 8×8 tile size, on the H100 GPU, our implementation

enables up to ∼88× faster inference than a linear layer with the same number of

trainable parameters.

• We empirically compare lmKANs and MLPs across diverse datasets, scales, and

backbones, using varied experimental setups to obtain a comprehensive view of

performance. Across these conditions, lmKANs are consistently Pareto-optimal with

respect to inference FLOPs. The performance of lmKANs is summarized in Fig. 1.

The proposed lmKAN layers can serve as a drop-in replacement for high-dimensional linear

mappings across a wide range of deep-learning architectures.

2


!!! page 3 "Pozdnyakov_2025_lmKAN"

2

Related work

Kolmogorov-Arnold Representation Theorem (KART) [13, 14] states that a continuous

function f : [0, 1]n →R can be represented as:

f(x1, . . . , xn) =

2n+1

X

q=1

Φq

n

X

p=1

ϕq,p(xp)

!

,

(1)

where ϕq,p : [0, 1] →R, and Φq : R →R are continuous univariate functions. There has

been a long debate [15, 16] on the usefulness of this theorem for machine learning because

of the general non-smoothness and wild behavior of the inner functions. Nevertheless, it

inspired the construction of Kolmogorov-Arnold Networks [17, 18], whose layers are defined

as yq = P

p fqp(xp), where fqp are trainable functions. Liu et al. [11] introduced the modern

version, which suggests stacking an arbitrarily large number of KAN layers and using an

arbitrarily large number of neurons, similarly to MLPs. While Liu et al. [11] illustrated

strong performance of KANs, many test cases involve ground-truth functions with known,

reasonably smooth KART or KART-like (matching KANs with more than one hidden layer

and a larger number of neurons) closed-form representations. Subsequent works such as Yang

and Wang [19], Kundu et al. [20], and Kashefi [21] further reinforced the efficiency of KANs.

On the contrary, Yu et al. [22] found that KANs can fall short compared to MLPs for some

tasks.

The idea of lookup-based O(1) computations of KAN univariate functions is sometimes briefly

mentioned but rarely implemented in practice [23, 24], likely because of challenges associated

with an efficient GPU implementation. Surprisingly, most of the research goes in the somewhat

opposite direction. B-splines, piecewise polynomial basis functions used in the original KAN

paper, have compact support and thus are well suited for O(1) inference.

Subsequent

works often replace them with dense basis functions, such as Chebyshev polynomials [25]

or Fourier harmonics [26]. The case of FastKAN [12], which replaces sparse B-splines with

similar-looking dense Gaussian radial basis functions exclusively for the sake of optimization,

is especially notable.

A few works, such as Moradzadeh et al. [27] and Huang et al. [28], implement the lookup

idea. Moradzadeh et al. [27], however, predict B-spline coefficients using an MLP for the

given grid points, which, thus, are not fully independent of each other. Huang et al. [28]

achieve remarkable efficiency on a small-scale problem from the original KAN paper by

algorithm-hardware co-design using the TSMC 22 nm RRAM-ACIM chip. Poluektov and

Polar [29] and Polar and Poluektov [30] employ piecewise linear parametrization suitable for

O(1) inference but do not focus on inference efficiency.

In this work, we provide CUDA kernels for efficient inference and benchmark the introduced

models against MLPs on general tasks where KART representations are not known in closed

form and where there is no reason to expect them to be smoother than in other cases.

3

Lookup multivariate Kolmogorov-Arnold Networks

At first glance, given that the inference cost of spline lookup tables does not depend on

the number of parameters, very expressive univariate functions with tens of thousands of

trainable parameters each are an ideal match for the Kolmogorov-Arnold Representation

Theorem. However, KANs rarely use more than a few dozen parameters per function in

practice. The difference between a univariate function parametrized by tens of thousands of

parameters and just a few dozen is the capability of the former to parametrize a very high

frequency band. On the one hand, this expressivity is necessary for closely approximating the

’wild behavior’ of KART inner functions, but on the other, it raises concerns about training

stability and generalization. On the contrary, multivariate functions can "accommodate" a

significantly larger number of parameters without spilling expressive power into exceedingly

high frequency bands. For instance, a four-dimensional function with just 10 grid points

along each dimension has roughly the same number of trainable parameters as a univariate

one with ∼104 grid intervals.

3


!!! page 4 "Pozdnyakov_2025_lmKAN"

A layer of a multivariate version of Kolmogorov-Arnold Networks with dimension d defines

the output as:

yq =

Nin/d−1

X

p=0

fqp(xdp, xdp+1..., xdp+d−1),

(2)

where fqp are trainable d-dimensional functions and Nin is the input dimensionality (assumed

to be divisible by d). We implement CUDA kernels for the two-dimensional case. The

motivation behind this choice is detailed in Sec. 3.3. An example of such a layer is depicted in

Fig. 2. Similar to KANs, these layers do not need additional activations in between and can

be stacked arbitrarily, substituting linear mapping-activation pairs in MLP-based backbones.

In Sec. 4.4, we empirically compare the two-dimensional version of lmKANs with one
dimensional FastKAN. The outcomes of these numerical experiments reinforce the intuitive

considerations given here and suggest that multidimensional building blocks can indeed be

more effective hosts for a large number of parameters in a practical setup.

Additionally, it is worth noting that, if necessary, multivariate functions fqp can always

fall back to sums of univariate ones, which would make the whole lmKAN fall back to

standard KAN. Thus, the Kolmogorov-Arnold Representation Theorem is applicable also to

our construction.

Figure 2: Schematic representation of a 2D lmKAN layer with 4 inputs and 3 outputs. This

layer defines outputs as: y0 = f00(x0, x1) + f01(x2, x3), y1 = f10(x0, x1) + f11(x2, x3), and

y2 = f20(x0, x1) + f21(x2, x3). The functions f∗∗(·, ·) are to be trained during fitting.

3.1

Function parametrization

During training, activations of neurons can evolve arbitrarily, making the use of grids defined

on bounded regions challenging. Therefore, we designed an unbounded grid which is still

regular enough to allow O(1) computations.

Sigma grid

The one-dimensional sigma grid, which is illustrated in Fig. 3a, is generated

by any sigmoid-like function σ(x). If the desired number of grid intervals is G, then the

grid points are given as the intersection of G −1 equispaced percentile levels with σ(x). An

example of a piecewise linear function defined on such a grid is given in Fig. 3b. Such a

construction spans the entire real axis. The grid has the finest resolution near the origin, and

becomes progressively coarser as |x| increases. For a given x, the index of the corresponding

grid interval can be computed as i = ⌊σ(x)G⌋, which makes such a grid suitable for O(1)

computations.

Static percentile grid

The choice of σ(x) in the construction above is somewhat arbitrary.

An additional consideration is that it would be beneficial to distribute inputs evenly, or

approximately evenly, across the grid intervals. If the probability distribution of inputs

is known, then one way to ensure perfect balance is to set σ(x) to be the corresponding

cumulative distribution function (CDF). However, it is challenging to implement such a

dynamic percentile grid in practice, as the distribution of inputs is unknown, can evolve

during training, and the corresponding CDF can hardly be queried in O(1) time.

Instead, we keep activations in a controlled range. A batch-normalization layer without affine

parameters placed before each lmKAN layer forces zero mean and unit variance. While it

4


!!! page 5 "Pozdnyakov_2025_lmKAN"

does not pin the entire distributions, it is safe to assume that they will be close enough to the

standard normal for a reasonable ratio of neurons. Therefore, a viable solution would be to

precede each lmKAN layer with a batch normalization with disabled affine transforms, and

select σ(x) to be the standard Gaussian CDF. In practice, we implement a fast approximation

that requires computing only a single exponent function at inference, see Appendix B. For

multivariate functions, we apply the same one-dimensional grid independently to each

coordinate.

4

3

2

1

0

1

2

3

4

x

0.2

0.0

0.2

0.4

0.6

0.8

1.0

1.2

a

(x)

Level lines

Grid points

i

1

i

i + 1

x

0.0

0.2

0.4

0.6

0.8

1.0

Bi(x)

c

Bi(x)

Grid points

4

3

2

1

0

1

2

3

4

x

1.0

0.5

0.0

0.5

1.0

f(x)

b

f(x)

Grid points

d

Figure 3: (a) Construction of the sigma grid; (b) an example of a piecewise linear function

defined on such a grid (c) Second-order B-spline (d) Two-dimensional second-order B-spline

.

B-splines

We use B-splines of second order built on top of the described grids as basis

functions to parametrize the lmKAN inner functions. A one-dimensional second-order B
spline centered around grid point i is given in Fig. 3c. It takes non-zero values on only two

adjacent grid intervals around the center grid point. If there are G intervals, then we use

G + 1 basis functions: G −1 such B-splines centered around each inner grid point, and two

linear functions on the left-most and right-most infinite intervals. For any given point x, there

are only two non-zero B-splines Bi(x) - the ones with i = ⌊σ(x)G⌋and i = ⌊σ(x)G⌋+ 1 (In

the corner case when x coincides with one of the grid points, there is only one). Appendix B

provides the definition of B-splines on edge intervals we use in this work, along with other

details.

A two-dimensional B-spline,

illustrated in Fig. 3d,

is defined as Bi1i2(x1, x2)

=

Bi1(x1) Bi2(x2).

All the functions defining a 2D lmKAN layer are parametrized as:

f(x1, x2) =

X

i1,i2

pi1i2 Bi1i2(x1, x2),

(3)

where pi1i2 are trainable coefficients.

With such a construction, there are (G + 1)2 independent parameters for each 2D function,

parametrized functions are bilinear on each 2D grid interval, all the functions are continuous

for arbitrary pi1i2, and all but the edge coefficients pi1i2 have a simple interpretation as the

value of the function on the corresponding grid point.

For any given point (x1, x2), there are only four non-zero B-splines; thus, one needs to

evaluate only four terms of Eq. 3 to compute f(x1, x2), which forms the basis of O(1)

5


!!! page 6 "Pozdnyakov_2025_lmKAN"

computations. The full algorithm to compute a standalone two-dimensional function is given

in Appendix B.1.

3.2

Computational cost

Algorithm 1 Forward pass of a 2D lmKAN layer.

Input: input vector x ∈RNin, parameter tensor P ∈R



G+1, G+1, Nin/2, Nout



.

P[ i1, i2, input_index, output_index ] is the value of finput_index, output_index at the

i1−, i2−th grid point.

Output: output vector y ∈RNout

1: y ←0

2: for input_index = 0 to Nin/2 −1 do

3:

i1, i2, Bi1i2(x1, x2), Bi1+1 i2(x1, x2), Bi1 i2+1(x1, x2), Bi1+1 i2+1(x1, x2) ←

Preamble

 x[2·input_index], x[2·input_index + 1]



4:

for output_index = 0 to Nout −1 do

5:

y[output_index] += Bi1 i2(x1, x2) P[ i1, i2, input_index, output_index ]

6:

y[output_index] += Bi1+1 i2(x1, x2) P[ i1+1, i2, input_index, output_index ]

7:

y[output_index] += Bi1 i2+1(x1, x2) P[ i1, i2+1, input_index, output_index ]

8:

y[output_index] += Bi1+1 i2+1(x1, x2) P[ i1+1, i2+1, input_index, output_index ]

9:

end for

10: end for

11: function Preamble(x1, x2)

▷Handling of edge-interval cases is omitted for brevity.

See Appendix B for more details.

Input: x1, x2; precomputed grid points G;

precomputed inverse areas Ainv[i1, i2] =



(G[i1 + 1] −G[i1])(G[i2 + 1] −G[i2])

−1

Output: indices i1, i2 and

B-splines Bi1 i2(x1, x2), Bi1+1 i2(x1, x2), Bi1 i2+1(x1, x2), Bi1+1 i2+1(x1, x2)

12:

i1 ←



σ(x1) G



13:

i2 ←



σ(x2) G



14:

Bi1 i2(x1, x2) ←(G[i1 + 1] −x1) (G[i2 + 1] −x2) Ainv[i1, i2]

15:

Bi1+1 i2(x1, x2) ←(x1 −G[i1]) (G[i2 + 1] −x2) Ainv[i1, i2]

16:

Bi1 i2+1(x1, x2) ←(G[i1 + 1] −x1) (x2 −G[i2]) Ainv[i1, i2]

17:

Bi1+1 i2+1(x1, x2) ←(x1 −G[i1]) (x2 −G[i2]) Ainv[i1, i2]

18:

return i1, i2, Bi1 i2(x1, x2), Bi1+1 i2(x1, x2), Bi1 i2+1(x1, x2), Bi1+1 i2+1(x1, x2)

19: end function

Overall, the functional form of lmKANs involves computations of many low-dimensional

functions with exactly the same arguments (those in the same column, see Fig. 2). When

doing so, it is possible to reuse many of the intermediate values, such as indices of the

grid intervals and B-splines. As Algorithm 1 elaborates, these intermediate values can be

computed once for each pair of inputs, and then utilized to compute the value of a given

function with just four multiply-add operations for the 2D case.

As the algorithm shows, the preamble part contributes only to an asymptotically insignificant

O(N) term, where N is the input (Nin) or output (Nout) dimension. Given that the total

number of 2D functions in an lmKAN layer is [Nin/2]Nout, the total number of required

multiply-add operations for the dominant, O(N 2), part is 4[Nin/2]Nout = 2NinNout, just 2×

that of a linear layer of the same shape. Following the common practice [31], we estimate

FLOPs as the number of fused multiply-adds of the main asymptotic term for both MLPs

and lmKANs.

It is worth noting that the O(N) preamble term is not an additional cost relative to MLPs; it

replaces the per-unit bias additions and activation evaluations that lmKANs do not require

— operations that can be quite expensive when the activations are transcendental functions

such as tanh.

6


!!! page 7 "Pozdnyakov_2025_lmKAN"

3.3

Perspective on dimensions and spline orders

All the constructions introduced so far straightforwardly generalize to a higher-dimensional

case. Evaluation of a single d-dimensional function parametrized by d-dimensional second
order B-splines would take 2d multiply-adds, which stem from the summation of B-spline

contributions residing on all the corners of the corresponding d-dimensional hypercube.

Given that the number of such d-dimensional functions would be d times smaller compared

to the number of weights of a linear layer of the same shape, the inference FLOPs of the

d-dimensional lmKAN layer would be 2d/d of that of the linear layer with the same shape.

These slowdown factors are exactly identical, 2×, for one- and two-dimensional lmKANs,

and start to grow for higher dimensions. Thus, we chose the two-dimensional version for the

implementation of CUDA kernels, as this extension of the standard univariate KAN comes

essentially for free.

If B-splines of order k are employed for parametrization instead of the second-order ones

described so far, the inference cost becomes kd/d of that of a linear layer. For more details,

see the B-spline definition at De Boor and De Boor [32], and how they are used in KANs [11].

Increasing the B-spline order brings a few benefits, but they likely do not justify the associated

increase in the computational cost.

The classical theorem about B-splines [33] indicates that while the order of B-splines affects

the convergence rate, any spline order is sufficient to approximate any function arbitrarily

closely by increasing the resolution of the grid1. Given that the computational cost of spline

look-up tables does not depend on the number of grid points, the grid resolution can be

arbitrarily increased without any computational overhead at inference.

On top of that, increasing the B-spline order introduces additional smoothness of the model.

Functions parametrized by B-splines of order k belong to Ck−2, but in general not to Ck−1.

The smoothness of second-order B-splines employed in this work matches that of ReLU [34],

one of the most popular and successful activation functions, which is also continuous, but not

continuously differentiable. Thus, it is questionable if the additional smoothness available

through higher orders k is necessary and would justify the associated computational overhead.

3.4

CUDA kernels

In this work, we implement CUDA kernels for efficient inference of 2D lmKANs on modern

GPUs. Our kernels use the classic shared-memory tiling used in GEMM [35]. In the following,

all benchmarks run in full-precision float32.

With a 16×16 tile, our implementation is ∼8× slower than a dense linear layer with the same

shape on an H100-SXM, irrespective of the grid resolution. The slowdown exceeds the ∼2×

FLOPs-based estimate from Sec. 3.2, primarily because of the less coherent memory-access

pattern of algorithm 1. Additionally, dense matrix multiplication has been the cornerstone

of many computational pipelines and, thus, has enjoyed decades of thorough optimization.

Finite shared-memory capacity limits the number of grid intervals to G≤20 on H100. At

this limit, an lmKAN layer holds (20 + 1)2/2 ≈220× more parameters than the linear

baseline with the same shape, so its inference time per trainable parameter is



(20 + 1)2/2



/8 ≈27.5× better.

Reducing the tile to 8×8 raises the slowdown to ∼9.5× but lets us increase G to 40, yielding

∼88.5× better per-parameter efficiency.

The performance of our kernels is even better when the feature dimension is small. The

numbers reported above were obtained in the limit of large batch sizes and feature dimensions.

Keeping the batch size large but setting, for instance, Nin = Nout = 32 lowers the slowdown

of the 16 × 16 kernel to only ∼2.5× relative to a linear layer of the same shape. Further

details are reported in Appendix D.

1This is applicable, though, to functions on a bounded domain.

7


!!! page 8 "Pozdnyakov_2025_lmKAN"

3.5

Hessian regularization

Direct fitting of splined functions with a fine grid imposes additional challenges related to

generalization. The problem is illustrated in Fig. 4a for the simple case of fitting a standalone

one-dimensional function parametrized by second-order B-splines on a uniform grid on [0, 1]

with G = 40 intervals, f(x) = P

i piBi(x).

0.0

0.2

0.4

0.6

0.8

1.0

f(x)

Problem

Ground truth

No regularisation

L2 regularisation

0.0

0.2

0.4

0.6

0.8

1.0

x

0.0

0.2

0.4

0.6

0.8

1.0

x

0.0

0.2

0.4

0.6

0.8

1.0

f(x)

Solution

Ground truth

f'(x) regularization

f''(x) regularization

f'''(x) regularization

Figure 4: Generalization pitfall.

Ground truth is an exact parabola, and the training set consists of 5 points, which are

illustrated on the plot. Since the number of grid points is large, the model has enough

flexibility to reproduce the training set exactly, but generalization is quite off. With such a

fine grid, only a few B-splines, marked as bold on the bottom panel of Fig. 4a, take non-zero

values for the training points. Thus, only the coefficients pi associated with these active

B-splines receive non-zero gradient during training, while all the others have no incentive to

evolve from the random values assigned at initialization. Standard L2 regularization is not

much better, as it simply pushes all non-active coefficients pi to zero, which also results in a

non-meaningful approximation after training.

When dealing with a similar problem, Xie et al. [36] employed off-diagonal regularization

based on a finite-difference scheme for the second derivative. One can put regularization

terms as λ P

i(pi −pi+1)2 for first derivative, λ P

i(pi −2pi+1 + pi+2)2 for second, and so on.

Such regularization schemes result in meaningful approximations after training, as illustrated

in Fig. 4b.

We implemented CUDA kernels for 2D lmKANs, which express general high-dimensional

mapping in terms of building blocks of two-dimensional functions. For 2D functions, we

use off-diagonal regularization based on the squared Frobenius norm of the Hessian, a

rotationally invariant measure of curvature in any direction, which is not to be confused

with the Laplacian. Furthermore, our finite-differences schemes take into account that the

grids, introduced in Sec. 3.1, are not uniform. More details are given in Appendix C.

The Hessian of a function is zero if and only if the function is linear. Therefore, the use of

a very strong Hessian-based regularization leads to linearization of the trained functions,

enforcing them to converge to f(x1, x2) = ax1 + bx2 + c. This makes the whole lmKAN

equivalent to an MLP of the same shape, modulo training dynamics. In other words, the

Hessian regularization coefficient λ can be used to smoothly adjust the lmKAN behavior

between fully unconstrained lmKAN and MLP extremes. This observation—that lmKANs

with heavy Hessian regularization match non-regularized MLPs—suggests that one should

use a combination of the proposed regularization scheme with standard ones, such as L2 or

dropout [37], for the best results.

8


!!! page 9 "Pozdnyakov_2025_lmKAN"

Preconditioning and fitting scheme

Similarly to the original KANs [11], we append a

preconditioning term to splined functions, which in our case is linear. To further increase

training stability, we employ a multi-staged fitting procedure, where the strength of the

described Hessian regularization is initially set to a high value and then gradually decays.

More details are available in Appendix E.

4

Experiments

We have demonstrated so far that lmKANs can have significantly better inference cost per

trainable parameter compared to linear layers in terms of both FLOPs and wall-clock time

on modern GPUs. The question is, however, whether this nominal efficiency translates to

real-life performance. Do lmKANs indeed represent a better trade-off between performance

and inference cost?

In this section, we empirically compare the efficiency of lmKANs and MLPs across the

following settings: (i) approximating general high-dimensional functions, (ii) on a tabular-like

dataset of randomly displaced methane configurations, and (iii) within CNN frameworks

evaluated on CIFAR-10 and ImageNet. Across all experiments, we use identical macro
architectural backbones for lmKANs and MLPs. Overall, to obtain a comprehensive picture

of the performance, we prioritized the diversity of the setups over a very large scale or the

architectural complexity of a particular backbone. We found that lmKANs are consistently

inference FLOPs — accuracy Pareto-optimal, with the largest gains on the methane dataset.

Finally, we compare lmKANs with FastKANs.

4.1

General function approximation

Our first experiment is set to measure crude flexibility of lmKANs in approximating general

high-dimensional functions, which we model by large teacher MLPs with fixed random

weights. We define a ground-truth R32 →R1 function as an MLP with 32 input neurons, 10

hidden layers, each with 1024 neurons, and hyperbolic tangent activations. When weights are

initialized using the default PyTorch initialization, the magnitude of activations progressively

decreases from layer to layer. Thus, to avoid this, we multiplied all the weights by 3.0 after

random initialization.

We fit both MLP and lmKAN students to approximate this ground-truth function and

compare their performance. We use the same fully connected backbone for both types of

models with two hidden layers and varying hidden dimensions. Both MLPs and lmKANs

use batch normalizations. We set affine=True for MLPs as it is the standard choice, and

affine=False for lmKANs in accordance with static percentile grids introduced in Sec. 3.1.

MLPs use ReLU activations, while lmKANs do not require any additional activation functions.

We use G = 12 for all the lmKAN models, as this was the optimal value found in the ablation

study described below. Pseudocode for both models is available in Fig. 5. Both students

have two hidden layers, which is one more than both Cybenko [38] (the one for MLPs) and

Kolmogorov-Arnold universal approximation theorems require. This setup, however, is more

realistic, as MLPs with exactly one hidden layer are rarely used in practice.

MLP student

Linear(input_dim →hidden_dim)

BatchNorm1d(hidden_dim, affine=True)

ReLU()

Linear(hidden_dim →hidden_dim)

BatchNorm1d(hidden_dim, affine=True)

ReLU()

Linear(hidden_dim →output_dim)

lmKAN student

lmKANLayer(input_dim →hidden_dim)

BatchNorm1d(hidden_dim, affine=False)

lmKANLayer(hidden_dim →hidden_dim)

BatchNorm1d(hidden_dim, affine=False)

lmKANLayer(hidden_dim →output_dim)

Figure 5: Pseudocode for MLP and lmKAN students.

We fit all the models with the Adam optimizer [39]. For each step of stochastic gradient

descent, we generate random inputs from the normal distribution, and compute the cor
9


!!! page 10 "Pozdnyakov_2025_lmKAN"

responding targets by evaluating the ground-truth teacher MLP. In such an infinite data

regime, the final Mean-Squared Error (MSE) depends on how flexible the models are, and

monotonically decreases with the hidden dimension for both MLPs and lmKANs.

The increase of the hidden dimension inevitably entails a higher computational cost at

inference, and the question is which family of models represents a better trade-off between

accuracy and computational efficiency. Our findings are summarized in Fig. 6. The left

column illustrates the final MSE of converged models depending on the hidden dimension,

the middle column represents the Pareto front between the final MSE and FLOPs required at

inference, and the last column contains the Pareto front between the final MSE and inference

H100 wall-clock time.

In order to justify the claims that lmKANs are indeed more efficient, we converge baseline

MLP-based models very tightly here, and in all similar experiments in this manuscript. For

the MLP baseline, we have two lines - one with a full training budget and one with only

half of it. The fact that these lines nearly coincide with each other demonstrates very tight

convergence.

Fig. 6 clearly indicates that lmKANs are significantly more FLOPs efficient at the same

accuracy level, up to 6×, for the largest dimensions. Furthermore, lmKANs also appeared

to be H100 wall-clock time optimal for all the scales, with the speed-up factor of about 1.8×

for the largest hidden dimension.

As an additional experiment, we fitted the same MLP and lmKAN students to approximate

an R32 →R32 function represented by a similar ground-truth MLP with random weights.

For this setup, lmKANs also appeared to be Pareto optimal, with FLOPs reduction up to

4.2×. More details are available in Appendix F.2.

32

64

128

256

512

1024

Hidden dimension

5 × 10

1

6 × 10

1

Mean Squared Error

MSE vs Hidden dimension

MLP 1/2

MLP

lmKAN

104

105

106

Inference FLOPs

6.0×

MSE vs Inference FLOPs

MLP 1/2

MLP

lmKAN

10

9

10

8

H100 SXM seconds/input

(large batch size)

1.8×

MSE vs Inverse H100 SXM throughput

MLP 1/2

MLP

lmKAN

Figure 6: lmKAN vs MLP for general function approximation.

The "MLP 1/2" line

corresponds to the outcome of the fitting procedure with only half of the training steps

compared to the "MLP" one.

34 6 8

12

16

20

26

32

40

G

0.4600

0.4625

0.4650

0.4675

0.4700

0.4725

Mean Squared Error

Figure 7: Final MSE vs G for the hidden_dim=256 lmKAN model.

10


!!! page 11 "Pozdnyakov_2025_lmKAN"

Ablation

We investigate the effect of the chosen number of grid intervals G on the resulting

lmKAN accuracy when approximating the R32 →R1 function with hidden_dim = 256. The

result is given in Fig. 7.

Contrary to our initial expectations, the final MSE does not monotonically decrease with

the grid resolution, having a distinct minimum at G = 12. This is happening despite the

fact that our setup effectively corresponds to an infinite data regime, effectively ruling out

overfitting as an explanation. We hypothesize that the reason is that Kolmogorov-Arnold

Networks are hard to converge for excessively fine grid resolution. Therefore, the optimal

value of G could depend on the training protocol. Appendix F.2 reinforces this supposition

by providing the MSE vs. epoch number plot with several lines corresponding to different G

values. Additionally, note that FastKANs were found to display the same effect to an even

greater degree, as detailed in Sec. 4.4.

4.2

Randomly displaced methane configurations

Figure 8: A methane config
uration

Our next step was to benchmark the performance of lmKANs

on real data.

Tabular datasets are the natural choice for

feedforward fully connected neural networks. Popular tabular

datasets, such as the Titanic [40] or housing prices [41], however,

are not particularly convenient for this purpose. First, they are

typically stochastic in nature - for instance, while it is possible

to improve a guess on the survival based on the data available

for the Titanic dataset, it is impossible to say for sure. Thus,

even an arbitrarily large model fitted on arbitrarily many data

points would have a non-zero limitation on the accuracy. In

other words, the performance of a model translates into an

error metric not so directly, making the comparisons between

different models less illustrative. Second, these datasets are

typically relatively small, making it challenging to sweep across

a wide range of model scales to obtain a comprehensive picture

of performance.

Therefore, we chose the tabular-like dataset of randomly displaced methane configurations [42]

for the comparison.

It consists of multiple off-equilibrium methane configurations, as

illustrated in Fig. 8. The target is given by the corresponding quantum-mechanical energy [43,

44]. Hydrogen atoms are placed around the carbon atom not as an ideal tetrahedron of an

equilibrium methane molecule, but rather randomly, varying from instance to instance. Thus,

the corresponding quantum-mechanical energies of such configurations are also different

from each other. Machine learning models fitted on such datasets belong to the class of

so-called machine learning interatomic potentials [45, 46]. This dataset is sufficiently large

for the comparisons, containing more than seven million configurations. Additionally, this

dataset is deterministic - the geometry of the corresponding methane configuration completely

determines the target (Formally, there can be a stochastic term due to the lack of complete

convergence of ab initio computations for the quantum-mechanical energy, but it is negligible

in practice).

The target, the potential energy of the system, is invariant with respect to rotations and

permutations of identical atoms2. Therefore, there are several viable representations of the

methane molecules depending on how these symmetries are addressed:

Cartesian Components: The simplest representation is a collection of all the Cartesian

components of all displacement vectors from the carbon atom to all the hydrogen atoms.

Since each methane molecule contains 4 hydrogen atoms, the total number of displacement

vectors is 4, and the total number of components is 12. When using this representation, we

simply concatenate all these components together and feed them to a fully connected MLP

or lmKAN whose input dimension is 12. This representation is not invariant with respect

to both rotations and permutations; thus, we use the corresponding augmentations during

2Formally, there is an additional symmetry, inversion, but the corresponding group contains only

two elements, thus it does not make much sense to treat it separately. We treat it as part of the

rotation group, and in the following, by rotation we mean proper or improper rotation.

11


!!! page 12 "Pozdnyakov_2025_lmKAN"

Table 1: Summary of methane representations

Label

Rotational

symmetry

Permutational

symmetry

#Features

Cartesian Components

Augmentations

Augmentations

12

Distances

Features

Augmentations

10

Cartesian Components Polynomials

Augmentations

Features

34

Distances Polynomials

Features

Features

31

training. We randomly permute hydrogen atoms and rotate each molecule whenever we

sample a minibatch from the training subset for each step of stochastic gradient descent.

Distances: Another possible representation is a collection of all the interatomic distances

between all the atoms. Since the total number of atoms is 5, the number of all the interatomic

distances is 5 ∗4/2 = 10. Therefore, the input dimension of fully connected networks applied

to this representation is 10. This representation is invariant with respect to rotations but not

with respect to permutations. During training, we use only permutational augmentations.

Cartesian Components Polynomials: We compute power sum symmetric polynomials on

top of the Cartesian components of the displacement vectors: Pαx,αy,αz = Pi=4

i=1 xαx

i yαy

i zαz

i

for non-negative integer αx+αy +αz ≤4. The total number of such symmetric polynomials is

34 (excluding trivial P0,0,0). This representation is invariant with respect to permutations but

not with respect to rotations. Thus, during training we use only rotational augmentations.

Distances Polynomials: The final representation is a collection of non-trivial symmetric

polynomials on top of the interatomic distances, constructed similarly as in Allen et al. [47].

The total number of such polynomials is 31, and their exact formulas are given in Appendix F.3.

This representation is invariant with respect to both rotations and permutations. Thus, we

do not use any augmentations during training for this representation.

The described representations are summarized in Table 1. We systematically evaluate all

four possible combinations of how the rotational and permutational symmetries can be

incorporated into the fitting pipeline. Within the Distances Polynomials representation,

the methane dataset is tabular in the classical sense — it is a table with about 7.7 million

rows and 31 columns. For other representations, the dataset is tabular-like given the available

augmentation strategies. We randomly split the data into 7000000, 300000, and 432488

train, validation, and test molecules, respectively.

For each representation, we fit the same families of MLP and lmKAN models as in the

previous section. The result is given in Fig. 9. For this dataset, we use G = 28, the optimal

value we found in ablation studies. Similarly to the previous experiment, we demonstrate

tight convergence of the baseline MLP models by providing three lines corresponding to

full, half, and quarter of the training budget, respectively. Overall, when compared to

domain-specific architectures, typically given by GNNs [48] and/or transformers [49], the

introduced feedforward fully connected models occupy a non-overlapping part of the Pareto

frontier — they are less accurate, but also orders of magnitude faster.

The figure illustrates that lmKANs consistently outperform MLPs across all modalities. Fur
thermore, the performance improvement is much larger compared to our previous experiment.

At the same accuracy level, lmKANs require dozens of times (or even up to one thousand

for the Distances modality) fewer inference FLOPs, which results in more than a 10×

improvement of the inference H100 wall-clock time.

On top of that, Fig. 9 provides early indications that lmKANs sometimes can be more

accurate in the limit of large scale, that is, to have better generalizability. The second row of

the figure, corresponding to the Distances modality, illustrates that the rate of improvement

of MLP models becomes very slow, and it is questionable if this family of models would ever

surpass the accuracy achieved by lmKAN models at any scale.

12


!!! page 13 "Pozdnyakov_2025_lmKAN"

8

16

32

64

128

256

512

1024

2048

10

1

100

Cartesian Components

Test RMSE / STD

Relative RMSE vs Hidden dimension

MLP 1/4

MLP 1/2

MLP

lmKAN

102

103

104

105

106

78.0×

Relative RMSE vs FLOPs

MLP 1/4

MLP 1/2

MLP

lmKAN

10

9

10

8

10

7

12.9×

Relative RMSE vs inverse H100 SXM throughput

MLP 1/4

MLP 1/2

MLP

lmKAN

8

16

32

64

128

256

512

1024

2048

10

2

10

1

Distances

Test RMSE / STD

MLP 1/4

MLP 1/2

MLP

lmKAN

102

103

104

105

106

1021.5×

MLP 1/4

MLP 1/2

MLP

lmKAN

10

9

10

8

10

7

71.6×

MLP 1/4

MLP 1/2

MLP

lmKAN

8

16

32

64

128

256

512

1024

2048

10

1

2 × 10

1

3 × 10

1

4 × 10

1

6 × 10

1

Cartesian Components

Polynomials

Test RMSE / STD

MLP 1/4

MLP 1/2

MLP

lmKAN

102

103

104

105

106

19.1×

MLP 1/4

MLP 1/2

MLP

lmKAN

10

9

10

8

10

7

4.1×

MLP 1/4

MLP 1/2

MLP

lmKAN

8

16

32

64

128

256

512

1024

2048

Hidden dimension

10

1

2 × 10

2

3 × 10

2

4 × 10

2

6 × 10

2

Distances

Polynomials

Test RMSE / STD

MLP 1/4

MLP 1/2

MLP

lmKAN

lmKAN Reg.

102

103

104

105

106

Inference FLOPs

77.4×

MLP 1/4

MLP 1/2

MLP

lmKAN

lmKAN Reg.

10

9

10

8

10

7

H100 SXM seconds / methane molecule

(large batch size)

11.4×

MLP 1/4

MLP 1/2

MLP

lmKAN

lmKAN Reg.

Figure 9: lmKAN vs MLP on the dataset of randomly displaced methane configurations.

"lmKAN Reg." curve corresponds to lmKAN fitted with Hessian regularization introduced in

Sec. 3.5. On the vertical axis, we plot the relative Root Mean Squared Error, which is given

as test RMSE normalized by standard deviation of the target in the dataset. The "MLP

1/2" and "MLP 1/4" curves correspond to outcomes of fitting procedures with half and a

quarter of the training budget, respectively.

On the other hand, depending on the nature of the data, raw lmKANs, without the Hessian

regularization we proposed in Sec. 3.5, can be more prone to overfitting. This happens for

the Distances Polynomials modality as the last row of Fig. 9 illustrates. This modality

incorporates all the symmetries into the representation and does not involve any sort of

augmentations. Therefore, it is likely that the generalization problem we outlined in Sec. 3.5

takes place for this fitting setup. As the green line of the fourth row of Fig. 9 illustrates, the

Hessian regularization is sufficient to overcome the overfitting. Properly regularized lmKANs

were found to outperform the MLPs and be Pareto optimal from the point of view of both

inference FLOPs and inference H100 wall-clock time.

13


!!! page 14 "Pozdnyakov_2025_lmKAN"

Ablations

Appendix F.3 contains ablation studies focusing on the grid resolution G and

the strength of Hessian regularization.

4.3

lmKAN-based Convolutional Neural Networks

In the introduction, we briefly outlined that high-dimensional linear mappings are the

primary building blocks in most architectures, not only in feedforward fully connected neural

networks. Convolutional Neural Networks are no exception.

A standard computer-vision two-dimensional convolution with kernel size k×k is parametrized

by linear mapping Rk2Cin →RCout, where Cin and Cout are numbers of input and output

channels, respectively. Since Kolmogorov-Arnold layers can be used as a general substitute

for high-dimensional linear mappings, one can construct a KAN-based convolutional neural

network well suited for image processing, as was done, e.g, in Bodner et al. [50]. In this

section, we compare the performance of lmKAN- and MLP-based CNNs on the CIFAR-10 [51]

and ImageNet [52] datasets.

CIFAR-10 CNN backbone

# Only convolutional and fully

connected layers are shown

# [32, 32, 3] →[16, 16, width]

Conv2D(3 →width, kernel_size = 2,

stride = 2)

# [16, 16, width] →[8, 8, width]

Conv2D(width →width, kernel_size =

2, stride = 2)

# [8, 8, width] →[4, 4, width]

Conv2D(width →width, kernel_size =

2, stride = 2)

# [4, 4, width] →[2, 2, width]

Conv2D(width →width, kernel_size =

2, stride = 2)

# [2, 2, width] →[1, 1, width]

Conv2D(width →width, kernel_size =

2, stride = 2)

FullyConnected(width →width)

FullyConnected(width →10)

ImageNet CNN backbone

# Only convolutional and fully

connected layers are shown

# [81, 81, 3] →[27, 27, base_width]

Conv2D(3 →base_width, kernel_size =

3, stride = 3)

# [27, 27, base_width] →[9, 9, 3*

base_width]

Conv2D(base_width →3*base_width,

kernel_size = 3, stride = 3)

# [9, 9, 3*base_width] →[3, 3, 9*

base_width]

Conv2D(3*base_width →9*base_width,

kernel_size = 3, stride = 3)

# [3, 3, 9*base_width] →[1, 1, 27*

base_width]

Conv2D(9*base_width →27*base_width,

kernel_size = 3, stride = 3)

FullyConnected(27*base_width →27*

base_width)

FullyConnected(27*base_width →1000)

Figure 10: CIFAR-10 and ImageNet CNN backbones. MLP-based CNNs additionally have

ReLU activations and batch normalizations with enabled affine transforms. lmKAN-based

CNNs do not require additional activations and use batch normalizations without affine

transforms as suggested by our static percentile grids described in Sec. 3.1.

4.3.1

CIFAR-10

Our backbone architecture consists of five 2 × 2 convolutions, each with stride 2, and two

fully connected layers at the end. Since the resolution of CIFAR-10 images is 32 × 32, where

32 = 25, five 2 × 2 convolutions with stride 2 transform the spatial dimensions of an image

exactly to 1×1. All the layers use the same width (= number of filters in case of convolutions,

and hidden dimension in case of fully connected layers), which we vary for both families

of the models. In other aspects, the models are similar to those we employed in previous

sections - we use batch normalizations with affine transforms for MLP-CNNs, and without

for lmKAN-CNNs; MLP-CNNs use ReLU activations, while lmKAN-CNNs do not require

additional activation layers.

14


!!! page 15 "Pozdnyakov_2025_lmKAN"

The dataset comes with pre-defined full training and test subsets. We split the full training

subset into training and validation parts in a 90%/10% ratio. Our augmentation pipeline

consists of established techniques, such as RandAugment [53], MixUp [54], CutMix [55], and

a few others. Further details about the augmentations and other aspects of our fitting setup

are available in Appendix F.4.

Our findings are illustrated in the upper row of Fig. 11. Similarly to previous experiments,

lmKAN-based CNNs were found to be more FLOPs efficient compared to classical MLP
based CNNs at the same accuracy level. The observed speed-up factor of 1.6-2.1× is not

so dramatic as we report in sections 4.1 and 4.2, but still substantial. We have not yet

implemented dedicated CUDA kernels for efficient inference of lmKAN-based convolutions.

Any type of convolution can be cast to a fully connected layer by the corresponding memory

manipulations, which we followed during fitting.

Ablations

Appendix F.4 contains ablation studies on 1) the effect of the number of grid

intervals G and 2) the effect of the strength of Hessian regularization λ.

8

16

32

64

Width

50

60

70

80

CIFAR

10

Test Accuracy (%)

Accuracy vs Hidden dimension

MLP CNN 1/4

MLP CNN 1/2

MLP CNN

lmKAN CNN

105

106

Inference FLOPs

50

60

70

80

2.1×

Accuracy vs Inference FLOPs

MLP CNN 1/4

MLP CNN 1/2

MLP CNN

lmKAN CNN

8

16

32

Base width

35

40

45

50

55

60

ImageNet

Val Top-5 Accuracy (%)

Accuracy vs Base width

lmKAN CNN

MLP CNN

MLP CNN 1/2

106

107

Inference FLOPs

35

40

45

50

55

60

1.7×

1.7×

Accuracy vs Inference FLOPs

lmKAN CNN

MLP CNN

MLP CNN 1/2

Figure 11: Comparison of the performance of standard MLP-based CNNs and lmKAN-based

CNNs on the CIFAR-10 and ImageNet datasets. The "MLP CNN 1/2" line corresponds to

the outcome of the fitting procedure with only half of the training steps compared to the

"MLP CNN" one.

4.3.2

ImageNet

To limit the computational cost, we downsampled the images to 81×81 (81 = 34) pixels. Our

backbone, illustrated in the right panel of Fig. 10, consists of four convolutional layers with

the 3× 3 kernel size and stride 3 and two fully connected layers. In contrast to the CIFAR-10

experiment, we progressively increase the number of filters as the spatial resolution of the

image decreases through the neural network. Our augmentation pipeline consists of the same

techniques as the ones we use for CIFAR-10, but with different hyperparameters; see more

details in Appendix F.5. Since the test subset is not publicly available, we use the validation

accuracy as the target metric. The performance of the models is summarized in the bottom

row of Fig. 11. The observed efficiency gains of 1.7× are in line with those for CIFAR-10.

15


!!! page 16 "Pozdnyakov_2025_lmKAN"

4.4

Comparison with FastKAN

We use the training script3 for the CIFAR-10 dataset available in the FastKAN GitHub

repository [56] as the basis for the comparison of lmKAN and FastKAN. However, we provide

several modifications to the pipeline.

The original script implements the fitting procedure of a fully connected FastKAN model on

the CIFAR-10 dataset without augmentations. The model has only one hidden layer with

256 neurons. Without augmentati ons, it overfits the data quickly. Thus, the very short

fitting procedure in the original script is sufficient.

We extend the script by the same augmentation pipeline as we used in Sec. 4.3 for the

CIFAR-10 dataset. We observed that because of augmentations, one has to fit the model for

a longer time, so the training budget was substantially increased. Additional changes are

detailed in Appendix F.6.

100

101

102

Parameters per function

(G + 1)2 for lmKAN

(num_grids + 1) for FastKAN

56

58

60

62

64

66

68

Test Accuracy (%)

lmKAN (2D) 1k

lmKAN (2D) 10k

FastKAN (1D) 1k

FastKAN (1D) 10k

MLP baseline 1k

MLP baseline 10k

Figure 12: Comparison of lmKAN and FastKAN within the fully connected framework on

the CIFAR-10 dataset. Both models were fit with 1k and 10k epochs.

These modifications significantly improve the performance of FastKAN models (54 −55%

validation accuracy in the original script), see Fig. 12. Furthermore, even the MLP baseline

of the same shape yields better accuracy compared to the performance of the FastKAN

model in the original script.

In this section, we systematically compare the performance of the lmKAN and FastKAN

models with the same backbone from the original FastKAN script. For each family of the

models, we vary the grid resolution and fit the models for one or ten thousand epochs each.

The comparison is given in Fig. 12.

The first observation is that the performance of FastKAN models degrades for excessively

fine grid resolutions. For the training budget of one thousand epochs, the final model is

even less accurate than the MLP baseline. For the ten thousand epochs, the effect is less

pronounced, but it still takes place. For lmKAN models, this degradation is much less severe,

if present at all.

The number of parameters per function scales quadratically with grid resolution for lmKANs

and linearly for FastKANs. Thus, although the rightmost lmKAN model in Fig. 12 uses

more parameters per function, it operates on a much coarser grid — only G = 16 grid

intervals per dimension, compared with num_grids = 200 for FastKANs. This suggests

that, for a comparable parameter budget per function, this coarser grid enforces a lower
frequency function class and, in turn, contributes to the superior training stability observed

for lmKANs.

Another distinct feature of Fig. 12 is that lmKANs achieve notably better accuracy compared

to FastKANs, even when the latter are evaluated with a very rich parametrization of inner

functions. Additionally, note that the number of trainable functions [Nin/2]Nout and NinNout

3https://github.com/ZiyaoLi/fast-kan/blob/master/examples/train_cifar10.py

16


!!! page 17 "Pozdnyakov_2025_lmKAN"

in an lmKAN and FastKAN layer, respectively. Thus, the same number of parameters per

function corresponds to a two times larger FastKAN model overall.

To conclude, these findings reinforce the intuitive considerations given in Sec. 3 and suggest

that building blocks of multivariate trainable functions are indeed more effective.

5

Limitations

Many of the difficulties arise when selecting an excessively high number of grid intervals G:

• When G is too large, lmKANs were found to be hard to converge.

• While the throughput does not depend on the grid resolution, both theoretically

and empirically, G still affects latency.

• Large G entails a large number of parameters; therefore, large models with fine grid

resolution have high memory requirements.

We have implemented CUDA kernels only for the full precision float32 data type. If using

data types such as bfloat16, the gains in efficiency are expected similarly to dense matrix

multiplications, but such kernels are yet to be implemented.

6

Summary

High-dimensional linear mappings are the cornerstone of modern deep learning, dominating

both the parameter count and the computational cost in most models. We introduce lookup

multivariate Kolmogorov-Arnold Networks (lmKANs) as a drop-in replacement that offers a

substantially better capacity–inference cost trade-off. Across all experiments, lmKANs were

Pareto-optimal in the inference FLOPs–performance plane. The efficiency gains are task
dependent: for general high-dimensional function approximation, modeled as a distillation

from a large ground-truth teacher MLP with random weights, lmKANs achieved up to

6× fewer FLOPs at matched accuracy. On randomly displaced methane configurations,

efficiency improved by up to 78×, or even more, for the Distances representation. Within

convolutional networks, the gains were smaller but still significant: 1.6–2.1× on CIFAR-10

and 1.7× on ImageNet.

Our CUDA kernels compete directly with highly optimized dense matrix multiplications—the

backbone of many numerical pipelines for decades. Even so, the gains were sufficient to

make lmKANs Pareto-optimal in H100 wall-clock time for both the general high-dimensional

function approximation and the methane dataset, achieving the speedup of more than an

order of magnitude in the latter case.

7

Acknowledgments

S.P. thanks Prashanth Kanduri, Nicholas J. Browning, and Henrique Mendonça for fruitful

discussions regarding CUDA, Bob Crovella, whose instrumental lectures are available online4,

and all the teachers of the CUDA course at Yandex School of Data Analysis.

S.P. acknowledges support from Intel and Merck KGaA via the AWASES programme. P.S.

acknowledges support from the NCCR Catalysis (grant number 225147), a National Centre

of Competence in Research funded by the Swiss National Science Foundation.

References

[1] Xiaohua Zhai, Alexander Kolesnikov, Neil Houlsby, and Lucas Beyer. Scaling vision

transformers. In Proceedings of the IEEE/CVF conference on computer vision and

pattern recognition, pages 12104–12113, 2022.

4https://www.youtube.com/playlist?list=PL6RdenZrxrw-zNX7uuGppWETdxt_JxdMj

17


!!! page 18 "Pozdnyakov_2025_lmKAN"

[2] Jared Kaplan, Sam McCandlish, Tom Henighan, Tom B Brown, Benjamin Chess, Rewon

Child, Scott Gray, Alec Radford, Jeffrey Wu, and Dario Amodei. Scaling laws for neural

language models. arXiv preprint arXiv:2001.08361, 2020.

[3] Sergey Ioffe and Christian Szegedy. Batch normalization: Accelerating deep network

training by reducing internal covariate shift. In International conference on machine

learning, pages 448–456. pmlr, 2015.

[4] Geoffrey E Hinton, Nitish Srivastava, Alex Krizhevsky, Ilya Sutskever, and Ruslan R

Salakhutdinov. Improving neural networks by preventing co-adaptation of feature

detectors. arXiv preprint arXiv:1207.0580, 2012.

[5] Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N

Gomez, Łukasz Kaiser, and Illia Polosukhin. Attention is all you need. Advances in

neural information processing systems, 30, 2017.

[6] Krzysztof Choromanski, Valerii Likhosherstov, David Dohan, Xingyou Song, Andreea

Gane, Tamas Sarlos, Peter Hawkins, Jared Davis, Afroz Mohiuddin, Lukasz Kaiser,

et al. Rethinking attention with performers. arXiv preprint arXiv:2009.14794, 2020.

[7] Jeffrey L Elman. Finding structure in time. Cognitive science, 14(2):179–211, 1990.

[8] Jie Zhou, Ganqu Cui, Shengding Hu, Zhengyan Zhang, Cheng Yang, Zhiyuan Liu,

Lifeng Wang, Changcheng Li, and Maosong Sun. Graph neural networks: A review of

methods and applications. AI open, 1:57–81, 2020.

[9] Yann LeCun, Léon Bottou, Yoshua Bengio, and Patrick Haffner. Gradient-based learning

applied to document recognition. Proceedings of the IEEE, 86(11):2278–2324, 2002.

[10] Alex Krizhevsky, Ilya Sutskever, and Geoffrey E Hinton. Imagenet classification with

deep convolutional neural networks. Advances in neural information processing systems,

25, 2012.

[11] Ziming Liu, Yixuan Wang, Sachin Vaidya, Fabian Ruehle, James Halverson, Marin

Soljačić, Thomas Y Hou, and Max Tegmark. Kan: Kolmogorov-arnold networks. arXiv

preprint arXiv:2404.19756, 2024.

[12] Ziyao Li. Kolmogorov-arnold networks are radial basis function networks. 2024.

[13] Andre˘ı Kolmogorov. On the representation of continuous functions of several variables

by superpositions of continuous functions of a smaller number of variables.

[14] Vladimir I Arnold. On functions of three variables. Collected Works: Representations

of Functions, Celestial Mechanics and KAM Theory, 1957–1965, pages 5–8, 2009.

[15] Federico Girosi and Tomaso Poggio.

Representation properties of networks: Kol
mogorov’s theorem is irrelevant. Neural Computation, 1(4):465–469, 1989.

[16] Johannes Schmidt-Hieber. The kolmogorov–arnold representation theorem revisited.

Neural networks, 137:119–126, 2021.

[17] Robert Hecht-Nielsen. Kolmogorov’s mapping neural network existence theorem. In

Proceedings of the international conference on Neural Networks, volume 3, pages 11–14.

IEEE press New York, NY, USA, 1987.

[18] Boris Igelnik and Neel Parikh. Kolmogorov’s spline network. IEEE transactions on

neural networks, 14(4):725–733, 2003.

[19] Xingyi Yang and Xinchao Wang. Kolmogorov-arnold transformer. arXiv preprint

arXiv:2409.10594, 2024.

[20] Akash Kundu, Aritra Sarkar, and Abhishek Sadhu. Kanqas: Kolmogorov-arnold network

for quantum architecture search. EPJ Quantum Technology, 11(1):76, 2024.

18


!!! page 19 "Pozdnyakov_2025_lmKAN"

[21] Ali Kashefi. Pointnet with kan versus pointnet with mlp for 3d classification and

segmentation of point sets. Computers & Graphics, page 104319, 2025.

[22] Runpeng Yu, Weihao Yu, and Xinchao Wang. Kan or mlp: A fairer comparison. arXiv

preprint arXiv:2407.16674, 2024.

[23] Shriyank Somvanshi, Syed Aaqib Javed, Md Monzurul Islam, Diwas Pandit, and Subasish

Das. A survey on kolmogorov-arnold network. ACM Computing Surveys, 2024.

[24] Tianrui Ji, Yuntian Hou, and Di Zhang. A comprehensive survey on kolmogorov arnold

networks (kan). arXiv preprint arXiv:2407.11075, 2024.

[25] Sidharth SS, Keerthana AR, Anas KP, et al. Chebyshev polynomial-based kolmogorov
arnold networks: An efficient architecture for nonlinear function approximation. arXiv

preprint arXiv:2405.07200, 2024.

[26] Jinfeng Xu, Zheyu Chen, Jinze Li, Shuo Yang, Wei Wang, Xiping Hu, and Edith C-H

Ngai. Fourierkan-gcf: Fourier kolmogorov-arnold network–an effective and efficient

feature transformation for graph collaborative filtering. arXiv preprint arXiv:2406.01034,

2024.

[27] Alireza Moradzadeh, Lukasz Wawrzyniak, Miles Macklin, and Saee G Paliwal. Ukan:

Unbound kolmogorov-arnold network accompanied with accelerated library. arXiv

preprint arXiv:2408.11200, 2024.

[28] Wei-Hsing Huang, Jianwei Jia, Yuyao Kong, Faaiq Waqar, Tai-Hao Wen, Meng-Fan

Chang, and Shimeng Yu. Hardware acceleration of kolmogorov-arnold network (kan)

for lightweight edge inference. In Proceedings of the 30th Asia and South Pacific Design

Automation Conference, pages 693–699, 2025.

[29] Michael Poluektov and Andrew Polar. Construction of the kolmogorov-arnold networks

using the newton-kaczmarz method. Machine Learning, 114(8):185, 2025.

[30] Andrew Polar and Michael Poluektov. A deep machine learning algorithm for construc
tion of the kolmogorov–arnold representation. Engineering Applications of Artificial

Intelligence, 99:104137, 2021.

[31] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. Deep residual learning

for image recognition. In Proceedings of the IEEE conference on computer vision and

pattern recognition, pages 770–778, 2016.

[32] Carl De Boor and Carl De Boor. A practical guide to splines, volume 27. springer New

York, 1978.

[33] Carl De Boor. On uniform approximation by splines. J. Approx. Theory, 1(1):219–235,

1968.

[34] Xavier Glorot, Antoine Bordes, and Yoshua Bengio. Deep sparse rectifier neural networks.

In Proceedings of the fourteenth international conference on artificial intelligence and

statistics, pages 315–323. JMLR Workshop and Conference Proceedings, 2011.

[35] Vasily Volkov and James W Demmel. Benchmarking gpus to tune dense linear algebra.

In SC’08: Proceedings of the 2008 ACM/IEEE conference on Supercomputing, pages

1–11. IEEE, 2008.

[36] Stephen R Xie, Matthias Rupp, and Richard G Hennig. Ultra-fast interpretable machine
learning potentials. npj Computational Materials, 9(1):162, 2023.

[37] Nitish Srivastava, Geoffrey Hinton, Alex Krizhevsky, Ilya Sutskever, and Ruslan Salakhut
dinov. Dropout: a simple way to prevent neural networks from overfitting. The journal

of machine learning research, 15(1):1929–1958, 2014.

[38] George Cybenko. Approximation by superpositions of a sigmoidal function. Mathematics

of control, signals and systems, 2(4):303–314, 1989.

19


!!! page 20 "Pozdnyakov_2025_lmKAN"

[39] Diederik P Kingma and Jimmy Ba. Adam: A method for stochastic optimization. arXiv

preprint arXiv:1412.6980, 2014.

[40] Kaggle.

Titanic — machine learning from disaster.

https://www.kaggle.com/

competitions/titanic. Accessed 2025-08-19.

[41] David Harrison Jr and Daniel L Rubinfeld. Hedonic housing prices and the demand for

clean air. Journal of environmental economics and management, 5(1):81–102, 1978.

[42] Sergey N Pozdnyakov, Michael J Willatt, Albert P Bartók, Christoph Ortner, Gábor

Csányi, and Michele Ceriotti.

Incompleteness of atomic structure representations.

Physical Review Letters, 125(16):166001, 2020.

[43] Justin M Turney, Andrew C Simmonett, Robert M Parrish, Edward G Hohenstein,

Francesco A Evangelista, Justin T Fermann, Benjamin J Mintz, Lori A Burns, Jeremiah J

Wilke, Micah L Abrams, et al. Psi4: an open-source ab initio electronic structure program.

Wiley Interdisciplinary Reviews: Computational Molecular Science, 2(4):556–565, 2012.

[44] Walter Kohn and Lu Jeu Sham. Self-consistent equations including exchange and

correlation effects. Physical review, 140(4A):A1133, 1965.

[45] Jörg Behler and Michele Parrinello.

Generalized neural-network representation of

high-dimensional potential-energy surfaces. Physical review letters, 98(14):146401, 2007.

[46] Albert P Bartók, Mike C Payne, Risi Kondor, and Gábor Csányi. Gaussian approxima
tion potentials: The accuracy of quantum mechanics, without the electrons. Physical

review letters, 104(13):136403, 2010.

[47] Alice EA Allen, Geneviève Dusson, Christoph Ortner, and Gábor Csányi. Atomic per
mutationally invariant polynomials for fitting molecular force fields. Machine Learning:

Science and Technology, 2(2):025017, 2021.

[48] Yaolong Zhang, Junfan Xia, and Bin Jiang. Physically motivated recursively embedded

atom neural networks: incorporating local completeness and nonlocality. Physical

Review Letters, 127(15):156002, 2021.

[49] Sergey Pozdnyakov and Michele Ceriotti. Smooth, exact rotational symmetrization for

deep learning on point clouds. Advances in Neural Information Processing Systems, 36:

79469–79501, 2023.

[50] Alexander Dylan Bodner, Antonio Santiago Tepsich, Jack Natan Spolski, and Santiago

Pourteau. Convolutional kolmogorov-arnold networks. arXiv preprint arXiv:2406.13155,

2024.

[51] Alex Krizhevsky, Geoffrey Hinton, et al. Learning multiple layers of features from tiny

images. 2009.

[52] Jia Deng, Wei Dong, Richard Socher, Li-Jia Li, Kai Li, and Li Fei-Fei. Imagenet: A

large-scale hierarchical image database. In 2009 IEEE conference on computer vision

and pattern recognition, pages 248–255. Ieee, 2009.

[53] Ekin D Cubuk, Barret Zoph, Jonathon Shlens, and Quoc V Le. Randaugment: Practical

automated data augmentation with a reduced search space. In Proceedings of the

IEEE/CVF conference on computer vision and pattern recognition workshops, pages

702–703, 2020.

[54] Hongyi Zhang, Moustapha Cisse, Yann N Dauphin, and David Lopez-Paz. mixup:

Beyond empirical risk minimization. arXiv preprint arXiv:1710.09412, 2017.

[55] Sangdoo Yun, Dongyoon Han, Seong Joon Oh, Sanghyuk Chun, Junsuk Choe, and

Youngjoon Yoo.

Cutmix: Regularization strategy to train strong classifiers with

localizable features. In Proceedings of the IEEE/CVF international conference on

computer vision, pages 6023–6032, 2019.

20


!!! page 21 "Pozdnyakov_2025_lmKAN"

[56] Ziyao Li. fast-kan: Fastkan — very fast implementation of kolmogorov–arnold networks

(kan). https://github.com/ZiyaoLi/fast-kan, 2024. GitHub repository.

[57] Yoshua Bengio, Nicholas Léonard, and Aaron Courville. Estimating or propagating

gradients through stochastic neurons for conditional computation.

arXiv preprint

arXiv:1308.3432, 2013.

[58] Emmanuel Bengio, Pierre-Luc Bacon, Joelle Pineau, and Doina Precup. Conditional

computation in neural networks for faster models. arXiv preprint arXiv:1511.06297,

2015.

[59] Robert A Jacobs, Michael I Jordan, Steven J Nowlan, and Geoffrey E Hinton. Adaptive

mixtures of local experts. Neural computation, 3(1):79–87, 1991.

[60] Noam Shazeer, Azalia Mirhoseini, Krzysztof Maziarz, Andy Davis, Quoc Le, Geoffrey

Hinton, and Jeff Dean. Outrageously large neural networks: The sparsely-gated mixture
of-experts layer. arXiv preprint arXiv:1701.06538, 2017.

[61] William Fedus, Barret Zoph, and Noam Shazeer. Switch transformers: Scaling to trillion

parameter models with simple and efficient sparsity. Journal of Machine Learning

Research, 23(120):1–39, 2022.

[62] Shenlong Wang, Simon Suo, Wei-Chiu Ma, Andrei Pokrovsky, and Raquel Urtasun.

Deep parametric continuous convolutional neural networks. In Proceedings of the IEEE

conference on computer vision and pattern recognition, pages 2589–2597, 2018.

[63] Ilyes Batatia, David P Kovacs, Gregor Simm, Christoph Ortner, and Gábor Csányi.

Mace: Higher order equivariant message passing neural networks for fast and accurate

force fields. Advances in neural information processing systems, 35:11423–11436, 2022.

[64] Sergey Pozdnyakov, Artem R Oganov, Efim Mazhnik, Arslan Mazitov, and Ivan Kruglov.

Fast general two-and three-body interatomic potential. Physical Review B, 107(12):

125160, 2023.

[65] Harm Derksen and Gregor Kemper. Computational invariant theory. Springer, 2015.

[66] Ilya Loshchilov and Frank Hutter. Sgdr: Stochastic gradient descent with warm restarts.

arXiv preprint arXiv:1608.03983, 2016.

21


!!! page 22 "Pozdnyakov_2025_lmKAN"

A

Additional related work

In this appendix, we review further related work beyond Kolmogorov-Arnold Networks.

Conditional computations

The proposed lookup multivariate Kolmogorov-Arnold Net
works fit within the general idea of conditional computation [57, 58], which suggests using

only part of a model’s parameters at inference time. The most popular subclass of such

architectures is the Mixture-of-Experts (MoE) family [59–61], in which multiple experts,

typically implemented as MLPs, process the current input only if they are deemed relevant.

In the proposed method, the spline lookup tables enable O(1) computations, which underpin

the observed efficiency of our approach. For a function parametrized in this way, its value at

any given point depends only on the small subset of parameters that control the function’s

behavior within the corresponding grid interval; all other parameters remain inactive, similarly

to other conditional-computation methods.

Whereas our method can be loosely characterized as performing low-level "weight lookup,"

classical MoE models can be viewed as performing high-level "expert lookup." In these models,

entire experts—typically full MLPs—or at least entire layers are either active or inactive

as a whole. In general, such high-level approaches dominate the landscape of conditional
computation models, while low-level ones are very rare, likely due to the challenges associated

with efficient GPU implementation.

Spline lookup tables

Outside the scope of general high-dimensional mappings, spline

lookup tables have found several applications in machine learning. For instance, Graph

Neural Networks (GNNs) applied to point clouds in Euclidean space [62] often have trainable

filters as part of the model. Such filters are one- or three-dimensional functions whose inputs

are inter-point distances or displacement vectors. Sometimes these functions are splined [63]

post-hoc, after the fitting of the model is finished.

In a more niche case, certain physics-inspired machine learning models can be parametrized

exclusively by low-dimensional functions. For such setups, Pozdnyakov et al. [64] and Xie

et al. [36] pushed the boundary of efficiency by applying B-spline techniques similarly to this

work.

B

More details on function parametrization

The σ(x) function

Section 3.1 of the main text describes the construction of the static

percentile grid used in the parametrization of all the functions lmKAN consists of. This

construction involves any sigmoid-like function σ(x), and, as was discussed in the main text,

it makes sense to shape it reasonably close to cumulative normal distribution to distribute

function arguments x evenly across grid intervals.

It is, however, computationally expensive to use the exact cumulative distribution function

of the normal distribution. Thus, we use a fast approximation, which is given in Eq. 4 and is

illustrated in Fig. 13.

This construction is cheap to compute because the computational pipeline consists of a single

exponential call and a few arithmetic operations, as elaborated in algorithm 2.

Algorithm 2 Evaluation of σ(x) with a single exponential call

Input: x ∈R

Output: σ(x)

1: t ←exp

 −|x|



▷compute expensive exponential only once

2: if x > 0 then

3:

σ(x) ←1 −0.5 t

4: else

5:

σ(x) ←0.5 t

6: end if

7: return σ(x)

22


!!! page 23 "Pozdnyakov_2025_lmKAN"

σ(x) =

(0.5 ex,

x ≤0,

1 −0.5 e−x,

x > 0.

(4)

4

2

0

2

4

x

0.0

0.2

0.4

0.6

0.8

1.0

(x)

Figure 13: Plot of the σ(x) function de
fined in Eq. 4.

Edge cases

Section 3.1 of the main text introduced static percentile grids and the corre
sponding basis of second-order B-splines. For a grid with G intervals and G −1 grid points,

there are G + 1 basis functions, out of which G −1 are given by second-order B-splines

centered around all grid points, as illustrated in the right panel of Fig. 3 of the main text.

The other two are given as linear functions on the left-most and right-most infinite intervals.

The second-order B-splines given in the right panel of Fig. 3 are defined to linearly increase

from 0 to 1 from the left grid point to the central one and then linearly decrease from 1 to 0

from the central grid point to the right grid point. This construction is well-defined for all

the inner grid points but requires additional definitions for the B-splines centered around

the left-most and right-most grid points, as these do not have left and right neighboring grid

points, respectively.

In order to define these edge B-splines, we introduce ’ghost’ left and right grid points. The

position of the left ghost point is given as G[0] −(G[1] −G[0]), where G[0] and G[1] are

the positions of left-most and second left-most grid points respectively. The right ghost

point is defined similarly. With such a notation of additional grid points, we can define edge

B-splines similarly to all the others.

Finally, there are two linear basis functions on the left-most and right-most infinite intervals.

We define them to be zeros in the left-most and right-most grid points, linearly increasing to

ones at the left and right ghost points and continuing to left and right infinities with the

same slope, respectively.

Difference between the direct use of the static percentile grid and the uniform

one with pre-normalization by σ(x)

A reader may ask themselves a question of what is

the difference between the proposed construction involving a function f(x) defined on static

percentile grid on (−∞, ∞) and a more simple approach which involves first mapping of an

input to (0, 1) by x′ = σ(x), and then computing a piecewise linear function g(x′) defined on

a uniform grid on [0, 1].

The answer is that the resulting functions in the initial space, f(x) and f ′(x) = g(σ(x)), are

not identical. Specifically, f ′(x) is no longer piecewise linear on each grid interval, with the

most notable difference being the behavior when x →±∞. Asymptotes of f(x) are linear,

while asymptotes of f′(x) are constant.

The concern with horizontal asymptotes is that they can cause the vanishing gradient

problem, which is believed to be one of the reasons why the ReLU [34] activations work

better than tanh. Given these considerations, we chose the direct application of the static

percentile grid for practical implementation.

B.1

Standalone two-dimensional function computation

Algorithm 3 provides a recipe to compute a standalone two-dimensional function given our

parametrization scheme. See discussion in Sec. 3.1 of the main text.

23


!!! page 24 "Pozdnyakov_2025_lmKAN"

Algorithm 3 O(1) evaluation of a standalone 2D lmKAN function. Red lines indicate

computations that can be reused when computing many 2D functions for the same arguments,

while green lines indicate computations that have to be repeated for each 2D function.

Input: scalars x1, x2 ∈R; grid points G; parameters P ∈R[G+1,G+1]

P[ i1, i2 ] stores the function value on the (i1, i2)-th grid point

Output: output y ∈R

1: function Eval2D(x1, x2) ▷Handling of edge-interval cases described above is omitted

for brevity.

2:

i1 ←



σ(x1) G



3:

i2 ←



σ(x2) G



4:

Bi1 i2(x1, x2) ←

G[i1 + 1] −x1

G[i1 + 1] −G[i1]

G[i2 + 1] −x2

G[i2 + 1] −G[i2]

5:

Bi1+1 i2(x1, x2) ←

x1 −G[i1]

G[i1 + 1] −G[i1]

G[i2 + 1] −x2

G[i2 + 1] −G[i2]

6:

Bi1 i2+1(x1, x2) ←

G[i1 + 1] −x1

G[i1 + 1] −G[i1]

x2 −G[i2]

G[i2 + 1] −G[i2]

7:

Bi1+1 i2+1(x1, x2) ←

x1 −G[i1]

G[i1 + 1] −G[i1]

x2 −G[i2]

G[i2 + 1] −G[i2]

8:

y ←0

9:

y += Bi1 i2(x1, x2) P[ i1, i2 ]

10:

y += Bi1+1 i2(x1, x2) P[ i1+1, i2 ]

11:

y += Bi1 i2+1(x1, x2) P[ i1, i2+1 ]

12:

y += Bi1+1 i2+1(x1, x2) P[ i1+1, i2+1 ]

13:

return y

14: end function

C

More details on Hessian regularization

Sec. 3.5 of the main text introduced the concept of off-diagonal Hessian regularization

which is based on finite difference schemes for squared Frobenius norm of the Hessian. This

appendix provides the exact equations we use in our implementation.

We use the following finite-differences approximation for the second derivative with respect

to x1:

∂2f

∂x2

1

(x1,x2)

≈2

 hℓf(x1 + hr, x2) −(hℓ+ hr) f(x1, x2) + hr f(x1 −hℓ, x2)



hℓhr (hℓ+ hr)

,

(5)

where hl is the spacing between left and central grid points, while hr is the spacing between

central and right grid points. The corresponding expression in terms of the coefficients pi,j

is given as:

Dx1,x1;i,j =

2



hi pi+1,j −(hi + hi+1) pi,j + hi+1 pi−1,j



hi hi+1 (hi + hi+1)

(6)

For the second derivative with respect to x2 we use an analogous expression:

∂2f

∂x2

2

(x1,x2)

≈

2



hb f(x1, x2 + hu) −(hb + hu) f(x1, x2) + hu f(x1, x2 −hb)



hb hu (hb + hu)

,

(7)

where hu and hb are upper and bottom spacings, respectively.

Dx2,x2;i,j =

2



hj pi,j+1 −(hj + hj+1) pi,j + hj+1 pi,j−1



hj hj+1 (hj + hj+1)

(8)

24


!!! page 25 "Pozdnyakov_2025_lmKAN"

For the mixed derivative, our finite-differences scheme is the following:

∂2f

∂x1 ∂x2

(x1,x2)

≈

f(x1 + hr, x2 + hp) −f(x1 + hr, x2 −hb) −f(x1 −hl, x2 + hp) + f(x1 −hl, x2 −hb)

(hr + hl) (hp + hb)

(9)

Dx1,x2;i,j =pi+1,j+1 −pi+1,j−1 −pi−1,j+1 + pi−1,j−1

(hi + hi+1) (hj + hj+1)

(10)

The final regularization term is the following:

Hi,j = D2

x1,x1;i,j + 2D2

x1,x2;i,j + D2

x2,x2;i,j.

(11)

In order to compute the total regularization term for the whole model, we 1) average Hi,j

across all the grid points and 2) summate these values across all the 2D functions within all

the lmKAN layers in the model.

D

CUDA kernels

The performance of our CUDA kernels with 16x16 tile size in the limit of large dimensions

is summarized in Fig. 14. All the lmKAN curves are computed with the largest number of

grid intervals G = 20 available for the 16x16 tile size. We compare the inference efficiency of

lmKAN and linear layers. On the left panel, we normalize time by the shape of the layers.

Fig. 14 illustrates a clear convergence of these normalized times to the same value for all

the dimensions. In the limit of large batch sizes, the forward pass of a lmKAN layer is ~8x

slower compared to a linear layer with the same shape. At the same time, a lmKAN layer

contains a significantly larger number of parameters than a linear layer of the same shape.

Thus, inference time per parameter is significantly better for lmKAN layers, about 27 times,

as illustrated on the right panel of Fig. 14.

211

213

215

217

219

Batch size

10

13

10

12

10

11

time / (batch_size * Nin * Nout), seconds

Nin = Nout = 256

Nin = Nout = 512

Nin = Nout = 1024

Nin = Nout = 2048

lmKAN

Linear

211

213

215

217

219

Batch size

10

14

10

13

time / (batch_size * #parameters), seconds

Nin = Nout = 256

Nin = Nout = 512

Nin = Nout = 1024

Nin = Nout = 2048

lmKAN

Linear

Figure 14: The performance of our CUDA kernels on the H100 SXM GPU in comparison

with the linear layer in the limit of large dimensions. Left panel - time normalized by shape.

Right panel - time normalized by the number of parameters.

Fig. 15 is an analogous illustration but for small dimensions - 16 and 32. Our CUDA kernels

are better adjusted for such small dimensions, and thus, relative performance compared to

linear layers is even higher in this case.

Finally, Fig. 16 illustrates the inference efficiency depending on the number of grid intervals

G, which control the number of parameters. The time indeed does not depend on G in the

large batch size limit.

25


!!! page 26 "Pozdnyakov_2025_lmKAN"

216

218

220

222

224

226

228

Batch size

10

13

10

12

10

11

10

10

time / (batch_size * Nin * Nout), seconds

Nin = Nout = 16

Nin = Nout = 32

lmKAN

Linear

216

218

220

222

224

226

228

Batch size

10

14

10

13

10

12

time / (batch_size * #parameters), seconds

Nin = Nout = 16

Nin = Nout = 32

lmKAN

Linear

Figure 15: The performance of our CUDA kernels on the H100 SXM GPU in comparison

with the linear layer for small dimensions. Left panel - time normalized by shape. Right

panel - time normalized by the number of parameters.

211

213

215

217

219

Batch size

10

12

3 × 10

13

4 × 10

13

6 × 10

13

2 × 10

12

time / (batch_size * Nin * Nout), seconds

Ni = 3

Ni = 4

Ni = 6

Ni = 8

Ni = 10

Ni = 12

Ni = 16

Ni = 20

Figure 16: Inference efficiency of an lmKAN layer depending on the number of grid intervals

G.

E

Preconditioning and fitting scheme

The first thing we attempted upon implementing the CUDA kernels was to fit a model

with the highest grid resolution, G = 40, supported for the 8 × 8 tile on the H100 GPU. In

this setup, each 2D function had as many as 412 = 1681 trainable parameters. We found

that the training was unstable, so we designed a preconditioning and multi-stage fitting

pipeline to stabilize it, which ended up being rather sophisticated. We employed this pipeline

consistently for all our experiments.

The subsequent evidence revealed that lmKANs (similarly to KANs) are progressively harder

to fit as grid resolution increases. In other words, our very first experiment was the most

challenging one. At more moderate grid resolutions, preconditioning measures can likely be

simplified, if not omitted altogether. Specifically, we think that a fitting scheme omitting

additional preconditioning terms, but preserving the Hessian regularization decay phase,

which is described in the following, could be effective. With that, below is the description of

the current pipeline.

E.1

Preconditioning

We precondition lmKAN layers by adding linear terms into the overall functional form. We

use one of the following:

26


!!! page 27 "Pozdnyakov_2025_lmKAN"

y = γ lmKAN(x) + ReLU

 Linear(x)



(12a)

y = γ lmKAN(x) + Linear

 ReLU(x)



(12b)

where the lmKAN weight, γ, is initially set to 0 and then gradually increased in our

multistaged fitting procedure described later. In the case of ReLU-last preconditioning of

Eq. 12a, we insert ReLU into all the layers except the last one; for ReLU-first preconditioning

of Eq. 12b, we insert ReLU into all the layers except the first one. Therefore, at the beginning,

when the lmKAN weight is zero, the model is equivalent to a pure MLP-based one for both

types of preconditioning.

A merit of ReLU-first preconditioning is that during inference the whole Eq. 12b can be

absorbed into a single lmKAN layer whenever the number of grid intervals G is even, that is,

when the origin is one of the grid points, see more details in Appendix F.1. Thus, this type

of preconditioning does not increase inference cost in any way. This is an advantage over the

original KAN preconditioning scheme [11], which requires the additional computation of the

computationally expensive transcendental function SiLU for each edge at inference.

Because of the possibility of such an absorption, the total inference FLOPs of a ReLU-first

preconditioned lmKAN layer is 2× those of a linear layer of the same shape, while for the

ReLU-last preconditioning, the slowdown factor is 3×, taking into account the linear branch.

E.2

Fitting procedure

Our fitting scheme consists of several phases:

Phase I - pure MLP: γ is set to 0, so the whole architecture is operating in pure MLP

mode. This part is typically very short.

Phase II - turning on lmKAN: γ is linearly (over time) increased from 0 to 0.3. After

that, there is some part with the constant γ = 0.3. At this phase, we use very strong (=

with a very high coefficient λ) Hessian regularization introduced in Appendix C. For all

the subsequent phases, lmKAN weight γ is fixed at 0.3. The pipeline is also stable if γ is

increased to 1.0, but in a few experiments we found that using 0.3 value leads to slightly

better final accuracy.

Phase III - Hessian regularization decay: At this phase, we gradually decay the

strength of the Hessian regularization λ from the initial very high value to the target value

if this regularization is intended to be utilized in this fitting procedure and to nearly zero

otherwise.

Phase IV - Main lmKAN fitting part: In this final phase, we keep Hessian regularization

to be constant at the value reached in the previous phase. The model is fit with the given

learning rate schedule. In the experiments in this work, we use a constant learning rate for

the most part of this phase, and step or exponential learning rate decay at the end.

An example of the described fitting procedure for one of the training runs we did for numerical

experiments described in Sec. 4.1 of the main text and in the Appendix F.2 is given in

Fig. 17.

27


!!! page 28 "Pozdnyakov_2025_lmKAN"

4.6 × 10

1

4.8 × 10

1

5 × 10

1

5.2 × 10

1

5.4 × 10

1

5.6 × 10

1

5.8 × 10

1

6 × 10

1

Loss

Total Loss (ESA)

Pure Loss (MSE, ESA)

0.00

0.05

0.10

0.15

0.20

0.25

0.30

lmKAN weight

10

18

10

15

10

12

10

9

10

6

10

3

Hessian regularization

103

104

105

106

Training Steps

10

5

10

4

10

3

Learning Rate

Figure 17: The multi-staged fitting procedure we use. Total loss indicates the full loss,

including the Hessian regularization term. Pure loss is only the MSE part. For clarity, we

plot exponential sliding averages of losses. Note that the horizontal scale is logarithmic. If it

is linear, the first couple of phases are hard to discern as they are very short. The fourth

phase takes most of the training budget. This training run corresponds to the unregularized

lmKAN, where Hessian regularization is turned on only at the beginning of the fitting to

ensure stability. At the end of phase III, it reaches nearly zero value, which, in this case, is

10−20.

28


!!! page 29 "Pozdnyakov_2025_lmKAN"

E.3

Comparison of the preconditioning schemes

8

16

32

64

Hidden dimension

50

55

60

65

70

75

80

Test Accuracy (%)

Accuracy vs Hidden dimension

MLP CNN 1/4

MLP CNN 1/2

MLP CNN

lmKAN CNN ReLU-last

lmKAN CNN ReLU-first

105

106

Inference FLOPs

Accuracy vs Inference FLOPs

MLP CNN 1/4

MLP CNN 1/2

MLP CNN

lmKAN CNN ReLU-last

lmKAN CNN ReLU-first

Figure 18: Comparison of the preconditioning schemes when fitting lmKANs on the CIFAR
10 dataset.

5 × 10

1

6 × 10

1

32

1

MSE

MSE vs Hidden dimension

MLP 1/2

MLP

lmKAN ReLU-last

lmKAN ReLU-first

MSE vs Inference FLOPs

MLP 1/2

MLP

lmKAN ReLU-last

lmKAN ReLU-first

MSE vs Inverse H100 SXM throughput

MLP 1/2

MLP

lmKAN ReLU-last

lmKAN ReLU-first

32

64

128

256

512

1024

Hidden dimension

6 × 10

1

7 × 10

1

8 × 10

1

32

32

MSE

MLP 1/2

MLP

lmKAN ReLU-last

lmKAN ReLU-first

104

105

106

Inference FLOPs

MLP 1/2

MLP

lmKAN ReLU-last

lmKAN ReLU-first

10

9

10

8

H100 SXM seconds/input

(large batch size)

MLP 1/2

MLP

lmKAN ReLU-last

lmKAN ReLU-first

Figure 19: Comparison of the preconditioning schemes when fitting lmKANs within general

function approximation setup.

We fitted lmKAN models with both types of preconditioning for the CIFAR-10 dataset and

for general function approximation. The results are given in Fig. 18 and Fig. 19. Overall,

the ReLU-last type of preconditioning appeared to lead to slightly more accurate models,

but this small gain in accuracy does not justify additional computational cost.

When designing some of our experiments we did not know this yet. Therefore, some of them

use the ReLU-last type of preconditioning.

We use the ReLU-last type of preconditioning for figures 7, 9, 21, and 22. We use the

ReLU-first type of preconditioning for figures 6, 11, 12, 23, and 24.

In other words, the performance of lmKANs on the methane datasets can likely be further

improved by switching from the ReLU-last type of preconditioning to the ReLU-first one.

However, since the observed gains in efficiency are already more than an order of magnitude

in terms of the H100 wall-clock time, we left this for future work.

29


!!! page 30 "Pozdnyakov_2025_lmKAN"

F

Experiments

F.1

General details about the benchmarking protocols

Within the scope of this work, we primarily focus on the saturated throughput in the limit

of large batch sizes. Thus, we benchmark all the models for progressively large batch sizes

until reaching saturation. All the models are benchmarked with 10 warm-up dry runs, and

20 timed runs. Overall, we tried to optimize each model as much as possible while staying

within the limits of full precision float32 data type.

MLPs employed in this work consist of three types of layers - linear ones, ReLU activations,

and batch normalizations. At inference, batch normalizations simply perform elementwise

linear transformation and thus can be absorbed into the weights of linear layers. We perform

this operation manually and, on top of that, compile the model with the torch_tensorrt

backend (with disabling tf32 to ensure full precision float32). We use the same compilation

strategy for FastKANs.

For lmKANs, when using ReLU-first preconditioning (see more details in Appendix E), we

absorb all the expression in Eq. 12b into the weights of the lmKAN layer. This modification

requires updating the lmKAN 2D functions as f(x1, x2) ←γf(x1, x2) + w1ReLU(x1) +

w2ReLU(x2). Our construction allows this absorption to be done exactly whenever the origin

is one of the grid points, which, in turn, is the case when the number of grid intervals G

is even. On top of that, batch normalizations are absorbed similarly to MLPs. We do not

compile lmKAN models.

For lmKAN models with the ReLU-last preconditioning we absorb only the lmKAN weight

γ.

F.2

General Function Approximation

The performance of lmKANs when approximating a R32 →R32 function generated similarly

as the R32 →R1 described in the main text is given in Fig. 20.

32

64

128

256

512

1024

Hidden dimension

6 × 10

1

7 × 10

1

8 × 10

1

Mean Squared Error

MSE vs Hidden dimension

MLP 1/2

MLP

lmKAN

104

105

106

Inference FLOPs

4.2×

MSE vs Inference FLOPs

MLP 1/2

MLP

lmKAN

10

9

10

8

H100 SXM seconds/input

(large batch size)

1.3×

MSE vs Inverse H100 SXM throughput

MLP 1/2

MLP

lmKAN

Figure 20: lmKAN vs MLP for general, R32 →R32, function approximation. The "MLP

1/2" line corresponds to the outcome of the fitting procedure with only half of the training

steps compared to the "MLP" one.

There is a trend that the relative performance of lmKANs improves with the scale. It is

clearly seen on the MSE vs FLOPs panel. On the MSE vs H100 wall-clock time panel, it is

first masked by the non-homogeneous efficiency of the code, but next still reveals itself for

the largest hidden dimensions.

F.3

Methane

F.3.1

The Distances Polynomials representation

It was mentioned in Sec. 4.2 of the main text that the representation Distances Polynomials

is given by non-trivial invariant polynomials computed on top of interatomic distances. These

polynomials are constant with respect to changing the order of identical hydrogen atoms.

30


!!! page 31 "Pozdnyakov_2025_lmKAN"

P1 = x5 + x6 + x7 + x8 + x9 + x10

P2 = x1 + x2 + x3 + x4

P3 = x2

5 + x2

6 + x2

7 + x2

8 + x2

9 + x2

10

P4 = x5x6 + x5x7 + x6x7 + x5x8 + x6x8 + x5x9 + x7x9 + x8x9+

x6x10 + x7x10 + x8x10 + x9x10

P5 = x1x5 + x2x5 + x1x6 + x3x6 + x1x7 + x4x7 + x2x8 + x3x8+

x2x9 + x4x9 + x3x10 + x4x10

P6 = x2

1 + x2

2 + x2

3 + x2

4

P7 = x3

5 + x3

6 + x3

7 + x3

8 + x3

9 + x3

10

P8 = x2

5x6 + x5x2

6 + x2

5x7 + x2

6x7 + x5x2

7 + x6x2

7 + x2

5x8 + x2

6x8+

x5x2

8 + x6x2

8 + x2

5x9 + x2

7x9 + x2

8x9 + x5x2

9 + x7x2

9 + x8x2

9+

x2

6x10 + x2

7x10 + x2

8x10 + x2

9x10 + x6x2

10 + x7x2

10 + x8x2

10 + x9x2

10

P9 = x1x2

5 + x2x2

5 + x1x2

6 + x3x2

6 + x1x2

7 + x4x2

7 + x2x2

8 + x3x2

8+

x2x2

9 + x4x2

9 + x3x2

10 + x4x2

10

P10 = x5x6x8 + x5x7x9 + x6x7x10 + x8x9x10

P11 = x1x5x6 + x1x5x7 + x1x6x7 + x2x5x8 + x3x6x8 + x2x5x9 + x4x7x9 + x2x8x9+

x3x6x10 + x4x7x10 + x3x8x10 + x4x9x10

P12 = x2

1x5 + x2

2x5 + x2

1x6 + x2

3x6 + x2

1x7 + x2

4x7 + x2

2x8 + x2

3x8+

x2

2x9 + x2

4x9 + x2

3x10 + x2

4x10

P13 = x1x2x5 + x1x3x6 + x1x4x7 + x2x3x8 + x2x4x9 + x3x4x10

P14 = x3

1 + x3

2 + x3

3 + x3

4

P15 = x4

5 + x4

6 + x4

7 + x4

8 + x4

9 + x4

10

P16 = x3

5x6 + x5x3

6 + x3

5x7 + x3

6x7 + x5x3

7 + x6x3

7 + x3

5x8 + x3

6x8+

x5x3

8 + x6x3

8 + x3

5x9 + x3

7x9 + x3

8x9 + x5x3

9 + x7x3

9 + x8x3

9+

x3

6x10 + x3

7x10 + x3

8x10 + x3

9x10 + x6x3

10 + x7x3

10 + x8x3

10 + x9x3

10

P17 = x1x3

5 + x2x3

5 + x1x3

6 + x3x3

6 + x1x3

7 + x4x3

7 + x2x3

8 + x3x3

8+

x2x3

9 + x4x3

9 + x3x3

10 + x4x3

10

P18 = x1x2

5x6 + x1x5x2

6 + x1x2

5x7 + x1x2

6x7 + x1x5x2

7 + x1x6x2

7 + x2x2

5x8 + x3x2

6x8+

x2x5x2

8 + x3x6x2

8 + x2x2

5x9 + x4x2

7x9 + x2x2

8x9 + x2x5x2

9 + x4x7x2

9 + x2x8x2

9+

x3x2

6x10 + x4x2

7x10 + x3x2

8x10 + x4x2

9x10 + x3x6x2

10 + x4x7x2

10 + x3x8x2

10 + x4x9x2

10

P19 = x2x2

5x6 + x3x5x2

6 + x2x2

5x7 + x3x2

6x7 + x4x5x2

7 + x4x6x2

7 + x1x2

5x8 + x1x2

6x8+

x3x5x2

8 + x2x6x2

8 + x1x2

5x9 + x1x2

7x9 + x3x2

8x9 + x4x5x2

9 + x2x7x2

9 + x4x8x2

9+

x1x2

6x10 + x1x2

7x10 + x2x2

8x10 + x2x2

9x10 + x4x6x2

10 + x3x7x2

10 + x4x8x2

10 + x3x9x2

10

P20 = x2

1x2

5 + x2

2x2

5 + x2

1x2

6 + x2

3x2

6 + x2

1x2

7 + x2

4x2

7 + x2

2x2

8 + x2

3x2

8+

x2

2x2

9 + x2

4x2

9 + x2

3x2

10 + x2

4x2

10

(13)

31


!!! page 32 "Pozdnyakov_2025_lmKAN"

P21 = x1x2x2

5 + x1x3x2

6 + x1x4x2

7 + x2x3x2

8 + x2x4x2

9 + x3x4x2

10

P22 = x2

1x5x6 + x2

1x5x7 + x2

1x6x7 + x2

2x5x8 + x2

3x6x8 + x2

2x5x9 + x2

4x7x9 + x2

2x8x9+

x2

3x6x10 + x2

4x7x10 + x2

3x8x10 + x2

4x9x10

P23 = x3

1x5 + x3

2x5 + x3

1x6 + x3

3x6 + x3

1x7 + x3

4x7 + x3

2x8 + x3

3x8+

x3

2x9 + x3

4x9 + x3

3x10 + x3

4x10

P24 = x4

1 + x4

2 + x4

3 + x4

4

P25 = x5

5 + x5

6 + x5

7 + x5

8 + x5

9 + x5

10

P26 = x1x4

5 + x2x4

5 + x1x4

6 + x3x4

6 + x1x4

7 + x4x4

7 + x2x4

8 + x3x4

8+

x2x4

9 + x4x4

9 + x3x4

10 + x4x4

10

P27 = x1x3

5x6 + x1x5x3

6 + x1x3

5x7 + x1x3

6x7 + x1x5x3

7 + x1x6x3

7 + x2x3

5x8 + x3x3

6x8+

x2x5x3

8 + x3x6x3

8 + x2x3

5x9 + x4x3

7x9 + x2x3

8x9 + x2x5x3

9 + x4x7x3

9 + x2x8x3

9+

x3x3

6x10 + x4x3

7x10 + x3x3

8x10 + x4x3

9x10 + x3x6x3

10 + x4x7x3

10 + x3x8x3

10 + x4x9x3

10

P28 = x2

1x3

5 + x2

2x3

5 + x2

1x3

6 + x2

3x3

6 + x2

1x3

7 + x2

4x3

7 + x2

2x3

8 + x2

3x3

8+

x2

2x3

9 + x2

4x3

9 + x2

3x3

10 + x2

4x3

10

P29 = x1x2x3

5 + x1x3x3

6 + x1x4x3

7 + x2x3x3

8 + x2x4x3

9 + x3x4x3

10

P30 = x3

1x2

5 + x3

2x2

5 + x3

1x2

6 + x3

3x2

6 + x3

1x2

7 + x3

4x2

7 + x3

2x2

8 + x3

3x2

8+

x3

2x2

9 + x3

4x2

9 + x3

3x2

10 + x3

4x2

10

P31 = x3

1x2x5 + x1x3

2x5 + x3

1x3x6 + x1x3

3x6 + x3

1x4x7 + x1x3

4x7 + x3

2x3x8 + x2x3

3x8+

x3

2x4x9 + x2x3

4x9 + x3

3x4x10 + x3x3

4x10

(14)

The exact form of these polynomials is given in Eq. 13 and Eq. 14, where x1, x2, ... x10

correspond to interatomic distances CH1, CH2, CH3, CH4, H1H2, H1H3, H1H4, H2H3,

H2H4, and H3H4 respectively. The presented polynomials form invariant generators [65] of

the group corresponding to arbitrary permutations of the hydrogen atoms. Therefore, the

Distances Polynomials representation preserves all the information about the initial CH4

molecule.

F.3.2

Ablations

The ablation study on the effect of Hessian regularization is given in Fig. 21, and the effect

of the number of grid intervals G in Fig. 22.

10

9

10

7

10

5

10

3

10

1

Hessian regularization

2 × 10

2

3 × 10

2

Validation RMSE / STD

Figure 21: Effect of the strength of Hessian regularization on the validation error when fitting

lmKAN with hidden_dim = 256 on the methane dataset using the Distances Polynomials

representation.

32


!!! page 33 "Pozdnyakov_2025_lmKAN"

3 4

6

8

12

16

20

24

28

34

40

Ni

0.035

0.040

0.045

0.050

0.055

Validation RMSE / STD

Figure 22: Effect of the number of grid intervals G on the validation error when fitting

lmKAN with hidden_dim = 128 on the methane dataset using the Cartesian Components

representation.

F.4

CIFAR-10

Augmentations

We use the following pool of augmentations for the CIFAR-10 dataset:

CIFAR-10 augmentation pipeline

MEAN = (0.4914, 0.4822, 0.4465)

STD = (0.2470, 0.2435, 0.2616)

nn.Sequential(

T.RandomCrop(32, padding=4),

T.RandomHorizontalFlip(),

T.ColorJitter(0.3, 0.3, 0.3, 0.05),

T.RandAugment(2, 7),

T.RandomErasing(p=0.25, scale=(0.05, 0.2), ratio=(0.3, 3.3)),

T.Normalize(MEAN, STD),

)

On top of these, we use MixUp [54] (α = 0.2) and CutMix [55] (β = 1.0) augmentations,

both with 50% probability.

When fitting the families of convolutional neural networks described in the main text, we

use the above pool of augmentations consistently for MLP-based and lmKAN-based CNNs.

For all the details about the fitting procedures see the configuration files attached to these

appendices.

F.5

ImageNet

The standard data preparation pipeline introduced by AlexNet[10] involves first resizing

an image to 256 pixels along the smallest dimension, then performing a random crop of

224 × 224 pixels during training, and a center crop of 224 × 224 pixels during validation.

We mimic this procedure by first resizing the image to 81 ∗256/224 ≈93 pixels across the

smallest dimension, and then performing random or center crops of 81 × 81 pixels.

Next, we use the following augmentation pipeline:

33


!!! page 34 "Pozdnyakov_2025_lmKAN"

2.5

5.0

7.5

10.0

12.5

15.0

17.5

20.0

G

80

82

84

86

88

Accuracy (%)

Train

Validation

Figure 23: Accuracy(G)

10

8

10

6

10

4

10

2

100

Hessian regularization strength,

76

78

80

82

84

86

88

Accuracy (%)

Train

Validation

Figure 24: Accuracy(Hessian regularization strength)

ImageNet augmentation pipeline

nn.Sequential(

T.RandomHorizontalFlip(),

T.ColorJitter(brightness=0.4, contrast=0.4, saturation=0.4, hue=0.1),

T.RandAugment(),

T.RandomErasing(p=0.25, scale=(0.02, 0.33), ratio=(0.3, 3.3), value=0),

T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),

)

On top of these, we use MixUp and CutMix.

F.6

Comparison with FastKAN

The data was split properly into train, validation, and test subsets, while the original

script employed only a train-validation split. We use the cosine (without restarts) learning

rate scheduler [66] instead of the exponential decay of the original script. Finally, the

34


!!! page 35 "Pozdnyakov_2025_lmKAN"

normalization was performed with true values of the mean and standard deviation for the

CIFAR-10 dataset, instead of the placeholder 0.5 values of the original script.

35

