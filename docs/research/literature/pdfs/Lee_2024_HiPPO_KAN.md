# Lee_2024_HiPPO_KAN

HiPPO-KAN: Efficient KAN Model for Time Series Analysis
SangJong Lee, Jin-Kwang Kim, JunHo Kim, TaeHan Kim, James Lee
XaaH Corp
{sangjong, jinkwang, demyank, taehankim, jaminyx}@xaah.xyz
Abstract
In this study, we introduces a parameter-efficient model that outperforms traditional models
in time series forecasting, by integrating High-order Polynomial Projection (HiPPO) theory into
the Kolmogorov-Arnold network (KAN) framework. This HiPPO-KAN model achieves superior
performance on long sequence data without increasing parameter count. Experimental results
demonstratethatHiPPO-KANmaintainsaconstantparametercountwhilevaryingwindowsizes
and prediction horizons, in contrast to KAN, whose parameter count increases linearly with win-
dow size. Surprisingly, although the HiPPO-KAN model keeps a constant parameter count as
increasingwindowsize,itsignificantlyoutperformsKANmodelatlargerwindowsizes. Thesere-
sults indicate that HiPPO-KAN offers significant parameter efficiency and scalability advantages
for time series forecasting. Additionally, we address the lagging problem commonly encountered
in time series forecasting models, where predictions fail to promptly capture sudden changes in
the data. We achieve this by modifying the loss function to compute the MSE directly on the
coefficientvectorsintheHiPPOdomain. Thisadjustmenteffectivelyresolvesthelaggingproblem,
resulting in predictions that closely follow the actual time series data. By incorporating HiPPO
theory into KAN, this study showcases an efficient approach for handling long sequences with
improved predictive accuracy, offering practical contributions for applications in large-scale time
series data.
1 Introduction
Thepurposeofdeeplearningistofindawell-approximatedfunction,especiallywhenatargetfunction
involves non-linearity or high-dimensionality. In the case of Multilayer perceptron (MLP), a represen-
tational ability for non-linear functions is guaranteed by the universal approximation theorem [1, 2].
Recently, Kolomogorov-Arnold network (KAN) has been proposed as a promising alternative to MLP
[3, 4]. This model is distinct to MLP in that it learns activations functions rather than weigths of
edges. Its representational ability is partially guaranteed by Kolomogorov-Arnold theorem (KAT),
while KAN slightly reshapes the theorem by assuming smooth activation functions but with a deeper
network so that it can utilize the back-propagation mechanism. It outperforms MLP with a better
scaling law, offering new pathway to modeling complex functions.
Numerous models based on MLP, RNN, and LSTM have been developed to conduct time-series
analysis, aiming to model complex patterns and non-linearities [5, 6, 7, 8, 9]. Also, deep state space
modelhasemergedasapowerfulapproachfortimeseriesforecasting[10]. Itcombinesthestrengthsof
traditional state space models with the representation-learning capabilities of deep learning, allowing
them to capture complex temporal dynamics more effectively. By integrating probabilistic reasoning
and deep learning, the deep state space model offers significant improvements in forecasting time-
series data [10, 11, 12]. While these methods have shown some success in capturing trends and
seasonality, they often face challenges in capturing complex patterns and, especially learning long-
term dependencies [13].
Long-termdependencyisparticularlyimportantintimeseriesanalysis,asmanyreal-worlddatasets
such as those in finance, weather forecasting, and energy consumption, involve patterns that evolve
over long periods. Capturing these dependencies enables models to make more accurate predictions
by considering not only short-term fluctuations but also broader trends and delayed effects that span
across extended windows. To address these issues, A. Gu et al. introduced the HiPPO (High-order
1
4202
tcO
91
]GL.sc[
1v93941.0142:viXra

Figure1: ThisdiagramillustratestheprocessofencodingtimeseriesdatausingtheHiPPOframework,
transformingitwiththeKolmogorov-ArnoldNetwork(KAN),anddecodingitbacktothetimedomain.
The initial time series l is projected into a coefficient vector c(L) through HiPPO. This vector is then
transformed by KAN into c(L+1), followed by decoding through HiPPO to reconstruct the time series
of length l + 1. This setup serves as an auto-encoder where HiPPO and KAN handle encoding,
transformation, and decoding, respectively.
Polynomial Projection Operator) theory and the Structured State Space (S4) model [14, 15, 16, 17],
which effectively capture long-range dependencies by performing online function approximation with
special initial conditions in the state space transition equation.
In this work, we build upon the HiPPO theory to enhance the capabilities of the Kolmogorov-
Arnold Network (KAN) for time series analysis. According to the HiPPO (High-order Polynomial
ProjectionOperator)theory,aspecialcombinationofmatricesAandB inthetransitionequationofa
statespacemodelenablesthemappingofsequentialdata,suchastimeseries,intoafinite-dimensional
spaceexpandedbywell-definedpolynomialbases. Thismeansthattimeseriesdatacanberepresented
as a coefficient vector whose dimension is independent of the length of the sequence.
Leveraging this property, we can effectively forecast future time-series with smaller parameters.
Figure 1 exhibits a schematic of the HiPPO-KAN process. It first encodes the time series data into
a fixed-dimensional coefficient vector using the HiPPO framework. Then it maps this coefficient
vector into another vector within the same dimensional space. This mapping is performed using the
Kolmogorov-Arnold Network (KAN), which acts as a function approximator in this context. Finally,
we decode the transformed coefficient vector back into the time domain using the inverse function
provided by the HiPPO framework. This process is analogous to an auto-encoder, where the encoder
and decoder are defined by the HiPPO transformations, and the latent space manipulation is handled
by KAN.
Accordingly, our contributions are as follows:
1. ParameterEfficiencyandScalabilityinUnivariateTimeSeriesPrediction. Wedemon-
strate that HiPPO-KAN achieves superior parameter efficiency in univariate time-series predic-
tiontasks. Thedimensionofthecoefficientvectorremainsfixedregardlessoftheinputsequence
length, enabling the model to scale to long sequences without increasing the number of parame-
ters. This scalability is crucial for practical applications involving large datasets.
2. Enhanced Performance Over Traditional KAN in Long-Range Forecasting. We show
that HiPPO-KAN outperforms the traditional KAN as well as other traditional models spe-
cialized to handle sequential data (e.g. RNN and LSTM), especially in long-range forecasting
scenarios. By effectively capturing long-term dependencies through the HiPPO framework, our
model provides more accurate predictions compared to KAN alone.
3. Novel Integration of HiPPO Theory with KAN. The use of HiPPO coefficients provides
a concise and interpretable state representation of the time series system. When combined with
KAN’s transparent architecture, this allows for better understanding and interpretability of the
model’s internal workings.
2

