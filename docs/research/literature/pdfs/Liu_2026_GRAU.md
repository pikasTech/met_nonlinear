# GRAU: Generic Reconfigurable Activation Unit Design for Neural Network Hardware Accelerators
**Author**: Yuhao Liu; Salim Ullah; Akash Kumar
**Creator**: arXiv GenPDF (tex2pdf:57610bf)

---

GRAU: Generic Reconfigurable Activation Unit

Design for Neural Network Hardware Accelerators

Yuhao Liu1,2,3

, Student Member, IEEE, Salim Ullah1

, Akash Kumar1

, Senior Member, IEEE

1Ruhr University Bochum, Germany 2Dresden University of Technology, Germany

3Center for Scalable Data Analytics and Artificial Intelligence (ScaDS.AI Dresden/Leipzig), Germany

Email: {yuhao.liu, salim.ullah, akash.kumar}@rub.de

Abstract—With the continuous growth of neural network

scales, low-precision quantization is widely used in edge ac
celerators. Classic multi-threshold activation hardware requires

2n thresholds for n-bit outputs, causing a rapid increase in

hardware cost as precision increases. We propose a reconfigurable

activation hardware, GRAU, based on piecewise linear fitting,

where the segment slopes are approximated by powers of two.

Our design requires only basic comparators and 1-bit right

shifters, supporting mixed-precision quantization and nonlinear

functions such as SiLU. Compared with multi-threshold activators,

GRAU reduces LUT consumption by over 90%, achieving higher

hardware efficiency, flexibility, and scalability.

I. INTRODUCTION

Continuously growing sizes of state-of-the-art neural net
work models encourage researchers to explore different

schemes to accelerate the network inference and improve

the power efficiency by reducing memory consumption and

computing power requirements. Therefore, quantization be
comes one of the most widely applied methods in related

works, especially by training the weights and activations in

the network model as low-precision integers. Considering that

the outputs of each neuron or kernel in Quantized Neural

Networks (QNNs) should be the quantized integers following

the selected precision, one re-quantization unit should be

implemented after the activation unit to convert the outputs

of the activation function to integers in the design of a QNN

hardware accelerator.

A. Motivation

Considering the nonlinear activation function and re
quantization computation are expensive on hardware implemen
tation, previous works have extensively explored the designs

of quantized activation hardware for QNN accelerators. One

of the widely used design paradigms is the Multi-Threshold

(MT) activation unit, adopted in well-known designs such

as FINN [1] and FINN-R [2]. By folding Batch Normaliza
tion, nonlinear activation, and re-quantization into a single

comparator-based block, MT units replace expensive arithmetic

operations with a set of fixed thresholds. However, this design

paradigm faces three major limitations as QNNs evolve:

1) Exponential hardware scaling with precision: MT unit

takes the integer outputs from Multiply-Accumulators (MAC)

and compares them with 2n −1 thresholds to produce n-bit

TABLE I: Comparison between Unified-Precision and Mixed
Precision QNN on MNIST [3]

MLP

CNN

Full 1-bit

Mixed (baseline)

Full 8-bit

Full 1-bit

Mixed (baseline)

Full 8-bit

Accuracy/%

92.29

95.91

97.36

96.26

98.79

99.14

Loss/%

-3.62

0.00

1.45

-2.53

0.00

0.35

Memory/Bytes

7,376

9,984

59,008

29,848

55,712

238,784

Baseline Ratio

0.74

1.00

5.91

0.54

1.00

4.29

1

2

3

−6

−4

−2

2

4

6

0.2

0.4

0.6

0.8

1

x

σ(x)

1

3?

2?

−10

−5

5

10

15

0.2

0.4

0.6

0.8

1

x

G(0.25x −0.5)

Fig. 1: Correct 2-bit quantization of Multi-Threshold unit (left)

in Sigmoid and the mistake of Multi-Threshold unit in non
monotonically increasing function (right)

outputs, such as 15 thresholds for 4-bit and 255 for 8-bit. If

the MAC result exceeds m thresholds, the quantized activation

output is an integer, m. This design paradigm suggests

exponentially increasing hardware resource consumption, since

following an increase in output precision, the number of

thresholds grows exponentially.

2) Inefficiency in mixed-precision quantization: Mixed
precision quantization has recently emerged as a key trend in

the design of lightweight AI on the edge. For instance, Liu et

al. [3] compared unified-precision and mixed-precision QNNs

using a small 4-layer MLP and CNN on MNIST [4]. Their

results in Table I indicate that 1/2/4/8-bit mixed precision offers

a trade-off between accuracy and memory usage compared to

BNN and QNN, tolerating a slight accuracy loss to significantly

reduce memory cost compared to QNN. However, the MT

unit must implement the maximum number of thresholds

