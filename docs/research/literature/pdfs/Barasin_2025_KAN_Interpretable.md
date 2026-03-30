# Barasin_2025_KAN_Interpretable

Exploring Kolmogorov-Arnold Networks for
Interpretable Time Series Classification
Irina Barasˇin, Blazˇ Bertalanicˇ, Mihael Mohorcˇicˇ and Carolina Fortuna
Department of Communication Systems, Jozˇef Stefan Institute
Jamova ulica 39, 1000 Ljubljana, Slovenia
irina.barasin@gmail.com, blaz.bertalanic, miha.mohorcic, carolina.fortuna @ijs.si
{ }
Abstract—Time series classification is a relevant step sup- roleinadvancingpredictiveandanalyticcapabilitiesthatdrive
porting decision-making processes in various domains, and critical decisions.
deep neural models have shown promising performance in
Unlike time series forecasting, which aims to predict future
this respect. Despite significant advancements in deep learn-
data points, time series classification aims to provide accurate
ing, the theoretical understanding of how and why complex
architectures function remains limited, prompting the need for interpretationandcategorizationoftemporaldatasequencesby
more interpretable models. Recently, the Kolmogorov-Arnold assigning a categorical label or a class label to each sequence
Networks (KANs) have been proposed as a more interpretable [5]. Following a well-accepted survey [6] that revealed the
alternative to deep learning. While KAN-related research is
lackofinvestigationofdeeplearningtechniquesfortimeseries
significantly rising, to date, the study of KAN architectures
classification,significantprogresshasbeenachievedinrelated
for time series classification has been limited. In this paper,
we aim to conduct a comprehensive and robust exploration of researchwithhundredsofnewworks,someofthemsurpassing
the KAN architecture for time series classification utilising 117 thenon-deepstateoftheart[7].Accordingtothemostrecent
datasets from UCR benchmark archive, from multiple different and extensive benchmarking work on more than 100 datasets
domains. More specifically, we investigate a) the transferability
from the UCR archive, the most extensive benchmark for
ofreferencearchitecturesdesignedforregressiontoclassification
time series classification, the state of the art F1 score of
tasks, b) identifying the hyperparameter and implementation
configurations for an architecture that best generalizes across 0.886 is achieved by Hive-Cote2 [8] [9], a large ensemble
117 datasets, c) the associated complexity trade-offs and d) withconsiderabletrainingtime.Thenon-deepandnon-hybrid
evaluateKANsinterpretability.Our resultsdemonstratethat(1) classificationmethodsthataremoreexplainableatbothfeature
the Efficient KAN outperforms MLPs in both performance and engineering and decision making steps achieve F1 of up to
training times, showcasing its suitability for classification tasks.
0.869whilethedeeparchitecturesreacharound0.88F1score.
(2)EfficientKANexhibitsgreaterstabilitythantheoriginalKAN
across grid sizes, depths, and layer configurations, especially Foundation models for time series, based on transformers,
when lower learning rates are employed. (3) KAN achieves are yet to be studied on cross-domain benchmarks such as
competitive accuracy compared to state-of-the-art models such UCR [10].
as HIVE-COTE2 and InceptionTime, while maintaining smaller
Despite the disruptive advancements introduced by break-
architecturesandfastertrainingtimes,highlightingitsfavorable
throughs in machine vision and natural language processing
balanceofperformanceandtransparency.(4)Theinterpretability
of the KAN model, as confirmed by SHAP analysis, reinforces over the last decades, the theoretical understanding of why
its capacity for transparent decision-making. and how complex deep architectures function has lagged
Index Terms—classification, time series, Kolmogorov Arnold behind [11]. This has prompted researchers to step back
networks, multilayer perceptrons and reconsider fundamental and mathematically simpler ar-
chitectures, such as MLPs [12]. Furthermore, the influence
I. INTRODUCTION of the academic scientific community in this new era of
AI is decreasing [13], while non-AI scientific communities
Time series classification is a relevant step supporting are concerned with the interpretability of deep models [11].
decision-making processes in various domains. For instance, Recently,theKolmogorov-ArnoldNetworks(KANs)[14]have
in healthcare time series classification enables the diagnosis been proposed as addressing the limitations of traditional
and monitoring of conditions by analyzing patterns in physio- neuralnetworks.KANshavedemonstratedtobeinterpretable,
logicalsignalssuchaselectrocardiogramsorbrainactivity[1]. even enabling symbolic regression, and have comparable per-
In finance, it enhances risk management and fraud detection formance with MLPs on small scale and science tasks with
by classifying trading behaviors and transaction patterns [2]. shallower architectures. Additional advantages have been ex-
By classifying activities based on sensor data in human ploredfordatafittingandsolvingpartialdifferentialequations
activityrecognition,itsupportspersonalizedrecommendations [15].
and safety monitoring [3]. In remote sensing, it contributes The main critique of the original KAN work is concerned
to environmental monitoring and land use classification by with the fairness of the comparison, triggering substantial
categorizing satellite or aerial imagery data over time [4]. In researchintobetterunderstandingoftheiroverallperformance
these fields, accurate time series classification plays a central beyond the initial small scale scientific tasks. Subsequently
1
5202
voN
1
]GL.sc[
3v40941.1142:viXra

it has been shown that their performance advantage in non- II. RELATEDWORK
scientificMLtaskssuchasvision,naturallanguageandaudio
processing does not hold [16]. Additional work reveals their Kolmogorov-Arnold Networks (KANs) emerged as an in-
reducedeffectivenessonfunctionswithnoise[17]whileother novative alternative to traditional Multi-Layer Perceptrons
works investigate the suitability of replacing the spline func- (MLPs), inspired by the Kolmogorov-Arnold representation
tions with wavelets [18]. The performance of KANs vs MLPs theorem. KANs were shown to outperform MLPs in both
ongraphlearningtasksiscomparedin[19].Theirpreliminary accuracy and interpretability on small-scale scientific tasks.
results reveal that while KANs are on-par with MLPs in Their design, which models complex functions and patterns
classification tasks, they seem to have a clear advantage in with fewer parameters, demonstrated potential to aid in math-
the graph regression tasks. ematical and physical discoveries [14]. Building on these
findings, subsequent research [15] further developed KANs
While KAN-related research is significantly rising, with
to bridge the gap between artificial intelligence and scientific
new scientific works published almost weekly, the study of
research. By allowing KANs to identify relevant features,
KAN architectures for time series has been limited to date.
reveal modular structures, and discover symbolic formulas,
Very early forecasting studies encompass Temporal KANs
KAN2.0[15]introducedabidirectionalapproachthatnotonly
(TKANs) [20], Temporal Kolmogorov Arnold Transformer
incorporates scientific knowledge into KANs but also enables
[21] and mixture-of-experts [22] for various domains from
KANs to extract interpretable scientific insights from data.
traffic and weather to satellite traffic [23] and integrating con-
However, KANs have been shown to be highly sensitive to
volutional layers with KANs to improve time-series forecast-
noise,promptingtheintroductionofoversamplinganddenois-
ing[24].Furthermore,withrespecttotimeseriesclassification,
ingtechniques,suchaskernelfilteringwithdiffusionmaps,to
studies on KANs robustness are emerging [25].
mitigate noise effects [17]. To improve the handling of noisy
Inthispaper,weaimtoconductacomprehensiveandrobust
data, architectural extensions have additionally explored the
exploration of the KAN architecture for time series classifi-
replacement of splines with wavelets [18], enhancing KAN’s
cation on the UCR benchmark. More specifically, we look at
robustness and adaptability in broader applications.
a) how the existing architectures for forecasting [23] transfer
KANs and MLPs were also investigated beyond scientific
to classification, b) the hyperparameter and implementation
datasets in various domains in a controlled study with consis-
influence on the classification performance in view of finding
tent parameters and FLOPs [16]. While MLPs outperformed
the one that performs best on the selected benchmark, c) the
KANs in most areas, KANs retained a distinct advantage in
complexity trade-offs, and d) interpretability advantages. The
symbolic formula representation due to B-spline activation
contributions of this paper are as follows.
functions. Replacing MLPs’ activations with B-splines im-
• A study on the suitability of KAN architectures for proved their performance, suggesting KAN-inspired enhance-
classification tasks on the UCR benchmark consisting of
ments for MLPs. However, KANs faced memory stability
117datasets.Thestudyfirstinvestigatesthefeasibilityof
issues in continual learning, requiring specialized tuning or
transferringexistingarchitecturesdesignedforregression
hybrid models. In graph learning tasks [19], experiments on
followed by finding the most suitable architecture for
node classification, graph classification, and graph regression
classification.
datasets indicated that KANs are on par with MLPs in classi-
• A hyperparameter impact analysis of two KAN imple- fication but exhibit an advantage in graph regression tasks.
mentations, analyzing how variations in grid size, net-
In a real-world satellite traffic forecasting task, KANs
workdepth,andnodeconfigurationsimpactclassification
achieved comparable or superior accuracy to MLPs while us-
performance. The analysis leads to finding the best per-
ing fewer parameters, showcasing their potential in predictive
forming KAN configuration that best generalizes across
analytics [23]. This application framed forecasting as a super-
the 117 datasets.
vised learning problem with specific input-output mappings
• The performance and computational complexity com- across time steps, using a GEO satellite traffic dataset. The
parison of the original KAN, the Efficient KAN im-
successofKANsinthissettingpromptedspecializedvariants,
plementation, and Multi-Layer Perceptrons (MLPs) on
such as Temporal KAN (T-KAN) and Multivariate Temporal
time series classification tasks revealing Efficient KAN’s
KAN (MT-KAN) [26]. T-KAN targets univariate time series,
superior stability across grid sizes, depths, and layer
capturing nonlinear relationships with symbolic regression,
configurations.
while MT-KAN models dependencies between multiple vari-
• We confirm KAN’s interpretability by diving deeper into ables for improved accuracy in multivariate settings. Further
thelearntfeatureimportanceandactivationsfunctionsvs
advancements, such as Temporal Kolmogorov-Arnold Net-
SHAP importance.
works(TKANs),incorporatedLSTM-inspiredmemorylayers,
The paper is structured as follows. We discuss related work excellingintaskssuchascryptocurrencytradingvolumefore-
in Section II. Section III outlines the problem statement, casting. Temporal Kolmogorov-Arnold Transformer (TKAT)
followed by Section IV detailing methodological aspects. A added self-attention mechanisms, outperforming conventional
comprehensive analysis of the results is presented in Section transformers in interpretability and precision in multivariate
V. Lastly, the paper concludes with Section VI. time series forcasting [20], [21]. Signature-Weighted KANs
2

