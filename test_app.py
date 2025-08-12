#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 文案生成工具測試腳本
"""

import requests
import json
import time
import sys

def test_app():
    """測試應用基本功能"""
    base_url = "http://localhost:5000"
    
    print("🧪 開始測試 AI 文案生成工具...")
    print("=" * 50)
    
    # 測試1: 檢查應用是否運行
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ 應用運行正常")
        else:
            print(f"❌ 應用響應異常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到應用，請確保應用正在運行")
        return False
    
    # 測試2: 測試拆解功能
    print("\n📝 測試文字拆解功能...")
    test_text = "Python爬蟲課程即將開課，適合初學者學習，課程內容豐富，包含實戰項目。"
    
    try:
        response = requests.post(
            f"{base_url}/decompose",
            data={"text": test_text, "language": "中文"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 拆解功能正常")
            print(f"   檢測語言: {data.get('detected_language')}")
            print(f"   標題建議: {data['decomposition']['title_suggestion']}")
        else:
            print(f"❌ 拆解功能異常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 拆解測試失敗: {e}")
        return False
    
    # 測試3: 測試確認功能
    print("\n✅ 測試確認拆解功能...")
    try:
        decomposition = data['decomposition']
        response = requests.post(
            f"{base_url}/confirm",
            json={"decomposition": decomposition}
        )
        
        if response.status_code == 200:
            confirm_data = response.json()
            confirmed_id = confirm_data['confirmed_id']
            print("✅ 確認功能正常")
            print(f"   確認ID: {confirmed_id}")
        else:
            print(f"❌ 確認功能異常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 確認測試失敗: {e}")
        return False
    
    # 測試4: 測試生成功能
    print("\n🎨 測試文案生成功能...")
    try:
        response = requests.post(
            f"{base_url}/generate",
            json={
                "confirmed_id": confirmed_id,
                "style": "活潑",
                "form": "社群貼文",
                "length": "中"
            }
        )
        
        if response.status_code == 200:
            gen_data = response.json()
            print("✅ 生成功能正常")
            print(f"   版本ID: {gen_data['version_id']}")
            print(f"   生成文案: {gen_data['generated_text'][:100]}...")
        else:
            print(f"❌ 生成功能異常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 生成測試失敗: {e}")
        return False
    
    # 測試5: 測試版本查詢
    print("\n📚 測試版本查詢功能...")
    try:
        response = requests.get(f"{base_url}/versions/{confirmed_id}")
        
        if response.status_code == 200:
            versions = response.json()
            print("✅ 版本查詢功能正常")
            print(f"   版本數量: {len(versions)}")
        else:
            print(f"❌ 版本查詢功能異常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 版本查詢測試失敗: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 所有測試通過！應用運行正常")
    return True

def main():
    """主函數"""
    print("🚀 AI 文案生成工具測試")
    print("請確保應用正在運行 (python app.py)")
    print()
    
    # 等待用戶確認
    input("按 Enter 鍵開始測試...")
    
    success = test_app()
    
    if success:
        print("\n✨ 測試完成，應用功能正常！")
    else:
        print("\n💥 測試失敗，請檢查應用配置")
        sys.exit(1)

if __name__ == "__main__":
    main()
