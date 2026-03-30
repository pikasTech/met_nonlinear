# Page 1

1
Recurrent Equilibrium Networks:
Flexible Dynamic Models with Guaranteed Stability
and Robustness
Max Revay⋆, Ruigang Wang⋆, Ian R. Manchester
Abstract—This paper introduces recurrent equilibrium net- In this paper, we introduce a new model structure: the
works(RENs),anewclassofnonlineardynamicalmodelsforap- recurrent equilibrium network (REN).
plicationsinmachinelearning,systemidentificationandcontrol.
1) RENs are highly flexible and include many established
The new model class admits “built in” behavioural guarantees
of stability and robustness. All models in the proposed class are models as special cases, including DNNs, RNNs, echo-
contracting – a strong form of nonlinear stability – and models state networks and stable linear dynamical systems.
cansatisfyprescribedincrementalintegralquadraticconstraints 2) RENs admit built in behavioural guarantees such as
(IQC), including Lipschitz bounds and incremental passivity.
stability, incremental gain, passivity, or other properties
RENs are otherwise very flexible: they can represent all stable
that are relevant to safety critical systems, and are
linearsystems,allpreviously-knownsetsofcontractingrecurrent
neural networks and echo state networks, all deep feedforward compatible with most existing frameworks for nonlin-
neuralnetworks,andallstableWiener/Hammersteinmodels,and ear/robust stability analysis.
can approximate all fading-memory and contracting nonlinear 3) RENsareeasytouseastheypermitadirect(smooth,un-
systems. RENs are parameterized directly by a vector in RN,
constrained)parameterizationenablinglearningoflarge-
i.e. stability and robustness are ensured without parameter
scale models via generic unconstrained optimization
constraints, which simplifies learning since generic methods for
unconstrained optimization such as stochastic gradient descent algorithms and off-the-shelf automatic-differentiation
and its variants can be used. The performance and robustness tools.
of the new model set is evaluated on benchmark nonlinear
A REN is a dynamical model incorporating an equilibrium
system identification problems, and the paper also presents
applicationsindata-drivennonlinearobserverdesignandcontrol network [10]–[12] , a.k.a. implicit network [13]. Equilibrium
with stability guarantees. networks are “implicit depth” neural networks, in which the
output is generated as the zero set of an equation relating
inputs and outputs, which can be viewed as the equilibrium
I. INTRODUCTION of a “fast” dynamical system. This implicit structure brings
the remarkable flexibility alluded to above, but also raises the
Deep neural networks (DNNs), recurrent neural networks
question of existence and uniqueness of solutions, i.e. well-
(RNNs), and related models have revolutionised many fields
posedness. A benefit of our parameterization approach is that
of engineering and computer science [1]. Their remarkable
the resulting RENs are always well-posed.
flexibility, accuracy, and scalability has led to renewed inter-
RENs can be constructed to be contracting [14], a strong
est in neural networks in many domains including learning-
form of nonlinear stability, and/or to satisfy robustness guar-
based/data-driven methods in control, identification, and re-
anteesintheformofincrementalintegralquadraticconstraints
lated areas (see e.g. [2]–[4] and references therein).
(IQCs) [15]. This class of constraints includes user-definable
However, it has been observed that neural networks can
boundsonthenetwork’sLipschitzconstant(incrementalgain),
be very sensitive to small changes in inputs [5], and this
which can be used to trade off performance vs sensitivity to
sensitivitycanextendtocontrolpolicies[6].Furthermore,their
adversarial perturbations. The IQC framework also encom-
scale and complexity makes them difficult to certify for use
passes many commonly used tools for certifying stability and
insafety-criticalsystems,anditcanbedifficulttoincorporate
performance of system interconnections, including passivity
priorphysicalknowledgeintoaneuralnetworkmodel,e.g.that
methods in robotics [16], networked-system analysis via dis-
a model should be stable. The most accurate current methods
sipation inequalities [17], µ analysis [18], and standard tools
for certifying stability and robustness of DNNs and RNNs
for analysis of nonlinear control systems [19].
are based on mixed-integer programming [7] and semidefinite
programming [8], [9] both of which face challenges when
scaling to large networks. A. Learning and Identification of Stable Models
The problem of learning dynamical systems with stability
⋆M.RevayandR.Wangmadeequalcontributiontothispaper.Thiswork
wassupportedbytheAustralianResearchCouncil,grantDP190102963. guarantees appears frequently in system identification. When
The authors are with the Australian Centre for Robotics and learning models with feedback it is not uncommon for the
School of Aerospace, Mechanical and Mechatronic Engineering,
model to be unstable even if the data-generating system is
The University of Sydney, Sydney, NSW 2006, Australia (e-mail:
ian.manchester@sydney.edu.au). stable.Forlinearmodels,variousmethodshavebeenproposed
3202
luJ
21
]GL.sc[
3v24950.4012:viXra

---

# Page 2

2
to guarantee stability via regularization and constrained opti- potential applications in control and related fields, some of
mization [20]–[24]. For nonlinear models, there has also been which we explore in this paper.
a substantial volume of research on stability guarantees, e.g. In robotics, passivity constraints are widely used to ensure
for polynomial models [25]–[28], Gaussian mixture models stable interactions e.g. in teleoperation, vision-based control,
[29], and recurrent neural networks [30]–[34]. However, the and multi-robot control [16] and interaction with physical
problemissubstantiallymorecomplexthanthelinearcasedue environments (e.g. [48], [49]). More generally, methods based
to the many possible nonlinear model structures and differing onquadraticdissipativityandIQCsareapowerfultoolforthe
definitions of nonlinear stability. Contraction is a strong form designofcomplexinterconnectedcyber-physicalsystems[15],
of nonlinear stability [14] which is particularly well-suited [17].Withintheseframeworks,theproposedRENarchitecture
to problems in learning and system identification since it can be used to learn subsystems that specify prescribed or
guarantees stability of all solutions of the model, irrespective parameterized IQCs, and which therefore cannot destabilize
of inputs or initial conditions. This is important in learning the system when interconnected with other components.
since the purpose of a model is usually to simulate responses A classical problem in control theory is observer design:
to previously unseen inputs. The works [25]–[28], [30], [33], to construct a dynamical system that estimates the internal
[34] are guaranteed to find contracting models. (latent) state of another system from partial measurements.
A recent approach is to search for a contracting dynamical
system that can reproduce true system trajectories [50], [51].
B. Lipschitz Bounds for Neural Network Robustness
In Section VIII, we formulate the observer design problem as
Model robustness can be characterized in terms of sensi- a supervised learning problem over a set of contracting non-
tivity to small perturbations in the input. It has recently been linear systems, and demonstrate the approach on an unstable
shown that recurrent neural network models can be extremely nonlinear reaction diffusion PDE.
fragile [35], i.e. small changes to the input produce dramatic In optimization of linear feedback controllers, the classi-
changes in the output. cal Youla-Kucera (or Q) parameterization provides a convex
Formally, sensitivity and robustness can be quantified via formulation for searching over all stabilizing controllers via
Lipschitz bounds on the input-output mapping associated with a “free” stable linear system parameter [18], [52], [53]. This
the model. In machine learning, Lipschitz constants are used approach can be extended to nonlinear systems [19], [54] in
in the proofs of generalization bounds [36], analysis of ex- whichthe“freeparameter”isastablenonlinearmodel.InSec.
pressiveness [37] and guarantees of robustness to adversarial IX,weapplythisideatooptimizenonlinearfeedbackpolicies
attacks [38], [39]. There is also ample empirical evidence to for constrained linear control.
suggest that Lipschitz regularity (and model stability, where
applicable) improves generalization in machine learning [40]
D. Convex and Direct Parameterizations
and system identification [33]. In reinforcement learning [41],
it has recently been found that the Lipschitz constant of The central contributions of this paper are new model pa-
policies has a strong effect on their robustness to adversarial rameterizations which have behavioral constraints, and which
attack [42]. In [43] it was shown that privacy preservation are amenable to optimization. The first set of parameteriza-
in dynamic feedback policies can be represented as an ℓ2 tions we introduce includes (convex) linear matrix inequality
Lipschitz bound. (LMI) constraints, building upon [25], [34]. LMI constraints
Unfortunately, even calculation of the Lipschitz constant can be incorporated into a learning process either through
of feedforward (static) neural networks is NP-hard [44]. introductionofbarrierfunctionsorprojections.However,they
The tightest tractable bounds known to date use incremental are computationally challenging for large-scale models. For
quadratic constraints to construct a behavioural description example, a path-following interior point method, as proposed
of the neural network activation functions [45], but using in [34] generally requires computing gradients of barrier
these results in training is complicated by the fact that the functions,linesearchprocedures,andacombinationof“inner”
constraints are not jointly convex in model parameters and and “outer” iterations as the barrier parameter changes.
constraint multipliers. In [46], Lipschitz bounded feedforward Toaddressthischallenge,inthispaperwealsointroducedi-
models were trained using the Alternating Direction Method rectparameterizationsofcontractingandrobustRENs.Thatis,
of Multipliers, and in [33], an a custom interior point solver weconstructasmoothmappingfromRN tothemodelweights
were used. However, the requirements to satisfy linear matrix such that every model in the image of this mapping satisfies
inequalities at each iteration make these methods difficult to the desired behavioural constraints. This can be thought of as
scale.In[47],theauthorsintroducedadirectparameterization constructing a (redundant) intrinsic coordinate system on the
of feedforward neural networks satisfying the bounds of [45], constraint manifold. The construction is related to the method
using techniques related to the present paper. of [55] for semidefinite programming, in which a positive-
semidefinite matrix is parameterized by square-root factors.
Our parameterization differs in that it avoids introducing any
C. Applications of Contracting and Robust Models in Data-
nonlinear equality constraints.
Driven Control and Estimation
Asmentionedabove,directparameterizationallowsgeneric
An ability to learn flexible dynamical models with contrac- optimization methods such as stochastic gradient descent
tion, robustness, and other behavioural constraints has many (SGD) and ADAM [56] to be applied. Another advantage

---

# Page 3

3
is that it allows easy random sampling of nonlinear models are flexible enough to make full use of available data, and yet
withtherequiredstabilityandrobustnessconstraintsbysimply guaranteed to be well-behaved in some sense.
sampling a random vector in RN. This allows straightforward Given a dataset z˜, we consider the problem of learning a
generation of echo state networks with prescribed behavioral nonlinear state-space dynamical model of the form
properties, i.e. large-scale recurrent networks with fixed dy-
x =f(x ,u ,θ), y =g(x ,u ,θ) (1)
namics and learnable output maps (see, e.g., [57], [58] and t+1 t t t t t
references therein). that minimizes some loss or cost function depending (in part)
on the data, i.e. to solve a problem of the form
E. Structure of this Paper
min (z˜,θ). (2)
θ∈Θ L
The paper structure is as follows:
• Sections II - VI discuss the proposed model class and In the above, x t ∈ Rn,u t ∈ Rm,y t ∈ Rp,θ ∈ Θ ⊆ RN are
itsproperties.SectionIIformulatestheproblemoflearn- the model state, input, output and parameters, respectively.
ing stable and robust dynamical models; in Section III Here f : Rn Rm Θ Rn and g : Rn Rm Θ Rp
× × → × × →
we present the REN model class; in Section IV we are piecewise continuously differentiable functions.
Example 1: In the context of system identification we may
present convex parameterizations of stable and robust
have z˜=(y˜,u˜) consisting of finite sequences of input-output
RENs; in Section V we present direct (unconstrained)
measurements, and aim to minimize simulation error:
parameterisations of RENs; in Section VI we discuss the
expressivityoftheRENmodelclass,showingitincludes (z˜,θ)= y y˜ 2 (3)
many commonly-used models as special cases. L ∥ − ∥T
• Sections VII - IX present applications of learning sta- where y = R a (u˜) is the output sequence generated by the
ble/robust nonlinear models. Section VII presents appli- nonlinear dynamical model (1) with initial condition x 0 = a
cations to system identification; Section VIII presents and inputs u t = u˜ t . Here the initial condition a may be part
applications to nonlinear observer design; Section IX of the data z˜, or considered a learnable parameter in θ.
presents applications to nonlinear feedback design for The main contributions of this paper are model parameter-
linear systems. Associated Julia code is available in the izations, and we make the following definitions:
package RobustNeuralNetworks.jl [59]. Definition 1: A model parameterization (1) is called a con-
vexparameterizationifΘ RN isaconvexset.Furthermore,
A preliminary conference version was presented in [60]. The it is called a direct parame ⊆ terization if Θ=RN.
present paper expands the class of robustness properties to
Direct parameterizations are useful for learning large-scale
more general dissipativity conditions, removes the restriction
models since many scalable unconstrained optimization meth-
that the model has zero direct-feedthrough, introduces the
ods (e.g. stochastic gradient descent) can be applied to solve
acyclic REN, adds proofs of all theoretical results, adds
(2). We will parameterize stable nonlinear models, and the
new material on echo state networks, and includes novel
particular form of stability we use is the following:
approaches to nonlinear observer design and optimization of
Definition2:Amodel(1)issaidtobecontractingwithrate
feedback controllers enabled by the REN.
α (0,1) if for any two initial conditions a,b Rn, given
∈ ∈
the same input sequence u ℓm, the state sequences xa and
F. Notation xb satisfy ∈ 2e
The set of sequences x : N Rn is denoted by ℓn . xa xb Kαt a b (4)
→ 2e | t − t|≤ | − |
Superscript n is omitted when it is clear from the context.
For x ℓn , x Rn is the value of the sequence x at for some K >0.
time t ∈ N 2e . Th t e ∈ subset ℓ ℓ consists of all square- Roughly speaking, contracting models forget their initial
2 2e
∈ ⊂ conditions exponentially. Beyond stability, we will also con-
summable sequences, i.e., x ℓ if and only if the ℓ
2 2
norm x :=
(cid:112)(cid:80)∞
x 2 i
∈
s finite, where () denotes
sider robustness constraints of the following form:
∥ ∥ t=0| t | | · | Definition 3: A model (1) is said to satisfy the incremen-
Euclidean norm. Given a sequence x ℓ , the ℓ norm
∈(cid:113) 2e 2 tal integral quadratic constraint (IQC) defined by (Q,S,R)
of its truncation over [0,T] is ∥ x ∥ T := (cid:80)T t=0| x t | 2. For where 0 Q Rp×p, S Rm×p, and R=R⊤ Rm×m, if
⟨ t p w x o , o si y t ⟩ i s v T e e q : u d = e e n fi (cid:80) c n e i T t s t = e x 0 an , x y d ⊤ t p y ∈ o t . si ℓ W t n 2 iv e e e , u s t s e h e m e A i i - n d ≻ n e e fi 0 r ni a p te n ro d m d A u at c r ⪰ t ix o , 0 v r e e to r sp d [ e 0 e c , n t T i o v t ] e e ly i a s . f i a n o n p r d u a t y ll b se p = q a ⪰ u i R r e s n o c ( e f v ∈ s ) so u s l a , u t v t i i s o ∈ f n y s ℓm 2 w e ∈ , it t h he in o it u i t a p l u c t o s n e d q i u ti e o n n c s es a, y ∈ b a ∈ = R R n a a ( n u d )
b
Wedenotethesetofpositive-definitediagonalmatricesbyD .
+
Given a positive-definite matrix P we use to denote the (cid:88) T (cid:20) ya yb(cid:21)⊤(cid:20) Q S⊤(cid:21)(cid:20) ya yb(cid:21)
|·| P t − t t − t d(a,b), T (5)
weighted Euclidean norm, i.e. | a | P =√a⊤Pa. t=0 u t − v t S R u t − v t ≥− ∀
for some function d(a,b) 0 with d(a,a)=0.
II. LEARNINGSTABLEANDROBUSTMODELS ≥
Important special cases of incremental IQCs include:
This paper is concerned with learning of nonlinear dynam-
• Q = 1I,R = γI,S = 0: the model satisfies an ℓ2
ical models, i.e. finding a particular model within a set of −γ
Lipschitz bound, a.k.a. incremental ℓ2-gain bound, of γ:
candidates using some data relevant to the problem at hand.
Thecentralaimofthispaperistoconstructmodelclassesthat R (u) R (v) γ u v , .
a a T T
∥ − ∥ ≤ ∥ − ∥

---

# Page 4

4
for all u,v ℓm, T N.
∈ 2e ∈ σ
• Q = 0,R = 2νI,S = I where ν 0: the model is
− ≥
monotone on ℓ2 (strongly if ν >0), a.k.a. incrementally v w
passive (incrementally strictly input passive, resp.):
R (u) R (v),u–v ν u v 2 G
⟨ a − a ⟩ T ≥ ∥ − ∥T y u
for all u,v ℓm and T N.
∈ 2e ∈ Fig. 1: REN as a feedback interconnection of a linear system
• Q = 2ρI,R = 0,S = I where ρ > 0: the model is
− G and a nonlinear activation σ.
incrementally strictly output passive:
R (u) R (v),u–v ρ R (u) R (v) 2
⟨ a − a ⟩ T ≥ ∥ a − a ∥T ItwillbeconvenienttorepresenttheRENmodelasafeed-
forallu,v ℓm andT N.Ifρ=1themodelisfirmly back interconnection of a linear system G and a memoryless
nonexpansiv ∈ e o 2 n e ℓ2. ∈ nonlinear operator σ, as depicted in Fig. 1:
In other contexts, Q,S,R may themselves be decision vari- W b
ables in a separate optimization problem to ensure stability of  x t+1  (cid:122)  A B (cid:125) 1 (cid:124) B 2  (cid:123)  x t   (cid:122) b (cid:125) x (cid:124)  (cid:123)
interconnected systems (see, e.g., [15], [17] . 

v
t


= C
1
D
11
D
12
w t+b v, (9)
Remark 1: Given a model class guaranteeing incremental y t C 2 D 21 D 22 u t b y
IQCdefinedbyconstantmatricesQ,S,R,itisstraightforward
to construct models satisfying frequency-weighted IQCs. E.g. w t =σ(v t ):= (cid:2) σ(v t 1) σ(v t 2) ··· σ(v t q) (cid:3)⊤ , (10)
by constructing a model R that is contracting and satisfies an where v ,w Rq are the input and output of activation
ℓ2 Lipschitzbound,andchoosingstablelinearfiltersW ,W , t t ∈
1 2 functionsrespectively.Thelearnableparameterisθ := W,b
with W 1 having a stable inverse, the new model where W R(n+q+p)×(n+q+m) is the weight matri { x, and }
b Rn+q+p ∈ the bias vector. Typically the activation function
y =W a (u)=W 1 −1R a (W 2 u) σ ∈ is fixed, although this is not essential.
is contracting and satisfies the frequency-weighted bound
A. Flexibility of Equilibrium Networks
W (W (u) W (v)) γ W (u v) .
∥ 1 a − a ∥ T ≤ ∥ 2 − ∥ T In [34] we introduced and studied a class of models similar
to (6), (7), (8) with the exception that D was absent1.
11
III. RECURRENTEQUILIBRIUMNETWORKS This apparently minor change to the model has far-reaching
consequences in terms of greatly increased representational
Themodelstructurewepropose–therecurrentequilibrium
flexibility and significantly simpler learning algorithms, while
network (REN) – is a state-space model of the form (1) with
alsorequiringassurancesaboutexistenceofsolutionsandtheir
efficient computation.
x =Ax +B w +B u +b , (6)
t+1 t 1 t 2 t x WithD =0,thenetwork(8)issimplyasingle-layerneu-
11
y t =C 2 x t +D 21 w t +D 22 u t +b y , (7) ral network. In contrast, equilibrium networks (D 11 = 0) are
̸
much more flexible, with many commonly-used feedforward
in which w is the solution of an equilibrium network, a.k.a.
t network architectures included as special cases. For example,
implicit network [10]–[13]:
consider a standard L-layer deep neural network:
w t =σ(D 11 w t +C 1 x t +D 12 u t +b v ), (8) z 0 =u,
z =σ(W z +b ), l=0,...,L 1 (11)
where A,B · ,C · ,D · are matricies of appropriate dimension, l+1 l l l −
b x Rn,b y Rp,b v Rq are“bias”vectors,andσisascalar y =W L z L +b L
∈ ∈ ∈
nonlinearity applied elementwise, referred to as an “activation
where z is the output of the lth hidden layer. This can be
l
function”. We will show below how to ensure that a unique
written as an equilibrium network with
solution w∗ to (8) exists and can be computed efficiently.
t
Remark2:Theterm“equilibrium”comesfromthefactthat w =col(z 1 ,...,z L ), b v =col(b 0 ,...,b L−1 ), b y =b L
any solution of the above implicit equation is also an equilib- C =0, C =0, D = (cid:2) 0 0 W (cid:3) , D =0,
1 2 21 L 22
r o i r um the po o in rd t in o a f r t y he di d f i f f e f r e e r n e t n ia c l e e e q q u u a a t t i i o o n n w d t k w +1 (s = ) σ = (Dw w t k + (s) b w + )  0 ··  ·  W 0 
“ σ f ( r D oz w en t ( ” s) f + or b w ea ) c , h wh t e . r O e n b w e = int C er 1 p x re t t + at D io d 1 n s 2 u o t t f + th b v e i R s E c − o N ns t m id o er d e e d l D 11 =      W ... 1 . . . . . . 0      , D 12 =     0 ...     .
is that it represents a two-timescale or singular perturbation 0 W 0 0
L−1
model, in which the “fast” dynamics in w are assumed to ···
reach the equilibrium (8) well within each time-step of the
1Notethat[34]useddifferentnotation,sointhatpaperitwasactuallyD22
“slow” dynamics in x (6). whichwasabsent,correspondingtoD11inthenotationofthepresentpaper.

---

# Page 5

5
Equilibrium networks can represent many other interesting D. Contracting and Robust RENs
structures including residual, convolution, and other feedfor-
We call the model of (9), (10) a contracting REN (C-REN)
ward networks. The reader is referred to [10]–[13] for further
if it is contracting and a robust REN (R-REN) if it satisfies
discussion of equilibrium networks and their properties.
the incremental IQC. We make the following assumption on
AllowingD tobenon-zeroisalsokeytoourconstruction
11 σ, which holds for commonly-used activation functions [62]:
ofdirectparamaterizationsofcontractingandrobustRENs(in
Assumption 1: The activation function σ is piecewise dif-
Sec.V).AsdiscussedinSectionI-Dthisenablesmodellearn-
ferentiable and slope-restricted in [0,1], i.e.,
ing via simple and generic first-order optimization methods,
whereas [34] required a specialized interior-point method to σ(y) σ(x)
0 − 1, x,y R, x=y. (14)
deal with model behavioural constraints. Direct parameteriza- ≤ y x ≤ ∀ ∈ ̸
−
tionalsoenableseasyrandomsamplingofcontractingmodels,
The following theorem gives conditions for contracting and
so-called echo state networks (see Sec. V-C) and this enables
robust RENs:
convex learning of nonlinear feedback controllers (see Sec.
Theorem 1: Consider the REN model (9), (10) satisfying
IX).
Assumption 1, and a given α¯ (0,1].
∈
1) Contracting REN: suppose there exists P = P⊤ 0
B. Well-posednessofEquilibriumNetworksandAcyclicRENs and Λ D such that ≻
+
∈
The added flexibility of equilibrium networks comes at a
price:dependingonthevalueofD ,theimplicitequation(8) (cid:20) α¯2P C⊤Λ (cid:21) (cid:20) A⊤(cid:21) (cid:20) A⊤(cid:21)⊤
11 − 1 P 0 (15)
mayormaynotadmitauniquesolutionw t foragivenx t ,u t . − ΛC 1 W − B 1 ⊤ B 1 ⊤ ≻
An equilibrium network or REN is well-posed if a unique
where W = 2Λ ΛD D⊤Λ. Then the REN is
solutionisguaranteed.In[12]itwasshownthatifthereexists − 11 − 11
a Λ Dn such that well-posed and contracting with some rate α<α¯.
∈ + 2) Robust REN: consider the incremental defined in IQC
2Λ ΛD D ⊤Λ 0, (12) (5) with given (Q,S,R) where Q 0. Suppose there
11 11
− − ≻ exist P =P⊤ 0 and Λ D suc ⪯ h that
+
then the equilibrium network is well-posed. We will show in ≻ ∈
Theorem1belowthatthisisalwayssatisfiedforourproposed  α¯2P C⊤Λ C⊤S⊤ 
− 1 2
model parameterizations.  − ΛC 1 W D 2 ⊤ 1 S⊤ − ΛD 12 
A useful subclass of REN that is trivially well-posed is SC SD D⊤Λ R+SD +D⊤S⊤
2 21 − 12 22 22
the acyclic REN where the weight D 11 is constrained to be  A⊤  A⊤⊤  C⊤  C⊤⊤
strictly lower triangular. In this case, the elements of w can 2 2
beexplicitlycomputedrow-by-rowfrom(8).Wecaninte t rpret − B 1 ⊤ P B 1 ⊤  +D 2 ⊤ 1QD 2 ⊤ 1 ≻ 0.
B⊤ B⊤ D⊤ D⊤
D as the adjacency matrix of a directed graph defining 2 2 22 22
11 (16)
interconnections between the neurons in the equilibrium net-
work and if D is strictly lower triangular then this graph is Then the REN is well-posed, satisfies (5) and is con-
11
guaranteed to be acyclic. Compared to the general REN, the tracting with a rate α<α¯.
acyclic REN is simpler to implement and in our experience
TheproofcanbefoundinAppendixA. Themainideabehind
often provides models of similar quality, as will be discussed
the LMI for the contracting REN is to use an incremental
in Sec. VII-B. Lyapunov function V(∆x) = ∆x2, where ∆x denotes the
| |P
difference between a pair of solutions, and show that
C. Evaluating RENs and their gradients
V(∆x ) α2V(∆x ) Γ(∆v ,∆w ) (17)
t+1 t t t
For a well-posed REN with full D , solutions can be ≤ −
11
computed by formulating an equivalent monotone operator andthatΓ(∆v ,∆w ) 0fortheactivationfunctionσ,where
t t
≥
splitting problem [61]. In the authors’ experience, the Peace- Γ is an incremental quadratic constraint as in [9], [34] with a
man Rachford algorithm is reliable and efficient [12]. multiplier matrix Λ. The construction for the Robust REN is
Whentraininganequilibriumnetworkviagradientdescent, similar, but uses an incremental dissipation inequality.
we need to compute the Jacobian ∂w∗/∂() where w∗ is the Remark 3: Note that (15) and (16) immediately imply that
t · t
solution of the implicit equation (8), and () denotes the input W 0, which is precisely the equilibrium network well-
· ≻
to the network or model parameters. By using the implicit posedness condition (12).
function theorem, ∂w∗/∂() can be computed via Remark 4: For a fixed REN model, Conditions (15) and
t ·
(16) are convex in the stability/performance certificate P and
∂w∗ ∂(Dw⋆+b )
t =(I JD)−1J t w (13) IQC multiplier Λ. However they are not jointly convex in the
∂() − ∂()
· · model parameters θ, certificate P, and multiplier Λ. We will
whereJ istheClarkegeneralizedJacobianofσ atDw∗+b . resolve this in the next section.
t w
From Assumption 1 in Section III-D, we have that J is Remark 5: The proof is based on IQC characterization of
a singleton almost everywhere. It was shown in [12] that (14)withadiagonalmultipliermatrixΛ.Ifsignalboundedness
Condition (12) implies matrix I JD is invertible. isofinterestratherthancontraction,thenonecanusearicher
−

