#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 文案生成工具簡化版本啟動腳本
"""

import os
import sys
from app_simple import app

def main():
    """主函數"""
    print("🚀 啟動 AI 文案生成工具（簡化版本）...")
    print("📱 應用將在 http://localhost:5000 運行")
    print("🔄 按 Ctrl+C 停止應用")
    print("💡 這是簡化版本，使用規則基礎的文案生成")
    print("-" * 50)
    
    try:
        # 設置環境變數
        os.environ.setdefault('FLASK_ENV', 'development')
        os.environ.setdefault('FLASK_DEBUG', 'True')
        
        # 啟動應用
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n👋 應用已停止")
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
