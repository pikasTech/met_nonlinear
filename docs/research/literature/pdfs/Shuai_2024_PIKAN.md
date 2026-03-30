# Shuai_2024_PIKAN

SHUAIH.,LIF.,PHYSICS-INFORMEDKOLMOGOROV-ARNOLDNETWORKS... 1
Physics-Informed Kolmogorov-Arnold Networks for
Power System Dynamics
Hang Shuai, Member, IEEE, and Fangxing Li, Fellow, IEEE
Abstract—Thispaperpresents,forthefirsttime,aframework underlying physical model, resulting in significantly reduced
forKolmogorov-ArnoldNetworks(KANs)inpowersystemappli- computation times and a lesser need for training data. Re-
cations.InspiredbytherecentlyproposedKANarchitecture,this
searchers further proposed a practical framework for identi-
paper proposes physics-informed Kolmogorov-Arnold Networks
fying essential features of nonlinear voltage dynamics. This
(PIKANs), a novel KAN-based physics-informed neural network
(PINN) tailored to efficiently and accurately learn dynamics approach converts PINNs into a mixed-integer linear program
within power systems. The PIKANs present a promising alter- [10]. It enables adjustment of the neural network’s output
native to conventional Multi-Layer Perceptrons (MLPs) based conservativeness concerning stability boundaries, eliminating
PINNs, achieving superior accuracy in predicting power system
the necessity for exhaustive time-domain simulations.
dynamics while employing a smaller network size. Simulation
Despite promising results in designing PINNs for power
results on a single-machine infinite bus system and a 4-bus 2-
generator system underscore the accuracy of the PIKANs in systemdynamics,thereremainssignificantroomforimprove-
predicting rotor angle and frequency with fewer learnable pa- ment in the accuracy of the learned dynamic models. For
rameters than conventional PINNs. Furthermore, the simulation instance, the PINNs agent developed in [9], exhibits relative
results demonstrate PIKANs’ capability to accurately identify
L errors of 2.37% between the exact and predicted solutions
2
uncertain inertia and damping coefficients. This work opens up
for the rotor angle of a SMIB power system. When used
a range of opportunities for the application of KANs in power
systems, enabling efficient determination of grid dynamics and to identify the generator inertia constant and the damping
precise parameter identification. coefficient of a power system, the mean error of parameter
identification of PINNs would reach around 50% when only
Index Terms—Kolmogorov-Arnold Networks (KANs), power
system dynamics, deep learning, swing equation, physics- limited measurements (such as rotor angle) are available
informed neural network (PINN). [11]. Furthermore, the aforementioned PINNs agent struggles
to effectively learn both the stable and unstable dynamics
of the same power system. This limitation necessitates the
I. INTRODUCTION
use of distinct, trained PINNs to achieve high accuracy in
DEEPlearning(DL)hasdemonstratedremarkablesuccess stable and unstable regimes [9]. In this work, inspired by
in addressing complex tasks, particularly in fields where recently proposed Kolmogorov-Arnold Networks (KANs) in
precise mathematical models are difficult to establish, such [12],weproposephysics-informedKANs(PIKANs)algorithm
as computer vision, natural language processing , protein for accurately predicting power system angular and frequency
structure prediction , and medical image analysis [1]. In the dynamics that reduces dependency on training data and en-
power sector, DL has also increasingly been investigated for ables a more smaller number of learnable parameter in neural
applications such as renewable energy forecasting [2], fault networks.
detection[3],powersystemstabilityassessment[4],reflecting Current DL architectures such as deep neural networks
its growing influence and great application potential in future (DNNs), recurrent neural networks (RNNs), convolutional
power grids. neural networks (CNNs) and PINNs, largely rely on Multi-
Regarding power system dynamics, significant efforts have Layer Perceptrons (MLPs) [13]. MLPs are fully connected
been made to develop various data-driven algorithms for neural networks featuring fixed activation functions in neu-
the online identification of power system dynamics [5]–[7]. rons, while weights associated with network connections are
Among these, DL techniques have been increasingly utilized adjusted using backpropagation techniques during training.
[8]. However, these DL-based approaches often lacked inte- Further, universal approximation theorems [14], [15] imply
gration with the underlying power system model. As a result, that MLPs are universal approximators, which can represent a
they relied heavily on the quality and quantity of training wide variety of interesting functions with appropriate weights
data, necessitating large datasets and complex neural network andactivationfunctions.However,MLPsbasedDLtechniques
architectures. Considering this, researchers futher proposed face challenges such as the requirement for large training
physics-informedneuralnetwork(PINN)basedalgorithmsfor datasets, catastrophic forgetting [16], and a lack of inter-
power system dynamic identification. For example, in [9], pretability[17](oftenreferredtoasthe”blackbox”problem).
a PINN approach was developed to learn the rotor angle KANs [12], promising alternatives to MLPs, also feature
and frequency dynamics of a single-machine infinite bus fully-connectednetworkstructures.UnlikeMLPs,KANsplace
(SMIB) power system. The PINN based method leverages the learnable activation functions on the edges, which usually
allowmuchsmallercomputationgraphsthanMLPsandcould
H.ShuaiandF.LiarewiththeDepartmentofElectricalEngineeringand reach more accurate learning results at the same time. While
ComputerScience,UniversityofTennessee,Knoxville,TN,37996,USA.(e-
MLPs have the potential to learn generalized additive struc-
mail:hshuai1@utk.edu;fli6@utk.edu)
ThisworkwassupportedinpartbytheCURENTresearchcenter. tures, they often struggle with efficiently approximating ex-
4202
guA
31
]YS.ssee[
1v05660.8042:viXra

SHUAIH.,LIF.,PHYSICS-INFORMEDKOLMOGOROV-ARNOLDNETWORKS... 2
ponential and sine functions using traditional activation func- P is the electrical power output (p.u.) of the ith generator,
ei
tions,suchasReLU.Incontrast,KANsexcelinlearningboth which can be calculated by the following equation [19]:
compositional structures and univariate functions effectively,
n
(cid:88)
thereby significantly outperforming MLPs [12]. Considering P = V V [B ·sin(θ −θ )+G ·cos(θ −θ )] (2)
ei i j ij i j ij i j
sine and cosine functions are fundametal funcations in power
j=1
systemdynamicsmodels,soKANswouldhavegreatpotential
where B and G are the susceptance and conductance of
tobemoreeffectiveatrepresentingdynamicsinpowersystems ij ij
the transmission line between bus i and j, respectively. V
than MLPs. In summary, KANs are mathematically sound, i
and V represent the voltage magnitudes at bus i and bus j,
accurateandinterpretable,whichofferarangeofopportunities j
respectively.
in power systems by precisely and adaptively determining
Fortransmissionsystems,whenthelinereactanceX greatly
grid dynamics as described by differential-algebraic equations
exceeds the resistance R, and assuming the bus voltage is 1
(DAEs).
p.u., equation (2) can be simplified to:
ThisisthefirstworktoproposetheuseofKANsforpower
n
systemapplications.Specifically,weutilizetheswingequation (cid:88)
P = B ·sin(θ −θ ) (3)
inpowersystemsasanexampletodemonstratetheirpotential. ei ij i j
j=1
We also demonstrate the proposed method can be used to
estimate uncertain inertia and damping coefficients. The main Forthefrequencydependentloadi,thefrequencydynamics
contributions of this work can be summarized as follows: in equation (1) can be simplified to:
• For the first time, we present a framework that integrates P mi −P ei −D i ·ω i =0 (4)
KANs with the PINNs architecture for power system
applications, and PIKAN algorithms for power system
where ω
i
= d
d
θ
t
i.
Therefore, the system dynamics can be described by equa-
dynamics are developed. We propose a PIKAN training
tions (1) and (4), which can be expressed in the form of a
procedure that leverages the power system swing equa-
DAE system:
tion model to reduce data dependency and achieve high
accuracy. x˙ =h(x ,y,p;λ)
sys sys
• Theperformanceoftheproposedmethodisdemonstrated 0=g(x ,y,p;λ) (5)
sys
on a SMIB system and a 4-bus 2-generator system.
P ∈[Pmin,Pmax],t∈[0,T]
The simulation results show that PIKANs achieve higher m m m
accuracy in solving the DAEs of power systems with where x = [θ;ω] is the power system state variables
sys
smallerneuralnetworksizecomparedtotraditionalMLP- vector. y = [P ] is the algebraic variables vector. p = [P ]
e m
based PINNs. represents the power system input variables. λ = [M;D;B]
This paper is organized as follows: Section II introduces is the parameter of the power system.
the power system dynamic model investigated in this work. In this work, we focus on using PIKANs to learn dynamics
SectionIIIpresentsKANsandtheframeworkdesignationthat described by equation (5), and identify uncertain inertia and
integrates KANs with the PINNs architecture for the power damping parameters in λ.
system dynamic application. Section IV shows numerical
simulationresultsonthetwotestingsystemsdemonstratingthe III. PHYSICS-INFORMEDKOLMOGOROV-ARNOLD
performance of the proposed algorithm. Section V discusses NETWORKSFORPOWERSYSTEMDYNAMICS
thefindingsandlimitationsofthiswork.SectionVIconcludes
A. Kolmogorov-Arnold Networks
the paper.
BasedonKolmogorov-ArnoldRepresentationtheorem[20],
foramultivariatecontinuousfunctionf onaboundeddomain,
II. POWERSYSTEMDYNAMICMODEL
it can be represented by a finite composition of continuous
Power system dynamics are described by swing equations. functions of a single variable and the binary operation of
By assuming the bus voltage magnitudes to be 1 per unit addition, as given by the following equation:
(p.u.), and neglecting the reactive power flows, the frequency
2k+1 k
dynamicsofeachgeneratoricanbedescribedbythefollowing f(x)=f(x ,x ,··· ,x )= (cid:88) Φ ( (cid:88) ϕ (x )) (6)
1 2 k q q,p p
equation [18]:
q=1 p=1
where ϕ : [0,1]→R and Φ : R→R. x is the input vector.
dθ q,p q
i =ω The theorem shows that learning a high-dimensional function
dt i
(1) f can be boiled down to learning a polynomial number of 1D
dω
M · i =P −P −D ·ω univariate functions ϕ and Φ . Actually, equation (6) can
i dt mi ei i i q,p q
be treated as a two layer network having a shape of [n,2n+
whereθ andω arethevoltageangleandangularfrequencyof 1,1], which has two-layer nonlinearities. However, these 1D
i i
the generator i (also connected to bus i), respectively. t is the functionscanbenon-smoothandevenfractal,sotheymaynot
time index. M and D are the inertia and damping constant be learnable in practice [21]. Thus, the theorem was thought
i i
ofthegeneratori,respectively.P isthenetpowerinjection. to be practically useless in machine learning.
mi

SHUAIH.,LIF.,PHYSICS-INFORMEDKOLMOGOROV-ARNOLDNETWORKS... 3
To make the KAN easy to train, we can design activation
Output
𝑦 functions as given below:
Learnable activation
functions on edges ϕ(x )=w·(b(x )+spline(x )) (10)
l,i l,i l,i
𝜙2,1,1 𝜙2,2,1 𝜙2,3,1 𝜱𝟑
Layer 3 where w is a factor to control the overall magnitude of the
activation function. b(x) is a basis function which can be set
to
𝑥 2,1 𝑥 2,2 𝑥 2,3 b(x )=silu(x )= x l,i (11)
l,i l,i 1+e−xl,i
spline(x ) is the spline function which can be parametrized
l,i
𝜙1,1,1 𝜙1,1,2 𝜙1,1,3 𝜙1,2,1 𝜙1,2,2 𝜙1,2,3 𝜙1,2,1 𝜙1,2,2 𝜙1,2,3 Layer 2 as a linear combination of B-splines:
𝜱𝟐
(cid:88)
spline(x )= c ·B (x ) (12)
l,i s s l,i
s
𝑥 𝑥 𝑥
1,1 1,2 1,3
where B (x ) is the B-spline function. During the training
s l,i
process, spline(·) and w are trainable, and we can initialize
spline(·) by drawing B-spline coefficients c ∼ N(0,0.12)
Layer 1 s
𝜙0,1,1 𝜙0,1,2 𝜙0,1,3 𝜙0,2,1 𝜙0,2,2 𝜙0,2,3 𝜱𝟏 and w initialized according to the Xavier initialization. It
worthnotingthatotheractivationfunctionsotherthanB-spline
can be also utilized. For instance, to address computational
cost problem caused by training learnable B-Splines, [22]
𝑥 𝑥
0,1 0,2
developed a wavelet KAN architecture based on the work in
Input
[12].
Fig.1. Illustrationofa3-layerKANhavingashapeof[2,3,3,1]. For a L-layer KAN with layers of equal width N
(which means each layer has N neurons), there are in total
To enable the Kolmogorov-Arnold theorem for machine O(N2L(G+k )) ∼ O(N2LG) parameters, where k and G
b b
learning,[12]innovativalyproposedtheKANsarchitecture,as are the order and intervals of the spline. Contrarily, an MLP
illustrated in Fig. 1. In KANs, each 1D function of equation with depth L and width N typically requires O(N2L) param-
(6) are parametrized as a B-spline curve. Each B-spline curve eters, suggesting it might be more parameter-efficient than a
iswithlearnablecoefficientsoflocalB-splinebasisfunctions. KAN. However, KANs often operate effectively with much
It is worth noting that the activation functions are placed on smaller N than MLPs. This not only reduces parameter count
edges instead of nodes in Fig. 1. To generalize the network butalsoenhancesgeneralizationandfacilitatesinterpretability.
described by equation (6) to arbitrary widths and depths, [12]
furtherdefinedaKANlayerandstackingmoreKANlayersas
B. Physics-informed KANs for Power System Dynamics
needed. A KAN layer with n -dimensional inputs and n -
l l+1
dimensional outputs is defined as a matrix of 1D functions: PINNsareuniversalfunctionapproximatorsthatincorporate
the knowledge of physical laws governing a given dataset
Φ ={ϕ }, i=1,2,··· ,n ,j =1,2,··· ,n (7)
l l,j,i l l+1 into the neural network training process [23]. This approach
mitigates the need for large amounts of training data and the
where function ϕ has trainable parameters, which is the
l,j,i
activationfunctionthatconnectstheith neuroninthelth layer large network sizes typically required by traditional DNNs. In
and the jth neuron in the l+1th layer. l is the index of the PINNs,thearchitectureconsistsofaMLPwithaninputlayer,
layer. Therefore, the output of the lth layer of the KAN is severalfullyconnectedhiddenlayersfeaturingfixednonlinear
activation functions at each neuron, and an output layer. Each
x =Φ x layertransitioninvolvestheapplicationofaweightmatrixW
l+1 l l l
  and an activation function σ :
ϕ (·) ϕ (·) ··· ϕ (·) l
l,1,1 l,1,2 l,1,nl
=

  
ϕ l,2,
. . .
1 (·) ϕ l,2,
. . .
2 (·) ··· ϕ l,2,
. . .
nl (·) 
   x l ,
MLP(x)=(W
L−1
◦σ
L−1
◦W
L−2
◦σ
L−2
◦···◦W
1
◦σ
1
◦W
( 0 1
)
3
x
)
ϕ (·) ϕ (·) ··· ϕ (·) During the training process, these weights are adjusted to
l,nl+1,1 l,nl+1,2 l,nl+1,nl
(8) minimize an objective function, which typically penalizes the
difference between the neural network’s predictions and the
In this way, the output of a KAN network composed of L
actual labels of the training data.
layers can be written as
Basedon[23], thedynamicsofa physicalsystemgoverned
by parametrized and nonlinear partial differential equations
KAN(x)=(Φ ◦Φ ◦···◦Φ ◦Φ )x (9)
L−1 L−2 1 0
(PDEs), as shown in equation (14), can be effectively learned
wherex∈Rn0 istheinputvectorofthenetwork.Considering using PINNs.
all the above operations are differentiable, KANs can be
∂u
trained with back propagation techniques. +N[u;λ]=0,x∈Ω,t∈[0,T] (14)
∂t

SHUAIH.,LIF.,PHYSICS-INFORMEDKOLMOGOROV-ARNOLDNETWORKS... 4
1) PIKAN for capturing power system dynamics: When
𝐱
Multi-Layer 𝐮(𝑡,𝐱) the PIKAN is used for capturing power system dynamics,
Perceptrons we assume system parameters λ = [M;D;B] in equation
𝑡 (MLPs) 𝜕𝐮 𝒩[𝐮;𝛌] 𝐟(𝑡,𝐱) (5) are known. Therefore, the input of KAN is defined as
𝜕𝑡
x := P . By inputting P and time period of interest to the
m m
PIKAN in Fig. 3, it can predict the voltage angle of each
Fig. 2. General structure of a PINN [9], [23]: it predicts the output u(t,x)
giveninputsxandt. bus, i.e., u = θ(t,P m ). The output of KAN is fed into the
DAE module of the PIKAN to incorporate the power system
where u(t,x) is the solution of the PDE, depending on dynamics model, as described by equation (5), into the neural
time t and system input x. N[·;λ] is a nonlinear operator network architecture. The training objective is to optimize the
parametrized by λ. Ω is a subset of RD. [0,T] is the time activation function Φ to minimize loss function in equation
interval within which the system evolves. (16) or (17). Thus, by minimising the total loss function over
ForthetraditionalPINNs,wecandefineaphysicsinformed the KAN parameters, we can obtain the optimal KAN:
neuralnetworkf(t,x)asequation(15)andproceedbyapprox-
imating u(t,x) by a MLP, as illustrated in Fig. 2. Φ∗ =argmin(MSE u +MSE f ) (18)
Φ
∂u Solving the above highly non-convex and multi-parameter
f(t,x)= +N[u;λ] (15)
∂t optimization problem is challenge. We can use the LBFGS
or Adam optimiser to get a solution. We refer to the PIKAN
AsshowninFig.2,theMLPsusedforpredictingf(t,x)shares
using the loss function in equation (16) as PIKAN-I, and the
the same parameters as the MLPs used for predicting u(t,x),
PIKAN using the loss function in equation (17) as PIKAN-II.
with the distinction lying in their activation functions. The
In other words, PIKAN-I uses only the measurements of the
parameterscommontobothneuralnetworksareoptimizedby
voltage angle θ to train the KAN, while PIKAN-II uses both
minimizing the following loss function:
thevoltageangleθandtheangularfrequencyωmeasurements
loss =MSE +MSE to train the KAN. The proposed PIKAN for power system
I u f
1 (cid:88)
Nu
1 (cid:88)
Nf dynamics can be summarized in Algorithm 1.
= |u(tn,xn)−un|2+ |f(tn,xn)|2 2) PIKAN for power system parameter identification: Es-
N u u N f f
u n=1 f n=1 timating power system inertia and damping coefficients is
(16)
crucial for maintaining frequency stability. With the increased
where loss MSE corresponds to the initial and boundary
u installation of inverter-based resources (IBRs) in modern
data,whileMSE enforcesthestructureimposedbyequation
f power systems, the inertia and damping constants can vary
(14) at a finite set of collocation data points. The loss MSE
u with the control strategies employed, potentially affecting
iscalculatedoverN initialandboundarytrainingdatapoints,
u system stability and dynamic performance. Therefore, it is
andMSE iscalculatedoverN collocationpoints.u(tn,xn)
f f u u necessary to frequently estimate these parameters. When the
and f(tn,xn) are outputs of the PINN, while un is the lable
f f PIKANisusedforparameteridentification,MandDinλwill
value of the nth data point.
beunknowninequation(5).ThestructureoftheKANremains
Considering we can usually obtain the measurement of
unchanged, except that the M and D parameters are now
derivatives of u(t,x) with respect to the input t, we can also
considered as additional variables during the minimization
usethefollowinglossfunctiontotrainthePINNnetwork[11]:
of the loss function in the network training process. So, by
minimising the total loss function over the KAN parameters
loss =MSE +MSE
II u f
and power system uncertain parameters, we can obtain the
1 (cid:88)
Nu
optimal KAN:
= |u(tn,xn)−un|2+|u˙(tn,xn)−u˙n|2
N u u u u
u
n=1 Φ∗,M∗,D∗ =arg min (MSE u +MSE f ) (19)
1 (cid:88)
Nf Φ,M,D
+ |f(tn,xn)|2
N f f The proposed PIKAN for power system parameter identifica-
f
n=1
(17) tion can be summarized in Algorithm 2 (see Appendix).
By using automatic differentiation in PyTorch, we can easily Tomeasuretheperformanceduringthetraining,wedefined
obtain the derivatives of u(tn,xn) with respect to the input t. the mean squared error (MSE) of the predictions on the test
u u
To reduce the dependency on training data and enhance dataset as
the accuracy of the learned model in the PINNs-based power
system dynamic model, we designed the PIKAN, as shown in 1 N (cid:88)test
MSE = |θ −θ |2 (20)
Fig. 3. The primary difference from the traditional PINN is t N pred,n n
test
n=1
thatweutilizeKANtopredictu(t,x)basedontheinputstate
xandtimet.ThisPIKANofferstwoadvantages:1)increased where n is the index of the sampled test data point. θ
pred,n
modellearningaccuracy,and2)reducednetworksizewithout and θ are the predicted and real voltage angle vector of all
n
sacrificing accuracy, which will be demonstrated in Section the buses in the system, respectively. N is the total points
test
IV. of the test dataset.