(SigKAN) extended these innovations by integrating path Specifically,insteadofassigningasingleclasslabeltoeach
signatures, making them robust for market volume prediction time series, the classifier outputs a probability distribution
[27].TheReversibleMixtureofKANExperts(RMoK)model, acrossallpossibleclasses.Thatis,foreachtimeseriesX ,the
i
anotherKAN-basedapproach,introducedamixture-of-experts classifier predicts a vector of probabilities P(Y = y X )
i c i
|
structuretoassignvariablestoKANexperts,achievingstrong for each class c 1,2,...,C .
∈{ }
performance in time series forecasting tasks by leveraging The classification function f can be realized through a
temporal feature weights to explain data periodicity [22]. multitude of exiting approaches [7], however we investigate
Although T-KAN, MT-KAN, TKAN, TKAT and SigKAN the recently proposed Kolmogorov Arnold Network (KAN)
extend the Kolmogorov–Arnold mapping, they integrate [14]promisingincreasedinterpretabilityandpotentialcompu-
forecasting-specific modules (e.g. temporal kernels, attention tational benefits compared to standard Multilayer Perceptron
masks) that diverge from the original design. As a result, they (MLP).
are unfit for classification without stripping or redesigning
these components and retraining under a classification objec-
tive. 2
To enhance time series classification robustness, hybrid
0
modelsthatcombineKANandMLParchitectureswerefurther
2
explored [25]. The study employed Efficient KAN as the −
primary implementation of KAN rather than the original
implementation.Twohybridconfigurations,KANMLP(KAN
with an MLP as the final layer) and MLP KAN (MLP with
a KAN as the final layer), were tested across the UCR
datasets, and both hybrids achieved performance comparable
to traditional KAN and MLP models. Notably, MLP KAN
demonstrated increased resilience against adversarial attacks.
ThisrobustnessisattributedtothelowerLipschitzconstantof
KANlayers,suggestingthatcombiningKANwithMLPstruc-
tures can strengthen adversarial resistance in neural networks,
thusopeningpossibilitiesformoresecureandreliablemodels.
Rather than focusing on robustness and hybrid architecture,
thisstudyaimsatunderstandingindepththeperformanceand
interpretability of KANs for time series classification.
III. PROBLEMSTATEMENT
In this paper we analyze the potential of KAN for solv-
ing univariate time-series classification problems. A univari-
ate time series X consists of a sequence of observations
[x ,x ,...,x ], where each x ,t 1,2,...,T represents
1 2 T t ∈ { }
a value observed at time t representing an ordered set of real
values [6].
A class label Y is a categorical variable associated with
a time series X, indicating the class that the time series
belongs to. The number of distinct classes is denoted by the
cardinality C of Y, meaning Y can take a value from the set
y ,y ,...,y . When C = 2, this corresponds to a binary 1 2 C
{ }
classification problem, while C > 2 represents a multiclass
classificationproblem.AsshowninFig.1,whereC =3,each
plot corresponds to a different class, illustrating the distinct
patterns for y , y , and y .
1 2 3
A dataset D = (X ,Y ),(X ,Y ),...,(X ,Y ) con- 1 1 2 2 N N { } sists of pairs (X ,Y ), where X ,i 1,2,3...,N represents
i i i
∈{ }
aunivariatetimeseries,andY isthecorrespondingclasslabel.
i
The task of time series classification involves training a
classifieronadatasetD tomapeachinputX toaprobability
i
distribution across the possible class labels [6].
f(D) Y (1)
≈
xeulaV t
y
1
2
0
2
−
xeulaV t
y
2
2
0
2 −
1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
Timestept
xeulaV t
y
3
Fig. 1: Example of time series data plotted by class, with
time steps on the x-axis and observed values x on the y-axis.
t
Figure depicts SmoothSubspace, one of the 117 datasets from
the UCR repository.
A. KAN for time series classification
The architecture of a KAN is depicted in Fig. 2. It can
be seen from the figure that, for an input instance X , the
i
network outputs Y label assignment probability vector. Y is
i
learnt from D as a composition of L appropriate univariate
functions Φ, as depicted in Fig. 2 and formalized in Eq. 2,
where L stands for the number of layers in the network.
EachlayerofaKANisrepresentedbyamatrixwhereeach
entry is an activation function. If there is a layer with d
in
nodesanditsneighboringlayerwithd nodes,thelayercan
out
be represented as a d d matrix of activation functions:
in out ×
The structure of a KAN can be represented as
[n ,...,n ], where L signifies the total number of layers
1 L+1
in the KAN. A deeper KAN can be thus formulated through
the composition of L layers as:
Y =KAN(X)=(Φ Φ Φ )X. (2) L L−1 1 ◦ ◦···◦
Φ= ϕ , p=1,2,...,d , q =1,2,...,d . (3)
q,p in out { }
Unlike traditional MLPs, where activation functions are
appliedatthenodesthemselves,KANplacesthemattheedges
betweenthenodes.KANemploystheSiLUactivationfunction
3

in combination with B-splines to enhance its expressiveness, Tobetterunderstandtheperformanceoftheevaluatedmod-
as per Eq. 4. This setup allows the edges to control the trans- els, it is crucial to explain their decision-making processes.
formations between layers, while the nodes perform simple Although black-box models achieve high accuracy, they often
summation operations. lack interpretability. KANs offer a shift in the interpretability
paradigm by allowing visualization of the model structure
ϕ(x)=w silu(x)+w spline(x). (4) along with its learned B-splines as shown in Fig. 2. Inter-
b s
pretabilityisfurtherenhancedbymodelpruningthatsimplifies
SiLU is defined as silu(x) = x/(1+e−x). This activation
visual representation by removing less important connections
function allows for smooth, non-linear transformations, which
within the model, which were determined through their sig-
helpsthenetworkcapturecomplexpatternsintimeseriesdata
nificance scores. These scores identify critical connections,
more effectively.
which highlight the most important features for the decision
B-splinesaresmoothpolynomialfunctionsofdegree(order)
ofthemodel.ThisapproachprovidesinsightsintohowKANs
k, which approximate data using control points. The order k
process data and make predictions by focusing on the most
controls the smoothness of the spline. Commonly, k = 3 is
influential connections within the structure of the model.
used for cubic splines. Each spline operates over a defined
grid G, which divides the input space into smaller intervals. 1) KAN learnable parameters: The number of learnable
The grid is determined by a set of grid points that define parameters in a KAN layer is determined by its architecture,
the segments of the spline. Increasing the number of grid whichincludescontributionsfromtheB-splinecontrolpoints,
points increases spline resolution, enabling more fine grained shortcut path weights, B-spline weights, and bias terms. As
approximation of the underlying univariate function. discussedin[16],thenumberoflearnableparametersforeach
A B-spline of order k requires G + k basis functions to KAN layer is:
represent the spline over the grid. For each input (node in a
layer), the evaluation of a B-spline of order k thus involves
computingG+k 1basisfunctionsandperformingaweighted
sum with the cor − responding control points. Parameters=(d in d out ) (G+k+3)+d out , (6)
· ·
G+k−1
(cid:88)
spline(x)= c B (x) (5)
i i
i=0
where d and d represent the input and output dimensions
in out
of the layer. This is consistent with findings in [14], which
p 1 p C alsoemphasizetheroleoflearnablecontrolpointsandweights
associated with the spline functions.
···
2) KAN FLOPs computation: The number of FLOPs in a
Kolmogorov–Arnold Network (KAN) is highly dependent on
+ +
the specific implementation and the way the network is com-
piled on various processor architectures. Different hardware
Φ platforms optimize these computations differently, leading to
L
variationsinpracticalFLOPsperformance.However,weadopt
the theoretical FLOPs computation model as outlined in [16]
··· ··· for consistency and comparison purposes.
ThetotalFLOPsforaKANlayercomefromthreeparts:the
. . .
. . . B-spline transformation, the shortcut path, and the merging of
. . .
thetwobranches.UsingtheDeBoor-Coxiterativeformulation
for B-splines, the FLOPs for one KAN layer in the original
··· ··· KAN implementation is given by Eq. 7 [16]:
+ + +
FLOPs= FLOPs of non-linear function d
in
·
Φ 1 +(d in · d out ) · [9 · k · (G+1.5 · k) (7)
+2 G 2.5 k+3].
· − ·
···
x x
1 T
FLOPs of one forward pass FP through a network with
Fig. 2: KAN architecture.
uniformhiddenlayersofsized d =M M arecalculated
in out
· ·
4

