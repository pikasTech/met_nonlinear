Enhancing Representation Learning for Periodic Time Series with
Floss: A Frequency Domain Regularization Approach
ChunweiYang XiaoxuChen LijunSun
SichuanUniversity McGillUniversity McGillUniversity
Chengdu,China Montreal,Canada Montreal,Canada
ycwcw123@gmail.com xiaoxu.chen@mail.mcgill.ca lijun.sun@mcgill.ca
HongyuYang YuankaiWu
SichuanUniversity SichuanUniversity
Chengdu,China Chengdu,China
yanghongyu@scu.edu.cn wuyk0@scu.edu.cn
ABSTRACT analysisplaysapivotalroleinpredictingtrafficflowsandopti-
Timeseriesanalysisisafundamentaltaskinvariousapplication mizingtransportationsystems[19,43,44].Moreover,infinancial
domains,anddeeplearningapproacheshavedemonstratedremark- markets,timeseriesanalysisisofutmostimportance.Itallows
ableperformanceinthisarea.However,manyreal-worldtimeseries forthemodelingofassetprices,enablesvolatilityforecasting,and
dataexhibitsignificantperiodicorquasi-periodicdynamicsthat assistsindevelopingeffectiveriskmanagementstrategies[34].The
areoftennotadequatelycapturedbyexistingdeeplearning-based applicationoftimeseriesanalysisinhealthcareprovesinvaluable
solutions.Thisresultsinanincompleterepresentationoftheun- aswell,aidinginpatientmonitoring,diseasesurveillance,andthe
derlyingdynamicbehaviorsofinterest.Toaddressthisgap,we predictionofhealthoutcomes[20,29].
proposeanunsupervisedmethodcalledFlossthatautomatically Thewidespreadadoptionofdeepneuralnetworksintimese-
regularizeslearnedrepresentationsinthefrequencydomain.The riesanalysishasbroughtaboutsignificantadvancementsinrecent
Flossmethodfirstautomaticallydetectsmajorperiodicitiesfrom years[28].Thesemodelshavedemonstratedtheirefficacyincap-
thetimeseries.Itthenemploysperiodicshiftandspectraldensity turingcomplextemporalpatternsbyleveragingsupervisedorun-
similaritymeasurestolearnmeaningfulrepresentationswithpe- supervisedtrainingapproaches.Throughpropertrainingmethod,
riodicconsistency.Inaddition,Flosscanbeeasilyincorporated neuralnetworksacquirerobusttemporalrepresentationsthatare
intobothsupervised,semi-supervised,andunsupervisedlearning well-suitedforvarioustaskswithintimeseriesanalysis[47].One
frameworks.Weconductextensiveexperimentsoncommontime crucialtaskwhereneuralnetworksexcelisforecasting,wherethey
seriesclassification,forecasting,andanomalydetectiontasksto leveragetheirlearnedtemporalrepresentationstomakeaccurate
demonstratetheeffectivenessofFloss.WeincorporateFlossinto predictionsaboutfuturevalues[42].Additionally,neuralnetworks
severalrepresentativedeeplearningsolutionstojustifyourdesign haveshownpromisingresultsinanomalydetectionwithintime
choicesanddemonstratethatitiscapableofautomaticallydiscover- seriesdata[26].
ingperiodicdynamicsandimprovingstate-of-the-artdeeplearning Thequestforauniversalrepresentationoftimeseriesdatahas
models. sparkedsignificantinterestindeeprepresentationlearningstrate-
gies,includingcontrastivelearning[4,14].Thesestrategiesaimto
extractpowerfulrepresentationsfromthehiddenlayersofdeep
:
neuralnetworks,capturingtheintrinsicfeaturesembeddedwithin
ChunweiYang,XiaoxuChen,LijunSun,HongyuYang,andYuankaiWu.
EnhancingRepresentationLearningforPeriodicTimeSerieswithFloss:A timeseriesdata.Thevalueofsuchrepresentationsextendstovar-
FrequencyDomainRegularizationApproach.14(1):XXX-XXX,2020. iousdownstreamtasks,includingtimeseriesanomalydetection,
doi:XX.XX/XXX.XX forecasting,andclassification.Researchershaveexploredspecific
invarianceswithintimeseriesdatatoenhancedeeprepresentation
Thesourcecode,data,and/orotherartifactshavebeenmadeavailableat learningframeworks.Forinstance,Franceschietal.[10]encour-
https://github.com/AgustDD/Floss. agedrepresentationsthatcloselyresemblesampledsubseries,while
Tonekabonietal.[32]enforcedsmoothnessbetweenadjacenttime
1 INTRODUCTION windows.Eldeleetal.[9]proposedamodelthatlearnsscaleand
Wearewitnessingcontinueddevelopmentsinsensortechnologies, permutation-invariantrepresentations.Yueetal.[47]introduced
wheresensorsproducemultivariatetimeseries.Theseadvances TS2Vec,acontrastivelearningframeworkthatcapturescontextual
havepavedthewayforthecriticalroleoftimeseriesanalysisin invariancesatmultipleresolutionswithintimeseries.Despitethe
variousscientificandengineeringfields.Intherealmofenergy progressmade,existingmethodsoftenborrowideasdirectlyfrom
management,timeseriesanalysisenablesaccurateloadforecast- contrastivelearningmethodsincomputervisionandnaturallan-
ing,facilitatingefficientresourceallocationandoptimalenergy guageprocessingdomains.However,unlikeimagesthattypically
utilization[7,15].Withintransportationengineering,timeseries possessrecognizablefeatures,timeseriesdataoftenexhibitunderly-
ingpatternsthatarenoteasilyexplainable.Applyingassumptions
Correspondingauthor(YuankaiWu,wuyk0@scu.edu.cn)
3202
peS
2
]GL.sc[
4v11010.8032:viXra

borrowedfromotherdomainswithoutcarefulconsiderationmay
resultinunsuccessfulrepresentationlearningfortimeseriesdata.
Thetemporaldynamicsofreal-worldprocessesoftenexhibit
recurringcyclesandsignificantperiodicity,whicharefundamen-
talcharacteristicsoftimeseriesdata[11].Thisinherentproperty
becomes particularly evident in time series associated with hu-
manbehavior,whereprominentdailyandweeklypatternsemerge.
Recognizingtheimportanceofcapturingandleveragingperiodic-
ity,theexplorationofrepresentationlearningmethodsthateffec-
tivelycapturetheunderlyingperiodicinvarianceholdssubstantial
promiseintimeseriesanalysis.Oneclassicalapproachtodetecting
Time Series Encoder
periodicityintraditionaltimeseriesanalysisistheemployment
offrequencydomainmethods,whichenabletheidentificationof
periodicpatternsbytransformingtimeseriesintothefrequency
domain[21].ThediscreteFouriertransform(DFT),forinstance,
facilitatestheconversionoftimeseriesfromthetimedomainto Periodic
Consistency
thefrequencydomain,yieldingtheperiodogramthatencodesthe
strengthatdifferentfrequencies.Similarly,othertransformations,
suchasthediscretecosinetransformandwavelettransform,can
alsoidentifyperiodicityandenhancesupervisedlearningintime Spectral Density1 Spectral Density2
series analysis [38]. These studies provide compelling evidence
thatfrequencydomaininformationharborsvaluableinsightsfor ≈
analyzingperiodictimeseriesdata.
Infact,frequency-domaininformationhasbeenwidelylever-
agedindeeplearningarchitecturesformodelingtimeseriesdata.
Figure1:Theframeworkofthepaper:Thetimeseriesshown
Zhouetal.[53]proposedtheuseofTransformersoperatingin
inthefigureexhibitsstrongdailyperiodicity.Afterdetecting
thefrequencydomain,enablingthecaptureofglobalproperties
thisperiodicity,weaimtomakethespectraldensitiesofthe
withintimeseriesdata.Wooetal.[40]introducedETSTransformer,
representationsoftwotimeseriessegments,whichdifferby
whichutilizesFourierbasesinthefrequencydomaintoextract
severalnumberofperiodicities,assimilaraspossible.
dominant seasonal patterns from time series. Liu et al. [22] de-
visedatree-structurednetworkthatiterativelydecomposesinput
signalsintovariousfrequencysubbands.Zhangetal.[50]decom-
posedtimeseriesintoseasonalandtrendcomponents,employing remainsinvariantunderperiodictransformations.Torealize
Fourierattentionforprediction.Wuetal.[41]employedFourier this,ourframeworkincorporatesstraightforwardandefficientdata
transformationtodisentangleoriginaltemporalvariationsintoin- augmentationsthatcanaccommodatevariousperiodictimeseries
traperiodandinterperiodvariations,capturingtheirdependencies withspecifiedperiodicities.Initially,weemployfrequencydomain
using2Dconvolutionaloperations.Notably,recenteffortshave transformationtoautomaticallydetectthedominantperiodicity
focusedonregulatingfrequency-domainrepresentationsthrough andcreateaperiodicviewofthetargettimeseriesbyintroducing
unsupervisedlearningapproaches.Zhangetal.[51]directlyapplied randomperiodicshiftsinthetemporaldimension.Subsequently,a
contrastivelearningtothefrequencytransformationofrawsignals, timeseriesencoderisemployedtolearnaperiodicinvariantrepre-
embeddingthetime-basedneighborhoodofanexamplecloseto sentation.Importantly,thisencodercanbeseamlesslyintegrated
itsfrequency-basedneighborhood.Similarideaswereexploredin intoanyexistingdeeplearningframework,therebyensuringcom-
CoST[39]andBTSF[46].However,whiletheseapproacheslever- patibilityandflexibilityinitsapplication.Finally,wedesignanovel
ageunsupervisedlearningandcontrastivelearning,noneofthem taskthatenforcesthesimilarityofspectraldensitiesbetweenthe
arespecificallydesignedtocaptureperiodicdynamicsintimeseries targettimeseriesanditsperiodicviews.Tomitigatetheinfluence
data. ofhigh-frequencynoise,weemployahierarchicalapproachtomea-
Inourpursuitofcapturingperiodicdynamicsbytimeseries surethesimilarityofspectraldensitiesbetweentherepresentations.
representations,weproposeanovelapproachthatleveragesthe TheintuitionofourworkisillustratedinFigure1.
principlesofcontrastivelearning[4,17].Contrastivelearningop- To the best of our knowledge, this study represents the first
eratesonthebasisoftwokeyelements:(i)acontrastivelossthat systematicinvestigationintothelearningofrepresentationsfor
comparesfeaturesand(ii)asetoftransformationsthatencodethe periodicorquasi-periodictimeseriesbyexaminingtheinvariance
desiredinvariances.Buildinguponthisframework,weintroducea ofspectraldensity.Specifically,ourFlosscanbeseamlesslyinte-
simpleyeteffectivecombinationoflossfunctionandtransformation gratedintocurrentsupervisedandunsupervisedframeworks.The
namedFloss,whichcanbeseamlesslyintegratedintounsupervised outcomesobtainedfromtaskssuchastimeseriesclassification,
andsemi-supervisedlearningmethodsspecificallydesignedfor forecasting,andanomalydetectionconfirmtheabilityofFlossto
periodictimeseriesanalysis.Ourapproachcentersonthehypoth- captureandencodeperiodicinvariancesintimeseries,resultingin
esisthatthespectraldensityofthelearnedrepresentation anotableenhancementoftaskperformance.
2

Thepaperisorganizedasfollows.Section2introducesthenec- transform(DWT),canalsobeusedtocalculatethespectraldensity.
essaryconceptsforunderstandingtheFlosssystem.InSection3, IfweemploytheDCT,thetransformationisgivenby:
weprovideacomprehensivedescriptionofourFlossframework. (cid:16)𝑛(cid:17)−1/2∑︁ 𝑛 (cid:16)𝜋𝑤 𝑗 (cid:17)
Furthermore,Section4showcasestheresultsofourforecasting, DCT(𝑤 𝑗)= ∧(𝑡)𝑥 𝑡cos (2𝑡−1) ,
classification,andanomalydetectionexperimentsusingtheFloss- 2 𝑡=1 2𝑛
enhancedmodelsonextensivebenchmarkingdatasets.Inaddtion, (cid:40) √1 if 𝑡 =1 (2)
in-depthanalysisandablationstudiesarealsoprovidedinSection4. ∧(𝑡)= 2
Finally,Section5offersconcludingremarksandsummarizesour 1 otherwise
work. Φ (cid:0)𝑤 𝑗 (cid:1) = (cid:12) (cid:12)DCT (cid:0)𝑤 𝑗 (cid:1)(cid:12) (cid:12) .
2 PRELIMINARIES 3 METHOD
Periodic time series: Given a data set of periodic time series, Inthissection,wepresenttheproposedfrequencydomainloss
denotedX ∈ R𝑁×𝑇×𝐹 ,where𝑁 representsthenumberoftime (Floss) for periodic time series and provide implementation de-
seriesand𝑇 and𝐹 indicatethesizeofthetimewindowandfeature tails.Flossisannovelframeworkthataimstocapturetheinherent
dimension,respectively,weassumethatthesetimeseriesexhibit periodicinvarianceoftimeseriesinitslearnedrepresentations.
periodicbehavior.Moreover,itisimportanttonotethatthepe- Toaccomplishthis,theframeworkincorporatestwokeysteps:a
riodicitiesmayvarywithinthesampledtimeranges.Tofurther periodicitydetectionmoduleforgeneratingperiodicviewsanda
clarify,let’sdefine [𝑡 1 ,𝑡 2 ] = {𝑡 1 ,𝑡 1 +1,...,𝑡 2 −1,𝑡 2 }.Weusethe novelobjectivethatcomparesthespectraldensitiesoftheserepre-
notation X [𝑡 ,𝑡 ] ∈ R𝑁×(𝑡 2 −𝑡 1 +1)×𝐹 to represent the time series sentations(Figure2).Bydoingso,thelearnedrepresentationsare
1 2
sampledfrom𝑡 1to𝑡 2. equippedwithanawarenessoftheunderlyingperiodicnatureof
To illustrate, let’s consider the scenario where X represents timeseries.
traffictimeseriescollectedfrom𝑁 trafficsensorsinaroadnetwork.
Ifwesamplethedataoveraperiodcorrespondingtoasingleday 3.1 PeriodicDetectionandAugmentation
forX [𝑡 1 ,𝑡 2 ],itbecomesapparentthatthedominantperiodicityis Assumingtheexistenceofmultipleperiodicitieswithineachtem-
approximately6hours,astrafficdatatypicallyexhibitsmorningand poral sampled time series X [𝑡 ,𝑡 ] ∈ R𝑁×(𝑡 2 −𝑡 1 +1)×𝐹 , our study
eveningpeaks.Conversely,ifwesamplethedataoverseveraldays focuses on a wide time range 1 [𝑡 2 1 ,𝑡 2 ] to encompass diverse and
forX [𝑡 1 ,𝑡 2 ],theprominentperiodwouldbeoneday.Furthermore, significantperiodicpatternsinthedata.Inordertocreateperiodic
itisworthnotingthattimeseriescanexhibitmultipleperiodicities.
transformation,itisnecessarytofirstidentifytheunderlyingpe-
Forinstance,inthetrafficexample,therecouldbeperiodicitiesof
riods.Thisisachievedbycalculatingtheaveragespectraldensity
6hoursand1day.Weintroducethenotation𝑝
[𝑡 1 ,𝑡 2 ]
∈Rtodenote
usingthefollowingprocedure:
theprominentperiodicityoftimeseriesX [𝑡 ,𝑡 ].
Timeseriesrepresentation: ForagivenX [ 1 𝑡 2 ,𝑡 ],arepresentation 1 ∑︁ 𝑁 ∑︁ 𝐹
modelG(·;𝜃)parameterizedby𝜃generatesar 1 ep 2 resentationtensor Φˆ = 𝑁𝐹 Φ n,f ,
Y [𝑡 1 ,𝑡 2 ] =G (cid:16) X [𝑡 1 ,𝑡 2 ];𝜃 (cid:17) .Here,Y [𝑡 1 ,𝑡 2 ] ∈R𝑁′×(𝑡 2 −𝑡 1 +1)×𝐹′ ,where 𝑛=1𝑓=1 (cid:16) (cid:17) (3)
𝑁′and𝐹′indicatethedimensionsofthemodifiedtimeseriescount 𝑤ˆ =argmax Φˆ ,
a
th
n
a
d
t
t
t
h
h
e
e
r
v
ep
al
r
u
es
e
e
o
n
f
ta
𝑁
tio
′
n
va
fe
ri
a
e
t
s
ur
d
e
e
,
p
re
e
s
n
p
d
e
i
c
n
t
g
iv
o
el
n
y.
t
I
h
t
e
is
c
i
h
m
o
p
ic
o
e
rt
o
a
f
n
G
tt
.
o
If
no
w
t
e
e
𝑝ˆ [𝑡 1 ,𝑡 2 ] =
(𝑡
2
−
𝑤
𝑡
ˆ 1
+1)
.
aimtogenerateanoverallrepresentationencompassingalltime
series,then𝑁′ =1.Ontheotherhand,ifthegoalistoproducea Here,Φ n,f representstheestimatedperiodogramofthe𝑓-thfeature
representationforeachindividualtimeseries,then𝑁′ =𝑁. ofthe𝑛-thtimeseries.ThesymbolΦˆ ∈R𝑡 2 −𝑡 1 +1denotestheaver-
PowerSpectralDensity:Insignalprocessing,thepowerspectral ageperiodogramacrossfeatures.Itisimportanttonotethatthe
densityprovidesinformationabouttheexpectedsignalpowerat 𝑗-thvalueΦ(𝑤 𝑗)signifiestheintensityofthefrequency-𝑗 periodic
differentfrequenciesofthesignal.Forexample,theperiodogramis basisfunction,whichisassociatedwiththeperiodlength
(𝑡
2
−
𝑤
𝑡
𝑗 1
+1)
.
ameasureofspectraldensityintheFourierdomain.Denotingthe Furthermore,weexaminethemaximumperiodicity𝑝ˆ [𝑡 ,𝑡 ] discov-
discreteFouriertransformasDFT (·),theperiodogramΦ(·)is eredthroughtheperiodogram,whichcorrespondstot 1 he 2 highest
computedas: valueobservedinΦˆ.
𝑛 Althoughtheperiodogramisextensivelyemployedforspectral
DFT (cid:0)𝑤 𝑗 (cid:1) = √ 1 ∑︁ 𝑥 𝑡 𝑒−2𝜋𝑖𝑤𝑗𝑡, analysisandcapturingperiodicdynamics,itsefficacycanbesub-
𝑛
𝑡=1 (1) optimalundercertaincircumstances.Notably,highlevelsofnoise
Φ (cid:0)𝑤 𝑗 (cid:1) =Re (cid:0)DFT (cid:0)𝑤 𝑗 (cid:1)(cid:1)2+Im (cid:0)DFT (cid:0)𝑤 𝑗 (cid:1)(cid:1)2, canobfuscatetheperiodicsignals,resultingininaccurateorpoten-
tiallydeceptiveoutcomes[33].Additionally,theperiodogrammay
where𝑥 𝑡 denotesthetimeseriesvalueattimepoint𝑡,Re(·)and encounterchallengeswhenfacedwithcomplexspectralshapes
Im(·)denotetherealandimaginaryparts,respectively.Eachele- orirregularpatterns,impedingitsabilitytopreciselycaptureand
mentoftheperiodogramrepresentsthepoweratfrequency𝑤 𝑗,or characterizetheunderlyingperiodicdynamics[37].
equivalently,atperiod1/𝑤 𝑗.Itisimportanttonotethatothertrans- Inourapproach,wecomputeaperiodogramforeachsampled
formations,suchasdiscretecosinetransform(DCT)andwavelet batch,whichessentiallyinvolvesrandomsamplingoverthetime
3

Periodicity Detection Encoder Floss
Time Series
Periodic view1 Periodic view2 𝚽1 𝚽2
≈
Spectral Density
Similarity
Periodic view Training for
Time Series Encoder Temporal Pooling downstream
tasks
Spectral Density
Similarity
≈
Periodic view1 Periodic view2 𝚽1 𝚽2
Figure2:Ourframeworkcomprisesthreecriticalsteps:(1)PeriodicityDetection:Weautomaticallydetectperiodicitypatterns
fromtheinputtimeseriessamplesandutilizethedetectedperiodicitytocreatetwoviewsoftheinputtimeseries.(2)Frequency
DomainSimilarityLearning:Thetwoperiodicviewsareprocessedthroughtheirrespectivetimeseriesencoders,generating
tworepresentations.(3)TheFlossalgorithmhierarchicallycalculatesthesimilaritiesbetweenthespectraldensitiesofthetwo
representationsusingtemporalpooling.Thepre-trainedencodercanthenbedirectlyappliedtodownstreamtasks.
domainduringthetrainingperiod.Wepositthatthepotentialin- Secondly,itenablestheidentificationofsimilarperiodicpatterns
accuraciesassociatedwiththeperiodogramcanbemitigatedby fromtherepresentationsofboththeoriginalviewanditsperiodic
employingthistemporalsamplingapproach.Byperformingran- view.
domsamplingoverawidetimerange,weincreasethenumber However,retainingallfrequencycomponents,asinEquation(4),
ofsamples,therebyenhancingthestatisticalconsistencyofthe mayleadtosubparrepresentations,asmanyhigh-frequencyfluctu-
estimatedperiodogram.Thisapproachissupportedbyempirical ationsintimeseriescanbeattributedtonoisyinputs.Conversely,
validation.Forinstance,inthefieldofsignalprocessing,random exclusivelypreservinglow-frequencycomponentsmightnotbe
samplingfollowedbyperiodogramanalysishasproveneffectivein suitablefortimeseriesmodeling,ascertainshiftsintrendswithin
identifyingperiodicsignals[31].Similarly,inastronomy,thisap- thetimeseriescarrysignificantmeaning.Tobettercaptureinfor-
proachhasbeensuccessfullyutilizedforperiodogramanalysis[35]. mationfromallfrequencycomponents,weproposeahierarchical
Afterobtainingtheestimated𝑝ˆ [𝑡 ,𝑡 ]forX [𝑡 ,𝑡 ],weshiftthedata frequencyloss,whichcompelstheencodertolearnrepresentations
1 2 1 2
alongthetimeaxistoexploittheperiodicdynamics.Weimplement atmultiplescales.Ourapproachinvolveshierarchicallyapplying
thisconceptthroughrandomperiodicshifts.Inaformalsense,we temporalmaxpoolingtothelearnedfeaturesYandYˆ,followed
considertheperiodicviewofX [𝑡
1
,𝑡
2
] asX [𝑡ˆ
1
,𝑡ˆ
2
],where𝑡ˆ 1 and𝑡ˆ 2 bycomputingtheirperiodicinvarianceloss.Thealgorithmicsteps
are𝑡 1 +𝑎𝑝ˆ [𝑡 ,𝑡 ] and𝑡 2 +𝑎𝑝ˆ [𝑡 ,𝑡 ],𝑎isarandominteger, for this calculation are outlined in Algorithm 1. Temporal max
1 2 1 2
poolingselectsthemostprominentelementwithinagivenregion
3.2 HierarchicalFrequency-DomainLoss oftherepresentation,therebyyieldinganoutputthatretainsthe
GivenanencoderG(·;𝜃)parameterizedby𝜃,alongwiththeorigi- salientfeatureswhileminimizingnoiseinterference.Furthermore,
thetemporalpoolingoperationreducesthetemporaldimensional-
nalviewX [𝑡
1
,𝑡
2
] anditsperiodicviewX [𝑡ˆ
1
,𝑡ˆ
2
],ourobjectiveisto
ityofthehiddenrepresentation.Consequently,thecorresponding
minimizethedifferenceinpowerspectraldensitybetweenthetwo
(cid:16) (cid:17) (cid:16) (cid:17) frequencycomponentofthehiddenrepresentationdecreasesaf-
representations.LetY = G X [𝑡 1 ,𝑡 2 ];𝜃 andYˆ = G X [𝑡ˆ 1 ,𝑡ˆ 2 ];𝜃 . termaxpooling,enablinggreateremphasisonthelow-frequency
LetΦ
Y
andΦ
Yˆ
representtheestimatedperiodogramsofYandYˆ component.Thisstrategyisreasonable,consideringourobjective
respectively.Thelossfunctionforachievingperiodicinvariance istoencodeperiodicinvariance,whichprimarilyresideswithin
canbedefinedasfollows: thelow-frequencydomain.
InAlgorithm1,theparameter𝜏playsacrucialroleincontrolling
1
L𝑓 = 𝑁′𝐹′ ∥Φ Y −Φ Yˆ ∥𝑙1 , (4) theweightingofhigh-frequencycomponentsinthecontextofmax
pooling.Alargervalueof𝜏 assignsgreaterimportancetothehigh-
where𝑁′and𝐹′denotetheprojectedtimeseriesandthenumber
frequencyparts.Forinstance,setting𝜏tomatchthetemporallength
offeaturesinYandYˆ respectively. ofthefeaturewouldeffectivelyequateittodirectlycomparing
By minimizing the loss function defined in Equation (4), we thespectraldensitiesofthetwofeatures.Itisnoteworthythatin
canreaptwodistinctadvantagesofpreservingperiodicinvariance. ourexperiment,wediscoveredcertaindatasetswhereemploying
Firstly,itensuresthattherepresentationsoftheoriginalviewand non-hierarchicalFlossanddirectlycomparingspectraldensities
itsperiodiccounterpartexhibitsimilaritywithinaspecificdomain.
4

Algorithm1Calculatingthehierarchicalfrequencyloss
Input:Y,Yˆ,aspectraldensitymeasureΦ
Parameter:Poolingscale𝜏 Encoder
Time Series
Output:HierarchicalLossLℎ𝑖𝑒𝑟 Transfer
1: Lℎ𝑖𝑒𝑟 ←L𝑓(Y,Yˆ,Φ(·)); Encoder Decoder
2: 𝑑 ←1
3: whilelength(Y) >1 do
4: Y ←maxpool1d(Y,𝜏); (a)Self-supervisedtraining(fixedencoderparameters
(cid:16) (cid:17) afterself-supervisedtraining)
5: Yˆ ←maxpool1d Yˆ,𝜏 ;
6: Lℎ𝑖𝑒𝑟 ←Lℎ𝑖𝑒𝑟 +L𝑓(Y,Yˆ,Φ(·));
7:
𝑑 ←𝑑+1;
Encoder
8: endwhile Time Series
9: Lℎ𝑖𝑒𝑟 ←Lℎ𝑖𝑒𝑟/𝑑; Transfer
10: return Lℎ𝑖𝑒𝑟. Encoder Decoder
(b)Pre-trainingthenFine-tuning
producedsuperioroutcomes.Subsequentanalyseswilldelvedeeper
intothisparticularaspect.
Decoder
3.3 TrainingSchemesUnderDifferentSettings Encoder
Time Series
TheFrequency-domainloss(Floss)function,whichisproposedin
Section3.2,canbereadilyemployedinbothsupervisedandun-
supervisedlearningsettings.Thissectionexplorestheintegration
ofFlossintounsupervised,semi-supervised,andsupervisedtime
(c)JointTraining
seriesanalysis.Wesummarizethetrainingstrategyofdifferent
schemesinFigure3
Figure3:Illustrationofdifferenttrainingschemes.
1)Self-supervisedtraining:Inthepretrainingphase,onlytheun-
labeledtimeseriesX ∈R𝑁×𝑇×𝐹 areavailable.First,werandomly
sampletheoriginalviewX [𝑡 1 ,𝑡 2 ]anditsperiodicviewX [𝑡ˆ 1 ,𝑡ˆ 2 ] from correspondinglabels D areavailableduringthetrainingphase.
X,consideringperiodicshifts.TomakeFlosscompatiblewithother Theencoder𝐺(·;𝜃)istrainedusingaweightedcombinationofthe
self-supervisedlearningschemes,wecanapplyaugmentationtech-
FlossL𝑓 andthesupervisedlossL𝑡𝑎𝑠𝑘.
niquessuchastimestampmaskingandrandomcropping[47]to
X [𝑡 1 ,𝑡 2 ] andX [𝑡ˆ 1 ,𝑡ˆ 2 ].Subsequently,wepasstheoriginalandtrans- 4 EXPERIMENTS
formedinputsthroughanencoder𝐺(·;𝜃).TheFlossiscomputed
(cid:16) (cid:17) (cid:16) (cid:17) Inthissection,weassesstheeffectivenessofFlossinperiodictime
using the representations𝐺 X [𝑡 1 ,𝑡 2 ];𝜃 and𝐺 X [𝑡ˆ 1 ,𝑡ˆ 2 ];𝜃 . The seriesforecasting,classification,andanomalydetection.Ourpri-
FlossL𝑓 canbecombinedwithotherself-supervisedlossfunctions maryobjectiveinthisstudyistodeterminewhetherincorporating
usingaweightedcombinationL𝑓 andothercontrastivelearning Flosscanenhancetheperformanceofcurrentsupervisedandun-
lossL𝑐𝑙 totraintheencoder𝐺(·;𝜃).Duringthisstage,thedown- supervisedrepresentationlearningframeworks.
streamtasksareassumedtobeunknown.Finally,wefollowthe
sameprotocolas[10],whereadecoderistrainedontopofthe 4.1 Multivariatetimeseriesforecasting
(cid:16) (cid:17)
representations𝐺 X [𝑡ˆ,𝑡ˆ];𝜃 tohandlethedownstreamtasks.It 4.1.1 ExistingAlgorithms. Weconsiderthreerepresentativemul-
1 2
isimportanttonotethattheparameters𝜃 oftheencoderremain tivariatetimeseriesforecastingmodels:1).TS2Vec[47]:Thisisa
fixedduringthefinaltrainingphase. purelyunsupervisedlearningmodel.TS2Vecemployscontrastive
2)Pre-trainingthenFine-tuning:Theprocedureforpretraining learning in a hierarchical manner on augmented views. Its en-
inthesemi-supervisedsettingissimilartothatoftheunsupervised coderisbasedonalightweighttemporalconvolutionalnetwork.
setting.However,duringthefine-tuningstage,theoptimizedmodel Aftertraining,theencoderremainsfixed,andridgeregressionis
parameters𝜃 of𝐺(·;𝜃) arefurtherfine-tunedtotransitionfrom usedfortheforecastingtask.TointegrateFlossintoTS2Vec,we
𝐺(·;𝜃)to𝐺(·;𝜙)usingthedownstreamtasks. adapttheaugmentationstrategyofTS2Vectoincorporateperi-
3)Jointtrainingundersupervisedlearningsetting:Inthejoint odicshifts.Werandomlysampletwosegments [𝑡 1 − 𝑗 1 ,𝑡 2 +𝑘 1 ]
trainingapproach,boththeencoderanddecoderaretrainedsimul- and[𝑡 1 +𝑎𝑝ˆ[𝑡 1 ,𝑡 2 ]−𝑗 2 ,𝑡 2 +𝑎𝑝ˆ[𝑡 1 ,𝑡 2 ]+𝑘 2 ],where𝑎,𝑗 1 ,𝑗 2 ,𝑘 1 ,and
taneously.Inthisscenario,theFlossservesasanauxiliaryregular- 𝑘 2arerandomintegers.WealsoapplyTS2Vec’stimestampmask
izationtermduringtraining,providingadditionalself-supervision strategytothetimeseriessegments.Then,wetrainourmodel
signalsthatcontributetoenhancinggeneralization.Specifically,in usingaweightedsumofthefrequencylossandcontrastiveloss
thissetting,boththeunlabeledtimeseriesX ∈R𝑁×𝑇×𝐹 andtheir fromTS2Vecontherepresentationsofthesegments [𝑡 1 ,𝑡 2 ] and
5

