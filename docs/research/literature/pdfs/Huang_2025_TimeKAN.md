# Huang_2025_TimeKAN

PublishedasaconferencepaperatICLR2025
TIMEKAN: KAN-BASED FREQUENCY DECOMPOSI-
TION LEARNING ARCHITECTURE FOR LONG-TERM
TIME SERIES FORECASTING
SongtaoHuang1,2,ZhenZhao1,CanLi3,LeiBai1(cid:66)
1ShanghaiArtificialIntelligenceLaboratory,Shanghai,China
2SchoolofInformationScienceandEngineering,LanzhouUniversity,Lanzhou,China
3TheKeyLaboratoryofRoadandTrafficEngineeringoftheMinistryofEducation,
TongjiUniversity,Shanghai,China
huangsongtao@pjlab.org.cn, zhen.zhao@outlook.com,
lchelen1005@gmail.com, baisanshi@gmail.com
ABSTRACT
Real-world time series often have multiple frequency components that are inter-
twinedwitheachother,makingaccuratetimeseriesforecastingchallenging. De-
composingthemixedfrequencycomponentsintomultiplesinglefrequencycom-
ponents is a natural choice. However, the information density of patterns varies
acrossdifferentfrequencies,andemployingauniformmodelingapproachfordif-
ferentfrequencycomponentscanleadtoinaccuratecharacterization. Toaddress
thischallenges,inspiredbytheflexibilityoftherecentKolmogorov-ArnoldNet-
work (KAN), we propose a KAN-based Frequency Decomposition Learning ar-
chitecture (TimeKAN) to address the complex forecasting challenges caused by
multiple frequency mixtures. Specifically, TimeKAN mainly consists of three
components: Cascaded Frequency Decomposition (CFD) blocks, Multi-order
KAN Representation Learning (M-KAN) blocks and Frequency Mixing blocks.
CFDblocksadoptabottom-upcascadingapproachtoobtainseriesrepresentations
foreachfrequencyband.BenefitingfromthehighflexibilityofKAN,wedesigna
novelM-KANblocktolearnandrepresentspecifictemporalpatternswithineach
frequencyband. Finally, FrequencyMixingblocksisusedtorecombinethefre-
quencybandsintotheoriginalformat. Extensiveexperimentalresultsacrossmul-
tiplereal-worldtimeseriesdatasetsdemonstratethatTimeKANachievesstate-of-
the-artperformanceasanextremelylightweightarchitecture. Codeisavailableat
https://github.com/huangst21/TimeKAN.
1 INTRODUCTION
Timeseriesforecasting(TSF)hasgarneredsignificantinterestduetoitswiderangeofapplications,
includingfinance(Huangetal.,2024),energymanagement(Yinetal.,2023),trafficflowplanning
(Jiang & Luo, 2022), and weather forecasting (Lam et al., 2023). Recently, deep learning has led
tosubstantialadvancementsinTSF,withthemoststate-of-the-artperformancesachievedbyCNN-
based methods (Wang et al., 2023; donghao & wang xue, 2024), Transformer-based methods(Nie
etal.,2023;Liuetal.,2024b)andMLP-basedmethods(Zengetal.,2023;Wangetal.,2024a).
Due to the complex nature of the real world, observed multivariate time series are often non-
stationary and exhibit diverse patterns. These intertwined patterns complicate the internal rela-
tionshipswithinthetimeseries,makingitchallengingtocaptureandestablishconnectionsbetween
historicalobservationsandfuturetargets. Toaddressthecomplextemporalpatternsintimeseries,
anincreasingnumberofstudiesfocusonleveragingpriorknowledgetodecomposetimeseriesinto
simplercomponentsthatprovideabasisforforecasting. Forinstance,Autoformer(Wuetal.,2021)
decomposestimeseriesintoseasonalandtrendcomponents. ThisideaisalsoadoptedbyDLinear
(Zengetal.,2023)andFEDFormer(Zhouetal.,2022b). Buildingonthisfoundation, TimeMixer
(Wang et al., 2024a) further introduces multi-scale seasonal-trend decomposition and highlights
the importance of interactions between different scales. Recent models like TimesNet (Wu et al.,
1
5202
beF
62
]GL.sc[
2v01960.2052:viXra

PublishedasaconferencepaperatICLR2025
2023),PDF(Daietal.,2024),andSparseTSF(Linetal.,2024)emphasizetheinherentperiodicity
intimeseriesanddecomposelongsequencesintomultipleshorteronesbasedontheperiodlength,
thereby enabling the separate modeling of inter-period and intra-period dependencies within tem-
poralpatterns. Insummary,thesedifferentdecompositionmethodsshareacommongoal: utilizing
thesimplifiedsubsequencestoprovidecriticalinformationforfuturepredictions,therebyachieving
accurateforecasting.
Itisworthnotingthattimeseriesareoftencomposedofmultiplefrequencycomponents,wherethe
low-frequencycomponentsrepresentlong-termperiodicvariationsandthehigh-frequencycompo-
nentscapturecertainabruptevents. Themixtureofdifferentfrequencycomponentsmakesaccurate
forecastingparticularlychallenging. Theaforementioneddecompositionapproachesmotivateusto
design a frequency decomposition framework that decouples different frequency components in a
timeseriesandindependentlylearnsthetemporalpatternsassociatedwitheachfrequency.However,
thisintroducesanotherchallenge:theinformationdensityofpatternsvariesacrossdifferentfrequen-
cies, andemployingauniformmodelingapproachfordifferentfrequencycomponentscanleadto
inaccuratecharacterizations,resultinginsub-optimalresults. Fortunately,anewneuralnetworkar-
chitecture,knownasKolmogorov-ArnoldNetworks(KAN)(Liuetal.,2024c),hasrecentlygained
significantattentioninthedeeplearningcommunityduetoitsoutstandingdata-fittingcapabilities
andflexibility,showingpotentialasasubstitutefortraditionalMLP.ComparedtoMLP,KANoffers
optional kernels and allows for the adjustment of kernel order to control its fitting capacity. This
considerationleadsustoexploretheuseofMulti-orderKANstorepresenttemporalpatternsacross
differentfrequencies,therebyprovidingmoreaccurateinformationforforecasting.
Motivatedbytheseobservations,weproposeaKAN-basedFrequencyDecompositionLearningar-
chitecture(TimeKAN)toaddressthecomplexpredictionchallengescausedbymultiplefrequency
mixtures. Specifically,TimeKANfirstemploysmovingaveragetoprogressivelyremoverelatively
high-frequencycomponentsfromthesequence. Subsequently,CascadedFrequencyDecomposition
(CFD) blocks adopt a bottom-up cascading approach to obtain sequence representations for each
frequency band. Multi-order KAN Representation Learning (M-KAN) blocks leverage the high
flexibility of KAN to learn and represent specific temporal patterns within each frequency band.
Finally,FrequencyMixingblocksrecombinethefrequencybandsintotheoriginalformat,ensuring
thatthisDecomposition-Learning-Mixingprocessisrepeatable,therebymodelingdifferenttempo-
ral patterns at various frequencies more accurately. The final high-level sequence is then mapped
to the desired forecasting output via a simple linear mapping. With our meticulously designed ar-
chitecture, TimeKAN achieves state-of-the-art performance across multiple long-term time series
forecastingtasks,whilealsobeingalightweightarchitecturethatoutperformscomplexTSFmodels
withfewercomputationalresources.
Ourcontributionsaresummarizedasfollows:
• Werevisittimeseriesforecastingfromtheperspectiveoffrequencydecoupling,effectively
disentangling time series characteristics through a frequency Decomposition-Learning-
Mixingarchitecturetoaddresschallengescausedbycomplexinformationcouplingintime
series.
• WeintroduceTimeKANasalightweightyeteffectiveforecastingmodelanddesignanovel
M-KAN blocks to effectively modeling and representing patterns at different frequencies
bymaximizingtheflexibilityofKAN.
• TimeKANdemonstratessuperiorperformanceacrossmultipleTSFpredictiontasks,while
havingaparametercountsignificantlylowerthanthatofstate-of-the-artTSFmodels.
2 RELATED WORK
2.1 KOLMOGOROV-ARNOLDNETWORK
Kolmogorov-Arnoldrepresentationtheoremstatesthatanymultivariatecontinuousfunctioncanbe
expressed as a combination of univariate functions and addition operations. Kolmogorov-Arnold
Network (KAN) (Liu et al., 2024c) leverages this theorem to propose an innovative alternative to
traditional MLP. Unlike MLP, which use fixed activation functions at the nodes, KAN introduces
2