---

# Page 6

6
class of multipliers designed for repeated nonlinearities [63]– Thefollowingresultsrelatestheaboveparameterizationsto
[65]. However, these multipliers are not valid for incremental the desired model behavioural properties:
IQCs and contraction [12]. Theorem 3: All models in Θ are well-posed and con-
C
While Q,S,R can be chosen so that a robust REN verifies tracting with rate α < α¯. All models in Θ are well-posed,
R
aparticular Lipschitzboundγ,thefollowingweakerproperty contracting with rate α < α¯, and satisfy the IQC defined by
is true of contracting RENs: (Q,S,R).
Theorem 2: Every contracting REN – i.e. a model (9), (10) The proof can be found in the Appendix C.
satisfying Assumption 1 and (15) – satisfies the ℓ2 Lipschitz Remark 6: With the convex parameterizations, is straight-
condition for some bound γ < . forward to enforce any desired sparsity structure on D , e.g.
∞ 11
The proof is in Appendix B. corresponding to a multi-layer neural network as per Section
III-A. Since Λ is diagonal, the sparsity structures of and
11
D
IV. CONVEXPARAMETERIZATIONSOFRENS D 11 =Λ−1 11 are identical, and so the desired structure can
D
be added as a linear constraint on .
In this section we propose convex parameterizations for 11
D
C-RENs/R-RENs, which are based on the following implicit
representation of the linear component G: V. DIRECTPARAMETERIZATIONSOFRENS
W(cid:102) In the previous section we gave convex parameterizations
(cid:122) (cid:125)(cid:124) (cid:123)
 Ex   F  x  of contracting and robust RENs in terms of linear matrix