SHUAIH.,LIF.,PHYSICS-INFORMEDKOLMOGOROV-ARNOLDNETWORKS... 5
𝑑
𝜕𝑡
𝐱 𝐮
𝑑2
𝐌𝑑
𝑑
2
𝑡
𝐮
2
+𝐃𝑑
𝜕
𝐮
𝑡
+𝐏𝑒- 𝐏𝑚 𝑀𝑆𝐸𝑓
𝑑𝑡2
Min
DAE Loss
𝑡 𝐮𝐱,𝑡 −𝐮𝑟𝑒𝑎𝑙(𝐱,𝑡)
𝑑
𝑀𝑆𝐸𝑢
𝜕𝑡 𝐮ሶ 𝐱,𝑡 −𝐮ሶ𝑟𝑒𝑎𝑙(𝐱,𝑡)
𝐾𝐴𝑁(𝐱,𝑡;𝜱) Boundary conditions (BC)
Dynamic No
prediction
𝜱∗
Yes
𝐿𝑜𝑠𝑠<𝜖
𝜱∗, M, D
Parameter
identification
Fig.3. Physics-InformedKolmogorov-ArnoldNetwork(PIKAN)forpowersystemdynamics.
Algorithm 1: PIKAN for capturing power system voltage angles of all buses from time 0 to T, respectively.
dynamics θt and θt are the actual and predicted voltage angle of
i pred,i
Data: Power system training and test dataset generated bus i at time t, respectively. ∥·∥ is the l2 norm for finite-
by time domain simulation; Power system dimensional vectors. For the inertia and damping coefficients
parameters (e.g., M, D, and B) identification performance, we defined the relative estimation
Result: KAN parameters error as:
Initialize KAN parameters: {Φ }L , G, and k ; |M −M | |D −D |
l l=1 b e = i pred,i , e = i pred,i (22)
Specify the loss function as equation (16) or (17); Mi M Di D
i i
Specify the initial & boundary training data points:
where M and M represent the actual and predicted
{(tn,xn),un}Nu , and specify collocation training i pred,i
u u n=1 inertia coefficients of the generator connected to bus i, re-
points: {(tn,xn)} Nf ;
f f n=1 spectively. D i and D pred,i represent the actual and predicted
Specify the test points: {(tn test ,xn test ),un test }N n= te 1 st; damping coefficients of bus i, respectively.
Set the maximum number of training steps N, and
learning rate; IV. SIMULATIONANDRESULTS
while n <N do
iter The performance of the proposed PIKANs for frequency
Forward pass of KAN to calculate all u(tn,xn). If
u u dynamics was demonstrated on a SMIB power system and a
loss function (17) is adopted, further calculate
4-bus 2-generator system, as shown in Fig. 4. To generate the
u˙(tn,xn) using automatic differentiation;
u u trainingandtestdatasets,weutilizedtimedomainsimulations
Calculate MSE based on the output of KAN and
u
implemented with SciPy in Python. The generated frequency
the measurements;
dynamicdataiswithatimestepof0.1sovertimewindow[0,
Calculate MSE based on the output of KAN and
f T] for each trajectory. The testing power system parameters
the power system dynamics given in equation (5);
are presented in Table 1 and Fig. 4. In the SMIB system,
Find the best KAN parameters to minimize the
we assume initial values for θ and ω to be 0.1 rad and
loss function using the LBFGS optimizer; 1 1
0.1 rad/s, respectively. The value of P ranges between 0.08
if n
iter
% 10 == 0 then m1
p.u. and 0.18 p.u., within which the SMIB system remains
Evaluate the performance of the PIKAN agent
stable. In this case setting, we generated 100 trajectories.
over the test points based on equation (20);
For each trajectory, the training and test datasets consist
end
of time intervals from 0 to 20 seconds with a 0.1-second
end
step, including the corresponding θ values at each time step
and the corresponding power injection value P . For the
m1
4-bus 2-generator system, similar to the setup in reference
To evaluate the predictive performance of the well-trained [11], we assume the system is in equilibrium at t = 0.
PIKANs,wedefinedtherelativepredictionerrorofthevoltage We then perturb the system with a constant input signal
angle as: P = a × [0.1,0.2,−0.1,−0.2] p.u. for t > 0 in each
m
trajectory. We generated 19 trajectories, with a ranging from
(cid:113)
∥θ0:T −θ0:T ∥ (cid:80)nb (cid:80)T (θt−θt )2 0.5to9.5inincrementsof0.5.Foreachtrajectory,thetraining
e = pred 2 = i=1 t=0 i pred,i and test datasets consist of time intervals from 0 to 5 seconds
θ ∥θ0:T∥ 2 (cid:113) (cid:80)nb (cid:80)T (θt)2 witha0.1-secondstep,includingthecorresponding[θ ,θ ,θ ,
i=1 t=0 i 1 2 3
(21) θ ]valuesateachtimestepandthecorrespondinginputsignal
4
where θ0:T and θ0:T represent the actual and predicted P . We conducted PIKANs training and performance testing
pred m

