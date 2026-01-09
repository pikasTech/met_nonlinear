<style>
pre {
  overflow-y: auto;
  max-height: 300px;
}
</style>
# README

## 安装

``` bash
git clone https://gitee.com/Lyon1998/seismic-ai
git submodule init
git submodule update
```

## 依赖

- MATLAB 2022a
- Docker

## 启动 jupyter 镜像

``` bash
sh build.sh
sh run.sh
# gpu mode: sh run.sh --gpus=all
```
打开 127.0.0.1:8888，密码: 518518

## Test
```
python3 test.py
```

## 工程结构

- application - jupyter notebook 以及相关的数据
- assets - 图片等资源文件，通常是 markdown 用到的
- docker - 容器相关文件
- document - 文档、论文以及参考文献
- lib - 库，主要是 seismic_ai Python 库，application 中会调用
- study - 相关学习资料
- testcase - 库的测例

# 2022年4月10日

## 地震领域的人工智能应用调研

### 应用层

- 勘探
  - 地震成像
    - P波到时
    - P波初动极性
    - 地震炮点集初动提取
    - 震相拾取
  
- 地震预测
  - 地震预警
    - 汶川余震
- 安全
  - 入侵检测
  - 滑坡事件
  - 建筑安全

### 中间层

- 数据处理
  - 数据分离
  - 数据压缩\压缩感知
  - 去噪
  
- 预测
  - 插值\废道重建
  
  - 频率拓展\估计法
  
    ![image-20220325002315910](assets/image-20220325002315910.png)
  
    使用中间段的数据，通过神经网路估计出低频段和高频段
  
    数据获得：对随机产生的速度模型进行模拟正演
  
- 辨识
  - 事件类型识别
### 数据渠道
- 加州南部区域的高达1820万个地震图
- 智能手机数据

## 重要文献

 [人工智能技术在地震减灾应用中的研究进展_隗永刚.pdf](D:\Users\lyon\Desktop\aiot\doc\reference\人工智能技术在地震减灾应用中的研究进展_隗永刚.pdf) 

 [基于卷积神经网络的地震数据重构与模型构建研究_毛博.caj](D:\Users\lyon\Desktop\aiot\doc\reference\基于卷积神经网络的地震数据重构与模型构建研究_毛博.caj) 



## 无线传感网中的人工智能应用调研

### 无线传感网

WSN 属于自组织网络。

- 特点

	- 成本低
	- 功耗有限
- 应用

	- 数据感知
	- 检测
- 挑战
	- 资源
	- 算力
	- 功耗
- 关键技术
	- 数据收集
	- 聚合
	- 传播
- 指标
	- 分组传输速率
	- 网络寿命
	- 能效比
- 研究热度

![image-20220325110106120](assets/image-20220325110106120.png)

18年开始发文量显著提高

- 人工智能相关技术

	- 模糊逻辑
	  模糊逻辑是一种模仿人类决策方式的人工智能技术。它被用于不确定的推理或管理不完整的信息。可能性是真（T）或假（F）。真值是在0和1之间的 "真值 "基础上工作的。.模糊集的成员资格可以取0和1之间的任何数值，例子包括中心点模糊化、最大值和平均最大值。
	
	- 人工神经网络
	  神经网络（ANN），强化学习（RL）和深度学习（DL）。凭借模仿生物神经网络和人类属性的能力，ANNs已经成功地解决了复杂的挑战性问题。已经成功地解决了复杂的挑战性问题。神经网络由小型被称为节点的互连设备，其灵感来自大脑中的生物神经元。信息从这些相互连接的设备中通过用箭头示的链接来传递。箭头。输入和权重是与传入连接相关的两个值。其总和将产生该单元的输出。在使用训练数据集训练ANN之后训练数据集后，可以引入新的数据集，这样训练后的ANN就可以进一步用于预测和分类目的。与其他方法相比，使用ANN的主要优势在于与其他方法相比，使用ANN的关键优势在于它能够对非线性和复杂的在输入和输出变量之间没有太多的干扰。它被用来用于解决许多与预测和验证、优化、函数近似、聚类、时间序列分析和模式识别。一些文献中存在几种ANN的结构，包括 径向基函数网络、多层感知（MLP）、反向传播（Back-Propagation）和递归神经网络（RNN）。

	- 进化计算

	- 元启发式算法
	  元启发式算法是最常见的算法类型，它使用一定程度的随机性来实现对困难问题的最优解（或尽可能的最优）。
	  元启发式算法被应用于大量的领域。元启发式算法可以以各种方式进行分类。基

	- 多智能体系统

	  多个相互作用的智能代理可以解决单个代理或单体系统难以解决的问题。单一系统难以解决的问题，通过搜索和与环境互动。代理人搜索寻找其他相邻的代理，并与他们或环境互动，以学习新事物并做出决定。为了完成他们指定的任务，代理利用他们的知识，做出决定并在环境中进行行动。

	- 基于轨迹的
	
	  通常目的是通过在设计（搜索）空间中的分片式运动来定位一个单一的最优解设计（搜索）空间（例如，模拟退火）。而基于群体的方案在搜索空间中使用多个解决方案并相互合作以达到最终的解决方案（例如，进化计算、物理启发计算和自然启发的计算）。进化计算的灵感来自于生物进化计算的灵感来自于生物进化和自然选择、交叉或重组和突变（例如，遗传算法、差分进化和记忆算法）。
	
	- 物理计算
	
	- 蜂群系统
	
	  由一群社会性昆虫产生的集体行为被称为蜂群智能（SI）。SI涉及到环境中众多同质个体的合作。
	  众多同质个体在环境中的合作。这种技术涉及战略，并在个体之间分享个体之间共享信息，以实现自我组织、学习和共同进化。迭代过程中，提供高效率。这些个体遵循非常简单的规则由于没有中央基础设施来显示个体的行为方式，个体之间可以进行互动，这些个体作为一个群体可以使用任何信息载体交换相关数据。
	
	- 强化学习
	
	  RL是人工智能的一个分支，涉及到智能代理应该如何在一个给定的环境中进行互动，以使累积奖励的概念最大化。环境中进行互动，以使累积奖励的概念最大化。学习是在RL过程中，通过学习实体和其周围环境之间的互动来完成。对象试图通过试验和错误来学习。价值函数价值函数、环境和强化函数是RL的三个主要组成部分。组成部分。RL的环境通常是动态的，有一系列可能的状态。在任何时候，每种状态都有一组可行的行动。
	
	- 混合

![image-20220325110527822](assets/image-20220325110527822.png)

## 重要文献

 [Recent Studies Utilizing Artificial Intelligence Techniques for Solving Data Collection, Aggregation and Dissemination Challenges in Wireless Sensor Networks A Review.pdf](..\reference\Recent Studies Utilizing Artificial Intelligence Techniques for Solving Data Collection, Aggregation and Dissemination Challenges in Wireless Sensor Networks A Review.pdf) 

## 小结

- 已经发现有一篇很新的关于 WSN 和 AI 综合应用的综述文献（2022年1月公开）

 [Recent Studies Utilizing Artificial Intelligence Techniques for Solving Data Collection, Aggregation and Dissemination Challenges in Wireless Sensor Networks A Review.pdf](..\reference\Recent Studies Utilizing Artificial Intelligence Techniques for Solving Data Collection, Aggregation and Dissemination Challenges in Wireless Sensor Networks A Review.pdf) 

- 在 [基于卷积神经网络的地震数据重构与模型构建研究_毛博.caj](D:\Users\lyon\Desktop\aiot\doc\reference\基于卷积神经网络的地震数据重构与模型构建研究_毛博.caj) 中，有一个关于使用 AI 进行频率拓展的应用，但仅限于仿真环境，且模型很简单。或许可以尝试复现并改进这个方法。

- AI 的一些常用技术还没有熟悉，目前只是简单的尝试了 tensorflow，运行了一些常见案例，如猫狗识别，人脸识别等。还缺乏一些基础知识，买了一本《统计学习原理》，在尝试补充相关的数学基础。

# 2022年5月13日

## 相关文献：生成数据断层识别

[FaultSeg3D: Using synthetic data sets to train an end-to-end convolutional neural network for 3D seismic fault segmentation](..\reference\geo2018-0646.1.pdf) 

## 阅读笔记：

<img src="assets/image-20220513203708841.png" alt="image-20220513203708841" style="zoom:50%;" />

<img src="assets/image-20220513203716426.png" alt="image-20220513203716426" style="zoom: 50%;" />

![image-20220513203900301](assets/image-20220513203900301.png)

从上一篇论文的结论部分出发，传统的方法对拟合参数、范围和数据质量很敏感，可以考虑使用机器学习的方法增强鲁棒性，以及提高算法的速度。

![image-20220520115807118](assets/image-20220520115807118-16612704126161.png)

或者可以考虑直接使用阶跃信号的时域数据或者频谱数据作为输入，不需要完整的扫频过程。

![image-20220520120018575](assets/image-20220520120018575-16612704126162.png)

![image-20220529232324856](assets/image-20220529232324856-16612704126173.png)

![image-20220529232338178](assets/image-20220529232338178-16612704126176.png)

![image-20220529232346408](assets/image-20220529232346408-16612704126175.png)

![image-20220529232356080](assets/image-20220529232356080-16612704126174.png)

![image-20220529232403479](assets/image-20220529232403479-16612704126177.png)

![image-20220529232416716](assets/image-20220529232416716-166127041261710.png)

![image-20220529232427383](assets/image-20220529232427383-16612704126178.png)

![image-20220529232433695](assets/image-20220529232433695-16612704126179.png)

![image-20220529232444596](assets/image-20220529232444596-166127041261711.png)

# 2022年5月23日

原先的方法对拟合参数和测量误差很敏感，需要人工调整才能得到比较好的效果。

测量结果和拟合结果之间有较大的差异，测量结果和拟合结果之间的差异主要来源于两个部分：

- 客观部分

  - 测量误差 — 可视为随机

  - 模型精度 — 可视为固定

- 主观部分

  - 实验员调参 — [频率权重] (可以视为一种标注)

考虑是否可以通过 AI 来学习实验员的标注过程，免去调参，以及减少测量误差的影响。

![image-20220523142337966](assets/image-20220523142337966-166127041261712.png)

实验的主要问题在于：

- 如何获得数据？
- 数据的生成方式
- 训练模型的结构和参数选择
- 对结果进行仿真测试 — 免标注，加噪声 （测量误差）
- 对结果进行实际测试

实际上传统方法使用的完整模型是[ 算法 + 可调参数 ]，AI模型不仅是对[算法]进行拟合，而是对[ 算法 + 可调参数 ]进行端到端的拟合。

# 2022年5月31日

需要对原数据进行生成，生成的方式有：

- 加滤波
  - 全频
  - 低频
  - 中频
  - 高频
- 加噪声
  - 全频段
  - 特定频段

# 2022年8月22日

## 上一篇电化学论文还没有解决的问题
1. 在某些情况下，系统对拟合方法和拟合配置的选择比较敏感，如果系统的拟合结果在低频阶段误差过大，反馈参数的计算结果就会受到影响。

- 可以通过神经网络替代传统的拟合过程，提高鲁棒性，或者直接由原始数据通过神经网络得到端到端的结果。

2. 自调整方法的速度只取决于自测试速度，因此也可以尝试更快的测试方法(如阶跃响应测量方法)。而自调节速度的提高在某些具体领域可能具有较大的意义.通过更快的自调整，可以放宽对敏感元件的稳定性要求，从而使一些性能优良但因稳定性不足而被排除在外的敏感元件重新纳入地震计的设计考虑。

- 可以通过神经网络，直接由时域数据对测试结果进行估计，提高测试的速度。

## 数据收集

电化学实验过程中记录了大量的实验数据，可以考虑从实验数据中获得训练的数据。

![image-20220822111533278](assets\image-20220822111533278.png)

### .mat 数据转换

实验数据是 matlab 生成的 .mat 格式数据，需要能够导入到 python 的机器学习框架中，需要对 .mat 格式的数据进行转码。

查阅资料得知，scipy.io 的 scio 模块可以导入 .mat 数据到 python 中。为了数据格式的通用性，将  .mat 的数据转为 json 格式的数据。

```python
import scipy.io as scio
import pandas as pd
import json
import numpy as np
import os
data_path = "data/20220531/20220531T170650-fl-11-data-282.mat"


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        elif np.iscomplexobj(obj):
            return abs(obj)
        return json.JSONEncoder.default(self, obj)


data = scio.loadmat(data_path)
data_json = json.dumps(data, cls=MyEncoder, sort_keys=False, indent=2)

save_path = os.path.splitext(data_path)[0] + '.json'
file = open(save_path, 'w', encoding='utf-8');
file.write(data_json)
file.close()

```

但是转码后的效果不好，只有开头有一些信息

``` json
{
  "__header__": "MATLAB 5.0 MAT-file, Platform: PCWIN64, Created on: Tue May 31 17:06:52 2022",
  "__version__": "1.0",
  "__globals__": [],
  "data_saved": [
    [
      [
        [
          [
            [
              [
                "20220531T170650"
              ],
              [
                "yyyymmdd"
              ],
              [
                [
                  [
                    [
                      "."
                    ],
                    [
                      "C:\\Users\\lyon\\Desktop\\seismic-ai\\application\\2.Run_MET_SIMULATION_ON_Matlab_And_Save_Result\\data"
                    ],
                    [
                      "31-5\u6708-2022 16:40:56"
                    ],
                    [
                      [
                        0
                      ]
                    ],
                    [
                      [
```