t+1 1 2 t
 Λv t = 1 B 11 B 12 w t+˜b (18) inequalities (LMIs), i.e. intersections of the cone of positive
y C C D D D D u semidefinite matrices with affine constraints. While convexity
t 2 21 22 t
of a model set is useful, LMIs are challenging to verify for
where E is an invertible matrix and Λ is a positive-
large-scale models, and especially to enforce during training.
definite diagonal matrix. The model parameters are θ :=
cvx In this section we provide direct parameterizations, i.e.
E,Λ,W(cid:102),˜b . smooth mappings from RN to the weights and biases of
{ }
Notethatθ caneasilybemappedtoθ bymultiplyingthe
cvx a REN, enabling unconstrained optimization methods to be
first and second rows of (18) by E−1 and Λ−1, respectively.
applied. We do so by first constructing representations of
Therefore the parameters E and Λ do not expand the model
RENs directly in terms of the positive semidefinite cone
set, however the extra degrees of freedom will allow us to
without affine constraints, and then parameterize this cone in
formulatesetsofC-RENsandR-RENsthatarejointlyconvex
terms of its square-root factors.
in the model parameters, stability certificate, and multipliers.
Definition 4: A model of the form (18), (10) is said to be
well-posed if it yields a unique (w ,x ) for any x ,u and A. Direct Parameterizations of Contracting RENs
t t+1 t t
˜b, and hence a unique response to any initial conditions and
The key observation leading to our construction is that the
input.
mapping from contracting REN parameters θ to H in (21)
cvx
To construct a convex parameterization of C-RENs, we
is surjective, i.e. it maps onto the entire cone of positive-
introduce the following LMI constraint:
definite matrices. Furthermore, as we will show below it is
 E+E⊤ 1 ⊤ F⊤ straightforward to construct a (non-unique) inverse that maps
H(θ cvx ):= − F C − 1 α¯2P − W C1 B1 ⊤  ≻ 0, (19) f p r o o s m ed a a n n y d po co si n ti t v ra e c - t d i e n fi g n R ite EN m . atrixbacktoθ cvx definingawell-
1
B P
a) Free parameters: of the parameters in θ , the fol-
cvx
where =2Λ ⊤. The convex parameterization of
W −D 11 −D11 lowing have no effect on stability and can be freely parame-
C-RENs is then given by terized in terms of their elements: Rn×m, C Rp×n,
2 2
Θ := θ = ⊤ 0s.t.H(θ ) 0 . 12 Rq×m, D 21 Rp×q, D 22 BRp× ∈ m,˜b R(2n+ ∈ q).
C cvx cvx D ∈ ∈ ∈ ∈
{ |∃P P ≻ ≻ } b) Constrainedparameters,acycliccase: theparameters
To construct convex parameterization of R-RENs, we propose E,F,Λ, and relate to internal dynamics and therefore
1 1
the following convex constraint: affect th B e stabilit C y properties of a REN. Here we construct
 E+E⊤ 1 ⊤ C⊤S⊤  them from two free matrix variables X R(2n+q)×(2n+q)
 S − C C − 1 α¯2P SD − W C1 ⊤ R+ D S 2 ⊤ 1 D S 2 ⊤ + − D D 1 ⊤ 2 S⊤  and W Y e 1 fi ∈ rst R c n o × n n st . ruct H from X as ∈
2 21 −D12 22 22
 
 F⊤  F⊤⊤  C⊤  C⊤⊤ H
11
H
12
H
13
−  B1 ⊤ ⊤  P −1  B1 ⊤ ⊤  +D D 2 2 ⊤ ⊤ 1QD D 2 2 ⊤ ⊤ 1 ≻ 0 H =H H 2 3 1 1 H H 2 3 2 2 H H 2 3 3 3 =X⊤X+ϵI ≻ 0 (21)
B2 B2 22 22
(20)
where ϵ is a small positive scalar, and we have partitioned H
where Q 0, S, and R are given. The convex parameteriza- intoblocksofsizen,n,andq.Comparing(21)to(19)wecan
tion of R- ⪯ RENs is then defined as immediately construct
Θ := θ = ⊤ 0s.t.(20) . F =H , =H , =H , = H . (22)
R cvx 31 1 32 33 1 21
{ |∃P P ≻ } B P C −

---

# Page 7

7
Further, it is straightforward to verify that the construction b) Constrained parameters: the construction is similar
to the contracting case in Section V-A.
1
E = 2 (H 11 + α¯ 1 2P +Y 1 − Y 1 ⊤), (23) ind S e i p n e c n e d D en 2 t 2 o = f 0 m , o C d o e n l d p i a ti r o a n m ( e 2 te 8 r a s ) . r N ed o u w ce C s o to nd R iti ≻ on 0 ( , 2 w 8 h b i ) ch ca i n s
results in H =E+E⊤ 1 for any Y . be satisfied if we construct H as
11 − α¯2P 1
We then construct a strictly lower-triangular 11 satisfying H =X⊤X+ϵI+
D
 ⊤  ⊤⊤  C⊤  C⊤⊤
H
22
=
W
=2Λ
−D 11 −D1
⊤
1
(24)
 D
