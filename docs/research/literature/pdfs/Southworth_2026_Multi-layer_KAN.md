# Southworth_2026_Multi-layer_KAN

Multilevel Training for Kolmogorov Arnold Networks
Ben S. Southworth∗
Jonas A. Actor†
Graham Harper‡
Eric C. Cyr‡
March 6, 2026
Abstract
Algorithmic speedup of training common neural architectures is made difficult by the lack of structure
guaranteed by the function compositions inherent to such networks. In contrast to multilayer perceptrons
(MLPs), Kolmogorov-Arnold networks (KANs) provide more structure by expanding learned activations in
a specified basis. This paper exploits this structure to develop practical algorithms and theoretical insights,
yielding training speedup via multilevel training for KANs. To do so, we first establish an equivalence
between KANs with spline basis functions and multichannel MLPs with power ReLU activations through
a linear change of basis. We then analyze how this change of basis affects the geometry of gradient-
based optimization with respect to spline knots. The KANs change-of-basis motivates a multilevel
training approach, where we train a sequence of KANs naturally defined through a uniform refinement
of spline knots with analytic geometric interpolation operators between models.
The interpolation
scheme enables a “properly nested hierarchy” of architectures, ensuring that interpolation to a fine model
preserves the progress made on coarse models, while the compact support of spline basis functions ensures
complementary optimization on subsequent levels. Numerical experiments demonstrate that our multilevel
training approach can achieve orders of magnitude improvement in accuracy over conventional methods
to train comparable KANs or MLPs, particularly for physics informed neural networks. Finally, this work
demonstrates how principled design of neural networks can lead to exploitable structure, and in this case,
multilevel algorithms that can dramatically improve training performance.
1
Introduction
Multilayer perceptrons (MLPs) [42, 49, 45] are a classical deep learning architecture that exploit the
composition of affine maps with a nonlinear scalar activation function. MLP architectures appear as blocks
in many state-of-the-art applications, including (but not limited to) variational autoencoders [34] and
transformers [62]. Training MLPs, especially modern multichannel and multihead variants of state-of-the-art
architectures, is a nontrivial numerical task. Typically these methods rely on iterative variants of stochastic
gradient descent resulting in relatively slow convergence. In contrast, in classical numerical methods, multilevel
and multigrid methods for solving numerical partial differential equations (PDEs), are some of the most
powerful solvers of linear and nonlinear equations, capable of solving a sparse n × n linear system in O(n)
operations.
Motivated by this success, there have been a number of attempts to extend multigrid ideas to machine
learning, e.g. [9, 20, 13, 32, 23, 16, 38, 18, 17]. The connection between deep neural networks and discretized
dynamical systems [21, 50, 10] provides theoretical motivation for applying multilevel methods from numerical
PDEs to neural network training, as ResNet depth can be interpreted as a time discretization. Building on
this interpretation, nested iteration via multilevel-in-layer is considered in [9] observing modest speedups, and
multigrid-in-time concepts are applied to develop a layer-parallel training strategy in [20, 13], but the obtained
speedups are due to parallelization and are not algorithmic. Several works have also designed architectures
that explicitly incorporate multigrid structure, e.g. [32, 23, 16]. While these approaches demonstrate that
multigrid principles can inform architecture design, they focus on model structure rather than training
algorithms and do not report training speedups. Rigorous multilevel training in the context of nonlinear
multigrid and cycling is considered in [38, 18], demonstrating modest convergence improvements. Most
∗Theoretical Division, Los Alamos National Laboratory, USA.
†Center for Computing Research, Sandia National Laboratories, USA.
1
arXiv:2603.04827v1  [cs.LG]  5 Mar 2026
recently, Feischl et al. [17] develops a theoretical framework for refinement of feed-forward neural networks
that is incorporated into the optimization procedure.
Nevertheless, to the best of our knowledge no multilevel machine learning works have provided algorithmic
speedups like seen in other fields such as numerical PDEs. Broadly, this is due to the lack of multilevel machine
learning hierarchies with good approximation properties between levels, and grid-specific optimization or
“relaxation” routines that complement the chosen coarsening and interpolation. Implicit in this context is the
substantial difficulty in defining coarse representations of a machine learning model. Because in machine
learning the coarse and fine models typically operate on the same dimensional space, there is no clear extension
of approximation properties from multigrid literature to motivate the choice of coarse model and transfer
operators. On a high level, coarse models must be (i) cheaper to (approximately) solve than the fine model,
(ii) not conflict with the fine model objective, and moreover (iii) provide correction or descent direction that
is difficult to capture/identify with the fine model, i.e. be complementary to “relaxation,” or grid-specific
optimization methods.
An alternative architecture to MLPs, Kolmogorov-Arnold Networks (KANs) [40], has gained popularity
in recent literature, having been used for a range of tasks including computer vision [8, 7, 11], time series
analysis [61, 15], scientific machine learning [1, 59, 65, 35, 30, 44, 28, 48], graph analysis [33, 6], and beyond;
see [54, 27] and references therein for a list of versions, extensions, and applications of KANs, and [43] for a
comprehensive review. The structural similarity between MLPs and KANs has been noted multiple times in
the literature, e.g. [45, 29, 39, 24, 47]. Due to their similarities, KANs tend to be comparable to MLPs for
learning tasks, with the same asymptotic complexity and convergence rates [19] and performance in variety
of head-to-head comparisons [67, 51, 66]. Compared to MLPs, KANs in particular are known for (i) being
more interpretable, as the model output consists of analytical functional composition, and (ii) being able to
better capture low-regularity solutions and mappings than traditional MLPs. However, theoretical insights
and practical algorithms for KANs that exhibit these properties while maintaining (or outperforming) MLPs
are generally inconsistent or lacking, and it is this gap that this paper aims to address, with the particular
aim of advancing training strategies to exploit multilevel optimization algorithms.
1.1
Contributions
In this paper, we advance theoretical and practical insights pertaining to KANs, improving upon our
conceptual understanding of how architectures and optimizers pair together to achieve better training and
model performance. We translate these insights into a demonstration that shows how multilevel methods can
dramatically improve training of a properly designed neural network. To do so, we:
1. exploit the relationship between KANs and multichannel MLPs to introduce a change-of-basis map
between the two architectures;
2. analyze how this change of basis alters the dynamics of gradient descent; and
3. introduce the concept of properly nested hierarchy for multilevel optimization, show that KANs with
appropriate interpolation operators satisfy this ansatz, and design and demonstrate a corresponding
multilevel training approach inspired by multigrid methods.
The outline of the paper and the technical steps and reasons that necessitate the accompanying analysis are
described next.
1.2
The rest of the paper
We begin in Section 2.1 by exploiting the relationship between B-Splines and ReLU activations to reformulate
KANs in the language of multichannel MLPs. We show that KAN architectures with spline activations are
equivalent to a certain form of multichannel MLPs under an appropriate linear change of basis, where the
biases are fixed to match the spline knots. In Section 2.2, we show that the linear change of basis between
KANs and multichannel MLPs exactly matches a finite-difference discretization of the rth derivative operator
on spline knots. This change of basis immediately yields a direct, non-recursive implementation of spline
basis KANs that is faster than the typical Cox-de Boor recursive form (see Section 2.3).
2
Despite the equivalence (as forward operators) under the change of basis, gradient-based training of KANs
and multichannel MLPs yield fundamentally distinct weight evolution. This is discussed abstractly in terms
of the geometry of the primal and dual space in Section 3, where a function of the change of basis matrix
between KANs and multichannel MLPs acts as a preconditioner of descent methods depending on your choice
of spaces. Combining these results with the analysis from Section 2.2 shows substantial benefit to the training
dynamics due to the eigenstructure of differential operators: the multichannel MLP formulation will strongly
prioritize training smooth functions across spline knots. This makes an expressive model of complex functions
easier for the KAN to realize, as compared to a multichannel MLP.
In Section 4, we exploit the mathematical formulations from Section 2 and Section 3 to develop an
efficient multilevel training framework for spline-based KANs, built on the structure that comes with the
spline parameterization, and structure that MLPs lack. To do this, we introduce a new concept of properly
nested hierarchies for multilevel optimization, which ensures that interpolation to a fine model does not
undo progress made on the coarse model. Our transfer operators are built geometrically, naturally yielding a
properly nested hierarchy, and accelerating the grid transfer methods posed in [40] to be fast enough to be
constructed/applied during training. The theory developed in Section 3 then indicates that gradient-based
optimization applied to the properly nested coarse and fine models are complementary, a fundamental
requirement for any successful multigrid method. Altogether, we believe that a properly nested hierarchy with
level-complementary gradient-based optimization routines provide the necessary components for a successful
multigrid method.
In Section 5, we then numerically demonstrate the multilevel training to provide significant improvements
in both accuracy and efficiency applied to functional regression and physics informed neural networks (PINNs).
We similarly show for the same problems that multilevel training applied to the equivalent multichannel MLP
basis, which lacks the level-complementary gradient-based optimization, yields effectively zero improvement
over just the coarse model. This is because training of the fine-grid multichannel MLP prioritizes modes
already captured by the coarse model.
2
KANs and multichannel MLPs
We begin our analysis with an introduction of KANs in the spline basis, and then demonstrate how a
linear transformation relates each layer in the spline basis to an equivalent multichannel MLP. From a
historical and approximation theory standpoint [41, 56, 45, 57], both KANs and MLPs stem from arguments
that expand upon the Kolmogorov Superposition Theorem (KST) [37], also called the Kolmogorov-Arnold
Superposition Theorem. This theorem states there exist functions ϕpq ∈C([0, 1]), for p = 1, . . . , n and
q = 1, . . . , 2n + 1, such that for any function f ∈C([0, 1]n), there are functions φq ∈C(R) such that
f(x1, . . . , xn) = P2n+1
q=1 φq
Pn
p=1 ϕpq(xp)

