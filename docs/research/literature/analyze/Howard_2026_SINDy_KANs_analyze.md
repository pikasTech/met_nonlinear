# Howard_2026_SINDy_KANs_analyze.md

## 1. Basic Information

| Field | Value |
|-------|-------|
| Title | SINDy-KANs: Sparse Identification of Nonlinear Dynamics through Kolmogorov-Arnold Networks |
| Authors | Amanda A. Howard, Nicholas Zolman, Bruno Jacob, Steven L. Brunton, Panos Stinis |
| Date | 2026 (preprint) |
| Venue | arXiv preprint |
| Priority | Medium |
| Keywords | KAN, SINDy, symbolic regression, interpretability, dynamical systems |

## 2. Core Content Summary

### Problem Statement
KANs learn activation functions that are not necessarily interpretable or sparse. Existing symbolic regression approaches with KANs are limited because learned activation functions don't align with candidate function libraries. This paper combines SINDy (Sparse Identification of Nonlinear Dynamics) with KANs to achieve sparse, interpretable equation discovery.

### Methodology
**SINDy-KANs**: Simultaneously trains a KAN and a SINDy-like representation by applying sparse regression at each KAN activation function level. Each activation function φ_ℓ,j,i is represented as a sparse combination of candidate functions from a library Θ.

Key innovation: Rather than post-hoc symbolic regression, SINDy-KANs enforce that activation functions decompose into sparse symbolic components **during training**.

### Architecture
- Multiplication-enabled KANs (MultKAN-like nodes) for handling products
- Shadow matrix Λ for L1 sparsity regularization
- Loss function combines KAN loss + SINDy reconstruction loss + sparsity penalty

### Applications
1. Symbolic regression: f(x,y) = cos(x² + y) - correctly learns composition
2. Linear ODE system: 3D system with rotation matrix
3. Damped pendulum: nonlinear dynamics discovery
4. ABC flow: learns frequencies without pre-specification

## 3. GAP Association Analysis

### GAP6 (Interpretability enhancement) - Medium Support
**Critical Support**: The paper directly addresses KAN interpretability through sparse symbolic decomposition.

Lines 83-86: "SINDy-KANs...increase interpretability of KAN representations with SINDy applied at the level of each activation function"

Lines 103-105: "we aim to make symbolic regression performed with KANs more interpretable by directly learning compositions of sparse equation representations through a SINDy-like approach"

**Critical Original Text** (Lines 99-100):
"Many papers discussing interpretability of KANs...do not connect them to a learned equation"

### GAP7 (Novel architectures/training methods) - Medium Support
**Critical Support**: Introduces novel combination of SINDy with KANs.

Lines 107-113: Discusses combining SINDy with deep KANs - "SINDy-KANs can be thought of as a deep version of ADAM-SINDy"

### GAP9 (Computational efficiency) - Weak/Minimal
No significant claims about computational efficiency or FLOPs reduction.

### GAP8 (Frequency domain operations) - No Support
No frequency domain analysis or operations.

## 4. Key Original Text Excerpts

### On interpretability limitation of standard KANs
> "In [1], the activation functions are identified by comparing with a library of candidate functions. As noted in [29], the learned activation functions will not necessarily align with the candidate functions, even if it is known that the candidate functions can be composed to output the target function." (Lines 103-104)

### On SINDy-KAN methodology
> "SINDy-KANs train a standard KAN and simultaneously find the coefficients ξ_ℓ,j,i by solving Eq. 13 for each activation function using sparse regression. In other words, SINDy-KANs learn the sparse representation and the KAN representation simultaneously." (Line 325)

### On learned sparsity
> "The coefficients Ξ_S should be sparse, so ||Ξ_S||_1 is minimized." (Line 297)

### On comparison with pykan
> "pykan struggles to learn the composition of functions...pykan misses the x² term, resulting in larger errors overall." (Lines 379-389)

## 5. GAP6 Evidence Strength Assessment

| Aspect | Strength | Evidence |
|--------|----------|----------|
| Interpretability improvement | **Medium-Strong** | Directly addresses interpretability through SINDy decomposition |
| Sparse representation | **Strong** | L1 regularization on activation coefficients |
| Symbolic regression | **Medium** | Better than pykan for composition, but limited to small networks |
| Comparison with standard KAN | **Medium** | Shows clear improvement in interpretability |

## 6. Relevance to MET Nonlinear Research

**Medium Relevance**: While this paper addresses KAN interpretability which aligns with GAP6, it focuses on dynamical systems and symbolic regression rather than frequency response compensation. The sparse representation approach could potentially inform interpretability strategies for frequency domain operations.

## 7. Priority Justification

Medium priority because:
1. Directly addresses GAP6 (interpretability) which is relevant to understanding what KAN layers learn
2. Novel architecture combining SINDy with deep KANs (supports GAP7)
3. No frequency domain content (not relevant to GAP8)
4. No computational efficiency claims (not relevant to GAP9)

## 8. Citation for Index

```markdown
- **Howard_2026_SINDy_KANs** - [Link](../markdown/Howard_2026_SINDy_KANs.md)
  - GAP6: Medium (interpretability via sparse symbolic decomposition)
  - GAP7: Medium (SINDy-KAN architecture)
  - Key: Addresses activation function alignment problem; learns sparse coefficients
```
