# Page 1

PublishedasaconferencepaperatICLR2025
FREDF: LEARNING TO FORECAST IN THE FREQUENCY
DOMAIN
HaoWang1 LichengPan1 YuanShen1 ZhichaoChen1 DeguiYang2
YifeiYang3 SenZhang4 XinggaoLiu1 HaoxuanLi5∗ DachengTao6∗
1DepartmentofControlScienceandEngineering,ZhejiangUniversity
2SchoolofAutomation,CentralSouthUniversity
3DepartmentofComputerScienceandEngineering,ShanghaiJiaoTongUniversity
4TrustandSafetyTeam,TikTokSydney,ByteDanceInc.
5CenterforDataScience,PekingUniversity
6GenerativeAILab,CollegeofComputingandDataScience,NanyangTechnologicalUniversity
Ho-ward@outlook.com hxli@stu.pku.edu.cn dacheng.tao@ntu.edu.sg
ABSTRACT
Timeseriesmodelingpresentsuniquechallengesduetoautocorrelationinbothhis-
toricaldataandfuturesequences. Whilecurrentresearchpredominantlyaddresses
autocorrelationwithinhistoricaldata,thecorrelationsamongfuturelabelsareoften
overlooked. Specifically,modernforecastingmodelsprimarilyadheretotheDirect
Forecast(DF)paradigm,generatingmulti-stepforecastsindependentlyanddisre-
gardinglabelautocorrelationovertime. Inthiswork,wedemonstratethatthelearn-
ingobjectiveofDFisbiasedinthepresenceoflabelautocorrelation. Toaddress
thisissue,weproposetheFrequency-enhancedDirectForecast(FreDF),whichmit-
igateslabelautocorrelationbylearningtoforecastinthefrequencydomain,thereby
reducingestimationbias. OurexperimentsshowthatFreDFsignificantlyoutper-
formsexistingstate-of-the-artmethodsandiscompatiblewithavarietyofforecast
models. Codeisavailableathttps://github.com/Master-PLC/FreDF.
1 INTRODUCTION
Time series modeling aims to utilize historical sequence to predict future data, which has been
successfullyappliedinvariousfields(Qiuetal.,2025),includinglong-termforecastinginweather
prediction(Bietal.,2023),short-termpredictionsinsecurity(Yanetal.,2024),anddataimputationin
industrialmaintenance(Wangetal.,2024b). Akeychallengeintimeseriesmodeling,distinguishing
itfromcanonicalregressiontasks,isthepresenceofautocorrelation,whichreferstothedependence
betweentimestepsinherentinboththeinputandlabelsequences.
Toaccommodateautocorrelationininputsequences,diverseforecastmodelshavebeendeveloped,
exemplified by recurrent (Salinas et al., 2020), convolution (Wu et al., 2023) and graph neural
networks(Yietal.,2023a). Recently,Transformer-basedmodels,utilizingself-attentionmechanisms
todynamicallyassessautocorrelation,havegainedprominence(Liuetal.,2024;Nieetal.,2023).
Concurrently,thereisagrowingtrendofincorporatingfrequencyanalysisintoforecastmodels. By
representingtheinputsequenceinthefrequencydomain,inputautocorrelationcanbeefficiently
accommodated, which proves to improve the forecast performance of Transformers (Zhou et al.,
2022)andMulti-LayerPerceptrons(MLPs)(Yietal.,2023b). Thesepioneeringworkshighlightthe
importanceofautocorrelationandfrequencyanalysisinadvancedtimeseriesmodeling.
Anothercriticalaspectistheautocorrelationwithinthelabelsequence,whereeachfuturestepis
autoregressivelydependentonitspredecessors. Thisphenomenon,termedaslabelautocorrelation,
posesacriticalissuewarrantinginvestigation. Specifically,recentforecastingmethodspredominantly
employtheDirectForecast(DF)paradigm(Liuetal.,2024;Nieetal.,2023),whichgeneratesmulti-
steppredictionssimultaneouslyviaamulti-outputhead(Liuetal.,2022b),optimizingforecasterrors
acrossallstepsconcurrently. However,thisapproachimplicitlyassumesstep-wiseindependencein
∗Correspondingauthor.
1
5202
yaM
6
]GL.sc[
2v99320.2042:viXra

---

# Page 2

PublishedasaconferencepaperatICLR2025
thelabelsequence,overlookingthelabelautocorrelationinherentinthetimeseriesforecasttask. We
theoreticallydemonstratethatthisoversightresultsinbiasedforecasts,revealingasignificantdefect
withtheexistingDFparadigm.
Toaddressthisissue,weintroducetheFrequency-enhancedDirectForecast(FreDF),astraightfor-
wardyeteffectiverefinementoftheDFparadigm. Thecentralideaistoaligntheforecastsandlabel
sequencesinthefrequencydomain,wherethelabelcorrelationisfoundtobeeffectivelydiminished.
ThismethodresolvesthediscrepancybetweenthescopeofDFandthecharacteristicsofactualtime
series,whileretainingDF’sadvantages,suchassampleefficiencyandsimplicityofimplementation.
Ourmaincontributionsaresummarizedasfollows:
• Weuncoverlabelautocorrelationasacriticalyetunderexploredchallengeinmoderntimeseries
modelingandtheoreticallyjustifyhowitbiasesthelearningobjectiveoftheprevalentDFparadigm.
• WeproposeFreDF,astraightforwardyeteffectivemodificationtotheDFparadigmthatlearnsto
forecastinthefrequencydomain,therebymitigatinglabelautocorrelationandreducingbias. To
ourknowledge,thisisthefirstefforttoutilizefrequencyanalysisforenhancingforecastparadigms.
• WevalidatetheefficacyofFreDFthroughcomprehensiveexperiments,demonstratingitsabilityto
enhancetheperformanceofstate-of-the-artforecastingmodelsacrossadiverserangeofdatasets.
2 PRELIMINARIES AND RELATED WORK
2.1 PROBLEMDEFINITION
In this study, uppercase letters (e.g., Y) denote random matrix, with subscripts (e.g., Y ) indi-
i,j
cating matrix entries. An uppercase letter followed by parentheses (e.g., Y(n)) represents an
observation of the random matrix. A multi-variate time series can be represented as a sequence
[X(1),X(2),··· ,X(N)],whereX(n)∈R1×Disthesampleatthen-thtimestampwithDcovari-
ates.DefineinputsequenceL∈RH×DandlabelsequenceY ∈RT×DwhereHandTaresequence
lengths. Atanarbitraryn-thstep,thesesequencesareobservedasL=[X(n−H+1),...,X(n)]
and Y = [X(n+1),...,X(n+T)]. The goal of time series forecast is identifying a model
g : RH×D → RT×D within a model family G (e.g., decision trees, neural networks) that gener-
atesthepredictionsequenceYˆ =g(L)approximatingthelabelsequenceY.
Therearetwocriticalaspectstoaccommodateautocorrelationintimeseriesmodeling: (1)selecting
amodelfamilyG thatencodesautocorrelationininputsequences,whichunderscoresthedesignof
modelarchitectures;(2)generatingforecaststhatrespectlabelautocorrelation,whichhighlightsthe
efficacyofforecastparadigms. Oursurveyconcentratesonexaminingbothaspects.
2.2 MODELARCHITECTURES
Toexploitautocorrelationintheinputsequences,avarietyofarchitectureshavebeendeveloped(Qiu
etal.,2024;Lietal.,2024c). InitialstatisticalmethodsincludeVAR(Watson,1993)andARIMA(As-
teriou&Hall,2011). Subsequently,neuralnetworksgainedprominencefortheirabilitytoautomate
featureinteractionandcapturenonlinearcorrelations. ExemplarsincludeRNNs(e.g.,DeepAR(Sali-
nasetal.,2020),S4(Guetal.,2021)),CNNs(e.g.,TimesNet(Wuetal.,2023)),andGNNs(e.g.,
MTGNN(Mateosetal.,2019)),eachdesignedtoeffectivelyencodeautocorrelation.Currentprogress
hasreachedadebatebetweenTransformer-basedandMLP-basedarchitectures, eachwithitsad-
vantagesandlimitations. Transformers(e.g.,PatchTST(Nieetal.,2023),iTransformer(Liuetal.,
2024))offersignificantscalabilityasdatasizeincreasesbutincurhighcomputationalcosts;MLPs
(e.g.,DLinear(Zengetal.,2023),TimeMixer(Wangetal.,2024c))aregenerallymoreefficientbut
lesseffectiveinscalingwithlargerdatasetsandstruggletoaccommodatevaryinginputlengths.
Anemergingapproachisrepresentingsequenceinthefrequencydomain(Wuetal.,2021;2025).This
method,incomparisontomodelingautocorrelationinthetemporaldomain,managesautocorrelation
effectivelywithlimitedcost. AprominentexampleisFedFormer(Zhouetal.,2022),whichcomputes
attentionscoresinthefrequencydomain,leadingtoimprovedefficiency,efficacy,andnoisereduction
capabilities. ThesuccessofthistechniqueextendstovariousarchitectureslikeTransformers(Zhou
etal.,2022;Wuetal.,2021),MLPs(Yietal.,2023b)andGNNs(Yietal.,2023a;Caoetal.,2020),
whichmakesitaversatileplugininthedesignofneuralnetworksfortimeseriesforecast.
2

---

# Page 3

PublishedasaconferencepaperatICLR2025
2.3 ITERATIVEFORECASTV.S. DIRECTFORECAST
Therearetwoparadigmstogeneratemulti-stepforecast: iterativeforecast(IF)anddirectforecast
(DF)(Liuetal.,2022b).TheIFparadigmfollowsthecanonicalsequence-to-sequencemanner,which
forecastsonestepatatimeandusespreviouspredictionsasinputforsubsequentforecasts. This
recursiveapproachrespectslabelautocorrelationinforecastgeneration,widelyusedbyearly-stage
methods(Laietal.,2018;Salinasetal.,2020). However,IFsuffersfromhighvarianceduetoerror
propagation,whichsignificantlyimpairsperformanceinlong-termforecasts(Taieb&Atiya,2015).
Therefore,modernworks(Lietal.,2021)advocatetheDFparadigm,whichgeneratesmulti-step
forecastssimultaneouslyusingamulti-outputhead,featuredbyfastinference,implementationease
andsuperioraccuracy. Currently,DFhasbeenadominantparadigm,continuingtobeemployedin
modernworks(Wuetal.,2023;Liuetal.,2024).
Significance of this work. Our work refines the DF paradigm by performing forecasting in the
frequencydomain1. Incontrasttorecentadvancementsthatincorporatefrequencyanalysiswithin
modelarchitecturestomanageinputautocorrelation(Yietal.,2023a;b;Wangetal.,2025),accelerate
computation(Langeetal.,2021),andimprovegenerationquality(Yuan&Qiao,2024),ourapproach
specificallyfocusesonrefiningthelossfunctiontomitigatethebiascausedbylabelautocorrelation,
whichisanunexploredyetsignificantaspectinmoderntimeseriesanalytics.
3 PROPOSED METHOD
3.1 MOTIVATION
Autocorrelationisafundamentalcharacteristicoftimeseriesdata,whereeachobservationishighly
dependentonpreviousones(Zengetal.,2023). Thischaracteristicsetstimeseriesapartfromother
typesofdataandcreatesspecificmodelingchallenges. Toaccommodateautocorrelation,various
neuralnetworkarchitectureshavebeendeveloped(Wuetal.,2021;Liuetal.,2024),whicheffectively
modeltheautocorrelationininputsequence. However,labelautocorrelationcannotbehandledvia
themodificationofneuralarchitectures. Toeffectivelymanagelabelautocorrelation,itisnecessary
tocreatelearningobjectivesthatspecificallyconsiderthesedependencies.
Moderntimeseriesforecastingmodelsareprimarilytrainedunderthemultitasklearningmanner,
knownasthedirectforecasting(DF)paradigm. Specifically,theDFparadigmemploysamulti-output
modelg :RH×D →RT×D togenerateT-stepforecastsYˆ =g (L). Themodelparametersθare
θ θ
optimizedbyminimizingthetemporalloss:
L(tmp) := (cid:88) T (cid:13) (cid:13)Y −Yˆ (cid:13) (cid:13) 2 . (1)
(cid:13) t t(cid:13)
2
t=1
Inthislearningobjective,thetemporallossateachforecaststepiscomputedindependently,treating
eachfuturetimestepasaseparatetask. Whilethismethodhasshownempiricaleffectiveness,it
overlookstheautocorrelationpresentwithinthelabelsequenceY. Specifically,thelabelsequenceis
autoregressivelygenerated,withY beinghighlydependentonY ,asillustratedbythebluearrows
t+1 t
inFig.1(a). Incontrast,thelearningobjectivein(1)assumesthateachstepinthelabelsequencecan
beindependentlymodeled,asindicatedbytheblackarrowsinFig.1(a). Thismisalignmentbetween
themodel’sassumptionsandthedata’scharacteristicsintroducesbiasintothelearningobjectiveof
theDFparadigm,asdemonstratedinTheorem3.1.
Theorem3.1(BiasofDF). GiveninputsequenceLandlabelsequenceY,thelearningobjective(1)
oftheDFparadigmisbiasedagainstthepracticalnegative-log-likelihood(NLL),expressedas:
  2
T T i−1
Bias= (cid:88)
2σ
1
2
(Y
i
−Yˆ
i
)2− (cid:88)
2σ2(1
1
−ρ2)
Y
i
−Yˆ
i
+ (cid:88) ρ
ij
(Y
j
−Yˆ
j
) , (2)
i=1 i=1 i j=1
whereYˆ indicatesthepredictionatthei-thstep,ρ denotesthepartialcorrelationbetweenY and
i ij i
Y givenL,ρ2 = (cid:80)i−1ρ2 .
j i j=1 ij
1GiventheinferiorperformanceoftheIFparadigm(Lietal.,2021),thispaperadvocatesadaptingtheDF
paradigmtohandlelabelautocorrelation,ratherthanrevisitingIFtodirectlymodellabelautocorrelation.
3

---

# Page 4

PublishedasaconferencepaperatICLR2025
...
Correlation modeled by DF.
Label autocorrelation ignored by DF.
(a)
                             
     
  
      
      
  
       
           
       
(b)
                         
     
  
      
      
  
      
         
      
(c)
                         
     
  
      
      
  
      
         
      
(d)
Figure1:Visualizinglabelautocorrelationintimeseriesforecasting.(a)showsthegenerationprocess
of time series with dependencies depicted as arrows. (b) shows the label correlation in the time
domain,whereeachelementρ indicatesthepartialcorrelationbetweenY andY givenL. (c-d)
i,j i j
showsthelabelcorrelationinthefrequencydomain,whereeachelementρ indicatesthepartial
i,j
correlationbetweenF andF givenL,shownwiththereal(c)andimaginarypart(d). Duetothe
i j
symmetryinherentinFFT,theforecastlengthinthefrequencydomainishalved.
According to Theorem 3.1, the presence of label autocorrelation ρ causes the loss to be biased
ij
againsttheNLLoftherealdata.Notably,thisbiasdiminishestozerowhenthelabelsareuncorrelated
(ρ =0). Therefore,labelautocorrelationisacrucialaspectfortrainingtimeseriesforecastmodels.
ij
3.2 REDUCELABELAUTOCORRELATIONWITHFOURIERTRANSFORM
AsestablishedinTheorem3.1,thebiasinthelearningobjectivedecreasesaslabelautocorrelation
diminishes. Toachievethisreduction,apromisingstrategyistransformingthelabelsequenceintoa
representationwhereautocorrelationisminimized. TheDiscreteFourierTransform(DFT),defined
inDefinition3.2,offersanintuitiveapproach,whichprojectsthesequenceontoasetoforthogonal
exponentialbases. Inthistransformedspace,thelabelsequenceisdescribedasalinearcombination
ofpredefinedtemporalpatternsthatareorthogonal,whicheffectivelybypassestheautocorrelationin
thetimedomain. Theefficacyofthistransformationinreducinglabelautocorrelationisformalizedin
Theorem3.3,wheredifferentfrequencycomponentsbecomedecorrelated. Consequently,thereduced
ρ lowersthebiasagainsttheNLL,whichbenefitsthetrainingoftimeseriesforecastmodels.
i̸=j
Definition 3.2 (Discrete Fourier Transform, DFT). The normalized DFT of a sequence Y =
[Y ,...,Y ]isdefinedastheprojectionontoasetoforthogonalFourierbasesatdifferentfrequen-
0 T−1
cies. Theprojectionforfrequencykiscomputedas
T (cid:88) −1 (cid:18) 2πk (cid:19) √
F = Y exp −j( )t / T,
k t T
t=0
wherej istheimaginaryunit,exp(·)istheFourierbasisfordifferentkvalues. TheDFTcomprises
thesetofprojectionsF = [F ,...,F ],denotedasF = F(Y),whichcanbecomputedviathe
1 T−1
FastFourierTransform(FFT)algorithmwithcomplexityO(TlogT).
Theorem3.3(Decorrelationbetweenfrequencycomponents). LetY beazero-mean,discrete-time,
wide-sense stationary random process of length T. As T → ∞, the DFT coefficients become
asymptoticallyuncorrelatedatdifferentfrequencies:
(cid:26) S (f ), ifk =k′,
lim E[F F∗]= Y k
T→∞ k k′ 0, ifk ̸=k′,
wheref = k andS (f)isthepowerspectraldensityofY .
k T Y
Casestudy. Tovalidateourtheoreticalclaims,weconductedacasestudyontheWeatherdataset,
illustratedinFig.1.ImplementationdetailsandadditionalevidenceareprovidedinAppendixA.The
mainobservationsaresummarizedasfollows:
• EvidenceofLabelAutocorrelation: Fig.1(b)quantifiesthepartialcorrelationsbetweendifferent
stepsY andY ofthelabelsequenceY,conditionedontheinputL. Anumberofnon-diagonal
i j
4

---

# Page 5

PublishedasaconferencepaperatICLR2025
elementsexhibitsubstantialvalues,withapproximately37.5%exceeding0.3. Thisindicatesthat
differenttimestepsinY arecorrelatedconditionedonL,confirmingthepresenceoflabelautocor-
relation. Moreover,theautocorrelationdisplaysregularvariations,evidencedbyalternatinglight
anddarkregionsinFig.1(b),suggestingaperiodicnatureintheseries. Suchlabelautocorrelation
makesthelearningobjectiveofthenaiveDFparadigmbiased,asestablishedinTheorem3.1.
• EffectofDomainTransformation: Fig.1(c-d)visualizethepartialcorrelationsbetweendifferent
frequencycomponentsofthetransformedlabelsequenceF.Themajorityofnon-diagonalelements
shownegligiblevalues,withonlyabout3.6%exceeding0.1. Thisdemonstratesthattransforming
thelabelsequencetothefrequencydomainsignificantlyreducesthepartialcorrelationsbetween
differentcomponents,corroboratingTheorem3.3. Thereductioninlabelcorrelationρ leadsto
i̸=j
adecreaseinthebiasidentifiedinTheorem3.1,underscoringthepotentialofforecastinginthe
frequencydomainformoreaccurateandunbiasedpredictions.
3.3 MODELIMPLEMENTATION
Input 𝑔(⋅) ℱ(⋅)
𝐿∈ℝ$×# 𝑌'∈ℝ!×# 𝐹'∈ℂ!×#
ℒ("#$) ℒ(&'()
𝑌∈ℝ!×# 𝐹∈ℂ!×#
Label ℱ(⋅)
Imaginary part
trap
laeR
This section introduces FreDF, an innovative ap-
proach that enhances the vanilla Direct Forecast
(DF)trainingparadigm. FreDFalignsforecastand
label sequences within the frequency domain, ef-
fectively mitigating the bias introduced by label
autocorrelation.
Visualization of 𝓕(⋅) Calculation of 𝓛(𝐟𝐞𝐪)
As illustrated in Fig. 2, the input sequence L is ℒ(&'()
fed into the model to generate T-step forecasts, 𝐹
expressed as Yˆ = g(L). The temporal forecast 𝐹'
errorL(tmp) iscomputedaccordingto(1). Subse-
quently,boththeforecastandlabelsequencesare
transformedintothefrequencydomainusingFFT. Figure 2: The workflow of FreDF. Key oper-
Thefrequencyforecasterroristhencalculatedas: ationsinthetimeandfrequencydomainsare
(cid:12) (cid:12) highlightedinredandblue,respectively.
L(feq) :=(cid:12)F(Yˆ)−F(Y)(cid:12) , (3)
(cid:12) (cid:12)
1
whereY ∈RT×D,|·| denotestheelement-wiseℓ
1 1
norm,summingtheabsolutevaluesofallelementswithinthematrix. SinceFFTisdifferentiable(Wu
etal.,2021;Zhouetal.,2022),L(freq)canbeoptimizedusingstandardstochasticgradientdescent
methods. Weadvocatetheuseoftheℓ lossinthefrequencydomaininsteadofthesquaredlossdue
1
tothenumericalcharacteristicsofthetransformedlabelsequence. Specifically,differentfrequency
componentsoftenexhibitvastlyvaryingmagnitudes;lowerfrequenciespossesssignificantlyhigher
amplitudescomparedtohigherfrequencies,makingthesquaredlosspronetoinstability. Byusing
theℓ loss,weseekforamorebalancedandstableoptimizationprocess.
1
Finally,thetemporalandfrequencyforecasterrorsarefused,withtheweightingparameter0≤α≤1
controllingtherelativecontributionofeacherror:
Lα :=α·L(feq)+(1−α)·L(tmp). (4)
By aligning the forecast and label sequences in the frequency domain, FreDF mitigates the bias
causedbylabelautocorrelationwhilemaintainingtheadvantagesoftheDFT,includingefficient
inferenceandmulti-tasklearningcapabilities. Additionally,FreDFismodel-agnostic,compatible
with various forecasting models g (e.g., Transformers and MLPs). This flexibility significantly
expandsthepotentialapplicationsofFreDFacrossdiversetimeseriesforecastingscenarios,where
differentforecastingmodelsmaydemonstratesuperiorperformance.
4 EXPERIMENTS
TodemonstratetheefficacyofFreDF,therearesixaspectsempiricallyinvestigated:
1. Performance: DoesFreDFwork? Section4.2comparesFreDFwithstate-of-the-artbaselines
using public datasets. The long-term forecasting task is investigated in Section 4.2 and the
short-termforecastingandimputationtasksareexploredinAppendixE.1.
5

---

# Page 6

PublishedasaconferencepaperatICLR2025
Table1: Long-termforecastingperformance.
FreDF iTransformer FreTS TimesNet MICN TiDE DLinear FEDformer Autoformer Transformer TCN
Models (Ours) (2024) (2023) (2023) (2023) (2023) (2023) (2022) (2021) (2017) (2017)
Metrics MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
ETTm1 0.392 0.399 0.415 0.416 0.407 0.415 0.413 0.418 0.399 0.423 0.419 0.419 0.404 0.407 0.440 0.451 0.596 0.517 0.943 0.733 0.891 0.632
ETTm2 0.278 0.319 0.294 0.335 0.335 0.379 0.297 0.332 0.300 0.356 0.358 0.404 0.344 0.396 0.302 0.348 0.326 0.366 1.322 0.814 3.411 1.432
ETTh1 0.437 0.435 0.449 0.447 0.488 0.474 0.478 0.466 0.525 0.515 0.628 0.574 0.462 0.458 0.441 0.457 0.476 0.477 0.993 0.788 0.763 0.636
ETTh2 0.371 0.396 0.390 0.410 0.550 0.515 0.413 0.426 0.624 0.549 0.611 0.550 0.558 0.516 0.430 0.447 0.478 0.483 3.296 1.419 3.325 1.445
ECL 0.170 0.259 0.176 0.267 0.209 0.297 0.214 0.307 0.187 0.297 0.251 0.344 0.225 0.319 0.229 0.339 0.228 0.339 0.274 0.367 0.617 0.598
Traffic 0.421 0.279 0.428 0.286 0.552 0.348 0.535 0.309 0.636 0.335 0.760 0.473 0.673 0.419 0.611 0.379 0.637 0.399 0.680 0.376 1.001 0.652
Weather 0.254 0.274 0.281 0.302 0.255 0.299 0.262 0.288 0.261 0.319 0.271 0.320 0.265 0.317 0.311 0.361 0.349 0.391 0.632 0.552 0.584 0.572
PEMS03 0.113 0.219 0.116 0.226 0.146 0.257 0.118 0.223 0.099 0.214 0.316 0.370 0.233 0.344 0.174 0.302 0.501 0.513 0.126 0.233 0.666 0.634
PEMS08 0.141 0.238 0.159 0.258 0.174 0.277 0.154 0.245 0.717 0.459 0.319 0.378 0.294 0.377 0.232 0.322 0.630 0.572 0.249 0.266 0.713 0.629
Note:Wefixtheinputlengthas96followingtheestablishedbenchmark(Liuetal.,2024).Boldtypefacehighlightsthetopperformance
foreachmetric,whileunderlinedtextdenotesthesecond-bestresults.Theresultsareaveragedoverforecastlengths(96,192,336and
720),withfullresultsinTable5.
2. Mechanism: Howdoesitwork? Section4.3offersanablativestudytodissectthecontributions
ofFreDF’sindividualcomponents,elucidatingtheirrolesinenhancingforecastingaccuracy.
3. Generality: Doesitsupportotherforecastingmodels? Section4.4verifiestheadaptabilityof
FreDFacrossdifferentforecastingmodels,withadditionalresultsdocumentedinAppendixE.2.
4. Flexibility: DoesitsupportalternativetransformationstoFFT?Section4.4replacesFFTwith
othertransformationstoshowcaseitsflexibilityofimplementation.
5. Sensitivity: Doesitrequirecarefulfine-tuning? Section4.5presentsasensitivityanalysisofthe
hyperparameterα,whereFreDFmaintainsefficacyacrossabroadrangeofparametervalues.
6. Efficiency: IsFreDFeffectivegivenlimitedsamples? Section4.6offersalearningcurveanalysis,
where FreDF achieves comparable performance with limited samples to that obtained using
substantiallymoretime-domainlabels,indicatinganadvantageoussampleefficiency.
4.1 SETUP
Datasets. Thedatasetsforlong-termforecastandimputationincludeETT(4subsets),ECL,Traffic,
WeatherandPEMS(Liuetal.,2024). Thedatasetforshort-termforecastisM4followingWuetal.
(2023). Eachdatasetisdividedchronologicallyfortraining,validationandtest. Detaileddataset
descriptionsareprovidedinAppendixD.1.
Baselines. Our baselines include various established models, which can be grouped into three
categories: (1)Transformer-basedmethods: Transformer(Vaswanietal.,2017),Autoformer(Wu
etal.,2021),FEDformer(Zhouetal.,2022),iTransformer(Liuetal.,2024);(2)MLP-basedmethods:
DLinear (Zeng et al., 2023), TiDE (Das et al., 2023), FreTS (Yi et al., 2023b); (3) other notable
models: TimesNet(Wuetal.,2023),MICN(Wangetal.,2023b),TCN(Baietal.,2018).
Implementation. The baseline models are reproduced using the scripts provided by Liu et al.
(2024). TheyaretrainedusingtheAdam(Kingma&Ba,2015)optimizertominimizetheMSE
loss. Datasetsaresplitchronologicallyintotraining,validation,andtestsets. Followingtheprotocol
outlinedinthecomprehensivebenchmark(Qiuetal.,2024),thedropping-lasttrickisdisabledduring
thetestphase. WhenintegratingFreDFtoenhanceanestablishedmodel,weadheretotheassociated
hyperparametersettingsinthepublicbenchmark(Liuetal.,2024),onlytuningαandlearningrate
conservatively. ExperimentsareconductedonIntel(R)Xeon(R)Platinum8383CCPUsandNVIDIA
RTX3090GPUs. MoreimplementationdetailsareprovidedinAppendixD.2.
4.2 OVERALLPERFORMANCE
Theperformanceonthelong-termforecasttaskispresentedinTable1,whereweselectiTransformer
as the forecast model g and enhance it with FreDF. Overall, FreDF improves the performance
of iTransformer substantially. For instance, on the ETTm1 dataset, FreDF decreases the MSE
6

---

# Page 7

PublishedasaconferencepaperatICLR2025
iTransformer iTransformer & FreDF iTransformer iTransformer & FreDF
0.50 0.50 80 GroundTruth 80 GroundTruth
0.25 0.25 Prediction Prediction
60 60
0.00 0.00
40 40
−0.25 −0.25
−0.50 GroundTruth −0.50 GroundTruth 20 20
Prediction Prediction
−0.75 −0.75 0 0
0 100 200 300 400 0 100 200 300 400 0 4 8 12 16 20 24 0 4 8 12 16 20 24
(a) (b) (c) (d)
Figure3: VisualizationofforecastsequencegeneratedwithandwithoutFreDFinthetime(a-b)and
frequency(c-d)domains,usingtheiTransformerasthebackbonemodel.
Table2: Ablationstudyresults.
Model L(tmp) L(feq) Data T=96 T=192 T=336 T=720 Avg
MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
ETTm1 0.346 0.379 0.391 0.400 0.426 0.422 0.493 0.460 0.414 0.415
ETTh1 0.390 0.409 0.442 0.440 0.479 0.457 0.483 0.479 0.449 0.446
DF (cid:33) (cid:37) ECL 0.147 0.239 0.166 0.258 0.178 0.271 0.209 0.298 0.175 0.266
Weather 0.201 0.246 0.250 0.282 0.302 0.317 0.370 0.361 0.280 0.302
ETTm1 0.324 0.361 0.374 0.387 0.403 0.405 0.468 0.443 0.392 0.399
ETTh1 0.380 0.399 0.429 0.425 0.474 0.451 0.467 0.464 0.437 0.435
FreDF† (cid:37) (cid:33) ECL 0.144 0.232 0.158 0.247 0.171 0.262 0.204 0.291 0.169 0.258
Weather 0.165 0.205 0.225 0.255 0.278 0.295 0.359 0.349 0.257 0.276
ETTm1 0.324 0.362 0.372 0.385 0.402 0.404 0.468 0.443 0.391 0.398
ETTh1 0.381 0.400 0.430 0.426 0.474 0.451 0.463 0.461 0.437 0.435
FreDF (cid:33) (cid:33) ECL 0.144 0.233 0.158 0.247 0.172 0.263 0.204 0.293 0.169 0.259
Weather 0.163 0.202 0.220 0.252 0.274 0.293 0.356 0.346 0.253 0.273
ofiTransformerby0.019. Similargainsareevidentinotherdatasets, whichcanbeattributedto
reconciliationoflabelautocorrelationwiththeDFparadigm,validatingefficacyofFreDF.
Moreover, FreDF enhances the performance of iTransformer to surpass even those models that
originallyoutperformediTransformeronsomedatasets. ItindicatesthattheimprovementsbyFreDF
exceedthoseachievablethroughdedicatedarchitecturaldesignalone,emphasizingtheimportanceof
handlinglabelautocorrelationandFreDF.
Showcases. WevisualizetheforecastsequencestohighlighttheimprovementsofFreDFinforecast
quality.AnETTm2snapshotwithT=336isdepictedinFig.3.AlthoughthemodelwithoutFreDFcan
followthegeneraltrendsofthelabelsequence,itstrugglestocapturethesequence’shigh-frequency
components,resultinginaforecastwithavisiblylowerfrequency.Additionally,theforecastsequence
exhibitsnumerousburrs.Theseissuesreflectthelimitationsofforecastinginthetimedomain,namely
thedifficultyincapturinghigh-frequencycomponentsandtheneglectofautocorrelationbetween
sequentialsteps. FreDFaddressestheselimitationseffectively. TheforecastsgeneratedunderFreDF
notonlykeeppacewiththelabelsequence,accuratelycapturinghigh-frequencycomponents,but
alsoexhibitasmootherappearancewithfewerirregularities,duetoitsawarenessofautocorrelation.
Table3: VaryingFFTimplementationresults.
ETTh1 ETTm1 ECL
Model
MSE ∆ MAE ∆ MSE ∆ MAE ∆ MSE ∆ MAE ∆
iTransformer 0.449 - 0.447 - 0.415 - 0.416 - 0.176 - 0.267 -
+FreDF-T 0.437 ↓2.63% 0.435 ↓2.62% 0.392 ↓5.49% 0.399 ↓4.01% 0.170 ↓3.41% 0.259 ↓2.77%
+FreDF-D 0.445 ↓0.92% 0.440 ↓1.42% 0.395 ↓4.77% 0.398 ↓4.33% 0.171 ↓2.51% 0.260 ↓2.52%
+FreDF-2 0.432 ↓3.94% 0.431 ↓3.57% 0.392 ↓5.60% 0.399 ↓4.05% 0.166 ↓5.32% 0.256 ↓4.20%
Note:∆denotestherelativeerrorreductioncomparedtoiTransformerwithDFparadigm.
7

---

# Page 8

PublishedasaconferencepaperatICLR2025
2−2
2−3
iTrans. DLine. Auto. Trans.
ESM
with FreDF 2−1 w/o FreDF -5.2%
-3.0% -7.0% -3.4% 2−2
iTrans. DLine. Auto. Trans.
(a) ECLwithMSE
EAM
with FreDF w/o FreDF -4.0%
-3.7% -6.0% 2−1 -3.0%
2−2
iTrans. DLine. Auto. Trans.
(b) ECLwithMAE
ESM
with FreDF -32.8% w/o FreDF
-12.9% 2−1 -9.7% -0.9%
2−2
iTrans. DLine. Auto. Trans.
(c) WeatherwithMSE
EAM
with FreDF -27.2% w/o FreDF
-12.6% -9.5% -2.0%
(d) WeatherwithMAE
Figure4: BenefitofincorporatingFreDFinvaryingmodels,shownwithcoloredbarsformeansover
forecastlengths(96,192,336,720)anderrorbarsfor99.9%confidenceintervals.
4.3 ABLATIONSTUDIES
In this section, we dissect the contributions of the temporal and frequency loss for enhancing
forecastperformance. TheresultsaredetailedinTable2,whereiTransformerisusedastheforecast
model. Overall,thefrequencylossconsistentlyimprovesperformancecomparedtothetemporal
loss. Therationaleisthatlabelautocorrelationcanbeeffectivelymanagedinthefrequencydomain,
aligningbetterwiththeconditionalindependenceassumptioninherentinDF.Moreover,learningto
forecastinbothdomainsgenerallyshowcaseimprovementcomparedtorelyingsolelyononedomain.
However,theimprovementoverL(feq)ismarginal. Hence,exclusivelyfocusingonfrequencydomain
forecastingemergesasaviablestrategyinmostcases,offeringpromisingperformancewithoutthe
complexityofbalancinglearningobjectives.
4.4 GENERALIZATIONSTUDIES
In this section, we investigate the utility of FreDF with different forecast models and domain
transformationstrategies,toshowcasethegeneralityofFreDF.Inthebar-plots,theforecasterrorsare
averagedoverforecastlengths(96,192,336,720),witherrorbarsas95%confidenceintervals.
Varyingforecastmodels. WeexploretheversatilityofFreDFinaugmentingrepresentativeneural
forecasting models: iTransformer, DLinear, Autoformer, and Transformer. FreDF demonstrates
significantenhancementsacrossthesemodelscomparedtothetraditionalDFparadigm,asillustrated
inFig.4. Notably,Transformer-basedmodelssuchastheAutoformerandTransformersubstantially
benefitfromtheintegrationofFreDF.OntheECLdataset,forinstance,theAutoformer(developed
in2021)enhancedbyFreDFoutperformsDLinear(developedin2023). MoreevidenceofFreDF’s
versatilityisprovidedinAppendixE.TheseresultsconfirmFreDF’spotentialasaplugin-and-play
strategytoenhancevarioustimeseriesforecastingmodels.
VaryingFFTimplementations. Wenotethatlabelautocorrelationexistsbetweennotonlydifferent
steps,butalsovariablesinmultivariateforecasting. Therefore,weimplementFFTalongthetime
(FreDF-T) and variable dimension (FreDF-D) to handle the corresponding correlations, with the
outcomesillustratedinTable3. Ingeneral,conductingFFTalongthetimeandvariableaxisbrings
similarperformancegain,whichshowcasestheexistenceofcorrelationbetweendifferentstepsand
variables,respectively. Inparticular,FreDF-TslightlyoutperformsFreDF-D,whichunderscores
the relative importance of auto-correlation in the label sequence. Finally, a strategic approach is
viewingthemultivariatesequenceasanimage,performing2-dimensionalFFTonbothtimeand
variableaxes(FreDF-2),whichaccommodatesthecorrelationsbetweenbothtimestepsandvariables
simultaneouslyandfurtherimprovesperformance.
Varying transformations. Motivated by the fact that FFT can be viewed as projections onto
exponentialbases,weextendtheimplementationofFreDFbyreplacingFFTwithprojectionsonto
otherestablishedpolynomials.Eachpolynomialsetisadeptatcapturingspecificdatapatterns,suchas
trendsandperiodicity,whicharechallengingtolearninthetimedomain. Theresultsaresummarized
inFig.5. Notably,projectionsontoLegendreandFourierbasesdemonstratesuperiorperformance.
Thissuperiorityisattributedtotheorthogonalityofthepolynomials,afeaturenotguaranteedby
8

---

# Page 9

PublishedasaconferencepaperatICLR2025
0.46
0.44
0.42
0.40
0.38
0.2 0.4 0.6 0.8
α
ESM
0.46 Legendre Laguerre Chebyshev Fourier
0.44
0.42
0.40
0.38
0.2 0.4 0.6 0.8
α
(a) ETTh1withMSE
EAM
Legendre Laguerre 0.40 Chebyshev Fourier
0.38
0.36
0.34
0.32
0.2 0.4 0.6 0.8
α
(b) ETTh1withMAE
ESM
Legendre Laguerre Chebyshev Fourier 0.40
0.38
0.36
0.2 0.4 0.6 0.8
α
(c) ETTm1withMSE
EAM
Legendre Laguerre Chebyshev Fourier
(d) ETTm1withMAE
Figure5: Varyingprojectionbasesresults,shownwithcoloredbarsformeansoverforecastlengths
(96,192,336,720)anderrorbarsfor99.9%confidenceintervals.
0.17
0.16
0.00.10.20.30.40.50.60.70.80.91.0
α
ESM
192 336 0.27
0.26
0.25
0.00.10.20.30.40.50.60.70.80.91.0
α
(a) ECLwithMSE
EAM
192 336 0.42
0.40
0.38
0.00.10.20.30.40.50.60.70.80.91.0
α
(b) ECLwithMAE
ESM
192 336 0.42
0.41
0.40
0.39
0.00.10.20.30.40.50.60.70.80.91.0
α
(c) ETTm1withMSE
EAM
192 336
(d) ETTm1withMAE
Figure6: Varyingstrengthoffrequencyloss(α)results,shownwithcoloredlinesforT=192,336.
others as analyzed in Appendix C. It underscores orthogonality when selecting polynomials for
implementingFreDF,whichispivotalforeliminatingautocorrelation.
4.5 HYPERPARAMETERSENSITIVITY
ThekeyhyperparameterofFreDFisthefrequencylossstrengthα. Theperformancegivendifferent
αissummarizedinFig.6. Overall,increasingαfrom0to1resultsinareductionofforecasterror,
albeitwithaslightincreasetowardstheendofthisrange. Forinstance,ontheECLdatasetwith
T=192, both MAE and MSE decrease from approximately 0.258 and 0.167 to 0.247 and 0.158,
respectively. Suchtrendofdiminishingerrorseemsconsistentacrossdifferentforecastlengthsand
datasets,supportingthebenefitoflearningtoforecastinthefrequencydomain. Notably,theoptimal
reductioninforecasterrortypicallyoccursatαvaluesnear1,suchas0.8fortheETTh1dataset,
ratherthanattheabsolutevalueof1. Therefore,unifyingsupervisionsignalsfrombothtimeand
frequencydomainsbringsperformanceimprovement. Similartrendsarepresentedacrossdifferent
datasetsandforeacstmodels,asdiscussedinAppendixE.3.
4.6 LEARNING-CURVEANALYSIS
0.55
0.50
0.45
0.2 0.4 0.6 0.8 1.0
Data Percentage
ESM
(feq) (tmp) 0.50
0.48
0.46
0.44
0.2 0.4 0.6 0.8 1.0
Data Percentage
(a)
EAM
Inthissection,weinvestigatethesampleefficiency
(feq) (tmp)
oflearninginthetimeversusfrequencydomains,
with the corresponding learning curves in Fig. 7.
Overall,givenlimitedtrainingdata,learninginthe
frequencydomaindemonstratesremarkableefficacy.
Withonly30%ofthetrainingdata,itachievesper-
formancecomparabletolearninginthetimedomain
(b)
usingthefulltrainingdataset.
Theunderlyingreasonforthisenhancedsampleef- Figure7: LearningcurveonETTm1dataset.
ficiencycanbeattributedtotheconsistentandmore
straightforward nature of the data representation.
Forinstance,aslidingwindowonasinesignalyieldsasetofdistinctsequencesinthetimedomain.
However,inthefrequencydomain,thesesequencespresentasimilarpattern: aprominentspikeata
specificfrequencyandnegligiblevalueselsewhere. Thisuniformitysimplifiesthelearningprocessby
9

---

# Page 10

PublishedasaconferencepaperatICLR2025
makingpatternsmoreconsistentandeasiertodecipher,thusreducingtheneedforextensivetraining
datasets.
5 CONCLUSION
Inthisstudy,weunderscorethechallengeoflabelautocorrelationintimeseriesmodeling,which
biases the learning objective of the widely adopted DF paradigm. To tackle this challenge, we
introduce a model-agnostic learning objective: FreDF, which mitigates label autocorrelation by
transformingthelabelsequenceintothefrequencydomain,therebyeffectivelyreducingthebias
causedbylabelautocorrelation. TheexperimentsdemonstratethatFreDFeffectivelyenhancesthe
performanceofprevalentforecastmodels.
Limitation & future works. In this work, we primarily utilize the Fourier transform for domain
transformation. Despiteempiricalefficacy,thepredefinedsetofexponentialbaseslackstheability
toadapttospecificdataproperties. Alternativetransformssuchindependentcomponentanalysis
canproduceorthogonalbasesconsideringdataproperties,representingavaluableavenueforfuture
research. Additionally,theissueoflabelautocorrelationextendsbeyondtimeseries,affectingdiverse
contextsinvolvingstructurallabels,suchas3Dpointclouds,speech,andimages. Thepotentialof
FreDFtoenhanceperformanceinthesecontextsawaitsfurtherexploration.
ACKNOWLEDGEMENT
ThisworkwassupportedbyNationalNaturalScienceFoundationofChina(623B2002,12075212).
ThefirstauthorextendsheartfeltgratitudetoProf. DeguiYangofCentralSouthUniversity,forhis
exceptionalsignalprocessinglecturesandgenerousresearchguidanceduringS.T.E.M.studies.
REFERENCES
DimitrosAsteriouandStephenGHall. Arimamodelsandthebox–jenkinsmethodology. Appl.Econ.,
2(2):265–286,2011.
ShaojieBai,JZicoKolter,andVladlenKoltun. Anempiricalevaluationofgenericconvolutionaland
recurrentnetworksforsequencemodeling. arXivpreprintarXiv:1803.01271,2018.
KaifengBi,LingxiXie,HenghengZhang,XinChen,XiaotaoGu,andQiTian. Accuratemedium-
rangeglobalweatherforecastingwith3dneuralnetworks. Nature,619(7970):533–538,2023.
MichelaBia,MartinHuber,andLuka´sˇLaffe´rs. Doublemachinelearningforsampleselectionmodels.
J.Bus.Econ.Stat.,42(3):958–969,2024.
DefuCao,YujingWang,JuanyongDuan,CeZhang,XiaZhu,CongruiHuang,YunhaiTong,Bixiong
Xu,JingBai,JieTong,etal. Spectraltemporalgraphneuralnetworkformultivariatetime-series
forecasting. InProc.Adv.NeuralInf.Process.Syst.,volume33,pp.17766–17778,2020.
Victor Chernozhukov, Denis Chetverikov, Mert Demirer, Esther Duflo, Christian Hansen, Whit-
neyNewey,andJamesRobins. Double/debiasedmachinelearningfortreatmentandstructural
parameters: Double/debiasedmachinelearning. Econom.J.,21(1),2018.
AbhimanyuDas,WeihaoKong,AndrewLeach,RajatSen,andRoseYu. Long-termforecastingwith
tide: Time-seriesdenseencoder. arXivpreprintarXiv:2304.08424,2023.
AlbertGu,KaranGoel,andChristopherRe. Efficientlymodelinglongsequenceswithstructured
statespaces. InProc.Int.Conf.Learn.Represent.,2021.
DiederikP.KingmaandJimmyBa. Adam: Amethodforstochasticoptimization. InProc.Int.Conf.
Learn.Represent.,2015.
GuokunLai, Wei-ChengChang, YimingYang,andHanxiaoLiu. Modelinglong-andshort-term
temporalpatternswithdeepneuralnetworks. InSIGIR,2018.
10

---

# Page 11

PublishedasaconferencepaperatICLR2025
HenningLange,StevenLBrunton,andJNathanKutz. Fromfouriertokoopman: Spectralmethods
forlong-termtimeseriesprediction. J.Mach.Learn.Res.,22(41):1–38,2021.
VincentLeGuenandNicolasThome. Shapeandtimedistortionlossfortrainingdeeptimeseries
forecastingmodels. InProc.Adv.NeuralInf.Process.Syst.,volume32,2019.
VincentLeGuenandNicolasThome. Probabilistictimeseriesforecastingwithshapeandtemporal
diversity. InProc.Adv.NeuralInf.Process.Syst.,volume33,pp.4427–4440,2020.
Haoxuan Li, Kunhan Wu, Chunyuan Zheng, Yanghao Xiao, Hao Wang, Zhi Geng, Fuli Feng,
Xiangnan He, and Peng Wu. Removing hidden confounding in recommendation: a unified
multi-tasklearningapproach. Proc.Adv.NeuralInf.Process.Syst.,36:54614–54626,2024a.
HaoxuanLi,ChunyuanZheng,ShuyiWang,KunhanWu,EricWang,PengWu,ZhiGeng,XuChen,
andXiao-HuaZhou. Relaxingtheaccurateimputationassumptionindoublyrobustlearningfor
debiasedcollaborativefiltering. InProc.Int.Conf.Mach.Learn.,volume235,pp.29448–29460,
2024b.
JianxinLi,XiongHui,andWancaiZhang. Informer: Beyondefficienttransformerforlongsequence
time-seriesforecasting. InProc.AAAIConf.Artif.Intell.,2021.
Zhe Li, Xiangfei Qiu, Peng Chen, Yihang Wang, Hanyin Cheng, Yang Shu, Jilin Hu, Chenjuan
Guo,AoyingZhou,QingsongWen,etal. Foundts: Comprehensiveandunifiedbenchmarkingof
foundationmodelsfortimeseriesforecasting. arXivpreprintarXiv:2410.11802,2024c.
MinhaoLiu,AilingZeng,MuxiChen,ZhijianXu,QiuxiaLai,LingnaMa,andQiangXu. Scinet:
timeseriesmodelingandforecastingwithsampleconvolutionandinteraction. InProc.Adv.Neural
Inf.Process.Syst.,2022a.
ShiyuLiu,RohanGhosh,andMehulMotani. Towardsbetterlong-rangetimeseriesforecastingusing
generativeforecasting. CoRR,abs/2212.06142,2022b.
YongLiu,TenggeHu,HaoranZhang,HaixuWu,ShiyuWang,LintaoMa,andMingshengLong.
itransformer: Invertedtransformersareeffectivefortimeseriesforecasting. InProc.Int.Conf.
Learn.Represent.,2024.
GonzaloMateos,SantiagoSegarra,AntonioG.Marques,andAlejandroRibeiro. Connectingthe
dots: Identifyingnetworkstructureviagraphsignalprocessing. IEEESignalProcess.Mag.,36(3):
16–43,2019.
YuqiNie,NamHNguyen,PhanwadeeSinthong,andJayantKalagnanam. Atimeseriesisworth64
words: Long-termforecastingwithtransformers. InProc.Int.Conf.Learn.Represent.,2023.
XiangfeiQiu,JilinHu,LekuiZhou,XingjianWu,JunyangDu,BuangZhang,ChenjuanGuo,Aoying
Zhou,ChristianS.Jensen,ZhenliSheng,andBinYang. Tfb: Towardscomprehensiveandfair
benchmarkingoftimeseriesforecastingmethods. Proc.VLDBEndow.,17(9):2363–2377,2024.
XiangfeiQiu,XiuwenLi,RuiyangPang,ZhichengPan,XingjianWu,LiuYang,JilinHu,YangShu,
XuesongLu,ChengchengYang,ChenjuanGuo,AoyingZhou,ChristianS.Jensen,andBinYang.
Easytime: Timeseriesforecastingmadeeasy. InProc.IEEEInt.Conf.DataEng.,2025.
David Salinas, Valentin Flunkert, Jan Gasthaus, and Tim Januschowski. Deepar: Probabilistic
forecastingwithautoregressiverecurrentnetworks. Int.J.Forecast,36(3):1181–1191,2020.
AminShabani,AmirAbdi,LiliMeng,andTristanSylvain.Scaleformer:Iterativemulti-scalerefining
transformersfortimeseriesforecasting. InProc.Int.Conf.Learn.Represent.,2022.
SouhaibBenTaiebandAmirFAtiya. Abiasandvarianceanalysisformultistep-aheadtimeseries
forecasting. IEEETrans.Neural.Netw.Learn.Syst.,27(1):62–76,2015.
AshishVaswani,NoamShazeer,NikiParmar,JakobUszkoreit,LlionJones,AidanNGomez,Lukasz
Kaiser,andIlliaPolosukhin. Attentionisallyouneed. InProc.Adv.NeuralInf.Process.Syst.,
2017.
11

---

# Page 12

PublishedasaconferencepaperatICLR2025
HaoWang,ZhichaoChen,JiajunFan,HaoxuanLi,TianqiaoLiu,WeimingLiu,QuanyuDai,Yichao
Wang,ZhenhuaDong,andRuimingTang. Optimaltransportfortreatmenteffectestimation. In
Proc.Adv.NeuralInf.Process.Syst.,2023a.
HaoWang, ZhichaoChen, ZhaoranLiu, HaozheLi, DeguiYang, XinggaoLiu, andHaoxuanLi.
Entire space counterfactual learning for reliable content recommendations. IEEE Trans. Inf.
ForensicsSecurity,pp.1–12,2024a.
HaoWang, XinggaoLiu, ZhaoranLiu, HaozheLi, YilinLiao, YuxinHuang, andZhichaoChen.
Lspt-d: Local similaritypreservedtransport for directindustrial data imputation. IEEE Trans.
Autom.Sci.Eng.,2024b.
HaoWang,ZhengnanLi,HaoxuanLi,XuChen,MingmingGong,BinChen,andZhichaoChen.
Optimaltransportfortimeseriesimputation. InProc.Int.Conf.Learn.Represent.,pp.1–9,2025.
HuiqiangWang,JianPeng,FeihuHuang,JinceWang,JunhuiChen,andYifeiXiao. Micn: Multi-
scalelocalandglobalcontextmodelingforlong-termseriesforecasting. InProc.Int.Conf.Learn.
Represent.,2023b.
ShiyuWang,HaixuWu,XiaomingShi,TenggeHu,HuakunLuo,LintaoMa,JamesYZhang,and
JunZhou. Timemixer: Decomposablemultiscalemixingfortimeseriesforecasting. InProc.Int.
Conf.Learn.Represent.,2024c.
MarkW.Watson. Vectorautoregressionsandcointegration. WorkingPaperSeries,Macroeconomic
Issues,4,1993.
HaixuWu,JiehuiXu,JianminWang,andMingshengLong.Autoformer:Decompositiontransformers
withAuto-Correlationforlong-termseriesforecasting. InProc.Adv.NeuralInf.Process.Syst.,
2021.
Haixu Wu, Tengge Hu, Yong Liu, Hang Zhou, Jianmin Wang, and Mingsheng Long. Timesnet:
Temporal 2d-variation modeling for general time series analysis. In Proc. Int. Conf. Learn.
Represent.,2023.
XingjianWu,XiangfeiQiu,ZhengyuLi,YihangWang,JilinHu,ChenjuanGuo,HuiXiong,andBin
Yang. Catch: Channel-awaremultivariatetimeseriesanomalydetectionviafrequencypatching. In
Proc.Int.Conf.Learn.Represent.,2025.
FengYan,ChunjieYang,XinminZhang,ChongYang,andZhiyongRuan. Btpnet: Aprobabilistic
spatial-temporalawarenetworkforburn-throughpointmultisteppredictioninsinteringprocess.
IEEETrans.NeuralNetw.Learn.Syst.,2024.
Kun Yi, Qi Zhang, Wei Fan, Hui He, Liang Hu, Pengyang Wang, Ning An, Longbing Cao, and
ZhendongNiu. Fouriergnn: Rethinkingmultivariatetimeseriesforecastingfromapuregraph
perspective. InProc.Adv.NeuralInf.Process.Syst.,2023a.
KunYi,QiZhang,WeiFan,ShoujinWang,PengyangWang,HuiHe,NingAn,DefuLian,Longbing
Cao, and Zhendong Niu. Frequency-domain mlps are more effective learners in time series
forecasting. InProc.Adv.NeuralInf.Process.Syst.,2023b.
XinyuYuanandYanQiao. Diffusion-ts: Interpretablediffusionforgeneraltimeseriesgeneration. In
Proc.Int.Conf.Learn.Represent.,2024.
Ailing Zeng, Muxi Chen, Lei Zhang, and Qiang Xu. Are transformers effective for time series
forecasting? InProc.AAAIConf.Artif.Intell.,2023.
TianZhou,ZiqingMa,QingsongWen,XueWang,LiangSun,andRongJin. FEDformer: Frequency
enhanced decomposed transformer for long-term series forecasting. In Proc. Int. Conf. Mach.
Learn.,2022.
12

---

# Page 13

PublishedasaconferencepaperatICLR2025
A OVERVIEW OF DML FOR PARTIAL CORRELATION ESTIMATION
A.1 MOTIVATION
Inthissection,weintroducetherationaleforemployingdoublemachinelearning(DML)toquantify
thepartialcorrelations. OurfocusisontheautocorrelationrepresentedbyY →Y where0≤t<
t t′
t′ < T. However, theforkstructureY ← L(n) → Y createsapseudocorrelationbetweenY
t t′ t′
andY (Wangetal.,2024a). Inthiscase,theautocorrelationY →Y isinfluencedbythepseudo
t t t′
correlations from the fork structure, rendering traditional correlation measures, such as Pearson
correlation,ineffectiveforquantifyingtheautocorrelationY →Y (Lietal.,2024a;b).
t t′
Toeffectivelyaddressthisinfluenceandquantifypartialcorrelation,itisessentialtoemploymethods
that excel in distinguishing direct relationships from spurious ones (Wang et al., 2023a). DML
is chosen for calculating partial correlation due to its ease of implementation and independence
from exhaustive hyperparameter tuning. DML offers a robust and reliable quantification of the
autocorrelationthatwecareabout(Biaetal.,2024;Chernozhukovetal.,2018).
A.2 METHOD
Inthissection,wedetailtheimplementationofDML,atwo-stepproceduredesignedforestimating
partial correlation. We define T ∈ R as the treatment variable, Y ∈ R as the outcome variable,
X ∈ RD as the control variable that needs to be accounted for. The implementation of DML is
depictedinFig.8(b)whichconsistsoftwostepsbelow.
• Orthogonalization. Thisstepinvolvesorthogonalizingboththeoutcome(Y)andthetreatment
(T)withrespecttothecontrolvariables(X). Tothisend,wefirstusetwomachinelearningmodels,
namelyϕandψ,topredicttheoutcomeandthetreatmentbasedonX. Thesepredictionsaimto
capturethecomponentsinY andT thatareinfluencedbyX. Subsequently,suchimpactofX can
beeliminatedbycalculatingtheresiduals:
Y˜ =Y −ϕ(X),
(5)
T˜ =T −ψ(X).
• Regression. ThisstepinvolvesregressingtheorthogonalizedoutcomeY˜ontheorthogonalized
treatmentT˜. Alinearregressionmodelisutilizedforthispurpose:
Y˜ =βT˜ +ϵ, (6)
whereϵistheerrorterm;β isthemodelcoefficientthatcanbeidentifiedviaordinaryleastsquares.
Theβ canbeidentifiedinasupervisedlearningmanner,withtheobjectiveofminimizingtheMSE
betweenthepredictionandrealvalues. Theidentifiedβ quantifiesthepartialcorrelationbetween
thetreatmentandtheoutcome,havingaccountedfortheinfluenceofX.
Byregressingtheorthogonalizedoutcomeontheorthogonalizedtreatment,DMLcapturesthedirect
effectofthetreatmentontheoutcomewithouttheinterferencefromcontrolvariables,asdepicted
in Fig. 8 (c). That is, DML isolates the desired partial correlation T → Y from the influencing
correlationT ←X →Y.
A.3 EXPERIMENTALSETTINGS
Inthissection,weoutlinetheexperimentalsettingsimplementedtoemployDMLforquantifyingthe
correlationsofinterest.
Generalsettings. Forthebaselearnersϕandψ,weoptforalinearregressionmodeloptimized
usingordinaryleastsquaresforitsefficiency2. FollowingAppendixA.1,wetreattheinputsequence
L as the control variable to adjust, and simplify the process by considering the last step in L as
representative. Moreover,wefocusexclusivelyonthecorrelationswithinthelastfeatureofeach
2Thelinearregressionmodel,chosenforitscomputationalefficiency,iscrucialinmanagingtheexperiment’s
scale,wherethetotalnumberofDMLestimatorscanbeexceedinglyhigh(e.g.,36,864forT=192).
13

---

# Page 14

PublishedasaconferencepaperatICLR2025
Pseudo correlation from
confounder
PsePusdeou cdoor rceolarrteiolant iforonm from
concfoounnfoduenr der
(a) (b) (c)
Figure8: VisualizationofpartialcorrelationandDMLapproachforpartialcorrelationquantification.
(a)ThecorrelationgraphwherethepseudocorrelationiscausedbytheforkstructureT ←X →Y.
(b)TheimplementationofDML,whereβ istheidentifiedstrengthofthepartialcorrelationT →Y.
(c)ThepartialcorrelationidentifiedbyDML.
dataset3. ThisfocusmakesY ascalarvaluewithintherealnumberspaceratherthanaD-dimensional
vectorinthisexperiment.
Specificationsforidentifyingtime-domainpartialcorrelation. Toassessthepartialcorrelation
Y →Y ,wetreatY asthetreatmentandY astheoutcome. TheDMLmodelistrainedusinga
t t′ t t′
setofNobservations: {L(n)} ,{Y (n)} ,and{Y (n)} . Thecoefficientβ derived
n=1:N t n=1:N t′ n=1:N
fromtheDMLmodelisinterpretedasthestrengthofthepartialcorrelationY →Y .
t t′
Specifications for identifying frequency-domain partial correlation. To quantify the partial
correlation F → F , we treat F as the treatment and F as the outcome. The DML model
k k′ k k′
is trained using a set of N observations: {L(n)} , {F (n)} , and {F (n)} . The
n=1:N k n=1:N k′ n=1:N
coefficientβ derivedfromtheDMLmodelisinterpretedasthestrengthofthepartialcorrelation
F →F . AnotablecomplexityarisesbecauseF isacomplexnumber. SinceDMListypically
k k′ k
designedforrealnumbersinsteadofcomplexnumbers,itrequiresaseparateconsiderationofthe
realandimaginarypartsofF .
k
A.4 MOREEXPERIMENTALRESULTS
Inthissection,weprovidecomprehensiveresultsoftheidentifiedpartialcorrelationstrengths,which
quantifiestheautocorrelationeffectinthetimeandfrequencydomain. Fig.9presentstheresultson
threedifferentdatasets: Traffic,ETTh1,andECL,withforecastlengthsetto192. Fig.10presents
theresultsforvaryingforecastlengths: 48,96,192,336,ontheECLdataset.
Theresultsshowsimilarpatternstothoseinthemaintext. Specifically,thenon-diagonalelements
in Fig. 9 (a-c) and Fig. 10 (a-d) often exhibit huge values, which affirms the presence of label
autocorrelationinthetimedomain. Incontrast,thenon-diagonalelementsinFig.9(d-i)andFig.10
(e-l)shownegligiblevalues,whichsuggeststhatfrequencycomponentsofF arealmostindependent
given L. These findings collectively verify (1) the existence of label autocorrelation in the time
domain;(2)themitigationoflabelcorrelationinthefrequencydomain.
3Thisfocusisalignedwiththestudy’sobjectiveofanalyzingautocorrelationinsteadofinter-featurecorrela-
tions,whichsimplifiestheinterpretationofresults.
14

---

# Page 15

PublishedasaconferencepaperatICLR2025
                             
     
  
   
  
      
  
       
   
   
   
       
(a)
                             
     
  
   
  
      
  
       
   
   
   
       
(b)
                             
     
  
   
  
      
  
       
   
   
   
       
(c)
                         
     
  
   
  
  
   
  
      
  
   
  
      
(d)
                         
     
  
   
  
  
   
  
      
  
   
  
      
(e)
                         
     
  
   
  
  
   
  
      
  
   
  
      
(f)
                         
     
  
   
  
  
   
  
      
  
   
  
      
(g)
                         
     
  
   
  
  
   
  
      
  
   
  
      
(h)
                         
     
  
   
  
  
   
  
      
  
   
  
      
(i)
Figure 9: More comprehensive visualizations of label autocorrelation in different domains and
datasets,withcolumnsrepresentingdifferentdatasets: Traffic,ETTh1,andECL,fromlefttoright.
Panels(a-c)showthelabelcorrelationinthetimedomain,whereeachelementρ indicatesthe
i,j
partialcorrelationbetweenY andY givenL. Panels(d-i)showthelabelcorrelationinthefrequency
i j
domain,whereeachelementρ indicatesthepartialcorrelationbetweenF andF givenL,shown
i,j i j
withthereal(d-f)andimaginarypart(g-i). DuetothesymmetryinherentinFFT,theforecastlength
inthefrequencydomainishalved.
15

---

# Page 16

PublishedasaconferencepaperatICLR2025
 
 
  
  
  
  
     
                           
   
   
   
   
   
   
(a)
                         
     
  
      
      
  
      
         
      
(b)
                             
     
  
      
      
  
       
           
       
(c)
                               
     
  
      
       
   
       
           
       
(d)
                      
 
 
 
 
  
  
     
  
   
   
   
   
   
   
(e)
 
 
  
  
  
  
     
                           
   
   
   
   
   
   
(f)
                         
     
  
      
      
  
      
         
      
(g)
                             
     
  
      
      
  
       
           
       
(h)
                      
 
 
 
 
  
  
     
  
   
   
   
   
   
   
(i)
 
 
  
  
  
  
     
                           
   
   
   
   
   
   
(j)
                         
     
  
      
      
  
      
         
      
(k)
                             
     
  
      
      
  
       
           
       
(l)
Figure10: Morecomprehensivevisualizationsoflabelautocorrelationindifferentdomainsandlabel
lengths,withcolumnsrepresentinglabellengthsH=48,96,192,336fromlefttoright. Panels(a-d)
showthelabelcorrelationinthetimedomain,whereeachelementρ indicatesthepartialcorrelation
i,j
betweenY andY givenL. Panels(e-l)showthelabelcorrelationinthefrequencydomain,where
i j
eachelementρ indicatesthepartialcorrelationbetweenF andF givenL,shownwiththereal
i,j i j
(e-h)andimaginarypart(i-l).
16

---

# Page 17

PublishedasaconferencepaperatICLR2025
B THEORETICAL JUSTIFICATION
TheoremB.1(BiasofvanillaDF,simplified). GivenaninputsequenceLandaunivariatelabel
sequenceY =[Y ,Y ](theforecastlengthissetto2forsimplicity),thelearningobjective(1)ofthe
1 2
DFparadigmisbiasedagainstthepracticalNLL,expressedas:
1 1
Bias= (Y −Yˆ )2− (Y −(Yˆ +ρ(Y −Yˆ ))2, (7)
2σ2 2 2 2σ2(1−ρ2) 2 2 1 1
whereYˆ indicatesthepredictionatthei-thstepandρdenotesthepartialcorrelationbetweenY
i 1
andY givenL.
2
Proof. Aligning with the maximum likelihood analysis, we assume the label sequence obeys a
normaldistributionwithmeanµ=[Yˆ ,Yˆ ]andcovarianceζ =[[σ2,ρσ2],[ρσ2,σ2]]. Thenegative
1 2 2
log-likelihood(NLL)ofY giventheinputsequenceLcanbeexpressedas
−logp(Y|L)=−logp(Y |L)−logp(Y |L,Y )
1 2 1
1 (Y −Yˆ )2
=−log(√ exp(− 1 1 ))
2πσ 2σ2
1 (Y −(Yˆ +ρ(Y −Yˆ ))2
−log( exp(− 2 2 1 1 )).
(cid:112) 2π(1−ρ2)σ 2σ2(1−ρ2)
Removingcoefficientsunrelatedtog,thepracticalNLLthatcontributesthegradientstoupdategis
1 1
NLL:= (Y −Yˆ )2+ (Y −(Yˆ +ρ(Y −Yˆ ))2.
2σ2 1 1 2σ2(1−ρ2) 2 2 1 1
If the independence assumption of different time step holds (i.e., Y and Y are conditionally
1 2
independentgivenL),wehaveρ = 0,followedbyp(Y |L,Y ) = p(Y |L). Inthiscase,theMSE
2 1 2
lossincanonicalDFmirrorsthepracticalNLL:
1 1
MSE= (Y −Yˆ )2+ (Y −Yˆ )2,
2σ2 1 1 2σ2 2 2
whereσisoftensetto1whenimplementingMSE.Iftheindependenceassumptiondoesnothold,
i.e.,consideringautocorrelationinthelabelsequence,wehaveρ̸=0. Inthiscase,theMSElossin
thetimedomainisbiasedtothepracticalNLL,expressedas:
1 1
Bias= (Y −Yˆ )2− (Y −(Yˆ +ρ(Y −Yˆ ))2.
2σ2 2 2 2σ2(1−ρ2) 2 2 1 1
ThisbiasintroducedbylabelautocorrelationmakestheMSElossinthetimedomainfailtoreflect
thepracticalNLLandthereforemisleadstheupdateofforecastmodelgunderDFparadigm.
TheoremB.2(BiasofvanilliaDF). GivenaninputsequenceLandaunivariatelabelsequenceY,
thelearningobjective(1)oftheDFparadigmisbiasedagainstthepracticalNLL,expressedas:
  2
T T i−1
Bias= (cid:88)
2σ
1
2
(Y
i
−Yˆ
i
)2− (cid:88)
2σ2(1
1
−ρ2)
Y
i
−Yˆ
i
+ (cid:88) ρ
ij
(Y
j
−Yˆ
j
) , (8)
i=1 i=1 i j=1
whereYˆ indicatesthepredictionatthei-thstep,ρ denotesthepartialcorrelationbetweenY and
i ij i
Y givenL,ρ2 = (cid:80)i−1ρ2 .
j i j=1 ij
Proof. WeassumethatthelabelsequenceY conditionedontheinputsequenceLfollowsamultivari-
atenormaldistributionwithmeanvectorµ=[Yˆ ,Yˆ ,...,Yˆ ]andcovariancematrixΣ,wherethe
1 2 T
diagonalentriesΣ =σ2andtheoff-diagonalentriesareΣ =ρ σ2fori̸=j . Here,ρ denotes
ii ij ij ij
thepartialcorrelationbetweenY andY giventheinputsequenceL. Onthebasis,theNLLofthe
i j
17

---

# Page 18

PublishedasaconferencepaperatICLR2025
labelsequenceY givenLcanbedecomposedintoasumofconditionalNLLsduetotheproperties
ofthemultivariatenormaldistribution:
T
(cid:88)
−logp(Y |L)=− logp(Y |L,Y ,Y ,...,Y ),
i 1 2 i−1
i=1
where each conditional probability p(Y | L,Y ,...,Y ) is Gaussian with mean Yˆ +
i 1 i−1 i
(cid:80)i−1ρ (Y −Yˆ )andvarianceσ2(1−ρ2),ρ2 = (cid:80)i−1ρ2 . Thus,theNLLcanbeexpressedas
j=1 ij j j i i j=1 ij
   2 
T i−1
−logp(Y |L)= (cid:88) 
2
1 log(2πσ2(1−ρ2
i
))+
2σ2(1
1
−ρ2)
Y
i
−Yˆ
i
+ (cid:88) ρ
ij
(Y
j
−Yˆ
j
) 

.
i=1 i j=1
Forthepurposeofgradient-basedoptimization,termsindependentofthemodelpredictionsYˆ can
i
beomitted. Therefore,thepracticalNLLcontributingtothegradientsisgivenby
  2
T i−1
NLL= (cid:88)
2σ2(1
1
−ρ2)
Y
i
−Yˆ
i
+ (cid:88) ρ
ij
(Y
j
−Yˆ
j
) .
i=1 i j=1
Ontheotherhand,theDFparadigmtypicallyemploystheMSEloss,expressedas
T
MSE= (cid:88) 1 (Y −Yˆ)2.
2σ2 i i
i=1
whichdeviatesfromthepracticalNLL.Thebiasisexpressedas:
 2
T T i−1
Bias=MSE−NLL= (cid:88)
2σ
1
2
(Y
i
−Yˆ
i
)2− (cid:88)
2σ2(1
1
−ρ2)
Y
i
−Yˆ
i
+ (cid:88) ρ
ij
(Y
j
−Yˆ
j
) .
i=1 i=1 i j=1
Whenthereexistslabelautocorrelation,i.e.,ρ ̸=0,thebiasaboveexists. Inthespecialcasewhere
ij
thelabelautocorrelationisdiminished,i.e.,ρ →0,thebiasapproacheszeroalmostsurely.
ij
CorollaryB.3(BiasofvanillaDF,multivariate). GivenaninputsequenceLandamultivariatelabel
sequenceY ∈RT×D,supposeZ ∈RT×DistheflattenedversionofY obtainedbyconcatenating
therows,thelearningobjective(1)oftheDFparadigmisbiasedagainstthepracticalNLL:
  2
T×D T×D i−1
Bias= (cid:88)
2σ
1
2
(Z
i
−Zˆ
i
)2− (cid:88)
2σ2(1
1
−ρ2)
Z
i
−Zˆ
i
+ (cid:88) ρ
ij
(Z
j
−Zˆ
j
) , (9)
i=1 i=1 i j=1
whereZˆ indicatesthepredictionofZ ,ρ denotesthepartialcorrelationbetweenZ andZ given
i i ij i j
L,ρ2 = (cid:80)i−1ρ2 .
i j=1 ij
Proof. This corollary immediately follows from Theorem B.2, by viewing the multivariate label
sequenceZ asanaugmentedunivariatesequence.
TheoremB.4(Decorrelationbetweenfrequencycomponents). SupposeY isazero-mean,discrete-
time,wide-sensestationaryrandomprocessoflengthT.AsT→∞,thenormalizedDFTcoefficients
becomeasymptoticallyuncorrelatedatdifferentfrequencies:
(cid:26) S (f ), ifk =k′,
lim E[F F∗]= Y k
T→∞ k k′ 0, ifk ̸=k′,
wheref = k andS (f)isthepowerspectraldensityofY .
k T Y
18

---

# Page 19

PublishedasaconferencepaperatICLR2025
Proof. Recalling that the normalized DFT coefficients F are defined as F =
√ k k
1/ T (cid:80)T−1Y e−j2πkt/T, k = 0,1,...,T−1. On this basis, the expected value of the
t=0 t
productF F∗ canbeexpressedas:
k k′
(cid:34)T−1 T−1 (cid:35)
E[F F∗]=E (cid:88) Y e−j2πkt/T· (cid:88) Y ej2πk′t′/T /T
k k′ t t′
t=0 t′=0
(10)
T−1T−1
=
(cid:88) (cid:88)
R
[t−t′]e−j2πkt/Tej2πk′t′/T/T,
Y
t=0 t′=0
where we interchanged the order of summation and expectation, and utilize the autocorrelation
function R [τ] = E[Y Y ]. Denote τ = t − t′, which allows us to rewrite t′ = t − τ. This
Y t t′
substitutionleadsusto:
T−1t−T+1
E[F F∗]= (cid:88) (cid:88) R [τ]e−j2π(kt/T−k′(t−τ)/T)/T
k k′ Y
t=0 τ=t
 
T−1 min(T−1,T−1+τ)
=
(cid:88)
R Y
[τ]e−j2πk′τ/T

(cid:88) ej2π(k′−k)t/T/T.
τ=−(T−1) t=max(0,τ)
whichimmediatelyfollowsswitchingtheorderofsummation. Theexpressionwithintheparentheses
isasummationofcomplexexponentials. Whenk ̸=k′,theinnertermapproacheszeroduetothe
mutualcancellationoftheoscillatoryexponentials:
lim E[F F∗]=0.
k k′
T→∞
Whenk =k′,theexponentialtermbecomesunity,andtheinnersumsimplifiesto:
min(T−1,T−1+τ)
(cid:88)
lim 1/T= lim 1−|τ|/T=1.
T→∞ T→∞
t=max(0,τ)
whichimmediatelyfollowsbyE[F F∗] = S (f ),whereS isthepowerspectraldensityofY
k k′ Y k Y
thatcanbecalculatedastheDFTofR . Theproofisthereforecompleted.
Y
C GENERALIZED TRANSFORMATION ONTO DIFFERENT BASES
Transformingtimeseriesdataontopredefinedspacesisafundamentalaspectofsignalprocessing
anddataanalysis,withvariousstrategiesavailablebasedontheselectedbases,suchasFourierand
Chebyshevbases.Theselectionofbasesisdeterminedbythespecificcharacteristicsandrequirements
oftheanalysis. Below, wepresentformaldefinitionsofcommontransformtechniquesandtheir
associatedbases,whereweformulatesignalsascontinuousfunctionsfortheeaseofdemonstration.
Fouriertransform. Itemploysexponentialpolynominalsasbaseswhichprovetobemutually
orthogonal. Thesepolynomialsareeffectiveforanalyzingperiodicsignalsorsignalswithastrong
frequencycomponent. Letkbethefrequency,theassociatedbasisfunctionandprojectionontoitcan
beformulatedasfollows:
f (t)=exp(−j(2π/H)kt),
k
(cid:90) ∞ (11)
F = x(t)f (t)dt
k k
−∞
Legendre transform. It uses the Legendre polynomials as bases which prove to be mutually
orthogonalontheinterval[−1,1].Thesepolynomialsareparticularlyusefulforrepresentingfunctions
defined on a finite interval, which makes them suitable for certain types of data smoothing and
approximationtasks. Thek-thpolynomialandtheassociatedprojectioncanbeformulatedas:
1 dk
f (t)= [(t2−1)k],
k 2kk!dtk
(12)
(cid:90) 1
F = x(t)f (t)dt
k k
−1
19

---

# Page 20

PublishedasaconferencepaperatICLR2025
3.6 3.6
0.5 0.5
3.5 3.5
0.0 0.0
−0.5 GroundTruth −0.5 GroundTruth 3.4 GroundTruth 3.4 GroundTruth
Prediction Prediction Prediction Prediction
0 100 200 300 400 0 100 200 300 400 0 50 100 150 200 0 50 100 150 200
(a) DFandFreDF(Fourierbases). (b) DFandFreDF(Legendrebases).
Figure11: Thelabelsequences(blacklines)andforecastsequencesgeneratedbyDF(bluelines)and
FreDF(redlines). TheforecastmodelusedisiTransformer,withexperimentsconductedonselected
snapshotscharacterizedbyperiodicity(a)andtrend(b).
Chebyshevtransform. ItusestheChebyshevpolynomialsasbases. Thesebasesarenotorigi-
nallyorthogonalbutbecomemutuallyorthogonalontheinterval[−1,1]withrespecttotheweight
√
1/ 1−t2. Thesepolynomialsareparticularlyusefulforapproximatingfunctionswithrapidvaria-
tions. Thek-thChebyshevpolynomialandtheassociatedprojectioncanbeformulatedasfollows:
f (t)=cos(karccos(t)),
k
(cid:90) 1 x(t)f (t) (13)
F = √ k dt
k
1−t2
−1
Laguerretransform. ItusestheLaguerrepolynomialsasbases. ThesebasesareNOToriginally
orthogonalbutbecomemutuallyorthogonalontheinterval[0,∞]withrespecttotheexponential
weightexp(t). Thesepolynomialsareparticularlyusefulinquantummechanicsandotherfields
involvingexponentialdecay. Thek-thLaguerrepolynomialandtheassociatedprojectioncanbe
formulatedasfollows:
dk
f (t)=exp(t) (exp(−t)tk),
k dtk
(14)
(cid:90) ∞ x(t)f (t)
F = k dt
k exp(t)
0
Thesepolynomialsetsareeffectiveforcapturingspecificdatapatterns,suchastrendsandperiodicity,
whichcanbedifficulttolearninthetimedomain. Byincorporatingthesepolynomialsets,FreDF
enhances its flexibility to handle time series data with varying characteristics. A case study is
presentedinFig.11. Specifically,theforecastsequencesgeneratedbythecanonicalDFstruggleto
captureincreasingtrendsorhigh-frequencyperiods;whereasthoseproducedbyFreDFeffectively
capturethedominantcharacteristics,therebysignificantlyimprovingforecastquality.
Insummary,FreDFdoesnotrelysolelyonFourierbasesbutcanbeadaptedtovariousbases,each
withuniquepropertiessuitablefordifferentapplications. TheselectionofbasesforFreDFdepends
onthecharacteristicsofthedataandthespecificobjectivesoftheanalysis.
D REPRODUCTION DETAILS
D.1 DATASETDESCRIPTIONS
Thedatasetsutilizedinthisstudycoverawiderangeoftimeseriesdata,detailedinTable4,each
exhibitinguniquecharacteristicsandtemporalresolutions:
• ETT(Lietal.,2021)comprisesdataon7factorsrelatedtoelectricitytransformers,collectedfrom
July2016toJuly2018. Thisdatasetisdividedintofoursubsets: ETTh1andETTh2,withhourly
recordings,andETTm1andETTm2,documentedevery15minutes.
• Weather(Wuetal.,2021)includes21meteorologicalvariablesgatheredevery10minutesthrough-
out2020fromtheWeatherStationoftheMaxPlanckBiogeochemistryInstitute.
• ECL(ElectricityConsumptionLoad)(Wuetal.,2021)presentshourlyelectricityconsumption
datafor321clients.
20

---

# Page 21

PublishedasaconferencepaperatICLR2025
Table4: Datasetdescription.
Dataset D Forecastlength Train/validation/test Frequency Domain
ETTh1 7 96,192,336,720 8545/2881/2881 Hourly Health
ETTh2 7 96,192,336,720 8545/2881/2881 Hourly Health
ETTm1 7 96,192,336,720 34465/11521/11521 15min Health
ETTm2 7 96,192,336,720 34465/11521/11521 15min Health
Weather 21 96,192,336,720 36792/5271/10540 10min Weather
ECL 321 96,192,336,720 18317/2633/5261 Hourly Electricity
Traffic 862 96,192,336,720 12185/1757/3509 Hourly Transportation
PEMS03 358 12,24,36,48 15617/5135/5135 5min Transportation
PEMS08 170 12,24,36,48 10690/3548/265 5min Transportation
Note:Ddenotesthenumberofvariates.Frequencydenotesthesamplingintervaloftimepoints.Train,Validation,Testdenotesthenumber
ofsamplesemployedineachsplit.ThetaxonomyalignswithWuetal.(2023).
• Traffic(Wuetal.,2021)featureshourlyroadoccupancyratesfrom862sensorsintheSanFrancisco
Bayareafreeways,spanningfromJanuary2015toDecember2016.
• PEMS(Liuetal.,2022a)containsthepublictrafficnetworkdatainCaliforniacollectedby5-minute
windows. Twopublicsubsets(PEMS03,PEMS08)areadoptedinthiswork.
Thedatasetsarechronologicallydividedintotraining,validation,andtestsetsfollowingtheprotocols
outlinedin(Qiuetal.,2024;Liuetal.,2024). Thedropping-lasttrickisdisabledduringthetest
phase. Thelengthoftheinputsequenceisstandardizedat96acrosstheETT,Weather,ECL,and
Trafficdatasets,withvaryinglabelsequencelengthsof96,192,336,and720.
D.2 IMPLEMENTATIONDETAILS
ThebaselinemodelsinthisstudyarereproducedusingtrainingscriptsobtainedfromtheiTransformer
repository(Liuetal.,2024)afterreproducibilityverification. ModelsaretrainedusingtheAdam
optimizer(Kingma&Ba,2015),withlearningratesselectedfromtheset10−3,5×10−4,10−4to
minimizetheMSEloss. Thetrainingislimitedtoamaximumof10epochs,incorporatinganearly
stoppingmechanismactivateduponalackofimprovementinvalidationperformanceover3epochs.
InexperimentsintegratingFreDFtoenhanceanexistingforecastmodel,weadheretotheassociated
hyperparametersettingsfromthepublicbenchmark(Liuetal.,2024),tuningonlyαwithin[0,1]and
learningrateconservatively. Finetuningthelearningrateisessentialtohandlethedifferentmagnitude
oftemporalandfrequencylosses. Fine-tuningisconductedtominimizetheMSEaveragedacrossall
forecastlengthsonthevalidationdataset.
E MORE EXPERIMENTAL RESULTS
E.1 OVERALLPERFORMANCE
Long-termforecast. Weprovidecomprehensiveperformancecomparisononthelong-termforecast
taskinTable5. TheiTransformermodelisusedtooperationalizetheFreDFparadigm. Despitethe
iTransformer’sexistingperformancegapcomparedtootherbaselinemodels,theincorporationof
FreDFenhancesitsperformanceinthemajorityofcases,securingthelowestMSEin31outof45
casesandMAEin40outof45cases. ThefewinstanceswhereFreDFdoesnotachievethelowest
MSEareattributedtotheinherentsuperiorityofothermodelsoveriTransformerinspecificdatasets
(forexample,FreTSversusiTransformerontheWeatherdataset).
Short-termforecast. Weinvestigatetheshort-termforecasttaskinTable6,withFreTSYietal.
(2023b)servingastheforecastingmodelintheFreDFimplementation. Consistentwiththelong-term
forecastingresults,FreDFenhancesFreTS’sperformanceinmostinstances. Notably,therearethree
21

---

# Page 22

PublishedasaconferencepaperatICLR2025
Table5: Thecomprehensiveresultsonthelong-termforecastingtask.
FreDF iTransformer FreTS TimesNet MICN TiDE DLinear FEDformer Autoformer Transformer TCN
Models
(Ours) (2024) (2023) (2023) (2023) (2023) (2023) (2022) (2021) (2017) (2017)
Metrics MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
1mTTE
96 0.324 0.362 0.346 0.379 0.339 0.374 0.338 0.379 0.318 0.366 0.364 0.387 0.345 0.372 0.389 0.427 0.468 0.463 0.591 0.549 0.887 0.613
192 0.373 0.385 0.392 0.400 0.382 0.397 0.389 0.400 0.364 0.396 0.398 0.404 0.381 0.390 0.402 0.431 0.573 0.509 0.704 0.629 0.877 0.626
336 0.402 0.404 0.427 0.422 0.421 0.426 0.429 0.428 0.398 0.428 0.428 0.425 0.414 0.414 0.438 0.451 0.596 0.527 1.171 0.861 0.890 0.636
720 0.469 0.444 0.494 0.461 0.485 0.462 0.495 0.464 0.514 0.501 0.487 0.461 0.473 0.451 0.529 0.498 0.749 0.569 1.307 0.893 0.911 0.653
Avg 0.392 0.399 0.415 0.416 0.407 0.415 0.413 0.418 0.399 0.423 0.419 0.419 0.404 0.407 0.440 0.451 0.596 0.517 0.943 0.733 0.891 0.632
2mTTE
96 0.173 0.252 0.184 0.266 0.190 0.282 0.185 0.264 0.178 0.275 0.207 0.305 0.195 0.294 0.194 0.284 0.240 0.319 0.317 0.408 3.125 1.345
192 0.241 0.298 0.257 0.315 0.260 0.329 0.254 0.307 0.240 0.317 0.290 0.364 0.283 0.359 0.264 0.324 0.300 0.349 1.069 0.758 3.130 1.350
336 0.298 0.334 0.315 0.351 0.373 0.405 0.314 0.345 0.299 0.354 0.377 0.422 0.384 0.427 0.319 0.359 0.339 0.375 1.325 0.869 3.185 1.375
720 0.398 0.393 0.419 0.409 0.517 0.499 0.434 0.413 0.482 0.479 0.558 0.524 0.516 0.502 0.430 0.424 0.423 0.421 2.576 1.223 4.203 1.658
Avg 0.278 0.319 0.294 0.335 0.335 0.379 0.297 0.332 0.300 0.356 0.358 0.404 0.344 0.396 0.302 0.348 0.326 0.366 1.322 0.814 3.411 1.432
1hTTE
96 0.382 0.400 0.390 0.410 0.399 0.412 0.422 0.433 0.383 0.418 0.479 0.464 0.396 0.410 0.377 0.418 0.423 0.441 0.796 0.691 0.767 0.633
192 0.430 0.427 0.443 0.441 0.453 0.443 0.465 0.457 0.500 0.491 0.521 0.503 0.449 0.444 0.421 0.445 0.498 0.485 0.813 0.699 0.739 0.619
336 0.474 0.451 0.480 0.457 0.503 0.475 0.492 0.470 0.546 0.530 0.659 0.603 0.487 0.465 0.468 0.472 0.506 0.496 1.181 0.876 0.717 0.613
720 0.463 0.462 0.484 0.479 0.596 0.565 0.532 0.502 0.671 0.620 0.893 0.736 0.516 0.513 0.500 0.493 0.477 0.487 1.182 0.885 0.828 0.678
Avg 0.437 0.435 0.449 0.447 0.488 0.474 0.478 0.466 0.525 0.515 0.628 0.574 0.462 0.458 0.441 0.457 0.476 0.477 0.993 0.788 0.763 0.636
2hTTE
96 0.289 0.337 0.301 0.349 0.350 0.403 0.320 0.364 0.361 0.404 0.400 0.440 0.343 0.396 0.347 0.391 0.383 0.424 2.072 1.140 3.171 1.364
192 0.363 0.385 0.382 0.402 0.472 0.475 0.409 0.417 0.495 0.490 0.528 0.509 0.473 0.474 0.430 0.443 0.557 0.511 5.081 1.814 3.222 1.398
336 0.419 0.426 0.430 0.434 0.564 0.528 0.449 0.451 0.671 0.588 0.643 0.571 0.603 0.546 0.469 0.475 0.470 0.481 3.564 1.475 3.306 1.452
720 0.415 0.437 0.447 0.455 0.815 0.654 0.473 0.474 0.968 0.712 0.874 0.679 0.812 0.650 0.473 0.480 0.501 0.515 2.469 1.247 3.599 1.565
Avg 0.371 0.396 0.390 0.410 0.550 0.515 0.413 0.426 0.624 0.549 0.611 0.550 0.558 0.516 0.430 0.447 0.478 0.483 3.296 1.419 3.325 1.445
LCE
96 0.144 0.233 0.148 0.239 0.189 0.277 0.171 0.273 0.168 0.280 0.237 0.329 0.210 0.302 0.200 0.315 0.199 0.315 0.252 0.352 0.688 0.621
192 0.159 0.247 0.167 0.258 0.193 0.282 0.188 0.289 0.177 0.289 0.236 0.330 0.210 0.305 0.207 0.322 0.215 0.327 0.266 0.364 0.587 0.582
336 0.172 0.263 0.179 0.272 0.207 0.296 0.208 0.304 0.185 0.296 0.249 0.344 0.223 0.319 0.226 0.340 0.232 0.343 0.292 0.383 0.590 0.588
720 0.204 0.294 0.209 0.298 0.245 0.332 0.289 0.363 0.218 0.323 0.284 0.373 0.258 0.350 0.282 0.379 0.268 0.371 0.287 0.371 0.602 0.601
Avg 0.170 0.259 0.176 0.267 0.209 0.297 0.214 0.307 0.187 0.297 0.251 0.344 0.225 0.319 0.229 0.339 0.228 0.339 0.274 0.367 0.617 0.598
cfifarT
96 0.391 0.265 0.397 0.272 0.528 0.341 0.504 0.298 0.609 0.317 0.805 0.493 0.697 0.429 0.577 0.362 0.609 0.385 0.686 0.385 1.451 0.744
192 0.410 0.273 0.418 0.279 0.531 0.338 0.526 0.305 0.621 0.328 0.756 0.474 0.647 0.407 0.603 0.372 0.633 0.400 0.679 0.377 0.842 0.622
336 0.424 0.280 0.432 0.286 0.551 0.345 0.540 0.310 0.641 0.342 0.762 0.477 0.653 0.410 0.615 0.378 0.637 0.398 0.663 0.361 0.844 0.620
720 0.460 0.298 0.467 0.305 0.598 0.367 0.570 0.324 0.671 0.354 0.719 0.449 0.694 0.429 0.649 0.403 0.668 0.415 0.693 0.381 0.867 0.624
Avg 0.421 0.279 0.428 0.286 0.552 0.348 0.535 0.309 0.636 0.335 0.760 0.473 0.673 0.419 0.611 0.379 0.637 0.399 0.680 0.376 1.001 0.652
rehtaeW
96 0.164 0.202 0.201 0.247 0.184 0.239 0.178 0.226 0.182 0.250 0.202 0.261 0.197 0.259 0.221 0.304 0.284 0.355 0.332 0.383 0.610 0.568
192 0.220 0.253 0.250 0.283 0.223 0.275 0.227 0.266 0.234 0.301 0.242 0.298 0.236 0.294 0.275 0.345 0.313 0.371 0.634 0.539 0.541 0.552
336 0.275 0.294 0.302 0.317 0.272 0.316 0.283 0.305 0.268 0.325 0.287 0.335 0.282 0.332 0.338 0.379 0.359 0.393 0.656 0.579 0.565 0.569
720 0.356 0.347 0.370 0.362 0.340 0.363 0.359 0.355 0.361 0.399 0.351 0.386 0.347 0.384 0.408 0.418 0.440 0.446 0.908 0.706 0.622 0.601
Avg 0.254 0.274 0.281 0.302 0.255 0.299 0.262 0.288 0.261 0.319 0.271 0.320 0.265 0.317 0.311 0.361 0.349 0.391 0.632 0.552 0.584 0.572
30SMEP
12 0.068 0.172 0.069 0.175 0.083 0.194 0.082 0.188 0.087 0.203 0.117 0.225 0.122 0.245 0.123 0.248 0.239 0.365 0.107 0.209 0.632 0.606
24 0.096 0.205 0.098 0.210 0.127 0.241 0.110 0.216 0.086 0.198 0.233 0.320 0.202 0.320 0.160 0.287 0.492 0.506 0.121 0.227 0.655 0.626
36 0.128 0.240 0.131 0.243 0.169 0.281 0.133 0.236 0.105 0.220 0.380 0.422 0.275 0.382 0.191 0.321 0.399 0.459 0.133 0.243 0.678 0.644
48 0.161 0.269 0.164 0.275 0.204 0.311 0.146 0.251 0.120 0.235 0.536 0.511 0.335 0.429 0.223 0.350 0.875 0.723 0.144 0.253 0.699 0.659
Avg 0.113 0.219 0.116 0.226 0.146 0.257 0.118 0.223 0.099 0.214 0.316 0.370 0.233 0.344 0.174 0.302 0.501 0.513 0.126 0.233 0.666 0.634
80SMEP
12 0.080 0.182 0.085 0.189 0.095 0.204 0.110 0.209 2.193 0.871 0.121 0.231 0.152 0.274 0.175 0.275 0.446 0.483 0.213 0.236 0.680 0.607
24 0.118 0.220 0.131 0.236 0.150 0.259 0.142 0.239 0.235 0.339 0.232 0.326 0.245 0.350 0.211 0.305 0.488 0.509 0.238 0.256 0.701 0.622
36 0.161 0.258 0.182 0.282 0.202 0.305 0.167 0.258 0.197 0.300 0.379 0.428 0.344 0.417 0.250 0.338 0.532 0.513 0.263 0.277 0.727 0.637
48 0.206 0.293 0.236 0.323 0.250 0.341 0.195 0.274 0.242 0.324 0.543 0.527 0.437 0.469 0.293 0.371 1.052 0.781 0.283 0.295 0.746 0.648
Avg 0.141 0.238 0.159 0.258 0.174 0.277 0.154 0.245 0.717 0.459 0.319 0.378 0.294 0.377 0.232 0.322 0.630 0.572 0.249 0.266 0.713 0.629
1stCount 31 40 0 0 1 0 1 1 10 4 0 0 0 0 3 0 0 0 0 0 0 0
Note:Wefixtheinputlengthas96following(Liuetal.,2024).Boldtypefacehighlightsthetopperformanceforeachmetric,whileunderlined
textdenotesthesecond-bestresults.Avgindicatestheresultsaveragedoverforecastinglengths:T=96,192,336and720.
Table6: Thecomprehensiveresultsontheshort-termforecastingtask.
FreDF FreTS iTransformer MICN DLinear Fedformer Autoformer
Models
(Ours) (2023) (2024) (2023) (2023) (2023) (2023)
Metric SMAPEMASEOWASMAPEMASEOWASMAPEMASEOWASMAPEMASEOWASMAPEMASEOWASMAPEMASEOWASMAPEMASEOWA
Yearly 13.556 3.046 0.798 13.576 3.068 0.801 13.797 3.143 0.818 14.594 3.392 0.873 14.307 3.094 0.827 13.648 3.089 0.806 18.477 4.26 1.101
Quarterly 10.374 1.229 0.919 10.361 1.223 0.916 10.503 1.248 0.932 11.417 1.385 1.023 10.500 1.237 0.928 10.612 1.246 0.936 14.254 1.829 1.314
Monthly 12.999 0.983 0.913 13.088 0.99 0.919 13.227 1.013 0.935 13.834 1.080 0.987 13.362 1.007 0.937 14.181 1.105 1.011 18.421 1.616 1.398
Others 5.294 3.614 1.127 5.563 3.71 1.17 5.101 3.419 1.076 6.137 4.201 1.308 5.12 3.649 1.114 4.823 3.243 1.019 6.772 4.963 1.495
Avg. 12.112 1.648 0.877 12.169 1.66 0.883 12.298 1.68 0.893 13.044 1.841 0.962 12.48 1.674 0.898 12.734 1.702 0.914 16.851 2.443 1.26
1stCount 3 3 3 1 1 1 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0
Note:Boldtypefacehighlightsthetopperformanceforeachmetric,whileunderlinedtextdenotesthesecond-bestresults.Avgindicates
theresultsaveragedoverforecastinglengths:yearly,quarterly,andmonthly.
22

---

# Page 23

PublishedasaconferencepaperatICLR2025
Table7: Thecomprehensiveresultsonthemissingdataimputationtask.
FreDF iTransformer FreTS TimesNet MICN TiDE DLinear FEDformer Autoformer
Models
(Ours) (2024) (2023) (2023) (2023) (2023) (2023) (2022) (2021)
pmiss MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
1mTTE
0.1250.001530.027900.002130.033070.011020.078430.011520.072670.002360.033710.450520.455140.001480.023800.682620.381110.376540.35378
0.25 0.002870.038010.004020.044340.010890.077530.012450.079460.002840.036910.417770.458840.001540.023510.682350.381160.370590.35261
0.3750.002560.036690.004580.046630.011000.078120.014070.086730.003230.039000.629350.555700.001750.023850.681910.381050.378770.36093
0.5 0.001520.027390.003630.043590.011020.078180.016760.096100.003520.040280.293420.393200.001920.022190.681190.380850.380520.36462
Avg 0.002120.032500.003590.041910.010980.078070.013700.083740.002990.037470.447760.465720.001670.023340.682020.381040.376600.35798
2mTTE
0.1250.003630.038400.003980.040340.031940.133490.011890.067100.002190.033450.830230.621740.038220.129433.103881.313561.401600.80777
0.25 0.004370.042550.004310.043030.035910.136550.017950.089390.003310.041000.814020.611000.030630.115473.103641.313481.410330.81363
0.3750.003520.038230.003420.037930.032500.133360.027420.114990.004310.045981.112250.736330.017090.088223.103281.313301.408120.81049
0.5 0.001370.023820.001600.025380.031260.130270.040530.142850.005050.049180.994590.706650.010250.064403.105271.313891.446170.81796
Avg 0.003220.035750.003330.036670.032900.133420.024450.103580.003710.042400.937770.668930.024050.099383.104021.313561.416550.81246
1hTTE
0.1250.001780.030590.003190.041020.014000.081810.004410.044030.004320.046550.363630.453500.002790.036170.683070.380260.431360.41184
0.25 0.002180.034050.003340.042050.013470.080970.003200.038500.004540.047690.284350.405160.002360.033240.681620.379730.435150.41584
0.3750.001820.031080.002800.038520.013080.080170.002610.035400.004540.047300.210380.340290.002100.031210.681810.379750.444310.42505
0.5 0.001140.024140.001740.030080.012760.079180.002450.034720.004370.045940.133440.271020.001750.028440.681370.379920.443120.42387
Avg 0.001730.029960.002770.037920.013330.080530.003170.038170.004440.046870.247950.367490.002250.032260.681970.379920.438480.41915
2hTTE
0.1250.002220.031240.004730.046060.044850.138490.005350.044950.003340.042021.158590.738710.022870.108853.127561.317461.451300.84467
0.25 0.004070.042580.005710.050960.046470.135510.004940.044760.004570.049500.756430.597470.024910.115113.128911.317541.453860.84388
0.3750.003060.036930.004520.045190.048300.135830.005120.046970.005350.053630.594700.523710.019440.102773.127881.317281.454640.84194
0.5 0.001290.023650.002490.033040.049000.134690.006040.052240.005840.055470.357750.404970.014650.087463.128821.317331.459970.84644
Avg 0.002660.033600.004360.043810.047150.136130.005360.047230.004770.050160.716870.566220.020460.103553.128291.317401.454940.84423
LCE
0.1250.000290.012570.001870.031910.010180.082550.004660.045970.036780.140780.329420.422540.106580.238080.458840.410050.201470.29003
0.25 0.000610.018460.002160.034910.010220.082690.003410.039780.041060.148470.288310.400310.106820.236540.458870.410070.206180.29771
0.3750.000900.022420.002110.034730.010220.082580.002300.032960.043730.152240.253100.376260.105000.234150.458860.410060.209980.30337
0.5 0.001030.023930.001750.031770.010250.082840.001710.028560.045200.153800.212800.345260.103620.231270.458910.410110.213220.30764
Avg 0.000710.019350.001970.033330.010220.082660.003020.036820.041690.148820.270910.386090.105500.235010.458870.410070.207710.29969
rehtaeW
0.1250.000500.012590.000610.014460.006610.061230.003000.021100.003170.036460.369820.404860.005140.052750.405560.426310.135380.17599
0.25 0.000670.015130.000730.017150.006570.061050.002140.018300.003250.039000.292960.364830.004760.050190.405580.426350.136880.18177
0.3750.000540.014430.000670.017000.006580.061130.000880.009240.003260.039970.175690.289130.004540.048110.405500.426330.138310.18700
0.5 0.000310.011070.000470.014290.006500.060710.000420.004630.003090.039290.125780.245980.004920.049610.405510.426320.138500.19051
Avg 0.000510.013310.000620.015730.006560.061030.001610.013320.003200.038680.241060.326200.004840.050160.405540.426330.137270.18382
1stCount 23 19 1 1 0 0 0 2 2 2 0 0 4 6 0 0 0 0
Note:Theinputlengthissetto96forallbaselines.Boldtypefacehighlightsthetopperformanceforeachmetric,whileunderlinedtext
denotesthesecond-bestresults.Avgindicatestheresultsaveragedovermissingratios:0.125,0.25,0.375,0.5.
23

---

# Page 24

PublishedasaconferencepaperatICLR2025
iTransformer DLinear Autoformer
0.5 0.5 0.5
0.0 0.0 0.0
−0.5 GroundTruth −0.5 GroundTruth −0.5 GroundTruth
Prediction Prediction Prediction
−1.0
0 100 200 300 400 0 100 200 300 400 0 100 200 300 400
iTransformer & FreDF DLinear & FreDF Autoformer & FreDF
0.5 0.5 0.5
0.0 0.0 0.0
−0.5 GroundTruth −0.5 GroundTruth −0.5 GroundTruth
Prediction Prediction Prediction
0 100 200 300 400 0 100 200 300 400 0 100 200 300 400
(a) (b) (c)
Figure12: TheforecastsequencesgeneratedwithDFandFreDF.Theforecastlengthissetto336
andtheexperimentisconductedonasnapshotofETTm2.
caseswhereFreTSoutperformsFreDF.Thisoccursbecausethelossweightαistunedtominimize
thevalidationerroraveragedacrossallforecastlengthsinsteadoffocusingonspecificlengths. While
itisfeasibletofine-tuneαforeachforecastlength,wedidnotusethisapproach,asthecurrentresults
sufficetodemonstrateFreDF’seffectiveness.
Missing data imputation. We investigate the imputation task in Table 7, with iTransformer
serving as the forecasting model in the FreDF implementation. All models are trained using an
autoencodingapproach: giveninputsequenceswithmissingentries,theyaretaskedwithrecovering
the non-missing entries during training, while they are employed to impute the missing entries
duringinference. TheresultsdemonstrateFreDF’sefficacyinthistask,significantlyimprovingthe
performance of iTransformer and outperforming most competitive methods. A unique aspect of
thistaskistheirregularityofthelabelsequencescausedbythemissingentries,whichdisruptsthe
physicalsemanticsrelatedtotheFouriertransform. ThisindicatesthattheeffectivenessofFreDF
doesnotstemfromthesemanticcharacteristicsoftheFouriertransformitself,butratherfromits
abilitytoalignthepropertiesoftimeseriesdatawiththeimplicitassumptionsoftheDFparadigm,
specificallytheconditionalindependenceoflabels.
Showcases. WeprovideadditionalshowcasesillustratingthechangeofforecastsequencesinFig.12
and14. Overall,FreDFeffectivelymitigatesblursandcaptureshighfrequencycomponents. These
successescanbeattributedtoFreDF’suniquecapabilitytooperateinthefrequencydomain,where
thechallengesofautocorrelationaremitigated,andtheexpressionofhigh-frequencycomponents
becomesstraightforward.
E.2 GENERALIZATIONSTUDIES
Inthissection,wefurtherexploretheversatilityofFreDFinimprovingvariousforecastingmodels:
iTransformer,DLinear,Autoformer,andTransformer. Theresults,displayedinFig.16,encompass
fivedistinctdatasetsandareaveragedoverforecastlengths(96,192,336,720),witherrorbarsre-
flecting95%confidenceintervals. FreDFsignificantlyimprovestheperformanceoftheseforecasting
models,particularlybenefitingTransformer-basedarchitectureslikeAutoformerandTransformer.
TheseresultsaffirmFreDF’sutilityinenhancingneuralforecastingmodels,highlightingitspotential
asaversatiletrainingmethodologyintimeseriesforecasting.
24

---

# Page 25

PublishedasaconferencepaperatICLR2025
iTransformer DLinear Autoformer
125 125 125
GroundTruth GroundTruth GroundTruth
100 Prediction 100 Prediction 100 Prediction
75 75 75
50 50 50
25 25 25
0 0 0
0 4 8 12 16 20 24 0 4 8 12 16 20 24 0 4 8 12 16 20 24
iTransformer & FreDF DLinear & FreDF Autoformer & FreDF
125 125 125
GroundTruth GroundTruth GroundTruth
100 Prediction 100 Prediction 100 Prediction
75 75 75
50 50 50
25 25 25
0 0 0
0 4 8 12 16 20 24 0 4 8 12 16 20 24 0 4 8 12 16 20 24
(a) (b) (c)
Figure13: ThespectrumofforecastsequencesgeneratedwithDFandFreDF.Theforecastlengthis
setto336andtheexperimentisconductedonasnapshotofETTm2. Onlythefirst24frequenciesof
thespectrumarepresented.
iTransformer DLinear Autoformer
0.50 0.50 0.50
0.25 0.25 0.25
0.00 0.00 0.00
−0.25 −0.25 −0.25
−0.50 GroundTruth −0.50 GroundTruth −0.50 GroundTruth
Prediction Prediction Prediction
−0.75 −0.75 −0.75
0 100 200 300 400 0 100 200 300 400 0 100 200 300 400
iTransformer & FreDF DLinear & FreDF Autoformer & FreDF
0.50 0.50 0.50
0.25 0.25 0.25
0.00 0.00 0.00
−0.25 −0.25 −0.25
−0.50 GroundTruth −0.50 GroundTruth −0.50 GroundTruth
Prediction Prediction Prediction
−0.75 −0.75 −0.75
0 100 200 300 400 0 100 200 300 400 0 100 200 300 400
(a) (b) (c)
Figure14: TheforecastsequencesgeneratedwithDFandFreDF.Theforecastlengthissetto336
andtheexperimentisconductedonanothersnapshotofETTm2.
25

---

# Page 26

PublishedasaconferencepaperatICLR2025
iTransformer DLinear Autoformer
80 GroundTruth 80 GroundTruth 80 GroundTruth
Prediction Prediction Prediction
60 60 60
40 40 40
20 20 20
0 0 0
0 4 8 12 16 20 24 0 4 8 12 16 20 24 0 4 8 12 16 20 24
iTransformer & FreDF DLinear & FreDF Autoformer & FreDF
80 GroundTruth 80 GroundTruth 80 GroundTruth
Prediction Prediction Prediction
60 60 60
40 40 40
20 20 20
0 0 0
0 4 8 12 16 20 24 0 4 8 12 16 20 24 0 4 8 12 16 20 24
(a) (b) (c)
Figure15: ThespectrumofforecastsequencesgeneratedwithDFandFreDF.Theforecastlength
is set to 336 and the experiment is conducted on another snapshot of ETTm2. Only the first 24
frequenciesofthespectrumarepresented.
20
2−1
iTrans. DLine. Auto. Trans.
EAM
with FreDF
w/o FreDF 21
20
2−1
iTrans. DLine. Auto. Trans.
EAM
with FreDF 20
w/o FreDF
2−1
iTrans. DLine. Auto. Trans.
EAM
with FreDF
w/o FreDF 20
2−1
2−2
iTrans. DLine. Auto. Trans.
EAM
with FreDF
w/o FreDF
2−1
iTrans. DLine. Auto. Trans.
EAM
with FreDF
w/o FreDF
20
2−1
iTrans. DLine. Auto. Trans.
ESM
with FreDF 22
w/o FreDF
21
20
2−1
iTrans. DLine. Auto. Trans.
(a) ETTh1
ESM
with FreDF
w/o FreDF 20
2−1
iTrans. DLine. Auto. Trans.
(b) ETTh2
ESM
with FreDF 21
w/o FreDF
20
2−1
2−2
iTrans. DLine. Auto. Trans.
(c) ETTm1
ESM
with FreDF
w/o FreDF
2−1
iTrans. DLine. Auto. Trans.
(d) ETTm2
ESM
with FreDF
w/o FreDF
(e) Traffic
Figure16: PerformanceofdifferentforecastmodelswithandwithoutFreDF.Theforecasterrorsare
averagedoverforecastlengthsandtheerrorbarsrepresent95%confidenceintervals.
26

---

# Page 27

PublishedasaconferencepaperatICLR2025
Table8: ComparableresultswithDTW-basedloss.
Dataset ETTm1 ETTh1
Models FreDF Dilate DPP FreDF Dilate DPP
Metrics MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
96 0.324 0.362 0.498 0.443 0.631 0.495 0.382 0.400 0.790 0.567 0.815 0.577
192 0.373 0.385 0.993 0.625 0.975 0.617 0.430 0.427 0.950 0.643 0.916 0.633
336 0.402 0.404 0.946 0.628 0.945 0.626 0.474 0.451 0.978 0.663 0.986 0.660
720 0.469 0.444 0.999 0.652 1.079 0.678 0.463 0.462 0.922 0.654 0.898 0.649
Avg 0.392 0.399 0.859 0.587 0.907 0.604 0.437 0.435 0.910 0.632 0.904 0.630
E.3 HYPERPARAMETERSENSITIVITY
Inthissection,weexaminehowadjustingthefrequencylossweightαimpactstheperformanceof
FreDFacrossthreemodels: iTransformer,Autoformer,andDLinear,withtheresultsinFig.17,18,
and19. Wefindthatincreasingαfrom0to1generallyreducesforecasterroracrossvariousdatasets
andforecastlengths,highlightingthebenefitsofafrequencydomainlearningapproach. Notably,
theminimumforecasterroroftenoccursatαvaluescloseto1,ratherthanat1itself;forinstance,
0.8isoptimalfortheETTh1dataset. Thissuggeststhatintegratingsupervisorysignalsfromboth
timeandfrequencydomainsenhancesforecastingperformance. However,theimprovementmaybe
incrementalcomparedtosimplysettingα=1.
E.4 COMPARISONWITHDTW-BASEDLEARNINGOBJECTIVES
In this section, we compare FreDF with works that employ DTW as learning objectives to align
the shape of the forecast sequence with the label sequence: Dilate (Le Guen & Thome, 2019)
andDPP(LeGuen&Thome,2020). Notably, theseworksdonothandlethebiasintroducedby
labelautocorrelation,whichmakesthemindependenttothecontributionofFreDF.Tomakeafair
comparison,weintegratedtheofficialimplementationsofthelossfunctionsintotheiTransformer
model. As shown in Table 8, FreDF significantly outperforms DTW-based methods across both
datasets. ThisimprovementstemsfromFreDF’suniqueabilitytodebiasthelearningobjective,a
capabilitythatDilateandDPPdonotpossess.
27

---

# Page 28

PublishedasaconferencepaperatICLR2025
0.41
0.40
0.39
0.38
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.44
0.43
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.48
0.46
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.48
0.47
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
0.46
MAE MSE 0.45
0.44
0.43
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE
(a)
0.34
0.32
0.30
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.40
0.38
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.43
0.42
0.41
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE
0.44
0.42
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
0.42 MAE MSE
0.40
0.38
0.36
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE
(b)
0.38
0.36
0.34
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
0.40 MAE MSE
0.39
0.38
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE
0.42
0.41
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE
0.48
0.46
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.42
0.40
0.38
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE
(c)
0.25
0.20
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.300
0.275
0.250
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.34
0.32
0.30
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
0.42
MAE MSE
0.41
0.40
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.325
0.300
0.275
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE
(d)
0.20
0.15
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.25
0.20
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.25
0.20
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.30
0.25
0.20
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.25
0.20
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE
(e)
0.40
0.35
0.30
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.40
0.35
0.30
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.40
0.35
0.30
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.45
0.40
0.35
0.30
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.40
0.35
0.30
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE
(f)
0.250
0.225
0.200
0.175
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
0.28 MAE MSE
0.26
0.24
0.22
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE
0.30
0.28
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
0.37 MAE MSE
0.36
0.35
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.30
0.28
0.26
0.24
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE
(g)
Figure17: FreDFimprovesiTransformerperformancegivenawiderangeoffrequencylossweight
α. TheseexperimentsareconductedonETTh1(a),ETTh2(b),ETTm1(c),ETTm2(d),ECL(e),
Traffic(f)andWeather(g)datasets. Differentcolumnscorrespondtodifferentforecastlengths(from
lefttoright: 96,192,336,720,andtheiraveragewithshadedareasbeing50%confidenceintervals).
28

---

# Page 29

PublishedasaconferencepaperatICLR2025
0.44
0.43
0.42
0.41
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.50
0.48
0.46
0.44
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.50
0.48
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.54
0.52
0.50
0.48
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.48
0.47
0.46
0.45
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE
(a)
0.40
0.35
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.55 0.50
0.45
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.48 0.46
0.44
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.500 0.475
0.450
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.45
0.40
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE
(b)
0.46
0.44
0.42
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
0.65
MAE MSE 0.60
0.55
0.50
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.7
0.6
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.7
0.6
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.60
0.55
0.50
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE
(c)
0.30
0.25
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
0.350
MAE MSE 0.325
0.300
0.275
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.36
0.34
0.32
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.420
0.415
0.410
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
0.375
MAE MSE 0.350
0.325
0.300
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE
(d)
0.30
0.25
0.20
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.30
0.25
0.20
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.30
0.25
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.35
0.30
0.25
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.30
0.25
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE
(e)
0.7 0.6
0.5
0.4
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV 0.7 MAE MSE 0.6
0.5
0.4
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.6
0.5
0.4
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.6
0.5
0.4
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.6
0.5
0.4
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE
(f)
0.35
0.30
0.25
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.35
0.30
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.38
0.36
0.34
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.44
0.42
0.40
0.38
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
0.40 MAE MSE
0.35
0.30
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE
(g)
Figure18: FreDFimprovesAutoformerperformancegivenawiderangeoffrequencylossweight
α. TheseexperimentsareconductedonETTh1(a),ETTh2(b),ETTm1(c),ETTm2(d),ECL(e),
Traffic(f)andWeather(g)datasets. Differentcolumnscorrespondtodifferentforecastlengths(from
lefttoright: 96,192,336,720,andtheiraveragewithshadedareasbeing50%confidenceintervals).
29

---

# Page 30

PublishedasaconferencepaperatICLR2025
0.41
0.40
0.39
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.445
0.440
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.48
0.47
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.515
0.510
0.505
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
0.47
MAE MSE 0.46
0.45
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE
(a)
0.40 0.35
0.30
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV 0.475 MAE MSE 0.450 0.425
0.400
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV 0.60 MAE MSE 0.55
0.50
0.45
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.8 0.7
0.6
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.55 0.50
0.45
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE
(b)
0.37
0.36
0.35
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
0.3900 MAE MSE
0.3875
0.3850 0.3825
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE
0.414
0.412
0.410
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.47
0.46 0.45
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.41
0.40
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE
(c)
0.30
0.25
0.20
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.35
0.30
0.25
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.40
0.35
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.50
0.45
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.40
0.35
0.30
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE
(d)
0.30
0.25
0.20
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.30
0.25
0.20
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.30
0.25
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
0.35 MAE MSE
0.30
0.25
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE 0.30
0.25
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
MAE MSE
(e)
0.7
0.6
0.5
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.6
0.5
0.4
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.6
0.5
0.4
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV
0.7
MAE MSE 0.6
0.5
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.6
0.5
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE
(f)
0.26 0.24
0.22
0.20
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.28
0.26
0.24
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.32
0.30
0.28
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE 0.38
0.36
0.34
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV 0.325 MAE MSE 0.300
0.275
0.250
0.00.10.20.30.40.50.60.70.80.91.0
α
eulaV MAE MSE
(g)
Figure19: FreDFimprovesDLinearperformancegivenawiderangeoffrequencylossweightα.
TheseexperimentsareconductedonETTh1(a),ETTh2(b),ETTm1(c),ETTm2(d),ECL(e),Traffic
(f)andWeather(g)datasets. Differentcolumnscorrespondtodifferentforecastlengths(fromleftto
right: 96,192,336,720,andtheiraveragewithshadedareasbeing50%confidenceintervals).
30

---

# Page 31

PublishedasaconferencepaperatICLR2025
A CASE STUDY WITH PATCHTST AND VARYING INPUT LENGTH.
Inthissection,wefocusoniTransformer(Liuetal.,2024)andPatchTST(Nieetal.,2023),highlight-
ingtheeffectivenessofFreDFinenhancingtheirperformancegivenvaryinginputsequencelengths,
tocomplementthefixedlengthof96usedinthemaintext. AccordingtoTable1,FreDFconsistently
improvestheperformanceofbothiTransformerandPatchTSTacrossdifferentinputlengths. Notably,
under our experimental conditions, PatchTST with H = 336 achieves results comparable to the
original“PatchTST/42”resultsreportedby Nieetal.(2023),whileFreDFfurtherreducedtheMSE
andMAEby0.002,demonstratingitsrobustnessacrossdifferentinputlengths.
Table1: VaryinginputsequencelengthresultsontheWeatherdataset.
Models FreDF iTransformer FreDF PatchTST
Metrics MSE MAE MSE MAE MSE MAE MSE MAE
htgnelecneuqestupnI
96 0.164 0.202 0.201 0.247 0.174 0.217 0.200 0.244
192 0.220 0.253 0.250 0.283 0.230 0.266 0.234 0.268
96 336 0.275 0.294 0.302 0.317 0.279 0.301 0.311 0.321
720 0.356 0.347 0.370 0.362 0.355 0.351 0.365 0.353
Avg 0.254 0.274 0.281 0.302 0.259 0.284 0.278 0.297
96 0.164 0.207 0.184 0.235 0.158 0.205 0.167 0.213
192 0.211 0.250 0.236 0.277 0.200 0.241 0.204 0.244
192 336 0.262 0.290 0.268 0.296 0.259 0.287 0.266 0.291
720 0.341 0.343 0.342 0.345 0.330 0.334 0.333 0.337
Avg 0.244 0.272 0.258 0.288 0.237 0.267 0.242 0.271
96 0.159 0.204 0.164 0.215 0.150 0.200 0.153 0.203
192 0.204 0.248 0.211 0.256 0.193 0.240 0.194 0.240
336 336 0.253 0.288 0.260 0.292 0.245 0.280 0.247 0.282
720 0.325 0.336 0.327 0.339 0.320 0.332 0.321 0.336
Avg 0.235 0.269 0.241 0.276 0.227 0.263 0.229 0.265
96 0.164 0.215 0.172 0.228 0.144 0.194 0.191 0.246
192 0.209 0.257 0.218 0.265 0.190 0.242 0.192 0.241
720 336 0.251 0.291 0.273 0.306 0.243 0.283 0.241 0.285
720 0.318 0.342 0.340 0.353 0.310 0.330 0.311 0.331
Avg 0.236 0.276 0.251 0.288 0.222 0.262 0.234 0.276
B RUNNING COST ANALYSIS
In this section, we analyze the running cost of FreDF. The core computation of FreDF involves
calculatingtheFFTofbothpredictedandlabelsequences,followedbycalculatingtheirpoint-wise
MAEloss. TheoverallcomplexityisdominatedbytheFFToperation,whichoperatesatO(TlogT),
whereTisthelabelsequencelength.
0.078
0.076
0.074
0.072
0.070
0.068
96 192 336 720
Prediction length (T)
)sm(
emiT
0.92
0.90
0.88
0.86
0.84
0.82
0.80
0.78
96 192 336 720
Prediction length (T)
)sm(
emiT
Figure1: Runningtimeintheforwardpass(leftpanel)andbackwardpass(rightpanel),shownwith
dashedlinesfortheaverageandshadedareasfor99.9%confidenceintervals.
Fig.1showstheempiricalrunningcostsofFreDFforvaryingsequencelengthsinthetrainingduration,
involvingtheforwardpassstage(FFTcalculation)andthebackwardpassstage(frequencylossand
gradientcomputation). Overall,foralabelsequencewithT < 720,FreDFaddsapproximately1
31

---

# Page 32

PublishedasaconferencepaperatICLR2025
Table2: Experimentalresults(mean )withvaryingseeds(2020-2024).
±std
Dataset ETTh1 Weather
Models FreDF iTransformer FreDF iTransformer
Metrics MSE MAE MSE MAE MSE MAE MSE MAE
96 0.377±0.001 0.396±0.001 0.391±0.001 0.409±0.001 0.168±0.003 0.205±0.003 0.203±0.002 0.246±0.002
192 0.428±0.001 0.424±0.001 0.446±0.002 0.441±0.002 0.220±0.001 0.254±0.001 0.249±0.001 0.281±0.001
336 0.466±0.001 0.442±0.001 0.484±0.005 0.460±0.003 0.281±0.002 0.298±0.002 0.299±0.002 0.315±0.002
720 0.468±0.005 0.465±0.003 0.499±0.015 0.489±0.010 0.364±0.008 0.354±0.006 0.371±0.001 0.361±0.001
Avg 0.435±0.002 0.432±0.002 0.455±0.006 0.450±0.004 0.258±0.004 0.278±0.003 0.280±0.001 0.301±0.002
Table3: Impactofaligningtheamplitudeandphasecharacteristics.
ECL ETTm1 ETTh1
Amp. Pha.
MSE MAE MSE MAE MSE MAE
(cid:33) (cid:37) 0.3356 0.4060 0.5936 0.5169 0.7303 0.5968
(cid:37) (cid:33) 0.1836 0.2752 0.4204 0.4173 0.4751 0.4487
(cid:33) (cid:33) 0.1698 0.2594 0.3920 0.3989 0.4374 0.4351
mstotheoveralltrainingduration. Moreover,frequencylosscomputationisnotrequiredduring
inference. Therefore,FreDFdoesnothindermodelefficiencyineithertrainingorinferencestages.
C RANDOM SEED SENSITIVITY
Inthissection,weinvestigatethesensitivityoftheresultstothespecificationofrandomseeds. To
thisend,wereportthemeanandstandarddeviationoftheresultsobtainedfromexperimentsusing
fiverandomseeds(2020,2021,2022,2023,2024)inTable2. Weexamine(1)iTransformerand(2)
FreDF,whichisappliedtorefineiTransformer. Theresultsshowminimalsensitivitytorandomseeds,
withstandarddeviationsbelow0.005insevenoutofeightaveragedcases.
D AMPLITUDE V.S. PHASE ALIGNMENT
Inthissection,weinvestigatetheimplementationofthefrequencyloss(3),withtheresultsaveraged
overforecastlengthsinTable3. Specifically,minimizingthefrequencyloss(3)ensuresthatboth
amplitudeandphasecharacteristicsoftheforecastmatchthoseoftheactuallabelsequencesinthe
frequencydomain. Insignalprocessing,bothcharacteristicsarefundamentalforaccuratelyrepre-
sentingsignaldynamics,andweanalyzetheirrespectivecontributions. Overall,bothcharacteristics
areessentialforFreDF’sperformance. Notably,phasealignmentisparticularlycrucial;aligningam-
plitudecharacteristicswithoutalsoaligningphasecharacteristicsleadstosubparperformance. This
phenomenonisreasonable,asevenminordeviationsinphasecharacteristicscanproducesignificant
discrepanciesinthetimedomain.
Table4: Comparableresultswithbaselinesutilizingmultiresolutiontrends.
Dataset ETTm1 ETTh1
Models FreDF TimeMixer FreDF Scaleformer FreDF TimeMixer FreDF Scaleformer
Metrics MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
96 0.316 0.354 0.322 0.361 0.365 0.391 0.393 0.417 0.364 0.393 0.375 0.445 0.375 0.415 0.407 0.445
192 0.360 0.377 0.362 0.382 0.417 0.436 0.435 0.439 0.422 0.424 0.441 0.431 0.414 0.440 0.430 0.455
336 0.383 0.399 0.392 0.405 0.478 0.461 0.541 0.500 0.454 0.432 0.490 0.458 0.463 0.468 0.462 0.475
720 0.447 0.440 0.453 0.441 0.575 0.533 0.608 0.530 0.467 0.460 0.481 0.469 0.484 0.499 0.545 0.551
Avg 0.377 0.393 0.382 0.397 0.459 0.455 0.494 0.471 0.427 0.427 0.446 0.441 0.434 0.455 0.461 0.482
32

---

# Page 33

PublishedasaconferencepaperatICLR2025
E COMPARISON WITH ADDITIONAL FORECAST ARCHITECTURES
Inthissection,weapplyFreDFtotwoadditionalforecastarchitectures,namelyTimeMixer(Wang
etal.,2024c)andScaleFormer(Shabanietal.,2022)toshowcasethegeneralityofFreDF.Toensure
afaircomparison,weutilizedtheirofficialrepositories,downloadingandconfiguringthemaccording
totheirspecifiedrequirements. WemodifiedtheirtemporalMSElosswiththeproposedlossinthe
FreDF. The loss strength parameters were fine-tuned on the validation set. As shown in Table 4,
FreDFsignificantlyenhancestheperformanceofthesearchitectures,demonstratingFreDF’sability
to support and improve existing models. These improvements underscore the independent and
complementarynatureofFreDF’scontributions.
33