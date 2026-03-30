# arXiv:1507.05535v1  [math.OC]  20 Jul 2015
**Creator**: dvips(k) 5.991 Copyright 2011 Radical Eye Software

---

arXiv:1507.05535v1  [math.OC]  20 Jul 2015

Identiﬁcation of Stochastic Wiener Systems

using Indirect Inference ⋆

Bo Wahlberg ∗James Welsh ∗∗Lennart Ljung ∗∗∗

∗Department of Automatic Control and ACCESS, School of Electrical

Engineering, KTH Royal Institute of Technology, SE-100 44

Stockholm, Sweden. (e-mail: bo.wahlberg@ee.kth.se).

∗∗School of Elect Engineering and Computer Science, The University

of Newcastle, Callaghan NSW 2308, Australia.

∗∗∗Division of Automatic Control, Link¨oping University, SE-581 83

Link¨oping, Sweden.

Abstract: We study identiﬁcation of stochastic Wiener dynamic systems using so-called indirect

inference. The main idea is to ﬁrst ﬁt an auxiliary model to the observed data and then in a

second step, often by simulation, ﬁt a more structured model to the estimated auxiliary model.

This two-step procedure can be used when the direct maximum-likelihood estimate is diﬃcult

or intractable to compute. One such example is the identiﬁcation of stochastic Wiener systems,

i.e., linear dynamic systems with process noise where the output is measured using a non
linear sensor with additive measurement noise. It is in principle possible to evaluate the log
likelihood cost function using numerical integration, but the corresponding optimization problem

can be quite intricate. This motivates studying consistent, but sub-optimal, identiﬁcation

methods for stochastic Wiener systems. We will consider indirect inference using the best linear

approximation as an auxiliary model. We show that the key to obtain a reliable estimate is to use

uncertainty weighting when ﬁtting the stochastic Wiener model to the auxiliary model estimate.

The main technical contribution of this paper is the corresponding asymptotic variance analysis.

A numerical evaluation is presented based on a ﬁrst-order ﬁnite impulse response system with

a cubic non-linearity, for which certain illustrative analytic properties are derived.

Keywords: system identiﬁcation, indirect inference, identiﬁcation of non-linear systems,

Wiener systems, stochastic non-linear system.

1. INTRODUCTION

The idea of using two-stage identiﬁcation methods, e.g.,

indirect inference, is by no means new in system identi
ﬁcation. Typically, a ﬂexible auxiliary model is ﬁtted to

data, and then in a second step this estimated model is

used to ﬁnd a more structured model. A well-known ex
ample of such an approach is the indirect Prediction Error

Minimization (PEM) method, S¨oderstr¨om et al. (1991),

where it is assumed that the model structure of interest

can be embedded in a larger model structure for which

the identiﬁcation problem is more tractable. In a second

step, the structured model is estimated from the larger

model using a weighted non-linear least squares method.

The indirect PEM method will, under certain assumptions,

have the same asymptotic statistical properties as the

Maximum-Likelihood (ML) method, but it can be more

eﬃciently calculated. Indirect PEM is a special case of

indirect inference, which was introduced in econometrics

in Gourieroux et al. (1993). Their main motivation was

identiﬁcation problems for which the ML method is in
⋆This work was partially supported by the Swedish Research Coun
cil and the Linnaeus Center ACCESS at KTH. The research leading

to these results has received funding from The European Research

Council under the European Community’s Seventh Framework pro
gram (FP7 2007-2013) / ERC Grant Agrement N. 267381

tractable. They also proposed the use of Monte Carlo

simulations to generate the cost to be minimized in the

second step.

G(q)

+

f(·)

+

u(t)

v(t)

z(t)

e(t)

y(t)

Fig. 1. Stochastic Wiener System

The concept of indirect inference was introduced to the

system identiﬁcation community by Welsh et al. (2009)

and Larsson et al. (2010). The aim of the current paper

is to provide further insights into the potential use of

indirect inference for the identiﬁcation of scalar discrete

time stochastic Wiener systems, illustrated in Figure 1, of

the form

z(t) = G(q)u(t) + v(t),