其他地方是意义不明的纯数据

``` json
     122,
      110,
      69,
      70,
      67,
      77,
      110,
      75,
      82,
      109,
      110,
      86,
      88,
      97,
      99,
      103,
      106,
      118,
      66,
      112,
      99,
      66,
      50,
      67,
      110,
      85,
      99,
      78,
      50,
      86,
      82,
      83,
      48,
```

查阅资料得知 matlab 也有转换 json 的库，编写 mat2json.m，进行转换

``` matlab
addpath('../../lib/met/project/software/met_simu/matCore');

close all;
clc;
clear;

watch_fun = watch_class;
watch = watch_fun.init();
watch.mydata.matdir = "data/20220531/20220531T170650-fl-11-data-282";
watch.A_gain = 1;
watch.config.show = "all";
watch = watch_fun.loadData(watch);

res = watch.mydata.data_saved.res;
par = watch.mydata.data_saved.par;
config = watch.mydata.data_saved.config;

res.H0 = rmfield(res.H0,"numer");
res.H0 = rmfield(res.H0,"syms");

res.Wa = rmfield(res.Wa,"numer");
res.Wa = rmfield(res.Wa,"syms");

res.Wf = rmfield(res.Wf,"numer");
res.Wf = rmfield(res.Wf,"syms");

res.Wfb = rmfield(res.Wfb,"numer");
res.Wfb = rmfield(res.Wfb,"syms");

res.Wfb0 = rmfield(res.Wfb0,"numer");
res.Wfb0 = rmfield(res.Wfb0,"syms");

res.Wfb0_simply = rmfield(res.Wfb0_simply,"number");
res.Ws = rmfield(res.Ws,"numer");
res.Ws = rmfield(res.Ws,"syms");

res = rmfield(res, "cfun");
res = rmfield(res, "Wp");

data.res = res;
data.par = par;
data.config = config;

data_json = jsonencode(data);

```

其中，matlab 中的虚数和符号是不能转换为 json 的，因此要使用 refield 删除这些数据

转换后的数据:

![image-20220822185539952](assets\image-20220822185539952.png)

![image-20220822185548943](assets\image-20220822185548943.png)

可以正确将 .mat 转换为 .json 数据。

# 2022年8月24日

## 批量转换 .mat 数据

递归地对目录下的所有 .mat 文件进行转换，（需要排除 main_data.mat 缓存文件）

``` matlab
   for i = 1:length(subdir)
        if subdir(i).isdir
           if strcmp(subdir(i).name, '.') || strcmp(subdir(i).name, '..')
                continue;
            end
            res = mat2json_with_res(fullfile(input_mat_path, subdir(i).name), output_dir, res);
        else
            if ~strcmp(subdir(i).name( end - 3:end), '.mat')
                continue;
            end
            if strcmp('main_data.mat', subdir(i).name)
                continue;
            end
            mat_file = fullfile(input_mat_path, subdir(i).name);
            if (0 == mat2json_file(mat_file, output_dir))
                res.success = res.success + 1;
            end
            res.totle = res.totle + 1;
        end
    end
```

指定输入和输出文件夹进行转换：

```matlab
mat2json('data', 'out');
mat2json('../../lib/met/project/software/met_simu/data', 'out');
```

转换结果：

```
...
Writing to file: out/20220311T050206-fl-11-data-282.json
[   OK]
Converting: ..\..\lib\met\project\software\met_simu\data\20220520\20220520T115045-fl-11-data-282.mat
Writing to file: out/20220520T115045-fl-11-data-282.json
[   OK]
Converting: ..\..\lib\met\project\software\met_simu\data\20220520\20220520T162638-fl-11-data-282.mat
Writing to file: out/20220520T162638-fl-11-data-282.json
[   OK]
Converting: ..\..\lib\met\project\software\met_simu\data\20220520\20220520T162715-fl-11-data-282.mat
Writing to file: out/20220520T162715-fl-11-data-282.json
[   OK]
    success: 92
      totle: 718
```

以往的数据共有 718 个，转换成功了 92 个，比较旧的数据因为格式原因没有解析成功。

转换成功的数据：

![image-20220824000834963](assets/image-20220824000834963.png)

# 2022年8月27日

解析 json 数据时发现存在问题

![image-20220827161557970](assets/image-20220827161557970.png)

当字串中存在 '\\' 符号时，会解析失败，原因是 matlab 生成 json 时没有给 '\\' 添加转义，这应该是 matlab 的 json 库的 bug。

config.mat_dir 属性在训练中用不到，可以直接删除

```matlab
config = rmfield(config, 'mat_dir');
```

# 2022年9月2日

## 使用 seismic_ai

seismic_ai 模块是一个专门为本项目编写的工具库，用来处理地震数据，在 /lib/seismic_ai/ 文件夹中。
为了能够在本目录下使用，将 /lib/seismic_ai 软连接到本目录下。

``` bash
ln -s ../../lib/seismic_ai .
```

根据路径导入数据，然后得到一个 `metData` 对象


```python
import seismic_ai
import tensorflow as tf
import numpy as np
import shutil
metData = seismic_ai.met.loadData('data/20220114T205036-fl-11-data-234.json')
```

打印 met 对象查看信息


```python
print(metData)
```

    METData(
        wswf=System(name=WsWf, freq[31], gain[31], phase[31]), 
        parameter=METParameter(frequency_low=1.1, curcuit=CurcuitParameter(C1=2.2e-06, C2=1e-08, R1=100000, R2=3000000.0, R3=200000), kp=0, kd=-0.01), 
        result=METResult(kp0=0.004080398172276639, kd0=-0.012818937163632837)
    )


`met` 对象中包含了传递函数对象 `wswf`，参数 `parameter`，和结果 `result`。

`parameter.frequency_low` 是期望的低频截止频率

`wswf` 是 `wswf` 环节的传递函数

`parameter` 的其他属性是系统的参数，包括电路参数 `curcuit`

`result` 是用之前的算法得到的反馈参数

## 训练目标

考虑可以使用 `wswf` 和 `parameter` 作为输入参数来训练网络，输出参数为 `result`。

这样可以免去拟合的环节，直接由测量的原始数据得到最后的结果，避免了拟合环节人工调参步骤，增强了鲁棒性。



构造训练用的数据单元，`y_train_unit` 是一个数据的输出单元，`x_train_unit` 是一个数据的输入单元。


```python
y_train_unit = np.array([metData.result.kp0, metData.result.kd0])
x_train_unit = np.array(
    metData.wswf.freq +
    metData.wswf.gain +
    metData.wswf.phase +
    metData.parameter.curcuit.list() +
    [metData.parameter.frequency_low]
)
print('y_train_unit=', y_train_unit)
print('x_train_unit=', x_train_unit)

```

    y_train_unit= [ 0.0040804  -0.01281894]
    x_train_unit= [1.00000000e-01 1.28682000e-01 1.65590000e-01 2.13084000e-01
     2.74201000e-01 3.52847000e-01 4.54050000e-01 5.84280000e-01
     7.51862000e-01 9.67509000e-01 1.24500900e+00 1.60210000e+00
     2.06161200e+00 2.65292000e+00 3.41382600e+00 4.39297400e+00
     5.65295900e+00 7.27433200e+00 9.36074400e+00 1.20455760e+01
     1.55004680e+01 1.99462870e+01 2.56672480e+01 3.30290870e+01
     4.25024340e+01 5.46929090e+01 7.03798370e+01 9.05660710e+01
     1.16542076e+02 1.49968491e+02 0.00000000e+00 4.51297065e+00
     5.80898906e+00 7.43162116e+00 9.60510150e+00 1.49966042e+01
     2.23541213e+01 2.71504478e+01 3.70576717e+01 4.79289886e+01
     4.36426964e+01 5.64164074e+01 7.26706127e+01 9.25784126e+01
     1.21592625e+02 1.58770552e+02 2.10635011e+02 2.73255794e+02
     3.57006141e+02 4.61926130e+02 5.93759717e+02 7.54506775e+02
     9.68770061e+02 1.23836089e+03 1.59462211e+03 2.02412805e+03
     2.60078348e+03 3.37140036e+03 4.36432784e+03 5.75127734e+03
     7.91933528e+03 0.00000000e+00 9.00049210e+01 9.00092010e+01
     9.00247340e+01 9.00547410e+01 9.00682830e+01 9.00116960e+01
     8.98093720e+01 8.93718950e+01 8.85082470e+01 8.62218170e+01
     8.45669860e+01 8.33900150e+01 8.37646030e+01 8.70381770e+01
     9.27116090e+01 1.00000710e+02 1.07235893e+02 1.12742615e+02
     1.15874382e+02 1.16630890e+02 1.15986351e+02 1.14068207e+02
     1.12017166e+02 1.09964401e+02 1.08547791e+02 1.07559792e+02
     1.07005424e+02 1.07006393e+02 1.05679825e+02 9.05816880e+01
     0.00000000e+00 2.20000000e-06 1.00000000e-08 1.00000000e+05
     3.00000000e+06 2.00000000e+05 1.10000000e+00]


遍历 `data` 文件夹下的所有数据，然后得到 `y_train` 和 `x_train`