PublishedasaconferencepaperatICLR2025
learnableactivationfunctionsalongtheedges. Duetotheflexibilityandadaptability,KANiscon-
sideredasapromisingalternativetoMLP.
The original KAN was parameterized using spline functions. However, due to the inherent com-
plexity of spline functions, the speed and scalability of the original KAN were not satisfactory.
Consequently, subsequent research explored the use of simpler basis functions to replace splines,
thereby achieving higher efficiency. ChebyshevKAN (SS, 2024) incorporates Chebyshev polyno-
mialstoparametrizethelearnablefunctions. FastKAN(Li,2024)usesfasterGaussianradialbasis
functionstoapproximatethird-orderB-splinefunctions.
Moreover,KANhasbeenappliedasalternativestoMLPinvariousdomains. ConvolutionalKAN
(Bodneretal.,2024)replacesthelinearweightmatricesintraditionalconvolutionalnetworkswith
learnablesplinefunctionmatrices. U-KAN(Lietal.,2024)integratesKANlayersintotheU-Net
architecture, demonstrating impressive accuracy and efficiency in several medical image segmen-
tation tasks. KAN has also been used to bridge the gap between AI and science. Works such as
PIKAN(Shuklaetal.,2024)andPINN(Wangetal.,2024b)utilizeKANtobuildphysics-informed
machinelearningmodels. ThispaperaimstointroduceKANintoTSFanddemonstratethestrong
potentialofKANinrepresentingtimeseriesdata.
2.2 TIMESERIESFORECASTING
Traditionaltimeseriesforecasting(TSF)methods,suchasARIMA(Zhang,2003),canprovidesuf-
ficient interpretability for the forecasting results but often fail to achieve satisfactory accuracy. In
recentyears,deeplearningmethodshavedominatedthefieldofTSF,mainlyincludingCNN-based,
Transformer-based, and MLP-based approaches. CNN-based models primarily apply convolution
operationsalongthetemporaldimensiontoextracttemporalpatterns. Forexample, MICN(Wang
etal.,2023)andTimesNet(Wuetal.,2023)enhancetheprecisionofsequencemodelingbyadjust-
ingthereceptivefieldtocapturebothshort-termandlong-termviewswithinthesequences. Mod-
ernTCN(donghao&wangxue,2024)advocatesusinglargeconvolutionkernelsalongthetemporal
dimensionandcapturebothcross-timeandcross-variabledependencies. ComparedtoCNN-based
methods,whichhavelimitedreceptivefield,Transformer-basedmethodsofferglobalmodelingca-
pabilities, making them more suitable for handling long and complex sequence data. They have
becomethecornerstoneofmoderntimeseriesforecasting. Informer(Zhouetal.,2021)isoneofthe
earlyimplementationsofTransformermodelsinTSF,makingefficientforecastingpossiblebycare-
fully modifying the internal Transformer architecture. PatchTST (Nie et al., 2023) divides the se-
quenceintomultiplepatchesalongthetemporaldimension,whicharethenfedintotheTransformer,
establishingitasanimportantbenchmarkinthetimeseriesdomain. Incontrast,iTransformer(Liu
et al., 2024b) treats each variable as an independent token to capture cross-variable dependencies
in multivariate time series. However, Transformer-based methods face challenges due to the large
numberofparametersandhighmemoryconsumption. RecentresearchonMLP-basedmethodshas
shownthatwithappropriatelydesignedarchitecturesleveragingpriorknowledge,simpleMLPscan
outperformcomplexTransformer-basedmethods. DLinear(Zengetal.,2023),forinstance,prepro-
cesses sequences using a trend-season decomposition strategy. FITS (Xu et al., 2024b) performs
lineartransformationsinthefrequencydomain,whileTimeMixer(Wangetal.,2024a)usesMLPto
facilitateinformationinteractionatdifferentscales. TheseMLP-basedmethodshavedemonstrated
strongperformanceregardingbothforecastingaccuracyandefficiency. Unliketheaforementioned
methods,thispaperintroducesthenovelKANtoTSFtorepresenttimeseriesdatamoreaccurately.
It also proposes a well-designed Decomposition-Learning-Mixing architecture to fully unlock the
potentialofKANfortimeseriesforecasting.
2.3 TIMESERIESDECOMPOSITION
Real-worldtimeseriesoftenconsistofvariousunderlyingpatterns. Toleveragethecharacteristics
ofdifferentpatterns,recentapproachestendtodecomposetheseriesintomultiplesubcomponents,
including trend-seasonal decomposition, multi-scale decomposition, and multi-period decomposi-
tion. DLinear (Zeng et al., 2023) employs moving averages to decouple the seasonal and trend
components. SCINet (Liu et al., 2022) uses a hierarchical downsampling tree to iteratively ex-
tract and exchange information at multiple temporal resolutions. TimeMixer (Wang et al., 2024a)
follows a fine-to-coarse principle to decompose the sequence into multiple scales across different
3

PublishedasaconferencepaperatICLR2025
High-order KAN High +
Frequency Depthwise Conv
Frequency
Upsampling
Mid-order KAN
Middle + +
Frequency Depthwise Conv
Frequency
Upsampling
Low-order KAN
Low
+ Frequency Depthwise Conv
raeniL tuptuO
Input Series (a)Cascaded Frequency (b) Multi-order KAN (c) Frequency Mixing ×L
Decomposition Representation Learning
Embedding +
Frequency
Moving Upsampling
Average
Embedding
Moving Frequency
Average Upsampling
Embedding
Figure1: ThearchitectureofTimeKAN,whichmainlyconsistsofCascadedFrequencyDecompo-
sitionblock,Multi-orderKANRepresentationLearningblock,andFrequencyMixingblock. Here,
wedividethefrequencyrangeofthetimeseriesintothreefrequencybandsasanexample.
time spans and further splits each scale into seasonal and periodic components. TimesNet (Wu
etal.,2023)andPDF(Daietal.,2024)utilizeFourierperiodicanalysistodecouplesequenceinto
multiplesub-periodsequencesbasedonthecalculatedperiod. Inspiredbytheseworks, thispaper
proposesanovelDecomposition-Learning-Mixingarchitecture,whichexaminestimeseriesfroma
multi-frequencyperspectivetoaccuratelymodelthecomplexpatternswithintimeseries.
3 TIMEKAN
3.1 OVERALLARCHITECTURE
GivenahistoricalmultivariatetimeseriesinputX∈RN×T,theaimoftimeseriesforecastingisto
predictthefutureoutputseriesX ∈ RN×F,whereT,F isthelook-backwindowlengthandthe
O
futurewindowlength,andN representsthenumberofvariates.Inthispaper,weproposeTimeKAN
to tackle the challenges arising from the complex mixture of multi-frequency components in time
series. The overall architecture of TimeKAN is shown in Figure 1. We adopt variate-independent
manner(Nieetal.,2023)topredicteachunivariateseriesindependently. Eachunivariateinputtime
seriesisdenotedasX ∈RT andweconsiderunivariatetimeseriesastheinstanceinthefollowing
calculation. InourTimeKAN,thefirststepistoprogressivelyremovetherelativelyhigh-frequency
componentsusingmovingaveragesandgeneratemulti-levelsequencesfollowedbyprojectingeach
sequence into a high-dimensional space. Next, adhering to the Decomposition-Learning-Mixing
architecture design principle, we first design Cascaded Frequency Decomposition (CFD) blocks
to obtain sequence representations for each frequency band, adopting a bottom-up cascading ap-
proach. Then,weproposeMulti-orderKANRepresentationLearning(M-KAN)blockstolearnand
representspecifictemporalpatternswithineachfrequencyband. Finally,FrequencyMixingblocks
recombinethefrequencybandsintotheoriginalformat,ensuringthattheDecomposition-Learning-
Mixingprocessisrepeatable. MoredetailsaboutourTimeKANaredescribedasfollow.
3.2 HIERARCHICALSEQUENCEPREPROCESSING
AssumethatwedividethefrequencyrangeofrawtimeseriesX intopredefinedkfrequencybands.
Wefirstusemovingaveragetoprogressivelyremovetherelativelyhigh-frequencycomponentsand
generate multi-level sequences {x 1 ,··· ,x k }, where x i ∈ R di T −1(i ∈ {1,··· ,k}). x 1 is equal to
theinputseriesX andddenotesthelengthofmovingaveragewindow. Theprocessofproducing
multi-levelsequencesisasfollows:
x =AvgPool(Padding(x )) (1)
i i−1
Afterobtainingthemulti-levelsequences,eachsequenceisindependentlyembeddedintoahigher
dimensionthroughaLinearlayer:
x =Linear(x ) (2)
i i
4

