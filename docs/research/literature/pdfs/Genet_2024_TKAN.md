# Genet_2024_TKAN

## Page 1

TKAN: Temporal Kolmogorov-Arnold Networks
Rémi Genet∗§ and Hugo Inzirillo†§
∗DRM, Université Paris Dauphine - PSL
† CREST-ENSAE, Institut Polytechnique de Paris
Abstract—Recurrent Neural Networks (RNNs) have revolu-
tionized many areas of machine learning, particularly in natural
language and data sequence processing. Long Short-Term Memory
(LSTM) networks have demonstrated their ability to capture
long-term dependencies in sequential data. Inspired by the
Kolmogorov-Arnold Networks (KANs), a promising alternative
to Multi-Layer Perceptrons (MLPs), we propose a new neural
network architecture inspired by KAN and LSTM, called
“Temporal Kolomogorov-Arnold Networks” (TKANs). TKANs
combine the strength of both networks. They are composed
of Recurring Kolmogorov-Arnold Networks (RKANs) Layers
embedding memory management. This innovation enables us to
perform multi-step time series forecasting with enhanced accuracy
and efficiency. By addressing the limitations of traditional models
in handling complex sequential patterns, the TKAN architecture
offers significant potential for advancements in fields requiring
more than one step ahead forecasting.
Fig. 1: Temporal Kolmogorov-Arnold Networks (TKAN)
I. INTRODUCTION
Time series forecasting is an important branch of statistical
analysis and machine learning. The development of machine
learning models has accelerated rapidly in the past few years.
Time series, which can be defined as sequences of data indexed
in time, are essential in finance, meteorology, and even in the
field of healthcare. The ability to accurately predict the future
evolution of such data has become a strategic issue for many
different industries that are constantly seeking innovation. In
recent years, the growing interest in this area of research is
mainly due to the massive increase in the availability of data.
Moreover, the increased computer processing capacity now
makes it possible to process large datasets. As a second driver
for innovation, new statistical methods, deep learning tech-
niques [1] and hybrid models have offered new opportunities
to improve the accuracy and efficiency of forecasts. Besides
§These authors contributed equally.
econometric models such as ARMA/ARIMA ([2], [3]) and
their numerous extensions, Recurrent Neural Networks (RNNs)
[4] yield families of models that have been recognized for their
proven effectiveness in terms of forecasting [5].
RNNs have been proposed to address the "persistence
problem", i.e. the potential dependencies between the successive
observations of some time series. Therefore, RNNs most often
outperform "static" networks as MLPs [6]. Traditional methods
of gradient descent may not be sufficiently effective for training
Recurrent Neural Networks (RNNs), particularly in capturing
long-term dependencies [7]. Meanwhile, [8] conducted an
empirical study revealing the effectiveness of gated mechanisms
in enhancing the learning capabilities of RNNs. Actually, RNNs
have proved to be one of the most powerful tools for processing
sequential data and solving a wide range of difficult problems in
the fields of automatic natural language processing, translation,
image processing and time series analysis where MLPs [9],
[10], [11] cannot perform well. When it comes to sequential
data management, MLPs face limitations. Unlike RNNs, MLPs,
are not designed to manage sequential data, information only
flows in one direction, from input to output (feedforward
connection). This specifica tion makes them not suitable
for modeling temporal sequences where taking into account
sequential patterns is essential for prediction. Another weakness
of MLPs is that these networks have no embedded mechanism
for cell memory state management. Recurrent Neural Networks
(RNNs) [12], [13] have provided an answer to these problems.
However, standard RNNs have solved one problem but created
another: "vanishing" or "exploding gradient problem" [14].
Traditional methods of gradient descent may not be sufficiently
effective for training RNNs, particularly in capturing long-term
dependencies [7]. Meanwhile, [8] conducted an empirical study
revealing the effectiveness of gated mechanisms in enhancing
the learning capabilities of RNNs. Actually, RNNs have proved
to be one of the most powerful tools for processing sequential
data and solving a wide range of difficult problems in the fields
of automatic natural language processing, translation, and time
series analysis. Recently, Liu et al. [15] proposed Kolmogorov-
Arnold Networks (KANs) as an alternative to MLPs. The
Kolmogorov-Arnold Network (KAN) is an efficient new neural
network architecture known for its improved performance
and interpretability. Unlike traditional models, KANs apply
activation functions on the connections between nodes, and
these functions can even learn and adapt during training. In
addition to using KAN Layer, Temporal Kolmogorov-Arnold
Networks (TKANs) manage temporality within a data sequence.
arXiv:2405.07344v4  [cs.LG]  14 Jul 2025


