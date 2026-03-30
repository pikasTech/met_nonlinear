KANELÉ: Kolmogorov–Arnold Networks for Efficient LUT-based
Evaluation
DucHoang∗ AarushGupta∗ PhilipHarris
dhoang@mit.edu aarushg@mit.edu pcharris@mit.edu
MassachusettsInstituteofTechnology MassachusettsInstituteofTechnology MassachusettsInstituteofTechnology
Cambridge,MA,USA Cambridge,MA,USA Cambridge,MA,USA
Kolmogorov-Arnold Kolmogorov-Arnold Quantization & Pruning Efficient LUT-based
Representation Theorem Network (KAN) implementation
x x
x x x x
Any multivariate continuous function 1 2 1 2 1 2
can be represented by a finite sum of
univaritate functions and additions.
f(x)=f(x
1
,⋯,x n)
2n+1 n
+ +
+ +
+
S
+
=
∑
Φq
∑
ϕ q,p(x p)
q=1 p=1
Where ϕ q,p:[0,1]→ℝ + + +
and Φq:ℝ→ℝ f(x ,x ) f(x 1 ,x 2 ) f(x ,x )
1 2 1 2
Figure1:FromtheKolmogorov-ArnoldRepresentationTheoremtoefficientKANFPGAinference.
Abstract CCSConcepts
Low-latency,resource-efficientneuralnetworkinferenceonFPGAs •Computingmethodologies→Machinelearningalgorithms;
isessentialforapplicationsdemandingreal-timecapabilityandlow •Hardware;
power.Lookuptable(LUT)-basedneuralnetworksareacommon
solution,combiningstrongrepresentationalpowerwithefficient Keywords
FPGAimplementation.Inthiswork,weintroduceKANELÉ,aframe- Kolmogorov–Arnold Networks (KANs), FPGAs, Lookup ta-
workthatexploitstheuniquepropertiesofKolmogorov–Arnold bles (LUTs), Neural networks, Quantization, Pruning, Hard-
Networks(KANs)forFPGAdeployment.Unliketraditionalmulti- ware–softwarecodesign
layerperceptrons(MLPs),KANsemploylearnableone-dimensional
ACMReferenceFormat:
splineswithfixeddomainsasedgeactivations,astructurenaturally
Duc Hoang, Aarush Gupta, and Philip Harris. 2026. KANELÉ: Kol-
suitedtodiscretizationandefficientLUTmapping.Wepresentthe
mogorov–ArnoldNetworksforEfficientLUT-basedEvaluation.InProceed-
firstsystematicdesignflowforimplementingKANsonFPGAs,
ingsofthe2026ACM/SIGDAInternationalSymposiumonFieldProgrammable
co-optimizingtrainingwithquantizationandpruningtoenable
GateArrays(FPGA’26),February22–24,2026,Seaside,CA,USA.ACM,New
compact,high-throughput,andlow-latencyKANarchitectures.Our York,NY,USA,12pages.https://doi.org/10.1145/3748173.3779202
resultsdemonstrateuptoa2700xspeedupandordersofmagni-
tuderesourcesavingscomparedtopriorKAN-on-FPGAapproaches. 1 Introduction
Moreover,KANELÉmatchesorsurpassesotherLUT-basedarchitec-
Lookuptable(LUT)basedneuralnetworkshavebecomeacen-
turesonwidelyusedbenchmarks,particularlyfortasksinvolving
tral paradigm for efficient FPGA inference, with designs such
symbolic or physical formulas, while balancing resource usage
as NeuralLUT-Assemble [6], TreeLUT [23], DWN [7], and oth-
acrossFPGAhardware.Finally,weshowcasetheversatilityofthe
ers[4,12,37,47]demonstratingdramaticgainsinarea,latency,
frameworkbyextendingittoreal-time,power-efficientcontrol
andpowerefficiency.Theseapproacheshighlighttheadvantages
systems.
ofrethinkingneuralnetworksaroundLUTprimitives,thoughthey
∗Bothauthorscontributedequallytothisresearch. remainlargelyconfinedtosupervisedlearningandtask-specific
architectures.
In this work, we demonstrate that Kolmogorov–Arnold Net-
ThisworkislicensedunderaCreativeCommonsAttribution4.0InternationalLicense. works(KANs)offeraprincipledfoundationforLUT-baseddesign.
FPGA’26,Seaside,CA,USA InspiredbytheKolmogorov–Arnoldrepresentationtheorem,KANs
©2026Copyrightheldbytheowner/author(s).
replacethefixedactivationsofMultilayerPerceptrons(MLPs)with
ACMISBN979-8-4007-2079-6/2026/02
https://doi.org/10.1145/3748173.3779202 learnableedgefunctionsandthematrixmultiplicationinMLPs
6202
beF
81
]RA.sc[
2v05821.2152:viXra

FPGA’26,February22–24,2026,Seaside,CA,USA DucHoang,AarushGupta,andPhilipHarris
withsummationatnodes(Fig.1).Thisactivation-centricformu- Sincetheirintroduction,KANshaveinspiredextensivefollow-up
lationalignsnaturallywithLUTs:eachlearnablesplinedefined work,includingtheoreticalanalyses[45,48],architecturalexten-
onafixeddomaincanbequantized,pruned,anddirectlymapped sions(e.g.,convolutional[9,15],temporal[18],andFourier-based
to LUTs. In the literature, although KANs have been shown to variants[21,49]),andapplicationsacrossscientificmodelingand
outperformMLPsinsettingssuchasPDEsolvingandscientific data-driventasks[13,19,25,46].
computing[27,28],theirpracticaldeploymenthasbeenhindered Despitethisrapidprogress,recentsurveysidentifycomputa-
byslowinferenceandcostlyhardwarerealizations[20,41].The tionalefficiencyandhardwareimplementationaskeyopenchal-
onlypriorFPGAimplementationconcludedKANswereimpractical, lenges[20,22,36].Todate,efficienthardwarerealizationremains
duetoexpensivesplineevaluationsandhighresourceusage[41]. largelyunexplored,withoneearlyattemptconcludingthatadirect
Thispapershowsthatbyre-formulatingKANinferenceentirely FPGAimplementationincursprohibitiveresourceandlatencycosts
intermsofLUTs,KANsarenotonlyfeasiblebuthighlyefficientin comparedtoMLPs[41].Ourworkdirectlychallengesthisconclu-
FPGAsettings.Thus,ourcontributionsarefourfold: sionbydemonstratingthattheactivation-centricdesignofKANsis,
infact,exceptionallywell-suitedforhardwareaccelerationthrough
(1) FPGA-tailoredKANArchitecture:WepresentKANELÉ,
aLUT-basedparadigm.
namedaftertheFrenchpastryknownforitscompactform
and rich structure [31]. At its core, the framework co-
optimizesquantization,pruning,andmappingofKANfunc-
2.2 LUT-basedNeuralNetworks
tionsontolearnedLUTsandadditions,therebyminimizing
memoryandlogicoverhead.FromaKANresearchperspec- LUT-basedneuralnetworksaimtoreplacearithmetic-heavyMAC
tive,KANELÉisthefirstFPGA-tailoredformulation,elimi- operationswithprecomputedfunctionevaluationsstoredinLUTs,
natingBRAM/DSPusage,reducinglatencybyupto2700×, exploitingtheabundantandlow-latencylogicresourcesofFPGAs.
andcuttingresourceusagebyover4000×comparedtoprior PioneeringframeworkslikeLUTNet[44]andLogicNets[42]first
designs[41]. demonstratedthereplacementofarithmeticwithdirectLUTmap-
(2) High-Performance Realizations: Unlike conventional pings.Subsequentworksgeneralizedthisconcepttoapproximate
LUT-basedneuralnetworks,wheresequentialLUTindexing morecomplexfunctions[4,5]andimprovedscalabilityusingaddi-
makespruningfundamentallyincompatiblewiththemodel tiveormodularensembles[6,30,47].Thisdesignphilosophyhas
structure,KANELÉleveragestheadditiveindependenceof alsobeenusedtoefficientlyimplementothermachinelearningmod-
KANstomakepruningbothnaturalandhardwareefficient. els,suchasgradient-boosteddecisiontrees[23].Anotherrelated
Buildingonthisarchitecture,KANELÉdeliversFPGAimple- approachisthefamilyofWeightlessNeuralNetworks(WNNs),
mentationsthatmatchorsurpassotherLUT-basedneuralde- whichstoreslearnedpatternsdirectlyinLUTs[3,7,32,38,39],
signs,particularlyfortaskswell-suitedtosymbolicmapping. thoughoftenatthecostofrepresentationalpower.
It sustains clock frequencies above 800MHz across most Conceptually,KANsareclosetoPolyLUT[4],PolyLUT-Add[30],
benchmarkswhileachievingastate-of-the-artArea×Delay andDWNs[7]butpossessdistinctstructuralproperties.WhilePoly-
productandmaintainingabalancedresourcefootprint. LUTtabulatesmultivariatepolynomials,whichtheoreticallyallows
(3) Open-sourceFramework:Weprovideanautomatedsoft- thenativerepresentationofarbitraryproducts𝑝(x)=(cid:206) 𝑖 𝑥 𝑖,this
ware–hardwareco-designflowthatcompilesKANsintoop- approachsuffersfromexponentialLUTgrowthrelativetoinput
timizedFPGAimplementationswithinseconds,supporting dimension.Incontrast,KANsdecomposefunctionsintosumsof
reproduciblestudiesacrossdomainssuchasbiology,physics, tabulatedunivariatesplines.Althoughthisformulationrelieson
vision,signalprocessing,andtabularML.Codeisavailable layercompositiontoapproximatethemultiplicativetermsinherent
at:https://github.com/Duchstf/KANELE toPolyLUT,ityieldslinearscalingwithinputdimensionandan
(4) ControlSystems:weextendKANELÉbeyondsupervised additivestructurethatisnaturallyamenabletopruning.Whilethis
learningtocontinuouscontrol,showingontheHalfCheetah formulationdoesn’texplicitlyrepresentpuremultiplicativeterms,
benchmarkfromOpenAIGym[40]thataquantizedKAN inpractice,compositionsoflow-order(≤3)splinesapproximate
policywith∼ 5×fewerparametersthananMLPbaseline suchinteractionseffectively.Moreover,DWN’sfullbinarizationof
policyachieveshigherrewards,underscoringitssuitability inputsandLUTshindersgeneralizationbeyondclassification,while
forresource-constrained,real-timecontrolsystems. KANELÉsupportshigher-precisionarithmeticfortaskssuchasau-
toencodingandcontinuouscontrol.Finally,DWN’sfinite-difference
2 Background&RelatedWorks differentiabilitymayfurtherconstrainoptimizationflexibilitycom-
ThissectionreviewsKolmogorov–ArnoldNetworks(KANs)and paredtoKANELÉgradientdescent.
priorworkonLUT-basedneuralnetworkinference.
2.1 Kolmogorov–ArnoldNetworks 3 KANArchitectureandQuantization-Aware
TrainingandPruning
Kolmogorov–ArnoldNetworks(KANs)replacethefixedactivation
functionsandmatrixmultiplicationsofMLPswithlearnablespline- WedesigntheKANELÉframeworkforKANFPGAdeployment
basedfunctionsonnetworkedges[28].Thisactivation-centricfor- usingquantization-awaretrainingandpruning,enablingefficient
mulationimprovesexpressivenessandinterpretability,oftenachiev- hardwaretranslationwhilepreservingconsistencybetweentrain-
ingcomparableaccuracywithfewerparametersandoperations. ingandinference.

KANELÉ:Kolmogorov–ArnoldNetworksforEfficientLUT-basedEvaluation FPGA’26,February22–24,2026,Seaside,CA,USA
3.2 Quantization-AwareTraining
ForefficientFPGAdeployment,weadoptquantization-awaretrain-
ing(QAT)viaAMD’sBrevitaslibrary[17].Quantizersareplaced
atthenetworkinputandaftereachKANlayer,ensuringthattrain-
ingadaptstotherequiredhardwareprecision.
ϕ(x) = ∑ i= 4 0 c i B i(x) Foralayer𝑙 withoutp x u 𝑙+ t 1 x ,𝑞 𝑙+ = 1 ∈ 𝑞 𝑙 R (x 𝑑 𝑙 𝑙 + + 1 1 ) , , thequantizedoutputis (6)
where𝑞 𝑙(·)isthelayerquantizer.Similarly,aninputquantizer𝑞 𝐼(·)
+ + +
B 0(x) B 1(x) B 2(x) B 3(x) isappliedtox 0 .
Thelayeroutputquantizerperforms𝑛 𝑙-bituniformquantization:
a b x𝑙+1,𝑞 =𝑠 𝑙 ·Quantize[𝑛 𝑙]
(cid:18) clip(x𝑙
𝑠 +1
,𝑎,𝑏)(cid:19)
, (7)
𝑙
Figure2:AKANactivation𝜙(𝑥)representedasalinearcom- where𝑠 𝑙 isalearnablescale(fixedatinference),and [𝑎,𝑏] isthe
binationofB-splinebasisfunctions𝐵 𝑖(𝑥)onagridover[𝑎,𝑏]: sharedquantizationdomain(Fig.3).
𝜙(𝑥)=(cid:205) 𝑖 𝑐 𝑖 𝐵 𝑖(𝑥).Trainablecoefficients𝑐 𝑖 controltheoverall Theinputquantizerincorporatesbothscale𝑠 𝐼 andbias𝑏 𝐼 to
functionshape. handleasymmetricdistributions:
(cid:18) clip(x ,𝑎,𝑏) (cid:19)
x 0,𝑞 =𝑠 𝐼 ·Quantize[𝑛 𝐼] 𝑠 0 +𝑏 𝐼 . (8)
𝐼
3.1 KANArchitecturewithLearnable
DuringRTLgeneration,𝑠 𝐼 and𝑏 𝐼 arefixedfordeterministicbehav-
ActivationFunctions
ior.
Beforeintroducingquantizationandpruning,wefirstoutlinethe Inpractice,inputpreprocessingisrealizedbyabatchnormal-
core architecture. Unlike MLPs, KANs replace fixed nonlineari- ization(zeromean,unitvariance)followedbyaScalarBiasScale
tieswithlearnableactivationfunctions,eachmodeledasalinear blockintroducing𝑏 𝐼 and𝑠 𝐼.Atinference,BNstatisticsarefolded
combinationofB-splinebasisfunctionswithtrainablecoefficients. intotheseconstants,yieldinganaffineshift–scale,clipping,and
B-splinesarepiecewisepolynomialsdefinedonagrid,providing quantization.ThisdesignpreservesLUT-basedcompatibilitywhile
smoothness,locality,andefficientnonlinearparameterization.More avoidingtheoverheadoffullbatchnormalization.
generally,activationscanbeexpressedinotherorthogonalbases, Duringtraining,quantizergradientsareapproximatedusingthe
suchasFourierseries[21,26,49]. straight-throughestimator(STE):
AKANlayerwith𝑑 in inputsand𝑑 out outputsisrepresentedasa 𝜕𝑞(𝑥)
matrixof1Dlearnablefunctions 𝜕𝑥 ≈1, (9)
Φ={𝜙 𝑞,𝑝}, 𝑝 =1,...,𝑑
in
, 𝑞=1,...,𝑑
out
, (1) whichallowsgradientflowthroughquantizedoperationswithout
modification.
whereeach𝜙 𝑞,𝑝 istrainable(Fig.2).
Forimprovedconvergence,each𝜙 𝑞,𝑝 combinesabaseactivation 3.3 PruningviaNorm-BasedSelection
𝜙(·)withB-splines{𝐵 𝑝,𝑘(·)}:
Toreduceresourceusage,weprunesplineconnectionsbyeval-
𝐺+𝑆 uating their contribution over the input domain. In contrast to
𝜙 𝑞,𝑝(𝑥 𝑝)=𝑤 𝑞 b , a 𝑝 se𝜙(𝑥 𝑝)+ ∑︁ 𝑤 𝑞 sp ,𝑝 li , n 𝑘 e𝐵 𝑝,𝑘(𝑥 𝑝), (2)
𝑘=1
where𝑤
𝑞
b
,
a
𝑝
seand𝑤
𝑞
sp
,𝑝
li
,
n
𝑘
earetrainable.Splinesaredefinedonagrid
ofsize𝐺 andorder𝑆withinafixeddomain[𝑎,𝑏].
b
Given𝑥 𝑙 ∈R𝑑 in,theoutputis
∑︁
𝑑𝑙
(𝑥 𝑙+1 )𝑗 = 𝜙 𝑗,𝑖(𝑥 𝑙,𝑖), 𝑗 =1,...,𝑑 𝑙+1 , (3)
𝑖=1
orincompactform
𝑥 𝑙+1 =Φ 𝑙(𝑥 𝑙), (4)
withΦ 𝑙 thefunctionmatrixoflayer𝑙.A𝐿-layerKANisthus a q l−1 (x l,2 bits) b
KAN(𝑥)=Φ 𝐿−1 ◦Φ 𝐿−2 ◦···◦Φ 0 (𝑥). (5)
AsillustratedinFig.1,KANsextendMLPsbylearningactivations
directly,offeringgreaterrepresentationalflexibilitywhilepreserv-
ingastructured,layer-wisegraph.
)stib
3,
1+l
x(l
q
Figure3:Layer-wiseuniformquantization.Here,2-bitinputs
𝑞 𝑙−1 (𝑥 𝑙) are mapped to 3-bit outputs𝑞(𝑥 𝑙+1 ) over the fixed
range[𝑎,𝑏].Orangemarkersindicatequantizationlevels;the
dottedcurveistheunderlyingcontinuousmapping.

FPGA’26,February22–24,2026,Seaside,CA,USA DucHoang,AarushGupta,andPhilipHarris
conventionalLUT-basedneuralnetworks—whichrelyonsequen-
KAN
tial LUT indexing, making every LUT entangled with the next
Parameters
andthusnearlyimpossibletoprunewithoutbreakingthemodel—
KANELÉexploitstheinherentlyadditivestructureofKANs,where
eachLUTcontributesindependentlytoasummation.Thisinde-
pendencemakespruningbothmathematicallynaturalanddirectly KAN Generation Training
compatiblewithFPGAhardware.TheoriginalKANpaperempha- (PyTorch) parameters Dataset
sizesefficientpruningasakeyadvantageofKAN’sedge-centric
architecture,andweextendthisinsighttodemonstrateadistinct
advantageovernode-basedLUTnetworksforefficienthardware
translation[28].
Quantization-aware
Foreachpair(𝑖,𝑗)ofinputandoutputneurons,wecomputethe
training and pruning
+ + + +
activationofthesplinecomponent:
(Pytorch)
𝐺+𝑆 … …
𝑓 𝑝→𝑞(𝑥)= ∑︁ 𝑤
𝑞
sp
,𝑝
li
,
n
𝑘
e𝐵 𝑝,𝑘(𝑥). (10)
𝑘=1
11 x y
Itsimportanceismeasuredviatheℓ 2 normacrossasampledinput Learned activations 10 00 1010
gridXconsistentwithitsquantizationlevel: to lookup tables y 01 01 1111
(cid:32) (cid:33)1/2 representation 10 0000
∥𝑓 𝑝→𝑞∥ 2 = ∑︁(cid:12) (cid:12) 𝑓 𝑝→𝑞(𝑥) (cid:12) (cid:12) 2 . (11) 00 x 11 0001
𝑥∈X
Astructuredpruningmaskisthenapplied:
RTL Testbench Systhesis and place &
(cid:40)
𝑚 𝑞,𝑝 =
1, ∥𝑓 𝑝→𝑞∥
2
>𝜏(𝑡),
(12)
(Vivado xsim) route (Vivado)
0, otherwise,
where𝜏(𝑡) isapruningthresholdthatchangesasafunctionof Functional simulation
epochs(𝑡)with
results
Bitstream
(cid:18) max(𝑡,𝑡 )(cid:19)
𝜏(𝑡)=𝑇exp −ln20· 0 .
𝑡
𝑓
−𝑡
0
Figure4:VisualizationoftheKANtoFPGAimplementation
Thispruningthresholdcorrespondstoanexponentialwarmup,
wherepruningstartsonepoch𝑡 andincreasesexponentially,hit- toolflow.
0
ting95%ofthefullpruningthreshold𝑇 ontargetepoch𝑡 𝑓.This
allowsustocontrolpruningdynamicstoavoidinterferencewith
4.1 Toolflow
propertraining.Backwardpruningisadditionallyappliedifthe
corresponding output neuron has no active connections in the Ahigh-leveloverviewofthetoolflowstagesisshowninFigure
subsequentlayer,ensuringconsistentsparsitypropagation. 4.Thispush-buttonworkflowremovesmanualRTLwork:start-
ingfromatrainedPyTorchcheckpoint,itdeterministicallyemits
3.4 KANHyperparameters RTL,memoryimages,andbuild/simulationscripts,enablingrapid
Tosummarize,thetraininganddeploymentofKANsinvolveshy- deploymentofarbitraryKANtopologiestoFPGAandbitstream
perparameterswhichcanbebrokenupintothreemainclasses: generationviaVivado.
splinerepresentationhyperparameters,hardwarearchitecturehy-
4.1.1 Training. ThetrainingprocessbeginsbyspecifyingtheKAN
perparameters,andpruninghyperparameters.Thedescriptionsand
hyperparameters(seeSection3.4)togetherwiththedatasettobe
impactofeachhyperparameteraredetailedinTable1.Thejoint
used.Theusermayfreelyselecttheoptimizerandlearning-rate
optimizationoftheseparametersprovidesaflexibledesignspace
schedulebestsuitedtotheirtask.Inourimplementation,weadopt
thatbalanceslearningcapacitywithhardwareefficiencyinFPGA
thePyTorchAdamWoptimizer[29]asthedefaultchoiceduetoits
deployments.
robustnessinhandlingweightdecay.Themodelisthentrained
withtheQATandpruningmechanismdescribedinSection3.2
4 LUT-BasedKANArchitecture
andSection3.3,respectively,toreduceresourceusageandlatency,
Thissectionoutlinesourend-to-endmappingoftrainedKANsto
whilepreservingaccuracy.Thisstepproducescompactlearned
synthesizableVHDLRTLandassociatedpipeliningstrategies.Our
activationsforKANthatcanbeefficientlymappedtoLUTrepre-
end-to-endtoolflowcurrentlysupportsthebasicKANarchitecture
sentationsforFPGAdeployment.
usingB-splines,asintheoriginalpaper[28].Extensionstoother
basesorarchitecturessuchasconvolutionsortransformersare 4.1.2 KANtoLogical-LUTsConversion. Following[6],wedenote
feasible.Theframeworkisdesignedforusability—anyonefamiliar lookuptablesextractedfromthenetworkasLogical-LUTs(L-LUTs),
withtrainingMLPscanreadilytrainanddeployKANELÉ. and FPGA fabric resources as Physical-LUTs (P-LUTs). From a

KANELÉ:Kolmogorov–ArnoldNetworksforEfficientLUT-basedEvaluation FPGA’26,February22–24,2026,Seaside,CA,USA
Table1:SummaryofKANtrainingparameters.Thefirstgroupinfluencestheaccuracythroughsplinerepresentation,the
secondgroupencodesthehardwarearchitecture,andthethirdgroupdeterminespruningpolicywhichaffectshardware
architecture.
Symbol Description Impact
𝐺 Gridsize(numberofintervals) Controlssplineresolution;accuracyonly
[𝑎,𝑏] Gridrange(splinedomain) Definessupportofbasisfunctions;accuracyonly
𝑆 Splineorder Smoothnessandflexibility;accuracyonly
𝑑 𝑙 Layerdimensions Affectsmodelcapacityandresourceusage
𝑛 𝑙 Layerbitwidth(QATprecision) Directtrade-offbetweenaccuracyandresourcecost
𝑇 Pruningthreshold GovernssparsityandLUTreductionandaccuracytradeoff
𝑡 Warmupstartepoch Determineswhenpruningwarmupstarts
0
𝑡 𝑓 Warmuptargetepoch Affectspruningwarmuprate
trained,pruned,andquantizedPyTorchKAN,eachsurvivingcon-
nectionistranslatedintoanL-LUT.Foreveryactiveedge,theinput
statespaceisenumeratedandtheKANlayer’spre-activationre-
sponseisevaluatedandquantized.Thisproducesper-connection
truthtablesstoredascompactJSONfiles,yieldingadeterminis-
tic,bit-accuratemappingofthemodelintointeger-valuedL-LUTs.
Therepresentationpreservesquantizationandsparsity,enabling
efficientFPGAdeployment.
4.1.3 RTLFileGeneration. FromtheL-LUTgraph,wegeneratea
completeRTLdesignforFPGAdeployment.ThetoolemitsVHDL
sourcesfortheKANcore,per-layerpackages,LUTentities,and
memoryinitializationfilesencodingthetruthtables.Aconfigu-
rationpackagespecifiesbitwidths,signaltypes,andaccumulator
sizes.EachL-LUTisinstantiatedasamemory-mappedcomponent,
organizedintolayers,withbalancedaddertreesforoutputaccu-
mulation.Pipelineregistersareinsertedbetweenlayerstoimprove Figure5:Balanced,pipelinedaddertreeforcomputingone
clockingandshortencriticalpaths.Theresultisaself-contained neuronactivationwith𝑛 𝑎𝑑𝑑 =2.
firmwarebundlethatincludessimulationtestbenches,initialization
vectors,andVivadobuildscripts—supportingfunctionalsimulation,
latencyevaluation,andFPGAsynthesis. introducepipeliningattwolevels:(i)withinaddertreesthataccu-
mulateoutputsofmultipleLogical-LUTs(L-LUTs)perchannel,and
(ii)betweenconsecutivenetworklayers.
4.1.4 SynthesisandPlace&Route. Wesynthesizethegenerated
RTLwithVivado 2024.1,targetingthexcvu9p-flgb2104-2-i AdderTreePipelining. Eachneuroncomputesaweightedsum
FPGA for benchmarking against LUT-based networks, and the ofactiveinputsviaareductiontreeoverL-LUToutputs.Anaïve
xczu7ev-ffvc1156-2-e FPGA for comparison with prior KAN single-stagesumcreatesalongcombinationalpath,therebylimiting
works.Toensurefairnessandconsistencywithpriorworks,we frequency.Instead,weimplementabalanced,pipelinedaddertree
usesettingsthatisolatecoredelayandarea,specificallyVivado’s withregistersaftereachstage.Ateachstageupto𝑛 inputsare
add
Flow_PerfOptimized_highmodewithOut-of-Contextsynthe- combined,reducingfan-inanddistributingadditionsovermultiple
sis,allowingeachmoduletobecompiledindependently.Whilethe cycles.Thedepthis
maximumclockisultimatelylimitedbytheFPGA’sglobalclock, (cid:108) (cid:109)
LUT-centricdesignssuchasKANELÉtypicallysustainhighfre- depthℓ = log𝑛 (𝑁 ℓ) ,
add
quencies,makingthecomputationalcoreunlikelytobethecritical
asshowninFigure5for𝑛 = 2.Attheendoftheaddertree,
pathinlargersystems.Thetargetclockperiodisthereforechosen add
quantization and saturation of the sum are performed to make
relativetonetworksize,followingpriorwork.
theoutputconsistentwiththesubsequentlayer’sinput.Thisis
takenintoaccountduringtraining,preventinganydegradationin
4.2 PipeliningStrategies accuracy.
EfficientpipeliningiscrucialforachievinghighFPGAclockfre- Inter-Layer Pipelining. Pipeline registers are also inserted be-
quencieswhilemaintaininglowlatencyacrossKANlayers.We tweenlayers,capturingsaturatedoutputsbeforefeed-forward.This

FPGA’26,February22–24,2026,Seaside,CA,USA DucHoang,AarushGupta,andPhilipHarris
isolatesLUTevaluation,summation,andactivationintime,min- cars.Anautoencoderistrainedonslidingwindowsofthe
imizingcriticalpathsandbalancinglatency.Registerinsertionis downsampledmelspectrogram(inputsize64).Forclassifica-
automatedinRTLgeneration,ensuringdeeppipeliningforarbi- tion,themeanreconstructionlossacrossallslidingwindow
traryKANtopologies. spectrogramsofanaudiofileiscomputed,andafixedthresh-
oldisappliedtolabelthesampleasananomaly.Notably,
Limitations. AsaLUT-basedmodel,KANinheritsknownlimita-
thisbenchmarkpresentssignificantlymorecomplexinputs
tions.LUTsizescalesexponentiallywithinputbitwidth,though
comparedtotheLUT-NNandKAN-FPGAbenchmarkswhile
onlylinearlywithfan-in[4,5].Forhigh-dimensionalinputs,pre-
alsoutilizinganon-classificationobjective(reconstruction
serving KAN’s structure requires long adder chains, reducing
loss).[8].
throughput and increasing resource usage. Adder trees sustain
These datasets span a spectrum of complexity, from low-
highclockfrequenciesbyaddingpipelinestages,atthecostof
dimensionaltoydatasets(Moons)tohigh-dimensionalreal-world
extraclockcycles.Thus,imagetaskslikeMNISTrequireaggressive
data(JSC,MNIST,ToyADMOS),ensuringthatboththerepresenta-
pruningtoremainresource-feasible,withsomeaccuracyloss.
tionalcapacityandhardwareefficiencyofKANELÉarethoroughly
5 ExperimentalResults evaluated.
5.1 Benchmarks 5.2 TrainingParameters
We evaluate KAN across three domains of datasets: (i) widely KANhyperparametersarestraightforwardtomanage.Thespline-
adoptedbenchmarkdatasetsfromtheLUT-basedneuralnetwork relatedparameters(𝐺,[𝑎,𝑏],𝑆)onlyaffectaccuracyandcanoften
literature,(ii)syntheticandtabulardatasetspreviouslyusedinKAN be set to robust defaults since they do not impact hardware re-
FPGAbenchmarking[41],and(iii)MLPerfTinydatasets,which sources.
providereal-worldtaskswithmorecomplexmodalitiesandobjec- Inpractice,balancingmodelperformancewithhardwareeffi-
tives.Together,thesedomainsformadiversetestbedtostudyKAN ciencycentersontuningthreekeyparameters:thelayerdimensions
acrossdifferenttasksandlevelsofcomplexity.Belowwebriefly (𝑑 𝑙),bitwidth(𝑛 𝑙),andpruningthreshold(𝑇).Thesedirectlycontrol
describeeachdataset. themodel’scapacity,numericalprecision,andsparsity.Asdemon-
stratedinTable2,thisallowsthequantizedandprunedKANsto
5.1.1 LUT-basedNeuralNetworkBenchmarks.
achievecompetitiveaccuracy—evenoutperformingfloating-point
• MNIST:Alarge-scalehandwrittendigitrecognitiondataset
versionsondatasetslikeWine(98.2%)—whilebeingoptimizedfor
containing 60,000 training and 10,000 test images of size
anefficientFPGAimplementation.
28×28,labeledacross10classes(digits0–9)[14].
• JSCOpenML:Atabulardataset[11]fromtheJSCsuite,con- 5.3 ComparisonwithLUT-NNArchitectures
sistingof16jetsubstructureinputfeaturesanda5-classjet
WebenchmarkedKANELÉagainststate-of-the-artLUT-basedar-
classificationtask.Ithasbeenwidelyusedincomparisons
chitecturesonthreedatasets:JSCCERNBox,JSCOpenML,and
ofLUT-basednetworks.Thisversioncontains830,000in-
MNIST(Table3).Itshouldbenotedthat,asdetailedinTable2,we
stancesandisknowntoexhibiteasierconvergence,possibly
assumethesameinputbitwidthcomparedtopriorworks,which
duetoimproveddatacuration[6].
isnotthecaseforDWN[7]thatusesathermometerencodingto
• JSCCERNBox:Anotherdataset[34]fromtheJSCbench-
assigndistinctfloating-pointthresholdstoeachfeature,leadingto
mark, involving the same jet tagging task. It comprises
potentiallylargeoverhead.
986,806instancesandisgenerallyconsideredmorechalleng-
ing,asmodelstrainedonittendtoachieveloweraccuracies JSC CERNBox. On the more difficult JSC CERNBox dataset,
duetotheincreaseddatasetcomplexity. KANELÉachievesthehighestaccuracy(75.1%),tyingwithNeural-
LUTwhilealsousing18×lessLUTsandtwoordersofmagnitude
5.1.2 KANFPGABenchmarks.
fewerresources.Comparedtothebestpriormodelwhenconsid-
• Moons:Asynthetictwo-classdataset[35]commonlyused
eringresources,NeuralLUT-Assemble,weobtainslightlyhigher
fortestingnonlineardecisionboundaries.Eachpointlies accuracywith1.7×fewerLUTs,over2.4×higher𝐹 ,andthe
max
in one of two interleaving half-moon shapes with added lowestArea×Delayproduct(4.1×104).Incontrast,alternatives
Gaussiannoise.
suchasAmigoLUT,PolyLUT,andLogicNetsconsumeanorderof
• Wine:AdatasetfromtheUniversityofCalifornia,Irvine magnitudemoreLUTs,sufferloweraccuracy,orarelimitedto𝐹
max
(UCI)MachineLearningRepository[2],containing13physic-
inthe200–500MHzrange.Overall,KANELÉsitsonthePareto
ochemicalattributesofwinesamplesclassifiedinto3quality
frontierofaccuracyversusefficiency,establishingitasthemost
categories.
efficientsolutionforthistask.
• DryBean:AnotherUCIdataset[1]with16numericalfea-
turesrepresentingbeanshapeandtexture,usedforclassify- JSCOpenML. OntheeasierJSCOpenMLdataset,mostneural
ing7differentbeanvarieties. networksplateauaround76%accuracy.KAN-LUTreachesthislevel
(76.0%)whileusingonly1232LUTs—thefewestamongallmodels
5.1.3 MLPerfTinyBenchmarks. andupto51×fewerthanthehls4mlimplementation.Compared
• ToyADMOS:Anaudioanomalydetectiondatasetfeaturing to NeuralLUT-Assemble, KAN-LUT requires 1.44× fewer LUTs
soundfilesfrombothnormallyfunctioninganddefectivetoy andachievesaslightlyhigher𝐹 (987vs.941MHz),thoughits
max

KANELÉ:Kolmogorov–ArnoldNetworksforEfficientLUT-basedEvaluation FPGA’26,February22–24,2026,Seaside,CA,USA
Table2:AccuracycomparisonofMLPFloatingPointandKANFloatingPointandQuantizedmodelsonbenchmarkdatasets.
Allmodelshavethesamedimensionslisted.Thefloatingpointversionsonlyusethelayersize(𝑑 𝑙)parameter.
Accuracy(%)/AUC
Datasets 𝐺 [𝑎,𝑏] 𝑆 𝑑 𝑙 𝑛 𝑙 𝑇
MLPFP KANFP KANQuantized&Pruned
KANFPGABenchmarks[41]
Moons 6 [-8,8] 3 [2,2,1] [6,5,8] 0. 87.2 97.7 97.4
Wine 6 [-8,8] 3 [13,4,3] [6,7,8] 0. 96.3 98.1 98.2
DryBean 6 [-8,8] 3 [16,2,7] [6,6,8] 0. 90.9 92.2 92.1
LUT-basedneuralnetworkbenchmarks
MNIST 30 [-8,8] 3 [784,62,10] [1,6,6] 1. 96.7 97.9 96.3
JSCCERNBox 30 [-2,2] 10 [16,12,5] [8,8,6] 0.14 73.0 75.1 75.1
JSCOpenML 40 [-2,2] 10 [16,8,5] [6,7,6] 0.9 76.5 76.5 76.0
MLPerfTinyBenchmark
ToyADMOS 30 [-2,2] 10 [64,16,8,16,64] [7,8,8,7,8] 0.9 0.80 0.83 0.83
longer latency (7.1ns vs. 2.1ns) results in a larger Area×Delay. Theresults,detailedinTable4,demonstratethatKANELÉoffers
Othernetworksachievemarginallyhigheraccuracy,butonlyatthe adramaticimprovementinhardwareefficiencyandperformance
costofsubstantiallygreaterresourceusageandlatency.Overall, whilemaintainingorexceedingtheaccuracyofthepreviouswork.
KAN-LUToffersoneofthebesttrade-offsbetweenaccuracyand Through its LUT-based approach, our implementation com-
efficiencyonthistask. pletelyeliminatestheneedforBRAMandDSPblocks,whichare
heavilyutilizedintheimplementationbyTranetal.Thisleadstoa
MNIST. On the MNIST dataset, KANELÉ achieves a high ac- massivereductionintheoverallhardwarefootprint.Forinstance,
curacyof96.3%,thoughsomespecializedmodelslikeNeuraLUT- ontheDryBeandataset,KANELÉusesonly402LUTsand471FFs,
AssembleandDWNreachcloseto98%.Intermsofhardwarere- whereasthepreviousworkconsumesover1.6millionLUTsand
sources, DWN is the most compact with 2092 LUTs. KANELÉ, 734,000FFs—areductionofmorethan4000xinLUTs.
with3809LUTs,isstillsignificantlymoreefficientthanthema- KANELÉalsoachieveshighmaximumfrequencies(upto1736
jorityofotherhigh-accuracymodels.Forinstance,itusesover20 MHz)andverylowlatencies.OntheDryBeanbenchmark,forexam-
timesfewerLUTsthanPolyLUT(75131LUTs)whileachievingonly ple,ourmodel’slatencyis7.1ns,aspeedupofover2600xcompared
2% lower accuracy. Architectures like NeuraLUT-Assemble and tothe18,960nsreportedbyTranetal.Consequently,KANELÉ
TreeLUTexcelinlatency(2.1nsand2.5ns)andachievethebest achievesanexcellentArea×Delayproductacrossallbenchmarks.
Area×Delayproducts.Thissuggeststhatthearchitecturalpriors
ofthesespecializedmodelsmaybebetteralignedwiththespatial
structureinherentinimagedatathanthefunction-approximation
paradigmofKANs.Consequently,extendingKANELÉtowardcon-
5.5 Comparisonwithhls4mlMLPerfTiny
volutionalarchitecturesappearstobeapromisingdirectionfor
futureworkonimage-basedtasks. To understand the performance of KANELÉ on more complex
Insummary,KANELÉconsistentlydemonstratesanexceptional datasets,wecomparetheframeworktohls4ml[10]ontheToyAD-
trade-offbetweenpredictiveaccuracyandhardwareresourceuti- MOSdataset,partoftheMLPerfTinybenchmarksuite.OtherLUT-
lizationacrossdifferentbenchmarks.KANachievesanefficient basedneuralnetworkshavenotattemptedthisbenchmark,possibly
balanceofFPGAresourcesbyleveragingbothLUTsandFFsina duetoitshighcomplexityand/ornon-classification-basedtrain-
complementarymanner.Itparticularlyexcelsincomplex,resource- ingscheme.TheresultsinTable5indicatethatKANELÉachieves
intensivetasksliketheJSCCERNBoxbenchmark,whereitsetsa substantiallybetterperformancethanpriorapproachesintermsof
newstate-of-the-artintermsoftheArea×Delayproduct.Basedon bothresourceefficiency,latency,andpower.Theseimprovements
thenatureofthesedatasets,itcanalsobeinferredthatKANELÉ highlightthepotentialofKANELÉforfuturestudiesinvolvingmore
isbettersuitedfortasksinvolvingsymbolicorphysicalformulas complexdatasetsaswellastasksbeyondclassification.Specifically,
betweentheinputandoutputs(e.g.,JSCvariants),whichnaturally KANELÉeliminatestheneedforBRAM,LUTRAM,andDSPs,while
alignswiththeKolmogorov-Arnoldrepresentationtheorem. reducingLUTusageby41.7%andFFusageby71.4%relativeto
hls4ml.Intermsofperformance,KANELÉdelivers330×higher
throughput,643×lowerlatencyanda9,840×reductioninenergy
5.4 ComparisonwithPriorKAN-FPGA
perinference.TheseresultsestablishKANELÉasahighlyefficient
Literature
alternativetoexistingFPGAneuralimplementations,withstrong
WebenchmarkedKANELÉagainsttheKANFPGAimplementation potentialforscalingtomorecomplexdatasetsandtasksbeyond
byTranetal.[41]ontheMoons,Wine,andDryBeandatasets. classification.

FPGA’26,February22–24,2026,Seaside,CA,USA DucHoang,AarushGupta,andPhilipHarris
Table3:EvaluationofKANELÉagainststate-of-the-artultra-low-latency,resource-efficientLUT-basednetworkarchitectures.
Resultsarereportedafterperformingout-of-contextsynthesisandplace-and-route.Inputbit-widthsareconsistentwiththose
usedinpriorworksforfaircomparison.
Dataset Model Accuracy(%) LUT FF DSP BRAM 𝑭max(MHz) Latency(ns) Area×Delay(LUT×ns)
KANELÉ 75.1 5034 1917 0 0 870 8.1 4.1×104
NeuraLUT-Assemble[6] 75.0 8539 1332 0 0 352 5.7 4.87×104
AmigoLUT-NeuraLUT[47] 74.4 42742 4717 0 0 520 9.6 4.10×105
JSCCERNBox PolyLUT-Add[30] 75.0 36484 1209 0 0 315 16 5.84×105
NeuraLUT[5] 75.1 92357 4885 0 0 368 14 1.29×106
PolyLUT[4] 75.0 246071 12384 0 0 203 25 6.15×106
LogicNets[42] 72.0 37931 810 0 0 427 13 4.93×105
KANELÉ 76.0 1232 900 0 0 987 7.1 8.7×103
NeuraLUT-Assemble[6] 76.0 1780 540 0 0 941 2.1 3.92×103
JSCOpenML TreeLUT[23] 75.6 2234 347 0 0 735 2.7 6.03×103
DWN[7] 76.3 4972 3305 0 0 827 7.3 3.6×104
da4ml[37] 76.9 12250 1502 0 0 212 18.9 2.3×105
hls4ml(Fahimetal.)[16] 76.2 63251 4394 38 0 200 45 2.85×106
KANELÉ 96.3 3809 4133 0 0 864 9.3 3.5×104
NeuraLUT-Assemble[6] 97.9 5070 725 0 0 863 2.1 1.06×104
TreeLUT[23] 96.6 4478 597 0 0 791 2.5 1.12×104
DWN[7] 97.8 2092 1757 0 0 873 9.2 1.92×104
PolyLUT-Add[30] 96.0 14810 2609 0 0 625 10 1.48×105
MNIST AmigoLUT-NeuraLUT[47] 95.5 16081 13292 0 0 925 7.6 1.22×105
NeuraLUT[5] 96.0 54798 3757 0 0 431 12 6.58×105
PolyLUT[4] 97.5 75131 4668 0 0 353 17 1.38×106
FINN[43] 96.0 91131 — 0 5 200 310 2.82×107
hls4ml(Ngadiubaetal.)[33] 95.0 260092 165513 0 345 200 190 4.94×107
Table4:FPGAresourceutilizationandlatencyofKANmodelsonMoons,Wine,andDryBeanbenchmarksasusedin[41]
Dataset Model Accuracy(%) 𝑭max(MHz) BRAM DSP FF LUT Latency(cycles) Latency(ns) Area×Delay(LUT×ns)
Moons KANELÉ 97 1736 0 0 57 67 5 2.9 1.9×102
KAN(Tranetal)[41] 97 - 10 120 8622 17877 128 1280 2.3×107
ChebyUnit[50] 100 - 10 40 12150 9888 13 130 1.3×106
Wine KANELÉ 98 983 0 0 686 534 6 6.1 8.8×103
KAN(Tranetal)[41] 97 - 132 950 74741 146843 688 6880 1.0×109
ChebyUnit[50] 95 - 132 324 22104 30154 13 130 3.9×106
DryBean KANELÉ 92 842 0 0 471 402 6 7.1 3.3×103
KAN(Tranetal)[41] 92 - 781 9111 734544 1677558 1896 18960 3.2×1010
ChebyUnit[50] 92 - 781 256 25198 27359 13 130 3.6×106
Table5:ComparisonofFPGAresourceutilization,latency,andpowerconsumptionfortheanomalydetectiontaskonthe
ToyADMOStimeseriesdatasetintheMLPerfTinyBenchmark,evaluatedonthexc7a100t-1csg324FPGA[8].
Dataset Model AUC BRAM(36kb) DSP FF LUT LUTRAM II(clocks) Throughput(inf/s) Latency(𝜇𝑠) Energy/inf.(𝜇𝐽)
ToyADMOS KANELÉ 0.83 0 0 17,643 29,981 0 1 228M 0.07 0.01
hls4ml(MLPerfTinyv0.7)[10] 0.83 22.5 207 61,639 51,429 5,780 144 694k 45 98.4
5.6 AblationStudy KANnetworkcanholisticallybethoughtofintermsofitsnumber
WeperformanablationstudyforKANELÉusingtheJSCOpenML ofedges:thisisproportionaltothenumberofLUTsandFFsused,
dataset,showninFigure6.Thisanalysisisolatestheeffectoffour as seen in Figures 6(b) and 6(c). Together, these insights guide
key design factors—accuracy, pruning, hidden layer width, and principleddesignchoicesfordeployingKANELÉundertightFPGA
modelbitwidth—onFPGAresourceutilization(LUTsandFFs).Itis resourcebudgets.
seenthatpruningandquantizationprovidethemosteffectivelevers
forcontrollinghardwarefootprint,whilehiddenlayerwidthand 5.7 ExtensiontoReal-timeControlSystems
accuracytuningallowfine-grainedtrade-offsbetweenperformance
TodemonstratethattheKANELÉparadigmextendswellbeyond
andefficiency.Anotherimportantconclusionisthatthesizeofa
thetraditionalsupervisedlearningtaskstypicallystudiedinthe

KANELÉ:Kolmogorov–ArnoldNetworksforEfficientLUT-basedEvaluation FPGA’26,February22–24,2026,Seaside,CA,USA
1200
1000
800
600
400
200
70 72 74 76
Accuracy (%)
tnuoC
ecruoseR
(a) (b) (c) (d)
1600
LUT LUT 12 k LUT 60 k LUT
1400
FF FF 10 k FF 50 k FF 1200
1000 8 k 40 k
800 6 k 30 k
600
4 k 20 k
400
2 k 10 k
200
0 0 0
0 20 40 60 80 100 0 20 40 60 12 10 8 6 4 2
Pruning Percentage (%) Hidden Layer Width Model Bitwidth
Figure6:AblationstudyofKANELÉontheJSCOpenMLbenchmarkdemonstratingtrade-offsbetweenaccuracy,pruning,
andresourceusage.(a)AccuracyimprovessteadilyashardwareresourcesscaleupwithLUTandFFusagegrowingatroughly
thesamerate.(b)LUT/FFusagescalesroughlylinearlywiththenumberofunprunededges.(c)LUT/FFusagescaleslinearly
withhiddenlayerwidth,confirmingadirectmappingfromlearnedactivationfunctions(edges)toresources.(d)Decreasing
activationbitwidthsreducesLUTresourceusageexponentially,withdiminishingreturnsobservedbelow6bits.
LUT-basedneuralnetworkcommunity,weapplyourframeworkto Table6:Networkarchitecturesoftheactorandcritic.
areinforcementlearningbenchmark.Specifically,weevaluateon
theHalfCheetahenvironment,aclassiccontinuouscontroltask Model Dimensions TrainableParameters
inreinforcementlearning(RL),mostcommonlyaccessedthrough MLPActor [17,64,64,6] 5383
theMuJoCophysicssimulatorviaOpenAIGym(nowGymnasium) MLPCritic [17,64,64,6] 5383
[40].Theobjectiveistolearnapolicythatenablesasimulated KANActor [17,6] 1020
two-legged agent to run as fast and as stably as possible. This
environmentiswidelyusedasastandardbenchmarktocompare
RLalgorithmsandfunctionapproximators.WhileHalfCheetahis returnof 2762.2,outperformingboththelargerMLPFPandquan-
asimulatedbenchmark,itcaptureskeyaspectsofmanypractical tizedactorbaselines(1676.4and1558.8)andthefull-precision
robotcontroltasks,astheyallrelyonthesameunderlyingdesign KANactor(2338.9).TheseresultsdemonstratethatKANsnotonly
andphysicsprinciples. remainrobustunderaggressive8-bitquantization,butcanalso
Thisextensionismotivatedbypriorworksuchas[24],wherethe benefitfromit,potentiallyduetoregularizationeffectsbyfixedbit
authorsshowedthatKANactornetworkswithsignificantlyfewer operations.
trainableparametersachievedhigherrewardscomparedtomuch
5.7.3 HardwarePerformance. ToevaluatetheefficiencyofKANs
largerMLPswhentrainedwiththeProximalPolicyOptimization
inpracticaldeployment,wecomparethehardwarecostofthe8-bit
(PPO)algorithm.PPOisoneofthemostwidelyusedRLalgorithms
quantizedKANactoragainstthe8-bitquantizedMLPactor.The
inpractice,particularlyinrobotics,games,andcontinuouscontrol
KANactorwasdeployedusingtheKANELÉframework,whilethe
tasks.
MLPactorwasimplementedwithhls4ml[16]usingtheResource
strategyforafairbaseline.Weplannedtohavebothmodelssynthe-
5.7.1 Setup. Sincethe primary focusof thispaperis inference
sizedonaXilinxxczu7ev-ffvc1156-2-eFPGAinout-of-context
efficiency,weincorporatedKANsonlyasthefunctionapproximator
mode.However,the8-bitMLPdesignexceedstheavailableFPGA
forthepolicy(actor),asthisisthecomponentthatmustbedeployed
resources,soitsperformanceresultsarebasedonHLSestimates
inpractice.Thevalue(critic)functionremainedanMLPforall
ratherthanthe actual implementation.Table7 summarizesthe
experiments.Weevaluatedfourtrainingscenarios:
results.Ascanbeseen,the8-bitKANactorachievessignificantly
(1) MLPactor+MLPcritic(bothFP), lowerresourceutilization,latency,andpowercomparedtothe8-
(2) QuantizedMLPactor(8-bit)+MLPFPcritic, bitMLPactor,underscoringtheadvantagesofKANsforreal-time
(3) KANFPactor+MLPFPcritic, reinforcementlearningcontroltasks.
(4) QuantizedKANactor(8-bit)+MLPFPcritic. Inconclusion,theHalfCheetahtaskisasimulatedenvironment
Toensurerobustnessagainstvarianceinrandominitialization, thatcapturescoreprinciplesofreal-worldcontroltasksandserves
eachscenariowastrainedwith5differentrandomseeds,for1mil- asastrongproxyfordomainswherereal-time,resource-efficient
lionenvironmentstepsperseed.Theactornetworkswerechosen policiesareessential.Theseresultsthereforehighlightthesuit-
such that the MLP actor had roughly five times more trainable abilityofKANsfordeploymentinsettingswheresuchconstraints
parametersthantheKANactor(Table6),highlightingthatKAN matter(e.g.,robotics,embeddedcontrol,trading,orquantumcom-
canbemoreeffectiveevenwithsignificantlyfewerparameters. puting).Thus,thebenchmarkservesasaproof-of-concept:KANs
canprovidecompetitiveorsuperiorRLperformancewhilebeing
5.7.2 Trainingresults. Figure7showsthelearningcurvesacross dramaticallymoreefficientintermsofsizeandquantizationtoler-
thefourscenarios.ThequantizedKANactorachievesanaverage ance.

FPGA’26,February22–24,2026,Seaside,CA,USA DucHoang,AarushGupta,andPhilipHarris
3200
2400
1600
800
0
200k 400k 600k 800k 1M
Training Steps
draweR
edosipE
ofcompilationandmoreoneofdirectinstantiation.Thisparadigm
HalfCheetah-v5
shift—fromemulatingarithmetictodirectlyconfiguringlogic—is
whatunlockstheextremeefficiencyof KANELÉ,sidesteppingthe
need for DSPs and BRAMs entirely and aligning the algorithm
directlywiththehardware’snativecapabilities.
AcrossstandardLUT–NNbenchmarksandpriorKAN–FPGA
tasks,KANELÉdemonstratesstrongperformancewithafavorable
Area×Delaytrade-off,offeringsubstantiallylowerlatencyandre-
Model : Dimension ducedlogicutilizationcomparedtoearlierKAN-on-FPGAdesigns,
MLP FP: [17, 64, 64, 6]
whilematchingorexceedingotherLUT-centricarchitectureswhen
MLP 8-bit: [17, 64, 64, 6]
KAN FP: [17, 6] thetargetfunctionexhibitssymbolicorphysics-inspiredstructure.
KAN 8-bit: [17, 6]
WefurtherdemonstratedtheapplicabilityofKANELÉtoreal-time
controlbydeployingan8-bitKANpolicythatsurpassesalarger
MLPwhileachievingultra-lowlatencyandhigherresourceeffi-
ciencyonFPGA.
Figure7:PPOtrainingonHalfCheetah-v5with5seeds.The
FutureWorks. Buildingonourresults,weidentifyseveralav-
quantizedKANactor(8-bit)outperformsboththeKAN(FP)
enuestobroadenthescopeandimpactofKANELÉ:
andthelargerMLP(FP),despiteusing∼5×fewerparameters,
showingrobustnesstoquantizationandstrongparameter • Broadermodelfamilies.ExtendingbeyondsingleKANsto
efficiency. ensembles,temporalandconvolutionalKANs,graph-based
KANs,ortransformer-styleKANs(“KAN-GPT”)onFPGAs.
• Alternativeorthogonalbases.MovingbeyondB-splines
Table 7: FPGA performance of the KAN 8-bit model on
byexploringFourier,wavelet,orrationalbasesforlearn-
theHalfCheetahRLtasktargetingthexczu7ev-ffvc1156-2-e
ableactivations.Thesealternativesmayimproveapproxi-
FPGA.TheMLP8-bitactordoesnotfitontheFPGA,soits
mationpowerandtrainingdynamicswhileremainingLUT-
powerestimateisunavailableandresourceusageisreported
compatible.
fromHLSestimates,whileKAN8-bitresultsareobtained
• Practicaldeploymentincontroltasks.Ourreinforce-
afterplace-and-routeinout-of-contextmode.
mentlearningdemoshowsthat8-bitKANpoliciescanout-
performlargerMLPswhilesustainingultra-lowFPGAla-
Metric KAN8-bit MLP8-bithls4ml tency,meetingdemandsofapplicationssuchasquantum
1MEpisodeReward 2762.2 1558.8 errorcorrection,plasmastabilization,adaptiveoptics,andro-
botics.Futureworktargetsrapidin-fieldadaptationthrough
Max.Frequency(𝐹 max) 884MHz 500MHz
hot-swappingedgetablesviapartialreconfigurationorLUT
Latency 4.5ns 893ns
updates,enablinglightweightonlinelearningwithminimal
BRAM 0 0 latency.
DSP 0 14,346
Flip-Flops(FF) 2,828 460,800 Realizingthefullpotentialofthisparadigm,however,firstre-
Look-UpTables(LUT) 1,136 230,400 quiresovercomingtheperceptionthatKANsareinherentlyineffi-
Area×Delay 1.3×104LUT·ns 2.1×108LUT·ns cientinhardware.Ourwork,KANELÉ,directlyrefutesthisview
DynamicPower 0.224nJ/sample ≫0.224nJ/sample byaligningtheactivation-centricKANformulationwiththenative
strengthsofFPGALUTfabrics.ThisapproachtransformsKANs
intoapractical,high-throughput,andpower-efficientinference
6 ConclusionandFutureWorks architecture.Webelievethishardware-centricperspectivenotonly
solvesacriticalimplementationchallengebutalsosolidifiesthe
WepresentKANELÉ,ahardware–softwareco-designframework
promisingpathtowardinterpretable,low-resourceneuralnetworks
that maps Kolmogorov–Arnold Networks (KANs) onto a LUT-
thatscalefromembeddedcontrollerstolargescientificinstruments,
nativecomputationalarchitectureforFPGAs.Unlikemostexisting
naturallybenefitingfromsoftware–hardwareco-design.
MLhardware–softwareco-designapproaches,KANsarebuilten-
tirelyfromlearnable1Dactivationfunctionsdefinedonafixed
domain.Eachlearnedactivationfunction𝜙(𝑥)isthusnotmerely Acknowledgments
approximatedbyaL-LUT:itisalookuptable.Moreover,theadditive Theauthorsthanktheanonymousreferees,VladimirLoncar,Marta
structureofKANsenablesanespeciallynaturalformofpruning: AndronicandRyanKastnerfortheirvaluablecommentsandhelpful
eachnodecanbedirectlyremovedfromthesummationwithout suggestions.PH,DH,andAGaresupportedbytheNSF-funded
disruptingtheremainingcomputation.Thisisinstarkcontrastto A3D3Institute(NSF-PHY-2117997).
conventionalLUT-basedneuralnetworks,whereLUTsaretypically
chainedtogetherasindicesintooneanother,makingtheremoval References
ofevenasingleLUTpracticallyimpossiblewithoutbreakingthe
[1] 2020. Dry Bean. UCI Machine Learning Repository. DOI:
model.Consequently,mappingaKANtoanFPGAislessaprocess https://doi.org/10.24432/C50S4B.

KANELÉ:Kolmogorov–ArnoldNetworksforEfficientLUT-basedEvaluation FPGA’26,February22–24,2026,Seaside,CA,USA
[2] StefanAeberhardandM.Forina.1992.Wine.UCIMachineLearningRepository. [24] VictorAugustoKich,JairAugustoBottega,RaulSteinmetz,RicardoBedinGrando,
DOI:https://doi.org/10.24432/C5PC7J. AyanoYorozu,andAkihisaOhya.2024.Kolmogorov-ArnoldNetworkforOnline
[3] IgorAleksander,W.V.Thomas,andPrBowden.1984.WISARD·aradicalstep ReinforcementLearning.arXiv:2408.04841[cs.LG] https://arxiv.org/abs/2408.
forwardinimagerecognition. SensorReview4(1984),120–124. https://api. 04841
semanticscholar.org/CorpusID:108462259 [25] ChenxinLi,XinyuLiu,WuyangLi,ChengWang,HengyuLiu,andYixuanYuan.
[4] Marta Andronic andGeorge A. Constantinides.2023. PolyLUT:Learning 2024. U-KANMakesStrongBackboneforMedicalImageSegmentationand
PiecewisePolynomialsforUltra-LowLatencyFPGALUT-basedInference.In Generation.arXivpreprintarXiv:2406.02918(2024).
2023InternationalConferenceonFieldProgrammableTechnology(ICFPT).IEEE. [26] LonglongLi,YipengZhang,GuanghuiWang,andKelinXia.2025.Kolmogorov–
doi:10.1109/icfpt59805.2023.00012 Arnoldgraphneuralnetworksformolecularpropertyprediction.NatureMachine
[5] MartaAndronicandGeorgeA.Constantinides.2024.NeuraLUT:HidingNeural Intelligence7,8(2025),1346–1354. doi:10.1038/s42256-025-01087-7
NetworkDensityinBooleanSynthesizableFunctions.In202434thInternational [27] Ziming Liu, Pingchuan Ma, Yixuan Wang, Wojciech Matusik, and Max
ConferenceonField-ProgrammableLogicandApplications(FPL).IEEE,140–148. Tegmark. 2024. KAN 2.0: Kolmogorov-Arnold Networks Meet Science.
doi:10.1109/fpl64840.2024.00028 arXiv:2408.10205[cs.LG] https://arxiv.org/abs/2408.10205
[6] MartaAndronicandGeorgeA.Constantinides.2025. NeuraLUT-Assemble: [28] ZimingLiu,YixuanWang,SachinVaidya,FabianRuehle,JamesHalverson,Marin
Hardware-awareAssemblingofSub-NeuralNetworksforEfficientLUTInference. Soljačić,ThomasY.Hou,andMaxTegmark.2025. KAN:Kolmogorov-Arnold
arXiv:2504.00592[cs.LG] https://arxiv.org/abs/2504.00592 Networks.arXiv:2404.19756[cs.LG] https://arxiv.org/abs/2404.19756
[7] AlanT.L.Bacellar,ZacharySusskind,MauricioBreternitzJr.,EugeneJohn,LizyK. [29] IlyaLoshchilovandFrankHutter.2019.DecoupledWeightDecayRegularization.
John,PriscilaM.V.Lima,andFelipeM.G.França.2025.DifferentiableWeightless arXiv:1711.05101[cs.LG] https://arxiv.org/abs/1711.05101
NeuralNetworks.arXiv:2410.11112[cs.LG] https://arxiv.org/abs/2410.11112 [30] Binglei Lou, Richard Rademacher, David Boland, and Philip H. W. Leong.
[8] ColbyBanbury,VijayJanapaReddi,PeterTorelli,JeremyHolleman,NatJeffries, 2024. PolyLUT-Add: FPGA-based LUT Inference with Wide Inputs.
CsabaKiraly,PietroMontino,DavidKanter,SebastianAhmed,DaniloPau,etal. arXiv:2406.04910[cs.LG] https://arxiv.org/abs/2406.04910
2021.MLPerfTinyBenchmark.ProceedingsoftheNeuralInformationProcessing [31] Marmiton.n.d..Cannelésbordelais.https://www.marmiton.org/recettes/recette_
SystemsTrackonDatasetsandBenchmarks(2021). canneles-bordelais_11439.aspx. Accessed:Sept23,2025.
[9] Alexander Dylan Bodner, Antonio Santiago Tepsich, Jack Natan Spolski, [32] IgorD.S.Miranda,AmanArora,ZacharySusskind,LuisA.Q.Villon,RafaelF.
andSantiagoPourteau.2025. ConvolutionalKolmogorov-ArnoldNetworks. Katopodis,DiegoL.C.Dutra,LeandroS.DeAraújo,PriscilaM.V.Lima,FelipeM.G.
arXiv:2406.13155[cs.CV] https://arxiv.org/abs/2406.13155 França,LizyK.John,andMauricioBreternitz.2022.LogicWiSARD:Memoryless
[10] HendrikBorras,GiuseppeDiGuglielmo,JavierDuarte,NicolòGhielmetti,Ben SynthesisofWeightlessNeuralNetworks.In2022IEEE33rdInternationalConfer-
Hawks,ScottHauck,Shih-ChiehHsu,RyanKastner,JasonLiang,AndresMeza, enceonApplication-specificSystems,ArchitecturesandProcessors(ASAP).19–26.
JulesMuhizi,TaiNguyen,RushilRoy,NhanTran,YamanUmuroglu,OliviaWeng, doi:10.1109/ASAP54787.2022.00014
AidanYokuda,andMichaelaBlott.2022.Open-sourceFPGA-MLcodesignfor [33] JenniferNgadiuba,VladimirLoncar,MaurizioPierini,SioniSummers,Giuseppe
theMLPerfTinyBenchmark. arXiv:2206.11791[cs.LG] https://arxiv.org/abs/ DiGuglielmo,JavierDuarte,PhilipHarris,DylanRankin,SergoJindariani,Mia
2206.11791 Liu,KevinPedro,NhanTran,EdwardKreinar,SheilaSagear,ZhenbinWu,and
[11] CERNCollaboration.2025.CERNBoxLHCJetsDataset. https://cernbox.cern. DucHoang.2020.CompressingdeepneuralnetworksonFPGAstobinaryand
ch/index.php/s/jvFd5MoWhGs1l5v/download[Accessed:Sept1,2025]. ternaryprecisionwithhls4ml. MachineLearning:ScienceandTechnology2,1
[12] SunChang,TheaÅrrestad,VladimirLončar,JenniferNgadiuba,andMariaSpirop- (dec2020),015001.doi:10.1088/2632-2153/aba042
ulu.2024.Gradient-basedAutomaticPer-WeightMixedPrecisionQuantization [34] OpenMLContributorsandLHCJetsHLFCurators.2020. hls4mllhcjetshlf
forNeuralNetworksOn-Chip.doi:10.7907/HQ8JD-RHG30 (OpenMLDataset42468). https://www.openml.org/d/42468[Accessed:Sept1,
[13] GonçaloG.Cruz,BalázsRenczes,MarkC.Runacres,andJanDecuyper.2025. 2025].
State-SpaceKolmogorovArnoldNetworksforInterpretableNonlinearSystem [35] Fabian Pedregosa, Gaël Varoquaux, Alexandre Gramfort, Vincent Michel,
Identification.IEEEControlSystemsLetters9(2025),847–852.doi:10.1109/LCSYS. Bertrand Thirion, Olivier Grisel, Mathieu Blondel, Peter Prettenhofer, Ron
2025.3578019 Weiss,VincentDubourg,JakeVanderplas,AlexandrePassos,DavidCournapeau,
[14] LiDeng.2012.TheMNISTDatabaseofHandwrittenDigitImagesforMachine MatthieuBrucher,MatthieuPerrot,andÉdouardDuchesnay.2011.Scikit-learn:
LearningResearch[BestoftheWeb]. IEEESignalProcessingMagazine29,6 MachineLearninginPython.JournalofMachineLearningResearch12,85(2011),
(2012),141–142.doi:10.1109/MSP.2012.2211477 2825–2830. http://jmlr.org/papers/v12/pedregosa11a.html
[15] IvanDrokin.2024. Kolmogorov-ArnoldConvolutions:DesignPrinciplesand [36] ShriyankSomvanshi,SyedAaqibJaved,MdMonzurulIslam,DiwasPandit,and
EmpiricalStudies.arXiv:2407.01092[cs.CV] https://arxiv.org/abs/2407.01092 SubasishDas.2025.ASurveyonKolmogorov-ArnoldNetwork.Comput.Surveys
[16] FarahFahim,BenjaminHawks,ChristianHerwig,JamesHirschauer,SergoJin- (June2025). doi:10.1145/3743128
dariani,NhanTran,LucaP.Carloni,GiuseppeDiGuglielmo,PhilipHarris,Jef- [37] ChangSun,ZhiqiangQue,VladimirLoncar,WayneLuk,andMariaSpiropulu.
freyKrupa,DylanRankin,ManuelBlancoValentin,JosiahHester,YingyiLuo, 2025.da4ml:DistributedArithmeticforReal-timeNeuralNetworksonFPGAs.
JohnMamish,SedaOrgrenci-Memik,TheaAarrestad,HamzaJaved,Vladimir arXiv:2507.04535[cs.AR] https://arxiv.org/abs/2507.04535
Loncar,MaurizioPierini,AdrianAlanPol,SioniSummers,JavierDuarte,Scott [38] ZacharySusskind,AmanArora,IgorD.S.Miranda,LuisA.Q.Villon,RafaelF.
Hauck,Shih-ChiehHsu,JenniferNgadiuba,MiaLiu,DucHoang,EdwardKreinar, Katopodis,LeandroS.deAraújo,DiegoL.C.Dutra,PriscilaM.V.Lima,Felipe
andZhenbinWu.2021. hls4ml:AnOpen-SourceCodesignWorkflowtoEm- M.G.França,MauricioBreternitz,andLizyK.John.2023. WeightlessNeural
powerScientificLow-PowerMachineLearningDevices.arXiv:2103.05579[cs.LG] NetworksforEfficientEdgeInference.InProceedingsoftheInternationalCon-
https://arxiv.org/abs/2103.05579 ferenceonParallelArchitecturesandCompilationTechniques(Chicago,Illinois)
[17] GiuseppeFranco,AlessandroPappalardo,andNicholasJFraser.2025.Xilinx/bre- (PACT’22).AssociationforComputingMachinery,NewYork,NY,USA,279–290.
vitas.doi:10.5281/zenodo.3333552 doi:10.1145/3559009.3569680
[18] RemiGenetandHugoInzirillo.2025. TKAN:TemporalKolmogorov-Arnold [39] ZacharySusskind,AlanBacellar,AmanArora,LuisVillon,RenanMendanha,Le-
Networks.arXiv:2405.07344[cs.LG] https://arxiv.org/abs/2405.07344 androSantiago,DiegoDutra,PriscilaLima,FelipeFrança,IgorMiranda,Mauricio
[19] Xiao Han, Xinfeng Zhang, Yiling Wu, Zhenduo Zhang, and Zhe Wu. Breternitz,andLIZYJOHN.2022.PruningWeightlessNeuralNetworks.37–42.
2025. Are KANs Effective for Multivariate Time Series Forecasting? doi:10.14428/esann/2022.ES2022-55
arXiv:2408.11306[cs.LG] https://arxiv.org/abs/2408.11306 [40] EmanuelTodorov,TomErez,andYuvalTassa.2012.MuJoCo:Aphysicsengine
[20] YuntianHou,TianruiJi,DiZhang,andAngelosStefanidis.2025.Kolmogorov- formodel-basedcontrol.In2012IEEE/RSJInternationalConferenceonIntelligent
ArnoldNetworks:ACriticalAssessmentofClaims,Performance,andPractical RobotsandSystems.5026–5033.doi:10.1109/IROS.2012.6386109
Viability.arXiv:2407.11075[cs.LG] https://arxiv.org/abs/2407.11075 [41] VanDuyTran,TranXuanHieuLe,ThiDiemTran,HoaiLuanPham,VuTrung
[21] AbdullahAlImranandMdFarhanIshmam.2024. FourierKANoutperforms DuongLe,TuanHaiVu,VanTinhNguyen,andYasuhikoNakashima.2024.
MLPonTextClassificationHeadFine-tuning.arXiv:2408.08803[cs.CL] https: ExploringtheLimitationsofKolmogorov-ArnoldNetworksinClassification:
//arxiv.org/abs/2408.08803 InsightstoSoftwareTrainingandHardwareImplementation.In2024Twelfth
[22] TianruiJi,YuntianHou,andDiZhang.2025. AComprehensiveSurveyon InternationalSymposiumonComputingandNetworkingWorkshops(CANDARW).
KolmogorovArnoldNetworks(KAN).arXiv:2407.11075[cs.LG] https://arxiv. 110–116.doi:10.1109/CANDARW64572.2024.00026
org/abs/2407.11075 [42] YamanUmuroglu,YashAkhauri,NicholasJ.Fraser,andMichaelaBlott.2020.
[23] AlirezaKhataeiandKiaBazargan.2025. TreeLUT:AnEfficientAlternative LogicNets:Co-DesignedNeuralNetworksandCircuitsforExtreme-Throughput
toDeepNeuralNetworksforInferenceAccelerationUsingGradientBoosted Applications.arXiv:2004.03021[eess.SP] https://arxiv.org/abs/2004.03021
DecisionTrees.InProceedingsofthe2025ACM/SIGDAInternationalSymposium [43] YamanUmuroglu,NicholasJ.Fraser,GiulioGambardella,MichaelaBlott,Philip
onFieldProgrammableGateArrays(FPGA’25).ACM,14–24.doi:10.1145/3706628. Leong,MagnusJahre,andKeesVissers.2017.FINN:AFrameworkforFast,Scal-
3708877 ableBinarizedNeuralNetworkInference.InProceedingsofthe2017ACM/SIGDA
InternationalSymposiumonField-ProgrammableGateArrays(FPGA’17).ACM,

