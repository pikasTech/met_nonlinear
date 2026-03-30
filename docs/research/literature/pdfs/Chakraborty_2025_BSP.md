**Creator**: LaTeX with hyperref

---

Binned Spectral Power Loss for Improved Prediction

of Chaotic Systems

Dibyajyoti Chakraborty∗

College of Information Sciences and Technology

Pennsylvania State University

University Park, PA, USA.

Arvind T. Mohan

Computational Physics and Methods

Los Alamos National Laboratory

Los Alamos, NM, USA

Romit Maulik

College of Information Sciences and Technology

Pennsylvania State University

University Park, PA, USA.

Abstract

Forecasting multiscale chaotic dynamical systems with deep learning remains a

formidable challenge due to the spectral bias of neural networks, which hinders the

accurate representation of fine-scale structures in long-term predictions. This issue

is exacerbated when models are deployed autoregressively, leading to compounding

errors and instability. In this work, we introduce a novel approach to mitigate the

spectral bias which we call the Binned Spectral Power (BSP) Loss. The BSP loss

is a frequency-domain loss function that adaptively weighs errors in predicting

both larger and smaller scales of the dataset. Unlike traditional losses that focus

on pointwise misfits, our BSP loss explicitly penalizes deviations in the energy

distribution across different scales, promoting stable and physically consistent

predictions. We demonstrate that the BSP loss mitigates the well-known problem of

spectral bias in deep learning. We further validate our approach for the data-driven

high-dimensional time-series forecasting of a range of benchmark chaotic systems

which are typically intractable due to spectral bias. Our results demonstrate that

the BSP loss significantly improves the stability and spectral accuracy of neural

forecasting models without requiring architectural modifications. By directly

targeting spectral consistency, our approach paves the way for more robust deep

learning models for long-term forecasting of chaotic dynamical systems.

1

Introduction

The improved forecasting of complex nonlinear dynamical systems is of vital importance to several

real-world applications such as in engineering [Kong et al., 2022], geoscience [Sun et al., 2024],

public health [Wang et al., 2021], and beyond. Frequently, the accurate modeling of such systems is

complicated by their multiscale nature and chaotic behavior. Physics-based models for such systems

are generally described as partial differential equations (PDE), the numerical solutions of which

require significant computational effort. For instance, the presence of multiscale behavior require very

fine spatial and temporal resolutions, when numerically solving such PDEs, which can be severely

limiting for real-time forecasting tasks [Harnish et al., 2021]. Chaotic systems also require the

assessment of statistics using ensembles of simulations, adding significant costs. This is one of they

key bottlenecks in a variety of applications in earth sciences, energy engineering and aeronautics.

One approach to addressing the aforementioned challenges is through the use of data-driven methods

for learning the time-evolution of such systems. In such methods, function approximation techniques

∗Corresponding author: d.chakraborty@psu.edu

Preprint. Under review.

arXiv:2502.00472v2  [cs.LG]  16 May 2025


!!! page 2 "Chakraborty_2025_BSP"

such as neural networks [Cybenko, 1989, McCulloch and Pitts, 1943], Gaussian processes [Santner,

2003], and neural operators [Chen and Chen, 1995], among others, are utilized to learn the map

between subsequent time-steps from training data. Subsequently, these trained models are deployed

autoregressively to perform roll-out forecasts for dynamics into the future. This approach holds

particular promise for systems where large volumes of data are available from open-sourced sim
ulations or observations. Recently, this approach to forecasting has been applied with remarkable

success to dynamical systems emerging in applications such as weather [Bi et al., 2022, Lam et al.,

2022, Pathak et al., 2022, Nguyen et al., 2023], climate [Guan et al., 2024, Watt-Meyer et al., 2023,

Rühling Cachay et al., 2024], nuclear fusion [Mehta et al., 2021, Burby et al., 2020, Li et al., 2024],

renewable energy [Sun et al., 2019, Wang et al., 2019], etc.

However, for several multiscale applications, purely data-driven forecast models suffer from a com
mon limitation that degrades their performance in comparison with physics-based solvers. This

pertains to an inability to capture the information at smaller scales in the spatial domain of the

dynamical system [Bonavita, 2024, Olivetti and Messori, 2024, Pasche et al., 2025, Mahesh et al.,

2024]. In the spectral space, these refer to the energy associated at higher wavenumbers. Conse
quently, data-driven models may be over or under-dissipative during autoregressive predictions which

eventually cause a significant disagreement with ground-truth and in worse-case scenarios, leading

to completely non-physical behavior [Chattopadhyay and Hassanzadeh, 2023]. These errors are

commonly understood to be caused by so-called spectral biases [Rahaman et al., 2019], defined

by the tendency of a neural network trained on a typical mean-squared-error loss function to op
timize the larger wavenumbers first while training. This phenomena has been observed across a

variety of architectures like generative adversarial networks [Schwarz et al., 2021, Chen et al., 2021],

transformers [Bhattamishra et al., 2022], state space models [Yu et al., 2024], physics-informed

neural networks [Chai et al., 2024], Kolmogorov-Arnold networks [Wang et al., 2024b], etc. The

mathematical relation to spectral biases is presented later in this manuscript.

Related Works : Significant research has focused on addressing the challenges of difficulty in

capturing high-frequency structures [Karniadakis et al., 2021, Lai et al., 2024, Chakraborty et al.,

2024, Chen et al., 2024]. A major direction of work involves architectural innovations in neural

networks aimed at mitigating spectral bias and improving resolution of fine-scale features. For

instance, Tancik et al. [2020] introduce Fourier feature mappings to enhance fully connected networks,

while the Hierarchical Attention Neural Operator (HANO) proposed by Liu et al. [2024] leverage

multilevel representations with self-attention and local aggregation to capture multiscale dependencies.

Similarly, diffusion models have shown promise by modeling the forecast as a sample from a

learnable stochastic process [Gao et al., 2023, Oommen et al., 2024, Luo et al., 2023]. PDE
Refiner [Lippe et al., 2023b] progressively refines predictions to capture both dominant and weak

frequency modes. Gestalt autoencoders [Liu et al., 2023] enhance reconstruction in both spatial

and spectral domains, while frequency-aware training strategies such as dynamic spectral weighting

have been proposed to prioritize specific wavenumber bands [Lin et al., 2023]. Multiscale neural

approximations and hierarchical discretization frameworks have also been used to improve fine-scale

information exchange and prediction quality [Barwey et al., 2023, Wang et al., 2020, Liu et al.,

2020, Khodakarami et al., 2025]. Some new approaches propose choices for hyperparameters or

data processing to improve the quality of the predictions [Cai et al., 2024]. Another direction is to

use hybrid techniques which combine numerical solvers with neural networks to improve energy

spectrum accuracy across scales [Shankar et al., 2023, Zhang et al., 2024]. Despite their effectiveness,

many of these methods involve complex architectural designs or heavy computational overhead.

We aim to address the following open question: How can we develop a universally adaptable method

that seamlessly integrates into any existing deep learning forecast architecture to mitigate spectral

bias and improve stability while maintaining computational efficiency? In this work, we propose

a novel approach to tackle this challenge, with a particular focus on its application in forecasting

chaotic dynamical systems.

Contributions : The contributions of this paper is as follows: First, we introduce the Binned Spectral

Power (BSP) Loss, a novel approach to address the spectral bias of arbitrary neural forecasting

models. By focusing on preserving the distribution of energy across different spatial scales instead

of relying solely on pointwise comparisons, our method enhances the stability and quality of long
term predictions. Second, our proposed framework is architecture agnostic, easily deployable, and

requires minimum additional hyperparameter tuning. This ensures that our approach remains broadly

applicable, computationally feasible, and adaptable to a variety of dynamical systems. Third, we show

that the BSP loss can actually mitigate the spectral bias using a synthetic example from Rahaman

2


!!! page 3 "Chakraborty_2025_BSP"

et al. [2019]. Fourth, we further examine the effectiveness of our method through extensive testing

on the forecasting of the following complex and high-dimensional chaotic systems: Kolmogorov

flow [Obukhov, 1983], a 2D benchmark for chaotic systems used for various studies [Kochkov et al.,

2021b], a high Reynolds number flow over NACA0012 airfoil [Towne et al., 2023] and the 3D

homogeneous isotropic turbulence [Mohan et al., 2020]. Our results indicate that the proposed loss

function significantly improves both predictive stability and spectral accuracy, mitigating common

limitations of deep learning models in capturing fine-scale structures over long forecasting horizons.

2

Background

We consider an operator G that maps one timestep of the state x of a dynamical system to the next.

This operator can be viewed as the optimal data-driven process that bypasses the direct solution of the

governing differential equation for each timestep, effectively describing the system’s dynamics. The

evolution of the the state at time t is given as xt = G(xt−1) = G(G(G(. . . G(x0)))) = Gt(x0). The

operator G can be approximated using a neural network model Fϕ(x), parameterized by learnable

variables ϕ. Such an approximation is backed by the universal approximation theorem for operators

[Chen and Chen, 1995]. These parameters of Fϕ(x) are optimized by minimizing the discrepancy

from the ground truth data (indexed discretely by j) using a one-step loss function defined as:

L = Ej

h

∥Fϕ(xj) −G(xj)∥2i

.

(1)

A commonly employed multi-rollout loss function [Keisler, 2022], LR, utilized in training many

state-of-the-art models, is defined as:

LR = Ej

"t=m

X

t=1

γ(t)

 F t

ϕ(xj) −Gt(xj)

2

#

,

(2)

where m denotes the number of rollouts included during training, and γ(t) is a hyperparameter that

assigns diminishing weights to errors in trajectories further along in time [Kochkov et al., 2023]. It

has an effect similar2 to the discount factor used in reinforcement learning(RL) [Amit et al., 2020].

Furthermore, to enhance computational efficiency and improve stability, the Pushforward Trick,

introduced in Brandstetter et al. [2022], is often used. This approach reduces computational overhead

by detaching the computational graph at intermediate rollouts. However, such methods alone cannot

address neither the phenomenon of spectral bias of neural networks nor stability [Chakraborty et al.,

2024, Schiff et al., 2024].

2.1

Spectral Bias in Deep Learning

Rahaman et al. [2019] showed that a combination of the theoretical properties of gradient descent

optimization, the architecture of neural networks, and the nature of function approximation in

