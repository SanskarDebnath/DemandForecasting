import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import json
import os
import webbrowser
from datetime import datetime


def dms_to_decimal(dms_str, ref):
    try:
        parts = str(dms_str).replace("deg", "").replace('"', "").replace("'", "").split()
        degrees = float(parts[0])
        minutes = float(parts[1])
        seconds = float(parts[2])
        decimal = degrees + minutes / 60 + seconds / 3600
        if ref in ['S', 'W']:
            decimal *= -1
        return round(decimal, 6)
    except Exception as e:
        print(f"Conversion error: {e}")
        return None



current_metadata = None
current_image_path = None

# Modern color scheme
BG_COLOR = "#f5f7fa"
HEADER_COLOR = "#ffffff"
BUTTON_COLOR = "#007aff"
BUTTON_HOVER = "#0062cc"
TEXT_COLOR = "#333333"
SECONDARY_COLOR = "#8e8e93"
ACCENT_COLOR = "#ff2d55"
FRAME_COLOR = "#ffffff"
DARK_TEXT = "#1d1d1f"
LIGHT_TEXT = "#86868b"

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
    global text_area, btn_map
    
    text_area.config(state=tk.NORMAL)
    text_area.delete(1.0, tk.END)
    btn_map.config(state=tk.DISABLED)

    # Configure text tags
    text_area.tag_configure("header", font=("Helvetica", 14, "bold"), foreground=DARK_TEXT)
    text_area.tag_configure("subheader", font=("Helvetica", 12, "bold"), foreground=DARK_TEXT)
    text_area.tag_configure("regular", font=("Helvetica", 12), foreground=TEXT_COLOR)
    text_area.tag_configure("metadata", font=("Courier", 11), foreground=DARK_TEXT)
    text_area.tag_configure("success", font=("Helvetica", 12), foreground="#34C759")
    text_area.tag_configure("warning", font=("Helvetica", 12), foreground=ACCENT_COLOR)
    text_area.tag_configure("info", font=("Helvetica", 12), foreground=SECONDARY_COLOR)
    
    file_name = os.path.basename(path)
    text_area.insert(tk.END, f"📁 File: {file_name}\n", "header")
    text_area.insert(tk.END, f"📂 Path: {os.path.abspath(path)}\n\n", "info")
    
    if "error" in metadata:
        text_area.insert(tk.END, f"❌ Error: {metadata['error']}\n", "warning")
        text_area.config(state=tk.DISABLED)
        return

    # Metadata badges
    text_area.insert(tk.END, "🔍 Metadata Overview:\n", "subheader")
    
    # Create a frame for badges
    badges_frame = tk.Frame(text_area, bg=FRAME_COLOR)
    text_area.window_create(tk.END, window=badges_frame)
    text_area.insert(tk.END, "\n")
    
    # Badge data - simplified without transparency which was causing issues
    badge_data = [
        ("EXIF", "EXIF" in json.dumps(metadata)), 
        ("GPS", "GPSLatitude" in metadata and "GPSLongitude" in metadata),
        ("ICC", "ICCProfileName" in metadata),
        ("XMP", any("XMP" in key for key in metadata.keys()))
    ]
    
    for i, (title, present) in enumerate(badge_data):
        color = "#34C759" if present else ACCENT_COLOR
        badge = tk.Label(
            badges_frame, 
            text=f" {title} {'✅' if present else '❌'} ",
            font=("Helvetica", 10, "bold"),
            bg=FRAME_COLOR,  # Solid background instead of transparent
            fg=color,
            padx=8,
            pady=4,
            bd=1,
            relief=tk.RIDGE
        )
        badge.grid(row=0, column=i, padx=5, pady=5)
    
    text_area.insert(tk.END, "\n")
    
    # GPS Section
    gps_lat = metadata.get("GPSLatitude")
    gps_lon = metadata.get("GPSLongitude")
    gps_lat_ref = metadata.get("GPSLatitudeRef", "")
    gps_lon_ref = metadata.get("GPSLongitudeRef", "")

    lat_decimal = dms_to_decimal(gps_lat, gps_lat_ref) if gps_lat else None
    lon_decimal = dms_to_decimal(gps_lon, gps_lon_ref) if gps_lon else None

    if lat_decimal and lon_decimal:
        text_area.insert(tk.END, "📍 GPS Coordinates Found:\n", "subheader")
        text_area.insert(tk.END, f"Latitude: {lat_decimal} ({gps_lat}) {gps_lat_ref}\n", "regular")
        text_area.insert(tk.END, f"Longitude: {lon_decimal} ({gps_lon}) {gps_lon_ref}\n\n", "regular")
        btn_map.config(state=tk.NORMAL)
        btn_map.lat = lat_decimal
        btn_map.lon = lon_decimal
    else:
        text_area.insert(tk.END, "📍 GPS Data\n", "subheader")
        text_area.insert(tk.END, "📵 This image does not contain GPS data\n", "warning")
        text_area.insert(tk.END, "💡 Tip: Use a photo taken with GPS/location enabled\n\n", "info")

    
    # Full metadata display
    text_area.insert(tk.END, "📋 Full Metadata:\n", "subheader")
    metadata_display = metadata.copy()
    metadata_display["FileLocation"] = os.path.abspath(path)
    metadata_str = json.dumps(metadata_display, indent=4)
    text_area.insert(tk.END, metadata_str, "metadata")
    
    text_area.config(state=tk.DISABLED)