y(t) = f(z(t)) + e(t),

(1)

with a stable transfer function G(q) (where q denotes the

shift operator), an input signal sequence {u(t)}, white

stationary process noise {v(t)} with zero mean and vari
ance σ2

v, an output signal sequence {y(t)}, and additive

white stationary measurement noise {e(t)} with zero mean

and variance σ2

e. The input signal u(t) is assumed to


!!! page 2 "Wahlberg_2015_stochastic_Wiener"

be independent of the noises (the open-loop case), and

may be a realization of a stochastic process with known

probability distribution. To simplify the presentation, we

will assume that the noise processes are independent and

normal (gaussian) distributed. The more general case with

coloured process noise can be handled using a predictor

model.

The main challenge is the non-linear function f(·), which

means that we have a non-linear stochastic system where

the process noise {v(t)} propagates through a non-linear

device. This typically corresponds to a non-linear sensor.

1.1 Contribution

The main objective of this paper is to study the indirect

inference method using the best linear approximation as an

auxiliary model and compare this to maximum-likelihood

and prediction error minimization methods for identiﬁca
tion of a stochastic Wiener system. The main challenge

is to handle the non-linear process noise contribution. It

is in principle possible to calculate the likelihood cost, or

some approximation of it, using for example particle ﬁlters

and/or Markov Chain Monte Carlo methods, but even for

simple examples the maximum-likelihood approach leads

to rather involved computations. A problem for prediction

error minimization methods is that the probability density

function of the conditional mean prediction error is quite

complicated and involves convolution integrals. This is the

reason for using more ad hoc identiﬁcation techniques. A

common approach is to use linear and gaussian approxi
mations. The main technical contributions are:

• To connect the use of best linear approximation of

stochastic Wiener systems with the method of indi
rect inference. We present the corresponding variance

uncertainty weighting, which for this case includes the

input signal. We also derive the asymptotic variance

expression for the estimated model parameters.

• Illustration of the results on a ﬁrst-order ﬁnite im
pulse response model, for which it is possible to

ﬁnd analytic expressions. The statistical performance

on this example of indirect inference based on best

linear approximation is comparable to that that of

maximum-likelihood estimation and prediction error

minimization. The computations for the indirect in
ference method are just a fraction of the ones for

calculating the maximum-likelihood estimate. The

example also shows that the cost of using a non
linear sensor is increased uncertainty in the estimated

model.

The statistical theory for identiﬁcation of stochastic

Wiener systems is by no means complete, and the aim of

this paper is to provide insights in some open important

problems.

1.2 System Identiﬁcation

Given measurements of the input and output signals

{u(t), y(t)}, t = 1, . . . , N, the task is to identify a model

of the stochastic Wiener system of the form,

z(t) = G(q, θ)u(t) + v(t),

y(t) = f(z(t)) + e(t)

(2)

where the model is parameterized by the parameter vector

θ ∈Rn. We assume that the true system can be described

by θo. The noise processes {v(t)} and {e(t)} are assumed to

be independent normal distributed (gaussian) zero mean

white noise. The corresponding noise variances σ2

v and

σ2

e are assumed to be known, but could be added to

the parameters to be estimated. This can, however, cause

identiﬁability problems. We will study the case when the

non-linear function f(·) is known. It is possible to extend

our results to the case when the function f(·) also is

estimated, which can result in an identiﬁability problem.

The reason for these simpliﬁcations is to focus on the

stochastic part due to the process noise v(t).

Identiﬁcation of Wiener systems is a well studied topic, see

for example Greblicki (1992); Wigren (1993); Bai (2003);

Zhu (2002); Enqvist and Ljung (2005); Pillonetto (2013);

Giri and Bai (2010) and the references therein. It forms

the basis for the identiﬁcation of more general non-linear

block diagram based models. However, many algorithms

assume no process noise, which leads to a non-linear least

squares problem minimizing the output error, i.e., the dif
ference between the measured and the simulated outputs.

The maximum-likelihood method for stochastic Wiener

systems was introduced in Hagenblad and Ljung (2000)

and analysed in more detail in Hagenblad et al. (2008).