---

## Page 2

The idea is to design a new family of neural networks capable
of catching long-term dependency. Our primary idea is to
introduce an external memory module which can be attached
to KAN Layers. This "memory" can store information that
is relevant to the temporal context and can be accessed by
the network during processing. This allows the network to
explicitly learn and utilize past information. Codes are available
at TKAN repository and can be installed using the following
command: pip install tkan. Data are accessible if the
reader wishes to reproduce our experiments using the GitHub
link provided above.
II. KOLMOGOROV-ARNOLD NETWORKS (KANS)
Multi-Layer Perceptrons (MLPs) [9] are extension of original
perceptron proposed by [16]. They were inspired by the
universal approximation theorem [11] which states that a feed-
forward network (FFN) with a single hidden layer containing
a finite number of neurons can arbitrarily well approximate
any continuous functions on a compact subset of Rn. On
the other side, Kolmogorov-Arnold Networks (KAN) focuses
on the Kolmogorov-Arnold representation theorem [17]. The
Kolmogorov-Arnold representation theorem states that any
multivariate continuous function f can be represented as
a composition of univariate functions and through additive
operations:
f(x1, . . . , xn) =
2n+1
X
q=1
Φq
 n
X
p=1
ϕq,p(xp)
!
(1)
where ϕq,p are univariates functions that map each input
variable xp ∈[0, 1] to R, and Φq : R →R. Since all functions
to be learnt are univariate, we can parametrize every 1D
function as a B-spline curve. The learnable coefficients are then
associated with local B-spline basis functions. The key insight
comes when we see the similarities between MLPs and KAN.
In MLPs, a layer includes a linear transformation followed by
nonlinear operations, and you can make the network deeper
by adding more layers. A KAN layer is rather
Φ = {ϕq,p},
p = 1, 2, . . . , nin,
q = 1, 2 . . . , nout,
(2)
where ϕq,p are parametrized function of learnable parameters.
In the Kolmogorov-Arnold theorem, the inner functions form
a KAN layer with nin = n and nout = 2n + 1, and the outer
functions form a KAN layer with nin = 2n + 1 and nout =
1. So, the Kolmogorov-Arnold representations in eq. (1) are
simply compositions of two KAN layers. Now it becomes clear
what it means to have Deep Kolmogorov-Arnold representation.
Taking the notation from [15] let us define a shape of KAN
[n0, n1, · · · , nL], where ni is the number of nodes in the ith
layer of the computational graph. We denote the ith neuron
in the lth layer by (l, i), and the activation value of the (l, i)-
neuron by xl,i. Between layer l and layer l+1, there are nlnl+1
activation functions: the activation function that connects (l, i)
and (l + 1, j) is denoted by
ϕl,j,i,
l = 0, · · · , L −1,
i = 1, · · · , nl,
j = 1, · · · , nl+1.
(3)
The pre-activation of ϕl,j,i is simply xl,i; the post-activation
of ϕl,j,i is denoted by ˜xl,j,i ≡ϕl,j,i(xl,i). The activation value
of the (l + 1, j) neuron is simply the sum of all incoming
post-activations:
xl+1,j =
nl
X
i=1
˜xl,j,i =
nl
X
i=1
ϕl,j,i(xl,i),
j = 1, · · · , nl+1.
(4)
Rewriting it under the matrix form will give:
xl+1 =





ϕl,1,1(·)
ϕl,1,2(·)
· · ·
ϕl,1,nl(·)
ϕl,2,1(·)
ϕl,2,2(·)
· · ·
ϕl,2,nl(·)
...
...
...
ϕl,nl+1,1(·)
ϕl,nl+1,2(·)
· · ·
ϕl,nl+1,nl(·)





