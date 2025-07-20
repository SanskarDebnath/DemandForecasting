import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import subprocess
import json
import os
import webbrowser
from datetime import datetime

BG_COLOR = "#0a0a0a"
FG_COLOR = "#00ff00"
ACCENT_COLOR = "#ff5555"
TEXT_BG = "#121212"
BUTTON_BG = "#1a3d1a"
BUTTON_ACTIVE = "#2a5d2a"
ENTRY_BG = "#1e1e1e"
HEADER_COLOR = "#003300"

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
        messagebox.showerror("MAP ERROR", f"COULD NOT OPEN MAP: {e}", parent=root)

def display_metadata(path, metadata):
    global text_area, btn_map    
    text_area.config(state=tk.NORMAL)
    text_area.delete(1.0, tk.END)
    btn_map.config(state=tk.DISABLED)
    text_area.tag_configure("header", font=("Consolas", 14, "bold"), foreground=FG_COLOR)
    text_area.tag_configure("subheader", font=("Consolas", 12, "bold"), foreground=FG_COLOR)
    text_area.tag_configure("regular", font=("Consolas", 11), foreground=FG_COLOR)
    text_area.tag_configure("metadata", font=("Consolas", 10), foreground=FG_COLOR)
    text_area.tag_configure("success", font=("Consolas", 11), foreground="#00ff00")
    text_area.tag_configure("warning", font=("Consolas", 11), foreground=ACCENT_COLOR)
    text_area.tag_configure("info", font=("Consolas", 11), foreground="#00cc00")
    
    file_name = os.path.basename(path)
    text_area.insert(tk.END, f"📁 FILE: {file_name}\n", "header")
    text_area.insert(tk.END, f"📂 PATH: {os.path.abspath(path)}\n\n", "info")
    
    if "error" in metadata:
        text_area.insert(tk.END, f"❌ ERROR: {metadata['error']}\n", "warning")
        text_area.config(state=tk.DISABLED)
        return

    text_area.insert(tk.END, "🔍 METADATA OVERVIEW:\n", "subheader")
    
    badges_frame = tk.Frame(text_area, bg=TEXT_BG)
    text_area.window_create(tk.END, window=badges_frame)
    text_area.insert(tk.END, "\n")

    badge_data = [
        ("EXIF", "EXIF" in json.dumps(metadata)), 
        ("GPS", "GPSLatitude" in metadata and "GPSLongitude" in metadata),
        ("ICC", "ICCProfileName" in metadata),
        ("XMP", any("XMP" in key for key in metadata.keys()))
    ]
    
    for i, (title, present) in enumerate(badge_data):
        color = "#00ff00" if present else ACCENT_COLOR
        badge = tk.Label(
            badges_frame, 
            text=f" {title} {'✅' if present else '❌'} ",
            font=("Consolas", 10, "bold"),
            bg=TEXT_BG,
            fg=color,
            padx=8,
            pady=4,
            bd=1,
            relief=tk.RIDGE
        )
        badge.grid(row=0, column=i, padx=5, pady=5)
    
    text_area.insert(tk.END, "\n")
    
    gps_lat = metadata.get("GPSLatitude")
    gps_lon = metadata.get("GPSLongitude")
    gps_lat_ref = metadata.get("GPSLatitudeRef", "")
    gps_lon_ref = metadata.get("GPSLongitudeRef", "")

    lat_decimal = dms_to_decimal(gps_lat, gps_lat_ref) if gps_lat else None
    lon_decimal = dms_to_decimal(gps_lon, gps_lon_ref) if gps_lon else None

    if lat_decimal and lon_decimal:
        text_area.insert(tk.END, "📍 GPS COORDINATES FOUND:\n", "subheader")
        text_area.insert(tk.END, f"LATITUDE: {lat_decimal} ({gps_lat}) {gps_lat_ref}\n", "regular")
        text_area.insert(tk.END, f"LONGITUDE: {lon_decimal} ({gps_lon}) {gps_lon_ref}\n\n", "regular")
        btn_map.config(state=tk.NORMAL)
        btn_map.lat = lat_decimal
        btn_map.lon = lon_decimal
    else:
        text_area.insert(tk.END, "📍 GPS DATA\n", "subheader")
        text_area.insert(tk.END, "📵 NO GPS DATA FOUND\n", "warning")
        text_area.insert(tk.END, "💡 TIP: USE GPS-ENABLED PHOTOS\n\n", "info")

    text_area.insert(tk.END, "📋 FULL METADATA:\n", "subheader")
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
    status_label.config(text=f"PROCESSING: {os.path.basename(path)}")
    root.update()
    try:
        current_metadata = extract_metadata_exiftool(path)
        display_metadata(path, current_metadata)
        btn_delete.config(state=tk.NORMAL)
        btn_embed.config(state=tk.NORMAL)
        status_label.config(text=f"LOADED: {os.path.basename(path)}")
    except Exception as e:
        messagebox.showerror("SYSTEM ERROR", f"PROCESSING FAILED: {str(e)}", parent=root)
        status_label.config(text="STATUS: READY")

