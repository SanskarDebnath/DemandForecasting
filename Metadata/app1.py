import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import json
import os
import webbrowser
from datetime import datetime

current_metadata = None
current_image_path = None

def extract_metadata_exiftool(path):
    try:
        result = subprocess.run(
            ['exiftool', '-j', path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0 or not result.stdout.strip():
            return {"error": f"ExifTool failed: {result.stderr.strip() or 'Unsupported or corrupt image format.'}"}
        metadata = json.loads(result.stdout)[0]
        return metadata
    except Exception as e:
        return {"error": str(e)}

def open_map(lat, lon):
    try:
        url = f"https://www.google.com/maps?q={lat},{lon}"
        webbrowser.open(url)
    except Exception as e:
        messagebox.showerror("Map Error", f"Could not open map: {e}")

def display_metadata(path, metadata):
    text_area.config(state=tk.NORMAL)
    text_area.delete(1.0, tk.END)
    btn_map.config(state=tk.DISABLED)

    text_area.insert(tk.END, f"🔍 Extracting metadata from: {path}\n\n")

    if "error" in metadata:
        text_area.insert(tk.END, f"❌ Error: {metadata['error']}\n")
        text_area.config(state=tk.DISABLED)
        return

    metadata_display = metadata.copy()
    metadata_display["FileLocation"] = os.path.abspath(path)

    # Badges
    badges = []
    if any(key.startswith("EXIF") or "Make" in key or "Model" in key for key in metadata.keys()):
        badges.append("EXIF ✅")
    else:
        badges.append("EXIF ❌")

    if "GPSLatitude" in metadata and "GPSLongitude" in metadata:
        badges.append("GPS ✅")
    else:
        badges.append("GPS ❌")

    if "ICCProfileName" in metadata:
        badges.append("ICC ✅")
    else:
        badges.append("ICC ❌")

    if any("XMP" in key for key in metadata.keys()):
        badges.append("XMP ✅")
    else:
        badges.append("XMP ❌")

    text_area.insert(tk.END, "📦 Metadata Presence: " + " | ".join(badges) + "\n\n")

    # GPS
    gps_lat = metadata.get("GPSLatitude")
    gps_lon = metadata.get("GPSLongitude")
    gps_lat_ref = metadata.get("GPSLatitudeRef", "")
    gps_lon_ref = metadata.get("GPSLongitudeRef", "")

    if gps_lat and gps_lon:
        text_area.insert(tk.END, "🌍 GPS Coordinates Found:\n")
        text_area.insert(tk.END, f"Latitude: {gps_lat} {gps_lat_ref}\n")
        text_area.insert(tk.END, f"Longitude: {gps_lon} {gps_lon_ref}\n\n")
        btn_map.config(state=tk.NORMAL)
        btn_map.lat = gps_lat
        btn_map.lon = gps_lon
    else:
        text_area.insert(tk.END, "📵 This image does not contain GPS data.\n")
        text_area.insert(tk.END, "💡 Tip: Use a photo taken with GPS/location ON.\n\n")

    metadata_str = json.dumps(metadata_display, indent=4)
    text_area.insert(tk.END, metadata_str)
    text_area.config(state=tk.DISABLED)

def choose_image_and_extract():
    global current_metadata, current_image_path
    path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.tiff;*.bmp;*.gif;*.dng;*.raw;*.heic")]
    )
    if not path:
        return
    current_image_path = path
    current_metadata = extract_metadata_exiftool(path)
    display_metadata(path, current_metadata)
    btn_delete.config(state=tk.NORMAL)

def save_metadata():
    if not current_metadata or not current_image_path:
        messagebox.showwarning("No Data", "No metadata to save.")
        return

    base_name = os.path.basename(current_image_path)
    name, _ = os.path.splitext(base_name)
    timestamp = datetime.now().strftime("%d%m%Y-%H%M%S")
    filename = f"{name}-{timestamp}.txt"
    save_path = os.path.join(os.getcwd(), filename)

    try:
        metadata_to_save = current_metadata.copy()
        metadata_to_save["FileLocation"] = os.path.abspath(current_image_path)

        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(metadata_to_save, indent=4))

        messagebox.showinfo("Saved", f"Metadata saved as:\n{filename}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def delete_output():
    global current_metadata, current_image_path
    current_metadata = None
    current_image_path = None
    text_area.config(state=tk.NORMAL)
    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, "🗑 Output deleted. Choose a new image to continue.")
    text_area.config(state=tk.DISABLED)
    btn_delete.config(state=tk.DISABLED)
    btn_map.config(state=tk.DISABLED)

def show_info():
    messagebox.showinfo(
        "About",
        "📸 Image Metadata Extractor\n\n"
        "Made with 💻 and ☕ by Sanskar.\n"
        "Uses ExifTool under the hood.\n"
        "Supports EXIF, IPTC, XMP, ICC, DNG, HEIC\n"
        "✔️ Includes metadata badges and GPS to Google Maps!"
    )

# GUI Setup
root = tk.Tk()
root.title("Image Metadata Extractor")
root.geometry("900x700")

# Menu
menubar = tk.Menu(root)
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="Save", command=save_metadata)
file_menu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=file_menu)

help_menu = tk.Menu(menubar, tearoff=0)
help_menu.add_command(label="Info", command=show_info)
menubar.add_cascade(label="Help", menu=help_menu)
root.config(menu=menubar)

# Buttons
btn_choose = tk.Button(root, text="Choose Image", command=choose_image_and_extract)
btn_choose.pack(pady=10)

btn_map = tk.Button(root, text="Open GPS in Google Maps", state=tk.DISABLED,
                    command=lambda: open_map(btn_map.lat, btn_map.lon))
btn_map.lat = None
btn_map.lon = None
btn_map.pack(pady=5)

text_area = tk.Text(root, bg="white", fg="red", font=("Courier", 10), state=tk.DISABLED)
text_area.pack(expand=True, fill=tk.BOTH)

btn_delete = tk.Button(root, text="Delete Output", command=delete_output, state=tk.DISABLED)
btn_delete.pack(pady=10)

# Launch GUI
root.mainloop()