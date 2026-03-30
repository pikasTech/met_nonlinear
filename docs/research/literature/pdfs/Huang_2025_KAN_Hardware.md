Hardware Acceleration of Kolmogorov–Arnold
Network (KAN) in Large-Scale Systems
Wei-Hsing Huang, Jianwei Jia, Yuyao Kong, Faaiq Waqar, Tai-Hao Wen, Meng-Fan Chang, Fellow, IEEE, Shimeng Yu,
Fellow, IEEE
Abstract—Recent developments have introduced
Kolmogorov-Arnold Networks (KAN), an innovative architectural
paradigm capable of replicating conventional deep neural network
(DNN) capabilities while utilizing significantly reduced parameter
counts through the employment of parameterized B-spline
functions incorporating trainable coefficients. Nevertheless, the B-
spline functional components inherent to KAN architectures
introduce distinct hardware acceleration complexities. While B-
spline function evaluation can be accomplished through look-up Fig. 1. Introduction of KAN and its potential for
table (LUT) implementations that directly encode functional parameter reduction.
mappings, thus minimizing computational overhead, such
1 INTRODUCTION
approaches continue to demand considerable circuit
infrastructure, including LUTs, multiplexers, decoders, and Contemporary deep neural network (DNN) models
associated components. This work presents an algorithm- characterized by their ever-escalating parameter counts present
hardware co-design approach for KAN acceleration. At the significant impediments to edge device deployment,
algorithmic level, techniques include Alignment-Symmetry and substantially constraining the implementation of privacy-
PowerGap KAN hardware aware quantization, KAN sparsity
preserving, real-time detection capabilities and severely limiting
aware mapping strategy, and circuit-level techniques include N:1
the feasibility of resource-constrained edge computing
Time Modulation Dynamic Voltage input generator with analog-
applications. Traditional deep neural networks, including
compute-in-memory (ACIM) circuits. Furthermore, this work
convolutional neural network (CNN) designs, large language
conducts comprehensive evaluations on large-scale KAN networks
to validate the proposed methodologies. Non-ideality factors, model (LLM) frameworks, and various other architectural
including partial sum deviations arising from process variations, paradigms, conventionally implement fixed, predetermined
have been evaluated with the statistics measured from the TSMC activation functions coupled with trainable weight parameters
22nm RRAM-ACIM prototype chips. Utilizing optimally [1][2]. The recently emerged Kolmogorov-Arnold Networks
determined KAN hyperparameters in conjunction with circuit (KAN) [3], which drew inspiration from the mathematical
optimizations fabricated at the 22nm technology node, despite the
foundations of the Kolmogorov-Arnold representation theorem
parameter count for large-scale tasks in this work increasing by
[4][5], fundamentally reimagines the traditional multi-layer
500K× to 807K× compared to tiny-scale tasks in previous work, the
perceptron (MLP) architecture by replacing conventional linear
area overhead increases by only 28K× to 41K×, with power
weight matrices with parameterized B-spline functions B(X)
consumption rising by merely 51× to 94×, while accuracy
degradation remains minimal at 0.11% to 0.23%, thereby while simultaneously implementing trainable, learnable
demonstrating the scaling potential of our proposed architecture. activation functions positioned on the network edges rather than
nodes. According to recent studies, KANs have demonstrated
Keywords—Kolmogorov-Arnold Networks (KAN), Quantization,
the ability to achieve comparable or superior accuracy with
Compute-in-Memory (CIM), Resistive Random Access Memory
networks that are smaller in parameter count compared to
(RRAM), Algorithm-Hardware Co-Design
traditional MLPs [3][23]. This innovative architectural
paradigm has been empirically validated, demonstrating
improvements not only in performance but also in
This work was supported in part by the PRISM, one of the
interpretability, as comprehensively illustrated in Fig. 1 [3][6].
SRC/DARPA JUMP 2.0 centers.
Wei-Hsing Huang, Jianwei Jia, Yuyao Kong, Faaiq Waqar, and KAN architectures demonstrate considerable potential and
Shimeng Yu are with the School of Electrical and Computer Engineering, promise to successfully replace conventional traditional DNN
Georgia Institute of Technology, Atlanta, GA 30332 USA backbones that utilize fixed activation functions combined with
(Corresponding author. E-mail: shimeng.yu@ece.gatech.edu).
learnable weights in increasingly complex DNN models,
Wei-Hsing Huang and Jianwei Jia are co-first authors.
Tai-Hao Wen is the Department of Electrical Engineering, National potentially enabling substantial reduction in the overall size of
Tsing Hua University (NTHU), Hsinchu 30013, Taiwan. large-scale models, including computationally intensive LLMs
Meng-Fan Chang is with the Department of Electrical Engineering, and recommendation models as MLPs are widely used as
National Tsing Hua University (NTHU), Hsinchu 30013, Taiwan, and
building blocks, and thereby facilitating their practical
also with Taiwan Semiconductor Manufacturing Company (TSMC),
Hsinchu 30075, Taiwan. deployment on edge devices.