|
{z
}
Φl
xl,
(5)
where Φl is the function matrix corresponding to the lth KAN
layer. A general KAN network is a composition of L layers:
given an input vector x0 ∈Rn0, the output of KAN is:
KAN(x) = (ΦL−1 ◦ΦL−2 ◦· · · ◦Φ1 ◦Φ0)x.
(6)
III. TEMPORAL KOLMOGOROV-ARNOLD NETWORKS
(TKANS)
Fig. 2: Temporal Kolmogorov-Arnold Networks (TKAN)
After proposing the RKAN (Recurrent Kolmogorov-Arnold
Network), which integrates temporality management by adapt-
ing the concept of Kolmogorov-Arnold networks to temporal
sequences, we developed an additional innovation to build our
neural network: the TKAN layer. This TKAN layer combines
the RKAN architecture with a slightly modified LSTM (Long
Short-Term Memory) cell. The idea is to propose an extension
of the model proposed by [15] to manage sequential data and
temporality during the learning task. The objective is to provide
a framework for time series forecasting on multiple steps ahead.
As discussed previously, RNNs’ weakness generally lies in the
difficulty of capturing the persistence of information when some
input sequence is quite long, resulting in a significant loss of
information in some tasks. LSTMs address this problem through
the use of a gating mechanism. LSTMs can be computationally
more expensive than standard RNNs; however, this extra
complexity is often justified by better performance on complex
learning tasks. The integration of an LSTM cell combined
2


---

## Page 3

with the RKAN enables the capture of complex nonlinearities
with learnable activation functions of RKAN, but also the
maintenance of a memory of past events over long periods with
the LSTM cell architecture. This combination offers superior
modeling power for tasks involving complex sequential data.
The major components of the TKAN are:
• RKAN Layers: RKAN layers enable the retention of short
term memory from previous states within the network.
Each RKAN layer manages this short term memory
throughout the processing in each layer.
• Gating Mechanisms: these mechanisms help to manage
the information flow. The model decides which informa-
tion should be retained or forgotten over time.
A. Recurring Kolmogorov-Arnold Networks (RKAN)
In neural networks, particularly in the context of recurrent
neural networks (RNN), a recurrent kernel refers to the set of
weights that are applied to the hidden state from the previous
timestep during the network’s operation. This kernel plays a
crucial role in how an RNN processes sequential data over
time. Let us denote τ = 1, 2, ... some discrete time steps. Each
step has a forward pass and backward pass. During the forward
pass, the output or activation of units are computed. During the
backward pass, the computation of the error for all weights is
made. During each timestep, an RNN receives an input vector
and the hidden state from the previous timestep ht−1 . The
recurrent kernel is a matrix of weights that transforms this
previous hidden state. This operation is usually followed by
an addition; the result of this transformation is passed through
a non-linear function, an activation function f(.), that can
take many forms: tanh, ReLU etc. The update stage could be
formulated as:
ht = f(Whhht−1 + Whxxt + bh),
(7)
where ht is the hidden state at time t ∈τ; Wh and Wx
are the recurrent kernel, a weight matrix that transforms the
previous hidden states ht−1, and the input kernel, a weight
matrix transforming the current input denoted xt, respectively.
In the next sections, we propose a new way of updating KANs.
We propose a process to maintain the memory of past inputs
by incorporating previous hidden states into the current states,
enabling the network to exhibit dynamic temporal behavior.
Recurrent Kernel is the key so that RKAN layers learn from
sequences for which context and order matter. We design the
TKAN to leverage the power of Kolmogorov-Arnold Network
while offering memory management to handle time dependency.
To introduce time dependency, we modify each transformation
function ϕl. Let’s denote the sublayers’ memory state ˜hl,t,
initialized with zeros and of shape (KANout). The input that
is fed to each sub KAN layers in the RKAN are created by
doing:
sl,t = Wl,˜xxt + Wl,˜h˜hl,t−1,
(8)
where Wl,˜x is the weight of the l-th layer applied to xt which
is the input at time t. Moreover, Wl,˜h are the weights of the
l-th layer applied to its previous substate. Let us first denote
KANin and KANout, the input dimension of RKAN Layer
input and outputs, respectively. The shape of Wl,˜x ∈R(d,KANin)
and Wl,˜h ∈R(KANout,KANin), which leads to sKANin
l,t
. Set
˜ot = ϕl(sl,t),
(9)
where ϕl is a KAN layer. The "memory" step ˜hl,t is defined
as a combination of past hidden states, such as:
˜hl,t = Whh˜hl,t−1 + Whz˜ot,
(10)
introducing vectors of weights, that weight the importance of
past values relative to the most recent inputs.
B. TKAN Architecture
Fig. 3: A three layers Temporal Kolmogorov-Arnold Networks
(TKAN) Block
For the next step, our aim is to manage memory and we
took inspiration from LSTM [18], [19]. We denote xt the input
vector of dimension d. This unit uses several internal vectors
and gates to manage information flow. The forget gate with
activation vector ft given by
ft = σ(Wfxt + Ufht−1 + bf),
(11)
decides what information to forget from the previous state. The
input gate, with activation vector denoted it, with
it = σ(Wixt + Uiht−1 + bi),
(12)
controls which new information to include. The output gate,
with activation vector ot. Set
rt = Concat[ϕ1(s1,t), ϕ2(s2,t), ..., ϕL(sL,t)],
(13)
where rt is a concatenation of the output of multiple KAN
Layers, and
ot = σ(Wort + bo),
(14)
where Wo ∈R(KANout∗L,out), out denoting the output dimen-
sion of TKAN. Equation (14) determines what information
from the current state to output given rt given from (13). ˜ht
is the "sub" memory of the RKAN layers. The hidden state of
the TKAN layer, ht, captures the unit’s output, while the cell
state ct is updated as follows:
ct = ft ⊙ct−1 + it ⊙˜ct,
(15)
3


