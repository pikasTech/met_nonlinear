# Cruz_2025_SS_KAN

## Page 1

arXiv:2506.16392v1  [cs.LG]  19 Jun 2025
State-Space Kolmogorov Arnold Networks for
Interpretable Nonlinear System Identification
Gonc¸alo G. Cruz, Bal´azs Renczes, Mark C. Runacres and Jan Decuyper
Abstract— While accurate, black-box system identifica-
tion models lack interpretability of the underlying system
dynamics. This paper proposes State-Space Kolmogorov-
Arnold Networks (SS-KAN) to address this challenge by
integrating Kolmogorov-Arnold Networks within a state-
space framework. The proposed model is validated on
two benchmark systems: the Silverbox and the Wiener-
Hammerstein benchmarks. Results show that SS-KAN pro-
vides enhanced interpretability due to sparsity-promoting
regularization and the direct visualization of its learned
univariate functions, which reveal system nonlinearities
at the cost of accuracy when compared to state-of-the-
art black-box models, highlighting SS-KAN as a promising
approach for interpretable nonlinear system identification,
balancing accuracy and interpretability of nonlinear system
dynamics.
Index Terms— Nonlinear systems identification, Grey-
box modelling, Machine learning
I. INTRODUCTION
S
YSTEM identification, the process of building mathemati-
cal models from observed data, is a fundamental discipline
in engineering and control. Accurate system models are useful
for tasks ranging from controller design and performance
optimization to fault detection and system analysis. Linear
system identification techniques have provided a robust and
well-understood framework for modeling linear systems [1].
However, real-world engineering systems are often nonlinear,
and relying solely on linear models can lead to inadequate
performance or even instability, particularly when operating in
extended regimes or encountering complex dynamics. While
black-box nonlinear system identification methods, especially
This article has been accepted for publication in IEEE Con-
trol
Systems
Letters.
Citation
information:
DOI
10.1109/LC-
SYS.2025.3578019. For the publisher’s version and full citation
details see: https://doi.org/10.1109/LCSYS.2025.3578019
Manuscript received March 17, 2025; revised April 21, 2025; accepted
June 2, 2025. Date of publication June 09, 2025.
This work was funded by the Strategic Research Program SRP60 of
the Vrije Universiteit Brussel.
G.G. Cruz, M. C. Runacres and J. Decuyper are with the Faculty
of Engineering Technology, Vrije Universiteit Brussel, 1050 Brussel,
Belgium (e-mail: goncalo.granjal.cruz@vub.be;mark.runacres@vub.be;
jan.decuyper@vub.be)
B. Renczes is with the Department of Artificial Intelligence and Sys-
tems Engineering, Budapest University of Technology and Economics,
Budapest, Hungary (e-mail: renczes@mit.bme.hu)
©2025 IEEE. All rights reserved, including rights for text and data
mining and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE
permission.
those leveraging deep neural networks, have demonstrated
impressive accuracy in capturing complex nonlinear behav-
iors [2], as highlighted in comprehensive reviews of recent
advancements and challenges in the field [3], a critical lim-
itation remains: their inherent lack of interpretability. Black-
box models lack transparency between model structure and
system physics by representing dynamics in latent spaces with
a high number of parameters, thus limiting the understanding
of the identified system’s behavior. Existing techniques like
polynomial decoupling have been proposed to address this
challenge by simplifying complex nonlinearities into more
understandable forms, aiming to extract structured models
from black-box representations [4], [5], though these might be
constrained by the initial black-box model’s structure. Other
authors have explored augmenting physical models [6] and
imposing prior physical information [7], reinforcing model
transparency and physical consistency.
To address the interpretability challenge, Kolmogorov-
Arnold Networks (KANs) [8] have emerged as an alternative,
expressing any multivariate continuous function as a sum of
compositions of learnable univariate functions. This structured
decomposition makes KANs more interpretable than tradi-
tional black-box models, being explored in various scientific
machine learning applications, potentially enabling hidden
physics discovery [9], [10], though practical challenges are
still under investigation [11].
In the context of system identification, KANs offer mul-
tiple advantages for modeling nonlinear systems, that are
actively being studied [12]. Their structured representation,
based on univariate functions, aims to capture complex non-
linear dynamics while simultaneously enhancing interpretabil-
ity, making them attractive for modeling unknown system
behaviors from input-output data. Moreover, the functional
decomposition inherent in KANs offers the potential to extract
meaningful insights from identified models, such as identifying
dominant input variables influencing system behavior. This
transparency can be valuable for understanding the identified
system and potentially for ensuring physical consistency in the
learned model.
In this paper, we propose State-Space Kolmogorov Arnold
Networks (SS-KAN), an approach that integrates KANs into a
state-space structure. Our primary contributions are the devel-
opment of this architecture, the demonstration of its trade-off
between accuracy and enhanced interpretability through the
visualization of learned univariate functions, and its successful
application to complex benchmark systems.


