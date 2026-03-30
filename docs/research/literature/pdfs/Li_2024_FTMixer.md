FTMixer: Frequency and Time Domain Representations Fusion
for Time Series Forecasting
ZhengnanLi YunxiaoQin
lzhengnan389@gmail.com qinyunxiao@cuc.edu.cn
CommunicationUniversityofchina CommunicationUniversityofchina
China,Beijing China,Beijing
XilongCheng YutingTan
xilongcheng330@gmail.com YutingTan@cuc.edu.cn
CommunicationUniversityofchina CommunicationUniversityofchina
China,Beijing China,Beijing
Abstract 1 Introduction
Timeseriesdatacanberepresentedinboththetimeandfrequency Timeseriesforecastingfindswideapplicationacrossvariousdo-
domains,withthetimedomainemphasizinglocaldependencies mains,includingtrafficflows[40],ECLconsumption[16,36,46],
andthefrequencydomainhighlightingglobaldependencies.To andweatherforecasting[4,20,22,25].Inrecentyears,advance-
harnessthestrengthsofbothdomainsincapturinglocalandglobal mentsindeeplearninghaverevolutionizedtimeseriesforecasting
dependencies,weproposeanovelFrequencyandTimeDomain [24,26,31,44]..Amongtheseadvancements,Transformer-based
Mixer(FTMixer)method.Toexploittheglobalcharacteristicsof methods [22, 30, 40, 49, 53] and MLP-based methods [7, 12, 15,
thefrequencydomain,weintroduceanovelFrequencyChannel 35,48]dominatethisfield.Mostpreviousmethodshaveconcen-
Convolution(FCC)module,designedtocaptureglobalinter-series tratedonlearningtimeseriesinthetimedomainandhaveachieved
dependencies.Inspiredbythewindowingconceptinfrequency promisingperformance[32].
domaintransformations,wefurtherproposeanovelWindowed On the other hand,recent studies [6, 11, 18, 39, 50, 52] have
Frequency-TimeConvolution(WFTC)module,whichcaptureslo- demonstratedthat,undercertainconditions(e.g.,earlystopping
caldependenciesbyleveragingbothfrequencydomainrepresenta- orlargestepsize),deepneuralnetworks(DNNs)tendtogravitate
tionsobtainedfromwindowedtransformationsandtimedomain towardssimplersolutions.Thisphenomenon,knownasimplicit
representations.Notably,FTMixeremploystheDiscreteCosine sparseregularization[18,52],suggeststhatdeepregressionmodels
Transformation(DCT)withrealnumbersinsteadofthecomplex- focusonthemostinfluentialdatapointswithintheinputsequence
number-basedDiscreteFourierTransformation(DFT),enablingdi- forregressiontasks.
rectutilizationofmoderndeeplearningoperatorsinthefrequency Inthecontextoftimeseriesforecasting,whenthemodeloperat-
domain.Extensiveexperimentalresultsacrosssevenreal-world inginthetimedomain,theseinfluentialdatapointscorrespondto
long-termtimeseriesdatasetsdemonstratethesuperiorityofFT- specifictimeinstants,enablingthemodeltofocusonthecritical
Mixer,intermsofbothforecastingperformanceandcomputational momentsthataremostpredictiveoffuturevalues.Incontrast,when
efficiency.Codeisavaliablehere. operatinginthefrequencydomain,implicitsparseregularization
directsthemodel’sfocustowardsthemostsignificantfrequency
CCSConcepts components.Sinceeachfrequencycomponentrepresentsasinu-
•Mathematicsofcomputing→Timeseriesanalysis. soidinthetimedomain,thisfocusallowsthemodeltocapture
theprimaryperiodicitiesofthedata,therebypreservingessential
Keywords patternswhileeffectivelyfilteringoutnoise[45,47,53].Figure1(a)
showsthattheweightsofthefrequencydomainFullyConnected
Timeseriesforecasting
layerrevealprominentdiagonalpatterns,highlightingthemodel’s
ACMReferenceFormat: abilitytocaptureperiodicitybyfocusingonsignificantfrequen-
ZhengnanLi,YunxiaoQin,XilongCheng,andYutingTan.2018.FTMixer:
cies.Incontrast,thetimedomainFullyConnectedlayer’sweights
FrequencyandTimeDomainRepresentationsFusionforTimeSeriesFore-
mustmanagedataacrossperiodicintervalstoidentifyperiodic
casting.In.ACM,NewYork,NY,USA,12pages.https://doi.org/XXXXXXX.
patterns,resultinginmorecomplexandlesssparserepresentations.
XXXXXXX
ThisincreasedsparsityinthefrequencydomainenhancesDeep
Permissiontomakedigitalorhardcopiesofallorpartofthisworkforpersonalor NeuralNetwork(DNN)learningbyimprovingfeatureextraction
classroomuseisgrantedwithoutfeeprovidedthatcopiesarenotmadeordistributed
andreducingoverfitting[18,28].Figure1(b)furtherillustratesthat
forprofitorcommercialadvantageandthatcopiesbearthisnoticeandthefullcitation
onthefirstpage.Copyrightsforcomponentsofthisworkownedbyothersthanthe outputsfromthefrequencydomainaresmootherandcapturemore
author(s)mustbehonored.Abstractingwithcreditispermitted.Tocopyotherwise,or periodicinformation,whiletimedomainoutputsemphasizelocal
republish,topostonserversortoredistributetolists,requirespriorspecificpermission
and/orafee.Requestpermissionsfrompermissions@acm.org. dependencies.
Conference’17,July2017,Washington,DC,USA Severalstudieshaveleveragedthefrequencydomaintoana-
©2018Copyrightheldbytheowner/author(s).PublicationrightslicensedtoACM. lyzetimeseriesdata[9,38,43,45,47,53].Forexample,TSLA-Net
ACMISBN978-1-4503-XXXX-X/18/06
[9]employsfrequencydomainadaptivedenoisingtoenhancethe
https://doi.org/XXXXXXX.XXXXXXX
4202
guA
01
]GL.sc[
2v65251.5042:viXra

Conference’17,July2017,Washington,DC,USA ZhengnanLi,YunxiaoQin,XilongCheng,andYutingTan
0 4 8 21 61 02 42 82 23 63 04 44 84 25 65 06 46 86 27 67 08 48 88 29
0
4 8
12
16
20
24
28
32
36
40
44
48
52
56
60
64 68
72
76
80
84
88
92
0 4 8 21 61 02 42 82 23 63 04 44 84 25 65 06 46 86 27 67 08 48 88 29
0
4 8 GroundTruth
12 Time Domain
16 Frequency Domain
20 0.4
24
28
32
36
40
44 0.6
48
52
56
60
6 6 4 8 0.8
72
76
80
84
88 1.0
92
0 25 50 75 100 125 150 175 200
Left: Frequency Domain Right: Time Domain Predictions
(a) (b)
Figure1:(a)VisualizationsoftheFullyConnected(FC)layerweightslearnedinthetimeandfrequencydomainsontheETTh1
dataset,withboththeinputandoutputlengthequalto96,resultingina96×96weightmatrix(𝑦-axis:theoutput,𝑥-axis:the
input).NotethatwetrainthefrequencydomainFClayerbyemployingtheDiscreteCosineTransform(DCT).FromtheFC
layerweightvisualizations,wecanseethatlearninginthefrequencydomainidentifiesclearerdiagonaldependenciesand
keypatternsthaninthetimedomain.(b)PredictionsofthefrequencydomainFClayerandthetimedomainFClayer.The
frequencydomainoutputissmootherandemphasizesperiodicinformationwithsmallerMSE=0.379,whilethetimedomain
outputcapturesmorelocaldependencieswithlargerMSE=0.383.
model’scapabilitytoidentifylong-termperiodicpatternsandim- Additionaly,tocaptureinter-seriesglobaldependencies,wepro-
provecomputationalefficiency.Similarly,TimesNet[41]utilizesthe poseanovelFrequencyChannelConvolution(FCC)module.The
FastFourierTransform(FFT)todetectperiodicitiesintimeseries FCCembedstheentiresequenceinthefrequencydomainbefore
dataandperformsconvolutionbasedontheseidentifiedperiodic performingconvolution,allowingforacomprehensiveanalysis
components. ofglobalpatterns.Toenhancethecaptureoflocaldependencies,
Despiteadvancementsinleveragingthefrequencydomainfor wedrawinspirationfromthewindowedDiscreteFourierTrans-
timeseriesanalysis,twomajorchallengesstillremain:1)Han- form (DFT) [34, 42] and introduce Windowed Frequency-Time
dling Complex Number Representations. Existing methods Convolution(WFTC)module.TheWFTCsegmentsthetimeseries
oftenrelyontheDiscreteFourierTransform(DFT)[41,43,53], intopatchesofvaryingscales,appliesfrequencydomaintransfor-
whichintroducescomplexrepresentationsoftimeseriesdata.Deep mationswithineachpatch,andthenperformsconvolutionacross
learningtechniquessuchasBatchNormalization[14]andactiva- thesepatchestoeffectivelycapturelocalvariations.Afterextract-
tionfunctions[10]arenotwell-suitedforthesecomplexnumbers. ingfrequencydomainrepresentations,wetransformthembackto
Althoughitispossibletoprocesstherealandimaginarypartssep- thetimedomainandintegratethemwiththeresultsoftheconvolu-
aratelywithdistinctmodelstoadaptcomplexnumberstodeep tionperformeddirectlyinthetimedomainonthepatches.Weuse
learningtechniques,thisapproachincreasesthenumberofparame- Depth-WiseSeparableConvolutiontoprocessfeaturesextractedby
tersandcomputationalcomplexity,andmayperformnotwell.The WFTC,balancingefficiencywithperformance.Theoutputsofthe
experimentalresultinTable5demonstratetheunsatisfactoryper- Depth-WiseSeparableConvolutionandFCCareaddedtogetherand
formanceofthisapproach.2)LossofLocalinformation.Global passedthroughaprojectionlayertoyieldthefinalmodeloutput.
frequencydomaintransformationsmainlycaptureglobaldependen- Moreover,weproposetheDual-DomainLossFunction(DDLF),
cies,potentiallymaskingcriticalvariationsandphenomena,such whichcomputeslossesseparatelyinthetimeandfrequencydo-
assuddenspikesandirregularpatterns[8,13,33,34,42],whichare mains.LeveragingtheDCT’sabilitytoconcentrateenergyinto
essentialforaccuratepredictionsandunderstandingtimeseries fewercoefficientsandoperatewithrealnumbers,thislossfunction
dynamics[27]. improvesthemodel’sabilitytocaptureandutilizedomain-specific
Toaddressaforementionedchallenges,weproposeamethodthat featureseffectively.
effectivelycombinesinsightsfromboththetimedomainandthe
frequencydomain:FrequencyandTimedomainMixer(FTMixer).
First,tofullyutilizethefrequencydomainwithdeeplearningmod- Contribution. Inthiswork,weexplorethepotentialofinte-
els,weemploytheDiscreteCosineTransformation(DCT)[2].Un- gratingtimeandfrequencydomainsfortimeseriesforecastingand
liketheDiscreteFourierTransform(DFT)[2,34],whichinvolves proposeanovelapproach,FTMixer.WeincorporatetheDiscreteCo-
complexnumbers,theDCToperatesexclusivelyonrealnumbers, sineTransform(DCT)intotimeseriesforecastingandintroducethe
makingitmorecompatiblewithmoderndeeplearningtechniques. FrequencyCaptureConvolution(FCC)moduletocaptureglobalde-
pendencies.InspiredbywindowedDCT,weproposetheWindowed