C2
2 ⊤ 1 R −1  D
C2
2 ⊤ 1 − D
2
2 ⊤ 1QD
2
2 ⊤ 1 ≻ 0,
(29)
0 0
by partitioning H into its diagonal and strictly upper/lower 2 2
22 B B
triangular components:
with X a free matrix variable, and then recover the remaining
modelparametersfrom H asperSectionV-A.NotethatH
H =Φ L L⊤ (25) ≻
22 − − 0, since 0 and Q 0.
R≻ ⪯
2) Models with D =0: in this case we need to construct
where Φ is a diagonal matrix and L is a strictly lower- 22 ̸
a D satisfying (28a). In what follows it will be useful to
triangular matrix, from which we construct the remaining 22
have Q invertible but we have only assumed that Q 0. If
parameters in θ cvx : Q is not negative-definite, we introduce =Q εI ⪯ 0 and
Q − ≺
1 note that (28a) is equivalent to
Λ= Φ, =L. (26)
2 D 11
R+SD +D⊤S⊤+D⊤ D 0 (30)
22 22 22Q 22 ≻
c) Constrained parameters, full case: The construction
for sufficiently small ε > 0. If Q 0 we simply set ε = 0,
of a C-REN with full (not acyclic) D is the same except
11 ≺
that we introduce two additional free variables: g Rq and i.e. =Q.
Q
Λ Y 2 = ∈ ed R ia q g × (g q ) , a a n n d d then construct a positive diagon ∈ al matrix 1) W th e at fa R ctor S Q = −1 − S L ⊤ ⊤ Q L Q 0 , h a e n n d c w e e th w er il e ls is ho a w n ( in se v e er P ti r b o l p e o L si R tion
Rm×m suc − h th Q at L⊤L ≻ =R S −1S⊤. ∈
1 R R − Q
D 11 =Λ − 2 (H 22 +Y 2 − Y 2 ⊤), (27) The direct parameterization of D 22 is
D = −1S⊤+L−1NL , (31)
which also results in parameters satisfying (24). 22 −Q Q R
where construction of N depends on the input and output
dimensions. If p m we take
B. Direct Parameterizations of Robust RENs ≥
M =X⊤X +Y Y⊤+Z⊤Z +ϵI,
We now provide a direct parameterization of RENs satisfy- 3 3 3 − 3 3 3
(cid:20) (I M)(I+M)−1(cid:21) (32)
ingtherobustnesscondition(20).Thefirststepistorearrange N = − .
2Z (I+M)−1
(20)intoanequivalentformwhichwillturnouttobeusefulin 3
−
theconstructionsinceitmakesexplicittheconnectionbetween
with X ,Y Rm×m and Z R(p−m)×m as free variables.
the R-REN and C-REN conditions: 3 3 ∈ 3 ∈
Note that M +M⊤ 0 so I+M is invertible.
≻
:=R+SD +D⊤S⊤+D⊤QD 0, (28a) If p<m, M is the same but we take
R 22 22 22 22 ≻
 ⊤  ⊤⊤  C⊤  C⊤⊤ N = (cid:2) (I+M)−1(I M) 2(I+M)−1Z⊤(cid:3) (33)
H(θ cvx ) ≻  D C B 2 2 ⊤ 2 1 R −1  D C B 2 2 ⊤ 2 1 − D 0 2 2 ⊤ 1QD 0 2 2 ⊤ 1 (2 , 8b) wi P th ro X po 3 , si Y ti 3 o ∈ n1 R : p T × h p e a c n o d ns − Z tr 3 uc ∈ ti R on ( − m o − f p D )× 22 p i a n s ( f 3 r 1 e ) e , v 3 (3 a 2 ri ) ab o l r e ( s 3 . 3)
is well-defined and satisfies Condition (30).
where H(θ ) is the C-REN condition defined in (19), = The proof is in Appendix D.
cvx 2
C
(D 2 ⊤ 2 Q+S)C 2 and D 21 =(D 2 ⊤ 2 Q+S)D 21 −D1 ⊤ 2 . a) Special Cases: the following are direct parameteriza-
The first construction we give is for the simplest case tions of D for some commonly-used robustness conditions:
22
withoutdirect-feedthrough,i.e.D
22
=0.However,someprac-
• Incrementally ℓ 2 stable RENs with Lipschitz bound of γ
tically useful constraints require D 22 = 0, e.g., incremental (i.e., Q= 1I,R =γI,S =0): We have D given in
passivity requires D 22 + D 2 ⊤ 2 ≻ 0. W ̸ e consider this more (31) with L − Q γ =I and L R =γI. 22
general case below. • Incrementally strictly output passive RENs (i.e., Q =
1) Models with D 22 = 0: for models with no direct − 2ρI,R=0,S =I): We have D 22 = ρ 1(I+M)−1.
feedthrough we have the following direct parameterization. • Incrementally input passive RENs (i.e., Q = 0,R =
a) Free variables: the following matrix variables can be 2νI,S = I): In this case, Condition (28a) becomes
freely parameterized in terms of their elements: Rn×m, − an LMI of the form D +D⊤ 2νI 0, which yields
C Rp×n, Rq×m, D Rp×q, ˜b R(2 B n+ 2 q ∈ ) a simple parameterizat 2 io 2 n wit 2 h 2 D − = ≻ νI+M.
2 12 21 22
∈ D ∈ ∈ ∈

---

# Page 8

8
C. Random Sampling of Nonlinear Systems and Echo State c) Stable linear systems: setting B ,C ,D ,D ,D
1 1 11 12 21
Networks andbtozero,RENsincludeallstablefinite-dimensionallinear
time-invariant (LTI) systems (see [34, Theorem 4]).
One benefit of the direct parameterizations of RENs is that
d) Previously proposed stable echo state networks: the
it is straightforward to randomly sample systems with the
stability condition for the ciRNN is the same as that proposed
desired behavioural properties. Since contracting and robust
RENs are constructed as the image of RN under a smooth for echo state networks in [57], [58], hence by randomly
sampling RENs as in Section V-C we sample from a strictly
mapping (Sections V-A and V-B), one can sample random
vectorsinRN andmapthemtorandomstable/robustnonlinear larger set of echo state networks than previously known.
e) Nonlinear finite impulse response (NFIR) Models: an
dynamical systems.
NFIR model a nonlinear mapping of a fixed history of inputs:
An“echostatenetwork”isamodelinwhichthestate-space
dynamics are randomly sampled but thereafter fixed, and with y =f(u ,u ,...u ),
t t t−1 t−h
a learnable output map (see ,e.g., [57], [58]):
for some fixed h. Setting
x =f(x ,u ) (34)
t+1 t t  0   I 
y =g(x ,u ,θ) (35)
where f is fixed and g t+ is 1 affinely t pa t rameterized by θ, i.e. A=     I I 0 ...     , B 2 =    0 0    , B 1 =0. (36)
g(x ,u ,θ)=g (x ,u )+
(cid:88)
θ gi(x ,u ).

...
  ... 
t t 0 t t i t t
i
The output y is then a nonlinear function (an equilibrium
Then,systemidentificationwithasimulation-errorcriteriacan network) of such truncated history of inputs.
be solved as a basic least squares problem. This approach is f) Block structured models: these are constructed from
reminiscentofsystemidentificationviaabasisofstablelinear seriesinterconnectionsofLTIsystemsandstaticnonlinearities
responses (see, e.g., [66]). [67], [68], and are included within the REN model set. For
For this approach to work over long horizons, it is essen- example:
tial that the random dynamics are stable. In [57], [58] and
1) Wiener systems consist of an LTI block followed by a
references therein, contraction of (34) is referred to as the
static non-linearity. This structure is replicated in (9),
“echo state property”, and simple parameterizations are given
(10) when B = 0 and C = 0. In this case the
1 2
for which contraction is guaranteed. The direct parameteri-
linear dynamical system evolves independently of the
zations of REN can be used to randomly sample from a rich
non-linearities and feeds into a equilibrium network.
classofcontractingmodels,bysamplingX,Y ,Y , , to
1 2 B 2 D 12 2) Hammerstein systems consist of a static non-linearity
construct the state-space dynamics and equilibrium network.
connected to an LTI system. This is represented in the
Such a model can be used e.g. for system identification by
REN when B = 0 and C = 0. In this case the input
2 1
simulating its response to inputs to generate data u˜ ,x˜ ,w˜ ,
t t t passes through a static equilibrium network and into an
and then the output mapping
LTI system.
y =C x˜ +D w˜ +D u˜ +b More generally, arbitrary series and parallel interconnections
t 2 t 21 t 22 t y
of LTI systems and static nonlinearities can also be con-
can be fit to y˜, minimizing (3) via least-squares to obtain
t structed.
the parameters C 2 ,D 21 ,D 22 ,b y . We will also see in Section g) Universal approximation properties: it is well known
IX how this approach can be applied in data-driven feedback
even single-hidden-layer neural networks have universal ap-
control design.
proximation properties, i.e. as the number of neurons goes to
infinity they can approximate any continuous function over a
VI. EXPRESSIVITYOFRENMODELCLASS bounded domain with arbitrary accuracy. RENs immediately
inherit this property for universal approximation of static
ThesetofRENscontainmanywidely-usedmodelstructures
maps, NFIR models, and other block-structured models.
as special cases, some of which we briefly describe here.
Furthermore, it was shown in [69] that as the number of
a) Deep, Residual, and Equilibrium Networks: as a spe-
states and activation functions grows, the REN structure is a
cialcasewithA,C ,C ,B ,B allzero,RENsinclude(static)
1 2 1 2 universal approximator of fading-memory nonlinear systems
equilibriumnetworks,whichasdiscussedinSectionIII-Aand
as defined in [70], as well as all nonlinear dynamical systems
[11]–[13] include standard deep neural networks (multi-layer
that are contracting and have finite Lipschitz bounds.
perceptrons), residual networks, and others.
b) PreviouslyproposedstableRNNs: ifwesetD =0,
11
then the nonlinearity is not an equilibrium network but a
VII. USECASE:STABLEANDROBUSTNONLINEAR
single-hidden-layer neural network, and our model set Θ
SYSTEMIDENTIFICATION
C
reducestothemodelsetproposedin[34].Therefore,theREN In this section we demonstrate the proposed models on
modelclassalsoincludesallothermodelsthatwereprovento the F16 ground vibration [71] and Wiener Hammerstein with
beinthatmodelsetin[34,Theorem5],includingpriorsetsof process noise [72] system identification benchmarks. We will
contracting RNNs including the ciRNN [33] and s-RNN [30]. compare the acyclic C-REN and Lipschitz-bounded R-REN

---

# Page 9

