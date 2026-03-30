# Iacob_2025_Koopman_Schoukens

Learning Koopman Models From Data Under General Noise Conditions∗
Lucian Cristian Iacob† , M´at´e Sz´ecsi‡ , Gerben Izaak Beintema† ,
Maarten Schoukens† , and Roland T´oth† ,‡
Abstract. This paper presents a novel identification approach of Koopman models of nonlinear systems with
inputs under rather general noise conditions. The method uses deep state-space encoders based on
the concept of state reconstructability and an efficient multiple-shooting formulation of the squared
loss of the prediction error to estimate the dynamics and the lifted state from input-output data.
Furthermore, the Koopman model structure includes an innovation noise term that is used to handle
process and measurement noise. It is shown that the proposed approach is statistically consistent
and computationally efficient due to the multiple-shooting formulation where, on subsections of
the data, multi-step prediction errors can be calculated in parallel. The latter allows for efficient
batch optimization of the network parameters and, at the same time, excellent long-term prediction
capabilities of the obtained models. The performance of the approach is illustrated by nonlinear
benchmark examples and an experimental quadcopter setup.
Key words. Koopman methods, nonlinear dynamical systems, data-driven modeling, system identification
MSC codes. 37M99, 47B33, 65P99 93B07, 93B15, 93B30
1. Introduction. Due to the continuously increasing performance expectations for dynam-
ical systems in engineering, nonlinear behavior in many application areas started to become
dominant, requiring novel methods that can stabilize and shape the performance of these
systems with the ease of conventional approaches that have been developed for linear time-
invariant systems. Hence, recent years have seen a strong push to find global linear embeddings
of nonlinear systems to simplify, among others, analysis, prediction and control. One such
embedding technique is based on the Koopman framework, where the concept is to lift the
nonlinear state space to a (possibly) infinite-dimensional space through the so-called observ-
able functions. The dynamics of the original system are preserved and governed by a linear
Koopman operator, enabling the representation of the system dynamics via a linear dynamical
description [6], [31] (for a more in depth-overview of the history of Koopman operator theory
and the state-of-the-art see [33]). In practice, by choosing a dictionary of a finite number of
observables a priori to construct time-shifted data matrices, linear Koopman-based models
∗Submitted to the editors on the 24th of May, 2025. This paper extends Deep Identification of Nonlinear Systems
in Koopman Form, which has appeared in the Proceedings of the 60th IEEE Conference on Decision and Control,
CDC, 2021
Funding: This work was funded by the European Union (ERC, COMPLETE, 101075836). The research was
also supported by the European Union within the framework of the National Laboratory for Autonomous Systems
(RRF-2.3.1- 21-2022-00002) and by the Air Force Office of Scientific Research under award number FA8655-23-1-
7061. Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those
of the European Union or the European Research Council Executive Agency. Neither the European Union nor the
granting authority can be held responsible for them.
† Control System Group, Dept. of Electrical Engineering, Eindhoven Technical University, The Netherlands
(l.c.iacob@tue.nl, g.i.beintema@tue.nl, m.schoukens@tue.nl, r.toth@tue.nl).
‡Systems
and
Control
Laboratory,
HUN-REN
Institute
for
Computer
Science
and
Control,
Hungary
(szecsi.mate@sztaki.hun-ren.hu, toth.roland@sztaki.hun-ren.hu).
1
arXiv:2507.09646v3  [eess.SY]  16 Nov 2025
2
L. C. IACOB, M. SZ´ECSI, G. I. BEINTEMA, M. SCHOUKENS, AND R. T´OTH
have been commonly obtained using simple least squares estimation [30]. One such approach,
called dynamic mode decomposition (DMD) [42], is based on constructing time-shifted data
matrices using directly measured state variables associated with the system. If the dictio-
nary consists of nonlinear functions of the state, this technique is known as extended DMD
(EDMD) [58]. However, among many challenges related to statistical consistency, availability
of state-measurements, etc., the main difficulty with these powerful methods lies in choosing
a finite number of lifting functions such that, in the lifted state-space, a linear time-invariant
(LTI) model exists that can capture well the dynamic behavior of the original nonlinear sys-
tem. While there exist methods for the automatic selection of the observables (see [7], [61]),
they still rely on an a priori choice of a dictionary of functions, which many times are difficult
to select and even characterize the resulting approximation error by them.
To circumvent this, a viable approach has been found in learning the lifting functions from
data by the use of machine learning methods such as Gaussian processes [22], kernel-based
methods [40], [59], or various forms of Artificial Neural Networks (ANNs) [27, 38, 39, 54].
Due to their flexibility in describing multiple model structures, applicability to large datasets,
many successful applications of these methods have been reported in the literature to obtain
accurate and compact Koopman models in practice.
However, a common drawback of learning-based methods together with the (E)DMD ap-
proaches is (i) the assumption of full-state measurement (e.g. [27], [39]), which is rarely the
case in engineering applications. Some works such as [18] and [61] do address partial state
observations, either by only lifting the output [61] or by implementing a DMD version that
uses time-delayed measurements [18]. In a different approach, [38] employs a Kalman filter
to estimate the lifted state. Nevertheless, a systematic framework for addressing partial state
measurements in the context of data-driven Koopman modelling is still lacking at large. Fur-
thermore, despite the powerful capabilities of these approaches that have been demonstrated
in multiple examples, generally (ii) little consideration of measurement or process noise is
taken, which can lead to serious bias of the models when applied in real-world applications.
Only a few papers present examples where measurement noise is even present in the data (e.g.
[16], [52]) and often only the robustness of the methods is analyzed (e.g. [47]). While there
are works that add process noise directly to the lifted representation (e.g. [38]), the way noise
enters the Koopman model is merely an assumption. As such, ensuring statistical guarantees
of consistency of the estimators remains an open question in the literature. A third important
issue is that (iii) the estimation of Koopman models for systems with inputs has only recently
been investigated, either through a nonlinear lifting [3] or by using state- and input-dependent
observables, together with input increments [54]. However, this often leads to models that
have limited applicability, as it is more difficult to analyze dynamical aspects of the system or
to design controllers to regulate the behavior compared to other model classes. Alternatively,
due to their simple structure, multiple works assume a fully LTI Koopman model (e.g. [20],
[29]) or, lately, bilinear (e.g.
[4, 38, 45]).
However, it is still largely unexplored how the
approximation capability of these model structures in a finite dimensional setting compares
to using more complex input structures such as control affine or nonlinear in both state and
input, as given in [10, 12, 46].
To overcome challenges (i)-(iii), we introduce a flexible Koopman model learning method
under control inputs, partial measurements, and with statistical guarantees of consistency
LEARNING KOOPMAN MODELS FROM DATA UNDER GENERAL NOISE CONDITIONS
3
under process and measurement noise. For this purpose, a deep-learning-based state-space
encoder approach is proposed, which is implemented in the deepSI toolbox1 in Python. The
main advantages of the approach together with our contributions2 are as follows:
• Analytic derivation of an exact Koopman model with control inputs and innovation
noise structure that can handle measurement and process noise;
• Deep-ANN based encoder function using the reconstructability concept to estimate
the lifted state using input-output data (allows for both full and partial state mea-
surements);
• Computationally efficient batch-wise (multiple-shooting) optimization
based deep-
learning identification method with consistency guarantees to estimate the proposed
Koopman models;
• Comparative study of Koopman model estimation with input structures of different
complexities (linear, bilinear, input affine, general);
The paper is structured as follows. Section 2 details the general Koopman framework and
we discuss the notions of observability and state reconstructability in the Koopman form. The
proposed Koopman encoder, the addition of input and the innovation-type model structure
are discussed in Section 3 together with the proposed deep-learning-based approach for the
estimation of the models. Section 4 discusses the convergence and consistency properties of
the estimator. In Section 5, the approach is tested on Wiener-Hammerstien and Bouc-Wen
benchmarks used in data-driven modeling and on experimental data obtained from a Crazyflie
2.1 nano-quadcopter, followed by a discussion of the results. The conclusions are presented in
Section 6.
2. Preliminaries. This section introduces the core concept of the Koopman framework and
describes the embedding of nonlinear systems in the solution set of linear representations. We
show that, while the behavior of the system can be represented using a linear form, a nonlinear
constraint still needs to be satisfied on the initial conditions to ensure a one-to-one mapping
between the solution sets. Based on this result, we explore observability and constructability
concepts in the original and lifted forms, for both autonomous and input-driven systems.
2.1. Koopman embedding of nonlinear systems. First, for the sake of simplicity, con-
sider a discrete-time nonlinear autonomous system:
(2.1)
xk+1 = f(xk),
with xk ∈Rnx being the state variable, f : Rnx →Rnx is a bounded nonlinear state transition
map and k ∈Z is the discrete time. The initial condition is denoted by x0 ∈X ⊆Rnx and
we assume that X is forward invariant under f(·), i.e., f(X) ⊆X, see [12]. The Koopman
framework uses observable functions ϕ ∈F to lift the system (2.1) to a higher dimensional
space with linear dynamics. These observables ϕ : X →R are scalar functions (generally
1deepSI toolbox available at https://github.com/MaartenSchoukens/deepSI
2The present paper extends the conference paper [10] in terms of introducing an innovation noise structure
in the Koopman model to handle process and measurement noise, proving the consistency of the estimator,
studying various lifted structures for control inputs and providing extensive analysis and testing of the capa-
bilities of the method on benchmarks and real-world data.
4
L. C. IACOB, M. SZ´ECSI, G. I. BEINTEMA, M. SCHOUKENS, AND R. T´OTH
nonlinear) and are from a Banach function space F.
As described in [31], the Koopman
operator K : F →F associated with (2.1) is defined through:
(2.2)
Kϕ = ϕ ◦f,
∀ϕ ∈F,
where ◦denotes function composition and (2.2) is equal to:
(2.3)
Kϕ(xk) = ϕ(xk+1).
Although the Koopman framework typically requires F to be spanned by an infinite number
of basis functions to fully describe the dynamics of (2.1), for practical use, an nf-dimensional
linear subspace Fnf ⊂F is considered, with Fnf = span

ϕj
	nf
