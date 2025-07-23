import requests
import tkinter as tk
from tkinter import font, ttk
from urllib.request import urlopen
from base64 import b64encode
from datetime import datetime
import os
from dotenv import load_dotenv

# Load .env for API key
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Ensure search history file exists
def ensure_history_file():
    if not os.path.exists("history.text"):
        with open("history.text", "w"): pass

# Save city to search history
def save_to_history(city):
    # Load the current history
    history = load_history()

    # Remove duplicates and add the new city to the top
    if city in history:
        history.remove(city)
    history.insert(0, city)

    # Save the updated history back to the file
    with open("history.text", "w") as file:
        for item in history:
            file.write(item + "\n")

# Load search history
def load_history():
    if os.path.exists("history.text"):
        with open("history.text", "r") as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    return []

# Update dropdown menu with latest history
def update_dropdown():
    history = load_history()
    dropdown["menu"].delete(0, "end")
    for city in history:
        dropdown["menu"].add_command(label=city, command=lambda value=city: set_city(value))
    if history:
        history_var.set(history[0])

# Set selected city from dropdown
def set_city(city):
    city_entry.delete(0, tk.END)
    city_entry.insert(0, city)
    show_weather()

# Fetch weather from API
def get_weather_data(city):
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Display weather data
def show_weather():
    city = city_entry.get().strip()
    if not city:
        return

    data = get_weather_data(city)
    if not data:
        weather_label.config(text="City not found.")
        return

    save_to_history(city)
    update_dropdown()

    location = f"{data['location']['name']}, {data['location']['country']}"
    time = datetime.strptime(data['location']['localtime'], '%Y-%m-%d %H:%M').strftime('%b %d, %Y %I:%M %p')
    temp_c = data['current']['temp_c']
    condition = data['current']['condition']['text'].lower()
    humidity = data['current']['humidity']
    wind = data['current']['wind_kph']
    rain = data['current'].get('precip_mm', 0)
    rain_chance = data['current'].get('precip_in', 0) * 10  # Example: Convert inches to percentage
    is_day = data['current']['is_day']
    icon_url = "http:" + data['current']['condition']['icon']

    # Theme based on condition and time of day
    if "clear" in condition or "sunny" in condition:
        bg_color = "#FFE066" if is_day else "#2C3E50"
        text_color = "#333333" if is_day else "#ffffff"
        accent_color = "#FFB703"
    elif "cloud" in condition:
        bg_color = "#B0BEC5"
        text_color = "#212121"
        accent_color = "#78909C"
    elif "rain" in condition:
        bg_color = "#607D8B"
        text_color = "#ffffff"
        accent_color = "#4FC3F7"
    elif "thunder" in condition:
        bg_color = "#455A64"
        text_color = "#FFEB3B"
        accent_color = "#FF5722"
    elif "snow" in condition:
        bg_color = "#E0F7FA"
        text_color = "#006064"
        accent_color = "#80DEEA"
    elif "fog" in condition or "mist" in condition:
        bg_color = "#ECEFF1"
        text_color = "#455A64"
        accent_color = "#CFD8DC"
    else:
        bg_color = "#87CEEB"  # Default Sky Blue
        text_color = "#333333"
        accent_color = "#007ACC"

    # Apply the background color to the app
    root.configure(bg=bg_color)
    title_label.configure(bg=bg_color, fg=text_color)
    weather_frame.configure(bg=bg_color)
    weather_icon_label.configure(bg=bg_color)
    weather_label.configure(bg=bg_color, fg=text_color)

    # Clear previous weather details
    for widget in weather_frame.winfo_children():
        widget.destroy()

    # Weather details as key-value pairs
    weather_details = [
        ("Location", location),
        ("Time", time),
        ("Temperature", f"{temp_c}°C"),
        ("Condition", condition.capitalize()),
        ("Humidity", f"{humidity}%"),
        ("Wind", f"{wind} km/h"),
        ("Rainfall", f"{rain} mm" if rain > 0 else "No rainfall"),
        ("Chance of Rain", f"{rain_chance}%" if rain_chance > 0 else "No chance of rain")
    ]

    # Create table in the weather_frame
    for i, (key, value) in enumerate(weather_details):
        tk.Label(weather_frame, text=key, font=text_font, bg=bg_color, fg=text_color, anchor="w").grid(row=i, column=0, padx=10, pady=5, sticky="w")
        tk.Label(weather_frame, text=value, font=text_font, bg=bg_color, fg=text_color, anchor="w").grid(row=i, column=1, padx=10, pady=5, sticky="w")

    # Weather icon
    try:
        img_data = urlopen(icon_url).read()
        img_b64 = b64encode(img_data)
        icon = tk.PhotoImage(data=img_b64)
        weather_icon_label.config(image=icon)
        weather_icon_label.image = icon
    except:
        weather_icon_label.config(image="", text="Icon not available")


