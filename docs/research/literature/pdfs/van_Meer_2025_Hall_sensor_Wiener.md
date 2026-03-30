**Creator**: TeX

---

Max van Meer, Self-Calibrating Position Measurements: Applied to Imperfect Hall Sensors,

Accepted for the joint 10th IFAC Symposium on Mechatronic Systems & 14th IFAC Symposium on Robotics,

Uploaded to ArXiv 8 May 2025

Self-Calibrating Position Measurements:

Applied to Imperfect Hall Sensors 1

Max van Meer ∗Marijn van Noije ∗Koen Tiels ∗Enzo Evers ∗∗

Lennart Blanken ∗,∗∗Gert Witvoet ∗,∗∗∗Tom Oomen ∗,∗∗∗∗

∗Control Systems Technology section, Department of Mechanical

Engineering, Eindhoven University of Technology, The Netherlands

(e-mail: m.v.meer@tue.nl).

∗∗Mechatronics department, Sioux Technologies B.V., Eindhoven, The

Netherlands.

∗∗∗Department of Optomechatronics, TNO, Delft, The Netherlands.

∗∗∗∗Delft Center for Systems and Control, Delft University of

Technology, Delft, The Netherlands.

Abstract: Linear Hall sensors are a cost-effective alternative to optical encoders for measuring

the rotor positions of actuators, with the main challenge being that they exhibit position
dependent inaccuracies resulting from manufacturing tolerances. This paper develops a data
driven calibration procedure for linear analog Hall sensors that enables accurate online estimates

of the rotor angle without requiring expensive external encoders. The approach combines closed
loop data collection with nonlinear identification to obtain an accurate model of the sensor

inaccuracies, which is subsequently used for online compensation. Simulation results show that

when the flux density model structure is known, measurement errors are reduced to the sensor

noise floor, and experiments on an industrial setup demonstrate a factor of 2.6 reduction in the

root-mean-square measurement error. These results confirm that Hall sensor inaccuracies can be

calibrated even when no external encoder is available, improving their practical applicability.

Keywords: Mechatronic Systems, Calibration, Hall Sensors, Nonlinear Identification, Position

Measurements

1. INTRODUCTION

Accurate

position

measurements

are

key

in

high
performance actuators for applications such as semi
conductor manufacturing or optical satellite communica
tion (Mack, 2007; Kramer et al., 2020). These actuators

must meet strict positioning requirements, often in the

micrometer or microradian range, to achieve accurate con
trol performance (Oomen, 2018). Meanwhile, the demand

for mass-produced solutions has created a need for more

economical sensors that still meet these requirements.

Figure 1 depicts a set of Linear Hall sensors on a ro
tor, which offer a promising alternative to costly, high
resolution encoders for electric actuators. A Hall sensor

outputs a voltage proportional to the local magnetic flux

density, which can be processed to estimate the rotor

angle (Ramsden, 2006; Liu et al., 2008). Compared to

high-end encoders, linear Hall sensors are cheaper, more

compact, and easier to integrate in large volumes.

1 This work is part of the research programme VIDI with project

number 15698, which is (partly) financed by the Netherlands Or
ganisation for Scientific Research (NWO). In addition, this research

has received funding from the ECSEL Joint Undertaking under

grant agreement 101007311 (IMOCO4.E). The Joint Undertaking

receives support from the European Union’s Horizon 2020 research

and innovation program.

Hall-based sensing nevertheless suffers from position
dependent inaccuracies due to uneven magnetization,

manufacturing

tolerances,

and

sensor

misalignments.

These imperfections introduce periodic measurement er
rors, which can lead to degraded control performance and

parasitic vibrations (Pan et al., 2015; Xiao et al., 2007),

see Figure 2. Calibration is thus required to eliminate the

resulting ripples in the estimated rotor position.

Existing approaches to sensor calibration use external

sensors or automated test benches to obtain a ground

truth (Dresscher et al., 2019; van Meer et al., 2023),