---

## Page 2

II. KOLMOGOROV-ARNOLD NETWORKS
KANs are an alternative neural network architecture in-
spired by the Kolmogorov-Arnold representation theorem,
which states that any continuous multivariate function f(x) :
[0, 1]n 7→R can be expressed as a sum of compositions of
univariate functions:
f(x) =
2n+1
X
q=1
Φq
 n
X
p=1
ϕq,p (xp)
!
(1)
where ϕq,p : [0, 1] 7→R are “inner” univariate functions
applied to individual input variables xp, and Φq : R 7→R
are “outer” univariate functions applied to the sum of these
inner function outputs. This essentially means that complex
functions can be decomposed into sums of simpler, one-
dimensional transformations.
Extending this concept, a KAN [8] structures these univari-
ate functions sequentially into L layers:
KAN(x) = (ΦL−1 ◦ΦL−2 ◦· · · ◦Φ1 ◦Φ0) (x)
(2)
where ◦denotes function composition and each layer function
Φl consists of learnable univariate functions that connect to the
next layer l + 1.
Considering layer l has nl nodes corresponding to outputs
from the previous layer, and layer l+1 has nl+1 nodes, then Φl
can be expressed as a matrix of learnable univariate functions,
ϕl,i,j(·):
Φl =




ϕl,1,1(·)
ϕl,1,2(·)
· · ·
ϕl,1,nl(·)
ϕl,2,1(·)
ϕl,2,2(·)
· · ·
ϕl,2,nl(·)
...
...
...
ϕl,nl+1,1(·)
ϕl,nl+1,2(·) · · ·
ϕl,nl+1,nl(·)



(3)
where each univariate function ϕ is parameterized as a sum of
a SiLU residual activation function and a linear combination
of B-spline functions, ϕ(x) = wbSiLU(x) + ws
P
i ciBi(x)
where the coefficients ci of the B-splines, as well as the scaling
factors wb and ws, are learnable parameters.
Unlike traditional neural networks with fixed nodal acti-
vations and learnable scalar weights on edges, KANs feature
learnable univariate activation functions on the edges and sum-
mations at the nodes. This can reduce the number of required
parameters while simultaneously increasing interpretability, as
the learned shapes of these edge functions can be visualized,
making KANs an attractive option for interpretable nonlinear
system identification.
III. STATE-SPACE KOLMOGOROV-ARNOLD NETWORKS
Building upon the motivation for interpretable system iden-
tification and drawing inspiration from the structural advan-
tages of state-space models and the interpretability of KANs,
we propose State-Space Kolmogorov-Arnold Networks (SS-
KAN). This approach aims to combine the strengths of both
methodologies: the physically meaningful structure of state-
space representations with the function approximation and
interpretability capabilities of KANs.
A general nonlinear dynamical system in a discrete-time
state-space form is written as:
x(k + 1) = Ax(k) + Bu(k) + f(x(k), u(k))
y(k) = Cx(k) + Du(k) + g(x(k), u(k))
(4)
where x(k) ∈Rnx represents the nx-dimensional state vector
at time step k, u(k) ∈Rnu is the nu-dimensional forcing
input, and y(k) ∈Rny denotes the ny-dimensional observable
output. The matrices A
∈
Rnx×nx and B
∈
Rnx×nu
are the discrete-time state and input matrices respectively,
representing the linear part of the state transition. The function
f : Rnx × Rnu →Rnx is a nonlinear function describing
nonlinear state transitions. Similarly, C ∈Rny×nx and D ∈
Rny×nu are the output and direct feedthrough matrices, and
g : Rnx × Rnu →Rny is a nonlinear function for the output
mapping. While traditional black-box system identification
might directly model the entire nonlinear system using a
large neural network, SS-KAN aims to retain the linear state-
space structure and enhance interpretability by modeling the
nonlinear functions f(·) and g(·). This explicit separation
simplifies the complexity of the functions KANs must ap-
proximate, improving training stability and allowing for stable
linear initialization, which is a common approach in system
identification and naturally reduces initialization sensitivity
inherent in KANs.
A. SS-KAN model structure
To formalize the SS-KAN architecture, we propose to
replace the unknown nonlinear functions f(·) and g(·) in (4)
with KANs. This leads to the SS-KAN model equations:
x(k + 1) = Ax(k) + Bu(k) + KANf(x(k), u(k))
y(k) = Cx(k) + Du(k) + KANg(x(k), u(k))
(5)
where KANf : Rnx × Rnu →Rnx and KANg : Rnx ×
Rnu →Rny. In this work, we utilize the efficientkan [13]
implementation of KANs. The inputs to both KANf and
KANg are the state vector x(k) and the input vector u(k).
The trainable parameters of the SS-KAN model, denoted
by θ, are composed of the linear state-space matrices and the
weights of the KAN:
θ = [A, B, C, D, θKANf , θKANg]T
(6)
where θKANf and θKANg represent the sets of trainable param-
eters within the KANs used for the state transition and output
mapping nonlinearities, respectively.
B. Cost Function and Optimization
The SS-KAN model parameters (6) are trained by min-
imizing a cost function that balances model accuracy with
interpretability:
L(θ) = 1
N ∥ySS−KAN −ydata∥2
2
+ λL2