def choose_image_and_extract():
    global current_metadata, current_image_path
    
    path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.tiff;*.bmp;*.gif;*.dng;*.raw;*.heic")]
    )
    if not path:
        return
    
    current_image_path = path
    status_label.config(text=f"Processing: {os.path.basename(path)}")
    root.update()
    
    try:
        current_metadata = extract_metadata_exiftool(path)
        display_metadata(path, current_metadata)
        btn_delete.config(state=tk.NORMAL)
        status_label.config(text=f"Loaded: {os.path.basename(path)}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to process image: {str(e)}")
        status_label.config(text="Ready")

def save_metadata():
    global current_metadata, current_image_path
    
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
        status_label.config(text=f"Metadata saved to {filename}")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        status_label.config(text="Save failed")

def delete_output():
    global current_metadata, current_image_path
    
    current_metadata = None
    current_image_path = None
    text_area.config(state=tk.NORMAL)
    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, "🗑 Output cleared. Select an image to view metadata.", "regular")
    text_area.config(state=tk.DISABLED)
    btn_delete.config(state=tk.DISABLED)
    btn_map.config(state=tk.DISABLED)
    status_label.config(text="Ready")

def show_info():
    messagebox.showinfo(
        "About Image Metadata Extractor",
        "📸 Image Metadata Extractor\n\n"
        "Version 2.0\n"
        "Developed with Python and Tkinter\n\n"
        "Features:\n"
        "• Extract EXIF, IPTC, XMP, ICC metadata\n"
        "• GPS location detection and mapping\n"
        "• Support for RAW and HEIC formats\n"
        "• Clean Apple-inspired UI\n\n"
        "© 2023 Sanskar - All rights reserved"
    )

def on_enter(e):
    e.widget.config(bg=BUTTON_HOVER)

def on_leave(e):
    e.widget.config(bg=BUTTON_COLOR)

# Main application window
root = tk.Tk()
root.title("Image Metadata Extractor")
root.geometry("1000x750")
root.configure(bg=BG_COLOR)

# Header
header_frame = tk.Frame(root, bg=HEADER_COLOR, height=80)
header_frame.pack(fill=tk.X, pady=(0, 10))

app_icon = tk.Label(
    header_frame, 
    text="📸", 
    font=("Helvetica", 28), 
    bg=HEADER_COLOR, 
    fg=BUTTON_COLOR
)
app_icon.pack(side=tk.LEFT, padx=(20, 10), pady=10)

app_title = tk.Label(
    header_frame, 
    text="Image Metadata Extractor", 
    font=("Helvetica", 20, "bold"), 
    bg=HEADER_COLOR, 
    fg=DARK_TEXT
)
app_title.pack(side=tk.LEFT, pady=10)

# Main content
main_frame = tk.Frame(root, bg=BG_COLOR)
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

# Button container
button_frame = tk.Frame(main_frame, bg=BG_COLOR)
button_frame.pack(fill=tk.X, pady=(10, 15))

# Buttons
btn_choose = tk.Button(
    button_frame,
    text="📁  Choose Image",
    command=choose_image_and_extract,
    bg=BUTTON_COLOR,
    fg="white",
    font=("Helvetica", 12, "bold"),
    bd=0,
    padx=15,
    pady=8,
    activebackground=BUTTON_HOVER,
    activeforeground="white"
)
btn_choose.pack(side=tk.LEFT, padx=5)
btn_choose.bind("<Enter>", on_enter)
btn_choose.bind("<Leave>", on_leave)

