# Page 1

ThisarticlehasbeenpublishedinIEEEAccess.
DigitalObjectIdentifier10.1109/ACCESS.2025.3642613
Low-Complexity Frequency-Dependent
Linearizers Based on Parallel Bias-Modulus and
Bias-ReLU Operations
DEIJANYRODRIGUEZLINARES ,(GraduateStudentMember,IEEE),andHÅKAN
JOHANSSON ,(SeniorMember,IEEE)
DepartmentofElectricalEngineering,LinköpingUniversity,58183Linköping,Sweden
Correspondingauthor:DeijanyRodriguezLinares(e-mail:deijany.rodriguez.linares@liu.se).
Thisworkbelongstotheproject"BasebandProcessingforBeyond5GWireless",whichisfinanciallysupportedbyELLIIT.
ABSTRACT This paper introduces low-complexity frequency-dependent (memory) linearizers designed
to suppress nonlinear distortion in analog-to-digital interfaces. Two different linearizers are considered,
based on nonlinearity models which correspond to sampling before and after the nonlinearity opera-
tions, respectively. The proposed linearizers are inspired by convolutional neural networks but have an
order-of-magnitudelowerimplementationcomplexitycomparedtoexistingneural-network-basedlinearizer
schemes.TheproposedlinearizerscanalsooutperformthetraditionalparallelHammersteinlinearizerseven
whenthenonlinearitieshavebeengeneratedthroughaHammersteinmodel.Further,adesignprocedureis
proposedinwhichthelinearizerparametersareobtainedthroughmatrixinversion.Thiseliminatestheneed
forcostlyandtime-consumingiterativenonconvexoptimizationthatistraditionallyassociatedwithneural
networktraining.Thedesigneffectivelyhandlesawiderangeofwidebandmulti-tonesignalsandfiltered
white noise. Examples demonstrate significant signal-to-noise-and-distortion ratio (SNDR) improvements
ofabout20–30dB,aswellasalowerimplementationcomplexitythantheHammersteinlinearizers.
INDEX TERMS Analog-to-digital interfaces, nonlinear distortion, linearization, frequency-dependent
nonlinearsystems,pre-sampling,post-sampling.
I. INTRODUCTION In analog circuits, the ENOB is degraded by nonlinear-
Conversions between analog and digital signals constitute ities and linearization techniques are therefore required to
fundamental functions that will always be required, as the reachalargeENOBwhichisrequiredinmanyapplications.
physical world is analog by nature whereas the signal pro- Forinstance,decodinghigh-ordermodulationschemessuch
cessingisprimarilycarriedoutinthedigitaldomain.These as 1024–quadrature amplitude modulation (1024-QAM) re-
fundamental functions are implemented using analog-to- quires SNRs around 35dB [6]. High SNDR is also needed
digital converters (ADCs) and digital-to-analog converters for recovering weak signals that may otherwise be masked
(DACs) as well as other components required before/after bystronger ones,duetoanalog front-endnonlinearitiesand
the ADC/DAC, like filters, power amplifiers, and mixers. I/Q imbalance, where over 50dB distortion suppression is
Theoverallconvertersarereferredtoasanalog-to-digitaland typicallyrequired[7],[8].
digital-to-analog interfaces (ADIs and DAIs, respectively).
Linearizationcanhoweveralsobeutilizedforlow/medium
Withtheever-increasingdemandsforhigh-performanceand
ENOBs. For example, it enables the use of one- or few-bit
low-costsignalprocessingandcommunicationsystems,there
ADCs, with performance below the targeted ENOB which
is a need to develop ADIs and DAIs with higher perfor-
issubsequentlyachievedthroughdigitalprocessing.Thereby
manceintermsofdatarates(relatedtobandwidths),effective
the energy consumption of the ADCs can be reduced sub-
resolution [effective number of bits (ENOB) determined by
stantiallyastheirenergy consumptionisveryhighforlarge
the signal-to-noise-and-distortion ratio (SNDR)1], and low
ENOBs,especiallywhenthedatarateisalsohigh[9].Forex-
implementation cost (small chip area and low energy con-
ample,the12-bitADC12DJ5200SEfromTexasInstruments
sumption)[1]–[5].ThispaperfocusesonADIs.
[10],dissipatesapproximately4Wattsata10.4GS/sdatarate
1Forafull-scalesinusoidal,ENOB=(SNDR−1.76)/6.02. insingle-channelmode.Itisparticularlyimportanttoreduce
5202
ceD
32
]PS.ssee[
3v01261.2142:viXra

---

# Page 2

ThisarticlehasbeenpublishedinIEEEAccess.
theADCpowerinapplicationsrequiringmanyADCslikein thisconcernsfindingappropriatenonlinearmodels,whichis
massive-MIMOcommunicationsystems[1],[11].However, beyond the scope of this paper. Instead, the focus here is to
toreachthetargetedENOBwhilekeepingtheoverallenergy introduceanovellinearizer(explainedbelow)andshowthat
consumptionlow,itisvitaltodevelopenergy-efficientdigital it can outperform classical polynomial-based linearizers. To
linearizers2. this end, we have chosen the Hammerstein linearizer as the
The nonlinear errors can be suppressed by utilizing an benchmark, as it is more straightforward to design, and has
a-priori assumed system model and parameter/order iden- beenshowntobeappropriateformanypracticalcircuitsand
tification within the model. One can in principle use a systems[3],[24]–[26].Inparticular,itwillbedemonstrated
Volterra series and its inverse [12], but the identification thattheproposedlinearizercanoutperformtheHammerstein
and compensation may become very complex and pro- linearizer even when the nonlinearities have been generated
hibitive. Alternatively, aiming at a reduced complexity, one throughaHammersteinmodel.
may use specific structural system models [13], in partic- In the proposed novel linearizer (seen in Fig. 3 in Sec-
ular parallel linear-nonlinear-linear (LNL) structures which tion III), the nonlinearity terms vp(n) in the Hammerstein
includepolynomial-basedparallelHammerstein,Wiener,and linearizer are replaced by the simpler nonlinearities |v(n)|
Wiener-Hammersteinstructures.However,alsofortheseop- or max{0,v(n)} [rectified linear unit (ReLU)] as they can
tions, there is a need to find an appropriate system model beimplementedinhardwarewithlowcomplexity[27],[28].
for each new circuit and their complexity still tends to be In addition, bias values are added before the nonlinearities.
high. As an attempt to alleviate these problems, the use of The proposed linearizer is inspired by convolutional neural
neural-networkbasedlinearizershaveappearedasanalterna- networks,buttheneural-networkschemesthathaveappeared
tiveapproach,astheycanmodelhigh-dimensionalproblems earlierintheliteratureinthiscontexthaveaveryhighimple-
withoutexplicitanalyticalexpressions.However,theneural- mentation complexity as mentioned earlier. The implemen-
network schemes that have appeared so far in this context tation complexity of the proposed linearizer is an order-of-
typically have large design and implementation complexi- magnitude lower, primarily because it does not contain the
ties. The ADI linearization papers that exist have reported multiplelayersandinterconnectionsusedintraditionalneural
schemes for which several hundreds or even thousands of networks.Asmentionedabove,itwillalsobedemonstrated
multiplicationsarerequiredpercorrectedsample[14]–[22]. thatitcanoutperformtheHammersteinlinearizer.Further,a
For the Hammerstein linearizers (used as the benchmark in designprocedureisproposedinwhichtheparameters(filter
this paper, see below) and proposed linearizers, the number coefficients)areobtainedthroughmatrixinversion.Thereby,
of multiplications required is about an order of magnitude one can eliminate the costly and time-consuming iterative
lower, as the examples in the paper will demonstrate (see nonconvexoptimizationthatistraditionallyusedwhentrain-
Section III-C1). Further, compared with the Hammerstein ing neural networks. Moreover, the design and evaluation
linearizers, the proposed ones offer savings between a few incorporatealargesetofwidebandmulti-tonesignalsandfil-
percentuptoabout60percentdependingonthescenario(see teredwhitenoise.Inthepreviousworks[14]–[18],[20],[22],
SectionsIII-C1andIV-D1). theevaluationshaveonlyincludedsingle-toneandfew-tone
signals or narrowband multi-tone signals. Our simulations
A. CONTRIBUTIONANDRELATIONTOPREVIOUSWORKS showSNDRimprovementsuptoabout20–30dBforawide
rangeofwidebandsignalscoveringmostoftheNyquistband.
TraditionallinearizersbasedonparallelLNLsystemsutilize
linear filters and polynomial nonlinearity terms vp(n), for a It is noted here that the proposed linearizers are not limited
set of p-values, where v(n) is the distorted signal. Common to low- or high-resolution ADCs, but to investigate their
polynomiallinearizersaretheparallelHammersteinsystem3 distortion-suppressioncapabilities,thefocusintheexamples
isonhigherresolutions(10-12bits).
(seeninFig.2inSectionII),andthecorrespondingWiener
Aspecialcaseoftheproposedlinearizerisobtainedwhen
systemwhichisobtainedbyinterchangingthenonlinearities
thefiltersarereplacedwithsingleparameters,i.e.,0th-order
andfilters[13].Bothsystemsarewidelyused,andtheyhave
filters.Thiscorrespondstothememorylesslinearizerwhich
thesamecomplexityforthesamenumberofbranchesandfil-
we introduced in [28] and was shown to outperform the
terorder.Theyaregenerallynotequivalentthough(exceptfor
Hammerstein linearizer. The use of a memoryless linearizer
thememorylesscase),andthebestchoicedependsonthesys-
istypicallysufficientfornarrowtomediumbandwidthsand
temathandthatshouldbelinearized[23,Chapt.5].However,
resolutions.Toreachhigherresolutionsoverwiderfrequency
2There are trade-offs between analog and digital implementation com- bands,oneneedstoincorporatememory(filters)inthemod-
plexitiesforatargetedresolution(SNDRperformance),butsuchtrade-off eling and linearization which is in focus here. Hence, this
studiesarebeyondthescopeofthispaper.Theobjectivehereisto,given paper extends the memoryless linearizer in [28] to memory
nonlinearitiesemanatingfromanalogerrors,reducethecomplexityofthe
(frequencydependent)linearizersbyincorporatingarbitrary-
digitallinearization.Tothisend,thepaperintroducesnovellinearizerstruc-
turesanddemonstratesthroughextensivesimulationsthattheyofferlower orderfilters.
computationalcomplexitythanthebenchmarkHammersteinlinearizersfor Moreover, it is often assumed that the ADI nonlinearity
thesameSNDRperformance.
distortioncanbemodeledasoccurringaftersampling.Ifthe
3Throughoutthepaper,parallelHammersteinwillforsimplicitybere-
ferredtoasHammerstein. nonlinearitydistortionisincurredbeforesampling,problems

---

# Page 3

ThisarticlehasbeenpublishedinIEEEAccess.
arise though due to undersampled nonlinearities when the TABLE1. Definitions,Notations,andAcronyms
desired (original) signal covers the whole (or most of) the
Nyquist band. In the frequency-independent (memoryless) Symbol/Acronym Description
case, the two models are equivalent as sampling and static A Matrixusedintheproposeddesign.
nonlinearitiescommute.However,ingeneral,thetwomodels
ap(k),gp(k) Impulseresponsesofthenonlinear-distortionfilters
inthepre-samplingandpost-samplingmodels.
arenotequivalent.Asshownin[29],itisstillpossiblethough
b Vectorusedintheproposeddesign.
torecoverthedesiredsignalfromtheundersampleddistorted bm,wm(l) Bias values and filter coefficients (weights) in
signal, as long as the desired signal is Nyquist sampled. In branchmoftheproposedlinearizer.
practice, this can be carried out by incorporating interpola- dp(l) Filtercoefficients(weights)inbranchpoftheHam-
mersteinlinearizer.
tion in the linearization [30]. This paper considers this case
ϕ
(cid:8) (·)k(cid:9)
Minimum number of multiplications required to
as well, by extending the memoryless linearizer in [28] to generatethenonlinearities(·)k.
incorporate both filters and additional interpolation. To this hk(n) Impulseresponsesofinterpolationfilters.
end,discrete-timeequivalencesofthelinearizerschemesare ReLU(·),|·| Nonlinearoperationsintheproposedlinearizer.
derivedwhichwerenotconsideredin[30]. S(PK+1) Number of multiplications required to create all
It is also noted here that neural networks have been ex- the static nonlinearities in the Hammerstein post-
samplinglinearizer.
ploredforpredistortingpoweramplifiers(PAs)inDAIs[3],
vp(·) NonlinearoperationsintheHammersteinlinearizer.
[27],[31]–[37],buttheyarenotdirectlytransferabletoADI
w Vectorcontainingallfiltercoefficients(weights)of
linearization.Asignificantdifferenceisthatthepredistorted theproposedlinearizer.
signalmustbeoversampledtoenabledistortioncancellation xa(t) Continuous-timesignal.
intheanalogdomain,whichisnotrequiredforADIlineariza- x(n),v(n),y(n) Desired, distorted, and compensated discrete-time
signals.
tion as mentioned above. A second major difference is that
λ ParameterusedintheL2-regularization.
inADIs,real-valuedsignalsaretypicallyconsidered,andthe
ADC Analog-to-digitalconverter.
aim is to suppress all nonlinearity terms. For predistortion
ADI Analog-to-digitalinterface.
techniques in DAIs, one normally assumes a complex (I/Q) DAC Digital-to-analogconverter.
basebandsignalinthedigitaldomain,andittypicallysuffices DAI Digital-to-analoginterface.
toconsideronlyodd-ordertermsinapolynomialmodeland dBFS Decibelfullscale.
to suppress the distortion centered around the signal band. ENOB Effectivenumberofbits.
The remaining distortion can in that case be removed by ELU Exponentiallinearunit.
I/Q In-phase/quadrature.
analogfiltering.
LNL Linear–nonlinear–linear.
MIMO Multiple-inputmultiple-output.
B. OUTLINE
QAM Quadratureamplitudemodulation.
Following this introduction, the pre-sampling distortion
QPSK Quadraturephaseshiftkeying.
model(samplingbeforeincurreddistortion)andtheparallel SFDR Spurious-freedynamicrange.
HammersteinlinearizerarereviewedinSectionII.SectionIII SNDR Signal-to-noise-and-distortionratio.
introduces the proposed linearizer and design procedure for SNR Signal-to-noiseratio.
thepre-samplingdistortionmodel,andalsoprovidesseveral
simulationresults.Then,SectionIVconsiderstheextension
incorporating interpolation for the post-sampling distortion practice,theoutputofanADCwillnotbex(n)butadistorted
model(samplingafterincurreddistortion),includingseveral versionofit,sayv(n).
simulations. Section V provides results for linearization of In the digital pre-sampling Hammerstein model (illus-
circuit-simulateddata.SectionVIdiscussesalternativenon- tratedinFig.1),v(n)isgeneratedviaamemorypolynomial
linearfunctions,whereasSectionVIIconcludesthepaper. accordingto
D Q D
DEFINITIONS,NOTATIONS,ANDACRONYMS v(n)=a + (cid:88) a (k)x(n−k)+ (cid:88)(cid:88) a (k)xp(n−k), (1)
0 1 p
Themaindefinitions,notations,andacronymsusedthrough-
k=0 p=2k=0
outthepaperaresummarizedinTable1.
where a is a constant (offset), a (k) is the impulse re-
0 1
II. PRE-SAMPLINGDISTORTIONMODELAND sponse of a linear-distortion discrete-time filter, and a p (k),
LINEARIZATION p=2,3,...,Q, are the impulse responses of the nonlinear-
Consider a desired discrete-time signal (sequence) x(n) = distortiondiscrete-timefilters.Tokeepthenotationsimpler,
x (nT), which is a sampled version of a continuous-time all filters are here of equal order D, but they can generally
a
signalx (t)withauniformsamplingintervalT.Itisassumed have different orders. As seen in Fig. 1, this model corre-
a
thattheFouriertransformX (jω)iszerofor|ω| > ω ,with sponds to sampling at the input (pre-sampling) followed by
a c
ω < π/T, implying that x (t) is bandlimited and satisfy nonlinarities generated in the digital domain. In the special
c a
the Nyquist criterion for uniform sampling of x (t) with a case, when a (k) are constants (zeroth-order filters), it can
a p
sampling frequency of 1/T without introducing aliasing. In equivalently be described as nonlinearities generated in the

---

# Page 4

ThisarticlehasbeenpublishedinIEEEAccess.
a 0 d 0
x (t) x(n) v(n) v(n) y(n)
a a (k) + d (l) +
1 1
t=nT
(·)2 a (k) + (·)2 d (l) +
2 2
(·)3 a (k) + (·)3 d (l) +
3 3
(·)Q a
Q
(k) (·)K+1 d
K+1
(l)
FIGURE1. Digitalpre-samplingHammersteinmodel(seeFootnote2) FIGURE2. Hammersteinlinearizerwiththeupper(lower)dashedbox
withtheupper(lower)dashedboxindicatingthelinearbranch(nonlinear indicatingthelinearbranch(nonlinearbranches).
branches).
c
0
v(n) y(n)
analog domain followed by sampling since the operations c 1 (l) +
then commute. However, when a (k) correspond to general
p
filtersandthenonlinearities’bandwidthsexceedtheNyquist b
1
band,oneneedstoincorporateinterpolationformoreaccurate
+ f (·) w (l) +
modelingoftheanalogdistortion(seetheextensioninSection 1 1
IV). Further, the signal contains quantization noise, but it is b
2
hereexcludedfromthemathematicalexpressionsforthesake
+ f (·) w (l) +
ofsimplicity.4 2 2
Beforeproceeding,itisnotedthat,tomodelthesignalas
in (1) in a practical system, the parameters a 0 and a p (k), b N
k=0,1,...,D,p=1,2,...,Q,needtobeestimated.Several
+ f (·) w (l)
methods are available for this purpose [13], [24]. However, N N
the focus of this paper is to assess and compare the per-
formanceandcomplexityoftheHammersteinandproposed FIGURE3. Proposedlinearizerwiththeupper(lower)dashedbox
linearizers, not to estimate model parameters. To this end, indicatingthelinearbranch(nonlinearbranches).
themodelin(1)isusedforgeneratingdistortedtrainingand
evaluationsignals.Itisstressedthoughthattheproposedlin-
Thatis,
earizersdonotassumethatthedistortedsignalisintheform
of(1).Itisalsoemphasizedthatthepre-samplingdistortion M K+1 M
(cid:88) (cid:88)(cid:88)
y(n)=d + d (l)v(n−l)+ d (l)vp(n−l), (2)
model (and the post-sampling distortion model discussed in 0 1 p
SectionIV)isadigitalmodelofaggregatenonlinearitiesoc- l=0 p=2 l=0
curringaftersampling(beforesamplinginthepost-sampling whered isaconstant(offset),d (l)istheimpulseresponse
0 1
case). It does not require a physical implementation in the ofalinear-branchfilter,andd (l),p=2,3,...,K+1,arethe
p
analog domain, but facilitates identification and compensa- K impulseresponsesoftheK nonlinear-branchfilters.Here,
tioninthedigitaldomain. M representsthefilterorder(memorydepth).Again,forno-
tationsimplicity,allfiltershavethesameorder,buttheycan
generallybedifferent.Inanimplementation,thisschemere-
A. HAMMERSTEINLINEARIZER
quires(M+1)(K+1)+K multiplicationsand(M+1)(K+1)
Given the distorted signal v(n), the linearization amounts
two-input additions per corrected output sample. It involves
to generating a compensated signal, say y(n), in which the
(M+1)(K+1)multiplicationsforgeneratingthefilteredver-
distortionhasbeensuppressed(ideallyremoved).Inthecon-
sionsofvp(n),andK multiplicationsforgeneratingallvp(n).
ventionalHammersteinlinearizer,illustratedinFig.2,y(n)is
generatedinthesamewayasthedistortedsignalismodeled.
III. PROPOSEDLINEARIZERFORTHEPRE-SAMPLING
DISTORTIONMODEL
Intheproposedlinearizerforthepre-samplingmodel,shown
4Signal quantization is included in all evaluations in the examples of
SectionsIIIandIV. inFig.3,thecompensatedsignaly(n)isgeneratedas

---

# Page 5

ThisarticlehasbeenpublishedinIEEEAccess.
M N M
(cid:88) (cid:88)(cid:88) c
y(n)=c + c (l)v(n−l)+ w (l)u (n−l), (3) 0
0 1 m m y(n)
l=0 m=1l=0 c (·) +
1
where M denotes the filter order of c (l) and of the N
1
nonlinear-branch filters w (l), m = 1,2,...,N, c is a
m 0
constantoffset,andthetermsu (n)are b 1
m v(n) w
01
+ f (·) + +
u (n)=f (v(n)+b ), (4) 1
m m m
b
withf m representingnonlinearoperations.Specifically,f m (v) 2 w 02
are chosen as either the modulus |v| or the ReLU operation + f (·) +
2
max{0,v} due to their simplicity and reduced complexity
b
in hardware implementation [27], [28] (also see Section N
w
0N
VI). Additionally, the bias values b , for m=1,2,...,N,
m + f (·)
N
are selected to be uniformly distributed within the range
[−b ,b ] where the optimal value for b is deter-
max max max
minedasdetailedlaterinSectionIII-B.Hence,thebiasvalues
b arechosenas
m w
11
2(m−1)b + +
b =−b + max, m=1,2,...,N. (5)
m max N −1
w
12
z−1 +
A. IMPLEMENTATIONCOMPLEXITY
In the implementation, the proposed scheme in (3) re-
quires only (M+1)(N+1) multiplications per sample, and w 1N
(M+1)(N+1)+N two-inputadditions,includingtheN bias
additions.Notably,theproposedlinearizerrequiresK multi-
plications less than the Hammerstein model at the expense
of K extra additions, when they have the same number of
branches(N=K).Hence,inparticularforcaseswhereasmall
M issufficient,themultiplicationcomplexityissubstantially w M1
lower for the proposed linearizer (also see Section III-C1). +
Further,sincemultiplicationsgenerallyrequiresubstantially
more power than additions in an implementation [38], [39], w M2
the proposed linearizer will have a lower implementation z−1 +
complexity.
Moreover, a significant additional advantage of the pro- w
MN
posed linearizer is that it eliminates the need for data quan-
tizationbeforefiltering.Conversely,intheHammersteinlin-
earizer,dataquantizationsmustbeperformedattheoutputs
ofthenonlinearities(i.e.,beforethefiltering)topreventex- FIGURE4. EquivalentimplementationoftheproposedlinearizerinFig.3,
utilizedintheproposeddesign.
cessivelylongandcostlyinternalwordlengths.Thesequan-
tizations introduce quantization errors (quantization noise),
which are scaled by the energy of the corresponding filters’
linearizer then amounts to determining the parameters c ,
impulseresponsesd (l)whichequalsthesumofthesquares 0
k c , w , and b so that the output signal y(n) closely ap-
oftheimpulseresponsevalues[40],[41].Consequently,the 1 lm m
proximates the desired signal x(n) in some sense, which is
impulseresponse valuesmust bekeptsmall toavoidsignif-
here assumed to be the least-squares sense. To this end, the
icant noise amplification, which would degrade the output
designproceduredescribedbelowisproposed,whichextends
SNDR.Alternatively,longerinternalwordlengthsneedtobe
ourfrequency-independentlinearizerin[28]toaccommodate
used,whichalsoincreasestheimplementationcost.Thepro-
frequencydependency.Itisassumedthatthesignalisnormal-
posedschemeovercomesthisproblemsinceallquantizations
izedsothatitsmodulusisboundedbyone.
arecarriedoutafterthefilteringoperations,therebyavoiding
noiseamplificationfromthequantizationstotheoutput. 1) Generate a set of R reference signals x (n) and the
r
corresponding distorted signals v (n), r=1,2,...,R,
r
B. PROPOSEDDESIGN usingasignalmodelasin(1)ormeasureddata.
Fordesignpurposes,wemakeuseoftheequivalentstructure 2) Generate a set of S uniformly distributed values of
in Fig. 4 where w =w (l). The design of the proposed b ∈ [b,b ].Wehaveexperimentallyobservedthat
lm m max l u