required by the highest precision. For instance, in 1/2/4/8
bit mixed-precision quantization, the MT unit must implement

255 thresholds for the 8-bit precision, while only a small

subset is used for lower precisions (for example, only one

threshold is used for 1-bit). Serial reuse of a comparator can

reduce hardware costs but significantly increases latency at

higher precisions.

arXiv:2602.22352v1  [cs.AR]  25 Feb 2026


!!! page 2 "Liu_2026_GRAU"

3) Inability to represent non-monotonic activations: Since

MT outputs always increase as more thresholds are exceeded

by inputs, the design inherently supports only monotonically

increasing functions. Emerging nonlinear activations, such

as SiLU [5], violate this constraint, making the MT unit

incompatible with many practical QNN settings. The left plot

in Figure 1 instantiates a correct quantization processing of

a Sigmoid function with three thresholds for 2-bit output.

However, the right plot shows an incompatible case of MT

units where the expected output, 3, at the threshold of 0.9,

is larger than the expected output, 2, at 6.0, violating the

monotonically increasing condition. The quantized output at

6.0 should be 3 since it exceeds three thresholds, and the

output at 0.9 should be 2 instead.

B. Related Works

Although the MT unit has been successfully adopted in

various well-known works, considering the above-discussed

shortcomings, we further surveyed other potential solutions

introduced in prior works, such as Piecewise Linearized Fitting

(PWLF), Second-Order Polynomial Fitting (SOPF), and Look
up Table (LUT):

• Compared to the Multi-Threshold activation method, the

LUT-based quantized activation unit is also hardware
friendly, as shown in the works of Piazza et al. [6], Pogiri

et al. [7], and Kumar Meher et al. [8]. However, it shares

the same shortcomings as the exponential growth of LUT

storage with increased output precision and larger fan-in

bit-width from the MAC output. Furthermore, for mixed

precision, the LUT-based scheme requires storing different

samples for each precision, which is hardware inefficient.

• PWLF and SOPF are more flexible than MT units to fit

various nonlinear functions, such as Zhang et al. [9], Li

et al. [10], Tsmots et al. [11], and Nguyen et al. [12]

explored the PWLF-based hardware design of Sigmoid

activation functions. Liu et al.[13] and Bouguezzi et

al. [14] presented the PWLF-based implementation for

Tanh and TanhExp. Tsmots et al. and Bouguezzi et

al. applied the SOPF-scheme for Sigmoid and Tanh

approximation on hardware. However, these schemes

are not hardware-friendly compared to the MT and

LUT schemes, since they need more complex arithmetic

operations on hardware.

Furthermore, there are some other shortcomings across these

four quantized activation design paradigms: Previous works

based on PWLF and SOPF mainly focus on designing a specific

activation unit for a given activation function, without the

support of reconfiguring the hardware to other functions at

runtime. In addition, Multi-Threshold and LUT activation units

require reconfiguring a massive number of threshold values or

look-up table data.

C. Contribution

As summarized in Table II, comparing the four activation

hardware design paradigms discussed above, we noticed that

TABLE II: Comparison between SOPF, PWLF, MT, LUT, and

GRAU for Quantized Activation Unit

Features

Hardware

Runtime

Non-monotonically

Adaptive for

Friendly

Reconfigurable

Increasing Function

Mixed-Precision

SOPF

Low

No

Yes

Yes

PWLF

Low

No

Yes

Yes

MT

High

Yes

No

No

LUT

High

Limited

Yes

No

GRAU

High

Yes

Yes

Yes

current activation hardware lacks a unified, hardware-efficient,

and reconfigurable design that can simultaneously support

multi-function, mixed-precision, and non-monotonic activa
tions. Therefore, we propose a novel Generic Reconfigurable

Activation Unit (GRAU) for low-precision quantized, integer
based QNN hardware accelerator designs with flexible support

of multi-activation function and mixed-precision quantization.

The main contributions of this work are as follows:

• Hardware Friendly and Runtime Reconfiguration: We

propose a generic activation unit based on PWLF with

Power-of-Two (PoT) and Additive Power-of-Two (APoT)

slope approximation, which was used in the design of

a multiplier in prior works [15, 16]. The design uses

only comparators and a 1-bit shifter pipeline and can be

reconfigured at runtime by updating a small set of break
point and shift-encoding registers. While PWLF, PoT,

and APoT techniques have been individually explored in

prior work, no existing design integrates these concepts

into a unified activation unit with runtime configurability

and mixed-precision support, nor evaluates their hardware

feasibility across multiple nonlinear activations, including

non-monotonic functions.

• Flexible Function Support and Adaptation for Mixed
Precision Quantization: GRAU supports multiple nonlin
ear and non-monotonic activations (e.g., ReLU, Sigmoid,

SiLU) and easily adapts to different quantization preci
sions through lightweight reconfiguration of breakpoints

