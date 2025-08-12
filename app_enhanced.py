#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 文案生成工具 - 增強版本
實現 readme 中的未來規劃功能
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import re
from datetime import datetime
import uuid
import random
import zipfile
from io import BytesIO

app = Flask(__name__)

# 儲存版本紀錄
versions = {}
batch_jobs = {}

# 支援的語言列表
SUPPORTED_LANGUAGES = {
    "中文": "zh",
    "英文": "en", 
    "日文": "ja",
    "韓文": "ko",
    "法文": "fr",
    "德文": "de",
    "西班牙文": "es",
    "葡萄牙文": "pt",
    "義大利文": "it",
    "俄文": "ru"
}

# 擴展的文案風格
ENHANCED_STYLES = {
    "活潑": {
        "description": "適合年輕族群，使用輕鬆活潑的語言",
        "emoji": "🎉",
        "tone": "輕鬆、有趣、充滿活力"
    },
    "專業": {
        "description": "適合商業場合，使用正式專業的語言",
        "emoji": "💼",
        "tone": "嚴謹、專業、可信賴"
    },
    "學術": {
        "description": "適合研究報告，使用嚴謹學術的語言",
        "emoji": "📚",
        "tone": "嚴謹、客觀、學術性"
    },
    "幽默": {
        "description": "適合娛樂場合，使用風趣幽默的語言",
        "emoji": "😂",
        "tone": "風趣、幽默、輕鬆"
    },
    "溫馨": {
        "description": "適合情感表達，使用溫暖親切的語言",
        "emoji": "💝",
        "tone": "溫暖、親切、關懷"
    },
    "激勵": {
        "description": "適合鼓舞人心，使用激勵性的語言",
        "emoji": "🔥",
        "tone": "激勵、鼓舞、正能量"
    },
    "神秘": {
        "description": "適合懸疑內容，使用神秘吸引的語言",
        "emoji": "🔮",
        "tone": "神秘、吸引、懸疑"
    },
    "優雅": {
        "description": "適合高端場合，使用優雅精緻的語言",
        "emoji": "✨",
        "tone": "優雅、精緻、高端"
    }
}

# 擴展的文案形式
ENHANCED_FORMS = {
    "社群貼文": {
        "description": "適合社群媒體的短文案，吸引眼球",
        "max_length": 200,
        "hashtag_support": True
    },
    "Email標題": {
        "description": "吸引人的Email標題，提高開信率",
        "max_length": 100,
        "hashtag_support": False
    },
    "完整文章": {
        "description": "完整的文章內容，詳細說明",
        "max_length": 1000,
        "hashtag_support": False
    },
    "廣告文案": {
        "description": "商業廣告文案，突出賣點",
        "max_length": 300,
        "hashtag_support": True
    },
    "新聞稿": {
        "description": "正式的新聞發布稿",
        "max_length": 500,
        "hashtag_support": False
    },
    "產品描述": {
        "description": "產品功能與特色描述",
        "max_length": 400,
        "hashtag_support": True
    },
    "活動宣傳": {
        "description": "活動推廣與宣傳文案",
        "max_length": 350,
        "hashtag_support": True
    },
    "品牌故事": {
        "description": "品牌理念與故事敘述",
        "max_length": 600,
        "hashtag_support": False
    }
}

def clean_text(text):
    """清理文字，去除多餘空格和亂碼"""
    # 去除多餘空格
    text = re.sub(r'\s+', ' ', text)
    # 去除特殊字符
    text = re.sub(r'[^\w\s\u4e00-\u9fff。，！？；：""''（）【】]', '', text)
    return text.strip()

def detect_language_enhanced(text):
    """增強的語言檢測"""
    # 語言特徵檢測
    language_scores = {}
    
    # 中文檢測
    chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
    language_scores['中文'] = chinese_chars
    
    # 英文檢測
    english_chars = len([c for c in text if c.isalpha() and ord(c) < 128])
    language_scores['英文'] = english_chars
    
    # 日文檢測
    japanese_chars = len([c for c in text if '\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff'])
    language_scores['日文'] = japanese_chars
    
    # 韓文檢測
    korean_chars = len([c for c in text if '\uac00' <= c <= '\ud7af'])
    language_scores['韓文'] = korean_chars
    
    # 返回得分最高的語言
    detected_lang = max(language_scores, key=language_scores.get)
    confidence = language_scores[detected_lang] / max(1, len(text))
    
    return detected_lang, confidence