```python
from json import load
import os
# for each file in data folder
file_path_list = []
for path, dir_list, file_list in os.walk('data'):
    for file_name in file_list:
        file_path_list.append(os.path.join(path, file_name))

y_train = []
x_train = []
for file_path in file_path_list:
    try:
        metData = seismic_ai.met.loadData(file_path)
        y_train_unit = np.array([metData.result.kp0, metData.result.kd0])
        x_train_unit = np.array(
            metData.wswf.freq +
            metData.wswf.gain +
            metData.wswf.phase +
            metData.parameter.curcuit.list() +
            [metData.parameter.frequency_low]
        )
        y_train.append(y_train_unit)
        x_train.append(x_train_unit)
    except:
        print('Error:', file_path)

y_train = np.array(y_train)
x_train = np.array(x_train)
print(y_train)
print(x_train)
```

    Error: data/20220520T162638-fl-11-data-282.json
    Error: data/20220520T162715-fl-11-data-282.json
    Error: data/20220520T115045-fl-11-data-282.json
    [[ 2.41434403e-02 -1.40480782e-01]
     [ 1.76011707e-03 -9.81469696e-03]
     [ 2.96105707e-03 -1.66545684e-02]
     [-1.07805150e-01 -4.38603514e-01]
     [ 4.08039817e-03 -1.28189372e-02]
     [ 1.75872523e-03 -5.86724769e-02]
     [-2.36593034e-01 -9.61164792e-01]
     [ 1.79377093e-03 -1.01119579e-02]
     [ 1.76011707e-03 -9.81469696e-03]
     [-9.74011791e-01 -3.95373080e+00]
     [ 1.88697225e-02 -5.96867904e-02]
     [ 1.76011707e-03 -9.81469696e-03]
     [-6.63284980e-03 -2.95270912e-01]
     [ 4.08039817e-03 -1.28189372e-02]
     [-6.63284980e-03 -2.95270912e-01]
     [ 4.79194166e-02 -8.60430403e-02]
     [ 5.90995670e-03 -2.79209022e-02]
     [ 2.94508031e-03 -7.46818640e-02]
     [ 6.00943904e-03 -8.07450797e-02]
     [ 1.68282074e-03 -9.31920248e-03]
     [ 2.91647233e-03 -7.63231826e-02]
     [-8.45883251e-02 -3.44471461e-01]
     [ 1.76011707e-03 -9.81469696e-03]
     [ 1.96315620e-02 -1.07252645e-01]
     [ 1.73835045e-03 -9.73915044e-03]
     [ 1.96315620e-02 -1.07252645e-01]
     [ 1.76011707e-03 -9.81469712e-03]
     [ 4.85058132e-03 -2.20210417e-02]
     [ 1.95151095e-02 -2.87449696e-02]
     [ 5.94302823e-03 -1.01068567e-02]
     [ 5.94302823e-03 -1.01068567e-02]
     [-1.19646228e-01 -4.86613743e-01]
     [-1.77252577e-02 -2.44276443e-01]
     [ 2.96105708e-03 -1.66545685e-02]
     [-1.85193315e-02 -2.29041249e-01]
     [ 2.96105707e-03 -1.66545684e-02]
     [ 1.76011707e-03 -9.81469696e-03]
     [ 3.43745986e-02 -1.80539701e-01]
     [-1.56382802e+00 -6.34729355e+00]
     [ 1.76011707e-03 -9.81469696e-03]
     [ 1.76011707e-03 -9.81469696e-03]
     [ 1.75865411e-03 -9.84792841e-03]
     [ 6.67388698e-03 -5.88344880e-02]
     [ 1.96315620e-02 -1.07252645e-01]
     [ 4.79194166e-02 -8.60430403e-02]
     [ 8.93857429e-02 -2.83961642e-01]
     [ 4.08039817e-03 -1.28189372e-02]
     [ 6.96791812e-03 -9.37696566e-02]
     [ 7.35021552e-03 -9.65482213e-02]
     [-5.16030021e-01 -2.09497440e+00]
     [-1.77252577e-02 -2.44276443e-01]
     [ 4.08040661e-03 -1.28189567e-02]
     [-2.75398290e-02 -2.99805303e-01]
     [ 1.62094585e-03 -9.06534235e-03]
     [ 1.75865411e-03 -9.84792841e-03]
     [ 2.94242831e-03 -7.82977359e-02]
     [ 1.76011707e-03 -9.81469696e-03]
     [ 6.00943904e-03 -8.07450797e-02]
     [ 2.96105707e-03 -1.66545684e-02]
     [ 2.94508031e-03 -7.46818640e-02]
     [ 3.43743082e-02 -1.80536370e-01]
     [ 6.00943904e-03 -8.07450797e-02]
     [ 1.95197714e-02 -1.06331324e-01]
     [ 2.94484624e-02 -1.58292516e-01]
     [ 2.94242831e-03 -7.82977359e-02]
     [ 4.08040661e-03 -1.28189567e-02]
     [ 6.96791812e-03 -9.37696566e-02]
     [ 1.76011707e-03 -9.81469696e-03]
     [ 1.76011707e-03 -9.81469696e-03]
     [ 4.08039817e-03 -1.28189372e-02]
     [ 1.58152370e-02 -1.85745980e-01]
     [ 3.51979875e-02 -1.10967515e-01]
     [ 1.75872523e-03 -5.86724769e-02]
     [ 2.91647225e-03 -7.63231825e-02]
     [-1.20411492e-01 -4.89715641e-01]
     [-2.75398290e-02 -2.99805303e-01]
     [ 5.94302823e-03 -1.01068567e-02]
     [-1.19646228e-01 -4.86613743e-01]
     [ 2.68698109e-03 -4.63811211e-03]
     [ 2.96105707e-03 -1.66545684e-02]
     [ 1.95197714e-02 -1.06331324e-01]
     [ 1.76011707e-03 -9.81469696e-03]
     [ 4.08040661e-03 -1.28189567e-02]
     [ 1.96315620e-02 -1.07252645e-01]
     [-6.63284980e-03 -2.95270912e-01]
     [ 5.94302823e-03 -1.01068567e-02]
     [ 4.08039817e-03 -1.28189372e-02]
     [ 1.75872523e-03 -5.86724769e-02]
     [-1.06224736e-02 -2.39840314e-01]
     [ 1.76011707e-03 -9.81469696e-03]
     [-1.19646228e-01 -4.86613743e-01]
     [-9.57837641e-01 -3.88809934e+00]
     [ 1.76011707e-03 -9.81469696e-03]
     [-1.07805150e-01 -4.38603514e-01]
     [-2.11952700e-03 -8.69714541e-02]
     [ 2.94484624e-02 -1.58292516e-01]
     [ 5.90995670e-03 -2.79209022e-02]
     [-1.20411492e-01 -4.89715641e-01]
     [ 1.76011707e-03 -9.81469696e-03]
     [ 1.75074855e-03 -9.88248407e-03]
     [ 1.49827823e-02 -9.95212248e-02]
     [ 5.94302823e-03 -1.01068567e-02]
     [ 7.35021552e-03 -9.65482213e-02]
     [ 1.76011707e-03 -9.81469696e-03]]
    [[1.00000e-01 1.28682e-01 1.65590e-01 ... 3.00000e+06 2.00000e+05
      1.10000e+00]
     [1.00000e-01 1.28682e-01 1.65590e-01 ... 3.00000e+06 2.00000e+05
      1.10000e+00]
     [1.00000e-01 1.28682e-01 1.65590e-01 ... 3.00000e+06 2.00000e+05
      1.10000e+00]
     ...
     [1.00000e-01 1.28682e-01 1.65590e-01 ... 3.00000e+06 2.00000e+05
      1.10000e+00]
     [1.00000e-01 1.28682e-01 1.65590e-01 ... 3.00000e+06 2.00000e+05
      1.10000e+00]
     [1.00000e-01 1.28682e-01 1.65590e-01 ... 3.00000e+06 2.00000e+05
      1.10000e+00]]


有一部分数据解析失败，解析成功了 `104` 份数据

`x_train` 输出为 `104*99` 的 `array`，`y_train` 的输出为 `104*2` 的 `array`

保存 `x_train` 和 `y_train` 数据到 json 格式


```python
shutil.rmtree('out')
os.mkdir('out')
np.save('out/x_train', x_train)
np.save('out/y_train', y_train)
```

# 2022年9月7日
使用 `x_train` 作为输入参数，`y_train` 作为输出参数，进行训练


```python
import numpy as np
import tensorflow as tf

# 加载数据
x_train = np.load('data/x_train.npy')
y_train = np.load('data/y_train.npy')

```

搭建网络的结构，使用 `Sequential` 模式搭建序列化的网络

> ## Dense层: 全连接层
>
> Dense层的参数: units, activation, kernel_initializer, bias_initializer
>
> units: 输出的维度
>
> activation: 激活函数
>
> kernel_initializer: 权重矩阵的初始化方式
>
> bias_initializer: 偏置向量的初始化方式
>
> kernel_regularizer: 权重矩阵的正则化方式
>
> bias_regularizer: 偏置向量的正则化方式
>
> input_dim: 输入的维度
>
> input_shape: 输入的形状
>
> 例子: tf.keras.layers.Dense(units=3, activation='softmax', kernel_initializer='random_normal', bias_initializer=tf.zeros_initializer())
>
> ## Flatten层: 将多维的输入一维化
>
> Flatten层的参数: input_shape
>
> input_shape: 输入的形状
>
> 例子: tf.keras.layers.Flatten(input_shape=(28, 28))

```python
# 随机打乱数据的顺序
np.random.seed(116)
np.random.shuffle(x_train)
np.random.seed(116)
np.random.shuffle(y_train)
tf.random.set_seed(116)
```


```python
try:
    # y_train[:, 0] 取输出参数的第一个维度（即kp）
    y_train_kp = y_train[:, 0]
    model = tf.keras.models.Sequential([
        # 全连接层, 128个神经元, 神经元个数为超参数
        tf.keras.layers.Dense(128, activation='softmax',
                              kernel_regularizer=tf.keras.regularizers.l2()),
        # 输出参数为 2
        tf.keras.layers.Dense(1, activation='softmax')
    ])

    model.compile(optimizer=tf.keras.optimizers.SGD(learning_rate=0.1),
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(
                      from_logits=False),
                  metrics=['sparse_categorical_accuracy'])

    model.fit(x_train, y_train_kp, batch_size=32, epochs=500,
              validation_split=0.2, validation_freq=20)

    model.summary()
except Exception as e:
    print(e)
```

    Epoch 1/500
    1/3 [=========>....................] - ETA: 0s - loss: 1.1156 - sparse_categorical_accuracy: 0.0000e+00Graph execution error:
    ...
    Received a label value of -1 which is outside the valid range of [0, 1).  Label values: 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -1 0 0 0 0 0
    	 [[{{node sparse_categorical_crossentropy/SparseSoftmaxCrossEntropyWithLogits/SparseSoftmaxCrossEntropyWithLogits}}]] [Op:__inference_train_function_516]


在训练时出现错误
```
Received a label value of -1 which is outside the valid range of [0, 1).  Label values: 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -1 0 0 0 0 0
```
看起来是标签出的问题，可能和标签的设置有关

在例程中，有转换训练数据的操作，尝试转换数据类型然后再训练，结果依然是 `Received a label value of -1 which is outside the valid range of [0, 1).`


```python
x_train_f32 = x_train.astype('float32')
y_train_kp_f32 = y_train_kp.astype('float32')

model = tf.keras.models.Sequential([
    # 全连接层, 128个神经元, 神经元个数为超参数
    tf.keras.layers.Dense(32, activation='softmax',
                          kernel_regularizer=tf.keras.regularizers.l2()),
    # 输出参数为 2
    tf.keras.layers.Dense(1, activation='softmax')
])

model.compile(optimizer=tf.keras.optimizers.SGD(learning_rate=0.3),
              loss=tf.keras.losses.MeanSquaredError(),
             )

model.fit(x_train_f32, y_train_kp_f32, batch_size=32, epochs=500,
          validation_split=0.2, validation_freq=20)

model.summary()
```

    Epoch 499/500
    3/3 [==============================] - 0s 3ms/step - loss: 1.1502
    Epoch 500/500
    3/3 [==============================] - 0s 13ms/step - loss: 1.1502 - val_loss: 1.0635
    Model: "sequential_1"
    _________________________________________________________________
     Layer (type)                Output Shape              Param #   
    =================================================================
     dense_2 (Dense)             (None, 32)                3200      
                                                                     
     dense_3 (Dense)             (None, 1)                 33        
                                                                     
    =================================================================
    Total params: 3,233
    Trainable params: 3,233
    Non-trainable params: 0
    _________________________________________________________________

```python
# y_train[:, 0] 取输出参数的第一个维度（即kp）
y_train_kp = y_train[:, 0]
model = tf.keras.models.Sequential([
    # 全连接层, 128个神经元, 神经元个数为超参数
    tf.keras.layers.Dense(128, activation='softmax',
                          kernel_regularizer=tf.keras.regularizers.l2()),
    # 输出参数为 2
    tf.keras.layers.Dense(1, activation='softmax')
])

model.compile(optimizer=tf.keras.optimizers.SGD(learning_rate=0.1),
              loss=tf.keras.losses.BinaryCrossentropy(
                  from_logits=False),
              metrics=['sparse_categorical_accuracy'])

model.fit(x_train, y_train_kp, batch_size=32, epochs=500,
          validation_split=0.2, validation_freq=20)

model.summary()

```

    Epoch 497/500
    3/3 [==============================] - 0s 3ms/step - loss: -0.7061 - sparse_categorical_accuracy: 0.0000e+00
    Epoch 498/500
    3/3 [==============================] - 0s 3ms/step - loss: -0.7067 - sparse_categorical_accuracy: 0.0000e+00
    Epoch 499/500
    3/3 [==============================] - 0s 3ms/step - loss: -0.7081 - sparse_categorical_accuracy: 0.0000e+00
    Epoch 500/500
    3/3 [==============================] - 0s 14ms/step - loss: -0.7091 - sparse_categorical_accuracy: 0.0000e+00 - val_loss: -0.3073 - val_sparse_categorical_accuracy: 0.0000e+00
    Model: "sequential_2"
    _________________________________________________________________
     Layer (type)                Output Shape              Param #   
    =================================================================
     dense_4 (Dense)             (None, 128)               12800     
                                                                     
     dense_5 (Dense)             (None, 1)                 129       
                                                                     
    =================================================================
    Total params: 12,929
    Trainable params: 12,929
    Non-trainable params: 0
    _________________________________________________________________


网上查到的类似问题

> https://blog.csdn.net/The_Time_Runner/article/details/93889004
>
> （已解决）Error: Received a label value of 1 which is outside the valid range of [0, 1)-Python,Keras
> 用Keras做文本二分类，总是遇到如题错误，
> 我的类别是0或1，但是错误跟我说不能是1.
>
> 参见：Received a label value of 1 which is outside the valid range of [0, 1) - Python, Keras
> loss function的问题。
>
> 原来用的是sparse_categorical_crossentropy，
>
> 改为 binary_crossentropy 问题解决。
>

loss 修改为 `loss=tf.keras.losses.BinaryCrossentropy()` 可以运行训练了

但是训练出来的 `loss=-0.7084` ，是个负值，应该是有问题 

`sparse_categorical_accuracy` 的值也一直是 `0.0000e+00`

查阅文档后发现是损失函数 `loss` 的设置对 `label` 的范围有要求    

>https://keras.io/api/losses/probabilistic_losses/
>
>``` python
>CategoricalCrossentropy class
>tf.keras.losses.CategoricalCrossentropy(
>    from_logits=False,
>    label_smoothing=0.0,
>    axis=-1,
>    reduction="auto",
>    name="categorical_crossentropy",
>)
>```
>
>Computes the crossentropy loss between the labels and predictions.
>
>Use this crossentropy loss function when there are two or more label classes. We expect labels to be provided in a one_hot representation. If you want to provide labels as integers, please use SparseCategoricalCrossentropy loss. There should be # classes floating point values per feature.
>
>In the snippet below, there is # classes floating pointing values per example. The shape of both y_pred and y_true are [batch_size, num_classes].

文中指出
>We expect labels to be provided in a one_hot representation.

需要标签以独热码的形式给出，因此 `label` 需要是一个元素值在 `[0,1)` 范围的向量。

因此 `loss` 函数不能够选择 `SparseCategoricalCrossentropy()`


```python
model = tf.keras.models.Sequential([
    tf.keras.Input(shape=(99,)),
    # 全连接层, 128个神经元, 神经元个数为超参数
    tf.keras.layers.Dense(128, activation='softmax',
                          kernel_regularizer=tf.keras.regularizers.l2()),
    # 输出参数为 2
    tf.keras.layers.Dense(1, activation='softmax')
])

model.summary()
```

