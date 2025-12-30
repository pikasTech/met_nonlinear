#!/usr/bin/env python3
"""
实际微调测试脚本 - WNET5q1h2u6l3项目

这是首次从Mock模式转向实际cli.py调用的测试
"""

import json
import shutil
import logging
import traceback
from pathlib import Path
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class RealTuningTest:
    """实际微调测试类"""
    
    def __init__(self):
        self.project_path = Path("/mnt/f/Work/met_nonlinear_worktrees/met_nonlinear_master/projects/WNET5q1h2u6l3")
        self.config_path = self.project_path / "config.json"
        self.backup_path = self.project_path / f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # 实验日志
        self.experiment_log = []
        
    def backup_config(self):
        """备份当前配置"""
        try:
            shutil.copy(self.config_path, self.backup_path)
            logger.info(f"✅ 配置已备份到: {self.backup_path}")
            return True
        except Exception as e:
            logger.error(f"❌ 配置备份失败: {e}")
            return False
    
    def load_current_config(self):
        """加载当前配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info("✅ 当前配置加载成功")
            return config
        except Exception as e:
            logger.error(f"❌ 配置加载失败: {e}")
            return None
    
    def save_config(self, config):
        """保存配置"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            logger.info("✅ 配置保存成功")
            return True
        except Exception as e:
            logger.error(f"❌ 配置保存失败: {e}")
            return False
    
    def add_layer5_compensation(self, config):
        """添加Layer 5补偿配置"""
        logger.info("🔧 添加Layer 5补偿配置...")
        
        # 基于分析结果，Layer 5偏置为-4.800256
        # 使用50%保守补偿策略
        layer5_compensation = [2.400128]  # 50% * 4.800256
        
        # 添加到配置中
        bias_adjustments = config["inference_config"]["bias_compensation"]["layer_bias_adjustments"]
        bias_adjustments["5"] = layer5_compensation
        
        logger.info(f"✅ Layer 5补偿值: {layer5_compensation}")
        
        # 记录实验
        self.experiment_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": "add_layer5_compensation",
            "value": layer5_compensation,
            "strategy": "conservative_50_percent"
        })
        
        return config
    
    def test_cli_call(self, mode="analyze"):
        """测试cli.py调用"""
        import subprocess
        
        cmd = [
            "conda", "run", "--no-capture-output", "-n", "tf26",
            "python", "cli.py", "-a", "WNET5q1h2u6l3"
        ]
        
        if mode == "force_analyze":
            cmd.insert(-1, "-f")  # 添加-f参数强制重新分析
        
        logger.info(f"🚀 执行命令: {' '.join(cmd)}")
        
        try:
            # 切换到项目根目录
            root_dir = "/mnt/f/Work/met_nonlinear_worktrees/met_nonlinear_master"
            
            result = subprocess.run(
                cmd,
                cwd=root_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                logger.info("✅ cli.py 执行成功")
                # 记录成功的输出的关键信息
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if 'RMS=' in line or '误差分析' in line or '偏置误差' in line:
                        logger.info(f"📊 {line.strip()}")
                        
                return True, result.stdout
            else:
                logger.error(f"❌ cli.py 执行失败 (返回码: {result.returncode})")
                logger.error(f"错误输出: {result.stderr}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            logger.error("❌ cli.py 执行超时")
            return False, "Timeout"
        except Exception as e:
            logger.error(f"❌ cli.py 执行异常: {e}")
            return False, str(e)
    
    def run_phase3_test(self):
        """执行Phase 3: 添加Layer 5补偿并测试"""
        logger.info("="*60)
        logger.info("🚀 开始Phase 3: Layer 5补偿配置测试")
        logger.info("="*60)
        
        # 1. 备份配置
        if not self.backup_config():
            return False
        
        # 2. 加载当前配置
        config = self.load_current_config()
        if config is None:
            return False
        
        # 3. 显示当前配置状态
        bias_adjustments = config["inference_config"]["bias_compensation"]["layer_bias_adjustments"]
        logger.info(f"📊 当前配置层数: {list(bias_adjustments.keys())}")
        
        # 4. 检查是否需要添加Layer 5
        if "5" not in bias_adjustments:
            logger.info("🔍 发现Layer 5缺少补偿配置")
            
            # 添加Layer 5补偿
            config = self.add_layer5_compensation(config)
            
            # 保存配置
            if not self.save_config(config):
                return False
            
            logger.info("✅ Layer 5补偿配置已添加")
        else:
            logger.info("ℹ️  Layer 5补偿配置已存在")
        
        # 5. 测试配置更新后的效果
        logger.info("🧪 测试配置更新后的效果...")
        success, output = self.test_cli_call("force_analyze")
        
        if success:
            logger.info("✅ Phase 3测试成功完成")
            
            # 记录实验结果
            self.experiment_log.append({
                "timestamp": datetime.now().isoformat(),
                "phase": "phase3_layer5_compensation",
                "status": "success",
                "config_layers": list(bias_adjustments.keys()),
                "execution_time": "successful"
            })
            
            return True
        else:
            logger.error("❌ Phase 3测试失败")
            
            # 尝试回滚配置
            logger.info("🔄 尝试回滚配置...")
            try:
                shutil.copy(self.backup_path, self.config_path)
                logger.info("✅ 配置已回滚")
            except Exception as e:
                logger.error(f"❌ 配置回滚失败: {e}")
            
            return False
    
    def save_experiment_log(self):
        """保存实验日志"""
        log_path = Path(__file__).parent / "logs" / f"real_tuning_experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "experiment_info": {
                        "project": "WNET5q1h2u6l3",
                        "type": "real_tuning_test",
                        "start_time": datetime.now().isoformat(),
                        "description": "First real tuning test from mock to actual cli.py calls"
                    },
                    "experiment_log": self.experiment_log
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📝 实验日志已保存: {log_path}")
            return log_path
        except Exception as e:
            logger.error(f"❌ 实验日志保存失败: {e}")
            return None


def main():
    """主函数"""
    logger.info("🎯 WNET5q1h2u6l3 实际微调测试开始")
    
    try:
        # 创建测试实例
        test = RealTuningTest()
        
        # 执行Phase 3测试
        success = test.run_phase3_test()
        
        # 保存实验日志
        test.save_experiment_log()
        
        if success:
            logger.info("🎉 Phase 3测试完全成功！")
            logger.info("📋 下一步可以进行单层微调测试")
        else:
            logger.error("❌ Phase 3测试失败，需要进一步调试")
        
        logger.info("="*60)
        logger.info("🏁 测试完成")
        logger.info("="*60)
        
        return success
        
    except Exception as e:
        logger.error(f"❌ 测试执行异常: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)