as in Eq. 8 [16]: IV. METHODOLOGY
In this section we elaborate on the methodology adopted
N = FLOPs of non-linear function T
FP
(cid:2) · for this study1. First we provide considerations on data and
+T M 9 k (G+1.5 k)
· · · · · preprocessing, followed by reference model configurations,
(cid:3)
+2 G 2.5 k+3 trainingprocess,hyperparamater,complexityandinterpretabil-
· − ·
(cid:0)
+(L 2) FLOPs of non-linear function M ity analysis.
− · ·
+M2 (cid:2) 9 k (G+1.5 k) (8)
A. Data and preprocessing
· · · ·
(cid:3)(cid:1)
+2 G 2.5 k+3
In this study, the UCR (University of California, River-
· − ·
+FLOPs of non-linear function M side) [28] dataset archive time series classification benchmark
·
+M C (cid:2) 9 k (G+1.5 k) is utilized , which contains a total of 128 univariate datasets
· · · · (cid:3) · from diverse domains, ranging from ECG signals and motion
+2 G 2.5 k+3 .
· − · capture data to spectrographs and simulated control systems.
B. Comparison of KAN to MLP for time series classification The datasets were selected based on their completeness,
since some datasets include time series instances containing
A Multilayer Perceptron (MLP) is a very well known type
missing values. To ensure that an adequate amount of data
of feed-forward neural network widely used for time series
remained for both the training and testing phases, these
classification.
datasetswereexcluded,resultingintotalof117datasetsused.
KANs and MLPs share several architectural principles but
Foreachdataset,theAppendixprovidesthenumberoftraining
differ significantly in how they implement non-linearity and
and test instances, the length of time series, and the number
function approximation. Both are fully connected neural net-
of classes.
works in which each layer’s nodes are densely connected to
Table I further shows descriptive statistics for 117 datasets.
the next. The input layer in each architecture corresponds
Each row represents a statistical measure: minimum, max-
to the length of the input time series, and the output layer
imum, mean, median and standard deviation. The columns
produces a probability distribution over class labels, allowing
correspond to the number of training samples, the number of
for multiclass classification.
test samples, the length of each time series and the number of
However, their treatment of activation differs notably. In
classes across the 117 UCR datasets.
MLPs, activation functions are applied at the neurons (i.e.
In terms of size, for training specifically, the datasets
nodes). In KANs, activation functions are applied on the
vary significantly, ranging from 16 up to 8,926 time series
edges between nodes. Regarding activation functions, the two
instances. The input lengths of these time series also showed
architectures also use different approaches. MLPs commonly
considerable diversity, ranging from 15 to 2,844 time steps
use standard functions such as ReLU, defined as ReLU(z)=
per instance in different datasets. Furthermore, the datasets
max(0,z). KANs employ the SiLU (Sigmoid Linear Unit)
included varying numbers of classes for classification tasks,
activation in combination with B-splines.
with scenarios ranging from binary classifications with 2
1) MLP learnable parameters: The number of learnable
classestomulticlassproblemswithupto60distinctclasses.To
parameters in an MLP is determined by the connections
illustratethediversityinshapeandclassstructure,wevisualize
between neurons across layers. For a fully connected layer
15 randomly selected datasets in Fig. 3 , where each subplot
with d input neurons and d output neurons, the number
in out displays one representative instance per class, with distinct
of learnable parameters [16] is:
colors denoting different classes.
Parameters=(d d )+d . (9) The first step in data preprocessing was normalization,
in out out
using‘StandardScaler‘fromthescikit-learnlibrary.Eachtime
2) MLP FLOPs computation: In a fully connected MLP, series X in the dataset D was standardized by applying the
each connection between two neurons wx + b performs a transformationx = xt−µt,whereµ andσ arethemean
t,scaled σt t t
weightedsumw xandaddsbiasb,resultingin1multiplication and standard deviation for the value at time t across all time
·
and 1 addition. Thus, each connection requires 2 FLOPs. series in D. This ensures that each time point t has a mean of
Foraneuronwithd inputs,calculatingtheoutputrequires 0andastandarddeviationof1,allowingforconsistentscaling
in
2 d FLOPs(forweights)and1FLOPforthebias,resulting across the dataset. This normalization is crucial for ensuring
in
×
inatotalof2 d +1FLOPs.Ifthereared outputneurons, that the input features are on a comparable scale, which helps
in out
×
the total FLOPs for the layer is d (2 d +1). in efficient training.
out in
× ×
We consider fully connected MLP which has input layer Data Availability Statement. The data that support
with T neurons, K hidden layers, with M neurons in each, the findings of this study are available in the UCR
andC neuronsinoutputlayer.FLOPsforforwardpropagation Archive at https://doi.org/10.1109/JAS.2019.1911747,
are therefore calculated as: and are also available in the public domain at
https://www.timeseriesclassification.com/.
N =(M +2MT)+(K 1)(M +2M2)+(M +2MC).
FP
−
(10) 1https://github.com/irina-b1/KAN TS
5

Adiac CricketX Earthquakes FiftyWords GunPoint
NonInvasiveFetalECGThorax2 WordSynonyms Phoneme RefrigerationDevices UWaveGestureLibraryAll
ACSF1 Crop EthanolLevel PigArtPressure PigCVP
Fig. 3: 15 datasets showing one representative time series per class. Distinct colors indicate different classes
Statistic Train Test Length Class
function as in the KAN models, for the same reasons. How-
Min 16 20 15 2
Max 8926 16800 2844 60 ever,insteadofL1weappliedL2regularizationwithaweight
Mean 496.72 1086.72 537.10 8.26 factor of 1, selected through empirical tuning.
Median 181 343 301 3
TheoriginalKANlibrary[14]wasmodifiedtoenableGPU
StdDev 1155.16 2080.59 583.14 12.26
support, allowing the experiments to leverage the computa-
TABLE I: Summary statistics of the 117 UCR archive time
tional power of GPUs rather than relying solely on CPU
series datasets
execution.Thus,allevaluationsofeachmodelwereconducted
on an NVIDIA A100 80GB GPU.
Forperformanceevaluation,weuseprecision,recallandF1
B. Training setup
score. The precision measures how many instances predicted
For training, each dataset was partitioned into a training as a certain class actually belong to that class, expressed
dataset and a validation dataset in an 80:20 ratio. The test as: Precision = TP , where TP (true positives) represents
TP+FP
datasets are provided separately by default. To ensure robust- the number of correctly identified positive instances, and FP
ness and mitigate the effects of random initialization, each (false positives) refers to the number of instances incorrectly
modelwastrainedon5differentrandomseeds.Thepresented identified as positive. Recall measures how many instances of
resultsareaveragesofthese5runsacrossall117datasets.The some class were correctly detected. It is given by: Recall =
models were trained for 500 epochs using batch size 16. TP , where FN (false negatives) represents the number of
TP+FN
The training process across all models used the Adam actual positive instances that the model failed to identify as
optimizer. The baseline architectures from [23] were trained positive.TheF1scoreisexpressedas:F1=2 Precision×Recall,
with a learning rate of 0.001. However, instead of the mean where higher values indicate better performan × ce P i re n cis b io a n l + an R c ec i a n ll g
absolute error (MAE) loss function used for regression tasks precision and recall (better classification).
in the original work, we employed the cross-entropy loss
function to address the classification nature of our problem.
C. Reference architecture configurations
Additionally, we introduced L1 regularization with a weight
factor of 0.1. Initially, we analyze the performance of KAN and MLP by
Similarly, in the baseline MLP models, we used the same adopting the regression designs from the extensive empirical
Adam optimizer, learning rate (0.001), and cross-entropy loss study in [23]. The goal is to gain insights into the generaliza-
6

tion capabilities and transfer potential of these architectures and spline grid resolutions. Taken together, this resulted in
from regression to classification problems. the development and evaluation of several tens of thousands
As discussed in Section III, we employ two different mod- of individual models across the full range of datasets and
els: KAN and MLP. Alongside the original implementation configurations within the UCR archive.
of KAN2, we also include its variant, Efficient KAN3, which
optimizes memory by reformulating the activation process, Hyperparameters Values
applying B-splines directly to inputs and combining them Gridsize G∈{3,5,10,15,20}
linearly, thus avoiding the need for large tensor expansions. It Networkdepth L∈{2,3,...,10}
Hiddenlayersize M ∈{5,10,...,100}
replaces input-based L1 regularization with weight-based L1,
Learningrate lr∈{0.0001,0.001,0.01,0.1,1}
improving efficiency. The L1 regularization is now computed Randomseed {0,1,2,5,42}
as mean absolute value of the spline weights [29]. Batchsize 16
Epochs 500
KAN and Efficient KAN are configured as [T, 40, 40, C],
representingadapth3network,whereT representsthelength TABLE II: Hyperparameters utilised for impact analysis for
oftheinputtimeseries,whileC denotesthenumberofclasses KAN and Efficient KAN models.
forclassification,asperSectionIII.Althoughthisarchitecture
appears to involve two layers between input and output, in
KANs depth refers to the number of trainable connections E. Complexity analysis
betweenlayers.Thus,althoughtherearetwohiddenlayers,the
In this section we evaluate resource consumption by cal-
model has three learnable transformations. A depth 4 variant
culating the average FLOPs over the 117 UCR datasets for
includesanadditionalhiddenlayerwith40nodes.Weretained
one prediction, and the theoretical energy consumption (TEC)
the spline order k =3 and a fixed grid size G=5.
per prediction. FLOPs were computed theoretically using
In contrast, the MLP architecture is configured as [T, 300,
Eqs. 8 and 10 outlined in Section III. As per Section IV-A,
300, 300, C], representing a depth 3 network. The depth 4
T 16,...,8,926 , C 2,...,60 .
variant adds a hidden layer of 300 nodes. ∈{ } ∈{ }
We estimated TEC as TEC = FLOPs [30], where
FLOPS/Watt
FLOPS/Watt represents the number of floating-point oper-
D. Hyperparameter impact analysis
ations executed per second per watt. As the experiments
To provide deeper insights into the KAN architecture’s
were conducted on an NVIDIA A100 80GB PCIe GPU, its
performance and provide design guidelines, we conduct an
theoreticalpowerconsumptionis65GFLOPS/Watt,forfloat32
analysisofhyperparametersandconfigurationparameterswith
operations, which were used for calculation.
thegoaloffindingthebestmodelfortimeseriesclassification
on the UCR behcmark , using a curated subset of 117 UCR F. Interpretability analysis
datasets. To assess hyperparameter effects, we systematically
WedemonstratetheinterpretabilityofKANsonarchitecture
varied grid size (G), network depth (L) and layer width
of shape [15, 15, 15, 3], that is amenable to visualization,
(M). Table II summarizes these parameters, where the first
with a grid size G=5, learning rate lr = 1, and L1 regular-
column lists each hyperparameter and the second indicates
ization of 0.01. The architecture and hyperparameters were
the range of values evaluated. For each of these evaluations,
iteratively optimized to ensure the model’s performance was
the models were trained using different learning rates lr
∈ competitive with MLPs and HiveCote 2.0, ensuring that the
0.0001,0.001,0.01,0.1,1 .
{ } model achieved comparable results while being significantly
The first evaluation examined the effect of grid size, where
less computationally complex. The interpretability results are
G 3,5,10,15,20 while keeping depth and layer size
∈ { } showcased on the SmoothSubspace dataset from the UCR
parameters fixed. Specifically, L=3,M =40.
repository, which has a length of 15 and 3 output classes.
Inthesecondevaluation,wevariedthedepthofthenetwork
However, the methods are equally effective across all datasets
by adjusting the number of layers L between 2 and 10, with
in the UCR repository.
constant grid G=5 and layer size M =40.
Furthermore, to validate the inherent interpretability of
In the final evaluation, the number of nodes per layer M
∈ KANandtoextractanyinsightfromtheMLP,globalSHapley
5,10,...100 was varied, while keeping the depth fixed at
{ } Additive exPlanations (SHAP) values [31] were used. SHAP
L=3 and grid size at G=5.
offers a model-agnostic framework for global interpretability
In summary, to ensure robust and representative results,
by quantifying the average contribution of each feature to the
separate models were trained for each of the 117 UCR
model’s predictions across the entire dataset. The contribution
datasets, with input and output layer sizes matched to the the
of a feature x is represented by its Shapley value, ϕ , which
i i
specifictimeserieslengthsandnumberofclasses,respectively.
is computed based on cooperative game theory. For a model
Multiple hyperparameter settings were tested for each one,
the prediction for an instance X is expressed as:
including different learning rates, depths, hidden layer sizes,
M
2github.com/KindXiaoming/pykan SHAP =ϕ + (cid:88) ϕ , (11)
0 i
3github.com/Blealtan/efficient-kan
i=1
7