[𝑡 1 +𝑎𝑝ˆ[𝑡 1 ,𝑡 2 ],𝑡 2 +𝑎𝑝ˆ[𝑡 1 ,𝑡 2 ]].Theestimatedperiodicityandfre- pretraining,thereconstructionlossissetto0.3,theFlossweight
quency loss are computed using discrete cosine transformation issetto1,andthemaskratioissetto0.4.Additionally,thebatch
(DCT).2)PatchTST[24]:ThismodelemploysavisionTransformer- sizeforWeather,Electricity,ETTh1,ETTh2,ETTm1,andETTm2
stylearchitectureformultivariatetimeseriesforecastinganduti- datasetsissetto8,whileforExchangeandILIdatasets,itissetto
lizespre-trainingandfine-tuningtechniquesfortraining.Inthe 16.
self-learningphase,themodelistrainedtoreconstructmaskedtime
4.1.4 ExperimentalResults. Table2showsthemultivariatelong-
seriespatches.Afterself-training,thetransformerisfine-tunedfor
termforecastingresults.Itshouldbenotedthatwererantheexper-
downstreammultivariateforecastingtasks.Inourapproach,Floss
imentsforfaircomparison;therefore,theperformanceofInformer,
collaborateswiththereconstructionlossinaweightedsumfashion
TS2Vec,andPatchTSTisslightlybetterthanwhatwasreportedin
duringtheself-trainingphase.3)Informer[52]:Thistransformer
theoriginalliterature.Weuseboldtexttohighlighttheimproved
modelisamilestoneintimeseriesforecastingandistrainedusing
performanceandredcolortoindicatetheaverageimprovements.
apurelysupervisedlearningapproach.WeincorporateFlossto
Thekeyobservationsareasfollows:
regularizeitshiddenrepresentation,specificallythelayerbefore
First,theinclusionofFlossenhancestheoverallperformanceof
thefinallayer.Themodelistrainedbycombiningtheforecasting
allthreerepresentativemodels.ThisdemonstratesthatFlosseffec-
lossandtheproposedfrequencylossusingaweightedsum.
tivelyutilizesinformativefeatureswithinthefrequencydomain,
Notonlydowechoosemodelsbasedontheparadigmsofdiffer-
leadingtoimprovedforecastingperformance.
enttrainingschemes,butthesizesofthesethreemodelsarealso
Secondly, Floss performs remarkably well on the Electricity
representative.TS2Vechasarelativelysmallstructure,Informeris
dataset,whichincludesthelargestnumber(321)oftimeseriesin
ofmediumsize,whilePatchTSTisalargermodel.
ourexperiments.Improvementsareobservedinallcases,indicating
4.1.2 PublicDatasets. Weassesstheeffectivenessofourproposed thatFlosshastheabilitytoencodesharedfrequencyinformation
Floss by evaluating its performance on 8 widely-used datasets, fromalargenumberoftimeseries,therebyenhancingforecasting
namely Weather, Exchange, Electricity, ILI, and 4 ETT datasets performance.
(ETTh1,ETTh2,ETTm1,ETTm2).Thesedatasetsarecommonly Thirdly,theinclusionofFlossdoesnotconsistentlyoutperform
employedforbenchmarkingpurposesandarepubliclyavailable themodelswithoutit.Thiscouldbeattributedtotherandomfactors
on[48].FortheTS2Vecmodel,weallocated60%ofthedatafor involvedinthetrainingprocesswithFloss,suchastherandom
training,20%forvalidation,and20%fortesting.ForthePatchTST samplingforperiodicitydetectionandtherandomshiftusingthe
andInformermodels,weallocated70%ofthedatafortraining,10% detectedperiodicity.Thesefactorsmightpreventthemodelsfrom
forvalidation,and20%fortesting.Thestatisticsofthosedatasets consistentlyleveragingvaluableinformation.Futurestudiesshould
aresummarizedinTable1. addressthisissuetoensuremoreconsistentresults.
AsdepictedinFigure4,thepredictionresultsofPatchTSTand
4.1.3 ExperimentalSettings. Followingpreviousworks[48,52,53],
TS2Vecw/oFlossarepresentedfortheETTh2andweatherdatasets.
weuseMeanSquaredError(MSE)andMeanAbsoluteError(MAE)
Inthelong-termforecastinghorizonofETTh2,Flossdemonstrates
as the core metrics to compare performance. All of the models
itssuperiorityinhandlingdistributionshiftsandtrend-seasonality
followthesameexperimentalsetupwithapredictionlengthof
𝑇 ∈{24,36,48,60}fortheILIdatasetand𝑇 ∈{96,192,336,720}for featuresincomparisontoTS2Vec.Thisadvantagecanbeattrib-
utedtotheenhancedabilityofFlosstoeffectivelyleveragetrend
otherdatasets,asmentionedintheoriginalpapers.ForPatchTST
andInformer,thelookbackwindowissetto𝐿=96.Weadhereto informationbyregularizingrepresentationsinthefrequencydo-
main.Figure4cfurtherdemonstratesthesuperiorperformance
thestandardprotocolandsplitalldatasetsintotraining,validation,
ofPatchTST-Flossinbothshort-termandlong-termforecasting
andtestsetsinchronologicalorderusingaratioof7:1:2.ForTS2Vec,
thelookbackwindowissetequaltothepredictionlength𝑇,and tasks,highlightingthesignificantbenefitsintroducedbyFlossin
thecontextofforecasting.
alldatasetsaresplitintotraining,validation,andtestsetsinthe
ratioof6:2:2(sameastheoriginalpaper[47]).
4.2 UnsupervisedTimeSeriesClassification
Thedetailedhyper-parameterconfigurationsofinformer-Floss
aresetasfollows:Thebatchsizeforalldatasetsissetto32.Loss withTS2Vec
weightsfordifferentdatasetsareasfollows:Weather(originalfore-
4.2.1 ExperimentalSetup. Inthissection,wecombineFlosswith
castinglossweight=0.3,Flossweight=2),Exchange(originalloss
thestate-of-the-art(SOTA)unsupervisedframeworkTS2Vec[47],
weight=0.3,Flossweight=0.7for96-stepaheadprediction,Floss
whichhasoutperformedseveralsupervisedlearningframeworks.
weight=0.8forallotherpredictionhorizons),Electricity(original
We utilize the same convolutional encoder as described in [47].
lossweight=0.3,Flossweight=2),ILI(originallossweight=0.3,
Additionally,wemodifythesamplingstrategyofTS2Vectocreate
Flossweight=0.5),ETTh1(originallossweight=0.3,Flossweight=
periodic shifts, aligning it with the settings used for the afore-
1),ETTh2(originallossweight=0.5,Flossweight=8),ETTm1,and
mentionedmultivariatetimeseriesforecasting.Followingthepre-
ETTm2(originallossweight=0.5,Flossweight=8).
trainingphase,wetrainanSVMclassifierwithanRBFkernelon
Thedetailedhyper-parameterconfigurationsofTS2Vec-Floss
topoftheinstance-levelrepresentationstoperformpredictions.
areasfollows:Thebatchsizeissetto16,theFlossweightforthe
contrastivelossofTS2Vecissetto1,andthelossforthecontrastive 4.2.2 PublicDatasets. Weevaluatetheeffectivenessofourpro-
lossofTS2Vecisassignedavalueof1.Similarly,thedetailedhyper- posed Floss by assessing its classification performance on two
parameterconfigurationsofPatchTST-Flossareasfollows:During widely-useddatasets:theUCRarchive[6]andUEAarchive[3].
6