. Classically φq and ϕpq are not differentiable at a dense set of
points and only H¨older or at best Lipschitz continuous [5, 56, 2]. Inspired by the KST, KANs replace the
functions φq and ϕpq with learned functions expressed in a fixed basis, often a spline basis [40]. While the
original KST invokes a single layer of function composition creating a shallow network, KANs use more layers
of function composition to increase the depth of the resulting representation. For a layer ℓwith P inputs and
Q outputs define the output of a KAN layer as x(ℓ+1)
q
= PP
p=1 ϕ(ℓ)
pq (x(ℓ)
p ) for q = 1, . . . , Q, with ϕ(ℓ)
pq trained
from data. In practice, each ϕ(ℓ)
pq must be represented in a computationally tractable form. Following [40],
we expand each ϕ(ℓ)
pq in a basis of B-splines of order r, yielding a finite-dimensional parameterization where
the spline coefficients become the trainable weights of the network. This choice of basis is motivated by the
approximation properties of splines and their compact support, which we will exploit throughout this work.
Specifically, given a set of knots, each ϕ(ℓ)
pq is represented as ϕ(ℓ)
pq (x) = Pn−1
i=1−r f
W (ℓ)
qpi b[r]
i (x), where f
W (ℓ)
qpi are
learnable weights and {b[r−1]
i
}n−1
i=1−r forms a B-spline basis.
3
2.1
Change of basis
We formalize the structure of the spline basis to establish an equivalence to an alternative representation
using ReLU activations via a linear change of basis. Let T = {ti}n+r−1
i=1−r be a strictly ordered1 set of n + 2r −1
spline knots, where ti < ti+1, with t0 = a and tn = b. Let Pk denote the space of polynomials of degree k.
The spline space of order r with knots T, denoted by Sr(T), is the set of functions
Sr(T) = {f ∈Cr−2([a, b]) : f|[ti,ti+1]∈Pr−1, ti ∈T}.
(1)
The spline space of order r consists of piecewise polynomials of degree r −1 (subject to additional smoothness
constraints). For r = 1, define b[1]
i (x) =
(
1
x ∈[ti, ti+1]
0
else
and for r > 1, we use the Cox-de Boor [14]
recursion formula:
b[r]
i (x) =
x −ti
ti+r−1 −ti
b[r−1]
i
(x) +
ti+r −x
ti+r −ti+1
b[r−1]
i+1 (x).
(2)
Each function b[r]
i
is supported on the interval [ti, ti+r]. We additionally define a ReLUr−1 basis, spanned by
functions
ψ[r]
i (x) = ReLU(x −ti)r−1.
(3)
We can now restate a classical spline approximation result, cf. [12].
Lemma 1. Both B[r]
S = {b[r]
i }n−1
i=1−r and B[r]
R = {ψ[r]
i }n−1
i=1−r are bases for Sr(T).
Thus there exists a linear change of basis between them; denote this change-of-basis matrix as A[r] ∈
R(n+r−1)×(n+r−1), so that
B[r]
S = A[r]B[r]
R ,
(4)
with B[r]
S and B[r]
R understood to be square matrices with columns given by basis vectors. The matrix A[r] is
structured and banded, with a particularly elegant expression for the case of uniform knot spacing:
Lemma 2. For r > 1, let A[r−1] denote splines of order r −1 constructed on knots for splines of order r.
Then the matrix A[r] is defined entry-wise as:
A[r]
ij =
1
ti+r−1 −ti
A[r−1]
ij
−
1
ti+r −ti+1
A[r−1]
i+1,j,
(5)
where we define A[r−1]
n+r,: = 0 to account for the special case of the final row i = n + r −1.
Proof. See Section B.
Corollary 1 (Uniform knots). In the case of uniform knots, with spacing h = ti −ti−1, A[r] is upper
triangular Toeplitz, with entries
A[r]
ij =
(
(−1)j−i
(j−i)! (r−j+i)!
r
hr−1
i ≤j ≤i + r
0
else
.
Proof. See Section B.
We now show that the change of basis A[r] (4) yields an equivalence between KANs and a certain form of
multichannel MLP. Each layer of a KAN architecture in the spline basis B[r]
S has spline coefficients stored as
parameters/weights in a 3-tensor f
W (ℓ) such that
x(ℓ+1)
q
=
P
X
p=1
n−1
X
i=1−r
f
W (ℓ)
qpi b[r]
i (x(ℓ)
p ).
(6)
1We assume a strictly ordered, i.e. nondegenerate, set of spline knots, which simplifies the required assumptions and definitions.
While the authors know of no theoretical reasons why degenerate splines should not be considered under this framework, there is
substantial technical rigor necessary to treat these properly, so we omit them from this discourse.
4
Define W (ℓ) = f
W (ℓ) ×3 (A[r])T , where ×3 denotes the 3-mode tensor product2; at the index level, W (ℓ)
qpj :=
Pn−1
i=1−r f
W (ℓ)
qpiA[r]
ij . Substituting the change of basis from (4) and definition of W (ℓ) into (6) yields
x(ℓ+1)
q
=
P
X
p=1
n−1
X
i=1−r
f
W (ℓ)
qpi


n−1
X
j=1−r
A[r]
ij ReLU(x(ℓ)
p
−tj)r−1


(7a)
=
P
X
p=1
n−1
X
j=1−r
W (ℓ)
qpj ReLU(x(ℓ)
p
−tj)r−1.
(7b)
With a notational shift outlined in Section A, we observe that (7) is an equivalent dense mulitchannel MLP
layer with ReLUr−1 activations. Altogether, we arrive at the following result.
Lemma 3 (Equivalence of KANs and multichannel MLPs). A single layer of a KAN in the form of (6),
with weight three-tensor f
W (ℓ), is equivalent to a single layer of a multichannel MLP in the form of (7) with
weight three-tensor W (ℓ) = f
W (ℓ) ×3 (A[r])T .
Now consider a full network consisting of multiple layers. For ease of notation, and with Section 3 in
mind, let us vectorize weights across all layers, and denote u as the full vector of weights in the spline basis
and w as the vector of weights in the ReLU basis; both u, w ∈RNw. Following the above discussion, with
appropriate concatenation and reordering/flattening of A[r] we can define the change of basis matrix A such
that
AT u = w.
Note, here the change of basis maps from weights in the spline basis to weights in the ReLU basis, opposite of
the direction of the functional change of basis (4). Assume the vectorization operation on the weights u and
w is ordered with respect to layer, output neuron, input neuron, and then spline knot. With this ordering
the resulting A is block diagonal over the first three dimensions (layer, output neuron, and input neuron)
with diagonal blocks given by (A[r]) of the appropriate dimension over spline knots.
2.2
Eigenstructure of A[r]
We now prove the following lemma regarding the structure of A[r] as a discrete approximation of certain
differential operators.
Lemma 4. Up to constant scaling by ±(r −1)!/h (with sign depending on r being odd or even), A[r] is a
forward finite difference approximation of the rth derivative on a 1d uniform grid of mesh spacing h, with
strongly enforced zero Dirichlet boundary conditions. Up to boundary nodes and constant scaling, (A[r])T A[r]
is also Toeplitz and a finite difference approximation of the (2r)th derivative on a 1d uniform grid of mesh
spacing h.
Proof. Let us consider the stencil v(r) for spline power r starting from the diagonal and extending to upper
triangular indices. Let the diagonal index correspond to zero and v(r)
i
denote the ith stencil index. Then
v(r)
i
:=
(−1)i
i! (r −i)!
r
hr−1 =
1
(r −1)!hr−1
h
(−1)i
r
i
i
,
i ≤r.
(8)
Now we recall the general forward finite difference for f (r)(x) centered at x is given by [52]
f (r)(x) ≈1
hr
r
X
i=0
(−1)r−i
r
i

f(x + ih).
(9)
This completes the proof for A[r], where zero Dirichlet boundary conditions correspond to truncated Toeplitz
structure in the final matrix rows. For Toeplitz properties of (A[r])T A[r] and corresponding stencil values see
2See [36] for more details on this operation.
5
[55, Lemma 23]. Consistent with above discussion, the stencil of the inner Toeplitz operator up to constant
global scaling takes the form of the general central finite difference approximation to the (2r)th derivative,
f (2r)(x) ≈
1
h2r
2r
X
i=0
(−1)i
2r
i

f(x + (r −i)h).
(10)
Lemma 4 proves a discrete differential relationship between the ReLU and spline bases in a KANs
architecture. For example, up to boundary nodes, for r = 1 we have that (A[r])T A[r] corresponds to the
[1, −2, 1] stencil for isotropic diffusion in 1d. This immediately gives us strong intuition on the effects of
(A[r])T A[r] as an operator. Let us consider eigenvalues of the (2r)th derivative operator D2r := d2r
dx and
consider the simplified setting of domain x ∈[0, 1] with periodic boundary conditions f (k)(0) = f (k)(1) for
k ∈{0, ..., 2r −1}. Consider the Fourier basis for eigenvectors
fi(x) := e−2πiix
i ∈Z.
(11)
Differentiating 2r times yields
f (2r)
i
(x) = D2re−2πiix = (−2πii)2re−2πiix = (−1)r(2πi)2re−2πiix,
(12)
for i ∈Z. Thus we have eigenvalues of D2r given by λ ∈{(−1)r(2πi)2r} for i ∈Z, with magnitude of
eigenvalue λ directly related to Fourier frequency of corresponding eigenvector fi(x) = e−2πiix.
Moving to the discrete setting and spline change of basis, (A[r])T A[r] does not impose periodic boundary
conditions and, by nature of the normal-equation form, eigenvalues will be strictly positive rather than
alternating sign with r as in the continuous analysis. This is because (A[r])T A[r] is approximating alternating
signs of the (2r)th derivative compared with the FD stencil in (10). However, we expect the broad properties
to still hold. First, the eigenvalues will span a large range, and (up to constant scaling) roughly take the
form ℓ2r for eigenvalue index ℓ∈[1, n] for n spline knots. Second, the eigenmodes will be correspondingly
ordered with respect to smoothness, with the smallest eigenvalues corresponding to the smoothest eigenmodes
and the largest eigenvalues corresponding to the most oscillatory eigenmodes on the spline grid, although
this eigenbasis will not be a strict Fourier basis due to non-periodic boundary conditions. Each of these
properties is demonstrated for r = 1 and r = 3 in Figure 1. Figure 2a then shows the difference in scaling of
smooth vs oscillatory modes on a spline grid by (A[r])T A[r] by considering the ratio of smallest to largest
eigenvalues. Continuing with the observation that eigenvalues approximately follow ℓ2r, we expect the ratio
to scale like n2r, which is confirmed in Figure 2a. Thus for even a small number of n = 10 spline knots,
the most oscillatory modes are scaled more than 100× stronger than the smoothest modes for r = 1 and
106× stronger for r = 3. To demonstrate the geometry in a simpler manner, we also plot the number of sign
changes in the discrete eigenvectors in Figure 2b. Here we see the expected simple structure, independent
of r – the eigenvector associated with the smallest eigenvalue of (A[r])T A[r] has no sign changes and the
eigenvector associated with the largest eigenvalue has n −1. Naturally (A[r](A[r])T )−1 follows the exact
opposite ordering.
We will show in Section 3 that the eigen-structure of these transfer operators has important impacts on
the training dynamics.
2.3
Computational cost
While both bases, B[r]
R and B[r]
S , are equivalent in terms of their outputs, they differ in their computational
cost for evaluating the output of each layer. The Cox-de Boor formula has been observed to be computa-
tionally expensive [46], and this reformulation using B[r]
R provides an impressive speedup to the underlying
computational graph. Consider that for a single layer a forward-pass through the standard B-spline basis
takes O(PQ(nr + r2)) floating-point operations per layer, the ReLU-based formulation requires only order
O(PQ(n + r)) operations, resulting in a speedup (in FLOPs) by a factor equal to the spline degree. This
removes the need to implement different versions of the spline activations as in [46, 53]. The change-of-basis
operation, i.e., multiplication by A, requires only O(nr) operations per layer, since A is a banded matrix with
6
0
10
20
30
40
50
Index
10
3
10
2
10
1
100
Eigenvalue (A[1])TA[1]
Eigenvalue
ind2
0.0
0.2
0.4
0.6
0.8
1.0
x
0.20
0.15
0.10
0.05
0.00
0.05
0.10
0.15
0.20
Eigenvector vi(x)
First five eigenvectors
0.0
0.2
0.4
0.6
0.8
1.0
x
0.20
0.15
0.10
0.05
0.00
0.05
0.10
0.15
0.20
Eigenvector vi(x)
Last five eigenvectors
(a) r = 1
0
10
20
30
40
50
Index
10
7
10
5
10
3
10
1
101
Eigenvalue (A[3])TA[3]
Eigenvalue
ind6
0.0
0.2
0.4
0.6
0.8
1.0
x
0.3
0.2
0.1
0.0
0.1
0.2
0.3
Eigenvector vi(x)
First five eigenvectors
0.0
0.2
0.4
0.6
0.8
1.0
x
0.20
0.15
0.10
0.05
0.00
0.05
0.10
0.15
0.20
Eigenvector vi(x)
Last five eigenvectors
(b) r = 3
Figure 1: Eigenvalues of (A[r])T A[r] ordered smallest to largest (left) and the first (center) and last (right) five
corresponding eigenvectors for n = 50 splines knots and example orders r ∈{1, 3}.
0
20
40
60
80
Number of spline knots
101
103
105
107
109
1011
1013
1015
max/
min
r=4
r=3
r=2
r=1
n2r
(a) Ratio of largest to smallest eigenvalue of (A[r])T A[r] as
a function of number of spline knots, shown for r ∈[1, 4].
This ratio provides the weighting of corresponding modes in
gradient descent based optimization.
0
20
40
60
80
100
Eigenvector index
0
20
40
60
80
100
Number of sign changes
(A[r])TA[r]
((A[r](A[r])T)
1
r=4
r=3
r=2
r=1
(b) Number of sign changes in discrete eigenvectors as a
function of eigenvector index, for n = 100 knots, r ∈[1, 4], and
eigenvalues ordered in ascending order. Shown for (A[r])T A[r]
and (A[r](A[r])T )−1.
Figure 2: Comparison of eigenvalue and eigenvector properties across spline orders.
r + 1 nonzero diagonals (see Appendix B for explicit construction). Thus for small spline order r, and even
moderate values of P and Q the cost is negligible compared to the contraction against the learnable weights.
On a set of predetermined spline knots, the matrix A can additionally be implemented via a convolution
stencil, which is particularly efficient for uniform knots.
To illustrate these results, we train a simple architecture with three hidden layers of width 64 using direct
implementations of (6) and (7), where the spline basis functions are implemented via the standard Cox-de
Boor recursive form. We measure the wallclock time per epoch for a range of spline orders r and number
of knots n, repeating each experiment 10 times to smooth out any noise in wallclock measurements; our
wallclock measurements include only the forward and backward passes through the network, and exclude
time for data loading and evaluation of a validation dataset. Linear algebra operations on modern GPUs
take advantage of the hardware architectures which complicates wallclock measurements, but in Figure 3, we
7
still see significant improvement in wallclock time that grows with r.
Figure 3: Speedup of evaluating a layer, by applying the ReLUr activation and then the change-of-basis matrix,
compared to computing the Cox-de Boor recursive formula for spline functions. Error bars show 1 standard deviation,
computed over 10 instances.
3
Gradient descent and choice of basis
Despite an equivalence (as forward operators) under the change-of-basis, gradient-based training of KANs
and multichannel MLPs yield fundamentally distinct dynamics during training, which we show by connecting
the change-of-basis operations to standard results from preconditioning.
To complement the architectures in Section 2, we formalize the notation for our training problem. We
consider training of a neural network with input data of dimension din ∈N and output data of dimension
dout ∈N, where we train on a flattened batch of k input-output data pairs {x, y} for x ∈Rkdin, y ∈Rkdout.
Let f(x; w) : Rkdin ×RNw 7→Rkdout denote the action of the ReLU-based network on batch input data x given
weights w, and let L : Rkdin × Rkdout × RNw 7→R be a scalar valued loss on the data for the given weights.
The resulting corresponding unconstrained optimization over weights is then given by minw∈Rn L(f(x; w), y).
We introduce the change of basis into this optimization problem, and define a nonlinear function
g(x; u) : Rkdin × RNw 7→Rkdout such that g(x; u) = f(x; AT u) = f(x; w), corresponding to a spline-based
KAN. Then we can equivalently minimize
min
w∈Rn L(f(x; w), y) = min
u∈Rn L(g(x; u), y).
(13)
Let ∇wL ∈RNw and ∇uL ∈RNw denote the standard ℓ2-gradient (easily computed with back propagation)
with respect to pairs {w, f} or {u, g} respectively. For gradient descent, we are interested in the basis
representing our primal and dual spaces. If we work exclusively in the w or u bases for the primal and dual
space, we arrive at standard potentially preconditioned gradient descent iterations:
wk+1 = wk −ηDw∇wL,
(14a)
uk+1 = uk −ηDu∇uL,
(14b)
for linear preconditioner Dw, Du, e.g. from ADAM or LBFGS (or D = I for gradient descent). Now consider
a change of basis w 7→AT u or u 7→A−T w. Let Jf := ∂f/∂w ∈Rk×Nw and Jg := ∂g/∂u ∈Rk×Nw
denote the Jacobians of f and g with respect to their natural variables. Since g(x; u) = f(x; AT u) we have
Jg = ∂f
∂w
∂w
∂u = JfAT . Let ∇mL ∈Rk denote the derivative of L with respect to model output over k data
samples. From (13) we can compute a gradient in w-space via
∇wL :=
 ∂f
∂w
T ∂L
∂f = JT
f ∇mL.
(15)
Similarly, we can compute a gradient in the u-space and arrive at the change of basis in the dual (gradient)
space:
∇uL :=
 ∂g
∂u
T ∂L
∂g = JT
g ∇mL = AJT
f ∇mL = A∇wL.
(16)
8
Substituting w 7→AT u and ∇wL 7→A−1∇uL into (14a), and u 7→A−T w and ∇uL 7→A∇wL into (14b) we
arrive at the preconditioned gradient descent iterations, respectively,
uk+1 = uk −ηA−T DwA−1∇uL,
(17a)
wk+1 = wk −ηAT DuA∇wL,
(17b)
where we have maintained the original preconditioners through the change of basis. This change-of-basis can
also be seen as imposing the geometry of the w space on the u space. A change of basis by AT , u 7→A−T u,
induces the pullback metric in U-space, ⟨x, y⟩U := yT AAT x, where letting Du = I, the gradient is now taken
with respect to the (AAT )-inner product. Recall the following result [4]:
Lemma 5. Consider L : Rn 7→R and let ∇L(x) denote the gradient of L in the ℓ2-inner product at x ∈Rn.
Let M ∈Rn×n be an SPD matrix. Then the gradient of L with respect to the M-induced inner product is
given by
∇ML(x) = M −1∇L(x).
(18)
We see that (17a) for Du = I is gradient descent with respect to {u, g} in the (AAT )-inner product,
arising from imposing the geometry of W-space on U-space. Similarly, for Dw = I (17b) is equivalent to
gradient descent in {w, f} with respect to the (AT A)−1 inner product, arising from the metric pullback
imposing the geometry of U-space on W-space.
For completeness, one can also mix spaces. Suppose we iterate in w but consider a gradient with respect
to u. Such iterations would take the form wk+1 = wk −ηDu∇uL. Substituting either ∇uL 7→A∇wL
or w 7→AT u we arrive at iterations wk+1 = wk −ηDuA∇wL or uk+1 = uk −ηA−T Du∇uL. Similarly
we can iterate in u but consider a gradient with respect to w.
Such iterations would take the form
uk+1 = uk −ηDw∇wL.
Substituting either ∇wL 7→A−1∇uL or u 7→A−T w we arrive at iterations
uk+1 = uk −ηDwA−1∇uL or wk+1 = wk −ηAT Dw∇wL. Note that computing gradients in the same basis
you are iterating in yields preconditioned gradient descent with SPD preconditioners related to the induced
inner product. In contrast, computing a gradient with respect to a different basis then you are iterating in
yields potentially nonsymmetric preconditioned descent. These methods correspond to a modified choice of
duality pairing, specifying the unique mapping between every dual vector (gradient) and primal vector. The
duality pairing is an invertible but not necessarily SPD matrix, in this case specifically given by the leading
preconditioning operator in each equation (assuming we don’t also consider a modified inner product).
Altogether we have four distinct iterations, with equivalent realizations in u or w show in Table 1. Note
that in the remainder of this paper we will consider iterating in the spline space u due to its interpretability,
and consider the iterations that arise from considering the u geometry and gradient (14b) or the w geometry
and gradient (17a), with the former being the gradient descent that arises naturally in KANs.
Geometry
Gradient
Space
Prec. update
w
∇wL
w
wk+1 = wk −ηDw∇wL
u
uk+1 = uk −ηA−T DwA−1∇uL
w
∇uL
w
wk+1 = wk −ηDuA∇wL
u
uk+1 = uk −ηA−T Du∇uL
u
∇uL
w
wk+1 = wk −ηAT DuA∇wL
u
uk+1 = uk −ηDu∇uL
u
∇wL
w
wk+1 = wk −ηAT Dw∇wL
u
uk+1 = uk −ηDwA−1∇uL
Table 1: Preconditioned gradient descent update rules under different parameterizations and gradient representations.
We associate the initial preconditioner to be consistent with the gradient, e.g. ∇u has preconditioner Du.
The preconditioning induced by the change of basis coupled with the spectral theory from Section 2.2
provides a framework for understanding and ensuring complementary optimization or “relaxation” on each
level in the multilevel hierarchy proposed in the next section (see Section 4.2).
Remark 1. Given the structure of A and each block A[r] derived in Section 3, we can bound the spectral
radius of the neural tangent kernel (NTK) to show that gradient based optimization routines for a ReLU and
spline basis as derived above can be used with comparable learning rates, despite the preconditioning induced
by the change of basis. However, the resulting training dynamics will differ significantly; for more on the
NTK of these matrices, see the Supplementary Material.
9
4
Multilevel training of KANs
We build upon the change-of-basis and preconditioning results for KANs to develop an efficient multilevel
training framework for spline-based KANs, exploiting the additional structure that comes with the spline
parameterization. With the preconditioning results above, we can view multichannel MLPs in a natural
spline basis that provides a functional framework for building models with straightforward hierarchy of scales
and transfer operators. KANs with spline basis functions and geometric transfer operators provide properly
nested hierarchies of different refinement and complementary level-specific optimization.
4.1
General multilevel formulation
Let P : RNc 7→RNf be a linear interpolation and change of basis from coarse weight space of dimension Nc
to fine weight space of dimension Nf. Optimizing over coarse space u(c), we have gradient updates
u(c)
k+1 = u(c)
k
+ ηPT ∇L(Pu(c)
k ).
(19)
Suppose ∇L(u) = Lu for linear operator L. Then this reduces to
u(c)
k+1 = u(c)
k
+ ηPT LPu(c)
k ,
(20)
which is exactly a Richardson iteration on a Galerkin coarse grid operator Lc := PT LP. If we further include
a diagonal scaling in Pu(c) such that Lc has unit diagonal, this results in a Jacobi relaxation iteration applied
to the Galerkin coarse grid operator, which is exactly the computational kernel in algebraic multigrid coarse
grid correction.3
Returning to optimization, consider model g(x; u) : Rkdin × RNw 7→Rkdout and loss L : Rkdin × Rkdout ×
RNw 7→R. To ensure good approximation of the fine-level objective by coarse-level updates, a natural
approach would be defining a coarse subspace optimization problem via
min
u(c)∈RNc L(g(x; Pu(c)), y).
(21)
This interpretation provides a framework to coarsen in weight space while ensuring good coarse approximation
(a key component of multigrid almost all multilevel machine learning methods currently lack). In practice
we do not want every level to be as expensive to evaluate as the finest level, as is naively the case in (21)
due to the size of the inner model g through which gradients are back-propagated. This does provide a
natural target for designing multilevel hierarchies and considering approximation properties though. Consider
a two-level hierarchy. Following the definition in (21), we define a natural relation between coarse and
fine architectures and corresponding transfer operators for a hierarchy that is properly nested in terms of
functional approximation.
Definition 1 (Properly nested hierarchy). Let gf(x; u(f)) : Rkdin × RNf 7→Rdout denote the action of the fine
operator on flattened input vector x ∈Rkdin with fine-grid weights u(f) ∈RNf and gc(x; u(c)) : Rkdin × RNc 7→
Rdout denote the action of the coarse operator on flattened input vector x ∈Rkdin with coarse-grid weights
u(c) ∈RNc. Let P : RNc 7→RNf be a linear interpolation operator from coarse to fine weight space. We
define {gf, gc, P} as a properly nested hierarchy if
gc(x; u(c)) = gf(x; Pu(c)),
(22)
that is, a properly nested hierarchy imposes that the fine operator exactly preserves the action of the coarse
operator under interpolation of weights.
This definition guarantees that interpolation of weights does not undo progress made via coarse level
optimization, as the fine model and corresponding loss will match that of the coarse model exactly. If we
satisfy the above definition, we can construct a change-of-basis hierarchy without having to evaluate a network
with fine level cost on every level. In particular, we satisfy the following proposition.
3Petrov-Galerkin transfer operators with restriction R ̸= PT can be achieved by considering a gradient in a non-standard
inner product or duality pairing. We will not consider such cases here.
10
Proposition 1 (Subspace optimization). Let gf, gc : Rdin 7→Rdout and P : RNc 7→RNf be as in Definition 1,
and define fine and coarse loss functions L : Rkdin × Rkdout × RNf 7→R, Lc : Rkdin × Rkdout × RNc 7→R
that are identical with respect to model output, that is, if gc(x; u(c)) = gf(x; u(f)) then Lc(gc(x; u(c)), y) =
L(gf(x; u(f)), y). Then
min
u(c) Lc(gc(x; u(c)), y) = min
u(c) L(gf(x; Pu(c)), y).
(23)
This is a simple result that formalizes the purpose of the properly nested hierarchy – optimizing in
the coarse space with coarse loss Lc is equivalent to optimizing the fine loss with weights restricted to a
subspace. However, we must be careful with our coarsening to ensure (22) is feasible. If we take something
like coarsening-in-layer, as considered a number of times in the literature, e.g. [20, 13, 38], such a constraint
may not be possible to satisfy. For an arbitrary number of levels, we define our nested multilevel optimization
in Algorithm 1. Note, in this paper we do not consider proper multilevel cycling. Nonlinear multigrid and
multigrid optimization are notoriously sensitive, and will be a topic for future work.
Algorithm 1 Nested Multilevel Optimization
Input: Hierarchy {gk}K
k=1, transfer operators {Pk−1
k
}K
k=2, training data x
Output: Solution u1 to finest level problem, minu1 L(g1(x; u1)).
1: Initialize uK
{Initialize weights on coarsest level}
2: for k = K to 2: do
3:
Solve minuk L(gk(x; uk))
{Solve level k optimization with initial guess uk}
4:
uk−1 ←Pk−1
k
uℓ
{Interpolate solution to finer level as initial guess}
5: end for
6: Solve minu1 L(g1(x; u1))
{Solve optimization on finest level with initial guess u1}
7: return u1
4.2
Transfer operators in KANs
Using multiresolution features of splines to build KANs at differing resolutions was introduced in [40]. However,
the refinement done in [40] does not perform geometric refinement; instead, they interpolate between grids of
arbitrary sizes. To do so, they solve for each hidden node a least-squares problem of size Ndata × (n + r −1),
which is (unsurprisingly) prohibitively costly. This idea was dismissed by the authors as being too slow for
practical applications. In contrast, it is substantially more efficient to refine geometrically and then use
restriction and prolongation operators from multigrid literature [25, 22] to perform the grid transfer, thus
enabling multilevel training to become much more feasible and cost-effective.
We first make the observation that for two sets of knots T, T ′ where T ⊂T ′, we have Sr(T ′) ⊂Sr(T).
Thus there exists an interpolation operator P from one grid to another in the case of nested grids. The splines
defined by an arbitrary set of knots T on arbitrary coarse grid with basis
n
b[r]
i,T
on−1
i=1−r has a corresponding
basis with knots T ′ on a finer grid given by
n
b[r]
i,T ′
om−1
i=1−r with m > n. For a KAN layer with knots T, we can
therefore define a fine KAN layer with knots T ′ whose values are identical, since for an interpolation matrix
P, we have
x(ℓ+1)
q
=
P
X
p=1
n−1
X
i=1−r
f
W (ℓ)
qpi,T b[r]
i,T (x(ℓ)
p ) =
P
X
p=1
n−1
X
i=1−r
m−1
X
j=1−r
f
W (ℓ)
qpi,T Pij b[r]
j,T ′(x(ℓ)
p )
:=
P
X
p=1
m−1
X
j=1−r
f
W (ℓ)
qpj,T ′ b[r]
j,T ′(x(ℓ)
p ).
(24)
In the general case of arbitrary T ⊂T ′, using the respective change-of-basis matrices A[r]
T , A[r]
T ′ defined via
Equation (5), we can write
P = A[r]
T I A[r]
T ′
−1,
where
Iij =
(
1
ti = t′
j for ti ∈T, t′
j ∈T ′
0
else
.
11
In the case of dyadic refinement on a uniform spline grid, P is explicitly given [25] as
Pij =





2−r
 
r
s
!
j = 2i + s
0
else
.
(25)
The refinement process described in Equation (24) produces a new KAN layer that is functionally equal to
the previous, but with more trainable parameters. Under this definition, we satisfy Definition 1, and can thus
define a properly nested hierarchy (21) without having to evaluate a network with fine level cost on every
level. This is one of the fundamental features of multilevel KANs, as it means the refinement process does
not modify the training progress made on coarse models.
Thus far, the multilevel method for KANs is not unique to our B-spline approach. The transfer operators
and properly nested hierarchy are valid for broad classes of KANs where activation functions are discretized.
Any discretization of activation functions with a similar nesting of spaces upon grid (or polynomial) refinement
satisfies this same result, which we will state below.
Lemma 6. Any KAN with activations defined over a basis which is nested under a refinement procedure can
be supplied with interpolation operators that yield a properly nested hierarchy (Definition 1).
Proof. Let B = {ϕi : [a, b] →R}nB
i=1 be a basis of size nB for the activation function space (e.g. B-splines,
Chebyshev, wavelets) on a domain [a, b] with a, b ∈R, a < b, and let B′ = {ϕ′
i : [a, b] →R}nB′
i=1 be a basis of
size nB′ > nB such that B′ ⊃B. Then there is an operator PB′
B : B →B′ which interpolates basis B to B′
such that for σ ∈B we have PB′
B σ ∈B′ and σ(x) ≡PB′
B σ(x).
Note that this form of network refinement is tied to the discretization of the activation functions; essentially
this performs refinement with respect to the channel dimension of the weight tensors, instead of refining the
number of hidden nodes at each layer. While there are efforts to refine networks by increasing the number of
layers or hidden nodes, the method in Lemma 6 does not change the number of nodes in the network.
4.3
Complementary relaxation
Complementary processes to attenuate different error modes is arguably the most fundamental component of
a successful multigrid method, and also the most challenging for multilevel ML. Previously we discussed how
KANs enable a well-defined nested hierarchy of ML models. In addition, it is critical that the “relaxation” or
local training on different levels is complementary, in that when you interpolate your model to a finer level,
your optimization takes advantage of this new expressivity.
From the results in Lemma 4 and Table 1, we can impose a strong preference in descent-based optimization
of multichannel MLPs/KANs toward learning higher or lower frequency functions with respect to the spline
knots based on the geometry of the gradient and objective space. For simplicity consider gradient descent,
Du, Dw = I. Recall from (17a), optimizing in the ReLU geometry and basis imposes a preconditioning in
the spline basis. For stability, the learning rate must be chosen to normalize that the largest eigenmode
of the preconditioned operator. When the preconditioner (AAT )−1 has a large spectral range, gradients
associated with small eigenvalues of (AAT )−1 provide almost no correction to the weights. As discussed
in Section 2.2, the eigenfunctions of even-order differential operators are ordered from smoothest to most
oscillatory in terms of magnitude from smallest to largest, and (AAT )−1 ∼(∂x)−r will be opposite. Moreover,
the eigenvalues span a range of magnitudes. For r = 1, we have (AAT )−1 ∼∆−1, where the smoothest
modes are order O(1) and oscillatory modes on the spline grid are are order O(h)2 for knot spacing h. Thus
gradient based optimization with a basis induced preconditioning (AAT )−1 will weight gradient corrections
that are smooth in knot space by orders of magnitude more than oscillatory ones. This is especially true for
r > 1. Thus multichannel MLPs do not satisfy a complementary relaxation, as all levels will strongly favor
optimizing smooth functions in the knot space. This is the opposite of what we want, as after refining our
spline knots we have added new expressivity via more complex/less smooth functions. If the optimizer cannot
quickly optimize over this new space, the refinement will be a waste. This phenomenon will be demonstrated
numerically in Section 5.
12
In contrast, in the natural KANs spline basis the free weights being optimized correspond to local basis
functions with compact support. As a result, a nonzero gradient at a specific weight results in an update that
largely effects a local region centered at the corresponding spline knot within the larger KANs functional
composition. To that end, we expect the gradient to transfer directly to these coefficients and naturally
support oscillatory functions on the resolution of spline knots, specifically due to the compact support and
localization. This is exactly the behavior needed in a multilevel training setting, so that when we perform a
uniform refinement of our spline knots, gradient-based optimizers on the refined model immediately start
utilizing the new expressivity in reducing the loss. Indeed, this behavior is exactly what we will demonstrate
numerically in the following section.
5
Numerical results
5.1
Regression
First we consider function regression of a 0.175 radian counterclockwise (≈10.03◦) coordinate rotation of the
nonsmooth function
f(x, y) = cos(4πx) + sin(πy) + sin(2πy) + | sin(3πy2)|,
(26)
with a [2, 5, 1] architecture. Optimization is performed with geometry and gradient defined by the spline basis
(u in the context of Section 3) with descent (14b), and the ReLU basis (w in the context of Section 3) with
descent (17a). In both cases, we consider training a coarse model, a fine model, and a multilevel training
schedule, as well as a comparable vanilla MLP architecture. We train using L-BFGS, each with equivalent
amounts of work (FLOPs) during training. Epochs counts are denoted in a list such as {32, 16, 8, 4}, meaning
32 epochs are performed on the initial model, and then 16 epochs are performed after transferring to a refined
model where the original grid was evenly subdivided once, and so on. The coarse model corresponds to
{128, 0, 0, 0}, the fine model to {0, 0, 0, 16}, and the multilevel model as {32, 16, 8, 4}. Results are shown in
Table 2 averaged across five random initializations.
Table 2: Accuracy for regression trained under different bases, architectures, and training regimes. Standard deviations
are computed over random initializations (N = 5).
Type
Layers
Basis
Fidelity
# Param.
MSE: mean (stdev)
KAN
[2, 5, 1]
ReLU
coarse
55
1.10 × 10−2 (8.32 × 10−3)
KAN
[2, 5, 1]
ReLU
fine
230
1.35 × 10−0 (1.50 × 10−1)
KAN
[2, 5, 1]
ReLU
multilevel
230
1.06 × 10−2 (8.03 × 10−3)
KAN
[2, 5, 1]
Spline
coarse
55
1.65 × 10−3 (4.18 × 10−5)
KAN
[2, 5, 1]
Spline
fine
230
2.54 × 10−3 (5.64 × 10−3)
KAN
[2, 5, 1]
Spline
multilevel
230
3.67 × 10−5 (7.19 × 10−5)
MLP
[2, 5, 1]
ReLU
20
2.94 × 10−2 (1.60 × 10−2)
MLP
[2, 30, 1]
ReLU
120
1.02 × 10−3 (9.42 × 10−4)
MLP
[2, 20, 20, 1]
ReLU
500
3.33 × 10−4 (2.92 × 10−4)
First and foremost, we see that training in the spline basis u leads to 1−3 orders of magnitude improvement
in accuracy compared with the ReLU basis w. It is also clear that for fixed number of training epochs, the
fine model, which is in principle more expressive, reaches at best a comparable accuracy to the coarse model
for spline basis, and two orders of magnitude worse for the ReLU basis. Multilevel training in the spline basis
significantly accelerates training, obtains orders of magnitude better accuracy than just training on a coarse
or fine model, and an order of magnitude better than a larger vanilla MLP. In contrast, multilevel training in
the ReLU basis provides effectively no improvement over just the coarse model. Building on theory from
Section 3, this makes perfect sense. When we refine our spline knots and begin gradient-based training of
the finer model in a ReLU basis, the associated preconditioning strongly favors geometrically smooth modes
by orders of magnitude. However, geometrically smooth modes are largely able to be represented by the
coarse model in the first place, which leads to the zero improvement in accuracy when training the refined
13
model in the ReLU basis. This is an important observation in the context of multilevel machine learning, and
effectively an extension of multigrid approximation properties to the context of stochastic optimization – it is
critical that training on the fine model is complementary to training on the coarse model.
Convergence histories under the same amount of training work are shown in Figure 4 to illustrate the
impact of refinement on training history. The points where the multilevel model loss stagnates before abruptly
dropping correspond to the epochs where the model is refined. Note that training on the fine models (KAN
or MLP) have effectively stalled, with loss decreasing extremely slowly. This emphasizes the value of the
multilevel training, where the loss evolution plot demonstrates that standalone fine KAN or MLP models
would take significantly more epochs to reach the accuracy obtained by the multilevel training, if at all.
0
20
40
60
80
100
120
Epoch
10
5
10
4
10
3
10
2
10
1
100
Loss
KAN ReLU (coarse)
KAN Spline (coarse)
KAN ReLU (fine)
KAN Spline (fine)
KAN ReLU (multilevel)
KAN Spline (multilevel)
MLP ReLU #1
MLP ReLU #2
MLP ReLU #3
Figure 4: Select convergence history for regression under approximately same amount of work for all different models.
Vertical lines indicate refinements for multilevel models.
5.2
Physics-informed neural networks
This section explores the impact of multilevel training physics-informed neural networks (PINNs). PINNs is by
now established as a leading neural network approach for approximating the solution of PDEs. Training these
models can be difficult with a number of tricks required to achieve reasonable solutions efficiently [64, 63].
Our goal is to use PINNs to study the performance characteristics of our KANs methodologies compared
to traditional architectures. To that end, we limit the use of specialized data modifications and training
techniques that yield state-of-the-art PINNs solutions. One included enhancement is residual-based attention
(RBA), proposed in [3], applied to the volumetric loss term. RBA improved convergence without obscuring
the interpretation of the results.
5.2.1
2d Poisson
The first PINN considered solves the 2d Poisson equation:
∇· (ϵ(⃗x)∇u(⃗x)) = f(⃗x)
⃗x ∈[−1, 1]2,
u(⃗x) = 0
x ∈∂Ω.
(27)
Letting ⃗x = [x, y], the coefficient and the manufactured solution are
ϵ(⃗x) =
 ϵl = 1
x < 0
ϵr = 1
2
x ≥0 , u∗(⃗x) =
 sin(πx) sin(3πy)
x < 0
sin(2πx) sin(3πy)
x ≥0
(28)
with the appropriate forcing f(⃗x). The PINN loss shown in Figure 5 (left) is defined over three sets of
equally spaced points; the volume V (2401 interior points on the interior), the boundary B (200 points on the
exterior) and the interface I (49 points where x = 0). The LI terms enforces the correct jump in the gradient
at x = 0. To permit the use of a single neural network approximation (as opposed to separate networks in
each subdomain) we augment the network with an additional level set field as proposed in [60].
Figure 5 (right) shows three different networks studied. Both KAN architectures use a multilevel training,
with the coarsest level containing 4 splines. The number of splines doubles at each subsequent finer level.
The networks are trained using Adam. Additional hyperparameters including loss term weightings can be
found in the Supplemental Material. The loss and error as a function of epoch are shown in Figure 6 for
14
LV (θ) =
X
⃗x∈V
∇·(ϵ(⃗x) ∇uN(⃗x))−f(⃗x)
2
LB(θ) =
X
⃗x∈B
uN(⃗x)
2
LI(θ) =
X
⃗x∈I
(ϵl∇uN(⃗xl)−ϵr∇uN(⃗xr))·[1, 0]
2
L(θ) = γV LV (θ) + γB LB(θ) + γI LI(θ)
Type
Layers
Basis
# Param.
KAN
[2,5,1]
Spline 140, 220, 380, 700
KAN
[2,5,1]
ReLU 140, 220, 380, 700
MLP [2,16,16,1] ReLU
352
Figure 5: For the 2d Possion problem in Sec. 5.2.1 (left) the volume, boundary and interface components of the
PINN loss, and (right) multilevel KAN and MLP architectures and parameter counts. The neural network uN has an
assumed dependence on parameters θ.
KAN with a spline basis (left), KAN with a ReLU basis (middle), and vanilla MLPs (right). The vertical
light gray dashed lines indicate an increase in the number of splines as the multilevel algorithm changes levels.
Both the multilevel KAN with spline basis and the vanilla MLP achieve small loss and small error. Multilevel
training with the ReLU basis fails to make progress however, and stagnates slightly below O(1) relative
ℓ2-error. Note that as the spline case, and the ReLU case form the same approximation space, the training
dynamics alone account for this difference. We hypothesize that the good performance of the spline basis is a
result of learning progressively higher frequency modes, as suggested by the theory developed in Section 3.
We also see the substantial advantages provided by multilevel training. The multilevel KAN with a spline
basis achieves smaller relative error faster than a comparable MLP, with significantly less noise in the actual
error with respect to epoch. This latter point is particularly important for robustness and generalization
when the target solution is not known. Returning to the multilevel KAN training, we also emphasize the clear
stair-casing effect in the multilevel training. For each refinement, particularly the refinements at 1250 and 2500
epochs, the loss and error have largely plateaued before refinement, and immediately after refinement we see
rapid decrease in loss and error, demonstrating how the model immediately takes advantages of its increased
expressivity. This behavior is indicative of a successful multilevel hierarchy and training methodology, and
also something we have not seen anywhere in the literature studying multilevel methods for machine learning.
0
1000
2000
3000
4000
5000
Epochs
10
2
10
1
100
101
Loss
2d Poisson: KAN Spline
Loss
Rel. l2 Error
Abs. l  Error
0
1000
2000
3000
4000
5000
Epochs
10
2
10
1
100
101
Loss
2d Poisson: KAN ReLU
0
1000
2000
3000
4000
5000
Epochs
10
2
10
1
100
101
Loss
2d Poisson: MLP ReLU
10
1
100
Error
10
1
100
Error
10
1
100
Error
Figure 6: 2d Poisson: Plots of loss and error vs. epoch for multilevel training of KANs under a spline basis (left),
multilevel training of KANs under a ReLU basis (center), and training of comparable MLP (right). The KAN Spline
and KAN ReLU are identical in terms of approximation power, yet differences in multilevel training performance
suggest that the relaxation for KAN Spline complements the refinement strategy.
5.2.2
1d Burger’s
Next we consider a short example training a PINN for 1d Burger’s equation ut+uux−νuxx = 0 with ν = 10−2
as a physical problem with inherently lower regularity. The solution is represented on space-time collocation
points on a 64 × 64 grid, and the entire batch is used each optimization step. We use weight-regularized
Adam and additionally employ a exponentially-cyclic learning rate scheduler as done in other places, e.g.
[64]. We run for 10000 steps for the basis results; for refinement, we use [3200, 0, 0] epochs for our coarse
15
model, [0, 0, 800] for the fine model (one level coarser than the regression problems), and [800, 400, 200] for
the multilevel model. Given the poor performance of the ReLU basis demonstrated previously, we only show
results using the spline basis for this problem. Results are shown in Table 3. The KAN architectures - even
the coarsest ones - outperform comparable MLP architectures in terms of training loss. Multilevel training is
where we see significant improvement, obtaining 2–3 orders of magnitude better accuracy than stand alone
KANs or MLPs on fine or coarse architectures, for comparable amounts of work.
Table 3: Accuracy for PINN problem, comparing the effects of geometric refinement of the spline knots for the KAN
basis. Comparable MLPs are included. Standard deviations computed across random initializations (N = 5).
Type
Layers
Fidelity
# Param.
Loss: mean (stdev)
KAN
[2, 20, 20, 1]
coarse
3400
6.635 × 10−3 (4.060 × 10−3)
KAN
[2, 20, 20, 1]
fine
9700
4.072 × 10−3 (2.514 × 10−3)
KAN
[2, 20, 20, 1]
multilevel
9700
2.402 × 10−5 (1.897 × 10−5)
MLP
[2, 20, 20, 1]
500
2.334 × 10−2 (1.740 × 10−3)
MLP
[2, 56, 56, 1]
3416
1.734 × 10−2(7.989 × 10−3)
5.2.3
Allen-Cahn Equation
Last, we consider a PINN problem of learning the solution to the Allen-Cahn equation,
∂tu(x, t) = −ϵ∂xxu(x, t) + 5u(x, t)3 −5u(x, t)
for (x, t) ∈[−1, 1] × [0, 1]
u(x, 0) =x2 cos(πx)
for (x, t) ∈[−1, 1] × {0}.
We use this to again demonstrate the power of multilevel training, as well as the spectral shaping in model
output that results from the multilevel training.
This equation has stable attractors as time increases at u = ±1 and an unstable fixed point at u = 0 that,
while minimizing the residual of the PDE, yields a solution that is incompatible with the initial condition.
As in the previous examples, we use residual-based attention during training, but otherwise do not use any of
the specialized modification and training techniques that are prevalent in state-of-the-art solutions, including
(but not limited to) time-causality, more advanced optimizers, and adaptive sampling of collocation points.
The point here is to emphasize that the multilevel training of KANs for PINNs is fast and robust out of the
box, without any modifications. We train each model with Adam optimizer with a learning rate of 0.001 for
2500 steps at each resolution, using a sigmoid normalization layer for a [2, 5, 5, 1] architecture using cubic
b-splines starting at a resolution of three interior spline knots equispaced on the interval [−1, 1]. The residual
during training is evaluated for the loss at 20, 000 collocation points randomly chosen in the domain.
The training loss histories for both bases, and a similarly-sized MLP, are shown in Figure 7, along with
the obtained physical solution. As previously, we see substantial benefits from multilevel training in the
spline basis, including immediate acceleration in training and reduction in loss at each refinement level. In
contrast, the ReLU basis is unable to exploit the increased network capacity from refinement, resulting in
a very poor solution. Moreover, a conventional MLP of similar size performs similarly to the ReLU KAN,
failing to capture any meaningful structure in the solution.
We further examine the residuals and spectra that arise in multilevel training of the spline-based KANs
in Figure 8 (similar plots for ReLU-based KANs can be found in Supplementary Material). Of note, we
clearly see that when using the spline basis, refinement provides not only better accuracy, but also substantial
differences in the spectrum of the Fourier modes in the residual: the energy in the Fourier modes decrease
with refinement, and the support of the Fourier modes active in the residual widen as we refine the spline
representations. These results reinforce the conclusions of our theory from the previous sections, that training
hierarchically in the spline basis enables targeted improvements of higher Fourier modes with refinement. In
contrast, the ReLU networks exhibit some improvement with increasing spline resolution, but the spectra
remains narrow – as spectral bias implies that multilevel training does not happen in a geometric space in
which we can exploit multigrid-style refinement – and as a result, the accuracy of the model suffers, even
though both architectures have the same approximation capabilities and belong to the same class.
16
0
2000
4000
6000
8000
10000
Epoch
10
5
10
4
10
3
10
2
10
1
Loss
Multilevel ReLU KAN: Loss History
Loss
0.0
0.2
0.4
0.6
0.8
1.0
t
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
1.00
x
Multilevel ReLU KAN: Solution u
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
u
0
2000
4000
6000
8000
10000
Epoch
10
5
10
4
10
3
10
2
10
1
Loss
Multilevel Spline KAN: Loss History
Loss
0.0
0.2
0.4
0.6
0.8
1.0
t
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
1.00
x
Multilevel Spline KAN: Solution u
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
u
0
2000
4000
6000
8000
10000
Epoch
10
5
10
4
10
3
10
2
10
1
Loss
MLP: Loss History
Loss
0.0
0.2
0.4
0.6
0.8
1.0
t
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
1.00
x
MLP: Solution u
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
u
Figure 7: Training histories for multilevel refinement of equivalent KAN architectures in both ReLU and B-spline
bases, with a similarly-sized MLP for comparison.
6
Conclusion
We have presented a theoretical and algorithmic framework for understanding and efficiently training
spline-based Kolmogorov-Arnold Networks using multilevel principles. Our main contributions address
both fundamental properties of KANs and practical training challenges. From a theoretical perspective, we
established that KANs with spline basis functions of order r are equivalent to multichannel MLPs with power
ReLU activations through a specific linear change of basis, where the transformation matrix A[r] corresponds
to a finite-difference discretization of the rth derivative. This equivalence yields immediate algorithmic
benefits in a non-recursive implementation of spline-based KANs that is faster than the standard Cox-de
Boor implementation. More importantly, our analysis reveals fundamental differences in how gradient-based
optimization behaves under different basis representations, despite their equivalence as forward operators. The
change of basis matrix A[r] acts as a preconditioner that dramatically affects training dynamics. Specifically,
gradient descent in the multichannel MLP (ReLU) basis heavily prioritizes smooth functions over oscillatory
ones by orders-of-magnitude scaling. In contrast, the natural spline basis enables strong feature localization
through compact support, allowing the network to efficiently learn functions with sharp gradients and low
regularity. This theoretical understanding provides rigorous justification for KANs’ observed advantages in
capturing complex, nonsmooth functions.
Building on these insights, we developed an efficient multilevel training framework based on uniform knot
refinement. We introduced the concept of properly nested hierarchies for multilevel optimization, ensuring
that a coarse model preserves the functional approximation achieved at finer levels—a critical property that
17
0.0
0.2
0.4
0.6
0.8
1.0
t
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
1.00
x
u4(x, t) (coarsest)
0.0
0.2
0.4
0.6
0.8
1.0
t
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
1.00
x
L(u4)(x, t) (coarsest)
200
100
0
100
200
t
200
100
0
100
200
x
FFT[L(u4)](
x,
t)
200
0
200
10
2
10
1
100
101
102
103
104
105
FFT along 
= 0
t = 0
x = 0
0.0
0.2
0.4
0.6
0.8
1.0
t
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
1.00
x
u3(x, t)
0.0
0.2
0.4
0.6
0.8
1.0
t
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
1.00
x
L(u3)(x, t)
200
100
0
100
200
t
200
100
0
100
200
x
FFT[L(u3)](
x,
t)
200
0
200
10
2
10
1
100
101
102
103
104
105
FFT along 
= 0
t = 0
x = 0
0.0
0.2
0.4
0.6
0.8
1.0
t
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
1.00
x
u2(x, t)
0.0
0.2
0.4
0.6
0.8
1.0
t
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
1.00
x
L(u2)(x, t)
200
100
0
100
200
t
200
100
0
100
200
x
FFT[L(u2)](
x,
t)
200
0
200
10
2
10
1
100
101
102
103
104
105
FFT along 
= 0
t = 0
x = 0
0.0
0.2
0.4
0.6
0.8
1.0
t
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
1.00
x
u1(x, t) (finest)
0.0
0.2
0.4
0.6
0.8
1.0
t
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
1.00
x
L(u1)(x, t) (finest)
200
100
0
100
200
t
200
100
0
100
200
x
FFT[L(u1)](
x,
t)
200
0
200
10
2
10
1
100
101
102
103
104
105
FFT along 
= 0
t = 0
x = 0
1.0
0.5
0.0
0.5
Solution u (x, t)
8
6
4
2
log10 |Residual| 
2
0
2
4
FFT magnitude (log10)
Figure 8: Plots of the trained B-spline-basis solution (leftmost) for the Allen-Cahn Equation in Section 5.2.3, residual
in log scale (left center), the Fourier transform of residual (right center), and cross-sections of the Fourier transform
along the axes ωt = 0 and ωx = 0 (rightmost). Each row displays the output after training at each level of refinement,
from coarsest (top) to finest (bottom). The first three columns share the same colorbar shown at the bottom of the
column.
prevents interpolated models from undoing progress. When combined with gradient-based descent methods
in the natural spline basis, which automatically provides complementary relaxation across hierarchy levels,
this framework achieves remarkable improvements: our numerical experiments consistently demonstrate 2-3
orders of magnitude better accuracy achieved compared to standard training methods or comparable MLPs,
while maintaining computational efficiency. In contrast, we also showed that attempting multilevel training
with the ReLU basis formulation provides effectively zero improvement over just using the coarse model,
confirming that successful multilevel methods require both proper nesting and complementary optimization
dynamics across levels. This principle has been elusive in multilevel machine learning but is naturally satisfied
by KANs in their native spline representation.
More broadly, our multilevel framework offers a principled demonstration that, with appropriate structure
18
and complementary dynamics across levels, multigrid ideas can indeed provide the efficiency gains in neural
network training that they have long delivered in scientific computing. Future work will consider multilevel
cycling, and extensions to other architectures and types of coarsening and refinement.
A
Notational Shift for MLP Architectures
Conventionally, an MLP with L hidden layers, starting with an input x = x(0), has each layer ℓ= 0, . . . , L −
1 expressed as x(ℓ+1) = σ
 W (ℓ)x(ℓ) + b(ℓ)
, with the final output NN(x) = x(L+1) = W (L)x(ℓ). This
compositional structure can be broken down more granularly, as
x(ℓ+ 1
2 ) = W (ℓ)x(ℓ),
x(ℓ+1) = σ

x(ℓ+ 1
2 ) + b(ℓ)
,
(29)
where then the final layer omits the nonlinear activation step so that NN(x) = x(L+ 1
2 ) instead of NN(x) =
x(L+1).
The rearranged layers used in our analysis, which post-multiply layers by learnable weights instead of
pre-multiplying by learnable weights, simply combine the expressions in (29) for ℓ= 1, . . . , L −1 into a
single step, x(ℓ+ 1
2 ) = W (ℓ)σ

x(ℓ−1
2 ) + b(ℓ−1)
, yielding the same computation. Notationally, we substitute
t(ℓ) = −b(ℓ), to match the conventions from spline literature. This yields our ultimate expression for each
layer,
x(ℓ+ 1
2 ) = W (ℓ)σ

x(ℓ−1
2 ) −t(ℓ−1)
.
(30)
B
Proofs regarding change of basis matrix A[r]
First, we prove the following result regarding ReLU functions.
Proposition 2. For any scalars a, b, and for r > 1,
(x −a)ReLU(x −b)r = ReLU(x −b)r+1 + (b −a)ReLU(x −b)r.
(31)
Proof. If x ≤b, then both sides equal zero. Thus, it suffices to consider x > b, where then ReLU(x−b) = x−b.
Thus, it suffices to show that (x −a)(x −b)r = (x −b)r+1 + (b −a)(x −b)r. Indeed, factoring the righthand
side, we see
(x −b)r+1 + (b −a)(x −b)r = (x −b)r ((x −b) + (b −a)) = (x −b)r(x −a),
(32)
which is the desired result.
We now derive a recursive definition for A[r], as stated in (5).
Lemma 7 (Lemma 2). For r > 1, let A[r−1] denote splines of order r −1 constructed on knots for splines of
order r. Then the matrix A[r] is defined entry-wise as:
A[r]
ij =
1
ti+r−1 −ti
A[r−1]
ij
−
1
ti+r −ti+1
A[r−1]
i+1,j,
(33)
where we define A[r−1]
n+r,: = 0 to account for the special case of the final row i = n + r −1.
Proof. It is easily verified that
A[1]
ij =
(
1
j = i
−1
j = i + 1 .
(34)
19
We now prove the main statement by induction. For the base case of r = 2, we have the known (e.g. [26])
result that
A[2]
ij =











1
ti+1−ti
j = i
−

1
ti+1−ti +
1
ti+2−ti+1

j = i + 1
1
ti+2−ti+1
j = i + 2
0
else
.
(35)
Directly from (34) and (35), we see that A[2] satisfies Equation (33) for r = 2. We proceed now to the
inductive step for r ≥2. Suppose the result holds through s = 1, . . . , r −1. By the recurrence relation used
to define b[r]
i , we have
b[r]
i (x) =
x −ti
ti+r−1 −ti
b[r−1]
i
(x) +
ti+r −x
ti+r −ti+1
b[r−1]
i+1 (x)
=

1
ti+r−1 −ti
 X
j
A[r−1]
ij
(x −ti) ReLU(x −tj)r−2−

1
ti+r −ti+1
 X
j
A[r−1]
i+1,j (x −ti+r) ReLU(x −tj)r−2.
By Lemma 2,
b[r]
i (x) =

1
ti+r−1 −ti
 X
j
A[r−1]
ij
(x −ti) ReLU(x −tj)r−2−

1
ti+r −ti+1
 X
j
A[r−1]
i+1,j (x −ti+r) ReLU(x −tj)r−2
=

1
ti+r−1 −ti
 X
j
A[r−1]
ij
 ReLU(x −tj)r−1 + (tj −ti)ReLU(x −tj)r−2
−

1
ti+r −ti+1
 X
j
A[r−1]
i+1,j
 ReLU(x −tj)r−1 + (tj −ti+r)ReLU(x −tj)r−2
.
Since b[r]
i
∈Cr−2([a, b]) and ReLU( ·−tj)r−1 ∈Cr−2([a, b]) but ReLU( ·−tj)r−2 /∈Cr−2([a, b]), the coefficients
of the ReLU(· −tj)r−2 terms must cancel. This is specifically because expanding the ReLU( · −tj)r−2 terms
as piecewise polynomials, none of the expanded terms are sufficiently differentiable at the knot, and thus
all terms must cancel for the full summation to be in Cr−2([a, b]). This can also be shown directly through
laborious arithmetic calculation. Therefore,
b[r]
i (x) =

1
ti+r−1 −ti
 X
j
A[r−1]
ij
ReLU(x −tj)r−1−

1
ti+r −ti+1
 X
j
A[r−1]
i+1,jReLU(x −tj)r−1
=
X
j

1
ti+r−1 −ti
A[r−1]
ij
−
1
ti+r −ti+1
A[r−1]
i+1,j

ReLU(x −tj)r−1,
which completes the proof.
We now derive a closed-form for A[r] for uniform knots. For r = 2, this is the matrix in [26], A = I−2S+S2,
for shift operator Sej = ej+1.
Corollary 1 (Corollary 1). In the case of uniform knots, with spacing h = ti −ti−1 = 1
n, A[r] takes the
direct form
A[r] =
h1−r
(r −1)!(A[1])r.
(36)
20
Moreover, A[r] is upper triangular Toeplitz, with entries
A[r]
ij =
(
(−1)j−i
(j−i)! (r−j+i)!
r
hr−1
i ≤j ≤i + r
0
else
.
(37)
Proof. This follows by noting that if ti+r−1 −ti = ti+r −ti+1 = h(r −1), (5) corresponds to a left scaling of
A[r−1] by
1
h(r−1)A[1] (34). Repeating this for r = 2, 3, ... yields (36). For the Toeplitz property, from (36) we
see that A[r] is a power of A[1]. Since A[1] is an upper bidiagonal Toeplitz matrix, it follows that A[r] is also
upper triangular Toeplitz (see, e.g. [55, Lemma 22]), with coefficients given in (37).
Acknowledgements
This work was funded in part by the National Nuclear Security Administration Interlab Laboratory Directed
Research and Development program under project number 20250861ER. Los Alamos National Laboratory
report number LA-UR-26-21552. This article has been authored by employees of National Technology &
Engineering Solutions of Sandia, LLC under Contract No. DE-NA0003525 with the U.S. Department of
Energy (DOE). The employees own all right, title and interest in and to the article and are solely responsible
for its contents. The United States Government retains and the publisher, by accepting the article for
publication, acknowledges that the United States Government retains a non-exclusive, paid-up, irrevocable,
world-wide license to publish or reproduce the published form of this article or allow others to do so, for
United States Government purposes. The DOE will provide public access to these results of federally
sponsored research in accordance with the DOE Public Access Plan https://www.energy.gov/downloads/
doe-public-access-plan BSS would like to thank Achi Brandt and Oren Livne for many early and engaging
discussions on multilevel methods for machine learning.
References
[1] D. W. Abueidda, P. Pantidis, and M. E. Mobasher, Deepokan: Deep operator network based on
kolmogorov arnold networks for mechanics problems, arXiv preprint arXiv:2405.19143, (2024).
[2] J. Actor, Computation for the kolmogorov superposition theorem, master’s thesis, Rice University, 2018.
[3] S. J. Anagnostopoulos, J. D. Toscano, N. Stergiopulos, and G. E. Karniadakis, Residual-
based attention in physics-informed neural networks, Computer Methods in Applied Mechanics and En-
gineering, 421 (2024), p. 116805, https://doi.org/https://doi.org/10.1016/j.cma.2024.116805,
https://www.sciencedirect.com/science/article/pii/S0045782524000616.
[4] C. Botsaris, Differential gradient methods, Journal of Mathematical Analysis and Applications, 63
(1978), pp. 177–198, https://doi.org/10.1016/0022-247x(78)90114-2.
[5] J. Braun and M. Griebel, On a constructive proof of kolmogorov’s superposition theorem, Constructive
approximation, 30 (2009), pp. 653–675.
[6] R. Bresson, G. Nikolentzos, G. Panagopoulos, M. Chatzianastasis, J. Pang, and M. Vazir-
giannis, Kagnns: Kolmogorov-arnold networks meet graph learning, arXiv preprint arXiv:2406.18380,
(2024).
[7] A. Cacciatore, V. Morelli, F. Paganica, E. Frontoni, L. Migliorelli, and D. Berardini, A
preliminary study on continual learning in computer vision using kolmogorov-arnold networks, arXiv
preprint arXiv:2409.13550, (2024).
[8] Y. Cang, L. Shi, et al., Can kan work? exploring the potential of kolmogorov-arnold networks in
computer vision, arXiv preprint arXiv:2411.06727, (2024).
[9] B. Chang, L. Meng, E. Haber, F. Tung, and D. Begert, Multi-level residual networks from
dynamical systems view, in International Conference on Learning Representations, 2018.
21
[10] R. T. Chen, Y. Rubanova, J. Bettencourt, and D. K. Duvenaud, Neural ordinary differential
equations, Advances in neural information processing systems, 31 (2018).
[11] M. Cheon, Demonstrating the efficacy of kolmogorov-arnold networks in vision tasks, arXiv preprint
arXiv:2406.14916, (2024).
[12] C. K. Chui, Multivariate splines, SIAM, 1988.
[13] E. C. Cyr, J. Hahne, N. S. Moore, J. B. Schroder, B. S. Southworth, and D. A. Var-
gas, Torchbraid: High-performance layer-parallel training of deep neural networks with mpi and gpu
acceleration, ACM Transactions on Mathematical Software, 51 (2025), pp. 1–30.
[14] C. De Boor, A practical guide to splines, vol. 27, springer New York, 1978.
[15] C. Dong, L. Zheng, and W. Chen, Kolmogorov-arnold networks (kan) for time series classification
and robust analysis, arXiv preprint arXiv:2408.07314, (2024).
[16] M. Eliasof, J. Ephrath, L. Ruthotto, and E. Treister, MGIC: Multigrid-in-channels neural
network architectures, SIAM Journal on Scientific Computing, 45 (2023), pp. S307–S328, https://doi.
org/10.1137/21m1430194.
[17] M. Feischl, A. Rieder, and F. Zehetgruber, Towards optimal hierarchical training of neural
networks, arXiv, (2024), https://doi.org/10.48550/arxiv.2407.02242, https://arxiv.org/abs/
2407.02242.
[18] L. Gaedke-Merzh¨auser, A. Kopaniˇc´akov´a, and R. Krause, Multilevel minimization for deep
residual networks, ESAIM: Proceedings and Surveys, 71 (2021), pp. 131–144, https://doi.org/10.
1051/proc/202171131.
[19] Y. Gao and V. Y. Tan, On the convergence of (stochastic) gradient descent for kolmogorov–arnold
networks, arXiv preprint arXiv:2410.08041, (2024).
[20] S. G¨unther, L. Ruthotto, J. B. Schroder, E. C. Cyr, and N. R. Gauger, Layer-parallel
training of deep residual neural networks, SIAM Journal on Mathematics of Data Science, 2 (2020),
pp. 1–23, https://doi.org/10.1137/19m1247620.
[21] E. Haber and L. Ruthotto, Stable architectures for deep neural networks, Inverse problems, 34
(2017), p. 014004.
[22] W. Hackbusch, Multi-grid methods and applications, vol. 4, Springer Science & Business Media, 2013.
[23] J. He and J. Xu, MgNet: A unified framework of multigrid and convolutional neural network, Science
China Mathematics, 62 (2019), pp. 1331–1354, https://doi.org/10.1007/s11425-019-9547-2, https:
//arxiv.org/abs/1901.10415.
[24] Y. He, Y. Xie, Z. Yuan, and L. Sun, Mlp-kan: Unifying deep representation and function learning,
arXiv preprint arXiv:2410.03027, (2024).
[25] K. H¨ollig, Finite element methods with B-splines, SIAM, 2003.
[26] Q. Hong, J. W. Siegel, Q. Tan, and J. Xu, On the activation function dependence of the spectral
bias of neural networks, arXiv preprint arXiv:2208.04924, (2022).
[27] Y. Hou and D. Zhang, A comprehensive survey on kolmogorov arnold networks (kan), arXiv preprint
arXiv:2407.11075, (2024).
[28] A. A. Howard, B. Jacob, S. H. Murphy, A. Heinlein, and P. Stinis, Finite basis kolmogorov-
arnold networks: domain decomposition for data-driven and physics-informed problems, arXiv preprint
arXiv:2406.19662, (2024).
22
[29] B. Igelnik and N. Parikh, Kolmogorov’s spline network, IEEE transactions on neural networks, 14
(2003), pp. 725–733.
[30] B. Jacob, A. A. Howard, and P. Stinis, Spikans: Separable physics-informed kolmogorov-arnold
networks, arXiv preprint arXiv:2411.06286, (2024).
[31] A. Jacot, F. Gabriel, and C. Hongler, Neural tangent kernel: Convergence and generalization in
neural networks, Advances in neural information processing systems, 31 (2018).
[32] T.-W. Ke, M. Maire, and S. X. Yu, Multigrid neural architectures, in Proceedings of the IEEE
Conference on Computer Vision and Pattern Recognition (CVPR), 2017, pp. 6665–6673.
[33] M. Kiamari, M. Kiamari, and B. Krishnamachari, Gkan: Graph kolmogorov-arnold networks,
arXiv preprint arXiv:2406.06470, (2024).
[34] D. P. Kingma, M. Welling, et al., Auto-encoding variational bayes, 2013.
[35] B. C. Koenig, S. Kim, and S. Deng, Kan-odes: Kolmogorov–arnold network ordinary differential
equations for learning dynamical systems and hidden physics, Computer Methods in Applied Mechanics
and Engineering, 432 (2024), p. 117397.
[36] T. G. Kolda and B. W. Bader, Tensor decompositions and applications, SIAM review, 51 (2009),
pp. 455–500.
[37] A. N. Kolmogorov, On the representation of continuous functions of many variables by superposition
of continuous functions of one variable and addition, in Doklady Akademii Nauk, vol. 114:5, Russian
Academy of Sciences, 1957, pp. 953–956.
[38] A. Kopaniˇc´akov´a and R. Krause, Globally convergent multilevel training of deep residual net-
works, SIAM Journal on Scientific Computing, 0 (2022), pp. S254–S280, https://doi.org/10.1137/
21m1434076.
[39] P.-E. Leni, Y. D. Fougerolle, and F. Truchetet, The kolmogorov spline network for image
processing, in Image Processing: Concepts, Methodologies, Tools, and Applications, IGI Global, 2013,
pp. 54–78.
[40] Z. Liu, Y. Wang, S. Vaidya, F. Ruehle, J. Halverson, M. Soljaˇci´c, T. Y. Hou, and
M. Tegmark, Kan: Kolmogorov-arnold networks, arXiv preprint arXiv:2404.19756, (2024).
[41] G. Lorentz, Metric entropy, widths, and superpositions of functions, The American Mathematical
Monthly, 69 (1962), pp. 469–485.
[42] W. S. McCulloch and W. Pitts, A logical calculus of the ideas immanent in nervous activity, The
bulletin of mathematical biophysics, 5 (1943), pp. 115–133.
[43] A. Noorizadegan, S. Wang, and L. Ling, A practitioner’s guide to kolmogorov-arnold networks,
arXiv preprint arXiv:2510.25781, (2025).
[44] S. Patra, S. Panda, B. K. Parida, M. Arya, K. Jacobs, D. I. Bondar, and A. Sen, Physics
informed kolmogorov-arnold neural networks for dynamical analysis via efficent-kan and wav-kan, arXiv
preprint arXiv:2407.18373, (2024).
[45] A. Pinkus, Approximation theory of the mlp model in neural networks, Acta numerica, 8 (1999),
pp. 143–195.
[46] Q. Qiu, T. Zhu, H. Gong, L. Chen, and H. Ning, Relu-kan: New kolmogorov-arnold networks that
only need matrix addition, dot multiplication, and relu, arXiv preprint arXiv:2406.02075, (2024).
[47] R. Qiu, Y. Miao, S. Wang, Y. Zhu, L. Yu, and X.-S. Gao, Powermlp: An efficient version of kan,
in Proceedings of the AAAI Conference on Artificial Intelligence, vol. 39:19, 2025, pp. 20069–20076.
23
[48] S. Rigas, M. Papachristou, T. Papadopoulos, F. Anagnostopoulos, and G. Alexandridis,
Adaptive training of grid-dependent physics-informed kolmogorov-arnold networks, IEEE Access, (2024).
[49] F. Rosenblatt, The perceptron: a probabilistic model for information storage and organization in the
brain., Psychological review, 65 (1958), p. 386.
[50] L. Ruthotto and E. Haber, Deep neural networks motivated by partial differential equations, Journal
of Mathematical Imaging and Vision, 62 (2020), pp. 352–364.
[51] K. Shukla, J. D. Toscano, Z. Wang, Z. Zou, and G. E. Karniadakis, A comprehensive and fair
comparison between mlp and kan representations for differential equations and operator networks, arXiv
preprint arXiv:2406.02917, (2024).
[52] N. J. A. Sloane and S. Plouffe, The encyclopedia of integer sequences, (No Title), (1995).
[53] C. C. So and S. P. Yung, Higher-order-relu-kans (hrkans) for solving physics-informed neural networks
(pinns) more accurately, robustly and faster, arXiv preprint arXiv:2409.14248, (2024).
[54] S. Somvanshi, S. A. Javed, M. M. Islam, D. Pandit, and S. Das, A survey on kolmogorov-arnold
network, arXiv preprint arXiv:2411.06078, (2024).
[55] B. S. Southworth, Necessary conditions and tight two-level convergence bounds for parareal and
multigrid reduction in time, SIAM Journal on Matrix Analysis and Applications, 40 (2019), pp. 564–608.
[56] D. A. Sprecher, A universal mapping for kolmogorov’s superposition theorem, Neural networks, 6
(1993), pp. 1089–1094.
[57] D. A. Sprecher, From Algebra to Computational Algorithms: Kolmogorov and Hilbert’s Problem 13,
Docent Press, 2017.
[58] P. Tilli, Singular values and eigenvalues of non-hermitian block toeplitz matrices, Linear algebra and
its applications, 272 (1998), pp. 59–89.
[59] J. D. Toscano, V. Oommen, A. J. Varghese, Z. Zou, N. A. Daryakenari, C. Wu, and G. E.
Karniadakis, From pinns to pikans: Recent advances in physics-informed machine learning, arXiv
preprint arXiv:2410.13228, (2024).
[60] Y.-H. Tseng, T.-S. Lin, W.-F. Hu, and M.-C. Lai, A cusp-capturing pinn for elliptic interface
problems, Journal of Computational Physics, 491 (2023), p. 112359.
[61] C. J. Vaca-Rubio, L. Blanco, R. Pereira, and M. Caus, Kolmogorov-arnold networks (kans) for
time series analysis, arXiv preprint arXiv:2405.08790, (2024).
[62] A. Vaswani, Attention is all you need, Advances in Neural Information Processing Systems, (2017).
[63] S. Wang, S. Sankaran, X. Fan, P. Stinis, and P. Perdikaris, Simulating three-dimensional
turbulence with physics-informed neural networks, arXiv preprint arXiv:2507.08972, (2025).
[64] S. Wang, S. Sankaran, H. Wang, and P. Perdikaris, An expert’s guide to training physics-informed
neural networks, arXiv preprint arXiv:2308.08468, (2023).
[65] Y. Wu, T. Su, B. Du, S. Hu, J. Xiong, and D. Pan, Kolmogorov–arnold network made learning
physics laws simple, The Journal of Physical Chemistry Letters, 15 (2024), pp. 12393–12400.
[66] R. Yu, W. Yu, and X. Wang, Kan or mlp: A fairer comparison, arXiv preprint arXiv:2407.16674,
(2024).
[67] C. Zeng, J. Wang, H. Shen, and Q. Wang, Kan versus mlp on irregular or noisy functions, arXiv
preprint arXiv:2408.07906, (2024).
24
Supplementary Material
C
Neural tangent kernel and change of basis
The Neural Tangent Kernel (NTK) is a powerful tool for understanding the training dynamics of neural
networks in the infinite-width limit [31]. The NTK describes how the network’s output changes with respect
to its parameters during training. For a neural network f(x; w) with parameters w, the NTK is defined as
W(x, x′) :=
D
∂f(x;w)
∂w
, ∂f(x′;w)
∂w
E
. For a batch of k data points, we can organize these gradients into a Jacobian
matrix J ∈Rk×Nw, where each row contains ∂f(x(i);w)
∂w
for the i-th data point. The NTK matrix for this
batch is then given by the Gram matrix NTK = JJT ∈Rk×k, whose (i, j)-th entry is precisely W(x(i), x(j)).
Under our change of basis from spline weights u to ReLU weights w = AT u, the Jacobian transforms as
Jg = JfAT , yielding NTK[r]
S = JfA[r](A[r])T JT
f for the spline basis.
The following theorem introduces a specific result from the field of block-Toeplitz operator theory, which
is used in proving the theorem that follows.
Theorem 1 (Maximum singular value of block-Toeplitz operators [58]). Let TN(F) be an N ×N block-Toeplitz
matrix, with continuous generating function F(x) : [0, 2π] →Cm×m. Then, the maximum singular value is
bounded above by
σmax(TN(F)) ≤
max
x∈[0,2π] σmax(F(x)),
for all N ∈N.
We now relate the spectral radius of the NTK matrix under a ReLU and spline basis.
Theorem 2. For symmetric positive semidefinite M let ρ(M) ≥0 denote the spectral radius. Then for
uniform knot spacing,
ρ(NTK[r]
S ) ≤4ρ(NTKR).
(38)
Proof. Define an auxiliary equivalent ReLUr−1 basis φ[r]
i (x) = ReLU
  x−ti
h
r−1 . As ReLU is a homogeneous
function with respect to positive scalars, this basis is equivalent again to the ReLU basis.
We therefore repeat the process of the above construction, yielding an equivalent change-of-basis matrix
eA[r], where eA[r] =
1
h1−r A[r]. Let J denote the Jacobian of f with respect to the weights W, so that
NTKR = JJT ,
NTK[r]
S = JAAT JT ,
(39)
where A is the reordered block diagonal operator of layer-specific A[r].
Note that JJT and JAAT JT are symmetric with nonnegative eigenvalues, and largest eigenvalue given by
the square of the largest singular value of J and JA, respectively. Noting that the largest singular value of an
operator is given by the ℓ2-norm, by sub-multiplicativity ∥JA∥≤∥J∥∥A∥. Thus we will bound the spectrum
of JA by considering the maximum singular value of the change of basis matrix A. Recall in the correct
ordering A is a block-diagonal matrix, with diagonal blocks given by eA[r] for each layer. The maximum
singular value of a block-diagonal matrix is given by the maximum over maximum singular values of each
block. Thus, we will proceed by considering ∥eA[r]∥for arbitrary P, Q and fixed r.
From Corollary 1, for uniform knots eA[r] is upper triangular Toeplitz. Appealing to Toeplitz matrix
theory, asymptotically (in n) tight bounds can be placed on the maximum singular value of eA[r] (and thus
equivalently the maximum eigenvalue of eA[r]( eA[r])T ) by way of considering the operator’s generator function.
Let αℓdenote the Toeplitz coefficient for the ith diagonal of a Toeplitz matrix, where α0 is the diagonal, α−1
the first subdiagonal, and so on. Then the Toeplitz matrix corresponds with a Fourier generator function,
F(x) = P∞
ℓ=−∞αℓe−iℓx. In our case we have scalar (i.e. blocksize N = 1) generating function of eA[r] given by
Fr(x) = r
r
X
ℓ=0
(−1)ℓ
(ℓ)! (r −ℓ)! e−iℓx = r · (1 −eix)r
r!
= nr−1 (1 −eix)r
(r −1)! .
(40)
25
Thus from Theorem 1, we have for r ∈Z+
∥eA[r]∥≤max
x
|Fr(x)| =
2r
(r −1)! ≤4
for r ≥1,
(41)
which completes the proof.
D
Hyper-parameters and Specializations
The examples from this paper were run on Nvidia A100 GPUs with a variety of different problem configurations
and seeds.
D.1
Function Regression
The function regression example in Section 5.1 utilizes a dataset with 20000 random uniform points on the
grid [0.0001, 0.9999]2. The network output is normalized by an affine transformation to [0, 1]. The random
number generator seeds are fixed at 1234, and any ensemble of five runs utilizes seeds 1234 through 1238.
The optimizer is L-BFGS with a learning rate of 1.0.
D.2
Physics Informed Neural Networks (PINNs)
The 2d Poisson problem uses residual based attention (RBA) [3] applied to the volumetric term. Assume
their are NV = |V | points in set V , and initialize a weighting vector ⃗λ such that λi = 1 where i = 1 . . . N.
The RBA scheme provides the update rule
λi = (1 −µ)λi + µ
ei
maxj ej
where ei =
∇·(ϵ(⃗x) ∇uN(⃗x))−f(⃗x)
.
(42)
The weighting vector scales each point in the volumetric loss term and is consequently incorporated into the
gradient. If ei is relatively large the contribution of that error to the loss is more heavily weighted.
The multilevel KANs training algorithm employs a linear ramp of the learning rate at the start of training,
and at the transition between levels. In the tables we denote η0 as the starting learning rate, and η as the
final target learning rate. The number of steps (or epochs for single batch PINNs training) that is required
to transition between them is denoted SLR.
Section 5.2.1: 2d Poisson Hyper-Parameters
Parameter
Symbol
Value
Loss Scaling
ΓV
10−2
ΓI
10−1
ΓB
100
Volume Points
|V |
2401
Boundary Points
|B|
200
Interface Points
|I|
49
MLP Layers
[2, 16, 16, 1]
KAN Layers
[2, 5, 1]
KAN Spline Order
3
KAN Coarse Grid Size
4
Optimizer
Adam
Learning Rate
η
10−2
Initial Learning Rate
η0
10−4
Ramping Steps
SLR
10
RBA Damping
µ
10−4
26
The 1d Burger’s example uses random number generator seeds that start at 1234 and increase by 10 for
each new run.
Section 5.2.2: 1d Burger’s Hyper-Parameters
Parameter
Symbol
Value
Loss Scaling
ΓV
100
ΓB
100
Volume Points
|V |
4096
Initial Condition Points
|B|
64
Optimizer
Adam
Learning Rate
η
10−3
Cycle
SLR
100
Exponential Decay Parameter γ
0.9995
The Allen-Cahn example uses the random number generator seed 1234. It uses the Adam optimizer with
a linear learning rate scheduler over the first 10 epochs to increase the learning rate from 10−4 to 10−2.
Section 5.2.3: Allen-Cahn Hyper-Parameters
Parameter
Symbol
Value
Loss Scaling
ΓV
10−1
ΓB
100
Volume Points
|V |
251001
Initial Condition Points |B|
501
Optimizer
Adam
Learning Rate
η
10−2
E
Allen-Cahn ReLU training
See Figure 9.
27
0.0
0.2
0.4
0.6
0.8
1.0
t
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
1.00
x
u4(x, t) (coarsest)
0.0
0.2
0.4
0.6
0.8
1.0
t
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
1.00
x
L(u4)(x, t) (coarsest)
200
100
0
100
200
t
200
100
0
100
200
x
FFT[L(u4)](
x,
t)
200
0
200
10
2
10
1
100
101
102
103
104
105
FFT along 
= 0
t = 0
x = 0
0.0
0.2
0.4
0.6
0.8
1.0
t
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
1.00
x
u3(x, t)
0.0
0.2
0.4
0.6
0.8
1.0
t
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
1.00
x
L(u3)(x, t)
200
100
0
100
200
t
200
100
0
100
200
x
FFT[L(u3)](
x,
t)
200
0
200
10
2
10
1
100
101
102
103
104
105
FFT along 
= 0
t = 0
x = 0
0.0
0.2
0.4
0.6
0.8
1.0
t
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
1.00
x
u2(x, t)
0.0
0.2
0.4
0.6
0.8
1.0
t
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
1.00
x
L(u2)(x, t)
200
100
0
100
200
t
200
100
0
100
200
x
FFT[L(u2)](
x,
t)
200
0
200
10
2
10
1
100
101
102
103
104
105
FFT along 
= 0
t = 0
x = 0
0.0
0.2
0.4
0.6
0.8
1.0
t
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
1.00
x
u1(x, t) (finest)
0.0
0.2
0.4
0.6
0.8
1.0
t
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
1.00
x
L(u1)(x, t) (finest)
200
100
0
100
200
t
200
100
0
100
200
x
FFT[L(u1)](
x,
t)
200
0
200
10
2
10
1
100
101
102
103
104
105
FFT along 
= 0
t = 0
x = 0
1.0
0.8
0.6
0.4
0.2
0.0
Solution u (x, t)
6
4
2
0
log10 |Residual| 
4
2
0
2
4
FFT magnitude (log10)
Figure 9: Plots of the trained ReLU-basis solution (leftmost) for the Allen-Cahn Equation, residual in log scale (left
center), the Fourier transform of residual (right center), and cross-sections of the Fourier transform along the axes
ωt = 0 and ωx = 0 (rightmost). Each row displays the output after training at each level of refinement, from coarsest
(top) to finest (bottom). The first three columns share the same colorbar shown at the bottom of the column.
28