FTMixer:FrequencyandTimeDomainRepresentationsFusionforTimeSeriesForecasting Conference’17,July2017,Washington,DC,USA
Frequency-TimeConvolution(WFTC)moduletocapturelocalde- traditionaldeeplearningtechniqueslikeactivationfunctionsand
pendenciesacrossbothtimeandfrequencydomains.Additionally, batchnormalizationoncomplexnumberdata(usedintheDFT)
weintroducetheDual-DomainLossFunction(DDLF)toleverage remainsuncertain.
thestrengthsofbothdomains.Extensiveexperimentsacrossseven ThisworkaddressestheselimitationsbyintroducingtheDiscrete
datasetsdemonstratethatFTMixeroutperformsstate-of-the-art CosineTransform(DCT)forthefirsttimeintimeseriesanalysis.
methods. ComparedtotheDiscreteFourierTransform(DFT)[2],DCTop-
eratesexclusivelyonrealnumbers,makingitmoresuitablefor
2 RelatedWork moderndeeplearningtechniques.Furthermore,DCTutilizesonly
amplitudetorepresentthefrequencydomaininformation,simpli-
2.1 TimeSeriesForecasting
fyingthecomputationofthelossfunctioninthefrequencydomain.
Time series forecasting plays a crucial role in various domains,
TheseadvantagesofDCTpavethewayforanovelandpotentially
includingfinance,publichealth,andweatherforecasting[40].Re-
moreeffectiveapproachtofrequency-awaretimeseriesforecasting.
cent years have witnessed significant development in this field
drivenbydeeplearningmodelsspecificallydesignedfortimeseries 2.3 ImplicitSparseRegulariation
tasks.Amongthesemodels,threeprominentarchitectureshave
Recentstudies[11,18,39,50,52]haveshownthat,underspecific
garneredconsiderableattention:Multi-LayerPerceptrons(MLPs),
conditions such as early stopping or large step sizes, deep neu-
Transformers,andTemporalConvolutionalNetworks(TCNs).
ralnetworks(DNNs)naturallyevolvetowardssimplersolutions.
Inspiredbytheirsuccessinnaturallanguageprocessing,Trans-
Specifically,[50]showsthatwhengradientdescentisapplieddi-
formershavebeenadaptedfortimeseriesanalysiswithremark-
rectlytotheresidualsumofsquareswithsufficientlysmallinitial
ableresults(e.g.,[17],[29],[45]).ExamplesincludeAutoformer
values,andproperearlystoppingrulesareemployed,theiterates
[40],whichutilizesattentionmechanismstodecomposesequences,
convergetoanearlysparse,rate-optimalsolutionthatoftensur-
PatchTST[30]whichsegmentssequencesinspiredbytheVision
passesexplicitlyregularizedapproaches.Similarly,[18]provesthat
Transformer (ViT) architecture, and iTransformer [22] that em-
earlystoppingtendstoleadmodelstowardssparsersolutions.Ad-
bedstheentiresequencethencomputingattentionacrosschannel
ditionally,[6]demonstratesthatifanexactsolutionexists,vanilla
dimensions.
gradientflowfortheoverparameterizedlossfunctionalconverges
Knownfortheirsimplicityandeffectiveness,MLPshavealso
foundapplicationintimeseriesanalysis(e.g.,[15],[23],[35],[19],
toagoodapproximationofthesolutionwithminimalℓ 1-norm.
[48],[43],[7],[3]).DLinear[48],forinstance,performstrend-season
3 Methodology
decompositionandlearnsusingtwoMLPs.RLinear[15]implements
reversible instance norm and achieves impressive performance. 3.1 Prelimiary
Additionally,FITS[43]directlylearnsinthefrequencydomain, 3.1.1 ProblemDefinition. Let[𝑋 1 ,𝑋 2 ,···,𝑋 𝑇] ∈R𝑁×𝑇 standfor
leadingtosurprisingresults. theregularlysampledmulti-channeltimeseriesdatasetwith𝑁
TemporalConvolutionalNetworks(TCNs)areanotherclassof seriesand𝑇 timestamps,where𝑋 𝑡 ∈R𝑁 denotesthemulti-channel
deeplearningmodelsexcellingatcapturinglocaldependencies
values of 𝑁 distinct series at timestamp 𝑡. We consider a time
withintimeseriesdata(e.g.,[4],[41],[37],[26]).TimesNet[41]
serieslookbackwindowoflength-𝐿 ateachtimestamp𝑡 asthe
u
ag
ti
i
l
n
iz
g
e
F
s
a
C
s
N
tF
N
ou
fo
r
r
ie
f
r
ea
T
t
r
u
a
r
n
e
s
e
fo
x
r
t
m
rac
(
t
F
i
F
o
T
n,
)
w
fo
i
r
th
pe
a
r
p
io
a
d
rt
ic
ic
it
u
y
la
e
r
x
f
t
o
r
c
a
u
ct
s
io
o
n
n
.
l
M
ev
o
e
d
r
-
- modelinput,namelyX𝑡 = [𝑋 𝑡−𝐿+1 ,𝑋 𝑡−𝐿+2 ,···,𝑋 𝑡] ∈R𝑁×𝐿 ;also,
weconsiderahorizonwindowoflength-𝜏 attimestamp𝑡 asthe
e
se
rn
ri
T
e
C
s
N
an
[
d
26
c
]
r
,
o
d
s
r
s
a
-
w
tim
in
e
gi
i
n
n
s
fo
p
r
ir
m
at
a
i
t
o
i
n
on
fro
si
m
m
t
u
r
l
a
t
n
a
s
n
f
e
o
o
rm
us
e
l
r
y
s
.
,
C
ca
o
p
n
t
v
u
T
re
im
si
e
n
N
te
e
r
t
- predictiontarget,denotedasY𝑡 = [𝑋 𝑡+1 ,𝑋 𝑡+2 ,···,𝑋 𝑡+𝜏] ∈R𝑁×𝜏 .
Thenthetimeseriesforecastingformulationistousehistorical
[4]proposesanovelpatchmethodtodeterminethesuitablelength
observations X𝑡 to predict future values Y𝑡. For simplicity, we
o ti f m th e e se p r a i t e c s h d w at in as d e o t w s. ,enhancingtheadaptabilityofTCNstovarious shortenthemodelinputX𝑡 asX= [𝑋 1 ,𝑋 2 ,···,𝑋 𝐿] ∈R𝑁×𝐿 and
reformulatethepredictiontargetasY= [𝑋 𝐿+1 ,𝑋 𝐿+2 ,···,𝑋 𝐿+𝜏] ∈
R𝑁×𝜏
,intherestofthepaper.
2.2 Frequency-AwareTimeSeriesForecasting
Severalsuccessfulapproacheshavedemonstratedthevalueofin- 3.1.2 DiscreteCosineTransformation. Ourmethodologyutilizes
corporatingfrequencydomaininformation.TSLA-Net[9]employs theDiscreteCosineTransform(DCT)toconvertinputdatainto
frequencydomainadaptivedenoisingtoenhancethemodel’scapa- thefrequencydomain.Thissectionprovidesanoverviewofthe
bilitytoidentifylong-termperiodicpatternsandimprovecomputa- DCTanditsrelationshiptotheDiscreteFourierTransform(DFT).
tionalefficiency.Similarly,TimesNet[41]utilizestheFastFourier The Cosine Transform is a variant of the Fourier Transform
Transform(FFT)todetectperiodicitiesintimeseriesdataandper- thatfocusesexclusivelyonthecosinecomponents[1].Itisparticu-
formsconvolutionbasedontheseidentifiedperiodiccomponents. larlyadvantageousforfunctionswithsymmetry,simplifyingthe
FreTS[47]forecaststimeseriesbyleveragingbothinner-series transformationprocesscomparedtotheFourierTransform,which
andinter-seriesinformation.Ontheotherhand,FITS[43]achieves includesbothsineandcosinecomponents.
improvedperformancebytrainingsequencesdirectlyinthefre-
ThecontinuousFourierTransformofafunction𝑓(𝑡)isgiven
quencydomainusingafullyconnectedlayer.However,asingle by:
linearmodeloftenprovesinsufficientforcapturingnon-linearpat- 𝐹(𝜔)= ∫ ∞ 𝑓(𝑡)𝑒−𝑖𝜔𝑡𝑑𝑡,
ternsinthefrequencydomain.Additionally,theeffectivenessof
−∞