Table1:Statisticsofpopulardatasetsforbenchmark.
Datasets ETTh1&ETTh2 ETTm1&ETTm2 Electricity Exchange-Rate Weather IL
Variates 7 7 321 8 21 7
Timesteps 17,420 69,680 26,304 7,588 52,696 966
Granularity 1hour 15min 1hour 1day 10min 1week
Table2:ErrorsofMultivariateTimeSeriesForecasting.Theimprovedresultsareinbold.
Dataset Informer Informer-Floss TS2vec TS2vec-Floss PatchTST PatchTST-Floss
Metric MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
96 0.427 0.460 0.277 0.370 1.719 0.921 1.278 0.840 0.144 0.192 0.125 0.173
192 0.346 0.414 0.361 0.402 1.650 0.925 1.360 0.882 0.191 0.241 0.183 0.229
Weather
336 0.583 0.543 0.407 0.408 1.949 1.043 1.318 0.876 0.244 0.280 0.232 0.271
720 0.916 0.705 0.837 0.668 2.718 1.287 1.559 0.972 0.314 0.331 0.301 0.325
96 0.841 0.746 0.753 0.705 0.498 0.527 0.422 0.484 0.099 0.224 0.099 0.225
192 1.132 0.847 1.180 0.859 1.112 0.781 0.851 0.687 0.210 0.331 0.210 0.330
Exchange
336 1.475 0.956 1.510 0.974 1.561 0.967 1.571 0.944 0.404 0.468 0.424 0.478
720 2.548 1.328 2.606 1.362 2.688 1.266 1.860 1.052 1.039 0.769 0.902 0.720
96 0.304 0.393 0.285 0.380 0.452 0.492 0.422 0.463 0.135 0.231 0.129 0.228
192 0.327 0.417 0.297 0.390 0.461 0.498 0.423 0.465 0.150 0.244 0.149 0.242
Electricity
336 0.333 0.422 0.302 0.396 0.472 0.491 0.426 0.468 0.165 0.259 0.159 0.260
720 0.351 0.427 0.325 0.406 0.544 0.547 0.513 0.516 0.203 0.292 0.201 0.287
24 5.940 1.720 5.460 1.580 3.349 1.168 3.686 1.276 2.883 1.189 2.962 1.200
36 4.999 1.508 5.300 1.541 3.671 1.244 4.131 1.399 2.986 1.195 2.850 1.169
ILI
48 5.004 1.542 5.319 1.570 4.150 1.324 4.153 1.364 3.411 1.287 2.899 1.174
60 5.403 1.554 5.631 1.589 4.231 1.340 4.185 1.359 3.207 1.233 3.142 1.227
96 0.941 0.769 0.801 0.695 0.699 0.592 0.804 0.666 0.373 0.402 0.368 0.397
192 1.007 0.786 0.867 0.713 0.789 0.643 0.876 0.704 0.403 0.419 0.403 0.421
ETTh1
336 1.038 0.784 1.140 0.859 0.907 0.709 0.969 0.750 0.443 0.449 0.432 0.441
720 1.144 0.857 1.184 0.883 1.084 0.800 0.969 0.750 0.482 0.490 0.451 0.472
96 3.283 1.502 2.763 1.372 1.034 0.806 1.065 0.808 0.287 0.344 0.285 0.342
192 4.371 1.815 4.110 1.713 1.973 1.118 2.177 1.163 0.363 0.392 0.359 0.386
ETTh2
336 4.215 1.642 3.910 1.656 2.831 1.319 2.398 1.238 0.375 0.409 0.376 0.405
720 3.656 1.619 3.222 1.541 2.561 1.353 2.578 1.331 0.411 0.443 0.399 0.428
96 0.657 0.575 0.629 0.582 0.611 0.551 0.565 0.519 0.282 0.339 0.281 0.328
192 0.725 0.619 0.744 0.647 0.675 0.589 0.616 0.553 0.329 0.369 0.319 0.356
ETTm1
336 0.725 0.619 1.053 0.819 0.725 0.621 0.681 0.593 0.358 0.387 0.349 0.378
720 1.133 0.845 0.997 0.778 0.810 0.671 0.763 0.643 0.411 0.415 0.397 0.411
96 0.555 0.462 0.488 0.514 0.443 0.495 0.371 0.447 0.164 0.254 0.158 0.233
192 0.695 0.686 0.715 0.652 0.615 0.598 0.546 0.561 0.220 0.294 0.197 0.252
ETTm2
336 1.270 0.871 1.119 0.805 0.975 0.765 0.863 0.721 0.271 0.327 0.248 0.319
720 3.171 1.367 3.414 1.374 2.024 1.093 1.977 1.104 0.354 0.381 0.339 0.355
Avg. 1.868 0.935 1.812 0.912 1.562 0.860 1.449 0.831 0.666 0.465 0.635 0.452
Improvements. ↓3.0% ↓2.4% ↓7.2% ↓3.4% ↓4.6% ↓2.8%
TheUCRarchiveconsistsof128univariatedatasets,whiletheUEA learnedfeatures,utilizingthetrainlabelsofthedataset.Finally,we
archivecontains30multivariatedatasets.Foreachdatasetconsid- outputthecorrespondingclassificationscoreonthetestset.For
ered,weutilizeitsoriginaltrain/testsplit.Weconductunsupervised thehyperparametersettings,batchsizeis16,thecontrastiveloss
trainingofanencoderusingthetrainsetofeachdataset.Subse- weightis1,Flossweightis1.
quently,wetrainanSVMclassifierwithaRBFkernelontopofthe
7

    
    
    
    
    
    
    
    
                            
predict horizon
eulav
TS2vec_FLoss     
Ground truth     
    
    
    
    
    
    
                            