The expectation-maximization algorithm for maximum
likelihood identiﬁcation and the use of the particle ﬁlter

have been studied in Wills et al. (2013); Wills and Ljung

(2010). As recently pointed out in Wahlberg et al. (2014),

the stochastic Wiener system identiﬁcation problem can

be viewed as a non-linear errors-in-variables problem, with

the well-known bias problem due to input noise. This

paper also proposes a prediction error minimization frame
work for identiﬁcation of stochastic Wiener systems. The

idea is to use the conditional mean predictor and notice

that the variance of the prediction errors may be highly

dependent on the input signal u(t). Hence, variance un
certainty weighting is most important in order to obtain

reliable estimates.

1.3 Outline

ML and PEM methods for stochastic Wiener system iden
tiﬁcation are reviewed in Sec. 2. In Sec. 3, we study how to

use the indirect inference approach for the identiﬁcation of

stochastic Wiener models by using the BLA as the auxil
iary model. A ﬁrst order FIR model example is outlined in

Sec. 4, and the corresponding numerical study is presented

in Sec. 5. The paper is concluded in Sec. 6.

2. ML AND PEM

As shown in Hagenblad and Ljung (2000), the negative log
likelihood function, given data and the normal distributed

noise model (2), equals

l(θ) = −

N

X

t=1

log

Z ∞

−∞

e−E(t,θ,z)dz,

where

E(t, θ, z) = [y(t) −f(z)]2

2σ2e

+ [z −G(q, θ)u(t)]2

2σ2v

.

The ML estimate of θ is obtained by minimizing l(θ).

There are at least two challenges with the ML method for


!!! page 3 "Wahlberg_2015_stochastic_Wiener"

stochastic Wiener systems. First, to evaluate the negative

log-likelihood cost at a certain parameter value θ we have

to calculate N integrals. This can be done rather eﬃciently

using numerical integration and parallel computations. A

diﬃculty is the integrand, where typically

e−E(t,θ,x) ≈



1, x small,

0, x otherwise.

The example to be considered in Sec. 4 corresponds to

E(x) ∼x6, which means that the integrand decreases very

rapidly to zero.

The PEM approach avoids the exponential function in
tegration issue by using a weighted least squares cost

function, see Wahlberg et al. (2014). The conditional mean

predictor of y(t) for given u(t) and θ is

ˆy(t, θ) = Ev{f(G(q, θ)u(t) + v(t))}.

(3)

Notice that the prediction error variance depends on the

input signal u(t). The optimally weighted quadratic PEM

cost-function, see Wahlberg et al. (2014), is

VN(θ) = 1

N

N

X

t=1

ǫ2(t, θ)

E{ǫ2(t, ˆθI)}

,

(4)

with prediction error ǫ(t, θ) = y(t) −ˆy(t, θ). The variance

weighting is calculated at a consistent initial estimate

ˆθI, e.g., the PEM estimate without weighting. The use

of weighting is important to obtain reliable estimates

and depends here on the input signal u(t). The PEM

estimate based on (4) is not asymptotically eﬃcient for

non-linear functions, since we use a weighted quadratic

cost-function. However, by using a cost-function based on

the probability density function of ǫ(t, θ), we obtain an

asymptotically eﬃcient PEM estimate, see Ljung (1999).

The computations will then be similar to the ML case,

involving multiple integral calculations with exponential

functions.

3. INDIRECT INFERENCE USING BEST LINEAR

APPROXIMATION

3.1 Best Linear Approximation of Stochastic Wiener

Systems

Let us illustrate the concept of indirect inference applied

to a stochastic Wiener system with a known non-linear

function. A common ﬁrst approach is to ﬁt a linear model

to the observed data. It is well known that if the input

signal is normal (gaussian) distributed, then the Best

Linear Approximation (BLA), see Ljung (2001) or (Giri

and Bai, 2010, Chapter 13), is a scaled version of the linear

dynamics transfer function G(q) of the Wiener system.

It is perhaps less well known that the same result holds

for stochastic Wiener systems with gaussian process noise

v(t). This extension follows more or less from Bussgang’s