9
with prescribed Lipschitz bound of γ with the widely-used 0.6
long short-term memory (LSTM) [73] and standard RNN
models with a similar number of parameters. We will also 0.5
compare to the Robust RNN proposed in [34] using the code
from github.com/imanchester/RobustRNN. 0.4
We fit models by minimizing simulation error: 0.3
L se (z˜,θ)= || y˜ − R a (u˜) || 2 T (37) 0.2
using minibatch gradient descent with the Adam optimizer 0.1
10 100 1000
[56].Modelperformanceismeasuredbynormalizedrootmean γ
square error on the test sets, calculated as:
y˜ R (u˜)
NRMSE= || − a || T. (38)
y˜
T || ||
Model robustness is measured in terms of the maximum
observed sensitivity:
R (u) R (v) γ =max|| a − a || T. (39)
u,v,a u v T
|| − ||
We find a local solution to (39) using gradient ascent with the
Adamoptimizer. Consequently γ is alowerbound onthe true
Lipschitz constant of the sequence-to-sequence map.
A. Benchmark Datasets and Training Details
1) F16 System Identification Benchmark: The F16 ground
vibration benchmark dataset [71] consists of accelerations
measured by three accelerometers, induced in the structure of
anF16fighterjetbyawingmountedshaker.Weusethemulti-
sine excitation dataset with full frequency grid. This dataset
consists of 7 multi-sine experiments with 73,728 samples and
varying amplitude. We use datasets 1, 3, 5 and 7 for training
and datasets 2, 4 and 6 for testing.
All models in our comparison have approximately 118,000
parameters: the RNN has 340 neurons, the LSTM has 170
neurons and the RENs have width n = 75 and q = 150.
Models were trained for 70 epochs with a sequence length
of 1024. The learning rate was initalized at 10−3 and was
reduced by a factor of 10 every 20 Epochs.
2) Wiener-Hammerstein With Process Noise Benchmark:
The Wiener Hammerstein with process noise benchmark
dataset[72]involvestheestimationoftheoutputvoltagefrom
two input voltage measurements from a Wiener-Hammerstein
system with large process noise. We have used the multi-sine
fade-out dataset consisting of two realisations of a multi-sine
input signal with 8192 samples each. The test set consists of
twoexperiments,arandomphasemulti-sineandasinesweep,
conducted without the added process noise.
All models in our comparison have approximately 42,000
parameters: the RNN has 200 neurons, the LSTM has 100
neurons and the RENs have n = 40 and q = 100. Models
were trained for 60 epochs with a sequence length of 512.
The initial learning rate was 10−3 and was reduced to 10−4
after 40 epochs.
ESMRN
R-aRENγ=10
R-aRENγ=20
R-aRENγ=40
C-aREN
RobustRNNγ=10
RobustRNNγ=20 RobustRNNγ=40
RobustRNNγ=
LSTM ∞
RNN
Fig. 2: Nominal performance versus robustness for models
trained on F16 ground vibration benchmark dataset. The
dashed vertical lines are the guaranteed upper bounds on γ
corresponding to the models with matching color.
B. Results and Discussion
In Figs. 2 and 3 we have plotted the test-set NRMSE (38)
versus the observed sensitivity (39) for each of the models
trained on the F16 and Wiener-Hammerstein Benchmarks,
respectively. The dashed vertical lines show the guaranteed
Lipschitz bounds for the REN and Robust RNN models.
We observe that the REN offers the best trade-off between
nominal performance and robustness, with the REN slightly
outperforming the LSTM in terms of nominal test error for
largeγ.Bytuningγ,nominaltestperformancecanbetraded-
off for robustness, signified by the consistent trend moving
diagonally up and left with decreasing γ. In all cases, we
found that the REN was significantly more robust than the
RNN,typicallyhavingabout10%ofthesensitivityfortheF16
benchmark and 1% on the Wiener-Hammerstein benchmark.
Also note that for small γ, the observed lower bound on the
Lipschitzconstantisveryclosetotheguaranteedupperbound,
showingthattherealLipschitzconstantofthemodelsisclose
to the upper bound.
Compared to the robust RNN proposed in [34], the REN
has similar bounds on the incremental ℓ gain, however the
2
added flexibility from the term D significantly improves
11
the nominal model performance for a given gain bound.
Additionally, while both the C-REN and Robust RNN γ=
∞ arecontractingmodels,wenotethattheC-RENissignificantly
more expressive with a NRMSE of 0.16 versus 0.24.
It is well known that many neural networks are very sensi-
tive to adversarial perturbations. This is shown, for instance,
inFig.4and5,wherewehaveplottedthechangeinoutputfor
a small adversarial perturbation ∆u <0.05, for a selection
|| ||
of models trained on the F16 benchmark dataset. Here, we
can see that both the RNN and LSTM are very sensitive to
the input perturbation. The R-REN and R-RNN on the hand,
have guaranteed bounds on the effect of the perturbation and
are significantly more robust.
WehavealsotrainedcyclicRENs(i.e.D isafullmatrix)
11
for the F16 Benchmark dataset. The resulting nominal perfor-
mance and sensitivities for the acyclic and cyclic RENs are
shown in Table I. We do not observe a significant difference
in performance between the cyclic and acyclic model classes.

---

# Page 10

10
0.50
0.45
0.40
0.35
0.30
0.25 10 100 1000
γ
ESMRN
R-aRENγ=1.5
R-aRENγ=2.5
R-aRENγ=3.5
C-aREN
LSTM
RNN
Fig. 3: Nominal performance versus robustness for models
trainedonWiener-Hammersteinwithprocessnoisebenchmark
dataset. The dashed vertical lines are the guaranteed upper
boundsonγ correspondingtothemodelswithmatchingcolor.
0.6
0.4
0.2
0.0
0.2
−
0.4
−
0.6
−
0 1000 2000 3000
TimeSteps
y∆
1
RNN
LSTM
R-aRENγ=40
R-aRENγ=10
RobustRNNγ=40
RobustRNNγ=10
Fig. 4: Change in output of models subject to an adversarial
perturbation with ∆u < 0.05. The incremental gains from
|| ||
∆u to ∆y are 980, 290, 37, 8.6, 38.9 and 9.1, respectively.
0.3
0.2
0.1
0.0
0.1
−
0.2
−
0.3
− 1000 1100 1200 1300 1400 1500
TimeSteps
y∆ 1
10
1
0 20 40 60
Epochs
RNN
LSTM
R-aRENγ=40
R-aRENγ=10
RobustRNNγ=40 RobustRNNγ=10
Fig. 5: Zoomed in version of Fig. 4.
TABLE I: Nominal performance (NRMSE) and upper and
lower bounds on Lipschitz constant for acyclic and cyclic
RENs on F16 benchmark dataset.
γ 10 20 40 60 100 ∞
γ 8.8 17.5 36.7 44.9 60.56 91.0
acyclic
NRMSE(%) 30.0 25.7 20.1 18.5 17.2 16.2
γ 9.1 17.1 36.0 44.6 57.9 85.26
cyclic
NRMSE(%) 30.3 26.8 21.8 19.9 19.3 16.8
ssoL
R-aRENγ=10
R-aRENγ=20
R-aRENγ=40
C-aREN
LSTM
RNN
Fig. 6: Traing loss versus epochs for models trained on F16
ground vibration benchmark dataset.
Finally, we have plotted the training loss (37) versus the
number of epochs in Fig. 6 for some of the models on the
F16 dataset. Compared to the LSTM, the REN takes a similar
number of steps and achieves a slightly lower training loss.
VIII. USECASE:LEARNINGNONLINEAROBSERVERS
Estimation of system states from incomplete and/or noisy
measurements is an important problem in many practical
applications.ForlinearsystemswithGaussiannoise,asimple
and optimal solution exists in the form of the Kalman filter,
but for nonlinear systems even finding a stable estimator
(a.k.a.observer)isnon-trivialandmanyapproacheshavebeen
investigated, e.g. [74]–[76]. Observer design was one of the
original motivations for contraction analysis [14], and in this
section, we show how a flexible set of contracting models
can be used to learn stable state observers via snapshots of a
nonlinear system model.
The aim is to estimate the state of a nonlinear system of
the form
x =f (x ,u ,w ), y =g (x ,u ,w ) (40)
t+1 m t t t t m t t t
where x X is an internal state to be estimated, y is an t t
availablem ∈ easurement,u Uisaknown(e.g.control)input, t
and w W comprises ∈ unknown disturbances and sensor
t ∈
noise.
A standard structure, pioneered by Luenberger, is an ob-
server of the form
xˆ =f (xˆ ,u ,0)+l(xˆ ,u ,y ) (41)
t+1 m t t t t t
i.e. a combination of a model prediction f and a mea-
m
surement correction function l. A common special case is
l(xˆ ,u ,y )=L(xˆ)(y g (xˆ ,u ,0)) for some gain L(xˆ).
t t t t m t t
−
In many practical cases the best available model f ,g
m m
is highly complex, e.g. based on finite element methods or
algorithmic mechanics [77]. This poses two major challenges
to the standard paradigm:
1) How to design the function l such that the observer
(41) is stable (preferably globally) and exhibits good
noise/disturbance rejection.
2) The model itself may be so complex that evaluating
f (xˆ ,u ,0) in real-time is infeasible, e.g. for stiff
m t t
systems where short sample times are required.

---

# Page 11

11
Our parameterization of contracting models enables an al- A. Example: Reaction-Diffusion PDE
ternative paradigm, first suggested for the restricted case of
We illustrate this approach by designing an observer for
polynomial models in [50], [51].
thefollowingsemi-linearreaction-diffusionpartialdifferential
Proposition 2: If we construct an observer of the form
equation:
xˆ =f (xˆ ,u ,y ) (42) ∂ξ(z,t) ∂2ξ(z,t)
t+1 o t t t
= +R(ξ,z,t), (47)
∂t ∂z2
such that the following two conditions hold:
ξ(z,0)=1, ξ(1,t)=ξ(0,t)=b(t) (48)
1) The system (42) is contracting with rate α (0,1) for
y =g(ξ,z,t) (49)
∈
some constant metric P 0.
≻
2) The following “correctness” condition holds: where the state ξ(z,t) is a function of both the spatial
coordinatez [0,1]andtimet R .Modelsoftheform(47)
+
f (x,u,0)=f (x,u,g (x,u,0)), (x,u) X U. ∈ ∈
m o m model processes such as combustion [78], bioreactors [79] or
∀ ∈ ×
(43) neural spiking dynamics [78]. The observer design problem
Then when w = 0 we have xˆ x as t . Suppose for such systems has been considered using complex back-
t t
→ → ∞
instead Condition 2) does not hold but that the observer (42) stepping methods that guarantee only local stability [79].
satisfies Conditions 1) and We consider the case where the local reaction dynamics
3) The following error bound holds (x,u,w) X U havethefollowingform,whichappearsinmodelsofcombus-
W: ∀ ∈ × × tion processes [78]:
1
f (x,u,g (x,u,w)) f (x,u,w) ρ. (44) R(ξ,z,t)= ξ(1 ξ)(ξ 1).
| o m − m |≤ 2 − − 2
Then the estimation error satisfies, with exponential conver- We consider the boundary condition b(t) as a known input
gence: and assume that there is a single measurement taken from the
ρ (cid:114) σ center of the spatial domain so y(t)=ξ(0.5,t).
lim t s → u ∞ p | xˆ t − x t |≤ 1 α σ , (45) We discretize z into N intervals with points z0,...,zN
− where zi =i∆z. The state at spatial coordinate zi and time t
where σ and σ denote the maximum and minimum singular is then described by ξ¯ =(ξ0,ξ1,...,ξN) where ξi =ξ(zi,t).
t t t t t
values of the contraction metric P, respectively. Thedynamicsoveratimeperiod∆tcanthenbeapproximated
Remark 7: Note that the error term (44) may result from using the following finite differences:
bounded disturbances w , modelling errors, or interpolation
t
errors arising from fitting the correctness condition to finite ∂ξ(z,t) ξ t i +∆t− ξ t i , ∂2ξ(z,t) ξ t i+1+ξ t i−1 − 2ξ t i .
data (see Sec VIII-A), or some combination of such factors. ∂t ≈ ∆t ∂z2 ≈ ∆z2
The reasoning for nominal convergence of the observer is Substituting them into (47) and rearranging for ξ¯ leads to
t+∆t
simple:(43)impliesthatifxˆ
0
=x
0
thenxˆ
t
=x
t
forallt 0,
an N +1 dimensional state-space model of the form:
≥
i.e. the true state is a particular solution of the observer. But
contraction implies that all solutions of the observer converge ξ¯ t+∆t =a rd (ξ¯ t ,b t ), y t =c rd (ξ¯ t ). (50)
to each other. Hence all solutions of the observer converge to
We generate training data by simulating the system (50) with
the true state. The proof of the estimation error bound can be
N = 50 for 105 time steps with the stochastic input b =
found in Appendix E. t+1
b +0.05ω where ω [0,1]. We denote this training data
Motivated by Proposition (2) we pose the observer design b t y z˜=(ξ˜ t ,y˜,˜b ) fo t r ∼ t= N 0,...,105∆t.
problem as a supervised learning problem over our class of t t t
To train an observer for this system, we construct a C-REN
contracting models.
with n = 51 and q = 200. We optimize the one step ahead
1) Construct the dataset: sample a set of points z˜ =
prediction error:
(xi,ui),i = 1,2,...,N where (xi,ui) X U,
f a { n m d (x f i o , r u e i, a 0 c ) h . compute g m i } = g m (xi,ui,0) ∈ and f × m i = L (z˜,θ)= T 1 T (cid:88) −1 | a rd (ξ˜ t ,˜b t ) − f o (ξ˜ t ,˜b t ,y˜ t ) | 2,
2) Learn a contracting system f minimizing the loss t=0
o
using SGD with the Adam optimizer [56]. Here, f (ξ,b,y) is
o
N
L o (z˜,θ)= (cid:88)(cid:12) (cid:12)f m i − f o (xi,ui,g m i ) (cid:12) (cid:12) 2 . (46) a dis C c - u R ss E e N d i d n es S c e r c ib ti e o d n b V y -A (9 . ) N , o (1 te 0) th u a s t in w g e d h i a r v ec e t ta p k a e ra n m th et e ri o z u a t ti p o u n t
i=1
mapping in (9) to be [C ,D ,D ]=[I,0,0].
2 21 22
Remark 8: An observer of the traditional form (41) with We have plotted results of the PDE simulation and the
l(xˆ t ,u t ,y t ) = L(xˆ)(y t g m (xˆ t ,u t ,0)) will always satisfy observer state estimates in Fig. 7. The simulation starts with
−
thecorrectnesscondition,butdesigningL(xˆ)toachieveglobal an initial state of ξ(z,0) = 1 and the observer has an initial
convergence may be difficult. In contrast, an observer design state estimate of ξ¯ =0. The error between the state estimate
0
using the proposed procedure will always achieve global and the PDE simulation’s state quickly decays to zero and the
convergence, but may not achieve correctness exactly. observer state continues to track the PDE’s state.

