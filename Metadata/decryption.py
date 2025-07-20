import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet, InvalidToken

# Theme
BG_COLOR = "#121212"
FG_COLOR = "#00ff00"
ENTRY_BG = "#1e1e1e"
TEXT_BG = "#0a0a0a"
BUTTON_BG = "#1a3d1a"
BUTTON_ACTIVE = "#2a5d2a"
WARNING_COLOR = "#ff5555"

def unlock_decrypt_area():
    key = entry_key.get().strip()
    if not key:
        messagebox.showwarning("Warning", "Please enter a decryption key", parent=root)
        return
    entry_cipher.config(state='normal')
    decrypt_btn.config(state='normal')
    global user_key
    user_key = key

def decrypt_text():
    encrypted_text = entry_cipher.get().strip()
    output_decrypt.config(state='normal')
    output_decrypt.delete("1.0", tk.END)

    try:
        cipher = Fernet(user_key.encode())
        decrypted = cipher.decrypt(encrypted_text.encode()).decode()
        output_decrypt.insert(tk.END, f"✅ DECRYPTED:\n{decrypted}", "success")
    except InvalidToken:
        output_decrypt.insert(tk.END, "❌ INVALID KEY OR CORRUPTED CIPHERTEXT", "error")
    except Exception as e:
        output_decrypt.insert(tk.END, f"❌ SYSTEM ERROR: {str(e).upper()}", "error")

    output_decrypt.config(state='disabled')

root = tk.Tk()
root.title("DECRYPTOR // CLASSIFIED MODULE")
root.geometry("800x600")
root.configure(bg=BG_COLOR)

style = {"font": ("Consolas", 10), "bg": BG_COLOR, "fg": FG_COLOR}
entry_style = {"font": ("Consolas", 10), "bg": ENTRY_BG, "fg": FG_COLOR, "insertbackground": FG_COLOR, "borderwidth": 2, "relief": tk.SOLID}
button_style = {"font": ("Consolas", 10, "bold"), "bg": BUTTON_BG, "fg": "#ffffff", "activebackground": BUTTON_ACTIVE, "activeforeground": "#ffffff", "borderwidth": 3, "relief": tk.RAISED}

tk.Label(root, text="DECRYPTION MODULE", bg=BG_COLOR, fg=FG_COLOR, font=("Consolas", 12, "bold")).pack(pady=10)
tk.Label(root, text="ENTER DECRYPTION KEY:", **style).pack()

entry_key = tk.Entry(root, width=90, **entry_style)
entry_key.pack(pady=5)

tk.Button(root, text="⏣ LOAD KEY ⏣", command=unlock_decrypt_area, **button_style).pack(pady=5)

tk.Label(root, text="DECRYPTION MODULE", bg=BG_COLOR, fg=FG_COLOR, font=("Consolas", 12, "bold")).pack(pady=10)

entry_cipher = tk.Entry(root, width=90, **entry_style)
entry_cipher.pack(pady=5)
entry_cipher.config(state='disabled')

decrypt_btn = tk.Button(root, text="⏣ DECRYPT ⏣", command=decrypt_text, **button_style)
decrypt_btn.pack(pady=5)
decrypt_btn.config(state='disabled')

output_decrypt = tk.Text(root, height=6, width=90, font=("Consolas", 10), bg=TEXT_BG, fg=FG_COLOR, borderwidth=2, relief=tk.SUNKEN)
output_decrypt.tag_config("success", foreground="#00ff00")
output_decrypt.tag_config("error", foreground=WARNING_COLOR)
output_decrypt.pack()
output_decrypt.config(state='disabled')

tk.Label(root, text="FOR AUTHORIZED PERSONNEL ONLY", font=("Consolas", 10), bg=BG_COLOR, fg="#007700").pack(pady=10)

root.mainloop()