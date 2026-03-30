# Silva_2024_REDOX_Gas

From Memory Traces to Surface Chemistry:
Decoding REDOX Reactions
Ana Luiza Costa Silva,∗,† Rafael Schio Wengenroth Silva,† Lucas Augusto
Mois´es,† Adenilson Jos´e Chiquito,† Marcio Peron Franco de Godoy,† Fabian
Hartmann,‡ and Victor Lopez-Richard†
†Departamento de F´ısica, Universidade Federal de S˜ao Carlos, 13565-905, S˜ao Carlos, SP,
Brazil
‡Julius-Maximilians-Universit¨at W¨urzburg, Physikalisches Institut and W¨urzburg-Dresden
Cluster of Excellence ct.qmat, Lehrstuhl f¨ur Technische Physik, Am Hubland, 97074
W¨urzburg, Deutschland
E-mail: analuiza@df.ufscar.br
Abstract
Gas and moisture sensing devices leveraging the resistive switching effect in tran-
sition metal oxide memristors promise to revolutionize next-generation, nano-scaled,
cost-effective, and environmentally sustainable sensor solutions. These sensors encode
readouts in resistance state changes based on gas concentration, yet their nonlinear
current-voltage characteristics offer richer dynamics, capturing detailed information
about REDOX reactions and surface kinetics. Traditional vertical devices fail to fully
exploit this complexity. This study demonstrates planar resistive switching devices,
moving beyond the Butler-Volmer model. A systematic investigation of the electro-
chemical processes in Na-doped ZnO with lateral planar contacts reveals intricate pat-
terns resulting from REDOX reactions on the device surface. When combined with
1
arXiv:2409.07299v2  [physics.app-ph]  28 Oct 2024
advanced algorithms for pattern recognition, allow the analysis of complex switching
patterns, including crossings, loop directions, and resistance values, providing unprece-
dented insights for next-generation complex sensors.
Introduction
The demand for advanced, miniaturized, and efficient information processing and sensing
technologies is driving the development of innovative semiconductor materials beyond sili-
con1–3. While some materials offer advantages in processing complexity, cost-effectiveness,
flexibility, and environmentally sustainable, other materials enable applications that cannot
be realized within silicon technology, e.g. spintronics, Mottronics, and in-memory comput-
ing4–6 to name a few. One specific notable phenomenon in electronic devices, absent in
silicon, is the resistive memory effect, which can be observed in materials fabricated with a
metal-insulator-metal (MIM) structure, whose insulating layer is often composed of a transi-
tion metal oxide or a semiconductor oxide7–10. Such structures can be utilized in traditional
computing architectures and in novel beyond von Neumann computational architectures,
such as in-memory computing, artificial neural networks or reservoir computing11–13. Ex-
ploring the electronic conduction mechanisms of materials exhibiting memory traces also
enable novel smart solutions for sensing applications of gases, gas mixtures and atmospheres.
Additional research indicates that certain semiconductor oxides exhibit resistive mem-
ory effects alongside with sensing functionalities, commonly referred to as “gasistors”10,14.
Among various approaches, elucidating the role of the surface in these processes presents
a significant challenge. Studies on gas sensing underscore the critical importance of un-
derstanding the interactions between gas-sensitive materials and the ambient atmosphere15.
However, the conventional MIM electrical contact configuration limits the detection capabil-
ities of memristor-based gas sensors, as the gas primarily interacts with the upper electrode
rather than directly with the oxide surface. Nontraditional setups such as lateral planar
electrical contacts, provide deeper insights into the factors influencing the resistive memory
2
effect. It also allows to expand the active detection area exposing the material surface either
partially or completely to the target element16. Thus, employing a lateral planar electrical
contact geometry enables the investigation of the active role of the film surface for mem-
ory effects of semiconductor oxides when exposed to various atmospheric conditions that
electrochemically react with it.
We present both theoretical and experimental evidence of complex patterns emerging
in the current-voltage loops of planar memristive devices. These phenomena result from
REDOX reactions at various sites and under different environments, revealing a complexity
that extends beyond the traditional Butler-Volmer model. Based on Na-doped ZnO planar
memristive devices synthesized by spray-pyrolysis, we show experimentally how the current-
voltage characteristics alter in the presence of different gas environments and how intricate
behaviors beyond the resistance change emerge. These behaviors differ in the number of
crossings, the symmetry of the response, and the polarity-dependent memory content. We
derive an analytical solution by adapting the Butler-Volmer model, which correlates changes
in the current-voltage response with the reaction type, the surrounding environment, and
the specific location of the reaction site.
Methods
Sample Preparation. The investigated system consists of (002) oriented polycrystalline
Na-doped ZnO thin films synthesized by the spray pyrolysis technique. This process is based
on spraying a precursor solution, carried by dry air, onto a preheated substrate where the
chemical-physical growth occurs. In this study, zinc acetate dihydrate (Zn(C2H3O2)2·2H2O
by Synth) and sodium hydroxide (NaOH by NEON) were used as the precursors. The zinc
and sodium precursor solutions were prepared in distilled water with a molarity of 5·10−3M
and thermally stirred at 100 ◦C. A nominal content of 10%Na was used for Zn doping,
referred to as ZnO:Na10%. The deposition and growth of the films were carried out at 300
3
◦C with a flow rate of 0.3 mL/min. For further details on the sample preparation via spray
pyrolysis, refer to17.
Material Characterization. The Thermo Scientific K-Alpha spectrometer provided
the X-ray photoelectron spectroscopy (XPS) for surface chemical analysis using the Al-Kα
monochromatic radiation (1486.6 eV). The spectra were fitted by a combination of Gaus-
sian (70%) and Lorentzian (30%) functions employing the Shirley method as the baseline
and aligning spectra on the adventitious carbon peak (C 1s – 284.8 eV) to correct charging
effects. Film morphology was analyzed using a scanning electron microscope (SEM) model
JEOL JSM 6510, equipped with a 20 kV electron beam and secondary electron (SE) mode.
With a high conductive silver paint 503, two planar electrical contacts separated by 1 mm
were prepared, allowing a large area for atmosphere contact. For electrical characterization,
a Keysight B2901A source measure unit provided the Current-voltage (I-V) curves and hys-
teresis loops with the sample mounted in a Linkam Scientific HFS600E cryostat equipped
with two tungsten positional probes. All measurements were performed at room tempera-
ture under various atmospheric conditions, including ambient air, vacuum, controlled relative
humidity (RH), and atmospheres of oxygen (O2) and carbon dioxide (CO2).
Theoretical Methods. For the theoretical simulation of the electrochemical reactions
occurring at the surface under lateral bias, we propose an alternative to the conventional
Butler-Volmer model. Our approach accounts for the complex interplay between different
electrochemical processes at various surface sites, including their respective REDOX charac-
teristics and environments. The electron transfer for each process is emulated by solving a
set of differential equations grounded in the relaxation time approximation. These equations
describe the time evolution of surface electron density fluctuations due to local reactions.
Numerical solutions were obtained using standard Runge-Kutta methods, which allowed
us to model the dynamic conductance response under varying voltage sweeps and simulate
the resulting current-voltage hysteresis loops. This approach provides a nuanced view of
concomitant electrochemical processes in laterally biased device configurations.
4
Results and discussion
The direction and rate of electrochemical reactions depend on the combined influence of
thermodynamics and kinetics. Thermodynamics, captured by the Gibbs free energy change
(∆GB), dictates the spontaneity and equilibrium of the reaction18. A negative ∆GB indicates
a thermodynamically favorable reaction, while the magnitude of ∆GB reflects the driving
force. However, ∆GB alone doesn’t provide information about the reaction time and a kinetic
approach is thus needed. In general, the activation energy over an energy barrier governs the
reaction rates. In electrochemical reactions, electron transfer processes involve overcoming
energy barriers at the electrode surface, as illustrated in Figure 1. Figure 1(a) depicts the
schematic representation of REDOX reactions at perpendicularly polarized electrodes. The
Butler-Volmer equation serves as a bridge between thermodynamic and kinetic reactions,
specifically those occurring at the electrode-electrolyte interface19. It relates the carrier flux
or electron transfer rate, fBW, to the difference between the actual electrode applied potential
and the equilibrium potential predicted by thermodynamics, ∆ϕ, and can be expressed as20
fBW = f0