2
However, despite these advantages, KAN operation inference accuracy performance. Moreover, current mainstream
fundamentally requires computationally intensive B-spline CIM input methodologies include binary input schemes with
function computation and evaluation. While classical multi-cycle operation, multi-voltage level input approaches
mathematical definitions involving recursive computational within single cycle operation, or time delay mechanisms with
methods [7] can theoretically evaluate B-spline functions with multi-bit input encoding. Binary input methodology offers
mathematical precision, the computational requirements and superior accuracy but consequently increases operational
processing demands increase dramatically and significantly latency and fundamentally limits achievable TOPS/W metrics.
with progressively higher-order k values. An alternative While multi-voltage level input approaches successfully achieve
approach more suitable for edge-friendly implementation favorable and attractive TOPS/W ratios combined with low
employs pre-computed lookup tables (LUTs) for direct and operational latency, the inherently constrained VDD range
immediate B-spline function mapping, substantially simplifying renders these inputs particularly susceptible to noise
the hardware implementation complexity and dramatically interference, thereby substantially compromising computational
reducing the overall computational demands. Despite these accuracy. Time-delay multi-bit input schemes offer enhanced
considerable advantages and benefits, this implementation noise resilience capabilities but at the considerable cost of
approach still necessitates and requires significant circuit increased operational latency and reduced throughput.
resources, including extensive LUTs, multiplexers (MUXs), In this work, we systematically aim to co-optimize both
decoders, and associated control logic, as comprehensively algorithmic and circuit-level implementations, strategically
depicted and shown in Fig. 2. reducing area, power consumption, and operational latency
Furthermore, KAN architectures, similar to traditional MLPs, while simultaneously increasing the computational accuracy of
inherently involve extensive and computationally intensive ACIM-based computation specifically tailored for KAN
parallel multiply-accumulate (MAC) operations throughout architectures. This paper presents a journal extension of our
their computational pipeline. The well-documented von previous conference presentation [24]. We have augmented all
Neumann bottleneck present in conventional computing four schemes with comprehensive implementation details and
architectures leads to substantial inefficiencies and performance introduced two additional algorithms to elaborate on the
degradation. This bottleneck results from the physical framework's technical specifications. Most importantly, our
separation between memory and processing units, causing prior work [24] limited its evaluation to small-scale models
significant data movement overhead that can dominate the (with 279~2232(cid:3031)B) within the context of knot theory, this work
overall energy consumption in data-intensive applications. employs large-scale KAN models (39(cid:3031)MB ~ 63(cid:3031)MB) for a
Compute-in-Memory (CIM) [8], representing an emerging non- recommendation system [23] to provide a scaling aspect of our
von Neumann architectural paradigm, directly addresses and proposed methodology. The evaluation in Section 4 is
mitigates this fundamental issue. CIM variants include digital- completely redone for the large-scale KAN models.
CIM (DCIM) [9], SRAM analog-CIM (ACIM) [10][11], and
RRAM-ACIM [12][13], etc. While DCIM and SRAM-ACIM 2 BACKGROUND
architectures offer comparatively higher computational
2.1 KAN: Kolmogorov-Arnold Networks and acceleration
accuracy than RRAM-ACIM implementations, the inherently
large SRAM cell sizes substantially limit achievable on-chip In contrast to MLPs, whose theoretical foundation rests on the
storage capacity, and their characteristically high standby power universal approximation theorem, KAN architectures are
consumption proves particularly undesirable and problematic grounded in the Kolmogorov-Arnold representation theorem.
for battery-constrained edge devices. Therefore, this paper The mathematical formulation of individual KAN layers
comprehensively examines and investigates RRAM-ACIM follows equations (1)-(2), wherein the b(x) component, initially
acceleration techniques for KAN architectures. However, it implemented through SiLU activation functions, incorporates
should be explicitly noted that the proposed algorithm-level residual connectivity into the architecture.
optimizations and enhancements are fundamentally hardware- ϕ(x) =w b b(x) + w s spline(x) (1)
agnostic and can be applied across different implementation spline(x) = (cid:3533)𝑐𝑖Bi(x) (2)
platforms.
(cid:3036)
Despite RRAM-ACIM's numerous advantages for practical
ϕ(x) =w b b(x) + (cid:3533)𝑐𝑖′Bi(x) (3)
edge deployment scenarios, including remarkably low standby
(cid:3036)
power consumption and high integration density, it encounters Fig. 1 depicts the relationship between the grid size parameter
several critical challenges as comprehensively illustrated in Fig. G and the B-spline order K, where the aggregate count of Bi(x)
2. The process-temperature-voltage (PVT) variations are key functions equals K+G. For the presented configuration with
concerns for ACIM. The progressively increasing array sizes K=3 and G=5, this work substitutes ReLU activation functions
combined with aggressive technology scaling substantially for the original SiLU implementation, achieving enhanced
exacerbate IR-drop phenomena [14], primarily due to increased hardware efficiency while maintaining computational accuracy.
parasitic bit line resistance, thereby hampering and degrading Given that the w b(x) term can be efficiently accelerated
b

through conventional RRAM-ACIM architectures, the primary spline ACIM co-design, it suffers from long bit-stream latency
optimization target becomes the wspline(x) computation. The and substantial overhead dominated by parameter memory and
s
implementation strategy involves the multiplication of w with random number generation. Moreover, these prior works
s
ci to generate ci', followed by 8-bit quantization, yielding the [25,26,27] have only been applied to small-scale tasks, whereas
modified formulation expressed in equation (3). This this work conducts a comprehensive evaluation on large-scale
configuration enables ci' storage within the RRAM-ACIM array, tasks.
where Bi(x) values are delivered through word lines (WL) to
2.2 Compute-in-memory
facilitate parallelized multiply-accumulate computations. LUT
implementations for Bi(x) computation demonstrate superior CIM architectures utilize various embedded memory
suitability for edge deployment scenarios relative to recursive technologies, including SRAM, eDRAM, and emerging non-
B-spline evaluation methodologies. Furthermore, the uniform volatile memories such as RRAM. These memory architectures
nodal distribution inherent in KAN architectures ensures that exhibit distinctive operational characteristics and confront
B(X) functional representations remain consistent across unique implementation constraints. SRAM-based CIM
varying knot grid intervals, thus enabling the feasibility of implementations, while benefiting from advanced process node
shared LUT architectures for multiple B(X) instantiations. availability and superior access latency characteristics, are
Nevertheless, as illustrated in Fig. 2, existing quantization constrained by substantial leakage current, rendering them
approaches [15][16] introduce misalignment between knot grid suboptimal for deployment in energy-constrained edge
and quantization grid structures, generating unique input-output computing environments where standby power minimization
mapping relationships for individual Bi(x) functions. remains critical. Non-volatile memory technologies present
Consequently, hardware implementations require dedicated attractive characteristics for edge deployment scenarios,
LUT, multiplexer, and decoder resources for each Bi(x) particularly through reduced quiescent power dissipation and
component at the edge, leading to substantial energy enhanced storage density at mature process nodes, translating to
consumption and silicon area penalties. While the adoption of favorable cost effectiveness. Nevertheless, voltage degradation
fixed, non-programmable LUT architectures offers a potential along bit lines in RRAM-ACIM configurations introduces
mitigation strategy through reduced circuit footprint, such inference precision limitations. Additionally, traditional CIM
implementations sacrifice architectural flexibility, particularly implementations predominantly utilize either voltage-domain or
the capability to dynamically modulate B(X) computational temporal-domain modulation schemes for encoding multi-bit
precision according to application-specific constraints. word line inputs within single operational cycles. These
Additionally, the proliferation of Bi(x) functional units modulation approaches demonstrate vulnerability to on-chip
corresponding to increased K and G parameters fundamentally interference, resulting in compromised computational accuracy
limits the deployment viability of traditional quantization as illustrated in Fig. 2. The N:1 Time Modulation Dynamic
strategies for sophisticated KAN architectures characterized by Voltage Input Generator and KAN sparsity-aware weight
elevated K and G values within resource-constrained edge mapping strategies, elaborated in Sections 3.2 and 3.3
environments. The Alignment-Symmetry and PowerGap respectively, provide systematic solutions to these
hardware-aware quantization methodology, detailed in Section implementation challenges within RRAM-ACIM frameworks.
3.1, is developed to overcome these limitations. Prior work [25]
explored the implementation of Piece-Wise Linear (PWL) 3 PROPOSED TOP-DOWN HW-SW CO-
approximations as alternatives to B-spline functions through OPTIMIZATION
one-hot and thermometer encoding schemes. However, as B-
3.1 Alignment-Symmetry and PowerGap KAN hardware
spline complexity increases, PWL requires correspondingly
aware quantization for B(X)
higher precision, and the use of one-hot or thermometer
The proposed Alignment-Symmetry and PowerGap KAN
encoding paradigms incurs substantial memory overhead,
hardware aware quantization (ASP-KAN-HAQ) is developed to
thereby limiting their practical applicability, particularly in
minimize computational overhead and energy consumption
large-scale and more complex tasks. Prior work [26] employed
associated with B(X) function evaluation as defined in Equation
analog resistor networks utilizing series and parallel
(3). This approach encompasses a two-stage optimization
configurations for B-spline function computation. However, this
strategy:
approach demands exceptionally high precision in resistance
 Phase one: Alignment-Symmetry for suppressing the
values, presenting significant limitations in high-precision
needs of programmable LUT by enabling zero offset
application scenarios, particularly for 8-bit implementations.
between knot grid and quantization grid.
Prior work [27] implemented KAN nonlinearities via stochastic
 Phase two: PowerGap for reducing decoder and
computing—using a Segmented Multi-Dimensional Multi-
multiplexer complexity by constraining knot grid
Driving Finite State Machine (SMM-FSM) driven by pseudo-
intervals to power-of-two magnitudes.
random bitstreams and crossbar-routed interconnects—but,
compared with our deterministic one-cycle shared-LUT B-