---

# Page 12

12
111
e
u
Tr
000...888
er
er v 000...666
bs
O
000...444
or
Err
000...222
0 500 1000 1500 2000
Time Steps 000
Fig. 7: Simulation of a semi-linear reaction diffusion equation
and the observer’s state estimate, with a measurement in the
centre of the spatial domain. The y-axis corresponds to the
spatial dimension and the x-axis corresponds to the time
dimension.
(a) True and estimated states for ξ1, located at PDE boundary.
t
1.00
0.75
0.50
0.25
0.00
0 500 1000 1500 2000
TimeSteps
01ξ t
IX. USECASE:DATA-DRIVENFEEDBACKCONTROL
DESIGN
In this section we show how a rich class of contracting
nonlinear models can be useful for nonlinear feedback de-
sign for linear dynamical systems with stability guarantees.
Even if the dynamics are linear, the presence of constraints,
uncertain parameters, non-quadratic costs, and non-Gaussian
disturbances can mean that non-linear policies are superior to
linear policies. Indeed, in the presence of constraints, model
predictive control (a nonlinear policy) is a common approach.
The basic idea we illustrate in this section is to build
on a standard method for linear feedback optimization: the
Youla-Kucera parameterization, a.k.a Q-augmentation [18],
[52], [53], [80]. For a discrete-time linear system model
x =Ax +B w +B u , (51) t+1 t 1 t 2 t
ζ =C x +D w +D u . (52)
t 1 t 11 t 12 t
y =C x +D w . (53)
t 2 t 21 t
with x the state, u the controlled input, w external inputs
(reference, disturbance, measurement noise), y a measured
output, and ζ comprises the “performance” outputs to kept
small (e.g. tracking error, control signal). We assume the
system is detectable and stabilizable, i.e. there exist L and
K such that A LC and A BK are Schur stable. Note that
if A is stable w − e can take L− =0,K=0. Consider a feedback
controller of the form:
xˆ =Axˆ +B u +Ly˜ (54)
t+1 t 2 t
y˜ =y C xˆ (55)
t t 2 t
−
u = Kxˆ +u˜ (56)
t t t
−
i.e. a standard output-feedback structure with v an additional
t
control augmentation. The closed-loop input-output dynamics
can be written as the transfer matrix
(cid:20) (cid:21) (cid:20) (cid:21)(cid:20) (cid:21)
ζ w
= T 0 T 1 (57)
y˜ 0 u˜
2
T
where we have used the fact that u˜ maps to x and xˆ equally,
hence the mapping from u˜ to y˜ is zero.
Itiswell-knownthatthesetofallstabilizinglinearfeedback
controllers can be parameterised by stable linear systems
: y˜ u˜, and moreover this convexifies the closed-loop
(b) True and estimated states for ξ10. Q (cid:55)→
t dynamics.Astandardapproach(e.g.[53],[80])istoconstruct
Fig. 8: True state and state estimates from the designed an affine parameterization for via a finite-dimensional
Q
observer and a free run simulation of the PDE. truncationofacompletebasisofstablelinearsystems,andop-
timizetomeetvariouscriteriaonfrequencyresponse,impulse
response, and response to application-dependent test inputs.
However, if the control augmentation u˜ is instead generated
by a contracting nonlinear system u˜= (y˜), then the closed-
Wehavealsoprovidedacomparisontoafreerunsimulation Q
loop dynamics w ζ are nonlinear but contracting and have
of the PDE with initial condition ξ(z,0) = 0 in Fig. 8. (cid:55)→
the representation
Here we can see that simulated trajectories with different
initial conditions do not converge. This suggests that the ζ = w+ ( w) (58)
0 1 2
system is not contracting and the state cannot be estimated T T Q T
by simply running a parallel simulation. The state estimates This presents opportunities for learning stabilizing controllers
of the observer, however, quickly converge on the true state. via parameterizations of stable nonlinear models.

---

# Page 13

13
A. Echo State Network and Convex Optimization B. Example
Here we describe a particular setting in which the data- We illustrate the approach on a simple discrete-time linear
driven optimization of nonlinear policies can be posed as system with transfer function
a convex problem. Suppose we wish to design a controller
0.3
solving (at least approximately) a problem of the form: = = =
T 0 T 1 −T 2 q2 2ρcos(ϕ)q+ρ2
−
minJ(ζ) s.t. c(ζ) 0 (59) with q the shift operator, ρ=0.8, and ϕ=0.2π. We consider
θ ≤
thetaskofminimizingtheℓ1 normoftheoutputinresponseto
where ζ is the response of the performance outputs to a stepdisturbances,whilekeepingthecontrolsignalubounded:
particular class of disturbances w, J is a convex objective u 5 for all t. This can be considered a data-driven
t
| | ≤
function, and c is a set of convex constraints, e.g. state and approach to an explicit model predictive control [82] with
control signal bounds. stability guarantees.
If we take as an echo state network, c.f. Section V-C: Training data is generated by a 25,000 sample piece-wise
Q
constant disturbance that has a hold time of 50 samples and a
q =f (q ,y˜), u˜ =g (q ,y˜,θ) magnitude uniformly distributed in the interval [-10, 10].
t+1 q t t t q t t
We construct a contracting model with n = 50 states
Q
where f is fixed and g is linearly parameterized by θ, i.e. and q = 500 neurons by randomly sampling a matrix X
q q (cid:104) (cid:105) ∈
R(2n+q)×(2n+q) with X 0, 4 and constructing a
g q (q t ,y˜ t ,θ)= (cid:88) θ i g q i(q t ,y˜ t ). C-RENviathemethodo ij ut ∼ line N inSe 2 c n ti + o q nV-A.Theremaining
i parameters are sampled from the Glorot normal distribution
[83]. For comparison, we construct a linear parameter of
Then has the representation Q
Q the form
(cid:88)
Q (y˜)= θ i Q i(y˜) q t+1 =A q q t +B q y˜ t , v t+1 =C q q t +D q y˜ t ,
i
(cid:104) (cid:105)
where A = λ A¯ with λ (0,1) and A¯ 0, 1 .
where i is a state-space model with dynamics f q and output q ρ(A¯) ∈ ij ∼ N 2n+q
gi. The Q n, we can perform data-driven controller optimization Note that A q is a stable matrix with a contraction rate of λ.
q We sample B from the Glorot normal distribution [83].
in the following way: q
TheresponsetotestinputsareshowninFig.9.Thebenefits
1) Construct (e.g. via random sampling, experiment) a
of learning a nonlinear parameter are that the control can
finite set of test signals wj. Q
respond aggressively to small disturbances, driving the output
2) Compute y˜j = wj for each j.
t T 2 quickly to zero, but respond less aggressively to large distur-
3) For each j, compute the response to y˜j:
bancestostaywithinthecontrolbounds.Incontrast,thelinear
control policy must respond proportionally to disturbances of
q =f (q ,y˜j), u˜ij =gi(q ,y˜j).
t+1 q t t t q t t all sizes. Since the control constraints require less aggressive
response to large disturbances, the linear controller must also
4) Construct the affine representation less aggressively to small disturbances, does not drive the
output to zero.
(cid:88)
ζj = wj + θ u˜ij.
0 i 1
T T
i
X. CONCLUSIONS
5) Solve the convex optimization problem:
In this paper we have introduced recurrent equilibrium
θ⋆ =argmin J(ζ)+R(θ) s.t. c(ζj) 0 networks (RENs) as a new model class for learning nonlin-
θ ≤ ear dynamical systems with built-in stability and robustness
constraints. The model set is flexible and admits a direct
where R(θ) is an optional regularization term.
parameterization, allowing learning of large-scale models via
The result will of course only be approximately optimal, genericunconstrainedoptimizationmethodssuchasstochastic
since wj are but a representative sample and the echo state gradient descent.
network provides only a finite-dimensional span of policies.
We have illustrated the benefits of the new model class
However it will be guaranteed to be stabilizing.
on problems in system identification, observer design, and
Remark 9: This framework can be extended to include control. On system identification benchmarks, the REN struc-
learning over all REN parameters, however the optimization ture outperformed the widely-used RNN and LSTM models
problemisnolongerconvex.Wehaverecentlyshownthatthis in terms of model fit while achieving far lower sensitivity to
amounts to learning over all stabilizing nonlinear controllers input perturbations. We further showed that the REN model
for a linear system [69] and extended the framework to learn architecture enables new approaches to nonlinear observer
robustly stabilizing controllers for uncertain systems [81]. design and optimization of nonlinear feedback controllers.

---

# Page 14

14
for some α < α¯. Left-multiplying by (cid:2) ∆x⊤ ∆w⊤(cid:3) and
Disturbance t t
7.5 OpenLoop right-multiplying by (cid:2) ∆x⊤ ∆w⊤(cid:3)⊤ , we obtain the following
t t
Linear
incremental Lyapunov inequality:
aREN
5.0
∆x 2 α2 ∆x 2 Γ(∆v ,∆w ) α2 ∆x 2. (64)
| t+1 |P ≤ | t |P − t t ≤ | t |P
2.5
where the second inequality follows by the incremental
0.0 quadratic constraint (62). Iterating over t gives (4) with
(cid:112)
K = σ¯/σ where σ¯ is the maximum singular value of P,
2.5
− and σ the minimum singular value.
0 100 200 300 400 500 600 The proof for the incremental IQC is similar: from (16)
Time Steps we obtain a non-strict version with α < α¯. Left multiplying
by (cid:2) ∆x⊤ ∆w⊤∆u⊤(cid:3) and right-multiplying by its transpose
Linear t t t
2 results in:
aREN
Contraints
∆x 2 α2 ∆x 2 Γ(∆v ,∆w )
0 | t+1 |P ≤ | t |P − t t
(cid:20)
∆y
(cid:21)⊤(cid:20)
Q
S⊤(cid:21)(cid:20)
∆y
(cid:21)
+ t t . (65)
∆u S R ∆u
t t
2
−
Since Γ(∆v ,∆w ) 0 from (62), and α<1 we have
t t
≥
4 (cid:20) ∆y (cid:21)⊤(cid:20) Q S⊤(cid:21)(cid:20) ∆y (cid:21)
− ∆x 2 ∆x 2 t t .
| t+1 |P −| t |P ≤ ∆u t S R ∆u t
0 100 200 300 400 500 600
Time Steps Telescoping sum of the above inequality yields the IQC (5)
with d(a,b) = (b a)⊤P(b a). Moreover, since Q 0,
Fig. 9: Output (top) and control signal (bottom) responses to taking ∆u =0 in − (65) reduce − s to (64) proving contracti ⪯ on.
t
stepdisturbancesfornonlinear(C-REN)andlineardata-driven
optimization of feedback controllers.
B. Proof of Theorem 2
We note that a REN has Lipschitz bound of γ if (28)
holds with Q = 1I,R = γI,S = 0. By taking Schur
APPENDIX −γ
complements and permuting the third and fourth columns and
A. Proof of Theorem 1 rows, the condition to be verified can be rewritten as:
 