---

## Page 4

where ˜ct = σ(Wcxt + Ucht−1 + bc) represents its internal
memory. All these internal states have a dimensionality of h.
The output of the final hidden layer, denoted ht, is given by:
ht = ot ⊙tanh(ct).
(16)
In the following section, we will describe the learning task
and proceed with several tests. We started to test the power of
prediction of our model for one step ahead forecasting and in
the second time for multi-step ahead [20], [21].
IV. LEARNING TASK
In order to assess the relevance of extending our model, we
created a simple training task to judge its ability to improve
the out-of-sample prediction accuracy over several steps ahead
for standard layers such as GRU or LSTM. We have chosen
to carry out our study not on synthetic data, but rather on real
market data, as this seems more relevant to us. Indeed, synthetic
market data can be easily biased to match an experiment.
A. Task Definition and Dataset
The task is to predict the market notional trades over future
periods. This is recognized as a difficult task as the market
behavior is difficult to predict. Nonetheless, this should not be
impossible as, unlike returns, volumes have internal patterns
such as seasonality, autocorrelation, and so on. We used Binance
as our only data source, as it is the largest player in the
crypto-currency market. Moreover, due to the lack of an overall
regulation that would take into account all exchange data,
exchanges are subject to a lot of falsified data by small players
who use wash trading to boost their figures.
Our dataset consists of the notional amounts traded each
hour on several assets: BTC, ETH, ADA, XMR, EOS, MATIC,
TRX, FTM, BNB, XLM, ENJ, CHZ, BUSD, ATOM, LINK,
ETC, XRP, BCH and LTC, which are to be used to predict
just one of them, BTC. The data period runs from January 1,
2020 to December 31, 2022.
B. Preprocessing
Data preparation is a necessary step for most machine
learning methods, in order to help gradient descent calculations
when data are of different sizes, to obtain stationarity series,
etc. This is even more true when using the Kolmogorov-Arnold
network, as the underlying B-Spline activation functions exhibit
power exponent. Thus, having poorly scaled data would result
in over or underflows that would hinder learning. This is also
true for market volume data, or notional data. Indeed, they
are series with very different scales across assets and between
points in time, not to mention non-stationarity issues over a
long period.
To obtain data that can be used for training, but also return
meaningful losses to optimize, we use a two-stage scaling. The
first step is to divide the values in the series by the moving
median of the last two weeks. This moving median window
is also shifted by the number of steps forward we want to
predict, so as not to include foresight. This first pre-treatment
aims to make the series more stationary over time. The second
pre-processing we apply is a simple MinMaxScaling per asset:
even if the minimum of the series is 0, this way of working
is simply a matter of dividing by its maximum value. The
objective is to scale the data in the [0, 1] interval to avoid an
explosive effect during learning due to the power exponent.
This pre-processing is, however, adjusted on the training set,
the adjustment meaning only the search for the maximum
value of each series, which is then used directly on the test
set. This means that, on the test set, it is possible to obtain
observations that are greater than 1. As long as no optimization
is launched, this is not a problem. Finally, we split our dataset
into a training set and a test set, with a standard proportion of
80-20. This represents over 21,000 points in the training set
and 5,000 in the test set.
C. Loss Function for Model Training
Since we have a numerical prediction problem, we have
opted to optimize our model using the root mean square error
(RMSE) as the loss function, whose formula is simple: RMSE
is the square root of
MSE = 1
N
N
X
i=1