and shifts.

• Approximation Experiments: As an experimental scheme,

we adopted the open-source pwlf library to convert

the nonlinear activation folded with batch normaliza
tion and output re-quantization. We evaluate PoT/APoT

approximations on MNIST and CIFAR-10 under 4/8
bit and 1/2/4/8-bit mixed-precision settings with various

activation functions. The results suggest the feasibility

of our approach to hardware: GRAU maintains accuracy

within 1% in most cases, and we analyze the rare cases

where larger deviations occur.

• Hardware Implementation: We implement both pipelined

and serialized GRAU variants. The pipelined design

achieves higher throughput, while the serialized version

provides lower cost and greater configurability.

• Resource Report: Based on the synthesis and implementa
tion in Vivado, the results show that our GRAU hardware

reduces LUT usage by over 90% compared with Multi-


!!! page 3 "Liu_2026_GRAU"

Fig. 2: Comparing the original nonlinear function, PWLF approximated function, PoT approximated PWLF function, and

APoT approximated PWLF function

TABLE III: Comparing the Accuracy of Original QNN, PWLF, PoT-PWLF, and APoT-PWLF Approximated QNN Models

Model

SFC

CNV

Dataset

MNIST

CIFAR-10

Precision

4bit

8bit

Mixed-Precision

Mixed-Precision

Activation

ReLU

Sigmoid

SiLU

ReLU

Sigmoid

SiLU

ReLU

Sigmoid

SiLU

ReLU

Sigmoid

SiLU

Original

98.23%

98.19%

98.27%

98.13%

98.16%

98.04%

97.73%

97.82%

97.55%

78.65%

76.81%

77.81%

PWLF

98.23%

98.14%

98.15%

98.14%

98.17%

98.15%

97.73%

97.82%

97.52%

78.24%

73.97%

78.21%

PoT-PWLF

16-bit

98.20%

98.19%

94.86%

98.10%

98.07%

97.90%

97.76%

97.82%

88.14%

77.56%

73.69%

67.11%

32-bit

98.20%

98.19%

95.00%

98.13%

98.06%

97.90%

97.76%

97.82%

88.14%

77.94%

73.64%

67.11%

APoT-PWLF

16-bit

98.22%

98.17%

94.86%

98.11%

98.18%

97.97%

97.74%

97.82%

88.39%

77.52%

73.68%

65.22%

32-bit

98.21%

98.18%

95.28%

98.14%

98.17%

97.98%

97.74%

97.82%

88.39%

78.18%

73.97%

67.95%

Threshold units, achieving higher frequency, lower Area
Delay-Product (ADP), and lower Power-Delay-Product

(PDP), which demonstrates promising hardware and

power efficiency.

Although GRAU can be integrated into any QNN accelerator

on FPGA/ASIC, the goal of this work is not to design a full

accelerator architecture. Instead, we aim to establish a unified

activation hardware design paradigm that enables runtime

reconfiguration, multi-function support, and mixed-precision

activation with significantly reduced overhead. Since quantized

activation functions are present in every layer of modern QNNs,

improving each activation unit directly scales across the entire

accelerator.

D. Organization

This manuscript is structured in the following way: Section

II discusses how to convert the original QNN models to the

PoT and APoT approximated models for GRAU hardware

and the hardware designs of GRAU activation units in this

work. Section III shows the hardware evaluation results of

the above-mentioned GRAU designs. Section IV discusses

the further potential improvement and optimization of GRAU

and concludes the contents of this paper.

II. IMPLEMENTATION

A. PoT and APoT Approximated Activation Functions for

GRAU Hardware

Following the objectives outlined above, we transform the

original nonlinear activation functions folded with BN and

output re-quantization in QNNs into PWLF, PoT-PWLF, and

APoT-PWLF representations compatible with the proposed

GRAU architecture. As this work does not aim to introduce a

novel fitting algorithm, we utilize the open-source pwlf [17]

library to construct PWLF models and obtain their PoT and

APoT approximations. To ensure efficient hardware realization,

we additionally constrain the number of segments and limit

the allowable range of power-of-two slopes when generating

the PoT- and APoT-based approximations.

In Figure 2, we introduce the instances of PWLF approxi
mated Sigmoid and SiLU functions and their PoT and APoT

variants with six segments for 8-bit quantization. The first

column in Figure 2 plots the original Sigmoid and SiLU folded

with BN and output re-quantization. The second and third

columns are their PoT and APoT approximated functions. As

shown in the plot of the original SiLU, its output is out of the

allowed range of signed 8-bit integers, causing the clamp shown


!!! page 4 "Liu_2026_GRAU"

