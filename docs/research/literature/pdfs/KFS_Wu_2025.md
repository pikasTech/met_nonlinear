# Page 1

KFS: KAN based adaptive Frequency Selection
learning architecture for long term time series forecasting
ChangningWu1,GaoWu1,RongyaoCai1,YongLiu*,1 ,KexinZhang*,1 ,
1InsitituteofCyber-SystemsandControl,ZhejiangUniversity,Hangzhou,China
*CorrespondingAuthor
Abstract introduces multi-scale seasonal-trend decomposition, high-
lighting the importance of multi-scale data. Recent mod-
Multi-scale decomposition architectures have emerged as
els like TimesNet (Wu et al. 2023) and SparseTFT (Lin
predominantmethodologiesintimeseriesforecasting.How-
etal.2024)concentrateondecomposinglongsequencesinto
ever,real-worldtimeseriesexhibitnoiseinterferenceacross
multipleshortersub-sequencesbasedonperiodicitylength.
differentscales,whileheterogeneousinformationdistribution
amongfrequencycomponentsatvaryingscalesleadstosub- Whilethesemethodsextractsubsequencesfromdiverseper-
optimalmulti-scalerepresentation.InspiredbyKolmogorov- spectives to capture critical information, the subsequences
ArnoldNetworks(KAN)andParseval’stheorem,wepropose split directly from the original series inevitably retain sub-
a KAN based adaptive frequency Selection learning archi- stantialnoise,leadingtosuboptimalproblems.
tecture (KFS) to address these challenges. This framework
It is worth noting that time series contain multiple fre-
tackles prediction challenges stemming from cross-scale
quency components, including noise that interferes with
noise interference and complex pattern modeling through
model learning. This inherent noise affects different fre-
its FreK module, which performs energy-distribution-based
dominantfrequencyselectioninthespectraldomain.Simul- quencies unevenly, causing lower signal-to-noise ratios at
taneously,KANenablessophisticatedpatternrepresentation lower-amplitude frequencies and consequently impairing
whiletimestampembeddingalignmentsynchronizestempo- modelpredictiveperformance.Mitigatingnoiseinterference
ralrepresentationsacrossscales.Thefeaturemixingmodule while blending diverse frequency components makes fore-
thenfusesscale-specificpatternswithalignedtemporalfea- casting particularly challenging. The aforementioned de-
tures.Extensiveexperimentsacrossmultiplereal-worldtime compositionmethodsinspireustodesignamulti-scalefre-
seriesdatasetsdemonstratethatKFSachievesstate-of-the-art
quencydenoisinghybridframeworkcapableofisolatingdif-
performanceasasimpleyeteffectivearchitecture.
ferentfrequencycomponentswhilefilteringhighsignal-to-
noiseratiodata.However,heterogeneousfrequencypatterns
Code—https://github.com/wcnExplosion/KFS-main
introducecomplexrepresentationalchallenges,oftenyield-
ing suboptimal results. Fortunately, Kolmogorov-Arnold
Introduction Network(KAN)(Liuetal.2025)hasrecentlygainedsignif-
Time series forecasting (TSF) is applied in various sig- icant attention in deep learning for its powerful data-fitting
nificant domains, including finance (Huang, Chen, and capabilityandflexibility,demonstratingpotentialtoreplace
Qiao 2024), traffic flow control (Jiang and Luo 2022), traditionalMLPs.ComparedtoMLPs,KANemployslearn-
and weather forecasting (Lam et al. 2023). Recently, deep able activation functions that control its fitting capacity
learning methods have driven continuous progress in the by adjusting basis functions. Moreover, TimeKAN (Huang
TSFfield,withCNN-based (donghaoandwangxue2024), etal.2025),aKANbasedmethod,hasachievedSOTAper-
MLP-based (Nieetal.2023),andTransformer-based (Zeng formanceinmultipledatasets,demonstratingtheremarkable
etal.2023)approaches. potentialofKANfortemporalfeaturerepresentation.These
Due to real-world complexities, observed time series of- considerations motivate us to explore KAN for represent-
ten exhibit intricate and diverse patterns. These interwo- ing patterns across different frequencies, thereby providing
ven patterns result in complex dependencies with substan- moreinformationforforecasting.
tialnoisecontamination,makingitchallengingtoestablish Inspired by these observations, we propose KAN based
connections between historical data and future variations. adaptivefrequencySelectionlearningarchitecture(KFS)to
To capture complex temporal patterns, increasing research addressforecastingchallengesarisingfromnoiseandmixed
focuses on leveraging prior knowledge to decompose time datapattern.Specifically,KFSfirstdecomposescomponents
series into simpler components as the foundation for fore- withinthedataviamovingaverages.Subsequently,theFreK
casting. For example, Autoformer (Wu et al. 2021), DLin- module performs frequency selection at multiple scales to
ear (Zeng et al. 2023), and FEDformer (Zhou et al. 2022a) denoisethedata,utilizingKANtolearnscale-specifictem-
decomposetimeseriesintotrendandseasonalcomponents. poral features from the denoised data. Finally, the hybrid
Building on this, TimeMixer (Wang et al. 2024a) further module aligns and fuses timestamp embeddings from the
5202
guA
6
]GL.sc[
2v53600.8052:viXra

---

# Page 2

lookbackwindowwithcorrespondingscalerepresentations, representation of seasonal patterns. Building on these ad-
achievingtemporalrepresentationalignmentandintegration vances,thisworkleveragesamulti-scaleframeworktocap-
acrossscalestopreciselymodeltemporalfeatures.Features turehierarchicalinformation,proposingKFS’snovelmulti-
fromdifferentscalesareaggregatedviaaveragingandpro- pathwayintegrationframework.Bydistinctlycapturingtem-
jectedtothedesiredforecasthorizonthroughsimplelinear poral representations and physical timestamp embeddings,
mapping.Withourmeticulouslydesignedarchitecture,KFS thenfusingthesecomponents,KFSachievesenhancedpre-
achieves state-of-the-art performance in long-term time se- cisionintimeseriesforecasting.
riesforecastingtasksacrossmultiplereal-worlddatasets.
Ourcontributionscanbesummarizedasfollows: Kolmogorov-ArnoldNetwork
TheKolmogorov-Arnoldrepresentationtheoremestablishes
• Wedesignedanenergy-distribution-basedfrequencyse-
that any multivariate continuous function can be expressed
lectionmethodthateffectivelyextractscomponentswith
as a composition of univariate functions and additive oper-
highersignal-to-noiseratios.TheresultingFreKmodule
ations. Using this theorem, KAN (Liu et al. 2025) intro-
reducesnoiseimpactandenablesefficientmodeling.
ducesanovelnetworkarchitecturethatsupplantstraditional
• We introduced a simple yet effective forecasting model
MLPs. Unlike MLPs with fixed activation functions, KAN
KFS,anddevelopedaMixingBlockthatalignsandfuses
incorporates learnable activation functions. This flexibility
multi-scaletimeserieswithcorrespondingtimestamps.
positionsKANasapromisingalternativetoMLPs.
• Comprehensive experiments demonstrate that our KFS InitialimplementationsofKANfacedcomputationalbot-
achieves state-of-the-art performance in long-term fore- tlenecks due to the excessive complexity of B-spline sam-
casting tasks across multiple datasets while exhibiting pling, hindering broader adoption. To address this limita-
exceptionalefficiency. tion, subsequent research explored alternative basis func-
tions, rKAN (Aghaei 2024) investigates rational functions
RelatedWorks asbasisfunctions,FastKAN (Li2024)acceleratescompu-
tationusingGaussianradialbasisfunctionstoapproximate
TimeSeriesForecasting
third-orderB-splinefunctions.
In recent years, deep learning approaches for TSF have
Furthermore, KAN has been adopted across diverse do-
gained significant attention, mainly including CNN-based,
mains as a substitute for MLP. Convolutional KAN (Bod-
MLP-based,andTransformer-basedmethodologies.
ner et al. 2025) replaces conventional kernels with learn-
CNN-based methods focus on extracting temporal fea-
able spline functions. KAT (Xingyi Yang 2025) integrates
ture representations through convolutional operations. For
KAN layers into Transformer architectures, demonstrating
example, MICN (Wang et al. 2023) and TimesNet (Wu
impressiveaccuracyinmultiplecomputervisiontasks.This
etal.2023)enhancetheaccuracyofsequencemodelingby
paperproposestointroduceKANtoTSFandexploreitspo-
strategically adjusting the receptive fields of their architec-
tentialinrepresentingtemporaldatapatterns.
tures.Transformer-basedapproaches,whilecontrastingwith
CNN methods, exhibit substantially larger receptive fields.
Preliminary
PatchTST (Nie et al. 2023) improves the capture of local
patternsbysegmentinginputdataintopatches,whileCross- Motivation
former (ZhangandYan2023)specializesinminingcross- In the physical world, time series data originate from sen-
variable dependencies. However, Transformer-based mod- sorsonphysicaldevicesorrecordingsofreal-worldrelation-
elsfacechallengesstemmingfromcomputationalcomplex- ships. These measurements inherently contain varying lev-
ity due to their massive parameterization. In this situation, elsofnoiseinterferenceduetofactorsincludingacquisition
MLP-based methods secure their position in TSF through methods,mechanicaltransmissionprocesses,andrecording
lightweight architectures. FITS (Xu, Zeng, and Xu 2024) mechanisms. This noise significantly compromises the re-
introducesnovellinearprojectionstoreduceinputcomplex- sults of time series analysis tasks, particularly forecasting
ity,requiringmerely10Kparameters.However,constrained and anomaly detection. Consequently, developing method-
by their parameterization, MLP-based approaches struggle ologies to mitigate noise-induced distortions becomes im-
toeffectivelyextractandfusediversedatamodalities. perativetoenhancetherepresentationoftemporalpatterns.
Unlike the aforementioned methods, this paper enhance Thispaperaddressesthischallengethroughtheviewofmul-
data quality through spectral filtering strategies and inte- tivariatetimeseriesforecasting.
grateamulti-scaleframeworktoextracttemporalrepresen- Weformallydecomposetheforecastingproblemintotwo
tations, achieving significantly improved accuracy in long fundamentalquestions.
termTimeSeriesForecasting.
1. How can we effectively reduce noise impact on both
dataandpredictivemodels?
Multi-ScaleArchitectureforTSF
2. How can we explicitly extract intrinsic information
In the field of TSF, extensive research has explored multi-
fromgiventimeseries?
scale architectures. TimeMixer (Wang et al. 2024a) pio-
neeredtheirapplicationinTSFthroughdecomposingmulti- For the first question, we begin by assuming that the data
scaletimeseries.MICN (Wangetal.2023)extendedmulti- primarilycontainschannel-wiseindependentadditivewhite
scale processing to convolutional layers, enabling efficient Gaussian noise. The primary mitigation approach for such

---

# Page 3

Temporal Token
Frequency
Adaptive
Band KAN
Embedding Selection
Down-
Sampling Frequency Adaptive
Band KAN AVG
Embedding Selection
Frequency
Adaptive
Band KAN C
Embedding Selection
Embedding
Down Sampling
Projection
Layer
C Concatation Add AVG Average
FreK Mixing Block
C KAN
C KAN
C KAN
C KAN
Output Layer
C KAN
C KAN
Input Data
Time Stamp
Figure1:OverallstructureoftheproposedKFS.Multi-scalearchitecturedecomposestimeseries.TheKANsareseamlessly
integrated within the model framework. FreK select the dominant frequency based on energy distribution and represent the
temporalpattern.MixingBlockaligntemporalrepresentationwithitstimestamp.
noisetraditionallyrequirespriorknowledgeofthenoisedis- Theorem2proposesthatbyfilteringthedominantfrequency
tribution, which introduces additional domain-specific as- bands of a time series, the proportion of noise can be re-
sumptions and hinders real-world applicability. However, duced,therebyenhancingthequalityoftimeseries.
the spectral uniformity of Gaussian white noise in the fre- Forthesecondquestion,wedrawuponexistingresearch
quency domain motivates our solution: By selecting fre- to carefully design a KAN-based network architecture un-
quency bands with concentrated energy as the dominant derthechannelindependenceassumption,integratedwitha
temporal features, we reconstruct the time series within a multi-scaletimeseriesmixingframework.
bounded error margin, effectively attenuating noise. This
principleisformalizedinthefollowingtheorems. MultiscaleTimeSeriesProcessing
Inlongtimeseriesforecasting,temporalsequencescancap-
Theorem1(Parseval’sTheorem) For a discrete signal
ture information from multiple scales by down sampling,
y ∈RLanditsDFTY ∈CL/2+1,theenergysatisfies:
therebyenhancingpredictionaccuracy.Foraninputtimese-
riesX ∈RL×C,wegeneratemulti-scalesequencesthrough
L−1 L/2
(cid:88) |y(t)|2 = 1 (cid:88) |Y[k]|2. (1) down sampling. Specifically, for each coarser-grained sub-
L sequence X , it is derived from the finer-grained sub-
i+1
t=0 k=0 sequence X at the preceding level by applying average
i
pooling. We then sequentially obtain a collection of time
Theorem 1 states that the total energy of a time series is series X = {x ,x ,...,x } across m scales, where each
0 1 m
equivalent in the frequency domain and the time domain. x i ∈ R D L i /×C and D donates the window size of average
Therefore, by processing the time series in the frequency
pooling. The down sampling process used in our work is
domain and converting it back to the time domain, the in-
shownasbelow:
formationoftheoriginaltimeseriescanbepreserved.This
x =AvgPool(x ) (3)
foundationallowsustoformalizeTheorem2,withitscom- i+1 i
Thistechniquehasbeenextensivelyadoptedintimeseries
pleteproofdetailedinAppendix.
forecastingmodelsand hasdemonstratedimproved predic-
Theorem2 Let observed time series y = y 0 + n, where tiveaccuracyalongwithenhancedmodelingcapabilities.
n ∼ N(0,σ2I),andy donatesoriginaltimesseries.After
0
DFT, there exist K ∈ N+ and ϵ > 0 such that the sparse Method
reconstructiony˜fromthetop-K frequenciesofY satisfies:
Overviewofthearchitecture
∥y˜−y ∥ <ϵ. (2) Thecorechallengeliesinresolvingsequencemodelingfor
0 2
channel-independent information while effectively reduc-
ing the influence of noise. To address this, we propose a

---

# Page 4

simple yet effective architecture, the KAN based adaptive Adaptive Embedding In contemporary state-of-the-art
FrequencySelectionlearningarchitecture(KFS),whichim- time series forecasting models, the integration of adap-
provespredictionaccuracybyorganicallyintegratingKAN tive modules into embeddings is frequently addressed. We
tocapturemultiscalechannel-independentfeaturesandtem- also introduce an adaptive parameter P ∈ RD to improve
poralrepresentation.TheoverallarchitectureofKFSisde- prediction efficacy, here D donates the dimension of em-
pictedinFigure 1.Specifically,itconsistsoftwokeycom- bedding space. However, unlike these approaches (Wang
ponents: a Frequency K-top Selection (FreK) Module and etal.2024c),theadaptiveparameterinadaptiveembedding
a Mixing Block. Detailed descriptions of each module are servestolearndistinctcharacteristicsuniquetoeachdataset.
deferredtothefollowingsections. TheusageofP withoneinputseriesx ∈ RL×C isasfol-
i
lows:
FrequencyK-topSelection Ej =concat([P,Linear(xj)]) (8)
i i
In real-world scenarios, a vast number of multivariate where j donates the index of variate. Thus, the whole em-
time series exhibit complex and diverse frequency com- beddingisexpressedasfollows:
ponents. Moreover, among the numerous frequency con-
stituentswithinthesetimeseries,notallcontributemeaning- E i =AE(x i )=[E i 1,E i 2,··· ,E i dmodel] (9)
fullytotherepresentation.Thesesequencescommonlycon- Group-Rational KAN Compared to traditional MLPs,
tain noise that reduces the signal-to-noise ratio of the time KAN replaces fixed activate functions with learnable uni-
series,therebyleadingtosuboptimalperformance. variatefunctions,allowingcomplexnonlinearrelationships
To address this, we designed Frequency K-top Selection to be modeled with fewer parameters and greater inter-
(FreK) module, which reduces noise through multi-scale pretability.Inourmethodology,weemployGroup-Rational
principalfrequencyselectionwhilecomprehensivelycaptur- KANs(XingyiYang2025)tolearnrepresentationsoftem-
ingtemporalrepresentationfromthetimeseries. poral components. The rational base functions are con-
Frequency Band Selection The FreK module first em- structedbyQ(x)andP(x)oforderm,n.
ploys its Frequency Band Selection (FBS) block to P(x) (cid:80)m a xi
screen primary components of time series through energy- ϕ(x)=wF(x)=w Q(x) =w (cid:80) i m =0 b i xi (10)
distribution-based filtering. Since multivariate time series i=0 i
exhibitcomplexenergydistributionsthataredifficulttoex- where a and b are coefficient of the rational function and
i i
tractdirectly,inspiredbyTheorem1,wetransformthetime wisthescalingfactor.
series into the spectral domain, initiating processing from To integrate rational functions as base functions within
the distribution of frequency components. Furthermore, to KANs while mitigating the instability caused by poles,
mitigate noise interference in time series and enhance the which occurs when Q(x)=0, Group-KAN employs a mod-
signal-to-noise ratio, we rank frequency bands in descend- ifiedformulationofthestandardrationalfunction.
ing order of spectral energy and select the top-K bands as a +a x+...+a xm
primaryconstituentsofthetimeseries.Theseselectedbands F(x)= 0 1 m (11)
1+|b x+...+b xm|
aretheninverselytransformedbacktothetemporaldomain 1 m
to reconstruct the time series. As demonstrated in Theo- Thus, Group-Rational KAN incorporates rational func-
rem3,controllingtheenergydistributionthresholdenables tions and constructs its processing architecture through
reconstruction of time series that optimally approximates group seperation and sharing base function within group.
thenoise-freesequence.Here,thereconstructedseriesx˜(t) For an input variable X ∈ Rdin, let i denotes its chan-
comesasfollowed: nelindex.Withg groups,eachgroupinGR-KANcontains
d = d /g channels, where ⌊i/dg⌋ represents the group
x˜(t)=rFFT(TopK(FFT(x(t))) (4) g in
index.TheoperationofGR-KANonxcanbeexpressedas:
whereK istheminimumvalueconductedasfollowed:
GR-KAN(x)=ϕ ◦ x=WF(x) (12)
(cid:80)K X[i]2
i=1 >δ (5) Tosimplifyit,weexpressitinmatrixformastheproductof
(cid:80)L
i=
/
1
2+1X[i]2
aweightmatrixW ∈Rdin×dout andarationalfunctionF:
{X(k)}L/2+1 =sorted[FFT(x(t))] (6)  
w
or
h
d
e
e
r
r
e
,δ
so
d
r
o
t
n
e
a
d
t
[
e
·
s
]d
th
o
e
n
k
a
t
=
h
t
1
e
r
s
es
s
h
o
o
rt
l
i
d
n
o
g
f
b
e
y
n
m
er
a
g
g
y
n
p
it
e
u
r
d
c
e
en
in
ta
d
g
e
e
s
.
cending W =

w 1
. .
.
,1 ·
.
·
..
· w 1
. .
.
,din


(13)
At this stage, x˜(t) consists predominantly of channel- w dout,1 ··· w dout,din
independenttemporalinformationwithlowernoise.Subse-
quently,FrekperformsAdaptiveEmbedding(AE)ofxalong F(x)= (cid:2) F (x ) ··· F (x ) (cid:3)T (14)
the temporal dimension and employs KAN for representa-
⌊1/dg⌋ 1 ⌊din/dg⌋ din
InourimplementationofRationalKAN,wesimplyprefix
tion learning of intrinsic information. This process can be
therationalfunctiontoalinearlayerasaunitofKAN.And
representedbythefollowingformula:
theKANusedinourworkisconsistoftwounits.
E =KAN(AE(x˜(t))) (7)
1
KAN (x)=linear(F(x)) (15)
where AE(·) donates the adaptive embedding, E donates i
1
thetemporalrepresentationbyFreK. whereidonatesthelayerindexinourKAN.

---

# Page 5

Models KFS(Ours) TimeXer TimeMixer iTransformer PatchTST TimesNet MICN DLinear FiLM Time-FFM
Metric MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
rehtaeW
96 0.1590.205 0.1570.205 0.1630.209 0.174 0.214 0.1860.227 0.1720.220 0.1980.261 0.1950.252 0.1950.236 0.1910.230
192 0.2070.249 0.2040.247 0.2110.254 0.221 0.254 0.2340.265 0.2190.261 0.2390.299 0.2370.295 0.2390.271 0.2360.267
336 0.2620.288 0.261 0.290 0.2630.293 0.278 0.296 0.2840.301 0.2800.306 0.2850.336 0.2820.331 0.2890.306 0.2890.303
720 0.3450.342 0.3400.341 0.3440.348 0.358 0.347 0.3560.349 0.3650.359 0.3510.388 0.3450.382 0.3600.351 0.3620.350
Avg 0.2430.271 0.241 0.271 0.2450.276 0.256 0.278 0.2650.285 0.2590.287 0.2680.321 0.2650.315 0.2710.290 0.2700.288
1hTTE
96 0.3680.397 0.382 0.403 0.3850.402 0.386 0.405 0.4600.447 0.3840.402 0.4260.446 0.3950.407 0.4380.433 0.3850.400
192 0.4250.426 0.429 0.435 0.4430.430 0.441 0.436 0.5120.477 0.4360.429 0.4540.464 0.4460.441 0.4940.466 0.4390.430
336 0.4670.446 0.468 0.448 0.5120.470 0.487 0.458 0.5460.496 0.4910.469 0.4930.487 0.4890.467 0.5470.495 0.4800.449
720 0.4540.458 0.469 0.461 0.4970.476 0.503 0.491 0.5440.517 0.5210.500 0.5260.526 0.5130.510 0.5860.538 0.4620.456
Avg 0.4280.431 0.437 0.437 0.4590.444 0.454 0.447 0.5160.484 0.4580.450 0.4750.480 0.4610.457 0.5160.483 0.4420.434
2hTTE
96 0.2800.334 0.286 0.338 0.2890.342 0.297 0.349 0.3080.355 0.3400.374 0.3720.424 0.3400.394 0.3220.364 0.3010.351
192 0.3620.387 0.363 0.389 0.3780.397 0.380 0.400 0.3930.405 0.4020.414 0.4920.492 0.4820.479 0.4050.414 0.3780.397
336 0.4060.421 0.414 0.423 0.4320.434 0.428 0.432 0.4270.436 0.4520.452 0.6070.555 0.5910.541 0.4350.445 0.4220.431
720 0.4230.435 0.408 0.432 0.4640.464 0.427 0.445 0.4360.450 0.4620.468 0.8240.655 0.8390.661 0.4450.457 0.4270.444
Avg 0.3670.394 0.367 0.396 0.3900.409 0.383 0.407 0.3910.441 0.4140.427 0.5740.531 0.5630.519 0.4020.420 0.3820.406
1mTTE
96 0.3140.354 0.318 0.356 0.3170.356 0.334 0.368 0.3520.374 0.3380.375 0.3650.387 0.3460.374 0.3530.370 0.3360.369
192 0.3580.378 0.362 0.383 0.3670.384 0.377 0.391 0.3900.393 0.3740.387 0.4030.408 0.3820.391 0.3890.387 0.3780.389
336 0.3880.398 0.395 0.407 0.3910.406 0.426 0.420 0.4210.414 0.4100.411 0.4360.431 0.4150.415 0.4210.408 0.4110.410
720 0.4600.446 0.452 0.441 0.4540.441 0.491 0.459 0.4620.449 0.4780.450 0.4890.462 0.4730.451 0.4810.441 0.4690.441
Avg 0.3800.394 0.382 0.397 0.3820.397 0.407 0.410 0.4060.407 0.4000.406 0.4230.422 0.4040.408 0.4120.402 0.3990.402
2mTTE
96 0.1730.253 0.171 0.256 0.1750.257 0.180 0.264 0.1830.270 0.1870.267 0.1970.296 0.1930.293 0.1830.266 0.1810.267
192 0.2360.295 0.237 0.299 0.2400.302 0.250 0.309 0.2550.314 0.2490.309 0.2840.361 0.2840.361 0.2480.305 0.2470.308
336 0.2910.332 0.296 0.338 0.3030.343 0.311 0.348 0.3090.347 0.3210.351 0.3810.429 0.3820.429 0.3090.343 0.3090.347
720 0.3950.395 0.392 0.394 0.3920.396 0.412 0.407 0.4120.404 0.4080.403 0.5490.522 0.5580.525 0.4100.400 0.4060.404
Avg 0.2740.319 0.274 0.322 0.2770.324 0.288 0.332 0.2900.334 0.2910.333 0.3530.402 0.3540.402 0.2880.328 0.2860.332
yticirtcelE
96 0.1480.238 0.140 0.242 0.1530.245 0.148 0.240 0.1900.296 0.1680.272 0.1800.293 0.2100.302 0.1980.274 0.1980.282
192 0.1640.253 0.157 0.256 0.1660.257 0.162 0.253 0.1990.304 0.1840.289 0.1890.302 0.2100.305 0.1980.278 0.1990.285
336 0.1810.274 0.176 0.275 0.1850.275 0.178 0.269 0.2170.319 0.1980.300 0.1980.312 0.2230.319 0.2170.300 0.2120.298
720 0.2190.306 0.211 0.306 0.2240.312 0.225 0.317 0.2580.352 0.2200.320 0.2170.330 0.2580.350 0.2780.356 0.2530.330
Avg 0.1780.267 0.171 0.270 0.1820.272 0.178 0.270 0.2160.318 0.1930.304 0.1960.309 0.2250.319 0.2230.302 0.2700.288
1st 40 24 2 0 0 0 0 0 1 2
Table1:Fullresultsofthemultivariatelong-termforecastingresultcomparison.Theinputsequencelengthissetto96forall
baselinesandthepredictionlengthsF ∈{96,192,336,720}.Avgmeanstheaverageresultsfromallfourpredictionlengths.
TimeStampEmbedding FeatureMixing
After specifically learning temporal information from time
Additionally, we introduce linear embeddings for times- seriesatdifferentscales,weneedtoorganicallyintegratethe
tamps.Intherealworld,physicalquantitiescloselyassoci- featurerepresentationslearnedbythemodel.Here,werefer
atedwithtimeseries,suchasmechanicalloadandelectricity tothewidelyadoptedfeedforwardnetwork.Incontrast,we
consumption, exhibit daily, monthly, yearly, and other lev- incorporatetimestampinformationfromthetimeseriesand
els of periodicity along the temporal dimension. By align- replacetheMLPwithaKAN.
ing timestamp information with the latent representations Assuch,thefeaturemixingmodulecanberepresentedby
learned by the model, we can further enhance the model’s thefollowingformula:
ability to understand time series data. While existing ap-
FM(E ,E )=E +KAN([E ,E ]) (16)
proaches (Wang et al. 2024c) incorporate timestamp infor- 1 s 1 1 s
mation to boost model performance, they neglect the crit-
whereE donatesthelinearembeddingoftimestamps.
s
ical synchronization of temporal markers with multi-scale
Forthefusedmultiscaledata,weemployaverageaggre-
sequence patterns. Our methodology resolves this through
gationfollowedbyasimplelinearprojectionlayertogener-
timestampdownsampling,wheretemporalembeddingsare
atethepredictedoutputy˜(t):
progressively coarsened to maintain alignment with corre-
spondingresolutionlevelsintheinputsequencehierarchy. y˜(t)=linear(FM ) (17)
avg

---

# Page 6

whereFM donatesthemeanFMoutputondifferentin- underlined. Lower MSE/MAE values indicate higher pre-
avg
putscales. dictionaccuracy.WeobservethatKFSdemonstratesexcep-
tionalperformanceinalldatasetsexceptfortheECLdataset.
LossFunction TimeXerachievesoptimalresultsonthisparticulardataset,
primarilybecauseitscross-attentionmechanismprovidesa
Incorporating frequency domain alignment terms into loss
strong ability of learning inter-channel relationships. This
functions is not novel. However, unlike previous work
architecture enables TimeXer to better model channel de-
(Wangetal.2025),ourapproachenforcesalignmentexclu-
pendencies, an advantage particularly pronounced in high-
sively on the dominant frequencies of the data. While this
dimensionaldatasetslikeElectricity.
method reduces fine-grained fitting precision, we maintain
Furthermore, both TimeXer and KFS consistently per-
that frequency-domain signals primarily serve as coarse-
formwellinlong-termforecastingtasks,demonstratingthe
grained representations for capturing macro-level trend
models’ strong generalization capabilities and KFS’s well-
shifts.Intuitively,fine-grainedinformationmodelingcanbe
designed framework. Compared with other SOTA models,
sufficiently handled by the MSE loss function alone. The
KFSintroducesaninnovativefrequency-domainprocessing
specificformulationisshownasfollows.
method for time series, extending multivariate forecasting
K frameworks in a new form. By leveraging the characteris-
1 (cid:88)
L = ||F{y˜(t)} −F{y(t)} || (18) ticsofmulti-scaletimeseriesframeworksandskillfullyin-
F K i i
tegratingspecializedfrequency-domainprocessingwithdi-
i
versefeaturerepresentations,KFSachievesoutstandingper-
BycombiningthehybridlossL withtheMSEloss,we
F formanceinmultipletimeseriesforecastingtasks.
arriveatourfinallossfunctionasfollows:
ModelAnalysis
L=αL +(1−α)L (19)
F MSE
Ablation Study To investigate the effectiveness of each
whereαisahyperparameter,y˜(t)donatesthepredictionof component of KFS, we perform detailed ablation of each
KFS,Kdonatestheindexoftop-Kfrequencypredictiondata possibledesignonweatherandETTh2datasets.Asshowin
withthehighestamplitudes.UnlikeFreK,theKhereisset Tab2,wehavefollowingobservations.
to a fixed value of 32. This loss function accounts for both
temporaldiscrepanciesandintroducesalignmentoftheprin-
Models KFS KAN→MLP w/oStamp w/oAE
cipalfrequenciesinthetimeseries.
Metric MSE MAE MSE MAE MSE MAE MSE MAE
Experiments
Datasets We conducted long-term forecasting experi-
ments on six real-world datasets: ETT-Series (Zhou et al.
2021),Electricity(Trindade2015)andWeather(Zhouetal.
2021).Followingestablishedprotocolsfrompreviousstud-
ies (Wuetal.2023;Wangetal.2024b),wesplitthedatasets
of the ETT series into training, validation, and test sets ac-
cordingtoa6:2:2ratio.Fortheremainingdatasets,theratio
is7:1:2.
Baselines We carefully selected representative models
as baselines in field of time series forecasting, includ-
ing: 1)Transformer-based models: TimeXer (Wang et al.
2024c), PatchTST (Nie et al. 2023), iTransformer (Liu
et al. 2024b). 2)CNN-based models: TimesNet (Wu et al.
2023), MICN (Wang et al. 2023). 3)MLP-based models:
TimeMixer(Wangetal.2024a),DLinear(Zengetal.2023).
4)Frequency-basedmodels:FiLM(Zhouetal.2022b).And
atimeseriesfoundationmodelTime-FFM(Liuetal.2024a).
Experimental Settings To ensure fair comparisons, we
adopt the same look-back window length T = 96 and the
same prediction length F = {96,192,336,720}. We use
MeanSquareError(MSE)andMeanAbsoluteError(MAE)
metricstoevaluatetheperformanceofeachmethod.
MainResults
ComprehensiveforecastingresultsareshowninTable1,the
bestresultsarehighlightedinBoldandthesecond-bestare
rehtaew
96 0.159 0.205 0.161 0.205 0.163 0.208 0.163 0.209
192 0.207 0.249 0.208 0.249 0.211 0.251 0.211 0.252
336 0.262 0.288 0.264 0.289 0.262 0.289 0.262 0.288
720 0.345 0.342 0.342 0.340 0.344 0.343 0.347 0.344
Avg 0.243 0.271 0.244 0.271 0.245 0.272 0.245 0.273
2hTTE
96 0.280 0.334 0.284 0.337 0.282 0.335 0.279 0.334
192 0.362 0.387 0.366 0.388 0.365 0.386 0.364 0.386
336 0.406 0.421 0.419 0.426 0.410 0.422 0.414 0.425
720 0.423 0.435 0.435 0.443 0.431 0.444 0.431 0.440
Avg 0.367 0.394 0.373 0.399 0.372 0.396 0.372 0.396
Table2:RsultsofAblationStudyonweatherandETTh2.
For KAN, we substituted it into a standard MLP with
matched parameterization. The consequent deterioration in
errormetricssubstantiatesthatKFS’simplementationofthe
KANdeliverssubstantiallystrongerrepresentationlearning
than conventional MLPs. This evidence validates the func-
tionalsuperiorityofrationalbasisfunctionsforTSF.
For Time Stamp part (w/o Stamp), We replaced the
time stamp embedding with a zero matrix of identical di-
mensions. We observed performance degradation on both
datasets when removing the TimeStamp component. No-
tably, the performance decline was more pronounced on
ETTh2thatisanelectricityequipmentloaddatasetexhibit-
ing stronger temporal periodicity compared to the Weather
dataset. This outcome empirically validates the simple yet
effectivedesignofourTimeStampembeddingmethodology.