exp

αe∆ϕ
kBT

−exp

−(1 −α) e∆ϕ
kBT

.
(1)
Here, ∆ϕ is the potential difference at the electrode-insulator interface and f0 relates to ex-
change current density which is proportional to the equilibrium activation rate, ke−∆GB/kBT.
k is a proportional constant, and kBT the thermal energy. Figure 1(b) schematically depicts
the Gibbs energy profile near the surfaces for perpendicularly polarized electrodes.
The
probability of an electron overcoming the activation barrier determines the reaction rate and
is influenced by the asymmetry of the barriers for the forward and reverse reactions. It
is characterized by the transfer coefficient α ∈[0, 1] in Equation 1. A transfer coefficient
of α = 0.5 represents a symmetrical reaction mechanism, where both forward and reverse
reactions have the same activation barriers and proceed at equal rates.
The Butler-Volmer equation has limitations in accurately describing electrochemical re-
5
actions at laterally biased surfaces due to several factors. It does not explicitly consider
the potential concomitance of oxidation and reduction reactions occurring simultaneously at
surface defects, such as vacancies or dangling bonds. The equation also assumes a uniform
and homogeneous electrode surface, whereas laterally biased surfaces may exhibit gradients
in properties such as work function or electron density. For instance, surface defects and
dangling bonds can act as active sites, displaying lower activation energies for oxidation and
reduction reactions compared to defect-free regions. Consequently, at these defect sites, both
oxidation and reduction reactions associated with a specific reactant compete, influencing
the overall electrical conductivity.
Let’s consider the case of contacts placed laterally on an electrode as shown in Fig-
ure 1(c), a configuration relevant to many technologies like finger-contact sensors and our
device. These contacts experience a potential difference, leading to a linear gradient of the
electrochemical potential across the electrode surface, as sketched in Figure 1(d) and (e) for
positive and negative bias, respectively. Let’s also assume, as represented in that panel, that
the surface contains active sites of size d, resulting in a local potential drop of |η|V , where
|η| = d/L. We can then consider various configurations of potential profiles to characterize
the electrochemical process triggered at these sites, describing how different chemical species,
with either oxidant or reductant character, interact with the surface. The electron transfer
rate for all these configurations can be expressed by the following equation as described in
Ref. 21
fL(V ) = f0
η

exp

αη eV
kBT

+ exp

−(1 −α) η eV
kBT

−2

