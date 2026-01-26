#!/usr/bin/env python3
"""
批量运行WaveNet5实验脚本

功能：
1. 使用subprocess机制批量运行多个实验
2. 将stdout/stderr分别保存到logs目录
3. 支持并行和串行运行模式
4. 实时显示运行状态
"""

import subprocess
import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
import argparse
import json

class ExperimentRunner:
    def __init__(self, base_dir=".", log_dir="logs"):
        self.base_dir = Path(base_dir)
        self.log_dir = self.base_dir / log_dir
        self.processes = {}
        self.start_times = {}
        
    def ensure_log_dir(self, project_name):
        """确保日志目录存在"""
        project_log_dir = self.log_dir / project_name
        project_log_dir.mkdir(parents=True, exist_ok=True)
        return project_log_dir
    
    def get_log_files(self, project_name):
        """获取日志文件路径"""
        log_dir = self.ensure_log_dir(project_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        stdout_file = log_dir / f"stdout_{timestamp}.log"
        stderr_file = log_dir / f"stderr_{timestamp}.log"
        
        return stdout_file, stderr_file
    
    def run_single_experiment(self, project_name, wait=True):
        """运行单个实验"""
        print(f"\n{'='*60}")
        print(f"🚀 启动实验: {project_name}")
        print(f"{'='*60}")
        
        # 获取日志文件
        stdout_file, stderr_file = self.get_log_files(project_name)
        
        # 构建命令
        cmd = [
            sys.executable,  # 使用当前Python解释器
            str(self.base_dir / "cli.py"),
            project_name
        ]
        
        print(f"📂 工作目录: {self.base_dir}")
        print(f"📋 命令: {' '.join(cmd)}")
        print(f"📄 标准输出: {stdout_file}")
        print(f"📄 错误输出: {stderr_file}")
        
        # 打开日志文件
        with open(stdout_file, 'w') as f_out, open(stderr_file, 'w') as f_err:
            # 写入启动信息
            f_out.write(f"{'='*60}\n")
            f_out.write(f"实验: {project_name}\n")
            f_out.write(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f_out.write(f"命令: {' '.join(cmd)}\n")
            f_out.write(f"{'='*60}\n\n")
            f_out.flush()
            
            # 启动进程
            process = subprocess.Popen(
                cmd,
                stdout=f_out,
                stderr=f_err,
                cwd=str(self.base_dir),
                text=True,
                bufsize=1  # 行缓冲
            )
            
            self.processes[project_name] = process
            self.start_times[project_name] = time.time()
            
            print(f"✅ 进程已启动 (PID: {process.pid})")
            
            if wait:
                # 等待进程完成
                self.wait_for_completion(project_name)
            
            return process
    
    def wait_for_completion(self, project_name):
        """等待单个实验完成"""
        process = self.processes.get(project_name)
        if not process:
            return
        
        print(f"\n⏳ 等待 {project_name} 完成...")
        
        # 监控进程
        while process.poll() is None:
            elapsed = time.time() - self.start_times[project_name]
            print(f"\r⏱️  运行时间: {elapsed:.0f}秒", end='', flush=True)
            time.sleep(1)
        
        # 获取返回码
        return_code = process.returncode
        elapsed = time.time() - self.start_times[project_name]
        
        print(f"\n{'✅' if return_code == 0 else '❌'} {project_name} 完成 (返回码: {return_code}, 耗时: {elapsed:.0f}秒)")
        
        # 检查日志文件大小
        stdout_file, stderr_file = self.get_log_files(project_name)
        stdout_size = os.path.getsize(stdout_file) if os.path.exists(stdout_file) else 0
        stderr_size = os.path.getsize(stderr_file) if os.path.exists(stderr_file) else 0
        
        print(f"📊 日志大小: stdout={stdout_size:,}字节, stderr={stderr_size:,}字节")
        
        return return_code
    
    def run_experiments_serial(self, project_list):
        """串行运行多个实验"""
        print(f"\n🔄 串行模式: 依次运行 {len(project_list)} 个实验")
        
        results = {}
        for project in project_list:
            start_time = time.time()
            process = self.run_single_experiment(project, wait=True)
            elapsed = time.time() - start_time
            results[project] = {
                'return_code': process.returncode,
                'elapsed_time': elapsed
            }
        
        return results
    
    def run_experiments_parallel(self, project_list, max_parallel=6):
        """并行运行多个实验"""
        print(f"\n🔄 并行模式: 最多同时运行 {max_parallel} 个实验")
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import queue
        
        # 使用线程池管理并行任务
        results = {}
        running_processes = {}
        project_queue = queue.Queue()
        
        # 将所有项目加入队列
        for project in project_list:
            project_queue.put(project)
        
        # 并行运行函数
        def run_and_wait(project_name):
            """运行单个实验并等待完成"""
            process = self.run_single_experiment(project_name, wait=False)
            running_processes[project_name] = process
            
            # 等待完成
            return_code = self.wait_for_completion(project_name)
            elapsed = time.time() - self.start_times[project_name]
            
            # 清理
            del running_processes[project_name]
            
            return project_name, {
                'return_code': return_code,
                'elapsed_time': elapsed
            }
        
        # 使用线程池执行
        with ThreadPoolExecutor(max_workers=max_parallel) as executor:
            # 提交初始任务
            futures = []
            for _ in range(min(max_parallel, len(project_list))):
                if not project_queue.empty():
                    project = project_queue.get()
                    future = executor.submit(run_and_wait, project)
                    futures.append(future)
                    time.sleep(0.5)  # 避免同时启动造成资源竞争
            
            # 处理完成的任务并提交新任务
            for future in as_completed(futures):
                project_name, result = future.result()
                results[project_name] = result
                
                # 如果还有任务，提交新的
                if not project_queue.empty():
                    project = project_queue.get()
                    new_future = executor.submit(run_and_wait, project)
                    futures.append(new_future)
                    time.sleep(0.5)
        
        return results
    
    def wait_all(self):
        """等待所有进程完成"""
        print(f"\n⏳ 等待所有进程完成...")
        
        results = {}
        for project_name, process in self.processes.items():
            if process.poll() is None:  # 仍在运行
                return_code = self.wait_for_completion(project_name)
                results[project_name] = {
                    'return_code': return_code,
                    'elapsed_time': time.time() - self.start_times[project_name]
                }
        
        return results
    
    def print_summary(self, results):
        """打印运行总结"""
        print(f"\n{'='*60}")
        print("📊 运行总结")
        print(f"{'='*60}")
        
        success_count = sum(1 for r in results.values() if r['return_code'] == 0)
        total_count = len(results)
        
        print(f"\n成功: {success_count}/{total_count}")
        print(f"\n详细结果:")
        
        for project, result in results.items():
            status = "✅ 成功" if result['return_code'] == 0 else "❌ 失败"
            elapsed = result['elapsed_time']
            print(f"  {project:<20} {status} (耗时: {elapsed:.0f}秒)")
        
        # 生成总结文件
        summary_file = self.log_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 总结文件: {summary_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批量运行WaveNet5实验')
    parser.add_argument('projects', nargs='*', help='要运行的项目名称列表')
    parser.add_argument('--mode', choices=['serial', 'parallel'], default='serial',
                       help='运行模式: serial(串行) 或 parallel(并行)')
    parser.add_argument('--max-parallel', type=int, default=6,
                       help='并行模式下的最大同时运行数')
    parser.add_argument('--log-dir', default='logs',
                       help='日志目录名称')
    
    # 预定义的实验组
    parser.add_argument('--phase1', action='store_true',
                       help='运行Phase1所有实验 (EFF_A1-D1)')
    parser.add_argument('--phase2', action='store_true',
                       help='运行Phase2所有实验 (EFF2_A1-C2)')
    parser.add_argument('--phase2-high', action='store_true',
                       help='仅运行Phase2高优先级实验 (EFF2_A1, B1)')
    parser.add_argument('--phase2-parallel', action='store_true',
                       help='并行运行所有Phase2实验（6个同时）')
    
    args = parser.parse_args()
    
    # 处理预定义实验组
    if args.phase1:
        projects = ['WNET5_EFF_A1', 'WNET5_EFF_A2', 'WNET5_EFF_B1',
                   'WNET5_EFF_C1', 'WNET5_EFF_C2', 'WNET5_EFF_D1']
    elif args.phase2 or args.phase2_parallel:
        projects = ['WNET5_EFF2_A1', 'WNET5_EFF2_A2', 'WNET5_EFF2_B1',
                   'WNET5_EFF2_B2', 'WNET5_EFF2_C1', 'WNET5_EFF2_C2']
        if args.phase2_parallel:
            args.mode = 'parallel'
            args.max_parallel = 6
    elif args.phase2_high:
        projects = ['WNET5_EFF2_A1', 'WNET5_EFF2_B1']
    else:
        projects = args.projects
    
    # 创建运行器
    runner = ExperimentRunner(log_dir=args.log_dir)
    
    print(f"🔬 WaveNet5批量实验运行器")
    print(f"{'='*60}")
    print(f"📋 实验列表: {', '.join(projects)}")
    print(f"🔄 运行模式: {args.mode}")
    if args.mode == 'parallel':
        print(f"🔢 最大并行数: {args.max_parallel}")
    print(f"📂 日志目录: {runner.log_dir}")
    
    # 确认运行
    print(f"\n准备运行 {len(projects)} 个实验，是否继续? (y/n): ", end='')
    if input().lower() != 'y':
        print("❌ 已取消")
        return
    
    # 运行实验
    start_time = time.time()
    
    if args.mode == 'serial':
        results = runner.run_experiments_serial(projects)
    else:
        results = runner.run_experiments_parallel(projects, args.max_parallel)
    
    total_time = time.time() - start_time
    
    # 打印总结
    runner.print_summary(results)
    print(f"\n⏱️  总耗时: {total_time:.0f}秒 ({total_time/60:.1f}分钟)")
    print(f"\n✅ 批量运行完成！")


if __name__ == "__main__":
    main()