PublishedasaconferencepaperatICLR2025
wherex i ∈ R di T −1 ×D andD isembeddingdimension. Wedefinex 1 asthehighestlevelsequence
and x as the lowest level sequence. Notably, each lower-level sequence is derived from the se-
k
quenceonelevelhigherbyremovingaportionofthehigh-frequencyinformation.Theaboveprocess
isapreprocessingprocessandonlyoccursonceinTimeKAN.
3.3 CASCADEDFREQUENCYDECOMPOSITION
Real-world time series are often composed of multiple frequency components, with the low-
frequency component representing long-term changes in the time series and the high-frequency
component representing short-term fluctuations or unexpected events. These different frequency
componentscomplementeachotherandprovideacomprehensiveperspectiveforaccuratelymod-
eling time series. Therefore, we design the Cascaded Frequency Decomposition (CFD) block to
accuratelydecomposeeachfrequencycomponentinacascadeway, thuslayingthefoundationfor
accuratelymodelingdifferentfrequencycomponents.
TheaimofCFDblockistoobtaintherepresentationofeachfrequencycomponent. Here,wetake
obtainingtherepresentationofthei-thfrequencybandasanexample.Toachieveit,wefirstemploy
the Fast Fourier Transform (FFT) to obtain the representation of x in the frequency domain.
i+1
Then, Zero-Padding is used to extend the length of the frequency domain sequence, so that it can
have the same length as the upper sequence x after transforming back to the time domain. Next,
i
weuseInverseFastFourierTransform(IFFT)totransformitbackintothetimedomain. Werefer
tothisupsamplingprocessasFrequencyUpsampling,whichensuresthatthefrequencyinformation
remainsunchangedbeforeandaftertheupsampling. TheprocessofFrequencyUpsamplingcanbe
describedas:
xˆ =IFFT(Padding(FFT(x ))) (3)
i i+1
Here,xˆ andx havethesamesequencelength.Notably,comparedtox ,xˆ lacksthei-thfrequency
i i i i
component. The reason is that x is originally formed by removing i-th frequency component
i+1
fromx inthehierarchicalsequencepreprocessingandx isnowtransformedintoxˆ througha
i i+1 i
losslessfrequencyconversionprocess, therebyaligninglengthwithx inthetimedomain. There-
i
fore, to get the series representation of the i-th frequency component f in time domain, we only
i
needtogettheresidualsbetweenx andxˆ :
i i
f =x −xˆ (4)
i i i
3.4 MULTI-ORDERKANREPRESENTATIONLEARNING
Given the multi-level frequency component representation {f ,··· ,f } generated by the CFD
1 k
block, we propose Multi-order KAN Representation Learning (M-KAN) blocks to learn specific
representations and temporal dependencies at each frequency. M-KAN adopts a dual-branch par-
allel architecture to separately model temporal representation learning and temporal dependency
learning in a frequency-specific way, using Multi-order KANs to learn the representation of each
frequencycomponentandemployingDepthwiseConvolutiontocapturethetemporaldependency.
ThedetailsofDepthwiseConvolutionandMulti-orderKANwillbegivenasfollows.
Depthwise Convolution To separate the modeling of temporal dependency from learning se-
quence representation, we adopt a specific type of group convolution known as Depthwise Con-
volution, inwhichthenumberofgroupsmatchestheembeddingdimension. DepthwiseConvolu-
tion employs D groups of convolution kernels to perform independent convolution operations on
theseriesofeachchannel. Thisallowsthemodeltofocusoncapturingtemporalpatternswithout
interferencefrominterchannelrelationships. TheprocessofDepthwiseConvolutionis:
f =Conv (f ,group=D) (5)
i,1 D→D i
Multi-orderKANs ComparedwithtraditionalMLP,KANreplaceslinearweightswithlearnable
univariate functions, allowing complex nonlinear relationships to be modeled with fewer parame-
tersandgreaterinterpretability. (Xuetal.,2024a). AssumethatKANiscomposedofL+1layer
neuronsandthenumberofneuronsinlayerlisn . Thetransmissionrelationshipbetweenthej-th
l
neuroninlayerl+1andallneuronsinlayerlcanbeexpressedasz =
(cid:80)nl
ϕ (z ),where
l+1,j i=1 l,j,i l,i
z isthej-thneuronatlayerl+1andz isthei-thneuronatlayerl. Wecansimplyunderstand
l+1,j l,i
5

PublishedasaconferencepaperatICLR2025
thateachneuronisconnectedtootherneuronsinthepreviouslayerthroughalearnableunivariate
functionϕ. ThevanillaKAN(Liuetal.,2024c)employssplinefunctionasthelearnableunivariate
basicfunctionsϕ,butsufferingfromthecomplexrecursivecomputationprocess,whichhindersthe
efficiencyofKAN.Here,weadoptChebyshevKAN(SS,2024)tolearntherepresentationofeach
frequencycomponent, i.e., channellearning. ChebyshevKANisconstructedfromlinearcombina-
tionsofChebyshevpolynomial.Thatis,usingthelinearcombinationofChebyshevpolynomialwith
differentordertogeneratelearnableunivariatefunctionϕ.TheChebyshevpolynomialisdefinedby:
T (x)=cos(narccos(x)) (6)
n
wherenisthehighestorderofChebyshevpolynomialsandthecomplexityofChebyshevpolyno-
mialsisincreasingwithincreasingorder. A1-layerChebyshevKANappliedtochanneldimension
canbeexpressedas:
D n
(cid:88)(cid:88)
ϕ (x)= Θ T (tanh(x )) (7)
o o,j,i i j
j=1i=0
(cid:40) ϕ (x) (cid:41)
1
KAN(x)= ··· (8)
ϕ (x)
D
where o is the index of output neuron and Θ ∈ RD×D×(n+1) are the learnable coefficients used
to linearly combine the Chebyshev polynomials. It is worth noting that the frequency compo-
nents within the time series exhibit increasingly complex temporal dynamics as the frequency in-
creases,necessitatinganetworkwithstrongerrepresentationcapabilitiestolearnthesecharacteris-
tics. ChebyshevKAN allows for the adjustment of the highest order of Chebyshev polynomials n
toenhanceitsrepresentationability. Therefore,fromthelow-frequencytohigh-frequencycompo-
nents, weadoptanincreasingorderofChebyshevpolynomialstoalignthefrequencycomponents
with the complexity of the KAN, thereby accurately learning the representations of different fre-
quencycomponents. WerefertothisgroupofKANswithvaryinghighestChebyshevpolynomials
ordersasMulti-orderKANs.Wesetanlowerboundorderb,andtherepresentationlearningprocess
forx canbeexpressedas:
i
f =KAN(f ,order=b+k−i) (9)
i,2 i
ThefinaloutputoftheM-KANblockisthesumoftheoutputsfromtheMulti-orderKANsandthe
DepthwiseConvolution.
fˆ =f +f (10)
i i,1 i,2
3.5 FREQUENCYMIXING
Afterspecificallylearningtherepresentationofeachfrequencycomponent,weneedtore-transform
thefrequencyrepresentationsintotheformofmulti-levelsequencesbeforeenteringnextCFDblock,
ensuring that the Decomposition-Learning-Mixing process is repeatable. Therefore, we designed
Frequency Mixing blocks to convert the frequency component at i-th level fˆ into multi-level se-
i
quencesx ,enablingittoserveasinputforthenextCFDblock. Totransformthefrequencycom-
i
ponentati-thlevelfˆ intomulti-levelsequencesx ,wesimplyneedtotosupplementthefrequency
i i
informationfromlevelsi+1tokbackintothei-thlevel. Thus,weemployFrequencyUpsampling
againtoincrementallyreintegratetheinformationintothehigherfrequencycomponents:
x =IFFT(Padding(FFT(x )))+f (11)
i i+1 i
For the last Frequency Mixing block, we extract the highest-level sequence x and use a simple
1
linearlayertoproducetheforecastingresultsX .
O
X =Linear(x ) (12)
O 1
Due to the use of a variate-independent strategy, we also need to stack the predicted results of all
variablestogethertoobtainthefinalmultivariatepredictionX .
O
6