theorem, Bussgang (1952): If z(t) is a normal distributed

stationary stochastic process with zero mean and if the

non-linear transformed process y(t) = f(z(t)) has zero

mean, then

E{y(t)z(t −τ)} = b0E{z(t)z(t −τ)},

b0 = E{f ′(z(t))}.

Adding independent gaussian process noise to the input

signal contribution, z(t) = G(q)u(t)+v(t), makes z(t) still

normal distributed and Bussgang’s theorem holds. Now we

are only interested in computing the partial correlations

using the relations

E{y(t)u(t −τ)} = b0E{z(t)u(t −τ)}

= b0E{[G(q)u(t)]u(t −τ)}.

(5)

A recent proof of (5) can be found in Banelli (2012), but

it already follows from Nutall (1958). This result proves

that the BLA of a stochastic Wiener system with a normal

distributed input signal again equals

GBLA(q) = b0G(q)

i.e., a scaled version of the linear transfer function. Notice

that b0 now also depends on the statistics of the process

noise v as well as of the input u. This result can be gen
eralized to separable stochastic processes, Nutall (1958);

Enqvist and Ljung (2005).

The BLA of a stochastic Wiener system for more general

input signal sequences can be obtained by simulations or

by analytic calculations (if the distribution of the input

signal is known).

3.2 An Optimally Weighted Indirect Inference Algorithm

We will now describe how to apply indirect inference to

the stochastic Wiener system identiﬁcation problem using

a two-step procedure based on BLA. From the given data

{u(t), y(t)}, t = 1, . . . , N, form the BLA cost-function

QN(β) = 1

N

N

X

t=1

[y(t) −Glin(q, β)u(t)]2.

(6)

Here we have used the notation Glin(q, β) to stress that

this is a linear transfer function parameterized by β ∈Rm.

It is in general of higher order compared to G(q, θ) in (2),

that is m is typically larger than n, the dimension of θ.

We have used an Output Error PEM cost-function (6),

but it is also possible to use a more general PEM model

structure, as described in Ljung (2001).

Step 1: Identify the BLA within the model structure

Glin(q, β), β ∈Rm, of the system from given data using

the cost-function (6)

ˆβN = arg min

β {QN(β)},

i.e., the BLA estimate equals ˆGBLA(q) = Glin(q, ˆβN).

The next question is to ﬁgure out the functional relation

β(θ), Rm 7→Rn that describes how the auxiliary estimate

ˆβN asymptotically depends on the underlying structured

model of interest, as a function of the model parameter

vector θ. Now assume that QN(β) converges (almost

surely) as the number of data N →∞to Q(β, θo), which

depends on the true system parameter vector θo. Here

Q(β, θ) = E{[y(t) −Glin(q, β)u(t)]2}

= Ev,u{[f(G(q, θ)u(t) + v(t)) −Glin(q, β)u(t)]2}.

The expectation is with respect to both the input signal

and the process noise. It is also be possible to only use

expectation with respect to the process noise for a given

input sequence. Let

β(θ) = arg min

β {Q(β, θ)},

and use the notation

βo = β(θo),

for the corresponding true parameter vector. This leads to:


!!! page 4 "Wahlberg_2015_stochastic_Wiener"

Step 2: (Analytic) Estimate the structured model pa
rameter vector θ by solving

ˆθN = arg min

θ [β(θ) −ˆβN]T W[β(θ) −ˆβN],

(7)

where W is a positive deﬁnite weighting matrix to be

speciﬁed.

For certain examples of non-linear functions and distribu
tions it may not possible to analytically ﬁnd the function

β(θ). One can then resort to Monte Carlo simulations. Let

QN,S(β, θ) =

1

S

S

X

s=1

1

N

N

X

t=1

[f(G(q, θ)u(t) + vs(t)) −Glin(q, β)u(t)]2}.

Here {vs(t)}, t = 1, . . . , N, s = 1. . . . , S, is a generated

noise realization of the process noise v(t) and S is the total

number of realizations used in the Monte Carlo Simulation.

Let

ˆβN,S(θ) = arg min

β {QN,S(β, θ)}.