where ϕ is the model’s baseline expected value across the [23], here KAN’s transferability to a different problem, i.e.
0
dataset,ϕ istheShapleyvalueoffeaturex ,andMrepresents classification, appears less successful.
i i
the total number of features. By aggregating these values, Lower performance results come with a significantly re-
SHAP enables insights into the global decisions of the model. duced training time of 45 seconds for depth 3 KAN, due to
∼
In addition, SHAP is also utilized to compare the feature theGPUacceleration,asdescribedinSectionIV-E,suggesting
importance of KANs to the MLP architecture. a trade-off between performance and efficiency. However, the
training time in depth 4 KAN increases to 57 seconds,
∼
V. RESULTS reflectingtheimpactoftheaddeddepthoncomputationalcost.
The models trained with the Efficient KAN implementation
Thissectionpresentsacomprehensiveanalysisoftheresults
offer a notable improvement in performance compared to the
through classification performance of reference architectures,
original KAN implementation. The Efficient KAN with 3-
computationalcomplexitycomparison,hyperparameterimpact
depth demonstrates a significant boost in performance with
analysis, and interpretability evaluation.
a mean precision of 0.72, recall of 0.70, and F1 score of
0.70. Similarly, the 4-depth Efficient KAN, maintains high
A. Classification performance analysis of reference architec-
performance metrics with a mean precision of 0.71, recall
tures
of 0.70, and F1 score of 0.69. Improvements in comparison
Table III presents the results of the classifiers with rows to KAN can be attributed to implementation changes, as
representing different models and their configurations. The discussed in Section IV-C.
first two rows provide the results for MLP models and the
The precision of Efficient KAN is slightly lower than
subsequentfourrowsforKANandEfficientKANmodels.The
that of the MLP models, which means that the model may
first column lists the type of model, while the second column
produce more false positives. However, the Efficient KAN
details the specific configuration of each model, including the
model compensates for this with higher recall, indicating
nodesperlayerandgridsizeforKANmodels.Thesubsequent
that it is better at identifying true positives. As a result, the
columnsprovidetheperformancemetricsforeachmodel,split
F1 score is also higher for Efficient KAN. This suggests
intothreemaincategories:precision,recall,andF1score.Each
that while Efficient KAN sacrifices a bit of precision, it
ofthesecategoriesisfurtherdividedintotwosubcolumnsthat
achieves a better overall performance by improving recall and
show the mean and standard deviation (StdDev) of the results
providing a more balanced model for classification. Along
acrossmultiple (i.e.5)runs. Thelastcolumn presentsaverage
with the increased performance, Efficient KAN maintains fast
time, measured in seconds, for training one model.
training times. The training time for the 3-depth model is
TheMLPmodelsdemonstraterelativelyhighandconsistent
approximately91seconds,withaslightincreaseto93seconds
performance across the precision, recall, and F1 score metrics
for the 4-depth model. This shows that while the original
for both depths. For the 3-layer MLP, the mean precision is
KAN implementation is less successful in transferring from
0.73 with a standard deviation of 0.20, and the 4-layer model
timeseriespredictiontoclassificationtasks,theEfficientKAN
exhibits the same mean and standard deviation for precision.
not only achieves this transfer effectively but also generalizes
Intermsofrecall,themeanvaluesareverysimilar,at0.66for
better across different datasets, making it a more effective
the3-layermodeland0.65forthe4-layermodel,withstandard
model overall.
deviations of 0.23 and 0.20, respectively. This indicates that
increasing the depth has little effect on the model’s ability to
B. Complexity analysis for the reference models
identifyrelevantinstances.Additionally,bothmodelsmaintain
comparable F1 score means of 0.64 (3 layers) and 0.62 (4 TableIVpresentsthecomputationalcomplexityanalysisfor
layers),althoughthestandarddeviationincreasesslightlyfrom theMLPandKANconfigurations.Thefirsttwocolumns,list-
0.25 to 0.26, suggesting a minor decrease in consistency for ing the model and configuration, are repeated from Table III.
the F1 score with the deeper model. The subsequent columns provide key complexity metrics: the
TheoriginalKANimplementationsshowasubstantialdrop third column displays the total number of lernable parameters
in performance compared to the MLP models. The 3-depth in each model, while the fourth column reports the average
KAN has a mean precision of 0.38, with a recall of 0.33 theoretical FLOPs for one prediction across all used UCR
and an F1 score of 0.30. The 4-depth KAN model continues datasets,basedonmodelarchitecturesdiscussedinSectionIII.
this trend with slightly lower performance, showing a mean ThelastcolumnpresentstheTheoreticalEnergyConsumption
precision of 0.37, recall of 0.32, and F1 score of 0.29. The (TEC) in Joules, calculated based on the FLOPs and GPU
further decline in performance suggests that adding depth efficiency, as per Section IV-E.
does not improve generalization but may instead lead to In the table we observe that MLPs, with approximately
overfitting, especially across multiple diverse datasets. These 344k and 434k learnable parameters for 3-depth and 4-depth,
results indicate that the original KAN struggles to match respectively, are the most computationally demanding models
the classification performance of the MLP. While previous in terms of learnable parameters and training duration. Their
research demonstrated that KAN performed well for time theoretical FLOPs reach 688,420 and 868,720, while requir-
series prediction and exhibited strong generalization abilities ing1.008 10−5 and1.336 10−5 Joulesofenergypersingle
× ×
8

Precision Recall F1score
Model Configuration TrainingTime(s)
Mean StdDev Mean StdDev Mean StdDev
MLP(3-depth) [300,300,300] 0.73 0.20 0.66 0.23 0.64 0.25 109.50
MLP(4-depth) [300,300,300,300] 0.73 0.20 0.65 0.20 0.62 0.26 105.53
KAN(3-depth) [40,40],G=5 0.38 0.17 0.33 0.21 0.30 0.21 44.99
KAN(4-depth) [40,40,40],G=5 0.37 0.11 0.32 0.20 0.29 0.20 56.88
EfficientKAN(3-depth) [40,40],G=5 0.72 0.20 0.70 0.21 0.70 0.22 90.80
EfficientKAN(4-depth) [40,40,40],G=5 0.71 0.20 0.70 0.22 0.69 0.22 92.71
TABLE III: Performance of reference regression architectures introduced in [23].
Model Configuration LernableParameters Theor.FLOPs TEC(Joules)
MLP(3-depth) [300,300,300] 344518 688420 1.008×10−5
MLP(4-depth) [300,300,300,300] 434818 868720 1.336×10−5
KAN(3-depth) [40,40],G=5 257649 6146993 9.457×10−5
KAN(4-depth) [40,40,40],G=5 275289 6566993 10.103×10−5
EfficientKAN(3-depth) [40,40],G=5 257649 6146993 9.457×10−5
EfficientKAN(4-depth) [40,40,40],G=5 275289 6566993 10.103×10−5
TABLE IV: Comparison of performance and computational characteristics across the reference models
prediction, positioning them as the best-performing models in
theoretical FLOPs and TEC (Total Energy Consumption). 0.7
Next, the table reveal that the original KAN implemen-
0.6
tation has noticeably fewer learnable parameters compared
to the MLP models, consistent with the theoretical analysis 0.5
in Section III-A. Despite the reduction in parameters, they
0.4
come with significantly higher theoretical FLOPs, with values
of 6,146,993 for depth 3 and 6,566,993 for depth 4, due 0.3
to B-spline computation, as per Eq. 8. The energy required
3 5 10 15 20
Grid
for a single prediction also reflects this increase, amounting
to 9.457 10−5 Joules for depth 3 and 10.103 10−5
× ×
Joules for depth 4. These results illustrate a trade-off, where
KAN achieves a smaller parameter count but requires greater
computational resources in terms of FLOPs and energy per
prediction.
The last two rows for the Efficient KAN implementation
show the same number of weights and theoretical FLOPs as
the original KAN implementation, as the model architectures
are identical. Despite higher energy consumption, Efficient
KAN maintains fast training times. Along with the discussed
increased performance, this balance of high performance and
lower computational costs makes these models strong candi-
dates for applications requiring both efficiency and effective-
ness.
However, despite these improvements, MLP models remain
farmoreenergy-efficient,requiring10timeslessenergy(TEC)
per prediction than both KAN and Efficient KAN models.
C. Hyperparameter impact analysis
In this section, we analyze the impact of key hyperparam-
eters on KAN and Efficient KAN models, with Figs. 4, 5 and
6 illustrating results for specific hyperparameter variations as
detailed in Section IV-D. Each figure includes line plots for
five different learning rates, where the same color represents
the results with the same learning rate for both models, with
KANdepictedwithsolidlinesandEfficientKANwithdashed
lines.
The impact of grid size G on model performance was
evaluated across various learning rates, focusing on mean F1
erocs1FnaeM
GridImpact
KAN
EfficientKAN
Lr0,0001
Lr0,001
Lr0,01
Lr0,1
Lr1
Fig. 4: Grid impact on KAN and Efficient KAN models
0.7
0.6
0.5
0.4
0.3
0.2
2 3 4 5 6 7 8 9 10
Depth
erocs1FnaeM
DepthImpact
KAN
EfficientKAN
Lr0,0001
Lr0,001
Lr0,01
Lr0,1
Lr1
Fig. 5: Depth impact on KAN and Efficient KAN models
score outcomes for both KAN and Efficient KAN. As it can
be seen in Fig. 4, results show a general trend of decreasing
F1 performance with increased grid size, which aligns with
findingsthatlargergridconfigurationscanleadtooptimization
challenges in KAN models [25]. This also suggests that
while increasing grid size makes B-splines locally accurate,
it potentially reduces the model’s overall performance by
making it globally inaccurate. While both models’ perfor-
mances decrease with grid size, Efficient KAN maintains
greater stability across grid configurations and learning rates,
with lower learning rates proving more effective in preserving
model performance.
At the lowest learning rates, Efficient KAN achieved the
9