2 Backgrounds
2.1 State Space Model
State space model can be written as
d
x(t)=Ax(t)+Bu(t), (1)
dt
y(t)=Cx(t)+Du(t), (2)
where u(t) ∈ Rl is an input vector, x(t) ∈ RN is a hidden state vector, and y(t) ∈ Rk is an output
vector. Eq.(1) describes the state dynamics, showing how the state x(t) evolves over time based on its
current value and the input u(t). The matrix A∈RN×N defines the influence of the current state on
itsrateofchange, whileB∈RN×l defineshowtheinputaffectsthestatedynamics. Eq.(2)represents
theoutputequation,illustratinghowthecurrentstateandinputproducetheoutputy(t). Thematrix
C∈Rk×N maps the state to the output, and D∈Rk×l maps the input directly to the output.
In many cases, especially when implementing skip connections akin to those in deep learning
architectures, we can set D=0. This simplifies the output equation to
y(t)=Cx(t). (3)
By doing so, the output depends solely on the internal state, allowing the model to focus on the
learned representations within x(t) without direct influence from the immediate input u(t). Gu et al.
showedthatwhenthesystemislineartime-invariant(LTI),theSSMreducestoasequence-to-sequence
mapping by defining a convolution mapping
K(t)=CetAB, y(t)=(K∗u)(t). (4)
Gu et al.[14] also showed that, by selecting specific initial conditions for the parameters (A,B), etAB
becomes a vector of N basis functions. This result enables the state-space model to perform online
function approximation using the HiPPO theory.
2.2 HiPPO Theory
The memorization process can be considered as a symmetry breaking of fully symmetric states. The
fully symmetric state represents a system with maximum entropy, where all configurations are equally
probable. Byintroducingtheinformationwewishtomemorizeasanexternalcondition,webreakthis
symmetry, allowing the system to settle into a specific state that encodes the memory.
In the context of continuous time series, this approach was exemplified by the Legendre Memory
Unit (LMU) [18]. The LMU employs continuous orthogonal functions—specifically, Legendre polyno-
mials—to maintain a compressed representation of the entire history of input data. Building upon
these principles, Gu et al. [14] connected memorization to state-space models with a strong theoreti-
cal foundation. Specifically, they demonstrated that a special initialization of the transition equation
in the state-space model enables closed-form function approximation, effectively capturing long-term
dependencies in sequential data. HiPPO treats memorization as an online function approximation.
Suppose we have a univariate time series function:
f :R →R, t(cid:55)→f(t). (5)
≥0
Since we are considering online function approximation, we define:
(cid:90) t (cid:90) t
x (t)= dsω(t,s)p (t,s)u(s), ⟨p , p ⟩ ≡ dsω(t,s)p (t,s)p (t,s)=δ , (6)
n n n m ω n m n,m
0 0
whichstatesthatforeveryfixedt,thefunctionp belongtoaHilbertspaceHandformanorthonormal
n
basis with respect to the measure ω(t,s). Rewriting Eq.(6), we have:
(cid:90) t
x (t)= dsω(t,s)p (t,s)u(s)=⟨u, p (t)⟩ , (7)
n n n ω
0
3

which indicates that the state vector x(t)=[x (t),x (t),...,x (t)]T represents the projection of u(s)
1 2 N
for s≤t onto an orthonormal basis with respect to weighted inner product defined by ω(t,s).
If we assume completeness, we have:
N
(cid:88)
u(s)= lim x (t)p (t, s) (8)
n n
N→∞
n=1
for all s ≤ t due to the completeness of the basis function. Since we are dealing with a finite N, by
choosing an appropriate cutoff, we obtain an approximate representation of the function u(s). Gu et
al. [17] defined this problem as online function approximation in the HiPPO theory.
(a) Comparison of S&P500 data with approximated (b) HiPPO approximation of S&P500 data for state
data using HiPPO for different state space dimen- space dimensions N =64,128,256, showing progres-
sions. sively closer fits to the original data as N increases.
Figure 2: HiPPO was applied to the S&P 500 data. The state space dimension used were N =
16,32,64,128,256, and as N increases, the approximation becomes increasingly closer to the original
function, reflecting a higher fidelity representation of the underlying dynamics.
From a physical standpoint, this is analogous to a multipole expansion, where each term has
a specific physical interpretation. In the case of a nonlinear function that takes the coefficients of
a multipole expansion as inputs, each coefficient corresponds to a node within the function. Ideally,
duringtheprocessoflearningthisnonlinearfunction,derivingaclosed-formsolutionorunderstanding
how each node operates would greatly aid in physical interpretation. This understanding can provide
significant insights into the underlying physics and how the model represents the system. To further
enhancethisinterpretability,weutilizedKANtomodelthemappingfromthecoefficientsofsequential
data of length l to sequential data of length l+1.
2.3 KAN
2.3.1 Kolmogorov-Arnold Theorem
The Kolmogorov-Arnold Representation Theorem states that any continuous multivariate function f
defined on a bounded domain In, where n is the number of variables and I =[0,1], can be expressed
as a finite sum of compositions of continuous univariate functions and addition. Specifically, for a
smooth function f:
2n+1 (cid:32) n (cid:33)
(cid:88) (cid:88)
f :In →R, x∈In (cid:55)→f(x ,··· ,x )= Φ ϕ (x ) , (9)
1 n q q,p p
q=1 p=1
whereeachϕ :I →RandΦ :R→Rarecontinuousunivariatefunctions. Thistheoremrevealsthat
q,p q
any multivariate continuous function can be constructed using only univariate continuous functions
and addition, significantly simplifying their analysis and approximation. This decomposition reduces
the complexity inherent in multivariate functions, making them more tractable for approximation
methods.
4