in the PWLF, PoT-PWLF, and APoT-PWLF plots of SiLU.

Therefore, in the worst-case scenario, if the original nonlinear

function falls outside both the allowed maximum and minimum

ranges of the quantized output, its PWLF, PoT-PWLF, and

APoT-PWLF approximated functions require two segments for

clamping. Therefore, we believe six is the minimum number

of segments to express the approximation of original nonlinear

functions.

From PWLF to PoT- and APoT-PWLF, we adopt a three-step

approximation:

• Considering that the inputs to our quantized activation

unit in the QNN accelerator are the integer outputs from

MACs, in PoT-PWLF and APoT-PWLF approximation,

we adjust the breakpoints of segments to their nearest

integers.

• We approximate the slope of each segment in PWLF

functions to the nearest PoT and APoT value. For instance,

if we define the allowable power range for PoT and APoT

approximation as [−10, 6), it means PoT approximated

slopes can be 2−10, 2−9, . . . , 24, 25, and APoT slopes

can be the sum of one combination with any of these

allowable PoT values, where one PoT value can only be

used once in combination.

• We chose the left rounded breaking point of each segment

to create a new linear function with approximated PoT

and APoT slopes. Therefore, as shown in the third column

in Figure 2, the PoT approximation has a small gap in

the right end of each segment, since the approximated

breaking points and slopes have a small bias for each

segment compared with the original PWLF functions.

APoT approximation also has this gap. However, it’s

more accurate than PoT. Therefore, the fourth column

cannot clearly show the tiny gap in APoT.

Therefore, based on Brevitas [18] and pwlf [17], we created

the PWLF, PoT-PWLF, and APoT-PWLF approximated QNN

models on MNIST and CIFAR10 after the Quantization-Aware

Training (QAT) as the following steps:

• Training the QNN models and recording the output

ranges of each quantized Fully Connected (FC) layer,

QuantLinear, and quantized Convolution (CONV) layers,

QuantConv2d while training, which are the MAC outputs

on hardware.

• For each layer, extend the recorded MAC output range

as 4× wider and average generating 1000 samples from

the extended range as dummy input. Then, extracting

the corresponding BN and quantized activation layers,

such as QuantReLU and QuantSigmoid in Brevitas, from

the trained QNN model and packaging them as black
boxes. Computing the output of these black boxes with the

dummy input. Then, adopt these outputs to fit a piecewise

linear function based on pwlf library [17], which will be

the same form as the second column in Figure 2.

• Extracting the breaking points, slopes from the fitted

piecewise linear function. Rounding the breaking points

and approximating the slopes as PoT and APoT form with

selected power ranges. We used [−10, 6) and [−24, 8) in

this work. Then, we created the PoT and APoT PWLF

functions and replaced the BN and quantized activation

layers in the original model to generate the PWLF, PoT
PWLF, and APoT-PWLF approximated models.

• Evaluating the accuracy of the original accurate model

and PWLF, PoT-PWLF, and APoT-PWLF approximated

models

As shown in Table III, we evaluated the above-mentioned

four different models with a Small Fully Connected Net
work (SFC) and Simplified VGG-like Convolution Neural

Network (CNV) from FINN [1] based on the MNIST [4] and

CIFAR-10 [19] datasets. SFC has four FC layers, containing

256/256/256/10 neurons, respectively. We evaluated it with

4/8-bit QNN models and one 1/2/4/8-bit mixed-precision QNN

model. CNV has three CONV blocks followed by three FC

layers. Each block consists of two 3x3 CONV layers and one

2x2 max-pooling layer. The channel number of CONV layers

in each CONV block is 64/128/256. The original FC layer

in CNV models has 512/512/10 neurons. To reduce the time

consumption of fitting the PWLF functions, we reduced it

to 256/256/10. Since we use one bit to represent the usage

of one power of two in the allowable range of [−10, 6) and

[−24, 8), GRAU hardware would require 16- and 32-bit data

as PoT and APoT setting encoding. As a result, the models

that support these two ranges are named 16/32-bit PoT-PWLF

and APoT-PWLF models.

As shown in Table III, PWLF, PoT-PWLF, and APoT-PWLF

approximations generally introduce less than 1% accuracy

loss across most experiments. More significant losses occur

primarily in SiLU-based models: PoT-PWLF and APoT-PWLF

approximations degrade accuracy by approximately 3% ∼10%

on 4-bit and mixed-precision SFC models, and similarly by

around 10% on mixed-precision CNV models. In contrast,

in Sigmoid-based CNV models, most degradation originates

from PWLF itself, with PoT/APoT approximations introducing

negligible additional loss.

To identify the source of approximation errors, we analyze

the PWLF functions generated by pwlf. Since pwlf is a