# --------------------------- GUI SETUP ---------------------------

root = tk.Tk()
root.title("🌤️ Weather App")
root.geometry("600x600")
root.resizable(False, False)
root.configure(bg="#87CEEB")
ensure_history_file()

# Fonts
title_font = font.Font(family="Helvetica", size=18, weight="bold")  # Reduced size
text_font = font.Font(family="Helvetica", size=10)  # Reduced size

# Bind the Enter key to the search functionality
root.bind('<Return>', lambda event: show_weather())

# Create a custom style for rounded widgets
style = ttk.Style()
style.theme_use("default")  # Use the default theme to allow customization

# Rounded style for Entry (Search Bar)
style.configure(
    "Rounded.TEntry",
    fieldbackground="#ffffff",
    borderwidth=1,
    relief="solid",
    padding=5,  # Reduced padding
    highlightthickness=0
)

# Rounded style for Button (Search Button)
style.configure(
    "Rounded.TButton",
    borderwidth=1,
    relief="solid",
    padding=5,  # Reduced padding
    background="#007ACC",
    foreground="#ffffff",
    font=("Helvetica", 10)  # Reduced font size
)

# Rounded style for OptionMenu (History Dropdown)
style.configure(
    "Rounded.TMenubutton",
    borderwidth=1,
    relief="solid",
    padding=5,  # Reduced padding
    background="#ffffff",
    font=("Helvetica", 10)  # Reduced font size
)

# Title
title_label = tk.Label(root, text="Weather Forecast", font=title_font, bg="#87CEEB", fg="white")
title_label.pack(pady=10)  # Reduced padding

# Create a frame for the search bar, search button, and dropdown
button_frame = tk.Frame(root, bg="#87CEEB")
button_frame.pack(pady=10)  # Add some spacing around the button section

# Search bar
city_entry = ttk.Entry(button_frame, font=text_font, width=25, justify="center", style="Rounded.TEntry")
city_entry.grid(row=0, column=0, padx=5, pady=5)  # Add padding between widgets
city_entry.insert(0, "enter city name")  # Placeholder text

# Search button
search_button = ttk.Button(button_frame, text="🔍 Search", command=show_weather, style="Rounded.TButton")
search_button.grid(row=0, column=1, padx=5, pady=5)  # Add padding between widgets

# Dropdown for history
history_var = tk.StringVar()
dropdown = ttk.OptionMenu(button_frame, history_var, "Select from history")
dropdown.grid(row=0, column=2, padx=5, pady=5)  # Add padding between widgets

# Icon
weather_icon_label = tk.Label(root, bg="#87CEEB")
weather_icon_label.pack(pady=10)

# Weather output
weather_label = tk.Label(root, font=text_font, bg="#87CEEB", fg="white", justify="center")
weather_label.pack(pady=5)  # Reduced padding

# Detailed weather frame (optional)
weather_frame = tk.Frame(root, bg="#87CEEB")
weather_frame.pack(pady=5)  # Reduced padding

# Run app
root.mainloop()
