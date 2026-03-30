# 调研报告：STEP1 Round120 文献补充调研

## 基本信息
- 日期：2026-03-30
- 阶段：STEP1 调研（第120轮）
- 覆盖范围：Wiener-KAN模型、频域损失函数、传感器漂移补偿最新文献
- 是否使用子代理：是（多轮子代理验证）

## 检索路径

### 关键词
- Wiener system identification neural network 2025
- KAN sensor time series 2025
- frequency domain loss time series 2025
- Wiener Hammerstein neural network identification

### 主要数据库
- arXiv
- Google Scholar
- IEEE Xplore
- ScienceDirect

### 检索式
- `site:arxiv.org Wiener KAN 2025`
- `site:arxiv.org frequency domain loss time series 2025`
- `site:sciencedirect.com measurement sensor nonlinearity`

## 发现结果

### 新增文献线索

| 文献 | 类型 | 相关性 | 入口/链接 |
|-----|------|-------|----------|
| FreDN (An 2025) | P0 | 高 | https://arxiv.org/abs/2511.11817 |
| Ada-MoGE (Ni 2025) | P1 | 高 | https://arxiv.org/abs/2512.02061 |
| Process-Informed KAN (Rubini 2025) | P0 | 高 | https://arxiv.org/abs/2509.20349 |
| FreLE (Sun 2025) | P0 | 高 | https://arxiv.org/abs/2510.25800 |
| FIRE (He 2025) | P0 | 高 | https://arxiv.org/abs/2510.10145 |
| FODEs (Guo 2025) | P1 | 中 | https://arxiv.org/abs/2510.04133 |
| PETSA (Medeiros 2025) | P0 | 高 | https://arxiv.org/abs/2506.23424 |
| OLMA (Shi 2025) | P0 | 高 | https://arxiv.org/abs/2505.11567 |
| AEFIN (Xiong 2025) | P0 | 高 | https://arxiv.org/abs/2505.06917 |
| TimeCF (Wang 2025) | P1 | 高 | https://arxiv.org/abs/2505.17532 |
| BSP Loss (Chakraborty 2025) | P1 | 高 | https://arxiv.org/abs/2502.00472 |
| Fre-CW (Feng 2025) | P1 | 中 | https://arxiv.org/abs/2508.08955 |

### 入口已定位（重复确认）
- KAN-FIF (Shen 2026) - 94.8%参数压缩
- FreDF (Wang 2025 ICLR) - AFMAE公式来源
- OLMA (Shi 2025) - 频域熵减定理
- Physical KAN (Taglietti 2026) - 传感器应用
- WaveKAN (Feng 2026) - 光学传感

### 疑似重复/已排除
- Fre-CW (Feng 2025) - 对抗攻击相关，与本论文目标不直接相关

## 待核实事项
- Process-Informed KAN (Rubini 2025) 需确认与本论文GAP7前馈利用非线性区的关联
- Ada-MoGE (Ni 2025) 的自适应频率专家混合模型可作为频域损失对比参考

## 对文档的影响
- 更新 `raw_literature.md`：新增12条文献线索
- 更新 `literature_catalog.md`：更新频域损失和传感器应用部分
- 更新 `GAP文献缺口.md`：确认所有GAP仍无缺口

## 原始链接
- https://arxiv.org/abs/2511.11817 (FreDN)
- https://arxiv.org/abs/2512.02061 (Ada-MoGE)
- https://arxiv.org/abs/2509.20349 (Process-Informed KAN)
- https://arxiv.org/abs/2510.25800 (FreLE)
- https://arxiv.org/abs/2510.10145 (FIRE)
- https://arxiv.org/abs/2506.23424 (PETSA)
- https://arxiv.org/abs/2505.11567 (OLMA)
- https://arxiv.org/abs/2505.06917 (AEFIN)