which effectively corrects measurement errors. Alterna
tively, filter-based methods (Xiao et al., 2007; Jung et al.,

2010) successfully suppress Hall-induced vibrations online

using feedback. Other methods avoid external sensors by

using measurement models (Du et al., 2018; Kim et al.,

2016) or extended Kalman filters (Yong Zhao and West
wick, 2004). Still, these methods have their limitations.

Reliance on external sensors greatly increases the cost

of calibration in a mass-production setting, even with

automated test benches. Moreover, filter-based methods

limit control bandwidth by introducing phase lag. Existing

methods avoiding external position sensors instead rely on

rough position estimates, assume ideal sensor placement or

are too computationally demanding for low-cost hardware.

Although these methods improve measurement accuracy,

no procedure relies solely on analog Hall signals and actua
arXiv:2505.04245v1  [eess.SY]  7 May 2025


!!! page 2 "van_Meer_2025_Hall_sensor_Wiener"

y0

rotor

stator with

Hall sensors

h = 1

h = 2

h = 3

unmodeled manufacturing defects

lead to measurement errors

Fig. 1. Experimental setup: Linear Hall sensors h on the

stator measure flux density dh from rotor-mounted

magnets. Blue and red blocks indicate south and

north poles. The flux density depends on the rotor

position y0, but reconstructing y ≈y0 is complicated

by unmodeled manufacturing defects. Stator windings

are omitted from the scheme for simplicity.

Fig. 2. Illustrative example of a position-dependent mea
surement inaccuracy, plotted along two out of nm

pole-pairs. When the position is reconstructed (

)

from flux density signals while neglecting higher order

harmonics, the estimate of true rotor angle (

) is not

accurate and potentially varies along each pole pair.

tor torque commands while avoiding strict assumptions on

sensor placement. Therefore, this paper aims to calibrate

analog linear Hall sensors through closed-loop experiments

and simulation error minimization. No external angle sen
sor or expensive test setup is needed, making the method

suitable for cost-sensitive, large-scale production.

The main contributions are as follows.

C1 A closed-loop identification and calibration strategy

is developed that relies solely on Hall measurements

and torque commands while capturing higher-order

harmonic distortions in the flux density.

C2 Simulation results show that the method accurately

estimates the rotor angle without external position

information.

C3 Experiments demonstrate improved measurement ac
curacy on an industrial setup.

This paper is structured as follows. Section 2 formalizes the

problem. Section 3 describes the calibration approach. Sec
tions 4 and 5 demonstrate its effectiveness in simulations

and experiments. Finally, Section 6 provides conclusions.

2. PROBLEM DESCRIPTION

This section describes the challenges associated with re
constructing the rotor position of an electric motor using

Hall sensor measurements.

2.1 Experimental setup: Hall sensors on an electric motor

Consider an electric motor with linear time-invariant (LTI)

torque dynamics given by

y0(s) = G(s)T(s),

(1)

where y0 ∈R represents the true rotor position,

T(s) = Tu(s) + Td(s)

(2)

is the applied torque consisting of a control action Tu

and external disturbances Td, and G(s) is a transfer

function with Laplace operator s. The rotor contains nm

pole pairs that generate a position-dependent magnetic

field. Three Hall sensors h ∈{1, 2, 3} are mounted on

the stator, spaced approximately 120◦apart in electrical

angle. Neglecting dependence on temperature, each sensor

measures a voltage dh assumed proportional to the local

magnetic flux density, given by

dh(tk) = gh(y0(tk)) + vh(tk),

(3)

where tk = Tsk with sample time Ts and discrete-time

sample number k. Here, gh(y0) describes the periodic

relationship between rotor position y0 and scaled flux

density with y0 = 0 at t0, and vh(tk) is zero-mean,

independent sensor noise with variance σ2

h. The series

connection of linear system G(s) and nonlinear functions

gh(y0) is recognized as a single-input multi-output Wiener

system in literature (Westwick and Verhaegen, 1996).

2.2 Computing the rotor position from Hall sensor data

Estimates y ≈y0 can be reconstructed from the Hall