j=1.
The finite-dimensional
approximation of the Koopman operator K can be described using the projection operator
Π : F →Fnf, and is given by:
(2.4)
Knf = ΠK|Fnf : Fnf →Fnf.
In practice, the Koopman matrix representation A ∈Rnf×nf is commonly used [31]:
(2.5)
Knfϕj =
nf
X
i=1
Aj,iϕi.
Note that there exist classes of systems that admit an exact finite dimensional embedding
and Knf captures exactly the effect of K. For example, [11] builds on the well known example
discussed in [5], [13], or [38], and develops an exact embedding algorithm for network intercon-
nections of block-oriented polynomial systems. Also, [21, 57, 60] discuss classes of nonlinear
systems that admit an exact embedding via immersion. Next, we introduce the lifted state
zk = Φ(xk), where Φ(xk) =
h
ϕ1(xk)
· · ·
ϕnf(xk)
i⊤
. The lifted finite dimensional linear
representation of (2.1) is then given by:
(2.6)
zk+1 = Azk.
The main challenge of the Koopman framework is the selection of the observables, including
their number, to obtain a suitable approximation in terms of an appropriate norm (or an
exact embedding) of the nonlinear system [31]. Additionally, it is often not clearly stated in
the literature that a linear system whose dynamics are governed by the Koopman matrix A
is only equivalent in terms of behavior (collections of all solution trajectories) to the original
nonlinear system (2.1) if explicit nonlinear constraints are imposed on the initial condition
of the lifted state, i.e., equivalent trajectories are only part of a manifold in the extended
solution space. We explore this further through a simple example.
2.2. Linear representations subject to nonlinear constraints. To illustrate the concept,
we consider the following polynomial system represented by (2.1), similar to the well-studied
example described in [5]:
(2.7)
"
xk+1,1
xk+1,2
#
=
"
axk,1
bxk,2 −cx2
k,1
#
LEARNING KOOPMAN MODELS FROM DATA UNDER GENERAL NOISE CONDITIONS
5
where a, b, c ∈R are constant parameters and xk,i denotes the ith element of xk. By considering
solutions of (2.7) only on [0, ∞) with initial condition x0 ∈R2, the feasible trajectories are
given by:
(2.8)
B =
n
x : Z+
0 →R2 | s.t. (2.7) is satisfied
o
.
To obtain the Koopman form, the following observables are chosen: ϕ1(xk) = xk,1, ϕ2(xk) =
xk,2 and ϕ3(xk) = x2
k,1, which give the equivalent lifted form:
(2.9)
Φ(xk+1) =


a
0
0
0
b
−c
0
0
a2


|
{z
}
A
Φ(xk).
Based on (2.9), consider the system zk+1 = Azk of dimension nz = 3 and with z0 ∈R3. The
solution set is described as:
(2.10)
BK =
n
z : Z+
0 →R3 | s.t. zk+1 = Azk
o
.
Note that (2.10) represents an unrestricted LTI behavior. It is easy to show that Φ(B) ⊆BK,
as any zk ∈BK with z0 ∈R3 for which z0,3 ̸= z2
0,1 will not correspond to a solution of (2.7),
i.e., Φ−1(zk) = xk /∈B. By introducing the constraint Ψ : R3 →R, Ψ(zk) = z2
k,1 −zk,3, the
solution set (2.10) with constraint Ψ is:
(2.11)
ˆBK =
n
z : Z+
0 →R3 | s.t. zk+1 = Azk, Ψ(z0) = 0
o
.
Then, it is possible to show that Φ(B) = ˆBK holds.
To illustrate this, Fig. 1 shows the
simulated trajectories of system (2.10) with a = 0.99, b = 0.9 and c = 0.9 and the constraint Ψ,
which we call the compliant surface. As can be seen in Fig. 1, only solutions (in green) starting
on the compliant surface remain on the compliant surface and correspond to solutions (in
black) of the original nonlinear system (2.7). This example highlights the need for additional
constraints on the Koopman form, or, as we now call it, the embedding of (2.1), to guarantee
a bijective relationship between the solution sets.
Note that, when x0 is known and the observable set Φ is given, this nonlinear condition
on the lifted states is alternatively defined by z0 = Φ(x0). This approach has been extensively
used in the Koopman literature, in both theoretical and application oriented works, see e.g.
[3, 8, 30, 50], and for a discussion on the connection between the nonlinear and lifted manifolds
for systems of the type (2.7), one can consult [5]. However, in an identification setting where
information on x0 is not available or only partially available (in contrast to explicitly lifting the
state via Φ(x0) as done in [5]), to construct a lifted model with the constrained solution set, one
needs to include the Ψ(z0) = 0 condition. Next, we explore observability and reconstructability
of z in view of this discussion.
6
L. C. IACOB, M. SZ´ECSI, G. I. BEINTEMA, M. SCHOUKENS, AND R. T´OTH
Figure 1: Compliant surface corresponding to Ψ (in blue), compliant trajectories of the lifted
system (in green), non-compliant trajectories (in red) of the lifted system and trajectories of
the original nonlinear system (in black).
2.3. Observability and reconstructability. Consider the system defined by (2.1) with
output
(2.12)
yk = h(xk),
where h : Rnx →Rny is a nonlinear output map. Given x0 ∈Rnx, the output map for the
state x associated with the nonlinear dynamics represented by (2.1) and (2.12) is:
(2.13)
Ox,n(x0) =


h(x0)
h ◦f(x0)
...
h ◦n−1 f(x0)


=


y0
y1
...
yn−1


where h ◦2 f(x0) = h ◦f ◦f(x0) and h ◦n f(x0) = h ◦f ◦n−1 f(x0) for n > 2. Let yn−1
0
=
h
y⊤
0
· · ·
y⊤
n−1
i⊤
. As described in [35], the representation satisfies the so-called observability
rank condition at x0 if, for n = nx, the rank of the Jacobian of Ox,n at x0 is nx. If this condition
is met, the representation is strongly locally observable at X0, where X0 is a neighborhood of
x0, and Ox,n is a diffeomorphism, i.e., it is invertible, on X0 [15]. We denote its inverse as
Λx,n : Rnny →X0 ⊆Rnx, such that
(2.14)
x0 = Λx,n(Ox,n(x0)) = Λx,n(yn−1
0
),
for all x0 ∈X0. Note that just like in the LTI case, if this property is satisfied for n = nx,
then (i) the rank condition can be satisfied for nx ≥n ≥1 and the minimal n for which it
LEARNING KOOPMAN MODELS FROM DATA UNDER GENERAL NOISE CONDITIONS
7
holds is called the lag n∗of the system at x0; (ii) the rank of the Jacobian does not change
for n ≥nx; (iii) hence, the existence of (2.14) is ensured for any n ≥n∗.
Throughout the paper, we call Λx,n the observability map, which can be used to compute
the initial condition x0 from future values of the output y. Conversely, the reconstructability
concept is used to calculate the initial condition from past values of the output. For n ≥1, it
holds that
(2.15)
x0 = ◦n−1f(x−n+1),
where ◦0f(x0) = x0. If, for the given n, Λx,n exists, then, using (2.15), we have:
(2.16)
x0 = ◦n−1f(Λx,n(y0
−n+1)) =: Πx,n(y0
−n+1)
for all x0 ∈X0. The function Πx,n : Rnny →X0 ⊆Rnx is called the reconstructability map.
In the Koopman form, assuming that the output function is in the span of the lifted states
(or simply included in the lifting set), i.e., yk = Czk, with C ∈Rny×nz, we construct the
following map:
(2.17)


y0
y1
...
yn−1
0


=








C
CA
...
CAn−1






z0
Ψ(z0)