high-dimensional spaces causes the network to learn lower frequencies faster and more effectively.

Mathematically, for N samples in a training batch, Equation 1 can be approximated by L1 as follows,

where subscript 1 signifies one step MSE loss.

L1 = 1

N

N

X

j=0

∥Fϕ(xj) −G(xj)∥2 .

(3)

The gradient of this loss function with respect to parameters ϕ is given by ∇ϕL1

=

2

N

PN

j=0 (Fϕ(xj) −G(xj)) ∇ϕFϕ(xj), which may be used in a gradient descent update step as

ϕk+1 = ϕk −α∇ϕL1, where α is the learning rate. Intuitively, gradient descent naturally favors

changes that yield the most substantial reduction in loss early in training. In the spectral space, this

is reflected in the components that have higher values in the Fourier series representation of Fϕ

[Oommen et al., 2024]. This causes the lower frequencies to be learned first which correspond to

global patterns that tend to dominate the error landscape in the initial phases of training. For more

details, readers are directed to Section 3 in Rahaman et al. [2019] and Section 4.1 in Oommen et al.

[2024].

2Although the discount factor in RL is unrelated directly to the γ(t) used here, there might be interesting

theoretical connections which we leave for future exploration.

3


!!! page 4 "Chakraborty_2025_BSP"

2.2

Energy Spectrum

The energy spectrum E(k) characterizes the distribution of energy among different frequency or

wavenumber components [Kolmogorov, 1941]. In our work the Fourier Transform is always taken

spatially. However, we use the terms frequency and wavenumber interchangeably henceforth. For an

arbitrary field u(x) (can be Fϕ(x) or G(x) from Equation 1) in a periodic domain of length L, the

Fourier transform F is defined as ˆu(k) = F(u(x)) = 1

L

R L

0 u(x)e−ikxdx, where ˆu(k) represents

the spectral coefficients corresponding to wavenumber k.

For higher-dimensional fields u(x, y, t) or u(x, y, z, t), the Fourier transform is extended to multiple

dimensions, and the energy density is computed by summing over all wavevectors of the same

magnitude: E(k) = 1

2

P

|k|=k |ˆu(k)|2, where k = (kx, ky, kz) is the wavevector, and summation

is performed over spherical shells in Fourier space. In computational settings, we often work

with discretized fields defined on a uniform grid. The discrete Fourier transform (DFT) is used

to approximate the energy spectrum: ˆu(k) =

1

N

PN−1

n=0 une−i2πkn/N, where N is the number of

grid points. For handling discrete wavenumbers in computational grids, binning helps to efficiently

average the energy over wavenumber shells, ensuring a smooth representation of the spectrum. The

magnitude of each wavenumber k is given as

k =

q

k2x + k2y + k2z

(4)

The bins can be logarithmically or linearly spaced. In our experiments, we use linearly spaced bins

for computing the energy contributions into wavenumber shells as:

E(k) =

X

k−∆k/2≤|k|<k+∆k/2

1

2|ˆu(k)|2,

(5)

where ∆k is the width of the bin. In several scenarios, a major portion of the energy is stored in the

lower wavenumbers, highlighted by the rapid decay of their energy spectrum. However, in complex

real-world systems, the energy spectrum typically exhibits a slow decay, preserving substantial energy

and valuable information at higher wave numbers. For example, in weather data, the small and

intermediate scale details correspond to anomalies like initial phases of storms [Ritchie and Holland,

1997], especially in a model with coarser grids.

2.3

Regularization in Fourier Space

An intuitive solution to the problem of capturing the fine scales can be to penalize the mismatch of

the Fourier transform of the model outputs from the ground truth [Chattopadhyay et al., 2024, Guan

et al., 2024, Kochkov et al., 2023]. This is typically done by a regularization in the Fourier space

such as

Lf = 1

N

N−1

X

j=0

X

k

wk |F (Fϕ(xj) −G(xj))|2

k .

(6)

where F is the Fourier transform, and wk is a hyperparameter used to weigh or cut-off some modes. It

is evident that Equation 6 will also be heavily biased towards the larger values in the Fourier spectrum

which typically correspond to the lower frequency modes. For example, if wk = 1, the effect of

Equation 6 is same as the loss function in Equation 3. To overcome this, Chattopadhyay et al. [2024]

used a cutoff to empirically ignore some of the lower frequencies. Guan et al. [2024] used a mean

absolute error in the tendency space after Fourier transform to obtain better performance. However,

for higher frequencies with extremely low contributions, it is not judicious to try to match them

exactly in a point wise manner. This is demonstrated by our experiments in later sections. Another

version of this loss function where wk = (1 + |k|2)s is called the Sobolev Loss [Li et al., 2021,

Czarnecki et al., 2017]. It shows promise in PDE applications as the Sobolev norms correspond to

certain physical quantities (e.g. energy, enstrophy). We compare against this loss function in further

sections. However, we note that the weight in the Sobolev loss is fixed to k2 and is not determined by

the distribution of energy in different scales of the training data. In the following section, we come

up a new strategy to solve the mentioned problems without modifying the network architecture or

incurring a heavy cost during training and inference.

3

Methodology

We introduce a novel Binned Spectral Power (BSP) loss function mentioned in Algorithm 1. This

is designed to evaluate discrepancies between predicted and target data fields by comparing their

4


!!! page 5 "Chakraborty_2025_BSP"

Algorithm 1 Binned Spectral Power (BSP) Loss Computation

Require: Predicted data uj, Target data vj ∈RC×H×W ×..., a small positive constant ϵ

Require: Number of wavenumber bins Nk, and method to define bin i (e.g., linear : 0-1, 1-2,..)

Require: Non-negative weights λi for each bin i = 1, . . . , Nk

Ensure: Spectral Loss L(j)

spec

ˆu ←F(uj), ˆv ←F(vj)

# N-D Spatial Fourier Transform

Eu ←1

2|ˆu|2, Ev ←1

2|ˆv|2

# Energy per mode (c, k)

k ←

q

k2x + k2y + . . .

# Wavenumber magnitude

for i = 1 to Nk do

Ebin

u (c, i) ←



1

Ni

P

k∈bini Eu(c, k)



· λi

# Avg. Eu(c, k) in bin and scale by λi

Ebin

v (c, i) ←



1

Ni

P

k∈bini Ev(c, k)



· λi

end for

L(j)

spec ←

1

Nk

PC

c=1

PNk

i=1



1 −Ebin

u (c,i)+ϵ

Ebin

v (c,i)+ϵ

2

# Final loss computation

spatial energy spectra at different scales. We reuse the concept of energy spectrum mentioned in

Section 2.2. First, the predicted and target samples are transformed into the wavenumber domain

using the Fourier transform. The magnitudes of energy components are computed by squaring the

Fourier coefficients. The wavenumber magnitudes are then computed using Equation 4 to group

spatial frequency components into scalar values. The energy components are binned by wavenumber

ranges, averaging the energy within each bin Ebin using Equation 5. Here every bin (k) is defined

as (k −∆k/2) ≤|k| < (k + ∆k/2). The BSP loss is calculated by comparing the binned energy

spectra of the predicted and target samples.

Unlike traditional loss functions like Mean Squared Error (MSE), which operate point-wise in the

physical domain, the BSP loss provides a robust learning of the various scales in the data, as explained

in the following. To ensure the accurate capturing of different scales we aim to get the ratio of the

energy in different bins close to identity. This squared relative error loss is successful to provide

equal weights to energy component at all wavenumber bins. The BSP Loss is defined as:

LBSP(u, v) = 1

Nk

C

X

c=1

Nk

X

i=1



1 −Ebin

u (c, i) + ϵ

Ebin

v (c, i) + ϵ

2

(7)

where Nk is the number of bins, i refers to a specific bin spanning a range of wavenumbers, and C is

the number of features (channels) in input u and target v. ϵ is used to eliminate the effect of extremely

small values in Ebin. The hyper-parameter λi (see Algorithm 1) is used to variably weight different

bins based on the requirements of the application. In most cases, this can be set to unity – however

special treatment may be needed for specific examples (see Experiment section). For computational

purposes, we empirically suggest to use predicted values and true values as u and v respectively in

LBSP. The algorithm can be written in a differentiable programming language to efficiently compute

the gradients required to minimize the BSP loss. A differentiable histogram can also be used to

efficiently perform the binning using latest libraries like Jax [Bradbury et al., 2018].

The BSP loss can be combined with the multi-step rollout loss given in Equation 2 for short term

accuracy, long term stability and spectral bias mitigation.

L∗

R = Ej

"t=m

X

t=1

γ(t)

 F t

ϕ(xj) −Gt(xj)

2 + µL(j,t)

BSP

#

(8)

where

L(j,t)

BSP = LBSP(F t

ϕ(xj), Gt(xj))

(9)

is the BSP loss at tth autoregressive rollout step of the model and µ is a hyper-parameter that is used

to weigh the two loss terms differently. The gradient of the BSP loss is

∇ϕLBSP = −2

N

N

X

j=1

1

Nk

Nk

X

i=1

C

X

c=1



1 −Ebin

F (c, i) + ϵ

Ebin

G (c, i) + ϵ

 ∇ϕEbin

F (c, i)

Ebin

G (c, i) + ϵ

(10)

5


!!! page 6 "Chakraborty_2025_BSP"

It can be shown, following a similar treatment as for the MSE Loss (also refer Section 4.1 from

Oommen et al. [2024]), that the ratio term present in the gradient of the BSP loss leads to equal

importance to all ranges of the energy spectrum. However, combining the BSP loss with the mean

square error loss gives slightly higher importance to the lower wavenumbers, which is desirable as

they contain the maximum energy. The weight µ can be adjusted to compensate for this when needed.

A detailed mathematical reasoning on the training dynamics using BSP loss and its comparison with

MSE loss is shown in Appendix B. The BSP loss mentioned henceforth is the combined MSE + BSP

loss mentioned in Equation 8.

3.1

Complexity

The BSP loss introduces minimal computational overhead compared to baseline objectives. The

additional cost scales linearly with batch size (nb) and quasi-linearly with the state dimension (d). It

is easily estimated by considering the cost of the FFT step and assuming a small number of frequency

bins (Nk ≪d). As detailed in Table 1, BSP has lower time and space complexity than MMD [Schiff

et al., 2024], and is comparable to standard MSE and push-forward losses. Here, d is the state