continuous, floating-point-oriented library, it does not naturally

adapt to the discrete integer-domain characteristics of MAC

outputs in QNN. When two fitted breakpoints are close (e.g.,

1.2 and 1.3), both round to the same integer, collapsing the

corresponding linear segment and reducing expressive capacity.

We observed such degenerate segments, particularly in SiLU

models, explaining the accuracy degradation in those settings.

Moreover, the pwlf library can only run on a CPU optimized

with multi-core acceleration. We measured the time cost of

piecewise linear fitting on our server (AMD EPYC 7513 32
Core Processor with 1TB memory). Fitting a single nonlinear

function with 1,000 samples takes approximately four minutes.

A model like ResNet-26 contains around 4,904 activation

kernels, which would require approximately 13.6 days for


!!! page 5 "Liu_2026_GRAU"

0

1

1

1

1

1

1

1

1

1

0

0

0

0

0

0

0

+/
32

16

8

4

2

1

Ǡ

ǡ

Ǡ

ǣ

Ǡ

ǧ

Ǡ

Ǡǥ

Ǡ

ퟑǡ

Ǡ

ǥǣ

Ǡ

Ǡǡǧ

Ǡ

ǡǤǥ

Ǡ

ǤǠǡ

Ǡ

Ǡퟎǡǣ

ǝ = 1

8 ǜ + ǆ

0

0

0

0

0

0

1

1

0

0

1

0

0

0

0

0

1

+/
32

16

8

4

2

1

Ǡ

ǡ

Ǡ

ǣ

Ǡ

ǧ

Ǡ

Ǡǥ

Ǡ

ퟑǡ

Ǡ

ǥǣ

Ǡ

Ǡǡǧ

Ǡ

ǡǤǥ

Ǡ

ǤǠǡ

Ǡ

Ǡퟎǡǣ

ǝ =−(1 + 1

2 + 1

16 +

1

1024 )ǜ + ǆ

Fig. 3: Encoding of segment slopes for PoT-PWLF (down)

and APoT-PWLF (up) approximation

Data_in

Setting_in

>>

MUX

Data_out

a) Shifter Unit for Single 2n

Sum_in

Data_in

>>

Data_out

MUX

0

+

Sum_out

Setting_in

b) Shifter Unit for Multiple 2n

Fig. 4: Shifter unit design in hardware for PoT-PWLF (a) and

APoT-PWLF (b) approximation

PWLF fitting. In our experiment setup, each model structure is

explored with nine variants; therefore, a full evaluation would

take around four months, excluding training. Consequently,

our experiments focus on smaller networks while maintaining

coverage across activation types and quantization precisions.

Importantly, these limitations come from the fitting tool

rather than the GRAU architecture. GRAU is independent

of the specific fitting algorithm and can be scaled to larger

models once more efficient, parallel, or GPU-accelerated fitting

libraries become available. Future integer-aware PWLF or

PoT/APoT approximation algorithms can further improve

accuracy without requiring any modification to the GRAU

hardware.

In summary, expressing BN-folded nonlinear activations

and re-quantization through PWLF, PoT-PWLF, and APoT
PWLF approximations enables the proposed GRAU to support

multi-activation, mixed-precision QNNs in a hardware-efficient

manner.

B. Hardware Implementation of GRAU

Considering we limit the power range of PoT-PWLF and

APoT-PWLF functions as [−10, 6) and [−24, 8), if we give

a 7/9-bit pre-left-shifting, which means timing a 26 or 28,

to every inputs, qin, as Qin = qin × 26 or Qin = qin × 28,

computing each qin × 2n, (−10 ≤n < 6) or (−24 ≤n < 8)

can be converted as only right shifting, Qin × 2m, (−16 ≤

m < 0) or (−32 ≤m < 0). Therefore, as shown in Figure 4,

we implemented different 1-bit shifter units for PoT-PWLF

and APoT-PWLF functions:

For PoT-PWLF, the shifter unit in Figure 4 (a) loads the

input data and, according to the 1-bit setting input, decides

if it needs to pass the 1-bit right-shifted data or the original

input data to the next shifter unit.

MAC

Thres.

Encode

Shifter Settings Buffer

Init

SU

Output

Shifter Settings Loader

0

1

1

0

SU Ctl

counter

Fig. 5: Serialized hardware implementation of Generic Activa
tion Unit PoT-PWLF and APoT-PWLF shifter unit

MAC

Thres. Pip.

Encode

Shifter Settings Buffer

Init

SU

SU

SU

SU

SU

Output

. . .

Shifter Settings Loader

0

1

1

0

1

1

0

0

1

1

0

0

1

1

0

1

. . .

Fig. 6: Pipelined hardware implementation of Generic Activa
tion Unit PoT-PWLF and APoT-PWLF shifter unit