2.3.2 Kolmogorov-Arnold Network
BuildingupontheKolmogorov-Arnoldrepresentationtheorem,theKolmogorov-ArnoldNetwork(KAN)
is designedto explicitlyparametrize thisrepresentationfor practicalfunction approximationin neural
networks [3, 4]. Since we have decomposed the multivariate function into univariate functions, the
problem reduces to parametrizing these univariate functions. To achieve this, we can use B-splines
due to their flexibility and smoothness properties, which are advantageous for interpolations. From
theperspectiveofgeneralizingtheKolmogorov–Arnold(KA)representationtheoremandextendingit
to deeper networks, the network architecture can be expressed as follows:
[n ,n ,··· ,n ], (10)
0 1 L
where n is the number of nodes in the l-th layer. The pre-activation values are given by:
l
(cid:88)
nl
x = ϕ (x ), l=0,...,L−1; j =1,...,n (11)
l+1,j l,j,i l,i l+1
i=1
where ϕ are the univariate functions with learnable parameters in the l-th layer.
l,j,i
In practice, the univariate functions ϕ in KAN are parametrized using B-splines to capture
l,j,i
complex nonlinearities while maintaining smoothness and flexibility. To enhance the representational
capacity of the network and facilitate efficient training, KAN employs residual activation functions
that combine a basis function with a spline function. Specifically, the activation function at each node
is defined as
ϕ(x)=w b(x)+w spline(x) (12)
b s
where b(x) is a predefined basis function, w and w are learnable weights, and spline(x) is a spline
b s
function constructed from B-spline basis functions. The basis function b(x) is typically chosen as the
SiLU (Sigmoid Linear Unit) activation function due to its smoothness and nonlinearity.
The overall network function is then:
KAN(x)=(Φ ◦Φ ◦···◦Φ )(x). (13)
L−1 L−2 0
In this expression, Φ represents the vector of univariate functions at layer l, and the composition of
l
these functions across layers forms the basis of KAN’s ability to approximate multivariate functions.
In the context our work, we extend KAN by integrating with the HiPPO framework to efficiently
handle time series data. This integration allows us to leverage KAN’s function approximation ca-
pabilities while benefiting from HiPPO’s ability to represent sequential data in a fixed-dimensional
space.
2.4 Time-series forecasting using KAN
Since its introduction, KAN have been proved to be a powerful tool for time-series forecasting due to
their effective approximation capabilities and training efficiency. It has been shown that KAN models
outperform MLP models in time-series forecasting, both in terms of accuracy and computational
efficiency [19, 20]. Furthermore, when KAN layers are incorporated within recurrent neural networks
(RNNs) and transformer architectures, they excel in multi-horizon forecasting tasks with reduced
overfitting issues [21, 22].
While these approaches validate the effectiveness of KAN models in time-series prediction and
outperforms traditional models specialized in sequential data (e.g., RNN and GRU), they involve
integratingKANintocomplexarchitectures,whichcanincreasesmodelcomplexityandcomputational
demands. In this study, however, we propose an alternative methodology that combines KAN models
with HiPPO transformation. By integrating KAN with the HiPPO transformation, we construct
a simpler model architecture that retains high predictive performance without relying on complex
recurrent or transformer structures.
5