∥A∥2
F + ∥B∥2
F + ∥C∥2
F + ∥D∥2
F

+ λL1
 ∥θKANf ∥1 + ∥θKANg∥1

(7)


---

## Page 3

Here, the first term represents the mean squared L2 norm
error, quantifying the discrepancy between the predicted output
ySS−KAN and the available ydata over N data points. The
second term is an L2 regularization penalty with the Frobenius
norm applied to the linear state-space matrices (A, B, C, D),
with λL2 controlling its strength to improve generalization of
the linear components and prevent overfitting. The third term
is an L1 regularization penalty on the KAN parameters (θKANf
and θKANg), with λL1 controlling its strength to promote
sparsity in the activation functions thus increasing the model
interpretability. In this work, for the internal KAN architecture,
we utilize cubic B-splines defined on a 5-point grid for each
univariate function and use two layers to showcase benchmark
interpretability. Increasing grid points can enhance detail but
adds parameters, while deeper KANs might be needed for
highly complex systems.
To optimize the model parameters θ, we utilize the AdamW
optimizer [14] with conservative initial learning rates, as this
was found to stabilize convergence. The training process em-
ploys batch optimization which was found to speedup conver-
gence. The training dataset is divided into empirically chosen
B batches of size Nbatch = N/B. The data is normalized
before training to a [-1,1] range where the B-splines domain
is initially defined, and is processed sequentially in time to
maintain temporal dependencies within each epoch.
The performance of the SS-KAN model is quantitatively
evaluated using the Root Mean Squared Error (RMSE). RMSE
provides a measure of the average error magnitude between
the predicted output ySS−KAN and the measured data ydata.
For a dataset with N data points, RMSE is defined as:
RMSE =
v
u
u
t 1
N
N
X
k=1
(ySS−KAN(k) −ydata(k))2
(8)
C. On the connection with decoupled state-space
models
A key aspect of regaining interpretability in KANs lies in
their reliance on an additive structure of univariate functionals.
Since univariate functions can be easily visualized, this often
leads to valuable insights into nonlinear relationships. Building
on similar reasoning, so-called decoupled functions have also
been proposed. In this approach, nonlinearity is constrained
within a set of so-called univariate “branches”, effectively
decoupling the multivariate relationship. Decoupled functions
are defined as f(x) = Wg
 VT x

