import customtkinter as ctk
import pandas as pd
import joblib
import pyttsx3
import serial
import re
import time
from tkinter import messagebox
from threading import Thread

# ========== CONFIGURATION ==========
SERIAL_PORT = "COM3"     # Change as per your system
BAUD_RATE = 9600
USE_HINDI_VOICE = True    # Auto speak result in Hindi
# ===================================

# UI settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# Load model and data
model = joblib.load("crop_model.pkl")
df = pd.read_csv("synthetic_crop_dataset_with_info.csv")

eng_descriptions = df.drop_duplicates("label").set_index("label")["description"].to_dict()
hindi_descriptions = {
    "Rice": "चावल को गर्म और आर्द्र जलवायु की आवश्यकता होती है। पानी की मात्रा अधिक चाहिए।",
    "Wheat": "गेहूं ठंडे और शुष्क मौसम में अच्छा उगता है।",
    "Maize": "मक्का को गर्म जलवायु और मध्यम नमी की जरूरत होती है।",
    "Sugarcane": "गन्ना उष्णकटिबंधीय क्षेत्रों में उच्च नमी के साथ अच्छा होता है।",
    "Cotton": "कपास सूखे और गर्म क्षेत्रों में बेहतर उगता है।",
    "Barley": "जौ ठंडी और शुष्क जलवायु में अच्छा होता है।",
    "Millets": "बाजरा सूखा-सहिष्णु है और कम पानी में भी उगता है।",
    "Groundnut": "मूंगफली को गर्म और नम जलवायु की जरूरत होती है।",
    "Soybean": "सोयाबीन को गर्म और आर्द्र वातावरण पसंद होता है।",
    "Lentil": "मसूर ठंडे और शुष्क क्षेत्रों के लिए उपयुक्त है।"
}

# Text-to-Speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 145)

# Speak function
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Crop prediction function
def predict_crop(temp, hum, moist):
    try:
        prediction = model.predict([[temp, hum, moist]])[0]

        desc_en = eng_descriptions.get(prediction, "No description available.")
        desc_hi = hindi_descriptions.get(prediction, "हिंदी जानकारी उपलब्ध नहीं है।")

        result_text = f"🌾 Recommended Crop: {prediction}\n\n📘 Description:\n{desc_en}\n\n🪔 हिंदी:\n{desc_hi}"
        result_label.configure(text_color="lightgreen")
        result_label.configure(text=result_text)

        if USE_HINDI_VOICE:
            Thread(target=lambda: speak(desc_hi)).start()

    except Exception as e:
        result_label.configure(text=f"❌ Error in prediction: {e}")

# Serial reader thread
def read_from_arduino():
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

                temp_entry.delete(0, "end")
                hum_entry.delete(0, "end")
                moist_entry.delete(0, "end")

                temp_entry.insert(0, str(temp))
                hum_entry.insert(0, str(hum))
                moist_entry.insert(0, str(moist))

                predict_crop(temp, hum, moist)
                time.sleep(10)  # Wait before next prediction
    except Exception as e:
        result_label.configure(text=f"❌ Serial Error: {e}")

# GUI Setup
app = ctk.CTk()
app.geometry("600x580")
app.title("🌾 AI Crop Recommendation System (Auto from Arduino)")
app.resizable(False, False)

title_label = ctk.CTkLabel(app, text="🌿 Smart Farming Assistant", font=ctk.CTkFont(size=24, weight="bold"))
title_label.pack(pady=15)

input_frame = ctk.CTkFrame(app, corner_radius=12)
input_frame.pack(pady=10, padx=20, fill="x")

temp_entry = ctk.CTkEntry(input_frame, placeholder_text="🌡 Temperature (°C)", height=40)
temp_entry.pack(pady=10, padx=20, fill="x")

hum_entry = ctk.CTkEntry(input_frame, placeholder_text="💧 Humidity (%)", height=40)
hum_entry.pack(pady=10, padx=20, fill="x")

moist_entry = ctk.CTkEntry(input_frame, placeholder_text="🌱 Soil Moisture (%)", height=40)
moist_entry.pack(pady=10, padx=20, fill="x")

# Result Label
result_label = ctk.CTkLabel(app, text="Waiting for Arduino data...", wraplength=550, justify="left", font=ctk.CTkFont(size=14))
result_label.pack(pady=20, padx=20)

# Start Arduino thread
Thread(target=read_from_arduino, daemon=True).start()

# Run app
app.mainloop()