Step 2: (Simulated) Estimate the structured model

parameter vector θ by solving

ˆθN,S = arg min

θ [ˆβN,S(θ) −ˆβN]T W[ˆβN,S(θ) −ˆβN],

(8)

where W is a positive deﬁnite weighting matrix to be

speciﬁed.

The optimal weighting matrix, W, equals the inverse of the

covariance matrix of the auxiliary estimate ˆβN, compare

Expression (9.11) for the asymptotic covariance matrix in

Ljung (1999). In our setting this translates to

W = [J−1

o IoJ−1

o ]−1,

(9)

Io = lim

N→∞Cov{

√

N ∂QN

∂β (βo, θo)}, Jo = ∂2Q

∂β2 (βo, θo).

In practise, one has to use a consistent estimate of W.

3.3 Performance Analysis

Next, we determine the asymptotic properties of the ﬁnal

estimate ˆθN. This can also be done using Taylor series

expansion arguments as described in Complement C4.4

in S¨oderstr¨om and Stoica (1989). The properties of the

function β(θ), Rm 7→Rn, are very important in order to

obtain a consistent estimate. It should be possible to invert

this function, θ = α(β(θ)), i.e., α(·) is a left inverse of β(·).

Deﬁne the Jacobian matrix

G = ∂β

∂θ (θo) ∈Rm×n,

(10)

and recall that we use the weighting matrix

W = [ lim

N→∞Cov{

√

N[ˆβN −βo]}]−1.

(11)

Variance Expression: The asymptotic covariance matrix of

ˆθN deﬁned by (7) equals

lim

N→∞Cov{

√

N[ˆθN −θo]} = [GT WG]−1,

(12)

where G is deﬁned by (10) and W by (11).

To prove this result, we will make a Taylor series expansion

of the cost-function at the minimizing θ:

Vw(θ) = [β(θ) −ˆβN]T W[β(θ) −ˆβN] ⇒V ′

w(ˆθN) = 0,

which gives [ˆθN −θo] ≈−[V ′′

w (θo)]−1V ′

w(θo). The Hessian

V ′′

w (θo) has to be invertible (positive deﬁnite for unique

local minimum) for this to hold. As shown in Complement

4.4 in S¨oderstr¨om and Stoica (1989)

V ′

w(θo) = 2GT W[ˆβN −βo] + O(1/N)

V ′′

w (θo) = 2GT WG + O(1/

√

N).

Hence

[ˆθN −θo] ≈−[GT WG]−1GT W[ˆβN −βo].

Since limN→∞Cov{

√

N[ˆβN−βo]} = W −1, this proves (12).

When using the Monte Carlo simulation approach in

Step 2, (8), the asymptotic covariance matrix of ˆθN,S

should be ampliﬁed by the factor (1 + 1/S), due to the

extra uncertainty from the simulations, see Heggland and

Frigessi (2004).

3.4 Comments

The suggestion to use the BLA as an auxiliary model is

rather ad hoc, but a very common choice in recent meth
ods for identiﬁcation of non-linear systems, Schoukens

et al. (2005); Pintelon and Schoukens (2012); Schoukens

et al. (2014); Schoukens and Rolain (2012); Sjoberg and

Schoukens (2012). Ljung (2001) contains an overview of

the role of BLA in system identiﬁcation. Another option

would be to use the biased estimate from minimizing

l(β) =

N

X

t=1

