# Literature Search: Neural Network Architecture Efficiency for Time Series

**Date**: 2026-03-28
**Search Focus**: Computational efficiency comparison of RNN vs CNN architectures for time series processing
**Databases Searched**: arXiv, IEEE Xplore (via web search), Google Scholar (via web search)

---

## Search Scope and Methodology

### Keywords Used
- RNN vs CNN
- LSTM efficiency
- 1D-CNN computational cost
- neural network parameter count
- FLOPs comparison
- convolutional vs recurrent networks
- temporal convolutional networks
- sequence modeling efficiency

### Databases Searched
1. arXiv (primary source)
2. IEEE Xplore (indirect via web search)
3. Google Scholar (indirect via web search)

---

## 1. Key Papers Found and Verified

### Paper 1: Comparative Study of CNN and RNN for Natural Language Processing
- **Authors**: Wenpeng Yin, Katharina Kann, Mo Yu, Hinrich Schutze
- **Year**: 2017
- **arXiv ID**: 1702.01923
- **URL**: https://arxiv.org/abs/1702.01923
- **Key Finding**: First systematic comparison of CNN and RNN on NLP tasks. CNN good at position-invariant features, RNN at sequential modeling.
- **Efficiency Focus**: Architecture comparison across NLP tasks
- **Status**: VERIFIED

### Paper 2: Deep Filtering with DNN, CNN and RNN
- **Authors**: Bin Xie, Qing Zhang
- **Year**: 2021
- **arXiv ID**: 2112.12616
- **URL**: https://arxiv.org/abs/2112.12616
- **Key Finding**: CNN outperforms DNN/RNN for filtering. RNN not suitable for filtering problems.
- **Efficiency Focus**: Comparative evaluation on filtering tasks
- **Status**: VERIFIED

### Paper 3: Stable Recurrent Models
- **Authors**: John Miller, Moritz Hardt
- **Year**: 2018
- **arXiv ID**: 1805.10369
- **URL**: https://arxiv.org/abs/1805.10369
- **Key Finding**: Stable RNNs well-approximated by feed-forward networks. Perform as well as unstable counterparts.
- **Efficiency Focus**: Stability vs computational complexity
- **Status**: VERIFIED

### Paper 4: Blending LSTMs into CNNs
- **Authors**: Krzysztof J. Geras et al.
- **Year**: 2015
- **arXiv ID**: 1511.06433
- **URL**: https://arxiv.org/abs/1511.06433
- **Key Finding**: Deep CNNs can match/exceed LSTM accuracy on speech recognition with model blending.
- **Efficiency Focus**: CNN vs LSTM, model compression
- **Status**: VERIFIED

### Paper 5: TCN - An Empirical Evaluation of Generic Convolutional and Recurrent Networks
- **Authors**: Shaojie Bai, J. Zico Kolter, Vladlen Koltun
- **Year**: 2018
- **arXiv ID**: 1803.01271
- **URL**: https://arxiv.org/abs/1803.01271
- **Key Finding**: Simple convolutional architectures outperform LSTMs across diverse tasks with longer memory.
- **Efficiency Focus**: Systematic comparison across benchmarks
- **Status**: VERIFIED

### Paper 6: Recurrent Additive Networks
- **Authors**: Kenton Lee, Omer Levy, Luke Zettlemoyer
- **Year**: 2017
- **arXiv ID**: 1705.07393
- **URL**: https://arxiv.org/abs/1705.07393
- **Key Finding**: RANs with additive updates perform on par with LSTMs with simpler computation.
- **Efficiency Focus**: Simplified RNN matching LSTM performance
- **Status**: VERIFIED

---

## 2. Additional Related Papers Identified

### Paper 7: On the Parameter Efficiency of LSTMs
- **Status**: PENDING - Need to verify exact paper ID
- **Focus**: Parameter count comparison between LSTM variants

### Paper 8: Efficient Convolutional Neural Networks for Time Series
- **Status**: PENDING - Search revealed papers on lightweight/efficient CNNs
- **Focus**: Efficient 1D-CNN architectures

### Paper 9: GRU vs LSTM vs RNN Parameter Efficiency
- **Status**: PENDING - Papers comparing gated recurrent unit parameter counts
- **Focus**: Parameter count comparisons

---

## 3. Key Findings Summary

### Parameter Count Comparisons

| Architecture | Typical Parameter Count | Relative Efficiency |
| LSTM | High (4x hidden size for gates) | Baseline |
| GRU | Lower than LSTM (3x hidden) | 30-40% fewer params |
| 1D-CNN | Varies with kernel size, channels | Weight sharing benefit |
| TCN | Depends on depth, dilation | Competitive |

### Computational Cost (FLOPs) Insights

1. RNNs (LSTM/GRU): O(n) per timestep, sequential computation
2. 1D-CNN: O(n) per layer but parallelizable, long receptive field with dilation
3. TCN: Parallel computation, efficient for long sequences
4. Feed-forward approximation: Can reduce compute with minimal accuracy loss

### Key Conclusions from Literature

1. CNN advantages: Parallelizable, longer memory, often better accuracy
2. RNN advantages: Natural for variable-length sequences, fewer parameters for certain tasks
3. TCN (Bai et al.): CNNs outperform LSTMs across diverse tasks
4. Filtering (Xie and Zhang): CNN outperforms RNN; RNN not suitable for filtering
5. Model compression (Geras et al.): CNNs with LSTM guidance achieve high accuracy

---

## 4. Pending Verification Items

1. Exact parameter count ratios: Extract from papers
2. FLOPs measurements: Specific comparisons
3. Time series specific studies: Not just NLP/speech
4. Hardware efficiency: GPU vs CPU comparisons

---

## References (Verified Papers)

1. Yin, W., Kann, K., Yu, M., and Schutze, H. (2017). Comparative Study of CNN and RNN for NLP. arXiv:1702.01923
2. Xie, B., and Zhang, Q. (2021). Deep Filtering with DNN, CNN and RNN. arXiv:2112.12616
3. Miller, J., and Hardt, M. (2018). Stable Recurrent Models. arXiv:1805.10369
4. Geras, K.J., et al. (2015). Blending LSTMs into CNNs. arXiv:1511.06433
5. Bai, S., Kolter, J.Z., and Koltun, V. (2018). An Empirical Evaluation of TCN. arXiv:1803.01271
6. Lee, K., Levy, O., and Zettlemoyer, L. (2017). Recurrent Additive Networks. arXiv:1705.07393

---

*Report generated: 2026-03-28*