sensor measurements dh if the mapping

g(y0) = [g1(y0) g2(y0) g3(y0)]⊤

(4)

has a left inverse. This is the case if and only if g(y0) is

injective, i.e., any unique flux density vector d = g(y0)

must correspond to exactly one rotor position y0. This is

not the case on the whole domain y0 ∈R: not only is g(y0)

periodic with mechanical period 2π, it is also periodic with

period

2π

nm if the pole-pairs are placed axisymmetrically.

This issue is overcome by including prior information

about the specific period that y0(tk) is currently in, e.g.,

by using the previous position estimate

ϕ ≜y(tk−1)

(5)

and assuming a sufficiently small Ts. In this case, g(y0) is

not required to be injective on the whole domain y0 ∈R,

but only in a domain Yϕ smaller than the periodicity of

g(y0), centered around ϕ:

Yϕ =



y0 | ϕ −π

nm

< y0 < ϕ + π

nm



.

(6)

Within this domain, the estimate y of the true position y0

follows from a function fϕ satisfying

fϕ(g(y0)) = y0,

∀y0 ∈Yϕ.

(7)

Thus, ϕ ≜y(tk−1) in (7) acts as a history-capturing

variable that enables reconstruction of the mechanical

rotor position y0 despite periodic flux densities.

Since g(y0) is unknown, (7) cannot be used for designing

the left inverse fϕ. Instead, fϕ is designed using a model

ˆg(y0) ≈g(y0) to satisfy the condition

fϕ(ˆg(y0)) = y0,

∀y0 ∈Yϕ,

(8)

where model mismatch would lead to estimation error

y0 −fϕ(ˆg(y0)). The next section addresses the importance

of accurately modeling ˆg(y0) ≈g(y0).


!!! page 3 "van_Meer_2025_Hall_sensor_Wiener"

Algorithm 1 Data-driven calibration of Hall sensors

Require: Controller C(s), BLA ˆGBLA(q), reference r(tk).

1: Track r(tk) in closed-loop using fϕ = f init

ϕ

in (9), store

d(tk) and y(tk) in D.

(Section 3.1)

2: Set ˆGBLA(q) ←ˆGBLA(q)/ˆc with (23).

(Section 3.3)

3: Solve (14) to obtain ˆgθ⋆.

(Section 3.1)

4: Create f ⋆

ϕ using (20).

(Section 3.2)

5: return Reconstruction function f ⋆

ϕ.

zoh

C(q)

e

G(s)

linear feedback

g(y0)

nonlinear plant

y0

ˆy0

output linearization

Td

fytk−1(d)

q−1

r

v

d

−

T

Tu

Fig. 3. Closed-loop data collection scheme. Rotor position

estimates y ≈y0 are reconstructed from flux density

signals d and are used for position feedback con
trol, suppressing external disturbances Td. Solid and

dashed lines represent continuous-time and discrete
time signals, respectively.

2.3 Consequences of incorrect reconstruction

Imperfect modeling of g(y0) leads to periodic errors in the

reconstructed rotor position y, resulting in ripples that

degrade tracking performance and cause vibrations. As
suming Hall signals are purely sinusoidal is inadequate due

to manufacturing tolerances, uneven magnetization, and

misaligned sensors. These imperfections introduce higher
order harmonics and cause measurement inaccuracy when

left unaddressed; see Figure 2. This shows the need for a

model ˆg(y0) to accurately capture flux density behavior.

2.4 Problem definition

The aim is to obtain accurate rotor position estimates

y ≈y0 from Hall sensor measurements d. No external

position sensors are available for calibration except for

validation purposes, and the solution must be robust

to external disturbances and implementable on low-cost

embedded hardware. This involves two main tasks:

(1) Identify an accurate flux density model ˆg(y0) based

on the measurements d and applied torque T.

(2) Design an fϕ satisfying (8).

3. SELF-CALIBRATING HALL SENSORS

This section describes the developed calibration approach

for Hall-based rotor position estimation. Section 3.1

