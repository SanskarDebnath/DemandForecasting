import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet, InvalidToken

BG_COLOR = "#0f111a"
FG_COLOR = "#e0e0e0"
ENTRY_BG = "#1f2233"
TEXT_BG = "#181b28"
BUTTON_BG = "#2c3e50"
BUTTON_ACTIVE = "#34495e"
WARNING_COLOR = "#e74c3c"
SUCCESS_COLOR = "#2ecc71"

class DecryptorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Secure Decryptor Console")
        self.master.geometry("880x620")
        self.master.configure(bg=BG_COLOR)

        self.user_key = None

        self._build_interface()

    def _build_interface(self):
        style = {"font": ("Segoe UI", 11), "bg": BG_COLOR, "fg": FG_COLOR}
        entry_style = {
            "font": ("Consolas", 11), "bg": ENTRY_BG, "fg": FG_COLOR,
            "insertbackground": FG_COLOR, "borderwidth": 1, "relief": tk.FLAT,
            "highlightthickness": 1, "highlightbackground": "#2c3e50"
        }
        button_style = {
            "font": ("Segoe UI", 11, "bold"), "bg": BUTTON_BG, "fg": FG_COLOR,
            "activebackground": BUTTON_ACTIVE, "activeforeground": FG_COLOR,
            "bd": 0, "relief": tk.FLAT, "cursor": "hand2", "padx": 10, "pady": 5
        }

        tk.Label(self.master, text="🔐 Secure Decryption Console", font=("Segoe UI", 14, "bold"), bg=BG_COLOR, fg=SUCCESS_COLOR).pack(pady=(20, 10))
        tk.Label(self.master, text="Enter Decryption Key:", **style).pack(anchor="w", padx=40)

        self.entry_key = tk.Entry(self.master, width=80, **entry_style)
        self.entry_key.pack(pady=6, padx=40)

        tk.Button(self.master, text="Load Key", command=self._load_key, **button_style).pack(pady=(10, 20))

        tk.Label(self.master, text="Encrypted Message:", **style).pack(anchor="w", padx=40)

        self.entry_cipher = tk.Entry(self.master, width=80, **entry_style)
        self.entry_cipher.pack(pady=6, padx=40)
        self.entry_cipher.config(state='disabled')

        self.decrypt_btn = tk.Button(self.master, text="Decrypt Message", command=self._decrypt, **button_style)
        self.decrypt_btn.pack(pady=(10, 20))
        self.decrypt_btn.config(state='disabled')

        self.output = tk.Text(self.master, height=8, width=80, font=("Consolas", 11), bg=TEXT_BG, fg=FG_COLOR, borderwidth=1, relief=tk.FLAT)
        self.output.tag_config("success", foreground=SUCCESS_COLOR)
        self.output.tag_config("error", foreground=WARNING_COLOR)
        self.output.pack(padx=40)
        self.output.config(state='disabled')

        tk.Label(self.master, text="Access Restricted — Authorized Personnel Only", font=("Segoe UI", 10), bg=BG_COLOR, fg="#888888").pack(pady=20)

    def _load_key(self):
        key = self.entry_key.get().strip()
        if not key:
            messagebox.showwarning("Warning", "Please enter a decryption key", parent=self.master)
            return
        self.user_key = key
        self.entry_cipher.config(state='normal')
        self.decrypt_btn.config(state='normal')

    def _decrypt(self):
        encrypted_text = self.entry_cipher.get().strip()
        self.output.config(state='normal')
        self.output.delete("1.0", tk.END)

        if not self.user_key or not encrypted_text:
            self.output.insert(tk.END, "❌ Missing input", "error")
        else:
            try:
                cipher = Fernet(self.user_key.encode())
                decrypted = cipher.decrypt(encrypted_text.encode()).decode()
                self.output.insert(tk.END, f"✅ Decrypted:\n{decrypted}", "success")
            except InvalidToken:
                self.output.insert(tk.END, "❌ Invalid key or corrupted ciphertext", "error")
            except Exception as e:
                self.output.insert(tk.END, f"❌ System Error: {str(e).upper()}", "error")

        self.output.config(state='disabled')

def main():
    root = tk.Tk()
    app = DecryptorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