:=
"
Olin
z,nz0
Ψ(z0)
#
:= Oz,n(z0).
In an LTI sense, the lifted system representation would be observable if there is an n ≥1 such
that rank(Olin
z,n) = nz. However, as observed in Section 2.2, it is also necessary to consider the
nonlinear constraints Ψ : Rnz →Rnc to ensure compliance of the initial condition z0. Hence,
if there is an n ≥1 such that the Jacobian of Oz,n(z0) has full rank nz, which implies that the
mapping Oz,n is locally invertible on a neighborhood Z0 of z0, then z0 is uniquely determined
from yn−1
0
and the constraint Ψ(z0). Then, there exists a Λz,n : Rnny →Z0 ⊆Rnz, such that
(2.18)
z0 = Λz,n(yn−1
0
),
for all z0 ∈Z0. We call Λz,n the observability map for autonomous Koopman models. To
utilize only past data for determining z0, we can also formulate (2.18) in a reconstructability
form. Let:
(2.19)
z0 = An−1z−n+1.
Using (2.18) in (2.19):
(2.20)
z0 = An−1Λz,n(y0
−n+1) := Πz,n(y0
−n+1)
where Πz,n : Rnny →Rnz is the Koopman reconstructability map for autonomous systems.
Note that the compliance constraint Ψ is part of Λz,n. This gives a different point of view on
reconstructability than in the work [50], where the observability notions are discussed based
8
L. C. IACOB, M. SZ´ECSI, G. I. BEINTEMA, M. SCHOUKENS, AND R. T´OTH
on an explicit definition of the lifting map, i.e., a given selection of the observables Φ. Note
that, for a nonlinear system representation with nx states and an explicit dictionary Φ, the
construction z0 = Φ(x0) = Φ(Πx,n(y0
−n+1)) allows to compute the initial lifted z0 based on x0,
using a much smaller amount of lags (at max n = nx) as, typically, nx ≪nz. As such, the
number of necessary lags n does not depend on the dimensionality of the lifted space, but of
the original nonlinear system, which drastically reduces the computational complexity.
It is important to emphasize that the conditions discussed in this subsection guarantee
local observability and necessary conditions for the local invertibility of (2.13) and (2.17).
However, for stronger, global guarantees, [1] describes, albeit for a continuous time systems,
that if f is Lipschitz continuous and h has a finite amount of nondegenerate critical points,
then n = 2nx + 1 is sufficient to ensure global existence of the reconstructabiltiy map, which
is in line with the results in [53].
3. Identification approach. Building on the previously discussed results, this section de-
tails the proposed Koopman model identification approach for nonlinear systems driven by an
external input and affected by process and measurement noise.
3.1. Data generating system. We consider the following nonlinear system:
xk+1 = fd(xk, uk, ek),
(3.1a)
yk = h(xk) + ek,
(3.1b)
with uk ∈U ⊆Rnu the control input and xk ∈X ⊆Rnx the state. The signal ek is the sample-
path realization of an i.i.d. white noise process of finite variance, taking values in E ⊆Rnx and
being independent from u in the statistical sense. The functions fd : X × U × E →Rnx and
h : X →Rny are the state-transition and output functions, respectively. It is assumed that
the sets U and E are such that X is forward invariant under fd and 0 ∈X. The objective is to
estimate a Koopman model of the deterministic (process) part of (3.1). This is done using an
input-output data sequence DN = {(uk, yk)}N
k=0 collected from the system (3.1). We define
next the model structure that we propose to identify a lifted Koopman form of the system
under the control input u and noise process e.
3.2. Koopman model structure. To analytically derive an equivalent Koopman model
of (3.1), we begin by decomposing fd(xk, uk, ek) into autonomous, input and noise-related
components as follows:
fd(xk, uk, ek) = fd(xk, 0, 0) + fd(xk, uk, ek) −fd(xk, 0, 0)
|
{z
}
˜fd(xk,uk,ek)
(3.2)
= fd(xk, 0, 0) + ˜fd(xk, uk, 0) + ˜fd(xk, uk, ek) −˜fd(xk, uk, 0)
|
{z
}
d(xk,uk,ek)
= f(xk) + g(xk, uk) + d(xk, uk, ek)
where g(xk, 0) = 0 and d(xk, uk, 0) = 0. This decomposition, which always exists, extends
the one discussed in [12] and [50] for the noiseless case. To derive an exact finite dimensional
Koopman representation, we make the following assumptions.
LEARNING KOOPMAN MODELS FROM DATA UNDER GENERAL NOISE CONDITIONS
9
Assumption 1. There exists a finite dimensional dictionary of observables Φ : X →Rnf
with Φ = [ ϕ1 · · · ϕnf ]⊤in an appropriate Banach space F such that Φ ◦f(·) ∈span{Φ},
which implies that
(3.3)
Φ ◦f(·) = AΦ(·) with A ∈Rnf×nf.
Assumption 2. The output map h can be exactly represented by the observables Φ in
Assumption 1, in other words h ∈span{Φ}, which implies that
(3.4)
h(·) = CΦ(·) with C ∈Rny×nf.
While Assumption 2 can be easily satisfied (for example by including h in the dictionary
of observables), Assumption 1 is more challenging due to the finite dimensionality. While
there exist methods for exact finite embedding of polynomial systems [11], [13], methods
for polyflows [17], or results in immersion theory [56], the conditions for the existence of
an exact embedding of more general classes of nonlinear systems are lacking. Hence, it is
currently an open question what are the limitations of Assumption 1, especially in terms of
the findings in [23]. Otherwise, (3.3) only holds in an approximative sense 3. In this work, we
use Assumptions 1 and 2 to derive the exact finite dimensional Koopman form of nonlinear
systems with control input and influenced by process and measurement noise and we use the
resulting form as our model structure to be identified.
For this purpose, we formulate the following theorem.
Theorem 3.1. Under Assumptions 1 and 2, the nonlinear system (3.1) can be written into
the form:
zk+1 = Azk + B(zk, uk)uk + K(zk, uk, ek)ek
(3.5a)
yk = Czk + ek
(3.5b)
which is an exact finite dimensional Koopman form with innovation noise structure and zk =
Φ(xk), with zk ∈Rnz being the lifted state and nz = nf.
Proof. The proof is given in Appendix A.
While (3.5) is an exact embedding if Assumptions 1 and 2 hold, in an identification setting it
may be desirable to trade accuracy with simplicity of the model. We can conceptually write
the Koopman model to be identified as:
zk+1 = Azk + Buk + Kek
(3.6a)
yk = Czk + ek
(3.6b)
where the input function B may have different complexities, i.e., B ∈{B, Pnz
i=1 Bizk,i
+B0, B(zk), B(zk, uk)}, corresponding to a linear, bilinear, input affine or what we call a
3For systems where exact finite dimensional embeddings are not possible, future research may provide a
way to combine the consistency result described in Section 4 with a method that quantifies the approximation
error when Assumption 1 does not hold. For example, it may be possible to characterize or mitigate the n-step
reconstructabiltiy error through a reprojection approach as discussed in [55].
10
L. C. IACOB, M. SZ´ECSI, G. I. BEINTEMA, M. SCHOUKENS, AND R. T´OTH
general model structure. Similar to the B matrix, the innovation noise term can be considered
with various dependencies: K ∈{K, Pnz
i=1 Kizk,i + K0, K(zk), K(zk, uk), K(zk, uk, ek)}.
Choosing a suitable structural form of B and K corresponds to a model structure selection
problem, as in classical system identification.
To use the more complex Koopman models for control (not fully LTI), it is possible to
cast the model into a linear parameter-varying (LPV) form (see [12] for the noiseless case) by
introducing a so called scheduling variable pk that is required to be measurable/observable
from the system. For nonlinear systems described by LPV models, there exists a multitude
of convex and computationally efficient control synthesis methods, where the user can also
shape performance and achieve global guarantees of stability [34]. To cast (3.6) into an LPV
form, we must first note that, generally, the noise ek is not directly measurable, but thanks to
the innovation noise setting of (3.1), ek = yk −Czk holds. Then, we can conceptually write
the LPV form of the Koopman model (3.6) as:
zk+1 = Azk + Bz(pk)uk + Kz(pk)ek
(3.7a)
yk = Czk + ek
(3.7b)
where pk = µ(zk, uk, yk) is a scheduling map and Bz with Kz belong to a predefined function
class such as affine, polynomial or rational, such that Bz ◦µ = B, Kz ◦µ = K [12], [34]. Note
that the dependencies of µ are based on the choice of B and K.
3.3. Identification problem. The objective is to introduce a parametrized version of (3.5)
to learn the underlying dependencies together with a lifting map using ANNs. This means
identifying the lifted state zk, the linear maps A, C, and the nonlinear maps B and K. To this
end, we introduce an identification cost function that we chose to be the squared prediction
error due to its extended use and success in system identification and its close connection
to maximum-likelihood estimators under specific settings [25], [26]. For this, a predictor is
needed and we derive it next.
As a first step, we exploit ek = yk −Czk in the assumed
innovation form (3.1) and substitute it in (3.5a) to obtain:
(3.8)
zk+1 = Azk + B(zk, uk)uk + K(zk, uk, yk −Czk)(yk −Czk)
=

A −˜K(zk, uk, yk)C