ˆX(i)
t+1 −X(i)
t+1
2
,
where N represents the number of samples in the dataset,
ˆX(i)
t+1 denotes the predicted notional values of Bitcoin at time
t + 1 for the i-th sample, and the quantities X(i)
t+1 are the
corresponding true values. We invoke RMSE first because it is
the most widely used and standard loss in machine learning for
this type of problem. The second reason is related to the metric
we want to use to display the results, namely the R-squared
(R2). Indeed, (R2) is interesting as a metric because it not
only gives information on the error but also on the error given
the variance of the estimated series, which means it’s much
easier to tell whether the model is performing well or not. This
explains why it is a measure widely used by econometricians
and practitioners. However, minimizing MSE is exactly the
same problem as maximizing the (R2), as its formula indicates:
R2 = 1 −
PN
i=1( ˆX(i)
t+1 −X(i)
t+1)2
PN
i=1(X(i)
t+1 −¯Xt+1)2 ,
D. Benchmarks
1) Model Architectures: In order to compare with compara-
ble things, we tested our TKAN layers against two of the most
widely used RNNs for multi-step predictions, namely gated
recurrent units (GRU) and long short-term memory (LSTM).
As can be seen, we are not comparing ourselves to complete
model architectures such as a temporal fusion transformer, as
what we are proposing is more a layer than a complete model
architecture.
To fairly compare the three models, we have opted for a very
simple configuration. We create three models to be compared
in the same way:
4


---

## Page 5