presents flux density modeling, experiment design, and

identification. Section 3.2 details the reconstruction func
tion, and Section 3.3 covers implementation. Algorithm 1

summarizes the procedure.

3.1 Modeling the flux density function g

The first step involves identifying an accurate model ˆg(y0)

of the flux density function g(y0) from measured data.

The modeling process consists of three key steps: experi
ment design, model structure definition, and identification.

These steps are described below.

Experiment design

Data is collected in closed-loop, using

a feedback controller C(s) for safety and for mitigation

of disturbances Td. During data collection, an initial re
construction function f init

ϕ

estimates the rotor position to

facilitate linear position feedback. This function combines

a Clarke transformation and the atan2 function to approx
imate the rotor position based on the Hall sensor measure
ments d = [d1, d2, d3]⊤(Hussain and Toliyat, 2016):

y(tk) = f init

ytk−1(d(tk))

f init

ytk−1(d(tk)) :=

1

nm



Γ



atan2



˜d2(tk), ˜d1(tk)



, ytk−1



,

(9)

with Γ : R × R →R an unwrapping function given by

Γ(ytk, ytk−1) := ytk−1 + mod

 ytk −ytk−1 + π, 2π



−π,

(10)

and ˜d = Cd with C the Clarke transformation matrix:

C = 2

3





1 −1

2

−1

2

0

√

3

2

−

√

3

2

1

2

1

2

1

2





.

(11)

This initial f init

ϕ

satisfies (7) if g(y0) consists solely of

three pure sinusoids shifted by 120◦, without higher-order

harmonics. In practice, however, sensor misalignments and

uneven magnetization give rise to harmonic distortions

that make (9) only an approximation y(tk) ≈y0(tk).

Despite these inaccuracies, the approximate reconstruc
tion is sufficient to enable closed-loop control, as shown

in Figure 3. The feedback controller C suppresses external

disturbances Td and ensures that the approximated rotor

position tracks a ramp reference. Perfect reference tracking

is not achieved because of the higher harmonics in g,

but this is not required for identification; the feedback

controller need only suppress Td in T. Section 3.3 addresses

the reference and controller design. During experiments,

the N samples of d(tk) and y(tk) are stored in the dataset

D for use in identification.

Model structure

The flux density function g(y0) is

parametrized linear in the parameters for simplicity:

ˆg⊤

θ (y0) = ψ(y0)θ,

(12)

where θ ∈Rnθ are model parameters, and

ψ(y0) = I3 ⊗β(y0),

(13)

with ⊗the Kronecker product and β : R →R1×m

a periodic basis function, such as a Fourier basis or a

periodic kernel function (Rasmussen and Williams, 2006).

The order m can be chosen by analyzing the harmonic

content of data d(tk).

Identification

The parameters θ are identified by solving

a simulation error minimization (SEM) problem. The cost

function J(θ) is defined as the squared 2-norm of the

difference between the measured flux density d ∈D and a

simulated flux density dsim

θ

:

min

θ

J(θ),

J(θ) =

N

X

k=1

 d(tk) −dsim

θ

(tk)

⊤ d(tk) −dsim

θ

(tk)



.

(14)


!!! page 4 "van_Meer_2025_Hall_sensor_Wiener"

Here, dsim

θ

(tk) is computed using the state and output

equations of the closed-loop system, incorporating a Best

Linear Approximation (BLA) ˆGBLA(q) ≈G(q), detailed

in Section 3.3, and the model ˆgθ(y0). These equations are:

dsim

θ

(tk) = ˆgθ(ysim

0

(tk)),

ysim

0,θ (tk) = CGBLAxGBLA,θ(tk),

xGBLA,θ(tk+1) = AGBLAxGBLA,θ(tk) + BGBLA,θT sim

θ

(tk),

T sim

θ

(tk) = CCxC,θ(tk) + DCesim

θ

(tk),

xC,θ(tk+1) = ACxC,θ(tk) + BCesim

θ

(tk),

(15)

esim

θ