```
Model: "sequential_3"
_________________________________________________________________
 Layer (type)                Output Shape              Param #   
=================================================================
 dense_6 (Dense)             (None, 128)               12800     
                                                                 
 dense_7 (Dense)             (None, 1)                 129       
                                                                 
=================================================================
Total params: 12,929
Trainable params: 12,929
Non-trainable params: 0
_________________________________________________________________
```

通过 `tf.keras.Input(shape=(99,))` 可以指定输入数据的尺寸，或者不指定时，由实际输入的数据进行推断。
设置其他的值会和实际输入的数据冲突，在这个案例中只能设置为 `99`。手动指定后，可以使用 `summary()` 方法得到模型的尺寸


```python
try:
    model = tf.keras.models.Sequential([
        # 全连接层, 128个神经元, 神经元个数为超参数
        tf.keras.layers.Dense(128, activation='softmax',
                              kernel_regularizer=tf.keras.regularizers.l2()),
        # 输出参数为 2
        tf.keras.layers.Dense(1, activation='softmax')
    ])
    model.summary()
except Exception as e:
    print(e)

```

```
This model has not yet been built. Build the model first by calling `build()` or by calling the model on a batch of data.
```


否则就会报错，表示这个模型还没有被建立 `This model has not yet been built.`，因为缺乏输入层的尺寸信息。

> In general, it's a recommended best practice to always specify the input shape of a Sequential model in advance if you know what it is.
> https://keras.io/guides/sequential_model/

根据官方手册的建议，如果事先已经知道了输入层的尺寸，那就应该指定。

预测 `kp` `kd` 的值属于回归问题，因此应当使用回归损失 `Regrassion losses`，而不是概率损失 `Probabilistic losses`

> Regrassion losses:
> https://keras.io/api/losses/probabilistic_losses/

这里使用了回归损失中的 `MeanSquaredError`


```python
# y_train[:, 0] 取输出参数的第一个维度（即kp）
y_train_kp = y_train[:, 0]
model = tf.keras.models.Sequential([
    # 全连接层, 128个神经元, 神经元个数为超参数
    tf.keras.layers.Dense(32, activation='softmax',
                          kernel_regularizer=tf.keras.regularizers.l2()),
    tf.keras.layers.Dense(32, activation='softmax'),    
    # 输出参数为 2
    tf.keras.layers.Dense(1, activation='softmax')
])

model.compile(optimizer=tf.keras.optimizers.SGD(learning_rate=0.1),
              loss=tf.keras.losses.MeanSquaredError())

history = model.fit(x_train, y_train_kp, batch_size=32, epochs=500,
          validation_split=0.1, validation_freq=1)

model.summary()

```

```
Model: "sequential_5"
_________________________________________________________________
 Layer (type)                Output Shape              Param #   
=================================================================
 dense_10 (Dense)            (None, 32)                3200      
                                                                 
 dense_11 (Dense)            (None, 32)                1056      
                                                                 
 dense_12 (Dense)            (None, 1)                 33        
                                                                 
=================================================================
Total params: 4,289
Trainable params: 4,289
Non-trainable params: 0
_________________________________________________________________
```


绘制出损失函数的曲线


```python
import matplotlib.pyplot as plt
loss = history.history['loss']
epochs = range(1, len(loss) + 1)

plt.title('Loss')
plt.plot(epochs, loss, 'blue', label='Validation loss')
plt.legend()
plt.show()
```

![png](assets/main_18_0.png)

# 2022年9月11日

## 研究目标

研究目标是用机器学习的方法代替电化学自整定中的传统方法。

1. 主要的优化点在于通过端对端的方式避免传统方法中的拟合环节。

> 前一篇自论文的结论部分其一：
>
> 在某些情况下，系统对拟合方法和拟合配置的选择比较敏感，如果系统的拟合结果在低频阶段误差过大，反馈参数的计算结果就会受到影响。

2. 其次的优化点在于提高自整定的速度

> 前一篇论文的结论部分其二：
>
> 自调整方法的速度只取决于自测试速度，因此也可以尝试更快的测试方法(如阶跃响应测量方法)。而自调节速度的提高在某些具体领域可能具有较大的意义.通过更快的自调整，可以放宽对敏感元件的稳定性要求，从而使一些性能优良但因稳定性不足而被排除在外的敏感元件重新纳入地震计的设计考虑。

可以通过神经网络，直接由时域数据对测试结果进行估计，提高测试的速度。

## 目前的进度和下一个月的计划

已经完成的进度：

1. 成功将先前积攒的数据转化成了可以进行训练的格式，转换了 718 次测试结果中的 104 个。
2. 搭建完成了基础的神经网络，可以进行训练并得到一个训练好的模型。

还没有完成的部分：

1. 还没有对训练好的模型建立评价指标。
2. 训练用的数据量不足，需要考虑使用仿真的方法生成训练数据。

存在的问题：

1. 在本机 linux 模拟器上搭建的训练服务器稳定性不好，开关机时容易出现数据损坏，且 win 下搭建的 linux 虚拟机无法使用 GPU 资源， CPU 训练速度慢。
2. 原先使用 Matlab 编写的仿真程序难以在训练服务器上运行，和训练服务器上的程序联调困难。

下一个月的计划：

1. 是否可以考虑在实验室部署一台 linux 服务器用于训练。

   另一个方面，可以将电化学测试设备连接到服务器上，直接通过服务器进行数据采集，需要进行实验或者采集数据时登录登录到服务器即可。

2. 用 Python 重写 Matlab 的仿真程序，使其可以在训练服务器上运行，解决和神经网络训练程序联调困难的问题，以及可以支持强化学习的训练方法。

3. 建立合适的模型评价指标，能够对以下三种方案统一评价：

   - 手动参数整定

   - 传统算法的参数整定

   - 基于神经网络的参数整定

# 2022年10月2日

主体部分的算法已经用 Python 重写完成，已经可以使用 Python 运行电化学检波器的自调整算法。

![Figure_1](assets/Figure_1.png)

和 MatLab 程序的对比：

![image-20221005132200995](assets/image-20221005132200995.png)

可以看到有较大的差异，还需要分析原因。



# 2022年10月9日

## 云服务器的使用情况

### 计费模式

使用按量计费的服务器需要预存费用

![image-20221009183343873](assets/image-20221009183343873.png)

先预存了 50 元进行测试，消耗后可以开票，开票金额任意

![image-20221009183614938](assets/image-20221009183614938.png)

10 元以上包邮

![image-20221009183628550](assets/image-20221009183628550.png)

### 创建服务器

选择配置后可以查看组用价格

![image-20221009183836883](assets/image-20221009183836883.png)

选择预装系统的镜像，使用 ubuntu 20.04

![image-20221009183907501](assets/image-20221009183907501.png)

选择好后创建服务器

![image-20221009184059279](assets/image-20221009184059279.png)

创建完成后登录 ssh

![image-20221009184152042](assets/image-20221009184152042.png)

然后安装基础软件： docker，nvidia-toolkit（tensorflow 调用 nvidia GPU 的工具）等

构建 jupyter 服务器镜像，启动 jupyter 服务器

![image-20221009184442899](assets/image-20221009184442899.png)

构建 jupyter 服务器需要 20 分钟左右

构建完成后可以使用云服务器的 IP 登录 jupter 服务器

![image-20221009191746869](assets/image-20221009191746869.png)

运行训练，测试速度。

服务器训练速度：14s

![image-20221009191855774](assets/image-20221009191855774.png)

本地的训练速度（作为对比）：27s

![image-20221009191832799](assets/image-20221009191832799.png)

这个是小规模的网络，在大规模的网络下提速效果会更明显。

### 销毁服务器

关机仍然会继续计费，只有销毁服务器能够停止计费，销毁会清除所有数据，下一次创建服务器仍然需要从头开始安装环境。

![image-20221009192038030](assets/image-20221009192038030.png)

# 2022年10月11日

调试发现 WsWf 的读取存在问题，调整代码后结果如下：

![image-20221005135713824](assets/image-20221005135713824.png)

MatLab 和 Python 的算法处理结果基本一致，Kp0 和 Kd0 的值相近，还存在的问题是符号相反。

# 2022年10月12日

快速原型平台的设计总结：

![image-20221015220431014](assets/image-20221015220431014.png)

![image-20221015220438891](assets/image-20221015220438891.png)

![image-20221015220447971](assets/image-20221015220447971.png)

![image-20221015220452945](assets/image-20221015220452945.png)

![image-20221015220458761](assets/image-20221015220458761.png)

测试平台改进计划：

1. 测试台增加 WIFI 模块，实现远程回传数据。

2. 测试台支持定时自动测试脚本。

目前的进度：

1. WIFI 模块选型和基本的设计已经完成，崔世泽在负责设计和打样 WIFI 模块。

2. 测试台已经能够运行 Python 测试脚本：

``` python
#!pika
# create objects
sg = MET.SignalGenerator()
ps = MET.Process()
saoPin = MET.Scanner()

config = {
    'mode': 'normal',
    'is_use_Wp': False,
    'is_enable_saoPin': True,
    'is_reboot_after_saoPin': True,
}

# config Process
ps.setMode(config['mode'])
if config['is_use_Wp'] :
    ps.enableWp()
else:
    ps.disableWp()

if config['is_enable_saoPin']:
    saoPin.enable()

if config['is_reboot_after_saoPin']:
    saoPin.rebootAfterScanEnable()
    saoPin.setContinue(False)
    
# print config
print('[Config]:')
print(config)
print('Start Process')
saoPin.enable()

exit()
#!pika
```

后续可以通过 WIFI 定时下发测试脚本，然后批量回收数据，测试的各种配置也通过脚本下发，不需要重新编译烧录固件。

# 2022年10月13日

## Python 电化学算法的问题

在 Python 拟合时设置和 Matlab 一样的初值，就能够达到非常相近的计算结果了。

```python
popt, pcov = curve_fit(fit_fun, x, y, p0=[2e4, 3e3, 4e1])
```

![image-20221009205059422](assets/image-20221009205059422.png)

误差小于 0.2%，可以看作是完全一致的。

# 2022年10月17日

## 文献调研

[人工智能在计算机辅助设计中的应用建模和优化模拟计算和混合信号电路：一种革新( IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS 2021)](https://gitee.com/Lyon1998/pikascript/attach_files/1221392/download)

### 应用背景

AMS电路：模拟和混合信号电路设计

自动化AMS电路设计过程一直是具有挑战性的，因为它与人类的专业知识和直觉密切相关，使各种参数与性能之间的关系。在给定主电路拓扑的情况下，为了满足所需的规格，需要选择电路参数优化[10]。这个电路优化问题，也就是。确定电路的参数值满足所需的规格，可以用数学优化方法求解。因此，计算机辅助设计(CAD)工具将能够利用诸如基于梯度的、凸优化和进化算法[11]、[12]等技术自动实现电路尺寸优化过程。

AMS电路参数自动搜索的主要途径是确定的技术(如。线性1规划(LP)，凸非线性规划(NLP)，和非凸整数非线性编程（明利浦）[13]），颗粒群情报,模拟退火，进化算法和贝叶斯优化(BO)[14]-[17]。虽然每一种方法都有它的自己的优点，也有缺点。例如，粒子群算法的收敛速度较低，BO算法的运行时间较长。此外，退火很容易陷入局部极小值。此外，进化算法是随机的，缺乏再现性。

人工神经网络(ann)是AMS电路自动化设计的另一种很有前途的方法，它可以解决上述问题。

此外，人工智能算法和其他方法适用于产率估计和高阶模型的制作，可以代替复杂的物理模型，在AMS电路设计[19]-[21]中计算成本更低。此外，深度强化学习(DRL)可以解决一般[22]中的许多人类决策问题。此外，可以利用AI用一组更简单的度量来取代冗长和昂贵的度量，从而简化AMS生产测试[23]。

人工智能的主要挑战是要有一个精确的模型，为训练集提供健壮和足够的仿真数据，因为必须有高维变异空间来建模过程变异和昂贵的仿真AMS增长系统的大小。

布局是AMS设计的另一个重要组成部分，最近有很多关于AI在AMS布局设计中的应用的研究，[29]、[30]对这些研究进行了详细的综述。然而，本文主要关注人工智能方法在AMS电路设计建模和优化中的最新应用。在第二节介绍了人工智能的主要概念和技术之后，在第三节和第四节分别解释了人工智能在自动化AMS电路尺寸优化和性能建模中的最新技术。接下来，第五节讨论了主要挑战，并对未来的工作提出了一些想法。最后，在第六节对全文进行了总结。

### AMS 设计过程

首先确定电路拓扑[55]-[57]，然后优化相应的设计参数，如元件尺寸，最后生成布局[58]。在优化方面投入了大量的精力。

常规优化方法：

经典的AMS电路优化方法可分为

- 基于模型的方法(如几何规划、支持向量机、神经网络、高斯过程(GP)等[59]-[70])

- 基于仿真的方法(如模拟退火(SA)、粒子群优化(PSO)、EA和基于梯度的多起点局部搜索(MSP)， MSP收敛速度优于其他方法[15]，[71]-[81])

### 基于模型的方法

- 优点是模型的可重用性和低计算成本，特别是在使用电磁(EM)组件的情况下。
- 困难是设计参数数量较多，且目标和约束函数高度非线性，这些模型的精度通常不高。
- 基于在线模型的混合方法被提出用于模拟电路[82]、[83]以及毫米波和射频(RF)电路[84],[87]。这些混合方法在优化过程中进行仿真，以逐步更新在线模型，而不是使用预先构建的离线模型[88]-[90]。最初，模型是由从随机抽样中收集的数据构建的，它指导下一个点的选择，以实现更优化的性能。

### 基于神经网络的方法

基于神经网络的方法在传统的电路尺寸设计方法中，设计人员或EDA工具试图在迭代循环中找到电路参数，同时在每次迭代中使用模拟器来评估设计。为了避免耗时的模拟，一些研究[111]-[113]使用神经网络模型用近似模型替代和补充SPICE模拟器。他们在后期实现模拟器只是为了保持准确性。即使使用人工神经网络而不是仿真器节省了大量的时间，这种神经网络模型的训练集应该覆盖整个设计空间，这将消耗大量的时间大量的资源。另一方面，Lourenço等人[26]，如图4所示，训练一个ANN模型，根据给定的规格直接调整和优化电路，而不是多次调用模拟器。

![image-20221021093126458](assets/image-20221021093126458.png)

AMS电路尺寸的不同方法: a)传统的基于优化的尺寸(逆方法)，即在迭代循环中从设计变量到电路性能; b)人工神经网络(ann)(直接方法)，即从电路性能到设计变量[26]。