---

# Page 6

ThisarticlehasbeenpublishedinIEEEAccess.
b=0.5 and b =1.5 are appropriate values when the 4) SelectthebestoftheS solutionsabove.
l u
signaliswithintherange[−1,1]. 5) Evaluate the linearizer over a large set of signals, say
3) Foreachspecifiedvalueofb ,thecorrespondingb R(eval),whereR(eval) ≫R.
max m
valuesarecalculatedasin(5).Then,minimizethecost Remark1:TheproposeddesignusesRreferencesignals.
functionE givenby Oncethesereferencesignalshavebeencollected,thedesign
amountstoamatrixinversionforagivensetofbiasvalues.
(cid:88) R (cid:88) L (cid:18) (cid:16) M(cid:17)(cid:19)2
E = y (n)−x n− , (6) Hence,thedesigntime(andthusconvergencetime)ismainly
r r 2
determined by the time it takes to collect the R reference
r=1n=1
signals. This is however common for all linearizers, which
where L denotes the data length and M/2 compen-
requirethesameamountofdatatoachievethesamelinearizer
sates for the delay of the linearization filters5. The
performance, and is thus not specific for our proposal. The
coefficients c , c , and w (for l=0,1,...,M, and
0 1 l,m
additionalaspectoffindingthebiasvaluescaninpracticebe
m=1,2,...,N)in(3)arecomputedusingmatrixinver-
carriedoutonlyonce,andonecanthenusethosebiasvalues
sion,incorporatingL -regularizationtoavoidlargepa-
2
when the model and model parameters change. This is be-
rametervaluesandtopreventill-conditionedmatrices.
causewehaveobservedthatthelinearizerperformancehasa
Specifically, let w be a ([(M+1)(N+1)+1]×1) col-
lowsensitivitytoexactbiasvalues,aslongastheyarelinearly
umnvectorcontainingallcoefficientsw ,alongwith
l,m
spacedbetweentheapproximateminimumandmaximumof
c (l) and c . Let A be an (L ×[(M+1)(N+1)+1])
1 0 r the signal.7 Taking this into account, the proposal has the
matrix, where each column contains the L samples of
samedesigntimeastheHammersteinlinearizer,butoffersa
u (n−l)forl=0,1,...,M andm=1,2,...,N,theL
r,m
lowerlinearizerimplementationcomplexity.Itisalsostressed
input samples v (n−l) for l=0,1,...,M, and L ones
r
againthattheproposalavoidsthecostlyandtime-consuming
(corresponding to the constant c ). Minimizing E in
0
iterative nonconvex optimization that is traditionally used
(6),intheleast-squaressense,yieldsthesolution(see
whentrainingneuralnetworks.
AppendixA)
w=A−1b, (7)
Remark2:Intheexampleslateronwheresyntheticdata
isused(Examples1–5),thereferencesignalsareknown(e.g.
where pilot sequences). It is appropriate to use such signals when
R R investigating the linearization capability of the linearizers,
(cid:88) (cid:88)
A=λI + A⊤A , b= A⊤b , bothfortheproposedoneandHammerstein.Inpractice,the
(M+1)(N+1)+1 r r r r
r=1 r=1 reference signals may not be completely known but have to
(8)
beestimated.Aslongasthesignalestimatesaresufficiently
with A⊤ being the transpose of A , and b be-
r r r accurate, the proposed design still works well. This will be
ing an L × 1 column vector containing the L sam-
illustratedinExample6wheresinusoidswithunknownam-
ples x (n−M/2) − v (n−M/2). It is noted here that
r r plitudesandphasesareused.Ingeneral,existingmethodsfor
x (n−M/2) − v (n−M/2) is used in b instead of
r r r estimationofmulti-sinesignalscanbeusedinthiscontext.
x (n−M/2), in order to compute small values of the
r Remark 3: In the proposed method, the bias values are
linear-branch filter coefficients. That is, we replace
optimizedoveradiscretesetofvalues,whichmeansthatthe
c (l)v(n−l) in (3) with v(n−M/2) + ∆c (l)v(n−l)
1 1 overallsolutionisnotguaranteedtobegloballyoptimal,even
and then compute the value of ∆c . In this way, all
1 ifeachsolutionwithfixedbiasvaluessois.However,alsofor
parameterstobecomputedintheleast-squaresdesign
aregularoptimization,wherethebiasvaluesandcoefficients
are small (zero in the ideal case with no distortion).6
arejointlyoptimized,onecannotguaranteeglobaloptimality
Further, λI is a diagonal matrix with
(M+1)(N+1)+1 astheproblemisthennotconvex.Hence,onlylocaloptimal-
smalldiagonalentriesλfortheL -regularization.The
2 itycanbeguaranteed. Startingwiththeproposedoptimized
linearized output (treated as a row vector) y =y (n),
r r solutions in the example sections, we have also carried out
n=1,2,...,L,isgivenby
furtherjointoptimizationswhichdonotimprovetheresults.
y =v +w⊤A⊤, (9) This shows that the proposed design yields at least locally
r r r
optimal solutions, which are also good solutions as they
wherev =
(cid:80)M
v (n−l),n=1,2,...,L isalsoarow
r l=0 r outperform the Hammerstein linearizers, whose optimized
vector.
solutionsareguaranteedtobegloballyoptimalsincetheylack
5Itisassumedintheexpressionn−M/2thatMiseven,butoddMcan biasvalues.
alsobehandledbyreplacingM/2with(M−1)/2or(M+1)/2.
6Thepaperfocusesonweaklynonlinearsystemswherethenonlinearities C. SIMULATIONSANDRESULTS
aremuchsmallerthanthedesiredsignalandthemodelparametersaresmall,
Fortheevaluationsandcomparisons,weassumeadistorted
whichistypicallythecaseinanalogcircuitswithundesirednonlinearities.
Inthiscase,thelinearizerscanalsohaverelativelysmallcoefficients,which signal v(n) with a distortion filter order of D=6. This sig-
in the proposed design are obtained through matrix inversion with L2-
regularization.Insystemswithlargermodelparameters,thelinearizersmay 7To assess the bias sensitivity, we changed the optimal bmax in the
needlargercoefficientswhichcanalsobeobtainedthroughtheproposed examplesby±3and±5percent.ThiscausedameanSNDRreductionof
designbyusingasmallerλfortheL2-regularization. lessthan1and2dB,respectively.