predict horizon
(a)TS2Vec-FlossforecastingresultsonETTh2
eulav
TS2vec_FLoss 0.8
Ground truth
0.7
0.6
0.5
0.4
0.3
0.2
0 5 10 15 20
predict horizon
(b)TS2VecforecastingresultsonETTh2
eulav
Ground truth
PatchTST-FLoss
PatchTST
(c)PatchTSTandPatchTST-Flossforecasting
resultsonweather
Figure4:Illustrationofthelong-termforecastingoutputofmodelw/oFlossonETTm2andweatherdatasets(Y-axis:forecasting
horizon).
CD and3.0%across29UEAdatasets.Itisimportanttonotethatthe
7 6 5 4 3 2 1 periodicity detection module is applicable to all UCR and UEA
datasets,andcomprehensiveresultsofTS2Vec-Flossonalldatasets
TNC TS2Vec-Floss canbefoundinthesupplementarymaterials.CriticalDifference
DTW TS2Vec
TS-TCC T-Loss diagram[8]forNemenyitestsonalldatasets(including125UCR
TST
and29UEAdatasets)ispresentedinFigure5,whereclassifiersthat
arenotconnectedbyaboldlinearesignificantlydifferentinaverage
Figure5:CriticalDifference(CD)diagramofrepresentation
rank.Unlikeexistingbaselinesthatneglectperiodicinformation,
learningmethodsontimeseriesclassificationtaskswitha
Flossutilizeshierarchicalfrequencydomaincomparisonbetween
confidencelevelof95%.
differentperiodicviews,resultinginenhancedperformance.
4.2.3 Compared Baselines. We perform comprehensive experi- 4.3 UnsupervisedTimeSeriesClassification
mentsontimeseriesclassificationtoassesstheclassificationper- withTS-TCC
formanceofourapproach,incomparisontootherunsupervised
4.3.1 ExperimentalSetup. WecombineFlosswithanotherrepre-
timeseriesrepresentationmodels,namelyT-Loss[10],TS-TCC[9],
sentativemodelfortimeseriesrepresentationcalledTS-TCC[9].To
TST[49],andTNC[32].Additionally,weincludeDTW(Dynamic
evaluateourmodel,weconducthumanactivityrecognition,sleep
TimeWarping)[23]asabaseline,employingaone-nearest-neighbor
stage classification, and epileptic seizure prediction tasks using
classifierwithDTWasthedistancemeasure.
open-sourcedatasets.FollowingtheapproachofTS-TCC,weper-
formpre-traininganddownstreamtaskfine-tuningfor40epochs.
Table3:Timeseriesclassificationresultscomparedtoother
Duringthepre-trainingphase,weincorporateFlosswiththecon-
timeseriesrepresentationmethodson125UCRdatasetsand
trastivelossfunctionofTS-TCC.IncontrasttotheTS2Vecsetup,
29UEAdatasets.
weintroduceaseparateperiodicaugmentationalongsidethejitter
andscaleaugmentationofTS-TCC.Moreover,Flossiscomputed
Method 125UCRdatasets 29UEAdatasets basedsolelyontheoriginalandperiodicviewsofthetimeseries
data.TheencoderistrainedusingAdamwithaweightedsumof
DTW 0.727 0.650
FlossandtheoriginallossofTS-TCC.Wemaintainthesamehy-
TNC 0.761 0.677
perparametersasthosereportedin[9].Forthelossweights,the
TST 0.641 0.635
originallossweightis0.3andFlossweightis2.
TS-TCC 0.757 0.682
T-Loss 0.806 0.675
4.3.2 PublicDatasets. Weassesstheclassificationperformanceof
TS2Vec 0.830 0.712
ourproposedFlossbyevaluatingitonthreewidely-useddatasets:
TS2Vec-Floss 0.849 0.739
1.UCIHARdataset[2]:Thisdatasetcontainssensorreadingsfor
30subjectsperforming6activities.ThesamplerateoftheHAR
dataset is 60Hz. 2.Sleep-EDF [13]: This dataset includes whole-
4.2.4 ExperimentalResults. Theevaluationresultsaresummarized nightPSGsleeprecordings,withasamplingrateof100Hz.3.The
inTable3.Flossdemonstratesasignificantimprovementcompared EpilepticSeizureRecognitiondataset[1]:Thisdatasetconsistsof
tootherrepresentationlearningmethodsonboththeUCRand EEGrecordingsfrom500subjects,wherethebrainactivitywas
UEAdatasets.Specifically,Flossachievesanaverageincreaseof recordedforeachsubjectfor23.6seconds.Wesplitthedatainto60%,
2.3%inclassificationaccuracyoverTS2Vecacross125UCRdatasets 20%,and20%fortraining,validation,andtesting,respectively.For
8