1) An initial recurrent layer of 100 units that returns
complete sequences,
2) An intermediate recurrent layer of 100 units, which
returns only the last hidden state,
3) A final dense layer with linear activation, with as many
units as there are timesteps to predict ahead
For the TKAN model, we used 5 B-spline activations of order
0 to 4 as sublayer activations, while we used the standard
activation function for GRU and LSTM. Finally, we also
compared the three models to the most naive benchmark, which
consists of using the last value as a predictor of the future,
the value being repeated when using several predictions in
advance.
2) Note on training details: Metrics are calculated directly
on scaled data and not on unscaled data. There are two reasons
for this: firstly, MinMax scaling has no impact on the metric
since the minimum is 0 and the data interval is [0, 1]; rescaling
would not have changed the R-squared. Rescaling from the
median split would have caused the series mean to be unstable
over time. This would have resulted in the error magnitude
drifting for certain parts of the series, making the metric
unreliable or meaningless. In terms of optimizing model details,
we used the Adam optimizer, one of the most popular choices,
used 20% of our training set as a validation set and included
two training recalls. The first is an early learning stopper,
which interrupts training after 6 consecutive periods without
improvement on the validation set, and restores the weights
associated with the best loss obtained on the validation set.
The second is a plateau learning rate reduction, which halves
the learning rate after three consecutive periods showing no
improvement on the validation set.
E. Results
To evaluate the model’s performance, taking into account
the risk of poor adaptation that may occur, we repeat the
experiment 5 times for each, and display below the mean and
standard deviation of the train results obtained from these 5
experiments.
TABLE I: Average (R2) obtained over 5 runs
Time
TKAN:5 B-Spline
GRU:default
LSTM:default
Last Value
1
0.33736
0.365136
0.355532
0.292171
3
0.21227
0.200674
0.061220
-0.062813
6
0.13784
0.082504
-0.225838
-0.331346
9
0.09803
0.087164
-0.290584
-0.457718
12
0.10401
0.017864
-0.473220
-0.518252
15
0.09512
0.033423
-0.404432
-0.555633
TABLE II: Standard Deviation of the (R2) obtained over 5
runs
Time
TKAN:5 B-Spline
GRU:default
LSTM:default
1
0.00704
0.008336
0.011163
3
0.00446
0.004848
0.080200
6
0.01249
0.023637
0.062710
9
0.02430
0.014833
0.052729
12
0.00132
0.086386
0.085746
15
0.00701
0.024078
0.092729
1) Performance Metrics Summary: The results show a
very logical decrease in terms of R2 with the number of
forward steps ahead, which is quite normal since we have
less information for the forward steps. However, the results
clearly show two things: the first is that while all models have a
relatively small difference in performance over a short horizon
such as 1 to 3 steps ahead, the relative performances change
much more with a longer time horizon. The LSTM model even
becomes useless and counter-productive with 6 periods, while
TKAN and GRU always achieve a higher average R-squared
value. However, TKAN stands out with longer time steps, with
an R-squared value at least 25% higher than that of GRU.
Another very interesting point is model stability, i.e. the ability
to calibrate well-functioning weights from samples without
too much variation from one experiment to the next, and here
again, TKAN showed much better stability than all the other
models.
2) Training Dynamics and Model Stability: To better under-
stand the differences in performance between the models, we
visualized training and validation losses over several training
sessions for each model. These graphs offer a dynamic view of
each model’s learning process and ability to generalize beyond
the training data.
Fig. 4: TKAN training and validation loss over epochs
Fig. 5: GRU training and validation loss over epochs
5


---

## Page 6