---

# Page 7

ThisarticlehasbeenpublishedinIEEEAccess.
1.0
0.8
0.6
0.4
0.2
0.0
0 0.2 0.4 0.6 0.8 1
NormalizedFrequency
edutingaM
×
10− 1
2
0
2 −
0 0.2 0.4 0.6 0.8 1
NormalizedFrequency
esahP
a2 a4 a6 a8 a10 Distortedsignal
a3 a5 a7 a9 0
20
−
40
−
60
−
80
−
0 0.2π 0.4π 0.6π 0.8π π
FIGURE5. Magnitudeandphaseresponseofap(k),forp=2,···,10,in
Example1. Linearizedsignal
0
nal is modeled as described in (1) with parameters8: a 0 =0, − 20
a (k)=[0,0,0,1,0,0,0], and a (k) for k=0,1,...,D and
1 p 40
p=2,3,...,Q, with Q=10, randomly generated with fre- −
quency responses as depicted in Fig. 5. We imposed a con- 60
straint to have a mean SNDR around 30 dB for the set of −
distortedsignals.TheSNDRindBforarealreferencesignal 80
−
x(n)anditsdistortedsignalv(n),computedoverL samples, 0 0.2π 0.4π 0.6π 0.8π π
is
(cid:32) (cid:80)L−1x2(n) (cid:33)
SNDR=10log n=0 [dB]. (10)
10 (cid:80)L−1(x(n)−v(n))2
n=0
Example1:Weconsiderthemulti-tonesignal
31
(cid:88)
x(n)=G× A sin(ω n+α ), (11)
k k k
k=1
where A =1 for all k, and α are randomly chosen from
k k
{π/4,−π/4,3π/4,−3π/4}, which corresponds to quadra-
turephaseshiftkeying(QPSK)modulation.Thefrequencies
ω aregivenby
k
2πk
ω = +∆ω, (12) k 64
inwhichcasethesignalcorrespondstothequadrature(imag-
inary)partof31activesubcarriersina64-subcarrierOFDM
signal with a random frequency offset ∆ω. In the design
andevaluationweuse,respectively,R=50andR(eval)=5000
signalswithrandomlygeneratedfrequencyoffsetsassuming
uniformdistributionbetween−π/64andπ/64,quantizedto
12 bits, and of length L=8192. The gain G is selected so
that the distorted signals are below one in magnitude. For
theL -regularization,alinearsearchisusedtofindthevalue
2
λ ∈ [10−10,10−1]thatbestfitseachinstance,meaningeach
combinationofb ,M,andN.TheHammersteinlinearizer
max
hasbeendesignedinthesamewaybutwithoutthebiasvalues.
Theconstraintwastoselecttheoptimalλ-value9,whichwas
primarilyusedtoregulatetheHammersteinlinearizertoavoid
large parameter values and large noise amplification. The
8We have also considered cases where a0 and a1(k) were randomly
generated(additionalsmalloffsetandlineardistortion),buttheresultswere
practicallythesame.
9Theoptimalλ-valueisdefinedhereasthevaluethatresultsinthesmallest
errorin(6)whileavoidingthematrixλI+A⊤Atobeill-conditionedand
ensuringthatalltheentriesinwarewithintherange[−1,1].
]Bd[murtcepsedutilpmA
Normalizedfrequency[rad]
FIGURE6. Spectrumbeforeandafterlinearizationforamulti-sinesignal
usingtheproposedlinearizerwithafilterorderofM=6andN=12
nonlinearbranches(Example1).
proposed linearizer does not have noise amplification and
thus allows larger parameter values, but the magnitudes of
thosevaluesareneverthelessbelowunityinmagnitude,even
witharelaxedL -regularization.
2
Further,wehave consideredboththemodulusandReLU
asnonlinearoperations,aswellascombinations(modulusin
somebranches,ReLUintheotherbranches),butthedifferent
optionsresultedinpracticallythesameperformance.There-
sultspresentedintheexamplesareforthemodulusoperation.
Figure6showsthespectrumbeforeandafterlinearization
for one of the signals using the proposed linearizer with a
filter order of M=6 and N=12 nonlinear branches. Figure
7plotsthemeanSNDRover5000signalsforeachlinearizer
instance(withanSNDRvarianceofapproximately0.5dBfor
allinstances)versusthenumberofbranchesfortheproposed
andHammersteinlinearizers.10
The signal-to-noise ratio (SNR) is approximately 65 dB
without distortion, and the SNDR is around 30 dB for the
distorted signals before linearization. As seen in Fig. 7, the
SNDR approaches 62 dB for the proposed linearizer, thus
an improvement by 32 dB which corresponds to more than
five bits improvement when using a linearizer filter order
of or above six, which is required here because the dis-
tortion filter order is six. For the Hammerstein linearizer,
the SNDR approaches only about 58dB. The difference be-
tween the SNDR values (62dB and 58dB) and the bound
10Foralldesigns,theoptimizedparametervaluesandarithmetic-operation
resultsarequantizedto14bitsintheevaluations.Thisprovidesapractical
trade-offbetweenhardwarecostandnumericalaccuracy.Increasingpreci-
sionbeyondthisyieldsnegligibleSNDRimprovements.

---

# Page 8

ThisarticlehasbeenpublishedinIEEEAccess.
65
60
55
50
45
40
35
30
12 4 6 8 10 12 14 16 18 20 22 24 26 28 30 32
Numberofnonlinearbranches
]Bd[RDNS
Distortedsignal
0
20
InitialSNDR −
Proposed(M=0) Hammerstein(M=0)
Proposed(M=2) Hammerstein(M=2) 40
Proposed(M=4) Hammerstein(M=4) −
Proposed(M=6) Hammerstein(M=6)
Proposed(M=8) Hammerstein(M=8) 60
Proposed(M=10) Hammerstein(M=10) −
Proposed(M=12) Hammerstein(M=12)
80
−
0 0.2π 0.4π 0.6π 0.8π π
Linearizedsignal
0
FIGURE7. SNDRversusnumberofnonlinearbranchesinExample1.
20
−
40
of 65dB (since SNDR ≤ SNR) can be attributed to the −
L 2 -regularization. The SNDR gap of 4dB is due to the fact 60
that the L -regularization has less impact on the proposed −
2
linearizer,whichisbecauseithasrelativelysmallcoefficients 80
−
evenwithoutL -regularization.11 ThisimpliesthattheHam- 0 0.2π 0.4π 0.6π 0.8π π
2
mersteinlinearizerhasalowerpeakperformance(about4dB
inthisexample)thantheproposedlinearizerforthesameL -
2
regularization.
Example2:Tofurtherillustratetherobustnessofthepro-
posedlinearizerdesignedinExample1,wehavealsoevalu-
ated it for the same type of multi-sine signal as in Example
1 but with some subcarriers set to zero, and for a bandpass
filteredwhite-noisesignalcovering60%oftheNyquistband.
As illustrated in Figs. 8 and 9 for one of each of these
signals, essentially the same result is obtained.12 Less than
1 dB SNDR degradation compared to the linearized signals
consideredinExample1isobserved.
Remark 4: It is noted that the multi-sine signals in Ex-
amples 1 and 2 correspond to the imaginary part of an
OFDM signal (as real signals are considered in the paper)
withQPSK(i.e.,4-QAM)modulation,whereasthebandpass
filtered white-noise signals in Example 2 resemble higher-
order QAM-modulated signals. Additional simulations with
16-QAM and 64-QAM show practically the same perfor-
mance, confirming that the method generalizes well across
generalwidebandcommunicationsignals.
Example3: Thisexamplepresentsresultssimilartothose
in Fig. 7 for Example 1, but with 5000 OFDM signals with
11The performance gap of 4 dB can be decreased by using a smaller
regularizationparameterλbutitalsocomeswithlargercoefficientvaluesand
increasedimplementationcostasmorebitsinternallyarethenrequiredinthe
Hammersteinlinearizerimplementation.AsdiscussedinSectionIII-A,this
isduetonoiseamplificationwhichispresentintheHammersteinlinearizer
but not in the proposed linearizer. To exemplify, in Example 1 with 24
branches and M=6, reducing λ by a factor of 250 for the Hammerstein
linearizer,causesthemaximumcoefficientmagnitudetoincreasebyafactor
of56comparedtotheoptimalλ(seeFootnote9).Further,toreducethe
performancegapto,e.g.,about1dB,22bitsarerequiredinstead14bits,
whichissufficientintheproposedlinearizer.
12The observed out-of-band spectral reduction in Fig. 9 is due to lin-
earizationofadistortedbandpassfilteredwhite-noisesignal.Inthiscasethe
linearizersuppressestheout-of-banddistortiondowntothenoisefloorwhich
emanatesfromdataquantization.
]Bd[murtcepsedutilpmA
Normalizedfrequency[rad]
FIGURE8. Spectrumbeforeandafterlinearizationforamulti-sinesignal
withnullsubcarriersusingtheproposedlinearizerwithafilterorderof
M=6andN=12nonlinearbranches(Example2).
Distortedsignal
0
20
−
40
−
60
−
80
−
0 0.2π 0.4π 0.6π 0.8π π
Linearizedsignal
0
20
−
40
−
60
−
80
−
0 0.2π 0.4π 0.6π 0.8π π
]Bd[murtcepsedutilpmA
Normalizedfrequency[rad]
FIGURE9. Spectrumbeforeandafterlinearizationforabandpassfiltered
white-noisesignalusingtheproposedlinearizerwithafilterorderof
M=6andN=12nonlinearbranches(Example2).
QPSKmodulationexhibitingsecond-orderfiltereddistortion
terms (D=2) with the parameters a =0, a =[0,1,0], and
0 1
randomly generated a for p=2,3,...,Q, with Q=10, and
p
whose frequency responses are as shown in Fig. 10. In this
case,thesignalcanbewelllinearizedwithanorderofM ≥2,
duetothesimplersecond-orderfiltereddistortionterms.This
isseeninFig.11.

---

# Page 9

ThisarticlehasbeenpublishedinIEEEAccess.
1.0
0.8
0.6
0.4
0.2
0.0
0 0.2 0.4 0.6 0.8 1
NormalizedFrequency
edutingaM
×
10− 1
2
0
2
−
0 0.2 0.4 0.6 0.8 1
NormalizedFrequency
esahP
a2 a4 a6 a8 a10
a3 a5 a7 a9
FIGURE10. Magnitudeandphaseresponsesofap(k),forp=2,···,10,
inExample3.
65
60
55
50
45
40
35
30
12 4 6 8 10 12 14 16 18 20 22 24 26 28 30 32
Numberofnonlinearbranches
]Bd[RDNS
65
60
55
50
45
40
35
30
14 20 40 80 160 320
Numberofmultiplications
InitialSNDR
Proposed(M=0) Hammerstein(M=0)
Proposed(M=2) Hammerstein(M=2)
Proposed(M=4) Hammerstein(M=4)
Proposed(M=6) Hammerstein(M=6)
Proposed(M=8) Hammerstein(M=8)
Proposed(M=10) Hammerstein(M=10)
FIGURE11. SNDRversusnumberofnonlinearbranchesinExample3.
1) ImplementationComplexity
Figures 7 and 11 show the SNDR improvement versus the
numberofbranchesinthelinearizer.However,asdiscussed
in Sections II and III, with N nonlinear branches, the Ham-
merstein linearizer (with N=K) requires K additional mul-
tiplicationscomparedtotheproposedscheme,whichhasK
additional additions, but since multiplications are generally
more expensive to implement than additions [38], [39], the
implementationcostwillbelowerfortheproposal.Thepro-
posed linearizer is thus more efficient for the same number
of nonlinear branches, especially when M is small and the
relative cost of multiplications is relatively high. This effi-
ciency is demonstrated in Figs. 12 and 13, which plot the
SNDRversusthenumberofmultiplicationsforbothmethods
inExample1andExample3,respectively.Itisobservedthat
theproposedlinearizerclearlyoutperformstheHammerstein
linearizer for a small M (M=2 in Fig. 13) whereas the two
methodshavecomparableperformanceforalargerM (M=6
in Figs. 12 and 13 and M=10 in Fig. 12). For instance, in
Example 3 with M=2, the Hammerstein linearizer requires
43multiplicationstoreach57dB(Fig.13),whereasthepro-
posedlinearizerachievesthesameperformancewithonly30
multiplications,correspondingtoasavingof13/43≈30%.It
isalsoobservedagainthattheproposedlinearizerachievesup
to4dBhigherSNDRthantheHammersteinlinearizer,asseen
in Figs. 7 and 11–13, due to the L -regularization. Finally,
2
althoughtheresultsherefocusondistortionordersD=6and
D=2,itshouldbenotedthatthelargestsavings(about50%)
]Bd[RDNS
=6 =10
M M
InitialSNDR
Proposed(M=6) Hammerstein(M=6)
Proposed(M=10) Hammerstein(M=10)
FIGURE12. SNDRversusnumberofmultiplicationsinExample1.
65
60
55
50
45
40
35
30
6 10 20 40 80 160 320
Numberofmultiplications
]Bd[RDNS
=2 =6 M M
InitialSNDR
Proposed(M=2) Hammerstein(M=2)
Proposed(M=6) Hammerstein(M=6)
FIGURE13. SNDRversusnumberofmultiplicationsinExample3.
of the proposed linearizer over the Hammerstein linearizer
occurinthememory-independentcase(D=0),whichallows
amemorylesslinearizer(M=0),aspreviouslyshownin[28].
Asmentionedintheintroduction,itisalsonotedthatboth
the proposed and Hammerstein linearizers are substantially
moreefficientthanexistingneural-network-basedlinearizers
which require several hundreds or even thousands of multi-
plicationstocorrecteachoutputsample,evenforsimplerand
more narrowband signals and for more modest SNDR im-
provements [14]–[22]. For example, the proposed linearizer
in Example 3 (Figs. 11 and 13), when it starts reaching its
SNDRsaturationlevel,requiresabout40multiplicationsfor
M=2. (Increasing M and N further only offers a modest
SNDR improvement at the cost of a higher complexity).
Correspondingly, in Example 1 (Figs. 7 and 12), about 80
multiplications are required for M=6 (recall that M=6 and
M=2correspondtothedistortionfilterorder,D=6andD=2,
inExample1andExample3,respectively).Thisisaboutan
order-of-magnitude lower complexity than for the existing
neural-network-basedlinearizers.
IV. PROPOSEDLINEARIZERFORTHEPOST-SAMPLING
DISTORTIONMODEL
To linearize post-sampling analog distortion, the proposed
linearizer in Section III is extended by incorporating inter-
polation.ThepointofdepartureisthentheanalogHammer-

---

# Page 10

ThisarticlehasbeenpublishedinIEEEAccess.
g 0 x a (t) x(n) v(n)
g (n) +
x (t) v(n) 1
a g (t) + t=nT
a1
t=nT
↑P h (n) (·)2 g (n) ↓P +
(·)2 g (t) + 2 2 2 2
a2
↑P h (n) (·)3 g (n) ↓P +
3 3 3 3
(·)3 g (t) +
a3
↑P
Q
h
Q
(n) (·)Q g
Q
(n) ↓P
Q
(·)Q g
aQ
(t)
FIGURE16. Discrete-timeequivalenceoftheschemeinFig.14.
FIGURE14. Analogpost-samplingHammersteinmodelwiththeupper
(lower)dashedboxindicatingthelinearbranch(nonlinearbranches).
lowedbyadownsamplerthatdiscardstheredundantsamples,
a) resulting in Fig. 15(b). Next, we note that the sampling at
the output of the filter g (t) fulfills the sampling theorem
x
a
(t) (·)Pk g
ak
(t) ak
forthesamplingrateP /T.Hence,asseeninFig.15(c),the
t=nT k
b) filter g ak (t) followed by the sampler can be replaced by a
sampler followed by a digital filter g (n) having the same
k
x a (t) (·)Pk g ak (t) ↓P k e k (n) frequency response as g ak (t), thus G k (ejωT/Pk)=G ak (jω), in
t=nT/Pk
the frequency region ω ∈ [0,πP /T]. As the nonlinearity
k
c)
is static (memoryless), we can then interchange the order
x a (t) (·)Pk g k (n) ↓P k e k (n) of the sampler and nonlinearity, as seen in Fig. 15(d). Now,
t=nT/Pk we note that x a (t) is oversampled P k times. Therefore, the
d) inputtothenonlinearitycanequivalentlybeobtainedthrough
x(n)
samplingattheoriginallowerrate1/T followedbyinterpo-
x a (t) (·)Pk g k (n) ↓P k e k (n) lation by P , the latter being represented by upsampling by
t=nT/Pk
P followed
k
by the discrete-time interpolation filter h (n).
e) k k
x(n) This yields Fig. 15(e). Making use of this equivalence, the
x a (t) ↑P
k
h
k
(n) (·)Pk g
k
(n) ↓P
k
e k (n) discrete-time equivalence to the whole scheme in Fig. 14 is
t=nT obtained according to Fig. 16. Here, we have also utilized
FIGURE15. Derivationofthediscrete-timeequivalenceofbranchkinFig. that,inthelinearbranch,g a1 (t)canbedirectlymodeledby
14. its discrete-time counterpart g (n) since filtering followed
1
by sampling is equivalent to sampling followed by filter-
ing, provided that only linear operations are involved and
steinmodelinFig.14wherethedistorteddigitalsignalv(n)
the signal is Nyquist sampled. Based on the discrete-time
is obtained by sampling the corresponding distorted analog
equivalencederivedabove,thelinearizersfollowinthesame
signal.Here,evenifx (t)isbandlimitedtotheNyquistband,
a
thenonlineardistortionisnot,becausethenonlinearities(·)p way as in Sections II and III as detailed below. The design
ofthelinearizersfollowsthesameprocedureasproposedin
widen the spectrum by a factor of p. However, as discussed
SectionIII.
in the introduction, it is still possible to recover the desired
sequencex(n)fromv(n)[29],whichinpracticecanbecarried
B. HAMMERSTEINLINEARIZER
outbyutilizinginterpolationinthelinearization[30].Tothis
FortheHammersteinlinearizer,thecompensatedsignaly(n)
end, we will make use of a discrete-time equivalence to the
isagaingeneratedinthesamewayasthedistortedsignalis
structure in Fig. 14, which was not considered in [30]. The
modeled.Toavoidfilteringoperationsatthehighersampling
discrete-timeequivalenceisderivedthroughthestepsshown
rate [see Fig. 15(e)] we make use of polyphase decomposi-
in Fig. 15(a)-(e) for one branch, which is further explained
tion [42], and write the transfer functions H (z) and G (z)
below. k k
accordingto
A. EQUIVALENTDISCRETE-TIMEMODEL H (z)=
P (cid:88)k−1
z−iH (zPk) (13)
k ki
StartingwiththebranchschemeinFig.15(a),wefirstreplace
i=0
thesamplingattheoutputwithaP -foldfastersampler13fol-
k and
P (cid:88)k−1
13It is assumed here that Pk=k, for k=2,3,...,Q, (Fig. 14), but in G
k
(z)= ziG
ki
(zPk), (14)
general,Pkcantakeonvaluesfromasetofintegervalues.
i=0

