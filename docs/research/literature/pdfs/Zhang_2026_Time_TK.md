Time-TK: A Multi-Offset Temporal Interaction Framework
Combining Transformer and Kolmogorov-Arnold Networks for
Time Series Forecasting
FanZhang ShimingFan HuaWang∗
SchoolofComputerScienceand SchoolofComputerScienceand SchoolofComputerandArtificial
Technology,ShandongTechnology Technology,ShandongTechnology Intelligence,LudongUniversity
andBusinessUniversity andBusinessUniversity Yantai,ShanDong,China
Yantai,ShanDong,China Yantai,ShanDong,China hwa229@163.com
zhangfan@sdtbu.edu.cn 2024410061@sdtbu.edu.cn
Abstract CCSConcepts
Time series forecasting is crucial for the World Wide Web and •Appliedcomputing→Forecasting;•Computingmethodolo-
representsacoretechnicalchallengeinensuringthestableand gies→Informationextraction;•Informationsystems→Traffic
efficientoperationofmodernwebservices,suchasintelligenttrans- analysis.
portationandwebsitethroughput.However,wehavefoundthat
existingmethodstypicallyemployastrategyofembeddingeach Keywords
timestepasanindependenttoken.Thisparadigmintroducesafun- Kolmogorov-ArnoldNetworks,Webtimeseriesdata,Multi-Offset
damentalinformationbottleneckwhenprocessinglongsequences, embeddingmechanism
therootcauseofwhichisthatindependenttokenembeddingde-
ACMReferenceFormat:
stroysacrucialstructurewithinthesequence—whatwetermas
FanZhang,ShimingFan,andHuaWang.2026.Time-TK:AMulti-Offset
multi-offsettemporalcorrelation.Thisreferstothefine-grained
TemporalInteractionFrameworkCombiningTransformerandKolmogorov-
dependenciesembeddedwithinthesequencethatspanacrossdif-
ArnoldNetworksforTimeSeriesForecasting.InProceedingsoftheACMWeb
ferenttimesteps,whichisespeciallyprevalentinregularWebdata.
Conference2026(WWW’26),April13–17,2026,Dubai,UnitedArabEmirates.
Tofundamentallyaddressthisissue,weproposeanewperspective ACM,NewYork,NY,USA,12pages.https://doi.org/10.1145/3774904.3792618
ontimeseriesembedding.Weprovideanupperboundontheap-
proximatereconstructionperformanceoftokenembedding,which 1 Introduction
guidesourdesignofaconciseyeteffectiveMulti-OffsetTimeEm-
InthevastanddynamicecosystemoftheWorldWideWeb,Long-
bedding(MOTE)methodtomitigatetheperformancedegradation
TermTimeSeriesForecasting(LTSF)hasemergedasacrucialre-
causedbystandardtokenembedding.Furthermore,ourMOTEcan
searchfrontier[5,14,16,18,26,32].Webplatformsthemselves
beintegratedintovariousexistingmodelsandserveasauniver-
aregeneratorsofmassivetime-seriesdata[34,41],rangingfrom
salbuildingblock.Basedonthisparadigm,wefurtherdesigna
websitetrafficanduserengagementmetricstothecontinuousdata
novelforecastingarchitecturenamedTime-TK.Thisarchitecture
streamsproducedbyInternetofThings(IoT)devicesinteracting
first utilizes a Multi-Offset Interactive KAN (MI-KAN) to learn
viaAPIs.Unlikeinformation-densedatasuchasimagesortext,the
and represent specific temporal patterns among multiple offset
corevalueoftime-seriesdataliesinitstemporaldynamicsrather
sub-sequences.Subsequently,itemploysanefficientMulti-Offset
thaninisolated,individualtimepoints[9,31].Thisinformation
Temporal Interaction mechanism (MOTI) to effectively capture
sparsityatasingletimestepmakesitextremelychallengingto
thecomplexdependenciesbetweenthesesub-sequences,achiev-
extractmeaningfulpatternsfromthedata[1].Consequently,the
ingglobalinformationintegration.Extensiveexperimentson14
researchfocushasdefinitivelyshiftedtowardsmodelingcomplex
real-worldbenchmarkdatasets,coveringdomainssuchastraffic
temporal dynamics. This shift not only profoundly aligns with
flowandBTC/USDTthroughput,demonstratethatTime-TKsignif-
theintrinsiccharacteristicsofweb-generateddatabutalsoserves
icantlyoutperformsallbaselinemodels,achievingstate-of-the-art
asthefoundationforuncoveringkeyunderlyingstructures,such
forecastingaccuracy.
astheperiodicityofdailyuseractivityandlong-termplatform
growth(trends),therebyenablingproactiveresourceplanningand
intelligentwebservices.
∗Correspondingauthor. Recently,Transformer-basedmodelshavereceivedincreasingat-
tentioninthecontextoflong-termtimeseriesforecasting.However,
someworkhasshownthatTransformerexhibitssuboptimalperfor-
manceinlong-termmultivariatetimeseriesforecastingtasks[46].
ThisismainlyattributedtothefactthatmostexistingLTSFmeth-
ThisworkislicensedunderaCreativeCommonsAttribution4.0InternationalLicense. odsfocusonreducingcomputationalcostsinunivariatesettings
WWW’26,Dubai,UnitedArabEmirates andlacktargetedmodelingapproachesthataddresstheunique
©2026Copyrightheldbytheowner/author(s).
characteristicsoflong-termmultivariatetimeseries.Timeseries
ACMISBN979-8-4007-2307-0/2026/04
https://doi.org/10.1145/3774904.3792618 datatypicallyexhibitstrongperiodiccharacteristicsalongwith
6202
naJ
03
]GL.sc[
1v09111.2062:viXra

WWW’26,April13–17,2026,Dubai,UnitedArabEmirates FanZhang,ShimingFan,andHuaWang
0.174
0.276
0.205
0.237
0.332 0.389
0.4370.589
0.353 0.437 0 0 .6 .5 3 3 7 2 0 0 . . 4 6 2 3 2 1 0.431 0.372 1G 5G 10G
0.5990.252
0.222
0.399
0.152
0.145
0.425
M ( i a x ) ed SeqInupeuntc es Inv ( e b r ) ted SeqInupeuntc es 0.093
Embedding Embedding
F
T
E
i
D
m
f
e
o
s
r
N
m
e
e
t
r
SeSgemqeunetnactieon iTr
M
an
S
s
G
fo
N
rm
et
er SeSgemqeunetnactieon (a) (b)
… …
ESmeqbueedndcinesg ESmeqbueedndcinesg
Figure2:(a)Averageperformanceacrossallpredictionwin-
dows,showingimprovementsoverthebaselineonvarious
Em P b a ( e c t d c ) d h i ng SeqInupeuntc es M Em ul b t ( i e d - d o ) d ff in se g t SeqInupeuntc es datasets. (b) Comparison of memory usage (GB), training
PatchTST SeSgemqeunetnactieon Patch Size 3 Time-TK SeSgemqeunetnactieon Offset Size 3 time(ms/iter),andMSEontheTrafficdataset.Theprediction
TimeKAN (Ours) lengthwassetto96.
…
ESmeqbueedndcinesg ESmeqbueedndcinesg
Figure1:Illustrationoffourtimeseriesembeddingstrategies. encodestheoriginalsequencewiththeoffsetsub-sequences.This
(a)Mixedembeddingofvariablesatthesametimestep.(b) helpsrecovermissinginformationincross-offsetsegmentsand
Invertedembeddingalongthetimeaxis.(c)Patchembedding integratesitintoaunifiedglobalrepresentation,enhancingthe
basedontemporalsegmentation.(d)Multi-Offsetembedding model’sabilitytocapturelong-termglobalstructure.Asshownin
mechanismusedintheproposedTime-TK. Figure2,Time-TKachievesstate-of-the-artperformanceonseveral
long-termtimeseriesforecastingtasks.Italsoadoptsalightweight
architecture that outperforms more complex TSF models while
irregularfluctuations,asillustratedinFigure1.Therefore,theto- usingfewercomputationalresources.
kenembeddingapproachbasedonasingletimestep[38,49,50] Ourmaincontributionsareasfollows:
isdifficulttocapturethesekeyfeatureseffectively.Somestudies
• Wefindthatexistingembeddingmethodscannoteffectively
haveattemptedtoperformtokenembeddinginthetimedimension
capturethedependenciesbetweendifferenttimesteps.To
[11,36]toenhancethemodel’sunderstandingoftheperiodicstruc-
addressthisproblem,thispaperproposesamulti-offsettem-
ture.However,thesemethodstypicallyrelyonholisticsequence
poral token embedding method, which is one of the few
embeddings,whichmayoverlookfine-grainedtemporaldynamics
waystoexploredirectlyfromtheoriginalsequence.
essentialforaccurateforecasting[45].Inaddition,LTSFismore
• Time-TKisalightweightandefficientmodelthatincorpo-
pronetooverfittingthanshort-termpredictiontasks.Duringtrain-
ratestheMI-KANmodule.LeveragingtheflexibilityofKAN,
ing,themodelmayoverfittonoisypatternsinthedataandfailto
iteffectivelymodelsmulti-offsetsub-sequences.Moreover,
capturetheunderlyingtrendsandtruetemporaldependencies.
Time-TKisamongthefewtimeseriesforecastingmodels
Toaddresstheseissues,weproposeTime-TK,amulti-offsettem-
thatsuccessfullyintegrateTransformerandKAN.
poralinteractionframeworkthatintegratesTransformerandKAN.
• Weconductextensiveexperimentson14real-worlddatasets,
Itfocusesoncapturingdeeptemporaldependenciesfromhistorical
andtheresultsdemonstratethatTime-TKconsistentlyachie-
timeseriestoenhancethemodel’slong-termforecastingcapabil-
vesstate-of-the-artperformance,validatingitseffectiveness
ity.Giventhatlong-termtimeseriesforecastingreliesheavilyon
forlong-termtimeseriesforecasting.
modelingextensivehistoricalinformation,wedesignourapproach
aroundtheinherenttemporalstructureofthedata.Specifically,
2 RelatedWorks
weintroduceamulti-offsettemporaltokenembeddingmechanism,
asshowninFigure1,whichdividestheoriginaltimeseriesinto Withthebreakthroughsofdeeplearning[8,21,23,25,39,40,43,44]
multiplesub-sequenceswithdifferentspansatfixedoffsetsalong innaturallanguageprocessing[7,22]andcomputervision[47,48],
thetemporaldimensionandperformsindependentembeddingop- itsapplicationintimeseriesforecastinghasalsogrownrapidly.
erationsoneachsub-sequence.TheMulti-OffsetInteractiveKAN TraditionalmethodssuchasARIMA[2]areconstrainedbylin-
(MI-KAN)moduleleveragestheflexibilityofKAN[4,29]inkernel earassumptions,makingtheminadequateforcapturingnonlin-
functionmodelingtodeeplymodelthetemporalstructurewithin eardynamicsintemporaldata.Incontrast,deeplearningmodels
eachoffsetsub-sequenceandcaptureitsuniquedynamicpatterns. suchasRNNs[13,19],LSTMs[10],andTransformers[35]have
Basedontheseoffsetembeddingtokens,themulti-offsettemporal significantlyimprovedforecastingaccuracybylearningtimede-
interactionmodulecapturescross-stepdependenciesbetweentime pendencies.Embeddingstrategiesplayacrucialroleintimeseries
stepsandcompensatesforlong-terminterleaveddynamicsthatare modeling,astheytransformlow-dimensionalrawinputsintohigh-
oftenoverlookedbytraditionalcontinuousembeddingmethods. dimensionalrepresentations,helpingmodelstocaptureunderlying
Toachieveamorecomprehensiveunderstandingofthetimese- temporalstructuresandsemanticpatterns.Inthissection,wesum-
ries,wefurtherdesignaglobalinteractionmechanismthatjointly marizethemainstreamembeddingapproachesfortimeseries.As

Time-TK:AMulti-OffsetTemporalInteractionFrameworkforTimeSeriesForecasting WWW’26,April13–17,2026,Dubai,UnitedArabEmirates
… Time-TK
(I) MOTE (III) MOTI
…
0 1 2 3 𝓛
Input:History ℒ timesteps
Multi-Offset Embedding
Linear Linear Linear
Linear Linear Linear
Linear Linear Linear
Nor
In
m
s
a
ta
li
n
z
c
a
e
tion
𝓜𝟏 𝓜𝟐 𝓜𝓞 Q K V
Multi-Head Attention
Multi-Head Attention
Multi-Head Attention
…
… … …
Time-TK Block
0 1 2 3 … T 0 1 2 3 … T 0 1 2 3 … T Multi-Offset Ori O gi r n i a g l i nal
Token Token
Token
FFN (II) MI-KAN
𝓜𝟏 … 𝓜𝟐 … … 𝓜𝒏 … Q K V
Inverse Instance 𝜙11:𝑁,1𝜙11:𝑁,2𝜙11:𝑁,3 …𝜙11:𝑁,𝑁 𝜙11:𝑁,1𝜙11:𝑁,2𝜙11:𝑁,3 …𝜙11:𝑁,𝑁 𝜙11:𝑁,1𝜙11:𝑁,2𝜙11:𝑁,3 …𝜙11:𝑁,𝑁 Global Interaction
Normalization … … … Mechanism
… Radial Basis Function … … Radial Basis Function … … Radial Basis Function …
… … …
𝜙1𝑛:𝑁,1𝜙1𝑛:𝑁,2𝜙1𝑛:𝑁,3 … 𝜙1𝑛:𝑁,𝑁 𝜙1𝑛:𝑁,1𝜙1𝑛:𝑁,2𝜙1𝑛:𝑁,3 … 𝜙1𝑛:𝑁,𝑁 𝜙1𝑛:𝑁,1𝜙1𝑛:𝑁,2𝜙1𝑛:𝑁,3 … 𝜙1𝑛:𝑁,𝑁 Multi-Layer Perceptron
… 𝓜𝟏′ … 𝓜𝟐′ … … 𝓜𝒏′ …
𝓛 𝓛+𝟏 𝓛+𝟐 𝓛+𝟑 … 𝓛+ℱ
Output:Future ℱ timesteps
Figure3:OverallarchitectureofTime-TK.MOTEperformsMulti-Offsettokenembeddingonthesequence,followedbyMI-KAN
learningrepresentationofthesubsequences,andfinallyinteractivepredictionthroughMOTI.
showninFigure1,thesemethodscangenerallybedividedinto AsshowninFigure3,ourproposedTime-TKarchitectureconsists
threecategories:Thefirstcategory[37,38,49,51]employschannel- ofmultiplestages.First,Multi-OffsetTokenEmbeddingdivides
mixingmechanisms,inwhicheachtimestepisrepresentedbythe theoriginalsequenceintomultiplesub-sequenceswithdifferent
integrationofcross-channellatentfeatures.However,MLP-based timespans.MI-KAN(Multi-OffsetInteractiveKAN)learnsandrep-
models[46]haveraisedthequestion:“AreTransformerseffective resentsspecifictemporalpatternsbetweenoffsetsub-sequences.
fortimeseriesforecasting?”Withtheiroutstandingperformance TheMulti-OffsetTemporalInteractivemodulecaptureslongdis-
andefficiency,theyposeasignificantchallengetotheeffective- tancedependenciesacrosstimestepsbasedontherepresentation
nessofsuchTransformer-basedmethods.Thesecondcategory[30] oftheseoffsetsub-sequences.Atahigherlevel,theglobalinter-
adoptspatch-basedembeddingsbysegmentingthesequenceinto actionmechanismfurtherfusesthecontextualinformationofthe
localwindowstopreservesegment-levelsemantics,therebycaptur- originalsequencewiththatofalloffsetsub-sequencestocapture
ingbroadertemporalpatternsthatareoftenmissedbypointwise themissinginformationacrossoffsetsegmentsandunifyitintothe
models.Thethirdcategory[28]introducesaninvertedembedding globalrepresentation.Thefinalpredictionisobtainedbymapping
mechanism, where complete sub-sequences along the temporal thelearnedrepresentationthroughalinearprojectionlayer.The
axisareembeddedintosingletokens,allowingeachtokentoag- coremodulesofTime-TKareintroducedindetailbelow,whilethe
gregateglobalsequencerepresentations.Thisdesignalignswell completealgorithmicworkflowisprovidedinAppendixC.The
withattention-basedarchitecturesandhasreceivedconsiderable codeisavailablefromtherepository1.
attention.
Unliketheaforementionedstrategies,weexploreanovelembed- 3.2 Multi-OffsetTokenEmbedding
dingmechanismaimedatenhancingthemodel’sabilitytolearn
Threemainformsofexistingembeddingmethodsexist:(i)uses
specifictemporalpatterns.Ourmethoddemonstratesconsistently
embeddingbasedonasingletimestepalsocalledchannelmixing
effective performance across a variety of experimental settings,
(CM),(ii)takestheentiretimedimensionastheembeddinginput.
validatingitsapplicabilitytotimeseriesforecastingtasks.
(iii)segmentsthetimedimensionforembedding.However,theseap-
proachesoftenstruggletoadequatelycapturedependenciesacross
3 Methodology differenttimescales,especiallyinperiodicandnon-stationarytime
series,leadingtolimitedinteractioncapabilities.Toaddressthis
3.1 OverviewofTime-TK
limitation,weproposeaMulti-OffsetTokenEmbeddingstrategy.
GivenahistoricaltimeseriesX = [𝑥
1
,...,𝑥
L
] ∈ R𝑁×L,theob- Specifically,givenapredefinedoffsetsizeO,wedividethehistori-
jectiveoftimeseriesforecastingistopredictfuturevaluesYˆ 𝑡 = calsequenceintomultiplesub-sequences{M 1 ,...,𝑀 O }.Asshown
[𝑥
L+1
,...,𝑥
L+F
] ∈R𝑁×F,where𝑁 isthenumberofvariables,L
isthelengthoftheinputsequence,andF istheforecasthorizon. 1https://github.com/fsmss/Time-TK

WWW’26,April13–17,2026,Dubai,UnitedArabEmirates FanZhang,ShimingFan,andHuaWang
inFigure1,unliketraditionalapproaches,weusemultiplesub- structurebutalsoenhancesrepresentationconsistencyacrossdif-
sequenceswithdifferenttemporaloffsetsastokeninputstocapture ferentsub-sequencesthroughaunifiedmodelingapproach,thereby
informationacrossvaryingtimescales.Thisdesignenablesthe facilitatingtheinteractionmoduleincapturingcorrelationsacross
modeltocapturetime-dependentfeaturesatdifferentgranularities timeoffsets.Finally,thelearningprocessoftheproposedMI-KAN
inlongsequences—forexample,somesub-sequencesaremoreef- modulecanbeformulatedas:
f s e u c i t t i e v d e f a o t r m lo o n d g e - li t n e g rm sh t o r r e t n -t d e s r . m Th fl e uc in tu tr a o ti d o u n c s t , i w on hi o le f o M th u e lt r i s -O ar ff e s b e e t t T te o r - {M 1 ′,...,𝑀 O ′ }=𝑀𝐼−𝐾𝐴𝑁(M 1 ,...,𝑀 O ) (4)
kenEmbeddingsignificantlyenhancesthemodel’sadaptabilityto Theoffsetsub-sequencerepresentations{M′,...,𝑀′ }∈RO×𝑁×𝑇
1 O
complextemporalpatterns,whileeffectivelymitigatingoverfitting obtainedfromtheMI-KANmodule,preservethetemporaldynamics
causedbynoiseinthetrainingdata,therebyimprovingoverall withineachindividualsub-sequence.
generalization.
3.4 Multi-OffsetTemporalInteraction
3.3 Multi-OffsetInteractiveKAN Forecasting
AftertheMulti-OffsetTokenEmbeddingprocess,weobtainmulti- Tofurthercapturecorrelationsacrossdifferenttimesteps,wein-
pleoffsetsub-sequences{M 1 ,...,𝑀 O }.Tofurthercapturethetem- troducethe Multi-OffsetTemporal InteractionMechanism. The
poraldependenciesbothwithinandacrossthesesub-sequences, primaryobjectiveofthismechanismistoleveragethepreviously
we design the Multi-Offset Interactive KAN (MI-KAN) module, proposedMulti-OffsetTokenEmbeddingtoenhancethemodel’s
whichaimstolearndedicatedrepresentationsforeachoffsetsub- abilitytocaptureimplicittemporalstructuresacrossmultiplere-
sequenceandmodeltheirmutualrelationships.Comparedwith latedsub-sequences.Specifically,foreachsub-sequencesM′ 𝑢,we
traditionalMLPs,KAN(Kolmogorov-ArnoldNetwork)[29]focuses applyamulti-headSelf-Attentionmechanism(𝑀𝑆𝐴)onallitsfea-
moreonapproximatingcomplex,high-dimensionalmappingrela- turedimensions:
tionshipsthroughasetofcombinablesimplefunctions.Specifically, A𝑢 =M′ 𝑢+𝑀𝑆𝐴(M′ 𝑢 ,M′ 𝑢 ,M′ 𝑢) (5)
KANenhancesthenetwork’sabilitytomodelnonlinearpatterns
byreplacingtraditionallinearconnectionsbetweenneuronswith WhereM′ 𝑢 ∈R𝑁×𝑇 representstherepresentationofthe𝑢-thoffset
learnableunivariatefunctions.Themappingbetweenneuronsin sub-sequence,and𝑀𝑆𝐴(·)isamulti-headself-attentionoperation.
adjacentlayerscanbeformulatedas: Duetotheuseofpiecewiseoffsetembeddings,eachsub-sequence
issignificantlyshortened,resultinginanattentioncomputation
Z 𝑗 (𝑙+1) =(cid:205)𝜙 𝑖𝑗(Z 𝑖 (𝑙)) (1) withapproximatelylineartimecomplexityatthisstage[42].After
𝑖
modelingtheinternalstructureofeachsub-sequence,wefurther
WhereZ(𝑙) representsthe𝑖thneuroninthe𝑙thlayer,Z(𝑙+1)
repre- introduce a global fusion operation to integrate the interaction
𝑖 𝑗
sentsthe𝑗thneuroninthe(𝑙+1)thlayer,and𝜙 𝑖𝑗 istheunivariate resultsoftheoriginalsequencerepresentationX withalloffset
mappingfunctionfromthe𝑖thtothe𝑙thneuron.EarlyKANimple- sub-sequencesA,inordertocapturepotentialdependenciesacross
mentationsusuallyusedsplinefunctionsasbasicbuildingblocks, differenttemporalsegments.Thefusionprocessisformallydefined
butsuchmethodsoftenrequirecomplexrescalingandhavepoor as:
stabilitywhendealingwithvariablescrossingtheboundariesof H =X+𝑀𝑆𝐴(Q=A,K =X,V =X) (6)
thedomain.Toaddresstheselimitations,weadoptthemoreeffi- ThesequenceprocessedbytheMulti-OffsetInteractionMechanism
cientandstableFastKANLayer[24],whichconstructsunivariate servesasthequery,whiletheoriginalsequenceactsasboththekey
mappingsusingcombinationsofradiallysymmetricfunctionsand andvalue,enablinginformationfusionacrossdifferenttemporal
offersgreaterflexibilityandgeneralizationcapability.Inourim- offsets.Togeneratethefinalpredictionresult,wemapthetime
plementation,weemployGaussianradialbasisfunctions(RBFs)to dimensiontothepredictionlengthofthetargetthroughalinear
modelthenonlinearrelationshipsintheinput.TheRBFisdefined layer.Thetransformationcanbeexpressedas:
asfollows:
Y =𝐿𝑖𝑛𝑒𝑎𝑟(H) ∈R𝑁×F (7)
𝜙(𝑟)=exp(−𝑟2 ) (2)
2ℎ2
Where𝑟 representsthedistancebetweentheinputandthecenter,
andℎcontrolsthesmoothnessofthefunction.Theoutputofthe
4 Experiments
RBFnetworkisalinearcombinationofthisradialbasisfunction,
4.1 ExperimentalSetup
weightedbyanadjustablecoefficient.TheoutputoftheentireRBF
networkcanbeexpressedas: Datasets.TovalidatetheeffectivenessofTime-TK,weconducted
extensiveexperimentson14differentdatasets,asshowninthe
𝑁
𝑓(𝑥)= (cid:205)𝑤 𝑖 𝜙(∥𝑥−𝑥 𝑖∥) (3) Table1,includingfoursubsetsofETT(ETTh1,ETTh2,ETTm1,and
𝑖=1
ETTm2),Electricity,Exchanges,Solar-Energy,weather[38],and
Where𝑤 𝑖isthelearnableweightand𝑥 𝑖istheRBFcenter.Itisworth Traffic.Forshort-termforecasting,weusedfoursubsetsofPEMS
notingthatFastKANLayerexhibitsstrongexpressivenessandef- (PEMS03, PEMS04, PEMS07, and PEMS08). Furthermore, we in-
fectivelycapturesthecomplexdynamicpatternspresentintime cluded20,000BTC/USDTdatarecordswitha5-minutethroughput.
seriesdata.Itgeneratescorrespondingdeeprepresentationsfor Accurateforecastscansignificantlyimprovetheeffectivenessof
eachinputsub-sequence.Thisdesignnotonlysimplifiesthemodel remedialorpreventivemeasuresimplementedbywebapplications,

Time-TK:AMulti-OffsetTemporalInteractionFrameworkforTimeSeriesForecasting WWW’26,April13–17,2026,Dubai,UnitedArabEmirates
Table1:Detaileddescriptionofthedataset.Dimindicatesthenumberofvariablesineachdataset.DatasetSizeindicatesthe
totalnumberoftimepointsin(trainingset,validationset,testset).PredictionLengthindicatesthefuturetimepointsthat
needtobepredicted.Eachdatasetcontainsfourpredictionsettings.Frequencyindicatesthesamplingintervalofthetime
points.DatastatisticsarefromiTransformer[28].
Dataset Dim PredictionLength DatasetSize Frequency Information
ETTh1,ETTh2 7 {96,192,336,720} {8545,2881,2881} Hourly Electricity
ETTm1,ETTm2 7 {96,192,336,720} {34465,11521,11521} 15min Electricity
Exchange 8 {96,192,336,720} {5120,665,1422} Daily Economy
Weather 21 {96,192,336,720} {36792,5271,10540} 10min Weather
ECL 321 {96,192,336,720} {18317,2633,5261} 10min Electricity
Traffic 862 {96,192,336,720} {12185,1757,3509} Hourly Transportation
Solar-Energy 137 {96,192,336,720} {36601,5161,10417} 10min Energy
PEMS03 358 {12,24,48,96} {15671,5135,5135} 5min Transportation
PEMS04 307 {12,24,48,96} {10172,3375,3375} 5min Transportation
PEMS07 883 {12,24,48,96} {16911,5622,5622} 5min Transportation
PEMS08 170 {12,24,48,96} {10690,3548,3548} 5min Transportation
BTC/USDT 5 {12,288,864} {12989,2004,4007} 5min Economy
Table2:Comparisonofmultivariatetimeseriesforecastingresultsfor13realdatasets.Averagelong-termforecastresults
withauniformlookbackwindowL=96foralldatasets.Allresultsareaveragedover4differentforecastlengths:F ={12,24,
48,96}forthePEMSdatasetandF ={96,192,336,720}forallotherdatasets.Thebestmodelisshowninboldblack,andthe
second-bestisunderlined.SeeAppendixBforcompleteresults.
Time-TK MMK TimeKAN CMoS MSGNet iTransformer TimeMixer PatchTST TimesNet DLinear Crossformer
Models
(Ours) (2025) (2025) (2025) (2024) (2024) (2024) (2023) (2023) (2023) (2023)
Metric MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
ETTh1 0.432 0.430 0.432 0.436 0.425 0.430 0.448 0.442 0.453 0.453 0.463 0.454 0.458 0.445 0.469 0.454 0.458 0.450 0.456 0.452 0.529 0.522
ETTh2 0.372 0.397 0.390 0.417 0.390 0.408 0.392 0.410 0.413 0.427 0.383 0.407 0.384 0.407 0.389 0.411 0.414 0.427 0.559 0.515 0.942 0.684
ETTm1 0.379 0.393 0.384 0.397 0.379 0.396 0.412 0.410 0.400 0.412 0.405 0.410 0.385 0.399 0.396 0.406 0.400 0.406 0.403 0.407 0.513 0.495
ETTm2 0.276 0.321 0.278 0.327 0.279 0.324 0.288 0.330 0.289 0.330 0.290 0.335 0.280 0.325 0.291 0.336 0.291 0.333 0.350 0.401 0.757 0.611
Electricity 0.174 0.265 0.201 0.286 0.197 0.286 0.204 0.284 0.194 0.301 0.178 0.270 0.182 0.272 0.211 0.301 0.193 0.295 0.212 0.300 0.244 0.334
Exchange 0.353 0.397 0.375 0.412 0.404 0.423 0.388 0.427 0.399 0.430 0.375 0.412 0.408 0.422 0.378 0.415 0.416 0.443 0.354 0.414 0.471 0.478
Solar-Energy 0.205 0.257 0.243 0.299 0.287 0.321 0.332 0.322 0.263 0.292 0.233 0.262 0.237 0.290 0.270 0.307 0.301 0.319 0.330 0.401 0.641 0.639
Weather 0.256 0.278 0.246 0.273 0.243 0.272 0.251 0.278 0.249 0.278 0.258 0.278 0.245 0.276 0.259 0.281 0.259 0.287 0.265 0.317 0.259 0.315
Traffic 0.425 0.278 0.541 0.335 0.590 0.374 0.617 0.366 0.660 0.382 0.428 0.282 0.485 0.298 0.555 0.362 0.620 0.336 0.625 0.383 0.550 0.304
PEMS03 0.112 0.219 0.158 0.261 0.171 0.258 0.147 0.253 0.150 0.251 0.113 0.221 0.144 0.258 0.137 0.240 0.147 0.248 0.278 0.375 0.169 0.281
PEMS04 0.109 0.218 0.152 0.279 0.148 0.259 0.124 0.249 0.122 0.239 0.111 0.221 0.161 0.272 0.145 0.249 0.129 0.241 0.295 0.388 0.209 0.314
PEMS07 0.093 0.195 0.138 0.233 0.139 0.240 0.154 0.247 0.122 0.227 0.101 0.204 0.162 0.253 0.144 0.233 0.124 0.225 0.329 0.395 0.235 0.315
PEMS08 0.145 0.224 0.214 0.268 0.213 0.291 0.176 0.255 0.205 0.285 0.150 0.226 0.206 0.296 0.200 0.275 0.193 0.271 0.379 0.416 0.268 0.307
Count 23 0 4 0 0 0 0 0 0 0 0
suchasinintelligenttrafficmanagementandwebsitetransactions. periodicfeaturessuchasseasonalityanddailyperiodicity[17],and
SeeAppendixA.1formoredetailedinformation. isaccompaniedbystrongnon-stationarity.Thefrequencydecom-
Setup.AllexperimentsareimplementedinPyTorch.Weuse positionarchitectureadoptedbyTimeKANcaneffectivelymodel
themainstreamMSEandMAEasourevaluationindicators.See periodicsignalsofdifferentfrequencies,soitperformsparticularly
AppendixA.3formoredetailedinformation. wellonmulti-perioddatasetssuchasWeather.
Baselines. We select 10 latest models, including MMK [12], Itisworthnotingthatwealsocomparewithexistingmodels
TimeKAN[15],CMoS[33],MSGNet[6],iTransformer[28],TimeMixer basedonKANarchitecture.ComparedwithMMK[12],ourmodel
[36],PatchTST[30],TimesNet[37],DLinear[46]andCrossformer Time-TK reduces MSE by 6.69% and MAE by 7.90% on average
[49]asourbaselines. on 13 real-world datasets. Compared with TimeKAN, Time-TK
reducesMSEby7.4%andMAEby8.57%,indicatingthatTime-TKis
4.2 MainResults successfulinintroducingKANnetworkintotimeseriesmodeling.
In addition, compared with iTransformer [28] based on overall
ThecomprehensivepredictionresultsofTime-TKand13baseline
temporalembeddingandPatchTST[30]basedontemporalpatch
modelsareshowninTable2.Thebestresultsaremarkedinbold
embedding,Time-TKreducesMSEby6.41%/10.84%andMAEby
andthesecondbestresultsaremarkedinblackunderline.The
5.47%/10.71%,respectively.
lowertheMSEandMAE,themoreaccuratethepredictionresults.
Additionally,Table3presentsthedetailedpredictionresultsof
Time-TKrankedfirstin23ofthe26experimentalcases,demon-
Time-TKagainstsevenbaselinemodelsontheBTC/USDTdataset.
stratingitsexcellentperformanceinbothlongandshorttimeseries
Theresultsclearlydemonstrateasignificantandconsistentper-
predictiontasks.OntheWeatherdataset,TimeKAN[15]achieved
formanceadvantageforTime-TKacrossallpredictionhorizons.
thebestresults.ThismaybebecauseWeatherdatahasmultiple

WWW’26,April13–17,2026,Dubai,UnitedArabEmirates FanZhang,ShimingFan,andHuaWang
Table3:PerformancecomparisonontheBTC/USDTdataset.Wepredictthetransactionthroughputforthenexthour,day,and
threedayswithaninputlengthofL=96.
Setting Metric Time-TK MMK TimeKAN CMoS MSGNet iTransformer TimeMixer
MAE 0.103 0.112 0.105 0.112 0.114 0.112 0.109
BTC/USDT->1hour RSE 0.725 0.742 0.725 0.729 0.732 0.729 0.727
RMSE 0.402 0.418 0.407 0.411 0.415 0.411 0.409
MAPE 1.459 1.509 1.358 1.480 1.520 1.480 1.527
MAE 0.228 0.237 0.232 0.242 0.242 0.238 0.230
BTC/USDT->1day RSE 0.904 0.93 0.913 0.945 0.925 0.922 0.910
RMSE 0.471 0.493 0.484 0.498 0.483 0.489 0.483
MAPE 3.606 3.661 3.568 3.726 3.740 3.710 3.560
MAE 0.324 0.340 0.332 0.336 0.341 0.330 0.340
BTC/USDT->3day RSE 1.020 1.163 1.143 1.159 1.210 1.140 1.169
RMSE 0.531 0.544 0.534 0.548 0.551 0.533 0.547
MAPE 8.512 8.886 8.534 8.868 8.893 8.728 8.806
Outof12experimentalevaluations(4metricsacross3settings), Table5:MOTEcaneffectivelyimprovetheforecastingper-
Time-TKsecuredthetopresult8timesandplacedwithinthetop formanceofmodelswithdifferentembeddingstrategies.
two10times.ThisstronglyindicatesthattheTime-TKarchitecture
ishighlyeffectiveformodelingcomplextimeseriesdata. iTransformer PatchTST TimesNet
Model
Foroverallperformance,wetrainon10representativedatasets InvertedEmbedding PatchEmbedding MixedEmbedding
with3randomseedsover4forecastinghorizons,asshowninTable Setup Original +MOTE Original +MOTE Original +MOTE
Metric MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
9.UsingTimeKANasthebaseline,aWilcoxontestontheaveraged
MSE/MAE yields𝑝-values of 1.86×10−2 and 5.86×10−3, both
below0.02,indicatingthattheoverallimprovementofTime-TK
overTimeKANisstatisticallysignificantatthe98%confidencelevel (99%forMAE).
Overall,thesesignificantperformanceimprovementsaremainly
duetothesynergybetweenourproposedMulti-OffsetTokenEm-
beddingandMulti-OffsetInteractionmechanism,whichenables
themodeltoeffectivelycapturecomplexandmulti-scaledynamic
patternsinthetimedimension.
Table4:Ablationexperimentsofmulti-offsetembeddingand
multi-offsetinteractionofTime-TK.
Strategy Time-TK iTransformer
MOTI+MOTE MOTI MOTE
Metric MSE MAE MSE MAE MSE MAE MSE MAE
96 0.370 0.393 0.378 0.396 0.416 0.427 0.394 0.409
ETTh1 1 3 9 3 2 6 0 0 . . 4 4 2 6 3 5 0 0 . . 4 4 2 4 1 4 0 0 . . 4 4 3 7 3 3 0 0 . . 4 4 2 4 4 4 0 0 . . 4 5 6 1 8 0 0 0 . . 4 4 5 7 7 9 0 0 . . 4 4 4 9 8 1 0 0 . . 4 4 4 6 1 4
720 0.470 0.462 0.493 0.470 0.490 0.489 0.519 0.502
96 0.315 0.354 0.326 0.362 0.347 0.382 0.336 0.370
ETTm1 1 3 9 3 2 6 0 0 . . 3 3 5 9 6 3 0 0 . . 3 4 7 0 8 2 0 0 . . 3 4 6 0 7 5 0 0 . . 3 4 8 0 2 3 0 0 . . 3 4 8 1 9 7 0 0 . . 4 4 0 2 0 2 0 0 . . 3 4 8 1 1 7 0 0 . . 3 4 9 1 5 8
720 0.453 0.439 0.468 0.443 0.470 0.454 0.487 0.456
96 0.083 0.202 0.084 0.203 0.092 0.214 0.088 0.209
Exchange 1 3 9 3 2 6 0 0 . . 1 3 6 2 8 2 0 0 . . 2 4 9 1 2 1 0 0 . . 1 3 7 3 8 2 0 0 . . 2 4 9 1 9 6 0 0 . . 1 3 8 5 9 6 0 0 . . 3 4 1 3 2 2 0 0 . . 1 3 8 3 3 6 0 0 . . 3 4 0 1 8 8
720 0.838 0.684 0.890 0.706 1.149 0.784 0.893 0.714
12 0.076 0.175 0.085 0.186 0.091 0.195 0.079 0.182
PEMS08 2 4 4 8 0 0 . . 1 1 0 8 6 3 0 0 . . 2 2 0 5 6 1 0 0 . . 1 1 2 9 2 9 0 0 . . 2 2 2 7 6 6 0 0 . . 1 1 2 6 3 0 0 0 . . 2 2 2 7 4 2 0 0 . . 1 1 1 8 5 6 0 0 . . 2 2 1 3 9 5
96 0.215 0.262 0.245 0.302 0.242 0.300 0.221 0.267
4.3 ModelAnalysis
4.3.1 AblationStudyontheDesignofMOTE. AsshowninTable4,
wefurtherevaluatedtheindependentcontributionofeachcompo-
nenttothemodelperformance.Bycomparingthepredictionresults
afterremovingthetwokeycomponentsofTime-TK,Multi-Offset
TokenEmbedding(MOTE)andMulti-OffsetTemporalInteraction
1hTTE 96 0.394 0.409 0.389 0.405 0.414 0.419 0.403 0.416 0.384 0.402 0.379 0.398 192 0.448 0.441 0.443 0.440 0.460 0.445 0.449 0.439 0.436 0.429 0.431 0.426
336 0.491 0.464 0.487 0.461 0.501 0.466 0.488 0.456 0.491 0.469 0.490 0.467
720 0.519 0.502 0.511 0.492 0.500 0.488 0.487 0.477 0.521 0.500 0.513 0.497
Avg 0.463 0.454 0.458 0.450 0.469 0.454 0.457 0.447 0.458 0.450 0.453 0.447
2hTTE 96 0.297 0.349 0.296 0.345 0.292 0.345 0.292 0.344 0.340 0.374 0.312 0.364 192 0.380 0.400 0.375 0.397 0.388 0.405 0.376 0.393 0.402 0.414 0.386 0.403 336 0.428 0.432 0.419 0.429 0.427 0.436 0.382 0.410 0.452 0.452 0.423 0.432
720 0.427 0.445 0.419 0.438 0.447 0.458 0.411 0.433 0.462 0.468 0.448 0.462
Avg 0.383 0.407 0.377 0.402 0.389 0.411 0.365 0.395 0.414 0.427 0.392 0.415
egnahcxE 96 0.088 0.209 0.088 0.208 0.090 0.211 0.084 0.202 0.107 0.234 0.091 0.211
192 0.183 0.308 0.179 0.304 0.186 0.307 0.174 0.296 0.226 0.344 0.192 0.321
336 0.336 0.418 0.321 0.411 0.339 0.424 0.320 0.407 0.367 0.448 0.362 0.403
720 0.893 0.714 0.864 0.707 0.898 0.718 0.855 0.696 0.964 0.746 0.912 0.721
Avg 0.375 0.412 0.363 0.408 0.378 0.415 0.358 0.400 0.416 0.443 0.389 0.414
raloS 96 0.203 0.238 0.198 0.235 0.234 0.286 0.231 0.278 0.250 0.292 0.237 0.284 192 0.233 0.261 0.226 0.269 0.267 0.310 0.257 0.296 0.296 0.318 0.288 0.311
336 0.248 0.273 0.236 0.273 0.290 0.315 0.283 0.308 0.319 0.330 0.292 0.317
720 0.249 0.276 0.243 0.283 0.289 0.317 0.286 0.313 0.338 0.337 0.301 0.319
Avg 0.233 0.262 0.226 0.265 0.270 0.307 0.264 0.299 0.301 0.319 0.280 0.308
(MOTI),wefoundthatthesetwocomponentshaveasignificant
positiveeffectonimprovingpredictionefficiency.
Table6:AblationexperimentsofMI-KANofTime-TK.
Metric ETTh1 ETTh2 ETTm1 ETTm2 Solar-Energy Electricity
Datasets MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
MLP 0.379 0.396 0.298 0.345 0.320 0.357 0.176 0.260 0.217 0.289 0.155 0.247
Conv1d 0.375 0.394 0.300 0.346 0.318 0.357 0.176 0.257 0.214 0.287 0.161 0.252
KAN 0.376 0.396 0.295 0.343 0.319 0.356 0.175 0.255 0.210 0.281 0.151 0.244
RBF 0.370 0.393 0.293 0.340 0.315 0.354 0.173 0.253 0.187 0.234 0.147 0.240
4.3.2 Ablation Study on the Design of MI-KAN. In this section,
wedesignseveralvariantstoinvestigatetheeffectivenessofMI-
KAN:○1 MLP,whereeachMI-KANisreplacedwithamultilayer
perceptron;○2 Conv1d,whereeachMI-KANisreplacedwitha1D
convolutionallayer;○3 KAN,whichusesaB-spline-basedKAN
structure[12];○4 RBF,whereradialbasisfunctions(RBFs)[4,24]
areusedastheactivationmoduleinourMI-KAN.Asshownin
Table6,MI-KANachievesthebestresults.Notably,bothMI-KAN
andtheB-spline-basedKANoutperformMLP,indicatingthatKAN

Time-TK:AMulti-OffsetTemporalInteractionFrameworkforTimeSeriesForecasting WWW’26,April13–17,2026,Dubai,UnitedArabEmirates
    
    
    
    
              
 3 U H G L F W L R Q  + R U L ] R Q
 ( 6 0
 ( O H F W U L F L W \    0 6 (
    
    
    
    
              
 3 U H G L F W L R Q  + R U L ] R Q
 ( $ 0
 ( O H F W U L F L W \    0 $ (
     
     
     
     
     
     
     
              
 3 U H G L F W L R Q  + R U L ] R Q
 ( 6 0
 ( 7 7 P     0 6 (
    
    
    
    
    
    
              
 3 U H G L F W L R Q  + R U L ] R Q
 ( $ 0
 ( 7 7 P     0 $ (
 :  2  7 U D Q V  :  2  . $ 1  7 U D Q V  . $ 1
Figure4:AblationstudycomparingTime-TKwithitsarchitecturalvariantsontheElectricityandETTm1datasetsacross
multiplepredictionhorizons.
hasstrongerrepresentationalcapacitythanMLP.Moreover,MI- wecomparedthefullmodel(Trans+KAN)withtwovariants:one
KANoutperformstheB-spline-basedKAN,furthervalidatingthe withtheTransformerattentionmechanismremoved(W/OTrans),
effectivenessofadoptingRBFs. andanotherwiththeKANmoduleremoved(W/OKAN).There-
sultsclearlyindicatethatourfullmodelachievedtheoptimalresults
Table 7: Prediction performance under different input acrossallpredictionhorizons.Thisfindingstronglydemonstrates
lengthsontheETTm1dataset.Theinputlengthisselected thatremovingeitherkeycomponentleadstoasignificantdegrada-
as L={48,96,144,192,288,384,480}, and the fixed prediction tioninmodelperformance,thusconfirmingtheindispensabilityof
lengthisF=96.MOTEcaneffectivelyenhancethelearning bothmodules.Wefurtherinvestigatethissynergybyvisualizingin-
ofhistoricalinformation. termediatefeaturerepresentationswitht-SNE,asshowninFig.tkt.
Asthefirstmoduleinourarchitecture,KAN(Figure5,left)actsasa
nonlinearfeatureextractorthatmapstherawinputsequenceonto
Model PatchTST +MOTE iTrans +MOTE
aring-shapedmanifoldwithclearperiodicstructure,revealingthe
Metric MSE MAE MSE MAE MSE MAE MSE MAE underlyingnonlinearpatternsbeforetemporaldependenciesare
48 0.502 0.437 0.504 0.440 0.458 0.424 0.450 0.420 modeled.ThesubsequentTransformerattention(Figure5,right)
96 0.329 0.365 0.340 0.368 0.336 0.370 0.342 0.375 thenperformsweightedaggregationovermultipletimestepson
144 0.324 0.359 0.316 0.356 0.318 0.363 0.311 0.361 thismanifoldtocapturelong-rangedependencies,whichleadsto
192 0.307 0.347 0.304 0.348 0.316 0.363 0.306 0.358 amore“mixed”cloudinthet-SNEprojectionratherthanstrictly
288 0.296 0.344 0.292 0.343 0.303 0.357 0.305 0.358 separatedclusters.Overall,thisvisualizationsuggeststhatMOTE
384 0.298 0.345 0.291 0.343 0.310 0.364 0.305 0.358 andKANtogetherorganizetherawseriesintostructuredcontinu-
480 0.297 0.346 0.291 0.342 0.314 0.366 0.304 0.357 ousrepresentationsandsupportmulti-scaletemporalintegration
ontopofthem.
 7  6 1 (  R I  . $ 1  7  6 1 (  R I  $ W W H Q W L R Q
  
4.5 Performancepromotion
     
InadditiontotheablationstudyonMulti-OffsetTokenEmbedding
   
(MOTE),wefurtherevaluateitsgeneralizabilityandtransferability
 
  acrossdifferentmodels.Specifically,weintegrateMOTEintothree
 
     representativemodelswithdifferentembeddingstrategiestoverify
whetheritcanenhanceperformance:
     
i) For iTransformer [28] with holistic embedding, we apply
                             
MOTEforembeddingandinteractionbeforetheattentionmodule
toenhanceintra-sequencemodelingcapability;ii)ForPatchTST
Figure5:t-SNEvisualizationafterKANandTransformer.
[30]withpatchembedding,weapplymulti-offsetsequencestoits
patchattention,enablingfiner-grainedmodelingofthesequence
structure;iii)ForTimesNet[37]withchannel-mixingarchitecture,
4.4 EffectivenessofcombiningKANand
weintroduceMOTEbeforetheconvolutionoperations,allowing
Transformer
themodeltobettercapturecomplexperiodicpatterns.
Tovalidatethesynergisticeffectivenessofthetwocorecomponents AsshowninTable5,integratingthemulti-offsetembeddinginto
inTime-TK,TransformerandKAN,weconductedacomprehensive allthreearchitecturesconsistentlyimprovesforecastingperfor-
ablationstudy,withtheresultsshowninFigure4.Intheexperiment, mance,demonstratingthatMOTEcanbewidelyappliedtovarious

WWW’26,April13–17,2026,Dubai,UnitedArabEmirates FanZhang,ShimingFan,andHuaWang
predictionmodelsandthatourproposedembeddingmechanism
exhibitsstrongscalability.
     
     
     
     
     
     
     
     
                   
 , Q S X W  / H Q J W K
 ( 6 0
 ( 7 7 0 
 2  7 L  X  P  U V  H  . $ 1     
 L 7 U D Q V I R U P H U
 3 D W F K 7 6 7     
    
    
    
    
    
                   
 , Q S X W  / H Q J W K
 ( 6 0
increasessignificantlywithlongersequences,owingtotheirpatch-
basedembeddingstrategies,wherethegrowingnumberofpatches
leadstohighermemoryoverhead.Notably,ourproposedTime-TK
demonstratesexcellentmemoryefficiencyacrossdifferentinput
 6 R O D U  ( Q H U J \
 2 X U V lengthswhilestillachievingsuperiorpredictiveperformance(see  7 L P H  . $ 1
 L 7 U D Q V I R U P H U
 3 D W F K 7 6 7 Figure6).ThisindicatesthatthedesignedMulti-OffsetTokenEm-
bedding(MOTE)strategycaneffectivelyutilizelonghistoricalin-
formationwithoutintroducingsubstantialcomputationalburden,
makingTime-TKanefficientforecastingframeworkwell-suitedfor
long-sequencemodeling.
    
Figure6:Thepredictionperformanceunderdifferentinput     
lengthsontwodatasets.Theinputlengthsareselectedas     
L={48,96,144,192,288,384,480},withafixedpredictionlength
    
ofF=96
   
   
4.6 IncreasinglookbackWindow    
Theoretically,basedonstatisticalmethods[3],richhistoricalinfor-    
mationhelpsmodelscapturelong-termdependenciesintimeseries.  
                         
Awell-designedforecastingmodelshouldbeabletoeffectively  6 H T X H Q F H  / H Q J W K
leveragelongerhistoricalsequencestoimprovepredictiveperfor-
mance.AsshowninFigure6,withtheincreaseofinputlength,
theiTransformer[28]usingfull-sequencetokenembeddingshows
asignificantdropinpredictionaccuracy,indicatingthatdirectly
embeddingtheentiresequencemayoverlookfiner-grainedlocal
informationwithinthesequence,thuslimitingmodelingcapacity
forlonginputs.Incontrast,modelsusingpatchtokenembedding,
suchasTimeKAN[15],andPatchTST[30],exhibitmorestableper-
formanceastheinputlengthincreases,suggestingthatthepatching
mechanismhelpsmitigateperformancedegradationfromlongin-
puts.However,theincreasednumberofpatchesalsoleadstohigher
memorycosts,whichlimitsscalabilityinlongsequencemodeling.
Notably,ourTime-TKbenefitsfromtheMOTEembeddingstrat-
egy,whereweembedmulti-offsetsub-sequencesindependently,
enablingthemodeltoadapttolongerlookbackwindowswhile
maintaininglowcomputationalcost.
PreviousstudiesshowthatthepredictiveperformanceofTrans-
formermodelsdoesnotnecessarilyimprovewithlongerlookback
lengths[46].Therefore,weintroduceMOTEintotwoattention-
basedmodels,PatchTSTandiTransformer.AsshowninTable7,
theoriginalmodelsexhibitageneralperformancedropasinput
lengthincreases,whileafterincorporatingMOTE,bothmodels
surprisingly benefit from the extended historical window more
effectively.
4.7 ComputationalCost
Toevaluatethecomputationalcostofdifferentmodels,wecompare
theirGPUmemoryusageundervaryinginputsequencelengths,
asshowninFigure7.iTransformerconsistentlymaintainshigh
GPUmemoryconsumptionacrossallinputlengths,withminimal
variation,primarilyduetoitsfull-sequenceembeddingstrategy,
whichmakesitscomputationalcomplexitylesssensitivetoinput
length.Incontrast,thememoryusageofPatchTSTandTimeKAN
  % L 0   H J D V 8  \ U R P H 0  8 3 *
 2 X U V
 7 L P H  . $ 1
 L 7 U D Q V I R U P H U
 3 D W F K 7 6 7
Figure 7: Comparison of GPU memory usage of different
modelsatdifferentinputsequencelengths.
5 Conclusion
Thispaperproposesanoveltimeseriesforecastingframework,
Time-TK,whichcombinesaMulti-OffsetTokenEmbedding(MOTE)
strategywithMulti-OffsetTemporalInteraction.Unlikeexisting
mainstreamembeddingmethods,MOTEmodelstheinputsequence
atmultipleoffsetpositions,enablingmoreefficientcaptureofboth
localandglobaltemporaldynamics.Itenhancestheutilizationof
longhistoricalinformationwithoutsignificantlyincreasingmem-
oryoverhead.Specifically,wefirstapplymulti-offsetembedding
andthenperformmulti-offsettemporalinteractiontolearntempo-
raldependenciesacrossdifferenttimespans.Extensiveexperiments
on13publicdatasetsdemonstratethatTime-TKoutperformsex-
isting state-of-the-art methods in both prediction accuracy and
generalizationcapability.Notably,theMOTEembeddingnotonly
improvesourmodel’sperformancebutalsoshowsconsistentgains
whenintegratedintootherarchitectureswithdifferentembedding
schemes,furthervalidatingitsgeneralityandeffectiveness.Time-
TKoffersnewinsightsanddirectionsfordesigningefficientand
scalabletimeseriesforecastingmodels.
Acknowledgements
Thisworkwassupportedinpartbythefollowing:theJointFund
oftheNationalNaturalScienceFoundationofChinaunderGrant
Nos.U24A20219,U24A20328,U22A2033,theNationalNaturalSci-
enceFoundationofChinaunderGrantNo.62272281,theSpecial
FundsforTaishanScholarsProjectunderGrantNo.tsqn202306274,
andtheYouthInnovationTechnologyProjectofHigherSchoolin
ShandongProvinceunderGrantNo.2023KJ212.

Time-TK:AMulti-OffsetTemporalInteractionFrameworkforTimeSeriesForecasting WWW’26,April13–17,2026,Dubai,UnitedArabEmirates
References
[24] ZiyaoLi.2024.Kolmogorov-arnoldnetworksareradialbasisfunctionnetworks.
[1] RazanAlkhanbouli,HourMatarAbdullaAlmadhaani,FarahAlhosani,andMecit arXivpreprintarXiv:2405.06721(2024).
CanEmreSimsekler.2025.Theroleofexplainableartificialintelligenceindisease [25] ZhimingLin,KaiZhao,SophieZhang,PeilaiYu,andCanranXiao.2025.CEC-
prediction:asystematicliteraturereviewandfutureresearchdirections.BMC Zero:Zero-SupervisionCharacterErrorCorrectionwithSelf-GeneratedRewards.
medicalinformaticsanddecisionmaking25,1(2025),110. arXivpreprintarXiv:2512.23971(2025).
[2] AdebiyiAAriyo,AdewumiOAdewumi,andCharlesKAyo.2014.Stockprice [26] DingyuanLiu,QiannanShen,andJiaciLiu.2026.TheHealth-WealthGradient
predictionusingtheARIMAmodel.In2014UKSim-AMSS16thinternational inLaborMarkets:IntegratingHealth,Insurance,andSocialMetricstoPredict
conferenceoncomputermodellingandsimulation.IEEE,106–112. EmploymentDensity.(January2026).doi:10.21203/rs.3.rs-8497932/v1Preprint,
[3] GeorgeEPBoxandGwilymMJenkins.1968.Somerecentadvancesinforecasting postedJanuary4,2026.
andcontrol.JournaloftheRoyalStatisticalSociety.SeriesC(AppliedStatistics)17, [27] MinhaoLiu,AilingZeng,MuxiChen,ZhijianXu,QiuxiaLai,LingnaMa,and
2(1968),91–109. QiangXu.2022. Scinet:Timeseriesmodelingandforecastingwithsample
[4] RomanBresson,GiannisNikolentzos,GeorgePanagopoulos,MichailChatzianas- convolutionandinteraction.AdvancesinNeuralInformationProcessingSystems
tasis,JunPang,andMichalisVazirgiannis.2024.Kagnns:Kolmogorov-arnold 35(2022),5816–5828.
networksmeetgraphlearning.arXivpreprintarXiv:2406.18380(2024). [28] YongLiu,TenggeHu,HaoranZhang,HaixuWu,ShiyuWang,LintaoMa,and
[5] RuichuCai,ZhifanJiang,KaitaoZheng,ZijianLi,WeilinChen,XuexinChen, MingshengLong.2024.iTransformer:InvertedTransformersAreEffectivefor
YifanShen,GuangyiChen,ZhifengHao,andKunZhang.2025.Learningdisen- TimeSeriesForecasting.InTheTwelfthInternationalConferenceonLearning
tangledrepresentationformulti-modaltime-seriessensingsignals.InProceedings Representations. https://openreview.net/forum?id=JePfAI8fah
oftheACMonWebConference2025.3247–3266. [29] ZimingLiu,YixuanWang,SachinVaidya,FabianRuehle,JamesHalverson,Marin
[6] WanlinCai,YuxuanLiang,XianggenLiu,JianshuaiFeng,andYuankaiWu.2024. Soljačić,ThomasYHou,andMaxTegmark.2024. Kan:Kolmogorov-arnold
Msgnet:Learningmulti-scaleinter-seriescorrelationsformultivariatetimeseries networks.arXivpreprintarXiv:2404.19756(2024).
forecasting.InProceedingsoftheAAAIconferenceonartificialintelligence,Vol.38. [30] YuqiNie,NamHNguyen,PhanwadeeSinthong,andJayantKalagnanam.2023.
11141–11149. Atimeseriesisworth64words:Long-termforecastingwithtransformers.arXiv
[7] ChaochaoChen,YizhaoZhang,YuyuanLi,JunWang,LianyongQi,Xiaolong preprintarXiv:2211.14730(2023).
Xu,XiaolinZheng,andJianweiYin.2024.Post-trainingattributeunlearningin [31] XiangfeiQiu,XingjianWu,YanLin,ChenjuanGuo,JilinHu,andBinYang.
recommendersystems.ACMTransactionsonInformationSystems43,1(2024), 2024.Duet:Dualclusteringenhancedmultivariatetimeseriesforecasting.arXiv
1–28. preprintarXiv:2412.10859(2024).
[8] XiaohongChen,CanranXiao,andYongmeiLiu.2024. Confusion-resistant [32] QiannanShenandJingZhang.2025. AI-EnhancedDisasterRiskPrediction
federatedlearningviadiffusion-baseddataharmonizationonnon-IIDdata.In withExplainableSHAPAnalysis:AMulti-ClassClassificationApproachUsing
Proceedingsofthe38thInternationalConferenceonNeuralInformationProcessing XGBoost.doi:10.21203/rs.3.rs-8437180/v1Preprint,Version1,postedDecember
Systems.137495–137520. 31,2025.
[9] ShimingFan,HuaWang,andFanZhang.2025.CAWformer:Acrossvariable [33] HaotianSi,ChanghuaPei,JianhuiLi,DanPei,andGaogangXie.2025.CMoS:
attentionwithdiscretewaveletdenoisingformultivariatetimeseriesforecasting. RethinkingTimeSeriesPredictionThroughtheLensofChunk-wiseSpatial
Knowledge-BasedSystems(2025),113846. Correlations.arXivpreprintarXiv:2505.19090(2025).
[10] FelixAGers,JürgenSchmidhuber,andFredCummins.2000.Learningtoforget: [34] YixiaoTeng,JiameiLv,ZipingWang,YiGao,andWeiDong.2025.TimeChain:
ContinualpredictionwithLSTM.Neuralcomputation12,10(2000),2451–2471. ASecureandDecentralizedOff-chainStorageSystemforIoTTimeSeriesData.
[11] LuHan,Xu-YangChen,Han-JiaYe,andDe-ChuanZhan.2024. Softs:Effi- InProceedingsoftheACMonWebConference2025.3651–3659.
cientmultivariatetimeseriesforecastingwithseries-corefusion.arXivpreprint [35] AshishVaswani,NoamShazeer,NikiParmar,JakobUszkoreit,LlionJones,
arXiv:2404.14197(2024). AidanNGomez,ŁukaszKaiser,andIlliaPolosukhin.2017. Attentionisall
[12] XiaoHan,XinfengZhang,YilingWu,ZhenduoZhang,andZheWu.2024. youneed.Advancesinneuralinformationprocessingsystems30(2017).
AreKANsEffectiveforMultivariateTimeSeriesForecasting? arXivpreprint [36] ShiyuWang,HaixuWu,XiaomingShi,TenggeHu,HuakunLuo,LintaoMa,
arXiv:2408.11306(2024). JamesYZhang,andJunZhou.2024. Timemixer:Decomposablemultiscale
[13] SeppHochreiterandJürgenSchmidhuber.1997.Longshort-termmemory.Neural mixingfortimeseriesforecasting.arXivpreprintarXiv:2405.14616(2024).
computation9,8(1997),1735–1780. [37] HaixuWu,TenggeHu,YongLiu,HangZhou,JianminWang,andMingsheng
[14] QiheHuang,ZhengyangZhou,KuoYang,andYangWang.2025. Exploiting Long.2023.Timesnet:Temporal2d-variationmodelingforgeneraltimeseries
LanguagePowerforTimeSeriesForecastingwithExogenousVariables.InPro- analysis.(2023).
ceedingsoftheACMonWebConference2025.4043–4052. [38] HaixuWu,JiehuiXu,JianminWang,andMingshengLong.2021.Autoformer:De-
[15] SongtaoHuang,ZhenZhao,CanLi,andLeiBai.2025.Timekan:Kan-basedfre- compositiontransformerswithauto-correlationforlong-termseriesforecasting.
quencydecompositionlearningarchitectureforlong-termtimeseriesforecasting. Advancesinneuralinformationprocessingsystems34(2021),22419–22430.
arXivpreprintarXiv:2502.06910(2025). [39] CanranXiao,JiabaoDou,ZhimingLin,ZongKe,andLiweiHou.2025. From
[16] XuanwenHuang,YangYang,YangWang,ChunpingWang,ZhishengZhang, PointstoCoalitions:HierarchicalContrastiveShapleyValuesforPrioritizing
JiarongXu,LeiChen,andMichalisVazirgiannis.2022. Dgraph:Alarge-scale DataSamples.arXivpreprintarXiv:2512.19363(2025).
financialdatasetforgraphanomalydetection.AdvancesinNeuralInformation [40] CanranXiao,ChuangxinZhao,ZongKe,andFeiShen.2025.Curiositymeets
ProcessingSystems35(2022),22765–22777. cooperation:Agame-theoreticapproachtolong-tailmulti-labellearning.arXiv
[17] ZahraKarevanandJohanAKSuykens.2020.TransductiveLSTMfortime-series preprintarXiv:2510.17520(2025).
prediction:Anapplicationtoweatherforecasting.NeuralNetworks125(2020), [41] YongzhengXie,HongyuZhang,andMuhammadAliBabar.2025.Multivariate
1–9. TimeSeriesAnomalyDetectionbyCapturingCoarse-GrainedIntra-andInter-
[18] ZongKe,YuqingCao,ZhenruiChen,YuchenYin,ShouchaoHe,andYuCheng. VariateDependencies.InProceedingsoftheACMonWebConference2025.697–705.
2025. Earlywarningofcryptocurrencyreversalrisksviamulti-sourcedata. [42] XiongxiaoXu,CanyuChen,YueqingLiang,BaixiangHuang,GuangjiBai,Liang
FinanceResearchLetters(2025),107890. Zhao,andKaiShu.2024.Sst:Multi-scalehybridmamba-transformerexpertsfor
[19] ZongKe,JiaqingShen,XuanyiZhao,XinghaoFu,YangWang,ZichaoLi,Lingjie long-shortrangetimeseriesforecasting.arXivpreprintarXiv:2404.14757(2024).
Liu,andHuailingMu.2025.AstabletechnicalfeaturewithGRU-CNN-GAfusion. [43] JiaweiYao,ChumingLi,andCanranXiao.2024.Swiftsampler:Efficientlearning
AppliedSoftComputing(2025),114302. ofsamplerby10parameters.AdvancesinNeuralInformationProcessingSystems
[20] DiederikPKingmaandJimmyBa.2014.Adam:Amethodforstochasticopti- 37(2024),59030–59053.
mization.arXivpreprintarXiv:1412.6980(2014). [44] HuaYe,SiyuanChen,ZiqiZhong,CanranXiao,HaoliangZhang,YuhanWu,and
[21] YuyuanLi,ChaochaoChen,YizhaoZhang,WeimingLiu,LingjuanLyu,Xiaolin FeiShen.2026.SeeingthroughtheConflict:TransparentKnowledgeConflict
Zheng,DanMeng,andJunWang.2023.Ultrare:Enhancingreceraserforrecom- HandlinginRetrieval-AugmentedGeneration.arXivpreprintarXiv:2601.06842
mendationunlearningviaerrordecomposition.AdvancesinNeuralInformation (2026).
ProcessingSystems36(2023),12611–12625. [45] GuoqiYu,JingZou,XiaoweiHu,AngelicaIAviles-Rivero,JingQin,andShujun
[22] YuyuanLi,XiaohuaFeng,ChaochaoChen,andQiangYang.2025. ASurveyon Wang.2024.Revitalizingmultivariatetimeseriesforecasting:Learnabledecom-
RecommendationUnlearning:Fundamentals,Taxonomy,Evaluation,andOpen positionwithinter-seriesdependenciesandintra-seriesvariationsmodeling.
Questions.IEEETransactionsonKnowledge&DataEngineering01(2025),1–20. arXivpreprintarXiv:2402.12694(2024).
doi:10.1109/TKDE.2025.3638174 [46] AilingZeng,MuxiChen,LeiZhang,andQiangXu.2023. Aretransformers
[23] Yuyuan Li, Yizhao Zhang, Weiming Liu, Xiaohua Feng, Zhongxuan Han, effectivefortimeseriesforecasting?.InProceedingsoftheAAAIconferenceon
ChaochaoChen,andChenggangYan.2025.Multi-ObjectiveUnlearninginRec- artificialintelligence,Vol.37.11121–11128.
ommenderSystemsviaPreferenceGuidedParetoExploration.IEEETransactions [47] FanZhang,GongguanChen,HuaWang,JinjiangLi,andCaimingZhang.2023.
onServicesComputing(2025). Multi-scalevideosuper-resolutiontransformerwithpolynomialapproximation.
IEEETransactionsonCircuitsandSystemsforVideoTechnology33,9(2023),4496–
4506.

WWW’26,April13–17,2026,Dubai,UnitedArabEmirates FanZhang,ShimingFan,andHuaWang
[48] FanZhang,GongguanChen,HuaWang,andCaimingZhang.2024.CF-DAN: forecastingtasks.MSErepresentstheaverageofthesquareddif-
Facial-expressionrecognitionbasedoncross-fusiondual-attentionnetwork.Com- ferences between the predicted and actual values, giving more
putationalVisualMedia10,3(2024),593–608.
weighttolargerdeviations.MAEreflectstheaverageoftheab-
[49] YunhaoZhangandJunchiYan.2023.Crossformer:Transformerutilizingcross-
dimensiondependencyformultivariatetimeseriesforecasting.InTheeleventh solutedifferences,thusprovidingamorebalancedpictureofthe
internationalconferenceonlearningrepresentations. overallmagnitudeoftheerror.Together,thesemetricsconstitutea
[50] HaoyiZhou,ShanghangZhang,JieqiPeng,ShuaiZhang,JianxinLi,HuiXiong,
andWancaiZhang.2021. Informer:Beyondefficienttransformerforlongse- comprehensiveassessmentofmodelaccuracy.Themathematical
quencetime-seriesforecasting.InProceedingsoftheAAAIconferenceonartificial definitionsareasfollows:
intelligence,Vol.35.11106–11115.
[51] T Fe ia d n fo Z r h m o e u r , : Z F i r q e i q n u g e M nc a y ,Q en in h g a s n o c n e g d W de e c n o , m X p u o e s W ed an tr g a , n L s i f a o n r g m S e u r n f , o a r n l d on R g o - n te g r J m in s . e 2 r 0 i 2 e 2 s . 𝑀𝑆𝐸= F 1 (cid:205) F (Y𝑖−Yˆ 𝑖) 2
forecasting.InInternationalconferenceonmachinelearning.PMLR,27268–27286. 𝑖=1
F (cid:12) (cid:12)
𝑀𝐴𝐸=
F
1 (cid:205)(cid:12)
(cid:12)
Y𝑖−Yˆ
𝑖
(cid:12)
(cid:12)
A ExperimentalSetting √︄ 𝑖=1
A.1 DATASETDESCRIPTIONS 𝑅𝑀𝑆𝐸=
F
1 (cid:205) F (Y𝑖−Yˆ 𝑖) 2
𝑖=1 (8)
TodemonstratetheapplicationeffectivenessofTime-TKacross √︄
variousdomains,weevaluatediton14differentdatasets.Thede-
(cid:205) F (Y𝑖−Yˆ𝑖)2
𝑅𝑆𝐸= 𝑖=1
scriptionsofthesedatasetsareasfollows: √︄
(cid:205) F (Y𝑖−Y¯)2
• ETT2[50]:containsdatawithtwodifferenttimegranular- 𝑖=1
ities:oneatthehourlylevel(ETTh)andtheotheratthe 𝑀𝐴𝑃𝐸= 1 (cid:205) F (cid:12) (cid:12)Y𝑖−Yˆ𝑖 (cid:12) (cid:12)
15-minutelevel(ETTm).Thisdatasetrecordsthetempera-
F
𝑖=1
(cid:12) Y𝑖 (cid:12)
tureandloadcharacteristicsofsevenoiltransformersfrom WhereF representsthesizeofthelookbackwindow,Y𝑖 repre-
July 2016 to July 2018.The Traffic dataset describes road sentsthetruevalue,andYˆ 𝑖 representsthepredictedvalueofthe
occupancy,collectedbysensorsontheFranciscoFreeway
model.
between2015and2016,withhourlyrecordings.
• Exchange3[38]:Apaneldatasetofdailyexchangeratesfrom
A.3 ExperimentalDetails
eightcountries,spanningfrom1990to2016.
• Weather4[38]:Records21weatherindicators,suchasair Specifically,allexperimentsinthisstudywereimplementedus-
ingPyTorchandexecutedonasingleNVIDIAA100-SXMGPU
temperatureandhumidity,withdatacollectedevery10min-
with40GBofmemory.ThemodelsweretrainedusingtheAdam
utesin2020,fromlocationsinGermany.
• Electricity5[38]:Includeshourlyelectricityconsumption optimizer[20]andoptimizedwiththeL2lossfunction.Thetraining-
validation-testsplitfollowsexistingpracticesintheliterature,such
datafrom321customersbetween2012and2014.
• SolarEnergy6:Containssolarpowergenerationdatafrom asthosereportedforiTransformer[28]andTimesNet[37].Specifi-
cally,theETTandPEMSseriesdatasetsweresplitina6:2:2ratio,
137photovoltaicplantsin2006,sampledevery10minutes.
• PEMS7[27]:ConsistsofCaliforniapublictransportationnet- whiletheremainingdatasetsuseda7:1:2split.Time-TKwastrained
for30epochswithearlystoppingbasedonapatienceof3onthe
workdata,collectedin5-minutewindows.Weusethesame
validationset.Formostdatasets,thelearningratewassetto0.003,
fourpublicsubsets(PEMS03,PEMS04,PEMS07,PEMS08)as
exceptforsmallerdatasetssuchastheETTseries,whereitwas
thoseusedinSCINet[27].
• Traffic8[38]:Collectshourlyroadoccupancydatafrom862 reducedto0.002.Thebatchsizewasadjustedbasedonthedataset
sizetomaximizeGPUutilizationwhileavoidingmemoryoverflow.
sensorsontheSanFranciscoFreewaybetweenJanuary2015
Forexample,abatchsizeof16wasusedfortheTrafficdataset,
andDecember2016.
• BTC/USDT9:Thelatest20,000BTC/USDTdatarecords,in- whileabatchsizeof64wasusedfortheWeatherdataset.Toen-
surereproducibility,allexperimentswereconductedwithafixed
cludingtheopeningprice,highestprice,lowestprice,closing
randomseedof2024.
price,andactualtradingvolumeofeachrecord.
ThemaindetailsareprovidedinTable1. B FullResults
Inthissection,wepresentthefullresultsoftheexperimentscon-
A.2 Evaluationmetrics
ductedinthisstudy,asshowninTable8.Theresultscoverevalua-
Meansquareerror(MSE)andMeanabsoluteerror(MAE)arecom-
tionsacrossdifferentdatasets,demonstratingtherobustnessofthe
monlyusedasmeasuresofforecastingperformanceintimeseries
proposedmethodinvariousreal-worldscenarios.Additionally,we
providedetailedperformancecurves,asshowninFigures1-4,fora
2https://github.com/zhouhaoyi/ETDataset comprehensiveunderstandingofthemodel’sbehavior.Thissection
3https://github.com/laiguokun/multivariate-time-series-data
aimstoprovidereaderswithacompleteviewoftheexperimental
4https://www.bgc-jena.mpg.de/wetter/
5https://archive.ics.uci.edu/ml/datasets/ElectricityLoadDiagrams20112014 outcomes,complementingthediscussionsinthemainbodyofthe
6https://www.nrel.gov/grid/solar-power-data.html paper.Weprovidedetailedtablesandfigurestofacilitateadeeper
7https://pems.dot.ca.gov/
interpretationoftheresultsandtosupporttheconclusionsdrawn
8https://pems.dot.ca.gov/
9https://www.kaggle.com/datasets/shivaverse/btcusdt-5-minute-ohlc-volume-data- intheprecedingsections.Table9showsthestatisticalsignificance
2017-2025 testresults.

Time-TK:AMulti-OffsetTemporalInteractionFrameworkforTimeSeriesForecasting WWW’26,April13–17,2026,Dubai,UnitedArabEmirates
Table8:AllexperimentsfixthelookbacklengthL=96.ForPEMS,thepredictionlengthisF ∈{12,24,48,96};forotherdatasets,
thepredictionlengthisF ∈{96,192,336,720}.Thebestresultisbold,thesecondbestresultisunderlined.
Models Ours MMK TimeKAN CMoS MSGNet iTrans TimeMixer PatchTST TimesNet DLinear Crossformer
Metrics MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
96 0.370 0.393 0.374 0.397 0.373 0.397 0.396 0.403 0.390 0.411 0.394 0.409 0.381 0.401 0.414 0.419 0.384 0.402 0.386 0.400 0.423 0.448
ETTh1 3 1 3 9 6 2 0 0 . . 4 4 6 2 5 3 0 0 . . 4 44 2 4 1 0 0 . . 4 4 6 1 1 9 0 0 . . 4 4 2 5 9 0 0 0 . . 4 4 1 5 4 1 0 0 . . 4 42 4 1 2 0 0 . . 4 4 8 3 1 2 0 0 . . 4 4 5 2 4 8 0 0 . . 4 4 8 4 2 3 0 0 . . 4 4 6 4 9 2 0 0 . . 4 4 9 4 1 8 0 0 . . 4 4 6 4 4 1 0 0 . . 5 4 0 4 1 0 0 0 . . 4 4 6 3 2 3 0 0 . . 5 4 0 6 1 0 0 0 . . 4 4 6 4 6 5 0 0 . . 4 4 9 3 1 6 0 0 . . 4 4 6 2 9 9 0 0 . . 4 4 8 3 1 7 0 0 . . 4 4 5 3 9 2 0 0 . . 5 4 7 7 0 1 0 0 . . 5 4 4 7 6 4
720 0.470 0.462 0.474 0.467 0.460 0.460 0.482 0.482 0.496 0.488 0.519 0.502 0.501 0.482 0.500 0.488 0.521 0.500 0.519 0.516 0.653 0.621
avg 0.432 0.430 0.432 0.436 0.425 0.430 0.448 0.442 0.453 0.453 0.463 0.454 0.458 0.445 0.469 0.454 0.458 0.450 0.456 0.452 0.529 0.522
96 0.293 0.340 0.301 0.353 0.293 0.341 0.309 0.351 0.329 0.371 0.297 0.349 0.292 0.343 0.292 0.345 0.340 0.374 0.333 0.387 0.745 0.584
ETTh2 1 3 9 3 2 6 0 0 . . 3 4 6 1 8 0 0 0 . . 3 4 8 2 8 3 0 0 . . 3 4 7 3 9 2 0 0 . . 4 4 0 4 5 6 0 0 . . 3 4 7 2 7 3 0 0 . . 3 4 9 3 1 5 0 0 . . 3 4 9 3 6 1 0 0 . . 4 4 3 0 7 4 0 0 . . 4 4 0 4 2 0 0 0 . . 4 4 1 4 4 5 0 0 . . 4 3 2 8 8 0 0 0 . . 4 4 0 3 0 2 0 0 . . 4 3 3 7 2 8 0 0 . . 4 3 3 9 4 7 0 0 . . 4 3 2 8 7 8 0 0 . . 4 4 3 0 6 5 0 0 . . 4 4 5 0 2 2 0 0 . . 4 4 5 1 2 4 0 0 . . 5 4 9 7 4 7 0 0 . . 5 4 4 7 1 6 1 0 . . 0 8 4 7 3 7 0 0 . . 7 6 3 5 1 6
720 0.418 0.438 0.446 0.463 0.467 0.465 0.431 0.446 0.480 0.477 0.427 0.445 0.454 0.458 0.447 0.458 0.462 0.468 0.831 0.657 1.104 0.763
avg 0.372 0.397 0.390 0.417 0.390 0.408 0.392 0.410 0.413 0.427 0.383 0.407 0.384 0.407 0.389 0.411 0.414 0.427 0.559 0.515 0.942 0.684
96 0.315 0.354 0.320 0.358 0.324 0.361 0.354 0.381 0.319 0.366 0.336 0.370 0.328 0.363 0.329 0.365 0.338 0.375 0.345 0.372 0.404 0.426
ETTm1 1 3 9 3 2 6 0 0 . . 3 39 5 3 6 0 0 . . 3 4 7 0 8 2 0 0 . . 3 3 6 9 4 5 0 0 . . 3 4 8 0 3 5 0 0 . . 3 35 8 7 6 0 0 . . 3 4 8 0 3 4 0 0 . . 4 3 2 9 3 0 0 0 . . 3 4 9 1 6 8 0 0 . . 4 3 1 7 7 7 0 0 . . 4 3 2 9 2 7 0 0 . . 3 4 8 1 1 7 0 0 . . 4 3 1 9 8 5 0 0 . . 3 3 9 6 0 4 0 0 . . 3 4 8 0 4 4 0 0 . . 3 4 8 0 0 0 0 0 . . 4 3 1 9 0 4 0 0 . . 3 4 7 1 4 0 0 0 . . 3 4 8 1 7 1 0 0 . . 4 3 1 8 3 0 0 0 . . 3 4 8 1 9 3 0 0 . . 4 5 5 3 0 2 0 0 . . 4 5 5 1 1 5
720 0.453 0.439 0.457 0.440 0.447 0.437 0.481 0.445 0.487 0.463 0.487 0.456 0.458 0.445 0.475 0.453 0.478 0.450 0.474 0.453 0.666 0.589
avg 0.379 0.393 0.384 0.397 0.379 0.396 0.412 0.410 0.400 0.412 0.405 0.410 0.385 0.399 0.396 0.406 0.400 0.406 0.403 0.407 0.513 0.495
96 0.173 0.253 0.176 0.261 0.174 0.255 0.186 0.270 0.182 0.266 0.185 0.271 0.178 0.259 0.193 0.280 0.187 0.267 0.193 0.292 0.287 0.366
ETTm2 1 3 9 3 2 6 0 0 . . 2 2 3 9 8 8 0 0 . . 2 3 9 3 8 9 0 0 . . 2 2 4 9 0 9 0 0 . . 3 3 0 4 2 2 0 0 . . 3 2 0 3 5 9 0 0 . . 2 3 9 4 9 3 0 0 . . 3 2 0 4 8 8 0 0 . . 3 3 4 0 4 7 0 0 . . 2 3 4 1 8 2 0 0 . . 3 3 4 0 6 6 0 0 . . 3 2 1 5 4 1 0 0 . . 3 3 1 5 2 0 0 0 . . 3 2 0 4 4 2 0 0 . . 3 3 4 0 2 3 0 0 . . 2 3 4 1 6 4 0 0 . . 3 3 5 0 1 7 0 0 . . 3 2 2 4 1 9 0 0 . . 3 3 0 5 9 1 0 0 . . 3 2 6 8 9 4 0 0 . . 4 3 2 6 7 2 0 0 . . 4 5 1 9 4 7 0 0 . . 5 4 4 9 2 2
720 0.395 0.395 0.397 0.401 0.399 0.400 0.409 0.400 0.414 0.404 0.411 0.405 0.395 0.397 0.410 0.405 0.408 0.403 0.554 0.522 1.730 1.042
avg 0.276 0.321 0.278 0.327 0.279 0.324 0.288 0.330 0.289 0.330 0.290 0.335 0.280 0.325 0.291 0.336 0.291 0.333 0.350 0.401 0.757 0.611
96 0.147 0.240 0.166 0.256 0.174 0.266 0.179 0.262 0.165 0.274 0.148 0.240 0.153 0.244 0.188 0.280 0.168 0.272 0.197 0.282 0.219 0.314
Electricity 1 3 9 3 2 6 0 0 . . 1 1 6 7 2 7 0 0 . . 2 2 5 6 3 9 0 0 . . 1 2 8 0 7 4 0 0 . . 2 2 7 9 4 0 0 0 . . 1 1 8 9 2 7 0 0 . . 2 2 7 8 3 6 0 0 . . 1 2 8 0 6 2 0 0 . . 2 2 6 8 9 5 0 0 . . 1 1 8 9 5 7 0 0 . . 2 3 9 0 2 4 0 0 . . 1 1 6 7 2 8 0 0 . . 2 2 5 6 3 9 0 0 . . 1 1 6 8 6 4 0 0 . . 2 2 5 7 6 5 0 0 . . 1 2 9 1 3 1 0 0 . . 2 3 8 0 5 2 0 0 . . 1 1 8 9 4 8 0 0 . . 2 3 8 0 9 0 0 0 . . 1 2 9 0 6 9 0 0 . . 2 3 8 0 5 1 0 0 . . 2 2 3 4 1 6 0 0 . . 3 3 2 3 2 7
720 0.209 0.298 0.247 0.323 0.236 0.320 0.247 0.321 0.231 0.332 0.225 0.317 0.226 0.313 0.253 0.335 0.220 0.320 0.245 0.333 0.280 0.363
avg 0.174 0.265 0.201 0.286 0.197 0.286 0.204 0.284 0.194 0.301 0.178 0.270 0.182 0.272 0.211 0.301 0.193 0.295 0.212 0.300 0.244 0.334
96 0.083 0.202 0.089 0.208 0.084 0.203 0.098 0.232 0.102 0.230 0.088 0.209 0.087 0.206 0.090 0.211 0.107 0.234 0.088 0.218 0.139 0.265
Exchange 1 3 9 3 2 6 0 0 . . 1 32 6 2 8 0 0 . . 4 2 1 9 1 2 0 0 . . 3 1 4 8 9 3 0 0 . . 4 3 3 0 1 2 0 0 . . 3 1 7 8 4 7 0 0 . . 4 3 4 0 1 7 0 0 . . 3 2 5 0 5 2 0 0 . . 4 3 3 2 3 4 0 0 . . 3 1 5 9 9 5 0 0 . . 4 3 3 1 6 7 0 0 . . 3 1 3 8 6 3 0 0 . . 4 3 1 0 8 8 0 0 . . 1 3 9 4 3 5 0 0 . . 3 4 1 2 0 5 0 0 . . 3 1 3 8 9 6 0 0 . . 3 4 0 2 7 4 0 0 . . 2 3 2 6 6 7 0 0 . . 4 3 4 4 8 4 0 0 . . 3 17 1 6 3 0 0 . . 3 4 1 2 5 7 0 0 . . 3 2 9 4 2 1 0 0 . . 4 3 6 7 8 5
720 0.838 0.684 0.880 0.707 0.972 0.739 0.896 0.718 0.940 0.738 0.893 0.714 1.008 0.747 0.898 0.718 0.964 0.746 0.839 0.695 1.110 0.802
avg 0.353 0.397 0.375 0.412 0.404 0.423 0.388 0.427 0.399 0.430 0.375 0.412 0.408 0.422 0.378 0.415 0.416 0.443 0.354 0.414 0.471 0.478
96 0.187 0.234 0.216 0.298 0.231 0.288 0.286 0.295 0.210 0.246 0.203 0.238 0.215 0.294 0.234 0.286 0.250 0.292 0.290 0.378 0.310 0.331
Solar-Energy 1 3 9 3 2 6 0 0 . . 2 2 0 1 5 3 0 0 . . 2 2 5 7 6 1 0 0 . . 2 2 4 6 1 3 0 0 . . 2 3 8 0 2 4 0 0 . . 2 3 9 2 0 6 0 0 . . 3 3 2 4 3 5 0 0 . . 3 3 2 6 3 4 0 0 . . 3 3 1 3 8 9 0 0 . . 2 2 6 9 5 4 0 0 . . 2 3 9 1 0 8 0 0 . . 2 2 3 4 3 8 0 0 . . 2 2 6 7 1 3 0 0 . . 2 2 3 5 7 2 0 0 . . 2 2 7 9 5 8 0 0 . . 2 2 6 9 7 0 0 0 . . 3 3 1 1 0 5 0 0 . . 2 3 9 1 6 9 0 0 . . 3 3 1 3 8 0 0 0 . . 3 3 2 5 0 3 0 0 . . 3 4 9 1 8 5 0 0 . . 7 7 3 5 4 0 0 0 . . 7 7 2 3 5 5
720 0.214 0.267 0.251 0.313 0.300 0.329 0.355 0.335 0.285 0.315 0.249 0.276 0.244 0.293 0.289 0.317 0.338 0.337 0.356 0.413 0.769 0.765
avg 0.205 0.257 0.243 0.299 0.287 0.321 0.332 0.322 0.263 0.292 0.233 0.262 0.237 0.290 0.270 0.307 0.301 0.319 0.330 0.401 0.641 0.639
96 0.173 0.213 0.164 0.210 0.161 0.208 0.170 0.217 0.163 0.212 0.174 0.214 0.165 0.212 0.177 0.218 0.172 0.220 0.196 0.255 0.158 0.230
Weather 1 3 9 3 2 6 0 0 . . 2 2 2 7 2 7 0 0 . . 2 2 5 9 7 6 0 0 . . 2 2 1 6 0 5 0 0 . . 2 25 9 1 0 0 0 . . 2 20 6 7 3 0 0 . . 2 29 4 0 9 0 0 . . 2 2 7 1 0 6 0 0 . . 2 2 5 9 7 4 0 0 . . 2 2 7 1 3 1 0 0 . . 2 2 9 5 9 4 0 0 . . 2 2 2 7 1 8 0 0 . . 2 2 9 5 6 4 0 0 . . 2 2 6 0 4 9 0 0 . . 2 2 5 9 3 3 0 0 . . 2 2 2 7 5 8 0 0 . . 2 2 9 5 7 9 0 0 . . 2 2 1 8 9 0 0 0 . . 2 3 6 0 1 6 0 0 . . 2 2 8 3 3 7 0 0 . . 2 3 9 3 6 5 0 0 . . 2 27 0 2 6 0 0 . . 2 3 7 3 7 5
720 0.351 0.346 0.343 0.342 0.340 0.341 0.348 0.344 0.351 0.348 0.358 0.347 0.342 0.345 0.354 0.348 0.365 0.359 0.345 0.381 0.398 0.418
avg 0.256 0.278 0.246 0.273 0.243 0.272 0.251 0.278 0.249 0.278 0.258 0.278 0.245 0.276 0.259 0.281 0.259 0.287 0.265 0.317 0.259 0.315
96 0.392 0.263 0.511 0.324 0.608 0.383 0.576 0.342 0.608 0.349 0.395 0.268 0.462 0.285 0.544 0.359 0.593 0.321 0.650 0.396 0.522 0.290
Traffic 1 3 9 3 2 6 0 0 . . 4 4 1 3 5 0 0 0 . . 2 2 7 7 3 9 0 0 . . 5 5 2 4 9 5 0 0 . . 3 3 3 3 0 4 0 0 . . 5 5 7 6 1 1 0 0 . . 3 3 6 6 4 4 0 0 . . 5 6 9 3 6 0 0 0 . . 3 3 6 7 1 1 0 0 . . 6 6 3 6 4 9 0 0 . . 3 3 7 8 1 8 0 0 . . 4 4 1 3 7 3 0 0 . . 2 2 7 8 6 3 0 0 . . 4 4 7 9 3 8 0 0 . . 2 2 9 9 6 6 0 0 . . 5 5 4 5 0 1 0 0 . . 3 3 5 5 4 8 0 0 . . 6 6 1 2 7 9 0 0 . . 3 3 3 3 6 6 0 0 . . 5 6 9 0 8 5 0 0 . . 3 3 7 7 0 3 0 0 . . 5 5 3 5 0 8 0 0 . . 2 3 9 0 3 5
720 0.463 0.297 0.580 0.351 0.619 0.385 0.667 0.390 0.729 0.420 0.467 0.302 0.506 0.313 0.586 0.375 0.640 0.350 0.645 0.394 0.589 0.328
avg 0.425 0.278 0.541 0.335 0.590 0.374 0.617 0.366 0.660 0.382 0.428 0.282 0.485 0.298 0.555 0.362 0.620 0.336 0.625 0.383 0.550 0.304
12 0.065 0.168 0.077 0.185 0.095 0.202 0.091 0.204 0.078 0.187 0.071 0.174 0.076 0.185 0.073 0.178 0.085 0.192 0.122 0.243 0.090 0.203
PEMS03 2 4 4 8 0 0 . . 0 1 8 2 6 3 0 0 . . 1 2 9 3 5 5 0 0 . . 1 1 1 8 9 4 0 0 . . 2 2 3 9 1 1 0 0 . . 1 1 3 8 8 0 0 0 . . 2 2 2 7 1 9 0 0 . . 1 1 1 5 3 3 0 0 . . 2 2 1 6 3 9 0 0 . . 1 1 0 7 8 8 0 0 . . 2 2 1 7 8 2 0 0 . . 0 1 9 2 3 5 0 0 . . 2 2 0 3 1 6 0 0 . . 1 1 1 8 2 1 0 0 . . 2 2 2 8 4 1 0 0 . . 1 1 0 5 5 9 0 0 . . 2 2 1 6 2 4 0 0 . . 1 1 1 5 8 5 0 0 . . 2 2 2 6 3 0 0 0 . . 2 3 0 3 1 3 0 0 . . 3 4 1 2 7 5 0 0 . . 1 2 2 0 1 2 0 0 . . 2 3 4 1 0 7
96 0.172 0.277 0.251 0.336 0.272 0.329 0.232 0.324 0.238 0.328 0.164 0.275 0.205 0.343 0.210 0.305 0.228 0.317 0.457 0.515 0.262 0.367
avg 0.112 0.219 0.158 0.261 0.171 0.258 0.147 0.253 0.150 0.251 0.113 0.221 0.144 0.258 0.137 0.240 0.147 0.248 0.278 0.375 0.169 0.281
12 0.076 0.178 0.096 0.205 0.102 0.202 0.092 0.208 0.086 0.199 0.078 0.183 0.091 0.203 0.085 0.189 0.087 0.195 0.148 0.272 0.098 0.218
PEMS04 2 4 4 8 0 0 . . 0 1 9 1 1 9 0 0 . . 1 2 9 3 9 1 0 0 . . 1 1 2 6 8 4 0 0 . . 2 3 4 0 7 9 0 0 . . 1 1 3 4 3 2 0 0 . . 2 2 4 7 1 1 0 0 . . 1 1 1 2 2 8 0 0 . . 2 2 5 4 3 7 0 0 . . 1 1 0 2 1 7 0 0 . . 2 2 1 4 8 7 0 0 . . 0 1 9 2 5 0 0 0 . . 2 2 0 3 5 3 0 0 . . 1 1 2 9 9 9 0 0 . . 2 3 4 0 3 3 0 0 . . 1 1 1 6 5 7 0 0 . . 2 2 2 7 2 3 0 0 . . 1 1 0 3 3 6 0 0 . . 2 2 1 5 5 0 0 0 . . 2 3 2 5 4 5 0 0 . . 3 4 4 3 0 7 0 0 . . 1 2 3 0 1 5 0 0 . . 2 3 5 2 6 6
96 0.150 0.262 0.221 0.355 0.214 0.321 0.163 0.286 0.174 0.292 0.150 0.262 0.223 0.338 0.211 0.310 0.190 0.303 0.452 0.504 0.402 0.457
avg 0.109 0.218 0.152 0.279 0.148 0.259 0.124 0.249 0.122 0.239 0.111 0.221 0.161 0.272 0.145 0.249 0.129 0.241 0.295 0.388 0.209 0.314
12 0.058 0.153 0.072 0.174 0.083 0.196 0.073 0.186 0.079 0.182 0.067 0.165 0.069 0.175 0.068 0.163 0.082 0.181 0.115 0.242 0.094 0.200
PEMS07 2 4 4 8 0 0 . . 0 1 7 0 6 6 0 0 . . 1 2 7 1 6 1 0 0 . . 1 1 1 6 7 9 0 0 . . 2 2 2 4 2 6 0 0 . . 1 1 0 7 1 2 0 0 . . 2 2 1 6 1 4 0 0 . . 1 1 1 6 0 5 0 0 . . 2 2 0 6 9 4 0 0 . . 0 1 9 3 9 3 0 0 . . 2 2 0 3 6 9 0 0 . . 0 1 8 1 8 0 0 0 . . 1 2 9 1 0 5 0 0 . . 1 1 0 7 7 5 0 0 . . 2 2 1 7 6 2 0 0 . . 1 1 0 7 2 0 0 0 . . 2 2 0 6 1 1 0 0 . . 1 1 0 3 1 4 0 0 . . 2 2 0 3 4 8 0 0 . . 2 3 1 9 0 8 0 0 . . 3 4 2 5 9 8 0 0 . . 1 3 3 1 9 1 0 0 . . 2 3 4 6 7 9
96 0.132 0.241 0.192 0.291 0.199 0.289 0.268 0.328 0.179 0.279 0.139 0.245 0.295 0.350 0.236 0.308 0.181 0.279 0.594 0.553 0.396 0.442
avg 0.093 0.195 0.138 0.233 0.139 0.240 0.154 0.247 0.122 0.227 0.101 0.204 0.162 0.253 0.144 0.233 0.124 0.225 0.329 0.395 0.235 0.315
12 0.076 0.175 0.088 0.191 0.103 0.217 0.095 0.202 0.105 0.211 0.079 0.182 0.093 0.202 0.098 0.205 0.112 0.212 0.154 0.276 0.165 0.214
PEMS08 2 4 4 8 0 0 . . 1 1 0 8 6 3 0 0 . . 2 25 0 1 6 0 0 . . 1 2 3 6 9 5 0 0 . . 2 3 4 0 3 2 0 0 . . 1 2 7 4 6 1 0 0 . . 2 3 8 2 7 9 0 0 . . 1 1 1 8 8 9 0 0 . . 2 2 3 8 1 5 0 0 . . 1 2 4 1 1 1 0 0 . . 2 3 4 0 3 0 0 0 . . 1 1 1 8 5 6 0 0 . . 2 21 3 9 5 0 0 . . 1 2 4 8 8 0 0 0 . . 3 2 5 6 7 1 0 0 . . 1 2 6 3 2 8 0 0 . . 2 3 6 1 6 1 0 0 . . 1 1 9 4 8 1 0 0 . . 2 2 3 8 8 3 0 0 . . 2 4 4 4 8 0 0 0 . . 4 3 7 5 0 3 0 0 . . 2 3 1 1 5 5 0 0 . . 2 3 6 5 0 5
96 0.215 0.262 0.363 0.336 0.332 0.331 0.302 0.301 0.364 0.387 0.221 0.267 0.301 0.363 0.303 0.318 0.320 0.351 0.674 0.565 0.377 0.397
avg 0.145 0.224 0.214 0.268 0.213 0.291 0.176 0.255 0.205 0.285 0.150 0.226 0.206 0.296 0.200 0.275 0.193 0.271 0.379 0.416 0.268 0.307
2
1
0
1
0 25 50 75 100 125 150 175 200
Time
eulaV
Input
GroundTruth
Prediction 2
1
0
1
0 25 50 75 100 125 150 175 200
Time
(Time-TK)
eulaV
Input
GroundTruth
Prediction 2
1
0
1
0 25 50 75 100 125 150 175 200
Time
(TimeKAN)
eulaV
Input
GroundTruth
Prediction 2
1
0
1
0 25 50 75 100 125 150 175 200
Time
(iTransformer)
eulaV
Input
GroundTruth
Prediction
(PatchTST)
Figure8:TheperformanceofeachmodelisvisualizedandcomparedonthetrafficdatasetwithlookbackwindowL =96,
predictionwindowF =96.

WWW’26,April13–17,2026,Dubai,UnitedArabEmirates FanZhang,ShimingFan,andHuaWang
2
1
0
1
0 50 100 150 200 250 300
Time
eulaV
Input
GroundTruth
Prediction 2
1
0
1
0 50 100 150 200 250 300
Time
(Time-TK)
eulaV
Input
GroundTruth
Prediction 2
1
0
1
0 50 100 150 200 250 300
Time
(TimeKAN)
eulaV
Input
GroundTruth
Prediction 2
1
0
1
0 50 100 150 200 250 300
Time
(iTransformer)
eulaV
Input
GroundTruth
Prediction
(PatchTST)
Figure9:TheperformanceofeachmodelisvisualizedandcomparedonthetrafficdatasetwithlookbackwindowL =96,
predictionwindowF =192.
2
1
0
1
0 100 200 300 400
Time
eulaV
Input
GroundTruth
Prediction 2
1
0
1
0 100 200 300 400
Time
(Time-TK)
eulaV
Input
GroundTruth
Prediction 2
1
0
1
0 100 200 300 400
Time
(TimeKAN)
eulaV
Input
GroundTruth
Prediction 2
1
0
1
0 100 200 300 400
Time
(iTransformer)
eulaV
Input
GroundTruth
Prediction
(PatchTST)
Figure10:TheperformanceofeachmodelisvisualizedandcomparedonthetrafficdatasetwithlookbackwindowL=96,
predictionwindowF =336.
2
1
0
1
0 100 200 300 400 500 600 700 800
Time
eulaV
Input
GroundTruth
Prediction 2
1
0
1
0 100 200 300 400 500 600 700 800
Time
(Time-TK)
eulaV
Input
GroundTruth
Prediction 2
1
0
1
0 100 200 300 400 500 600 700 800
Time
(TimeKAN)
eulaV
Input
GroundTruth
Prediction 2
1
0
1
0 100 200 300 400 500 600 700 800
Time
(iTransformer)
eulaV
Input
GroundTruth
Prediction
(PatchTST)
Figure11:TheperformanceofeachmodelisvisualizedandcomparedonthetrafficdatasetwithlookbackwindowL=96,
predictionwindowF =720.
Table9:OverallforecastingperformanceofTime-TKand C MoreDetailsofTime-TK
TimeKANon10benchmarkdatasets.Wereportmean±stan-
ThisalgorithmdescribesthebasicprocessoftheTime-TKmodel.
darddeviationoverthreeruns. First,theinputtimeseriesX ∈R𝑁×LisnormalizedusingRevIN,re-
sultinginX𝑛.Then,theMulti-OffsetTemporalEmbedding(MOTE)
Time-TK TimeKAN methodisappliedtodividethenormalizeddataintomultiplesub-
Datasets
MSE MAE MSE MAE
sequenceswithdifferenttimeoffsets,{M
1
,...,𝑀
O
}.Thesesubse-
quencesarefurtherprocessedbytheMulti-OffsetInteractiveKAN
ETTh1 0.433±0.005 0.430±0.003 0.425±0.005 0.430±0.004 (MI-KAN)module,yielding{M′,...,𝑀′ }.Foreachsubsequence,a
ETTh2 0.371±0.004 0.399±0.005 0.389±0.002 0.408±0.003 1 O
ETTm1 0.380±0.004 0.395±0.004 0.381±0.005 0.397±0.004 Multi-HeadSelf-Attention(MSA)mechanismisappliedtocapture
ETTm2 0.276±0.002 0.321±0.003 0.281±0.003 0.327±0.003 interactions,resultinginA𝑖.Subsequently,theseinteractionresults
Electricity 0.175±0.005 0.270±0.004 0.198±0.003 0.288±0.002 arefusedwiththeoriginalsequenceXthroughaglobalMulti-Head
Solar-Energy 0.203±0.006 0.265±0.003 0.278±0.005 0.315±0.004 Self-AttentionoperationtogeneratethefinalrepresentationH.
Weather 0.255±0.003 0.278±0.002 0.244±0.005 0.273±0.003 Finally,thepredictorisappliedtoHtoobtainthepredictionYˆ,and
Traffic 0.425±0.004 0.278±0.002 0.593±0.003 0.378±0.005 theresultisdenormalizedviatheinverseReVINtoobtainthefinal
PEMS04 0.109±0.005 0.217±0.004 0.157±0.007 0.263±0.008 predictionoutputYˆ.Thealgorithmcontinuesuntilthestopping
PEMS08 0.149±0.005 0.232±0.006 0.217±0.004 0.293±0.006
criteriaaremet.