PublishedasaconferencepaperatICLR2025
Table1:Fullresultsofthemultivariatelong-termforecastingresultcomparison.Theinputsequence
lengthissetto96forallbaselinesandthepredictionlengthsF ∈{96,192,336,720}. Avgmeans
theaverageresultsfromallfourpredictionlengths.
Models TimeKAN TimeMixer iTransformer Time-FFM PatchTST TimesNet MICN DLinear FreTS FiLM FEDformer Autoformer
Ours 2024a 2024b 2024a 2023 2023 2023 2023 2024 2022a 2022b 2021
Metric MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
1hTTE
96 0.367 0.395 0.385 0.402 0.386 0.405 0.385 0.400 0.460 0.447 0.384 0.402 0.426 0.446 0.397 0.412 0.395 0.407 0.438 0.433 0.395 0.424 0.449 0.459
192 0.414 0.420 0.443 0.430 0.441 0.436 0.439 0.430 0.512 0.477 0.436 0.429 0.454 0.464 0.446 0.441 0.490 0.477 0.494 0.466 0.469 0.470 0.500 0.482
336 0.445 0.434 0.512 0.470 0.487 0.458 0.480 0.449 0.546 0.496 0.638 0.469 0.493 0.487 0.489 0.467 0.510 0.480 0.547 0.495 0.490 0.477 0.521 0.496
720 0.444 0.459 0.497 0.476 0.503 0.491 0.462 0.456 0.544 0.517 0.521 0.500 0.526 0.526 0.513 0.510 0.568 0.538 0.586 0.538 0.598 0.544 0.514 0.512
Avg 0.417 0.427 0.459 0.444 0.454 0.447 0.442 0.434 0.516 0.484 0.495 0.450 0.475 0.480 0.461 0.457 0.491 0.475 0.516 0.483 0.498 0.484 0.496 0.487
2hTTE
96 0.290 0.340 0.289 0.342 0.297 0.349 0.301 0.351 0.308 0.355 0.340 0.374 0.372 0.424 0.340 0.394 0.332 0.387 0.322 0.364 0.358 0.397 0.346 0.388
192 0.375 0.392 0.378 0.397 0.380 0.400 0.378 0.397 0.393 0.405 0.402 0.414 0.492 0.492 0.482 0.479 0.451 0.457 0.405 0.414 0.429 0.439 0.456 0.452
336 0.423 0.435 0.432 0.434 0.428 0.432 0.422 0.431 0.427 0.436 0.452 0.452 0.607 0.555 0.591 0.541 0.466 0.473 0.435 0.445 0.496 0.487 0.482 0.486
720 0.443 0.449 0.464 0.464 0.427 0.445 0.427 0.444 0.436 0.450 0.462 0.468 0.824 0.655 0.839 0.661 0.485 0.471 0.445 0.457 0.463 0.474 0.515 0.511
Avg 0.383 0.404 0.390 0.409 0.383 0.407 0.382 0.406 0.391 0.411 0.414 0.427 0.574 0.531 0.563 0.519 0.433 0.446 0.402 0.420 0.437 0.449 0.450 0.459
1mTTE
96 0.322 0.361 0.317 0.356 0.334 0.368 0.336 0.369 0.352 0.374 0.338 0.375 0.365 0.387 0.346 0.374 0.337 0.374 0.353 0.370 0.379 0.419 0.505 0.475
192 0.357 0.383 0.367 0.384 0.377 0.391 0.378 0.389 0.390 0.393 0.374 0.387 0.403 0.408 0.382 0.391 0.382 0.398 0.389 0.387 0.426 0.441 0.553 0.496
336 0.382 0.401 0.391 0.406 0.426 0.420 0.411 0.410 0.421 0.414 0.410 0.411 0.436 0.431 0.415 0.415 0.420 0.423 0.421 0.408 0.445 0.459 0.621 0.537
720 0.445 0.435 0.454 0.441 0.491 0.459 0.469 0.441 0.462 0.449 0.478 0.450 0.489 0.462 0.473 0.451 0.490 0.471 0.481 0.441 0.543 0.490 0.671 0.561
Avg 0.376 0.395 0.382 0.397 0.407 0.410 0.399 0.402 0.406 0.407 0.400 0.406 0.423 0.422 0.404 0.408 0.407 0.417 0.412 0.402 0.448 0.452 0.588 0.517
2mTTE
96 0.174 0.255 0.175 0.257 0.180 0.264 0.181 0.267 0.183 0.270 0.187 0.267 0.197 0.296 0.193 0.293 0.186 0.275 0.183 0.266 0.203 0.287 0.255 0.339
192 0.239 0.299 0.240 0.302 0.250 0.309 0.247 0.308 0.255 0.314 0.249 0.309 0.284 0.361 0.284 0.361 0.259 0.323 0.248 0.305 0.269 0.328 0.281 0.340
336 0.301 0.340 0.303 0.343 0.311 0.348 0.309 0.347 0.309 0.347 0.321 0.351 0.381 0.429 0.382 0.429 0.349 0.386 0.309 0.343 0.325 0.366 0.339 0.372
720 0.395 0.396 0.392 0.396 0.412 0.407 0.406 0.404 0.412 0.404 0.408 0.403 0.549 0.522 0.558 0.525 0.559 0.511 0.410 0.400 0.421 0.415 0.433 0.432
Avg 0.277 0.322 0.277 0.324 0.288 0.332 0.286 0.332 0.290 0.334 0.291 0.333 0.353 0.402 0.354 0.402 0.339 0.374 0.288 0.328 0.305 0.349 0.327 0.371
rehtaeW
96 0.162 0.208 0.163 0.209 0.174 0.214 0.191 0.230 0.186 0.227 0.172 0.220 0.198 0.261 0.195 0.252 0.171 0.227 0.195 0.236 0.217 0.296 0.266 0.336
192 0.207 0.249 0.211 0.254 0.221 0.254 0.236 0.267 0.234 0.265 0.219 0.261 0.239 0.299 0.237 0.295 0.218 0.280 0.239 0.271 0.276 0.336 0.307 0.367
336 0.263 0.290 0.263 0.293 0.278 0.296 0.289 0.303 0.284 0.301 0.246 0.337 0.285 0.336 0.282 0.331 0.265 0.317 0.289 0.306 0.339 0.380 0.359 0.395
720 0.338 0.340 0.344 0.348 0.358 0.347 0.362 0.350 0.356 0.349 0.365 0.359 0.351 0.388 0.345 0.382 0.326 0.351 0.360 0.351 0.403 0.428 0.419 0.428
Avg 0.242 0.272 0.245 0.276 0.258 0.278 0.270 0.288 0.265 0.285 0.251 0.294 0.268 0.321 0.265 0.315 0.245 0.294 0.271 0.290 0.309 0.360 0.338 0.382
yticirtcelE
96 0.174 0.266 0.153 0.245 0.148 0.240 0.198 0.282 0.190 0.296 0.168 0.272 0.180 0.293 0.210 0.302 0.171 0.260 0.198 0.274 0.193 0.308 0.201 0.317
192 0.182 0.273 0.166 0.257 0.162 0.253 0.199 0.285 0.199 0.304 0.184 0.322 0.189 0.302 0.210 0.305 0.177 0.268 0.198 0.278 0.201 0.315 0.222 0.334
336 0.197 0.286 0.185 0.275 0.178 0.269 0.212 0.298 0.217 0.319 0.198 0.300 0.198 0.312 0.223 0.319 0.190 0.284 0.217 0.300 0.214 0.329 0.231 0.443
720 0.236 0.320 0.224 0.312 0.225 0.317 0.253 0.330 0.258 0.352 0.220 0.320 0.217 0.330 0.258 0.350 0.228 0.316 0.278 0.356 0.246 0.355 0.254 0.361
Avg 0.197 0.286 0.182 0.272 0.178 0.270 0.270 0.288 0.216 0.318 0.193 0.304 0.196 0.309 0.225 0.319 0.192 0.282 0.223 0.302 0.214 0.327 0.227 0.338
1stCount 17 22 4 3 5 4 3 2 0 0 1 0 1 0 0 0 1 0 0 0 0 0 0 0
4 EXPERIMENTS
Datasets We conduct extensive experiments on six real-world time series datasets, including
Weather, ETTh1, ETTh2, ETTm1, ETTm2 and Electricity for long-term forecasting. Following
previous work (Wu et al., 2021), we split the ETT series dataset into training, validation, and test
setsinaratioof6:2:2. Fortheremainingdatasets,weadoptasplitratioof7:1:2.
Baseline Wecarefullyselectelevenwell-acknowledgedmethodsinthefieldoflong-termtimese-
ries forecasting as our baselines, including (1) Transformer-based methods: Autoformer (2021),
FEDformer (2022b), PatchTST (2023), iTransformer (2024b); (2) MLP-based methods: DLin-
ear (2023) and TimeMixer (2024a) (3) CNN-based method: MICN (2023), TimesNet (2023); (4)
Frequency-based methods: FreTS (2024) and FiLM (2022a). And a time series foundation model
Time-FFM(2024a).
ExperimentalSettings Toensurefaircomparisons,weadoptthesamelook-backwindowlength
T = 96andthesamepredictionlengthF = {96,192,336,720}. WeutilizetheL2lossformodel
traininganduseMeanSquareError(MSE)andMeanAbsoluteError(MAE)metricstoevaluatethe
performanceofeachmethod.
4.1 MAINRESULTS
The comprehensive forecasting results are presented in Table 1, where the best results are high-
lighted in bold red and the second-best are underlined in blue. A lower MSE/MAE indicates a
more accurate prediction result. We observe that TimeKAN demonstrates superior predictive per-
formanceacrossalldatasets,exceptfortheElectricitydataset,whereiTransformerachievesthebest
result. ThisisduetoiTransformer’suseofchannel-wiseself-attentionmechanismstomodelinter-
variabledependencies,whichisparticularlyeffectiveforhigh-dimensionaldatasetslikeElectricity.
Additionally, both TimeKAN and TimeMixer perform consistently well in long-term forecasting
tasks,showcasingthegeneralizabilityofwell-designedtime-seriesdecompositionarchitecturesfor
accuratepredictions. Comparedwithotherstate-of-the-artmethods, TimeKANintroducesanovel
7