, with univariate functions
gi(zi) : R 7→R of linear forms zi := v⊤
i x, and i = 1, . . . , r.
Here, r is the number of branches, and W and V are linear
transformation matrices. It has been demonstrated [15] that
a broad class of multivariate functions can be accurately
approximated in a decoupled form. A notable distinction is
that KANs use regularization to promote sparsity and model
simplicity, while in decoupled functions, model complexity
is usually controlled through the parameter r. Beyond visu-
alizing the nonlinearities, further insight may be gained by
examining the inputs to the nonlinear components, particularly
in systems where a dominant nonlinear term involves a specific
physical state variable (e.g., a hardening spring in mechanical
systems, see section IV). In this regard [5] demonstrated that
single-branch decoupled functions, when embedded in state-
space models, could yield physically meaningful intermediate
variables zi. However, this physical interpretability is not
preserved in the state variables themselves, due to the mixing
introduced by the linear transformation matrix V. KANs, on
the other hand, guided towards a lean network through regu-
larization, may naturally revert to a structure where only one
of the input variables drives the nonlinearity. Since SS-KANs
take the state variables as input, and under the assumption
of a well-approximated nonlinearity, this structure may help
preserve or even promote physical interpretability of the state
variables themselves, particularly for systems governed by a
single dominant nonlinear term.
IV. SILVERBOX TEST CASE - DUFFING OSCILLATOR
To evaluate the effectiveness of the SS-KAN model, we
consider the well-known Silverbox benchmark system [16],
which can be viewed as an electronic version of the forced
Duffing oscillator, a second-order nonlinear system with a cu-
bic nonlinearity. The Duffing oscillator is a widely recognized
benchmark in nonlinear system identification due to its well-
characterized nonlinear behavior and relevance to many physi-
cal systems, particularly in mechanics and structural dynamics.
The true equation of motion for the Duffing oscillator is given
by:
m¨x + c ˙x + kx + αx3 = u(t)
(9)
where, x represents the displacement, ˙x and ¨x are its time
derivatives, m is the mass, c is the damping coefficient, k
is the linear stiffness, α is the cubic nonlinear stiffness, and
u(t) is the external forcing input. The cubic term αx3 is the
key nonlinear element that we aim to identify and interpret
using our SS-KAN approach in a pure system identification
approach where the true parameters of the Duffing oscillator
(m, c, k, α) are unknown.
The data for the Silverbox benchmark is obtained from the
Nonlinear Benchmark repository [17]. It consists of a training
set of Ntrain = 65000 samples and a test set of Ntest = 40000
samples. The training data comprises a collection of random
phase multisines with a constant amplitude in a frequency
range up to 200 Hz. The test data consists of filtered Gaussian
noise with a linearly increasing amplitude, including extrapo-
lation regions beyond the training range.
A. SS-KAN Model Setup
For state-space representation, we define the state vector
x =
x
˙xT , where x represents position and ˙x velocity.
The discrete-time SS-KAN model for the Silverbox bench-
mark utilizes a state vector of dimension nx = 2 and a
scalar input nu = 1 and output ny = 1, making it a single
input single output (SISO) test case. The KAN for the state
transition, KANf, consists of 2 layers with the hidden layer
size nl = 2, while the KAN for the output mapping, KANg,
is set to zero (KANg = 0), implying a purely linear output
mapping in this SS-KAN configuration. The data are scaled
to the range [−1, 1] to align with the grid domain of the


---

## Page 4

