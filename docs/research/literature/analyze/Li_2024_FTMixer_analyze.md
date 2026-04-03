# Li_2024_FTMixer 分析报告

## 论文基本信息

- **标题**: FTMixer: Frequency and Time Domain Representations Fusion for Time Series Forecasting
- **作者**: Zhengnan Li, Yunxiao Qin, Xilong Cheng, Yuting Tan
- **机构**: 中国传媒大学 (Communication University of China)
- **发表时间**: 2024年
- **会议/期刊**: ACM conference (待确认)

## 论文核心内容摘要

FTMixer提出一种结合时域和频域表示的时间序列预测方法。核心贡献：
1. **DCT替代DFT**: 使用离散余弦变换(DCT)替代复数傅里叶变换(DFT)，便于深度学习处理
2. **FCC模块**: 频域通道卷积，捕获全局序列间依赖性
3. **WFTC模块**: 加窗频时卷积，捕获局部依赖性
4. **双域损失函数(DDLF)**: 时域MSE + 频域MAE

## 与GAP10的关联分析

### 批判性支持

**GAP10**: AFMAE vs 纯MAE 改进支撑

该论文证明了频域MAE损失相对于纯时域损失的优势：

- **Line 447**: 消融实验证明频域损失的有效性
  > "For ETTh1, which features complex seasonal patterns and long-term trends [40, 45], excluding the frequency domain loss component, results in an increased MSE from 0.402 to 0.419."

- **Line 341**: 频域采用MAE的原因
  > "In the frequency domain, we employ Mean Absolute Error (MAE), following [38], due to its effectiveness in handling varying magnitudes of frequency components and its stability compared to squared loss functions."

这支撑了AFMAE相对于纯MAE的改进思路：频域MAE能够捕获纯时域MAE无法捕获的周期性特征。

### 直接支持

- **Line 346**: 提出DDLF双域损失函数，在时域和频域分别计算损失
  公式7：
  ```
  L_time = MSE(Y - F(X))
  L_fre = MAE(DCT(Y) - DCT(F(X)))
  L_total = L_time + L_fre
  ```

## 与GAP11的关联分析

### 批判性支持

**GAP11**: AFMAE vs 其他频率相关损失函数效率

FTMixer使用DCT-MAE而非FFT-MAE，证明了不同频域损失函数的选择影响效率。

- **Line 123**: DCT优势
  > "Unlike the Discrete Fourier Transform (DFT), which involves complex numbers, the DCT operates exclusively on real numbers, making it more compatible with modern deep learning techniques."

- **Line 171**: DCT简化频域损失计算
  > "Furthermore, DCT utilizes only amplitude to represent the frequency domain information, simplifying the computation of the loss function in the frequency domain."

- **Line 455**: DCT vs DFT性能比较
  > "As shown in Table 5, the DCT version of the model consistently outperforms the DFT version."

这支撑了AFMAE（直接计算能量，无需FFT）的效率优势：DCT比DFT更简单高效。

### 直接支持

- **Line 341**: 频域MAE的稳定性
  > "due to its effectiveness in handling varying magnitudes of frequency components and its stability compared to squared loss functions."

## 结论

| GAP | 支撑类型 | 强度 | 说明 |
|------|----------|------|------|
| GAP10 | 方法论支撑 | 中 | 频域损失有效性间接证据 |
| GAP11 | 方法论支撑 | 中-弱 | DCT vs FFT效率 |

**关键引用**:
- Line 346-347: DDLF公式 (公式7)
- Line 447: 频域损失有效性消融实验
- Line 123, 171: DCT简化计算的优势