For APoT-PWLF, the shifter unit in Figure 4 (b) loads the

input data and a sum output from the prior shifter unit. After

applying the 1-bit right shift to the input data, according to

the 1-bit setting input, this shifter unit will determine whether

to add the right-shifted data to the loaded sum output. Then,

it will transfer the 1-bit right-shifted input and the sum result

to the next shifter unit.

As a result, if we can implement a 16/32 shifter unit

and connect them as a pipeline, using the 6/8-bit pre-left
shifted data as input, we can compute the results of the inputs

times PoT or APoT slopes. To control these shifter units, as

shown in Figure 3, we defined the shifter control encoding

format, which is the Setting In signals in each shifter unit

of Figure 4. Figure 3 shows the 17-bit shifter control encoding

for 16 shifter units in PoT and APoT approximation with the

power range of [−10, 6). Its first bit is the sign bit. Before the

computation, all inputs should apply a 6-bit pre-left-shifting.

For the PoT-PWLF shifter computation in Figure 3 (down),

because it only supports the format of single 2n, the setting

should consist of multiple consecutive ”1” and consecutive

”0”. For instance, if the slope is 1

8, the digits from 32 to 1

8

should be ”1”. Then, the 6-bit pre-left-shifted input will be

right-shifted 9 times in the shifter units, which received the

”1” from Setting In. The result from the last shifter unit is

equal to the original input divided by 8 (right shifting 3 bits).

For APoT-PWLF shifter computation in Figure 3 (up), if

the slope is 1 + 1

2 + 1

16 +

1

1024, the Setting In digits for 1, 1

2,

1

16, and

1

1024 should be ”1”. Then, the 6-bit pre-left-shifted

input will be executed 1-bit right shifting in every shifter unit,

and the shifted data in 1, 1

2,

1

16, and

1

1024 units will be added

into the sum.


!!! page 6 "Liu_2026_GRAU"

TABLE IV: Hardware Results of Multi-Threshold, PoT-PWLF, and APoT-PWLF Activation Units

Scheme

Mode

LUT

FF

Frequency

Total Delay

Power

Area-Delay

Power-Delay

Latency (Cycles)

(ns)

(W)

Products

Products

1-bit

2-bit

4-bit

8-bit

Multi-Threshold

Pipelined

10206

18568

200MHz

2.848

0.129

0.3673

29066.688

1

3

15

255

Serialization

2796

8264

100MHz

5.777

0.032

0.1848

16152.492

1

3

15

255

PoT-PWLF

Pipelined

660

1006

250MHz

1.57

0.018

0.0282

1036.2

6

6

24

24

Serialization

270

456

250MHz

2.338

0.012

0.028

631.26

6

6

24

24

APoT-PWLF

Pipelined

786

1097

250MHz

1.946

0.016

0.0311

1529.556

6

6

24

24

Serialization

283

463

250MHz

2.352

0.011

0.0258

665.616

6

6

24

24

If all shifter encoding bits are 0, it means the slope is 0.

Based on the above-mentioned principle, we implemented

two different GRAU architectures for PoT-PWLF and APoT
PWLF shifter units. Figure 5 shows the serialized architecture

of GRAU. It only implements one shifter unit and reuses it for

different slope approximations. Figure 6 shows the pipelined

architecture of GRAU, which consists of a shifter unit pipeline.

The integer outputs of the MAC will be loaded into the

thresholds first to determine which segment they belong to.

As shown in Table III, for a PWLF function with 6 segments,

if we consider the inputs, which are out of the range of the

function approximation, belong to the first and last segments,

we only need to implement 5 thresholds to classify the inputs.

After obtaining the index of the segment by thresholds, GRAU

loads the shifter unit setting from the setting buffer and passes

it to the setting loader to regenerate the setting encode in

the correct format for both pipelined and serialized GRAU

designs. The MAC output will be transmitted to the initial

module simultaneously to apply the pre-left shift. After both

input and shifter settings are ready for processing, they will be

loaded into the serialized shifter unit or shifter unit pipeline

to compute the products between the input and the slope,

approximated in the PoT or APoT form. The final result will

apply the sign bit and bias to complete the piecewise linear

approximation for the activation unit. Therefore, based on the

above-mentioned designs, if we reload the value of thresholds

and shifter settings, GRAU can be reconfigured to approximate

different nonlinear functions for the QNN acceleration on

hardware.

III. EVALUATION

To evaluate this work, we implemented six different acti
vation unit instances on hardware based on Multi-Threshold

architecture, 16-bit PoT-PWLF, and APoT-PWLF-based GRAU

architectures. Three of these six instances are implemented as

a pipeline structure, and the others are serialized structures.

