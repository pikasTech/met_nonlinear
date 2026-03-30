# Gong_2026_SWAN_Seismic

TRAINING A GENERALIZABLE DIFFUSION MODEL FOR SEISMIC
DATA PROCESSING USING A LARGE-SCALE OPEN-SOURCE
WAVEFORM DATASET
XINYUE GONG, SERGEY FOMEL, AND YANGKANG CHEN
Abstract. We introduce the Seismic Waveforms dataset for Automatic Neural-network
processing (SWAN), a comprehensive and standardized benchmark designed to advance
data-driven seismic signal processing. SWAN aggregates diverse synthetic and real seismic
waveforms spanning a wide range of geological structures, noise conditions, propagation en-
vironments, and acquisition geometries, providing a unified foundation for training highly
generalizable models. Leveraging this dataset, we develop and evaluate a conditionally con-
strained residual diffusion model for core seismic processing tasks, focusing on missing-trace
reconstruction. Extensive experiments demonstrate that diffusion models trained on SWAN
achieve state-of-the-art performance across heterogeneous testing scenarios, outperforming
leading deep-learning and physics-based baselines on both synthetic benchmarks and field
data examples. The results highlight SWAN’s value as both a scalable training corpus and
a rigorous evaluation framework, and illustrate the strong potential of diffusion-based archi-
tectures for robust, generalizable seismic data processing.
1. Introduction
Deep learning (DL) has emerged as a transformative paradigm in seismic data processing
and imaging, leading to substantial improvements across core tasks such as noise attenuation
[21, 13, 9], missing-trace reconstruction [6, 14], deblending [11] and full-wave inversion (FWI)
[15].
Modern neural architectures, ranging from convolutional neural networks (CNNs) to
transformer-based models [10] and diffusion models [7], have demonstrated strong capability in
learning the spatiotemporal complexity of seismic wavefields.
Although these developments are encouraging, progress in DL for seismic processing remains
constrained by a persistent data bottleneck [12]. Publicly available seismic datasets are limited
in scale, heterogeneous in format, and often not provided in an AI-ready form suitable for
modern end-to-end learning pipelines [19, 17]. Consistently preprocessed patch-level wavefield
datasets are particularly scarce, even though they are essential for training models that can
operate reliably across surveys, acquisition geometries, and noise environments.
This limitation has become increasingly evident with the emergence of geophysical foun-
dation models. The Seismic Foundation Model (SFM) [17], for example, aggregates millions
of seismic images to pretrain large self-supervised backbones for interpretation-oriented tasks.
While such efforts demonstrate the potential of large-scale pretraining, they also expose a
clear gap. The community lacks an accessible, standardized wavefield dataset specifically de-
signed to support low-level processing tasks such as denoising, interpolation, and missing-trace
reconstruction. Existing foundation-model datasets focus primarily on labels or structural in-
terpretation targets rather than the raw wavefield representations needed for signal-processing
Date: January 2026.
1
arXiv:2603.13645v1  [physics.geo-ph]  13 Mar 2026
2
XINYUE GONG, SERGEY FOMEL, AND YANGKANG CHEN
workflows. As a result, reproducibility and fair comparison across DL-based seismic processing
methods remain difficult.
Beyond dataset scale, diversity, and accessibility, current public resources also suffer from
inconsistent preprocessing practices. Different surveys may adopt incompatible normalization
strategies, patch sizes, noise handling, or coordinate conventions [8, 17]. These inconsistencies
hinder cross-survey generalization and contribute to a long-standing challenge in seismic ML,
where models succeed on narrowly defined datasets but fail to transfer across geological settings
or acquisition conditions [19].
To address these limitations, we introduce the Seismic Waveforms Dataset for Automatic
Neural-network processing (SWAN), a unified and AI-ready seismic patch corpus designed
specifically for DL-based wavefield processing. SWAN contains 537,373 non-overlapping 128×128
patches obtained from 20 synthetic and real surveys. Synthetic datasets contribute approxi-
mately 74.4% of all patches, while real field datasets contribute the remaining 25.6%. This com-
bination provides both physics-consistent ground truth and the geological variability necessary
for generalizable learning. Each patch is accompanied by comprehensive metadata describing
acquisition geometry, normalization factors, spatial context, and quality indicators, enabling
transparent data filtering and complete traceability.
SWAN offers several contributions that distinguish it from existing seismic datasets. First,
it is explicitly designed for wavefield-level processing rather than structural interpretation,
making it directly applicable to seismic reconstruction, denoising, and acquisition recovery
[20]. Second, it functions as a foundation dataset that supports model training, benchmarking,
and cross-survey evaluation across diverse DL architectures, including CNNs, transformers,
and diffusion models. Third, it integrates synthetic and real data in a unified format, which
narrows the domain gap between numerical simulations and field acquisition conditions and
enables more robust and transferable learning [8].
As seismic research continues to adopt data-centric AI practices [16], SWAN provides a stan-
dardized and extensible platform for developing and evaluating DL-based seismic processing
methods. By unifying data formatting, normalization, patch extraction, and metadata con-
ventions, SWAN improves reproducibility, facilitates fair comparisons, and enables the broader
community to build upon a common seismic data backbone [18]. We expect SWAN to support
both academic research and industrial applications, particularly in areas such as interpolation,
noise suppression, and generative modeling for seismic reconstruction.
2. SWAN Dataset
To support large-scale and generalizable DL research for seismic wavefield processing, we
construct the SWAN dataset. SWAN is a unified, AI-ready collection of seismic patches ex-
tracted from a wide range of synthetic and real surveys. The dataset addresses a longstanding
bottleneck in seismic machine learning, namely the lack of standardized patch-level data that
consistently represent both prestack and poststack wavefields. This section outlines the overall
data processing workflow and describes the composition of the four major dataset categories.
2.1. Data Processing Pipeline. The SWAN dataset is produced through a unified work-
flow that standardizes diverse seismic surveys into consistently formatted 128 × 128 wavefield
patches. The complete workflow is illustrated in Fig. 1. Synthetic surveys originate from bench-
mark velocity models, including BP 1994, BP 2004, BP 2007 TTI, BP 2.5D, Marmousi, Pluto,
SEAM Phase I, and Amoco. Real surveys come from several major geological regions such as
the Taranaki Basin in New Zealand, the North Sea F3 block, the Gulf of Mexico, Alaska, and
SWAN
3
Wyoming. These datasets cover both marine and land environments and include shot gathers
as well as migrated sections.
All seismic volumes are represented as 2D wavefields and partitioned into fixed-size patches
using a 128 × 128 sliding window with a stride of 128 samples. Each patch is normalized by its
maximum absolute amplitude, resulting in values within [−1, 1]. This step eliminates the need
for survey-specific scaling and allows patches from heterogeneous surveys to be used directly
in DL workflows.
Quality control is performed automatically.
For most datasets, patches containing more
than 90% zero values are removed because such tiles typically originate from edge padding,
inactive traces, or empty recording windows.
For several datasets with known acquisition
or preprocessing characteristics, this threshold is adjusted to better preserve valid wavefield
information. This flexible approach maintains dataset consistency while retaining meaningful
seismic signals.
Each retained patch is stored together with metadata describing the survey name, patch
position, time, and trace indices, normalization factors, and quality indicators such as zero
ratio. These metadata support reproducibility, survey-level filtering, reconstruction of spatial
context, and flexible dataset selection for DL model training. In total, SWAN contains 537,373
patches extracted from 20 datasets.
2.2. Dataset Composition. The SWAN dataset integrates 20 constituent datasets grouped
into four major categories. Synthetic datasets contribute approximately 74.4% of all patches,
while real surveys contribute 25.6%. Although the distribution is imbalanced, additional field
datasets will be incorporated in future releases to expand real-data diversity. Representative
examples from each category appear in Fig. 2.
Synthetic Prestack. This category includes eight modeling benchmarks, such as BP 1994,
BP 2.5D, BP 2004 velocity, BP migration, BP 2007 TTI, Marmousi, Pluto, and Amoco. These
datasets exhibit clean reflection events, diffractions, anisotropic wavefronts, and long-offset
kinematic patterns. Their controlled nature makes them particularly suitable for evaluating
DL-based interpolation and generative reconstruction. Representative examples appear in the
green-bordered rows of Fig. 2.
Synthetic Poststack. Two SEAM Phase I datasets extracted along the inline and crossline
directions belong to this category.
They capture structurally complex deepwater geology,
including salt bodies, sharply contrasting reflectors, and faulted sedimentary units.
These
characteristics provide a rich test bed for structure-preserving denoising and post-migration
enhancement. Representative examples appear in the blue-bordered rows of Fig. 2.
Real Prestack. Real prestack datasets include Stratton 3D, the USGS Alaska line, and the
Oz marine survey. They contain acquisition challenges such as statics, ground roll, swell noise,
irregular offsets, and nonstationary amplitude decay. These properties make them essential
for assessing the robustness and generalization of DL-based reconstruction.
Representative
examples appear in the teal-bordered rows of Fig. 2.
Real Poststack. This category includes a large collection of migrated 2D and 3D surveys,
including F3 (North Sea), Kerry, Waihapa, Waipuku, BOEM Gulf of Mexico, Kahu, and Teapot
Dome.
These datasets exhibit diverse structural features such as faults, channels, dipping
reflectors, and unconformities. They provide geologically meaningful patterns for evaluating
structural fidelity in DL-based processing. Representative examples appear in the red-bordered
rows of Fig. 2.
4
XINYUE GONG, SERGEY FOMEL, AND YANGKANG CHEN
Table 1. Detailed summary of the SWAN dataset collections.
Dataset
Files Patches Dim (samples × traces) dt (ms) Region / Source
Synthetic Prestack
1994bp
876
137,559
1152 × 3008
5.4
BP Benchmark
1994bp_mig
278
7,557
2000 × 240–480
4.0
BP Migration Test
1997bp_2.5d
1
1,991
384 × 98,560
9.9
BP 2.5D Model
2004bp_velocity 1,354
117,638
2001 × 1201
6.0
BP Velocity Model
2007bp_tti
1,641
49,599
1151 × 800
8.0
BP TTI Model
Amoco
385
1,086
384 × 256
9.9
AMOCO
Marmousi
1
982
1500 × 256
4.0
SMAART JV
Pluto
694
9,081
1126 × 350
8.0
SMAART JV
Synthetic Poststack
SEAM_1
1002
38,596
851 × 1169
4.0
SEAM Phase I
SEAM_2
1169
35,927
851 × 1002
4.0
SEAM Phase I
Real Prestack
Alaska
58
1,300
3000 × 95
2.0
USGS NPRA Alaska
OZ Yilmaz
40
471
975–2535 × 24–216
4.0
SEG Textbook
Stratton
102
5,198
3000 × 328–652
2.0
OSG Texas
Real Poststack
KERRY
735
11,597
1252 × 287
4.0
New Zealand
WAIHAPA
305
5,795
2501 × 227
2.0
New Zealand
WAIPUKU
312
4,107
2001 × 148
2.0
New Zealand
BOEM
1
7,302
450 × 311,640
10.0
Gulf of Mexico
F3
651
13,290
462 × 951
4.0
Dutch North Sea
KAHU
1
85,437
1500 × 994,230
4.0
New Zealand
Teapot Dome
1
2,860
1501 × 33,286
2.0
RMOTC Wyoming
3. Methodology
3.1. Diffusion Models. Diffusion models approximate complex data distributions by gradu-
ally corrupting a clean signal and learning a neural network that inverts this transformation.
Let x0 denote a clean seismic patch.
The forward diffusion process applies a sequence of
Gaussian perturbations:
(1)
q(xt | xt−1) = N(√αtxt−1, (1 −αt)I) ,
with the closed-form marginal
SWAN
5
(2)
xt = √¯αt x0 +
√
1 −¯αt ϵ,
ϵ ∼N(0, I),
where ¯αt = Qt
s=1 αs. A neural network estimates the injected noise by minimizing
(3)
LDDPM = E

