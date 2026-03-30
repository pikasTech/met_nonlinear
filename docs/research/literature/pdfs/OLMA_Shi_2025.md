# Page 1

OLMA: One Loss for More Accurate Time Series
Forecasting
TianyiShi1,†,ZhuMeng1,†,YueChen1,SiyangZheng1,FeiSu1,2,JinHuang3,
ChangruiRen3,ZhichengZhao1,2,*
1BeijingUniversityofPostsandTelecommunications
2BeijingKeyLaboratoryofNetworkSystemandNetworkCulture
3BeijingAcademyofBlockchainandEdgeComputing
†EqualContribution
*CorrespondingAuthor
{sty0622, bamboo, chenyue, zhengsiyang, sufei, zhaozc}@bupt.edu.cn,
{huangjin, rencr}@baec.org.cn
Abstract
Timeseriesforecastingfacestwoimportantbutoftenoverlookedchallenges.Firstly,
theinherentrandomnoiseinthetimeserieslabelssetsatheoreticallowerbound
for the forecasting error, which is positively correlated with the entropy of the
labels. Secondly, neural networks exhibit a frequency bias when modeling the
state-space of time series, that is, the model performs well in learning certain
frequencybandsbutpoorlyinothers,thusrestrictingtheoverallforecastingper-
formance. To address the first challenge, we prove a theorem that there exists
a unitary transformation that can reduce the marginal entropy of multiple cor-
related Gaussian processes, thereby providing guidance for reducing the lower
boundofforecastingerror. Furthermore,experimentsconfirmthatDiscreteFourier
Transform (DFT) can reduce the entropy in the majority of scenarios. Corre-
spondingly, to alleviate the frequency bias, we jointly introduce supervision in
thefrequencydomainalongthetemporaldimensionthroughDFTandDiscrete
WaveletTransform(DWT).Thissupervision-sidestrategyishighlygeneraland
can be seamlessly integrated into any supervised learning method. Moreover,
we propose a novel loss function named OLMA, which utilizes the frequency
domaintransformationacrossbothchannelandtemporaldimensionstoenhance
forecasting. Finally,theexperimentalresultsonmultipledatasetsdemonstratethe
effectivenessofOLMAinaddressingtheabovetwochallengesandtheresulting
improvementinforecastingaccuracy. Theresultsalsoindicatethattheperspectives
ofentropyandfrequencybiasprovideanewandfeasibleresearchdirectionfortime
seriesforecasting. Thecodeisavailableat: https://github.com/Yuyun1011/
OLMA-One-Loss-for-More-Accurate-Time-Series-Forecasting.
1 Introduction
Timeseriesforecastingisanimportantfundamentaltechniquewithbroadapplicationsinenergyman-
agement,financialtrading,transportationoptimization,weatherpredictionandhealthcaremonitoring.
Asthevolumeoftemporaldatacontinuestogrowrapidly,enhancingforecastingaccuracyhasbecome
anurgentneed. Asmachinelearningadvances,neuralnetworkshavebecomethedominantapproach
for time series forecasting. Most research efforts have concentrated on developing increasingly
sophisticated models to capture the underlying distributions of time series in real-world settings
([1,2,3,4]).
Preprint.Underreview.
5202
peS
52
]GL.sc[
2v76511.5052:viXra

---

# Page 2

However,fromadata-centricperspective,real-worldtimeseriesareinevitablycorruptedbypurely
randomnoise. Thisnoiseoverlaystheunderlyinglearnablepatterns,renderingperfectforecasting
impossible,regardlessofhowstrongtheneuralnetwork’scapacitytomodelthedatadistribution
is. [5,6]haveshownthattheestimationerrorofarandomvariable(orstochasticprocess)hasa
theoreticallowerbound,whichispositivelycorrelatedwithitsownentropy. However,theyhave
notfurtherinvestigatedwhetherthetheoreticallowerboundsoftheestimationerrorsdecreasewhen
multiplecorrelatedstochasticprocessesarepresent.
Inthiswork,weprovideaconcreteresultthattherenecessarilyexistsaunitarytransformationthat
decreasesthemarginalentropyofmultiplecorrelatedGaussianstochasticprocesses(thesumofthe
entropyoftheindividualprocesses). InSection3,adetailedproofofthistheoremispresented. By
modelingthelabeldataoftimeseriesasacombinationofalearnableinformativecomponentand
an unlearnable stochastic component, this conclusion provides theoretical guidance for reducing
thelowerboundofforecastingerror. Inparticular,ourexperimentsdemonstratethat,inpractical
scenarios, the DFT applied along the channel dimension serves as a unitary transformation that
reducesentropy.
Another prevalent challenge in time series forecasting is the frequency bias of neural networks
([7, 8, 9]). More precisely, neural networks tend to exhibit inherent differences in their learning
capacityindifferentfrequencybands. Infact,thisissueisnotconfinedtothedomainoftimeseries
forecasting,italsoposesasignificantchallengeinthefieldofcomputervision. [10]and[11]have
independentlytackledtheproblemoffrequencybiasbyintroducingfrequencydomaintransformation
modulesintotheirrespectivearchitectures.
To enhance the universality of using frequency domain transformations to alleviate the inherent
frequency bias of neural networks, we embed the transformation directly into the loss function,
enabling its application to any supervised learning method without altering the target network.
Specifically,inspiredby[12],weappliedtheDFTandDWTtothetemporaldimensionoftimeseries
labelsandpredictions.
In summary, we propose a novel supervision method for time series forecasting, termed OLMA,
whichappliesfrequencydomaintransformationstoboththechannelandtemporaldimensionsof
multivariatetimeseries. Thisapproachnotonlyreducestheentropyoflabelnoise,butalsomitigates
theinherentfrequencybiasofneuralnetworks. Sincethissolutionisformulatedasalossfunction,
it can be seamlessly integrated into any supervised model. The contributions of this paper are
summarizedbelow.
• Weanalyzetimeseriesforecastingerrorsfromtheperspectiveofentropy,thenwetheoret-
icallyandempiricallydemonstratethatthereexistsaunitarytransformationthatreduces
themarginalentropyofmultivariatecorrelatedGaussianprocesses. Moreover,ithasbeen
validatedthatconstructinglossinthefrequencydomainalongthetemporaldimensioncan
alleviatethefrequencybiasofneuralnetworks.
• WeproposeOLMA,asupervisionmethodthatappliesfrequencydomainlossalongboththe
channelandtemporaldimensionsoftimeseries. OLMAprovidesaminimalistyeteffective
approachtoreducingtheentropyoflabelnoisewhilemitigatingtheinherentfrequencybias
ofneuralnetworks. Moreover,itisplug-and-playandcanbeseamlesslyintegratedintoany
supervisedlearningframework.
• On9publictimeseriesforecastingdatasets,OLMAwasevaluatedwithmultiplerepresen-
tativebaselinemodelsanddemonstratedsuperiorperformancecomparedtotheiroriginal
timedomainsupervisionmethods. Ourworkcallsfortimeseriesforecastingresearchnot
onlytopursueinnovationsinmodelarchitecturesbutalsotodevotegreaterattentiontothe
intrinsicpropertiesofdata,inordertodiscovermoreefficientandgeneralizableapproaches
forimprovingforecastingaccuracy.
2 RelatedWorks
Timeseriesforecastingapproaches. Withtheriseofneuralnetworks,timeseriesmodelinghad
significantlyevolved,particularlywiththeadventofrecurrentneuralnetwork(RNN)-basedmethods
(e.g.,DeepAR[13],LSTNet[14],DA-RNN[15])andconvolutionalneuralnetwork(CNN)-based
approaches(e.g.,TCN[16],SCINet[17],TimesNet[4]). TheintroductionoftheTransformer[18]
2

---

# Page 3

architecture,knownforitsexceptionalmodelingcapacity,hadledtoasurgeinTransformer-based
forecastingmodels. EarlyexamplesincludedInformer[19],whichappliedTransformersdirectlyto
timeseriesforecasting;PatchTST[20],whichtreatedtimeseriessegmentsastokens;andiTrans-
former[3],whichintegratedbothtemporalandchannel-wisedependencies. Interestingly,DLinear
[21] demonstrated the surprising effectiveness of simple linear layers in time series forecasting,
prompting the development of multilayer perceptron (MLP)-based time domain models such as
TimeXer[22],TimeMixer[23],andWPMixer[24]. Furthermore,TimeLLM[25],AutoTime[26],
andTimeCMA[2]provedtheeffectivenessoflargelanguagemodels(LLMs)intimeseriesforecast-
ing. Recently,theMamba-basedmodel,S-Mamba[1]andAffirm[27],hadalsodemonstratedthe
superiorcapabilitiesofstatespacemodelsintimeseriesforecasting.
Forecasting errors from entropy perspective. [5] established information-theoretic bounds on
estimationandforecastingerrorsintimeseries,showingtheirdependenceontheconditionalentropy
ofthedata. [6]proposedaframeworktoevaluatetimeseriesforecastingalgorithmsbyrelatinglower
bounds of forecasting error to the conditional entropy rate of the series. Both suggested that the
lowerboundoftimeseriesforecastingerrorwaspositivelycorrelatedwiththeentropyofthelabels,
offeringaninsightfulperspective. Nevertheless,theydidnotexplorehowdecreasinginformation
entropycouldenhanceforecastingperformance.
Frequencybiasofneuralnetworks. [9]and[8]hadrigorouslydemonstratedthatneuralnetworks
exhibitfrequencybias. [10]tackledthefrequencybiasofdeepneuralnetworksbyusingafrequency-
based multi-grade learning approach to better capture high-frequency features. [28] addressed
the frequencybias ofMLPs by usingFourier featuremappings, enablingfaster learningof high-
frequencyfunctionsinlow-dimensionaltasks. [11]proposedFredformertomitigatefrequencybias
by learning features evenly across all frequency bands, improving forecasting of high- and low-
frequencycomponents. Thesemethodsaddressedfrequencybiasbydesigningnetworkarchitectures
thatincorporatefrequencydomaintransformations,buttheirapplicabilityisoftenlimitedtospecific
models.
3 Methodology
This chapter first theoretically demonstrates the possibility of reducing the marginal entropy of
multivariatetimeseries(Section3.1),andthenpresentsthedetailedformulationoftheOLMAloss
(Section3.2).
3.1 TheoreticalDerivation
Preliminaries. Letxbeacontinuousrandomvariablewithdifferentialentropyh(x),andletxˆbean
unbiasedestimateofxformedwithoutanysideinformation. Underthisconstraint,unbiasedness
requiresxˆ = E[x],sotheestimationerrore = x−xˆ = x−E[x]iszero-mean. Sincedifferential
entropy is translation-invariant, h(e) = h(x). According to the maximum entropy theorem for
continuous random variables with given mean and variance ([29]), for any random variable, its
entropyisupper-boundedbythatofaGaussianwiththesamevariance,
1
h(e)=h(x)≤ log(2πeVar(e)), (1)
2
whereVardenotesthevariance. Itcanberearrangedtogivethedesiredlowerboundonthemean
squarederror,
1
E[(x−xˆ)2]=Var(e)≥ 22h(x). (2)
2πe
TheequalityholdsifandonlyifxisGaussian([5]).
LetY ∈Rc×l denotethetimeserieslabelswithcdimensions(channels)andlengthl. Followedby
[30,31,32],thelabelisdecomposedintotwocomponentsasY =Z+N,whereZ,N ∈Rc×ldenote
components of learnable deterministic process (without randomness, the entropy is theoretically
zero)andcomponentsofunlearnablestochasticnoiserespectively. WeassumethatN isGaussian
([33,34])andmutuallyindependentacrossdifferenttimestepsforanalyticaltractability. Thus,the
lowerboundofN ∈Rl,thevariableithofN,is
i
l l
(cid:88) E[(N [t]−Nˆ [t])2]≥ (cid:88) 1 22h(Ni[t]) = l 22h(Ni). (3)
i i 2πe 2πe
t=1 t=1
3

---

# Page 4

Thisindicatesthatthelowerboundoftheforecastingerrorforeachtimeseriesvariableispositively
correlatedwithitsownentropy. Ifthereexistsaninvertibletransformationthatcanreduceentropy,
thelowerboundoftheforecastingerrorcanbedecreased,therebyimprovingtheforecastingaccuracy.
Inthisregard,weproposeTheorem1,whichdemonstratesthatsuchtransformationindeedexists.
Theorem1. IfmultipleGaussianstochasticprocessesareinternallyindependentandidentically
distributed(i.i.d.) butexhibitcorrelationsacrossprocesses,thentherenecessarilyexistsaunitary
transformationthatreducestheirmarginalentropy,i.e.,thesumoftheentropyofeachindividual
process.
BeforeprovingTheorem1,westate3lemmasthatwillbeusedintheproof.
Lemma 1. Let A ∈ Cn×n be a positive definite Hermitian matrix with main diagonal elements
a ,a ,...,a . ThenthedeterminantofAsatisfiestheinequality:
11 22 nn
n
(cid:89)
det(A)≤ a , (4)
jj
j=1
withequalityifandonlyifAisadiagonalmatrix.
ProofofLemma1.SinceAispositivedefiniteHermitian,itadmitsauniqueCholeskydecomposition
A=LL∗,whereLisalowertriangularmatrixwithl >0fori=1,2,...,n,andL∗denotesthe
ii
conjugatetransposeofL([35]). ThedeterminantofAcanbeexpressedas
n
(cid:89)
det(A)=det(LL∗)=|det(L)|2 =( l )2. (5)
ii
i=1
ThediagonalelementsofAaregivenbya =Σn |l |2 ≥|l |2,fori=1,2,...,n. Takingthe
ii k=i ik ii
productoftheseinequalitiesyields
n n n
(cid:89) (cid:89) (cid:89)
a ≥ |l |2 =( l )2 =det(A). (6)
ii ii ii
i=1 i=1 i=1
Equalityholdsifandonlyifa =l2 foralli,whichrequiresl =0forallk <i. ThisimpliesLis
ii ii ik
diagonal,andconsequentlyA=LL∗isalsodiagonal. Thus,Lemma1isproved.
Lemma2(UnitarydiagonalizationofaHermitianmatrix). LetA∈Cn×nbeaHermitianmatrix
(i.e.,A=A∗). ThenthereexistsaunitarymatrixU ∈Cn×n(i.e.,U∗ =U−1)andarealdiagonal
matrixΛ=diag(λ ,λ ,...,λ )suchthat
1 2 n
A=UΛU∗. (7)
ThecolumnsofU formanorthonormalbasisofCnconsistingofeigenvectorsofA,andthediagonal
entries of Λ are the corresponding eigenvalues. Furthermore, if A is positive definite, then all
eigenvaluesλ arepositive([36]).
i
Lemma3(Path-ConnectednessoftheUnitaryGroup). TheunitarygroupU(n)ispath-connected.
Thatis,foranytwounitarymatricesU,V ∈U(n),thereexistsacontinuousfunctionφ:[0,1]→
U(n)suchthatφ(0)=U andφ(1)=V ([37]).
ProofofTheorem1. LetG∈Rc×l denoteccorrelatedGaussianstochasticprocessesandlengthl.
ForeachprocessG ,sincethevariablesarei.i.d. Gaussian,itsentropyis
i
1 l
h(G )= log((2πe)ldet(Σ )) i. = i.d. log(2πeσ2), (8)
i 2 i 2 i
whereΣ isthecovariancematrixofG ,andσ2correspondstothevarianceofeachGaussianrandom
i i i
variable. ThesumofthemarginalentropyofGis
c c c
(cid:88) (cid:88) l l (cid:89)
h(G )= log(2πeσ2)= log((2πe)c σ2). (9)
i 2 i 2 i
i=1 i=1 i
Itisevidentthat
(cid:81)cσ2
istheproductofthefirst-orderprincipalminorsofthecovariancematrix
i i
ofG,whichisdenotedasS = 1GG∗,whereG∗ istheconjugatetransposematrixofG. Whena
l
unitarytransformationF isappliedtoG,thecovariancematrixS istransformedinto
u
1 1
S = FG(FG)∗ =F( GG∗)F∗ =FSF∗. (10)
u l l
4

---

# Page 5

AccordingtoLemma1,det(S)<
(cid:81)cσ2,becausetheG
sarecorrelated,theequalitydoesnotapply.
i i i
AccordingtoLemma2,thereisnecessarilyaunitarytransformationF suchthatS becomesa
v u
diagonalmatrix,whichmeansdet(S )= (cid:81)c σˆ2,whereσˆ2istheelementonthemaindiagonalof
u i=1 i i
S . Sinceaunitarytransformationdoesnotchangethedeterminantofamatrix,det(S)=det(S ).
u u
Insummary,thereexistsaunitarytransformationφ(0)=I (identitymatrix)suchthatthemaindiag-
onalofthecovariancematrixofGremainsunchanged,andtherealsoexistsaunitarytransformation
φ(1)=F thatreducesittoitsminimumvaluedet(S). Sincetheunitaryspaceiscontinuous(from
v
φ(0)=Itoφ(1)=F ),therangeofattainablevaluesformsaclosedrealvalueinterval(from
(cid:81)cσ2
v i i
todet(S)),therenecessarilyexistsaF =φ(λ),0<λ<1suchthatdet(S)< (cid:81)c σˆ2 < (cid:81)cσ2,
λ i=1 i i i
that is the product of the main diagonal entries is reduced. In conjunction with Eq. 9, it can be
rigorouslydeducedthattherenecessarilyexistsaunitarytransformationthatreducesthemarginal
entropyoftheGaussianprocess. Thus,Theorem1isproved.
3.2 OLMALoss
TheforecastingofthemodelisdenotedasYˆ ∈Rl×c,andthecorrespondinglabelasY ∈Rl×c. Ac-
cordingtoTheorem1,theDFTappliedalongthechanneldimensionactsasaunitarytransformation
thatcanreducethemarginalentropyofmultivariatetimeserieslabels(theexperimentalvalidationis
presentedinSection4). Thecomputationcanbeexplicitlyformulatedas
L(c) =α (cid:88) l−1(cid:13) (cid:13)F (Yˆ )−F (Y ) (cid:13) (cid:13) , (11)
olma (cid:13) f t,: f t,: (cid:13)
1
t=0
where0<α<1isthehyperparametertoadjustthestrengthofL(c) ,Yˆ andY areforecasting
olma t,: t,:
andlabelsequenceofthetthtimesteprespectivelyandF representsDFTthatdetailedcalculationis
f
c−1
(cid:88)
F (Y )[k]= Y ·e−2πikn/c, k =0,1,...,c−1, (12)
f t,: t,n
n=0
whereiistheimaginaryunit.
Toalleviatethefrequencybiasofneuralnetworks,wealsoapplyfrequencydomaintransformations
directlyatthesupervisionstage. Thisprovidesthemostconvenientwaytoadapttoallsupervised
timeseriesforecastingmodels. Inspiredby[12], weperformDFTandDWTalongthetemporal
dimensionofthetimeseries.ApplyingafullDFTtolongnon-stationarysignalsmayyieldmisleading
frequencyrepresentations,sinceitassumesglobalstationarityandoverlookslocalizedvariations. In
contrast,WaveletTransform,alocalizedalternativetotheshort-timeFourierTransform,captures
bothtemporalandfrequencyinformation,makingiteffectiveformodelinglong-termnon-stationary
patternsintimeseries. ThecomputationofL(t) is
olma
L(t) =β (cid:88) c−1(cid:13) (cid:13)F (Yˆ )−F (Y ) (cid:13) (cid:13) +γ (cid:88) c−1(cid:13) (cid:13)F (Yˆ )−F (Y ) (cid:13) (cid:13) , (13)
olma (cid:13) f :,i f :,i (cid:13) (cid:13) w :,i w :,i (cid:13)
1 1
i=0 i=0
whereYˆ andY areforecastingandlabelsequenceoftheith channelrespectively,thehyperpa-
:,i :,i
rametersβ andγ (where0 < β,γ < 1andα+β+γ = 1)areintroducedtoadjustthestrength
of alignment in the Fourier and Wavelet domains, respectively, and F denotes the DWT. For
w
k =1,2,...,l/2,thereare
cA +cD cA −cD
Y = k√ k, Y = k√ k, F (Y )={cA ,...,cA ,cD ,...,cD }.
2k−1,i 2k,i w :,i 1 k 1 k
2 2
(14)
wherecAistheapproximationcoefficientandcDisthedetailcoefficientofY . Notethatsquared
:,i
orhigher-ordernormsfortheerrorarenotadopted. Because,inmosttimeseriesdata,themagnitude
offrequencycomponentsvariessignificantlyacrossdifferentbandsinthefrequencydomain. In
particular,low-frequencycomponentstypicallydominateandexhibitmuchlargeramplitudesthan
high-frequencycomponents. Toensurestabilityoftheloss,theL1normisadopted. Finally,the
OLMAlossL isdefinedasalinearcombinationofthefrequencydomainlossesalongthetemporal
O
andchanneldimensions,
L =L(t) +L(c) . (15)
O olma olma
5

---

# Page 6

Figure1: Entropychangesafterapplyingchannel-wiseDFTindifferenttimeseriesdatasets.
4 Experiments
4.1 LowEntropyRepresentationofTimeSeries
InspiredbyTheorem1,weaimtodeveloparepresentationmethodthatreducesthemarginalentropy
oftimeseriesalongthetemporaldimension. SincetheDFTdecomposesasequenceintodifferent
frequency components, we apply it along the channel dimension so that energy from the same
frequencybandisconcentratedwithinthesamechannel. Thisreducestheuncertaintywithineach
individualchannelandtherebydecreasestheentropyofthetimeseries. Fortheoriginalreal-valued
timeseriesY ∈ Rl, wecomputeitsShannonentropy. Becausethetrueprobabilitydistribution
:,i
ofeachvalueisinaccessible,wereplaceitwiththeempiricalprobabilityestimatedfromthedata.
Concretely, thevaluesofY arefirstpartitionedintoM equal-width, non-overlappingbins. Let
:,i
n =number(Y ∈M ),j =0,1,...l−1denotethenumberofseriespointsthatfallintoM ,
k j,i k k
thekthintervalofM. Theempiricalprobabilityp =n /l. Therefore,theShannonentropyofY
k k :,i
canbeexpressedas
M
(cid:88)
H(Y )=− p log(p ), (16)
:,i k k
k=1
Since Y becomes a complex-valued sequence after the DFT, we treat it as a two-dimensional
:,i
discretesequenceandcomputeitsjointentropyfollowingthemethoddescribedabove. Followed
by[1,3,4],ETT(4subsets),Exchange,Illness(ILI),Weather,Electricity(ECL),Trafficdatasets
areusedinourexperiments(seeAppendixA.1fordatasetdetails). Eachdatasetissegmentedinto
96-lengthsegmentsalongthetemporaldimension. AsshowninFigure1,theentropyofeachsegment
is indicated with a scatter plot, where green represents the entropy of the original sequence and
orangerepresentstheentropyafterapplyingDFTalongthechanneldimension. Evidently,inmost
scenarios,representingtimeseriesusingDFTalongthechanneldimensioncansignificantlyreduce
theirmarginalentropy,whichexperimentallyvalidatesTheorem1. Moreover,thisrepresentation
significantlyreducestheentropydifferencesacrossdifferenttimeseriessamples,whichindicatesa
moreuniformdistributionofinformation,withoutextremeredundancyoruncertainty. However,fora
fewdatasets,suchasECL,thiscanleadtoanincreaseinentropy,whichmayaffecttheforecasting
performanceofcertainmodels(adetaileddiscussionisprovidedinSection4.3and4.4).
6

---

# Page 7

Figure2: (a)denotestheforecastingerroracrossdifferentfrequencybandsontheETTh1testset
duringtraining,reflectingthefrequencybiasofthenetwork. (b)and(d)visualizetheforecasting
andgroundtruthvaluesinthetimeandfrequencydomainsundertimedomainMSEsupervision,
respectively. (c)and(e)visualizetheforecastingandgroundtruthvaluesinthetimeandfrequency
domainsunderOLMAsupervision,respectively.
4.2 AlleviationofFrequencyBias
Followedby[7],wequantifyfrequencybiasbymeasuringtheforecastingerrorsofdifferentfrequency
bands. AsevidencedbythetwogreencurvesinFigure2(a), themodelmanifestsapronounced
frequency bias, exhibiting a preferential tendency toward capturing high-frequency components.
ItisworthnotingthattheDLinearmodelemployedinthisexperimentwasspecificallydesigned
tobalancelow-andhigh-frequencylearningthroughparallelseasonalandtrendbranches,yetthe
issueoffrequencybiasstillpersists. AfterapplyingOLMAsupervision,themodel’sabilitytolearn
low-frequency components is substantially enhanced, while its ability to capture high-frequency
componentsremainslargelyunaffected. Thisprovidesempiricalevidencethatapplyingsupervision
inthefrequencydomainallowsthenetworktoaccessinformationacrossallfrequencybandsmore
directly,effectivelyalleviatingitsintrinsicfrequencybias.
Forgreaterclarity,wevisualizetheforecastinginboththetimeandfrequencydomains. Asillustrated
inFigure2(b),thegroundtruthexhibitsanoverallupwardtrend,whichismanifestedprimarilyinthe
low-frequencycomponents. However,undertimedomainsupervision,thenetworkexhibitslimited
capacityincapturinglow-frequencyinformation,andconsequently,suchatrendcannotbeadequately
fitted. Incontrast,undertheguidanceofOLMA,thenetworkexhibitsamarkedlyimprovedcapacity
toapproximatethetrendcomponent,asshownintheplot(c). Inaddition,comparisonofplots(d)
and(e)revealsthatOLMAsupervisionprovidesamorefaithfulapproximationoftheprimaryand
secondaryspectralpeaksinthelow-frequencybandthanconventionaltimedomainMSE.Thisserves
ascompellingevidenceforthenetwork’senhancedproficiencyinmodelinglow-frequencystructures,
substantiatingtheclaimthatdirectfrequencydomainsupervisionprovidesaprincipledsolutionto
alleviatefrequencybias. Inaddition,wealsodiscusstheissueoffrequencybiasfromtheperspective
ofthedata,seeAppendixA.2fordetails.
4.3 PerformanceofOLMA
WefurthervalidatetheeffectivenessofOLMAbyincorporatingitintoseveralstate-of-the-artbaseline
modelsacrossdiversesettings. ThesemethodsincludeMamba-basedS-Mamba[1],LLM-based
TimeCMA[2],Transformer-basediTransformer[3],CNN-basedTimesNet[4],linear-basedDLinear
[21],andMLP-basedTimeMixer[23]andTimeXer[22]. Theaverageforecasterrorsoffourhorizons
7

---

# Page 8

Table1: PerformanceofOLMAondifferenttimeseriesdatasets. Lowerforecastingerrorsindicate
betterperformance. Thebestresultsarehighlightedinbold. TDLdenotesthetemporaldomainloss
(MSE)correspondingtoeachbaseline.
S-Mamba TimeCMA iTransformer TimesNet TimeXer TimeMixer DLinear
Dataset Loss
MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
TDL 0.455 0.450 0.438 0.441 0.454 0.448 0.460 0.455 0.437 0.437 0.447 0.440 0.423 0.437
ETTh1
OLMA 0.432 0.426 0.433 0.434 0.444 0.437 0.445 0.443 0.436 0.429 0.435 0.429 0.413 0.424
TDL 0.381 0.405 0.407 0.420 0.383 0.407 0.407 0.421 0.368 0.396 0.374 0.401 0.431 0.447
ETTh2
OLMA 0.362 0.391 0.388 0.408 0.376 0.400 0.401 0.416 0.363 0.389 0.368 0.394 0.415 0.434
TDL 0.398 0.405 0.393 0.406 0.407 0.410 0.411 0.418 0.382 0.397 0.381 0.396 0.357 0.379
ETTm1
OLMA 0.379 0.386 0.383 0.391 0.397 0.398 0.393 0.402 0.377 0.385 0.378 0.385 0.353 0.372
TDL 0.288 0.332 0.290 0.333 0.288 0.332 0.296 0.332 0.274 0.322 0.275 0.323 0.267 0.332
ETTm2
OLMA 0.278 0.319 0.285 0.323 0.283 0.324 0.285 0.323 0.271 0.315 0.273 0.319 0.263 0.322
TDL 0.251 0.276 0.248 0.281 0.258 0.278 0.259 0.286 0.241 0.271 0.240 0.272 0.246 0.300
Weather
OLMA 0.241 0.265 0.245 0.275 0.255 0.275 0.257 0.281 0.239 0.266 0.242 0.266 0.240 0.280
TDL 0.367 0.408 0.446 0.457 0.360 0.403 0.408 0.439 0.372 0.409 0.352 0.398 0.367 0.416
Exchange
OLMA 0.350 0.398 0.416 0.441 0.353 0.401 0.403 0.434 0.349 0.398 0.342 0.393 0.315 0.394
TDL 2.027 1.066 1.864 0.873 2.552 1.109 2.263 0.928 2.143 0.961 2.088 0.977 2.169 1.041
ILI
OLMA 1.806 0.853 1.858 0.869 2.516 1.097 2.045 0.869 2.124 0.944 1.739 0.828 2.049 0.970
TDL 0.170 0.265 0.213 0.307 0.178 0.270 0.194 0.296 0.171 0.270 0.182 0.273 0.166 0.264
ECL
OLMA 0.167 0.262 0.200 0.296 0.169 0.258 0.188 0.288 0.172 0.268 0.183 0.272 0.167 0.263
TDL 0.414 0.276 0.697 0.370 0.428 0.282 0.625 0.331 0.466 0.287 0.499 0.322 0.434 0.295
Traffic
OLMA 0.412 0.265 0.696 0.370 0.421 0.270 0.616 0.319 0.468 0.277 0.496 0.308 0.433 0.293
{96,192,336,720}fordifferentmethodsondifferentdatasets(ILIare{12,24,48,96})areshown
inTable1(completeexperimentalresultsanddetailedsettingofhyperparametersareprovidedinthe
AppendixA.3). Inaccordancewithcommonlyadoptedprotocols,eachdatasetisdividedintotraining
(60%),validation(20%)andtest(20%)subsets. TheexperimentalresultsindicatethatOLMA,when
directlyintegratedintodiversebaselinemodels,consistentlyoutperformsthewidelyadoptedtime
domainsupervisionapproaches. Moreintriguingly,OLMAeliminatestherelianceontimedomain
supervisionaltogether,insteadrepresentingtimeserieslabelspurelywithinthefrequencydomain.
ThisphenomenoncanbeexplainedbyParseval’sTheorem[38].
Parseval’sTheorem. Letx(t)bethetimedomainsignalofinterest. Thetotalenergyofthesignal
inthetimedomainisequaltothatinthefrequencydomain. Mathematically, thisrelationshipis
expressedas
(cid:90) ∞ (cid:90) ∞
|x(t)|2dt= |X(f)|2df (17)
−∞ −∞
whereX(f)istheFourierTransformofx(t). Thisindicatesthatthefrequencydomainrepresentation
ofasignalpreservesitstotalenergyandonlyredistributesitacrossfrequencycomponents. Therefore,
applying supervision in the frequency domain does not result in any energy loss, and retains the
fullinformationalcontentoftheoriginalsignal. Thus, combiningtimedomainsupervisionwith
OLMAdoesnotprovideanyadditionalinformationgain(experimentalvalidationisprovidedinthe
AppendixA.4).
Consequently,OLMAconstitutesaninformation-losslessrepresentationoftimeseriesthateffectively
reduces theirintrinsic disorder, asmeasured by entropy. Nevertheless, asshownin Figure 1, for
datasets characterized by more intricate channel interactions, exemplified by ECL, the Fourier
Transformcaninadvertentlyincreasetheentropyofthetimeseries. Theperformanceofmethods
such as DLinear and TimeMixer on the ECL, as reported in Table 1, substantiates this finding.
Becausetheirarchitecturesarerelativelysimple,thesemodelsareunabletocounteracttheincrease
indisorderinducedbyentropygrowth,resultinginlimitedperformanceimprovement.
4.4 Ablations
A detailed ablation study is conducted on the ETTh1 and ECL dataset using iTransformer and
TimeMixertoexaminethecontributionsoftwofrequencydomainlosscomponentsinOLMA,those
are the channel-wise L(c) and the temporal-wise L(t) . In Table 2, “Channel" represents L(c)
olma olma olma
and “Temporal" represents L(t) . Both are discarded, denoting the MSE loss originally used by
olma
themodels. FordatasetsuchasETTh1,wherechannel-wiseDFTeffectivelyreducesinformation
entropy, iTransformer and TimeMixer achieve enhanced forecasting performance by leveraging
8

---

# Page 9

Table2: AblationstudyofOLMAonchannelandtemporallosses.
iTransformer TimeMixer
Channel Temporal
ETTh1 ECL ETTh1 ECL
✗ ✗ 0.454 0.448 0.178 0.270 0.447 0.440 0.182 0.273
✓ ✗ 0.448 0.440 0.172 0.263 0.439 0.433 0.197 0.284
✗ ✓ 0.451 0.444 0.175 0.262 0.442 0.436 0.183 0.274
✓ ✓ 0.444 0.437 0.169 0.258 0.435 0.429 0.183 0.272
Figure3: ImpactoftheratiobetweenchannelandtemporallossesinOLMAonforecastingerror.
solelyL(c) . However,fordatasetlikeECL,wherechannel-wiseDFTincreasesentropy,MLP-based
olma
predictorssuchasTimeMixeraresubstantiallyaffected, whereasTransformer-basedmodelslike
iTransformerremainlargelyunaffected. Moreover,thestabilizationofentropydistributionfurther
enhancesiTransformer’sforecastingperformance. Thisfurthercorroboratestheanalysispresentedin
Section4.1.
4.5 ImpactofChannelandTemporalLossesonForecastingPerformance
Intheablationstudy,wehavealreadydemonstratedthatjointlyapplyinglossesalongboththechannel
andtemporaldimensionsyieldssuperiorforecastingperformance.However,anopenquestionremains
thatdoestherelativeweightingbetweenthetwolossesexertasignificantinfluenceonforecasting
accuracy? Tothisend,wetaketheWeatherdatasetasanexampleandconductdetailedexperiments
usingiTransformer. Specifically,asshowninFigure3,wevarytheproportionofthechannelloss
across {0.1, 0.3, 0.5, 0.7, 0.9}, and evaluate the model under four different forecasting lengths
{96,192,336,720}. Itisevidentthatevenundersubstantialvariationsintherelativeweightingof
channelandtemporallosses,themodel’sforecastingperformanceremainslargelyunaffected,which
impliesthatwithinarelativelywiderangeofweightassignments,themodelforecastingperformance
remainsstableandstrong,eliminatingtheneedfortediousandexpensivehyperparameterfine-tuning.
AdditionalexperimentsareprovidedintheAppendixA.5.
5 ConclusionsandFutureDirections
Conclusions. Weprovethatunitarytransformationscanreducethemarginalentropyofmultivariate
time series, yielding low-entropy representations that enhance forecasting accuracy. Meanwhile,
wemitigatefrequencybiasofneuralnetworksbyenforcingsupervisiondirectlyinthefrequency
domain. Asacombinationofthesetwosolutions,OLMAprovidesaminimalistapproachthatcanbe
seamlesslyintegratedintoanysupervisedlearningmodel.
Futuredirections. Werevealtwooverlookedissuesthatoffervaluableguidanceforfutureresearch.
Firstly,weanalyzetimeseriesrepresentationsfromtheperspectiveofentropy. Althoughwehave
proposedaneffectiverepresentationforentropyreductionintimeseries,thisapproachstillleaves
considerable room for improvement. Future work should strive to identify representations with
minimal entropy in order to further lower the fundamental bound of forecasting error. Secondly,
futureworkshouldassessmodelperformanceacrossdifferentfrequencybandsintimeseriesand
developmoretargetedsolutionsaccordingly.
References
[1] ZihanWang,FanhengKong,ShiFeng,MingWang,XiaocuiYang,HanZhao,DalingWang,andYifei
Zhang. Ismambaeffectivefortimeseriesforecasting? Neurocomputing,619:129178,2025.
9

---

# Page 10

[2] ChenxiLiu,QianxiongXu,HaoMiao,SunYang,LingzhengZhang,ChengLong,ZiyueLi,andRuiZhao.
Timecma:Towardsllm-empoweredtimeseriesforecastingviacross-modalityalignment. arXivpreprint
arXiv:2406.01638,2024.
[3] YongLiu,TenggeHu,HaoranZhang,HaixuWu,ShiyuWang,LintaoMa,andMingshengLong. itrans-
former:Invertedtransformersareeffectivefortimeseriesforecasting. arXivpreprintarXiv:2310.06625,
2023.
[4] HaixuWu,TenggeHu,YongLiu,HangZhou,JianminWang,andMingshengLong. Timesnet:Temporal
2d-variationmodelingforgeneraltimeseriesanalysis. arXivpreprintarXiv:2210.02186,2022.
[5] SongFang,MikaelSkoglund,KarlHenrikJohansson,HideakiIshii,andQuanyanZhu. Genericvariance
boundsonestimationandpredictionerrorsintimeseriesanalysis:Anentropyperspective. In2019IEEE
InformationTheoryWorkshop(ITW),pages1–5.IEEE,2019.
[6] SaeyoungRho. Estimatinglowerboundsfortimeseriespredictionerror. PhDthesis,Massachusetts
InstituteofTechnology,2020.
[7] Annan Yu, Dongwei Lyu, Soon Hoe Lim, Michael W Mahoney, and N Benjamin Erichson. Tuning
frequencybiasofstatespacemodels. arXivpreprintarXiv:2410.02035,2024.
[8] JonasKiesslingandFilipThor. Acomputabledefinitionofthespectralbias. InProceedingsoftheAAAI
ConferenceonArtificialIntelligence,volume36,pages7168–7175,2022.
[9] YuanCao, ZhiyingFang, YueWu, Ding-XuanZhou, andQuanquanGu. Towardsunderstandingthe
spectralbiasofdeeplearning. arXivpreprintarXiv:1912.01198,2019.
[10] RonglongFangandYueshengXu. Addressingspectralbiasofdeepneuralnetworksbymulti-gradedeep
learning. AdvancesinNeuralInformationProcessingSystems,37:114122–114146,2024.
[11] Xihao Piao, Zheng Chen, Taichi Murayama, Yasuko Matsubara, and Yasushi Sakurai. Fredformer:
Frequencydebiasedtransformerfortimeseriesforecasting. InProceedingsofthe30thACMSIGKDD
conferenceonknowledgediscoveryanddatamining,pages2400–2410,2024.
[12] RameshNeelamani,HyeokhoChoi,andRichardBaraniuk. Forward:Fourier-waveletregularizeddeconvo-
lutionforill-conditionedsystems. IEEETransactionsonsignalprocessing,52(2):418–433,2004.
[13] DavidSalinas,ValentinFlunkert,JanGasthaus,andTimJanuschowski. Deepar:Probabilisticforecasting
withautoregressiverecurrentnetworks. Internationaljournalofforecasting,36(3):1181–1191,2020.
[14] LidaLi,KunWang,ShuaiLi,XiangchuFeng,andLeiZhang. Lst-net:Learningaconvolutionalneural
networkwithalearnablesparsetransform. InEuropeanconferenceoncomputervision,pages562–579.
Springer,2020.
[15] YaoQin,DongjinSong,HaifengChen,WeiCheng,GuofeiJiang,andGarrisonCottrell. Adual-stage
attention-basedrecurrentneuralnetworkfortimeseriesprediction. arXivpreprintarXiv:1704.02971,
2017.
[16] ShaojieBai,JZicoKolter,andVladlenKoltun. Anempiricalevaluationofgenericconvolutionaland
recurrentnetworksforsequencemodeling. arXivpreprintarXiv:1803.01271,2018.
[17] MinhaoLiu,AilingZeng,MuxiChen,ZhijianXu,QiuxiaLai,LingnaMa,andQiangXu. Scinet:Time
seriesmodelingandforecastingwithsampleconvolutionandinteraction. AdvancesinNeuralInformation
ProcessingSystems,35:5816–5828,2022.
[18] AshishVaswani,NoamShazeer,NikiParmar,JakobUszkoreit,LlionJones,AidanNGomez,Łukasz
Kaiser,andIlliaPolosukhin. Attentionisallyouneed. Advancesinneuralinformationprocessingsystems,
30,2017.
[19] HaoyiZhou, ShanghangZhang, JieqiPeng, ShuaiZhang, JianxinLi, HuiXiong, andWancaiZhang.
Informer:Beyondefficienttransformerforlongsequencetime-seriesforecasting. InProceedingsofthe
AAAIconferenceonartificialintelligence,volume35,pages11106–11115,2021.
[20] YuqiNie,NamHNguyen,PhanwadeeSinthong,andJayantKalagnanam. Atimeseriesisworth64words:
Long-termforecastingwithtransformers. arXivpreprintarXiv:2211.14730,2022.
[21] AilingZeng,MuxiChen,LeiZhang,andQiangXu. Aretransformerseffectivefortimeseriesforecasting?
InProceedingsoftheAAAIconferenceonartificialintelligence,volume37,pages11121–11128,2023.
10

---

# Page 11

[22] YuxuanWang,HaixuWu,JiaxiangDong,GuoQin,HaoranZhang,YongLiu,YunzhongQiu,Jianmin
Wang,andMingshengLong.Timexer:Empoweringtransformersfortimeseriesforecastingwithexogenous
variables. arXivpreprintarXiv:2402.19072,2024.
[23] ShiyuWang,HaixuWu,XiaomingShi,TenggeHu,HuakunLuo,LintaoMa,JamesYZhang,andJunZhou.
Timemixer:Decomposablemultiscalemixingfortimeseriesforecasting.arXivpreprintarXiv:2405.14616,
2024.
[24] MdMahmuddunNabiMurad,MehmetAktukmak,andYasinYilmaz. Wpmixer:Efficientmulti-resolution
mixing for long-term time series forecasting. In Proceedings of the AAAI Conference on Artificial
Intelligence,volume39,pages19581–19588,2025.
[25] MingJin,ShiyuWang,LintaoMa,ZhixuanChu,JamesYZhang,XiaomingShi,Pin-YuChen,Yuxuan
Liang,Yuan-FangLi,ShiruiPan,etal.Time-llm:Timeseriesforecastingbyreprogramminglargelanguage
models. arXivpreprintarXiv:2310.01728,2023.
[26] YongLiu,GuoQin,XiangdongHuang,JianminWang,andMingshengLong. Autotimes:Autoregressive
timeseriesforecastersvialargelanguagemodels. AdvancesinNeuralInformationProcessingSystems,
37:122154–122184,2024.
[27] YuhanWu,XiyuMeng,HuajinHu,JunruZhang,YaboDong,andDongmingLu. Affirm: Interactive
mambawithadaptivefourierfiltersforlong-termtimeseriesforecasting. InProceedingsoftheAAAI
ConferenceonArtificialIntelligence,volume39,pages21599–21607,2025.
[28] Matthew Tancik, Pratul Srinivasan, Ben Mildenhall, Sara Fridovich-Keil, Nithin Raghavan, Utkarsh
Singhal, RaviRamamoorthi, JonathanBarron, andRenNg. Fourierfeaturesletnetworkslearnhigh
frequencyfunctionsinlowdimensionaldomains. Advancesinneuralinformationprocessingsystems,
33:7537–7547,2020.
[29] EdwinTJaynes. Informationtheoryandstatisticalmechanics. Physicalreview,106(4):620,1957.
[30] YanLi,XinjiangLu,YaqingWang,andDejingDou. Generativetimeseriesforecastingwithdiffusion,
denoise,anddisentanglement. AdvancesinNeuralInformationProcessingSystems,35:23009–23022,
2022.
[31] TianZhou,ZiqingMa,QingsongWen,LiangSun,TaoYao,WotaoYin,RongJin,etal. Film:Frequency
improvedlegendrememorymodelforlong-termtimeseriesforecasting. Advancesinneuralinformation
processingsystems,35:12677–12690,2022.
[32] GeorgeEPBoxandGwilymMJenkins. Somerecentadvancesinforecastingandcontrol. Journalofthe
RoyalStatisticalSociety.SeriesC(AppliedStatistics),17(2):91–109,1968.
[33] SuzanneAigrainandDanielForeman-Mackey. Gaussianprocessregressionforastronomicaltimeseries.
AnnualReviewofAstronomyandAstrophysics,61(1):329–371,2023.
[34] XinyuYuanandYanQiao. Diffusion-ts:Interpretablediffusionforgeneraltimeseriesgeneration. arXiv
preprintarXiv:2403.01742,2024.
[35] ThomasBondoPedersen,SusiLehtola,IgnacioFdez.Galván,andRolandLindh. Theversatilityofthe
choleskydecompositioninelectronicstructuretheory. Wileyinterdisciplinaryreviews: Computational
molecularscience,14(1):e1692,2024.
[36] LSCederbaum,JSchirmer,andH-DMeyer. Blockdiagonalisationofhermitianmatrices. Journalof
physicsA:MathematicalandGeneral,22(13):2427,1989.
[37] AnthonyWKnappandAnthonyWilliamKnapp.Liegroupsbeyondanintroduction,volume140.Springer,
1996.
[38] GeraldBFolland. Fourieranalysisanditsapplications,volume4. AmericanMathematicalSoc.,2009.
[39] VictorChernozhukov,DenisChetverikov,MertDemirer,EstherDuflo,ChristianHansen,WhitneyNewey,
andJamesRobins. Double/debiasedmachinelearningfortreatmentandstructuralparameters,2018.
11

---

# Page 12

Table3: Informationofeachdataset. Channelrepresentsthevariatenumberofeachdataset. Length
isthetotalnumberoftimesteps. Samplingratedenotesthesamplingintervaloftimesteps. Domain
referstotheapplicationareatowhichthedatasetbelongs.
Dataset Channel Length Samplingrate Domain
ETTh1&ETTh2 7 17420 1Hour Energy
ETTm1&ETTm2 7 69680 15Minutes Energy
Weather 21 52696 10Minutes Climate
Exchange 8 7588 1Day Finance
ILI 7 966 1Week Healthcare
Electricity 321 26304 1Hour Energy
Traffic 862 17544 1Hour Transportation
A Appendix
A.1 Datasets
Thedatasetsusedinourexperimentsspanawidevarietyofreal-worldtimeseriesapplications.TheETTdataset
collectsindustrialtemperatureandtorquedata,dividedintofoursubsets(ETTh1,ETTh2,ETTm1,ETTm2),
eachreflectingdifferenttemporalgranularitiesandperiodsforevaluatinglong-sequenceforecastingmodels.
TheWeatherdatasetconsistsofmeteorologicalvariablessuchastemperature,humidity,andwindspeedacross
multiplegeographiclocations,andiswidelyusedinenvironmentalforecasting. TheExchangeRatedataset
containsforeignexchangeratesofeightmajorcurrenciesagainsttheUSdollarandiscommonlyusedfor
financialtimeseriesforecasting.TheILIdatasetcompriseshistoricalweeklyrecordsofflu-relatedcasecounts
releasedbytheUnitedStatesCentersforDiseaseControlandPrevention,suitableforepidemiologicalmodeling.
TheElectricitydatasetreflectshousehold-levelelectricityconsumptionacrosshundredsofclientsandsupports
studiesonenergydemandforecasting.TheTrafficdatasetcapturesvehicleroadoccupancyacrossCalifornia’s
highwaysystem,usefulforurbanmobilityprediction. Moredetailedinformationaboutthesequencelength,
numberofchannels,andsamplingrateforeachdatasetisprovidedinTable3.
A.2 ExplainingFrequencyBiasfromDataPerspective
Theinherentfrequencypreferenceofneuralnetworksisawell-recognizedphenomenon.However,thecharacter-
isticsofthedataitselfcanalsoinfluencethenetwork’sabilitytolearnacrossdifferentfrequencycomponents.In
thetimedomain,strongcorrelationsbetweentimepoints(e.g.,highvaluesoftheautocorrelationfunction)imply
thattheerrorsofadjacentpointsinthelosscomputationarehighlycorrelated. This,inturn,biasesgradient
descentupdatestowardcapturinglocalvariationpatterns.AsillustratedinFigure2(b),thetimeseriesexhibits
stronglocaloscillations,indicatingthathigh-frequencycomponentsdominatewithintheseregions.Thisprovides
anadditionalexplanationforwhythemodeltendstoprioritizelearninghigh-frequencyinformation. Inthe
frequencydomain,afterapplyingtheFouriertransform,differentfrequencycomponentsbecomeapproximately
orthogonal(i.e.,weaklycorrelated). Thisimpliesthattheerrorassociatedwitheachfrequencycomponent
contributesindependentlytothelossfunction.Consequently,gradientdescentupdatesthenetworkparameters
correspondingtoeachfrequencyinanindependentmanner,preventinganysinglefrequencyfromdominating
theoptimizationprocess.Tovalidatethis,weconductedexperimentsontheETTh1dataset.AsshowninFigure
4(a),thedataexhibitsstrongcorrelationsamongadjacentpointsinthetimedomain. Incontrast,(b)and(c)
clearlydemonstratethatsuchcorrelationsbecomemuchweakerinthefrequencydomain.
Specifically,weemployaDoubleMachineLearning(DML)[39]approachtoeliminatetheinfluenceofcon-
foundersoncorrelationestimation. ThespecificcomputationprocedureisasAlgorithm1,whichestimates
thecausalcorrelationfromtimepointttot′withinatimeseriesusingresidualregressionbasedontheDML
framework.
Lettheinputtimeseriesbe{x ,x ,...,x },whereN isthetotalsequencelength.Ittakesfourparameters:a
1 2 N
windowsizew(issetto2inthiswork)todefinethesetofconfounders(assumingthatconfoundingfactors
existinthesequencenearthesourcetimesteps),thesourceandtargettimestepstandt′suchthatt<t′,and
themaximumlengthusedforcomputingsequencecorrelationT (issetto96inthiswork).Eachtimepointi
vis
(fromwtoN −T )definesalocalcontextforcausalevaluation.Thevalueatindexj =i+tservesasthe
vis
sourcetimestepssetT,andthevalueatindexk=i+t′servesasthetargettimestepssetO.Foreachsuch
pair,weconstructasetofconfoundersCbycollectingthe2wneighborsaroundx ,excludingx itself(and
i i
optionallyexcludingx ifitappearsinthecontextwindow).
j
Aftercollectingthesamplesoftreatment,outcome,andconfounders,wetraintwoseparateregressionmodels:
• Model topredictthesourceT fromtheconfoundersC,andcomputetheresidualst˜.
t
• Model topredictthetargetOfromtheconfoundersC,andcomputetheresidualso˜.
o
12

---

# Page 13

Figure4: ThecorrelationmatricesontheETTh1dataset. (a)Correlationmatrixinthetimedomain.
(b)CorrelationmatrixoftherealpartafterFourierTransform. (c)Correlationmatrixoftheimaginary
part.
Theseresidualsrepresentthepartsofthesourceandtargetthatarenotexplainedbytheconfounders. The
finalcausaleffectestimatee t→t′ iscomputedastheabsoluteva
(cid:12)
lueofthe
(cid:12)
regressioncoefficientbetweent˜and
o˜,whichisequivalenttothenormalizedcovariance: e t→t′ = (cid:12) (cid:12) C V o a v r ( ( t˜ t˜ ,o ) ˜)(cid:12) (cid:12) ,whereCovdenotesthecovariance
calculation,andVardenotesthevariancecalculation.Thisvaluecapturestheresidualdependencebetweenthe
sourceandthetargetafteradjustingforconfoundingvariables,andthusservesasaproxyforcausalcorrelation.
Likewise,applyingthisalgorithminthefrequencydomainonlyrequiresapreliminaryfixed-lengthFourier
Transformontheentiretimeseries.
Algorithm1CausalCorrelationofTimeSeries
Require: Timeseries{x ,x ,...,x },windowsizew,offsetst<t′,visiblerangeT
1 2 N vis
Ensure: Estimatedcausaleffecte
t→t′
1: PrecomputeconfoundersC i ←{x i−w ,...,x i−1 ,x i+1 ,...,x i+w }
2: InitializesamplelistT ←[],O ←[],C ←[]
3: foreachi=wtoN −T do
vis
4: j ←i+t, k ←i+t′
5: ifk ≥N then
6: continue
7: endif
8: T ←x j ,O ←x k ,C ←C i
9: endfor
10: Trainingadoublemachinelearningmodel.
11: TrainModel t (C,T),getresidualst˜=Model t (C)−T
12: TrainModel o (C,O),getresidualso˜=Model o (C)−O
(cid:12) (cid:12)
13: Computee t→t′ =(cid:12) (cid:12) C V ov ar ( ( t˜ t˜ , ) o˜)(cid:12) (cid:12)
14: return e t→t′
A.3 FullResults
ThefullexperimentalresultsarereportedinTables4and5.Withoutintroducinganyarchitecturalmodifications,
simplyreplacingtheoriginaltimedomainlosswithOLMAconsistentlyimprovestheforecastingperformance
acrossmodels.Specifically,torespecttheoriginalsupervisionschemesofthevariousmethods,allmodelsexcept
WPMixeremployedtheMSEloss,whileWPMixerusedtheSmoothL1loss[24]. Forthehyperparameters
(α,β,γ)ofOLMA,weassignequalweights(0.34,0.33,0.33)forallmodels. Specifically,fortheECLand
Trafficdatasets,tomitigatetheimpactofentropyincreasecausedbychannel-wiseFouriertransform,wesetthe
hyperparametersto(0.1,0.45,0.45).
A.4 OLMAorOLMA+TimeDomainSupervision?
Aninterestingquestionarises,thatis,canincorporatingtimedomainsupervisionintoOLMAleadtobetter
forecastingperformance?Inotherwords,doesthepurefrequencydomainsupervisionofOLMAalreadycapture
13

---

# Page 14

Table4: FullresultsofforecastingerrorsofOLMAonmainstreammodelbaselines(TimeCMA,
S-Mamba,iTransformerandTimesNet)whichsupervisedbytimedomainlosses(TDL)ondifferent
datasets. Lowervaluesindicatebetterperformance. Thebestresultsarehighlightedinbold.
TimeCMA S-Mamba iTransformer TimesNet
Dataset Length TDL OLMA TDL OLMA TDL OLMA TDL OLMA
MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
96 0.392 0.413 0.389 0.406 0.386 0.405 0.368 0.387 0.386 0.405 0.382 0.396 0.389 0.412 0.382 0.403
192 0.432 0.435 0.431 0.428 0.443 0.437 0.422 0.417 0.441 0.436 0.435 0.427 0.439 0.442 0.432 0.435
ETTh1 336 0.467 0.452 0.464 0.445 0.489 0.468 0.466 0.438 0.487 0.458 0.483 0.454 0.494 0.471 0.480 0.458
720 0.461 0.465 0.449 0.456 0.502 0.489 0.470 0.463 0.503 0.491 0.476 0.472 0.516 0.494 0.485 0.476
Avg 0.438 0.441 0.433 0.434 0.455 0.450 0.432 0.426 0.454 0.448 0.444 0.437 0.460 0.455 0.445 0.443
96 0.326 0.364 0.315 0.357 0.296 0.348 0.281 0.333 0.297 0.349 0.294 0.343 0.337 0.370 0.312 0.350
192 0.419 0.420 0.382 0.398 0.376 0.396 0.357 0.382 0.380 0.400 0.373 0.391 0.405 0.415 0.392 0.406
ETTh2 336 0.443 0.443 0.432 0.435 0.424 0.431 0.403 0.418 0.428 0.432 0.417 0.426 0.453 0.450 0.438 0.445
720 0.441 0.453 0.423 0.442 0.426 0.444 0.408 0.432 0.427 0.445 0.420 0.439 0.434 0.448 0.460 0.464
Avg 0.407 0.420 0.388 0.408 0.381 0.405 0.362 0.391 0.383 0.407 0.376 0.400 0.407 0.421 0.401 0.416
96 0.324 0.365 0.313 0.352 0.333 0.368 0.311 0.348 0.334 0.368 0.325 0.359 0.334 0.375 0.326 0.360
192 0.374 0.394 0.362 0.377 0.376 0.390 0.357 0.372 0.377 0.391 0.373 0.381 0.408 0.414 0.390 0.397
ETTm1 336 0.407 0.415 0.396 0.399 0.408 0.413 0.393 0.395 0.426 0.420 0.411 0.407 0.415 0.422 0.402 0.410
720 0.469 0.448 0.462 0.437 0.475 0.448 0.455 0.430 0.491 0.459 0.479 0.445 0.485 0.461 0.454 0.439
Avg 0.393 0.406 0.383 0.391 0.398 0.405 0.379 0.386 0.407 0.410 0.397 0.398 0.411 0.418 0.393 0.402
96 0.182 0.263 0.175 0.255 0.179 0.263 0.171 0.250 0.180 0.264 0.177 0.256 0.189 0.266 0.178 0.255
192 0.257 0.316 0.245 0.298 0.250 0.309 0.238 0.295 0.250 0.309 0.243 0.300 0.252 0.307 0.246 0.301
ETTm2 336 0.310 0.348 0.307 0.338 0.312 0.349 0.300 0.336 0.311 0.348 0.306 0.340 0.323 0.350 0.306 0.337
720 0.412 0.404 0.414 0.400 0.411 0.406 0.402 0.396 0.412 0.407 0.407 0.399 0.419 0.405 0.411 0.398
Avg 0.290 0.333 0.285 0.323 0.288 0.332 0.278 0.319 0.288 0.332 0.283 0.324 0.296 0.332 0.285 0.323
96 0.170 0.217 0.166 0.209 0.165 0.210 0.152 0.193 0.174 0.214 0.168 0.205 0.169 0.219 0.165 0.211
192 0.216 0.257 0.211 0.252 0.214 0.252 0.204 0.241 0.221 0.254 0.219 0.252 0.225 0.265 0.222 0.260
Weather 336 0.268 0.299 0.267 0.294 0.274 0.297 0.264 0.287 0.278 0.296 0.276 0.294 0.281 0.304 0.277 0.297
720 0.340 0.351 0.337 0.346 0.350 0.345 0.344 0.339 0.358 0.347 0.356 0.348 0.359 0.354 0.362 0.355
Avg 0.248 0.281 0.245 0.275 0.251 0.276 0.241 0.265 0.258 0.278 0.255 0.275 0.259 0.286 0.257 0.281
96 0.114 0.242 0.104 0.231 0.086 0.207 0.083 0.202 0.086 0.206 0.085 0.205 0.105 0.235 0.109 0.240
192 0.209 0.331 0.200 0.323 0.182 0.304 0.179 0.300 0.177 0.299 0.177 0.300 0.223 0.344 0.215 0.333
Exchange 336 0.379 0.452 0.370 0.446 0.332 0.418 0.317 0.408 0.331 0.417 0.330 0.416 0.363 0.439 0.366 0.439
720 1.080 0.802 0.992 0.764 0.867 0.703 0.821 0.681 0.847 0.691 0.818 0.681 0.940 0.739 0.921 0.725
Avg 0.446 0.457 0.416 0.441 0.367 0.408 0.350 0.398 0.360 0.403 0.353 0.401 0.408 0.439 0.403 0.434
24 1.870 0.913 1.962 0.909 2.103 0.972 2.007 0.932 2.438 1.076 2.450 1.082 1.806 0.893 1.715 0.857
36 1.825 0.852 1.827 0.857 1.832 0.921 1.703 0.759 2.455 1.086 2.410 1.071 2.679 0.986 2.402 0.924
ILI 48 1.824 0.834 1.764 0.827 2.224 0.998 1.877 0.725 2.580 1.118 2.513 1.095 2.584 0.938 2.224 0.843
60 1.938 0.892 1.880 0.882 1.950 1.373 1.636 0.994 2.734 1.155 2.689 1.140 1.981 0.894 1.840 0.851
Avg 1.864 0.873 1.858 0.869 2.027 1.066 1.806 0.853 2.552 1.109 2.516 1.097 2.263 0.928 2.045 0.869
96 0.144 0.244 0.149 0.248 0.139 0.235 0.138 0.233 0.148 0.240 0.145 0.234 0.168 0.272 0.165 0.266
192 0.161 0.261 0.174 0.275 0.159 0.255 0.158 0.251 0.162 0.253 0.159 0.247 0.185 0.288 0.183 0.283
ECL 336 0.227 0.328 0.197 0.293 0.176 0.272 0.173 0.270 0.178 0.269 0.173 0.262 0.204 0.306 0.193 0.293
720 0.320 0.397 0.280 0.370 0.204 0.298 0.199 0.293 0.225 0.317 0.200 0.287 0.219 0.318 0.210 0.309
Avg 0.213 0.307 0.200 0.296 0.170 0.265 0.167 0.262 0.178 0.270 0.169 0.258 0.194 0.296 0.188 0.288
96 0.717 0.379 0.705 0.373 0.382 0.261 0.381 0.250 0.395 0.268 0.388 0.254 0.589 0.315 0.573 0.306
192 0.708 0.377 0.682 0.364 0.396 0.267 0.389 0.255 0.417 0.276 0.410 0.264 0.618 0.324 0.623 0.320
Traffic 336 0.655 0.351 0.668 0.351 0.417 0.276 0.417 0.266 0.433 0.283 0.426 0.271 0.632 0.336 0.626 0.323
720 0.709 0.374 0.730 0.392 0.460 0.300 0.461 0.287 0.467 0.302 0.461 0.289 0.659 0.349 0.643 0.328
Avg 0.697 0.370 0.696 0.370 0.414 0.276 0.412 0.265 0.428 0.282 0.421 0.270 0.625 0.331 0.616 0.319
14

---

# Page 15

Table5: FullresultsofforecastingerrorsofOLMAonmainstreammodelbaselines(TimeMixer,
TimeXer, DLinear and WPMixer) which supervised by time domain losses (TDL) on different
datasets. Lowervaluesindicatebetterperformance. Thebestresultsarehighlightedinbold.
TimeMixer TimeXer DLinear WPMixer
Dataset Length TDL OLMA TDL OLMA TDL OLMA TDL OLMA
MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
96 0.375 0.400 0.370 0.388 0.382 0.403 0.378 0.391 0.375 0.399 0.365 0.386 0.347 0.383 0.345 0.379
192 0.429 0.421 0.417 0.419 0.429 0.435 0.430 0.423 0.405 0.416 0.402 0.408 0.381 0.408 0.378 0.404
ETTh1 336 0.484 0.458 0.472 0.443 0.468 0.448 0.470 0.442 0.439 0.443 0.430 0.428 0.382 0.412 0.379 0.408
720 0.498 0.482 0.481 0.466 0.469 0.461 0.465 0.459 0.472 0.490 0.454 0.474 0.405 0.432 0.401 0.431
Avg 0.447 0.440 0.435 0.429 0.437 0.437 0.436 0.429 0.423 0.437 0.413 0.424 0.379 0.409 0.376 0.406
96 0.289 0.341 0.286 0.335 0.286 0.338 0.279 0.330 0.289 0.353 0.284 0.346 0.253 0.328 0.253 0.326
192 0.372 0.392 0.365 0.386 0.363 0.389 0.365 0.384 0.383 0.418 0.370 0.402 0.303 0.364 0.304 0.363
ETTh2 336 0.417 0.431 0.407 0.420 0.414 0.423 0.414 0.419 0.448 0.465 0.448 0.461 0.305 0.371 0.305 0.370
720 0.419 0.440 0.414 0.434 0.408 0.432 0.395 0.422 0.605 0.551 0.556 0.525 0.373 0.417 0.371 0.413
Avg 0.374 0.401 0.368 0.394 0.368 0.396 0.363 0.389 0.431 0.447 0.415 0.434 0.309 0.370 0.308 0.368
96 0.320 0.357 0.311 0.343 0.318 0.356 0.311 0.345 0.299 0.343 0.298 0.338 0.275 0.333 0.275 0.329
192 0.361 0.381 0.357 0.371 0.362 0.383 0.357 0.371 0.335 0.365 0.334 0.359 0.319 0.362 0.311 0.352
ETTm1 336 0.390 0.404 0.388 0.394 0.395 0.407 0.389 0.394 0.369 0.386 0.369 0.379 0.347 0.384 0.346 0.378
720 0.454 0.441 0.454 0.430 0.452 0.441 0.451 0.431 0.425 0.421 0.423 0.413 0.403 0.414 0.399 0.413
Avg 0.381 0.396 0.378 0.385 0.382 0.397 0.377 0.385 0.357 0.379 0.356 0.372 0.336 0.373 0.333 0.368
96 0.175 0.258 0.171 0.251 0.171 0.256 0.168 0.249 0.167 0.260 0.164 0.253 0.159 0.246 0.157 0.243
192 0.237 0.299 0.235 0.295 0.237 0.299 0.232 0.291 0.224 0.303 0.224 0.289 0.214 0.286 0.214 0.281
ETTm2 336 0.298 0.340 0.294 0.335 0.296 0.338 0.290 0.328 0.281 0.342 0.282 0.339 0.266 0.322 0.267 0.319
720 0.391 0.396 0.390 0.396 0.392 0.394 0.393 0.391 0.397 0.421 0.383 0.408 0.344 0.374 0.344 0.370
Avg 0.275 0.323 0.273 0.319 0.274 0.322 0.271 0.315 0.267 0.332 0.263 0.322 0.246 0.307 0.246 0.303
96 0.163 0.209 0.158 0.198 0.157 0.205 0.155 0.198 0.176 0.237 0.172 0.221 0.141 0.188 0.140 0.186
192 0.208 0.250 0.206 0.243 0.204 0.247 0.202 0.242 0.220 0.282 0.213 0.260 0.185 0.229 0.185 0.230
Weather 336 0.251 0.287 0.261 0.285 0.261 0.290 0.259 0.285 0.265 0.319 0.257 0.298 0.236 0.271 0.235 0.271
720 0.339 0.341 0.341 0.338 0.340 0.341 0.338 0.337 0.323 0.362 0.320 0.351 0.307 0.321 0.306 0.322
Avg 0.240 0.272 0.242 0.266 0.241 0.271 0.239 0.266 0.246 0.300 0.241 0.283 0.217 0.252 0.217 0.252
96 0.083 0.201 0.082 0.200 0.087 0.206 0.085 0.205 0.081 0.203 0.080 0.202 0.094 0.216 0.092 0.212
192 0.177 0.299 0.177 0.299 0.176 0.298 0.175 0.297 0.157 0.293 0.156 0.288 0.184 0.306 0.183 0.305
Exchange 336 0.329 0.413 0.320 0.409 0.346 0.425 0.338 0.421 0.333 0.441 0.365 0.452 0.339 0.421 0.340 0.421
720 0.817 0.678 0.787 0.663 0.879 0.707 0.799 0.670 0.897 0.725 0.657 0.634 0.831 0.682 0.753 0.644
Avg 0.352 0.398 0.342 0.393 0.372 0.409 0.349 0.398 0.367 0.416 0.315 0.394 0.362 0.406 0.342 0.396
24 2.245 0.985 2.245 0.953 2.203 0.958 2.205 0.958 2.215 1.081 2.119 0.964 1.349 0.731 1.432 0.745
36 1.962 0.930 1.610 0.785 2.099 0.928 2.088 0.924 1.963 0.963 2.051 0.966 1.462 0.764 1.599 0.791
ILI 48 2.393 1.086 1.563 0.785 2.081 0.977 2.064 0.928 2.130 1.024 1.992 0.961 1.813 0.882 1.525 0.788
60 1.753 0.908 1.539 0.790 2.190 0.980 2.140 0.966 2.368 1.096 2.035 0.989 1.712 0.889 1.586 0.809
Avg 2.088 0.977 1.739 0.828 2.143 0.961 2.124 0.944 2.169 1.041 2.049 0.970 1.584 0.817 1.536 0.783
96 0.153 0.247 0.155 0.246 0.140 0.242 0.140 0.239 0.140 0.237 0.140 0.236 0.128 0.222 0.128 0.221
192 0.166 0.256 0.167 0.257 0.157 0.256 0.158 0.255 0.153 0.249 0.154 0.249 0.145 0.237 0.145 0.237
ECL 336 0.185 0.277 0.184 0.273 0.176 0.275 0.176 0.272 0.169 0.267 0.169 0.267 0.161 0.256 0.160 0.253
720 0.225 0.310 0.224 0.312 0.211 0.306 0.215 0.306 0.203 0.301 0.205 0.300 0.196 0.287 0.197 0.287
Avg 0.182 0.273 0.183 0.272 0.171 0.270 0.172 0.268 0.166 0.264 0.167 0.263 0.158 0.251 0.158 0.250
96 0.482 0.315 0.462 0.301 0.428 0.271 0.429 0.258 0.410 0.282 0.410 0.282 0.354 0.246 0.354 0.244
192 0.486 0.315 0.476 0.299 0.448 0.282 0.456 0.268 0.423 0.287 0.422 0.286 0.371 0.253 0.367 0.251
Traffic 336 0.503 0.332 0.499 0.306 0.473 0.289 0.472 0.282 0.436 0.296 0.435 0.293 0.387 0.267 0.383 0.265
720 0.524 0.326 0.545 0.326 0.516 0.307 0.513 0.300 0.466 0.315 0.464 0.311 0.431 0.289 0.427 0.285
Avg 0.499 0.322 0.496 0.308 0.466 0.287 0.468 0.277 0.434 0.295 0.433 0.293 0.386 0.264 0.383 0.261
15

---

# Page 16

Table6: ComparisonofforecastingerrorsbetweenOLMAandthecombinedOLMA+MSEloss
acrossdifferentdatasets. Lowervaluesindicatebetterperformance. Thebestresultsarehighlighted
inbold.
96 192 336 720
Dataset Loss Average Improvement
MSE MAE MSE MAE MSE MAE MSE MAE
OLMA+MSE 0.367 0.388 0.402 0.409 0.429 0.429 0.455 0.475 0.419
ETTh1 0.3%
OLMA 0.365 0.386 0.402 0.408 0.429 0.428 0.453 0.474 0.418
OLMA+MSE 0.297 0.338 0.332 0.360 0.380 0.370 0.420 0.413 0.364
ETTm1 0.2%
OLMA 0.297 0.338 0.331 0.359 0.379 0.369 0.419 0.412 0.363
OLMA+MSE 0.171 0.223 0.212 0.262 0.258 0.303 0.322 0.357 0.264
Weather 1.4%
OLMA 0.171 0.217 0.211 0.257 0.256 0.296 0.320 0.351 0.260
alltheessentialinformationinthetimeseries,orwouldaddingtimedomainsupervisionintroduceredundant
information?Toexplorethis,weconductexperimentsusingthebasicDLinearmodel.Table6comparesthe
forecastingerrorsofOLMAaloneandOLMAcombinedwithtimedomainsupervision.ItisevidentthatOLMA
aloneachievesbetterperformanceinmostcases. Thissuggeststhattemporaldomainsupervisiondoesnot
provideadditionalusefulinformationontopofOLMAandmayevenintroducenoisethatharmsperformancein
certainscenarios.
A.5 ImpactofChannelandTemporalLossesonForecastingPerformance
TheimpactofthebalancingchannelandtemporallossesofOLMAonforecastingerrorisfurtherevaluatedon
theETTh1,ETTm1andWeatherdatasetswithforecastinglengthsof{96,192,336,720}.Figure5illustrates
theforecastingerrorsofWPMixerindifferentlossweightconfigurations.Theresultsshowthattheperformance
ofOLMAremainsstableacrossawiderangeoflossweightratiosbetweenchannelandtemporaldimensions.
ThisdemonstratesthatOLMAisaparameter-insensitivelossfunction,whichcanbeseamlesslyappliedtoany
supervisedmethodwithouttheneedforcomplexhyperparametertuning.
Figure5:ImpactoftheratiobetweenchannelandtemporaldimensionlossesinOLMAonforecasting
erroronETTh1,ETTm1andWeatherdatasetsundervariousforecastinglengths{96,192,336,720}
byWPMixer.
16