def save_metadata():
    global current_metadata, current_image_path
    if not current_metadata or not current_image_path:
        messagebox.showwarning("WARNING", "NO METADATA TO SAVE", parent=root)
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
        messagebox.showinfo("SUCCESS", f"METADATA SAVED AS:\n{filename}", parent=root)
        status_label.config(text=f"STATUS: SAVED TO {filename}")
    except Exception as e:
        messagebox.showerror("ERROR", str(e).upper(), parent=root)
        status_label.config(text="STATUS: SAVE FAILED")

def delete_output():
    global current_metadata, current_image_path
    current_metadata = None
    current_image_path = None
    text_area.config(state=tk.NORMAL)
    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, "🗑 OUTPUT CLEARED. SELECT IMAGE TO CONTINUE.", "regular")
    text_area.config(state=tk.DISABLED)
    btn_delete.config(state=tk.DISABLED)
    btn_map.config(state=tk.DISABLED)
    btn_embed.config(state=tk.DISABLED)
    status_label.config(text="STATUS: READY")

def show_info():
    messagebox.showinfo(
        "SYSTEM INFO",
        "📸 IMAGE METADATA EXTRACTOR\n\n"
        "VERSION: 2.0 [CLASSIFIED]\n"
        "SYSTEM: PYTHON/TKINTER\n\n"
        "CAPABILITIES:\n"
        "• EXIF/IPTC/XMP/ICC METADATA EXTRACTION\n"
        "• GPS GEOLOCATION MAPPING\n"
        "• RAW/HEIC FORMAT SUPPORT\n"
        "• SECURE METADATA EMBEDDING\n\n"
        "-----DEVELOPED BY SANSKAR DEBNATH-----",
        "-----VERSION 1-----",
        parent=root
    )