---

# Page 7

0.40
0.38
0.2 0.4 0.6 0.8 1.0
scirteM
ETTh1
0.34
0.32
0.30
0.28
0.2 0.4 0.6 0.8 1.0
Energy percent δ
scirteM
ETTh2
MSE
MAE
Figure 2: The impact of δ on metrics. This experiment is
conducted on ETTh1 and ETTh2 datasets with look-back
window96andpredictionlength96.
Methods Top-K(Ours) AvgFilter GaussianFilter
Metric MSE MAE MSE MAE MSE MAE
rehtaew
96 0.159 0.205 0.161 0.208 0.160 0.206
192 0.207 0.249 0.214 0.255 0.211 0.252
336 0.262 0.288 0.272 0.294 0.265 0.289
720 0.345 0.342 0.346 0.342 0.345 0.343
Avg 0.243 0.271 0.248 0.274 0.245 0.272
2hTTE
0.40
0.39
0.38
0.37
0.0 0.2 0.4 0.6 0.8 1.0
96 0.280 0.334 0.292 0.345 0.283 0.336
192 0.362 0.387 0.380 0.399 0.364 0.388
336 0.406 0.421 0.423 0.431 0.407 0.423
720 0.423 0.435 0.437 0.448 0.433 0.443
Avg 0.367 0.394 0.383 0.405 0.372 0.397
Table 3: Rsults of Filter Study On weather and ETTh2
dataset.
For Embedding method (w/o AE), We substituted the
learnable parameter P in the Adaptive Embedding with a
fixedzeromatrixofidenticalshapeanddimensions.
For FreK, we conducted two experiments to investigate
theeffectofTop-KSelection.Inoneexperiment,weevalu-
atedtheimpactofδonmodelperformanceusingtheETTh1
and ETTh2 datasets. In another experiment, we examined
how alternative filtering methods (e.g. mean filtering and
Gaussian filtering) affect model effectiveness on both the
ETTh2andWeatherdatasets.Theresultsofthesetwoexper-
iments are presented in Figure 2 and Table 3, respectively.
Fromtheresults,weobservethatasδincreases,modelmet-
rics generally reach their minimum at δ = 0.9, indicating
thatourenergy-threshold-basedfrequencyselectionstrategy
improvestheperformanceofthemodel.Furthermore,com-
paredtoalternativefilteringmethods,ourapproachachieves
superiorresults,validatingtheeffectivenessoftheTop-Kse-
lectionstrategyinmitigatingnoiseinterference.
For the loss term, we conducted a dedicated experiment
on the ETTh1 dataset to investigate the impact of α on
scirteM
ETTh1
MSE
MAE
0.350
0.325
0.300
0.0 0.2 0.4 0.6 0.8 1.0
α
scirteM
ETTh2
Figure 3: The impact of α on metrics. This experiment is
conductedonETTh1datasetwithpredictionlength96.
Model Memory StepTime FLOPs
PatchTST 807MB 70ms 51.28GB
FEDformer 379MB 70ms 5.28GB
TimesNet 1227MB 50ms 115.85GB
TimeMixer 132MB 13ms 0.62GB
KFS 116MB 21ms 1.66GB
Table4:AcomparisonofusedMemory,TrainingTimeper
stepandFLOPsbetweenKFSandother4models.Toensure
afaircomparison,wefixthepredictionlengthF = 96and
theinputlengthT =96,andsettheinputbatchsizeto32.
model performance, with experimental results presented in
Figure3.Theexperimentalresultsdemonstrateappropriate
calibration of α substantially enhances model capabilities,
experimentally validating the efficacy of our proposed loss
functioncombination.
EfficiencyAnalysis Weconductedacomprehensivecom-
parison of training time, used memory and FLOPs in var-
ious baseline models in the Weather dataset, using official
model configurations and identical batch size. The results
areshowninTable4.ItisclearthatourKFSdemonstrates
significantadvantagesinmemorycostinallmodels.More-
over,theefficiencyofKFSoutperformsotherTransformer-
based and CNN-based models. Furthermore, the training
timeandFLOPsrevealsthatdespiteKFS’sincorporationof
FFT operations, which increase computational complexity,
theoveralltrainingefficiencyremainscompetitive.
Conclusion
In this paper, we propose the KAN-based long term Time
seriesforecasting(KFS)frameworktoaddressspectralnoise
entanglement in complex time series. Comprehensive ex-
periments demonstrate that KFS achieves state-of-the-art
performance in long-term forecasting tasks across diverse
datasets,showcasingsuperiorefficiencyandeffectiveness.

