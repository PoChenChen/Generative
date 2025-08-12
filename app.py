from flask import Flask, render_template, request, jsonify, send_file
from transformers import pipeline
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)

# 初始化 Hugging Face 模型（離線）
# 使用更適合中文的模型
generator = pipeline("text-generation", model="gpt2")

# 儲存版本紀錄
versions = {}

def clean_text(text):
    """清理文字，去除多餘空格和亂碼"""
    import re
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
    """使用LLM將文章拆成結構化資訊"""
    # 這裡使用簡單的規則來模擬LLM拆解
    # 實際應用中可以替換為真正的LLM模型
    
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

def generate_content(decomposition, style, form, length):
    """根據拆解內容和參數生成新文案"""
    
    # 構建提示詞
    style_map = {
        "活潑": "活潑有趣的風格",
        "專業": "專業嚴謹的風格", 
        "學術": "學術研究的風格",
        "幽默": "幽默風趣的風格"
    }
    
    form_map = {
        "社群貼文": "適合社群媒體的短文案",
        "Email標題": "吸引人的Email標題",
        "完整文章": "完整的文章內容"
    }
    
    length_map = {
        "短": "100字以內",
        "中": "200-300字",
        "長": "500字以上"
    }
    
    prompt = f"""
    請根據以下拆解內容，生成一段{style_map.get(style, style)}的{form_map.get(form, form)}，
    字數要求：{length_map.get(length, length)}。
    
    拆解內容：
    標題：{decomposition['title_suggestion']}
    目標受眾：{decomposition['audience']}
    目的：{decomposition['purpose']}
    語調：{decomposition['tone']}
    關鍵要點：{', '.join(decomposition['key_points'])}
    
    請生成符合要求的文案：
    """
    
    # 使用模型生成
    try:
        result = generator(
            prompt,
            max_length=300,
            num_return_sequences=1,
            do_sample=True,
            temperature=0.8
        )[0]["generated_text"]
        
        # 清理生成結果
        generated_text = result.replace(prompt, "").strip()
        if not generated_text:
            generated_text = "無法生成文案，請重試。"
            
        return generated_text
    except Exception as e:
        return f"生成失敗：{str(e)}"

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
    generated_text = generate_content(decomposition, style, form, length)
    
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
    app.run(debug=True)