4
Fig. 3. HW efficient Alignment-Symmetry KAN
Quantization for LUTs optimization.
Fig. 2. Challenges hindering low-power and high
accuracy edge AI applications.
The subsequent analytical framework examines a representative Fig. 4. HW efficient PowerGap KAN Quantization for
configuration with parameters K=3 and G=5, yielding eight MUXs and Decoders optimization.
basis functions B (x) through B (x) per input channel. The
0 7 representations, which permits a 50% reduction in shared LUT
implementation assumes 8-bit input quantization with values
memory requirements. This optimized architectural
spanning the integer range [0, 255]. Notably, the ASP-KAN-
configuration is designated as a Sharable-Hemi LUT (SH-LUT).
HAQ framework maintains extensibility to arbitrary parameter
Following the Alignment-Symmetric phase, a direct
configurations of K and G, variable precision specifications, and
implementation strategy for value routing from the SH-LUT to
architectural layers incorporating negative-valued inputs.
respective B0(x) through B7(x) functions with reduced
A. Phase One: Alignment-Symmetric
hardware complexity utilizes eight 2L-to-1 transmission gate
The first phase, designated as Alignment-Symmetric, derives
multiplexers (TG-MUXs) alongside an 8-bit optimized decoder
from empirical observations presented in Fig. 3. The
architecture. Nevertheless, this configuration continues to
misalignment between knot grid and quantization grid prevents
exhibit substantial silicon area requirements and elevated power
the utilization of a unified LUT across multiple B(X) functional
dissipation characteristics.
instances, despite potential data translation from disparate knot
B. Phase Two: PowerGap
grid intervals into a common interval space. This limitation is
The second phase, designated as PowerGap, is developed to
resolved through the ASP-KAN-HAQ framework, which
minimize transmission gate MUXs (TG-MUX) and decoder
establishes precise alignment between knot and quantization
overhead following the Alignment-Symmetric optimization.
grid structures for individual B(X) functions. This alignment is
Through constraining knot grid intervals to power-of-two values,
achieved by imposing a constraint whereby the quantization grid
this approach decouples local from global information domains,
dimensions constitute integer multiples of the corresponding
substantially reducing decoder and TG-MUX area requirements
knot grid parameters, formulated as:
as illustrated in Fig. 4, with the mathematical representation
G ∗ L ≤2(cid:3041),where L ∈ Z+ (4)
expressed as:
In Equation (4), the parameters G and n represent the knot count G ∗ 2(cid:3005) ≤ 2(cid:3041),where D ∈ Z+ (5)
and the system's maximum bit-width specification, respectively.
Within the KAN architecture, information contained in
The value of L that satisfies Equation (4) constrains the data
individual knot grids is characterized as local information,
range to the interval [0, G*L-1]. Values of L adhering to this
whereas the mapping between distinct grid intervals and their
integer multiple relationship eliminate positional discrepancies
corresponding B(X) functions constitutes global information.
between knot and quantization grids, thereby facilitating the
This distinction enables substantial reductions in hardware
deployment of a unified LUT architecture across all B(X)
resource utilization.
functional components. Additionally, this constraint induces
The hardware requirements are significantly reduced:
symmetrical properties within the quantized B(X)

Fig. 5. Hardware architecture with Alignment-Symmetry and PowerGap KAN hardware aware quantization.
1. TG-MUXs: from original eight 2L-to-1 TG-MUXs to which inevitably amplifies the impact of device variation,
optimized four L-to-1 TG-MUXs and four 1-to-5 TG- supply noise, and nonlinearity of the MOSFET transfer curve,
DEMUXs. leading to poor robustness. In contrast, PWM maps information
2. Decoders: from original one 8-bit decoder to optimized one into temporal width differences, which provides better resilience
(8-D)-bit decoder and one D-bit decoder. against small analog variations; however, distinguishing
Since decoder area scales exponentially with bit-width multiple bit levels requires long pulse widths, thereby extending
specifications, the silicon footprint of a single 8-bit decoder the MAC cycle and severely degrading throughput. To
substantially surpasses the combined area of an (8-D)-bit overcome these limitations, we develop an N:1 Time-Modulated
decoder and a D-bit decoder. Consequently, parameter values Dynamic Voltage Input Generator (TM-DV-IG), which maps
that simultaneously satisfy the constraints imposed by LUT values B(X) into multi-level WL signals by simultaneously
Equations (4) and (5) achieve optimal area reduction across exploiting both the voltage and time domains. The WL input is
LUT, decoder, and TG-MUX components, as mathematically encoded as a dynamic voltage pulse whose amplitude and width
formulated by: jointly determine the BL charging process, thus distributing
G ∗ 2(cid:3013)(cid:3005) ≤ 2(cid:3041),where LD ∈ Z+ (6) information across two orthogonal domains. For a single RRAM
We designate this optimal value as LD and this value constrains cell, the BL current is proportional to the WL voltage, i.e.,
the data range to the interval [0, G*2LD-1]. Fig. 5 depicts the 𝐼[𝑥]∝𝑓(𝑉[𝑥]),𝑥 ∈[0, 2(cid:3015)−1] , where 𝑓 denotes the
hardware architecture and dataflow for B(X) lookup operations MOSFET transfer function; when this current flows for a
following ASP-KAN-HAQ optimization. Please note that Fig. duration 𝑡 =𝑊[𝑥], the accumulated charge becomes 𝑄 =𝐼[𝑥]∙
5 presents a high-level architectural diagram. As shown in Fig. 𝑊[𝑥]. By carefully designing the DAC output voltages V[ 2(cid:3015)−
6, during actual implementation, when the Quant Grid is even 1: 0] such that the current ratios
numbered, the entire LUT can be partitioned into two halves for satisfy 𝐼[0]:𝐼[1]:𝐼[2]…:𝐼[2(cid:3015)−1]=0:1:2:…:2(cid:3015)−1 , the
mutual sharing. When the Quant Grid is odd numbered, all unit interval of charge is defined as 𝑊 ∙𝐼[1], which enables a
(cid:3017)(cid:2869)
LUTs remain shareable except for the central LUT. Since only linear distribution of charge values Q across all bit combinations.
a single LUT cannot be shared, the additional overhead incurred Compared with pure voltage input methods, this hybrid
by odd numbered Quant Grids is negligible. Fig. 7 shows the approach enhances tolerance to noise and device variation,
efficient lookup process wherein multiple Xi values share a while compared with pure PWM schemes, it avoids long pulses
single SH-LUT, facilitating the transfer of corresponding LUT and maintains high operation speed (>100 MHz), thereby
values (B (Xi) ) from local to global scope, which are enabling multi-bit MAC execution within a single clock cycle.
0~7-global LV
subsequently propagated to the input generator. The TM-DV-IG is composed of five major components: a
Delay Chain, a Pulse Modulation and Timing Control Module
3.2 N:1 Time Modulation Dynamic Voltage Input Generator
(PM-TCM), an N-bit DAC, a Transmission-Gate Multiplexer
for ACIM for ∑ci' Bi(X)
(TG-MUX), and a Buffer Array, as illustrated in Fig. 8. The PM-
In conventional CIM architectures, multi-bit WL input TCL not only generates the control signals for buffer array
methods are typically realized through either pure voltage voltage switching but also works with the delay chain to
modulation [18][19] or pure pulse-width modulation (PWM) generate ratioed pulses W , W , and W with timing
P1 PN P(N+1)
[20][21]. Voltage modulation encodes WL weights directly into proportions of 1: 2N: 2N+1. This design eliminates the need for
different amplitude levels, but the voltage interval between counter-based digital logic, thereby saving area. The N-bit DAC
adjacent levels becomes narrow as the bit resolution increases,