.
(2)
In this equation, f0 ∝exp(−∆GB/kBT), where ∆GB is the Gibbs activation energy barrier
represented by the gray lines in Figure 1(d) and (e). More information on the details of this
equation and deviations from the Butler-Volmer model can be found in the Suppl. material.
The transfer coefficient α in Eq. 2 continues to weight the configuration symmetry, and η
corresponds to the reaction character: for η < 0 the reaction is reductant and otherwise
6
oxidant.
In Figure 1, the red and blue arrows represent the main electron fluxes at the interfaces
of the active sites, corresponding to electron capture and release due to the REDOX char-
acter, respectively. In symmetric cases (α = 0.5), two primary configurations emerge: one
characterized by a purely oxidant contribution independent of polarity, denoted as case A
and another (case B) featuring a purely reductant character, also independent of polarity.
Additionally, two asymmetric configurations, labeled as C and D, are depicted to underscore
the polarity dependence of the REDOX reactions in those cases.
RED
OX
V
(a)
e-
e-
(b)
Gibbs free energy 
Growth direction
oxidant
reductant
A
A
B
B
C
C
D
D
(d)
d
ΔGB
oxidant
reductant
Reactant character:
Positive bias
Negative bias (e)
Gibbs free energy 
OX
L
e-
e-
RED
V
(c)
Figure 1: (a) Schematic representation of REDOX reactions at perpendicularly biased elec-
trodes and (b) the corresponding Gibbs energy profile close to the surfaces. (c) Representa-
tion of the REDOX reactions under lateral biasing, (d) and (e) potential Gibbs energy profiles
for lateral electron activation and trapping under positive and negative biases, respectively:
A, predominant surface oxidation for a symmetric molecular adsorption; B, predominant
surface reduction for a symmetric molecular adsorption; C, predominant surface oxidation
(reduction) under positive (negative) bias; D, predominant surface reduction (oxidation) un-
der positive (negative) bias.
Surface REDOX reactions can be significantly enhanced by introducing reactive elements
into oxide hosts. For example, the spray-pyrolysis technique offers an efficient and versatile
7
method for doping ZnO with strategic elements. This approach is cost-effective, operates
without the need for vacuum conditions, and supports large-scale material production. Fur-
thermore, the residual gases released during film growth are environmentally benign, making
this technique both practical and eco-friendly. The experiments were conducted with resis-
tive memory devices based on Na-doped ZnO, prepared as described in Ref. 22 with 10%
nominal Na-content. Insights about the surface feature, like surface defects and adsorp-
tion sites, were obtained by X-ray photoelectron spectroscopy (XPS) as shown in Figure 2.
Figures 2(a) and (b) display the survey scans for the undoped ZnO (reference sample) and
Na-doped ZnO, respectively. The data show that the surfaces primarily consist of Zn, O, and
C, with Na detected only in the Na-doped sample – indicating the absence of contamination
in the growth process as depicted in the undoped ZnO film, Figure 2(c), while the ZnO:Na
sample exhibits a binding energy at 1071.4 eV – attributed to the Na–O bond23, Figure 2(d).
The high-resolution spectra in the O 1s are shown in Figures 2(e) e (f) for ZnO and
ZnO:Na, respectively. Two distinct peaks are observed: the lower energy peak, O 1s(1),
corresponds to oxygen bonded to Zn or substitutional Na in the ZnO wurtzite structure24,25,
while the higher energy peak, O 1s(2), can be attributed to two possible surface species –
oxygen vacancies (VO) in the ZnO lattice23,26 or hydroxyl groups (OH) from chemisorbed
water27,28. Furthermore, the Na-doped ZnO sample exhibits a higher energy shoulder at
535.9 eV (O 1s(3)) assigned to water molecules in the gas phase interacting with the atmo-
sphere29. Notably, the higher intensity of O 1s(2) indicates a Na-inducing mechanism that
increases the density of oxygen vacancies30, which are then partially occupied by OH groups
detected by XPS. Figure 2 also presents SEM images illustrating the surface morphology
of both undoped and Na-doped ZnO films at a 2 µm scale. In Figure 2(g), the undoped
ZnO shows a smooth, homogeneous surface, typical of nanostructured polycrystalline films.
The addition of sodium, however, introduces distinct morphological features, such as micro-
and nanostructures. Figure 2(h) reveals the nanoporous surface morphology of Na-doped
ZnO, whose hydrophilic nature can trap water molecules, evidenced by the O 1s(3) band in
8
the XPS spectrum. These microscopic observations underscore the significant impact of the
synthesis method on defining structural characteristics, particularly in relation to dopant
effects on surface morphology and potential applications. Dopant incorporation influences
electrochemical properties by modifying the active surface area available for reactions, which
may lead to non-uniform charge distribution and fluctuations in electric fields and reaction
rates31,32. Such effects can result in unregulated or slower REDOX processes and the for-
mation of charge traps that impede electron transfer. Furthermore, dopant agglomerations
impair ionic mobility, which compromises the efficiency and reliability of devices such as
sensors and resistive memory systems, ultimately reducing their sensitivity, stability, and
overall performance33–35.
0
3 0 0
6 0 0
9 0 0
1 0 7 6
1 0 7 2
1 0 6 8
5 3 7
5 3 4
5 3 1
5 2 8
( h )
( g )
N a  1 s
O  K L L
( f )
( d )
( b )
( e )
( c )
Z n  3 d
Z n  3 s
Z n  3 s
C  1 s
Z n  L M
M
O  1 s
Z n  L M
M
O  K L L
Z n  2 p
3 / 2
Z n  2 p
1 / 2
( a )
Z n  3 d
Z n  3 s
Z n  3 s
C  1 s
Z n  L M
M
O  1 s
Z n  L M
M
Z n  2 p
3 / 2
Z n  2 p
1 / 2
O  1 s
Z n O : N a
Z n O : N a
Z n O : N a
Z n O
Z n O
Z n O
N a  1 s
O 1 s ( 1 )
I n t e n s i t y  ( a .  u . )
B i n d i n g  E n e r g y  ( e V )
O  1 s ( 3 )
O  1 s ( 2 )
O  1 s ( 2 )
O  1 s ( 1 )
Figure 2: XPS spectra of ZnO and ZnO:Na films – (a) and (b) survey scans, (c) and (d)
high-resolution XPS of the Na 1s level, (e) and (f) high-resolution XPS of the O 1s level.
The SEM images at 2 µm scale with 750x magnification are shown in (g) and (h) for the
ZnO and ZnO:Na, respectively.
Experiments using normal pulse voltammetry with rectangular voltage pulses, as depicted
in Figure 3(a), were conducted in an ambient atmosphere. Figures 3(b) and (c) depict the
observed evolution of the conductance during the application of positive and negative bias
voltage pulses, respectively, with a pulse duration of 600 seconds. Our analysis reveals at least
six distinct contributions with contrasting timescales. To facilitate the fitting process, we
9
combine these contributions into pairs, designated as mechanisms 1, 2, and 3, as illustrated
in Figures 3(b) and (c). For mechanism 1, two characteristic timescales can be extracted: τ1
= 5 s and τ2 = 63 s. Mechanism 2 exhibits timescales of τ1 = 25.8s s and τ2 = 33.2s. Finally,
the mechanism 3 displays the longest duration with τ1 = 90 s and τ2 = 155 s. Nonmonotonic
temporal transients in the conductance can indicate the concurrence of processes occurring
at different timescales.
8
1 6
0
2 0 0
4 0 0
6 0 0
- 4 0
0
( c )
( b )
2 0
 E x p e r i m