0.7
0.6
0.5
0.4
0.3
0.2
5 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85 90 95 100
LayerSize
erocs1FnaeM
Lower learning rates yielded a more gradual decline, stabiliz-
LayerSizeImpact
ing around 0.3 before slightly decreasing further. Regardless KAN
EfficientKAN of the learning rate, increasing depth consistently resulted in
Lr0,0001
lower performance. These results suggest that KAN performs
Lr0,001
Lr0,01 best with smaller depths and benefits less from deeper con-
Lr0,1
Lr1 figurationsduetochallengesincapturingcomplextime-series
dependencies effectively at greater depths.
We further analyzed the effect of layer size, defined as the
numberofnodesineachlayer,onmodelperformance.Results
are presented in Fig. 6. For Efficient KAN, lower learning
rates (lr = 0.0001 and lr = 0.001) consistently yielded the
Fig. 6: Layer size impact on KAN and Efficient KAN models
best results, with lr =0.01 performing slightly worse. Larger
learning rates led to a significant performance drop, mirroring
previousobservations. Amonglayersizes, configurationswith
highest F1 scores, with lr = 0.0001 and lr = 0.001 yielding
5 and 10 nodes per layer generally underperformed compared
nearly identical and stable results across grid sizes. For these
to larger sizes, which yielded stable F1 scores. These smaller
rates, the F1 score exhibited a slight, linear decrease from
configurations lack the complexity required to model diverse
0.69 at G = 3 to approximately 0.66 at G = 20, suggesting
time-seriesdataeffectively,especiallygiventheshortestseries
minimal sensitivity to grid variation. The learning rate lr =
length of 15 data points. When layer sizes exceeded this
0.01yieldedslightlylowerperformancethanlr =0.0001and
threshold, Efficient KAN maintained consistent performance
lr =0.001, following a similarly gradual decrease across grid
by avoiding overgeneralization and better capturing the data’s
sizes. In contrast, higher learning rates (lr =0.1 and lr =1)
intricacies.
resultedinsignificantlylowerF1scores,averagingaround0.3
For KAN, the trend remained opposite: higher learning
acrossallgridsizes,showinglimitedgridsensitivitybutalmost
rates produced better F1 scores, with lr = 0.1 consistently
50% reduced effectiveness relative to lower rates.
yielding the highest performance. Unlike Efficient KAN,
KAN,incontrast,exhibitedanopposinglearningratetrend,
KAN’s performance gradually improved with increasing layer
with performance improving as learning rates increased. All
size, indicating that a larger number of nodes allowed it to
learningratesforKANshowedasimilarpattern:asubstantial
capture more complex dependencies in the time-series data.
drop in F1 score from G=3 to G=10, followed by a more
A notable increase in F1 performance occurred with a layer
gradualdeclinewithincreasinggridsize.Notably,evenKAN’s
configuration of 30 nodes per layer and a learning rate of
bestconfigurationsfellwellbelowthebestresultsofEfficient
lr =0.001, highlighting this setup’s capacity to leverage both
KAN, underscoring a clear performance gap. A deviation in
themodel’sstructureandtime-seriescomplexity.However,the
KAN’s trend was seen at lr = 1 for G = 3, where the F1
worst-performing configuration for KAN was a high learning
scorewasunexpectedlylowerthanatG=5,unlikeotherrates
rate with very few nodes (5–20 per layer), which led to
where G=3 consistently achieved the highest performance.
significant overgeneralization and poor performance. Smaller
Theeffectofmodeldepthrevealssimilartrends,asshownin configurations likely struggle to represent complex patterns
Fig.5.EfficientKANachievedthehighestperformanceatthe effectively, leading to overly simplistic models that underfit
smallest learning rates (lr = 0.0001 and lr = 0.001), though the data’s temporal dependencies.
differencesbetweentheseratesbecamemorepronouncedwith In summary, the analyses of grid size, depth, and layer
increasing depth. At a learning rate of lr = 0.01, Efficient size reveal clear distinctions in how KAN and Efficient KAN
KAN’s performance declined more sharply with increasing respond to different hyperparameter configurations. Efficient
depth, achieving a peak F1 score of 0.69 at depth 2, but KAN consistently performs best with smaller learning rates,
droppingto0.64atdepth10.Thispatternalignswithprevious showing stability across grid, depth, and layer size variations
research indicating that higher learning rates can destabilize due to its inherent regularization mechanisms. This stability
training by causing the model to overshoot optimal parameter allowsEfficientKANtoavoidoverfittingandadapteffectively
values. In time-series tasks, lower learning rates in combina- even with moderate layer sizes, particularly when layer sizes
tion with Efficient KAN’s regularization mechanisms enable exceed the shortest time series length. In contrast, KAN’s
it to adjust gradually, allowing the model to learn nuanced optimal performance relies on higher learning rates and in-
temporal patterns without abrupt parameter updates, thereby creasedlayersizes,astheseconfigurationsenableittocapture
supporting stable and high performance. more complex dependencies in the time-series data. KAN’s
In contrast, KAN’s behavior across learning rates mirrored performance improves gradually with layer size and depth but
the patterns observed in the grid size analysis, with generally is more sensitive to increases in grid size. Overall, Efficient
lowerperformancecomparedtoEfficientKAN.Forshallower KAN demonstrates a robust ability to maintain high per-
depths (2–3), KAN achieved its best performance with higher formance with conservative hyperparameter settings, whereas
learningrates;however,theseratesledtoasharpperformance KAN benefits more from expanded configurations to reach its
drop as depth increased, with F1 scores falling below 0.2. optimal performance.
10

Precision Recall F1score Trainingtime(seconds)
Model Configuration
Mean StdDev Mean StdDev Mean StdDev Mean StdDev
KAN [40],G=5 0.58 0.19 0.56 0.21 0.54 0.22 6.36 2.8
EfficientKAN [40,40],G=3 0.72 0.20 0.71 0.21 0.70 0.23 95.00 205.1
MLP(3-depth) [300,300,300] 0.73 0.20 0.66 0.23 0.64 0.25 109.5 368.5
InceptionTime / 0.84 0.17 0.83 0.18 0.84 0.18 4006.60 5049.82
Hive-Cote2.0 / 0.87 0.13 0.85 0.16 0.85 0.17 14700.32 57228.95
TABLE V: Comparison of top-performing KAN models vs the reference MLP, InceptionTime and Hive-Cote2 SotA on 117
datasets in UCR archive.
Out of all computed results across various hyperparameter
configurations, we selected the best-performing KAN and 1.0
EfficientKANmodels.TheirresultsarepresentedinTableV.
The table is structured in a similar manner as Table III, along 0.8
with additional column showing mean and standard deviation
of average training time in seconds. 0.6
0.4
F1 score
5 4 3 2 1 0.2
KAN4.6724 1.5905HC2
0.0
MLP3.7198 1.7759InceptionTime
0.0 0.2 0.4 0.6 0.8 1.0
Efficient KAN3.2414 KANMeanF1
Fig. 7: Critical diagram of F1 score for five models
For comparison, we also include results from the MLP
model discussed in Section V-A, InceptionTime [32] baseline
and Hive-Cote 2.0 as a state-of-the-art benchmark. Efficient
KAN demonstrates comparable performance to MLP, with
higher F1 scores and significantly faster training times. Al-
though Hive-Cote 2.0 achieves the highest overall perfor-
mance, Efficient KAN provides a balanced tradeoff with
substantiallyreducedtrainingtime,makingitapracticalalter-
nativefortime-sensitiveapplications.Thisisfurtherillustrated
in the critical difference diagrams in Fig. 7, where Efficient
KAN ranks above MLP but still below Hive-Cote 2.0 and
InceptionTime,reflectingitscompetitiveaccuracywhilemain-
taining efficiency. In contrast, KAN ranks lowest, showing
a more significant deviation in performance. To provide a
more detailed insight into comparison between the three best
developedmodels,wealsoincludethreescatter-plotsinFig.8
, that visualize pairwise comparisons between them: KAN
vs. MLP, Efficient KAN vs. MLP, and KAN vs. Efficient
KAN.Ineachscatterplot,themeanF1-scoreacross5different
runs for each dataset obtained by one model is plotted on
the x-axis, while the mean F1-score of the other model is
plotted on the y-axis. These plots provide an intuitive visual
comparison of relative performance across datasets. Points
above the diagonal line indicate datasets where the model on
the y-axis outperforms the one on the x-axis.
In Figure 8a , Efficient KAN is compared to the original
KAN.Themajorityofpointslieabovethediagonal,indicating
thatEfficientKANachieveshigherF1-scoresthantheoriginal
KAN on most datasets. Similarly, scatter plot in Figure 8b
confirms that Efficient KAN generally outperforms MLP. In
Figure 8c , original KAN is compared to MLP. While MLP
1FnaeMNAKtneicffiE
KANvsEfficientKANMeanF1ScoresperDataset
EfficientKANwinshere
KANwinshere
(a) Efficient KAN vs KAN
1.0
0.8
0.6
0.4
0.2
0.0
0.0 0.2 0.4 0.6 0.8 1.0
MLPMeanF1
1FnaeMNAKtneicffiE
EfficientKANvsMLPMeanF1ScoresperDataset
EfficientKANwinshere
MLPwinshere
(b) Efficient KAN vs MLP
1.0
0.8
0.6
0.4
0.2
0.0
0.0 0.2 0.4 0.6 0.8 1.0
MLPMeanF1
1FnaeMNAK
KANvsMLPMeanF1ScoresperDataset
KANwinshere
MLPwinshere
(c) KAN vs MLP
Fig. 8: Scatter plots comparing mean F1 scores of different
model pairs.
11

