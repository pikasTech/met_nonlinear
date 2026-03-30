SOH-KLSTM:AHybridKolmogorov-ArnoldNetworkandLSTMModelforEnhancedLithium-IonBatteryHealth
Monitoring
ImenJarrayaa, SafaBenAtitallaha,b,∗, FatimahAlahmeda, MohamedAbdelkadera,
MahaDrissa,b, FatmaAbdelhadic and AnisKoubaaa
aRoboticsandInternetofThingsLaboratory,CollegeofComputerandInformationSciences,Riyadh,12435,SaudiArabia
bRIADILaboratory,NationalSchoolofComputerScience,UniversityofManouba,Manouba 2010,Tunisia
cCollegeofElectricalandComputerEngineering,KingAbdulazizUniversity,Jeddah,22254,SaudiArabia
ARTICLE INFO ABSTRACT
Keywords: AccurateandreliableStateOfHealth(SOH)estimationforLithium(Li)batteriesiscritical
StateofHealth toensurethelongevity,safety,andoptimalperformanceofapplicationslikeelectricvehicles,
LongShort-TermMemory unmannedaerialvehicles,consumerelectronics,andrenewableenergystoragesystems.Con-
Kolmogorov-ArnoldNetworks ventionalSOHestimationtechniquesfailtorepresentthenon-linearandtemporalaspectsof
CandidateCellState batterydegradationeffectively.Inthisstudy,weproposeanovelSOHpredictionframework
LithiumBatteries (SOH-KLSTM)usingKolmogorov-ArnoldNetwork(KAN)-IntegratedCandidateCellStatein
LSTMforLibatteriesHealthMonitoring.ThishybridapproachcombinestheabilityofLSTM
to learn long-term dependencies for accurate time series predictions with KAN’s non-linear
approximation capabilities to effectively capture complex degradation behaviors in Lithium
batteries. KAN addresses LSTM’s limitations in handling non-smooth approximations and
memorydecayoverextendedsequences.ThecombinationofLSTMandKANensuresthatthe
modelaccuratelydepictsboththetime-dependentchangesandthecomplicatednon-linearitiesof
batterydegradation.ExperimentalvalidationwasperformedonseveralsubsetsfromtheNASA
PrognosticsCenterofExcellence(PCoE)dataset,whichincludesLi-ionbatterydatacollected
duringhundredsofcharge-dischargecyclesundervariousoperatingconditions.Theproposed
modelachievedaRootMeanSquareError(RMSE)of0.001682intheNASAB0005subset,
significantly outperforming the LSTM-only model, which achieved an RMSE of 0.058334.
Thiscorrespondstoa97.12%reductioninpredictionerror,reflectingthesuperiorpredictive
performanceofourproposedmodel,withanaccuracyapproximately35timesgreaterthanthat
oftheLSTMmodelalone.TheresultsofadditionalNASAPCoEsubsetsfurtherhighlightthe
superiorperformanceandcomputationalefficiencyofthemodel,positioningitasapromising
solutionforreal-timebatteryhealthmonitoringandmanagementsystems.
1. Introduction
Lithium(Li)batterieshaveemergedasadominantenergystoragesolutionduetotheirexceptionalenergydensity,
prolongedcyclelife,fastchargingcapability,andadaptabilityacrossdiverseapplications,includingelectricvehicles,
renewableenergysystems,andportableelectronics[1,2,3].However,theirperformanceinevitablydegradeswithtime
drivenbyrepeatedchargeanddischargecycles,temperaturefluctuations,andageingeffects[4,5].Thisdegradation
notonlyreducesbatteryefficiencyandreliabilitybutalsoposessignificantsafetyrisks,particularlyinhigh-demand
applicationswhereperformanceconsistencyiscritical[6],[7].Asaresult,accurateestimationoftheStateofHealth
(SOH)isessentialtoensurethelongevityandsafeoperationofLibatteries.
SOHisakeyindicatoroftheremainingcapacityandfunctionalintegrityofabatteryrelativetoitsinitialstate.It
encompasseskeyvariablessuchasvoltage,current,temperature,andotherfactorsthatinfluencebatteryperformance.
By monitoring these parameters, SOH estimation enables early detection of performance deterioration, allowing
proactivemaintenanceandoptimizedbatteryutilization[8].
ReliableSOHpredictionisfundamentaltoBatteryManagementSystems(BMS),whichenablethemtomonitor
performance,preventfailures,andoptimizebatteryusage.Incriticalapplicationssuchaselectricvehiclesandlarge-
scale energy storage, inaccurate SOH predictions can cause system malfunctions, unplanned downtime, and safety
hazards[9].Therefore,preciseSOHestimationnotonlyimprovessafetyandreliabilitybutalsoenhancessustainability
andcost-effectivenessbyextendingthelifespanofbattery-poweredsystems[10].
ORCID(s):
: PreprintsubmittedtoElsevier Page1of22
5202
guA
13
]GL.sc[
1v69401.9052:viXra

SOH-KLSTM Model for Enhanced Lithium-Ion Battery Health Monitoring
Overtheyears,severalapproachesforestimatingtheSOHofLibatterieshavebeenproposed.Theseapproaches
canbeclassifiedintofourmaincategories:experimental,model-based,data-driven,andfusionmethods,asshownin
Figure1.Belowisabriefoverviewofthesemethods.
• Model-based approaches, such as electrochemical models and Kalman filters, are more computationally
efficient and suitable for real-time use, but are highly dependent on detailed knowledge of the internal states
ofthebattery,whichmaynotalwaysbereadilyaccessible[11].MethodsbasedontheKalmanfilterhavebeen
used,suchastheadaptiveunscentedKalmanfilter[12].
• Experimentaltechniques,includingcapacitymeasurementsandelectrochemicalimpedancespectroscopy,offer
highaccuracyinassessingbatteryhealth,butareoftenimpracticalforreal-timemonitoringduetotheirinvasive
natureanddependenceonspecializedequipment[13].
• Data-drivenmethods,drivenbyadvancesinMachineLearning(ML),havedemonstratedsubstantialpromise
in handling large-scale battery data without the need for in-depth knowledge of internal battery mechanisms.
Techniques such as SVR, Random Forests and advanced neural networks such as LSTM and Convolutional
NeuralNetworks(CNNs)haveshownremarkablesuccessinidentifyingcomplexpatternsinbatterydegradation
data [14, 15, 16]. These methods are particularly effective for the prediction of SOH in real time, where
adaptabilityandpredictiveaccuracyarecriticalforvaryingoperatingconditions.
• Fusion methods, which combine two or more methods and can include experimental, model-based, or data-
drivenapproaches,haveemergedasacomprehensivesolutionforSOHestimationbycapturingmultipleaspects
ofbatterydegradation.However,despitetheirpromise,thesehybridmodelsoftenfacechallengesduetotheir
computational complexity, which can hinder real-time applications and large-scale deployment [17]. In this
category,ahybridmethodbasedonparticleswarmoptimizationandextremeMLhasbeenproposedforenhanced
SOHestimation[18,19].
Figure 1: Classification of battery SOH estimation methods.
: PreprintsubmittedtoElsevier Page 2 of 22

SOH-KLSTM Model for Enhanced Lithium-Ion Battery Health Monitoring
CurrentSOHestimationmodelscontinuetofacechallengesinaccuratelyrepresentingthecomplexitiesassociated
withbatterydeterioration.Thesechallengesareparticularlypronouncedinreal-worldscenarioswherebatteriesoperate
under diverse environmental conditions, varying load profiles, and across different battery chemistries. The highly
complexandnonlinearinteractionsbetweeninternalbatteryparametersmakeitdifficultforconventionalMLmodels
togeneralizeeffectively.
Recurrentneuralnetworks(RNNs),suchasLSTMnetworks,haveshownpromiseintime-seriespredictiondueto
theirabilitytomodelsequentialdependencies.However,LSTMsstillfacelimitationswhenhandlingthenon-linear
and heterogeneousdegradation patternsof lithium-ion batteries. Theirreliance onstandard activation functionsand
memorycellsrestrictstheirabilitytofullycapturetheintricaterelationshipsthatgovernbatteryaging.
To address these limitations, we introduce a novel hybrid approach, the SOH-KLSTM Model, which integrates
LSTM networks with the Kolmogorov-Arnold Networks (KAN) to improve the accuracy of SOH prediction. By
embeddingKANwithintheLSTMarchitecture,weenhancetheabilityofthemodeltolearnandrepresentcomplex,
non-linear dependencies in battery degradation data. This integration significantly improves the accuracy of the Li
batteryhealthSOHestimation,representinganadvanceoverexistingmethodsthatfailtogeneralizebetweendifferent
batterytypesandoperatingconditions.TheSOH-KLSTMmodelisnotasimplecombinationofthesetwoalgorithms,
butafundamentallyenhancedLSTMdesignthatintegratesKANwithinthecorearchitecturetoimprovepredictive
accuracy.Theintegrationisachievedinaninnovativeandstructurallyuniquemanner:
• KAN-EnhancedCandidateCellState:ConventionalLSTMmodelscalculatethepotentialcellstateemploying
a transformation with fixed weights. Our model replaced this transformation with a KAN-oriented adaptive
functionthatlearnsnon-linearrelationshipsinsequentialdatadynamically.Thisenhancestheexpressivenessof
themodel,allowingittocaptureintricatedegradationbehaviorsmoreeffectively.
• B-SplineAugmentedFeatureSpace:UnlikeconventionalLSTMmodelsthatrelyjustonweightmatrices,our
approachusesB-splinetransformationsalongwiththecandidatecellstatecalculation.Thisapproachallowsfor
thedetectionofbothabruptandgradualchangesinbatterydegradationtrends,thankstoitslocalizedadaptability.
• Self-Learned Activation Functions: Conventional LSTMs limit adaptability by using predefined activation
functions such as sigmoid, tanh, or ReLU. In contrast, our model adapts to the changing dynamics of battery
healthbydynamicallylearningactivationfunctionsthroughKAN,whichallowsustostrengthenthestabilityof
gradientflow.
With these changes, the information flow in LSTM networks is much improved, enabling SOH-KLSTM to predict
batterySOHwhileaccuratelycapturingbothshort-andlong-termdegradationpatterns.
Themaincontributionsofthispaperareasfollows.
1. A novel SOH-KLSTM model is introduced that integrates KAN into the LSTM architecture to enhance the
prediction of battery SOH by capturing both temporal dependencies and complex non-linear degradation
patterns.
2. The proposed model leverages KAN-enhanced candidate cell state computation, improving the ability of the
LSTMtohandleintricatedegradationbehaviorsinLibatteries.
3. TheSOH-KLSTMmodelisimplementedandvalidatedusingseveralreal-worldbatterydatasetsfromNASA’s
PCoE, demonstrating the superior effectiveness of this hybrid model compared to the standalone LSTM in
predictingSOHindiverseoperationalconditions.
4. AcomparativestudyhighlightsthesignificantimprovementsofthemodeloverexistingSOHestimationmethods
intermsofpredictiveaccuracyandcomputationalefficiency,demonstratingitssuperiorityforreal-timebattery
managementapplications.
ThestructureofthispaperisorganizedtofirstprovideanextensivereviewoftheexistingSOHestimationmethods
inSection2,coveringtraditionalMLmodels,hybridapproaches,anddata-driventechniqueswhilehighlightingthe
research gaps addressed in this study. The LSTM model used for the estimation of SOH is detailed in Section 3,
followedbytheintroductionoftheproposedSOH-KLSTMmodelinSection4,whichdescribesitsarchitectureand
key advantages over conventional approaches. The experimental results, which demonstrate the performance of the
modelinvariousdatasets,arepresentedinSection5.Finally,thekeyfindingsaresummarizedinSection6,alongwith
suggestionsforfutureresearchtofurtherenhanceSOHpredictionmodels.
: PreprintsubmittedtoElsevier Page 3 of 22

SOH-KLSTM Model for Enhanced Lithium-Ion Battery Health Monitoring
2. RelatedWork
ThedevelopmentofreliableSOHpredictionmethodsforLibatteriesprogressedsignificantly,transitioningfrom
standardMLmodelstomoresophisticateddeeplearning(DL)frameworks.Theprimarychallengeremainstoachieve
abalancebetweenpredictionaccuracy,generalizationcapability,andcomputationalefficiency,particularlyinreal-time
applications.
The application of Artificial Intelligence (AI) in SOH prediction has evolved significantly, transitioning from
traditional regression-based methods to more advanced deep learning frameworks. A notable example is the work
ofMaetal.(2022)[20],whichintroducedanenhancedLSTM-basedSOHestimationframeworkthatincorporatesthe
extractionofhealthindicators,theselectionoffeatures,andtheoptimizationofhyperparameters.Thestudyidentified
15healthindicatorsfromthecharging-dischargingprocess,capturingexternalbatterycharacteristicssuchasvoltage,
current,andtemperaturetomodelbatteryagingandenhancingtheaccuracyandrobustnessofthepredictionofthe
model.However,theproposedmodelreliesonpredefinedhealthindicators,whichlimititsadaptabilityinscenarios
wherenoveldegradationpatternsemerge.
HybridMLmodelshaveemergedasakeyadvanceinthepredictionofSOHbycombiningmultipletechniquesto
take advantage of the strengths of each method [21, 22, 23, 24, 25, 26, 27, 28]. Bao et al. (2023) [28] introduced
a hybrid deep neural network with dimensional attention (CNN-VLSTM-DA) for SOH estimation, integrating a
CNN, a multilayer variant LSTM network and a dimensional attention mechanism. CNN extracts hierarchical
features from battery data, while VLSTM, enhanced with peephole connections, refines the ability to capture long-
term dependencies. The dimensional attention mechanism further improves feature selection by assigning different
weightstoeachdimension.ThemodelwasvalidatedonNASA,CALCE,andOxforddatasets,demonstratingstrong
performanceunderdiversecharge/dischargeconditions.However,theCNN-VLSTM-DAmodelcomeswithahigh
computationalcomplexitythatlimitsitsreal-timeapplicability.Zhuetal.(2023)[29]introducedahybridframework
combining CNNs with LSTM, enabling the model to automatically learn from time series data. CNNs effectively
capture spatial features, while LSTMs handle temporal dependencies, making this combination highly effective for
SOHprediction.However,despitetheimprovements,theapproachfacedchallengessuchasoverfitting,particularly
when applied to smaller datasets. In addition, Obisakin et al. (2022) [30] proposed a hybrid model that integrates
Support Vector Regression (SVR) with LSTM, achieving an RMSE of 0.005 in the B0005 dataset. Although this
hybrid model demonstrated improved accuracy, SVR struggled to capture the long-term dependencies crucial for
accuratebatteryhealthforecasting.ThesestudiesdemonstratedthatLSTMmodels,whilewell-suitedfortime-series
data,couldfurtherbenefitfromdomain-specificenhancementstoaddresslong-termSOHpredictionchallenges.
Recent advances have introduced more specialized methods to improve SOH prediction by integrating diverse
techniques. For example, Tao et al. (2024) [31] introduced a multiscale data fusion and anti-noise extended LSTM
(MSDF-ANELSTM) model to further enhance SOH prediction. In this approach, the feature extraction process is
automated by utilizing the Fast Fourier Transform (FFT) to analyze micro-scale data such as current and voltage
in the frequency domain, and then Principal Component Analysis (PCA) is applied to reduce feature redundancy
and prevent overfitting. Moreover, the hidden layer structure of the LSTM is improved by separating positive and
negative correlation gating weights, reducing the model’s complexity and improving generalization. Additionally, a
novelcombinationofExtendedKalmanFilter(EKF)andGradientDescent(GD)forweightupdatingfurtherenhances
noise suppression, addressing a common issue in battery data. As a result, this method significantly outperformed
traditionalLSTMmodels,achievinga66.66%improvementinaccuracy,83.84%betterstability,and72.54%improved
generalization.
In addition, recent developments in SOH estimation have explored model-data fusion approaches, combining
physics-basedmodelingandDLtoimprovepredictiveperformance.Chenetal.(2024)[19]introducedahybridSOH
estimationframeworkthatintegratesafractional-orderRCEquivalentCircuitModel(ECM)withaDLnetwork.Their
approach begins with correlation analysis to extract health features from raw battery data, followed by fractional
particle swarm optimization. These optimized parameters, which capture the internal dynamics of the battery, are
furtheranalyzedtoselectthemostrelevantSOHindicators.AnimprovedVisionTransformer(VIT)networkisthen
trained using the selected health features. The experimental results demonstrate that their method achieves higher
predictiveaccuracythanconventionaldata-drivenmodels.However,thisapproachintroducesadditionalcomputational
complexityduetoECMparameteridentificationandfeaturecorrelationanalysis. Moreover,Wangetal.(2024)[32]
introduced Physics-Informed Neural Networks (PINN), which combine empirical degradation models and state-
spaceequationsfortheestimationofSOH.Byembeddingphysics-basedprinciplesintoneuralnetworks,theirmodel
: PreprintsubmittedtoElsevier Page 4 of 22

SOH-KLSTM Model for Enhanced Lithium-Ion Battery Health Monitoring
achievedaMAPEof0.87%onadatasetof387batteries,improvinginterpretabilityandmodelrobustness.However,
PINNs, despite their precision, can be computationally intensive, limiting their scalability in large-scale real-time
applications.
FurtherinnovationcamewiththeintroductionofSelf-SupervisedLearning(SSL)methods.Cheetal.(2023)[33]
proposedanSSLframeworktoaddresstheissueoflimitedlabeleddataforthepredictionofSOH.Bycombiningauto-
encoder-decoderarchitectureswithrandomforestregression,themodeleffectivelylearnedhiddenagingcharacteristics
fromunlabeleddata,significantlyreducingrelianceonlargelabeleddatasets.Themodelachievedrobustperformance,
with an error distribution below 4% and overall errors less than 1.14%. However, the ensemble-based approach
introducedcomputationalcomplexity,limitingitssuitabilityforreal-timeSOHestimationinlarge-scalesystemswhere
efficiencyiscritical.
Furthermore, Graph-based models provide an innovative approach by capturing the underlying relationships
betweenbatteryparameters.Yaoetal.(2023)[14]introducedanovelgraph-basedframework,CL-GraphSAGE,for
thepredictionofSOH,whichcapturesbothtemporalandspatialdependenciesinbatteryhealthindicators(HIs).The
modelutilizesPearson’scorrelationcoefficientstoidentifyHIshighlycorrelatedwithSOH,formingagraphstructure
toenhancepredictionaccuracy.TemporalfeaturesarecapturedusingCNNsandLSTMs,whilespatialrelationshipsare
modeledthroughtheGraphSAGEarchitecture,whichpropagatesinformationthroughthegraph.Theresultsshowed
thatCL-GraphSAGEoutperformedtraditionalmethodssuchasCNN,LSTM,andGCN,achievinganRMSEaslow
as0.2% on datasetsfrom MIT,NASA, andexperimental sources. Thisvalidation indiverse datasets confirmedthe
robustnessofthemodel.However,whileCL-GraphSAGEimprovedaccuracybyleveragingspatialandtemporaldata,
itstruggledtocapturesequentialdependencies,whichlimiteditseffectivenessforlong-termSOHprediction.
Similarly, Wei et al. (2024) [34] proposed the Conditional Graph Convolutional Network (CGCN), designed to
enhanceSOHandRemainingUsefulLife(RUL)predictionsbycapturingbothfeature-to-featureandfeature-to-SOH
correlations.TheCGCNframeworkutilizestwotypesofundirectedgraphs:onetomodelrelationshipsbetweenbattery
features and another to model the correlations between those features and SOH or RUL. To further refine temporal
predictions,themodelincorporatesdilatedconvolutionaloperationsthatexpandthereceptivefieldandimprovethe
captureoflong-termdependenciesintime-seriesdatawithoutsignificantlyincreasingcomputationalcomplexity.The
resultsdemonstratedanotableimprovementinpredictiveaccuracy.CGCNachievedRMSEvaluesof0.73%forSOH
and 0.92% for RUL on NASA and Oxford datasets, outperforming traditional GCN and other ML models in these
tests. This improvement was attributed to the model’s ability to transmit information more effectively through the
graph,capturingbothtemporalandspatialdependencies.However,despitethesegainsinaccuracy,theCGCNfaced
challengesingeneralizingacrosshighlyvariableoperationalconditions,akeychallengeforscalableSOHandRUL
prediction.Theperformanceofthemodelwasparticularlydependentonthequalityandconsistencyofthedata,which
couldlimititseffectivenessinenvironmentswithsignificantoperationalvariability.
RecentworkshavealsoexploredattentionmechanismstoimprovetheaccuracyofthepredictionofSOH[35,36].
Zhaoetal.(2023)[36]introducedaMulti-HeadAttention-TimeConvolutionNetwork(MHAT-TCN),whichintegrates
multi-head attention learning with gray relational analysis (GRA) to identify key health indicators (HIs) correlated
with battery capacity. This approach improves the accuracy of SOH prediction by focusing on relevant HIs during
the training process. The MHAT-TCN was validated using leave-one-out cross-validation (LOOCV) across datasets
fromsimilarbatterymodels.ThemodeldemonstratedsignificantimprovementsinthepredictionofSOH,withRMSE
values of 0.0262 and MAPE of 3.6990, outperforming conventional models such as TCN and LSTM. This method
improves predictive performance by capturing local regeneration phenomena, a key factor in battery degradation
analysis.Althoughthemodelshowedsuperioraccuracyacrossvariousdatasets,itsincreasedcomputationalcomplexity
remainsalimitation,particularlywhenappliedinreal-timeapplicationswherefasterpredictionsarenecessary.
In conclusion, while various SOH prediction methods offer unique strengths, they continue to present trade-
offs between accuracy, interpretability, and scalability [8, 37, 38, 39, 40]. Hybrid models, which combine multiple
techniques,andgraph-basedapproachesshowsignificantpromiseduetotheirabilitytocapturecomplexrelationships
in the data. However, the increasing demand for large-scale real-time applications, particularly in practical battery
managementsystems(BMS),necessitatesfurtheradvancementstoenhanceefficiency,reliability,andadaptability.A
majorchallengeremainsthecomputationalcomplexityassociatedwithadvancedSOHpredictionmodels.Although
deeplearning,hybridmethods,andattention-basedmodelsimprovepredictiveperformance,theirfeasibilityforreal-
time deployment is challenged by high computational demands. Reducing complexity while maintaining predictive
accuracyiscriticalforenablingwidespreadadoptioninindustrialandautomotiveapplications.Furthermore,improving
: PreprintsubmittedtoElsevier Page 5 of 22

SOH-KLSTM Model for Enhanced Lithium-Ion Battery Health Monitoring
generalizationcapabilitiesacrossdiverseoperationalconditionsremainsakeyobjectivetoensurerobustandadaptable
performanceinrealworldscenarios.
One of the main contributions in this paper is the fusion of LSTM networks with KANs [41]. In 2024, KANs
recently gained significant traction as a promising approach, offering advantages over traditional techniques. While
some studies have explored their application in SOH estimation [42, 43, 44, 45], their full potential remains under-
utilized,particularlyinhybridarchitecturesthatintegratesequentiallearningandnonlinearfunctionapproximation.
Toaddressexistinglimitations,weproposetheSOH-KLSTMmodel,whichintegratesthestrengthsoftheLSTMand
KANnetworks.Infact,KANexcelsincapturingthenon-lineardegradationbehaviorsofLibatteries,whileLSTMis
proficientinmodelingtemporalsequencesofbatteryusage.Bycombiningthesetwoapproaches,theSOH-KLSTM
modelprovidesacomprehensivesolutionthatimprovespredictionaccuracyandgeneralizationunderdifferentbattery
conditions.ThishybridarchitectureprovidesascalableandadaptableapproachforthepredictionofSOHwithhigh
precision,generalization,andcomputationalefficiency.Unlikeprevioushybridapproaches,suchasKAN-LSTM[42]
andCNN-KAN[43],whereKANisappliedbeforeoraftertheusedmodel,ourapproachdirectlyintegratesKANinto
thecomputationofthecandidatecellstateoftheLSTM.ThisintegrationemploysB-splinetransformationsandSiLU
activationfunctions.Incontrast,existingstudieshaveappliedKANdifferently.Zhangetal.[42]useKANforfeature
compressionbeforepassingdatatoanLSTM.Pengetal.[43]applyKANafterLSTMtorefinetheextractedtemporal
features.Chenetal.[44]incorporateKANwithinaTransformer-basedfusionframework,usingB-splineinterpolation
forhigh-dimensionalfeaturetransformations.Zhangetal.[45]integrateKANwithCNN,whereitconvertshigh-level
CNN-extractedfeaturesintorefinedSOHpredictions.
Inourapproach,byembeddingKANwithintheLSTMstructureatanearlierstage,theSOH-KLSTMmodeloffers;
improvedfeaturerepresentation,morefine-grainedcontroloverhiddenstateupdates,andbettergeneralizationacross
diversebatterytypesandoperationalconditions.
3. BatteryStateofHealthEstimation:Methodology
ThehealthofLibatteriesisanimportantfactorinoptimizingenergystorageinvestments,reducingmaintenance
costs,andensuringreliableoperation.AccurateSOHestimationisessentialtoeffectivelymanagebatteryperformance.
However, this process is complex and influenced by several interrelated factors, such as charge-discharge cycles,
environmentalconditions,andinternalresistance.Thesefactorssignificantlyaffectthedegradationrateofthebattery,
whichinturnaffectsitssafety,energyefficiency,andoverallusefullife.Specifically,keyparameterssuchastemperature
variations, current loads, and voltage changes further contribute to battery deterioration, underscoring the need for
real-timemonitoringtoensureaccuratepredictions,asshowninFigure2.
3.1. ProblemStatement
TheSOHisacriticalmetricforevaluatingabattery’scurrentperformanceandestimatingitsremaininglifespan.
Itrepresentstheresidualcapacityofthebatteryrelativetoitsnominal(initial)capacitywhennew.Typically,SOHis
calculatedusingEquation1[46]:
𝐶
𝑆𝑂𝐻 = 𝑡 ×100% (1)
𝐶
𝑛𝑜𝑚𝑖𝑛𝑎𝑙
where 𝐶 represents the current battery capacity at time 𝑡, and 𝐶 is the nominal capacity specified by the
𝑡 𝑛𝑜𝑚𝑖𝑛𝑎𝑙
manufacturerwhenthebatteryisnew.
Inthecontextofbatteryhealthmonitoring,particularlyforassessingenergyefficiency,analternativeexpression
ofSOHisbasedontheratioofchargethroughput.Equation2definesthisapproach,whichcomputestheratioofthe
battery’sstartingcapacitytoitstotalchargeprovided[46]:
𝑄
𝑆𝑂𝐻 = 𝑜𝑢𝑡 ×100% (2)
𝑄
𝑖𝑛
where 𝑄 is the total discharged energy, and 𝑄 is the total energy charged into the battery. This formulation
𝑜𝑢𝑡 𝑖𝑛
highlightsthebattery’sabilitytoretainenergyduringoperation,whichisessentialforapplicationslikeelectricvehicles
andenergystoragesystems.
: PreprintsubmittedtoElsevier Page 6 of 22

SOH-KLSTM Model for Enhanced Lithium-Ion Battery Health Monitoring
Asthebatteryundergoescontinuouschargeanddischargecycles,itscapacity𝐶 graduallydecreaseswithtime,
𝑡
directlyinfluencingtheSOH.Modelingthisdegradationrequirescapturingintricatetemporaldependenciesandnon-
linearrelationshipsamongvariousoperationalparameters.TheproposedSOH-KLSTMmodelemploysasetoftime
seriesinputfeaturestoestimateboththeSOHandtheremainingbatterycapacity.Thesefeaturesareintegratedinto
theinputmatrix𝑋,representingtheoperationalstateofthesystemattime𝑡.ThemodelpredictsSOHandcapacity
𝑡
usingadifferentialequation-basedapproachasdefinedinEquation3:
𝑑𝑦̂ SOH , 𝑑𝑦̂ cap =𝑓 ( 𝑋, 𝑑ℎ 𝑡−1, 𝑑𝐶 𝑡−1;𝜃 ) (3)
𝑑𝑡 𝑑𝑡 𝑡 𝑑𝑡 𝑑𝑡
where𝑦̂ isthepredictedSOH,𝑦̂ isthepredictedbatterycapacity,𝑋 isthevectorofinputcharacteristicsat
SOH cap 𝑡
time𝑡,ℎ and𝐶 denotethehiddenandcellstatesfromtheprevioustimestep,and𝜃representsthetrainablemodel
𝑡−1 𝑡−1
parameters,suchasweightsandbiases.Theinputmatrix𝑋 playsanessentialroleinaccuratelypredictingbothSOH
𝑡
andcapacitybycapturingthenecessaryoperationalparameters,includingcurrent,voltage,temperature,andcapacity
ofthepreviouscycle.ThesefeaturesareexpressedinEquation4:
𝑋 = [C ,𝑉,𝐼,𝑇 ] (4)
𝑡 𝑡−1 𝑡 𝑡 𝑡
whereC isthecapacityofthepreviouscycle,𝑉 istheterminalvoltageattime𝑡,𝐼 istheterminalcurrentat
𝑡−1 𝑡 𝑡
time𝑡,𝑇 isthebatterytemperatureattime𝑡.
𝑡
Each of these parameters plays a distinct role in battery performance. The capacity 𝐶 reflects the capacity of
𝑡
thebatterytostoreenergy,whichdecreaseswithage.Voltage𝑉 dropsastheinternalresistanceincreases,signaling
𝑡
degradation. Current 𝐼 influences heat generation and efficiency, while temperature 𝑇 impacts chemical reactions,
𝑡 𝑡
accelerating or slowing aging. These operational features enable the SOH-KLSTM model to capture non-linear
degradationpatternsandpredictSOHandcapacitywithhighaccuracyovertime.
Figure 2: SOH estimation process for a lithium-ion battery. This diagram illustrates the key indicators used in SOH
estimation, including voltage (𝑉), current (𝐼), temperature (𝑇), and previous capacity (𝐶 ). These indicators influence
𝑡 𝑡 𝑡 𝑡+1
battery degradation and overall capacity (𝐶), which is monitored to assess SOH.
𝑡
: PreprintsubmittedtoElsevier Page 7 of 22

SOH-KLSTM Model for Enhanced Lithium-Ion Battery Health Monitoring
3.2. LSTMforSOHEstimation
Recent advancements in ML, particularly long-short-term memory networks [47, 48, 49, 50, 51, 52], have
demonstrated their effectiveness in the prediction of SOH. LSTM models excel at capturing temporal dependencies
within sequential data, making them highly suitable for real-time monitoring and identifying nonlinear degradation
patternsovertime.ThesecharacteristicsmakeLSTMnetworksidealforbatterymanagementsystems,astheyenable
accuratediagnostics,proactivedecision-making,andfailureprevention.
3.2.1. LSTMGateMechanisms
LSTM networks process sequential battery data and capture long-term dependencies within time series features
[39,53].Theirarchitectureincorporatesspecializedgatingmechanisms,includinginput,forget,andoutputgates,to
managetheflowofinformationacrosstimesteps.Thisstructurekeepsrelevantinformationwhilediscardingirrelevant
data, improving the accuracy of the SOH estimation. Managing memory over time is essential for neural networks,
andLSTMsachievethiswiththefollowinggatemechanisms:
1. InputGate(𝑖):controlstheextenttowhichnewinformationispassedintothecellstateattime𝑡:
𝑡
𝑖 =𝜎(𝑊 ⋅[ℎ ,𝑋]+𝑏) (5)
𝑡 𝑖 𝑡−1 𝑡 𝑖
where𝜎isthesigmoidactivationfunction,𝑊 istheweightmatrixfortheinputgate,ℎ istheprevioushidden
𝑖 𝑡−1
state,𝑋 isthecurrentinput,and𝑏 isthebiastermfortheinputgate.
𝑡 𝑖
2. ForgetGate(𝑓):determineshowmuchofthepreviouscellstateshouldberetained:
𝑡
𝑓 =𝜎(𝑊 ⋅[ℎ ,𝑋]+𝑏 ) (6)
𝑡 𝑓 𝑡−1 𝑡 𝑓
where𝑊 istheweightmatrixfortheforgetgate,and𝑏 isitsbiasterm.
𝑓 𝑓
3. OutputGate(𝑜):regulateshowmuchoftheupdatedcellstateispassedtothehiddenstate:
𝑡
𝑜 =𝜎(𝑊 ⋅[ℎ ,𝑋]+𝑏 ) (7)
𝑡 𝑜 𝑡−1 𝑡 𝑜
where𝑊 istheweightmatrixfortheoutputgate,and𝑏 isthecorrespondingbiasterm.
𝑜 𝑜
Thesegatemechanismsmanagethenetwork’smemoryandensurethattheLSTMeffectivelycapturesbothshort-
termandlong-termdependencieswithinthedata.
3.2.2. CellStateandHiddenStateUpdates
The LSTM model maintains two core components, the cell state and the hidden state, to update and retain
informationovertime.Thesecomponentsensurethatthenetworkdynamicallyadjustsitsmemory,retainingrelevant
informationwhileeliminatingunnecessarydetails.
1. CellStateUpdate:Thenewcellstate𝐶 iscalculatedbycombiningthepreviouscellstate𝐶 ,modulatedby
𝑡 𝑡−1
theforgetgate,withnewcandidateinformationregulatedbytheinputgate:
𝐶 =𝑓 ⋅𝐶 +𝑖 ⋅𝐶̃ (8)
𝑡 𝑡 𝑡−1 𝑡 𝑡
Thismechanismensurestheselectiveretentionofpastmemorywhileincorporatingnewinformationasneeded.
2. HiddenStateUpdate:Thehiddenstateℎ isupdatedbasedonthenewcellstate,filteredthroughtheoutput
𝑡
gate:
ℎ =𝑜 ⋅tanh(𝐶) (9)
𝑡 𝑡 𝑡
Thisupdateensuresthatrelevantaspectsofthecellstatearepassedtothehiddenstateforthenexttimestep,
maintainingcontinuityacrossthesequence.
These updates allow the LSTM to dynamically adapt its internal memory, retaining essential information over
longperiodsanddiscardingirrelevantdata.ThiscapabilitymakesLSTMnetworkshighlyeffectiveinmanagingtime-
dependentrelationshipswithinbatterydata,leadingtoimprovedbatterymanagementperformance.
: PreprintsubmittedtoElsevier Page 8 of 22

SOH-KLSTM Model for Enhanced Lithium-Ion Battery Health Monitoring
3.2.3. SOHandCapacityEstimation
OncetheLSTMprocessestheinputsequence,thefinalhiddenstateℎ,whichcapturesthetemporaldependencies
𝑡
andrelevantinformationfromtheinputfeatures,ispassedthroughafullyconnectedlayer.Thislayertransformsthe
hiddenstateintothefinalpredictionsforboththeSOHandthebatterycapacity.ThepredictionisexpressedinEquation
10
𝑦̂
SOH
,𝑦̂
cap
=𝑊 out⋅ℎ
𝑡
+𝑏
out
(10)
where 𝑊 represents the weight matrix of the fully connected layer, and 𝑏 is the bias vector that adjusts the
out out
predictions.Theoutputs𝑦̂ and𝑦̂ correspondtothepredictedSOHandbatterycapacity,respectively.
SOH cap
TheoverallprocessofSOHandcapacityestimationusingtheLSTMnetworkissummarizedinAlgorithm1.The
algorithmdetailshowtheLSTMprocessessequentialbatterydata,updatesitsinternalstates,andgeneratespredictions
forSOHandbatterycapacity.
Algorithm1LSTMforSOHandCapacityEstimation
Input:Inputsequence𝑋,hiddenstateℎ ,cellstate𝐶
𝑡 𝑡−1 𝑡−1
Output:PredictedSOH𝑦̂
SOH
andcapacity𝑦̂
cap
Initialization:
Initializeweights𝑊,𝑊 ,𝑊 ,𝑊 andbiases𝑏,𝑏 ,𝑏 ,𝑏
𝑖 𝑓 𝑜 𝐶 𝑖 𝑓 𝑜 𝐶
Initializehiddenstateℎ andcellstate𝐶
0 0
foreachtimestep𝑡do
Computepre-activation:𝑧 =𝑊 ⋅𝑋 +𝑈 ⋅ℎ +𝑏
𝑡 𝑡 𝑡−1
Updategates:
𝑖 =𝜎(𝑧 ) (Inputgate)
𝑡 𝑡,0
𝑓 =𝜎(𝑧 ) (Forgetgate)
𝑡 𝑡,1
𝑜 =𝜎(𝑧 ) (Outputgate)
𝑡 𝑡,3
Computecandidatecellstate:𝐶̃ =tanh(𝑧 )
𝑡 𝑡,2
Updatecellstate:𝐶 =𝑓 ⋅𝐶 +𝑖 ⋅𝐶̃
𝑡 𝑡 𝑡−1 𝑡 𝑡
Updatehiddenstate:ℎ =𝑜 ⋅tanh(𝐶)
𝑡 𝑡 𝑡
endfor
FinalSOHandCapacityEstimation:
𝑦̂
SOH
,𝑦̂
cap
=𝑊 out⋅ℎ
𝑡
+𝑏
out
3.3. Kolmogorov-ArnoldNetworks
Kolmogorov-ArnoldNetworksisauniversalfunctionapproximatorthatlearnsanadaptive,non-lineartransforma-
tionofinputfeatureswithoutrelyingonpredefinedactivationfunctions.KANaddressesseverallimitationsinherent
in traditional deep learning models, such as Multi-Layer Perceptrons (MLPs) [54]. Although MLPs are effective at
modeling complex patterns, they often struggle with issues of interpretability and accuracy due to their reliance on
fixedactivationfunctions.Incontrast,KANsovercomethesechallengesbyemployinglearnableactivationfunctions
along the edges, enabling a more nuanced capture of non-linear dependencies. The theoretical foundation of KANs
istheKolmogorov-Arnoldtheorem,whichguaranteesthatanycontinuousmultivariatefunction𝑓(𝑥 ,𝑥 ,…,𝑥 )can
1 2 𝑛
bedecomposedintoafinitesumofcontinuousunivariatefunctions.Inparticular,thetheoremassertsthatthereexist
continuousfunctionsΦ and𝜑 suchthat:
𝑞 𝑞,𝑝
( )
2𝑛+1 𝑛
∑ ∑
𝑓(𝑥)= Φ 𝜑 (𝑥 ) (11)
𝑞 𝑞,𝑝 𝑝
𝑞=1 𝑝=1
where Φ is responsible for aggregating the transformed inputs, while each 𝜑 (𝑥 ) individually transforms the
𝑞 𝑞,𝑝 𝑝
𝑝-thinputfeature.Theindices𝑝and𝑞denotethetransformationstagesand𝑛isthetotalnumberofinputcharacteristics.
Thisdecompositionprovidesaflexibleframeworkforrepresentingcomplexfunctionsinhigh-dimensionalspaces,as
showninFigure3.
: PreprintsubmittedtoElsevier Page 9 of 22

SOH-KLSTM Model for Enhanced Lithium-Ion Battery Health Monitoring
IntheKANframework,eachactivationfunctionisdesignedtobelearnableandismodeledasacombinationofa
basisfunctionandaB-splinetransformation:
𝜑(𝑥)=𝑤 𝑏(𝑥)+𝑤 spline(𝑥) (12)
𝑏 𝑠
𝑤 and 𝑤 are trainable scalar weights that control the contributions of the basis function 𝑏(𝑥) and the B-spline
𝑏 𝑠
transformationspline(𝑥),respectively.Althoughtheseweightscouldbemergedintothefunctions𝑏(𝑥)andspline(𝑥),
keepingthemseparateoffersfinercontroloverthemagnitudeofactivationandimprovestrainingstability.Typically,
the basis function 𝑏(𝑥) is implemented using the SiLU activation function, which provides smooth, nonmonotonic
transformationsandpromotesgradientstability.Thespline(x)transformationisexpressedasalinearcombinationof
B-splinebasisfunctions:
∑
spline(𝑥)= 𝑐𝐵(𝑥) (13)
𝑖 𝑖
𝑖
where𝐵(𝑥)aretheB-splinebasisfunctionsand𝑐 aretrainablecoefficients.Thisrepresentationallowsthemodelto
𝑖 𝑖
learnlocalizedtransformations,whichareparticularlyeffectiveincapturingfine-grainedpatternsinthedata.
Figure 3: The hierarchical structure of the two-layer KAN approach, where input features (𝑋 ,𝑋 ) are transformed using
1 2
B-spline functions (𝜑), summed, and processed through learnable activation functions (Φ ,Φ ). The B-spline activation
1 2
functioninsetillustratesthebasisexpansionprocess,demonstratinghowlocalizedfeaturerepresentationsarecombinedto
enhance predictive performance.
4. SOH-KLSTM:ProposedKAN-IntegratedCandidateCellStateinLSTMModel
The proposed SOH-KLSTM model is based on the standard LSTM architecture, incorporating its essential
components,includingmemorycells,inputgates,forgetgates,andoutputgates.Thekeyadvancementofthismodel
lies in the refinement of the candidate cell state 𝐶̃, which is dynamically optimized using Kolmogorov-Arnold
𝑡
networks.Thisenhancementallowsthemodeltoeffectivelycapturebothlinearandhighlynon-lineardependenciesin
batterydegradationtrends,leadingtoamoreaccurateandreliableestimationoftheSOH.AsillustratedinFigure4,
the KAN module replaces the conventional linear transformation used in standard LSTMs with a more flexible
nonlinearfunctionmapping,generatingtheenhancedcandidatecellstate𝐶̃KAN.UnliketraditionalLSTMarchitectures,
𝑡
where candidate cell states are computed using fixed-weight transformations, KAN introduces an adaptive learning
mechanism that dynamically adjusts function representations based on input variations. Specifically, KAN employs
: PreprintsubmittedtoElsevier Page 10 of 22

SOH-KLSTM Model for Enhanced Lithium-Ion Battery Health Monitoring
B-splinetransformations(seeSubSection4.2)andtheSiLUactivationfunction(refertoSubsection4.3)toconstructa
robustfunctionapproximationframework.TheuseofB-splinetransformationsenableslocalizedadaptability,allowing
themodeltocapturefine-grainedvariationsinSOHdata,whileSiLUactivationensuressmoothandstablegradient
propagation,improvinglearningefficiency.
Figure4:TheproposedSOH-KLSTMmodelforSOHandcapacityestimation.ThearchitectureoftheSOH-KLSTMmodel
consists of three main stages: (1) Data Preprocessing, where NASA battery datasets are split into training, validation,
andtestingsets;(2)ModelLearning,wheretheinputfeatures(voltage,current,temperature,andcapacity)areprocessed
through an LSTM-based structure enhanced with a KAN for candidate cell state computation; and (3) Performance
Validation, where the trained model outputs predictions for SOH and capacity.
: PreprintsubmittedtoElsevier Page 11 of 22

SOH-KLSTM Model for Enhanced Lithium-Ion Battery Health Monitoring
Once the enhanced candidate cell state 𝐶̃KAN is calculated, it is seamlessly integrated with the input and forget
𝑡
gate outputs to update the final cell state 𝐶. This adaptive integration refines the memory update process by
𝑡
dynamically modulating the influence of non-linear transformations, thereby capturing both short-term fluctuations
and long-term degradation patterns more effectively. Using the expressive power of KAN, the model selectively
preservescriticalbatteryhealthinformationwhileattenuatingtransientnoiseandirrelevantperturbations.Thisrefined
updatemechanismsignificantlybolsterstheSOH-KLSTMmodel’scapacitytoextractandmaintainintricatetemporal
dependenciesfromsequentialSOHdata.Byachievingajudiciousbalancebetweenmemoryretentionandforgetting,
the model improves its predictive accuracy, ensuring that essential long-term trends are learned while extraneous
detailsaresystematicallydiscarded.Consequently,thisresultsinimprovedrobustnessandreliabilityinestimatingSOH
andbatterycapacity,makingtheproposedapproachparticularlywell-suitedforreal-worldbatteryhealthmonitoring
applications.
4.1. KAN-EnhancedCandidateCellStateinLSTM
TraditionalLSTMmodelscomputethecandidatecellstateusingafixedweighttransformationbasedonasimple
lineartransformationfollowedbytanhactivation,forexample.However,thisconventionalapproachfailstocapture
complex non-linear dependencies in battery degradation patterns. The KAN-Integrated Candidate Cell State in the
LSTMmodelimprovestheconventionalLSTMbyreplacingthisstandardlineartransformationusedtocalculatethe
candidatecellstate𝐶̃ withamoreflexiblenon-lineartransformationprovidedbytheKAN.Thisenhancementaimsto
𝑡
capturebothlineartrendsandcomplexnon-lineardependenciesinsequentialdataandimprovethemodel’spredictive
accuracy. The SOH-KLSTM model is not a simple combination of two algorithms, but a fundamentally improved
LSTM design that integrates KAN within the core architecture to improve predictive accuracy. This integration is
achievedinaninnovativeandstructurallyuniquemanner.TheKANmoduleappliesB-splinetransformationsandthe
SiLUactivationfunctiontogeneratetheenrichedcandidatecellstate,denoted𝐶̃KAN.Thisimprovedcandidatestate
𝑡
incorporatesmoreinformationfromtheinput,ensuringthatthemodelcaneffectivelylearnbothsimpleandintricate
patterns.ThecalculationoftheKAN-enhancedcandidatecellstateisgivenbyEquation14:
( )
𝑘 𝑛
𝐶̃KAN =SiLU( 𝑊 ⋅[ℎ ,𝑋]+𝑏 ) + ∑ 𝑤 𝐵 ∑ Ψ (𝑋) (14)
𝑡 𝐶 𝑡−1 𝑡 𝐶 𝑗 𝑗,𝑘 𝑞,𝑝 𝑡
𝑗=1 𝑝=1
where𝑊 istheweightmatrixappliedtotheconcatenationoftheprevioushiddenstateℎ andthecurrentinput
𝐶 𝑡−1
𝑋.Thebiastermis𝑏 ,andtheSiLUactivationfunctionintroducessmoothnonlinearityforstablelearning.Thesecond
𝑡 𝐶
termusesweightedB-splinetransformations𝐵 ,parameterizedby𝑤 ,tocapturecomplexnon-lineardependencies
𝑗,𝑘 𝑗
presentintheinputdata.Thisnovelcandidatecellstaterefinementmechanismensuresthatbothshort-termfluctuations
andlong-termdegradationpatternsarecapturedeffectively,makingthemodelmorerobusttonon-stationarybattery
healthdynamics.
Aftercomputingtheenrichedcandidatecellstate𝐶̃KAN,itiscombinedwiththeoutputoftheinputgate𝑖 andthe
𝑡 𝑡
forgetgate𝑓 togeneratetheupdatedcellstateusingEquation15.
𝑡
𝐶 =𝑓 ⋅𝐶 +𝑖 ⋅𝐶̃KAN (15)
𝑡 𝑡 𝑡−1 𝑡 𝑡
In this context, the forget gate 𝑓 controls how much of the previous cell state 𝐶 is retained, ensuring that
𝑡 𝑡−1
relevant past information is preserved. The input gate 𝑖 determines how much of the new candidate state 𝐶̃KAN is
𝑡 𝑡
added,allowingthemodeltoeffectivelyincorporatenewinformation.
4.2. B-SplineTransformations
B-splinesarepiecewisepolynomialfunctionsthatprovidesmoothandlocalizedtransformationsofinputfeatures.
Unliketraditionaltransformations,whichmayimposerigidfunctionalforms,B-splinesdynamicallyadjusttocomplex
non-linearpatternsfoundinbatterydegradationdata,makingthemparticularlysuitableforSOHestimation[19].They
aredefinedbyknotpoints,whichsegmenttheinputspaceandadegree𝑘thatcontrolsthesmoothnessofthecurve.
ThebasecaseandtherecursiveformulationoftheB-splinesareexpressedinthefollowing:
: PreprintsubmittedtoElsevier Page 12 of 22

SOH-KLSTM Model for Enhanced Lithium-Ion Battery Health Monitoring
BaseCase(Degree0B-spline):
{
1 if𝑡 ≤𝑥<𝑡 ,
𝑁 (𝑥)= 𝑖 𝑖+1 (16)
𝑖,0 0 otherwise
Recursive Case (Higher Degree B-splines): Forhigher-degreeB-splines,therecursiveformulaisappliedusing
Equation17:
𝑥−𝑡 𝑡 −𝑥
𝑁 (𝑥)= 𝑖 ⋅𝑁 (𝑥)+ 𝑖+𝑘+1 ⋅𝑁 (𝑥) (17)
𝑖,𝑘 𝑡 −𝑡 𝑖,𝑘−1 𝑡 −𝑡 𝑖+1,𝑘−1
𝑖+𝑘 𝑖 𝑖+𝑘+1 𝑖+1
Where𝑁 (𝑥)istheB-splinebasisfunctionofdegree𝑘atposition𝑖,and𝑡 aretheknotpointsthatsplittheinput
𝑖,𝑘 𝑖
space.
Thetransformationappliedtoeachfeature𝑥 intheSOH-KLSTMisrepresentedbytheΨ-functioninEquation
𝑝
18:
𝑘
∑
Ψ (𝑥 )= 𝑐 𝐵 (𝑥 ) (18)
𝑞,𝑝 𝑝 𝑖,𝑞,𝑝 𝑖,𝑘 𝑝
𝑖=1
where𝐵 (𝑥 )aretheB-splinebasisfunctionsofdegree𝑘,𝑐 arethelearnedcoefficients,and𝑚isthenumber
𝑖,𝑘 𝑝 𝑖,𝑞,𝑝
ofB-splinebasisfunctions.
ConventionalDLmodelsoftenrelyonfixedactivationfunctionsthatmaynotcapturelocalizedvariationsinbattery
degradation.Incontrast,B-splinetransformationsprovideahighlyflexible,piecewisepolynomialrepresentation,and
allowourSOH-KLSTMmodeltoeffectivelymodelbothgradualandabruptchangesinSOHindicators,suchasvoltage,
current, and temperature fluctuations. By integrating learnable activations with localized B-spline transformations,
KANsofferarobustandflexibleapproachtomodelingcomplexhigh-dimensionalfunctions,therebyovercomingthe
limitationsoftraditionalMLParchitectures.
4.3. SiLUActivationFunction
TheSigmoid-weightedLinearUnitsactivationfunctionhasemergedasacompellingalternativetoconventional
activation functions, offering both smoothness and computational efficiency [55]. Ensuring smooth non-linear
transitionsfacilitatesstablegradientpropagation.OneoftheuniquestrengthsofSiLUliesinitsabilitytoretainnegative
information while preserving positive scaling, allowing neural networks to effectively capture complex patterns in
high-dimensionaldata.Thispropertyimprovestheconvergenceandgeneralizationoftraining.Asaresult,ithasbeen
widelyadoptedinvariousMLtasks,includingimageclassification,objectdetection,andnaturallanguageprocessing
[56],[57].TheSiLUfunctionisformallydefinedasfollows[58]:
𝑥
SiLU(𝑥)= =𝑥⋅𝜎(𝑥), (19)
1+𝑒−𝑥
where𝜎(𝑥)= 1 representsthesigmoidfunction.
1+𝑒−𝑥
TheSiLUfunctionexhibitsdistinctasymptoticpropertiesforlargeinputmagnitudes:
• Forlargepositiveinputs(𝑥→+∞),thesigmoidfunctionapproachesunity:
𝜎(𝑥)→1, thus,SiLUbehavesasanidentityfunction: SiLU(𝑥)≈𝑥. (20)
• Forlargenegativeinputs(𝑥→−∞),thesigmoidfunctionconvergestozero:
𝜎(𝑥)→0, thus,SiLUasymptoticallyapproacheszero: SiLU(𝑥)≈0. (21)
TheSiLUactivationfunctionissmoothandnon-monotonic,enablingstablegradientupdatesandricherrepresen-
tationsthanReLUand𝜎.Itisboundedbelowfornegativeinputs,yetunboundedabove,effectivelyscalingactivations
andmitigatingthedyingReLUproblem.Byallowinggradientsforbothpositiveandslightlynegativeinputs,SiLU
enhancesconvergenceandperformance,makingitidealforourproposedSOH-KLSTM.
: PreprintsubmittedtoElsevier Page 13 of 22

SOH-KLSTM Model for Enhanced Lithium-Ion Battery Health Monitoring
4.4. AlgorithmSteps
The SOH-KLSTM model integrates a KAN module into the LSTM architecture to predict SOH and battery
capacity.TheLSTMupdateshiddenandcellstatesovertime,whereastheKANmodulerefinesthecandidatecellstate.
Theinput,forgetandoutputgatesregulatetheinformationflowbyretainingessentialdataanddiscardingirrelevant
details.Algorithm2detailstheoperationsforSOHandcapacityestimation.Theoverallarchitectureoftheproposed
modelisdepictedinFigure4,highlightingitsthreekeystages:datapreprocessing,modellearning,andperformance
validation.
Algorithm2ProposedSOH-KLSTMmodelforSOHandCapacityEstimation
Input:Inputsequence𝑋,hiddenstateℎ ,cellstate𝐶
𝑡 𝑡−1 𝑡−1
Output:PredictedSOH𝑦̂
SOH
andbatterycapacity𝑦̂
cap
Initialization:Initializeweights𝑊
𝑖
,𝑊
𝑓
,𝑊
𝑜
,𝑊
𝐶
,KANweights𝑊
KAN
,recurrentweights𝑈
𝑖
,𝑈
𝑓
,𝑈
𝑜
,𝑈
𝐶
,B-spline
coefficients,andbiases𝑏,𝑏 ,𝑏 ,𝑏
𝑖 𝑓 𝑜 𝐶
foreachtimestep𝑡do
Computepre-activation:
𝑧 =𝑊 ⋅𝑋 +𝑈 ⋅ℎ +𝑏
𝑡 𝑡 𝑡−1
Split𝑧 intocomponents:𝑧 ,𝑧 ,𝑧 ,𝑧
𝑡 𝑡,0 𝑡,1 𝑡,2 𝑡,3
Computegateactivations:
𝑖 =𝜎(𝑧 ) (Inputgate)
𝑡 𝑡,0
𝑓 =𝜎(𝑧 ) (Forgetgate)
𝑡 𝑡,1
𝑜 =𝜎(𝑧 ) (Outputgate)
𝑡 𝑡,3
ComputeKAN-enhancedcandidatecellstate:
( )
𝑘 𝑛
𝐶̃
𝑡
KAN =SiLU(𝑊 KAN⋅𝑧
𝑡,2
+𝑏 KAN)+ ∑ 𝑤
𝑖
𝐵
𝑖,𝑘
(𝑋
𝑡
) ∑ Ψ
𝑞,𝑝
(𝑋
𝑡
)
𝑖=1 𝑝=1
Updatethecellstate:
𝐶 =𝑓 ⋅𝐶 +𝑖
⋅𝐶̃KAN
𝑡 𝑡 𝑡−1 𝑡 𝑡
Updatethehiddenstate:
ℎ =𝑜 ⋅tanh(𝐶)
𝑡 𝑡 𝑡
endfor
FinalSOHandCapacityEstimation:
𝑦̂
SOH
,𝑦̂
cap
=𝑊 out⋅ℎ
𝑡
+𝑏
out
Return:PredictedSOH𝑦̂
SOH
andbatterycapacity𝑦̂
cap
5. ExperimentsandResults
This section provides a detailed overview of the dataset, experimental setup, and results analysis of the SOH-
KLSTMmodeltopredicttheSOHofLi-ionbatteries.
: PreprintsubmittedtoElsevier Page 14 of 22

SOH-KLSTM Model for Enhanced Lithium-Ion Battery Health Monitoring
5.1. Dataset
FortheevaluationoftheSOH-KLSTNmodel,wehaveusedseveralsubsetsfromNASA’sPrognosticsCenterof
Excellence(PCoE)BatteryDataset,whichcontainsdatafrom34lithium-ion(Li-ion)18650cells,eachwithacapacity
of2Ah.Thesecellswerecycledto70%or80%oftheiroriginalcapacityundervarioustemperatureconditionsusinga
custom-builtbatterytester.Thecyclingprocessincludedthreekeyphases:charging,discharging,andelectrochemical
impedancespectroscopy(EIS).
The charging was carried out using a constant current-constant voltage (CC-CV) method at 1.5 A until the
cells reached 4.2 V, with a cutoff current of 20 mA. Various discharge profiles were used to simulate realistic
use and accelerate degradation. EIS was conducted with a frequency sweep from 0.1 to 5 KHz, providing detailed
informationontheinternalelectrochemicalpropertiesofthecells.Thisdatasetcapturesvaluablebatteryperformance
anddegradationpatternsundervariousoperationalconditions.
The selected subsets include data from rechargeable Li-ion 18650 batteries, specifically: B0005 (B05), B0007
(B07),B18,B33,B34,B46,B47,andB48.Eachsubsetincludesdifferentoperationalandenvironmentalconditions,
offeringacomprehensivebasisforevaluatingbatteryhealththroughvariousstressfactors.Thisdiversityisessential
forbuildingarobustmodelcapableofaccuratelypredictingSOHindifferentusagescenarios.Forenhancedanalysis,
thedatasetshavebeenorganizedbasedonuniformconditiondatasets,currentdischargeconditions,andtemperature
profiles,asfollows[59],[60],[61]:
1. GroupA:UniformConditionDatasetsatAmbientTemperature
ThisgroupincludesbatteriesB05,B07,andB18,whichweretestedunderidenticalconditionswithadischarge
current of 2A and an ambient temperature of 24°C. These datasets simulate moderate operating conditions,
providingabaselineforcomparisonwithmoredemandingscenarios.Theyserveasacontrolgrouptoanalyze
batterydegradationundernormalenvironmentalconditions.
2. GroupB:High-PowerCycleDatasets
ThisgroupincludesbatteriesB33andB34,testedwithahighdischargecurrentof4A.Thesedatasetsrepresent
high-powerapplicationswherefrequentrapidcharginganddischargingcyclesaccelerateagingduetothermal
stress. They are essential for evaluating the durability of Li-ion batteries in demanding applications, such as
electricvehicles.
3. GroupC:Low-TemperatureDatasets
Group C consists of batteries B46, B47, and B48, tested at a low temperature of 4°C with various discharge
currents. These datasets help assess the effects of cold environments on battery performance, including
increased internal resistance, reduced charge retention, and overall efficiency loss. This information is crucial
for applications requiring battery reliability in extreme cold, such as outdoor power systems and cold-climate
operations.
5.2. ExperimentalSetup
TheexperimentswerecarriedoutonamachineequippedwithanIntelCorei9-11900Kprocessor(3.50GHz,8
cores,16threads),64GBofDDR4RAM,andanNVIDIARTX3080GPUwith10GBofVRAM,runningUbuntu
20.04 LTS. The implementation was performed using Python 3.8, with key libraries including TensorFlow 2.x and
Keras for constructing and training the neural network. Data preprocessing and manipulation were managed using
NumPy and Pandas, while SciPy facilitated mathematical operations such as B-spline transformations to enhance
featureextraction.
For performance evaluation, scikit-learn was employed to compute metrics such as RMSE and execution time.
DatavisualizationandfurtheranalysiswereperformedusingMatplotlib,ensuringthatbothqualitativeandquantitative
aspectsofthemodelperformancewerethoroughlyassessed.
DetailedstepsfortheimplementationoftheSOH-KLSTMmodelareoutlinedbelow.
• Data Preprocessing: The dataset is divided into subsets of training (70%), validation (20%) and tests (10%)
toguaranteeareliablegeneralization.AMinMaxScalerisusedtonormalizethedataandscaleallfeaturesto
thesamerange.Thisstepimprovesmodelconvergenceandpreventsfeatureswithlargernumericalvaluesfrom
dominatingthelearningprocess.
• ModelLearning:ThetrainingprocessisperformedusingtheAdamoptimizerwithalearningrateof0.001,a
batchsizeof32,andamaximumof100epochsperfold.Earlystoppingisimplementedtohalttrainingifthe
: PreprintsubmittedtoElsevier Page 15 of 22

SOH-KLSTM Model for Enhanced Lithium-Ion Battery Health Monitoring
validationlossdoesnotimprovefor10consecutiveepochs.Adaptivelearningratereductionfurtherrefinesthe
learningprocessbyadjustingthelearningratewhenvalidationlossplateaus,ensuringoptimalconvergence.
• PerformanceValidation:Themodel’sperformanceisevaluatedusingRMSEforSOHpredictions,providing
a measure of prediction accuracy. The execution time for each fold is also recorded to assess computational
efficiency,confirmingthepracticalityofthemodelforreal-worldapplications.
5.3. EperimentalResults
TheSOH-KLSTMmodelachievedhighpredictiveaccuracyinallsubsetsofbatterydatatested.Figure5compares
the actual and predicted SOH for various battery cells. The SOH-KLSTM model effectively tracks the actual SOH
values,evenwhenbatteriesexhibitirregulardegradationpatterns.Thisperformancedemonstratesthemodel’sability
tocapturebothcontinuousandnonlineardegradationbehaviors,offeringreliableSOHpredictionsovermultiplecycles.
Table 1 presents the evaluation metrics, with RMSE quantifying predictive accuracy and execution time reflecting
computationalefficiency.
5.3.1. RMSEAnalysis
TheRMSEvaluespresentedinTable1highlightthehighaccuracyoftheSOH-KLSTMmodelacrossalldatasets
and demonstrate its robustness under different operating conditions, including varying temperatures and discharge
rates.Tofurtheranalyzetheadaptabilityofthemodel,weevaluateitsperformanceundermoderate,high-power,and
low-temperatureconditions,providinginsightsintoitsapplicabilityintherealworldinvariousscenarios.
For moderate conditions (Group A: B05, B07, B18), tested at an ambient temperature of 24°C with a discharge
currentof2A,themodelachievesimpressivelylowRMSEvalues:0.001682forB05,0.002112forB07and0.001816
forB18.TheseresultsconfirmSOH-KLSTM’shighpredictiveaccuracyinstableenvironments,makingitwell-suited
forapplicationssuchasconsumerelectronicsandrenewableenergystoragesystems,wheretemperaturefluctuations
areminimalandbatterydegradationfollowspredictabletrends.
Forhigh-powercycleconditions(GroupB:B33,B34),batteriesweresubjectedtohigherdischargecurrents(4A),
making them representative of electric vehicle and industrial applications where batteries experience frequent rapid
charging and discharging. The model maintains strong performance with RMSE values of 0.003976 for B33 and
0.002342forB34.TheslightincreaseinRMSEcomparedtomoderateconditionsisattributedtothestressimposedby
higherdischargeratesandtemperaturevariations.B33andB34weretestedatalowtemperatureof4°C,incontrastto
the24°CconditionofGroupA.At4°C,batteryefficiencytypicallydecreasesduetoincreasedinternalresistanceand
reducedionmobility.TheSOH-KLSTMmodelsuccessfullycapturesbatterydegradationtrendsinthesechallenging
conditions,confirmingitsstabilityandeffectivenessforhigh-performanceapplicationssuchaselectricvehicles,where
rapidcharge-dischargecyclesandtemperatureshiftssignificantlyaffectbatteryhealth.
BatteriesB46,B47,andB48weretestedundersimilarlow-temperatureconditions(approximately4°C)butata
muchlowerdischargerateof1A.Here,theRMSEvalueswereslightlyhigher,with0.006440forB46,0.006888for
B47,and0.007114forB48.AlthoughtheseerrorsaremarginallyhigherthanthoseinGroupB,theyremainwithin
anacceptablerange.Thissuggeststhatwhilelowerdischargecurrentsinextremelycoldconditionsmayintroducea
bitmorevariability(likelyduetothecombinedeffectsofreducedionmobilityandthelessaggressivecycling),the
modelstillrobustlytracksthebattery’sstateofhealth.
TheresultsconfirmthatSOH-KLSTMishighlyadaptabletoawiderangeofoperatingconditions.Althoughthe
model achieves the lowest RMSE in moderate conditions, it also shows strong resilience in high-power cycles and
low-temperatureenvironments,makingitsuitableforreal-worldSOHmonitoringindiverseapplications.
5.3.2. ExecutionTimeAnalysis
The computational efficiency of the SOH-KLSTM model was assessed based on execution time, as presented
inTable1.Themodelconsistentlyachievedfastprocessingtimes,demonstratingitssuitabilityforreal-timebattery
management, where timely and accurate SOH predictions are essential. Execution times ranged from 1.260 s (B46)
to 3.422 s (B33), highlighting the model’s efficiency even in high-power datasets. This rapid processing capability
ensures continuous monitoring and real-time decision-making, making SOH-KLSTM highly applicable in battery
healthdiagnosticsandpredictivemaintenance.
: PreprintsubmittedtoElsevier Page 16 of 22

SOH-KLSTM Model for Enhanced Lithium-Ion Battery Health Monitoring
Figure 5: Comparison of actual and predicted SOH for different lithium-ion battery datasets: (a) B05, (b) B07, (c) B18,
(d) B33, (e) B34, (f) B46, (g) B47, and (h) B48. The plots show the actual SOH (red points) and the predicted SOH
(blue points) over battery cycle counts.
: PreprintsubmittedtoElsevier Page 17 of 22

SOH-KLSTM Model for Enhanced Lithium-Ion Battery Health Monitoring
Table 1
Execution Time and RMSE for SOH-KLSTM on Various Data Subsets
Dataset RMSE Execution Time (s)
B05 0.001682 2.627
B07 0.002112 2.506
B18 0.001816 1.736
B33 0.003976 3.422
B34 0.002342 2.380
B46 0.006440 1.260
B47 0.006888 1.316
B48 0.007114 2.614
5.4. ComparisonwithState-of-The-ArtMethods
To evaluatethe effectiveness of theproposed SOH-KLSTM model, wecompare its performance againstseveral
state-of-the-artSOHestimationmodels,includingLSTM[14],CNN-LSTM[29],SVR-LSTM[30],DEGWO-LSTM
[20], GPR [62], SBL [63], CMMOG [64], and DGL-STFA [65], as summarized in Table 2. The comparison is
based on RMSE and Mean Absolute Percentage Error (MAPE), along with percentage error reduction, providing a
comprehensiveassessmentofpredictiveaccuracyandmodelefficiency.RMSEquantifieslargeerrormagnitudes,while
MAPEoffersarelativemeasureofpredictionaccuracy,whichisparticularlyrelevantforreal-worldSOHestimation
applications.
OntheB0005dataset,SOH-KLSTMachievesthelowestRMSEof0.001682,representinga97.12%errorreduction
comparedtoLSTM(0.058334),whileontheB0007dataset,itachieves0.002112RMSE,markinga94.85%reduction
over LSTM (0.041061). Furthermore, SOH-KLSTM demonstrates superior accuracy, with a MAPE of 0.17% on
B0005,significantlylowerthanCNN-LSTM(2.00%)andLSTM(5.83%).ComparedtoCNN-LSTM,SOH-KLSTM
achievesa65.74%improvementinRMSEduetoitsenhancedabilitytocapturelong-termdependencies.Comparedto
SVR-LSTM,whichrecordsanRMSEof0.003,SOH-KLSTMperformsbetter,benefittingfromtheKANframework’s
superior nonlinear approximation capability. These results confirm the superior accuracy and efficiency of SOH-
KLSTMtopredictbatterySOH,whichmakesithighlysuitableforreal-worldapplications.
TofurtherassesstheeffectivenessofSOH-KLSTM,wecompareditwiththeGaussianProcessRegression(GPR)
modelproposedbyYaoetal.[62].Thismodeldemonstratesstrongtheoreticalperformance,butishighlysensitiveto
thevariabilityoftrainingdata,whichreducesitsreliabilityindynamicenvironments.
Additionally,wecomparedSOH-KLSTMwiththeLSTM-basedSOHestimationmodelthatincorporateshealth
indicatorselectionandhyperparameteroptimizationusingtheDifferentialEvolutionGreyWolfOptimizer(DEGWO)
[20].Thismethodselectsvoltage,current,andtemperature-basedHIs,appliesPearsoncorrelationandNeighborhood
ComponentAnalysis(NCA)toeliminateredundancy,andoptimizesLSTMhyperparametersusingDEGWO.Although
DEGWO-LSTM achieves improved feature selection, it falls short in terms of nonlinear feature representation and
temporal modeling, resulting in higher RMSE values (0.325 on B0005 and 0.377 on B0007) compared to SOH-
KLSTM.
Furthermore,weevaluatedSOH-KLSTMagainsttheSparseBayesianLearning(SBL)modelproposedbyLietal.
[63],whichextractsmulti-sourceHIsfromvoltage,temperature,andincrementalcapacitycurves.TheSBLframework
employsBayesianinferenceandfeatureselectionusingPearsoncorrelationtoimproveestimationaccuracy.However,
it imposes high computational costs, which reduces its real-time applicability. The SBL model records high RMSE
values(3.5656onB0005and2.6153onB0007),indicatingaweakerpredictiveprecisioncomparedtoSOH-KLSTM.
We also compared our model with the Convolutional Neural Network-Multi-gate Mixture of Gated Recurrent
Units(CMMOG)modelproposedbyZhangetal.[64].Thisapproachintegratesmulti-tasklearningforsimultaneous
SOH regression across multiple battery conditions, combining CNN for feature extraction, GRU for state mapping,
and a multi-gated network for weight optimization. However, it fails to maintain high precision across different
charge/dischargeconditions,withRMSEvaluesashighas0.6490onB0005.
Finally,wecompareSOH-KLSTMwiththeDGL-STFAmodel[65],whichleveragesdynamicgraphlearningand
spatial–temporalfusionattentionmechanismstomodelevolvingrelationshipsbetweenbatteryhealthindicators.DGL-
STFArecordsanRMSEof0.876,highlightingitscomputationalinefficiencycomparedtotheproposedSOH-KLSTM.
: PreprintsubmittedtoElsevier Page 18 of 22

SOH-KLSTM Model for Enhanced Lithium-Ion Battery Health Monitoring
Table 2
Comparison of proposed SOH-KLSTM performance for SOH prediction with other models proposed in the literature.
B0005 Dataset1 B0007 Dataset2
RMSE MAPE Error RMSE MAPE Error
Ref Model
↓(%) ↓(%) Reduction ↑(% ) ↓(%) ↓(%) Reduction ↑(%)
Obisakin et al.
SVR-LSTM 0.003 0.30 94.86% – – –
[30]
Ma et al. [20] DEGWO-LSTM 0.325 0.467 - 0.377 0.423 -
Yao et al. [14] LSTM 0.058334 5.83 – 0.041061 4.11 –
Zhu et al.[29] CNN-LSTM 0.02 2.00 65.74 0.03 3.00 26.83
Lie et al. [63] SBL 3.5656 - - 2.6153 - -
Yao et al. [62] GPR 0.0114 - - - - -
Zhang et al. [64] CMMOG 0.6490 0.4731 - - -
Chen et al. [65] DGL-STFA 0.876 - - 0.876 - -
Proposed model SOH-KLSTM 0.001682 0.17 97.12 0.002112 0.21 94.85
These results confirm that SOH-KLSTM achieves state-of-the-art accuracy while maintaining computational
efficiency,makingitanoptimalsolutionforreal-worldapplications,includingelectricvehiclesandindustrialbattery
managementsystems.
5.5. Discussion
The results confirm that the SOH-KLSTM model provides an optimal balance between accuracy and efficiency.
ThelowRMSEvaluesacrossdiversedatasetshighlightthemodel’sabilitytoaccuratelypredictSOHundervarious
conditions,includingchallenginghigh-powerandlow-temperatureenvironments.Inaddition,itsfastexecutiontimes
support real-time applications, such as electric vehicles, consumer electronics, and grid energy storage. The SOH-
KLSTMmodelsetsanewstandardfortheestimationofSOHinLibatteries,providingareliable,scalable,andreal-
timesolutionforaccuratebatteryhealthprediction.
Below,wehighlightthemajorfindings,relatedtotheproposedSOH-KLSTM,fromtheexperiments:
• Predictive Accuracy: The SOH-KLSTM model consistently achieves lower RMSE values across datasets,
outperformingconventionalandhybridmethods.TheinclusionofKANimprovesthemodel’sabilitytocapture
intricatedegradationpatterns,leadingtosuperiorpredictionaccuracy.
• Generalization Across Operating Conditions: The SOH-KLSTM model demonstrates robustness across a
rangeofoperationalconditions,includinghigh-powercyclesandlow-temperatureenvironments.Forexample,
ontheB33high-powercycledataset,themodelachievedanRMSEof0.003976,whileonthelow-temperature
B46 dataset, the RMSE was 0.006440, confirming its versatility for real-world applications such as electric
vehicles.
• ComputationalEfficiency:Withexecutiontimesrangingbetween1.26sand3.42s,theSOH-KLSTMmodel
is computationally efficient, making it well-suited for real-time applications. Fast execution is particularly
importantforBMS,wheretimelySOHpredictionsareessential.
The integration of KAN into the LSTM architecture significantly enhances the ability of the model to capture
thecomplex,non-lineardynamicspresentinbatterydegradationprocesses.Thesekeyimprovementsdistinguishthe
SOH-KLSTMmodelfromconventionalLSTMapproaches:
• Non-LinearRepresentation:SOH-KLSTMutilizesB-splinetransformationsforeachinputfeature,enabling
themodeltocapturelocalizednon-lineardependenciesthattraditionalLSTMmodelsoftenfailtograsp.
• Localized Feature Interactions: By incorporating B-spline basis functions, SOH-KLSTM achieves fine-
grained control over input-output mappings. This is crucial for the estimation of SOH,as battery degradation
patternsvarybetweendifferentregionsoftheinputspace.
: PreprintsubmittedtoElsevier Page 19 of 22

SOH-KLSTM Model for Enhanced Lithium-Ion Battery Health Monitoring
• SiLUActivationforStability:TheinclusionoftheSiLUactivationfunctionensuressmooth,stablelearning
by maintaining zero-mean and unit-variance activations, accelerating convergence and mitigating issues like
vanishingorexplodinggradients.
• Improved Prediction Accuracy: By combining B-spline transformations for local modeling with SiLU’s
stabilizing effects, SOH-KLSTM enhances prediction accuracy for SOH and battery capacity, capturing both
globaltrendsandlocalizedpatternsformorereliablepredictions.
6. Conclusion
The SOH-KLSTM model offers significant advances in the prediction of SOH for lithium-ion batteries by
integrating KAN to enhance the candidate cell state within LSTM networks. This integration, combined with
experimentalvalidationonmultiplesubsetsofNASA’sPrognosticsCenterofExcellence(PCoE)dataset,demonstrates
thatSOH-KLSTMachievessuperiorpredictiveaccuracy,withuptoa97.12%reductioninpredictionerrorcompared
tobaselinemodels.ThepowerfulabilityoftheKANmoduletocapturecomplexandnon-lineardegradationpatterns
furtherbooststhemodel’sperformance,enablingittooutperformadvancedmethodssuchasCNN-LSTMandSVR-
LSTM.Consequently,theSOH-KLSTMmodelprovidesreliableSOHpredictionsindiverseoperationalconditions,
includinghigh-powercyclesandlow-temperatureenvironments,makingitidealforapplicationsinelectricvehicles,
renewableenergystoragesystems,andotherindustriesrequiringefficientbatterymanagement.Futureworkwillfocus
on predicting Remaining Useful Life (RUL), improving computational efficiency, and extending SOH-KLSTM to
batterypacks.Byapplyingthemodelatthecelllevelandaggregatingpredictionsusingfusionstrategies(e.g.,weighted
averaging,andadaptivetechniques),ouraimistodeveloparobustframeworkforpack-levelSOHestimation,enhancing
itsreal-worldapplicability.
Declarationofinterests
Theauthorsdeclarethattheyhavenoknownfinancialinterestsorpersonalrelationshipsthatcouldhaveinfluenced
theworkpresentedinthispaper.
Acknowledgements
TheauthorswouldliketothankPrinceSultanUniversityfortheirsupport.
References
[1] AyatGharehghani,MoeedRabiei,SadeghMehranfar,SoheilSaeedipour,AminMahmoudzadehAndwari,AntonioGarcía,andCarlosMico
Reche. Progressinbatterythermalmanagementsystemstechnologiesforelectricvehicles. RenewableandSustainableEnergyReviews,
202:114654,2024.
[2] ImenJarraya,FerdaousMasmoudi,MohamedHediChabchoub,andHafedhTrabelsi.Anonlinestateofchargeestimationforlithium-ionand
supercapacitorinhybridelectricdrivevehicle.JournalofEnergyStorage,26:100946,2019.
[3] FatmaAbdelhedi,ImenJarraya,HaneenBawayan,MohamedAbdelkeder,NassimRizoug,andAnisKoubaa. Optimizingelectricvehicles
efficiency with hybrid energy storage: Comparative analysis of rule-based and neural network power management systems. Energy,
313:133979,2024.
[4] MengLi,YulunZhang,HuiZhou,FengxiaXin,MStanleyWhittingham,andBoryannLiaw.Lithiuminventorytrackingasanon-destructive
batteryevaluationandmonitoringmethod.NatureEnergy,9(5):612–621,2024.
[5] ImenJarrraya,LaidDegaa,NassimRizoug,MohamedHediChabchoub,andHafedhTrabelsi.Comparisonstudybetweenhybridnelder-mead
particleswarmoptimizationandopencircuitvoltage—recursiveleastsquareforthebatteryparametersestimation.JournalofEnergyStorage,
50:104424,2022.
[6] FoadH.Gandoman,JorisJaguemont,ShovonGoutam,RahulGopalakrishnan,YousefFirouz,TheodorosKalogiannis,NoshinOmar,and
JoeriVanMierlo. Conceptofreliabilityandsafetyassessmentoflithium-ionbatteriesinelectricvehicles:Basics,progress,andchallenges.
AppliedEnergy,251:113343,2019.
[7] HuixinTian,PengliangQin,KunLi,andZhenZhao.Areviewofthestateofhealthforlithium-ionbatteries:Researchstatusandsuggestions.
JournalofCleanerProduction,261:120813,2020.
[8] SaharKhaleghi,MdSazzadHosen,JoeriVanMierlo,andMaitaneBerecibar. Towardsmachine-learningdrivenprognosticsandhealth
managementofli-ionbatteries.acomprehensivereview.RenewableandSustainableEnergyReviews,192:114224,2024.
[9] S.Seoletal.Improvingsohestimationforlithium-ionbatteriesusingtimegan.JournalofPowerSources,490:229693,2023.
[10] ChaolongZhang,LaijinLuo,ZhongYang,ShaishaiZhao,YigangHe,XiaoWang,andHongxiaWang.Batterysohestimationmethodbased
ongradualdecreasingcurrent,doublecorrelationanalysisandgru.GreenEnergyandIntelligentTransportation,2(5):100108,2023.
: PreprintsubmittedtoElsevier Page 20 of 22

SOH-KLSTM Model for Enhanced Lithium-Ion Battery Health Monitoring
[11] L.ZhengandX.Guo.Comparativestudyonincrementalcapacityanalysiswithmachinelearningalgorithmsforstateofhealthestimationof
lithium-ionbatteries.IEEETransactionsonPowerDelivery,2023.
[12] ShulinLiu,XiaDong,XiaodongYu,XiaoqingRen,JinfengZhang,andRuiZhu.Amethodforstateofchargeandstateofhealthestimation
oflithium-ionbatterybasedonadaptiveunscentedkalmanfilter. EnergyReports,8:426–436,2022. The2022InternationalConferenceon
EnergyStorageTechnologyandPowerSystems.
[13] G.Nuroldayevaetal.Stateofhealthestimationmethodsforlithium-ionbatteries.InternationalJournalofEnergyResearch,2023.
[14] Xing-YanYao,GuolinChen,MichaelPecht,andBinChen. Anovelgraph-basedframeworkforstateofhealthpredictionoflithium-ion
battery.JournalofEnergyStorage,58:106437,2023.
[15] Y.Liangetal. Stateofhealthpredictionoflithium-ionbatteriesusingcombinedmachinelearningmodelbasedonnonlinearconstraint
optimization.JournalofTheElectrochemicalSociety,2024.
[16] KailongLiu,YunlongShang,QuanOuyang,andWidanalageDhammikaWidanage. Adata-drivenapproachwithuncertaintyquantification
forpredictingfuturecapacitiesandremainingusefullifeoflithium-ionbattery.IEEETransactionsonIndustrialElectronics,68(4):3170–3180,
2020.
[17] NassimNoura,LoïcBoulon,andSamirJemeï. Areviewofbatterystateofhealthestimationmethods:Hybridelectricvehiclechallenges.
WorldElectricVehicleJournal,11(4):66,2020.
[18] KuiChen,JialiLi,KaiLiu,ChangshanBai,JiaminZhu,GuoqiangGao,GuangningWu,andSalahLaghrouche. Stateofhealthestimation
for lithium-ion battery based on particle swarm optimization algorithm and extreme learning machine. Green Energy and Intelligent
Transportation,3(1):100151,2024.
[19] GuanxuChen,FangfangYang,WeiwenPeng,YuqianFan,andXiminLyu. State-of-healthestimationforlithium-ionbatteriesbasedon
kullback–leiblerdivergenceandaretentivenetwork.AppliedEnergy,376:124266,2024.
[20] YanMa,CeShan,JinwuGao,andHongChen.Anovelmethodforstateofhealthestimationoflithium-ionbatteriesbasedonimprovedlstm
andhealthindicatorsextraction.Energy,251:123973,2022.
[21] KristenASeverson,PeterMAttia,NormanJin,NicholasPerkins,BenbenJiang,ZiYang,MichaelHChen,MuratahanAykol,PatrickK
Herring,DimitriosFraggedakis,etal.Data-drivenpredictionofbatterycyclelifebeforecapacitydegradation.NatureEnergy,4(5):383–391,
2019.
[22] KaushikDas,RoushanKumar,andAnurupKrishna.Analyzingelectricvehiclebatteryhealthperformanceusingsupervisedmachinelearning.
RenewableandSustainableEnergyReviews,189:113967,2024.
[23] MahshidNAmiri,AnneHåkansson,OdneSBurheim,andJacobJLamb.Lithium-ionbatterydigitalization:Combiningphysics-basedmodels
andmachinelearning.RenewableandSustainableEnergyReviews,200:114577,2024.
[24] YaxiangFan,FeiXiao,ChaoranLi,GuorunYang,andXinTang.Anoveldeeplearningframeworkforstateofhealthestimationoflithium-ion
battery.JournalofEnergyStorage,32:101741,2020.
[25] YingZhangandYan-FuLi. Prognosticsandhealthmanagementoflithium-ionbatteryusingdeeplearningmethods:Areview. Renewable
andsustainableenergyreviews,161:112282,2022.
[26] YuxiangCai,WeiminLi,TaimoorZahid,ChunhuaZheng,QingguangZhang,andKunXu. Earlypredictionofremainingusefullifefor
lithium-ionbatteriesbasedonceemdan-transformer-dnnhybridmodel.Heliyon,9(7),2023.
[27] JiahuanLu,RuiXiong,JinpengTian,ChenxuWang,andFengchunSun.Deeplearningtoestimatelithium-ionbatterystateofhealthwithout
additionaldegradationexperiments.NatureCommunications,14(1):2760,2023.
[28] XinyuanBao,LipingChen,AntónioMLopes,XinLi,SiqiangXie,PenghuaLi,andYangQuanChen. Hybriddeepneuralnetworkwith
dimensionattentionforstate-of-healthestimationoflithium-ionbatteries.Energy,278:127734,2023.
[29] ChunxiangZhu,MingyuGao,ZhiweiHe,HengWu,ChangchengSun,ZhaoweiZhang,andZhengyiBao.Stateofhealthpredictionforli-ion
batterieswithend-to-enddeeplearning.JournalofEnergyStorage,65:107218,2023.
[30] InioluwaObisakinandChikodinakaVanessaEkeanyanwu.Stateofhealthestimationoflithium-ionbatteriesusingsupportvectorregression
andlongshort-termmemory.OpenJournalofAppliedSciences,12(8):1366–1382,2022.
[31] JunjieTao,ShunliWang,WenCao,YixiuCui,CarlosFernandez,andJosepM.Guerrero. Innovativemultiscalefusion-antinoiseextended
longshort-termmemoryneuralnetworkmodelingforhighprecisionstateofhealthestimationoflithium-ionbatteries.Energy,page133541,
2024.
[32] FujinWang,ZhiZhai,ZhibinZhao,YiDi,andXuefengChen. Physics-informedneuralnetworkforlithium-ionbatterydegradationstable
modelingandprognosis.NatureCommunications,15(1):4332,2024.
[33] YunhongChe,YushengZheng,XinSui,andRemusTeodorescu.Boostingbatterystateofhealthestimationbasedonself-supervisedlearning.
JournalofEnergyChemistry,84:335–346,2023.
[34] YupengWeiandDazhongWu.Stateofhealthandremainingusefullifepredictionoflithium-ionbatterieswithconditionalgraphconvolutional
network.ExpertSystemswithApplications,238:122041,2024.
[35] HuanWang,Yan-FuLi,andYingZhang. Bioinspiredspikingspatiotemporalattentionframeworkforlithium-ionbatteriesstate-of-health
estimation.RenewableandSustainableEnergyReviews,188:113728,2023.
[36] HongqianZhao,ZhengChen,XingShu,JiangweiShen,ZhenzhenLei,andYuanjianZhang.Stateofhealthestimationforlithium-ionbatteries
basedonhybridattentionanddeeplearning.ReliabilityEngineering&SystemSafety,232:109066,2023.
[37] LingzhiSu,YanXu,andZhaoyangDong.State-of-healthestimationoflithium-ionbatteries:Acomprehensiveliteraturereviewfromcellto
packlevels.EnergyConversionandEconomics,2024.
[38] MohammedHindawiandSaeedMianQaisarªYasirBasheer.Anoverviewofartificialintelligencedrivenli-ionbatterystateestimation.IoT
Enabled-DCMicrogrids:Architecture,Algorithms,Applications,andTechnologies,page121,2024.
[39] PierpaoloDini,AntonioColicelli,andSergioSaponara.Reviewonmodelingandsoc/sohestimationofbatteriesforautomotiveapplications.
Batteries,10(1):34,2024.
: PreprintsubmittedtoElsevier Page 21 of 22

SOH-KLSTM Model for Enhanced Lithium-Ion Battery Health Monitoring
[40] XiangyangXia,JiahuiYue,YuanGuo,ChonggengLv,XiaoyongZeng,YongkaiXia,andGuiquanChen. Technologiesforenergystorage
powerstationssafetyoperation:Batterystateevaluationsurveyandacriticalanalysis.IEEEAccess,12:31334–31356,2024.
[41] Yuntian Hou, Jinheng Wu, Xiaohang Feng, et al. A comprehensive survey on kolmogorov arnold networks (kan). arXiv preprint
arXiv:2407.11075,2024.
[42] ZhaoZhang,RunrunZhang,XinLiu,ChaolongZhang,GengzhiSun,YujieZhou,ZhongYang,XumingLiu,ShiChen,XinyuDong,etal.
Advancedstate-of-healthestimationforlithium-ionbatteriesusingmulti-featurefusionandkan-lstmhybridmodel. Batteries,10(12):433,
2024.
[43] JunPeng,XuanZhao,JianMa,DeanMeng,ShuhaiJia,KaiZhang,ChenyanGu,andWenhaoDing.Stateofhealthestimationofli-ionbattery
viaincrementalcapacityanalysisandinternalresistanceidentificationbasedonkolmogorov–arnoldnetworks.Batteries,10(9),2024.
[44] ChuangChen,YuhengWu,JiantaoShi,DongdongYue,GeShi,andDongzhenLyu. Aparallelweightedadtc-transformerframeworkwith
funetfusionandkanforimprovedlithium-ionbatterysohprediction.ControlEngineeringPractice,159:106302,2025.
[45] YujieZhou,ChaolongZhang,XulongZhang,andZihengZhou. Lithium-ionbatterysohestimationmethodbasedonmulti-featureand
cnn-bilstm-mha.WorldElectricVehicleJournal,15(7):280,2024.
[46] HanLiu,XinyuCao,FengdaoZhou,andGangLi. Onlinefusionestimationmethodforstateofchargeandstateofhealthinlithiumbattery
storagesystems.AIPAdvances,13(4),2023.
[47] HaoZhang,HanleiSun,LeKang,YiZhang,LichengWang,andKaiWang. Predictionofhealthlevelofmultiformlithiumsulfurbatteries
basedonincrementalcapacityanalysisandanimprovedlstm.ProtectionandControlofModernPowerSystems,9(2):21–31,2024.
[48] BaoliangChen,YongguiLiu,andBinXiao. Anovelhybridneuralnetwork-basedsohandrulestimationmethodforlithium-ionbatteries.
JournalofEnergyStorage,98:113074,2024.
[49] YiwenSun,HengweiXie,QiDiao,HongzhangXu,XiaojunTan,YuqianFan,andLiangliangWei. Anovelsohestimationmethodwith
attentionalfeaturefusionconsideringdifferentialtemperaturefeaturesforlithium-ionbatteries. IEEETransactionsonInstrumentationand
Measurement,2024.
[50] HuanweiXu,LingfengWu,ShizheXiong,WeiLi,AkhilGarg,andLiangGao.Animprovedcnn-lstmmodel-basedstate-of-healthestimation
approachforlithium-ionbatteries.Energy,276:127585,2023.
[51] ShuminChen,JialiYu,LingxinCui,MengtingChen,andMinXiao. Adata-drivenbatterysohestimationmethodwithcnn-lstmmodeland
ssaoptimizing.In202436thChineseControlandDecisionConference(CCDC),pages3381–3385.IEEE,2024.
[52] HuzaifaRauf,MuhammadKhalid,andNaveedArshad.Machinelearninginstateofhealthandremainingusefullifeestimation:Theoretical
andtechnologicaldevelopmentinbatterydegradationmodelling.RenewableandSustainableEnergyReviews,156:111903,2022.
[53] ZhongRenandChangqingDu.Areviewofmachinelearningstate-of-chargeandstate-of-healthestimationalgorithmsforlithium-ionbatteries.
EnergyReports,9:2993–3021,2023.
[54] ZimingLiu,YixuanWang,SachinVaidya,FabianRuehle,JamesHalverson,MarinSoljačić,ThomasYHou,andMaxTegmark. Kan:
Kolmogorov-arnoldnetworks.arXivpreprintarXiv:2404.19756,2024.
[55] StefanElfwing,EijiUchibe,andKenjiDoya. Sigmoid-weightedlinearunitsforneuralnetworkfunctionapproximationinreinforcement
learning.Neuralnetworks,107:3–11,2018.
[56] MatthiasWolff,FlorianEilers,andXiaoyiJiang. Cvkan:Complex-valuedkolmogorov-arnoldnetworks. arXivpreprintarXiv:2502.02417,
2025.
[57] MuhammadUmairDanishandKatarinaGrolinger. Kolmogorov–arnoldrecurrentnetworkforshorttermloadforecastingacrossdiverse
consumers.EnergyReports,13:713–727,2025.
[58] HangShuaiandFangxingLi. Physics-informedkolmogorov-arnoldnetworksforpowersystemdynamics. IEEEOpenAccessJournalof
PowerandEnergy,2025.
[59] XueyingZhengandXiaogangDeng. State-of-healthpredictionforlithium-ionbatterieswithmultiplegaussianprocessregressionmodel.
IEEEAccess,7:150383–150394,2019.
[60] JeyeongLim,Eui-SeongHan,DongHwanKim,andByoungKukLee.Anoptimalclusteringalgorithmforseconduseofretiredevbatteries
usingdbscanandpcaschemesconsideringperformancedeviation. In2023IEEEAppliedPowerElectronicsConferenceandExposition
(APEC),pages582–586.IEEE,2023.
[61] BingyangChen,LuluFan,XingjieZeng,MuGu,andJiehanZhou. Acontribution-awarefederatedframeworkforelectricvehiclebatteries
healthestimation.IEEEInternetofThingsJournal,2024.
[62] LeiYao,JishuWen,YanqiuXiao,CaipingZhang,YongpengShen,GuangzhenCui,andDandanXiao. Stateofhealthestimationapproach
forli-ionbatteriesbasedonmechanismfeatureempowerment.JournalofEnergyStorage,84:110965,2024.
[63] XiaoyuLi,MohanLyu,KuoLi,XiaoGao,CaixiaLiu,andZhaoshengZhang. Lithium-ionbatterystateofhealthestimationbasedon
multi-sourcehealthindicatorsextractionandsparsebayesianlearning.Energy,282:128445,2023.
[64] ChaolongZhang,LiangTu,ZhongYang,BolunDu,ZihengZhou,JiWu,andLipingChen. Acmmog-basedlithium-batterysohestimation
methodusingmulti-tasklearningframework.JournalofEnergyStorage,107:114884,2025.
[65] ZhengChenandQuanQian.Dgl-stfa:Predictinglithium-ionbatteryhealthwithdynamicgraphlearningandspatial–temporalfusionattention.
EnergyandAI,19:100462,2025.
: PreprintsubmittedtoElsevier Page 22 of 22