3 HiPPO-KAN
Building upon the HiPPO framework, we consider a univariate time series u ∈ RL. The HiPPO
1:L
transformation maps this time series into a coefficient vector c(L) ∈RN via the mapping
hippo :RL →RN, u (cid:55)→c(L) =hippo (u ), (14)
L 1:L L 1:L
where N is the dimension of the hidden state. In our proposed method, the KAN is utilized to model
themappingbetweencoefficientvectorscorrespondingtotimeseriesoflengthLandL+1. Specifically,
KAN transforms the coefficient vector c(L) into a new coefficient vector c(L+1):
KAN:RN →RN, c(L) (cid:55)→c(L+1) =KAN(c(L)). (15)
The resultant coefficient vector c(L+1) represents the encoded state of the time series extended to
length L+1. Given the coefficient c(L+1), we can easily construct a time series data of length L+1.
Let this process be denoted as hippo−1:
hippo−1 :RN →RL+1, c(L+1) (cid:55)→u′ =hippo−1 (c(L+1)), (16)
L+1 1:L+1 L+1
whereu andu′ aredifferenttimeseries. Thisprocesseffectivelyextendstheoriginaltimeseries
1:L 1:L+1
by one time step, generating a prediction for the next value in the sequence. By operating within the
fixed-dimensionalcoefficientspaceRN,whereN isindependentofthesequencelengthL,ourapproach
maintainsparameterefficiencyandscalability. TheuseofKANinthiscontextallowsforthemodeling
of complex nonlinear relationships between the coefficients, capturing the underlying dynamics of the
time series.
3.1 Definition of HiPPO-KAN
We define the HiPPO-KAN model as a seq2seq mapping that integrates the HiPPO transformations
with the KAN mapping. Formally, HiPPO-KAN is defined as
HiPPO-KAN≡hippo−1 ◦KAN◦hippo . (17)
L+1 L
Thiscompositemappingtakestheoriginaltimeseries{u }L asinputandproducesanextendedtime
t t=1
series {u }L+1 as output:
t t=1
HiPPO-KAN:RL →RL+1, {u }L (cid:55)→{u′}L+1. (18)
t t=1 t t=1
In other words, HiPPO-KAN maps a time series of length L to a different time series of length
L+1, effectively predicting the next value in the sequence while retaining the original sequence. By
integrating these components, HiPPO-KAN effectively captures long-term dependencies and complex
temporalpatternsintime-seriesdata. OperatingwithinthecoefficientspaceRN ensuresthatthemodel
remains parameter-efficient and scalable, as the dimensionality N does not depend on the sequence
length L.
Following the definition of the HiPPO-KAN model, we derive its explicit output formulation by
integrating the HiPPO transformations with the KAN mapping. Applying the hippo transformation
L
to the input time series {u }L , the function f(s) can be approximately represented in terms of
t t=1
orthogonal basis functions:
N
(cid:88)
f(s)≈ c p (L,s), (19)
n n
n=1
where c ∈R are the coefficients, and p (L,s) are the HiPPO basis functions evaluated at time L for
n n
all s≤L.
Utilizing the KAN mapping, we update the coefficients to incorporate the system dynamics:
N
(cid:88)
c′ = Φ (c ), (20)
n nm m
m=1
6

where Φ are the elements of the KAN matrix Φ∈RN×N. We defined hippo−1 as
nm
N N (cid:32) N (cid:33)
u′ = (cid:88)(cid:0) c′ +Bu (cid:1) p (L+1,s)= (cid:88) (cid:88) Φ (c )+Bu p (L+1,s), (21)
1:L+1 n L n nm m L n
n=1 n=1 m=1
whereB ∈RN islearnableparameters. ThisisanalogoustotheBu(t)terminthestate-spacemodel’s
state equation. Evaluating at s=L+1, the final output for the next time step is:
N (cid:32) N (cid:33)
(cid:88) (cid:88)
u′ = Φ (c )+Bu p (L+1,L+1). (22)
L+1 nm m L n
n=1 m=1
√
In the case of Leg-S, from the definition of basis, we have p (L+1,L+1)= 2n+1 [14, 17]. Hence,
n
we obtain
(cid:88) N √ (cid:32) (cid:88) N (cid:33)
u′ = 2n+1 Φ (c )+Bu . (23)
L+1 nm m L
n=1 m=1
This methodology resembles an auto-encoder architecture, where the encoder (HiPPO transfor-
mation) compresses the input time series into a latent coefficient vector c(L), the dynamics of which
is modelled by KAN layers in our HiPPO-KAN model. The decoder (inverse HiPPO transforma-
tion) reconstructs the extended time series from c(L+1). The fixed-dimensional latent space acts as a
bottleneck, promoting efficient learning.
3.2 Method
3.2.1 Task Definition
In this study, we address the problem of time series forecasting in the context of cryptocurrency
markets, specifically focusing on the BTC-USDT trading pair. The objective is to predict the next
price point given a historical sequence of observed prices. Formally, let {u }L denote a univariate
t t=1
time series representing the BTC-USDT prices at discrete time steps t = 1,2,...,L, where L is the
window size. The forecasting task aims to estimate the subsequent value u based on the given
L+1
window of past observations.
Mathematically, the prediction function can be expressed as:
uˆ =f(u ,u ,...,u ), (24)
L+1 1 2 L
where f :RL →R is a mapping from the past L observations to the predicted next value uˆ .
L+1
The challenge inherent in this task include:
• Non-Stationary Cryptocurrency prices exhibit high volatility and non-stationary behavior,
making it difficult to model underlying patterns using traditional statistical methods.
• Long-Term Dependencies Capturing long-term dependencies is essential, as market trends
and cycles can influence future prices over extended periods.
• ComputationalEfficiency Handlinglongsequencesefficientlywithoutaproportionalincrease
in computational complexity or model parameters is critical for scalability.
Our approach utilize the HiPPO-KAN model to effectively tackle these challenges by encoding the
input time series into a fixed-dimensional coefficient vector using the HiPPO transformation. This
allows the model to process long sequence while maintaining a constant parameter count, facilitating
efficient learning and improved predictive accuracy.
3.2.2 Data Normalization
We evaluated the performance of HiPPO-KAN using the BTC-USDT 1-minute futures data from
January 1st to Feburuary 1st, which consists of univariate time series data. Prior to training, we
normalized the raw time series data using the formula (u −µ)/µ, where µ denotes the mean value of
t
7