e n t a l  R e s u l t
 T h e o r e t i c a l  R e s u l t
 M
e c h a n i s m
 1
 M
e c h a n i s m
 2
 M
e c h a n i s m
 3
 
C o n d u c t a n c e  ( n S )
+2 0  V
V o l t a g e  ( V )
0
( a )
T i m
e  ( s )
−2 0  V
Figure 3: (a) Rectangular voltage pulses for which the conductance evolution with time was
obtained: (b) for positive bias and (c) for negative bias.
The experimental cyclic voltammetry analysis was conducted using voltage sweeps with
a 20 V amplitude. The results, displayed in Figure 4, show current-voltage loops under
different scanning periods. In vacuum, as shown in Figure 4(a), the measurement exhibits
ohmic behavior, with no observable hysteresis. In contrast, under ambient atmosphere (Fig-
10
ures 4(b)-(f)) memory traces appear which are sensitive to the sweep periods. First, Fig-
ure 4(b) shows the evolution of the hysteresis loops towards stabilization for a scanning
period of 30 seconds. All other figures correspond to stabilized responses. A complex pat-
tern with different maximal and minimal currents, memory content, and number of crossings
emerges under different periods of the voltage driving. While for 60s only a single crossing
at zero bias emerges, the number of crossing increases to 2 for larger periods with an avoided
crossing at zero bias. Also, the maximal and minimal current values exhibit a non-monotonic
behavior with maximal currents observed at a period of 120s.
To examine how complex patterns emerge depending on the REDOX character, Fig-
ures 4(g)-(i) present the current-voltage hysteresis loops generated under controlled atmo-
spheres of O2, CO2, and H2O (measured at varying relative humidity (RH) levels). The
conductance in all three environments is significantly higher than in vacuum, with distinct
differences observed between the atmospheres. One notable difference is the time scale, with
CO2 reactions responding more rapidly than those in O2 or H2O. It is clear that the complex
effects observed under ambient conditions cannot be attributed solely to the sum of these
three components. The intricate dynamics revealed in Figures 4(b)-(f) likely result from the
combined electrochemical effects of various species, potentially including interactions with
CO molecules present in the atmosphere15, which were not examined in this study. Addi-
tionally, moisture is expected to have complex effects36, potentially involving ionic transport
channels through surface vacancies and protonic diffusion over hydroxyl groups37. The for-
mation of adsorbed carbonates on the ZnO surface hydroxyls cannot be ruled out either38,39.
Pattern recognition is an area where artificial intelligence significantly surpasses tradi-
tional computing architectures, including quantum computing40.
As shown in Figure 4,
the hysteresis loops differ in several key aspects: the number of crossings, the minimum
and maximum current values, the memory content within the loops, and the symmetry of
the current-voltage response under voltage polarity reversal. Traditionally, assessments of
device sensitivity have focused on variations between the Low Resistance State (LRS) and
11
- 5
0
5
- 1 0
0
1 0
- 3 0
0
3 0
- 1 0
0
1 0
- 8
0
8
- 1
0
1
- 2 0
- 1 0
0
1 0
2 0
- 3
0
3
- 2 0
- 1 0
0
1 0
2 0
- 5
0
5
- 2 0
- 1 0
0
1 0
2 0
- 1 5
0
1 5 ( i )
( h )
( g )
( f )
( e )
( d )
( c )
( b )
( a )
P e r i o d :  6 0  s
C u r r e n t  ( n A )
P e r i o d :  1 2 0  s
P e r i o d :  6 0 0  s
P e r i o d :  9 0 0  s
P e r i o d :  3 0  s
P e r i o d :  6 0 0  s
V a c u u m
 6 0 0  s
 1 2 0  s
