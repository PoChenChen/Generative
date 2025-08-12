#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 文案生成工具增強版本啟動腳本
實現 readme 中的未來規劃功能
"""

import os
import sys
from app_enhanced import app

def main():
    """主函數"""
    print("🚀 啟動 AI 文案生成工具（增強版本）...")
    print("📱 應用將在 http://localhost:5000 運行")
    print("🔄 按 Ctrl+C 停止應用")
    print("✨ 新功能：多語言支援、擴展風格、批量處理")
    print("🌍 支援語言：中文、英文、日文、韓文、法文、德文、西班牙文、葡萄牙文、義大利文、俄文")
    print("🎨 文案風格：活潑、專業、學術、幽默、溫馨、激勵、神秘、優雅")
    print("📝 文案形式：社群貼文、Email標題、完整文章、廣告文案、新聞稿、產品描述、活動宣傳、品牌故事")
    print("📦 批量處理：支援多文字同時處理，提高工作效率")
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
