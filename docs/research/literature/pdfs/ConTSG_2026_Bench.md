ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

arXiv:2603.04767v1 [cs.LG] 5 Mar 2026

Shaocheng Lan 1 Shuqi Gu 1 Zhangzhi Xiong 1 Kan Ren 1

Abstract
Conditional time series generation plays a critical role in addressing data scarcity and enabling causal analysis in real-world applications. Despite its increasing importance, the field lacks a standardized and systematic benchmarking framework for evaluating generative models across diverse conditions. To address this gap, we introduce the Conditional Time Series Generation Benchmark (ConTSG-Bench). ConTSG-Bench comprises a large-scale, well-aligned dataset spanning diverse conditioning modalities and levels of semantic abstraction, first enabling systematic evaluation of representative generation methods across these dimensions with a comprehensive suite of metrics for generation fidelity and condition adherence. Both the quantitative benchmarking and in-depth analyses of conditional generation behaviors have revealed the traits and limitations of the current approaches, highlighting critical challenges and promising research directions, particularly with respect to precise structural controllability and downstream task utility under complex conditions. We have open-sourced ConTSG-Bench at Github.
1. Introduction
Conditional time series generation (ConTSG) has emerged as a transformative capability for scientific and industrial advancement. Its application spans from realistic data simulation for healthcare and climate applications (Lai et al., 2025b; Lu et al., 2024; Narasimhan et al., 2024), causal inference (Xia et al., 2025), to privacy-preserving data synthesis (Liu et al., 2025). While unconditional generation has seen significant progress (Pei et al., 2021; Desai et al., 2021; Jeon et al., 2022) with established benchmarks for fidelity and diversity (Ang et al., 2023), the research frontier has shifted toward controllable synthesis: the ability to
1School of Information Science and Technology, ShanghaiTech University, Shanghai, China. Correspondence to: Kan Ren <renkan@shanghaitech.edu.cn>.
Preprint. March 6, 2026.

Modality

Text Variate 0 is a generally increasing trend with...
Condition

Attribute

Attribute Value

trend

up

......

......

Conditional Generator

Class Label

0

 



 

1

 



 

0

Time Series

Semantic Abstraction

Morphological
Variate 0 is a generally increasing trend with moderate volatility and no clear periodicity...

Conceptual
The current weather is clear...The humidity levels are dropping but remain high.

Figure 1. Conditional time series generation with varying conditioning modalities (text, attribute, class label) and semantic abstraction levels (morphological vs. conceptual).

generate high-fidelity time series data that strictly adheres to user-defined, multimodal conditions.
However, the landscape of ConTSG remains highly fragmented, hindering algorithmic innovation and practically effective model development. Current methodologies are isolated by their specific conditioning modalities: some rely on discrete class labels (Lee et al., 2023), others on structured attributes (Narasimhan et al., 2024), and recent works have begun exploring natural language descriptions (Gu et al., 2025). These models are typically evaluated on incompatible datasets with different condition modalities, making it infeasible to systematically compare conditional generation effectiveness or relative model performance.
Furthermore, evaluations in prior works overlook critical capabilities required for robust real-world deployment of ConTSG models. The primary dimension involves the semantic abstraction of conditions (Figure 1): while some methods specify target morphology directly (Dohi et al., 2025) (e.g., specify volatility and periodicity), others describe high-level concepts (Wagner et al., 2020) (e.g., weather conditions). The latter requires models to autonomously infer corresponding temporal patterns from abstract semantics, which is significantly more challenging. Beyond semantic abstraction level, practical simulation demands fine-grained controllability to execute precise local constraints, which is often obscured by aggregate global metrics (Williams et al., 2025). Finally, true robustness necessitates compositional generalization, ensuring models can synthesize time series

1

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

underlying novel conditions, e.g., attribute combinations that are absent from the training distribution (Jing et al., 2024). As current evaluations typically isolate these factors under single-modality settings, the resulting performance landscape of ConTSG models remains incomplete.
To resolve these critical gaps, we introduce ConTSGBench, a unified evaluation benchmark for conditional time series generation. Our benchmark is the first to systematically disentangle condition types along two axes (Figure 1): modality (class label, attribute, text) and semantic abstraction level (morphology, concept). We curate a series of large-scale datasets featuring aligned conditions across all three modalities, including dual-level annotations for selected subsets to enable controlled cross-abstraction comparisons. Furthermore, ConTSG-Bench provides a unified evaluation suite that jointly assesses fidelity, condition adherence, fine-grained control, compositional generalization and downstream utility, allowing model behaviors to be characterized along multiple practically relevant dimensions.
Leveraging this framework, we conduct a rigorous evaluation of representative models, yielding several pivotal insights. For instance, we observe that text-conditioned models achieve the highest performance ceiling yet exhibit significant variance across architectures. Notably, current generators universally struggle with precise fine-grained control and compositional generalization, suggesting that existing methods may lack the structural inductive biases or algorithmic innovation necessary for complex real-world synthesis.
In summary, our contributions are summarized as follows:
· A Unified Benchmarking Framework: We establish the first systematic evaluation protocol for conditional time series generation, covering diverse condition types and multi-faceted metrics for fidelity and condition adherence.
· Multimodal Aligned Datasets: We construct large-scale datasets with aligned multimodal conditions and varied semantic abstraction levels, specifically designed to address the scarcity of aligned data and enable rigorous cross-modality benchmarking.
· Systematic Evaluation and Analysis: We provide an indepth characterization of state-of-the-art models, uncovering critical bottlenecks, which may shed some light on future research in conditional time series generation. To facilitate reproducibility and future research, we will publicly release all code, datasets, and evaluation pipelines.
2. Related Works
Time Series Generation Early work on time series generation mainly focuses on unconditional synthesis, where the

goal is to model the marginal distribution of a sequence without explicit control signals. Representative approaches include Generative Adversarial Network (GAN) (Goodfellow et al., 2020) and Variational Autoencoders (VAE) (Kingma & Welling, 2019) based models such as TimeGAN (Pei et al., 2021), TimeVAE (Desai et al., 2021), and GT-GAN (Jeon et al., 2022), used for tasks like data augmentation and privacy preservation. These methods establish the basic toolkit for time series synthesis but lack mechanisms for fine-grained control over the generated trajectories.
More recently, the field has shifted towards conditional time series generation, where models are guided by auxiliary information. Label-based approaches use discrete class labels within conditional Generative Adversarial Networks (GAN) (Goodfellow et al., 2020) or Variational Auto-Encoder (VAE) (Kingma & Welling, 2019) frameworks. TTS-CGAN (Li et al., 2022) employs a Transformerbased conditional GAN with auxiliary classification, while TimeVQVAE (Lee et al., 2023) learns discrete latent codes with label-aware priors to improve fidelity.
Beyond labels, attribute-conditioned models condition on low-dimensional metadata, including categorical and continuous covariates. TimeWeaver (Narasimhan et al., 2024) leverages attention-based diffusion with heterogeneous metadata; WaveStitch (Shankar et al., 2025) employs statespace-based diffusion for tabular series with hierarchical attributes; TEdit (Jing et al., 2024) uses multi-scale patch diffusion for attribute-guided editing.
Recently, a complementary line of work explores textconditioned time series generation, using natural language as the conditioning modality. Several concurrent methods study general text-to-time-series generation with diffusionbased (Ho et al., 2020) or Transformer-based (Vaswani et al., 2017) architectures. BRIDGE (Li et al., 2025) and VerbalTS (Gu et al., 2025) propose domain-agnostic diffusionbased generators that couple text encoders with time-series backbones, with VerbalTS further introducing multi-view noise estimation and multi-focal text processing to enhance semantic alignment. T2S (Ge et al., 2025) combines flow matching with a diffusion transformer (DiT) backbone for prompt-based series generation, while Text2Motion (Guo et al., 2022) employs a latent-space autoregressive VAE originally designed for motion synthesis. DiffuSETS (Lai et al., 2025a) instead targets the medical domain, conditioning 12-lead ECG synthesis on clinical reports and patient information. Overall, conditional time series generation is moving from low-dimensional structured conditions toward flexible natural language prompts, but each method is evaluated on its own datasets, condition formats, and metrics.
Time Series Benchmark Standardized benchmarking serves as a critical foundation for advancing time series

2

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

research. Within this landscape, evaluation frameworks for forecasting are comparatively mature. TSLib (Wang et al., 2024), ProbTS (Zhang et al., 2024b) and GIFT-Eval (Aksu et al., 2024) provide unified codebases, large collections of datasets, and standardized pipelines for evaluating deep and foundation models across diverse forecasting settings. These efforts, however, primarily target predictive accuracy and uncertainty quantification rather than generative modeling under rich conditioning modalities.
Regarding time series generation, TSGBench (Ang et al., 2023) is the pioneering benchmark that standardizes the evaluation of unconditional models. While it incorporates limited experiments on weakly conditioned settings (e.g., discrete class labels), it does not provide a systematic evaluation framework for controllable generation. Crucially, it fails to cover heterogeneous conditioning modalities, such as structured attributes and natural language text, and lacks metrics designed to verify the condition adherence between complex conditions and generated time series.
Our work is complementary to these benchmarks and focuses specifically on conditional time series generation. By establishing aligned conditions across modalities and semantic levels, ConTSG-Bench enables systematic cross-method comparison and reveals failure modes that remain invisible under existing protocols. Table 1 summarizes the key differences across conditioning modalities and evaluation dimensions.
3. ConTSG-Bench Framework
This section formalizes the conditional generation task, outlines our research questions, and describes the dataset construction and evaluation pipeline.
3.1. Task: Conditional Time Series Generation
We study conditional time series generation, where the goal is to synthesize realistic time series that both match the realdata distribution and adhere to a user-specified condition. Let x  RL×F denote a time series of length L with F variables. Condition is denoted by c  C, where C may take different modalities, including (i) discrete class label clabel, (ii) structured attribute vector cattr with heterogeneous categorical fields, and (iii) natural-language description ctext.
Given a dataset of aligned pairs D = {(xi, ci)}Ni=1 sampled from an unknown real joint distribution pr(x, c), a conditional generator aims to learn a distribution p(x | c) such that samples x^  p(x | c) are (1) realistic with respect to the marginal data distribution and (2) faithful to the condition. Importantly, these two objectives are orthogonal: a model may produce plausible outputs that ignore the condition, or faithfully follow the condition while generating implausible patterns. Our evaluation therefore assesses

fidelity and adherence separately.
Beyond modality, conditions also vary in semantic abstraction (Figure 1). We distinguish two levels: morphological conditions that directly specify temporal structures (e.g., trends, peaks, and their placement), and conceptual conditions that describe high-level semantics (e.g., a clinical diagnosis) and require the model to infer the corresponding temporal patterns. ConTSG-Bench systematically covers both dimensions under a unified task formulation.
3.2. Evaluation Dimensions
ConTSG-Bench is designed not only to rank models, but also to stress-test the key capabilities that conditional time series generators are expected to have in practice: producing realistic data, following conditions, handling different kinds of conditions, and being useful for downstream tasks. To make these desiderata explicit, we organize our study around five research questions.
Generating realistic time series and following conditions are complementary but distinct capabilities: a model may produce plausible outputs that ignore the condition, or faithfully adhere to the condition while generating implausible patterns. To disentangle these two dimensions, we first ask: RQ1 (Overall benchmarking). How do representative conditional time series generation models compare in terms of generation fidelity and condition adherence across diverse datasets and conditioning modalities?
Beyond overall performance, models may behave very differently depending on the semantic abstraction of conditions. For instance, in ECG generation, a condition can describe observable waveform morphology ("irregular RR intervals and absent P-waves") or a high-level clinical concept ("atrial fibrillation"). Both refer to the same underlying pattern, yet the latter requires the model to infer temporal structures from abstract domain semantics. Since conceptual conditions require expert annotation while morphological descriptions are domain-agnostic and lower-cost, understanding model sensitivity to this distinction has practical value. This motivates RQ2 (Semantic abstraction): How sensitive are models to the semantic type of conditions, specifically morphological versus conceptual descriptions, when the underlying time series is fixed?
Practical applications often require precise control over local temporal patterns. For instance, in network monitoring, a user may specify "signal drops in the middle segment, then recovers in the final quarter". RQ3 (Fine-grained control) probes: To what extent can models follow such fine-grained local specifications, and what are the dominant failure modes?
In practice, test-time conditions may be out-of-distribution, involving novel attribute combinations unseen during train-

3

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

Table 1. Comparison of conditional time series generation methods and benchmarks along three dimensions: (1) supported condition modalities, (2) semantic abstraction levels, and (3) evaluation dimensions beyond fidelity, which is universally assessed. Abbreviations: Attr = Attribute; Morph = Morphological; Adh. = Condition Adherence; Fine-gr. = Fine-grained control; Comp. Gen. = Compositional generalization; Down. Util. = Downstream utility.

Method
Existing Benchmark TSGBench (Ang et al., 2023)
Label-conditioned TimeVQVAE (Lee et al., 2023) TTS-CGAN (Li et al., 2022)
Attribute-conditioned TimeWeaver (Narasimhan et al., 2024) TEdit (Jing et al., 2024) WaveStitch (Shankar et al., 2025)
Text-conditioned Text2Motion (Guo et al., 2022) DiffuSETS (Lai et al., 2025a) BRIDGE (Li et al., 2025) T2S (Ge et al., 2025) VerbalTS (Gu et al., 2025)
Unified Benchmark ConTSG-Bench (Ours)

Condition Modality Text Attr Label









































 

 

Condition Semantic Morph Concept

















































Adh.

 
  
    


Evaluation Dimensions Fine-gr. Comp. Gen. Down. Util.









































































ing. For example, a model may encounter "high volatility + downward trend + multiple level shifts", a combination absent in the training set. Robust models should compositionally understand each attribute rather than memorize training combinations. This raises RQ4 (Compositional generalization): Can models generalize to novel attribute combinations where multiple attribute values differ from those observed during training?
Ultimately, generation quality is meaningful only if it translates to practical value. A key use case is data scarcity: when real labeled data is limited, can generated samples substitute for real data in training downstream classifiers? This leads to RQ5 (Practical utility): How well can generated data substitute for real data in downstream tasks?
Sections 4.1­4.5 present experimental results and findings for each research question.
3.3. Datasets
ConTSG-Bench comprises eight datasets spanning diverse domains including healthcare, meteorology, energy, traffic, and network telemetry, covering both synthetic benchmarks with known ground-truth and real-world data with authentic temporal dynamics. Full statistics are provided in Appendix A.
As discussed in Section 2, existing conditional generators operate under heterogeneous conditioning modalities: labelconditioned methods use discrete class labels, attributeconditioned methods condition on structured metadata,

and text-conditioned methods leverage natural language prompts. A key contribution of ConTSG-Bench is providing aligned conditions across all three modalities for each time series: a class label clabel, a structured attribute vector cattr, and a textual description ctext. Since these conditions are derived from the same underlying semantics, our benchmark enables controlled cross-modality comparison that is otherwise infeasible with existing datasets.
To align these modalities, we design an LLM-based pipeline with three stages. First, we prompt an LLM to generate morphological captions ctext that describe observable temporal patterns (e.g., trend direction, periodicity, local anomalies) from time series (Appendix A.2.1). Second, we apply an iterative attribute-schema discovery procedure: the LLM proposes candidate attributes from sampled captions, merges redundant categories, and finalizes a compact schema; attribute values are then extracted from each caption to form cattr (Appendix A.2.2). Finally, class labels clabel are obtained by indexing unique attribute combinations (Appendix A.2.3). This pipeline ensures consistency across modalities while requiring minimal manual effort.
Beyond modality, we observe that existing text-conditioned datasets conflate two distinct levels of semantic abstraction. Some datasets provide morphological conditions that directly describe observable temporal structures, such as trend shapes and local patterns (Ge et al., 2025); others provide conceptual conditions that describe high-level domain semantics without revealing the waveform (Li et al., 2025); still others mix both types without explicit distinction (Feng

4

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

et al., 2025). ConTSG-Bench explicitly disentangles these two levels: for PTB-XL and Weather datasets, we provide paired morphological and conceptual conditions for the same time series, enabling direct comparison of how models handle different abstraction levels (Appendix A.3).
This two-dimensional design, systematically covering condition modality and semantic abstraction, distinguishes ConTSG-Bench from prior work and enables more finegrained analysis of conditional generation capabilities.
3.4. Evaluated Methods
To comprehensively assess conditional time series generation, we benchmark ten representative models spanning all three conditioning modalities supported by ConTSGBench (Table 1). We include label-conditioned models TimeVQVAE (Lee et al., 2023) and TTS-CGAN (Li et al., 2022), which condition on discrete class labels and represent early approaches to conditional time series synthesis. For attribute-conditioned generation, we evaluate TimeWeaver (Narasimhan et al., 2024), TEdit (Jing et al., 2024), and WaveStitch (Shankar et al., 2025), which condition on structured attribute vectors containing heterogeneous categorical and continuous fields, and are designed for controllable synthesis and counterfactual analysis. We also benchmark five recent text-conditioned generators: BRIDGE (Li et al., 2025), VerbalTS (Gu et al., 2025), T2S (Ge et al., 2025), DiffuSETS (Lai et al., 2025a), and Text2Motion (Guo et al., 2022), which generate time series from natural-language descriptions using various generative approaches and text encoding strategies. As shown in Table 1, text-conditioned models exhibit the richest diversity in design choices, yet their coverage of semantic abstraction levels and evaluation dimensions remains limited prior to our benchmark. All models are trained on the same training splits of ConTSG-Bench with validation-based early stopping, ensuring fair comparison. Detailed model implementations and training configurations are provided in Appendix B.
3.5. Evaluation Protocol
Since conditional generation is inherently one-to-many, each model produces K samples {x^(k)}Kk=1  p(x | c) per condition. Depending on the evaluation goal, metrics either aggregate statistics over all K samples or adopt a best-of-K strategy that selects the sample closest to a reference time series.
We organize our evaluation along two complementary axes: generation fidelity, which assesses whether generated series are statistically realistic regardless of the specific condition; and condition adherence, which measures alignment between the generated output and the specified condition. Within each axis, we employ both embedding-based and sta-

tistical metrics. Embedding-based metrics require a shared representation space where time series and textual conditions can be directly compared. To this end, we train a Contrastive Text­Time Series Pretraining (CTTP) model (Gu et al., 2025) per dataset, which learns aligned representations by maximizing similarity between matched (time series, text) pairs. The resulting time-series encoder ts and text encoder text are frozen and reused for all embeddingbased evaluations (see Appendix C.2 for training details).
The detailed evaluation protocols, including specific metrics, formulas, and experimental settings for each research question, are presented alongside their corresponding experimental results in Section 4.
4. Experimental Results
4.1. Overall Benchmarking
Protocol. We assess both generation fidelity and condition adherence using the following metrics. Generation fidelity assesses whether generated series are statistically realistic regardless of specific conditions. We report embedding-based metrics including Fre´chet Inception Distance (FID) (Heusel et al., 2017) between CTTP embeddings of real and generated series, and Precision/Recall (Kynka¨a¨nniemi et al., 2019) in the embedding space, as well as statistical metrics such as marginal distribution difference, autocorrelation difference, skewness, and kurtosis differences. Condition adherence measures alignment between generated outputs and specified conditions. We report CTTP Score (similarity between embeddings of generated time series and the conditioning text), Joint Fre´chet Time Series Distance (JFTSD) (Narasimhan et al., 2024), and joint Precision/Recall, where each sample is represented by the concatenation of its time series embedding and condition embedding. Formal definitions are provided in Appendix C.1. For each model, dataset, and metric, we obtain a scalar score averaged over three random seeds. We normalize metric directions so that higher values indicate better performance, then convert scores to ranks per metric and dataset. To summarize overall performance, we first average ranks across all metrics within each metric group (fidelity or adherence), then average these group-level ranks across datasets; error bars reflect cross-dataset variability.
Results. Figure 2 presents overall rankings across both metric groups, with the left panel reflecting generation fidelity and the right panel reflecting condition adherence. Our results for RQ1 reveal three high-level patterns. First, good generation fidelity does not guarantee condition adherence. While some models (e.g., VerbalTS) perform consistently well on both dimensions, others (e.g., DiffuSETS) show significant rank improvements only under conditional evaluation, confirming the need to evaluate these two aspects