∥ϵ −ϵθ(xt, t)∥2
.
This classical formulation is effective for image generation, yet it relies on isotropic Gaussian
corruption and produces stochastic reverse trajectories.
These properties conflict with the
structured nature of seismic degradation, which is dominated by spatially coherent missing
traces rather than random noise.
Moreover, reversing diffusion from pure noise disregards
the information present in the observed waveform and introduces sampling variance. These
issues motivate a diffusion formulation that is more tightly aligned with seismic physics and
reconstruction objectives.
3.2. Residual-Guided Diffusion Model (RGDM). To address these limitations, we intro-
duce the Residual-Guided Diffusion Model (RGDM). The key idea is to reformulate diffusion as
a residual-correction process that remains anchored to the observed seismic waveform instead
of drifting toward pure noise. RGDM models the latent evolution as a sequence of determin-
istic corrections that reflect the discrepancy between the observed and clean wavefields. The
training and sampling workflows are shown in Fig. 3.
3.2.1. Forward Process. Let d = M ⊙x0 denote the observed gather. RGDM initializes the
terminal diffusion state using a mild Gaussian perturbation:
(4)
xT = d + σT ϵ.
The forward evolution then proceeds through residual increments:
(5)
xt = xt−1 + rt + βtϵt,
where rt represents the deviation between xt−1 and the underlying clean manifold associated
with x0. This formulation ensures that the latent trajectory remains centered on the observed
data rather than diffusing toward noise. As a result, the forward process captures a physically
meaningful correction pathway that reflects seismic acquisition effects.
3.2.2. Reverse Process. The reverse process predicts step-wise corrections that cancel the ac-
cumulated residuals. A U-Net-based rectifier Rθ(xt, t, d) estimates
(6)
ˆrt = Rθ(xt, t, d),
and the reverse update becomes
(7)
xt−1 = xt −ˆrt −β2
t
¯βt
ˆϵt + ηtϵ,
with the induced noise estimate:
6
XINYUE GONG, SERGEY FOMEL, AND YANGKANG CHEN
(8)
ˆϵt = xt −d −¯rt(θ)
¯βt
.
The reverse dynamics remain deterministic when ηt = 0, producing a stable reconstruction
trajectory that progressively removes artifacts while respecting the information contained in d.
3.2.3. Training Objective. RGDM employs a U-Net backbone with temporal embeddings and
multi-head self-attention to jointly process xt and the observed waveform d. Training directly
matches the true and predicted residual increments:
(9)
LRGDM = E