thedatawithineachwindow. Thisnormalizationservesseveralcriticalpurposesinthecontextoftime
seriesmodeling. Firstly,itcentersthedataaroundzero,whichhelpsinstabilizingthetrainingprocess
andacceleratingconvergencebymitigatingbiasesintroducedbyvaryingdatascales. Secondly,scaling
by the mean adjusts for fluctuations in the magnitude of the data across different windows, ensuring
that the model’s learning is not skewed by windows with larger absolute values.
By normalizing each window individually, we effectively address the non-stationarity inherent in
financialtimeseriesdata,wherestatisticalpropertiessuchasmeanandvariancecanchangeovertime.
This window-specific normalization allows the model to focus on learning the underlying patterns and
dynamics within each window without being influenced by shifts in the data scale. Consequently, this
approach enhances the robustness of the model and improves its ability to generalize across different
segments of the time series.
3.2.3 Loss Function for Model Training
The training of the HiPPO-KAN model involves optimizing the network parameters to minimize the
discrepancy between the predicted values and the actual observed values in the time series data. We
employ the Mean Squared Error (MSE) as the loss function, which is a standard choice for regression
tasks in time series forecasting due to its sensitivity to large errors.
The MSE loss function is defined as:
D
L(θ)=
1 (cid:88)(cid:16)
u(i) −uˆ(i)
(cid:17)2
, (25)
D L+1 L+1
i=1
where θ represents the model parameters, D is the number of samples in the training set, u(i) is the
L+1
true next value in the time series for the i-th sample, and uˆ(i) is the corresponding prediction made
L+1
by the model.
MinimizingtheMSElossencouragesthemodeltoproducepredictionsthatare,onaverage,asclose
as possible to the actual values, with larger errors being penalized more heavily due to the squaring
operation. The choice of MSE as the loss function aligns with the evaluation metrics used in our
experiments, namely the Mean Squared Error (MSE) and Mean Absolute Error (MAE), facilitating a
consistent assessment of the model’s performance during training and testing.
3.2.4 Experimental Results
TheexperimentalresultsarepresentedinTables1tofacilitateaclearandconcisecomparisonofmodel
performances. Table 1 summarizes the results for a prediction horizon of 1. Each table includes the
model name, window size, network width (architecture), Mean Squared Error (MSE), Mean Absolute
Error (MAE), and the number of parameters used in the model.
By organizing the results in tabular form, we provide a straightforward means to compare the
effectiveness of HiPPO-KAN against baseline models such as HiPPO-MLP, KAN, LSTM, and RNN
across different configurations. This structured presentation highlights the consistency and scalability
of HiPPO-KAN, especially in terms of parameter efficiency and predictive accuracy over varying win-
dowsizesandpredictionhorizons. ThetablesclearlydemonstratethatHiPPO-KANachievessuperior
performancewithfewerparameters,emphasizingtheadvantagesofintegratingHiPPOtransformations
with KAN mappings in time series forecasting tasks.
WepresentadditionalexperimentalresultsinAppendixA.ToevaluatethescalabilityoftheHiPPO-
KAN model, we test its performance of HiPPO-KAN on even larger window sizes. Furthermore, we
demonstrate that information bottleneck theory can be effectively applied within the HiPPO-KAN
framework.
3.3 Lagging problem
While the result presented above are impressive, we observed that the model still suffers from the
lagging problem when examining the plots of the predictions. The lagging problem refers to the
phenomenonwherethemodel’spredictionslagbehindtheactualtimeseries,failingtocapturesudden
changes promptly [23]. This issue is particularly detrimental in time series forecasting, where timely
and accurate predictions are crucial.
8

Table 1: Performance comparison of models for prediction horizon 1. Best models are highlighted in
bold.
Model Window Size Width MSE MAE Parameters
HiPPO-KAN 120 [16, 16] 3.40×10−7 4.14×10−4 4,384
HiPPO-KAN 500 [16, 16] 3.34×10−7 3.95×10−4 4,384
HiPPO-KAN 1200 [16, 16] 3.26×10−7 4.00×10−4 4,384
HiPPO-MLP 120 [32, 64, 64, 32, 32] 2.33×10−6 1.04×10−3 9,792
HiPPO-MLP 500 [32, 64, 64, 32, 32] 2.68×10−5 3.84×10−3 9,792
HiPPO-MLP 1200 [32, 64, 64, 32, 32] 5.87×10−6 1.96×10−3 9,792
KAN 120 [120, 1] 8.9×10−7 6.82×10−4 1,680
KAN 500 [500, 1] 1.66×10−6 9.62×10−4 7,000
KAN 1200 [1200, 1] 4.03×10−6 1.56×10−3 16,800
LSTM 120 - 4.69×10−7 4.99×10−4 4,513
LSTM 500 - 6.50×10−7 6.00×10−4 4,513
LSTM 1200 - 9.21×10−7 7.21×10−4 4,513
RNN 120 - 1.14×10−6 8.60×10−4 12,673
RNN 500 - 1.09×10−6 7.70×10−4 12,673
RNN 1200 - 1.18×10−6 7.79×10−4 12,673
Figure 3: MSE and MAE comparisons for various models (HiPPO-KAN, KAN, LSTM, RNN) using
different window sizes (120, 500, 1200). The results show the performance of each model in terms of
error metrics as the window size increases.
Toaddressthisissue,wemodifiedthelossfunctionusedduringtrainingandputB =0. Insteadof
computingtheMSEbetweentheinverse-HiPPO-transformedoutputsuˆ =hippo−1 (cid:0) cˆ(L+1)(cid:1) and
1:L+1 L+1
the actual time series u , we computed the MSE directly on the coefficient vectors in the HiPPO
1:L+1
domain. Specificaly, the loss function is defined as:
L(θ)= 1 (cid:88) D (cid:12) (cid:12)c(L+1)(i)−cˆ(L+1)(i) (cid:12) (cid:12) 2 (26)
D (cid:12) true (cid:12)
i=1
whereθrepresentsthemodelparameters,Disthenumberofsamplesinthetrainingset,c(L+1)(i) =
true
hippo (cid:0) u(i) (cid:1) isthetruecoefficientvectorobtainedbyapplyingtheHiPPOtransformationtothe
L+1 1:L+1
actualtimeseries, andcˆ(L+1)(i) =KAN (cid:0) c(L)(i)(cid:1) isthepredictedcoefficientvectoroutputbytheKAN
model.
9

