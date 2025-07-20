import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet, InvalidToken

BG_COLOR = "#121212"
FG_COLOR = "#00ff00"
ENTRY_BG = "#1e1e1e"
TEXT_BG = "#0a0a0a"
BUTTON_BG = "#1a3d1a"
BUTTON_ACTIVE = "#2a5d2a"
WARNING_COLOR = "#ff5555"

def encrypt_text():
    text = entry_encrypt.get().strip()
    if not text:
        messagebox.showwarning("Warning", "Enter text to encrypt", parent=root)
        return

    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted = cipher.encrypt(text.encode()).decode()

    output_encrypt.config(state='normal')
    output_encrypt.delete("1.0", tk.END)
    output_encrypt.insert(tk.END, f"🔑 KEY:\n{key.decode()}\n\n🔒 CIPHERTEXT:\n{encrypted}")
    output_encrypt.config(state='disabled')

def decrypt_text():
    key_input = entry_key.get().strip()
    encrypted_text = entry_decrypt.get().strip()

    output_decrypt.config(state='normal')
    output_decrypt.delete("1.0", tk.END)

    if not key_input or not encrypted_text:
        output_decrypt.insert(tk.END, "ERROR: KEY AND CIPHERTEXT REQUIRED", "error")
    else:
        try:
            cipher = Fernet(key_input.encode())
            decrypted = cipher.decrypt(encrypted_text.encode()).decode()
            output_decrypt.insert(tk.END, f"DECRYPTED PLAINTEXT:\n{decrypted}", "success")
        except InvalidToken:
            output_decrypt.insert(tk.END, "CRYPTOGRAPHIC FAILURE: INVALID KEY OR CORRUPTED DATA", "error")
        except Exception as e:
            output_decrypt.insert(tk.END, f"SYSTEM ERROR: {str(e).upper()}", "error")

    output_decrypt.config(state='disabled')

root = tk.Tk()
root.title("TOP SECRET // CRYPTO SYSTEM // CLASSIFIED")
root.geometry("800x650")
root.configure(bg=BG_COLOR)

style = {
    "font": ("Consolas", 11, "bold"),
    "bg": BG_COLOR,
    "fg": FG_COLOR,
    "selectbackground": "#003300",
    "selectforeground": "#ffffff",
    "insertbackground": FG_COLOR
}
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

header = tk.Label(root, 
                 text="◈ TOP SECRET CRYPTOGRAPHIC SYSTEM ◈",
                 font=("Consolas", 14, "bold"),
                 bg=BG_COLOR,
                 fg=FG_COLOR)
header.pack(pady=10)

tk.Label(root, 
        text="[ENCRYPTION MODULE]", 
        font=("Consolas", 11, "bold"),
        bg=BG_COLOR,
        fg="#00cc00").pack(pady=(10,5))

tk.Label(root, 
        text="ENTER CLEARTEXT:", 
        font=("Consolas", 10),
        bg=BG_COLOR,
        fg=FG_COLOR).pack()

entry_encrypt = tk.Entry(root, width=80, **entry_style)
entry_encrypt.pack(pady=5)

encrypt_btn = tk.Button(root, 
                       text="⏣ INITIATE ENCRYPTION ⏣", 
                       command=encrypt_text,
                       **button_style)
encrypt_btn.pack(pady=10)

output_encrypt = tk.Text(root, 
                        height=8, 
                        width=90, 
                        wrap='word', 
                        font=("Consolas", 10),
                        bg=TEXT_BG,
                        fg=FG_COLOR,
                        borderwidth=2,
                        relief=tk.SUNKEN)
output_encrypt.pack()
output_encrypt.config(state='disabled')

tk.Label(root, 
        text="\n[DECRYPTION MODULE]", 
        font=("Consolas", 11, "bold"),
        bg=BG_COLOR,
        fg="#00cc00").pack(pady=(10,5))

tk.Label(root, 
        text="ENTER CRYPTO KEY:", 
        font=("Consolas", 10),
        bg=BG_COLOR,
        fg=FG_COLOR).pack()

entry_key = tk.Entry(root, width=90, **entry_style)
entry_key.pack(pady=5)

tk.Label(root, 
        text="ENTER CIPHERTEXT:", 
        font=("Consolas", 10),
        bg=BG_COLOR,
        fg=FG_COLOR).pack()

entry_decrypt = tk.Entry(root, width=90, **entry_style)
entry_decrypt.pack(pady=5)

decrypt_btn = tk.Button(root, 
                       text="⏣ INITIATE DECRYPTION ⏣", 
                       command=decrypt_text,
                       **button_style)
decrypt_btn.pack(pady=10)

output_decrypt = tk.Text(root, 
                        height=6, 
                        width=90, 
                        wrap='word', 
                        font=("Consolas", 10),
                        bg=TEXT_BG,
                        fg=FG_COLOR,
                        borderwidth=2,
                        relief=tk.SUNKEN)
output_decrypt.tag_config("success", foreground="#00ff00")
output_decrypt.tag_config("error", foreground=WARNING_COLOR)
output_decrypt.pack()
output_decrypt.config(state='disabled')

footer = tk.Label(root, 
                 text="FOR AUTHORIZED PERSONNEL ONLY // SANSKAR DEBNATH",
                 font=("Consolas", 10),
                 bg=BG_COLOR,
                 fg="#007700")
footer.pack(pady=10)

root.mainloop()