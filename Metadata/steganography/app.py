import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import subprocess
import json
import webbrowser
import shutil
import tempfile
import base64
from datetime import datetime
from typing import Optional, Dict, Any

class AdvancedMetadataAnalyzer:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.current_metadata = None
        self.current_image_path = None
        self.temp_files = []
        
        # Set up ExifTool paths first
        self.exiftool_path = self.get_exiftool_path()
        if not self.exiftool_path:
            messagebox.showerror("Error", "Could not find ExifTool installation")
            sys.exit(1)
            
        # Then setup UI once
        self.setup_styles()
        self.create_ui()        
    def get_exiftool_path(self) -> Optional[str]:
        """Find ExifTool executable in common locations"""
        # Check if exiftool is in PATH
        if shutil.which("exiftool"):
            return "exiftool"
            
        # Check in current directory
        if os.path.exists("exiftool.exe"):
            return "exiftool.exe"
            
        # Check in exiftool_files subdirectory
        if os.path.exists(os.path.join("exiftool_files", "exiftool.exe")):
            return os.path.join("exiftool_files", "exiftool.exe")
            
        # Check in script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        exiftool_path = os.path.join(script_dir, "exiftool.exe")
        if os.path.exists(exiftool_path):
            return exiftool_path
            
        exiftool_path = os.path.join(script_dir, "exiftool_files", "exiftool.exe")
        if os.path.exists(exiftool_path):
            return exiftool_path
            
        return None
        
    def setup_styles(self) -> None:
        """Define color scheme and fonts"""
        self.style = {
            'bg': "#0a0a0a",
            'fg': "#00ff00",
            'accent': "#ff5555",
            'text_bg': "#121212",
            'button': "#1a3d1a",
            'button_active': "#2a5d2a",
            'header': "#003300",
            'success': "#00ff00",
            'warning': "#ff5555",
            'info': "#00cc00",
            'font': "Consolas",
            'font_bold': ("Consolas", "bold")
        }
        
    def create_ui(self) -> None:
        """Build the user interface"""
        self.create_header()
        self.create_main_frame()
        self.create_status_bar()
        self.create_menu()
        
    def create_header(self) -> None:
        """Create application header"""
        header = tk.Frame(self.root, bg=self.style['header'], height=80)
        header.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(
            header, text="🔐", font=(self.style['font'], 28),
            bg=self.style['header'], fg=self.style['fg']
        ).pack(side=tk.LEFT, padx=(20, 10), pady=10)
        
        tk.Label(
            header, text="SECURE METADATA ANALYZER", 
            font=(self.style['font'], 18, "bold"),
            bg=self.style['header'], fg=self.style['fg']
        ).pack(side=tk.LEFT, pady=10)

    def create_main_frame(self) -> None:
        """Create main content area"""
        main_frame = tk.Frame(self.root, bg=self.style['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        self.create_button_panel(main_frame)
        self.create_text_display(main_frame)
        
    def create_button_panel(self, parent: tk.Frame) -> None:
        """Create control buttons panel"""
        button_frame = tk.Frame(parent, bg=self.style['bg'])
        button_frame.pack(fill=tk.X, pady=(10, 15))
        
        buttons = [
            ("📁 SELECT IMAGE", self.load_image),
            ("💾 SAVE METADATA", self.save_metadata),
            ("🌍 VIEW IN MAPS", self.open_map_with_coords, tk.DISABLED),
            ("📝 EMBED MESSAGE", self.embed_custom_metadata),
            ("🔒 ATTACH FILE", self.attach_hidden_file),
            ("🔓 EXTRACT FILE", self.extract_hidden_file, tk.DISABLED),
            ("🗑️ CLEAR", self.clear_output)
        ]
        
        for i, (text, command, *state) in enumerate(buttons):
            btn = tk.Button(
                button_frame,
                text=text,
                command=command,
                font=(self.style['font'], 10, "bold"),
                bg=self.style['button'],
                fg="white",
                activebackground=self.style['button_active'],
                activeforeground="white",
                borderwidth=3,
                relief=tk.RAISED,
                state=state[0] if state else tk.NORMAL
            )
            btn.pack(side=tk.LEFT if i < len(buttons)-1 else tk.RIGHT, padx=5)
            btn.bind("<Enter>", lambda e: e.widget.config(bg=self.style['button_active']))
            btn.bind("<Leave>", lambda e: e.widget.config(bg=self.style['button']))
            
            # Store important buttons as attributes
            if "MAPS" in text:
                self.btn_map = btn
            elif "EXTRACT" in text:
                self.btn_extract = btn
            elif "CLEAR" in text:
                self.btn_clear = btn

    def create_text_display(self, parent: tk.Frame) -> None:
        """Create the metadata display area"""
        text_frame = tk.Frame(parent, bg=self.style['text_bg'], bd=2, relief=tk.SUNKEN)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_area = tk.Text(
            text_frame, 
            bg=self.style['text_bg'], 
            fg=self.style['fg'], 
            font=(self.style['font'], 10),
            yscrollcommand=scrollbar.set,
            padx=15,
            pady=15,
            bd=0,
            highlightthickness=0,
            insertbackground=self.style['fg']
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_area.yview)
        
        self.initialize_text_display()
    
    def initialize_text_display(self) -> None:
        """Set up initial text display with welcome message"""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        
        # Configure text tags
        tags = [
            ("header", 14, "bold", self.style['fg']),
            ("subheader", 12, "bold", self.style['fg']),
            ("regular", 11, "", self.style['fg']),
            ("metadata", 10, "", self.style['fg']),
            ("success", 11, "", self.style['success']),
            ("warning", 11, "", self.style['warning']),
            ("info", 11, "", self.style['info'])
        ]
        
        for name, size, weight, color in tags:
            self.text_area.tag_configure(
                name, 
                font=(self.style['font'], size, weight), 
                foreground=color
            )
        
        welcome_msg = [
            ("🔐 SECURE METADATA ANALYZER [READY]\n\n", "header"),
            ("SELECT AN IMAGE FILE TO BEGIN ANALYSIS\n\n", "regular"),
            ("SUPPORTED FORMATS: JPG, PNG, TIFF, BMP, GIF, DNG, RAW, HEIC\n", "info"),
            ("\n🔒 HIDDEN FILE ATTACHMENT FEATURE AVAILABLE\n", "success"),
            ("\n⚠️ WARNING: USE RESPONSIBLY. UNAUTHORIZED ACCESS PROHIBITED\n", "warning")
        ]
        
        for text, tag in welcome_msg:
            self.text_area.insert(tk.END, text, tag)
            
        self.text_area.config(state=tk.DISABLED)
    
    def create_status_bar(self) -> None:
        """Create status bar at bottom of window"""
        status_frame = tk.Frame(self.root, bg=self.style['header'], height=24)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(
            status_frame, 
            text="STATUS: READY", 
            bg=self.style['header'], 
            fg=self.style['fg'],
            font=(self.style['font'], 9),
            anchor=tk.W,
            padx=10
        )
        self.status_label.pack(fill=tk.X, side=tk.LEFT)
    
    def create_menu(self) -> None:
        """Create menu bar"""
        menubar = tk.Menu(
            self.root, 
            bg=self.style['header'], 
            fg=self.style['fg'], 
            bd=0, 
            font=(self.style['font'], 9)
        )
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.style['text_bg'], fg=self.style['fg'])
        file_menu.add_command(label="OPEN IMAGE", command=self.load_image)
        file_menu.add_command(label="SAVE METADATA", command=self.save_metadata)
        file_menu.add_separator()
        file_menu.add_command(label="EXIT", command=self.cleanup)
        menubar.add_cascade(label="FILE", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.style['text_bg'], fg=self.style['fg'])
        edit_menu.add_command(label="CLEAR", command=self.clear_output)
        edit_menu.add_command(label="ATTACH FILE", command=self.attach_hidden_file)
        edit_menu.add_command(label="EXTRACT FILE", command=self.extract_hidden_file)
        menubar.add_cascade(label="EDIT", menu=edit_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.style['text_bg'], fg=self.style['fg'])
        help_menu.add_command(label="ABOUT", command=self.show_about)
        menubar.add_cascade(label="HELP", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    # Core functionality methods
    def load_image(self) -> None:
        """Load and process selected image file"""
        filetypes = [
            ("Image files", "*.jpg;*.jpeg;*.png;*.tiff;*.bmp;*.gif;*.dng;*.raw;*.heic"),
            ("All files", "*.*")
        ]
        
        path = filedialog.askopenfilename(filetypes=filetypes)
        if not path:
            return
            
        self.current_image_path = path
        self.status_label.config(text=f"PROCESSING: {os.path.basename(path)}")
        self.root.update()
        
        try:
            self.current_metadata = self.extract_metadata(path)
            self.display_metadata(path, self.current_metadata)
            self.btn_map.config(state=tk.NORMAL)
            self.btn_extract.config(state=tk.NORMAL)
            self.btn_clear.config(state=tk.NORMAL)
            self.status_label.config(text=f"LOADED: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("ERROR", f"PROCESSING FAILED: {str(e)}", parent=self.root)
            self.status_label.config(text="STATUS: READY")
    
    def extract_metadata(self, path: str) -> Dict[str, Any]:
        """Extract metadata using exiftool"""
        try:
            result = subprocess.run(
                [self.exiftool_path, '-j', path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            if not result.stdout.strip():
                return {"error": "No metadata found or unsupported format"}
                
            metadata = json.loads(result.stdout)[0]
            
            # Check for hidden file marker
            if 'Comment' in metadata and "hidden_file" in metadata['Comment']:
                metadata['hidden_file'] = True
                
            return metadata
            
        except subprocess.CalledProcessError as e:
            return {"error": f"ExifTool error: {e.stderr.strip()}"}
        except Exception as e:
            return {"error": str(e)}
    
    def display_metadata(self, path: str, metadata: Dict[str, Any]) -> None:
        """Display metadata in the text area"""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        
        file_name = os.path.basename(path)
        self.text_area.insert(tk.END, f"📁 FILE: {file_name}\n", "header")
        self.text_area.insert(tk.END, f"📂 PATH: {os.path.abspath(path)}\n\n", "info")
        
        if "error" in metadata:
            self.text_area.insert(tk.END, f"❌ ERROR: {metadata['error']}\n", "warning")
            self.text_area.config(state=tk.DISABLED)
            return

        # Show metadata overview
        self.text_area.insert(tk.END, "🔍 METADATA OVERVIEW:\n", "subheader")
        self.create_metadata_badges(metadata)
        self.text_area.insert(tk.END, "\n")
        
        # Show GPS data if available
        self.display_gps_data(metadata)
        
        # Show hidden file indicator if present
        if metadata.get('hidden_file'):
            self.text_area.insert(tk.END, "🔒 HIDDEN FILE DETECTED\n\n", "success")
        
        # Show full metadata
        self.text_area.insert(tk.END, "📋 FULL METADATA:\n", "subheader")
        metadata_display = metadata.copy()
        metadata_display["FileLocation"] = os.path.abspath(path)
        self.text_area.insert(tk.END, json.dumps(metadata_display, indent=4), "metadata")
        
        self.text_area.config(state=tk.DISABLED)
    
    def create_metadata_badges(self, metadata: Dict[str, Any]) -> None:
        """Create visual badges for metadata categories"""
        badges_frame = tk.Frame(self.text_area, bg=self.style['text_bg'])
        self.text_area.window_create(tk.END, window=badges_frame)
        
        categories = [
            ("EXIF", "EXIF" in json.dumps(metadata)), 
            ("GPS", self.has_gps_data(metadata)),
            ("ICC", "ICCProfileName" in metadata),
            ("XMP", any("XMP" in key for key in metadata.keys())),
            ("HIDDEN", metadata.get('hidden_file', False))
        ]
        
        for i, (title, present) in enumerate(categories):
            color = self.style['success'] if present else self.style['warning']
            emoji = "✅" if present else "❌"
            
            badge = tk.Label(
                badges_frame, 
                text=f" {title} {emoji} ",
                font=(self.style['font'], 10, "bold"),
                bg=self.style['text_bg'],
                fg=color,
                padx=8,
                pady=4,
                bd=1,
                relief=tk.RIDGE
            )
            badge.grid(row=0, column=i, padx=5, pady=5)
    
    def has_gps_data(self, metadata: Dict[str, Any]) -> bool:
        """Check if GPS data exists in metadata"""
        return all(key in metadata for key in ['GPSLatitude', 'GPSLongitude'])
    
    def display_gps_data(self, metadata: Dict[str, Any]) -> None:
        """Display GPS coordinates if available"""
        if not self.has_gps_data(metadata):
            self.text_area.insert(tk.END, "📍 GPS DATA\n", "subheader")
            self.text_area.insert(tk.END, "📵 NO GPS DATA FOUND\n\n", "warning")
            return
            
        lat = self.dms_to_decimal(
            metadata['GPSLatitude'], 
            metadata.get('GPSLatitudeRef', 'N')
        )
        lon = self.dms_to_decimal(
            metadata['GPSLongitude'], 
            metadata.get('GPSLongitudeRef', 'E')
        )
        
        if lat and lon:
            self.text_area.insert(tk.END, "📍 GPS COORDINATES FOUND:\n", "subheader")
            self.text_area.insert(tk.END, f"LATITUDE: {lat} ({metadata['GPSLatitude']}) {metadata.get('GPSLatitudeRef', '')}\n", "regular")
            self.text_area.insert(tk.END, f"LONGITUDE: {lon} ({metadata['GPSLongitude']}) {metadata.get('GPSLongitudeRef', '')}\n\n", "regular")
            
            # Store coordinates for map button
            self.btn_map.lat = lat
            self.btn_map.lon = lon
    
    def dms_to_decimal(self, dms_str: str, ref: str) -> Optional[float]:
        """Convert DMS coordinates to decimal format"""
        try:
            parts = str(dms_str).replace("deg", "").replace('"', "").replace("'", "").split()
            degrees = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])
            decimal = degrees + minutes / 60 + seconds / 3600
            return round(decimal * (-1 if ref in ['S', 'W'] else 1), 6)
        except Exception:
            return None
    
    def save_metadata(self) -> None:
        """Save metadata to JSON file"""
        if not self.current_metadata or not self.current_image_path:
            messagebox.showwarning("WARNING", "NO METADATA TO SAVE", parent=self.root)
            return
            
        default_name = f"{os.path.splitext(os.path.basename(self.current_image_path))[0]}_metadata.json"
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=default_name,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not save_path:
            return
            
        try:
            metadata_to_save = self.current_metadata.copy()
            metadata_to_save["FileLocation"] = os.path.abspath(self.current_image_path)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(metadata_to_save, f, indent=4)
                
            messagebox.showinfo("SUCCESS", f"METADATA SAVED TO:\n{save_path}", parent=self.root)
            self.status_label.config(text=f"STATUS: SAVED TO {os.path.basename(save_path)}")
        except Exception as e:
            messagebox.showerror("ERROR", f"SAVE FAILED: {str(e)}", parent=self.root)
            self.status_label.config(text="STATUS: SAVE FAILED")
    
    def clear_output(self) -> None:
        """Clear current analysis"""
        self.current_metadata = None
        self.current_image_path = None
        
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "🗑 OUTPUT CLEARED. SELECT IMAGE TO CONTINUE.", "regular")
        self.text_area.config(state=tk.DISABLED)
        
        self.btn_map.config(state=tk.DISABLED)
        self.btn_extract.config(state=tk.DISABLED)
        self.btn_clear.config(state=tk.DISABLED)
        self.status_label.config(text="STATUS: READY")
    
    def open_map_with_coords(self) -> None:
        """Open maps with stored coordinates"""
        if hasattr(self.btn_map, 'lat') and hasattr(self.btn_map, 'lon'):
            self.open_map(self.btn_map.lat, self.btn_map.lon)
    
    def open_map(self, lat: float, lon: float) -> None:
        """Open default browser with Google Maps location"""
        try:
            webbrowser.open(f"https://www.google.com/maps?q={lat},{lon}")
        except Exception as e:
            messagebox.showerror("ERROR", f"COULD NOT OPEN MAP: {e}", parent=self.root)
    
    def embed_custom_metadata(self) -> None:
        """Embed custom message in image metadata"""
        if not self.current_image_path:
            messagebox.showwarning("WARNING", "NO IMAGE SELECTED", parent=self.root)
            return
            
        custom_message = simpledialog.askstring(
            "EMBED MESSAGE", 
            "ENTER MESSAGE TO EMBED IN IMAGE:",
            parent=self.root
        )
        
        if not custom_message:
            return
            
        try:
            result = subprocess.run(
                ["exiftool", f"-Comment={custom_message}", "-overwrite_original", self.current_image_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            if result.returncode == 0:
                messagebox.showinfo("SUCCESS", "MESSAGE EMBEDDED IN IMAGE METADATA", parent=self.root)
                self.current_metadata = self.extract_metadata(self.current_image_path)
                self.display_metadata(self.current_image_path, self.current_metadata)
            else:
                raise Exception(result.stderr)
        except Exception as e:
            messagebox.showerror("ERROR", f"EMBED FAILED: {str(e)}", parent=self.root)
    
    def attach_hidden_file(self) -> None:
        """Attach a hidden file to the current image"""
        if not self.current_image_path:
            messagebox.showwarning("Warning", "No image selected", parent=self.root)
            return
            
        MAX_SIZE = 96000  # Safe limit for metadata comments
        
        file_path = filedialog.askopenfilename(title="Select file to hide")
        if not file_path:
            return
            
        try:
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > MAX_SIZE:
                messagebox.showwarning(
                    "File Too Large",
                    f"File size ({file_size/1024:.1f}KB) exceeds maximum allowed ({MAX_SIZE/1024:.1f}KB)\n"
                    "Please select a smaller file.",
                    parent=self.root
                )
                return

            # Create temporary working copy
            temp_path = tempfile.mktemp(suffix=".tmp")
            shutil.copy2(self.current_image_path, temp_path)
            self.temp_files.append(temp_path)
            
            # Read and encode file
            with open(file_path, 'rb') as f:
                file_data = f.read()
            encoded_data = base64.b64encode(file_data).decode('utf-8')
            
            # Create backup
            backup_path = self.current_image_path + ".bak"
            shutil.copy2(self.current_image_path, backup_path)
            self.temp_files.append(backup_path)
            
            # Store filename and size in UserComment
            filename = os.path.basename(file_path)
            marker = f"hidden_file:{filename}:{file_size}"
            exiftool_path = os.path.join(os.path.dirname(__file__), 'exiftool.exe')

            # First command - store marker
            subprocess.run(
                [exiftool_path, f'-UserComment={marker}', '-overwrite_original', temp_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Second command - store data
            subprocess.run(
                [exiftool_path, f'-Comment={encoded_data}', '-overwrite_original', temp_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Verify the attachment
            new_metadata = self.extract_metadata(temp_path)
            if 'UserComment' not in new_metadata or filename not in new_metadata['UserComment']:
                raise Exception("File attachment verification failed")
            
            # Replace original with modified file
            os.replace(temp_path, self.current_image_path)
            
            messagebox.showinfo(
                "Success", 
                f"File '{filename}' successfully hidden in image metadata",
                parent=self.root
            )
            
            self.current_metadata = new_metadata
            self.display_metadata(self.current_image_path, self.current_metadata)
            self.btn_extract.config(state=tk.NORMAL)
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror(
                "Error", 
                f"ExifTool failed: {e.stderr.decode().strip()}",
                parent=self.root
            )
            # Restore from backup if error occurs
            if os.path.exists(backup_path):
                os.replace(backup_path, self.current_image_path)
        except Exception as e:
            messagebox.showerror(
                "Error", 
                f"Failed to attach file: {str(e)}",
                parent=self.root
            )
        finally:
            # Clean up temp files
            self.clean_temp_files()

    def create_button_panel(self, parent: tk.Frame) -> None:
        """Create control buttons panel"""
        button_frame = tk.Frame(parent, bg=self.style['bg'])
        button_frame.pack(fill=tk.X, pady=(10, 15))
        
        buttons = [
            ("📁 SELECT IMAGE", self.load_image),
            ("💾 SAVE METADATA", self.save_metadata),
            ("🌍 VIEW IN MAPS", self.open_map_with_coords, tk.DISABLED),
            ("📝 EMBED MESSAGE", self.embed_custom_metadata),
            ("🔒 ATTACH FILE", self.attach_hidden_file),
            ("🔓 EXTRACT FILE", self.extract_hidden_file, tk.DISABLED),
            ("🗑️ CLEAR", self.clear_output)
        ]
        
        for i, (text, command, *state) in enumerate(buttons):
            btn = tk.Button(
                button_frame,
                text=text,
                command=command,
                font=(self.style['font'], 10, "bold"),
                bg=self.style['button'],
                fg="white",
                activebackground=self.style['button_active'],
                activeforeground="white",
                borderwidth=3,
                relief=tk.RAISED,
                state=state[0] if state else tk.NORMAL
            )
            btn.pack(side=tk.LEFT if i < len(buttons)-1 else tk.RIGHT, padx=5)
            btn.bind("<Enter>", lambda e: e.widget.config(bg=self.style['button_active']))
            btn.bind("<Leave>", lambda e: e.widget.config(bg=self.style['button']))
            
            # Store important buttons as attributes
            if "MAPS" in text:
                self.btn_map = btn
            elif "EXTRACT" in text:
                self.btn_extract = btn
            elif "CLEAR" in text:
                self.btn_clear = btn

    def extract_hidden_file(self) -> None:
        """Extract a hidden file from current image"""
        if not self.current_metadata or not self.current_image_path:
            messagebox.showwarning("Warning", "No image loaded", parent=self.root)
            return
            
        if 'UserComment' not in self.current_metadata:
            messagebox.showinfo("Info", "No hidden file found", parent=self.root)
            return
            
        try:
            # Parse the marker
            marker = self.current_metadata['UserComment']
            if "hidden_file:" not in marker:
                raise Exception("Invalid hidden file format")
                
            parts = marker.split(":")
            if len(parts) < 3:
                raise Exception("Invalid marker format")
                
            filename = parts[1]
            expected_size = int(parts[2])
            
            # Get encoded data from Comment field
            if 'Comment' not in self.current_metadata:
                raise Exception("No data found in Comment field")
                
            encoded_data = self.current_metadata['Comment']
            
            # Decode and verify
            file_data = base64.b64decode(encoded_data.encode('utf-8'))
            if len(file_data) != expected_size:
                raise Exception(f"Size mismatch: expected {expected_size}, got {len(file_data)}")
                
            # Get save location
            save_path = filedialog.asksaveasfilename(
                initialfile=filename,
                title="Save hidden file as"
            )
            
            if not save_path:
                return
                
            # Save the file
            with open(save_path, 'wb') as f:
                f.write(file_data)
                
            messagebox.showinfo(
                "Success", 
                f"Hidden file extracted to:\n{save_path}",
                parent=self.root
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error", 
                f"Failed to extract file: {str(e)}",
                parent=self.root
            )
    
    def clean_temp_files(self) -> None:
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass
        self.temp_files = []
    
    def cleanup(self) -> None:
        """Clean up and exit"""
        self.clean_temp_files()
        self.root.destroy()
    
    def show_about(self) -> None:
        """Show about dialog"""
        about_text = (
            "🔐 SECURE METADATA ANALYZER PRO\n\n"
            "VERSION: 2.5 (SECURE EDITION)\n\n"
            "FEATURES:\n"
            "- Advanced metadata extraction\n"
            "- GPS coordinate mapping\n"
            "- Secure file attachment system\n"
            "- Stealthy data embedding\n\n"
            "WARNING: Use only for authorized purposes.\n"
            "Unauthorized data concealment may violate laws.\n\n"
            "© 2023 Secure Systems Development"
        )
        
        messagebox.showinfo("ABOUT", about_text, parent=self.root)

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedMetadataAnalyzer(root)
    root.mainloop()