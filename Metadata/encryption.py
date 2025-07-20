# encryptor.py
import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet

# --- Theme Colors ---
BG_COLOR = "#121212"
FG_COLOR = "#00ff00"
ENTRY_BG = "#1e1e1e"
TEXT_BG = "#0a0a0a"
BUTTON_BG = "#1a3d1a"
BUTTON_ACTIVE = "#2a5d2a"

# --- Encrypt Function ---
def encrypt_text():
    text = entry_encrypt.get().strip()
    if not text:
        messagebox.showwarning("Warning", "Enter text to encrypt", parent=root)
        return

    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted = cipher.encrypt(text.encode()).decode()

    key_output.config(state='normal')
    key_output.delete("1.0", tk.END)
    key_output.insert(tk.END, key.decode())
    key_output.config(state='disabled')

    encrypted_output.config(state='normal')
    encrypted_output.delete("1.0", tk.END)
    encrypted_output.insert(tk.END, encrypted)
    encrypted_output.config(state='disabled')

# --- GUI Setup ---
root = tk.Tk()
root.title("ENCRYPTOR MODULE :: CLASSIFIED")
root.geometry("800x600")
root.configure(bg=BG_COLOR)

# --- Styles ---
entry_style = {
    "font": ("Consolas", 10),
    "bg": ENTRY_BG,
    "fg": FG_COLOR,
    "insertbackground": FG_COLOR,
    "borderwidth": 2,
    "relief": tk.SOLID
}
button_style = {
    "font": ("Consolas", 10, "bold"),
    "bg": BUTTON_BG,
    "fg": "#ffffff",
    "activebackground": BUTTON_ACTIVE,
    "activeforeground": "#ffffff",
    "borderwidth": 3,
    "relief": tk.RAISED
}

# --- Header ---
tk.Label(root, text="ENCRYPTION PANEL", font=("Consolas", 14, "bold"), bg=BG_COLOR, fg=FG_COLOR).pack(pady=10)

# --- Plaintext Entry ---
tk.Label(root, text="ENTER TEXT TO ENCRYPT:", font=("Consolas", 10), bg=BG_COLOR, fg=FG_COLOR).pack()
entry_encrypt = tk.Entry(root, width=90, **entry_style)
entry_encrypt.pack(pady=5)

# --- Encrypt Button ---
tk.Button(root, text="⏣ ENCRYPT ⏣", command=encrypt_text, **button_style).pack(pady=10)

# --- Key Output ---
tk.Label(root, text="ENCRYPTION KEY:", font=("Consolas", 10), bg=BG_COLOR, fg=FG_COLOR).pack()
key_output = tk.Text(root, height=2, width=90, font=("Consolas", 10), bg=TEXT_BG, fg=FG_COLOR, borderwidth=2, relief=tk.SUNKEN)
key_output.pack(pady=5)
key_output.config(state='disabled')

# --- Encrypted Output ---
tk.Label(root, text="ENCRYPTED TEXT:", font=("Consolas", 10), bg=BG_COLOR, fg=FG_COLOR).pack()
encrypted_output = tk.Text(root, height=6, width=90, font=("Consolas", 10), bg=TEXT_BG, fg=FG_COLOR, borderwidth=2, relief=tk.SUNKEN)
encrypted_output.pack(pady=5)
encrypted_output.config(state='disabled')

# --- Footer ---
tk.Label(root, text="ENCRYPTOR // SANSKAR DEBNATH", font=("Consolas", 10), bg=BG_COLOR, fg="#007700").pack(pady=10)

root.mainloop()