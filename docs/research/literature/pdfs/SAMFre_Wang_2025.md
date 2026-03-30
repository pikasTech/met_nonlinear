# Page 1

5202
yaM
32
]GL.sc[
1v23571.5052:viXra
TimeCF: A TimeMixer-Based Model with adaptive Convolution and
Sharpness-Aware Minimization Frequency Domain Loss for
long-term time seris forecasting
BinWanga, HemingYanga and JinfangShenga,∗
aSchoolofComputerScienceandEngineering,CentralSouthUniversity,ChangSha,410000,HuNan,China
ARTICLE INFO ABSTRACT
Keywords: Recentstudieshaveshownthatbyintroducingpriorknowledge,multi-scaleanalysisofcomplex
Timeseriesforecast andnon-stationarytimeseriesinrealenvironmentscanachievegoodresultsinthefieldoflong-
FourierTransform termforecasting.However,affectedbychannel-independentmethods,modelsbasedonmulti-scale
Convolution analysismayproducesuboptimalpredictionresultsduetotheautocorrelationbetweentimeseries
Sharpness-awareminimization labels,whichinturnaffectsthegeneralizationabilityofthemodel.Toaddressthischallenge,
weareinspiredbytheideaofsharpness-awareminimizationandtherecentlyproposedFreDF
methodanddesignadeeplearningmodelTimeCFforlong-termtimeseriesforecastingbased
ontheTimeMixer,combinedwithourdesignedadaptiveconvolutioninformationaggregation
moduleandSharpness-AwareMinimizationFrequencyDomainLoss(SAMFre).Specifically,
TimeCFfirstdecomposestheoriginaltimeseriesintosequencesofdifferentscales.Next,the
same-sizedconvolutionmodulesareusedtoadaptivelyaggregateinformationofdifferentscales
onsequencesofdifferentscales.Then,decomposingeachsequenceintoseasonandtrendpartsand
thetwopartsaremixedatdifferentscalesthroughbottom-upandtop-downmethodsrespectively.
Finally,differentscalesareaggregatedthroughaFeed-ForwardNetwork.What’smore,extensive
experimentalresultsondifferentreal-worlddatasetsshowthatourproposedTimeCFhasexcellent
performanceinthefieldoflong-termforecasting.
1. Introduction
With the development of information technology in the past decade, time series forecasting, a field of great
significancetohumanlife,hasbeensupportedbyinformationtechnologyresourcessuchascomputingpowerand
algorithmsandhasplayedanindispensableroleinkeyareasrelatedtohumanlivingstandards,suchasfinanciallevel
prediction(Sonkavde,Dharrao,Bongale,Deokate,DoreswamyandBhat(2023)),trafficflowplanning(Huo,Zhang,
Wang,Gao,HuandYin(2023);Huang,Zhang,Feng,YeandLi(2023)),weatherforecast(Bi,Xie,Zhang,Chen,Gu
andTian(2023)),watertreatment(Farhi,Kohen,MamaneandShavitt(2021);Afan,Mohtar,Khaleel,Kamel,Mansoor,
Alsultani,Ahmed,SherifandEl-Shafie(2024)),energyandpowerresourceallocation(AlkhayatandMehmood(2021);
Yin,CaoandLiu(2023)).Sincethebeginoftimeseriesforecasting,therearemainlythefollowingmodelarchitectures:
ModelsbasedonCNN(Li,Jian,Wan,Geng,Fang,Chen,Gao,JiangandZhu(2024)),ModelsbasedonRNN(Salinas,
Flunkert,GasthausandJanuschowski(2020)),ModelsbasedonTransformer(Liang,Yang,DengandYang(2024))and
ModelsbasedonMLP(Challu,Olivares,Oreshkin,RamÃŋrez,CansecoandDubrawski(2023)).
Althoughresearchershaveproposedavarietyofmethodstosolvetheproblemoftimeseriesforecasting,theprocess
ofcapturingandbuildingamodeloftimeseriesfromthepasttothefutureischallengingbecausethenaturalsequence
oftimeserieshascomplexandnon-stationarypropertiesandthenoisefromthedataacquisitionequipmentcanaffect
thepredictionresults.Inordertosolvethisproblem,thecurrentmainstreamresearchcanbedividedintotwocategories:
oneisbasedontheTransformer(Vaswani,Shazeer,Parmar,Uszkoreit,Jones,Gomez,KaiserandPolosukhin(2017)),
whichachievesthefittingoftimeseriesthroughalargenumberofparameters.However,althoughthelargenumberof
parametersoftheTransformercansolvetheproblemofcomplexandnon-stationarytimeseriestosomeextent,itseasy
overfittingandslowtrainingspeedhavenotbeenreliablysolved.Therefore,afterfullystudyingthecomponentsof
timeseries,researchersusethepriorknowledgeofphysicsandmathematicstodecomposetimeseriesintosimpler
componentstoreducethedifficultyofthepredictionprocess.Onthisbasis,TimeMixer(Wang,Wu,Shi,Hu,Luo,Ma,
∗Correspondingauthor
wb_csut@csu.edu.cn(B.Wang);244712142@csu.edu.cn(H.Yang);jfsheng@csu.edu.cn(J.Sheng)
ORCID(s):0009-0002-0536-2898(B.Wang);0009-0009-1683-6068(H.Yang);0000-0002-6533-7822(J.Sheng)
Bin Wang et al.: PreprintsubmittedtoElsevier Page1of10

---

# Page 2

ZhangandZhou(2024))furtherintroducedtheideaofmulti-scaledecomposition,andTimeKAN(Huang,Zhao,Liand
Bai(2025))proposedmodelingbasedonfrequenciesofdifferentscalesbasedonTimeMixer.Insummary,current
researchershopetosimplifytheoriginaltimeseriestoprovideadditionalpriorinformationforthetimeseriesmodel,
therebyimporvingthepredictionaccuracyofthetimeseriesforecastingmodel.
Itisundeniablethatthemodelbasedontheideaofchannelindependencedoesobtainmoreaccurateresultsunder
certainconditions,buttheactualtimeseriesisaserieswithhighautocorrelation.Thisautocorrelationismanifestedin
thatitisnotonlycorrelatedintheorderoftime,butalsohasacertaindegreeofcorrelationbetweenthelabelsofthe
sequence.Therefore,underthepremiseofchannelindependence,theautocorrelationbetweenlabelshasnotbeenfully
processed,whichmaycauseacertaindegreeofdistortionintheresultsofthemodel.Fortunately,amethodcalled
FreDF(Wang,Pan,Chen,Yang,Zhang,Yang,Liu,LiandTao(2024))hasrecentlybeenappliedtothefieldoftime
seriesforecasting.ItusesFourierorfastFouriertransformtotransformthesequencelabelsfromthetimedomaintothe
frequencydomainwithoutchangingthemodelstructuretodealwiththeautocorrelationinthetimeseries.Inaddition,
wenotethatanideacalledsharpness-awareminimization(SAM)(Foret,Kleiner,MobahiandNeyshabur(2021))canbe
combinedwithFreDFtoreducethesharpnessofthelosssothatthemodelhasbettergeneralizationability.Atthe
sametime,inspiredbytheideaofattentionmechanisminTransformerandtheideaofreceptivefieldinCNNfield,
wefoundthatneighboringandglobalinformationcanalsobeusedintimeseriestosupplementinformationinthe
predictionprocess.Therefore,weproposetouseconvolutionkernelsofthesamesizeatdifferentscalestoobtainglobal
informationatlow-frequencyscalesandneighboringinformationathigh-frequencyscalestoachievetheaggregationof
globalandlocalinformationwithasmallnumberofparameters.
Combining the advantages of the above technologies, we propose a frequency-independent multi-scale hybrid
architecture (TimeCF) based on the TimeMixer model to solve the problems of global and local information loss,
autocorrelationbetweensequencelabelsintimeseriesforecastingandgeneralizationability.Intermsofmodelstructure,
TimeCFisbasedontheTimeMixermodelarchitecture.First,itusesthedownsamplingmethodtogeneratetimeseries
atmultiplescales.Secondly,throughthePDMC(PastDecomposableMixingwithadaptiveConv)moduledesignedby
us,wefirstusetheconvolutionoperationofthesameconvolutionkernelonthesequencesofdifferentscalestoachieve
adaptiveinformationaggregationbetweendifferentscales.Then,accordingtopriorknowledge,theseasonandtrendof
theinputsequencearedecomposedseparately.Throughourdesign,PDMCobtainsinformationofdifferentreceptive
fieldsaccordingtodifferentinputscalesanddecomposesthesequencesofdifferentscalesintoseasonalandtrend
partstoachievemoredetailedmodeling.Inthepredictionstage,theoutputpredictionlayeraggregatestheprediction
componentsofdifferentscalestoutilizethecomplementarypredictioncapabilitiesbetweenmulti-scalesequencesto
achieveaccurateprediction.
Ingeneral,ourcontributionsareasfollows:
1. Different from previous methods, we propose to use adaptive convolution modules to achieve information
aggregationofreceptivefieldsofdifferentscalesbasedonsamplingresultsofdifferentscales.What’smore,
weusethetransformationfromtimedomaintofrequencydomaintosolvethechallengesbroughtbycomplex
informationcouplingintimeseries.
2. WeproposedarelativelylightweighttimeseriespredictionmodelTimeCFandintroducedthereceptivefieldidea
intheCNNfieldtomaximizetheuseofinformationaggregationatdifferentscalestosupplementglobaland
localinformation.AndbasedontheideasofFreDFandSAM,weachievedthedecouplingoftheautocorrelation
betweenthelabelsofthetimeseriesandtheimprovementofthemodel’sgeneralizationability.
3. TimeCFshowsexcellentperformanceinmultipletimeseriesforecastingtasksanddatasets,whileachievinga
relativelybalancedstatebetweenmodelparametersandpredictionaccuracy.
2. RelatedWork
2.1. MainstreamModelArchitecture
Thecoreofthetimeseriesforecastingmodelistohaveefficientandstablepatternextractionandmodelingcapabilities
indifferenttimeseries,soastomodelandpredictcomplextimeseries.TraditionalmodelssuchasARIMA(Zhang
(2003))andLSTM(HochreiterandSchmidhuber(1997))canaccuratelypredicttimeserieswithsimplecyclesandtrends,
butthesemodelsarelimitedbyparametersandmodelstructuressothepredictioneffectfornonlinearanddynamictime
seriesisoftenunsatisfactory.Inrecentyears,deeplearningmethodshavebeguntomakegreatstridesinthedirection
oftimeseriesforecasting.FortheTransformer,researchershaveproposedmanymethodstoapplyittothefieldoftime
seriesprediction:Autoformer(Wu,Xu,WangandLong(2021))proposedanautocorrelationmechanismtoreducethe
Bin Wang et al.: PreprintsubmittedtoElsevier Page 2 of 10

---

# Page 3

timecomplexityofthemodelto𝑂(𝑛⋅𝑙𝑔(𝑛)).SAMformer(Ilbert,Odonnat,Feofanov,Virmaux,Paolo,Palpanasand
Redko(2024))solvedtheinstabilityproblemduringlargemodeltrainingbyusingSharpness-AwareMinimization.
Informer(Zhou,Zhang,Peng,Zhang,Li,XiongandZhang(2021))usedProbSpareself-attentionandSelf-attention
Distillingtoenableittoeffectivelyhandleoverlylonginputsequences.iTransformer(Liu,Hu,Zhang,Wu,Wang,
MaandLong(2024))invertedthetimeseriesandthenusedtheEncoderforprediction.Mamba(GuandDao(2023))
combinedtheparallelizationcapabilityofTransformerandthehistoricalinformationcontrolcapabilityofRNN,and
basedontheideaofSSM,itwasabletohandlethecorrelationproblembetweenvariablesatalowercost.PatchTST(Nie,
Nguyen,SinthongandKalagnanam(2023))regardedthetimeseriesasmultipleindependenttimeperiodsofchannels,
andcombineditwithTransformerforprediction,achievinggoodresults.Andsomeresearchershavefoundthatthe
useofCNNideascanbetterconstructtherelationshipbetweenlabelsandtimestepsintimeseries:MICN(Wang,
Peng, Huang, Wang, Chen and Xiao (2023)) introduces the idea of image processing and captures information of
differentreceptivefieldsthroughconvolutionkernelsofdifferentsizes.TimesNet(Wu,Hu,Liu,Zhou,WangandLong
(2023))performsFouriertransformonthetimeseriesandselectsitsTop-kcycles,thenexpandseachcycleintoa
two-dimensionalimageandusesa2D-kernelconvolutionkernelforfeatureextraction.ModernTCN(donghaoandxue
(2024))proposestouselargeconvolutionkernelsonthetimedimensionofthetimeseriessothatthemodelcancapture
dependenciesacrosstimeandvariablesatthesametime.Inaddition,researchershavealsoproposedsomemodels
thatarenotlimitedtoTransformerandCNN:GRU(Chung,Gulcehre,ChoandBengio(2014))introducesagating
mechanismthatallowsthemodeltodynamicallyadjusttheratioofmemoryandforgettingaccordingtothecurrent
inputandpreviousstate,makingitmoreflexibleandexpressivethantraditionalRNN.DLinear(Zeng,Chen,Zhangand
Xu(2023))decomposestimeseriesintoseasonalandtrendcomponentsforseparatepredictions.FITS(Xu,Zengand
Xu(2024))roposestheuseofbasicMLPforpredictioninthefrequencydomainbasedonDlinear.AndSparseTSF(Lin,
Lin,Wu,ChenandYang(2024))obtaininformationaboutadjacenttimestepsthroughconvolution,andthenpredict
futureresultsseparatelythroughsparsetechnology.
Consideringtheadvantagesandlimitationsoftheabovemodels,peopleneedatimeseriesforecastingmodelthat
canextractdifferentfeaturesandhaveaccuratepredictionresults.Therefore,weproposedTimeCF,basedontheoriginal
ideaofscaledecomposition,toobtainfeaturesofdifferentscalesthroughconvolutiontoachievemulti-scaleadaptive
informationaggregation.
2.2. ParametersUpdate
Nowadaysresearchershavebeguntofindthattheeffectsthatthemodelscanachieveonthetrainingsetareoften
notachievedonthetestset.Thisisbecausewhenthemodelusesanoptimizertooptimizethenon-convexlossfunction
onthetrainingset,itmayenterasuboptimalorsharpminimum,resultingininsufficientgeneralizationofthemodel.In
responsetothissituation,researchershaveproposedamethodcalledsharpness-awareminimizationtoupdatemodel
parameters to improve the generalization ability of deep neural networks: SAM(Foret et al. (2021)) proposed the
sharpness-awareminimizationmethod,whichfirstfindsthepointwiththemaximumlossintheneighborhoodofthe
currentparameterandthenusesgradientdescenttoupdatetheparametersbasedonthismaximumpoint,sothatthe
parameterscanbemovedtoaflatareatoreducethesharpnessofthelossfunction.WSAM(Yue,Jiang,Ye,Gao,Liuand
Zhang(2023))introducestheconceptofweightsbasedonSAM,andadjuststhecontributionofdifferentparameters
tosharpnessaccordingtotheimportanceoftheparametersorotherindicators,therebymoreeffectivelyregularizing.
FSAM(Li,Zhou,He,ChengandHuang(2024))effectivelyimprovesthegeneralizationperformanceandrobustnessof
themodelbyimprovingadversarialperturbationsandoptimizingthefullgradientestimationmethod.
Consideringthegeneralizationdegreeofthemodel,weproposeamodelparameterupdatemodulecalledSAMFre
basedontheSAMideatoimprovetheoverallgeneralizationabilityofthemodel.
3. TimeCF
3.1. OverView
The basic definition of time series forecasting is to input the historical data of a multivariate time series
𝑋 ∈ 𝑅𝑇×𝑁 and after the model calculation, output the future multivariate output sequence 𝑋 ∈ 𝑅𝐹×𝑁,
𝑖𝑛𝑝𝑢𝑡 𝑜𝑢𝑡𝑝𝑢𝑡
whereTrepresentsthelookbacklengthofthehistoricaldatadefinedbythemodel,Frepresentsthefuturetimelength
tobepredictedandNrepresentsthenumberoflabelsinthetimeseries.
InTimeCF,weusetheideaofchannelindependencetomakeindependentpredictionsforeachlabelinthetime
{ }
series.Therefore,theoriginalinputcanberegardedas 𝑋 ,𝑋 ,…,𝑋 ,where𝑋 ∈ 𝑅𝑇 canbe
𝑖𝑛𝑝𝑢𝑡1 𝑖𝑛𝑝𝑢𝑡2 𝑖𝑛𝑝𝑢𝑡𝑁 𝑖𝑛𝑝𝑢𝑡𝑖
Bin Wang et al.: PreprintsubmittedtoElsevier Page 3 of 10

---

# Page 4

(a) Input Preprocessing (b) PDMC (c) Output Predicting
L x Mixing
Embed Conv la Pred real labels
n
n o
Sampling
Embed Conv o itis
o p m
s a e
S N F F
Pred
SAM
ℱ
Fr
(
e
∙)
s s o
Embed Conv o Pred L
c d
e n ℱ(∙) n
D e o
Embed Conv rT Pred + tic
id
e
Input Series rP
Figure 1: TimeCF Architecture
regardedastheinputinstanceofTimeCF.TheoverallstructureofTimeCFisshowninFigure1,whichconsistsof
threecomponents:InputPreprocessinglayer,PDMClayer,andOutputPredictinglayer.Atthesametime,SAMFreasa
moduletosolvetheautocorrelationbetweenvariablesandimprovethegeneralizationabilityofthemodelindirectly
participatesinmodeltraininginthestagesofcalculatingmodellossandupdatingmodelparameters.Insummary,the
overallprocessofTimeCFconsistsofthreeexplicitmodulesandoneimplicitmodule.
3.2. InputPreprocessinglayer
Since we treat the time series 𝑋 ∈ 𝑅𝑇 in each label as a separate input instance, for each instance
𝑖𝑛𝑝𝑢𝑡𝑖
{ }
𝑋 ,wefirstusethepoolinglayertogeneratemulti-levelsequencesofdifferentscales 𝑋 ,𝑋 ,…,𝑋 ,where
𝑖𝑛𝑝𝑢𝑡𝑖 1 2 𝑘
𝑇
𝑋
𝑖
∈ 𝑅𝑑𝑖−1 (𝑖∈{1,…𝑘}).Theoutput𝑋
𝑖
istheresultof𝑖−1timesofdownsamplingoftheoriginalinput𝑋
𝑖𝑛𝑝𝑢𝑡𝑖
.
𝑋 isequaltotheoriginalinputsequence𝑋 and𝑑 representsthelengthofthemovingwindowinthepoolinglayer.
1 𝑖𝑛𝑝𝑢𝑡𝑖
Thespecificmulti-scalesequencegenerationformulaisasfollows:
( ( ))
𝑋 =𝑃𝑜𝑜𝑙 𝑃𝑎𝑑𝑑𝑖𝑛𝑔 𝑋 (1)
𝑖 (𝑖−1)
Aftergeneratingthemulti-scalesequences,eachsequencewillhaveatime-relatedmask𝑋 mask𝑖.Eachsequenceis
firstnormalizedbytheRevInnormalizationlayer,andthenthemaskandsequenceareembeddedbytheEmbedding
layer.Thespecificprocessisasfollows:
( ) ( )
𝑋 𝑖 =𝑇𝑒𝑚𝑝𝑜𝑟𝑎𝑙𝐸𝑚𝑏𝑒𝑑𝑑𝑖𝑛𝑔 𝑋 mask𝑖 +𝑇𝑜𝑘𝑒𝑛𝐸𝑚𝑏𝑒𝑑𝑑𝑖𝑛𝑔 𝑅𝑒𝑣𝐼𝑁(𝑋 𝑖 ) (2)
𝑇 ×𝐷
Informula(2),thesequenceofeachscaleis𝑋
𝑖
∈𝑅𝑑𝑖−1 ,𝐷istheoutputdimensionofembedding.Atthispoint,
thepreprocessingpartoftheinputdataiscompleted,andthisstageisonlyperformedonceduringthemodeltraining
process.
3.3. PastDecomposableMixingwithadaptiveConvlayer
Recentstudieshavefoundthatmosttimeseriesarethefusionofdifferentcomponentsofdifferentperiodsatmost
scales.Therefore,weproposethePDMCmodule,whichuseslong-termandshort-termchangestoanalyzevarious
periodicandnon-periodicpropertiesoftheentiretimeseries,whileobtaininginformationofdifferentreceptivefieldsat
differentscalesthroughconvolution.Specifically,inthePDMC,wefirstaddglobalorlocalinformationtothesequence
throughtheideaofconvolutionandadaptation:
𝑋 =𝛼×𝐶𝑜𝑛𝑣𝐵𝑙𝑜𝑐𝑘𝑠
( 𝑋𝑇)𝑇
+𝑋 (3)
𝑖 [𝑖] 𝑖 𝑖
The𝑋 istheoutputoftheinputpreprocessinglayerandtheformulafor𝐶𝑜𝑛𝑣𝐵𝑙𝑜𝑐𝑘𝑠 (𝑋)isasfollow:
𝑖 [𝑖]
Bin Wang et al.: PreprintsubmittedtoElsevier Page 4 of 10

---

# Page 5

𝐶𝑜𝑛𝑣𝐵𝑙𝑜𝑐𝑘𝑠 (𝑋)=𝐶𝑜𝑛𝑣(𝐺𝐸𝐿𝑈(𝐶𝑜𝑛𝑣(𝐺𝐸𝐿𝑈(𝐶𝑜𝑛𝑣(𝑁𝑜𝑟𝑚(𝑋)))))) (4)
[𝑖]
Next,wewillexplainwhyusingthesamesizeofconvolutioncanobtaininformationofdifferentreceptivefields.First,
thelookbackwindowlengthselectedbythismodelis96,whichisconsistentwiththemainstreammodel,andthenumber
{ }
ofdownsamplingissetto3.SotheinputofPDMCis 𝑋 ∈𝑅96×𝐷,𝑋 ∈𝑅48×𝐷,𝑋 ∈𝑅24×𝐷,𝑋 ∈𝑅12×𝐷 ,where
1 2 3 4
96,48,24,12arethetimewindowsafterdownsampling.Andin𝐶𝑜𝑛𝑣𝐵𝑙𝑜𝑐𝑘𝑠 (𝑋),weusethreelayersofconvolution
[𝑖]
andtheconvolutionkernelsizeofeachlayeris3,andthepaddingis1.Thismeansthatafterthreeconvolutions,each
{ }
timepointin 𝑋 ,𝑋 ,𝑋 ,𝑋 containsinformationfromatleast2 + 2 + 2,or6neighboringtimepoints.Fromthe
1 2 3 4
perspectiveofPDMCstacking,thenumberofPDMCstackingsis𝐿(𝐿≥2).Sofor𝑋 ,thewindowoflength6×𝐿
4
willeventuallycovertheentiresequencelength,whichcanbeconsideredasobtainingglobalinformation.Butfor
𝑋 ,𝑋 and𝑋 ,thewindowoflength6×𝐿onlyoccupiesapartofthesequencelength,whichcanbeconsideredas
1 2 3
obtaininglocalinformationofdifferentproportions.Insummary,byusingconvolutionblocksandPDMCstacking,
TimeCFcanobtaininformationofdifferentreceptivefieldsatdifferentscales.
Then,wedecomposethesequenceofeachscaleintoseasonandtrendparts:
( )
𝑆𝑒𝑎𝑠𝑜𝑛,𝑇𝑟𝑒𝑛𝑑 =𝐷𝑒𝑐𝑜𝑚𝑝 𝑋 (5)
𝑖 𝑖 𝑖
𝑆𝑒𝑎𝑠𝑜𝑛,𝑇𝑟𝑒𝑛𝑑 refertotheseasonandtrendpartsdecomposedfromthei-thscalerespectively.Weputallthe
𝑖 𝑖
seasonandtrendcomponentsintothelists𝑆𝑒𝑎𝑠𝑜𝑛and𝑇𝑟𝑒𝑛𝑑 respectively,andbasedontheideaofTimeMixer,we
performscalefusionontheseasonandtrendrespectively:
𝑆𝑒𝑎𝑠𝑜𝑛,𝑇𝑟𝑒𝑛𝑑 =𝑆𝑒𝑎𝑠𝑜𝑛𝑀𝑖𝑥(𝑆𝑒𝑎𝑠𝑜𝑛),𝑇𝑟𝑒𝑛𝑑𝑀𝑖𝑥(𝑇𝑟𝑒𝑛𝑑) (6)
Thefusionoftheseasontermisabottom-upsequencefusionandthetrendtermisatop-downsequencefusion
whichmakefulluseoftheinformationinherentinbothparts.Finally,PDMCpassestheseasonpart,trendpartand
originalsequencethroughthefeedforwardnetworktoachievethefusionbetweendifferentcomponents:
( )
𝑋 =𝑋 +𝐹𝐹𝑁 𝑆𝑒𝑎𝑠𝑜𝑛 +𝑇𝑟𝑒𝑛𝑑 (7)
𝑖 𝑖 𝑖 𝑖
Sofar,thePDMCblockhasfinallyrealizedthecoretasksoffeatureextractionandmulti-scalemixingprocess
throughtheadaptiveinformationaggregationbyconvolution,thedecompositionandmixingoftheseasontermand
trendterm.
3.4. OutputPredictinglayer
{ } 𝑇 ×𝐷
Inthepredictionoutputstage,theoutputofPDMCweobtainis 𝑋
1
,𝑋
2
,…,𝑋
𝑘
,where𝑋
𝑖
∈𝑅𝑑𝑖−1 (𝑖∈{1,…𝑘}).
Soifweneedtomakeapredictionfor𝑋 inthetimedimension,weneedtochangethedimensionof𝑋 atleasttwice.
𝑖 𝑖
Specifically,firstalignthetimedimensionof𝑋 withthepredictedfuturelengthaccordingtodifferentscales.Then
𝑖
adjustthedimensionofthesequencesothatthemodelvectordimensionDcanbereducedbacktotheinitialvalue:
( )
𝑋 =𝐿𝑖𝑛𝑒𝑎𝑟 𝐿𝑖𝑛𝑒𝑎𝑟
( 𝑋𝑇)𝑇
(8)
𝑖 2 1 𝑖
Theinputdimensionofthe𝐿𝑖𝑛𝑒𝑎𝑟 is 𝑇 ,andtheoutputdimensionisthepredictionlength𝐹.Asaresult,time
1 𝑑𝑖−1
seriesofdifferentscalesgeneratepredictionsofcorrespondingtimelengths.Then,theinputdimensionofthe𝐿𝑖𝑛𝑒𝑎𝑟
2
is𝐷andtheoutputdimension1.Thisistomakethesequencedimensionmatchthetargetoutputdimension,orlet
𝑋 ∈𝑅𝐹
𝑖
Itisnotdifficulttoseethateachscalesequenceeventuallygeneratesapredictionsequence.Thenwesumallthe
predictionsequencesandusetheRevINlayerofthepreprocessinglayertoperforminversenormalization:
(∑ )
𝑋 =𝑖𝑅𝑒𝑣𝐼𝑁 𝑋 (9)
𝑂 𝑖
Atthispoint,thepredictionofasinglelabeliscompleted,andthesequencesofdifferentscalesarefinallyfused
togetherthroughthestack()functiontoforecasttheresult.
Bin Wang et al.: PreprintsubmittedtoElsevier Page 5 of 10

---

# Page 6

3.5. Sharpness-AwareMinimizationFrequencyDomainLoss
ThelossfunctionoftraditionaltimeseriesforecastingmodelisusuallyMSEloss,whichhasshownitssuperiority
inthetrainingprocessofalargenumberoftimeseriesforecastingmodels.However,withtheintroductionoftheideaof
channelindependence,FreDF’sresearchershavenoticedthattheMSElosshardlytakesintoaccounttheautocorrelation
betweendifferentlabelsofthetimeseriesinthemodelusingthechannelindependencemethod.Therefore,itisnotthe
bestchoicetocalculatethelossbyMSEinthetrainingprocessofthetimeseriesforecastingmodelusingthechannel
independencemethod.However,accordingtotheideaofFouriertransform,ifdifferentlabelsareprojectedintothe
frequencydomain,unrelatedfeaturecanbeobtainedinthefrequencydomainsothatthemodelbasedontheideacan
obtainbetterresultsthanthetraditionalMSElosswhencalculatingtheloss.Atthesametime,wenoticedthatthe
overallgeneralizationperformanceofthemodelcanbeimprovedbyadjustingthesharpnessofthelossthroughthe
SAMmethod.Basedonthesetwoideas,theTimeCFweproposedintroducestheSAMFremoduletodecouplethe
autocorrelationbetweendifferentlabelsinthetimeseriesandimprovethegeneralizationability.Specifically,SAMFre
projectsthemodel’spredictionresultsandtheactuallabelvaluesintothefrequencydomainthroughFouriertransform,
thencalculatesthelossusingtheL1norm,andfinallyaddsittotheoriginalMSElosstogetthecompleteloss:
𝑙𝑜𝑠𝑠=𝛼×| 𝐹𝐹𝑇 (𝑝𝑟𝑒𝑑)−𝐹𝐹𝑇 (𝑟𝑒𝑎𝑙)|1 +(1−𝛼)×𝑀𝑆𝐸 (10)
Aftercalculatingtheloss,themodelusesbasicoptimizationmethodstooptimizethemodelparametersbefore
thenumberofupdatesreachesthesetthreshold.Whenthenumberofupdatesreachesthethreshold,themodeluses
theSAMmethodtocalculatethepointwiththelargestlossintheneighborhoodofthecurrentparameter,andthen
performsgradientbackpropagationbasedonthispointtoachieveparameterupdate:
∇ 𝐿𝑜𝑠𝑠
𝜖̂(𝑤) = 𝜌 𝑤 (11)
‖∇ 𝑤 𝐿𝑜𝑠𝑠 ‖2
𝑔 = ∇ 𝐿𝑜𝑠𝑠| (12)
𝑤 |𝑤+𝜖̂(𝑤)
𝑤 = 𝑤 − 𝜂 ⋅ 𝑔 (13)
Sofar,wehaveoptimizedthemodelparameterupdatepartthroughSAMFre,sothatthemodelcanbetterdealwith
theautocorrelationproblembetweenlabelsindifferentsequencesandimprovethegeneralizationabilityofthemodel.
4. Results
4.1. Experimentsetting
Experimentaldatasets:Inordertoverifythepredictionaccuracyofourmodelontimeseriesgeneratedinreal
environments,weselectedsixcommonlyusedreal-worlddatasets:Weather,ETTh1,ETTh2,ETTm1,ETTm2and
Electricity(Zhouetal.(2021);Wuetal.(2021))andconductedsufficientexperimentsonthesesixdatasetstoverifythe
abilityofourmodelinlong-termforecasting.
Benchmarkmodels:Basedontimeliness,innovationandpredictioneffect,weselected8timeseriesforecastingmod-
elswhicharewidelyacclaimedinthefieldoftimeseriesforecastingasourbaselines,including:(1)TimeKAN(Huang
etal.(2025))(2)TimeMixer(Wangetal.(2024))(3)iTransformer(Liuetal.(2024))(4)SparseTSF(Linetal.(2024))
(5) FreTS(Yi, Zhang, Fan, Wang, Wang, He, An, Lian, Cao and Niu (2023)) (6) PatchTST(Nie et al. (2023)) (7)
TimesNet(Wuetal.(2023))(8)DLinear(Zengetal.(2023))
Experimental environment and related indicators: All experiments were implemented based on PyTorch and
conductedonasingleNVIDIA309024GBGPU.Atthesametime,inordertoensurefaircompetitionamongthe
models,wesetthelookbackwindow,predictionlength,andevaluationindexto96,96,192,336,720,meansquare
error(MSE),andmeanabsoluteerror(MAE)respectively.WhatâĂŹsmore,thebenchmarkmodelistestedusingthe
scriptsprovidedintheoriginalcode,whilethetestoftheTimeCFmodelweproposedsetsdifferenttrainingroundsand
earlystoppingthresholdsaccordingtothesizeofdifferentdatasetstoimprovetestefficiency.
Bin Wang et al.: PreprintsubmittedtoElsevier Page 6 of 10

---

# Page 7

Table 1
Performance comparison of different time series forecasting models on benchmark datasets.
TimeCF TimeKAN TimeMixer iTransformer SparseTSF FreTS PatchTST TimesNet Dlinear
Models
Ours 2025 2024 2024 2024 2024 2023 2023 2023
Metric MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
96 0.359 0.391 0.367 0.394 0.381 0.398 0.394 0.409 0.385 0.391 0.395 0.407 0.376 0.397 0.389 0.411 0.396 0.410
192 0.401 0.419 0.414 0.419 0.441 0.430 0.448 0.441 0.434 0.420 0.490 0.477 0.426 0.432 0.439 0.441 0.445 0.440
ETTh1 336 0.440 0.436 0.445 0.434 0.500 0.459 0.492 0.465 0.476 0.439 0.510 0.480 0.469 0.457 0.493 0.470 0.487 0.465
720 0.466 0.462 0.451 0.463 0.552 0.507 0.521 0.504 0.461 0.454 0.568 0.538 0.518 0.504 0.516 0.494 0.512 0.510
avg 0.417 0.427 0.419 0.428 0.468 0.449 0.464 0.455 0.439 0.426 0.490 0.475 0.447 0.447 0.459 0.454 0.460 0.456
96 0.282 0.333 0.291 0.340 0.286 0.339 0.300 0.349 0.302 0.346 0.332 0.387 0.308 0.359 0.337 0.370 0.341 0.395
192 0.372 0.389 0.374 0.391 0.391 0.404 0.381 0.399 0.384 0.395 0.451 0.457 0.380 0.406 0.404 0.414 0.481 0.479
ETTh2 336 0.410 0.422 0.423 0.434 0.421 0.432 0.423 0.432 0.421 0.427 0.466 0.473 0.412 0.429 0.455 0.452 0.592 0.542
720 0.416 0.436 0.462 0.461 0.468 0.468 0.426 0.445 0.420 0.437 0.485 0.471 0.435 0.456 0.434 0.448 0.840 0.661
avg 0.370 0.395 0.387 0.406 0.391 0.411 0.383 0.406 0.382 0.401 0.433 0.447 0.384 0.412 0.407 0.421 0.564 0.519
96 0.307 0.345 0.321 0.361 0.327 0.364 0.341 0.376 0.356 0.375 0.337 0.374 0.323 0.364 0.333 0.375 0.345 0.373
192 0.353 0.372 0.356 0.382 0.367 0.386 0.380 0.394 0.394 0.392 0.382 0.398 0.371 0.391 0.407 0.413 0.381 0.391
ETTm1 336 0.377 0.395 0.381 0.400 0.393 0.403 0.419 0.418 0.425 0.413 0.420 0.423 0.398 0.408 0.413 0.421 0.415 0.415
720 0.441 0.430 0.451 0.437 0.451 0.442 0.486 0.455 0.487 0.448 0.490 0.471 0.457 0.444 0.503 0.467 0.472 0.450
avg 0.370 0.386 0.377 0.395 0.384 0.399 0.406 0.411 0.415 0.407 0.407 0.416 0.387 0.402 0.414 0.419 0.403 0.407
96 0.169 0.252 0.175 0.257 0.174 0.257 0.183 0.266 0.184 0.267 0.186 0.275 0.184 0.267 0.189 0.266 0.193 0.292
192 0.238 0.299 0.239 0.299 0.236 0.299 0.252 0.312 0.248 0.305 0.259 0.323 0.246 0.304 0.252 0.307 0.284 0.361
ETTm2 336 0.296 0.335 0.301 0.340 0.301 0.339 0.314 0.351 0.307 0.342 0.349 0.386 0.311 0.348 0.321 0.349 0.384 0.429
720 0.400 0.393 0.398 0.398 0.400 0.400 0.411 0.406 0.407 0.398 0.559 0.511 0.418 0.414 0.418 0.404 0.556 0.523
avg 0.276 0.320 0.278 0.323 0.278 0.324 0.290 0.334 0.287 0.328 0.338 0.373 0.290 0.333 0.295 0.331 0.354 0.401
96 0.162 0.204 0.162 0.208 0.161 0.208 0.175 0.215 0.197 0.236 0.171 0.227 0.175 0.217 0.168 0.219 0.196 0.256
192 0.209 0.249 0.207 0.249 0.207 0.251 0.225 0.257 0.243 0.273 0.218 0.280 0.220 0.255 0.225 0.265 0.238 0.299
Weather 336 0.266 0.293 0.263 0.290 0.264 0.293 0.279 0.298 0.292 0.308 0.265 0.317 0.279 0.297 0.281 0.303 0.281 0.330
720 0.345 0.343 0.338 0.340 0.345 0.345 0.361 0.350 0.368 0.357 0.326 0.351 0.356 0.348 0.359 0.354 0.345 0.381
avg 0.246 0.272 0.242 0.271 0.244 0.274 0.260 0.280 0.275 0.293 0.245 0.293 0.257 0.279 0.258 0.285 0.265 0.316
96 0.153 0.245 0.174 0.266 0.156 0.247 0.148 0.240 0.209 0.280 0.171 0.260 0.180 0.272 0.168 0.271 0.210 0.301
192 0.166 0.256 0.182 0.272 0.170 0.260 0.164 0.256 0.205 0.281 0.177 0.268 0.187 0.279 0.187 0.289 0.210 0.304
ECL 336 0.183 0.274 0.196 0.286 0.187 0.278 0.177 0.270 0.218 0.295 0.190 0.284 0.204 0.295 0.201 0.302 0.223 0.319
720 0.221 0.305 0.236 0.320 0.227 0.312 0.228 0.313 0.260 0.327 0.228 0.316 0.245 0.328 0.229 0.324 0.257 0.349
avg 0.181 0.270 0.197 0.286 0.185 0.274 0.179 0.269 0.223 0.296 0.191 0.282 0.204 0.294 0.196 0.297 0.225 0.318
TotalAVG 0.310 0.345 0.317 0.352 0.325 0.355 0.330 0.359 0.337 0.359 0.351 0.381 0.328 0.361 0.338 0.368 0.379 0.403
1stTimes 19 21 5 4 2 0 4 4 0 2 1 0 0 0 0 0 0 0
4.2. Experimentresults
Allresultsinthisexperimentareobtainedafterlocalexperiments(exceptforFreTSwhoseresultsareobtained
fromtheoriginalpaper)andallresultsareshowninTable1.WedefinethatthelowerthevaluesofMSEandMAE,
thebetterthemodelpredictioneffect.Atthesametime,thebestresultsareshowninboldredandthesecondbest
resultsareshowninboldblack.ItisnotdifficulttoseefromTable1thattheTimeCFweproposedhasshowngood
performanceonmostdatasets,exceptforweatherandECL,whereKANandTransformermodelcanbetterhandlethe
autocorrelationdependenciesforhigh-dimensionaldatasets.Evenifitdoesnotachievetheoptimalpredictioneffectin
somedatasets,thepredictionaccuracyofTimeCFisnotmuchdifferentfromtheresultsachievedbytheoptimalmodel.
TheaveragevaluesofMSEandMAEincreasedby2.2%and1.9%comparedwiththesuboptimalmodel.Andifwe
lookatthenumberoftimestheoptimalpredictionisobtained,TimeCFisfaraheadofallmodelsthatappearedinthe
experiments.ThisprovesthatTimeCFhasaccurateandgeneralpredictioncapabilitiesonmostnaturaltimeseries.
4.3. Ablationexperiment
Todemonstratetheaccuracyofourdesignandadditionofmodules,weusedthreeformsofTimeCFmodelsin
theablationimplementationtocomparewithourselectedbaselinemodelTimeMixer:(1)TimeCFwiththeSAMFre
moduleomitted(2)TimeCFwiththeconvolutionpartomittedand(3)thecompleteTimeCF.AsshowninTable2,
TimeCFwithoutcompletemoduleshasacertainimprovementoverthebaselinemodelintheexperiment,butthe
Bin Wang et al.: PreprintsubmittedtoElsevier Page 7 of 10

---

# Page 8

Table 2
Ablation study of TimeCF.
ETTh1 ETTh2 ECL
Model
MSE MAE MSE MAE MSE MAE
TimeMixer 0.469 0.449 0.392 0.411 0.185 0.274
TimeCFw/oSAMFre 0.466 0.452 0.392 0.417 0.182 0.273
TimeCFw/oCONV 0.430 0.425 0.372 0.396 0.185 0.272
TimeCF(ours) 0.417 0.427 0.371 0.396 0.181 0.270
Table 3
Parameter comparison of different time series forecasting models on various datasets.
Parameters(Number)
Model
ETTh1 ETTh2 ETTm1 ETTm2 Weather ECL
TimeMixer 75.3K 75.3K 75.3K 77.5K 104K 104K
iTransformer 224K 224K 224K 224K 4.83M 4.83M
TimesNet 605K 1.19M 4.70M 1.19M 1.19M 150M
SparseTSF 0.041K 0.041K 0.581K 0.581K 0.581K 0.041K
TimeCF(ours) 125K 125K 125K 275K 179K 179K
improvementisnotsignificant.Thisshowsthatboththedecouplingoflabelautocorrelationintimeseriesandthe
enhancementofgeneralizationabilitybasedonSAMFreandtheadaptiveinformationaggregationbetweendifferent
scales based on convolution can only enhance the partial information extraction and prediction capabilities of the
baselinemodelTimeMixertoacertainextent.However,thegoodperformanceofthecompleteTimeCFshowsthat
theinformationofdifferentscalesandreceptivefieldsobtainedbyconvolutionmaycontainsomeinformationwith
autocorrelation.AndbyusingSAMFre,theautocorrelationwithinthispartofinformationcanbeproperlydecoupled,
whichisreflectedintheresultsthatitexceedsthebaselinemodelintermsofevaluationindicators.Finally,itisproved
thattheadaptiveinformationaggregationmodulebasedonconvolutionandtheSAMFremoduleproposedbyusare
bothindispensablepartsoftheTimeCFmodel.
4.4. Modelefficiency
InordertoverifytheefficiencyoftheTimeCFmodelweproposed,wesetthelookbackwindowandtheprediction
lengthto96and96totesttheparametersizeofthemodel.WeselectedthreebenchmarkmodelsbasedontheTransformer
architecture,theCNNarchitectureandtheMLPmodel,andamodelwiththesmallestnumberofparametersasthe
baselinemodelformodelefficiency.ItisnotdifficulttoseefromTable3thattheTransformerandCNN-basedmodelsare
limitedbythemodelstructure,andtheirparametervolumeismaintainedataveryhighlevelonalldatasets.Themodel
parametersoftheMLP-basedmodelTimeMixerandtheTimeCFweproposedarebasicallymaintainedatarelatively
lowleveloneachdataset,andthefluctuationrangeisnotlarge.AlthoughthenumberofparametersofSparseTSFis
muchsmallerthanthatoftheTimeCFweproposedandTimeMixer,consideringthebalancebetweenpredictioneffect
andparametervolume,webelievethattheTimeCFweproposedhasstableandefficientmodeloperationefficiency
whileensuringtheaccuracyofthepredictionresultsunderdifferentdatasets.Therefore,itcanbeconsideredthatthe
TimeCFweproposedcanachieveexcellentpredictionperformancewithonlyarelativelysmallamountofcomputing
resources.
5. Conclusion
Inourpaper,weproposedatimeseriespredictionmodelTimeCFbasedontheTimeMixerdecomposition-learning-
mixingarchitecturetoachievehigh-precisiontimeseriesforecasting.WiththesupportofPDMC,TimeCFcanutilizethe
informationofdifferentreceptivefieldsofsequencesofdifferentscales,learnandmixtheseasonalandtrendsequences
separatelyandfinallycombineSAMFretodecoupletheautocorrelationbetweenlabelsandreducethesharpnessof
thelossfunction.TheperformanceofourmodelonrealdatasetsalsoprovesthatTimeCFcancopewithtimeseries
predictiontasksintherealworldwithgoodpredictionperformance.
Bin Wang et al.: PreprintsubmittedtoElsevier Page 8 of 10

---

# Page 9

References
Afan,H.A.,Mohtar,W.H.M.W.,Khaleel,F.,Kamel,A.H.,Mansoor,S.S.,Alsultani,R.,Ahmed,A.N.,Sherif,M.,El-Shafie,A.,2024.Data-driven
waterqualitypredictionforwastewatertreatmentplants.Heliyon10.Publisher:Elsevier.
Alkhayat,G.,Mehmood,R.,2021.Areviewandtaxonomyofwindandsolarenergyforecastingmethodsbasedondeeplearning.EnergyandAI4,
100060.Publisher:Elsevier.
Bi,K.,Xie,L.,Zhang,H.,Chen,X.,Gu,X.,Tian,Q.,2023.Accuratemedium-rangeglobalweatherforecastingwith3Dneuralnetworks.Nature
619,533–538.Publisher:NaturePublishingGroup.
Challu,C.,Olivares,K.G.,Oreshkin,B.N.,RamÃŋrez,F.G.,Canseco,M.M.,Dubrawski,A.,2023.NHITS:NeuralHierarchicalInterpolationfor
TimeSeriesForecasting,in:AAAI,pp.6989–6997.URL:https://doi.org/10.1609/aaai.v37i6.25854.
Chung,J.,Gulcehre,C.,Cho,K.,Bengio,Y.,2014.Empiricalevaluationofgatedrecurrentneuralnetworksonsequencemodeling,in:NIPS2014
WorkshoponDeepLearning,December2014.
donghao,L.,xue,w.,2024.ModernTCN:AModernPureConvolutionStructureforGeneralTimeSeriesAnalysis,in:TheTwelfthInternational
ConferenceonLearningRepresentations.URL:https://openreview.net/forum?id=vpJMJerXHU.
Farhi,N.,Kohen,E.,Mamane,H.,Shavitt,Y.,2021. PredictionofwastewatertreatmentqualityusingLSTMneuralnetwork. Environmental
Technology&Innovation23,101632.Publisher:Elsevier.
Foret,P.,Kleiner,A.,Mobahi,H.,Neyshabur,B.,2021.Sharpness-awareMinimizationforEfficientlyImprovingGeneralization,in:International
ConferenceonLearningRepresentations.URL:https://openreview.net/forum?id=6Tm1mposlrM.
Gu,A.,Dao,T.,2023.Mamba:Linear-timesequencemodelingwithselectivestatespaces.arXivpreprintarXiv:2312.00752.
Hochreiter,S.,Schmidhuber,J.,1997.Longshort-termmemory.Neuralcomputation9,1735–1780.Publisher:MITpress.
Huang,S.,Zhao,Z.,Li,C.,Bai,L.,2025.TimeKAN:KAN-basedFrequencyDecompositionLearningArchitectureforLong-termTimeSeries
Forecasting.arXivpreprintarXiv:2502.06910.
Huang,X.,Zhang,B.,Feng,S.,Ye,Y.,Li,X.,2023.Interpretablelocalflowattentionformulti-steptrafficflowprediction.Neuralnetworks161,
25–38.Publisher:Elsevier.
Huo,G.,Zhang,Y.,Wang,B.,Gao,J.,Hu,Y.,Yin,B.,2023.HierarchicalspatioâĂŞtemporalgraphconvolutionalnetworksandtransformernetwork
fortrafficflowforecasting.IEEETransactionsonIntelligentTransportationSystems24,3855–3867.Publisher:IEEE.
Ilbert,R.,Odonnat,A.,Feofanov,V.,Virmaux,A.,Paolo,G.,Palpanas,T.,Redko,I.,2024.SAMformer:UnlockingthePotentialofTransformers
inTimeSeriesForecastingwithSharpness-AwareMinimizationandChannel-WiseAttention,in:ICML.URL:https://openreview.net/
forum?id=8kLzL5QBh2.
Li,L.,Jian,C.,Wan,F.,Geng,D.,Fang,Z.,Chen,L.,Gao,Y.,Jiang,W.,Zhu,J.,2024. LagCNN:AFastyetEffectiveModelforMultivariate
Long-termTimeSeriesForecasting,in:CIKM,pp.1235–1244.URL:https://doi.org/10.1145/3627673.3679672.
Li,T.,Zhou,P.,He,Z.,Cheng,X.,Huang,X.,2024.FriendlySharpness-AwareMinimization,in:ProceedingsoftheIEEE/CVFConferenceon
ComputerVisionandPatternRecognition(CVPR),pp.5631–5640.
Liang,X.,Yang,E.,Deng,C.,Yang,Y.,2024.CrossFormer:Cross-ModalRepresentationLearningviaHeterogeneousGraphTransformer.ACM
Trans.Multim.Comput.Commun.Appl.20,380:1–380:21.URL:https://doi.org/10.1145/3688801.
Lin,S.,Lin,W.,Wu,W.,Chen,H.,Yang,J.,2024.SparseTSF:ModelingLong-termTimeSeriesForecastingwith*1k*Parameters,in:Forty-first
InternationalConferenceonMachineLearning.URL:https://openreview.net/forum?id=54NSHO0lFe.
Liu,Y.,Hu,T.,Zhang,H.,Wu,H.,Wang,S.,Ma,L.,Long,M.,2024.iTransformer:InvertedTransformersAreEffectiveforTimeSeriesForecasting,
in:TheTwelfthInternationalConferenceonLearningRepresentations.URL:https://openreview.net/forum?id=JePfAI8fah.
Nie,Y.,Nguyen,N.H.,Sinthong,P.,Kalagnanam,J.,2023.ATimeSeriesisWorth64Words:Long-termForecastingwithTransformers,in:The
EleventhInternationalConferenceonLearningRepresentations.URL:https://openreview.net/forum?id=Jbdc0vTOcol.
Salinas,D.,Flunkert,V.,Gasthaus,J.,Januschowski,T.,2020.DeepAR:Probabilisticforecastingwithautoregressiverecurrentnetworks.International
journalofforecasting36,1181–1191.Publisher:Elsevier.
Sonkavde,G.,Dharrao,D.S.,Bongale,A.M.,Deokate,S.T.,Doreswamy,D.,Bhat,S.K.,2023. Forecastingstockmarketpricesusingmachine
learninganddeeplearningmodels:Asystematicreview,performanceanalysisanddiscussionofimplications.InternationalJournalofFinancial
Studies11,94.Publisher:MDPI.
Vaswani,A.,Shazeer,N.,Parmar,N.,Uszkoreit,J.,Jones,L.,Gomez,A.N.,Kaiser,Å.,Polosukhin,I.,2017.Attentionisallyouneed.Advancesin
neuralinformationprocessingsystems30.
Wang,H.,Pan,L.,Chen,Z.,Yang,D.,Zhang,S.,Yang,Y.,Liu,X.,Li,H.,Tao,D.,2024.Fredf:Learningtoforecastinfrequencydomain.arXiv
preprintarXiv:2402.02399.
Wang,H.,Peng,J.,Huang,F.,Wang,J.,Chen,J.,Xiao,Y.,2023. MICN:Multi-scaleLocalandGlobalContextModelingforLong-term
SeriesForecasting,in:TheEleventhInternationalConferenceonLearningRepresentations.URL:https://openreview.net/forum?id=
zt53IDUR1U.
Wang,S.,Wu,H.,Shi,X.,Hu,T.,Luo,H.,Ma,L.,Zhang,J.Y.,Zhou,J.,2024. TimeMixer:DecomposableMultiscaleMixingforTimeSeries
Forecasting,in:ICLR.URL:https://openreview.net/forum?id=7oLshfEIC2.
Wu,H.,Hu,T.,Liu,Y.,Zhou,H.,Wang,J.,Long,M.,2023.TimesNet:Temporal2D-VariationModelingforGeneralTimeSeriesAnalysis,in:The
EleventhInternationalConferenceonLearningRepresentations.URL:https://openreview.net/forum?id=ju_Uqw384Oq.
Wu,H.,Xu,J.,Wang,J.,Long,M.,2021. Autoformer:DecompositionTransformerswithAuto-CorrelationforLong-TermSeriesForecasting,
in: Beygelzimer, A., Dauphin, Y., Liang, P., Vaughan, J.W. (Eds.), Advances in Neural Information Processing Systems. URL: https:
//openreview.net/forum?id=I55UqU-M11y.
Xu,Z.,Zeng,A.,Xu,Q.,2024. FITS:ModelingTimeSerieswith\10k\Parameters,in:TheTwelfthInternationalConferenceonLearning
Representations.URL:https://openreview.net/forum?id=bWcnvZ3qMb.
Yi,K.,Zhang,Q.,Fan,W.,Wang,S.,Wang,P.,He,H.,An,N.,Lian,D.,Cao,L.,Niu,Z.,2023.Frequency-domainmlpsaremoreeffectivelearners
intimeseriesforecasting.AdvancesinNeuralInformationProcessingSystems36,76656–76679.
Bin Wang et al.: PreprintsubmittedtoElsevier Page 9 of 10

---

# Page 10

Yin,L.,Cao,X.,Liu,D.,2023.Weightedfully-connectedregressionnetworksforone-day-aheadhourlyphotovoltaicpowerforecasting.Applied
Energy332,120527.Publisher:Elsevier.
Yue,Y.,Jiang,J.,Ye,Z.,Gao,N.,Liu,Y.,Zhang,K.,2023.Sharpness-AwareMinimizationRevisited:WeightedSharpnessasaRegularization
Term,in:KDD,pp.3185–3194.URL:https://doi.org/10.1145/3580305.3599501.
Zeng,A.,Chen,M.,Zhang,L.,Xu,Q.,2023.Aretransformerseffectivefortimeseriesforecasting?,in:ProceedingsoftheAAAIconferenceon
artificialintelligence,pp.11121–11128.Issue:9.
Zhang,G.P.,2003.TimeseriesforecastingusingahybridARIMAandneuralnetworkmodel.Neurocomputing50,159–175.Publisher:Elsevier.
Zhou,H.,Zhang,S.,Peng,J.,Zhang,S.,Li,J.,Xiong,H.,Zhang,W.,2021.Informer:Beyondefficienttransformerforlongsequencetime-series
forecasting,in:ProceedingsoftheAAAIconferenceonartificialintelligence,pp.11106–11115.Issue:12.
Bin Wang et al.: PreprintsubmittedtoElsevier Page 10 of 10