Lourenço等人[26]在选择神经网络超参数时考虑了以下考虑因素，

- 第一，为了有一个丰富的编码,每一层的节点数在第一层增加，然后向输出层减少。
- 为了找到一个不那么复杂的模型，最好在训练过程中设计一个低误差的模型，并使用L2正则化来补偿过拟合[114]。
- 第三，为了得到一个能给出最佳交叉验证分数的模型，需要对超参数空间进行探索。两种常用的方法是考虑指定超参数的所有组合的网格搜索和从具有指定分布的超参数空间中提取样本的随机搜索[115]。在他们的神经网络方法中，电路规格是给定的输入节点和输出节点决定电路的规模。

### 基于贝叶斯模型

融合的方法有一些应用贝叶斯的研究模型融合(BMF)[24]，[126]，[136]-[141]准确估算硅前验证和硅后验证电路性能的参数和统计分布。Wang等人[138]利用BMF的思想进行性能建模。BMF中的融合意味着通过信息作为先验知识，从简单的早期模型(如示意图级)到后期性能模型(如后布局)，以减少昂贵的后期建模成本。因此，BMF在使用模拟数据逼近早期性能模型后，为使用该早期模型的相同性能的后期模型生成样本点。然后将这些先验知识与极少的后期采样点结合，通过贝叶斯推理(Bayesian inference)求解后期模型系数[142]。因此，只需要少量的采样点就可以拟合高维后期模型。

### 半监督学习方法

上述所有方法都被归类为监督学习，因为它们只使用标记训练集。为了减少收集标记数据所需的工作量，一些研究已经转向半监督[52],[141]。使用这种方法是因为需要更少的标记数据来建立精确的模型。学习[21]，[24]，Alawieh等人[24]，[141]提出了贝叶斯联合学习分层绩效建模。之所以这么叫，是因为它们将整个电路划分为多个块，例如用于收发电路的低噪声放大器(LNA)、混合器等，并使用了共同学习的概念。在这种半监督学习方法中，可以以较低的计算成本对块级性能进行建模。

# 2022年10月24日

python 仿真模型可以成功导出处理好的数据：

![](assets/image-20221026192407559.png)

将需要保存的数据通过关键词参数构造数据对象

``` python
res = ResultData(H=H,
                 H0=H0,
                 H0h=H0h,
                 H0l=H0l,
                 Kd0=Kd0,
                 Kp0=Kp0,
                 Wa=wa,
                 Wf=wf,
                 Wfb=wfb,
                 Wfb0=Wfb0,
                 Wfb0_simply=Wfb0_simply,
                 Ws=ws,
                 WsWf=wswf)
```
数据对象的内部由 `_DictData` 类实现
``` python
class ResultData(_DictData):
    pass
```

`_DictData` 内部维护一个 dict，在构造函数中，使用 **kwargs 将关键词参数的入参截获，然后存储到内部 _dict

```python
class _DictData:
    _dict = {}

    def __init__(self, **kwargs):
        self._dict = kwargs

    def add(self, **kwargs):
        self._dict.update(kwargs)

    def todict(self):
        for (key, value) in self._dict.items():
            if isinstance(value, object):
                if hasattr(value, 'todict'):
                    self._dict[key] = value.todict()
        return self._dict

    def __getattr__(self, __name: str):
        return self._dict[__name]
```

`add` 方法支持后续添加 dict 的键值，`todict` 返回该对象的 dict，如果 dict 的成员值也有 `todict` 方法，那么递归地取其 dict 值。

`__getattr__` 方法支持数据劫持，可以通过 `obj.val` 形式的对象成员索引直接返回内部的 dict 键值，等效于 `obj._dict['val']`。

实验对象主类 `Exam` 的 `todict` 方法将需要导出的数据打包，并递归调用其 `todict()` 方法。

```python
class Exam:
    ...
	def todict(self):
    	return {
        	'res': self.res.todict(),
        	'par': self.par.todict(),
        	'config': self.config.todict()
    	}
	def save(self, dir='test/testout.json'):
        with open(dir, 'w') as f:
            json.dump(self.todict(), f)   
    ...
```

`save` 方法将 dict 数据结构转换为 json 数据并保存。

# 2022年10月27日

机器学习模型读取仿真模型生成的假数据

![image-20221027223649129](assets/image-20221027223649129.png)

![image-20221027223705527](assets/image-20221027223705527.png)

![image-20221027223719577](assets/image-20221027223719577.png)

![image-20221027223726998](assets/image-20221027223726998.png)

# 2022年11月1日

数字反馈电路-信号处理单元供电部分的改进：

![image-20221103152124217](assets/image-20221103152124217.png)

原电路由单个 AMS1117-3.3 将 +8V 电源转为 +3.3V 电源，压差过大，导致发热，新电路增加一级 AMS1117-5.0，先将 +8V 电源转为 +5V 电源，再转为 +3.3V 电源，将压差分散在两篇 LDO，解决发热问题。

另一方面，两级 LDO 进一步抑制了电源纹波。

![image-20221103152347286](assets/image-20221103152347286.png)

# 2022年11月3日 批量数据的生成

``` python
from metCore import exam_class
import seismic_ai
import numpy as np
```

使用 304 实测数据作为仿真基准，

```python
single_sheet = 304
exam = exam_class.Exam()
exam.config.get_data_from_xlsx = 1
exam.config.sheetList = [single_sheet]
exam.config.WfType = 1
exam.config.hand_data = single_sheet
exam.config.dataLength = 30
exam.config.isAutoDataLength = 0
exam.config.fitRange = range(5, 25)
exam.config.fl = 0.7
# 使用当前目录的 xlsx 文件作为数据源
exam.config.xlsxDir = 'main_data.xlsx'

T1 = 1 / 70
bet = 1 / 5 / T1
T2 = 1 / 50
alp = 1 / 200 / T1
exam.config.Wp = exam_class.System()
exam.config.Wp.T1 = T1
exam.config.Wp.bet = bet
exam.config.Wp.T2 = T2
exam.config.Wp.alp = alp
```

然后对传递函数的参数增加偏执，然后在范围内生成数据

``` python
def _do_process_save(exam, file_name):
    exam.process()
    exam.save(file_name)
A_k_range = np.arange(0.1, 10, 0.01)
B_k_range = np.arange(0.1, 10, 0.01)
C_k_range = np.arange(0.1, 10, 0.01)
i = 0
for A_k in A_k_range:
    for B_k in B_k_range:
        for C_k in C_k_range:
            exam.config.A_k = A_k
            exam.config.B_k = B_k
            exam.config.C_k = C_k
            i+=1
            print('正在处理第{}个数据..'.format(i))
            file_name = 'tmp/simu_{}.json'.format(i)
            _do_process_save(exam, file_name)
```

输出：生成到 26281个，然后 python 内核卡死了，可能是一次处理太多，内存不够

``` 
正在处理第40个数据..
正在处理第41个数据..
正在处理第42个数据..
正在处理第43个数据..
正在处理第44个数据..
正在处理第45个数据..
正在处理第46个数据..
...
正在处理第26278个数据..
正在处理第26279个数据..
正在处理第26280个数据..
正在处理第26281个数据..
Canceled future for execute_request message before replies were done
The Kernel crashed while executing code in the the current cell or a previous cell. Please review the code in the cell(s) to identify a possible cause of the failure. Click here for more info. View Jupyter log for further details.
```

生成成功的数据：

![image-20221104160826374](assets/image-20221104160826374.png)

# 2022年11月7日

## 加速数据生成

之前生成 2.6 万份数据用了 70 分钟，速度较慢，而且存在失败的情况，需要提高生成速度。

分析后发现性能瓶颈在于读取 excel 数据，因此在数据读取部分加入缓存机制。

```python
@classmethod
def fromXlsx(
        cls,
        xlsx_dir,
        sheetList,
        isAutoDataLength,
        dataLengh):
    if hasattr(cls, 'data_cache'):
        return cls.data_cache
    data = ExamData()
    data.loadXlsm(xlsx_dir, sheetList)
    dataStandard = data.standardize()
    data = data.cut(
        dataStandard, dataLengh, isAutoDataLength)
    cls.data_cache = data
    return data
```

将 `fromXlsx()` 方法改为类方法，起到单例的效果，使得所有对象共享 `class` 数据区，然后 `hasattr()` 判断是否已经在 `class` 数据区缓存了数据，如果没有缓存，则磁盘读取 excel, 然后 `cls.data_cache = data` 缓存进 `class` 数据区。

优化后2.6 万份数据的用时 为 2 分钟，提高了 35 倍。

![image-20221110125325199](assets/image-20221110125325199.png)

## 断点继续生成

任务目标是 97 万份数据，为避免意外终止需要重新生成，在数据生成时加入断点继续的机制：

``` python
def _do_process_save(exam, file_name):
    if os.path.exists(file_name):
        return
    exam.process()
    exam.save(file_name)
```

当数据文件已经存在时，直接 `return` 跳过，从未开始生成的文件开始。

这个方法需要保证数据文件命名在不同的任务中具有一致性，使用自增 ID 确保。

``` python
for A_k in A_k_range:
    for B_k in B_k_range:
        for C_k in C_k_range:
            exam.config.A_k = A_k
            exam.config.B_k = B_k
            exam.config.C_k = C_k
            i+=1
            if i % 1000 == 0:
                print(f'{i}: [{A_k}, {B_k}, {C_k}]')
            file_name = 'tmp/simu_{}.json'.format(i)
```

每份数据 `i+=1`，起到自增 ID 的效果，生成的数据文件名为 `tmp/simu_{id}.json`。

最后生成了 97 万份数据， 用时 60 分钟左右。

![image-20221110212839579](assets/image-20221110212839579.png)

生成的数据有 23G。

``` shell
/tf/seismic-ai/application/6.Generate_batch_data (master) # du -h tmp
23G     tmp
```

# 2022年11月11日

制作了绘图工具库，对生成的数据进行抽样绘图

![image-20221125103530036](assets/image-20221125103530036.png)

![image-20221125103542679](assets/image-20221125103542679.png)

![image-20221125103547281](assets/image-20221125103547281.png)

![image-20221125103608149](assets/image-20221125103608149.png)

![image-20221125103559184](assets/image-20221125103559184.png)



# 2022年11月16日

## 文献查阅

### The Electrochemical Seismometer Based on Fine-Tune Sensing Electrodes for Undersea Exploration (2020)

《基于微调传感电极的电化学地震仪在海底勘探中的应用》

这篇文章讲了整个传感器的制作，其中有一个小结讲了力平衡反馈