theSleep-EDFdataset,weperformasubject-wisesplittoprevent
 
overfitting.Werepeattheexperimentsfivetimesusingfivedifferent
 
seeds.Duringthefine-tuningphase,wetrainalinearclassifier(a
single MLP layer) on top of a frozen self-supervised pretrained  
encodermodeltoperformclassification.  
4.3.3 Experimental Results. We report the accuracy (ACC) and  
macroF1score(MF1)oftheTS-TCC-Floss,rawTS-TCC[9],CPC[25]  
andSimCLR[5]inTable4.Similartothefindingsobservedinthe
TS2Vecexperiments,theintegrationofFlossyieldssignificanten-
hancementsintheperformanceofTS-TCC.Notably,anintriguing
aspectemergeswhenexaminingthethreedatasetsemployedinthis
study,whereinthesamplingperiodsarecomparativelyshort.Intu-
itively,discerningthepresenceofshort-termperiodicinformation
inthesedatasetsposesaformidablechallenge.However,employing
Flossstillyieldsnotableimprovementsacrossthesedatasets.This
phenomenoncanbeattributedtotheinherentcapacityofFlossto
autonomouslydetectperiodicity,therebyeffectivelycapturingim-
perceptiblequasi-periodicvariationswithinthedata.Consequently,
Flossexhibitsanautomaticmechanismforaugmentingtherep-
resentationalqualityofexistingmodels,therebyadvancingtheir
efficacy.
4.4 UnsupervisedAnomalyDetection
4.4.1 ExperimentalSetup. Foranomalydetection,wefollowthe
streaming evaluation protocol, where the task is to determine
whether the last point𝑡 is an anomaly. As same as in [47], we
definetheanomalyscoreasthedissimilaritybetweentherepre-
sentationscomputedfromtheoriginalseriesandtheonewitha
maskatthelasttimepoint.Weusethesamecomputationstrategy
asdescribedin[47]tocomputeanomalies.Twopublicdatasets
areusedtoevaluateourmodel.Yahoo1isabenchmarkdatasetfor
anomalydetection,whichincludes367hourlysampledtimeseries
withtaggedanomalypoints.KPI [27]includesmultipleminutely
sampledrealKPIcurvesfromvariousInternetcompanies.Inthe
normalsetting,eachtimeseriessampleissplitintotwohalves
accordingtothetimeorder,wherethefirsthalfisusedforunsu-
pervisedtrainingandthesecondhalfisusedforevaluation.We
alsoevaluatethecold-startproblem,inwhichtheTS2VecandFloss
encoderaretrainedontheItalyPowerDemanddatasetfromtheUCR,
asItalyPowerDemandexhibitsdailyperiodicity.Weuseprecision,
recallandF1-scoretomeasuretheperformanceofanomalydetec-
tion.Fornormalsettings,batchsizeissetto16,Flossweightis1,
contrastivelossweightis0.6.ForYahoo(Cold-start)andKPI(Cold-
start),Batchsizeis16,Flossweightis1,contrastivelossweightis
1.
4.4.2 ExperimentalResults. Theanomalydetectionperformance
ofTS2Vec-Floss,TS2Vec,andastrongunsupervisedlearningbase-
lineSR[27]arepresentedinTable5.Inthenormalsetting,Floss
improvestheF1scoreby1.19%ontheYahoo datasetand1.08%
ontheKPI datasetcomparedtoTS2Vec.ThisindicatesthatFloss
ismoresensitivetooutliersintimeseries,asitcapturesperiodic
dynamicsandexpressesfine-grainedinformationthroughhierar-
chicalpooling.Inthecoldstartsetting,theimprovementofFloss
1https://yahooresearch.tumblr.com/post/114590420346/a-benchmark-dataset-for-
time-series-anomaly
eulav
 
 
 
 
normal  
anomaly_label
 