---

# Page 8

References Wang, H.; Pan, L.; Shen, Y.; Chen, Z.; Yang, D.; Yang, Y.;
Zhang,S.;Liu,X.;Li,H.;andTao,D.2025. FreDF:Learn-
Aghaei, A. A. 2024. rKAN: Rational Kolmogorov-Arnold
ingtoForecastintheFrequencyDomain. InTheThirteenth
Networks. arXiv:2406.14495.
InternationalConferenceonLearningRepresentations.
Bodner,A.D.;Tepsich,A.S.;Spolski,J.N.;andPourteau,
Wang,H.;Peng,J.;Huang,F.;Wang,J.;Chen,J.;andXiao,
S. 2025. Convolutional Kolmogorov-Arnold Networks.
Y.2023.MICN:Multi-scaleLocalandGlobalContextMod-
arXiv:2406.13155.
elingforLong-termSeriesForecasting. InTheEleventhIn-
donghao,L.;andwangxue.2024. ModernTCN:AModern ternationalConferenceonLearningRepresentations.
Pure Convolution Structure for General Time Series Anal-
Wang,S.;Wu,H.;Shi,X.;Hu,T.;Luo,H.;Ma,L.;Zhang,
ysis. In The Twelfth International Conference on Learning
J.Y.;andZHOU,J.2024a.TimeMixer:DecomposableMul-
Representations.
tiscaleMixingforTimeSeriesForecasting. InTheTwelfth
Huang,H.;Chen,M.;andQiao,X.2024. GenerativeLearn- InternationalConferenceonLearningRepresentations.
ing for Financial Time Series with Irregular and Scale- Wang,Y.;Wu,H.;Dong,J.;Liu,Y.;Long,M.;andWang,J.
InvariantPatterns. InTheTwelfthInternationalConference 2024b.DeepTimeSeriesModels:AComprehensiveSurvey
onLearningRepresentations. andBenchmark.
Huang,S.;Zhao,Z.;Li,C.;andBAI,L.2025. TimeKAN: Wang, Y.; Wu, H.; Dong, J.; Liu, Y.; Qiu, Y.; Zhang, H.;
KAN-based Frequency Decomposition Learning Architec- Wang,J.;andLong,M.2024c.Timexer:Empoweringtrans-
ture for Long-term Time Series Forecasting. In The Thir- formers for time series forecasting with exogenous vari-
teenth International Conference on Learning Representa- ables. AdvancesinNeuralInformationProcessingSystems.
tions. Wu, H.; Hu, T.; Liu, Y.; Zhou, H.; Wang, J.; and Long, M.
Jiang,W.;andLuo,J.2022.Graphneuralnetworkfortraffic 2023.TimesNet:Temporal2D-VariationModelingforGen-
forecasting: A survey. Expert Systems with Applications, eral Time Series Analysis. In International Conference on
207:117921. LearningRepresentations.
Wu, H.; Xu, J.; Wang, J.; and Long, M. 2021. Auto-
Lam,R.;Sanchez-Gonzalez,A.;Willson,M.;Wirnsberger,
former:DecompositionTransformerswithAuto-Correlation
P.; Fortunato, M.; Alet, F.; Ravuri, S.; Ewalds, T.; Eaton-
forLong-TermSeriesForecasting.InRanzato,M.;Beygelz-
Rosen, Z.; Hu, W.; Merose, A.; Hoyer, S.; Holland, G.;
imer, A.; Dauphin, Y.; Liang, P.; and Vaughan, J. W., eds.,
Vinyals, O.; Stott, J.; Pritzel, A.; Mohamed, S.; and
Advances in Neural Information Processing Systems, vol-
Battaglia, P. 2023. Learning skillful medium-range global
ume34,22419–22430.CurranAssociates,Inc.
weatherforecasting. Science,382(6677):1416–1421.
Xingyi Yang, X. W. 2025. Kolmogorov-Arnold Trans-
Li,Z.2024.Kolmogorov-ArnoldNetworksareRadialBasis
former. In The Thirteenth International Conference on
FunctionNetworks. arXiv:2405.06721.
LearningRepresentations.
Lin, S.; Lin, W.; Wu, W.; Chen, H.; and Yang, J. 2024.
Xu, Z.; Zeng, A.; and Xu, Q. 2024. FITS: Modeling Time
SparseTSF: Modeling Long-term Time Series Forecasting
Serieswith$10k$Parameters. InTheTwelfthInternational
with *1k* Parameters. In Forty-first International Confer-
ConferenceonLearningRepresentations.
enceonMachineLearning.
Zeng,A.;Chen,M.;Zhang,L.;andXu,Q.2023.AreTrans-
Liu, Q.; Liu, X.; Liu, C.; Wen, Q.; and Liang, Y. 2024a. formersEffectiveforTimeSeriesForecasting?
Time-FFM: Towards LM-Empowered Federated Founda-
Zhang,Y.;andYan,J.2023. Crossformer:TransformerUti-
tionModelforTimeSeriesForecasting.InTheThirty-eighth
lizing Cross-Dimension Dependency for Multivariate Time
Annual Conference on Neural Information Processing Sys-
SeriesForecasting.InInternationalConferenceonLearning
tems.
Representations.
Liu, Y.; Hu, T.; Zhang, H.; Wu, H.; Wang, S.; Ma, L.; and Zhou, H.; Zhang, S.; Peng, J.; Zhang, S.; Li, J.; Xiong, H.;
Long, M. 2024b. iTransformer: Inverted Transformers Are and Zhang, W. 2021. Informer: Beyond Efficient Trans-
EffectiveforTimeSeriesForecasting. InTheTwelfthInter- former for Long Sequence Time-Series Forecasting. In
nationalConferenceonLearningRepresentations. TheThirty-FifthAAAIConferenceonArtificialIntelligence,
Liu,Z.;Wang,Y.;Vaidya,S.;Ruehle,F.;Halverson,J.;Sol- AAAI 2021, Virtual Conference, volume 35, 11106–11115.
jacic, M.; Hou, T. Y.; and Tegmark, M. 2025. KAN: Kol- AAAIPress.
mogorov–ArnoldNetworks.InTheThirteenthInternational Zhou, T.; Ma, Z.; Wen, Q.; Wang, X.; Sun, L.; and Jin, R.
ConferenceonLearningRepresentations. 2022a.FEDformer:Frequencyenhanceddecomposedtrans-
Nie, Y.; Nguyen, N. H.; Sinthong, P.; and Kalagnanam, J. formerforlong-termseriesforecasting. InProc.39thInter-
2023. A Time Series is Worth 64 Words: Long-term Fore-
nationalConferenceonMachineLearning(ICML2022).
casting with Transformers. In The Eleventh International Zhou,T.;Ma,Z.;xuewang;Wen,Q.;Sun,L.;Yao,T.;Yin,
ConferenceonLearningRepresentations. W.;andJin,R.2022b.FiLM:FrequencyimprovedLegendre
MemoryModelforLong-termTimeSeriesForecasting. In
Trindade, A. 2015. ElectricityLoadDiagrams20112014.
Oh, A. H.; Agarwal, A.; Belgrave, D.; and Cho, K., eds.,
UCI Machine Learning Repository. DOI:
AdvancesinNeuralInformationProcessingSystems.
https://doi.org/10.24432/C58C86.