6
Fig. 8. N:1 Time Modulation Dynamic Voltage input
generator for ACIM.
Fig. 6. The hardware architecture with efficient LUT
retrieval process.
Fig. 7. The hardware architecture with efficient LUT
retrieval process.
Fig. 9. (a) BL linear Q value generation theory (b) 3-3 bit
produces 2N distinct fixed voltage levels, which are selectively
input vector scheme for high accuracy application; (c) 4-
connected to the buffer array through the TG-MUX under
4 bit input vector schemes for high speed application
control of PM-TCM pulses. The PM-TCM arranges these pulses
to drive the TG-MUX switches so that different supply voltages IG, where the lower 4 bits control the W pulse voltage
P1
V[ 2(cid:3015)−1: 0] are dynamically assigned to the buffer array modulation (V[a]) and the upper 4 bits control the W pulse
P3
according to the required LUT mapping. Meanwhile, the 2N+1 voltage modulation (V[b]). The resulting WL[0] input is the
ratio pulse is applied directly to the buffer array, whose outputs combined dynamic voltage pulse of V[a] and V[b], producing
are connected to the WLs. During read operation, the PM-TCM an effective output voltage V on the sampling capacitor. This
out
first receives the 2N-bit input vector, consults the LUT to configuration yields 8×8=64 distinct voltage states,
determine the required pulse-voltage combination, and then enabling dense encoding. In contrast, in the high-accuracy mode
generates the corresponding WL input waveform. On the BL (TD-A), as shown in Fig. 9(c) with N=3, the design provides
side as shown in Fig.9 (a), a clamping circuit holds the BL finer charge resolution for precision-critical tasks. This
voltage at a reference level V clamp . In idle mode, precharge adaptability, together with the dual-domain encoding principle,
transistors initialize the capacitor to VDD; in read mode, makes TM-DV-IG a scalable and efficient solution for next-
different combinations of WL voltage and pulse duration generation multi-bit CIM arrays. For further optimization by co-
discharge the capacitor with distinct currents, producing unique design ability, we can also optimize the N value for different
charge levels Q. These charge differences are then sensed by the high-performance (TD-P) and high-accuracy (TD-A)
sense amplifier (SA), realizing a linear and robust mapping of requirements.
digital inputs to analog charge values. Importantly, the TM-DV-
IG supports circuit reusability across multiple WLs, allowing 3.3 KAN sparsity-aware weight mapping for ci’
most peripheral blocks to be shared and thereby minimizing area The parasitic resistance in BLs causes IR-drop, introducing
overhead. Furthermore, by adjusting the design parameter N, the computational errors during current-based summation in
architecture can be flexibly optimized for different operating RRAM-ACIM’s MAC operations, with consequent degradation
modes. In the high-performance mode (TD-P), as illustrated in of inference precision. While prior research [14] has attempted
Fig. 9(b) with N=4, throughput is prioritized: during the positive to address this challenge, existing solutions necessitate either
half clock cycle, an 8-bit input vector is applied to the TM-DV- supplementary circuit components or constraints on maximum

Fig. 10. KAN sparsity-aware weight mapping. Fig. 11. KAN-NeuroSim hyperparameter optimization
framework.
array dimensions. The proposed KAN sparsity-aware weight inference, slices are combined by shift-and-add, so we only
mapping technique (KAN-SAM) circumvents these limitations optimize rows (distance), not columns. Phase C: For each
by operating within existing hardware and algorithmic coefficient, we build a score that favors three things: (i) bases
frameworks without requiring architectural modifications. that fire more often, (ii) bases that are stronger on average, and
The inherent characteristics of B(X) functions within KAN (iii) bases that are stable (low relative variability). Stability is
architectures dictate that only a subset of B(X) functions activate derived from the coefficient of variation (standard deviation
for any specific input value. In configurations where K=3, over mean) with a small numerical guard; then softly squashed
concurrent activation is limited to four B(X) functions. Through to a 0~1 weight so unstable bases are de-emphasized without
analysis of input probability distributions across data ranges, the hard thresholds. A tunable mix combines “expected contribution”
B(X) functions exhibiting maximum activation likelihood can and “stability” into a single criticality score. Row mapping
be identified, designated as B_H(X). Similarly, functions with policy: Sort coefficients by the criticality score (high→low) and
minimal activation probability are denoted as B_L(X). The ci' assign rows from nearest to farthest using a precomputed order.
coefficients associated with B_H(X) are strategically allocated IR-drop grows with distance along the bit-line; giving the
to RRAM cells positioned proximate to BL clamping circuitry, closest rows to the most impactful and stable coefficients
preserving computational precision for frequently occurring reduces analog error where it matters most.
inputs. In contrast, ci' coefficients linked to B_L(X) are assigned
3.4 KAN-NeuroSim hyperparameter optimization framework
to cells at greater distances from clamping circuits, thus
enhancing aggregate inference accuracy through probability- Section 3.1 presented the B(X) lookup optimization achieved
aware spatial optimization. through ASP-KAN-HAQ, which yields distinct LD values
Diverse applications and model architectures demonstrate corresponding to different G parameter configurations.
varying distributional characteristics. Fig. 10 exemplifies the However, a systematic methodology for identifying optimal G
KAN-SAM methodology utilizing a Gaussian distribution parameters under hardware-imposed constraints remained
paradigm. As depicted in Fig. 10, within an input domain unaddressed. Section 3.2 introduced the dual operational modes
spanning [-N, N], the centrally located Bi(X) functions exhibit of TM-DVS-IG, namely the high-performance (TD-P) and high-
maximal activation probabilities, whereas boundary-positioned accuracy (TD-A) configurations. Nonetheless, a comprehensive
Bi(X) functions demonstrate minimal triggering likelihood. analytical framework for evaluating the respective impacts of
Therefore, the allocation of central ci' parameters (associated TD-P and TD-A modes on system-level performance metrics
with B_H(X)) to RRAM cells adjacent to clamping circuits, has not been established, limiting the ability to guide mode
coupled with the assignment of peripheral ci' parameters (linked selection based on application-specific requirements.
to B_L(X)) to cells at increased distances, optimizes system- To overcome these constraints, the KAN-NeuroSim
level inference precision. This mapping strategy remains hyperparameter optimization framework is proposed, as
applicable for input domains bounded by [0, N]. illustrated in Fig. 11. The framework operates through a two-
To ensure that KAN-SAM performs robustly across varying stage process. The initial stage, indicated by the brown pathway
input distributions, we introduce Algorithm 1: KAN-SAM in Fig. 11, establishes hardware specifications (energy budget,
Strategy. Phase-A: In this phase we scan the training set once. silicon area, computational latency) alongside KAN
For each basis Bi, record how often it fires (activation architectural parameters (network topology, K, and G values).
probability), its average magnitude when active, and how much These specifications are subsequently processed through an
it varies. Phase-B: Each trained coefficient becomes 8 binary extended NeuroSim implementation [17][28][29], which
slices stored on a fixed 8-column template in every row (most integrates ASP-KAN-HAQ and TM-DV-IG methodologies to
significant bit, MSB→least significant bit, LSB). During derive energy consumption, area utilization, and latency metrics.
When computed metrics violate hardware specifications, the