>### C. The Negative Force-Balanced Feedback System
>
>To expand the working bandwidth, the negative force-balanced feedback systems are necessary to function the closed loop processes. An effective negative feedback system based on electromagnetic induction principle was introduced in [17], and the system composition illustrated in figure 1(a). The feedback force produced by coil applied to the movable frame, which conducts an opposite movement relative to input velocity, and then the feedback velocity acts on the liquid mass through the membranes which attach to the moveable frame finally.
>
>The signal conditional circuits He(s) are mainly functioned to compensate and eliminate the poles, which expand the potential bandwidth after feedback. Another function of signal conditional circuit is signal amplification and its was limited by the noise level.
>
>The transfer function of the closed loop can describe as:
>
>![image-20221116151632794](assets/image-20221116151632794.png)
>
>In [(5)](https://ieeexplore.ieee.org/document/#deqn5), the Uo(s) is the output voltage and the vin(s) is the input velocity. The H1(s) describes the open loop transfer function of seismometer. The HCO(s) stands for the process of coil function and can be simplified as kco/s, in which the constant kco featured as the transfer coefficient from feedback voltage to feedback velocity, in order to keep the stability of the system, the feedback circuit Hf(s) is better to be kf⋅s among the working bandwidth. The final transfer function of close-loop can be simplified as:
>
>![image-20221116151659604](assets/image-20221116151659604.png)

该文使用的反馈模型较为简单，直接取深度负反馈时的结果。该文指出了线圈的传递函数为 `Kco/s` ，和已发表的自整定论文一致，反馈网络的传递函数为 `Kf * s` ，只包含 `Kd` 反馈的部分。

### Temperature Compensation of the MEMS-Based Electrochemical Seismic Sensors（2021）

《基于MEMS的电化学地震传感器的温度补偿》

- 温度对电化学地震传感器的影响：电化学地震传感器的性能受周围温度的影响很大。对于液体环境，电解质中离子的对流和扩散受温度的影响。此外，电化学反应速率也与温度有关，提供弹性力的弹性膜的弹性系数也受到温度的严重影响。因此，当电化学地震传感器在温度变化很大的恶劣环境中工作时，设备的性能会下降。
- 关于温度影响的研究：莫斯科物理与技术学院的Dmitry A. Chikishev研究了温度对传感器幅频特性的影响[[13](https://www.mdpi.com/2072-666X/12/4/387/htm#B13-micromachines-12-00387)]。在他们的工作中，在0.1 Hz ~ 443 Hz的频率范围内，在-15 °C / -35 °C ~ + 70 °C的温度范围内，测试了开环灵敏度。结果发现，灵敏度随温度变化了几个数量级。数据处理结果表明，开环灵敏度曲线的特征频率值与温度倒数呈指数关系。他们还验证了温度对电解质粘度的影响。然而，他们的工作没有提出有效的温度补偿方法，也没有研究较低频率的温度特性。吉林大学林军对MTLS10电化学地震传感器进行了温度补偿研究[[14](https://www.mdpi.com/2072-666X/12/4/387/htm#B14-micromachines-12-00387)]。他们的研究测试了10°C~45°C温度范围的灵敏度曲线，并开发了温度系数模型，通过数学模型校正了温度敏感性。但该模型在0.1 Hz频率以下校正效果较差，无法实现实时补偿。
- 文章亮点：1. 实时温度补偿， 2. 灵敏度变化从 25dB 降低至 2dB

文中先是使用了传递函数的物理+经验公式进行拟合：

> ![image-20221116162615275](assets/image-20221116162615275.png)

拟合结果：

> ![image-20221116154701381](assets/image-20221116154701381.png)
>
> The fitting results are shown in [Figure 2](https://www.mdpi.com/2072-666X/12/4/387/htm#fig_body_display_micromachines-12-00387-f002). The fitting results of high frequency were poor, but the trends were consistent.

该文也指出，物理+经验公式的传递函数拟合方法在高频处效果不好。

受温度影响的开环闭环曲线实测图：

>![image-20221116154838554](assets/image-20221116154838554.png)
>
>The sensitivities of the sensor increased with the increase of the surrounding temperature in a non-linear manner.

随温度升高，开环传递函数会 **非线性** 地增加，闭环传递函数受影响没有开环的明显，但在40°时出现了共振点。

- 改进的拟合方式

> ![image-20221116162136863](assets/image-20221116162136863.png)
>
> In order to further analyze the influence of temperature on open-loop sensitivities, the open-loop sensitivity curves were fitted through typical elements.

文中使用 typical elements 拟合方式，通过分析频率域的图像特征，给出了拟合的公式：

> ![image-20221116162419980](assets/image-20221116162419980.png)

评：这种拟合方法仅依照频率特性的表象，脱离了对系统物理特性的分析，变成了纯粹经验公式。该拟合公式的没有物理根据，对具有不同固有频率和在不同温度下的电化学反应腔的趋近能力没有保障，仅适用于特殊情况，不具有普遍性。

### Effect of temperature on the performance of electrochemical seismic sensor and the compensation method

《温度对电化学地震传感器性能的影响及补偿方法》

亮点：

- 建立了温度漂移传递函数模型

- 使用补偿公式进行后矫正



# 2022年12月21日

下一步计划：

1. 完成反馈参数 -> 闭环传递函数的“正演算法”
1. 对闭环传递函数进行评价

2. 建立温度 -> 开环传递函数的模型

# 2023年2月15日

训练的总体思路

![IMG_20230215_150202](assets/IMG_20230215_150202.jpg)

![IMG_20230215_150210](assets/IMG_20230215_150210.jpg)

![IMG_20230215_150219](assets/IMG_20230215_150219.jpg)·


# 2023年3月28日

## 工作进度汇报

### 一、背景

在项目中，我们需要对高频信号进行滤波处理。滤波器的设计需要考虑滤波器类型（低通、高通、带通等）和截止频率等参数。为了实现这一需求，我们决定采用`SOS`（Second-Order Sections）滤波器。在本次任务中，我们编写了一个Python工具，用于生成SOS滤波器的参数，并验证了其性能。以下是本次工作的详细过程和结果。

### 二、需求分析

生成`SOS`滤波器的参数，包括滤波器类型、截止频率、阶数和采样频率。
将生成的参数转换为C语言中的`SOS`结构体。
验证滤波器的性能，包括幅频特性曲线。
将生成的参数和性能曲线保存为文件。

### 三、程序设计

我们首先实现了一个名为`create_sos`的函数，该函数根据输入的滤波器类型、截止频率、阶数和采样频率生成`SOS`滤波器的参数。此函数使用了`scipy.signal.butter`函数来生成滤波器参数。

为了验证滤波器的性能，我们实现了一个名为`plot_sos_frequency_response`的函数。该函数根据生成的`SOS`滤波器参数计算幅频特性曲线，并使用`matplotlib`库绘制曲线。我们还实现了一个名为`save_sos_to_file`的函数，用于将生成的滤波器参数保存为文件。

![image-20230329103047905](assets/image-20230329103047905.png)

最后，我们将这些功能整合到一个命令行工具中，用户可以通过命令行参数来指定滤波器的类型、截止频率、阶数和采样频率。工具会生成相应的滤波器参数、C语言结构体和幅频特性曲线，并将它们保存到文件中。

![image-20230329103259315](assets/image-20230329103259315.png)

### 四、测试与优化

在编写程序的过程中，我们遇到了一些问题，例如生成滤波器参数时，当滤波器类型为带通滤波器时，需要提供两个截止频率。为了解决这个问题，我们对`create_sos`函数进行了相应的修改。

另一个问题是生成的`SOS`结构体与预期不符。为了解决这个问题，我们重新审查了代码，并对生成`SOS`结构体的部分进行了调整。

我们还对代码进行了一些优化，例如添加了类型提示（type hint），以提高代码的可读性。此外，我们还对程序进行了测试，确保其在不同类型的滤波器和参数下都能正常工作。

在测试过程中，我们遇到了一个关于`divide by zero encountered in log10`的警告。经过分析，我们发现这是因为在计算幅频特性曲线时，有些频率处的信号强度接近于零，导致计算出的分贝值出现负无穷大。为了解决这个问题，我们对`plot_sos_frequency_response`函数进行了修改，确保在计算分贝值时不会出现除以零的情况。

## SOS滤波器C语言模块

我们已经成功地实现了一个SOS滤波器C语言模块（sos_filter.c 和 sos_filter.h），该模块包括用于处理滤波器的相关函数。通过该模块，用户可以在C环境下方便地应用SOS滤波器来处理信号。

该模块实现了以下功能：

- 创建滤波器：用户可以通过提供SOS系数矩阵和滤波器阶数来创建一个SOSFilter对象。此对象包含了滤波器的所有信息，包括系数矩阵和滤波器状态。对应函数为sos_create(float* sos_coefficients, int num_sections)。

  ![image-20230329103322857](assets/image-20230329103322857.png)

- 滤波操作：用户可以将输入信号送入滤波器进行处理。该模块提供了一个函数sos_filter(SOSFilter* filter, float input)，用于处理输入信号并输出滤波后的结果。

  ![image-20230329103342301](assets/image-20230329103342301.png)

- 销毁滤波器：当滤波器不再需要时，用户可以使用sos_destroy(SOSFilter* filter)函数释放其所占用的资源。

  ![image-20230329103353033](assets/image-20230329103353033.png)

示例代码已经包含在模块的注释中，展示了如何创建滤波器、处理信号以及销毁滤波器的过程。

请注意，此模块不提供SOS滤波器系数的计算。用户可以使用其他工具（如Python的SciPy库）计算滤波器的SOS系数。

# 2023年3月29日

## 科研进度汇报

### 1. 自动生成滤波器C语言初始化函数
我们开发了一个Python脚本，可以自动生成指定类型、截止频率、阶数和采样率的滤波器C语言初始化函数。该脚本会生成一个C头文件（.h），包含创建滤波器所需的函数。这些函数可以用于初始化滤波器并返回一个SOSFilter对象。具体来说，根据滤波器的类型、截止频率、阶数和采样率参数，使用SciPy库的设计SOS滤波器函数生成SOS矩阵，然后将这些参数和SOS矩阵存储到一个头文件中。头文件的命名格式和函数名都经过优化，避免使用不合法的字符，确保可以在C代码中直接使用。

![image-20230329103424919](assets/image-20230329103424919.png)

### 2. 优化幅频特性绘图

为了更好地展示滤波器的性能，我们优化了幅频特性绘图功能。在新的实现中，我们根据滤波器类型和截止频率，自动调整了图像的显示范围。对于带通滤波器，我们将频率轴的范围设置为截止频率附近的一个对数区间；对于其他类型的滤波器，我们将频率轴的范围设置为截止频率附近的一个对数区间，但限制在0.01Hz至500Hz之间。同时，我们也调整了幅度轴的显示范围，使其聚焦在截止频率附近的幅值。

此外，我们在图像中用红色竖线标注了实际的截止频率，并在图像上显示了具体数值。同时，我们还在图像中添加了一个文本框，用于显示滤波器的关键参数，如滤波器类型、截止频率、阶数和采样率等。文本框的背景设置为不透明，以便阅读。最后，我们将频率轴设置为对数坐标，以便更直观地展示滤波器的频率特性。

![image-20230329103017132](assets/image-20230329103017132.png)

以上这些优化使得幅频特性绘图功能更加实用和直观，有助于更好地评估滤波器的性能。

# 2023年4月3日

## 实验背景

为了进行力平衡反馈的模拟电路全过程仿真实验，需要包含传感器和力反馈器（线圈）的传递函数。为了在Multisim中进行仿真，我们需要使用运放网络对传感器和力反馈器的传递函数进行模拟，从而实现力平衡闭环的仿真。

## 实验目的

1. 使用微分电路与二阶低通滤波器模拟传感器传递函数：H(s) = A * s / (s^2 + s * C + B)
2. 通过A, B, C求解模拟传感器所需的电阻和电容值

## 数据来源

A、B、C是实测数据的拟合结果，通过实验获得的传感器数据来拟合得到这些参数。

## 实验方法

1. 首先，我们根据给定的传递函数 H(s) = A * s / (s^2 + s * C + B) 设计了一个微分电路和二阶低通滤波器。

   Sallen-Key 二阶低通滤波器：

   ![image-20230403163719571](assets/image-20230403163719571.png)

   ![image-20230403163731374](assets/image-20230403163731374.png)

2. 为了简化问题，我们假定了一些电阻值，例如 R_39 = 10kΩ，R_42 = 10kΩ，R_43 = 10kΩ。

3. 接下来，我们使用Python的SymPy库根据给定的A, B, C值求解了模拟传感器所需的电阻和电容值。

   ![25e4a93f566e2ae0586263098f1b00f](assets/25e4a93f566e2ae0586263098f1b00f.jpg)

   代码在 /tools/ABC_to_simu_pars.py

4. 通过求解，我们得到了以下电阻和电容值：

   - R_39: 10.0 kΩ
   - R_42: 10.0 kΩ
   - R_43: 10.0 kΩ
   - C_14: 7.75169705639763 µF
   - C_15: 213.111050836627 nF
   - C_16: 121.119996608640 pF

5. 根据求解出的电阻和电容值，我们搭建了相应的电路，并测试了其性能。

   ![image-20230403162653406](assets/image-20230403162653406.png)

## 图像结果

![image-20230403162856308](assets/image-20230403162856308.png)

## 实验结论

通过本次实验，我们成功地设计并搭建了一个模拟传感器，使其传递函数满足 H(s) = A * s / (s^2 + s * C + B)。实验结果表明，所求得的电阻和电容值能够有效地实现预期的传递函数性能。我们通过观察图像结果进一步验证了电路的性能。本实验为我们在实际应用中设计类似的传感器以及力平衡反馈仿真提供了宝贵的经验。

## 闭环仿真结果

![image-20230403202657335](assets/image-20230403202657335.png)

仿真出现过很异常无法解释的图像，都是因为运放同向输入端没有接地导致的，仿真的时候同向输入端一定要接地。

# 2023-4-4

数字反馈电路板需要修改的问题：

- 安装孔的间距偏小，要使用游标卡尺测量精确的实际孔间距（所有部分）
- 二极管的位置影响安装（电源-放大部分）
- 排针要换成1.27MM间距的
- 数字板需要引出3V3的电源来连接JLINK，JLINK的连接可以保持2.54MM间距，因为工作中不会连接JLINK。

模拟反馈板的设计：

- 模拟反馈板直接兼容（电源-放大部分），新版都采用1.27MM间距排针，为了兼容2.54MM间距的旧版，还需要打一个1.27 <---> 2.54 的转接板。

- 模拟反馈板需要有测试信号的输入端，叠加到线圈驱动信号上，测试信号的输入端要进行下拉，确保悬空时不会引入噪声。

- 数字反馈板要能够直接插在模拟反馈板上，使用数字反馈板施加测试信号，对系统的开闭环传递函数进行测试。

## 引入拟合参数 --> 等效电路参数的计算

数据处理流程改进，在处理实验数据时，将反映腔的拟合参数以及等效电路的参数进行计算和导出。

# 2023年12月14日

俄罗斯反应腔+自制电路板会出现类似一边电极断开的波形现象，更换了反应腔后仍然有相同情况，可能需要根据俄罗斯反应腔修改最前端的电流-电压放大级。

![image-20231214164119869](assets/image-20231214164119869.png)

在测试结果的表现为THD很高（波形不够正弦）

![image-20231214164446569](assets/image-20231214164446569.png)

![image-20231214164455465](assets/image-20231214164455465.png)

![image-20231214164505708](assets/image-20231214164505708.png)

有一个明显的不同是偏置给的不一样，而且没有接R4这个电阻，多了RZ25这个电阻（这个或许影响不大）

先将R1换成100K，然后将R4短接

# 2023年12月15日

电流转电压级的噪声问题

![686de704e71b381131949b0e6a483ca](assets/686de704e71b381131949b0e6a483ca.png)

![29eadc1b01ac92fae384dabf60bb0aa](assets/29eadc1b01ac92fae384dabf60bb0aa.png)

![b65a0231b42d324a3c5eb0a25b5151f](assets/b65a0231b42d324a3c5eb0a25b5151f.png)

（2024年3月5日补）最后解决底噪的方法是堆叠电容：

![image-20240305103513992](assets/image-20240305103513992.png)

![image-20240305103151827](assets/image-20240305103151827.png)

# 2023年12月28日

可以加载calibaration_analyzer格式的数据了，拟合效果很好。

fl=0.7

![image-20231228154609927](assets/image-20231228154609927.png)

fl=1

![image-20231228155300639](assets/image-20231228155300639.png)

但是目前数据是带有校正系数 65 * 20 的，会对 kp、kd的计算产生影响。

反馈参数是和 Ka 成正比的：

![image-20231228161129040](assets/image-20231228161129040.png)

所以这个 Ka 需要进行正确的测定

对俄罗斯MET进行闭环试验：

10Hz 开环 gain 689 H0 gain 254

开环 3.7V（Vpp） 闭环期望 1.36V 此时 kd = -0.045

实际调出的开环/闭环对比：

![image-20231228171118308](assets/image-20231228171118308.png)

![image-20231228185308060](assets/image-20231228185308060.png)

![image-20231228185340564](assets/image-20231228185340564.png)

截止频率1Hz和截止频率0.5Hz时的Kd方向不一致，应该是计算存在问题。

查之前的记录，拟合的效果都近似，仅仅是数值不一样，就会有很不一样的结果：

![image-20231228193402363](assets/image-20231228193402363.png)

![image-20231228193506593](assets/image-20231228193506593.png)

拟合效果几乎一致，但是仅仅是初值不同，还是有很大差异

可能是，在趋近其他位置时有问题，也可能是存在多解，但有些解是无效的

（例如低频处和高频处）

要先把闭环仿真跑起来，验证解的有效性，然后再分析出现无效解的原因

# 2023年12月29日

验证数值解：

![image-20231229154823792](assets/image-20231229154823792.png)

对比Wfb的数值解和解析解（简化后），发现数值解和解析解有很大区别：

![image-20231229161131391](assets/image-20231229161131391.png)

解析解的简化是建立在可以用kp，kd，即0阶和1阶微分来代替原传递函数的情况，根据目前的结果分析，应该是还需要更高阶，如kd2、kd3项，才能满足wfb的数值解的要求。

# 2023年12月29日



# 设计情况和校正效果总结



## 温度漂移校正思路

目前的思路是先将之前的校正系数计算方法进行仿真和实验验证，然后编写基于机器学习的迭代法方法，最后进行性能指标对比。

迭代法的设计思路：

1. 迭代法的核心是调整反馈系数向量 kp，kd 和增益倍率 g，通过神经网络（NN）计算这些参数的变化。NN根据当前和期望的闭环传递函数、当前参数和自身的权重和偏置来进行计算。

2. 数据来源方面，开环测试提供了MET的传递函数和温度之间关系的初始数据集，包含不同温度下的开环传递函数测量值，用于模型训练和验证。

3. 为了提高模型的泛化能力，采用了数据增广方法，通过对MET传递函数的拟合参数增加偏置来模拟不同特性的MET检波器。这使得模型能够适应具有不同固有特性的MET检波器。

最后，优化目标是调整NN的参数，以在最少的迭代次数内，使MET的闭环传递函数达到期望传递函数的预定精度。

## 程序设计情况和校正结果

- 对俄罗斯反映腔 + 自制电路板进行了闭环实验（反馈系数先是手调的，没有精调）

![image-20231228171118308](assets/image-20231228171118308.png)

​	验证了反馈系统可以正常工作，从结果看，通频段比较平坦，低频有些高，从以往的经验看，增加 Kp 的值可以将低频的部分压低。高频的截止频率不是很高，这和前置电路的设计有关系。

- 成功加载了新的自测试的格式的数据，跑通了拟合程序和反馈系数自动计算的程序，拟合效果良好。对于不同的`fl`值（0.7和1）的拟合效果：

  `fl=0.7` 的拟合效果：
  ![image-20231228154609927](assets/image-20231228154609927.png)

  `fl=1` 的拟合效果：
  ![image-20231228155300639](assets/image-20231228155300639.png)
  



## 遇到的问题

- 对俄罗斯MET的测试结果运行反馈参数自动校正程序时，发现不同截止频率下`Kd`方向不一致，可能存在计算问题。这一现象在以下图形中得到体现：


  ![image-20231228185308060](assets/image-20231228185308060.png)
  ![image-20231228185340564](assets/image-20231228185340564.png)

- 不同拟合结果显示，即使拟合效果相近，不同初始值也会导致结果有较大差异。这一点从以下拟合结果中可以看出：

  ![image-20231228193402363](assets/image-20231228193402363.png)
  ![image-20231228193506593](assets/image-20231228193506593.png)

  对反馈参数的计算过程进行了检查，发现主要可能存在问题的地方是对反馈环节进行了简化（去掉了2阶及以上的部分）

  ![image-20231228161129040](assets/image-20231228161129040.png)

  对比了简化之前和简化之后的wfb计算结果：
  ![image-20231229161131391](assets/image-20231229161131391.png)

  从结果上看，简化后的结果和简化前不能很好对应，这说明了之前的简化计算方式仅在某些情况下是有效的，在其他情况下（主要以更高阶数项主导）的情况下是效果不好的。

## 下一步解决方案

- 运行闭环仿真，验证解的有效性。

- 分析无效解的原因，特别是在处理低频和高频处的问题。

- 目前有两种解决思路

  1. 考虑引入更高阶项（如`kd2`、`kd3`），以满足`wfb`的数值解要求。但这会导致电路的实现困难。

  2. 改进简化的方法，使其能够和简化前的对应关系更好。

- 跑通闭环仿真，然后按照基于机器学习的迭代法思路设计程序。

# 2024年1月3日

闭环反正可能存在问题，仿真了简化前和简化后的闭环传递函数，简化前的闭环传递函数应当能够和h0严格对应才是正确的：

![1704285917214](assets/1704285917214.jpg)

# 2024年1月8日

![image-20240108092247381](assets/image-20240108092247381.png)

Wfb0 采用 number 计算和采用 abs 的计算结果有不同，number 计算结果：

![image-20240108092422131](assets/image-20240108092422131.png)



![1704285917214](assets/1704285917214.jpg)

abs 的计算结果：

![image-20240108092613221](assets/image-20240108092613221.png)

![image-20240108092621902](assets/image-20240108092621902.png)

可以看到使用 number 计算的闭环仿真不能和 h0 对应上，而使用 abs 的仿真可以。

理论上说，使用 number 仿真（拉普拉斯变换的复数形式）是应该可以同时仿真出 abs 和 phase 的。

下面应该改进计算方式，统一使用拉普拉斯变换的方式计算，然后再由拉普拉斯变换导出幅频特性和相频特性。

修改代码，一律使用 number 进行仿真得到的效果：

![image-20240108105457409](assets/image-20240108105457409.png)

![image-20240108105658945](assets/image-20240108105658945.png)

检查ws的拟合部分：

拟合时用的是幅度的表达式：

![image-20240108110046339](assets/image-20240108110046339.png)

拟合后还原时用的是传递函数的表达式

![image-20240108110024857](assets/image-20240108110024857.png)

尝试将拟合时用的也一律统一为传递函数表达式：

![image-20240108110712967](assets/image-20240108110712967.png)

更换后的效果还是和之前一样。

如果把 kp、kd 手动调整一个系数，可以得到比较好的仿真结果：

![image-20240108160049536](assets/image-20240108160049536.png)

![image-20240108160100041](assets/image-20240108160100041.png)

关于kd的符号问题，经过检查是打印错误，kp、kd在打印时调换了，修复后，kd一直为正，这是符合预期的，kp有时为正，有时为负，这是因为kp起到了调整闭环传递函数的阻尼系数的作用，为正时降增加阻尼，为负时降低阻尼。

下面应该研究手动调整的这个系数对应的物理意义，并且给出直接计算这个系数的方法。（这个系数和应该和测量系统和反馈控制的放大倍数有关，即AD、DA及其信号调理电路）。

![image-20240108161919168](assets/image-20240108161919168.png)

![image-20240108161926037](assets/image-20240108161926037.png)

![image-20240108161946075](assets/image-20240108161946075.png)

![image-20240108161953593](assets/image-20240108161953593.png)

Ka的结果不会影响闭环仿真的结果，虽然Kp、Kd发生了变化，但是因为闭环仿真中也用到了Ka，实际上Ka在闭环仿真中又将其引起的Kp、Kd的变化给抵消了。

![image-20240109100924944](assets/image-20240109100924944.png)

尝试去除增益调整，对与仿真结果没有影响。

![image-20240109101523124](assets/image-20240109101523124.png)

分析 wfb0 和 wfb0_simply，对比wfb0和wfb0_simply可以发现，除了高频部分外，斜率是近似的。可以发现这个0.16的系数是差在了 simply 简化的步骤。

计算了wfb0_pars（基于完整的解析式计算得出的结果）

![image-20240109104551549](assets/image-20240109104551549.png)

# 2024年1月9日

用同样的数据对比matlab的结果：

![image-20240109152102030](assets/image-20240109152102030.png)

![image-20240109152107645](assets/image-20240109152107645.png)

matlab 中的 wfb、wfb0、wfb_simply 的一致性更好

matlab 计算的 kp0、kd0 （-0.0055, 0.0025）和 python 计算的 kp0、kd0 （-0.0057, 0.00245) 是近似的，但是 wfb 、wfb0 和 wfb0 simply 是很不一致的。

应该确保拟合结果完全一致，然后对比其余的数据处理过程。目前看很可能是仿真的问题，而不是反馈网络的计算问题。

![image-20240109161417923](assets/image-20240109161417923.png)

将 python 拟合的参数直接赋值给 matlab 的计算程序：

![image-20240109162713840](assets/image-20240109162713840.png)

![image-20240109162727565](assets/image-20240109162727565.png)

结果kp0、kp0的值和 python 计算的是完全一致的，说明解析解的计算式完全等效的。

对比 Wfb0 的计算结果（复数）：

![image-20240109182838012](assets/image-20240109182838012.png)

![image-20240109183025175](assets/image-20240109183025175.png)

计算结果有较大差异。

h0 对比，h0 是一致的



![image-20240109183053489](assets/image-20240109183053489.png)

![image-20240109183121791](assets/image-20240109183121791.png)

Ws 对比，Ws 一致

![image-20240109183425367](assets/image-20240109183425367.png)

![image-20240109183232089](assets/image-20240109183232089.png)

Wf 对比，Wf 是一致的

![image-20240109183531905](assets/image-20240109183531905.png)

![image-20240109183557407](assets/image-20240109183557407.png)

Wa 对比，Wa 有明显差异

![image-20240109183626859](assets/image-20240109183626859.png)

![image-20240109183644776](assets/image-20240109183644776.png)

Wa 的计算公式存在问题（频率和角频率的转换），修复后：

![image-20240109184147826](assets/image-20240109184147826.png)

修复后重新进行仿真计算，wfb0_simply和wfb0 wfb0_pars 的近似关系较好。

![image-20240109184223973](assets/image-20240109184223973.png)

闭环仿真结果符合预期

![image-20240109184311504](assets/image-20240109184311504.png)

![image-20240109184216516](assets/image-20240109184216516.png)

下一步要验证一组仿真和实际测试的效果差异，如果效果较为一致，可以进行批量的仿真（包含温度特性），在完成批量的仿真之后，再进行更广泛的多组试验验证。

# 2024年1月10日

电路板听到有异常响动，只保留电源、前放板无声音，测量线圈两端150欧，去掉LM7322后无声音，可能是LM7322过流烧掉了。

测量结果应该去除增益调整的影响（这个增益调整是和激振器对比得到的调整系数）：

![image-20240109202809630](assets/image-20240109202809630.png)

去除后的kp0、kd0：

![image-20240109202852072](assets/image-20240109202852072.png)

实际的闭环反馈效果（只加kd不加kp的结果）：

![image-20240110102011448](assets/image-20240110102011448.png)

和仿真的闭环传递函数近似。

![image-20240110141112066](assets/image-20240110141112066.png)

橙色是加了KP的效果，但是因为和上一次测试相比，额外通电了一个晚上，因此重新测试不带kp的结果。

![image-20240110145439609](assets/image-20240110145439609.png)

可以看到Kp的加入使得低频部分有稍微往上抬的作用，这是符合仿真结果的。

# 2024年1月10日

下一步对所有温度下的测试数据进行批量仿真：

![image-20240110164104787](assets/image-20240110164104787.png)

![image-20240110164111463](assets/image-20240110164111463.png)

![image-20240110164119920](assets/image-20240110164119920.png)

![image-20240110164130106](assets/image-20240110164130106.png)

![image-20240110164148119](assets/image-20240110164148119.png)

![image-20240110164155182](assets/image-20240110164155182.png)

![image-20240110164205908](assets/image-20240110164205908.png)

![image-20240110164220895](assets/image-20240110164220895.png)

从-10°到50°的数据进行了仿真，总体效果符合预期，但-10°和接近55°的拟合效果相较于中间的温度效果有所下降。

# 2024年1月12日

对测试结果进行检查，确定测量的可靠性： 

![99e3f6bad839bafc426f794e7610da4](assets/99e3f6bad839bafc426f794e7610da4.png)

抽取了7.27Hz这个点，可以看到数据是较标准的正弦波，没有出现饱和、截至等问题，可以认为测量数据是可靠的。

![0f4f04fc276a31329e0e029985e4b82](assets/0f4f04fc276a31329e0e029985e4b82.png)

准备基于热敏电阻的补偿方法的测试，分析俄罗斯的电路图，热敏电阻是 RZT1 和 RZT2

![48f46a26ea187f9baa8909ec1c2bfa1](assets/48f46a26ea187f9baa8909ec1c2bfa1.png)

![9dd493eefcb7ce00eb1c2f82ba3a94d](assets/9dd493eefcb7ce00eb1c2f82ba3a94d.png)

分析自制的电路图前端，对应的是 R6 和R7

![a84a641e8c36d6750661459e006195a](assets/a84a641e8c36d6750661459e006195a.png)

把R6和R7换成RTZ1和RTZ2

![60c8a108b52480eb2ff687893773601](assets/60c8a108b52480eb2ff687893773601.png)

![5244f34aa6cadaf1d8eea1350f4aefa](assets/5244f34aa6cadaf1d8eea1350f4aefa.jpg)

![e62a9da10beb356ac2cce796ff8ce74](assets/e62a9da10beb356ac2cce796ff8ce74.jpg)

常温测试热敏电阻为1.58K，1.69K

# 2024年1月13日

带温度补偿的各个温度闭环测试结果：

![c2d3391d48c4162e791309530c97369](assets/c2d3391d48c4162e791309530c97369.png)

# 2024年1月15日

低频截止频率和温度的关系（校准后）

![image-20240114155854776](assets/image-20240114155854776.png)

this method (simu) 是当前的方法的结果（仿真），reference method 是使用热敏电阻补偿的方法。

整理绘图的格式，使用 scienceplot 进行绘图风格的调整：

``` python
import scienceplots
# Set the plotting style
plt.style.use(['science', 'ieee'])
```


![image-20240116104921158](assets/image-20240116104921158.png)

![image-20240116104940183](assets/image-20240116104940183.png)

做了高频截止频率的数据分析对比：

![image-20240116105118856](assets/image-20240116105118856.png)

从数据上看，本方法和参考方法的高频截止频率都会受到影响。考虑本方法在闭环后再增加一个串联环节来进行补偿，将高频截止频率补偿到接近一致。

考虑对高频截止频率进行拟合(将拟合的频率范围限定在(3-200Hz）：

拟合结果：

![b8b9a9d57e5aa1a54fcc99f14859510](assets/b8b9a9d57e5aa1a54fcc99f14859510.png)

观察拟合结果的相位特性，发现和实际的相位特性有较大的不同

![image-20240116105453015](assets/image-20240116105453015.png)

# 2024年1月16日

改进拟合方法，在损失函数中考虑相位特性：

```python
def loss(params, k=1):
    A, omega_n, zeta = params
    predicted_gain = second_order_system(A, omega_n, zeta, freq_filtered)
    predicted_phase = calculate_phase(A, omega_n, zeta, freq_filtered)
    return k * np.mean((gain_filtered - predicted_gain)**2) + (1-k) * np.mean((phase[mask] - predicted_phase)**2)
```

通过权衡因子 k 来控制幅度因素和相位因素在损失函数中的权重，k=0.9 时：

![image-20240116110828662](assets/image-20240116110828662.png)

![image-20240116110841332](assets/image-20240116110841332.png)

根据两个参数的物理意义来设置初值：

1. **固有频率 `omega_n`**：这是一个系统在没有阻尼的情况下自然振动的频率。物理上，频率不能是负的，因为它代表每秒振动的次数。因此，如果拟合得到的 `omega_n` 是负数，这通常意味着拟合是不正确的。
2. **阻尼比 `zeta`**：阻尼比描述了系统阻尼的强度。在大多数实际应用中，`zeta` 应为非负数。`zeta = 0` 表示无阻尼系统，`zeta = 1` 表示临界阻尼，`zeta > 1` 表示过阻尼。负阻尼比在物理上通常没有意义，因为它会导致系统振动的振幅随时间增加而增加，这在大多数实际情况下是不可能的。

在拟合结果为非正时，loss返回一个极大的数，确保不会导致负值的结果：

![image-20240116153242954](assets/image-20240116153242954.png)

拟合的初值设置：

`initial_guess=[200, 500, 0.1]`， 即 A=200，omega_n = 500, zeta =0.1

不同温度下的拟合结果：

![image-20240116153503238](assets/image-20240116153503238.png)

![image-20240116153517309](assets/image-20240116153517309.png)

![image-20240116153532214](assets/image-20240116153532214.png)

![image-20240116153541415](assets/image-20240116153541415.png)

![image-20240116153549877](assets/image-20240116153549877.png)

![image-20240116153559051](assets/image-20240116153559051.png)

![image-20240116153606199](assets/image-20240116153606199.png)

![image-20240116153618917](assets/image-20240116153618917.png)

从结果看到，整体拟合效果较好，高频比低频的拟合效果好，相位趋势近似（在拟合范围[5-100Hz]，但是相位似乎存在一个常数项的差值，这可能是系统本身并不是严格的二阶系统，系统中的某些环节的作用下存在一个群时延。

为了避免采样密集的频率区域有偏大的损失权重，对采样点的采样密度进行加权：

![image-20240116155421539](assets/image-20240116155421539.png)

增加了一个 `group_delay` 参数补偿群时延：

![image-20240116162955297](assets/image-20240116162955297.png)

针对低温的数据设置单独的拟合范围：

![image-20240116162913456](assets/image-20240116162913456.png)

![image-20240116162927251](assets/image-20240116162927251.png)

![image-20240116163020408](assets/image-20240116163020408.png)

![image-20240116163036662](assets/image-20240116163036662.png)

![image-20240116163046710](assets/image-20240116163046710.png)

![image-20240116163057813](assets/image-20240116163057813.png)

![image-20240116163107745](assets/image-20240116163107745.png)

![image-20240116163118049](assets/image-20240116163118049.png)

![image-20240116163127469](assets/image-20240116163127469.png)

# 2024年1月17日

补偿环节可以考虑使用一个超前或者滞后环节：



![1705412347447](assets/1705412347447.jpg)

![image-20240116214010709](assets/image-20240116214010709.png)

转折频率 T 可调，beta < 1  时为超前环节， beta > 1 时为滞后环节

![1705414001546](assets/1705414001546.png)

如果用转折频率 1/T 处对应上预期高频截止频率，将该点上调 ΔG，则 β 可以计算为：

![image-20240116220944214](assets/image-20240116220944214.png)

![image-20240116222209687](assets/image-20240116222209687.png)

校正效果：由原来的 60Hz 抬高到了 90 Hz

# 2024年1月18日

整理了代码结构，统一使用`exam_process.System`数据结构，弃用`system.DataSystem`数据结构。

对不同温度下的数据进行高频截止频率校正

![image-20240117160333763](assets/image-20240117160333763.png)

![image-20240117160436492](assets/image-20240117160436492.png)

![image-20240117160448206](assets/image-20240117160448206.png)

![image-20240117160456788](assets/image-20240117160456788.png)

![image-20240117160504727](assets/image-20240117160504727.png)

![image-20240117160511727](assets/image-20240117160511727.png)

对25度到50度的数据进行了有效的校准，校准前的误差在23Hz，校准后2Hz

![image-20240117161222344](assets/image-20240117161222344.png)

-10度没有校准完成：

![image-20240117161327955](assets/image-20240117161327955.png)

# 2024年1月19日

![image-20240116220944214](assets/image-20240116220944214.png)

由 beta 的计算公式可知，ΔG^2 不能超过 2，因此使用单个校正环节无法校正偏差较大的传递函数。考虑使用多个校正环节的串联形式。

补偿器可能会出现补偿系数过大的情况：

![image-20240117164656430](assets/image-20240117164656430.png)

![image-20240117164711425](assets/image-20240117164711425.png)

减少预期频率到60Hz：

![image-20240117164753386](assets/image-20240117164753386.png)

![image-20240117164813626](assets/image-20240117164813626.png)



此时的补偿效果：![image-20240117165608093](assets/image-20240117165608093.png)

![image-20240117165615861](assets/image-20240117165615861.png)

![image-20240117165626220](assets/image-20240117165626220.png)

![image-20240117165634115](assets/image-20240117165634115.png)

![image-20240117165642101](assets/image-20240117165642101.png)

![image-20240117165651946](assets/image-20240117165651946.png)

![image-20240117164836114](assets/image-20240117164836114.png)

# 2024年1月20日

遇到补偿系数过大的情况，考虑在补偿的后面加一个低通滤波器

不适用后置低通滤波器：

![image-20240117192430602](assets/image-20240117192430602.png)

![image-20240117192608657](assets/image-20240117192608657.png)

![image-20240117192908808](assets/image-20240117192908808.png)

使用后置低通滤波器：

![image-20240117192525916](assets/image-20240117192525916.png)

![image-20240117192535280](assets/image-20240117192535280.png)

后置低通滤波器可以在一定程度上改善高频过度补偿的问题，以及减轻对高频噪声的放大作用。

![image-20240117192948650](assets/image-20240117192948650.png)

目前在设定高频截止频率为80Hz时，对除了-10°C的点外，都由比较好的补偿作用。

对于较低温度的点，存在最初的拟合效果就不够理想的可能性，导致后续计算的情况较为异常。

重新检查拟合情况，发现，对于-10°C的ws拟合，原先的拟合效果`fit`在高频出差异很大，应该替换为新的拟合结果 `fit2`

![image-20240117212059343](assets/image-20240117212059343.png)

分别使用两个函数来计算number（fit和result），使其和远fit的相位近似（为了后边的计算）：

![image-20240117220806982](assets/image-20240117220806982.png)

![image-20240117220819713](assets/image-20240117220819713.png)

如果不超出一阶补偿范围（补偿系数不超过1.414），那么补偿效果是很好的：

![image-20240117223035222](assets/image-20240117223035222.png)

超出后会不好：

![image-20240117223028053](assets/image-20240117223028053.png)

考虑不要使用一阶系统的串联，而是使用一个二阶系统的谐振峰来进行补偿：

![image-20240118104530377](assets/image-20240118104530377.png)

![image-20240118104536972](assets/image-20240118104536972.png)

![image-20240118104543971](assets/image-20240118104543971.png)

![image-20240118104549957](assets/image-20240118104549957.png)

![image-20240118104559701](assets/image-20240118104559701.png)

二阶系统的谐振峰可以趋于无限大，没有补偿范围的限制。

当补偿系数>1时，用二阶系统的谐振峰补偿到90Hz的效果

（补偿系数<1时仍用1阶系统进行补偿）：

![image-20240118104955107](assets/image-20240118104955107.png)

![image-20240118105004082](assets/image-20240118105004082.png)

![image-20240118105010846](assets/image-20240118105010846.png)

![image-20240118105015645](assets/image-20240118105015645.png)

![image-20240118105024494](assets/image-20240118105024494.png)

![image-20240118105031267](assets/image-20240118105031267.png)

![image-20240118105038949](assets/image-20240118105038949.png)

![image-20240118105046929](assets/image-20240118105046929.png)

![image-20240118105055723](assets/image-20240118105055723.png)

# 2024年1月24日

后置滤波器在阶数高时会导致补偿后的阻尼系数过低：

![image-20240124165754705](assets/image-20240124165754705.png)

对预期截止频率进行针对性的微调：![image-20240124205004059](assets/image-20240124205004059.png)

