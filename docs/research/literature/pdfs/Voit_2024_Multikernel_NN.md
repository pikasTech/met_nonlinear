# Page 1

1
Multiplant Nonlinear System Identification by
Block-Structured Multikernel Neural Networks in
Applications of Interference Cancellation
Svantje Voit, Student Member, IEEE, and Gerald Enzner, Senior Member, IEEE
Abstract—Problemsoflinearsystemidentificationhaveclosed- The process of interference cancellation is crucial in ap-
form solutions, e.g., using least-squares or maximum-likelihood plications like acoustic echo cancellation (AEC) in hands-free
methods on input-output data. However, already the seemingly
systemsforspeechcommunication[1]–[4]orself-interference
simplestproblemsofnonlinearsystemidentificationpresentmore
cancellation (SIC) in full-duplex radios for wireless com-
difficulties related to the optimisation of the furrowed error
surface.ThosecasesincludetheHammersteinplantwithtypically munication [5]–[9]. In hands-free speech communication, a
a bilinear model representation based on polynomial or Fourier microphone not only receives the desired speech from the
expansion of its nonlinear element. Wiener plants induce actual near end, but also an acoustic echo of the far-end voice.
nonlinearity in the parameters, which further complicates the
The cancellation of this echo signal by estimating the echo
optimisation. Neural network models and related optimisers
path model is required as an important subtask in acoustic
are, however, well-prepared to represent and solve nonlinear
problems.Unfortunately,theavailabledatafornonlinearsystem echo control systems. Similarly, inband full-duplex radios
identification might be too diverse to support accurate and simultaneously transmit and receive through the same time
consistent model representation. This diversity may refer to and frequency resource. The desired signal from a remote
different impulse responses and nonlinear functions that arise
side thus cannot be reliably restored at the receiver since
in different measurements of (different) plants. We therefore
the signal emitted by the transmitter strongly penetrates the
propose multikernel neural network models to represent non-
linear plants with a subset of trainable weights shared between receiver chain as self-interference. Very accurate cancellation
differentmeasurementsandanothersubsetofplant-specific(i.e., of the self-interference is required here.
multikernel) weights to adhere to the characteristics of specific Inbothcases,thenonlinear(NL)plant,i.e.,theechoorself-
measurements.Wedemonstratethatinthiswaywecanfitneural
interference path, impedes the modelling of the interference
network models to the diverse data which cannot be done with
process that needs to be compensated. In the acoustic system,
some standard methods of nonlinear system identification. For
model testing, the subset of shared weights of the entire trained high playback volumes on small transducer geometries cause
model is reused to support the identification and representation the loudspeaker to introduce nonlinear behaviour [10]. In
of unseen plant measurements, while the plant-specific model wirelesssystems,nonlinearitiescanbefoundintermsofpower
weights are readjusted to specifically meet the test data.
amplifiers [11] or analogue-to-digital converters [12] with
Index Terms—Nonlinear system identification, neural net- saturationorclippingbehaviours.Astheseapplicationsexhibit
works, adaptive filters nonlinear aspects that need to be modelled as accurately
as possible to achieve the desired cancellation, the use of
classical linear system identification models would be limited
I. INTRODUCTION
to insufficient results [13], [14].
INTERFERENCE cancellation typically relies on plant
The task of nonlinear system identification has been ap-
identification in order to duplicate and compensate unde-
proached by different model classes. Nonlinear stochastic
sired interference from a primary observation signal that also
state-space models are a very general framework applied to
contains an information-bearing desired signal. The goal is to
the AEC problem, where the nonlinearity is captured by
enhancetheaccessibilityoftheinformationinthedesiredsig-
sampled distributions [15] or functional expansions [16], [17]
nal by subtracting an estimated interference from the primary
around an acoustic system state. Another very general class
signal.Todoso,theprimarysignalservesasatargetresponse
is given by nonlinear autoregressive moving average models
for an interference plant model. An auxiliary signal, which
with exogenous inputs (NARMAX) [18], [19]. Here, the
is ideally independent from the information-bearing signal,
model is a general function on a sequence of past inputs,
serves as the model input. The model parameters (in some
outputs and noise terms. It is initially formulated in a very
cases termed filter coefficients) are then adjusted in a system
abstractwaybeforebeingfurtherspecifiedasamoreconcrete
identification fashion to match the model output to the actual
model the parameters of which can be estimated. If domain-
interferencelinkedtothesameauxiliarysignalbytheinitially
knowledge allows, the model architecture can be reduced to a
unknown plant. The model structure must be architected for
subsystemofthegeneralNARMAXframework,whereby,e.g.,
its capability of representing the plant, while the actual plant
the Volterra model [20], the block-structured models, such as
structure is assumed to be available as domain-knowledge.
Wiener [21] or Hammerstein [22], memory polynomials [11],
[23], and many neural network architectures [24], [25] can be
ThisworkwassupportedbygrantDFGEN869/4-1,projectno.449601577.
regarded as special cases.
4202
ceD
01
]PS.ssee[
1v07370.2142:viXra

---

# Page 2

2
When dealing with applications, such as AEC and SIC, s[n]
domain-knowledgeisalwaysprovidedtojustifymorespecific
x[n] d[n] y[n] e[n]
modelarchitectures,pavingthewayforaphysicallymotivated Plant + +
designtolocalisebothlinearandnonlinearsystemcomponents
−
and allowing for systematic evaluation of the components.
However,thereisalwaysatrade-offbetweenalgorithmiccom-
d[n]
plexityandmodellingcapability[15]–[17],[26]–[32].Volterra Model
series, for instance, can represent a variety of nonlinear b
optimise
behaviours, but are associated with large computational effort
hampering practical relevance. An implementation of Volterra
Fig.1. Interferencecancellationusingamodelbasedonsystemidentification.
series higher than second order may be unrealistic, although
it might be physically necessary. Models are therefore often
restricted to a memory element before or after a memoryless across the data, while another set of multikernel weights is
nonlinearity,i.e.,modelsconsistingofastaticnonlinearblock adjusted for plant-specific representation. We initially validate
surrounded by one or two dynamic linear blocks. These the framework with white-noise data and further apply it
block structures are called Wiener, Hammerstein or Wiener- to more realistic problems, such as AEC with Hammerstein
Hammerstein, depending on the respective block order. nonlinearity and SIC with Wiener nonlinearity.
Neural networks can be a powerful tool for redesigning the
The paper is organised as follows: Section II describes
trade-off, as the simple Wiener or Hammerstein nonlinearity
the general cancellation problem. Section III outlines the
can be easily represented and extended by creating more
plant-specific diversity of block-structured nonlinear systems.
complex models bottom-up when further modelling capability
Section IV reviews classical methods for nonlinear modelling
is required according to more specific domain-knowledge.
as well as the neural-network approximation. Plant-specific
Neuralnetworkswereusedinapplicationswheresystemiden-
modelling via the multikernel approach is introduced in Sec-
tificationisdesirable,butthenetworkswerenotconfiguredso
tion V, which is then combined in Section VI with shared
astomeetthesystemidentificationpurpose.Insomecases,not
nonlinear modelling to form multikernel neural networks, the
onlytheauxiliaryreferencesignalisfedintothemodel,which
functionality of which is also demonstrated in this section.
is necessary to enforce nonlinear plant representation, but
Sections VII and VIII examine the approach in specific areas
also the primary observation signal appears as an input [33]–
ofapplication,i.e.,theacousticechocancellationandtheself-
[37]. These ”look-alikes” of plant modelling do not enforce a
interference cancellation, respectively. Section IX concludes.
decorrelation of the network output from the desired signal,
since the desired signal is part of the network input via the
primarysignal.Subtractionofthemodeloutputsignalfromthe II. CANCELLATIONPROBLEMFORMULATION
primary signal can therefore distort the desired signal during
the interference cancellation. Ininterferencecancellation,amodelisemployedtoidentify
The public availability of realistic datasets further supports andcancelanundesiredinterferenced[n]presentinaprimary
the development of neural networks for nonlinear modelling. signaly[n],whichalsocontainsaninformation-bearingsignal
ForrealisticexperimentsinAECapplications,dataisprovided components[n].Fig.1depictssuchasetup.Here,theprimary
withinthepopularAECchallengedatabase[38].Forthewire- signal y[n] = d[n]+s[n] is used as the desired response of
lessapplication,theWLANtoolbox[39]allowsthesimulation themodel.Anauxiliarysignalx[n]servesasthemodelinput,
of realistic data [14] for the development of SIC models. In whilstthisauxiliarysignalisobtainedfromareferencesensor
both domains, the underlying plants can be considered as which is designed such that the information-bearing signal in
a block-structured transmission path consisting of different the primary signal is not detectable via the reference signal
linear and nonlinear components. The data shows that plant and is therefore physically independent.
diversity remains a problem in the use of neural networks The method of interference cancellation structures and ad-
and, to our knowledge, has not yet been fully addressed. The justs weights of the model so that its output d[n] at discrete
desired variability w.r.t. different plants is achieved in [40] time n matches the interference d[n], which is linked to the
by replacing parts of the network with an adaptive filter in auxiliaryreferencesignalx[n]throughanunkno(cid:98)wnplant.This
the test mode. For network training, however, the data must method can be understood as system identification in which
be constrained to consistent room impulse responses therein. the plant is identified using a most appropriate model. Here,
Thesystemin[41],supposedly,determinesavariablenetwork potential nonlinearities in the system must be included in the
model individually for each given input signal, i.e., instead model structure, such that the interference cancellation is able
of identifying a general nonlinearity across all plants, a fully to subtract the estimated interference d[n] from the primary
plant-specific identification is performed. signal y[n] with best fidelity to d[n]. The optimal result is an
Inthispaper,weintroduceaframeworktorepresentshared error signal e[n] = y[n] d[n] that con(cid:98)veys only the desired
−
and variable plant behaviour in the training and evaluation signal s[n], effectively removin(cid:98)g any component related to
of system identification neural networks. By leveraging do- x[n]. This process of inter(cid:98)ference cancellation is crucial in
main knowledge of the plant, we propose multikernel neural applications where isolating the interference signal is vital for
network models with a subset of its trainable weights shared further processing or analysis.

---

# Page 3

3
The Wiener structure [42], [43] is defined as a dynamic
f[κ]()
block followed by a static nonlinear block to create an overall
x[n] · d[n]
h[κ] model of nonlinearity with memory. In addition, a distinction
is made between cascaded and parallel [11], [41] Wiener
structures, whereby the cascaded structure is a special case
(a)Wienerstructure. of the parallel structure. The parallel structure results as a
sumofmultipleWienerstructures[32],therefore,iftheentire
structureiscomposedofonlyoneWienersubsystem,itresults
f[κ](x[n])
x[n] d[n] inthecascadedversion.ItisshowninFig.2a,wheretheinput
h[κ] x[n] is first processed by convolution related to the dynamic
block with impulse response h[κ][n] and then by the static
nonlinear function f[κ]() such that the output signal reads
(b)Hammersteinstructure. ·
L
Fig.2. Plantswithdifferentnonlinearblock-structures. d[n]=f[κ] h[κ][m]x[n m] . (1)
(cid:32) − (cid:33)
m=0
(cid:88)
Wienermodellingisaseeminglysimplemethodofcombining
III. BLOCK-STRUCTUREDNONLINEARMULTIPLANTS
memory and nonlinearity, however, its nonlinearity in the
parameters challenges the system identification [44], [45].
Domain-knowledge is the basis for designing model-based
The Hammerstein structure consists of a static nonlinearity
prototypes of plant structures that consist of dynamic linear
followed by a dynamical block [46]–[48] and thus can be
and static nonlinear blocks, which may appear in different
linear in the parameters (if the nonlinear function is pre-
constellations for certain application areas. A dynamic block
determined). Parallel [16] and cascaded [17] Hammerstein
represents linear-time-invariant (LTI) behaviour, i.e., typically
structures exist in the applications, whereby parallel struc-
with memory, which can be characterised by an impulse
tures are formed as a summation of multiple Hammerstein
responsemodeloftheblock.Consideringdifferentrealisations
subsystems, enabling the representation of nonlinearity with
or measurements of plants to be formally represented in this
memory.AcascadedHammersteinstructureemploysthesame
paper as multiplants, we introduce a plant-specific impulse
linear dynamical block for each subsystem and thus collapses
response h[κ][n] for a dynamical block of plant κ. Here, the
tothemodellingofnonlinearitieswithoutmemory.Itisshown
plant index κ depicts an additional dimension of system rep-
in Fig. 2b and, according to the commutation of convolution
resentation beyond classical LTI theory. Our intention hereby
and nonlinear mapping compared to the Wiener structure, the
is to describe significant system variability across different
output signal of Hammerstein structures differently reads
observations (i.e., sample data in the neural network context)
while assuming LTI behaviour per observation. Static blocks L
then refer to memoryless nonlinear functions f[κ](x[n]) for d[n]= h[κ][m]f[κ](x[n m]) . (2)
−
which it is not possible to describe a convolutive input-output m (cid:88) =0
relationship or commutativity with its input x[n]. As before, With its linearity in the parameters, it can more easily be
the dimension κ shall here represent potential variability of employed with linear estimation algorithms [26], [49].
the respective block across sample data of a plant structure, ThereareaswellmixedformsofWienerandHammerstein
whilethenonlinearfunctionisstillassumedtobefixedwithin structures,i.e.,Wiener-Hammersteinstructures,thatforexam-
a single observation sequence of plant κ. pleconsistofastaticblocksandwichedbetweentwodynamic
blocks. This paper, however, will not cover all possibilities of
For both block-types, we will distinguish between variant
domain-specific plant representation.
and invariant blocks. While those variant blocks or variant
plants made from such blocks were indexed with the κ, their
IV. NONLINEARFUNCTIONREPRESENTATION
invariant counterparts will be denoted as dynamical blocks
with impulse responses h[κ][n] = h[n] or static blocks with In none of the structures, the actual nonlinear function is
nonlinear function f[κ](x[n]) = f(x[n]) across all samples typically known a-priori in closed form. Therefore, a para-
κ=1,...,K of a multiplant. Consequently, invariant blocks metric representation f(x[n];a p ,b p ) is needed to set up and
can be understood as a special case of variant ones. fit the function. Before, the terminology of functions being
linear or nonlinear in the parameters is briefly clarified. To
In order to contrast with block structures, we recall the
this end, a functional form
Volterra series expansions as a very abstract and contained
structure to model a plant. It can form a variety of nonlinear P
functions, but potentially requires a huge number of parame- f(x[n];a p ,b p )= a p Φ p (x[n]; b p ) (3)
ters,whichisincreasingsuperlinearlywithincreasingmemory p=1
(cid:88)
and polynomial order, and is therefore limited to applications is considered, where the function output is determined via the
with low system orders [42], [43]. The following provides input x[n], the parameters a and b , and the nonlinear basis
p p
an overview of common block-structured nonlinear models functions Φ (). The function f(x[n];a ,b ) is then linear in
p p p
·
with a deliberately small number of parameters and restricted its parameters a that directly relate to the function output,
p
application based on dedicated domain knowledge. while nonlinear in the parameters b of the basis functions.
p

---

# Page 4

4
A. Representations with Linearity in the Parameters
x
1
Parametric expansions can be specified by fixed basis func-
x
tions Φ () weighted by linear coefficients a , while any 2
p p · nonlinear coefficients b are discarded.
p
Oneimportantrepresentationisthepowerserieswithprim-
itive polynomials of x[n] as the basis functions,
P
f (x[n]; a )= a xp[n], (4)
power p p
p=1
(cid:88)
typically assuming the range 1<x[n]<1 for stability, and
−
the parameters to be estimated are the p-th coefficients a of
p
the P-th order polynomial. Optimality of the coefficients may
be designated in terms of the least-squares error between the
parametric representation and the actual nonlinear function:
2
+1 P
a =argmin f(x[n]) a xp[n] dx[n]. (5)
p p
ap (cid:90)−1 (cid:32) − p=1 (cid:33)
(cid:88)
A(cid:98)nother representation relies, for instance, on the odd
Fourier series with orthogonal sinusoidal basis functions,
P
x[n]
f (x[n]; a )= a sin 2π p , (6) fourier p p
· · T
p=1 (cid:18) x (cid:19)
(cid:88)
with a hyperparameter T defining the fundamental period
x
(i.e., effectively the x[n] range) of a periodical function. The
linear parameters for least-squares functional approximation
are known as the odd Fourier coefficients
2 Tx/2 x[n]
a = f(x[n]) sin 2π p dx[n]. (7)
p
T · · · T
x (cid:90)−Tx/2 (cid:18) x (cid:19)
Whether the basis functions qualify for good representation
(cid:98)
depends on the target function f(x[n]), on the input x[n],
specifically the adequate range and the distribution of the
input, and on the manageable nonlinear order P.
B. Representation with Nonlinearity in the Parameters
In our applications we would require arbitrary placement
of a nonlinear function in a block structure and we would
havetocopewithpotentiallyuncertaininputsignalrange.We
thus like to have control over the range of the input signal
before the nonlinearity takes place and therefore introduce a
nonlinear function representation by neural networks, specifi-
callythemulti-layerperceptron(MLP)[50],[51].Itconsistsof
ℓ=1,...,D 1 hidden layers each with p =1,...,P output
ℓ ℓ
− channelsandnonlinearinput-outputrelationintheparameters,
Pℓ
f [n]=tanh b f [n] , (8)
pℓ+1 pℓ+1,pℓ pℓ
(cid:32) (cid:33)
p (cid:88)ℓ=1
with the first layer input f [n] = x [n], p = 1,...,P , and p0 p0 0 0
P = I denotes available input channels. The typical tanh- 0
activations conclude the arithmetic logic of each hidden layer.
For regression a linear output layer may finally aggregate the
available nonlinear representations of the last hidden layer as
PD
f x[n]; a ,b = a f [n]. (9)
p p,pD pℓ+1,pℓ p,pD pD
(cid:0) (cid:1)
p (cid:88)D=1
...
f
1
NL block
f
2
b pℓ+1,pℓ
x I a p,pD
...
f P
Fig.3. NonlinearmemorylessblockwhichmapsanI-dimensionalinputto
anonlinearP-dimensionaloutputusinginternaltanh-activations.
The MLP-based nonlinear block is thus denoted as these
stacked D +1 layers with its trainable parameters a and b,
the input dimensionality I, and output dimensionality P as
showninFig.3.Thisnonlinear(NL)blockcanbewellplaced
in arbitrary positions of a model structure as the nonlinear
parameters b are capable of controlling the block’s input and
the linear parameters a its output, respectively.
Our implementation of this NL block (using PyTorch
functions) employs D + 1 layers of 1D-Conv specification
with kernelsize of one for memoryless nonlinearity. In this
case, the padding does not matter. The input-tensor then
X
consists of three dimensions (K,I,M), where K denotes
different realisations of a plant structure, I the input-channel
dimensionality, and M the number of time samples of an
input sequence x[n]. For a single-channel time-domain input
signal it holds I =1. According to (8) and (9), the NL block
then maps the input to an output tensor with dimension
F
(K,P,M). Here, the second tensor dimension forms a P-th
order nonlinear expansion. The first tensor dimension remains
untouched for parallel processing and overall loss minimisa-
tion.Theblock’strainableweightsaandbarethussharedfor
system identification across the different plant observation.
V. LINEARMULTIKERNELREPRESENTATION
We briefly recap that Section III has introduced the di-
mension of plant variability in problems of nonlinear system
identification. Section IV has described the possibility of
neuralnetworkmodellingtorepresentthenonlineardimension
in those problems of nonlinear system identification. Given
the trend of large datasets for the optimisation of neural
networks, the purpose of this upcoming section is to address
the issue of plant variability within a dataset by describing a
corresponding neural network representation. Specifically, the
idea is to oppose to the dimension of plant variability the
dimension of multikernel representation in the networks. The
multikernel approach thus invokes multiple specific kernels to
representthespecificplantsofspecificdatasamples.However,
thismultikernelrepresentationisnotnecessarilydevotedtoan
entire model architecture under consideration for the system
identification problem. Here in this section we thus introduce
themultikernelapproachonlyforthelinear(yetimportantfor
system modelling) layers of an entire model.
A. Time-Domain FIR Block
LTI behaviour of a plant component with input x[n] can
be modelled by FIR filtering with impulse response w[l] at
lag indices l = 0,...,L 1. The corresponding input-output
−

---

# Page 5

5
x
1
x
2
...
d
FIR block 1
d
2
w[l,κ,i,p]
x I
...
As a baseline for the proposed multikernel model, for the
sake of clarity, we write out a single-kernel model, i.e.,
I L−1
d[t,m,κ,p]= x[t,m l,κ,i]w[l,i,p], (15)
d P −
i=1 l=0
(cid:88)(cid:88)
where the plant index is dropped from the multikernel in
Fig. 4. Multikernel FIR-Block which maps a I-dimensional input on a P- (14), while it persists with input and output sequences. This
dimensionaloutputtomodelLTIbehaviourwithmemoryL. essentially means that the kernel w[l,i,p] is conventionally
shared across the data samples corresponding to different
plants, which, supposedly, hampers minimum mean-square
relationship of the plain FIR model at discrete time step n is
error representation of data samples by the model.
then written by convolution as simple as
L−1 B. Frequency-Domain FIR-Block Representation
d[n]= x[n l]w[l], (10)
− Based on the success story of frequency-domain represen-
l=0
(cid:88) tations for adaptive online learning of FIR filters [26], specif-
with one-dimensional signal x[n] and one-dimensional convo- ically in the field of speech processing [1], [52], this method
lutional kernel w[l]. For versatile representation in the neural is here adopted with the hypothesis of potentially advanced
network context, several additional dimensions are required. learning in the context of neural-network representation. We
In order to support system identification with K different therefore provide a kernel definition with zero padding in the
plants or different observations of a plant, a two-dimensional convolutive dimension of the original temporal time steps,
inputsequencex[n,κ]andatwo-dimensionalkernelw[l,κ]of
w[m,κ,i,p] m=0,...L 1
shape(L,K)arerequiredforrepresentation.Theinput-output w z [m,κ,i,p]= 0 m=L,...M − 1,
relationship is then given by (cid:26) − (16)
of kernel shape (L+R 1,K,I,P) with the previous con-
L−1 −
strainingtoM =L+R 1.ItsM-dimensionalrepresentation
d[n,κ]= x[n l,κ]w[l,κ], (11)
−
− in the discrete Fourier transform (DFT) domain is
l=0
(cid:88)
M−1
where the plant index κ reproduces from the input to the out- W[k,κ,i,p] = w [m,κ,i,p]e−ȷ2πmk/M (17)
put.Formultiple-inputmultiple-output(MIMO)representation z
m=0
ofdifferentplants,werequireathree-dimensionalinputsignal (cid:88)
L−1
x[n,κ,i] and a four-dimensional kernel w[l,κ,i,p] of shape = w[l,κ,i,p]e−ȷ2πlk/M (18)
(L,K,I,P) to deliver a three-dimensional output as
l=0
(cid:88)
I L−1 with discrete frequency index k =0,...,M 1. Further using
−
d[n,κ,p]= x[n l,κ,i]w[l,κ,i,p], (12) the input signal in the DFT domain along the m-dimension,
−
(cid:88) i=1 (cid:88) l=0 M−1
X[t,k,κ,i]= x[t,m,κ,i]e−ȷ2πmk/M , (19)
where I and P here denote the multiple-input and multiple-
output dimensionality, respectively. Further considering a seg- m (cid:88) =0
mentation of the input sequences according to where merely the time step index m is converted into the dis-
crete frequencies k, we can obtain the predicted output signal
x[t,m,κ,i]=x[tR+m,κ,i], (13) in the time domain by elementwise spectral multiplication of
matching dimensions in the DFT domain and inverse DFT,
with m = 0,...,M 1, the new time step index of the
− I
subsequences or ”frames”, M the frame length, t the frame
D[t,k,κ,p] = X[t,k,κ,i]W[k,κ,i,p] (20)
index, R the frame shift, and thus M R the frame overlap,
− i=1
wegotafour-dimensionalinputsignalx[t,m,κ,i].Itstilluses (cid:88)
M−1
1
the four-dimensional kernel to produce the output signal d[t,m,κ,p] = D[t,k,κ,p]e+ȷ2πmk/M , (21)
M
I L−1 k (cid:88) =0
d[t,m,κ,p]= x[t,m l,κ,i]w[l,κ,i,p], (14) with valid output samples only for m = M R,...,M 1
− − −
according to the principles of overlap-save processing.
i=1 l=0
(cid:88)(cid:88)
where the frames t are reproduced from input to output with
C. FIR Block Implementation
shared kernels according to the idea of the same plant being
responsible for one input sequence and the frames therein. In our PyTorch implementation, the data passed through
In order to obtain m = 0,...,R valid and seamless output an FIR block is arranged as a four-dimensional input tensor.
time steps of the convolution for the given frame-shift R, the The first dimension is the batchsize and it hosts the frames
kernelsize must be constrained to L=M R+1. t=0,...,T for parallel processing with same kernels for one
−

---

# Page 6

6
FIR block 1 1
2
X w [l,κ,1,p]
1
...
NL block 1
2
b pℓ+1,pℓ
P1 a p,pD
...
of the last block is always one for single-input single-output
FIR block 2 (SISO) system identification problems.
D At this point, we shall return to the fact that FIR blocks w [l,κ,p,1]
P2 2 b wereintroducedtoprimarilyaccomplishthedesiredmultiplant
representation. Now considering architectures with connected
NL and FIR blocks, however, it should be noted that the mul-
Fig.5. Block-structureoftheFIR NL FIRmodel.
P1 P2 tichannel interplay of NL and FIR blocks additionally implies
the possibility of plant-specific nonlinear representation. This
effect is due to the mathematical nature of nonlinear expan-
and the same plant index κ. The second dimension keeps the
sion, i.e., a NL block with multichannel output effectively
individual plants κ=0,...,K. Then follows the dimension of
spans a basis for nonlinear modelling, while actual nonlinear
inputs i=1,...,I, before the last dimension is used to repre-
functions are achieved by the plant-specific aggregation with
sent the sequence of time steps m=0,...,M per frame. The
a subsequent FIR block.
FIR block thus converts a (T,K,I,M)-dimensional input-
Given the above short notation of block-structured model
tensor to a (T,K,P,R)-dimensional output tensor . The
X D architectures, we can also refer to some important special
implementation of the FIR block, however, depends on the
cases of it. By discarding the first FIR block in Fig. 5 and
previous time- or frequency-domain logic.
consideringsimplyP =1inputchannels,anNL FIRmodel
1) Time-Domain FIR-Block: To form the system output 1 P2
architecture is obtained. With P = P > 1 we then arrive at
withP outputchannels,anumberofP 2D-Conv-Layersisset 2
the parallel Hammerstein model NL FIR, whereas P = 1
up in parallel. This extra effort is rooted in the fact that the P 2
yields the cascaded Hammerstein model NL FIR, both of
output-channel dimension is employed for group processing 1
which renowned for instance in applications of acoustic sys-
in order to enable the representation of individual kernels
tem identification [16], [17], [28], [30]. The cascaded model
for the K individual plants (PyTorch: ’groups = K’) which
exhibits greatly less parameters, but appears more delicate
equalsthenumberofinputandoutputchannels.Wethushave
in terms of the optimisation problem. Parallel models better
specific kernels of size (I,L) for each plant in the data. The
learn the optimum parameters and achieve richer interplay of
paddingregardingthedimensionoftimestepsissetto’valid’.
nonlinearity and memory by aggregating basis function with
Accordingly, the kernel slides along the dimension of time
possibly different phase. By discarding the second FIR block
steps m while aggregating the input dimension i.
in Fig. 5, we obtain an FIR NL Wiener architecture, where
2) Frequency-DomainFIR-Block: Complex-valuedweights P1
P = P > 1 once more refers to a parallel FIR NL and
W according to (20) are set up with two real-valued weight 1 P
P =1 a cascaded FIR NL representation.
tensorsofsize (M,K,I,P).Inorderto constraintheweights 1 1
according to (17), the available weights can be converted
to time domain via IFFT, the last M L time steps are
− B. Model Parameter Identification
forcedtozero,beforetheresultisconvertedbacktofrequency
domain by FFT. The input signal is then converted into the Once the block structure of a model is defined based on
FFT domain as shown by (19) and elementwise spectral availabledomain-knowledge,theoptimalmodelparameterset
multiplication (20) takes place in the FFT domain, before the Θ[κ] = w [l,κ,1,p],w [l,κ,p,1],a ,b needs to
{
1 2 p,pD pℓ+1,pℓ}
output tensor is obtained with IFFT and the valid samples are be determined for given a data set. To do so, the aim is to
saved and returned as the block output according to (21). minimise the misalignment between the model output tensor
Θ[κ] and the primary signal tensor as target, which can
D Y
be stated as the optimisation problem
VI. MULTIKERNELNEURALNETWORKMODEL (cid:0) (cid:1)
Differentapplicationdomainsrequiredifferentmodelstruc- Θ [κ] =argmin Θ[κ] 2 , (22)
tures, for instance, according to basic plant structures shown Θ Y −D
(cid:13) (cid:13)
in Section III. Model representations of linear and nonlinear i.e., the optim(cid:98)isation of the (cid:13) (cid:13)mean-sq (cid:0) uare (cid:1) e (cid:13) (cid:13)rror (MSE) loss
blocks therein were then provided by Sections IV and V. We
between model prediction and target. We here rely on the
now form some basic model architectures with competence
Adam optimiser [53] with learning rate µ = 0.01, β = 0.9
for multiplant representation and demonstrate their operation 0 1
and β = 0.999. In every iteration all available data frames
with respect to possibly different plant structures. 2
from all plants are employed for optimisation.
A. Model Architectures
C. Synthetic Multiplant Data
Inordertointroduceacompactnotationofblock-structured
models,letusfirstlyconsidertheconfigurationshowninFig.5 Preparing for various applications, we employ computer-
comprising of two FIR blocks and one NL block. This model generated white Gaussian noise and recorded speech as input
architectureis heredenoted byFIR NL FIR,indicating the x[n] for plant simulation. The speech signals are taken from
P1 P2
order of applied FIR/NL blocks, while the subscript describes the AEC Challenge data set [38] each with a duration of 10
the number of connecting output channels. In our context, the secondsatasamplingfrequencyof16kHz,whiletheGaussian
number of inputs to the first block and the number of outputs noise signals consist of N =32,000 samples per sequence.