8
Algorithm 1 KAN-SAM-Strategy Algorithm 2 Sensitivity-based Grid Assignment for KAN-
Require: Trained KAN coefficients {𝑐(cid:4593)}(cid:3012)(cid:2878)(cid:3008)(cid:2879)(cid:2869); training set 𝐷 ; NeuroSim
(cid:3036) (cid:3036)(cid:2880)(cid:2868) train
B-spline params (𝐾,𝐺) ; crossbar with 𝑅 rows; precomputed Require: Network architecture: 𝐿 (number of layers); Grid
row order RowOrder (nearest→ farthest); hyperparameters templates 𝐺 , 𝐺 , 𝐺 ; Training parameters:
high med low
α,β∈[0,1] with α+β=1, and ε>0. warmup_epochs
Assumption: bit-sliced columns use a fixed 8-bit template Phase 1: Layer Sensitivity Profiling
across rows (MSB→LSB). 1: Initialize KAN model with uniform grid 𝐺 init
Phase A: Input-side statistics 2: Train model for warmup_epochs
1: Initialize cnt[𝑖]←0, 𝑠 [𝑖]←0, 𝑠 [𝑖]←0 for all 𝑖. 3: for 𝑖 = 1 to 𝐿 do
(cid:2869) (cid:2870) (cid:2870)
2: for all 𝑥∈𝐷 train do 4: Compute sensitivity: 𝑆 ←𝔼 (cid:4680)(cid:4678) (cid:2869) ∑(cid:3014)(cid:3284) (cid:3436) (cid:3105)ℒ (cid:3440) (cid:4679)(cid:4681)
3: 𝐴←active_B_indices(𝑥;𝐾,𝐺) (cid:3036) (cid:3049)(cid:3028)(cid:3039) (cid:3014)(cid:3284) (cid:3037)(cid:2880)(cid:2869) (cid:3105)(cid:3030)(cid:3284),(cid:3285)
4: for all {𝑖∈𝐴} do 5: end for
5: 𝑏←𝐵(𝑥) {Spline/LUT; 𝑏≥0} Phase 2: Sensitivity Classification and Grid Assignment
(cid:3036)
6: cnt[𝑖]←cnt[𝑖]+1; 𝑠 (cid:2869) [𝑖]←𝑠 (cid:2869) [𝑖]+𝑏; 𝑠 (cid:2870) [𝑖]←𝑠 (cid:2870) [𝑖]+𝑏(cid:2870) 6: Sort 𝑆=[𝑆 (cid:2869) ,𝑆 (cid:2870) ,…,𝑆 (cid:3013) ] in descending order
7: end for 7: τ ←percentile(𝑆,67) {Top 33% are high sensitivity}
high
8: end for 8: τ ←percentile(𝑆,33) {Bottom 33% are low sensitivity}
low
9: for 𝑖=0 𝑡𝑜 𝐾+𝐺−1 do 9: for 𝑖 = 1 to 𝐿 do
10: 𝑝[𝑖]←cnt[𝑖]/|𝐷 train | {Activation probability} 10: if 𝑆 (cid:3036) ≥τ high then
11: μ[𝑖]← (cid:3046)(cid:3117)[(cid:3036)] {Arithmetic mean (for CV)} 11: 𝐺 (cid:3036) ←𝐺 high {High sensitivity}
(cid:2923)(cid:2911)(cid:2934)(cnt[(cid:3036)],(cid:2869))
12: class ←``HIGH''
12: var[𝑖]← (cid:3046)(cid:3118)[(cid:3036)] −(cid:4672) (cid:3046)(cid:3117)[(cid:3036)] (cid:4673) (cid:2870) 13: else if (cid:3036) 𝑆 (cid:3036) ≥τ low then
(cid:2923)(cid:2911)(cid:2934)(cnt[(cid:3036)],(cid:2869)) (cid:2923)(cid:2911)(cid:2934)(cnt[(cid:3036)],(cid:2869))
14: 𝐺 ←𝐺 {Medium sensitivity}
13: end for (cid:3036) med
15: 𝑐𝑙𝑎𝑠𝑠 ←``MEDIUM''
Phase B: Quantization and bit vectors (cid:3036)
16: else
14: for 𝑖=0 𝑡𝑜 𝐾+𝐺−1 do
17: 𝐺 ←𝐺 {Low sensitivity}
15: 𝑏 ←(cid:3427)𝑏 ,…,𝑏 (cid:3431)∈{0,1}(cid:2876) {8-bit slices} (cid:3036) low
(cid:3036) (cid:3036),(cid:2875) (cid:3036),(cid:2868) 18: 𝑐𝑙𝑎𝑠𝑠 ←``LOW''
16: (cid:3627)𝑐 (cid:3036) ′(cid:3627) (cid:3018) ←∑(cid:2875) (cid:2921)(cid:2880)(cid:2868) b (cid:2919),(cid:2921) 2(cid:2921) {Digital magnitude} 19: end if (cid:3036)
17: end for 20: end for
Phase C: Coefficient criticality (CV-based stability) 21: return 𝐺∗=[𝐺 (cid:2869) ,𝐺 (cid:2870) ,…,𝐺 (cid:3013) ]
18: for 𝑖=0 𝑡𝑜 𝐾+𝐺−1 do To enable users to achieve better performance under limited
19: σ[𝑖]←(cid:3493)var[𝑖]; CV[𝑖]← (cid:2978)[(cid:3036)] hardware constraints, we introduce Algorithm 2: Sensitivity-
(cid:2972)[(cid:3036)](cid:2878)(cid:2965)
20: 𝑆[𝑖]← (cid:2869) ∈(0,1] {Monotone squashing of CV} based Grid Assignment for KAN-NeuroSim. This strategy
(cid:2869)(cid:2878)CV[(cid:3036)] allows users to allocate larger G values to regions of the network
21: 𝐽[𝑖]←𝑝[𝑖]∙𝜇[𝑖]∙|𝑐(cid:4593)| {Expected contribution}
(cid:3036) (cid:3018) that exhibit higher sensitivity in order to preserve accuracy,
22: 𝐶 [𝑖]←𝛼𝐽[𝑖]+𝛽𝑆[𝑖]∙𝐽[𝑖]
(cid:3050) while assigning smaller G values to less sensitive regions to
23: end for
Row mapping policy reduce hardware requirements. The algorithm operates in two
24: Sort 𝑖 by 𝐶_𝑤[𝑖] (ℎ𝑖𝑔ℎ→low) to obtain 𝑄; assign phases. First, during a warmup training period, we profile each
𝑄[1],𝑄[2],… to rows from nearest to farthest using layer's sensitivity by computing the gradient. This sensitivity
RowOrder.
metric quantifies the degree of sensitivity for each region. In the
framework iteratively adjusts either the constraint parameters or
second phase, layers are classified into three sensitivity tiers
KAN hyperparameters until compliance is achieved. Following
based on percentile thresholds. High sensitivity layers (top 33%)
successful constraint satisfaction, the secondary stage employs
are assigned G , as they require finer grid resolution for
the grid extension methodology established in the original KAN high
accurate feature extraction. Medium sensitivity layers (middle
literature to enhance computational accuracy. Throughout the
34%) receive G , while low sensitivity layers (bottom 33%)
training procedure, grid expansion occurs at N-epoch intervals. med
operate efficiently with G . This heterogeneous assignment
The parameter G undergoes incremental augmentation by a low
ensures that computational resources are allocated where they
user-specified value E, contingent upon sustained validation
provide the most benefit. Following the sensitivity-based grid
loss reduction and compliance with hardware resource
assignment, KAN-NeuroSim implements a two-step
boundaries as determined through NeuroSim evaluation. When
optimization process as shown in Fig. 11. It should be noted that
these criteria are not satisfied, the grid extension process is
users may autonomously determine the granularity of grid
terminated, with the system reverting to the preceding G
pre
templates. Three grid resolution levels—namely G , G , and
configuration. The framework incorporates RRAM non-ideality high med
G —are utilized here as examples, and variable grid
factors, particularly partial sum error characteristics, derived low
resolutions can be assigned within the same layer based on
from statistical measurements conducted on TSMC 22nm
sensitivity requirements.
RRAM-ACIM prototype chip. This integration guarantees that
the resulting KAN hyperparameters deliver optimized hardware
performance and inference accuracy when deployed on RRAM-
4 EVALUATION RESULTS
ACIM systems.