---

# Page 9

Appendix Algorithm1:TheOverallArchitectureofKFS
ProofofTheory2 Input:look-backsequenceX ∈RL×C,timestampsT ∈.
Parameter:Energythresholdδ,Lossfunctionhyperparam-
Theorem3 Theory 2 Let observed time series y = y +
0 eterα,Downsamplinglayernumbern.
n, where n ∼ N(0,σ2I), and y donates original times
0 Output:Predictionsyˆ
series.AfterDFT,thereexistK ∈ N+ andϵ > 0suchthat
1: X=XT
thesparsereconstructiony˜fromthetop-KfrequenciesofY
satisfies: 2: {X 0 ,X 1 ,...,X n }=Downsampling(X)
∥y˜−y ∥ <ϵ. (20) 3: {T 0 ,T 1 ,...,T n }=Downsampling(T)
0 2 4: foriin{0,...,n}do
5: X i =RevIn(X i ,’norm’)
tha P t r P o ( o ∥ f y˜ . − To y 0 p ∥ ro 2 v > e T ϵ h ) e h o a re s m an 2 u , p i p t e s r uf b fi o c u e n s d to µ d < em 1 o , n w st h r i a c t h e 6 7 8 : : : E E F 1 s M i i = = i L F = r in e E K e i a ( r X + (T i K i ) ) AN([Ei,Ei])
reducestoverifyingthefollowinginequality: 1 1 s
9: endfor
10: FM avg = n+ 1 1 (cid:80)n i=0 FM i
Cσ2K+ (cid:80) |Y(j)|2 11: yˆ=linear(FM avg )
P(cid:0) ∥y˜−y ∥2 >ϵ (cid:1) ≤ j>K 0 <1, 12: returnyˆ
0 2 ϵ
whereY(j) isthej-thlargestDFTcoefficientofy ,C > 0
0 0
isaconstantvalue. DetailedAlgorithmDescription
Thereconstructionerrordecomposesintotwoparts: The pseudocode of the KFS algorithm is shown in Algo-
rithm 1. The algorithm initializes the input data and pa-
K
∥y˜−y ∥2 = (cid:88) |Y(j)|2 + (cid:88) |N(j)|2 . rameters and performs normalization. After downsampling
0 2 0 method,thedataistheniteratedthroughFreKblocktoex-
j>K j=1 tract multi-scale information. The time stamp is also pro-
(cid:124) (cid:123)(cid:122) (cid:125) (cid:124) (cid:123)(cid:122) (cid:125)
SignalEnergyLoss RetainedNoiseEnergy cessed by downsampling method and embedded by linear
embeddingmethod.MixingBlocksfuseeachscaledfeature
1. Signal energy loss: By Parseval’s theorem, with its time stamp, respectively. Following this, all fused
(cid:80) |Y(j)|2 is the energy discarded from the featuresarecombinedviaaveragemethodatfeaturedimen-
j>K 0
true signal. Since y has finite energy (∥y ∥2 < ∞), sion. The prediction output is conducted by linear projec-
0 0 2
(cid:80) |Y(j)|2 →0asK →∞. tion.
j>K 0
2. Retainednoiseenergy:Thecoefficients|N(j)|2 follow DetailsofExperiments
a chi-square distribution χ2 2K (real and imaginary parts Detailed Dataset Descriptions Detailed descriptions of
ofcomplexGaussianareindependent).ByMarkov’sin- thedatasetsareshowninTable6.Dimdenotesthenumber
equality: of channels in each dataset. Dataset Size denotes the total
 (cid:88) K  E (cid:104) (cid:80)K j=1 |N(j)|2 (cid:105) Kσ2 n sp u e m ct b i e v r el o y f .P ti r m ed e ic p t o io in n ts L i e n ng (T th ra d i e n n , o V t a e l s id th a e tio fu n t , u T re es t t i ) m s e pl p it o , in re ts -