∥rt −Rθ(xt, t, d)∥2
.
This objective enforces a physically interpretable correction path and encourages the model
to learn how seismic acquisition patterns distort wavefields.
4. Numerical Experiments
To demonstrate the practical value and learning potential enabled by the SWAN dataset, we
train our reconstruction model using 50,000 randomly selected patches from each data category.
The experiments evaluate not only the reconstruction capability of the proposed method but
also its generalization to datasets that never appear in the SWAN training subset. Several
representative baselines are included for comparison, including projection onto convex sets
(POCS) algorithm [1], damped rank-reduction (DRR) [4], and PySeistr [5]. Unless otherwise
specified, all experiments use 50% irregular trace removal.
Most experiments follow a blind-test protocol.
The test datasets include four synthetic
benchmarks as well as several field examples, comprising a 2D hyperbolic gather, a 2D edge-
structure gather, a 3D hyperbolic volume, a synthetic DAS gather, a Viking Graben 2D section,
a SeanS3 3D volume, and a local field DAS segment. One non-blind experiment involving the
1997 BP dataset is also included to assess the impact on migration imaging.
4.1. Example 1: Synthetic Hyperbolic Data. The first blind-test dataset was originally
introduced by Zhou et al. [23]. It contains a marine-style common-shot gather with several
clean hyperbolic reflection events (Fig. 4a), making it a standard benchmark for interpolation
under 50% irregular sampling (Fig. 4f).
Figure 4 shows the reconstruction results. POCS (Fig. 4b) recovers only low-wavenumber
trends and introduces strong vertical streaks. DRR (Fig. 4c) improves reflector continuity but
still leaves scattered incoherent energy. PySeisTr (Fig. 4d) suppresses a portion of the noise
and better preserves event geometry, although substantial residual energy remains (Fig. 4i).
Our SWAN-trained model (Fig. 4e; SNR = 20.85 dB) achieves the most coherent reconstruc-
tion. Reflection events exhibit continuous curvature, consistent phase alignment, and stable
amplitudes across the entire gather. The residual panel (Fig. 4j) shows only weak and spatially
isolated energy. These results indicate that the model has learned strong event-level priors
from the SWAN dataset and generalizes effectively to unseen synthetic gathers.
4.2. Example 2: Synthetic Edge-Structure Data. The second blind-test dataset was in-
troduced by Zhou et al. [22] for evaluating edge-preserving reconstruction methods. The gather
contains strong lateral terminations and sharp discontinuities that challenge interpolation al-
gorithms.
SWAN
7
The observed data with 50% trace removal (Fig. 5f) exhibit fragmented edges and aliasing.
POCS (Fig. 5b) recovers primarily smooth background components. DRR (Fig. 5c) improves
reflector continuity but introduces noticeable artifacts in the missing regions. PySeisTr (Fig. 5d)
better reconstructs dipping events but leaves substantial residuals (Fig. 5i).
Our model (Fig. 5e; SNR = 10.71 dB) accurately restores both continuous reflections and
abrupt terminations. The residuals (Fig. 5j) are weak and spatially compact, demonstrating
that the SWAN-trained model captures geometric complexity even though such edge structures
were not explicitly seen during training.
4.3. Example 3: 3D Synthetic Hyperbolic Volume. The third experiment uses a 3D
synthetic hyperbolic volume introduced by Bai et al. [2]. The volume contains dipping and
curved reflectors with strong spatial continuity, making it suitable for evaluating reconstruction
in three dimensions.
The observed data with 50% missing traces (Fig. 6f) exhibit severe disruption of 3D con-
tinuity. POCS (Fig. 6b) and DRR (Fig. 6c) partially restore structures but leave significant
incoherent energy. PySeisTr (Fig. 6d; 12.83 dB) produces more consistent reflectors yet intro-
duces leakage around complex curvature.
The proposed method (Fig. 6e; 14.37 dB) reconstructs the 3D structures with the highest
fidelity. The residuals (Fig. 6j) remain weak and spatially isolated, demonstrating that the
model generalizes effectively to volumetric settings even though training uses only 2D patches.
4.4. Example 4: Synthetic DAS Data. The fourth experiment evaluates a synthetic DAS
dataset introduced by Chen et al. [3]. The gather contains dipping reflections typical of surface
DAS acquisitions, and 50% of the channels are removed.
POCS (Fig. 7b; 7.90 dB) introduces vertical striping and fails to reconstruct detailed events.
DRR (Fig. 7c; 10.19 dB) improves continuity but leaves incoherent energy in regions with rapid
dip changes. PySeisTr (Fig. 7d; 18.52 dB) preserves reflector geometry more effectively but still
exhibits leakage.
The proposed method (Fig. 7e; 19.99 dB) yields the most stable reconstruction with coherent
amplitude variations and minimal artifacts. The residuals (Fig. 7j) confirm accurate DAS-event
preservation.
4.5. Example 5: Viking Graben 2D Field Data. This experiment uses the well-known
Viking Graben 2D poststack section with dimensions 1500 × 1012 and a sampling interval of
4 ms.
Randomly removing 30%, 50%, and 70% of the traces provides three reconstruction
settings (Figs. 8b–d).
For the 30% removal case, the proposed method achieves the highest accuracy (12.17 dB),
outperforming POCS (11.82 dB), DRR (9.20 dB), and PySeisTr (7.13 dB). Under 50% removal,
the proposed method again leads with 9.34 dB. The most challenging 70% case shows severe
degradation for all methods, but the proposed model remains competitive at 4.51 dB with
better reflector continuity than the baselines.
4.6. Example 6: SeanS3 3D Field Data. The SeanS3 3D volume contains 500 time samples,
180 receivers, and 20 inlines. With 50% missing traces (Fig. 9b), POCS (5.54 dB) preserves
major events but leaves strong imprinting artifacts. DRR (4.92 dB) and PySeisTr (4.59 dB)
oversmooth the data. The proposed method achieves 7.75 dB with clearer event continuity and
reduced artifacts.
8
XINYUE GONG, SERGEY FOMEL, AND YANGKANG CHEN
Table 2. Quantitative comparison for Example 7.
Method
SNR (dB)
PSNR (dB)
MSE
SSIM
Observed
3.74
36.65
1.1760 × 10−4
0.9569
POCS
7.25
40.16
5.2355 × 10−5
0.9858
DRR
2.13
35.04
1.7036 × 10−4
0.9403
PySeistr
4.67
37.58
9.4969 × 10−5
0.9844
Ours
8.23
41.14
4.1839 × 10−5
0.9943
4.7. Example 7: Field DAS Section. A zoomed region of a field DAS gather from Chen et
al. [3] is extracted to evaluate reconstruction of fine-scale DAS features. The incomplete input
(Fig. 10b; 3.74 dB) exhibits disrupted curvature and discontinuous events.
POCS (7.25 dB) restores part of the dominant arrival but introduces striping artifacts. DRR
(2.13 dB) fails to preserve event curvature. PySeisTr (4.67 dB) produces smoother events but
retains leakage.
The proposed method (8.23 dB) achieves the most coherent event recovery and yields the
highest metrics in Table 2, indicating superior preservation of DAS waveform texture.
4.8. Example 8: Reconstruction and Migration Imaging on the 1997 BP Dataset.
The final experiment assesses how interpolation quality affects migration imaging.
We use
385 shot gathers from the 1997 BP model, each containing 256 traces and 384 samples with a
sampling interval of 10 ms. Because some 1997 BP slices are included in SWAN, this is not a
blind test; instead it evaluates downstream imaging.
Reconstruction under 50% removal is shown in Fig. 11. POCS (16.21 dB) partially restores
events but introduces vertical streaking. DRR (23.78 dB) oversmooths dipping energy. Py-
SeisTr (11.33 dB) reduces noise but smears reflectors. The proposed method achieves 29.62 dB
with coherent dipping events and minimal artifacts.
To evaluate imaging quality, we apply CMP sorting, NMO correction, stacking, and Kirchhoff
PSTM. The velocity model is converted from SEG-Y to RSF and resampled. Migration of
incomplete data results in severe reflector breakage (Fig. 12c). POCS and PySeisTr improve
reflector visibility but leave noise and smearing. DRR oversmooths the gathers.
Migration using the proposed reconstruction (Fig. 12g) produces the cleanest section with
sharp dips, reduced migration noise, and well-focused reflectors. This experiment highlights
how reconstruction quality directly influences seismic imaging.
5. Discussion
5.1. Generalization Enabled by SWAN. The SWAN dataset is designed to reflect the
physical consistency of seismic waveforms across a broad range of geological and acquisition
scenarios. It includes hyperbolic reflections from horizontally layered media, dipping and curved
events associated with structural deformation, laterally truncated terminations that resemble
fault or stratigraphic edges, pseudo three-dimensional reflector continuity across inline and
crossline directions, and a wide range of noise characteristics observed in both marine and land
surveys. This diversity allows the learning model to acquire a statistically stable prior that
captures essential kinematic and dynamic properties of seismic reflections.
The numerical experiments demonstrate that the model consistently reconstructs key seismic
attributes in a wide spectrum of settings. The reconstructed gathers preserve expected event
SWAN
9
geometry, amplitude behavior, and continuity, regardless of whether the input is a simple
synthetic hyperbolic pattern, an edge structure with abrupt terminations, a volumetric three-
dimensional reflector, or a field dataset such as the Viking Graben section, the SeanS3 volume,
or the DAS acquisitions. This stability across datasets indicates that SWAN provides a unified
event-level representation that cannot be learned from a single survey and is essential for cross-
survey generalization.
A major factor behind this generalization capability lies in the standardized design of the
dataset. All wavefields are converted into non-overlapping patches of identical size, normalized
consistently, and filtered using a unified quality control rule. Metadata describing sampling
intervals, normalization factors, and acquisition characteristics are recorded for each patch.
These procedures eliminate survey-specific preprocessing variations that often hinder cross-
survey learning in seismic applications. As a result, SWAN offers a reproducible and coherent
representation of seismic waveforms that supports large-scale training and robust transfer to
new datasets. This design provides a solid foundation for future community benchmarks, where
reproducibility and consistent preprocessing are necessary for fair comparison among different
reconstruction methods.
5.2. Deterministic Residual Pathways in RGDM. The advantages of the proposed RGDM
become apparent when considering its residual-guided diffusion mechanism and the determin-
istic behavior of its latent space evolution. Classical diffusion models operate by gradually
corrupting data toward Gaussian noise and learning to reverse this corruption through sto-
chastic sampling steps. Such a formulation is not aligned with seismic degradation patterns,
which arise from spatially coherent missing traces rather than random noise.
In contrast,
RGDM evolves through residual increments that describe the mismatch between the observed
data and the underlying clean waveform. This leads to a correction pathway that preserves
physically plausible event geometry throughout the diffusion process.
The deterministic nature of the reverse trajectory further reduces sampling variance and
avoids the generation of spurious reflections.
This property is crucial for seismic applica-
tions, where small amplitude variations, subtle edge terminations, and reflector continuity can
strongly influence interpretation and downstream imaging. Because SWAN exposes the model
to a broad variety of reflection patterns and noise regimes, the latent space learned by RGDM
contains a richer representation of seismic waveform characteristics than would be possible
with a narrow or single survey training set. Consequently, RGDM follows stable and physi-
cally meaningful diffusion paths even when applied to data from geological environments or
acquisition geometries not present in the training examples.
5.3. Limitations and Future Directions. Although RGDM performs well on the three-
dimensional volume considered in this study, the current framework remains limited by its
two-dimensional formulation and network. When applied to volumetric data, the model pro-
cesses each slice independently. True three-dimensional reflector continuity is therefore not
explicitly represented, and crossline relationships must be inferred indirectly.
As a result,
strongly curved horizons, fault-bounded geometries, and other volumetric features may be im-
perfectly reconstructed when the degree of out-of-plane variation is high. These limitations
highlight that both the dataset and the model architecture need to be extended toward explicit
three-dimensional representations in order to fully address the complexity of modern seismic
acquisitions.
Beyond the reconstruction task, the combination of large-scale datasets and generative mod-
els offers promising directions for future research. Diffusion models can be used not only as
10
XINYUE GONG, SERGEY FOMEL, AND YANGKANG CHEN
reconstruction engines, but also as data synthesizers and augmenters that support pretraining,
domain adaptation, and cross-survey generalization. With appropriate extensions, SWAN may
evolve into a foundation-level training corpus for seismic processing tasks, enabling models that
learn transferable representations of waveform physics.
Scalability and reproducibility are central considerations for future development. Expanding
SWAN to include additional geological provinces such as deepwater basins, arid land environ-
ments, and borehole-oriented surveys would increase the diversity of acquisition conditions.
Incorporating wide-azimuth, ocean-bottom-node, and irregular dense sampling would further
broaden the range of structural and kinematic patterns available for training. Standardizing
metadata and survey descriptors across all components will be essential for establishing a long-
term community benchmark that supports reproducible experimentation and fair comparison
among different waveform processing methods.
Ultimately, these efforts will pave the way
toward next-generation foundation models for seismic data processing and imaging.
6. Conclusion
We introduced SWAN, a large-scale open-source seismic waveforms dataset designed to sup-
port the development of generalizable deep-learning models for seismic processing. Building
upon this dataset, we proposed the Residual-Guided Diffusion Model (RGDM), which refor-
mulates diffusion as a deterministic residual-correction process anchored to the observed wave-
form. RGDM leverages the structured nature of seismic residuals and the rich event-level priors
learned from SWAN to achieve accurate and physically consistent reconstruction with only a
few diffusion steps. Extensive experiments on synthetic, pseudo-3D, and field data (the Viking
Graben 2D section and SeanS3 3D volume) demonstrate that RGDM outperforms established
baselines, including POCS, DRR, and PySeistr, particularly in scenarios with severe missing-
trace or complex reflector features. These results highlight the importance of combining diverse
training data with diffusion models tailored to seismic physics. The SWAN dataset and RGDM
framework together provide a robust foundation for future research in machine-learning-based
seismic processing, and we anticipate that they will facilitate further advances in interpolation,
denoising, imaging, and multi-dimensional seismic reconstruction.
7. Data Availability Statement
The datasets will be available in the public domain.
References
[1] R. Abma and N. Kabir. 3d interpolation of irregular data with a pocs algorithm. Geo-
physics, 71:E91–E97, 2006. doi: 10.1190/1.2356088.
[2] M. Bai, G. Huang, H. Wang, and Y. Chen. Seismic signal enhancement based on the
low-rank methods. Geophysical Prospecting, 68(9):2783–2807, 2020.
[3] Y. Chen, A. Savvaidis, S. Fomel, Y. Chen, O. M. Saad, H. Wang, Y. A. S. I. Oboue,
L. Yang, and W. Chen. Denoising of distributed acoustic sensing seismic data using an
integrated framework. Seismological Research Letters, 94(1):457–472, 2023. doi: 10.1785/
0220220117.
[4] Yangkang Chen, Weilin Huang, Liuqing Yang, Yapo Abolé Serge Innocent Oboué,
Omar M. Saad, and Yunfeng Chen.
DRR: an open-source multi-platform package for
the damped rank-reduction method and its applications in seismology. Computers & Geo-
sciences, 180:105440, 2023.
SWAN
11
[5] Yangkang Chen, Alexandros Savvaidis, Sergey Fomel, Yunfeng Chen, Omar M. Saad, Yapo
Abolé Serge Innocent Oboué, Quan Zhang, and Wei Chen. Pyseistr: a python package
for structural denoising and interpolation of multi-channel seismic data.
Seismological
Research Letters, 94(3):1703–1714, 2023. doi: 10.1785/0220220242.
[6] Xinyue Gong, Sheng Chen, and Chao Jin. Intelligent reconstruction for spatially irregular
seismic data by combining compressed sensing with deep learning.
Frontiers in Earth
Science, 11:1299070, 2023. doi: 10.3389/feart.2023.1299070.
[7] Xinyue Gong, Wei Luo, Sheng Chen, Yunfeng Zhang, Rui Dou, and Hongyi Xiao. Dual-
conditional diffusion model for seismic data reconstruction: Integrating observed data and
sampling matrix constraints. IEEE Transactions on Geoscience and Remote Sensing, 63:
1–20, 2025. doi: 10.1109/TGRS.2025.3603101.
[8] Zhixiang Guo, Xinming Wu, Luming Liang, Hanlin Sheng, Nuo Chen, and Zhengfa Bi.
Cross-domain foundation model adaptation: Pioneering computer vision models for geo-
physical data analysis. Journal of Geophysical Research: Machine Learning and Compu-
tation, 2(1):e2025JH000601, 2025. doi: 10.1029/2025JH000601.
[9] Chao Li, Guo Liu, Xia Chen, Zeyu Li, Sergey Fomel, and Yangkang Chen. Joint recon-
struction and multiple attenuation using one-step randomized-order damped rank reduc-
tion method. IEEE Transactions on Geoscience and Remote Sensing, 62:1–11, 2024. doi:
10.1109/TGRS.2024.3435560.
[10] Chao Li, Sergey Fomel, Yangkang Chen, Robin Dommisse, and Alexandros Savvaidis.
Faultvitnet: A vision transformer assisted network for 3d fault segmentation. Journal of
Geophysical Research: Machine Learning and Computation, 2(2):e2024JH000488, 2025.
doi: 10.1029/2024JH000488.
[11] Chao Li, Guochang Liu, Zhiyong Wang, Zhichao Li, Sergey Fomel, and Yangkang
Chen.
Simultaneous off-the-grid deblending and data reconstruction via unsupervised
deep learning. IEEE Transactions on Geoscience and Remote Sensing, 63:1–11, 2025. doi:
10.1109/TGRS.2025.3548644.
[12] Markus Reichstein, Gustau Camps-Valls, Bjorn Stevens, Martin Jung, Joachim Denzler,
Nuno Carvalhais, and Prabhat. Deep learning and process understanding for data-driven
earth system science. Nature, 566(7743):195–204, 2019. doi: 10.1038/s41586-019-0912-1.
[13] Omar M Saad, Yangkang Chen, Alexandros Savvaidis, Sergey Fomel, Xinyu Jiang, Dingyao
Huang, et al. Deep denoising autoencoder for seismic random noise attenuation. Geo-
physics, 85(6):V367–V376, 2020. doi: 10.1190/GEO2019-0605.1.
[14] Omar M. Saad, Sergey Fomel, Raymond Abma, and Yangkang Chen. Unsupervised deep
learning for 3d interpolation of highly incomplete data. Geophysics, 88(1):WA189–WA200,
2023.
[15] Omar M Saad, Randy Harsuko, and Tariq Alkhalifah. Siamesefwi: A deep learning network
for enhanced full waveform inversion. Journal of Geophysical Research: Machine Learning
and Computation, 1(3):e2024JH000227, 2024.
[16] Johannes Schneider, Christian Meske, and Patrick Kuss.
Foundation models: A new
paradigm for artificial intelligence. Business & Information Systems Engineering, 66(2):
1–11, 2024. doi: 10.1007/s12599-024-00851-0.
[17] Hanlin Sheng, Xinming Wu, Xu Si, Jintao Li, Sibo Zhang, and Xudong Duan. Seismic
foundation model (sfm): A next-generation deep-learning model in geophysics. Geophysics,
90(2):IM59–IM79, 2025. doi: 10.1190/GEO2024-0087.1.
[18] Carol Tenopir, Lisa Christian, Suzie Allard, and Jennifer Borycz. Research data sharing:
Practices and attitudes of geophysicists. Earth and Space Science, 5(12):891–902, 2018.
12
XINYUE GONG, SERGEY FOMEL, AND YANGKANG CHEN
doi: 10.1029/2018EA000461.
[19] Xinming Wu, Jianwei Ma, Xu Si, Zhengfa Bi, Jiarun Yang, Hui Gao, et al.
Sensing
prior constraints in deep neural networks for solving exploration geophysical problems.
Proceedings of the National Academy of Sciences, 120(23):e2219573120, 2023. doi: 10.
1073/pnas.2219573120.
[20] Fangshu Yang and Jianwei Ma.
Deep-learning inversion:
A next-generation seismic
velocity model building method.
Geophysics, 84(4):R583–R599, 2019.
doi: 10.1190/
GEO2018-0249.1.
[21] Liuqing Yang, Wei Chen, Hang Wang, and Yangkang Chen. Deep learning seismic random
noise attenuation via improved residual convolutional neural network. IEEE Transactions
on Geoscience and Remote Sensing, 59(9):7968–7981, 2021.
[22] Y. Zhou, S. Li, D. Zhang, and Y. Chen. Seismic noise attenuation using an online subspace
tracking algorithm. Geophysical Journal International, 222(3):1765–1788, 2020.
[23] Y. Zhou, J. Yang, H. Wang, G. Huang, and Y. Chen. Statistics-guided dictionary learning
for automatic coherent noise suppression. IEEE Transactions on Geoscience and Remote
Sensing, 60:1–17, 2020.
SWAN
13
Figure 1. Overview of the SWAN data processing pipeline, including syn-
thetic and real data sources, patch extraction, normalization, quality filtering,
and metadata generation.
14
XINYUE GONG, SERGEY FOMEL, AND YANGKANG CHEN
Figure 2. Representative 128 × 128 patches sampled from the four SWAN
categories.
Each group of three rows corresponds to one data type and is
outlined using a distinct border color: real poststack (red, rows 1–3), real
prestack (teal, rows 4–6), synthetic poststack (blue, rows 7–9), and synthetic
prestack (green, rows 10–12).
SWAN
15
Figure 3. Residual-guided diffusion framework used for seismic reconstruc-
tion. The training stage (top) learns residual increments, while the sampling
stage (bottom) applies deterministic reverse diffusion conditioned on the ob-
served waveform.
Figure 4. Example 1. Interpolation of a synthetic hyperbolic gather with
50% irregular sampling. (a) Complete data. (b)–(e) Reconstruction results of
POCS, DRR, PySeisTr, and the proposed method. (f) Observed gather with
50% missing traces. (g)–(j) Corresponding residual panels.
16
XINYUE GONG, SERGEY FOMEL, AND YANGKANG CHEN
Figure 5. Example 2. Interpolation of a synthetic edge-structure gather with
50% irregular sampling. (a) Complete data. (b)–(e) Reconstruction results of
POCS, DRR, PySeisTr, and the proposed method. (f) Observed gather with
50% missing traces. (g)–(j) Corresponding residual panels.
Figure 6. Example 3.
Interpolation of a 3D synthetic hyperbolic volume
with 50% irregular sampling. (a) Complete data. (b)–(e) Results of POCS,
DRR, PySeisTr, and the proposed model. (f) Observed data with 50% missing
traces. (g)–(j) Residual panels.
SWAN
17
Figure 7. Example 4. Reconstruction of a synthetic DAS gather with 50% ir-
regular sampling. (a) Complete data. (b)–(e) Reconstruction results of POCS,
DRR, PySeisTr, and the proposed method. (f) Observed data with 50% miss-
ing traces. (g)–(j) Corresponding residuals.
18
XINYUE GONG, SERGEY FOMEL, AND YANGKANG CHEN
Figure 8. Example 5. Reconstruction of Viking Graben 2D field data with
30%, 50%, and 70% random trace removal. (a) Complete post-stack data. (b)–
(d) Observed data. (e)–(p) Reconstructions for all methods at each removal
level.
SWAN
19
Figure 9. Example 6. Reconstruction of SeanS3 3D field data with 50% miss-
ing traces. (a) Complete volume. (b) Observed data. (c)–(f) Reconstructions
from POCS, DRR, PySeisTr, and the proposed model.
20
XINYUE GONG, SERGEY FOMEL, AND YANGKANG CHEN
Figure 10. Example 7. Reconstruction of a zoomed field DAS segment with
50% irregular sampling. (a)–(f) Complete, observed, and reconstructed data
for all methods. (g)–(l) Zoomed and residual views.
SWAN
21
Figure 11. Example 8. Reconstruction of a 1997 BP shot gather with 50%
missing traces.
22
XINYUE GONG, SERGEY FOMEL, AND YANGKANG CHEN
Figure 12. PSTM imaging results for the 1997 BP model.