(tk) = r(tk) −ysim

θ

(tk),

ysim

θ

(tk) = f init

ysim

θ

(tk−1)(dsim

θ

(tk)),

∀k ∈{1, . . . , N}

with zero initial conditions. Here, AGBLA, BGBLA, and

CGBLA represent the state and output matrices of the

BLA, while AC, BC, CC, and DC describe the discrete
time controller. Problem (14) is solved using an interior
point method with approximate gradients, starting at

an initial estimate θ0 corresponding to pure sinusoids,

i.e., the inverse of f init. Since the cost is non-convex, θ⋆

corresponds to a local minimum.

3.2 Designing a reconstruction function f ⋆

ϕ

With the flux density model ˆg(y0) available, a reconstruc
tion function f ⋆

ϕ is designed to estimate the rotor position

while compensating for inaccuracies in the initial recon
struction function f init

ϕ

. First, a lookup table is defined

on a grid of M equidistant points y0,i within the interval

[0, 2π). Using the model ˆg(y0), the corresponding outputs

of the initial reconstruction function f init

ϕ

are computed:

ˆyi = f init

y0,i(ˆgθ(y0,i)),

i ∈{1, . . . , M}.

(16)

The additive measurement error caused by f init

ϕ

on this

grid is then estimated as

ˆηLUT

i

:= y0,i −ˆyi,

i ∈{1, . . . , M}.

(17)

Next, a piecewise-linear correction function ˆηLUT(ˆy) is

defined to interpolate between the points (ˆyi, ηLUT

i

). For a

given ˆy, the index i is determined such that:

i = argmini {ˆy ∈[ˆyi, ˆyi+1)} ,

(18)

where the interpolation wraps around at the boundaries,

i.e., ˆyM+1 = ˆy1 and ηLUT

M+1 = ηLUT

1

. The piecewise-linear

interpolation is then computed as:

ηLUT(ˆy) = ˆηLUT

i

+

ˆy −ˆyi

ˆyi+1 −ˆyi

 ˆηLUT

i+1 −ˆηLUT

i



.

(19)

Finally, the reconstruction function f ⋆

ϕ is defined to com
pensate for the additive measurement error, yielding:

f ⋆

ϕ(d) = f init

ϕ

(d) + ηLUT  f init

ϕ

(d)



.

(20)

This adjustment corrects the periodic inaccuracies in f init

ϕ

in a computationally lightweight manner, improving the

accuracy of rotor position estimation. Note that this

simple approach requires (16) to be bijective. If it is

not, a different approach to designing f ⋆

ϕ is required that

avoids f init

ϕ

altogether. The next section discusses relevant

implementation aspects.

3.3 Implementation aspects

Several practical considerations are important for imple
menting the developed method, as detailed next.

Control and reference design

The closed-loop data col
lection in Section 3.1.1 uses a feedback controller C(s)

to suppress external disturbances Td on total torque T.

To mitigate these disturbances, the sensitivity (Franklin

et al., 1994) must be low in magnitude. With the nonlinear

function g approximately linearized by f init

ϕ

in Figure 3,

the sensitivity is given by

S(s) = T(s)

Td(s) ≈

1

1 + G(s) C(s).

(21)

Including an integrator in C(s) ensures that the sensitivity

is low in magnitude at low frequencies and effectively sup
presses slowly varying disturbances. A slow ramp reference

from 0 to 2πn rad with n ∈R≥1 places any position
dependent disturbances in this low-frequency range where

they are well attenuated.

Obtaining a Best Linear Approximation

The BLA

ˆGBLA(q) required for Step 3 in Algorithm 1 is identified up

to an unknown constant in closed-loop using the approach

described in Pintelon and Schoukens (2012, Section 3.8),

averaging over multiple realizations of random-phase mul
tisine reference signals. This yields

ˆGBLA(q) = cG(q),

(22)

with c ∈R. To correct for this mismatch, ˆc ≈c is estimated

from data D by minimizing

ˆc = arg min

c

 ysim