SHUAIH.,LIF.,PHYSICS-INFORMEDKOLMOGOROV-ARNOLDNETWORKS... 6
𝐵 =0.2 𝑝.𝑢.
12
Main
(a) G
grid
101
𝑃 1 𝑉 1 ∠𝜃 𝑉 2 ∠0 102
Bus @1 𝐵
13
=0.5 𝑝.𝑢. Bus @3 103
G 𝐷 3 104
(b) 𝐵 =1.2 𝑝.𝑢.
14 𝑀,𝐷
1 1 𝐵 34 =0.1 𝑝.𝑢. 𝐵 23 =1.4 𝑝.𝑢. 105
Bus @4 𝐵 =0.8 𝑝.𝑢. Bus @2 106
24
𝐷 4 G 𝑀 2 ,𝐷 2 107
Fig.4. Testingsystems:(a)SMIBpowersystem,(b)4-bussystemwithtwo 108
generator. 0 50 100 150 200 250 300 350
Steps
inPyTorchonanIntelXeon(R)Gold6248RCPU@3.00GHz
× 48 Windows based server with 64 GB RAM.
TABLEI
PARAMETERSOFTHECASESTUDIES
SMIBsystem 4-bus2-generatorsystem
Parameters
M (p.u.) D (p.u.) M (p.u.) D (p.u.)
Bus@1 0.4 0.15 0.3 0.15
Bus@2 — — 0.2 0.3
Bus@3 — — 0 0.25
Bus@4 — — 0 0.2
Note:Thelineparametersofthetestingsystemscanbefoundin
Fig. 4.
A. Data-driven solution of frequency dynamics
In the study of capturing frequency dynamics, the inertia
and damping coefficients of the testing systems are known
parameters. We evaulated the capability of the PIKANs to
accurately predict trajectories of θ and ω for uncertain power
injections.
1) SMIB system: For the SMIB system, we used a 2-layer
KAN with a shape of [2, 5, 1]. In each training step, the
randomly sampled time t and power injection P were fed
m1
into the KAN, and trained to minimize the loss function in
equation (16) for the PIKAN-I algorithm (or equation (17)
for the PIKAN-II algorithm). For both PIKAN-I and PIKAN-
II algorithms, the intervals of the B-spline were set to G =
10, and the order of the B-spline was set to k = 3. We
b
set N = 40, N = 800, and N = 20,100. The training
u f test
convergence process of the PIKAN-I algorithm is depicted
in Fig. 5. It shows that the PIKAN-I converges quickly and
achieves lower losses within hundreds of training steps. Fig.
6 depicts the comparison between the PIKAN-I predicted and
theactualtrajectoryoftheangleθandtheangularfrequencyω
of bus 1 in the SMIB system. The angular frequency ω in the
figure was calculated by differentiating the signal associated
with the voltage angle θ. In the left figures of Fig. 6, we
present the least accurate estimation of the voltage angle and
frequency trajectory, yielding a relative prediction error (e )
θ
of1.06%. Conversely,inthe rightfigures,we demonstratethe
most accurate estimation of the voltage angle and frequency
trajectory,achievingarelativepredictionerror(e )of0.014%.
θ
ssol
gniniarT
PDE loss (MSEf)
BC loss (MSEu) Test loss (MSEt)
Fig.5. TrainingconvergenceprocessofthePIKAN-Ialgorithmforcapturing
SMIBsystemfrequencydynamics.TheLBFGSoptimizerwasemployed,with
parameter maximum iteration set to 20. Thus, each optimization step in the
figurecontains20iterations.
1.50
1.25
1.00
0.75
0.50
0.25
0.00
0 5 10 15 20
)dar(
P = 0.18 p.u. P = 0.169 p.u.
1.50
1.25
1.00
0.75
0.50
0.25
0.00
0 5 10 15 20
0.4
0.3
0.2
0.1
0.0
0.1
0.2
0 5 10 15 20
Time (s)
)s/dar(
Exact Predicted
P = 0.18 p.u. P = 0.169 p.u.
0.4
0.3
0.2
0.1
0.0
0.1
0.2
0 5 10 15 20
Time (s)
Fig.6. Comparisonofthepredictedandexactsolutionforthevoltageangle
andfrequencywiththePIKAN-IforSMIBpowersystemdynamics.
The median value of the prediction error on voltage angle
over the 100 trajectories is 0.688%, which indicate that the
PIKAN-I is able to predict the trajectory of the angle with
high accuracy.
If we use measurements of both θ and ω to train the
KAN, denoted as the PIKAN-II algorithm, the accuracy of
the agent can be further improved, with the median value
of the prediction error on the voltage angle decreasing to
0.633% (see Table II). We also compared the performance of
the proposed method with the MLP-based PINNs for power
systems proposed in [9] and [11]. The prediction errors for
the 100 tested trajectories are presented in Fig. 7 and Table
II. The proposed method outperforms the traditional PINNs,
demonstratingtheeffectivenessofthePIKANsinlearningthe
dynamics of SMIB systems. From the results in Fig. 7, we
can observe that incorporating measurements of ω (i.e., using
the loss function defined in equation (17)) during training
improves the performance of the agent for both the PIKAN
and traditional PINN methods.

SHUAIH.,LIF.,PHYSICS-INFORMEDKOLMOGOROV-ARNOLDNETWORKS... 7
TABLEII
DYNAMICCAPTURINGSTUDYRESULTS:ESTIMATIONERROROFTHETRAJECTORYOFθ(t)
SMIBsystem 4-bus2-generatorsystem
Estimationerror
Max(%) Min(%) Median(%) Max(%) Min(%) Median(%)
PIKAN-I 1.06 0.014 0.688 4.85 0.043 4.64
PIKAN-II 1.53 0.184 0.633 1.94 0.040 0.538
PINN-I([9]) 2.30 0.057 1.96 6.35 0.151 5.03
PINN-II([11]) 1.48 0.206 0.800 5.98 0.076 2.59
2.0
1.5
1.0
0.5
0.0
PIKAN-I PIKAN-II PINN-I PINN-II
Methods
)%(
seirotcejart
001
detset
eht
fo
e
0.2
0.1
0.0
0.1
0.2
0.3
0.4
0 1 2 3 4 5
Fig. 7. Performance of the proposed method and the MLPs based PINNs
for the SMIB system. The parameters and hyperparameters setting is same
withreference[9].ForthePINN-IandPINN-II,wesetNu=40andN
f
=
8,000.
2)4-bus2-generatorsystem:Tofurthertesttheperformance
of the proposed method in capturing the dynamics of multi-
machinepowersystems,weevaluateditona4-bus2-generator
system as shown in Fig. 4 (b). For this case study, we
employed a 2-layer KAN with a structure of [5, 10, 4]. In
each training step, the randomly sampled time t and power
injection[P ,P ,P ,P ]arefedintotheKAN,which
m1 m2 m3 m4
isthentrainedtominimizethelossfunctioninequation(16)or
(17),ultimatelyoutputtingthevoltageanglesofthefourbuses
attimet.ForbothPIKAN-IandPIKAN-II,theintervalsofthe
B-spline were set to G=5, and the order of the B-spline was
set to k =3. We set N = 80, N = 4000, and N =969. b u f test
Fig. 8 depicts the comparison between the predicted and
the actual trajectory of the angle [θ , θ , θ , θ ] and the
1 2 3 4
frequency[ω ,ω ,ω ,ω ]of4busesinthesystem.Intheleft
1 2 3 4
figures of Fig. 8, we present the least accurate estimation of
the voltage angle and frequency trajectory, yielding a relative
predictionerror(e )of1.94%.Conversely,intherightfigures,
θ
we demonstrate the most accurate estimation of the voltage
angle and frequency trajectory, achieving a relative prediction
error (e ) of 0.04%. The median value of the estimation error
θ
onvoltageangleoverthe19trajectoriesis0.538%,indicating
that PIKAN-II can predict the trajectory of the angle with
high accuracy. In contrast, the traditional PINN-I and PINN-
II algorithms performed much worse, with median estimation
errors on the voltage angle of 5.03% and 2.59%, respectively.
The performance comparisons between PIKANs and PINNs
are summarized in Table II. The results on the 4-bus 2-
)dar(
P = [0.2, 0.4, -0.2, -0.4] p.u. P = [0.95, 1.9, -0.95, -1.9] p.u.
1.0
0.5
0.0
0.5
1.0
0 1 2 3 4 5
0.2
0.0
0.2
0.4
0.6
0.8
1.0
0 1 2 3 4 5
Time (s)
)s/dar(
bus@1 bus@2 bus@3 bus@4
P = [0.2, 0.4, -0.2, -0.4] p.u. P = [0.95, 1.9, -0.95, -1.9] p.u.
1
0
1
2
3
4
5
0 1 2 3 4 5
Time (s)
Fig. 8. Comparison of the predicted and exact solutions for the voltage
angleandfrequencyusingPIKAN-IIforthe4-bus2-generatorpowersystem
dynamics. Solid lines represent the exact trajectory, while dashed lines
representthepredictedtrajectorybyPIKAN-II.
generator system also demonstrate that the proposed method
outperforms traditional PINN-based approaches.
B. Data-driven inertia and damping coefficients identification
In the parameter identification study, the inertia and damp-
ingcoefficientsofthetestingsystemsareunknownparameters.
We assessed the capability of PIKANs to accurately estimate
these unknown parameters from observed trajectories.
The parameters and hyperparameters of the PIKANs for
assessing inertia and damping coefficients are the same as
those of the PIKANs agents in Section IV-A. Since the
neuralnetwork’sweightsareinitializedrandomly,weruneach
estimationofthefouralgorithms20times.Figs.9and10show
the distribution of parameter estimation errors on the 4-bus 2-
generatorsystemfortheproposedmethodandthecomparison
methods. PIKAN-I achieves a median relative error below
10% for evaluating the inertia and damping coefficients of
the system. In contrast, PIKAN-II demonstrates significantly
betterperformance,achievingamedianrelativeerrorofaround
1% for inertia coefficients and 0.1% for several damping
coefficients. The traditional PINNs, however, perform much
worse than the proposed methods. Additionally, we observed
that incorporating measurements of ω during training can
significantlyimprovetheparameterestimationaccuracyofthe
agent for both the PIKAN and traditional PINN methods.

SHUAIH.,LIF.,PHYSICS-INFORMEDKOLMOGOROV-ARNOLDNETWORKS... 8
102
101
100
101
102
M1 M2
)%(
rorrE
noitamitsE
evitaleR
Inertia Parameter Identification for the 4-Bus 2-Generator System
Method PINN-I PINN-II
PIKAN-I PIKAN-II
Fig.9. InertiacoefficientsestimationerrorsofPIKANsandPINNs.
102
101
100
101
102
D1 D2 D3 D4
)%(
rorrE
noitamitsE
evitaleR
101
102
103
104
105
102 103
Number of parameters
Damping Parameter Identification for the 4-Bus 2-Generator System
Method
PINN-I
PINN-II
PIKAN-I
PIKAN-II
Fig.10. DampingcoefficientsestimationerrorsofPIKANsandPINNs.
C. Number of network parameters vs. PIKAN performance
ResultsinTablesIIandIIIindicatethat,fortheSMIBcase,
PIKANs achieved greater accuracy in grid dynamic learning
while using only 41% of the network size of the PINNs.
Similarly, for the 4-bus 2-generator case, PIKANs achieved
higher accuracy while utilizing only 58% of the network size
of the PINNs.
For a L-layer KAN with layers of equal width N, there
are in total O(N2LG) parameters, and an MLP only needs
O(N2L)parametersforthesamenumberoflayersandwidth.
However, KANs typically achieve similar performance with a
much smaller N compared to MLPs. Fig. 11 illustrates the
scaling laws of losses as a function of the number of parame-
ters in both PIKANs and PINNs. The results demonstrate that
KANs exhibit steeper scaling laws than MLPs. This implies
that PIKANs can achieve comparable or even superior accu-
racyinpowersystemdynamiclearningwithfewerparameters
thanPINNs.Theimplicationsofthesefindingsaresignificant.
They suggest that while KANs may initially seem to require
moreparametersduetotheO(N2LG)scaling,theirabilityto
useasmallerN effectivelyreducestheoverallparametercount
needed for high performance. Consequently, PIKANs offer a
moreefficientandscalablesolutionforcomplexlearningtasks
inpowersystems,surpassingtraditionalMLP-basedPINNsin
terms of both accuracy and parameter efficiency.
D. Reduced data dependency
PIKANs introduce a KAN training framework designed
to leverage the inherent dynamics of power systems. Con-
sequently, compared to traditional DNNs without a physics-
informed architecture, PIKANs can significantly reduce the
required size of the training dataset. For the two testing
)tESM(
ssol
tseT
KAN [2, 5, 1] MLP (depth=3) MLP (depth=4)
MLP (depth=5) MLP (depth=6)
Fig.11. Scalinglawsoflossesagainstthenumberofparametersfordifferent
physics-informedneuralnetworksappliedtotheSMIBsystem.
6
5
4
3
2
1
0 0 100 200 300 400 500 600 700 800
Number of training data points Nu
)%(
no
rorre
noitamitsE
Deep neural network for SMIB system Deep neural network for 4-bus 2-generator system
PIKAN-II for SMIB system
PIKAN-II for 4-bus 2-generator system
PIKAN-II: Nu = 40
PIKAN-II: Nu = 80
Fig. 12. Performance comparison of traditional DNNs and PIKANs with
varyingnumbersoftrainingdatapoints.FortheSMIBcase,a[2,10,10,10,
10,10,1]DNNarchitectureisemployed.Forthe4-bussystem,a[5,30,30,
4]DNNarchitectureisutilized,andtheAdamoptimizerwasemployed.
systems in Table II, the performance of traditional DNNs,
employingidenticalarchitectureandparametersasthePINNs,
varies with the number of training data points, as illustrated
in Fig. 12. From the results, it is observed that PIKANs can
achieve similar or even better performance while requiring
only 10% of the training data points compared to traditional
DNNs.
V. DISCUSSION
Thispaperintroduces,forthefirsttimeinpowersystems,a
KAN-based PINN (i.e., PIKAN) approach that explicitly con-
siders the swing equations describing the frequency behavior
of grids. As a promising alternative to traditional MLPs, the
proposed PIKANs for power system dynamics can achieve
comparableorevenhigheraccuracywithfewerneuralnetwork
parameters compared to MLP-based PINNs. The advantage
of PIKANs is particularly significant given the challenges of
training large neural networks, such as large language models
(LLMs),whichareresource-intensiveandconsumesubstantial
amounts of energy. This opens up numerous opportunities
in power systems, as PIKANs can potentially be used to
accurately and efficiently solve DAEs in power grids. In
addition, PIKANs require only a very limited amount of
trainingdata.Forinstance,fortheSMIBsystem,PIKANsneed
only N = 40 points {(tn,xn),un}Nu } to train the agent.
u u u n=1
Even for a larger power system, such as the 4-bus 2-generator
system, PIKANs still need only N =80 training data points.
u
Althoughwerequiresignificantlymorecollocationpoints(for
example,N =800fortheSMIBcase)toevaluatetheMSE
f f
terminthelossfunctiongiveninequation(16),itisimportant

