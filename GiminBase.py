# import customtkinter as ctk
# from tkinter import messagebox
# import google.generativeai as genai
# from threading import Thread
# import time

# # Set your Gemini API key
# genai.configure(api_key="AIzaSyCuM_l7gDak-8y5tIefRVXE_QKfOYhoulo")  # 🔴 Replace with your key

# # Gemini model
# model = genai.GenerativeModel("gemini-2.0-flash")

# # App UI setup
# ctk.set_appearance_mode("dark")
# ctk.set_default_color_theme("green")

# app = ctk.CTk()
# app.geometry("600x550")
# app.title("🌾 Online AI Crop Advisor using Gemini")
# app.resizable(False, False)

# title_label = ctk.CTkLabel(app, text="🌿 Online Smart Farming Assistant", font=ctk.CTkFont(size=24, weight="bold"))
# title_label.pack(pady=15)

# input_frame = ctk.CTkFrame(app, corner_radius=12)
# input_frame.pack(pady=10, padx=20, fill="x")

# temp_entry = ctk.CTkEntry(input_frame, placeholder_text="🌡 Temperature (°C) / तापमान", height=40)
# temp_entry.pack(pady=10, padx=20, fill="x")

# hum_entry = ctk.CTkEntry(input_frame, placeholder_text="💧 Humidity (%) / नमी", height=40)
# hum_entry.pack(pady=10, padx=20, fill="x")

# moist_entry = ctk.CTkEntry(input_frame, placeholder_text="🌱 Soil Moisture (%) / मिट्टी की नमी", height=40)
# moist_entry.pack(pady=10, padx=20, fill="x")

# # Result area
# result_label = ctk.CTkLabel(app, text="", wraplength=500, justify="left", font=ctk.CTkFont(size=14))
# result_label.pack(pady=15, padx=20)

# # Loader animation
# loading_label = ctk.CTkLabel(app, text="", font=ctk.CTkFont(size=12, weight="normal"))
# loading_label.pack()

# # Loader animation thread
# def loading_animation():
#     dots = ["", ".", "..", "..."]
#     i = 0
#     while loading:
#         loading_label.configure(text="🔄 Thinking" + dots[i % 4])
#         i += 1
#         time.sleep(0.4)
#     loading_label.configure(text="")

# # Gemini query function
# def query_gemini(prompt_text):
#     try:
#         response = model.generate_content(prompt_text)
#         return response.text
#     except Exception as e:
#         return f"❌ Error: {str(e)}"

# # Main prediction handler
# def predict_crop():
#     global loading
#     try:
#         temp = float(temp_entry.get())
#         hum = float(hum_entry.get())
#         moist = float(moist_entry.get())

#         loading = True
#         Thread(target=loading_animation).start()

#         prompt = (
#             f"Based on the following environmental conditions, suggest the most suitable crop for a farmer to grow "
#             f"and provide a short explanation in Hindi:\n\n"
#             f"Temperature: {temp} °C\nHumidity: {hum} %\nSoil Moisture: {moist} %\n\n"
#             f"Output Format:\n"
#             f"Crop: <Crop Name>\nReason: <Explanation in Hindi>"
#         )

#         def run_query():
#             result = query_gemini(prompt)
#             result_label.configure(text=result, text_color="lightgreen")
#             global loading
#             loading = False

#         Thread(target=run_query).start()

#     except ValueError:
#         messagebox.showerror("Input Error", "Please enter valid numbers.\nकृपया सही मान दर्ज करें।")

# # Button
# predict_btn = ctk.CTkButton(app, text="🌐 Predict with Gemini AI", width=300, height=45, command=predict_crop)
# predict_btn.pack(pady=20)

# # Start the app
# app.mainloop()

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
app.geometry("600x570")
app.title("🌱 AI Crop Advisor (Live from Arduino)")

title_label = ctk.CTkLabel(app, text="🌿 Smart Farming Advisor", font=ctk.CTkFont(size=24, weight="bold"))
title_label.pack(pady=15)

data_display = ctk.CTkLabel(app, text="Waiting for sensor data...", font=ctk.CTkFont(size=14))
data_display.pack(pady=10)

result_label = ctk.CTkLabel(app, text="", wraplength=550, justify="left", font=ctk.CTkFont(size=14))
result_label.pack(pady=20)

loading_label = ctk.CTkLabel(app, text="", font=ctk.CTkFont(size=12))
loading_label.pack()

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

# -- Gemini prompt --
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

# -- Read Arduino and Predict --
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

                time.sleep(10)  # Delay next prediction

    except Exception as e:
        data_display.configure(text=f"❌ Serial Error: {e}")

# -- Start Reading Serial in Background --
Thread(target=read_serial_and_predict, daemon=True).start()

# -- Run App --
app.mainloop()