θ0,c(tpsim) −ydat(tpdat)

2 ,

(23)

where ysim

θ0,c(tpsim) follows from (15) using a scaled BLA

˜BGBLA = cBGBLA, and ydat ∈D. Moreover, tp is the time

instance of the last full rotation:

pι := arg max

pι {yι(tpι) = 2πn | n ∈N, tpι ≤tN} ,

(24)

for both ι ∈{sim, dat}. The estimate ˆc ≈c in (23) relies

on g(y0) being periodic with known period 2π. Indeed,

the number of full rotations of the rotor is independent

of the shape of the measurement errors, so any mismatch

between simulation (15) and the data must be attributed

to incorrect scaling of the BLA. Once ˆc ≈c is estimated, it

is used to compensate the BLA in Step 2 of Algorithm 1,

before the nonlinear identification step.

4. SIMULATION RESULTS

This section demonstrates the performance of the devel
oped calibration approach on a simulation example.

4.1 Simulation setup

Consider an example motor with nm = 11 permanent

magnets and linear dynamics

G(s) := y0(s)

T(s) =

1.663 · 105

s3 + 632.6 s2 + 2702 s exp

 1.2 · 10−4s



.

(25)

Moreover, g(y0) is parametrized by a Fourier basis β(y0) ∈

R1×(2nh+1). The first element is β1(y0) = 1, and

β1+i(y0) = sin

 y0 h⌈i/2⌉



,

β2+i(y0) = cos

 y0 h⌈i/2⌉



,

∀i ∈{ i ∈N | i odd, 1 ≤i ≤2nh −1},

(26)

with harmonics h = [ 1, . . . , 11 ]⊤. A parameter vector θ

is chosen so that each permanent magnet has a slightly


!!! page 5 "van_Meer_2025_Hall_sensor_Wiener"

0

2

1.5

1.75

2

2.25

2.5

2.75

3

3.25

3.5

Fig. 4. Simulation example. The first Hall signal d1(tk)

(

) is approximately periodic with the magnet pitch,

with slight variations across magnets. The estimates

ˆd1 = ˆg1,θ⋆(d(tk)) (

) from the model in Step 3 of

Algorithm 1 closely match the true function.

different flux density profile, as Figure 4 shows it is not

quite periodic with period 2π/nm. The flux density signals

are sampled at Fs = 4000 Hz, each with noise variance

σ2

h = 7.5 · 10−6 V. A stabilizing controller is given by

C(q) =

2.94q3 −3.29q2 −2.10q + 2.45

q4 −3.45q3 + 4.52q2 −2.68q + 0.61

(27)

and is used in the control scheme in Figure 3.

4.2 Approach

First, a BLA ˆGBLA(s) is measured in closed-loop follow
ing the procedure in Section 3.3.2. Algorithm 1 is then

applied with model structure (26). During data collection,

a reference r(tk) increases linearly from 0 to 13 rad in 26 s.

Problem (14) is solved in two hours on a standard desktop

computer, and (16) is verified to be bijective.

4.3 Results

Figure 4 illustrates one of the simulated flux density

signals d1(tk), together with the estimates

ˆd1(tk)

=

ˆg1,θ⋆(ysim

0

(tk)). The model ˆgθ⋆accurately captures the

slight flux density variations across the magnets. Figure 5

depicts the estimation error in the rotor angle when using

the initial reconstruction f init

ϕ

versus the final reconstruc
tion f ⋆

ϕ. The initial reconstruction exhibits a clear periodic

error due to unmodeled higher-order harmonics. The final

reconstruction f ⋆

ϕ corrects these structural errors and re
duces the error to the sensor noise level. Note that the true

rotor position y0 is only used here for validation; it is not

part of the calibration procedure.

These results show that the developed method accurately

calibrates Hall sensors without relying on an external

reference encoder. As shown next, measurement accuracy

is also improved on an industrial setup.

5. EXPERIMENTAL RESULTS

This section validates the approach experimentally.

5.1 Experimental setup

A confidential setup from Sioux Technologies B.V. with