SHUAIH.,LIF.,PHYSICS-INFORMEDKOLMOGOROV-ARNOLDNETWORKS... 9
to note that this evaluation is not dependent on measured of complex physical systems, such as the dynamics of
voltage angle and angular frequency data. This means we can bulk power systems. However, in the case of the swing
generate any number of collocation points without needing to equations examined in this study, we observed that the
produce labels for those data points. symbolic formula provided by the well-trained PIKAN
SimilarwithtraditionalPINNs,PIKANshavethecapability does not accurately capture the frequency dynamics of
todirectlycomputethevoltageangleatanygiventimestept . the two testing systems, despite the PIKAN model itself
1
Incontrast,numericalmethodsmustintegratestartingfromthe precisely predicting the grid dynamics. This discrepancy
initial conditions at t = t and proceed sequentially to reach may stem from the limited library of symbolic formulas
0
t = t . This provides significant advantages over traditional available in the current version of KAN package in [27],
1
numerical integration methods. or perhaps the formula for the grid dynamics is not
In this study, our primary focus was on exploring how inherently symbolic.
PIKANs could achieve higher accuracy in learning power 4) Continual learning: One drawback of MLPs is their ten-
system dynamics while maintaining a smaller network size. dency to forget previously learned tasks when transition-
Theoretically, KANs outperform MLPs in terms of accuracy, ing from one task to another. Liu et al. [12] demonstrate
interpretability, and reduction of catastrophic forgetting. Nev- thatfora1Dregressiontask,KANsexhibitlocalplastic-
ertheless, to fully harness the potential of PIKANs, several ity and can prevent catastrophic forgetting by leveraging
challenges must be addressed. the locality of splines. However, the extent to which
1) Training and computing time: From the results presented KANscanavoidcatastrophicforgettinginmorecomplex
in Table III, it is evident that the training of PIKANs learning tasks, such as power system dynamics as ex-
requiresconsiderablymoretimecomparedtoPINNs.Liu ploredinthisstudy,remainsunclear.Inourinvestigation,
etal.[12]attributethisslowertrainingtotheinefficiency we observed that a well-trained PIKAN, initially trained
of current activation functions in batch computations. on data from stable scenarios (e.g., P ∈ [0.08,0.18]
m1
Despite the extended training duration, the superior per- p.u. for the SMIB case), tends to forget previously
formance and accuracy of PIKANs may justify the addi- learneddynamicswhenfurthertrainedondynamicsfrom
tional time investment, especially in scenarios requiring unstable scenarios (e.g., P ∈ [0.20,0.25] p.u. for
m1
high precision. After offline training, we evaluate the the SMIB case). Therefore, further investigation into the
PIKAN’s performance based on its online computational continual learning capabilities of the proposed PIKANs
speedrequiredtosolvetheDAEdefinedbyequation(5). is warranted in future research.
For19differentinitialconditionsofthe4-bus2-generator
VI. CONCLUSIONS
system,theode45solveraverages0.017secondstosolve
This is the first paper to propose physics-informed KANs
the swing equations across the time interval from 0
for power system applications. By integrating KAN with
seconds to 5 seconds, whereas PIKAN averages 0.024
PINN, we achieve higher accuracy in solving the differential-
seconds. In future research, we aim to explore tech-
algebraic equations of power systems with smaller neural
niques utilizing more efficient activation functions, such
network size compared to traditional MLP-based PINNs. In
as Jacobi polynomials proposed by [24], to substantially
our case studies, we showcased the effectiveness of the pro-
enhance training speeds. And primary investigation in
posedPIKANsinaccuratelycapturingthedynamicsofpower
[25] demonstrates that Jacobi polynomials can reduce
systems. Furthermore, we demonstrated their capability to
training times by two orders of magnitude compared to
identifyuncertainsysteminertiaanddampingparameters,with
KANs using B-spline activation functions in the context
highaccuracyusingalimitedsetoftrainingdatapoints.These
of solving specific PDEs.
results underscore the promising potential of the PIKANs
2) Accuracy:OursimulationresultsdemonstratedthatKAN-
for practical applications in power systems, opening up new
based PINNs exhibit higher accuracy compared to MLP-
avenues for their use.
based PINNs in modeling power system dynamics. Re-
searchers have also found that KANs generally achieve
APPENDIXA
greater accuracy than MLPs in most PDE problems [26].
However, whether KANs consistently outperform MLPs See Algorithm 2.
in various power dynamic problems requires further
investigation. Additionally, understanding why PIKANs REFERENCES
have higher accuracy than conventional PINNs warrants [1] M. I. Razzak,S. Naz, and A. Zaib, “Deep learningfor medical image
further exploration. One possible reason could be that processing: Overview, challenges and the future,” Classification in
BioApps:Automationofdecisionmaking,pp.323–350,2018.
KANsemploylearnableactivationfunctions,allowingfor
[2] T. Hong, P. Pinson, Y. Wang, R. Weron, D. Yang, and H. Zareipour,
more complex learned activations compared to the fixed “Energyforecasting:Areviewandoutlook,”IEEEOpenAccessJournal
activation functions (such as ReLU) used in MLPs. ofPowerandEnergy,vol.7,pp.376–388,2020.
[3] H.Jiang,J.J.Zhang,W.Gao,andZ.Wu,“Faultdetection,identification,
3) Interpretability: KANs have the potential to serve as
andlocationinsmartgridbasedondata-drivencomputationalmethods,”
foundational models for AI + Science due to their ac- IEEETransactionsonSmartGrid,vol.5,no.6,pp.2947–2956,2014.
curacy and interpretability [12]. With KANs, humans [4] C. Ren, Y.Xu, and R. Zhang, “An interpretabledeep learning method
forpowersystemtransientstabilityassessmentviatreeregularization,”
can interactively obtain the symbolic formula of the
IEEE Transactions on Power Systems, vol. 37, no. 5, pp. 3359–3369,
model’soutput,whichsignificantlyfacilitatestheanalysis 2022.