FPGA’26,February22–24,2026,Seaside,CA,USA DucHoang,AarushGupta,andPhilipHarris
65–74.doi:10.1145/3020078.3021744 andRyanKastner.2025. GreaterthantheSumofitsLUTs:ScalingUpLUT-
[44] ErweiWang,JamesJ.Davis,PeterY.K.Cheung,andGeorgeA.Constantinides. basedNeuralNetworkswithAmigoLUT.InProceedingsofthe2025ACM/SIGDA
2019.LUTNet:RethinkingInferenceinFPGASoftLogic.arXiv:1904.00938[cs.LG] InternationalSymposiumonFieldProgrammableGateArrays(Monterey,CA,USA)
https://arxiv.org/abs/1904.00938 (FPGA’25).AssociationforComputingMachinery,NewYork,NY,USA,25–35.
[45] YixuanWang,JonathanW.Siegel,ZimingLiu,andThomasY.Hou.2025. On doi:10.1145/3706628.3708874
theexpressivenessandspectralbiasofKANs.arXiv:2410.01803[cs.LG] https: [48] RunpengYu,WeihaoYu,andXinchaoWang.2024. KANorMLP:AFairer
//arxiv.org/abs/2410.01803 Comparison.arXiv:2407.16674[cs.LG] https://arxiv.org/abs/2407.16674
[46] YizhengWang,JiaSun,JinshuaiBai,CosminAnitescu,MohammadSadegh [49] JushengZhang,YijiaFan,KaitongCai,andKezeWang.2025.Kolmogorov-Arnold
Eshaghi, Xiaoying Zhuang, Timon Rabczuk, and Yinghua Liu. 2025. FourierNetworks.arXiv:2502.06018[cs.LG] https://arxiv.org/abs/2502.06018
Kolmogorov–Arnold-Informed neural network: A physics-informed deep [50] Zhonglongyou,WEN-LINGDING,Chieh-HsinYu,HUNGYUCHEN,TSUNG-
learning framework for solving forward and inverse problems based on KAIWENG,You-JinLiu,andErayHsieh.2026. CHEBYUNIT:HARDWARE-
Kolmogorov–ArnoldNetworks. ComputerMethodsinAppliedMechanicsand ACCELERATED ENERGY-EFFICIENT FPGA WITH LOW COMPUTATION
Engineering433(Jan.2025),117518. doi:10.1016/j.cma.2024.117518 COMPLEXITYFORARTIFICIALINTELLIGENCEACCELERATION. https:
[47] OliviaWeng,MartaAndronic,DanialZuberi,JiaqingChen,CalebGeniesse, //openreview.net/forum?id=ifKE2RjnXm
GeorgeA.Constantinides,NhanTran,NicholasJ.Fraser,JavierMauricioDuarte,