btn_save = tk.Button(
    button_frame,
    text="💾  Save Metadata",
    command=save_metadata,
    bg=SECONDARY_COLOR,
    fg="white",
    font=("Helvetica", 12, "bold"),
    bd=0,
    padx=15,
    pady=8,
    activebackground="#5a5a5f",
    activeforeground="white"
)
btn_save.pack(side=tk.LEFT, padx=5)
btn_save.bind("<Enter>", lambda e: btn_save.config(bg="#5a5a5f"))
btn_save.bind("<Leave>", lambda e: btn_save.config(bg=SECONDARY_COLOR))

btn_map = tk.Button(
    button_frame,
    text="🌍  View in Google Maps",
    state=tk.DISABLED,
    command=lambda: open_map(btn_map.lat, btn_map.lon) if btn_map.cget('state') == tk.NORMAL else None,
    bg=ACCENT_COLOR,
    fg="white",
    font=("Helvetica", 12, "bold"),
    bd=0,
    padx=15,
    pady=8,
    activebackground="#d40f3d",
    activeforeground="white"
)
btn_map.lat = None
btn_map.lon = None
btn_map.pack(side=tk.LEFT, padx=5)
btn_map.bind("<Enter>", lambda e: btn_map.config(bg="#d40f3d") if btn_map.cget('state') == tk.NORMAL else None)
btn_map.bind("<Leave>", lambda e: btn_map.config(bg=ACCENT_COLOR) if btn_map.cget('state') == tk.NORMAL else None)

btn_delete = tk.Button(
    button_frame,
    text="🗑️  Clear Output",
    command=delete_output,
    state=tk.DISABLED,
    bg=SECONDARY_COLOR,
    fg="white",
    font=("Helvetica", 12, "bold"),
    bd=0,
    padx=15,
    pady=8,
    activebackground="#5a5a5f",
    activeforeground="white"
)
btn_delete.pack(side=tk.RIGHT, padx=5)
btn_delete.bind("<Enter>", lambda e: btn_delete.config(bg="#5a5a5f") if btn_delete.cget('state') == tk.NORMAL else None)
btn_delete.bind("<Leave>", lambda e: btn_delete.config(bg=SECONDARY_COLOR) if btn_delete.cget('state') == tk.NORMAL else None)

# Text area with scrollbar
text_frame = tk.Frame(main_frame, bg=FRAME_COLOR, bd=0, relief=tk.FLAT)
text_frame.pack(fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(text_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_area = tk.Text(
    text_frame, 
    bg=FRAME_COLOR, 
    fg=TEXT_COLOR, 
    font=("Helvetica", 12),
    yscrollcommand=scrollbar.set,
    padx=15,
    pady=15,
    bd=0,
    highlightthickness=0
)
text_area.pack(fill=tk.BOTH, expand=True)

scrollbar.config(command=text_area.yview)

# Initial message
text_area.config(state=tk.NORMAL)
text_area.insert(tk.END, "📸 Welcome to Image Metadata Extractor\n\n", "header")
text_area.insert(tk.END, "To get started, click 'Choose Image' to select an image file.\n\n", "regular")
text_area.insert(tk.END, "Supported formats: JPG, PNG, TIFF, BMP, GIF, DNG, RAW, HEIC\n", "info")
text_area.config(state=tk.DISABLED)

# Status bar
status_frame = tk.Frame(root, bg="#e0e0e0", height=24)
status_frame.pack(fill=tk.X, side=tk.BOTTOM)

status_label = tk.Label(
    status_frame, 
    text="Ready", 
    bg="#e0e0e0", 
    fg=SECONDARY_COLOR,
    font=("Helvetica", 10),
    anchor=tk.W,
    padx=10
)
status_label.pack(fill=tk.X, side=tk.LEFT)

# Menu
menubar = tk.Menu(root, bg=HEADER_COLOR, fg=DARK_TEXT, bd=0)

file_menu = tk.Menu(menubar, tearoff=0, bg=HEADER_COLOR, fg=DARK_TEXT)
file_menu.add_command(label="Open Image", command=choose_image_and_extract)
file_menu.add_command(label="Save Metadata", command=save_metadata)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=file_menu)

edit_menu = tk.Menu(menubar, tearoff=0, bg=HEADER_COLOR, fg=DARK_TEXT)
edit_menu.add_command(label="Clear Output", command=delete_output)
menubar.add_cascade(label="Edit", menu=edit_menu)

help_menu = tk.Menu(menubar, tearoff=0, bg=HEADER_COLOR, fg=DARK_TEXT)
help_menu.add_command(label="About", command=show_info)
menubar.add_cascade(label="Help", menu=help_menu)

root.config(menu=menubar)

# Run the application
root.mainloop()