PublishedasaconferencepaperatICLR2025
Table2: AblationstudyoftheFrequencyUpsampling. Thebestresultsareinbold.
ETTh1 ETTh2 ETTm1 ETTm2 Weather Electricity
Datasets
Metric MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
LinearMapping 0.401 0.413 0.312 0.362 0.328 0.365 0.180 0.263 0.164 0.211 0.184 0.275
LinearInterpolation 0.383 0.398 0.296 0.347 0.336 0.370 0.181 0.263 0.165 0.210 0.196 0.277
TransposedConvolution 0.377 0.407 0.290 0.344 0.326 0.366 0.178 0.261 0.163 0.211 0.188 0.274
FrequencyUpsamping 0.367 0.395 0.290 0.340 0.322 0.361 0.174 0.255 0.162 0.208 0.174 0.266
Table3: AblationstudyoftheMulti-orderKANs. Thebestresultsareinbold.
ETTh1 ETTh2 ETTm1 ETTm2 Weather
Datasets
Metric MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
MLPs 0.376 0.397 0.298 0.348 0.319 0.361 0.178 0.264 0.162 0.211
FixedLow-orderKANs 0.376 0.398 0.292 0.341 0.327 0.366 0.175 0.257 0.164 0.211
FixedHigh-orderKANs 0.380 0.407 0.310 0.363 0.327 0.269 0.176 0.257 0.164 0.212
Multi-orderKANs 0.367 0.395 0.290 0.340 0.322 0.361 0.174 0.255 0.162 0.208
Decomposition-Learning-Mixing framework, closely integrating the characteristics of Multi-order
KANs with this hierarchical architecture, enabling superior performance in a wide range of long-
termforecastingtasks.
4.2 ABLATIONSTUDY
Inthissection,weinvestigateseveralkeycomponentsofTimeKAN,includingFrequencyUpsam-
pling,DepthwiseConvolutionandMulti-orderKANs.
FrequencyUpsampling ToinvestigatetheeffectivenessofFrequencyUpsampling,wecompared
it with three alternative upsampling methods that may not preserve frequency information before
and after transformation: (1) Linear Mapping; (2) Linear Interpolation; and (3) Transposed Con-
volution. As shown in Table 2, replacing Frequency Upsampling with any of these three methods
resultedinadeclineinperformance.Thisindicatesthattheseupsamplingtechniquesfailtomaintain
the integrity of frequency information after transforming, leading to the Decomposition-Learning-
Mixingframeworkineffective. ThisstronglydemonstratesthatthechosenFrequencyUpsampling,
asanon-parametricmethod,isanirreplaceablecomponentoftheTimeKANframework.
Multi-orderKANs WedesignedthefollowingmodulestoinvestigatetheeffectivenessofMulti-
orderKANs:(1)MLPs,whichmeansusingMLPtoreplaceeachKAN;(2)FixedLow-orderKANs,
which means using a KAN of order 2 at each frequency level; and (3) Fixed High-order KANs,
which means using a KAN of order 5 at each frequency level. The comparison results are shown
inTable3. Overall,Multi-orderKANsachievedthebestperformance. ComparedtoMLPs,Multi-
orderKANsperformsignificantlybetter,demonstratingthatwell-designedKANspossessstronger
representation capabilities than MLPs and are a compelling alternative. Both Low-order KANs
andHigh-orderKANsperformedworsethanMulti-orderKANs, indicatingthevalidityofourde-
signchoicetoincrementallyincreasetheorderofKANstoadapttotherepresentationofdifferent
frequency components. Thus, the learnable functions of KANs are indeed a double-edged sword;
achievingsatisfactoryresultsrequiresselectingtheappropriateleveloffunctioncomplexityforspe-
cifictasks.
DepthwiseConvolution ToassesstheeffectivenessofDepthwiseConvolution,wereplaceitwith
the following choice: (1) w/o Depthwise Convolution; (2) Standard Convolution; (3) Multi-head
Self-Attention. The results are shown in Table 4. Overall, Depthwise Convolution is the best
choice. We clearly observe that removing Depthwise Convolution or replacing it with Multi-head
Self-Attentionleadstoasignificantdropinperformance,highlightingtheeffectivenessofusingcon-
volutiontolearntemporaldependencies. WhenDepthwiseConvolutionisreplacedwithStandard
8

PublishedasaconferencepaperatICLR2025
Table4: AblationstudyoftheDepthwiseConvolution. Thebestresultsareinbold.
ETTh1 ETTh2 ETTm1 ETTm2 Weather
Datasets
Metric MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
w/oDepthwiseConv 0.379 0.397 0.296 0.343 0.337 0.373 0.180 0.263 0.168 0.211
StandardConv 0.364 0.393 0.295 0.345 0.323 0.364 0.180 0.264 0.162 0.210
Self-Attention 0.377 0.406 0.293 0.342 0.329 0.365 0.184 0.272 0.174 0.225
DepthwiseConv 0.367 0.395 0.290 0.340 0.322 0.361 0.174 0.255 0.162 0.208
0.195
0.190
0.185
0.180
0.175
0.170
0.165
0.160
48 96 192 336 512 720
T
ESM
ETTm2
0.21
TimeKAN
TimeMixer 0.20
iTransformer
PatchTST 0.19
0.18
0.17
0.16
0.15
0.14
48 96 192 336 512 720
T
ESM
Weather
TimeKAN
TimeMixer
iTransformer
PatchTST
Figure2: ComparisonofforecastingperformancebetweenTimeKANandotherthreemodelswith
varyinglook-backwindowsonETTm2andWeatherdatasets. Thelook-backwindowsareselected
tobeT ∈{48,96,192,336,512,720},andthepredictionlengthisfixedtoF =96.
Convolution, there are declines in most metrics, which implies that focusing on extracting tempo-
raldependenciesindividuallywithDepthwiseConvolution,withoutinterferencefrominter-channel
relationships,isareasonabledesign.
VaringLook-backWindow Inprinciple,extendingthelook-backwindowcanprovidemorein-
formationforpredictingfuture,leadingtoapotentialimprovementinforecastingperformance.Aef-
fectivelong-termTSFmethodequippedwithastrongtemporalrelationextractioncapabilityshould
beabletoimproveforecastingperformancewhenlook-backwindowlengthincreasing(Zengetal.,
2023). As a model based on frequency decomposition learning, TimeKAN should achieve better
predictive performance as the look-back window lengthens, since more incremental frequency in-
formationisavailableforprediction.TodemonstratethatTimeKANbenefitsfromalargerlook-back
window,weselectlook-backwindowlengthsfromT ={48,96,192,336,512,720}whilekeeping
thepredictionlengthfixedat96. AsdemonstratedinFigure2,ourTimeKANconsistentlyreduces
theMSEscoresasthelook-backwindowincreases,indicatingthatTimeKANcaneffectivelylearn
fromlongtimeseries.
4.3 MODELEFFICIENCY
WecompareTimeKANwithMLP-basedmethodTimeMierandTransformer-basedmethodsiTrans-
formerandPatchTST,intermsofmodelparametersandMultiply-AccumulateOperations(MACs),
tovalidatethatTimeKANisalightweightandefficientarchitecture. Toensureafaircomparison,
wefixthepredictionlengthF =96andinputlengthT =96,andsettheinputbatchsizeto32. The
comparisonresultsaresummarizedinTable5.ItisclearthatourTimeKANdemonstratessignificant
advantagesinboth modelparametersizeand MACs, particularlywhencomparedto Transformer-
based models. For instance, on the Electricity dataset, the parameter count of PatchTST is nearly
295 times that of TimeKAN, and its MACs are almost 118 times greater. Even when compared
totherelativelylightweightMLP-basedmethodTimeMixer, TimeKANshowssuperiorefficiency.
OntheWeatherdataset, TimeKANrequiresonly20.05%oftheparametersneededbyTimeMixer
andonly36.14%oftheMACs. Thisremarkableefficiencyadvantageisprimarilyattributedtothe
lightweightarchitecturaldesign. ThemaincomputationsoftheTimeKANmodelareconcentrated
9