(a)Anomalydetectionlabelsof
Yahoo
eulav
normal
anomaly-pred
(b)AnomalypredictedbyFloss
ofYahoo
Figure6:Anomalydetectionresults
onbothdatasetsisevenmorenoticeable(about10%onF1score),
demonstratingitsabilitytocapturegeneralperiodicinvariance
withstrongtransferability.
Wealsoprovidevisualizationsoftheanomalydetectionper-
formedbyFlossinFigure6.Inbothexamples,weobservethat
Flossaccuratelyidentifiesallanomalies.Itisworthnotingthatthe
onlynegativeresultobtainedbyFlossisstillincloseproximityto
thecorrespondinggroundtruthanomalytimepoint.
4.5 UnsupervisedAnomalyDetectionwith
otherModels
4.5.1 ExperimentalSetup. Inthisstudy,weperformexperiments
ontwoextensivelyutilizedanomalydetectiondatasets:MSL(Mars
ScienceLaboratoryrover)[16]andSMD(ServerMachineDataset)[30].
Weselectedthesetwodatasetsduetotheirpronouncedperiodic
patterns.Adheringtothepre-processingtechniquesoutlinedin
AnomalyTransformer[45],wedividedthedatasetintosequential,
non-overlappingsegmentsusingaslidingwindowapproach.Sub-
sequently,weemployedadeeplearningmodeltoreconstructthe
inputsamples,withtheresultingreconstructionerrorservingas
theinherentanomalyindicator.Toensureequitablecomparisons,
wesolelymodifiedthebasemodelsforreconstruction,employing
theconventionalreconstructionerrorasthestandardizedanomaly
criterionacrossallexperiments.Eachdatasetconsistsoftraining
andtestingsubsets,withvalidationsubsetsidenticaltothetest-
ingsubsets.Anomaliesareonlylabeledwithinthetestingsubset.
ThecalculationofFlossisintegratedintothe‘anomaly_detection‘
methodofeachmodel.Initially,weperformperiodicitydetection
ontheinputdataandextractperiodicsegments.Subsequently,we
extractfeaturesfromthesesegmentsandcalculatetheFloss.Fi-
nally, the Floss is incorporated into the model training process.
Throughouttheseexperiments,theFlossweightissetto1,andthe
reconstructionlossweightissetto0.3.
Aftertrainingthemodel,weanalyzethetrainingdatawithina
gradient-freecontext.Foreachdatabatch,weemploythetrained
modeltoreconstructitandcalculatethereconstructionerrorscores.
Toestablishtheanomalythreshold,weaggregatescoresfromboth
thetrainingandtestdatasets.Thiscombinedscoreassistsindeter-
miningthethreshold,basedonapredefinedanomalyratio.Sub-
sequently,wecomparethetestdatascoreswiththethresholdto
identifyanomalies.Scoresexceedingthethresholdareclassifiedas
anomalies,whilethosefallingbelowitarecategorizedasnormal.
9

Table4:TimeseriesclassificationresultscomparedtoothertimeseriesrepresentationmethodsonHAR,Sleep-EDFand
Epilepsy.
Datasets HAR Sleep-EDF Epilepsy
Metric ACC MF1 ACC MF1 ACC MF1
CPC 83.85±1.51 83.27±1.66 82.82±1.68 73.94±1.75 96.61±0.43 94.44±0.69
SimCLR 80.97±2.46 80.19±2.64 78.91±3.11 68.60±2.71 96.05±0.34 93.53±0.63
TS-TCC 90.37±0.34 90.38±0.39 83.00±0.71 73.57±0.74 97.23±0.10 95.54±0.08
TS-TCC-Floss 90.86±0.34 90.56±0.35 83.70±0.45 73.53±0.39 97.41±0.17 97.75±0.00
Table5:Univariatetimeseriesanomalydetectionresults.
   
   
Dataset Yahoo KPI
Metric F1 Prec. Rec. F1 Prec. Rec.    
SR 0.563 0.451 0.747 0.622 0.647 0.598    
TS2Vec 0.745 0.729 0.762 0.677 0.929 0.533
   
TS2Vec-FLoss 0.754 0.752 0.763 0.799 0.946 0.559
    Cold-start:
SR 0.529 0.404 0.765 0.666 0.637 0.697    
                         
TS2Vec 0.726 0.692 0.763 0.676 0.907 0.540
Timestamp
TS2Vec-FLoss 0.734 0.706 0.769 0.741 0.942 0.594
4.5.2 ModelsImprovedbyFloss. Weconsiderfournotablemulti-
variatetimeseriesforecastingmodelsasfeaturedin[41]:1).FED-
former[53]:ThismodelcombinesaTransformerarchitecturewith
theseasonal-trenddecompositionmethod.2).TimesNet[41]:Item-
ploysFastFourierTransform(FFT)toconvertthetimeseriesintoa
2Drepresentation,utilizingCNNsasthefoundationalframework.
3).Reformer[18]:ThisvariantoftheTransformerreplacesthecon-
ventionaldot-productattentionmechanismwithalocality-sensitive
hashingapproach.4).AconventionalTransformer[36].
4.5.3 Results. Table6illustratesthatFlosscontinuestoenhance
anomalydetectionperformance,yieldingimprovementsforthe
selectedmodelinmostinstances.Wehavesummarizedsomein-
triguingobservationsasfollows:1).Flossdemonstratesanotable
improvementintheF1scoresfornearlyallmodels,withtheex-
ception being TimesNet on the SMD dataset. This discrepancy
couldpotentiallyarisefromTimesNet’sadeptutilizationofperi-
odicinformationthroughitsinherentFFTblock.2).Remarkably,
theTransformer-FlosscombinationattainsthehighestF1score
ontheMSLdataset,surpassingeventhemoreintricateTimesNet
model.ThisoutcomesuggeststhatFlosscanimbueasimplermodel
withrobusttimeseriesprocessingcapabilities,offeringvaluable
insightsfordesigningmodelsinthecontextofanomalydetection
tasks.
Wedemonstratethereconstructioneffectsafterincorporating
Floss into the Transformer in Figure 7. It can be observed that
whenanomaliesoccur,theTransformermodelwithFlossexhibits
largerreconstructionerrorscomparedtotheregularTransformer
model.Floss,tosomeextent,preservestheconsistencyofperiodic
observationsinthespectrum.Manyanomaliesoftenmanifestas
significant changes in certain parts of the spectrum. Therefore,
eulav
reconstruction(floss)
reconstruction
origin
anomaly
Figure7:Visualizationofthereconstruction,truevalueand
anomaly.
Floss,bymaintainingtheconsistencyofperiodicspectralpatterns,
isadvantageousforanomalydetection.
4.6 DetailedStudyofFloss
AsFlossisdesignedasaplug-inlossfunction,therecanbevarious
instanceswithdifferentimplementationchoicesforeachmodule.In
thissection,acomprehensiveanalysisandcomparisonofdifferent
instancesofFlossareconducted.Inthefollowingdiscussions,we
considerthesimplestTS2Vecasthebaselineandcompareitwith
othervariantsonmultivariatetimeseriesforecastingforWeather,
Exchange,ILIandEttm1.Furthermore,weemployafixedsetof
hyperparameterstoensureafaircomparison.Itisworthnoting
thatsomeresultsmayappearworsethanthosereportedinTable2
becauseweonlypresentedthebestresultsinTable2
4.6.1 Effectsofperiodicdetectionmodule. Weinitiatedourinvesti-
gationbyexaminingtheinfluenceoftheperioddetectionmodule
onthemodel.AcomparativeanalysiswasconductedbetweenFloss
andtwoalternativemodels,namelyrandomanddayshift.InFig-
ure8a,’random’signifiestheutilizationofrandomaugmentation
duringeachcomparisonwithFloss,while’dayshift’denotesthe
shiftingoftimeseriesbyonedayateachstep,operatingunderthe
implicitassumptionthatalltimeseriesexhibitadailyperiodicity.
Theoutcomesunveiledthatbothmodelsincorporatingrandom
shiftinganddayshiftingexhibitedinferiorperformancecompared
totheTS2Vecmodel.
SinceFlossassumesthattherepresentationofperiodicshifts
issimilarinthefrequencydomain,augmentingtimeserieswith
10

Table6:Anomalydetectiontask.Wecalculatetheaccuracy,precision,recallandF1scoresforeachdataset.
Dataset MSL SMD
Metric Acc. Prec. Rec. F1 Acc. Prec. Rec. F1
FEDformer 0.9673 0.7714 0.7679 0.7857 0.9763 0.7732 0.6094 0.6816
FEDformer-Floss 0.9651 0.9059 0.7465 0.8185 0.9781 0.7846 0.6508 0.7114
TimesNet 0.9647 0.8955 0.7529 0.8180 0.9877 0.8788 0.8154 0.8459
TimesNet-Floss 0.9648 0.8959 0.7541 0.8187 0.9867 0.8684 0.8008 0.8332
Reformer 0.9638 0.9014 0.7372 0.8111 0.9780 0.7832 0.6524 0.7118
Reformer-Floss 0.9647 0.9055 0.7430 0.8163 0.9781 0.7832 0.6538 0.7127
Transformer 0.9634 0.8977 0.7366 0.8093 0.9780 0.7832 0.6524 0.7118
Transformer-Floss 0.9652 0.9062 0.7470 0.8189 0.9781 0.7828 0.6537 0.7125
periodidentificationandFFTforFlosscomputation.Ourinvestiga-
2.0 2.007 1.812 2.149 2.051 2 3 . . 5 0 2.259 2.767 tionyieldednoteworthyresults,unveilingthesignificanceofthe
1.5 2.0 1.953 combination.ItwasobservedthatemployingFFTforperiodidenti-
fication,whileleveragingDCTforspectraldensitycomputation,
1.0 0.952 0.903 0.969 0.955 1.5 1.018 1.117 1.198 yieldedthemostoptimaloutcomesintermsofperformance.
1.0
0.5 MSE 0.5 MSE 4.6.3 EffectsofFlossweights. Flossoperatesinconjunctionwith
MAE MAE
0.0 0.0 thelossofothermodels.Ourencoderistrainedusingaweighted
TS2vec period random day_shift DCT FFT DCT+FFT
sumofFlossandotherlossfunctions.Assigningahigherweightto
(a)Effectoftheperioddetection (b)FFTandDCT:peridoicityis Flossindicatesagreaterrelianceoncapturingperiodicinvariances.
moduleonforecastingerrors detectedbyFFT,DCT+FFT:peri-
ToinvestigatetheimpactoftheFlossweight,wesetthecontrastive
. odicityisdtectedbyDCT.
lossweightofTS2Vecto0.5andevaluatethemodel’sperformance
withdifferentlossweightsonthreedatasets.Theresultsarepre-
2.0 2.047 1.959 1.956 2.014 sentedinFigure8c.Thefindingsdemonstratetherobustnessofour
1.5 proposedmethodtothechoiceofweight.Theperformanceofthe
1.0 0.957 0.936 0.934 0.956 modelremainsconsistentacrossvariousweightsettings.However,
uponcloseranalysis,weidentifythattheweightrangebetween
0.5 MSE
0.3and0.5yieldsthebestperformance.
MAE
0.0
0.1 0.3 0.5 0.7 4.6.4 EffectsofhierarchicalFlosscomputation. AsdescribedinSec-
Floss weight
tion3.2,weemployahierarchicalFlosscomputationstrategytoal-
(c)EffectofFlossweightsonfore-
locategreaterweightstothelow-frequencycomponents.However,
castingerrors.
itisnoteworthythatemployinghierarchicalFlosscomputation
maynotbenecessaryforalldatasets.Theperformancecomparison
Figure8:Ablationresults.
withouthierarchicalcomputationispresentedinFigure9.Specifi-
cally,ourexperimentationontheelectricitydatasetdemonstrates
asubstantialenhancementinmodelperformancewhenutilizing
randomshiftsorassumingadailyshiftmightnoteffectivelycap-
hierarchicalFlosscomputation.Incontrast,fortheweatherdataset,
turetheunderlyingpatternsandperiodicbehavior.Thesefindings
weobservedthatrefrainingfromhierarchicalFlosscomputation
suggestthatconsideringgenericshiftsorassumingaspecificdaily
actuallyyieldedsuperioroutcomes.Whenemployinghierarchical
patternmightoverlookthenuanceddynamicsofthetimeseries.
computation,wetendtofocusmoreoncapturingthesimilarities
Notably,itwasobservedthatonlythemodelincorporatingthepe-
in the low-frequency components. On the other hand, without
rioddetectionmoduleforaugmentationoutperformedTS2Vec.This
employinghierarchicalcomputation,wetreatallfrequencycom-
highlightsthecriticalroleplayedbytheperioddetectionmodule
ponentsequally,includingthehigh-frequencycomponents.This
inenhancingthemodel’sperformance.
observationsuggeststhatindatasetssuchasweather,afterunder-
4.6.2 CombinationofDCTandFFT. Wealsoconductedanexam- goingperiodicvariations,theabstractrepresentationofthehigh-
inationofthecombinationofFastFourierTransform(FFT)and frequencycomponentsremainsrelativelyunchanged.Preserving
DiscreteCosineTransform(DCT)inrelationtoperiodidentifica- allfrequenciesbecomesmoreeffectiveforsuchdata.
tionandFlosscomputation.InFigure8b,’FFT’and’DCT’signify Moreover,weobservedasignificantimprovementinlong-term
theutilizationofFFTandDCTforFlosscalculation,respectively. forecastingperformancewhenhierarchicalFlosscomputationwas
Notably,bothapproachesemployFFTforperiodicdetection.On notemployedforweatherdataset.Thisfindingsuggeststhatforthe
theotherhand,’DCT+FFT’indicatestheapplicationofDCTfor weatherdataset,thelong-termvariationtrendmaybeconcealed
11

