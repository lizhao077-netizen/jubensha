import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- 环境检查 ---
try:
    import flask
    print(f"✅ Flask 环境配置成功！版本：{flask.__version__}")
except ImportError:
    print("❌ 报错：仍未找到 Flask。请尝试在 PyCharm 设置中手动安装。")
    exit()

app = Flask(__name__)
CORS(app)  # 允许手机跨域访问

DB_FILE = 'messages.json'

# 初始化数据文件
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

@app.route('/')
def home():
    return "摩天轮后端服务已启动！"

@app.route('/api/messages', methods=['GET'])
def get_messages():
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return jsonify(json.load(f))

@app.route('/api/messages', methods=['POST'])
def save_message():
    new_msg = request.json
    with open(DB_FILE, 'r+', encoding='utf-8') as f:
        messages = json.load(f)
        messages.append(new_msg)
        f.seek(0)
        json.dump(messages, f, ensure_ascii=False, indent=4)
        f.truncate()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    # Render 会通过环境变量指定端口，如果没有则默认 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)