PublishedasaconferencepaperatICLR2025
Table5: Acomparisonofmodelparameters(Params)andmultiply-accumulateoperations(MACs)
for TimeKAN and three other models. To ensure a fair comparison, we fix the prediction length
F = 96andtheinputlengthT = 96,andsettheinputbatchsizeto32. Thelowestcomputational
costishighlightedinbold.
ETTH1 ETTH2 ETTm1 ETTm2 Weather Electricity
Datasets
Metric Params MACs Params MACs Params MACs Params MACs Params MACs Params MACs
TimeMixer 75.50K 20.37M 75.50K 20.37M 75.50K 20.37M 77.77K 24.18M 104.43K 82.62M 106.83K 1.26G
iTransformer 841.57K 77.46M 224.22K 19.86M 224.22K 19.86M 224.22K 19.86M 4.83M 1.16G 4.83M 16.29G
PatchTST 3.75M 5.90G 10.06M 17.66G 3.75M 5.90G 10.06M 17.66G 6.90M 35.30G 6.90M 539.38G
TimeKAN 12.84K 7.63M 15.00K 8.02M 14.38K 7.63M 38.12K 16.66M 20.94K 29.86M 23.34K 456.50M
intheM-KANblock,andtheDepthwiseConvolutionweemployedsignificantlyreducesthenum-
berofparametersthroughgroupedoperations.Additionally,thepowerfulrepresentationcapabilities
affordedbyMulti-orderKANsallowustorepresenttimeserieswithveryfewneurons. Therefore,
we cannot overlook that TimeKAN achieves outstanding forecasting performance while requiring
minimalcomputationalresources.
5 CONCLUSION
WeproposedanefficientKAN-basedFrequencyDecompositionLearningarchitecture(TimeKAN)
for long-term time series forecasting. Based on Decomposition-Learning-Mixing architecture,
TimeKAN obtains series representations for each frequency band using a Cascaded Frequency
Decomposition blocks. Additionally. a Multi-order KAN Representation Learning blocks further
leverage the high flexibility of KAN to learn and represent specific temporal patterns within each
frequencyband. Finally,FrequencyMixingblocksrecombinethefrequencybandsintotheoriginal
format. Extensiveexperimentsonreal-worlddatasetsdemonstratethatTimeKANachievesthestate
oftheartforecastingperformanceandextremelylightweightcomputationalconsumption.
ACKNOWLEDGEMENTS
ThisworkissupportedbyShanghaiArtificialIntelligenceLaboratory. Thisworkwasdoneduring
SongtaoHuang’sinternshipatShanghaiArtificialIntelligenceLaboratory.
REFERENCES
Alexander Dylan Bodner, Antonio Santiago Tepsich, Jack Natan Spolski, and Santiago Pourteau.
Convolutionalkolmogorov-arnoldnetworks. arXivpreprintarXiv:2406.13155,2024.
TaoDai,BeiliangWu,PeiyuanLiu,NaiqiLi,JigangBao,YongJiang,andShu-TaoXia. Periodicity
decoupling framework for long-term series forecasting. In The Twelfth International Confer-
ence on Learning Representations, 2024. URL https://openreview.net/forum?id=
dp27P5HBBt.
Luo donghao and wang xue. ModernTCN: A modern pure convolution structure for general time
seriesanalysis.InTheTwelfthInternationalConferenceonLearningRepresentations,2024.URL
https://openreview.net/forum?id=vpJMJerXHU.
Mononito Goswami, Konrad Szafer, Arjun Choudhry, Yifu Cai, Shuo Li, and Artur Dubrawski.
Moment: A family of open time-series foundation models. In ICML, 2024. URL https:
//openreview.net/forum?id=FVvf69a5rx.
HongbinHuang,MinghuaChen,andXiaoQiao. Generativelearningforfinancialtimeserieswith
irregularandscale-invariantpatterns. InTheTwelfthInternationalConferenceonLearningRep-
resentations,2024. URLhttps://openreview.net/forum?id=CdjnzWsQax.
10

PublishedasaconferencepaperatICLR2025
Weiwei Jiang and Jiayun Luo. Graph neural network for traffic forecasting: A survey. Expert
Systems with Applications, 207:117921, 2022. ISSN 0957-4174. doi: https://doi.org/10.1016/
j.eswa.2022.117921. URL https://www.sciencedirect.com/science/article/
pii/S0957417422011654.
RemiLam,AlvaroSanchez-Gonzalez,MatthewWillson,PeterWirnsberger,MeireFortunato,Fer-
ran Alet, Suman Ravuri, Timo Ewalds, Zach Eaton-Rosen, Weihua Hu, Alexander Merose,
Stephan Hoyer, George Holland, Oriol Vinyals, Jacklynn Stott, Alexander Pritzel, Shakir Mo-
hamed,andPeterBattaglia. Learningskillfulmedium-rangeglobalweatherforecasting. Science,
382(6677):1416–1421,2023. doi: 10.1126/science.adi2336. URLhttps://www.science.
org/doi/abs/10.1126/science.adi2336.
Chenxin Li, Xinyu Liu, Wuyang Li, Cheng Wang, Hengyu Liu, and Yixuan Yuan. U-kan
makes strong backbone for medical image segmentation and generation. arXiv preprint
arXiv:2406.02918,2024.
Ziyao Li. Kolmogorov-arnold networks are radial basis function networks. arXiv preprint
arXiv:2405.06721,2024.
Shengsheng Lin, Weiwei Lin, Wentai Wu, Haojun Chen, and Junjie Yang. SparseTSF: Modeling
long-termtimeseriesforecastingwith*1k*parameters.InForty-firstInternationalConferenceon
MachineLearning,2024. URLhttps://openreview.net/forum?id=54NSHO0lFe.
MinhaoLiu,AilingZeng,MuxiChen,ZhijianXu,QiuxiaLai,LingnaMa,andQiangXu. Scinet:
Time series modeling and forecasting with sample convolution and interaction. Advances in
NeuralInformationProcessingSystems,35:5816–5828,2022.
Qingxiang Liu, Xu Liu, Chenghao Liu, Qingsong Wen, and Yuxuan Liang. Time-FFM: To-
wards LM-empowered federated foundation model for time series forecasting. In The Thirty-
eighth Annual Conference on Neural Information Processing Systems, 2024a. URL https:
//openreview.net/forum?id=HS0faHRhWD.
Yong Liu, Tengge Hu, Haoran Zhang, Haixu Wu, Shiyu Wang, Lintao Ma, and Mingsheng Long.
itransformer: Inverted transformers are effective for time series forecasting. In The Twelfth In-
ternationalConferenceonLearningRepresentations, 2024b. URLhttps://openreview.
net/forum?id=JePfAI8fah.
Ziming Liu, Yixuan Wang, Sachin Vaidya, Fabian Ruehle, James Halverson, Marin Soljacˇic´,
Thomas Y Hou, and Max Tegmark. Kan: Kolmogorov-arnold networks. arXiv preprint
arXiv:2404.19756,2024c.
Yuqi Nie, Nam H Nguyen, Phanwadee Sinthong, and Jayant Kalagnanam. A time series is worth
64 words: Long-term forecasting with transformers. In The Eleventh International Confer-
ence on Learning Representations, 2023. URL https://openreview.net/forum?id=
Jbdc0vTOcol.
KhemrajShukla,JuanDiegoToscano,ZhichengWang,ZongrenZou,andGeorgeEmKarniadakis.
Acomprehensiveandfaircomparisonbetweenmlpandkanrepresentationsfordifferentialequa-
tionsandoperatornetworks. arXivpreprintarXiv:2406.02917,2024.
SidharthSS. Chebyshevpolynomial-basedkolmogorov-arnoldnetworks: Anefficientarchitecture
fornonlinearfunctionapproximation. arXivpreprintarXiv:2405.07200,2024.
HuiqiangWang,JianPeng,FeihuHuang,JinceWang,JunhuiChen,andYifeiXiao. MICN:Multi-
scalelocalandglobalcontextmodelingforlong-termseriesforecasting. InTheEleventhInterna-
tional Conference on Learning Representations, 2023. URL https://openreview.net/
forum?id=zt53IDUR1U.
Shiyu Wang, Haixu Wu, Xiaoming Shi, Tengge Hu, Huakun Luo, Lintao Ma, James Y. Zhang,
and JUN ZHOU. Timemixer: Decomposable multiscale mixing for time series forecasting. In
The Twelfth International Conference on Learning Representations, 2024a. URL https://
openreview.net/forum?id=7oLshfEIC2.
11