Fig.14. WL input methods performance comparison with
SPICE simulation at 22 nm for N=1 2-bit vector input
scheme.
Fig. 12. Comparison of Normalized Area between proposed
ASP-KAN-HAQ and conventional method based on Post-
Training Quantization [29] using NVIDIA's TensorRT
framework .
Fig.15. WL input methods performance comparison with
SPICE simulation at 22 nm for N=2 4-bit vector input
scheme.
B(X) value retrieval, to its delivery to the input generator. The
evaluation encompasses various precision levels ranging from
4-bit to 8-bit quantization, with 8-bit selected as the optimal
trade-off between accuracy and hardware efficiency. Fig. 12
Fig. 13. Comparison of Normalized Energy Consumption and Fig. 13 illustrate the efficacy of our approach. With G
between proposed ASP-KAN-HAQ and conventional
scaling from 8 to 64, our method exhibits substantial
method based on Post-Training Quantization [29] using
advantages over conventional techniques, delivering an
NVIDIA's TensorRT framework.
average area reduction of 40.14× and an average energy
A. ASP-KAN-HAQ
reduction of 5.74×. Specifically, at G=8, our method achieves
We utilize a large-scale task [23] for evaluating ASP-KAN-
33.97× area reduction and 7.12× energy savings, while at G=64,
HAQ, employing the CF-KAN architecture—an encoder-
these improvements scale to 44.24× and 4.67× respectively. The
decoder framework based on KAN designed for
energy efficiency gains are primarily attributed to simplify
recommendation systems. As outlined in Section 3.1, the
decoder structure and the LUT reduction achieved by the
parameter G serves as a key factor in ASP-KAN-HAQ. To
proposed SH-LUT architecture. This can be attributed to
systematically evaluate our method's scalability across more
inherent constraints in conventional quantization approaches,
complex KAN architectures with arbitrary G values, we
wherein non-zero offsets between quantization and knot grids
progressively increased G using the grid extension approach, a
hinder the ability to share LUTs across different B(X) values. In
methodology established by the original KAN paper authors.
contrast, our approach enables all B(X) values to utilize a
Our experimental setup utilized TSMC 22nm technology node
unified LUT while separating local and global information,
parameters. The evaluation environment incorporated detailed
thereby reducing TG-MUX and decoder areas and maintaining
circuit-level simulations using SPICE for accurate power and
KAN scalability at the edge through ASP-KAN-HAQ.
timing analysis, while area estimations were derived from
synthesized netlists. We evaluated ASP-KAN-HAQ against
B. N:1 Time Modulation Dynamic Voltage input generator
conventional quantization approaches [15][16] with respect to
To quantitatively evaluate the benefits of the proposed N:1
energy and area metrics at the 22nm technology node. For this
TM-DV-IG for KAN accelerator implementation, we compared
study, Post-Training Quantization [29] implemented via
its performance against conventional pure voltage and pure
NVIDIA's TensorRT framework served as our comparison
PWM input schemes across multiple WL resolutions, as shown
baseline. To isolate variables, we concentrated our analysis on
in Fig. 14–17. Benchmark simulations were performed for N=1-
the hardware pathway from the input X, through LUT-based

10
Fig.16. WL input methods performance comparison with
SPICE simulation at 22 nm for N=3 3-bit vector input scheme.
Fig. 18. Comparison of accuracy degradation from KAN
software baseline across different RRAM array sizes
(As.). The statistics of measured RRAM-ACIM chips
[13] are used.
Fig.17. WL input methods performance comparison with
SPICE simulation at 22 nm for N=4 8-bit vector input
scheme.
4, which means 2-, 4-, 6-, and 8-bit input vectors, corresponding
to 22, 24, 26, and 28 distinct WL pulses for BL sampling,
respectively. For fair comparison, the unit pulse width was
assigned identically to all three methods, as illustrated in Fig.
8(b) and (c). The evaluation was conducted in a 22 nm
technology node, and all circuit modules were validated at the
transistor level using SPICE. The results reveal distinct trade-
offs across the three methods. In the 2-bit input case (Fig. 14),
Fig. 19. Comparison of proposed KAN accelerator with
the pure voltage scheme achieves the best figure-of-merit
previous work across small-scale and large-scale
(FOM) due to its minimal latency, while PWM provides
computational tasks.
superior power efficiency. The TM-DV-IG in this low-
pure PWM. In the 8-bit scheme (N=4), an 8-bit input vector is
resolution case exhibits the lowest FOM, primarily due to its
directly applied to the WL as shown in Fig.17, and TM-DV-IG
relatively redundant circuit structure. However, when the input
continues to demonstrate significant FOM improvements over
resolution increases (N>1, i.e., 4-, 6-, and 8-bit vectors), the
both conventional approaches. These results confirm that the
advantages of TM-DV-IG become increasingly evident. For the
proposed TM-DV-IG effectively balances latency, area, and
6-bit scheme (N=3), although the pure voltage method still
power, making it a scalable and efficient enabler for KAN
achieves the lowest latency, it requires a high-resolution DAC,
algorithm implementation on RRAM-based CIM architectures.
which reduces noise margin and incurs significant static power
consumption. Specifically, it suffers from a 1.96× area overhead
C. KAN sparsity-aware weight mapping
and an 11.9× power overhead compared with TM-DV-IG. The
We estimated the IR-drop issue and evaluated the proposed
pure PWM method shows the poorest performance, exhibiting
KAN-SAM architecture. The IR-drop phenomenon in RRAM-
an 8× latency overhead and a 1.07× area overhead due to the
ACIM systems occurs when multiple cells along a bit-line are
long delay chain requirement. In contrast, TM-DV-IG, by
activated simultaneously, causing voltage degradation that
combining voltage and timing modulation, avoids the noise
directly impacts computation accuracy. Firstly, we refer to
margin limitations of the high-bit DAC and the excessive timing
TSMC’s 22 nm RRAM-ACIM chip measurement results [13] of
overhead of PWM, thereby achieving superior overall efficiency.
the single BL IR drop effect in array sizes ranging from 128 to
When all three metrics—area, power, and latency—are jointly
1024. These measurements provide empirical validation of the
considered, TM-DV-IG delivers the highest FOM once 𝑁>1. In
voltage drop characteristics under different array configurations,
the 6-bit configuration as shown in Fig.16, it achieves 3×
establishing a reliable foundation for our error modeling.
improvement over pure voltage and 4.1× improvement over