def decompose_text_enhanced(text, language):
    """增強的內容拆解"""
    sentences = [s.strip() for s in text.split("。") if s.strip()]
    title = sentences[0][:30] + "..." if len(sentences[0]) > 30 else sentences[0]
    
    # 智能分析文案目的
    purpose_keywords = {
        "推廣": ["推廣", "宣傳", "廣告", "行銷", "銷售"],
        "教育": ["教學", "學習", "課程", "培訓", "教育"],
        "資訊": ["資訊", "消息", "公告", "通知", "報告"],
        "娛樂": ["娛樂", "有趣", "好玩", "精彩", "刺激"],
        "服務": ["服務", "幫助", "支援", "協助", "諮詢"]
    }
    
    detected_purpose = "資訊傳達"
    for purpose, keywords in purpose_keywords.items():
        if any(keyword in text for keyword in keywords):
            detected_purpose = purpose
            break
    
    # 智能分析目標受眾
    audience_keywords = {
        "年輕人": ["年輕人", "學生", "青年", "青少年"],
        "上班族": ["上班族", "職場", "工作", "專業"],
        "家長": ["家長", "父母", "家庭", "孩子"],
        "企業": ["企業", "公司", "商業", "B2B"],
        "一般大眾": ["大眾", "所有人", "大家", "各位"]
    }
    
    detected_audience = "一般讀者"
    for audience, keywords in audience_keywords.items():
        if any(keyword in text for keyword in keywords):
            detected_audience = audience
            break
    
    decomposition = {
        "title_suggestion": title,
        "audience": detected_audience,
        "purpose": detected_purpose,
        "tone": "專業、友善",
        "length": "200-300字",
        "key_points": sentences[:5],
        "facts_or_constraints": [],
        "call_to_action": "了解更多資訊",
        "language": language,
        "confidence": 0.8
    }
    
    return decomposition

def generate_content_enhanced(decomposition, style, form, length, language="中文"):
    """增強的文案生成"""
    
    # 獲取風格和形式的詳細資訊
    style_info = ENHANCED_STYLES.get(style, {})
    form_info = ENHANCED_FORMS.get(form, {})
    
    # 多語言模板
    templates = {
        "中文": {
            "活潑": {
                "社群貼文": "🎉 超棒的{title}來啦！{key_points} 快來看看吧！",
                "Email標題": "🔥 不容錯過：{title}",
                "完整文章": "親愛的朋友們！{title} 真的超級棒！{key_points} 相信你一定會喜歡的！"
            },
            "專業": {
                "社群貼文": "專業{title}，{key_points}，值得信賴的選擇。",
                "Email標題": "專業服務：{title}",
                "完整文章": "我們很榮幸為您介紹{title}。{key_points} 我們的專業團隊將為您提供最優質的服務。"
            }
        },
        "英文": {
            "活潑": {
                "社群貼文": "🎉 Amazing {title} is here! {key_points} Check it out!",
                "Email標題": "🔥 Don't miss: {title}",
                "完整文章": "Hey everyone! {title} is absolutely fantastic! {key_points} You're going to love it!"
            },
            "專業": {
                "社群貼文": "Professional {title}, {key_points}, a choice you can trust.",
                "Email標題": "Professional Service: {title}",
                "完整文章": "We are honored to introduce {title}. {key_points} Our professional team will provide you with the highest quality service."
            }
        }
    }
    
    # 選擇模板
    lang_templates = templates.get(language, templates["中文"])
    style_templates = lang_templates.get(style, lang_templates["專業"])
    template = style_templates.get(form, "這是關於{title}的內容。{key_points}")
    
    # 填充內容
    key_points_text = "、".join(decomposition['key_points'][:3])
    generated_text = template.format(
        title=decomposition['title_suggestion'],
        key_points=key_points_text
    )
    
    # 根據長度調整
    max_length = form_info.get("max_length", 300)
    if length == "短":
        generated_text = generated_text[:max_length//3] + "..."
    elif length == "中":
        generated_text = generated_text[:max_length//2]
    elif length == "長":
        generated_text = generated_text[:max_length]
    
    # 添加標籤（如果支援）
    if form_info.get("hashtag_support", False):
        hashtags = f"\n\n#{style}#{form}#{language}"
        generated_text += hashtags
    
    return generated_text

def create_batch_job(texts, styles, forms, lengths, languages):
    """創建批量處理任務"""
    job_id = str(uuid.uuid4())
    
    batch_jobs[job_id] = {
        "id": job_id,
        "status": "processing",
        "total": len(texts),
        "completed": 0,
        "results": [],
        "created_at": datetime.now().isoformat()
    }
    
    # 模擬批量處理
    for i, text in enumerate(texts):
        try:
            # 處理每個文字
            decomposition = decompose_text_enhanced(text, languages[i] if i < len(languages) else "中文")
            generated_text = generate_content_enhanced(
                decomposition, 
                styles[i] if i < len(styles) else "專業",
                forms[i] if i < len(forms) else "完整文章",
                lengths[i] if i < len(lengths) else "中",
                languages[i] if i < len(languages) else "中文"
            )
            
            batch_jobs[job_id]["results"].append({
                "index": i,
                "original_text": text,
                "decomposition": decomposition,
                "generated_text": generated_text,
                "style": styles[i] if i < len(styles) else "專業",
                "form": forms[i] if i < len(forms) else "完整文章",
                "length": lengths[i] if i < len(lengths) else "中",
                "language": languages[i] if i < len(languages) else "中文"
            })
            
            batch_jobs[job_id]["completed"] += 1
            
        except Exception as e:
            batch_jobs[job_id]["results"].append({
                "index": i,
                "error": str(e)
            })
    
    batch_jobs[job_id]["status"] = "completed"
    return job_id

@app.route("/")
def index():
    return render_template("index_enhanced.html")

@app.route("/api/languages")
def get_languages():
    """獲取支援的語言列表"""
    return jsonify(SUPPORTED_LANGUAGES)

@app.route("/api/styles")
def get_styles():
    """獲取支援的文案風格"""
    return jsonify(ENHANCED_STYLES)

@app.route("/api/forms")
def get_forms():
    """獲取支援的文案形式"""
    return jsonify(ENHANCED_FORMS)

@app.route("/decompose", methods=["POST"])
def decompose():
    """Step 1: 拆解原始文字"""
    text = request.form.get("text", "")
    language = request.form.get("language", "自動檢測")
    
    if not text.strip():
        return jsonify({"error": "請輸入文字"}), 400
    
    # 清理文字
    cleaned_text = clean_text(text)
    
    # 檢測語言
    if language == "自動檢測":
        detected_lang, confidence = detect_language_enhanced(cleaned_text)
    else:
        detected_lang, confidence = language, 1.0
    
    # 拆解內容
    decomposition = decompose_text_enhanced(cleaned_text, detected_lang)
    
    return jsonify({
        "decomposition": decomposition,
        "detected_language": detected_lang,
        "confidence": confidence,
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
    
    # 儲存到檔案
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
    language = request.json.get("language", "中文")
    
    # 讀取確認的拆解內容
    try:
        with open(f"confirmed_{confirmed_id}.json", "r", encoding="utf-8") as f:
            confirmed_data = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "找不到確認的拆解內容"}), 404
    
    decomposition = confirmed_data["decomposition"]
    
    # 生成新文案
    generated_text = generate_content_enhanced(decomposition, style, form, length, language)
    
    # 儲存版本紀錄
    version_id = str(uuid.uuid4())
    version_data = {
        "id": version_id,
        "confirmed_id": confirmed_id,
        "timestamp": datetime.now().isoformat(),
        "style": style,
        "form": form,
        "length": length,
        "language": language,
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
            "language": language,
            "timestamp": version_data["timestamp"]
        }
    })