PublishedasaconferencepaperatICLR2025
Yizheng Wang, Jia Sun, Jinshuai Bai, Cosmin Anitescu, Mohammad Sadegh Eshaghi, Xiaoying
Zhuang, Timon Rabczuk, and Yinghua Liu. Kolmogorov arnold informed neural network: A
physics-informed deep learning framework for solving pdes based on kolmogorov arnold net-
works. arXivpreprintarXiv:2406.11045,2024b.
Haixu Wu, Jiehui Xu, Jianmin Wang, and Mingsheng Long. Autoformer: Decomposi-
tion transformers with auto-correlation for long-term series forecasting. In M. Ranzato,
A. Beygelzimer, Y. Dauphin, P.S. Liang, and J. Wortman Vaughan (eds.), Advances in Neu-
ral Information Processing Systems, volume 34, pp. 22419–22430. Curran Associates, Inc.,
2021. URL https://proceedings.neurips.cc/paper_files/paper/2021/
file/bcc0d400288793e8bdcd7c19a8ac0c2b-Paper.pdf.
Haixu Wu, Tengge Hu, Yong Liu, Hang Zhou, Jianmin Wang, and Mingsheng Long. Timesnet:
Temporal 2d-variation modeling for general time series analysis. In The Eleventh International
ConferenceonLearningRepresentations,2023.URLhttps://openreview.net/forum?
id=ju_Uqw384Oq.
KunpengXu,LifeiChen,andShengruiWang.Arekaneffectiveforidentifyingandtrackingconcept
driftintimeseries? arXivpreprintarXiv:2410.10041,2024a.
Zhijian Xu, Ailing Zeng, and Qiang Xu. FITS: Modeling time series with $10k$ parameters. In
The Twelfth International Conference on Learning Representations, 2024b. URL https://
openreview.net/forum?id=bWcnvZ3qMb.
KunYi,QiZhang,WeiFan,ShoujinWang,PengyangWang,HuiHe,NingAn,DefuLian,Long-
bingCao,andZhendongNiu. Frequency-domainmlpsaremoreeffectivelearnersintimeseries
forecasting. AdvancesinNeuralInformationProcessingSystems,36,2024.
Linfei Yin, Xinghui Cao, and Dongduan Liu. Weighted fully-connected regression networks
for one-day-ahead hourly photovoltaic power forecasting. Applied Energy, 332:120527, 2023.
ISSN0306-2619. doi: https://doi.org/10.1016/j.apenergy.2022.120527. URLhttps://www.
sciencedirect.com/science/article/pii/S0306261922017846.
Ailing Zeng, Muxi Chen, Lei Zhang, and Qiang Xu. Are transformers effective for time series
forecasting? In Proceedings of the AAAI conference on artificial intelligence, volume 37, pp.
11121–11128,2023.
G.Peter Zhang. Time series forecasting using a hybrid arima and neural network
model. Neurocomputing, 50:159–175, 2003. ISSN 0925-2312. doi: https://doi.org/10.
1016/S0925-2312(01)00702-0. URL https://www.sciencedirect.com/science/
article/pii/S0925231201007020.
HaoyiZhou,ShanghangZhang,JieqiPeng,ShuaiZhang,JianxinLi,HuiXiong,andWancaiZhang.
Informer:Beyondefficienttransformerforlongsequencetime-seriesforecasting. InProceedings
oftheAAAIconferenceonartificialintelligence,volume35,pp.11106–11115,2021.
Tian Zhou, Ziqing Ma, Qingsong Wen, Liang Sun, Tao Yao, Wotao Yin, Rong Jin, et al. Film:
Frequencyimprovedlegendrememorymodelforlong-termtimeseriesforecasting. Advancesin
neuralinformationprocessingsystems,35:12677–12690,2022a.
TianZhou,ZiqingMa,QingsongWen,XueWang,LiangSun,andRongJin.Fedformer:Frequency
enhanceddecomposedtransformerforlong-termseriesforecasting. InInternationalconference
onmachinelearning,pp.27268–27286.PMLR,2022b.
12

