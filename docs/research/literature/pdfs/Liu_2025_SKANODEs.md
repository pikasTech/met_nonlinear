# Liu_2025_SKANODEs

Structured Kolmogorov-Arnold Neural ODEs for
Interpretable Learning and Symbolic Discovery of
Nonlinear Dynamics
Wei Liua,c, Kiran Bacsab,c, Loon Ching Tanga, Eleni Chatzib,c,∗
aDepartment of Industrial Systems Engineering and Management, National University of
Singapore, Singapore
bDepartment of Civil, Environmental and Geomatic Engineering, ETH
Zürich, Zürich, Switzerland
cFuture Resilient Systems, Singapore-ETH Centre, Singapore
Abstract
Understanding and modeling nonlinear dynamical systems is a fundamental chal-
lenge across science and engineering. Deep learning has shown remarkable poten-
tial for capturing complex system behavior, yet achieving models that are both ac-
curate and physically interpretable remains difficult. To address this, we propose
Structured Kolmogorov-Arnold Neural ODEs (SKANODEs), a framework that
integrates structured state-space modeling with Kolmogorov-Arnold Networks
(KANs). Within a Neural ODE architecture, SKANODE employs a fully trainable
KAN as a universal function approximator to perform virtual sensing, recovering
latent states that correspond to interpretable physical quantities such as displace-
ments and velocities. Leveraging KAN’s symbolic regression capability, SKAN-
ODE then extracts compact, interpretable expressions for the system’s governing
dynamics. Experiments on two canonical nonlinear oscillators and a real-world F-
16 ground vibration dataset demonstrate that SKANODE reliably recovers phys-
ically meaningful latent displacement and velocity trajectories from acceleration
measurements, identifies the correct governing nonlinearities—including the cu-
bic stiffness in the Duffing oscillator and the nonlinear damping structure in the
Van der Pol oscillator—and reveals hysteretic signatures in the F-16 interface dy-
namics through structured latent phase portraits and an interpretable symbolic
∗Corresponding author at: Department of Civil, Environmental and Geomatic Engineering,
ETH Zürich, Zürich, Switzerland
Email address: chatzi@ibk.baug.ethz.ch (Eleni Chatzi)
arXiv:2506.18339v3  [cs.LG]  5 Mar 2026
model. Across all three cases, SKANODE provides more accurate and robust
predictions than black-box NODE baselines and classical ARX and NARX iden-
tification, while producing equation-level descriptions of the learned nonlinear
dynamics.
Keywords: Physics-encoded deep learning, Kolmogorov-Arnold Network,
symbolic equation discovery, differential equations, Neural ODE, inductive bias,
structured representation, nonlinear dynamics
1. Introduction
The rise of deep learning has significantly advanced the modeling and under-
standing of complex nonlinear dynamical systems, spanning structural mechanics,
fluid dynamics, climate modeling, and biological systems [1, 2, 3, 4]. Among the
dominant architectures, recurrent neural networks (RNNs) prove notable success
in handling sequential data and high-dimensional time series [5, 6]. However,
their discrete-time formulation makes them less suitable for capturing the inher-
ently continuous evolution of many real-world systems, especially those governed
by differential equations or with irregular temporal sampling [7].
To overcome these limitations, Neural Ordinary Differential Equations (NODEs)
have emerged as a principled framework that integrates deep learning with dif-
ferential equation modeling [8]. NODEs offer a flexible, continuous-time latent
representation that is more aligned with the physics of real systems. They have
been successfully applied across diverse application domains. Yet, despite their
expressiveness, NODEs often function as black-box models in that, while they
successfully learn efficient latent representations, these do not reveal the underly-
ing (physical) governing mechanisms [9, 10, 11]. This opacity presents a critical
barrier in scientific and engineering disciplines, where trust and understanding of
the model are just as important as predictive performance.
To promote interpretability and physical consistency, recent efforts have ex-
plored symbolic equation discovery—learning explicit mathematical expressions
from data that describe a system’s underlying dynamics [12]. A prominent method
in this respect is the Sparse Identification of Nonlinear Dynamics (SINDy) frame-
work [13], which assumes access to all physical states and their derivatives, and
identifies governing equations by performing sparse regression over a predefined
function library. SINDy and its extensions [14, 15] have been successfully applied
in low-dimensional and noise-free settings. However, they often fail in practical
2
scenarios where system states are only partially observed or measured indirectly
and where derivative estimation is highly sensitive to noise.
Other approaches, such as Physics-Informed Neural Networks (PINNs) [11]
and PDE-Net [16], embed physical knowledge into the training loss to learn gov-
erning equations, but typically require known equation structures, spatial deriva-
tives, or collocation points. Genetic programming techniques (e.g., Eureqa [12])
and neural-symbolic hybrids (e.g., [17, 18, 19]) attempt to evolve symbolic ex-
pressions through heuristic search, but often suffer from scalability issues, non-
differentiable optimization steps, or dependency on prior knowledge about the
functional form.
Most of these existing methods are built on the assumption of direct access
to physical coordinates, clean measurements, and a priori specification of basis
functions or symbolic templates. As such, their applicability is severely limited
in real-world systems where observations are noisy and indirect. This is particu-
larly true in engineering applications, where sensors provide accelerations or other
high-order measurements [20, 21]. More importantly, most symbolic discovery
pipelines are separate from the modeling framework—they operate as post-hoc
approximators, rather than as end-to-end trainable components within a system
identification architecture.
To overcome these limitations, a novel framework, termed Structured Kolmogorov-
Arnold Neural ODEs (SKANODEs), is proposed, which unifies continuous-time
neural modeling, structured physical inductive biases, and end-to-end symbolic
discovery of governing equations within a single differentiable pipeline. At the
core of SKANODE is the Kolmogorov-Arnold Network (KAN) [22], a recent
neural architecture that supports smooth transitions between black-box function
approximation and symbolic representation learning. KAN employs adaptive,
spline-based basis functions that are differentiable and expressive, while retain-
ing the structure necessary for symbolic interpretability.
In SKANODE, KAN is first used as a universal function approximator to learn
latent state dynamics that align with physically meaningful quantities such as dis-
placement and velocity. Importantly, these physical states are not assumed to be
directly observed. Instead, the model is trained solely on indirect sensor mea-
surements, such as accelerations, by embedding a structured state-space model
and observation model that enforce physically consistent relationships between
observables and latent coordinates. This enables SKANODE to perform virtual
sensing, inferring unmeasured physical quantities directly from indirect measure-
ments. Once physically meaningful latent dynamics are revealed, KAN’s sym-
bolic regression capability is activated to automatically extract explicit symbolic
3
expressions describing the underlying governing dynamics. The symbolic model
is then integrated back into the Neural ODE framework and calibrated to enhance
predictive accuracy and improve the precision of the discovered governing equa-
tions.
The resulting framework supports both prediction and equation-level interpre-
tation under partial observability. Through extensive evaluations on simulated
benchmark systems and a real-world F-16 ground vibration dataset, it is demon-
strated that SKANODE achieves strong predictive accuracy while providing trans-
parent, interpretable descriptions of nonlinear dynamics. This capability broadens
the practical use of deep learning for scientific modeling, engineering diagnostics,
and physics-based decision making.
2. Background
2.1. Physics-Encoded Machine Learning
Physics-encoded machine learning encompasses a family of approaches that
integrate physical principles directly into machine learning architectures, enhanc-
ing interpretability, generalization, and predictive performance [23, 24]. By em-
bedding physical structures within model formulations, these methods provide
powerful tools for modeling complex systems and uncovering governing dynam-
ics.
A representative example of this class involves Dynamic Bayesian Networks
(DBNs), often instantiated as dynamical variational autoencoders (VAEs) [25],
where physical knowledge is incorporated into the latent transition dynamics or
the encoder-decoder structure. By leveraging such models, prior knowledge about
system behavior can be integrated to improve both predictive accuracy and inter-
pretability [26, 27, 28, 29]. These techniques are closely related to deep state-
space models that similarly exploit structured latent representations [30, 31].
Neural Ordinary Differential Equations (NODEs) represent another important
class of physics-encoded frameworks. Unlike conventional recurrent neural net-
works [32], which operate in discrete time, NODEs model continuous-time sys-
tem dynamics by directly learning the governing differential equations. This con-
tinuous formulation avoids discretization errors inherent to conventional archi-
tectures and offers a natural framework for representing physical processes that
evolve continuously in time. Since their introduction, NODEs have been extended
to address a variety of structured and domain-specific scenarios [9, 33, 34, 35, 36],
with applications spanning structural dynamics [37], computational physics [38],
4
pharmacology [39], and chemical engineering [40]. As such an instance, physics-
informed NODEs integrate physical knowledge into the model architecture, pro-
viding a versatile framework for discrepancy modeling and structural identifi-
cation of monitored systems [41]. As the subsequent sections will detail, our
approach is built upon NODEs, leveraging its strengths in capturing complex
continuous-time dynamics.
Other related efforts include Hamiltonian-inspired frameworks that enforce
energy conservation through tailored network structures [42], often coupled with
symplectic integrators to preserve physical invariants [43, 44].
2.2. Neural Ordinary Differential Equations
The foundational work by [8] introduced Neural Ordinary Differential Equa-
tions (NODEs) as a continuous-depth counterpart to discrete neural networks,
marking a paradigm shift in how dynamic systems can be approached within the
machine learning community. Formally, let z(C) ∈R
= represent the state of a sys-
tem at time C. The dynamic evolution of the state can be described by the ODE:
3z(C)
3C
= 5 (z(C) C \)
(1)
where 5 : R
= × R →R
=
is a neural network parameterized by \, which ap-
proximates the derivative of z with respect to time. Solving this ODE yields the
continuous trajectory of z(C) from an initial state z(C
0 ) forward in time.
Training NODEs involves optimizing the parameters \ to minimize a loss
function that measures discrepancies between model predictions and observed
data. Unlike conventional neural networks, where backpropagation is applied di-
rectly through network layers, NODEs require differentiating through the entire
ODE solver, since model predictions are generated by numerically integrating the
learned differential equation. This continuous-time backpropagation is efficiently
handled using the adjoint sensitivity method [8], which computes gradients with
respect to \ without storing full trajectories, enabling memory-efficient training
over long time horizons.
Augmented NODEs.
While NODEs are well-suited for modeling continu-
ous dynamics, they are limited in expressivity due to the topological constraints
of ODE flows—specifically, their inability to represent functions involving inter-
secting trajectories or changing data topology. To address this, [45] introduced
Augmented NODEs (ANODEs), which extend the state space by incorporating
additional dimensions. By lifting the dynamics into a higher-dimensional space,
ANODEs circumvent the representational limitations of standard NODEs.
If
5
q(C) ∈R
3 denotes the original system state and a(C) ∈R
0 the augmented compo-
nents, the combined system evolves as:
3
3C
 q(C)
