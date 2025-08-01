import customtkinter as ctk
import serial
import time
import google.generativeai as genai
from threading import Thread
import re

# ============ CONFIG =============
SERIAL_PORT = "COM3"  # Change to your Arduino COM port
BAUD_RATE = 9600
GEMINI_API_KEY = "AIzaSyCuM_l7gDak-8y5tIefRVXE_QKfOYhoulo"  # Replace with your Gemini API key
# =================================

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# --- App UI Setup ---
app = ctk.CTk()
app.geometry("650x720")
app.title("🌱 AI Crop Advisor (Live from Arduino + Chatbot)")

title_label = ctk.CTkLabel(app, text="🌿 Smart Farming Advisor", font=ctk.CTkFont(size=24, weight="bold"))
title_label.pack(pady=10)

# ===== Scrollable Frame =====
scroll_frame = ctk.CTkScrollableFrame(app, width=620, height=620)
scroll_frame.pack(pady=10)

# ======= Sensor Section =======
sensor_title = ctk.CTkLabel(scroll_frame, text="📟 Live Sensor Data", font=ctk.CTkFont(size=18, weight="bold"))
sensor_title.pack(pady=(10, 5))

data_display = ctk.CTkLabel(scroll_frame, text="Waiting for sensor data...", font=ctk.CTkFont(size=14))
data_display.pack(pady=5)

result_label = ctk.CTkLabel(scroll_frame, text="", wraplength=580, justify="left", font=ctk.CTkFont(size=14))
result_label.pack(pady=10)

loading_label = ctk.CTkLabel(scroll_frame, text="", font=ctk.CTkFont(size=12))
loading_label.pack()

# ======= Chatbot Section =======
chat_title = ctk.CTkLabel(scroll_frame, text="🧠 Ask Any Question (Farming Help)", font=ctk.CTkFont(size=18, weight="bold"))
chat_title.pack(pady=(20, 5))

chat_entry = ctk.CTkEntry(scroll_frame, placeholder_text="Type your farming question here...", width=500)
chat_entry.pack(pady=5)

chat_button = ctk.CTkButton(scroll_frame, text="Send", width=100)
chat_button.pack(pady=5)

chat_response_label = ctk.CTkLabel(scroll_frame, text="", wraplength=580, justify="left", font=ctk.CTkFont(size=14))
chat_response_label.pack(pady=10)

# -- Loading animation --
loading = False
def animate_loading():
    dots = ["", ".", "..", "..."]
    i = 0
    while loading:
        loading_label.configure(text="🌐 Thinking" + dots[i % 4])
        i += 1
        time.sleep(0.5)
    loading_label.configure(text="")

# -- Gemini prompt for sensor data --
def query_gemini(temp, hum, moist):
    prompt = (
        f"Suggest a suitable crop and give short reason in Hindi based on:\n"
        f"Temperature: {temp} °C\nHumidity: {hum} %\nSoil Moisture: {moist} %\n"
        f"Format:\nCrop: <name>\nReason: <short reason in Hindi>"
    )
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"

# -- Gemini prompt for chatbot --
def ask_chatbot(question):
    try:
        response = model.generate_content(question)
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"

# -- Serial reading and prediction --
def read_serial_and_predict():
    global loading
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        time.sleep(2)
        while True:
            line = ser.readline().decode().strip()
            match = re.search(r"TEMP:(\d+\.?\d*),HUM:(\d+\.?\d*),SOIL:(\d+)", line)
            if match:
                temp = float(match.group(1))
                hum = float(match.group(2))
                moist = int(match.group(3))

                display = f"🌡 Temp: {temp} °C | 💧 Humidity: {hum}% | 🌱 Soil: {moist}%"
                data_display.configure(text=display)

                loading = True
                Thread(target=animate_loading).start()

                def ask_gemini():
                    result = query_gemini(temp, hum, moist)
                    result_label.configure(text=result, text_color="lightgreen")
                    global loading
                    loading = False

                Thread(target=ask_gemini).start()

                time.sleep(10)

    except Exception as e:
        data_display.configure(text=f"❌ Serial Error: {e}")

# -- Chatbot Button Action --
def handle_chat():
    question = chat_entry.get()
    if not question.strip():
        chat_response_label.configure(text="❗ Please type a question.")
        return

    global loading
    loading = True
    Thread(target=animate_loading).start()

    def get_answer():
        response = ask_chatbot(question + " (in very short)")
        chat_response_label.configure(text=response, text_color="lightblue")
        global loading
        loading = False

    Thread(target=get_answer).start()

chat_button.configure(command=handle_chat)

# -- Start Reading Serial in Background --
Thread(target=read_serial_and_predict, daemon=True).start()

# -- Run App --
app.mainloop()
