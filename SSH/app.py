import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import paramiko
import posixpath
import os
import stat
from datetime import datetime

class SSHFileManager:
    def __init__(self, root):
        self.root = root
        self.root.title("SSH File Manager")
        self.root.geometry("1000x700")
        self.root.configure(bg="#121212")

        self.ssh = None
        self.sftp = None
        self.home_path = "/home/sanskar/shared_ssh_folder"
        self.current_path = self.home_path

        self.init_login_frame()

    def init_login_frame(self):
        self.login_frame = tk.Frame(self.root, bg="#121212")
        self.login_frame.pack(pady=120)

        style = {"fg": "#ffffff", "bg": "#121212", "font": ("Consolas", 12)}

        tk.Label(self.login_frame, text="Host:", **style).grid(row=0, column=0, sticky='e')
        tk.Label(self.login_frame, text="Username:", **style).grid(row=1, column=0, sticky='e')
        tk.Label(self.login_frame, text="Password:", **style).grid(row=2, column=0, sticky='e')

        self.entry_host = tk.Entry(self.login_frame, font=("Consolas", 12))
        self.entry_user = tk.Entry(self.login_frame, font=("Consolas", 12))
        self.entry_pass = tk.Entry(self.login_frame, show="*", font=("Consolas", 12))

        self.entry_host.grid(row=0, column=1, padx=10, pady=5)
        self.entry_user.grid(row=1, column=1, padx=10, pady=5)
        self.entry_pass.grid(row=2, column=1, padx=10, pady=5)

        tk.Button(self.login_frame, text="Connect", font=("Consolas", 12), command=self.connect_ssh).grid(row=3, column=0, columnspan=2, pady=15)

    def connect_ssh(self):
        host = self.entry_host.get()
        user = self.entry_user.get()
        passwd = self.entry_pass.get()

        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(hostname=host, username=user, password=passwd)
            self.sftp = self.ssh.open_sftp()
            try:
                self.sftp.stat(self.home_path)
            except IOError:
                self.sftp.mkdir(self.home_path)
            self.current_path = self.home_path
            self.show_file_browser()
        except Exception as e:
            messagebox.showerror("Login Failed", str(e))

    def show_file_browser(self):
        self.login_frame.destroy()
        self.browser_frame = tk.Frame(self.root, bg="#121212")
        self.browser_frame.pack(fill='both', expand=True)

        self.path_label = tk.Label(self.browser_frame, text=f"Location: {self.current_path}", bg="#121212", fg="#00FFAA", font=("Consolas", 12, "bold"), padx=10, pady=10)
        self.path_label.pack(fill='x')

        self.tree = ttk.Treeview(self.browser_frame, columns=("name", "type", "size", "modified"), show="headings", selectmode="browse")
        self.tree.heading("name", text="Name", anchor='w')
        self.tree.heading("type", text="Type", anchor='w')
        self.tree.heading("size", text="Size", anchor='w')
        self.tree.heading("modified", text="Modified", anchor='w')
        self.tree.column("name", width=350, anchor='w')
        self.tree.column("type", width=80, anchor='w')
        self.tree.column("size", width=100, anchor='w')
        self.tree.column("modified", width=200, anchor='w')

        scrollbar = ttk.Scrollbar(self.browser_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.tree.bind('<Double-Button-1>', self.navigate)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Consolas", 11), rowheight=28, background="#1e1e1e", fieldbackground="#1e1e1e", foreground="#ffffff")
        style.configure("Treeview.Heading", font=("Consolas", 11, "bold"), background="#333", foreground="#00FFAA")

        btn_frame = tk.Frame(self.browser_frame, bg="#121212")
        btn_frame.pack(pady=10)

        buttons = [
            ("Upload Files", self.upload_files),
            ("Upload Folder", self.upload_folder),
            ("Download", self.download_file),
            ("Delete", self.delete_file),
            ("Refresh", self.refresh_file_list),
            ("New Folder", self.create_folder),
            ("Home", self.go_home)
        ]

        for i, (text, command) in enumerate(buttons):
            tk.Button(btn_frame, text=text, width=14, font=("Consolas", 10), command=command).grid(row=0, column=i, padx=5)

        self.refresh_file_list()

    def refresh_file_list(self):
        try:
            self.tree.delete(*self.tree.get_children())
            files = self.sftp.listdir_attr(self.current_path)
            self.path_label.config(text=f"Location: {self.current_path}")

            if self.current_path != self.home_path:
                self.tree.insert("", "end", values=("..", "DIR", "", ""))

            files.sort(key=lambda x: not stat.S_ISDIR(x.st_mode))

            for f in files:
                name = f.filename
                file_type = "DIR" if stat.S_ISDIR(f.st_mode) else "FILE"
                size = f"{round(f.st_size/1024, 1)} KB" if f.st_size > 0 else "0 KB" if file_type == "FILE" else ""
                mod_time = datetime.fromtimestamp(f.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                self.tree.insert("", "end", values=(name, file_type, size, mod_time))
        except Exception as e:
            messagebox.showerror("Error", f"Could not list directory: {str(e)}")

    def navigate(self, event):
        selection = self.tree.item(self.tree.focus())
        values = selection.get("values")
        if not values:
            return
        name = values[0]
        if name == "..":
            new_path = posixpath.dirname(self.current_path)
            if new_path.startswith(posixpath.dirname(self.home_path)):
                self.current_path = new_path
        else:
            new_path = posixpath.join(self.current_path, name)
            try:
                if stat.S_ISDIR(self.sftp.stat(new_path).st_mode):
                    self.current_path = new_path
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return
        self.refresh_file_list()

    def upload_files(self):
        local_paths = filedialog.askopenfilenames()
        if local_paths:
            for local_path in local_paths:
                try:
                    remote_path = posixpath.join(self.current_path, os.path.basename(local_path))
                    self.sftp.put(local_path, remote_path)
                except Exception as e:
                    messagebox.showerror("Upload Failed", f"{os.path.basename(local_path)}: {str(e)}")
            self.refresh_file_list()
            messagebox.showinfo("Upload Complete", f"{len(local_paths)} file(s) uploaded.")

    def upload_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            try:
                self.upload_directory_recursive(folder_path, self.current_path)
                self.refresh_file_list()
                messagebox.showinfo("Success", f"Folder '{os.path.basename(folder_path)}' uploaded.")
            except Exception as e:
                messagebox.showerror("Upload Failed", str(e))

    def upload_directory_recursive(self, local_dir, remote_dir):
        folder_name = os.path.basename(local_dir)
        new_remote_path = posixpath.join(remote_dir, folder_name)
        try:
            self.sftp.mkdir(new_remote_path)
        except IOError:
            pass  # If folder already exists

        for item in os.listdir(local_dir):
            local_path = os.path.join(local_dir, item)
            remote_path = posixpath.join(new_remote_path, item)
            if os.path.isdir(local_path):
                self.upload_directory_recursive(local_path, new_remote_path)
            else:
                self.sftp.put(local_path, remote_path)

    def download_file(self):
        selection = self.tree.item(self.tree.focus())
        values = selection.get("values")
        if not values or values[1] != "FILE":
            return
        name = values[0]
        remote_path = posixpath.join(self.current_path, name)
        local_path = filedialog.asksaveasfilename(initialfile=name)
        if local_path:
            try:
                self.sftp.get(remote_path, local_path)
                messagebox.showinfo("Success", f"Downloaded to {local_path}")
            except Exception as e:
                messagebox.showerror("Download Failed", str(e))

    def delete_file(self):
        selection = self.tree.item(self.tree.focus())
        values = selection.get("values")
        if not values or values[0] == "..":
            return
        name = values[0]
        remote_path = posixpath.join(self.current_path, name)
        try:
            if stat.S_ISDIR(self.sftp.stat(remote_path).st_mode):
                if len(self.sftp.listdir(remote_path)) > 0:
                    if not messagebox.askyesno("Confirm", "Directory not empty! Delete anyway?"):
                        return
                self.sftp.rmdir(remote_path)
            else:
                self.sftp.remove(remote_path)
            self.refresh_file_list()
            messagebox.showinfo("Deleted", f"Deleted {name}")
        except Exception as e:
            messagebox.showerror("Delete Failed", str(e))

    def create_folder(self):
        folder_name = simpledialog.askstring("Create Folder", "Enter folder name:")
        if folder_name:
            new_dir = posixpath.join(self.current_path, folder_name)
            try:
                self.sftp.mkdir(new_dir)
                self.refresh_file_list()
                messagebox.showinfo("Folder Created", f"Created folder: {folder_name}")
            except Exception as e:
                messagebox.showerror("Creation Failed", str(e))

    def go_home(self):
        self.current_path = self.home_path
        self.refresh_file_list()

if __name__ == '__main__':
    root = tk.Tk()
    app = SSHFileManager(root)
    root.mainloop()
