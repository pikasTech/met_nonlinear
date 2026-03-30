# Page 1

5202
nuJ
92
]GL.sc[
1v42432.6052:viXra
Accurate Parameter-Efficient Test-Time Adaptation for Time Series Forecasting
HeitorR.Medeiros*12 HosseinSharifi-Noghabi1 GabrielL.Oliveira1 SagharIrandoust1
Abstract
Look-back Window Forecast Window
Real-world time series often exhibit a non- input time-series Par ( t P ia T l ) GT
stationarynature,degradingtheperformanceof input with lag
pre-trainedforecastingmodels. Test-TimeAdap-
tation(TTA)addressesthisbyadjustingmodels
duringinference,butexistingmethodstypically
Full GT (T)
update the full model, increasing memory and
computecosts. WeproposePETSA,aparameter-
Figure1.Illustration of the test-time adaptation setup in
efficient method that adapts forecasters at test
PETSA. The model observes a look-back window and makes
timebyonlyupdatingsmallcalibrationmodules
predictions over the forecast window. A partial portion of the
on the input and output. PETSA uses low-rank
groundtruth(PT)becomesavailableshortlyafterprediction(light
adaptersanddynamicgatingtoadjustrepresenta- yellow),whichisusedtoadaptthemodelonline.Fullgroundtruth
tionswithoutretraining. Tomaintainaccuracyde- (T) may also be observed after the forecast window completes
spitelimitedadaptationcapacity,weintroducea (shadedyellow).PETSAusesbothpartialanddelayedTtoupdate
specializedlosscombiningthreecomponents: (1) lightweightcalibrationmodulesduringinference. TheX isthe
arobustterm,(2)afrequency-domaintermtopre- time-seriesinput,andY isthesametime-serieswithalag,which
serveperiodicity,and(3)apatch-wisestructural canbepartiallyusedasgroundtruth.TheX t∗ istheinputattime
termforstructuralalignment. PETSAimproves t∗andthepartialbatchgoesuntilt∗+p t∗ timestep.
theadaptabilityofvariousforecastingbackbones
whilerequiringfewerparametersthanbaselines.
breaks,ordomainshifts,leadtoasignificantdegradationin
Experimentalresultsonbenchmarkdatasetsshow
accuracy(Kimetal.,2024;2025).
thatPETSAachievescompetitiveorbetterperfor-
manceacrossallhorizons. Ourcodeisavailable Test-TimeAdaptation(TTA)hasemergedasapromising
at: https://github.com/BorealisAI/ strategy to mitigate these shifts by updating models dur-
PETSA. inginference(Wangetal.,2020;Kimetal.,2025). How-
ever, most TTA methods either rely on access to source
data (Wang et al., 2020) or update the entire model (Hu
1.Introduction
etal.,2022),resultinginhighcomputationaloverhead. Fur-
thermore, limited information at test time makes reliable
Time series forecasting (TSF) plays a critical role in ap-
adaptationchallenging(Kimetal.,2024;Kudratetal.,2025)
plications such as weather prediction, traffic monitoring,
Inthispaper,weintroduceParameter-EfficientTime-Series
andfinancialmodeling(Wuetal.,2021;Zhouetal.,2021;
Adaptation (PETSA) framework (Figure 2), tailored for
Kudratetal.,2025). WhiledeeplearningmodelslikeTrans-
test-timeadaptationoftime-seriesforecasters.
formers and MLPs have significantly improved TSF per-
formance (Shabani et al., 2022; Wang et al., 2025), they Ourmaincontributionscanbesummarizedasfollows.
oftenassumestationarityandstrugglewhenthedatadistri-
(1)WeproposePETSA,atest-timeadaptationframework
butionshiftsovertime(Kimetal.,2025). Inpractice,such
thatcalibratesinputandoutputfeaturesusinglightweight
shifts,whicharenormallycausedbyseasonality,structural
low-rankadaptersanddynamicgating.
*WorkdoneduringaninternshipatBorealisAI.
(2) We design a unified PETSA loss combining Huber,
1BorealisAI,Montreal,Canada2Dept.ofSystemsEngineering,
frequency,andpatch-wisestructuraltermsforrobustand
ETSMontreal,Canada.Correspondenceto:HeitorR.Medeiros
<heitor.rapela-medeiros.1@ens.etsmtl.ca>. structure-awareadaptation.
(3) We benchmark PETSA across six datasets and show
SecondWorkshoponTest-TimeAdaptation: PuttingUpdatesto
theTest! atICML2025,Vancouver,Canada. 2025. Copyright thatitimprovesmultipleforecasterswhilemaintaininghigh
2025bytheauthor(s). efficiency.
1

---

# Page 2

AccurateParameter-EfficientTest-TimeAdaptationforTimeSeriesForecasting.
Parameter-Efficient Time Series Adaptation (PETSA)
Trainable parameters Frozen model Trainable parameters
Source
Forecaster
Test-time Calibrated Test-time Calibrated
Input Input Output Output
Dynamic Calibrating Dynamic Calibrating
Gating Output Gating Output
Figure2.PETSA.Attesttime,theinputX isfirstpassedthroughadynamicinputcalibrationmodulethatappliesagatedlow-rank
t
transformation.ThecalibratedinputX t caliisthenprocessedbyafrozenpre-trainedforecaster.ItsoutputYˆ t∗ isrefinedbyasimilaroutput
calibrationmoduletoproducethefinalpredictionYˆcali.Onlythecalibrationmodulesareupdatedduringtest-timeadaptationusingthe
t∗
PETSAlosswithpartiallyandfullyobservedgroundtruthavailablewithadelay.Moduleswithtrainableparametershaveafireicon,
whilefrozenoneshaveaniceicon.
2.RelatedWorks 3.ProposedMethod
Time-SeriesForecasting(TSF).RecentTSFmodelsspan 3.1.PreliminaryDefinitions
Transformers,linearprojections,andMLP-basedforecast-
TSF.TSFinvolvespredictingfuturevaluesofasequence
ers. Transformer-based models like iTransformer (Liu
basedonhistoricalobservations.Formally,givenahistorical
et al., 2024b) and PatchTST (Nie et al., 2023) capture
multivariate time series X = {x ,x ,...,x }
long-rangedependenciesthroughself-attention,whilelin- t−L t−L+1 t−1
consistingofLconsecutiveobservations,thegoalofTSF
ear approaches such as DLinear (Zeng et al., 2023) and
istolearnaforecastingmodelf (·)thatgeneratesaccurate
OLS(Toner&Darlow,2024)offercompetitiveperformance θ
predictions of the next T future steps, denoted as: Y =
withlowercomplexity. MLP-basedmethodslikeFreTS(Yi
{x ,x ,...,x }=f (X).
etal.,2023)andMICN(Wangetal.,2023)balanceexpres- t t+1 t+T−1 θ
siveness and efficiency using global/local mixing. These TTAinTSF.InTSF,TTAmitigatesdistributionshiftsby
modelshighlightthetrade-offbetweenaccuracyandcom- updating the model using only test inputs. Methods like
putationalcostinTSF. TAFASassumethatpartialgroundtruthbecomesavailable
shortlyafterprediction,enablingonlineupdates.Theadapta-
Parameter-Efficient Fine-Tuning (PEFT). PEFT tech-
tionwindowisdefinedusingthedominantperiod,estimated
niquesadaptlargemodelsusingasmallnumberoftunable
viaFastFourierTransform(FFT).PETSAadoptsthissetup,
parameters. Popular strategies include LoRA (Hu et al.,
usingbothpartialandfulllabelstoupdateitslightweight
2022),DoRA(Liuetal.,2024a),andvisualadapterslike
gatingmodulesduringinference,sameasinTAFAS(Kim
VPT(Jiaetal.,2022)orAdaptFormer(Chenetal.,2022).
etal.,2025).
WhilePEFThasseenwideuseinvisionandNLP,recent
effortsextendtoTSF(Guptaetal.,2024;Ruanetal.,2024;
3.2.PETSA
Nieetal.,2024). However,existingmethodsmainlyfocus
onfine-tuninganddonotaddresstest-timeadaptation. We propose Parameter-Efficient Time-Series Adaptation
(PETSA),alightweightframework,designedtoadapttime-
Test-Time Adaptation (TTA). TTA enables models to
seriesforecastingmodelsatinferencewithoutmodifying
adapttodistributionshiftsduringinferenceusingunlabeled
thecoremodelparameters. Itintroducesinputandoutput
data (Zhao et al., 2023; Liang et al., 2025). Techniques
calibration modules that leverage low-rank adapters and
like TENT (Wang et al., 2020), LAME (Boudiaf et al.,
dynamicgatingmechanismstocorrectfordistributionshifts.
2022), and entropy minimization update model statistics
DynamicCalibrationMechanism. Attesttime,PETSA
oroutputs. InTSF,TAFAS(Kimetal.,2025)introduces
calibratesboththeinputandoutputofafrozenforecaster
a batch-level adaptation scheme using delayed partial la-
using lightweight low-rank adapters and dynamic gating,
bels. PETSAbuildsonthislinebyintroducingaparameter-
inspired by Dynamic Tanh (DyT) (Zhu et al., 2025) and
efficient,gating-basedarchitecturewithspecializedlosses
TAFAS.Thecalibratedinput(Xˆcali)andcalibratedoutput
forrobustandstructuredtest-timeadaptation. t∗
(Yˆcali)arecomputedasfollows:
t∗
2

---

# Page 3

AccurateParameter-EfficientTest-TimeAdaptationforTimeSeriesForecasting.
Table1.MSE across datasets and window sizes. The input training sequence length is set to 96 for all baselines. Results for ✗-
checkpoint,TF-TAFAS,andPETSA-PT.ThelowerMSEismarkedinbold.Additionally,weprovidedarow-counter(RW),which
countsthewinnerforeachrow,meaningthebestforthewindowlengthonthedatasetamongallmodels,andacolumn-counter(CW),
withthewinnerpermodel,andthetotalsumofcolumnwinners.
Transformer-based Linear-based MLP-based Counter
Models iTransformer PatchTST DLinear OLS FreTS MICN RW
Wind. ✗ TF PT ✗ TF PT ✗ TF PT ✗ TF PT ✗ TF PT ✗ TF PT TF PT
96 0.449 0.435 0.432 0.433 0.426 0.426 0.470 0.462 0.459 0.451 0.442 0.440 0.446 0.440 0.438 0.520 0.493 0.493 2 6
192 0.510 0.503 0.501 0.491 0.482 0.481 0.521 0.512 0.511 0.505 0.492 0.492 0.502 0.494 0.492 0.591 0.560 0.559 1 6
1hTTE
336 0.564 0.562 0.561 0.555 0.546 0.543 0.566 0.560 0.555 0.551 0.542 0.538 0.554 0.548 0.547 0.665 0.632 0.643 1 5
720 0.702 0.663 0.659 0.706 0.680 0.680 0.712 0.682 0.679 0.700 0.666 0.650 0.718 0.687 0.688 0.904 0.792 0.785 2 5
Avg 0.557 0.541 0.538 0.546 0.533 0.532 0.567 0.554 0.551 0.552 0.535 0.530 0.555 0.542 0.541 0.670 0.619 0.620 1 5
96 0.439 0.416 0.413 0.451 0.437 0.436 0.444 0.417 0.414 0.444 0.416 0.415 0.433 0.421 0.416 0.487 0.458 0.456 0 6
192 0.508 0.476 0.473 0.504 0.486 0.489 0.518 0.480 0.474 0.518 0.479 0.475 0.501 0.482 0.475 0.554 0.511 0.510 1 5
1mTTE
336 0.613 0.556 0.552 0.558 0.539 0.542 0.593 0.549 0.545 0.593 0.548 0.543 0.570 0.547 0.543 0.612 0.579 0.573 1 5
720 0.485 0.453 0.450 0.479 0.463 0.465 0.482 0.449 0.446 0.481 0.449 0.446 0.468 0.452 0.448 0.525 0.486 0.484 1 5
Avg 0.257 0.255 0.254 0.236 0.235 0.235 0.232 0.230 0.230 0.231 0.228 0.228 0.239 0.236 0.236 0.256 0.252 0.252 5 6
96 0.344 0.330 0.328 0.317 0.308 0.309 0.325 0.319 0.318 0.326 0.319 0.318 0.332 0.321 0.321 0.359 0.339 0.342 3 4
192 0.424 0.396 0.397 0.433 0.402 0.402 0.409 0.387 0.385 0.416 0.391 0.388 0.412 0.383 0.383 0.437 0.439 0.434 3 5
2hTTE
336 0.332 0.320 0.319 0.318 0.305 0.305 0.313 0.305 0.305 0.314 0.305 0.304 0.317 0.306 0.306 0.345 0.334 0.335 4 5
720 0.168 0.167 0.166 0.160 0.160 0.160 0.160 0.158 0.158 0.160 0.159 0.159 0.158 0.157 0.157 0.175 0.175 0.176 5 5
Avg 0.220 0.217 0.215 0.207 0.204 0.204 0.193 0.191 0.191 0.194 0.192 0.192 0.192 0.191 0.191 0.213 0.209 0.203 4 6
96 0.339 0.330 0.322 0.334 0.327 0.328 0.306 0.297 0.296 0.307 0.298 0.298 0.301 0.292 0.293 0.332 0.322 0.320 3 4
192 0.250 0.244 0.241 0.237 0.235 0.235 0.223 0.219 0.219 0.223 0.220 0.220 0.221 0.217 0.218 0.243 0.238 0.236 4 5
2mTTE
336 0.087 0.085 0.086 0.086 0.082 0.083 0.091 0.089 0.088 0.081 0.080 0.078 0.083 0.079 0.079 0.115 0.115 0.109 3 4
720 0.181 0.174 0.175 0.188 0.174 0.179 0.183 0.176 0.173 0.173 0.164 0.165 0.173 0.164 0.163 0.216 0.198 0.198 4 3
Avg 0.343 0.313 0.335 0.338 0.281 0.332 0.328 0.294 0.292 0.323 0.285 0.281 0.324 0.295 0.298 0.398 0.304 0.280 3 3
96 0.366 0.345 0.341 0.372 0.353 0.367 0.372 0.359 0.357 0.353 0.294 0.286 0.354 0.335 0.327 0.558 0.307 0.357 2 4
192 0.173 0.166 0.166 0.173 0.170 0.171 0.195 0.180 0.176 0.196 0.181 0.178 0.186 0.175 0.174 0.176 0.175 0.174 2 5 egnahcxE
336 0.223 0.211 0.212 0.220 0.214 0.216 0.240 0.224 0.223 0.241 0.222 0.223 0.231 0.215 0.218 0.224 0.217 0.220 5 1
720 0.281 0.261 0.265 0.276 0.265 0.268 0.292 0.271 0.271 0.292 0.271 0.273 0.284 0.264 0.266 0.281 0.269 0.268 5 2
Avg 0.355 0.339 0.341 0.355 0.337 0.336 0.364 0.350 0.345 0.364 0.344 0.346 0.360 0.340 0.344 0.353 0.347 0.345 3 3
96 0.173 0.166 0.166 0.173 0.170 0.171 0.195 0.180 0.176 0.196 0.181 0.178 0.186 0.175 0.174 0.176 0.175 0.174 2 5
192 0.223 0.211 0.212 0.220 0.214 0.216 0.240 0.224 0.223 0.241 0.222 0.223 0.231 0.215 0.218 0.224 0.217 0.220 5 1 rehtaeW
336 0.281 0.261 0.265 0.276 0.265 0.268 0.292 0.271 0.271 0.292 0.271 0.273 0.284 0.264 0.266 0.281 0.269 0.268 5 2
720 0.355 0.339 0.341 0.355 0.337 0.336 0.364 0.350 0.345 0.364 0.344 0.346 0.360 0.340 0.344 0.353 0.347 0.345 3 3
Avg 0.258 0.244 0.246 0.256 0.247 0.248 0.273 0.256 0.254 0.273 0.255 0.255 0.265 0.248 0.251 0.258 0.252 0.252 5 3
✗ TF PT ✗ TF PT ✗ TF PT ✗ TF PT ✗ TF PT ✗ TF PT
Counter CW 13 19 24 14 7 30 14 23 18 19 12 22
SumCol. TF:88 PT:127
follows:
Xˆcali =X +(tanh(α⊙X )·W +b)
t∗ t∗ t∗
(cid:16) (cid:17) (1)
Yˆcali =Yˆ + tanh(α⊙Yˆ )·W +b ,
t∗ t∗ t∗ (cid:40) 0.5(Yˆcali−Y )2,if|Yˆcali−Y |<δ
L = t∗ t∗ t∗ t∗ (2)
where X t∗ ∈ RB×L×V and Yˆ t∗ ∈ RB×L×V are the test- Hub δ·(|Yˆ t c ∗ ali−Y t∗ |−0.5·δ),otherwise.
timeinputandoutputrespectively,α ∈ RV isalearnable
gatingparameterpervariable(wecontroltheinitialization where δ is a hyperparameter to control the sensitivity to
withahyperparameter),appliedelement-wise,W =A·B, outliers and smoothness of the predictions (in this work,
with A ∈ RL×r, B ∈ Rr×L×V forming the low-rank δ isfixedat0.5), (2)afrequency-domainloss(L )that
freq
weighttensor,b∈RL×Visalearnablebiasterm(Aisini- alignstheFFTspectraofpredictionsandgroundtruthto
tializedwithXavierNorm. andBwithzeros). Thisenables preserveperiodicpatterns,whilereducingestimationbias,
PETSAtoefficientlycalibratetime-seriesrepresentations as described in FreDF (Wang et al., 2025), described as
byupdatingonlyasmallnumberofparametersattesttime. follows:
PETSA Optimization. PETSA uses a combination of
(cid:13) (cid:13)
different losses, while TAFAS only uses MSE loss. Our L =(cid:13)F(Yˆcali)−F(Y )(cid:13) , (3)
freq (cid:13) t∗ t∗ (cid:13)
PETSAlosscombinestotalandpartiallosses(L = 1
PETSA
L + L ) , where L is computed using delayed full
T pt T
ground-truth labels and L uses partially observed la- whereF(.) = FFT, and(3)apatch-wisestructural loss
pt
bels(Kimetal.,2025). Eachlosstermincorporatesthree (L )thatcaptureslocalcorrelations,means,andvariances
pw
components: (1) a Huber loss (L ) (Huber, 1992) for to enhance structural alignment (Kudrat et al., 2025), de-
Hub
robustnesstooutliers(Shabanietal.,2022), describedas scribedasfollows:
3

---

# Page 4

AccurateParameter-EfficientTest-TimeAdaptationforTimeSeriesForecasting.
L = (cid:88) L (Yˆcali,Y ). (4) pw k t∗ t∗
k∈{corr,mean,var}
Finally, the partial (PT) and delayed GT (T) loss are de-
scribedasfollows:
L =L +L +βL (5)
pt Hubpt pwpt freqpt
L =L +L +βL . (6) T HubT pwT freqT
To the best of our knowledge, this is the first work to do
parameter-efficientTTAforTSF.Byupdatingonlyasmall
setofcalibrationparametersattesttime,PETSAenables
fast,stable,andmemory-efficientadaptationacrossawide
rangeofforecastingmodelsanddatasets.
Best-Value Count by Window Length: TF vs PT
30
25
20
15
10
5
0
tnuoC
tseB
latoT
0.70 0.65
0.60
0.55
0.50
0.45
1e6
3.5 14.00MB
3.0
2.5
2.0 33.6x
1.5
1.0 3.00MB
0.5 0.50MB 1.25M 0 B .15MB 14.8 0 x .22MB 0.42MB
0.0 0.10MB
96
TAFAS
PETSA
96 192 336 720 Avg
Window Length
Figure3.Totalnumberofbest-valuewinsgroupedbywindow
lengthforTAFASandPETSAapproaches.PETSAconsistently
outperformsTAFASacrossallhorizons.
4.Experiments
4.1.ExperimentalProtocol
(a) Datasets: We demonstrate the effectiveness of our
method,PETSA,usingwidelyusedmultivariateTSFbench-
markdatasets: ETTh1,ETTm1,ETTh2,ETTm2,Exchange,
andWeather(Wuetal.,2021;Zhouetal.,2021).
(b)ImplementationDetails: Ourframeworkisbuiltontop
ofTAFAS(Kimetal.,2025). WeusedPyTorchforPETSA
implementation, andtraining/adaptthemodelsusingone
NVIDIAA100.
(c)Baselines: Weevaluateourproposedmethodagainsta
diversesetofbaselinemodels,groupedintothreemaincate-
gories: (1)Transformer-basedapproaches,includingiTrans-
former (Liu et al., 2024b), PatchTST (Nie et al., 2023);
(2)Linear-basedmodels,comprisingDLinear(Zengetal.,
2023),OLS(Toner&Darlow,2024),and(3)MLP-based
influential architectures, such as FreTS (Yi et al., 2023),
MICN (Wang et al., 2023). Additionally, we provide the
methodswithoutandwithadaptationusingTAFAS(Kim
etal.,2025)andPETSA.Weprovideadditionaldetailsin
theAppendix.
ESM
sretmaraP
fo rebmuN
MSE vs. Window Size (ETTh1)
iTransformer TAFAS PETSA (R=16)
Parameters vs. Window Size (ETTh1)
TAFAS Parameters PETSA Parameters (R=16)
192 Window Size 336 720
Figure4.Comparison of PETSA and TAFAS on ETTh1 for
iTransformer.Top:MSEacrossdifferentwindowsizeswithno
adaptation,TAFAS,andPETSA.Bottom: Numberoftrainable
parametersusedforadaptation.PETSAachievessimilarorbetter
accuracywhileusingupto33.6×fewerparametersatwindow
size720.MemoryusageisannotatedinMB.
4.2.Results
InTable1,acrossalldatasetsandmodelcategories,PETSA
achievesthehighestnumberofbest-MSEscores(127wins),
outperformingTAFAS(88wins). Itsconsistentadvantage
acrosstransformer-,linear-,andMLP-basedarchitectures
demonstrates strong adaptability, where all PETSA mod-
elshadfewerparametersthanTAFAS.Figure3showsthat
PETSAachievesmorebest-valuescoresthanTAFASacross
different window lengths. Even as the forecast window
increases,PETSAmaintainsastronglead,demonstrating
robustnesstolonger-termuncertainty. InFigure4,PETSA
achievesconsistentlylowerMSEacrossallwindowsizes,
andforwindowsize720,ithas33×fewerparametersthan
TAFAS,highlightingitsefficiencyduetothelow-rankadap-
tationwithdynamicgating,whichisinputconditionedand
morerobusttooutliersinlong-rangeforecastingasaresult
ofitslossoptimization.
5.Conclusion
In this work, we introduced PETSA, a lightweight,
parameter-efficienttest-timeadaptationframeworkfortime-
seriesforecastingthatdynamicallycorrectsbothinputsand
outputs via gated calibration modules. PETSA test-time
calibrationlosscombinesarobustcomponent,afrequency-
domaintermtopreservedominantperiodicpatterns,anda
patch-wisestructuraltermtoenforcestructuralalignment,
whichareessentialtoadapttheforecasterduringtest-time.
Acrossdiversebenchmarks,PETSAconsistentlyimproves
forecastingperformancewhileupdatingfewerparameters
againstbaselines.
4

---

# Page 5

AccurateParameter-EfficientTest-TimeAdaptationforTimeSeriesForecasting.
References Nie, T., Mei, Y., Qin, G., Sun, J., and Ma, W. Channel-
awarelow-rankadaptationintimeseriesforecasting. In
Boudiaf,M.,Mueller,R.,BenAyed,I.,andBertinetto,L.
Proceedingsofthe33rdACMInternationalConference
Parameter-freeonlinetest-timeadaptation. InProceed-
onInformationandKnowledgeManagement,pp.3959–
ingsoftheIEEE/CVFConferenceonComputerVision
3963,2024.
andPatternRecognition,pp.8344–8353,2022.
Nie,Y.,Nguyen,N.H.,Sinthong,P.,andKalagnanam,J. A
Chen, S., Ge, C., Tong, Z., Wang, J., Song, Y., Wang, J.,
timeseriesisworth64words:Long-termforecastingwith
and Luo, P. Adaptformer: Adapting vision transform-
transformers. InTheEleventhInternationalConference
ersforscalablevisualrecognition. AdvancesinNeural
onLearningRepresentations,2023.
InformationProcessingSystems,35:16664–16678,2022.
Ruan, W., Chen, W., Dang, X., Zhou, J., Li, W., Liu, X.,
Gupta, D., Bhatti, A., Parmar, S., Dan, C., Liu, Y., Shen,
andLiang,Y. Low-rankadaptationforspatio-temporal
B.,andLee,S. Low-rankadaptationoftimeseriesfoun-
forecasting. arXivpreprintarXiv:2404.07919,2024.
dationalmodelsforout-of-domainmodalityforecasting.
InProceedingsofthe26thInternationalConferenceon
Shabani, A., Abdi, A., Meng, L., and Sylvain, T. Scale-
MultimodalInteraction,pp.382–386,2024.
former: Iterative multi-scale refining transformers for
timeseriesforecasting. arXivpreprintarXiv:2206.04038,
Hu,E.J.,Shen,Y.,Wallis,P.,Allen-Zhu,Z.,Li,Y.,Wang,
2022.
S.,Wang,L.,Chen,W.,etal. Lora: Low-rankadaptation
oflargelanguagemodels. ICLR,1(2):3,2022.
Toner, W. and Darlow, L. N. An analysis of linear time
seriesforecastingmodels. InInternationalConference
Huber,P.J. Robustestimationofalocationparameter. In
onMachineLearning,pp.48404–48427.PMLR,2024.
Breakthroughsinstatistics: Methodologyanddistribu-
tion,pp.492–518.Springer,1992.
Wang,D.,Shelhamer,E.,Liu,S.,Olshausen,B.,andDarrell,
T. Tent: Fullytest-timeadaptationbyentropyminimiza-
Jia, M., Tang, L., Chen, B.-C., Cardie, C., Belongie, S.,
tion. arXivpreprintarXiv:2006.10726,2020.
Hariharan,B.,andLim,S.-N. Visualprompttuning. In
Europeanconferenceoncomputervision,pp.709–727.
Wang,H.,Peng,J.,Huang,F.,Wang,J.,Chen,J.,andXiao,
Springer,2022.
Y. Micn: Multi-scalelocalandglobalcontextmodeling
Kim,D.,Park,S.,andChoo,J. Whenmodelmeetsnewnor- forlong-termseriesforecasting. InTheeleventhinterna-
mals: test-timeadaptationforunsupervisedtime-series tionalconferenceonlearningrepresentations,2023.
anomalydetection. InProceedingsoftheAAAIconfer-
Wang,H.,Pan,L.,Chen,Z.,Yang,D.,Zhang,S.,Yang,Y.,
ence on artificial intelligence, volume 38, pp. 13113–
Liu,X.,Li,H.,andTao,D. Fredf: Learningtoforecast
13121,2024.
inthefrequencydomain. InICLR,2025.
Kim, H., Kim, S., Mok, J., and Yoon, S. Battling the
Wu,H.,Xu,J.,Wang,J.,andLong,M.Autoformer:Decom-
non-stationarityintimeseriesforecastingviatest-time
positiontransformerswithauto-correlationforlong-term
adaptation. arXivpreprintarXiv:2501.04970,2025.
seriesforecasting. Advancesinneuralinformationpro-
Kudrat,D.,Xie,Z.,Sun,Y.,Jia,T.,andHu,Q. Patch-wise cessingsystems,34:22419–22430,2021.
structurallossfortimeseriesforecasting. arXivpreprint
Yi, K., Zhang, Q., Fan, W., Wang, S., Wang, P., He, H.,
arXiv:2503.00877,2025.
An,N.,Lian,D.,Cao,L.,andNiu,Z. Frequency-domain
Liang,J.,He,R.,andTan,T. Acomprehensivesurveyon mlpsaremoreeffectivelearnersintimeseriesforecasting.
test-time adaptation under distribution shifts. Interna- AdvancesinNeuralInformationProcessingSystems,36:
tionalJournalofComputerVision,133(1):31–64,2025. 76656–76679,2023.
Liu, S.-Y., Wang, C.-Y., Yin, H., Molchanov, P., Wang, Zeng,A.,Chen,M.,Zhang,L.,andXu,Q.Aretransformers
Y.-C.F.,Cheng,K.-T.,andChen,M.-H. Dora: Weight- effectivefortimeseriesforecasting? InProceedingsof
decomposedlow-rankadaptation. InForty-firstInterna- theAAAIconferenceonartificialintelligence,volume37,
tionalConferenceonMachineLearning,2024a. pp.11121–11128,2023.
Liu,Y.,Hu,T.,Zhang,H.,Wu,H.,Wang,S.,Ma,L.,and Zhao, H., Liu, Y., Alahi, A., and Lin, T. On pitfalls of
Long,M. itransformer: Invertedtransformersareeffec- test-time adaptation. In Proceedings of the 40th Inter-
tivefortimeseriesforecasting. InTheTwelfthInterna- nationalConferenceonMachineLearning,pp.42058–
tionalConferenceonLearningRepresentations,2024b. 42080,2023.
5

---

# Page 6

AccurateParameter-EfficientTest-TimeAdaptationforTimeSeriesForecasting.
Zhou,H.,Zhang,S.,Peng,J.,Zhang,S.,Li,J.,Xiong,H., Appendix
andZhang,W.Informer:Beyondefficienttransformerfor
Hereweprovideadditionalinformationandresultsforour
longsequencetime-seriesforecasting. InProceedingsof
paper.
theAAAIconferenceonartificialintelligence,volume35,
pp.11106–11115,2021. Reproducingtheresults
Zhu, J., Chen, X., He, K., LeCun, Y., and Liu, Z. OurcodebaseisbuiltontopofTAFAS(Kimetal.,2025),
Transformers without normalization. arXiv preprint wherewefollowedtheirexperimentalsetupandhyperpa-
arXiv:2503.10622,2025. rametersforgeneratingthebaselinecheckpointmodelsand
adapted models. Additionally, for our method, we have
hyperparameterstocontrolthefrequencyloss,thenumber
oflow-rankparameters,andthegatinginitialization,where
weprovideadditionalablationsinthenextsession.
AdditionalresultsonParameter-Efficiency
InFigure5, PETSAandTAFASshowverysimilarMSE
resultsacrossallwindowsizesontheETTh1datasetusing
theOLSmodel. Bothmethodsfollowthesametrend,with
PETSAslightlyoutperformingTAFASatlargerwindows.
In terms of parameters, PETSA remains highly efficient,
using only 0.21 MB at window size 720, while TAFAS
requires3.70MB.Acrossallwindowsizes,PETSAkeeps
memoryusageconsistentlylowwhileachievingcomparable
orbetterperformance,highlightingitsparameterefficiency.
InFigure6,PETSAachievessimilarMSEtoTAFASacross
allwindowsizesonETTm1withOLS,withslightlybetter
results at short horizons. For a window of 720, we kept
thememorylowat0.11MB,whileTAFASrequired3.70.
Asthisdatasetiseasierthantheotherone,wehadagood
trade-offbetweenperformanceandmemory.
WehadsimilartrendsforFigures7andFigures8,weare
comparablewithTAFASintermsofMSE,andthememory
isalsolower. However,wecanseethatETTh1/ETTh2re-
quiresabitmorememorythanETTm1/ETTm2toachieve
competitive results. This trade-off happens due to the
factthatETTh1/ETTh2datasetsaremorechallengingthan
ETTm1/ETTm2;thus,morememoryisrequiredtoremain
performingwellintermsofMSEandstillbeingparameter
efficientcomparedtoTAFAS.
InFigure9,PETSAandTAFASshowsimilarMSEtrends
acrosswindowsizes,withbothmethodsdegradingasthe
horizonincreases. However,PETSArequiresover4×less
memorythanTAFASatwindowsize720,makingitamuch
more efficient alternative. Finally, in Figure 10, despite
similarperformance,PETSAsignificantlyreducestheadap-
tationcost,usinglessthanhalfofthememorycomparedto
TAFASatwindowsize720.
AblationonLow-Rank(R)parameter
Inthisablation,Figure11,weconductastudyaboutthelow-
rank hyperparameter, which directly impacts the number
ofadditionaltrainableparametersforthedynamicgating
mechanism.
6

---

# Page 7

AccurateParameter-EfficientTest-TimeAdaptationforTimeSeriesForecasting.
3.70 MB
3.5
3.0
0.60
2.5
2.0
0.55
1.5
0.50 1.0 0.86 MB
0.5 0.13 MB 0.32 MB
0.45
0.0 0.03 MB 0.03 MB 0.22 MB 0.21 MB
96 192 336 720 96 192 336 720
Window Size Window Size
ESM
)BM(
sretemaraP
fo
rebmuN
MSE vs. Window Size (ETTh1 - OLS) Parameters vs. Window Size (ETTh1 - OLS)
TAFAS TAFAS Parameters
0.65 PETSA PETSA Parameters
Figure5.ComparisonofPETSAandTAFASonETTh1forOLS.Left:MSEacrossdifferentwindowsizeswithTAFAS,andPETSA.
Right:Numberoftrainableparametersusedforadaptation.MemoryusageisannotatedinMB.
MSE vs. Window Size (ETTm1 - OLS) Parameters vs. Window Size (ETTm1 - OLS)
0.550 TAFAS Parameters
3.5 PETSA Parameters
0.525
3.0
0.500
2.5
0.475
2.0
0.450
0.425 1.5
0.400 1.0
0.375 0.5
0.350 0.0
ESM
)BM(
sretemaraP
fo
rebmuN
TAFAS 3.70 MB
PETSA
0.86 MB
0.32 MB
0.13 MB 0.04 MB 0.06 MB 0.11 MB
0.03 MB
96 192 336 720 96 192 336 720
Window Size Window Size
Figure6.ComparisonofPETSAandTAFASonETTm1forOLS.Left:MSEacrossdifferentwindowsizeswithTAFAS,andPETSA.
Right:Numberoftrainableparametersusedforadaptation.MemoryusageisannotatedinMB.
AblationonDynamicGatingparameter thatthefrequencycomponentharmedtheperformancefor
thisdataset, andβ = 0.0meansthatonlytheHuberloss
Inthisablation,Figure12,westudytheinitialvalueforthe
andstructuralpatchcomponentsarebeingused. Depending
dynamicgating. Thishyperparameterimpactstheweights
onthemodel,thefrequencylosshelpstheperformance;for
ofthelow-rankadaptation,providingalearnablewaycondi-
instance, the best performance for the FreTS model was
tionedontheinputtoadjustitsvalues;highervaluesmake
whentheβwasequalto0.1(forthemajorityofthedatasets
theweightspositiveduetothetanh;otherwise,lowervalues
andwindows). Forsomedatasets,ahighervaluecanbethe
maketheadaptedweightnegative,decreasingthevalueof
best result, so we recommend hyperparameter tuning for
thefinalcalibratedinput.
optimalperformance.
AblationonLossComponents
In this ablation, we study the impact of the loss compo-
nents for PETSA during TTA. In Figure 13, we see that
theMSElossisnotsufficientforreachingthebestperfor-
mancevaluesintermsoftestMSE,similartowhatoccurs
withonlyHuberloss. However,thetotallossgotthebest
resultsforETTh1OLSwithβ equalto0.0,whichmeans
7

---

# Page 8

AccurateParameter-EfficientTest-TimeAdaptationforTimeSeriesForecasting.
MSE vs. Window Size (ETTh2 - OLS) Parameters vs. Window Size (ETTh2 - OLS)
TAFAS Parameters
0.38 PETSA Parameters
0.36
0.34
0.32
0.30
0.28
0.26
0.24
ESM
)BM(
sretemaraP
fo
rebmuN
3.70 MB
0.86 MB
0.32 MB
0.13 MB 0.22 MB 0.11 MB
0.05 MB 0.04 MB
96 192 336 720 96 192 336 720
Window Size Window Size
Figure7.ComparisonofPETSAandTAFASonETTh2forOLS.Left:MSEacrossdifferentwindowsizeswithTAFAS,andPETSA.
Right:Numberoftrainableparametersusedforadaptation.MemoryusageisannotatedinMB.
MSE vs. Window Size (ETTm2 - OLS) Parameters vs. Window Size (ETTm2 - OLS)
0.30 TAFAS TAFAS Parameters
PETSA 3.5 PETSA Parameters
0.28
3.0
0.26
2.5
0.24
2.0
0.22
1.5
0.20
1.0
0.18 0.5
0.16 0.0
ESM
)BM(
sretemaraP
fo
rebmuN
3.70 MB
0.86 MB
0.32 MB 0.22 MB
0.13 MB 0.11 MB
0.04 MB
0.03 MB
96 192 336 720 96 192 336 720
Window Size Window Size
Figure8.ComparisonofPETSAandTAFASonETTm2forOLS.Left:MSEacrossdifferentwindowsizeswithTAFAS,andPETSA.
Right:Numberoftrainableparametersusedforadaptation.MemoryusageisannotatedinMB.
MSE vs. Window Size (exchange_rate - OLS) Parameters vs. Window Size (exchange_rate - OLS)
TAFAS Parameters
PETSA Parameters
ESM
)BM(
sretemaraP
fo
rebmuN
TAFAS 4.23 MB
0.6 PETSA 4
0.5
3
0.4
2
0.3
0.2 1 0.98 MB 0.95 MB
0.37 MB
0.15 MB 0.13 MB
0.1 0.03 MB 0.04 MB
0
96 192 336 720 96 192 336 720
Window Size Window Size
Figure9.ComparisonofPETSAandTAFASonExchangeRateforOLS.Left:MSEacrossdifferentwindowsizeswithTAFAS,and
PETSA.Right:Numberoftrainableparametersusedforadaptation.MemoryusageisannotatedinMB.
8

---

# Page 9

AccurateParameter-EfficientTest-TimeAdaptationforTimeSeriesForecasting.
MSE vs. Window Size (weather - OLS) Parameters vs. Window Size (weather - OLS)
0.350
TAFAS Parameters
PETSA Parameters
10
0.325
0.300 8
0.275
6
0.250
4
0.225
2
0.200
0.175 0
96 192 336 720
Window Size
ESM
)BM(
sretemaraP
fo
rebmuN
TAFAS 11.10 MB
PETSA
4.61 MB
2.57 MB
0.97 MB
0.39 MB
0.07 MB 0.21 MB 0.31 MB
96 192 336 720
Window Size
Figure10.ComparisonofPETSAandTAFASonWeatherforOLS.Left: MSEacrossdifferentwindowsizeswithTAFAS,and
PETSA.Right:Numberoftrainableparametersusedforadaptation.MemoryusageisannotatedinMB.
0.450
0.448
0.446
0.444
0.442
0.440
8 16 32 64 128
Rank
ESM
tseT
ETTh1 (Window=96) - OLS
0.504
0.502
0.500
0.498
0.496
0.494
0.492
8 16 32 64 128
Rank
ESM
tseT
ETTh1 (Window=192) - OLS
0.550
0.548
0.546
0.544
0.542
0.540
0.538
0.536
8 16 32 64 128
Rank
ESM
tseT
ETTh1 (Window=336) - OLS
0.70
0.69
0.68
0.67
0.66
0.65
8 16 32 64 128
Rank
ESM
tseT
OLS TAFAS PETSA
ETTh1 (Window=720) - OLS
Figure11.Comparisonoftheoriginalmodel,TAFAS,andPETSAonETTh1forOLS.MSEacrossdifferentranksforwindows96,
196,336,and720.
9

---

# Page 10

AccurateParameter-EfficientTest-TimeAdaptationforTimeSeriesForecasting.
0.450
0.448
0.446
0.444
0.442
0.440
0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
Gating Init Value
ESM
tseT
ETTh1 (Window=96) - OLS
0.504
0.502
0.500
OLS
TAFAS 0.498
PETSA
0.496
0.494
0.492
0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
Gating Init Value
ESM
tseT
ETTh1 (Window=192) - OLS
OLS
TAFAS
PETSA
0.552
0.550
0.548
0.546
0.544
0.542
0.540
0.538
0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.9 1.0
Gating Init Value
ESM
tseT
ETTh1 (Window=336) - OLS
0.70
0.69
0.68
0.67
0.66
OLS
TAFAS
PETSA 0.65
0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
Gating Init Value
ESM
tseT
ETTh1 (Window=720) - OLS
OLS
TAFAS
PETSA
Figure12.Comparisonoftheoriginalmodel,TAFAS,andPETSAonETTh1forOLS.MSEacrossdifferentgatinginitialvaluesfor
windows96,196,336,and720.
10

---

# Page 11

AccurateParameter-EfficientTest-TimeAdaptationforTimeSeriesForecasting.
0.4420
0.4417
0.4415
0.4413
0.4410
0.4407
0.4405
0.4403
0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
Beta ( in Loss)
ESM
tseT
ETTh1 (Window=96) - OLS
PETSA - MSE Loss 0.4945
PETSA - Huber Loss
PETSA - Huber + Pw
PETSA - Total Loss 0.4940
0.4935
0.4930
0.4925
0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
Beta ( in Loss)
ESM
tseT
ETTh1 (Window=192) - OLS
PETSA - MSE Loss
PETSA - Huber Loss
PETSA - Huber + Pw
PETSA - Total Loss
0.543
0.542
0.541
0.540
0.539
0.538
0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
Beta ( in Loss)
ESM
tseT
ETTh1 (Window=336) - OLS
0.662
0.660
0.658
PETSA - MSE Loss
PETSA - Huber Loss 0.656 PETSA - Huber + Pw
PETSA - Total Loss
0.654
0.652
0.650
0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
Beta ( in Loss)
ESM
tseT
ETTh1 (Window=720) - OLS
PETSA - MSE Loss
PETSA - Huber Loss
PETSA - Huber + Pw
PETSA - Total Loss
Figure13.ComparisonofdifferentlosstermsinPETSAonETTh1forOLS.MSEacrossdifferentbetavaluesforwindows96,196,
336,and720.
11