5

9HUEDO76 7(GLW
7LPH:HDYHU 7H[W0RWLRQ :DYH6WLWFK
%ULGJH 'LIIX6(76 7LPH949$(
76 776&*$1


ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

*HQHUDWLRQ)LGHOLW\

&RQGLWLRQ$GKHUHQFH

9HUEDO76 'LIIX6(76
7(GLW 7LPH:HDYHU 7H[W0RWLRQ :DYH6WLWFK
%ULGJH 7LPH949$(
76 776&*$1









$YHUDJH5DQNORZHULVEHWWHU













$YHUDJH5DQNORZHULVEHWWHU

7H[WEDVHG

$WWULEXWHEDVHG

/DEHOEDVHG

Figure 2. Model ranking under two metric groups: (left) generation fidelity that evaluates marginal distribution of generated time series; (right) condition adherence that evaluates joint/conditional alignment between time series and conditions.

37%;/'7:



&RQFHSWXDO

0RUSKRORJLFDO

37%;/&536

:HDWKHU'7:


:HDWKHU&536

'7: &536 '7: &536









 %'ULLGIIJXH6(977HLU6PEDHO97649$(777(6G7&LHW*[W$01RWLRQ 7UH76WLUPLHHY:D:OHDDYYHHU6WLWFK

%'ULLGIIJXH6(977HLU6PEDHO97649$(777(6G7&LHW*[W$01RWLRQ 7UH76WLUPLHHY:D:OHDDYYHHU6WLWFK

 7H[W0RWLRQ7(G%LWUL9GHJUHEDOU7H76WLUPLHH7Y:DLPOHDHY9H4:U 9D$YH(767WL6WF&K*$1'7LIIX66(76

7H[W0RWLRQ7(G%LWUL9GHJUHEDOU7H76WLUPLHH7Y:DLPOHDHY9H4:U 9D$YH(767WL6WF&K*$1'7LIIX66(76

Figure 3. Morphological vs. conceptual conditioning: absolute performance. DTW and CRPS on PTB-XL and Weather under the two condition types.

separately. Second, text conditioning offers the highest performance ceiling but also the largest variance. Textconditioned models span the full range from top (VerbalTS) to bottom, whereas attribute-conditioned methods cluster in the upper-middle tier and label-conditioned baselines consistently rank lowest. This suggests that while natural language provides richer expressiveness, current architectures vary widely in their ability to leverage it. Third, cross-dataset robustness remains a major challenge. The large error bars indicate that no model dominates across all datasets, and rankings can shift substantially depending on data characteristics. This motivates future work on domain-agnostic architectures and training strategies that generalize across heterogeneous time series domains. Detailed per-dataset metric scores are reported in Appendix D.1.
4.2. Morphological vs. Conceptual Conditions
Protocol. To compare how models handle conditions at different semantic abstraction levels, we need metrics that capture generation quality when the underlying time series is fixed but the condition form varies. Embedding-based metrics such as CTTP Score are sensitive to the textual form of conditions: morphological and conceptual descriptions have different text representations even when describing the

same time series, making cross-type comparisons unfair. We therefore adopt reference-based metrics that use the source time series as a fixed anchor. Specifically, for each condition, we generate K samples and compute Dynamic Time Warping (DTW) and Continuous Ranked Probability Score (CRPS) relative to the source time series from which the condition was derived. We report minimum DTW (best-of-K) and mean CRPS (over all K samples) (Appendix C.1).
Results. Figure 3 reveals that condition semantics affect generation difficulty in a dataset-dependent manner. On PTB-XL, morphological and conceptual conditions lead to similar DTW/CRPS for most models, whereas on Weather the gap is substantial, with conceptual conditions often yielding lower error. This suggests that the relative difficulty of morphological versus conceptual conditioning depends on the intrinsic regularity of the underlying signals: highly structured domains (e.g., ECG) may be equally accessible from either condition type, while complex natural phenomena benefit more from expert-level conceptual descriptions. We provide additional analysis of model ranking stability across condition types in Appendix D.2.

6

$FFXUDF\ORJ $FF#
0HDQ$FFORJ

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

6KDSHOHW-RLQW$FFXUDF\6\QWK8
  


9HUEDO76 7H[W0RWLRQ

5HWULHYDO$FFXUDF\7HOHFRP76

   

%ULGJH

   3RRO6L]H
'LIIX6(76 76

7HPSRUDO2UGHU$FFXUDF\7HOHFRP76
   

5HWULHYDO *7 5DQGRP

Figure 4. Fine-grained control evaluation. Left: Joint shapelet classification accuracy on Synth-U, where all three segment-level local patterns must be correctly generated. Middle: Segment retrieval accuracy (Acc@1) as a function of candidate pool size on TelecomTS-Segment. Right: Segment­text temporal order accuracy on TelecomTS-Segment.

4.3. Fine-grained Control
Protocol. To evaluate whether models can follow finegrained local specifications, we employ three complementary approaches depending on dataset characteristics. (i) Classifier-based evaluation. On synthetic data where the local pattern of each segment (e.g., peak, sag) is determined by the generation script, we train a segment-level 1D-CNN classifier to verify whether generated segments contain the specified patterns. We report joint classification accuracy, which requires all segment-level patterns to be correctly generated. (ii) Retrieval-based evaluation. For each segment of a generated sample, we construct a candidate pool containing its true segment-level description plus n - 1 distractors sampled from the test set, retrieve the closest description using CTTP embeddings, and report top-1 retrieval accuracy. To reduce variance from pool composition, we repeat the construction m times and average results. We additionally compare against a naive retrieval baseline that retrieves the nearest training segment based on text embeddings. (iii) Temporal order evaluation. On real-world data with segment-level captions, we test whether each generated segment can correctly retrieve its corresponding positional description (e.g., segment 1  description 1). Retrieval accuracy and confusion matrices reveal whether models preserve the intended temporal order. We instantiate these protocols on two datasets: Synth-U (three segments with controllable peaks and sags) and TelecomTS-Segment, where each sequence is partitioned into four segments with independent captions. Implementation details are provided in Appendix D.3.
Results. On Synth-U (Figure 4, left), most text-conditioned generators exceed the random baseline, indicating they can capture coarse local patterns when the underlying signal family is simple. However, only VerbalTS and DiffuSETS consistently outperform a naive retrieval baseline, indicating that simple retrieval is already highly competitive. On TelecomTS-Segment (Figure 4, middle and right), results differ markedly: as the candidate pool grows, most gener-

ators rapidly approach the random baseline, implying insufficient discriminability for segment-level retrieval. For temporal order, mean accuracy is near chance for all generators; detailed confusion matrices in Appendix D.3.2 reveal that failure patterns vary across models. Together, these results reveal that fine-grained controllability does not reliably transfer from simple synthetic data to real-world dynamics, and most models fail to achieve segment-level semantic alignment comparable to simple retrieval baselines. This motivates future work on segment-aware objectives and architectures with explicit positional control.

4.4. Compositional Generalization

Protocol. To assess generalization to novel attribute com-

binations, we adopt the same retrieval-based protocol as

RQ3 and additionally measure compositional distance from

the training distribution. To quantify how far a test condi-

tion lies from training examples, we define the Hamming

distance between two attribute vectors as HD(ca1ttr, c2attr) =

M j=1

1[c1at,tjr

=

ca2t,tjr ],

where

M

is

the

number

of

attributes.

For each test condition with attribute vector catettsrt, we com-

pute the average Hamming distance to its k nearest neigh-

bors in the training set:

dknn(catettsrt)

=

1 k

HD(catetstrt, cattr). (1)

cattrKNNk (ctaetstrt)

Since CTTP encoders themselves may exhibit limited compositional generalization, we normalize retrieval accuracy as Accnorm = Accgen/Accref, where Accgen and Accref denote accuracy using generated samples and reference time series respectively. We partition test samples into the closest 20% and farthest 20% by dknn and compare their Accnorm to quantify robustness to novel attribute combinations.

Figure 5 compares normalized retrieval accuracy between test samples whose attribute combinations are closest to (top 20%) and farthest from (bottom 20%) the training distribution, quantifying generalization to novel compositions.

7

)DUWKHVW+'Acc

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

norm

norm

)DUWKHVW1HDUHVWAcc

 
 
 





Acc 



1HDUHVW+'





norm

9HUEDO76 7H[W0RWLRQ

7LPH:HDYHU 76

7(GLW :DYH6WLWFK

776&*$1 %ULGJH

'LIIX6(76 7LPH949$(

Figure 5. Compositional generalization analysis. Left: normalized retrieval accuracy for head (closest 20% to training distribution) vs. tail (farthest 20%, novel attribute combinations) test samples; points below the diagonal indicate performance degradation on out-of-distribution combinations. Right: accuracy gap (tail - head) for each model, where negative values reflect sensitivity to novel attribute combinations.

over random guessing, making the metric comparable across datasets with varying task difficulty. A lower drop rate indicates better substitutability.

7(GLW

7LPH:HDYHU

'LIIX6(76

7LPH949$(

9HUEDO76

:DYH6WLWFK

7H[W0RWLRQ

%ULGJH

76

776&*$1

















'URS5DWLRORZHULVEHWWHU

7H[WEDVHG

$WWULEXWHEDVHG

/DEHOEDVHG

Figure 6. Drop rate distribution across datasets and models. Lower drop rate indicates better substitutability of generated data.

Results. Three patterns emerge from the results. First, most models exhibit performance degradation from head to tail, confirming that novel attribute combinations pose a universal challenge. Second, stronger models (e.g., VerbalTS, which also achieves better performance in Section 4.1) show larger drops yet their tail accuracy still exceeds the head accuracy of weaker models, suggesting that better condition adherence provides an absolute advantage even under distribution shift. Third, models with minimal or reversed degradation (e.g., TimeVQVAE) tend to have low absolute accuracy, indicating that their apparent robustness stems from weak responsiveness to conditions rather than true compositional understanding. Together, these findings suggest that models which faithfully adhere to conditions are more sensitive to novel combinations, highlighting the need for architectures that can generalize individual attribute semantics beyond memorized training patterns.

4.5. Practical Utility

Protocol. To measure practical utility, we evaluate whether generated data can substitute for real data in training downstream classifiers. We train a multi-head classifier where each head predicts the value of a corresponding attribute, and compare two training settings: using fully real data versus fully generated data. We report macro-averaged accuracy across attribute classes and quantify utility loss using the drop rate:

Drop Rate = 1 - accgen - accrand ,

(2)

accreal - accrand

where accreal and accgen denote classifier accuracy when trained on real and generated data respectively, and accrand is the random-guessing baseline. This formulation normalizes the utility gap by the maximum achievable improvement

Results. Figure 6 visualizes the drop rate across all models and datasets. Most generative models achieve lower drop rates than the random baseline, indicating that synthetic series preserve discriminative features for classification. However, on complex datasets, some models exhibit drop rates exceeding the random baseline, suggesting that mode collapse or distribution shift can produce data that harms classifier training. Moreover, we observe substantial variance in model rankings across datasets, indicating that no single model consistently dominates. This suggests that the utility of generated data is highly dataset-dependent and cannot be reliably predicted from generation fidelity metrics alone. Detailed results are provided in Appendix D.4.
5. Conclusion and Future Work
We introduced ConTSG-Bench, the first comprehensive benchmark for conditional time series generation that spans multiple conditioning modalities and semantic abstraction levels. Our large-scale evaluation of representative models reveals several key insights. First, generation fidelity and condition adherence are complementary capabilities that require separate evaluation, and text-based conditioning offers the highest performance ceiling but also the widest variance. Second, current methods universally struggle with fine-grained local control and compositional generalization: most models fail to surpass simple retrieval baselines on segment-level tasks, and stronger condition adherence paradoxically leads to greater sensitivity to novel attribute combinations. Third, the downstream utility of generated data varies substantially across datasets and cannot be reliably predicted from fidelity metrics alone. These findings motivate future work on architectures with compositional inductive biases, segment-aware objectives, and domain-agnostic generalization strategies.

8

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

Impact Statement
This paper introduces a benchmark for conditional time series generation, aiming to facilitate standardized evaluation and reproducible research in this area. Time series generation has broad applications in domains such as healthcare, finance, and climate science, where synthetic data can help address data scarcity and enable safer experimentation. While we do not foresee immediate negative societal impacts from our benchmarking framework itself, we acknowledge that generative models, if misused, could potentially produce misleading synthetic data. We encourage practitioners to apply appropriate validation when using generated time series in safety-critical applications.
References
Aksu, T., Woo, G., Liu, J., Liu, X., Liu, C., Savarese, S., Xiong, C., and Sahoo, D. Gift-eval: A benchmark for general time series forecasting model evaluation. CoRR, abs/2410.10393, 2024. doi: 10.48550/ARXIV. 2410.10393. URL https://doi.org/10.48550/ arXiv.2410.10393.
Ang, Y., Huang, Q., Bao, Y., Tung, A. K., and Huang, Z. Tsgbench: Time series generation benchmark. Proc. VLDB Endow., 17(3):305­318, 2023.
Ansari, A. F., Stella, L., Turkmen, C., Zhang, X., Mercado, P., Shen, H., Shchur, O., Rangapuram, S. S., Arango, S. P., Kapoor, S., et al. Chronos: Learning the language of time series. arXiv preprint arXiv:2403.07815, 2024.
Chang, H., Zhang, H., Jiang, L., Liu, C., and Freeman, W. T. Maskgit: Masked generative image transformer. In IEEE/CVF Conference on Computer Vision and Pattern Recognition, CVPR 2022, New Orleans, LA, USA, June 18-24, 2022, pp. 11305­11315. IEEE, 2022. doi: 10. 1109/CVPR52688.2022.01103. URL https://doi. org/10.1109/CVPR52688.2022.01103.
Chen, S. Beijing multi-site air-quality data. UCI Machine Learning Repository, 10:C5RK5G, 2019.
Comanici, G., Bieber, E., Schaekermann, M., Pasupat, I., Sachdeva, N., Dhillon, I., Blistein, M., Ram, O., Zhang, D., Rosen, E., et al. Gemini 2.5: Pushing the frontier with advanced reasoning, multimodality, long context, and next generation agentic capabilities. arXiv preprint arXiv:2507.06261, 2025.
Desai, A., Freeman, C., Wang, Z., and Beaver, I. Timevae: A variational auto-encoder for multivariate time series generation. arXiv preprint arXiv:2111.08095, 2021.
Dohi, K., Ito, A., Purohit, H., Nishida, T., Endo, T., and Kawaguchi, Y. Domain-independent automatic generation of descriptive texts for time-series data. In 2025

IEEE International Conference on Acoustics, Speech and Signal Processing, ICASSP 2025, Hyderabad, India, April 6-11, 2025, pp. 1­5. IEEE, 2025. doi: 10.1109/ ICASSP49660.2025.10888432. URL https://doi. org/10.1109/ICASSP49660.2025.10888432.
Feng, A., Varvarigos, A., Panitsas, I., Fernandez, D., Wei, J., Guo, Y., Chen, J., Maatouk, A., Tassiulas, L., and Ying, R. Telecomts: A multi-modal observability dataset for time series and language analysis. arXiv preprint arXiv:2510.06063, 2025.
Ge, Y., Li, J., Zhao, Y., Wen, H., Li, Z., Qiu, M., Li, H., Jin, M., and Pan, S. T2s: High-resolution time series generation with text-to-series diffusion models. arXiv preprint arXiv:2505.02417, 2025.
Gneiting, T. and Raftery, A. E. Strictly proper scoring rules, prediction, and estimation. Journal of the American statistical Association, 102(477):359­378, 2007.
Goodfellow, I. J., Pouget-Abadie, J., Mirza, M., Xu, B., Warde-Farley, D., Ozair, S., Courville, A. C., and Bengio, Y. Generative adversarial networks. Commun. ACM, 63(11):139­144, 2020. doi: 10.1145/3422622. URL https://doi.org/10.1145/3422622.
Gu, A., Goel, K., and Re´, C. Efficiently modeling long sequences with structured state spaces. In The Tenth International Conference on Learning Representations, ICLR 2022, Virtual Event, April 25-29, 2022. OpenReview.net, 2022. URL https://openreview.net/ forum?id=uYLFoz1vlAC.
Gu, S., Li, C., Jing, B., and Ren, K. Verbalts: Generating time series from texts. In Forty-second International Conference on Machine Learning, 2025.
Gulrajani, I., Ahmed, F., Arjovsky, M., Dumoulin, V., and Courville, A. C. Improved training of wasserstein gans. Advances in neural information processing systems, 30, 2017.
Guo, C., Zou, S., Zuo, X., Wang, S., Ji, W., Li, X., and Cheng, L. Generating diverse and natural 3d human motions from text. In IEEE/CVF Conference on Computer Vision and Pattern Recognition, CVPR 2022, New Orleans, LA, USA, June 18-24, 2022, pp. 5142­5151. IEEE, 2022. doi: 10.1109/CVPR52688.2022.00509. URL https:// doi.org/10.1109/CVPR52688.2022.00509.
Heusel, M., Ramsauer, H., Unterthiner, T., Nessler, B., and Hochreiter, S. Gans trained by a two time-scale update rule converge to a local nash equilibrium. Advances in neural information processing systems, 30, 2017.
Ho, J., Jain, A., and Abbeel, P. Denoising diffusion probabilistic models. Advances in neural information processing systems, 33:6840­6851, 2020.

9

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

Jeon, J., Kim, J., Song, H., Cho, S., and Park, N. Gt-gan: General purpose time series synthesis with generative adversarial networks. Advances in Neural Information Processing Systems, 35:36999­37010, 2022.
Jing, B., Gu, S., Chen, T., Yang, Z., Li, D., He, J., and Ren, K. Towards editing time series. In Globersons, A., Mackey, L., Belgrave, D., Fan, A., Paquet, U., Tomczak, J. M., and Zhang, C. (eds.), Advances in Neural Information Processing Systems 38: Annual Conference on Neural Information Processing Systems 2024, NeurIPS 2024, Vancouver, BC, Canada, December 10 - 15, 2024, 2024.
Kingma, D. P. and Welling, M. An introduction to variational autoencoders. Found. Trends Mach. Learn., 12 (4):307­392, 2019. doi: 10.1561/2200000056. URL https://doi.org/10.1561/2200000056.
Kynka¨a¨nniemi, T., Karras, T., Laine, S., Lehtinen, J., and Aila, T. Improved precision and recall metric for assessing generative models. Advances in neural information processing systems, 32, 2019.
Lai, G., Chang, W.-C., Yang, Y., and Liu, H. Modeling long-and short-term temporal patterns with deep neural networks. In The 41st international ACM SIGIR conference on research & development in information retrieval, pp. 95­104, 2018.
Lai, Y., Chen, J., Zhao, Q., Zhang, D., Wang, Y., Geng, S., Li, H., and Hong, S. Diffusets: 12-lead ECG generation conditioned on clinical text reports and patientspecific information. Patterns, 6(10):101291, 2025a. doi: 10.1016/J.PATTER.2025.101291. URL https://doi. org/10.1016/j.patter.2025.101291.
Lai, Y., Chen, J., Zhao, Q., Zhang, D., Wang, Y., Geng, S., Li, H., and Hong, S. Diffusets: 12-lead ecg generation conditioned on clinical text reports and patient-specific information. Patterns, 2025b.
Lee, D., Malacarne, S., and Aune, E. Vector quantized time series generation with a bidirectional prior model. arXiv preprint arXiv:2303.04743, 2023.
Leo. Istanbul traffic index. Kaggle, 2024. URL https: //www.kaggle.com/datasets/leonardo00/ istanbul-traffic-index/data.
Li, H., Huang, Y., Xu, C., Schlegel, V., Jiang, R., BatistaNavarro, R., Nenadic, G., and Bian, J. Bridge: Bootstrapping text to control time-series generation via multi-agent iterative optimization and diffusion modelling. arXiv preprint arXiv:2503.02445, 2025.

Li, X., Ngu, A. H. H., and Metsis, V. TTS-CGAN: A transformer time-series conditional GAN for biosignal data augmentation. CoRR, abs/2206.13676, 2022. doi: 10.48550/ARXIV.2206.13676. URL https://doi. org/10.48550/arXiv.2206.13676.
Liu, P., Zhu, H., Kreacic, E., and Vyetrenko, S. Privacyaware time series synthesis via public knowledge distillation. arXiv preprint arXiv:2511.00700, 2025.
Liu, X., Gong, C., and Liu, Q. Flow straight and fast: Learning to generate and transfer data with rectified flow. In The Eleventh International Conference on Learning Representations, ICLR 2023, Kigali, Rwanda, May 1-5, 2023. OpenReview.net, 2023. URL https: //openreview.net/forum?id=XVjTT1nw5z.
Lu, C., Reddy, C. K., Wang, P., Nie, D., and Ning, Y. Multilabel clinical time-series generation via conditional gan. IEEE Transactions on Knowledge and Data Engineering, 36(4):1728­1740, 2024. doi: 10.1109/TKDE.2023. 3310909.
Makowski, D., Pham, T., Lau, Z. J., Brammer, J. C., Lespinasse, F., Pham, H., Scho¨lzel, C., and Chen, S. H. A. NeuroKit2: A python toolbox for neurophysiological signal processing. Behavior Research Methods, 53(4):1689­1696, feb 2021. doi: 10.3758/ s13428-020-01516-y. URL https://doi.org/10. 3758%2Fs13428-020-01516-y.
Narasimhan, S. S., Agarwal, S., Akcin, O., Sanghavi, S., and Chinchali, S. Time weaver: A conditional time series generation model. arXiv preprint arXiv:2403.02682, 2024.
Ni, H., Szpruch, L., Sabate-Vidales, M., Xiao, B., Wiese, M., and Liao, S. Sig-wasserstein gans for time series generation. In Proceedings of the Second ACM International Conference on AI in Finance, pp. 1­8, 2021.
Nie, Y. A time series is worth 64words: Long-term forecasting with transformers. arXiv preprint arXiv:2211.14730, 2022.
Peebles, W. and Xie, S. Scalable diffusion models with transformers. In IEEE/CVF International Conference on Computer Vision, ICCV 2023, Paris, France, October 1-6, 2023, pp. 4172­4182. IEEE, 2023. doi: 10.1109/ ICCV51070.2023.00387. URL https://doi.org/ 10.1109/ICCV51070.2023.00387.
Pei, H., Ren, K., Yang, Y., Liu, C., Qin, T., and Li, D. Towards generating real-world time series data. In Proceedings of the 2021 IEEE International Conference on Data Mining (ICDM), Auckland, New Zealand, 2021.

10

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

Radford, A., Kim, J. W., Hallacy, C., Ramesh, A., Goh, G., Agarwal, S., Sastry, G., Askell, A., Mishkin, P., Clark, J., Krueger, G., and Sutskever, I. Learning transferable visual models from natural language supervision. CoRR, abs/2103.00020, 2021. URL https://arxiv.org/ abs/2103.00020.
Ronneberger, O., Fischer, P., and Brox, T. U-net: Convolutional networks for biomedical image segmentation. In International Conference on Medical image computing and computer-assisted intervention, pp. 234­241. Springer, 2015.
Shankar, A., Chen, L. Y., van Deursen, A., and Hai, R. Wavestitch: Flexible and fast conditional time series generation with diffusion models. Proc. ACM Manag. Data, 3(6):1­25, 2025. doi: 10.1145/3769842. URL https://doi.org/10.1145/3769842.
Song, J., Meng, C., and Ermon, S. Denoising diffusion implicit models. In 9th International Conference on Learning Representations, ICLR 2021, Virtual Event, Austria, May 3-7, 2021. OpenReview.net, 2021. URL https: //openreview.net/forum?id=St1giarCHLP.
Tashiro, Y., Song, J., Song, Y., and Ermon, S. Csdi: Conditional score-based diffusion models for probabilistic time series imputation. Advances in neural information processing systems, 34:24804­24816, 2021.
Van Den Oord, A., Vinyals, O., et al. Neural discrete representation learning. Advances in neural information processing systems, 30, 2017.
Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., and Polosukhin, I. Attention is all you need. Advances in neural information processing systems, 30, 2017.
Wagner, P., Strodthoff, N., Bousseljot, R., Kreiseler, D., Lunze, F. I., Samek, W., and Schaeffter, T. Ptbxl, a large publicly available electrocardiography dataset. Scientific Data, 7, 2020. URL https: //api.semanticscholar.org/CorpusID: 218865062.

Machine Learning, ICML 2025, Vancouver, BC, Canada, July 13-19, 2025. OpenReview.net, 2025. URL https: //openreview.net/forum?id=ih2WuBT1Fn.
Xia, Y., Xu, C., Liang, Y., Wen, Q., Zimmermann, R., and Bian, J. Causal time series generation via diffusion models. arXiv preprint arXiv:2509.20846, 2025.
Xu, Z., Bian, Y., Zhong, J., Wen, X., and Xu, Q. Beyond trend and periodicity: Guiding time series forecasting with textual cues. arXiv e-prints, pp. arXiv­2405, 2024.
Zhang, B., Zhang, P., Dong, X., Zang, Y., and Wang, J. Long-clip: Unlocking the long-text capability of clip. In European conference on computer vision, pp. 310­325. Springer, 2024a.
Zhang, J., Wen, X., Zhang, Z., Zheng, S., Li, J., and Bian, J. Probts: Benchmarking point and distributional forecasting across diverse prediction horizons. In Globersons, A., Mackey, L., Belgrave, D., Fan, A., Paquet, U., Tomczak, J. M., and Zhang, C. (eds.), Advances in Neural Information Processing Systems 38: Annual Conference on Neural Information Processing Systems 2024, NeurIPS 2024, Vancouver, BC, Canada, December 10 - 15, 2024, 2024b.
Zhang, Y., Li, M., Long, D., Zhang, X., Lin, H., Yang, B., Xie, P., Yang, A., Liu, D., Lin, J., Huang, F., and Zhou, J. Qwen3 embedding: Advancing text embedding and reranking through foundation models. CoRR, abs/2506.05176, 2025. doi: 10.48550/ARXIV. 2506.05176. URL https://doi.org/10.48550/ arXiv.2506.05176.
Zhou, H., Zhang, S., Peng, J., Zhang, S., Li, J., Xiong, H., and Zhang, W. Informer: Beyond efficient transformer for long sequence time-series forecasting. In Proceedings of the AAAI conference on artificial intelligence, volume 35, pp. 11106­11115, 2021.

Wang, Y., Wu, H., Dong, J., Liu, Y., Long, M., and Wang, J. Deep time series models: A comprehensive survey and benchmark. CoRR, abs/2407.13278, 2024. doi: 10.48550/ ARXIV.2407.13278. URL https://doi.org/10. 48550/arXiv.2407.13278.
Williams, A. R., Ashok, A., Marcotte, E´ ., Zantedeschi, V., Subramanian, J., Riachi, R., Requeima, J., Lacoste, A., Rish, I., Chapados, N., and Drouin, A. Context is key: A benchmark for forecasting with essential textual information. In Forty-second International Conference on

11

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation
A. Dataset Construction Details
A.1. Synthetic Datasets
We utilize synthetic datasets constructed in VerbalTS (Gu et al., 2025), including univariate dataset (Synth-U) and multivariate dataset (Synth-M). With a human-defined attribute set, both datasets are generated using an established pipeline which first synthesizes time series data based on sampled attributes from the set and then synthesizes corresponding textual description through substituting attribute values into the text templates. The Synth-U and Synth-M statistic details of the number of tokens in the text data are given in Table 2 and Table 3 respectively. Note that we utilize tokenizer from Long-clip(Zhang et al., 2024a) for all the datasets in our experiments.

Set

Average Tokens Median Tokens Max Tokens Std. Dev.

Training

41.09

42.0

60

8.90

Validation

41.21

42.0

60

8.94

Test

41.21

42.0

60

8.92

Table 2. Summary of token number statistics for Synth-U dataset.

Set

Average Tokens Median Tokens Max Tokens Std. Dev.

Training

62.23

63.0

83

8.97

Validation

62.27

63.0

83

9.10

Test

62.39

63.0

82

9.17

Table 3. Summary of token number statistics for Synth-M dataset.

A.1.1. ATTRIBUTE SET

Attribute Category

Value Options

Trend Types1

[Linear, Quadratic, Exponential, Logistic]

Trend Directions1

[Up, Down]

Season Cycles1

[0, 1, 2, 4]

Local Shapelets2

[None, Single Peak, Sag, Double Peaks]

High Freq. Components2 [0, 16, 32, 64]

Multivariable*

[X/Y-axis Flip, Shift Forward/Backward]

* Only applicable to Synth-M. 1 Primary Attribute. 2 Secondary Attribute.

Table 4. Attribute Set

Trend Type Function

Linear

xtrend = t

Quadratic

xtrend = t2

Exponential

xtrend

=

2t 1024

Logistic

xtrend

=

1 1+exp(-t )

ti  [0, 1] and t  [-10, 10].

Table 5. Trend Type Functions

VerbalTS defines 6 types of attribute as summarized in Table 4, including Trend Types, Trend Directions, Season cycles, Shapelets, High Frequency Components and Multivariables. Note that only the construction for Synth-M dataset will be assigned with a sampled Multivariable attribute. Elaborations on these attributes are as follows.
· Trend Types and Trend Directions: Trend component xtrend of the time series is jointly composed by trend types and trend directions. The trend trajectory types are characterized by 4 functions: linear, quadratic, exponential, and logistic. For each trend trajectory, direction can be either up or down. Complete details of the corresponding functions and value ranges of the trend type are listed in Table 5. For trend directions, up trend indicates xtrend = xtrend and down trend indicates xtrend = -xtrend.
· Season Cycles: To simulate season component xseason, synthetic time series data incorporate a set of sinusoidal waves. The periodicity of waves is controlled by parameter ncycle, which takes values from the set {0, 1, 2, 4} to represent
12

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation different cycles. Season component xseason can be mathematically formulated as:
xseason = a sin(2t + ), where t  [0, ncycle], ncycle  [0, 20, 21, 22], a  U (0.4, 0.6),   U (0, 2) (3)

· Local Shapelets: Three distinct local shapelets--single peak, sag, and double peaks--are defined to simulate local details in real-world time series which is denoted as xlocal. Further details of local shapelets, including morphological definition and stochastic injection, can be referred to Appendix A.1.3.
· High Frequency Components: To simulate high-frequency signals in real-world data, synthetic time series incorporate high-frequency components , denoted as xhf, which are constructed using the same equation 3 as introduced in the Season Cycles except for ncycle  [0, 16, 32, 64], a  U (0.1, 0.3).
· Multivariable: The multi-variable transfer rules comprise X-axis flip, Y-axis flip, and temporal shifts (forward and backward). Flipping operations flip the time series of the first variable along X-axis or Y-axis to generate time series for the second variable, and the shifting operations translate the time series along the temporal dimension by a shift distance dshift  [20, 40]. Multivariable attribute is adopted only when generating Synth-M dataset.

A.1.2. SYNTH-U AND SYNTH-M

As aforementioned, with defined attribute set, time series data can be synthesized accordingly. In addition, VerbalTS further categorizes attributes into primary and secondary as shown in Table 4. Primary attributes, including Trend Types, Trend Directions and Season Cycles, are shared by all data in the dataset, while secondary attributes, including Local Shapelets and High Frequency Components, are sample-specific in the dataset. Meanwhile noises are common in real-world time series, so noise will be added to the time series to increase randomness. The injection of noise is sample-specific and noise is sampled from a Gaussian distribution xnoise  N (µ, 2),   [0.04, 0.06].

Utilizing the attribute components predefined above, the synthesis formula for generating Synth-U dataset can be formulated

as:

x = xtrend + xseason + xlocal + xhf + xnoise

(4)

Synth-M shares the similar generation formula but in a multivariate setting with the extra attribute Multivariable. Following VerbalTS (Gu et al., 2025), each of Synth-U and Synth-M dataset includes 32000 instances through sampling 1000 samples for 32 (4 Trend Types×2 Trend Directions×4 Season Cycles) combinations of primary attribiutes. Instances are split into training set, validation set and test set in the ratio of 6:1:1.

A.1.3. LABELING SEGMENTS
Leveraging local shapelets attributes, we define four corresponding morphological shapelet labels, including single peak, sag, double peaks and nothing, to simulate real-world time series fine-grained details. Textual description generation utilizes these labels and corresponding templates. A single peak is characterized by a symmetrical linear incline and decline over a time span of length 9, with zeros on both sides and a peak midpoint in the range of [1.0, 1.2]. The sag is defined as the symmetrical shape of a single peak across the x-axis. A double peak is formed by concatenating two single-peak structures. We partition the time series into three segments of equal length. Within each segment, there is a 70% chance of nothing, while the single peak, sag, and double peak each have a 10% probability of being inserted at a random location.

A.2. Real-World Augmented Datasets
A.2.1. LLM CAPTION GENERATION
The overall LLM caption generation pipeline is illustrated in Figure 7. For datasets without textual information, we generate high-quality morphological caption for these time series by leveraging the capability of Large Language Model (LLM). In our implementation, we choose Gemini-2.5-flash (Comanici et al., 2025) as the LLM. LLM Caption Generation pipeline can be applied to both univariate and multivariate time series. Each variate data of the multivariate time series can also be processed by the pipeline separately if specifically required. To efficiently execute captioning operation, we pre-process time series data as follows:

· Rounding: We first round the numerical values of time series to 3 decimal places to reduce massive token cost.

13

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

Prompt
Figure 7. Overall Pipeline of LLM Caption Generation

The series exhibits a general downward trend with significant volatility, marked by a prominent peak followed by a sharp
trough, and several smaller, irregular
fluctuations thereafter.

· Structuring: We then convert the numpy number sequence into a list, compute its length, and encapsulate them into a JSON object which includes the sequence information and its length information. For processing multivariate time series, sequence information will be a nested list. Note that when dumping JSON for uploading to the LLM, the number list will be serialized into strings.

Code Snippet 1. LLM Captioning Generation Prompt for Univariate Time Series

1 def make_prompt(

2

include_context: bool,

3

forbid_semantics: bool,

4 ) -> str:

5

context_line = (

6

"If a channel_description is provided, include that context in your description."

7

if include_context

8

else "Do NOT mention any domain semantics or variable names."

9

)

10

if forbid_semantics:

11

context_line = "Do NOT mention any domain semantics or variable names."

12

prompt = f"""You are a time-series analyst. You will receive a single-channel sequence

13

14

Task:

15

- Write a concise intrinsic description focusing on trend, volatility, periodicity,

16

and notable peaks/troughs.

17

- Mention level shifts if present.

18

- Keep it short (1-2 sentences).

19

- {context_line}

20

Output JSON schema:

21

{{

22

\"description\": \"<short description>\"

23

}}

24

Return only JSON (no extra text).

25

""".strip()

26

return prompt

As for prompt engineering, we carefully design the system instruction to prompt LLM to act as a 'Time-Series Analyst' and output structured JSON schema for returning caption. The instructions specifically instruct LLM to pay attention to the morphology of time series, including trend, periodicity, etc. It is worth noticing that mentioning any domain semantics or variable names of time series is not permitted and this can be assured through prompt engineering. An example prompt template for univariate time series can be referred to code snippet 1.
After combining the structured data and prompt into payload, we can obtain the morphological caption of time series by LLM API with rigorous configuration setting.
14

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation
A.2.2. ATTRIBUTE VECTOR EXTRACTION
As aforementioned in Section 3.3, to obtain structured attribute vector cattr, Attribute Vector Extraction comprises two procedures: Attribute Schema Discovery and Attribute Vector Value Assignment.
Attribute Schema Discovery Pipeline is developed to, if structured attribute information is not provided in the dataset, discover an appropriate and structured attribute set for all unstructured textual descriptions or captions in the dataset through leveraging the capability of Large Language Model(LLM). In our implementation, we choose Gemini-2.5-flash (Comanici et al., 2025) as the LLM.
The formal objective of the pipeline is to obtain a discrete attribute schema S mainly consisting of a set of attributes A = {a1, a2, . . . , am}, where each attribute ai is defined by a name, a semantic definition, and a set of discrete value options Vi. Each discrete value option has a string name and a corresponding index. We denote dataset as D, mini-batch size as N , stability threshold as K and maximum iteration as T . An example schema of ETTm1 produced by the pipeline is presented in code snippet 2.
Because prompting LLM to look into the whole text dataset and extract our desired schema is nearly impossible, the discovery process is formulated as an iterative algorithm. Pipeline progressively refines the schema by exposing the model to random batches of data samples. The process continues until the schema converges and stabilizes. The pipeline of algorithm is elaborated as follows:

Code Snippet 2. Example Schema of ETTm1 Dataset A.2.4

1{

2 "scope": "text",

3 "attributes": [

4

{

5

"name": "level_shift_presence",

6

"definition": "Indicates if there are abrupt changes in the average level

of the series.",

7

"values": [

8

"multiple_shifts", "no_shifts", "other",

9

"single_downward_shift", "single_upward_shift"

10

]

11

},

12

......

13 ]

14 }

1. Sampling: A mini-batch of text samples Bt  D is drawn without replacement (where possible) to ensure diversity.
2. Prompt Engineering: A prompt Pt is constructed containing: · System Instruction: Defines the task (designing a coarse discrete schema), constraints (e.g., 3­8 values per attribute), and the mandatory inclusion of an 'other' category for robustness. · Current State: The schema from the previous iteration, St-1. · Observations: The current data batch Bt.
3. Inference & Parsing: The LLM generates a candidate update St. We enforce a strict JSON output schema to ensure syntactic validity. If schema parsing fails, the model is recursively prompted to repair the error JSON.
4. Canonicalization: The raw output is normalized (e.g., whitespace stripping) and deduplicated to form St.
5. Stability Check: We compute the hash value H(St). If H(St) = H(St-1) for K consecutive rounds, the process terminates.
15

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation
6. Ending: If stability check is passed within the maximum iteration limit, the algorithm immediately terminates and the final output schema is preserved. Otherwise the algorithm ends when iteration times reach the maximum limit T .

In our implementation, we empirically set N = 100, K = 3 and T = 50. Pseudocode of the algorithm can be referred to 1.
After obtaining the attribute set from the Attribute Schema Discovery Pipeline, we can further integrate dataset samples' textual descriptions with this attribute set through appropriate prompting and structuring, so as to subsequently feed them into LLM for value assignment to every sample's structured attribute vector.

Algorithm 1 Attribute Schema Discovery Pipeline

1: Input: Dataset D, Mini-Batch size N , Stability threshold K, Maximum Iteration T

2: Output: Optimized Schema S

3: Sprev  , kstable  0, tround  0, U sedIndices  

4: while kstable < K and tround < T do

5: tround  tround + 1

6: Indices  SAMPLEINDICES(|D|, N ) \ U sedIndices

7: B  {D[i] | i  Indices}

8: U sedIndices  U sedIndices  Indices

9: P rompt  BUILDPROMPT(B, Sprev)

10: Sraw  LLM(P rompt)

11: Scurr  CANONICALIZE(Sraw)

12: if HASH(Scurr) == HASH(Sprev) then

13:

kstable  kstable + 1

14: else

15:

kstable  0

16: end if

17: Sprev  Scurr

18: end while

19: return Sprev

A.2.3. CLASS LABEL ACQUISITION
After attribute vector extraction, each sample in the dataset is assigned a structured attribute vector. The specific values within each vector define a unique attribute combination. By aggregating all such combinations in the dataset, we form a set of N distinct entries. Therefore, each attribute vector can be accordingly mapped to an N -dimensional one-hot vector through indexing, denoted as its class label clabel.
A.2.4. INDIVIDUAL DATASET DETAILS
AirQuality Beijing (Chen, 2019) Pollutants readings are often included in the air quality reports and are very important for the environment and human society. Collected from 12 nationally-controlled monitoring stations and provided by the Beijing Municipal Environmental Monitoring Center, AirQuality Beijing dataset comprises hourly atmospheric pollutant records integrated with corresponding meteorological data. The time period is from March 1st, 2013 to February 28, 2017.
For each initial raw data sequence from one station, it contains 35,064 observations and is partitioned along the temporal axis into training, validation and test subsets using a ratio of 8:1:1. Then the dataset is obtained by using a sliding window with a sequence length of 24 and a stride of 24 to slice every station's subset data. Finally each sample in the dataset is a multivariate time series with a sequence length of 24 (representing 24-hour window in a day) and 6 variates which correspond to 6 critical air pollutants: PM2.5, PM10, SO2, NO2, CO, and O3. The dataset contains N = 17, 532 samples in total and the sizes of training, validation, and testing sets are Ntrain = 14, 025, Nvalid = 1, 753, and Ntest = 1, 754, respectively. There are 5 attributes extracted from the schema produced by LLM Caption Generation A.2.1 and Attribute Schema Discovery Pipeline A.2.2 and are shown in Table 6.
The case visualization of Airquality Beijing time series data with its corresponding condition in three modalities is shown in Figure 8. The statistic details of the number of tokens in the text data are given in Table 7.
16

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

Attribute Particulate Matter Profile
Ozone Peak Intensity Inverse Relationship Strength Primary Pollution Event Timing

Value Options

Definition

Consistently Low, Low with a Significant Spike, Moderate and Fluctuating, High and Worsening, Consistently High, High with Significant Improvement

The overall 24-hour trend and severity of PM2.5 and PM10.

Suppressed or No Peak, Moderate Peak, The strength of the afternoon ozone (O3) peak. Strong/Very High Peak

No Clear Relationship, Weak Relationship, The clarity of the inverse relationship between

Strong and Clear Relationship

O3 and primary pollutants (NO2, CO).

No Specific Event, Morning Peak, Midday/After- The main time of day when primary pollutants

noon Peak, Evening/Nighttime Peak

(PM, CO, NO2) are highest.

Table 6. Attribute Set for Air Quality Profile.

Set

Average Tokens Median Tokens Max Tokens Std. Dev.

Training Validation Test

220.00 221.61 218.08

212.0 213.0 209.0

611

54.85

508

55.64

472

54.33

Table 7. Summary of token number statistics for Airquality Beijing dataset.

TelecomTS (Feng et al., 2025) In the context of monitoring complex systems, vast streams of time-series metrics produced by modern enterprises, also known as observability data, can be very important. Unlike conventional datasets that operate on minute-level aggregations, TelecomTS captures high-frequency network dynamics with a sampling interval of 100ms. The data was collected from a real-world 5G network testbed, incorporating Commercial Off-The-Shelf (COTS) user equipment (UE) under varying channel conditions.
The dataset comprises 32,000 samples generated from diverse realistic internet traffic scenarios. Following the ratio of 8:1:1, dataset is empirically split into training, validation and test set with size of 25600, 3200, 3200, respectively. Each sample in the dataset is a multivariate time series with a sequence length of 128 and 18 distinct Key Performance Indicator variates. In our experiments, we only utilize time series data from variate Reference Signal Received Power (RSRP) and Uplink Signal-to-Noise Ratio (UL SNR), and further treat it as a new multivariate dataset. In our implementation, we predefine the attribute names as rsrp seg{i}, ul snr seg{i}, i  {1, 2, 3, 4}, and then use LLM Caption Generation A.2.1 and Attribute Schema Discovery Pipeline A.2.2 to produce discrete attribute value options. Eventually there are 8 attributes whose value options are identical, including "drop", "drop recovery", "other", "periodic", "spiky", "stable", "step change", "trend down", "trend up", "volatile". The case visualization of TelecomTS time series data with its corresponding condition in three modalities is shown in Figure 9.
In addition, we further prepare augmented TelecomTS dataset, denoted as TelecomTS-Segment, for the Fine-grained Control experiment in RQ3. We partition the sequence into four segments and perform captioning for each segment. The TelecomTS-Segment statistic details of the number of tokens in the text data are given in Table 8.

Set

Average Tokens Median Tokens Max Tokens Std. Dev.

Training Validation Test

168.14 167.30 168.67

165.0 164.0 165.0

386

31.06

302

30.07

323

31.27

Table 8. Summary of token number statistics for Telecomts-Segment dataset.

ETTm1 The ETTm1 dataset is derived from the Electricity Transformer Dataset (ETDataset) (Zhou et al., 2021), which is collected via a real-world platform in partnership with the Beijing Guowang Fuda Science and Technology Development Company. The time period is from July 2016 to July 2018. There are 7 variates in the raw data: three variates of useful load (HUFL, MUFL, LUFL), three variates of useless load (HULL, MULL, LULL), and Oil Temperature (OT).
The initial raw data sequence, containing 69,680 observations, is partitioned along the temporal axis into training, validation
17

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

The day began with declining levels of PM2.5,
PM10, NO2, and CO, while SO2 was relatively
low and O3 was minimal. Throughout the
morning, PM10 increased while PM2.5, SO2 and NO2 remained
relatively stable......

Attribute

Value

Particulate_Matter_ Profile

"High and Worsening": 3

Ozone_Peak_Intensity "Strong/Very High Peak": 2

Inverse_Relationship_ "Weak Relationship": 1 Strength
Primary_Pollution_Ev "Evening/Nighttime Peak": 3 ent Timing

Figure 8. Case Visualization of Airquality Beijing Data

The RSRP signal exhibits distinct step-like changes and a sharp drop-andrecovery event, while UL_SNR remains consistently stable with
moderate volatility throughout the entire time series. RSRP starts at 118.0 dBm, sharply increases to -117.0 dBm in Segment 0, then abruptly drops to -118.0 dBm in Segment 1. Segment 2 sees an abrupt increase to -117.0 dBm, followed by a sharp drop and immediate recovery, before
becoming perfectly stable at -117.0 dBm in Segment 3. In contrast, UL_SNR shows no significant changes across any segments or transitions,
maintaining a stable behavior with moderate volatility, largely unaffected by the dynamic RSRP fluctuations.

Attribute rsrp_seg1 rsrp_seg2 rsrp_seg3 rsrp_seg4 ul_snr_seg1 ul_snr_seg2 ul_snr_seg3 ul_snr_seg4

Value "stable": 0 "step_change": 3 "spiky": 5 "step_change": 3 "trend_down": 2 "trend_up: 1 "trend_down": 2 "stable": 0

Figure 9. Case Visualization of TelecomTS Data

and test subsets using a ratio of 8:1:1. Then the dataset is obtained by using a sliding window with a sequence length of 120 and a stride of 30 to slice each subset. In addition, in our experiments, we decompose these multivariate time series into individual univariate sequences. Finally each sample in the dataset is a univariate time series with a sequence length of 120. The dataset contains N = 17, 532 samples in total and the sizes of training, validation, and testing sets are Ntrain = 13, 013, Nvalid = 1, 631, and Ntest = 1, 631, respectively. There are 5 attributes extracted from the schema produced by LLM Caption Generation A.2.1 and Attribute Schema Discovery Pipeline A.2.2 and are shown in Table 9.
The case visualization of ETTm1 time series data with its corresponding condition in three modalities is shown in Figure 10. The statistic details of the number of tokens in the text data are given in Table 10.

The series exhibits a general downward trend with significant volatility, marked by a prominent peak followed by a sharp
trough, and several smaller, irregular
fluctuations thereafter.

Attribute

Value

level_shift_presence "other": 2

overall_trend

"downward_trend": 0

periodicity

"absent": 0

prominent_features "peaks_and_troughs": 2

volatility_level

"high_volatility": 1

Figure 10. Case Visualization of ETTm1 Data

18

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

Attribute level shift presence overall trend periodicity prominent features volatility level

Value Options

Definition

multiple shifts, no shifts, other, sin- Indicates if there are abrupt changes in the aver-

gle downward shift, single upward shift

age level of the series.

downward trend, fluctuating trend, mixed trend, Captures the long-term trajectory and persistent no clear trend, other, stable level, upward trend directional movement of the signal.

absent, other, present, unclear

Assesses the existence of repetitive cycles or patterns occurring at fixed time intervals.

minor fluctuations, other, peaks and troughs, Characterizes the most distinct visual landmarks

peaks only, troughs only

or morphological events within the data.

decreasing volatility, high volatility, increas- Evaluates the intensity and temporal evolution ing volatility, low volatility, mixed volatility, of variance and fluctuations in the series. moderate volatility, other

Table 9. Attribute Set for ETTm1.

Set

Average Tokens Median Tokens Max Tokens Std. Dev.

Training

43.37

42.0

86

7.54

Validation

43.84

43.0

81

8.03

Test

44.24

43.0

74

7.71

Table 10. Summary of token number statistics for ETTm1 dataset.

Istanbul Traffic (Leo, 2024) Istanbul Traffic dataset records Istanbul city's traffic index at one-minute intervals. The time series data includes three key variates: a city-wide index (TI) and separate indices for the Asian (TI An) and European (TI Av) regions. The time period is from November 2022 to June 2024, with a sampling frequency of one minute and update frequency of a week.
The initial raw data sequence, containing 817,769 observations, is first taken a sample every ten minutes and then partitioned along the temporal axis into training, validation and test subsets using a ratio of 8:1:1. Then the Istanbul Traffic dataset is obtained by using a sliding window with a sequence length of 144 and a stride of 24 to slice each subset. In addition, in our experiments, we decompose these multivariate time series into individual univariate sequences. Finally each sample in the dataset is a univariate time series with a sequence length of 144. The dataset contains N = 31, 971 samples in total and the sizes of training, validation, and testing sets are Ntrain = 25, 596, Nvalid = 3, 186, and Ntest = 3, 189, respectively. There are 6 attributes extracted from the schema produced by LLM Caption Generation A.2.1 and Attribute Schema Discovery Pipeline A.2.2 and are shown in Table 11.

Attribute extreme points level shifts overall trend periodicity volatility change volatility level

Value Options

Definition

absent, other, present

Denotes the existence of significant local maxima (peaks) or minima (troughs) within the signal.

absent, other, present distinct, present gradual, Specifies the occurrence and specific characteristics of

step wise

sudden transitions in the series' baseline.

downward, mixed, other, stable, upward

Represents the predominant long-term trajectory of the data over the entire observation window.

absent, other, present

Evaluates whether the sequence demonstrates rhythmic or recurring temporal structures.

decreasing, increasing, other, stable volatility Tracks the evolution of fluctuation intensity, indicating if the variance expands or contracts over time.

high, low, moderate, no volatility, other

Quantifies the overall magnitude of oscillations and noise levels present in the time series.

Table 11. Attribute Set for Istanbul Traffic.

The case visualization of Istanbul Traffic time series data with its corresponding condition in three modalities is shown in Figure 11. The statistic details of the number of tokens in the text data are given in Table 12.
19

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

Set

Average Tokens Median Tokens Max Tokens Std. Dev.

Training Validation Test

45.64 45.40 44.41

44.0

288

11.60

43.0

188

11.73

43.0

122

11.22

Table 12. Summary of token number statistics for Istanbul Traffic dataset.

The overall traffic index exhibits step-like level shifts, with periods of stability at various levels (1, 2, 4, 6, 8) and no clear trend or periodicity. Notable peaks occur at levels 6 and 8, while troughs are at level 1 and 2.

Attribute extreme_points level_shifts overall_trend periodicity volatility_change volatility_level

Value "present": 2 "step_wise": 4 "stable": 3 "absent": 0 "stable_volatility": 3 "moderate": 2

Figure 11. Case Visualization of Istanbul Traffic Data

A.3. Real-World Datasets with Paired Conditions
As aforementioned, with respect to the experiment in RQ2, PTB-XL (Wagner et al., 2020) and Weather (Xu et al., 2024) datasets are further processed to annotate every time series instance with both a morphological description and conceptual description.
A.3.1. PTB-XL
Electrocardiography (ECG) remains a fundamental diagnostic instrument for evaluating cardiac health. The integration of automated ECG interpretation systems can be rather important and beneficial. PTB-XL dataset is a dataset is a large dataset of 21837 clinical 12-lead ECGs from 18885 patients of 10 second length. We split the dataset in a ratio of 8:1:1 and obtain training, validation and testing set with the size of 17418, 2183 and 2198 respectively. Each sample data contains a multivariate time series with the length of 1000 and variate number of 12.
Conceptual information is included in the original dataset for each sample and is further utilized to form conceptual description. Following Neurokit2 (Makowski et al., 2021), to annotate samples with more accurate morphological description, instead of prompting LLM to do morphological captioning, we first leverage neuropsychological library neurokit2 to obtain the physical features of ECG signals, categorize them into single-label attributes, and then generate textual description utilizing the attribute values and there corresponding predefined templates.
Instead of using Attribute Schema Discovery Pipeline A.2.2, the attribute sets for the morphological condition and conceptual condition are obtained from Neurokit2 library and patient diagnostic information respectively. The details of these two attribute sets are presented in Table 13 and Table 14.
The case visualization of PTB-XL time series data with its corresponding condition in three modalities is shown in Figure 12. The statistic details of the number of tokens in the morphological and conceptual text data are given in Table 15 and 16 respectively.
A.3.2. WEATHER
Collected at the Max Planck Institute for Biogeochemistry's WS Beutenberg station in Jena, Germany, this comprehensive dataset includes an eight-year climatic observations from 2014 to 2022. There are 21 distinct meteorological parameters included in the dataset, ranging from atmospheric pressure (p, mbar) to carbon dioxide concentration (CO2, ppm). They are captured at frequent 10-minute intervals with per-second timestamp precision.
The raw data is sliced into 6-hour windows (36 time steps), strictly anchored by existing caption timestamps to ensure
20

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

Attribute rhythm
hr cat rr regularity qrs cat qtc cat st anterior
st lateral
st inferior

Value Options

Definition

SR, AFIB, AFLT, STACH, SBRAD, Primary rhythm code (highest confidence) SARRH, PACE, SVARR, BIGU, TRIGU, SVTAC, PSVT, unknown

bradycardia, normal, tachycardia

HR < 60 / 60-100 / > 100 bpm

regular, mild irregular, irregular

RR CV < 0.05 / 0.05-0.12 / > 0.12

normal, borderline, wide

QRS < 100 / 100-120 / > 120 ms

normal, borderline, prolonged

QTc < 450 / 450-480 / > 480 ms

normal, mild elevation, high elevation, ST deviation in V1-V4 mild depression, high depression

normal, mild elevation, high elevation, ST deviation in I, aVL, V5-V6 mild depression, high depression

normal, mild elevation, high elevation, ST deviation in II, III, aVF mild depression, high depression
Table 13. Morphological Condition Attribute Set for PTB-XL

Attribute age group sex diagnosis
heart axis

Value Options

Definition

young, middle aged, elderly

Age < 40 / 40-65 / > 65

male, female

From metadata

43 diagnostic codes (e.g., NORM, IMI, ASMI, Primary diagnosis (highest confidence) LVH, ...)

normal, LAD, RAD, ALAD, ARAD, unknown From metadata Table 14. Conceptual Condition Attribute Set for PTB-XL

Morphological
sinus rhythm with normal heart rate and regular
intervals; QRS duration wide; QTc interval normal.
Conceptual
ECG from a middle-aged female with normal ECG......

Morph_Attribute rhythm ......

Value "SVARR": 7 ......

Concept_Attribute Value

age_group

"middle_aged": 1

......

......

Figure 12. Case Visualization of PTB-XL Data

data validity. These time series snippets are partitioned in chronological order and in the ratio of 8:1:1, producing training, validation and testing sets with the size of 10489, 1311, 1312 respectively. In addition, given that time series with 21 variates will result in rather long captions produced by LLM, we extract 10 meteorological variates data out and treat them as the new multivariate data used for our experiment. These 10 variates include: temperature (T, degC), wind speed (wv, m/s), wind direction (wd, deg), atmospheric pressure (p, mbar), relative humidity (rh, %), rainfall (rain, mm), rain duration (raining, s), shortwave radiation (SWDR, W/m²), photosynthetically active radiation (PAR, µmol/m²/s) and maximum photosynthetically active radiation (max. PAR, µmol/m²/s).
The conceptual descriptions of the data are human expert weather forecasts obtained from public platforms. The morphological descriptions of the data are generated using Gemini-2.5-flash with appropriate structured payload and prompting.
21

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

Set

Average Tokens Median Tokens Max Tokens Std. Dev.

Training

25.94

24.0

51

5.07

Validation

26.17

24.0

50

5.17

Test

26.16

24.0

50

4.98

Table 15. Summary of token number statistics for PTB-XL morphological text data.

Set

Average Tokens Median Tokens Max Tokens Std. Dev.

Training

16.29

16.0

29

4.37

Validation

16.13

16.0

28

4.17

Test

16.19

16.0

27

4.19

Table 16. Summary of token number statistics for PTB-XL conceptual text data.

We utilize Attribute Schema Discovery Pipeline A.2.2 to obtain the attribute set for both morphological and conceptual conditions. For the morphological condition, so as to converge faster and produce more morphologically reasonable schema, we predefine each variate of time series as an attribute without specifying variate name or semantic meaning, and eventually obtain identical value options for each attribute, including "flat", "level shift", "other", "periodic", "spiky", "trend down" and "trend up". For the conceptual condition, there are 7 attributes extracted from the produced schema shown in Table 17.

Attribute humidity level pressure level season sky condition temperature level time of day wind strength

Value Options

Definition

dry, extremely high, high, low, medium, moderately dry, A qualitative representation of the ambient mois-

saturated, somewhat humid, unknown, very high

ture concentration in the atmosphere.

average, high, low, unknown, very high, very low

Reflects the barometric status and atmospheric pressure fluctuations.

autumn, spring, summer, unknown, winter

Identifies the specific climatological period of the year for the given data.

broken clouds, clear, cloudy, fog, other, partly cloudy, Characterizes the visual appearance of the firmapassing clouds, precipitation, scattered clouds, sunny ment and the density of cloud coverage.

chilly, cool, high, low, medium, unknown, warm

Provides a non-numeric evaluation of the thermal state of the environment.

afternoon, early morning, evening, morning, night, un- Categorizes the observation into broad diurnal

known

temporal segments.

calm, fresh, gentle, light, moderate, strong, unknown

Describes the magnitude and kinetic energy of atmospheric air flow.

Table 17. Conceptual Condition Attribute Set for Weather.

The case visualization of Weather time series data with its corresponding condition in three modalities is shown in Figure 13. The statistic details of the number of tokens in the morphological and conceptual text data are given in Table 18 and Table 19 respectively.
B. Model Implementation Details
In this section, we provide the implementation details for all evaluated models in ConTSG-Bench. We first describe the unified training configuration shared across all models, followed by model-specific adaptations organized by conditioning modality.
B.1. General Training Configuration All experiments are conducted on a single NVIDIA A40 GPU with 48GB memory using full-precision (FP32) training. All datasets are normalized using channel-wise z-score standardization, where each feature dimension is independently standardized to zero mean and unit variance based on training set statistics.
22

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

Set

Average Tokens Median Tokens Max Tokens Std. Dev.

Training Validation Test

142.49 146.09 144.45

140.0 143.0 142.0

276

28.91

251

31.04

269

31.14

Table 18. Summary of token number statistics for Weather morphological text data.

Set

Average Tokens Median Tokens Max Tokens Std. Dev.

Training Validation Test

70.10 73.40 72.87

69.0

130

10.05

73.0

125

10.64

73.0

112

10.58

Table 19. Summary of token number statistics for Weather conceptual text data.

Morphological
Variate 0 is a generally increasing trend with moderate volatility and no
clear periodicity...
Conceptual
It's the early morning of a day in January.......

Morph_Attribute variate_0 ......

Value "trend_up": 6 ......

Concept_Attribute Value

humidity_level

"high": 2

......

......

Figure 13. Case Visualization of Weather Data

The maximum number of training epochs is set to 700, with early stopping triggered if the validation loss fails to improve for 50 consecutive epochs. For two-stage models (TimeVQVAE (Lee et al., 2023), T2S (Ge et al., 2025), Text2Motion (Guo et al., 2022), and DiffuSETS (Lai et al., 2025a)), we allocate 200 epochs for the first stage and 500 epochs for the second stage, with early stopping applied independently to each stage. All models use the AdamW optimizer with a weight decay of 1 × 10-4. We perform grid search over learning rate  {10-3, 10-4}, batch size  {32, 64, 128, 256}, and learning rate scheduler  {cosine, linear, none}, selecting the best configuration based on validation loss.
For diffusion-based models, we adopt DDIM (Song et al., 2021) as the unified sampling framework, except for T2S (Ge et al., 2025) which employs rectified flow with Euler ODE integration. For text-conditioned models, we use Qwen3-Embedding0.6B (Zhang et al., 2025) as the sentence encoder, except for VerbalTS (Gu et al., 2025) which trains its own text encoder from scratch.
B.2. Label-Conditioned Models
TTS-CGAN (Li et al., 2022). TTS-CGAN employs a Transformer-based conditional GAN architecture (Goodfellow et al., 2020) for class-conditioned time series synthesis. We include it as a representative of GAN-based approaches, offering a fundamentally different training paradigm compared to diffusion-based methods. The model uses WGANGP (Gulrajani et al., 2017) training with auxiliary classification losses to encourage class-distinctive pattern generation. The core architecture, including the Transformer-based generator and patch-based discriminator, remains unchanged.
TimeVQVAE (Lee et al., 2023). TimeVQVAE leverages vector quantization (Van Den Oord et al., 2017) to compress time series into discrete latent representations, offering an alternative paradigm to continuous diffusion-based methods. The model operates in two stages: (1) a VQ-VAE encodes time series into discrete tokens via time-frequency decomposition with separate codebooks for low and high-frequency components; (2) a MaskGIT-style (Chang et al., 2022) bidirectional Transformer learns the prior distribution over quantized tokens. Our implementation is based on the official repository and
23

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation
preserves all core components. For adaptation to our benchmark, we map discrete attribute combinations onto class labels through Cartesian product encoding. The two-stage training is integrated into our multi-stage framework with automatic weight loading between phases.
B.3. Attribute-Conditioned Models
TEdit (Jing et al., 2024). TEdit was originally designed for the task of Time Series Editing (TSE), employing a multiresolution diffusion architecture with attribute conditioning. We include it as a representative of multi-scale patch-based diffusion approaches. For adaptation to our benchmark, we reformulate TEdit from an editing model to a conditional generation model by removing the two-stage editing procedure (DDIM forward encoding followed by reverse decoding) and instead performing standard diffusion-based generation from Gaussian noise. The bootstrap learning component is also removed as it is specific to the editing task. The core architecture remains unchanged, including the multi-resolution patch embedding, residual blocks with time-feature Transformer attention, and the heterogeneous attribute encoder.
TimeWeaver (Narasimhan et al., 2024). TimeWeaver is a diffusion-based model designed for generating time series conditioned on heterogeneous metadata. As the original implementation is not publicly available, we provide a faithful reimplementation based on the published paper, following the CSDI-based backbone architecture (Tashiro et al., 2021). For adaptation to our benchmark, we focus on discrete attribute conditioning while omitting support for continuous and time-varying metadata, as these modalities are not present in our evaluation datasets. The core architectural components, including interleaved temporal-feature attention and the metadata fusion mechanism, closely follow the original paper.
WaveStitch (Shankar et al., 2025). WaveStitch is designed for synthesizing tabular time series with hierarchical attributes. It employs a diffusion model backbone based on Structured State Spaces (S4) (Gu et al., 2022), which captures long-range temporal dependencies more efficiently than standard attention mechanisms. We include it as a representative of S4-based conditional diffusion architectures. The original implementation uses cyclic encoding that maps temporal attributes (e.g., hour-of-day) to sine-cosine pairs, assuming periodic semantics. For our benchmark, we replace cyclic encoding with learnable embeddings to handle general discrete attributes without assuming specific semantics. The embeddings are injected into each residual block through additive conditioning. The core S4-based diffusion backbone with skip connections and gating mechanism remains unchanged.
B.4. Text-Conditioned Models
BRIDGE (Li et al., 2025). BRIDGE was originally proposed for text-controlled time series generation, serving as a representative of prototype-based diffusion architectures. The core architecture comprises a Domain-Unified Prototyper that extracts latent representations from example time series, and a 1D U-Net (Ronneberger et al., 2015) diffusion backbone with cross-attention between the denoising signal and the extracted prototypes. We adopt the official implementation from the TimeCraft repository and extend the input dimension from univariate to multivariate by modifying only the input channel dimension. At inference time, this model requires an additional example time series to guide generation through prototype extraction. To ensure fair comparison with other models, we randomly sample these example prompts from the training set rather than using oracle references. The core generative mechanism remains unchanged, including the prototype extraction, the cross-attention conditioning pathway, and the classifier-free guidance.
T2S (Ge et al., 2025). T2S employs a two-stage latent diffusion framework. In stage one, a convolutional AutoEncoder compresses time series into a fixed 30-position latent space via bilinear interpolation. In stage two, a Diffusion Transformer (Peebles & Xie, 2023) with Adaptive Layer Normalization (AdaLN) performs Rectified Flow (Liu et al., 2023) generation in the latent space. Although the original paper describes a VAE architecture, we follow the official codebase which implements a standard AutoEncoder without the variational component. The original implementation is restricted to univariate series. We extend the encoder and decoder to accept C input channels, where the convolutional layers naturally aggregate cross-variate information.
VerbalTS (Gu et al., 2025). VerbalTS was originally proposed for text-conditioned multivariate time series generation. We include it as a representative of multi-scale diffusion approaches with hierarchical text conditioning mechanisms. Unlike other text-conditioned models that rely on pretrained sentence encoders, VerbalTS trains its text encoder from scratch jointly with the generation model, enabling end-to-end optimization of text-time series alignment. Our implementation follows the
24

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation
official repository and preserves all core components, including the multi-scale patch-based architecture and adaptive layer normalization conditioning.

Text2Motion (Guo et al., 2022). Text2Motion was originally proposed for generating human motion from natural language descriptions. We include this method as a representative of latent-space autoregressive VAE architectures, offering an alternative generative paradigm to diffusion-based approaches. For adaptation to our benchmark, we replace the original token-level word embeddings (which require part-of-speech annotations and language-specific preprocessing) with precomputed sentence embeddings from Qwen3-Embedding-0.6B, projected through a learnable linear layer. This modification ensures consistency with other text-conditioned baselines while eliminating external NLP dependencies. The core generative mechanism, including the two-stage training protocol (autoencoder pretraining followed by conditional latent generator training), remains unchanged.

DiffuSETS (Lai et al., 2025a). DiffuSETS was originally designed for 12-lead ECG generation conditioned on clinical text reports and patient-specific attributes. We include it as a representative of the latent diffusion paradigm, employing a two-stage architecture: a VAE (Kingma & Welling, 2019) compresses time series into latent space, followed by a U-Net (Ronneberger et al., 2015) denoiser with text conditioning via cross-attention. For adaptation to our benchmark, we generalize the input channel dimension to support arbitrary multivariate time series and remove patient-specific attributes (age, sex, heart rate), as these attributes are not consistently available across all benchmark datasets. The core latent diffusion mechanism remains unchanged.

C. Evaluation Metrics Implementation Details
C.1. Metric Implementation Details
In this section, we provide the mathematical formulations and implementation details for the evaluation metrics introduced in the main text. As aforementioned, we categorize these evaluation metrics into two groups: (1) generation fidelity and (2) condition adherence. Furthermore, depending on whether the metric leverages embeddings, we categorize these evaluation metrics into two groups: (1) statistical and (2) embedding-based. The taxonomy of evaluation metrics are listed in Table 20.

Table 20. Taxonomy of Evaluation Metrics for ConTSG

Category Generation Fidelity Condition Adherence

Statistical
· MDD (Marginal Distribution Difference) · ACD (Auto-Correlation Difference) · SD / KD (Skewness / Kurtosis Difference)
· DTW Score (Alignment Distance) · CRPS (Distribution Calibration and Sharpness)

Embedding-based
· FID (Fre´chet Inception Distance) · Precision & Recall
· CTTP Score (Cosine Similarity) · J-FTSD (Joint-Space FID) · Joint Precision & Recall

We denote the real data distribution consisting of n pairs of time series and conditions as Dr = {(x1r, c1), . . . , (xnr , cn)}, where xir  RL×F represents the real time series with length L and F features, and ci represents the corresponding condition. Similarly, we denote the dataset of generated time series produced by any arbitrary conditional generation model G and corresponding conditions as Dg = {(x1g, c1), . . . , (xng , cn)}, where xig = G(ci). We utilize time series encoder and textual description encoder from the trained CTTP model to project time series data and text data into the embedding space respectively. For embedding-based metrics, let ts(·) denote the time series encoder and text(·) denote the text encoder.
C.1.1. GENERATION FIDELITY
These metrics evaluate the quality of generated distribution xg against the real distribution xr without considering condition adherence of the generated time series. The primary focus is to quantify the fidelity of generated time series samples and to assess whether the generator accurately captures the marginal distribution of the real time series data.

Fre´chet Inception Distance (Heusel et al., 2017) Utilizing the Wasserstein-2 distance between the Gaussian approximations of two embeddings, FID assesses the distance between the feature distributions of real and generated data. We compute the embeddings of time series data zid = ts(xid) for d  {r, g} and further approximate these two embedding distributions
25

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

as Gaussian Distributions N (µzr , zr ) and N (µzg , zg ) where µ and  are the empirical mean and covariance. Therefore FID metric is formally formulated as:

FID(Dr, Dg) = µzr - µzg 22 + Tr zr + zg - 2(zr zg )1/2 .

(5)

where µzd and zd for d  {g, r} are calculated as:

1 µzd = n

n

zid,

1 zd = n - 1

n
(zid - µzd )(zid - µzd ).

(6)

i=1

i=1

Precision & Recall (Kynka¨a¨nniemi et al., 2019) While FID provides a statistic of the distance between feature distributions, Precision and Recall can evaluate the fidelity of generated samples and the diversity of generated distribution respectively. These metrics rely on constructing an explicit non-parametric representations of the manifolds of real and generated data in the feature space. Here we use r = {ts(x) | x  Dr} and g = {ts(x) | x  Dg} to denote the sets of embeddings for real and generated time series.
The manifold of  is approximated by forming a hypersphere for each sample embedding v  , where the radius of hypersphere is determined by the distance to its k-th nearest neighbor in . As such, a binary indicator function f (q, ) can be defined to determine whether a query sample q in the embedding space lies within the manifold of :

f (q, ) = 1, if    s.t. q - 2   - NNk(, )2

(7)

0, otherwise,

where NNk(, ) returns k-th nearest feature vector of  from set . Intuitively, f (q, ) indicates if a sample in the embedding space falls within the k-NN hypersphere of at least one sample in the reference set . We adopt k = 5 in our experiments. Now Precision and Recall metrics can be formally formulated leveraging manifold and function f (q, ). Precision measures the fraction of generated samples that fall within the estimated manifold of the real data. A high precision indicates that the generated samples are realistic and resemble the training data. Precision is mathematically formulated as:

1

Precision(r, g) = |g| gg f (g, r).

(8)

Recall measures the fraction of real samples that fall within the estimated manifold of the generated data. A high recall

indicates that the generator covers diversity of the true distribution without mode collapse. Recall is mathematically

formulated as:

1

Recall(g, r) = |r| rr f (r, g).

(9)

Distributional Statistics Following TSGBench (Ang et al., 2023), to assess whether the generated time series captures finegrained temporal properties, we utilize four key statistical measures including marginal distribution difference (MDD) (Ni et al., 2021), auto-correlation difference (ACD) (Lai et al., 2018), skewness difference (SD), and kurtosis difference (KD). For these four metrics, smaller values indicate more similar statistical distributions between the generated time series data and the real-world data.
Marginal Distribution Difference (MDD) measures how closely the distributions of the real and generated series align. The probability density functions of real and generated time series data are approximated using empirical histograms with B bins for each dimension and time step. In our experiments, we discretize the continuous time series values into histograms with B = 32 bins whose boundaries are determined by the dynamic range in the training set. To ensure consistent evaluation, any values in the generated or test sets falling outside this pre-defined range are assigned to the first or last bin. Let pr(b) and pg(b) denote the probability mass in the b-th bin for real and generated data, respectively. MDD is therefore defined as the average absolute difference between two histograms across bins:

1B

MDD(Dr, Dg) = B |pr(b) - pg(b)|.

(10)

b=1

26

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

Auto-Correlation Difference (ACD) evaluates the preservation of temporal dependencies through computing the difference of autocorrelation of real and generated time series. Autocorrelation coefficient k at lag k for a single time series x from dataset D, which measures the linear relationship between observations separated by k time steps, is calculated as:

k(x) =

L-k t=1

(xt

-

µ)(xt+k

Lt=1(xt - µ)2

-

µ) .

(11)

where µ is the mean of this time series. Therefore the average lag k autocorrelation profile for the entire dataset D is

denoted

as

¯k (D)

=

1 |D|

xD k(x). As such, ACD is formally defined as the Euclidean distance between the mean

autocorrelation profile vectors of real and generated data denoted as ¯r and ¯g:

L-1

ACD(Dr, Dg) = ¯r - ¯g2 =

(¯k(Dr) - ¯k(Dg))2.

(12)

k=1

Skewness characterizes difference in the asymmetry of the data distribution around its mean. Given the mean (standard deviation) of the real time series as µr(r) and the generated time series as µg(g), Skewness Difference (SD) is formulated as the difference of Skewness coefficients between the real and generated data distributions:

SD(Dr, Dg) = |S(Dr) - S(Dg)|, where S(Di) = E
i{r,g}

Di - µi 3 . i

(13)

Kurtosis measures the presence of outliers in a distribution, revealing extreme deviations from the mean. Given the mean (standard deviation) of the real time series as µr(r) and the generated time series as µg(g), Kurtosis Difference (KD) is formulated as the difference of Kurtosis coefficients between the real and generated data distributions:

KD(Dr, Dg) = |K(Dr) - K(Dg)|, where K(Di) = E
i{r,g}

Di - µi 4 . i

(14)

C.1.2. CONDITION ADHERENCE
Since the aforementioned metrics exclusively focus on evaluating the generation fidelity and marginal distribution of time series features, they are insensitive to the condition adherence. They fail to penalize realistic samples that are mismatched with their corresponding conditions, making them insufficient for assessing conditional generation. Consequently, we introduce condition-adherence metrics to fairly evaluate whether the generated sample xig adhere to the specific condition ci and preserve the joint distribution properties.

CTTP Score (Gu et al., 2025) Similar to CLIP Score (Radford et al., 2021), CTTP Score measures the direct adherence between the generated time series and its condition using cosine similarity in the latent space:

CTTP

Score

=

1 n

n i=1

ts(xgi ) · text(ci) ts (xig )2 text (ci )2

.

(15)

A higher CTTP score shows better semantic alignment between the embedding vectors of the time series and its corresponding textual description, indicating stronger condition adherence. In our implementation, we compute the CTTP Score between time series and textual descriptions, rather than directly between time series and other condition modalities (e.g., numerical forecasting horizons or categorical labels). This design choice is motivated by our dataset construction process, where each sample is paired with a textual description that semantically encapsulates the conditioning information. As a result, the textual description can serve as a unified semantic proxy for evaluating condition adherence across different conditioning modalities within our benchmark.

Joint Frechet Time Series Distance (J-FTSD) (Narasimhan et al., 2024) J-FTSD extends the FID to the joint feature space of time series and condition to reflect condition adherence. Let X  RL×F be the domain of time series, C be the domain of conditions. Denote the dimension of embedding space of time series and text conditions as k. We define the
Joint Feature Space Z as the image of the Cartesian product X × C under the joint projection :

Z  z  R2k | z = ts(x)  text(c), x  X , c  C , (x, c) = ts(x)  text(c).

(16)

27

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

Here,  denotes concatenation, and (x, c) maps the pair into the 2d-dimensional vector space. Consequently we can construct joint space embeddings zid for d  {g, r} by concatenating the time series and condition embeddings:

zid = (xdi , ci) i : (xdi , ci)  Dd, d  {g, r}.

(17)

As such, J-FTSD is formally formulated as the Fre´chet distance between these joint distributions on joint feature space. The metric function J-FTSD(Dg, Dr) adopts the same formulation as formulae 5 and 6 but operate on the joint feature space 16.

Joint Precision & Recall Complementary to J-FTSD, we extend Precision & Recall metrics on the joint feature space of time series and condition. The formulae for these two metrics remain the same as equations 7, 8 and 9 but operate on the joint feature space 16.

Dynamic Time Warping (DTW) DTW measures the alignment distance between the generated sample xig and the ground truth reference xir associated with the same condition. Given two time series sequences X = (x1, . . . , xN ) and Y = (y1, . . . , yM ), DTW computes the optimal sequence alignment by minimizing the cumulative distance between aligned
points. Under defined local distance measure d(xi, yj), typically the Euclidean distance xi - yj2, DTW distance is computed using dynamic programming to find the minimum cumulative cost matrix Dp  RN×M . Each element Dp(i, j)
represents the minimum distance between the subsequences X1:i and Y1:j, governed by the following recurrence relation:

 Dp(i - 1, j) 

(insertion)

Dp(i, j) = d(xi, yj) + min Dp(i, j - 1)

(deletion)

(18)

Dp(i - 1, j - 1) (match)

where boundary conditions are Dp(0, 0) = 0 and Dp(i, 0) = Dp(0, j) =  for i, j > 0. The final DTW distance is given by Dp(N, M ) and thus we denote operator DTW(·, ·):

DTW(X, Y ) = Dp(N, M ), where |X| = M, |Y | = N.

(19)

Utilizing operator DTW(·, ·), for each sample in the real-world dataset Dr with condition ci, we generate K time series {xig,k}Kk=1, take the minimum as sample score so as to leverage best-of-K strategy to account for the stochasticity of generation, and eventually average over samples:

1 DTW Score = n

n

min
k{1...K}

DTW(xir

,

xig,k

),

where xig,k = G(ci).

(20)

i=1

Continuous Ranked Probability Score (CRPS) (Ansari et al., 2024) CRPS generalizes the Mean Absolute Error (MAE) to the probabilistic setting by measuring the distance between the empirical cumulative distribution of generated samples and a reference value, therefore can better assess both the calibration and sharpness of the generation distribution.
Let Fcd denote the cumulative distribution function (CDF) of the generated probabilistic forecast, and y be the ground truth observation value. The CRPS measures the integrated squared difference between the forecast CDF and the Heaviside step function of the observation, and can be mathematically formulated as:



CRPS(Fcd, y) =

(Fcd(z) - I(z  y))2 dz.

(21)

-

where I(·) is the indicator function. Since generative models produce samples rather than CDF, this integral is approximated by leveraging the key property of CRPS showed by (Gneiting & Raftery, 2007) which is mathematically formulated as:

CRPS(F,

y)

=

EX F

[|X

-

y|]

-

1 2 EX,XF

[|X

-

X  |],

(22)

where X and X are independent random variables drawn from distribution F and E[·]. Leveraging the strategy of aggregating over all K samples, let y^t = {y^t(1), . . . , y^t(K)} denote the set of K generated samples at time step t for one

28

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation
instance, and yt be the corresponding real-world data value. Utilizing the approximation equation 22, the instance-level CRPS at time t is computed as:

1 CRPS(t) =
S

K

|y^t(i)

-

yt|

-

1 2S2

K

K
|y^t(i) - y^t(j)|.

(23)

i=1

i=1 j=1

The final metric for one instance is computed as the average CRPS across all time steps.
C.2. CTTP Model Training
The Contrastive Text-Time Series Pretraining (CTTP) is used to bridge time series representation and condition representation. In the evaluation setup of our benchmark, we train CTTP model for each dataset so as to obtain time-series encoder ts and text encoder text. These encoders after training can be utilized to produce corresponding embedding representation which is critical for embedding-based metrics introduced in Appendix C.1.
Conceptually similar to the CLIP model (Radford et al., 2021), CTTP training leverages contrastive learning technique to align time series data and associated textual conditions. Specifically, let X  RB×K×L denote a batch of B time-series samples and C  NB×M represent the associated tokenized textual description data. Following VerbalTS (Gu et al., 2025), we utilize PatchTST (Nie, 2022) as the temporal encoder ts(·) and Long-clip (Zhang et al., 2024a) as the tokenizer and text encoder text(·). As shown in Algorithm 2, these encoders project the raw data into a unified d-dimensional embedding space, yielding Zx  RB×d and Zc  RB×d respectively. Then we compute the cosine similarity score matrix S  RB×B of Zx and Zc. Subsequently, cross-entropy loss of similarity matrix S against ground truth label identity matrix I  RB×B can be calculated across two dimensions. The optimization target is to minimize a bidirectional cross-entropy loss that maximizes the similarity between true pairs while penalizing all mismatched pairs.

Algorithm 2 CTTP

1: Input: Batch of aligned time-series data X and textual descriptions C.

2: Output: Bidirectional cross-entropy loss Ltotal.

3: // Embeddings Extraction

4: Zx  ts(X)

5: Zc  text(C)

6:

7: // Similarity Computation

8: S  Similarity(Zx, Zc)

9:

10: // Compute Cross-Entropy Loss

11: Lts align  CrossEntropy(S, I, dim = 1)

12: Ltxt align  CrossEntropy(S, I, dim = 0)

13:

14: // Compute Bidirectional Cross-Entropy Loss

15:

Ltotal



1 2

(Lts

align

+

Ltxt

align)

16: return Ltotal

We train the CTTP model with batch size B = 256, learning rate 1 × 10-4, early stopping patience of 50 epochs, and a maximum of 500 epochs. Table 21 reports the validation accuracy for each dataset. Note that under a batch size of 256, the random baseline accuracy is merely 1/256  0.39%. Even the lowest observed accuracy (16.09% on TelecomTS-Segment) exceeds this baseline by over 40×, indicating that CTTP successfully learns meaningful alignment between time series and textual conditions. The variation in accuracy across datasets reflects inherent differences in task difficulty, such as the discriminability of textual descriptions and the complexity of temporal patterns.
29

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

Table 21. CTTP validation accuracy across different datasets. The values represent the maximum validation accuracy achieved during training.

Dataset
TelecomTS TelecomTS-Segment PTB-XL (Morph.) PTB-XL (Concept) Weather (Morph.) Weather (Concept)

Acc (%)
37.19 16.09 28.31 33.85 20.52 20.90

Dataset
ETTm1 Istanbul Traffic Synth-M Synth-U Air Quality

Acc (%)
16.59 17.45 98.35 92.52 18.37

D. Additional Experimental Results
D.1. Main Results (RQ1)
D.1.1. COMPLETE RESULTS
This section provides the complete per-dataset evaluation results for all benchmark models, as summarized in Section 4.1. Tables 22­31 report detailed metric scores across all ten dataset configurations, including both generation fidelity metrics (ACD, SD, KD, MDD, FID, Precision, Recall) and condition adherence metrics (J-FTSD, Joint Precision, Joint Recall, CTTP Score). Each entry reports the mean and standard deviation over three independent runs. Bold values indicate the best-performing model for each metric on each dataset.

Table 22. Evaluation results for Synth-U dataset

Model
Bridge DiffuSETS T2S TEdit Text2Motion TimeVQVAE TimeWeaver TTSCGAN VerbalTS WaveStitch

ACD
0.0314±0.0116 0.0552±0.0113 0.0489±0.0098 0.0658±0.0015 0.0821±0.0067 0.0800±0.0016 0.0735±0.0098 0.2849±0.0016 0.0601±0.0037 0.0491±0.0262

SD
0.0974±0.0775 0.1404±0.1382 0.4960±0.4106 0.1632±0.1069 0.0715±0.0413 0.0457±0.0244 0.0469±0.0182 0.1043±0.0575 0.0317±0.0252 0.1236±0.1098

KD
0.6417±0.0562 0.8331±0.8645 0.7833±0.4301 0.2876±0.1147 0.2046±0.0673 0.7758±0.0165 0.5210±0.1770 0.1352±0.0728 0.3739±0.0601 0.3398±0.1632

MDD
0.0282±0.0001 0.0203±0.0050 0.0358±0.0165 0.0216±0.0056 0.0150±0.0029 0.0245±0.0012 0.0207±0.0058 0.0233±0.0049 0.0156±0.0020 0.0354±0.0135

FID
50.1814±3.8816 41.5913±8.8965 144.4827±27.3339 49.1590±7.0552 58.5985±12.4265 75.7424±2.1271 55.4405±14.8883 119.9663±24.7832 37.9622±1.8307 54.6382±15.5595

J-FTSD
55.1401±2.8398 46.5630±10.9944 156.3209±27.2652 59.9647±6.4816 66.6559±11.6903 83.9404±2.0995 65.8629±14.1253 132.8113±21.8516 41.3352±2.0161 66.8958±16.9945

Precision
0.5906±0.0411 0.5842±0.0770 0.2330±0.1987 0.5448±0.0081 0.5509±0.0702 0.7228±0.0130 0.6252±0.0406 0.1867±0.0720 0.6828±0.0204 0.4412±0.1738

Recall
0.0745±0.0104 0.2054±0.0257 0.0000±0.0000 0.1217±0.0344 0.0562±0.0302 0.0170±0.0011 0.1102±0.0759 0.0000±0.0000 0.2021±0.0208 0.1430±0.1044

Joint Precision
0.8228±0.0404 0.8427±0.1608 0.2862±0.0746 0.7358±0.0081 0.7030±0.0355 0.7329±0.0121 0.7436±0.0266 0.1907±0.0009 0.9524±0.0080 0.6172±0.1921

Joint Recall
0.4752±0.0240 0.6600±0.1285 0.0140±0.0109 0.3991±0.0576 0.3052±0.0937 0.2192±0.0138 0.3437±0.1154 0.0290±0.0273 0.7239±0.0285 0.3617±0.1186

CTTP Score
22.9919±0.7649 24.6628±4.6115 10.3251±4.3402 20.3756±0.7434 17.6067±1.7010 16.0165±0.2354 19.0760±1.8983 9.3852±2.2275 27.2469±0.5870 19.1474±1.8355

Table 23. Evaluation results for Synth-M dataset

Model
Bridge DiffuSETS T2S TEdit Text2Motion TimeVQVAE TimeWeaver TTSCGAN VerbalTS WaveStitch

ACD
0.0580±0.0239 0.0413±0.0190 0.0753±0.0360 0.0556±0.0061 0.0764±0.0132 0.0733±0.0028 0.0580±0.0070 0.2652±0.0004 0.0514±0.0023 0.0539±0.0225

SD
0.1382±0.1703 0.0847±0.0714 0.3972±0.1165 0.0314±0.0065 0.0572±0.0455 0.0282±0.0148 0.0508±0.0214 0.0990±0.0456 0.0405±0.0323 0.2148±0.1342

KD
0.4220±0.2471 0.1596±0.1405 1.4948±0.1724 0.2552±0.1086 0.2479±0.0465 0.6307±0.1129 0.1758±0.1539 0.6451±0.0323 0.1925±0.0603 0.3029±0.2332

MDD
0.0294±0.0003 0.0209±0.0030 0.0305±0.0047 0.0155±0.0016 0.0140±0.0007 0.0211±0.0006 0.0155±0.0010 0.0397±0.0013 0.0153±0.0002 0.0137±0.0042

FID
46.1556±12.6821 35.6547±6.2623 113.6724±7.3416 35.1944±0.9255 60.4473±16.6599 60.6209±0.4303 31.1737±2.9653 99.8948±16.5567 33.5643±5.2371 22.2000±7.4868

J-FTSD
53.5891±12.6868 42.0699±9.1293 123.0193±7.4631 43.8138±1.1236 65.1781±16.1543 66.8617±0.3628 40.3713±3.1536 111.5366±15.1510 38.0327±5.2630 36.2440±6.5269

Precision
0.6962±0.0760 0.6668±0.1098 0.4246±0.0932 0.7398±0.0177 0.8230±0.0588 0.8671±0.0062 0.7210±0.0280 0.0789±0.0287 0.7711±0.0128 0.5129±0.0297

Recall
0.1510±0.0483 0.2551±0.0755 0.0000±0.0000 0.2298±0.0203 0.0746±0.0694 0.0531±0.0037 0.2762±0.0169 0.0001±0.0001 0.2871±0.0439 0.5322±0.1085

Joint Precision
0.4030±0.0832 0.5958±0.2316 0.1523±0.0379 0.6117±0.0138 0.6024±0.0818 0.5932±0.0054 0.5937±0.0572 0.0726±0.0003 0.7493±0.0315 0.2262±0.0381

Joint Recall
0.2333±0.0861 0.4658±0.1855 0.0096±0.0025 0.3923±0.0090 0.2304±0.1378 0.2115±0.0043 0.4322±0.0477 0.0166±0.0080 0.5033±0.0727 0.5402±0.1755

CTTP Score
18.8397±0.5783 21.2378±4.6499 1.6491±3.4922 21.2387±0.3449 19.9581±1.7206 19.8635±0.1381 20.8463±0.9775 10.1633±0.3424 24.6611±0.8267 11.9796±2.1070

D.1.2. GENERATION QUALITY VISUALIZATION AND CASE STUDIES
To complement the quantitative metrics reported in Section 4.1, we provide qualitative visualizations of generated time series across all benchmark datasets. Figures 14­23 present side-by-side comparisons of all evaluated models, where each subplot displays the ground truth (blue) against the generated distribution characterized by the median (red line) and quantile bands (25%­75% dark, 10%­90% light) computed from 10 independent samples. These visualizations offer intuitive insights into each model's ability to capture temporal dynamics, variance calibration, and condition adherence that may not be fully reflected by aggregate metrics.
D.2. Morphological vs. conceptual Conditions (RQ2)
This section extends the analysis in Section 4.2 by visualizing the rank stability of models across morphological and conceptual conditions. Figure 24 reveals substantial rank shifts when switching between condition types: many models lie far from the diagonal, indicating that their relative performance is highly sensitive to the semantic abstraction level
30

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

Table 24. Evaluation results for AirQuality Beijing dataset

Model
Bridge DiffuSETS T2S TEdit Text2Motion TimeVQVAE TimeWeaver TTSCGAN VerbalTS WaveStitch

ACD
0.0337±0.0069 0.0467±0.0051 0.1079±0.0264 0.0369±0.0082 0.0518±0.0023
-- 0.0400±0.0090 0.1453±0.0008 0.0433±0.0067 0.0497±0.0059

SD
0.2094±0.0560 0.1189±0.0173 0.3482±0.1443 0.0975±0.0171 0.1444±0.0659
-- 0.3657±0.3719 0.3554±0.0263 0.1661±0.0616 0.4480±0.0737

KD
0.7371±0.0695 0.3604±0.1177 1.5353±0.2622 0.5143±0.0824 0.5000±0.0190
-- 1.1163±0.9383 1.1388±0.0845 0.6455±0.0758 3.6987±2.3803

MDD
0.0290±0.0012 0.0249±0.0016 0.0382±0.0045 0.0213±0.0008 0.0246±0.0003 0.0469±0.0199 0.0223±0.0011 0.0408±0.0021 0.0238±0.0021 0.0256±0.0020

FID
159.6945±20.3313 121.7182±10.4377 223.7563±25.8692 109.7493±5.9814 83.4466±5.3609
-- 108.5736±17.3495 260.6018±8.8347 110.4491±15.4693 145.6924±7.8526

J-FTSD
160.6358±20.4623 122.5601±10.4545 225.3871±25.8658 110.7139±5.9993 84.2614±5.3351
-- 109.5707±17.4145 261.9308±8.7990 111.3438±15.5030 146.9278±7.8691

Precision
0.8957±0.0040 0.9183±0.0111 0.0029±0.0040 0.8953±0.0242 0.9126±0.0092
-- 0.8407±0.0568 0.9905±0.0097 0.8862±0.0116 0.8476±0.0803

Recall
0.0458±0.0079 0.0466±0.0323 0.3919±0.2264 0.1456±0.0287 0.1368±0.0201
-- 0.1144±0.0389 0.0002±0.0003 0.1045±0.0216 0.0829±0.0568

Joint Precision
0.8081±0.0362 0.8985±0.0229 0.1564±0.0922 0.8407±0.0087 0.9610±0.0023
-- 0.8267±0.0478 0.6790±0.0311 0.8719±0.0354 0.7385±0.0465

Joint Recall
0.2602±0.0690 0.4681±0.0790 0.0281±0.0088 0.5160±0.0375 0.7296±0.0086
-- 0.4719±0.0876 0.0272±0.0046 0.4574±0.1072 0.2315±0.0299

CTTP Score
5.2102±0.7037 6.1099±0.2019 -1.2634±1.6210 4.8901±0.5026 6.9590±0.1399
-- 4.8673±0.3098 4.5250±0.2955 5.9685±0.3691 4.0933±0.2179

Table 25. Evaluation results for ETTm1 dataset

Model
Bridge DiffuSETS T2S TEdit Text2Motion TimeVQVAE TimeWeaver TTSCGAN VerbalTS WaveStitch

ACD
0.1069±0.0210 0.1420±0.0860 0.1150±0.1321 0.1692±0.0495 0.1114±0.0418 0.0530±0.0183 0.0840±0.0421 0.3025±0.0004 0.1580±0.0851 0.0522±0.0263

SD
0.4925±0.0322 8.5331±11.3647 1.1269±1.5301 0.7493±0.1854 0.8648±1.1884 1.9516±0.1991 1.0313±0.2021 1.4856±0.1301 1.7842±1.0089 0.8096±0.6837

KD
3.3521±0.0656 258.7216±428.3528
3.1332±1.8773 3.8786±0.3975 8.8360±13.6306 9.3044±5.1511 4.1960±0.9162 4.8669±0.0738 4.5994±2.9595 2.1095±1.8257

MDD
0.0272±0.0021 0.0424±0.0130 0.0540±0.0060 0.0233±0.0058 0.0243±0.0050 0.0358±0.0025 0.0284±0.0096 0.0397±0.0128 0.0312±0.0158 0.0346±0.0037

FID
42.0076±9.4701 56.4434±37.3998 95.0026±49.3734 23.1472±1.4568 48.5253±14.8678 28.2658±6.1412 48.9813±10.8794 109.9494±39.1794 48.1654±36.0804 57.2002±27.9974

J-FTSD
42.6005±9.5725 56.9916±37.5302 95.6860±49.4863 23.8535±1.4339 48.9968±14.9018 28.7677±6.1357 49.6649±10.8627 110.6666±39.2287 48.7078±36.0243 57.7153±27.9582

Precision
0.6698±0.0357 0.6126±0.4295 0.1115±0.0891 0.6089±0.0985 0.6105±0.1036 0.7515±0.0630 0.6918±0.0608 0.5916±0.2918 0.5001±0.1365 0.6116±0.1092

Recall
0.4616±0.0276 0.3859±0.2482 0.3323±0.2293 0.5883±0.0525 0.2676±0.1474 0.3961±0.0843 0.6074±0.0544 0.0310±0.0434 0.4321±0.2522 0.4460±0.1493

Joint Precision
0.6089±0.0069 0.5409±0.1071 0.2886±0.1804 0.4828±0.0635 0.6579±0.0434 0.6195±0.0233 0.4462±0.0399 0.5872±0.0650 0.5983±0.1195 0.5980±0.0778

Joint Recall
0.4793±0.0305 0.4806±0.2584 0.2387±0.1566 0.5748±0.0152 0.4560±0.0629 0.6089±0.0345 0.5810±0.0774 0.2304±0.1585 0.4766±0.1713 0.4833±0.1294

CTTP Score
1.8156±0.3851 1.9019±1.1863 3.4514±0.9474 1.9972±0.0725 1.9365±0.4914 2.1357±0.1940 2.6474±0.6668 1.5059±0.4984 2.0389±0.6608 1.9481±0.8432

Table 26. Evaluation results for Istanbul Traffic dataset

Model
Bridge DiffuSETS T2S TEdit Text2Motion TimeVQVAE TimeWeaver TTSCGAN VerbalTS WaveStitch

ACD
0.0294±0.0019 0.1470±0.0883 0.2451±0.0331 0.0310±0.0013 0.0573±0.0095 0.2015±0.2004 0.0267±0.0040 0.3399±0.0019 0.0236±0.0064 0.0215±0.0143

SD
0.4812±0.2556 2.2346±1.5908 0.3192±0.3463 0.2893±0.1829 0.1450±0.0801 0.3223±0.1256 0.2055±0.1461 0.1098±0.1733 0.1323±0.1749 0.4960±0.5091

KD
0.1500±0.1943 12.9962±11.1741 1.5178±1.0697 0.2992±0.2275 0.0779±0.0754 2.0618±2.2354 0.5147±0.1591 0.3162±0.3823 0.0921±0.1554 0.5819±0.8230

MDD
0.0363±0.0051 0.0408±0.0191 0.0281±0.0067 0.0176±0.0020 0.0102±0.0015 0.0401±0.0049 0.0200±0.0013 0.0205±0.0065 0.0114±0.0013 0.0179±0.0085

FID
14.5301±2.1501 28.6764±21.1976 142.4714±16.1469 7.4086±1.4342 2.7859±1.9849 33.9157±29.6866 8.5903±1.4171 10.5484±1.9197 4.2518±1.3981 10.9867±7.3042

J-FTSD
15.0547±2.1321 29.3117±21.3957 143.6973±16.1239 8.1024±1.4414 3.1654±1.9895 34.7945±29.9070 9.3096±1.3745 11.4818±1.7699 4.6698±1.4376 11.7453±7.4962

Precision
0.9347±0.0086 0.5917±0.3045 0.0000±0.0000 0.8277±0.0097 0.8548±0.0071 0.4548±0.5252 0.6785±0.0899 0.2352±0.3364 0.8212±0.0148 0.8430±0.0097

Recall
0.2896±0.0140 0.3923±0.3925 0.1653±0.1908 0.8405±0.0470 0.7271±0.0547 0.1102±0.1273 0.8306±0.0199 0.1501±0.0575 0.8730±0.0154 0.8246±0.0213

Joint Precision
0.6885±0.0511 0.6023±0.1723 0.0052±0.0042 0.6223±0.0059 0.8559±0.0074 0.3241±0.3565 0.6244±0.0079 0.5300±0.0348 0.8438±0.0212 0.5964±0.0711

Joint Recall
0.5944±0.0409 0.6127±0.1566 0.0708±0.0754 0.7407±0.0267 0.8218±0.0083 0.3084±0.2928 0.7515±0.0314 0.6533±0.0315 0.8502±0.0111 0.7315±0.0028

CTTP Score
4.7030±0.0194 4.7812±0.0942 5.4458±0.1697 4.7114±0.0205 4.8171±0.0368 4.7204±0.2820 4.7321±0.0164 4.7343±0.0327 4.8572±0.0309 4.8229±0.1616

Table 27. Evaluation results for TelecomTS dataset

Model
Bridge DiffuSETS T2S TEdit Text2Motion TimeVQVAE TimeWeaver TTSCGAN VerbalTS WaveStitch

ACD
0.0487±0.0105 0.0510±0.0225 0.1037±0.0461 0.0661±0.0202 0.0791±0.0194 0.0945±0.0048 0.0405±0.0017 0.0968±0.0016 0.0681±0.0123 0.0359±0.0131

SD
0.9491±0.4001 0.7260±0.4397 0.5110±0.3631 0.5190±0.2698 0.9901±0.5188 0.6221±0.5406 0.5127±0.4358 0.6770±0.1124 0.7456±0.4566 9.1142±7.8505

KD
9.1130±2.3490 5.6203±2.3342 7.4168±1.4742 8.3735±1.4039 6.9028±7.4454 9.2415±5.1114 7.8862±1.0464 7.1605±0.0680 3.0511±2.1876 520.8309±673.3080

MDD
0.0328±0.0092 0.0237±0.0061 0.0352±0.0099 0.0240±0.0027 0.0134±0.0013 0.0356±0.0044 0.0270±0.0033 0.0336±0.0049 0.0244±0.0123 0.0254±0.0027

FID
91.1473±30.6606 65.9887±43.5030 155.1567±53.1827 58.6366±7.6197 53.5293±49.7279 123.6608±29.9672 61.9709±8.2364 162.4984±16.7258 70.7905±49.6275 52.9260±3.8831

J-FTSD
97.2862±34.8033 71.4901±48.4934 161.8594±51.7074 62.8779±7.5856 57.1443±55.5941 127.4633±29.4431 66.1418±8.0489 165.5502±16.3078 76.3063±54.6152 57.0388±3.8700

Precision
0.6494±0.2329 0.5795±0.0342 0.6012±0.1847 0.5381±0.0291 0.6083±0.0382 0.4742±0.0994 0.5307±0.0174 0.4214±0.1161 0.4344±0.1827 0.5677±0.0573

Recall
0.1973±0.1341 0.2395±0.1685 0.0556±0.0582 0.4052±0.1134 0.3191±0.0470 0.1486±0.0431 0.3902±0.0212 0.0081±0.0087 0.4723±0.1165 0.5003±0.0939

Joint Precision
0.1758±0.0312 0.2928±0.0737 0.1321±0.0769 0.1658±0.0115 0.6771±0.0478 0.1206±0.0329 0.1752±0.0253 0.1009±0.0369 0.2819±0.1858 0.1884±0.0125

Joint Recall
0.2073±0.1534 0.3366±0.1251 0.0390±0.0366 0.4103±0.0534 0.5239±0.0683 0.1557±0.0355 0.3628±0.0304 0.0343±0.0203 0.4065±0.1094 0.4248±0.0151

CTTP Score
1.6884±1.3374 4.5457±3.3877 0.1068±1.1882 2.1875±0.3157 9.3332±5.8628 1.1549±0.2186 2.2295±0.7243 1.0022±0.3437 4.8817±4.8977 2.9696±0.4048

Table 28. Evaluation results for Weather Conceptual dataset

Model
Bridge DiffuSETS T2S TEdit Text2Motion TimeVQVAE TimeWeaver TTSCGAN VerbalTS WaveStitch

ACD
0.0343±0.0026 0.1379±0.0601 0.0932±0.0099 0.0341±0.0079 0.0500±0.0067 0.0707±0.0160 0.0417±0.0111 0.1674±0.0007 0.0312±0.0063 0.0360±0.0078

SD
19.5672±0.0892 19.1210±0.2734 18.8126±0.2219 23.4401±3.5566 18.1200±0.0912 19.0337±0.1169 30.7571±5.0285 19.5566±0.0473 16.8770±0.3247 19.3397±3.0419

KD
2320.6266±0.5614 2317.8549±1.5389 2315.7835±3.1762 2362.1122±232.1081 2298.9082±3.6489 2319.5249±4.1065 2618.7799±427.4573 2319.8547±0.0190 2119.4812±115.5857 2381.9672±223.8178

MDD
0.0205±0.0002 0.0395±0.0004 0.0303±0.0120 0.0087±0.0006 0.0077±0.0002 0.0263±0.0006 0.0092±0.0009 0.0278±0.0014 0.0069±0.0005 0.0100±0.0015

FID
45.0646±12.7574 149.2328±16.4051 110.0314±70.9398 12.0106±0.3898 5.5376±0.3020 47.5908±4.9055 14.5267±2.7804 77.7704±8.0560
6.7655±0.4107 23.5472±10.8784

J-FTSD
47.7810±13.0501 156.1811±15.6110 114.0980±71.4178 14.0126±0.3361 6.8965±0.3269 53.5766±5.1236 16.7852±2.8460 87.3545±6.9016
8.2458±0.4857 25.8877±11.4028

Precision
0.7533±0.0367 0.5943±0.5162 0.1852±0.2814 0.8595±0.0103 0.9215±0.0068 0.3864±0.0614 0.8554±0.0144 0.0988±0.0421 0.9062±0.0115 0.8214±0.0593

Recall
0.0292±0.0035 0.0025±0.0027 0.2594±0.2369 0.4530±0.0183 0.5861±0.0076 0.0030±0.0033 0.3404±0.0782 0.0023±0.0040 0.5810±0.0376 0.3806±0.1746

Joint Precision
0.6301±0.0803 0.1057±0.0414 0.2071±0.2433 0.8321±0.0394 0.9726±0.0013 0.2642±0.0303 0.7838±0.0635 0.1047±0.0207 0.9365±0.0206 0.6773±0.1797

Joint Recall
0.2497±0.0523 0.0368±0.0335 0.2154±0.2516 0.7543±0.0223 0.9174±0.0080 0.1413±0.0256 0.6519±0.1023 0.0302±0.0133 0.8643±0.0387 0.5343±0.2120

CTTP Score
27.3101±2.2800 16.0544±1.6389 20.2179±6.5903 30.2036±0.6333 32.8174±0.0093 22.9355±0.3264 29.3724±1.0899 19.4969±0.6018 32.0586±0.3861 28.1586±2.5472

Table 29. Evaluation results for Weather Morphological dataset

Model
Bridge DiffuSETS T2S TEdit Text2Motion TimeVQVAE TimeWeaver TTSCGAN VerbalTS WaveStitch

ACD
0.0434±0.0056 0.1140±0.0194 0.1051±0.0062 0.0678±0.0148 0.0537±0.0011 0.0743±0.0107 0.0577±0.0045 0.1674±0.0003 0.0380±0.0095 0.0847±0.0280

SD
20.2137±1.0936 19.3972±0.0958 18.9384±0.1181 22.1650±2.8657 16.9457±0.8890 19.5004±0.0346 30.4996±9.8795 19.5790±0.0341 19.9470±5.1280 23.5656±3.5672

KD
2332.3187±23.7888 2316.9628±0.8818 2307.1773±15.1844 2419.3456±169.2376 2202.2627±81.5057 2320.3193±5.6500 3074.8412±1242.8652 2317.6421±0.0104 2189.2177±79.7855 2753.7917±388.6124

MDD
0.0247±0.0019 0.0351±0.0073 0.0379±0.0060 0.0218±0.0031 0.0116±0.0008 0.0276±0.0012 0.0209±0.0031 0.0287±0.0021 0.0131±0.0015 0.0230±0.0010

FID
64.8944±13.2709 157.8052±30.8667 192.1624±16.7269 65.5004±3.5415 28.5415±3.2102 56.0410±1.7473 59.2733±7.1994 90.0769±2.5817 27.5585±0.6906 73.5734±26.5046

J-FTSD
66.2769±13.2006 159.6305±30.7734 194.2186±16.1008 67.7105±3.5083 29.2164±3.2280 58.1840±1.7424 61.5426±7.1911 92.3755±2.5714 28.4955±0.7503 75.6773±26.4374

Precision
0.6966±0.0382 0.6047±0.0700 0.0262±0.0197 0.6801±0.1054 0.8674±0.0180 0.4939±0.1206 0.6905±0.0756 0.3608±0.0361 0.8168±0.0375 0.6954±0.1230

Recall
0.0536±0.0298 0.0000±0.0000 0.0000±0.0000 0.2309±0.0457 0.2289±0.0476 0.0224±0.0178 0.1913±0.0212 0.0114±0.0077 0.3803±0.0366 0.1049±0.0660

Joint Precision
0.5948±0.0314 0.3559±0.1084 0.1502±0.0008 0.4573±0.0650 0.8948±0.0168 0.4527±0.0118 0.4632±0.0466 0.3905±0.0179 0.7990±0.0427 0.4726±0.0331

Joint Recall
0.3425±0.0798 0.0432±0.0213 0.0246±0.0032 0.3496±0.0237 0.7569±0.0231 0.2782±0.0165 0.3435±0.0263 0.1065±0.0104 0.6867±0.0249 0.2945±0.1092

CTTP Score
9.3509±0.6411 6.6785±0.4084 5.9304±0.2041 7.0731±0.0988 12.2402±0.2928 7.1866±0.1688 6.9464±0.2249 7.5842±0.1109 11.0544±0.3955 7.0805±0.4286

31

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

Table 30. Evaluation results for PTB-XL Conceptual dataset

Model
Bridge DiffuSETS T2S TEdit Text2Motion TimeVQVAE TimeWeaver TTSCGAN VerbalTS WaveStitch

ACD
0.0623±0.0109 0.1051±0.0163 0.2110±0.0467 0.0861±0.0166 0.3232±0.0300 0.1330±0.0069 0.0957±0.0134 0.1191±0.0052 0.0877±0.0035 0.2455±0.0231

SD
2.8098±0.0209 5.8130±2.0835 3.2119±0.2035 2.7860±0.0251 3.6515±0.3254 3.0693±0.0762 2.7221±0.0887 2.8939±0.0169 2.7724±0.0393 2.9168±0.1337

KD
184.4093±0.2316 212.3178±45.9144 177.6389±4.7735 182.9535±0.4488 176.4981±6.7947 178.4336±5.5833 182.5281±1.0799 185.1279±0.0856 182.9009±0.4347 183.0252±1.0258

MDD
0.0149±0.0004 0.0187±0.0109 0.0296±0.0113 0.0123±0.0031 0.0184±0.0003 0.0169±0.0001 0.0166±0.0024 0.0099±0.0010 0.0147±0.0024 0.0454±0.0030

FID
324.8132±8.8372 247.9444±75.7033 264.7998±77.9925 250.0269±17.9467 375.3458±11.3807 336.9363±5.3872 226.2710±35.8371 253.2181±44.4526 291.2634±22.8198 159.5548±18.2590

J-FTSD
336.5941±8.4960 277.3275±56.9501 298.9812±71.9978 283.1505±12.3875 384.0842±10.1483 348.3181±4.9416 269.3634±34.6358 283.2832±37.8909 312.2934±16.3870 200.7510±16.2223

Precision
0.9994±0.0011 0.7419±0.3434 0.5946±0.1745 0.7050±0.1150 1.0000±0.0000 1.0000±0.0000 0.6708±0.0833 0.8003±0.1479 0.7965±0.2009 0.3872±0.1124

Recall
0.0000±0.0000 0.0027±0.0023 0.0005±0.0008 0.0000±0.0000 0.0000±0.0000 0.0000±0.0000 0.0003±0.0003 0.0000±0.0000 0.0000±0.0000 0.0010±0.0020

Joint Precision
0.5886±0.0157 0.4659±0.2270 0.4369±0.1171 0.5127±0.0309 0.4729±0.0241 0.5535±0.0279 0.3922±0.0087 0.5071±0.0272 0.5801±0.0384 0.3751±0.0228

Joint Recall
0.0002±0.0003 0.0224±0.0357 0.0030±0.0041 0.0015±0.0027 0.0000±0.0000 0.0000±0.0000 0.0070±0.0046 0.0002±0.0005 0.0000±0.0000 0.0106±0.0123

CTTP Score
219.3064±2.9385 234.0506±9.7990 251.9576±41.4880 247.6307±9.3556 202.0106±3.7835 213.6566±2.1786 247.5866±7.5712 237.0574±19.2253 231.1296±10.9904 301.7921±35.3379

Table 31. Evaluation results for PTB-XL Morphological dataset

Model
Bridge DiffuSETS T2S TEdit Text2Motion TimeVQVAE TimeWeaver TTSCGAN VerbalTS WaveStitch

ACD
0.0561±0.0069 0.1072±0.0214 0.1938±0.0339 0.0896±0.0067 0.2502±0.0827 0.1271±0.0131 0.1583±0.0744 0.1137±0.0114 0.0806±0.0009 0.1745±0.0565

SD
2.8160±0.0264 2.6434±0.4425 3.5991±0.9877 2.8194±0.0438 4.7425±0.1136 3.8563±0.7084 2.9044±0.1796 2.8947±0.0903 2.7478±0.0734 2.9124±0.1740

KD
184.2775±0.0876 157.9633±33.0249 176.7059±6.9755 182.7912±0.4054 165.2220±3.7201 204.6594±31.9805 182.1393±1.1913 185.0735±0.1622 182.2294±0.8419 182.5091±0.5141

MDD
0.0158±0.0004 0.0134±0.0048 0.0295±0.0149 0.0107±0.0013 0.0192±0.0001 0.0167±0.0004 0.0276±0.0136 0.0095±0.0007 0.0147±0.0018 0.0415±0.0090

FID
500.8181±26.0678 313.8154±93.6001 399.7197±70.8724 258.1951±37.9238 558.6359±0.9435 541.0195±10.8172 414.3049±42.5995 285.7187±26.8165 410.6861±20.8180 397.0965±128.0726

J-FTSD
513.6664±22.7653 346.6596±89.2739 437.2591±62.4090 292.2583±34.9973 564.2688±0.3375 554.5409±9.8160 446.2753±44.4224 324.8612±32.3804 440.4774±22.6577 433.9989±125.4409

Precision
0.5895±0.3693 0.4795±0.2270 0.9020±0.0396 0.8967±0.0563 0.9998±0.0003 0.9472±0.0359 0.6742±0.0786 0.8935±0.0274 0.4398±0.4801 0.5732±0.1572

Recall
0.0000±0.0000 0.0073±0.0043 0.0021±0.0021 0.0009±0.0010 0.0002±0.0003 0.2059±0.1926 0.0003±0.0005 0.0010±0.0018 0.0035±0.0025 0.0025±0.0022

Joint Precision
0.3423±0.0101 0.4268±0.0776 0.4022±0.0374 0.5207±0.0606 0.3270±0.0009 0.2991±0.0128 0.4823±0.0609 0.5270±0.0173 0.3800±0.1228 0.4787±0.0527

Joint Recall
0.0011±0.0003 0.0173±0.0132 0.0026±0.0026 0.0047±0.0024 0.0003±0.0005 0.0231±0.0257 0.0049±0.0053 0.0049±0.0054 0.0015±0.0009 0.0146±0.0120

CTTP Score
140.6902±12.3004 211.1689±39.4551 150.1159±18.8086 256.6325±15.3421 115.7349±0.4308 120.2263±3.5252 153.4790±20.0120 240.9490±37.7297 183.1183±26.2431 140.0256±65.4110

of the conditioning signal. For instance, some models excel under morphological descriptions that explicitly specify temporal patterns, yet underperform when conditioned on conceptual descriptions that require implicit domain knowledge mapping. This divergence underscores that semantic abstraction level constitutes a critical axis for benchmarking conditional generation--evaluations conducted under only one condition type may yield conclusions that do not generalize to the other. The dataset-dependent patterns (compare PTB-XL vs. Weather panels) further suggest that the optimal condition type depends on domain characteristics, motivating future work on condition-adaptive architectures.
D.3. Fine-grained Control (RQ3)
This section supplements the fine-grained control experiments with implementation details and additional failure mode analysis.
D.3.1. SYNTH-U CLASSIFIER DETAILS
To verify whether generated segments contain the specified local patterns, we train a lightweight 1D-CNN classifier on ground-truth Synth-U segments. The classifier consists of three convolutional layers followed by global average pooling and two independent linear heads predicting the number of peaks (3 classes) and sags (2 classes) as defined in Section A.1.3. We train with AdamW (lr=10-3, weight decay=10-4) for 30 epochs and select the checkpoint with the highest validation joint accuracy. Joint accuracy requires all three segment-level predictions (peaks and sags) to be correct simultaneously, providing a strict measure of fine-grained control success.
D.3.2. TEMPORAL ORDER ANALYSIS ON TELECOMTS-SEGMENT
Figure 25 visualizes the temporal order confusion matrices. Each row corresponds to a generated segment (TS i), and each column to a within-series caption (Text j); an ideal model should exhibit strong diagonal dominance. Strikingly, all generative models produce near-uniform distributions (entries  0.25), indicating that they fail to associate segment-level descriptions with their correct temporal positions. In contrast, the ground-truth retrieval (rightmost panel) shows clear diagonal structure, confirming that the alignment between segments and texts is learnable in principle; however, current generators fail to capture it.
D.4. Practical Utility (RQ5)
As discussed in Section 4.5, we evaluate the practical utility of generated time series by measuring how well they can substitute for real data in downstream classification tasks. Following the drop rate metric defined in Equation 2, we train classifiers on fully generated data and compare their performance against classifiers trained on real data. Table 32 presents the detailed drop rate for each model across all datasets, complementing the aggregated visualization in Figure 6.

32

Var 0 Value

Var 0

Var 1

Var 0

Var 1

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

VerbalTS

2

0

2

0

5T0ime 100

Value

TEdit

2

0

2

0

5T0ime 100

Value

TimeWeaver
2

0

2

0

5T0ime 100

Value

Text2Motion
2

0

2

0

5T0ime 100

Value

Generation Quality: Synth-U

WaveStitch

Bridge

0

2

0

5T0ime 100

Value

0

2

0

5T0ime 100

Real

Generated Median

Gen 25%-75%

Value

DiffuSETS
2

0

2

0

5T0ime 100

Gen 10%-90%

Value

TimeVQVAE

0

2

0

5T0ime 100

Value

T2S
10

0

0

5T0ime 100

Value

TTSCGAN

0

2

0

5T0ime 100

Figure 14. Generation Quality Comparison: Synth-U. Each subplot shows one model's performance on one variable. Blue line: ground truth; Red line: generated median; Red bands: 25%-75% (dark) and 10%-90% (light) quantile ranges of 10 generated samples.

Value

2 VerbalTS

0

20

5T0ime 100

2

0

2

0

5T0ime 100

Value

Value

2 TEdit
0

0

5T0ime 100

2

0

20

5T0ime 100

Value

Value

2 TimeWeaver

0

20

5T0ime 100

2

0

0

5T0ime 100

Value

Value

2 Text2Motion

0

0

5T0ime 100

2

Value

Generation Quality: Synth-M

WaveStitch

0

5

0

5T0ime 100

5

Value

2 Bridge

0

0

5T0ime 100

2

Value

Value

0

0

0

5T0ime 100

0

5T0ime 100

Real

Generated Median

0

0

5T0ime 100

Gen 25%-75%

Value

Value

2 DiffuSETS

0

0

5T0ime 100

2

0

20

5T0ime 100

Gen 10%-90%

Value

Value

2 TimeVQVAE

0

0

5T0ime 100

2

0

0

5T0ime 100

Value

Value

T2S

0

50

5T0ime 100

5 0

5

0

5T0ime 100

Value

Value

2 TTSCGAN

1 0

0

5T0ime 100

2

1

0

0

5T0ime 100

Value

Figure 15. Generation Quality Comparison: Synth-M. Each subplot shows one model's performance on one variable. Blue line: ground truth; Red line: generated median; Red bands: 25%-75% (dark) and 10%-90% (light) quantile ranges of 10 generated samples.

Value

Value

1 VerbalTS

0

10

1T0ime 20

1

0

10

1T0ime 20

1

0

10

1T0ime 20

Value

Value

Value

TEdit
0

5

10 0

1T0ime 20

1

0

10

1T0ime 20

1

0

10

1T0ime 20

Value

Value

Value

1 TimeWeaver

0

10

1T0ime 20

1

0

10

1T0ime 20

1

0

10

1T0ime 20

Value

Value

Value

Generation Quality: AirQuality Beijing

1 Text2Motion

0

10

1T0ime 20

1

Value

WaveStitch

5

0

0

1T0ime 20

5.0

Value

1 Bridge

0

10

1T0ime 20

1

Value

0

2.5

10

1T0ime 20

0.0 0

1T0ime 20

1

5

0

Value

10

1T0ime 20

0

0

1T0ime 20

Value

Value

0

10

1T0ime 20

1

0

10

1T0ime 20

Value

Value

Value

1 DiffuSETS

0

10

1T0ime 20

1

0

10

1T0ime 20

1

0

1

0

1T0ime 20

Value

Value

Value

TimeVQVAE

T2S

1

5

Value

0

0

10

1T0ime 20

0

1T0ime 20

1

0

Value

0

2

10

1T0ime 20

40

1T0ime 20

1

0.0

0

2.5

Value

10

1T0ime 20

5.0 0

1T0ime 20

Real

Generated Median

Gen 25%-75%

Gen 10%-90%

Value

Value

Value

1 TTSCGAN

0

10

1T0ime 20

1

0

10

1T0ime 20

1

0

10

1T0ime 20

Value

Figure 16. Generation Quality Comparison: AirQuality Beijing. Each subplot shows one model's performance on one variable. Blue line: ground truth; Red line: generated median; Red bands: 25%-75% (dark) and 10%-90% (light) quantile ranges of 10 generated samples.

VerbalTS

0.5 1.0

1.5

0

5T0ime 100

2

0

2

0

5T0ime 100

Value

Value

TEdit
0

1

0

5T0ime 100

50

25

0

0

5T0ime 100

Value

Value

TimeWeaver
2 0

0

5T0ime 100

2

0

2

0

5T0ime 100

Value

Value

Generation Quality: TelecomTS

Text2Motion
0.6 0.8

WaveStitch
0

Bridge
0

Value

Value

1.0 0

5T0ime 100

0

1

0

5T0ime 100

Value

10

5T0ime 100

1

0

1

0

5T0ime 100

Value

10

5T0ime 100

1

0

1

0

5T0ime 100

Real

Generated Median

Gen 25%-75%

Value

Value

DiffuSETS
0.5

1.0

0

5T0ime 100

1

0

1

0

5T0ime 100

Gen 10%-90%

Value

Value

TimeVQVAE

0

10

5T0ime 100

2.5

0.0

2.5

0

5T0ime 100

Value

Value

T2S
0 1

0

5T0ime 100

2.5

0.0

2.5 0

5T0ime 100

Value

Value

TTSCGAN
1

0

1

0

5T0ime 100

1

0

1

0

5T0ime 100

Var 1 Value

Figure 17. Generation Quality Comparison: TelecomTS. Each subplot shows one model's performance on one variable. Blue line: ground truth; Red line: generated median; Red bands: 25%-75% (dark) and 10%-90% (light) quantile ranges of 10 generated samples.

VerbalTS
2.5

0.0

2.5

0

5T0ime 100

Value

TEdit

2.5

0.0

0

5T0ime 100

Value

TimeWeaver

2

0

0

5T0ime 100

Value

5 Text2Motion

0

0

5T0ime 100

Value

Generation Quality: ETTm1

WaveStitch 1 Bridge

Value

0.5

0

1.0

0

5T0ime 100

10

5T0ime 100

Real

Generated Median

Gen 25%-75%

Value

DiffuSETS
2.5

0.0

2.5

0

5T0ime 100

Gen 10%-90%

Value

TimeVQVAE

0

2

0

5T0ime 100

Value

T2S
20

10

0

0

5T0ime 100

Value

TTSCGAN

0.0 0.5

0

5T0ime 100

Figure 18. Generation Quality Comparison: ETTm1. Each subplot shows one model's performance on one variable. Blue line: ground truth; Red line: generated median; Red bands: 25%-75% (dark) and 10%-90% (light) quantile ranges of 10 generated samples.

Var 2

Var 0 Value

Var 0 Value

33

Var 0 Value

Var 1 Value

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

VerbalTS
0.5
0.0
0.5 0 50Time100 150

Value

TEdit
2 0
0 50Time100 150

Value

2 TimeWeaver
0 0 50Time100 150

Value

Generation Quality: Istanbul Traffic

Text2Motion
0.5 0.0

WaveStitch
2

Bridge
0

Value

Value

0.5 0 50Time100 150

0 0 50Time100 150

10

50Time100 150

Real

Generated Median

Gen 25%-75%

Value

DiffuSETS
1 0
0 50Time100 150
Gen 10%-90%

Value

TimeVQVAE
2 0 2
0 50Time100 150

Value

T2S
0 5
0 50Time100 150

Value

TTSCGAN
1 0 1
0 50Time100 150

Figure 19. Generation Quality Comparison: Istanbul Traffic. Each subplot shows one model's performance on one variable. Blue line: ground truth; Red line: generated median; Red bands: 25%-75% (dark) and 10%-90% (light) quantile ranges of 10 generated samples.

Var 0 Value

Generation Quality: PTB-XL Conceptual

VerbalTS
2.5

TEdit
5

TimeWeaver
20

Text2Motion

WaveStitch

2

25

Bridge
2

Value

Value

Value

Value

Value

0.0

0

0

0

0

25

0

0

T5im00e 1000

0

T5im00e 1000

0

T5im00e 1000

0

T5im00e 1000

0

T5im00e 1000

0

T5im00e 1000

2.5 0.0 2.5
0

Value

10 0

T5im00e 1000

0

10

Value

0

10

T5im00e 1000

0

Value

2.5 0.0 2.5

T5im00e 1000

0

25

Value

0

T5im00e

1000

25 0

Value

2.5 0.0 2.5

T5im00e 1000

0

T5im00e 1000

0 50

10

Value

0

T5im00e 1000

0

10

Value

0

10

T5im00e 1000

0

Value

0.0

2.5

T5im00e 1000

0

50

Value

0

T5im00e

1000

50 0

Value

0.0

2.5

T5im00e 1000

0

T5im00e 1000

Value

Value

Value

DiffuSETS

TimeVQVAE

5
0 0

T5im00e 1000

Value

2 0 20

0

Value

10

T5im00e 1000

0

5 0 50

Value

2.5 0.0 2.5

T5im00e 1000

0

0

Value

10

T5im00e 1000

0

0

0.0

Value

5

2.5

Value

5 0 5

0

T5im00e 1000

0

T5im00e 1000

0

Real

Generated Median

Gen 25%-75%

Gen 10%-90%

T2S

TTSCGAN

2

Value

0

T5im00e 1000

20

2.5

Value

0.0

2.5

T5im00e 1000

T5im00e 1000

0

T5im00e 1000

Value

0.0

2.5

T5im00e 1000

0

T5im00e 1000

Var 2 Value

Figure 20. Generation Quality Comparison: PTB-XL Conceptual. Each subplot shows one model's performance on one variable. Blue line: ground truth; Red line: generated median; Red bands: 25%-75% (dark) and 10%-90% (light) quantile ranges of 10 generated samples.

Var 1 Value

Generation Quality: PTB-XL Morphological

VerbalTS

2.5

0.0

2.5

0

T5im00e 1000

Value

TEdit
5

0

5

0

T5im00e 1000

Value

TimeWeaver

10

0

10 0

T5im00e 1000

Value

Text2Motion
2 0

0

T5im00e 1000

Value

25 WaveStitch

0

25

0

T5im00e 1000

Value

Bridge
2 0

0

T5im00e 1000

Value

DiffuSETS
0

20

0

T5im00e 1000

Value

TimeVQVAE

2

0

20

T5im00e 1000

Value

0 5
0

T2S
T5im00e 1000

Value

TTSCGAN
2

0

20

T5im00e 1000

5 0 50

Value

10

0

T5im00e 1000

0

10

Value

0

10

T5im00e 1000

0

Value

2.5 0.0 2.5

T5im00e 1000

0

Value

0 50

T5im00e 1000

0

Value

2.5 0.0 2.5

T5im00e 1000

0

T5im00e 1000

Value

5 0 50

Value

2.5 0.0 2.5

T5im00e 1000

0

0

Value

5

T5im00e

1000

10 0

Value

2.5 0.0 2.5

T5im00e 1000

0

T5im00e 1000

Value

0.0

2.5 0.0

2.5

2.5

Value

10

Value

0

0.0

10

2.5

Value

Value

0

0.0

50

2.5

Value

20

0.0

Value

0

2.5

Value

5

0.0

Value

0 5

2.5

0

T5im00e 1000

0

T5im00e 1000

0

T5im00e 1000

0

T5im00e 1000

0

T5im00e 1000

0

T5im00e 1000

0

T5im00e 1000

0

T5im00e 1000

0

T5im00e 1000

0

T5im00e 1000

Real

Generated Median

Gen 25%-75%

Gen 10%-90%

Figure 21. Generation Quality Comparison: PTB-XL Morphological. Each subplot shows one model's performance on one variable. Blue line: ground truth; Red line: generated median; Red bands: 25%-75% (dark) and 10%-90% (light) quantile ranges of 10 generated samples.

Var 0 Value

VerbalTS
2 1 0 0 10 Tim2e0 30
0.025 0.000
0 10 Tim2e0 30
0 1 2 0 10 Tim2e0 30

Value

Value

Value

TEdit
2 1
0 10 Tim2e0 30
2
0 0 10 Tim2e0 30 2 0 2 0 10 Tim2e0 30

Value

Value

Value

TimeWeaver
2
0 0 10 Tim2e0 30
0.025 0.000
0 10 Tim2e0 30 1 0 1
0 10 Tim2e0 30

Value

Value

Value

Generation Quality: WEATHER Conceptual

Text2Motion
2 1
0 10 Tim2e0 30 0.02 0.00
0 10 Tim2e0 30 0 1
0 10 Tim2e0 30

Value

Value

Value

10 WaveStitch
5 0
0 10 Tim2e0 30 0
2 0 10 Tim2e0 30
20
0 0 10 Tim2e0 30

Value

Value

Value

2 1 00
0.02 0.00 0.02 0
1 0 1
0

Bridge
10 Tim2e0 30 10 Tim2e0 30 10 Tim2e0 30

Value

Value

Value

DiffuSETS
2
0 0 10 Tim2e0 30
0
5 0 10 Tim2e0 30
2 0 2 0 10 Tim2e0 30

Value

Value

Value

TimeVQVAE
2
0 0 10 Tim2e0 30
0.02 0.00
0 10 Tim2e0 30 0 1
0 10 Tim2e0 30

Real

Generated Median

Gen 25%-75%

Gen 10%-90%

Value

Value

Value

T2S
2
1 0 10 Tim2e0 30
0.25 0.00 0.25
0 10 Tim2e0 30
1 0 1
0 10 Tim2e0 30

Value

Value

Value

TTSCGAN
2 0
0 10 Tim2e0 30
0 1
0 10 Tim2e0 30 1 0 1
0 10 Tim2e0 30

Var 2 Value

Figure 22. Generation Quality Comparison: WEATHER Conceptual. Each subplot shows one model's performance on one variable. Blue line: ground truth; Red line: generated median; Red bands: 25%-75% (dark) and 10%-90% (light) quantile ranges of 10 generated samples.

Var 0 Value

Var 2 Value

Var 1 Value

34

Var 1 Value

ConTSG-Bench: A Unified Benchmark for Conditional Time Series Generation

Var 0 Value

VerbalTS
2 0
0 10 Tim2e0 30
0.05 0.00
0 10 Tim2e0 30 1 0 1
0 10 Tim2e0 30

Value

Value

Value

TEdit
2 0
0 10 Tim2e0 30 0.02 0.00
0 10 Tim2e0 30
0 2 0 10 Tim2e0 30

Value

Value

Value

TimeWeaver
2
0
0 10 Tim2e0 30
0.05
0.00 0 10 Tim2e0 30
1 0 1
0 10 Tim2e0 30

Value

Value

Value

Generation Quality: WEATHER Morphological

Text2Motion
2
0 0 10 Tim2e0 30
0.02 0.00
0 10 Tim2e0 30
0 1
0 10 Tim2e0 30

Value

Value

Value

WaveStitch
2.5 0.0 2.5
0 10 Tim2e0 30
0.0 0.5
0 10 Tim2e0 30 0
5 0 10 Tim2e0 30

Value

Value

Value

2
1 0
0.02 0.00 0.02 0
1 0 1
0

Bridge
10 Tim2e0 30 10 Tim2e0 30 10 Tim2e0 30

Value

Value

Value

DiffuSETS
2
0 0 10 Tim2e0 30
0 5
0 10 Tim2e0 30 0
5 0 10 Tim2e0 30

Value

Value

Value

TimeVQVAE
2 1 0
0 10 Tim2e0 30 0.02
0.00
0 10 Tim2e0 30
0 1
0 10 Tim2e0 30

Real

Generated Median

Gen 25%-75%

Gen 10%-90%

Value

Value

Value

20 T2S
0 0 10 Tim2e0 30
25 0 25
0 10 Tim2e0 30
0
100 0 10 Tim2e0 30

Value

Value

Value

TTSCGAN
2 0
0 10 Tim2e0 30 0.5 0.0
0 10 Tim2e0 30 1 0 1
0 10 Tim2e0 30

Var 2 Value

Figure 23. Generation Quality Comparison: WEATHER Morphological. Each subplot shows one model's performance on one variable. Blue line: ground truth; Red line: generated median; Red bands: 25%-75% (dark) and 10%-90% (light) quantile ranges of 10 generated samples.

Conceptual Rank (1 = Best) Conceptual Rank (1 = Best) Conceptual Rank (1 = Best) Conceptual Rank (1 = Best)

PTB-XL DTW

PTB-XL CRPS

Weather DTW

Weather CRPS

10

10

10

10

8

8

8

8

6

6

6

6

4

4

4

4

2

2

2

2

BetteMr oartpCh2oonlcoegp4ictuaallR6ank8(1 =10BEeqsuta)l performMaonrcpeh2olog4ical dR6iaffnusk8e(t1s =10Best) t2s Morph2toelxotg24imcaoltiR6oannk8(1 =10Bteimste)weaver Morph2olvoegr4ibcaalltsR6ank8(1 =1w0Baevests)titch

Better at Morphological

bridge

retrieval

tedit

timevqvae

ttscgan

Figure 24. Morphological vs. conceptual conditioning: rank stability. Each point is a model with ranks computed separately under morphological (x-axis) and conceptual (y-axis) conditions (lower is better). Points near the diagonal indicate stable rankings across condition types, while off-diagonal points indicate sensitivity to condition semantics.

76 76 76 76 76 76 76 76 76 76 76 76 76 76 76 76 76 76 76 76 76 76 76 76 76 76 76 76

%ULGJH
0.25 0.24 0.24 0.27 0.25 0.24 0.24 0.27 0.25 0.24 0.24 0.27 0.25 0.24 0.25 0.27
7H[W 7H[W 7H[W 7H[W

'LIIX6(76
0.23 0.25 0.25 0.27 0.25 0.25 0.23 0.27 0.24 0.25 0.24 0.27 0.24 0.24 0.23 0.28
7H[W 7H[W 7H[W 7H[W

76
0.24 0.25 0.25 0.26 0.24 0.24 0.26 0.25 0.25 0.25 0.26 0.25 0.23 0.26 0.25 0.26
7H[W 7H[W 7H[W 7H[W

7H[W0RWLRQ
0.26 0.25 0.25 0.24 0.25 0.26 0.24 0.24 0.24 0.27 0.25 0.24 0.24 0.25 0.26 0.25
7H[W 7H[W 7H[W 7H[W

9HUEDO76
0.25 0.26 0.24 0.26 0.25 0.25 0.24 0.25 0.24 0.26 0.24 0.26 0.25 0.25 0.25 0.25
7H[W 7H[W 7H[W 7H[W

5HWULHYDO
0.31 0.25 0.22 0.23 0.25 0.28 0.24 0.23 0.22 0.25 0.28 0.26 0.21 0.23 0.24 0.32
7H[W 7H[W 7H[W 7H[W

JW
0.57 0.16 0.13 0.13 0.5 0.17 0.54 0.16 0.13 0.4 0.16 0.17 0.52 0.14 0.3 0.18 0.16 0.16 0.50 0.2
7H[W 7H[W 7H[W 7H[W

Figure 25. Temporal order confusion matrices on TelecomTS-Segment. Rows denote generated segments (TS i) and columns denote within-series captions (Text j); diagonal dominance indicates correct segment­text alignment.

Table 32. Drop Rate by Model and Dataset (lower is better)

Dataset
AirQuality Beijing ETTm1 Istanbul Traffic PTB-XL (Conceptual) PTB-XL (Morphological) Synth-M Synth-U TelecomTS Weather (Conceptual) Weather (Morphological)
Mean

TEdit
0.301 0.290 1.232 0.672 0.320 0.093 0.165 0.015 0.850 0.668
0.461

TimeWeaver
0.336 0.382 0.705 0.722 0.624 0.096 0.205 0.018 0.879 0.436
0.440

DiffuSETS
0.574 0.365 0.918 0.532 0.202 0.538 0.598 0.022 0.993 0.433
0.517

TimeVQVAE
0.509 0.560 1.210 0.841 0.607 0.420 0.389 0.307 0.898 0.517
0.626

VerbalTS
0.631 0.279 1.020 0.582 0.499 0.098 0.035 0.012 0.704 1.303
0.516

WaveStitch
0.505 0.507 1.046 0.827 0.620 0.571 0.286 0.005 0.787 1.073
0.623

Text2Motion
0.696 1.086 0.741 1.383 0.585 0.537 0.640 0.078 0.840 1.311
0.790

Bridge
0.787 0.598 0.953 0.568 0.719 0.730 0.296 0.094 0.863 0.994
0.660

T2S
1.106 0.426 1.290 1.003 0.645 0.905 1.000 0.104 0.799 0.555
0.783

TTSCGAN
0.863 0.573 0.747 1.083 0.546 0.989 0.967 0.157 0.942 1.036
0.790

35