---

# Page 11

ThisarticlehasbeenpublishedinIEEEAccess.
a) a) b
m
v(n) e (n) v(n) e (n)
k m
↑P
k
h
k
(n) (·)Pk d
k
(n) ↓P
k
↑P
m
h
m
(n) + f
m
(·) w
m
(n) ↓P
m
b) b) b m e m (n)
v(n) e (n) v(n)
k
h
k0
(n) (·)Pk d
k0
(n) + + h
m0
(n) f
m
(·) w
m0
(n) +
h
k1
(n) (·)Pk d
k1
(n) +
h (n) f (·) w (n) +
m1 m m1
h
kPk−1
(n) (·)Pk d
kPk−1
(n)
h (n) f (·) w (n)
mPm−1 m mPm−1
FIGURE17. Nonlinear-branchimplementationoftheHammerstein
linearizer.
FIGURE18. Nonlinear-branchimplementationoftheproposedlinearizer.
respectively.Throughtheuseofthecorrespondingpolyphase
ponentsbecomezero,whichexplainsthetermmin(k,M+1)
realizations,eachnonlinearbranchcanthenbeimplemented
in the summation. To exemplify, the minimum number of
accordingtoFig.17(b)wherealloperationsarecarriedoutat
multiplications to generate all the nonlinearities (·)k, for
the input-output sampling rate. Utilizing this, it is observed
P = 10 and M=2 (M + 1 ≥ 10), is S(10)=77(177),
thatthefinaldiscrete-timemodelandlinearizerbelongtothe K+1
distributed as S =2(2), S =6(6), S =6(8), and so on un-
classofparallelLNLsystems,whereeachbranchcomprises 2 3 4
til S =12(40) with the sequence14 of four multiplications
a filter (here polyphase component), a static nonlinearity 10
(·)Pk, and a filter whose coefficients are determined by the (·) × −− ( → ·) (·)2 × −− ( → ·) (·)3 × −− ( → ·)2 (·)5 × −− ( → ·)5 (·)10.
ADI’sdistortion.ThemaindifferencefromtheHammerstein
linearizer in Section II (Fig. 2) is that, here, each static C. PROPOSEDLINEARIZER
nonlinearity (·)Pk is present in P k polyphase branches and UtilizingagainthepolyphasedecompositionofH k (z)in(13)
eachbranchincorporatestheinterpolationfilters’polyphase andthatofw (n)accordingto
m
components[Fig.17(b)].
P (cid:88)m−1
W (z)= ziW (zPm), (16)
1) ImplementationComplexity m mi
i=0
Theinterpolationfiltersareexcludedinthecomplexitycom-
parisons as they are common for the Hammerstein and the andthecorrespondingpolyphaserealizations,eachnonlinear
proposedschemes.Comparedwiththepre-samplingscheme, branchintheproposedlinearizercanbeimplementedaccord-
thenumberofmultiplicationsrequiredforthepost-sampling ing to Fig. 18(b), where the bias values have been moved
Hammerstein linearizer increases because several copies of to the input (see the explanation below). As seen, for the
eachstaticnonlinearity(·)Pk needtobeimplementedandthe proposedlinearizer,thestaticnonlinearities(·)ppresentinthe
generation of the different nonlinearities can not be shared Hammersteinlinearizerareagainreplacedwithadditivebias
betweenthebranchesastheyhavedifferentinputs(different values followed by the simpler nonlinear modulus or ReLU
polyphasecomponents’outputs).Thus,thenumberofmulti- operations(compareFigs.17and18).
plicationsrequiredtocorrecteachoutputsampleincreasesto
(M +1)×(K +1)+S(P ),where 1) ImplementationComplexity
K+1
FortheproposedlinearizerwithN=K,thenumberofmulti-
S(P )=
P (cid:88)K+1
min(k,M +1)ϕ
(cid:8) (·)k(cid:9)
(15)
plicationsisalways(M+1)×(K+1)astherearenomultipli-
K+1
cationsinvolvedinthenonlinearoperations.Ifimplemented
k=2 (cid:124) (cid:123)(cid:122) (cid:125)
Sk straightforwardly, this comes at the cost of an increase in
represents the number of multiplications required to create the number of bias additions as P m such additions are re-
all the static nonlinearities (·)k for the nonlinear branches quiredineachnonlinearbranch.However,observingthatthe
k=2,··· ,P . Here, ϕ (cid:8) (·)k(cid:9) represents the minimum polyphasecomponentsapproximateunity-gainallpassfilters
K+1
number of multiplications required to generate one of the [44],onecancarryoutonlyonebiasadditionattheinputof
nonlinearities (·)k in a particular branch k, which can be each nonlinear branch as seen in Fig. 18. This is because a
found through an optimal addition-chain exponentiation al-
gorithm [43], whereas S k represents the total nonlinearity- 14Notethatthesequences(·) × −− ( → ·) (·)2× −− (· → )2 (·)4× −− ( → ·)2 (·)6× −− ( → ·)4 (·)10,
multiplicationcomplexityofbranchk.Further,whenthefilter and(·) × −− ( → ·) (·)2 × −− (· → )2 (·)4 × −− ( → ·)4 (·)8 × −− ( → ·)2 (·)10 canalsobeusedto
lengthM+1issmallerthanP
k
=k,k−M−1polyphasecom- obtainthenonlinearity(·)10withfourmultiplications.

