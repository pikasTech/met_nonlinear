# 逐层偏置补偿图形化工作流程

本文档使用多种图形化技术展示WaveNet5模型的逐层偏置补偿流程。

## 1. 整体补偿流程图 (Mermaid)

```mermaid
flowchart TB
    subgraph init["初始状态（无补偿）"]
        direction LR
        L1_0[Layer 1<br/>SVF]
        L2_0[Layer 2]
        L3_0[Layer 3]
        L4_0[Layer 4]
        L5_0[Layer 5<br/>输出层]
        
        L1_0 -->|Error₁₀<br/>微小| L2_0
        L2_0 -->|Error₂₀<br/>0.006| L3_0
        L3_0 -->|Error₃₀<br/>0.002| L4_0
        L4_0 -->|Error₄₀<br/>0.002| L5_0
        L5_0 -->|Error₅₀<br/>0.068| output0[输出]
    end
    
    subgraph step1["第1步：补偿Layer 1"]
        direction LR
        L1_1[Layer 1<br/>+补偿₁]
        L2_1[Layer 2]
        L3_1[Layer 3]
        L4_1[Layer 4]
        L5_1[Layer 5]
        
        L1_1 -->|Error₁₁<br/>≈0| L2_1
        L2_1 -->|Error₂₁| L3_1
        L3_1 -->|Error₃₁| L4_1
        L4_1 -->|Error₄₁| L5_1
        L5_1 -->|Error₅₁<br/>改善| output1[输出]
        
        L2_1 -.->|测量误差<br/>计算补偿| L1_1
    end
    
    subgraph step2["第2步：补偿Layer 2"]
        direction LR
        L1_2[Layer 1<br/>+补偿₁]
        L2_2[Layer 2<br/>+补偿₂]
        L3_2[Layer 3]
        L4_2[Layer 4]
        L5_2[Layer 5]
        
        L1_2 -->|Error₁₂| L2_2
        L2_2 -->|Error₂₂<br/>≈0| L3_2
        L3_2 -->|Error₃₂| L4_2
        L4_2 -->|Error₄₂| L5_2
        L5_2 -->|Error₅₂<br/>进一步改善| output2[输出]
        
        L3_2 -.->|测量误差<br/>计算补偿| L2_2
    end
    
    subgraph step3["第3步：补偿Layer 3（最终）"]
        direction LR
        L1_3[Layer 1<br/>+补偿₁]
        L2_3[Layer 2<br/>+补偿₂]
        L3_3[Layer 3<br/>+补偿₃]
        L4_3[Layer 4]
        L5_3[Layer 5]
        
        L1_3 -->|Error₁₃<br/>微小| L2_3
        L2_3 -->|Error₂₃<br/>0.001| L3_3
        L3_3 -->|Error₃₃<br/>≈0| L4_3
        L4_3 -->|Error₄₃<br/>0.0007| L5_3
        L5_3 -->|Error₅₃<br/>0.009<br/>↓86.8%| output3[输出]
        
        L4_3 -.->|测量误差<br/>计算补偿| L3_3
    end
    
    init --> step1
    step1 --> step2
    step2 --> step3
    
    style L1_0 fill:#FFE4B5
    style L1_1 fill:#90EE90
    style L1_2 fill:#90EE90
    style L1_3 fill:#90EE90
    style L2_2 fill:#90EE90
    style L2_3 fill:#90EE90
    style L3_3 fill:#90EE90
    style output3 fill:#98FB98,stroke:#006400,stroke-width:3px
```

## 2. 补偿机制示意图 (Mermaid)

```mermaid
graph LR
    subgraph "补偿原理"
        A[后层输出误差] --> B[计算补偿值<br/>Comp = -Error]
        B --> C[应用到前层<br/>Layer_new = Layer_old + Comp]
        C --> D[误差传播被抵消]
    end
    
    style A fill:#FFB6C1
    style B fill:#87CEEB
    style C fill:#98FB98
    style D fill:#FFD700
```

## 3. 误差改进瀑布图 (PlantUML)

```plantuml
@startuml
!theme plain
title 各层偏置误差改进效果

rectangle "基准配置" as baseline {
  rectangle "Layer 1: <0.0001" as b1 #FFE4B5
  rectangle "Layer 2: 0.006" as b2 #FFA07A
  rectangle "Layer 3: 0.002" as b3 #FFB6C1
  rectangle "Layer 4: 0.002" as b4 #FFB6C1
  rectangle "Layer 5: 0.068" as b5 #FF6347
}

rectangle "补偿后配置" as compensated {
  rectangle "Layer 1: <0.0001 (0%)" as c1 #E0FFE0
  rectangle "Layer 2: 0.001 (↓80%)" as c2 #90EE90
  rectangle "Layer 3: 0.001 (↓40.1%)" as c3 #98FB98
  rectangle "Layer 4: 0.0007 (↓62.3%)" as c4 #90EE90
  rectangle "Layer 5: 0.009 (↓86.8%)" as c5 #006400
}

b1 -[hidden]-> b2
b2 -[hidden]-> b3
b3 -[hidden]-> b4
b4 -[hidden]-> b5

c1 -[hidden]-> c2
c2 -[hidden]-> c3
c3 -[hidden]-> c4
c4 -[hidden]-> c5

baseline --> compensated : "应用逐层补偿"
@enduml
```

## 4. 补偿步骤时序图 (Mermaid)