Secondly, MAC error rates induced by IR-drop were extracted to: 1) ASP-KAN-HAQ's reduction in energy consumption, 2)
from TSMC's 22 nm RRAM-ACIM chips, which were our highly integrated system leveraging the high-performance
subsequently used to train four CF-KAN models in PyTorch, parallel computing capabilities of RRAM-ACIM, and 3) TM-
employing G values of 7, 15, 30, and 60 that correspond to array DV-IG achieving optimal trade-offs among accuracy, energy
dimensions of 128, 256, 512, and 1024, respectively. The choice consumption, latency, and area. Therefore, this work maintains
of these specific G values ensures comprehensive coverage of high efficiency even in large-scale applications with extremely
practical RRAM array dimensions. high parameter counts.
The baseline approach applied uniform mapping of different
ci' values to RRAM-ACIM without accounting for Bi(X) 5 Conclusion
activation probabilities. Through the integration of extracted This work introduces an innovative hardware acceleration
MAC error rates and variable Bi(X) activation probabilities, we methodology for KAN through algorithm-hardware co-design.
evaluated the influence of KAN-SAM on accuracy performance. The proposed algorithmic and circuit-level innovations
Our sparsity-aware mapping strategy strategically places effectively minimize hardware overhead, power consumption,
weights with higher activation probabilities in array positions and maintain inference accuracy for resource-constrained edge
less susceptible to IR-drop effects, effectively minimizing the computing applications. To the best of our knowledge, this work
overall computational error. Fig. 18 illustrates that with array represents the first validation of large-scale tasks on KAN
dimensions increasing from 128 to 1024, KAN-SAM achieves accelerators. Evaluation results demonstrate that, compared to
accuracy enhancements ranging from 2.83× to 5.31×. This previous work operating on tiny tasks, despite the parameter
progressive improvement underscores KAN-SAM's capability count for large-scale tasks in this work increasing by 500K× to
in improving the scalability of RRAM-ACIM systems. 807K×, the area overhead increases by only 28K× to 41K×,
while power consumption increases by merely 51× to 97×, with
D. KAN-NeuroSim hyperparameter optimization framework accuracy degradation remaining minimal at 0.11% to 0.23%,
We employed KAN-NeuroSim within a PyTorch environment thereby showcasing the exceptional scaling capability of our
to optimize the G value for KAN architecture under various proposed architecture.
hardware constraints for large-scale recommendation system
tasks, utilizing the Anime dataset for our analysis. In this study, 6 References
we explored two architectures respectively targeting high [1] S. Pouyanfar et al., “A survey on deep learning: Algorithms, techniques,
and applications,” ACM Computing Surveys, 2019.
performance mode (CF-KAN-1) and high accuracy mode (CF-
[2] W. X. Zhao et al, “A survey of large language models,” arXiv:2303.18223,
KAN-2). When searching for optimal parameters for high
2023.
performance, we implemented Algorithm 2, a Sensitivity-based [3] Z. Liu et al., “KAN: Kolmogorov-Arnold Networks,” arXiv:2404.19756,
Grid Assignment strategy for KAN-NeuroSim, ensuring 2024.
minimal Grid utilization in non-sensitive regions to enhance [4] A.N. Kolmogorov, “On the representation of continuous functions of
several variables as superpositions of continuous functions of a smaller
hardware performance, while allocating additional Grid
number of variables,” Dokl. Akad. Nauk, 108(2), 1956.
resources in sensitive regions to prevent significant accuracy [5] A.N. Kolmogorov, “On the representation of continuous functions of
degradation. Furthermore, we deployed TM-DV-IG's TD-P many variables by superposition of continuous functions of one variable
and addition,” Dokl. Akad. Nauk, Vol. 114. 953–956, 1957.
mode in non-sensitive regions to reduce latency and energy
[6] C. J Vaca-Rubio et al., “Kolmogorov-arnold networks (kans) for time
consumption, while employing TD-A mode in sensitive regions series analysis,” arXiv:2405.08790, 2024.
to maintain high accuracy when executing complex large-scale [7] W. J Gordon et al., “B-spline curves and surfaces,” Computer Aided
tasks. Regarding the high accuracy mode (CF-KAN-2), Geometric Design, pages 95–126. Elsevier, 1974.
[8] S. Yu et al., “Compute-in-Memory chips for deep learning: Recent trends
Algorithm 2 was disabled to ensure optimal accuracy, with the
and prospects,” IEEE Circuits and Systems Magazine, vol. 21, pp. 31-56,
entire network utilizing Ghigh and operating in TD-A mode to 2021.
guarantee maximum accuracy. Fig. 19 demonstrates the [9] Y.-D. Chih et al., “An 89 TOPS/W and 16.3 TOPS/mm2 alldigital SRAM-
performance of this work, showing energy consumption of based full-precision compute-in memory macro in 22 nm for machine-
learning edge applications,” IEEE International Solid-State Circuits
289.6 nJ and 645.9 nJ for large-scale tasks with parameter Conference (ISSCC), 2021.
counts of 39 MB and 63 MB, respectively, with corresponding [10] X. Si et al., “A Local Computing Cell and 6T SRAM-Based Computing-
latencies of 3648 ns and 4416 ns, while accuracy degradation in-Memory Macro With 8-b MAC Operation for Edge AI Chips,” IEEE
Journal of Solid-State Circuits (JSSC), vol. 56, no. 9, pp. 2817- 2831, 2021.
remained minimal at only 0.23% and 0.11%.
[11] J.-W. Su et al., “A 8-b-Precision 6T SRAM Computing-in-Memory Macro
Compared to previous work operating exclusively on tiny-scale Using Segmented-Bitline Charge-Sharing Scheme for AI Edge Chips,”
tasks, CF-KAN-1 and CF-KAN-2 have parameter counts 500K IEEE Journal of Solid-State Circuits (JSSC), vol. 57, no. 2, pp. 609–624,
2022.
and 807K times larger than [27], yet the area increased by only
[12] C.-X. Xue et al., “A 1 Mb multibit ReRAM computing-in-memory macro
28K and 41K times, respectively. This is attributed to our with 14.6 ns parallel MAC computing time for CNN based AI edge
efficient ASP-KAN-HAQ, which significantly reduces the processors,” IEEE International Solid-State Circuits Conference (ISSCC),
2019.
hardware resources required for LUTs. On the other hand,
[13] W.-H. Huang et al., “A nonvolatile Al-edge processor with 4MB SLC-
power consumption increased by 51× and 94×, respectively, due
MLC hybrid-mode ReRAM compute-in-memory macro and 51.4-