[y(t) −f(G(q, β)u(t)]2

and then use Step 2 to remove the bias of this estimate.

A challenge is to ﬁnd even more eﬃcient auxiliary models.

The key property is that β(θ) should have a left inverse

(identiﬁability) and

G = ∂β

∂θ (θo) ∈Rm×n

(13)

should be “large” (sensitive) and at the same time β should

be easy to estimate from the given data.

3.5 Indirect Inference

As mentioned in the introduction the indirect inference

approach was developed in Gourieroux et al. (1993) as

a way to ﬁnd consistent model estimates even when the

ML method is intractable. Our description of the indirect

inference approach applied to BLA in the previous section

is mainly based on Heggland and Frigessi (2004). The

theory of indirect inference is more general, and the key

step is to choose the auxiliary model parameterized by β

and the data-driven cost-function QN(β). A convergence

analysis of the general indirect inference method presented

in Heggland and Frigessi (2004) is based on using the

concept of ﬁnite dimension auxiliary statistics.

If QN(β) is based on a suﬃcient statistics the indirect

inference method is eﬃcient (except for the factor (1 +

1/S)). This is not the case for stochastic Wiener systems,

for which no ﬁnite dimensional suﬃcient statistics exists.

For the BLA approach we are only using a second order

statistics.

4. ILLUSTRATING EXAMPLE

We will use the following simple example to try to further

understand the properties of the stochastic Wiener system

identiﬁcation methods described in the previous sections,


!!! page 5 "Wahlberg_2015_stochastic_Wiener"

z(t) = θu(t) + u(t −1) + v(t)

y(t) = [z(t)]3 + e(t).

(14)

The same example was used in Larsson et al. (2010);

Wahlberg et al. (2014). We will study two diﬀerent input

white noise distributions, a normal (gaussian) and an

uniform distribution, both with variance σ2

u. The noises

are assumed to be white zero mean normal distributed

with variances σ2

e and σ2

v, respectively.

The maximum-likelihood cost-function

l(θ) = −

N

X

t=1

log E¯v{ σv

√

2π e

−

1

2σ2e

[y(t)−(θu(t)+u(t−1)+σv¯v)3]2

}

is calculated using a Gauss Hermite approximation of

order 1000. The reason for this high order is the e−x6 tends

to zero very quickly and the integral is rather diﬃcult to

approximate. We have noticed that increased process noise

variance σ2

v makes it even more challenging.

The conditional mean predictor equals

ˆy(t, θ) = θ3u3(t) + u3(t −1) + 3(θu2(t)u(t −1)

+ θu(t)u2(t −1) + θu(t)σ2

v + u(t −1)σ2

v),

(15)

and is used in the PEM method (4).

In order to evaluate the indirect inference method we

will study the BLA. Assume ﬁrst that the input signal is

normal distributed with zero mean and variance σ2

u. The

BLA of model order one, i.e., based on minimizing

E{(y(t) −β1u(t) + β2u(t −1))2}

is



β1(θ)

β2(θ)



= [3σ2

uθ2 + 3(σ2

u + σ2

v)]



θ

1



,

(16)

for which

β1

β2

= θ,

since the BLA for gaussian input signal is just a scaled

version of G(q, θ). This also gives that β(α) has a left

inverse and we have identiﬁability of θ from β.

The corresponding BLA when the input signal is uniformly

distributed with zero mean variance σ2

u is



β1(θ)

β2(θ)



=







9

5σ2

uθ3 + 3(σ2

u + σ2

v)θ

3σ2

uθ2 + 3(3

5σ2

u + σ2

v)





.

(17)

For the indirect inference method we will use

QN(β) = 1

N

N

X

t=1

(y(t) −β1u(t) + β2u(t −1))2

and hence

∂QN

∂β

= 2

N

N

X

t=1



(y(t) −β1u(t) + β2u(t −1))u(t)

(y(t) −β1u(t) + β2u(t −1))u(t −1)



and we need to calculate the weighting matrix W from (9).

Here Jo = σ2

uI and the tedious work is to calculate Io. It

can, however, be estimated as

ˆIo = 1

N

N

X

t=1

h

[y(t) −ˆβ1u(t) −ˆβ2u(t −1)]2 ×



u2(t)

u(t)u(t −1)

u(t))u(t −1)

u2(t −1)



Comment: The key to get the order one indirect inference

method to work is to use the weighting W = ˆI−1

o . The

paper Larsson et al. (2010) does not use weighting, which

explains their non-intuitive simulation result that it is

better to use a zero order BLA model than a ﬁrst order

one (which should contain more information).

We will ﬁnally study the zero order model case, for which

no weighting is needed. Here

QN(β) = 1

N

N

X

t=1

(y(t) −β1u(t))2

with the BLA given by β1(θ) in (16) and (17). An alter
native cost-function is

QN(β) = 1