```mermaid
sequenceDiagram
    participant 测试系统
    participant Layer1 as Layer 1 (SVF)
    participant Layer2 as Layer 2
    participant Layer3 as Layer 3
    participant Layer4 as Layer 4
    participant Layer5 as Layer 5
    
    Note over 测试系统,Layer5: 初始测试（无补偿）
    测试系统->>Layer1: 测量Error₁₀
    测试系统->>Layer2: 测量Error₂₀ = 0.006
    测试系统->>Layer3: 测量Error₃₀ = 0.002
    测试系统->>Layer4: 测量Error₄₀ = 0.002
    测试系统->>Layer5: 测量Error₅₀ = 0.068
    
    Note over 测试系统,Layer2: 第1步：补偿Layer 1
    Layer2-->>测试系统: Error₂₀
    测试系统->>Layer1: 应用补偿₁ = -Error₂₀
    Note right of Layer1: Layer1 += 补偿₁
    测试系统->>Layer1: 重测Error₁₁ ≈ 0
    
    Note over 测试系统,Layer3: 第2步：补偿Layer 2
    Layer3-->>测试系统: Error₃₁
    测试系统->>Layer2: 应用补偿₂ = -Error₃₁
    Note right of Layer2: Layer2 += 补偿₂
    测试系统->>Layer2: 重测Error₂₂ ≈ 0
    
    Note over 测试系统,Layer4: 第3步：补偿Layer 3
    Layer4-->>测试系统: Error₄₂
    测试系统->>Layer3: 应用补偿₃ = -Error₄₂
    Note right of Layer3: Layer3 += 补偿₃
    测试系统->>Layer3: 重测Error₃₃ ≈ 0
    
    Note over 测试系统,Layer5: 最终测试
    测试系统->>Layer5: 测量Error₅₃ = 0.009
    Note right of Layer5: 改进86.8%！
```

## 5. 误差传播可视化 (Mermaid)

```mermaid
graph TD
    subgraph "误差传播路径"
        E1[Layer 1 误差] --> E2[Layer 2 输入]
        E2 --> E2O[Layer 2 误差]
        E2O --> E3[Layer 3 输入]
        E3 --> E3O[Layer 3 误差]
        E3O --> E4[Layer 4 输入]
        E4 --> E4O[Layer 4 误差]
        E4O --> E5[Layer 5 输入]
        E5 --> E5O[Layer 5 误差<br/>最终输出]
    end
    
    subgraph "补偿效果"
        C1[补偿₁抵消E1] -.-> E2
        C2[补偿₂抵消E2O] -.-> E3
        C3[补偿₃抵消E3O] -.-> E4
        
        style C1 fill:#90EE90
        style C2 fill:#90EE90
        style C3 fill:#90EE90
    end
    
    E5O --> Result[最终误差大幅降低<br/>0.068 → 0.009]
    style Result fill:#98FB98,stroke:#006400,stroke-width:3px
```

## 6. 改进效果柱状图 (Chart.js 配置)

```javascript
// 可用于生成交互式图表的配置
const chartConfig = {
    type: 'bar',
    data: {
        labels: ['Layer 1', 'Layer 2', 'Layer 3', 'Layer 4', 'Layer 5'],
        datasets: [{
            label: '基准误差',
            data: [0.0001, 0.006, 0.002, 0.002, 0.068],
            backgroundColor: '#FF6B6B',
            borderColor: '#C92A2A',
            borderWidth: 1
        }, {
            label: '补偿后误差',
            data: [0.0001, 0.001, 0.001, 0.0007, 0.009],
            backgroundColor: '#51CF66',
            borderColor: '#2B8A3E',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: '逐层偏置误差对比'
            },
            tooltip: {
                callbacks: {
                    afterLabel: function(context) {
                        if (context.datasetIndex === 1) {
                            const improvements = [0, 80.0, 40.1, 62.3, 86.8];
                            return `改进: ${improvements[context.dataIndex]}%`;
                        }
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: '偏置误差'
                }
            }
        }
    }
};
```

## 7. 补偿算法流程 (Mermaid)

```mermaid
flowchart TD
    Start([开始]) --> Init[初始化所有层参数]
    Init --> Test0[测试基准配置<br/>记录所有层误差]
    
    Test0 --> Loop{i = 1 to 3}
    
    Loop -->|是| Measure[测量第 i+1 层的输出误差]
    Measure --> Calc[计算补偿值<br/>Comp_i = -Error_{i+1}]
    Calc --> Apply[应用补偿到第 i 层<br/>Layer_i += Comp_i]
    Apply --> Retest[重新测试所有层]
    Retest --> Update[更新误差记录]
    Update --> Loop
    
    Loop -->|否| Final[最终测试和验证]
    Final --> Report[生成补偿报告]
    Report --> End([结束])
    
    style Start fill:#90EE90
    style End fill:#90EE90
    style Calc fill:#87CEEB
    style Apply fill:#DDA0DD
    style Report fill:#FFD700
```

## 使用说明

1. **Mermaid图表**：可以在支持Mermaid的Markdown查看器中直接渲染（如GitHub、GitLab、VS Code等）
2. **PlantUML图表**：需要PlantUML支持，可以使用在线渲染器或IDE插件
3. **Chart.js配置**：可以在网页中使用Chart.js库生成交互式图表
4. **导出选项**：所有图表都可以导出为SVG、PNG等格式供文档使用

## 图表生成工具推荐

- **在线工具**：
  - [Mermaid Live Editor](https://mermaid.live/)
  - [PlantUML Web Server](http://www.plantuml.com/plantuml)
  - [Chart.js Playground](https://www.chartjs.org/docs/latest/samples/)

- **VS Code插件**：
  - Markdown Preview Mermaid Support
  - PlantUML
  - Markdown Preview Enhanced

- **其他工具**：
  - draw.io / diagrams.net
  - Lucidchart
  - Microsoft Visio

---

生成时间: 2025-07-13