outperforms KAN on a number of datasets, the distinction is
y y y
less prominent compared to the previous two comparisons. 1 2 3
D. Interpretability analysis
In this section, we evaluate the interpretability of the
KAN model and compare it with the interpretability of MLP,
following the methodology described in Section IV-F. The
interpretability of the two models is demonstrated using the
SmoothSubspace dataset from the UCR archive shown in
Fig. 1. We compare the interpretability of the KAN model
withthebestMLPconfiguration(seeTableV),whichachieved
an F1 score of almost 0.88 on the used dataset, which is
similar to the fine-tuned KAN model utilised to demonstrate
interpretability described in Section IV-F.
Unlike traditional neural networks such as MLPs, which
requirepost-hoctechniqueslikeSHAPtogaininterpretability,
KANs offer interpretability by design through their composi-
tion graph. Fig. 9 provides a visualization of the structure of
the KAN model, where the thickness of the edges represents
the importance of the connections based on the edge scores
according to Section IV-F. The corresponding B-splines for
these edges show which function is applied to the input
features and provide information on how the input features
are modified by the architecture. The x-axis of the enhanced
x x x x x x x x x x x x x x x
1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
B-splineinFig.9representstherangeofinputfeatures,while
the y-axis indicates the corresponding outputs of the spline
function applied to these inputs.
Looking at the KAN graph in Fig. 9, it can be seen that
features x , x , and x emerge as the most influential for
5 10 12
the models decision, based on the edge weights where thicker
lines represent higher edge weight. Looking at Fig. 1 that
input features x , x are effective in differentiating class y
5 10 2
fromclassesy andy ,whilefeaturex furtherdistinguishes
1 3 12
betweenclassesy andy .Additionally,lookingatclassy in
1 3 3
Fig.1,wecanseethatmajorityofthevalueswithinthedataset
arewhithin[0,1]forinputfeaturex .Lookingatthelearned
12
B-splinecorrespondingtothisfeatureinFig.9wecanseethat
when x is between 0 and 1, the spline increases the values
12
Fig.9:KANmodelwithedgethicknessindicatingconnection
up to 300, while the values outside of this range decrease
importance and B-spline plots showing learned functions on
to values between 0 and -200, diminishing their contribution.
edges.
Similar observations can also be made for the input features
x and x . In contrast, looking at feature x , we can see that
5 10 9
it provides limited relevance for classification indicated by its
thinner connection edgesin Fig. 9 .As seen in Fig. 1,it helps feature for each predicted class. Each figure is divided into
separatingclassy ,butofferslittledistinctionbetweenclasses threesections,correspondingtothethreeoutputclasses.Inthe
2
y and y , where values largely overlap. This aligns with the plots, each feature’s contribution is represented by its SHAP
1 3
low model sensitivity reflected in the KAN graph. value, which indicates whether it positively contributes to the
To validate and further quantify feature contributions and prediction or negatively. Feature values are color-coded, with
also compare feature importance of KAN to MLP, we apply red indicating high values and blue low values. As it can
SHAP analysis as described in Section IV-F. This allows us be seen in Fig. 1, 2 represents the highest value, while 2
−
to validate whether the influential features identified through represents the lowest value. Middle-range values between 1
−
KAN’s structure and learned B-splines in Fig. 9 are also to 1, are shown as purple dots. Purple dots correspond to
reflected consistently by the more established SHAP expla- the flat parts of the series, where consecutive values show
nations. Figs. 10 and 11 display the feature importance for minimalvariation,whileredandbluedotsareassociatedwith
each class of the SmoothSubspace dataset for both KAN and the highly fluctuating sections of the series.
MLP, sorted from the most important to the least important Examining the SHAP plot for the KAN model in Fig. 10,
12

Featureimpactony Featureimpactony Featureimpactony
1 2 3 High
x x x
10 10 12
x x x
7 3 15
x x x
2 12 10
x x x
12 7 11
x x x
3 2 3
x x x
15 9 14
x x x
14 15 9
x x x
1 6 13
x x x
11 1 5
x x x
9 11 1
x x x
5 14 6
x x x
8 8 4
x x x
4 4 7
x x x
13 5 2
x x x
6 13 8
Low
−0.2 −0.1 0.0 0.1 0.2 0.3 0.4 −0.4 −0.2 0.0 0.2 0.4 −0.4−0.3−0.2−0.1 0.0 0.1 0.2
SHAPvalue(impactonmodeloutput) SHAPvalue(impactonmodeloutput) SHAPvalue(impactonmodeloutput)
eulaverutaeF
Fig. 10: SHAP summary plots showing feature impacts in KAN model
Featureimpactony Featureimpactony Featureimpactony
1 2 3 High
x x x
7 7 15
x x x
11 15 11
x x x
10 6 14
x x x
15 14 13
x x x
6 10 12
x x x
13 2 5
x x x
5 9 9
x x x
3 11 7
x x x
2 12 6
x x x
1 13 2
x x x
8 3 4
x x x
14 1 10
x x x
9 4 1
x x x
4 8 3
x x x
12 5 8
Low
−0.4 −0.2 0.0 0.2 0.4 −0.4 −0.2 0.0 0.2 0.4 −0.4−0.3−0.2−0.1 0.0 0.1 0.2 0.3
SHAPvalue(impactonmodeloutput) SHAPvalue(impactonmodeloutput) SHAPvalue(impactonmodeloutput)
eulaverutaeF
Fig. 11: SHAP summary plots showing feature impacts in MLP model
it can be seen that the top contributors, features x and x coherentwiththeunderlyingsequentialpatterns,whichmakes
10 12
consistently stand out, aligning with KAN’s interpretability its feature contributions harder to interpret in relation to the
findings from Fig. 9. Interestingly, compared to the feature original series.
importance from Fig. 9, feature x is not present among the In summary, KAN provides interpretability inherently
5
top contributors according to SHAP. This contrast shows how through its graph structure and learned splines. SHAP is
different interpretability methods can yield complementary employed primarily to validate and complement this built-in
insights, each capturing unique aspects of feature importance. transparency.Incontrast,MLPrequiresSHAPorsimilartools
For the MLP model, which lacks inherent interpretability, to expose any interpretability, underscoring the advantage of
SHAP is essential. Fig. 11 presents SHAP-based feature KANsinapplicationswhereunderstandingmodeldecisionsis
importances for MLP. As it can be seen, feature x is the critical.
7
most important in distinguishing classes y and y , compared
1 2
to x for KAN model. However, for both MLP and KAN
VI. CONCLUSION
10
the x 10 and x 7 are shown as top 4 contributing features in The aim of this study was to conduct a comprehensive
distinguishing between the classes, indicating that both MLP and robust exploration of the KAN architecture for time
andKANmodelingeneralconsidersimilarfeaturesaskeyto series classification. To achieve that, we first investigated
distinguish between the three classes. the transferability of reference Kolmogorov-Arnold Networks
However,whilebothmodelshighlightsimilarfeaturesover- (KANs)fromregressiontoclassificationtasks,runningalarge
all, it is evident that for KAN the SHAP color coding aligns number of models across 117 diverse datasets from the UCR
consistently with the structure of the time series, whereas in Benchmark. We conducted hyperparameter search on two
the MLP the color mapping appears more scattered and less KAN implementations in view of finding the best architecture
13

forthetaskathandandconcludedwithaninterpretabilityanal- [12] D.Teney,A.M.Nicolicioiu,V.Hartmann,andE.Abbasnejad,“Neural
ysis.OurfindingsshowthattheEfficientKANimplementation redshift:Randomnetworksarenotrandomfunctions,”inProceedingsof
theIEEE/CVFConferenceonComputerVisionandPatternRecognition,
has a significant performance improvement over the original
2024,pp.4786–4796.
KAN and is also superior to MLPs by 6 percentage points in [13] N. Ahmed, M. Wahed, and N. C. Thompson, “The growing influence
F1 score on the reference architectures. The hyperparameter of industry in ai research,” Science, vol. 379, no. 6635, pp.
884–886, 2023. [Online]. Available: https://www.science.org/doi/abs/
analysis revealed that Efficient KAN consistently outperforms
10.1126/science.ade2420
KAN across variations in grid size, depth, and layer size, [14] Z. Liu, Y. Wang, S. Vaidya, F. Ruehle, J. Halverson, M. Soljacˇic´,
showcasing its robustness and adaptability to diverse datasets. T.Y.Hou,andM.Tegmark,“Kan:Kolmogorov-arnoldnetworks,”arXiv
preprintarXiv:2404.19756,2024.
Efficient KAN proved more stable than KAN across grid
[15] Z. Liu, P. Ma, Y. Wang, W. Matusik, and M. Tegmark, “Kan
sizes,depths,andlayerconfigurations,particularlywithlower 2.0: Kolmogorov-arnold networks meet science,” arXiv preprint
learning rates. The interpretability of KANs was confirmed arXiv:2408.10205,2024.
[16] R.Yu,W.Yu,andX.Wang,“Kanormlp:Afairercomparison,”arXiv
through SHAP analysis and B-spline visualization, highlight-
preprintarXiv:2407.16674,2024.
ingtheirpotentialfortransparentdecision-making.Incontrast, [17] H. Shen, C. Zeng, J. Wang, and Q. Wang, “Reduced effectiveness of
MLPs, though competitive in performance, exhibited less kolmogorov-arnold networks on functions with noise,” arXiv preprint
arXiv:2407.14882,2024.
interpretability.Futureworkcouldexplorehybridarchitectures
[18] Z. Bozorgasl and H. Chen, “Wav-kan: Wavelet kolmogorov-arnold
and further optimization to enhance KAN’s application scope. networks,”arXivpreprintarXiv:2405.12832,2024.
[19] R. Bresson, G. Nikolentzos, G. Panagopoulos, M. Chatzianastasis,
J. Pang, and M. Vazirgiannis, “Kagnns: Kolmogorov-arnold networks
FUNDING
meetgraphlearning,”arXivpreprintarXiv:2406.18380,2024.
[20] R. Genet and H. Inzirillo, “Tkan: Temporal kolmogorov-arnold net-
ThisworkwassupportedbytheSlovenianResearchAgency
works,”arXivpreprintarXiv:2405.07344,2024.
(Javna Agencija za Raziskovalno Dejavnost RS) under grant [21] ——,“Atemporalkolmogorov-arnoldtransformerfortimeseriesfore-
P2-0016. A preprint has previously been published [33]. casting,”arXivpreprintarXiv:2406.02486,2024.
[22] X.Han,X.Zhang,Y.Wu,Z.Zhang,andZ.Wu,“Kan4tsf:Arekanand
Conflict of Interest: The authors declare that they have no kan-basedmodelseffectivefortimeseriesforecasting?”arXivpreprint
conflict of interest. arXiv:2408.11306,2024.
[23] C. J. Vaca-Rubio, L. Blanco, R. Pereira, and M. Caus, “Kolmogorov-
arnold networks (kans) for time series analysis,” arXiv preprint
REFERENCES arXiv:2405.08790,2024.
[24] I. E. Livieris, “C-kan: A new approach for integrating convolutional
[1] W. K. Wang, I. Chen, L. Hershkovich, J. Yang, A. Shetty, G. Singh, layers with kolmogorov–arnold networks for time-series forecasting,”
Y.Jiang,A.Kotla,J.Z.Shang,R.Yerrabellietal.,“Asystematicreview Mathematics,vol.12,no.19,p.3022,2024.
oftimeseriesclassificationtechniquesusedinbiomedicalapplications,” [25] C. Dong, L. Zheng, and W. Chen, “Kolmogorov-arnold networks
Sensors,vol.22,no.20,p.8016,2022. (kan) for time series classification and robust analysis,” arXiv preprint
[2] R. Devaki, V. Kathiresan, and S. Gunasekaran, “Credit card fraud arXiv:2408.07314,2024.
detectionusingtimeseriesanalysis,”InternationalJournalofComputer [26] K.Xu,L.Chen,andS.Wang,“Kolmogorov-arnoldnetworksfortime
Applications,vol.3,pp.8–10,2014. series: Bridging predictive power and interpretability,” arXiv preprint
[3] J.Yang,M.N.Nguyen,P.P.San,X.Li,andS.Krishnaswamy,“Deep arXiv:2406.02496,2024.
convolutional neural networks on multichannel time series for human [27] H. Inzirillo and R. Genet, “Sigkan: Signature-weighted kolmogorov-
activityrecognition.”inIjcai,vol.15. BuenosAires,Argentina,2015, arnoldnetworksfortimeseries,”arXivpreprintarXiv:2406.17890,2024.
pp.3995–4001. [28] H.A.Dau,A.Bagnall,K.Kamgar,C.-C.M.Yeh,Y.Zhu,S.Gharghabi,
[4] C. Go´mez, J. C. White, and M. A. Wulder, “Optical remotely sensed C. A. Ratanamahatana, and E. Keogh, “The ucr time series archive,”
timeseriesdataforlandcoverclassification:Areview,”ISPRSJournal IEEE/CAAJournalofAutomaticaSinica,vol.6,no.6,pp.1293–1305,
ofphotogrammetryandRemoteSensing,vol.116,pp.55–72,2016. 2019.
[5] A. Bagnall, M. Middlehurst, G. Forestier, A. Ismail-Fawaz, A. Guil- [29] Blealtan, “Efficient-kan,” 2024, gitHub repository. [Online]. Available:
laume, D. Guijo-Rubio, C. W. Tan, A. Dempster, and G. I. Webb, https://github.com/Blealtan/efficient-kan
“A hands-on introduction to time series classification and regression,” [30] B.Subramaniam,W.Saunders,T.Scogland,andW.-c.Feng,“Trendsin
in Proceedings of the 30th ACM SIGKDD Conference on Knowledge energy-efficientcomputing:Aperspectivefromthegreen500,”in2013
DiscoveryandDataMining,2024,pp.6410–6411. InternationalGreenComputingConferenceProceedings. IEEE,2013,
[6] H.IsmailFawaz,G.Forestier,J.Weber,L.Idoumghar,andP.-A.Muller, pp.1–8.
“Deeplearningfortimeseriesclassification:areview,”Dataminingand [31] S. Lundberg, “A unified approach to interpreting model predictions,”
knowledgediscovery,vol.33,no.4,pp.917–963,2019. arXivpreprintarXiv:1705.07874,2017.
[7] M.Middlehurst,P.Scha¨fer,andA.Bagnall,“Bakeoffredux:areview [32] H. Ismail Fawaz, B. Lucas, G. Forestier, C. Pelletier, D. F. Schmidt,
and experimental evaluation of recent time series classification algo- J. Weber, G. I. Webb, L. Idoumghar, P.-A. Muller, and F. Petitjean,
rithms,”DataMiningandKnowledgeDiscovery,pp.1–74,2024. “Inceptiontime: Finding alexnet for time series classification,” Data
[8] A.Bagnall,J.Lines,J.Hills,andA.Bostrom,“Time-seriesclassification MiningandKnowledgeDiscovery,vol.34,no.6,pp.1936–1962,2020.
with cote: The collective of transformation-based ensembles,” IEEE [33] I. Barasˇin, B. Bertalanicˇ, M. Mohorcˇicˇ, and C. Fortuna, “Exploring
Transactions on Knowledge and Data Engineering, vol. 27, no. 9, pp. kolmogorov-arnoldnetworksforinterpretabletimeseriesclassification,”
2522–2535,2015. arXivpreprintarXiv:2411.14904,2024.
[9] M.Middlehurst,J.Large,M.Flynn,J.Lines,A.Bostrom,andA.Bag-
nall,“Hive-cote2.0:anewmetaensemblefortimeseriesclassification,”
MachineLearning,vol.110,no.11,pp.3211–3243,2021.
[10] Y.Liang,H.Wen,Y.Nie,Y.Jiang,M.Jin,D.Song,S.Pan,andQ.Wen,
“Foundation models for time series analysis: A tutorial and survey,”
in Proceedings of the 30th ACM SIGKDD Conference on Knowledge
DiscoveryandDataMining,2024,pp.6555–6565.
[11] G.Bachmann,S.Anagnostidis,andT.Hofmann,“Scalingmlps:Atale
ofinductivebias,”AdvancesinNeuralInformationProcessingSystems,
vol.36,2024.
14