Fig. 6: LSTM training and validation loss over epochs
The visual representations clearly corroborate the statistical
results presented above. The GRU and LSTM models show a
significant divergence between their learning loss and validation
trajectories, particularly as the number of epochs increases.
This divergence suggests a potential overfitting where the
model learns idiosyncrasies from the training data rather than
generalizing them. This stability in the TKAN model’s learning
process, evident in the closer alignment of its learning and
validation loss curves, implies a consistent learning model that
effectively captures the underlying patterns in the data without
overfitting.
V. CONCLUSION
In this paper, we proposed an adaptation of the Kolmogorov-
Arnold Network architecture for time series that incorporates
both recurring and gating mechanisms. The architecture,
while not so complicated, enables improving multiple steps’
performances and stability compared to traditional methods
and seems to be promising. The temporal Kolmogorov-Arnold
networks (TKANs) combine the best features of recurrent
neural networks (RNNs) and Kolmogorov-Arnold Networks
(KANs). This new architecture tackles the usual problems
of RNNs (long-term dependency). TKANs embed Recurrent
Kolmogorov-Arnold Networks (RKAN). These layers help the
system to memorize and use new and old information efficiently.
Compared to more traditional models such as LSTM and GRU,
TKAN particularly stands out when it comes to making longer-
term predictions, showing that it is capable of handling different
situations and longer periods of time. Our experiments show
that it is usable and more stable than GRU and LSTM on real
historical market data. While not specifically interesting for
short-term predictions, it especially demonstrates an ability to
largely outperform other models when it comes to multi-step
predictions.This also confirms that the idea developed in the
original KAN paper works well on real use cases and is totally
relevant for time series analysis. This paper opens interesting
new ways to improve our capacities to calibrate accurate time-
series models over multiple steps, which is one of the hardest
tasks in temporal analysis.
REFERENCES
[1] O. B. Sezer, M. U. Gudelek, and A. M. Ozbayoglu, “Financial time
series forecasting with deep learning: A systematic literature review:
2005–2019,” Applied soft computing, vol. 90, p. 106181, 2020.
[2] S. Makridakis and M. Hibon, “Arma models and the box–jenkins
methodology,” Journal of forecasting, vol. 16, no. 3, pp. 147–163, 1997.
[3] P. Mondal, L. Shit, and S. Goswami, “Study of effectiveness of time
series modeling (arima) in forecasting stock prices,” International Journal
of Computer Science, Engineering and Applications, vol. 4, no. 2, p. 13,
2014.
[4] L. R. Medsker, L. Jain et al., “Recurrent neural networks,” Design and
Applications, vol. 5, no. 64-67, p. 2, 2001.
[5] H. Hewamalage, C. Bergmeir, and K. Bandara, “Recurrent neural
networks for time series forecasting: Current status and future directions,”
International Journal of Forecasting, vol. 37, no. 1, pp. 388–427, 2021.
[6] Q. V. Le, N. Jaitly, and G. E. Hinton, “A simple way to initialize recurrent
networks of rectified linear units,” arXiv preprint arXiv:1504.00941, 2015.
[7] Y. Bengio, P. Simard, and P. Frasconi, “Learning long-term dependencies
with gradient descent is difficult,” IEEE Transactions on Neural Networks,
vol. 5, no. 2, pp. 157–166, 1994.
[8] J. Chung, Ç. Gülçehre, K. Cho, and Y. Bengio, “Empirical evaluation
of gated recurrent neural networks on sequence modeling,” CoRR, vol.
abs/1412.3555, 2014.
[9] K. Hornik, M. Stinchcombe, and H. White, “Multilayer feedforward
networks are universal approximators,” Neural networks, vol. 2, no. 5,
pp. 359–366, 1989.
[10] S. Haykin, Neural networks: a comprehensive foundation.
Prentice Hall
PTR, 1998.
[11] G. Cybenko, “Approximation by superpositions of a sigmoidal function,”
Mathematics of control, signals and systems, vol. 2, no. 4, pp. 303–314,
1989.
[12] P. J. Werbos, “Backpropagation through time: what it does and how to
do it,” Proceedings of the IEEE, vol. 78, no. 10, pp. 1550–1560, 1990.
[13] R. J. Williams, “A learning algorithm for continually running fully
recurrent neural netwokrs,” Neural Computation, vol. 1, pp. 256–263,
1989.
[14] S. Hochreiter, “The vanishing gradient problem during learning recurrent
neural nets and problem solutions,” International Journal of Uncertainty,
Fuzziness and Knowledge-Based Systems, vol. 6, no. 02, pp. 107–116,
1998.
[15] Z. Liu, Y. Wang, S. Vaidya, F. Ruehle, J. Halverson, M. Soljaˇci´c, T. Y.
Hou, and M. Tegmark, “Kan: Kolmogorov-arnold networks,” arXiv
preprint arXiv:2404.19756, 2024.
[16] F. Rosenblatt, “The perceptron: A probabilistic model for information
storage and organization in the brain.” Psychological Review, vol. 65,
pp. 386–408, 1958.
[17] A. N. Kolmogorov, On the representation of continuous functions of
several variables by superpositions of continuous functions of a smaller
number of variables.
American Mathematical Society, 1961.
[18] S. Hochreiter and J. Schmidhuber, “Long short-term memory,” Neural
computation, vol. 9, no. 8, pp. 1735–1780, 1997.
[19] R. C. Staudemeyer and E. R. Morris, “Understanding lstm–a tutorial
into long short-term memory recurrent neural networks,” arXiv preprint
arXiv:1909.09586, 2019.
[20] C. Fan, Y. Zhang, Y. Pan, X. Li, C. Zhang, R. Yuan, D. Wu, W. Wang,
J. Pei, and H. Huang, “Multi-horizon time series forecasting with
temporal attention learning,” in Proceedings of the 25th ACM SIGKDD
International conference on knowledge discovery & data mining, 2019,
pp. 2527–2535.
[21] B. Lim, S. Ö. Arık, N. Loeff, and T. Pfister, “Temporal fusion transformers
for interpretable multi-horizon time series forecasting,” International
Journal of Forecasting, vol. 37, no. 4, pp. 1748–1764, 2021.
6