dimension, |ϕ| the number of model parameters, NN the cost of a network forward pass, nb the

batch size, and nt the number of rollout steps. MSE1 and MSEt refer to one-step and multi-step MSE

losses, respectively, and Pfwd denotes the push-forward trick from Brandstetter et al. [2022].

Table 1: Time and space complexity of different objectives.

OBJECTIVE

COST O(·)

MEMORY O(·)

MSE1

nbd + nbNN

nbd + nb|ϕ|

MSEt

ntnbd + ntnbNN

ntnbd + ntnb|ϕ|

PFWD

nbd + nbNN

nbd + nb|ϕ|

MMD

n2

bd + nbNN

n2

bd + nb|ϕ|

BSP

nbd log d + nbNN

nbd + nb|ϕ|

4

Experiments

We test our proposed methodology for several benchmark problems. These experiments aim to test

the capabilities of our proposed loss function function to preserve the small scale structures when

applied to high-dimensional dynamical systems using existing deep learning architectures.

4.1

Mitigating the Spectral Bias

Figure 1: (left) MSE over training iterations for BSP Loss (blue), MSE (orange), and FFT Loss

(green), showing faster convergence of BSP. (right) Frequency domain plot of predictions across

training: BSP (top) recovers high-frequency components of g(k) better than MSE (bottom).

We follow Rahaman et al. [2019] to evaluate the mitigation of spectral bias using BSP loss. A target

function g(x) = P

i Ai sin(2πkix + ϕi) is constructed as a sum of sinusoidal components with

varying frequencies, amplitudes, and phases. A 6-layer ReLU network with 256 units per layer is

trained to approximate g(x) using 200 uniformly spaced samples over [0, 1]. We compare models

trained with standard MSE loss versus BSP loss. Further details are provided in Appendix C.1.

6


!!! page 7 "Chakraborty_2025_BSP"

The impact of BSP Loss on function approximation and frequency learning is evident across the

training iterations. The model trained with BSP Loss reconstructs the true function g(x) with higher

accuracy compared to those trained with MSE Loss, particularly in the earlier training stages (refer

Figure 6 in Appendix). The advantage of BSP Loss is highlighted in Figure 1 (right), where its

Fourier Transform representations capture high-frequency components of the true function g(k) more

effectively than MSE Loss, which struggles to learn these components. Additionally, in Figure 1

(left) we indicate the Mean Squared Error (MSE) throughout training iterations for the MSE loss,

the BSP loss and the FFT regularizer mentioned in [Chattopadhyay et al., 2024]. Although the FFT

loss performs slightly better than just using the MSE loss, BSP clearly outperforms all of them

illustrating its superior convergence properties. Additionally we would like to mention that we can

not use the MMD loss here as it is a simple function approximation task and there is no concept

of underlying distribution or attractor (in other words, we do not have any batches to compute the

MMD). These results collectively demonstrate that BSP Loss mitigates spectral bias and enhances

function approximation by preserving the higher-frequency information in the learning process.

4.2

Two-dimensional turbulence

(a) Vorticity fields across time for different mod
els compared with ground truth (bottom row).

DCNN+BSP preserves spatial structure and physical

consistency even at long times, while other models

suffer from blurring or instability (blank images).

(b) Time-averaged energy spectrum compar
ison for various models.

(c) Correlation with DNS over time for dif
ferent models

Figure 2: Comparison of NODE, MP-NODE, and DCNN models with MSE, MMD, and BSP losses.

(a) shows spatial accuracy and stability over time; (b–c) summarize spectral fidelity and correlation

behavior. BSP matches ground truth energy spectrum best over 900 steps. MMD aligns the best

at short times (t<100) but degrades later. Overall, BSP maintains structure and energy distribution

across long forecast horizons.

Forced two-dimensional turbulence is a standard benchmark for dynamical system prediction due to

its chaotic behavior [Stachenfeld et al., 2021, Schiff et al., 2024, Frerix et al., 2021]. We evaluate

our proposed loss on 2D homogeneous isotropic turbulence with Kolmogorov forcing, governed

by the incompressible Navier-Stokes equations. Dataset details are in Appendix C.2. All baseline

models are trained using the multi-step rollout loss from Equation 2 and the pushforward-trick. We

use the dilated Convolutional Neural Network (DCNN) architecture [Stachenfeld et al., 2021], with

7


!!! page 8 "Chakraborty_2025_BSP"

hyperparameters listed in Appendix F. For this test case as well as the following example in Section

4.3, we use λi as k2

(bin i) following widely used procedure in literature [Shankar et al., 2023, Oommen

et al., 2024, Li et al., 2021].As benchmarks, we include DCNN with Maximum Mean Discrepancy

(DCNN + MMD) [Schiff et al., 2024], which promotes attractor learning for stability, and Neural

ODE (NODE) and MP-NODE [Chen et al., 2018, Chakraborty et al., 2024], with results taken from

[Chakraborty et al., 2024]. Appendix A details these baselines.

Figure 2a shows that DCNN trained with MSE becomes unstable at longer rollouts, consistent with

prior works. DCNN + MMD improves stability up to t = 100 but becomes unstable after that,

diverging in high-wavenumber energy (Figure 2b) due to failure to capture finer details [Maulik

et al., 2019]. NODE and MP-NODE remain stable but fail to preserve small-scale structures. In

contrast, DCNN + BSP maintains stability and resolves both large- and small-scale features across

the trajectory, preserving the energy spectrum throughout (Figure 2b). Unlike MMD, the BSP loss

does not minimize error in physical-space, leading to no significant improvement in correlation

metrics here(Figure 2c). However, for stochastic systems like turbulence, invariant metrics are more

meaningful. Appendix C.2, Figure 7 compares distributions of velocity, vorticity, turbulence kinetic

energy, and dissipation rate, showing BSP better preserves physical invariants than baselines.

Figure 3: Total variation (TV) distance between the predicted and true spectral component distri
butions across wavenumbers kx and ky for different loss functions. Among all methods, the model

trained with the BSP loss exhibits the lowest TV distance, indicating the closest match to the true

spectral distribution and the most effective mitigation of spectral bias.

We also benchmark against other spectral losses: Sobolev [Li et al., 2021], relative FFT, and relative

Sobolev. The total variation (TV) distance is employed to quantify discrepancies between the spectral

component distributions at different wavenumbers, providing a robust measure of how predicted and

true spectra differ across scales. As shown in Figure 3, BSP outperforms other losses in spectral

fidelity. We note that the Sobolev loss also shows decent performance. We hypothesize that the poor

performance of the relative losses is due to them trying to minimize very small values in the Fourier

domain in a point-to-point manner, which is nontrivial. This justifies our use of binning to capture

the energy at different scales in the BSP loss.

4.3

3D Turbulence

This experiment uses data from a three-dimensional direct numerical simulation (DNS) of incom
pressible, homogeneous, isotropic turbulence [Mohan et al., 2020]. Further details of this dataset

are mentioned in Appendix C.3. We use a UNet based architecture for both MSE and BSP loss

implementation.The hyperparameters of the model is mentioned in the Appendix F. In Figure 4, we

observe here that both the models show minimal spectral bias and improved stability. This is related

to the reduced spectral bias of models with larger parameter space(refer Appendix A.5. in [Rahaman

et al., 2019]). We limit the extent of forecasting in this experiment due to limited training and

validation data. We tested all models with 30 autoregressive rollouts, which represents approximately

one cycle of turbulence for this dataset. Figure 4 shows the model trained with BSP loss captures the

fine scales better visually. It is also evident from Figure 5 that the BSP loss shows a marked accuracy

8


!!! page 9 "Chakraborty_2025_BSP"

Figure 4: Velocity magnitude 3D plot for ground truth(left), UNet prediction(mid), and UNet + BSP

loss prediction(right) after 5 auto-regressive rollouts. Clearly the UNet prediction has some blurring

effect compared to other two.

in the energy spectrum at high wavenumbers, corresponding to dynamically important small-scale

structures in chaotic systems. Moreover, we present more metrics to further explore the performance

of our method in Appendix C.3. With this evidence, we can conclude that the BSP loss helps in

preserving the distribution of energy across different scales and spatial structures.

Figure 5: Comparison of energy spectra E(k) as a function of wavenumber at different time steps

(T = 1, 15, 30) and averaged over time. The plots show results from DNS (blue solid line), UNet

(orange dashed line), and UNet model trained with BSP loss (green dashed line), along with the

theoretical k−5/3 scaling [Kolmogorov, 1941] (red solid line). The inclusion of BSP improves the

spectral accuracy at high wavenumbers compared to the standalone UNet approach.

5

Discussion

Capturing features across a wide range of spatial and temporal scales in complex, real-world dy
namical systems is a significant challenge for data-driven forecasting techniques. While recent

studies have started to address the issue, they often require specialized neural architectures or end

up adding substantial computational costs both during training and forecasting. To address this,

we introduce a novel Binned Spectral Power (BSP) loss function that steps away from point-wise

comparisons in the physical domain and instead measures differences in terms of spatial energy

distributions. By applying a Fourier transform to the input fields and binning the magnitude of the

Fourier coefficients by wavenumbers, we minimize discrepancies between the predicted fields and

target data across multiple scales. The BSP loss offers a more balanced and efficient way to capture

both large and small features without heavily modifying the model or incurring significant extra costs.

9


!!! page 10 "Chakraborty_2025_BSP"

Our experiments demonstrate that we can effectively reduce the spectral bias of neural networks

in function approximation. We also showcase the advantages of BSP loss using challenging test

cases such as turbulent flow forecasting. These results empirically show that the BSP loss function

improves the ability of a neural network model to mitigate spectral bias and capture information at

different scales in the data.

Limitation : We would like to emphasize that it is non-trivial to define the BSP loss in an unstructured

grid. As demonstrated in Appendix D, when applied to a problem with a non-uniform grid using

interpolation, the resulting improvement is minimal. While we implement some potential solutions

there, addressing this challenge in a broader context remains an avenue for future research.

Acknowledgments and Disclosure of Funding

This research used resources of the Argonne Leadership Computing Facility (ALCF), a U.S. Depart
ment of Energy (DOE) Office of Science user facility at Argonne National Laboratory and is based

on research supported by the U.S. DOE Office of Science-Advanced Scientific Computing Research

(ASCR) Program, under Contract No. DE-AC02-06CH11357. RM/DC acknowledge funding support