1.2
1.0
0.8
0.6
0.4
0.2
0.0 96 192 336 720 pred_len
ESM
1.035 1.03 1.121 1.165 3.0
2.5
2.0
0.513 1.5 0.422 0.423 0.426
1.0
without-hier
with-hier 0.5
0.0 96 192 336 720 pred_len
(a) Effect of the hierarchical
FlosscomputationonElectricity
dataset.
ESM
3.048 35
30
1.973
25
1.271 1.3661.361 1.426 1.318 1.439 20
without-hier
15 with-hier
10 0 100 200 300 400 500 600
sample
(b)EffectofthehierarchicalFloss
computationonWeatherdataset
.
Figure9:EffectofhierarchicalFlosscomputation.
withintheunchangedhigh-frequencycomponentsunderperiodic
shifts.Thesephenomenacallforfurtherin-depthresearchtodesign
morerobustmodelscapableofcapturingthesepatterns.
4.6.5 Representationvisualization. Figure10displaysthet-SNE
embeddingofTS2Vec-FlossandFlossonnineconsecutivedaysof
theElectricity andETTh1datasets.Thesedatasetsareknownto
exhibitpronounceddailyperiodicity.Consequently,theautomatic
periodic detection module is anticipated to capture this strong
periodicpattern.Inthisvisualization,themodelwithFlossproduces
amoreperiodiccloudstructure,characterizedbyareducedpresence
ofeasilydistinguishablehour-of-daygroupings.
 K R X U  R I  G D \  K R X U  R I  G D \
  
20 20
16 16
  12 12
8 8
   4 4
           0            0
(a)FlossrepresentationsonElec-(b) TS2Vec representations on
tricity Electricity
 K R X U  R I  G D \  K R X U  R I  G D \
   20 20
16 16
  12 12
8 8
   4 4
        0               0
(c) Floss representations on(d) TS2Vec representations on
ETTh1 ETTh1
Figure10:T-SNEvisualizationsofthelearnedrepresenta-
tionsofTS2Vec-FlossandTS2VeconElectricityandETTh1.
Differentcolorsrepresentdifferenthoursofday.
4.6.6 AccuracyofPeriodicityDetection. Weprovideacasestudy
(informer-FlossforElectricity)oftheperiodicitydetectionmod-
uleinFigure11.WecanobservethatFlosscanaccuratelycapture
yticidoirep
Figure11:PeriodicityDetectionResultswithinformer-Floss
forElectricity.
theperiodicities.Moreover,mostofthedetectedperiodicitiesare
approximatelyequalto24hours(1day),whichsupportsourmotiva-
tioninadoptingautomaticperiodicitydetectionforrepresentation
learning.
5 CONCLUSION
Inthisstudy,weaddressedthechallengeofeffectivelycapturing
periodicorquasi-periodicdynamicspresentinreal-worldtimese-
riesdatausingdeeplearningapproaches.Whiledeeplearninghas
shownimpressiveperformanceinvariousapplicationdomains,it
oftenstrugglestoadequatelyrepresenttheunderlyingperiodic
behaviorsintimeseriesdata.Tobridgethisgap,weintroducedan
unsupervisedmethodcalledFloss.Flossisdesignedtoautomatically
detectmajorperiodicitiesintimeseriesdataandutilizesperiodic
shiftandspectraldensitysimilaritymeasurestolearnmeaningful
representationswithperiodicconsistencyinthefrequencydomain.
ByseamlesslyincorporatingFlossintosupervised,semi-supervised,
andunsupervisedlearningframeworks,wedemonstrateditsversa-
tilityandabilitytoenhancetimeseriesanalysistasks.
Ourextensiveexperimentsoncommontimeseriesanalysistasks
showcasedtheeffectivenessofFloss.Itoutperformedstate-of-the-
artdeeplearningmodels,validatingitscapabilitytoautomatically
discoverperiodicdynamics.Theresultsunderscoretheimportance
ofconsideringdomain-specificknowledgeaboutperiodicbehaviors
toenrichthelearnedrepresentationsindeeplearningmodels.
Forfuturework,exploringadvancedmodelingtechniquesthat
caneffectivelycapturethehiddenlong-termpatternsincomplex
datasuchasweatherdataremainsapromisingdirection.Inthe
weatherdataset,weobservedasignificantimprovementinlong-
termforecastingperformancewhenhierarchicalFlosscomputation
was not employed. his finding suggests that for some datasets,
the long-term variation trend may be concealed within the un-
changed high-frequency components under periodic shifts. For
futurework,exploringadvancedmodelingtechniquesthatcanef-
fectivelycapturethehiddenlong-termpatternsinweatherdatare-
mainsapromisingdirection.Thismayinvolvetheincorporationof
domain-specificknowledge,suchasexternalfactors,toenhancethe
modelingprocess.Furthermore,extendingtheresearchtoconsider
morecomplexanddynamicscenarios,suchastimeseriespredic-
tionunderextremeweatherevents,couldpresentnewchallenges
andopportunitiesforadvancingtimeseriesanalysis.Flosssolely
addressesthefrequencydomainsimilarityofthemodelconcerning
temporalperiodicity.Integratingstate-of-the-arttechniques,such
asGraphNeuralNetworks(GNNs)andgraphspectralanalysis,
12