zk + B(zk, uk)uk + ˜K(zk, uk, yk)yk
|
{z
}
F(zk,uk,yk)
with ˜K(zk, uk, yk) := K(zk, uk, yk −Czk). Then, iterating (3.5b) forward in time, for n ≥1,
we arrive at
yk = Czk + ek
yk+1 = Czk+1 + ek+1 = CF(zk, uk, yk) + ek+1
...
yk+n = C(◦nF)(zk, uk+n−1
k
, yk+n−1
k
) + ek+n
(3.9)
where uk+n−1
k
= [ u⊤
k · · · u⊤
k+n−1 ]⊤and yk+n−1
k
is similarly defined in the previous subsection.
In a compact form:
(3.10)
yk+n
k
= Γn(zk, uk+n−1
k
, yk+n−1
k
) + ek+n
k
,
LEARNING KOOPMAN MODELS FROM DATA UNDER GENERAL NOISE CONDITIONS
11
with ek+n
k
= [ e⊤
k
· · · e⊤
k+n]⊤.
Based on the i.i.d noise assumption of ek, the conditional
expectation of (3.10) w.r.t. e based on the available input-output data and zk is:
(3.11)
ˆyk+n
k
= Ee
n
yk+n
k
| zk, uk+n−1
k
, yk+n−1
k
o
= Γn(zk, uk+n−1
k
, yk+n−1
k
)
which is the one-step-ahead predictor associated with (3.5) along the time interval [k, k + n]
and with initial condition zk.
This can be computed for the entire data sequence DN as
ˆyN
0 = ΓN(z0, uN−1
0
, yN−1
0
) or, for a particular time-moment, as ˆyk = γk(z0, uk−1
0
, yk−1
0
) with
γk = C(◦kF).
As a next step to identify a Koopman embedding of the data-generating system (3.1) in
the form of (3.5), we introduce a parameterization of (3.5) in terms of
ˆzk+1 = Aθˆzk + Bθ(ˆzk, uk)uk + Kθ(ˆzk, uk, ˆek)ˆek,
(3.12a)
ˆyk = Cθˆzk.
(3.12b)
In (3.12), ˆz is the predicted lifted state, ˆy is the predicted output, and ˆe is the prediction
error. While Aθ and Cθ are matrices with their elements as parameters, the maps Bθ and
Kθ are considered with a given choice of complexity: linear, bilinear, input affine, or general
nonlinear dependency. In the linear case, Bθ and Kθ are also matrices with their elements as
parameters, in the bilinear case, the matrices of the bilinear relations are taken as parameters,
while, in the input affine and general cases, Bθ and Kθ are represented by ANNs with weights
and bias terms collected in θ together with the weights of a linear bypass. The collection of
all parameters associated with Aθ, . . . , Kθ are collected in θ ∈Θ ⊆Rnθ. The parameterized
model structure gives rise to a parametrized predictor ΓN,θ, providing the calculation of ˆyk
and the prediction error ˆek over a data set DN = {(uk, yk)}N
k=0 of the data-generating system.
To accurately estimate (3.5), we minimize the ℓ2 loss of the error between the measured
output yk and predicted output ˆyk:
(3.13)
V pred
DN (θ) =
1
N + 1
N
X
k=0
∥yk −ˆyk∥2
2.
Note that in (3.13), the initial lifted state z0 is unknown and needs to be optimized during the
minimization of (3.13). The minimum of (3.13) will provide a Koopman model with the best
one-step-ahead prediction performance. Later we will investigate how this estimate is related
to the true Koopman embedding of the original nonlinear system, if it exists.
There are two challenges associated with (3.13): (i) estimation of (3.5) in this form does
not provide a direct characterisation of the observable or a way how the lifted state can
be calculated from measurable variables in the original system; (ii) the computational cost
of solving the minimisation problem based on (3.13) is high in case of large data sets and
numerically challenging under ANN prametrisation of Bθ or Kθ, due to vanishing of the
gradients during backward / forward propagation.
3.4. Subspace encoder. To overcome problem (i), in this section, the estimation of the
lifted state zk is considered in terms of an encoder. By exploiting input-output data, we use
12
L. C. IACOB, M. SZ´ECSI, G. I. BEINTEMA, M. SCHOUKENS, AND R. T´OTH
the reconsutructability concept, discussed in the autonomous case, which we now generalize
for (3.5). Starting with observability, the following equality holds based on (3.10):
(3.14)
"
Γn(zk, uk+n−1
k
, yk+n−1
k
) + ek+n
k
Ψ(zk)
#
|
{z
}
Oz,n(zk,uk+n−1
k
,ek+n
k
)
=
"
yk+n
k
0
#
where, as in the autonomous case, we have the set of nonlinear constraints Ψ. For n ≥1, if
∃(z∗, w∗) ∈Rnz × Rnnu×(n+1)ny×(n+1)ny for which the Jacobian ∇(z∗,w∗)Oz,n has full row rank
nz, then there exist open sets Z0 ⊆Rnz, U0 ⊆Rnu, Y0 ⊆Rny, E0 ⊆Rny, corresponding to the
neighborhood of (z∗, w∗) for which Oz,n is partially invertible and (3.5) is locally observable
on (Z0, U0, Y0, E0), see [35]. Note that if the representation is locally observable, then the
above condition is satisfied for any n ≥nz −1 By inverting Oz,n, we get
(3.15)
zk = Λz,n(uk+n−1
k
, yk+n
k
, ek+n
k
)
where Λz,n : Un
0 × Yn+1
0
× En+1
0
→Rnz is the observability map. To determine zk based on
past input-output data, we derive
zk = (◦nF)(zk−n, uk−1
k−n, yk−1
k−n)
(3.16)
= (◦nF)(Λz,n(uk−1
k−n, yk
k−n, ek
k−n), uk−1
k−n, yk−1
k−n)
:= Πz,n(uk−1
k−n, yk
k−n, ek
k−n)
where Πz,n : Un
0 × Yn+1
0
× En+1
0
→Rnz is the recosntructability map. Note that the noise
sequence ek
k−n is not directly available in practice, hence to compute zk based on (3.16), again
we can exploit the i.i.d. white noise property of ek to arrive at:
(3.17)
¯zk = Ee
n
zk | uk−1
k−n, yk
k−n
o
= ¯Πz,n(uk−1
k−n, yk
k−n),
which mapping gives an efficient estimator of zk in the conditional mean sense based on
past data with a given lag n.
In fact, (3.17) functions as an encoder, mapping from the
past data to the lifted state zk, i.e., a subspace of the lifted state space. However, an exact
calculation of the encoder ¯Πz,n for a given ANN parametrization of fθ and hθ is infeasible
in practice, due to the required analytic inversion of Oz,n to get Λz,n and the computation
of the conditional expectation of ¯Πz,n under the unknown probability density function of ek.
Hence, our objective is to learn ¯Πz,n directly from the data by introducing a parametrized
function ¯Πη
z,n with parameters η ∈Υ ⊆Rnη, e.g., using an ANN in the general case, which is
co-estimated with Aθ, Bθ, Cθ and Kθ4.
Note that, similar to the autonomous case discussed in Section 2.3, we can conceptually
show that exploiting the observability and reconstructability properties of the nonlinear system
4We note an alternate method described in [38], where the authors describe the Koopman representation
as a hidden Markov model and use Kalman filtering to estimate the latent (lifted) state based on partial
observations. However, the bilinear form and the way noise affects the lifted model are chosen empirically,
whereas (3.12) represents an analytical form.
LEARNING KOOPMAN MODELS FROM DATA UNDER GENERAL NOISE CONDITIONS
13
(3.1), the potentially needed number of lags n ≥nz −1 is greatly reduced. Given a lifting map
Φ : Rnx →Rnz, the state zk = Φ(xk) can be calculated based on the reconstructed xk using
a number of lags n ≥nx −1, as detailed in [2], for the reconstructabillity map associated to
(3.1). As such, when computing ¯Πη
z,n, the number of lags needed to estimate zk is related to
the dimension of the underlying nonlinear system, rather than that of the lifted system. It
is important to note that, while nx −1 guarantees local invertibility, for global observability
guarantees one would need to increase the number of lags n. For example, works such as [48]
and [49] describe a sufficient condition for reconstruction of xk to be n ≥2nx, for nonlinear
systems with deterministic and stochastic forcing, respectively. Note that, as the last step in
(3.9) is k + n instead of k + n −1, we subtract 1 from the given value in [48] and [49], which is
2nx + 1. While (3.14) is more complex than the maps discussed in [48] and [49], these results
can still serve as a guideline when performing experiments and choosing n. Furthermore, if
nx is known, although Oz,n may be locally invertible for smaller values of n, it is still a safe
choice to start with n ≥nx −1, which provides local guarantees for reconstructability.
3.5. Model estimation via multiple shooting and subspace encoding. To overcome
problem (ii), we truncate the ℓ2 prediction loss (3.13) to a horizon of length T and we di-
vide the data into subsections on which the truncated prediction loss is calculated, giving
a so called multiple shooting form of the optimization problem. This approach reduces the
computational cost and improves numerical stability [41]. Accordingly, the prediction loss is
reformulated as:
V enc
DN (θ, η) =
1
Nsec
N−T+1
X
k=n+1
T−1
X
τ=0
∥yk+τ −ˆyk+τ|k∥2
2
(3.18a)
ˆzk|k = ¯Πη
z,n(uk−1
k−n, yk
k−n)
(3.18b)
ˆzk+τ+1|k = Aθˆzk+τ|k + Bθ(ˆzk+τ|k, uk+τ)uk+τ
(3.18c)
+ Kθ(ˆzk+τ|k, uk+τ, ˆek+τ|k)ˆek+τ|k
ˆyk+τ|k = Cθˆzk+τ|k
(3.18d)
ˆek+τ|k = yk+τ −ˆyk+τ|k
(3.18e)
with Nsec = (N −T −n + 1)T. Here, the notation (|) is introduced to make the distinction
(current time index | start index) of variables associated with a given section of the data. Note
that chopping up the cost function to T-length sections would require the introduction of the
initial condition of ˆzk|k as an optimization variable, which would tremendously increase the
number of optimization variables, potentially losing any computational benefit of the multiple-
shooting-based reformulation. To avoid this, the previously introduced subspace encoder is
used
(3.19)
ˆzk|k := ¯Πη
z,n(uk−1
k−n, yk
k−n),
with η ∈Υ ⊆Rnη, corresponding to a general ANN parameterization of ¯Πη
z,n under n number
of lags.
Now we can co-estimate the encoder ¯Πη
z,n together with the parameterized
matrices
(Aθ, Cθ) and matrix functions (Bθ, Kθ) of the Koopman model.
Fig. 2 shows the result-
ing network structure. Note that the computational cost of (3.18) can be further reduced
14
L. C. IACOB, M. SZ´ECSI, G. I. BEINTEMA, M. SCHOUKENS, AND R. T´OTH
Subspace encoder
Prediction map
-
-
τ = 0
τ = 1
τ = T −1
Cθ
Cθ
Cθ
ˆyk|k
yk
ˆek|k
Aθ
Bθ
Kθ
Aθ
Bθ
Kθ
uk
uk+T−2
¯Πη
z,n
ˆyk+1|k
ˆyk+T−1|k
. . .
. . .
yk+T−2
ˆzk|k
ˆzk+1|k
ˆzk+T−1|k
ˆek+T−2|k
yk, yk−1, . . . , yk−n
uk−1, . . . , uk−n
Figure 2: Network architecture. The lifted state at moment k, i.e., ˆzk|k, is estimated using
the encoder function ¯Πη
z,n based on previously measured input and output data.
by using a batched formulation, which allows to compute the cost of each section in parallel,
independent from each other. This is achieved by only summing over a subset of the sections,
which can also partially overlap. The reformulated batch cost function is:
V batch
DN
(θ, η) =
1
Nbatch
X
k∈I
1
T
T−1
X
τ=0
∥yk+τ −ˆyk+τ|k∥2
2
(3.20a)
I ⊂IN−T+1
n+1
= {n + 1, n + 2, . . . , N −T + 1}
(3.20b)
s.t. |I| = Nbatch
(3.20c)
which enables the application of advanced batch optimization algorithms like Adam [19].
Moreover, the complete dataset does not need to be fully loaded into the memory, making the
implementation more efficient [2].
4. Consistency analysis. Next, we show the consistency of the proposed identification
scheme that corresponds to the minimization of (3.18). In fact, under the assumption that
an exact finite-dimensional Koopman embedding of (3.1) in the form of (3.5) exists, we show
that the resulting model estimate will converge to an equivalent representation of the system
in the form (3.5) if the number of data points in the available data set DN tends to infinity,
that is, N →∞. The consistency analysis discussed in this section is an adaptation of the
arguments in [2] to the considered Koopman identification problem.
4.1. Convergence. As a first step, the convergence of the Koopman model estimate will
be shown. By satisfying Assumptions 1 and 2, the data-generating system (3.1) has an exact
representation by the Koopman form (3.5) according to Theorem 3.1. To show convergence,
this equivalent Koopman form of the system needs to satisfy the following stability condition:
Condition 1. For any δ > 0, there exist a c ∈[0, ∞) and a λ ∈[0, 1) such that
Ee{∥yk −˜yk∥4
2} < cλk,
∀k ≥0,
(4.1)
LEARNING KOOPMAN MODELS FROM DATA UNDER GENERAL NOISE CONDITIONS
15
under any initial conditions z0, ˜z0 ∈Rnz with ∥z0 −˜z0∥2 < δ and {(uτ, eτ)}k
τ=0 ∈S[0,∞], where
S[0,∞] is the σ-algebra generated by the random variables {(uτ, eτ)}∞
τ=0, and yk and ˜yk satisfy
(3.5) with the same (uk, ek), but with z0 and ˜z0.
To identify (3.5), the model structure Mξ is composed of the Koopman model (3.12) with
the forms of parametrization discussed in Section 3.3 and the subspace encoder (3.19) with the
parametrization discussed in Section 3.4, giving the total parameter vector ξ = [ θ⊤
η⊤]⊤
that is restricted to vary in a compact set Ξ ⊂Rnξ. This gives the model set M = {Mξ |
ξ ∈Ξ}. For each ξ ∈Ξ, the model Mξ with a given encoder lag n ≥1, can be written in a
one-step-ahead predictor form
(4.2)
ˆyk+τ|k = γpred
τ
(yk+τ−1
k−n
, uk+τ−1
k−n
, ξ),
which is a combination of γk based on (3.11) and encoder (3.17). Note that based on the
parametrizations discussed in Sections 3.3 and 3.4, γpred
(·)
is differentiable w.r.t. ξ everywhere
on an open neighborhood ˘Ξ of Ξ.
Furthermore, (4.2) is required to be stable under any
perturbation of the measured data, which is expressed as follows.
Condition 2. There exist scalars c ∈[0, ∞) and λ ∈[0, 1) such that, for any ξ ∈˘Ξ and for
any {(yτ, uτ)}k
τ=−n, {(˜yτ, ˜uτ)}k
τ=−n ∈R(ny+nu)×(n+k+1), the predictors
ˆypred
k
= γpred
k
(yk−1
−n , uk−1
−n , ξ),
˜ypred
k
= γpred
k
(˜yk−1
−n , ˜uk−1
−n , ξ),
satisfy
(4.3)
∥ˆypred
k
−˜ypred
k
∥2 ≤cσ(k),
∀k ≥0,
with σ(k) = Pk
τ=−n λk−τ  ∥uτ −˜uτ∥2 + ∥yτ −˜yτ∥2

