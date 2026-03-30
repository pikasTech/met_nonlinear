# Li_2024_KA_GNN

KA-GNN: KOLMOGOROV-ARNOLD GRAPH NEURAL NETWORKS
FOR MOLECULAR PROPERTY PREDICTION
LonglongLi1,2,3,YipengZhang3,GuanghuiWang1,andKelinXia3
1SchoolofMathematics,ShandongUniversity,Jinan250100,China
2DataScienceInstitute,ShandongUniversity,Jinan250100,China
3DivisionofMathematicalSciences,SchoolofPhysicalandMathematicalSciences,NanyangTechnological
University,Singapore637371,Singapore
Emails: longlee@mail.sdu.edu.cn,yipeng001@e.ntu.edu.sg,ghwang@sdu.edu.cn,xiakelin@ntu.edu.sg
ABSTRACT
Askeymodelsingeometricdeeplearning,graphneuralnetworkshavedemonstratedenormouspower
inmoleculardataanalysis. Recently,aspecially-designedlearningscheme,knownasKolmogorov-
ArnoldNetwork(KAN),showsuniquepotentialfortheimprovementofmodelaccuracy,efficiency,
andexplainability. Hereweproposethefirstnon-trivialKolmogorov-ArnoldNetwork-basedGraph
NeuralNetworks(KA-GNNs),includingKAN-basedgraphconvolutionalnetworks(KA-GCN)and
KAN-basedgraphattentionnetwork(KA-GAT).TheessentialideaistoutilizesKAN’suniquepower
tooptimizeGNNarchitecturesatthreemajorlevels,includingnodeembedding,messagepassing,
andreadout. Further,withthestrongapproximationcapabilityofFourierseries,wedevelopFourier
series-basedKANmodelandprovidearigorousmathematicalproveoftherobustapproximation
capabilityofthisFourierKANarchitecture. TovalidateourKA-GNNs,weconsidersevenmost-
widely-usedbenchmarkdatasetsformolecularpropertypredictionandextensivelycomparewith
existingstate-of-the-artmodels. IthasbeenfoundthatourKA-GNNscanoutperformtraditional
GNNmodels. Moreimportantly,ourFourierKANmodulecannotonlyincreasethemodelaccuracy
butalsoreducethecomputationaltime. ThisworknotonlyhighlightsthegreatpowerofKA-GNNs
inmolecularpropertypredictionbutalsoprovidesanovelgeometricdeeplearningframeworkforthe
generalnon-Euclideandataanalysis.
Keywords Kolmogorov-ArnoldNetwork,Fourierseries,GraphNeuralNetwork,MolecularPropertyPrediction
1 Introduction
Drugdevelopmentisacomplexandcostlyprocess,typicallyrequiringdecadesoftimeandsubstantialinvestment[1].
Inthischallenginglandscape,artificialintelligence(AI)hasbecomeparticularlyvaluable,significantlyimpactingthe
predictionofmolecularpropertiesandshowingimmensepromiseindrugdesign[2,3]. AIhasgreatlyadvancedvirtual
screeningprocesses,potentiallyreducingthetimeandinvestmentrequired[4,5,6]. AI-basedmolecularmodels,which
drivetheseadvancements,generallyfallintotwocategories: thosebasedonmoleculardescriptorsandend-to-enddeep
learningmodels[7].
Thefirstcategoryreliesonmoleculardescriptorsorfingerprintsasinputfeaturesformachinelearningalgorithms. This
process,knownasfeaturizationorfeatureengineering,involvesnotonlycapturingphysical,chemical,andbiological
propertiesbutalsoincorporatingawidearrayoffingerprintsbasedonmolecularstructureinformation. Amongthese,
structure-basedfingerprints,particularlythosederivedfromtopologicaldataanalysismethods,haveprovenhighly
effectiveinmolecularrepresentationandfeaturization[8,9,10,11]. Theintegrationofthesefingerprintswithlearning
models has achieved significant success in various stages of drug design, including protein-ligand binding affinity
prediction[12,13],proteinmutationanalysis[14,15],anddrugdesign[16,17],amongotherareas.
4202
ceD
81
]GL.sc[
2v32311.0142:viXra

Thesecondcategoryincludesend-to-enddeeplearningmodelsthatutilizevariousmolecularrepresentationssuchas
SimplifiedMolecularInputLineEntrySystem(SMILES)strings,images,ormoleculargraphs,anddeployarchitectures
like Transformers, Convolutional Neural Networks (CNNs), and Graph Neural Networks (GNNs) for prediction
[18, 19, 20, 21, 22, 23]. Among these, molecular graphs based on covalent bonds are predominantly employed
todescribemoleculartopology. Geometricdeeplearningmodelsbasedonthesemoleculargraphs, suchasGraph
ConvolutionalNetworks(GCNs)[24],graphautoencoders[25],andgraphtransformers[26],havebeenextensivelyused
inmoleculardataanalysisanddrugdesign. Additionally,recentresearchhasdemonstratedthatmoleculardescriptors
basedonnon-covalentinteractionsperformexceptionallywellinpredictingprotein-ligandandprotein-proteinbinding
affinities[27]. Theseobservationsimplythatnewgeometricmoleculargraphrepresentationscouldsurpasstraditional
covalent-bond-basedgraphs. Byintegratingthesegeometry-basedmoleculargraphsintoGeometricDeepLearning
(GDL)models,itispossibletoenhancemodelperformanceanddeepentheunderstandingofmoleculargeometry[28].
Molecule MoleculeGraph Message Passing Readout
Covalent
Non-Covalent
𝑦#
𝑣
KAN Node Embedding Message Passing
𝑥(#) 𝑥(#)
! %
𝑓! ⊕ KAN ℎ ! (') ℎ ! (() + ℎ ! (()*)
𝜑! ($ ,! ) 𝜑& ($ ,! ) 𝜑' ($ ,! ) 𝜑! ($ ,& ) 𝜑& ($ ,& ) 𝜑' ($ ,& ) |𝑁 1 𝑣 | & 𝑓"! |𝑁 1 𝑣 | & ℎ " (() ⊕ KAN
"∈$(!) "∈$(!)
𝑥 ! (#&!) 𝑥 % (#&!) 𝑥 ' (#&!)
𝑓 " Linear ℎ ! (() Linear + KAN ℎ ! (()*)
𝑓 ! Linear + KAN ℎ " (' ! ) ℎ " (() Linear
KA-GCN 𝑓 "! Linear
|𝑁
1
𝑣 |
& 𝑧
"
(()*)𝛼"!
1 "∈$(!)
KA-GAT
|𝑁𝑣 |
& 𝑓"!
𝜎
"∈$(!)
⊕ KAN ℎ ! (') ℎ " (( ! ) KAN ℎ " (( ! )*)
Figure1: OverviewoftheKA-GNNmodelarchitecture. Theflowchartillustratesthemodifiedcomponentswithinthe
GNN:nodeembedding,message-passing,poolingandpredictionmodules.
Kolmogorov-Arnold Networks (KANs), which are based on the Kolmogorov-Arnold representation theorem, are
increasinglyrecognizedasapotentalternativetoMulti-layerPerceptrons(MLPs). KANsdistinguishedbytheirunique
architecture that employs different learnable activation functions, eliminate traditional linear weight matrices and
enhancemodelaccuracyandefficiency,particularlyinsolvingpartialdifferentialequations,asdescribedbyLiuet
al. [29]. RecentresearchhighlightstheversatilityandadaptabilityofKANsacrossvariousdomains[30,31,32,33].
One notable application is the integration of KANs with existing neural network models to enhance performance.
Forinstance, Genetetal. [33]significantlyimprovedmulti-steptimeseriesforecastingbyintegratingKANswith
Long Short-Term Memory networks (LSTMs). Cheon et al. [34] effectively classified remote sensing scenes by
mergingKANswithpre-trainedConvolutionalNeuralNetwork(CNN)models. Kiamarietal. [35]demonstratedtheir
multifunctionalitybyincorporatingKANsintoGraphConvolutionalNetworks(GCNs)forsemi-supervisedgraph
learningtasks. Furthermore,adaptationsinthebasefunctionsofKANstobettersuitneuralnetworkapplicationshave
led to significant enhancements. Bozorgasl et al. [36] improved the interpretability and performance of KANs by
incorporatingwaveletfunctionsthatmoreeffectivelycapturethefrequencycomponentsofdata. Tashinetal. [37]
employedKANswithFouriertransformbasisfunctionsforfeaturetransformationbeforeGNNprocessing,validating
theirutilityinSmallMolecule-ProteinInteractionPredictions. Lietal. [38]usedadaptiveRadialBasisFunctions
2

(RBFs)inKANstoenhancefeatureupdatingandreplaceMLPsinthepredictionphase,demonstratingrobustintegration
capabilitieswithvariousneuralnetworkframeworks. Kashefietal. [39]appliedJacobipolynomialstodesignKAN
layers for GNNs, effectively predicting fluid fields on irregular geometries. These advancements underscore the
significantpotentialofKANstorefineneuralnetworkarchitectures. Theongoingexplorationofhowtofurtherenhance
KANsandintegrateitintonodefeatureembedding,messagepassingindifferentGNNframeworks,andtheprediction
phaseremainsavitalareaofresearch.
Inthispaper,weintroducethefirstnon-trivialKolmogorov-ArnoldNetwork-basedGraphNeuralNetworks(KA-GNNs),
includingKAN-basedconvolutionalnetworks(KA-GCN)andKAN-basedgraphattentionnetwork(KA-GAT).Figure
1outlinesthegeneralKA-GNNsarchitecture. DifferentfromalltheprevioustrivialKAN-basedGNNmodels,which
onlyreplacetheMLPinthereadoutpartwithastandardKANmodule,weutilizesKANtooptimizeGNNarchitectures
atthreemajorlevels,includingnodeembedding,messagepassing,andreadout. Further,aFourierseries-basedKAN
modelhasbeendevelopedandarigoroustheoreticalproveofitsrobustapproximationcapabilityisgiven. Basedon
sevenbenchmarkdatasets,wehaveextensivelyvalidatedourKA-GNNsandcomparedwithstate-of-the-artmodels.
OurKA-GNNshaveachievedbothgreataccuracyandefficiency,providinganovelgeometricdeeplearningframework
foranalyzinggeneralnon-Euclideandata.
2 Results
2.1 Kolmogorov-ArnoldNetwork(KAN)
Kolmogorov-ArnoldRepresentationTheoremTheKolmogorov–ArnoldRepresentationTheorem(orSuperposition
Theorem)isamilestoneinthefieldofrealanalysisandapproximationtheory.Itstatesthateverymultivariatecontinuous
functioncanberepresentedassuperpositionoftheadditionofcontinuousfunctionsofonevariable. Thistheoremnot
onlysolvesHilbert’sthirteenthproblemitselfbutalsogeneralizesittoabroaderform.
VladimirArnoldandAndreyKolmogorov’sworks[40]provethatarbitrarymultivariatecontinuousfunctionf canbe
writtenasafinitecompositionofcontinuousfunctionsofasinglevariableandthebinaryoperationofaddition. More
specifically,
2n+1 (cid:32) n (cid:33)
(cid:88) (cid:88)
f(x ,...,x )= Φ ϕ (x ) , (1)
1 n q q,p p
q=0 p=1
wherendenotethenumberofvariablesofthefunctionf. Φ :R→Randϕ :[0,1]→Rarecontinuesfunction.
q q,p
2.1.1 Kolmogorov-ArnoldNetwork(KAN)
InspiredbytheKolmogorov-Arnoldrepresentationtheorem,Liuetal. [29]proposedanewdeeplearningarchitecture
calledtheKolmogorov-ArnoldNetwork(KAN)asapromisingalternativetotheMulti-LayerPerceptron(MLP).To
enhancetheKAN’srepresentationalcapacityandleveragemoderntechniques(e.g.,backpropagation)fortrainingthe
networks,KANtranscendsseverallimitationsoftheKolmogorov-Arnoldrepresentationtheorem:
• KANdoesnotadheretotheoriginaldepth-2width-(2n+1)representation;instead,itgeneralizestoarbitrary
widthsanddepths. Specifically,lettheactivationvaluesinlayerlbedenotedbyx(l) :=(x(l),x(l),··· ,x(l)),
1 2 nl
wheren isthewidthoflayerl. Theactivationvalueinlayerl+1isthensimplythesumofallincoming
l
post-activations:
x(l+1) = (cid:88)
nl
ϕ(l)(x(l)), j =1,...,n . (2)
j j,i i l+1
i=1
Here,ϕ(l)fori=1,...,n andj =1,...,n arethepre-activationfunctionsinlayerl. Therolesofthese
j,i l l+1
functionsinKANareanalogoustotherolesoftheinnerfunctionsϕ inequation1.
q,p
• AlthoughmanyconstructiveproofsoftheKolmogorov-Arnoldrepresentationtheoremindicatethattheinner
functionsϕ inequation1arehighlynon-smooth[41,42],KANoptsforsmoothfunctionsaspre-activation
q,p
functionsϕ(l)tofacilitatebackpropagation. Liuetal. [29]selectedfunctionsbasedonB-splines.
j,i
3

2.1.2 Fourier-seriesKANmodel
Tooptimizethenetworkandavoidcomplexcalculations, weproposetoutilizeFourierseriesasthepre-activation
functionsforKAN[37]asinEq.(2):
K
ϕ(l)(x)=
(cid:88)(cid:16)
A(l) cos(kx)+B(l) sin(kx)
(cid:17)
, (3)
j,i k,j,i k,j,i
k=1
whereK isthenumberofharmonics,andA(l) andB(l) arelearnableparametersinitiallysampledfromanormal
k,j,i k,j,i
(cid:16) (cid:17)
distributionN 0, 1 .
nl+1×K
Consequently,theactivationvalueatthej-thneuroninlayerl+1canbeobtainedby,
x(l+1) = (cid:88)
nl
(cid:88)
K
(cid:16) A(l) cos(kx(l))+B(l) sin(kx(l)) (cid:17) , (4)
j k,j,i i k,j,i i
i=1k=1
wherex(l) = (x(l),x(l),...,x(l))denotestheinputvectorofactivationvaluesinlayerloftheKAN,andx(l+1) =
1 2 nl
(x(l+1),x(l+1),...,x(l+1))representstheoutputvector. Eq(4)canbeconciselyexpressedas: x(l+1) =KAN (x(l)),
1 2 nl+1 l
whereKAN (·)denotestheaboveKANfunctioninlayerl. Thisnetworkisintegratedintoagraphneuralnetwork,
l
culminatinginanovelarchitecturenamedKA-GNNs,whichisemployedformolecularpropertypredictiontasks.
Given that the inner functions in Eq (1) of the Kolmogorov-Arnold representation theorem can exhibit significant
non-smoothness,wedonotusethistheoremasthefoundationaltheoryforshowingtheapproximationcapabilityofour
model. Instead,webaseourapproachontheextensionofCarleson’stheorem[43]regardingtheconvergenceofFourier
seriesformultivariablefunctions,asprovedbyFeffermanin[44]:
Theorem1 Let Zn denote the n-dimensional integer lattice, and let Zn = {1,2,...,N}n ⊂ Zn. Then for the
N
functionf ∈L2([0,2π]n)anditsFourierexpansion:
f(⃗x)∼ (cid:88) (cid:16) a cos(⃗k·⃗x)+b sin(⃗k·⃗x) (cid:17) ,
⃗k ⃗k
⃗k∈Zn
wherex∈[0,2π]nandL2([0,2π]n)denotesthespaceofsquare-integrablefunctionson[0,2π]n,whichconsistsofall
functionsf suchthat (cid:82) |f(⃗x)|2d⃗x<∞. Wehave
[0,2π]n
f(⃗x)= lim (cid:88) (cid:16) a cos(⃗k·⃗x)+b sin(⃗k·⃗x) (cid:17)
⃗k ⃗k
N→∞
⃗k∈Zn
N
almosteverywhere.
TheabovetheoremdemonstratesthestrongapproximationcapabilityofFourierseries,whichiswhyweadoptFourier
seriesasthefoundationalbasisforourmodel. Therefore,weretainthearchitectureoftheKolmogorov-Arnoldnetwork
but replace the pre-activation functions with Fourier series. We can further prove that this new KAN architecture
providesthepotentialofrobustapproximationcapability:
Theorem2 Letf ∈L2([0,2π]n)beasquare-integrablefunction. Foralmostevery⃗x∈[0,2π]n andforanyϵ>0,
thereexistapositiveintegerKandasequenceofFourier-basedKANfunctionsKAN atmultiplelayersl=0,1,...,L,
l
suchthatthenumberofharmonicsinthepre-activationfunctionsoftheseKANfunctionsdoesnotexceedK,and
|f(⃗x)−KAN ◦KAN ◦···◦KAN (⃗x)|<ϵ,
L L−1 0
where◦denotesfunctioncomposition.
Insummary,ourmodelextendstheKolmogorov-ArnoldNetwork(KAN)architecturebyincorporatingFourierseries
aspre-activationfunctionstoenhanceapproximationcapability.
2.2 Kolmogorov-ArnoldNetwork-basedGraphNeuralNetworkModels
InourKA-GNNmodels,amoleculeisrepresentedasagraphG=(V,E),whereV denotesthesetofnodesandE
denotesthesetofedges. Eachnoderepresentsanatomandanedgeisformedamonganytwoatomsiftheirdistanceis
4

Table1: FeaturesTypeandDescriptioninKA-GNNmodels. Herewelistbothatom,covalentbond,andnon-covalent
bondfeatures.
FeaturesType Description Type Size
Atom CGCNN Atomicnumber,Radius,andelectronegativity One-Hot 92
BondDirectionality None,Beginwedge,Begindash,etc. One-Hot 7
BondType Single,Double,Triple,orAromatic. One-Hot 4
CovalentBond
BondLength Numericalandsquarelengthofthebond. Float 2
InRing Indicatesifthebondispartofachemicalring. One-Hot 2
Atomcharges AtomschargesinMolecular(q ,q ,q ·q ) Float 3
Non-CovalentBond i j i j
Distancebetweenatoms Distancebetweenatoms( 1 , 1 , 1 ) Float 3
dij d6
ij
d1
ij
2
withinacutoffdistance(inourmodel,weusecutoffdistanceas5Å).Figure1Aillustratesthecomplexinteractions
withinthemolecule,highlightingboththecovalentbonds(solidlines)andnon-covalentcut-offbonds(dashedlines)
withdistanceslessthan5angstromsareconsideredinourKA-GNNmodel. Ouratomicfeatures—comprisingatomic
number,radius,andelectronegativity—arederivedusingRdkit,followingtheapproachinCGCNN[45]andPCNN
[46]. Eachnodev ∈ V isassociatedwithafeaturevectorf , whichisa92-dimensionalvectorcomposedofone-
v
hot encoded representations of atomic properties, following the approach described in [45]. Similarly, each edge
uv ∈ E isassociatedwithafeaturevectorf ,whichisa21-dimensionalvectorincorporatingbothchemicaland
uv
geometricalinformationofthebonduv. Theedgesinourmodelcanbeclassifiedintotwotypes,i.e.,covalentbonds
andnon-covalentbonds,withdifferentinitialfeatures. DetaileddescriptionsofthefeaturevectorsareprovidedinTable
1.
2.2.1 KA-GCNModel
OurKA-GCNarchitecturehasthreemajorsteps,includingnodeembedding,message-passing,andreadout. First,one
KANlayerisemployedintheinitializationofnodeembeddingsh(0),v ∈V asfollows,
v
 
1 (cid:88)
h(
v
0) :=KANf
v
⊕(
|N(v)|
f
uv
), (5)
u∈N(v)
where N(v) represents the set of the neighboring nodes of node v (excluding v itself), |N(v)| is the number of
neighboringnodes,and⊕representsvectorconcatenation.
Second, one or several KAN layers are employed in the message passing module. At the layer l, the KAN-based
messagepassingmodulecanbeexpressedas,
 
1 (cid:88)
h(
v
l+1) :=h(
v
l)+KANh(
v
l)⊕(
|N(v)|
h(
u
l)). (6)
u∈N(v)
Computationally,thefirstKANlayermapsinitialfeaturevectorf fromdimension113toupdatedfeaturevectorh
v v
withdimension64. Afterthat,thefeaturedimensionwillstaythesameinthelatermessage-passingprocess.
Third,oneorseveralKANlayersareemployedinthereadoutmodule. AfterL-ththemessagepassingphases,weapply
averagepoolingacrossallnodefeaturestoobtainalatentvectorforthemoleculargraphG. Anone-layerortwo-layer
KANmodelisemployedinreadoutmoduleforthefinalpredictionasfollows,
(cid:32) (cid:33) (cid:32) (cid:32) (cid:33)(cid:33)
1 (cid:88) 1 (cid:88)
yˆ:=KAN h(L) or,yˆ:=KAN KAN h(L)
|V| v |V| v
v∈V v∈V
Thecross-entropyisusedasthelossfunctionasfollows,
(cid:88)
L:=− (y log(yˆ)+(1−y )log(1−yˆ)),
i i i i
i
wherey denotestheactuallabel,andyˆ denotesthepredictedlabel.
i i
5

2.2.2 KA-GATModel
SimilartotheKA-GCNarchitecture,theKA-GATmodelinitializesthenodeandedgeembeddings,h(0) andh(0),
v uv
usingaKANlayerasfollows:
  
1 (cid:88)
h(
v
0) :=KANf
v
⊕
|N(v)|
f uv,
(7)
u∈N(v)
h(0) :=KAN(Linear(f )+Linear(f )+Linear(f ))
uv v uv u
Subsequently,theKA-GATmodelusestheseinitialembeddingstocomputeattentionscoresthatguidetheaggregation
ofmessages:
(cid:16) (cid:17) (cid:16) (cid:17)
z(l+1) :=Linear h(l) ,z(l+1) :=Linear h(l) ,
v v u u
(cid:16) (cid:17)
α :=Softmax h(l) ,m(l+1) :=z(l+1)·α
uv uv uv u uv
(8)
 
1 (cid:88)
m( v l+1) :=z v (l+1)+ |N(v)|  m( u l v +1) 
u∈N(v)
Then,oneormoreKANlayersareusedtoupdatethenodeandedgefeatures:
h(l+1) :=KAN(m(l+1)), h(l+1) :=KAN(h(l)) (9)
v v uv uv
Finally,aftermessagepassing,theKA-GATmodelemploysthesamereadoutmoduleasusedintheKA-GCN.
2.3 KA-GNNsforMolecularPropertyAnalysis
2.3.1 PerformanceandcomparisonofKA-GNNs
ToevaluatetheperformanceofourproposedKA-GNNmodels,weconsidersevenwidely-usedbenchmarkdatasets
fromMoleculeNet[47]. Ofthese,threedatasets—MUV,HIV,andBACE—arefromthebiophysicsdomain. Therest
fourdatasetsarefromthephysiologydomain,includingBBBP,Tox21,SIDER,andClinTox.
Inourcomparativeanalysisacrosssevendatasets,weevaluatedarangeofgeometricdeeplearningmodels,including
AttentiveFP[48],D-MPNN[49],Mol-GDL[28],N-Gram[50],PretrainGNN[51],GROVER[26],GraphMVP[52],
MolCLR[53],GEM[54],Uni-mol[55],SMPT[56],andGNN-SKAN[38]. Additionally,weincludedourKAN-based
GNNmodels,suchastheGNN-SKAN[38]. FurtherdetailsonthesemodelscanbefoundinSubsectionBaseline
Models.
The comparative results in Table 2 further confirm the superiority of the KA-GNNs model. Our model achieves
state-of-the-artperformanceacrossallbenchmarkdatasets,particularlyexcellingoncomplexandchallengingdatasets
suchasClinToxandMUV.Theseresultsdemonstratetherobustcapabilityofourmodelinhandlingmoleculardata.
Notably,intheBBBPdataset,theAUCforKA-GCNandKA-GATshowedimprovementsofapproximately7.95%and
7.68%.
2.3.2 ImportanceofFourierseriesforKA-GNNs
Inthisresearch,weemployedaFourier-basedKolmogorov-ArnoldNetwork(KAN)astheprimarycomputational
mechanismwithinourGNNarchitecture,whichdifferssignificantlyfromtraditionalMLP-basedapproaches. Toassess
theimpactofdifferentbasefunctionsonthepredictionofmolecularproperties,weexploredseveralbasefunction
includingB-spline,polynomial,Fourier-series,intheKA-GCNsarchitecture. Thesemodelsweretestedwithinthe
traditionalGCNframeworkaswellastheGATframework. ThecomparativeresultsaresummarizedinTable3. The
Polynomial-basefunctioncanbeexpressedinEq(10).
x(l+1) = (cid:88)
nl
(cid:88)
K
(cid:16) C(l) (x(l))k (cid:17) , (10)
j k,j,i i
i=1k=1
6

Table2: ComparisonofKA-GNNswithstate-of-the-artgeometricdeeplearningmodelsindifferentmolecularproperty
datasets. TheperformancemetricistheaverageofReceiverOperatingCharacteristic-AreaUndertheCurve(ROC-
AUC).Thestandarddeviationresultsaredenotedassubscripts. Thebestmodelforeachcategoryishighlightedinbold,
whilethesecond-bestperformanceismarkedwithunderline. Thenotation-indicatesthattheresultswerenotreported.
Model BACE BBBP ClinTox SIDER Tox21 HIV MUV
No.molecules 1513 2039 1478 1427 7831 41127 93808
No.avgatoms 65 46 50.58 65 36 46 43
No.tasks 1 1 2 27 12 1 17
D-MPNN[49] 0.809 0.710 0.906 0.570 0.759 0.771 0.786
(0.006) (0.003) (0.007) (0.007) (0.007) (0.005) (0.014)
AttentiveFP[48] 0.784 0.663 0.847 0.606 0.781 0.757 0.786
(0.022) (0.018) (0.003) (0.032) (0.005) (0.014) (0.015)
N-GramRF[50] 0.779 0.697 0.775 0.668 0.743 0.772 0.769
(0.015) (0.006) (0.040) (0.007) (0.009) (0.004) (0.002)
N-GramXGB[50] 0.791 0.691 0.875 0.655 0.758 0.787 0.748
(0.013) (0.008) (0.027) (0.007) (0.009) (0.004) (0.002)
PretrainGNN[51] 0.845 0.687 0.726 0.627 0.781 0.799 0.813
(0.007) (0.013) (0.015) (0.008) (0.006) (0.007) (0.021)
GROVE_base[26] 0.821 0.700 0.812 0.648 0.743 0.625 0.673
(0.007) (0.001) (0.030) (0.006) (0.001) (0.009) (0.018)
GROVE_large[26] 0.810 0.695 0.762 0.654 0.735 0.682 0.673
(0.014) (0.001) (0.037) (0.001) (0.001) (0.011) (0.018)
GraphMVP[52] 0.812 0.724 0.791 0.639 0.759 0.770 0.777
(0.009) (0.016) (0.028) (0.012) (0.005) (0.012) (0.006)
MolCLR[53] 0.824 0.722 0.912 0.589 0.750 0.781 0.796
(0.009) (0.021) (0.035) (0.014) (0.002) (0.005) (0.019)
GEM[54] 0.856 0.724 0.901 0.672 0.781 0.806 0.817
(0.011) (0.004) (0.013) (0.004) (0.001) (0.009) (0.005)
Mol-GDL[28] 0.863 0.728 0.966 0.831 0.794 0.808 0.675
(0.019) (0.019) (0.002) (0.002) (0.005) (0.007) (0.014)
Uni-mol[55] 0.857 0.729 0.919 0.659 0.796 0.808 0.821
(0.002) (0.006) (0.018) (0.013) (0.005) (0.003) (0.013)
SMPT[56] 0.873 0.734 0.927 0.676 0.797 0.812 0.822
(0.015) (0.003) (0.002) (0.050) (0.001) (0.001) (0.008)
GNN-SKAN[38] 0.747 0.676 - 0.614 0.747 0.786 -
(0.009) (0.014) (0.005) (0.005) (0.015)
KA-GCN 0.890 0.787 0.989 0.842 0.799 0.821 0.834
(0.014) (0.014) (0.003) (0.001) (0.005) (0.005) (0.009)
KA-GAT 0.884 0.785 0.991 0.847 0.800 0.823 0.834
(0.004) (0.021) (0.005) (0.002) (0.006) (0.002) (0.010)
Table 3: Comparison of the performance of KA-GNN (and KA-GAT) models with three types of base functions,
includingB-spline,polynomial,andFourierseries.
Dataset KA-GCNModels KA-GATModels
B-spline Polynomial Fourierseries B-spline Polynomial Fourierseries
BACE 0.771 0.853 0.890 0.808 0.8319 0.884
(0.012) (0.027) (0.014) (0.009) (0.007) (0.004)
BBBP 0.723 0.654 0.787 0.657 0.708 0.785
(0.008) (0.009) (0.014) (0.004) (0.005) (0.021)
ChinTox 0.973 0.981 0.989 0.948 0.983 0.991
(0.006) (0.004) (0.003) (0.003) (0.003) (0.005)
SIDER 0.824 0.832 0.842 0.825 0.836 0.847
(0.003) (0.006) (0.001) (0.004) (0.001) (0.002)
Tox21 0.724 0.715 0.799 0.731 0.753 0.800
(0.005) (0.004) (0.005) (0.012) (0.004) (0.006)
HIV 0.753 0.804 0.821 0.744 0.818 0.823
(0.007) (0.010) (0.005) (0.018) (0.006) (0.002)
MUV 0.638 0.787 0.834 0.792 0.797 0.834
(0.008) (0.012) (0.009) (0.013) (0.011) (0.010)
(cid:16) (cid:17)
where, C(l) is learnable parameters initially sampled from a normal distribution N 0, 1 . x(l) =
k,j,i nl+1×K
(x(l),x(l),...,x(l))denotestheinputvectorofactivationvaluesinlayerlofthePolynomial-seriesbasedKAN.
1 2 nl
The data in the table illustrate that the KA-GCN and KA-GAT models, which incorporate Fourier-based methods,
consistently outperform other models across all tested datasets. This underscores the substantial advantages of
integratingFourier-basedapproachesinenhancingthepredictiveaccuracyandgeneralizabilityofGNNarchitectures.
ThesuperiorityofthesemodelsislargelyattributabletothepowerfulapproximationcapabilitiesofFourier-basedKAN,
whichwehavesubstantiatedinTheorem2andwillfurthervalidatethroughsubsequentfunctionfittingevaluations.
Furthermore,ourablationstudynotonlyvalidatesourhypothesisthatFourier-basedKANprovidesarobustframework
forimprovingmolecularpropertyprediction,significantlyenhancingeverythingfrommolecularfeatureinitializationto
messagepassingingraphneuralnetworksandpredictioncomputations,butalsocomparestheoperationalefficiencyof
modelsunderdifferentbasefunctions. AsshowninFigure2AandB,theresultsdemonstratethatFourier-basedKAN
significantlyoutperformsB-splineKANintermsofefficiency. TheFourier-basedmodelsalsoclearlysurpasstheGCN
andGATmodelsthatutilizetheseothertwobasefunctions.
Furthermore,inthisstudy,wealsocomparedthetraditionalGCNandGATmodelswithourKA-GNNs(KA-GCN
and KA-GAT), on the same feature molecular graphs. Table 4 illustrates that KA-GNNs demonstrate significant
7

Table4: ComparisonofGCN/GATmodelsandKA-GCN/KA-GATwithFourierseries.
Dataset GCN KA-GCN GAT KA-GAT
BACE 0.835 0.890 0.834 0.884
(0.014) (0.014) (0.012) (0.004)
BBBP 0.735 0.787 0.707 0.785
(0.011) (0.014) (0.007) (0.021)
ChinTox 0.979 0.989 0.983 0.991
(0.004) (0.003) (0.006) (0.005)
SIDER 0.834 0.842 0.836 0.847
(0.001) (0.001) (0.002) (0.002)
Tox21 0.747 0.799 0.751 0.800
(0.006) (0.005) (0.007) (0.006)
HIV 0.762 0.821 0.761 0.823
(0.005) (0.005) (0.003) (0.002)
MUV 0.741 0.834 0.784 0.834
(0.006) (0.009) (0.019) (0.010)
performance improvements across all datasets. This confirms that the incorporation of Fourier series significantly
enhancesthemodels’abilitytorecognizeandexpresstheinherentperiodicityandcomplexityinchemicalstructures.
Discussion
We attribute the effectiveness and power of the KA-GNNs model to three core innovations. First, in constructing
moleculargraphs,weincorporateedgesnotonlyfromtraditionalcovalentbondsbutalsofromnon-covalentinteractions
basedonacut-offdistance. Thisapproachsignificantlyenhancesthemodel’sunderstandingofmolecularstructures,
enablingittocapturemoremolecularpropertiesthantraditionalcovalentinteractionsalone. Second, weintegrate
theKolmogorov-ArnoldNetwork(KAN)intoourmodel. KANsignificantlyreducesthenumberofparameterswhile
providing high interpretability and enhanced expressive power, leading to superior performance of the KA-GNNs
model. Third,wereplacethepre-activationfunctionintheKANmodelfromtheoriginalB-splinestoFourierseries
functions. Fourierseriesfunctions,widelyusedinsignalprocessing,haveproveneffectiveinourmodelforanalyzing
and learning high-dimensional graphical data. By learning and optimizing the coefficients of these Fourier series
functions for different variables, KA-GNNs improves the accuracy and stability of predictions when dealing with
complexchemicalandbiologicaldatastructures. Thesethreeinnovationscollectivelycontributetotheoutstanding
performanceofKA-GNNs,makingitapowerfultoolformolecularpropertyprediction.
However,ourKA-GNNsstillhavelimitations. Oneofthekeychallengesistheirinterpretability. EventhoughKANs
havebeendesignedforexcellentinterpretabilityandindeedshowgoodresultsinPDEexamples. Inourstudy,the
pruningprocesshoweverdoesnotgeneratebiologicallymeaningfulsuperpositionstructures,thatareeasytointerpretate.
A B
Figure2: ThecomparisonthecomputationalefficiencyofKA-GNNsbasedonB-spline,polynomial,andFourierseries.
A.RunningtimeofKA-GCNmodelfor100epochsacrossdifferentdatasets. B.RunningtimeofKA-GATModelfor
100epochsacrossdifferentdatasets.
8

3 Methods
3.1 ApproximationCapabilityofFourierKAN
Given that the inner functions in Eq (1) of the Kolmogorov-Arnold representation theorem can exhibit significant
non-smoothness,wedonotusethistheoremasthefoundationaltheoryforshowingtheapproximationcapabilityofour
model. Instead,webaseourapproachontheextensionofCarleson’stheorem[43]regardingtheconvergenceofFourier
seriesformultivariablefunctions,asprovedbyFeffermanin[44]:
Theorem3 Let Zn denote the n-dimensional integer lattice, and let Zn = {1,2,...,N}n ⊂ Zn. Then for the
N
functionf ∈L2([0,2π]n)anditsFourierexpansion:
f(⃗x)∼ (cid:88) (cid:16) a cos(⃗k·⃗x)+b sin(⃗k·⃗x) (cid:17) ,
⃗k ⃗k
⃗k∈Zn
wherex∈[0,2π]nandL2([0,2π]n)denotesthespaceofsquare-integrablefunctionson[0,2π]n,whichconsistsofall
functionsf suchthat (cid:82) |f(⃗x)|2d⃗x<∞. Wehave
[0,2π]n
f(⃗x)= lim (cid:88) (cid:16) a cos(⃗k·⃗x)+b sin(⃗k·⃗x) (cid:17)
⃗k ⃗k
N→∞
⃗k∈Zn
N
almosteverywhere.
TheabovetheoremdemonstratesthestrongapproximationcapabilityofFourierseries,whichiswhyweadoptFourier
seriesasthefoundationalbasisforourmodel. Therefore,weretainthearchitectureoftheKolmogorov-Arnoldnetwork
but replace the pre-activation functions with Fourier series. We can further prove that this new KAN architecture
providesthepotentialofrobustapproximationcapability:
Theorem4 Letf ∈L2([0,2π]n)beasquare-integrablefunction. Foralmostevery⃗x∈[0,2π]n andforanyϵ>0,
thereexistapositiveintegerKandasequenceofFourier-basedKANfunctionsKAN atmultiplelayersl=0,1,...,L,
l
suchthatthenumberofharmonicsinthepre-activationfunctionsoftheseKANfunctionsdoesnotexceedK,and
|f(⃗x)−KAN ◦KAN ◦···◦KAN (⃗x)|<ϵ,
L L−1 0
where◦denotesfunctioncomposition.
Theorem5 Let Zn denote the n-dimensional integer lattice, and let Zn = {1,2,...,N}n ⊂ Zn. Then for the
N
functionf ∈L2([0,2π]n)anditsFourierexpansion:
f(⃗x)∼ (cid:88) (cid:16) a cos(⃗k·⃗x)+b sin(⃗k·⃗x) (cid:17) ,
⃗k ⃗k
⃗k∈Zn
wherex∈[0,2π]nandL2([0,2π]n)denotesthespaceofsquare-integrablefunctionson[0,2π]n,whichconsistsofall
functionsf suchthat (cid:82) |f(⃗x)|2d⃗x<∞.
[0,2π]n
Wehave
f(⃗x)= lim (cid:88) (cid:16) a cos(⃗k·⃗x)+b sin(⃗k·⃗x) (cid:17)
⃗k ⃗k
N→∞
⃗k∈Zn
N
almosteverywhere.
Proof. ThetheoremfollowsasaparticularinstanceofthemultidimensionalCarlesontheorem,asestablishedin[44].
Theorem6 Letf ∈L2([0,2π]n)beasquare-integrablefunction. Foralmostevery⃗x∈[0,2π]n andforanyϵ>0,
thereexistapositiveintegerKandasequenceofFourier-basedKANfunctionsKAN atmultiplelayersl=0,1,...,L,
l
suchthatthenumberofharmonicsinthepre-activationfunctionsoftheseKANfunctionsdoesnotexceedK,and
9

|f(⃗x)−KAN ◦KAN ◦···◦KAN (⃗x)|<ϵ,
L L−1 0
where◦denotesfunctioncomposition.
Proof. BasedonTheorem1,thereexistsanumberN suchthat
(cid:12) (cid:12)
(cid:12) (cid:12)
(cid:12) (cid:12) (cid:12) f(⃗x)− (cid:88) (cid:16) a ⃗k cos(⃗k·⃗x)+b ⃗k sin(⃗k·⃗x) (cid:17)(cid:12) (cid:12) (cid:12) < 2 ϵ . (11)
(cid:12) ⃗k∈Zn (cid:12)
N
Furthermore,thereexistsδ >0suchthatforany⃗k∈Zn andanyy ∈Rwith∥y−⃗k·⃗x∥<δ,wehave
N
ϵ
|cos(y)−cos(⃗k·⃗x)|< , (12)
4Nna
⃗k
and
ϵ
|sin(y)−sin(⃗k·⃗x)|< . (13)
4Nnb
⃗k
LetS(N ,id)(x)denotethepartialsumofthefirstN termsoftheFourierexpansionoff,whereN issuchthat
1 1 1
δ
|x−S(N ,id)(x)|< , (14)
1 nN
andid:x(cid:55)→xistheidentityfunctionon[0,2π].
Toprovetheresult,selectK =max{N,N }. WeconstructKANfunctionsKAN andKAN intwolayerstoachieve
1 0 1
|f(⃗x)−KAN ◦KAN (⃗x)|<ϵ.Inthefollowingproof,wedenotetheinputvectoratlayerlbyx(l) =(x(l),x(l),...),
1 0 1 2
andlettheinitialinputvectorx(0) =⃗x
ForZn ={⃗k ,⃗k ,...,⃗k }with⃗k =(k ,k ,...,k ),definethepre-activationfunctionatlayer0as
N 1 2 Nn j j,1 j,2 j,n
ϕ(0)(x)=k S(N ,id)(x), i=1,2,...,n, j =1,2,...,Nn.
j,i j,i 1
Thenthej-thneuronatlayer1isx(1) = (cid:80)n k S(N ,id)(x(0)). From(14),wehave
j i=1 j,i 1 i
(cid:12) (cid:12)
(cid:12)x(1)−⃗k ·x(0)(cid:12)<δ, forallj =1,2,...,Nn. (15)
(cid:12) j j (cid:12)
Atlayer1,definethepre-activationfunctionas
ϕ(1)(x)=a cos(x)+b sin(x), i=1,2,...,Nn, j =1.
j,i ⃗ki ⃗ki
Thesingleneuronatlayer2is
Nn
x(2) =
(cid:88)(cid:16)
a cos(x(1))+b sin(x(1))
(cid:17)
.
1 ⃗ki i ⃗ki i
i=1
Using(12),(13),and(15),weget
(cid:12) (cid:12)
(cid:12) (cid:12)
(cid:12) (cid:12) (cid:12) x( 1 2)− (cid:88) (cid:16) a ⃗k cos(⃗k·x(0))+b ⃗k sin(⃗k·x(0)) (cid:17)(cid:12) (cid:12) (cid:12) < 2 ϵ .
(cid:12) ⃗k∈Zn (cid:12)
N
Finally,usingtheinequality(11),weconclude
10

(cid:12) (cid:12) ϵ ϵ
(cid:12)f(⃗x)−x(2)(cid:12)< + =ϵ,
(cid:12) 1 (cid:12) 2 2
Noticethatx(2) =KAN ◦KAN (x(0))bydefinition,wecompletetheproof.
1 1 0
A B C
D E F
Figure3: Fourier-seriesKANandtwo-layersMLPfitsixdifferentfunctions: A.Linearfunctiony =3x+5,K =200
inFourier-seriesKAN;B.Exponentialfunctiony = 3exp(1x), K = 120inFourier-seriesKAN;C.Logarithmic
2
functiony = 2log(x)+3,K = 100inFourier-seriesKAN;D.Polynomialfunctiony = 2x2−4x+1,K = 500
inFourier-seriesKAN;E.Sinfunctiony =2sin(3x)+1,K =100inFourier-seriesKAN;F.SinandCosfunction
y =3sin(x)+2cos(2x)+1,K =100inFourier-seriesKAN.
Incontrasttothemultilayerperceptron(MLP)approach,whichincreasesthenumberoflayerstoenhancethemodel’s
ability to fit the data, the Fourier KAN model enhances its fitting ability by adjusting the number of Fourier basis
functions(controlledbytheKparameter)andtheoptiontoincludeabiastermtodecomposecomplexfunctionsinto
simplersineandcosinewaveforms. Thisstrategicdecompositionnotonlyimprovesthemodel’sexpressivenessbutalso
reducesthecomputationalburden. Weevaluatedthefittingabilityoftwo-layersMLPandone-layerFourierseriesKAN
onsixdifferentfunctiontypes,andtheresultsareshowninFigure3. OuranalysisshowsthatFourierKANcapturesthe
underlyingpropertiesofthefunctionmoreskillfullyandexhibitssuperiorexpressiveness,especiallyintheabilitytofit
periodicfunctions.
3.2 BenchmarkDatasets
ForanextensivevalidationofourKA-GNNmodel,weusedsevenbenchmarkdatasetsfromMoleculeNet[47]. Three
datasetsarefromthebiophysicsdomain: MUV,HIV,andBACE.MUV,asubsetofPubChemBioAssayrefinedusing
nearestneighboranalysis,isdesignedforvalidatingvirtualscreeningtechniques. TheHIVdatasetmeasurestheability
of molecules to inhibit HIV replication. BACE includes both quantitative (IC50) and qualitative (binary) binding
resultsforinhibitorsofhumanβ-secretase1(BACE-1). Theremainingfourdatasetsarefromthephysiologydomain:
BBBP,Tox21,SIDER,andClinTox. BBBPcontainsbinarylabelsforblood-brainbarrierpenetration. Tox21provides
qualitativetoxicitymeasurementsfor12biologicaltargets. SIDERisadatabaseofmarketeddrugsandtheiradverse
drugreactions(ADRs),groupedinto27systemorganclasses. ClinToxincludesqualitativedataonFDA-approved
drugsandthosethatfailedclinicaltrialsduetotoxicity.
TheoriginaldatainthesedatasetsareSMILESstringsofthemolecules. Duringdatapreprocessing,weusetheMerck
molecular force field (MMFF94) function from the RDKit package to generate 3D molecular structures from the
SMILES strings. Based on the generated structures, we construct graphs for the GNN in our KA-GNN model to
predicttherelevantproperties. Forevaluation,weusetheReceiverOperatingCharacteristic-AreaUndertheCurve
(ROC-AUC)metric. Additionally,weemploythescaffoldsplittingmethod[57]todividethedatasetsintotraining,
validation,andtestsetsinaratioof8:1:1.
11

Table5: KA-GCNandKA-GATparametersfordifferentdatasets.
Dataset Model Batchsize LR K Layers Heads Epochs
BACE KA-GNN 128 1e-4 1 3 - 500
BACE KA-GAT 64 1e-4 2 2 4 500
BBBP KA-GNN 128 1e-4 2 1 - 500
BBBP KA-GAT 128 1e-4 5 2 2 500
ChinTox KA-GNN 128 1e-4 2 2 - 500
ChinTox KA-GAT 128 1e-4 5 2 2 500
SIDER KA-GNN 128 1e-4 2 1 - 500
SIDER KA-GAT 128 1e-4 4 2 2 500
Tox21 KA-GNN 512 1e-4 2 2 - 500
Tox21 KA-GAT 512 1e-4 3 2 2 500
HIV KA-GNN 512 1e-4 2 2 - 500
HIV KA-GAT 512 1e-4 2 2 4 500
MUV KA-GNN 512 1e-4 2 2 - 500
MUV KA-GAT 512 1e-4 3 2 4 500
3.3 BaselineModels
OurKA-GNNmodelhasbeenevaluatedalongsideaselectionofstate-of-the-artGNNarchitectures,includingbothpre-
trainedandnon-pre-trainedmodels. TheseencompassMPNNframeworkslikeD-MPNN[49],attention-drivenmodels
suchasAttentiveFP[48],andmulti-scaleapproachesexemplifiedbyMol-GDL[28]. Importantly,ourcomparisons
alsoextendtogeometry-focusedgraphmodelsthatleveragepre-training,includingN-Gram[50],PretrainGNN[51],
GROVER[26],GraphMVP[52],MolCLR[53],GEM[54],Uni-mol[55],SMPT[56],andGNN-SKAN[38]. Table5
isthehyperparameterssettingforvariousdatasets,includingmodeltype,batchsize,learningrate(LR),numberof
harmonics(K),numberofmessagepassinglayers,numberofattentionheads(forGAT),andnumberofepochs.
Table6: HyperparameterSensitivityAnalysisforKA-GNN.
Batchsize 64 128 256 512
BACE 0.887 0.890 - -
BBBP 0.696 0.787 - -
ChinTox 0.992 0.989 - -
SIDER 0.841 0.842 - -
Tox21 0.772 0.774 0.769 0.799
HIV 0.754 0.768 0.778 0.821
MUV 0.686 0.696 0.725 0.834
LR 1e-3 5e-4 1e-4 5e-5
BACE 0.806 0.818 0.890 0.858
BBBP 0.692 0.717 0.787 0.736
ChinTox 0.984 0.979 0.991 0.989
SIDER 0.831 0.837 0.842 0.835
Tox21 0.725 0.763 0.799 0.764
HIV 0.754 0.779 0.821 0.819
MUV 0.708 0.723 0.834 0.801
#Layers 0 1 2 3
BACE 0.674 0.719 0.822 0.890
BBBP 0.720 0.787 0.734 0.672
ChinTox 0.973 0.976 0.989 0.984
SIDER 0.838 0.830 0.842 0.829
Tox21 0.702 0.721 0.799 0.760
HIV 0.718 0.763 0.821 0.754
MUV 0.700 0.756 0.834 0.710
12

3.4 HyperparameterSensitivityAnalysis
Table6presentsananalysisofthesensitivityofvarioushyperparameters,includingbatchsize,learningrate(LR),and
networkdepth, ontheperformanceofmolecularpropertypredictionmodels. Theresultssuggestthatselectingan
optimalbatchsizeandalowerlearningratetendstoenhancemodelperformance. However,increasingthenumber
oflayersdoesnotconsistentlyyieldimprovementsandmayevenresultinoverfittingordiminishingreturns. These
findingshighlightthecriticalroleofhyperparametertuninginachievingoptimalmodelperformance.
4 Conclusion
Inthisstudy,weproposethefirstnon-trivialKolmogorov-ArnoldNetwork-basedGraphNeuralNetworks(KA-GNNs).
Our KA-GNNs utilize KAN’s unique power to optimize GNN architectures at three major levels, including node
embedding, message passing, and readout. We develop Fourier series-based KAN model and provide a rigorous
mathematicalproveoftherobustapproximationcapabilityoftheFourierKANarchitecture. Wecomparetheeffects
ofvariouspre-activationfunctionchoicesontheexpressivepoweroftheKANmodelintermsofmodelperformance
andcomputationalefficiency,identifyingFourierseriesastheoptimalpre-activationfunction. Basedonwidely-used
benchmarkdatasetsformolecularpropertyprediction,weextensivelycomparewithexistingstate-of-the-artmodels,
andfindthatourKA-GNNscanoutperformtraditionalGNNmodels. Thisworknotonlyhighlightsthegreatpower
ofKA-GNNsinmolecularpropertypredictionbutalsoprovidesanovelgeometricdeeplearningframeworkforthe
generalnon-Euclideandataanalysis.
References
[1] JamesPHughes,StephenRees,SBarrettKalindjian,andKarenLPhilpott. Principlesofearlydrugdiscovery.
Britishjournalofpharmacology,162(6):1239–1249,2011.
[2] YangZhang,CaiqiLiu,MujiexinLiu,TianyuanLiu,HaoLin,Cheng-BingHuang,andLinNing. Attentionisall
youneed: utilizingattentioninAI-enableddrugdiscovery. Briefingsinbioinformatics,25(1):bbad467,2024.
[3] HCSChan,HShan,TDahoun,HVogel,andSYuan. Advancingdrugdiscoveryviaartificialintelligence. Trends
inPharmacologicalSciences,40(8):592–604,2019.
[4] KACarpenterandXHuang. Machinelearning-basedvirtualscreeninganditsapplicationstoAlzheimer’sdrug
discovery: areview. CurrentPharmaceuticalDesign,24(28):3347–3358,2018.
[5] EHBMaia,LCAssis,TADeOliveira,AMDaSilva,andAGTaranto. Structure-basedvirtualscreening: from
classicaltoartificialintelligence. FrontiersinChemistry,8:343,2020.
[6] TZhao,YHu,LRValsdottir,TZang,andJPeng.Identifyingdrug–targetinteractionsbasedongraphconvolutional
networkanddeepneuralnetwork. BriefingsinBioinformatics,22(2):2141–2150,2021.
[7] JunXia,LechengZhang,XiaoZhu,YueLiu,ZhangyangGao,BozhenHu,ChengTan,JiangbinZheng,Siyuan
Li,andStanZLi. Understandingthelimitationsofdeepmodelsformolecularpropertyprediction: Insightsand
solutions. AdvancesinNeuralInformationProcessingSystems,36:64774–64792,2023.
[8] CDurán,SDaminelli,andJMThomas. Pioneeringtopologicalmethodsfornetwork-baseddrug–targetprediction
byexploitingabrain-networkself-organizationtheory. BriefingsinBioinformatics,19(6):1183–1202,2018.
[9] DucDuyNguyen,ZixuanCang,andGuo-WeiWei. Areviewofmathematicalrepresentationsofbiomolecular
data. PhysicalChemistryChemicalPhysics,22(8):4343–4367,2020.
[10] StephenBonneretal. Implicationsoftopologicalimbalanceforrepresentationlearningonbiomedicalknowledge
graphs. BriefingsinBioinformatics,23(5):bbac279,2022.
[11] ZMengandKXia. Persistentspectral-basedmachinelearning(PerSpectML)forprotein-ligandbindingaffinity
prediction. ScienceAdvances,7(19):eabc5329,2021.
[12] DDNguyenandGWWei. AGL-Score: AlgebraicGraphLearningScoreforProtein-LigandBindingScoring,
Ranking,Docking,andScreening. JournalofChemicalInformationandModeling,59(7):3291–3304,2019.
[13] NASzulc,ZMackiewicz,andJMBujnicki. Structuralinteractionfingerprintsandmachinelearningforpredicting
andexplainingbindingofsmallmoleculeligandstoRNA. BriefingsinBioinformatics,24(4):bbad187,2023.
[14] JChen,RWang,MWang,andGWWei. MutationsstrengthenedSARS-CoV-2infectivity. JournalofMolecular
Biology,432(19):5212–5226,2020.
13

[15] RWang,YHozumi,CYin,andGWWei. MutationsonCOVID-19diagnostictargets. Genomics,112(6):5204–
5213,2020.
[16] KGao,DDNguyen,MTu,andGWWei. Generativenetworkcomplexfortheautomatedgenerationofdrug-like
molecules. JournalofChemicalInformationandModeling,60(12):5682–5698,2020.
[17] Bo-WeiZhao,Xiao-RuiSu,Peng-WeiHu,Yu-PengMa,XiZhou,andLunHu. Ageometricdeeplearningframe-
workfordrugrepositioningoverheterogeneousinformationnetworks. BriefingsinBioinformatics,23(6):bbac384,
2022.
[18] PLi,YLi,andCYHsieh. TrimNet: learningmolecularrepresentationfromtripletmessagesforbiomedicine.
BriefingsinBioinformatics,22(4):bbaa266,2021.
[19] Xiao-Shuang Li, Xiang Liu, Le Lu, Xian-Sheng Hua, Ying Chi, and Kelin Xia. Multiphysical graph neural
network(MP-GNN)forCOVID-19drugdesign. BriefingsinBioinformatics,23(4):bbac231,2022.
[20] CKang, HZhang, andZLiu. LR-GNN:Agraphneuralnetworkbasedonlinkrepresentationforpredicting
molecularassociations. BriefingsinBioinformatics,23(1):bbab513,2022.
[21] HanxuanCai,HuiminZhang,DuanchengZhao,JingxingWu,andLingWang. FP-GNN:Aversatiledeeplearning
architectureforenhancedmolecularpropertyprediction. BriefingsinBioinformatics,23(6):bbac408,2022.
[22] Hui Liu, Yibiao Huang, Xuejun Liu, and Lei Deng. Attention-wise masked graph contrastive learning for
predictingmolecularproperty. BriefingsinBioinformatics,23(5):bbac303,2022.
[23] RZhang,YLin,andYWu. MvMRL:AMulti-ViewMolecularRepresentationLearningMethodforMolecular
PropertyPrediction. BriefingsinBioinformatics,25(4):bbae298,2024.
[24] RMercado,TRastemo,ELindelöf,GKlambauer,OEngkvist,HChen,andEJBjerrum. Graphnetworksfor
moleculardesign. MachineLearning: ScienceandTechnology,2(2):025023,2021.
[25] QLiu,MAllamanis,MBrockschmidt,andAGaunt. Constrainedgraphvariationalautoencodersformolecule
design. AdvancesinNeuralInformationProcessingSystems,31,2018.
[26] YRong,YBian,TXu,WXie,YWei,WHuang,andJHuang. Self-supervisedgraphtransformeronlarge-scale
moleculardata. AdvancesinNeuralInformationProcessingSystems,33:12559–12571,2020.
[27] MWang,ZCang,andGWWei. Atopology-basednetworktreeforthepredictionofprotein-proteinbinding
affinitychangesfollowingmutation. NatureMachineIntelligence,2(2):116–123,2020.
[28] CShen,JLuo,andKXia. Moleculargeometricdeeplearning. CellReportsMethods,3(11),2023.
[29] ZLiu,YWang,SVaidya,FRuehle,JHalverson,MSoljacˇic´,TYHou,andMTegmark. Kan:Kolmogorov-Arnold
networks. arXivpreprintarXiv:2404.19756,2024.
[30] RBresson,GNikolentzos,andGPanagopoulos. Kagnns: Kolmogorov-Arnoldnetworksmeetgraphlearning.
arXivpreprintarXiv:2406.18380,2024.
[31] BCKoenig,SKim,andSDeng. KAN-ODEs: Kolmogorov–ArnoldNetworkOrdinaryDifferentialEquationsfor
LearningDynamicalSystemsandHiddenPhysics. ComputerMethodsinAppliedMechanicsandEngineering,
432:117397,2024.
[32] MLiu, SBian, andBZhou. ikan: GlobalIncrementalLearningwithKANforHumanActivityRecognition
AcrossHeterogeneousDatasets. Proceedingsofthe2024ACMInternationalSymposiumonWearableComputers,
pages89–95,2024.
[33] RGenetandHInzirillo. Tkan: Temporalkolmogorov-arnoldnetworks. arXivpreprintarXiv:2405.07344,2024.
[34] MCheon. Kolmogorov-ArnoldNetworkforSatelliteImageClassificationinRemoteSensing. arXivpreprint
arXiv:2406.00600,2024.
[35] MKiamari,MKiamari,andBKrishnamachari. GKAN:GraphKolmogorov-ArnoldNetworks. arXivpreprint
arXiv:2406.06470,2024.
[36] ZBozorgaslandHChen. Wav-kan: Waveletkolmogorov-arnoldnetworks. arXivpreprintarXiv:2405.12832,
2024.
[37] TAhmedandMHRSifat.GraphKAN:GraphKolmogorovArnoldNetworkforSmallMolecule-ProteinInteraction
Predictions. InProceedingsoftheICML’24WorkshoponMachineLearningforLifeandMaterialScience: From
TheorytoIndustryApplications,2024.
[38] RuifengLi,MingqianLi,WeiLiu,andHongyangChen. GNN-SKAN:HarnessingthePowerofSwallowKANto
AdvanceMolecularRepresentationLearningwithGNNs. arXivpreprintarXiv:2408.01018,2024.
14

[39] AliKashefi. PointNetwithKANversusPointNetwithMLPfor3DClassificationandSegmentationofPointSets.
arXivpreprintarXiv:2410.10084,2024.
[40] ANKolmogorov. Ontherepresentationofcontinuousfunctionsofmanyvariablesbysuperpositionofcontinuous
functionsofonevariableandaddition. DokladyAkademiiNauk,114:953–956,1957.
[41] DASprecher. AnumericalimplementationofKolmogorov’ssuperpositions. NeuralNetworks,9(5):765–772,
1996.
[42] JBraunandMGriebel. OnaconstructiveproofofKolmogorov’ssuperpositiontheorem. ConstructiveApproxi-
mation,30:653–675,2009.
[43] LCarleson. OnconvergenceandgrowthofpartialsumsofFourierseries. ActaMathematica,116:135–157,1966.
[44] CFefferman. OntheconvergenceofmultipleFourierseries. BulletinoftheAmericanMathematicalSociety,
77:744–745,1971.
[45] TXieandJCGrossman. Crystalgraphconvolutionalneuralnetworksforanaccurateandinterpretableprediction
ofmaterialproperties. PhysicalReviewLetters,120(14):145301,2018.
[46] LLi,XiangLiu,andGWang. PathComplexNeuralNetworkforMolecularPropertyPrediction. InProceedings
oftheICML2024WorkshoponGeometry-groundedRepresentationLearningandGenerativeModeling,2024.
[47] ZWu,BRamsundar,ENFeinberg,JGomes,CGeniesse,ASPappu,KLeswing,andVPande. MoleculeNet: a
benchmarkformolecularmachinelearning. ChemicalScience,9(2):513–530,2018.
[48] ZXiong,DWang,XLiu,FZhong,XWan,XLi,ZLi,XLuo,KChen,HJiang,etal. Pushingtheboundariesof
molecularrepresentationfordrugdiscoverywiththegraphattentionmechanism. JournalofMedicinalChemistry,
63(16):8749–8760,2019.
[49] KYang,KSwanson,WJin,CColey,PEiden,HGao,AGuzman-Perez,THopper,BKelley,MMathea,etal.
Analyzing learned molecular representations for property prediction. Journal of Chemical Information and
Modeling,59(8):3370–3388,2019.
[50] SLiu,MFDemirel,andYLiang. N-gramgraph:Simpleunsupervisedrepresentationforgraphs,withapplications
tomolecules. AdvancesinNeuralInformationProcessingSystems,32,2019.
[51] WHu,BLiu,JGomes,MZitnik,PLiang,VPande,andJLeskovec. StrategiesforPre-trainingGraphNeural
Networks. InInternationalConferenceonLearningRepresentations,2019.
[52] SLiu,HWang,WLiu,JLasenby,HGuo,andJTang. Pre-trainingMolecularGraphRepresentationwith3D
Geometry. InInternationalConferenceonLearningRepresentations,2022.
[53] YWang,JWang,ZCao,andABFarimani. Molecularcontrastivelearningofrepresentationsviagraphneural
networks. NatureMachineIntelligence,4(3):279–287,2022.
[54] XiaominFang,LihangLiu,JieqiongLei,DonglongHe,ShanzhuoZhang,JingboZhou,FanWang,HuaWu,and
HaifengWang. Geometry-enhancedmolecularrepresentationlearningforpropertyprediction. NatureMachine
Intelligence,4(2):127–134,2022.
[55] GZhou, ZGao, QDing, HZheng, HXu, ZWei, LZhang, andGKe. Uni-Mol: AUniversal3DMolecular
RepresentationLearningFramework. TheEleventhInternationalConferenceonLearningRepresentations,2023.
[56] YLi,WWang,JLiu,andCWu. Pre-trainingmolecularrepresentationmodelwithspatialgeometryforproperty
prediction. ComputationalBiologyandChemistry,109:108023,2024.
[57] B. Ramsundar, P. Eastman, P. Walters, and V. Pande. Deep Learning for the Life Sciences: Applying Deep
LearningtoGenomics,Microscopy,DrugDiscovery,andMore. O’ReillyMedia,Inc.,Sebastopol,CA,1stedition,
2019.
15