60
80
100
120
140
160
Time (s)
−0.2
0.0
0.2
y [V]
True Output (y) - Train
True Output (y) - Test
Error (y −ySS−KAN)
Fig. 1.
Time-Domain Performance of SS-KAN Model on Silverbox Benchmark. The blue and orange lines show the true output signal for the
(partial) training and test sets, respectively. The red line represents the simulation error (y −ySS−KAN) across both datasets. The vertical
dashed line indicates the split between the training and testing data. The horizontal dotted lines indicate the amplitude extrapolation bound where
the error increases.
B-spline basis functions used in the KAN implementation.
The linear state-space matrices (A, B, C, D) are initialized
to represent a stable, weakly damped linear system close to
an identity mapping. The regularization penalties are applied
with λL1 = λL2 = 10−4. The AdamW optimizer is run with a
learning rate set to 10−3 and a batch size Nbatch = 64 for 100
epochs (≈1 hour) in a M4 Pro (10 CPU cores at 4.5GHz).
B. Results
The RMSE on the test data obtained on the Silverbox
benchmark with the proposed SS-KAN model is compared
against several established baseline models reported in the
literature and summarized in Table I.
TABLE I
RMSE COMPARISON ON SILVERBOX TEST DATA
Model
Model Type
RMSE [V]
Train Time
BLA [16]
Linear Black-Box
0.0135
∼seconds
PNLSS [18]
Nonlinear Black-Box
0.0003
∼hours
Deep Encoder [2]
Nonlinear Black-Box
0.0014
∼days
SS-KAN
Nonlinear Grey-Box
0.0039
∼hours
The proposed SS-KAN model achieves a Test RMSE of
0.0039 V on the Silverbox benchmark. While the mature poly-
nomial nonlinear state-space (PNLSS) model demonstrates the
lowest RMSE, achieving the highest quantitative accuracy on
this benchmark, linked to the underlying system’s polynomial
nature, SS-KAN still exhibits a significantly lower RMSE –
approximately one order of magnitude – compared to the
Best Linear Approximation (BLA). Compared to the Deep
Enconder approach, SS-KAN’s RMSE is slightly higher.
However, our SS-KAN implementation, not only preserves
the original state dimensions but has fewer degrees of freedom
due to the simpler chosen architecture, training effectively in
100 epochs, requiring only around one hour of computation
time on a modern laptop. This contrasts with the reported
multi-day training for the Deep Encoder approach but is
comparable to PNLSS models which achieve high accuracy
but have training times that are dependent on specific model
complexity (e.g., polynomial degree used). While not achiev-
ing the absolute lowest RMSE, the quantitative performance
of SS-KAN in Table I demonstrates a strong balance between
accuracy and efficiency. A qualitative analysis of the time-
domain response offers further insights regarding its ability
to track the system’s dynamic behavior over time. Fig. 1
presents the time-domain absolute error between the SS-KAN
model predicted output and the measured output for part of
the training and testing datasets.
The simulation error (red line) remains small throughout the
majority of the time series, indicating accurate tracking of the
system’s dynamics by the SS-KAN model. A slight increase
in simulation error is observed within the extrapolation region
(horizontal dotted lines) in the test data. Despite this, the
overall error magnitude remains low, demonstrating good
generalization and suggesting that the nonlinear dynamics have
been effectively identified by the KAN. The low simulation
error visualized in Fig. 1 supports the quantitative RMSE
results presented in Table I, confirming the SS-KAN model’s
ability to accurately capture the nonlinear dynamics of the
Silverbox benchmark in the time domain.
After showcasing the SS-KAN’s ability to capture the sys-
tem’s dynamics over time, we now focus on the interpretability
advantage of the model. Since KANf in the SS-KAN model
(5) learns the nonlinear state updates, visualizing its output as
a function of the state and input can reveal how the model
represents the system’s nonlinear dynamics, especially since
the KAN preserves the function inputs without mixing, unlike
the decoupling approach discussed above.
For the Silverbox test case, we focus on visualizing the
univariate functions within KANf by fixing the velocity state
( ˙x) and the input (u) to their mean values and then varying
the position state (x) over the training data range. As it can be
seen in Fig. 2, this allows to isolate and visualize the direct
influence of the displacement state variable on the learned
nonlinear state updates.
The KAN function for the velocity ˙x state update (orange)
exhibits a cubic shape, indicating that SS-KAN effectively cap-
tures the cubic stiffness nonlinearity of the Duffing oscillator in
the velocity state equation. A polynomial fit shows it to be well
approximated by y ≈−996x3+12.8x2−24.6x−0.115 (dotted
black line). The dominant cubic term clearly indicates that SS-


---

## Page 5

