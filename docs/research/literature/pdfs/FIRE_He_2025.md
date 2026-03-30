# Page 1

A Unified Frequency Domain Decomposition Framework for
Interpretable and Robust Time Series Forecasting
ChengHe XijieLiang ZengrongZheng
cheng.he@mail.ustc.edu.cn lxjie@blackwingasset.com lxjie@blackwingasset.com
UniversityofScienceandTechnology ShanghaiBlackWingAsset Di-Matrix(Shanghai)Information
ofChina ManagementCo.,Ltd. TechnologyCo.,Ltd.
Hefei,China Shanghai,China Shanghai,China
PatrickP.C.Lee XuHuang ZhaoyiLi
pclee@cse.cuhk.edu.hk xuhuangcs@mail.ustc.edu.cn lizhaoyi777@mail.ustc.edu.cn
TheChineseUniversityofHongKong UniversityofScienceandTechnology UniversityofScienceandTechnology
HongKong,China ofChina ofChina
Hefei,China Hefei,China
HongXie DefuLian EnhongChen
xiehong2018@foxmail.com liandefu@ustc.edu.cn cheneh@ustc.edu.cn
UniversityofScienceandTechnology UniversityofScienceandTechnology UniversityofScienceandTechnology
ofChina ofChina ofChina
Hefei,China Hefei,China Hefei,China
Abstract oftenfailtocapturecomplexunderlyingpatternswhenanalyzed
Currentapproachesfortimeseriesforecasting,whetherinthetime solelyinthetemporaldomain.
or frequency domain, predominantly use deep learning models Toeffectivelycapturethecomplexpatternsoftimeseriesdata,
basedonlinearlayersortransformers.Theyoftenencodetime recentresearchhasexploredfrequency-domainrepresentations
seriesdatainablack-boxmannerandrelyontrial-and-erroropti- fortimeseriesdatausingFastFourierTransform(FFT).Notable
mizationsolelybasedonforecastingperformance,leadingtolimited approaches such as FredFormer [27], FreTS [41], and FITS [38]
interpretabilityandtheoreticalunderstanding.Furthermore,thedy- leverage frequency-domain techniques, including channel-wise
namicsindatadistributionovertimeandfrequencydomainspose attention,frequency-temporaldependencymodeling,andcomplex-
acriticalchallengetoaccurateforecasting.WeproposeFIRE,a valued interpolation, while WPMixer [24] employs wavelet de-
unifiedfrequencydomaindecompositionframeworkthatprovides compositioncombinedwithmultiplayerperceptrons(MLPs)for
amathematicalabstractionfordiversetypesoftimeseries,soas long-termforecasting.Hybridarchitectures,suchasCDX-Net[18],
toachieveinterpretableandrobusttimeseriesforecasting.FIRE FEDformer[45],andTimeMixer++[32],integratetemporaland
introducesseveralkeyinnovations:(i)independentmodelingof frequency-domainfeaturestoenhancetherobustnessandaccu-
amplitudeandphasecomponents,(ii)adaptivelearningofweights racyoftimeseriesrepresentations.Despitetheseadvances,most
offrequencybasiscomponents,(iii)atargetedlossfunction,and(iv) existingmodelsencodetimeseriesrepresentationsempiricallyina
anoveltrainingparadigmforsparsedata.Extensiveexperiments black-boxmanner,optimizedthroughtrial-and-errorbasedonfore-
demonstratethatFIREconsistentlyoutperformsstate-of-the-art castingoutcomes.Thislimitsbothinterpretabilityandtheoretical
modelsonlong-termforecastingbenchmarks,achievingsuperior insightsintotheunderlyingdatastructure.
predictiveperformanceandsignificantlyenhancinginterpretability Timeseriesforecastingisfurthercomplicatedbyconceptdrift
oftimeseriesrepresentations. [4,10,12,29],wherethestatisticalpropertiesandpatternsoftime
seriesdatashiftovertime.Suchdynamicsalsoimplybasisevolu-
tioninthefrequencydomainwhentimeseriesdataisdecomposed
1 Introduction into frequencycomponents viaFFT [13, 14, 23, 44], wherenew
Timeseriesforecastingisacriticalyetchallengingtaskinvari- frequencybasesappearandexistingonesdisappear.Basisevolu-
ousdomainssuchaswebmining,predictivemaintenanceofIoT tioncomplicatesfrequency-domainanalysis,asmodelsbuilton
devices,trafficprediction,weatherforecasting,electricityloadman- staticbasisassumptionscannotreadilymaintainstableandaccu-
agement,andfinancialanalysis.Recently,theattentionmechanism raterepresentations.Consequently,modelstrainedonhistorical
[31]hasprovenhighlyeffective,establishingtransformer-basedar- databecomelesseffectiveforfuturepredictionsunderconceptdrift
chitecturesasthedominantapproachfortimeseriesrepresentation andbasisevolution.However,currentstate-of-the-artforecasting
learninginthetemporaldomain[7,19,28,33,36,37,40,43].These modelseitheroverlookthesephenomenaoraddressthemonly
modelsoutperformtraditionalrecurrentneuralnetworks(RNNs) implicitly,leavingavoidininterpretableandrobustsolutions.
andconvolutionalneuralnetworks(CNNs)[1,2,5,8,9,16,39],par- WeproposeFIRE,anovelunifiedfrequencydomaindecomposi-
ticularlyeffectiveincapturinglong-rangedependencies.However, tionframeworkforinterpretableandrobusttimeseriesforecasting.
timeseriesdata,composedoftemporallyorderedscalarsequences,
1
5202
tcO
11
]GL.sc[
1v54101.0152:viXra

---

# Page 2

Conference’17,July2017,Washington,DC,USA ChengHe,XijieLiang,ZengrongZheng,PatrickP.C.Lee,XuHuang,ZhaoyiLi,HongXie,DefuLian,andEnhongChen
Itprovidesaconsistentmathematicalabstractionfordiversetimese- realpart𝑎[𝑘]andtheimaginarypart𝑏[𝑘]as:
riesdataunderconceptdriftandbasisevolution,therebyenabling
interpretablefrequency-domainrepresentations.Itincorporates 𝑋[𝑘] =
𝑁
∑︁
−1
𝑥[𝑛]·
(cid:20)
cos
(cid:18)2𝜋
𝑘𝑛
(cid:19)
−𝑗sin
(cid:18)2𝜋
𝑘𝑛
(cid:19)(cid:21)
severalkeyfeatures:(i)modelingamplitudeandphasecomponents 𝑁 𝑁
𝑛=0
independentlytocaptureunderlyingtemporaldynamicsincon- 𝑁
∑︁
−1 (cid:18)2𝜋 (cid:19)
ceptdrift,(ii)learningadaptivelytheweightsoffrequencybasis 𝑎[𝑘] = 𝑥[𝑛]·cos 𝑘𝑛
𝑁 (3)
componentsacrossdatapatchestotracktheevolvingimportance 𝑛=0
offrequencybases,(iii)atargetedlossfunctionthatexplicitlyac- 𝑁
∑︁
−1 (cid:18)2𝜋 (cid:19)
countsforbasisevolution,and(iv)anoveltrainingparadigmthat 𝑏[𝑘] =− 𝑥[𝑛]·sin 𝑘𝑛
𝑁
integratesHuberlosswithahybridstrongandweakconvergence 𝑛=0
frameworktoacceleratetrainingandimprovegeneralization,par- 𝑋[𝑘] =𝑎[𝑘]+𝑗·𝑏[𝑘]
ticularlywhenlarge-scale,high-qualityopendatasetsarelimited. Wecanderivetheamplitude𝐴[𝑘] andphase𝜙[𝑘] inthefre-
Ourmaincontributionsaresummarizedasfollows: quencydomainas:
• WeproposeFIRE,aunifiedfrequencydomaindecomposition 𝐴[𝑘] = √︁ 𝑎[𝑘]2+𝑏[𝑘]2
frameworkthatprovidesanalyticalmodelingfordiversetypesof
timeseries.FIREincorporatesseveralkeytechniquestoachieve (cid:18)𝑏[𝑘](cid:19) (4)
𝜙[𝑘] =arctan .
interpretabilityandrobustnessfortimeseriesforecasting. 𝑎[𝑘]
• ExtensiveexperimentsdemonstratethatFIREconsistentlyout- TheinverseDFTreconstructsthetimeseries𝑥(𝑡)as:
performsstate-of-the-artbaselinesacrossvariouslong-termfore-
castingtasks,deliveringcost-effectiveandinterpretablesolutions 𝑁 ∑︁ −1 (cid:18)2𝜋 (cid:19)
suitableforindustrialapplications. 𝑥[𝑛] =𝑎 0+ 𝛽 𝑘 𝐴[𝑘]·cos 𝑁 𝑘𝑛−𝜙[𝑘] , (5)
𝑘=1
where𝑎 0= 𝐴
𝑁
[0] istheDCcomponent(intercept)correspondingto
2 Preliminaries 𝑘 =0inthefrequencydomain,and𝛽
𝑘
istheweightofthe𝑘-thbasis
Weintroducetheanalyticalformulationoftimeseriesdata,key component.AlthoughtheFourierseriesisstrictlydefinedforperi-
conceptsofconceptdriftandbasisevolution,andthenotationsand odicsignals,non-periodicsignalscanbeapproximatedbyassuming
metricsusedinthispaper. thesequenceperiodmatchesthenumberoftimepoints.Thus,we
canhaveauniformrepresentationfor𝑥(𝑡)fromEquation(5).
2.1 AnalyticalFormulationofTimeSeriesData 2.2 ConceptDriftinTimeDomain
Inmathematicsandengineering,complexdatacanberepresented Mostmachinelearningalgorithmsassumestationarystatistical
asaninfiniteseriesofbasisvectors.TheFourierseries,awidely distributions between training and testing phases. However, in
usedsetofbasisvectors,effectivelyrepresentstimeseriesdata practicaltimeseriesapplications,theunderlyingdatadistribution
thatsatisfyspecificconditions.Specifically,ifatimeseries𝑥(𝑡)isa oftenevolves,leadingtodistinctpatternsinfuturedatacompared
periodicsignalwithperiod𝑇 andsatisfiestheDirichletconditions tohistoricaldata.Thisphenomenon,termedconceptdrift,refers
(i.e.,absolutelyintegrableoveroneperiod,withafinitenumberof totemporalchangesinstatisticalproperties[29].Indatastream
discontinuitiesofthefirstkindandextrema),thenthesignalcan mining,methodslikeADWIN[3]canbeusedtodetectchange
beaccuratelyrepresentedbyaFourierseries. pointsandidentifyshiftsindataconceptsovertime.
Wedefine𝑋[𝑘]asadiscreteFouriertransform(DFT)of𝑥(𝑛)as:
Definition1(Degreeofconceptdrift). Let𝑁
change
bethenumber
ofdetectedchangepointsand𝑁 bethetotalnumberoftime
total
pointsinadataset.Thedegreeofconceptdrift𝐷 isdefinedas:
𝑁−1 drift
𝑋[𝑘] = ∑︁ 𝑥[𝑛]·𝑒−𝑗2 𝑁 𝜋𝑘𝑛, (1) 𝑁 change
𝑛=0
𝐷 drift=
𝑁
total
(6)
Ahigher𝐷 indicatesmorefrequentchangesinthedatadis-
drift
tribution,andhencegreaterconceptdrift.
where𝑛isthetimeindexinthetemporaldomain,𝑘isthefrequency
indexinthefrequencydomain,bothrangingfrom0to𝑁 −1,and
𝑗 istheimaginaryunitsatisfying 𝑗2 =−1.UsingEuler’sformula, 2.3 BasisEvolutioninFrequencyDomain
wecanexpresstheexponentialtermintrigonometricformas: Conceptevolutiontraditionallyreferstotheemergenceofnew
classesorconceptsindatastreams[23],andcanbeextendedto
changesintheunderlyingbasisfunctionsinfrequency-domain
(cid:18)2𝜋 (cid:19) (cid:18)2𝜋 (cid:19) time series analysis. After time series data is transformed into
𝑒−𝑗2 𝑁 𝜋𝑘𝑛 =cos 𝑁 𝑘𝑛 −𝑗sin 𝑁 𝑘𝑛 (2) the frequency domain via FFT, it is segmented into patches,
each represented by a vector of 𝑁 basis energies: E(𝑞) =
(cid:0)𝐸(𝑞),𝐸(𝑞),...,𝐸(𝑞)(cid:1), 𝑞 = 1,2,...,𝑄,where𝐸(𝑞) ≥ 0istheen-
1 2 𝑁 𝑘
SubstitutingEquation(2)intoEquation(1),wecanobtainthe ergyofthe𝑘-thfrequencybasisinpatch𝑞.
2

---

# Page 3

AUnifiedFrequencyDomainDecompositionFrameworkforInterpretableandRobustTimeSeriesForecasting Conference’17,July2017,Washington,DC,USA
Definition2(Basisevolutioncriterion). Foreachbasis𝑘,the 3.1 ModelArchitecture
relativeenergychangebetweentwoconsecutivepatches𝑞−1and Toeffectivelycapturecomplextemporaldependenciesandconcept
𝑞is: drift,FIREprimarilyoperatesinthefrequencydomain.Specifically,
|𝐸(𝑞) −𝐸(𝑞−1)| therawmultivariatetimeseriesdataisfirstpreprocessedandtrans-
𝛿(𝑞) = 𝑘 𝑘 , (7) formedintothefrequencydomainviatheFastFourierTransform
𝑘 𝐸
𝑘
(𝑞−1) +𝜂
(FFT),whichdecomposesthesignalsintoorthogonalsinusoidal
where𝜂 >0isasmallconstanttoavoiddivisionbyzero.Basis𝑘is basisfunctions.Thistransformation,alongwiththeresultingfre-
saidtoevolveatpatch𝑞if quencydomainrepresentation,revealsrichspectralcharacteristics
thatfacilitatethedesignofspecializedmodulescapableofmodeling
𝛿(𝑞) >𝜖, (8) intricatecorrelationsandevolvingpatternsinthedata,whileadap-
𝑘
tivelyhandlingbasisevolution.FIREiscomposedofthreemain
where𝜖 >0isafixedthreshold.
components,illustratedinFigure1:
Definition3(Patch-levelbasisevolution). Apatch𝑞 iscon- • Embeddingandtransformation:ThismoduleappliesChan-
sideredtoexhibitbasisevolutionifthefractionofevolvingbases nel Independent (CI) processing and Instance Normalization
exceedsathreshold𝜏 ∈ (0,1]: (IN)totherawinputdata.Thenormalizeddataissegmented
intopatchesandconvertedintothefrequencydomainviaFFT.
1 𝑁 ∑︁ −1 1 (cid:0)𝛿(𝑞) >𝜖(cid:1) >𝜏, (9) Thesefrequency-domainpatchesarethenembeddedintoahigh-
𝑁 𝑘 dimensionalfeaturespacethroughadedicatedembeddinglayer,
𝑘=0
enablingeffectivefeatureextraction.
where1(·)istheindicatorfunction. • Frequencydomainbackbone:Operatingoncomplex-valued
frequencypatches,thisbackboneemployscomplexlinearlayers
Definition 4 (Degree of basis evolution). Let Q𝑒 = {𝑞 |
tocaptureintra-patchcorrelations.Itexplicitlymodelsamplitude
patch𝑞exhibitsbasisevolution} be the set of evolving patches.
andphasecomponentstohandleconceptdrift,whileanattention
Thedegreeofbasisevolutionover𝑄patchesis:
mechanismadaptivelylearnsweightsforthesinusoidalbasisto
𝐷 𝑒𝑣𝑜𝑙𝑢𝑡𝑖𝑜𝑛 =
|Q
𝑄
𝑒|
∈ [0,1]. (10)
a
in
d
t
d
o
re
c
s
o
s
m
b
p
a
l
s
e
i
x
s
r
e
e
v
p
o
r
l
e
u
s
t
e
io
n
n
ta
.
t
T
io
h
n
e
s
p
f
r
o
o
r
ce
su
ss
b
e
s
d
eq
fe
u
a
e
t
n
u
t
r
p
es
ro
a
c
r
e
e
s
r
s
e
in
c
g
o
.
mbined
• Outputprojectionmodule:Thismodulegeneratesfrequency-
Basisevolutionreflectsthenon-stationarynatureoftimeseries,
domainpredictionsbyflatteningandapplyingalinearprojec-
as the frequency components that characterize the data evolve
tion. The predicted signals are then transformed back to the
overtime.Thenon-stationarynaturecomplicatesmodelingand
timedomainthroughinverseFFT(iFFT),followedbyinstance
predictioninthefrequencydomain.
denormalizationtoproducethefinalforecasts.
• Compositelossfunction:Toeffectivelyhandlebasisevolution
2.4 StrongandWeakConvergence
andconceptdrift,FIREemploysacompositelosscombiningthree
Instatisticallearningtheory[30],convergenceinHilbertspacesis terms:aHuberlosswithhybridconvergencethatbalancesstrong
categorizedintostrongandweakconvergence[17].Specifically,a andweakconvergenceforbettergeneralizationundersparseand
sequenceoffunctions{𝑓 ℎ(𝒙)}
ℎ
∞
=1
issaidtoconvergestronglytoa noisydata;anFFT-domainlossthatdirectlyminimizespredic-
targetfunction𝑓(𝒙)if: tionerrorsinthefrequencydomain,thusexplicitlyaddressing
basisevolution;andaphaseregularizationtermthatenforces
lim ∥𝑓 ℎ(𝒙)−𝑓(𝒙)∥=0, (11)
smoothphasetransitionstoenhancestabilityandrobustnessof
ℎ→∞
thelearnedrepresentations.
wherethenormisdefinedinthecorrespondingHilbertspace.In
contrast,{𝑓 ℎ(𝒙)}
ℎ
∞
=1
convergesweaklyto𝑓(𝒙)if:
freq
T
u
h
e
r
n
o
c
u
y
g
-
h
do
th
m
e
a
i
in
nt
f
e
r
g
a
r
m
a
e
ti
w
o
o
n
r
o
k
f
,F
th
IR
e
E
se
eff
co
e
m
cti
p
v
o
e
n
ly
en
ca
ts
pt
w
u
i
r
t
e
h
s
i
b
n
o
a
th
u
g
n
l
i
o
fi
b
e
a
d
l
lim⟨𝜙(𝒙),𝑓 ℎ(𝒙)−𝑓(𝒙)⟩=0, ∀𝜙(𝒙) ∈𝐿 2 , (12) andlocaltemporaldynamics,enablinginterpretableandrobusttime
ℎ→∞
seriesforecasting.
where⟨·,·⟩denotestheinnerproductin𝐿
2
space.
Strongconvergenceimposesstricterpointwisestability.Itoffers
robusttheoreticalguarantees,butrequireslargedatasetsandexten- 3.2 EmbeddingandTransformation
sivetraining.Incontrast,weakconvergencefocusesonstatistical
LetX=[𝑋 𝑐,𝑙 :𝑐 ∈ [𝐶],𝑙 ∈ [𝐿]]denoteamultivariatetimeseriesin-
behavioracrossthedatadistributionandimposeslessrestrictivere-
stancewith𝐶variablesand𝐿timestamps.Eachinstanceisfirstpro-
quirements.Itenablesfastertrainingandbetterperformancewith
cessedusingChannelIndependent(CI)processingandsegmented
sparsedata,whilemaintainingrigorousmathematicalfoundations.
intooverlappingpatchesfollowingthepatchingscheme[25].The
Inthiswork,weaimtocombinestrongandweakconvergence. resultingpatchesarerepresentedasX𝑃 ∈ R𝑁𝑝×𝐿𝑝,where𝑁 𝑝 is
thenumberofpatchesand𝐿 isthelengthofeachpatch.These
𝑝
3 FIREDesign patchesarethentransformedintothefrequencydomainviaFFT.
WepresentFIRE’sdesign,aimingtoaddressconceptdriftandbasis Subsequently, a linear embedding layer projects the frequency-
evolution. domainpatchesintoahigher-dimensionalfeaturespace,yielding
3

---

# Page 4

Conference’17,July2017,Washington,DC,USA ChengHe,XijieLiang,ZengrongZheng,PatrickP.C.Lee,XuHuang,ZhaoyiLi,HongXie,DefuLian,andEnhongChen
Predicted Output
(e.g., 3 channels)
iFFT
Linear
Projection
Basis evolution
modeling Causal Complex
Attention( ) Data Reconst
Concept drift
modeling
Linear(A) Linear(Φ)
Patch Mixing
Complex Linear
Embedding
FFT
Patching
CI +
Instance Norm
Multivariate Time Series Data
(e.g., 3 channels)
&
gniddebmE
noitamrofsnarT
Channel Patch FFT
results
ycneuqerF
enobkcaB
niamoD
4
2
Instance
Denorm
Output
0
Project 0 5 10 15
Frequency index
Figure1:ModelarchitectureofFIRE.Ittranformsmultivari-
atetimeseriesintothefrequencydomainthroughasequence
ofstepsincludingCI,IN,patching,andFFT.Itcapturesintra-
patch correlations using complex linear layers. It models
conceptdriftvialineartransformations,andbasisevolution
viacausalattentionmechanisms.Itfinallygeneratespredic-
tionsbyaflattenedlinearprojectionlayer.
H𝑖 ∈C𝑁𝑝×𝐷,where𝐷denotestheembeddingdimension:
X𝑃 =FFT(Patching(CI(X))),
(13)
H𝑖 =Wembed·X𝑃 .
Here,H𝑖 isacomplex-valuedtensorcapturingrichfrequencyfea-
turesfordownstreamprocessing.
3.3 FrequencyDomainBackbone
Startingfromtheembeddedfrequency-domaininputH𝑖 ∈C𝑁𝑝×𝐷,
FIREappliesacomplex-valuedlineartransformationtomodelintra-
patchcorrelations:
H𝑃 =Linear C(H𝑖)=WC·H𝑖+bC , (14)
whereWC ∈C𝐷×𝐷andbC ∈C𝐷arelearnablecomplexweightsand
biases,andtheoutputH𝑃 ∈C𝑁𝑝×𝐷 retainsthesamedimensionsas
theinput.
Thiscomplexlineartransformationeffectivelymodelsthelocal-
izedfrequencyinteractionswithineachpatch,enablingthenetwork
toextractrichamplitudeandphaseinformationthatiscrucialfor
representingtemporaldynamics.Suchfrequency-domainrepre-
sentationsnaturallyfacilitatethecharacterizationofconceptdrift,
as temporal distributional shiftsmanifest as variationsin these
frequencycomponents.
)edutilpma(01gol
π
Patch 1
Patch 2 π/2
0
-π/2
-π0 5 10 15
Frequency Index
(a)Amplitudevariationbetweenconsecu-
tivefrequencypatches
)dar(
esahP
Patch 1
Patch 2
(b) Phasevariationbetweenconsecutive
frequencypatches
Figure2:Variationsinamplitudeandphasedistributions
between consecutive frequency patches in the frequency
domain. The patches are sampled from the Weather and
Etth1datasets,respectively.
Learningofconceptdrift.Conceptdriftreferstotemporaldis-
tributionalshifts,whichcanbeequivalentlycharacterizedinthe
frequencydomainasvariationsinamplitudeandphasedistribu-
tionsacrosslocalizedfrequencypatches(Figure2).
Lemma3.1(EquivalenceofConceptDriftModelinginTempo-
ralandFrequencyDomains). Anon-stationarytimeserieswith
time-varyingdistributionexhibitsconceptdrift.Underlineartime-
invariantsignaldecomposition,modelingdistributionalshiftsinthe
temporaldomainisequivalenttomodelingindependentchanges
inamplitudeandphaseinthefrequencydomain.
Proof. Anytimeseriescanbedecomposedintofrequencycom-
ponents via the Fourier transform (see Section 2, Equation (5)).
SincethediscreteFouriertransform(DFT)isalinear,invertible
mapping—andthefastFouriertransform(FFT)providesanefficient
waytocomputeit—itpreservesallinformationcontainedinthe
originaltimeseries.Consequently,anytemporalchangesinthe
series,suchasshiftsinmean,variance,orotherdistributionalprop-
erties,manifestascorrespondingchangesintheamplitudeand
phaseofthefrequencycomponents.Thisone-to-onecorrespon-
denceguaranteesthatmodelingconceptdriftinthetimedomainis
fullyequivalenttomodelingitinthefrequencydomain,without
anylossofinformation. □
BasedonthecomplexlineartransformationoutputH𝑃 ,weex-
tractamplitudeA ∈ R𝑁𝑝×𝐷 andphase𝝓 ∈ [−𝜋,𝜋]𝑁𝑝×𝐷 compo-
nents.Toeffectivelycaptureconceptdrift,FIREmodelsamplitude
andphasevariationsacrosspatchesindependently.Specifically,it
employstwoseparatelinearlayerstolearntheinter-patchcorrela-
tionsforamplitudeandphase:
A ˆ =Linear 𝐴𝑚𝑝(A)=W𝐴𝑚𝑝A+b𝐴𝑚𝑝 ,
(15)
𝝓 ˆ =Linear 𝜙(𝝓)=W𝜙𝝓+b𝜙 ,
whereW𝐴𝑚𝑝 ,W𝜙 ∈R𝐷×𝐷 andb𝐴𝑚𝑝 ,b𝜙 ∈R𝐷 arelearnableparam-
eters.Thisdisentangleddesignenablesinterpretableandeffective
adaptationtonon-stationarytimeseriesbyseparatelymodeling
amplitudeandphasedriftdynamics.
Learningofbasisevolution.Whilelinearlayerseffectivelycap-
tureconceptdriftthroughamplitudeandphasevariations,their
capacitytomodelthemorecomplex,non-lineartemporaldynam-
icsoffrequencybasisevolutionislimited.Inparticular,traditional
frequency-domainmodelsrelyingsolelyonlineartransformations
struggletoadapttoabruptchangesorlong-rangedependenciesin
4

---

# Page 5

AUnifiedFrequencyDomainDecompositionFrameworkforInterpretableandRobustTimeSeriesForecasting Conference’17,July2017,Washington,DC,USA
thespectralbases.Incontrast,causalattentionprovidesaflexible 3.4 OutputProjection
mechanismtodynamicallyweightandintegratehistoricalampli- Afterbackboneprocessing,FIREflattenstheoutputH𝑜 andpasses
tudefeatures,makingitbettersuitedtohandlesuddenshiftsand itthroughalinearprojectionlayertoproducepredictionsinthe
intricatebasisevolutionpatterns. frequencydomain.Thesearethentransformedbacktothetime
FIREleveragesacausalmaskedattentionmechanismapplied domainusingiFFT,followedbyinstancedenormalization,toyield
directlyonthepreviousoutputedamplituderepresentationsA ˆ ∈ thefinalforecasts:
R𝑁𝑝×𝐷 obtainedfromtheamplitudelinearlayer(Equation(15)).
Thissequenceofamplitudeembeddingscompactlyrepresentsthe X𝑜𝑢𝑡 =Denorm(iFFT(WLinProj·Flatten(H𝑜))) (21)
frequencybasesacrosspatches𝑝 =1,...,𝑁 𝑝 .Thecausalattention whereX out ∈R𝐿𝑝𝑟𝑒𝑑×𝐶,with𝐿 𝑝𝑟𝑒𝑑 denotingthepredictionlength.
offersthreekeyadvantagesoverlinearlayers:
• Adaptivetemporalweighting:Itdynamicallylearnstoweigh 3.5 LossFunction
historicalamplitudefeatures,focusingonthemostrelevantpast Aftertheoutputprojectionmodule,weneedtoquantifytheloss
patchesforthecurrentbasisevolution. betweenX𝑜𝑢𝑡 andthegroundtruthX𝑡𝑟𝑢𝑒 .FIREemploysacomposite
• Modelinglong-rangedependencies:Self-attentionnaturally losscomprisingtheHuberlosswithhybridconvergence(L𝑤ℎ ),FFT
capturescomplexdependenciesacrossdistantpatches,essential loss(Lfft ),andphaseregularization(R𝜙 ).Thislossalsoexplicitly
forrepresentinggradualorabruptspectralchanges. guidesthemodeltoaddressconceptdriftandbasisevolutioninthe
• Preserving causality: The causal mask ensures that the ba- frequencydomain,therebyprovidingaclearobjectiveforparameter
sisatpatch𝑝 dependsonlyoncurrentandpastpatches≤ 𝑝, optimization:
maintainingtemporalconsistencyrequiredforforecasting. L=L𝑤ℎ+Lfft+R𝜙 . (22)
Formally,theamplitudefeaturesareprojectedintoqueriesand Theindividualcomponentsaredetailedasfollows.
keys: Huberlosswithhybridconvergence.Tobalancestrongand
Q=A ˆ W𝑄 , K=A ˆ W𝐾 , (16) weakconvergenceandimprovegeneralizationundersparsedata
(Section2),FIREadoptsHuberloss[15],whichsmoothlyinterpo-
where W𝑄 ,W𝐾 ∈ R𝐷×𝑑 are learnable parameters, and𝑑 is the latesbetweenℓ andℓ losses:
2 1
attentiondimension.
M T ∈ h { e 0, s − ca ∞ le } d 𝑁 d 𝑝 o × t 𝑁 - 𝑝 p : roductattentionscoresaremaskedcausallyby L𝛿(X𝑡𝑟𝑢𝑒 ,X𝑜𝑢𝑡)= 𝐿 1 𝐿 ∑︁ 𝑝𝑟𝑒𝑑 𝛿2 (cid:32)√︂ 1+ (cid:16)𝑥 𝑡𝑟𝑢𝑒 𝛿 −𝑥 𝑜𝑢𝑡(cid:17)2 −1 (cid:33)
𝑝𝑟𝑒𝑑
𝑙=1
(cid:40) (23)
0, 𝑞≤𝑝
M𝑝,𝑞 = , where𝛿isahyperparametercontrollingthetransitionthreshold.
−∞, 𝑞 >𝑝
Toincorporateweakconvergence(Equation(12)),theHuberloss
where𝑞≤𝑝indicatesthatattentionatpatch𝑝iscomputedonly isweightedbyamatrixW∈R1×𝐵 (withbatchsize𝐵)thatlinearly
overpatch𝑝 andallprecedingpatches𝑞,ensuringcausalityby combinesidentityandpredicate-basedcomponents:
excludingfuturepatches.TheattentionweightsW∈R𝑁𝑝×𝑁𝑝 are 𝐵
∑︁
computedas L𝑤ℎ = W·L𝛿(𝑥 𝑡𝑟𝑢𝑒 ,𝑥 𝑜𝑢𝑡), W=𝜏ˆI+𝜏P, (24)
(cid:18) QK⊤ (cid:19) 𝑏=1
W=softmax √
𝑑
+M . (17) where𝜏 =1−𝜏ˆbalancesstrongandweakconvergence,Iisthe
identitymatrix,andPistheempiricalcovariancematrixofpredi-
Tofurtherrefineintra-patchimportance,amplitudevectorA ˆ is
cates:
projectedbyalearnablelinearlayer: 1 ∑︁ 𝑚
V=W𝑝A ˆ +b𝑝 , (18) P= 𝑚 𝑠=1 𝜓 𝑠 𝜓 𝑠 ⊤. (25)
where𝑚isthenumberofpredicates.Forsimplicity,weuseasingle
whereV ∈ R𝑁𝑝×𝐷,W𝑝 ∈ R𝐷×𝐷 andb𝑝 ∈ R𝐷.Thefinaldynamic
predicate𝜓(𝒙)=1inthiswork.Thisformulationleveragesstatisti-
weightsUmodulatingthefrequencybasesareobtainedbycombin-
calinvariantscapturedbyweakconvergencetoenhancerobustness
inginter-patchattentionandintra-patchprojections:
andgeneralization,particularlyinnoisyorsparsescenarios.
U=WV, (19) FFTloss.TheFFTloss,Lfft ,isdefinedasthemeanabsoluteerror
(MAE)betweenthepredictedandgroundtruthsequencesinthe
withU ∈ R𝑁𝑝×𝐷.TheseadaptiveweightsUareappliedelement- frequencydomain:
wisetotheoriginalfrequencybasesB,producingthedynamically
evolvedbases: 1 ∑︁
𝑁𝑓
H𝑜 =U⊙B, (20)
Lfft=
𝑁 𝑓
𝑘=1
|FFT(X𝑡𝑟𝑢𝑒)−FFT(X𝑜𝑢𝑡)| (26)
whereH𝑜 ∈C𝑁𝑝×𝐷,⊙denoteselement-wisemultiplication. where𝑁
𝑓
isthenumberofbasesofthepredictedsequenceinthe
Thiscausalattention-baseddesignenablesFIREtoflexiblyand frequencydomain.Thislossexplicitlyaddressesbasisevolutionby
effectivelycapturecomplex,non-linear,andtemporallyadaptive minimizingdiscrepanciesinfrequencybasisvectors.
basisevolutionpatterns,surpassingtherepresentationallimitations Phaseregularization.Toensuresmoothandstablephasetran-
oftraditionallinearlayers. sitions,FIREintroducesphaseregularizationtoconstrainphase
5

---

# Page 6

Conference’17,July2017,Washington,DC,USA ChengHe,XijieLiang,ZengrongZheng,PatrickP.C.Lee,XuHuang,ZhaoyiLi,HongXie,DefuLian,andEnhongChen
changesinthepredictedsequence.Itformulatesafirst-orderdiffer- Table1:Statisticsofdatasets
encepenalty:
Dataset Length Dimension Frequency
R𝜙 =𝜆 𝐷 1 −1 𝐷 ∑︁ −1 (cid:16) 𝜙 𝑜 𝑑 𝑢 + 𝑡 1−𝜙 𝑜 𝑑 𝑢𝑡 (cid:17)2 , (27) E E T T T T m h 1 6 7 9 4 6 2 8 0 0 7 7 1 1 5 h m ou in r
𝑑=1 Weather 52696 21 10min
where𝜆isaweightingfactor,𝐷isthemodeldimensionality,and Electricity 26304 321 1hour
𝜙𝑑 denotesthephasefeatureofthe𝑑-thdimension.Thisenhances Traffic 17544 862 1hour
out
modelrobustnessandgeneralizability.
3.6 Discussion Weselectrepresentativebaselinesforcomparison.Werepro-
Timeseriesforecastinginthetimedomainischallengingdueto ducetheresultsoftwofrequency-basedmodels,FredFormer[27]
complexpatternsandlimitedinformation.Instead,FIREfirsttrans- andWPMixer[24].Forotherbaselines,includingTimeMixer[33],
formsthedataintothefrequencydomainviaFFT,whichdecom- iTransformer[21],PatchTST[25],andTimesNet[35],wereport
posesthe signalinto multiplefrequency basiscomponents. We theresultsaspublishedintheirrespectivepapers.
chooseFFToverotherbasisdecompositionmethodsbecauseitis
reversibleandparameter-free,requiringnohyperparametertuning 4.2 ExperimentalSettings
orpriorknowledge,thusmakingitbroadlyapplicabletovarious Wechoosealook-backwindowof96andforecastfuturetimepoints
timeseries(seeAppendixAfordetails). 𝑇 ∈{96,192,336,720}.Weusethemeansquarederror(MSE)and
Traditionalmethodstypicallymodeltherealandimaginaryparts meanabsoluteerror(MAE)astheevaluationmetricsandcompare
ofthetransformedsignal.However,theselackclearphysicalin- theresultswiththebest-performingresultsofSOTAmodelspre-
terpretationandmakeithardtohardtoconnecttheresultsback sentedinpapersorreproducedfromtheirpublishedsourcecodes.
totheoriginaldata.Incontrast,FIREconvertseachcomplexcom- WeimplementFIREinPyTorch[26]andtrainitonasingleNVIDIA
ponentintoamplitude(indicatingthestrengthorenergyofeach A10040GBGPU.
basis)andphase(indicatingthetiming),modelingthemseparately
(Equation(4)).Thisdecompositionenablesthemodeltocapturedis- 4.3 ForecastingResults
tinctphysicalfeaturesandconceptdriftpatternswhilemaintaining
Table2summarizesthefullforecastingresults,withthebestperfor-
adirectlinktotheoriginalsignal.Tobettercapturethetempo-
mancehighlightedinbold.TheresultsshowthatFIREconsistently
ralevolutionoffrequencybases,weintroduceacausalattention
outperformsallcompetitors,achievingthebestresultsin21out
mechanismthatadaptivelylearnshowbasiscomponentschange
of 35 tasks based on MSE and 26 out of 35 based on MAE. On
andinteractacrosspatches(Equations(16)–(20)).Afterforecasting
average,FIREimprovesMSEby3%-8%comparedtothesecond-
inthefrequencydomain,themodelconvertstheresultsbackto
best model, WPMixer, and by 20%-30% compared to the worst-
thetimedomain.Finally,acompositelossfunction(Equation(22))
performingmodel,TimesNet,withthelargestgainsobservedin
isemployed,measuringlossinbothtime(Equation(12))andfre-
certain datasets such as ETTh1 and Traffic. Similarly, for MAE,
quencydomains(Equation(26)),whileconstrainingphaseshifts
FIRE’srelativeimprovementsare2%-7%overWPMixerand15%-
(Equation(27))toensuresmoothandrobustpredictions.
25%overTimesNetacrossvarioustasks.Ourresultsdemonstrate
Insummary,FIREsucceedsbyextractingmoreinterpretableand
FIRE’srobustnessandsuperiorabilitytocapturecomplextemporal
physicallymeaningfulfeatures,explicitlymodelingtheirdynamics
dynamicsforlong-termforecasting.
andinteractions,andoptimizingwithmathematicallyandphysi-
callygroundedobjectives.ThisdesignmakesFIRErobust,adaptive,
4.4 AblationResults
andaccurateacrossdiversereal-worldforecastingtasks.
Tocomprehensivelyassesstheeffectivenessofourmoduledesign,
wereporttheaverageforecastingresultsacrosssevendatasetsinTa-
4 Experiments
ble3.Ourfullmodel,FIRE,achievesthebestaverageMSEon5out
WeextensivelyevaluatetheperformanceofFIREacrossavarietyof
of7datasetsandthebestaverageMAEon6outof7datasets,con-
long-termforecastingtasks.WecompareFIREagainststate-of-the-
sistentlyoutperformingthetwovariants:FIRE_advanced,which
artbaselines,particularlythosethatemphasizefrequency-domain
removesthebasisevolutionmodule,andFIRE_base,whichsim-
modelingoftimeseriesdata.Wealsoperformcomprehensiveab-
plifiesconceptdriftmodeling.Thesequantitativeimprovements
lationstudies,hyperparametersensitivityanalyses,andtargeted
highlighttheimportanceofjointlymodelingbothdatadriftand
experimentsonhandlingconceptdriftandbasisevolution.
basisevolutiontocapturecomplextemporaldynamicsforaccu-
rateforecasting.Weprovidethefulldetailedforecastingresults
4.1 DatasetsandBaselines inAppendix(SectionB.2),whichfurtherverifythatFIREattains
Weconductexperimentsonsevenwidelyusedpublictimeseries superiorperformanceinthemajorityofindividualexperiments,
forecasting datasets [36] (see Table 1), including the Electricity demonstratingitsrobustnessandeffectiveness.
TransformerTemperaturedatasetsatbothhourlyandminute-level Weconductanablationstudybyprogressivelyremovingcompo-
granularities(ETTh1,ETTh2,ETTm1,ETTm2),aswellasWeather, nentsofthelossfunctiontoevaluatetheirindividualcontributions.
Traffic,andElectricityPowerConsumption(ELC). Specifically,FIRE_enhancedremovesthephaseregulationtermR𝜙 ;
6

---

# Page 7

AUnifiedFrequencyDomainDecompositionFrameworkforInterpretableandRobustTimeSeriesForecasting Conference’17,July2017,Washington,DC,USA
Table2:Long-termforecastingresultsforpredictionlengths𝑇 ∈{96,192,336,720}.Bestresultsarehighlightedinbold.
Model FIRE Fredformer WPMixer TimeMixer iTransformer PatchTST TimesNet
Dataset T MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
96 0.365 0.390 0.373 0.392 0.375 0.393 0.375 0.400 0.386 0.405 0.460 0.447 0.384 0.402
192 0.420 0.418 0.433 0.420 0.428 0.417 0.429 0.421 0.441 0.436 0.512 0.477 0.436 0.429
ETTh1 336 0.458 0.437 0.470 0.437 0.477 0.439 0.484 0.458 0.487 0.458 0.546 0.496 0.638 0.469
720 0.456 0.454 0.467 0.456 0.460 0.454 0.498 0.482 0.503 0.491 0.544 0.517 0.521 0.500
Avg. 0.425 0.425 0.436 0.426 0.435 0.426 0.447 0.440 0.454 0.447 0.516 0.484 0.495 0.450
96 0.282 0.333 0.293 0.342 0.283 0.335 0.289 0.341 0.297 0.349 0.308 0.355 0.340 0.374
192 0.362 0.383 0.371 0.389 0.364 0.391 0.372 0.392 0.380 0.400 0.393 0.405 0.402 0.414
ETTh2 336 0.403 0.419 0.382 0.409 0.409 0.424 0.386 0.414 0.428 0.432 0.427 0.436 0.452 0.452
720 0.408 0.433 0.415 0.434 0.429 0.443 0.412 0.434 0.427 0.445 0.436 0.450 0.462 0.468
Avg. 0.364 0.392 0.365 0.394 0.371 0.398 0.364 0.395 0.383 0.407 0.391 0.411 0.414 0.427
96 0.310 0.344 0.326 0.361 0.316 0.352 0.320 0.357 0.334 0.368 0.352 0.374 0.338 0.375
192 0.356 0.375 0.363 0.380 0.362 0.376 0.361 0.381 0.377 0.391 0.390 0.393 0.374 0.387
ETTm1 336 0.385 0.397 0.395 0.403 0.387 0.396 0.390 0.404 0.426 0.420 0.421 0.414 0.410 0.411
720 0.448 0.431 0.453 0.438 0.447 0.432 0.454 0.441 0.491 0.459 0.462 0.449 0.478 0.450
Avg. 0.375 0.387 0.384 0.396 0.378 0.389 0.381 0.395 0.407 0.410 0.406 0.407 0.400 0.406
96 0.170 0.252 0.177 0.259 0.171 0.252 0.175 0.258 0.180 0.264 0.183 0.270 0.187 0.267
192 0.237 0.297 0.243 0.301 0.233 0.294 0.237 0.299 0.250 0.309 0.255 0.314 0.249 0.309
ETTm2 336 0.299 0.338 0.302 0.340 0.290 0.333 0.298 0.340 0.311 0.348 0.309 0.347 0.321 0.351
720 0.399 0.395 0.397 0.396 0.387 0.390 0.391 0.396 0.412 0.407 0.412 0.404 0.408 0.403
Avg. 0.276 0.321 0.280 0.324 0.270 0.317 0.275 0.323 0.288 0.332 0.290 0.334 0.291 0.333
96 0.162 0.204 0.163 0.207 0.162 0.204 0.163 0.209 0.174 0.214 0.186 0.227 0.172 0.220
192 0.207 0.246 0.211 0.251 0.209 0.246 0.208 0.250 0.221 0.254 0.234 0.265 0.219 0.261
Weather 336 0.263 0.287 0.267 0.292 0.263 0.287 0.251 0.287 0.278 0.296 0.284 0.301 0.246 0.337
720 0.340 0.338 0.343 0.341 0.340 0.339 0.339 0.341 0.358 0.347 0.356 0.349 0.365 0.359
Avg. 0.243 0.269 0.246 0.273 0.244 0.269 0.240 0.271 0.258 0.278 0.265 0.285 0.251 0.294
96 0.474 0.272 0.406 0.277 0.465 0.286 0.462 0.285 0.395 0.268 0.526 0.347 0.593 0.321
192 0.487 0.269 0.426 0.290 0.475 0.290 0.473 0.296 0.417 0.276 0.522 0.332 0.617 0.336
Traffic 336 0.484 0.275 0.432 0.281 0.489 0.296 0.498 0.296 0.433 0.283 0.517 0.334 0.629 0.336
720 0.531 0.295 0.463 0.300 0.527 0.318 0.506 0.313 0.467 0.302 0.552 0.352 0.64 0.35
Avg. 0.494 0.278 0.432 0.287 0.489 0.298 0.484 0.297 0.428 0.282 0.529 0.341 0.62 0.336
96 0.148 0.236 0.147 0.241 0.150 0.241 0.153 0.247 0.148 0.240 0.190 0.296 0.168 0.272
192 0.161 0.249 0.165 0.258 0.162 0.252 0.166 0.256 0.162 0.253 0.199 0.304 0.184 0.322
Elc 336 0.176 0.265 0.177 0.273 0.179 0.270 0.185 0.277 0.178 0.269 0.217 0.319 0.198 0.300
720 0.215 0.299 0.213 0.304 0.217 0.304 0.225 0.310 0.225 0.317 0.258 0.352 0.220 0.320
Avg. 0.175 0.262 0.176 0.269 0.177 0.267 0.182 0.272 0.178 0.270 0.216 0.318 0.193 0.304
Best_count 21/35 26/35 8 1 6 9 0 0 0 0 0 0 0 0
Table3:Averageresultsofmoduleablation Table4:Averageresultsoflossablation
Model FIRE FIRE_adv. FIRE_base Model FIRE FIRE_enh. FIRE_adv. FIRE_base
Dataset MSE MAE MSE MAE MSE MAE Dataset MSE MAE MSE MAE MSE MAE MSE MAE
ETTh1 0.425 0.425 0.431 0.430 0.434 0.427 ETTh1 0.424 0.424 0.428 0.427 0.439 0.437 0.433 0.433
ETTh2 0.364 0.392 0.362 0.392 0.363 0.393 ETTh2 0.363 0.392 0.363 0.391 0.385 0.406 0.367 0.394
ETTm1 0.375 0.387 0.375 0.391 0.376 0.390 ETTm1 0.374 0.386 0.374 0.387 0.384 0.401 0.378 0.395
ETTm2 0.276 0.321 0.277 0.322 0.275 0.320 ETTm2 0.276 0.320 0.277 0.319 0.296 0.343 0.282 0.327
Weather 0.243 0.269 0.245 0.272 0.246 0.272 Weather 0.243 0.268 0.243 0.267 0.2448 0.2710 0.2450 0.2705
Traffic 0.494 0.278 0.495 0.290 0.506 0.308 Traffic 0.494 0.277 0.487 0.286 0.509 0.287 0.510 0.290
Elc 0.175 0.262 0.178 0.264 0.189 0.273 Elc 0.175 0.262 0.174 0.262 0.180 0.270 0.181 0.270
Best_Count 5/7 6/7 1/7 0/7 1/7 1/7 Best 4/7 4/7 3/7 3/7 0 0 0 0
4.5 ConceptDriftandBasisEvolution
WequantifythedegreeofconceptdriftusingADWIN(Section2.2)
and the degree of basis evolution (Section 2.3). To evaluate the
FIRE_advancedfurtherremovestheFFTlossL𝑓𝑒𝑞 basedonFIRE impactofthesephenomenaonmodelperformance,weselecttwo
_base;andFIRE_basediscardsallspecializedlossdesigns,relying representativeunivariatetimeseries:Weather_d11(dimension11)
solelyontheHuberloss.Table4presentstheaverageforecasting andTraffic_d738(dimension738).Weather_d11exhibitsaconcept
results.WhilethefullmodelFIREshowsslightlybetteraverage driftdegreeof3.07%andabasisevolutiondegreeof8.39%,whereas
MSEandMAEcomparedtoFIRE_enhanced,thefulldetailedre- Traffic_d738showssubstantiallylowerdegreesof0.26%and1.19%,
sults(seeAppendixB.2)revealthatFIREconsistentlyoutperforms respectively.WeapplyFIREtothesedatasetsandcompareitsfore-
allvariantsonalargernumberofindividualexperiments.This castingaccuracyagainstthreeSOTAfrequency-domainmodels:
indicatesthatalthoughtheaverageimprovementsappearmodest, FredFormer,WPMixer,andFITS.AsshowninTable5,FIREcon-
thefullmodeldemonstratesmoresubstantialandconsistentad- sistentlyoutperformsthesebaselines,especiallyonWeather_d11
vantagesinspecificcases,highlightingtheimportanceofeachloss wheredatadriftandbasisevolutionaremorepronounced.Specif-
componentforrobustforecastingperformance. ically,onWeather_d11,FIREachievesanaverageMSEreduction
7

---

# Page 8

Conference’17,July2017,Washington,DC,USA ChengHe,XijieLiang,ZengrongZheng,PatrickP.C.Lee,XuHuang,ZhaoyiLi,HongXie,DefuLian,andEnhongChen
Table5:Effectivenessofconceptdriftandbasisevolution.
0.28
Model FIRE FredFormer Wpmixer FITS
0.25
Dataset T MSE MAE MSE MAE MSE MAE MSE MAE
96 0.110 0.237 0.131 0.260 0.111 0.239 0.127 0.257 0.23
192 0.185 0.312 0.203 0.326 0.193 0.317 0.200 0.322 0.20
Weather-d11 336 0.302 0.395 0.321 0.405 0.305 0.395 0.317 0.401
720 0.462 0.497 0.481 0.503 0.469 0.496 0.478 0.501 32 64 128 256
Avg. 0.264 0.360 0.284 0.373 0.269 0.362 0.280 0.370 Dimension
96 1.854 0.687 1.882 0.742 1.871 0.690 1.921 0.741
192 1.898 0.687 1.969 0.746 1.918 0.679 1.951 0.729
Traffic-d738 336 1.809 0.665 1.879 0.720 1.815 0.645 1.846 0.705
720 1.698 0.639 1.732 0.672 1.742 0.646 1.711 0.691
Avg. 1.814 0.669 1.865 0.720 1.836 0.665 1.857 0.716
of 7.0% compared to FredFormer, 17.5% compared to WPMixer,
and12.9%comparedtoFITS.IntermsofMAE,FIREimprovesby
about3.5%,7.7%,and5.5%overFredFormer,WPMixer,andFITS,
respectively.OnthemorestableTraffic_d738dataset,FIREobtains
thebestaverageMSE(1.814),improvingby2.3%,1.2%,and2.1%
overFredFormer,WPMixer,andFITS,respectively.RegardingMAE,
FIREoutperformsFredFormerandFITSby7.1%and6.5%,respec-
tively,whileWPMixerachievesaslightlybetterMAE(0.665)than
FIRE(0.669)byabout0.6%.TheseresultsdemonstrateFIRE’ssupe-
rioradaptabilityandrobustnessinhandlingdynamictimeseries
forecastingscenarios.
4.6 ScalabilityAnalysis
ToinvestigatethescalabilityofFIRE,wetrainthemodelwithin-
creasingsizefromboththedepth(numberoflayers)andwidth(em-
beddingdimension)perspectives.Forecastingexperimentsarecon-
ductedontwodatasets:WeatherandElectricity.Figure3presents
theaverageforecastingresults,measuredbyMeanSquaredError
(MSE),onbothdatasetsforvariousforecastinghorizons,including
𝑇 ∈{96,192,336,720}timesteps,usingdifferentnumbersoflayers
andembeddingdimensions.
Theresultsdemonstratethat,unliketimeseriesfoundationmod-
els[6,11,22,34,42],timeseriesforecastingmodelsaretypically
trainedondomain-specificdatasetswithlimiteddatavolume.As
showninFigure3,increasingmodelcapacity—eitherbyenlarging
thehiddendimensionorstackingmorelayers—yieldsdiminishing
returnsafteracertainpoint.Specifically,boththemodeldimension
andlayeranalysisplotsindicatethatMSEsaturatesasthemodel
sizeincreases,andmayevenslightlyworsenduetooverfitting.This
phenomenonsuggeststhat,fortimeseriesforecastingtaskswith
constraineddata,thescalabilityofmodelsisfundamentallylimited.
Oncethemodelcapacitymatchestherepresentationalneedsofthe
data,furtherscalingdoesnotimproveperformance.Thisisinsharp
contrasttoFoundationModels,wherescalingupwithabundant
dataoftenleadstocontinuousperformancegains.
4.7 Hyper-parameterAnalysis
Patch length is a crucial hyper-parameter for FIRE. We eval-
uate the model’s sensitivity to different patch lengths on the
WeatherandElectricitydatasets,forecastingfuturetimepoints
𝑇 ∈{96,192,336,720}.Table6reportstheforecastingresultsmea-
suredbyMSEandMAE.FortheWeatherdataset,thebestoverall
performanceisachievedwithapatchlengthof16,yieldinganaver-
ESM
Weather 0.26
Electricity
0.24
0.22
0.20
0.18
1 3 6 9
Num_layers
(a)Modeldimensionanalysis
ESM
Weather
Electricity
(b)Modellayeranalysis
Figure3:Modelscalabilityanalysis
Table6:Forecastingresultsofvariouspatchlengths
PatchLen 4 8 16 32 48
Dataset T MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
96 0.163 0.205 0.163 0.204 0.162 0.203 0.163 0.202 0.163 0.204
192 0.210 0.248 0.210 0.249 0.208 0.246 0.209 0.249 0.209 0.246
Weather 336 0.266 0.288 0.267 0.290 0.266 0.290 0.268 0.289 0.268 0.292
720 0.343 0.342 0.343 0.340 0.342 0.339 0.346 0.342 0.344 0.341
Avg. 0.246 0.271 0.246 0.271 0.245 0.270 0.247 0.271 0.246 0.271
96 0.154 0.243 0.152 0.240 0.149 0.237 0.149 0.236 0.148 0.235
192 0.165 0.253 0.163 0.250 0.162 0.249 0.161 0.249 0.161 0.248
Elc 336 0.180 0.270 0.177 0.267 0.177 0.267 0.176 0.265 0.178 0.268
720 0.223 0.306 0.217 0.301 0.214 0.298 0.213 0.298 0.216 0.299
Avg. 0.181 0.268 0.177 0.265 0.176 0.263 0.175 0.262 0.176 0.263
ageMSEof0.245andMAEof0.270.FortheElectricitydataset,the
optimalpatchlengthis32,withanaverageMSEof0.175andMAE
of0.262.Notably,thedifferencesinperformanceacrossvarious
patchlengthsaremarginal.Forinstance,onWeather,theworst
averageMSE(0.246atpatchlength4)isonly0.001higherthan
the best (0.245 at patch length 16). Similarly, on Electricity, the
averageMSEvarieswithin0.006acrossalltestedpatchlengths.
ThisdemonstratesthatFIREexhibitsstrongrobustnessandlow
sensitivitytopatchlengthselection,consistentwiththescalability
analysisdiscussedearlier.
5 RelatedWork
Timeseriesforecastingandtemporalmodels.Timeseriesfore-
castingpresentsuniquechallenges,especiallyinmodelinglong-
termdependenciesandcomplextemporaldynamics.Transformer-
basedarchitectures[31]haverecentlyadvancedthefieldbyleverag-
ingself-attentiontocaptureglobaltemporalrelationships,outper-
formingtraditionalRNNsandCNNs[2,5,9,16]thatoftenstruggle
withscalabilityandlong-rangemodeling.Notableadvancements
includeInformer[43],whichintroducesProbSparseattentionfor
efficienthandlingoflongsequences,andAutoformer[36],which
decomposestimeseriesintotrendandseasonalcomponentsto
improveinterpretabilityandforecastingaccuracy.PatchTST[25]
restructuresinputsequencesintopatchesforparallelprocessing
inlong-termprediction.Pyraformer[20]andTimesNet[35]ex-
plorehierarchicalandmulti-scalerepresentationstofurtherrefine
temporalmodeling.
Frequency-domainapproaches.Despitevariousadvancements,
time-domainmodelsstillfallshortincapturingperiodicityandspec-
tralpatternsinherentinmanyreal-worldtimeseries.Frequency-
domainapproachesfillthisvoidbyleveragingFourierandwavelet
transformstoextractglobalandperiodicfeatures.Fredformer[27]
employsfrequencychannel-wiseattentiontoselectivelyfocuson
informativespectralcomponents,whileFreTS[41]modelsdepen-
denciesacrossfrequencychannelsandtemporaldimensionsusing
MLPs. FITS [38] employs complex-valued layers for expressive
8

---

# Page 9

AUnifiedFrequencyDomainDecompositionFrameworkforInterpretableandRobustTimeSeriesForecasting Conference’17,July2017,Washington,DC,USA
frequency-domaintransformations,andWPMixer[24]integrates [4] DihiaBoulegane,VitorCerquiera,andAlbertBifet.2022.AdaptiveModelCom-
waveletdecompositionwithMLPstocapturebothlocalizedand pressionofEnsemblesforEvolvingDataStreamsForecasting.In2022Interna-
long-termpatterns.Thesemodelshavedemonstratedcompetitive
tionalJointConferenceonNeuralNetworks(IJCNN).1–8.doi:10.1109/IJCNN55064.
2022.9892811
orsuperiorperformancecomparedtopurelytemporalapproaches. [5] JiezhuCheng,KaizhuHuang,andZibinZheng.2020.TowardsBetterForecasting
Hybridtemporal-frequencymodels.Recentstudieshaveex- byFusingNearandDistantFutureVisions.InTheThirty-FourthAAAIConference
onArtificialIntelligence,AAAI2020,TheThirty-SecondInnovativeApplications
ploredhybridapproachesthatcombinetemporalandfrequency-
ofArtificialIntelligenceConference,IAAI2020,TheTenthAAAISymposiumon
domaininformation.CDX-Net[18]integratesCNNs,RNNs,and EducationalAdvancesinArtificialIntelligence,EAAI2020,NewYork,NY,USA,
attention mechanisms to extract and fuse multivariate features February7-12,2020.AAAIPress,3593–3600.
[6] AbhimanyuDas,WeihaoKong,RajatSen,andYichenZhou.2024.Adecoder-
from both domains. FEDformer [45] unifies trend-seasonal de- onlyfoundationmodelfortime-seriesforecasting.InForty-firstInternational
compositionwithFourieranalysiswithinaTransformerframe- ConferenceonMachineLearning,ICML2024,Vienna,Austria,July21-27,2024.
OpenReview.net. https://openreview.net/forum?id=jn2iTJas6h
work,enablingrobustrepresentationofmultivariatetimeseries.
[7] WenjieDu,DavidCôté,andYanLiu.2023.SAITS:Self-attention-basedimputation
TimeMixer++[32]generatesmulti-scaleseriesviatemporaldown- fortimeseries.ExpertSyst.Appl.219(2023),119619.doi:10.1016/J.ESWA.2023.
sampling,appliesFFT-basedperiodicanalysis,andemploysatten- 119619
[8] M.DurairajandB.H.KrishnaMohan.2022. Aconvolutionalneuralnetwork
tionmechanismstolearnrobustrepresentationsofseasonaland basedapproachtofinancialtimeseriesprediction.NeuralComput.Appl.34,16
trendcomponents. (2022),13319–13337.doi:10.1007/S00521-022-07143-2
Limitationsofexistingapproaches.Mostfrequency-domain [9] V
Fo
a
r
le
e
n
c
t
a
i
s
n
ti
F
n
l
g
un
w
k
i
e
t
r
h
t,
A
D
u
a
t
v
o
id
re
S
g
a
r
l
e
i
s
n
s
a
i
s
v
,
e
an
R
d
ec
J
u
an
rre
G
n
a
t
st
N
ha
e
u
tw
s.
o
2
r
0
k
1
s
7
.
.D
Co
e
R
ep
R
A
a
R
b
:
s
P
/1
ro
7
b
0
a
4
b
.0
il
4
i
1
st
1
i
0
c
andhybridmodels,however,operateasblack-boxpredictors,op- (2017).arXiv:1704.04110
timizedprimarilyforaccuracywithlimitedinterpretability.Also, [10] JoãoGama,Indre˙Žliobaite˙,AlbertBifet,MykolaPechenizkiy,andAbdelhamid
theyrarelyaddresspracticalchallenges,suchasconceptdriftand
Bouchachia.2014.Asurveyonconceptdriftadaptation.ACMcomputingsurveys
(CSUR)46,4(2014),1–37.
basisevolution,whichunderminetheirrobustnessindynamicen- [11] MononitoGoswami,KonradSzafer,ArjunChoudhry,YifuCai,ShuoLi,andArtur
vironmentswheredistributionalshiftsarecommon. Dubrawski.2024.MOMENT:AFamilyofOpenTime-seriesFoundationModels.
InForty-firstInternationalConferenceonMachineLearning,ICML2024,Vienna,
Austria,July21-27,2024.OpenReview.net. https://openreview.net/forum?id=
6 Conclusion FVvf69a5rx
[12] NuwanGunasekara,BernhardPfahringer,HeitorMuriloGomes,AlbertBifet,
WeusethediscreteFouriertransformtounifytheformulationof andYunSingKoh.2024.Recurrentconceptdriftsondatastreams.International
varioustypesoftimeseries.WeproposeFIRE,anewforecasting JointConferencesonArtificialIntelligenceOrganization.
[13] GajendraSinghGurjarandShardaChhabria.2015.Areviewonconceptevolution
frameworkthatworksinthefrequencydomainthroughbasisde- techniqueondatastream.In2015InternationalConferenceonPervasiveComputing
composition.ThisallowsFIREtocapturericher,multi-dimensional (ICPC).1–3.doi:10.1109/PERVASIVE.2015.7087172
[14] AhsanulHaque,LatifurKhan,MichaelBaron,BhavaniThuraisingham,andCharu
featuresoftemporaldata.Akeystrengthof FIREisitsexplicit
Aggarwal.2016.Efficienthandlingofconceptdriftandconceptevolutionover
andseparatemodelingofamplitudeandphaseforhandlingkey StreamData.In2016IEEE32ndInternationalConferenceonDataEngineering
challengesintimeseriesforecasting,namelyconceptdriftandbasis (ICDE).481–492.doi:10.1109/ICDE.2016.7498264
evolution.FIREcombinesrigorousmathematicalideaswithpracti-
[15] PeterJ.Huber.1981.RobustStatistics.Wiley. doi:10.1002/0471725250
[16] GuokunLai,Wei-ChengChang,YimingYang,andHanxiaoLiu.2018. Mod-
calcomponents,includinglineartransformations,causalattention, elingLong-andShort-TermTemporalPatternswithDeepNeuralNetworks.
andacompositelossfunction,soastoadaptdynamicallyandro- InThe41stInternationalACMSIGIRConferenceonResearch&Developmentin
InformationRetrieval,SIGIR2018,AnnArbor,MI,USA,July08-12,2018,Kevyn
bustlytochangingtemporalpatterns,evenwhendataarenoisy Collins-Thompson,QiaozhuMei,BrianD.Davison,YiqunLiu,andEmineYilmaz
orsparse.Ourexperimentsondiversereal-worlddatasetsshow (Eds.).ACM,95–104.
[17] Chun-NaLi,YiweiSong,andYuan-HaiShao.2025. DomainAdaptationvia
thatFIREconsistentlyachievesbetteraccuracy,improvedinter-
LearningUsingStatisticalInvariant.IEEETrans.Knowl.DataEng.37,7(2025),
pretability,andstrongrobustness.Itperformsespeciallywellunder 4023–4034.doi:10.1109/TKDE.2025.3565780
severeconceptdriftandbasisevolution,provingitseffectiveness [18] JiajiaLi,LingDai,FengTan,HuiShen,ZikaiWang,BinSheng,andPengwei
Hu.2022.CDX-NET:Cross-DomainMulti-FeatureFusionModelingViaDeep
indynamicscenarios.
NeuralNetworksforMultivariateTimeSeriesForecastinginAIOps.InIEEE
Forfuturework,weplantostrengthentheintegrationofmathe- InternationalConferenceonAcoustics,SpeechandSignalProcessing,ICASSP2022,
maticaltheorywithaninterpretablemodeldesignfortimeseries VirtualandSingapore,23-27May2022.IEEE,4073–4077.doi:10.1109/ICASSP43922.
2022.9746242
forecasting, move beyond trial-and-error methods, and develop [19] JiajiaLi,FengTan,ChengHe,ZikaiWang,HaitaoSong,LingfeiWu,andPengwei
moreprincipledandtransparentforecastingtechniques,soasto Hu.2022.HigeNet:AHighlyEfficientModelingforLongSequenceTimeSeries
tackleincreasinglycomplextemporaldata.
PredictioninAIOps.CoRRabs/2211.07642(2022).arXiv:2211.07642doi:10.48550/
ARXIV.2211.07642
[20] ShizhanLiu,HangYu,CongLiao,JianguoLi,WeiyaoLin,AlexX.Liu,and
SchahramDustdar.2022.Pyraformer:Low-ComplexityPyramidalAttentionfor
References
Long-RangeTimeSeriesModelingandForecasting.InTheTenthInternational
[1] KonstandinosAiwansedo,JérômeBosche,WafaBadreddine,MohamedHamza ConferenceonLearningRepresentations,ICLR2022,VirtualEvent,April25-29,2022.
Kermia,andOussamaDjadane.2024. CNN-N-BEATS:NovelHybridModel OpenReview.net. https://openreview.net/forum?id=0EXmFzUn5I
forTime-SeriesForecasting.InDeepLearningTheoryandApplications-5th [21] YongLiu,TenggeHu,HaoranZhang,HaixuWu,ShiyuWang,LintaoMa,and
InternationalConference,DeLTA2024,Dijon,France,July10-11,2024,Proceedings, MingshengLong.2024.iTransformer:InvertedTransformersAreEffectivefor
PartI(CommunicationsinComputerandInformationScience,Vol.2171),Ana TimeSeriesForecasting.InTheTwelfthInternationalConferenceonLearning
Fred,AllelHadjali,OlegGusikhin,andCarloSansone(Eds.).Springer,38–57. Representations,ICLR2024,Vienna,Austria,May7-11,2024.OpenReview.net.
doi:10.1007/978-3-031-66694-0_3 https://openreview.net/forum?id=JePfAI8fah
[2] ShaojieBai,J.ZicoKolter,andVladlenKoltun.2018.AnEmpiricalEvaluationof [22] YongLiu,HaoranZhang,ChenyuLi,XiangdongHuang,JianminWang,and
GenericConvolutionalandRecurrentNetworksforSequenceModeling.CoRR MingshengLong.2024.Timer:GenerativePre-trainedTransformersAreLarge
abs/1803.01271(2018).arXiv:1803.01271 TimeSeriesModels.InForty-firstInternationalConferenceonMachineLearning,
[3] AlbertBifetandRicardGavaldà.2007.LearningfromTime-ChangingDatawith ICML2024,Vienna,Austria,July21-27,2024.OpenReview.net. https://openreview.
AdaptiveWindowing.InProceedingsoftheSeventhSIAMInternationalConference net/forum?id=bYRYb7DMNo
onDataMining,April26-28,2007,Minneapolis,Minnesota,USA.SIAM,443–448. [23] MohammadM.Masud,QingChen,LatifurKhan,CharuC.Aggarwal,JingGao,
doi:10.1137/1.9781611972771.42
9

---

# Page 10

Conference’17,July2017,Washington,DC,USA ChengHe,XijieLiang,ZengrongZheng,PatrickP.C.Lee,XuHuang,ZhaoyiLi,HongXie,DefuLian,andEnhongChen
JiaweiHan,andBhavaniThuraisingham.2010.AddressingConcept-Evolution cc/paper/2021/hash/bcc0d400288793e8bdcd7c19a8ac0c2b-Abstract.html
inConcept-DriftingDataStreams.InICDM2010,The10thIEEEInternational [37] JiehuiXu,HaixuWu,JianminWang,andMingshengLong.2022. Anomaly
ConferenceonDataMining,Sydney,Australia,14-17December2010,GeoffreyI. Transformer:TimeSeriesAnomalyDetectionwithAssociationDiscrepancy.In
Webb,BingLiu,ChengqiZhang,DimitriosGunopulos,andXindongWu(Eds.). TheTenthInternationalConferenceonLearningRepresentations,ICLR2022,Virtual
IEEEComputerSociety,929–934.doi:10.1109/ICDM.2010.160 Event,April25-29,2022.OpenReview.net. https://openreview.net/forum?id=
[24] MdMahmuddunNabiMurad,MehmetAktukmak,andYasinYilmaz.2025.WP- LzQQ89U1qm_
Mixer:EfficientMulti-ResolutionMixingforLong-TermTimeSeriesForecasting. [38] ZhijianXu,AilingZeng,andQiangXu.2024.FITS:ModelingTimeSerieswith10k
InAAAI-25,SponsoredbytheAssociationfortheAdvancementofArtificialIntelli- Parameters.InTheTwelfthInternationalConferenceonLearningRepresentations,
gence,February25-March4,2025,Philadelphia,PA,USA,TobyWalsh,JulieShah, ICLR2024,Vienna,Austria,May7-11,2024.OpenReview.net. https://openreview.
andZicoKolter(Eds.).AAAIPress,19581–19588.doi:10.1609/AAAI.V39I18.34156 net/forum?id=bWcnvZ3qMb
[25] YuqiNie,NamH.Nguyen,PhanwadeeSinthong,andJayantKalagnanam.2023. [39] NingXue,IsaacTriguero,GrazzielaP.Figueredo,andDarioLanda-Silva.2019.
ATimeSeriesisWorth64Words:Long-termForecastingwithTransformers. EvolvingDeepCNN-LSTMsforInventoryTimeSeriesPrediction.InIEEECon-
InTheEleventhInternationalConferenceonLearningRepresentations,ICLR2023, gressonEvolutionaryComputation,CEC2019,Wellington,NewZealand,June
Kigali,Rwanda,May1-5,2023.OpenReview.net. https://openreview.net/forum? 10-13,2019.IEEE,1517–1524.doi:10.1109/CEC.2019.8789957
id=Jbdc0vTOcol [40] YiyuanYang,ChaoliZhang,TianZhou,QingsongWen,andLiangSun.2023.
[26] AdamPaszke,SamGross,FranciscoMassa,AdamLerer,JamesBradbury,Gre- DCdetector:DualAttentionContrastiveRepresentationLearningforTimeSe-
goryChanan,TrevorKilleen,ZemingLin,NataliaGimelshein,LucaAntiga, riesAnomalyDetection.InProceedingsofthe29thACMSIGKDDConferenceon
AlbanDesmaison,AndreasKöpf,EdwardZ.Yang,ZacharyDeVito,MartinRai- KnowledgeDiscoveryandDataMining,KDD2023,LongBeach,CA,USA,August
son,AlykhanTejani,SasankChilamkurthy,BenoitSteiner,LuFang,JunjieBai, 6-10,2023,AmbujK.Singh,YizhouSun,LemanAkoglu,DimitriosGunopulos,
andSoumithChintala.2019.PyTorch:AnImperativeStyle,High-Performance XifengYan,RaviKumar,FatmaOzcan,andJiepingYe(Eds.).ACM,3033–3045.
DeepLearningLibrary.InAdvancesinNeuralInformationProcessingSystems doi:10.1145/3580305.3599295
32:AnnualConferenceonNeuralInformationProcessingSystems2019,NeurIPS [41] KunYi,QiZhang,WeiFan,ShoujinWang,PengyangWang,HuiHe,NingAn,
2019,December8-14,2019,Vancouver,BC,Canada,HannaM.Wallach,Hugo DefuLian,LongbingCao,andZhendongNiu.2023.Frequency-domainMLPs
Larochelle,AlinaBeygelzimer,Florenced’Alché-Buc,EmilyB.Fox,andRoman areMoreEffectiveLearnersinTimeSeriesForecasting.InAdvancesinNeural
Garnett(Eds.).8024–8035. https://proceedings.neurips.cc/paper/2019/hash/ InformationProcessingSystems36:AnnualConferenceonNeuralInformation
bdbca288fee7f92f2bfa9f7012727740-Abstract.html ProcessingSystems2023,NeurIPS2023,NewOrleans,LA,USA,December10-16,
[27] XihaoPiao,ZhengChen,TaichiMurayama,YasukoMatsubara,andYasushi 2023,AliceOh,TristanNaumann,AmirGloberson,KateSaenko,MoritzHardt,
Sakurai.2024. Fredformer:FrequencyDebiasedTransformerforTimeSeries andSergeyLevine(Eds.). http://papers.nips.cc/paper_files/paper/2023/hash/
Forecasting.InProceedingsofthe30thACMSIGKDDConferenceonKnowledge f1d16af76939f476b5f040fd1398c0a3-Abstract-Conference.html
DiscoveryandDataMining,KDD2024,Barcelona,Spain,August25-29,2024, [42] YunhaoZhang,MinghaoLiu,ShengyangZhou,andJunchiYan.2024.UP2ME:
RicardoBaeza-YatesandFrancescoBonchi(Eds.).ACM,2400–2410.doi:10.1145/ UnivariatePre-trainingtoMultivariateFine-tuningasaGeneral-purposeFrame-
3637528.3671928 workforMultivariateTimeSeriesAnalysis.InForty-firstInternationalConference
[28] JunhoSong,KeonwooKim,JeonglyulOh,andSungzoonCho.2023.MEMTO: onMachineLearning,ICML2024,Vienna,Austria,July21-27,2024.OpenRe-
Memory-guidedTransformerforMultivariateTimeSeriesAnomalyDetection. view.net. https://openreview.net/forum?id=aR3uxWlZhX
InAdvancesinNeuralInformationProcessingSystems36:AnnualConferenceon [43] HaoyiZhou,ShanghangZhang,JieqiPeng,ShuaiZhang,JianxinLi,HuiXiong,
NeuralInformationProcessingSystems2023,NeurIPS2023,NewOrleans,LA,USA, andWancaiZhang.2021. Informer:BeyondEfficientTransformerforLong
December10-16,2023,AliceOh,TristanNaumann,AmirGloberson,KateSaenko, SequenceTime-SeriesForecasting.InThirty-FifthAAAIConferenceonArtificial
MoritzHardt,andSergeyLevine(Eds.). http://papers.nips.cc/paper_files/paper/ Intelligence,AAAI2021,Thirty-ThirdConferenceonInnovativeApplicationsof
2023/hash/b4c898eb1fb556b8d871fbe9ead92256-Abstract-Conference.html ArtificialIntelligence,IAAI2021,TheEleventhSymposiumonEducationalAdvances
[29] AlexeyTsymbal.2004.Theproblemofconceptdrift:definitionsandrelatedwork. inArtificialIntelligence,EAAI2021,VirtualEvent,February2-9,2021.AAAIPress,
ComputerScienceDepartment,TrinityCollegeDublin106,2(2004),58. 11106–11115.doi:10.1609/AAAI.V35I12.17325
[30] VladimirVapnikandRaufIzmailov.2020.Completestatisticaltheoryoflearning: [44] PengZhou,YufengGuo,HaoranYu,YuantingYan,YanpingZhang,andXindong
learningusingstatisticalinvariants.InConformalandProbabilisticPrediction Wu.2024.ConceptEvolutionDetectingoverFeatureStreams.ACMTransactions
andApplications,COPA2020,9-11September2020,VirtualEvent(Proceedingsof onKnowledgeDiscoveryfromData18,8(2024),1–32.
MachineLearningResearch,Vol.128),AlexanderGammerman,VladimirVovk, [45] TianZhou,ZiqingMa,QingsongWen,XueWang,LiangSun,andRongJin.2022.
ZhiyuanLuo,EvgueniN.Smirnov,GiovanniCherubin,andMarcoChristini FEDformer:FrequencyEnhancedDecomposedTransformerforLong-termSeries
(Eds.).PMLR,4–40. http://proceedings.mlr.press/v128/vapnik20a.html Forecasting.InInternationalConferenceonMachineLearning,ICML2022,17-23
[31] AshishVaswani,NoamShazeer,NikiParmar,JakobUszkoreit,LlionJones, July2022,Baltimore,Maryland,USA(ProceedingsofMachineLearningResearch,
AidanN.Gomez,LukaszKaiser,andIlliaPolosukhin.2017.AttentionisAllyou Vol.162),KamalikaChaudhuri,StefanieJegelka,LeSong,CsabaSzepesvári,Gang
Need.InAdvancesinNeuralInformationProcessingSystems30:AnnualConference Niu,andSivanSabato(Eds.).PMLR,27268–27286. https://proceedings.mlr.press/
onNeuralInformationProcessingSystems2017,December4-9,2017,LongBeach, v162/zhou22g.html
CA,USA,IsabelleGuyon,UlrikevonLuxburg,SamyBengio,HannaM.Wallach,
RobFergus,S.V.N.Vishwanathan,andRomanGarnett(Eds.).5998–6008.
[32] ShiyuWang,JiaweiLi,XiaomingShi,ZhouYe,BaichuanMo,WenzeLin,Sheng-
tongJu,ZhixuanChu,andMingJin.2024.TimeMixer++:AGeneralTimeSeries
PatternMachineforUniversalPredictiveAnalysis.CoRRabs/2410.16032(2024).
arXiv:2410.16032doi:10.48550/ARXIV.2410.16032
[33] ShiyuWang,HaixuWu,XiaomingShi,TenggeHu,HuakunLuo,LintaoMa,
JamesY.Zhang,andJunZhou.2024. TimeMixer:DecomposableMultiscale
MixingforTimeSeriesForecasting.InTheTwelfthInternationalConferenceon
LearningRepresentations,ICLR2024,Vienna,Austria,May7-11,2024.OpenRe-
view.net. https://openreview.net/forum?id=7oLshfEIC2
[34] GeraldWoo,ChenghaoLiu,AkshatKumar,CaimingXiong,SilvioSavarese,
andDoyenSahoo.2024.UnifiedTrainingofUniversalTimeSeriesForecasting
Transformers.InForty-firstInternationalConferenceonMachineLearning,ICML
2024,Vienna,Austria,July21-27,2024.OpenReview.net. https://openreview.net/
forum?id=Yd8eHMY1wz
[35] HaixuWu,TenggeHu,YongLiu,HangZhou,JianminWang,andMingsheng
Long.2023.TimesNet:Temporal2D-VariationModelingforGeneralTimeSeries
Analysis.InTheEleventhInternationalConferenceonLearningRepresentations,
ICLR2023,Kigali,Rwanda,May1-5,2023.OpenReview.net. https://openreview.
net/forum?id=ju_Uqw384Oq
[36] HaixuWu,JiehuiXu,JianminWang,andMingshengLong.2021.Autoformer:De-
compositionTransformerswithAuto-CorrelationforLong-TermSeriesForecast-
ing.InAdvancesinNeuralInformationProcessingSystems34:AnnualConference
onNeuralInformationProcessingSystems2021,NeurIPS2021,December6-14,2021,
virtual,Marc’AurelioRanzato,AlinaBeygelzimer,YannN.Dauphin,PercyLiang,
andJenniferWortmanVaughan(Eds.).22419–22430. https://proceedings.neurips.
10

---

# Page 11

AUnifiedFrequencyDomainDecompositionFrameworkforInterpretableandRobustTimeSeriesForecasting Conference’17,July2017,Washington,DC,USA
A ComparisonBetweenFFTandWavelet Table7:Fullresultsofmoduleablation
Transform
model FIRE FIRE_adv. FIRE_base
Both the Fast Fourier Transform (FFT) and Wavelet Transform
arefundamentaltoolsfordecomposingtimeseriesdatafromthe dataset T MSE MAE MSE MAE MSE MAE
timedomainintothefrequencydomain,enablinglosslessforward 96 0.365 0.390 0.369 0.391 0.373 0.391
andinversetransformations.Despitethissharedcapability,they 192 0.420 0.418 0.425 0.425 0.422 0.421
ETTh1 336 0.458 0.437 0.459 0.438 0.466 0.438
differsignificantlyintheirunderlyingprinciplesandsuitability 720 0.456 0.454 0.470 0.467 0.474 0.459
for general-purpose time series forecasting. In this section, we Avg. 0.425 0.425 0.431 0.430 0.434 0.427
comparetheircharacteristicsandexplainwhyFFTisgenerallymore 96 0.282 0.333 0.280 0.331 0.281 0.333
appropriateformodelingdiversetimeseriesdatainforecasting 192 0.362 0.383 0.359 0.382 0.360 0.384
ETTh2 336 0.403 0.419 0.398 0.421 0.400 0.420
tasks. 720 0.408 0.433 0.412 0.433 0.409 0.433
• Parameter-free nature of FFT: FFT is a deterministic, Avg. 0.364 0.392 0.362 0.392 0.363 0.393
parameter-freetransformationthatdecomposesasignalinto 96 0.310 0.344 0.313 0.353 0.317 0.352
192 0.356 0.375 0.358 0.379 0.360 0.378
afixedsetoforthogonalfrequencybases.Theabsenceof ETTm1 336 0.385 0.397 0.386 0.399 0.383 0.397
hyperparameterseliminatestheneedfordomain-specific 720 0.448 0.431 0.444 0.434 0.443 0.433
knowledgeormanualtuningduringdecomposition,making Avg. 0.375 0.387 0.375 0.391 0.376 0.390
FFThighlysuitableformodelingdiversetimeseriesina 96 0.170 0.252 0.172 0.253 0.172 0.253
192 0.237 0.297 0.238 0.298 0.237 0.297
generalandautomatedmanner. ETTm2 336 0.299 0.338 0.300 0.338 0.296 0.334
• HyperparameterdependenceofWaveletTransform: 720 0.399 0.395 0.398 0.397 0.394 0.394
Incontrast,theWaveletTransformrequiresselectingspe- Avg. 0.276 0.321 0.277 0.322 0.275 0.320
cificwaveletfunctionsandscaleparameters,whichactas 96 0.162 0.204 0.164 0.206 0.165 0.208
hyperparameterscriticallyinfluencingthedecomposition 192 0.207 0.246 0.209 0.247 0.209 0.248
Weather 336 0.263 0.287 0.266 0.293 0.267 0.291
results.Carefultuningoftheseparameterscanenhancerep- 720 0.340 0.338 0.342 0.341 0.343 0.340
resentationoftimeseriesexhibitinglocalized,transient,or Avg. 0.243 0.269 0.245 0.272 0.246 0.272
non-stationarybehaviors.However,thisrelianceondomain 96 0.474 0.272 0.479 0.285 0.493 0.304
expertise and parameter selection limits its applicability 192 0.487 0.269 0.480 0.286 0.486 0.299
Traffic 336 0.484 0.275 0.490 0.281 0.507 0.306
inuniversalforecastingframeworksacrossheterogeneous 720 0.531 0.295 0.532 0.309 0.536 0.324
datasets. Avg. 0.494 0.278 0.495 0.290 0.506 0.308
Insummary,althoughbothFFTandWaveletTransformprovide 96 0.148 0.236 0.151 0.239 0.162 0.249
192 0.161 0.249 0.163 0.250 0.172 0.258
losslesstime-frequencyanalysis,FFT’sparameter-freeanduniver- Elc 336 0.176 0.265 0.179 0.267 0.189 0.275
salnaturemakesitmoresuitableforgeneral-purposetimeseries 720 0.215 0.299 0.217 0.301 0.232 0.310
forecasting.Conversely,theWaveletTransformisbettersuitedto Avg. 0.175 0.262 0.178 0.264 0.189 0.273
specializedscenarioswheredomainknowledgeguideshyperpa- Best_Count 27/35 30/35 6/35 3/35 3/35 2/35
rametertuningtoeffectivelycapturecomplexlocalizedfeatures.
codes.
B ExperimentalDetails
Summaryofkeyhyperparameters:
B.1 Implementationdetails • Inputlength(look-backwindow):96
Weuseafixedlook-backwindow(contextlength)of96timepoints • Forecasthorizons:𝑇 ∈{96,192,336,720}
to model the historical data and forecast future horizons𝑇 ∈ • Patchlength:8to48
{96,192,336,720}.Thepatchlengthisvariedbetween8and48 • Batchsize:32to256
tobalancethetrade-offbetweentemporalresolutionandcomputa- • Learningratestested:1×10−2,5×10−3,2×10−3,1×10−3,5×
tionalefficiency.Trainingisperformedusingmini-batchgradient
10−4,1×10−4
descentwithbatchsizesrangingfrom32to256.Largerbatchsizes • Optimizer:ADAM
improveparallelismandenablemoreefficientutilizationofGPU • Earlystopping:validationlossnoimprovementfor8con-
resources.WeadopttheADAMoptimizerformodeloptimization, secutiveepochs
tuningthelearningrateovertheset{1×10−2,5×10−3,2×10−3,1× • Hardware:NVIDIAA100GPUwith40GBmemory
10−3,5×10−4,1×10−4}toachievestableandefficientconvergence.
Earlystoppingisemployedbasedonthevalidationloss:ifthevali- B.2 Fullresults
dationlossdoesnotdecreasefor8consecutiveepochs,whichhelps Ablation results. To complement the average results reported
prevent overfitting and reduces unnecessary computation. The earlier,Table7presentsthefullforecastingperformanceformodule
modelisimplementedinPyTorchandtrainedonasingleNVIDIA ablation.FIREachievesthebestMSEin27outof35experiments
A100GPUwith40GBofmemory.EvaluationmetricsincludeMean andthebestMAEin30outof35.Incontrast,FIRE_advancedranks
SquaredError(MSE)andMeanAbsoluteError(MAE).Wecompare secondwithonly6and3bestresultsonMSEandMAE,respectively.
ourresultsagainstthebest-performingstate-of-the-artmodelsre- Theseresultsdemonstratethecriticalimportanceofmodelingboth
portedintheliteratureorreproducedfromtheirpublishedsource datadriftandbasisevolutionforimprovedforecastingaccuracy.
11

---

# Page 12

Conference’17,July2017,Washington,DC,USA ChengHe,XijieLiang,ZengrongZheng,PatrickP.C.Lee,XuHuang,ZhaoyiLi,HongXie,DefuLian,andEnhongChen
Table8:FullresultsofLossablation Table9:Forecastingresultsofvariouslookbackwindowsizes
Model \sysname \sysname_enh. \sysname_adv. \sysname_base Windowsize 96 192 288 384 512
Dataset MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
Data T MSE MAE MSE MAE MSE MAE MSE MAE 0.376 0.396 0.373 0.396 0.375 0.395 0.376 0.398 0.382 0.405
0.433 0.466 0.425 0.422 0.417 0.418 0.418 0.423 0.406 0.421
96 0.365 0.390 0.369 0.391 0.385 0.401 0.381 0.400 ETTh1 0 0 . . 4 4 6 8 6 0 0 0 . . 4 4 4 7 2 0 0 0 . . 4 5 4 0 9 9 0 0 . . 4 4 3 8 3 9 0 0 . . 4 5 4 4 0 0 0 0 . . 4 5 3 1 4 0 0 0 . . 4 42 3 9 3 0 0 . . 4 4 3 5 1 8 0 0 . . 4 44 2 0 7 0 0 . . 4 4 4 6 2 3
192 0.420 0.418 0.423 0.420 0.432 0.434 0.426 0.429 Avg. 0.439 0.444 0.439 0.435 0.443 0.439 0.414 0.427 0.414 0.433
ETTh1 336 0.458 0.437 0.462 0.438 0.465 0.447 0.458 0.441 0 0 . . 1 2 6 0 2 9 0 0 . . 2 2 0 4 4 7 0 0 . . 1 1 5 9 4 8 0 0 . . 1 2 9 3 5 7 0 0 . . 1 1 4 9 7 4 0 0 . . 1 2 9 3 4 9 0 0 . . 1 1 5 9 0 5 0 0 . . 1 2 9 4 5 1 0 0 . . 1 1 4 9 6 0 0 0 . . 1 2 9 3 2 6
720 0.456 0.454 0.461 0.459 0.474 0.467 0.468 0.464 Weather 0.267 0.289 0.252 0.282 0.251 0.281 0.246 0.281 0.248 0.283
0.343 0.339 0.330 0.335 0.322 0.332 0.317 0.331 0.312 0.333
Avg. 0.424 0.424 0.428 0.427 0.439 0.437 0.433 0.433 Avg. 0.245 0.270 0.233 0.262 0.229 0.261 0.227 0.262 0.224 0.261
96 0.282 0.333 0.281 0.333 0.300 0.348 0.283 0.332
192 0.362 0.383 0.360 0.382 0.382 0.397 0.360 0.384
ETTh2 336 0.403 0.419 0.403 0.418 0.425 0.432 0.406 0.425 0.44
720 0.408 0.433 0.411 0.433 0.434 0.448 0.420 0.438
Avg. 0.363 0.392 0.363 0.391 0.385 0.406 0.367 0.394 0.43
96 0.310 0.344 0.312 0.349 0.325 0.368 0.316 0.357 0.42
192 0.356 0.375 0.359 0.376 0.369 0.390 0.360 0.380
ETTm1 336 0.385 0.397 0.383 0.395 0.390 0.407 0.389 0.403 96 Loo 1 k 9 - 2 back 2 8 w 8 indo 3 w 8 4 length 512
720 0.448 0.431 0.442 0.430 0.453 0.442 0.448 0.441
Avg. 0.374 0.386 0.374 0.387 0.384 0.401 0.378 0.395
96 0.170 0.252 0.170 0.250 0.192 0.283 0.177 0.262
192 0.237 0.297 0.238 0.297 0.254 0.317 0.242 0.303
ETTm2 336 0.299 0.338 0.300 0.337 0.319 0.358 0.305 0.344
720 0.399 0.395 0.399 0.394 0.419 0.416 0.404 0.401
Avg. 0.276 0.320 0.277 0.319 0.296 0.343 0.282 0.327
96 0.162 0.204 0.160 0.202 0.163 0.207 0.162 0.205
192 0.207 0.246 0.206 0.244 0.208 0.249 0.207 0.247
Weather 336 0.263 0.287 0.264 0.287 0.264 0.288 0.267 0.291
720 0.340 0.338 0.342 0.338 0.344 0.34 0.344 0.339
Avg. 0.243 0.268 0.243 0.267 0.2448 0.2710 0.2450 0.2705
96 0.474 0.272 0.466 0.284 0.481 0.270 0.481 0.278
192 0.487 0.269 0.475 0.287 0.499 0.282 0.492 0.283
Traffic 336 0.484 0.275 0.482 0.278 0.509 0.289 0.516 0.293
720 0.531 0.295 0.527 0.297 0.547 0.307 0.552 0.306
Avg. 0.494 0.277 0.487 0.286 0.509 0.287 0.510 0.290
96 0.148 0.236 0.149 0.238 0.153 0.244 0.154 0.243
192 0.161 0.249 0.160 0.248 0.167 0.256 0.166 0.256
Elc 336 0.176 0.265 0.176 0.266 0.181 0.273 0.182 0.274
720 0.215 0.299 0.214 0.299 0.222 0.308 0.225 0.309
Avg. 0.175 0.262 0.174 0.262 0.180 0.270 0.181 0.270
Best 20/35 22/35 15/35 13/35 0 0 0 0
Additionally,Table8presentsthefullresultsoflossfunction
ablationsacrosssevendatasets.Ourfullmodel,FIRE,achievesthe
bestMSEandMAEin20and22outofallexperiments,respectively,
outperformingallvariants.Thesystematicperformancedegrada-
tionobservedwhenremovingeachlosscomponentconfirmsthe
essentialcontributionofeverylosstermtotheoverallforecasting
accuracy.Thisablationstudyvalidatesthedesignofthecomposite
lossinenhancingmodeleffectiveness.
Modelsensitivitytolook-backwindowlength.Weevaluate
theimpactofvaryinglook-backwindowsizes{96,192,288,384,512}
onforecastingperformanceusingETTh1andWeatherdatasets,
withotherhyper-parametersfixed.AsshowninTable9andFigure
4,forETTh1,increasingthewindowsizefrom96to384consis-
tentlyreducestheaverageMSEfrom0.439to0.414andMAEfrom
eulav
cirteM
0.26
0.24
Avg MSE
Avg MAE
96 192 288 384 512 Look-back window length
(a)ETTh1
eulav
cirteM Avg MSE Avg MAE
(b)Weather
Figure4:AverageforecastingresultsonETTh1andWeather
datasetswithvariouslookbackwindowlengths.
0.444to0.427,indicatingimprovedaccuracyduetomorehistori-
calinformation.However,furtherincreasingthewindowto512
leadstoaslightincreaseinMSE(0.439)andMAE(0.433),suggest-
ingdiminishingreturnsorpotentialnoiseintroduction.Similarly,
ontheWeatherdataset,averageMSEandMAEdecreasesteadily
from0.245and0.270atwindow96to0.224and0.261atwindow
512,showingconsistentgainswithlongerlook-backwindows.The
improvementsarelesspronouncedbeyondwindowsize384,indi-
catingperformancesaturation.
Overall,theseresultsdemonstratethatenlargingthelook-back
windowgenerallyenhancesforecastingaccuracybyleveraging
moretemporalcontext,butbeyondacertainlength,thebenefits
plateauorslightlydecline,likelyduetonoiseaccumulationand
redundancyintheinputdata.
12