APPENDIX
In this section, we present a summary table of the average F1-scores for the best-performing models identified during our
experiments. Specifically, this includes the Kolmogorov–Arnold Network (KAN) with configuration [40], G = 5 and learning
rate 0.1, the Efficient KAN variant with configuration [40,40], G = 3 and learning rate 0.001, and a baseline Multi-Layer
Perceptron(MLP)withthreehiddenlayersofsize300andalearningrateof0.001.TheresultsarereportedasmeanF1-scores
averaged across five random seeds to ensure robustness and comparability. The table is structured as follows: The first column
lists the dataset names, followed by the size of the training and test subsets. The next column shows the length of the time
series (input) and the number of classes (output), which correspond to the input and output layer sizes of the models. The
remaining columns display the average F1-scores and standard deviations for each model configuration.
Name Train/Test Length/Class KAN Efficient KAN MLP
Adiac 390 / 391 176 / 37 0.401 ± 0.051 0.694 ± 0.019 0.409 ± 0.026
ArrowHead 36 / 175 251 / 3 0.430 ± 0.039 0.688 ± 0.005 0.805 ± 0.013
Beef 30 / 30 470 / 5 0.334 ± 0.092 0.801 ± 0.000 0.889 ± 0.015
BeetleFly 20 / 20 512 / 2 0.565 ± 0.065 0.869 ± 0.028 0.894 ± 0.001
BirdChicken 20 / 20 512 / 2 0.560 ± 0.061 0.734 ± 0.000 0.755 ± 0.051
Car 60 / 60 577 / 4 0.600 ± 0.076 0.803 ± 0.034 0.780 ± 0.016
CBF 30 / 900 128 / 3 0.480 ± 0.063 0.956 ± 0.006 0.857 ± 0.002
ChlorineConcentration 467 / 3840 166 / 3 0.484 ± 0.019 0.741 ± 0.007 0.232 ± 0.000
CinCECGTorso 40 / 1380 1639 / 4 0.425 ± 0.075 0.799 ± 0.010 0.733 ± 0.009
Coffee 28 / 28 286 / 2 0.498 ± 0.076 1.000 ± 0.000 1.000 ± 0.000
Computers 250 / 250 720 / 2 0.538 ± 0.023 0.498 ± 0.007 0.566 ± 0.030
CricketX 390 / 390 300 / 12 0.344 ± 0.009 0.550 ± 0.012 0.446 ± 0.006
CricketY 390 / 390 300 / 12 0.369 ± 0.016 0.546 ± 0.010 0.500 ± 0.012
CricketZ 390 / 390 300 / 12 0.344 ± 0.022 0.555 ± 0.017 0.447 ± 0.025
DiatomSizeReduction 16 / 306 345 / 4 0.401 ± 0.047 0.809 ± 0.020 0.770 ± 0.013
DistalPhalanxOutlineAgeGroup 400 / 139 80 / 3 0.489 ± 0.049 0.589 ± 0.007 0.519 ± 0.016
DistalPhalanxOutlineCorrect 600 / 276 80 / 2 0.677 ± 0.043 0.708 ± 0.004 0.692 ± 0.014
DistalPhalanxTW 400 / 139 80 / 6 0.397 ± 0.026 0.420 ± 0.011 0.329 ± 0.010
Earthquakes 322 / 139 512 / 2 0.495 ± 0.028 0.483 ± 0.025 0.481 ± 0.011
ECG200 100 / 100 96 / 2 0.714 ± 0.075 0.876 ± 0.010 0.804 ± 0.022
ECG5000 500 / 4500 140 / 5 0.495 ± 0.025 0.582 ± 0.007 0.379 ± 0.001
ECGFiveDays 23 / 861 136 / 2 0.556 ± 0.053 0.887 ± 0.005 0.939 ± 0.006
ElectricDevices 8926 / 7711 96 / 7 0.289 ± 0.032 0.488 ± 0.007 0.249 ± 0.016
FaceAll 560 / 1690 131 / 14 0.546 ± 0.042 0.728 ± 0.012 0.659 ± 0.007
FaceFour 24 / 88 350 / 4 0.318 ± 0.027 0.699 ± 0.011 0.774 ± 0.021
FacesUCR 200 / 2050 131 / 14 0.432 ± 0.030 0.741 ± 0.008 0.625 ± 0.012
FiftyWords 450 / 455 270 / 50 0.178 ± 0.019 0.487 ± 0.005 0.190 ± 0.015
Fish 175 / 175 463 / 7 0.675 ± 0.035 0.843 ± 0.006 0.827 ± 0.014
FordA 3601 / 1320 500 / 2 0.482 ± 0.063 0.703 ± 0.007 0.340 ± 0.000
FordB 3636 / 810 500 / 2 0.490 ± 0.022 0.643 ± 0.012 0.331 ± 0.000
GunPoint 50 / 150 150 / 2 0.734 ± 0.081 0.905 ± 0.005 0.727 ± 0.041
Ham 109 / 105 431 / 2 0.640 ± 0.050 0.699 ± 0.007 0.711 ± 0.012
HandOutlines 1000 / 370 2709 / 2 0.787 ± 0.048 0.792 ± 0.007 0.859 ± 0.016
Haptics 155 / 308 1092 / 5 0.389 ± 0.026 0.432 ± 0.007 0.413 ± 0.017
Herring 64 / 64 512 / 2 0.477 ± 0.070 0.568 ± 0.028 0.698 ± 0.035
InlineSkate 100 / 550 1882 / 7 0.229 ± 0.015 0.290 ± 0.009 0.311 ± 0.010
InsectWingbeatSound 220 / 1980 256 / 11 0.359 ± 0.047 0.594 ± 0.004 0.600 ± 0.015
ItalyPowerDemand 67 / 1029 24 / 2 0.878 ± 0.020 0.951 ± 0.002 0.951 ± 0.005
LargeKitchenAppliances 375 / 375 720 / 3 0.480 ± 0.034 0.438 ± 0.013 0.439 ± 0.011
Lightning2 60 / 61 637 / 2 0.661 ± 0.088 0.680 ± 0.026 0.675 ± 0.037
Lightning7 70 / 73 319 / 7 0.361 ± 0.057 0.639 ± 0.017 0.570 ± 0.028
Mallat 55 / 2345 1024 / 8 0.496 ± 0.053 0.921 ± 0.008 0.869 ± 0.041
Meat 60 / 60 448 / 3 0.807 ± 0.125 0.930 ± 0.006 0.939 ± 0.009
MedicalImages 381 / 760 99 / 10 0.361 ± 0.039 0.546 ± 0.015 0.242 ± 0.028
MiddlePhalanxOutlineAgeGroup 400 / 154 80 / 3 0.351 ± 0.043 0.395 ± 0.024 0.227 ± 0.043
MiddlePhalanxOutlineCorrect 600 / 291 80 / 2 0.521 ± 0.043 0.463 ± 0.013 0.420 ± 0.027
MiddlePhalanxTW 399 / 154 80 / 6 0.378 ± 0.026 0.331 ± 0.010 0.251 ± 0.002
MoteStrain 20 / 1252 84 / 2 0.576 ± 0.088 0.811 ± 0.013 0.860 ± 0.002
NonInvasiveFetalECGThorax1 1800 / 1965 750 / 42 0.590 ± 0.038 0.896 ± 0.005 0.777 ± 0.009
NonInvasiveFetalECGThorax2 1800 / 1965 750 / 42 0.582 ± 0.049 0.925 ± 0.002 0.815 ± 0.019
OliveOil 30 / 30 570 / 4 0.531 ± 0.047 0.822 ± 0.033 0.834 ± 0.028
Continued on next page
15