from the DOE Office of Science ASCR program (DOE-FOA-2493, PM-Dr. Steve Lee), Fusion En
ergy Sciences program (DOE-FOA-2905, PM-Dr. Michael Halfmoon), and computational resources

from the Penn State Institute for Computational and Data Sciences. ATM acknowledge support from

Artimis LDRD project at Los Alamos National Lab.

References

Ron Amit, Ron Meir, and Kamil Ciosek. Discount factor as a regularizer in reinforcement learning.

In International conference on machine learning, pages 269–278. PMLR, 2020.

Shivam Barwey, Varun Shankar, Venkatasubramanian Viswanathan, and Romit Maulik. Multiscale

graph neural network autoencoders for interpretable scientific machine learning. Journal of

Computational Physics, 495:112537, 2023.

Satwik Bhattamishra, Arkil Patel, Varun Kanade, and Phil Blunsom. Simplicity bias in transformers

and their ability to learn sparse boolean functions. arXiv preprint arXiv:2211.12316, 2022.

Kaifeng Bi, Lingxi Xie, Hengheng Zhang, Xin Chen, Xiaotao Gu, and Qi Tian. Pangu-weather:

A 3d high-resolution model for fast and accurate global weather forecast.

arXiv preprint

arXiv:2211.02556, 2022.

Massimo Bonavita. On some limitations of current machine learning weather prediction models.

Geophysical Research Letters, 51(12):e2023GL107377, 2024.

James Bradbury, Roy Frostig, Peter Hawkins, Matthew James Johnson, Chris Leary, Dougal

Maclaurin, George Necula, Adam Paszke, Jake VanderPlas, Skye Wanderman-Milne, and

Qiao Zhang.

JAX: composable transformations of Python+NumPy programs, 2018.

URL

http://github.com/google/jax.

Johannes Brandstetter, Daniel Worrall, and Max Welling. Message passing neural pde solvers. arXiv

preprint arXiv:2202.03376, 2022.

Joshua William Burby, Qi Tang, and R Maulik. Fast neural poincaré maps for toroidal magnetic

fields. Plasma Physics and Controlled Fusion, 63(2):024001, 2020.

Zhicheng Cai, Hao Zhu, Qiu Shen, Xinran Wang, and Xun Cao. Batch normalization alleviates the

spectral bias in coordinate networks. In Proceedings of the IEEE/CVF Conference on Computer

Vision and Pattern Recognition, pages 25160–25171, 2024.

Abdulkadir Canatar, Blake Bordelon, and Cengiz Pehlevan. Spectral bias and task-model align
ment explain generalization in kernel regression and infinitely wide neural networks. Nature

communications, 12(1):2914, 2021.

Xintao Chai, Wenjun Cao, Jianhui Li, Hang Long, and Xiaodong Sun. Overcoming the spectral

bias problem of physics-informed neural networks in solving the frequency-domain acoustic wave

equation. IEEE Transactions on Geoscience and Remote Sensing, 2024.

10


!!! page 11 "Chakraborty_2025_BSP"

Dibyajyoti Chakraborty, Seung Whan Chung, and Romit Maulik. Divide and conquer: Learning

chaotic dynamical systems with multistep penalty neural ordinary differential equations. arXiv

preprint arXiv:2407.00568, 2024.

Ashesh Chattopadhyay and Pedram Hassanzadeh. Long-term instabilities of deep learning-based

digital twins of the climate system: The cause and a solution. arXiv preprint arXiv:2304.07029,

2023.

Ashesh Chattopadhyay, Michael Gray, Tianning Wu, Anna B Lowe, and Ruoying He. Oceannet: A

principled neural operator-based digital twin for regional oceans. Scientific Reports, 14(1):21181,

2024.

Ricky TQ Chen, Yulia Rubanova, Jesse Bettencourt, and David K Duvenaud. Neural ordinary

differential equations. Advances in neural information processing systems, 31, 2018.

Shengyu Chen, Peyman Givi, Can Zheng, and Xiaowei Jia. Physics-enhanced neural operator for

simulating turbulent transport. arXiv preprint arXiv:2406.04367, 2024.

Tianping Chen and Hong Chen. Universal approximation to nonlinear operators by neural networks

with arbitrary activation functions and its application to dynamical systems. IEEE transactions on

neural networks, 6(4):911–917, 1995.

Yuanqi Chen, Ge Li, Cece Jin, Shan Liu, and Thomas Li. Ssd-gan: measuring the realness in the

spatial and spectral domains. In Proceedings of the AAAI Conference on Artificial Intelligence,

volume 35, pages 1105–1112, 2021.

Michael Chertkov, Alain Pumir, and Boris I Shraiman. Lagrangian tetrad dynamics and the phe
nomenology of turbulence. Physics of fluids, 11(8):2394–2410, 1999.

Seung Whan Chung and Jonathan B Freund. An optimization method for chaotic turbulent flow.

Journal of Computational Physics, 457:111077, 2022.

George Cybenko. Approximation by superpositions of a sigmoidal function. Mathematics of control,

signals and systems, 2(4):303–314, 1989.

Wojciech M Czarnecki, Simon Osindero, Max Jaderberg, Grzegorz Swirszcz, and Razvan Pascanu.

Sobolev training for neural networks. Advances in neural information processing systems, 30,

2017.

Don Daniel, Daniel Livescu, and Jaiyoung Ryu. Reaction analogy based forcing for incompressible

scalar turbulence. Physical Review Fluids, 3(9):094602, 2018.

Thomas Frerix, Dmitrii Kochkov, Jamie Smith, Daniel Cremers, Michael Brenner, and Stephan

Hoyer. Variational data assimilation with a learned inverse observation operator. In International

Conference on Machine Learning, pages 3449–3458. PMLR, 2021.

Sicheng Gao, Xuhui Liu, Bohan Zeng, Sheng Xu, Yanjing Li, Xiaoyan Luo, Jianzhuang Liu,

Xiantong Zhen, and Baochang Zhang. Implicit diffusion models for continuous super-resolution.

In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pages

10021–10030, 2023.

Haiwen Guan, Troy Arcomano, Ashesh Chattopadhyay, and Romit Maulik. Lucie: A lightweight

uncoupled climate emulator with long-term stability and physical consistency for o (1000)-member

ensembles. arXiv preprint arXiv:2405.16297, 2024.

Cale Harnish, Luke Dalessandro, Karel Matous, and Daniel Livescu. A multiresolution adaptive

wavelet method for nonlinear partial differential equations. International Journal for Multiscale

Computational Engineering, 19(2), 2021.

Arthur Jacot, Franck Gabriel, and Clément Hongler. Neural tangent kernel: Convergence and

generalization in neural networks. Advances in neural information processing systems, 31, 2018.

Ruoxi Jiang, Peter Y Lu, Elena Orlova, and Rebecca Willett. Training neural operators to preserve

invariant measures of chaotic attractors. Advances in Neural Information Processing Systems, 36:

27645–27669, 2023.

11


!!! page 12 "Chakraborty_2025_BSP"

George Em Karniadakis, Ioannis G Kevrekidis, Lu Lu, Paris Perdikaris, Sifan Wang, and Liu Yang.

Physics-informed machine learning. Nature Reviews Physics, 3(6):422–440, 2021.

Ryan Keisler.

Forecasting global weather with graph neural networks.

arXiv preprint

arXiv:2202.07575, 2022.

Siavash Khodakarami, Vivek Oommen, Aniruddha Bora, and George Em Karniadakis. Mitigating

spectral bias in neural operators via high-frequency scaling for physical systems. arXiv preprint

arXiv:2503.13695, 2025.

Dmitrii Kochkov, Jamie A. Smith, Ayya Alieva, Qing Wang, Michael P. Brenner, and Stephan

Hoyer. Machine learning–accelerated computational fluid dynamics. Proceedings of the National

Academy of Sciences, 118(21), 2021a. ISSN 0027-8424. doi: 10.1073/pnas.2101784118. URL

https://www.pnas.org/content/118/21/e2101784118.

Dmitrii Kochkov, Jamie A Smith, Ayya Alieva, Qing Wang, Michael P Brenner, and Stephan Hoyer.

Machine learning–accelerated computational fluid dynamics. Proceedings of the National Academy

of Sciences, 118(21):e2101784118, 2021b.

Dmitrii Kochkov, Janni Yuval, Ian Langmore, Peter Norgaard, Jamie A Smith, Griffin Mooers, James

Lottes, Stephan Rasp, Peter D Düben, Milan Klöwer, et al. Neural general circulation models.

CoRR, 2023.

Andrey Nikolaevich Kolmogorov. The local structure of turbulence in incompressible viscous fluid

for very large reynolds. Numbers. In Dokl. Akad. Nauk SSSR, 30:301, 1941.

Ling-Wei Kong, Yang Weng, Bryan Glaz, Mulugeta Haile, and Ying-Cheng Lai. Digital twins of

nonlinear dynamical systems. arXiv preprint arXiv:2210.06144, 2022.

Ching-Yao Lai, Pedram Hassanzadeh, Aditi Sheshadri, Maike Sonnewald, Raffaele Ferrari, and

Venkatramani Balaji. Machine learning for climate physics and simulations. Annual Review of

Condensed Matter Physics, 16, 2024.

Remi Lam, Alvaro Sanchez-Gonzalez, Matthew Willson, Peter Wirnsberger, Meire Fortunato, Alexan
der Pritzel, Suman Ravuri, Timo Ewalds, Ferran Alet, Zach Eaton-Rosen, et al. Graphcast: Learning

skillful medium-range global weather forecasting. arXiv preprint arXiv:2212.12794, 2022.

H Li, L Wang, YL Fu, ZX Wang, TB Wang, and JQ Li. Surrogate model of turbulent transport in

fusion plasmas using machine learning. Nuclear Fusion, 65(1):016015, 2024.

Zongyi Li, Nikola Kovachki, Kamyar Azizzadenesheli, Burigede Liu, Kaushik Bhattacharya, Andrew

Stuart, and Anima Anandkumar. Markov neural operators for learning chaotic systems. arXiv

preprint arXiv:2106.06898, pages 2–3, 2021.

Zongyi Li, Daniel Zhengyu Huang, Burigede Liu, and Anima Anandkumar. Fourier neural operator

with learned deformations for pdes on general geometries. Journal of Machine Learning Research,

24(388):1–26, 2023.

