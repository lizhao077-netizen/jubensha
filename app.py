import os
import certifi
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 允许跨域，解决前端调用问题

# --- 1. 数据库配置 ---

MONGO_URI = os.environ.get("MONGO_URI")


client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
# ... 其余逻辑不变 ...

try:
    # 使用 certifi.where() 解决 Windows 下的 SSL 证书校验问题
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client['ferris_wheel_db']  # 数据库名
    collection = db['messages']  # 表名（集合名）
    # 测试一下是否能连通
    client.admin.command('ping')
    print("✅ 成功连接到 MongoDB Atlas！")
except Exception as e:
    print(f"❌ 数据库连接失败: {e}")


# --- 2. 路由逻辑 ---

@app.route('/api/messages', methods=['GET'])
def get_messages():
    try:
        # 从数据库读取最新的 50 条消息，按 ID 倒序排列
        msgs = list(collection.find().sort("_id", -1).limit(50))

        results = []
        for m in reversed(msgs):  # 反转回正序显示在前端
            results.append({
                "user": m.get('user'),
                "content": m.get('content'),
                "avatar": m.get('avatar'),
                "time": m.get('time', datetime.now().strftime("%H:%M"))
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/messages', methods=['POST'])
def save_message():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "无数据"}), 400

    try:
        # 添加当前服务器时间
        data['time'] = datetime.now().strftime("%H:%M")
        # 直接插入到 MongoDB
        collection.insert_one(data)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    # 获取 Render 分配的端口，如果没有则默认 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
