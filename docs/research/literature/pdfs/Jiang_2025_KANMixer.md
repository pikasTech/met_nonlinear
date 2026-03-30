KANMixer: Can KAN Serve as a New Modeling Core for Long-term Time Series
Forecasting?
LingyuJiang1,YupingWang2,YaoSu5,ShuoXing3,WenjingChen3,XinZhang4,
ZhengzhongTu3,ZimingZhang5,FangzhouLin1,3,5*†,MichaelZielewski1†,KazunoriDYamada1†
1TohokuUniversity2UniversityofMichigan3TexasA&MUniversity
4SanDiegoStateUniversity5WorcesterPolytechnicInstitute
jiang.lingyu.p7@dc.tohoku.ac.jp,flin2@wpi.edu,mike.zielewski@tohoku.ac.jp,yamada@tohoku.ac.jp
Abstract
Different models for LTSF task.
In recent years, multilayer perceptrons (MLP)-based deep e Input Input Input
learning models have demonstrated remarkable success in
lu
d o
long-term time series forecasting (LTSF). Existing ap- M
proaches typically augment MLP backbones with hand-
ticilp
crafted external modules to address the inherent limitations x
E
of their flat architectures. Despite their success, these aug- e mentedmethodsneglecthierarchicallocalityandsequential n o b k Patch Mixer M Tr ix e i n n d g S M ea ix s i o n n g al Temporal
inductivebiasesessentialfortime-seriesmodeling,andrecent ca Mixing(KAN) B
s
o
t
v
u
e
d
r
i
c
e
o
s
m
in
e
d
t
i
h
c
e
a
s
t
e
e
l
d
i
i
m
m
i
i
t
n
at
i
i
s
o
h
n
in
s,
g
w
p
e
er
e
f
x
o
p
rm
lo
a
r
n
e
c
K
e
o
i
l
m
m
p
o
r
g
o
o
v
r
e
o
m
v
e
-A
nt
r
s
n
.
o
T
l
o
d
ticilp
Embedding Mixer Feed Forwad
m
Networks(KAN),arecentlyproposedmodelfeaturingadap- I
d
tivebasisfunctionscapableofgranular,localmodulationof a Predict Head Multi-predictor Predict
e
n
se
o
r
n
v
l
e
in
a
ea
s
ri
a
tie
n
s
e
.
w
Th
m
is
o
r
d
a
e
i
l
s
i
e
n
s
g
a
c
f
o
u
r
n
e
da
fo
m
r
en
L
t
T
a
S
l
F
q
?
ue
T
st
o
io
a
n
n
:
s
C
w
a
e
n
r
K
th
A
i
N
s,
cid
H
t Mu
R
l
e
ti
c
-
o
le
n
v
s
e
t
l
r u
W
c
a
ti
v
o
e
n
let
Mixing Head(KAN)
we introduce KANMixer, a concise architecture integrating e rP Output Output KA O N u M tpu ix t er
a multi-scale mixing backbone that fully leverages KAN’s WPMixer TimeMixer
(ours)
adaptivecapabilities.Extensiveevaluationdemonstratesthat
KANMixerachievesstate-of-the-artperformancein16outof
Figure 1: Architectural diagrams of various LTSF models.
28experimentsacrosssevenbenchmarkdatasets.Touncover
Explicit modules embed domain priors (e.g., decomposi-
the reasons behind this strong performance, we systemati-
tion, multi-scale), implicit backbones capture temporal de-
callyanalyzethestrengthsandlimitationsofKANMixerin
pendencies, and prediction heads generate multi-step fore-
comparisonwithtraditionalMLParchitectures.Ourfindings
reveal that the adaptive flexibility of KAN’s learnable basis casts.
functions significantly transforms the influence of network
structuralprioronforecastingperformance.Furthermore,we
identifycriticaldesignfactorsaffectingforecastingaccuracy
tions include, but are not limited to, energy systems (Ra-
and offer practical insights for effectively utilizing KAN in
jagukguk, Ramadhan, and Lee 2020), electricity manage-
LTSF. Together, these insights provide the first empirically
ment(Trindade2015),weatherprediction(Wuetal.2023b),
groundedguidelinesforeffectivelyleveragingKANinLTSF.
and traffic planning (Cao et al. 2025; Zhuang et al. 2022).
Codeisavailableinthesupplementaryfile.
Deep learning methods (Lai et al. 2018; Salinas, Flunkert,
andGasthaus2019)nowdominatetheLTSFlandscape,hav-
Introduction ing largely surpassed traditional statistical methods (e.g.,
ARIMA(HoandXie1998))andclassicalmachinelearning
Long-term time series forecasting (Chen et al. 2023b)
algorithms(e.g.,GBDT(ChenandGuestrin2016;Keetal.
(LTSF)isafundamentaltaskwithprofoundreal-worldim-
2017)).Themodelarchitecturesrapidlyevolvedfromearly
pact, underpinning strategic planning and operational de-
recurrent neural networks (RNNs) (D YAMADA, Lin, and
cisions across a multitude of critical sectors. The primary
Nakamura2021;Lyuetal.2021),suchasLongShort-Term
task of LTSF is to predict future values of a multivariate
Memory networks (LSTMs (Hochreiter and Schmidhuber
timeseriesoveranextendedhorizon,whosecorechallenge
1997)),tographneuralnetworks(GNNs)thatleveragerela-
iscapturinglong-rangetemporaldependencies.Itsapplica-
tionalandstructuralinformation((Gaoetal.2024;Wuetal.
*Projectlead. 2021b;Jiangetal.2025)),andsubsequentlytoTransformer-
†FangzhouLin,MichaelZielewskiandKazunoriDYamadaare based(Vaswanietal.2023)architecturesexemplifiedbyIn-
thecorrespondingauthors. former (Zhou et al. 2021), Autoformer (Wu et al. 2021a),
5202
guA
3
]GL.sc[
1v57510.8052:viXra

FEDformer (Zhou et al. 2022) and PatchTST (Nie et al. by spline-based basis functions, the effectiveness of mod-
2023).Poweredbysophisticatedself-attentionmechanisms erate network depths in balancing representation and op-
(Yamada,Baladram,andLin2022),Transformermodelsex- timization, and the nuanced interactions between KAN’s
celatcapturingcross-variaterelationships,settingnewper- adaptability and imposed structural priors. These analyses
formancestandardsinLTSF. yieldpracticalguidelinesforeffectivelyleveragingKANin
However,thisdominancewasupendedbyDLinear(Zeng future model design. The main contributions of this paper
et al. 2023), which demonstrated that a surprisingly simple areasfollows:
linear model could decisively outperform complex Trans-
• WeproposeKANMixer,astructurallysimplemodelfea-
formers.Inspiredbythisfinding,researchersstartedimprov-
turing KAN as its modeling core. KANMixer surpasses
ing MLP backbones by adding extra hand-designed parts.
more complex SOTA models in performance, demon-
Thesepartsbringinstructuralknowledgetomakeupforthe
stratingitseffectiveness.
factthatMLPshaveaflatdesignanddon’tnaturallyunder-
• We provide a systematic analysis of KAN’s modeling
stand the order or patterns in data. Examples of such mod-
characteristics in LTSF, revealing that KAN’s superior
ules include frequency decomposition blocks (Wang et al.
performanceoriginatesfromtheadaptiveplasticityofits
2025a) and patch mixing layers (Gong, Tang, and Liang
basis functions. Our analysis also shows that structural
2024).ThisledtomodelslikeWPMixer(Murad,Aktukmak,
priorsinteractdifferentlywithKANcomparedtoMLP.
andYilmaz2024),TimeMixer(Wangetal.2024),FreTS(Yi
etal.2023),andTiDE(Dasetal.2023).Althoughthisstrat- • Toourknowledge,wedeliverthefirstsetofempirically
egy initially yielded significant improvements, recent fair- grounded, practical guidelines for effectively applying
benchmark studies reveal that their additional complexity KANtoLTSF,emphasizingthecriticalimportanceofthe
offersonlydiminishinggainsinperformance(Brigatoetal. predictionheadandoptimalnetworkdepthinmaximiz-
2025). ingforecastingperformance.
Theseobservationspointtotheinherentlimitationsinthe
MLP backbone itself, suggesting the necessity to explore RelatedWork
more efficient core modeling architectures. In this context,
Kolmogorov–ArnoldNetwork
Kolmogorov-ArnoldNetworks(KAN)(Liuetal.2025)pro-
vide a compelling alternative by adaptively learning rep- Inspired by the Kolmogorov–Arnold representation theo-
resentations through spline-based basis functions directly rem (Schmidt-Hieber 2021), Liu et al. (Liu et al. 2025)
from data, achieving compact yet powerful universal ap- introduced the Kolmogorov–Arnold Network (KAN), sig-
proximation and enabling fine-grained local modulation of nificantly innovating over traditional MLPs. KAN models
nonlinearities(Schmidt-Hieber2021).Theseuniqueproper- each connection with trainable B-spline curves, enhancing
tiesmotivateourcentralresearchquestion:CanKANserve functional plasticity and accuracy in scientific computing
asanewmodelingcoreforLTSF? tasks with fewer parameters (Wang et al. 2025b). How-
Recent pioneering studies have begun to integrate KAN ever,despitetheseadvantages,KAN’strainingtypicallyin-
into LTSF, demonstrating its potential (Vaca-Rubio et al. curshighercomputationalcostsduetothecomplexityofB-
2024). For example, TimeKAN (Huang et al. 2025) in- splinebasisfunctions(Ji,Hou,andZhang2025).Recentim-
corporates a multi-order KAN and achieves state-of-the-art provementsthusfocusonalternativebasisfunctionstomiti-
(SOTA)performance,whileReversibleMixtureofKANEx- gatetheselimitationsandenhancespecificaspectsofKAN:
perts (RMoK) (Han et al. 2025) successfully validates its ChebyshevKAN(SSetal.2024)employsChebyshevpoly-
utilityasabuildingblock.However,existingstudiesprimar- nomials for efficiency; Kolmogorov–Arnold–Fourier Net-
ily utilize KAN as an auxiliary module, without exploring work (KAF) (Zhang et al. 2025) leverages random Fourier
itspotentialasamodelcore. features for efficient high-frequency pattern representation;
Tothisend,weintroduceKANMixer,aconcisearchitec- Wav-KAN (Bozorgasl and Chen 2024) uses wavelets for
ture designed around KAN as the modeling core. By em- fastertrainingandrobustness.
ployingaminimalisticmulti-scalemixingbackbone,ourde-
ExplicitParadigmsinLTSF
sign maximally leverages KAN’s adaptive basis functions
while avoiding unnecessary complexity, ensuring that ob- MLP-based models often struggle to capture intricate tem-
served performance gains can be attributed directly to the poral patterns spanning multiple trends, periodicities, and
KANcore.AsshowninFigure1,KANMixer’sconcisear- high-frequencyfluctuations.Thislimitationarisesfromtheir
chitecture is noticeably more streamlined than more com- fixed,non-adaptivereceptivefieldsandlackofinductivebi-
plexmodelslikeWPMixerandTimeMixer.Moreover,based asestailoredforsequentialdata.Explicitparadigmsmitigate
on numerical experimental results, KANMixer achieves these limitations by embedding domain-specific priors into
state-of-the-art(SOTA)performancein16outof28experi- datarepresentations(Liuetal.2024a;Dengetal.2024),no-
mentsacross7benchmarkdatasets.Ourinvestigationcom- tablythroughdecompositionandmulti-scalemodeling.
pellinglyvalidatesKAN’spotentialasapowerfulmodeling Decomposition (Liu et al. 2024a; Deng et al. 2024) sep-
coreforLTSF. arates sequences into simpler subcomponents by either de-
Beyond achieving superior performance, our systematic composingthemintotrends,seasonality,andresidualsinthe
analysiselucidateshowandwhyKANimprovesforecasting time domain or into high, mid, and low-frequency compo-
accuracy.Specifically,wehighlightthecriticalrolesplayed nentsinthefrequencydomain.Forinstance,DLinear(Zeng

etal.2023)employsmovingaveragestoextracttrends,mod-
Input
eling residuals linearly; FreTS (Yi et al. 2023) operates di-
rectlyinthefrequencydomain;TimesNet(Wuetal.2023a)
Multiscale
identifiesdominantfrequenciesviaFFTtoexplicitlymodel
intra-andinter-periodvariations.
Norm Average Average
Multi-scalemodelingcapturestemporaldynamicsatmul-
Pooling Pooling
tiple resolutions (Shabani et al. 2022; Zhong et al. 2023),
Temporal
significantly enhancing forecasting capabilities. SCINet
Mixing
(LIU et al. 2022) partitions sequences recursively into hi-
erarchicalstructures,capturingdependenciesacrossscales. KAN Layer
N
KAN Layer
ImplicitParadigmsinLTSF Predict Head
Transformer architectures (Vaswani et al. 2023), particu-
KKKAAANNN LLLaaayyyeeerrr
Denorm
larly through multi-head self-attention, dominate implicit
modeling by capturing long-range sequence dependencies. Output
Informer (Zhou et al. 2021) introduced ProbSparse self-
attention for efficiency; Autoformer (Wu et al. 2021a) em-
Figure2:ThearchitectureofKANMixerconsistsofamulti-
ployed auto-correlation mechanisms, explicitly decompos-
scale processing module, a temporal mixing module, and a
ingsequencesintotrendsandseasonalities.Nonetheless,the
KAN-basedpredictionhead.
quadraticcomplexityofvanillaTransformersremainscom-
putationallyintensive.
To reduce computational complexity, recent methods
OverallArchitecture
adopt lightweight mixing-based architectures, replacing at-
tentionwithlinear-complexityMLPblocks.TSMixer(Chen We design our KANMixer to be concise, standalone, and
et al. 2023a) alternately applies MLPs across temporal and freefromexternalmodules,inthehopethatitcanbeplug-
cross-variate dimensions, while TimeMixer (Wang et al. and-played into any LTSF models. Following the recent
2024)integratesdual-scalemixing. successes in LTSF (Nie et al. 2023), we adopt a channel-
Moreover, graph neural networks (GNNs) and diffusion independent approach to forecast each variable separately.
models (Meijer and Chen 2024; Zhuang et al. 2024; Gao The overall structure of KANMixer is illustrated in Fig-
et al. 2023) have gained prominence. MTGNN (Wu et al. ure 2. It is comprised of three modules: (1) an explicit
2020)explicitlyleveragesgraphstructuresforspatiotempo- multi-scalemodulethatdown-samplesinputsequencesinto
raldependencies,andSTGAIL(Liuetal.2024d)integrates scale-enrichedrepresentations;(2)animplicittemporalmix-
diffusion processes with spatial-temporal graph layers, ef- ing module employing a minimalistic fine-to-coarse fu-
fectivelymodelingcomplexdynamics. sion strategy to hierarchically integrate features; and (3) a
KAN-based prediction head producing the final forecasts.
All modules in our KANMixer employ adaptive KAN lay-
KANMixer
ers. We perform ablation studies of each of these compo-
ProblemDefinitionforLTSF nentstounderstandtheircontributionindifferentmodeling
paradigms.Below,wedescribethedetailsofeachmodel.
In this section, we provide the setup and definition of the
LTSFproblem(Chenetal.2023b).Givenahistoricalmulti-
ExplicitMulti-ScaleProcessing
variatetimeseriesoflengthLobservedattimestept:
Time series data typically exhibit distinct characteristics
X ={X1,X2,...,Xd}L , Xi ∈R, (1) across multiple temporal scales, ranging from macroscopic
t t t t=1 t trends to fine-grained fluctuations. To efficiently capture
where d denotes the number of observed variables, and thesediversetemporaldynamicswithoutalteringtheintrin-
L is the length of the look-back window, the goal of time sic data structure, we adopt average pooling with a fixed
seriesforecastingistopredictthefuturevaluesforthenext kernelsizek togeneratemulti-scalerepresentations.These
P steps: pooledrepresentationsareconcatenatedwiththeoriginalse-
quencealongthefeaturedimensionandprojectedintoauni-
fied latent representation Xms ∈ Rdmodel×L. This enriched
Xˆ =f(X)={Xˆ t 1,Xˆ t 2,...,Xˆ t d}L t= + L P +1 , Xˆ t i ∈R. (2) representationnaturallyfacilitatessubsequentimplicitmix-
ingmodulestoaggregatetemporalinformationfromlocalto
InLTSFtasks,commonpracticeintheliteratureistouse
globalcontexts.
the Mean Squared Error (MSE) as the primary evaluation
metricandlossfunction(Huangetal.2025),definedas:
ImplicitTemporalMixingModule
L+P d Giventheenrichedmulti-scalerepresentation,weemploya
MSE= 1 (cid:88) (cid:88) (Xi−Xˆi)2. (3) minimalisticTemporalMixingmoduletohierarchicallyin-
P ×d t t tegrate temporal dependencies, effectively balancing local
t=L+1i=1

andglobalcontexts. seed,andbatchsizeandorder.Morespecifically,wetrained
Specifically,theTemporalMixingbackbonecomprisesN all models utilizing the L loss function (MSE), the Adam
2
stacked mixing blocks operating on multi-scale representa- optimizerwithafixedlearningrateoflr = 0.01,batchsize
tions {Z0 ,...,Zk }, where i = 0 denotes the highest b = 32, and the same random seed as in prior work. To
l−1 l−1
(finest)resolution,andi=kthelowest(coarsest). ensure fair comparisons, results for KANMixer and repro-
Within each block, information propagates from finer to ducedbaselines(TimeKAN,TimeMixer)areaveragedover
coarserscalesthroughastreamlinedfusionmechanismwith fiveruns,whileremainingresultsarereporteddirectlyfrom
residual connections. Concretely, representations at scale i theirrespectivepapers.Themodelwidthwastreatedasahy-
are updated by integrating downsampled and transformed perparameter,asMLP-basedmodelstypicallyrequirewider
featuresfromtheadjacentfinerscalei−1viaadaptiveKAN widths than their KAN-based counterparts to achieve opti-
layers: mal performance. We conduct all experiments on a server
Hi =Zi +KAN (Zi−1). (4) with4NVIDIAAmpereA10080GGPUs.
l l−1 down l−1
Subsequently, each representation Hi undergoes channel-
l
wise refinement via a KAN-based feed-forward network Mainresults
(KAN ), with residual connections ensuring stable train-
ffn
ing: As shown in Table 1, KANMixer delivers SOTA accuracy
Zi =Hi+KAN (Hi). (5) acrosssevenlong-termtime-seriesbenchmarks.Leveraging
l l ffn l
its concise yet effective architecture, it secures first-place
Stacking multiple such blocks results in a deep, adap-
performance in 16 MSE and 11 MAE configurations, con-
tivemulti-scalerepresentation,effectivelyexploitingKAN’s
sistentlyoutperformingmorecomplexmodels.Thisadvan-
nonlinearmodelingcapabilities.
tage is particularly notable on the ETTh1 dataset, where
Finally,scale-specificKANpredictionheadsmapthela-
KANMixerachievesanaverageMSEimprovementof4.9%
tent features Zi N to scale-specific forecasts Y(cid:98)i. The final acrossallforecastlengths.
forecast is obtained by summing predictions across scales,
While KANMixer performs strongly across most bench-
leveraginginsightsfromalltemporalresolutions:
marks, specialized architectures excel in certain scenarios.
k For example, Transformer-based models like iTransformer
(cid:88)
Y(cid:98) = Y(cid:98) i. (6) outperformontheElectricitydataset(321variables)dueto
their explicit modeling of cross-variate correlations. Sim-
i=0
ilarly, Time-FFM excels on the highly volatile Exchange
Experiments dataset,benefitingfromitsfoundation-modeldesigntailored
ExperimentalSettings tocapturegeneralmacroeconomicpatterns.
While performance on these specialized datasets high-
Datasets Our experiments utilize seven commonly used
lights the strengths of targeted architectures, KANMixer
real-world datasets: the ETT series (Zhou et al. 2021) (in-
demonstratesstrongresultsacrossabroaderrangeofbench-
cluding ETTh1, ETTh2, ETTm1, and ETTm2), Exchange
marks. Its effectiveness stems from a minimalistic multi-
Rate,Weather,andElectricity.Consistentwithpreviousre-
scale feature augmentation strategy, explicitly leveraging
search(Zhouetal.2021),theETTdatasetsaredividedinto
adaptive KAN layers without unnecessary complexity or
training, validation, and testing sets with a ratio of [6:2:2],
commondecomposition-basedpriors.Particularlyinsightful
while the Weather, Exchange Rate, and Electricity datasets
isthecomparisonwithTimeKAN,anotherpioneeringKAN-
followapartitionratioof[7:1:2].
based model. While TimeKAN validates the potential of
Baseline We select widely adopted, well-acknowledged
KANinLTSFbyintegratingitintoacomplexcascadedfre-
methods from the LTSF literature, covering various model
quencydecompositionarchitecture,oursimpler,moredirect
categories, including the KAN-based TimeKAN (Wu et al.
KANMixer consistently outperforms it. Our design choice
2023a),Transformer-basedmodels(e.g.,iTransformer(Liu
is supported by our critical analysis, revealing how to un-
etal.2024c),PatchTST(Nieetal.2023)),MLP-basedmod-
leashKAN’sfullpotential.Overall,theseresultsclearlyaf-
els(e.g.,TimeMixer(Wangetal.2024),DLinear(Zengetal.
firm our initial hypothesis: KAN can serve as a powerful
2023),FreTS(Yietal.2023),TiDE(Dasetal.2023)),CNN-
general-purposemodelingcore.
basedTimesNet(Wuetal.2023a),andTime-FFM(Liuetal.
2024b),afoundationmodelfortimeseriesforecasting.For
the recent TimeKAN and TimeMixer models, we have re- FurtherAnalysisonKAN-basedModel
producedtheirexperimentstoensurefaircomparisons.
EvaluationBuildinguponpastresearch(Wuetal.2021a), In this section, we conduct a series of controlled ablation
weutilizetheMeanSquaredError(MSE)andMeanAbso- studies on KANMixer to exploit the full potential of KAN
lute Error (MAE) (Hyndman and Athanasopoulos 2018) to as a modeling core in LTSF. To ensure our findings are
quantitativelyevaluateandcomparemodelperformance. generalizableacrossdiverseforecastingscenarios,weselect
ExperimentalSetupForfaircomparison,westrictlyfollow three representative benchmark datasets: ETTh1, ETTm1,
theexperimentalsettingsin(Wuetal.2021a),includingthe and Weather. Across all our analyses, we observe that the
same hyperparameters such as learning rate and its sched- model exhibits remarkably consistent performance trends
uler, regularization parameter, number of epochs, random acrossthesediversedatasets.

KANMixer TimeKAN TimeMixer iTransformer Time-FFM TimesNet PatchTST FreTS DLinear TiDE
Models (Ours) 2025 2024 2024 2024 2023 2023 2024 2023 2023
MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
96 0.367 0.392 0.384 0.396 0.385 0.402 0.386 0.405 0.385 0.400 0.384 0.402 0.460 0.447 0.395 0.407 0.397 0.412 0.479 0.464
192 0.422 0.427 0.437 0.425 0.436 0.429 0.441 0.436 0.439 0.430 0.439 0.429 0.512 0.477 0.490 0.477 0.446 0.441 0.525 0.492
ETTh1
336 0.446 0.444 0.476 0.439 0.529 0.456 0.487 0.458 0.480 0.449 0.638 0.469 0.546 0.496 0.510 0.480 0.489 0.467 0.565 0.515
720 0.442 0.455 0.468 0.470 0.483 0.474 0.503 0.491 0.462 0.456 0.512 0.500 0.544 0.517 0.568 0.538 0.513 0.510 0.594 0.558
96 0.288 0.342 0.306 0.353 0.289 0.341 0.297 0.349 0.301 0.351 0.340 0.374 0.308 0.355 0.332 0.364 0.340 0.394 0.400 0.440
192 0.371 0.394 0.375 0.392 0.391 0.403 0.380 0.400 0.378 0.397 0.402 0.414 0.393 0.405 0.451 0.457 0.482 0.479 0.528 0.509
ETTh2
336 0.419 0.433 0.425 0.435 0.426 0.433 0.428 0.432 0.422 0.431 0.452 0.452 0.427 0.436 0.466 0.473 0.591 0.541 0.643 0.571
720 0.448 0.454 0.471 0.464 0.468 0.468 0.427 0.445 0.427 0.444 0.462 0.468 0.436 0.450 0.485 0.471 0.839 0.661 0.874 0.679
96 0.311 0.355 0.326 0.363 0.320 0.360 0.334 0.368 0.336 0.369 0.338 0.375 0.352 0.374 0.337 0.374 0.346 0.374 0.364 0.387
192 0.357 0.378 0.359 0.384 0.370 0.387 0.377 0.391 0.378 0.389 0.374 0.387 0.390 0.393 0.382 0.398 0.382 0.391 0.398 0.404
ETTm1
336 0.381 0.400 0.390 0.407 0.389 0.402 0.426 0.420 0.411 0.410 0.410 0.411 0.421 0.410 0.420 0.423 0.415 0.451 0.428 0.425
720 0.444 0.439 0.442 0.435 0.451 0.439 0.491 0.459 0.469 0.441 0.478 0.450 0.462 0.449 0.490 0.471 0.473 0.451 0.487 0.461
96 0.173 0.257 0.177 0.259 0.176 0.257 0.180 0.264 0.181 0.267 0.187 0.267 0.183 0.270 0.186 0.275 0.193 0.293 0.207 0.305
192 0.239 0.303 0.242 0.304 0.240 0.302 0.250 0.309 0.247 0.308 0.249 0.309 0.255 0.315 0.259 0.323 0.284 0.361 0.290 0.364
ETTm2
336 0.300 0.343 0.304 0.344 0.303 0.343 0.311 0.348 0.309 0.347 0.321 0.351 0.309 0.347 0.420 0.423 0.382 0.429 0.377 0.422
720 0.398 0.401 0.400 0.401 0.404 0.404 0.412 0.407 0.406 0.404 0.408 0.403 0.412 0.404 0.559 0.511 0.558 0.525 0.558 0.524
96 0.083 0.202 0.086 0.206 0.090 0.235 0.086 0.206 0.081 0.201 0.107 0.234 0.088 0.205 0.093 0.220 0.088 0.218 0.094 0.218
192 0.174 0.297 0.182 0.303 0.187 0.343 0.177 0.299 0.168 0.293 0.226 0.344 0.176 0.299 0.222 0.350 0.176 0.315 0.184 0.307
Exchange
336 0.323 0.411 0.349 0.427 0.353 0.473 0.331 0.417 0.299 0.396 0.367 0.448 0.301 0.397 0.386 0.467 0.313 0.427 0.349 0.431
720 0.841 0.687 0.923 0.719 0.934 0.761 0.847 0.691 0.805 0.674 0.964 0.746 0.901 0.714 0.875 0.708 0.839 0.695 0.852 0.698
96 0.162 0.209 0.163 0.209 0.162 0.209 0.174 0.214 0.191 0.230 0.172 0.220 0.186 0.227 0.171 0.227 0.195 0.252 0.202 0.261
192 0.206 0.249 0.209 0.252 0.211 0.254 0.221 0.254 0.236 0.267 0.219 0.261 0.234 0.265 0.218 0.280 0.237 0.295 0.242 0.298
Weather
336 0.264 0.291 0.264 0.292 0.263 0.293 0.278 0.296 0.289 0.303 0.246 0.337 0.284 0.301 0.265 0.317 0.282 0.331 0.287 0.335
720 0.345 0.344 0.340 0.343 0.344 0.348 0.358 0.347 0.362 0.350 0.365 0.359 0.356 0.349 0.326 0.351 0.345 0.382 0.351 0.386
96 0.162 0.260 0.177 0.267 0.156 0.247 0.148 0.240 0.198 0.282 0.168 0.272 0.190 0.296 0.171 0.260 0.210 0.302 0.237 0.329
192 0.171 0.261 0.182 0.272 0.166 0.257 0.162 0.253 0.199 0.285 0.184 0.322 0.199 0.304 0.177 0.268 0.210 0.305 0.236 0.330
Electricity
336 0.191 0.283 0.198 0.287 0.185 0.275 0.178 0.269 0.212 0.298 0.198 0.300 0.217 0.319 0.190 0.284 0.223 0.319 0.249 0.344
720 0.229 0.313 0.239 0.321 0.224 0.312 0.225 0.317 0.253 0.330 0.220 0.320 0.258 0.352 0.228 0.316 0.258 0.350 0.284 0.373
1stCount 16 11 1 7 1 6 4 3 5 6 2 0 0 0 1 0 0 0 0 0
Table1:ForecastingresultswithareviewwindowT = 96andpredictionlengthsP ∈ {96,192,336,720}.Thebestresultis
highlightedinbold,followedbyunderline.
KANversusMLPinLTSF KANandMLPvariants.WeobservethatKANachievesits
optimal performance at three layers (KAN-3L) with a nar-
A central debate around KAN is whether its advantages,
rowermodelwidthcomparedtoMLP.StackingofKANlay-
initially established in scientific computing contexts (e.g.,
ersprovidesnoadditionalgainsandcausestraininginstabil-
approximating PDE solutions), generalize broadly across
ity, occasionally leading to exploding gradients. Similar to
machine learning tasks. Tran et al. (Tran et al. 2024) re-
KAN,deeperMLPmodelsalsofailtoyieldadditionalper-
ported that KAN did not consistently outperform conven-
formancegains,indicatingpotentialoptimizationdifficulties
tionalMLPonstandardimageclassificationdatasets.Simi-
or representational limitations, further highlighting KAN’s
larambiguitiesexistinLTSF;notably,TimeKAN’s(Huang
comparativeadvantageoverMLP.
et al. 2025) ablation studies showed that substituting KAN
modules with simpler MLPs only incurs minimal perfor-
Component-wiseAblationofKANModules
mancedegradation.
To clarify the relative effectiveness of KAN and MLP Having established the general superiority of KAN, we
in LTSF, we systematically substituted KAN layers with nextseektopinpointpreciselywhichcomponentwithinthe
MLP layers in KANMixer and compared their perfor- KANMixer architecture contributes the most to its perfor-
mance across varying depths (2–4 layers). Results in Table mance.Toachievethis,weconductasystematiccomponent-
2 clearly demonstrate that KAN consistently outperforms wise ablation study, in which we sequentially replace each
MLP within our KANMixer architecture on the evaluated KAN-based module with its MLP architecture counterpart.
LTSFtasks.Toensureafaircomparison,wetreatthemodel Theresults,presentedinTable3,clearlydemonstratethatal-
widthasahyperparameterandtuneitindependentlyforthe thougheveryKANmodulecontributespositively,theKAN-

ETTh1 ETTm1 Weather
Model Chebyshev Wavelet Fourier B-spline MLP
MSE MAE MSE MAE MSE MAE
KAN-2L 0.434 0.437 0.379 0.396 0.245 0.278
0.7
KAN-3L 0.419 0.430 0.377 0.394 0.244 0.273
KAN-4L 0.436 0.438 0.381 0.396 0.246 0.289
MLP-2L 0.450 0.458 0.481 0.516 0.254 0.284
0.6
MLP-3L 0.449 0.445 0.478 0.514 0.255 0.285
MLP-4L 0.445 0.445 0.466 0.504 0.253 0.284
0.5
Table2:AblationstudyonstackingdepthcomparingKAN-
MixervariantswithKANversusMLP.
0.4
ETTh1 Weather
Model
MSE MAE MSE MAE
0.3
KANMixer(ours) 0.419 0.430 0.244 0.273 24 48 72 96 120 144 168 192 336 504 672 720
w/oKAN-FFN 0.440 0.441 0.245 0.274
(a)ETTh1dataset
w/oKAN-Mixing 0.440 0.435 0.245 0.274
w/oKAN-Prediction 0.451 0.439 0.255 0.278 Chebyshev Wavelet Fourier B-Spline MLP
1.0
Table 3: Ablation study where KANMixer modules are in-
0.9
dividuallyreplacedbyMLParchitecturecounterparts.
0.8
based prediction head emerges as the single most critical
0.7
driverofperformance.RemovingtheKAN-basedprediction
headleadstothemostsignificantperformancedegradation, 0.6
underscoring that future LTSF model designs can benefit
0.5
substantiallyfromprioritizingflexibilityatthefinalpredic-
tionstage. 0.4
We attribute this profound impact to the adaptive plas-
0.3
ticityofKAN’slearnablebasisfunctions,apropertythatis
maximallyexploitedatthefinal,mostcomplexstageoffore- 0.2
24 48 72 96 120 144 168 192 336 504 672 720
casting. This is due to the fact that the final mapping from
(b)ETTm1dataset
deep latent features to the forecast sequence typically con-
stitutesaparticularlyintricatefunctionapproximationtask, Figure 3: The MSE (Y-axis) results of different variants
wheretheflexibilityofaKANlayerlikelyprovidessuperior across various prediction lengths (X-axis) on ETTh1 and
fidelitycomparedtoaconventionalMLParchitecture.These ETTm1datasets.
findings suggest that designing novel, highly adaptive pre-
dictionheadsisapromisingdirection.Enhancingtheflexi- ingthemodel’sabilitytoreliablycapturetemporalrelation-
bilityofthefinalpredictionmoduleitself,ratherthanrelying ships.Theseresultsclarifythatthesuperiorperformanceof
onmorecomplexarchitectures,couldyieldsubstantialgains KANarchitecturesfundamentallyreliesonthechoiceofba-
forLTSF. sisfunctions,withtheadaptiveB-splineconsistentlyoutper-
formingothersduetoitsinherentflexibility.
ImpactofBasisFunctionChoiceonKAN Thisinsightalsohelpstoreinterpretseeminglycontradic-
Performance toryfindingsinrelatedwork.Forexample,TimeKAN’sab-
lationstudyshowedanegligibleperformancedropwhenits
ToinvestigatethemechanismdrivingKAN’seffectiveness,
KANmodulewasreplacedbyMLP.Ourstudyindicatesthat
we analyze the impact of the choice of the basis function.
this is likely because they used the Chebyshev basis func-
WecomparefourKANMixervariants,eachusingaB-spline
tion and did not apply a proper architectural configuration
(original),Chebyshev,Fourier,andWaveletbasisfunctions.
to their KAN module. This indicates that the vast majority
WealsoincludeastandardMLPbaselineforreference.
ofTimeKAN’sperformanceadvantagecomesfromitscas-
AsshowninFigure3,undertheKANMixerarchitecture,
caded frequency decomposition. In contrast, our work ex-
only the B-spline function consistently maintains superior
plicitlyisolatesandclarifiestheroleofbasisfunctionchoice
performance across different forecast lengths. The Cheby-
inKANeffectiveness,leadingdirectlytoourcentralcontri-
shevbasisexhibitsinconsistentbehavior,withperformance
bution:wearethefirsttoprovideclearguidelinesonconfig-
significantlydegradingasthepredictionlengthincreaseson
uringKANtofullyharnessitscapabilities.
theETTh1dataset,indicatinglimitedlong-termforecasting
capability, though it still manages to outperform the MLP
ImpactofStructuralPriorsonKANPerformance
ontheETTm1dataset.Incontrast,bothFourierandWavelet
basesconsistentlyfailtoyieldimprovementsovertheMLP. To understand the interaction between KAN and the struc-
Notably,theWaveletbasisexperiencessevereinstabilityand tural priors, which commonly include decomposition and
convergence issues at longer prediction lengths, undermin- multi-scalerepresentations.Specifically,weappliedtwode-

96 192 336 720
Method MACs Params
Mem Time Mem Time Mem Time Mem Time
KANMixer(MLP) 21.44M 92.9K 1.1 17.6 1.3 16.1 1.6 16.9 2.3 15.8
KANMixer(B-spline) 90.57M 321.73K 3.7 49.9 5.2 48.8 7.4 49.2 13.7 51.5
KANMixer(Chebyshev) 22.93M 160.93K 1.9 28.9 2.6 28.8 3.7 29.6 7.4 30.2
KANMixer(Fourier) 126.04M 371.10K 4.4 29.4 6.1 28.6 8.6 28.9 15.8 27.0
KANMixer(Wavelet) 39.12M 120.73K 1.4 26.0 2.0 26.2 2.8 30.9 5.0 42.1
TimeKAN 7.63M 17.45K 1.0 27.0 1.4 28.4 2.0 31.1 3.8 30.3
TimeMixer 30.40M 133.74K 1.5 16.3 1.7 16.1 2.0 16.7 2.7 15.8
PatchTST 5.89G 3.75M 4.7 6.7 6.6 6.6 9.0 7.4 15.7 7.6
iTransformer 28.05M 224.22K 37.3 6.3 37.8 6.3 38.7 6.7 40.9 7.0
Table4:Computationcost(MACs),parameterfootprint,andtraining-resourceconsumption(peakGPUmemoryinMiBand
epochwall-timeinseconds)onETTh1fordifferentlook-backwindows.(M=106;G=109).
Model ETTh1 ETTm1 ∆MSE Mixer with different basis functions compared to main-
MSE MAE MSE MAE stream methods in three key aspects: computational cost,
MLP 0.459 0.445 0.392 0.411 N/A
trainingefficiency,andGPUmemoryconsumption.
MLP DFT 0.456 0.452 0.388 0.402 -0.003(↓)
First, KANMixer has higher computation costs (MAC)
MLP MA 0.448 0.447 0.381 0.405 -0.011(↓)
and more parameters than its MLP counterpart, reflect-
MLP NoMS 0.464 0.441 0.398 0.416 +0.005(↑)
KAN 0.419 0.430 0.377 0.394 N/A ing a trade-off between computational cost and enhanced
KAN DFT 0.444 0.447 0.387 0.401 +0.025(↑) approximation capability. However, even our most com-
KAN MA 0.452 0.450 0.384 0.400 +0.033(↑) plex KANMixer variant remains significantly lighter than
KAN NoMS 0.439 0.438 0.383 0.397 +0.020(↑) mainstream Transformer models like PatchTST (90.57M
vs. 5.89G MACs), firmly placing it within the category of
Table 5: Ablation study on the effect of structural priors. lightweightmodels.Second,despitecomparabletheoretical
Positive ∆ values indicate performance degradation, and MACs (22.93M vs. 21.44M), KAN variants exhibit notice-
negative values indicate performance improvement relative ablylongertrainingtimes.Forexample,Cheby-KANMixer
tothebaselinemodel. takes nearly twice as long to train compared to the MLP
composition methods, Discrete Fourier Transform (DFT) version (28.9s vs. 17.6s). This indicates the root cause is
and Moving Average (MA), to our KANMixer architec- not inherent computational complexity, but rather the cur-
ture to explicitly disentangle intricate temporal variations. rent lack of optimized low-level CUDA kernels, similar to
Inaseparateexperiment,weablateKANMixer’smulti-scale those available for linear layers. Third, GPU memory con-
processingmodule(KAN NoMS)toassessitscontribution. sumption rises with prediction length, potentially limiting
The results in Table 5 reveal an unexpected result: applicabilityinextremelylong-horizonscenarios.
while decomposition slightly improves MLP performance, Insummary,werecognizethesechallengesasrealbutpri-
it surprisingly degrades KAN’s performance, regardless of marily engineering hurdles rather than fundamental limita-
whether decomposition is applied in the frequency domain tions.Optimizationssuchasspecializedcomputekernelsor
(DFT) or the time domain (MA). We hypothesize that ar- modelpruningtechniquesholdsignificantpromiseforsub-
tificially imposed structural priors potentially limit KAN’s stantiallymitigatingtheseoverheads.
capability to adaptively learn representations directly from
rawdata,thuslimitingitseffectiveness.
ConclusionandFutureWork
In contrast, removing the multi-scale module also leads
toaperformancedrop,highlightingacomplementaryprin- ConclusionInthispaper,weexploreKANasanovelmod-
ciple: although KAN resists artificial structural constraints, eling core for LTSF. We propose KANMixer, a concise ar-
itbenefitssubstantiallyfromthecomplementaryforecasting chitecture solely built upon KAN-based components, em-
capabilitiesprovidedbyenrichedmulti-scaleinputfeatures. ployingaminimalisticmulti-scalemixingbackboneanddi-
This enables KAN to dynamically integrate coarse-grained verging from the trend of introducing external complexity.
representations for long-term patterns and fine-grained in- Experimental evaluations demonstrate KANMixer’s SOTA
puts for local fluctuations, aligning well with its adaptive performance.Moreover,oursystematicanalysesrevealcrit-
modelingstrengths. icalinsightsintoKAN’sadvantages,includingadaptiveba-
sisfunctionselectionandinteractionswithstructuralpriors.
ComputationalEfficiencyandResourceAnalysisof
These findings provide practical guidelines for effectively
KAN leveraging KAN, suggesting a promising path toward sim-
AlthoughKANdemonstratesexcellentperformance,transi- pleryetmorepowerfulforecastingmodels.
tioning it from a research prototype to a practical tool re- FutureWorkcouldaddressthecomputationaloverhead
quires addressing several overhead considerations. In Ta- andmemorydemandsofKANbyoptimizingcomputational
ble 4, we systematically evaluate the efficiency of KAN- kernelsandexploringmodelcompressiontechniques.

References Huang,S.;Zhao,Z.;Li,C.;andBAI,L.2025. TimeKAN:
KAN-based Frequency Decomposition Learning Architec-
Bozorgasl, Z.; and Chen, H. 2024. Wav-KAN: Wavelet
ture for Long-term Time Series Forecasting. In The Thir-
Kolmogorov-ArnoldNetworks. arXiv:2405.12832.
teenth International Conference on Learning Representa-
Brigato, L.; Morand, R.; Strømmen, K.; Panagiotou, M.; tions.
Schmidt, M.; and Mougiakakou, S. 2025. Position: There
Hyndman, R.; and Athanasopoulos, G. 2018. Forecasting:
are no Champions in Long-Term Time Series Forecasting.
PrinciplesandPractice. Australia:OTexts,2ndedition.
arXiv:2502.14045.
Ji, T.; Hou, Y.; and Zhang, D. 2025. A Comprehen-
Cao, X.; Zhuang, D.; Zhao, J.; and Wang, S. 2025. sive Survey on Kolmogorov Arnold Networks (KAN).
Virtual Nodes Improve Long-term Traffic Prediction. arXiv:2407.11075.
arXiv:2501.10048.
Jiang, X.; Zhang, W.; Fang, Y.; Gao, X.; Chen, H.; Zhang,
Chen,S.-A.;Li,C.-L.;Yoder,N.;Arik,S.O.;andPfister,T. H.; Zhuang, D.; and Luo, J. 2025. Time series supplier al-
2023a. TSMixer:AnAll-MLPArchitectureforTimeSeries locationviadeepblack-littermanmodel. InProceedingsof
Forecasting. arXiv:2303.06053. the AAAI Conference on Artificial Intelligence, volume 39,
11870–11878.
Chen, T.; and Guestrin, C. 2016. XGBoost: A Scalable
Tree Boosting System. In Proceedings of the 22nd ACM Ke, G.; Meng, Q.; Finley, T.; Wang, T.; Chen, W.; Ma, W.;
SIGKDD International Conference on Knowledge Discov- Ye,Q.;andLiu,T.-Y.2017. LightGBM:AHighlyEfficient
ery and Data Mining, KDD ’16, 785–794. New York, Gradient Boosting Decision Tree. In Guyon, I.; Luxburg,
NY, USA: Association for Computing Machinery. ISBN U. V.; Bengio, S.; Wallach, H.; Fergus, R.; Vishwanathan,
9781450342322. S.; and Garnett, R., eds., Advances in Neural Information
ProcessingSystems,volume30.CurranAssociates,Inc.
Chen,Z.;Ma,M.;Li,T.;Wang,H.;andLi,C.2023b. Long
sequencetime-seriesforecastingwithdeeplearning:Asur- Lai,G.;Chang,W.-C.;Yang,Y.;andLiu,H.2018.Modeling
vey. InformationFusion,97:101819. Long-andShort-TermTemporalPatternswithDeepNeural
Networks. arXiv:1703.07015.
D YAMADA, K.; Lin, F.; and Nakamura, T. 2021. De-
Liu,J.;Ma,T.;Su,Y.;Rong,H.;Khalil,A.A.E.-R.M.;Wa-
velopinganovelrecurrentneuralnetworkarchitecturewith
hab,M.M.A.;andOsibo,B.K.2024a. Temporalpatterns
fewerparametersandgoodlearningperformance. Interdis-
decomposition and Legendre projection for long-term time
ciplinaryinformationsciences,27(1):25–40.
seriesforecasting. TheJournalofSupercomputing,80(16):
Das, A.; Kong, W.; Leach, A.; Mathur, S. K.; Sen, R.; and 23407–23441.
Yu,R.2023.Long-termForecastingwithTiDE:Time-series
LIU,M.;Zeng,A.;Chen,M.;Xu,Z.;LAI,Q.;Ma,L.;and
Dense Encoder. Transactions on Machine Learning Re-
Xu,Q.2022. SCINet:TimeSeriesModelingandForecast-
search.
ingwithSampleConvolutionandInteraction. InOh,A.H.;
Deng,J.;Ye,F.;Yin,D.;Song,X.;Tsang,I.;andXiong,H. Agarwal, A.; Belgrave, D.; and Cho, K., eds., Advances in
2024. Parsimonyorcapability?decompositiondeliversboth NeuralInformationProcessingSystems.
in long-term time series forecasting. Advances in Neural
Liu, Q.; Liu, X.; Liu, C.; Wen, Q.; and Liang, Y. 2024b.
InformationProcessingSystems,37:66687–66712.
Time-FFM: Towards LM-Empowered Federated Founda-
Gao,X.;Jiang,X.;Haworth,J.;Zhuang,D.;Wang,S.;Chen, tionModelforTimeSeriesForecasting.InTheThirty-eighth
H.;andLaw,S.2024.Uncertainty-awareprobabilisticgraph Annual Conference on Neural Information Processing Sys-
neuralnetworksforroad-leveltrafficcrashprediction. Acci- tems.
dentAnalysisPrevention,208:107801.
Liu, Y.; Hu, T.; Zhang, H.; Wu, H.; Wang, S.; Ma, L.; and
Gao,X.;Jiang,X.;Zhuang,D.;Chen,H.;Wang,S.;andHa- Long, M. 2024c. iTransformer: Inverted Transformers Are
worth,J.2023. Spatiotemporalgraphneuralnetworkswith EffectiveforTimeSeriesForecasting. InTheTwelfthInter-
uncertaintyquantificationfortrafficincidentriskprediction. nationalConferenceonLearningRepresentations.
CoRR. Liu,Y.;Zhang,Y.;Zhang,X.;Yang,Y.;Xie,Y.;Machiani,
S. G.; Li, Y.; and Luo, J. 2024d. Align Along Time and
Gong, Z.; Tang, Y.; and Liang, J. 2024. PatchMixer:
Space:AGraphLatentDiffusionModelforTrafficDynam-
A Patch-Mixing Architecture for Long-Term Time Series
ics Prediction. In 2024 IEEE International Conference on
Forecasting.
DataMining(ICDM),271–280.
Han, X.; Zhang, X.; Wu, Y.; Zhang, Z.; and Wu, Z. 2025.
Liu,Z.;Wang,Y.;Vaidya,S.;Ruehle,F.;Halverson,J.;Sol-
AreKANsEffectiveforMultivariateTimeSeriesForecast-
jacic, M.; Hou, T. Y.; and Tegmark, M. 2025. KAN: Kol-
ing? arXiv:2408.11306.
mogorov–ArnoldNetworks.InTheThirteenthInternational
Ho, S.; and Xie, M. 1998. The use of ARIMA models for ConferenceonLearningRepresentations.
reliability forecasting and analysis. Computers Industrial
Lyu, Y.; Li, M.; Huang, X.; Guler, U.; Schaumont, P.; and
Engineering,35(1):213–216.
Zhang,Z.2021.TreeRNN:Topology-preservingdeepgraph
Hochreiter,S.;andSchmidhuber,J.1997. LongShort-Term embeddingandlearning.In202025thInternationalConfer-
Memory. NeuralComputation,9(8):1735–1780. enceonPatternRecognition(ICPR),7493–7499.IEEE.

Meijer, C.; and Chen, L. Y. 2024. The Rise of Diffusion Wu, H.; Hu, T.; Liu, Y.; Zhou, H.; Wang, J.; and Long,
ModelsinTime-SeriesForecasting. arXiv:2401.03006. M.2023a. TimesNet:Temporal2D-VariationModelingfor
GeneralTimeSeriesAnalysis. InInternationalConference
Murad,M.M.N.;Aktukmak,M.;andYilmaz,Y.2024.WP-
onLearningRepresentations.
Mixer: Efficient Multi-Resolution Mixing for Long-Term
TimeSeriesForecasting. arXiv:2412.17176. Wu, H.; Xu, J.; Wang, J.; and Long, M. 2021a. Auto-
former:DecompositionTransformerswithAuto-Correlation
Nie, Y.; Nguyen, N. H.; Sinthong, P.; and Kalagnanam, J.
for Long-Term Series Forecasting. In Beygelzimer, A.;
2023. A Time Series is Worth 64 Words: Long-term Fore-
Dauphin, Y.; Liang, P.; and Vaughan, J. W., eds., Advances
casting with Transformers. In The Eleventh International
inNeuralInformationProcessingSystems.
ConferenceonLearningRepresentations.
Wu, H.; Zhou, H.; Long, M.; and Wang, J. 2023b. Inter-
Rajagukguk, R. A.; Ramadhan, R. A. A.; and Lee, H.-J.
pretable weather forecasting for worldwide stations with a
2020. A Review on Deep Learning Models for Forecast-
unifieddeepmodel. Nat.Mac.Intell.,5(6):602–611.
ing Time Series Data of Solar Irradiance and Photovoltaic
Wu,Y.;Zhuang,D.;Labbe,A.;andSun,L.2021b.Inductive
Power. Energies,13(24).
graph neural networks for spatiotemporal kriging. In Pro-
Salinas, D.; Flunkert, V.; and Gasthaus, J. 2019. DeepAR: ceedings of the AAAI conference on artificial intelligence,
Probabilistic Forecasting with Autoregressive Recurrent volume35,4478–4485.
Networks. arXiv:1704.04110.
Wu, Z.; Pan, S.; Long, G.; Jiang, J.; Chang, X.; and
Schmidt-Hieber, J. 2021. The Kolmogorov–Arnold repre- Zhang, C. 2020. Connecting the Dots: Multivariate
sentation theorem revisited. Neural Networks, 137: 119– Time Series Forecasting with Graph Neural Networks.
126. arXiv:2005.11650.
Shabani, A.; Abdi, A.; Meng, L.; and Sylvain, T. 2022. Yamada,K.D.;Baladram,M.S.;andLin,F.2022. Relation
Scaleformer: Iterative multi-scale refining transformers for isanoptionforprocessingcontextinformation. Frontiersin
timeseriesforecasting. arXivpreprintarXiv:2206.04038. ArtificialIntelligence,5:924688.
SS, S.; AR, K.; R, G.; and KP, A. 2024. Chebyshev Yi,K.;Zhang,Q.;Fan,W.;Wang,S.;Wang,P.;He,H.;An,
Polynomial-BasedKolmogorov-ArnoldNetworks:AnEffi- N.;Lian,D.;Cao,L.;andNiu,Z.2023. Frequency-domain
cient Architecture for Nonlinear Function Approximation. MLPsareMoreEffectiveLearnersinTimeSeriesForecast-
arXiv:2405.07200. ing. In Thirty-seventh Conference on Neural Information
ProcessingSystems.
Tran, V. D.; Le, T. X. H.; Tran, T. D.; Pham, H. L.; Le, V.
Zeng,A.;Chen,M.;Zhang,L.;andXu,Q.2023.AreTrans-
T.D.;Vu,T.H.;Nguyen,V.T.;andNakashima,Y.2024.Ex-
formers Effective for Time Series Forecasting? Proceed-
ploringtheLimitationsofKolmogorov-ArnoldNetworksin
ingsoftheAAAIConferenceonArtificialIntelligence,37(9):
Classification: Insights to Software Training and Hardware
11121–11128.
Implementation. arXiv:2407.17790.
Zhang, J.; Fan, Y.; Cai, K.; and Wang, K. 2025.
Trindade, A. 2015. ElectricityLoadDiagrams20112014.
Kolmogorov-ArnoldFourierNetworks. arXiv:2502.06018.
UCI Machine Learning Repository. DOI:
Zhong, S.; Song, S.; Zhuo, W.; Li, G.; Liu, Y.; and Chan,
https://doi.org/10.24432/C58C86.
S.-H.G.2023. Amulti-scaledecompositionmlp-mixerfor
Vaca-Rubio, C. J.; Blanco, L.; Pereira, R.; and Caus, M.
timeseriesanalysis. arXivpreprintarXiv:2310.11959.
2024. Kolmogorov-ArnoldNetworks(KANs)forTimeSe-
Zhou, H.; Zhang, S.; Peng, J.; Zhang, S.; Li, J.; Xiong, H.;
riesAnalysis. arXiv:2405.08790.
and Zhang, W. 2021. Informer: Beyond Efficient Trans-
Vaswani, A.; Shazeer, N.; Parmar, N.; Uszkoreit, J.; Jones, former for Long Sequence Time-Series Forecasting. Pro-
L.;Gomez,A.N.;Kaiser,L.;andPolosukhin,I.2023. At- ceedings of the AAAI Conference on Artificial Intelligence,
tentionIsAllYouNeed. arXiv:1706.03762. 35(12):11106–11115.
Wang, H.; Pan, L.; Shen, Y.; Chen, Z.; Yang, D.; Yang, Y.; Zhou, T.; Ma, Z.; Wen, Q.; Wang, X.; Sun, L.; and Jin,
Zhang,S.;Liu,X.;Li,H.;andTao,D.2025a.FreDF:Learn- R. 2022. FEDformer: Frequency Enhanced Decomposed
ingtoForecastintheFrequencyDomain. InTheThirteenth Transformer for Long-term Series Forecasting. In Chaud-
InternationalConferenceonLearningRepresentations. huri,K.;Jegelka,S.;Song,L.;Szepesvari,C.;Niu,G.;and
Wang,S.;Wu,H.;Shi,X.;Hu,T.;Luo,H.;Ma,L.;Zhang,
Sabato,S.,eds.,Proceedingsofthe39thInternationalCon-
J.Y.;andZHOU,J.2024. TimeMixer:DecomposableMul- ference on Machine Learning, volume 162 of Proceedings
tiscaleMixingforTimeSeriesForecasting. InTheTwelfth ofMachineLearningResearch,27268–27286.PMLR.
InternationalConferenceonLearningRepresentations. Zhuang,D.;Huang,Y.;Jayawardana,V.;Zhao,J.;Suo,D.;
andWu,C.2022. TheBraess’sParadoxinDynamicTraffic.
Wang, Y.; Sun, J.; Bai, J.; Anitescu, C.; Eshaghi,
In 2022 IEEE 25th International Conference on Intelligent
M. S.; Zhuang, X.; Rabczuk, T.; and Liu, Y. 2025b.
TransportationSystems(ITSC),1018–1023.IEEE.
Kolmogorov–Arnold-Informed neural network: A physics-
informeddeeplearningframeworkforsolvingforwardand Zhuang, D.; Jiang, C.; Zheng, Y.; Wang, S.; and Zhao,
inverse problems based on Kolmogorov–Arnold Networks. J. 2024. GETS: Ensemble Temperature Scaling for
ComputerMethodsinAppliedMechanicsandEngineering, Calibration in Graph Neural Networks. arXiv preprint
433:117518.
arXiv:2410.09570.

ReproducibilityChecklist perwithalicensethatallowsfreeusageforresearch
purposes(yes/partial/no/NA)yes
3.5. All datasets drawn from the existing literature (po-
1.GeneralPaperStructure
tentially including authors’ own previously pub-
1.1. Includes a conceptual outline and/or pseudocode de- lished work) are accompanied by appropriate cita-
scriptionofAImethodsintroduced(yes/partial/no/NA) tions(yes/no/NA)yes
yes
3.6. All datasets drawn from the existing literature
1.2. Clearlydelineatesstatementsthatareopinions,hypoth- (potentially including authors’ own previously
esis, and speculation from objective facts and results published work) are publicly available (yes/par-
(yes/no)yes tial/no/NA)yes
1.3. Provideswell-markedpedagogicalreferencesforless- 3.7. All datasets that are not publicly available are de-
familiarreaderstogainbackgroundnecessarytorepli- scribed in detail, with explanation why publicly
catethepaper(yes/no)yes availablealternativesarenotscientificallysatisficing
(yes/partial/no/NA)NA
2.TheoreticalContributions
2.1. Does this paper make theoretical contributions? 4.ComputationalExperiments
(yes/no)no
4.1. Does this paper include computational experiments?
Ifyes,pleaseaddressthefollowingpoints:
(yes/no)yes
2.2. All assumptions and restrictions are stated clearly Ifyes,pleaseaddressthefollowingpoints:
and formally (yes/partial/no) Type your response
here 4.2. This paper states the number and range of values
tried per (hyper-) parameter during development of
2.3. Allnovelclaimsarestatedformally(e.g.,intheorem thepaper,alongwiththecriterionusedforselecting
statements)(yes/partial/no)Typeyourresponsehere the final parameter setting (yes/partial/no/NA) par-
tial
2.4. Proofs of all novel claims are included (yes/par-
tial/no)Typeyourresponsehere 4.3. Any code required for pre-processing data is in-
cludedintheappendix(yes/partial/no)no
2.5. Proof sketches or intuitions are given for complex
and/or novel results (yes/partial/no) Type your re- 4.4. Allsourcecoderequiredforconductingandanalyz-
sponsehere ing the experiments is included in a code appendix
(yes/partial/no)yes
2.6. Appropriate citations to theoretical tools used are
given(yes/partial/no)Typeyourresponsehere 4.5. All source code required for conducting and ana-
lyzing the experiments will be made publicly avail-
2.7. All theoretical claims are demonstrated empirically
able upon publication of the paper with a license
tohold(yes/partial/no/NA)Typeyourresponsehere
that allows free usage for research purposes (yes/-
2.8. Allexperimentalcodeusedtoeliminateordisprove partial/no)yes
claims is included (yes/no/NA) Type your response
4.6. All source code implementing new methods have
here
comments detailing the implementation, with refer-
encestothepaperwhereeachstepcomesfrom(yes/-
3.DatasetUsage partial/no)yes
3.1. Doesthispaperrelyononeormoredatasets?(yes/no) 4.7. If an algorithm depends on randomness, then the
yes method used for setting seeds is described in a way
Ifyes,pleaseaddressthefollowingpoints: sufficient to allow replication of results (yes/par-
tial/no/NA)yes
3.2. A motivation is given for why the experiments
are conducted on the selected datasets (yes/par- 4.8. This paper specifies the computing infrastructure
tial/no/NA)yes used for running experiments (hardware and soft-
ware), including GPU/CPU models; amount of
3.3. All novel datasets introduced in this paper are in- memory; operating system; names and versions of
cludedinadataappendix(yes/partial/no/NA)NA relevantsoftwarelibrariesandframeworks(yes/par-
tial/no)yes
3.4. All novel datasets introduced in this paper will be
madepubliclyavailableuponpublicationofthepa- 4.9. This paper formally describes evaluation metrics

usedandexplainsthemotivationforchoosingthese
metrics(yes/partial/no)yes
4.10. Thispaperstatesthenumberofalgorithmrunsused
tocomputeeachreportedresult(yes/no)yes
4.11. Analysis of experiments goes beyond single-
dimensional summaries of performance (e.g., aver-
age; median) to include measures of variation, con-
fidence, or other distributional information (yes/no)
no
4.12. Thesignificanceofanyimprovementordecreasein
performance is judged using appropriate statistical
tests(e.g.,Wilcoxonsigned-rank)(yes/partial/no)no
4.13. This paper lists all final (hyper-)parameters used
foreachmodel/algorithminthepaper’sexperiments
(yes/partial/no/NA)yes