N

N

X

t=1

(y(t) −β2u(t −2))2,

with the BLA given by β2(θ) from (16) or (17). A problem

here is that β2(θ) is quadratic in θ and we do not have an

unique solution with respect to θ.

5.

SIMULATION RESULT

We will use the following numerical values for the system

parameters in (14):

θo = 0.5,

σ2

v = 0.2,

σ2

e = 0.1.

We will use the analytic Step 2, (7), for the indirect

inference based on BLA, and will evaluate the following

methods for N = 1000 observations:

Method 1:

ML

Method 2:

PEM with optimal weighting

Method 3:

Zero order indirect inference

Method 4:

First order indirect inference, no weighting

Method 5:

First order indirect inference, with weighting

The following table summarizes the simulation results for

the normal distributed input sequence with zero mean and

variance σ2

u = 1/3 over 1000 noise and input realizations:

Method 1:

mean: 0.5025

std: 0.0303

Method 2:

mean: 0.5014

std: 0.0349

Method 3:

mean: 0.4983

std: 0.0446

Method 4:

mean: 0.4977

std: 0.0554

Method 5:

mean: 0.4982

std: 0.0418

The next table summarizes the simulation results for the

uniform distributed input sequence

with zero mean and

variance σ2

u = 1/3 over 1000 noise and input realizations

Method 1:

mean: 0.4994

std: 0.0325

Method 2:

mean: 0.4984

std: 0.0346

Method 3:

mean: 0.4988

std: 0.0454

Method 4:

mean: 0.4984

std: 0.0458

Method 5:

mean: 0.4987

std: 0.0377

The conclusion from the numerical study is that the ML, as

expected, gives the best performance. However, PEM and

indirect inference with optimal weighting give also good


!!! page 6 "Wahlberg_2015_stochastic_Wiener"

results. The computational times for these methods are

only a fraction of that of ML. The simulation study also

shows that a zero order model can give better results than

using a ﬁrst order model and no weighting, c.f., Larsson

et al. (2010).

It should be noted that the asymptotic variance when

f(x)

= x equals (σ2

v + σ2

e)/(σ2

uN), with a standard

deviation equal to 0.0173 for the example above. Hence,

the non-linear function f(x) = x3 gives a more diﬃcult

estimation problem than the standard case f(x) = x.

6. CONCLUSION

In this paper, we have utilised the indirect inference

method based on the best linear approximation to identify

stochastic Wiener systems. The results show that to obtain

a reliable estimate, it is important to use an optimal

weighting when estimating the structured model from the

auxiliary model. The weighting here is the inverse of the

covariance matrix of the BLA parameter estimate. We

have analyzed the statistical properties of the correspond
ing indirect inference estimate using results from system

identiﬁcation. The methods have been evaluated using a

ﬁrst order FIR system with a cubic non-linearity. The

simulation results demonstrate that the proposed indirect

inference BLA approach performs quite well compared to

the ML and weighted PEM methods. A major advantage

is that the indirect inference algorithms are very compu
tationally fast and direct to implement.

There are many open questions when it comes to identi
ﬁcation of stochastic non-linear dynamic systems. For ex
ample, performance results to guide the choice of sensors.

REFERENCES

Bai, E.W. (2003).

Frequency domain identiﬁcation of

Wiener models. Automatica, 39(9), 1521–1530.

Banelli, P. (2012). Non-linear transformations of gaussians

and gaussian-mixtures with implications on estimation

and information theory. IEEE Trans. on Inf. Theory.

submitted, available on arXiv:1111.5950v3 [cs.IT].

Bussgang, J.

(1952).

Cross-correlation function

of

amplitude-distorted gaussians signals. Technical Report

216, MIT Laboratory of Electronics.

Enqvist, M. and Ljung, L. (2005). Linear approximations

of nonlinear FIR systems for separable input processes.

Automatica, 41(3), 459–473.

Giri, F. and E-W. Bai, (Eds.) (2010). Block-oriented Non
linear System Identiﬁcation. Lecture Notes in Control

and Information Sciences.

Volume 404, ISBN: 978-1
84996-512-5.

