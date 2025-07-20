import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import subprocess
import json
import os
import webbrowser
from datetime import datetime
from typing import Optional, Dict, Any

class MetadataAnalyzer:
    BG_COLOR = "#0a0a0a"
    FG_COLOR = "#00ff00"
    ACCENT_COLOR = "#ff5555"
    TEXT_BG = "#121212"
    BUTTON_BG = "#1a3d1a"
    BUTTON_ACTIVE = "#2a5d2a"
    ENTRY_BG = "#1e1e1e"
    HEADER_COLOR = "#003300"
    
    def __init__(self, master):
        self.master = master
        self.current_metadata: Optional[Dict[str, Any]] = None
        self.current_image_path: Optional[str] = None
        self.setup_ui()
        
    def setup_ui(self):
        self.master.title("IMAGE METADATA ANALYZER")
        self.master.geometry("1000x750")
        self.master.configure(bg=self.BG_COLOR)
        
        self.create_header()
        self.create_main_frame()
        self.create_status_bar()
        self.create_menu()
        
    def create_header(self):
        header_frame = tk.Frame(self.master, bg=self.HEADER_COLOR, height=80)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(
            header_frame, 
            text="🔍", 
            font=("Consolas", 28), 
            bg=self.HEADER_COLOR, 
            fg=self.FG_COLOR
        ).pack(side=tk.LEFT, padx=(20, 10), pady=10)
        
        tk.Label(
            header_frame, 
            text="METADATA ANALYZER PRO", 
            font=("Consolas", 18, "bold"), 
            bg=self.HEADER_COLOR, 
            fg=self.FG_COLOR
        ).pack(side=tk.LEFT, pady=10)
    
    def create_main_frame(self):
        main_frame = tk.Frame(self.master, bg=self.BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        self.create_button_panel(main_frame)
        self.create_text_display(main_frame)
        
    def create_button_panel(self, parent):
        button_frame = tk.Frame(parent, bg=self.BG_COLOR)
        button_frame.pack(fill=tk.X, pady=(10, 15))
        
        button_config = {
            "font": ("Consolas", 10, "bold"),
            "bg": self.BUTTON_BG,
            "fg": "white",
            "activebackground": self.BUTTON_ACTIVE,
            "activeforeground": "white",
            "borderwidth": 3,
            "relief": tk.RAISED
        }
        
        self.btn_choose = tk.Button(
            button_frame,
            text="📁 SELECT IMAGE",
            command=self.choose_image_and_extract,
            **button_config
        )
        self.btn_choose.pack(side=tk.LEFT, padx=5)
        
        self.btn_save = tk.Button(
            button_frame,
            text="💾 SAVE METADATA",
            command=self.save_metadata,
            **button_config
        )
        self.btn_save.pack(side=tk.LEFT, padx=5)
        
        self.btn_map = tk.Button(
            button_frame,
            text="🌍 VIEW IN MAPS",
            state=tk.DISABLED,
            command=self.open_map_with_coords,
            **button_config
        )
        self.btn_map.pack(side=tk.LEFT, padx=5)
        
        self.btn_embed = tk.Button(
            button_frame,
            text="📝 EMBED MESSAGE",
            command=self.insert_custom_metadata,
            state=tk.DISABLED,
            **button_config
        )
        self.btn_embed.pack(side=tk.LEFT, padx=5)
        
        self.btn_delete = tk.Button(
            button_frame,
            text="🗑️ CLEAR OUTPUT",
            command=self.clear_output,
            state=tk.DISABLED,
            **button_config
        )
        self.btn_delete.pack(side=tk.RIGHT, padx=5)
        
        for btn in [self.btn_choose, self.btn_save, self.btn_map, self.btn_embed, self.btn_delete]:
            btn.bind("<Enter>", lambda e: e.widget.config(bg=self.BUTTON_ACTIVE))
            btn.bind("<Leave>", lambda e: e.widget.config(bg=self.BUTTON_BG))
    
    def create_text_display(self, parent):
        text_frame = tk.Frame(parent, bg=self.TEXT_BG, bd=2, relief=tk.SUNKEN)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_area = tk.Text(
            text_frame, 
            bg=self.TEXT_BG, 
            fg=self.FG_COLOR, 
            font=("Consolas", 10),
            yscrollcommand=scrollbar.set,
            padx=15,
            pady=15,
            bd=0,
            highlightthickness=0,
            insertbackground=self.FG_COLOR
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_area.yview)
        
        self.initialize_text_display()
    
    def initialize_text_display(self):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        
        self.configure_text_tags()
        
        self.text_area.insert(tk.END, "🔍 IMAGE METADATA ANALYZER [READY]\n\n", "header")
        self.text_area.insert(tk.END, "SELECT AN IMAGE FILE TO BEGIN ANALYSIS\n\n", "regular")
        self.text_area.insert(tk.END, "SUPPORTED FORMATS: JPG, PNG, TIFF, BMP, GIF, DNG, RAW, HEIC\n", "info")
        self.text_area.config(state=tk.DISABLED)
    
    def configure_text_tags(self):
        self.text_area.tag_configure("header", font=("Consolas", 14, "bold"), foreground=self.FG_COLOR)
        self.text_area.tag_configure("subheader", font=("Consolas", 12, "bold"), foreground=self.FG_COLOR)
        self.text_area.tag_configure("regular", font=("Consolas", 11), foreground=self.FG_COLOR)
        self.text_area.tag_configure("metadata", font=("Consolas", 10), foreground=self.FG_COLOR)
        self.text_area.tag_configure("success", font=("Consolas", 11), foreground="#00ff00")
        self.text_area.tag_configure("warning", font=("Consolas", 11), foreground=self.ACCENT_COLOR)
        self.text_area.tag_configure("info", font=("Consolas", 11), foreground="#00cc00")
    
    def create_status_bar(self):
        status_frame = tk.Frame(self.master, bg=self.HEADER_COLOR, height=24)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(
            status_frame, 
            text="STATUS: READY", 
            bg=self.HEADER_COLOR, 
            fg=self.FG_COLOR,
            font=("Consolas", 9),
            anchor=tk.W,
            padx=10
        )
        self.status_label.pack(fill=tk.X, side=tk.LEFT)
    
    def create_menu(self):
        menubar = tk.Menu(self.master, bg=self.HEADER_COLOR, fg=self.FG_COLOR, bd=0, font=("Consolas", 9))
        
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.TEXT_BG, fg=self.FG_COLOR)
        file_menu.add_command(label="OPEN IMAGE", command=self.choose_image_and_extract)
        file_menu.add_command(label="SAVE METADATA", command=self.save_metadata)
        file_menu.add_separator()
        file_menu.add_command(label="EXIT", command=self.master.quit)
        menubar.add_cascade(label="FILE", menu=file_menu)
        
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.TEXT_BG, fg=self.FG_COLOR)
        edit_menu.add_command(label="CLEAR OUTPUT", command=self.clear_output)
        menubar.add_cascade(label="EDIT", menu=edit_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.TEXT_BG, fg=self.FG_COLOR)
        help_menu.add_command(label="SYSTEM INFO", command=self.show_info)
        menubar.add_cascade(label="HELP", menu=help_menu)
        
        self.master.config(menu=menubar)
    
    def dms_to_decimal(self, dms_str: str, ref: str) -> Optional[float]:
        try:
            parts = str(dms_str).replace("deg", "").replace('"', "").replace("'", "").split()
            degrees = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])
            decimal = degrees + minutes / 60 + seconds / 3600
            return round(decimal * (-1 if ref in ['S', 'W'] else 1), 6)
        except Exception:
            return None
    
    def extract_metadata(self, path: str) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                ['exiftool', '-j', path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode != 0 or not result.stdout.strip():
                return {"error": f"ExifTool failed: {result.stderr.strip() or 'Unsupported or corrupt image format.'}"}
            return json.loads(result.stdout)[0]
        except Exception as e:
            return {"error": str(e)}
    
    def choose_image_and_extract(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.tiff;*.bmp;*.gif;*.dng;*.raw;*.heic")]
        )
        if not path:
            return
            
        self.current_image_path = path
        self.status_label.config(text=f"PROCESSING: {os.path.basename(path)}")
        self.master.update()
        
        try:
            self.current_metadata = self.extract_metadata(path)
            self.display_metadata(path, self.current_metadata)
            self.btn_delete.config(state=tk.NORMAL)
            self.btn_embed.config(state=tk.NORMAL)
            self.status_label.config(text=f"LOADED: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("ERROR", f"PROCESSING FAILED: {str(e)}", parent=self.master)
            self.status_label.config(text="STATUS: READY")
    
    def display_metadata(self, path: str, metadata: Dict[str, Any]):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.btn_map.config(state=tk.DISABLED)
        
        file_name = os.path.basename(path)
        self.text_area.insert(tk.END, f"📁 FILE: {file_name}\n", "header")
        self.text_area.insert(tk.END, f"📂 PATH: {os.path.abspath(path)}\n\n", "info")
        
        if "error" in metadata:
            self.text_area.insert(tk.END, f"❌ ERROR: {metadata['error']}\n", "warning")
            self.text_area.config(state=tk.DISABLED)
            return

        self.text_area.insert(tk.END, "🔍 METADATA OVERVIEW:\n", "subheader")
        self.create_metadata_badges(metadata)
        self.text_area.insert(tk.END, "\n")
        
        self.display_gps_data(metadata)
        self.display_full_metadata(path, metadata)
        
        self.text_area.config(state=tk.DISABLED)
    
    def create_metadata_badges(self, metadata: Dict[str, Any]):
        badges_frame = tk.Frame(self.text_area, bg=self.TEXT_BG)
        self.text_area.window_create(tk.END, window=badges_frame)
        
        badge_data = [
            ("EXIF", "EXIF" in json.dumps(metadata)), 
            ("GPS", "GPSLatitude" in metadata and "GPSLongitude" in metadata),
            ("ICC", "ICCProfileName" in metadata),
            ("XMP", any("XMP" in key for key in metadata.keys()))
        ]
        
        for i, (title, present) in enumerate(badge_data):
            color = "#00ff00" if present else self.ACCENT_COLOR
            tk.Label(
                badges_frame, 
                text=f" {title} {'✅' if present else '❌'} ",
                font=("Consolas", 10, "bold"),
                bg=self.TEXT_BG,
                fg=color,
                padx=8,
                pady=4,
                bd=1,
                relief=tk.RIDGE
            ).grid(row=0, column=i, padx=5, pady=5)
    
    def display_gps_data(self, metadata: Dict[str, Any]):
        gps_lat = metadata.get("GPSLatitude")
        gps_lon = metadata.get("GPSLongitude")
        gps_lat_ref = metadata.get("GPSLatitudeRef", "")
        gps_lon_ref = metadata.get("GPSLongitudeRef", "")

        lat_decimal = self.dms_to_decimal(gps_lat, gps_lat_ref) if gps_lat else None
        lon_decimal = self.dms_to_decimal(gps_lon, gps_lon_ref) if gps_lon else None

        if lat_decimal and lon_decimal:
            self.text_area.insert(tk.END, "📍 GPS COORDINATES FOUND:\n", "subheader")
            self.text_area.insert(tk.END, f"LATITUDE: {lat_decimal} ({gps_lat}) {gps_lat_ref}\n", "regular")
            self.text_area.insert(tk.END, f"LONGITUDE: {lon_decimal} ({gps_lon}) {gps_lon_ref}\n\n", "regular")
            self.btn_map.config(state=tk.NORMAL)
            self.btn_map.lat = lat_decimal
            self.btn_map.lon = lon_decimal
        else:
            self.text_area.insert(tk.END, "📍 GPS DATA\n", "subheader")
            self.text_area.insert(tk.END, "📵 NO GPS DATA FOUND\n", "warning")
            self.text_area.insert(tk.END, "💡 TIP: USE GPS-ENABLED PHOTOS\n\n", "info")
    
    def display_full_metadata(self, path: str, metadata: Dict[str, Any]):
        self.text_area.insert(tk.END, "📋 FULL METADATA:\n", "subheader")
        metadata_display = metadata.copy()
        metadata_display["FileLocation"] = os.path.abspath(path)
        self.text_area.insert(tk.END, json.dumps(metadata_display, indent=4), "metadata")
    
    def save_metadata(self):
        if not self.current_metadata or not self.current_image_path:
            messagebox.showwarning("WARNING", "NO METADATA TO SAVE", parent=self.master)
            return
            
        base_name = os.path.basename(self.current_image_path)
        name, _ = os.path.splitext(base_name)
        timestamp = datetime.now().strftime("%d%m%Y-%H%M%S")
        filename = f"{name}-{timestamp}.json"
        
        try:
            metadata_to_save = self.current_metadata.copy()
            metadata_to_save["FileLocation"] = os.path.abspath(self.current_image_path)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(metadata_to_save, f, indent=4)
                
            messagebox.showinfo("SUCCESS", f"METADATA SAVED AS:\n{filename}", parent=self.master)
            self.status_label.config(text=f"STATUS: SAVED TO {filename}")
        except Exception as e:
            messagebox.showerror("ERROR", str(e).upper(), parent=self.master)
            self.status_label.config(text="STATUS: SAVE FAILED")
    
    def clear_output(self):
        self.current_metadata = None
        self.current_image_path = None
        
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "🗑 OUTPUT CLEARED. SELECT IMAGE TO CONTINUE.", "regular")
        self.text_area.config(state=tk.DISABLED)
        
        self.btn_delete.config(state=tk.DISABLED)
        self.btn_map.config(state=tk.DISABLED)
        self.btn_embed.config(state=tk.DISABLED)
        self.status_label.config(text="STATUS: READY")
    
    def open_map_with_coords(self):
        if hasattr(self.btn_map, 'lat') and hasattr(self.btn_map, 'lon'):
            self.open_map(self.btn_map.lat, self.btn_map.lon)
    
    def open_map(self, lat: float, lon: float):
        try:
            webbrowser.open(f"https://www.google.com/maps?q={lat},{lon}")
        except Exception as e:
            messagebox.showerror("ERROR", f"COULD NOT OPEN MAP: {e}", parent=self.master)
    
    def insert_custom_metadata(self):
        if not self.current_image_path:
            messagebox.showwarning("WARNING", "NO IMAGE SELECTED", parent=self.master)
            return
            
        custom_message = simpledialog.askstring("MESSAGE ENTRY", "ENTER MESSAGE TO EMBED:", parent=self.master)
        if not custom_message:
            return
            
        try:
            result = subprocess.run(
                ["exiftool", f"-Comment={custom_message}", "-overwrite_original", self.current_image_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode == 0:
                messagebox.showinfo("SUCCESS", "METADATA EMBEDDED", parent=self.master)
                self.current_metadata = self.extract_metadata(self.current_image_path)
                self.display_metadata(self.current_image_path, self.current_metadata)
            else:
                raise Exception(result.stderr)
        except Exception as e:
            messagebox.showerror("ERROR", f"EMBED FAILED: {e}", parent=self.master)
    
    def show_info(self):
        messagebox.showinfo(
            "SYSTEM INFO",
            "📸 IMAGE METADATA ANALYZER\n\n"
            "VERSION: 2.0\n"
            "SYSTEM: PYTHON/TKINTER\n\n"
            "CAPABILITIES:\n"
            "• EXIF/IPTC/XMP/ICC METADATA EXTRACTION\n"
            "• GPS GEOLOCATION MAPPING\n"
            "• RAW/HEIC FORMAT SUPPORT\n"
            "• METADATA EMBEDDING\n",
            parent=self.master
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = MetadataAnalyzer(root)
    root.mainloop()