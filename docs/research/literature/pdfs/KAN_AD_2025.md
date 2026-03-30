# Page 1

KAN-AD: Time Series Anomaly Detection with Kolmogorov–Arnold Networks
QuanZhou12 ChanghuaPei13 FeiSun4 JingHan5 ZhengweiGao5 HaimingZhang1 GaogangXie1
DanPei6 JianhuiLi71
Abstract
Local Peaks
Local Drop Local Drop
Timeseriesanomalydetection(TSAD)underpins Figure1. Illustrationoflocaldropsandpeaks.
real-timemonitoringincloudservicesandweb
systems,allowingrapididentificationofanoma-
Time Series Anomaly Score
✅ ✅ ✅
liestopreventcostlyfailures. MostTSADmeth-
odsdrivenbyforecastingmodelstendtooverfit Clean Train Sample
by emphasizing minor fluctuations. Our analy-
❌ ❌ ✅
sisrevealsthateffectiveTSADshouldfocuson
modeling“normal”behaviorthroughsmoothlo- Noisy Train Sample
calpatterns. Toachievethis,wereformulatetime
Figure2.Comparisonofanomalydetectionperformance.Top:All
seriesmodelingasapproximatingtheserieswith
methodssuccessfullydetectanomalieswhentrainedoncleandata
smoothunivariatefunctions. Thelocalsmooth-
(blackcurve,anomaloussegmentsinpink). Bottom: TimesNet
nessofeachunivariatefunctionensuresthatthe
andKANfailtodetectanomalieswhentrainedonnoisydata.Blue
fitted time series remains resilient against local
markersindicatelocaldropsandpeaks;redcurveshowsanomaly
disturbances. However,adirectKANimplemen-
scores.
tation proves susceptible to these disturbances
duetotheinherentlylocalizedcharacteristicsof 1.Introduction
B-splinefunctions. WethusproposeKAN-AD,
TimeSeriesAnomalyDetection(TSAD)servesasacriti-
replacingB-splineswithtruncatedFourierexpan-
calcomponentinmodernITinfrastructure(Lietal.,2019;
sionsandintroducinganovellightweightlearning
Qu et al., 2024) and manufacturing systems (Zhan et al.,
mechanismthatemphasizesglobalpatternswhile
2021;Wangetal.,2022), enablingrapididentificationof
stayingrobusttolocaldisturbances. Onfourpop-
potentialanomaliesandprovidingsufficientcluesforfault
ular TSAD benchmarks, KAN-AD achieves an
localization(Sunetal.,2024;Kieuetal.,2022). Theemer-
average15%improvementindetectionaccuracy
genceofdeeplearning-basedforecastingapproaches(Xu
(withpeaksexceeding27%)overstate-of-the-art
etal.,2022;Wuetal.,2023;Zhouetal.,2023)havesuper-
baselines. Remarkably, it requires fewer than
sededtraditionalrule-basedmethods(Breunigetal.,2000;
1,000 trainable parameters, resulting in a 50%
Sifferetal.,2017),establishingnewstate-of-the-artperfor-
faster inference speed compared to the original
mancethroughtheircapacitytofithistoricaldataanddetect
KAN, demonstrating the approach’s efficiency
anomaliesviaprediction-observationcomparisons.
andpracticalviability.
However, the effectiveness of the forecasting-based ap-
proachdeclineswhenencounteringtimeserieswithlocal-
ized disturbances. As illustrated in Figure 1, time series
1Computer Network Information Center, Chinese Academy
of Sciences 2University of the Chinese Academy of Sciences datafrequentlyexhibitlocalpeaksanddropsthatcansig-
3HangzhouInstituteforAdvancedStudy,UniversityoftheChi- nificantly impact model learning. Existing deep learning
neseAcademyofSciences4InstituteofComputingTechnology, methods (Tuli et al., 2022; Wu et al., 2023) often overfit
ChineseAcademyofSciences5ZTE6DepartmentofComputer
totheselocaldisturbances, compromisingtheirabilityto
ScienceandTechnology,TsinghuaUniversity7SchoolofFron-
detectanomalieseffectively. FromthethirdcolumnofFig-
tierSciences,NanjingUniversity.Correspondenceto:JianhuiLi
<lijh@nju.edu.cn>,ChanghuaPei<chpei@cnic.cn>. ure2,wecanobservethatcomparedtotrainingwithclean
data,TimesNet(Wuetal.,2023)trainedonnoisydatafails
Proceedingsofthe42nd InternationalConferenceonMachine todetectanomaliesinthesamples.
Learning,Vancouver,Canada.PMLR267,2025.Copyright2025
bytheauthor(s). Our experimental analysis reveals that forecasting-based
1
5202
luJ
8
]GL.sc[
3v87200.1142:viXra

---

# Page 2

KAN-AD:TimeSeriesAnomalyDetectionwithKolmogorov–ArnoldNetworks
TSADmethodssufferperformancedegradationbyattempt- termswhichiscomputationintensive,weonlyusethefirst
ingtomodeleverydetailedpatternsinrawtimeseriesdata. N termsofFourierseries. Toovercomethelimitationthat
While these methods aim to identify anomalies through thefirstNtermsofFourierseriescanonlymodelperiodic
comparisonwithpredictedbehavior,suchdetailedmodel- nosmallerthan 1,wedesignedanalternativeindex-based
N
ingprovesunnecessaryandpotentiallydetrimental, espe- univariatefunctiontocapturethefine-scaleperiodicmissing
cially given that real-world time series typically contain fromthefirstNterms. Third,weincorporateddifferencing
variousformsofanomaliesandirrelevantdisturbances,pre- to isolate time series trend effects on coefficient estima-
senting two significant challenges: firstly, the difficulty tion,leadingtoimprovedmodelingaccuracythroughmore
inestablishingauniversalcriterionforfilteringthesedis- precisecoefficients.
turbances,andsecondly,developinganothermodeltoen-
OurcomprehensiveevaluationdemonstratesthatKAN-AD
sure the forecasting model’s input is free of local distur-
achieves15%higherF1accuracywhilebeing50%faster
bancesisresource-intensive. Giventheseinherentlimita-
thantheoriginalKANarchitecture. Ourcodeispublicly
tionsinbothfiltering-basedanddual-modelingapproaches,
available at https://github.com/CSTCloudOps/
researchershaveexploredVAE-basedapproachestoaddress
KAN-AD. Ourcontributionsareasfollows:
thechallengeoflocaldisturbancemitigation. VAE-based
approaches(Xuetal.,2018;Wangetal.,2024)assumethat • We reformulate the problem to assist deep learning-
normalpatternsintimeseriesclusterinalow-dimensional basedforecastingmodelsfortimeseriesanomalyde-
latentspaceandcanbeeffectivelyreconstructed,thereby tection(TSAD)tasksbyminimizingoverfittingtolocal
overcoming interference from data perturbations. Never- perturbations.
theless, as demonstrated in FCVAE (Wang et al., 2024),
VAE-based approaches struggle with underfitting, which
• WeintroduceKAN-AD,aninnovativeTSADapproach.
impairstheirabilitytoreconstructtheoriginaltimeseries
KAN-AD,builtmeticulouslyontheKANbackbone,
andlimitstheireffectiveness.
exhibits substantial improvements in both detection
Tomitigatelocaldisturbances,wereformulateTSADbyap- precisionandinferenceefficiency.
proximatingtimeseriesusingsmoothunivariatefunctions,
buildingonthetheoreticalfoundationthatnormalsequences
• Weperformedcomprehensiveexperimentsonfourpub-
exhibitgreaterlocalsmoothnessthanabnormalones(Xu
liclyavailabledatasets,verifyingtheeffectivenessand
et al., 2022). To achieve this formulation, Kolmogorov-
efficiencyagainststate-of-the-artTSADbenchmarks.
ArnoldNetworks(KANs)(Liuetal.,2025)offerapromis-
ingdirectionbydecomposingcomplexobjectivesintocom-
binations of learnable univariate functions based on the 2.PreliminariesandProblemFormulation
Kolmogorov-Arnoldrepresentationtheorem(Kolmogorov,
2.1.ProblemStatement
1957). Thisdecompositionapproachhasshownremarkable
effectivenessinvariousdomains(Yuetal.,2024;Bodner This paper primarily addresses the issue of anomaly de-
etal.,2024). However,directapplicationofKANtoTSAD tection in single time series curves, also known as uni-
presents significant challenges. From the fourth column variate time series (UTS). To elaborate on the problem
intheupperpartofFigure2,itcanbeobservedthatmod- morecomprehensively,considerthefollowingUTSobserva-
elstrainedoncleantrainingsamplescandetectanomalies tionaldata: x ={x ,x ,x ,...,x }andanomalylabels
0:t 0 1 2 t
in the test samples. But we find that KAN fails to detect C = {c ,c ,c ,...,c }, where x ∈ R, c ∈ {0,1}, and
0 1 2 t t
anomalieswhenthetrainingsamplescontainnoisysamples t∈N. Here,x representstheentireobservedtimeseries,
0:t
. Themainreasonisthat,althoughKANcanspecifyuni- andC denotesthetemporalanomalylabels.
variatefunctions,i.e.,B-spinefunction,thesefunctionsare
GivenaUTSx=[x ,x ,x ,...,x ],theobjectiveofUTS
notspecificallydesignedfortimeseriesandcanstilloverfit 0 1 2 t
anoomaly detection is to utilize the data [x ,x ,...,x ]
localfeatures,failingtocompletelyeliminatetheimpactof 0 1 i
precedingeachpointx topredictc .
localpeaksordrops. i i
Toaddressthesechallenges,weproposeKAN-AD,adopt- 2.2.Kolmogorov–ArnoldNetworks
ingKANasourbackbone. Byconsideringthecharacteris-
ticsoftimeseries,weredesignKANinthreeaspects. First, 2.2.1.THEORETICALFOUNDATION
wereplacetheB-spinefunctionwithFourierseries. Fourier
The Kolmogorov–Arnold representation theorem demon-
serieshavelocalsmoothnesscomparedtosplinefunctions,
strates that any multivariate continuous function can be
while their natural periodicity allows for better modeling
decomposed into a finite sum of univariate functions, as
ofglobalpatterns(Dym&HP,1972;Stein&Shakarchi,
showninEquation(1),whereφ areunivariatefunctions
q,p
2011). Second, as the Fourier series contains unlimited
that map each input variable x , and Φ are continuous
p q
2

---

# Page 3

KAN-AD:TimeSeriesAnomalyDetectionwithKolmogorov–ArnoldNetworks
functions.
H=Stack(cos(x ),sin(x ),...,cos(nx ),sin(nx ))
2n+1 n 0:i 0:i 0:i 0:i
f(x 1 ,x 2 ,...,x n )= (cid:88) Φ q ( (cid:88) φ q,p (x p )) (1) Θ(x 0:i )= (cid:2) A 1 ,B 1 ,A 2 ,B 2 ,...,A n ,B n (cid:3)
q=1 p=1 x′ =A +Θ(x )×H (4)
0:i 0 0:i
KAN(x)=(Φ ◦Φ ◦···◦Φ )(x) (2)
L−1 L−2 0
Formally,weemployFourierseriesfornormalpatternrep-
2.2.2.NETWORKARCHITECTUREANDFUNCTION
resentation, motivated by two key advantages over alter-
REPRESENTATION
native approaches such as B-spline functions. First, the
KANconsistsofaseriesofinterconnectedunivariatesub- constituent sine and cosine functions exhibit superior lo-
networks,eachresponsibleforlearningdistinctfeaturesof calsmoothness,avoidingthepotentialoverfittingtolocal
thedata. Unliketraditionalmulti-layerperceptrons(MLPs), noise. Second,Fourierseriesnaturallycaptureglobalpat-
whichemployfixedactivationfunctionsateachnode,KAN terns,particularlyexcellingatmodelingperiodicbehaviors
replaceseachweightparameterwithaunivariatefunction. in time series. Following this motivation, we introduce
TheresultingfunctionalformfordeeperKANcanbeex- thefunctiondeconstruction(FD)mechanism,wheref,the
pressedasEquation(2),whereeachΦ l representsalayer mapping between the historical window x 0:i and its next
ofunivariatefunctionsappliedtotheinputorintermediate behaviorx i+1 ,canbeexpandedasshowninEquation(3).
outputs. The vanilla KAN (Liu et al., 2025) implements ThenormalpatterncanberepresentedbythefiniteN terms
theseunivariatefunctionsusingB-splines(DeBoor,1978), oftheseries(Kolmogorov,1957),denotedasg(x),while
whichprovidelocalizedfunctionapproximationcapabili- the terms beyond N capture the stochastic observational
ties. However,thislocalizationpropertypresentsanotable noiseϵ. Thenormalpatternx′ 0:i canthenbeexpressedas
considerationinanomalydetectioncontexts. Sinceanoma- inEquation(4), whereHdenotestheunivariatefunction
lous patterns typically manifest as localized features (Xu matrix. Thisdecompositioncombinedwithlearnablecoeffi-
etal.,2022),B-splinesmayinadvertentlyfittheseoutliers, cientsfiltersoutpotentialnoiseandsignificantlysimplifies
potentiallycompromisingmodelaccuracy. theconstructionofnormalpatterns.
3.2.MappingPhase
3.Methodology
AsshowninFigure3b,theprimarypurposeofthemapping
Thecorechallengeintimeseriesanomalydetection(TSAD)
phaseistotransformtheoriginaltimeseriessignalx ∈
liesinestablishingaccuratenormalpatternswhilemaintain- 0:i
RT into multiple new sets of values x ∈ RT×(N+N)
ingrobustnesstolocaldisturbances(Lietal.,2021). Tradi- 0:i
throughaseriesofunivariatefunctions. Here,T isthesize
tionalapproachesthatdirectlypredictbasedonhistorical
oftheslidingwindow. ThefirstN representsthenumber
data inevitably incorporate local noise into their learned
ofsineseriesunivariatefunctions,andtheotherN repre-
patterns. Buildingontheobservationthatnormalsequences
sentsthenumberofcosineseriesunivariatefunctions. The
exhibit greater smoothness than abnormal ones, we pro-
detailedcalculationmethodisshowninEquation(3). No-
poseKAN-AD,anovelanomalydetectionframeworkthat
tably, besides the univariate function terms, an A term
leverages this smoothing feature to identify anomalies in 0
representingtheaveragevaluewithintheslidingwindow
complextimeseriesdata.
isalsopresent,whichvariesacrossdifferentwindows. To
mitigatetheimpactoffluctuatingA oncoefficientfitting,
0
3.1.DesignofKAN-AD
aconstanttermeliminationmoduleisemployed.
The pipeline of KAN-ADconsists of three main stages:
ConstantTermElimination: InFourierseries,A repre-
0
mapping,reducing,andprojection. Inthemappingphase,
sentsthemeanvalueofthefunction. Althoughnormaliza-
we decompose the input time window into multiple uni-
tionensuresthattheentiretimeserieshasameanofzero,
variatefunctions. Thereducingphasethencombinesthese
individualtimewindowsmaystillexhibitsignificantfluctu-
functions through learned coefficients to reconstruct the
ationsintheirmeansduetothepresenceofatrend. These
“normal” pattern. Finally, the projection phase leverages
variationsintheconstanttermultimatelyaffectthemodel’s
this pattern to predict future behavior, enabling anomaly
accurateestimationofFouriercoefficients,leadingtobiases
detectionthroughcomparisonwithreal-timeobservations.
intheconstructionofthenormalpattern.
N
(cid:88) Tomitigatetheimpactofmeanfluctuationsonthemodel’s
f(x )=A + (A cos(nx )+B sin(nx ))+ϵ
0:i 0 n 0:i n 0:i approximationofnormaltimeseriespatterns,weemploy
n=1
first-order differencing during data preprocessing to min-
(cid:124) (cid:123)(cid:122) (cid:125)
g(x0:i) imize the residual trend component in the data and sub-
(3)
sequentlyrenormalizethedifferenceddata. Thisstrategy
3

---

# Page 4

KAN-AD:TimeSeriesAnomalyDetectionwithKolmogorov–ArnoldNetworks
KAN
learnable univariate functions
on edges
sum operations
on nodes
KAN-AD (ours)
fixed activation functions
on nodes
learnable weights
on edges
fixed univariate functions
on edges
(a)Illustrationoflearningcomponentsin (b) Illustration of the KAN-ADprocess using a sliding window approach. During the
KANandKAN-AD.KAN-ADlearnsthe mappingphase,rawtimewindowsaretransformedintomultipleunivariatefunctions.In
coefficients on edges with fixed univari- thereducingphase,aone-dimensionalconvolutionalkernellearnscoefficientsforthese
atefunctions,andperformsweightedsum univariatefunctions,aggregatingthemintoanormalpatternforthecurrenttimewindow.
operationsonnodes. Bluelinesindicate Intheprojectionphase,asingle-layerMLPpredictsfuturenormalpatterns.
edgeswithweights.
Figure3. IllustrationofKAN-AD.
allowsthemodeltofocusonestimatingFouriercoefficients Thefunctiondeconstruction(FD)mechanismaddressesthis
A andB ,therebyavoidingtheneedtolearnfrequently challengebytransformingthemodelingofnormalpatterns
1:n 1:n
changingconstantterms. Afterthisdifferentialstrategy,the intoaweightedcombinationofunivariatefunctions. This
normalpatternx′ canbeexpressedasx′ ∼Θ(x )×H transformationsubstantiallyreducesthemodel’sparameter
0:i 0:i 0:i
quantity-insteadofrequiringnumerousparametersforfine-
Periodic-EnhancedKAN-AD: FourierseriesoffiniteN
grainedfeaturemodeling,FDmechanismachievesefficient
termscannotmodelaperiodsmallerthan 1,whichlimits
N representation through estimating coefficients of a small
KAN-AD’sabilitytoexpresstimeseriescontainingmore
numberofunivariatefunctions.
subtleperiods.
Toaddressthislimitationandenhancethemodel’sability
tocaptureperiodicpatternsintimeseries,weintroducead- H(0)=Stack(X,S ,P ,...,S ,P ),∀n∈[1,...,N] (6)
1 1 n n
ditionalunivariatefunctionswithdifferentperiods. Specifi-
cally,weincorporatetrigonometriccomponentscos(2πni) H(l) =CNN(CNN(H(l−1))) ∀l∈[1,2,...,L] (7)
T
andsin(2πni)whereidenotesthewindowindex,withco- 2N 2
T (cid:88) (cid:88)
efficientslearnedthroughone-dimensionalconvolutionnet- Conv(H)= W c [m]·H c [i+m−1] (8)
works. Ourimplementationutilizesthreecomplementary c=1m=0
univariatefunctionsshowninEquation(5): therawtime CNN(H)=GELU(BN(Conv(H))) (9)
variableX,theFourierseriesS ,andthesine-cosinewave
n
P n . Thisintegrationofmulti-periodicunivariatefunctions Toeffectivelyestimatetheseunivariatefunctioncoefficients,
enhancesKAN-AD’scapacitytomodeltemporalpatterns. weemployastackedone-dimensionalconvolutionalneural
network(1DCNN).Thisarchitecturechoiceismotivated
X =x 0:i bytwokeyfactors: 1DCNNsexcelatsequencemodeling
S ={sin(nx ),cos(nx )} (5) throughtemporaldimensiontraversal,whiletheirconvolu-
n 0:i 0:i
2πni 2πni tional kernels naturally capture the diverse features intro-
P n ={sin( T ),cos( T )} duced by the FD mechanism. As shown in Equation (6),
KAN-ADfirstconstructsaunivariatefunctionmatrixH(0)
bycombiningtherequiredfunctionsforagiventimewin-
3.3.ReducingPhase
dow. Thismatrixisthenprocessedthroughmultiplestacked
Another challenge in real-world time series anomaly de- 1D convolutional layers with a kernel size of 3, progres-
tection is the high computational cost. Existing methods sivelyapproximatingthenormalpatternthroughcoefficient
often sacrifice efficiency for accuracy, making them im- learning, as expressed in Equation (7). Here, L denotes
practical in resource-constrained or large-scale settings. thenumberofCNNblocks,withthenetworkCNN(H)and
4

---

# Page 5

KAN-AD:TimeSeriesAnomalyDetectionwithKolmogorov–ArnoldNetworks
convolution operation Conv(H) defined in Equations (8)
Table1. DatasetStatistics.
and(9). TheconvolutionoperationinEquation(8)applies
Dataset Curves Train TrainAno% Test TestAno%
a kernel W to each channel H , where indices m and t
c c KPI 29 3,073,567 2.70% 3,073,556 1.85%
representpositionswithintheconvolutionalkernelandtime TODS 15 75,000 5.32% 75,000 6.38%
window,respectively. WSD 210 3,829,373 2.43% 3,829,537 0.76%
UCR 203 3,572,316 0.00% 7,782,539 0.47%
To ensure training stability and reduce internal covariate
shift,weapplybatchnormalization(Ioffe&Szegedy,2015) WSD(Zhangetal.,2022),andUCR(Wu&Keogh,2021).
aftereachconvolutionallayer(Equation(9)),followedby DatasetcharacteristicsaresummarizedinTable1,includ-
GaussianErrorLinearUnits(GELUs)(Hendrycks&Gim- ingcurvecounts, sizes, andanomalyrates. Theanomaly
pel, 2016) for activation. The final stage of the reducing intervallengthdistributions,showninFigure6,revealthat
phaseemploysaresidualconnection(Heetal.,2016)be- whilemostanomaliesspanlessthan10points,WSDand
tweenthehiddenstateH(L)andtheoriginalinputH(0)to
UCRcontainextendedanomalysegmentsexceeding300
maintainnumericalstability,asshowninEquation(10). Fi- points,enablingcomprehensiveevaluation. Detaileddataset
nally,a1-widthconvolutionalkernelreducesthedimension- descriptionsareprovidedinAppendixA.1.
alityofH(L)′ togeneratethenormalpatternapproximation
x′ 0:i withinthecurrenttimewindow: 4.1.2.MODELTRAININGANDINFERENCE
H(L)′ =H(L)+H(0) (10) Weimplementasystematicexperimentalprotocolforboth
x′ =GELU(BN(DownConv(H(L)′ )) (11) ourmethodandbaselineapproaches. Foreachtimeseries,
0:i
wetraindedicatedKAN-ADmodelsusingconsistenthyper-
Here,DownConv(H)= (cid:80)2N W ·H [i]denotesthecon- parameters: batchsize1024,learningrate0.01,andmaxi-
c=1 c c
volutionoperationforreducingdimensions. mum100epochs. Thevalidationstrategyvariesbydataset,
withUCRreserving20%oftrainingdataandotherdatasets
3.4.ProjectionPhase employinga4:1:5ratiofortraining,validation,andtesting
splits. Toensurefaircomparison,wefaithfullyreplicateall
Afterobtainingthecurrentwindow’snormalmodeapproxi- baselinemethodsfollowingtheiroriginalimplementations
mationx′ 0:i ,wepredictthefuturebehaviorx i+1 througha andhyperparametersettingsasspecifiedintheirrespective
single-layerMLP,leveragingKAN-AD’saccurateapproxi- papers. Duringinference,westandardizethebatchsizeto
mationcapability: 1acrossallmethodsforcomparableefficiencyassessment.
x =W ·x′ +b (12) ResultspresentedinTable2reportmeansandstandardde-
i+1 0:i
viationsfromfiveindependenttrialswithdifferentrandom
whereW andbdenotetheweightmatrixandbiastermof seeds.
thelinearlayer.
4.1.3.BASELINES
4.Evaluation
We conducted comparative experiments with ten state-
of-the-art time series anomaly detection methods: LST-
Inthissection,weconductcomprehensiveexperimentspri-
MAD (Malhotra et al., 2015), FCVAE (Wang et al.,
marilyaimedatansweringthefollowingresearchquestions.
2024),SRCNN(Renetal.,2019),FITS(Xuetal.,2024),
RQ1: How does KAN-ADcompare to state-of-the-art TimesNet (Wu et al., 2023), OFA (Zhou et al., 2023),
anomalydetectionmethodsinperformanceandefficiency? TranAD(Tulietal.,2022),SubLOF(Breunigetal.,2000),
RQ2: How sensitive is KAN-ADto hyperparameters? AnomalyTransformer(Xuetal.,2022)(abbreviatedasAn-
RQ3: How effective is each design choice in KAN-AD? oTransinthetables),KAN(Liuetal.,2025)andSAND(Bo-
RQ4: HowsensitiveisKAN-ADtoanomaliesinthetrain- nioletal.,2021).Detaileddescriptionsofthesemethodscan
ingdata? befoundinAppendixA.2. Fordatasetsnotfeaturedinthe
baselineliterature,wemeticulouslytunedhyperparameters
Inaddition,wealsoevaluateourmethodonamultivariate
viagridsearchtooptimizetheperformanceofthebaseline
time series anomaly detection dataset to demonstrate the
methodontherespectiveevaluationmetrics.
applicationpotentialofKAN-ADinmorescenarios.
4.1.4.EVALUATIONMETRICS
4.1.Experimentalsettings
In practical applications, operations teams are less con-
4.1.1.DATASET
cernedwithpoint-wiseanomalies(i.e.,whetherindividual
We evaluate KAN-ADon four publicly available UTS datapointsareclassifiedasanomalous)andmorefocused
datasets: KPI(Competition,2018),TODS(Laietal.,2021), ondetectingsustainedanomaloussegmentswithintimese-
5

---

# Page 6

KAN-AD:TimeSeriesAnomalyDetectionwithKolmogorov–ArnoldNetworks
Table2.Performancecomparison. Bestscoresarehighlightedinbold,andsecondbestscoresarehighlightedinboldandunderlined.
MetricsincludeF1(BestF1),F1 (EventF1),F1 (DelayF1),AUPRC(areaundertheprecision-recallcurve)andAvgF1 (averageF1
e d e e
scoreacrossfourdatasets).
KPI TODS WSD UCR
Method F1 F1 F1 AUPRC F1 F1 F1 AUPRC F1 F1 F1 AUPRC F1 F1 F1 AUPRC AvgF1 e
e d e d e d e d
SRCNN 0.4137 0.0994 0.2266 0.3355 0.6239 0.1918 0.4399 0.6076 0.4092 0.1185 0.1951 0.3080 0.5964 0.1369 0.1656 0.51090.1367
SAND 0.2710 0.0397 0.1097 0.2022 0.5372 0.1879 0.5103 0.5145 0.1761 0.0839 0.1267 0.1238 0.7044 0.5108 0.5116 0.65500.2056
AnoTrans 0.6103 0.3020 0.3623 0.5676 0.4875 0.1915 0.2918 0.4148 0.4348 0.2311 0.1517 0.3527 0.6135 0.1696 0.1084 0.54580.2236
TranAD 0.7553 0.5611 0.6399 0.7399 0.5035 0.2460 0.3619 0.4501 0.7570 0.6338 0.4158 0.7106 0.5278 0.1840 0.1554 0.45990.4062
SubLOF 0.7273 0.2805 0.4994 0.7015 0.7997 0.4795 0.7169 0.7809 0.8683 0.6585 0.4917 0.8353 0.8468 0.4772 0.4151 0.80010.4739
TimesNet 0.8022 0.6363 0.6995 0.8166 0.6232 0.3327 0.4495 0.6031 0.9406 0.8444 0.6170 0.9376 0.5273 0.1805 0.1439 0.45360.4985
FITS 0.9083 0.6353 0.8175 0.9359 0.7773 0.5416 0.6312 0.7725 0.9732 0.8391 0.6535 0.9771 0.6664 0.2926 0.2912 0.59690.5772
OFA 0.8810 0.6150 0.7952 0.9009 0.6928 0.5811 0.5588 0.7206 0.9564 0.8344 0.6250 0.9615 0.6294 0.3176 0.1503 0.56990.5870
FCVAE 0.9398 0.7556 0.8624 0.9572 0.8652 0.6995 0.7482 0.8798 0.9650 0.8610 0.6583 0.9653 0.7651 0.3812 0.2857 0.71450.6743
LSTMAD 0.9376 0.7742 0.8782 0.9624 0.8633 0.6981 0.7655 0.8740 0.9866 0.9028 0.6743 0.9849 0.7040 0.3482 0.3121 0.64320.6808
KAN 0.9411 0.7816 0.8666 0.9664 0.8109 0.6466 0.7518 0.8286 0.9879 0.8939 0.6650 0.9881 0.8016 0.4120 0.3971 0.74890.6835
0.9442 0.7989 0.8755 0.9693 0.9425 0.8940 0.8391 0.9716 0.9888 0.8927 0.6623 0.9868 0.8554 0.5335 0.5177 0.8188 0.7798
KAN-AD
±0.0007 ±0.0054 ±0.0024 ±0.0008 ±0.0040 ±0.0022 ±0.0055 ±0.0035 ±0.0005 ±0.0025 ±0.0022 ±0.0009 ±0.0040 ±0.0046 ±0.0042 ±0.0041
Ground Truth Anomaly point Table3. EfficiencycomparisononUCRdataset.
Detected Result
T
Fa
ru
ls
e
e
P
P
o
o
s
s
i
i
t
t
i
i
v
v
e
e Method GPUTime CPUTime Parameters F1 e
5-Delay PA
False Negative S
S
A
ub
N
L
D
OF
-
-
56
2
3
99
7s
s
-
-
0
0.
.
4
51
77
08
2
Point-wise PA OFA 220s 3087s 81.920M 0.3176
view as an event AnoTrans 201s 1152s 4.752M 0.1696
FCVAE 2327s 1743s 1.414M 0.3812
Event-wise PA
TimesNet 182s 259s 73,449 0.1805
LSTMAD 73s 267s 10,421 0.3482
Figure4.Illustration of the adjustment strategy. Point-wise PA KAN 66s 34s 1,360 0.4120
FITS 32s 17s 624 0.2926
givesaninflatedscorewhensomeanomalysegmentspersistfor
TranAD 113s 62s 369 0.1840
a long duration. Event-wise PA treats each anomaly segment KAN-AD 42s 36s 274 0.5335
asanevent, completelydisregardingthelengthoftheanomaly
segment.k-delayPAconsidersonlyanomaliesdetectedwithinthe
withresultssummarizedinTable2. Ouranalysisfocuses
firstkpointsaftertheanomalyonset,treatinganydetectedlateras
on three key dimensions: detection accuracy, model effi-
undetected.
ciency,andcomputationalrequirements. Acrossdiverseex-
riesdata. Furthermore,duetothepotentialimpactofsuch
perimentalsettings,KAN-ADdemonstratesconsistentand
segments,earlyidentificationiscrucial. Previouswork(Xu
robustperformanceadvantages.IntheTODSdataset,where
et al., 2018) proposed the Best F1 metric, which iterates
trainingdatacontainsasubstantialproportionofanomalies,
overallthresholdsandappliesapointadjustmentstrategy
KAN-ADsignificantlyoutperformsSOTAby27%onEvent
tocalculatetheF1score. However,ithasbeencriticizedfor
F1,highlightingitsrobustlearningcapabilitiesinhandling
performanceinflation(Laietal.,2021;Wu&Keogh,2021).
noisytrainingdata. Fordatasetsexhibitingstrongperiodic
Toaddressthis,wealsoadoptDelayF1(Renetal.,2019) characteristics (WSD and KPI), KAN-ADachieves com-
and Event F1. Delay F1 is similar to Best F1 but uses a parableorsuperiorperformancerelativetostate-of-the-art
delaypointadjustmentstrategy. AsshowninFigure4,the approaches. EveninthechallengingUCRdatasetscenario,
second anomaly was missed because the detection delay wherethetrainingsetlacksanomalysamplesandcontains
exceededthethresholdoffivetimeintervals. Inallexperi- significant periodic variations, KAN-ADeffectively cap-
ments,adelaythresholdoffivewasusedacrossalldatasets. turesnormalpatterns,whereasbaselinemethodsshowre-
Event F1, on the other hand, treats anomalies of varying ducedeffectivenessinpatternrecognition. Quantitatively,
lengths as anomalies with a length of 1, minimizing per- KAN-ADachieves more than a 15% improvement in av-
formanceinflationcausedbyexcessivelylonganomalous erageEventF1scorecomparedtoexistingstate-of-the-art
segments. For the sake of convenience, unless otherwise methods.
stated,weuseEventF1astheprimarymetric,asitismore
Thecomputationalefficiencyanalysis,presentedinTable3,
alignmentwiththeneedforreal-timeanomalydetectionin
revealsanotherdistinctiveadvantageofKAN-AD. Wenote
real-worldsituations.
thatseveralbaselinemethodsareexcludedfromthiscompar-
isonduetoimplementationconstraints: SAND’sCPU-only
4.2.RQ1. PerformanceandEfficiencyComparison
execution requirement and SubLOF’s limited multi-core
WepresentacomprehensiveevaluationofKAN-ADacross utilizationcapabilitiesprecludefaircomparisoninmodern
multipletimeseriesanomalydetection(TSAD)experiments, hardware acceleration contexts. Among the other mod-
6

---

# Page 7

KAN-AD:TimeSeriesAnomalyDetectionwithKolmogorov–ArnoldNetworks
Original Sample SubLOF FITS FCVAE
KAN TimesNet TranAD OFA
SAND AnomalyTransformer LSTMAD KAN-AD (ours)
Figure5.CasestudyonUCRInternalBleeding10.Theblackcurve
representstheoriginalsample,theredcurverepresentstheanomaly
scoresprovidedbythemethod,andthetrueanomalysegmentsare
highlightedinpink.
1.0
0.9
0.8
0.7
0.6 100 101 102 Anomaly Length
FDC
0.84
0.82
0.8
KPI
TODS 0.78
WSD
UCR 0.76 96 128
1 2 N 4 8 16 16 32 64 T
Figure6.Anomalous
lengthsdistribution.
CRPUA
tionsamongnormalsamplesacrosscyclesleadtoperiodic
falsealarmsduringnormalsegments,consistentwithour
observationsinFigure2. Amongthemethodslisted,while
OFA,LSTMAD,SubLOF,andFITScandetectanomalies,
their high anomaly scores during normal segments indi-
cate excessive sensitivity to minor fluctuations in normal
data. Incontrast,KAN-ADexcelsinidentifyinganomalies
whilemaintainingminimalanomalyscoresduringnormal
segments.
4.3.RQ2. Hyperparametersensitivity
TheKAN-ADmodelincorporatestwokeyhyperparameters:
thenumberoftermsinunivariatefunctionsN andthewin-
dowsizeT. Toinvestigatetheultimateimpactofthesepa-
rametersonmodelperformance,weconductedexperiments
ontheUCRdatasetwhileholdingallotherparameterscon-
stant. AsfindingssummarizedinFigure7,alargerwindow
size facilitates more accurate learning of normal patterns
whenN isfixed,leadingtoimprovedperformance. When
T isfixed,insufficientunivariatefunctionslimitKAN-AD’s
expressive power, while excessive N can lead to overfit-
ting. Overall,KAN-ADachieveditsbestperformancewith
T =96andN =2. Notably,evenwithsuboptimalhyper-
Figure7.Modelperformanceunder
parametersettingslikeT = 16andN = 1,wesurpassed
differenthyperparameters.
SOTAmethodsontheUCRdataset.
els, we observe a wide spectrum of model complexities,
withparametercountsrangingfrommillionstohundreds.
4.4.RQ3. AblationStudies
Large-scale models like OFA utilize 81.92M parameters,
whileestablishedapproachessuchasAnomalyTransformer, Inthissection,weinvestigatedtheimpactofconstantterm
FCAVE, and TimesNet employ between 73k and 4.75M elimination modules, different univariate function selec-
parameters. Incontrast,KAN-ADachievescompetitiveper- tions on algorithm performance and the influence of the
formance with remarkable efficiency, requiring only 274 functiondeconstructionmechanism.
parameters,a25%reductioncomparedtoTranAD,thenext
mostcompactmodelinourcomparison. 4.4.1.CONSTANTTERMELIMINATIONMODULE
These empirical findings underscore KAN-AD’s excep- We employed a constant term elimination (CTE) module
tionalefficiency-performanceinTSADtasks. Byachiev- duringdatapreprocessingtomitigatetheinfluenceofthe
ing state-of-the-art or near state-of-the-art performance offsettermA inEquation(3). Furtherexperimentswere
0
while significantly reducing the parameter footprint, conductedacrossalldatasetstoevaluatetheimpactofin-
KAN-ADdemonstratestheeffectivenessofourdesignprin- corporatingCTEwithinthepreprocessingpipeline. Aspre-
ciplesincreatingefficient, practicalsolutions. Thiscom- sentedinFigure8,theimpactofCTEvariesacrossdatasets,
binationofhighdetectionaccuracyandminimalcomputa- reflecting inherent data characteristics. For datasets with
tionalrequirementspositionsKAN-ADasanidealchoice pronounced periodicity or strong temporal stability (e.g.,
forresource-constrainedorcost-sensitivedeploymentsce- WSD),thebenefitsofCTEarelessapparent. Conversely,
narios,offeringacompellingbalancebetweenmodelcom- for datasets exhibiting larger value fluctuations or trends
plexityanddetectioncapabilities. (e.g., KPI, TODS and UCR), CTE yields significant im-
provements.
4.2.1.CASESTUDY
4.4.2.SELECTIONOFUNIVARIATEFUNCTIONS
We analyzed anomaly detection performance on UCR
datasetsamplestoillustratehowvariousmethodsrespondto To assess the impact of different univariate functions on
identicalanomalies,asshowninFigure5.Theselectedsam- modelperformance,weconductedexperimentsusingcom-
pledisplayedpatternanomalies,markedbysignificantdevi- mon univariate functions listed in Table 4. In our imple-
ationsfromtypicalbehavior. BothTranADandTimesNet mentations,duetovaryinginputrangerequirementsacross
exhibitdifficultyestablishingnormalpatterns. Minorvaria-
7

---

# Page 8

KAN-AD:TimeSeriesAnomalyDetectionwithKolmogorov–ArnoldNetworks
1.0
0.9
0.8
0.7
0.6
0.5
0.4
0.3 KPI TODS WSD UCR
Dataset
e1F
1.0
w/o CTE
w/ CTE 0.9
0.8
0.7
0.6
0.5
0.4
0.3 KPI TODS WSD UCR
Dataset
Figure8.Modelperformanceunder
differentpreprocessing.
e1F
0.9
Taylor Chebyshev I Chebyshev II Fourier(Ours)
0.8
0.7
0.6
0.5
0.4
0.3
0.2
0.1 10% 15% 20% 25% 30% 35% 40%
Ano in train
Figure9.Modelperformanceunder
differentunivariatefunction.
e1F
KAN-AD LSTMAD
TranAD FCVAE SRCNN KAN
TimesNet AnomalyTransformer
Figure10.Modelperformanceunder
differentanomalyratiosintraining.
Table4.Commonlyusedunivariatefunctionsfortimeseriesap- Table5.ModelperformanceonUCRdatasetunderdifferentfunc-
proximation. tiondeconstructionstrategies.
Name Φ (x) Variation F1 F1 AUPRC
n e d
TaylorSeries xn KAN-AD 0.5335 0.5177 0.8188
FourierSeries cos(nx)+sin(nx) w/oX 0.5153 0.4974 0.8066
ChebyshevPolynomialI cos(narccos(x)) w/oP 0.5081 0.4810 0.8007
ChebyshevPolynomialII sin((n+1)arccos(x)) w/oS 0.5056 0.5113 0.7998
sin(arccos(x)) w/oX&P 0.4737 0.4583 0.7872
w/oX&S 0.4698 0.4610 0.7767
w/oS&P 0.4561 0.4637 0.7595
univariatefunctions,appropriatenormalizationtechniques
areemployed. Specifically,min-maxscalingtotherange
4.6.Ablationonfunctiondeconstructionmechanism
x∈[−1,1]wasutilizedforbothtypesofChebyshevpoly-
nomials,whilez-scorewasemployedforTaylorseriesand To investigate the impact of the function deconstruction
Fourierseries. Theperformanceofallfourunivariatefunc- mechanism,wecomparedthemodel’sdetectioncapabilities
tionswascomparedusingthesameconfiguration.Asresults underdifferentunivariatefunctioncombinationstrategies.
presentedinFigure9,Fourierseriesconsistentlyachieved For clarity, the specific definitions are provided in Equa-
thetoptwoperformanceacrossalldatasets.Incontrast,Tay- tion (5). As the results presented in Table 5, the model’s
lorseriesexhibitedpersistentbiasduetonon-zerofunction detection performance exhibited a notable improvement
valuesinmostcases,hinderingoptimalmodelperformance. with an increasing number of univariate functions. Both
TheobjectiveofbothtypesofChebyshevpolynomialsis Fourierseriesandcosinewavesoutperformedtherawinput
to minimize the maximum error, which potentially con- data,likelyduetotheirsmootherrepresentationscompared
flictswithanomalydetectionmethodsthatminimizemean totheoriginalsignal, enablinghigherdetectionaccuracy.
squaredpredictionerror,thusleadingtosuboptimalperfor- The combination of different features, particularly those
mance. involvingFourierseriesandcosinewaves,resultedinsignif-
icantperformancegainsasthefeaturecountincreased. Ulti-
4.5.RQ4. RobustnesstoAnomalousData mately,KAN-ADachievedoptimaldetectionperformance
byintegratingallfeatures. Itisworthnotingthateventhe
ToevaluateKAN-AD’srobustnesstoanomaliesinthetrain-
variant of KAN-ADutilizing only the raw time series X
ingset,weconductedadditionalexperimentsusingsynthetic
outperformsKAN,clearlydemonstratingtheadvantageof
datasetsconstructedinaccordancewiththeTODSdataset
Fourierseriesovertheuseofsplinefunctionsforoptimizing
generation methodology. We synthesized test datasets
univariatefunctions.
containinglocalpeaksanddropsanomalies,andprogres-
sively increased the proportion of these anomalies in the
4.7.PerformanceonMultivariateTimeSeries
initially anomaly-free training set. As illustrated in Fig-
ure10,KAN-ADdemonstratesstableperformanceacross ToextendKAN-AD’sapplicationtothemultivariatetime
all anomaly ratios. Popular methods such as LSTMAD, series (MTS) scenario, we adopt a channel-independent
performwellatloweranomalyratiosbutexperienceasig- approach. Specifically, an MTS input with the shape
nificant decline as the ratio increases. Other approaches, (batch size, window length, n features)
like TranAD, fail to achieve optimal performance due to is reshaped into (batch size * n features,
overfittingtofine-grainedstructureswithinthetimeseries. window length). Eachofthen featureschannels
8

---

# Page 9

KAN-AD:TimeSeriesAnomalyDetectionwithKolmogorov–ArnoldNetworks
Table6.BestF1andparametercountsformultivariatetimeseriesanomalydetection. Bestandsecondbestresultsareinboldand
underline.
Methods SMD MSL SMAP SWaT PSM AvgF1 Parameters@MSL
Informer(Zhouetal.,2021) 0.8165 0.8406 0.6992 0.8143 0.7710 0.7883 504,174
AnomalyTransformer(Xuetal.,2022) 0.8549 0.8331 0.7118 0.8310 0.7940 0.8050 4,863,055
DLinear(Zengetal.,2023) 0.7710 0.8488 0.6926 0.8752 0.9355 0.8246 20,200
Autoformer(Wuetal.,2021) 0.8511 0.7905 0.7112 0.9274 0.9329 0.8426 325,431
FEDformer(Zhouetal.,2022) 0.8508 0.7857 0.7076 0.9319 0.9723 0.8497 1,119,982
TimesNet(Wuetal.,2023) 0.8462 0.8180 0.6950 0.9300 0.9738 0.8526 75,223
UniTS(Gaoetal.,2024) 0.8809 0.8346 0.8380 0.9326 0.9743 0.8921 8,066,376
KAN-AD(ours) 0.8429 0.8501 0.9450 0.9350 0.9650 0.9076 4,491
is thus treated as an independent univariate time series construction capabilities: TranAD (Tuli et al., 2022) em-
instance.KAN-ADisthenappliedtotheseindividualseries. ploysadversariallearningforrobustpatterncapture,while
Thischannel-independentstrategyhasproveneffective(Nie OFA(Zhouetal.,2023)leveragesGPT-2(Radfordetal.,
etal.,2023). Byadoptingasimilarprinciple,KAN-ADcan 2019)formodelingcomplextemporaldependencies.
leverageitsrobustunivariatemodelingcapabilitiesacross
Pattern Change Detection Methods: These approaches
allchannelsofanMTSdataset. Themodelistrainedonthe
identifyanomaliesthroughcomparativeanalysisofcurrent
collectionofthesereshapedunivariateinstances,allowing
andhistoricalpatterns. Earlymethods,likeSubLOF(Bre-
ittolearngeneralizednormalpatterns.
unigetal.,2000)quantifypatternvariationsusingwindow-
WeimplementedMTSversionsofKAN-ADinpopulartime based distance metrics. SAND employs temporal shape-
series library (THUML) and evaluated them on the com- basedclusteringtodistinguishanomalouspatterns. Recent
monSMD(Suetal.,2019),MSL(Hundmanetal.,2018a), advances,exemplifiedbyTriAD(Sunetal.,2024),leverage
SMAP(Hundmanetal.,2018b),SWaT(Mathur&Tippen- multi-domaincontrastivelearningframeworks,demonstrat-
hauer,2016),andPSM(Abdulaaletal.,2021)datasets. Our ingsuperiorperformanceonUCRdatasets.
evaluationmetricusestheBestF1scorewhichisconsistent
withthebaselinemethods. Weintroducethesedatasetsand
6.Conclusion
baselinemethodsindetailintheAppendixB.Asdetailed
inTable6,KAN-ADachievesthehighestaverageBestF1 Trainingtimeseriesanomalydetectionmodelswithdatasets
scoreof0.9076,acrossallfivebenchmarkdatasets,outper- containing anomalies is essential for deployment in pro-
formingalllistedSOTAmethods. Asignificantadvantage duction environments. Existing algorithms often rely on
ofKAN-ADisitsexceptionalparameterefficiency. With carefully selected features and complex architectures to
only4,491trainableparameters(measuredonMSL),KAN- achieve minor accuracy gains, neglecting robustness dur-
AD utilizes substantially fewer parameters than all other ing training. This paper introduces KAN-AD, a robust
comparedmethods. anomalydetectionmodelrootedintheKolmogorov–Arnold
representation theorem. KAN-ADtransforms the predic-
5.RelatedWork tion of time points into the estimation of coefficients of
Fourierseries,achievingstrongperformancewithfewpa-
TimeSeriesForecastingMethods: Thesemethodscanbe rameters,significantlyreducingcostswhileenhancingro-
categorizedintoprediction-basedandreconstruction-based bustness to outliers. KAN-ADincludes a constant term
methods, bothaiming toidentifydeviationsfromnormal elimination module to address temporal trends and lever-
patternsthroughtemporalanalysis. Prediction-basedmeth- agesfrequencydomaininformationforbetterperformance.
ods,likeFITS(Xuetal.,2024)achievesefficientdetection KAN-ADsurpasses the SOTA model across four public
through frequency domain analysis with minimal param- datasetswitha15%improvementinaverageEventF1score,
eters, while LSTMAD (Malhotra et al., 2015) leverages simultaneously achieving an 80% reduction in parameter
LSTMnetworks(Hochreiter&Schmidhuber,1997)tocap- countand50%fasterinferencespeedcomparedtovanilla
turecomplextemporaldependencies. Reconstruction-based KAN. With KAN-AD, a promising research direction is
approaches,likeDonut(Xuetal.,2018)focusontimese- to explore whether normal patterns in time series can be
riesdenoising,whileFCVAE(Wangetal.,2024)enhances representedmoreefficientlybyleveragingadditionaldata.
theVAE(Kingma&Welling,2022)frameworkbyincor-
poratingfrequencydomaininformation. Recentadvances
inTransformerarchitectureshavefurtherstrengthenedre-
9

---

# Page 10

KAN-AD:TimeSeriesAnomalyDetectionwithKolmogorov–ArnoldNetworks
Acknowledgments Hendrycks,D.andGimpel,K. Gaussianerrorlinearunits
(gelus). arXivpreprintarXiv:1606.08415,2016.
This work was partially funded by the National
Key Research and Development Program of China Hochreiter,S.andSchmidhuber,J.Longshort-termmemory.
(No.2022YFB2901800),theNationalNaturalScienceFoun- Neuralcomputation,9(8):1735–1780,1997.
dationofChina(62202445),theNationalNaturalScience
FoundationofChina-ResearchGrantsCouncil(RGC)Joint Hundman, K., Constantinou, V., Laporte, C., Colwell, I.,
ResearchScheme(62321166652),andtheNationalNatural andSoderstrom,T. Detectingspacecraftanomaliesus-
ScienceFoundationofChina(GrantNo. W2412136). inglstmsandnonparametricdynamicthresholding. In
Proceedings of the 24th ACM SIGKDD international
conference on knowledge discovery & data mining, pp.
ImpactStatement
387–395,2018a.
Thispaperpresentsworkwhosegoalistoadvancethefield
Hundman, K., Constantinou, V., Laporte, C., Colwell, I.,
of Machine Learning. There are many potential societal
andSoderstrom,T. Detectingspacecraftanomaliesus-
consequences of our work, none which we feel must be
inglstmsandnonparametricdynamicthresholding. In
specificallyhighlightedhere.
Proceedings of the 24th ACM SIGKDD international
conference on knowledge discovery & data mining, pp.
References
387–395,2018b.
Abdulaal, A., Liu, Z., and Lancewicki, T. Practical ap-
Ioffe,S.andSzegedy,C. Batchnormalization:Accelerating
proachtoasynchronousmultivariatetimeseriesanomaly
deepnetworktrainingbyreducinginternalcovariateshift.
detection and localization. In Proceedings of the 27th
InInternationalconferenceonmachinelearning,pp.448–
ACM SIGKDD conference on knowledge discovery &
456.pmlr,2015.
datamining,pp.2485–2494,2021.
Kieu,T.,Yang,B.,Guo,C.,Cirstea,R.-G.,Zhao,Y.,Song,
Bodner,A.D.,Tepsich,A.S.,Spolski,J.N.,andPourteau,
Y., and Jensen, C. S. Anomaly detection in time se-
S. Convolutional kolmogorov-arnold networks, 2024.
rieswithrobustvariationalquasi-recurrentautoencoders.
URLhttps://arxiv.org/abs/2406.13155.
In 2022 IEEE 38th International Conference on Data
Engineering(ICDE),pp.1342–1354.IEEE,2022.
Boniol, P., Paparrizos, J., Palpanas, T., and Franklin,
M. J. Sand: streaming subsequence anomaly detec- Kingma,D.P.andWelling,M. Auto-encodingvariational
tion. Proceedings of the VLDB Endowment, 14(10): bayes,2022.
1717–1729,2021.
Kolmogorov,A.N. Ontherepresentationsofcontinuous
Breunig,M.M.,Kriegel,H.-P.,Ng,R.T.,andSander,J.Lof: functionsofmanyvariablesbysuperpositionofcontinu-
identifyingdensity-basedlocaloutliers. InProceedings ousfunctionsofonevariableandaddition.InDokl.Akad.
ofthe2000ACMSIGMODinternationalconferenceon NaukUSSR,volume114,pp.953–956,1957.
Managementofdata,pp.93–104,2000.
Lai, K.-H., Zha, D., Xu, J., Zhao, Y., Wang, G., and
Competition,A. Kpidataset. https://github.com/ Hu, X. Revisiting time series outlier detection: Def-
iopsai/iops,2018. initions and benchmarks. In Thirty-fifth conference
on neural information processing systems datasets and
DeBoor,C. Apracticalguidetosplines. Springer-Verlag benchmarkstrack(round1),2021.
googleschola,2:4135–4195,1978.
Li,D.,Chen,D.,Jin,B.,Shi,L.,Goh,J.,andNg,S.-K.Mad-
Dym,H.andHP,M. Fourierseriesandintegrals. 1972. gan: Multivariateanomalydetectionfortimeseriesdata
with generative adversarial networks. In International
Gao,S.,Koker,T.,Queen,O.,Hartvigsen,T.,Tsiligkaridis, conference on artificial neural networks, pp. 703–716.
T., andZitnik, M. Units: Aunifiedmulti-tasktimese- Springer,2019.
riesmodel. AdvancesinNeuralInformationProcessing
Systems,37:140589–140631,2024. Li, Z., Zhao, Y., Han, J., Su, Y., Jiao, R., Wen, X., and
Pei,D. Multivariatetimeseriesanomalydetectionand
He,K.,Zhang,X.,Ren,S.,andSun,J. Deepresiduallearn- interpretationusinghierarchicalinter-metricandtemporal
ing for image recognition. In Proceedings of the IEEE embedding. InProceedingsofthe27thACMSIGKDD
conference on computer vision and pattern recognition, conference on knowledge discovery & data mining, pp.
pp.770–778,2016. 3220–3230,2021.
10

---

# Page 11

KAN-AD:TimeSeriesAnomalyDetectionwithKolmogorov–ArnoldNetworks
Liu, Z., Wang, Y., Vaidya, S., Ruehle, F., Halver- Szegedy, C., Liu, W., Jia, Y., Sermanet, P., Reed, S.,
son, J., Soljacˇic´, M., Hou, T. Y., and Tegmark, M. Anguelov,D.,Erhan,D.,Vanhoucke,V.,andRabinovich,
Kan: Kolmogorov-arnoldnetworks. In The Thirteenth A. Going deeper with convolutions. In Proceedings
International Conference on Learning Representations, of the IEEE conference on computer vision and pattern
2025. recognition,pp.1–9,2015.
Malhotra,P.,Vig,L.,Shroff,G.,Agarwal,P.,etal. Long THUML. thuml/time-series-library: Alibraryforadvanced
short term memory networks for anomaly detection in deep time series models. URL https://github.
timeseries. InEsann,volume2015,pp. 89,2015. com/thuml/Time-Series-Library.
Mathur,A.P.andTippenhauer,N.O. Swat: Awatertreat-
Tuli,S.,Casale,G.,andJennings,N.R. Tranad: deeptrans-
menttestbedforresearchandtrainingonicssecurity. In
former networks for anomaly detection in multivariate
2016internationalworkshoponcyber-physicalsystems
timeseriesdata. ProceedingsoftheVLDBEndowment,
forsmartwaternetworks(CySWater),pp.31–36.IEEE,
15(6):1201–1214,2022.
2016.
Wang, Y., Perry, M., Whitlock, D., and Sutherland, J. W.
Nie,Y.,H.Nguyen,N.,Sinthong,P.,andKalagnanam,J. A
Detectinganomaliesintimeseriesdatafromamanufac-
timeseriesisworth64words:Long-termforecastingwith
turingsystemusingrecurrentneuralnetworks. Journal
transformers. In International Conference on Learning
ofManufacturingSystems,62:823–834,2022.
Representations,2023.
Wang,Z.,Pei,C.,Ma,M.,Wang,X.,Li,Z.,Pei,D.,Raj-
Qu, X., Liu, Z., Wu, C. Q., Hou, A., Yin, X., and Chen,
mohan,S.,Zhang,D.,Lin,Q.,Zhang,H.,Li,J.,andXie,
Z. Mfgan: Multimodalfusionforindustrialanomalyde-
G. Revisitingvaeforunsupervisedtimeseriesanomaly
tectionusingattention-basedautoencoderandgenerative
detection: A frequency perspective. In Proceedings
adversarialnetwork. Sensors,24(2):637,2024.
of the ACM on Web Conference 2024, WWW ’24,
Radford, A., Wu, J., Child, R., Luan, D., Amodei, D., pp. 3096–3105, New York, NY, USA, 2024. Associa-
Sutskever,I.,etal. Languagemodelsareunsupervised tionforComputingMachinery. ISBN9798400701719.
multitasklearners. OpenAIblog,1(8):9,2019. doi: 10.1145/3589334.3645710. URLhttps://doi.
org/10.1145/3589334.3645710.
Ren, H., Xu, B., Wang, Y., Yi, C., Huang, C., Kou, X.,
Xing,T.,Yang,M.,Tong,J.,andZhang,Q. Time-series
Wu,H.,Xu,J.,Wang,J.,andLong,M. Autoformer: De-
anomalydetectionserviceatmicrosoft. InProceedings
compositiontransformerswithauto-correlationforlong-
of the 25th ACM SIGKDD international conference on
termseriesforecasting. AdvancesinNeuralInformation
knowledge discovery & data mining, pp. 3009–3017,
ProcessingSystems,34:22419–22430,2021.
2019.
Wu, H., Hu, T., Liu, Y., Zhou, H., Wang, J., and Long,
Siffer, A., Fouque, P.-A., Termier, A., and Largouet, C.
M. Timesnet: Temporal2d-variationmodelingforgen-
Anomalydetectioninstreamswithextremevaluetheory.
eraltimeseriesanalysis. InInternationalConferenceon
InProceedingsofthe23rdACMSIGKDDinternational
LearningRepresentations,2023.
conferenceonknowledgediscoveryanddatamining,pp.
1067–1075,2017.
Wu,R.andKeogh,E.J. Currenttimeseriesanomalydetec-
tionbenchmarksareflawedandarecreatingtheillusion
Stein, E. M. and Shakarchi, R. Fourier analysis: an
of progress. IEEE transactions on knowledge and data
introduction,volume1. PrincetonUniversityPress,2011.
engineering,35(3):2421–2429,2021.
Su, Y., Zhao, Y., Niu, C., Liu, R., Sun, W., and Pei,
D. Robust anomaly detection for multivariate time se- Xu,H.,Chen,W.,Zhao,N.,Li,Z.,Bu,J.,Li,Z.,Liu,Y.,
ries through stochastic recurrent neural network. In Zhao,Y.,Pei,D.,Feng,Y.,etal. Unsupervisedanomaly
Proceedings of the 25th ACM SIGKDD international detectionviavariationalauto-encoderforseasonalkpis
conference on knowledge discovery & data mining, pp. in web applications. In Proceedings of the 2018 world
2828–2837,2019. widewebconference,pp.187–196,2018.
Sun, Y., Pang, G., Ye, G., Chen, T., Hu, X., and Yin, H. Xu, J., Wu, H., Wang, J., and Long, M. Anomaly trans-
Unravelingtheanomaly’intimeseriesanomalydetection: former: Timeseriesanomalydetectionwithassociation
Aself-supervisedtri-domainsolution.In2024IEEE40th discrepancy. In International Conference on Learning
International Conference on Data Engineering (ICDE). Representations,2022.URLhttps://openreview.
IEEE,2024. net/forum?id=LzQQ89U1qm_.
11

---

# Page 12

KAN-AD:TimeSeriesAnomalyDetectionwithKolmogorov–ArnoldNetworks
Xu,Z.,Zeng,A.,andXu,Q.Fits:Modelingtimeserieswith
10kparameters.InInternationalConferenceonLearning
Representations(ICLR),2024.
Yu,R.,Yu,W.,andWang,X. Kanormlp: Afairercompar-
ison. arXivpreprintarXiv:2407.16674,2024.
Zeng,A.,Chen,M.,Zhang,L.,andXu,Q. Aretransform-
erseffectivefortimeseriesforecasting? InProceedings
of the AAAI conference on artificial intelligence, vol-
ume37,pp.11121–11128,2023.
Zhan, P., Wang, S., Wang, J., Qu, L., Wang, K., Hu, Y.,
andLi,X. Temporalanomalydetectiononiiot-enabled
manufacturing. JournalofIntelligentManufacturing,32:
1669–1678,2021.
Zhang, S., Zhong, Z., Li, D., Fan, Q., Sun, Y., Zhu, M.,
Zhang, Y., Pei, D., Sun, J., Liu, Y., et al. Efficient kpi
anomaly detection through transfer learning for large-
scalewebservices. IEEEJournalonSelectedAreasin
Communications,40(8):2440–2455,2022.
Zhou,H.,Zhang,S.,Peng,J.,Zhang,S.,Li,J.,Xiong,H.,
andZhang,W. Informer: Beyondefficienttransformer
forlongsequencetime-seriesforecasting.InProceedings
of the AAAI conference on artificial intelligence, vol-
ume35,pp.11106–11115,2021.
Zhou, T., Ma, Z., Wen, Q., Wang, X., Sun, L., and
Jin, R. Fedformer: Frequency enhanced decom-
posed transformer for long-term series forecasting. In
Internationalconferenceonmachinelearning,pp.27268–
27286.PMLR,2022.
Zhou, T., Niu, P., Sun, L., Jin, R., et al. One fits all:
Power general time series analysis by pretrained lm.
Advancesinneuralinformationprocessingsystems,36:
43322–43355,2023.
12

---

# Page 13

KAN-AD:TimeSeriesAnomalyDetectionwithKolmogorov–ArnoldNetworks
A.DatasetsandBaseliensonUnivariateTimeSeries
A.1.Datasets
Weselectedfourdatasetsfromdiversedomains,withsamplesoriginatingfrom:
• KPI(Competition,2018): ThisdatasetcomprisesservicemetricscollectedfromfivemajorInternetcompanies: Sogou,
eBay,Baidu,Tencent,andAlibaba. Thedatapointsareprimarilyrecordedevery1-2minutes,withsomesections
exhibitinga5-minuteinterval.
• TODS(Laietal.,2021): TODScomprisesartificiallycreatedtimeseries,eachdesignedtopresentspecifictypesof
anomalies. Itsexcellentinterpretabilityandcarefullyconstructeddatadistributionsmakeitsuitableforin-depthcase
studies.
• WSD (Zhang et al., 2022): This dataset consists of web server metrics collected from three companies providing
large-scalewebservices: Baidu,Sogou,andeBay.
• UCR(Wu&Keogh,2021): Thisarchivecontainsdatafrommultipledomainswithasingleanomaloussegmenton
eachtimeseries. Inadditiontorealanomalies,UCRalsoincludessyntheticbuthighlyplausibleanomalies.
A.2.Baselines
WeselectedthefollowingbaselineapproachestofurtherelaborateontheperformancedifferencesbetweenKAN-ADand
SOTAmethods:
• SubLOF(Breunigetal.,2000)representstraditionaloutlierdetectiontechniquesbasedondistancemetrics.
• SRCNN(Renetal.,2019)isasupervisedapproachreliantonhigh-qualitylabeleddata.
• LSTMAD(Malhotraetal.,2015)leveragesLongShort-TermMemory(LSTM)networks(Hochreiter&Schmidhuber,
1997)fordeeplearning-basedanomalydetection.
• FITS(Xuetal.,2024)achievesparameter-efficientanomalydetectionbyupsamplingfrequencydomaininformation
usingalow-passfilterandsimplelinearlayers.
• FCVAE(Wangetal.,2024)isunsupervisedreconstructionmethodbasedonVariationalAutoencoder(VAE)(Kingma
&Welling,2022),designedtoreconstructnormalpatterns.
• AnomalyTransformer(Xuetal.,2022)employsattentionmechanismtocomputertheassociationdiscrepancy.
• TranAD(Tulietal.,2022)incorporatestheprinciplesofadversariallearningtodevelopatrainingframeworkwithtwo
stageswhileintegratingthestrengthsofself-attentionencoderstocapturethetemporaldependencyembeddedinthe
timeseries.
• SAND(Bonioletal.,2021)utilizesanovelstatisticalapproachbasedoncurveshapeclusteringforanomalydetection
inastreamingfashion.
• TimesNet(Wuetal.,2023)leveragesanInception(Szegedyetal.,2015)-basedcomputervisionbackbonetoenhance
learningcapabilities.
• OFA(Zhouetal.,2023),withGPT-2(Radfordetal.,2019)asitsbackbone,improvesitsabilitytocapturepoint-to-point
dependencies.
• KAN(Liuetal.,2025)leveragesKolmogorov-Arnoldrepresentationtheorytodecomposecomplexlearningobjectives
intolinearcombinationsofunivariatefunctions.
Thesebaselinemethodsencompassavarietyofanomalydetectionparadigms: shape-basedSAND,subsequencedistance-
based SubLOF, Transformer-based approaches like OFA, TranAD, and Anomaly Transformer for modeling sequence
relationships,andfrequencydomaininformationenhancedmethodsFCVAEandFITS.
13

---

# Page 14

KAN-AD:TimeSeriesAnomalyDetectionwithKolmogorov–ArnoldNetworks
B.DatasetsandBaselinesonMultivariateTimeSeries
B.1.Datasets
WeevaluatedKAN-ADonfivewidely-usedpublicbenchmarkdatasetsformultivariatetimeseriesanomalydetection:
• SMD(Suetal.,2019): Adatasetcollectedfromalargeinternetcompany,containingdatafrommanyservermachines
overseveralweeks.
• MSL(Hundmanetal.,2018a): AdatasetfromNASAcontainingtelemetrydatafromtheMarsScienceLaboratory
rover.
• SMAP(Hundmanetal.,2018b): AnotherNASAdataset,containingtelemetrydatafromtheSMAPsatellite.
• SWaT(Mathur&Tippenhauer,2016): Adatasetgeneratedfromascaled-downreal-worldwatertreatmenttestbed,
includingnormalandattackscenarios.
• PSM(Abdulaaletal.,2021): AdatasetfromeBay,consistingofaggregatedmetricsfrommultipleapplicationservers.
B.2.Baselines
WeselectedthefollowingbaselineapproachestofurtherevaluateKAN-ADandSOTAmethodsonmultivariatetimeseries
datasets:
• Informer(Zhouetal.,2021):ATransformer-basedmodeldesignedforlongsequencetime-seriesforecasting,featuring
aProbSparseself-attentionmechanismtoimproveefficiency.Foranomalydetection,ittypicallyreliesonreconstruction
errororforecasterror.
• AnomalyTransformer(Xuetal.,2022): ATransformerarchitecturespecificallytailoredfortimeseriesanomaly
detection,whichaimstolearnprior-associationsandseries-associationstobetterdistinguishanomalies.
• DLinear (Zeng et al., 2023): A simple yet effective linear model that decomposes the time series into trend and
remaindercomponents,challengingthenecessityofcomplexTransformerarchitecturesforsomeforecastingtasksand
adaptableforanomalydetectionviareconstruction.
• Autoformer(Wuetal.,2021): ATransformermodelwithanoveldecompositionarchitectureandanAuto-Correlation
mechanism,designedtodiscoverseries-wiseconnectionsandimprovelong-termforecastingaccuracy.
• FEDformer(Zhouetal.,2022): ATransformervariantthatenhancesperformanceforlongsequenceforecastingby
employingfrequency-enhanceddecompositionandamixtureofexpertdesigninthefrequencydomain.
• TimesNet(Wuetal.,2023): Amodelthattransforms1Dtimeseriesintoasetof2Dtensorsbasedonidentifiedperiods
andappliesa2Dkernel(e.g.,Inceptionblock)tocapturebothintra-periodandinter-periodvariationsforgeneraltime
seriesanalysis.
• UniTS(Gaoetal.,2024): Aimstoprovideaunifiedframeworkfortimeseriesanalysis,oftenleveraginglarge-scale
pre-trainingondiversedatasetstobuildauniversalrepresentationforbothunivariateandmultivariatetimeseriestasks.
14