Firstly, well-posedness follows directly from (15), since it α¯2P C⊤Λ A⊤ 0 C⊤
− 1 2
implies W 0 which is precisely (12).  ΛC W B⊤ ΛD D⊤ 
≻  − 1 1 − 12 21 
ToprovecontractionandincrementalIQCsweconsiderthe  A B P−1 B D⊤  0. (66)
incremental dynamics, i.e. differences between two sequences   0 D⊤ 1 Λ B⊤ γI 2 0 22  ≻
(xa,wa,va,ua) and (xb,wb,vb,ub), which we denote ∆x =  − 12 2 
t C D D 0 γI
xa xb and similarly for other variables. The incremental 2 21 22
dy t n − amic t s generated by (1) are Now, the upper-left quadrant is positive-definite via Schur
complement of (15). Hence, by taking γ sufficiently large,
    
∆x t+1 A B 1 B 2 ∆x t the condition (66) will be verified.
 ∆v t =C 1 D 11 D 12∆w t, (60)
∆y C D D ∆u
t 2 21 22 t C. Proof of Theorem 3
∆w t =σ(v t b+∆v t ) − σ(v t b). (61) Toshowwell-posedness,from(19)wehaveE+E⊤ P
≻ ≻
0 and =2Λ ΛD D⊤Λ 0 where D =Λ−1 .
To deal with the nonlinear element (61), we note that the W − 11 − 11 ≻ 11 D 11
The first inequality implies that E is invertible and thus (9)
constraint (14) can be rewritten as (σ(x) σ(y))(x y)
− − ≥ is well-posed. The second one ensures that the equilibrium
(σ(x) σ(y))2, and by taking a conic combinations of this
− network (8) is well-posed by the main result of [12].
inequalityforeachchannelwithmultipliersλ >0,weobtain
i To prove contraction, applying the inequality
the following incremental quadratic constraint:
α¯2E⊤ −1E E + E⊤ 1 [26, Sec. II] and a
P ⪰ − α¯2P
(cid:20) (cid:21)⊤(cid:20) (cid:21)(cid:20) (cid:21) Schur complement to (19) gives
∆v 0 Λ ∆v
Γ(∆v,∆w)= 0, (62)
∆w Λ 2Λ ∆w ≥ (cid:20) α¯2E⊤ −1E ⊤(cid:21) (cid:20) F⊤(cid:21) (cid:20) F⊤(cid:21)⊤
− P −C1 −1 0.
which is valid for any Λ=diag(λ ,...,λ ) D . −C 1 W − B1 ⊤ P B1 ⊤ ≻
1 q +
∈ By substituting F =EA, =EB , =EB , =ΛC
To prove contraction, we first note that if (15) holds then 1 1 2 2 1 1
B B C
and = ΛD into the above inequality, we obtain (15)
11 11
(cid:20) α2P C⊤Λ (cid:21) (cid:20) A⊤(cid:21) (cid:20) A⊤(cid:21)⊤ with D P =E⊤ −1E.Thus,Θ C isasetofC-RENs.Similarly,
− ΛC 1 − W 1 − B 1 ⊤ P B 1 ⊤ ⪰ 0 (63) we can show P that (20) implies (16) for R-RENs.

---

# Page 15

15
D. Proof of Proposition 1 [8] A.Raghunathan,J.Steinhardt,andP.Liang,“Certifieddefensesagainst
adversarialexamples,”inInternationalConferenceonLearningRepre-
With the factorization = L⊤L , (30) is equivalent to
Q − Q Q sentations(ICLR),2018.
[9] M. Fazlyab, A. Robey, H. Hassani, M. Morari, and G. J. Pappas,
R S −1S⊤ (L D L−⊤S⊤)⊤(L D L−⊤S⊤),
− Q ≻ Q 22 − Q Q 22 − Q “EfficientandaccurateestimationofLipschitzconstantsfordeepneural
networks.”inAdvancesinNeuralInformationProcessingSystems,2019.
which implies that R S −1S⊤ 0, hence L R is well- [10] S. Bai, J. Z. Kolter, and V. Koltun, “Deep equilibrium models,” in
− Q ≻
defined. AdvancesinNeuralInformationProcessingSystems,2019.
If p m, from (32) we have N⊤N I since [11] E.WinstonandJ.Z.Kolter,“Monotoneoperatorequilibriumnetworks,”
≥ ≺ inAdvancesinNeuralInformationProcessingSystems,2020.
(I+M)⊤(I+M) (I+M)⊤N⊤N(I+M) [12] M.Revay,R.Wang,andI.R.Manchester,“Lipschitzboundedequilib-
− riumnetworks,”arXiv:2010.01732,2020.
=2(M⊤+M) 4Z⊤Z =4(X⊤X +ϵI) 0. [13] L.ElGhaoui,F.Gu,B.Travacca,A.Askari,andA.Tsai,“Implicitdeep
− 3 3 3 3 ≻ learning,”SIAMJournalonMathematicsofDataScience,vol.3,no.3,
Similarly, for the case p<m we can obtain NN⊤ I from pp.930–958,2021.
(33), which also implies N⊤N I. Finally, by su ≺ bstituting [14] W.LohmillerandJ.-J.E.Slotine,“Oncontractionanalysisfornon-linear
≺ systems,”Automatica,vol.34,pp.683–696,1998.
(31) into (30) we have
[15] A. Megretski and A. Rantzer, “System analysis via integral quadratic
constraints,” IEEE Transactions on Automatic Control, vol. 42, no. 6,
R+SD 22 +D 2 ⊤ 2 S⊤+D 2 ⊤ 2Q D 22 =L⊤ R (I − N⊤N)L R ≻ 0. [16] p T p . . H 8 a 1 t 9 an – a 8 k 3 a 0 , , N 19 . 9 C 7 h . opra, M. Fujita, and M. W. Spong, Passivity-based
controlandestimationinnetworkedrobotics. Springer,2015.
E. Proof of Proposition 2 [17] M. Arcak, C. Meissen, and A. Packard, Networks of dissipative sys-
tems: compositional certification of stability, performance, and safety.
When the correctness condition (43) holds, we have that
Springer,2016.
xˆ t =x t for all t 0 if xˆ 0 =x 0 , i.e. the true state trajectory [18] K. Zhou, J. C. Doyle, K. Glover et al., Robust and Optimal Control.
isaparticularsolu ≥ tionoftheobserver.Butcontractionimplies PrenticehallNewJersey,1996,vol.40.
[19] A.vanderSchaft,L2-GainandPassivityinNonlinearControl,3rded.
thatallsolutionsoftheobserverconvergetoeachother.Hence
Springer-Verlag,2017.
when w =0 we have xˆ t x t as t . [20] J. M. Maciejowski, “Guaranteed stability with subspace methods,”
→ →∞
Now we consider the case where the correctness condition Systems&ControlLetters,vol.26,no.2,pp.153–156,Sep.1995.
[21] T. Van Gestel, J. A. Suykens, P. Van Dooren, and B. De Moor,
does not hold but its error is bounded by (44). The dynamics
“Identification of stable models in subspace identification by using
of ∆x:=xˆ x can be written as regularization,”IEEETransactionsonAutomaticControl,vol.46,no.9,
−
pp.1416–1420,2001.
∆x =f (xˆ ,u ,y ) f (x ,u )
t+1 o t t t − m t t [22] S. L. Lacy and D. S. Bernstein, “Subspace identification with guar-
=f (x +∆x ,u ,y ) f (x ,u ,y )+e anteedstabilityusingconstrainedoptimization,”IEEETransactionson
o t t t t o t t t t
− automaticcontrol,vol.48,no.7,pp.1259–1263,2003.
where e = f (x ,u ,y ) f (x ,u ). By the mean-value [23] U. Nallasivam, B. Srinivasan, V.Kuppuraj, M. N. Karim, and R. Ren-
t o t t t m t t
theorem, ∆x =F(z,u ) − ∆x +e where F = ∂[fo](z,u ) gaswamy, “Computationally efficient identification of global ARX pa-
t+1 t t t t ∂x t rameters with guaranteed stability,” IEEE Transactions on Automatic
forsomez.Bythetriangleinequality ∆x t+1 P F t ∆x t P + Control,vol.56,no.6,pp.1406–1411,Jun.2011.
| | ≤| |
e and by contraction F ∆x α∆x . So we have [24] D. N. Miller and R. A. De Callafon, “Subspace identification with
t P t t P t P
| | | | ≤ | | eigenvalueconstraints,”Automatica,vol.49,no.8,pp.2468–2473,2013.
∆x ∆x (α 1)∆x + e , [25] M. M. Tobenkin, I. R. Manchester, J. Wang, A. Megretski, and
t+1 P t P t P t P
| | −| | ≤ − | | | | R.Tedrake,“Convexoptimizationinidentificationofstablenon-linear
(α 1)∆x t P +√σ¯ρ. statespacemodels,”in49thIEEEConferenceonDecisionandControl
≤ − | | √ (CDC),2010.
From which it follows that the set ∆x σ¯ρ is forward- [26] M.M.Tobenkin,I.R.Manchester,andA.Megretski,“Convexparame-
| t | P ≤ 1−α terizationsandfidelityboundsfornonlinearidentificationandreduced-
invariant and exponentially attractive, since α 1 < 1. The
− order modelling,” IEEE Transactions on Automatic Control, vol. 62,
claimed result then follows from √σ ∆x t ∆ x P . no.7,pp.3679–3686,Jul.2017.
| |≤| |
[27] J.Umenberger,J.Wagberg,I.R.Manchester,andT.B.Scho¨n,“Max-
imum likelihood identification of stable linear dynamical systems,”
REFERENCES
Automatica,vol.96,pp.280–292,2018.
[1] Y.LeCun,Y.Bengio,andG.Hinton,“Deeplearning,”Nature,vol.521, [28] J. Umenberger and I. R. Manchester, “Specialized interior-point algo-
no.7553,pp.436–444,2015. rithmforstablenonlinearsystemidentification,”IEEETransactionson
[2] S. Levine, C. Finn, T. Darrell, and P. Abbeel, “End-to-end training of AutomaticControl,vol.64,no.6,pp.2442–2456,2018.
deepvisuomotorpolicies,”TheJournalofMachineLearningResearch, [29] S. M. Khansari-Zadeh and A. Billard, “Learning stable nonlinear dy-
vol.17,no.1,pp.1334–1373,2016. namicalsystemswithGaussianmixturemodels,”IEEETransactionson
[3] H.Yin,P.Seiler,M.Jin,andM.Arcak,“Imitationlearningwithstability Robotics,vol.27,no.5,pp.943–957,Oct.2011.
andsafetyguarantees,”IEEEControlSystemsLetters,vol.6,pp.409– [30] J. Miller and M. Hardt, “Stable recurrent models,” in International
414,2021. ConferenceonLearningRepresentations,2019.
[4] L. Brunke, M. Greeff, A. W. Hall, Z. Yuan, S. Zhou, J. Panerati, and [31] J.UmenbergerandI.R.Manchester,“Convexboundsforequationerror
A.P.Schoellig,“Safelearninginrobotics:Fromlearning-basedcontrol instablenonlinearidentification,”IEEEControlSystemsLetters,vol.3,
to safe reinforcement learning,” Annual Review of Control, Robotics, no.1,pp.73–78,Jan.2019.
andAutonomousSystems,vol.5,pp.411–444,2022. [32] G.ManekandJ.Z.Kolter,“Learningstabledeepdynamicsmodels,”in
[5] C. Szegedy, W. Zaremba, I. Sutskever, J. Bruna, D. Erhan, I. Good- AdvancesinNeuralInformationProcessingSystems,2019.
fellow, and R. Fergus, “Intriguing properties of neural networks,” in [33] M. Revay and I. Manchester, “Contracting implicit recurrent neural
InternationalConferenceonLearningRepresentations(ICLR),2014. networks: Stable models with improved trainability,” in Learning for
[6] A.RussoandA.Proutiere,“Towardsoptimalattacksonreinforcement DynamicsandControl. PMLR,2020,pp.393–403.
learningpolicies,”in2021AmericanControlConference(ACC). IEEE, [34] M.Revay,R.Wang,andI.R.Manchester,“Aconvexparameterizationof
2021,pp.4561–4567. robustrecurrentneuralnetworks,”IEEEControlSystemsLetters,vol.5,
[7] V.Tjeng,K.Y.Xiao,andR.Tedrake,“Evaluatingrobustnessofneural no.4,pp.1363–1368,2021.
networkswithmixedintegerprogramming,”inInternationalConference [35] M.Cheng,J.Yi,P.-Y.Chen,H.Zhang,andC.-J.Hsieh,“Seq2sick:Eval-
onLearningRepresentations(ICLR),2018. uating the robustness of sequence-to-sequence models with adversarial

