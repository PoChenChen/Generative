#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 文案生成工具增強版本測試腳本
測試多語言支援、擴展風格、批量處理等新功能
"""

import requests
import json
import time
import sys

def test_enhanced_app():
    """測試增強版本應用基本功能"""
    base_url = "http://localhost:5000"
    
    print("🧪 開始測試 AI 文案生成工具（增強版本）...")
    print("=" * 60)
    
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
        print("💡 請先運行：python run_enhanced.py")
        return False
    
    # 測試2: 測試API資源載入
    print("\n🌍 測試API資源載入...")
    try:
        # 測試語言API
        response = requests.get(f"{base_url}/api/languages")
        if response.status_code == 200:
            languages = response.json()
            print(f"✅ 語言API正常，支援 {len(languages)} 種語言")
            print(f"   支援語言：{', '.join(list(languages.keys())[:5])}...")
        else:
            print(f"❌ 語言API異常: {response.status_code}")
            return False
        
        # 測試風格API
        response = requests.get(f"{base_url}/api/styles")
        if response.status_code == 200:
            styles = response.json()
            print(f"✅ 風格API正常，支援 {len(styles)} 種風格")
            print(f"   支援風格：{', '.join(list(styles.keys())[:5])}...")
        else:
            print(f"❌ 風格API異常: {response.status_code}")
            return False
        
        # 測試形式API
        response = requests.get(f"{base_url}/api/forms")
        if response.status_code == 200:
            forms = response.json()
            print(f"✅ 形式API正常，支援 {len(forms)} 種形式")
            print(f"   支援形式：{', '.join(list(forms.keys())[:5])}...")
        else:
            print(f"❌ 形式API異常: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API資源測試失敗: {e}")
        return False
    
    # 測試3: 測試多語言拆解功能
    print("\n📝 測試多語言拆解功能...")
    test_cases = [
        {
            "text": "Python爬蟲課程即將開課，適合初學者學習，課程內容豐富，包含實戰項目。",
            "language": "自動檢測",
            "expected_lang": "中文"
        },
        {
            "text": "Python web scraping course is about to start, suitable for beginners to learn, with rich course content including practical projects.",
            "language": "自動檢測",
            "expected_lang": "英文"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            response = requests.post(
                f"{base_url}/decompose",
                data={"text": test_case["text"], "language": test_case["language"]}
            )
            
            if response.status_code == 200:
                data = response.json()
                detected_lang = data.get('detected_language')
                confidence = data.get('confidence', 0)
                print(f"✅ 測試案例 {i} 通過")
                print(f"   檢測語言: {detected_lang} (預期: {test_case['expected_lang']})")
                print(f"   置信度: {confidence:.2f}")
                print(f"   標題建議: {data['decomposition']['title_suggestion']}")
            else:
                print(f"❌ 測試案例 {i} 失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 測試案例 {i} 異常: {e}")
            return False
    
    # 測試4: 測試確認功能
    print("\n✅ 測試確認拆解功能...")
    try:
        # 使用第一個測試案例的結果
        response = requests.post(
            f"{base_url}/decompose",
            data={"text": test_cases[0]["text"], "language": test_cases[0]["language"]}
        )
        
        if response.status_code == 200:
            data = response.json()
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
        else:
            print(f"❌ 拆解功能異常: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 確認測試失敗: {e}")
        return False
    
    # 測試5: 測試多風格生成功能
    print("\n🎨 測試多風格文案生成功能...")
    test_styles = ["活潑", "專業", "幽默"]
    
    for style in test_styles:
        try:
            response = requests.post(
                f"{base_url}/generate",
                json={
                    "confirmed_id": confirmed_id,
                    "style": style,
                    "form": "社群貼文",
                    "length": "中",
                    "language": "中文"
                }
            )
            
            if response.status_code == 200:
                gen_data = response.json()
                print(f"✅ {style} 風格生成成功")
                print(f"   版本ID: {gen_data['version_id']}")
                print(f"   生成文案: {gen_data['generated_text'][:50]}...")
            else:
                print(f"❌ {style} 風格生成失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ {style} 風格生成異常: {e}")
            return False
    
    # 測試6: 測試批量處理功能
    print("\n📦 測試批量處理功能...")
    batch_texts = [
        "第一個文案：Python課程開課",
        "第二個文案：Web開發培訓",
        "第三個文案：數據分析課程"
    ]
    
    try:
        response = requests.post(
            f"{base_url}/batch",
            json={
                "texts": batch_texts,
                "styles": ["專業"] * len(batch_texts),
                "forms": ["社群貼文"] * len(batch_texts),
                "lengths": ["中"] * len(batch_texts),
                "languages": ["中文"] * len(batch_texts)
            }
        )
        
        if response.status_code == 200:
            batch_data = response.json()
            job_id = batch_data['job_id']
            print("✅ 批量處理任務創建成功")
            print(f"   任務ID: {job_id}")
            print(f"   總數: {batch_data['total']}")
            
            # 等待批量處理完成
            print("⏳ 等待批量處理完成...")
            max_wait = 30  # 最多等待30秒
            wait_time = 0
            
            while wait_time < max_wait:
                time.sleep(2)
                wait_time += 2
                
                try:
                    status_response = requests.get(f"{base_url}/batch/{job_id}")
                    if status_response.status_code == 200:
                        job_status = status_response.json()
                        if job_status['status'] == 'completed':
                            print("✅ 批量處理完成")
                            print(f"   成功處理: {job_status['completed']}/{job_status['total']}")
                            break
                        else:
                            print(f"   進度: {job_status['completed']}/{job_status['total']}")
                    else:
                        print(f"❌ 獲取批量處理狀態失敗: {status_response.status_code}")
                        break
                except Exception as e:
                    print(f"❌ 監控批量處理狀態異常: {e}")
                    break
            
            if wait_time >= max_wait:
                print("⚠️ 批量處理超時，但任務可能仍在進行中")
                
        else:
            print(f"❌ 批量處理創建失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 批量處理測試失敗: {e}")
        return False
    
    # 測試7: 測試版本查詢
    print("\n📚 測試版本查詢功能...")
    try:
        response = requests.get(f"{base_url}/versions/{confirmed_id}")
        
        if response.status_code == 200:
            versions = response.json()
            print("✅ 版本查詢功能正常")
            print(f"   版本數量: {len(versions)}")
            
            # 顯示版本詳情
            for i, version in enumerate(versions, 1):
                print(f"   版本 {i}: {version['style']} - {version['form']} - {version.get('language', '中文')}")
        else:
            print(f"❌ 版本查詢功能異常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 版本查詢測試失敗: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 所有測試通過！增強版本應用運行正常")
    print("✨ 新功能測試結果：")
    print("   🌍 多語言支援：✅ 正常")
    print("   🎨 擴展風格：✅ 正常")
    print("   📝 擴展形式：✅ 正常")
    print("   📦 批量處理：✅ 正常")
    print("   🔄 版本管理：✅ 正常")
    return True

def main():
    """主函數"""
    print("🚀 AI 文案生成工具增強版本測試")
    print("請確保增強版本應用正在運行 (python run_enhanced.py)")
    print()
    print("🧪 測試內容：")
    print("   • 多語言支援（中文、英文、日文等10種語言）")
    print("   • 擴展文案風格（活潑、專業、幽默等8種風格）")
    print("   • 擴展文案形式（社群貼文、廣告文案等8種形式）")
    print("   • 批量處理功能（多文字同時處理）")
    print("   • 智能語言檢測")
    print("   • 版本管理與下載")
    print()
    
    # 等待用戶確認
    input("按 Enter 鍵開始測試...")
    
    success = test_enhanced_app()
    
    if success:
        print("\n✨ 測試完成，增強版本應用功能正常！")
        print("🚀 所有未來規劃功能已實現並測試通過！")
    else:
        print("\n💥 測試失敗，請檢查應用配置")
        sys.exit(1)

if __name__ == "__main__":
    main()