12
251TOPS/W,” IEEE International Solid-State Circuits Conference Jianwei Jia received the B.S. degree in
(ISSCC), 2023.
Microelectronics Science and Engineering from
[14] B. Liu et al., “Reduction and IR-drop compensations techniques for
Nankai University, Tianjin, China, in 2021, and
reliable neuromorphic computing systems,” IEEE/ACM International
Conference on Computer-Aided Design (ICCAD), 2014. the M.S. degree in Electrical and Computer
[15] A. Gholami et al., “A survey of quantization methods for efficient neural Engineering from the University of Michigan,
network inference,” arXiv:2103.13630, 2021.
Ann Arbor, MI, USA, in 2023. He is currently pursuing the
[16] B. Rokh et al., “A comprehensive survey on model quantization for deep
neural networks in image classification,” ACM Trans. Intell. Syst. Ph.D. degree at the Georgia Institute of Technology, Atlanta,
Technol., vol. 14, no. 6, pp. 1–50, Dec. 2023. GA, USA.
[17] X. Peng et al., “DNN+NeuroSim: An end-to-end benchmarking
framework for compute-in-memory accelerators with versatile device
technologies,” IEEE International Electron Devices Meeting (IEDM),
2019. Yuyao Kong received the B.S. degree from
[18] Z. Jiang et al., “C3SRAM: An In-Memory-Computing SRAM Macro Nanjing Tech University, Nanjing, China, in
Based on Robust Capacitive Coupling Computing Mechanism,” IEEE
2015, the M.S. degree from the University of
Journal of Solid-State Circuits (JSSC), vol. 55, no. 7, pp. 1888-1897, 2020.
[19] A. Biswas et al., “Conv-RAM: An energy-efficient SRAM with embedded Southampton, Southampton, U.K., in 2016, and
convolution computation for low-power CNN-based machine learning the Ph.D. degree from the School of Electronic
applications,” IEEE International Solid-State Circuits Conference
Science and Engineering, Southeast University, Nanjing, China,
(ISSCC), 2018.
in 2023. He is currently a Postdoctoral Fellow with the
[20] Q. Dong et al., “15.3 A 351TOPS/W and 372.4GOPS Compute-in-
Memory SRAM Macro in 7nm FinFET CMOS for Machine-Learning Laboratory for Emerging Devices and Circuits, Georgia
Applications,” IEEE International Solid-State Circuits Conference
Institute of Technology, advised by Prof. Shimeng Yu. His
(ISSCC), 2020.
research interests include compute-in-memory (CIM)-based
[21] S. K. Gonugondla et al., “A 42pJ/decision 3.12TOPS/W robust in-memory
machine learning classifier with on-chip training,” IEEE International algorithm-hardware co-design targeting AI processors and
Solid-State Circuits Conference (ISSCC), 2018.
probabilistic computing, as well as low-voltage SRAM and
[22] A. Davies et al. “Advancing mathematics by guiding human intuition with
other energy-efficient circuit designs.
ai,” Nature, 600(7887):70–74, 2021.
[23] Jin-Duk Park et al., “CF-KAN: Kolmogorov Arnold network-based
collaborative filtering to mitigate catastrophic forgetting in recommender Faaiq Waqar received a B.S. degree in computer
systems,” arXiv:2409.05878, 2024.
science and electrical & computer engineering
[24] W.-H. Huang et al., “Hardware acceleration of Kolmogorov-Arnold
from Oregon State University, Corvallis, OR, in
network (KAN) for lightweight edge inference,” Asia and South Pacific
Design Automation Conference (ASPDAC), 2025. 2022. He is currently pursuing a Ph.D. in
[25] C. Sudarshan et al., “A Kolmogorov–Arnold Compute-in-Memory (KA- electrical & computer engineering from the
CIM) Hardware Accelerator with High Energy Efficiency and Flexibility,”
Georgia Institute of Technology, Atlanta, GA. Prior to joining
Research Square, preprint, 2025. Available:
https://www.researchsquare.com/article/rs-5804189/v1. Georgia Tech, he worked as a hardware engineer for Microsoft’s
[26] P. Duarte et al., “Function Approximation Using Analog Building Blocks Silicon Engineering Solutions team. He was the recipient of the
in Flexible Electronics,” International Symposium on Quality Electronic
NSF Graduate Research Fellowship and the Georgia Tech
Design (ISQED), 2025.
President’s Fellowship in 2023. His current research interests
[27] K. Hu et al., “SCKAN: A Stochastic Computing-Based Accelerator for
Efficient Implementation of Kolmogorov-Arnold Networks,” TechRxiv , pertain to the modeling and metrology of emerging amorphous
preprint, 2024. Available:
oxide semiconductor and ferroelectric devices for applications
https://www.techrxiv.org/users/830901/articles/1224596-sckan-a-
stochastic-computing-based-accelerator-for-efficient-implementation-of- in neuromorphic, reconfigurable, and high-performance
kolmogorov-arnold-networks. computational systems.
[28] J. Lee et al., “NeuroSim V1.4: Extending Technology Support for Digital
Compute-in-Memory Toward 1nm Node,” IEEE Transactions on Circuits
and Systems I: Regular Papers, 2024, Tai-Hao Wen (Member, IEEE) received the B.S.
[29] J. Read et al., “NeuroSim V1.5: Improved Software Backbone for degree in electrical engineering from National
Benchmarking Compute-in-Memory Accelerators with Device and Tsing Hua University, Hsinchu, Taiwan, in 2020,
Circuit-level Non-idealities,” arXiv:2505.02314, 2025.
and the Ph.D. degree in electrical engineering
from National Tsing Hua University, Hsinchu,
Wei-Hsing Huang received the B.S. degree in
Taiwan, in 2024. He is currently a Postdoctoral Research Fellow
electrical engineering from the National Chung
with the Department of Electrical and Computer Engineering,
Cheng University, Chiayi, Taiwan, in 2017, and
University of Michigan, Ann Arbor, USA. His research interests
the M.S. degree in electrical engineering and
include memory circuit design and compute-in-memory for
computer science from the National Tsing Hua
emerging nonvolatile memories, as well as hardware-efficient
University, Hsinchu, Taiwan, in 2019. He is currently a
system design.
Research Assistant in electrical and computer engineering with
Georgia Institute of Technology, Atlanta, GA, USA. His current
research interests include deep learning algorithms and
algorithm-hardware co-design for deep learning.

Meng-Fan Chang received the M.S. degree from
The Pennsylvania State University, State
College, PA, USA, and the Ph.D. from the
National Chiao Tung University, Hsinchu,
Taiwan. Prior to 2006, he worked in the industry
for over ten years. This included the design of
memory compilers (Mentor Graphics, Wilsonville, OR, USA,
from 1996 to 1997) and the design of embedded SRAM and
Flash macros (Design Service Division, TSMC, Hsinchu, From
1997 to 2001). In 2001, he co-founded IPLib, Hsinchu, where
he developed embedded SRAM and ROM compilers, flash
macros, and flat-cell ROM products, until 2006. He is currently
a Distinguished Professor at the National Tsing Hua University
(NTHU) and the Director of Corporate Research, TSMC. His
research interests include circuit design for volatile and
nonvolatile memory, ultralow-voltage systems, 3-D memory,
circuitdevice interactions, spintronic circuits, memristor logics
for neuromorphic computing, and computing-in-memory for
artificial intelligence.
Shimeng Yu (Fellow, IEEE) is a full professor
of electrical and computer engineering at
Georgia Institute of Technology, where he
holds the Dean’s Professorship. He received the
B.S. degree in microelectronics from Peking
University in 2009, and the M.S. degree and Ph.D. degree in
electrical engineering from Stanford University in 2011 and
2013, respectively. From 2013 to 2018, he was an assistant
professor at Arizona State University. He is elevated for the
IEEE Fellow for contributions to non-volatile memories and in-
memory computing. His general research interests are
semiconductor devices and integrated circuits for energy-
efficient computing systems. His expertise is on the emerging
non-volatile memories for AI hardware and 3D integration.
Prof. Yu’s 400+ journal/conference publications received more
than 30,000 citations with H-index 82. He is the theme lead of
two SRC/DARPA JUMP 2.0 centers on intelligent
memory/storage and heterogeneous/monolithic 3D integration.

