1
AR-KAN: Autoregressive-Weight-Enhanced
Kolmogorov-Arnold Network for Time Series
Forecasting
Chen Zeng, Tiehang Xu, and Qiao Wang , Senior Member, IEEE
Abstract—Traditional neural networks struggle to capture models like Mamba[16] have emerged as efficient alterna-
the spectral structure of complex signals. Fourier neural net- tives to attention mechanisms, offering linear-time computa-
works (FNNs) attempt to address this by embedding Fourier tion and strong performance on long-range sequences. More
series components, yet many real-world signals are almost-
recently, Kolmogorov-Arnold Networks (KANs)[17][18] have
periodic with non-commensurate frequencies, posing additional
challenges. Building on prior work[41] showing that ARIMA been introduced as a novel architecture with high expressivity
outperforms large language models (LLMs) for forecasting, we and flexible modeling of nonlinear mappings. In parallel,
extend the comparison to neural predictors and find ARIMA the rapid progress of large language models (LLMs) has
still superior. We therefore propose the Autoregressive-Weight- led to approaches such as LLMTime[42] and Time-LLM[19],
Enhanced Kolmogorov–Arnold Network (AR-KAN), which in-
which adapt pretrained language models to temporal tasks by
tegrates a pre-trained AR module for temporal memory with
a KAN for nonlinear representation. The AR module preserves leveraging their strong generalization and sequence modeling
essential temporal features while reducing redundancy. Experi- capabilities.
ments demonstrate that AR-KAN matches ARIMA on almost- In the context of neural forecasting, a specialized research
periodic functions and achieves the best results on 72% of
focusesonspectralanalysisthroughspecificnetworks,suchas
Rdatasets series, with a clear advantage on data with periodic
Fourier Neural Networks (FNNs)[20]. These models incorpo-
structure. These results highlight AR-KAN as a robust and
effective framework for time series forecasting. Our code is
rateFourierseriestoenhancespectralmodeling[21].Represen-
available at https://github.com/ChenZeng001/AR-KAN. tativeexamplesincludetheFourierNeuralOperator(FNO)[23]
and the Fourier Analysis Network (FAN)[22], which have
Index Terms—Time series forecasting, ARIMA, Kolmogorov-
Arnold Network, KAN, Almost periodic functions been applied to physics-informed learning, partial differential
equation solving, and time series prediction.
Nevertheless, these neural network models grounded in
I. INTRODUCTION
representationbyFourierseriesmayoverlookakeytheoretical
Time series forecasting is a fundamental task in sig-
constraint:theadditivecombinationofperiodicelementsdoes
nal processing[1][2], statistics[3], and numerous applied fields, notnecessarilyresultinaperiodicfunction[24][25].Throughout
including economics[4], meteorology[5], and healthcare[6].
history, this important topic prompted N. Wiener to create
Among classical approaches, the Autoregressive Integrated
the renowned Generalized Harmonic Analysis (GHA) theory,
Moving Average (ARIMA) model[7] stands out as one of
which works alongside the spectral analysis of time series.
the most influential and widely adopted methods, because it
When the constituent frequencies are incommensurable, the
integrates autoregression, differencing, and moving average resulting signal is almost-periodic[26], meaning that it exhibits
elements to provide a comprehensible and effective approach
recurrence without strict periodicity. Empirical studies show
for handling practical time series data, even when the time
that for such signals, even advanced neural models, including
series is non-stationary. FNNs, are often outperformed by classical ARIMA[27][28] and
ApartfromtheaforementionedstatisticsorFourieranalysis- an evaluation could be referred as to our recent work [41].
based methods, neural networks have been utilized in time
Empirical studies indicate that, for such signals, even ad-
series forecasting for many years[8], with the goal of en-
vancedneuralmodelssuchasFNNsareoftenoutperformedby
abling the modeling of complex nonlinear dependencies. Ar- classical ARIMA methods [27][28]. A more detailed evaluation
chitectures such as Multi-Layer Perceptrons (MLPs)[10] and can be found in our recent work [41].
Recurrent Neural Networks (RNNs)[11], particularly Long
To address this, we propose AR-KAN, a hybrid model that
Short-Term Memory (LSTM) networks[12], have been widely
integrates the strengths of traditional and modern approaches.
studied. In recent years, Transformer-based models[13][14][15] BasedontheUniversalMyopicMappingTheorem[29][30],AR-
have gained popularity due to their self-attention mechanism
KAN employs a KAN as the static nonlinear component,
and parallel processing capabilities. Meanwhile, state space
while introducing memory through a pre-trained autoregres-
sive (AR) model. This design enables AR-KAN to combine
Both C. Zeng and T. Xu was with the School of Information Sci-
ence and Engineering, Southeast University, Nanjing, China (email: chen- the adaptability and expressiveness of KANs with the strong
zeng@seu.edu.cn,220250920@seu.edu.cn). spectral bias inherent in traditional AR models. Furthermore,
Q.WangwaswithboththeSchoolofInformationScienceandEngineering
the AR memory module itself is a data-driven model whose
andtheSchoolofEconomicsandManagement,SoutheastUniversity,Nanjing,
China(CorrespondingAuthor,email:qiaowang@seu.edu.cn). weights are not fixed but are adaptively determined by the
5202
peS
81
]GL.sc[
2v76920.9052:viXra

2
characteristics of the data. Additionally, it can be shown The integration component (1 − B)d transforms non-
that when handling time series forecasting tasks, this module stationary series into stationary ones by differencing. The
effectivelyeliminatesredundancywhileretainingthemaximal ARIMA model captures linear temporal dependencies and
amount of useful information. This property allows the model is known for its statistical interpretability and relatively low
to flexibly adapt to various temporal patterns without manual computational cost. Despite its simplicity, ARIMA remains a
intervention. strongbaselineinmanypracticalapplications,especiallywhen
Extensive experiments demonstrate AR-KAN’s effective- the underlying signal exhibits regular, stationary behavior.
ness. On almost-periodic functions, it matches ARIMA’s per-
formance. And on real-world datasets from Rdatasets[40], it B. MLP and KAN
outperforms baselines on 72% of tasks. The few cases where
MLPisoneofthemostfundamentalarchitecturesinneural
AR-KAN does not dominate correspond mostly to datasets
networks. An MLP consists of multiple layers of affine trans-
with weak or nearly absent periodicity, which are inherently
formationsfollowedbypointwisenonlinearactivations.Given
difficulttoforecastwithoutadditionalpriorinformation.When an input x∈Rd, an L-layer MLP computes:
focusing on datasets with stronger periodic components, AR-
KAN shows a clear and consistent advantage, highlighting its
(cid:16) (cid:17)
robustness, adaptability, and potential as a unified framework f MLP (x)=W(L)σ L−1 ···σ 1 W(1)x+b(1) +b(L), (3)
for time series forecasting.
where W(ℓ), b(ℓ) are learnable parameters, and σ denotes the
The structure of this paper is organized as follows: ℓ
nonlinear activation at layer ℓ.
Section II introduces the background, including time series
However, MLPs exhibit a well-known spectral bias[31],
forecasting tasks, ARIMA, MLP, and KAN models. Sec-
meaning they tend to learn low-frequency components of the
tion III presents the Universal Myopic Mapping Theorem
targetfunctionearlierandmoreaccuratelythanhigh-frequency
and explains how it inspires the overall architecture of our
components. While this inductive bias can be beneficial in
AR-KAN model. Section IV describes the experiments con-
some applications, it limits the ability of MLPs to capture
ductedtodemonstratetheeffectivenessandgeneralizabilityof
fine-grained or oscillatory patterns in data.
AR-KAN, including evaluations on two constructed almost-
To overcome the limited expressiveness of fixed activation
periodic functions and real-world time series. Finally, Section
functionsintraditionalMLPs,KANshavebeenproposedasa
V concludes the paper.
more flexible and interpretable alternative. KANs are inspired
by the Kolmogorov–Arnold representation theorem[32], which
II. BACKGROUND
states that any multivariate continuous function f : [0,1]d →
A. Time Series Forecasting and ARIMA R can be expressed as a finite composition of univariate
Timeseriesforecastingaimstopredictasequencebasedon continuous functions:
its past observations. Formally, given a univariate time series
2d+1 (cid:32) d (cid:33)
{x }T ,theforecastingprobleminvolveslearningamapping (cid:88) (cid:88)
n n=1 f(x ,...,x )= ϕ ψ (x ) , (4)
F such that: 1 d q qi i
q=1 i=1
xˆ =F(x ,x ,...,x ), (1) whereϕ q andψ qi areunivariatecontinuousfunctions.Inspired
n+h n n−1 n−p+1
by this constructive result, KANs replace the fixed nonlinear
wherexˆ n+h denotestheforecastforh-stepsahead(h=1in activations in MLPs with learnable univariate functions, typi-
this paper), and p is the order of historical dependence. This cally represented by splines.
formulation can be extended to multivariate or probabilistic Given an input x∈Rd, an L-layer KAN computes:
settings, but the central challenge remains: capturing the
underlying temporal dynamics, dependencies, and possibly f (x)=Φ(L)Ψ(L−1)···Ψ(1)(x), (5)
KAN
noise in the observed data.
A classical and widely used model for time series forecast-
where each layer Ψ(ℓ) :Rdℓ →Rdℓ+1 is defined by:
ing is ARIMA. ARIMA is particularly effective for stationary
or differenced stationary processes. The general form of an [Ψ(ℓ)(x)] = (cid:88)
dℓ
w(ℓ)·ψ(ℓ)(x ), (6)
j ij ij i
ARIMA(p, d, q) model is given by:
i=1
and Φ(L) denotes the final output transformation, typically of
Φ(B)(1−B)dx =Θ(B)ϵ , (2)
n n the same form. Here, each ψ(ℓ) is a learnable univariate func-
ij
where: tion, often implemented using splines, and w(ℓ) are learnable
ij
• B is the backshift operator, i.e., Bkx n =x n−k , scalar weights.
• Φ(B)=1−a 1 B−···−a p Bp istheautoregressive(AR) UnlikeMLPs,KANsdonotexhibitalow-frequencyspectral
polynomial of order p, bias [33]. This enables them to capture high-frequency and
• Θ(B) = 1+b 1 B +···+b q Bq is the moving average oscillatory components more effectively, making them well
(MA) polynomial of order q, suited for modeling time series with rich spectral structures.
• d is the degree of differencing to ensure stationarity, However, this advantage can also introduce challenges.
• ϵ n is assumed to be white noise: ϵ t ∼N(0,σ2). Withoutalow-frequencybias,KANstendtobemoresensitive

3
Fig. 1: Universal Myopic Mapping Theorem.
Fig. 2: Model Structure of AR-KAN.
to high-frequency noise[34] and may have difficulty learning A. Universal Myopic Mapping Theorem
functions with limited regularity[35]. In such cases, the model
may overfit to spurious variations or become unstable during The Universal Myopic Mapping Theorem [29][30] provides a
training. powerful theoretical guarantee for modeling dynamic systems
Nevertheless, in most real-world time series, especially using shallow, feedforward structures. Specifically, it states
those with structured periodicity, seasonal trends, or non- that any shift-invariant and myopic dynamical map can be
stationary high-frequency patterns, this characteristic is ben- uniformly approximated arbitrarily well by a two-stage archi-
eficial. The ability of KANs to model a broad spectrum tecture: a bank of linear filters followed by a static nonlinear
of frequency behaviors often leads to better performance mapping, as shown in Fig. 1.
compared to MLPs.
Theorem 1 (Universal Myopic Mapping Theorem [29][30]).
Let M be a shift-invariant and myopic dynamical system
that maps a real-valued time series {x n } n∈Z to outputs {y n }
III. AR-KAN via a causal and bounded operator. Then, for any ε > 0,
there exists a finite collection of linear filters {h }N and a
i i=1
continuous static nonlinear function f : RN → R such that
θ
AR-KAN is derived from the Universal Myopic Mapping
the approximation
Theorem. Therefore, in this section, we first introduce the
Universal Myopic Mapping Theorem, then followed by a
detailed explanation of the AR-KAN model architecture. y ≈f ((h ∗x) ,(h ∗x) ,...,(h ∗x) )
n θ 1 n 2 n N n

4
satisfies
a=R−1r. (10)
sup|y −f ((h ∗x) ,...,(h ∗x) )|<ε,
n θ 1 n N n
n Here, the autocorrelation function r(i) is defined as
(cid:80)
where ∗ denotes convolution and (h ∗x) = h (τ)x .
i n τ i n−τ
r(i)=E[x(n)x(n−i)], (11)
This theorem establishes that it is theoretically sufficient
to model a wide class of dynamical systems using a finite or, in practice, estimated from the empirical data as
bankoflinearfiltersfollowedbyanonlinearfunction,without
N−1
requiring recurrent or deep sequential architectures. The key 1 (cid:88)
r(i)≈ x(n)x(n−i), (12)
property of myopia means that each output depends only N −i
n=i
on a bounded past history, and shift-invariance ensures time-
homogeneity. where N is the total number of available samples.
This formulation reveals a key feature of our memory
module: the filter weights {a } are not fixed parameters,
i
B. Model Structure of AR-KAN
but are derived from the underlying data through statistical
Inspired by the Universal Myopic Mapping Theorem, we estimation. In contrast to static memory schemes such as
design the AR-KAN as a two-stage architecture composed of tapped-delay lines[38] or gamma memory[39], our data-driven
a data-driven memory module and a static nonlinear map- design allows the memory module to adapt flexibly to the
ping, as illustrated in Fig. 2. The static nonlinear network autocorrelation structure of different time series.
is implemented using a KAN, which has been discussed in
Section II to possess stronger spectral modeling capabilities
C. Analysis of the AR Memory Module
thantraditionalMLPs,particularlyforhigh-frequencysignals.
To further elucidate the advantage of the AR memory
For the memory module, we adopt a pre-trained AR model
module, we provide a theoretical analysis demonstrating that
to serve as the bank of linear filters, effectively incorporating
it optimally preserves useful information while eliminating
the strengths of classical linear time series models into our
redundancy. Consider a general linear memory module with
architecture.
output:
The memory module operates in the following manner: we
first train an AR model from the input time series {x(n)} to
y (n)=w x(n−i), 0≤i≤p−1, (13)
predict the next step via i i
where w are the weights.
i
p−1
(cid:88) We aim to maximize the total correlation between the
xˆ(n+1)= a x(n−i), (7)
i memory outputs and the target x(n + 1), which represents
i=0
the useful information captured:
where p is the AR order and {a }p−1 are the learned AR
i i=0 p−1
coefficients. These coefficients are then extracted to define (cid:88)
max E[y (n)x(n+1)]. (14)
a set of fixed linear filters. At each time step n, a delay i
buffer forms the historical input vector {x(n−i)}p−1, which i=0
i=0
is multiplied elementwise with the corresponding {a }p−1 However, this objective alone is insufficient, as it can be
i i=0
and passed to the subsequent KAN module. This structure trivially maximized by arbitrarily increasing the magnitude of
is equivalent to setting the impulse response of the i-th filter w i , which would also amplify noise and irrelevant compo-
in Fig. 1 as: nents. To prevent this and encourage the memory to focus on
themostinformativefeatures,weintroduceaconstraintonthe
total output energy of the memory module:
h (n)=a δ(n−i), 0≤i≤p−1, (8)
i i
where δ(·) is the Kronecker delta function.
(cid:32)p−1 (cid:33)2
(cid:88)
To express the AR coefficients {a } explicitly in terms minE  y i (n) . (15)
i
of the time series {x(n)}, we can solve the Yule–Walker i=0
equations[36][37]. Specifically, let a = [a 0 ,a 1 ,...,a p−1 ]⊤ be This constraint penalizes high-energy outputs, effectively
the coefficient vector, r=[r(1),r(2),...,r(p)]⊤ the autocor- forcing the memory to represent the target using a compact
relation vector, and R the p×p autocorrelation matrix given setoffeaturesanddiscardredundantinformation.Wecombine
by these two objectives into a single optimization goal:
 
r(0) r(1) ··· r(p−1)
 r(1) r(0) ··· r(p−2) (cid:88) p−1 1
(cid:32)
(cid:88) p−1
(cid:33)2
R= 

. .
.
. .
.
... . .
.
 

, (9) L=
i=0
E[y i (n)x(n+1)]− 2 E 
i=0
y i (n) . (16)
r(p−1) r(p−2) ··· r(0)
To find the optimal weights that maximize L, we solve
then the AR coefficients are computed via: ∂L =0 for w=[w ,w ,...,w ]⊤ gives:
∂w 0 1 p−1

5
TABLE I: Test loss (MSE) of various models on Noisy Almost Periodic Functions
functions σ ARIMA AR-KAN AR-MLP KAN MLP Transformer LSTM Mamba FAN FNO
0.1 0.0142 0.0203 0.0270 0.1507 0.1216 0.0584 0.0743 0.1194 0.1173 0.0767
0.2 0.0550 0.0770 0.0959 0.1946 0.1273 0.3903 0.1462 0.2934 0.4266 0.1305
f1
0.3 0.1206 0.1681 0.1999 0.2947 0.2408 0.4635 0.5209 0.3781 0.7023 0.1979
0.4 0.2155 0.2892 0.3543 0.6241 1.4625 1.5572 0.3932 0.5932 0.7965 0.7865
0.1 0.0194 0.0193 0.0214 0.0515 0.1525 0.0947 0.0813 0.1149 0.0384 0.0322
0.2 0.0881 0.0724 0.0922 0.2812 0.1550 0.5346 0.2424 0.2593 0.5109 0.2747
f2
0.3 0.1647 0.1593 0.1745 0.2577 0.6787 1.2197 0.4042 0.5592 0.3506 0.4277
0.4 0.3108 0.2769 0.3341 0.7100 1.1827 3.8209 0.4932 0.5914 0.7702 1.1133
Note:Boldnumbersindicatetheminimumvalueineachrow;italicnumbersindicatethesecondminimumvalue.
Fig. 3: Performance of ARIMA, AR-KAN and FAN on Noisy Almost Periodic Functions, σ =0.4 (left: f , right: f ).
1 2
perform experiments on noisy almost-periodic functions to
w∗ =R−1r, (17) show that modern models fall short of traditional ARIMA
models in terms of spectral analysis, while our AR-KAN
which is exactly the solution for the AR coefficients. This
achieves performance comparable to ARIMA. Then, we ex-
result confirms that the AR memory module optimally bal-
tend the evaluation to real-world datasets from Rdatasets[40],
ances the dual goals of preserving predictive information and
and observe that AR-KAN achieves the best performance on
minimizing redundancy, providing a principled foundation for
72%ofdatasets.Thefewcaseswhereitunderperformsmostly
its use in AR-KAN.
involve weak or absent periodicity, which are inherently hard
This adaptability endows AR-KAN with stronger gener-
topredictwithoutpriorknowledge.Forstronglyperiodicdata,
alization across diverse temporal patterns. The linear filters
AR-KAN shows a clear and consistent advantage.
capture data-specific short-term dynamics, while the nonlin-
ear KAN component models higher-order, nonlinear interac-
A. Noisy Almost Periodic Functions
tions. Together, they form a powerful hybrid that balances
We construct noisy almost-periodic functions by superim-
interpretability, efficiency, and expressiveness in time series
posing 2 trigonometric waves with incommensurate frequen-
forecasting.
cies and adding Gaussian noise:
IV. EXPERIMENTS
f (t)=cos(2t)+cos(2πt)+noise, (18)
We conduct experiments in two parts to demonstrate both 1
the effectiveness and generalizability of AR-KAN. First, we f (t)=sin(3t)+sin(2et)+noise, (19)
2

6
TABLE II: Test loss (MSE) of various models on Rdatasets with periodicity strength
Datasets PeriodicityStrength ARIMA AR-KAN AR-MLP KAN MLP LSTM FAN FNO LLMTime
airpass ts 41.28% 0.3329 0.0706 0.0871 0.3046 0.3025 0.4249 0.5163 0.6982 0.1937
goog200 ts 34.24% 4.7135 0.1228 0.8096 3.6632 3.5888 3.2584 3.0580 7.9012 1.1351
euretail ts 18.39% 0.4967 0.9964 1.3328 1.1984 0.4226 1.6740 1.1469 0.1821 1.5009
ausbeer ts 14.63% 0.0418 0.0357 0.0741 0.1031 0.5102 0.0692 0.0802 0.1114 0.0436
h02 ts 13.31% 0.2726 0.1263 0.1782 1.3708 0.5258 0.2103 0.6003 0.8209 0.1371
BJsales ts 10.08% 0.3241 0.0032 0.0261 0.0358 0.7849 0.0643 0.2393 1.0370 0.0131
a10 ts 6.36% 0.1441 0.1353 0.4775 2.5033 2.2638 0.8809 0.4913 0.3851 0.3457
hsales2 ts 4.20% 0.5781 0.5232 0.6301 2.1212 0.8286 1.7787 1.7065 0.8850 0.5667
co2 ts 3.69% 0.0218 0.0014 0.0064 0.3079 0.0460 0.1640 0.1584 0.1963 0.0109
hyndsight ts 2.61% 0.8729 0.2471 0.3961 1.5734 0.4892 0.5929 0.6164 0.6793 0.4510
bricksq ts 1.33% 0.2080 0.0502 0.0823 0.2542 0.2769 0.2961 0.9625 0.2607 0.2541
elecequip ts 1.25% 0.3159 0.1528 0.1346 0.5968 0.5538 0.8984 0.7761 0.4870 1.4010
elecdaily mts 1.16% 0.4331 0.2123 0.2573 0.4410 0.5366 0.6792 0.8981 0.5919 0.6127
gtemp both ts 0.50% 2.2374 0.2936 0.5328 3.2225 2.2946 1.6629 2.8678 1.6660 5.0938
discoveries ts 0.22% 1.6030 2.1695 2.3091 1.7269 1.6264 1.7949 1.0153 0.8469 1.2922
elec ts 0.16% 0.2731 0.0069 0.0060 0.0930 0.0436 0.1833 0.3258 0.0625 0.0727
economics df ts 0.00% 3.5659 0.0845 0.4398 2.3047 1.8717 2.2520 1.8607 7.7670 1.6490
auscafe ts 0.00% 0.3301 0.3813 0.1180 2.6312 0.7564 0.3746 1.4820 3.4769 0.4463
Note:Boldnumbersindicatetheminimumvalueineachrow.Rowsareshadedinredwhenperiodicityispresent(≥0.5%)andinbluewhenperiodicityis
weak(<0.5%).
Fig. 4: Performance of ARIMA and AR-KAN on two different types of time series in Rdatasets. the left column shows results
on a10_ts (a highly periodic series), and the right column shows results on discoveries_ts (a nearly non-periodic
series).
where the noise is sampled from a zero-mean Gaussian dis- specificallyforspectrallearning.AsillustratedinFig.3,FAN
tribution with variance σ2. Almost-periodic functions like this is only able to capture the rough trend of the signal but fails
are of particular significance in the development of harmonic to reconstruct fine-grained details. In contrast, the AR-KAN
analysis, and they form the basis of generalized harmonic achieves excellent performance comparable to ARIMA. It in-
analysis (GHA) as formulated by Wiener[2]. heritsthestrongspectralanalysiscapabilitiesofautoregressive
We vary the noise level σ from 0.1 to 0.4 and compare models while also benefiting from the KAN’s near absence of
the performance of ARIMA and 9 neural models. The results spectral bias, enabling it to handle the intricate details of the
are shown in TABLE I. Typically, the outcomes of certain time series effectively.
experiments (σ = 0.4) produced by ARIMA, AR-KAN, and This combination of strengths makes AR-KAN particularly
FAN are shown in Fig. 3. suitable for data with complex frequency structures. The re-
Experimental results show that for almost-periodic func- sultshighlighttheeffectivenessofourarchitectureinbridging
tions, all 7 existing neural networks perform worse than the gap between traditional statistical methods and modern
ARIMA,includingFNOandFAN,bothofwhicharedesigned neural networks.

7
B. Rdatasets APPENDIXB
We further evaluate AR-KAN on real-world series from
MODELARCHITECTUREANDCONFIGURATION
Rdatasets[40]. For each dataset, we quantify its Periodicity
models architectureandconfiguration
Strength as the ratio of the energy of the seasonal component
(obtainedbySTLdecomposition[43])tothetotalenergyofthe ARIMA p=20,d=0or1,q=1or2
original series: KAN width=[20,50,1],grid=3,k=3
MLP width=[20,128,256,128,1]
∥x ∥2
Periodicity Strength= seasonal 2. feature dimension=64,nhead=4,
∥x∥2 Transformer
2 encoder layers=2,feedforward dimension=128
The period used in STL decomposition is determined by the input size=1,hidden size=64,
LSTM
largestnonzero-lagpeakintheseries’autocorrelationfunction. num layers=2,output size=1
Our results in TABLE II show that AR-KAN achieves the
input dim=1,d model=48,d state=32,
bestperformanceon72%ofdatasets.Moreover,itsadvantage Mamba
d conv=20,n layers=5
growswithincreasingPeriodicityStrength,indicatingthatAR-
input dim=20,output dim=1,hidden dim=2048,
KAN excels on series with clear or strong periodic compo- FAN
num layers=5,p ratio=0.25
nents. In contrast, its few underperforming cases correspond
input dim=20,output dim=1,modes=8,
to datasets with weak or nearly absent periodicity, which are FNO
channels=32,fourier layers=2
inherentlyhardtoforecastwithoutadditionalpriorknowledge
LLMTime DeepSeek-V3,experiment times=10
and remain challenging for all competing methods. They are
illustrated in Fig. 4. By the way, Fourier-based models fail
to generalize despite their spectral priors, and other neural
REFERENCES
baselines show similar limitations.
LLM-based methods such as LLMTime[42] approach [1] G.E.P.Box,G.M.Jenkins,G.C.Reinsel,andG.M.Ljung,TimeSeries
Analysis:ForecastingandControl,5thed. Hoboken,NewJersey:John
ARIMA[41] in performance but still fall short of AR-KAN, Wiley&SonsInc.,2015.
indicating that LLMs are not yet mature for time series [2] N. Wiener, Extrapolation, interpolation, and smoothing of stationary
timeseries:withengineeringapplications. TheMITPress,1949.
forecasting. Both LLMs and neural networks struggle to cap-
[3] C. Ferna´ndez-Pe´rez, J. Tejada, and M. Carrasco, “Multivariate time
ture frequency structure, whereas AR offers a statistical view series analysis in nosocomial infection surveillance: a case study,”
for genuine spectral analysis. By combining this frequency- International Journal of Epidemiology, vol. 27, no. 2, pp. 282–288, 4
1998.[Online].Available:https://doi.org/10.1093/ije/27.2.282
awaremodelingwithKAN’snonlinearexpressivity,AR-KAN
[4] T. Wang, R. Beard, J. Hawkins, and R. Chandra, “Recursive deep
achieves robust, domain-general performance. learning framework for forecasting the decadal world economic
outlook,”IEEEAccess,vol.12,pp.152921–152944,12024.[Online].
Available:https://doi.org/10.1109/access.2024.3472859
V. CONCLUSION
[5] M.Singh,V.S.B,N.Acharya,A.Grover,S.A.Rao,B.Kumar,Z.-L.
In this paper, we reveal that existing neural networks strug- Yang, and D. Niyogi, “Short-range forecasts of global precipitation
usingdeeplearning-augmentednumericalweatherprediction,”62022.
gle with spectral analysis and often underperform ARIMA on
[Online].Available:https://arxiv.org/abs/2206.11669
almost-periodic functions. Guided by the Universal Myopic [6] Y.Deng,S.Liu,Z.Wang,Y.Wang,Y.Jiang,andB.Liu,“Explainable
Mapping Theorem, we propose AR-KAN, which combines time-series deep learning models for the prediction of mortality,
prolonged length of stay and 30-day readmission in intensive care
ARIMA’s autoregressive memory with KAN’s nonlinear ex-
patients,” Frontiers in Medicine, vol. 9, 9 2022. [Online]. Available:
pressivity. Experiments show that AR-KAN matches ARIMA https://doi.org/10.3389/fmed.2022.933037
on almost-periodic functions and outperforms baselines on [7] G.E.P.BoxandG.M.Jenkins,“Somerecentadvancesinforecasting
andcontrol,”JournaloftheRoyalStatisticalSociety.SeriesC(Applied
72% of real-world datasets, with its advantage growing on
Statistics),vol.17,no.2,pp.91–109,1968.
series with clear periodic patterns. These results highlight [8] B. Lim and S. Zohren, “Time-series forecasting with deep learning: a
AR-KAN as a robust and unified framework for time series survey,”PhilosophicalTransactionsoftheRoyalSocietyAMathematical
PhysicalandEngineeringSciences,vol.379,no.2194,p.20200209,2
forecasting.
2021.[Online].Available:https://doi.org/10.1098/rsta.2020.0209
[9] R. Csorda´s, C. Potts, C. D. Manning, and A. Geiger, “Recurrent
Neural Networks Learn to Store and Generate Sequences using
APPENDIXA
Non-Linear Representations,” 8 2024. [Online]. Available: https:
DATASAMPLINGANDEVALUATIONPROTOCOL //arxiv.org/abs/2408.10920
[10] I.A.GheyasandL.S.Smith,“Aneuralnetworkapproachtotimeseries
In the Noisy Almost Periodic Functions experiment, the
forecasting,” 2009. [Online]. Available: https://api.semanticscholar.org/
temporal variable t ranges from 0 to 8π, and a total of 500 CorpusID:2266156
samplesareuniformlycollectedoverthisinterval.Thedataset [11] L.R.Medsker,L.Jainetal.,“Recurrentneuralnetworks,”Designand
applications,vol.5,no.64-67,p.2,2001.
is split into training and testing sets with an 80/20 ratio:
[12] S.HochreiterandJ.Schmidhuber,“LongShort-Termmemory,”Neural
the first 80% of the sequence is used for training, while the Computation, vol. 9, no. 8, pp. 1735–1780, 11 1997. [Online].
remaining 20% is reserved for testing. Available:https://doi.org/10.1162/neco.1997.9.8.1735
[13] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N.
For the Rdatasets experiment, all time series are standard-
Gomez, L. Kaiser, and I. Polosukhin, “Attention is All you Need,”
ized based on their mean and standard deviation. Then also arXiv (Cornell University), vol. 30, pp. 5998–6008, 6 2017. [Online].
apply the 80/20 split strategy: the training set consists of the Available:https://arxiv.org/pdf/1706.03762v5
[14] Q. Wen, T. Zhou, C. Zhang, W. Chen, Z. Ma, J. Yan, and L. Sun,
first 80% of each sequence, and the testing set consists of the
“Transformers in Time Series: A survey,” 2 2022. [Online]. Available:
final 20%. https://arxiv.org/abs/2202.07125

8
[15] H. Zhou, S. Zhang, J. Peng, S. Zhang, J. Li, H. Xiong, and A Containing Papers of a Mathematical or Physical Character,
W. Zhang, “Informer: Beyond efficient transformer for long sequence vol. 226, no. 636-646, pp. 267–298, 1 1927. [Online]. Available:
Time-Series forecasting,” Proceedings of the AAAI Conference on https://doi.org/10.1098/rsta.1927.0007
Artificial Intelligence, vol. 35, no. 12, pp. 11106–11115, 5 2021. [37] G. T. Walker, “On periodicity in series of related terms,” Proceedings
[Online].Available:https://doi.org/10.1609/aaai.v35i12.17325 of the Royal Society of London Series A Containing Papers of a
[16] A. Gu and T. Dao, “Mamba: Linear-Time Sequence Modeling MathematicalandPhysicalCharacter,vol.131,no.818,pp.518–532,
with Selective State Spaces,” 12 2023. [Online]. Available: https: 61931.[Online].Available:https://doi.org/10.1098/rspa.1931.0069
//arxiv.org/abs/2312.00752 [38] J. A. Moorer, “About this reverberation business,” Computer Music
[17] Z.Liu,Y.Wang,S.Vaidya,F.Ruehle,J.Halverson,M.Soljacˇic´,T.Y. Journal, vol. 3, no. 2, p. 13, 6 1979. [Online]. Available:
Hou,andM.Tegmark,“Kan:Kolmogorov-arnoldnetworks,”2024. https://doi.org/10.2307/3680280
[18] Y.LuandF.Zhan,“KolmogorovArnoldNetworksinFraudDetection: [39] B. De Vries and J. C. Principe, “The gamma model—A new neural
Bridging the gap between theory and practice,” 8 2024. [Online]. model for temporal processing,” Neural Networks, vol. 5, no. 4,
Available:https://arxiv.org/abs/2408.10263 pp. 565–576, 7 1992. [Online]. Available: https://doi.org/10.1016/
[19] M. Jin, S. Wang, L. Ma, Z. Chu, J. Y. Zhang, X. Shi, P.-Y. Chen, s0893-6080(05)80035-8
Y. Liang, Y.-F. Li, S. Pan, and Q. Wen, “Time-LLM: Time series [40] V. Arel-Bundock, “Rdatasets: A collection of datasets originally
Forecasting by reprogramming large language models,” 10 2023. distributed in r packages,” GitHub. [Online]. Available: https:
[Online].Available:https://arxiv.org/abs/2310.01728 //github.com/vincentarelbundock/Rdatasets
[20] M. Tancik, P. P. Srinivasan, B. Mildenhall, S. Fridovich-Keil, [41] R.CaoandQ.Wang,“Anevaluationofstandardstatisticalmodelsand
N. Raghavan, U. Singhal, R. Ramamoorthi, J. T. Barron, and R. Ng, llmsontimeseriesforecasting,”in2024IEEEInternationalConference
“Fourier features let networks learn high frequency functions in low on Future Machine Learning and Data Science (FMLDS), 2024, pp.
dimensionaldomains,”NeuralInformationProcessingSystems,vol.33, 533–538.
pp.7537–7547,62020.[Online].Available:https://proceedings.neurips. [42] N.Gruver,M.Finzi,S.Qiu,andA.G.Wilson,“Largelanguagemodels
cc/paper/2020/file/55053683268957697aa39fba6f231c68-Paper.pdf are Zero-Shot time series forecasters,” 10 2023. [Online]. Available:
[21] M. Kim, Y. Hioka, and M. Witbrock, “Neural fourier modelling: a https://arxiv.org/abs/2310.07820
highly compact approach to Time-Series analysis,” 10 2024. [Online]. [43] R. B. Cleveland, W. S. Cleveland, J. E. McRae, I. Terpenning et al.,
Available:https://arxiv.org/abs/2410.04703 “Stl: A seasonal-trend decomposition,” J. off. Stat, vol. 6, no. 1, pp.
[22] Y. Dong, G. Li, Y. Tao, X. Jiang, K. Zhang, J. Li, J. Deng, J. Su, 3–73,1990.
J. Zhang, and J. Xu, “FAN: Fourier Analysis Networks,” 10 2024.
[Online].Available:https://arxiv.org/abs/2410.02675
[23] S.Guan,K.-T.Hsu,andP.V.Chitnis,“FourierNeuralOperatornetwork
forfastphotoacousticwavesimulations,”Algorithms,vol.16,no.2,p.
124,22023.[Online].Available:https://arxiv.org/abs/2108.09374
[24] A. S. Besicovitch, “Almost periodic functions,” Nature, vol. 131,
no. 3307, p. 384, 3 1933. [Online]. Available: https://doi.org/10.1038/
131384b0
[25] G. B. Folland, “Fourier analysis and its applications,” Choice Reviews
Online, vol. 30, no. 03, pp. 30–1562, 11 1992. [Online]. Available:
https://doi.org/10.5860/choice.30-1562
[26] L. Amerio and G. Prouse, Almost-Periodic functions and
functional equations, 1 1971. [Online]. Available: https:
//doi.org/10.1007/978-1-4757-1254-4
[27] R. H. Shumway and D. S. Stoffer, Time Series Analysis and its
applications, 11 2010. [Online]. Available: https://doi.org/10.1007/
978-1-4419-7865-3
[28] J. F. Torres, D. Hadjout, A. Sebaa, F. Mart´ınez-A´lvarez, and
A. Troncoso, “Deep learning for Time Series Forecasting: A survey,”
Big Data, vol. 9, no. 1, pp. 3–21, 12 2020. [Online]. Available:
https://doi.org/10.1089/big.2020.0159
[29] I. Sandberg and L. Xu, “Uniform approximation of multidimensional
myopic maps,” IEEE Transactions on Circuits and Systems I
Fundamental Theory and Applications, vol. 44, no. 6, pp. 477–500, 6
1997.[Online].Available:https://doi.org/10.1109/81.585959
[30] I. W. Sandberg and L. Xu, “Uniform Approximation of Discrete-
Space Multidimensional Myopic Maps,” Circuits Systems and Signal
Processing, vol. 16, no. 3, pp. 387–403, 5 1997. [Online]. Available:
https://doi.org/10.1007/bf01246720
[31] Q. Hong, J. W. Siegel, Q. Tan, and J. Xu, “On the Activation
Function Dependence of the Spectral Bias of Neural Networks,” 8
2022.[Online].Available:https://arxiv.org/abs/2208.04924
[32] A. B. Givental, B. A. Khesin, J. E. Marsden, A. N. Varchenko,
O. Y. Viro, and V. M. Zakalyukin, On the representation of
functions of several variables as a superposition of functions
of a smaller number of variables, 1 2009. [Online]. Available:
https://doi.org/10.1007/978-3-642-01742-1 5
[33] Y. Wang, J. W. Siegel, Z. Liu, and T. Y. Hou, “On the
expressiveness and spectral bias of KANs,” 10 2024. [Online].
Available:https://arxiv.org/abs/2410.01803
[34] H. Shen, C. Zeng, J. Wang, and Q. Wang, “Reduced effectiveness of
kolmogorov-arnoldnetworksonfunctionswithnoise,”inICASSP2025
-2025IEEEInternationalConferenceonAcoustics,SpeechandSignal
Processing(ICASSP),2025,pp.1–5.
[35] C. Zeng, J. Wang, H. Shen, and Q. Wang, “KAN versus MLP
on Irregular or Noisy Functions,” 8 2024. [Online]. Available:
https://arxiv.org/abs/2408.07906
[36] G. U. Yule, “VII. On a method of investigating periodicities
disturbed series, with special reference to Wolfer’s sunspot numbers,”
Philosophical Transactions of the Royal Society of London Series

