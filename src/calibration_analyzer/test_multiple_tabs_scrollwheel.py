# -*- coding: utf-8 -*-
"""
测试多标签页侧边栏滚轮控制功能
验证修复效果：
1. 每个标签页的侧边栏滚轮控制独立工作
2. 鼠标离开侧边栏后滚轮事件不再生效
"""

import tkinter as tk
from adjuster_core import Panel

def test_multiple_tabs():
    """测试多标签页的侧边栏滚轮功能"""
    
    # 第一个标签页的数据绑定
    databinding1 = {
        'param1_tab1': 10.0,
        'param2_tab1': 20.0,
        'param3_tab1': 30.0,
        'param4_tab1': 40.0,
        'param5_tab1': 50.0,
        'param6_tab1': 60.0,
        'param7_tab1': 70.0,
        'param8_tab1': 80.0,
        'param9_tab1': 90.0,
        'param10_tab1': 100.0,
        'checkbox1_tab1': True,
        'checkbox2_tab1': False,
        'file_path_tab1@filepath': '',
        'folder_path_tab1@folderpath': '',
        'button1_tab1@button': '标签1按钮',
        '@on_change': ['param1_tab1', 'param2_tab1']
    }
    
    # 第二个标签页的数据绑定
    databinding2 = {
        'param1_tab2': 15.0,
        'param2_tab2': 25.0,
        'param3_tab2': 35.0,
        'param4_tab2': 45.0,
        'param5_tab2': 55.0,
        'param6_tab2': 65.0,
        'param7_tab2': 75.0,
        'param8_tab2': 85.0,
        'param9_tab2': 95.0,
        'param10_tab2': 105.0,
        'checkbox1_tab2': False,
        'checkbox2_tab2': True,
        'file_path_tab2@filepath': '',
        'folder_path_tab2@folderpath': '',
        'button1_tab2@button': '标签2按钮',
        '@on_change': ['param1_tab2', 'param2_tab2']
    }
    
    # 第三个标签页的数据绑定
    databinding3 = {
        'param1_tab3': 12.0,
        'param2_tab3': 22.0,
        'param3_tab3': 32.0,
        'param4_tab3': 42.0,
        'param5_tab3': 52.0,
        'param6_tab3': 62.0,
        'param7_tab3': 72.0,
        'param8_tab3': 82.0,
        'param9_tab3': 92.0,
        'param10_tab3': 102.0,
        'checkbox1_tab3': True,
        'checkbox2_tab3': True,
        'file_path_tab3@filepath': '',
        'folder_path_tab3@folderpath': '',
        'button1_tab3@button': '标签3按钮',
        '@on_change': ['param1_tab3', 'param2_tab3']
    }
    
    def callback1(data):
        print(f"标签页1回调: {data}")
    
    def callback2(data):
        print(f"标签页2回调: {data}")
        
    def callback3(data):
        print(f"标签页3回调: {data}")
    
    # 创建第一个Panel（主窗口）
    panel1 = Panel(
        databinding=databinding1,
        callback=callback1,
        name='标签页1测试',
        with_plot=True,
        redirect_stdout=True
    )
    
    # 创建第二个Panel（标签页）
    panel2 = Panel(
        databinding=databinding2,
        callback=callback2,
        name='标签页2测试',
        with_plot=True,
        redirect_stdout=False  # 只在第一个标签页重定向输出
    )
    
    # 创建第三个Panel（标签页）
    panel3 = Panel(
        databinding=databinding3,
        callback=callback3,
        name='标签页3测试',
        with_plot=True,
        redirect_stdout=False
    )
    
    print("🎯 多标签页侧边栏滚轮测试已启动！")
    print("")
    print("🧪 测试说明:")
    print("   1. 切换到不同的标签页")
    print("   2. 将鼠标移到左侧边栏内，使用滚轮滚动")
    print("   3. 验证每个标签页的侧边栏滚轮都能正常工作")
    print("   4. 将鼠标移出侧边栏，验证滚轮不再影响侧边栏")
    print("   5. 将鼠标移到绘图区域，验证滚轮不影响侧边栏")
    print("")
    print("✅ 预期结果:")
    print("   - 每个标签页的侧边栏滚轮控制独立工作")
    print("   - 鼠标在侧边栏内时滚轮有效")
    print("   - 鼠标离开侧边栏后滚轮对侧边栏无效")
    print("   - 切换标签页不会影响其他标签页的滚轮功能")
    print("")
    print("🔧 测试项目:")
    print("   ✓ 标签页1的侧边栏滚轮")
    print("   ✓ 标签页2的侧边栏滚轮") 
    print("   ✓ 标签页3的侧边栏滚轮")
    print("   ✓ 鼠标进入/离开侧边栏的事件处理")
    print("   ✓ 多标签页之间的滚轮事件隔离")
    
    # 启动主界面循环
    if hasattr(Panel, 'main_window') and Panel.main_window:
        Panel.main_window.mainloop()

if __name__ == "__main__":
    test_multiple_tabs()