---

# Page 16

16
examples.”inAssociationfortheAdvancementofArtificialIntelligence, [61] E. K. Ryu and S. Boyd, “Primer on monotone operator methods,”
2020,pp.3601–3608. AppliedandComputationalMathematics,vol.15,no.1,pp.3–43,2016.
[36] P.L.Bartlett,D.J.Foster,andM.J.Telgarsky,“Spectrally-normalized [62] I.Goodfellow,Y.Bengio,andA.Courville,Deeplearning. MITpress,
marginboundsforneuralnetworks,”inAdvancesinNeuralInformation 2016.
ProcessingSystems,2017,pp.6240–6249. [63] Y.-C. Chu and K. Glover, “Bounds of the induced norm and model
[37] S.ZhouandA.P.Schoellig,“Ananalysisoftheexpressivenessofdeep reduction errors for systems with repeated scalar nonlinearities,” IEEE
neuralnetworkarchitecturesbasedontheirLipschitzconstants,”arXiv TransactionsonAutomaticControl,vol.44,no.3,pp.471–483,1999.
preprintarXiv:1912.11511,2019. [64] F. J. D’Amato, M. A. Rotea, A. Megretski, and U. Jo¨nsson, “New
[38] T. Huster, C.-Y. J. Chiang, and R. Chadha, “Limitations of the Lip- resultsforanalysisofsystemswithrepeatednonlinearities,”Automatica,
schitz constant as a defense against adversarial examples,” in Joint vol.37,no.5,pp.739–747,2001.
EuropeanConferenceonMachineLearningandKnowledgeDiscovery [65] V.V.KulkarniandM.G.Safonov,“Allmultipliersforrepeatedmono-
inDatabases. Springer,2018,pp.16–29. tonenonlinearities,”IEEETransactionsonAutomaticControl,vol.47,
[39] H. Qian and M. N. Wegman, “L2-nonexpansive neural networks,” in no.7,pp.1209–1212,2002.
InternationalConferenceonLearningRepresentations(ICLR),2019. [66] B. Wahlberg and P. M. Ma¨kila¨, “On approximation of stable linear
[40] H. Gouk, E. Frank, B. Pfahringer, and M. J. Cree, “Regularisation of dynamical systems using Laguerre and Kautz functions,” Automatica,
neuralnetworksbyenforcingLipschitzcontinuity,”MachineLearning, vol.32,no.5,pp.693–708,May1996.
vol.110,no.2,pp.393–416,2021. [67] M.SchoukensandK.Tiels,“Identificationofblock-orientednonlinear
[41] R.S.SuttonandA.G.Barto,ReinforcementLearning:AnIntroduction. systems starting from linear approximations: A survey,” Automatica,
MITpress,2018,vol.2. vol.85,pp.272–292,2017.
[42] A.RussoandA.Proutiere,“Optimalattacksonreinforcementlearning [68] F. Giri and E.-W. Bai, Block-oriented nonlinear system identification.
policies,”arXiv:1907.13548,2019. Springer,2010,vol.1.
[43] Y. Kawano and M. Cao, “Design of privacy-preserving dynamic con- [69] R. Wang, N. H. Barbara, M. Revay, and I. R. Manchester, “Learning
trollers,” IEEE Transactions on Automatic Control, vol. 65, no. 9, pp. over all stabilizing nonlinear controllers for a partially-observed linear
3863–3878,Sep.2020. system,”IEEEControlSystemsLetters,vol.7,pp.91–96,2023.
[44] A. Virmaux and K. Scaman, “Lipschitz regularity of deep neural [70] S. Boyd and L. Chua, “Fading memory and the problem of approxi-
networks: analysis and efficient estimation,” in Advances in Neural matingnonlinearoperatorswithVolterraseries,”IEEETransactionson
InformationProcessingSystems,vol.31,2018. circuitsandsystems,vol.32,no.11,pp.1150–1161,1985.
[45] M. Fazlyab, M. Morari, and G. J. Pappas, “Safety verification and [71] J.Noe¨landM.Schoukens,“F-16aircraftbenchmarkbasedonground
robustness analysis of neural networks via quadratic constraints and vibrationtestdata,”WorkshoponNonlinearSystemIdentificationBench-
semidefinite programming,” IEEE Transactions on Automatic Control, marks,pp.15–19,2017.
vol.67,no.1,pp.1–15,2020. [72] M.SchoukensandJ.Noe¨l,“Wiener-hammersteinbenchmarkwithpro-
[46] P. Pauli, A. Koch, J. Berberich, P. Kohler, and F. Allgo¨wer, “Training cessnoise,”WorkshoponNonlinearSystemIdentificationBenchmarks,
robustneuralnetworksusingLipschitzbounds,”IEEEControlSystems pp.19–23,2017.
Letters,vol.6,pp.121–126,2021. [73] S. Hochreiter and J. Schmidhuber, “Long short-term memory,” Neural
[47] R. Wang and I. R. Manchester, “Direct parameterization of Lipschitz- computation,vol.9,pp.1735–1780,1997.
boundeddeepnetworks,”InternationalConferenceonMachineLearn- [74] A. Astolfi, D. Karagiannis, and R. Ortega, Nonlinear and Adaptive
ing(ICML),2023. ControlwithApplications. SpringerScience&BusinessMedia,2007.
[48] F. Ferraguti, N. Preda, A. Manurung, M. Bonfe`, O. Lambercy, [75] H. K. Khalil, High-Gain Observers in Nonlinear Feedback Control.
R. Gassert, R. Muradore, P. Fiorini, and C. Secchi, “An energy tank- SIAM,2017.
based interactive control architecture for autonomous and teleoperated [76] P.Bernard,ObserverDesignforNonlinearSystems. Springer,2019.
robotic surgery,” IEEE Transactions on Robotics, vol. 31, no. 5, pp. [77] R.Featherstone,RigidBodyDynamicsAlgorithms. Springer,2014.
1073–1088,Oct.2015. [78] B.H.GildingandR.Kersner,TravellingWavesinNonlinearDiffusion-
[49] E. Shahriari, A. Kramberger, A. Gams, A. Ude, and S. Haddadin, ConvectionReaction. Birkhauser,2012,vol.60.
“Adaptingtocontacts:Energytanksandtaskenergyforpassivity-based [79] T. Meurer, “On the extended Luenberger-type observer for semilinear
dynamic movement primitives,” in 2017 IEEE-RAS 17th International distributed-parameter systems,” IEEE Transactions on Automatic Con-
ConferenceonHumanoidRobotics(Humanoids),2017,pp.136–142. trol,vol.58,no.7,pp.1732–1743,2013.
[50] I.R.Manchester,“Contractingnonlinearobservers:Convexoptimization [80] S. P. Boyd and C. H. Barratt, Linear controller design: limits of
andlearningfromdata,”in2018AmericanControlConference(ACC). performance. PrenticeHall,1991.
IEEE,2018,pp.1873–1880. [81] R.WangandI.R.Manchester,“Youla-REN:Learningnonlinearfeed-
[51] B. Yi, R. Wang, and I. R. Manchester, “Reduced-order nonlinear backpolicieswithrobuststabilityguarantees,”in2022AmericanControl
observers via contraction analysis and convex optimization,” IEEE Conference(ACC),2022,pp.2116–2123.
TransactionsonAutomaticControl,vol.67,no.8,pp.4045–4060,2021. [82] A. Alessio and A. Bemporad, “A survey on explicit model predictive
[52] D. Youla, H. Jabr, and J. Bongiorno, “Modern Wiener-Hopf design of control,” in Nonlinear Model Predictive Control: Towards New Chal-
optimalcontrollers–PartII:Themultivariablecase,”IEEETransactions lenging Applications, ser. Lecture Notes in Control and Information
onAutomaticControl,vol.21,no.3,pp.319–338,Jun.1976. Sciences, L. Magni, D. M. Raimondo, and F. Allgo¨wer, Eds. Berlin,
[53] J. P. Hespanha, Linear Systems Theory. Princeton university press, Heidelberg:Springer,2009,pp.345–369.
2018. [83] X. Glorot and Y. Bengio, “Understanding the difficulty of training
[54] K. Fujimoto and T. Sugie, “Characterization of all nonlinear stabiliz- deepfeedforwardneuralnetworks,”in13thinternationalconferenceon
ing controllers via observer-based kernel representations,” Automatica, artificialintelligenceandstatistics. JMLRWorkshopandConference
vol.36,no.8,pp.1123–1135,Aug.2000. Proceedings,2010,pp.249–256.
[55] S.BurerandR.D.Monteiro,“Anonlinearprogrammingalgorithmfor
solvingsemidefiniteprogramsvialow-rankfactorization,”Mathematical
Programming,vol.95,no.2,pp.329–357,2003.
[56] D.P.KingmaandJ.Ba,“Adam:AMethodforStochasticOptimization,”
InternationalConferenceforLearningRepresentations(ICLR),2017.
[57] M.BuehnerandP.Young,“Atighterboundfortheechostateproperty,”
IEEE Transactions on Neural Networks, vol. 17, no. 3, pp. 820–824,
May2006.
[58] I. B. Yildiz, H. Jaeger, and S. J. Kiebel, “Re-visiting the echo state
property,”NeuralNetworks,vol.35,pp.1–9,Nov.2012.
[59] N. H. Barbara, M. Revay, R. Wang, J. Cheng, and I. R. Manchester,
“Robustneuralnetworks.jl: A package for machine learning and data-
drivencontrolwithcertifiedrobustness,”arXiv:2306.12612,2023.
[60] M.Revay,R.Wang,andI.R.Manchester,“Recurrentequilibriumnet-
works:Unconstrainedlearningofstableandrobustdynamicalmodels,”
in 60th IEEE Conference on Decision and Control (CDC), 2021, pp.
2282–2287.