and ∥γpred
k
(0k−1
−n , 0k−1
−n , ξ)∥2 ≤c, with
0k−1
−n = [0 . . . 0]⊤. Additionally, there exist c ∈[0, ∞) and λ ∈[0, 1) such that
∂
∂ξγpred
k
satisfies
(4.3) as well.
Now we can state the following theorem on convergence of the estimator.
Theorem 4.1. If the Koopman form (3.5) of the data-generating system satisfies Condition
1 with a quasi-stationary u independent of the white noise process e and the model set M
defined by (3.12) and (3.19) satisfies Condition 2, then
sup
vec(θ,η)∈Ξ
V enc
DN (θ, η) −Ee{V enc
DN (θ, η)}

2 →0,
(4.4)
with probability 1 as N →∞.
Proof. As the identification criterion (3.18a) satisfies Condition C1 in [24], the proof of
[24, Lemma 3.1] applies to the case considered.
4.2. Consistency. To formally show consistency, the Koopman form (3.5) of the data-
generating system must belong to the chosen set of models M. This means that there exists
a ξo ∈Ξ such that the one-step-ahead predictor γpred
k
associated with Mξo and the Koopman
form (3.5) of the data-generating system are the same. Unfortunately, a system can have many
16
L. C. IACOB, M. SZ´ECSI, G. I. BEINTEMA, M. SCHOUKENS, AND R. T´OTH
equivalent state-space representations; hence, even if in terms of (4.4), the estimator converges,
it can do so to just a ξ that corresponds to a different state-space representation expressing
the same dynamics. Therefore, we need to understand consistency w.r.t. an equivalence class
of (3.5). For this purpose, introduce Ξo ⊂Ξ, which contains all ξo ∈Ξo that correspond to
equivalent models of the data-generating system in the one-step-ahead prediction sense. Note
that if Ξo = ∅, then chosen parameterization based M can not describe the true (3.5) and
consistency cannot hold.
Before arriving at our result, we need to make sure that the data contains enough infor-
mation to recover the true underlying dynamics:
Condition 3. For the given model set M = {Mξ | ξ ∈Ξ} with ξ = [ θ⊤
η⊤]⊤, we
call the input sequence {uk}N−1
k=0 in DN generated by the Koopman form (3.5) of the data-
generating system weakly persistently exciting5, if for all pairs of parameters given by ξ1 ∈Ξ
and ξ2 ∈Ξ for which the function mapping is unequal, i.e., V enc
(·) (θ1, η1) ̸= V enc
(·) (θ2, η2), we
have
V enc
DN (θ1, η1) ̸= V enc
DN (θ2, η2)
(4.5)
with probability 1.
Next, to prove consistency, all elements of Ξo must have minimal asymptotic cost in terms
of limN→∞V enc
DN (θ, η). However, due to the prediction error nature of the used ℓ2-type loss
function together with the existence of Ee{V end
DN (θ, η)} (shown in Theorem 4.1), the minimal
asymptotic cost property of Ξo is satisfied by V enc
DN . For a detailed proof, see [24].
Theorem 4.2. Under the conditions of Theorem 4.1 and Condition 3,
lim
N→∞
ˆξN ∈Ξo
(4.6)
with probability 1, where
ˆξN = arg min
vec(θ,η)∈Ξ
V enc
DN (θ, η).
(4.7)
Proof. The proof is a direct application of Lemma 4.1 in [24] because the loss function
(3.18a) fulfills Condition (4.4) in [24].
5. Experiments and results. Next we test the proposed Koopman model identification
approach on a simulation study of a nonlinear Wiener-Hammerstein system that admits an
exact Koopman embedding and the publicly available Bouc-Wen oscillator-based identification
benchmark that has hysteretic behavior and it is notoriously hard to identify. Finally, we apply
our approach to capture a Koopman form of the the flight dynamics of a Crazyflie 2.1 nano
quadcopter using measured flight data.
5Note that the notion of persistency of excitation used here is in line with the classical notion of informativity
in system identification, see [25], and it implies distinguishability (under the data DN) of the achieved cost
and the predictors corresponding to the used model structure for θ values that do not correspond to equivalent
models.
LEARNING KOOPMAN MODELS FROM DATA UNDER GENERAL NOISE CONDITIONS
17
uk
ek
ek
LTI1
LTI2
f
vk
wk
¯vk
yk
ek
Figure 3: Wiener-Hammerstein system
5.1. Wiener-Hammerstein system. To illustrate the performance of the proposed Koop-
man model structure and learning method as well as the ability to handle process noise, we
consider a Wiener-Hammerstein system described by the interconnection of 2 single-input
single-output (SISO) LTI blocks and a polynomial nonlinearity, as shown in Fig. 3.
The
dynamics of the first block are
xk+1 = A1xk + B1uk + K1ek
(5.1a)
vk = C1xk
(5.1b)
with xk ∈Rnx the state vector, uk ∈R the input, and ek ∼N(0, σ2
e) being an i.i.d. white
noise process with standard deviation σe > 0, while A1 ∈Rnx×nx, B1 ∈Rnx, K1 ∈Rnx and
C1 ∈R1×nx. The output vk ∈R of (5.1) is affected by
(5.2)
wk = f(vk) = α0 + α1vk + α2v2
k + α3v3
k,
with {αi}3
i=1 ⊂R. As vk = C1xk, (5.2) can be written as:
(5.3)
f(vk) = f(C1xk) = α0 + α1C1xk + α2C(2)
1 x(2)
k
+ α3C(3)
1 x(3)
k .
We denote by (i) the Kronecker power, i.e., C(3) = C1 ⊗C1 ⊗C1, where ⊗is the Kronecker
product. Finally, the second linear block is described as
¯xk+1 = A2¯xk + B2wk + K2ek
(5.4a)
yk = C2¯xk
| {z }
¯vk
+ek
(5.4b)
with ¯xk ∈Rn¯x the state vector and with matrices similarly defined as for the first LTI block.
With nx = n¯x = 2, the exact numerical values of the matrices and the polynomial coefficients
are given in [14]. The system described by (5.1)–(5.4) can be exactly represented by a finite
dimensional Koopman model (3.5). For brevity, we refer the reader to [14] for the derivations,
which uses a similar finite dimensional conversion approach to [13]. The resulting lifted state
is
(5.5)
zk =
h
x⊤
k
(x(2)
k )⊤
(x(3)
k )⊤
¯x⊤
k
i⊤
.
To generate data, the input is considered as a white noise process with uniform distribution
uk ∼U(−1, 1), independent of e, while the standard deviation σe of e is chosen to obtain 5−30
dB levels of signal-to-noise ratio (SNR) at the output. Based on this, train, validation and test
18
L. C. IACOB, M. SZ´ECSI, G. I. BEINTEMA, M. SCHOUKENS, AND R. T´OTH
5
10
15
20
25
30
SNR [dB]
0.00
0.05
0.10
0.15
0.20
0.25
0.30
NRMS
Simulation results
No K
Linear K
K(z, u, e)
Figure 4: NRMS of the simulation responses of the process part of the Koopman
models w.r.t. a noiseless test data set, when the Koopman models are estimated
with noisy data under various SNR levels (Wiener-Hammerstein system).
5
10
15
20
25
30
SNR [dB]
0.0
0.1
0.2
0.3
0.4
0.5
0.6
0.7
0.8
NRMS
Prediction results
No K
Linear K
K(z, u, e)
True model - No K
True model - K(z, u, e)
Figure 5: NRMS of the one-step-ahead prediction by the Koopman models
w.r.t. noisy test data sets with different SNRs, when the Koopman models are
also estimated with noisy data under these SNR levels (Wiener-Hammerstein
system).
LEARNING KOOPMAN MODELS FROM DATA UNDER GENERAL NOISE CONDITIONS
19
data sets are generated of length N = 12000, 4000 and 4000, respectively, with independent
realizations of u and e.
In the considered Koopman model structure Mξ, defined by (3.12) and (3.19), the encoder
¯Πη
z,n, the input function Bθ and the innovation noise structure Kθ are parametrized as feed-
forward neural networks with 1 hidden layer, tanh activation and 40 neurons per layer for the
encoder and Bθ function, and 80 neurons for Kθ, while Aθ and Cθ are taken as parametrized
matrices (also Kθ in the linear case). The parameters are initialized using Xavier initialization
and we employ early stopping. The lifting dimension is selected to coincide with the exact
model, i.e., nz = 12 and we use an encoder lag of n = 12. The prediction horizon is chosen
to be T = 51 with a batch size of 256. For training, Adam optimization [19] is used with
the obtained training and validation data sets and with a learning rate of α = 10−3 and the
exponential decay rates set to β1 = 0.9 and β2 = 0.999. The quality of the obtained models
are assessed in terms of the normalized root mean square (NRMS) and RMS errors:
(5.6)
NRMS = RMS
σy
=
q
1
N−n
PN
k=n ∥ˆyk −yk∥2
2
σy
where σy is the sample standard deviation of y, giving NRMS ∈[0, 1]. Note that the first n
steps are skipped in (5.6) as they are used for the encoder function.
Fig. 4 shows the simulation performance of the identified models on noiseless test data
when trained on noisy data of particular SNRs. Models with various choices of Kθ are also
compared: no Kθ, linear Kθ, and general Kθ(ˆzk, uk, ˆek). It can be seen that the linear inno-
vation noise structure is able to reduce the approximation error with a factor of up to two
and slight improvements are obtained with the more complex noise model. Next, we ana-
lyse the one-step-ahead prediction performance. Similar to the simulation test case, Fig. 5
compares the NRMS errors of these model structures, in a filtering scenario, using noisy test
data. As in the simulation scenario, the models are trained on noisy data with the respective
SNRs. To provide context for these results, two additional dashed reference lines are included
in the figure which represent the one-step-ahead prediction error of the true model, showing
the proven convergence and consistency properties as the noise diminishes. It is also clear
that incorporating a linear Kθ significantly reduces the NRMS error compared to the base-
line model (which is correctly identified) without an innovation noise structure. In overall,
both the simulation and prediction results highlight the importance of the innovation noise
structure in increasing accuracy of the identified Koopman models.
5.2. Bouc-Wen benchmark. The Bouc-Wen oscillator benchmark [36, 37, 44] is exten-
sively used for testing capabilities of nonlinear system identification approaches as it describes
a system with hysteresis which is a challenging behavior to capture from data accurately. The
Bouc-Wen oscillator can be modeled as:
(5.7)
mL¨y + r(y, ˙y) + q(y, ˙y) = u,
with mL the mass, y its displacement, ˙y the velocity, and u the external force applied to
the system. The restoring force r(y, ˙y) is linear while q(y, ˙y) is a dynamic nonlinear function
describing the hysteresis curve.
Both these effects are extensively described in [44] where
20
L. C. IACOB, M. SZ´ECSI, G. I. BEINTEMA, M. SCHOUKENS, AND R. T´OTH
0
20
40
60
Samples (x10³)
−2
−1
0
1
2
y [mm]
Train
0
5
10
15
20
Samples (x10³)
−2
0
2
Validation
0
50
100
150
Samples (x10³)
−2
−1
0
1
2
Sinesweep Test
−100
0
100
u [N]
−0.5
0.0
0.5
1.0
Sine Test
0
2
4
6
8
Samples (x10³)
−2
−1
0
1
2
y [mm]
Multisine Test
Figure 6: Train, validation and test (multisine, sine and sinesweep) datasets used for the
experiments (Bouc-Wen benchmark).
the parameters are chosen for the Bouc-Wen benchmark such that the hysteretic behavior is
significantly present.
To estimate a Koopman model of the Bouc-Wen benchmark system, the training dataset
contains input-output data generated by using two sinusoidal signals with frequencies of 1 and
4 Hz, as well as four random phase multisine signals with frequency bands ranging from 1 to
150 Hz. For validation, a dataset is generated with an input containing a multisine signal also
with an excited frequency range between 1 and 150 Hz followed by a sinusoidal signal at 2 Hz.
For test data, the simulated response is generated by multisine and sinesweeep signals as given
in [44], as well as a 3 Hz sinusoidal signal to showcase the hysteretic behavior. Note that,
as detailed in [44], the data is sampled at a frequency of fs = 750 Hz. These used detasets
are shown in Fig. 6. As the data is noiseless, the estimation of a noise model is not required
which means that Kθ is set to 0.
To estimate a Koopman model of the system, the encoder ¯Πη
z,n and the input matrix
function Bθ are parametrized as feedforward neural networks with one hidden layer, having
tanh activation and 40 neurons and we use n = 5 number of lags. The network parameters
are initialized as in the previous example. The prediction horizon value is set to T = 101 with
a batch size 256. For training, a learning rate of α = 10−3 and exponential decays β1 = 0.9
and β2 = 0.999 are used.
Next, we show how different complexities in the B function as well as the lifting dimension
affect the approximation capabilities of Koopman models. This is shown in Fig. 7, for both
LEARNING KOOPMAN MODELS FROM DATA UNDER GENERAL NOISE CONDITIONS
21
25 10
20
30
50
100
Observables
0.00
0.05
0.10
0.15
0.20
0.25
NRMS
Multisine
B
Bz + B0
B(z)
B(z, u)
25 10
20
30
50
100
Observables
0.00
0.05
0.10
0.15
0.20
0.25
0.30
Sinesweep
Figure 7: Overview of NRMS errors of identified Koopman models with different complexities
of B (linear, bilinear, input affine, and general) and increasing lifting dimension using the
multisine and sinesweep test datasets (Bouch-Wen benchmark).
0
2
4
6
8
Samples (×10³)
−2
−1
0
1
2
y [mm]
test output
simulation error encoder
0
25
50
75
100
125
150
Samples (×10³)
−1.5
−1.0
−0.5
0.0
0.5
1.0
1.5
y [mm]
test output
simulation error encoder
−100
−50
0
50
100
u [N]
−0.75
−0.50
−0.25
0.00
0.25
0.50
0.75
1.00
y [mm]
test output
simulation encoder
Figure 8: Simulated output responses of the estimated model (B(z) structure with nz = 100)
on the test data under multisine (left) and sinesweep (centre) inputs and hysteretic behavior
(right) (Bouch-Wen benchmark).
the multisine and sinesweep tests, using a number of observables nz ∈{3, 5, 10, 20, 30, 50, 100}.
The linear Koopman model with constant B performs the worst, showing no significant im-
provement for larger nz.
The bilinear (BLTI) model shows a strong increase in accuracy
with larger lifting dimensions however, the overall improvement from nz = 10 to nz = 100
drastically slows down. The best performing models are the input affine (with B(z)) and full
22
L. C. IACOB, M. SZ´ECSI, G. I. BEINTEMA, M. SCHOUKENS, AND R. T´OTH
Method
gr-SS-NN
SS-NN Suykens Impr
SS-NN Suykens
Poly-NL-SS
RMS
7.53 × 10−6
8.91 × 10−6
2.65 × 10−5
1.34 × 10−5
Koopman structure
Linear
Bilinear
Input affine
General
RMS
1.60 × 10−4
3.69 × 10−5
1.43 × 10−5
1.59 × 10−5
Nr. observables
nz = 50
nz = 100
nz = 100
nz = 50
Table 1: Comparison of the estimated Koppman models with state of the art estimation
methods applied on the Bouch-Wen benchmark in terms of achieved simulation RMS on
multisine test data.
dependency (with B(z, u)) models, which demonstrate good approximation capability at only
a relatively small lifting dimension, (e.g., nz = 20). It can be seen that one can trade complex-
ity with lifting dimension and vice-versa. For example, a bilinear model is generally a good
trade-off between lifting dimension and approximation capability, while better approximation
results can be obtained with input affine or general models at lower dimensions (e.g. nz = 20
in this example) at the cost of model complexity. We do note that, somewhat nonintuitively,
we obtain the lowest error with the input affine model (see Table 1), instead of the general
model structure, which is due to the increased size of the parameerization and complexity of
the optimization problem. Moreover, as we utilize early stopping, it is possible that running
the learning for longer or optimizing the learning rates may produce better results. However,
a general conclusion is that a fully LTI model is unable to capture the system dynamics.
The best performing model in the multisine case is the model structure with input affine
complexity and a lifting dimension of nz = 100 (although a close result is also obtained with
nz = 20).
We use this model for comparing the results against other available methods.
In Fig. 8, the simulation results using the test data show a low error for the multisine and
sinesweep input excitation, and clearly show that the hysteretic behavior is well captured.
In Table 1, we can see that the simulation performance of the obtained Koopman model is
close to the state of the art (for the interested reader, the other methods are described in
more detail in [9, 43]). The approaches that obtain slightly better results do not impose a
particular structure on the learned model. The Koopman model (3.5) is able to accurately
capture the system behavior and offers a good overall trade-off between state dimension and
model complexity. Furthermore, even the more complex structures, i.e., input affine or general,
can be cast into LPV representations [12] for which there exist convex and computationally
efficient control methods [34].
5.3. Quadrotor example. In this section we demonstrate the applicability of the proposed
Koopman model identification approach on capturing the flight dynamics of a Crazyflie 2.1
quadrotor. We first show simulation results, followed by an experimental study on the real-
world system.
5.3.1. Simulation study. The considered simulation model of the drone implements the
rigid body dynamics as described in [28] and uses three coordinate frames: north-east-down
(NED) oriented inertial frame Fi; the vehicle frame Fv (origin at the centre of gravity of the
quadrotor) sharing the same orientation as Fi ; the body frame Fb (orientation fixed to the
quadrotor) whose origin coincides with Fv. The model has 12 motion states composed of the
LEARNING KOOPMAN MODELS FROM DATA UNDER GENERAL NOISE CONDITIONS
23
position s = [ x y z ]⊤, translational velocity v = [ vx vy vz ]⊤expressed in Fi, ζ = [ ϕ θ ψ ]⊤
describing the orientation as Z-Y-X Euler angles in Fv, and ω = [ p q
r]⊤, describing the
rotational velocity of Fb w.r.t. Fv, given in Fb. The inputs to the system are the total thrust
T and the torque vector τ = [ τϕ τθ τψ]⊤both given in Fb and produced by the four rotors.
The diagonal values of the inertia matrix of the drone are set to Jx = Jy = 1.4 × 10−5 kg·m2,
Jz = 2.17 × 10−5 kg·m2, and the off-diagonal values are 0, the mass is m = 0.027 kg, and
g = 9.8 m/s2, which are experimentally obtained using a real-world Crazyflie 2.1 quadrotor.
The simulation is performed with Runge-Kutta 4 integration at a sampling rate of 48 Hz,
accurately replicating the expected flight-dynamics.
As the system is unstable, flight-trajectories are generated by using a gain-scheduled linear
quadratic regulator (LQR) controller, designed w.r.t. the local linearisations at each time step
of the simulation model. The LQR is scheduled based on a desired state trajectory that is
calculated for a x-y-z-ψ defined flight-path reference by taking advantage of the differential
flatness property of the system, see [32]. We presume full state measurements, hence the
collected dataset consists of the system inputs and the states of the dynamical system. Since
the dynamics governing the evolution of the position states consist solely of integration, the
identification process can be simplified by focusing only on [ v⊤ζ⊤ω⊤]⊤. The size of the
recorded datasets can be viewed in Table 3. For more details about the simulation and data
collection procedure, the reader can refer to [51].
In our study, we have investigated various dependencies of the input matrix B and em-
ulated different levels of sensor noise. Additionally, we examined the effect of including the
original motion states among the observables by setting C = [ I
0 ] where I and 0 denote
identity and zero matrices of appropriate dimensions. This modification aids the design of
reference tracking controllers, as it allows the reference signal to be defined directly in terms
of the original motion states.
To train the Koopman models, a prediction horizon of T = 80 is selected for V batch
DN
,
corresponding to 1.7 seconds of flight. This duration is sufficient as it significantly exceeds
the largest time constants of a miniature quadrotor. During experiments, we found that a
lifted state dimension of nz = 40 works best. Dimensions lower than this failed to adequately
capture the system behavior, whereas dimensions higher than this led to overfitting, as ev-
idenced by elevated NRMS values during model testing.
The encoder ¯Πη
z,0 and the input
matrix function Bθ are parametrized as deep neural networks with 2 hidden layers, 64 nodes,
and tanh activation. With the availability of full-state measurements, the encoder only uses
one measurement corresponding to the present timestep, and so it is simplified to be the
lifting function. Parameter initialization is done identically to the previous experiments. For
optimization, a batch size of 256 is selected, with a learning rate of α = 10−4 and exponential
decay rates of β1 = 0.9 and β2 = 0.999. Additionally, an ℓ2 parameter regularization is added
to (3.18a) to prevent overfitting and we set the penalty coefficient to λ = 0.5 × 10−4.
Model performance across various nz values can be seen in Table 2 in terms of the 160-step
NRMS errors for the trained models on the test data set. For comparison purposes, results on
a full nonlinear model estimated by the SUBNET approach [51] are also included to indicate
performance of a nonlinear model estimate without any restrictions on the network structure.
In the network structure column, the subscripts (·)θ, (·)lin, and (·)I denote the implementation
of a function as a deep neural network, linear or identity layers. The superscript of A(·) denotes
24
L. C. IACOB, M. SZ´ECSI, G. I. BEINTEMA, M. SCHOUKENS, AND R. T´OTH
Data
Network structure
Noise
RMS
NRMS
Train
Validation
Test
Simulation
A20, Bθ(z), Clin
None
0.108
0.120
0.130
A40, Bθ(z), Clin
None
0.061
0.069
0.079
A60, Bθ(z), Clin
None
0.071
0.096
0.089
A40, Bθ(z), Clin
25 dB
0.106
0.120
0.089
A40, Bθ(z), Clin
20 dB
0.116
0.161
0.099
A40, Bθ(z, u), Clin
None
0.074
0.090
0.087
A40, Bθ(z), CI
None
0.069
0.095
0.087
General nonlinear
None
0.061
0.042
0.055
Real
A40, Bθ(z), Clin
Sensor3
0.163
0.213
0.228
A40, Bθ(z, u), Clin
Sensor
0.151
0.199
0.217
A40, Bθ(z), CI
Sensor
0.140
0.207
0.216
General nonlinear
Sensor
0.142
0.200
0.216
Table 2: Precision of various identified Koopman models in the quadrotor example. The used
model structures and the level of added noise to the datasets are specified along with the
required training time and NRMS errors w.r.t. both simulation and experimental datasets.
the lifted state-space dimension. The Koopman model achieves good performance in terms of
the NRMS error only slightly exceeding that of the nonlinear SUBNET. Similar to the Bouc-
Wen example, we found that the dependence of B on u slightly deteriorates the performance,
compared to the input affine model structure. In the table, the effects of measurement noise
can also be seen. Even at a level of 20 dB, the Koopman model remains capable of capturing
the dynamics. Enforcing the original states among the observables only slightly decreases the
simulation precision of the model, which we consider as a good tradeoff for the simpler model
structure.
5.3.2. Experimental results. The experimental setup consists of the Crazyflie 2.1 nano
quadrotor, equipped with onboard sensors and a microcontroller, the OptiTrack motion cap-
ture system for accurate global position measurements, and a ground control PC. State es-
timation is done by an extended Kalman filter also performing sensor fusion of the various
measurements.
Data collection is done at a control and sampling frequency of 200 Hz, which is higher than
in the simulation environment, but necessary for the agile maneuvering of the real quadrotor.
The size of the datasets are reported in Table 3.
For data collection and to conduct the
experiments, we use the same reference paths as in the simulation environment, executed by
the Mellinger controller [32] for reference tracking.
The network structures that were found to perform the best in the simulation environment
were used for training on the real dataset. The 200-step open loop test results can be viewed
in Table 2. The increase in NRMS values compared to simulation experiments may not fully
6No artificial noise was added, the real dataset was only affected by the noise inherent to the inaccuracies
of the various sensors equipped on the Crazyflie.
LEARNING KOOPMAN MODELS FROM DATA UNDER GENERAL NOISE CONDITIONS
25
Dataset sizes
Synthetic Real-world
Train
123 197
228 323
Validation
21 740
40 292
Test
480
3 000
Table 3: The sample size of train, validation,
and test datasets (quadrotor example).
Figure 9: Crazyflie 2.1 during flight.
0.00
0.25
0.50
0.75
1.00
1.0
0.5
0.0
0.5
vx [m
s ]
0.00
0.25
0.50
0.75
1.00
0.2
0.1
0.0
0.1
0.2
vy [m
s ]
0.00
0.25
0.50
0.75
1.00
1.0
0.5
0.0
0.5
vz [m
s ]
0.00
0.25
0.50
0.75
1.00
5
0
5
10
[ ]
0.00
0.25
0.50
0.75
1.00
40
20
0
20
[ ]
0.00
0.25
0.50
0.75
1.00
1
2
3
4
[ ]
0.00
0.25
0.50
0.75
1.00
t [sec]
1.5
1.0
0.5
0.0
0.5
p [rad
s ]
0.00
0.25
0.50
0.75
1.00
t [sec]
2
0
2
4
q [rad
s ]
0.00
0.25
0.50
0.75
1.00
t [sec]
0.1
0.0
0.1
r [rad
s ]
Koopman 
Nonlinear SUBNET
Real system
,
,
Figure 10: Simulation results of the estimated Koopman model and the estimated nonlinear
SUBNET model w.r.t. the measured flight data in the test data set.
represent the actual performance of the trained models. In open-loop simulations, deviations
inevitably grow as errors accumulate over time and more critical is the resemblance between
the shapes of the Koopman model outputs and the real system. Also, there are unmeasured
deterministic disturbances such as airflow effects on the real quadcopter, which can not be
fully captured by the considered noise model. As can be seen in Fig. 10 and Table 2, the
Koopman models closely match the performance of the general nonlinear SUBNET — in the
identity output case they are identical — demonstrating that the Koopman models accurately
capture the dynamics of the system.
6. Conclusion. In this paper a deep-learning-based Koopman identification method for
nonlinear systems driven by an external input and affected by process and measurement noise
is proposed, which provides statistically consistent estimation of the underlying nonlinear dy-
namics. For this purpose, we have shown that under control inputs and innovation noise,
the data-generating system can be written in a Koopman model form, which in turn can be
26
L. C. IACOB, M. SZ´ECSI, G. I. BEINTEMA, M. SCHOUKENS, AND R. T´OTH
used for formulating a one-step-ahead predictor. With the help of this predictor and under
various levels of complexity in the parameterization of the input and innovation matrices, it
has been shown that we can formulate a computationally efficient multiple-shooting-based
learning method that minimizes the mean squared prediction error of the model. To circum-
vent a priori heuristic choice of a dictionary of observables, a neural-network-based encoder is
used for the lifting and state-estimation, which is consistent with the reconstructability map of
the Koopman model. Compared to other learning-based Koopman identification methods, the
proposed approach not only provides theoretical guarantees of consistency and a computation-
ally efficient learning pipeline even in case when no direct state measurments are available, but
it is also shown to successfully capture the underlying nonlinear behavior in various examples,
from identification benchmarks to real-world flight dynamics of a quadcopter.
Appendix A. Proof of Theorem 3.1.
To show that (3.5) is an exact embedding of (3.1),
we employ function factorization through the second fundamental theorem of calculus (FTC),
extending the approach in [12] to systems with process noise. Based on (3.2), we have the
following decomposition:
(A.1)
xk+1 = fd(xk, uk, ek) = f(xk) + g(xk, uk) + d(xk, uk, ek)
with g(xk, 0) = 0 and d(xk, uk, 0) = 0. The proof is composed of three steps:
Step 1: Embedding the autonomous part: Take uk = 0, ek = 0, implying g(xk, 0) = 0 and
d(xk, uk, 0) = 0 such that xk+1 = f(xk). Then, based on Assumption 1, it holds that:
(A.2)
Φ(xk+1) = Φ(f(xk)) = AΦ(xk).
Step 2: Embedding the control input part: Take ek = 0, implying d(xk, uk, 0) = 0 such
that xk+1 = f(xk) + g(xk, uk). Using the results in [12] and (A.2), the exact lifted form of
xk+1 = f(xk) + g(xk, uk) is:
(A.3)
Φ(xk+1) −Φ(f(xk))
|
{z
}
AΦ(xk)
=
 Z 1