Conference’17,July2017,Washington,DC,USA ZhengnanLi,YunxiaoQin,XilongCheng,andYutingTan
where𝐹(𝜔)representsthefrequencydomainrepresentationof𝑓(𝑡). Here,Yˆ denotesthemodel’soutput,andXrepresentstheinput
Forevenfunctions𝑓 𝑒(𝑡),theFourierTransformcanbeexpressed timeseries.𝑓 WFTCappliestheWFTCmoduletoeachchannelofX,
purelyintermsofcosinefunctions: with𝑓 DSand𝑓 Prerepresentingdepth-wiseseparableconvolution
∫ ∞ (DS-Conv)andthemodelpredictor,respectively.
𝐹(𝜔)= 𝑓 𝑒(𝑡)cos(𝜔𝑡)𝑑𝑡.
−∞ 3.3 FrequencyChannelConvolution
Thisrelationshiphighlightstheefficiencyofcosinecomponents
TheFCCmoduleisdesignedtocaptureglobalinter-seriesdepen-
forsymmetricfunctions.Weformalizethisconnectionbetween
denciesinthefrequencydomain.Standardconvolutiontendstoem-
the Discrete Cosine Transform (DCT) and the Discrete Fourier
phasizelocaldependencies,whichusuallyoverlookbroader,global
Transform(DFT)withthefollowingtheorem:
patternsduetoitsinherentfocusonlocalfeatures.Toaddressthis
TheDiscreteCosineTransform(DCT)ofasequencecanbede-
limitation,weapplytheDiscreteCosineTransform(DCT)toeach
rivedfromtheDiscreteFourierTransform(DFT)ofasymmetrically
channeloftheinputsequence,convertingitintothefrequency
extendedversionofthesequence[1].TheDCTforasequencexof
domain,whichcanbeformulatedas:
length𝐿isdefinedas:
X𝑓 =Embedding(DCT(X)) (4)
𝐿
∑︁
−1 (cid:18)𝜋 (cid:18)
1
(cid:19) (cid:19)
𝑥¯𝑘 =
𝑛=0
𝑥 𝑛cos
𝐿
𝑛+
2
𝑘 , (1) X
Th
𝑓
e
r
D
ep
is
r
c
e
r
s
e
e
t
n
e
t
C
s
o
th
s
e
in
f
e
re
T
q
r
u
a
e
n
n
sf
c
o
y
rm
do
(
m
D
a
C
in
T)
re
is
p
a
re
p
s
p
e
l
n
ie
t
d
at
t
i
o
on
th
o
e
f
i
t
n
h
p
e
u
i
t
n
X
p
,
u
a
t
n
X
d
.
where𝑥 𝑛isthe𝑛-thelementofthesequencex,and𝑥¯𝑘denotesthe𝑘- theresultingfrequencydomainrepresentationisthenembedded
alongthesequencedimension.Followingthistransformation,we
thfrequencycomponentintheDCTfrequencydomaincoefficients,
with𝑘 ∈{0,1,...,𝐿−1}. performconvolutionwithkernelsizesequaltothevariabledimen-
UsingEq.1,weobtainx¯ = [𝑥¯0 ,𝑥¯1 ,...,𝑥¯𝐿−1 ],representingthe sions,effectivelyallowingconvolutionacrosstheentirevariable
dimension.
frequencyfeaturesofx.
TheDCTisreversible,allowingthetransformationoffrequency
domaincoefficientsbacktothetimedomainthroughtheinverse
ZFCC =iDCT(Linear(Conv1d(X𝑓))) (5)
DiscreteCosineTransform(iDCT): This approach allows the FCC module to effectively capture
globaldependenciesandperiodicpatterns,enhancingthemodel’s
1
𝐿
∑︁
−1 (cid:18)𝜋 (cid:18)
1
(cid:19) (cid:19)
abilitytounderstandlong-termtrendsintimeseriesdata.
𝑥 𝑛 =
2
𝑥¯0 + 𝑥¯𝑘cos
𝐿
𝑘+
2
𝑛 . (2)
𝑘=1
3.4 WindowedFrequency-TimeConvolution
ByemployingtheDCT,ourmethodologyeffectivelytransitions
Existingfrequency-domainmodelsoftenconcentratesolelyonthe
inputdataintothefrequencydomain.TheDCT,renownedinsignal
globalfrequencyrepresentationofentiresequences,whichmay
processing,emphasizescosinecomponentsandoperatesefficiently
resultinsimilarrepresentationsfordistincttime-domainsequences.
withrealnumbers,makingitwell-suitedforintegrationwithdeep
Inspiredbythewindowingtechniqueinfrequencydomaintrans-
learningframeworks.
formations[27,33],weproposetheWindowedFrequency-Time
Convolution(WFTC)moduletocapturefine-grainedinformation
3.2 OverallArchitecture
byapplyingtheDiscreteCosineTransform(DCT)withinmulti-
Toaddressthechallengeofcapturingbothlocalandglobalpatterns scalewindows.
intimeseriesdata,weintroducetheFrequencyandTimedomain IntheWFTCmodule,asillustratedinFigure2,eachchannelof
Mixer(FTMixer)method.AsshowninFigure2,FTMixerincorpo- theinputsequenceisinitiallysegmentedintopatchesofvarious
ratestwokeymodules:FrequencyChannelConvolution(FCC)and scales.TheDCTisthenappliedwithineachpatchtoderivethelocal
WindowedFrequency-TimeConvolution(WFTC). frequencydomainrepresentation.Tocapturelocaldependencies,
TheFCCmoduleisdesignedtocaptureinter-seriesdependencies weperformconvolutiononthesepatches.Subsequently,wetrans-
inthefrequencydomain,enhancingthemodel’sabilitytodetect formthefrequencydomainembeddingsbacktothetimedomain
globalpatternsthatmaybemissedinthetimedomain.Meanwhile, andaddthemtotheresultoftheconvolutionperformeddirectly
theWFTCmoduleemploysmulti-scalewindowingtocapturede- inthetimedomainonthepatches.Thisapproachenhancesthe
tailed local frequency information, addressing the limitation of model’sabilitytocapturelocaldependencies.Theoverallprocess
traditionalmethodsthatrelysolelyonglobalfrequencyrepresen- canbeformulatedas:
t
f
a
ea
ti T
t
o
u
h n
r
e s
e
s . e
ex
c
t
o
r
m
ac
p
ti
o
o
n
n
e
,
n
im
ts
p
w
ro
o
v
r
i
k
ng
to
o
g
v
e
e
th
ra
e
l
r
l
t
p
o
er
b
f
a
o
l
r
a
m
nc
a
e
nc
lo
e
c
i
a
n
l
t
a
i
n
m
d
e
g
s
l
e
o
r
b
ie
a
s
l  F
Z
P
P
𝑗
𝑗
=
=
i
F
D
P
C
𝑗
T
+
(cid:0)
C
C
o
o
n
n
v
v
(
(
P
D
𝑗
C
)
T(P𝑗))(cid:1),
(6)
for
T
ec
h
a
e
st
m
in
o
g
d
.
elstructureofFTMixerissummarizedasfollows:


Z
Z
˜ P
W
𝑗
F
=
TC
E
=
mb
C
e
o
d
n
d
c
i
a
n
t
g
e
(
(
Z
Z˜
P
P
𝑗
1
)
,Z˜ P2 ,...,Z˜ P𝑛 ),
whereP𝑗 denotesthe𝑗-thpatch(e.g.,P1orP2inFigure2)inthe
 Z
Z
F
D
C
S
C
=
=
𝑓 D
𝑓 F
S
C
(
C
C
(
o
X
n
)
c
,
ate(𝑓 WFTC (X)), (3)
W
pa
F
tc
T
h
C
fo
m
ll
o
o
d
w
u
i
l
n
e
g
.Z
th
P
e
𝑗
e
r
m
ep
b
r
e
e
d
se
d
n
in
t
g
st
l
h
ay
e
e
f
r
e
,
a
w
tu
h
r
e
e
r
s
e
e
e
x
m
tr
b
a
e
c
d
t
d
ed
in
f
g
o
i
r
s
t
a
h
p
e
p
𝑗
li
-
e
th
d

Y
Z
ˆ =
=Z
𝑓 P
F
r
C
e
C
(Z
+
),
ZDS , a
to
lo
a
n
f
g
ee
th
d
e
-fo
se
rw
qu
a
e
r
n
d
c
l
e
ay
d
e
i
r
m
.Z
en
W
s
F
io
T
n
C
o
is
f
t
e
h
a
e
ch
ou
p
t
a
p
t
u
c
t
h
o
i
f
n
th
a
e
m
W
an
FT
ne
C
r
m
si
o
m
d
i
u
la
le
r


FTMixer:FrequencyandTimeDomainRepresentationsFusionforTimeSeriesForecasting Conference’17,July2017,Washington,DC,USA
sequence
channel
spectrum
channel
DCT
DCT
DCT
DCT
Conv Linear iDCT
WFTCModule
WFTC Module
WFTC Module
WFTC Module
DS
Conv
feature
DCT Conv iDCT
DCT Conv iDCT
channel
feature
channel
Predictor Prediction
L
Windowing patch P1
P2
Embedding
Embedding
Concat
𝐗𝐗
FCC module
𝐘𝐘 Concat
𝐙𝐙FCC
+
𝐙𝐙
𝐙𝐙DS
+
𝐙𝐙P1
Conv
𝐙𝐙𝑊𝑊𝑊𝑊𝑊𝑊𝑊𝑊
+
𝐙𝐙P2
Conv
Figure2:TheframeworkofFTMixer.FTMixercomprisestwomainmodules:FCCandWFTC.AnexampleXcontainingfour
channelsisvisualizedhereforeasierunderstanding.ThemodelpredictorisaLinearlayer.
forthecurrentinputchannel.Notethatweseparatelyapplythe Where𝐹(𝑋)representsthepredictionofthemodel.
WFTCmoduleoneachinputchannel,whichisshowninFigure2.
4 Experiment
3.5 Depth-WiseSeparableConvolution 4.1 ExperimentSettings
AfterobtainZWFTCforallinputchannel,wefirstconcatethemand Inthissection,weevaluatetheefficacyofFTMixerontimese-
thenapplyDepth-WiseSeparableConvolution(DSConvolution) riesforecasting,andanomalydetectiontasks.Weshowthatour
[5],tofurtherprocesstheobtainedfeature.DSConvolutiondecou- FTMixercanserveasafoundationmodelwithcompetitiveperfor-
plesthelearningofintra-patchdimensionsfromthelearningof manceonthesetasks.
inter-patchdimensions.Itismorecomputationallyefficientthan
vanillaconvolutionandcomprisestwocomponents:Depth-Wise
Table1:TheStatisticsofthesevendatasetsusedinourex-
Convolution(DWConv)andPoint-WiseConvolution(PWConv).
periments.
DWConvaggregatesinter-patchinformationthroughgroupedcon-
volution,whilePWConvoperatesakintoaFeedForwardNetwork Datasets ETTh1&2 ETTm1&2 Traffic ECL Weather
(FFN)toextractintra-patchinformation.
Channels 7 7 862 321 21
Timesteps 17,420 69,680 17,544 26,304 52,696
3.6 Dual-DomainLossFunction
Granularity 1hour 5min 1hour 1hour 10min
Tofullyleveragetheadvantagesofboththefrequencyandtime
domains,weproposeaDual-DomainLossFunction(DDLF)that
computeslossesseparatelyineachdomain.Forthetimedomain,we
Datasets. Weperformallexperimentsonsevenwidely-used
useMeanSquaredError(MSE),consistentwithmosttime-domain-
real-worldmulti-channeltimeseriesforecastingdatasets.These
basedmethods[22,26,30,40,48].Inthefrequencydomain,we
datasetsencompassdiversedomains,includingECLTransformer
employMeanAbsoluteError(MAE),following[38],duetoitseffec-
Temperature(ETTh1,ETTh2,ETTm1,andETTm2)[51],ECL,Traf-
tivenessinhandlingvaryingmagnitudesoffrequencycomponents
fic,andWeather,asutilizedbyAutoformer[40].Forfairnessin
anditsstabilitycomparedtosquaredlossfunctions.Theuseof
comparison,weadheretoastandardizedprotocol[22],dividingall
DiscreteCosineTransform(DCT)facilitatesthisapproachbycon-
forecastingdatasetsintotraining,validation,andtestsets.Specifi-
centratingenergyintofewercoefficientsandutilizingrealnumbers,
cally,weemployaratioof6:2:2fortheETTdatasetand7:1:2for
whichenhancesthecaptureoffrequencydomaininformation.The
theremainingdatasets,inlinewith[9,22,26,30,41].RefertoTable
overalllossfunctionofourmethodisthusformulatedas:
1foranoverviewofthecharacteristicsofthesedatasets.
 L
L
t
fr
im
e
e
=
=
𝑀
𝑀
𝐴
𝑆
𝐸
𝐸
(𝐷
(Y
𝐶
−
𝑇(
𝐹
Y
(
)
X
−
))
𝐷
,
𝐶𝑇(𝐹(X))), (7) Tim
E
e
v
s
a
N
lu
et
a
[
t
4
io
1
n
],i
p
s
r
b
o
a
to
se
c
d
ol
o
.
n
O
t
u
w
r
o
ev
k
a
e
l
y
ua
m
ti
e
o
t
n
ric
fr
s
a
:
m
M
e
e
w
an
or
S
k
q
,
u
in
a
s
re
p
d
ire
E
d
rr
b
o
y
r
 L
total
=L
time
+L
fre
.
(MSE)andMeanAbsoluteError(MAE).Toensurefaircomparison,


Conference’17,July2017,Washington,DC,USA ZhengnanLi,YunxiaoQin,XilongCheng,andYutingTan
Table 2: Full forecasting results on different prediction lengths ∈ {96,192,336,720}. Lower MSE and MAE indicate better
performance.Wehighlightthebestperformancewithredboldtext.
Methods FTMixer ModernTCN TSLANet iTransformer PatchTST Crossformer FEDformer RLinear Dlinear TimesNet
Methods —— ICLR2024 ICML2024 ICLR2024 ICLR2023 ICLR2023 ICML2022 ICLR2022 AAAI2023 ICLR2023
Metric MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
1ℎ𝑇𝑇𝐸
96 0.356 0.388 0.391 0.410 0.382 0.406 0.386 0.405 0.382 0.401 0.423 0.448 0.376 0.419 0.386 0.395 0.375 0.399 0.384 0.402
192 0.401 0.410 0.416 0.423 0.422 0.435 0.441 0.436 0.428 0.425 0.471 0.474 0.420 0.448 0.437 0.424 0.405 0.416 0.436 0.429
336 0.422 0.425 0.437 0.435 0.443 0.451 0.487 0.458 0.451 0.436 0.570 0.546 0.459 0.465 0.479 0.446 0.439 0.443 0.491 0.469
720 0.430 0.454 0.461 0.470 0.499 0.498 0.503 0.491 0.452 0.459 0.653 0.621 0.506 0.507 0.481 0.470 0.472 0.490 0.521 0.500
Avg 0.402 0.419 0.426 0.434 0.434 0.447 0.454 0.448 0.428 0.430 0.529 0.522 0.440 0.460 0.446 0.434 0.423 0.437 0.458 0.450
2ℎ𝑇𝑇𝐸
96 0.275 0.335 0.279 0.344 0.289 0.351 0.297 0.349 0.285 0.340 0.745 0.584 0.358 0.397 0.288 0.338 0.289 0.353 0.340 0.374
192 0.336 0.375 0.342 0.387 0.342 0.388 0.380 0.400 0.356 0.386 0.877 0.656 0.429 0.439 0.374 0.390 0.383 0.418 0.402 0.414
336 0.359 0.398 0.363 0.402 0.371 0.413 0.428 0.432 0.365 0.405 1.043 0.731 0.496 0.487 0.415 0.426 0.448 0.465 0.452 0.452
720 0.388 0.427 0.390 0.428 0.417 0.450 0.427 0.445 0.395 0.427 1.104 0.763 0.463 0.474 0.420 0.440 0.605 0.551 0.462 0.468
Avg 0.339 0.383 0.344 0.390 0.355 0.401 0.383 0.407 0.347 0.387 0.942 0.684 0.437 0.449 0.374 0.399 0.431 0.447 0.414 0.427
1𝑚𝑇𝑇𝐸
96 0.284 0.334 0.293 0.345 0.286 0.340 0.334 0.368 0.291 0.340 0.404 0.426 0.379 0.419 0.355 0.376 0.299 0.343 0.338 0.375
192 0.321 0.361 0.336 0.372 0.329 0.372 0.377 0.391 0.328 0.365 0.450 0.451 0.426 0.441 0.391 0.392 0.335 0.365 0.374 0.387
336 0.355 0.384 0.370 0.391 0.356 0.387 0.426 0.420 0.365 0.389 0.532 0.515 0.445 0.459 0.424 0.415 0.369 0.386 0.410 0.411
720 0.415 0.417 0.422 0.419 0.417 0.418 0.491 0.459 0.422 0.423 0.666 0.589 0.543 0.490 0.487 0.450 0.425 0.421 0.478 0.450
Avg 0.343 0.373 0.355 0.382 0.347 0.380 0.407 0.410 0.352 0.379 0.513 0.495 0.448 0.452 0.414 0.408 0.357 0.379 0.400 0.406
2𝑚𝑇𝑇𝐸
96 0.163 0.252 0.168 0.257 0.167 0.262 0.180 0.264 0.169 0.254 0.287 0.366 0.203 0.287 0.182 0.265 0.167 0.260 0.187 0.267
192 0.219 0.287 0.225 0.297 0.230 0.305 0.250 0.309 0.230 0.294 0.414 0.492 0.269 0.328 0.246 0.304 0.224 0.303 0.249 0.309
336 0.269 0.320 0.273 0.328 0.284 0.337 0.311 0.348 0.280 0.329 0.597 0.542 0.325 0.366 0.307 0.342 0.281 0.342 0.321 0.351
720 0.351 0.377 0.370 0.390 0.368 0.391 0.412 0.407 0.378 0.386 1.730 1.042 0.421 0.415 0.407 0.398 0.397 0.421 0.408 0.403
Avg 0.250 0.309 0.259 0.318 0.262 0.324 0.288 0.332 0.264 0.316 0.757 0.611 0.305 0.349 0.286 0.327 0.267 0.332 0.291 0.333
𝑐𝑖𝑓𝑓𝑎𝑟𝑇
96 0.362 0.238 0.425 0.298 0.372 0.261 0.395 0.268 0.401 0.267 0.522 0.290 0.587 0.366 0.649 0.389 0.410 0.282 0.593 0.321
192 0.382 0.252 0.435 0.302 0.388 0.266 0.417 0.276 0.406 0.268 0.530 0.293 0.604 0.373 0.601 0.366 0.423 0.287 0.617 0.336
336 0.389 0.256 0.446 0.306 0.394 0.269 0.433 0.283 0.421 0.277 0.558 0.305 0.621 0.383 0.609 0.369 0.436 0.296 0.629 0.336
720 0.425 0.281 0.452 0.311 0.430 0.289 0.467 0.302 0.452 0.297 0.589 0.328 0.626 0.382 0.647 0.387 0.466 0.315 0.640 0.350
Avg 0.390 0.257 0.440 0.304 0.396 0.271 0.428 0.282 0.420 0.277 0.550 0.304 0.610 0.376 0.627 0.378 0.434 0.295 0.620 0.336
𝑟𝑒ℎ𝑡𝑎𝑒𝑊
96 0.143 0.187 0.150 0.204 0.148 0.198 0.174 0.214 0.160 0.204 0.158 0.230 0.217 0.296 0.192 0.232 0.176 0.237 0.172 0.220
192 0.188 0.232 0.196 0.247 0.194 0.242 0.221 0.254 0.204 0.245 0.206 0.277 0.276 0.336 0.240 0.271 0.220 0.282 0.219 0.261
336 0.241 0.276 0.247 0.286 0.245 0.282 0.278 0.296 0.257 0.285 0.272 0.335 0.339 0.380 0.292 0.307 0.265 0.319 0.280 0.306
720 0.318 0.332 0.330 0.339 0.325 0.337 0.358 0.349 0.329 0.338 0.398 0.418 0.403 0.428 0.364 0.353 0.323 0.362 0.365 0.359
Avg 0.223 0.257 0.231 0.269 0.228 0.265 0.258 0.278 0.238 0.268 0.259 0.315 0.309 0.360 0.272 0.291 0.246 0.300 0.259 0.287
𝐿𝐶𝐸
96 0.127 0.217 0.142 0.345 0.136 0.229 0.148 0.240 0.138 0.230 0.219 0.314 0.193 0.308 0.201 0.281 0.140 0.237 0.168 0.272
192 0.145 0.235 0.156 0.25 0.152 0.244 0.162 0.253 0.149 0.243 0.231 0.322 0.201 0.315 0.201 0.283 0.153 0.249 0.184 0.289
336 0.163 0.262 0.174 0.269 0.168 0.262 0.178 0.269 0.169 0.262 0.246 0.337 0.214 0.329 0.215 0.298 0.169 0.267 0.198 0.300
720 0.199 0.285 0.211 0.297 0.205 0.293 0.225 0.317 0.211 0.299 0.280 0.363 0.246 0.355 0.257 0.331 0.203 0.301 0.220 0.320
Avg 0.159 0.249 0.171 0.290 0.165 0.257 0.178 0.270 0.167 0.259 0.244 0.334 0.214 0.327 0.219 0.298 0.166 0.264 0.193 0.295
weusepredictionlengthsof{96,192,336,720}andsetthehistor- Baselinesetting. WecompareFTMixeragainstavarietyofstate-
icalhorizonlengthto𝑇 = 336forourmodel.Forothermodels, of-the-artbaselines.Transformer-basedbaselinesincludeiTrans-
wefollow[30,41]bytreatingthehistoricalhorizon𝑇 asahyper- former,PatchTST,Crossformer,FEDformer,andAutoformer.MLP-
parameter and using the settings from their original papers, as basedbaselinesincludeRLinear[15]andDLinear[48].Besides,we
somemodelsmayexhibitperformancedegradationwithincreasing alsoconsidertheConvolutional-basedbaselineSCINet[21],the
historicalhorizons.Forbaselines,wereportthebestresultsfrom general-purposetimeseriesmodelsTimesNet,anotherfrequency
theiroriginalworksiftheirsettingsmatchours;otherwise,we domainrelatedbaselineTSLANet[9],andModernTCN[26].
re-runtheirofficialcodestoensurefaircomparison.Notably,some
officialcodesofbaselinescontainabugthatdropsthelastbatch
4.2 ExperimentalResults
duringtesting1.Wefixedthisissueandre-runthesebaselines.All
reportedresultsareaveragedover10randomseeds. QuantitativeComparison.Table2presentsthecomprehensive
forecastingresults,withthetop-performingresultshighlighted
1Wefoundthisbugat:https://github.com/yuqinie98/PatchTST/issues/7. inboldredandthesecond-bestresultsunderlinedinblue.Lower

FTMixer:FrequencyandTimeDomainRepresentationsFusionforTimeSeriesForecasting Conference’17,July2017,Washington,DC,USA
Table3:TheablationexperimentalresultsaboutWFTCand Table4:Theablationexperimentsaboutlossfunction(MSE).
FCC(MSE).
ETTh1 Weather ECL ETTm2
ETTh1 ECL Weather ETTm2
w/oFreLoss 0.419 0.231 0.169 0.262
w/oWFTC 0.447 0.186 0.255 0.263 w/oTimeLoss 0.418 0.246 0.164 0.256
w/oFCC 0.427 0.171 0.242 0.258 Ours 0.402 0.223 0.159 0.250
Ours 0.402 0.159 0.223 0.250
Table5:ExperimentalresultscomparingtheDCTandDFT
versions of our model (MSE). Although the DCT version
values of Mean Squared Error (MSE) and Mean Absolute Error showsonlyamarginalimprovementovertheDFTversion
(MAE)indicatebetterpredictiveperformance.Itisevidentthat intermsofperformance,itismoreefficientasitavoidsthe
FTMixerconsistentlydemonstratesthemostpromisingpredictive additionalcomplexityofseparatelyprocessingtherealand
performanceacrossalldatasets.Onthe𝐸𝑇𝑇ℎ1dataset,FTMixer
imaginarypartsofcomplexnumbers.
outperformsModernTCNandTSLANet,achievingnoticeablere-
ductionsinMSEandMAE,whichunderscoresitseffectivenessin ETTh1 ECL Weather ETTm2
capturingcomplexpatterns.Thistrendcontinuesonthe𝐸𝑇𝑇ℎ2
Ours(DFTVersion) 0.407 0.164 0.226 0.254
dataset,whereFTMixerexcelsbeyondCrossformerandFEDformer,
Ours(DCTVersion) 0.402 0.159 0.223 0.250
especiallyinlongerforecastinghorizonssuchas720.Additionally,
onthe𝑇𝑟𝑎𝑓𝑓𝑖𝑐dataset,FTMixerconsistentlydeliversthelowest
losscomparedtoDlinearandTimesNet. inter-seriesrelationships,whicharecrucialfordatasetswithcom-
Toprovideadeeperunderstandingofwhyourmethodoutper- plexinter-seriesstructures.AsshowninTable3,omittingFCC
formsothers,weanalyzeitsperformanceonthreerepresentative resultsinsignificantperformancedegradation,particularlyonthe
datasets:ETTh1Dataset:TheETTh1datasetfeaturesbothglobal ECLdataset,wheretheMSErisesfrom0.159to0.171whenFCCis
andcomplexlocalmulti-scaledependencies[45].Inthiscontext, removed.ThisindicatesFCC’sessentialroleinleveragingglobal
FTMixerexcelsbyleveragingitsabilitytocapturebothglobalde- frequencydomaininformationtoenhanceforecastingaccu-
pendenciesthroughFCCandlocaldependenciesthroughWFTC, racy.
resultinginsuperiorperformance.WeatherDataset:Characterized
bylocaldependenciesandsignificantnoise[45],thisdatasetposes TheEffectivenessofDDLF. Weassesstheeffectivenessofthe
achallenge.FTMixereffectivelycapturesintricatepatternsdespite Dual-DomainLossFunction(DDLF)throughablationexperiments
thenoise,demonstratingitspromisingperformanceinnoisyenvi- ontheETTh1andWeatherdatasets.ForETTh1,whichfeatures
ronments.ECLDataset:Withsignificantglobaldependencies[36], complexseasonalpatternsandlong-termtrends[40,45],excluding
thisdatasethighlightsFTMixer’scapabilitytoexcelevenwhen thefrequencydomainlosscomponent,L fre ,resultsinanincreased
globalpatternsareprevalent.FTMixerconsistentlyoutperforms MSEfrom0.402to0.419.Thissuggeststhatfrequencydomaininfor-
othermodels,showcasingitseffectivenessincapturingbothglobal mationiscrucialforcapturingperiodictrends.Removingthetime
andlocaldependenciesacrossdiversedatasets. domainlosscomponent,L time,alsodegradesperformance,raising
theMSEto0.418,indicatingtheimportanceofcapturinglocalde-
5 ModelAnalysis pendencies.Similarly,intheWeatherdataset,whichinvolvesless
pronouncedperiodicpatternsbuthassignificantlocalvariations
5.1 AblationStudy
[45],theMSEincreasesfrom0.223to0.231whenL isomitted,
fre
Inthissubsection,weassessthecontributionsofeachcomponent andto0.246whenL timeisremoved.Thesefindingsunderscorethe
ofourFTMixermethodbyremovingitfromFTMixer.Theresults, necessityofintegratingbothfrequencyandtimedomainlossesto
presentedinTables3and4,underscorethesignificanceofeach effectivelycapturethediversefeaturespresentindifferentdatasets,
component.Theexperimentalsettingsforthisablationstudyare therebyenhancingoverallforecastingaccuracy.
consistentwiththoseemployedinthemainexperiments.
5.2 DCTvsDFT
TheEffectivenessofWFTC. TheWindowedFrequency-Time
Inthissection,wereplaceDCTwithDFTtocomparetheirperfor-
Convolution(WFTC)moduleisdesignedtocapturelocaldepen-
manceunderthesameexperimentalsetupasthemainexperiments.
dencies.Itisparticularlyeffectiveondatasetswithpronounced
SinceDFTproducescomplexnumbers,weseparatelypredictthe
localpatterns,suchasWeatherandETTh1.Asdemonstratedin
realandimaginaryparts.Thesecomponentsarethencombined
Table3,theremovalofWFTCleadstoamarkeddecreaseinper-
andtransformedbacktothetimedomainusingtheinverseDFT
formance.Forinstance,withoutWFTC,themeansquarederror
(IDFT).Processingrealandimaginarypartsindependentlyintro-
(MSE)increasesto0.447ontheETTh1datasetandto0.186onthe
ducesadditionalparametersandcomputationaloverhead,making
ECLdataset.ThisdeclineemphasizestheWFTC’scriticalrolein
thisapproachlessefficientcomparedtousingDCT.Asshownin
extractingcomplexmulti-scalelocalfeaturesandimproving
Table5,theDCTversionofthemodelconsistentlyoutperforms
themodel’sabilitytohandleintricatelocaldependencies.
theDFTversion.Forexample,ontheETTh1dataset,DCTachieves
TheEffectivenessofFCC. TheFrequencyChannelConvolu- aMeanSquaredError(MSE)of0.402,whereasDFTresultsinan
tion(FCC)modulefocusesoncapturingglobaldependenciesand MSEof0.407.Wehypothesizethatthesuperiorperformanceof

Conference’17,July2017,Washington,DC,USA ZhengnanLi,YunxiaoQin,XilongCheng,andYutingTan
0.2 0.2 0.2
0.4 0.4 0.4
0.6 0.6 0.6
0.8 0.8 0.8
1.0 1.0 1.0
1.2 1.2 1.2
1.4 1.4 1.4
1.6 1.6 1.6
GroundTruth GroundTruth GroundTruth
Prediction Prediction Prediction
0 100 200 300 400 0 100 200 300 400 0 100 200 300 400
Ours PatchTST ModernTCN
Figure3:ThevisualizationofpredictionsbyFTMixer,PatchTST,andModernTCNontheETTh1datasetshowsthattheproposed
FTMixerachievesthebestperformancewithanMSEof0.356,comparedtoPatchTST’s0.382andModernTCN’s0.375.
Table 6: The computational cost comparisonbetween the delineatedinTable6,FTMixershowcasedsuperiorefficiencywhen
proposedFTMixer,iTransformer,andPatchTST.Thebatch comparedtotwoprominentstate-of-the-artmethodsModernTCN
sizeforETTh1datasethereis32,whilethebatchsizeforECL andPatchTST.ModernTCN’sefficiencydiminishesasthenumber
datasethereis1. ofchannelsescalatesduetothelinearcomplexityofitsconvolu-
tionkernelwithrespecttochannelcount.Forinstance,theETTh1
Cost Benchmark FTMixer ModernTCN PatchTST datasetcomprises7channels,whiletheECLdatasetcomprises321
ETTh1 0.021s 0.043s 0.027s channels.Incontrast,FTMixerexhibitslowermemorycostsun-
Time
ECL 0.023s 0.141s 0.036s dersimilarconditions,demonstratingitsefficiencyacrossvarying
channelcounts.
ETTh1 272MB 316MB 448MB
Memory
ECL 304MB 3350MB 828MB
5.4 Visualization
Table7:TheperformanceoftheproposedFTMixerunder
Here,wevisualizethepredictionsontheETTh1dataset.Asillus-
diverseinputlengths.
tratedinFigure3,ourFTMixermodelmoreeffectivelycapturesthe
primarytrends,aligningmorecloselywiththegroundtruthcom-
ETTh1 Weather Traffic
paredtothetwobaselines,PatchTSTandModernTCN.Incontrast,
MSE MAE MSE MAE MSE MAE
ModernTCNandPatchTSTexhibitmorelocalizedfeaturesandare
96 0.368 0.390 0.165 0.207 0.392 0.261 lessaccurateinreflectingtheoveralltrend.
192 0.360 0.389 0.153 0.195 0.376 0.247
336 0.356 0.388 0.143 0.187 0.362 0.238 5.5 VaryingInputLength
720 0.355 0.387 0.142 0.189 0.354 0.231
Inthissection,weevaluatetheperformanceofourmodelwith
varyinginputlengths𝐿 ∈ {96,192,336,720}whilemaintaininga
fixedpredictionlengthof96.AsillustratedinTable7,theperfor-
DCToverDFTisduetotheinefficiencyandadditionalcomplexity
manceofFTMixerimproveswithlongerinputlengths.Forinstance,
involvedinseparatelyprocessingrealandimaginarycomponents,
ontheETTh1dataset,theMSEdecreasesfrom0.368at𝐿 = 96
whichimpactstheoverallforecastingaccuracy.
to0.355at𝐿 = 720,demonstratingthemodel’senhancedability
5.3 ComputationalEfficiency incapturinglong-termdependencies.Similarly,ontheWeather
dataset,MSEdropsfrom0.165at𝐿=96to0.142at𝐿=720,indi-
Inthissubsection,wedelveintothecomputationalefficiencyanaly-
catingimprovedperformanceinmanagingcomplexseasonaland
sisoftheproposedFTMixer.FTMixerstandsoutasapurelyTempo-
trendpatterns.TheseimprovementscanbeattributedtoFTMixer’s
ralConvolutionalNetwork(TCN)-basedmethod,distinguishedby
WindowedFrequency-TimeConvolution(WFTC)andFrequency
itsstreamlinedcomputationaloverhead.UnlikeTransformer-based
ChannelConvolution(FCC),whicheffectivelycapturebothlocal
methodologies,whichtypicallyentailacomputationalcomplexity
andglobalpatterns.Longerinputlengthsprovidethemodelwitha
of𝑂(𝑇2)perlayer,FTMixersignificantlymitigatesthisburdento
morecomprehensivetemporalcontext,enablingittobettermanage
𝑂(𝐾𝑇),where𝐾 denotesthesizeoftheconvolutionkernel.The
andintegratevariousdependenciespresentinthedata.
computationalcomplexityoftheFeatureVisionConvolution(FCC)
component within FTMixer is expressed as𝑂(𝑇𝑀𝐾), where 𝑀
signifies the number of channels and𝐾 denotes the size of the 6 Conclusion
convolution kernel. To substantiate the efficiency claims of FT- This paper investigates the potential of combining information
Mixer,experimentswereconductedwithaninputlengthof336 fromboththetimedomainandthefrequencydomainfortimese-
andanoutputlengthof96ontheETTh1andECLdatasets.As riesforecastingtasks.WeproposeanovelmethodcalledFTMixer,

FTMixer:FrequencyandTimeDomainRepresentationsFusionforTimeSeriesForecasting Conference’17,July2017,Washington,DC,USA
whichintegratestheDiscreteCosineTransform(DCT).Ourap-
proachincludestheFrequencyConvolutionComponent(FCC)for
capturingglobaldependenciesandtheWindowedFrequency-Time
Convolution(WFTC)moduleforlocaldependencyextractionin
bothdomains.Extensiveexperimentsdemonstratetheeffective-
nessofFTMixer,showcasingitsstate-of-the-artperformanceand
computationalefficiency.Thesefindingsunderscorethesignificant
valueoffrequencydomaininformationandthecombinedapproach
ofFCCandWFTCinenhancingtimeseriesforecasting.Webelieve
these results caninspire further exploration into thefrequency
domain’sroleintimeseriesforecastingtasks.

Conference’17,July2017,Washington,DC,USA ZhengnanLi,YunxiaoQin,XilongCheng,andYutingTan
References
[30] Y.Nie,N.H.Nguyen,P.Sinthong,andJ.Kalagnanam.Atimeseriesisworth64
[1] N.Ahmed,T.Natarajan,andK.Rao.Discretecosinetransform.IEEETransactions words:Long-termforecastingwithtransformers.arXivpreprintarXiv:2211.14730,
onComputers,C-23(1):90–93,1974.doi:10.1109/T-C.1974.223784. 2022.
[2] N.Ahmed,T.Natarajan,andK.R.Rao.Discretecosinetransform.IEEEtransac- [31] B.N.Oreshkin,D.Carpov,N.Chapados,andY.Bengio.N-beats:Neuralbasis
tionsonComputers,100(1):90–93,1974. expansionanalysisforinterpretabletimeseriesforecasting,2020.
[3] C.Challu,K.G.Olivares,B.N.Oreshkin,F.Garza,M.Mergenthaler-Canseco, [32] S.Qi,Z.Xu,Y.Li,L.Wen,Q.Wen,Q.Wang,andY.Qi. Pdetime:Rethinking
andA.Dubrawski. N-hits:Neuralhierarchicalinterpolationfortimeseries long-termmultivariatetimeseriesforecastingfromtheperspectiveofpartial
forecasting,2022. differentialequations,2024.
[4] M.Cheng,J.Yang,T.Pan,Q.Liu,andZ.Li.Convtimenet:Adeephierarchical [33] L.F.RichardsonandW.F.Eddy. Algorithm991:The2dtreeslidingwindow
fullyconvolutionalmodelformultivariatetimeseriesanalysis.arXivpreprint discretefouriertransform.ACMTransactionsonMathematicalSoftware,45(1):
arXiv:2403.01493,2024. 1–12,Feb.2019.ISSN1557-7295.doi:10.1145/3264426.URLhttp://dx.doi.org/10.
[5] F.Chollet.Xception:Deeplearningwithdepthwiseseparableconvolutions,2017. 1145/3264426.
URLhttps://arxiv.org/abs/1610.02357. [34] R.Stasiński. Dctcomputationusingreal-valueddftalgorithms. In200211th
[6] H.-H.Chou,J.Maly,andH.Rauhut.Moreisless:Inducingsparsityviaoverpa- EuropeanSignalProcessingConference,pages1–4,2002.
rameterization,2023.URLhttps://arxiv.org/abs/2112.11027. [35] W.TonerandL.Darlow.Ananalysisoflineartimeseriesforecastingmodels,
[7] A.Das,W.Kong,A.Leach,R.Sen,andR.Yu.Long-termforecastingwithtide: 2024.
Time-seriesdenseencoder.arXivpreprintarXiv:2304.08424,2023. [36] A.Trindade.ElectricityLoadDiagrams20112014.UCIMachineLearningReposi-
[8] I.Daubechies.Thewavelettransform,time-frequencylocalizationandsignal tory,2015.DOI:https://doi.org/10.24432/C58C86.
analysis. IEEETransactionsonInformationTheory,36(5):961–1005,1990. doi: [37] H.Wang,J.Peng,F.Huang,J.Wang,J.Chen,andY.Xiao.Micn:Multi-scalelocal
10.1109/18.57199. andglobalcontextmodelingforlong-termseriesforecasting.InTheEleventh
[9] E.Eldele,M.Ragab,Z.Chen,M.Wu,andX.Li.Tslanet:Rethinkingtransformers InternationalConferenceonLearningRepresentations,2022.
fortimeseriesrepresentationlearning.InInternationalConferenceonMachine [38] H.Wang,L.Pan,Z.Chen,D.Yang,S.Zhang,Y.Yang,X.Liu,H.Li,andD.Tao.
Learning,2024. Fredf:Learningtoforecastinfrequencydomain.arXivpreprintarXiv:2402.02399,
[10] K.Fukushima. Visualfeatureextractionbyamultilayerednetworkofanalog 2024.
thresholdelements.IEEETransactionsonSystemsScienceandCybernetics,5(4): [39] B.Woodworth,S.Gunasekar,J.D.Lee,E.Moroshko,P.Savarese,I.Golan,
322–333,1969.doi:10.1109/TSSC.1969.300225. D.Soudry,andN.Srebro.Kernelandrichregimesinoverparametrizedmodels,
[11] D.Gissin,S.Shalev-Shwartz,andA.Daniely.Theimplicitbiasofdepth:How 2020.URLhttps://arxiv.org/abs/2002.09277.
incrementallearningdrivesgeneralization,2019.URLhttps://arxiv.org/abs/1909. [40] H.Wu,J.Xu,J.Wang,andM.Long. Autoformer:Decompositiontransform-
12051. erswithauto-correlationforlong-termseriesforecasting.Advancesinneural
[12] L.Han,X.-Y.Chen,H.-J.Ye,andD.-C.Zhan.Softs:Efficientmultivariatetime informationprocessingsystems,34:22419–22430,2021.
seriesforecastingwithseries-corefusion,2024. [41] H.Wu,T.Hu,Y.Liu,H.Zhou,J.Wang,andM.Long.Timesnet:Temporal2d-
[13] F.Harris.Ontheuseofwindowsforharmonicanalysiswiththediscretefourier variationmodelingforgeneraltimeseriesanalysis.InTheeleventhinternational
transform.ProceedingsoftheIEEE,66(1):51–83,1978.doi:10.1109/PROC.1978. conferenceonlearningrepresentations,2022.
10837. [42] K.Xu,M.Qin,F.Sun,Y.Wang,Y.-K.Chen,andF.Ren.Learninginthefrequency
[14] S.IoffeandC.Szegedy.Batchnormalization:Acceleratingdeepnetworktraining domain.InProceedingsoftheIEEE/CVFconferenceoncomputervisionandpattern
byreducinginternalcovariateshift,2015.URLhttps://arxiv.org/abs/1502.03167. recognition,pages1740–1749,2020.
[15] T.Kim,J.Kim,Y.Tae,C.Park,J.-H.Choi,andJ.Choo. Reversibleinstance [43] Z.Xu,A.Zeng,andQ.Xu.Fits:Modelingtimeserieswith10𝑘parameters.arXiv
normalizationforaccuratetime-seriesforecastingagainstdistributionshift.In preprintarXiv:2307.03756,2023.
InternationalConferenceonLearningRepresentations,2021. [44] W.Xue,T.Zhou,Q.Wen,J.Gao,B.Ding,andR.Jin. Card:Channelaligned
[16] G.Lai,W.-C.Chang,Y.Yang,andH.Liu.Modelinglong-andshort-termtemporal robustblendtransformerfortimeseriesforecasting,2024.
patternswithdeepneuralnetworks,2018. [45] H.Ye,J.Chen,S.Gong,F.Jiang,T.Zhang,J.Chen,andX.Gao.Atfnet:Adaptive
[17] B.Li,W.Cui,L.Zhang,C.Zhu,W.Wang,I.W.Tsang,andJ.T.Zhou.Difformer: time-frequencyensemblednetworkforlong-termtimeseriesforecasting,2024.
Multi-resolutionaldifferencingtransformerwithdynamicrangingfortimeseries [46] J.Ye,W.Zhang,K.Yi,Y.Yu,Z.Li,J.Li,andF.Tsung. Asurveyoftimeseries
analysis.IEEETransactionsonPatternAnalysisandMachineIntelligence,45(11): foundationmodels:Generalizingtimeseriesrepresentationwithlargelanguage
13586–13598,2023.doi:10.1109/TPAMI.2023.3293516. model,2024.
[18] J.Li,T.V.Nguyen,C.Hegde,andR.K.W.Wong.Implicitsparseregularization: [47] K.Yi,Q.Zhang,W.Fan,S.Wang,P.Wang,H.He,D.Lian,N.An,L.Cao,andZ.Niu.
Theimpactofdepthandearlystopping,2021.URLhttps://arxiv.org/abs/2108. Frequency-domainmlpsaremoreeffectivelearnersintimeseriesforecasting,
05574. 2023.
[19] Z.Li,R.Cai,Z.Yang,H.Huang,G.Chen,Y.Shen,Z.Chen,X.Song,Z.Hao,and [48] A.Zeng,M.Chen,L.Zhang,andQ.Xu.Aretransformerseffectivefortimeseries
K.Zhang.Whenandhow:Learningidentifiablelatentstatesfornonstationary forecasting?,2022.
timeseriesforecasting,2024. [49] Y.ZhangandJ.Yan. Crossformer:Transformerutilizingcross-dimensionde-
[20] B.Lim,S.O.Arik,N.Loeff,andT.Pfister. Temporalfusiontransformersfor pendencyformultivariatetimeseriesforecasting.InTheeleventhinternational
interpretablemulti-horizontimeseriesforecasting,2020. conferenceonlearningrepresentations,2022.
[21] M.Liu,A.Zeng,M.Chen,Z.Xu,Q.Lai,L.Ma,andQ.Xu.Scinet:Timeseries [50] P.Zhao,Y.Yang,andQ.-C.He.High-dimensionallinearregressionviaimplicit
modelingandforecastingwithsampleconvolutionandinteraction.Advancesin regularization. Biometrika,109(4):1033–1046,Feb.2022. ISSN1464-3510. doi:
NeuralInformationProcessingSystems,35:5816–5828,2022. 10.1093/biomet/asac010.URLhttp://dx.doi.org/10.1093/biomet/asac010.
[22] Y.Liu,T.Hu,H.Zhang,H.Wu,S.Wang,L.Ma,andM.Long. itransformer: [51] H.Zhou,S.Zhang,J.Peng,S.Zhang,J.Li,H.Xiong,andW.Zhang.Informer:
Invertedtransformersareeffectivefortimeseriesforecasting. arXivpreprint Beyondefficienttransformerforlongsequencetime-seriesforecasting.InThe
arXiv:2310.06625,2023. Thirty-FifthAAAIConferenceonArtificialIntelligence,AAAI2021,VirtualConfer-
[23] Y.Liu,C.Li,J.Wang,andM.Long.Koopa:Learningnon-stationarytimeseries ence,volume35,pages11106–11115.AAAIPress,2021.
dynamicswithkoopmanpredictors,2023. [52] M.ZhouandR.Ge.Implicitregularizationleadstobenignoverfittingforsparse
[24] Y.Liu,H.Wu,J.Wang,andM.Long.Non-stationarytransformers:Exploring linearregression,2023.URLhttps://arxiv.org/abs/2302.00257.
thestationarityintimeseriesforecasting,2023. [53] T.Zhou,Z.Ma,Q.Wen,X.Wang,L.Sun,andR.Jin.Fedformer:Frequencyen-
[25] Y.Liu,H.Zhang,C.Li,X.Huang,J.Wang,andM.Long.Timer:Transformers hanceddecomposedtransformerforlong-termseriesforecasting.InInternational
fortimeseriesanalysisatscale,2024. conferenceonmachinelearning,pages27268–27286.PMLR,2022.
[26] D.LuoandX.Wang. Moderntcn:Amodernpureconvolutionstructurefor
generaltimeseriesanalysis.InTheTwelfthInternationalConferenceonLearning
Representations,2024.
[27] G.Michau,G.Frusque,andO.Fink. Fullylearnabledeepwavelettransform
forunsupervisedmonitoringofhigh-frequencytimeseries.Proceedingsofthe
NationalAcademyofSciences,119(8),Feb.2022.ISSN1091-6490.doi:10.1073/
pnas.2106598119.URLhttp://dx.doi.org/10.1073/pnas.2106598119.
[28] R.Mukherji,M.Schöne,K.K.Nazeer,C.Mayr,D.Kappel,andA.Subramoney.
Weightsparsitycomplementsactivitysparsityinneuromorphiclanguagemodels,
2024.
[29] Z.Ni,H.Yu,S.Liu,J.Li,andW.Lin.Basisformer:Attention-basedtimeseries
forecastingwithlearnableandinterpretablebasis,2024.

FTMixer:FrequencyandTimeDomainRepresentationsFusionforTimeSeriesForecasting Conference’17,July2017,Washington,DC,USA
A Visualizationofresults B ImpactofWindowSizeonWFTC
Figure4visualizestheoutputofFTMixeronsixrealbenchmarks. Performance
FTMixerdemonstratesexceptionalaccuracy,producingpredictions Inthissection,weanalyzetheimpactofwindowsizeontheETTh1
highlyconsistentwithgroundtruth. dataset,withinputlengthsof96,192,336,720andanoutputlength
of96.TheresultsarereportedinTable8.Wefindthattheproposed
FTMixerperformsthebestwithawindowsizeof24.

Conference’17,July2017,Washington,DC,USA ZhengnanLi,YunxiaoQin,XilongCheng,andYutingTan
0.10 G Pr r e o d u i n c d ti T o r n uth G Pr r e o d u i n c d ti T o r n uth 0 0 . . 7 5 5 0 G Pr r e o d u i n c d ti T o r n uth
2
0.25
0.08 0.00
1 0.25
0.06 0.50
0 0.75
0.04 1.00
1
0.02
0 100 200 300 400 0 100 200 300 400 0 100 200 300 400
Weather ECL ETTm2
1.0 G Pr r e o d u i n c d ti T o r n uth 0.75 G Pr r e o d u i n c d ti T o r n uth 0.2
1.1 0.50 0.4
0.25 0.6
1.2 0.00 0.8
0.25 1.0
1.3 0.50 1.2
1.4 0.75 1.4
1.00 1.6
1.5
GroundTruth
Prediction
1.6
0 100 200 300 400 0 100 200 300 400 0 100 200 300 400
ETTm1 ETTh2 ETTh1
Figure4:VisualizationofMeta-Tunerforecastingonsixdataset.
Table8:TheperformanceoftheproposedFTMixerunderdiverseWFTCwindowsize.
WindowSize
12 24 48
Inputlength
MSE MAE MSE MAE MSE MAE
96 0.373 0.391 0.368 0.390 0.370 0.391
192 0.364 0.390 0.360 0.389 0.363 0.390
336 0.360 0.389 0.356 0.388 0.359 0.389
720 0.357 0.388 0.355 0.387 0.356 0.388