Bytrainingthemodelusingthismodifiedlossfunction,weaimedtoalignthelearningprocessmore
closely with the underlying representation in the coefficient space, where the HiPPO transformation
captures the essential dynamics of the time series. This approach emphasizes learning the progression
of the coefficient directly, which may help the model respond more promptly to changes in the input
data.
3.3.1 Interpretation of the Coefficient-Based Loss Function
Representation of Functions in Finite-Dimensional Space When obtaining the coefficient
vector c, it is important to recognize that c does not represent a single, unique function. Instead, it
encapsulatesanapproximationoftheoriginaltimeseriesfunctionwithinafinite-dimensionalsubspace
spanned by the first N basis functions. The approximated function f(s) of a function f can be
true
expressed as:
N ∞ ∞
(cid:88) (cid:88) (cid:88)
f (s)= c p (t,s)+ c p (t,s)=f(s)+ c p (t,s) (27)
true i i i i i i
i=1 i=N+1 i=N+1
where p (t,s) are the orthogonal basis functions of the HiPPO transformation, and c are the cor-
i i
responding coefficients. The finite sum over i = 1 to N captures the primary components of the
function, while the infinite sum over i=N+1 to ∞ represents the residual components not captured
duetotruncationatN. Thismeansthatcrepresentsaclassoffunctionssharingthesamecoefficients
for the first N basis functions but potentially differing in higher-order terms. By working with this
finite-dimensionalapproximation,themodelfocusesonthemostsignificantfeaturesofthetimeseries,
enabling efficient learning and generalization.
Impact of Batch Training on Loss Computation In our training process, we utilize batch
training, where the model parameters are updated based on the mean loss computed over a batch of
samples. Specifically, the loss function computes the average MSE between the predicted and true
coefficient vectors across the batch:
L(θ)= 1 (cid:88) D (cid:12) (cid:12)c(L+1)(i)−cˆ(L+1)(i) (cid:12) (cid:12) 2 , (28)
D (cid:12) true (cid:12)
i=1
where D is the batch size. This approach means that the model learns to minimize the average
discrepancy between the predicted and actual coefficients over various time series segments within the
batch.
ConvergencetoaSpecificFunctionThroughBatchAveraging Byminimizingtheaverageloss
across the batch, the model effectively converges towards a specific coefficient vector c that represents
the common underlying dynamics present in the batch samples. This process is akin to converging to
aspecificfunctionamongthepossibleoneswithinthefunctionspacedefinedbythefinite-dimensional
basis. Thebatchaveragingactsasamechanismtoalignthemodel’spredictionwiththesharedfeatures
across different time series segments, guiding it towards a consensus representation.
As a result, the model captures the dominant patterns and trends that are consistent across the
batch,enhancingitsabilitytogeneralizeandreducingthelikelihoodofoverfittingtospecificinstances.
The batch mean effectively smooths out idiosyncratic variations in individual samples, promoting the
learning of robust features pertinent to the forecasting task. This convergence towards a specific
function helps the model to produce more accurate and reliable predictions, particularly when dealing
with complex and noisy time series data.
Advantages of the Legendre Basis with Exponential Decay Weighting In the HiPPO trans-
formation, the choice of the Leg-S plays a crucial role in enhancing the model’s predictive capabili-
ties. The Leg-S approximation employs a weighting scheme with exponential decay, meaning that the
weightsassignedtopastinputsdecreaseexponentiallyovertime. Thisweightingeffectivelyimplements
amemorizationschemethatplacesmoreemphasisonthepresentthanonthepast. Asaresult,recent
inputs have a stronger influence on the model’s state representation than older inputs.
This characteristic leads to more accurate approximations near the final boundary of the time
interval, specifically at the prediction point s=t=L+1. Since the model assigns greater importance
to recent data, the approximated function f(s) closely matches the actual time series values in the
10

neighborhoodofthefinalboundary. ThereforetheLegendrebasisfunctionsintheLeg-Sapproximation
provide almost equal to the actual values at the final time steps.
ByleveragingtheexponentialdecayweightingoftheLeg-Sbasis,themodelcanproducepredictions
that closely follow the actual data where it matters most—the immediate future. This enhanced
accuracy at the prediction boundary is particularly beneficial in time series forecasting applications,
where capturing sudden changes and trends promptly is crucial for timely and accurate predictions.
The ability to emphasize recent observations allows the HiPPO-KAN model to be more responsive to
newinformation,effectivelymitigatingissueslikethelaggingproblemandimprovingoverallforecasting
performance. As illustrated in Figure 5, the predictions made by the model are now more accurately
aligned with the actual time series, effectively capturing sudden changes without delay. Additional
results can be found in Appendix A.
Figure 4: Lagging Effect in KAN Models. These models exhibit a tendency to produce outputs
that closely mimic the preceding values, indicating an inability to capture rapid changes in the data
effectively.
Figure 5: The modified loss function effectively resolves the lagging problem, resulting in predictions
that closely follow the actual time series data. This result is based on a randomly selected segment of
BTC-USDT 1-minute interval data, using a KAN architecture with a width of [16, 2, 16].
11

