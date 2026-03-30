# Page 1

5202
yaM
92
]GL.sc[
2v47391.1052:viXra
Fixing the Double Penalty in Data-Driven Weather Forecasting
Through a Modified Spherical Harmonic Loss Function
ChristopherSubich1 SyedZahidHusain1 LeoSeparovic1 JingYang1
Abstract publication of these models, the field has been joined by
manyothers,includingtheArtificialIntelligenceForecast-
Recentadvancementsindata-drivenweatherfore-
ingSystem(AIFS)developedbyECMWFitself(Langetal.,
castingmodelshavedelivereddeterministicmod-
2024a).
elsthatoutperformtheleadingoperationalfore-
castsystemsbasedontraditional,physics-based Fromthestandpointofmachinelearning,atmosphericfore-
models. However,thesedata-drivenmodelsare castingisalarge-scalegenerativeproblemcomparableto
typicallytrainedwithameansquarederrorloss predictingthenextframeofavideo. Asatypicalexample,
function,whichcausessmoothingoffinescales theversionoftheGraphCastmodeldeployedexperimentally
througha“doublepenalty”effect. Wedevelopa bytheNationalOceanicandAtmosphericAdministration
simple, parameter-freemodificationtothis loss (NOAA) (Sadeghi Tabas et al., 2025; NOAA, 2024) pre-
function that avoids this problem by separating dicts the 6-hour forecast for six atmospheric variables at
thelossattributabletodecorrelationfromtheloss eachof13verticallevelsplusfivesurfacevariables,ona¼°
attributable to spectral amplitude errors. Fine- latitude/longitudegrid,forabout86millionoutputdegrees
tuning the GraphCast model with this new loss offreedominaggregate. GraphCasttakestwotime-levels
function results in sharp deterministic weather asinput,sotheinputforthismodelhasabout170million
forecasts,anincreaseofthemodel’seffectiveres- degreesoffreedom.
olutionfrom1,250kmto160km,improvements
Thesefirst-generationdata-drivenweathermodelsgenerally
toensemblespread,andimprovementstopredic-
act as deterministic forecast systems, where each unique
tionsoftropicalcyclonestrengthandsurfacewind
initialconditionismappedtoasingleforecastandverified
extremes.
againsta“groundtruth”fromadataanalysissystem. The
ERA5 atmospheric reanalysis (Hersbach et al., 2020) of
ECMWF is most often used as the source of initial and
1.Introduction
verifyingdatafortheseforecastsystemsowingtoitshigh
The models developed in Weyn et al. (2020) and Keisler qualityandconsistentbehaviourfrom1979topresent.
(2022)suggestedthatdeepneuralnetworksmight“solve”
the problem of medium-range weather forecasting with 1.1.TheProblemofForecastSmoothing
data-driven machine learning models. In 2023, the re-
Despitetheiroverallforecastskill,deterministicdata-driven
leaseofGraphCast(Lametal.,2023),FourCastNet(Kurth
forecast systems are universally understood to produce
etal.,2023),andPangu-Weather(Bietal.,2023)demon-
overly-smooth forecasts. A typical example of this be-
stratedforecastskillthatmetorsurpassedthatofthehigh-
haviourisshowninfigure1wherea3.5-daypredictionof
resolution forecast system (IFS) of the European Centre
winterstormEunicebythe13-level,¼°GraphCastmodel
for Medium Range Weather Forecasts (ECMWF) at lead
is too weak and overly smooth. This smoothing results
times (forecast lengths) up to 10 days, and some com-
inanunder-predictionoflocalizedextremeevents,andit
menters (Bauer, 2024) anticipated that data-driven fore-
makesthemodellesssuitablefordownstreamtaskssuchas
castingwouldsoonsupplanttraditionalnumericalweather
spectralnudging(Husainetal.,2024)anddataassimilation
prediction (NWP) in all operational contexts. Since the
(Slivinskietal.,2025).
1MeteorologicalResearchDivision,EnvironmentandClimate
Thissmoothingismost-discussedinrelationtothepredic-
Change Canada, Dorval, Quebec, Canada. Correspondence to:
tionofgridded,globalweatherfields,butitisstillpresent
ChristopherSubich<christopher.subich@ec.gc.ca>.
inmodelsthathaveradicallydifferentarchitectures. Allen
Proceedingsofthe42nd InternationalConferenceonMachine etal.(2025)developsamodelthatoperatesdirectlyinobser-
Learning,Vancouver,Canada.PMLR267,2025.Copyright2025 vationspacewithoutanunderlyinggridthatstillproduces
bytheauthor(s).
1

---

# Page 2

60°N 24
55°N
50°N
45°N
60°N
55°N
17
50°N
45°N
60°N
55°N
50°N
10
45°N
20°W 10°W 0°
)s/m(
deeps
dniw
m01
directly model the physics of the atmosphere, such that
the system’s forecasts are always plausible atmospheric
stateswithoutexcessivesmoothing. Turningsuchasystem
into an ensemble prediction system involves supplying it
withperturbedinitialconditionsandpossiblystochastically
perturbingthemodel’ssub-gridparameterizations(Palmer,
2001;Berneretal.,2015).
Inthemachinelearningspace,Maheshetal.(2024)devel-
opsawell-calibratedlargeensembleusing29independently-
trainedinstantiationsoftheBonevetal.(2023)architecture.
When combined with initial-condition perturbations, the
result was a well-calibrated large ensemble, despite each
individualensemblemembersufferingfromthesmoothness
typicalofdeterministicdata-drivenforecastsystems.
Lagerquist&Ebert-Uphoff(2022)alsodevelopsavariety
oflossfunctionsbasedonthesamespatialmethods(suchas
filteringandmax-pooling)toverifyforecastsofconvective
eventslikethunderstormsinevaluationofhigh-resolution,
limited-areamodels.
Figure1.10mwindspeedandmeansealevelpressureforwinter NEURALGCM
stormEunice,18Feb2022at0hUTC.Top: HRESdataat¼°
NeuralGCM (Kochkov et al., 2024) is one of the few
(ground truth), middle: 3.5d forecast produced by GraphCast,
bottom:thiswork.Thisworkproducesanoverallsharperforecast, globaldata-drivenmodelsthathasaddressedtheproblem
withabetterpredictionofthewinterstorm’sstrength. ofsmoothingevenindeterministic(non-ensemble)config-
urations. However,thismodelisdifficulttocomparewith
itspeers. Ithasahybridarchitecture,combiningaclassical
smoothforecastsofthefuture,andHanetal.(2024)shows
dynamicalcorewithalearnednetworkforsub-gridparame-
diminishedforecastactivity(abulkmeasurerelatedtoblur-
terizationsthatactsindependentlyateachverticalcolumn,
ring)atlongerleadtimesforalocal-areamodeldespitea
and the classical dynamical core should cause fine-scale
nominalkilometer-scaleresolution.
features to develop naturally. In addition, the model was
The conventional wisdom is that this smoothing is some- trainedusingaweightedsumofseverallossfunctions,one
thingthatcanbefixedinthecontextofanensembleforecast- ofwhichusesMSEonlyonacoarsened(smoothed)version
ingsystem,whichproducesrealizationsfromthespaceof oftheforecastandverifyinganalysiswhileanothermatches
potentialfutureforecasts. GenCast(Priceetal.,2025)and thesphericalharmonicpowerspectrum(butnotphase)only
AIFS-CRPS(Langetal.,2024b)directlyproduceastochas- athighwavenumbers(shortscales). Itisnotclearwhich
tic¼°forecastgiveninitialvaluesandasourceofrandom ofthesepropertiesarenecessaryorsufficienttoreducethe
noise. SEEDS (Li et al., 2024) and ArchesWeatherGen smoothingofdeterministicNeuralGCMforecasts,andthe
(Couaironetal.,2024)areexamplesofmodelsthatpredict useofseverallossfunctionsaddsmanydegreesoffreedom
variationsaroundanensemblemean,usingthegenerative intheirweightingandinternalfiltering.
stepto“fillintheblanks”aroundasmoothbaseline. Lippe
etal.(2023)approachesthisproblemfromamoregeneral
1.2.ThisWork
partialdifferentialequationframework, anditdevelopsa
diffusionmethodthatiterativelyrefinesfinerscales. Thepurposeofthisworkistotackletheproblemofsmooth-
ing ina purelydeterministic, data-driven setting: canwe
Oftheseexamples,allbutAIFS-CRPSuseadiffusiontech-
produceasharpforecastoftheatmospherewithoutdirectly
niquewithmeansquarederror(MSE)usedasthede-noising
modellingensembleuncertainty? Ouransweris“yes.” By
lossfunction,whileAIFS-CRPSinsteadusesthecontinuous
modifyingtheMSElossfunctiontosmoothlyinterpolate
rankedprobabilityscore(CRPS,Gneiting&Raftery(2007))
betweenamplitude-preservationandclassicalMSE,wecan
asitslossfunctiontodirectlyoptimizethespread/errorrela-
efficientlyfine-tuneaversionoftheGraphCastmodeltofix
tionshipofitsproducedensemble.
itssmoothingproblemandreproducesharpforecasts. This
However,wethinkthattheproblemofgeneratingagood greatlyincreasesthemodel’seffectiveresolution,producing
ensembleisdistinctfromtheproblemofforecastsharpness betterpredictionsoftropicalcycloneintensityandsurface
andeffectiveresolution. TraditionalNWPsystemstryto windspeed.
2

---

# Page 3

Section 2 describes the modified loss function, its theory thatobeysParseval’stheorem. Takingthisdecomposition
of operation, and the fine-tuning procedure used for this point-by-point,extendingtheanalysistoincludeanonzero
work. Section 3 presents verification results of the fine- mean,andtakingtheexpectationoveranensembleofpre-
tunedGraphCastmodel,andsection4concludeswithdis- dictionsgivesrisetoskill/spreadevaluations. However,this
cussionofthemethod’slimitationsandpotentialextensions. decompositionisnotpossibleattrainingtimeforadeter-
Appendix A discusses the loss function in the context of ministicdata-drivenweatherforecast,andinsteadweturn
maximumlikelihoodestimation,andappendixBpresents toasphericalharmonicdecomposition.
moredetailedverificationstatistics.
Let Yl(i,j) be the complex-valued spherical harmonic
k
mode with total wavenumber k and zonal wavenumber l
2.Method atthe(i,j)gridpointonalatitude/longitudegrid,normal-
ized such that (cid:82) Yl(Yn)∗ = δ δ , where (·)∗ is the
2.1.SmoothingIsOptimalUnderMeanSquaredError k m km ln
complexconjugate1. Ascalarfieldx(i,j)definedonthe
IntheNWPcommunity,modelevaluationusingthemean latitude/longitudegridcanbewrittenintermsofspherical
squarederroriswidelyunderstoodtosufferfromaso-called harmonicsas:
“doublepenalty”(Hoffmanetal.,1995;Ebertetal.,2013).
k
(cid:88) (cid:88)
UnderMSE,agoodforecastthatcorrectlypredictsafeature x(i,j)= α (k,l)Yl(i,j),
x k
suchasastormbutmissesitslocationispenalizedtwice
k l=−k
comparedtoaperfectforecast,onceformissingthestorm
with α (k,l) the corresponding spectral coefficient. For
atitscorrectlocationandagainforpredictingastormatan x
twofieldsxandythelatitude-weightedMSEis:
incorrectlocation. IntraditionalNWP,thisdoublepenalty
makesmodelverificationmoredifficult,particularlywhen (cid:88)(cid:88)
MSE(x,y)= dA(i,j)(x(i,j)−y(i,j))2
studyingtheimpactofimprovementstoforecastresolution
i j
thatcreatemoreopportunitiesformisplacedpredictions.
k
(cid:88) (cid:88)
WhenMSEisusedasthelossfunctiontotrainadata-driven = |α (k,l)−α (k,l)|2, (3)
x y
model, the double penalty problem is more than annoy- k l=−k
ance: it encourages the model to generate unrealistically
wherethedAtermisincorporatedintothenormalization
smooth predictions by reducing the amplitude of unpre-
of Yl. Importantly, α and α are independent with
dictable scales. To show this quantitatively, consider the k x y
respect to zonal and total wavenumber, but the double
caseofpredictingasinglevariable. LetY = N(0,1)be
summation here now allows us to group these terms in a
thetarget,andletX betheimperfectpredictionofthattar-
physically meaningful way. Grouping terms in the inner
get,modelledasanormalrandomvariablewithastandard
deviation of σ X =
(cid:112)E(X2)
and correlation coefficient
(
P
z
S
on
D
al)
(x
su
)
m
=
to
(cid:80)
geth
|α
erg
(k
iv
,
e
l
s
)|
r
2
is
a
e
n
t
d
o
c
th
o
e
h
p
er
o
e
w
n
e
c
r
e
s
C
pe
o
c
h
tra
(
l
x
d
,
e
y
n
)
si
=
ty
ofρ = E(XY)/σ X , whereE(·)istheexpectationopera- (cid:80) R k (α (k,l)α l ∗(k x ,l))/ (cid:112) PSD (x)PSD (y) k (where
tor. WritingX intermsofacorrelatedandanuncorrelated l x y k k
R(·) takes the real part) as scale-dependent analogs to
componentgives:
variance and correlation respectively. Performing the
(cid:112)
X =σ (ρY + 1−ρ2N(0,1)), (1) appropriatesubstitutions:
X
andthecorrespondingexpectedMSEis: (cid:88)
MSE(x,y)= PSD (x)+PSD (y)−
k k
E(MSE(X,Y))=E((X−Y)2)
k
(cid:112)
=E(X2)+E(Y2)−2E(XY) 2 PSD
k
(x)PSD
k
(y)Coh
k
(x,y). (4)
=σ X 2 +1−2σ X ρ. (2) If x is taken to be a forecast field and y is the
ground-truth analysis, as in (2) this is minimized when
ForfixedY,thisMSEisoptimizedwithaperfectpredic-
(cid:112)
PSD (x)PSD (y)−1 =Coh (x,y)
tion, when σ = 1 and ρ = 1. However, if 0 < ρ < 1 k k k
X
becausetheprocessisonlypartiallypredictable,theMSE This optimum leads to the observed smoothing in data-
isoptimizedwithrespecttoσ X whenσ X =ρ<1,leading drivenmodelsthroughtwofactors:
toanunderpredictionoftheprocess’snaturalvariability.
• Finescales(largek,shortwavelengths)aregenerally
2.2.SpectralSeparationoftheMeanSquaredError lesspredictablethancoarsescales(smallk,largewave-
lengths),particularlyatlongerleadtimes,and
Predictions of global weather are high-dimensional, but
equations (1) and (2) can be extended to any decomposi- 1In practice, this work takes advantage of the property that
tion(partitionofunity)ofthepredictionandtargetfields Y−l =(Yl)∗toworkwithonlynon-negativewavenumbers.
k k
3

---

# Page 4

1.1
1.0
0.9
0.8
0.7
0 75000 150000 225000 300000
pets-elgniS
Amplitude ratio
Coherence
0.9
0.8
0.7
0.6
0.5
300000 304000 307000 311000
Batch
pets-itluM
moredesirableifthelossfunctionreflectedourtruegoal,
encouragingforecaststocorrelatewelltotheground-truth
andretainrealisticvariationatfinerscales.
Fortunately, beginning with MSE written in terms of its
spectraldecomposition,thisisasimplemodification. First,
we write (4) in terms of a perfectly-correlated loss (with
Coh (x,y)=1)andaresidual:
k
(cid:88) (cid:112) (cid:112)
MSE(x,y)= ( PSD (x)− PSD (y))2+
k k
k
(cid:112)
2 PSD (x)PSD (y)(1−Coh (x,y)). (5) k k k
Then,weseektobreaktheinteractionbetweenthespectral
6h
24h amplitudes and coherence contained in the second term
48h of (5). One option would be to fix the role of x as a
72h trialpredictionandyastheverifyinganalysisandreplace
(cid:112)
PSD (x)PSD (y) by PSD (y), but the symmetry of
k k k
thelossfunctioncanberetainedbywriting:
Figure2.Amplituderatio(solid)andcoherence(dashed)forthe
(cid:88) (cid:112) (cid:112)
sphericalharmonicmodewithtotalwavenumber100fortempera- AMSE(x,y)= ( PSD k (x)− PSD k (y))2+
tureat850hPaduringthetrainingofa1°versionoftheGraphCast k
modelwithanMSElossfunction.Attop,valuesfor6hleadtime 2max(PSD (x),PSD (y))(1−Coh (x,y)). (6)
k k k
duringthesingle-steppre-trainingphaseandatbottom, values
for6h–72hduringtheforecastrollout(batches300,000–311,000, AMSEisnowanadjustedmeansquarederror,whichcan
incrementingonestepevery1,000batches). actasadrop-inreplacementduringmodeltraining. Likeits
unmodifiedcounterpart,AMSEiszeroifandonlyifx=y,
• Data-driven models with conventional architectures
andithasthesameTaylorexpansion(inx)aboutx = y.
learntosmoothfinescales(reducingthepowerspectral
Thegradientsof−AMSE(x,y)withrespecttox(thatis,
density)morequicklythantheylearntopredictthem
minimizing AMSE) will always point in the direction of
(increasingcoherence).
increasedcoherence(Coh (x,y)→1)andacorrectspec-
k
tral magnitude (PSD (x) → PSD (y)), even if physical
Thisisillustratedinfigure2, whichshowstheamplitude k k
limitstopredictabilityimposeapracticallimittocoherence.
ratio(squarerootofpowerspectraldensityratio)andcoher-
AMSEretainstheunitsofMSEandhasasimilarmagnitude,
encefortotalwavenumber100(wavelengthabout400km)
butitisnolongerapropermetricbecauseitdoesnotsatisfy
betweenpredictionsofthetemperaturefieldatthe850hPa
thetriangleinequality.
levelandthegroundtruth,fora1°versionofGraphCastdur-
ingtrainingwiththecurriculumofLametal.(2023). After Unlikethemixoffilteredandspectrallossfunctionsusedby
arapidadjustmentfrominitiallyrandomoutputs,theampli- NeuralGCM,(6)isparameter-free,requiringnoselection
tuderatioandcoherencecloselytrackeachother,withan ofcutoffscalesorscaledadditionofqualitativelydifferent
initialsmoothingfollowedbyagradualbutpartialsharpen- terms. A parameter could be added to (6) to change the
ingasthemodellearnstopredictthisscale(withincreasing relative weights of its two terms, but that was not neces-
coherence). Whentrainingisextendedautoregressivelyto saryinthiswork. AppendixAcontemplatesextendingthis
12steps(72hforecasts),smoothingincreasesatlongerlead frameworktomaximumlikelihoodestimation.
timesastheforecastlengthincreases.
Equation6isdefinedforasingletwo-dimensionalvariable,
butGraphCastproducesseveraloutputspergridpoint.Inthe
2.3.SpectrallyAdjustedMeanSquaredError
¼°,13-levelversionofthemodelconsideredhere,thereare
Thissmoothingisundesirable. Itmakestheproducedfore- sixvariables(geopotential,temperature,specifichumidity,
castslessrealistic,anditcomplicatesmodelcomparisons. twocomponentsofhorizontalwind,andverticalwind)pro-
Lametal.(2023)performsextensiveverificationunderan ducedateachof13atmosphericlevelsplusfivevariables
“optimalblurring”modeltoshowthatthepurportedforecast (2-metertemperature,twocomponentsof10-mhorizontal
power of GraphCast is not just an artifact of its smooth- wind,meansealevelpressure,and6h-accumulatedprecipi-
ing,andmorestraightforwardverificationmethodologies tation)atthesurface. Thisworkfollowsequation(A.19)of
suchasthatofRaspetal.(2024)mayconflatetheeffects Lametal.(2023)byaggregatingeachvariable’serror(MSE
ofmore-optimalsmoothingwithforecastskillevenwhen there,AMSEhere)withaper-variableweight,levelweight-
evaluating at reduced resolution. It would instead be far ing proportional to the pressure level, and normalization
4

---

# Page 5

Length scale (km)
Table1.Fine-tuning curriculum for the ¼°/13-level version of 4000 1250 444 160100 55
GraphCasttrainedforthisstudy, includingthepeakandtermi-
nallearningrates(LR)ofthecosineannealingscheduleusedat 1.0
eachstage.Thebatchsizewas8throughout,andeachstagehada
warm-upperiodof64batches. 0.5
0.0
Length Batches Peak/EndLR GPUTime
1step(6h) 25,000 2.5·10−5/1.25·10−7 7.7d
2steps(12h) 2,500 2.5·10−6/7.5·10−8 2.2d
4steps(24h) 2,500 2.5·10−6/7.5·10−8 4.3d
8steps(48h) 1,250 2.5·10−6/7.5·10−8 4.6d
12steps(72h) 1,250 2.5·10−6/7.5·10−8 7.4d
ofthedisparateunitsbyaper-variable,per-levelstandard
deviation.
2.4.Fine-TuningMethodology
Wedemonstratetheefficacyofthislossfunctionusinga¼°,
13-level version of GraphCast. Based on the observation
above that the model tends to rapidly adjust its per-scale
smoothing to match its coherence, we treat this as a fine-
tuningprocessandbeginwiththe“operational”checkpoint
providedbyLametal.(2024),whichispubliclyavailable
underaCreativeCommonslicense.
Ourfine-tuningmethodologyissummarizedintable1,and
theoverallapproachisinspiredbySubich(2024). While
the baseline model checkpoint was trained over 72h (12
autoregressive steps of 6h each), in earlier testing at 1°
wefounditbettertobeginthefine-tuningwithsingle-step
forecastsandincreasetheforecastlengthinstages. Training
oversinglestepsisbothfasterperstepandsupportshigher
learningrates.
The other training hyperparameters, including AdamW
(Loshchilov&Hutter,2019)hyperparametersettingsand
per-variable, per-level loss weightings were identical to
thosedescribedbyLametal.(2023).
The13-levelGraphCastcheckpointthatformsthebaseof
ourfine-tunedmodelwasoriginallytrainedontheERA5
reanalysis from 1979–2017, then itself fine-tuned on the
initialconditionsusedforthecontemporaneousHRES(IFS)
modelfromECMWFover2016–2021. Weusedthislatter
datasetandtrainingperiodinourwork,anditisavailable
from Rasp et al. (2024) as the “HRES-fc0” dataset. As
describedinLametal.(2023),wesupplementedtheHRES
datawiththeaccumulatedprecipitationfieldfromtheERA5
reanalysisoverthetrainingperiod,sinceaninitialconditions
datasethasnoaccumulatedprecipitationbydefinition. The
equivalentdataforcalendaryear2022isalsoavailable,and
weusedthisperiodformodelevaluation.
We fine-tuned our model on 1-2 nodes of a cluster con-
h6
Control
AMSE AR12
AMSE AR1
1.0
0.5
0.0
h021
Amplitude ratio
Coherence
1.0
0.5
0.0
0 10 32 90 250400 720
Total wavenumber
h042
Figure3.Amplituderatio(solid)andcoherence(dashed)forall
output variables and levels, weighted using the variable/level
weightsinthelossfunction,forthecontrolmodelandthiswork
afterthe1-steptrainingandaftercompletefine-tuning. Top: 6h
leadtime,middle:120h(5d)leadtime,bottom:240h(10d)lead
time.Thedashedlineisplacedwhereamodelwouldunderrepre-
sentthepowerspectraldensityby25%.
taining4NVidiaA10040GiBGPUspernode,usingdata
parallelismwiththebatchsplitacrossGPUsandthegradi-
entsaccumulatedviaMPI.Overall,thefine-tuningprocess
tookabout26.2GPU-days. Lametal.(2023)doesnotdis-
closethetotaltrainingtimerequiredtoproducethemodel
checkpointfromscratch,butothermodelsofsimilarsize
(Bonevetal.,2023;Langetal.,2024a;Bietal.,2023)report
trainingtimesofabout1GPU-yearusingsimilarhardware.
3.Results
Thefine-tunedmodelisevaluatedagainstthecontrol(un-
modified)modelovercalendaryear2022usingtheHRES
datasetforinitializationandasgroundtruthunlessother-
wise specified. As reported in Lam et al. (2023) and is
typicalinotherdeterministicdata-drivenmodels,forecast
performanceatlongerleadtimesimproveswhenthemodel
isautoregressivelytrainedovermultiplesteps,andthefully-
tuned model (trained over 12 forecast steps and labelled
“AMSEAR12”inthefiguresanddiscussionbelow)iscon-
sideredtheprimarymodelforevaluation.
Sincemulti-steptrainingalsotendstocausebothfine-scale
smoothing and a loss of variability in ensemble settings,
theserespectiveevaluations(sections3.1and3.2)willalso
includethemodelcheckpointcreatedafterjustsingle-step
5

---

# Page 6

fine-tuning,denoted“AMSEAR1.” The AMSE AR1 model shows the same qualitative be-
haviourbutgeneratesthis“noise”morestrongly,leadingto
3.1.EffectiveResolution areducedeffectiveresolutionofabout450km(wavenumber
90). Theforecastsproducedbythisversionofthemodelare
Conventional,physics-basedNWPmodelsarewidelyun-
lesscoherentwiththeanalysis,showingareducedforecast
derstoodtohaveaneffectiveresolutionthatiscoarserthan
skillatallscalesforlongerforecasts.
themodel’snativegridresolution. Limitstoeffectivereso-
lutioncomefromthelimitedfidelityofspatialortemporal Forillustration,appendixB.2showsamplitudespectrafor
discretization,fromartificialdiffusionordampingusedto selectvariablesatvariousleadtimes,withoutnormalizing
stabilize a model, and from sub-grid processes (such as by the spectralmagnitude of the ground truth. Appendix
turbulence)thatmustbeimperfectlyestimatedratherthan B.5 discusses the effective resolution of the model when
directlymodelled. Amodelbehavesunrealisticallyatscales trained with either mean squared error or mean absolute
finerthanitseffectiveresolution,typicallyprovidinginsuffi- (L1)error.
cientvariabilityandtoo-smoothsolutions.
3.2.LaggedEnsembleVerification
Deterministic data-driven NWP models do not have the
same underlying numerical issues that result in reduc- The observation that AMSE-based fine-tuning provides
tions to effective resolution, but the smoothing produced sharpforecastsisencouraging,butthataloneisnotenough
by training with an MSE-based loss function acts in a to demonstrate utility. The model might have learned to
very similar way. Figure 3 shows the amplitude ratio matchitsexpectedvariancebygeneratingquasi-staticnoise
(cid:113)
( PSD (x)PSD−1(y)) and coherence (Coh (x,y)) be- thatdoesnotsufficientlydependonthesurroundingflow,
k k k forexample. Theidealwaytomeasurethissortofforecast
tween each of the GraphCast models and the verifying
skill is in an ensemble setting, where the chaotic nature
analysisovercalendaryear2022. Tocomputeacombined
of the atmosphere is accounted for by evaluating the full
curve despite the many per-gridpoint values predicted by
distributionofplausibleoutputsgivenaninitialcondition.
themodel,thestatisticsforeachseparatevariablearecom-
binedusingthesamevariableandlevelweightingusedin Developmentofafullensemblesystemiswellbeyondthe
themodel’slossfunction2. scopeofthiswork,butBrenowitzetal.(2025)providesa
proceduretoevaluateadeterministicmodelusinganensem-
The control model significantly smooths fine scales even
blegeneratedfromtime-separatedinitialconditions. The
afterasingle6-hourforecaststep,andthatsmoothingin-
central idea of this method is that predictions initialized
creaseswiththeforecastleadtime. Ifwesomewhatarbitrar-
atdifferenttimesshoulddiverge,soseveralconsecutively-
ilydrawthelineofeffectiveresolutionatthepointwhere
initializedforecaststhatareallvalidatasharedtimeforman
themodelhaslost25%oftheper-wavenumberenergy(cor-
ad-hocensemble,withouttheneedforanauxiliarymethod
respondingtoaratioofpowerspectraldensitiesof0.75or
√
ofdefininganensembleofinitialconditions.
anamplituderatioof 0.75),the5-daypredictionsofthe
controlmodelreachthatcutoffatwavenumber32, corre- Thisapproachisimplementedhere,usingforecastsinitial-
spondingtooscillationswithawavelengthofabout1250 izedat12-hourlyintervalsin2022andevaluatedfrom10
km. Smallchangesinthetargetamplituderatiowillresult January20220:00UTCto31December202212:00UTC.
insmallchangestothederivedeffectiveresolution. Eachsetofnineconsecutivelyinitializedforecasts(span-
ningfourdaysfrombeginningtoend)formsanensemble,
Themodelsfine-tunedinthisworkdonotshowthistypeof
andtheensemble’snotionalleadtimeisthatofitscentral
fine-scaledissipation. TheAMSEAR12modelhasasmall
member.
amountofsmoothingatmoderatescales,butthevariability
recoversagainatfinerscales,andadissipation-baseddefi- TheprimaryevaluationmetricsaretheCRPS,ensembleroot
nitionofeffectiveresolutionwouldbeextremelysensitive meansquarederror(eRMSE),andspread/errorratio,with
tothecutoffvalue. Instead,weobservethatforlongerfore- definitionsgiveninappendixB.4.Foranoperationalensem-
caststhemodelhasmoreenergyatsmallscalesthaninthe ble,aspread/errorratiocloseto1isconsideredideal,but
ground-truthdataset,suggestinga“noise-based”definition thatisconfoundedherebecausethemembersofalagged
of effective resolution. For long forecasts, the amplitude ensemble are not statistically interchangeable. Since de-
ratiorisesabove1aroundwavenumber250,givinganef- terministic data-driven NWP models are underdispersive,
fectiveresolutionofabout160km. however,alargerspread/errorratioisgenerallybetter.
2Normalizationofthedisparatevariablesbystandarddeviation Figure4showstheevolutionofthesestatisticsversuslead
wasnotrequiredhere,sincetheamplituderatioandcoherenceare timeforaselectionofvariablesandlevels,andmoredetailed
alreadydimensionless.
evaluation of CRPS and eRMSE are shown in figures 11
and12. TheAMSEAR12modelshowsconsistentimprove-
6

---

# Page 7

200
150
100
50
)
(
SPRC
z500 (m2 s 2)
Control
AMSE AR12
400
200
)
(
ESMRe
AMSE AR1
1.3
1.2
1.1
1.0
3 4 5 6 7 8
Lead time (d)
)1
( rorre/daerpS
t850 (K) q700 (g kg 1) 2t (K)
1.0
1.00
0.6 0.8
0.75
0.6
0.50 0.4
0.4
1.50 2.0
2.0
1.25
1.5
1.5
1.00
1.0 1.0
0.75
0.9
0.8
0.9 0.8
0.7 0.7
0.8
0.6
0.6
3 4 5 6 7 8 3 4 5 6 7 8 3 4 5 6 7 8
Lead time (d) Lead time (d) Lead time (d)
Figure4.Laggedensemblestatisticsforgeopotential(z)at500hPa,temperature(t)at850hPa,specifichumidity(q)at700hPa,and
2-metertemperature(2t)fromlefttoright.ThestatisticsaretheCRPS,rootmeansquarederroroftheensemblemean,andspread-error
ratio,fromtoptobottom.
ments to the CRPS while the eRMSE sees little change, versionproduceareasonable5-daypredictionofthestorm’s
indicating that the fine tuning process produces a better- location(withinabout125km),butthecontrolversionof
calibrated (more dispersive) ensemble without degrading GraphCastpredictsanunrealisticallyweakstorm.
overallpredictiveperformance.
Morequantitatively,figure6showsthemeanintensityand
While the AMSE AR1 model shows greater ensemble mean absolute position errors for tropical cyclones over
spread, the less skillful forecast results in a significantly 20June–19September2022initializations,usingthealgo-
reducedCRPS.However, unliketheresultsofBrenowitz rithmofZadraetal.(2014)tocompareagainsttheInterna-
etal.(2025),thespread/errorratiooftheAR1andAR12 tionalBestTrackArchiveforClimateStewardshipdatabase
models converge for most variables at longer lead times, (Knappetal.,2010). Comparedtotheseobservations,even
suggestingthatmulti-steptraininginthisframeworkdoes the HRES data is imperfect and shows a weak-intensity
notcauseacollapseofvariabilityinanensemblesetting. bias. The control model has a larger weak-intensity bias
thatincreaseswithleadtime,buttheAMSEAR12model
3.3.HurricanePredictionandExtremeWeather retainsthequalityoftheHRESdataset. Thestormlocation
predictionsbetweenthecontrolandAMSEAR12models
Theeffectofimprovedeffectiveresolutionismoststrongly
areequivalent.
apparentinthepredictionoflocalextremes,andfewweather
eventsaremoreextremethantropicalcyclones. Extremeweatherincludesmorethantropicalcyclones,and
appendixB.3discussesquantile-quantilepredictionsofsur-
Data-drivenNWPmodelslikeGraphCastimprovepredic-
facewindspeedandtemperature,validatedagainststation
tionsofhurricanetracksrelativetoconventionalNWPmod-
observations. BoththecontrolmodelandAMSEAR12pro-
els(seeforexamplefigure3AofLametal.(2023)). Since
ducerealistictemperatureextremes,buttheAMSEAR12
stormsareguidedbylarge-scale“steeringflows”thathave
model provides more realistic predictions of wind-speed
naturalscalesofthousandsofkilometers,thesepredictions
extremes.
ofstormpositionarerelativelyunaffectedbythemodels’
limitedeffectiveresolutionsbutbenefitfromimprovements
4.Discussion&Limitations
inlarge-scaleforecastskill. However,cyclonesthemselves
arecomparativelysmall,andpredictionsofthestorminten-
Using the mean squared error as a model loss function
sityaresignificantlyaffectedbyMSE-inducedsmoothing.
asks the model to average away unpredictable scales. In
Figure5depictsthissituationforHurricaneIan,themost weatherforecasting,theunpredictablescalesaregenerally
intenseAtlantictropicalcycloneofthe2022season. Both thesmallerscalesthatcarryinformationaboutlocalvari-
the control version of GraphCast and the AMSE AR12 ance,andthisaveragingprocessleadstodata-drivenweather
forecaststhatarefarsmootherthanthegridresolutionwould
7

---

# Page 8

28°N
40.0
26°N
24°N 34.5
28°N
26°N 29.0
24°N
28°N
23.5
26°N
18.0
24°N
85°W 83°W 81°W
)s/m(
deeps
dniw
m01
Figure6.Predictionsoftropicalcycloneintensity((a),meanmaxi-
mumsurfacewindspeed;(b)meanminimumcentralpressure)and
meanabsolutepositionerror(c)forforecastsinitialized20June–
19September2022.Orangesquaresshowstatisticallysignificant
differencesbetweentheAMSEAR12andcontrolpredictions.
SincetheAMSElossfunction(6)iszeroifandonlyifthe
Figure5.10mwindspeedandmeansealevelpressureforHurri- predictedfieldmatchesthegroundtruth,itmaybeuseful
caneIan,28Sept2022at12hUTC.Top:HRESdataat¼°,middle:
throughout model training rather than just during a fine-
5dforecastproducedbythecontrolGraphCastmodel,bottom:the
tuningpass. However,athoroughtestofthisproposition
modelafter12-stepfine-tuningwithAMSE.
would require a considerable computational budget, so it
is left for future work. Use of the AMSE loss function
suggest. throughout the training process might improve the coher-
enceoffine-scalepredictionbyallowingthemodeltospend
Thisisnotapropertyinherenttodata-drivenNWP.Theal-
moreofitstrainingtime“seeing”thesemodes,butonthe
ternatelossfunctionbasedon(6)usesaspectraltransform
otherhandthecoherence-dependentsmoothingencouraged
to separate the loss attributable to amplitude error from
bytheMSElossfunction(figure2)mightactasanimplicit
thatattributabletodecorrelation,encouragingthemodelto
regularizationthatsmoothsthemodel’sgradientsandspeeds
reproducearealisticspectrumevenifitcan’tmakeanac-
uptrainingoverall.
curateprediction. Whenappliedtothe¼°,13-levelversion
ofGraphCastwithanabbreviatedfine-tuningprocess,we
4.1.EffectiveResolution
recoveramodelthathasamuchfinereffectiveresolution,
hasimprovedCRPS-basedverificationinalaggedensemble The ultimate conclusion of this work is that the AMSE-
setting,andfixestheweakintensitybiasinthepredictionof based error measure improves the effective resolution of
tropicalcyclones. NWPweathermodels,butthephrase“effectiveresolution”
mustalwaysbeaccompaniedbythequestion,“effectiveat
When fine-tuned autoregressively over multiple forecast
what?”
steps,themodelsuffersfromasmallamountofsmoothing
atmesoscales(intermediatescales). Wespeculatethatthis Wechosetodefineaneffectiveresolutionbasedonsmooth-
isbecausesuchautoregressivetraininghastwoobjectives: ing of fine scales, since a model that simply doesn’t rep-
forecastsareaskedbothtobeaccurate(andthussharp,per resentascalecannoteffectivelymodelit. However,other
(6))andtobegoodinitialconditionsforthenextforecast definitionsexistintheliterature,andusersofthesemodels
step.Thislattergoalisimplicit,anditisnotdirectlyaffected shouldkeeptheirultimategoalsinmind. Forexample,Kent
by the loss function used in training. Future work will etal.(2014)studiesvariousdiscretizationschemesfornu-
considertheuseofareplaybufferintraining(likethatof mericalpartialdifferentialequationsunderbothdiffusion
Chenetal.(2023))toseeiflong-rangeforecastskillmight (smoothing)anddispersion(wavepropagation)definitions
beretainedwithevenbetterpredictionofamplitudes. ofeffectiveresolution.
8

---

# Page 9

4.2.AlternativeGrids trajectory,inadditiontothewhole-ensembleoptimization
encouragedbyCRPS-likeensembletraining.
Passing from equation (2) to (4) makes use of Parseval’s
theoremtogiveanexactrelationshipbetweenthespatially-
CodeandDataAvailability
definedmeansquarederrorandtheequivalentinthespec-
tral representation. Implementing this in a training cycle
An implementation of the AMSE error function and the
requiresfastcomputationofsphericalharmonictransforms.
code used to train GraphCast for this work are available
Thisissimpleenoughforgloballatitude/longitudegrids,but
at https://github.com/csubich/graphcast/
itmightbedifficultforlocal-areamodelswithoutaregular
tree/amse under the Apache 2.0 license. The
globalgridstructure.
fine-tuned checkpoints produced for this study are
Inthesecases,wethinkthatthebasicintuitionbehind(6) available at https://huggingface.co/csubich/
mightstillapplythroughothermultiscaledecompositions graphcast_amseundertheCC-BY-ND-SA4.0license,
suchaswaveletlifting(Sweldens&Schro¨der,2000),pro- asderivativeworksoftheDeepMind“graphcast-operational”
videdsuitableequivalentstoscale-dependentvarianceand checkpoint.
correlationcouldbefound. Themultiscaledecomposition
iscriticalinsomeform,however,sincethemethodtakesad- Acknowledgements
vantageoftheapproximateindependenceofscale-separated
modes. Withoutsuchadecomposition(e.g. applyingthe The authors would like to thank Charlie He´bert-Pinard,
adjustmentof(6)globally,withouttheharmonictransform), Vikram Khade, and Hugo Vandenbroucke-Menu of the
themodelmightbeableto“coverup”alackoffine-scale Canadian Centre for Meteorological and Environmental
variabilitybyover-emphasizingcoarserscales. Predictionforaccesstothe1°-trainedversionofGraphCast
usedtoproducetheresultsoffigure2.
4.3.ApplicationstoOtherDomains
ImpactStatement
AMSEisanaturalerrorfunctionforweatherpredictionbe-
causethespectraldecompositionisphysicallymeaningful
Accurateweatherforecastsareavitalpublicservice,andits
and relatively stable over time. A partially incorrect but
benefitsaredisproportionatelyconcentratedintheextremes.
realisticpredictionofweatherat2000kmscaleswouldnot
Accurateforecastsofextremeweathersuchastropicalcy-
significantly change the amount of energy present at 100
clonessavelives. Ononehand,thismeansthatweshould
km scales, just its relative location. The goal of a deter-
beeagertodevelopimprovementstoweatherforecasting
ministicforecastistobephysicallyplausible,andacorrect
systems,butontheotherhanditmeansthatweshouldbe
predictionofspectralamplitudesisanecessarycondition
very careful not to just “chase scores,” confusing what’s
forphysicalplausibility.
easytocalculatewithwhat’strulyimportant.
Themethodcanbemechanicallyappliedwheneveraspec-
Thisworkcontributestothisfieldbyintroducingawayto
traldecompositionispossible,butadditionalvalueisonly
makedata-drivenweatherforecastingmorerealistic,with
likelywhenasub-aggregationofthatspectrumismeaning-
variabilityatmoderateandfinescalesthatismuchcloser
ful. Thisismostobviouslypossibleinotherareasoffluid
toreality. Thisimprovesvariousprobabilisticscoresand
dynamics,particularlythemodellingofturbulentflows. In
predictions of tropical cyclone intensity, but this is not a
thatdomain,Chakrabortyetal.(2025)developedabinned
guaranteeofcompletephysicalplausibility.Inparticular,we
spectrallossfunction(onaplanardomain)thatisreminis-
havenotyetshownthattheseforecastsarebetter-behaved
centoftheamplitude-onlycomponentof(6),butitdiscards
“outofdistribution,”suchaswhensimulatingpossiblefuture
thephaseinformation. Weareoptimisticthatintegrating
climatepaths.
thespectralcorrelationalongthelinesofAMSEwillmake
suchmodelsmorerobust. Operational weather centres are very diligent about per-
formingrigorousevaluationofmodelsbeforemakingthem
operational,andwehopethatthisworkcanhelpeasethe
4.4.ApplicationstoEnsembleModelling
pathtowardstheadoptionofbetter-performing,data-driven
Weareparticularlyencouragedbythebeneficialimpactthat forecastingsystemsinthenearfuture.
AMSE-basedtraininghasonthespreadofforecastsinan
ensemblesetting. Withoutanydedicatedensemble-based
References
trainingweendupwithamodelthatnonethelessproduces
amorerealisticspreadofforecasts. Infuturework,wehope Allen,A.,Markou,S.,Tebbutt,W.,Requeima,J.,Bruinsma,
tousethislossfunctionasabasisforanensembleforecast W.P.,Andersson,T.R.,Herzog,M.,Lane,N.D.,Chantry,
whereeachindividualensemblememberproducesarealistic M., Hosking, J.S., andTurner, R.E. End-to-enddata-
9

---

# Page 10

drivenweatherprediction. Nature,pp.1–8,March2025. Gneiting,T.andRaftery,A.E.StrictlyProperScoringRules,
ISSN1476-4687. doi: 10.1038/s41586-025-08897-0. Prediction, and Estimation. Journal of the American
StatisticalAssociation,102(477):359–378,March2007.
Bauer, P. What if? Numerical weather prediction at the
ISSN0162-1459. doi: 10.1198/016214506000001437.
crossroads. JournaloftheEuropeanMeteorologicalSo-
ciety,1:100002,December2024. ISSN2950-6301. doi: Han,T.,Guo,S.,Ling,F.,Chen,K.,Gong,J.,Luo,J.,Gu,J.,
10.1016/j.jemets.2024.100002. Dai,K.,Ouyang,W.,andBai,L. FengWu-GHR:Learn-
ingtheKilometer-scaleMedium-rangeGlobalWeather
Berner,J.,Fossell,K.R.,Ha,S.-Y.,Hacker,J.P.,andSny-
Forecasting, January 2024. URL http://arxiv.
der, C. Increasing the Skill of Probabilistic Forecasts:
org/abs/2402.00059. arXiv:2402.00059[physics].
UnderstandingPerformanceImprovementsfromModel-
ErrorRepresentations. MonthlyWeatherReview,143(4): Hersbach,H.,Bell,B.,Berrisford,P.,Hirahara,S.,Hora´nyi,
1295–1320,April2015. ISSN1520-0493,0027-0644. A.,Mun˜oz-Sabater,J.,Nicolas,J.,Peubey,C.,Radu,R.,
Schepers,D.,Simmons,A.,Soci,C.,Abdalla,S.,Abel-
Bi, K., Xie, L., Zhang, H., Chen, X., Gu, X., and Tian,
lan, X., Balsamo, G., Bechtold, P., Biavati, G., Bidlot,
Q. Accurate medium-range global weather forecast-
J., Bonavita, M., De Chiara, G., Dahlgren, P., Dee, D.,
ing with 3D neural networks. Nature, 619(7970):533–
Diamantakis,M.,Dragani,R.,Flemming,J.,Forbes,R.,
538, July 2023. ISSN 1476-4687. doi: 10.1038/
Fuentes,M.,Geer,A.,Haimberger,L.,Healy,S.,Hogan,
s41586-023-06185-3.
R.J.,Ho´lm,E.,Janiskova´,M.,Keeley,S.,Laloyaux,P.,
Bonev, B., Kurth, T., Hundt, C., Pathak, J., Baust, M., Lopez,P.,Lupu,C.,Radnoti,G.,deRosnay,P.,Rozum,I.,
Kashinath, K., andAnandkumar, A. SphericalFourier Vamborg,F.,Villaume,S.,andThe´paut,J.-N. TheERA5
Neural Operators: Learning Stable Dynamics on the global reanalysis. Quarterly Journal of the Royal Me-
Sphere. InProceedingsofthe40thInternationalConfer- teorologicalSociety,146(730):1999–2049,2020. ISSN
enceonMachineLearning,volume202,pp.2806–2823. 1477-870X. doi: 10.1002/qj.3803.
PMLR,July2023. ISSN:2640-3498.
Hoffman,R.N.,Liu,Z.,Louis,J.-F.,andGrassoti,C.Distor-
Brenowitz, N. D., Cohen, Y., Pathak, J., Mahesh, A., tionRepresentationofForecastErrors. MonthlyWeather
Bonev,B.,Kurth,T.,Durran,D.R.,Harrington,P.,and Review, 123(9):2758–2770, September 1995. ISSN
Pritchard, M. S. A Practical Probabilistic Benchmark 1520-0493,0027-0644. doi: 10.1175/1520-0493(1995)
forAIWeatherModels. GeophysicalResearchLetters, 123⟨2758:DROFE⟩2.0.CO;2.
52(7):e2024GL113656, 2025. ISSN 1944-8007. doi:
Husain,S.Z.,Separovic,L.,Caron,J.-F.,Aider,R.,Buehner,
10.1029/2024GL113656.
M., Chamberland, S., Lapalme, E., McTaggart-Cowan,
Chakraborty, D., Mohan, A. T., and Maulik, R. Binned R.,Subich,C.,Vaillancourt,P.,Yang,J.,andZadra,A.
SpectralPowerLossforImprovedPredictionofChaotic Leveraging data-driven weather models for improving
Systems,February2025. URLhttp://arxiv.org/ numerical weather prediction skill through large-scale
abs/2502.00472. arXiv:2502.00472[cs]. spectral nudging, July 2024. URL http://arxiv.
org/abs/2407.06100. arXiv:2407.06100[physics].
Chen, K., Han, T., Gong, J., Bai, L., Ling, F., Luo, J.-J.,
Chen,X.,Ma,L.,Zhang,T.,Su,R.,Ci,Y.,Li,B.,Yang, Keisler, R. ForecastingGlobalWeatherwithGraphNeu-
X.,andOuyang,W.FengWu:PushingtheSkillfulGlobal ral Networks, February 2022. URL http://arxiv.
Medium-rangeWeatherForecastbeyond10DaysLead, org/abs/2202.07575. arXiv:2202.07575[physics].
April2023. URLhttp://arxiv.org/abs/2304.
02948. arXiv:2304.02948[physics]. Kent, J., Whitehead, J. P., Jablonowski, C., and Rood,
R.B. Determiningtheeffectiveresolutionofadvection
Couairon,G.,Singh,R.,Charantonis,A.,Lessig,C.,and schemes.PartI:Dispersionanalysis. JournalofCompu-
Monteleoni, C. ArchesWeather&ArchesWeatherGen: tationalPhysics,278:485–496,December2014. ISSN
a deterministic and generative model for efficient ML
0021-9991. doi: 10.1016/j.jcp.2014.01.043.
weather forecasting, December 2024. URL http://
arxiv.org/abs/2412.12971. arXiv:2412.12971 Knapp, K. R., Kruk, M. C., Levinson, D. H., Diamond,
[cs]. H.J.,andNeumann,C.J. TheInternationalBestTrack
Archive for Climate Stewardship (IBTrACS). Bulletin
Ebert,E.,Wilson,L.,Weigel,A.,Mittermaier,M.,Nurmi,
oftheAmericanMeteorologicalSociety,91(3):363–376,
P., Gill, P., Go¨ber, M., Joslyn, S., Brown, B., Fowler,
March2010. doi: 10.1175/2009BAMS2755.1.
T.,andWatkins,A. Progressandchallengesinforecast
verification.MeteorologicalApplications,20(2):130–139, Kochkov,D.,Yuval,J.,Langmore,I.,Norgaard,P.,Smith,
2013. ISSN1469-8080. doi: 10.1002/met.1392. J.,Mooers,G.,Klo¨wer,M.,Lottes,J.,Rasp,S.,Du¨ben,
10

---

# Page 11

P.,Hatfield,S.,Battaglia,P.,Sanchez-Gonzalez,A.,Will- Leutbecher, M. and Palmer, T. N. Ensemble forecasting.
son, M., Brenner, M.P., andHoyer, S. Neuralgeneral Journal of Computational Physics, 227(7):3515–3539,
circulationmodelsforweatherandclimate. Nature,632 March2008. ISSN0021-9991. doi: 10.1016/j.jcp.2007.
(8027):1060–1066,August2024. ISSN1476-4687. doi: 02.014.
10.1038/s41586-024-07744-y.
Li,L.,Carver,R.,Lopez-Gomez,I.,Sha,F.,andAnderson,J.
Kurth,T.,Subramanian,S.,Harrington,P.,Pathak,J.,Mar- Generativeemulationofweatherforecastensembleswith
dani,M.,Hall,D.,Miele,A.,Kashinath,K.,andAnand- diffusionmodels. ScienceAdvances,10(13):eadk4489,
kumar, A. FourCastNet: Accelerating Global High- March2024. doi: 10.1126/sciadv.adk4489.
ResolutionWeatherForecastingUsingAdaptiveFourier
Neural Operators. In Proceedings of the Platform for Lippe,P.,Veeling,B.,Perdikaris,P.,Turner,R.,andBrand-
AdvancedScientificComputingConference,PASC’23, stetter,J. PDE-Refiner: AchievingAccurateLongRoll-
pp.1–11,NewYork,NY,USA,June2023.Association outswithNeuralPDESolvers. AdvancesinNeuralInfor-
forComputingMachinery. ISBN9798400701900. doi: mationProcessingSystems,36:67398–67433,December
10.1145/3592979.3593412. 2023.
Lagerquist,R.andEbert-Uphoff,I.CanWeIntegrateSpatial
Loshchilov,I.andHutter,F.DecoupledWeightDecayRegu-
VerificationMethodsintoNeuralNetworkLossFunctions larization,January2019. URLhttp://arxiv.org/
forAtmosphericScience? ArtificialIntelligenceforthe abs/1711.05101. arXiv:1711.05101[cs,math].
EarthSystems,1(4),November2022. ISSN2769-7525.
doi: 10.1175/AIES-D-22-0021.1. Mahesh, A., Collins, W., Bonev, B., Brenowitz, N., Co-
hen,Y.,Elms,J.,Harrington,P.,Kashinath,K.,Kurth,T.,
Lam,R.,Sanchez-Gonzalez,A.,Willson,M.,Wirnsberger,
North, J., OBrien, T., Pritchard, M., Pruitt, D., Risser,
P.,Fortunato,M.,Alet,F.,Ravuri,S.,Ewalds,T.,Eaton-
M., Subramanian, S., and Willard, J. Huge Ensem-
Rosen,Z.,Hu,W.,Merose,A.,Hoyer,S.,Holland,G.,
bles Part I: Design of Ensemble Weather Forecasts us-
Vinyals, O., Stott, J., Pritzel, A., Mohamed, S., and
ing Spherical Fourier Neural Operators, August 2024.
Battaglia, P. Learning skillful medium-range global
arXiv:2408.03100[physics]version: 1.
weatherforecasting. Science,382(6677):1416–1421,De-
cember2023. doi: 10.1126/science.adi2336.
NOAA. GraphCast with GFS input, 2024. URL
https://registry.opendata.aws/
Lam, R., Sanchez-Gonzalez, A., Willson, M., Wirns-
noaa-nws-graphcastgfs-pds/.
berger, P., Fortunato, M., Alet, F., Ravuri, S., Ewalds,
T., Eaton-Rosen, Z., Hu, W., Merose, A., Hoyer,
Palmer, T. N. A nonlinear dynamical perspective on
S., Holland, G., Vinyals, O., Stott, J., Pritzel, A.,
modelerror:Aproposalfornon-localstochastic-dynamic
Mohamed, S., and Battaglia, P. GraphCast GitHub
parametrizationinweatherandclimatepredictionmod-
repository, July 2024. URL https://github.
els. QuarterlyJournaloftheRoyalMeteorologicalSo-
com/google-deepmind/graphcast. original-
ciety,127(572):279–304,2001. ISSN1477-870X. doi:
date: 2023-07-14T11:07:57Z.
10.1002/qj.49712757202.
Lang,S.,Alexe,M.,Chantry,M.,Dramsch,J.,Pinault,F.,
Raoult, B., Clare, M. C. A., Lessig, C., Maier-Gerber, Price,I.,Sanchez-Gonzalez,A.,Alet,F.,Andersson,T.R.,
M.,Magnusson,L.,Boualle`gue,Z.B.,Nemesio,A.P., El-Kadi,A.,Masters,D.,Ewalds,T.,Stott,J.,Mohamed,
Dueben,P.D.,Brown,A.,Pappenberger,F.,andRabier, S.,Battaglia,P.,Lam,R.,andWillson,M. Probabilistic
F. AIFS - ECMWF’s data-driven forecasting system, weatherforecastingwithmachinelearning. Nature,637
June2024a. URLhttp://arxiv.org/abs/2406. (8044):84–90, January 2025. ISSN 1476-4687. doi:
01465. arXiv:2406.01465[physics]. 10.1038/s41586-024-08252-9.
Lang, S., Alexe, M., Clare, M. C. A., Roberts, C., Ade- Rasp,S.,Hoyer,S.,Merose,A.,Langmore,I.,Battaglia,P.,
woyin,R.,Boualle`gue,Z.B.,Chantry,M.,Dramsch,J., Russell,T.,Sanchez-Gonzalez,A.,Yang,V.,Carver,R.,
Dueben,P.D.,Hahner,S.,Maciel,P.,Prieto-Nemesio,A., Agrawal,S.,Chantry,M.,BenBouallegue,Z.,Dueben,
O’Brien,C.,Pinault,F.,Polster,J.,Raoult,B.,Tietsche, P., Bromberg, C., Sisk, J., Barrington, L., Bell, A.,
S., and Leutbecher, M. AIFS-CRPS: Ensemble fore- and Sha, F. WeatherBench 2: A Benchmark for the
castingusingamodeltrainedwithalossfunctionbased Next Generation of Data-Driven Global Weather Mod-
on the Continuous Ranked Probability Score, Decem- els. Journal of Advances in Modeling Earth Systems,
ber 2024b. URL http://arxiv.org/abs/2412. 16(6):e2023MS004019, 2024. ISSN 1942-2466. doi:
15832. arXiv:2412.15832[physics]version: 1. 10.1029/2023MS004019.
11

---

# Page 12

Sadeghi Tabas, S., Wang, J., Lei, W., Row, M.,
Zhang, Z., Zhu, L., Peng, J., and Carley, J. R.
GFS-Powered Machine Learning Weather Prediction:
A Comparative Study on Training GraphCast with
NOAA’s GDAS Data for Global Weather Forecasts,
2025. URL https://repository.library.
noaa.gov/view/noaa/67485.
Slivinski,L.C.,Whitaker,J.S.,Frolov,S.,Smith,T.A.,and
Agarwal,N.AssimilatingObservedSurfacePressureInto
MLWeatherPredictionModels. GeophysicalResearch
Letters,52(6):e2024GL114396,2025. ISSN1944-8007.
doi: 10.1029/2024GL114396.
Subich, C. Efficient fine-tuning of 37-level GraphCast
with the Canadian global deterministic analysis, Au-
gust 2024. URL http://arxiv.org/abs/2408.
14587. arXiv:2408.14587[cs].
Sweldens,W.andSchro¨der,P. Buildingyourownwavelets
athome. InKlees,R.andHaagmans,R.(eds.),Wavelets
in the Geosciences, Lecture Notes in Earth Sciences,
pp.72–107.SpringerBerlinHeidelberg,Berlin,Heidel-
berg, 2000. ISBN 978-3-540-46590-4. doi: 10.1007/
BFb0011093.
To¨dter, J. and Ahrens, B. Generalization of the Igno-
rance Score: Continuous Ranked Version and Its De-
composition. Monthly Weather Review, 140(6):2005–
2017, June 2012. ISSN 1520-0493, 0027-0644. doi:
10.1175/MWR-D-11-00266.1.
Weyn, J. A., Durran, D. R., and Caruana, R. Improv-
ingData-DrivenGlobalWeatherPredictionUsingDeep
Convolutional Neural Networks on a Cubed Sphere.
Journal of Advances in Modeling Earth Systems, 12
(9):e2020MS002109, 2020. ISSN 1942-2466. doi:
10.1029/2020MS002109.
Zadra,A.,McTaggart-Cowan,R.,Vaillancourt,P.A.,Roch,
M., Be´lair, S., and Leduc, A.-M. Evaluation of Tropi-
calCyclonesintheCanadianGlobalModelingSystem:
SensitivitytoMoistProcessParameterization. Monthly
WeatherReview,142(3):1197–1220,March2014.
12

---

# Page 13

A.RelationshiptoMaximumLikelihoodEstimation
IndevelopingtheAMSElossfunction,thetransformationfromordinary,gridpoint-basedMSE(2)toitsspectraldefinition
withpowerspectraldensitiesandcoherence(5)isalgebraicinnature. ThebeneficialeffectoftheAMSElossfunction’s
separationofspectral-ampltiudeanddecoherencetermsarisesbecausetheunderlyingspectraldecompositionisphysically
meaningful. Atfineenoughscales,atmosphericdynamicsareincreasinglyrotationallysymmetricandposition-invariant,
withindividualspectralamplitudesthatlooklikedrawsfromaGaussiandistribution.
If we elevate this property from a fortunate coincidence to a simplifying assumption, we can treat the set of modes
correspondingtoaparticulartotalwavenumberasrandomvariablesandapplythemachineryofensembleverificationto
individual,deterministicforecasts. Thegoalofproducingrealisticforecastsdespitelimitedpredictabilityisconceptually
similartothegoalofmaximum-likelihoodestimation,soweconsiderheretheeffectofKullback-Leibler(KL)divergence
minimization. Inthemeteorologyliterature,theKLdivergenceisnamedthecontinuousignorancescore(To¨dter&Ahrens,
2012),anditissometimesusedforensembleverification.
Treatthemodescorrespondingtoasingletotalwavenumberkasadrawfroma2k−1-dimensionalnormalrandomvariable3
withmeanzeroandsomefinitestandarddeviation. Inthisinterpretation,theground-truthanalysisis:
Y =σ N2k−1(0,1). (7)
k Y
Theforecastisitselftakentobeanormalrandomvariable,butfollowingthepatternof(5)itispartiallycorrelatedtoY and
hasitsownstandarddeviation. Takethecorrelationtobeρandtheforecaststandarddeviationtobeσ ,and:
X
(cid:18) (cid:19)
ρ (cid:112)
X =σ Y + 1−ρ2N2k−1(0,1) , (8)
k X σ
Y
notingforemphasisthatthisdefinitionofX dependsuponY. Withtheassumptionthateachoftheper-wavenumbermodes
areindependentlydrawnfromthisdistribution,wecanalsotreatX andY asaproductof2k−1independent,scalarrandom
variables,whichwillsimplifythefollowingalgebra.
TheKLdivergenceofthedatagiventheforecastisthengivenby:
(cid:90) (cid:18) P (y′) (cid:19)
D (Y∥X)= P (y′)log Y dy′, (9)
KL Y P (y′)
X
fortherespectiveprobabilitydensityfunctions(PDFs)P andP andintegratingoverthespaceofpossibleobservations
Y X
parameterizedbyy′. Withtheseformulations,thePDFofY issimple:
(cid:18) y′2 (cid:19)
P (y′)=(2πσ2)−1/2exp − . (10)
Y Y 2σ2
Y
ThePDFofX ismorecomplicatedbecauseofitsdependenceonY,butforanyindividualobservationy(8)becomesa
shiftedGaussian,giving:
(cid:32) (x−ρσXy)2 (cid:33)
P (x|y)=(2πσ2 (1−ρ2))−1/2exp − σY , or
X X 2σ2 (1−ρ2)
X
(cid:32) (1−ρσX)2y2 (cid:33)
P (y|y)=(2πσ2 (1−ρ2))−1/2exp − σY . (11)
X X 2σ2 (1−ρ2)
X
(9)thenbecomes:
(cid:90)
D (Y∥X)=const(Y)− P (y)log(P (y))dy
KL Y X
(cid:90) (cid:18) y2 (cid:19)(cid:32) (1−ρσX)2y2 (cid:33)
=const(Y)+ (2πσ2)−1/2exp − log(2πσ2 (1−ρ2))+ σY dy
Y 2σ2 X 2σ2 (1−ρ2)
Y X
3That is, k independent complex-valued modes from 1...k with independent real and imaginary parts and a single, real zero-
wavenumbermode.
13

---

# Page 14

HRES Control AMSE AR1 AMSE AR12
2.5
55°N
0.0
50°N
45°N 2.5
)2
s2m
001(
005z
2.5
55°N
0.0
50°N
45°N 2.5
)K(
058t
2
55°N
0
50°N
45°N 2
)1
gkg(
007q
5
55°N
0
50°N
45°N 5
20°W 10°W 0°20°W 10°W 0°20°W 10°W 0°20°W 10°W 0°
)K(
t2
Figure7. Visualizationofhigh-passfilteredforecastandanalysisfieldsfortheforecastshownin1.
(σ −ρσ )2
=const(Y)+log(σ2 (1−ρ2))+ Y X . (12)
X 2σ2 (1−ρ2)
X
Minimizing(12)forσ whileholdingσ andρfixediscomplicated,butsolvednumericallytheoptimalstandarddeviation
X Y
ratioσ σ−1islessthanunity,reachingaminimumofabout0.66nearρ=0.4andincreasingforbothlowerandhigher
X Y
valuesofcorrelation. Thisislessintuitivethantheσ =σ optimumof(6),butitstillwouldsmoothfinescalesmuchless
X Y
thantheσ =σ ρoptimumof(2).
X Y
Implementing(12)asalossfunctionwouldbeconceptuallyinteresting,butthisseemsimpracticalbecausetheexpression
hassingularbehaviournearρ=1,wheretheimpliedrandompartofthepredictioncollapsestozerovariance.
B.SupplementalVerification
B.1.Visualization
Figure7visualizesthehigh-wavenumbercomponentsofasampleforecastmatchingthewinterstormEuniceprediction
showninfigure1. Theappliedfilterfourth-orderinsphericalharmonicspace,withthefunctionalform:
k4
HPF(k)=1− 0 , (13)
k4+k4
0
wherekisthetotalwavenumberandk =50isthecutoffnumber,chosentoemphasizemodeswithlengthscalesof800
0
kmandshorter. Overall,thepredictionsofthecontrolandAMSE-trainedmodelsshowverysimilarstructures,buttraining
with(6)asthelossfunctionenhancesthehigh-modevariabilityoftheforecasts.
14

---

# Page 15

101
100
10 1
h6
z500
HRES Control
101
100
10 1
h021
AMSE AR12 AMSE AR1
101
100
10 1
30 90 270 720
Total wavenumber
h042
t850 q700 2t
10 1 10 1
10 1
10 2 10 2
10 1 10 1
10 1
10 2 10 2
10 3
10 1 10 1
10 1
10 2 10 2
10 3
30 90 270 720 30 90 270 720 30 90 270 720
Total wavenumber Total wavenumber Total wavenumber
Figure8. Amplitudespectraldensityforthevariablesoffigure4at6h,120h,and240hleadtimes.
B.2.Spectra
√
Figure8showstheamplitudespectraldensity(squarerootofpowerspectraldensity,withunitsproportionalto1/ cycle)
atmoderatetofinescalesforseveralvariablesandleadtimes. Becauseoftheenergycascadeintheatmosphere,thespectra
ofmostvariablesfollowpower-lawdistributions. Energyintheatmosphereisultimatelyremovedbyturbulent,frictional
dissipation,butnopracticalglobalatmosphericmodelcaneffectivelyresolvethesescales.
Nonetheless,theavailableenergypertotalwavenumbervariesoverseveralordersofmagnitude,andevenlargeamplitude
densitydifferencesbetweenmodelscanappearsmallonthetypicallog-logscalesofthesegraphs. The2mtemperature
fieldshowsverylittlesmoothingcomparedtotheanalysisregardlessofmodelbecauseitisstronglyaffectedbythelocal
elevation,whichisalwayssuppliedasaconstantfield.
B.3.Quantile/QuantilePlots
Quantile-quantileplotsshowajointcumulativedensityfunction,andweusethemheretoevaluatetheoverallrealismofthe
forecastsproducedbythecontrolandAMSEAR12modelsindependentlyoftheforecastskill. Infigures9and10,the
x-locationofeachpointisthelabelledpercentileofNorthAmericanweatherstationobservationsforNorthernHemisphere
winterandsummerperiods. They-locationofeachpointisthecorrespondingpercentilefortheHRESanalysisorthe5-day
forecastsproducedbythecontrolandAMSEAR12models,interpolatedtothestationlocations. Forexample,intheleft
paneloffigure9,the98thpercentilecorrespondstoanobservedwindspeedofabout11.5m/s,butthe98thpercentileofthe
HRESanalysiswasabout10m/s.
They =xlineonthequantile-quantileplot,shownasadashedlineineachpanel,suggeststhattheforecastandobservations
have the same unconditional distributions when aggregated, and departures from the diagonal line indicate systematic
underpredictionoroverpredictionofextremevalues. Inourcase,figure9showsthattheAMSEAR12modelhasamore
realisticrepresentationofsurfacewinds,matchingthetrendsseenintheHRESdata. Thecontrolmodelproducesnoticeably
weakerwindsatallpercentiles,showingasystematicshiftinthedistributiontowardsweakersurfacewinds,particularlyin
summer.
Incontrast,figure10showsthatthemodelsareessentiallyequivalentinthedistributionof2mtemperatures. Asdiscussed
insectionB.2,the2mtemperaturefieldshowslittlesmoothinginthecontrolmodel,likelyduetothestronginfluenceof
elevationonthesurfacetemperature. Improvementstotheforecastof2mtemperatureintheAMSEAR12modelarefound
15

---

# Page 16

Figure9.Quantile-quantileplotsof10mwindspeedatsurfacestationlocationsfortheNorthAmericandomain.Atleft,1Jan–30March
2022(borealwinter),andatright20June–19September2022(borealsummer). ThecontrolandAMSEAR12pointsshowmodel
evaluationsfor5-dayforecasts.TheshadedregiondenotesconfidenceintervalbasedontheKolmogorov-Smirnovtest.
moreintheforecastskill(seefigure11)thanintheunconditionaldistributionoftemperatures.
B.4.DetailsoftheLaggedEnsembleVerification
Brenowitzetal.(2025)usesseveralmetricstoevaluatethequalityofthelaggedensembles. Inthiswork,weusethefair
CRPSscore,theensemblerootmeansquarederror(eRMSE),andthespread-errorratio(SER).TheeRMSEstatisticis
derivedfromitssquaredversion(ensemblemeansquarederror),evaluatedpointwiseandintegratedoverthegrid. TheSER
statisticisthesimpleratiooftheintegratedMSEandensemblespread(unbiasedestimateofvariance),notingforemphasis
thattheratioistakenafterthegrid-averaging. ForanensembleofN members(x )evaluatedoverN forecasts
e 1...Ne date
withverifyinganalysisy,thecorrespondingformulasare:
1 N (cid:88)date(cid:88) (cid:32) 1 (cid:88) Ne
CRPS(x,y)= dA(i,j) |x (i,j)−y(i,j)|+
N N k
date e
d=1 i,j k=1
1 (cid:88)
Ne
(cid:88)
Ne (cid:33)
|x (i,j)−x (i,j)| , (14)
2N (N −1) k l
e e
k=1l=1
 1/2
1 N (cid:88)date(cid:88)
eRMSE(x,y)= dA(i,j)(x¯(i,j)−y(i,j))2  , and (15)
N
date
d=1 i,j
SER(x,y)= (cid:32) 1 N (cid:88)date 1 (cid:80) i,j dA(i,j) (cid:80)N k= e 1 (x k (i,j)−x¯(i,j))2 (cid:33)1/2 , (16)
N N −1 (cid:80) dA(i,j)(x¯(i,j)−y(i,j))2
date d=1 e i,j
wherex¯(i,j)=N−1(cid:80)
x (i,j)istheensemblemeanatthe(i,j)gridpoint.
e k k
Figures11and12showtheCRPSandeRMSEskillscoresrespectivelyofthelaggedensemblegeneratedwithAMSE
AR12comparedtothelaggedensembleofthecontrolmodelforthegeopotential(z),temperature(t),specifichumidity
(q),andu-componentofwind(u)atseveralelevationsandforthemeansealevelpressure(msl),2-metertemperature(2t),
u-componentof10mwind(10u),and6h-accumulatedprecipitation(tp)atthesurface.
Forthesefigures,statisticalsignificancewasdeterminedbybootstrapping,sampling1/3ofthetotaldatesineachsampleto
giveanaveragegapbetweendatesof36h. Theforecastskillofpersistence(thatis,thegainoveraclimatologicalforecastby
16

---

# Page 17

Figure10.Asinfigure9,for2mtemperature.Lowpercentiles(extremecold)areshownfortheNorthernHemispherewinter,andhigh
percentiles(extremeheat)areshownfortheNorthernHemispheresummer.
predictingthateverythingwillremainconstant)decaysveryquicklyover36h,sosamplesso-spacedapartarereasonably
independentofeachother.
Overall,AMSEAR12showsCRPSskillimprovementsformostvariablesandmostleadtimes,buttotalprecipitationshows
onlysmallimprovementsatlongleadtimesanddegradationatshortleadtimes. Thisisexplainedbytheseparationofmodes
in(5)notbeinganaturaloneforprecipitation. Precipitationisoftenlocalizedbutalwaysnon-negative,andconsequentlyits
spectraldecompositiondoesnotreallyresemblethenormally-distributedrandomvaluesthatgivemeaningto(5)and(6).
TheeRMSEskillchartshouldbeinterpretedwithcaution. Thescoresof(14)–(16)weredevelopedforthecaseofanideal
ensemble,wheremembersarestatisticallyindistinguishablefromeachotherandequallyaccurateinexpectation. Thisis
notreallythecaseforalaggedensemble,wheretheshorter-durationmembersshouldbenoticeablymoreaccuratethan
longer-durationmembersandanidealaggregationwouldseparatelyweighteachterm. ThisisnotdonebyBrenowitzetal.
(2025)forsimplicityandtoavoidfreeparameters,butwebelievethattheearlylead-timesmoothinginthecontrolmodel
makesequal-weightingmoreoptimalforitslaggedensemblethanforthelaggedensembleofAMSEAR12.
Forlongleadtimesthisadvantagediminishes,wheretherelativedegradationofforecastqualityismuchstrongerbetween
0.5daysand4.5daysthanitisbetween6daysand10days. Inthisregime,AMSEAR12beginstoshoweRMSEskillover
thecontrolensemble.
B.4.1.UNBIASEDENSEMBLEROOTMEANSQUAREDERROR
TheeRMSEformulaof(15)isabiasedestimatorofthetrueensemblemeanerror,overestimatingtheerrorinproportionto
theensemble(sample)spreadwhentheensemblesizeisfinite.
ConsiderN differentrealizations(x )ofasinglevariabledrawnfromN(µ,σ2)whentheground-truthvalueis0.Applying
e i
(15)tothisgives:
(cid:32) (cid:33)2 
1 (cid:88) σ2
E(eMSE(x,0))=E  N x i =µ2+ N , (17)
e e
i
whichoverestimatesthetrueensemblemeansquarederror. Thisoverestimateismoresevereforsmallensemblessuchas
thelaggedensembleconfigurationofsection3.2,wheretheensemblesizecannotbeeasilyincreased.
Leutbecher&Palmer(2008)proposescorrectingthisoverestimatebysubtractingthestandarderrortermtogiveanunbiased
estimatoroftheensemblemeansquarederrorwithafinitesamplesize. Inthenotationof(15),thecorrespondingrootmean
17

---

# Page 18

z
t
q
u
z
t
q
u
z
t
q
u
msl
2t
10u
tp
3 4 5 6 7 8
Lead time (d)
aPh052
aPh005
aPh058
ecafruS
Figure11.CRPSskillscore(%improvement),measuredastherelativedifferencebetweentheCRPS(14)ofthe12-stepfine-tunedmodel
andtheCRPSofthecontrolmodel,foraselectionofvariablesandleadtimes. Orangeup-arrowsshowwherethefine-tunedmodel
performsbetter,bluedown-arrowsshowwherethecontrolmodelperformsbetter.Hollowarrowsrepresentadifferenceoflessthan1%,
anddifferencesof2%orlargeraremarked.Hollowcirclesmarkvaluesthatarenotstatisticallysignificantatthe90%level.
squaredformulabecomes:
(cid:32) 1 N (cid:88)date(cid:88) (cid:18)(cid:16) 1 (cid:88) Ne (cid:17)2
ub eRMSE(x,y)= dA(i,j) x (i,j)−y(i,j) −
N N k
date e
d=1 i,j k=1
1 (cid:88)
Ne (cid:19)(cid:33)1/2
(x (i,j)−x¯(i,j))2 , (18)
N (N −1) k
e e
k=1
whichperformsthiscorrectionpointwiseonthegridbeforecomputingthespatialaverageandtakingthesquareroot.
ImplementingthisadjustmentslightlyimprovesthescoresoftheAMSE-tunedmodelcomparedtothecontrolmodel,and
thecorresponding“scorecard”isshowninfigure13.
18

---

# Page 19

z
t
q
u
z
t
q
u
z
t
q
u
msl
2t
10u
tp
3 4 5 6 7 8
Lead time (d)
aPh052
aPh005
aPh058
ecafruS
Figure12. Asfigure11,forensemblerootmeansquarederror(15).
19

---

# Page 20

z
t
q
u
z
t
q
u
z
t
q
u
msl
2t
10u
tp
3 4 5 6 7 8
Lead time (d)
aPh052
aPh005
aPh058
ecafruS
Figure13. Asfigures11and12,fortheunbiasedensemblerootmeansquarederror(18).
20

---

# Page 21

Table2.Cumulativerankedprobabilityscoresforthemodelsfine-tunedinthisstudyinthelaggedensembleconfigurationdescribed
insection3.2,forthe“headline”variablesandlevelsinfigure1ofRaspetal.(2024).Lowerisbetter;thebestscoreisboldedandthe
second-placescoreisitalicized.
Model z500hPa(m2s−2) t850hPa(K) q700hPa(g·kg−1) u850hPa(m·s−1)
2.5d 5.0d 7.5d 2.5d 5.0d 7.5d 2.5d 5.0d 7.5d 2.5d 5.0d 7.5d
Control 31.038 84.315 162.481 0.428 0.691 1.003 0.357 0.523 0.652 0.823 1.340 1.904
MSEAR12 31.285 82.100 155.703 0.419 0.664 0.949 0.356 0.526 0.652 0.819 1.335 1.886
MAEAR12 29.969 80.621 155.361 0.410 0.654 0.947 0.340 0.499 0.624 0.811 1.313 1.859
AMSEAR1 33.720 94.703 186.202 0.422 0.721 1.078 0.354 0.558 0.721 0.863 1.485 2.115
AMSEAR12 30.565 80.469 153.267 0.418 0.653 0.935 0.347 0.510 0.634 0.832 1.341 1.882
B.5.AblationStudies
6h 120h 240h
1.2
1.0
0.8
0.6
0.4 AMSE AR12
MSE AR12 Amplitude ratio
0.2
MAE AR12 Coherence
0.0
0 10 32 90 250 720 0 10 32 90 250 720 0 10 32 90 250 720
Total wavenumber Total wavenumber Total wavenumber
Figure14.Asfigure3,forthecomparisonmodelsofsectionB.5.OnlythemodeltrainedwiththeAMSEerrorfunctionretainssharpness
tofinescales.
Toensurethattheresultsofthisstudyarenotsimplyanartifactofincreasingthemodel’soveralltrainingtime,wecompare
againsttwoadditionalfine-tunings:
1. MSEAR12implementsthefine-tuningscheduleoftable1withtheunmodifiedmeansquarederrorlossfunction,as
withGraphCast’sprincipaltraining.
2. MAEAR12implementsthefine-tuningschedulewithameanabsoluteerrorlossfunction,preservingtheper-variable
andper-levelweightingsoferror.
Figure14showstheaggregatedper-wavenumberperformanceofthesemodels, andtable2evaluatestheirCRPSfora
selectionofvariables,levels,andleadtimesinthelaggedensembleconfiguration.
Bothmodelsstillshowexcessivesmoothingoffinescales, buttrainingwithmeanabsoluteerrormoderatelyimproves
sharpnessatthemediumscales(wavenumbers32–200forlongerleadtimes,correspondingtolengthscalesof1250–250
kilometers).
TheexcessivesmoothingoftheMSE-trainedmodelisexpectedfromsection2.1,butthatargumentdoesnotdirectlyapply
tothemeanabsoluteerrorlossfunction. However,wecanstillunderstandthisbehaviourintuitively. Amodelthatisoptimal
underthemeanabsoluteerrorpredictsthemeanofadistribution,andatlongerleadtimesfinescalesarelesspredictable
thancoarserscales. Therefore,thepredictionofthemedianfutureshouldbesmootherthanitsrealization.
EventhemoderateimprovementtosharpnessfortheMAE-trainedmodelresultsinimprovementstotheCRPSofthelagged
ensemble,asshownintable2.
21