---

# Page 7

7
0
1
fs(x)
f(x) 20 −
0 b
40
−
1 60
− −
4 3 2 1 0 1 2 3 4 0 200 400 600 800 1,000
− − − −
x
epoch
(a)nonlinearsigmoidalfunction.
2
fc(x)
f(x)
0 b
2
−
4 3 2 1 0 1 2 3 4
− − − −
x
(b)nonlinearclippingfunction.
Fig.6. MemorylessplantnonlinearitiesanditsidentificationbyNLblock.
Plants with Wiener and Hammerstein system structure
according to Fig. 2 are simulated. The plant-specific LTI
behaviour therein is implemented by convolution
511
d[n]= h[κ][l]x[n l] (23)
−
l=0
(cid:88)
using plant-specific synthetic impulse responses h[κ][l] drawn
according to [54], [55]. For the nonlinear system part, two
types of multiplant nonlinearity are employed:
• a sigmoidal input-output characteristic
f[κ](x[n])=γ[κ] arctan(δ[κ]x[n]) (24)
s
with plant-specific scaling by γ[κ] and δ[κ]
• a hard-limiting input-output characteristic
x[n] for x[n] x [κ]
f[κ](x[n])= ≤ max , (25)
c (cid:40)x
max
[κ] othe
(cid:12)
rwise
(cid:12)
(cid:12) (cid:12)
where the clipping can be customised by x [κ]. max
To quantify the respective nonlinearity, the
E (αx)2
SDR(x,f)=10log { } (26)
10 E (f(x) αx)2
(cid:20) { − }(cid:21)
ofthelinearpartαxrelativetothenonlinearresidualoff(x)
is used, where α=E x∗f(x) /E x∗x .
{ } { }
A total of N=10 different plant realisations are generated
for the Wiener and the Hammerstein scenario each, where the
plant-specific nonlinearity ranges from SDR of 4dB to 32dB
with mean SDR of 14dB. For the latter, as an example, the
nonlinear functions are shown in Fig. 6. The verification in
the following subsection takes place with y[n] = d[n], i.e.,
the desired signal of s[n] of Fig. 1 being zero. From the
simulatedplantinputandoutputsequenceswesegmentframes
accordingto(13)withframesizeM =2(L +L )andframe-
1 2
shiftR=(M (L +L )+1)/2,whereL andL refertothe
1 2 1 2
−
kernelsizes of the two FIR blocks, if they exist in the general
]Bd[ESMN Single-kernelFIRblock Multikerneltime-domainFIRblock
Multikernelfreq.-domainFIRblock
(a)whitenoiseexcitationwith32,000·K timesamplesperepoch.
0
20
−
40
−
60
−
0 200 400 600 800 1,000
epoch
]Bd[ESMN
(b)speechexcitationwith160,000·K timesamplesperepoch.
Fig.7. FIR-blockmodellingoflinearmultiplantswithdifferentinputsignals.
modelarchitectureofFig5.Forthesakeofcompleteness,the
hyperparameters of the NL block therein are set to D = 5
hidden layers with P =6 internal and P =6 output units.
ℓ
D. Verification of Multikernel Neural Network Models
Firstly, the FIR block and the NL block is considered for
verification alone. The FIR block in its variants of Section V
isemployedforrepresentationofthelinearmultiplantin(23).
Fig.7showsthelearningcurvesoftheFIRmodelintermsof
normalised MSE for white Gaussian noise and speech-based
data. In both cases a conventional single-kernel FIR block
modelclearlyfailstomatchthemodeloutputtoplant-specific
observationsprovidedastrainingdata.TheMSEremainshigh
around 0dB, demonstrating the need for multiple kernels in
themodel.ForthewhitenoisecaseinFig.7a,themultikernel
FIRblockthendeliversMSEintheorderof 70dBwhichis
−
successful and plausible for the synthetic data at hand. After
500trainingepochs,theNMSEofthetime-domainFIRblock
scrapes off, but could be stabilised to 70dB with a smaller
−
learning rate. With speech input into the plants, as shown by
Fig. 7b, the optimisation of the time-domain FIR block gets
stuck around mediocre 30dB and merely the frequency-
−
domain FIR block successfully attains the former 70dB
−
NMSE. The self-correlation property of speech signals sup-
posedlyhindersefficientmodellinginthetimedomain,butthe
frequency-domain ultimately rescues the training by analogy
with adaptive filter theory [26]. The NL block alone of
Section IV is then applied to nonlinear functions according to
(24) and (25). Fig. 6 shows the successful nonlinear function
approximationf(x)oftherespectivenonlinearities,wherethe
better approximation of the sigmoidal function is plausible
with tanh-activ(cid:98)ations inside the NL block.
Next we conduct a comprehensive matrix study with the
range of nonlinear model architectures described in Sec-
tion VI-A and a variation of data sets, i.e., based on single-
plant (labelled ”inv”) and multi-plant (labelled ”var”) simula-

---

# Page 8

8
TABLEI
MINIMUMNMSE[dB]ACHIEVEDBYUSINGDIFFERENTMODELARCHITECTUREONDATAFROMPLANTSWITHDIFFERENTCHARACTERISTICS.
Model
FIR NL FIR NL FIR FIR NL FIR NL FIR NL FIR FIR NL FIR FIR NL FIR FIR NL FIR
1 6 1 6 1 1 1 6 6 1 6 6
WienerData
h fc
L=512 L
1
=512,L
2
=1
inv inv -11 -11 -11 -59 -52 -67 -60 -55 -57
var inv -10 -10 -10 -59 -54 -61 -63 -44 -57
inv var -13 -13 -13 -16 -16 -46 -59 -47 -44
var var -12 -12 -12 -14 -14 -44 -60 -44 -42
HammersteinData
fs h
L=512 L
1
=1,L
2
=512
inv inv -14 -65 -68 -14 -17 -68 -65 -67 -64
var inv -7 -22 -54 -14 -19 -65 -70 -64 -62
inv var -14 -68 -67 -7 -10 -65 -63 -62 -60
var var -7 -23 -49 -7 -12 -49 -48 -49 -49
tion of LTI and NL parts of Wiener and Hammerstein plant TABLEII
structures. The matrix is depicted in Table I including the MINIMUMNMSE[dB]OFTHEPROPOSEDMULTIKERNELNEURAL
NETWORKANDBASELINEMODELS.
final MSEs of the respective model parameter learnings. Just
note that the FIR block here uses its time-domain version, WienerData Model
since the study is restricted to the white Gaussian noise input. h fc Multikernel MemoryPolynomial Single-Kernel
ThesimulationofWienerdatahereusesclippingnonlinearity, inv inv -57 -12 -48
while Hammerstein data is created sigmoidal. var inv -57 -11 -0
A pure FIR model (left column) naturally fails the good inv var -44 -10 -8
MSE representation of the nonlinear data. For good nonlinear var var -42 -10 -1
representation, however, it is still important where an addi- HammersteinData
tional NL block is placed in the architecture. The two-block fs h
NL P FIR model, for instance, cannot represent the Wiener inv inv -64 -55 -53
data and, conversely, the FIR NL model cannot represent var inv -62 -27 -8
P
Hammerstein data well (indicated by minimum NMSE in the inv var -60 -55 -0
order of 12dB). The FIR NL model is also not sufficient var var -49 -27 -0
P
−
to match the Wiener data with multiplant nonlinearity. This
requires an additional FIR block to follow the NL block as polynomial with its efficient individual LS solution per plant
in the FIR P NL P FIR model (right column). Here, the plant- observation can naturally better represent multiplant nonlin-
specific aggregation of basis functions into a plant-specific earity (labelled ”var”) in Hammerstein data, but turns out to
nonlinear representation takes place. Those models according belimitedtoanaverageof 27dBMSE,whichcanbetraced
toFig.5aresufficientlypowerfultorepresentallconstellations tothecasesofstrongernon − linearityinthedata.Theproposed
of the Wiener data such that the minimum NMSE attains multikernelneuralnetworkmodelcanverygoodrepresentthe
40dB and below. For Hammerstein data, already the two- Hammerstein data in all constellations as shown before. For
−
block ”parallel” NL P FIR model with P = 6 NL channels is thecaseoftheWienerdata,thethree-blockmultikernelmodel
very successful and can model all constellations with single- of this experiment is the only architecture to successfully
or multiplants. The larger three-block models (right) continue match the data with low MSE. The memory polynomial with
to be successful on the Hammerstein data as well. its structure of nonlinear basis functions followed by FIR
We then consider established nonlinear system models, i.e.,
filters does not fit the Wiener data.
• a ”memory polynomial” [11] based on Eq. (4) but with
FIR filters in place of the memoryless a coefficients, VII. APPLICATIONTOACOUSTICECHOCANCELLATION
p
• a”single-kernel”neuralWiener-Hammersteinmodel[40] The proposed framework is now applied in the domain of
for comparison with our strongest FIR NL FIR ”multikernel” acoustic echo control. Acoustic echo appears as distraction in
6 6
representation in Table II. The memory polynomial uses a hands-free voice terminals. Due to acoustic coupling between
nonlinear model order P = 6 and FIR filters of length loudspeaker and microphone, i.e., the echo path, the far-end
L=512. It is practically linear in the parameters and solved receives a delayed version of the own voice. It inhibits fluent
in the least-squares (LS) sense per plant. The single-kernel conversation during important double-talk speech periods.
neural baseline relies on the FIR NL FIR representation and
6 6
A. Hands-Free System
istrainedinthesameframeworkwiththemultikernelversion.
Apparently,thesingle-kernelmodelmerelyrepresentsthedata The near-end microphone of a hands-free speech system in
with a single plant in it (labelled ”inv”) well. The memory Fig. 8 captures the desired speech signal s[n] at discrete time

---

# Page 9

9
Near-end
s[n]
Hammerstein
d[n]
h[κ]
htapohce
Far-end
D D
y[n] e[n] s[n] freq.-domain
+ FIR blbock FDK b F tofar-end
d[n] − b w[l,κ,p,1]
w[l,κ,p,1]
b
Multikernel
Neural
Network 1 2 ... P 1 2 ... P
Model
f[κ](x[n]) NL block
x[n]
a p,pD save
f ()
fromfar-end b pℓ+1,pℓ weights p ·
b
Fig.8. Setupforacousticechocancellation.Themodeloutputd(cid:98)[n]approx- X
imatestheechosignald[n],suchthate[n]≈s[n]atthesystemoutput. (a)NL FIRfortraining.
P
n plus, unfortunately, a potentially nonlinear echo signal
∞
d[n]= h[κ][m]f[κ](x[n m]) (27)
−
m=1
(cid:88)
of the far-end (reference) speech x[n]. In this domain model,
it is thus assumed that the echo path exhibits Hammerstein
block structure. An acoustic echo canceller (i.e., generally in
place of the multikernel network of Fig. 8) aims to eliminate
the interfering echo d[n] from the microphone signal y[n] =
s[n]+d[n] without distorting the desired signal s[n].
Moregenerally,systemsforacousticechocontroltradition-
ally consist of two stages. The acoustic echo canceller (AEC)
is a first component and frequently models the echo path for
echo estimation and subtraction by a linear FIR filter model.
Echo path tracking in this system identification scenario is
accomplishedbyadaptivefilteralgorithms,suchasnormalised
least-mean squares (NLMS), recursive least-squares (RLS),
or frequency-domain adaptive filters (FDAF) [26]. These al-
gorithms are sensitive to local interference, such as double-
talk, or echo path nonlinearities. The double-talk problem has
been tackled successfully with adaptive learning rates based
on double-talk detectors [1], filter mismatch estimation [56],
or noisy state-space modelling and Kalman filtering [52]. The
problemofnonlinearities,whichappearduetotheloudspeaker
in the echo path, has been addressed, for instance, by means
of block-structured nonlinear Hammerstein models with fixed
nonlinear basis functions as described in Section IV-A. A
different approach of dealing with nonlinearities is to apply
additional spectral masking to the error signal e[n] in Fig. 8
in order to sufficiently suppress residual echo and potentially
ambient noise. This second stage is performed via statistical
model-based postfilters [3], [4] or neural networks [57]–
[60]. In this article, we are focusing on the isolated task of
acousticechocancellation(AEC)basedonthedomain-specific
Hammerstein echo path structure. It guides the corresponding
model structure to include nonlinearities and in this way
reduceresidualechobelowwhatalinearfiltercando,without
harmtothedesiredspeech.Theapproachmaystillbeextended
with more complex block structures, additional postfilter or
masking networks in future work.
dexfi
NL block
X
(b)NL FDKFfortesting.
P
Fig. 9. Multikernel neural network models for training to extract nonlinear
function across different plants, and testing used on unseen data with fixed
nonlinearfunctionapproximationandFDKFasFIRblock.
B. Domain-Specific Neural-Network for AEC
For the AEC approach, certain requirements have to be
met. While our frequency-domain FIR block is currently ap-
plicablefortrainingconditions,theactualnetworkapplication
must further provide agility for double-talk robustness, non-
stationary speech characteristic, as well as long and possibly
time-varying room impulse responses (RIRs) easily in the
order of 4000 or more filter taps.
To cope with the requirements we outline our training and
testingstrategy.WerelyontheNL FIRmodelwithfrequency-
6
domainFIRblockasproposedinSectionVI.TheNLblockis
specified with D =3 hidden layers with P =9 internal units
ℓ
and P =6 output units. While the training phase takes place
in a far-end single-talk scenario, the test phase additionally
involves double-talk scenes and uses completely unseen data,
whichwasnotincludedinthetraining.Tomanage,thetesting
henceemploysthedomain-specificfrequency-domainadaptive
Kalmanfilter(FDKF)[52]anditsmultichannelversion[16]in
placeoftheFIRblock.Thecorrespondingmodelarchitectures
for training and test phases are shown in Fig. 9. The training
architecture in Fig. 9a basically aims at the identification of a
common nonlinear basis across plants, while the multikernel
FIR block of the model here represents the typically variable
acoustic impulse responses of a training data set. The weights
of the NL block are saved when a minimal normalised MSE
(NMSE)isreached.Inthetestphase,theseweightsareloaded
into the corresponding NL block of the test architecture in
Fig. 9b. With the FDKF in place of the FIR block, which is
in the following termed the NL FDKF model, our intention
6
istocanceloutnonlinearechothroughdouble-talkwithtime-
varying echo path impulse responses.
C. Experimental Results
Our experimentation uses the 16kHz synthetic database
provided by the ICASSP-2021 AEC Challenge [38]. The
structure of training and test data sets as well as far-end and
near-end signals is retained in our experiments.

---

# Page 10

10
20
10
0
0 2 4 6 8 10
time[s]
]Bd[ELRE
FDKF
NL6FDKF
(a)single-talkscenario.
20
10
0
0 2 4 6 8 10
time[s]
]Bd[ELRE
(b)double-talkscenario.
20
10
0
0 2 4 6 8 10
time[s]
]Bd[ELRE
16
14
12
10
8
6
4
2
0
0 2 4 6 8 10
time[s]
(c)single-talkwithecho-path-changescenario.
Fig.10. TestmodelfromFig.9bappliedto’self-made’testscenariosacross
K=5echoplantswithNLblocktrainedon’self-made’trainingdata.
Forfirstexperimentswerelyonownnonlinearitiesandecho
path impulse responses. For training we generate K = 20
’self-made’echopathplantsandfeedwithfar-endsignalsx[n]
of 10 seconds duration from the AEC Challenge training data
set. The far-end signals are processed by nonlinear functions
f[κ](x) to mimic loudspeaker distortion, i.e., before the echo
path.Specifically,thearctandefinedin(24)isusedforplants
κ=1,...,5, while the clipping-nonlinearity given in (25) is
used for κ=6,...,10. By adjusting δ[κ] or x [κ], the non- max
linearityisconfiguredsuchthattheSDR(x,f)rangesbetween
4dB and 33dB, whereby an average of 7dB is achieved.
Another ten linear samples (f[κ](x) = x, κ = 11,...20) are
includedinthetrainingset.Tocreatetheechosignalsd[n],the
nonlinearly mapped far-end signals are convolved with room
impulse response h[κ][n] of length L = 4096 generated by
the image method [54], [55] at different room positions. The
near-end signal s[n] is zero in all training samples.
For firsttesting, K =5 other echoplants are generatedand
fed with AEC Challenge far-end test samples. The procedure
of creating the echo signals is similar to the training set,
but here uses three other arctan and two other clipping
nonlinearities with average SDR(x,f) = 7dB. The echo
signals are further superimposed with the corresponding AEC
]Bd[ELRE
FDKF NL6FDKF’self-made’ NL6FDKFChallenge
Fig. 11. AEC Challenge single-talk scenario. Averaged over K = 15
randomly selected files from the AEC Challenge test set. NL block trained
on’self-made’trainingdataandNLblocktrainedonAECChallengedata.
Challenge near-end speech of 3 7 seconds duration and
−
zero-padding to 10 seconds and scaling according to [38].
Threedifferentscenariosareconsidered:a)far-endsingle-talk
similartothetrainingset;b)double-talkwithnear-endspeech;
c) far-end single-talk with echo-path change in the middle.
For AEC assessment, we then evaluate the ERLE[n] =
10log E d2[n] /E (d[n] d[n])2 averagedoverthetest
10 { } { − }
data for the three different test scenarios. Fig. 10 depicts our
(cid:0) (cid:1)
NL FDKF results with respec(cid:98)t to a baseline linear single-
6
channel FDKF algorithm. The superiority of the NL FDKF 6
in comparison to the linear version is firstly visible in single-
talk shown in Fig. 10a, where the linear FDKF is limited
according the SDR(x,f) = 7dB, which NL FDKF can
6
clearly overcome. The performance of NL FDKF is also seen
6
inthedouble-talkscenarioinFig.10b,althoughtheadvantage
here is smaller due to the near-end speech presence, mainly
between second 3 and 8. If reconvergence is required after a
changeintheechopath,theNL FDKFisstillabovethelinear
6
FDKF, as can be seen in Fig. 10c.
In order to investigate if the learned NL FIR nonlinearity
6
also generalises to echo paths and nonlinearities originally
used in the AEC Challenge, we further evaluate a subset of
the original synthetic test set. It consists of K =15 randomly
selected files from the test data set [38], comprising the
respective far-end speech x[n], the echo signal d[n] including
nonlinearity,andthenear-endspeechs[n].Exactdetailsofthe
echo signal generator are not known. Results of the previous
linearFDKFandNL FDKFmultikernelneuralnetworkmodel
6
are shown in Fig. 11. It can be seen that the ’self-made’
NL FDKFpartlyaddressesthenonlinearityoftheoriginaltest
6
data by some improvement over the just linear FDKF model.
Additionally,anNL FDKFmodelistrainedwithoriginaldata
6
from the AEC Challenge using a total of K = 40 linear
and nonlinear files. Surprisingly, this model trained on the
supposedly more appropriate AEC Challenge data performs
below the model trained on our ’self-made’ data.