SHUAIH.,LIF.,PHYSICS-INFORMEDKOLMOGOROV-ARNOLDNETWORKS... 10
TABLEIII
TRAININGTIMEFORRESULTSGIVENINTABLEII
Orderof Intervalsof No.of Training Trainingtime
System Methods Networklayers
B-spline(k b) B-spline(G) parameters iterations (ms/iter.)
PIKAN-I [2,5,1] 3 10 195 7000 87.5
PIKAN-II [2,5,1] 3 10 195 7000 130
SMIBsystem
[2,10,10,10,
PINN-I([9]) – – 481 50000 0.54
10,10,1]
[2,10,10,10,
PINN-II([11]) – – 481 10000 3.41
10,10,1]
PIKAN-I [5,10,4] 3 5 720 3000 1225
4-Bus PIKAN-II [5,10,4] 3 5 720 3000 1390
2-GeneratorSystem PINN-I([9]) [5,30,30,4] – – 1234 50000 2.89
PINN-II([11]) [5,30,30,4] – – 1234 50000 3.78
Algorithm 2:PIKANforgridparameteridentification neural networks for power systems,” in 2020 IEEE power & energy
societygeneralmeeting(PESGM). IEEE,2020,pp.1–5.
Data: Power system training and test dataset generated
[10] G.S.Misyris,J.Stiasny,andS.Chatzivasileiadis,“Capturingpowersys-
by time domain simulation temdynamicsbyphysics-informedneuralnetworksandoptimization,”
Result: KAN parameters and estimated inertia M and in202160thIEEEConferenceonDecisionandControl(CDC),2021,
pp.4418–4423.
damping D parameters
[11] J. Stiasny, G. S. Misyris, and S. Chatzivasileiadis, “Physics-informed
Initialize KAN parameters: {Φ l }L l=1 , G, and k b ; neural networks for non-linear system identification for power system
Initialize inertia M and damping D parameters; dynamics,”in2021IEEEMadridPowerTech. IEEE,2021,pp.1–6.
[12] Z. Liu, Y. Wang, S. Vaidya, F. Ruehle, J. Halverson, M. Soljacˇic´,
Specify the loss function as equation (16) or (17);
T.Y.Hou,andM.Tegmark,“Kan:Kolmogorov-arnoldnetworks,”arXiv
Specify the initial & boundary training data points: preprintarXiv:2404.19756,2024.
{(tn,xn),un}Nu , and specify collocation training [13] Y.LeCun,Y.Bengio,andG.Hinton,“Deeplearning,”nature,vol.521,
u u n=1
points: {(tn,xn)} Nf ; no.7553,pp.436–444,2015.
f f n=1 [14] T.ChenandH.Chen,“Universalapproximationtononlinearoperators
Specify the test points: {(tn ,xn ),un }Ntest; byneuralnetworkswitharbitraryactivationfunctionsanditsapplication
test test test n=1
to dynamical systems,” IEEE transactions on neural networks, vol. 6,
Set the maximum number of training steps N, and
no.4,pp.911–917,1995.
learning rate; [15] Y. Lu and J. Lu, “A universal approximation theorem of deep neural
while n <N do networks for expressing probability distributions,” Advances in neural
iter
Forward pass of KAN to calculate all u(tn,xn). If informationprocessingsystems,vol.33,pp.3094–3105,2020.
u u [16] R. Kemker, M. McClure, A. Abitino, T. Hayes, and C. Kanan, “Mea-
loss function (17) is adopted, further calculate
suringcatastrophicforgettinginneuralnetworks,”inProceedingsofthe
u˙(tn,xn) using automatic differentiation; AAAIconferenceonartificialintelligence,vol.32,no.1,2018.
u u
Calculate MSE based on the output of KAN and [17] F.-L.Fan,J.Xiong,M.Li,andG.Wang,“Oninterpretabilityofartificial
u neuralnetworks:Asurvey,”IEEETransactionsonRadiationandPlasma
the measurements;
MedicalSciences,vol.5,no.6,pp.741–760,2021.
Calculate MSE based on the output of KAN and [18] H.Shuai,B.She,J.Wang,andF.Li,“Safereinforcementlearningfor
f
the power system dynamics given in equation (5); grid-forminginverterbasedfrequency regulationwithstabilityguaran-
tee,” Journal of Modern Power Systems and Clean Energy, pp. 1–8,
Find the best KAN parameters and inertia M and
2024.
damping D parameters to minimize the loss [19] V.Vittal,J.D.McCalley,P.M.Anderson,andA.Fouad,PowerSystem
function using the LBFGS optimizer; ControlandStability,3rdEdition. JohnWiley&Sons,2019.
[20] A. N. Kolmogorov, On the representation of continuous functions of
if n % 10 == 0 then
iter severalvariablesbysuperpositionsofcontinuousfunctionsofasmaller
Evaluate the performance of the PIKAN agent numberofvariables. AmericanMathematicalSociety,1961.
over the test points based on equation (20); [21] T. Poggio, A. Banburski, and Q. Liao, “Theoretical issues in deep
networks,”ProceedingsoftheNationalAcademyofSciences,vol.117,
end
no.48,pp.30039–30045,2020.
end [22] Z. Bozorgasl and H. Chen, “Wav-kan: Wavelet kolmogorov-arnold
networks,”arXivpreprintarXiv:2405.12832,2024.
[23] M.Raissi,P.Perdikaris,andG.E.Karniadakis,“Physicsinformeddeep
learning (part i): Data-driven solutions of nonlinear partial differential
equations,”arXivpreprintarXiv:1711.10561,2017.
[5] S.Sinha,S.P.Nandanoori,andE.Yeung,“Datadrivenonlinelearning
[24] SynodicMonth, “Chebykan,” https://github.com/SynodicMonth/
of power system dynamics,” in 2020 IEEE Power & Energy Society
ChebyKAN,2024.
GeneralMeeting(PESGM),2020,pp.1–5.
[25] K.Shukla,J.D.Toscano,Z.Wang,Z.Zou,andG.E.Karniadakis,“A
[6] R.Satheesh,N.Chakkungal,S.Rajan,M.Madhavan,andH.H.Alhelou,
comprehensive and fair comparison between mlp and kan representa-
“Identificationofoscillatorymodesinpowersystemusingdeeplearning
tions for differential equations and operator networks,” arXiv preprint
approach,”IEEEAccess,vol.10,pp.16556–16565,2022.
arXiv:2406.02917,2024.
[7] N. Bhusal, R. M. Shukla, M. Gautam, M. Benidris, and S. Sengupta,
[26] Y. Wang, J. Sun, J. Bai, C. Anitescu, M. S. Eshaghi, X. Zhuang,
“Deep ensemble learning-based approach to real-time power system
T.Rabczuk,andY.Liu,“Kolmogorovarnoldinformedneuralnetwork:
state estimation,” International Journal of Electrical Power & Energy
Aphysics-informeddeeplearningframeworkforsolvingpdesbasedon
Systems,vol.129,p.106806,2021.
kolmogorovarnoldnetworks,”arXivpreprintarXiv:2406.11045,2024.
[8] Y.Zhang,X.Shi,H.Zhang,Y.Cao,andV.Terzija,“Reviewondeep
[27] KindXiaoming,“pykan,”https://github.com/KindXiaoming/pykan,2024,
learningapplicationsinfrequencyanalysisandcontrolofmodernpower
accessed:Jun.2024.
system,” International Journal of Electrical Power & Energy Systems,
vol.136,p.107744,2022.
[9] G. S. Misyris, A. Venzke, and S. Chatzivasileiadis, “Physics-informed