---

# Page 12

ThisarticlehasbeenpublishedinIEEEAccess.
1.0
0.8
0.6
0.4
0.2
0.0
0 0.2 0.4 0.6 0.8 1
NormalizedFrequency
edutingaM
×
10− 1
2
0
2
−
0 0.2 0.4 0.6 0.8 1
NormalizedFrequency
esahP
g2 g4 g6 g8 g10
g3 g5 g7 g9
FIGURE19. Magnitudeandphaseresponsesofgp(k),forp=2,···,10,in
Example4.
Distortedsignal
0
20
−
40
−
60
−
80
−
0 0.2π 0.4π 0.6π 0.8π π
Linearizedsignal
0
20
−
40
−
60
−
80
−
0 0.2π 0.4π 0.6π 0.8π π
]Bd[murtcepsedutilpmA
50
45
40
35
30
12 4 6 8 10 12 14 16 18 20 22 24 26 28 30 32
Numberofnonlinearbranches
Normalizedfrequency[rad]
FIGURE20. Spectrumbeforeandafterlinearizationforamulti-sinesignal
usingtheproposedlinearizerwithafilterorderofM=6andN=16
nonlinearbranches(Example4).
constant b at the input of a linear and time-invariant filter m
h (n) results in the constant b H (ej0)=b at its output mk m mk m
for a unity-gain allpass filter with a real impulse response
h (n)whichistheassumptionhere.Inthisway,theoverall mk
numberofbiasadditionswillbethesameasintheproposed
pre-samplingschemeinSectionIII.
D. SIMULATIONSANDRESULTS
We assume a distorted signal v(n) generated in the ana-
log domain through the discrete-time equivalence in Fig.
16. The nonlinear-model coefficients were chosen in the
same way as before (see Footnote 4), thus here with
g =0, g (k)=[0,1,0], and g (k) randomly generated for
0 1 p
k=0,1,...,D,p=2,3,...,QwithD=2andQ=10.Wethus
assume a distorted signal v(n) exhibiting second-order fil-
tered distortion, with g (k) randomly generated with fre-
p
quencyresponsesasseeninFig.19.
]Bd[RDNS
InitialSNDR PL(M=6) HL(M=6)
PL(M=0) PL(M=8) HL(M=0) HL(M=8)
PL(M=2) PL(M=10) HL(M=2) HL(M=10)
PL(M=4) PL(M=12) HL(M=4) HL(M=12)
FIGURE21. SNDRversusnumberofnonlinearitybranches.HerePL
standsfortheproposedlinearizerandHLfortheHammersteinlinearizer.
(Example4)
Example4: Weconsiderasetofmulti-tonesignalssimilar
to those in Example 1, and Example 3, generated through
(11), with A =1 for all k, ω computed as in (12), and
k k
α alsorandomlyselectedfrom{π/4,−π/4,3π/4,−3π/4},
k
correspondingtoQPSKmodulation.Here,weuse50active
carriers out of 64, covering approximately 80% of the first
Nyquist band. Both the reference and distorted signals are
quantizedto10bitsforadatasetwithR=50andR(eval)=5000
signals. Figure 20 displays the spectrum before and after
linearization for one of the multi-tone signals, whereas Fig.
21plotsthemeanSNDRoverallsignalsforeachinstanceof
theproposedandHammersteinlinearizers.
In this example, the SNR is approximately 53 dB with-
out distortion, whereas the SNDR is about 30 dB for the
distorted signals before linearization. As seen in Fig. 21,
with a linearizer filter order of M=2, the SNDR can be
enhanced by about 15 dB. With M=4, an additional 3 dB
SNDRimprovementcanbeachieved.Increasingtheorderto
M=12canfurtherenhancetheSNDRby3dB,totalinga21
dB improvement and approaching 51 dB, which is about 2
dB below the SNR. Beyond this level, additional increases
in the linearizer filter order yield progressively smaller im-
provements, making further enhancements computationally
inefficient.Hence,asforthepre-samplinglinearizer,thereisa
cleartrade-offbetweenadditionalcomputationalcomplexity
and SNDR improvement. For the Hammerstein linearizer,
the SNDR saturates at a somewhat lower level due to L - 2
regularization,whichisneededtokeepthemultipliervalues
smalltoavoidlargequantizationnoiseamplification,asdis-
cussedearlierinSectionIII.Finally,comparingthisexample
withExamples1-3,where12-bitdatawasused,itisseenthat
the data wordlength does not affect the robustness, but only
theSNDRlevels(compareFigs.7and21).
1) ImplementationComplexity
An observation from Fig. 21 is that the Hammerstein lin-
earizer appears slightly better than the proposed one when
increasing the number of branches for the case with M=2.
However, when comparing the SNDR against the number
of multiplications for both methods, the proposed linearizer