a(C)

= 5
 q(C)
a(C)

 C \


(2)
so that the augmented states belong to the higher dimensional space R
3+0
.
Second-order NODEs.
Following a related direction, [9] proposed Second-
Order NODEs (SONODEs), designed to model systems governed by higher-order
dynamics, common in many physical and engineering domains. SONODEs are
formulated as:
3
3C
 q(C)
a(C)

= 5
 q(C)
a(C)

 C \

=

a(C)
(q(C) a(C) C \)


(3)
The adjoint state in SONODEs also follows a second-order ODE [9], making the
adjoint sensitivity method directly applicable. While SONODE introduces an ex-
plicit derivative term a(C) into the system formulation, the learned states remain
abstract latent variables without guaranteed correspondence to physically mean-
ingful quantities such as velocity. In particular, SONODE does not impose struc-
tured observation models that reflect the physical measurement processes (e.g.,
acceleration sensors), which can limit interpretability when applied to real-world
physical systems.
2.3. Symbolic Equation Discovery and Kolmogorov–Arnold Networks
Symbolic equation discovery encompasses a family of methodologies aiming
to learn explicit, interpretable mathematical expressions governing system behav-
ior, rather than treating the model as a black box. In early approaches, genetic
programming-based methods, such as Eureqa [12], searched over expression trees
to discover functional relationships [46, 47]. Although powerful, these methods
often suffer from long runtimes, overfitting, and lack of scalability as model com-
plexity grows [48].
More recent techniques such as Sparse Identification of Nonlinear Dynamics
(SINDy) [13] and its extensions [14, 15, 49] apply sparse regression over pre-
defined function libraries to recover concise governing equations. Despite achiev-
ing strong performance in controlled scenarios, SINDy-like methods depend heav-
ily on (i) access to full state variables and their derivatives, (ii) carefully selected
candidate functions, and (iii) accurate numerical differentiation—assumptions that
are often violated in real-world, noisy or partially observed systems.
6
To improve scalability and expressiveness, differentiable symbolic regression
frameworks such as AI Feynman [50], PySR [51], and neural symbolic regression
(e.g., [19, 52, 53]) employ neural-guided search or evolutionary optimization to
discover analytic expressions. These methods offer greater automation but retain
critical limitations: they often function as post-hoc pipelines requiring clean, fully
observed data and are rarely integrated directly into architectures like NODEs
[48].
Inspired by the quest for scalable, end-to-end symbolic learning, transformer-
augmented approaches [54, 55, 56] and LLM-based frameworks (e.g., LLM-SR
[57]) have recently emerged. These methods leverage pre-trained or generative
models to propose symbolic equations, achieving better coverage and robustness.
However, they still typically rely on full-state observations and external symbolic
modules rather than end-to-end trainable ODE frameworks.
To overcome these limitations, the Kolmogorov–Arnold Network (KAN) is
adopted—a neural architecture grounded in the Kolmogorov–Arnold represen-
tation theorem and introduced in recent literature [22]. KAN replaces traditional
MLPs with networks whose activation function nodes are parameterized as learn-
able spline functions, enabling both:
• Flexible approximation: KAN functions as a universal approximator, lever-
aging spline-based units to learn expressive mappings directly from data;
• Symbolic extraction: The learned activation function at each KAN node
can be parsed into a compact symbolic form, representing distinct compu-
tational components that collectively assemble into the full expression of
the governing equation..
Recent works [22, 58] demonstrate KAN’s ability to discover explicit formu-
las, highlighting its applicability to scientific modeling. Crucially, KANs are fully
differentiable and seamlessly integrate into NODE-based architectures. Unlike
prior symbolic methods, KAN enables end-to-end symbolic equation discovery
from indirect sensor data—such as accelerations—without requiring direct access
to physical coordinates or numerical derivatives. This supports the recovery of
governing equations under partial observability, making KAN an ideal compo-
nent for our NODE-based framework.
Sparsification.
To support interpretability and generalization, KAN also in-
corporates a built-in sparsification mechanism. Unlike MLPs, which typically
impose sparsity on linear weights, KAN applies L1 regularization directly on the
7
learnable activation functions. Specifically, the L1 norm of an activation func-
tion q is defined as the average magnitude of its output over a batch of #
? inputs
{G (B) }#
?
B=1
:
|q|
1 ≡1
#
?
#
?Õ
B=1
 q(G
(B) )
 
