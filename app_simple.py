#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 文案生成工具 - 簡化版本（不依賴 Transformers）
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import re
from datetime import datetime
import uuid
import random

app = Flask(__name__)

# 儲存版本紀錄
versions = {}

def clean_text(text):
    """清理文字，去除多餘空格和亂碼"""
    # 去除多餘空格
    text = re.sub(r'\s+', ' ', text)
    # 去除特殊字符
    text = re.sub(r'[^\w\s\u4e00-\u9fff。，！？；：""''（）【】]', '', text)
    return text.strip()

def detect_language(text):
    """簡單的語言檢測"""
    chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
    english_chars = len([c for c in text if c.isalpha()])
    
    if chinese_chars > english_chars:
        return "中文"
    else:
        return "英文"

def decompose_text(text):
    """使用簡單規則將文章拆成結構化資訊"""
    # 簡單的標題提取（取第一句）
    sentences = [s.strip() for s in text.split("。") if s.strip()]
    title = sentences[0][:30] + "..." if len(sentences[0]) > 30 else sentences[0]
    
    # 模擬拆解結果
    decomposition = {
        "title_suggestion": title,
        "audience": "一般讀者",
        "purpose": "資訊傳達",
        "tone": "專業、友善",
        "length": "200-300字",
        "key_points": sentences[:5],  # 取前5句作為要點
        "facts_or_constraints": [],
        "call_to_action": "了解更多資訊"
    }
    
    return decomposition

def generate_content_simple(decomposition, style, form, length):
    """使用簡單規則生成文案"""
    
    # 文案模板
    templates = {
        "活潑": {
            "社群貼文": "🎉 超棒的{title}來啦！{key_points} 快來看看吧！",
            "Email標題": "🔥 不容錯過：{title}",
            "完整文章": "親愛的朋友們！{title} 真的超級棒！{key_points} 相信你一定會喜歡的！"
        },
        "專業": {
            "社群貼文": "專業{title}，{key_points}，值得信賴的選擇。",
            "Email標題": "專業服務：{title}",
            "完整文章": "我們很榮幸為您介紹{title}。{key_points} 我們的專業團隊將為您提供最優質的服務。"
        },
        "學術": {
            "社群貼文": "研究發現：{title}，{key_points}，具有重要意義。",
            "Email標題": "學術研究：{title}",
            "完整文章": "本研究探討了{title}的相關問題。{key_points} 研究結果顯示了重要的學術價值。"
        },
        "幽默": {
            "社群貼文": "😂 聽說{title}超厲害！{key_points} 要不要來試試看？",
            "Email標題": "😄 有趣的消息：{title}",
            "完整文章": "哈哈，今天要跟大家分享一個有趣的話題：{title}！{key_points} 保證讓你笑到肚子痛！"
        }
    }
    
    # 選擇模板
    template = templates.get(style, {}).get(form, "這是關於{title}的內容。{key_points}")
    
    # 填充內容
    key_points_text = "、".join(decomposition['key_points'][:3])
    generated_text = template.format(
        title=decomposition['title_suggestion'],
        key_points=key_points_text
    )
    
    # 根據長度調整
    if length == "短":
        generated_text = generated_text[:100] + "..."
    elif length == "長":
        generated_text = generated_text + " 更多詳細內容請關注我們的更新。"
    
    return generated_text

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/decompose", methods=["POST"])
def decompose():
    """Step 1: 拆解原始文字"""
    text = request.form.get("text", "")
    language = request.form.get("language", "中文")
    
    if not text.strip():
        return jsonify({"error": "請輸入文字"}), 400
    
    # 清理文字
    cleaned_text = clean_text(text)
    
    # 檢測語言
    detected_lang = detect_language(cleaned_text)
    
    # 拆解內容
    decomposition = decompose_text(cleaned_text)
    
    return jsonify({
        "decomposition": decomposition,
        "detected_language": detected_lang,
        "cleaned_text": cleaned_text
    })