PublishedasaconferencepaperatICLR2025
A ADDITIONAL MODEL ANALYSIS
Table6: Fullcomparisonresultsofmodelparameters(Params)andmultiply-accumulateoperations
(MACs)forTimeKANandothermodels. Toensureafaircomparison,wefixthepredictionlength
F = 96andtheinputlengthT = 96,andsettheinputbatchsizeto32. Thelowestcomputational
costishighlightedinbold.
ETTH1 ETTH2 ETTm1 ETTm2 Weather Electricity
Datasets
Metric Params MACs Params MACs Params MACs Params MACs Params MACs Params MACs
TimeMixer 75.50K 20.37M 75.50K 20.37M 75.50K 20.37M 77.77K 24.18M 104.43K 82.62M 106.83K 1.26G
iTransformer 841.57K 77.46M 224.22K 19.86M 224.22K 19.86M 224.22K 19.86M 4.83M 1.16G 4.83M 16.29G
PatchTST 3.75M 5.90G 10.06M 17.66G 3.75M 5.90G 10.06M 17.66G 6.90M 35.30G 6.90M 539.38G
TimesNet 605.48K 18.13G 1.19M 36.28G 4.71M 144G 1.19M 36.28G 1.19M 36.28G 150.30M 4.61T
MICN 25.20M 71.95G 25.20M 71.95G 25.20M 71.95G 25.20M 71.95G 111.03K 295.07M 6.64M 19.5G
Dlinear 18.62K 0.6M 18.62K 0.6M 18.62K 0.6M 18.62K 0.6M 18.62K 0.6M 18.62K 0.6M
FreTS 3.24M 101.46M 3.24M 101.46M 3.24M 101.46M 3.24M 101.46M 3.24M 101.46M 3.24M 101.46M
FILM 12.58M 2.82G 12.58M 2.82G 12.58M 2.82G 12.58M 2.82G 12.58M 8.46G 12.58M 8.46G
FEDFormer 23.38M 24.96G 23.38M 24.96G 23.38M 24.96G 23.38M 24.96G 23.45M 25.23G 24.99M 30.89G
AutoFormer 10.54M 22.82G 10.54M 22.82G 10.54M 22.82G 10.54M 22.82G 10.61M 23.08G 12.14M 28.75G
TimeKAN 12.84K 7.63M 15.00K 8.02M 14.38K 7.63M 38.12K 16.66M 20.94K 29.86M 23.34K 456.50M
A.1 COMPUTATIONALCOMPLEXITYANALYSIS
InourTimeKAN,themaincomputationalcomplexityliesinFastFourierTransform(FFT),Depth-
wiseConvolutionblockandMulti-orderKANblock. ConsideratimeserieswithlengthLandthe
hidden state of each time point is D. For FFT, the computation complexity is O(L logL). For
Depthwise Convolution block, if we set the convolutional kernel to M and stride to 1, the com-
plexityisO(LDM). Finally,assumingthatthehighestorderofChebyshevpolynomialsisK,the
complexityofMulti-orderKANblockisO(LD2K).SinceM,D,Kareconstantsthatareindepen-
dentoftheinputlengthL,thecomputationalcomplexityofboththeDepthwiseConvolutionblock
andtheMulti-orderKANblockcanbereducedtoO(L),whichislinearaboutthesequencelength.
Insummary,theoverallcomputationalcomplexityismax(O(LlogL),O(L)=O(LlogL). When
theinputisamultivariatesequencewithM variables,thecomputationalcomplexitywillexpandto
O(MLlogL)duetoourvariable-independentstrategy.
A.2 MODELEFFICIENCY
Here, we provide the complete results of model efficiency in terms of parameters and MACs in
Table6. Ascanbeseen,exceptforDLinear,ourTimeKANconsistentlydemonstratesasignificant
advantage in both parameter count and MACs compared to any other model. DLinear is a model
consistingofonlyasinglelinearlayer,whichmakesitthemostlightweightintermsofparameters
andMACs. However,theperformanceofDLinearalreadyshowsasignificantgapwhencompared
to state-of-the-art methods. Therefore, our TimeKAN actually achieves superior performance in
bothforecastingaccuracyandefficiency.
A.3 ERRORBARS
To evaluate the robustness of TimeKAN, we repeated the experiments on three randomly selected
seedsandcompareditwiththesecond-bestmodel(TimeMixer). Wereportthemeanandstandard
deviationoftheresultsacrossthethreeexperiments,aswellastheconfidencelevelofTimeKAN’s
superiorityoverTimeMixer. Theresultsareaveragedoverfourpredictionhorizons(96, 192, 336,
and 720). As shown in the Table 7, in most cases, we have over 90% confidence that TimeKAN
outperformsthesecond-bestmodelanddemonstratesgoodrobustneofTimeKAN.
13

PublishedasaconferencepaperatICLR2025
Table7: StandarddeviationandstatisticaltestsforourTimeKANmethodandsecond-bestmethod
(TimeMixer)onfivedatasets.
Metric MSE MAE
Dataset TimeKAN TimeMixer Confidence TimeKAN TimeMixer Confidence
ETTh1 0.422±0.004 0.462±0.006 99% 0.430±0.002 0.448±0.004 99%
ETTh2 0.387±0.003 0.392±0.003 99% 0.408±0.003 0.412±0.004 90%
ETTm1 0.378±0.002 0.386±0.003 99% 0.396±0.001 0.399±0.001 99%
ETTm2 0.278±0.001 0.278±0.001 — 0.324±0.001 0.325±0.001 90%
Weather 0.243±0.001 0.245±0.001 99% 0.273±0.001 0.276±0.001 99%
Table8: ComparisonontheElectricitydatasetwhenthelookbackwindowisexpandedto512.
96 192 336 720
Models
MSE MAE MSE MAE MSE MAE MSE MAE
MOMENT 0.136 0.233 0.152 0.247 0.167 0.264 0.205 0.295
TimeMixer 0.135 0.231 0.149 0.245 0.172 0.268 0.203 0.295
TimeKAN 0.133 0.230 0.149 0.247 0.165 0.261 0.203 0.294
A.4 FREQUENCYLEARNINGWITHLONGERWINDOW
In Table 1, TimeKAN performs relatively poorly on the Electricity dataset. We infer that its poor
performanceontheelectricitydatasetisduetotheoverlyshortlook-backwindow(T =96),which
cannot provide sufficient frequency information. To verify this, we compare the average number
of effective frequency components under a specific look-back window. Specifically, we randomly
select a sequence of length T from the electricity dataset and transform it into the frequency do-
mainusingFFT.Wedefineeffectivefrequenciesasthosewithamplitudesgreaterthan0.1timesthe
maximumamplitude. Then,wetaketheaveragenumberofeffectivefrequenciesobtainedacrossall
variablestoreflecttheamountofeffectivefrequencyinformationprovidedbythesequence. When
T = 96 (the setting in this paper), the average number of effective frequencies is 10.69. When
weextendthesequencelengthto512,theaveragenumberofeffectivefrequenciesbecomes19.74.
Therefore,theeffectivefrequencyinformationprovidedby512timestepsisnearlytwicethatof96
timesteps. ThisindicatesthatT =96losesasubstantialamountofeffectiveinformation.
TovalidatewhetherusingT =512allowsustoleveragemorefrequencyinformation,weextendthe
look-backwindowofTimeKANto512ontheelectricitydatasetandcompareitwiththestate-of-
the-artmethodsTimeMixerandtimeseriesfoundatiommodelMOMENT(Goswamietal.,2024).
TheresultsareshowninTable8.AlthoughTimeKANperformssignificantlyworsethanTimeMixer
whenT =96,itachievesthebestperformanceontheelectricitydatasetwhenthelook-backwindow
is extended to 512. This also demonstrates that TimeKAN can benefit significantly from richer
frequencyinformation.
A.5 IMPACTOFNUMBEROFFREQUENCYBANDS
To explore the impact of the number of frequency bands on performance, we set the number of
frequencybandsto2,3,4,and5. Theeffectsofdifferentfrequencybanddivisionsonperformance
are shown in the Table 9. As we can see, in most cases, dividing the frequency bands into 3 or 4
layers yields the best performance. This aligns with our prior intuition: dividing into two bands
resultsinexcessivefrequencyoverlap,whiledividingintofivebandsleadstotoolittleinformation
within each band, making it difficult to accurately model the information within that frequency
range.
14

PublishedasaconferencepaperatICLR2025
Table9:Impactofnumberoffrequencybandsonperformanceunderthe96-to-96predictionsetting.
ETTh2 Weather Electricity
NumberofFrequency
MSE MAE MSE MAE MSE MAE
2 0.292 0.340 0.164 0.209 0.183 0.270
3 0.290 0.339 0.163 0.209 0.177 0.268
4 0.290 0.340 0.162 0.208 0.174 0.266
5 0.295 0.346 0.164 0.211 0.177 0.273
B MATHEMATICAL DETAILS
B.1 KOLMOGOROV-ARNOLDNETWORK
Kolmogorov-Arnoldrepresentationtheoremstatesthatanymultivariatecontinuousfunctioncanbe
expressed as a combination of univariate functions and addition operations. More specifically, a
multivariatecontinuousfunctiong :[0,1]n ⇒Rcanbedefinedas:
2n+1 n
(cid:88) (cid:16)(cid:88) (cid:17)
g(x)=g(x ,··· ,x )= Φ ϕ (x ) (13)
1 n i ij j
i=1 j=1
where ϕ and Φ are univariate functions. Following the pattern of MLP, Kolmogorov-Arnold
ij i
Network(KAN)(Liuetal.,2024c)extendstheKolmogorov-Arnoldtheoremtodeeprepresentations,
i.e.,stackedmultilayerKolmogorov-Arnoldrepresentations.AssumethatKANiscomposedofL+1
layerneuronsandthenumberofneuronsinlayerlisn . Thetransmissionrelationshipbetweenthe
l
j-thneuroninlayerl+1andallneuronsinlayerlcanbeexpressedas:
(cid:88)
nl
x = ϕ (x ) (14)
l+1,j l,j,i l,i
i=1
We can simply understand that each neuron is connected to other neurons in the previous layer
through a univariate function ϕ. Similar to MLP, the computation of all neurons at layer l can be
reorganizedasafunctionmatrixmultiplicationΦ
l−1
. Therefore,givenainputvectorx∈Rn0,the
finaloutputofKANnetworkis:
KAN(x)=(Φ ◦···◦Φ ◦Φ )x (15)
L−1 1 0
In vanilla KAN (Liu et al., 2024c), the univariate function ϕ is parametrized using B-splines,
l,j,i
whichisaclassofsmoothcurvesconstructedviasegmentedpolynomialbasisfunctions. Toensure
thestabilityandenhancetherepresentationalcapacity,KANoverlaysthesplinefunctiononafixed
basisfunctionb,whichistypicallytheSiLUfunction:
ϕ(x)=w b(x)+w spline(x) (16)
b s
(cid:88)
spline(x)= c B (x) (17)
i i
i
where w and w are learnable weights and spline(x) is the spline function constructed from the
b s
linear combination of B-spline basis functions B . However, the complex recursive computation
i
processofhigh-orderB-splinefunctionshinderstheefficiencyofKAN.Therefore,inthiswork,we
adoptthesimplerChebyshevpolynomialastheunivariatefunctiontoreplacetheB-splinefunction
(SS,2024). TheunivariatefunctiondefinedbytheChebyshevpolynomialisgivenasfollows:
T (x)=cos(karccos(x)) (18)
k
Here, k represents the order of the polynomial. Then, we consider the univariate function Φ as a
linearcombinationofChebyshevpolynomialswithdifferentorders:
(cid:88)
nl
(cid:88)
nl
(cid:88)
K
x = ϕ (x )= Θ T (tanh(x )) (19)
l+1,j l,j,i l,i i,k k l,i
i=1 i=1k=0
Where Θ is the coefficients of k-th order Chebyshev polynomials acting on the x and tanh
i,k l,i
is the tanh activation function used to normalize the inputs to between -1 and 1. By adjusting the
highest order of the Chebyshev polynomial K, we can control the fitting capability of KAN. This
alsoinspirestourdesignoftheMulti-orderKANtodynamicallyrepresentdifferentfrequencies.
15

PublishedasaconferencepaperatICLR2025
B.2 FOURIERTRANSFORM
Timeseriesareoftencomposedofmultiplefrequencycomponentssuperimposedoneachother,and
itisdifficulttoobservetheseindividualfrequencycomponentsdirectlyinthetimedomain. There-
fore,transformingatimeseriesfromthetimedomaintothefrequencydomainforanalysisisoften
necessary. TheDiscreteFourierTransform(DFT)isacommonlyuseddomaintransformationalgo-
rithmthatconvertsadiscrete-timesignalfromthetimedomaintothecomplexfrequencydomain.
Mathematically,givenasequenceofrealnumbersx[n]intimedomain,wheren=0,1,...,N −1
theDFTprocesscanbedescribedas:
N−1 N−1 (cid:18) (cid:18) (cid:19) (cid:18) (cid:19)(cid:19)
X[k]= (cid:88) x[n]·e−i2 N πkn = (cid:88) x[n] cos 2π kn −isin 2π kn , k =0,1,...,N−1
N N
n=0 n=0
(20)
whereX[k]isthek-thfrequencycomponentoffrequencydomainsignalandiistheimaginaryunit.
Similarly, we can use Inverse DFT (iDFT) to convert a frequency domain signal back to the time
domain.
N−1 N−1 (cid:18) (cid:18) (cid:19) (cid:18) (cid:19)(cid:19)
x[n]= 1 (cid:88) X[k]·ei2 N πkn = 1 (cid:88) X[k] cos 2π kn +isin 2π kn (21)
N N N N
k=0 k=0
ThecomputationalcomplexityoftheDFTistypicallyO(N2)(Zhouetal.,2022b). Inpractice,we
usetheFastFourierTransform(FFT)toefficientlycomputetheDiscreteFourierTransform(DFT)
ofcomplexsequences,whichreducesthecomputationalcomplexitytoO(N logN). Additionally,
byemployingtheRealFFT(rFFT),wecancompressaninputsequenceofN realnumbersintoa
signalsequenceinthecomplexfrequencydomaincontainingN/2+1frequencycomponents.
16