a Brushless Direct Current (BLDC) motor is used for

experimental validation. The setup follows Figure 1, with

a rotor of nm = 11 pole pairs and an external encoder for

0

2

-20

-15

-10

-5

0

5

10

15

10-3

Fig. 5. Measurement error in the simulation. Using the

initial f init

ϕ

(d) results in a large measurement error

(

). Using f ⋆

ϕ(d) from Algorithm 1 reduces the mea
surement error down to the noise floor (

).

0

2

1

2

3

4

Fig. 6. Experimental data. The measured Hall signal

d1(tk) (

) repeats roughly with each magnet but

shows slight variations. The identified model ˆd1(tk) =

ˆg1,θ⋆(ysim

0

(tk)) (

) accurately estimates the flux den
sities without relying on y0(tk).

0

2

-0.02

-0.01

0

0.01

0.02

Fig. 7. Measurement error in the experiments, with the

external encoder used for validation only. The ini
tial f init

ϕ

(d) produces a large error (

). After Algo
rithm 1, f ⋆

ϕ(d) achieves a significant reduction (

).

validation only. Three Hall sensors, spaced approximately

120 electrical degrees apart, are sampled at Fs = 4000 Hz.

The same feedback controller as in (27) is used.

5.2 Approach

As before, a BLA ˆGBLA(s) is identified using the closed
loop approach in Section 3.3.2. The flux density model

ˆgθ is then expressed through a kernel-based basis function

β(y0) : R →R1×m, where m = 400. A grid of m points y0,j

is defined equidistantly in [ 0, 2π). The kernel is defined by

βj(y0) = k(y0, y0,j),

k(y, y′) = σ2

f exp



−1

2ℓ2 ∥x −x′∥2

,

(28)


!!! page 6 "van_Meer_2025_Hall_sensor_Wiener"

100

11

102

0

1

2

3

4

10-5

Fig. 8. Cumulative power spectral density of the mea
surement error. The initial f init

ϕ

(d) (

) shows clear

periodic content with the spatial frequency nm = 11

corresponding to the magnet count. The final f ⋆

ϕ(d)

(

) corrects for these errors.

where x = [sin(y), cos(y)]⊤. Hyperparameters σf and ℓ

are selected by including them as design variables in (14).

The reference r(tk) is a ramp from 0 to 20 rad over 40 s.

Problem (14) is solved in ten hours on a standard desktop

computer, and (16) is verified to be bijective.

5.3 Results

Figure 6 shows an example of the measured Hall signal

d1(tk) and its estimate ˆd1(tk) = ˆg1,θ⋆(ysim

0

(tk)), where

the identified model captures magnet variations. Figure 7

presents the measurement error using the external encoder

for validation. The initial reconstruction f init

ϕ

results in

an RMS error of 5.7 mrad, while the final reconstruction

f ⋆

ϕ compensates for higher-order harmonics, reducing it to

2.2 mrad. The peak ∥η∥∞is reduced by a factor of 2.5.

Figure 8 shows the cumulative power spectral density of

the measurement error. Much of the frequency content

aligns with the magnet pitch, which the corrected recon
struction significantly suppresses. These results confirm

that the calibration method improves rotor position es
timation on an industrial setup, achieving a factor of 2.6

improvement in RMS accuracy and a factor of 2.5 in peak

error without requiring an external reference encoder.

5.4 Discussion

The residual errors in Figure 7 are presumably caused by

nonlinear dynamics that are periodic in y0 with period 2π,

such as cogging, affecting d and indistinguishable from the

contribution of g. A potential solution might be to repeat

the data collection process for different angular placements

of the motor coils, averaging out this effect. This would

require a modular design and involves further research.

Furthermore, the developed two-step approach could po
tentially be simplified to directly construct fϕ from data,

avoiding modeling the of g. The current two-step approach

is motivated by the expectation that nonlinear identifica
tion through simulation-error minimization is more robust

to measurement noise on d, yet a more thorough analysis

for this choice is desirable.