−0.2
−0.1
0.0
0.1
0.2
x(k)
−15
−10
−5
0
5
10
15
KANf(x(k), ˙x, u) Nonlinear Output
Position (x) State Update
Velocity ( ˙x) State Update
y = −996x3 + 12.8x2 −24.6x −0.115
Fig. 2.
Learned KANf (x(k), ˙x, u) nonlinear functions by varying
the position state variable (x) for both position x (blue) and velocity ˙x
(orange) state updates. The velocity ˙x state update is well-approximated
by y ≈−996x3 + 12.8x2 −24.6x −0.115 (dotted black). The
dominant cubic term captures the Duffing oscillator’s stiffness, while the
smaller quadratic and linear terms reveal the KAN’s ability to identify
more subtle dynamic effects.
KAN effectively captures the cubic stiffness nonlinearity of the
Duffing oscillator. The presence of a quadratic term suggests
the model has identified secondary nonlinear effects, known to
be potentially present in the Silverbox benchmark’s physical
realization. The residual linear dynamics are captured by the
KAN, which is not constrained to model purely nonlinear
effects and can thus account for linear components not fully
represented by the global linear matrices. The constant term
is minimal, suggesting a minor offset. In contrast, the KAN
function for the position state update (blue) remains near-
zero, suggesting a negligible nonlinear contribution to the
position state evolution. This analysis aligns with the expected
nonlinear dynamics in (9). Moreover, the cubic shape of the
KANf velocity state update remains consistent even when the
fixed values of the velocity state ( ˙x) and input (u) for Fig.
2 are varied across their respective ranges from minimum to
maximum values observed in the training data. This highlights
that the SS-KAN model correctly identifies the position state
(x) as the dominant input variable driving the cubic nonlinear-
ity, with the other inputs playing a negligible role in shaping
this specific nonlinear behavior. In parallel, a complementary
analysis to further emphasize this point, omitted here, of fixing
both the position state x and input u, while varying the velocity
state ˙x and of fixing the both position and velocity states
x, while varying the input u, was performed. This analysis
confirms the negligible magnitude of the univariate functions
in both cases, reinforcing the interpretability strengths of the
SS-KAN approach, revealing not only the functional shape
of the dominant cubic nonlinearity but also the negligible
influence of other input variables on the state updates.
V. WIENER-HAMMERSTEIN TEST CASE
To further evaluate the generalizability of the proposed SS-
KAN model, we consider the Wiener-Hammerstein benchmark
system [19], schematically represented in Fig. 3. This bench-
mark presents a distinct identification challenge compared to
the Silverbox. Instead of a localized nonlinearity within the
state dynamics, the Wiener-Hammerstein system features a
saturation-type nonlinearity (diode-resistor), f(·) between two
third order linear dynamic blocks, G1(s) and G2(s). This
structure and the lack of direct access to internal states require
the model to infer the system’s nonlinear behavior only from
the input-output signals, respectively, u(t) and y(t), making
it a SISO system. The dataset, generated with an electronic
circuit excited by a filtered Gaussian excitation signal, consists
of Ntrain = 80000 samples for training and Ntest = 78000
samples for testing.
Fig. 3. Schematic description of the Wiener-Hammerstein system.
A. SS-KAN Model Setup
To model the Wiener-Hammerstein structure within the
SS-KAN framework, we adapt the general model equations
(5) to explicitly represent the cascaded linear-nonlinear-linear
blocks. The discrete-time state-space equations are given by:
x1(k + 1) = A1x1(k) + B1u(k)
v(k) = C1x1(k) + D1u(k)
w(k) = KAN(v(k))
x2(k + 1) = A2x2(k) + B2w(k)
y(k) = C2x2(k) + D2w(k)
(10)
where, x1(k) ∈R3 and x2(k) ∈R3 represent the state vectors
of the linear blocks. The intermediate signal v(k) represents
the output of the G1(s) linear block and is the input to the
static nonlinearity, modeled by KAN : R →R, approximating
the static diode-resistor nonlinearity. The output of the KAN
then drives the G2(s) linear block. The overall measured
system output is denoted by y(k).
The KAN architecture consists of 2 layers with a hid-
den layer size nl = 15. The dynamic grid update ap-
proach
[8]
adapts
the
spline
grids
based
on
the
in-
put activations range during training. The linear matri-
ces (A1, B1, C1, D1, A2, B2, C2, D2) are initialized using
Chebyshev filter information from the benchmark reference.
The regularization penalties are λL1 = λL2 = 10−4. The
AdamW optimizer is run with a decaying learning rate from
10−4 and a batch size Nbatch = 2048 for 500 epochs (≈6−8
hours) using the same hardware as the Silverbox test case.
B. Results
Similar to the Silverbox test case, we quantitatively evalu-
ate the performance of the SS-KAN model on the Wiener-
Hammerstein benchmark by comparing the obtained test
RMSE to literature, as summarized in Table II.
The SS-KAN model achieves a Test RMSE of 0.0114 V on
the Wiener-Hammerstein benchmark. As shown in Table II,


