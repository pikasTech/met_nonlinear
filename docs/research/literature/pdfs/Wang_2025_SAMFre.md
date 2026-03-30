# Wang_2025_SAMFre

arXiv:2505.17532v1  [cs.LG]  23 May 2025
TimeCF: A TimeMixer-Based Model with adaptive Convolution and
Sharpness-Aware Minimization Frequency Domain Loss for
long-term time seris forecasting
Bin Wanga, Heming Yanga and Jinfang Shenga,∗
aSchool of Computer Science and Engineering, Central South University, ChangSha, 410000, HuNan, China
A R T I C L E I N F O
Keywords:
Time series forecast
Fourier Transform
Convolution
Sharpness-aware minimization
A B S T R A C T
Recent studies have shown that by introducing prior knowledge, multi-scale analysis of complex
and non-stationary time series in real environments can achieve good results in the field of long-
term forecasting. However, affected by channel-independent methods, models based on multi-scale
analysis may produce suboptimal prediction results due to the autocorrelation between time series
labels, which in turn affects the generalization ability of the model. To address this challenge,
we are inspired by the idea of sharpness-aware minimization and the recently proposed FreDF
method and design a deep learning model TimeCF for long-term time series forecasting based
on the TimeMixer, combined with our designed adaptive convolution information aggregation
module and Sharpness-Aware Minimization Frequency Domain Loss (SAMFre). Specifically,
TimeCF first decomposes the original time series into sequences of different scales. Next, the
same-sized convolution modules are used to adaptively aggregate information of different scales
on sequences of different scales. Then, decomposing each sequence into season and trend parts and
the two parts are mixed at different scales through bottom-up and top-down methods respectively.
Finally, different scales are aggregated through a Feed-Forward Network. What’s more, extensive
experimental results on different real-world datasets show that our proposed TimeCF has excellent
performance in the field of long-term forecasting.
1. Introduction
With the development of information technology in the past decade, time series forecasting, a field of great
significance to human life, has been supported by information technology resources such as computing power and
algorithms and has played an indispensable role in key areas related to human living standards, such as financial level
prediction(Sonkavde, Dharrao, Bongale, Deokate, Doreswamy and Bhat (2023)), traffic flow planning(Huo, Zhang,
Wang, Gao, Hu and Yin (2023); Huang, Zhang, Feng, Ye and Li (2023)), weather forecast(Bi, Xie, Zhang, Chen, Gu
and Tian (2023)), water treatment(Farhi, Kohen, Mamane and Shavitt (2021); Afan, Mohtar, Khaleel, Kamel, Mansoor,
Alsultani, Ahmed, Sherif and El-Shafie (2024)), energy and power resource allocation(Alkhayat and Mehmood (2021);
Yin, Cao and Liu (2023)). Since the begin of time series forecasting, there are mainly the following model architectures:
Models based on CNN(Li, Jian, Wan, Geng, Fang, Chen, Gao, Jiang and Zhu (2024)), Models based on RNN(Salinas,
Flunkert, Gasthaus and Januschowski (2020)), Models based on Transformer(Liang, Yang, Deng and Yang (2024)) and
Models based on MLP(Challu, Olivares, Oreshkin, RamÃŋrez, Canseco and Dubrawski (2023)).
Although researchers have proposed a variety of methods to solve the problem of time series forecasting, the process
of capturing and building a model of time series from the past to the future is challenging because the natural sequence
of time series has complex and non-stationary properties and the noise from the data acquisition equipment can affect
the prediction results. In order to solve this problem, the current mainstream research can be divided into two categories:
one is based on the Transformer(Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser and Polosukhin (2017)),
which achieves the fitting of time series through a large number of parameters. However, although the large number of
parameters of the Transformer can solve the problem of complex and non-stationary time series to some extent, its easy
overfitting and slow training speed have not been reliably solved. Therefore, after fully studying the components of
time series, researchers use the prior knowledge of physics and mathematics to decompose time series into simpler
components to reduce the difficulty of the prediction process. On this basis, TimeMixer(Wang, Wu, Shi, Hu, Luo, Ma,
∗Corresponding author
wb_csut@csu.edu.cn (B. Wang); 244712142@csu.edu.cn (H. Yang); jfsheng@csu.edu.cn (J. Sheng)
ORCID(s): 0009-0002-0536-2898 (B. Wang); 0009-0009-1683-6068 (H. Yang); 0000-0002-6533-7822 (J. Sheng)
Bin Wang et al.: Preprint submitted to Elsevier
Page 1 of 10
Zhang and Zhou (2024)) further introduced the idea of multi-scale decomposition, and TimeKAN(Huang, Zhao, Li and
Bai (2025)) proposed modeling based on frequencies of different scales based on TimeMixer. In summary, current
researchers hope to simplify the original time series to provide additional prior information for the time series model,
thereby imporving the prediction accuracy of the time series forecasting model.
It is undeniable that the model based on the idea of channel independence does obtain more accurate results under
certain conditions, but the actual time series is a series with high autocorrelation. This autocorrelation is manifested in
that it is not only correlated in the order of time, but also has a certain degree of correlation between the labels of the
sequence. Therefore, under the premise of channel independence, the autocorrelation between labels has not been fully
processed, which may cause a certain degree of distortion in the results of the model. Fortunately, a method called
FreDF(Wang, Pan, Chen, Yang, Zhang, Yang, Liu, Li and Tao (2024)) has recently been applied to the field of time
series forecasting. It uses Fourier or fast Fourier transform to transform the sequence labels from the time domain to the
frequency domain without changing the model structure to deal with the autocorrelation in the time series. In addition,
we note that an idea called sharpness-aware minimization(SAM)(Foret, Kleiner, Mobahi and Neyshabur (2021)) can be
combined with FreDF to reduce the sharpness of the loss so that the model has better generalization ability. At the
same time, inspired by the idea of attention mechanism in Transformer and the idea of receptive field in CNN field,
we found that neighboring and global information can also be used in time series to supplement information in the
prediction process. Therefore, we propose to use convolution kernels of the same size at different scales to obtain global
information at low-frequency scales and neighboring information at high-frequency scales to achieve the aggregation of
global and local information with a small number of parameters.
Combining the advantages of the above technologies, we propose a frequency-independent multi-scale hybrid
architecture (TimeCF) based on the TimeMixer model to solve the problems of global and local information loss,
autocorrelation between sequence labels in time series forecasting and generalization ability. In terms of model structure,
TimeCF is based on the TimeMixer model architecture. First, it uses the downsampling method to generate time series
at multiple scales. Secondly, through the PDMC (Past Decomposable Mixing with adaptive Conv) module designed by
us, we first use the convolution operation of the same convolution kernel on the sequences of different scales to achieve
adaptive information aggregation between different scales. Then, according to prior knowledge, the season and trend of
the input sequence are decomposed separately. Through our design, PDMC obtains information of different receptive
fields according to different input scales and decomposes the sequences of different scales into seasonal and trend
parts to achieve more detailed modeling. In the prediction stage, the output prediction layer aggregates the prediction
components of different scales to utilize the complementary prediction capabilities between multi-scale sequences to
achieve accurate prediction.
In general, our contributions are as follows:
1. Different from previous methods, we propose to use adaptive convolution modules to achieve information
aggregation of receptive fields of different scales based on sampling results of different scales. What’s more,
we use the transformation from time domain to frequency domain to solve the challenges brought by complex
information coupling in time series.
2. We proposed a relatively lightweight time series prediction model TimeCF and introduced the receptive field idea
in the CNN field to maximize the use of information aggregation at different scales to supplement global and
local information. And based on the ideas of FreDF and SAM, we achieved the decoupling of the autocorrelation
between the labels of the time series and the improvement of the model’s generalization ability.
3. TimeCF shows excellent performance in multiple time series forecasting tasks and datasets, while achieving a
relatively balanced state between model parameters and prediction accuracy.
2. Related Work
2.1. Mainstream Model Architecture
The core of the time series forecasting model is to have efficient and stable pattern extraction and modeling capabilities
in different time series, so as to model and predict complex time series. Traditional models such as ARIMA(Zhang
(2003)) and LSTM(Hochreiter and Schmidhuber (1997)) can accurately predict time series with simple cycles and trends,
but these models are limited by parameters and model structures so the prediction effect for nonlinear and dynamic time
series is often unsatisfactory. In recent years, deep learning methods have begun to make great strides in the direction
of time series forecasting. For the Transformer, researchers have proposed many methods to apply it to the field of time
series prediction: Autoformer(Wu, Xu, Wang and Long (2021)) proposed an autocorrelation mechanism to reduce the
Bin Wang et al.: Preprint submitted to Elsevier
Page 2 of 10
time complexity of the model to 𝑂(𝑛⋅𝑙𝑔(𝑛)). SAMformer(Ilbert, Odonnat, Feofanov, Virmaux, Paolo, Palpanas and
Redko (2024)) solved the instability problem during large model training by using Sharpness-Aware Minimization.
Informer(Zhou, Zhang, Peng, Zhang, Li, Xiong and Zhang (2021)) used ProbSpare self-attention and Self-attention
Distilling to enable it to effectively handle overly long input sequences. iTransformer(Liu, Hu, Zhang, Wu, Wang,
Ma and Long (2024)) inverted the time series and then used the Encoder for prediction. Mamba(Gu and Dao (2023))
combined the parallelization capability of Transformer and the historical information control capability of RNN, and
based on the idea of SSM, it was able to handle the correlation problem between variables at a lower cost. PatchTST(Nie,
Nguyen, Sinthong and Kalagnanam (2023)) regarded the time series as multiple independent time periods of channels,
and combined it with Transformer for prediction, achieving good results. And some researchers have found that the
use of CNN ideas can better construct the relationship between labels and time steps in time series: MICN(Wang,
Peng, Huang, Wang, Chen and Xiao (2023)) introduces the idea of image processing and captures information of
different receptive fields through convolution kernels of different sizes. TimesNet(Wu, Hu, Liu, Zhou, Wang and Long
(2023)) performs Fourier transform on the time series and selects its Top-k cycles, then expands each cycle into a
two-dimensional image and uses a 2D-kernel convolution kernel for feature extraction. ModernTCN(donghao and xue
(2024)) proposes to use large convolution kernels on the time dimension of the time series so that the model can capture
dependencies across time and variables at the same time. In addition, researchers have also proposed some models
that are not limited to Transformer and CNN: GRU(Chung, Gulcehre, Cho and Bengio (2014)) introduces a gating
mechanism that allows the model to dynamically adjust the ratio of memory and forgetting according to the current
input and previous state, making it more flexible and expressive than traditional RNN. DLinear(Zeng, Chen, Zhang and
Xu (2023)) decomposes time series into seasonal and trend components for separate predictions. FITS(Xu, Zeng and
Xu (2024)) roposes the use of basic MLP for prediction in the frequency domain based on Dlinear. And SparseTSF(Lin,
Lin, Wu, Chen and Yang (2024)) obtain information about adjacent time steps through convolution, and then predict
future results separately through sparse technology.
Considering the advantages and limitations of the above models, people need a time series forecasting model that
can extract different features and have accurate prediction results. Therefore, we proposed TimeCF, based on the original
idea of scale decomposition, to obtain features of different scales through convolution to achieve multi-scale adaptive
information aggregation.
2.2. Parameters Update
Nowadays researchers have begun to find that the effects that the models can achieve on the training set are often
not achieved on the test set. This is because when the model uses an optimizer to optimize the non-convex loss function
on the training set, it may enter a suboptimal or sharp minimum, resulting in insufficient generalization of the model. In
response to this situation, researchers have proposed a method called sharpness-aware minimization to update model
parameters to improve the generalization ability of deep neural networks: SAM(Foret et al. (2021)) proposed the
sharpness-aware minimization method, which first finds the point with the maximum loss in the neighborhood of the
current parameter and then uses gradient descent to update the parameters based on this maximum point, so that the
parameters can be moved to a flat area to reduce the sharpness of the loss function. WSAM(Yue, Jiang, Ye, Gao, Liu and
Zhang (2023)) introduces the concept of weights based on SAM, and adjusts the contribution of different parameters
to sharpness according to the importance of the parameters or other indicators, thereby more effectively regularizing.
FSAM(Li, Zhou, He, Cheng and Huang (2024)) effectively improves the generalization performance and robustness of
the model by improving adversarial perturbations and optimizing the full gradient estimation method.
Considering the generalization degree of the model, we propose a model parameter update module called SAMFre
based on the SAM idea to improve the overall generalization ability of the model.
3. TimeCF
3.1. OverView
The basic definition of time series forecasting is to input the historical data of a multivariate time series
𝑋𝑖𝑛𝑝𝑢𝑡∈𝑅𝑇×𝑁and after the model calculation, output the future multivariate output sequence 𝑋𝑜𝑢𝑡𝑝𝑢𝑡∈𝑅𝐹×𝑁,
where T represents the lookback length of the historical data defined by the model, F represents the future time length
to be predicted and N represents the number of labels in the time series.
In TimeCF, we use the idea of channel independence to make independent predictions for each label in the time
series. Therefore, the original input can be regarded as {𝑋𝑖𝑛𝑝𝑢𝑡1, 𝑋𝑖𝑛𝑝𝑢𝑡2, … , 𝑋𝑖𝑛𝑝𝑢𝑡𝑁
} , where 𝑋𝑖𝑛𝑝𝑢𝑡𝑖∈𝑅𝑇can be
Bin Wang et al.: Preprint submitted to Elsevier
Page 3 of 10
Sampling
Embed
Embed
Embed
Embed
Conv
Conv
Conv
Conv
Decomposition
Seasonal
Trend
FFN
+
real labels 
ℱ(∙)
ℱ(∙)
Mixing
Pred
Pred
Pred
Pred
Prediciton
L x
Input Series
(a) Input Preprocessing
(b) PDMC
(c) Output Predicting
SAMFre
Loss
Figure 1: TimeCF Architecture
regarded as the input instance of TimeCF. The overall structure of TimeCF is shown in Figure 1, which consists of
three components: Input Preprocessing layer, PDMC layer, and Output Predicting layer. At the same time, SAMFre as a
module to solve the autocorrelation between variables and improve the generalization ability of the model indirectly
participates in model training in the stages of calculating model loss and updating model parameters. In summary, the
overall process of TimeCF consists of three explicit modules and one implicit module.
3.2. Input Preprocessing layer
Since we treat the time series 𝑋𝑖𝑛𝑝𝑢𝑡𝑖∈𝑅𝑇in each label as a separate input instance, for each instance
𝑋𝑖𝑛𝑝𝑢𝑡𝑖,we first use the pooling layer to generate multi-level sequences of different scales {𝑋1, 𝑋2, … , 𝑋𝑘
}, where
𝑋𝑖∈𝑅
𝑇
𝑑𝑖−1 (𝑖∈{1, … 𝑘}). The output 𝑋𝑖is the result of 𝑖−1 times of downsampling of the original input 𝑋𝑖𝑛𝑝𝑢𝑡𝑖.
𝑋1is equal to the original input sequence 𝑋𝑖𝑛𝑝𝑢𝑡𝑖and 𝑑represents the length of the moving window in the pooling layer.
The specific multi-scale sequence generation formula is as follows:
𝑋𝑖= 𝑃𝑜𝑜𝑙(𝑃𝑎𝑑𝑑𝑖𝑛𝑔(𝑋(𝑖−1)
))
(1)
After generating the multi-scale sequences, each sequence will have a time-related mask 𝑋mask𝑖. Each sequence is
first normalized by the RevIn normalization layer, and then the mask and sequence are embedded by the Embedding
layer. The specific process is as follows:
𝑋𝑖= 𝑇𝑒𝑚𝑝𝑜𝑟𝑎𝑙𝐸𝑚𝑏𝑒𝑑𝑑𝑖𝑛𝑔(𝑋mask𝑖
) + 𝑇𝑜𝑘𝑒𝑛𝐸𝑚𝑏𝑒𝑑𝑑𝑖𝑛𝑔(𝑅𝑒𝑣𝐼𝑁(𝑋𝑖))
(2)
In formula (2), the sequence of each scale is 𝑋𝑖∈𝑅
𝑇
𝑑𝑖−1 ×𝐷, 𝐷is the output dimension of embedding. At this point,
the preprocessing part of the input data is completed, and this stage is only performed once during the model training
process.
3.3. Past Decomposable Mixing with adaptive Conv layer
Recent studies have found that most time series are the fusion of different components of different periods at most
scales. Therefore, we propose the PDMC module, which uses long-term and short-term changes to analyze various
periodic and non-periodic properties of the entire time series, while obtaining information of different receptive fields at
different scales through convolution. Specifically, in the PDMC, we first add global or local information to the sequence
through the idea of convolution and adaptation:
𝑋𝑖= 𝛼× 𝐶𝑜𝑛𝑣𝐵𝑙𝑜𝑐𝑘𝑠[𝑖]
(𝑋𝑇
𝑖
)𝑇+ 𝑋𝑖
(3)
The 𝑋𝑖is the output of the input preprocessing layer and the formula for 𝐶𝑜𝑛𝑣𝐵𝑙𝑜𝑐𝑘𝑠[𝑖] (𝑋) is as follow:
Bin Wang et al.: Preprint submitted to Elsevier
Page 4 of 10
𝐶𝑜𝑛𝑣𝐵𝑙𝑜𝑐𝑘𝑠[𝑖] (𝑋) = 𝐶𝑜𝑛𝑣(𝐺𝐸𝐿𝑈(𝐶𝑜𝑛𝑣(𝐺𝐸𝐿𝑈(𝐶𝑜𝑛𝑣(𝑁𝑜𝑟𝑚(𝑋))))))
(4)
Next, we will explain why using the same size of convolution can obtain information of different receptive fields. First,
the lookback window length selected by this model is 96, which is consistent with the mainstream model, and the number
of downsampling is set to 3. So the input of PDMC is {𝑋1 ∈𝑅96×𝐷, 𝑋2 ∈𝑅48×𝐷, 𝑋3 ∈𝑅24×𝐷, 𝑋4 ∈𝑅12×𝐷}
, where
96,48,24,12 are the time windows after downsampling. And in 𝐶𝑜𝑛𝑣𝐵𝑙𝑜𝑐𝑘𝑠[𝑖] (𝑋),we use three layers of convolution
and the convolution kernel size of each layer is 3, and the padding is 1. This means that after three convolutions, each
time point in {𝑋1, 𝑋2, 𝑋3, 𝑋4
}
contains information from at least 2 + 2 + 2, or 6 neighboring time points. From the
perspective of PDMC stacking, the number of PDMC stackings is 𝐿(𝐿≥2). So for 𝑋4, the window of length 6 × 𝐿
will eventually cover the entire sequence length, which can be considered as obtaining global information. But for
𝑋1,𝑋2 and 𝑋3,the window of length 6 × 𝐿only occupies a part of the sequence length, which can be considered as
obtaining local information of different proportions. In summary, by using convolution blocks and PDMC stacking,
TimeCF can obtain information of different receptive fields at different scales.
Then, we decompose the sequence of each scale into season and trend parts:
𝑆𝑒𝑎𝑠𝑜𝑛𝑖, 𝑇𝑟𝑒𝑛𝑑𝑖= 𝐷𝑒𝑐𝑜𝑚𝑝(𝑋𝑖
)
(5)
𝑆𝑒𝑎𝑠𝑜𝑛𝑖,𝑇𝑟𝑒𝑛𝑑𝑖refer to the season and trend parts decomposed from the i-th scale respectively. We put all the
season and trend components into the lists 𝑆𝑒𝑎𝑠𝑜𝑛and 𝑇𝑟𝑒𝑛𝑑respectively, and based on the idea of TimeMixer, we
perform scale fusion on the season and trend respectively:
𝑆𝑒𝑎𝑠𝑜𝑛, 𝑇𝑟𝑒𝑛𝑑= 𝑆𝑒𝑎𝑠𝑜𝑛𝑀𝑖𝑥(𝑆𝑒𝑎𝑠𝑜𝑛) , 𝑇𝑟𝑒𝑛𝑑𝑀𝑖𝑥(𝑇𝑟𝑒𝑛𝑑)
(6)
The fusion of the season term is a bottom-up sequence fusion and the trend term is a top-down sequence fusion
which make full use of the information inherent in both parts. Finally, PDMC passes the season part, trend part and
original sequence through the feed forward network to achieve the fusion between different components:
𝑋𝑖= 𝑋𝑖+ 𝐹𝐹𝑁(𝑆𝑒𝑎𝑠𝑜𝑛𝑖+ 𝑇𝑟𝑒𝑛𝑑𝑖
)
(7)
So far, the PDMC block has finally realized the core tasks of feature extraction and multi-scale mixing process
through the adaptive information aggregation by convolution, the decomposition and mixing of the season term and
trend term.
3.4. Output Predicting layer
In the prediction output stage, the output of PDMC we obtain is {𝑋1, 𝑋2, … , 𝑋𝑘
}
, where 𝑋𝑖∈𝑅
𝑇
𝑑𝑖−1 ×𝐷(𝑖∈{1, … 𝑘}).
So if we need to make a prediction for 𝑋𝑖in the time dimension, we need to change the dimension of 𝑋𝑖at least twice.
Specifically, first align the time dimension of 𝑋𝑖with the predicted future length according to different scales. Then
adjust the dimension of the sequence so that the model vector dimension D can be reduced back to the initial value:
𝑋𝑖= 𝐿𝑖𝑛𝑒𝑎𝑟2
(
𝐿𝑖𝑛𝑒𝑎𝑟1
(𝑋𝑇
𝑖
)𝑇)
(8)
The input dimension of the 𝐿𝑖𝑛𝑒𝑎𝑟1 is
𝑇
𝑑𝑖−1, and the output dimension is the prediction length𝐹. As a result, time
series of different scales generate predictions of corresponding time lengths. Then, the input dimension of the 𝐿𝑖𝑛𝑒𝑎𝑟2
is 𝐷and the output dimension 1. This is to make the sequence dimension match the target output dimension, or let
𝑋𝑖∈𝑅𝐹
It is not difficult to see that each scale sequence eventually generates a prediction sequence. Then we sum all the
prediction sequences and use the RevIN layer of the preprocessing layer to perform inverse normalization:
𝑋𝑂= 𝑖𝑅𝑒𝑣𝐼𝑁
(∑
𝑋𝑖
)
(9)
At this point, the prediction of a single label is completed, and the sequences of different scales are finally fused
together through the stack() function to forecast the result.
Bin Wang et al.: Preprint submitted to Elsevier
Page 5 of 10
3.5. Sharpness-Aware Minimization Frequency Domain Loss
The loss function of traditional time series forecasting model is usually MSE loss, which has shown its superiority
in the training process of a large number of time series forecasting models. However, with the introduction of the idea of
channel independence, FreDF’s researchers have noticed that the MSE loss hardly takes into account the autocorrelation
between different labels of the time series in the model using the channel independence method. Therefore, it is not the
best choice to calculate the loss by MSE in the training process of the time series forecasting model using the channel
independence method. However, according to the idea of Fourier transform, if different labels are projected into the
frequency domain, unrelated feature can be obtained in the frequency domain so that the model based on the idea can
obtain better results than the traditional MSE loss when calculating the loss. At the same time, we noticed that the
overall generalization performance of the model can be improved by adjusting the sharpness of the loss through the
SAM method. Based on these two ideas, the TimeCF we proposed introduces the SAMFre module to decouple the
autocorrelation between different labels in the time series and improve the generalization ability. Specifically, SAMFre
projects the model’s prediction results and the actual label values into the frequency domain through Fourier transform,
then calculates the loss using the L1 norm, and finally adds it to the original MSE loss to get the complete loss:
𝑙𝑜𝑠𝑠= 𝛼× |𝐹𝐹𝑇(𝑝𝑟𝑒𝑑) −𝐹𝐹𝑇(𝑟𝑒𝑎𝑙)|1 + (1 −𝛼) × 𝑀𝑆𝐸
(10)
After calculating the loss, the model uses basic optimization methods to optimize the model parameters before
the number of updates reaches the set threshold. When the number of updates reaches the threshold, the model uses
the SAM method to calculate the point with the largest loss in the neighborhood of the current parameter, and then
performs gradient backpropagation based on this point to achieve parameter update:
̂𝜖(𝑤) = 𝜌
∇𝑤𝐿𝑜𝑠𝑠
‖∇𝑤𝐿𝑜𝑠𝑠‖2
(11)
𝑔= ∇𝑤𝐿𝑜𝑠𝑠||𝑤+ ̂𝜖(𝑤)
(12)
𝑤= 𝑤−𝜂⋅𝑔
(13)
So far, we have optimized the model parameter update part through SAMFre, so that the model can better deal with
the autocorrelation problem between labels in different sequences and improve the generalization ability of the model.
4. Results
4.1. Experiment setting
Experimental datasets: In order to verify the prediction accuracy of our model on time series generated in real
environments, we selected six commonly used real-world datasets: Weather, ETTh1, ETTh2, ETTm1, ETTm2 and
Electricity(Zhou et al. (2021); Wu et al. (2021)) and conducted sufficient experiments on these six datasets to verify the
ability of our model in long-term forecasting.
Benchmark models: Based on timeliness, innovation and prediction effect, we selected 8 time series forecasting mod-
els which are widely acclaimed in the field of time series forecasting as our baselines, including: (1) TimeKAN(Huang
et al. (2025)) (2) TimeMixer (Wang et al. (2024)) (3) iTransformer(Liu et al. (2024)) (4) SparseTSF(Lin et al. (2024))
(5) FreTS(Yi, Zhang, Fan, Wang, Wang, He, An, Lian, Cao and Niu (2023)) (6) PatchTST(Nie et al. (2023)) (7)
TimesNet(Wu et al. (2023)) (8) DLinear(Zeng et al. (2023))
Experimental environment and related indicators: All experiments were implemented based on PyTorch and
conducted on a single NVIDIA 3090 24GB GPU. At the same time, in order to ensure fair competition among the
models, we set the lookback window, prediction length, and evaluation index to 96, 96, 192, 336, 720, mean square
error (MSE), and mean absolute error (MAE) respectively. WhatâĂŹs more, the benchmark model is tested using the
scripts provided in the original code, while the test of the TimeCF model we proposed sets different training rounds and
early stopping thresholds according to the size of different data sets to improve test efficiency.
Bin Wang et al.: Preprint submitted to Elsevier
Page 6 of 10
Table 1
Performance comparison of different time series forecasting models on benchmark datasets.
Models
TimeCF
TimeKAN
TimeMixer iTransformer SparseTSF
FreTS
PatchTST
TimesNet
Dlinear
Ours
2025
2024
2024
2024
2024
2023
2023
2023
Metric
MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE MSE MAE
ETT h1
96 0.359 0.391 0.367 0.394 0.381 0.398 0.394 0.409 0.385 0.391 0.395 0.407 0.376 0.397 0.389 0.411 0.396 0.410
192 0.401 0.419 0.414 0.419 0.441 0.430 0.448 0.441 0.434 0.420 0.490 0.477 0.426 0.432 0.439 0.441 0.445 0.440
336 0.440 0.436 0.445 0.434 0.500 0.459 0.492 0.465 0.476 0.439 0.510 0.480 0.469 0.457 0.493 0.470 0.487 0.465
720 0.466 0.462 0.451 0.463 0.552 0.507 0.521 0.504 0.461 0.454 0.568 0.538 0.518 0.504 0.516 0.494 0.512 0.510
avg 0.417 0.427 0.419 0.428 0.468 0.449 0.464 0.455 0.439 0.426 0.490 0.475 0.447 0.447 0.459 0.454 0.460 0.456
ETT h2
96 0.282 0.333 0.291 0.340 0.286 0.339 0.300 0.349 0.302 0.346 0.332 0.387 0.308 0.359 0.337 0.370 0.341 0.395
192 0.372 0.389 0.374 0.391 0.391 0.404 0.381 0.399 0.384 0.395 0.451 0.457 0.380 0.406 0.404 0.414 0.481 0.479
336 0.410 0.422 0.423 0.434 0.421 0.432 0.423 0.432 0.421 0.427 0.466 0.473 0.412 0.429 0.455 0.452 0.592 0.542
720 0.416 0.436 0.462 0.461 0.468 0.468 0.426 0.445 0.420 0.437 0.485 0.471 0.435 0.456 0.434 0.448 0.840 0.661
avg 0.370 0.395 0.387 0.406 0.391 0.411 0.383 0.406 0.382 0.401 0.433 0.447 0.384 0.412 0.407 0.421 0.564 0.519
ETT m1
96 0.307 0.345 0.321 0.361 0.327 0.364 0.341 0.376 0.356 0.375 0.337 0.374 0.323 0.364 0.333 0.375 0.345 0.373
192 0.353 0.372 0.356 0.382 0.367 0.386 0.380 0.394 0.394 0.392 0.382 0.398 0.371 0.391 0.407 0.413 0.381 0.391
336 0.377 0.395 0.381 0.400 0.393 0.403 0.419 0.418 0.425 0.413 0.420 0.423 0.398 0.408 0.413 0.421 0.415 0.415
720 0.441 0.430 0.451 0.437 0.451 0.442 0.486 0.455 0.487 0.448 0.490 0.471 0.457 0.444 0.503 0.467 0.472 0.450
avg 0.370 0.386 0.377 0.395 0.384 0.399 0.406 0.411 0.415 0.407 0.407 0.416 0.387 0.402 0.414 0.419 0.403 0.407
ETT m2
96 0.169 0.252 0.175 0.257 0.174 0.257 0.183 0.266 0.184 0.267 0.186 0.275 0.184 0.267 0.189 0.266 0.193 0.292
192 0.238 0.299 0.239 0.299 0.236 0.299 0.252 0.312 0.248 0.305 0.259 0.323 0.246 0.304 0.252 0.307 0.284 0.361
336 0.296 0.335 0.301 0.340 0.301 0.339 0.314 0.351 0.307 0.342 0.349 0.386 0.311 0.348 0.321 0.349 0.384 0.429
720 0.400 0.393 0.398 0.398 0.400 0.400 0.411 0.406 0.407 0.398 0.559 0.511 0.418 0.414 0.418 0.404 0.556 0.523
avg 0.276 0.320 0.278 0.323 0.278 0.324 0.290 0.334 0.287 0.328 0.338 0.373 0.290 0.333 0.295 0.331 0.354 0.401
Weather
96 0.162 0.204 0.162 0.208 0.161 0.208 0.175 0.215 0.197 0.236 0.171 0.227 0.175 0.217 0.168 0.219 0.196 0.256
192 0.209 0.249 0.207 0.249 0.207 0.251 0.225 0.257 0.243 0.273 0.218 0.280 0.220 0.255 0.225 0.265 0.238 0.299
336 0.266 0.293 0.263 0.290 0.264 0.293 0.279 0.298 0.292 0.308 0.265 0.317 0.279 0.297 0.281 0.303 0.281 0.330
720 0.345 0.343 0.338 0.340 0.345 0.345 0.361 0.350 0.368 0.357 0.326 0.351 0.356 0.348 0.359 0.354 0.345 0.381
avg 0.246 0.272 0.242 0.271 0.244 0.274 0.260 0.280 0.275 0.293 0.245 0.293 0.257 0.279 0.258 0.285 0.265 0.316
ECL
96 0.153 0.245 0.174 0.266 0.156 0.247 0.148 0.240 0.209 0.280 0.171 0.260 0.180 0.272 0.168 0.271 0.210 0.301
192 0.166 0.256 0.182 0.272 0.170 0.260 0.164 0.256 0.205 0.281 0.177 0.268 0.187 0.279 0.187 0.289 0.210 0.304
336 0.183 0.274 0.196 0.286 0.187 0.278 0.177 0.270 0.218 0.295 0.190 0.284 0.204 0.295 0.201 0.302 0.223 0.319
720 0.221 0.305 0.236 0.320 0.227 0.312 0.228 0.313 0.260 0.327 0.228 0.316 0.245 0.328 0.229 0.324 0.257 0.349
avg 0.181 0.270 0.197 0.286 0.185 0.274 0.179 0.269 0.223 0.296 0.191 0.282 0.204 0.294 0.196 0.297 0.225 0.318
Total AVG
0.310 0.345 0.317 0.352 0.325 0.355 0.330 0.359 0.337 0.359 0.351 0.381 0.328 0.361 0.338 0.368 0.379 0.403
1st Times
19
21
5
4
2
0
4
4
0
2
1
0
0
0
0
0
0
0
4.2. Experiment results
All results in this experiment are obtained after local experiments(except for FreTS whose results are obtained
from the original paper) and all results are shown in Table 1. We define that the lower the values of MSE and MAE,
the better the model prediction effect. At the same time, the best results are shown in bold red and the second best
results are shown in bold black. It is not difficult to see from Table 1 that the TimeCF we proposed has shown good
performance on most datasets, except for weather and ECL, where KAN and Transformer model can better handle the
autocorrelation dependencies for high-dimensional datasets. Even if it does not achieve the optimal prediction effect in
some datasets, the prediction accuracy of TimeCF is not much different from the results achieved by the optimal model.
The average values of MSE and MAE increased by 2.2% and 1.9% compared with the suboptimal model. And if we
look at the number of times the optimal prediction is obtained, TimeCF is far ahead of all models that appeared in the
experiments. This proves that TimeCF has accurate and general prediction capabilities on most natural time series.
4.3. Ablation experiment
To demonstrate the accuracy of our design and addition of modules, we used three forms of TimeCF models in
the ablation implementation to compare with our selected baseline model TimeMixer: (1) TimeCF with the SAMFre
module omitted (2) TimeCF with the convolution part omitted and (3) the complete TimeCF. As shown in Table 2,
TimeCF without complete modules has a certain improvement over the baseline model in the experiment, but the
Bin Wang et al.: Preprint submitted to Elsevier
Page 7 of 10
Table 2
Ablation study of TimeCF.
Model
ETT h1
ETT h2
ECL
MSE
MAE
MSE
MAE
MSE
MAE
TimeMixer
0.469
0.449
0.392
0.411
0.185
0.274
TimeCF w/o SAMFre
0.466
0.452
0.392
0.417
0.182
0.273
TimeCF w/o CONV
0.430
0.425
0.372
0.396
0.185
0.272
TimeCF (ours)
0.417 0.427 0.371 0.396 0.181 0.270
Table 3
Parameter comparison of different time series forecasting models on various datasets.
Model
Parameters (Number)
ETT h1 ETT h2 ETT m1 ETT m2 Weather
ECL
TimeMixer
75.3K
75.3K
75.3K
77.5K
104K
104K
iTransformer
224K
224K
224K
224K
4.83M
4.83M
TimesNet
605K
1.19M
4.70M
1.19M
1.19M
150M
SparseTSF
0.041K
0.041K
0.581K
0.581K
0.581K
0.041K
TimeCF (ours)
125K
125K
125K
275K
179K
179K
improvement is not significant. This shows that both the decoupling of label autocorrelation in time series and the
enhancement of generalization ability based on SAMFre and the adaptive information aggregation between different
scales based on convolution can only enhance the partial information extraction and prediction capabilities of the
baseline model TimeMixer to a certain extent. However, the good performance of the complete TimeCF shows that
the information of different scales and receptive fields obtained by convolution may contain some information with
autocorrelation. And by using SAMFre, the autocorrelation within this part of information can be properly decoupled,
which is reflected in the results that it exceeds the baseline model in terms of evaluation indicators. Finally, it is proved
that the adaptive information aggregation module based on convolution and the SAMFre module proposed by us are
both indispensable parts of the TimeCF model.
4.4. Model efficiency
In order to verify the efficiency of the TimeCF model we proposed, we set the lookback window and the prediction
length to 96 and 96 to test the parameter size of the model. We selected three benchmark models based on the Transformer
architecture, the CNN architecture and the MLP model, and a model with the smallest number of parameters as the
baseline model for model efficiency. It is not difficult to see from Table 3 that the Transformer and CNN-based models are
limited by the model structure, and their parameter volume is maintained at a very high level on all datasets. The model
parameters of the MLP-based model TimeMixer and the TimeCF we proposed are basically maintained at a relatively
low level on each dataset, and the fluctuation range is not large. Although the number of parameters of SparseTSF is
much smaller than that of the TimeCF we proposed and TimeMixer, considering the balance between prediction effect
and parameter volume, we believe that the TimeCF we proposed has stable and efficient model operation efficiency
while ensuring the accuracy of the prediction results under different datasets. Therefore, it can be considered that the
TimeCF we proposed can achieve excellent prediction performance with only a relatively small amount of computing
resources.
5. Conclusion
In our paper, we proposed a time series prediction model TimeCF based on the TimeMixer decomposition-learning-
mixing architecture to achieve high-precision time series forecasting. With the support of PDMC, TimeCF can utilize the
information of different receptive fields of sequences of different scales, learn and mix the seasonal and trend sequences
separately and finally combine SAMFre to decouple the autocorrelation between labels and reduce the sharpness of
the loss function. The performance of our model on real datasets also proves that TimeCF can cope with time series
prediction tasks in the real world with good prediction performance.
Bin Wang et al.: Preprint submitted to Elsevier
Page 8 of 10
References
Afan, H.A., Mohtar, W.H.M.W., Khaleel, F., Kamel, A.H., Mansoor, S.S., Alsultani, R., Ahmed, A.N., Sherif, M., El-Shafie, A., 2024. Data-driven
water quality prediction for wastewater treatment plants. Heliyon 10. Publisher: Elsevier.
Alkhayat, G., Mehmood, R., 2021. A review and taxonomy of wind and solar energy forecasting methods based on deep learning. Energy and AI 4,
100060. Publisher: Elsevier.
Bi, K., Xie, L., Zhang, H., Chen, X., Gu, X., Tian, Q., 2023. Accurate medium-range global weather forecasting with 3D neural networks. Nature
619, 533–538. Publisher: Nature Publishing Group.
Challu, C., Olivares, K.G., Oreshkin, B.N., RamÃŋrez, F.G., Canseco, M.M., Dubrawski, A., 2023. NHITS: Neural Hierarchical Interpolation for
Time Series Forecasting, in: AAAI, pp. 6989–6997. URL: https://doi.org/10.1609/aaai.v37i6.25854.
Chung, J., Gulcehre, C., Cho, K., Bengio, Y., 2014. Empirical evaluation of gated recurrent neural networks on sequence modeling, in: NIPS 2014
Workshop on Deep Learning, December 2014.
donghao, L., xue, w., 2024. ModernTCN: A Modern Pure Convolution Structure for General Time Series Analysis, in: The Twelfth International
Conference on Learning Representations. URL: https://openreview.net/forum?id=vpJMJerXHU.
Farhi, N., Kohen, E., Mamane, H., Shavitt, Y., 2021. Prediction of wastewater treatment quality using LSTM neural network. Environmental
Technology & Innovation 23, 101632. Publisher: Elsevier.
Foret, P., Kleiner, A., Mobahi, H., Neyshabur, B., 2021. Sharpness-aware Minimization for Efficiently Improving Generalization, in: International
Conference on Learning Representations. URL: https://openreview.net/forum?id=6Tm1mposlrM.
Gu, A., Dao, T., 2023. Mamba: Linear-time sequence modeling with selective state spaces. arXiv preprint arXiv:2312.00752 .
Hochreiter, S., Schmidhuber, J., 1997. Long short-term memory. Neural computation 9, 1735–1780. Publisher: MIT press.
Huang, S., Zhao, Z., Li, C., Bai, L., 2025. TimeKAN: KAN-based Frequency Decomposition Learning Architecture for Long-term Time Series
Forecasting. arXiv preprint arXiv:2502.06910 .
Huang, X., Zhang, B., Feng, S., Ye, Y., Li, X., 2023. Interpretable local flow attention for multi-step traffic flow prediction. Neural networks 161,
25–38. Publisher: Elsevier.
Huo, G., Zhang, Y., Wang, B., Gao, J., Hu, Y., Yin, B., 2023. Hierarchical spatioâĂŞtemporal graph convolutional networks and transformer network
for traffic flow forecasting. IEEE Transactions on Intelligent Transportation Systems 24, 3855–3867. Publisher: IEEE.
Ilbert, R., Odonnat, A., Feofanov, V., Virmaux, A., Paolo, G., Palpanas, T., Redko, I., 2024. SAMformer: Unlocking the Potential of Transformers
in Time Series Forecasting with Sharpness-Aware Minimization and Channel-Wise Attention, in: ICML. URL: https://openreview.net/
forum?id=8kLzL5QBh2.
Li, L., Jian, C., Wan, F., Geng, D., Fang, Z., Chen, L., Gao, Y., Jiang, W., Zhu, J., 2024. LagCNN: A Fast yet Effective Model for Multivariate
Long-term Time Series Forecasting, in: CIKM, pp. 1235–1244. URL: https://doi.org/10.1145/3627673.3679672.
Li, T., Zhou, P., He, Z., Cheng, X., Huang, X., 2024. Friendly Sharpness-Aware Minimization, in: Proceedings of the IEEE/CVF Conference on
Computer Vision and Pattern Recognition (CVPR), pp. 5631–5640.
Liang, X., Yang, E., Deng, C., Yang, Y., 2024. CrossFormer: Cross-Modal Representation Learning via Heterogeneous Graph Transformer. ACM
Trans. Multim. Comput. Commun. Appl. 20, 380:1–380:21. URL: https://doi.org/10.1145/3688801.
Lin, S., Lin, W., Wu, W., Chen, H., Yang, J., 2024. SparseTSF: Modeling Long-term Time Series Forecasting with *1k* Parameters, in: Forty-first
International Conference on Machine Learning. URL: https://openreview.net/forum?id=54NSHO0lFe.
Liu, Y., Hu, T., Zhang, H., Wu, H., Wang, S., Ma, L., Long, M., 2024. iTransformer: Inverted Transformers Are Effective for Time Series Forecasting,
in: The Twelfth International Conference on Learning Representations. URL: https://openreview.net/forum?id=JePfAI8fah.
Nie, Y., Nguyen, N.H., Sinthong, P., Kalagnanam, J., 2023. A Time Series is Worth 64 Words: Long-term Forecasting with Transformers, in: The
Eleventh International Conference on Learning Representations. URL: https://openreview.net/forum?id=Jbdc0vTOcol.
Salinas, D., Flunkert, V., Gasthaus, J., Januschowski, T., 2020. DeepAR: Probabilistic forecasting with autoregressive recurrent networks. International
journal of forecasting 36, 1181–1191. Publisher: Elsevier.
Sonkavde, G., Dharrao, D.S., Bongale, A.M., Deokate, S.T., Doreswamy, D., Bhat, S.K., 2023. Forecasting stock market prices using machine
learning and deep learning models: A systematic review, performance analysis and discussion of implications. International Journal of Financial
Studies 11, 94. Publisher: MDPI.
Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A.N., Kaiser, Å., Polosukhin, I., 2017. Attention is all you need. Advances in
neural information processing systems 30.
Wang, H., Pan, L., Chen, Z., Yang, D., Zhang, S., Yang, Y., Liu, X., Li, H., Tao, D., 2024. Fredf: Learning to forecast in frequency domain. arXiv
preprint arXiv:2402.02399 .
Wang, H., Peng, J., Huang, F., Wang, J., Chen, J., Xiao, Y., 2023. MICN: Multi-scale Local and Global Context Modeling for Long-term
Series Forecasting, in: The Eleventh International Conference on Learning Representations. URL: https://openreview.net/forum?id=
zt53IDUR1U.
Wang, S., Wu, H., Shi, X., Hu, T., Luo, H., Ma, L., Zhang, J.Y., Zhou, J., 2024. TimeMixer: Decomposable Multiscale Mixing for Time Series
Forecasting, in: ICLR. URL: https://openreview.net/forum?id=7oLshfEIC2.
Wu, H., Hu, T., Liu, Y., Zhou, H., Wang, J., Long, M., 2023. TimesNet: Temporal 2D-Variation Modeling for General Time Series Analysis, in: The
Eleventh International Conference on Learning Representations. URL: https://openreview.net/forum?id=ju_Uqw384Oq.
Wu, H., Xu, J., Wang, J., Long, M., 2021. Autoformer: Decomposition Transformers with Auto-Correlation for Long-Term Series Forecasting,
in: Beygelzimer, A., Dauphin, Y., Liang, P., Vaughan, J.W. (Eds.), Advances in Neural Information Processing Systems.
URL: https:
//openreview.net/forum?id=I55UqU-M11y.
Xu, Z., Zeng, A., Xu, Q., 2024. FITS: Modeling Time Series with \10k\ Parameters, in: The Twelfth International Conference on Learning
Representations. URL: https://openreview.net/forum?id=bWcnvZ3qMb.
Yi, K., Zhang, Q., Fan, W., Wang, S., Wang, P., He, H., An, N., Lian, D., Cao, L., Niu, Z., 2023. Frequency-domain mlps are more effective learners
in time series forecasting. Advances in Neural Information Processing Systems 36, 76656–76679.
Bin Wang et al.: Preprint submitted to Elsevier
Page 9 of 10
Yin, L., Cao, X., Liu, D., 2023. Weighted fully-connected regression networks for one-day-ahead hourly photovoltaic power forecasting. Applied
Energy 332, 120527. Publisher: Elsevier.
Yue, Y., Jiang, J., Ye, Z., Gao, N., Liu, Y., Zhang, K., 2023. Sharpness-Aware Minimization Revisited: Weighted Sharpness as a Regularization
Term, in: KDD, pp. 3185–3194. URL: https://doi.org/10.1145/3580305.3599501.
Zeng, A., Chen, M., Zhang, L., Xu, Q., 2023. Are transformers effective for time series forecasting?, in: Proceedings of the AAAI conference on
artificial intelligence, pp. 11121–11128. Issue: 9.
Zhang, G.P., 2003. Time series forecasting using a hybrid ARIMA and neural network model. Neurocomputing 50, 159–175. Publisher: Elsevier.
Zhou, H., Zhang, S., Peng, J., Zhang, S., Li, J., Xiong, H., Zhang, W., 2021. Informer: Beyond efficient transformer for long sequence time-series
forecasting, in: Proceedings of the AAAI conference on artificial intelligence, pp. 11106–11115. Issue: 12.
Bin Wang et al.: Preprint submitted to Elsevier
Page 10 of 10