0
∂Φ
∂x (f(xk) + λg(xk, uk)) dλ
!
g(xk, uk)
|
{z
}
˜Bx(xk,uk)
.
Step 3: Embedding the noise part: For the full nonlinear dynamics described by:
(A.4)
xk+1 = f(xk) + g(xk, uk) + d(xk, uk, ek),
we can apply the proof of Theorem 2 in [12]: in Eq. (43) in [12], chose qk+1 = xk+1 (which
is expanded as (A.4)) and pk+1 = f(xk) + g(xk, uk), giving an exact lifted form that includes
the effect of noise as:
(A.5)
Φ(xk+1) −Φ(f(xk) + g(xk, uk))
|
{z
}
AΦ(xk)+ ˜Bx(xk,uk)
=
=
 Z 1
0
∂Φ
∂x (f(xk) + g(xk, uk) + λd(xk, uk, ek)) dλ
!
d(xk, uk, ek)
|
{z
}
˜
Kx(xk,uk,ek)
.
LEARNING KOOPMAN MODELS FROM DATA UNDER GENERAL NOISE CONDITIONS
27
By applying the exact factorization Lemma 1 in [12], we get:
(A.6)
Φ(xk+1) = AΦ(xk) + Bx(xk, uk)uk + Kx(xk, uk, ek)ek
with
Bx(xk, uk) =
Z 1
0
∂˜Bx
∂u (xk, λuk) dλ, Kx(xk, uk, ek) =
Z 1
0
∂˜Kx
∂e (xk, uk, λek) dλ.
Furthermore, let zk = Φ(xk) and xk = Φ†(zk), where † denotes the inverse. Then, considering
that Assumption 2 holds, i.e., h ∈span{Φ}, an exact finite dimensional Koopman embedding
of (3.1) is given by:
zk+1 = Azk + B(zk, uk)uk + K(zk, uk, ek)ek
yk = Czk + ek
(A.7)
with B(zk, uk) := Bx(Φ†(zk), uk), K(zk, uk, ek) := Kx(Φ†(zk), uk, ek).
REFERENCES
[1] J. Alexandre Pinto Sales de Noronha, Suficient conditions for reconstructability on the autonomous
continuous time SUBNET method, Eindhoven University of Technology, 2023, https://research.tue.nl/
nl/publications/suficient-conditions-for-reconstructability-on-the-autonomous-con/. Stageverslag.
[2] G. I. Beintema, M. Schoukens, and R. T´oth, Deep subspace encoders for nonlinear system identifi-
cation, Automatica, 156 (2023), p. 111210.
[3] M. Bonnert and U. Konigorski, Estimating Koopman invariant subspaces of excited systems using
artificial neural networks, 21st IFAC World Congress, Berlin, Germany, 53 (2020), pp. 1156–1162.
[4] D. Bruder, X. Fu, and R. Vasudevan, Advantages of bilinear Koopman realizations for the modeling
and control of systems with unknown dynamics, IEEE Robotics and Automation Letters, 6 (2020),
pp. 4369–4376.
[5] S. L. Brunton, B. W. Brunton, J. L. Proctor, and J. N. Kutz, Koopman invariant subspaces and
finite linear representations of nonlinear dynamical systems for control, PLoS ONE, 11 (2016).
[6] S. L. Brunton, M. Budiˇsi´c, E. Kaiser, and J. N. Kutz, Modern Koopman theory for dynamical
systems, SIAM Review, 64 (2022), pp. 229–340.
[7] S. L. Brunton, J. L. Proctor, and J. N. Kutz, Discovering governing equations from data by sparse
identification of nonlinear dynamical systems, Proceedings of the National Academy of Sciences, 113
(2016), pp. 3932–3937.
[8] P. S. Cisneros, A. Datar, P. G¨ottsch, and H. Werner, Data-driven quasi-LPV model predictive
control using Koopman operator techniques, 21st IFAC World Congress, 53 (2020), pp. 6062–6068.
[9] A. Fakhrizadeh Esfahani, P. Dreesen, K. Tiels, J.-P. No¨el, and J. Schoukens, Parameter reduc-
tion in nonlinear state-space identification of hysteresis, Mechanical Systems and Signal Processing,
104 (2018), pp. 884–895.
[10] L. C. Iacob, G. I. Beintema, M. Schoukens, and R. T´oth, Deep identification of nonlinear systems
in Koopman form, in 60th IEEE Conference on Decision and Control (CDC), 2021, pp. 2288–2293.
[11] L. C. Iacob, M. Schoukens, and R. T´oth, Finite dimensional Koopman form of polynomial nonlinear
systems, 22nd IFAC World Congress, Yokohama, Japan, 56 (2023), pp. 6423–6428.
[12] L. C. Iacob, R. T´oth, and M. Schoukens, Koopman form of nonlinear systems with inputs, Auto-
matica, 162 (2024), p. 111525.
[13] L. C. Iacob, R. T´oth, and M. Schoukens, Exact finite Koopman embedding of block-oriented polyno-
mial systems, 2025, https://arxiv.org/abs/2507.15093.
28
L. C. IACOB, M. SZ´ECSI, G. I. BEINTEMA, M. SCHOUKENS, AND R. T´OTH
[14] L. C. Iacob, R. T´oth, and M. Schoukens, Exact Koopman Embedding of Discrete Time Wiener-
Hammerstein Structure with Noise, Technical Report, Eindhoven University of Technology, 2025.
[15] A. Isidori, Nonlinear Control Systems, Springer London, 3 ed., 1995.
[16] L. Jiang and N. Liu, Correcting noisy dynamic mode decomposition with Kalman filters, Journal of
Computational Physics, 461 (2022), p. 111175.
[17] R. M. Jungers and P. Tabuada, Non-local linearization of nonlinear differential equations via polyflows,
in 2019 American Control Conference (ACC), 2019, pp. 1–6.
[18] P. Ketthong, J. Samkunta, N. T. Mai, M. A. S. Kamal, I. Murakami, and K. Yamada, Data-
driven Koopman based system identification for partially observed dynamical systems with input and
disturbance, Sci, 6 (2024).
[19] D. P. Kingma and J. Ba, Adam: A method for stochastic optimization, in International Conference on
Learning Representations (ICLR), 2015.
[20] M. Korda and I. Mezi´c, Linear predictors for nonlinear dynamical systems: Koopman operator meets
model predictive control, Automatica, 93 (2018), pp. 149–160.
[21] J. Levine and R. Marino, Nonlinear system immersion, observers and finite-dimensional filters, Sys-
tems & Control Letters, 7 (1986), pp. 133–142.
[22] Y. Lian and C. N. Jones, On Gaussian process based Koopman operators, 21st World Congress, Berlin,
Germany, 53 (2020), pp. 449–455.
[23] Z. Liu, N. Ozay, and E. D. Sontag, Properties of immersions for systems with multiple limit sets with
implications to learning Koopman embeddings, Automatica, 176 (2025), p. 112226.
[24] L. Ljung, Convergence analysis of parametric identification methods, IEEE Transactions on Automatic
Control, 23 (1978), pp. 770–783.
[25] L. Ljung, System Identification: Theory for the User, Prentice Hall PTR, 2 ed., 1999.
[26] L. Ljung, System Identification: An Overview, Springer, London, 2013, pp. 1–20.
[27] B. Lusch, J. N. Kutz, and S. L. Brunton, Deep learning for universal linear embeddings of nonlinear
dynamics, Nature Communications, 9 (2018).
[28] R. Mahony, V. Kumar, and P. Corke, Multirotor Aerial Vehicles: Modeling, Estimation, and Control
of Quadrotor, IEEE Robotics & Automation Magazine, 19 (2012), pp. 20–32.
[29] G. Mamakoukas, M. L. Casta˜no, X. Tan, and T. D. Murphey, Derivative-based Koopman operators
for real-time control of robotic systems, IEEE Transactions on Robotics, 37 (2020), pp. 2173–2192.
[30] A. Mauroy and J. Goncalves, Koopman-based lifting techniques for nonlinear systems identification,
IEEE Transactions on Automatic Control, 65 (2020), pp. 2550–2565.
[31] A. Mauroy, I. Mezi´c, and Y. Susuki, The Koopman Operator in Systems and Control: Concepts,
Methodologies, and Applications, Springer International Publishing, 2020.
[32] D. Mellinger and V. Kumar, Minimum snap trajectory generation and control for quadrotors, in Proc.
of the IEEE Int. Conf. on Rob. and Aut., 2011, pp. 2520–2525.
[33] I. Mezi´c, Koopman operator, geometry, and learning of dynamical systems,, Notices of the American
Mathematical Society, 68 (2021), p. 1087–1105.
[34] J. Mohammadpour and C. W. Scherer, Control of Linear Parameter Varying Systems with Applica-
tions, Springer, 2012.
[35] H. Nijmeijer, Observability of autonomous discrete time non-linear systems: a geometric approach,
International Journal of Control, 36 (1982), pp. 867–874.
[36] J.-P. No¨el and M. Schoukens, Hysteretic benchmark with a dynamic nonlinearity, 2020, https://doi.
org/10.4121/12967592.v1.
[37] J.-P. No¨el and M. Schoukens, Nonlinear benchmark: Bouc-Wen hysteretic system, 2025, https://
www.nonlinearbenchmark.org/benchmarks/bouc-wen (accessed 18-03-2025).
[38] S. Otto, S. Peitz, and C. Rowley, Learning bilinear models of actuated Koopman generators from
partially observed trajectories, SIAM Journal on Applied Dynamical Systems, 23 (2024), pp. 885–923.
[39] S. Otto and C. Rowley, Linearly recurrent autoencoder networks for learning dynamics, SIAM Journal
on Applied Dynamical Systems, 18 (2019), pp. 558–593.
[40] F. M. Philipp, M. Schaller, K. Worthmann, S. Peitz, and F. N¨uske, Error bounds for kernel-based
approximations of the Koopman operator, Applied and Computational Harmonic Analysis, 71 (2024),
p. 101657.
[41] A. H. Ribeiro, K. Tiels, J. Umenberger, T. B. Sch¨on, and L. A. Aguirre, On the smoothness of
LEARNING KOOPMAN MODELS FROM DATA UNDER GENERAL NOISE CONDITIONS
29
nonlinear system identification, Automatica, 121 (2020), p. 109158.
[42] C. Rowley, I. Mezi´c, S. Bagheri, P. Schlatter, and D. Henningson, Spectral analysis of nonlinear
flows, Journal of Fluid Mechanics, 641 (2009), pp. 115–127.
[43] M. Schoukens, Improved initialization of state-space artificial neural networks, in 2021 European Control
Conference (ECC), 2021, pp. 1913–1918.
[44] M. Schoukens and J. No¨el, Three benchmarks addressing open challenges in nonlinear system identi-
fication, 20th IFAC World Congress, Toulouse, France, 50 (2017), pp. 446–451.
[45] J. C. Schulze, D. T. Doncevic, and A. Mitsos, Identification of mimo Wiener-type Koopman models
for data-driven model reduction using deep learning, Computers & Chemical Engineering, 161 (2022),
p. 107781.
[46] H. Shi and M. Q.-H. Meng, Deep Koopman operator with control for nonlinear systems, IEEE Robotics
and Automation Letters, 7 (2022), pp. 7700–7707.
[47] S. Sinha, S. P. Nandanoori, and D. A. Barajas-Solano, Online real-time learning of dynamical
systems from noisy streaming data, Scientific Reports, 13 (2023), p. 22564.
[48] J. Stark, Delay embeddings for forced systems. I. Deterministic forcing, Journal of Nonlinear Science, 9
(1999), pp. 255–332.
[49] J. Stark, D. S. Broomhead, M. E. Davies, and J. Huke, Delay embeddings for forced systems. II.
Stochastic forcing, Journal of Nonlinear Science, 13 (2003), pp. 519–577.
[50] A. Surana, Koopman operator based observer synthesis for control-affine nonlinear systems, in IEEE
55th Conference on Decision and Control (CDC), 2016, pp. 6492–6499.
[51] M. Sz´ecsi, B. Gy¨or¨ok, A. Weinhardt-Kov´acs, G. I. Beintema, M. Schoukens, T. P´eni, and
R. T´oth, Deep learning of vehicle dynamics, in 20th IFAC Symposium on System Identification
SYSID 2024, vol. 58, Jan. 2024, pp. 283–288.
[52] N. Takeishi, Y. Kawahara, and T. Yairi, Learning Koopman invariant subspaces for dynamic mode
decomposition, in International Conference on Neural Information Processing Systems (NIPS), 2017.
[53] F. Takens, Detecting strange attractors in turbulence, in Dynamical Systems and Turbulence, Warwick
1980, D. Rand and L.-S. Young, eds., Springer Berlin Heidelberg, 1981, pp. 366–381.
[54] B. van der Heijden, L. Ferranti, J. Kober, and R. Babuˇska, Deepkoco: Efficient latent plan-
ning with a task-relevant Koopman representation, in 2021 IEEE/RSJ International Conference on
Intelligent Robots and Systems (IROS), 2021, pp. 183–189.
[55] P. van Goor, R. Mahony, M. Schaller, and K. Worthmann, Maximum-likelihood reprojections for
reliable Koopman-based predictions and bifurcation analysis of parametric dynamical systems, 2025,
https://arxiv.org/abs/2506.17817.
[56] Z. Wang and R. M. Jungers, A data-driven immersion technique for linearization of discrete-time
nonlinear systems, 21st World Congress, Berlin, Germany, 53 (2020), pp. 869–874.
[57] Z. Wang, R. M. Jungers, and C. J. Ong, Computation of invariant sets via immersion for discrete-
time nonlinear systems, Automatica, 147 (2023), p. 110686.
[58] M. Williams, I. Kevrekidis, and C. Rowley, A data–driven approximation of the Koopman operator:
Extending dynamic mode decomposition, Journal of Nonlinear Science, 25 (2015), pp. 1307–1346.
[59] M. O. Williams, C. W. Rowley, and I. G. Kevrekidis, A kernel-based method for data-driven
Koopman spectral analysis, Journal of Computational Dynamics, 2 (2015), pp. 247–265.
[60] W. S. Wong, New classes of finite-dimensional nonlinear filters, Systems & Control Letters, 3 (1983),
pp. 155–164.
[61] E. Yeung, S. Kundu, and N. O. Hodas, Learning deep neural network representations for Koopman
operators of nonlinear dynamical systems, in American Control Conference (ACC), 2019, pp. 2832–
4839.
