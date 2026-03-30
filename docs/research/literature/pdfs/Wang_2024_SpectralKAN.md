# Wang_2024_SpectralKAN

SpectralKAN: Weighted Activation Distribution
Kolmogorov-Arnold Network for Hyperspectral Image
Change Detection
YanhengWanga,XiaohanYub,YongshengGaoc,∗,JianjunShad,JianWange,Shiyong
Yana,KaiQina,YonggangZhangd andLianruGaof
aSchoolofEnvironmentandSpatialInformatics,ChinaUniversityofMiningandTechnology,Xuzhou
221116,China
bSchoolofComputing,MacquarieUniversity,Sydney,NSW2109,Australia
cSchoolofEngineeringandBuiltEnvironment,GriffithUniversity,Nathan,QLD4111,Australia
dCollegeofIntelligentSystemsScienceandEngineering,HarbinEngineeringUniversity,Harbin150001,
China
eSchoolofIntelligencePolicing,ChinaPeople’sPoliceUniversity,Langfang,065000,China
fKeyLaboratoryofComputationalOpticalImagingTechnology,AerospaceInformationResearchInstitute,
ChineseAcademyofSciences,Beijing100094,China
Abstract
Kolmogorov-Arnold networks (KANs) represent data features by learning the activa-
tionfunctionsanddemonstratesuperioraccuracywithfewerparameters,FLOPs,GPU
memoryusage(Memory), shortertrainingtime(TraT),andtestingtime(TesT)when
handling low-dimensional data. However, when applied to high-dimensional data,
whichcontainssignificantredundantinformation,thecurrentactivationmechanismof
KANsleadstounnecessarycomputations,therebyreducingcomputationalefficiency.
KANsrequirereshapinghigh-dimensionaldataintoaone-dimensionaltensorasinput,
whichinevitablyresultsinthelossofdimensionalinformation. Toaddresstheselim-
itations, we propose weighted activationdistributionKANs (WKANs), which reduce
thefrequencyofactivationspernodeanddistributenodeinformationintodifferentout-
putnodesthroughweightstoavoidextractingredundantinformation. Furthermore,we
introduce a multilevel tensor splitting framework (MTSF), which decomposes high-
dimensionaldatatoextractfeaturesfromeachdimensionindependentlyandleverages
tensor-parallel computation to significantly improve the computational efficiency of
WKANsonhigh-dimensionaldata. Inthispaper, wedesignSpectralKANforhyper-
∗Correspondingauthor.Y.Gao.(e-mail:yongsheng.gao@griffith.edu.au)
6202
naJ
21
]VC.sc[
2v94900.7042:viXra

spectralimagechangedetectionusingtheproposedMTSF.SpectralKANdemonstrates
outstanding performance across five datasets, achieving an overall accuracy (OA) of
0.9801andaKappacoefficient(K)of0.9514ontheFarmlanddataset, withonly8k
parameters, 0.07 M FLOPs, 911 MB Memory, 13.26 s TraT, and 2.52 s TesT, under-
scoringitssuperioraccuracyefficiencytrade-off. Thesourcecodeispubliclyavailable
athttps://github.com/yanhengwang-heu/SpectralKAN.
Keywords: Activationfunctions,changedetection,high-dimensionaldata,
hyperspectralimages,Kolmogorov-Arnoldnetworks.
1. Introduction
KolmogorovArnoldNetworks(KANs),neuralarchitecturesbasedontheKolmogorovArnold
representationtheorem,havebeenproposedasalternativestoMulti-LayerPerceptrons
(MLPs) [1, 2]. Structurally, KANs are similar to MLPs, but they differ in their use
of activation functions. While MLPs rely on a single activation function across all
edges,KANsemploydifferent,learnableactivationfunctionsonvariousedges,endow-
ingthemwithstrongernonlinearrepresentationcapabilities. AlthoughasingleKAN
layer with the same number of nodes contains significantly more parameters than an
MLPlayer,KANsrequirefewerlayerstoachievesuperiorfeatureextractionforlow-
dimensional data. This leads to a lower overall number of parameters (NP), fewer
floating-point operations (FLOPs), reduced GPU memory usage (Memory), shorter
training time (TraT) and testing time (TesT). However, KANs fail to perform well in
handlinghigh-dimensionaldata,suchashyperspectralimagechangedetection.
Hyperspectral images are three-dimensional data that capture tens to hundreds of
spectralbandsfrommicrowavetomid-infraredwavelengths[3,4]. Hyperspectralim-
agechangedetectioninvolvesanalyzingmulti-temporalimagestoobtaininformation
about land changes [5, 6]. Convolutional neural networks (CNNs), graph neural net-
works (GNNs), and transformers built on MLPs perform well on high-dimensional
data [7, 8, 9]. However, their high accuracy comes with the cost of a large NP, high
FLOPs,extensiveMemory,andlongTraTandTesT.Thesefactorsmakecomputational
efficiencycrucialforhigh-dimensionaldataresearch,astheycansignificantlyimpact
2

Accuracy (Kappa %)
SpectralKAN 96 SpectralKAN
95
TriTF TriTF
SST-Former 94
SST-Former
ML-EDAN 93 ML-EDAN
DA-Former HyperSIGMA
92 DA-Former
HyperSIGMA
91 CSA-Net
CSA-Net
90
1000100 10 1 0.1 0.01 0.001 5 10 15 20 … 13151320
NP(M) TesT(s)
Fig.1: Performancecomparisonofstate-of-the-artmethodsandtheproposedSpectralKANonthecom-
monlyusedFarmlanddataset.
the feasibility and scalability of analysis. Given these challenges, advancing KANs
technologytohandlehigh-dimensionaldataisapromisingapproach.
ThemainchallengesofadvancingKANsforanalyzinghigh-dimensionaldataare
summarizedasfollows.
• A common approach to improving KANs is to replace MLPs in existing net-
works,suchasU-Net,withKANs. However,KANstypicallyhavemoreparam-
etersthanMLPsforthesamenumberofnodes,thusnegatingtheiradvantagesin
termsofcomputationalefficiencyandprovidingonlylimitedaccuracyimprove-
ments.
• KANsutilizeamechanismthatinvolvesmultipleactivationsofoneinputnode,
leading to a substantial increase in NP and FLOPs for high-dimensional data.
Additionally, high-dimensional data often contains significant information re-
dundancy, resultinginmanyparametersbeingdevotedtomanagingthisredun-
dantinformation.
• KANsaredesignedtoacceptone-dimensionalinputs, necessitatingthereshap-
ing of high-dimensional data into a one-dimensional format. This reshaping
process often leads to the loss of critical structural information inherent in the
originaldata.
Inthispaper,wetakeasignificantstepforwardinadvancingKANsforprocessing
3

Spatial Local Channel Local
Tensor Tensor
X 1 X
…
hse R
…
t u pt u
O
esi w
hcta P
X 2 Inp P u a t t : c h h w × i w se ×b g nittil p S
ros ne T
…
…
…
…
p sreya L l s N la A it l K e a v p W e S -l g nitt i
&
l p S
e p
r
a
os ne T … …
…
q sreya L l l s e N n A n l a K e h v W C e -l D : : e : 1 1 t L
C
e × × e c a
h
b 1 t r
a
i T T n o
n
a e e n b n n
g
l s s
e
M e o o r r ϕ ap
Fig.2:FlowchartoftheSpectralKAN.SpectralKANfirstsplitseachpatchintomultiplespatiallocaltensors
{vi }h
i=
×
1
w.Globalspatialfeaturesfarethenextractedusingspatial-levelWKANswithintheMTSF.Wefurther
splitf intochannellocaltensors{fe }b
e=1
. Channel-levelWKANsinMTSFsubsequentlyextractspectral
featuresandclassifythemaseitherchangedorunchanged.
high-dimensionaldata. TheweightedactivationdistributionKolmogorov-Arnoldnet-
works(WKANs)areproposed,reducingtheNPandFLOPsbyreducingthenumberof
activationspernode. Byemployingaweightedactivationdistribution, weeffectively
capture the dependencies between input and output nodes, which in turn reduces the
extractionofredundantinformation. Weintroduceamultileveltensorsplittingframe-
work (MTSF) to extract features from each dimension of high-dimensional data and
perform classification in the final layer. At each level, MTSF separates tensors and
allocatesthemtodifferentcomputationnodes,whereWKANsareusedtocalculatere-
lationshipsbetweenlocaltensors,ultimatelyobtainingglobalfeaturesforthatdimen-
sionallevel.Thistensor-parallelcomputationmethodnotonlyimprovescomputational
efficiencybutalsoacceleratesprocessingtimes.
Wedemonstratetheeffectivenessofourapproachusinghyperspectralimagechange
detectionasacasestudy. TheproposedSpectralKAN,basedonWKANsandMTSF,
isvalidatedonfivedatasets. AsshowninFig.1,SpectralKANoutperformedstate-of-
the-artalgorithmsonthewidelyusedFarmlanddatasetintermsofaccuracy(Kappa),
NP and TesT. SpectralKAN achieved the highest performance with the least NP and
shortest TesT, highlighting its effectiveness and efficiency in high-dimensional data
processing. Therearethreemaincontributionsinthispaperassummarizedfollows.
4

• We introduce WKANs, an optimization of KANs for high-dimensional data,
whichreducethenumberofactivationfunctionspernode,useweightstocontrol
theirsize,anddistributeactivationvaluestodifferentoutputnodes. Theycom-
pensateforinformationlossfromfewerbasicactivationsbyextractingredundant
information,significantlyloweringtheNPandFLOPs.
• WedevelopanMTSF,whichaddressesthestructuralinformationlossinherentin
KANs by separating tensors along different dimensions and extracting features
from each dimension. Additionally, the parallel tensor computation of MTSF
enhancesoverallcomputationalefficiency.
• WeproposeanovelSpectralKAN,advancingthepureKANsforhigh-dimensional
data processing. This method eliminates the need to replace MLPs in classical
networks,achievinghigheraccuracywhilereducingNP,FLOPs,Memory,TraT,
andTesT.
2. RelatedWork
2.1. Kolmogorov-ArnoldNetworks
Kolmogorov-Arnoldrepresentationtheoremstatesthatamultivariatefunctioncan
be represented as the superposition of continuous functions of a single variable with
twoparameters.Kolmogorov-Arnoldrepresentationtheoremhasbeenusedtoviewthe
neuralnetworkasamultivariatecontinuousfunction[10,11]. Thedepthandwidthof
thesenetworkshavealwaysbeen2and2n+1,respectively.Theydidnotconsiderusing
backpropagationtoupdatethenetwork. BasedonKolmogorov-Arnoldrepresentation
theorem, Liu et al. [2] designed deeper and more flexible KANs, which have been
proventopossessastrongerfunctionfittingcapabilitythanMLPs.
KANs have quickly gained attention, leading to numerous applications. KANs
were utilized to extract time-series information and proved their effectiveness in se-
quence feature extraction [12, 13, 14]. Cross-dataset human activity recognition has
beenachievedbasedonKANs[15]. Wav-KAN[16]isamodelthatusescontinuousor
discretewavelettransformstofitcontinuousmultivariatefunctionstogetabettertrain-
ing speed, performance and computational efficiency than MLPs. Jamali et al. [17]
5

introduced HybridKAN for hyperspectral image classification. HybridKAN replaces
theMLPsin3DCNN,2DCNN,and1DCNNwithKANs,therebyincreasingtheNP
andFLOPscomparedwithCNNs,whilealsorelyingonprincipalcomponentanalysis
(PCA)fordimensionalityreduction,whichleadstoconsiderablespectralinformation
loss. DeepOKAN[18]notonlyreplacestheB-splinesinKANswithGaussianradial
basisfunctionsbutalsosubstitutesthetraditionalMLPsinDeepONetwithKAN-based
architecturesformodelingcontinuousoperatormappingsincomplexengineeringand
mechanics problems. These design choices result in a substantially larger number of
parameters than standard KANs. A U-KAN that combines U-Net and KANs is pro-
posedtosegmentmedicalimages[15]. Xuetal. [19]combinedGCNsandKANsfor
recommendationtasksanduseddropouttoenhancetherepresentationalcapability. A
KCN[20]thatcombinesCNNsandKANshasbeenusedforsatelliteremotesensing
imageclassification. ItvalidatestheeffectivenessofKANsforremotesensingimage
processingbyreplacingtheMLPsindifferentCNN-basedbackboneswithKANs,and
demonstratesthatKANsshowbetterconvergence.
ThepureKAN-basedmethodshavedemonstratedgoodefficiencyonlow-dimensional
data. However, studies on their application to high-dimensional data remain limited.
Moreover,replacingMLPswithKANsinexistingnetworkssuchasU-Nettendstoin-
creasethetotalNPduetothehighercomplexityofasingleKANlayer,whileyielding
onlymarginalaccuracyimprovements.Thesestudieshavenotextendedtheadvantages
ofKANstohigh-dimensionaldata,wherecomputationalefficiencyisofparamountim-
portance.
2.2. DeepLearningforHyperspectralImageChangeDetection
Deeplearningdemonstratesstrongrepresentationalcapabilitiesforhigh-dimensional
data, achieving significant success in hyperspectral image processing. It is widely
usedtoextractspectral-spatialfeaturesfromhyperspectralimages. Spectralandspa-
tialattentionnetworksemploylearnableattentionmechanisms, enablingtheeffective
suppression of irrelevant spectral bands and spatial information [21, 22, 23]. Trans-
formers have been specifically employed to learn and process spectral sequence in-
formation, thereby enhancing the capability to capture intricate spectral patterns and
6

dependencies[24,25].Temporalinformationiscrucialandvariousmethodshavebeen
developed to detect changes between different temporal hyperspectral images. The
commonly used method is subtracting [26, 27] or concatenating [28] multi-temporal
imagesbeforefeatureextraction. Featureswerefusedatdifferentlayerstoobtainthe
multi-scale change features [29, 30, 31]. Long short-term memory network (LSTM)
was utilized to learn temporal change information [32, 33, 34]. Foundation models
have been introduced into change detection, leveraging large-scale pretraining to en-
hance generalization across diverse datasets and scenarios [35, 36]. For urgent tasks
and real-time processing, computational efficiency is equally critical. However, most
existingmethodsprimarilyfocusonimprovingaccuracy,whiletheirperformancewith
respecttoNP,FLOPs,memoryusage,TraT,andTesTremainsunsatisfactory.
3. ProposedMethod
3.1. SpectralKANOverview
The overall flowchart of SpectralKAN is illustrated in Fig. 2. Let X ∈ RH×W×b
1
and X ∈ RH×W×b denote a pair of co-registered bi-temporal hyperspectral images.
2
X = X −X is divided into multiple patches {x}H×W with a stride of 1, where x ∈
1 2 i i=1
Rh×w×b. h×wdenotesthepatchsize,brepresentsthenumberofspectralbandsineach
patch. xundergoestensorsplitting,resultinginspatiallocaltensors{v}h×w,v ∈R1×b.
i i=1 i
These local tensors are processed in parallel by the first level of the MTSF, where
they interact to extract global spatial features f ∈ R1×b. Next, the spatial dimension
is removed by reshaping f into Rb×1. f is decomposed into b channel-local tensors
{f }b . ThesetensorsarethenprocessedbythesecondleveloftheMTSF,producing
e e=1
a 1×2 output that captures global spatial-spectral features. Each level of the MTSF
isbuiltfromWKANs. The1×2tensorindicatestheprobabilitiesofchangeandno-
change, with the higher probability determining the change detection result. During
testing,theresultsfromallpatchesarecombinedtogeneratethefinalchangedetection
map.
7

3.2. WeightedActivationDistributionKANs
WKANsareaspecialvariantofKANstailoredforhigh-dimensionaldata,designed
toextractfeaturesbylearningactivationfunctions. WKANsconsistof LlayersΦ =
l
{Φ
l,1
,Φ
l,2
,...,Φ
l,m
},andthenetworkasawholecanberepresentedas:
∏L−1
f(x)=x· Φ (1)
l
l=0
If the input to the l-th layer of WKANs is x l ∈ Rm and the output is x l+1 ∈ Rn, the
computationwithinthislayerisdefinedas:
 
x l+1 =
(
Φ l,1 Φ l,2 ... Φ l,m
)

x
x
l
l
. .
.
,
,
1
2

(2)
x l,m
Inthisequation,Φ l,i = {ϕ 1 (·),ϕ 2 (·),...,ϕ n (·)}isthesetofactivationfunctionsfor x l,i ,
wherei∈[0,m]. EachΦ l,i consistsoftwoactivationfunctionswithweightssuchthat
     

ϕ
ϕ
1
2
.
.
.
(
(
·
·
)
)

=

w
w
a
a
.
.
.
,
,
1
2

α(·)+

w
w
b
b
.
.
.
,
,
1
2

spline(·) (3)
ϕ n (·) w a,n w b,n
whereα(·)andspline(·)arebasicactivationfunctions.α(·)referstosigmoidlinearunit
(SiLU)function. spline(·)iscomposedofmultipleB-splinebasisfunctions:
∑z+g
spline(x)= rB(x) (4)
i i
i=1
where B(·)isthei-thB-splinebasisfunction, r isthecorrespondingweight, zandg
i i
arethedegreeandgridofthe spline(·),respectively. Theweightsw andw scalethe
a b
activationfunctionsanddistributetheactivatedinputnodeinformationtodifferentout-
putnodes. Foreachinputx l,i processedbyΦ l,i ,andnoutputs{x l+1,i,j }n j=1 areproduced.
The detailed calculation process is illustrated in Fig. 3. Finally, the j-th node of the
outputx l+1,j iscomputedbysummingthecontributionsfromallinputs:
∑m
x l+1,j = x l+1,i,j (5)
i=1
8

x x x
l+1, i, 1 l+1, i, 2 l+1, i, n
x x x
l+1, i, 1 l+1, i, 2 l+1, i, n
x x … l+1,1 l+1,n
w
b,1 w
b,2 w
b,n
ϕ ϕ 2 … ϕ w a,1 w a,2 w a,n
1 n
r r 1 r z+g 2
…
B(·) B(·) B (·)
SiLU 1 2 z+g
x
l, i x x x
x l,1 l,2 l,m
l, i
x x x x x x l+1, i, 1 l+1, i, 2 l+1, i, n l+1, i, 1 l+1, i, 2 l+1, i, n
…
ϕ
ϕ 2 … ϕ w w w w w w
1 n a,1 b,1 a,2 b,2 a,n b,n
…
x SiLU Spline(·)
l, i
x
l, i
  w a,1  x l+1, i, 1
w spline b,1 w …
a,n
w b,n  x l+1, i, n
SiLU
z+ g
k
=1
rk B
k
( x ) x l+1,2
…

…
x
l,i
… … …
…
Fig.3:Structureofthel-thWKANlayerwithminputnodesandnoutputnodes.
3.3. MultilevelTensorSplittingFramework
Inspiredby[24,37,38],wedesigntheMTSF,whichdecomposeshigh-dimensional
tensors into multiple lower-dimensional tensors and assigns each dimension-specific
tensor to dedicated WKANs for feature extraction. Consider a s-dimensional input
x ∈ Rd1 ×d2 ×···×ds and an MTSF composed of s WKANs layers. Initially, x undergoes
tensor splitting to obtain d
1
dimensional local tensors {v
i
}d
i=
1
1
, where v
i
∈ Rd2 ×···×ds.
We define the first WKANs in the MTSF with d input nodes and a single output
1
node,processingalld tensorsinparallel,andaggregatingtheirfeaturesintoaunified
1
representation:
 
f = L∏
l
1
=
−
0
1 Φ 1,l

v
v . .
.
1
2

, f ∈R1×d2 ×···×ds (6)
v
d1
whereΦ 1,l representstheactivationfunctionsofthel-thlayerinthefirstWKANs,L 1 is
thenumberoflayersinthefirstWKANswithintheMTSF.Thisstructureensuresthat
{v
i
}d
i=
1
1
arecompressedintoasingleaggregatedrepresentation f ∈R1×d2 ×···×ds,capturing
theglobalinformationalongthefirstdimension. Thefirstdimensionisthenremoved
by reshaping f into Rd2 ×···×ds, facilitating the extraction of features along the second
dimension. Tensor splitting is subsequently applied along the second dimension to
obtaind localtensors, whicharethenprocessedinparalleltoextractfeaturesatthis
2
level. The second WKANs then process these tensors to capture global information
9

along the second dimension, analogous to the first dimension. This process repeats
for each subsequent dimension until global features for all dimensions are obtained.
Finally, the last WKANs produces an output y′ ∈ R1×c, where c is the number of
classes.Thecross-entropylossfunctionisthenusedtocalculatethedifferencebetween
thepredictedoutputy′andthetruelabely,guidingthenetworksoptimization.
SpectralKANisformulatedasanMTSFwithtwoWKANsforhyperspectralchange
detection,inwhichahyperspectralimagepatchisdecomposedintotwosetsoftensors
correspondingtothespatialandspectraldimensions. ThetwoWKANs,consistingof
L and L layers, are employed to separately extract spatial and spectral representa-
p q
tions. Inthefinallayer,theoutputnodecountcissettotwo,representingthechange
andno-changeclasses. ThepseudocodeofSpectralKANisshowninAlgorithm1.
Algorithm1SpectralKANforHyperspectralImageChangeDetection
Input: Bi-temporalhyperspectralimagesX ,X ∈RH×W×b
1 2
Output: ChangedetectionmapY
1:
X←X
1
−X
2
;initializeY←∅
2: fori←1toH×W do
3: x i ←Extract_Patches(X,patch_size=h×w)
4: Splitx i →{v j }h j= × 1 w, v j ∈R1×b
5: f ←Spatial-levelWKANs({v j })
6: Reshape f: R1×b →Rb×1
7: Split f →{f e }b e=1
8: p 1 ,p 2 ←Channel-levelWKANs({f e })
9: y←argmax(p 1 ,p 2 )
10: Y i ←y
11: endfor
12: returnY
3.4. MethodAnalysis
WKANsvsKANs: InKAN,eachactivationfunctionϕ(·)iscomposedofaunique
α(·)andspline(·):
10

x x x
l+1, i, 1 l+1, i, 2 l+1, i, n
x x x
l+1, i, 1 l+1, i, 2 l+1, i, n
…
w
b,1 w
b,2 w
b,n
ϕ ϕ 2 … ϕ w a,1 w a,2 w a,n
1 n
r r
1 r z+g
2
…
B(·) B(·) B (·)
SiLU 1 2 z+g
x
l, i
x
l, i
x x x x x x
l+1, i, 1 l+1, i, 2 l+1, i, n l+1, i, 1 l+1, i, 2 l+1, i, n
…
ϕ
ϕ 1 2 … ϕ n w a,1 w b,1 w a,2 w b,2 w a,n w b,n
…
x SiLU Spline(·)
l, i
x
l, i
Fig.4:StructureofasingleKANlayerwithoneinputnodeandnoutputnodes.
ϕ (·)=w ·α (·)+w ·spline (·) (7)
ij a ij b ij
whereirepresentsthei-thinputnode,and jdenotesthe j-thoutputnode. Thedetailed
calculation process is illustrated in Fig. 4. In comparison, WKAN uses a single α(·)
and a spline(·) for each input node across all output nodes, as indicated in Eq. 3. In
bothWKANsandKANs,theprimaryFLOPsintheactivationfunctionϕ(·)stemfrom
computationswithinα(·)andspline(·)andtheirmultiplicationwithweightsw andw .
a b
Specifically,α(·)incursO(4)FLOPs,whileB(·)z+grequiresO(4z(z+g))FLOPs.
Each
i i=1
weightmultiplicationfurtherrequiresO(1)FLOPs. Themainweightsforϕ(·)include
w ∈R1,w ∈R1,andrz+g ∈Rz+g. Foralayerwithminputnodesandnoutputnodes,
a b i=1
theFLOPsandNParesummarizedasfollows:
• WKANs:
-Flops: O(2mn+4m(1+z(z+g)2))
-NP:O(2mn+m(z+g))
• KANs:
-Flops: O(2mn+4mn(1+z(z+g)2))
-NP:O(2mn+mn(z+g))
WecanobservethatasingleWKANlayerhasapproximatelyntimesfewerNPand
FLOPscomparedtoasingleKANlayer. TheactivationmechanisminWKANsallows
11

themtoreducetheNPwithoutcompromisingaccuracywhilestillextractingadditional
featuresfromredundantnodes.
MTSFvsWKANs:MTSFprocesseseachdimensionhierarchicallyandinparallel,
reducing the number of nodes compared to WKANs. This leads to fewer activation
functions at the edges and consequently reduces both FLOPs and NP. For example,
SpectralKANisanMTSFdesignedforhyperspectraldata,processesinput x∈Rh×w×b
byspatial-levelWKANsand channel-levelWKANs withinput node countsof h×w
andb,respectively. Incontrast,asingleWKANswithouttensorsplittingwouldhave
h×w×binputnodes. AssumingL andL arebothsetto1,withoutputnodesbeing
p q
1 in both SpectralKAN and a single WKAN layer, the computational aspects can be
summarizedasfollows:
• MTSF:
-Flops: O((hw+b)(2+4(1+z(z+g)2))
-NP:O((hw+b)(2+(z+g)))
• WKANs:
-Flops: O(hwb(2+4(1+z(z+g)2))
-NP:O(hwb(2+(z+g)))
TheMTSFreducestheNPandFLOPstoapproximately(1/b+1/hw)ofthosein
WKANs. Moreover,MTSFenhancesfeatureextractionbyprocessingeachdimension
separately,leadingtoabetterrepresentationofhigh-dimensionaldata.
4. Experiments
4.1. Datasets
Weconductedexperimentsusingfivepubliclyavailabledatasets:Farmland1,USA[39],
River[40],BayArea2,andSantaBarbara2. ThesedatasetswerecapturedbytheEarth
Observation-1Hyperionhyperspectralsensor(EO-1)ortheAirborneVisible/Infrared
1https://rslab.ut.ac.ir/data
2https://citius.usc.es/investigacion/datasets/hyperspectral-change-detectiondataset
12

Imaging Spectrometer (AVIRIS). The changes in these datasets mainly involve land
covertypesandRivervariations. Thesatellitesource(SS),imagingtimes(IT),cover
land (CL), size (h×w×b) and spatial resolution (SR) for five datasets are provided in
Table 1. For each dataset, we used 1% of the pixels for training and the remaining
pixelsfortesting,asdetailedinTable2.
Table1:DetailsofFiveHyperspectralImageChangeDetectionDatasets
Dataset SS IT CL Size SR
Farmland EO-1 05.2006and04.2007 Yancheng,China 450×140×155 30m
River EO-1 05.2013and12.2013 Jiangsu,China 431×241×198 30m
USA EO-1 05.2004and05.2007 Hermiston,USA 307×241×154 30m
BayArea AVIRIS 2013and2015 BayArea,USA 600×500×224 20m
SantaBarbara AVIRIS 2013and2014 SantaBarbara,USA 984×740×224 20m
Table2:TheNumberofTrainingandTestSetsintheFiveDatasets.
TrainingSet TestingSet
Dataset Unchanged Changed Unknown
Unchanged Changed Unchanged Changed
Farmland 44723 18277 0 447 182 44276 18095
River 101885 9698 0 1018 96 100867 9602
USA 57311 16676 0 573 166 56738 16510
BayArea 34211 39270 226519 342 392 33869 38878
SantaBarbara 80418 52134 595608 804 521 79614 51613
Table3: ComparisonofOA,K, NP,FLOPs, Memory, TraTandTesTwithState-of-the-artMethodson
Farmland.TheBestResultsareHighlightedInBold.
OA K NP(k) FLOPs(M) Memory(MB) TraT(s) TesT(s)
ML-EDAN 0.97 0.9270 88130 275 3617 93.42 9.02
SST-Former 0.9743 0.9379 2498 145 1370 56.87 7.52
CSANet 0.9619 0.9075 2428 140 1561 63.9 7.85
TriTF 0.9754 0.9403 172 21 2406 49.02 16.06
DA-Former 0.9657 0.9174 398 30 1586 1444.43 10.46
HyperSIGMA 0.9661 0.9182 174596 29284 13585 868.32 1317.75
SpectralKAN 0.9801 0.9514 8 0.07 911 13.26 2.52
13

Table4: ComparisonofOA,K, NP,FLOPs, Memory, TraTandTesTwithState-of-the-artMethodson
River.TheBestResultsareHighlightedInBold.
OA K NP(k) FLOPs(M) Memory(MB) TraT(s) TesT(s)
ML-EDAN 0.9484 0.6783 88526 285 3629 163.05 17.34
SST-Former 0.9644 0.7671 2520 148 1483 124.15 15.7
CSANet 0.9501 0.6762 2452 144 1586 29.9 10.84
TriTF 0.9699 0.8099 181 22 2486 95.45 31.42
DA-Former 0.9509 0.7041 409 32 1455 1477.47 20.11
HyperSIGMA 0.9622 0.7532 174629 29285 13471 1711.32 2374.74
SpectralKAN 0.9745 0.8366 9 0.09 961 25.55 5.1
Table5:ComparisonofOA,K,NP,FLOPs,Memory,TraTandTesTwithState-of-the-artMethodsonUSA.
TheBestResultsareHighlightedInBold.
OA K NP(k) FLOPs(M) Memory(MB) TraT(s) TesT(s)
ML-EDAN 0.9400 0.8245 88121 275 3621 112.76 11.70
SST-Former 0.9431 0.8286 2498 145 1373 65.67 8.82
CSANet 0.9374 0.8167 2427 140 1561 77.5 9.73
TriTF 0.9563 0.8701 171 21 2418 59.69 19.89
DA-Former 0.9348 0.8169 398 30 1970 1269.04 12.41
HyperSIGMA 0.9454 0.8403 174595 29284 13583 989.03 1496.31
SpectralKAN 0.9591 0.8804 8 0.07 911 15.8 2.89
4.2. ExperimentalSetup
TheSpectralKANwasimplementedusingPyTorch2.3.0withCUDA11.8,andwas
trainedonanIntelo˝ Corei9-10900KCPUpairedwith128GBofRAMandNVIDIA
TITANRTXGPU.TheoperatingsystemusedwasUbuntu20.04.1LTS.In spline(·),
zandgweresetto3and5,respectively,followingcommonlyusedvaluesinexisting
KANsmodels. ThelayersL andL weresetto3and2. Eachimagepatchwassized
p q
5×5. Thespatial-levelWKANsinSpectralKANcomprisedthreelayerswith25,16,
and 1 node(s) respectively, while the channel-level WKANs consisted of two layers
withband2nodes. Thetrainingprocessinvolved200epochswithabatchsizeof64.
TheAdamoptimizerwasusedwithalearningrateof0.001,decayedbyafactorof0.9
every 10 epochs. The parameters (w , w , and r) were initialized using the Kaiming
a b
initializationmethod.
14

Six commonly used state-of-the-art methods, ML-EDAN [41], SST-Former [24],
CSANet[42],TriTF[43],DA-Former[44],andHyperSIGMA[35]wereusedascom-
parison methods. Performance was assessed using overall accuracy (OA) and Kappa
(K).Theconfusionmatrixwasemployedtodeterminetruepositive(TP),truenegative
(TN),falsepositive(FP),andfalsenegative(FN).OArepresentstheproportionofall
pixelsthatarecorrectlyclassified:
TP+TN
OA= (8)
TP+FP+TN+FN
K measuresperformanceconsideringclassimbalanceandisgivenby:
OA−p
K = e (9)
1−p
e
(TP+FP)(TP+FN)(TN+FN)(TN+FP)
p = (10)
e (TP+FP+TN+FN)2
Additionally,wecomparedtheNP,FLOPs,Memory,TraTandTesTofdifferentmeth-
ods,asthesemetricsarecrucialforpracticalapplicationsinhyperspectralimagechange
detection.
Table6:ComparisonofOA,K,NP,FLOPs,Memory,TraTandTesTwithState-of-the-artMethodsonBay
Area.TheBestResultsareHighlightedInBold.
OA K NP(k) FLOPs(M) Memory(MB) TraT(s) TesT(s)
ML-EDAN 0.9634 0.9264 88766 291 3635 113.41 53.82
SST-Former 0.9661 0.932 2534 150 1581 78.89 52.71
CSANet 0.9826 0.9652 2468 147 1564 48.1 31.01
TriTF 0.9814 0.9626 186 22 2496 64.88 102.64
DA-Former 0.9807 0.9612 416 33 1991 1309.59 56.65
HyperSIGMA 0.9779 0.9555 174649 29286 13435 1033.53 1575.78
SpectralKAN 0.9641 0.9329 10 0.1 981 17.33 14.18
4.3. ComparisonwithState-of-the-artMethods
Each experiment was repeated five times, and the average results are presented.
Fig.5,7,6,8,9displaythevisualresultsfortheFarmland,River,USA,BayArea,and
SantaBarbaradatasetsusingstate-of-the-artmethods. TheOA,K,NP,FLOPs,Mem-
ory,TraTandTesTforthesedatasetsarelistedinTable3,4,5,6,and7,respectively.
15

Table7:ComparisonofOA,K,NP,FLOPs,Memory,TraTandTesTwithState-of-the-artMethodsonSanta
Barbara.TheBestResultsareHighlightedInBold.
OA K NP(k) FLOPs(M) Memory(MB) TraT(s) TesT(s)
ML-EDAN 0.9828 0.9636 88766 290 3631 210.73 128.59
SST-Former 0.9752 0.9478 2534 150 1544 149.85 134.62
CSANet 0.9916 0.9823 2468 147 1368 144.2 75.25
TriTF 0.9854 0.9693 186 22 2464 134.07 250.28
DA-Former 0.9920 0.9832 416 33 1984 1590.66 140.03
HyperSIGMA 0.9837 0.9658 174649 29286 13435 2068.93 2919.26
SpectralKAN 0.9776 0.9531 10 0.1 981 30.10 34.72
1 2
(a) (b) (c) (d) (e) (f) (g) (h) (i) (j)
Fig.5: TheresultsonFarmlanddatasets. (a)Beforetemporalhyperspectralimages, (b)Aftertemporal
hyperspectralimages,(c)Groundtruth,(d)ML-EDAN,(e)SST-Former,(f)CSANet,(g)DA-Former,(h)
TriTF,(i)HyperSIGMA,(j)Ours.Thewhitepixelsarechanged,andtheblackpixelsareunchanged.
ResultsAnalysisfortheFarmlandDataset: AsillustratedinFig.5,theML-EDAN
mapshowsconsiderablesalt-and-peppernoise. SST-FormerandDA-Formerstruggle
withedgedetection,whileSST-FormerandCSANetmisssomealarmareas.TriTFand
HyperSIGMAalsoexhibitminorsalt-and-peppernoise.Incontrast,SpectralKANpro-
videssuperiorvisualquality.Table3showsthatSpectralKANachievesthehighestOA
andK,exceedingthesecond-bestTriTFby0.47%and1.11%,respectively. Moreover,
SpectralKANdemonstratesthelowestNP(8k),FLOPs(0.07M),memoryusage(911
MB),TraT(13.26s),andTesT(2.52s)amongallmethods,demonstratingitssuperior
computationalefficiency.
ResultsAnalysisfortheRiverDataset: Fig.7showsthevisualresultsfortheRiver
dataset. ML-EDAN exhibited numerous false positives and false negatives. SST-
Former, CSANet, and TriTF struggled with edge detection for small objects. DA-
16

CSA1Net Tri2T F DA-Former HyperSIGMA Ours
(a) (b) (c) (d) (e)
(f) (g) (h) (i) (j)
Fig.6: TheresultsonUSAdatasets. (a)Beforetemporalhyperspectralimages,(b)Aftertemporalhyper-
spectralimages,(c)Groundtruth,(d)ML-EDAN,(e)SST-Former,(f)CSANet,(g)DA-Former,(h)TriTF,
(i)HyperSIGMA,(j)Ours.Thewhitepixelsarechanged,andtheblackpixelsareunchanged.
Former and HyperSIGMA missed several changes in small areas. In contrast, Spec-
tralKAN showed improved visual results with fewer false negatives in small objects.
InTable4,althoughML-EDAN,SST-Former,CSANet,andDA-Formerhaveshorter
TesT,theyshowlowerK andlongerTraT.HyperSIGMAperformstheworstacrossthe
lastfiveevaluationmetrics. SpectralKANachievesthehighestOAandK,surpassing
TriTFby0.46%inOAand2.67%inK. SpectralKANalsodemonstratesclearadvan-
tages,exhibitingthelowestNP(9k),FLOPs(0.09M),memoryusage(961MB),TraT
(25.55s),andTesT(5.1s)amongallmethods.
Results Analysis for the USA Dataset: Fig. 6 shows varying degrees of missed
alarmareasacrossallmethods.SST-FormerandCSANetprovidesubparvisualresults,
whileTriTF,DA-Former,andSpectralKANperformwellonlargeobjectsbutstruggle
withnarrowandsmallobjects. Table5confirmsthatSpectralKANandTriTFarethe
top performers in OA and K, while methods such as DA-Former exhibit the lowest
accuracyonthisdataset. SpectralKANnotonlyachievesthehighestaccuracybutalso
substantiallyreducesNP,FLOPs,Memory,TraT,andTesTcomparedtootherstate-of-
the-art methods. In particular, SpectralKAN outperforms TriTF, with NP decreasing
17

1 2
(a) (b) (c) (d) (e) (f) (g) (h) (i) (j)
Fig.7: TheresultsonRiverdatasets. (a)Beforetemporalhyperspectralimages,(b)Aftertemporalhyper-
spectralimages,(c)Groundtruth,(d)ML-EDAN,(e)SST-Former,(f)CSANet,(g)DA-Former,(h)TriTF,
(i)HyperSIGMA,(j)Ours.Thewhitepixelsarechanged,andtheblackpixelsareunchanged.
CSANet X 1 T r i T F X 2 D A - FGorromuenrd t r u t h H y p e r SMIGL-MEAD A N O uSrSsT -Former
(a) (b) (c) (d) (e)
(f) (g) (h) (i) (j)
Fig.8: TheresultsonBayAreadatasets. (a)Beforetemporalhyperspectralimages, (b)Aftertemporal
hyperspectralimages,(c)Groundtruth,(d)ML-EDAN,(e)SST-Former,(f)CSANet,(g)DA-Former,(h)
TriTF,(i)HyperSIGMA,(j)Ours. Thewhitepixelsarechanged,andtheblackpixelsareunchanged. The
graypixelsareunknownongroundtruth.
from171k to8k, FLOPsfrom21M to0.07M,Memoryfrom2418MBto911MB,
TraTfrom59.69sto15.8s,andTesTfrom19.89sto2.89s,demonstratingsuperior
efficiencywhilemaintainingthebestperformance.
Results Analysis for the Bay Area Dataset: Fig. 8 displays the visual results for
theBayAreadataset. Whileallmethodseffectivelydetectedchangesinlabeledareas,
only SST-Former and SpectralKAN provided detailed edge detection. Given that the
annotatedregionsprimarilyconsistoflargerobjects,theperformanceofSpectralKAN
remainscompetitive, eventhoughitsaccuracyisslightlylowercomparedtoCSANet
18

(a) (b) (c) (d) (e)
(f) (g) (h) (i) (j)
Fig.9:TheresultsonSantaBarbaradatasets.(a)Beforetemporalhyperspectralimages,(b)Aftertemporal
hyperspectralimages,(c)Groundtruth,(d)ML-EDAN,(e)SST-Former,(f)CSANet,(g)DA-Former,(h)
TriTF,(i)HyperSIGMA,(j)Ours. Thewhitepixelsarechanged,andtheblackpixelsareunchanged. The
graypixelsareunknownongroundtruth.
andothermethods. Table6indicatesthatCSANet,TriTF,andDA-Formerachievethe
top three OA and K scores. Although SpectralKAN lags behind by 3.23%, 2.97%,
and 2.83% in K, respectively, it excels in detecting object edges and small objects,
which are challenging for the other methods. Closer inspection reveals that most of
SpectralKANserrorsoccuralongchangeboundaries. Thisissuearisesbecausespline
functionsareinherentlysmoothandcontinuous,makingthembettersuitedformodel-
inglow-frequencyandsmoothlyvaryingregionssuchasbackgroundsortheinteriors
oflargehomogeneousobjects. Incontrast,boundariesintheBayAreadatasetcontain
substantial mixed pixels and high-frequency transitions. Consequently, spline-based
activationsmayunder-respondtotheseabruptvariations,leadingtooccasionalmissed
detectionsalongobjectedges. Evenwiththislimitation,SpectralKANproducesclean
boundarymapsanddeliversstrongaccuracywhilekeepingNP,FLOPs,memory,TraT,
andTesTsubstantiallylowerthancompetingmodels.
Results Analysis for the Santa Barbara Dataset: As shown in Fig. 9, all methods
perform well in the annotated regions. SpectralKAN demonstrates clear advantages
19

in detecting small objects and delineating the boundaries of changed areas, under-
scoringitsstrongfeatureextractioncapability. Table7furtherindicatesthatalthough
SST-Former achieves slightly lower accuracy than some methods, its OA and K still
reach97.52%and94.78%,respectively.Bycontrast,DA-Former,CSANet,andHyper-
SIGMAdeliverhigherchangedetectionaccuracy,butatthecostofsubstantiallylarger
NP, Memory, and FLOPs, as well as longer TraT and TesT. SpectralKAN attains an
OAof97.76%andaK of95.31%,whichisabout3%lowerthanthebest-performing
DA-Former in terms of K, yet still represents competitive accuracy. Similar to the
Bay Area dataset, the main source of error lies near object boundaries, where high-
frequencymixedpixelscausethesplineactivationtoundershootsharptransitions,re-
sulting in a small number of missed edge pixels. Despite this, SpectralKAN remains
themostlightweightmethod, requiringonly10k parameters, 0.1M FLOPs, 981MB
memory, and achieving the shortest TraT and TesT (30.10 s and 34.72 s) among all
comparedapproaches.
In conclusion, ML-EDAN demonstrated relatively low OA and K. SST-Former,
DA-Former,andHyperSIGMAoutperformedML-EDAN,showingbetterresults.CSANet
excelledontheBayAreaandSantaBarbaradatasetsbutunderperformedontheother
three. TriTFachievedsecond-highestaccuracyacrossalldatasets. Allthesemethods
exhibit higher NP, FLOPs, Memory, TraT and TesT. SpectralKAN achieved the best
OAandK ontheFarmland,River,andUSAdatasets,andalsoperformedwellonthe
BayAreaandSantaBarbaradatasets.SpectralKANiscomposedofonlyafewWKAN
layers,resultinginasubstantiallyreducedNPcomparedwiththestate-of-the-artmeth-
ods. SpectralKANintegratesmultipleactivationfunctions,providingstrongernonlin-
earfeatureextractioncapability. Consequently,theconsiderablereductioninNPdoes
not compromise accuracy, and the lower NP directly translates into reduced FLOPs,
Memory, TraT, and TesT, making SpectralKAN particularly suitable for deployment
ondeviceswithlimitedcomputationalresources.
4.4. AblationStudies
WeconductedablationstudiestoevaluatetheeffectivenessoftheproposedWKANs
and MTSF. Four model configurations were considered: the original KANs [2], the
20

Table8: AblationExperimentResultsforWKANsandMTSF,ShowingK andNP.TheBestResultsare
HighlightedinBold.
Farmland River USA BayArea Barbara
WKANMTSF
K NP(k) K NP(k) K NP(k) K NP(k) K NP(k)
KANs % % 0.9435 620 0.7638 792 0.8437 616 0.9109 896 0.9479 896
WKANs ! % 0.9426 155 0.7648 198 0.8423 154 0.9185 224 0.9529 224
MTSF-KANs % ! 0.9497 29 0.8219 36 0.878 29 0.9347 40 0.9565 40
SpectralKAN ! ! 0.9514 8 0.8366 9 0.8804 8 0.9329 10 0.9531 10
proposed WKANs, MTSF constructed with KANs (MTSF-KANs), and MTSF con-
structedwithWKANs(SpectralKAN).Theresultsacrossfivedatasetsaresummarized
inTable8,usingNPandK asevaluationmetrics.
WeobservedthatWKANsandSpectralKANachievedapproximatelyafourfoldre-
ductioninNPcomparedwithKANsandMTSF-KANs,respectively. Despitethissub-
stantialreduction, K remainedlargelystableacrossdatasets, indicatingthatWKANs
effectivelysuppressredundantrepresentationsinhigh-dimensionaldatawithoutcom-
promisinginformationintegrity.Furthermore,comparisonsbetweenKANsandMTSF-
KANs, as well as between WKANs and SpectralKAN, showed that MTSF achieved
more than a twentyfold reduction in NP while simultaneously improving K. These
resultsdemonstratethatMTSFnotonlyenhanceshigh-dimensionalfeatureextraction
butalsosubstantiallyreducescomputationalcost.
4.5. EffectofHyperparameters
TostudytheeffectofhyperparametersonSpectralKAN,wefocusedonthenumber
ofnodesandhiddenlayers,aswellasthenumberoftrainingsamples. Otherhyperpa-
rametersweresetbasedonpriorworkandempiricalexperience.
DifferentnumbersofnodesandhiddenlayersinSpectralKANresultindifferentNP
and accuracy. We selected six different combinations of nodes and layers to identify
theoptimalstructure: a: [25,1],[b,2],b: [25,16,1],[b,2],c: [25,1],[b,16,2],d: [25,
16,1],[b,16,2],e:[25,64,1],[b,16,2],andf:[25,16,1],[b,64,2].Inaf,thefirstset
specifies the number of nodes in each layer of the spatial-level WKANs (e.g., [25,1]
indicates 25 nodes in the first layer and 1 node in the second layer), while the sec-
21

0.96
0.92
a
b
a
p c
p 0.88
a
K d
e
0.84 f
0.8
Farmland river USA Bay Area San Barbara
Fig.10:TheKofdifferentnodesandlayersonfivedatasets.
1
0.95
0.9
0.85
0.8
0.75
0.7
0.001 0.005 0.01 0.02 0.05 0.1 0.2
appaK
Farmland
river
USA
Bay Area
San Barbara
Number of Training Samples
Fig.11:TheKofdifferenttrainingsetnumberonfivedatasets.
22

ondsetprovidesthecorrespondinglayer-wisenodeconfigurationofthechannel-level
WKANs. Fromatof,thenumberofnodesorlayersgraduallyincreases,accompanied
by an increase in NP. The K of experiments can be seen in Fig. 10. In the Farmland
dataset,asthenumberofnodesorlayersincreases,theK alsograduallyincreases. In
the other datasets, however, no consistent pattern is observed. Considering both NP
andK,wedeterminethatbisthebestconfiguration.
Different tasks have varying requirements for number of training samples. 0.1%,
0.5%,1%,2%,5%,10%,20%ofthepixelsastrainingsetstoanalyzetheirimpacton
SpectralKAN.TheresultsareshowninFig.11. Weobservethatwithalargernumber
oftrainingsamples,theaccuracyofchangedetectionincreases.
5. Conclusion
In this paper, we propose WKANs and MTSF to advance KANs for processing
high-dimensionaldata. Weapplytheseinnovationstohyperspectralimagechangede-
tectionbydevelopingtheSpectralKAN.Extensiveexperimentsonfivedatasetsdemon-
stratethatSpectralKANachievesanaverageOAof97.11%andaK of91.09%.Mean-
while, it substantially reduces NP, FLOPs, and Memory, achieving TesT up to two
times faster than the best baseline method. Overall, SpectralKAN combines com-
petitive accuracy with high efficiency, making it suitable for scenarios with limited
computationalresources. Butspline-basedactivationstendtoproduceoverlysmooth
responses in the high-frequency regions typically found along hyperspectral object
boundaries, which may lead to missed detections at change edges. In future work,
weplantoaddressthislimitationbyincorporatingfrequency-domaintransformations,
suchastheDiscreteCosineTransform,toenhancethemodelsabilitytocapturehigh-
frequency boundary information. Additionally, we will extend the MTSF to other
high-dimensional tasks, such as 3D point clouds and video data, to further validate
itseffectivenessandbroadenitsapplications.
23

6. DeclarationofInterestStatement
Theauthorsdeclarethattheyhavenoknowncompetingfinancialinterestsorper-
sonalrelationshipsthatcouldhaveappearedtoinfluencetheworkreportedinthispa-
per.
7. Acknowledgement
This work was supported in part by the National Key Laboratory on Electromag-
neticEnvironmentalEffectsandElectro-opticalEngineeringunderGrantKY3240020001
andtheAerospaceScienceandTechnologyInnovationDevelopmentFundunderGrant
ZY0110020009.
References
[1] K.Hornik,M.Stinchcombe,H.White,Multilayerfeedforwardnetworksareuni-
versalapproximators,Neuralnetworks2(5)(1989)359–366.
[2] Z. Liu, Y. Wang, S. Vaidya, F. Ruehle, J. Halverson, M. Soljacˇic´, T. Y.
Hou, M. Tegmark, Kan: Kolmogorov-arnold networks, arXiv preprint
arXiv:2404.19756(2024).
[3] R. Wu, H. Liu, Z. Yue, C.-W. Sham, J.-B. Li, Feature space expansion and
compression with spatial-spectral augmentation for hyperspectral image class-
incrementallearning,PatternRecognition(2025)111830.
[4] Z.Jiang,J.Li,S.Xu,Z.Liu,D.Ma,Q.Wang,Y.Yuan,Cross-domainhyperspec-
tralimageclassification,PatternRecognition(2025)111836.
[5] J. Qu, J. He, W. Dong, J. Zhao, S2cyclediff: Spatial-spectral-bilateral cycle-
diffusion framework for hyperspectral image super-resolution, in: Proceedings
oftheAAAIConferenceonArtificialIntelligence,Vol.38,2024,pp.4623–4631.
[6] Y.Wang, L.Gao, D.Hong, J.Sha, L.Liu, B.Zhang, X.Rong, Y.Zhang, Mask
deeplab: End-to-endimagesegmentationforchangedetectioninhigh-resolution
24

remote sensing images, International Journal of Applied Earth Observation and
Geoinformation104(2021)102582.
[7] Y.Li, W.Xie, H.Li, Hyperspectralimagereconstructionbydeepconvolutional
neuralnetworkforclassification,PatternRecognition63(2017)371–383.
[8] K.-K. Huang, C.-X. Ren, H. Liu, Z.-R. Lai, Y.-F. Yu, D.-Q. Dai, Hyperspectral
imageclassificationviadiscriminativeconvolutionalneuralnetworkwithanim-
provedtripletloss,PatternRecognition112(2021)107744.
[9] A. Sellami, S. Tabbone, Deep neural networks-based relevant latent represen-
tation learning for hyperspectral image classification, Pattern Recognition 121
(2022)108224.
[10] D.A.Sprecher,S.Draghici,Space-fillingcurvesandkolmogorovsuperposition-
basedneuralnetworks,NeuralNetworks15(1)(2002)57–67.
[11] P.-E. Leni, Y. D. Fougerolle, F. Truchetet, The kolmogorov spline network for
image processing, in: Image Processing: Concepts, Methodologies, Tools, and
Applications,IGIGlobal,2013,pp.54–78.
[12] C.J.Vaca-Rubio,L.Blanco,R.Pereira,M.Caus,Kolmogorov-arnoldnetworks
(kans)fortimeseriesanalysis,arXivpreprintarXiv:2405.08790(2024).
[13] R. Genet, H. Inzirillo, Tkan: Temporal kolmogorov-arnold networks, arXiv
preprintarXiv:2405.07344(2024).
[14] Z.Huang, J.Cui, L.Yu, L.F.HerbozoContreras, O.Kavehei, Abnormalityde-
tectionintime-seriesbio-signalsusingkolmogorov-arnoldnetworksforresource-
constraineddevices,medRxiv(2024)2024–06.
[15] M. Liu, S. Bian, B. Zhou, P. Lukowicz, ikan: Global incremental learning with
kanforhumanactivityrecognitionacrossheterogeneousdatasets,arXivpreprint
arXiv:2406.01646(2024).
[16] Z. Bozorgasl, H. Chen, Wav-kan: Wavelet kolmogorov-arnold networks, arXiv
preprintarXiv:2405.12832(2024).
25

[17] A. Jamali, S. K. Roy, D. Hong, B. Lu, P. Ghamisi, How to learn more? explor-
ing kolmogorovarnold networks for hyperspectral image classification, Remote
Sensing16(21)(2024). doi:10.3390/rs16214015.
[18] D.W.Abueidda,P.Pantidis,M.E.Mobasher,Deepokan: Deepoperatornetwork
based on kolmogorov arnold networks for mechanics problems, arXiv preprint
arXiv:2405.19143(2024).
[19] J.Xu, Z.Chen, J.Li, S.Yang, W.Wang, X.Hu, E.C.-H.Ngai, Fourierkan-gcf:
Fourierkolmogorov-arnoldnetwork–aneffectiveandefficientfeaturetransforma-
tionforgraphcollaborativefiltering,arXivpreprintarXiv:2406.01034(2024).
[20] M. Cheon, Kolmogorov-arnold network for satellite image classification in re-
motesensing,arXivpreprintarXiv:2406.00600(2024).
[21] L.Wang,L.Wang,Q.Wang,P.M.Atkinson,Ssa-siamnet: Spectral–spatial-wise
attention-basedsiamesenetworkforhyperspectralimagechangedetection,IEEE
TransactionsonGeoscienceandRemoteSensing60(2021)1–18.
[22] M. Hu, C. Wu, L. Zhang, Globalmind: Global multi-head interactive self-
attention network for hyperspectral change detection, ISPRS Journal of Pho-
togrammetryandRemoteSensing211(2024)465–483.
[23] H.Yu,H.Yang,L.Gao,J.Hu,A.Plaza,B.Zhang,Hyperspectralimagechange
detectionbasedongatedspectral–spatial–temporalattentionnetworkwithspec-
tralsimilarityfiltering,IEEETransactionsonGeoscienceandRemoteSensing62
(2024)1–13.
[24] Y.Wang,D.Hong,J.Sha,L.Gao,L.Liu,Y.Zhang,X.Rong,Spectral–spatial–
temporaltransformersforhyperspectralimagechangedetection, IEEETransac-
tionsonGeoscienceandRemoteSensing60(2022)1–14.
[25] M.Han,J.Sha,Y.Wang,X.Wang,Pbformer: Pointandbi-spatiotemporaltrans-
formerforpointwisechangedetectionof3durbanpointclouds,RemoteSensing
15(9)(2023)2314.
26

[26] Q.Guo,J.Zhang,C.Zhong,Y.Zhang,Changedetectionforhyperspectralimages
viaconvolutionalsparseanalysisandtemporalspectralunmixing, IEEEJournal
ofSelectedTopicsinAppliedEarthObservationsandRemoteSensing14(2021)
4417–4426.
[27] X. Ou, L. Liu, B. Tu, G. Zhang, Z. Xu, A cnn framework with slow-fast band
selectionandfeaturefusiongroupingforhyperspectralimagechangedetection,
IEEETransactionsonGeoscienceandRemoteSensing60(2022)1–16.
[28] X.Zhang,S.Tian,G.Wang,X.Tang,J.Feng,L.Jiao,Cast: Acascadespectral
awaretransformerforhyperspectralimagechangedetection,IEEETransactions
onGeoscienceandRemoteSensing61(2023)1–14.
[29] F.Luo,T.Zhou,J.Liu,T.Guo,X.Gong,J.Ren,Multiscalediff-changedfeature
fusionnetworkforhyperspectralimagechangedetection,IEEETransactionson
GeoscienceandRemoteSensing61(2023)1–13.
[30] J.Qu,W.Dong,Y.Yang,T.Zhang,Y.Li,Q.Du,Cycle-refinedmultidecisionjoint
alignment network for unsupervised domain adaptive hyperspectral change de-
tection,IEEETransactionsonNeuralNetworksandLearningSystems36(2024)
2634–2647.
[31] L. Ning, Q. Zhou, Q. Wang, J. Gao, X. Li, Cross-resolution change detection
inremotesensingviaunequalrelationshipsfromafrequencyperspective, IEEE
TransactionsonGeoscienceandRemoteSensing63(2025)1–14.
[32] A.Song,J.Choi,Y.Han,Y.Kim,Changedetectioninhyperspectralimagesusing
recurrent3dfullyconvolutionalnetworks,RemoteSensing10(11)(2018)1827.
[33] B.Bai,W.Fu,T.Lu,S.Li,Edge-guidedrecurrentconvolutionalneuralnetwork
formultitemporalremotesensingimagebuildingchangedetection,IEEETrans-
actionsonGeoscienceandRemoteSensing60(2021)1–13.
[34] C. Shi, Z. Zhang, W. Zhang, C. Zhang, Q. Xu, Learning multiscale temporal–
spatial–spectral features via a multipath convolutional lstm neural network for
27

change detection with hyperspectral images, IEEE Transactions on Geoscience
andRemoteSensing60(2022)1–16.
[35] D.Wang, M.Hu, Y.Jin, Y.Miao, J.Yang, Y.Xu, X.Qin, J.Ma, L.Sun, C.Li,
etal.,Hypersigma: Hyperspectralintelligencecomprehensionfoundationmodel,
IEEETransactionsonPatternAnalysisandMachineIntelligence47(2025)6427
–6444.
[36] J.Gao,D.Zhang,F.Wang,L.Ning,Z.Zhao,X.Li,Combiningsamwithlimited
data for change detection in remote sensing, IEEE Transactions on Geoscience
andRemoteSensing63(2025)1–11.
[37] X.Wang,F.Zhang,K.Zhang,W.Wang,X.Dun,J.Sun,Learningspatial-spectral
dualadaptivegraphembeddingformultispectralandhyperspectralimagefusion,
PatternRecognition151(2024)110365.
[38] Z.Chen, C.Liu, J.Zhou, Ssit: Aspatial-spectralinteractivetransformerforhy-
perspectralimagedenoising,ScienceofRemoteSensing(2025)100276.
[39] M.Hasanlou,S.T.Seydi,Hyperspectralchangedetection:Anexperimentalcom-
parativestudy,Internationaljournalofremotesensing39(20)(2018)7029–7083.
[40] Q.Wang,Z.Yuan,Q.Du,X.Li,Getnet:Ageneralend-to-end2-dcnnframework
forhyperspectralimagechangedetection,IEEETransactionsonGeoscienceand
RemoteSensing57(1)(2018)3–13.
[41] J. Qu, S. Hou, W. Dong, Y. Li, W. Xie, A multilevel encoder–decoder atten-
tionnetworkforchangedetectioninhyperspectralimages,IEEETransactionson
GeoscienceandRemoteSensing60(2021)1–13.
[42] R.Song,W.Ni,W.Cheng,X.Wang,Csanet:Cross-temporalinteractionsymmet-
ricattentionnetworkforhyperspectralimagechangedetection,IEEEGeoscience
andRemoteSensingLetters19(2022)1–5.
[43] X.Wang,K.Zhao,X.Zhao,S.Li,Tritf: Atriplettransformerframeworkbased
onparentsandbrotherattentionforhyperspectralimagechangedetection,IEEE
TransactionsonGeoscienceandRemoteSensing61(2023)1–13.
28

[44] Y.Wang,J.Sha,L.Gao,Y.Zhang,X.Rong,C.Zhang,Asemi-superviseddomain
alignmenttransformerforhyperspectralimageschangedetection,IEEETransac-
tionsonGeoscienceandRemoteSensing61(2023)1–11.
29