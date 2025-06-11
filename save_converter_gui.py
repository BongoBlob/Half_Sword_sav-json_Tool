import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

root = tk.Tk()
root.title("Sav converter :-)")
root.geometry("300x200")
root.resizable(True, True)

style = ttk.Style(root)
style.theme_use('xpnative' if 'xpnative' in style.theme_names() else 'vista' if 'vista' in style.theme_names() else 'default')

def show_progress_and_run(callback):
    prog_win = tk.Toplevel(root)
    prog_win.title("Loading")
    prog_win.geometry("300x100")
    prog = ttk.Progressbar(prog_win, orient='horizontal', length=250, mode='determinate')
    prog.pack(pady=20)
    prog_win.grab_set()
    steps = 20
    def step(i=0):
        if i <= steps:
            prog['value'] = (i / steps) * 100
            root.after(50, step, i + 1)
        else:
            prog_win.destroy()
            callback()
    step()

def get_uesave_path():
    return resource_path("uesave.exe")

def convert_sav_to_json_real():
    sav_path = filedialog.askopenfilename(title="Select .sav file", filetypes=[("Save Files", "*.sav")])
    if not sav_path:
        return
    json_path = os.path.splitext(sav_path)[0] + ".json"
    try:
        subprocess.run([get_uesave_path(), "to-json", "-i", sav_path, "-o", json_path], check=True)
        messagebox.showinfo("Success", f"Converted to {json_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Conversion failed:\n{e}")

def convert_json_to_sav_real():
    json_path = filedialog.askopenfilename(title="Select .json file", filetypes=[("JSON Files", "*.json")])
    if not json_path:
        return
    sav_path = os.path.splitext(json_path)[0] + ".sav"
    try:
        subprocess.run([get_uesave_path(), "from-json", "-i", json_path, "-o", sav_path], check=True)
        messagebox.showinfo("Success", f"Converted to {sav_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Conversion failed:\n{e}")

def convert_sav_to_json():
    show_progress_and_run(convert_sav_to_json_real)

def convert_json_to_sav():
    show_progress_and_run(convert_json_to_sav_real)

def show_credits():
    credits_win = tk.Toplevel(root)
    credits_win.title("Credits")
    credits_win.geometry("350x150")
    credits_win.resizable(True, True)

    frame = ttk.Frame(credits_win)
    frame.pack(padx=10, pady=10, fill='both', expand=True)

    try:
        image_path = resource_path("yellowfish.jpg")
        image = Image.open(image_path)
        image = image.resize((100, 100), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        label_img = tk.Label(frame, image=photo)
        label_img.image = photo
        label_img.pack(side="left", padx=(0, 10))
    except Exception as e:
        tk.Label(frame, text=f"[Image error: {e}]", fg="red").pack(side="left")

    tk.Label(frame, text="creator: bongoblob", font=("Comic Sans MS", 16, "bold")).pack(side="left")

# MENU
menubar = tk.Menu(root)

file_menu = tk.Menu(menubar, tearoff=0)
new_menu = tk.Menu(file_menu, tearoff=0)
new_menu.add_command(label="Create Blank SAV", command=lambda: None)
new_menu.add_command(label="Create Blank JSON", command=lambda: None)
file_menu.add_cascade(label="New", menu=new_menu)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=file_menu)

credits_menu = tk.Menu(menubar, tearoff=0)
credits_menu.add_command(label="View Credits", command=show_credits)
menubar.add_cascade(label="Credits", menu=credits_menu)

root.config(menu=menubar)

# MAIN GUI
ttk.Label(root, text="SAV/JSON Converter", font=("Segoe UI", 14, "bold")).pack(pady=15)
ttk.Button(root, text="Convert SAV → JSON", command=convert_sav_to_json).pack(pady=10)
ttk.Button(root, text="Convert JSON → SAV", command=convert_json_to_sav).pack(pady=10)

root.mainloop()