Name Train/Test Length/Class KAN Efficient KAN MLP
OSULeaf 200 / 242 427 / 6 0.427 ± 0.023 0.502 ± 0.020 0.502 ± 0.010
PhalangesOutlinesCorrect 1800 / 858 80 / 2 0.616 ± 0.031 0.693 ± 0.014 0.380 ± 0.000
Phoneme 214 / 1896 1024 / 39 0.034 ± 0.004 0.042 ± 0.001 0.031 ± 0.003
Plane 105 / 105 144 / 7 0.829 ± 0.060 0.982 ± 0.000 0.985 ± 0.005
ProximalPhalanxOutlineAgeGroup 400 / 205 80 / 3 0.698 ± 0.035 0.704 ± 0.008 0.757 ± 0.016
ProximalPhalanxOutlineCorrect 600 / 291 80 / 2 0.780 ± 0.026 0.820 ± 0.009 0.840 ± 0.018
ProximalPhalanxTW 400 / 205 80 / 6 0.473 ± 0.016 0.538 ± 0.013 0.412 ± 0.012
RefrigerationDevices 375 / 375 720 / 3 0.449 ± 0.030 0.412 ± 0.009 0.380 ± 0.009
ScreenType 375 / 375 720 / 3 0.360 ± 0.021 0.410 ± 0.014 0.387 ± 0.013
ShapeletSim 20 / 180 500 / 2 0.466 ± 0.053 0.400 ± 0.043 0.481 ± 0.010
ShapesAll 600 / 600 512 / 60 0.365 ± 0.060 0.684 ± 0.007 0.572 ± 0.015
SmallKitchenAppliances 375 / 375 720 / 3 0.341 ± 0.049 0.472 ± 0.012 0.462 ± 0.012
SonyAIBORobotSurface1 20 / 601 70 / 2 0.523 ± 0.093 0.602 ± 0.008 0.664 ± 0.023
SonyAIBORobotSurface2 27 / 953 65 / 2 0.559 ± 0.056 0.811 ± 0.003 0.811 ± 0.002
StarLightCurves 1000 / 8236 1024 / 3 0.847 ± 0.024 0.916 ± 0.003 0.627 ± 0.001
Strawberry 613 / 370 235 / 2 0.928 ± 0.018 0.959 ± 0.002 0.938 ± 0.005
SwedishLeaf 500 / 625 128 / 15 0.715 ± 0.037 0.886 ± 0.006 0.739 ± 0.023
Symbols 25 / 995 398 / 6 0.313 ± 0.091 0.738 ± 0.007 0.814 ± 0.019
SyntheticControl 300 / 300 60 / 6 0.900 ± 0.016 0.941 ± 0.006 0.924 ± 0.012
ToeSegmentation1 40 / 228 277 / 2 0.501 ± 0.034 0.613 ± 0.012 0.595 ± 0.006
ToeSegmentation2 36 / 130 343 / 2 0.442 ± 0.033 0.575 ± 0.022 0.657 ± 0.016
Trace 100 / 100 275 / 4 0.800 ± 0.038 0.852 ± 0.014 0.626 ± 0.016
TwoLeadECG 23 / 1139 82 / 2 0.561 ± 0.070 0.803 ± 0.007 0.871 ± 0.026
TwoPatterns 1000 / 4000 128 / 4 0.789 ± 0.041 0.918 ± 0.009 0.861 ± 0.011
UWaveGestureLibraryAll 896 / 3582 945 / 8 0.874 ± 0.024 0.947 ± 0.003 0.924 ± 0.008
UWaveGestureLibraryX 896 / 3582 315 / 8 0.597 ± 0.017 0.726 ± 0.002 0.667 ± 0.018
UWaveGestureLibraryY 896 / 3582 315 / 8 0.541 ± 0.018 0.661 ± 0.002 0.617 ± 0.023
UWaveGestureLibraryZ 896 / 3582 315 / 8 0.531 ± 0.027 0.657 ± 0.007 0.576 ± 0.011
Wafer 1000 / 6164 152 / 2 0.963 ± 0.006 0.982 ± 0.002 0.964 ± 0.010
Wine 57 / 54 234 / 2 0.650 ± 0.024 0.783 ± 0.020 0.872 ± 0.033
WordSynonyms 267 / 638 270 / 25 0.188 ± 0.022 0.378 ± 0.012 0.275 ± 0.025
Worms 181 / 77 900 / 5 0.370 ± 0.033 0.450 ± 0.020 0.419 ± 0.022
WormsTwoClass 181 / 77 900 / 2 0.537 ± 0.021 0.568 ± 0.020 0.575 ± 0.031
Yoga 300 / 3000 426 / 2 0.731 ± 0.054 0.840 ± 0.006 0.721 ± 0.022
ACSF1 100 / 100 1460 / 10 0.525 ± 0.057 0.674 ± 0.031 0.636 ± 0.051
BME 30 / 150 128 / 3 0.368 ± 0.040 0.953 ± 0.006 0.957 ± 0.007
Chinatown 20 / 343 24 / 2 0.653 ± 0.129 0.960 ± 0.013 0.951 ± 0.007
Crop 7200 / 16800 46 / 24 0.453 ± 0.022 0.714 ± 0.005 0.442 ± 0.022
DodgerLoopDay 78 / 80 288 / 7 0.155 ± 0.030 0.549 ± 0.026 0.544 ± 0.027
DodgerLoopGame 20 / 138 288 / 2 0.479 ± 0.016 0.648 ± 0.020 0.749 ± 0.004
DodgerLoopWeekend 20 / 138 288 / 2 0.470 ± 0.098 0.708 ± 0.049 0.565 ± 0.223
EOGHorizontalSignal 362 / 362 1250 / 12 0.381 ± 0.051 0.427 ± 0.015 0.431 ± 0.017
EOGVerticalSignal 362 / 362 1250 / 12 0.210 ± 0.023 0.323 ± 0.021 0.351 ± 0.039
EthanolLevel 504 / 500 1751 / 4 0.355 ± 0.030 0.586 ± 0.007 0.648 ± 0.039
FreezerRegularTrain 150 / 2850 301 / 2 0.946 ± 0.027 0.989 ± 0.001 0.967 ± 0.006
FreezerSmallTrain 28 / 2850 301 / 2 0.728 ± 0.023 0.819 ± 0.006 0.804 ± 0.004
Fungi 18 / 186 201 / 18 0.080 ± 0.030 0.536 ± 0.014 0.006 ± 0.003
GunPointAgeSpan 135 / 316 150 / 2 0.932 ± 0.028 0.964 ± 0.001 0.851 ± 0.055
GunPointMaleVersusFemale 135 / 316 150 / 2 0.984 ± 0.009 1.000 ± 0.000 0.932 ± 0.022
GunPointOldVersusYoung 136 / 315 150 / 2 0.999 ± 0.001 1.000 ± 0.000 1.000 ± 0.000
HouseTwenty 40 / 119 2000 / 2 0.727 ± 0.020 0.748 ± 0.007 0.738 ± 0.014
InsectEPGRegularTrain 62 / 249 601 / 3 1.000 ± 0.000 1.000 ± 0.000 1.000 ± 0.000
InsectEPGSmallTrain 17 / 249 601 / 3 0.732 ± 0.155 1.000 ± 0.000 1.000 ± 0.000
MelbournePedestrian 1194 / 2439 24 / 10 0.764 ± 0.032 0.895 ± 0.007 0.642 ± 0.046
MixedShapesRegularTrain 500 / 2425 1024 / 5 0.825 ± 0.024 0.899 ± 0.002 0.872 ± 0.014
MixedShapesSmallTrain 100 / 2425 1024 / 5 0.752 ± 0.028 0.808 ± 0.003 0.803 ± 0.014
PigAirwayPressure 104 / 208 2000 / 52 0.037 ± 0.010 0.080 ± 0.012 0.091 ± 0.010
PigArtPressure 104 / 208 2000 / 52 0.101 ± 0.014 0.157 ± 0.012 0.165 ± 0.021
PigCVP 104 / 208 2000 / 52 0.058 ± 0.021 0.085 ± 0.009 0.062 ± 0.006
PowerCons 180 / 180 144 / 2 0.918 ± 0.040 0.972 ± 0.005 0.999 ± 0.002
Rock 20 / 50 2844 / 4 0.266 ± 0.058 0.605 ± 0.028 0.581 ± 0.017
SemgHandGenderCh2 300 / 600 1500 / 2 0.732 ± 0.025 0.873 ± 0.011 0.790 ± 0.016
SemgHandMovementCh2 450 / 450 1500 / 6 0.411 ± 0.021 0.590 ± 0.010 0.504 ± 0.016
Continued on next page
16

Name Train/Test Length/Class KAN Efficient KAN MLP
SemgHandSubjectCh2 450 / 450 1500 / 5 0.484 ± 0.056 0.873 ± 0.004 0.714 ± 0.056
SmoothSubspace 150 / 150 15 / 3 0.862 ± 0.048 0.974 ± 0.003 0.859 ± 0.009
UMD 36 / 144 150 / 3 0.369 ± 0.071 0.795 ± 0.020 0.911 ± 0.011
17