We have not implemented the GRAU instance for 32-bit PoT
PWLF and APoT-PWLF, which support the range [−24, 8)

for the power of two, because, as shown in Table III, 16-bit

and 32-bit approximations of PoT-PWLF and APoT-PWLF

have similar accuracy. However, the 32-bit GRAU requires

more hardware resources. Considering that the Multi-Threshold

activation unit can reconfigure thresholds for different acti
vation functions, which can also be considered a kind of

generic reconfigurable activation unit, we include it in this

evaluation as a baseline. This baseline follows the official

FINN-R implementation[2], where each output precision level

requires 2n −1 thresholds after BN folding. This behavior is

inherent to the MT paradigm rather than a design choice, and is

well documented in prior FINN literature. We optimized it as a

pipelined structure consisting of 255 threshold units connected

in a pipeline, and a serialized structure that implements only

one reusable threshold with 255 threshold registers.

Therefore, as shown in Table IV, we synthesized and

implemented these instances using Vivado on the Ultra96-V2

FPGA platform. Based on the post-implementation timing

simulation, we evaluated their power, critical path delay,

emphArea-Delay-Product (ADP), and Power-Delay-Product

(PDP).

1) Hardware Resource Consumption: As shown in the LUT

and FF columns of Table IV, our PoT-PWLF and APoT-PWLF
based GRAU instances consume only 6.4%, 7.7%, 9.7%, and

10.1% of LUTs of the corresponding pipelined and serialized

Multi-Threshold based activation units. Compared the design

difference between Multi-Threshold and our GRAU units: A

pipelined Multi-Threshold activation unit needs 255 threshold

units and 255 threshold value registers to support the highest

8-bit quantization. A serialized Multi-Threshold activation unit

needs one threshold unit and 255 threshold value registers

to support the highest 8-bit quantization. However, when our

GRAU activation unit applies six segments and (-10,6) ranges

of power in PWLF approximation, its pipelined instances need

only five threshold units, five threshold value registers, five

16-bit shifter setting registers, and 16 1-bit right shifters. Its

serialized instances need only one threshold unit, five threshold

value registers, five 16-bit shifter setting registers, and one

1-bit right shifter. Therefore, our GRAU architecture can cost

much fewer hardware resources to support mixed-precision

multiple activation functions.

2) Latency: As shown in the latency column in Table IV,

Multi-Threshold activation unit takes 1/3/15/255 cycles to

processing one input. Because our GRAU instances have

one pre-left-shifting unit, five thresholds, 16 right shifters,

one sign bit processing unit, and one bias adder, it will take

24 cycles to complete one approximate nonlinear processing,

which is slower than the 1/2/4-bit quantization of the Multi
Threshold activation unit. Therefore, considering that GRAU

also has five thresholds, it can support the 1/2-bit Multi
Threshold quantization. We implemented a bypass for our

GRAU instances for 1/2-bit. Therefore, as shown in the latency


!!! page 7 "Liu_2026_GRAU"

column in Table IV, they take 6 cycles in 1/2-bit columns.

3) Total Delay, Power, ADP, and PDP:

The post
implementation timing simulation on Vivado reported the

power, critical path delay, Area-Delay-Product (ADP), and

Power-Delay-Product (PDP) of our six instances. The fre
quency shows the highest frequency these instances can support.

Therefore, we can infer that our GRAU implementations can

support higher clock frequencies due to their low critical total

path delay. Moreover, the lower ADP and PDP of our GRAU

also show that our work has better power and design efficiency

than the Multi-Threshold activation units.

IV. CONCLUSION AND FURTHER WORKS

To support the multi-function, mixed-precision QNN and

optimize the hardware resource consumption, we explored

the Generic Reconfigurable Activation Unit (GRAU) based

on Piecewise Linear Fitting approximated function, Power
of-Two approximated PWLF function, and Additive Power-of
Two approximated PWLF function. The experiment results for

the TFC and CNV models, using the MNIST and CIFAR
10 datasets, show that the PoT-PWLF and APoT-PWLF

approximations result in a small accuracy loss compared to the

original, accurate QNN models. Therefore, we implemented

the serialized and pipelined PoT-PWLF and APoT-PWLF

approximated Generic Reconfigurable Activation Unit (GRAU)

in this work. The implementation results show that our work

can reduce more than 90% of the LUT consumption of Multi
Threshold-based generic activation functions, supporting higher

clock frequencies with better power and hardware efficiency.

Considering the higher accuracy loss of SiLU-based SFC

and CNV models, we found that the fitted piecewise linear

functions influence the accuracy of our approximated models,

because we are just converting the fitted floating-point-based

PWLF functions to our integer-based PoT-PWLF and APoT
PWLF functions. Therefore, for future work, we will explore