Xinmiao Lin, Yikang Li, Jenhao Hsiao, Chiuman Ho, and Yu Kong. Catch missing details: Image

reconstruction with frequency augmented variational autoencoder. In Proceedings of the IEEE/CVF

Conference on Computer Vision and Pattern Recognition, pages 1736–1745, 2023.

Alec J Linot and Michael D Graham. Data-driven reduced-order modeling of spatiotemporal chaos

with neural ordinary differential equations. Chaos: An Interdisciplinary Journal of Nonlinear

Science, 32(7), 2022.

Alec J Linot, Joshua W Burby, Qi Tang, Prasanna Balaprakash, Michael D Graham, and Romit

Maulik. Stabilized neural ordinary differential equations for long-time forecasting of dynamical

systems. Journal of Computational Physics, 474:111838, 2023.

Phillip Lippe, Bas Veeling, Paris Perdikaris, Richard Turner, and Johannes Brandstetter. Pde
refiner: Achieving accurate long rollouts with neural pde solvers. Advances in Neural Information

Processing Systems, 36:67398–67433, 2023a.

12


!!! page 13 "Chakraborty_2025_BSP"

Phillip Lippe, Bastiaan S Veeling, Paris Perdikaris, Richard E Turner, and Johannes Brandstetter.

Modeling accurate long rollouts with temporal neural pde solvers. In ICML Workshop on New

Frontiers in Learning, Control, and Dynamical Systems, 2023b.

Hao Liu, Xinghua Jiang, Xin Li, Antai Guo, Yiqing Hu, Deqiang Jiang, and Bo Ren. The devil

is in the frequency: Geminated gestalt autoencoder for self-supervised visual pre-training. In

Proceedings of the AAAI Conference on Artificial Intelligence, volume 37, pages 1649–1656, 2023.

Xinliang Liu, Bo Xu, Shuhao Cao, and Lei Zhang. Mitigating spectral bias for the multiscale operator

learning. Journal of Computational Physics, 506:112944, 2024.

Ziqi Liu, Wei Cai, and Zhi-Qin John Xu. Multi-scale deep neural network (mscalednn) for solving

poisson-boltzmann equation in complex domains. arXiv preprint arXiv:2007.11207, 2020.

Feng Luo, Jinxi Xiang, Jun Zhang, Xiao Han, and Wei Yang. Image super-resolution via latent

diffusion: A sampling-space mixture of experts and frequency-augmented decoder approach. arXiv

preprint arXiv:2310.12004, 2023.

Ankur Mahesh, William Collins, Boris Bonev, Noah Brenowitz, Yair Cohen, Joshua Elms, Peter

Harrington, Karthik Kashinath, Thorsten Kurth, Joshua North, et al. Huge ensembles part i:

Design of ensemble weather forecasts using spherical fourier neural operators. arXiv preprint

arXiv:2408.03100, 2024.

Romit Maulik, Omer San, Adil Rasheed, and Prakash Vedula. Subgrid modelling for two-dimensional

turbulence using neural networks. Journal of Fluid Mechanics, 858:122–144, 2019.

Warren S McCulloch and Walter Pitts. A logical calculus of the ideas immanent in nervous activity.

The bulletin of mathematical biophysics, 5:115–133, 1943.

Viraj Mehta, Ian Char, Willie Neiswanger, Youngseog Chung, Andrew Nelson, Mark Boyer, Egemen

Kolemen, and Jeff Schneider. Neural dynamical systems: Balancing structure and flexibility

in physical prediction. In 2021 60th IEEE Conference on Decision and Control (CDC), pages

3735–3742. IEEE, 2021.

Arvind T Mohan, Dima Tretiak, Misha Chertkov, and Daniel Livescu. Spatio-temporal deep learning

models of 3d turbulence with physics informed diagnostics. Journal of Turbulence, 21(9-10):

484–524, 2020.

Tung Nguyen, Rohan Shah, Hritik Bansal, Troy Arcomano, Romit Maulik, Veerabhadra Kotamarthi,

Ian Foster, Sandeep Madireddy, and Aditya Grover. Scaling transformer neural networks for

skillful and reliable medium-range weather forecasting. arXiv preprint arXiv:2312.03876, 2023.

AM Obukhov. Kolmogorov flow and laboratory simulation of it. Russ. Math. Surv, 38(4):113–126,

1983.

Leonardo Olivetti and Gabriele Messori. Do data-driven models beat numerical models in forecasting

weather extremes? a comparison of ifs hres, pangu-weather, and graphcast. Geoscientific Model

Development, 17(21):7915–7962, 2024.

Vivek Oommen, Aniruddha Bora, Zhen Zhang, and George Em Karniadakis. Integrating neural

operators with diffusion models improves spectral representation in turbulence modeling. arXiv

preprint arXiv:2409.08477, 2024.

Olivier C Pasche, Jonathan Wider, Zhongwei Zhang, Jakob Zscheischler, and Sebastian Engelke.

Validating deep learning weather forecast models on recent high-impact extreme events. Artificial

Intelligence for the Earth Systems, 4(1):e240033, 2025.

Jaideep Pathak, Shashank Subramanian, Peter Harrington, Sanjeev Raja, Ashesh Chattopadhyay,

Morteza Mardani, Thorsten Kurth, David Hall, Zongyi Li, Kamyar Azizzadenesheli, et al. Fourcast
net: A global data-driven high-resolution weather model using adaptive Fourier neural operators.

arXiv preprint arXiv:2202.11214, 2022.

Nasim Rahaman, Aristide Baratin, Devansh Arpit, Felix Draxler, Min Lin, Fred Hamprecht, Yoshua

Bengio, and Aaron Courville. On the spectral bias of neural networks. In International conference

on machine learning, pages 5301–5310. PMLR, 2019.

13


!!! page 14 "Chakraborty_2025_BSP"

Elizabeth A Ritchie and Greg J Holland. Scale interactions during the formation of typhoon irving.

Monthly weather review, 125(7):1377–1396, 1997.

Olaf Ronneberger, Philipp Fischer, and Thomas Brox. U-net: Convolutional networks for biomedical

image segmentation. In Medical image computing and computer-assisted intervention–MICCAI

2015: 18th international conference, Munich, Germany, October 5-9, 2015, proceedings, part III

18, pages 234–241. Springer, 2015.

Salva Rühling Cachay, Bo Zhao, Hailey Joren, and Rose Yu. Dyffusion: A dynamics-informed

diffusion model for spatiotemporal forecasting. Advances in Neural Information Processing

Systems, 36, 2024.

TJ Santner. The design and analysis of computer experiments, 2003.

Yair Schiff, Zhong Yi Wan, Jeffrey B Parker, Stephan Hoyer, Volodymyr Kuleshov, Fei Sha, and

Leonardo Zepeda-Núñez. Dyslim: Dynamics stable learning by invariant measure for chaotic

systems. arXiv preprint arXiv:2402.04467, 2024.

Katja Schwarz, Yiyi Liao, and Andreas Geiger. On the frequency bias of generative models. Advances

in Neural Information Processing Systems, 34:18126–18136, 2021.

Varun Shankar, Vedant Puri, Ramesh Balakrishnan, Romit Maulik, and Venkatasubramanian

Viswanathan. Differentiable physics-enabled closure modeling for burgers’ turbulence. Ma
chine Learning: Science and Technology, 4(1):015017, 2023.

Kimberly Stachenfeld, Drummond B Fielding, Dmitrii Kochkov, Miles Cranmer, Tobias Pfaff,

Jonathan Godwin, Can Cui, Shirley Ho, Peter Battaglia, and Alvaro Sanchez-Gonzalez. Learned

coarse models for efficient turbulence simulation. arXiv preprint arXiv:2112.15275, 2021.

Yiming Sun, Ian Simpson, Hua-Liang Wei, and Edward Hanna. Probabilistic seasonal forecasts

of north atlantic atmospheric circulation using complex systems modelling and comparison with

dynamical models. Meteorological Applications, 31(1):e2178, 2024.

Yuchi Sun, Vignesh Venugopal, and Adam R Brandt. Short-term solar power forecast with deep

learning: Exploring optimal input and output configuration. Solar Energy, 188:730–741, 2019.

Matthew Tancik, Pratul Srinivasan, Ben Mildenhall, Sara Fridovich-Keil, Nithin Raghavan, Utkarsh

Singhal, Ravi Ramamoorthi, Jonathan Barron, and Ren Ng. Fourier features let networks learn

high frequency functions in low dimensional domains. Advances in neural information processing

systems, 33:7537–7547, 2020.

Aaron Towne, Scott TM Dawson, Guillaume A Brès, Adrián Lozano-Durán, Theresa Saxton-Fox,

Aadhy Parthasarathy, Anya R Jones, Hulya Biler, Chi-An Yeh, Het D Patel, et al. A database for

reduced-complexity modeling of fluid flows. AIAA journal, 61(7):2867–2892, 2023.

Bo Wang, Wenzhong Zhang, and Wei Cai. Multi-scale deep neural network (mscalednn) methods for

oscillatory stokes flows in complex domains. arXiv preprint arXiv:2009.12729, 2020.

Huaizhi Wang, Zhenxing Lei, Xian Zhang, Bin Zhou, and Jianchun Peng. A review of deep learning

for renewable energy forecasting. Energy Conversion and Management, 198:111799, 2019.

Rui Wang, Danielle Maddix, Christos Faloutsos, Yuyang Wang, and Rose Yu. Bridging physics-based

and data-driven modeling for learning dynamical systems. In Learning for dynamics and control,

pages 385–398. PMLR, 2021.

Sifan Wang, Jacob H Seidman, Shyam Sankaran, Hanwen Wang, George J Pappas, and Paris

Perdikaris. Bridging operator learning and conditioned neural fields: A unifying perspective. arXiv

preprint arXiv:2405.13998, 2024a.

Yixuan Wang, Jonathan W Siegel, Ziming Liu, and Thomas Y Hou. On the expressiveness and

spectral bias of kans. arXiv preprint arXiv:2410.01803, 2024b.

14


!!! page 15 "Chakraborty_2025_BSP"

Oliver Watt-Meyer, Gideon Dresdner, Jeremy McGibbon, Spencer K Clark, Brian Henn, James Dun
can, Noah D Brenowitz, Karthik Kashinath, Michael S Pritchard, Boris Bonev, et al. Ace: A fast,

