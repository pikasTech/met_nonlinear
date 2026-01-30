# R14 SVF层误差仿真含Dense结果报告图片插入验证实现报告

## 任务目标

在 R13 的基础上，进一步完善 `wnet5-circuit-validation` 任务的报告生成功能：
1. 插入图片必须使用 `![]()` 的 Markdown 格式。
2. 图片路径必须使用相对路径（相对于报告文件）。
3. 增加验证代码，确保 `data/plots` 目录下的所有 PNG 图片都被正确插入到 `data/reports/report.md` 中，无遗漏且路径正确。
4. **新增**：重构报告逻辑结构，使其符合“数据绘图 -> 误差因素分析”的逻辑流。
5. **新增**：为所有生成的图表（包括辅助图表）提供详细的文字说明。

## 实现方案

### 1. 报告逻辑结构重构

修改 `visualization/wnet5_circuit_validator.py` 中的 `_generate_svf_error_report` 方法，将报告内容重新组织为以下章节：
- **1. 概述**：项目基本信息、频率范围、仿真模式。
- **2. 频率响应对比（仿真 vs 实测）**：
    - 2.1 仿真与实测合并对比图 (`frequency_response_comparison_merged.png`)
    - 2.2 频率响应误差比值图 (`frequency_response_error_ratio.png`)
- **3. 误差因素分析**：
    - 3.1 E96 量化影响分析 (`frequency_response_e96_comparison.png`)
    - 3.2 SVF 层误差对整体的影响：
        - 3.2.1 SVF 参数拟合验证 (`svf_fit_comparison.png`)
        - 3.2.2 SVF 层原始误差分布 (`svf_error_comparison_merged.png`)
        - 3.2.3 SVF 误差对整体电路的影响 (`svf_dense_error_comparison.png`)
- **4. 结论**：汇总拟合质量指标（RMSE, R²）并分析误差来源。
- **5. 其他生成图表**：自动包含未在上述章节中引用的所有 PNG 图片。

### 2. 增强的图表说明系统

为每个图表添加了标准化的描述块，包括：
- **设计目的**：解释该图表解决什么问题。
- **横轴/纵轴**：明确物理量和刻度类型。
- **数据曲线**：解释不同线型、颜色的含义。
- **数据来源**：说明数据是来自理论计算、实验测量还是拟合结果。

对于“其他生成图表”章节，引入了 `plot_descriptions` 模板字典，确保如 `frequency_response.png` 等辅助图表也能获得专业的文字说明。

### 3. 自动化验证与相对路径

- **Markdown 格式**：统一使用 `![标题](../plots/文件名.png)`。
- **相对路径**：固定使用 `../plots/` 前缀，确保报告在 `reports/` 目录下能正确引用 `plots/` 目录的资源。
- **验证逻辑**：
    - 使用正则表达式 `re.findall(r'!\[.*?\]\(\.\./plots/(.*?)\)', content)` 提取报告中所有已插入的图片文件名。
    - 与磁盘上的 `all_plots` 进行对比，找出遗漏项。
    - 重新读取保存后的文件，验证每个图片文件的路径字符串是否完全匹配预期格式。

## 代码实现细节

核心验证与动态插入逻辑如下：

```python
        # R14: 确保所有图片都被插入
        plot_dir = self.output_path / "plots"
        all_plots = list(plot_dir.glob("*.png"))
        
        # 简单的正则匹配已插入的图片
        import re
        inserted_plots = re.findall(r'!\[.*?\]\(\.\./plots/(.*?)\)', report_content)
        
        missing_plots = []
        for plot_file in all_plots:
            if plot_file.name not in inserted_plots:
                missing_plots.append(plot_file.name)
        
        if missing_plots:
            # 定义已知图表的说明模板
            plot_descriptions = { ... }
            report_content += "\n## 5. 其他生成图表\n\n"
            for plot_name in missing_plots:
                # 根据模板或默认格式插入图片和说明
                ...

        # ... 保存报告 ...

        # R14: 验证代码
        with open(report_path, 'r', encoding='utf-8') as f:
            final_content = f.read()
        
        verification_failed = False
        for plot_file in all_plots:
            if plot_file.name not in final_content:
                logger.error(f"❌ 报告验证失败！图片 {plot_file.name} 未被插入到报告中。")
                verification_failed = True
            else:
                expected_rel_path = f"../plots/{plot_file.name}"
                if expected_rel_path not in final_content:
                    logger.error(f"❌ 报告验证失败！图片 {plot_file.name} 的路径格式不正确。")
                    verification_failed = True
```

## 运行验证

使用以下命令运行测试：
`python cli.py ep c:\work\met_nonlinear_master\ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer1`

### 运行日志摘录
```
[INFO  4.78s] 生成SVF误差仿真报告...
[INFO  4.79s] ✅ 报告验证通过：所有图片均已正确插入且路径正确。
[INFO  4.79s] SVF误差仿真报告已保存: c:\work\met_nonlinear_master\ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer1\data\reports\report.md
```

### 报告内容验证
生成的报告 [report.md](../../ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer1/data/reports/report.md) 具有清晰的逻辑层次：
1.  **先展示数据对比**（2.1, 2.2 节）。
2.  **再分析误差因素**（3.1 节分析 E96，3.2 节分析 SVF 偏差）。
3.  **所有图片**均正确显示，且带有详细的“设计目的”等说明文字。

## 结论

R14 的要求已全部实现。报告不仅实现了图片插入的格式规范化和自动化验证，还通过逻辑重构和详细描述，使其从一份简单的“结果清单”转变为一份具有专业分析深度的“技术报告”。