the possibility of directly fitting the accurate nonlinear function

to our PoT-PWLF and APoT-PWLF functions, or even investi
gate the potential paradigms of achieving learnable PoT-PWLF

and APoT-PWLF functions through network training.

REFERENCES

[1]

Yaman Umuroglu et al. “FINN: A framework for fast, scalable

binarized neural network inference”. In: Proceedings of the 2017

ACM/SIGDA International Symposium on Field-Programmable Gate

Arrays. 2017, pp. 65–74.

[2]

Michaela Blott et al. “FINN-R: An end-to-end deep-learning frame
work for fast exploration of quantized neural networks”. In: ACM

Transactions on Reconfigurable Technology and Systems (TRETS)

11.3 (2018), pp. 1–23.

[3]

Yuhao Liu, Salim Ullah, and Akash Kumar. “Bitwise Systolic Array

Architecture for Runtime-Reconfigurable Multi-Precision Quantized

Multiplication on Hardware Accelerators”. In: 2025 26th International

Symposium on Quality Electronic Design (ISQED). 2025, pp. 1–9.

[4]

Li Deng. “The mnist database of handwritten digit images for machine

learning research”. In: IEEE Signal Processing Magazine 29.6 (2012),

pp. 141–142.

[5]

Stefan Elfwing, Eiji Uchibe, and Kenji Doya. “Sigmoid-weighted lin
ear units for neural network function approximation in reinforcement

learning”. In: Neural networks 107 (2018), pp. 3–11.

[6]

F. Piazza, A. Uncini, and M. Zenobi. “Neural networks with digital

LUT activation functions”. In: Proceedings of 1993 International

Conference on Neural Networks (IJCNN-93-Nagoya, Japan). Vol. 2.

1993, 1401–1404 vol.2.

[7]

Revathi Pogiri, Samit Ari, and K K Mahapatra. “Design and FPGA

Implementation of the LUT based Sigmoid Function for DNN

Applications”. In: 2022 IEEE International Symposium on Smart

Electronic Systems (iSES). 2022, pp. 410–413.

[8]

Pramod Kumar Meher. “An optimized lookup-table for the evaluation

of sigmoid function for artificial neural networks”. In: 2010 18th

IEEE/IFIP International Conference on VLSI and System-on-Chip.

2010, pp. 91–95.

[9]

Ming Zhang, Stamatis Vassiliadis, and Jose G. Delgado-Frias. “Sig
moid generators for neural computing using piecewise approxima
tions”. In: IEEE transactions on Computers 45.9 (1996), pp. 1045–

1049.

[10]

Zerun Li et al. “FPGA Implementation for the Sigmoid with Piecewise

Linear Fitting Method Based on Curvature Analysis”. In: Electronics

11.9 (2022).

[11]

Ivan Tsmots, Oleksa Skorokhoda, and Vasyl Rabyk. “Hardware

Implementation of Sigmoid Activation Functions using FPGA”.

In: 2019 IEEE 15th International Conference on the Experience

of Designing and Application of CAD Systems (CADSM). 2019,

pp. 34–38.

[12]

Vantruong Nguyen, Jueping Cai, and Linyu Wei. “Low Complexity

Sigmoid Function Implementation Using Probability-Based Piecewise

Linear Function”. In: Proceedings of the 2019 2nd International Con
ference on Algorithms, Computing and Artificial Intelligence. ACAI

’19. New York, NY, USA: Association for Computing Machinery,

2020, 236–241.

[13]

Kezhu Liu et al. “Cost effective Tanh activation function circuits

based on fast piecewise linear logic”. In: Microelectronics Journal

138 (2023), p. 105821.

[14]

Safa Bouguezzi, Hassene Faiedh, and Chokri Souani. “Hardware

Implementation of Tanh Exponential Activation Function using

FPGA”. In: 2021 18th International Multi-Conference on Systems,

Signals, and Devices (SSD). 2021, pp. 1020–1025.

[15]

Dominika Przewlocka-Rus et al. Power-of-Two Quantization for Low

Bitwidth and Hardware Compliant Neural Networks. 2022. arXiv:

2203.05025 [cs.LG].

[16]

Yuhang Li, Xin Dong, and Wei Wang. Additive Powers-of-Two

Quantization: An Efficient Non-uniform Discretization for Neural

Networks. 2020. arXiv: 1909.13144 [cs.LG].

[17]

Charles F. Jekel and Gerhard Venter. pwlf: A Python Library for

Fitting 1D Continuous Piecewise Linear Functions. 2019.

[18]

Alessandro Pappalardo. Xilinx/brevitas. 2023.

[19]

Alex Krizhevsky, Geoffrey Hinton, et al. “Learning multiple layers

of features from tiny images”. In: (2009).