4 Conclusion
Inthisstudy,weintroducedHiPPO-KAN,anovelmodelthatintegratestheHiPPOframeworkwiththe
KAN model to enhance time series forecasting. By encoding time series data into a fixed-dimensional
coefficient vector using the HiPPO transformation, and then modeling the progression of these coeffi-
cients with KAN, HiPPO-KAN efficiently performed time-series prediction task.
Our experimental results, as presented in Table 1, demonstrate that HiPPO-KAN consistently
outperformstraditionalKANandotherbaselinemodelssuchasHiPPO-MLP,LSTM,andRNNacross
various window sizes and prediction horizons. Notably, HiPPO-KAN maintains a constant parameter
count regardless of sequence length, highlighting its parameter efficiency and scalability. For example,
at a window size of 1,200 and a prediction horizon of 1, HiPPO-KAN achieved an MSE of 3.26×10−7
and an MAE of 4.00×10−4, compared to KAN’s MSE of 4.03×10−6 and MAE of 1.56×10−3, with
fewer parameters.
The integration of HiPPO theory into the KAN framework provides a powerful approach for han-
dlinglongsequenceswithoutincreasingthemodelsize. Byoperatingwithinafixed-dimensionallatent
space, HiPPO-KAN not only improves predictive accuracy but also offers better interpretability of
the model’s internal workings. The use of KAN allows for modeling complex nonlinear relationships
between the HiPPO coefficients, capturing the underlying dynamics of the time series more effectively
thantraditionalmethods. ThesepromisingresultspositionHiPPO-KANasasignificantadvancement
in time-series forecasting, offering a scalable and efficient solution that could potentially revolutionize
applications across various domains, from financial modeling to climate prediction.
Additionally, we addressed the lagging problem commonly encountered in time series forecasting
models. By modifying the loss function to compute the MSE directly on the coefficient vectors in the
HiPPO domain, we significantly improved the model’s ability to capture sudden changes in the data
withoutdelay. Thisadjustmentalignsthelearningprocessmorecloselywiththeunderlyingdynamics
of the time series, allowing HiPPO-KAN to produce predictions that closely follow the actual data, as
illustrated in Figure 5.
4.1 Future Work
Integration with Graph Neural Networks for Multivariate Time Series
To extend HiPPO-KAN to handle multivariate time series data, we propose integrating it with Graph
NeuralNetworks(GNNs)[1]. Inthisframework,eachvariableortimeseriesinthemultivariatedataset
is represented as a node within a graph structure. At each node, the HiPPO transformation encodes
the local time series data into a fixed-dimensional coefficient vector, analogous to a gauge vector in
physics.
These gauge-like vectors serve as localized representations of the temporal dynamics at each node.
Theedgesofthegraphdefinetheinteractionsbetweennodes,capturingthedependenciesandrelation-
shipsamongdifferentvariablesinthedataset. Bymodelingtheseinteractions,wecandefinefunctions
that operate on pairs or groups of coefficient vectors, effectively allowing information to flow across
the graph and capturing the multivariate dependencies.
ThisintegrationleveragesthestrengthofHiPPO-KANinmodelingindividualtimeseriesefficiently
while utilizing the relational modeling capabilities of GNNs to handle the interconnectedness of mul-
tivariate data. Future work could focus on developing this combined HiPPO-KAN-GNN architecture,
investigating how the interactions between nodes can be effectively modeled, and exploring the im-
pact on forecasting accuracy and interpretability. This approach has the potential to address complex
systems where variables are interdependent, such as in financial markets, climate modeling, and social
network analysis.
References
[1] M.M.Bronstein, J.Bruna, T.Cohen, andP.Velickovic. Geometricdeeplearning: Grids, groups,
graphs, geodesics, and gauges. arXiv preprint arXiv:2104.13478, 2021.
[2] I. Goodfellow, Y. Bengjo, and A. Courville. Deep Learning. Adaptive Computation and Machine
Learning series. The MIT Press, 2016.
12