def insert_custom_metadata():
    if not current_image_path:
        messagebox.showwarning("WARNING", "NO IMAGE SELECTED", parent=root)
        return
    custom_message = simpledialog.askstring("SECURE MESSAGE ENTRY", "ENTER MESSAGE TO EMBED:", parent=root)
    if not custom_message:
        return
    try:
        result = subprocess.run(
            ["exiftool", f"-Comment={custom_message}", "-overwrite_original", current_image_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            messagebox.showinfo("SUCCESS", "METADATA EMBEDDED SECURELY", parent=root)
            current_metadata = extract_metadata_exiftool(current_image_path)
            display_metadata(current_image_path, current_metadata)
        else:
            raise Exception(result.stderr)
    except Exception as e:
        messagebox.showerror("CRYPTO FAILURE", f"EMBED FAILED: {e}", parent=root)

def on_enter(e):
    e.widget.config(bg=BUTTON_ACTIVE)
def on_leave(e):
    e.widget.config(bg=BUTTON_BG)

root = tk.Tk()
root.title("CLASSIFIED // IMAGE METADATA ANALYZER // TOP SECRET")
root.geometry("1000x750")
root.configure(bg=BG_COLOR)

header_frame = tk.Frame(root, bg=HEADER_COLOR, height=80)
header_frame.pack(fill=tk.X, pady=(0, 5))

app_icon = tk.Label(
    header_frame, 
    text="🔍", 
    font=("Consolas", 28), 
    bg=HEADER_COLOR, 
    fg=FG_COLOR
)
app_icon.pack(side=tk.LEFT, padx=(20, 10), pady=10)

app_title = tk.Label(
    header_frame, 
    text="SANSKAR'S IMG ANALYZER", 
    font=("Consolas", 18, "bold"), 
    bg=HEADER_COLOR, 
    fg=FG_COLOR
)
app_title.pack(side=tk.LEFT, pady=10)

main_frame = tk.Frame(root, bg=BG_COLOR)
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
button_frame = tk.Frame(main_frame, bg=BG_COLOR)
button_frame.pack(fill=tk.X, pady=(10, 15))

btn_style = {
    "font": ("Consolas", 10, "bold"),
    "bg": BUTTON_BG,
    "fg": "white",
    "activebackground": BUTTON_ACTIVE,
    "activeforeground": "white",
    "borderwidth": 3,
    "relief": tk.RAISED
}
btn_choose = tk.Button(
    button_frame,
    text="📁 SELECT IMAGE",
    command=choose_image_and_extract,
    **btn_style
)
btn_choose.pack(side=tk.LEFT, padx=5)
btn_choose.bind("<Enter>", on_enter)
btn_choose.bind("<Leave>", on_leave)
btn_save = tk.Button(
    button_frame,
    text="💾 SAVE METADATA",
    command=save_metadata,
    **btn_style
)
btn_save.pack(side=tk.LEFT, padx=5)
btn_save.bind("<Enter>", on_enter)
btn_save.bind("<Leave>", on_leave)
btn_map = tk.Button(
    button_frame,
    text="🌍 VIEW IN MAPS",
    state=tk.DISABLED,
    command=lambda: open_map(btn_map.lat, btn_map.lon) if btn_map.cget('state') == tk.NORMAL else None,
    **btn_style
)
btn_map.lat = None
btn_map.lon = None
btn_map.pack(side=tk.LEFT, padx=5)
btn_map.bind("<Enter>", on_enter)
btn_map.bind("<Leave>", on_leave)
btn_embed = tk.Button(
    button_frame,
    text="📝 EMBED MESSAGE",
    command=insert_custom_metadata,
    state=tk.DISABLED,
    **btn_style
)
btn_embed.pack(side=tk.LEFT, padx=5)
btn_embed.bind("<Enter>", on_enter)
btn_embed.bind("<Leave>", on_leave)
btn_delete = tk.Button(
    button_frame,
    text="🗑️ CLEAR OUTPUT",
    command=delete_output,
    state=tk.DISABLED,
    **btn_style
)
btn_delete.pack(side=tk.RIGHT, padx=5)
btn_delete.bind("<Enter>", on_enter)
btn_delete.bind("<Leave>", on_leave)
text_frame = tk.Frame(main_frame, bg=TEXT_BG, bd=2, relief=tk.SUNKEN)
text_frame.pack(fill=tk.BOTH, expand=True)
scrollbar = tk.Scrollbar(text_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_area = tk.Text(
    text_frame, 
    bg=TEXT_BG, 
    fg=FG_COLOR, 
    font=("Consolas", 10),
    yscrollcommand=scrollbar.set,
    padx=15,
    pady=15,
    bd=0,
    highlightthickness=0,
    insertbackground=FG_COLOR
)
text_area.pack(fill=tk.BOTH, expand=True)
scrollbar.config(command=text_area.yview)
text_area.config(state=tk.NORMAL)
text_area.insert(tk.END, "🔍 IMAGE METADATA ANALYZER [ONLINE]\n\n", "header")
text_area.insert(tk.END, "SELECT AN IMAGE FILE TO BEGIN ANALYSIS\n\n", "regular")
text_area.insert(tk.END, "SUPPORTED FORMATS: JPG, PNG, TIFF, BMP, GIF, DNG, RAW, HEIC\n", "info")
text_area.config(state=tk.DISABLED)
status_frame = tk.Frame(root, bg=HEADER_COLOR, height=24)
status_frame.pack(fill=tk.X, side=tk.BOTTOM)
status_label = tk.Label(
    status_frame, 
    text="STATUS: READY", 
    bg=HEADER_COLOR, 
    fg=FG_COLOR,
    font=("Consolas", 9),
    anchor=tk.W,
    padx=10
)
status_label.pack(fill=tk.X, side=tk.LEFT)
menubar = tk.Menu(root, bg=HEADER_COLOR, fg=FG_COLOR, bd=0, font=("Consolas", 9))
file_menu = tk.Menu(menubar, tearoff=0, bg=TEXT_BG, fg=FG_COLOR)
file_menu.add_command(label="OPEN IMAGE", command=choose_image_and_extract)
file_menu.add_command(label="SAVE METADATA", command=save_metadata)
file_menu.add_separator()
file_menu.add_command(label="EXIT", command=root.quit)
menubar.add_cascade(label="FILE", menu=file_menu)
edit_menu = tk.Menu(menubar, tearoff=0, bg=TEXT_BG, fg=FG_COLOR)
edit_menu.add_command(label="CLEAR OUTPUT", command=delete_output)
menubar.add_cascade(label="EDIT", menu=edit_menu)
help_menu = tk.Menu(menubar, tearoff=0, bg=TEXT_BG, fg=FG_COLOR)
help_menu.add_command(label="SYSTEM INFO", command=show_info)
menubar.add_cascade(label="HELP", menu=help_menu)
root.config(menu=menubar)
root.mainloop()