holdspromiseformodelingintertimeseriesinvarianceandopti- [19] YaguangLi,RoseYu,CyrusShahabi,andYanLiu.2018. DiffusionConvolu-
mizingtimeseriesanalysisperformance.ByleveragingGNNsand tionalRecurrentNeuralNetwork:Data-DrivenTrafficForecasting.InInterna-
tionalConferenceonLearningRepresentations. https://openreview.net/forum?
graphspectralanalysis,wecangainadeeperunderstandingof
id=SJiHXGWAZ
therelationshipsbetweenmultipletimeseries,capturingintricate [20] ZacharyCLipton,DavidCKale,RandallWetzel,etal.2016.Modelingmissing
temporaldependenciesandinterdependenciesamongtimeseries. datainclinicaltimeserieswithrnns.MachineLearningforHealthcare56(2016),
253–270.
[21] LauraAMcSweeney.2006.Comparisonofperiodogramtests.JournalofStatisti-
ACKNOWLEDGMENTS calComputationandSimulation76,4(2006),357–369.
[22] LIUMinhao,AilingZeng,LAIQiuxia,RuiyuanGao,MinLi,JingQin,andQiang
ThisworkwassupportedbyNationalNaturalScienceFoundation Xu.2021. T-WaveNet:ATree-StructuredWaveletNeuralNetworkforTime
SeriesSignalAnalysis.InInternationalConferenceonLearningRepresentations.
ofSichuanProvince(GrantNo.2023NSFSC1423),theTianfuEmei
[23] MeinardMüller.2007.Dynamictimewarping.Informationretrievalformusic
PlanofSichuanProvince,andtheFundamentalResearchFundsfor andmotion(2007),69–84.
theCentralUniversities. [24] YuqiNie,NamHNguyen,PhanwadeeSinthong,andJayantKalagnanam.2023.
ATimeSeriesisWorth64Words:Long-termForecastingwithTransformers.
InTheEleventhInternationalConferenceonLearningRepresentations. https:
REFERENCES //openreview.net/forum?id=Jbdc0vTOcol
[25] AaronvandenOord,YazheLi,andOriolVinyals.2018.Representationlearning
[1] RalphGAndrzejak,KlausLehnertz,FlorianMormann,ChristophRieke,Pe- withcontrastivepredictivecoding.arXivpreprintarXiv:1807.03748(2018).
terDavid,andChristianEElger.2001.Indicationsofnonlineardeterministic [26] JohnPaparrizos,YuhaoKang,PaulBoniol,RueySTsay,ThemisPalpanas,and
andfinite-dimensionalstructuresintimeseriesofbrainelectricalactivity:De- MichaelJFranklin.2022.TSB-UAD:anend-to-endbenchmarksuiteforunivariate
pendenceonrecordingregionandbrainstate. PhysicalReviewE64,6(2001), time-seriesanomalydetection.ProceedingsoftheVLDBEndowment15,8(2022),
061907. 1697–1711.
[2] DavideAnguita,AlessandroGhio,LucaOneto,XavierParra,JorgeLuisReyes- [27] HanshengRen,BixiongXu,YujingWang,ChaoYi,CongruiHuang,XiaoyuKou,
Ortiz,etal.2013.Apublicdomaindatasetforhumanactivityrecognitionusing TonyXing,MaoYang,JieTong,andQiZhang.2019.Time-seriesanomalydetec-
smartphones..InEsann,Vol.3.3. tionserviceatmicrosoft.InProceedingsofthe25thACMSIGKDDinternational
[3] AnthonyBagnall,HoangAnhDau,JasonLines,MichaelFlynn,JamesLarge, conferenceonknowledgediscovery&datamining.3009–3017.
AaronBostrom,PaulSoutham,andEamonnKeogh.2018.TheUEAmultivariate [28] DavidSalinas,ValentinFlunkert,JanGasthaus,andTimJanuschowski.2020.
timeseriesclassificationarchive,2018.arXivpreprintarXiv:1811.00075(2018). DeepAR:Probabilisticforecastingwithautoregressiverecurrentnetworks.Inter-
[4] TingChen,SimonKornblith,MohammadNorouzi,andGeoffreyHinton.2020. nationalJournalofForecasting36,3(2020),1181–1191.
Asimpleframeworkforcontrastivelearningofvisualrepresentations.InInter- [29] HuanSong,DeeptaRajan,JayaramanThiagarajan,andAndreasSpanias.2018.
nationalconferenceonmachinelearning.PMLR,1597–1607. Attendanddiagnose:Clinicaltimeseriesanalysisusingattentionmodels.In
[5] XinleiChenandKaimingHe.2021. Exploringsimplesiameserepresentation ProceedingsoftheAAAIconferenceonartificialintelligence,Vol.32.
learning.InProceedingsoftheIEEE/CVFconferenceoncomputervisionandpattern [30] YaSu,YoujianZhao,ChenhaoNiu,RongLiu,WeiSun,andDanPei.2019.Robust
recognition.15750–15758. anomalydetectionformultivariatetimeseriesthroughstochasticrecurrent
[6] HoangAnhDau,AnthonyBagnall,KavehKamgar,Chin-ChiaMichaelYeh,Yan neuralnetwork.InProceedingsofthe25thACMSIGKDDinternationalconference
Zhu,ShaghayeghGharghabi,ChotiratAnnRatanamahatana,andEamonnKeogh. onknowledgediscovery&datamining.2828–2837.
2019.TheUCRtimeseriesarchive.IEEE/CAAJournalofAutomaticaSinica6,6 [31] AndrzejTarczynskiandNajibAllay.2004.Spectralanalysisofrandomlysampled
(2019),1293–1305. signals:suppressionofaliasingandsamplerjitter.IEEETransactionsonSignal
[7] JanGDeGooijerandRobJHyndman.2006.25yearsoftimeseriesforecasting. Processing52,12(2004),3324–3334.
Internationaljournalofforecasting22,3(2006),443–473. [32] SanaTonekaboni,DannyEytan,andAnnaGoldenberg.2020. Unsupervised
[8] JanezDemšar.2006.Statisticalcomparisonsofclassifiersovermultipledatasets. RepresentationLearningforTimeSerieswithTemporalNeighborhoodCoding.
TheJournalofMachinelearningresearch7(2006),1–30. InInternationalConferenceonLearningRepresentations.
[9] EmadeldeenEldele,MohamedRagab,ZhenghuaChen,MinWu,CheeKeong [33] MachikoToyoda,YasushiSakurai,andYoshiharuIshikawa.2013.Patterndis-
Kwoh,XiaoliLi,andCuntaiGuan.2021.Time-SeriesRepresentationLearningvia coveryindatastreamsunderthetimewarpingdistance.TheVLDBJournal22
TemporalandContextualContrasting.InProceedingsoftheThirtiethInternational (2013),295–318.
JointConferenceonArtificialIntelligence,IJCAI-21.2352–2359. [34] RueySTsay.2005.Analysisoffinancialtimeseries.Johnwiley&sons.
[10] Jean-YvesFranceschi,AymericDieuleveut,andMartinJaggi.2019.Unsupervised [35] JacobTVanderPlasandŽeljkoIvezic.2015.Periodogramsformultibandastro-
scalablerepresentationlearningformultivariatetimeseries.Advancesinneural nomicaltimeseries.TheAstrophysicalJournal812,1(2015),18.
informationprocessingsystems32(2019). [36] AshishVaswani,NoamShazeer,NikiParmar,JakobUszkoreit,LlionJones,
[11] WayneAFuller.2009.Introductiontostatisticaltimeseries.JohnWiley&Sons. AidanNGomez,ŁukaszKaiser,andIlliaPolosukhin.2017. Attentionisall
[12] ShaghayeghGharghabi,Chin-ChiaMichaelYeh,YifeiDing,WeiDing,Paul youneed.Advancesinneuralinformationprocessingsystems30(2017).
Hibbing,SamuelLaMunion,AndrewKaplan,ScottECrouter,andEamonnKeogh. [37] MichailVlachos,PhilipYu,andVittorioCastelli.2005.Onperiodicitydetection
2019. Domainagnosticonlinesemanticsegmentationformulti-dimensional andstructuralperiodicsimilarity.InProceedingsofthe2005SIAMinternational
timeseries.Dataminingandknowledgediscovery33(2019),96–130. conferenceondatamining.SIAM,449–460.
[13] AryLGoldberger,LuisANAmaral,LeonGlass,JeffreyMHausdorff,PlamenCh [38] QingsongWen,KaiHe,LiangSun,YingyingZhang,MinKe,andHuanXu.
Ivanov,RogerGMark,JosephEMietus,GeorgeBMoody,Chung-KangPeng,and 2021. RobustPeriod:Robusttime-frequencyminingformultipleperiodicity
HEugeneStanley.2000.PhysioBank,PhysioToolkit,andPhysioNet:components detection.InProceedingsofthe2021InternationalConferenceonManagementof
ofanewresearchresourceforcomplexphysiologicsignals.circulation101,23 Data.2328–2337.
(2000),e215–e220. [39] GeraldWoo,ChenghaoLiu,DoyenSahoo,AkshatKumar,andStevenHoi.2021.
[14] MichaelGutmannandAapoHyvärinen.2010.Noise-contrastiveestimation:A CoST:ContrastiveLearningofDisentangledSeasonal-TrendRepresentationsfor
newestimationprincipleforunnormalizedstatisticalmodels.InProceedingsof TimeSeriesForecasting.InInternationalConferenceonLearningRepresentations.
thethirteenthinternationalconferenceonartificialintelligenceandstatistics.JMLR [40] GeraldWoo,ChenghaoLiu,DoyenSahoo,AkshatKumar,andStevenHoi.2022.
WorkshopandConferenceProceedings,297–304. ETSformer:ExponentialSmoothingTransformersforTime-seriesForecasting.
[15] TaoHong,PierrePinson,ShuFan,HamidrezaZareipour,AlbertoTroccoli,and arXivpreprintarXiv:2202.01381(2022).
RobJHyndman.2016.Probabilisticenergyforecasting:Globalenergyforecasting [41] HaixuWu,TenggeHu,YongLiu,HangZhou,JianminWang,andMingsheng
competition2014andbeyond.,896–913pages. Long.2023.TimesNet:Temporal2D-VariationModelingforGeneralTimeSeries
[16] KyleHundman,ValentinoConstantinou,ChristopherLaporte,IanColwell,and Analysis.InTheEleventhInternationalConferenceonLearningRepresentations.
TomSoderstrom.2018.Detectingspacecraftanomaliesusinglstmsandnonpara- https://openreview.net/forum?id=ju_Uqw384Oq
metricdynamicthresholding.InProceedingsofthe24thACMSIGKDDinterna- [42] XinleWu,DalinZhang,ChenjuanGuo,ChaoyangHe,BinYang,andChristianS
tionalconferenceonknowledgediscovery&datamining.387–395. Jensen.2021.AutoCTS:Automatedcorrelatedtimeseriesforecasting.Proceedings
[17] PrannayKhosla,PiotrTeterwak,ChenWang,AaronSarna,YonglongTian, oftheVLDBEndowment15,4(2021),971–983.
PhillipIsola,AaronMaschinot,CeLiu,andDilipKrishnan.2020. Supervised [43] YuankaiWu,HuachunTan,LingqiaoQin,BinRan,andZhuxiJiang.2018. A
contrastivelearning.AdvancesinNeuralInformationProcessingSystems33(2020), hybriddeeplearningbasedtrafficflowpredictionmethodanditsunderstanding.
18661–18673. TransportationResearchPartC:EmergingTechnologies90(2018),166–180.
[18] NikitaKitaev,LukaszKaiser,andAnselmLevskaya.2019.Reformer:TheEfficient
Transformer.InInternationalConferenceonLearningRepresentations.
13

[44] ZWu,SPan,GLong,JJiang,andCZhang.2019. GraphWaveNetforDeep TimeSeriesRepresentationLearning(KDD’21).AssociationforComputing
Spatial-TemporalGraphModeling.InThe28thInternationalJointConference Machinery,NewYork,NY,USA,2114–2124. https://doi.org/10.1145/3447548.
onArtificialIntelligence(IJCAI).InternationalJointConferencesonArtificial 3467401
IntelligenceOrganization. [50] XiyuanZhang,XiaoyongJin,KarthickGopalswamy,GauravGupta,Youngsuk
[45] JiehuiXu,HaixuWu,JianminWang,andMingshengLong.2021. Anomaly Park,XingjianShi,HaoWang,DanielleCMaddix,andYuyangWang.2022.First
Transformer:TimeSeriesAnomalyDetectionwithAssociationDiscrepancy.In De-TrendthenAttend:RethinkingAttentionforTime-SeriesForecasting.arXiv
InternationalConferenceonLearningRepresentations. preprintarXiv:2212.08151(2022).
[46] LingYangandShendaHong.2022. Unsupervisedtime-seriesrepresentation [51] XiangZhang,ZiyuanZhao,TheodorosTsiligkaridis,andMarinkaZitnik.2022.
learningwithiterativebilineartemporal-spectralfusion.InInternationalConfer- Self-supervisedcontrastivepre-trainingfortimeseriesviatime-frequencycon-
enceonMachineLearning.PMLR,25038–25054. sistency.arXivpreprintarXiv:2206.08496(2022).
[47] ZhihanYue,YujingWang,JuanyongDuan,TianmengYang,CongruiHuang, [52] HaoyiZhou,ShanghangZhang,JieqiPeng,ShuaiZhang,JianxinLi,HuiXiong,
YunhaiTong,andBixiongXu.2022.Ts2vec:Towardsuniversalrepresentation andWancaiZhang.2021. Informer:Beyondefficienttransformerforlongse-
oftimeseries.InProceedingsoftheAAAIConferenceonArtificialIntelligence, quencetime-seriesforecasting.InProceedingsoftheAAAIConferenceonArtificial
Vol.36.8980–8987. Intelligence,Vol.35.11106–11115.
[48] AilingZeng,MuxiChen,LeiZhang,andQiangXu.2023. AreTransformers [53] TianZhou,ZiqingMa,QingsongWen,XueWang,LiangSun,andRongJin.2022.
EffectiveforTimeSeriesForecasting? ProceedingsoftheAAAIConferenceon FEDformer:Frequencyenhanceddecomposedtransformerforlong-termseries
ArtificialIntelligence. forecasting.arXivpreprintarXiv:2201.12740(2022).
[49] GeorgeZerveas,SrideepikaJayaraman,DhavalPatel,AnuradhaBhamidipaty,
andCarstenEickhoff.2021.ATransformer-BasedFrameworkforMultivariate
14