---

# Page 11

11
z(t)
transmitsignal
PA D/A
TX
Multikernel
Neural
x[n] Network
ATT A/D Model
y[n]
RX f[κ]( · ) y[n] −
LNA A/D b +
signal
ofinterest
ecnerefretnifles
lesssystemmustaccuratelymodelandcanceltheoverwhelm-
Wiener
ingself-interferencey[n]fromthetransmitterintothereceiver.
BoththeSIandtheSICarerepresentedinthecomplex-valued
baseband domain. Note that the reference z(t) is in the SIC
path represented by the digital version x[n].
Experiments below will be performed for simulated high-
h[κ]
throughput (HT) transmission in a wireless local area net-
work (WLAN) with data available in [14]. It uses orthogonal
d(t)
frequency-divisionmultiplexing(OFDM)basebandsignalsac-
cording to IEEE-802.11n with 20MHz channel bandwidth. It
e[n] willberelevantforourmultikernelmodelthatthenonlinearity
ofLNAandA/Disinthedatarealisedwithpolarcoordinates
in the complex baseband domain as
Fig.12. Wirelesssystemwithself-interferenceasanonlinearWienermodel. f[κ]()=f[κ]( ) eȷ̸ (·) (29)
· mag |·| ·
where f () is a real-valued saturation and such that the
VIII. APPLICATIONTOWIRELESSSELF-INTERFERENCE mag ·
average SDR of different plants f[κ]() amounts to 10dB.
CANCELLATION ·
Full-duplex communication, where transmission and recep-
B. Complex-valued Multikernel Neural Network
tion occur simultaneously on the same frequency resource,
A multikernel FIR NL FIR model of Section VI is em-
promises greater efficiency and flexibility in wireless systems. 1 1
ployed to represent the Wiener SI plant with its potential
Theprimarychallenge,however,istheself-interference(SI)of
variability of linear and nonlinear components. Extension
the transmitted signal leaking into the receiver and impeding
is required for applying this model in the complex-valued
the desired communication. In Wi-Fi, for instance, the trans-
basebanddomain.Fig.13showsthemodelarchitecture,where
mitted signal power is around 20dB, while the information-
the bold links represent complex-valued signals, which are
bearing signal can be near the noise floor at about 90dB.
− converted into Cartesian and polar forms as necessary.
To avoid the obstructing interference, it must be cancelled
The complex-valued FIR blocks operate in Cartesian form,
by in the order of 110dB from the receiver. Generally, the
where the real and imaginary parts of the input signal,
self-interference cancellation (SIC) hence involves techniques
ℜ{X}
and ,areprocessedwithtwoconvolutionalkernelssuch
like passive or active shielding, analogue cancellation, and
ℑ{X}
that valid components, and , of a complex-valued
digitalbasebandadaptivecancellationtoachievethenecessary
ℜ{·} ℑ{·}
outputsignalaredelivered.Inlightoftheplantinformationin
reduction [5]–[7]. In doing so, the strong self-interference is
[14], our hyperparameters include the FIR filter lengths L =
also subject to system nonlinearities in the SI path, which 1
20, and L =1 samples in the time domain.
additionallychallengessystemmodelling.Inwhatfollows,we 2
Takingintoaccounttheformerexpression(29)forcomplex-
briefly describe the wireless architecture, the related data for
valuednonlinearityinthedata,werealiseourcomplex-valued
our study, the placement of a multikernel neural network for
nonlinear modelling by means of the former NL block on
modelling, and the experimental results obtained with it.
the magnitude of a complex-valued signal and then recom-
bine with the original phase, such that our model function
A. Wireless System
f()=f ( ) eȷ̸ (·) complies with (29). The NL block is
A configuration for cross-domain self-interference cancel- · mag |·| ·
configured with D = 3 hidden layers with P = 15 internal
lation can be defined according to Fig. 12. The impact of ℓ
n(cid:98)onlinea(cid:98)r tanh-activations each.
power-amplifier (PA) nonlinearity is here effectively avoided
Fortheoptimisationofthetrainableparameters,theaverage
by the utilisation of the analogue reference signal z(t) in
mean-square error (MSE) of real and imaginary model output
the continuous time domain t to support the SIC according
componentsw.r.t.theSItargety[n]isusedasthelossfunction.
to previously proposed systems [12], [61]. This reference of
In the training phase all trainable parameters of FIR and NL
the antenna output is attenuated (ATT) by auxiliary analogue
blocks are adjusted for minimisation. In the test phase of
componentstotherangeofanA/Dconverter,beforeitcanbe
the model, we retain the trained NL block parameters, while
supplied to a digital model of the SI path, here a multikernel
reoptimising the FIR block parameters in order to cope with
neuralnetworkmodel.Inthisconfiguration,theSIpathsubject
new multiplants of the test data [14].
to modelling extends from the PA output z(t) to the received
signal y[n] and thus refers to a Wiener plant model. The PA
C. Experimental Results
output firstly propagates through a presumably linear TX to
RX multiplant h[κ](t) followed by nonlinear saturation in the Withtheproposedmultikernelmodel,anumberofbaseline
LNA and A/D components due to its high power, i.e., models further take part in the evaluation, i.e.,
y[n]=f[κ](h[κ](t) z(t)), (28) • a multiplant ’linear FIR’ model consisting of only one
∗ FIR block with kernelsize L=20,
with the information-bearing signal being neglected in the • a plant-specific ’memory polynomial’ model [11] with
scope of this paper. To achieve full-duplex operation, a wire- nonlinear order P =15 and filter length L=20,