skillful learned global atmospheric model for climate prediction. arXiv preprint arXiv:2310.02074,

2023.

Annan Yu, Dongwei Lyu, Soon Hoe Lim, Michael W Mahoney, and N Benjamin Erichson. Tuning

frequency bias of state space models. arXiv preprint arXiv:2410.02035, 2024.

Enrui Zhang, Adar Kahana, Alena Kopaniˇcáková, Eli Turkel, Rishikesh Ranade, Jay Pathak, and

George Em Karniadakis. Blending neural operators and relaxation methods in pde numerical

solvers. Nature Machine Intelligence, pages 1–11, 2024.

A

Baseline Models and Loss Functions

A.1

Dilated Convolutional Neural Networks

Dilated Convolutional Neural Networks (DCNNs) enhance traditional convolutional layers by in
troducing a dilation rate d into the convolution operation. This allows the receptive field to expand

exponentially without increasing the number of parameters. This architecture is used in several

dynamical systems forecasting models[Schiff et al., 2024, Chai et al., 2024, Stachenfeld et al., 2021].

In our work we use the architecture similar to [Schiff et al., 2024]. It has an encoder, CNN blocks,

and a decoder. The Encoder first transforms the input through two Convolutional layers with circular

padding and GELU activation, ensuring smooth feature extraction. The CNN block then applies a

sequence of dilated convolutions with varying dilation rates [1,2,4,8,4,2,1], allowing the network to

efficiently capture both local and long-range dependencies while preserving resolution. A residual

connection is added to stabilize learning and maintain input information. We employ 4 such CNN

blocks. The Decoder then reconstructs the output using a couple of Convolutional layers with circular

padding. The model operates recursively over multiple rollout steps, where each prediction is fed

back into the network, making it particularly effective for sequence forecasting tasks.

A.2

Maximum Mean Discrepancy (MMD) Loss

Maximum Mean Discrepancy (MMD) used in [Schiff et al., 2024] is a statistical measure that

quantifies the difference between two probability distributions in a reproducing kernel Hilbert space

(RKHS). Given two distributions P and Q over a space X, the squared MMD is defined as:

MMD2(P, Q) = Ex,x′∼P [k(x, x′)] + Ey,y′∼Q[k(y, y′)] −2Ex∼P,y∼Q[k(x, y)],

(11)

where k : X × X →R is a positive-definite kernel. In the context of chaotic systems, MMD loss

is used to match the empirical invariant measure µ with the learned distribution ˆµ. Given observed

samples {xi}N

i=1 and generated samples {ˆxj}M

j=1, the empirical MMD estimate is:

ˆ

MMD

2 =

1

N 2

X

i,j

k(xi, xj) +

1

M 2

X

i,j

k(ˆxi, ˆxj) −

2

NM

X

i,j

k(xi, ˆxj).

(12)

Minimizing this loss ensures that the learned model captures the long-term statistical properties of

the chaotic system.

A.3

Neural Ordinary Differential Equations

Neural Ordinary Differential Equations (NODEs) provide a continuous-time approach to modeling

dynamic systems by parameterizing the derivative of the state variable using a neural network [Chen

et al., 2018]. It is described as follows:

du(t)

dt

= R(u(t), t, Θ),

for

t ∈[t0, T],

(13)

where R(u(t), t, Θ) is a neural network parameterized by Θ. The initial condition is given as:

u(t0) = u0.

(14)

The solution u(t) is obtained by integrating the system over time using numerical solvers such

as Euler’s method or higher-order solvers like Runge-Kutta. In our case it can be the state of the

dynamical system. The parameters Θ are learned by minimizing a loss function (typically MSE from

15


!!! page 16 "Chakraborty_2025_BSP"

ground truth) using backpropagation through the solver or with the adjoint method. Neural ODEs

are particularly useful for modeling time-series data, continuous normalizing flows, and various

physical systems where the dynamics are governed by differential equations [Chen et al., 2018]. Their

continuous nature provides a flexible alternative to traditional discrete-layer neural networks.

A.4

Multi-step Penalty Neural ODE

The Multi-step Penalty Neural ODE (MP-NODE) is formulated by [Chakraborty et al., 2024] as:

du(t)

dt

−R(u(t), t, Θ) = 0,

for

t ∈[tk, tk+1)

u(tk) = u+

k ,

for

k = 0, . . . , n −1.

(15)

The corresponding loss function incorporates a penalty term and is expressed as:

L = LGT + µ

2 LP ,

(16)

where:

LGT =

PN

i=1 |ui −utrue

i

|2

2N

,

LP =

Pn−1

k=1 |u+

k −u−

k |2

n −1

,

(17)

represent the loss with respect to ground truth and the penalty loss enforcing continuity, respectively.

For k = 1, 2, . . . , n, the term u−

k is computed as:

u−

k = uk−1 +

Z t−

k

t+

k−1

R(u(t), t, Θ) dt.

(18)

The penalty strength µ(here) plays a critical role in handling local discontinuities (quantified by

|u+

k −u−

k |). The update strategy for µ follows a heuristic approach, where adjustments are made

based on the observed loss curves [Chung and Freund, 2022]. Chakraborty et al. [2024] show that the

MP-NODE performs better for forecasting of chaotic systems.

B

Training Dynamics via Neural Tangent Kernel Approximation

To understand how the Binned Spectral Power (BSP) loss potentially mitigates spectral bias, we

analyze the training dynamics of Fourier modes under gradient descent. Let Ω⊂Rd be a compact

domain and fθ : Ω→RD be a smooth vector-valued neural network parameterized by θ ∈Rp,

which aims to approximate a target vector-valued function v : Ω→RD. This section uses simplified

definitions and reasonable assumptions following prior works on training dynamics using Neural

Tangent Kernel(NTK) approximation [Jacot et al., 2018, Canatar et al., 2021, Rahaman et al., 2019].

For any wavevector k ∈Zd, the Fourier coefficients of fθ(x) and v(x) are vectors in CD:

ˆfθ(k) =

Z

Ω

fθ(x) e−2πik·x dx,

ˆv(k) =

Z

Ω

v(x) e−2πik·x dx.

(19)

Each component j ∈{1, . . . , D} of these vector coefficients, ˆfθ,j(k) and ˆvj(k), is a complex

number. Since fθ(x) and v(x) are real-valued, their Fourier coefficients satisfy ˆfθ(−k) = ˆfθ(k)∗and

ˆv(−k) = ˆv(k)∗, where z∗denotes the component-wise complex conjugate of vector z.

We consider the continuous-time analogue of gradient descent:

dθ

dn = −∇θL(θ),

(20)

where L(θ) is the training loss. The evolution of the k-th Fourier coefficient vector ˆfθ(k) is then

given by the chain rule, applied component-wise or using Jacobians:

dˆfθ(k)

dn

= (∇θˆfθ(k)) dθ

dn = −(∇θˆfθ(k))∇θL(θ),

(21)

where ∇θˆfθ(k) is the D × p Jacobian matrix whose (j, l)-th entry is ∂ˆ

fθ,j(k)

∂θl

.

The Neural Tangent Kernel (NTK) for vector-valued outputs is a matrix-valued kernel. The (j, m)-th

component of the NTK matrix ˆΘ(k, k′) (of size D × D) is defined as [Canatar et al., 2021]:

ˆΘjm(k, k′) :=

D

∇θ ˆfθ,j(k), ∇θ ˆfθ,m(k′)∗E

=

p

X

l=1

∂ˆfθ,j(k)

∂θl

∂ˆfθ,m(k′)∗

∂θl

.

(22)

16


!!! page 17 "Chakraborty_2025_BSP"

In the infinite-width limit, ˆΘ(k, k′) is assumed constant during training [Jacot et al., 2018] and

approximately diagonal in the Fourier basis [Canatar et al., 2021, Rahaman et al., 2019]:

ˆΘ(k, k′) ≈δk,k′ Θ(k),

(23)

where Θ(k) is a D × D positive semi-definite matrix for each frequency k. "Anomalous" NTK terms

are assumed negligible. A common further simplification is that Θ(k) is itself diagonal or even scalar,

i.e., Θ(k) = Θ(k)ID, where ID is the D × D identity matrix and Θ(k) ≥0.

The general training dynamic for the vector ˆfθ(k), derived from NTK theory for vector outputs, is:

dˆfθ(k)

dn

≈−Θ(k)

∂L

∂ˆfθ(k)∗.

(24)

Here

∂L

∂ˆfθ(k)∗is a D-dimensional column vector whose j-th component is

∂L

∂ˆ

fθ,j(k)∗.

B.1

Training dynamics under MSE Loss

The Mean Squared Error (MSE) loss for vector-valued functions is:

LMSE(θ) = 1

2

Z

Ω

∥fθ(x) −v(x)∥2

RDdx = 1

2

Z

Ω

D

X

j=1

(fθ,j(x) −vj(x))2dx.

(25)

Using Parseval’s theorem (component-wise, assuming |Ω| = 1):

LMSE(θ) = 1

2

X

p

D

X

j=1

ˆfθ,j(p) −ˆvj(p)

2

= 1

2

X

p

∥ˆfθ(p) −ˆv(p)∥2

CD.

(26)

The derivative vector ∂LMSE

∂ˆfθ(k)∗has components

∂LMSE

∂ˆ

fθ,j(k)∗= 1

2( ˆfθ,j(k) −ˆvj(k)). Thus:

∂LMSE

∂ˆfθ(k)∗= 1

2



ˆfθ(k) −ˆv(k)



.

(27)

Substituting into Eq. (24):

dˆfθ(k)

dn

≈−1

2Θ(k)



ˆfθ(k) −ˆv(k)



.

(28)

If Θ(k) = Θ(k)ID, and absorbing the 1/2 factor as before:

dˆfθ(k)

dn

≈−Θ(k)



ˆfθ(k) −ˆv(k)



.

(29)

Each component of ˆfθ(k) evolves towards the corresponding component of ˆv(k), governed by the

scalar rate Θ(k). Here Θ(k) is larger for lower modes which causes the spectral bias [Rahaman et al.,

2019]. However, we note that the term



ˆfθ(k) −ˆv(k)



is also larger intuitively for lower modes.

B.2

Training dynamics under BSP Loss

For vector-valued functions, the spectral energy Eθ(k) at mode k is typically defined as the sum of

energies over all D output dimensions:

