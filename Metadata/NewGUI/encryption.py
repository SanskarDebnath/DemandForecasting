import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet

BG_COLOR = "#0f111a"
FG_COLOR = "#e0e0e0"
ENTRY_BG = "#1f2233"
TEXT_BG = "#181b28"
BUTTON_BG = "#2c3e50"
BUTTON_ACTIVE = "#34495e"
SUCCESS_COLOR = "#2ecc71"

class EncryptorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Secure Encryptor Console")
        self.master.geometry("880x620")
        self.master.configure(bg=BG_COLOR)

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

        tk.Label(self.master, text="🔒 Secure Encryption Console", font=("Segoe UI", 14, "bold"), bg=BG_COLOR, fg=SUCCESS_COLOR).pack(pady=(20, 10))
        tk.Label(self.master, text="Enter Text to Encrypt:", **style).pack(anchor="w", padx=40)

        self.entry_text = tk.Entry(self.master, width=80, **entry_style)
        self.entry_text.pack(pady=6, padx=40)

        tk.Button(self.master, text="Encrypt Text", command=self._encrypt, **button_style).pack(pady=(10, 20))

        tk.Label(self.master, text="Encryption Key:", **style).pack(anchor="w", padx=40)
        self.output_key = tk.Text(self.master, height=2, width=80, font=("Consolas", 11), bg=TEXT_BG, fg=FG_COLOR, borderwidth=1, relief=tk.FLAT)
        self.output_key.pack(padx=40, pady=6)
        self.output_key.config(state='disabled')

        tk.Label(self.master, text="Encrypted Text:", **style).pack(anchor="w", padx=40)
        self.output_encrypted = tk.Text(self.master, height=6, width=80, font=("Consolas", 11), bg=TEXT_BG, fg=FG_COLOR, borderwidth=1, relief=tk.FLAT)
        self.output_encrypted.pack(padx=40, pady=6)
        self.output_encrypted.config(state='disabled')

        tk.Label(self.master, text="Encryptor Utility — Authorized Use Only", font=("Segoe UI", 10), bg=BG_COLOR, fg="#888888").pack(pady=20)

    def _encrypt(self):
        text = self.entry_text.get().strip()
        if not text:
            messagebox.showwarning("Warning", "Enter text to encrypt", parent=self.master)
            return

        key = Fernet.generate_key()
        cipher = Fernet(key)
        encrypted = cipher.encrypt(text.encode()).decode()

        self.output_key.config(state='normal')
        self.output_key.delete("1.0", tk.END)
        self.output_key.insert(tk.END, key.decode())
        self.output_key.config(state='disabled')

        self.output_encrypted.config(state='normal')
        self.output_encrypted.delete("1.0", tk.END)
        self.output_encrypted.insert(tk.END, encrypted)
        self.output_encrypted.config(state='disabled')

def main():
    root = tk.Tk()
    app = EncryptorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
