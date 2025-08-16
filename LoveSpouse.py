from flask import Flask, render_template_string, request
import serial
import threading

app = Flask(__name__)

# Настройка COM-порта
SERIAL_PORT = "COM5"
BAUD_RATE = 115200
ser = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Love Spouse</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #1e1e2f, #12121d);
            color: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            overflow: hidden;
            position: relative;
        }
        .graph-container {
            width: 100%;
            max-width: 140px;
            height: 112px;
            border-radius: 24px;
            margin-bottom: -118px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }
        .graph-bar {
            position: absolute;
            bottom: 0;
            width: 5px;
            background: linear-gradient(135deg, #EE82EE, #FF1493);
            transition: transform 0.2s ease;
            border-radius: 5px; /* Добавляем скругление */
        }
        .container {
            display: flex;
            align-items: flex-start;
            gap: 30px;
            border-radius: 24px;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(10px);
        }
        .vertical-slider {
            width: 80px; /* Сделали слайдер уже */
            height: 350px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            cursor: pointer;
            position: relative;
            overflow: hidden;
            box-shadow: inset 0 4px 8px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .slider-level {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            background: linear-gradient(135deg, #EE82EE, #FF1493);
            transition: height 0.2s ease;
            border-radius: 24px 24px 0 0;
        }
        .button-container {
            display: flex;
            flex-direction: column;
            gap: 15px;
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
        }
        .button {
            width: 80px;
            height: 80px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: none;
            border-radius: 24px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            text-align: center;
            line-height: 60px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .button:hover { background: rgba(76, 175, 80, 0.3); }
        .button:active { transform: scale(0.95); }
        .button.active {
            background: linear-gradient(135deg, #EE82EE, #FF1493);
            box-shadow: 0 4px 12px rgba(238, 130, 238, 0.5);
        }
        .random-button {
            width: 80px;
            height: 80px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: none;
            border-radius: 24px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            text-align: center;
            line-height: 60px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .random-button:hover { background: rgba(76, 175, 80, 0.3); }
        .random-button.active {
            background: linear-gradient(135deg, #EE82EE, #FF1493);
        }
        .timer-area {
            width: 80px;
            height: 80px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            margin-bottom: 15px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="graph-container" id="graphContainer"></div>
    <div class="container">
        <div>
            <div class="timer-area">00:00</div>
            <div class="vertical-slider" id="powerSlider" onclick="handleSliderClick(event)" onmousedown="startDrag(event)">
                <div class="slider-level" id="sliderLevel" style="height: 0;"></div>
            </div>
        </div>
    </div>
    <div class="button-container">
        <button class="button" id="button8" onclick="toggleMode(8)">Mode 1</button>
        <button class="button" id="button9" onclick="toggleMode(9)">Mode 2</button>
        <button class="button" id="button10" onclick="toggleMode(10)">Mode 3</button>
        <button class="button" id="button11" onclick="toggleMode(11)">Mode 4</button>
        <button class="button" id="button12" onclick="toggleMode(12)">Mode 5</button>
        <button class="button" id="button13" onclick="toggleMode(13)">Mode 6</button>
        <button class="random-button" id="randomButton" onclick="toggleRandomMode()">Random</button>
        <button class="random-button" id="smoothButton" onclick="toggleSmoothMode()">Random2</button>
    </div>
    <script>
        let activeButtonId = null, currentLevel = 0, isDragging = false;
        let isRandomModeActive = false, isSmoothModeActive = false;
        let randomInterval = null, smoothInterval = null;
        const graphContainer = document.getElementById('graphContainer');
        const maxBars = 130, barWidth = 5, updateInterval = 100;

        function updateGraph(level) {
            const bar = document.createElement('div');
            bar.classList.add('graph-bar');
            bar.style.height = `${(level / 7) * 100}%`;
            bar.style.right = '0';
            graphContainer.prepend(bar);
            const bars = graphContainer.querySelectorAll('.graph-bar');
            bars.forEach((bar, index) => bar.style.transform = `translateX(-${index * barWidth}px)`);
            if (bars.length > maxBars) graphContainer.removeChild(bars[bars.length - 1]);
        }

        function updateSliderLevel(level) {
            currentLevel = level;
            document.getElementById('sliderLevel').style.height = (level / 7) * 100 + '%';
        }

        function sendPowerLevel(level) {
            fetch('/setPowerLevel', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'level=' + level
            });
        }

        function handleSliderClick(event) {
            const slider = document.getElementById('powerSlider');
            const clickY = event.clientY - slider.getBoundingClientRect().top;
            let level = Math.round((1 - clickY / slider.offsetHeight) * 7);
            level = Math.max(0, Math.min(level, 7));
            updateSliderLevel(level);
            sendPowerLevel(level);
            updateGraph(level);
        }

        function startDrag(event) {
            isDragging = true;
            document.addEventListener('mousemove', handleDrag);
            document.addEventListener('mouseup', stopDrag);
            handleDrag(event);
        }

        function handleDrag(event) {
            if (isDragging) {
                const slider = document.getElementById('powerSlider');
                const clickY = event.clientY - slider.getBoundingClientRect().top;
                let level = Math.round((1 - clickY / slider.offsetHeight) * 7);
                level = Math.max(0, Math.min(level, 7));
                updateSliderLevel(level);
                sendPowerLevel(level);
                updateGraph(level);
            }
        }

        function stopDrag() {
            isDragging = false;
            document.removeEventListener('mousemove', handleDrag);
            document.removeEventListener('mouseup', stopDrag);
        }

        document.addEventListener('wheel', (event) => {
            let newLevel = currentLevel;
            newLevel += event.deltaY < 0 ? 1 : -1;
            newLevel = Math.max(0, Math.min(newLevel, 7));
            updateSliderLevel(newLevel);
            sendPowerLevel(newLevel);
            updateGraph(newLevel);
            event.preventDefault();
        }, { passive: false });

        function toggleMode(buttonId) {
            const button = document.getElementById('button' + buttonId);
            if (activeButtonId === buttonId) {
                activeButtonId = null;
                button.classList.remove('active');
                fetch('/activateButton', { method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body: 'button=0' });
            } else {
                if (activeButtonId !== null) document.getElementById('button' + activeButtonId).classList.remove('active');
                activeButtonId = buttonId;
                button.classList.add('active');
                fetch('/activateButton', { method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body: 'button=' + buttonId });
            }
        }

        function resetAllModes() {
            updateSliderLevel(0);
            sendPowerLevel(0);
            for (let i = 8; i <= 13; i++) {
                const button = document.getElementById('button' + i);
                if (button.classList.contains('active')) button.classList.remove('active');
            }
            fetch('/activateButton', { method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body: 'button=0' });
        }

        function toggleRandomMode() {
            const button = document.getElementById('randomButton');
            if (isRandomModeActive) {
                clearInterval(randomInterval);
                button.textContent = 'Random';
                button.classList.remove('active');
                resetAllModes();
            } else {
                button.textContent = 'Random';
                button.classList.add('active');
                randomInterval = setInterval(() => {
                    const randomLevel = Math.floor(Math.random() * 8);
                    updateSliderLevel(randomLevel);
                    sendPowerLevel(randomLevel);
                    updateGraph(randomLevel);
                }, 1000);
            }
            isRandomModeActive = !isRandomModeActive;
        }

        function toggleSmoothMode() {
            const button = document.getElementById('smoothButton');
            if (isSmoothModeActive) {
                clearInterval(smoothInterval);
                button.textContent = 'Random2';
                button.classList.remove('active');
                resetAllModes();
            } else {
                button.textContent = 'Random2';
                button.classList.add('active');
                let targetLevel = Math.floor(Math.random() * 8);
                smoothInterval = setInterval(() => {
                    if (currentLevel !== targetLevel) {
                        currentLevel += currentLevel < targetLevel ? 1 : -1;
                        updateSliderLevel(currentLevel);
                        sendPowerLevel(currentLevel);
                        updateGraph(currentLevel);
                    } else {
                        targetLevel = Math.floor(Math.random() * 8);
                    }
                }, Math.floor(Math.random() * 150) + 50);
            }
            isSmoothModeActive = !isSmoothModeActive;
        }

        setInterval(() => updateGraph(currentLevel), updateInterval);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/setPowerLevel', methods=['POST'])
def set_power_level():
    try:
        level = int(request.form.get('level', '0'))
        if 0 <= level <= 7:
            send_command_to_esp32(level)
    except ValueError:
        pass
    return '', 204

@app.route('/activateButton', methods=['POST'])
def activate_button():
    try:
        button = int(request.form.get('button', '0'))
        if 0 <= button <= 13:
            send_command_to_esp32(button)
    except ValueError:
        pass
    return '', 204

def send_command_to_esp32(command):
    global ser
    if ser and ser.is_open:
        ser.write(f"{command}\n".encode())

def start_serial():
    global ser
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to {SERIAL_PORT}")
    except Exception as e:
        print(f"Error opening serial port: {e}")

if __name__ == '__main__':
    threading.Thread(target=start_serial, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