[3] Z. Liu, Y. Wang, S. Vaidya, F. Ruehle, J. Halverson, M. Soljiacic, T. Y. Hou, and M. Tegmark.
Kan: Kolmogorov-arnold networks. arXiv preprint arXiv:2404.19756, 2024.
[4] Z. Liu, P. Ma, Y. Wang, W. Matusik, and M. Tegmark. Kan 2.0: Kolmogorov-arnold networks
meet science. arXiv preprint arXiv:2408.10205, 2024.
[5] G. P. Zhang. An investigation of neural networks for linear time-series forecasting. Computers &
Operations Research, 28(12):1183–1202, 2001.
[6] H. S. Hippert, C. E. Pedreira, and R. C. Souza. Neural networks for short-term load forecasting:
A review and evaluation. IEEE Transactions on Power Systems, 16(1):44–55, 2001.
[7] Z. C. Lipton, J. Berkowitz, and C. Elkan. A critical review of recurrent neural networks for
sequence learning. arXiv preprint arXiv:1506.00019, 2015.
[8] F. A. Gers, J. Schmidhuber, and F. Cummnins. Learning to forget: Continual prediction with
lstm. Neural Computation, 12(10):2451–2471, 2000.
[9] Y. Kong, Z. Wang, Y. Nie, T. Zhou, S. Zohren, Y. Liang, P. Sun, and Q. Wen. Unlocking the
power of lstm for long term time series forecasting. arXiv preprint arXiv:2408:10006, 2024.
[10] S. S. Rangapuram, M. Seeger, J. Gasthaus, L. Stella, Y. Wang, and T. Januschowski. Deep state
space models for time series forecasting. In Advances in Neural Information Processing Systems,
pages 7796–7805, 2018.
[11] L.Li,J.Yan,X.Yang,andY.Jin. Learninginterpretabledeepstatespacemodelforprobabilistic
time series forecasting. arXiv preprint arXiv:2102.00397, 2021.
[12] H.Inzirillo. Deepstatespacerecurrentneuralnetworksfortimeseriesforecasting. arXiv preprint
arXiv:2407.15236, 2024.
[13] Yoshua Bengio, Patrice Simard, and Paolo Frasconi. Learning long-term dependencies with gra-
dient descent is difficult. IEEE transactions on neural networks, 5(2):157–166, 1994.
[14] A. Gu, T. Dao, S. Ermon, A. Rudra, and C. R´e. Hippo: Recurrent memory with optimal
polynomial projections. arXiv preprint arXiv:2008.07669, 2020.
[15] A. Gu, K. Goel, and C. R´e. Efficiently modeling long sequences with structured state spaces.
arXiv preprint arXiv:2111.00396, 2022.
[16] A.Gu,A.Gupta,K.Goel,andC.R´e. Ontheparametrizationandinitializationofdiagonalstate
space models. arXiv preprint arXiv:2206.11893, 2022.
[17] A. Gu, I. Johnson, A. Timalsina, A. Rudra, and C. Re. How to train your hippo: State space
models with generalized orthogonal basis projections. arXiv preprint arXiv:2206.12037, 2022.
[18] A.R.Voelker,I.Kajic,andC.Eliasmith.Legendrememoryunits: Continuous-timerepresentation
in recurrent neural networks. In Advances in Neural Information Processing Systems (NeurIPS
2019), Vancouver, Canada, 2019.
[19] Cristian J Vaca-Rubio, Luis Blanco, Roberto Pereira, and M`arius Caus. Kolmogorov-arnold
networks (kans) for time series analysis. arXiv preprint arXiv:2405.08790, 2024.
[20] Kunpeng Xu, Lifei Chen, and Shengrui Wang. Kolmogorov-arnold networks for time series:
Bridging predictive power and interpretability. arXiv preprint arXiv:2406.02496, 2024.
[21] Remi Genet and Hugo Inzirillo. Tkan: Temporal kolmogorov-arnold networks. arXiv preprint
arXiv:2405.07344, 2024.
[22] Remi Genet and Hugo Inzirillo. A temporal kolmogorov-arnold transformer for time series fore-
casting. arXiv preprint arXiv:2406.02486, 2024.
[23] J.Li,L.Song,D.Wu,J.Shui,andT.Wang. Laggingprobleminfinancialtimeseriesforecasting.
Neural Computing and Applications, 35:20819–20839, 2023.
13

[24] TishbyNaftaliandZaslavskyNoga. Deeplearningandtheinformationbottleneckprinciple. arXiv
preprint arXiv:1503.02406, 2015.
[25] Andrew M Saxe, Yamini Bansal, Joel Dapello, Madhu Advani, Artemy Kolchinsky, Brendan D
Tracey, and David D Cox. On the information bottleneck theory of deep learning*. Journal of
Statistical Mechanics: Theory and Experiment, 2019(12):124020, 2019.
14

APPENDIX
A Additional Experimental Results
To further elucidate the scalability and robustness of the HiPPO-KAN model, we conducted a series
of experiments with larger window sizes of 2500, 3000, 3500, and 4000. The results are summarized
in Table 2. Our findings indicate that the model’s accuracy experiences only marginal degradation as
the window size increases up to 4000. Notably, while the window size expands by a factor of 33, the
MSE loss of the model increases by a mere factor of approximately 1.3, with model parameters held
constant. This small increase in error relative to the substantial increase in window size demonstrates
the exceptional scalability and computational efficiency of the HiPPO-KAN model. These results
not only demonstrate the model’s resilience to increased input complexity but also underscore its
potentialforapplicationinscenariosdemandingtheprocessingofextensivetemporalsequenceswithout
significant compromise in performance.
Table 2: Performance of HiPPO-KAN on larger window sizes. Best models are highlighted in bold.
Model Window Size Width MSE MAE Parameters
HiPPO-KAN 2500 [16, 16] 3.33×10−7 4.13×10−4 4384
HiPPO-KAN 3000 [16, 16] 3.68×10−7 4.41×10−4 4384
HiPPO-KAN 3500 [16, 16] 4.01×10−7 4.66×10−4 4384
HiPPO-KAN 4000 [16, 16] 4.38×10−7 4.89×10−4 4384
HiPPO-KAN 2500 [16, 2, 16] 3.10×10−7 3.90×10−4 1344
HiPPO-KAN 3000 [16, 2, 16] 3.29×10−7 4.05×10−4 1344
HiPPO-KAN 3500 [16, 2, 16] 3.46×10−7 4.19×10−4 1344
HiPPO-KAN 4000 [16, 2, 16] 3.96×10−7 4.50×10−4 1344
HiPPO-KAN 2500 [16, 4, 16] 3.13×10−7 3.94×10−4 2400
HiPPO-KAN 3000 [16, 4, 16] 3.29×10−7 4.05×10−4 2400
HiPPO-KAN 3500 [16, 4, 16] 4.03×10−7 4.66×10−4 2400
HiPPO-KAN 4000 [16, 4, 16] 3.84×10−7 4.48×10−4 2400
Figure6: PerformanceofHiPPO-KANonlargerwindowsizes,illustratingtheimpactofthebottleneck
layer on model efficiency. Configurations with a bottleneck achieve lower Mean Squared Error (MSE)
and Mean Absolute Error (MAE) compared to models without a bottleneck despite having fewer
parameters.
15

In addition, we conducted experiments with HiPPO-KAN models incorporating a bottleneck layer
within their network architecture. Intriguingly, as demonstrated in Table 2 and Fig. 6, the HiPPO-
KAN model featuring a bottleneck layer exhibited better performance compared to its counterpart
without such a layer, despite having fewer parameters. This seemingly counterintuitive outcome can
be elucidated through the lens of information bottleneck theory [24, 25]. This theoretical framework
positsthatmodelscanderivebenefitsfromcompressinginputinformation, therebydistillingthemost
salient features pertinent to the prediction task. The enhanced performance of the bottleneck model
aligns with this principle, suggesting that the constrained representation enforced by the bottleneck
layer facilitates more effective feature extraction and, consequently, improved predictive capability.
16