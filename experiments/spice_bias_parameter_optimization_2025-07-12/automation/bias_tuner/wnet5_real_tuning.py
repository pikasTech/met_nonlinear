#!/usr/bin/env python
"""
WNET5q1h2u6l3 实际自动微调执行脚本

专注于Layer 1-4的自动化微调，完全忽略Layer 5
使用自动微调器进行实际偏置补偿优化
"""

import sys
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from tuner import BiasTuner
    from core.compensator import CompensationStrategy
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保在bias_tuner目录中运行此脚本")
    sys.exit(1)


def main():
    """WNET5q1h2u6l3 实际微调主流程"""
    print("🎯 WNET5q1h2u6l3 自动微调器执行开始")
    print("=" * 60)
    
    # 项目配置
    project_path = Path("/mnt/f/Work/met_nonlinear_worktrees/met_nonlinear_master/projects/WNET5q1h2u6l3")
    
    print(f"📁 项目路径: {project_path}")
    print(f"🎯 目标层: Layer 1-4 (忽略Layer 5)")
    print("🔧 补偿策略: 同相位策略")
    print("🚀 调用方式: 实际cli.py调用")
    print()
    
    # 创建微调器
    print("🔧 创建自动微调器...")
    tuner = BiasTuner(
        project_path,
        strategy=CompensationStrategy.SAME_PHASE,
        python_env="conda run --no-capture-output -n tf26 python",
        dry_run=False  # 实际调用模式
    )
    print("✅ 微调器创建成功")
    print()
    
    # Step 1: 基线测量
    print("📊 Step 1: 运行基线测量...")
    print("-" * 40)
    try:
        baseline = tuner.run_baseline_measurement()
        print(f"✅ 基线错误测量完成，覆盖 {len(baseline['statistics'])} 层")
        
        # 显示基线统计
        if 'statistics' in baseline:
            for layer_idx, stats in baseline['statistics'].items():
                if int(layer_idx) <= 4:  # 只显示Layer 1-4
                    print(f"   Layer {layer_idx}: abs_mean={stats.get('abs_mean', 0):.6f}")
        print()
        
    except Exception as e:
        print(f"❌ 基线测量失败: {e}")
        return False
    
    # Step 2: 序列微调 Layer 1-4
    print("🔄 Step 2: 序列微调 Layer 1-4...")
    print("-" * 40)
    print("🎯 微调顺序: Layer 2 → Layer 3 → Layer 4")
    print("   (Layer 1 已经很好，跳过微调)")
    print("📐 补偿系数: 保守策略 80%")
    print()
    
    try:
        results = tuner.tune_sequential(
            layer_order=[2, 3, 4],  # 专注于Dense层，忽略Layer 1(已优化)和Layer 5
            scale_factors={2: 0.8, 3: 0.8, 4: 0.8}  # 80% 保守补偿
        )
        
        print(f"✅ 序列微调完成，处理了 {len(results)} 层")
        
        # 显示每层结果
        for result in results:
            layer_idx = result["layer_idx"]
            if layer_idx <= 4:  # 确保只处理Layer 1-4
                stats = result["statistics"].get(str(layer_idx), {})
                print(f"   Layer {layer_idx}: 误差降至 {stats.get('abs_mean', 0):.6f}")
        print()
        
    except Exception as e:
        print(f"❌ 序列微调失败: {e}")
        return False
    
    # Step 3: 生成报告
    print("📋 Step 3: 生成微调报告...")
    print("-" * 40)
    try:
        report_path = tuner.generate_report()
        print(f"✅ 报告已保存: {report_path}")
        print()
        
    except Exception as e:
        print(f"⚠️  报告生成失败: {e}")
        print("   (这不影响主要微调结果)")
        print()
    
    # Step 4: 改善效果总结
    print("📈 Step 4: 微调效果总结")
    print("-" * 40)
    
    if tuner.tuning_history and len(tuner.tuning_history) >= 2:
        baseline_stats = tuner.tuning_history[0]["statistics"]
        final_stats = tuner.tuning_history[-1]["statistics"]
        
        print("🎯 Layer 1-4 补偿效果:")
        
        total_improvement = 0
        improved_layers = 0
        
        for layer_idx in [1, 2, 3, 4]:
            layer_str = str(layer_idx)
            if layer_str in baseline_stats and layer_str in final_stats:
                before = baseline_stats[layer_str].get("abs_mean", 0)
                after = final_stats[layer_str].get("abs_mean", 0)
                
                if before > 0:
                    improvement = (before - after) / before * 100
                    total_improvement += improvement
                    improved_layers += 1
                    
                    status = "✅" if improvement > 10 else "⚠️" if improvement > 0 else "❌"
                    print(f"   {status} Layer {layer_idx}: {before:.6f} → {after:.6f} "
                          f"({improvement:+.1f}%)")
        
        if improved_layers > 0:
            avg_improvement = total_improvement / improved_layers
            print(f"\n🏆 平均改善效果: {avg_improvement:.1f}%")
            
            if avg_improvement > 30:
                print("🎉 微调效果优秀！")
            elif avg_improvement > 10:
                print("✅ 微调效果良好")
            else:
                print("⚠️  微调效果一般，可能需要调整策略")
    
    print()
    print("=" * 60)
    print("🏁 WNET5q1h2u6l3 自动微调完成")
    print("📝 注意: Layer 5 已按要求完全忽略")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 微调执行成功完成！")
        else:
            print("\n❌ 微调执行失败")
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n🛑 用户中断执行")
        sys.exit(130)
        
    except Exception as e:
        print(f"\n❌ 执行异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)