O x y g e n
V o l t a g e  ( V )
 1 2 0  s
 3 6 0  s
 6 0 0  s
C O
2
P e r i o d :  6 0 0  s
 R H  0 %
 R H  5 5 %
 R H  7 5 %
H
2 O
Figure 4: (a) Experimental current-voltage sweep performed in vacuum, (b) current-voltage
loops performed over a 30-second period, illustrating the stability trend of the system through
the cycles. (c)-(f) Stable current-voltage loops performed in ambient atmosphere for increas-
ing voltage sweeping periods. Stable loops obtained under controlled atmospheres of (g)
oxygen (O2) and (h) carbon dioxide (CO2). Relative humidity of: 0% (dry air), 55% ± 5%
and 75% ± 5% were also analyzed at scan periods of (i) 600 seconds.
High Resistance State (HRS) in response to different gases and concentrations While this
approach facilitates straightforward integration with readout circuits, it overlooks the much
richer and more selective information encoded in the full loop dynamics. For example, under
ambient conditions, multiple crossings are evident, whereas a pure O2 atmosphere shows
no such crossings, and a CO2 atmosphere exhibits multiple crossings during specific scan-
12
ning intervals. Additionally, the symmetry of the response allows for clear differentiation
between O2 and CO2 atmospheres. In contrast, high humidity levels result in a weaker mem-
ristive response but larger minimum and maximum currents. This analysis reveals distinct
and identifiable patterns corresponding to different atmospheric conditions, enabling precise
differentiation between them.
The origin of the complex behavior can be attributed to the simultaneous occurrence
of different electrochemical reactions at surface sites with varying environments.
These
reactions induce fluctuations in surface electron density, δn, leading to deviations of the
surface conductance from its equilibrium value, G0, by Gn ∝δn. To fully account for the
contributions of each electrochemical reaction, the electron transfer rate for each reaction
type (j) must be considered. This requires introducing the index (j) in Eq. 2, which identifies
each process and its corresponding transfer rate, f (j)
L , reflecting different environments (∆G(j)
B
and α(j)) and REDOX characteristics (η(j)). Each process, governed by its relaxation time
(τj), evolves over according to
dδn(j)
dt
= −δn(j)
τj
+ f (j)
L (V ),
(3)
resulting in a total fluctuation δn(V ) = P
j δn(j) which influences the conductance as
G(V ) = G0 + eµ
L2δn(V ),
(4)
where the current is defined by I = G · V , with µ representing electron mobility and e the
elementary charge. Solving Equation 3 under this condition yields the electron fluctuation,
δn(j)(t) = τjf (j)
L (V0) +
h
δn(j)(0) −τjf (j)
L (V0)
i
exp(−t/τj) and the corresponding conductance
response to the voltage step (assumed to start at t = 0)
G = ˜G0 +
X
j
˜G(j) exp

−t
τj