P  |N(j)|2 >t≤ = . to be predicted, and four prediction settings are included
t t
j=1 ineachdataset.Frequencydenotesthesamplingintervalof
timepoints.Informationreferstothemeaningofthedata.
3. Jointbound:Foranyϵ > (cid:80) |Y(j)|2,setϵ = ϵ−
j>K 0 1 Baseline Models We briefly describe the selected base-
(cid:80) |Y(j)|2.Then: lines:
j>K 0
TimeXer(Wangetal.2024c)TimeXerisaTransformer-
 
P(cid:0) ∥y˜−y 0 ∥2 2 >ϵ (cid:1) ≤P  (cid:88) K |N(j)|2 >ϵ 1≤ K ϵ σ 1 2 . b p va a le r s m i e a d b en l m e t s a o r t d y h e r l o in t u h p g a u h t ts a i , n c c a r o c o r h s p i s o e - v a ra t i t n t e e g n s ti t e o h x n e o i g r m e e i n n c o t h e u a g s n r v i a s t a m i r o i . n abl w es ith as in su p p u - t
j=1
PatchTST(Nieetal.2023)isaTransformer-basedmodel
Substitutingϵ givestheresultwithC =1. utilizingpatchingandCItechnique.Italsoenableeffective
1
pretrainingandtransferlearningacrossdatasets.
Obviously,thereexistatleastoneK andoneϵsatisfying
iTransformer (Liu et al. 2024b) embeds each time series
Kσ2 <ϵ− (cid:80) j>K |Y 0 (j)|2,thenwecangettheupperbound as variate tokens and is a fundamental backbone for time
is: seriesforecasting.
Kσ2 Kσ2 TimesNet (Wu et al. 2023) is a CNN-based model with
= <1
ϵ 1 ϵ− (cid:80) |Y(j)|2 TimesBlock as a task-general backbone. It transforms 1D
j>K 0 timeseriesinto2Dtensorstocaptureintraperiodandinter-
Therefore,theory2isproven. periodvariations.

