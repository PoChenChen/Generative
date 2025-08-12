#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復專案目錄結構腳本
"""

import os
import shutil

def fix_project_structure():
    """修復專案目錄結構"""
    print("🔧 開始修復專案目錄結構...")
    
    # 檢查並創建 templates 目錄
    if not os.path.exists("templates"):
        print("📁 創建 templates 目錄...")
        os.makedirs("templates")
    
    # 檢查並創建 static 目錄
    if not os.path.exists("static"):
        print("📁 創建 static 目錄...")
        os.makedirs("static")
    
    # 移動 index.html 到 templates 目錄
    if os.path.exists("templete/index.html"):
        print("📄 移動 index.html 到 templates 目錄...")
        shutil.copy2("templete/index.html", "templates/index.html")
        print("✅ index.html 已移動到 templates 目錄")
    
    # 移動 style.css 到 static 目錄
    if os.path.exists("templete/style.css"):
        print("🎨 移動 style.css 到 static 目錄...")
        shutil.copy2("templete/style.css", "static/style.css")
        print("✅ style.css 已移動到 static 目錄")
    
    # 檢查 requirements.txt
    if os.path.exists("templete/requirements.txt"):
        print("📦 移動 requirements.txt 到根目錄...")
        shutil.copy2("templete/requirements.txt", "requirements_full.txt")
        print("✅ requirements.txt 已複製為 requirements_full.txt")
    
    print("\n🎉 目錄結構修復完成！")
    print("\n📁 當前目錄結構：")
    print_directory_structure(".")

def print_directory_structure(path, prefix=""):
    """打印目錄結構"""
    if not os.path.isdir(path):
        return
    
    items = sorted(os.listdir(path))
    for i, item in enumerate(items):
        if item.startswith('.') or item in ['__pycache__', 'venv']:
            continue
            
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        next_prefix = "    " if is_last else "│   "
        
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            print(f"{prefix}{current_prefix}{item}/")
            print_directory_structure(full_path, prefix + next_prefix)
        else:
            print(f"{prefix}{current_prefix}{item}")

if __name__ == "__main__":
    print("🚀 AI 文案生成工具 - 目錄結構修復")
    print("=" * 50)
    
    try:
        fix_project_structure()
        print("\n✨ 現在您可以運行應用了！")
        print("\n💡 使用方法：")
        print("1. 安裝依賴：pip install -r requirements_simple.txt")
        print("2. 運行簡化版本：python run_simple.py")
        print("3. 或運行完整版本：python run.py")
        
    except Exception as e:
        print(f"❌ 修復失敗：{e}")
        print("\n💡 請手動執行以下操作：")
        print("1. 將 'templete' 文件夾重命名為 'templates'")
        print("2. 確保 index.html 在 templates 目錄中")
        print("3. 確保 style.css 在 static 目錄中")