,
(5)
13
where ˜G0 = G0 + eµ
L2
P
j τjf (j)
L (V0) represents the background conductance contribution and
˜G(j) = eµ
L2
h
δn(j)(0) −τjf (j)
L (V0)
i
. Note that the sign of ˜G(j) depends on the initial fluctuation
condition and can be positive or negative. Beyond this ambiguity, Equation 5 captures the
interplay between the influence of various types of active sites and their characteristic time
constants, τj. The experiments using normal pulse voltammetry with rectangular voltage
pulses (see Figures 3(b) and (c)) have been fitted using Equation 5. While the model captures
the core reaction kinetics, it doesn’t account for mass transport and interdiffusion, which
can introduce delays in the transient response of conductance. To address this and fit the
experimental results in Figures 3(b) and (c), a time delay (t →t−∆tdelay
(j)
) was incorporated
into Equation 5.
To replicate the intricate patterns observed in the experimental cyclic voltammetry data
shown in Figure 4, current-voltage curves can be calculated using Equations 3 and 4. This
involves applying various transfer rates, f (j)
L , which account for different environments (∆G(j)
B
and α(j)) and REDOX character (η(j)).
Our primary focus is on emulating the number
of crossings, the symmetry of the memory content, maximal current values, and the loop
direction, all of which are influenced by these variations.
First, we consider a simple single process that breaks inversion symmetry (α →1), as
illustrated in diagrams C or D of Figure 1(d), and further depicted in Figure 5(a) and (b).
The resulting memory loops are asymmetric with a zero-voltage crossing. For an oxidizing
reaction (Figure 5(a)), the maximum current observed for positive polarity is lower than that
for negative polarity, and the current-voltage loop exhibits a clockwise rotation. Conversely,
for a reducing reaction (Figure 5(b)), the maximum current for positive polarity exceeds
that for negative polarity, and the loop rotates counterclockwise.
For a more symmetrical case (while keeping α ̸= 0.5), the loop shape, even with a single
transfer mechanism, may exhibit multiple crossings within the first or third quadrant of the
current-voltage plane. Two possible scenarios are depicted in Figures 5(c) and (d). It is
important to note that the presence of an additional crossing in either the upper or lower
14
loop is influenced by the transition in reaction character (from oxidant to reductant and vice
versa) at positive or negative polarity, as well as by the voltage sweep rate. Further details
can be found in the Supplementary Material and in Ref. 21.
When two concurrent transfer mechanisms with similar relaxation times, such as those
characterized by τ2 and τ3, are present, the resulting memory traces become even more
intricate. In this situation, varying the voltage period can cause the total area of the upper
loop to change sign, leading to a complete reversal of the loop direction and producing
multiple crossings in the first quadrant21.
A specific case involving two concurrent symmetric oxidation and reduction processes,
each with identical relaxation times but differing activation energy barriers as described in
Equation 2, is illustrated in Figure 5(e). This scenario produces a pinched, non-crossing
hysteresis at V = 0, due to the combined influence of the two opposing transfer functions.
The transition between oxidant and reductant behavior with varying bias introduces addi-
tional crossings in the first and third quadrants. By adjusting the relative strengths of these
two processes, the loop direction can be reversed, as depicted in Figure 5(f). Breaking the
inversion symmetry leads to polarity dependence, which results in a crossing at V = 0 and
the possibility of an extra crossing in one of the quadrants.
Our analysis reveals that at shorter periods (Figures 4(b) and (c)), the dynamics cor-
respond to asymmetric adsorption, characterized by oxidation at positive polarity and re-
duction at negative polarity. This behavior is accurately captured by the theoretical model
shown in Figure 5(a). As the period lengthens, an inverted dynamic emerges, characterized
by multiple crossings, as depicted in Figure4(d) and aligned with the theoretical patterns
in Figure5(c) or (e). At the longest periods, these asymmetric dynamics appear to subside,
revealing the influence of two concurrent symmetric contributions—oxidation and reduc-
tion—which can be observed in Figure 4(e). Here, surface reduction dominates at higher
voltages, leading to curve intersections in both quadrants without crossing at the origin.
The experimental curves in Figures 4(e) and (f) show strong similarities with the theoretical
15
- 2
0
2
4
- 4
- 2
0
2
- 2
0
2
4
- 2 0
0
2 0
- 2
0
2
- 2 0
0
2 0
- 2
0
2
- 2 0
0
2 0
- 1
0
1
( a )
C u r r e n t  ( a .  u . )
( f )
( e )
( c )
( b )
( d )
V o l t a g e  ( V )
Figure 5: Theoretical current-voltage loops: (a), (b), (c), and (d) for a single asymmetric
electron transfer process, while (e) and (f) illustrate current-voltage loops for a combination
of two symmetric electron transfer processes.
16
predictions in Figure 5(e), while those in controlled atmospheres align with the processes
illustrated in Figures 4(b) and (c). Table 1 summarizes the parameters extracted from these
experiments, with the final three columns corresponding to the results of the computational
simulations. Additional I-V loops for different sweep periods are presented in Figure S4 in
the Supplementary Information.
Table 1: Parameters extracted from the I-V hysteresis curves. CW and CCW, denoting the
direction of the loop under positive polarity—clockwise and counterclockwise, respectively.
Y (Yes) and N (No) indicate the presence of zero-bias crossings, multiple crossings, symmetry
of the current in the positive and negative quadrants, and symmetry of the hysteresis loop
contents.The parameter η characterizes the oxidizing or reducing nature of the process,
while the mechanism denotes whether the process is a single asymmetric (1 AS) process or
a combination of two symmetric processes (2 S). The final column shows which theoretical
curve corresponds to the experimental data.
Period
Loop
direction
Zero
crossing
Additional
crossing
Symmetry
(current)
Symmetry
(content)
η
Mechanism
Figure 3
ambient atmosphere
30 s
CW
Y
N
Y
Y
positive
1 AS
a
60 s
CW
Y
N
Y
Y
positive
1 AS
a
120 s
CCW
Y
Y
Y
N
positive
1 AS
c
600 s
CW/CCW
N
Y
Y
Y
negative
positive
2 S
e
900 s
CW/CCW
N
Y
Y
Y
negative
positive
2 S
e
in O2 atmosphere
120 s
CCW
Y
N
Y
N
negative
1 AS
b
600 s
CCW
Y
N
Y
N
negative
1 AS
b
CO2 atmosphere
120 s
CCW
Y
N
Y
N
negative
1 AS
b
360 s
CCW
Y
Y
N
N
positive
1 AS
c
600 s
CCW
Y
N
N
N
negative
1 AS
b
H2O atmosphere
600 s - RH 0%
CCW
Y
N
Y
N
negative
1 AS
b
600 s - RH 55%
CCW
Y
N
Y
N
negative
1 AS
b
600 s - RH 75%
CCW
Y
Y
Y
N
positive
1 AS
c
17
Conclusions
In conclusion, our study uncovers the intricate dynamics of resistive memory in Na-doped
ZnO thin films under diverse atmospheric conditions. The complex current-voltage hysteresis
loops observed emphasize the influence of asymmetric adsorption configurations, the signif-
icance of voltage sweep rates, and the local environment in shaping memory traces. These
rich dynamics arise from the combined electrochemical interactions of multiple species. Our
proposed transfer rate formula, specifically designed for lateral biasing, offers a powerful tool
for analyzing electrochemical reactions at surface states. By integrating this refined model,
we can achieve a more precise characterization of the dynamic processes governing resistive
memory effects, leading to a deeper understanding of surface interactions and transfer mech-
anisms. This approach opens new avenues for optimizing electrochemical systems across
various applications.
18
Acknowledgement
This study was financed in part by the Coordena¸c˜ao de Aperfei¸coamento de Pessoal de
N´ıvel Superior - Brazil (CAPES); the Conselho Nacional de Desenvolvimento Cient´ıfico e
Tecnol´ogico - Brazil (CNPq) Proj. 311536/2022-0 and 312254/2023-7; and FAPESP: Procs.
2023/17490-2 and 2023/05436-3.
This research used resources provided by the National
Nanotechnology Laboratory (LNNano), which operates within the Brazilian Center for Re-
search in Energy and Materials (CNPEM), a private non-profit organization supervised by
the Ministry of Science, Technology, and Innovations (MCTI) of Brazil. We are grateful
to the XPS team for their help during the experimental work (proposals XPS-28104 and
XPS-28108).
References
(1) Wang, T.-Y.; Meng, J.-L.; Li, Q.-X.; He, Z.-Y.; Zhu, H.; Ji, L.; Sun, Q.-Q.; Chen, L.;
Zhang, D. W. Reconfigurable optoelectronic memristor for in-sensor computing appli-
cations. Nano Energy 2021, 89, 106291.
(2) Wei, S.; Li, Z.; John, A.; Karawdeniya, B. I.; Li, Z.; Zhang, F.; Vora, K.; Tan, H. H.;
Jagadish, C.; Murugappan, K.; others Semiconductor nanowire arrays for high-
performance miniaturized chemical sensing. Advanced Functional Materials 2022, 32,
2107596.
(3) Lee, D.; Yun, M. J.; Kim, K. H.; Kim, S.; Kim, H.-D. Advanced recovery and high-
sensitive properties of memristor-based gas sensor devices operated at room tempera-
ture. ACS sensors 2021, 6, 4217–4224.
(4) Joksas, D.; AlMutairi, A.; Lee, O.; Cubukcu, M.; Lombardo, A.; Kurebayashi, H.;
Kenyon, A. J.; Mehonic, A. Memristive, Spintronic, and 2D-Materials-Based Devices
19
to Improve and Complement Computing Hardware. Advanced Intelligent Systems 2022,
4, 2200068.
(5) Scheiderer, P.; Schmitt, M.; Gabel, J.; Zapf, M.; St¨ubinger, M.; Sch¨utz, P.; Dudy, L.;
Schlueter, C.; Lee, T.-L.; Sing, M.; others Tailoring materials for mottronics: excess
oxygen doping of a prototypical mott insulator. Advanced Materials 2018, 30, 1706708.
(6) Chiu, Y.-C.; Khwa, W.-S.; Yang, C.-S.; Teng, S.-H.; Huang, H.-Y.; Chang, F.-C.;
Wu, Y.; Chien, Y.-A.; Hsieh, F.-L.; Li, C.-Y.; others A CMOS-integrated spintronic
compute-in-memory macro for secure AI edge devices. Nature Electronics 2023, 6,
534–543.
(7) Datye, I. M.; Rojo, M. M.; Yalon, E.; Deshmukh, S.; Mleczko, M. J.; Pop, E. Localized
heating and switching in MoTe2-based resistive memory devices. Nano letters 2020,
20, 1461–1467.
(8) Zhang, F.; Zhang, H.; Krylyuk, S.; Milligan, C. A.; Zhu, Y.; Zemlyanov, D. Y.; Ben-
dersky, L. A.; Burton, B. P.; Davydov, A. V.; Appenzeller, J. Electric-field induced
structural transition in vertical MoTe2-and Mo1–x W x Te2-based resistive memories.
Nature materials 2019, 18, 55–61.
(9) Isyaku, U. B.; Khir, M. H. B. M.; Nawi, I. M.; Zakariya, M.; Zahoor, F. ZnO based
resistive random access memory device: a prospective multifunctional next-generation
memory. IEEE Access 2021, 9, 105012–105047.
(10) Lee, D.; Jung, J.; Kim, S.; Kim, H.-D. Gas detection and recovery characteristics at
room temperature observed in a Zr3N4-based memristor sensor array. Sensors and
Actuators B: Chemical 2023, 376, 132993.
(11) Zhang, B.; Guo, T.; Zhou, Y.; Lu, S.; Chen, Z.; Zhou, N.; Wu, Y. A. Asymmetric-
Resistive-Switching Device with Reconfigurable Synaptic Functions for Logic-In-
Memory. ACS Applied Engineering Materials 2024,
20
(12) Abunahla, H.; Halawani, Y.; Alazzam, A.; Mohammad, B. NeuroMem:
Analog
graphene-based resistive memory for artificial neural networks. Scientific reports 2020,
10, 9473.
(13) Zhong, Y.; Tang, J.; Li, X.; Gao, B.; Qian, H.; Wu, H. Dynamic memristor-based reser-
voir computing for high-efficiency temporal signal processing. Nature communications
2021, 12, 408.
(14) Chae, M.; Lee, D.; Jung, J.; Kim, H.-D. Enhanced memristor-based gas sensor for fast
detection using a porous carbon nanotube top electrode with membrane. Cell Reports
Physical Science 2023, 4.
(15) Blackman, C. Do we need “ionosorbed” oxygen species?(or,“a surface conductivity
model of gas sensitivity in metal oxides based on variable surface oxygen vacancy con-
centration”). ACS sensors 2021, 6, 3509–3516.
(16) Devi, M.; Khandelwal, S.; Vidiˇs, M.; Plecenik, T.; Jabir, A. A Gas-sensitive Current-
driven Memristor: Characterisation and Modelling. 2024 IEEE International Confer-
ence on Interdisciplinary Approaches in Technology and Management for Social Inno-
vation (IATMSI). 2024; pp 1–6.
(17) De Godoy, M.; de Herval, L.; Cotta, A.; Onofre, Y.; Macedo, W. ZnO thin films de-
sign: the role of precursor molarity in the spray pyrolysis process. Journal of Materials
Science: Materials in Electronics 2020, 31, 17269–17280.
(18) Landau, L. D.; Lifshitz, E. M. Statistical Physics; Pergamon Press: New York, 1980.
(19) Bard, A. J.; Faulkner, L. R.; others Fundamentals and applications. Electrochemical
methods 2001, 2, 580–632.
(20) Atkins, P.; De Paula, J. Physical chemistry; Macmillan, 2006; Vol. 1.
21
(21) Lopez-Richard, V.; Silva, R. S. W.; Lipan, O.; Hartmann, F. Tuning the conductance
topology in solids. Journal of Applied Physics 2023, 133, 134901.
(22) Silva, A. L. C.; Vargas, L. M.; Peres, M. L.; Teodoro, M. D.; de Godoy, M. P. Exploring
Na Doping in ZnO Thin Films: Electrical and Optical Insights. Coatings 2024, 14,
510.
(23) Erdogan, N.; Kutlu, T.; Sedefoglu, N.; Kavak, H. Effect of Na doping on microstruc-
tures, optical and electrical properties of ZnO thin films grown by sol-gel method.
Journal of Alloys and Compounds 2021, 881, 160554.
(24) Ye, Z.; Wang, T.; Wu, S.; Ji, X.; Zhang, Q. Na-doped ZnO nanorods fabricated by
chemical vapor deposition and their optoelectrical properties. Journal of Alloys and
Compounds 2017, 690, 189–194.
(25) Mueen, R.; Lerch, M.; Cheng, Z.; Konstantinov, K. Na-doped ZnO UV filters with
reduced photocatalytic activity for sunscreen applications. Journal of Materials Science
2020, 55, 2772–2786.
(26) Guo, H.-L.; Zhu, Q.; Wu, X.-L.; Jiang, Y.-F.; Xie, X.; Xu, A.-W. Oxygen deficient
ZnO 1- x nanosheets with high visible light photocatalytic activity. Nanoscale 2015,
7, 7216–7223.
(27) Frankcombe, T. J.; Liu, Y. Interpretation of oxygen 1s X-ray photoelectron spec-
troscopy of ZnO. Chemistry of Materials 2023, 35, 5468–5474.
(28) Idriss, H. On the wrong assignment of the XPS O1s signal at 531–532 eV attributed to
oxygen vacancies in photo-and electro-catalysts for water splitting and other materials
applications. Surface science 2021, 712, 121894.
(29) Yamamoto, S.; Bluhm, H.; Andersson, K.; Ketteler, G.; Ogasawara, H.; Salmeron, M.;
22
Nilsson, A. In situ x-ray photoelectron spectroscopy studies of water on metals and
oxides at ambient conditions. Journal of Physics: Condensed Matter 2008, 20, 184025.
(30) Silva, A. L. C.; Vargas, L. M. B.; Peres, M. L.; Rodrigues, A. D. G.; Chiquito, A. J.;
Teodoro, M. D.; de Godoy, M. P. Giant photoresponse in p-type sodium-doped ZnO
films. Journal of Alloys and Compounds 2024, 175761.
(31) Wu, R.; Hao, J.; Zheng, S.; Sun, Q.; Wang, T.; Zhang, D.; Zhang, H.; Wang, Y.;
Zhou, X. N dopants triggered new active sites and fast charge transfer in MoS2
nanosheets for full Response-Recovery NO2 detection at room temperature. Applied
Surface Science 2022, 571, 151162.
(32) Joshi, S.; Smieszek, N.; Chakrapani, V. Effects of charge fluctuation and charge reg-
ulation on the phase transitions in stoichiometric VO2. Scientific Reports 2020, 10,
17121.
(33) Rehman, S.; Kim, H.; Farooq Khan, M.; Hur, J.-H.; Lee, A. D.; Kim, D.-k. Tuning of
ionic mobility to improve the resistive switching behavior of Zn-doped CeO2. Scientific
Reports 2019, 9, 19387.
(34) Li, G.-J.; Zhang, X.-H.; Kawi, S. Relationships between sensitivity, catalytic activity,
and surface areas of SnO2 gas sensors. Sensors and Actuators B: Chemical 1999, 60,
64–70.
(35) Wang, C.; Yin, L.; Zhang, L.; Xiang, D.; Gao, R. Metal oxide gas sensors: sensitivity
and influencing factors. sensors 2010, 10, 2088–2106.
(36) Milano, G.; Luebben, M.; Laurenti, M.; Boarino, L.; Ricciardi, C.; Valov, I. Structure-
Dependent Influence of Moisture on Resistive Switching Behavior of ZnO Thin Films.
Advanced Materials Interfaces 2021, 8, 2100915.
23
(37) Messerschmitt, F.; Kubicek, M.; Rupp, J. L. How does moisture affect the physical
property of memristance for anionic–electronic resistive switching memories? Advanced
Functional Materials 2015, 25, 5117–5125.
(38) Gankanda, A.; Cwiertny, D. M.; Grassian, V. H. Role of atmospheric CO2 and H2O
adsorption on ZnO and CuO nanoparticle aging: formation of new surface phases and
the impact on nanoparticle dissolution. The Journal of Physical Chemistry C 2016,
120, 19195–19203.
(39) Kahyarian, A.; Achour, M.; Nesic, S. Mathematical modeling of uniform CO2 corrosion.
Trends in Oil and Gas Corrosion Research and Technologies 2017, 805–849.
(40) Sheridan, P.; Ma, W.; Lu, W. Pattern recognition with memristor networks. 2014 IEEE
International Symposium on circuits and systems (ISCAS). 2014; pp 1078–1081.
24
TOC Graphic
25