---

# Page 10

Dataset Dim PredictionLength DatasetSize Frequency Information
ETTh1,ETTh2 7 {96,192,336,720} (8545,2881,2881) Hourly Electricity
ETTm1,ETTm2 7 {96,192,336,720} (34465,11521,11521) 15min Electricity
Weather 21 {96,192,336,720} (36792,5271,10540) 10min Weather
ECL 321 {96,192,336,720} (18317,2633,5261) Hourly Electricity
Table5:Detaileddatasetdescriptions.
Dataset ETTh1 ETTh2
Metric MSE MAE MSE MAE
96 0.371±0.002 0.397±0.001 0.290±0.004 0.343±0.003
192 0.434±0.006 0.429±0.002 0.370±0.004 0.391±0.002
336 0.467±0.002 0.446±0.001 0.420±0.008 0.426±0.004
720 0.468±0.012 0.466±0.005 0.423±0.006 0.435±0.004
Dataset ETTm1 ETTm2
Metric MSE MAE MSE MAE
96 0.313±0.002 0.353±0.003 0.172±0.001 0.253±0.001
192 0.359±0.001 0.378±0.001 0.236±0.001 0.295±0.001
336 0.389±0.001 0.400±0.001 0.292±0.001 0.331±0.001
720 0.459±0.004 0.445±0.002 0.394±0.001 0.391±0.001
Table6:MeanvaluesandstandarddeviationsofKFS.
MICN (Wang et al. 2023) is a CNN-based model com- Hyper-ParameterSelectionandImplementationDetails
bining local features and global correlations to capture the For the main experiments, we have the following hyper-
overallviewoftimeseries. parameters. The dimension of embedding d . The hid-
model
TimeMixer (Wang et al. 2024a) is an MLP-based model denstateofKANd ff .d model andd ff aresetviahyperpa-
introducing multiscale mixing technology. It achieves a rametersearchingamongtherangeof{128,256,512,1024}
complextemporalpatternrepresentationwithseasonaltrend ford model and{256,512,1024,2048}ford ff .Andweset
decomposition. α=0.3andδ =80%intheETTm1,ETTm2,Weatherand
DLinear (Zeng et al. 2023) is an MLP-based model ECL datasets. For ETTh1 and ETTh2, we search α in the
with just one linear layer, which unexpectedly outperforms range of 0 to 1 with step 0.1. And for δ, the step is 0.05.
transformer-basedmodelsinlong-termTSF. DetailedhyperparameterscanbefoundattheCode&Data
Appendix.
FiLM(Zhouetal.2022b)isanMLP-basedmodel.Itcon-
ductstemporalpatternrepresentationbylegendrepolynomi-
alsprojectionsandfourierprojection.
Time-FFM (Liu et al. 2024a) is foundation model using sectionExtraExperimentalResults
LLM. It aligns modality representation and is empowered
subsectionRobustness Evaluation To get more robust ex-
bylanguagemodel.
perimental results, we repeat each experiment three times
withfiveseeds(2020-2024)intheETTh1,ETTh2,ETTm1,
Metric Details Regarding metrics, we utilize the mean
ETTm2 datasets, demonstrating that KFS performance is
square error (MSE) and mean absolute error (MAE) for
stable. For easier comparison, the results are shown in the
long-termforecasting.Thecalculationsofthesemetricsare:
maintextwhentheseedissetto2021.Allexperimentsare
conductedusing PyTorchon anNVIDIA 409024GB GPU
T
MSE = 1 (cid:88) (yˆ −y )2 andarerepeatedthreetimesforconsistency.
T i i
i=0 DiscussionsonLimitationsandFuture
Improvement
T
MSE = 1 (cid:88) |yˆ −y | Recently,severalspecificdesignshavebeenutilizedtobetter
T i i capture complex sequential dynamics, such as RevIN, Fre-
i=0