Gourieroux, C., Monfort, A., and Renault, E. (1993).

Indirect inference.

Journal of applied econometrics,

8(S1), S85–S118.

Greblicki, W. (1992).

Nonparametric identiﬁcation of

Wiener systems.

IEEE Transactions on Information

Theory, 38(5), 1487–1493.

Hagenblad, A. and Ljung, L. (2000). Maximum likelihood

estimation of Wiener models.

In

Proceedings of the

39th IEEE Conference on Decision and Control, 2000,

volume 3, 2417–2418 vol.3.

Hagenblad, A., Ljung, L., and Wills, A. (2008). Maximum

likelihood identiﬁcation of Wiener models. Automatica,

44(11), 2697–2705.

Heggland, K. and Frigessi, A. (2004). Estimating functions

in indirect inference.

Journal of the Royal Statistical

Society: Series B (Statistical Methodology), 66(2), 447–

462.

Larsson, C., Hjalmarsson, H., and Rojas, C. (2010). Iden
tiﬁcation of nonlinear systems using misspeciﬁed predic
tors. In 49th IEEE Conference on Decision and Control

(CDC), 2010, 7214–7219.

Ljung, L. (2001). Estimating linear time invariant models

of non-linear time-varying systems. European Journal

of Control, 7(2-3), 203–219. Semi-plenary presentation

at the European Control Conference, Sept 2001.

Ljung, L. (1999).

System Identiﬁcation: Theory for the

User. Pearson Education.

Nutall, A. (1958). Theory and application of the separable

class of random processes. Technical report, MIT.

Pillonetto, G. (2013). Consistent identiﬁcation of Wiener

systems: A machine learning viewpoint.

Automatica,

49(9), 2704 – 2712.

Pintelon, R. and Schoukens, J. (2012). System identiﬁca
tion: a frequency domain approach. John Wiley & Sons.

Schoukens, J., Pintelon, R., Dobrowiecki, T., and Rolain,

Y. (2005). Identiﬁcation of linear systems with nonlinear

distortions. Automatica, 41(3), 491–504.

Schoukens, M., Pintelon, R., and Rolain, Y. (2014). Iden
tiﬁcation of Wiener - Hammerstein systems by a non
parametric separation of the best linear approximation.

Automatica, 50(2), 628–634.

Schoukens, M. and Rolain, Y. (2012). Parametric identi
ﬁcation of parallel Wiener systems. IEEE Transactions

on Instrumentation and Measurement, 61(10), 2825–

2832.

Sjoberg, J. and Schoukens, J. (2012). Initializing Wiener

Hammerstein models based on partitioning of the best

linear approximation. Automatica, 48(2), 353 – 359.

S¨oderstr¨om, T. and Stoica, P. (1989). System Identiﬁca
tion. Prentice-Hall International.

S¨oderstr¨om, T., Stoica, P., and Friedlander, B. (1991). An

indirect prediction error method for system indentiﬁca
tion. Automatica, 27(1), 183–188.

Wahlberg, B., Welsh, J.S., and Ljung, L. (2014). Identiﬁca
tion of Wiener systems with process noise is a nonlinear

errors-in-variables problem. In 53th IEEE Conference

on Decision and Control (CDC).

Welsh,

J.,

Aguero,

J.C.,

and

Alamir,

M.

(2009).

Continuous-time system identiﬁcation using indirect in
ference. In SYSID 2009, volume 15, 1169–1174.

Wigren, T. (1993). Recursive prediction error identiﬁca
tion using the nonlinear Wiener model.

Automatica,

29(4), 1011–1025.

Wills, A. and Ljung, L. (2010).

Wiener system iden
tiﬁcation using the maximum likelihood method.

In

Block-oriented nonlinear system identiﬁcation, 89–110.

Springer.

Wills, A., Sch¨on, T.B., Ljung, L., and Ninness, B. (2013).

Identiﬁcation of Hammerstein - Wiener models. Auto
matica, 49(1), 70–81.

Zhu, Y. (2002). Estimation of an N-L-N Hammerstein 
Wiener model. Automatica, 38(9), 1607–1614.

