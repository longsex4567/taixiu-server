from flask import Flask, request, jsonify
import json, time, os

app = Flask(__name__)

# ====================== CẤU HÌNH FILE LƯU ======================
RECHARGE_FILE = "recharge_codes.json"
WITHDRAW_FILE = "withdraw_history.json"

# ====================== API: TẠO MÃ NẠP (ADMIN) ======================
@app.route("/api/recharge", methods=["POST"])
def create_recharge_code():
    data = request.get_json()
    code = data.get("code", "").strip().upper()
    amount = int(data.get("amount", 0))

    if not code or amount <= 0:
        return jsonify({"ok": False, "msg": "Thiếu mã hoặc số tiền không hợp lệ."}), 400

    try:
        with open(RECHARGE_FILE, "r", encoding="utf8") as f:
            codes = json.load(f)
    except:
        codes = {}

    if code in codes:
        return jsonify({"ok": False, "msg": "Mã đã tồn tại."}), 400

    codes[code] = amount
    with open(RECHARGE_FILE, "w", encoding="utf8") as f:
        json.dump(codes, f, ensure_ascii=False, indent=2)

    print(f"✅ Tạo mã nạp: {code} — {amount:,} VNĐ")
    return jsonify({"ok": True, "msg": "Đã tạo mã nạp thành công."})


# ====================== API: KIỂM TRA MÃ NẠP (CLIENT) ======================
@app.route("/api/check_recharge", methods=["POST"])
def check_recharge():
    data = request.get_json()
    code = data.get("code", "").strip().upper()
    if not code:
        return jsonify({"ok": False, "msg": "Thiếu mã nạp tiền."}), 400

    try:
        with open(RECHARGE_FILE, "r", encoding="utf8") as f:
            codes = json.load(f)
    except:
        codes = {}

    if code not in codes:
        return jsonify({"ok": False, "msg": "Mã không hợp lệ hoặc đã sử dụng."})

    amount = codes.pop(code)
    with open(RECHARGE_FILE, "w", encoding="utf8") as f:
        json.dump(codes, f, ensure_ascii=False, indent=2)

    print(f"💰 Nạp thành công {amount:,} VNĐ với mã {code}")
    return jsonify({"ok": True, "amount": amount})


# ====================== API: RÚT TIỀN (CLIENT) ======================
@app.route("/api/withdraw", methods=["POST"])
def withdraw():
    data = request.get_json()
    bank = data.get("bank", "").strip()
    account = data.get("account", "").strip()
    amount = int(data.get("amount", 0))

    if not bank or not account or amount <= 0:
        return jsonify({"ok": False, "msg": "Thiếu thông tin hoặc số tiền không hợp lệ."}), 400

    try:
        with open(WITHDRAW_FILE, "r", encoding="utf8") as f:
            history = json.load(f)
    except:
        history = []

    history.append({
        "bank": bank,
        "account": account,
        "amount": amount,
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    })

    with open(WITHDRAW_FILE, "w", encoding="utf8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    print(f"💸 RÚT: {amount:,} VNĐ → {bank} ({account})")
    return jsonify({"ok": True, "msg": "Đã ghi nhận yêu cầu rút tiền."})


# ====================== CHẠY SERVER ======================
if __name__ == "__main__":
    print("=====================================")
    print("🚀 SERVER ĐANG CHẠY TẠI: http://127.0.0.1:5000")
    print("=====================================")
    app.run(host="0.0.0.0", port=5000)
