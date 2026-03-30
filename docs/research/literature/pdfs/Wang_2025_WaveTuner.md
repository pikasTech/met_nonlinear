WaveTuner: Comprehensive Wavelet Subband Tuning for Time Series Forecasting
YuboWang1,HuiHe1,ChaoxiNiu2 ZhendongNiu1
1BeijingInstituteofTechnology
2UniversityofTechnologySydney
Abstract
root:4.53
Due to the inherent complexity, temporal patterns in real-
world time series often evolve across multiple intertwined
scales, including long-term periodicity, short-term fluctu-
ations, and abrupt regime shifts. While existing litera-
ture has designed many sophisticated decomposition ap-
proaches based on the time or frequency domain to parti- a:3.82 d:1.24
tion trend–seasonality components and high–low frequency
components, an alternative line of approaches based on the
waveletdomainhasbeenproposedtoprovideaunifiedmulti-
resolutionrepresentationwithprecisetime–frequencylocal-
ization. However, most wavelet-based methods suffer from aa: 3.09 ad: 0.57 da: 0.26 dd: 0.33
apersistentbiastowardrecursivelydecomposingonlylow-
frequencycomponents,severelyunderutilizingsubtleyetin-
formativehigh-frequencycomponentsthatarepivotalforpre-
cisetimeseriesforecasting.Toaddressthisproblem,wepro-
pose WaveTuner, a Wavelet decomposition framework em-
powered by full-spectrum subband Tuning for time series
forecasting.Concretely,WaveTunercomprisestwokeymod-
ules: (i) Adaptive Wavelet Refinement module, that trans-
forms time series into time-frequency coefficients, utilizes
an adaptive router to dynamically assign subband weights,
and generates subband-specific embeddings to support re-
finement; and (ii) Multi-Branch Specialization module, that
employs multiple functional branches, each instantiated as
a flexible Kolmogorov–Arnold Network (KAN) with a dis-
tinct functional order to model a specific spectral subband.
Equipped with these modules, WaveTuner comprehensively
tunes global trends and local variations within a unified
time–frequency framework. Extensive experiments on eight
real-world datasets demonstrate WaveTuner achieves state-
of-the-artforecastingperformanceintimeseriesforecasting.
Introduction
Time series forecasting, which aims to infer future val-
uesfromtemporalpatternsofhistoricalobservations,plays
a pivotal role in a wide range of real-world applications,
such as transportation management (Cirstea et al. 2022),
inventory optimization (Seyedan, Mafakheri, and Wang
2023), and climate modeling (Haq 2022). In recent years,
various deep learning models based on diverse architec-
tures—suchasRNNs(Amalou,Mouhni,andAbdali2022),
CNNs (Mehtab and Sen 2022), Transformers (Woo et al.
Copyright©2026,AssociationfortheAdvancementofArtificial
Intelligence(www.aaai.org).Allrightsreserved.
<
3.66 0.59
<
3.66 0.59
<
shannonentropy
time series
1stdecompose
4.25
level 1
2nddecompose
level 2
(a)Entropy–basedtwo-levelwaveletpacketdecomposition
dnabycneuqerF
edutilpmA
(b)WaveletSpectraVisualizationofa(Left)andd(Right)
Figure1:Thecriticalroleofanalyzinghigh-frequencycom-
ponentsinwaveletdecomposition.
2024), and MLPs (Zeng et al. 2023)—have gained signif-
icant attention and driven notable progress for time series
forecasting(LimandZohren2021).
Despite these impressive advances, modeling time se-
ries remains fundamentally challenging due to the intrin-
sic complex nature of the real world, where temporal pat-
terns unfold across multiple entangled scales, including
long-termperiodicity,short-termfluctuations,abruptregime
shifts, etc (Zhang et al. 2025a; Piao et al. 2024a). To
tackle such complex temporal patterns, a compelling strat-
egy is to leverage prior knowledge to decompose time se-
ries into trend and seasonal components (Wu et al. 2021;
Zhou et al. 2022; Zeng et al. 2023), further enriched with
multi-scale refinements that capture cross-scale interac-
tions(Wangetal.2024a),orintochunkswithdifferentpe-
riod lengths (Wu et al. 2022). Concurrently, the frequency
domain has emerged as a powerful alternative to conven-
tional time-domain approaches by providing global view
5202
voN
42
]GL.sc[
1v64881.1152:viXra

andenergycompaction,twoadvantagedpropertiesinacces- frequency characteristics: low-frequency subbands benefit
sibleinthetimedomain(Yietal.2023a),promptingasurge fromsmoother,low-orderfunctionstocaptureglobaltrends,
of interest in decomposing time series into high- and low- whilehigh-frequencysubbandsrequirehigher-orderexpres-
frequencycomponents(Piaoetal.2024b;Huangetal.2025; sivenesstomodelrapidlychanginglocalpatterns.
Wuetal.2025).Nevertheless,frequency-baseddecomposi- Ourcontributionscanbesummarizedasfollows:
tion remains fundamentally constrained in capturing time-
• We reveal a strong bias toward high-frequency compo-
sensitive patterns that evolve dynamically over time. Sur-
nents of current wavelet-based solutions, and propose
passingtheinherentlimitationsofpuretime-orfrequency-
WaveTuner, a novel wavelet decomposition framework
domain approaches, the wavelet domain is rapidly gaining
that enables full-spectrum subband tuning for effective
momentumforitsuniqueabilitytounifytimeandfrequency
timeseriesforecasting.
analysis,yieldingmulti-resolutionandtime-sensitiverepre-
• WeintroducetheAWRmoduletotransformtimeseries
sentationswithstronglocalizationacrossbothdomains(Guo
into time-frequency coefficients and dynamically assign
etal.2022).
importance weights to each subband, enabling adaptive
However,wavelet-empoweredforecastersarestillsuffer-
emphasisacrossthefrequencyspectrum.
ing from a persistent bias toward recursively decompos-
ing only low-frequency signals (i.e., approximation coef- • We then introduce the MBS module to leverage
ficients), rendering them particularly vulnerable to high- frequency-specific KAN-based subnetworks with vary-
frequency signals (i.e., detail coefficients)—subtle yet in- ingfunctionalorderstoalignmodelexpressivenesswith
formative components for accurately forecasting time se- spectralcharacteristics.
ries. Such bias severely undermines the full potential of • Extensive experiments on eight forecasting benchmarks
the wavelet domain. To highlight the importance of high- demonstrate the superiority of our model over state-of-
frequency signals, Figure 1 (a) illustrates a two-level op- the-artmethods.
timal subband tree guided by Shannon entropy. Although
thehigh-frequencybanddistypicallyunderexploredbyex- RelatedWorks
isting methods (Yi et al. 2024), it exhibits a high entropy
Deep Time Series Forecasting. Recent advances in TSF
of 1.24, suggesting the presence of rich structural informa-
span various architectural paradigms, including CNN-,
tion.Uponfurtherdecompositionofd,thecomponentofdd
RNN-,Transformer-,andMLP-basedmethods.Earlymod-
stillexhibitspronouncedperiodicpatterns(seeredcircles),
els such as DeepAR (Salinas et al. 2020) and SCINet (Liu
indicating that d retains entangled yet structured temporal
et al. 2022) utilized RNN and CNN structures to cap-
patternsthatmeritdeeperdecompositionformoreeffective
ture temporal dependencies, but struggled with long-
modeling. Additionally, the wavelet spectra of da and dd
range forecasting. Transformer-based models, such as In-
exhibitstrongtime-localizedinformation(seeFigure1(b)),
former (Zhou et al. 2021), Autoformer (Wu et al. 2021),
on par with those observed in the aa ← a → ad branch.
Crossformer(ZhangandYan2023),andiTransformer(Liu
This observation further reinforces the necessity of deeper
et al. 2023), have significantly improved long-horizon pre-
decomposition to isolate more informative time-frequency
diction through sparse attention, series decomposition, and
characteristics.
patch-based representations (Nie et al. 2022). More re-
Toaddresstheaforementionedissues,weproposeWave-
cently,MLP-basedapproaches(TangandZhang2025)have
Tuner, a Wavelet decomposition framework empowered by
gained attention due to their architectural simplicity and
full-spectrumsubbandTuningforeffectivetimeseriesfore-
competitiveperformance.DLinear(Zengetal.2023),RLin-
casting. The core idea of WaveTuner is to adaptively focus
ear (Li et al. 2023), and TimeMixer (Wang et al. 2024b)
onhigh-frequencydetailcoefficientsacrossmulti-resolution
employtrend-remainderdecomposition,MLPormulti-scale
waveletsubbands,facilitatingthediscoveryofoptimalsub-
mixing strategies. PatchMLP (Tang and Zhang 2025) and
band routing patterns tailored to each time series input.
TVNet (Li, Li, and Diao 2025) further show that patch-
Specifically, we introduce the Adaptive Wavelet Refine-
ingenhanceslocaltemporalpatternmodeling.Beyondtime-
ment (AWR) module, which transforms time series into
domain modeling, frequency-aware methods have emerged
time-frequency coefficients and utilizes an adaptive router
as an effective alternative. FredFormer (Piao et al. 2024b),
to dynamically assign subband weights, enabling subband-
FilterNet (Yi et al. 2024), and ReFocus (Yu et al. 2025)
specificrefinementthatenhancesthemodel’sabilitytocap-
leverage Fourier transforms to highlight mid- or high-
ture localized frequency dynamics. These coefficients are
frequencyinformation.TimeKAN(Huangetal.2025)com-
further refined to model inter-variable dependencies via
binesfrequencydecompositionwithMulti-orderKANs(Liu
hardware-friendly linear layers with residual connections,
et al. 2024b), capturing nonlinear dynamics across differ-
yieldingfinertime-frequencyrepresentationsthatempower
ent frequency bands. In contrast to conventional time- or
WaveTuner to capture more informative and discriminative
frequency-domain approaches, WaveTuner extracts contin-
patterns across diverse spectral bands. Inspired by the ex-
uouswaveletsubbandfeaturestoconstructmulti-resolution
ceptional data-fitting capacity of Kolmogorov-Arnold Net-
representationsthatarebothtemporallysensitiveandwell-
works (KAN), we design the Multi-branch Specialization
localized.
(MBS)module,whereeachbranch—instantiatedasaKAN
of different functional order—is specialized for a specific Wavelet Analysis in Time Series Modeling Unlike the
spectral band. This design aligns model complexity with Fourier transform, the wavelet transform offers time-

frequency localization, enabling signal modeling at mul- AdaptiveWaveletRefinement
tiple resolutions. WPMixer (Murad, Aktukmak, and Yil-
As shown in the upper-left part of Figure 2, AWR
maz 2025) leverages wavelet-based multilevel decomposi-
moduel consists Wavelet Packet Decomposition, Adaptive
tionandintegratespatchmechanismstomodelwaveletco-
Frequency-awareWeightingandWaveEmbedding.
efficients. AdaWaveNet (Yu, Guo, and Sano 2024) decom-
poses time series into seasonal and trend components and Wavelet Packet Decomposition. Since time series data
appliesaliftingschemetomodeltheseasonalpart.Wavelet- often exhibit non-stationary behavior, RevIN (Kim et al.
Mixer(Zhangetal.2025b)utilizesmulti-resolutionwavelet 2021) is employed for both normalization prior to wavelet
decomposition combined with a lightweight MLP-mixer packetdecomposition(WPD)anddenormalizationafterthe
architecture to enhance long-term multivariate time series reconstruction. WPD extends traditional wavelet decompo-
forecasting. WFTNET (Liu et al. 2024a) combines Fourier sition by recursively applying both low-pass and high-pass
transformandwavelettransformtoexploreglobalandlocal filtersateachlevel,enablingafullbinarytreedecomposition
periods. WTFTP (Zhang et al. 2023) combine the Wavelet oftheinput.Thisapproachpreservespotentiallyvaluablein-
Transformer with the encoder and decoder structures to formation contained in both low- and high-frequency com-
predict aircraft trajectories. WaveRoRA (Liang, Sun, and ponents. Specifically, the normalized time series is trans-
Guizani 2024) improves prediction performance by learn- formed into a set of multi-level wavelet packet coefficients
ing the relationship between frequency bands through the withenrichedrepresentationalcapacity,andthewaveletco-
route attention mechanism. Wavelet transforms, when inte- efficientscanbeexpressedas:
grated with deep architectures such as CNNs and RNNs,
WPD(X ,ψ,m)={X [i]|i∈{1,...,2m}}
have demonstrated substantial performance gains in vari- L w
ous tasks (Stefenon et al. 2023, 2024). Moreover, wavelet = (cid:110) band(m) (cid:12) (cid:12)band ∈{a,d}m, j =1,...,2m (cid:111) , (1)
packet transforms offer strong potential for time-series de- j (cid:12) j
noising, further enhancing robustness in downstream mod-
wheremdenotesthenumberofdecompositionlevels,ψrep-
eling (Frusque and Fink 2024). In this paper, we explore
resentsthewaveletfunction,andnindicatesthenumberof
a
re
f
s
r
o
e
l
q
u
u
ti
e
o
n
n
cy
d
-
e
a
c
w
o
a
m
re
po
m
si
o
t
d
io
e
n
lin
w
g
it
a
h
pp
a
r
n
oa
a
c
d
h
ap
th
ti
a
v
t
e
c
r
o
o
m
ut
b
e
i
r
ne
to
sm
be
u
t
l
t
t
e
i-
r
wavelet coefficients of X
w
[i] ∈ RC×Li obtained after de-
compositionwithL beingthelengthofwaveletcoefficent.
capturethediversedynamicsinmultivariatetimeseries. i
Eachsubbandislabeledasband(m) ∈ {a,d}m,whichrep-
j
resentsauniquepathfromtheroottoaleafnodeinthefull
Methodology
binarytree.Forinstance,withm=2,theresultingsubbands
ProblemFormulation are aa, ad, da, and dd, corresponding to different combi-
For time series forecasting, given an input multivariate nations of approximation a and detail d operations applied
time series X = {x ,x ,...,x ,x } ∈ acrosslevels.
L t−L+1 t−L+2 t−1 t
RC×L, the goal is to predict the future time series X =
T Adaptive Frequency-aware Weighting. To effectively
{x ,x ,...,x } ∈ RC×T, where x ∈ R1×C de-
t+1 t+2 t+T t leveragethemulti-bandwaveletpacketcoefficientsobtained
notesamultivariatedatapointattimet,C isthenumberof
throughdecomposition,weproposeanadaptivefrequency-
the variables, L and T are the length of look-back window
aware weighting module, which functions as a soft routing
andhorizonwindow.
mechanism.Insteadofprocessingallfrequencycomponents
equally,thismoduledynamicallyassignsimportancescores
OverviewofWaveTuner
toeachsubbandbasedontheinputcharacteristicsandfore-
The overall framework of WaveTuner is illustrated in Fig- castingobjective.Inthisway,itservesasanadaptiverouter
ure 2. WaveTuner consists of two core components: the that selectively emphasizes informative frequency compo-
AdaptiveWaveletRefinement(AWR)moduleandtheMulti- nents while suppressing irrelevant or noisy ones, guiding
Branch Specialization (MBS) module. The AWR module downstreammodulestofocusontask-relevantsignals.
firstapplieswaveletpacketdecompositiontothenormalized Specifically, for each frequency subband X [i] obtained
w
timeseries,generatingmulti-resolutionwaveletcoefficients. fromthewaveletpacketdecomposition,itisfirstprocessed
An adaptive routing mechanism is then employed to dy- throughanaveragepoolingoperationtosummarizeitssig-
namicallyassignimportanceweightstodifferentfrequency nal strength. This summary is then passed through a Feed-
subbands, enabling the model to selectively emphasize in- ForwardNetwork(FFN)tooutputaweightλ foreachband:
i
formativecomponentsacrossthespectrum.Theseweighted
coefficients are further projected into a latent space to cap- λ i =FFN(AvgPool(X w [i])). (2)
tureinter-variabledependenciesatmultiplefrequencyreso-
Thelearnedweightisthenusedtoadjusttheimportance
lutions.Consideringthatlow-frequencycoefficientsprimar-
ofeachbandasfollows:
ilyencodelong-termtrendsandhigh-frequencycomponents
reflect fine-grained fluctuations, the MBS module adopts X ′ [i]=λ ·X [i]. (3)
w i w
a frequency-aware modeling strategy. It learns specialized
representations for each subband to effectively capture the By learning these weights in an end-to-end manner,
diverseandmulti-scaletemporalpatternsinherentinmulti- the model effectively performs adaptive subband selection,
variatetimeseries. wheremorerelevantbandsareemphasizedwhileothersare

mronniveR
… …
𝑋 𝑊 [1] 𝑋 𝑤 ′ [1] 𝑓 1
𝑋 𝑊 [2] 𝑋 𝑤 ′ [2] 𝑓 2
𝑋 𝑊 [2𝑚] 𝑋 𝑤 ′ [2𝑚] 𝑓 2𝑚
Adaptive Frequency-
aware Weighting
…
1-order branch
2-order branch
2𝑚-order branch
Wave
Embedding
…
𝑓መ
1 𝑦ො 1
𝑓መ
2 𝑦ො 2
𝑓መ
2𝑚 𝑦ො 2𝑚
Head
…
mronedniveR
low frequency
high frequency
…
𝑋 [1] 𝑊
𝑋 [2] 𝑊
𝑋 [2𝑚] 𝑊
…
Stack
𝑋 [1]
𝑊
𝑋 [2] 𝑊
𝑋 [2𝑚]
𝑊
Adaptive Frequency-aware weighting
NFF
…
𝜆 1
𝜆 2
𝜆 2𝑚
…
𝑋′ [1] 𝑤
𝑋′ [2] 𝑤
𝑋′ [2𝑚] 𝑤
… … …
𝑓 1
𝑓 2
𝑓 2𝑚
… …
order= b+1
order=b+2
order=b+2𝑚
…
Branch Specialization
AWR MBS
low frequency
𝑓መ 1
𝑓መ 2
𝑓መ 2𝑚
𝐅𝐅𝐍
𝟑 KAN
𝐅𝐅𝐍 𝟏 𝐅𝐅𝐍 𝟐 Wave Embedding high frequency
Figure 2: Framework of WaveTuner, composed of Adaptive Wavelet Refinement (AWR) and Multi-Branch Specialization
(MBS). AWR applies wavelet packet decomposition, adaptive frequency-aware weighting, and wave embedding to highlight
informativesubbands.MBSassignsspecializedbranchestoeachbandforfrequency-specificmodeling.Finally,theheadmod-
ulemapstheresultstothepredictionhorizonbeforereconstructionviainversewaveletpackettransform.
attenuated.Thismechanismimplicitlysearchesforanopti- a Chebyshev polynomial-based KAN with a chosen or-
malsubbandtreestructurewithouttheneedforhand-crafted der.Thepolynomialorderincreasesprogressivelywithfre-
frequencyselectionrules,improvingboththeflexibilityand quency,enablinglow-frequencybranchestocapturesmooth
expressivenessofthemodelinthefrequencydomain. global trends, while high-frequency branches model fine-
grained temporal variations. We adopt KAN as the func-
Wave Embedding. To better model inter-variable rela-
tional learner for each subband due to its strong approx-
tionships, the Wave Embedding module maps wavelet co-
imation and interpretability, achieved via learnable poly-
efficients of the same frequency band across variables into
nomial expansions. Compared with prior time-domain ap-
high-dimensional space, where dependencies among vari-
proaches(Zengetal.2023),ourfrequency-domainspecial-
ablescanbeeffectivelylearned.Specifically,thecombined
izationenhancesbothinterpretabilityandmodelingflexibil-
use of FFNi and FFNi with residual connections projects
1 2 ity.
thecoefficientstoarichfeaturerepresentation:
Specifically, we adopt Chebyshev polynomials T (x) =
n
X ′ [i]=FFNi(X ′ [i]), (4) cos(n·arccos(x))asthefunctionalbasistoconstructexpres-
we 1 w
sive univariate functions. The learnable univariate function
X ′ [i]=Norm(FFNi(X ′ [i])+X ′ [i]). (5) ϕ (x),correspondingtotheo-thoutputneuron,isdefinedas
we 2 we we o
To capture the interactions across different frequency alinearcombinationofChebyshevpolynomials:
bands,FFN isappliedonthetransformedfeatures:
3 D n
(cid:88)(cid:88)
f i =Re(Norm(Re(FFNi 3 (X w ′ e [i])+X w ′ e [i]))), (6) ϕ o (x)= Θ o,j,i T i (Tanh(x j )), (7)
j=1i=0
where FFN denotes different feed-forward networks, and
i
Norm(·)representslayernormalization.TheRe(·)operation
(cid:40)ϕ (x)(cid:41)
permutes the variable dimension to facilitate inter-variable i
KAN(x)= ··· , (8)
modeling. The resulting f denotes the refined representa-
i ϕ (x)
tion of the i-th frequency component, incorporating inter- D
variabledependencies. wherendenotesthehighestorderoftheChebyshevpolyno-
mial,andΘ∈RD×D×(n+1)representsthelearnableparam-
Multi-BranchSpecialization
eters.Tobettermodeltheincreasedcomplexityandvariabil-
Tomodelfrequency-specifictemporaldynamics,wefurther ity of high-frequency components, we assign higher-order
introduce the MBS module that assigns each wavelet sub- Chebyshev expansions to higher-frequency bands. Specifi-
band a dedicated functional learner. Each branch employs cally,fortheinputfeaturef fromthei-thfrequencyband,
i

Models WaveTuner WPMixer TimeKAN TimeMixer FreTS PatchTST TimesNet RLinear
Metrics MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
1mTTE
96 0.321 0.357 0.332 0.362 0.322 0.361 0.320 0.357 0.335 0.372 0.329 0.367 0.338 0.375 0.355 0.376
192 0.362 0.379 0.364 0.379 0.357 0.383 0.367 0.381 0.388 0.401 0.367 0.385 0.374 0.387 0.387 0.392
336 0.393 0.400 0.394 0.401 0.382 0.401 0.390 0.404 0.421 0.426 0.399 0.410 0.410 0.411 0.424 0.415
720 0.456 0.435 0.457 0.435 0.445 0.435 0.498 0.482 0.486 0.465 0.454 0.439 0.478 0.450 0.487 0.450
2mTTE
96 0.173 0.254 0.173 0.253 0.174 0.255 0.175 0.258 0.189 0.277 0.175 0.259 0.187 0.267 0.182 0.265
192 0.237 0.295 0.237 0.295 0.239 0.299 0.237 0.299 0.258 0.326 0.241 0.302 0.249 0.309 0.246 0.304
336 0.297 0.336 0.299 0.336 0.301 0.340 0.298 0.340 0.343 0.390 0.305 0.343 0.321 0.351 0.307 0.342
720 0.394 0.393 0.391 0.392 0.395 0.396 0.391 0.396 0.495 0.480 0.402 0.400 0.408 0.403 0.407 0.398
1hTTE
96 0.368 0.395 0.374 0.387 0.368 0.398 0.375 0.400 0.395 0.425 0.414 0.419 0.384 0.402 0.386 0.395
192 0.416 0.416 0.429 0.416 0.414 0.420 0.429 0.421 0.448 0.440 0.460 0.445 0.436 0.429 0.437 0.424
336 0.431 0.426 0.455 0.430 0.445 0.434 0.484 0.458 0.343 0.390 0.501 0.466 0.491 0.469 0.479 0.446
720 0.464 0.459 0.481 0.473 0.444 0.459 0.498 0.482 0.558 0.532 0.500 0.488 0.521 0.500 0.481 0.470
2hTTE
96 0.277 0.331 0.278 0.332 0.290 0.340 0.289 0.341 0.309 0.364 0.302 0.348 0.340 0.374 0.318 0.363
192 0.350 0.379 0.350 0.379 0.375 0.392 0.372 0.392 0.395 0.425 0.388 0.400 0.402 0.414 0.401 0.412
336 0.363 0.398 0.371 0.402 0.423 0.435 0.386 0.414 0.462 0.467 0.426 0.433 0.452 0.452 0.436 0.442
720 0.412 0.433 0.421 0.439 0.443 0.449 0.412 0.434 0.721 0.604 0.431 0.446 0.462 0.468 0.442 0.454
LCE
96 0.146 0.248 0.150 0.242 0.174 0.266 0.153 0.247 0.309 0.364 0.181 0.270 0.168 0.272 0.201 0.281
192 0.158 0.256 0.163 0.253 0.182 0.273 0.166 0.256 0.175 0.262 0.188 0.274 0.184 0.289 0.201 0.283
336 0.178 0.273 0.179 0.271 0.197 0.286 0.185 0.277 0.185 0.278 0.204 0.293 0.198 0.300 0.215 0.298
720 0.214 0.306 0.222 0.307 0.236 0.320 0.225 0.310 0.220 0.315 0.246 0.324 0.220 0.320 0.257 0.331
cfifarT
96 0.438 0.293 0.466 0.286 0.612 0.391 0.462 0.285 0.593 0.378 0.475 0.290 0.593 0.321 0.649 0.389
192 0.452 0.299 0.492 0.297 0.580 0.368 0.473 0.296 0.595 0.377 0.466 0.296 0.617 0.336 0.601 0.366
336 0.464 0.310 0.493 0.298 0.593 0.368 0.498 0.296 0.609 0.385 0.482 0.304 0.629 0.336 0.609 0.369
720 0.519 0.347 0.527 0.318 0.630 0.388 0.506 0.312 0.673 0.418 0.514 0.322 0.640 0.350 0.647 0.387
rehtaeW
96 0.154 0.199 0.164 0.205 0.162 0.208 0.163 0.209 0.174 0.208 0.177 0.218 0.172 0.220 0.192 0.232
192 0.206 0.248 0.208 0.247 0.207 0.249 0.208 0.250 0.219 0.250 0.225 0.259 0.219 0.261 0.240 0.271
336 0.265 0.289 0.267 0.291 0.263 0.290 0.263 0.293 0.273 0.290 0.278 0.297 0.280 0.306 0.292 0.307
720 0.340 0.340 0.341 0.339 0.338 0.341 0.344 0.348 0.334 0.332 0.354 0.348 0.365 0.359 0.364 0.353
egnahcxE 96 0.081 0.201 0.088 0.206 0.087 0.206 0.085 0.204 0.091 0.217 0.088 0.205 0.107 0.234 0.093 0.217
192 0.176 0.299 0.185 0.304 0.181 0.299 0.180 0.302 0.175 0.310 0.176 0.299 0.226 0.344 0.184 0.307
336 0.335 0.417 0.336 0.418 0.347 0.426 0.361 0.438 0.334 0.434 0.301 0.397 0.367 0.448 0.351 0.432
720 0.861 0.698 0.876 0.705 0.995 0.748 1.011 0.744 0.716 0.674 0.901 0.714 0.964 0.746 0.886 0.714
Table1:Resultsofmultivariatelong-termforecastingwithvariouspredictionlengths(96,192,336,720).Thebestandsecond
performancesareboldedandunderlined,respectively.
weapplyaKANtransformationwithorderb+i,wherebis Then, the reconstruction of the wavelet coefficient se-
thebeginningpolynomialorder.Theoutputisdefinedas: quencebacktothetimedomainisperformedviatheinverse
waveletpackettransform(IWPT)asfollows:
f(cid:98)i =KAN(f
i
,order =b+i)+f
i
, (9)
wheretheresidualconnectionhelpspreserveoriginalinfor-
mationandstabilizetraining. X(cid:98)T =IWPT ψ (x (cid:98)1 ,x (cid:98)2 ,...,x (cid:98)t+T )∈RC×T . (11)
TrainingObjective
FollowingtheMBSmodule,aheadmoduleisemployedto Tooptimizethemodelparametersandensurerobustness
map the feature representations of each frequency compo- tooutliers,weadopttheSmoothL1Lossasthetrainingob-
nent to the target prediction length. Specifically, the head jective,i.e.,
moduletakesthefusedfeaturevectorsasinputandapplies
aFFNtoproducethepredictedwaveletcoefficientswiththe  (cid:12) (cid:12)
predictiondimensionalityd pred : (0.5(X T −Xˆ T )2)/T, if (cid:12) (cid:12) X T −Xˆ T (cid:12) (cid:12) <1
L= (cid:12) (cid:12)
x (cid:98)i =FFN head (f(cid:98)i )∈RC×dpred. (10) ((cid:12) (cid:12) X T −Xˆ T (cid:12) (cid:12) −0.5)/T, otherwise .

Datasets ETTm2 ECL Traffic
Metrics MSE MAE MSE MAE MSE MAE
DWT 0.277 0.320 0.183 0.277 0.477 0.314
w/oAda 0.282 0.323 0.180 0.275 0.506 0.321
w/oWE 0.277 0.320 0.195 0.280 0.514 0.328
MLPs 0.278 0.321 0.182 0.277 0.495 0.321
FLOK 0.279 0.323 0.180 0.274 0.485 0.317
FHOK 0.280 0.324 0.177 0.272 0.487 0.315
WaveTuner 0.275 0.319 0.174 0.271 0.469 0.311
Table 2: Ablation of WaveTuner, averaged over T ∈
{96,192,336,720}.
1.2 1.0 0.8 0.6 0.4 0.2
0.0 0.2
aa ad da dd
thgieW evaW Pred Len 0.80 0.91 9 1 6 92 0.60 0.71 336 0.55 720 0.40 0.41 0.360.32 0.360.36 0.20 0.09 0.15 0.18 0.21 0.00
-0.16-0.11 -0.23-0.17 -0.20
aa ad da dd
(a) Learned frequency weights
ofdifferenthorizons
thgiew evaW
decompositionandfrequency-awarespecializationforlong-
term time series forecasting. In particular, it achieves no-
tableimprovementsoverchannel-independentmodelssuch
as WPMixer, TimeKAN and PatchTST, suggesting that
explicitly modeling inter-variable dependencies in multi-
resolution contributes significantly to performance gains.
WaveTunerconsistentlyoutperformsexistingbaselines,val-
idating the effectiveness of integrating fine-grained fre-
quency decomposition and frequency-aware specialization
forlong-termtimeseriesforecasting.AlthoughbothWave-
Tuner and TimeKAN adopt KAN-based modeling, the su-
perior performance of WaveTuner highlights the benefit of
coupling KAN with wavelet-based subband decomposition
and specialization. Compared to frequency-domain models
like FreTS, WaveTuner’s multi-resolution formulation of-
var1 fers richer frequency representations, enabling better cap- var2 0.410.430.45 var3 tureofcomplexperiodicstructures.Moreover,methodslike RLinearthatrelyonstaticlinearmappingswithoutdecom- 0.090.120.13 0.180.150.13 positionfallshortinmodelinghierarchicaltemporaldepen-
-0.16-0.16 dencies,furtherdemonstratingtheadvantagesoffrequency- -0.24
awarearchitectures.
(b)Learnedweightsofdifferent
ModelAnalysis
variables
Tuning Capability of Adaptive Wavelet Refinement.
Figure3:Visualizationoflearnedweight. We perform ablation studies to validate the components
withintheAdaptiveWaveletRefinementmodule,including
WaveletPacketDecomposition(WPD),adaptiveweighting,
Experiments andtheWaveEmbedding(WE)mechanism.Theresultsare
presentedinTable2.ReplacingWPDwithstandardDiscrete
ExperimentalSetup
Wavelet Transform (DWT) leads to degraded performance,
Datasets & Evaluation Metrics. We evaluated the per-
highlightingthebenefitoffine-grainedfrequencydecompo-
formance of our WaveTuner on 8 commonly used LSTF
sition.Removingtheadaptiveweightingmodule(w/oAda)
benchmarkdatasets:ETT(Zhouetal.2021),Exchange(Lai
also downgrades accuracy, confirming its role in dynami-
et al. 2018), Weather (Wu et al. 2021), Electricity (Wu
cally emphasizing relevant frequency bands. Furthermore,
et al. 2021), and the Traffic (Wu et al. 2021) dataset. Two
substituting the WE module with a simple MLP (w/o WE)
commonly used metrics are used for evaluation, i.e., Mean
results in performance drops, demonstrating the effective-
Squared Error (MSE) and Mean Absolute Error (MAE).
ness of modeling inter-variable dependencies across multi-
More details on datasets and evaluation metrics are pre-
pleresolutions.
sentedinthesupplementary.
Single- vs. Multi-Branch Specialization. Three variants
Baselines. WeselectedeightwidelyacknowledgedSOTA
are designed to demonstrate the effective of this module:
models as benchmarks for comparison. These include
(1) MLPs: replace each KAN with an MLP; (2) FLOK:
wavelet-based model:WPMixer (Murad, Aktukmak, and
useFixedLow-Order(order2)KANsforallsubbands;(3)
Yilmaz2025),frequency-basedmodels:TimeKAN(Huang
FHOK: use Fixed High-Order (order 5) KANs. As shown
et al. 2025), FreTS (Yi et al. 2023b), time-domain models:
inTable2,ourspecializationmoduleachievesthebestper-
TimesNet(Wuetal.2022),TimeMixer(Wangetal.2024b),
formance. It outperforms MLPs by leveraging order adap-
RLinear(Lietal.2023),PatchTST(Nieetal.2022).
tivity,andexceedsbothFLOKandFHOK,demonstrating
thebenefitofassigningappropriatefunctionalcomplexityto
Implemention Details. Following TimeKAN (Huang
differentfrequencybands.
et al. 2025) settings, the lookback window and prediction
lengths are set to L = 96 and T = {96,192,336,720} Frequency Band Weight Distributions. Figure 3 (a) il-
forallexperiments.AllmodelsareimplementedinPyTorch lustrates the learned frequency weights for a single vari-
2.1.2.ExceptthatthetrafficdatasetisevaluatedonanH20- able under prediction lengths of 96, 192, 336, and 720 on
NVLink GPU, others are on a NVIDIA RTX 4090. More ETTm1. With a decomposition depth of 2, the input is di-
detailsareprovidedinthesupplementary. vided into four subbands (aa,ad,da,dd). Despite identical
inputs,themodelassignsdifferentimportancetoeachsub-
MainResults
bandacrossforecastinghorizons,indicatingstep-dependent
Table1presentstheforecastingresultsonalldatasets.Wave- frequency selection. Figure 3 (b) shows the frequency
Tuner consistently outperforms existing baselines, validat- weightsforthreerepresentativevariablesunderaprediction
ing the effectiveness of integrating fine-grained frequency lengthof96.Thedistinctweightingpatternsacrossvariables

1.0
1.2
1.4
1.6
1.8
0 50 100 150 200
eulaV
1.0
1.2
1.4
1.6
History
Ground Truth 1.8
Prediction
0 50 100 150 200
(a)WPMixer
eulaV
1.0
1.2
1.4
1.6
History
Ground Truth 1.8
Prediction
0 50 100 150 200
(b)TimeKAN
eulaV
History
Ground Truth
Prediction
(c)WaveTuner
Figure4:VisualizationofpredictionsontheETTh1datasetwithlookbackandhorizonlengthas96.
0
1
2
3
0 10 20 30
eulaV
0.4
true aa true ad pred aa 0.2 pred ad
0.0
0.2
0.4
0 10 20 30
0.4
0.2
0.0
0.2
0.4
0 10 20 30
eulaV
FreTS Memory 2.7GB, 0.6s
Footprint 1.0GB 1.5GB 2.0GB
RLinear TimeKAN
1.2GB, 1.2s 2.6GB, 2.1s
0.4 PatchTST
true da true dd
pred da 0.2 pred dd WaveTuner 2.0GB, 1.7s
2.0GB, 1.0s
0.0 Wpmixer TimeMixer
2.GB, 1.2s
0.2 1.5GB, 18.6s
0.4
0 10 20 30
Figure6:Effectivenessandefficiencycomparison.
Figure5:Decompositionvisualizationoftheprediction.
AdaptiveWaveletRefinementandMulti-BranchSpecializa-
indicate variable-specific frequency preferences. These re-
tion.Specifically,WaveletPacketTransformincursacostof
sultsdemonstratethatWaveTuner’sadaptivewaveletrefine-
O(C·L·m),AdaptiveWeightingO(C·2m),WaveEmbed-
ment effectively captures task-relevant frequency features,
ding O(L·C ·d), where C, L, m, and d denote the num-
improvingmodelflexibilityandforecastingaccuracy.
berofvariables,sequencelength,decompositionlevels,and
VisualizationofPrediction. Figure4presentspredictions embedding dimension, respectively. Multi-Branch Special-
for a sample from the ETTh1 dataset. WaveTuner is com- izationintroducesacostofO(L·d2·K),withK arecon-
paredwithtworepresentativebaselines:WPMixer(wavelet- stants in practice, the total complexity scales linearly with
based) and TimeKAN (frequency-based). As shown in the respect to both the number of variables and the sequence
figure, WaveTuner generates more accurate and smoother length: O(C · L). Figure 6 shows the empirical compari-
forecasts. Specifically, it better preserves informative fre- sononETTh2withahistorywindowof96andaprediction
quency components while mitigating overfitting to noise, length of 336. WaveTuner not only delivers the best fore-
outperforming both baselines. To further interpret the pre- casting accuracy but also surpasses WPMixer in terms of
diction behavior, we visualize in Figure 5 the wavelet co- computationalefficiency.
efficientscorrespondingtoWaveTuner’soutputinFigure4.
Thefourplotspresentthepredictedversusgroundtruthco- Conclusion
efficientsacrossfoursubbands(aa,ad,da,dd)fromalevel-
2 wavelet decomposition. We observe that low-frequency In this paper, we propose WaveTuner, a novel frequency-
bands(e.g.,aa)capturemajortrendsandareaccuratelyes- aware forecasting framework that integrates adaptive
timated,whilehigh-frequencybands(e.g.,dd)exhibitflatter waveletrefinementwithmulti-branchspecializationtocap-
structures,andthemodelavoidsfittingspuriousfluctuations. ture temporal dynamics across multiple frequency bands.
Despite using high-order KANs for high-frequency model- The refinement module conducts fine-grained wavelet
ing, the network adaptively suppresses unnecessary com- packet decomposition and adaptively weights subbands
plexity when signal variance is low. This selective expres- basedontask-andvariable-specificproperties.Thespecial-
siveness demonstrates WaveTuner’s frequency-aware de- ization module assigns tailored learners to each subband,
sign—preserving detail where informative, and promoting enablingfrequency-awareanddisentangledrepresentations.
generalization where appropriate—aligning well with our Thisdesignallowsthemodeltoflexiblycapturebothglobal
coremotivation. trendsandlocalvariationsacrossdiversetemporalpatterns.
Extensive experiments show that WaveTuner outperforms
EfficiencyAnalysis. Theoverallcomputationalcomplex- strong baselines, validating the effectiveness of combining
ityofWaveTunerisdeterminedbyitstwocorecomponents: adaptivefrequencymodelingwithspecialization.

References Liu, Z.; Wang, Y.; Vaidya, S.; Ruehle, F.; Halver-
son, J.; Soljacˇic´, M.; Hou, T. Y.; and Tegmark, M.
Amalou, I.; Mouhni, N.; and Abdali, A. 2022. Multivari-
2024b. Kan:Kolmogorov-arnoldnetworks. arXivpreprint
ate time series prediction by RNN architectures for energy
arXiv:2404.19756.
consumptionforecasting. EnergyReports,8:1084–1091.
Mehtab,S.;andSen,J.2022. Analysisandforecastingoffi-
Cirstea,R.-G.;Yang,B.;Guo,C.;Kieu,T.;andPan,S.2022.
nancialtimeseriesusingCNNandLSTM-baseddeeplearn-
Towards spatio-temporal aware traffic time series forecast-
ingmodels. InAdvancesinDistributedComputingandMa-
ing. In 2022 IEEE 38th International Conference on Data
chineLearning:ProceedingsofICADCML2021,405–423.
Engineering(ICDE),2900–2913.IEEE.
Springer.
Frusque,G.;andFink,O.2024. Robusttimeseriesdenois-
Murad,M.M.N.;Aktukmak,M.;andYilmaz,Y.2025.WP-
ingwithlearnablewaveletpackettransform. AdvancedEn-
Mixer:Efficientmulti-resolutionmixingforlong-termtime
gineeringInformatics,62:102669.
series forecasting. In Proceedings of the AAAI Conference
Guo, T.; Zhang, T.; Lim, E.; Lopez-Benitez, M.; Ma, F.;
onArtificialIntelligence,volume39,19581–19588.
and Yu, L. 2022. A review of wavelet analysis and its ap-
Nie, Y.; Nguyen, N. H.; Sinthong, P.; and Kalagnanam, J.
plications: Challenges and opportunities. IEEe Access, 10:
2022. Atimeseriesisworth64words:Long-termforecast-
58869–58903.
ingwithtransformers. arXivpreprintarXiv:2211.14730.
Haq, M. A. 2022. CDLSTM: A novel model for climate
Piao,X.;Chen,Z.;Murayama,T.;Matsubara,Y.;andSaku-
change forecasting. Computers, Materials & Continua,
rai,Y.2024a.Fredformer:FrequencyDebiasedTransformer
71(2).
forTimeSeriesForecasting. InKDD,2400–2410.ACM.
Huang, S.; Zhao, Z.; Li, C.; and Bai, L. 2025. TimeKAN:
Piao,X.;Chen,Z.;Murayama,T.;Matsubara,Y.;andSaku-
KAN-based Frequency Decomposition Learning Architec-
rai,Y.2024b. Fredformer:Frequencydebiasedtransformer
tureforLong-termTimeSeriesForecasting. arXivpreprint
fortimeseriesforecasting. InProceedingsofthe30thACM
arXiv:2502.06910.
SIGKDD Conference on Knowledge Discovery and Data
Kim,T.;Kim,J.;Tae,Y.;Park,C.;Choi,J.-H.;andChoo,J. Mining,2400–2410.
2021. Reversibleinstancenormalizationforaccuratetime-
Salinas,D.;Flunkert,V.;Gasthaus,J.;andJanuschowski,T.
seriesforecastingagainstdistributionshift. InInternational
2020. DeepAR: Probabilistic forecasting with autoregres-
conferenceonlearningrepresentations.
sive recurrent networks. International journal of forecast-
Lai,G.;Chang,W.-C.;Yang,Y.;andLiu,H.2018.Modeling ing,36(3):1181–1191.
long-andshort-termtemporalpatternswithdeepneuralnet-
Seyedan, M.; Mafakheri, F.; and Wang, C. 2023. Order-
works. InThe41stinternationalACMSIGIRconferenceon
up-to-level inventory optimization model using time-series
research&developmentininformationretrieval,95–104.
demand forecasting with ensemble deep learning. Supply
Li, C.; Li, M.; and Diao, R. 2025. TVNet: A Novel Time ChainAnalytics,3:100024.
SeriesAnalysisMethodBasedonDynamicConvolutionand
Stefenon, S. F.; Seman, L. O.; Aquino, L. S.; and dos San-
3D-Variation. arXivpreprintarXiv:2503.07674.
tosCoelho,L.2023.Wavelet-Seq2Seq-LSTMwithattention
Li,Z.;Qi,S.;Li,Y.;andXu,Z.2023. Revisitinglong-term fortimeseriesforecastingoflevelofdamsinhydroelectric
timeseriesforecasting:Aninvestigationonlinearmapping. powerplants. Energy,274:127350.
arXivpreprintarXiv:2305.10721.
Stefenon,S.F.;Seman,L.O.;daSilva,E.C.;Finardi,E.C.;
Liang, A.; Sun, Y.; and Guizani, N. 2024. WaveRoRA: dosSantosCoelho,L.;andMariani,V.C.2024.Hypertuned
Wavelet Rotary Route Attention for Multivariate Time Se- wavelet convolutional neural network with long short-term
riesForecasting. arXivpreprintarXiv:2410.22649. memory for time series forecasting in hydroelectric power
Lim,B.;andZohren,S.2021. Time-seriesforecastingwith plants. Energy,313:133918.
deep learning: a survey. Philosophical Transactions of the Tang, P.; and Zhang, W. 2025. Unlocking the Power of
RoyalSocietyA,379(2194):20200209. Patch:Patch-BasedMLPforLong-TermTimeSeriesFore-
Liu, M.; Zeng, A.; Chen, M.; Xu, Z.; Lai, Q.; Ma, L.; and casting.InProceedingsoftheAAAIConferenceonArtificial
Xu,Q.2022. Scinet:Timeseriesmodelingandforecasting Intelligence,volume39,12640–12648.
withsampleconvolutionandinteraction. AdvancesinNeu- Wang,S.;Wu,H.;Shi,X.;Hu,T.;Luo,H.;Ma,L.;Zhang,
ralInformationProcessingSystems,35:5816–5828. J.Y.;andZhou,J.2024a. TimeMixer:DecomposableMul-
Liu,P.;Wu,B.;Li,N.;Dai,T.;Lei,F.;Bao,J.;Jiang,Y.;and tiscaleMixingforTimeSeriesForecasting. InICLR.Open-
Xia,S.-T.2024a.Wftnet:Exploitingglobalandlocalperiod- Review.net.
icityinlong-termtimeseriesforecasting. InICASSP2024- Wang,S.;Wu,H.;Shi,X.;Hu,T.;Luo,H.;Ma,L.;Zhang,
2024 IEEE International Conference on Acoustics, Speech J.Y.;andZhou,J.2024b. Timemixer:Decomposablemul-
andSignalProcessing(ICASSP),5960–5964.IEEE. tiscale mixing for time series forecasting. arXiv preprint
Liu, Y.; Hu, T.; Zhang, H.; Wu, H.; Wang, S.; Ma, L.; arXiv:2405.14616.
and Long, M. 2023. itransformer: Inverted transformers Woo, G.; Liu, C.; Kumar, A.; Xiong, C.; Savarese, S.; and
are effective for time series forecasting. arXiv preprint Sahoo, D. 2024. Unified training of universal time series
arXiv:2310.06625. forecastingtransformers.

Wu, H.; Hu, T.; Liu, Y.; Zhou, H.; Wang, J.; and Long, M. the AAAI conference on artificial intelligence, volume 35,
2022. Timesnet: Temporal 2d-variation modeling for gen- 11106–11115.
eraltimeseriesanalysis. arXivpreprintarXiv:2210.02186. Zhou, T.; Ma, Z.; Wen, Q.; Wang, X.; Sun, L.; and Jin,
Wu,H.;Xu,J.;Wang,J.;andLong,M.2021. Autoformer: R. 2022. FEDformer: Frequency Enhanced Decomposed
Decompositiontransformerswithauto-correlationforlong- Transformer for Long-term Series Forecasting. In ICML,
termseriesforecasting.Advancesinneuralinformationpro- volume162ofProceedingsofMachineLearningResearch,
cessingsystems,34:22419–22430. 27268–27286.PMLR.
Wu,X.;Qiu,X.;Li,Z.;Wang,Y.;Hu,J.;Guo,C.;Xiong,H.;
and Yang, B. 2025. CATCH: Channel-Aware Multivariate
TimeSeriesAnomalyDetectionviaFrequencyPatching. In
ICLR.OpenReview.net.
Yi,K.;Fei,J.;Zhang,Q.;He,H.;Hao,S.;Lian,D.;andFan,
W.2024. Filternet:Harnessingfrequencyfiltersfortimese-
riesforecasting.AdvancesinNeuralInformationProcessing
Systems,37:55115–55140.
Yi,K.;Zhang,Q.;Fan,W.;Wang,S.;Wang,P.;He,H.;An,
N.;Lian,D.;Cao,L.;andNiu,Z.2023a.Frequency-domain
MLPsareMoreEffectiveLearnersinTimeSeriesForecast-
ing. InNeurIPS.
Yi,K.;Zhang,Q.;Fan,W.;Wang,S.;Wang,P.;He,H.;An,
N.;Lian,D.;Cao,L.;andNiu,Z.2023b.Frequency-domain
MLPs are more effective learners in time series forecast-
ing. Advances in Neural Information Processing Systems,
36:76656–76679.
Yu, G.; Li, Y.; Wang, J.; Guo, X.; Aviles-Rivero, A. I.;
Yang, T.; and Wang, S. 2025. ReFocus: Reinforcing Mid-
Frequency and Key-Frequency Modeling for Multivariate
TimeSeriesForecasting. arXivpreprintarXiv:2502.16890.
Yu, H.; Guo, P.; and Sano, A. 2024. AdaWaveNet: Adap-
tivewaveletnetworkfortimeseriesanalysis. arXivpreprint
arXiv:2405.11124.
Zeng,A.;Chen,M.;Zhang,L.;andXu,Q.2023. Aretrans-
formerseffectivefortimeseriesforecasting?InProceedings
oftheAAAIconferenceonartificialintelligence,volume37,
11121–11128.
Zhang,Y.;andYan,J.2023. Crossformer:Transformeruti-
lizingcross-dimensiondependencyformultivariatetimese-
riesforecasting.InTheeleventhinternationalconferenceon
learningrepresentations.
Zhang, Z.; Guo, D.; Zhou, S.; Zhang, J.; and Lin, Y.
2023.Flighttrajectorypredictionenabledbytime-frequency
wavelettransform. NatureCommunications,14(1):5258.
Zhang,Z.;Pham,T.D.;An,Y.;Doan,N.P.;Alsharari,M.;
Tran, V.; Hoang, A.; Vandierendonck, H.; and Mai, S. T.
2025a. WaveletMixer:AMulti-ResolutionWaveletsBased
MLP-Mixer for Multivariate Long-Term Time Series Fore-
casting. InAAAI,22741–22749.AAAIPress.
Zhang,Z.;Pham,T.D.;An,Y.;Doan,N.P.;Alsharari,M.;
Tran, V.-H.; Hoang, A.-T.; Vandierendonck, H.; and Mai,
S. T. 2025b. WaveletMixer: a multi-resolution wavelets
based MLP-mixer for multivariate long-term time series
forecasting. InProceedingsoftheAAAIConferenceonAr-
tificialIntelligence,volume39,22741–22749.
Zhou, H.; Zhang, S.; Peng, J.; Zhang, S.; Li, J.; Xiong, H.;
andZhang,W.2021.Informer:Beyondefficienttransformer
forlongsequencetime-seriesforecasting. InProceedingsof

