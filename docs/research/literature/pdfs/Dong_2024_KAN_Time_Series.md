# Dong_2024_KAN_Time_Series

Kolmogorov-Arnold Networks (KAN) for Time
Series Classification and Robust Analysis
Chang Dong1, Liangwei Zheng1, and Weitong Chen ⋆1
1The University of Adelaide
{chang.dong, liangwei.zheng, weitong.chen}@adelaide.edu.au
Abstract. Kolmogorov-ArnoldNetworks(KAN)hasrecentlyattracted
significantattentionasapromisingalternativetotraditionalMulti-Layer
Perceptrons (MLP). Despite their theoretical appeal, KAN require val-
idation on large-scale benchmark datasets. Time series data, which has
becomeincreasinglyprevalentinrecentyears,especiallyunivariatetime
seriesarenaturallysuitedforvalidatingKAN.Therefore,weconducteda
faircomparisonamongKAN,MLP,andmixedstructures.Theresultsin-
dicatethatKANcanachieveperformancecomparableto,orevenslightly
betterthan,MLPacross128timeseriesdatasets.Wealsoperformedan
ablation study on KAN, revealing that the output is primarily deter-
minedbythebasecomponentinsteadofb-splinefunction.Furthermore,
weassessedtherobustnessofthesemodelsandfoundthatKANandthe
hybrid structure MLP KAN exhibit significant robustness advantages,
attributed to their lower Lipschitz constants. This suggests that KAN
andKANlayersholdstrongpotentialtoberobustmodelsortoimprove
the adversarial robustness of other models.
Keywords: Kolmogorov-ArnoldNetworks·Time-Series·AdversarialAt-
tack
1 Introduction
Inrecentyears,time-seriesanalysishasbecomeincreasinglyprevalentinvarious
fields,includinghealthcare[6],humanactivityrecognition[16],remotesensing[17]
etc.Amongthese,timeseriesclassification(TSC)isoneofthekeychallengesin
time series analysis. Due to rapid advancements in machine learning research,
many TSC algorithms have been proposed. Before the prevalence of deep learn-
ing, numerous effective algorithms existed. For instance, NN-DTW [1] is based
on measuring the general similarity of whole sequences using different distance
metrics. Other methods included identifying repeated shapelets in sequences as
features[7],discriminatingtimeseriesbythefrequencyofrepetitionofsomesub-
series [18], and using ensemble methods [13]. However, these approaches often
faced limitations, as they were either difficult to generalize to various scenarios
or had high time complexity.
⋆ Corresponding Author
4202
peS
11
]GL.sc[
3v41370.8042:viXra

2 Chang et al.
In recent years, deep learning-based methods have achieved notable success
in various fields such as image recognition and natural language processing.
Consequently, many techniques from these domains have been adapted for time
seriesclassification,includingConvolutionalNeuralNetworks(CNNs)[9],Recur-
rentNeuralNetworks(RNNs)[11],andTransformers[20].Evenlargemodel-based
classification has found extensive application in time series classification[21].
The development of neural networks is fundamentally rooted in the concept
ofthemulti-layerperceptron(MLP).Regardlessoftheircomplexity,neuralnet-
works retain an architecture similar to that of MLP. According to the Universal
Approximation Theorem (UAT), any function can be approximated by a finite
number of single-layer perceptrons[8]. This theorem underpins the capability
of MLP to model and fit complex distributions. Recently, Liu, et al have pro-
posed a new paradigm for neural networks called Kolmogorov-Arnold Networks
(KAN)[14],whichcontrastswithtraditionalMLP-basedneuralnetworks.Unlike
MLP,KANisbasedonKolmogorov-ArnoldTheory(KAT)[12]andexplicitlyde-
fines the model size required for fitting. Both MLP and KAN have analogous
structures:inMLP,neuronoutputsundergoalineartransformationfollowedby
activation before being passed to the next neuron, whereas in KAN, the edges
serve as learnable activation functions, followed by a linear transformation be-
fore passing to the next neuron. This learnable activation function makes KAN
a potential competitor to MLP neural networks. However, KAN has only been
validated within formulas constructed in the physical domain and has not been
tested on large-scale datasets, leaving its scalability unproven. Univariate time
series are inherently well-suited to KAN’ inputs, making them excellent candi-
datesforvalidation.Furthermore,therobustnessofTSChasgarneredsignificant
attention in recent years[3,4,5,10]. As a new architecture, KAN’ robustness has
not yet been studied. Given these circumstances, to validate the performance
and robustness of KAN in TSC tasks, we conducted the following work:
– We performed a fair comparison across 128 UCR datasets among KAN,
MLP, KAN MLP (KAN with the last layer replaced by MLP), MLP KAN
(MLP with the last layer replaced by KAN) under identical configurations,
and MLP L (MLP with the same number of parameters). We found that
KAN could achieve performance comparable to MLP.
– We conducted an ablation study to investigate the roles of the base and
B-spline functions. The results indicated that the output values were pre-
dominantlydeterminedbythebasefunction.Additionally,weobservedthat
in the absence of the base function, spline functions with large grid sizes
were difficult to optimize.
– WeassessedtherobustnessofKANbycomparingitwithothermodels.Our
findingsrevealedthatKANexhibitedsuperioradversarialrobustnessdueto
its lower Lipschitz constant.

KAN for Time Series Classification and Robust Analysis 3
– We observed an anomalous phenomenon that KAN with higher grid sizes
demonstratedgreaterrobustnessdespitehavingahigherLipschitzconstant.
Weprovidedareasonablehypothesisforthisobservationinthefinalsection.
2 Background
2.1 Kolmogorov-Arnold representation
KAN is inspired by Kolmogorov-Arnold representation theory (KAT). It states
that any multivariate continuous function defined in a bounded domain can be
represented as a finite composition of continuous functions of a single variable
and the binary operation of addition. Specifically, if f is a continuous function
on a bounded domain D ⊂Rn, then there exist continuous functions ϕ and ψ
ij i
such that:
 
2n+1 n
(cid:88) (cid:88)
f(x 1 ,x 2 ,...,x n )= ψ i ϕ ij (x j ), (1)
i=1 j=1
where ϕ :[0,1]→R and ψ :R→R. It transforms the task of learning a mul-
ij i
tivariable function into learning a finite number of univariable functions. Com-
pared to MLP, it explicitly provides the number of one-dimensional functions
needed for fitting. However, these univariable functions could be non-smooth
or even fractal, making it theoretically feasible but practically useless. Never-
theless, Liu et al.[14] found that, by analogy to MLP in neural networks, KAN
need not be limited to two layers and finite width to fit all non-linearities. Fur-
thermore,mostnaturalfunctionstendtobesmoothandhavesparsestructures.
These insights suggest that an scalable KAN could become a strong competitor
to MLP.
2.2 Adversarial Attack
Adversarialattacksinvolveapplyingcarefullycraftedsmallperturbationsr ∈Rd
to input data x ∈ Rd, leading to significant changes in a model’s output, such
as fooling a classifier f :x→Rm with the goal of altering the predicted label.
argmax {f(x)}≠ argmax {f(x )},
adv
(2)
x =x+r, s.t. ||r||2 ≪||x||2.
adv
here,theperturbationr issmallinmagnituderelativetoxasindicatedbytheir
norms. We normally apply these perturbations to test whether the model can
be fooled, thus assessing its robustness. To consider the worst-case scenario, we
typically implement the gradient attacks which require knowledge of all the in-
formation about the model and the data. Among them, the most widely used

4 Chang et al.
methodistheProjectionGradientDescent(PGD)[15],thegradient-baseditera-
tiveattackmethod,whichisthemosteffectivemethodtoevaluatetherobustness
of models against gradient attacks. This can be characterized by:
x(t+1) =Clip {x(t) +α·sign(∇ L(x(t) ,y))}, (3)
adv x,ϵ adv x(t) adv
adv
here, t is the iteration index, Clip {·} ensures that x(t+1) remains within ϵ of
x,ϵ adv
the original input x. This method iteratively adjusts x to maximize the loss
adv
functioninthedirectionthatmovesitawayfromits originalprediction y,while
ensuring x stays within a small perturbation distance ϵ from x.
adv
2.3 Local Lipschitz Constant
A function f : Rm → Rn is defined to be ℓ -locally Lipschitz continuous at
f
radius r if for each i=1,...,n, and ∀ ∥x −x ∥≤r, the following holds:
1 2
∥f(x )−f(x )∥≤ℓ ∥x −x ∥ (4)
1 2 f 1 2
where ℓ is the local Lipschitz constant. Hereafter, we will refer to it simply as
f
the Lipschitz constant. The Lipschitz constant is directly linked to perturbation
stability, which in turn relates to robustness[19].
3 Methodology
3.1 Kolmogorov-Arnold Networks (KAN)
Assume there is a data distribution D ⊆ Rd ×Rm. Our objective is to learn
a function f : x ∈ Rd → y ∈ Rm such that the following risk is minimized
as Rˆ(f) = 1 (cid:80)n ∥y −f(x )∥. The purpose of the KAN is to learn such a
n i=1 i i
representation of f, thereby minimizing the objective loss. The original KAN
usedatwo-layerstructure,whileLiu,etal.[14]extendedtoarbitrarywidthand
depth. In contrast to MLP, the activation function are placed on edges instead
of the neurons, KAN use 3rd-order B-spline (k =3) functions for fitting, which
allows learning sophisticated activation function by controlling the weight of
each basis. In this case, the neuron q in the layer l+1 can be represented as :
n n k+G
(cid:88) (cid:88) (cid:88)
xspline = wspline·Φ (x )= wspline· w ·B (x ), (5)
l+1,q p,q l,q,p l,p p,q i i l,p
p=1 p=1 i=1
where x is the input from an arbitrary neuron p in the previous layer l. The
l,p
input from all n neurons in the previous layer l undergoes a nonlinear trans-
formation produced by a learnable B-spline combination, where G is the grid
size which determines the number of B-spline bases (k+G). This is followed by
a weighted summation to obtain the qth output of xspline. Additionally, KAN
l+1,q

KAN for Time Series Classification and Robust Analysis 5
Fig.1: A three-layer KAN structure with the architecture [3-5-3-1].
introduce a base function similar to residual connections, using weighted silu,
to stabilize optimization, which can be represented as:
n n
xbase = (cid:88) wbase·silu(x )= (cid:88) wbase· x l,p (6)
l+1,q p,q l,p p,q 1+e−xl,p
p=1 p=1
Therefore, the output of the qth neuron in layer l+1 can be represented as:
x =xspline+xbase (7)
l+1,q l+1,q l+1,q
Foramulti-layerKAN,thefinaloutputcanberepresentedasanestedstructure
of layers:
f(x)=f(x ,x ,...,x )=Ψ ◦Ψ ...◦Ψ ◦x (8)
1 2 n L L−1 1
where Ψ denotes the lth layer, which includes the combination of the above two
l
operations: a spline transformation and a base activation silu. Fig. 1 illustrates
a three-layer KAN structure with the architecture [3-5-3-1], clearly depicting
how KAN operate.
3.2 KAN for time series classification
We constructed classifiers using KAN, similar to the structure shown in fig. 1.
Due to the setting of the B-spline fitting interval being [−1,1], the data dis-
tribution outside this interval will not achieve an effective fitting. Instead of
directly adopting the method proposed by Liu et al., which suggested updating

6 Chang et al.
the grid interval according to data distribution, We employed a more straight-
forward approach. We fixed the B-Spline grid interval to [−1,1] throughout the
process, and applied batch normalization to keep the distribution within [−1,1]
in each KAN Layer, to ensure the data distribution conforms to the grid and
optimize the training process. Thus, to build a KAN for TSC, we adopted a 3-
layer structure with the output transformed to the number of classes, having an
architectureof[d-d-128-m],wheredisthesequencelengthandmisthenumber
ofclasses.Meanwhile,WecomparedKANwithMLPthathadthesamenumber
of parameters and neurons per layer, as well as networks where the last layer
of KAN was replaced with MLP (KAN MLP) and the last layer of MLP was
replaced with KAN (MLP KAN). The experimental design is shown in tab. 1.
Table 1: Model Architectures and Parameters(G=5, k= 3 for all B-splines)
Networks Architecture Activation Parameters (≈)
KAN [d-d-128-m] Silu, B-Spline (2+G+k)·d2+(258+128·(G+k))·d
MLP I [d-d-128-m] Relu d2+131d
MLP II [d-10d-128-m] Relu 10d2+1310d
KAN MLP [d-d-128-m] Relu, Silu, B-Spline (2+G+k)·d2+130d
MLP KAN [d-d-128-m] Relu, Silu, B-Spline d2+(2+G+k)·128d
4 Experiment Settings
Dataset: We applied the UCR2018 datasets [2] to evaluate these models. The
UCR Time Series Archive encompasses 128 datasets, which are all univariate.
Thesedatasetsspanadiverserangeofreal-worlddomains,includinghealthcare,
human activity recognition, remote sensing and more. Each dataset comprises a
distinct number of samples, all of which have been pre-partitioned into training
andtestingsets.Reflectingtheintricaciesofreal-worlddata,thearchiveincludes
datasets with missing values, imbalances, and those with limited training sam-
ples.
Evaluation Metrics: We used the accuracy and the F1 score to assess the
performance of all models in tab. 1. During adversarial attacks, we evaluate the
robustness of the models using the Attack Success Rate (ASR).
Experiment setup:Ourexperimentswereexecutedonaserverequippedwith
Nvidia RTX 4090 GPUs, 64 GB RAM, and an AMD EPYC 7320 processor.
Parameter setting: In our experiments, we utilized the open-source GitHub
projectefficient-KAN1 toreplacetheoriginalCPU-basedKANarchitecturepro-
1 Our Github, and efficient-KAN.

KAN for Time Series Classification and Robust Analysis 7
posedbyLiuetal.[14].Thismodification,alongwithswitchingtheoptimizerto
AdamWfromBFGS,allowedforfastertrainingspeeds.Wesetthedropoutrate
to 0.1 and trained all the models for 1000 epochs. The learning rate was initial-
izedat1e-2anddecayedto90%ofitspreviousvalueevery25epochs.Especially
for KAN, we used a weight decay of 1e-2, set L1 regularization for the weights
to 0, and entropy regularization to 1e-5. For adversarial attacks, we employed
the PGD with non-targeted attacks. The perturbation magnitude eps(ϵ) is set
at [0.05, 0.1, 0.25, 0.5], with a step size of 0.01 times eps and 100 iterations for
each attack.
5 Result
5.1 Performance Comparison
Fig.2(a)and(b)showtheaccuracyandF1distributionacross128UCRdatasets
for the five models respectively. We observe that these five models achieve rel-
atively similar performance across the 128 datasets, both in terms of F1 score
andaccuracy.However,KANperformsslightlybetteroverall.Thisconclusionis
also supported by the results shown from the critical diagrams in Fig. 3, where
only KAN and MLP L in the same parameters exhibit statistically significant
differences.Inthecriticaldiagram,KANranksthehighest,indicatingitsstrong
fitting capability and demonstrating that it can achieve performance compara-
ble to, or even better than, traditional neural networks on the benchmark time
series datasets.
(a) Test Accuracy of five models (b) Test F1 Score of five models
Fig.2: Performance comparison of five models across 128 datasets
5.2 Ablation Study of KAN
KANhaveamorecomplexstructurecomparedtoMLP,duetothecombinations
of base and spline functions. The different grid sizes of spline functions have
varying impacts on performance. To evaluate their influences, we investigated
three configurations of KAN as follows:

8 Chang et al.
Fig.3: Critical diagram of accuracy for five models across 128 datasets (higher
rank is better)
1. Complete KAN with different grid sizes: 1, 5, 50
2. KAN with only the wpline component, with different grid sizes: 1, 5, 50
3. KAN with only the base component
Table 2: Test accuracy of models with different architectures on the 128
dataset. The values corresponding to columns 1, 5, and 50 represent the
number of datasets out of 128 where the accuracy of the grid size
corresponding to each row is greater than or equal to that of the grid size in
the column, under the same architecture. Q1, Q2, and Q3 denote the quantiles
of the accuracy distribution across the 128 datasets.
KAN Configuration Grid Size 1 5 50 Q1 Q2 Q3
1 128 64 96 0.6000 0.7991 0.9214
w/ base & Spline 5 76 128 112 0.6146 0.7750 0.9387
50 39 24 128 0.5626 0.6976 0.847
1 128 100 122 0.5591 0.7571 0.9009
w/o Base 5 40 128 119 0.5054 0.6706 0.8271
50 13 19 128 0.2226 0.4315 0.5732
w/o Spline - - 0.5652 0.7698 0.9000
Tab. 2 presents the overall performance of these three configurations across
128datasets.Weobservedthatanexcessivelylargegridsizeleadstoperformance
degradation,regardlessofwhetheritisinthecompleteKANorwithoutthebase
function. In the complete KAN, there is little difference in performance with
smaller grid sizes. For grid size = 1, nearly 50% of the datasets achieved over
80% accuracy, whereas for grid size = 50, this value drops to less than 70%. In
theKANwithoutthebasefunction,overallperformancesignificantlydeclinesas
thegridsizeincreases.Particularly,forgridsize=50,theaccuracyof50%ofthe
datasets is below 43.15%. Additionally, we found that the performance of KAN
without the spline function is close to that of the KAN network with only the
spline function and with grid size = 1. This indicates that the fitting capability

KAN for Time Series Classification and Robust Analysis 9
Table 3: Test(Train) accuracy of different KAN on the CBF dataset.
KAN Configuration 1 5 50
w/ Base & Spline 0.9011(0.9667) 0.9644(0.9667) 0.9300(0.9667)
w/o Base 0.8722(1.0000) 0.8644(0.9667) 0.3178(0.6667)
w/o Spline 0.8811(1.0000) 0.8811(1.0000) 0.8811(1.0000)
of KAN largely comes from the simple activation functions, suggesting that
complex B-spline combinations may lead to optimization difficulties. To explain
the result above, we analyzed the CBF dataset, which exhibited results similar
to the overall trend as shown in tab. 3. Most results are comparable, except for
the model with only the Spline function and a grid size of 50, which performed
significantly worse. We analyzed the output results of the two parts at the last
layer as shown in the fig. 4.
Weobservedtwophenomenaacrossboththetrainingandtestingsets:First,
the output values of the spline are relatively smaller and more concentrated
compared to those of the base configuration. This indicates that the spline’s
contribution to the final decision is less significant than that of the base, sug-
gestingthatthebaseconfigurationplaysamorecriticalroleindecision-making.
Second, the most significant difference between fig. 4c and 4d is the distinct
distribution observed when the base component is removed. When the grid size
is set to 1, the output distributions for these three configurations are similar,
exhibiting two prominent peaks on both the positive and negative sides, with
thenegativepeakbeinghigherandmorenumerous.Thispatternoccursbecause
the CBF dataset has 3 categories, thus, when one class is predicted with high
confidence, the other two classes tend to output negative values. However, this
scenario changes drastically at a grid size of 50. Here, the spline output shows
onlyasinglepeakconcentratedaroundzerobothinthetrainingandtestingset,
correspondingtotheloweraccuracyobservedintab.2foragridsizeof50(with-
out Base). This further confirms that an excessively large grid size complicates
the network’s optimization.
5.3 Evaluation and Analysis of Adversarial Robustness
We also found that KAN demonstrate better robustness compared to MLP. We
performed PGD untargeted attacks on the aforementioned five models, with ϵ
ranging from 0.05 to 0.5. The results consistently show that KAN significantly
outperformMLP.Fig.5illustratestheASRofPGDonthesemodels.Weobserve
thatKANandMLP KANexhibitremarkablerobustnesscomparedtotheother
three models, with this advantage increasing as ϵ grows. Specifically, at ϵ=0.5,
the MLP KAN model shows the best robustness among the five, with the ASR
on50%ofthedatasetremainingbelowapproximately75%,whereastheASRfor
MLP, MLP L, and KAN MLP approach 1 for nearly 50% of the dataset. From

10 Chang et al.
(a) Train: Grid Size = 1 (b) Train: Grid Size = 50
(c) Test: Grid Size = 1 (d) Test: Grid Size = 50
Fig.4: Distribution of the flattened Train/Test output values of the last layer
of the model under different configurations on the CBF dataset. (a) Train:
Grid size of 1, (b)Train: Grid size of 50, (c) Test: Grid size of 1, and (d)Test:
Grid size of 50.
fig.6,itisevidentthatKANandMLP KANdemonstratesignificantlydifferent
robustness across 128 datasets compared to the other three models.
To explain this phenomenon, we obtained the Lipschitz constants for the
KAN, MLP, and MLP KAN models. Fig. 7 shows the distribution of Lipschitz
constant differences across 128 datasets. Fig. 8a and 8b both indicate that the
model with KAN layer generally results in a decrease in the Lipschitz constants
for most datasets, which is consistent with the observations in fig. 5. The com-
bination of spline functions produced by KAN with a low grid size tends to be
smooth and flat, making it difficult for small changes in input to cause signifi-
cant changes in the output y. Additionally, as shown in the previous fig. 4, the
output distribution of the B-spline function is more narrow compared to the
combination of activation and linear functions, thus contributing minimally to

KAN for Time Series Classification and Robust Analysis 11
(a) eps = 0.05 (b) eps = 0.1
(c) eps = 0.25 (d) eps = 0.5
Fig.5: ASR distribution across 128 datasets for five models in different
perturbation eps.
the output. This could be the primary reason why KAN is more robust under
attack.
However,weobservedtheoppositeresultinanotherexperiment.Fig.8shows
that the Lipschitz constant corresponding to a larger grid size is greater. This is
evident because as the number of grids increases, the slopes of the spline basis
also increase, making the overall B-spline function more likely to produce larger
slopes. However, the results indicate that a larger Lipschitz constant leads to
greaterrobustness,with104outof128datasetshavinganASRlessthanorequal
to that corresponding to a grid size of 1, demonstrating stronger robustness.
We preliminarily believe this might be because the value distribution produced
by the B-spline is much smaller compared to the base function, thus the base
contributes the majority in decision-making. However, the gradients of the B-
spline with a larger grid size are substantial, thus during PGD attacks, the
gradient is mainly provided by the B-spline part, which might not necessarily
provide the correct direction compared to the base. Therefore, networks with
larger Lipschitz constants exhibit stronger robustness. This may also further
imply why models are difficult to optimize as the grid size increases.

12 Chang et al.
(a) eps = 0.05 (b) eps = 0.1
(c) eps = 0.25 (d) eps = 0.5
Fig.6: Critical diagram of ASR rank across 128 datasets for five models in
different perturbation eps (lower rank is better)
(a) KAN - MLP (b) MLP KAN - MLP
Fig.7: Lipschitz constant distribution differences across 128 dataset
(a) Grid Size 50 vs Grid Size 1 (b) Grid Size 1 - Grid Size 50
Fig.8: Comparison of (a) ASR and (b) Lipschitz constant distribution
differences across 128 dataset between Grid Size of 50 and Grid Size of 1

KAN for Time Series Classification and Robust Analysis 13
6 Conclusion
In this paper, we applied the KAN in Time Series Classification and conducted
a fair comparison among KAN, MLP, and mixed structures. We found that
KAN can achieve comparable performance to MLP. Additionally, we analyzed
the importance of each component of KAN and discovered that a larger grid
size can be difficult to optimize, leading to lower performance. Furthermore,
we evaluated the adversarial robustness of KAN and these models, finding that
KAN exhibited remarkable robustness. This robustness is attributed to KAN’s
lower Lipschitz constant. Moreover, we found that KAN with a larger grid size
have a greater Lipschitz constant but exhibit stronger robustness. We provided
anexplanationforthisphenomenon,althoughitrequiresfurtherverificationand
broader experiments in our future work.
7 Acknowledgments
We thank all the creators and providers of the UCR time series benchmark
datasets. This research work is supported by Australian Research Council Link-
age Project (LP230200821), Australian Research Council Discovery Projects
(DP240103070 ), Australian Research Council ARC Early Career Industry Fel-
lowship (IE230100119), Australian Research Council ARC Early Career Indus-
tryFellowship(IE240100275),andUniversityofAdelaide,SustainabilityFAME
Strategy Internal Grant 2023.

14 Chang et al.
References
1. Bagnall, A., Lines, J., Bostrom, A., Large, J., Keogh, E.: The great time series
classification bake off: a review and experimental evaluation of recent algorithmic
advances. Data mining and knowledge discovery 31, 606–660 (2017)
2. Dau, H.A., Bagnall, A., Kamgar, K., Yeh, C.C.M., Zhu, Y., Gharghabi, S.,
Ratanamahatana,C.A.,Keogh,E.:Theucrtimeseriesarchive.IEEE/CAAJour-
nal of Automatica Sinica 6(6), 1293–1305 (2019)
3. Dong, C., Li, Z., Zheng, L., Chen, W., Zhang, W.E.: Boosting certificate ro-
bustness for time series classification with efficient self-ensemble. arXiv preprint
arXiv:2409.02802 (2024)
4. Dong, C.G., Zheng, L.N., Chen, W., Zhang, W.E., Yue, L.: Swap: Exploiting
second-rankedlogitsforadversarialattacksontimeseries.In:2023IEEEInterna-
tional Conference on Knowledge Graph (ICKG). pp. 117–125. IEEE (2023)
5. Fawaz, H.I., Forestier, G., Weber, J., Idoumghar, L., Muller, P.A.: Adversarial
attacksondeepneuralnetworksfortimeseriesclassification.In:2019International
Joint Conference on Neural Networks (IJCNN). pp. 1–8. IEEE (2019)
6. Forestier, G., Petitjean, F., Senin, P., Despinoy, F., Huaulm´e, A., Fawaz, H.I.,
Weber,J.,Idoumghar,L.,Muller,P.A.,Jannin,P.:Surgicalmotionanalysisusing
discriminative interpretable patterns. Artificial intelligence in medicine 91, 3–11
(2018)
7. Hills, J., Lines, J., Baranauskas, E., Mapp, J., Bagnall, A.: Classification of time
seriesbyshapelettransformation.Dataminingandknowledgediscovery 28,851–
881 (2014)
8. Hornik,K.,Stinchcombe,M.,White,H.:Multilayerfeedforwardnetworksareuni-
versal approximators. Neural networks 2(5), 359–366 (1989)
9. Ismail Fawaz, H., Lucas, B., Forestier, G., Pelletier, C., Schmidt, D.F., Weber,
J.,Webb, G.I.,Idoumghar,L.,Muller,P.A.,Petitjean,F.: Inceptiontime:Finding
alexnetfortimeseriesclassification.DataMiningandKnowledgeDiscovery34(6),
1936–1962 (2020)
10. Karim, F., Majumdar, S., Darabi, H.: Adversarial attacks on time series. IEEE
transactionsonpatternanalysisandmachineintelligence43(10),3309–3320(2020)
11. Karim,F.,Majumdar,S.,Darabi,H.,Chen,S.:Lstmfullyconvolutionalnetworks
for time series classification. IEEE access 6, 1662–1669 (2017)
12. Kolmogorov, A.N.: On the representation of continuous functions of several vari-
ables by superpositions of continuous functions of a smaller number of variables.
American Mathematical Society (1961)
13. Lines, J., Taylor, S., Bagnall, A.: Hive-cote: The hierarchical vote collective of
transformation-based ensembles for time series classification. In: 2016 IEEE 16th
International Conference on Data Mining (ICDM). pp. 1041–1046 (2016). https:
//doi.org/10.1109/ICDM.2016.0133
14. Liu, Z., Wang, Y., Vaidya, S., Ruehle, F., Halverson, J., Soljaˇci´c, M., Hou, T.Y.,
Tegmark,M.:Kan:Kolmogorov-arnoldnetworks.arXivpreprintarXiv:2404.19756
(2024)
15. Madry,A.,Makelov,A.,Schmidt,L.,Tsipras,D.,Vladu,A.:Towardsdeeplearning
models resistant to adversarial attacks. arXiv preprint arXiv:1706.06083 (2017)
16. Nweke,H.F.,Teh,Y.W.,Al-Garadi,M.A.,Alo,U.R.:Deeplearningalgorithmsfor
human activity recognition using mobile and wearable sensor networks: State of
the art and research challenges. Expert Systems with Applications 105, 233–261
(2018)

KAN for Time Series Classification and Robust Analysis 15
17. Pelletier,C.,Webb,G.I.,Petitjean,F.:Temporalconvolutionalneuralnetworkfor
theclassificationofsatelliteimagetimeseries.RemoteSensing 11(5), 523(2019)
18. Scha¨fer,P.:Thebossisconcernedwithtimeseriesclassificationinthepresenceof
noise. Data Mining and Knowledge Discovery 29, 1505–1530 (2015)
19. Tholeti,T.,Kalyani,S.:Therobustwaytostackandbag:thelocallipschitzway.
arXiv preprint arXiv:2206.00513 (2022)
20. Wen, Q., Zhou, T., Zhang, C., Chen, W., Ma, Z., Yan, J., Sun, L.: Transformers
in time series: A survey. arXiv preprint arXiv:2202.07125 (2022)
21. Zhou, T., Niu, P., Sun, L., Jin, R., et al.: One fits all: Power general time series
analysis by pretrained lm. Advances in neural information processing systems 36,
43322–43355 (2023)