@app.route("/batch", methods=["POST"])
def batch_generate():
    """批量生成文案"""
    data = request.json
    texts = data.get("texts", [])
    styles = data.get("styles", ["專業"] * len(texts))
    forms = data.get("forms", ["完整文章"] * len(texts))
    lengths = data.get("lengths", ["中"] * len(texts))
    languages = data.get("languages", ["中文"] * len(texts))
    
    if not texts:
        return jsonify({"error": "請提供要處理的文字"}), 400
    
    # 創建批量任務
    job_id = create_batch_job(texts, styles, forms, lengths, languages)
    
    return jsonify({
        "job_id": job_id,
        "status": "processing",
        "total": len(texts)
    })

@app.route("/batch/<job_id>")
def get_batch_status(job_id):
    """獲取批量任務狀態"""
    if job_id not in batch_jobs:
        return jsonify({"error": "任務不存在"}), 404
    
    return jsonify(batch_jobs[job_id])

@app.route("/batch/<job_id>/download")
def download_batch_results(job_id):
    """下載批量處理結果"""
    if job_id not in batch_jobs:
        return jsonify({"error": "任務不存在"}), 404
    
    job = batch_jobs[job_id]
    if job["status"] != "completed":
        return jsonify({"error": "任務尚未完成"}), 400
    
    # 創建 ZIP 文件
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 添加結果文件
        for i, result in enumerate(job["results"]):
            if "error" not in result:
                filename = f"文案_{i+1}_{result['style']}_{result['form']}.txt"
                content = f"""文案內容：
{result['generated_text']}

生成參數：
風格：{result['style']}
形式：{result['form']}
長度：{result['length']}
語言：{result['language']}
生成時間：{datetime.now().isoformat()}
"""
                zf.writestr(filename, content.encode('utf-8'))
    
    memory_file.seek(0)
    
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f"批量文案_{job_id[:8]}.zip"
    )

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
        f.write(f"語言：{version['language']}\n")
        f.write(f"生成時間：{version['timestamp']}\n")
    
    return send_file(temp_file, as_attachment=True, download_name=filename)

@app.route("/regenerate", methods=["POST"])
def regenerate():
    """重新生成文案"""
    confirmed_id = request.json.get("confirmed_id")
    style = request.json.get("style")
    form = request.json.get("form")
    length = request.json.get("length")
    language = request.json.get("language")
    
    # 如果沒有提供新參數，使用最後一個版本的參數
    if not all([style, form, length, language]):
        user_versions = [v for v in versions.values() if v["confirmed_id"] == confirmed_id]
        if user_versions:
            last_version = max(user_versions, key=lambda x: x["timestamp"])
            style = style or last_version["style"]
            form = form or last_version["form"]
            length = length or last_version["length"]
            language = language or last_version.get("language", "中文")
    
    # 調用生成函數
    return generate()

if __name__ == "__main__":
    print("🚀 啟動 AI 文案生成工具（增強版本）...")
    print("📱 應用將在 http://localhost:5000 運行")
    print("🔄 按 Ctrl+C 停止應用")
    print("✨ 新功能：多語言支援、擴展風格、批量處理")
    print("-" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