---

## Page 6

TABLE II
RMSE COMPARISON ON WIENER-HAMMERSTEIN TEST DATA
Model
Model Type
RMSE [V]
Train Time
BLA [20]
Linear Black-Box
0.0562
∼seconds
PNLSS [21]
Nonlinear Black-Box
0.0004
∼hours
Deep Encoder [2]
Nonlinear Black-Box
0.0002
∼days
SS-KAN
Nonlinear Grey-Box
0.0114
∼hours
while SS-KAN outperforms the BLA, its RMSE is higher than
that of the PNLSS and Deep Encoder models. This highlights a
trade-off between prioritizing SS-KAN interpretability against
achieving the lowest possible quantitative error of black-box
models. In terms of computational efficiency, SS-KAN (∼6-8
hours) is considerably faster than the Deep Encoder (∼days)
and falls within a similar order of magnitude as PNLSS models
(∼hours), whose specific training times are highly dependent
on their complexity. Fig. 4 displays the KAN learned nonlinear
function of the Wiener-Hammerstein system (10). The KAN
exhibits a linear trend with saturation. For lower input values,
the function shows a near-linear trend, corresponding to the
diode being ”off” or non-conducting, resulting in a linear
relationship (voltage divider behavior) in the electronic circuit.
Beyond a certain input threshold, the function saturates and
becomes nearly constant, representing the diode ”turning on”
and clamping the voltage to a saturation level, thus capturing
the saturation nonlinearity of the diode-resistor circuit. The
physical interpretation of the learned nonlinear function, is a
key strength of the SS-KAN approach, particularly in contrast
to black-box models where such insights are often hidden in
latent spaces or hyperparameters.
−0.5
0.0
0.5
v(k)
−0.05
0.00
0.05
0.10
0.15
w(k) = KAN(v)
Fig. 4. Learned KAN function for Wiener-Hammerstein nonlinearity. The
x-axis represents the input to the KAN, the intermediate signal v(k),
and the y-axis represents the output of the KAN, w(k). It exhibits a
linear trend with saturation, directly reflecting the behavior of the diode-
resistor nonlinearity.
VI. CONCLUSION
We introduced State-Space Kolmogorov-Arnold Networks
(SS-KAN), a new approach for interpretable nonlinear system
identification that integrates Kolmogorov-Arnold Networks
into a state-space framework. The analysis on the Silverbox
and Wiener-Hammerstein benchmarks demonstrates that SS-
KAN trades-off black-box quantitative accuracy for inter-
pretability. While SS-KAN does not reach the absolute lowest
RMSE compared to highly flexible black-box models, the
visualization of learned KAN functions within SS-KAN pro-
vides direct and physically meaningful insights into the system
nonlinearities, revealing the cubic stiffness of the Duffing
oscillator and the saturation characteristic of the Wiener-
Hammerstein system. This enhanced interpretability, achieved
without sacrificing significant accuracy, is the key contribution
of SS-KAN, offering a valuable tool for interpretable system
identification.
REFERENCES
[1] R. Pintelon and J. Schoukens, System identification: a frequency domain
approach.
John Wiley & Sons, 2012.
[2] G. Beintema, R. Toth, and M. Schoukens, “Nonlinear state-space
identification using deep encoder networks,” Proceedings of Machine
Learning Research, vol. 144, no. 2021, pp. 241–250, 2021.
[3] G. Pillonetto, A. Aravkin, D. Gedon, L. Ljung, A. H. Ribeiro, and
T. B. Sch¨on, “Deep networks for system identification: A survey,”
Automatica, vol. 171, p. 111907, 1 2025.
[4] J. Decuyper, P. Dreesen, J. Schoukens, M. C. Runacres, and K. Tiels,
“Decoupling
Multivariate
Polynomials
for
Nonlinear
State-Space
Models,” IEEE Control Systems Letters, vol. 3, no. 3, pp. 745–750, 7
2019.
[5] J. Decuyper, K. Tiels, M. Runacres, and J. Schoukens, “Retrieving
highly structured models starting from black-box nonlinear state-space
models using polynomial decoupling,” Mechanical Systems and Signal
Processing, vol. 146, p. 106966, 1 2021.
[6] Y. Liu, R. T´oth, and M. Schoukens, “Physics-Guided State-Space
Model Augmentation Using Weighted Regularized Neural Networks,”
IFAC-PapersOnLine, vol. 58, no. 15, pp. 295–300, 5 2024.
[7] S. Moradi, N. Jaensson, R. T´oth, and M. Schoukens, “Physics-Informed
Learning Using Hamiltonian Neural Networks with Output Error Noise
Models,” IFAC-PapersOnLine, vol. 56, no. 2, pp. 5152–5157, 7 2023.
[8] Z. Liu, Y. Wang, S. Vaidya, F. Ruehle, J. Halverson, M. Soljacic,
T. Y. Hou, and M. Tegmark, “KAN: Kolmogorov–arnold networks,” in
The Thirteenth International Conference on Learning Representations,
2025.
[9] B. C. Koenig, S. Kim, and S. Deng, “KAN-ODEs: Kolmogorov–Arnold
network ordinary differential equations for learning dynamical systems
and hidden physics,” Computer Methods in Applied Mechanics and
Engineering, vol. 432, no. PA, p. 117397, 12 2024.
[10] A. Pal and S. Nagarajaiah, “Kan/multkan with physics-informed
spline
fitting
(kan-pisf)
for
ordinary/partial
differential
equation
discovery of nonlinear dynamic systems,” 2024. [Online]. Available:
https://arxiv.org/abs/2411.11801
[11] K. Shukla, J. D. Toscano, Z. Wang, Z. Zou, and G. E. Karniadakis, “A
comprehensive and FAIR comparison between MLP and KAN repre-
sentations for differential equations and operator networks,” Computer
Methods in Applied Mechanics and Engineering, vol. 431, 11 2024.
[12] K. Cherifi, A. E. Messaoudi, H. Gernandt, and M. Roschkowski,
“Nonlinear port-hamiltonian system identification from input-state-
output data,” 2025. [Online]. Available: https://arxiv.org/abs/2501.06118
[13] Blealtan, “efficientkan,” 2024. [Online]. Available: https://github.com/
Blealtan/efficient-kan
[14] I. Loshchilov and F. Hutter, “Decoupled Weight Decay Regularization,”
in International Conference on Learning Representations, 2017.
[15] J. Decuyper, K. Tiels, S. Weiland, and J. Schoukens, “Decoupling
multivariate functions using a non-parametric Filtered CPD approach,”
IFAC-PapersOnLine, vol. 54, no. 7, pp. 451–456, 7 2021.
[16] A. Marconato, J. Sj¨oberg, J. Suykens, and J. Schoukens, “Identification
of the Silverbox Benchmark Using Nonlinear State-Space Models,”
IFAC Proceedings Volumes, vol. 45, no. 16, pp. 632–637, 7 2012.
[17] Schoukens,
“Nonlinear
Benchmarks,”
2024.
[Online].
Available:
https://github.com/MaartenSchoukens/nonlinear benchmarks
[18] J. Paduart, L. Lauwers, J. Swevers, K. Smolders, J. Schoukens, and
R. Pintelon, “Identification of nonlinear systems using Polynomial
Nonlinear State Space models,” Automatica, vol. 46, no. 4, pp.
647–656, 2010.


---

## Page 7

[19] J. Schoukens, J. Suykens, and L. Ljung, “Wiener-hammerstein bench-
mark,” in 15th IFAC Symposium on System Identification (SYSID 2009),
July 6-8, 2009, St. Malo, France, 2009.
[20] L. Lauwers, R. Pintelon, and J. Schoukens, “Modelling of Wiener-
Hammerstein Systems via the Best Linear Approximation,” IFAC
Proceedings Volumes, vol. 42, no. 10, pp. 1098–1103, 2009.
[21] J. Paduart, L. Lauwers, R. Pintelon, and J. Schoukens, “Identification
of a Wiener-Hammerstein system using the polynomial nonlinear state
space approach,” Control Engineering Practice, vol. 20, no. 11, pp.
1133–1139, 11 2012.