---

# Page 13

ThisarticlehasbeenpublishedinIEEEAccess.
50
45
40
35
30
5 10 20 40 80 160 320 640 1280
Numberofmultiplications
]Bd[RDNS
Distortedsignal
0
20
−
40
−
InitialSNDR
PL(M=2) HL(M=2) 60
PL(M=4) HL(M=4) −
PL(M=6) HL(M=6)
PL(M=8) HL(M=8) 80
−
0 0.2π 0.4π 0.6π 0.8π π
Linearizedsignal
FIGURE22. SNDRversusnumberofmultiplicationsinExample4.HerePL 0
standsfortheproposedlinearizerandHLfortheHammersteinlinearizer.
20
−
achievesahigherSNDRwithlowercomplexity.Thisisillus- 40
−
tratedinFig.22.
ItisseenthatforanychosenHammersteinlinearizercon- 60
−
figuration, there is always a configuration in the proposed
80
methodthatachievessuperiorperformancewithlowercom- −
0 0.2π 0.4π 0.6π 0.8π π
plexity. The savings range from a few percent up to about
60% depending on the scenario. For example, for M=4, to
reachanSNDRof46dB,theproposedlinearizerrequires30
multiplications,whereastheHammersteinlinearizerrequires
76,correspondingtoasavingof46/76≈60.5%.
Comparedwiththepre-samplinglinearizers,thedifference
incomplexityislargerhereforthepost-samplinglinearizers.
This is because the overall complexity of the static nonlin-
earities(·)p ismuchhigherheresinceseveralcopiesofthem
need to be implemented, and they have to be implemented
separately. In the pre-sampling case, one can share compu-
tations between the different nonlinearities, which is why it
sufficestocomputeK multiplicationsintotaltogenerateall
nonlinearities(·)p inFig.2.Hence,ingeneral,theproposed
linearizerismoreefficientinthepost-samplingcasethanin
thepre-samplingcase,whencomparingwiththecorrespond-
ingHammersteinlinearizers.
Example 5: To further illustrate the robustness of the
proposedpost-samplinglinearizer,wehavealsoevaluatedit
using the same type of multi-sine signal as in Example 4,
but with some subcarriers set to zero, and a bandpass fil-
tered white-noise signal covering 60% of the Nyquist band.
As illustrated in Figs. 23 and 24 for each of these signals,
essentially the same results are obtained as before. There is
lessthan1dBSNDRdegradationcomparedtothesignalsin
Example4forwhichthelinearizerwasdesigned.
V. LINEARIZATIONPERFORMANCEFOR
CIRCUIT-SIMULATEDDATA
Example6:Thisexamplewilldemonstratethattheproposed
design and linearizers also work when the reference signals
arenotknownbuthavetobeestimated.Forthispurpose,we
assesstheperformanceoftheproposedlinearizerappliedon
dataobtainedfromcircuitsimulationsinCadence,andagain
comparewiththeHammersteinlinearizer.
We use a dataset of distorted single-tone complex signals
]Bd[murtcepsedutilpmA
Normalizedfrequency[rad]
FIGURE23. Spectrumbeforeandafterlinearizationforamulti-sinesignal
withnullsubcarriersusingtheproposedlinearizerwithafilterorderof
M=6andN=16nonlinearbranches(Example5).
provided in an industry-collaboration project in which an
internal non-commercial ADC was designed. The signals
were initially generated at an RF frequency of 3.6 GHz and
subsequently demodulated to their corresponding complex
baseband signals. As this paper focuses on real signals, we
usetherealpartsofthesignalsintheevaluation.Further,in
the design of the linearizers, it is here necessary to estimate
thereferencesignals,asonlythefrequenciesareknownbut
not the exact gain and phase offsets of the signals. We have
usedtheleast-squaresbasedestimationtechniquedetailedin
Chapter1.6of[45]forthispurpose.
The signal frequencies are f=f ×[73,93,113]/L, where
s
the sampling frequency is f =10 GS/s and the signal length
s
is L=8192. It corresponds to the rounded frequencies
[89.1,113.5,137.9] MHz. The signal level is approximately
−1 dB full scale (dBFS). In the project, the focus was to
improvethespurious-freedynamicrange(SFDR),measured
in dBFS, which is why we use this metric here as well as
theSNDR.Further,asthebasebandsignalbandwidth(below
138MHz)ismuchsmallerthanthesamplingfrequency,we
use the pre-sampling linearizers in Section III (i.e., without
additionalinterpolation).
It is observed that the signals contain high-order nonlin-
earity terms. The x11-term is around −65 dBFS, whereas
powertermsabove11arebelow−80dBFS.Thenonlinear-
ities also have a rather strong frequency dependency, which
emanates from several sources (mixers, filters, and ADCs).
This leads to relatively high filter orders for the linearizer
filters when large SFDR improvements are targeted. This is
becauseabruptfrequencydependentchanges(corresponding

---

# Page 14

ThisarticlehasbeenpublishedinIEEEAccess.
Distortedsignal
0
20
−
40
−
60
−
80
−
0 0.2π 0.4π 0.6π 0.8π π
Linearizedsignal
0
20
−
40
−
60
−
80
−
0 0.2π 0.4π 0.6π 0.8π π
]Bd[murtcepsedutilpmA
Distortedsignal
0
20
−
40
−
60
−
80
−
100
−
120
−
140
−
0 1 2 3 4 5
Linearizedsignal
0
20
−
40
−
60
−
80
−
100
−
120
−
140
−
0 1 2 3 4 5
Normalizedfrequency[rad]
FIGURE24. Spectrumbeforeandafterlinearizationforabandpass
filteredwhite-noisesignalusingtheproposedlinearizerwithafilterorder
ofM=6andN=16nonlinearbranches.
tonarrowtransitionsbands)requirehighfilterorders[46].For
onlyafewsignals,onemayuselowerfilterorders,butthen
thequantizationnoisewillbeamplifiedduetoill-conditioned
filterdesign.
Usingtheproposedlinearizerwith9branches,tosuppress
all the nonlinearities to around −75 dBFS we need a filter
order of M=22. For this design, the SNDR is 68 dB. The
Hammerstein linearizer with the same number of branches
and filter order achieves practically the same SFDR and
SNDR. Recall that the performance of the proposed pre-
samplinglinearizeriscomparabletothatofthecorresponding
Hammerstein linearizer for larger values of M, both regard-
ing SNDR (and SFDR) improvements and implementation
complexity (see the discussion in Section III-C1). Again,
however, the proposed linearizer has the advantage that it
does not require internal data quantizations. The spectra of
thelinearizedsignalsareasshowninFig.25whenusingthe
proposedlinearizer.
For comparison, commercial GS/s-rate 12-bit ADCs op-
eratinginsimilarbandwidthregimestypicallyreportENOB
valuesaround8–10 (correspondingtoSNDRvaluesaround
50–62dB)andSFDRvaluesinthe65–78dBFSrangeunder
standard single-tone testing (see for example [47]). Hence,
the 68 dB SNDR and 75 dBFS SFDR obtained here after
linearizationrepresentstate-of-theartperformance.
VI. ALTERNATIVENONLINEARFUNCTIONS
In this paper, the nonlinear functions f (v) are chosen as
m
either the modulus or ReLU due to their simplicity and low
complexityinhardwareimplementation[27],[28].Wehave
]Bd[murtcepsedutilpmA
Frequency[GHz]
FIGURE25. Spectrumbeforeandafterlinearizationforsingle-tone
signals(superimposed)usingtheproposedlinearizerinExample6.
also considered other common nonlinear functions such as
the sigmoid, hyperbolic tangent, and exponential linear unit
(ELU), but they significantly increase the implementation
complexity for a targeted SNDR, as they require additional
multiplicationsandadditions.Toillustratethis,Fig.26shows,
forthesecond-orderdistortioninExample3,theperformance
ofthedifferentnonlinearfunctionsintermsofSNDRversus
the number of multiplications. As seen, the use of these
alternative nonlinear functions leads to worse performance
and substantially increased complexity compared to the use
ofthemodulus(orReLU)aswellastheHammersteinnon-
linearities.Here,thecomplexitieswhenusingthealternative
functions are based on their Taylor expansions with three
and five terms, and not counting trivial multiplications like
1/2.TheplotinFig.26alsoincludesthenonlinearfunction
leaky ReLU (with negative-slope coefficient α=0.1) which
leadstoalinearizerwithapproximatelythesamecomplexity
as for the Hammerstein linearizer (with the same number
of branches), but also with worse linearization performance
whenthenumberofbranchesisrelativelysmall.
Another alternative is the simple binary step function
which corresponds to 1-bit quantization. Thereby, the mul-
tiplications can be eliminated as their inputs are either zero
or one. However, it was shown in [48] for the frequency-
independent case (M=0, the only case considered in that
paper), that the linearizer then requires at least an order
of magnitude more branches than the proposed linearizer
(and also the Hammerstein linearizer), in order to achieve
the same moderate SNDR level (eight-bit data). For higher
SNDR levels, even two orders of magnitude more branches

---

# Page 15

ThisarticlehasbeenpublishedinIEEEAccess.
65
60
55
50
45
40
35
30
6 10 20 40 80 160 320
Numberofmultiplicationspersample
]Bd[RDNS
even when the nonlinearities have been generated through
InitialSNDR
Proposed(M=2) a Hammerstein model. This was demonstrated through nu-
Hammerstein(M=2)
ELU[3terms](M=2) merousdesignexamplesforvarioussignaltypesandscenar-
ELU[5terms](M=2)
ios, including both simulated and circuit-simulated data. In
general,theanalysisandsimulationsshowthattheproposed
linearizer is more efficient in the post-sampling case than
in the pre-sampling case, when comparing with the corre-
LeakyReLU(M=2)
Sigmoid[3terms](M=2) sponding Hammerstein linearizers. An additional advantage
Sigmoid[5terms](M=2)
HyperbolicTangent[3terms](M=2) of the proposed linearizer, over the Hammerstein linearizer,
HyperbolicTangent[5terms](M=2)
is that it eliminates the need for internal data quantizations,
therebyautomaticallyavoidingnoiseamplificationfromthe
quantizationstotheoutput.
A design procedure was also proposed in which the lin-
FIGURE26. SNDRversusthenumberofmultiplicationsfordifferent
nonlinearfunctions. earizer parameters are obtained through matrix inversion.
Thereby,onecancircumventthecostly,time-consuming,and
time-unpredictable iterative nonconvex optimization that is
may be required. This implies that the number of additions
traditionallyadoptedforneuralnetworktraining.Italsooffers
required will increase ten times or more and implies that
predictableonlinetrainingandreal-timeupdatesinresponse
thetotalimplementationcomplexitymayevenexceedthatof
tochangesincircuitry.Theproposeddesigneffectivelyhan-
the proposed linearizer. It was also shown in [48] that, with
dlesawiderangeofwidebandmulti-tonesignalsandfiltered
properly selected bias values, an alternative implementation
whitenoise.Simulationsdemonstratedsignificantsignal-to-
basedonlook-uptablescanbeused,therebyeliminatingall
noise-and-distortion ratio (SNDR) improvements of about
computationsexceptforoneadditionandonemultiplication.
20–30dBforboththesimulatedandcircuit-simulateddata.
The price to pay is the implementation cost of the look-
Further,relatedtohardwareimplementationcost,thepro-
uptablewhosememorysizeequalsthenumberofbranches
posedlinearizerscanachievethesameSNDRasthebench-
plusone(N+1).Thus,thatalternativeisattractiveprimarily
mark Hammerstein linearizers with a lower computational
forthefrequency-independentcaseandmoderateresolutions.
(arithmetic) complexity which correlates with the hardware
For the general frequency dependent case studied in this
implementation complexity. One can therefore conjecture
paper (M>0), an extension of that approach would become
thattheproposedlinearizerscanoffermoreefficienthardware
lessattractiveasthecostofthememorythenbecomeshigh,
implementationsthanHammerstein.Itwashoweverbeyond
especiallyforhigherresolutionsrequiringmanybranchesand
the scope of this paper to investigate hardware implementa-
because the memory size is here (N+1)×(M+1). It is also
tionsbutisleftforfuturework.Thefocusofthepaperwasto
noted that the look-up table approach proposed in [48] can
assessthefundamentalpropertiesoftheproposedlinearizers
onlybeextendedtothepre-samplinglinearizerinthispaper
and show that they are computationally more efficient than
(Fig. 3), not the post-sampling linearizer (Fig. 18). For the
theHammersteinlinearizers.
latter,onemayconsiderusingalook-uptableineachbranch,
Finally, it is noted that the proposed linearizers resemble
butthenthetotalmemorysizewouldgrowexponentiallyas
theHammersteinlinearizersinthatthefiltersappearafterthe
(N+1)×2M+1 which becomes prohibitive when M and N
nonlinear operations. Future work will also consider cases
increase.
where filters appear before the nonlinear operations, as in
To conclude, considering frequency dependent as well as
WienerandWiener-Hammersteinlinearizers(seethediscus-
pre-sampling-distortion and post-sampling-distortion mod-
sioninSectionI-A).
els, the modulus and ReLU are generally the most effi-
cientchoicesforlow-complexitylinearization,especiallyfor
APPENDIXA LEAST-SQUARESSOLUTION
higherresolutions.
The equation A w=b can be solved in the least-squares
r r
sensebyfindingw thatsatisfiesA ⊤A w=A ⊤b ,which
r r r r
VII. CONCLUSION yieldsw=(A ⊤A )−1A ⊤b [49].Forasetofsuchequa-
r r r r
Thispaperintroducedlow-complexitylinearizersforthesup-
tions,
pression of nonlinear distortion in ADIs. Two different lin- A w=b ,
e
e
a
a
r
r
i
i
z
ti
e
e
r
s
s
a
w
re
er
i
e
n
c
c
o
u
n
rr
s
e
i
d
de
a
r
f
e
t
d
e
,
r
b
a
a
n
s
d
ed
be
o
f
n
o
m
re
o
s
d
a
e
m
ls
p
w
lin
h
g
e
,
re
re
th
sp
e
e
n
c
o
ti
n
v
l
e
in
ly
- 
A
1
2
w=b
1
2
,
. (A.1)
(referred to as pre-sampling and post-sampling linearizers, .
respectively).Theproposedlinearizersareinspiredbyneural
 .
A w=b ,
networks but have an order-of-magnitude lower implemen- R R
tation complexity compared to traditional neural-network- theproblemcanberewrittenas
based linearizer schemes. The proposed linearizers can also
outperform the traditional parallel Hammerstein linearizers A w=b , (A.2)
stack stack

---

# Page 16

ThisarticlehasbeenpublishedinIEEEAccess.
with     [16] H.Deng,Y.Hu,andL.Wang,‘‘Anefficientbackgroundcalibrationtech-
A 1 b 1 niqueforanalog-to-digitalconvertersbasedonneuralnetwork,’’Integr.
A 2 b 2 VLSIJ.,vol.74,pp.63–70,Sep.2020.
A stack =  . .   , b stack =  . .   , (A.3) [17] X.Peng,Y.Mi,Y.Zhang,Y.Xiao,W.Zhang,Y.Tang,andH.Tang,‘‘A
 .   .  neuralnetwork-basedharmonicsuppressionalgorithmformedium-to-high
resolutionADCs,’’inProc.IEEEElectronDevicesTechnol.Manuf.Conf.
A b
R R (EDTM),Apr.2021,pp.1–3.
whichyields [18] M.Chen,Y.Zhao,N.Xu,F.Ye,andJ.Ren,‘‘Apartiallybinarizedand
fixedneuralnetworkbasedcalibratorforSAR-pipelinedADCsachieving
w=(A⊤ A )−1A⊤ b . (A.4) 95.0-dBSFDR,’’inIEEEInt.Symp.CircuitsSyst.(ISCAS),May2021.
stack stack stack stack [19] M. Fayazi, Z. Colter, E. Afshari, and R. Dreslinski, ‘‘Applications of
(cid:124) (cid:123)(cid:122) (cid:125) (cid:124) (cid:123)(cid:122) (cid:125)
A b artificial intelligence on the modeling and optimization for analog and
mixed-signalcircuits:Areview,’’IEEETrans.CircuitsSyst.I,Reg.Papers,
Thiscanbeequivalentlywrittenas
vol.68,no.6,pp.2418–2431,Jun.2021.
[20] D.Zhai,W.Jiang,X.Jia,J.Lan,M.Guo,S.-W.Sin,F.Ye,Q.Liu,J.Ren,
(cid:18) R (cid:19)−1 R
(cid:88) (cid:88) and C. Chen, ‘‘High-speed and time-interleaved ADCs using additive-
w= A⊤A A⊤b . (A.5)
r r r r neural-network-basedcalibrationfornonlinearamplitudeandphasedis-
r=1 r=1 tortion,’’IEEETrans.CircuitsSyst.I,Reg.Papers,vol.69,no.12,pp.
4944–4957,Dec.2022.
IncludingL -regularization(a.k.a.Tikhonovregularization),
2 [21] Z. Lu, B. Zhang, X. Peng, H. Liu, X. Ye, Y. Li, Y. Peng, Y. Xiao,
a diagonal matrix λI with small diagonal entries λ is added
W.Zhang,andH.Tang,‘‘Anewartificialneuralnetwork-basedcalibration
totheright-handsideof(A.5).Theresultingequationisthen
mechanismforADCs:Atime-interleavedADCcasestudy,’’IEEETrans.
equivalentto(7),withAandbin(8)andA r andb r defined VeryLargeScaleIntegr.(VLSI)Syst,vol.32,no.7,pp.1184–1194,May
inSectionIII-B. 2024.
[22] Y.Peng,Y.Xiao,L.Chen,H.Tang,andX.Peng,‘‘Anovelcalibration
algorithmforADCsbasedoninversemappingbyneuralnetwork,’’IEEE
REFERENCES
Trans.CircuitsSyst.II:ExpressBriefs,vol.71,no.7,pp.3283–3287,Feb.
[1] E. Björnson and Ö. Demir, Introduction to Multiple Antenna Commu- 2024.
nicationsandReconfigurableSurfaces. Delft,TheNetherlands:Now [23] L.Ljung,SystemIdentification:TheoryfortheUser,ser.PrenticeHall
Publishers,Inc.,2024. Information and System Sciences Series. Upper Saddle River, NJ:
[2] C.G.Tsinos,A.Kaushik,A.Arora,C.Masouros,F.Liu,andS.Chatzino- PrenticeHall,1999.
tas,‘‘Lowcomplexityjointradar-communicationsystemsdesignintheRF [24] Y.Mao,F.Ding,L.Xu,andT.Hayat,‘‘Highlyefficientparameterestima-
domain,’’IEEETrans.GreenCommun.Netw.,Apr.2025,earlyAccess. tionalgorithmsforHammersteinnon-linearsystems,’’IETControlTheory
[3] M.F.Haider,F.You,S.He,T.Rahkonen,andJ.P.Aikio,‘‘Predistortion- Appl.,vol.13,no.4,pp.477–485,Feb.2019.
basedlinearizationfor5Gandbeyondmillimeter-wavetransceiversys- [25] P.Gilabert,G.Montoro,andE.Bertran,‘‘OntheWienerandHammerstein
tems:Acomprehensivesurvey,’’IEEECommun.Surv.Tuts.,vol.24,no.4, modelsforpoweramplifierpredistortion,’’inProc.Asia–PacificMicrow.
pp.2029–2072,Aug.2022. Conf.(APMC),vol.2,Dec.2005,pp.1–4.
[4] H.Chu,X.Pan,J.Jiang,X.Li,andL.Zheng,‘‘Adaptiveandrobustchannel
[26] T.Sadeghpour,H.Karkhaneh,R.Abd-Alhameed,A.Ghorbani,I.T.E.
estimationforIRS-aidedmillimeter-wavecommunications,’’IEEETrans.
Elfergani,andY.A.S.Dama,‘‘Hammersteinpredistorterforhighpower
Veh.Technol.,vol.73,no.7,pp.9411–9423,Jul.2024.
RFamplifiersinOFDMtransmitters,’’inProc.URSIGen.Assem.Sci.
[5] Z.Zhao,X.Chen,F.Meng,Z.Yang,B.Liu,N.Zhu,K.Wang,K.Ma,
Symp(GASS),Aug.2011,pp.1–4.
andK.SengYeo,‘‘Designandanalysisofa22.6-to-73.9GHzlow-noise
[27] C.Tarver,A.Balatsoukas-Stimming,andJ.R.Cavallaro,‘‘Designand
amplifierfor5GNRFR2andNR-Umultiband/multistandardcommuni-
implementationofaneuralnetworkbasedpredistorterforenhancedmobile
cations,’’IEEEJ.Solid-StateCircuits,vol.60,no.9,pp.3189–3201,Sep.
broadband,’’in2019IEEEInt.WorkshopSignalProcess.Syst.(SiPS),Oct.
2025.
2019,pp.296–301.
[6] Interline, ‘‘Minimum 802.11 SNR Sensitivity,’’ https://interline.pl/
[28] D.R.LinaresandH.Johansson,‘‘Low-complexitymemorylesslinearizer
Information-and-Tips/Minimum-802.11-SNR-Sensitivity. Accessed on
foranalog-to-digitalinterfaces,’’inProc.24thInt.Conf.onDigitalSignal
2025-11-21.
Process.(DSP),Rhodes,Greece,Jun.2023,pp.1–5.
[7] M.Valkama,A.ShahedHaghGhadam,L.Anttila,andM.Renfors,‘‘Ad-
[29] J.TsimbinosandK.V.Lever,‘‘InputNyquistsamplingsufficestoidentify
vanceddigitalsignalprocessingtechniquesforcompensationofnonlinear
andcompensatenonlinearsystems,’’IEEETrans.SignalProcess.,vol.46,
distortioninwidebandmulticarrierradioreceivers,’’IEEETrans.Microw.
no.10,pp.2833–2837,Oct.1998.
TheoryTech.,vol.54,no.6,pp.2356–2366,Jun.2006.
[30] R. Vansebrouck, C. Jabbour, O. Jamin, and P. Desgreys, ‘‘Fully-digital
[8] M.Valkama,M.Renfors,andV.Koivunen,‘‘AdvancedmethodsforI/Q
blindcompensationofnon-lineardistortionsinwidebandreceivers,’’IEEE
imbalancecompensationincommunicationreceivers,’’IEEETrans.Signal
Trans.CircuitsSyst.I:Reg.Papers,vol.64,no.8,pp.2112–2123,Aug.
Process.,vol.49,no.10,pp.2335–2344,Oct.2001.
2017.
[9] B.Murmann,‘‘ADCperformancesurvey1997-2024,’’https://github.com/
bmurmann/ADC-survey.Accessedon2025-11-21. [31] Z. Liu, X. Hu, L. Xu, W. Wang, and F. M. Ghannouchi, ‘‘Low com-
[10] TexasInstruments(ADC12DJ5200SE),‘‘10.4GSPSSingle-Channelor5.2 putationalcomplexitydigitalpredistortionbasedonconvolutionalneural
GSPSDual-Channel,12-bit,RF-SamplingAnalog-to-DigitalConverter,’’ networkforwidebandpoweramplifiers,’’IEEETrans.onCircuitsSyst.II:
https://www.ti.com/product/ADC12DJ5200SE,2023,Accessed:2025-11- ExpressBriefs,vol.69,no.3,pp.1702–1706,Mar.2022.
21. [32] S.Li,G.Zhao,C.Yu,F.Li,andY.Liu,‘‘Powerscalableneuralnetwork
[11] T.L.Marzetta,E.G.Larsson,H.Yang,andH.Q.Ngo,Fundamentalsof modelforwidebanddigitalpredistortion,’’IEEEMicrow.Wirel.Technol.
MassiveMIMO. Cambridge,U.K.:CambridgeUniv.Press,2016. Lett.,vol.33,no.12,pp.1658–1661,Dec.2023.
[12] W.A.Frank,‘‘SamplingrequirementsforVolterrasystemidentification,’’ [33] C.Jiang,G.Yang,R.Han,J.Tan,andF.Liu,‘‘Gateddynamicneuralnet-
IEEESignalProcess.Lett.,vol.3,pp.266–268,Sep.1996. workmodelfordigitalpredistortionofRFpoweramplifierswithvarying
[13] H.-W.Chen,‘‘Modelingandidentificationofparallelnonlinearsystems: transmissionconfigurations,’’IEEETrans.Microw.TheoryTech.,vol.71,
structuralclassificationandparameterestimationmethods,’’Proc.IEEE, no.8,pp.3605–3616,Aug.2023.
vol.83,no.1,pp.39–66,Jan.1995. [34] P. Ghazanfarianpoor, S.-H. Javid-Hosseini, F. Abbasnezhad, A. Arian,
[14] S.Xu,X.Zou,B.Ma,J.Chen,L.Yu,andW.Zou,‘‘Deep-learning-powered V. Nayyeri, and P. Colantonio, ‘‘A neural network-based pre-distorter
photonicanalog-to-digitalconversion,’’LightSci.Appl.,vol.8,no.66,Jul. forlinearizationofRFpoweramplifiers,’’in202322ndMediterranean
2019. Microw.Symp.(MMS),Oct.2023,pp.1–4.
[15] Y.Xiang,M.Chen,D.Zhai,Y.Zhao,J.Ren,andF.Ye,‘‘Aneuralnetwork [35] G.PrasadandH.Johansson,‘‘Alow-complexitypost-weightingpredis-
basedbackgroundcalibrationforpipelined-SARADCsatlowhardware torterinamMIMOtransmitterundercrosstalk,’’IEEECommun.Lett.,
cost,’’ElectronicsLetters,vol.59,no.15,pp.1–3,Aug.2023. vol.27,no.12,pp.3315–3319,Dec.2023.

---

# Page 17

ThisarticlehasbeenpublishedinIEEEAccess.
[36] G. Prasad, H. Johansson, and R. Hussain Laskar, ‘‘A general approach HÅKAN JOHANSSON (S’97–M’98–SM’06)re-
tofullylinearizethepoweramplifiersinmMIMOwithlowcomplexity,’’ ceived the Master of Science degree in Com-
IEEETrans.Commun.,vol.73,no.7,pp.4749–4765,Dec.2025. puter Science and Engineering, and the Licenti-
[37] S.-H.Javid-Hosseini,P.Ghazanfarianpoor,V.Nayyeri,andP.Colantonio, ate,Doctoral,andDocentdegreesinElectronics
‘‘A unified neural network-based approach to nonlinear modeling and Systems,fromLinköpingUniversity,Sweden,in
digitalpredistortionofRFpoweramplifier,’’IEEETrans.Microw.Theory 1995,1997,1998,and2001,respectively.During
Tech.,vol.72,no.9,pp.5031–5038,Sep.2024.
1998 and 1999 he held a postdoctoral position
[38] K.K.Parhi,VLSIDigitalSignalProcessingSystems:DesignandImple-
with the Signal Processing Laboratory, Tampere
mentation. Hoboken,NJ,USA:JohnWiley&Sons,2007.
UniversityofTechnology,Finland.Heiscurrently
[39] I.Koren,ComputerArithmeticAlgorithms,SecondEdition,ser.AkPeters
aProfessorattheDivisionofCommunicationSys-
Series. Natick,MA,USA:Taylor&Francis,2001.
tems,DepartmentofElectricalEngineering,LinköpingUniversity.Hewas
[40] L.B.Jackson,DigitalFiltersandSignalProcessing(3rdEd.). Boston,
MA,USA:KluwerAcademicPublishers,1996. one of the founders of the spin-off company Signal Processing Devices
[41] L. Wanhammar and H. Johansson, Digital Filters Using MATLAB. SwedenABin2004(nowTeledyneSPDevices).Hisresearchencompasses
Linköping,Sweden:LinköpingUniv.,2013. theory,design,andimplementationofefficientandflexiblesignalprocessing
[42] P.P.Vaidyanathan,MultirateSystemsandFilterBanks. EnglewoodCliffs, systemsforvariouspurposes.Hehasauthoredorco-authoredfourbooksand
NJ:PrenticeHall,1993. some80journalpapersand150conferencepapers.Hehasco-authoredone
[43] H.M.Bahig,M.H.El-Zahar,andK.Nakamula,‘‘Someresultsforsome journalpaperandtwoconferencepapersthathavereceivedbestpaperawards
conjectures in addition chains,’’ in Combinatorics, Computability and andauthoredorco-authoredthreeinvitedjournalpapersandfourinvited
Logic. London,U.K.:SpringerLondon,2001,pp.47–54. bookchapters.Healsoholdseightpatents.HeservedasaTechnicalProgram
[44] H.JohanssonandO.Gustafsson,‘‘Linear-phaseFIRinterpolation,deci- Co-ChairforIEEEInt.SymposiumonCircuitsandSystems(ISCAS)2017
mation,andMth-bandfiltersutilizingtheFarrowstructure,’’IEEETrans. and2025.HehasservedasanAssociateEditorforIEEETrans.onCircuits
CircuitsSyst.I,vol.52,no.10,pp.2197–2207,Oct.2005.
and Systems I and II, IEEE Trans. Signal Processing, and IEEE Signal
[45] P.Löwenborg,Mixed-SignalProcessingSystems,2nded. Linköping,
Processing Letters, and as an Area Editor for Digital Signal Processing
Sweden:LinköpingUniversity,2006.
(Elsevier).
[46] K.Ichige,M.Iwaki,andR.Ishii,‘‘Accurateestimationofminimumfilter
length for optimum FIR digital filters,’’ IEEE Trans. Circuits Syst. II,
vol.47,no.10,pp.1008–1016,Oct.2000.
[47] Texas Instruments, ‘‘Analog-to-digital converters (ADCs): High-Speed
ADCs.’’ https://www.ti.com/product-category/data-converters/adcs/
high-speed/overview.html,accessed:2025-11-21.
[48] D.R.LinaresandH.Johansson,‘‘Digitallinearizerbasedon1-bitquanti-
zations,’’inProc.IEEEInt.Conf.Commun.Technol.(ICCT),Oct.2024,
pp.1659–1663.
[49] T. Hastie, R. Tibshirani, and J. Friedman, The Elements of Statistical
Learning:DataMining,Inference,andPrediction,2nded.,ser.Springer
SeriesinStatistics. NewYork,NY,USA:Springer,2009.
DEIJANYRODRIGUEZLINARES(GraduateStu-
dent Member, IEEE) received the Bachelor of
Science in Nuclear Engineering, a Postgraduate
Diploma in Medical Physics and the Master of
Science degree in Nuclear Engineering from the
HigherInstituteofTechnologiesandAppliedSci-
ences(InSTEC),UniversityofHavana,Cuba,in
2015,2016and2018,respectively.Heiscurrently
pursuingaPh.D.degreewiththeDivisionofCom-
municationSystems,DepartmentofElectricalEn-
gineering,LinköpingUniversity,Sweden.From2019to2020,hewasan
AssociateResearcheratInSTEC,andfrom2015to2018,heworkedasa
JuniorMedicalPhysicistattheCubanStateCenterfortheControlofDrugs,
Equipment and Medical Devices (CECMED). Since 2019, he has been a
JuniorAssociateoftheAbdusSalamInternationalCentreforTheoretical
Physics (ICTP), Trieste, Italy. His research interests include signal pro-
cessing,wirelesscommunication,reinforcementlearning,andmathematical
optimization.