---

# Page 11

quencyRepresentation,KANmethodandChannelIndepen-
dence.
(1)RevIN: Real-world time series always exhibit non-
stationarybehavior,wherethedatadistributionchangesover
time.RevInisanormalization-and-denormalizationmethod
for TSF to effectively constrain non-stationary information
(mean and variance) in the input layer and restore it in the
output layer. The work has managed to improve the delin-
eationoftemporaldependencieswhileminimizingtheinflu-
enceofnoise.InKFS,wealsoadoptthemethodofRevIN.It
isusedfornormalizingeachscaleddata,respectively(Fig-
ure 4. And the output is denormalized by the RevIN layer
for original scale. However, it is difficult to adequately ad-
dress the intricate distribution shifts between layers within
deep networks, necessitating further refinement to resolve
suchshifts.
(2)Frequency representation: TS data, characterized by
theirinherentcomplexityanddynamicnature,oftencontain
informationthatissparseanddispersedacrossthetimedo-
main. The frequency domain representation is proposed to
promise a morecompact and efficient representation of the
inherent patterns. KFS minimizes the impact of noise via
Frequency Band Selection showed in Figure 5. However,
some overlooked periods or trend changes may represent
significantevents,resultinginlossofinformation.
(3)KAN method: KAN have emerged as a promising
candidate to potentially replace MLPs, demonstrating ex-
ceptional representational capabilities. However, their sub-
stantialcomputationaloverheadandrelativelyhomogeneous
base functions have constrained their applicability to di-
verse domains, prompting the development of numerous
variants. While these variants have achieved notable suc-
cesses in their respective fields, there is no existing work
thathasyetdesignedefficientbasefunctionsspecificallyop-
timizedfortimeseriesrepresentation.OurKFSframework
employs rational KAN as its feature representation back-
bone. Consequently, our future research will focus on de-
velopingdomain-specificKANvariantsgroundedinthein-
trinsicmechanismsoftimeseriesdata.
(4) Channel Independence (CI): the CI method sac-
rifices capacity in favor of more reliable predictions.
PatchTST (Nie et al. 2023) achieves SOTA results using
theCIapproach.However,neglectingcorrelationsbetween
channels may lead to incomplete modeling. In KFS, we
leverage the CI approach without integrating dependencies
across different variables over time. However, in multivari-
ate forecasting modeling, solely considering channel-wise
information is incomplete as it neglects inter-channel de-
pendencies. On the other hand, the complex trade-off be-
tween channel-specific patterns and cross-channel relation-
ships complicates the integration mechanisms within mod-
els.Therefore,ourfutureworkwillfurtherexplorechannel
correlation pattern discovery and effective fusion methods
fordiverseinformationsources.
We believe that more effective sequence modeling mod-
els will be proposed to adequately address issues such as
distributionshift,multivariatesequencemodeling,etc.Asa
result, KAN-based models have great potential waiting for
furtherexplorationinmoreareasoftimeseries.

---

# Page 12

Rebuild Rescale
Scale 1
RevIn KT
Scale N
Figure4:TheDesignforSequentialModelling(RevIn)
FFT
& Masking rFFT
Energy Threshold boundary Energy Threshold boundary
Sort
Zero Masking
Input Data Output Data
Figure5:TheTop-KSelectioninourwork.Thesortoperationisonlyusedforsearchtheindexoffrequency.