Eθ(k) := 1

2∥ˆfθ(k)∥2

CD = 1

2

D

X

j=1

| ˆfθ,j(k)|2 = 1

2ˆfθ(k)†ˆfθ(k).

(30)

Similarly for Ev(k) := 1

2∥ˆv(k)∥2

CD. With this scalar definition of energy per mode k, we define a

continuous analogue of the BSP loss (without the binning for simplicity):

LBSP(θ) =

Z 

1 −Eθ(k′) + ε

Ev(k′) + ε

2

dk′.

(31)

17


!!! page 18 "Chakraborty_2025_BSP"

The derivative ∂LBSP

∂Eθ(k) is as before: ∂LBSP

∂Eθ(k) = −2 Ev(k)−Eθ(k)

(Ev(k)+ε)2 . The derivative of Eθ(k) with respect

to a component ˆfθ,j(k)∗is

∂Eθ(k)

∂ˆ

fθ,j(k)∗= 1

2 ˆfθ,j(k). Thus, the j-th component of ∂LBSP

∂ˆfθ(k)∗is:

∂LBSP

∂ˆ

fθ,j(k)∗=

∂LBSP

∂Eθ(k)

∂Eθ(k)

∂ˆ

fθ,j(k)∗=



−2 Ev(k)−Eθ(k)

(Ev(k)+ε)2

 

1

2 ˆfθ,j(k)



. So, the derivative vector is:

∂LBSP

∂ˆfθ(k)∗= −Ev(k) −Eθ(k)

(Ev(k) + ε)2

· ˆfθ(k).

(32)

Substituting into Eq. (24):

dˆfθ(k)

dn

≈−Θ(k)



−Ev(k) −Eθ(k)

(Ev(k) + ε)2

· ˆfθ(k)



≈Θ(k)Ev(k) −Eθ(k)

(Ev(k) + ε)2 ˆfθ(k).

(33)

If Θ(k) = Θ(k)ID, the dynamics become:

dˆfθ(k)

dn

≈Θ(k)Ev(k) −Eθ(k)

(Ev(k) + ε)2 ˆfθ(k).

(34)

In this case, all components of ˆfθ(k) are scaled by the factor, which depends on the square of the total

energy Ev(k) in mode k. This adaptive reweighting (based on training data) in BSP loss based on

different frequency modes k helps mitigate spectral bias.

C

Additional Information, Results and Experiments

C.1

Mitigating the Spectral Bias

Figure 6: Function approximation across training iterations. Top: BSP Loss; Bottom: MSE Loss.

BSP better captures sharp transitions and high-frequency modes early in training.

We replicate the setup from Rahaman et al. [2019] to construct a target function g : [0, 1] →R as a

weighted sum of sinusoids:

g(x) =

X

i

Ai sin(2πkix + ϕi),

(35)

where κ = (5, 10, . . . , 50) are the frequencies, amplitudes α = (A1, . . . , An) vary smoothly from

0.08 to 1.2, and ϕi are uniformly sampled phases. The amplitudes rise to a peak and fall off, to

highlight spectral bias in the learned function (see Figure 1 (right)).

We train a 6-layer ReLU network with 256 units per layer on 200 uniform samples over [0, 1], for

60,000 iterations. Two variants are compared: one trained with MSE loss and another with BSP loss.

18


!!! page 19 "Chakraborty_2025_BSP"

Since this is a 1D problem, the Fourier transform directly resolves the wavenumber content, so no

binning is required. This leads to the simplified form of BSP loss:

L = ∥fϕ(x) −g(x)∥2 + µ



1 −∥F(fϕ(x))∥+ ϵ

∥F(g(x))∥+ ϵ

2

,

(36)

where µ = 5 controls the strength of spectral alignment and ϵ = 1 ensures numerical stability. We

conduct an ablation study on relevant hyperparameters in Appendix E.

In higher-dimensional problems, Fourier modes are typically grouped by isotropic wavenumber

magnitude (see Equation 4), requiring binning across Cartesian shells. This is not needed here due to

the 1D structure. Figure 6 shows that model trained with BSP Loss reconstructs the target function

g(x) more accurately than models trained with MSE Loss, especially during the initial phases of

training.

C.2

Kolmogorov Flow

Figure 7: Comparison of the probability density functions (PDFs) of various invariant physical

quantities of different models predictions against the true data. The quantities shown are distributions

of: (top left) pixelwise velocity u(x), (top right) pixelwise vorticity, (bottom left) turbulence kinetic

energy, and (bottom right) dissipation rate. The models compared include a baseline deterministic

convolutional neural network (dCNN), dCNN with maximum mean discrepancy (MMD) loss, dCNN

with Binned Spectral Power (BSP) loss, a Neural Ordinary Differential Equation (NODE), and a

Multi-step Penalty NODE (MPNODE). The distribution of quantities for model trained with BSP loss

(dashed blue line) is the closest to the ground truth(solid black line) for all the invariant quantities.

Dataset : The two-dimensional Navier-Stokes equations are given by:

∂u

∂t + ∇· (u ⊗u) = 1

Re∇2u −1

ρ∇p + f,

∇· u = 0,

(37)

where u = (u, v) is the velocity vector, p is the pressure, ρ is the density, Re is the Reynolds number,

and f represents the forcing function, defined as:

19


!!! page 20 "Chakraborty_2025_BSP"

f = A sin(ky)ˆe −ru,

(38)

with parameters A = 1 (amplitude), k = 4 (wavenumber), r = 0.1 (linear drag), and Re = 1000

(Reynolds number) selected for this study as given in [Shankar et al., 2023]. Here, ˆe denotes

the unit vector in the x-direction.

The initial condition is a random divergence-free velocity

field [Kochkov et al., 2021a]. The ground truth datasets are generated using direct numerical

simulations (DNS) [Kochkov et al., 2021b] of the governing equations within a doubly periodic

square domain of size L = 2π, discretized on a uniform 512 × 512 grid and filtered to a coarser

64 × 64 grid. The trajectories are sampled temporally after the flow reaches the chaotic regime, with

snapshots spaced by T = 256∆tDNS, ensuring sufficient distinction between consecutive states.

Details of the dataset construction can be found in the work by [Shankar et al., 2023].

Additional results: Figure 7 presents a detailed comparison of how well different models reproduce

key physical invariants of the underlying dynamics by plotting the probability density functions

(PDFs) of four important quantities: pixel-wise u(x) velocity, vorticity, turbulence kinetic energy

(TKE), and dissipation rate. These metrics are crucial because they characterize both large-scale

flow structures and small-scale turbulent behaviors, providing a comprehensive assessment of the

physical fidelity of the models. The models evaluated include the same baselines as mentioned in

section 4.2. The results show that across all four quantities, the model trained with BSP loss (shown

by a dashed blue line) produces distributions that align most closely with the ground truth data (solid

black line). This indicates that the BSP loss not only improves spectral accuracy but also enables

the model to better capture the complex statistical properties of the underlying dynamical system,

outperforming both baseline loss functions and other models like NODE and MPNODE in preserving

invariant physical characteristics.

C.3

3D Homogeneous Isotropic Turbulence

Figure 8: The figure illustrates the comparison of the intermittency plots for UNet models trained

with MSE loss (orange) and UNet trained with BSP loss (green) across different time steps (T).

Dataset : The computational domain is a cubic box with dimensions of 1283 grid points. Two scalar

fields, each with distinct probability density function (PDF) characteristics, are advected as passive

scalars by the turbulent flow. This dataset is taken from [Mohan et al., 2020]. They refer to this

20


!!! page 21 "Chakraborty_2025_BSP"

dataset as ScalarHIT, following [Daniel et al., 2018]. The DNS is performed with a pseudo-spectral

code, ensuring incompressibility via

∂xivi = 0,

(39)

and solving the Navier–Stokes equations

∂tvi + vj∂xjvi = −1

ρ∂xip + ν∇2vi + f v

i .

(40)

Low-wavenumber forcing (k < 1.5) maintains a statistically steady state. Dealiasing is performed

Figure 9: The figure illustrates the comparison of the QR plots for UNet models trained with MSE

loss (orange) and UNet trained with BSP loss (green) across different time steps (T) and resolutions

(r). The QR plots signify the theree dimensional chaos in turbulence.

through phase-shifting and truncation, achieving a resolved maximum wavenumber of kmax ≈60

with spectral resolution ηkmax ≈1.5. Scalar transport is governed by

∂tϕ + vj∂xjϕ = D∇2ϕ + f ϕ,

(41)

where ϕ is a passive scalar and D is its diffusivity. Both the viscosity ν and diffusivity D are chosen

so that the Schmidt number Sc = ν/D = 1. The integral-scale Reynolds number is expressed in

terms of the Taylor microscale as

Reλ =

r

20

3

TKE

ν

,

(42)

where TKE denotes the turbulent kinetic energy. They use a novel scalar forcing approach, inspired

by chemical reaction kinetics [Daniel et al., 2018] to achieve desired stationary scalar PDFs and

ensure scalar boundedness. Assuming scalar bounds ϕl = −1 and ϕu = +1, the forcing term is

modeled as

f ϕ = sign(ϕ)fc|ϕ|n(1 −|ϕ|)m,

(43)

where fc, m, and n adjust PDF shape and scalar distribution. By appropriate parameter choices,

different scalar PDFs are realized. For the present dataset, one scalar exhibits near-Gaussian behavior

21


!!! page 22 "Chakraborty_2025_BSP"

(kurtosis ≈3) while the other has a lower kurtosis (≈2.2). With this forcing, the velocity and scalar

fields reach a statistically stationary state at Reλ ≈91. Two scalars with distinct PDFs allow for

testing model capabilities to reproduce both Gaussian-like and bounded scalar distributions.

Additional Results : In Fig. 8, we present the intermittency plots. Intermittency refers to the

fluctuations in velocity gradients, leading to deviations from Gaussian statistics. This can be analyzed

using the probability density function (PDF) of the velocity gradient tensor, which often exhibits

heavy tails due to strong localized fluctuations and is a harder quantity to learn correctly [Mohan

et al., 2020]. The tensor, defined as the spatial derivatives of the velocity components, captures

small-scale structures where intermittency effects are most pronounced. We observe near perfect

prediction at high frequencies, represented by the tails of the PDF.

Finally, the most stringent test of this method is presented in the Q-R plane spectra in Fig. 9, which

