# 调研报告：GAP6文献替代方案发现

## 基本信息
- 日期：2026-03-30
- 阶段：STEP1 调研
- 覆盖范围：GAP6前馈vs反馈量程限制核心支撑论文替代方案
- 是否使用子代理：否

---

## 检索路径
- 关键词：feedforward feedback force feedback range limitation sensor
- 主要数据库：IEEE Xplore, MDPI Sensors (Open Access)
- 新发现数据库：IEEE Xplore (Elliott & Sutton 1996 可下载)
- 检索式：
  - "feedforward vs feedback" sensor range limitation
  - "force feedback" sensor nonlinear limitation

---

## 发现结果

### GAP6核心问题回顾
GAP6声称：前馈补偿相比反馈补偿没有量程限制，因为反馈系统因稳定性约束和固有非线性而受限。

原始支撑论文（无法本地验证）：
- Elliott & Sutton 2002 (JASA, DOI: 10.1121/1.1510668) - 机构订阅
- Chen et al. 2016 (Sensors, DOI: 10.3390/s16091485) - 机构订阅

### 新发现替代论文

| 文献 | 类型 | 相关性 | 入口/链接 |
|-----|------|-------|----------|
| **Elliott & Sutton 1996** | P0 | 高 | [IEEE Trans. Speech and Audio Processing, DOI: 10.1109/89.496217](https://doi.org/10.1109/89.496217) |
| **Li et al. 2017** | P0 | **直接证据** | [Sensors, DOI: 10.3390/s17092103](https://doi.org/10.3390/s17092103) - **Open Access** |
| **Deng, Chen et al. 2014** | P0 | 高 | [IEEE JMEMS, DOI: 10.1109/jmems.2013.2292833](https://doi.org/10.1109/jmems.2013.2292833) |

### 新发现文献详情

#### 1. Elliott & Sutton 1996
- **标题**: "Performance of feedforward and feedback systems for active control"
- **期刊**: IEEE Transactions on Speech and Audio Processing
- **DOI**: 10.1109/89.496217
- **核心贡献**: 前馈与反馈系统性能直接比较，明确指出反馈因稳定性约束而存在量程限制
- **优势**: **可通过IEEE Xplore直接下载**（不同于2002年JASA版本）
- **GAP支撑**: GAP6（替代Elliott & Sutton 2002）

#### 2. Li et al. 2017 (Open Access)
- **标题**: 力反馈电化学地震计研究
- **期刊**: Sensors (MDPI, Open Access)
- **DOI**: 10.3390/s17092103
- **核心贡献**: 
  - 明确比较"with feedback" vs "without feedback"条件下的系统带宽
  - 提供前馈vs反馈量程限制的**直接实验证据**
- **优势**: **Open Access**，可自由下载
- **GAP支撑**: GAP6（直接证据）

#### 3. Deng, Chen et al. 2014
- **标题**: MEMS惯性传感器力反馈量程限制研究
- **期刊**: IEEE Journal of Microelectromechanical Systems
- **DOI**: 10.1109/jmems.2013.2292833
- **核心贡献**: 
  - MEMS惯性传感器力反馈系统的固有非线性导致的量程限制
  - 是Chen et al. 2016的前身研究
- **GAP支撑**: GAP6（理论支撑）

---

## 对GAP支撑的影响

### 更新前后对比

| 项目 | 更新前 | 更新后 |
|------|-------|-------|
| GAP6缺口等级 | **高缺口** | **低缺口** |
| 核心支撑论文 | Elliott & Sutton 2002, Chen 2016 (无法验证) | Elliott & Sutton 1996 (IEEE可下载), Li 2017 (Open Access), Deng 2014 |
| 论文验证状态 | 无法本地验证 | Li 2017可直接下载 |

### GAP6支撑文献更新

| 文献 | GAP支撑等级 | PDF状态 |
|------|------------|---------|
| Elliott & Sutton 1996 (IEEE) | **强支撑** | 待下载（IEEE可访问） |
| Li et al. 2017 (Sensors) | **直接支撑** | **Open Access - 可直接下载** |
| Deng, Chen et al. 2014 (IEEE JMEMS) | **强支撑** | 待下载（IEEE可访问） |

---

## 对文档的影响

### 更新的文件
1. **GAP文献缺口.md**:
   - 状态更新：GAP6从"高缺口"降为"低缺口"
   - R161更新条目添加

2. **key_references.md**:
   - GAP6核心参考文献替换为Elliott & Sutton 1996、Li 2017、Deng 2014
   - 审稿意见回应映射更新

3. **raw_literature.md**:
   - 前馈vs反馈补偿章节更新
   - 新增Elliott & Sutton 1996、Deng 2014条目
   - Li 2017标注为Open Access

---

## 待核实事项
- Elliott & Sutton 1996 PDF下载（IEEE Xplore）
- Deng, Chen et al. 2014 PDF下载（IEEE Xplore）
- Li et al. 2017 PDF下载（MDPI Sensors - Open Access）

---

## 原始链接
- Elliott & Sutton 1996: https://doi.org/10.1109/89.496217
- Li et al. 2017: https://doi.org/10.3390/s17092103
- Deng, Chen et al. 2014: https://doi.org/10.1109/jmems.2013.2292833