---

# Page 12

12
NL block
ℜ{X} complex-val. ℜ{·} |·| ℜ{·} complex-val. ℜ{Y}
X
complex
FIR block 1
complex
b pℓ+1,pℓ
complex
FIR block 2
b comple
Y
x
a
w [l,κ,1,1] ∠
1,pD
w [l,κ,1,1] b
ℑ{X} 1 ℑ{·} ℑ{·} 2 ℑ{Y}
b
Fig.13. Block-structuredFIR1NL1FIRmodelforcomplex-valuedsignals.
TABLEIII
MINIMUMNMSE[dB]ACHIEVEDWITHCOMPLEX-VALUEDMODELSON
COMPLEX-VALUEDWIENERMULTIPLANT(LABELLED”VAR”)DATA.
Model FIR 1 NL 1 FIR FIR 1 NL 1 FIR Memory linearFIR
(Fig.13) (single kernel) Polynomial
h f
inv inv -69 -44 -14 -11
var inv -70 -5 -13 -12
inv var -68 -25 -14 -12
var var -69 -5 -12 -11
• the proposed complex-valued multikernel FIR 1 NL 1 FIR
neural network as shown by Fig. 13,
• and a complex-valued FIR 1 NL 1 FIR version with single
kernel and otherwise the same configuration.
TableIIIshowstheminimumNMSEachievedforthediffer-
ent models. The linear FIR model does not possess sufficient
nonlinear modelling ability to represent the nonlinear Wiener
data. The single-kernel FIR NL FIR model does not possess
1 1
the capacity to represent multiplant data with either variable
linear or nonlinear components (labelled ”var”). The memory
polynomialrootedinHammersteinmodellingisneitherableto
represent the Wiener data with relevant accuracy. As a result,
merely the multikernel model (left column) is able to model
the SI data [14] well with a minimum MSE around 70dB.
−
Fig. 14 finally provides an illustration of power spectral
densities (PSDs) of the involved SI signals before and after
cancellation. The unprocessed received signal y[n] appears at
the top and depicts an average attenuation level of 40dB
−
according to passive SI shielding provided in the data. From
there, a linear FIR model can just insignificantly reduce the
SI to about 50dB. The proposed multikernel FIR NL FIR
1 1 −
model, however, creates an SIC residual below 100dB,
−
consisting of the incoming 40dB of the unprocessed data
−
andtheadditional 70dBaccordingtoTableIII,andtherefore
−
attains the noise floor of the available data.
40
−
60
−
80
−
100
−
10,000 5,000 0 5,000 10,000
− −
Hz
]Bd[DSP
IX. CONCLUSION
While deep learning is progressing relentlessly with pow-
erful networks for classification and regression problems, it is
notquitesocommonlyusedforproblemsofnonlinearsystem
identification. This paper has demonstrated conceptually and
by considering typical applications of system identification
that this might be rooted in the specific type of data and in
thedesireofcustom-fitarchitectures.Thedata,ifitcomprises
elementssuchaslinearandnonlinearsystemresponses,canbe
extremely inconsistent between different training samples and
therefore complete hamper the identification of a good model
representation. Regarding the model architectures, the system
identification would typically rely on specific structures based
on dedicated domain-knowledge. Yet, this paper demonstrates
thatthepopularconceptofarchitectureswithtrainableweights
is applicable to nonlinear system identification as well, since
there can be appropriate such model subsections with cross-
data utility. Specifically, we have presented a block-structured
approach for nonlinear modelling with a subset of trainable
weights across the training data and another subset of plant-
specific weights represented by multikernels. In this way the
otherwise inconsistent data of different plant observations can
be well represented both in training and testing, opening a
deep learning perspective for nonlinear system identification.
REFERENCES
[1] J.Benesty,T.Ga¨nsler,D.Morgan,M.Sondhi,andS.Gay,Advancesin
NetworkandAcousticEchoCancellation. Springer,2001.
[2] E.Ha¨nslerandG.Schmidt,TopicsinAcousticEchoandNoiseControl.
Springer,2006.
[3] P. Vary and R. Martin, Digital Speech Transmission - Enhancement,
Coding,andErrorConcealment. Wiley,2006.
[4] G.Enzner,H.Buchner,A.Favrot,andF.Kuech,“Acousticechocontrol,”
in Academic Press Library in Signal Process. Elsevier, 2014, vol. 4,
pp.807–877.
[5] M. Heino et al., “Recent advances in antenna design and interference
cancellation algorithms for in-band full duplex relays,” IEEE Comm.
Mag.,vol.53,no.5,pp.91–101,2015.
[6] K. E. Kolodziej, B. T. Perry, and J. S. Herd, “In-band full-duplex
technology: Techniques and systems survey,” IEEE Trans. Microwave
TheoryTechn.,vol.67,no.7,pp.3025–3041,2019.
[7] B. Smida, A. Sabharwal, G. Fodor, G. C. Alexandropoulos, H. A.
Suraweera,andC.Chae,“Full-duplexwirelessfor6G:Progressbrings
newopportunitiesandchallenges,”IEEEJ.Sel.AreasCommun.,vol.41,
no.9,pp.2729–2750,2023.
receivedsignaly[n] e[n]withFIR1NL1FIR [8] C.Sexton,N.J.Kaminski,J.M.Marquez-Barja,N.Marchetti,andL.A.
e[n]withlinearFIR DaSilva, “5G: Adaptable networks enabled by versatile radio access
technologies,” IEEE Commun. Surveys Tuts., vol. 19, no. 2, pp. 688–
720,2017.
[9] Y. He, H. Zhao, W. Guo, S. Shao, and Y. Tang, “Frequency-domain
successivecancellationofnonlinearself-interferencewithreducedcom-
plexity for full-duplex radios,” IEEE Trans. Commun., vol. 70, no. 4,
pp.2678–2690,2022.
[10] W. Klippel, “Nonlinear large-signal behavior of electrodynamic loud-
Fig.14. PSDsofreceivedsignaly[n]withoutSICanderrorsignale[n]= speakers at low frequencies,” Jrnl. Audio Eng. Soc., vol. 40, pp. 483–
y[n]−y (cid:98) [n]afterSIC.Averageof10signalsfromthe”inv/var”testcase. 496,1992.

---

# Page 13

13
[11] D. R. Morgan, Z. Ma, J. Kim, M. G. Zierdt, and J. Pastalan, “A [36] H.Zhang,S.Kandadai,H.Rao,M.Kim,T.Pruthi,andT.Kristjansson,
generalized memory polynomial model for digital predistortion of RF “Deep adaptive AEC: Hybrid of deep learning and adaptive acoustic
power amplifiers,” IEEE Trans. Signal Process., vol. 54, no. 10, pp. echo cancellation,” in Proc. IEEE Intl. Conf. Acoustics, Speech and
3852–3860,2006. SignalProcess.,2022,pp.756–760.
[12] E.AhmedandA.M.Eltawil,“All-digitalself-interferencecancellation [37] N.L.WesthausenandB.T.Meyer,“Acousticechocancellationwiththe
technique for full-duplex systems,” IEEE Trans. Wireless Commun., dual-signal transformation LSTM network,” in Proc. IEEE Intl. Conf.
vol.14,no.7,pp.3519–3532,2015. Acoustics,SpeechandSignalProcess.,2021,pp.7138–7142.
[13] M. I. Mossi, N. Evans, and C. Beaugeant, “An assessment of linear [38] K. Sridhar, R. Cutler, A. Saabas, T. Parnamaa, M. Loide, H. Gamper,
adaptive filter performance with nonlinear distortions,” in Proc. IEEE S.Braun,R.Aichner,andS.Srinivasan,“ICASSP2021AcousticEcho
Intl.Conf.Acoustics,SpeechandSignalProcess.,2010,pp.313–316. Cancellation Challenge: datasets, testing framework, and results,” in
[14] G. Enzner, A. Chinaev, S. Voit, and A. Sezgin, “On neural-network Proc. IEEE Intl. Conf. Acoustics, Speech and Signal Process., 2021,
representation of wireless self-interference for inband full-duplex pp.151–155.
communications,” 2024. [Online]. Available: https://arxiv.org/abs/2410. [39] M.S.Gast,802.11n:ASurvivalGuide. O’ReillyMedia,Inc.,2012.
00894 [40] M.Halimeh,C.Huemmer,andW.Kellermann,“Aneuralnetwork-based
[15] C. Huemmer, C. Hofmann, R. Maas, and W. Kellermann, “Estimating nonlinearacousticechocanceller,”IEEESignalProcess.Lett.,vol.26,
parameters of nonlinear systems using the elitist particle filter based no.12,pp.1827–1831,2019.
onevolutionarystrategies,”IEEE/ACMTrans.Audio,Speech,Language [41] A. N. Birkett and R. A. Goubran, “Acoustic echo cancellation using
Process.,vol.26,no.3,pp.595–608,2018. NLMS-neuralnetworkstructures,”inProc.IEEEIntl.Conf.Acoustics,
[16] S. Malik and G. Enzner, “State-space frequency-domain adaptive fil- SpeechandSignalProcess.,vol.5. IEEE,1995,pp.3035–3038.
tering for nonlinear acoustic echo cancellation,” IEEE Trans. Audio, [42] M.Schetzen,TheVolterraandWienerTheoriesofNonlinearSystems.
Speech,LanguageProcess.,vol.20,no.7,pp.2065–2079,2012. KriegerPub.,2006.
[17] ——,“AvariationalBayesianlearningapproachfornonlinearacoustic [43] V.J.MathewsandG.Sicuranza,PolynomialSignalProcessing. John
echocontrol,”IEEETrans.SignalProcess.,vol.61,no.23,pp.5853– Wiley&Sons,Inc.,2000.
5867,2013. [44] T.WigrenandA.E.Nordsjo,“CompensationoftheRLSalgorithmfor
[18] S. A. Billings, Nonlinear System Identification: NARMAX Methods in outputnonlinearities,”IEEETrans.Autom.Control,vol.44,no.10,pp.
theTime,Frequency,andSpatio-TemporalDomains. Wiley,2013. 1913–1918,1999.
[19] S. Chen, S. A. Billings, C. F. N. Cowan, and P. M. Grant, “Practical [45] A. E. Nordsjo and L. H. Zetterberg, “Identification of certain time-
identification of NARMAX models using radial basis functions,” Intl. varying nonlinear Wiener and Hammerstein systems,” IEEE Trans.
Jrnl.Control,vol.52,no.6,pp.1327–1350,1990. SignalProcess.,vol.49,no.3,pp.577–592,2001.
[20] M. Zeller and W. Kellermann, “Fast and robust adaptation of DFT- [46] O.Nelles,NonlinearSystemIdentification. Springer,2020.
domainVolterrafiltersindiagonalcoordinatesusingiteratedcoefficient [47] K.NarendraandP.Gallman,“Aniterativemethodfortheidentification
updates,” IEEE Trans. Signal Process., vol. 58, no. 3, pp. 1589–1604, ofnonlinearsystemsusingaHammersteinmodel,”IEEETrans.Autom.
2009. Control,vol.11,no.3,pp.546–550,1966.
[21] T.Wigren,“Convergenceanalysisofrecursiveidentificationalgorithms [48] A.E.NordsjoandL.Zetterberg,“Identificationofcertaintime-varying
based on the nonlinear Wiener model,” IEEE Trans. Autom. Control, nonlinearWienerandHammersteinsystems,”IEEETrans.SignalPro-
vol.39,no.11,pp.2191–2206,1994. cess.,vol.49,no.3,pp.577–592,2001.
[22] W.GreblickiandM.Pawlak,“NonparametricidentificationofHammer- [49] J.KimandK.Konstantinou,“Digitalpredistortionofwidebandsignals
stein systems,” IEEE Trans. Inf. Theory, vol. 35, no. 2, pp. 409–418, basedonpoweramplifiermodelwithmemory,”Electron.Lett.,vol.37,
1989. no.23,p.1,2001.
[23] T. Ma¨kela¨ and R. Niemisto¨, “Effects of harmonic components gener- [50] C.M.BishopandN.M.Nasrabadi,PatternRecognitionandMachine
ated by polynomial preprocessor in acoustic echo control,” Proc. Intl. Learning. Springer,2006,vol.4,no.4.
Workshop,Acoust.Echo,NoiseControl,pp.139–142,2003. [51] I.Goodfellow,Y.Bengio,andA.Courville,DeepLearning. MITPress,
[24] S. Chen, S. A. Billings, and P. M. Grant, “Non-linear system identi- 2016,http://www.deeplearningbook.org.
fication using neural networks,” Intl. Jrnl. Control, vol. 51, no. 6, pp. [52] G. Enzner and P. Vary, “Frequency-domain adaptive Kalman filter
1191–1214,1990. for acoustic echo control in hands-free telephones,” Signal Process.,
[25] J. Kelley and M. T. Hagan, “Comparison of neural network NARX Elsevier,vol.86,no.6,pp.1140–1156,June2006.
and NARMAX models for multi-step prediction using simulated and [53] D.P.KingmaandJ.Ba,“Adam:Amethodforstochasticoptimization,”
experimental data,” Expert Systems with Applications, vol. 237, p. inProc.Intl.Conf.LearningRepresentations,2015.
121437,2024. [54] (2024) RIR Generator. [Online]. Available: https://www.
[26] S.Haykin,AdaptiveFilterTheory. PearsonEducation,2014. audiolabs-erlangen.de/fau/professor/habets/software/rir-generator
[27] A. Stenger and R. Rabenstein, “Adaptive Volterra filters for nonlinear [55] J.B.AllenandD.A.Berkley,“Imagemethodforefficientlysimulating
acousticechocancellation,”inProc.IEEE-EURASIPWorkshopNonlin- small-roomacoustics,”Jrnl.AcousticalSoc.America,vol.65,no.4,pp.
earSignalImageProcess.,1999,pp.679–683. 943–950,1979.
[28] A.StengerandW.Kellermann,“Adaptationofamemorylesspreproces- [56] J.M.Valin,“Onadjustingthelearningrateinfrequencydomainecho
sor for nonlinear acoustic echo cancelling,” Signal Process., Elsevier, cancellation with double-talk,” IEEE Trans. Audio, Speech, Language
vol.80,no.9,pp.1747–1760,2000. Process.,vol.15,no.3,pp.1030–1034,2007.
[29] A.Gue´rin,G.Faucon,andR.LeBouquin-Jeanne`s,“Nonlinearacoustic [57] M.Halimeh,T.Haubner,A.Briegleb,A.Schmidt,andW.Kellermann,
echocancellationbasedonVolterrafilters,”IEEESpeechAudioProcess., “Combiningadaptivefilteringandcomplex-valueddeeppostfilteringfor
vol.11,no.6,pp.672–683,2003. acousticechocancellation,”inProc.IEEEIntl.Conf.Acoustics,Speech
[30] F.KuechandW.Kellermann,“Orthogonalizedpowerfiltersfornonlin- andSignalProcess.,2021,pp.121–125.
earacousticechocancellation,”SignalProcess.,Elsevier,vol.86,no.6, [58] J. M. Valin, S. Tenneti, K. Helwani, U. Isik, and A. Krishnaswamy,
pp.1168–1181,2006. “Low-complexity, real-time joint neural echo control and speech en-
[31] S. Malik and G. Enzner, “Fourier expansion of Hammerstein models hancement based on PercepNet,” in Proc. IEEE Intl. Conf. Acoustics,
for nonlinear acoustic system identification,” in Proc. IEEE Intl. Conf. SpeechandSignalProcess.,2021,pp.7133–7137.
Acoustics,SpeechandSignalProcess. IEEE,2011,pp.85–88. [59] A. Ivry, I. Cohen, and B. Berdugo, “Deep residual echo suppression
[32] L. Ding, G. T. Zhou, D. R. Morgan, Z. Ma, J. S. Kenney, J. Kim, withatunabletradeoffbetweensignaldistortionandechosuppression,”
andC.R.Giardina,“Arobustdigitalbasebandpredistorterconstructed inProc.IEEEIntl.Conf.Acoustics,SpeechandSignalProcess.,2021.
usingmemorypolynomials,”IEEETrans.Commun.,vol.52,no.1,pp. [60] S.VoitandG.Enzner,“GeneralizedWienerfilterfornonlinearacoustic
159–165,2004. echocontrol,”inProc.ITGConf.SpeechCommunication. VDE,2023,
[33] A.Ivry,I.Cohen,andB.Berdugo,“Nonlinearacousticechocancellation pp.146–150.
withdeeplearning,”inProc.ISCAInterspeech,2021,pp.4773–4777. [61] D.Korpi,L.Anttila,andM.Valkama,“Referencereceiverbaseddigital
[34] S. Braun and M. Valero, “Task splitting for DNN-based acoustic echo self-interference cancellation in MIMO full-duplex transceivers,” in
and noise removal,” in Proc. Intl. Workshop Acoustic Signal Enhance- IEEEGlobecomWorkshops,2014,pp.1001–1007.
ment,2022,pp.1–5.
[35] E.Seidel,J.Franzen,M.Strake,andT.Fingscheidt,“Y2-netFCRNfor
acousticechoandnoisesuppression,”inProc.ISCAInterspeech,2021,
pp.4763–4767.