6. CONCLUSION

The developed method improves measurement accuracy

of Hall sensors without using external encoders, improv
ing positioning performance and reducing vibrations cost
effectively for mass production. The simulation error min
imization accurately estimates flux density functions, and

the resulting compensation function reduces measurement

error by a factor of 2.6 on an industrial setup. These

findings eliminate the need for expensive test benches

and enable low-cost position measurements. Future work

will focus on reducing offline computation time through

multiple shooting and lower-dimensional model structures,

and an extension to Hammerstein systems.

ACKNOWLEDGEMENTS

The authors thank Sioux Technologies B.V. for the devel
opments that led to these results and for their support in

carrying out the experiments reported in this paper.

REFERENCES

Dresscher, M., Human, J.D., Witvoet, G., et al. (2019).

Key

Challenges and Results in the Design of Cubesat Laser Terminals,

Optical Heads and Coarse Pointing Assemblies.

In 2019 IEEE

ICSOS, 1–6.

Du, S., Hu, J., Zhu, Y., and Zhang, M. (2018). A Hall sensor-based

position measurement with on-line model parameters computation

for permanent magnet synchronous linear motor. IEEE Sen. J.,

18(13), 5245–5255.

Franklin, G., Powell, J.D., and Emami-Naeini, A. (1994). Feedback

Control Of Dynamic Systems.

Hussain, H.A. and Toliyat, H.A. (2016). Field Oriented Control of

tubular PM Linear Motor using linear Hall Effect sensors.

In

SPEEDAM 2016, 1, 1244–1248.

Jung, S., Lee, B., and Nam, K. (2010). PMSM control based on edge

field measurements by Hall sensors. In 2010 APEC, 2002–2006.

Kim, J., Choi, S., Cho, K., and Nam, K. (2016). Position Estimation

Using Linear Hall Sensors for Permanent Magnet Linear Motor

Systems. IEEE Trans. Ind. Elec., 63(12), 7644–7652.

Kramer, L., Peters, J., Voorhoeve, R., et al. (2020). Novel motoriza
tion axis for a Coarse Pointing Assembly in Optical Communica
tion Systems. In IFAC 2020 World Congr., volume 53, 8426–8431.

Liu, X., Zheng, Z., Ye, Y., and Lu, Q. (2008). Position detecting for

the air-cored TPMLSM with linear Hall-effect sensors. In ICEMS

2008, 1417–1420.

Mack, C. (2007).

Fundamental Principles of Optical Lithography.

Wiley.

Oomen, T. (2018). Advanced motion control for precision mecha
tronics: Control, identification, and learning of complex systems.

IEEJ J. Ind. Appl., 7(2), 127–140.

Pan, S., Commins, P.A., and Du, H. (2015). Tubular linear motor

position detection by Hall-effect sensors. In AUPEC 2015, 1–5.

Pintelon, R. and Schoukens, J. (2012).

System Identification: A

Frequency Domain Approach. Wiley, 2nd edition.

Ramsden, E. (2006). Hall-Effect Sensors. Elsevier, Burlington, 2nd

edition.

Rasmussen, C. and Williams, C. (2006).

Gaussian processes for

machine learning. London, England.

van Meer, M., Deniz, E., Witvoet, G., and Oomen, T. (2023). Cas
caded Calibration of Mechatronic Systems via Bayesian Inference.

In The 22nd World Congress of the International Federation of

Automatic Control, 3405–3410. Yokohama, Japan.

Westwick, D. and Verhaegen, M. (1996). Identifying MIMO Wiener

systems using subspace model identification methods. Sig. Proc.,

52(2), 235–258.

Xiao, L., Yunyue, Y., and Zhuo, Z. (2007). Study of the Linear Hall
Effect Sensors Mounting Position for PMLSM. In 2007 ICIEA,

1175–1178.

Yong Zhao and Westwick, D. (2004). A direct approach to identify

closed loop Wiener systems, whose linear dynamics are open-loop

unstable. In ACC 2004, 1, 4782–4787.