@app.route("/confirm", methods=["POST"])
def confirm():
    """Step 2: 使用者確認拆解內容"""
    decomposition = request.json.get("decomposition", {})
    
    # 儲存確認後的拆解內容
    confirmed_id = str(uuid.uuid4())
    confirmed_data = {
        "id": confirmed_id,
        "timestamp": datetime.now().isoformat(),
        "decomposition": decomposition
    }
    
    # 儲存到檔案（實際應用中可以使用資料庫）
    with open(f"confirmed_{confirmed_id}.json", "w", encoding="utf-8") as f:
        json.dump(confirmed_data, f, ensure_ascii=False, indent=2)
    
    return jsonify({"confirmed_id": confirmed_id})

@app.route("/generate", methods=["POST"])
def generate():
    """Step 3: 生成新文案"""
    confirmed_id = request.json.get("confirmed_id")
    style = request.json.get("style", "專業")
    form = request.json.get("form", "完整文章")
    length = request.json.get("length", "中")
    
    # 讀取確認的拆解內容
    try:
        with open(f"confirmed_{confirmed_id}.json", "r", encoding="utf-8") as f:
            confirmed_data = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "找不到確認的拆解內容"}), 404
    
    decomposition = confirmed_data["decomposition"]
    
    # 生成新文案
    generated_text = generate_content_simple(decomposition, style, form, length)
    
    # 儲存版本紀錄
    version_id = str(uuid.uuid4())
    version_data = {
        "id": version_id,
        "confirmed_id": confirmed_id,
        "timestamp": datetime.now().isoformat(),
        "style": style,
        "form": form,
        "length": length,
        "generated_text": generated_text
    }
    
    versions[version_id] = version_data
    
    return jsonify({
        "version_id": version_id,
        "generated_text": generated_text,
        "metadata": {
            "style": style,
            "form": form,
            "length": length,
            "timestamp": version_data["timestamp"]
        }
    })

@app.route("/versions/<confirmed_id>")
def get_versions(confirmed_id):
    """獲取特定拆解內容的所有版本"""
    user_versions = [v for v in versions.values() if v["confirmed_id"] == confirmed_id]
    return jsonify(user_versions)

@app.route("/download/<version_id>")
def download_version(version_id):
    """下載特定版本的文案"""
    if version_id not in versions:
        return jsonify({"error": "版本不存在"}), 404
    
    version = versions[version_id]
    filename = f"文案_{version['style']}_{version['form']}_{version['timestamp'][:10]}.txt"
    
    # 創建臨時檔案
    temp_file = f"temp_{filename}"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(f"文案內容：\n{version['generated_text']}\n\n")
        f.write(f"生成參數：\n")
        f.write(f"風格：{version['style']}\n")
        f.write(f"形式：{version['form']}\n")
        f.write(f"長度：{version['length']}\n")
        f.write(f"生成時間：{version['timestamp']}\n")
    
    return send_file(temp_file, as_attachment=True, download_name=filename)

@app.route("/regenerate", methods=["POST"])
def regenerate():
    """重新生成文案（同參數或改參數）"""
    confirmed_id = request.json.get("confirmed_id")
    style = request.json.get("style")
    form = request.json.get("form")
    length = request.json.get("length")
    
    # 如果沒有提供新參數，使用最後一個版本的參數
    if not all([style, form, length]):
        user_versions = [v for v in versions.values() if v["confirmed_id"] == confirmed_id]
        if user_versions:
            last_version = max(user_versions, key=lambda x: x["timestamp"])
            style = style or last_version["style"]
            form = form or last_version["form"]
            length = length or last_version["length"]
    
    # 調用生成函數
    return generate()

if __name__ == "__main__":
    print("🚀 啟動 AI 文案生成工具（簡化版本）...")
    print("📱 應用將在 http://localhost:5000 運行")
    print("🔄 按 Ctrl+C 停止應用")
    print("-" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