represents the three-dimensional chaos in turbulence. QR plots are used to analyze the local flow

topology by examining the invariants of the velocity gradient tensor [Chertkov et al., 1999]. The

second invariant, Q, represents the balance between rotational and strain effects, while the third

invariant, R, characterizes the nature of vortex stretching and flow structures. The spectra at r = 0

indicate high frequencies, while those at r = 8 and r = 32 indicate intermediate frequencies and low

frequencies, respectively. Historically, ML methods have struggled to capture the r = 0 spectra and

instead predict Gaussian-like noise [Mohan et al., 2020], but we show that the BSP loss accurately

captures these dynamics without compromising dynamics at r = 8, 32. These plots show that

even after conserving the smaller structures in the flow, the predictions do not deviate from key

characteristics of turbulence.

D

Turbulent flow over an airfoil

In this section, we examine the turbulent wake flow downstream of a NACA0012 airfoil operating

at a Reynolds number of 23,000, a free-stream Mach number of 0.3, and an angle of attack of

6◦. We utilize a large eddy simulation (LES) dataset provided by [Towne et al., 2023], available

through the publicly accessible Deep Blue Data repository from the University of Michigan. The flow

features have coherent structures associated with Kelvin-Helmholtz instability over the separation

bubble and Von-Kármán vortex shedding in the wake, while exhibiting features at multiple scales

characteristic of turbulent flows. This makes it an ideal test case for several experiments including

validating computational fluid dynamics (CFD) models, analyzing flow dynamics, and exploring

reduced-order modeling approaches. For more details on the dataset refer Section VII in [Towne

et al., 2023]. We follow the same data pre-processing strategy as given in [Oommen et al., 2024]. The

field is interpolated to convert it to a rectangular domain (200x400 pixels). We implement a UNet

architecture [Ronneberger et al., 2015] for the base model and improve it by using our BSP loss. The

hyperparameters of the model are mentioned in Appendix F.

Contrary to the previous case, here we observed that the energy spectrum of the UNet model prediction

is very close to the ground truth even without the BSP loss. Therefore, we use the square root of

the Fourier amplitudes in the energy spectrum to highlight the difference following [Oommen et al.,

2024]. Although it is difficult to compare the results visually from Figure D, we observe that the BSP

loss enhances the model’s ability to capture smaller scale structures given by the higher wavenumbers

in the energy spectrum (

p

E(k) in this case) in Figure 11(left). The improvement here is marginal as

the model without BSP loss itself does a good job in preserving the energy spectrum of the flow field.

To determine the performance of the BSP loss further, we compare it with a larger(as per number of

parameters) state-of-the-art, Continuous Vision Transformer(CVIT) [Wang et al., 2024a] model. Due

to the stochastic nature of the flow field, we compare the probability density function for the velocity

values at a probe in the flow mentioned by the red dot in Figure 10. In Figure 11(right), we observe

that the UNet (trained with MSE loss) model does not preserve the probability distribution of the

velocity field at the probe. However, the BSP loss improves its performance which is comparable

to the approximately 60 times larger CVIT model. The UNet has a narrower distribution due to the

spectral bias shifting the flow towards its mean after several rollouts. However, UNet with BSP loss

has a wider distribution encompassing a wide range of values. The BSP loss can also be implemented

with the CVIT model for further comparison. Since CVIT is operated point-wise, defining the BSP

loss can be challenging. The vmap function can be used to overcome this and reshape the output to a

2D grid. Moreover, models like geo-FNO [Li et al., 2023] can be used to extend the predictive model

22


!!! page 23 "Chakraborty_2025_BSP"

Figure 10: Comparison of model predictions at different timesteps for UNet (trained with MSE loss)

and UNet + BSP Loss. The red dot is the point where the PDF is computed.

Figure 11: (left)Square root of the energy spectra for ground truth and model predictions. The energy

spectra shown here is the mean of first 10 timestep predictions. (right)Distribution of velocity field at

a location downstream of the airfoil. It shows the comparison of PDFs of ground truth and various

model predictions.

to non-uniform grids and BSP loss can be applied in the uniform latent dimension. We leave these

paradigms for future research.

E

Ablation Study

In this section we perform ablation study for the hyperparamers in the BSP loss function, namely

µ and ϵ. From Table 2, it is observed that for all values of µ that we considered, the BSP loss

consistently shows better performance by an order of magnitude from other baselines.

E.1

Kuramoto-Shivashinsky Equation

The Kuramoto–Sivashinsky (KS) equation is a nonlinear partial differential equation that shows

chaotic dynamics and is used as a benchmark for comparing forecast models [Lippe et al., 2023a, Li

et al., 2021, Jiang et al., 2023]. In one spatial dimension, it is given by:

∂tu + u∂xu + ∂xxu + ∂xxxxu = 0,

(44)

23


!!! page 24 "Chakraborty_2025_BSP"

Table 2: Comparison of mean square error at the end of optimization metrics for different values of µ

for the Synthetic Experiment in Section 4.1 . The table compares models trained with MSE loss, BSP

loss, and FFT loss [Chattopadhyay et al., 2024]. The MSE loss column is just for comparison as it

does not have the hyperparameter µ. The best performing model is highlighted in bold.

µ

MSE

BSP

FFT

0.1

0.206 ± 0.190

0.302 ± 0.213

1

0.026 ± 0.011

0.081 ± 0.027

5

0.202±0.057

0.018 ± 0.007

0.226 ± 0.045

7.5

0.048 ± 0.033

0.260 ± 0.024

10

0.081 ± 0.045

0.381 ± 0.012

where u(x, t) represents the evolving field, typically taken to be periodic in space. The term u∂xu

introduces nonlinearity, ∂xxu accounts for linear instability, and the hyperviscous term ∂xxxxu

provides stabilizing dissipation. Despite its simple form, the KS equation exhibits spatiotemporal

chaos and is often used as a benchmark for studying nonlinear dynamics, chaos, and reduced-order

modeling in dynamical systems. The training dataset is generated from a single long-term simulation

of the Kuramoto-Sivashinsky equation, spanning t = 0 to t = 105, with samples recorded every 0.25

time units. Owing to the ergodic nature of the KS system, this extended trajectory effectively captures

a wide range of dynamical behaviors and can be partitioned into multiple shorter sub-trajectories with

distinct initial conditions. We used this dataset directly from previous studies [Linot and Graham,

2022, Linot et al., 2023, Chakraborty et al., 2024].

We implement a recurrent forecasting model using a two-layer Long Short Term Memory (LSTM)

network. The model processes input sequences of dimension 64 and projects the final hidden state of

the 2 layer LSTM (with 128 hidden units) through a fully connected layer to produce a 64-dimensional

output. The LSTM captures temporal dependencies in the input sequence, enabling the model to learn

effective representations for time series prediction. Forecasting is done in an autoregressive manner.

We choose this model to show the ability of BSP loss to work with different model architectures. We

perform an ablation study by implementing the BSP loss with values of ε ∈{0, 10−6, 10−8, 10−10}

and compare it with the model trained with just the MSE loss. As shown in Fig. 12, models trained

with BSP loss exhibit consistently lower ensemble RMSE over time, with larger ϵ values yielding

improved medium-range forecasting accuracy. Spectral analysis further confirms that BSP loss

trained with any ϵ value aligns spatial structures at different scales more closely with ground truth

(refer Fig. 13b). The tradeoff between better medium-range forecast and better spatial structure

fidelity for high and low ε respectively can be clearly seen from Table 3.

Table 3: Comparison of total RMSE over timesteps (0 to 100) and relative spectrum RMSE for models

trained with MSE loss and BSP loss at varying ε. The lowest error in each column is highlighted in

bold. The relative RMSE is chosen for energy spectrum due to varying sclaes.

Model

Forecast RMSE

E(k) relative RMSE

MSE Loss

0.2112 ± 0.1747

2283.2818 ± 696.5619

BSP Loss (ϵ = 10−6)

0.1313 ± 0.1114

1081.0023 ± 348.6294

BSP Loss (ϵ = 10−8)

0.1385 ± 0.1180

79.1884 ± 26.0279

BSP Loss (ϵ = 10−10)

0.1459 ± 0.1320

1.6356 ± 0.5601

BSP Loss (ϵ = 0)

0.1632 ± 0.1352

0.3638 ± 0.2560

F

Hyperparameters

In this section we declare the model hyperparametrs in Table 4. All model hyperparameters are kept

same for both baselines and the model trained with BSP loss. The NODE and MPNODE models

are used directly from Chakraborty et al. [2024]. The hyperparameters of CVIT model is taken

form [Wang et al., 2024a]. The length of trajectory used in training is started from 1 and gradually

increased to Max Timesteps(t).

24


!!! page 25 "Chakraborty_2025_BSP"

Figure 12: Comparison of predicted trajectories (left) and ensemble mean absolute error (right) for

models trained with different loss functions. Rows correspond to models trained with MSE loss

and BSP loss with varying ε ∈{0, 10−6, 10−8, 10−10}, along with the ground truth (bottom row).

BSP-trained models exhibit reduced forecast error, particularly for larger values of ε.

25


!!! page 26 "Chakraborty_2025_BSP"

(a) Ensemble RMSE variation with timesteps.

(b) Energy spectra comparison for different models

Figure 13: Comparison of MSE and BSP-trained models across two diagnostics: (a) RMSE : BSP
trained models achieve consistently lower RMSE than MSE. Larger values of ε show better RMSE.

(b) Energy spectrum E(k). BSP loss improves spectral fidelity, particularly for smaller values of ε

(e.g., 0, 10−10). Shaded regions denote 1σ ensemble variability.

Table 4: Hyperparameters used for different models and datasets.

Setting

2D Turbulence

Airfoil

3D Turbulence

Airfoil Large

Model Name

DCNN

UNet

UNet

CVIT

Parameters

1.1M

0.6M

90M

37M

Learning Rate

10−3 to 10−5

5 × 10−4 to 10−6

5 × 10−4 to 10−6

10−3 to 10−6

Max Timesteps (t)

4

5

3

1

γ(t)

0.9t−1

0.9t−1

0.9t−1

NA

µ

1

0.1

1

NA

λk

k2

1

k2

NA

Optimizer

Adam

Adam

Adam

Adam

Scheduler

Cosine

ReduceLROnPlateau

Cosine

NA

Batch Size

32

32

8

32

26