(4)
For a KAN layer  with =
in inputs and = out outputs, we denote q 89
as the
learnable activation function connecting input 8 to output 9. The L1 norm of the
entire layer is the sum of L1 norms of all activation functions:
||
1 ≡
= in
Õ
8=1
= out
Õ
9=1
|q 89 |1 
(5)
To further enhance sparsity, KAN introduces an entropy regularization term
that encourages selective activation. The entropy of a layer is defined as:
(() ≡−
= in
Õ
8=1
= out
Õ
9=1
|q 89 |1
||
1
log
 |q 89 |1
||
1


(6)
which penalizes a uniform distribution over activation magnitudes and encourages
a sparse subset of nodes to dominate.
The total training objective combines the prediction loss with both L1 and
entropy regularization across all KAN layers indexed by ; = 0     ! −1:
 total = 
pred + _
 
‘ 1
!−1Õ
;=0
|
; |1 + ‘ 2
!−1Õ
;=0
((
; )
!

(7)
where _ controls the overall regularization strength, and ‘
1  ‘
2 (typically set to 1)
balance the two regularization components.
This sparsification framework allows KAN to learn parsimonious and inter-
pretable structures while preserving representational capacity. In this work, this
built-in regularization strategy is adopted as part of the proposed symbolic mod-
eling framework.
2.4. State-Space Representation
Transforming higher-order differential equations into a system of first-order
equations—known as the state-space representation—has become standard prac-
tice across engineering disciplines [59]. This formulation facilitates the analysis
8
and numerical solution of complex dynamical systems by enabling the use of al-
gorithms designed for first-order systems, which are generally more robust and
easier to implement [60]. Consider, for instance, a second-order nonlinear dy-
namical system expressed as:
¥G(C) = (G(C) ¤G(C) D(C))
(8)
Here,  defines the dynamics of single degree-of-freedom (DOF) system, where
G(C) ∈R
1 represents the displacement and D(C) ∈R
1 denotes the input to the
system, typically reflecting an external force. In the state-space formulation, the
primary focus is on identifying the essential variables that are crucial for com-
pletely characterizing the system’s state at any particular moment. Typically, these
variables include displacements and velocities in second-order physical systems.
Thus, the original equation (8) can be restructured into two first-order equations,
with displacements and velocities serving as the state variables, represented by:
¤z =
 ¤G
¤E

=

E
(G E D)

= 5 (z D)
(9)
where z = [G E]
) encapsulates displacements and velocities. The same principle
can be extended to higher-order dynamics by incorporating higher-order deriva-
tives into the state vector. Employing a first-order differential equation simplifies
the integration process over time, allowing for use of straightforward methods,
such as Euler or Runge-Kutta schemes. This property is further advantageous for
applying deep learning methods that are originally invented for first-order equa-
tions, such as NODEs, to learn higher-order dynamics.
An interesting observation is that the second first order equation in Eq.(9) pre-
cisely describes the generation of acceleration, with the state vector as input to the
function . This suggests that when dealing with systems that feature accelera-
tion measurements, the same function  can describe the observation generation
process. Consequently,  remains the sole function to be learned, eliminating the
need for an additional observation process model to infer the relationship between
observation and state vector. Moreover, this also enforces a physically coupled
system state and observation, given the derivative relation indicated by Eq.(9).
This implies that the two coordinates and observation adhere to the strict con-
straint of being interconnected displacement, velocity, and acceleration quantities
throughout the training process, enhancing the transparency of the entire frame-
work. Further elaboration on this formulation is provided in the subsequent sec-
tion, accompanied by a series of theoretical and experimental demonstrations to
illustrate its advantages.
9
It is reminded that we here focus on second-order dynamics because they are
prevalent in vibrational analysis, where the system states can be interpreted as
displacement and velocity. These dynamics are significant in various engineering
and physical systems, such as mechanical oscillators, electrical circuits, and struc-
tural vibrations [61]. This approach also serves as a foundation for extending the
analysis to more complex, higher-order systems. For completeness, it is noted that
the state-space form naturally applies to higher-order dynamics. Given a general
nonlinear =-order ODE of the form:
3 = G
3C
=
= 

G
3G
3C
 3 2 G
3C
2  
3 =−1 G
3C
=−1
 D


(10)
the state variable z = [I
1  I
2  I
3   I
= ] is defined as:
I 1 = G I
2 =
3G
3C
 I
3 =
3 2 G
3C
2   I
= =
3 =−1 G
3C
=−1

(11)
Then the system of state equations can be written as:
¤z =
26666666664
¤I 1
¤I 2

¤I =−1
¤I =
37777777775
=
26666666664
I 2
I 3

I =
(I
1  I
2  I
3   I
=  D)
37777777775
= 5 (z D)
(12)
3. Methodology
This section presents the proposed Structured Kolmogorov–Arnold Neural ODE
(SKANODE) framework, which enables end-to-end symbolic discovery of gov-
erning equations from partially observed nonlinear dynamical systems. The core
objective of SKANODE is to directly learn physically interpretable latent states—
such as displacements and velocities—along with explicit symbolic governing
equations, using only indirect sensor measurements such as accelerations. To
achieve this, SKANODE integrates two key components: (i) a structured state-
space formulation that incorporates physics-informed inductive biases by orga-
nizing latent states into physically meaningful coordinates, and (ii) a two-stage
learning scheme utilizing Kolmogorov–Arnold Networks (KAN) to perform both
universal function approximation and symbolic equation extraction. In the first
stage, SKANODE employs a fully trainable KAN to approximate the latent accel-
eration dynamics under the structured Neural ODE formulation. Once physically
10
Figure 1: A first-stage Kolmogorov–Arnold Network (KANapprox) is employed as a universal func-
tion approximator within the proposed structured state-space Neural ODE framework to perform
virtual sensing. Throughout training, the latent state variables and reconstructed observations are
constrained to evolve as physically interpretable quantities—specifically displacement, velocity,
and acceleration—enforced by the inductive biases encoded in the structured representation. Once
coherent latent displacement and velocity states are learned, they are passed to a second network
(KANsymbolic), which performs symbolic equation discovery and extracts a closed-form expression
for the governing dynamics. The resulting symbolic expression learned by (KANsymbolic) is then
substituted back into the Neural ODE, and the symbolic model is further trained to calibrate its
coefficients, improving both the precision of the discovered governing equation and the predictive
accuracy of system responses.
meaningful latent states are revealed, the dynamics are distilled into compact sym-
bolic forms using the spline-based representation of KAN. The discovered sym-
bolic model is then integrated back into the Neural ODE framework and calibrated
to enhance predictive accuracy and improve the precision of the discovered gov-
erning equation.
3.1. Structured State-Space Modeling
A general deep state-space model for dynamical systems can be formulated
as:
¤z(C) = 5
\ C (z(C) u(C))
(13)
y(C) = 6
\ > (z(C) u(C))
(14)
where z(C) ∈R
=
denotes the latent state, and 5 \ C , 6 \ >
are learnable functions
governing the transition and observation processes, respectively. While expres-
sive, this formulation typically yields black-box models with limited interpretabil-
ity—particularly for physical systems governed by second-order dynamics.
To address this, a structured state-space formulation is introduced, tailored for
modeling such systems using Neural ODEs. The latent state is defined as:
11
z(C) =
 x(C)
v(C)


(15)
where x(C) ∈R
3 represents displacement, and v(C) ∈R
3 represents velocity for a
3-dimensional system. The system dynamics are modeled as:
3
3C
 x(C)
v(C)

=

v(C)
 \ (x(C) v(C) u(C))


(16)
and the observation model is defined by:
y(C) = 
\ (x(C) v(C) u(C))
(17)
where u(C) ∈R
? is the external input (e.g., force), and y(C) ∈R
3 are the measured
accelerations. The same function  \ governs both the transition dynamics and the
observation process, ensuring consistency between the latent state evolution and
observable measurements. Let H denote the function space of candidate functions
for the governing dynamics, consisting of all functions  : R
3 × R
3 × R
? →R
3
parameterized by the trainable network  \ . In the SKANODE framework, H is
realized either by fully trainable Kolmogorov–Arnold Networks (KAN) during
the universal approximation stage, or by their extracted symbolic representations
after symbolic equation discovery.
This formulation implicitly encodes the second-order nature of the physical
system. The first equation, 3x
3C
= v, links displacement and velocity, while the
second equation models the acceleration dynamics through 3v
3C
= 
\ (x v u). By
structuring the observation model directly as acceleration, the framework natu-
rally reflects the physical measurement process often encountered in real-world
sensor deployments (e.g., accelerometers).
Although the model is trained solely on acceleration measurements, the struc-
tured Neural ODE formulation enforces derivative relationships that allow the
latent states to evolve consistently as physically interpretable displacement and
velocity trajectories. This tight coupling provides a strong inductive bias that en-
ables the model to recover meaningful latent dynamics even in the absence of
direct state measurements.
Training Objective.
To estimate the model parameters \, the loss function
is defined as the discrepancy between the predicted and measured accelerations:
12
L(\) =
C #Õ
C=C
0
∥^y(C) −y(C)
∥2 =
C #Õ
C=C
0
∥ \ (^x(C)
^v(C) u(C)
) −y(C)
∥2 
(18)
where (^x(C)
^v(C)) are the estimated latent states obtained by solving the Neural
ODE forward in time. The summation is performed over all available time instants
C 0  C 1      C
# , which may be non-uniformly spaced in time.
To avoid overfitting, the sparsification techniques detailed in Section 2.3 are
incorporated into the training procedure. These include L1 regularization and
entropy regularization, which control the model complexity and improve gener-
alization. Additionally, in KANsymbolic, several linear nodes are predefined for
specific terms, such as the linear components of the damping ratio and stiffness.
These linear relationships are fixed apriori, with only the affine weights remaining
trainable. Nonlinear terms, such as the cubic term in the Duffing oscillator and the
quadratic term in the Van der Pol oscillator, are fully discovered by the network,
including both the functional form and the affine parameters.
3.2. KAN-Based Two-Stage Learning
To facilitate interpretable equation discovery within the structured state-space
Neural ODE framework, the Kolmogorov–Arnold Network (KAN) is incorpo-
rated, which is a spline-based architecture capable of acting both as a universal
function approximator and a symbolic expression learner.
The SKANODE training procedure consists of two key stages:
Stage 1: Learning Structured Latent Dynamics with KANapprox. In the first stage,
the acceleration dynamics are modeled using KANapprox, a fully trainable Kol-
mogorov–Arnold Network configured as a universal approximator. This network
models the acceleration dynamics based on the structured Neural ODE formula-
tion:
3
3C
 x(C)
v(C)

=

v(C)
KANapprox(x(C) v(C) u(C))


The model is trained using acceleration-only measurements, and due to the en-
forced derivative relationships in the ODE structure, the latent variables x(C) and
v(C) evolve as displacement and velocity trajectories. The purpose of this stage
is to establish a coherent and physically meaningful latent space that reflects the
true system dynamics, even under partial observability.
13
Stage 2: Symbolic Equation Discovery and Calibration with KANsymbolic. Once
KANapprox has been trained and meaningful latent states are recovered, the learned
displacement and velocity signals are used as inputs to a second KAN, denoted
KANsymbolic. This KAN is utilized in symbolic mode, enabling automatic extrac-
tion of analytic expressions for the system’s governing dynamics.
The symbolic structure discovered by KANsymbolic is then integrated back into
the structured ODE framework, replacing KANapprox. In this phase, the symbolic
form is kept fixed and its affine coefficients are calibrated by further training the
Neural ODE with the new symbolic KANsymbolic. This calibration process ensures
that the symbolic expression remains interpretable while achieving a high-fidelity
approximation of both the system response and the true dynamics.
This two-stage learning approach—first leveraging KANapprox to recover phys-
ically meaningful latent states, and then using KANsymbolic for symbolic equation
discovery and calibration—enables SKANODE to offer a unified, interpretable,
and end-to-end differentiable framework for modeling nonlinear dynamical sys-
tems. Importantly, the entire process requires only indirect measurements, such as
accelerations, eliminating the need for full-state observations or numerical differ-
entiation, which are common limitations in existing symbolic regression methods.
3.3. Properties of SKANODE
In general deep state-space models, such as those described by Eqs. (13) and
(14), the learned latent state representation is inherently non-unique. Specifi-
cally, multiple state-space parameterizations related through admissible coordi-
nate transformations can yield identical observable predictions. This well-known
non-identifiability property (e.g., [62]) implies that conventional unconstrained
state-space models often produce latent representations that are mathematically
valid but physically uninterpretable, as the latent states may correspond to arbi-
trary linear or nonlinear transformations of the true physical coordinates.
The structured state-space formulation adopted in SKANODE directly ad-
dresses this ambiguity by embedding physically meaningful inductive biases into
both the latent state design and the observation model. By explicitly structuring
the latent space as displacement and velocity, and by defining acceleration as both
the second-order state derivative and the observed output, SKANODE tightly con-
strains the learned representation to evolve consistently with physical quantities of
interest. This design significantly reduces the solution space, mitigates coordinate
indeterminacy, and promotes the recovery of interpretable system dynamics even
when trained solely on indirect measurements such as accelerations.
14
A formal identifiability result is now stated, establishing that under certain
conditions SKANODE can recover the true governing dynamics of the system.
Proposition 1 (Identifiability of SKANODE). Consider a true second-order dy-
namical system of the form:
¥G(C) = 
∗(G(C) ¤G(C) D(C))
where  ∗denotes the true governing function. Assume:
(i) The measured observable is acceleration: H(C) = ¥G(C).
(ii) The structured state-space model given by Eq. (16) and observation model
Eq. (17) are adopted.
(iii) The function space H consists of functions  \ parameterized by the neural
network model, and the true function satisfies  ∗∈H.
(iv) The mappings C ↦→H(C) and C ↦→^H(C) both belong to a finite-dimensional
function class F of dimension 3 F .
(v) The training data contains # ¡ 3
F distinct time samples C 0      C
# .
Then, if minimizing the loss function
L(\) =
#Õ
8=0
∥ \ ( ^G(C
8 ) ^E(C
8 ) D(C
8 )) −H(C
8 )∥2
(19)
yields zero loss, i.e., L(\) = 0, it follows that
 \ ( ^G(C) ^E(C) D(C)) ≡
∗(G(C) E(C) D(C))
and the estimated latent states ^G(C) ^E(C) coincide with the true states G(C) E(C) up
to numerical integration accuracy.
This result highlights that, under appropriate structural assumptions, sufficient
data richness, and model capacity, the SKANODE framework enables the recov-
ery of both physically meaningful latent states and the true governing dynam-
ics directly from indirect measurements. The structured state-space formulation,
combined with consistency between state evolution and observation, eliminates
the need for full-state measurements or numerical differentiation, distinguishing
SKANODE from conventional black-box approaches and classical symbolic re-
gression methods.
The validity of this proposition is further demonstrated empirically through
the simulated and real-world experiments presented in Section 4.
15
4. Results
To demonstrate the enhanced interpretability and precision of the dynamics
learned by the proposed method, SKANODE is assessed through a series of ex-
amples involving both simulated and real-world nonlinear dynamical systems.
SKANODE is first applied to two classic benchmark systems broadly used in
nonlinear dynamics research: the Duffing oscillator and the Van der Pol oscil-
lator [61]. These synthetic examples illustrate SKANODE’s ability to accurately
recover physically meaningful latent states and to extract precise symbolic expres-
sions for the governing equations. The evaluation is then extended to real-world
data by analyzing ground vibration measurements from an F-16 aircraft, aiming to
model the nonlinear interactions at the interface between the aircraft’s right wing
and its payload. The results across these experiments further support the theoret-
ical properties discussed in the previous section, demonstrating the effectiveness
of SKANODE in practical applications.
For all comparative experiments, care was taken to ensure a consistent train-
ing setup across models. The only architectural difference lies in the use of the
KAN in SKANODE, whereas ANODE and SONODE adopt MLPs. In addition to
deep learning baselines, two classical input-output identification models are also
included as references: the linear AutoRegressive model with eXogenous inputs
(ARX) and its nonlinear extension (NARX). Both methods are fitted directly on
the measured acceleration signals, with the same input-output split as SKANODE,
and are evaluated on the same test horizon using identical error metrics. For ARX
and NARX, only accelerations are predicted directly; the corresponding displace-
ment and velocity trajectories are obtained by numerical time integration of the
predicted accelerations using the ground-truth initial conditions.
The architectures of the KAN modules used in SKANODE are visualized in
the corresponding experimental subsections. In our implementation, B-splines
are adopted as the spline basis, with 5th-order B-splines specifically employed.
The activation functions are modeled via B-splines with a residual connection,
which is a typical design feature of KANs. Each KAN is initialized with 6 knots
(forming 5 intervals), and the knots are adaptively updated during the training
process. For MLP-based models, a 5-layer network with 32 hidden units per layer
is adopted throughout. Identical data preprocessing, batch sizes, learning rates
schedules, and total training epochs were applied across all models to ensure a
fair comparison. The experiments are conducted on a local workstation with an
NVIDIA GeForce GTX 5080 GPU. Each experiment is run for 1,000 epochs. The
data and code used in this paper are publicly available on GitHub at https:
16
//github.com/liouvill/SKANODE.
4.1. Duffing Oscillator
A Duffing oscillator is a representative nonlinear dynamical system describing
the motion of a damped oscillator with cubic stiffness nonlinearity. The governing
equation is given by:
<¥G(C) + 2¤G(C) + :G(C) + :
3 G 3 (C) = D(C)
(20)
where < = 10 kg, 2 = 01 Ns/m, : = 15 N/m, and :
3 = 10 N/m
3 , resulting in
strongly nonlinear dynamics. The system is excited by a sinusoidal input D(C) =
sin(cC). Data are simulated at a sampling frequency of 10 Hz over 60 seconds,
with the first 20 seconds used for training and the remaining 40 seconds for testing.
Figure 2: Results on the Duffing oscillator. Top left: Symbolic governing equation discovered
by KANsymbolic, compared against the numerical baseline. The identified node receiving displace-
ment input G correctly captures the expected cubic nonlinearity. Top right: Predicted system
observables (accelerations) obtained using the SKANODE framework. SKANODE accurately re-
constructs accelerations directly from the inferred latent dynamics, without the need for a separate
observation model. Bottom: Inferred latent state variables compared to ground truth. The latent
states recovered by SKANODE correspond closely to physically meaningful displacement and
velocity trajectories, unlike ANODE and SONODE, whose latent states remain abstract represen-
tations without clear physical interpretation.
The performance of SKANODE is evaluated and compared against ANODE
and SONODE, as well as classical input-output identification baselines ARX and
17
NARX, on this system, as shown in the top-right subfigure of Figure 2. For bench-
marking the symbolic learning capability, a numerical baseline is constructed by
directly integrating the measured acceleration signals to obtain velocity and dis-
placement, which are then supplied to SINDy to extract a compact symbolic ex-
pression. The predicted trajectories from this numerical benchmark are gener-
ated by solving the discovered equations and serve to assess the accuracy of the
identified dynamics. It is important to note that this numerical baseline serves
solely as a reference for benchmarking the symbolic discovery process; it is not
a predictor by itself, as it merely integrates the measured signals without learn-
ing the underlying dynamics prior to extracting a symbolic form of the governing
equations, and its predictions completely depend on the quality of the extracted
equation. In contrast, the proposed SKANODE framework functions both as a
dynamics learner—capable of end-to-end prediction of system responses—and as
a symbolic extractor that uncovers governing equations from the learned latent
quantities.
The symbolic governing equation extracted by KANsymbolic within SKAN-
ODE is shown in Figure 2, where the identified expression accurately captures the
true system dynamics. Notably, the extracted symbolic network exhibits a distinct
cubic node connected to the displacement input G, consistent with the character-
istic cubic stiffness nonlinearity inherent in the Duffing oscillator. The predicted
accelerations and recovered latent state trajectories are also presented. While all
three models achieve reasonable accuracy in reconstructing the observable ac-
celerations, only SKANODE successfully recovers latent states that correspond
directly to physically meaningful displacement and velocity trajectories. This ad-
vantage stems from its structured state-space design and the symbolic learning
capability of the Kolmogorov–Arnold Network.
To quantitatively evaluate model performance, mean squared errors (MSE) are
computed for both predicted accelerations and inferred latent states against the
ground truth. The mean and standard deviation of MSE values over three inde-
pendent runs are reported in Table 1. All models achieve similar performance in
predicting accelerations, while SKANODE consistently shows slightly superior
accuracy. More pronounced differences appear in the recovery of latent states:
SKANODE achieves the lowest MSE and variance, indicating its ability to ex-
tract physically interpretable dynamics reliably across repeated trials. In contrast,
ANODE displays high variance and poor latent state interpretability, confirming
its tendency to learn arbitrary latent representations. SONODE produces more
stable but still non-interpretable latent trajectories, as its structure does not explic-
itly align with the true physical coordinates. ARX and NARX provide additional
18
Table 1: Model performance measured in MSE for Duffing oscillator experiments subjected to
different levels of observation noise. The observational noise is assumed to be Gaussian, randomly
sampled from the distribution N (0 f
2 ), and the value listed in the noise level column indicates
the value of standard deviation f. ANODE fails to converge even at the minimal noise level of
0.001.
Noise
level
Model
acceleration
(measurement)
displacement
velocity
Numerical
3.37×10
−3
2.69×10
−3
1.06×10
−3
ARX
1.22×10
−2
5.87
2.12×10
−2
NARX
6.82×10
−2
6.13
4.65×10
−2
0
ANODE
(3.15 ± 1.42)×10
−2
(9.95 ± 0.32)×10
−1
6.06 ± 5.17
SONODE
(1.52 ± 0.71)×10
−2
1.01 ± 0.02
9.46 ± 0.14
S3 NODE
(1.11 ± 0.51)×10
−3
(1.45 ± 0.76)×10
−3
(4.53 ± 2.78)×10
−4
SKANODE
(3.29 ± 0.00)×10
−5
(2.81 ± 0.00)×10
−4
(1.31 ± 0.00)×10
−5
Numerical
1.45×10
−3
1.12×10
−3
4.51×10
−4
ARX
1.41×10
−2
9.68
2.97×10
−2
NARX
1.57×10
−1
2.94×10
−1
2.74×10
−2
0.001
ANODE
NaN
NaN
NaN
SONODE
(5.41 ± 6.13)×10
−2
1.01 ± 0.02
9.33 ± 0.33
S3 NODE
(6.78 ± 3.43)×10
−4
(1.08 ± 0.49)×10
−3
(2.85 ± 1.84)×10
−4
SKANODE
(3.36 ± 0.00)×10
−5
(2.80 ± 0.00)×10
−4
(1.30 ± 0.00)×10
−5
Numerical
4.93×10
−3
4.48×10
−3
1.53×10
−3
ARX
1.74×10
−2
12.49
3.81×10
−2
NARX
1.82×10
−2
17.62
6.38×10
−2
0.005
ANODE
NaN
NaN
NaN
SONODE
(2.19 ± 2.86)×10
−1
(7.92 ± 3.07)×10
−1
6.89 ± 3.59
S3 NODE
(1.25 ± 0.99)×10
−3
(1.46 ± 1.07)×10
−3
(5.09 ± 4.41)×10
−4
SKANODE
(5.90 ± 0.00)×10
−5
(2.90 ± 0.00)×10
−4
(1.40 ± 0.00)×10
−5
Numerical
3.04×10
−2
1.28×10
−2
1.53×10
−2
ARX
2.34×10
−2
44.40
9.17×10
−2
NARX
1.91×10
−2
1.52×10
3
3.36
0.01
ANODE
NaN
NaN
NaN
SONODE
(1.76 ± 0.57)×10
−2
1.01 ± 0.02
9.39 ± 0.22
S3 NODE
(1.18 ± 1.00)×10
−3
(4.64 ± 1.97)×10
−4
(4.07 ± 4.62)×10
−4
SKANODE
(1.38 ± 0.00)×10
−4
(2.93 ± 0.00)×10
−4
(1.44 ± 0.00)×10
−5
19
reference points from classical system identification. While they can sometimes
yield reasonable acceleration predictions, they do not impose physically meaning-
ful state structure and therefore do not support reliable displacement and veloc-
ity recovery, especially under measurement noise. Consistent with this limitation,
ARX/NARX exhibit substantially larger errors for latent state reconstruction. Fur-
thermore, a structured state-space Neural ODE using a conventional multilayer
perceptron (MLP) in place of KAN is also evaluated—referred to as S3 NODE in
Table 1—implemented as a 5-layer MLP with 32 hidden units per layer. These
results indicate that the advantage of SKANODE stems both from its structured
inductive biases in the latent and observation models and from the symbolic dis-
covery capability of KAN, which improves interpretability and predictive accu-
racy by uncovering governing equations and enhancing the estimation of system
quantities.
Importantly, SKANODE not only improves interpretability but also contributes
to better predictive performance, underscoring the value of incorporating physics-
encoded structure and symbolic discovery capability. To further assess robustness,
Table 1 presents results under varying levels of observation noise. It is noted that
ANODE experiences severe convergence issues under noisy conditions, even at
the minimal noise level, whereas SKANODE maintains stable performance across
all scenarios.
To complement MSE and provide a more diagnostic perspective, the Structural
Similarity Index (SSIM) is also reported. SSIM captures the perceptual similarity
between predicted and ground-truth trajectories. Results across different levels of
observation noise are summarized in Table 2. The SSIM analysis reinforces the
conclusions drawn from MSE: SKANODE consistently attains highest scores (¡
09 across all states and noise levels), indicating that its predictions are not only
numerically accurate but also structurally faithful. S3 NODE also demonstrates
strong performance but remains consistently below SKANODE, while SONODE
yields moderate similarity and ANODE fails to converge under noisy conditions.
To further substantiate that the symbolic representation obtained via the pro-
posed scheme, KANsymbolic, provides operational value beyond post-hoc inter-
pretability, we introduce an additional downstream control study on the Duff-
ing oscillator. The extracted closed-form governing dynamics are first rewrit-
ten in control-affine form and then directly embedded into a classical feedback-
linearization (FBL) controller.
The regulation task is evaluated under observation noise with standard de-
viation f = 005, thereby reflecting realistic sensing conditions. Three control
strategies are compared: (i) feedback linearization using the extracted closed-form
20
Table 2: Model performance measured in SSIM for Duffing oscillator experiments subjected to
different levels of observation noise. Structural Similarity Index (SSIM) is used to quantify the
perceptual similarity between predicted and ground-truth signals. The observational noise is as-
sumed to be Gaussian, randomly sampled from the distribution N (0 f
2 ), and the value listed in
the noise level column indicates the value of standard deviation f. ANODE fails to converge even
at the minimal noise level of 0.001.
Noise
level
Model
acceleration
(measurement)
displacement
velocity
Numerical
0.9759
0.5822
0.9317
ARX
0.9294
0.0570
0.6204
NARX
0.7995
0.0388
0.4557
ANODE
0.8612 ± 0.0471
0.0335 ± 0.0010
0.0064 ± 0.0013
0
SONODE
0.9240 ± 0.0253
0.0368 ± 0.0013
0.0365 ± 0.0016
S3 NODE
0.9850 ± 0.0083
0.6990 ± 0.0847
0.9623 ± 0.0209
SKANODE
0.9997 ± 0.0000
0.8689 ± 0.0000
0.9974 ± 0.0000
Numerical
0.9873
0.7285
0.9599
ARX
0.9241
0.0328
0.5355
NARX
0.5440
0.0271
0.4681
0.001
ANODE
NaN
NaN
NaN
SONODE
0.8623 ± 0.1085
0.0366 ± 0.0009
0.0370 ± 0.0024
S3 NODE
0.9895 ± 0.0056
0.7394 ± 0.0681
0.9720 ± 0.0149
SKANODE
0.9997 ± 0.0000
0.8691 ± 0.0000
0.9974 ± 0.0000
Numerical
0.9710
0.4690
0.9173
ARX
0.9142
0.0177
0.4702
NARX
0.9132
0.0224
0.3821
0.005
ANODE
NaN
NaN
NaN
SONODE
0.6693 ± 0.3518
0.0309 ± 0.0093
0.0406 ± 0.0053
S3 NODE
0.9845 ± 0.0101
0.7171 ± 0.0969
0.9605 ± 0.0272
SKANODE
0.9995 ± 0.0000
0.8663 ± 0.0000
0.9972 ± 0.0000
Numerical
0.8667
0.2673
0.6864
ARX
0.9037
0.0308
0.2436
NARX
0.8938
0.0698
0.0616
0.01
ANODE
NaN
NaN
NaN
SONODE
0.9129 ± 0.0218
0.0374 ± 0.0015
0.0355 ± 0.0009
S3 NODE
0.9865 ± 0.0120
0.8452 ± 0.0458
0.9692 ± 0.0291
SKANODE
0.9990 ± 0.0000
0.8654 ± 0.0000
0.9971 ± 0.0000
21
Figure 3: Downstream control study on Duffing regulation, comparing PD (no inversion), feed-
back linearization using the KAN universal-approximator with Newton inversion (KAN FBL),
and feedback linearization using the extracted closed-form KAN symbolic model (KAN symbolic
FBL). Top: state regulation trajectories for displacement G (left) and velocity E (right). Bottom
left: control effort D(C). Bottom right: box plot of per-step controller computation time (log
scale). The symbolic feedback-linearization controller achieves regulation performance compara-
ble to Newton-based inversion while substantially reducing online computation cost.
symbolic model (KAN symbolic FBL), (ii) feedback linearization using the KAN
universal approximator, which requires online Newton-based inversion at each
time step (KAN FBL), and (iii) a baseline proportional–derivative (PD) controller.
This comparison allows us to isolate the practical advantage of the symbolic
model: while preserving the nonlinear dynamics learned by the universal approx-
imator, the explicit closed-form expression removes the need for iterative online
inversion and enables direct analytical controller synthesis. As shown in Figure 3,
KAN symbolic FBL and KAN FBL achieve essentially identical regulation per-
formance, attaining RMSEG
= 01068, RMSE
E
= 0141, and settling time of
157 s for both, indicating that the symbolic form precisely preserves the dynam-
ics learned by the universal approximator. Importantly, KAN symbolic FBL is
substantially faster at inference time: the mean online solve time is 149 ‘s com-
pared with 10225 ‘s for Newton inversion (approximately 74 × 10
3 speedup),
with p99 latency 175 ‘s versus 135157 ‘s. Compared with PD, KAN sym-
bolic FBL also improves regulation quality (RMSEG : 01068 vs. 01207; RMSE
E :
0141 vs. 0285; settling time: 157 s vs. 549 s). These results demonstrate that
22
KANsymbolic provides a practical downstream benefit: it preserves control perfor-
mance while dramatically reducing online computational cost, which is critical
for real-time model-based control.
Taken together, these results confirm that the superiority of SKANODE arises
from both its structured inductive biases and symbolic discovery capability, which
jointly enhance interpretability, predictive accuracy, and robustness compared to
conventional neural ODE variants.
4.2. Van der Pol Oscillator
The Van der Pol oscillator is another canonical nonlinear dynamical system
characterized by nonlinear damping, distinct from the Duffing oscillator. Its gov-
erning equation is given by:
¥G(C) + ‘(1 −G
2 ) ¤G(C) + G(C) = D(C)
(21)
where the damping parameter is set to ‘ = −1. The system is excited by a si-
nusoidal input D(C) = sin(cC). Data are generated at a sampling rate of 10 Hz
over 60 seconds, with the first 20 seconds used for training and the remaining 40
seconds for testing.
Table 3: Model performance on Van der Pol (VDP) acceleration prediction measured in MSE and
SSIM. SKANODE outperforms both deep learning and numerical baselines.
Model
MSE
SSIM
Numerical
1.0247
0.6783
ARX
3.9180
0.0307
NARX
125.8891
0.0045
ANODE
21.6218
0.1612
SONODE
3.6513
0.1502
SKANODE
0.2317
0.8764
The performance of SKANODE, ANODE, and SONODE, as well as classical
identification baselines ARX and NARX, is summarized in Table 3. The symbolic
governing equation extracted by KANsymbolic within SKANODE is shown in Fig-
ure 4, where the identified expression accurately reflects the true system dynam-
ics, outperforming the numerical baseline. The symbolic network clearly reveals
a distinct quadratic node that receives the displacement input G and multiplies
with the velocity input ¤G, consistent with the nonlinear damping characteristic
23
Figure 4: Results on the Van der Pol oscillator. NARX trajectories are omitted for visual clarity.
Top left: Symbolic governing equation discovered by KANsymbolic, compared against the numer-
ical baseline. The identified node receiving displacement input G correctly captures the expected
quadratic nonlinearity. Top right: Predicted system observables (accelerations) obtained using
the SKANODE framework. SKANODE accurately reconstructs accelerations directly from the
inferred latent dynamics, without the need for a separate observation model. Bottom: Inferred
latent state variables compared to ground truth. The latent states recovered by SKANODE cor-
respond closely to physically meaningful displacement and velocity trajectories, unlike ANODE
and SONODE, whose latent states remain abstract representations without clear physical interpre-
tation.
of the Van der Pol oscillator. The corresponding predicted accelerations and re-
covered latent states are also presented. SKANODE accurately reconstructs both
the observable accelerations and the latent states, recovering physically meaning-
ful displacement and velocity trajectories. In contrast, ANODE fails to capture
the system dynamics entirely, producing large deviations even in reconstructing
the measured accelerations. SONODE performs better than ANODE in predict-
ing the observables but still exhibits notable discrepancies and does not recover
physically interpretable latent states. Its latent representations remain abstract,
as the model lacks explicit physical structure. These results highlight the ad-
vantage of SKANODE in simultaneously achieving high predictive accuracy and
interpretable latent dynamics through its structured state-space formulation and
symbolic discovery capability.
24
4.3. F-16 Aircraft
(a) Complete aircraft structure
(b) Back connection of the right-wing-to-payload
mounting interface
Figure 5: Overview of F16 aircraft and sensor location.
The last example expands to a real-world complex system. The study pre-
sented by [63] details the experimental data collected from a full-scale F-16 air-
craft during a ground vibration test master class. The dataset is publicly available
at https://data.4tu.nl/articles/_/12954911. To simulate real-
world conditions, two dummy payloads were mounted on the wing tips of the air-
craft. The setup includes 145 acceleration sensors distributed across the aircraft,
under excitation of a shaker installed beneath the right wing to apply sine-sweep
excitations over a frequency range of 2 to 15 Hz. Data from three specific sen-
sors were made public: one at the excitation point, one on the right wing near
the nonlinear interface of interest, and one on the payload adjacent to the same
interface. These measurements were taken at a sampling frequency of 400 Hz. In
this work, the highest excitation level in this public dataset (95.6 N input ampli-
tude) is considered, under which the system nonlinearity is most pronounced. The
interfaces, consisting of T-shaped connectors on the payload side, slid through a
rail attached to the wing side, were identified by preliminary investigation as pri-
mary sources of nonlinearity in the aircraft’s structural dynamics, particularly at
the right-wing-to-payload interface.
In our setting, the acceleration measured at the excitation point serves as the
input reference for the model, while the acceleration measured on the right wing
near the nonlinear interface is used as the output signal. Data from the first 2.5
seconds of measurement were used for training, with the subsequent 10 seconds
used for testing.
The predicted vibration responses are shown in Figure 6. Trained only on
a short initial segment of the response with substantially smaller amplitude than
the subsequent prediction horizon, SKANODE yields a predicted trajectory that
matches the measured response significantly better than both the numerical base-
line and ANODE. Furthermore, the phase portraits of the inferred latent states
25
Figure 6: Results on the F-16 aircraft. Top left: Symbolic governing equation discovered by
KANsymbolic. Top right: Predicted system observables (accelerations), with the red vertical line
marking the training horizon. Bottom: Inferred latent states visualized in phase portraits. The
phase plot obtained by SKANODE exhibits distinct closed-loop patterns characteristic of hys-
teretic behavior, whereas the phase plot from ANODE yields abstract latent trajectories that lack
clear physical interpretation.
reveal that SKANODE produces a much more structured and physically mean-
ingful phase space, exhibiting characteristic loop patterns indicative of hysteretic
behavior. This observation is consistent with the findings of [64], confirming
the presence of nonlinear hysteresis at the interface. Such interpretability offers
important practical value: identifying hysteretic signatures in the dynamics can
provide insights into localized energy dissipation mechanisms and evolving struc-
tural degradation. This information may support engineers in diagnosing potential
fatigue-related issues, monitoring wear at critical joints, and informing predictive
maintenance strategies in complex aerospace structures.
In addition, a spectrogram comparison is provided to assess whether the learned
models preserve the time-frequency content of the nonlinear response. As shown
in Figure 7, SKANODE better preserves the dominant frequency ridges and their
time-varying evolution, whereas the baselines exhibit noticeable frequency smear-
ing and mismatched band intensities.
Building on these observations, SKANODE is extended by introducing an ad-
26
Figure 7: Time-frequency comparison of the F-16 acceleration response using spectrograms.
SKANODE more faithfully reproduces the dominant frequency bands and their temporal evo-
lution.
ditional latent hysteretic state 0  , leading to the following structured formulation:
¤z =
266664
¤G
¤E
¤0 
377775
=
266664
E
−:G −U0
 −2E +
1
< D
 \ (E 0
 )
377775

where  \ captures the hysteretic dynamics and U ∈[0 1] weights the relative
contributions of elastic stiffness and hysteretic components.
Through this extended structured state-space design, SKANODE is able to
identify a symbolic governing equation, as presented in Figure 6. The resulting
equation again aligns with the findings of [64], confirming that under low-level ex-
citation, the system behavior is dominated by linear stiffness with mild hysteretic
effects.
In comparison, the numerical baseline using SINDy fails to identify an equa-
tion incorporating the internal hysteretic mechanism. This is because it directly
integrates the acceleration signals and seeks an explicit symbolic relation between
acceleration, displacement, and velocity, without modeling any latent hysteresis
effects. The identified equation from the numerical baseline becomes unstable and
diverges over the prediction horizon, as the identified expression does not capture
the true underlying dynamics of the system.
We further assess the model performance using both MSE and SSIM metrics.
As reported in Table 4, the proposed SKANODE consistently outperforms the
deep learning as well as the numerical baselines in predicting accelerations. The
27
Table 4: Model performance on F-16 acceleration prediction measured in MSE and SSIM. SKAN-
ODE outperforms both deep learning and numerical baselines.
Model
MSE
SSIM
Numerical
NaN
NaN
ARX
0.5131
0.3597
NARX
0.5085
0.3409
ANODE
0.7139
0.3987
SONODE
0.5324
0.3568
SKANODE
0.0022
0.9576
Figure 8: Prediction error distribution for the F-16 acceleration response. SKANODE errors are
more tightly clustered around zero compared with the deep learning and numerical baselines,
indicating higher accuracy and more reliable predictions.
distribution of prediction errors is revealed in Figure 8, where SKANODE exhibits
errors that are more tightly clustered around zero. This indicates that SKANODE
achieves higher accuracy and provides more reliable predictions. Overall, this ex-
ample underscores the capability of SKANODE to effectively capture complex,
real-world nonlinear dynamics through the structured latent state design and in-
terpretable symbolic equation discovery.
5. Conclusion
In this work, a novel framework, termed Structured Kolmogorov–Arnold Neu-
ral ODEs (SKANODE), is proposed, which integrates structured state-space mod-
28
eling with symbolic equation discovery for learning interpretable dynamics from
partially observed nonlinear systems. By embedding a physically meaningful la-
tent state structure and leveraging the Kolmogorov–Arnold Network (KAN) as
both a universal function approximator and symbolic learner, SKANODE bridges
the gap between the expressive capacity of deep learning and the interpretabil-
ity required for scientific modeling. This approach enables the direct recovery of
physically meaningful latent states, such as displacements and velocities, while
simultaneously extracting explicit symbolic governing equations directly from in-
direct measurements like accelerations.
Comprehensive experiments on multiple nonlinear dynamical systems demon-
strate that SKANODE outperforms existing NODE variants as well as classical
system identification baselines in both predictive accuracy and interpretability.
Specifically, SKANODE recovers equation-level descriptions that match the ex-
pected nonlinear mechanisms across all considered systems. For the Duffing os-
cillator, the discovered symbolic form captures the characteristic cubic stiffness
nonlinearity, while the structured latent coordinates evolve as physically meaning-
ful displacement and velocity. For the Van der Pol oscillator, the extracted sym-
bolic structure reflects the nonlinear damping mechanism through the expected
state-dependent coupling. For the real-world F-16 ground vibration dataset, the in-
ferred latent phase portraits exhibit closed-loop hysteretic patterns, and the learned
symbolic model captures an associated internal hysteretic mechanism via the ad-
ditional latent hysteretic state. In all three cases, the proposed method yields
more accurate and robust predictions than black-box NODE baselines and clas-
sical ARX/NARX identification. These results highlight the importance of com-
bining inductive structural biases with symbolic discovery capabilities to guide
the learning process toward solutions that are physically consistent, robust, and
interpretable.
The ability to uncover governing equations from indirect observations makes
SKANODE particularly well-suited for scientific and engineering domains where
full-state measurements are often impractical, and model transparency is critical
for trustworthy decision-making. In terms of applicability, the proposed frame-
work is intended for nonlinear dynamical systems whose dominant behavior can
be reasonably captured by a smooth ODE that admits a structured state-space rep-
resentation (e.g., second-order dynamics with displacement and velocity states, or
modest extensions with additional latent internal variables). This class includes
a wide range of engineering systems in structural dynamics, vibration mitiga-
tion, aeroelasticity, and electromechanical devices. Effective use further relies on
a measurement model compatible with the imposed structure (e.g., acceleration
29
measurements consistent with second-order dynamics), on sufficient observabil-
ity of the structured latent states from the available measurements, and on suffi-
ciently informative excitation and, where relevant, known external inputs. When
the above conditions are violated—for example in systems dominated by non-
smooth switching or impacts, strong sensing distortions such as bias, drift, or col-
ored noise, unmeasured forcing, or weak excitation—the recovered latent states
and symbolic expressions may lose physical meaning or become non-unique. In
such cases, additional domain-specific constraints, hybrid formulations, or more
flexible observation models may be required.
Future work will explore the integration of stronger domain-specific priors and
constraints within the symbolic extraction process, as well as extensions that im-
prove robustness to realistic sensing imperfections. One promising extension is to
incorporate a partially decoupled observation model trained jointly with the dy-
namics to account for sensing distortions. Such modeling flexibility would allow
the framework to adapt to more challenging real-world sensing environments.
Acknowledgement
The research was conducted at the Future Resilient Systems at the Singapore-
ETH Centre, which was established collaboratively between ETH Zurich and the
National Research Foundation Singapore. This research is supported by the Na-
tional Research Foundation Singapore (NRF) under its Campus for Research Ex-
cellence and Technological Enterprise (CREATE) programme.
30
References
[1] H. Wang, T. Fu, Y. Du, W. Gao, K. Huang, Z. Liu, P. Chandak, S. Liu,
P. Van Katwyk, A. Deac, et al., Scientific discovery in the age of artificial
intelligence, Nature 620 (7972) (2023) 47–60.
[2] P. R. Vlachas, G. Arampatzis, C. Uhler, P. Koumoutsakos, Multiscale sim-
ulations of complex systems by learning their effective dynamics, Nature
Machine Intelligence 4 (4) (2022) 359–366.
[3] B. Hamzi, H. Owhadi, Learning dynamical systems from data: a simple
cross-validation perspective, part i: parametric kernel flows, Physica D:
Nonlinear Phenomena 421 (2021) 132817.
[4] Q. Li, T. Lin, Z. Shen, Deep learning via dynamical systems: An approx-
imation perspective, Journal of the European Mathematical Society 25 (5)
(2022) 1671–1709.
[5] A. Sherstinsky, Fundamentals of recurrent neural network (rnn) and long
short-term memory (lstm) network, Physica D: Nonlinear Phenomena 404
(2020) 132306.
[6] P. R. Vlachas, P. Koumoutsakos, Learning on predictions: Fusing training
and autoregressive inference for long-term spatiotemporal forecasts, Physica
D: Nonlinear Phenomena 470 (2024) 134371.
[7] J. Lee, E. De Brouwer, B. Hamzi, H. Owhadi, Learning dynamical sys-
tems from data: A simple cross-validation perspective, part iii: Irregularly-
sampled time series, Physica D: Nonlinear Phenomena 443 (2023) 133546.
[8] R. T. Chen, Y. Rubanova, J. Bettencourt, D. K. Duvenaud, Neural ordinary
differential equations, Advances in neural information processing systems
31 (2018).
[9] A. Norcliffe, C. Bodnar, B. Day, N. Simidjievski, P. Liò, On second order
behaviour in augmented neural odes, Advances in neural information pro-
cessing systems 33 (2020) 5911–5921.
[10] C. Fronk, L. Petzold, Interpretable polynomial neural ordinary differential
equations, Chaos: An Interdisciplinary Journal of Nonlinear Science 33 (4)
(2023).
31
[11] M. Raissi, P. Perdikaris, G. E. Karniadakis, Physics-informed neural net-
works: A deep learning framework for solving forward and inverse problems
involving nonlinear partial differential equations, Journal of Computational
Physics 378 (2019) 686–707.
[12] M. Schmidt, H. Lipson, Distilling free-form natural laws from experimental
data, science 324 (5923) (2009) 81–85.
[13] S. L. Brunton, J. L. Proctor, J. N. Kutz, Discovering governing equations
from data by sparse identification of nonlinear dynamical systems, Proceed-
ings of the National Academy of Sciences (2016) 201517384.
[14] S. H. Rudy, S. L. Brunton, J. L. Proctor, J. N. Kutz, Data-driven discovery
of partial differential equations, Science Advances 3 (4) (2017) e1602614.
[15] H. Schaeffer, Learning partial differential equations via data discovery and
sparse optimization, Proceedings of the Royal Society A: Mathematical,
Physical and Engineering Sciences 473 (2197) (2017) 20160446.
[16] Z. Long, Y. Lu, B. Dong, Pde-net 2.0: Learning pdes from data with a
numeric-symbolic hybrid deep network, Journal of Computational Physics
399 (2019) 108925.
[17] Y. Chen, Y. Luo, Q. Liu, H. Xu, D. Zhang, Symbolic genetic algorithm
for discovering open-form partial differential equations (sga-pde), Physical
Review Research 4 (2) (2022) 023174.
[18] F. Sun, Y. Liu, J.-X. Wang, H. Sun, Symbolic physics learner: Discovering
governing equations via monte carlo tree search, in: International Confer-
ence on Learning Representations, 2023.
URL https://openreview.net/forum?id=ZTK3SefE8_Z
[19] S. Kim, P. Y. Lu, S. Mukherjee, M. Gilbert, L. Jing, V. ˇCeperi´c, M. Soljaˇci´c,
Integration of neural network-based symbolic regression in deep learning
for scientific discovery, IEEE transactions on neural networks and learning
systems 32 (9) (2020) 4166–4177.
[20] C. P. Fritzen, Vibration-based structural health monitoring–concepts and ap-
plications, Key Engineering Materials 293 (2005) 3–20.
32
[21] B. Hamzi, H. Owhadi, Y. Kevrekidis, Learning dynamical systems from
data: A simple cross-validation perspective, part iv: case with partial ob-
servations, Physica D: Nonlinear Phenomena 454 (2023) 133853.
[22] Z. Liu, Y. Wang, S. Vaidya, F. Ruehle, J. Halverson, M. Soljaˇci´c, T. Y.
Hou, M. Tegmark, Kan:
Kolmogorov-arnold networks, arXiv preprint
arXiv:2404.19756 (2024).
[23] S. A. Faroughi, N. Pawar, C. Fernandes, M. Raissi, S. Das, N. K. Kalan-
tari, S. K. Mahjour, Physics-guided, physics-informed, and physics-encoded
neural networks in scientific computing, arXiv preprint arXiv:2211.07377
(2022).
[24] M. Haywood-Alexander, W. Liu, K. Bacsa, Z. Lai, E. Chatzi, Discussing
the spectrum of physics-enhanced machine learning; a survey on structural
mechanics applications, Data-Centric Engineering (2024).
[25] L. Girin, S. Leglaive, X. Bie, J. Diard, T. Hueber, X. Alameda-Pineda, Dy-
namical variational autoencoders: A comprehensive review, arXiv preprint
arXiv:2008.12595 (2020).
[26] W. Liu, Z. Lai, K. Bacsa, E. Chatzi, Physics-guided deep markov models for
learning nonlinear dynamical systems with uncertainty, Mechanical Systems
and Signal Processing 178 (2022) 109276.
[27] G. Revach, N. Shlezinger, X. Ni, A. L. Escoriza, R. J. Van Sloun, Y. C.
Eldar, Kalmannet: Neural network aided kalman filtering for partially known
dynamics, IEEE Transactions on Signal Processing 70 (2022) 1532–1547.
[28] W. Liu, Z. Lai, K. Bacsa, E. Chatzi, Neural extended kalman filters for learn-
ing and predicting dynamics of structural systems, Structural Health Moni-
toring 23 (2) (2024) 1037–1052.
[29] N. Takeishi, A. Kalousis, Physics-integrated variational autoencoders for ro-
bust and interpretable generative modeling, Advances in Neural Information
Processing Systems 34 (2021) 14809–14821.
[30] S. S. Rangapuram, M. W. Seeger, J. Gasthaus, L. Stella, Y. Wang,
T. Januschowski, Deep state space models for time series forecasting, Ad-
vances in neural information processing systems 31 (2018) 7785–7794.
33
[31] L. Li, J. Yan, X. Yang, Y. Jin, Learning interpretable deep state space model
for probabilistic time series forecasting, in: Proceedings of the 28th Interna-
tional Joint Conference on Artificial Intelligence, 2019, pp. 2901–2908.
[32] S. Hochreiter, J. Schmidhuber, Long short-term memory, Neural computa-
tion 9 (8) (1997) 1735–1780.
[33] A. Norcliffe, C. Bodnar, B. Day, J. Moss, P. Liò, Neural ode processes, in:
International Conference on Learning Representations, 2021.
URL https://openreview.net/forum?id=27acGyyI1BY
[34] X. Liu, T. Xiao, S. Si, Q. Cao, S. Kumar, C.-J. Hsieh, Neural sde: Stabilizing
neural ode networks with stochastic noise, arXiv preprint arXiv:1906.02355
(2019).
[35] H. Xia, V. Suliafu, H. Ji, T. Nguyen, A. Bertozzi, S. Osher, B. Wang, Heavy
ball neural ordinary differential equations, Advances in Neural Information
Processing Systems 34 (2021) 18646–18659.
[36] C. Salvi,
M. Lemercier,
A. Gerasimovics,
Neural stochastic pdes:
Resolution-invariant learning of continuous spatiotemporal dynamics, Ad-
vances in Neural Information Processing Systems 35 (2022) 1333–1344.
[37] D. A. Najera-Flores, M. D. Todd, A structure-preserving neural differential
operator with embedded hamiltonian constraints for modeling structural dy-
namics, Computational Mechanics 72 (2) (2023) 241–252.
[38] K. Lee, E. J. Parish, Parameterized neural ordinary differential equations:
Applications to computational physics problems, Proceedings of the Royal
Society A 477 (2253) (2021) 20210162.
[39] Z. Qian, W. Zame, L. Fleuren, P. Elbers, M. van der Schaar, Integrating ex-
pert odes into neural odes: pharmacology and disease progression, Advances
in Neural Information Processing Systems 34 (2021) 11364–11383.
[40] O. Owoyele, P. Pal, Chemnode: A neural ordinary differential equations
framework for efficient chemical kinetic solvers, Energy and AI 7 (2022)
100118.
[41] Z. Lai, C. Mylonas, S. Nagarajaiah, E. Chatzi, Structural identification with
physics-informed neural ordinary differential equations, Journal of Sound
and Vibration 508 (2021) 116196.
34
[42] S. Greydanus, M. Dzamba, J. Yosinski, Hamiltonian neural networks, Ad-
vances in neural information processing systems 32 (2019).
[43] S. Saemundsson, A. Terenin, K. Hofmann, M. Deisenroth, Variational in-
tegrator networks for physically structured embeddings, in: International
Conference on Artificial Intelligence and Statistics, PMLR, 2020, pp. 3078–
3087.
[44] K. Bacsa, Z. Lai, W. Liu, M. Todd, E. Chatzi, Symplectic encoders
for physics-constrained variational dynamics inference, Scientific Reports
13 (1) (2023) 2643.
[45] E. Dupont, A. Doucet, Y. W. Teh, Augmented neural odes, in: Advances in
Neural Information Processing Systems, 2019, pp. 3134–3144.
[46] J. Bongard, H. Lipson, Automated reverse engineering of nonlinear dynam-
ical systems, Proceedings of the National Academy of Sciences 104 (24)
(2007) 9943–9948.
[47] I. G. Tsoulos, I. E. Lagaris, Solving differential equations with genetic pro-
gramming, Genetic Programming and Evolvable Machines 7 (2006) 33–54.
[48] K. Yu, E. Chatzi, G. Kissas, Grammar-based ordinary differential equation
discovery, Mechanical Systems and Signal Processing 240 (2025) 113395.
doi:https://doi.org/10.1016/j.ymssp.2025.113395.
URL https://www.sciencedirect.com/science/article/
pii/S0888327025010969
[49] A. Pal, S. Bhowmick, S. Nagarajaiah, Physics-informed ai and ml-based
sparse system identification algorithm for discovery of pde’s representing
nonlinear dynamic systems, Mechanical Systems and Signal Processing 238
(2025) 113238.
[50] S.-M. Udrescu, M. Tegmark, Ai feynman: A physics-inspired method for
symbolic regression, Science advances 6 (16) (2020) eaay2631.
[51] M. Cranmer, Interpretable machine learning for science with pysr and sym-
bolicregression. jl, arXiv preprint arXiv:2305.01582 (2023).
[52] G. Lample, F. Charton, Deep learning for symbolic mathematics, arXiv
preprint arXiv:1912.01412 (2019).
35
[53] P.-A. Kamienny, G. Lample, S. Lamprier, M. Virgolin, Deep generative sym-
bolic regression with monte-carlo-tree-search, in: International Conference
on Machine Learning, PMLR, 2023, pp. 15655–15668.
[54] L. Biggio, T. Bendinelli, A. Neitz, A. Lucchi, G. Parascandolo, Neural sym-
bolic regression that scales, in: International Conference on Machine Learn-
ing, Pmlr, 2021, pp. 936–945.
[55] P.-A. Kamienny, S. d’Ascoli, G. Lample, F. Charton, End-to-end symbolic
regression with transformers, Advances in Neural Information Processing
Systems 35 (2022) 10269–10281.
[56] S. Becker, M. Klein, A. Neitz, G. Parascandolo, N. Kilbertus, Predicting or-
dinary differential equations with transformers, in: International conference
on machine learning, PMLR, 2023, pp. 1978–2002.
[57] P. Shojaee, K. Meidani, S. Gupta, A. B. Farimani, C. K. Reddy, Llm-sr:
Scientific equation discovery via programming with large language models,
in: International Conference on Learning Representations, 2025.
URL https://openreview.net/forum?id=m2nmp8P5in
[58] Z. Liu, P. Ma, Y. Wang, W. Matusik, M. Tegmark, Kan 2.0: Kolmogorov-
arnold networks meet science, arXiv preprint arXiv:2408.10205 (2024).
[59] T. Kailath, Linear systems, Vol. 156, Prentice-Hall Englewood Cliffs, NJ,
1980.
[60] S. Wang, Q. Li, StableSSM: Alleviating the curse of memory in state-space
models through stable reparameterization, in: Forty-first International Con-
ference on Machine Learning, 2024.
URL https://openreview.net/forum?id=nMN5hNZMQK
[61] J. M. T. Thompson, H. B. Stewart, Nonlinear dynamics and chaos, John
Wiley & Sons, 2002.
[62] D. Simon, Optimal state estimation: Kalman, h∞, and nonlinear approaches.
hoboken, NJ: John Wiley and Sons, Jg 10 (2006) 0470045345.
[63] J.-P. Noël, M. Schoukens, F-16 aircraft benchmark based on ground vibra-
tion test data, in: 2017 Workshop on Nonlinear System Identification Bench-
marks, Vol. 22, 2017, p. 30.
36
[64] T. Dossogne, C. Grappasonni, G. Kerschen, B. Peeters, J. Debille, M. Vaes,
J. Schoukens, Nonlinear ground vibration identification of an f-16 aircraft-
part ii: Understanding nonlinear behaviour in aerospace structures using
sine-sweep testing, in: International Forum on Aeroelasticity and Structural
Dynamics, IFASD 2015, 2015.
37
Appendix A. SKANODE Recovers True System Dynamics
In this section, it is theoretically demonstrated that, under certain conditions
and assuming idealized loss minimization in the theoretical setting, the proposed
Structured Kolmogorov–Arnold Neural ODE (SKANODE) framework is capable
of exactly recovering the true governing dynamics.
Proposition 1 (Identifiability of SKANODE). Consider a true second-order dy-
namical system of the form:
¥G(C) = 
∗(G(C) ¤G(C) D(C))
where  ∗denotes the true governing function. Assume:
(i) The measured observable is acceleration: H(C) = ¥G(C).
(ii) The structured state-space model given by Eq. (16) and observation model
Eq. (17) are adopted.
(iii) The function space H consists of functions  \ parameterized by the neural
network model, and the true function satisfies  ∗∈H.
(iv) The mappings C ↦→H(C) and C ↦→^H(C) both belong to a finite-dimensional
function class F of dimension 3 F .
(v) The training data contains # ¡ 3
F distinct time samples C 0      C
# .
Then, if minimizing the loss function
L(\) =
#Õ
8=0
∥ \ ( ^G(C
8 ) ^E(C
8 ) D(C
8 )) −H(C
8 )∥2
(A.1)
yields zero loss, i.e., L(\) = 0, it follows that
 \ ( ^G(C) ^E(C) D(C)) ≡
∗(G(C) E(C) D(C))
and the estimated latent states ^G(C) ^E(C) coincide with the true states G(C) E(C) up
to numerical integration accuracy.
38
Proof. The true system evolves according to:
3
3C
 G(C)
E(C)

=

E(C)
 ∗(G(C) E(C) D(C))


H(C) = 
∗(G(C) E(C) D(C))
The SKANODE model estimates:
3
3C
 ^G(C)
^E(C)

=

^E(C)
 \ ( ^G(C) ^E(C) D(C))


^H(C) = 
\ ( ^G(C) ^E(C) D(C))
By minimizing the loss to zero, we have ^H(C
8 ) = H(C
8 ) at all training points C 8 .
Since both H(C) and ^H(C) belong to the finite-dimensional function class F , and
we have # ¡ 3
F distinct sampled time points, it follows directly by the definition
of F that:
^H(C) ≡H(C)
∀C
Therefore, we have
 \ ( ^G(C) ^E(C) D(C)) = 
∗(G(C) E(C) D(C))
∀C
Both systems now evolve under identical ODEs:
3
3C
 ^G(C)
^E(C)

=
3
3C
 G(C)
E(C)


with identical initial conditions ^G(C
0 ) = G(C
0 ), ^E(C
0 ) = E(C
0 ). By uniqueness
of solutions to ODE initial value problems (Picard–Lindelöf theorem), it follows
that:
^G(C) ≡G(C)
^E(C) ≡E(C)
∀C
Thus, both the governing function and the latent states are exactly recovered.

39
