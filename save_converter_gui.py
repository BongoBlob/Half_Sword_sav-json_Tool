import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import os
import sys
import random

# --- Resource path helper for PyInstaller bundles ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Main App Setup ---
root = tk.Tk()
root.title("Half Sword Sav-Json tool")
root.geometry("400x400")
root.resizable(True, True)

# Set custom icon for ALL windows (root and Toplevels)
icon_path = resource_path("myicon.ico")
root.iconbitmap(default=icon_path)

# Use modern themed style
style = ttk.Style(root)
style.theme_use('xpnative' if 'xpnative' in style.theme_names() else 'vista' if 'vista' in style.theme_names() else 'default')

# Variables for progress bar and options
use_progress = tk.BooleanVar(value=True)
progress_duration = tk.IntVar(value=1000)

# --- Progress bar after file select ---
def show_progress(callback_after=None):
    if not use_progress.get():
        if callback_after:
            callback_after()
        return

    prog_win = tk.Toplevel(root)
    prog_win.title("Finishing Up...")
    prog_win.geometry("300x100")
    prog_win.iconbitmap(default=icon_path)
    # Position prog_win near root
    prog_win.geometry(f"+{root.winfo_x()+50}+{root.winfo_y()+50}")
    prog = ttk.Progressbar(prog_win, orient='horizontal', length=250, mode='determinate')
    prog.pack(pady=20)
    prog_win.grab_set()

    steps = 20
    delay = progress_duration.get() // steps

    def step(i=0):
        if i <= steps: 
            prog['value'] = (i / steps) * 100 
            root.after(delay, step, i + 1) 
        else: 
            prog_win.destroy() 
            if callback_after: 
                callback_after() 

    step() 

# --- uesave executable path --- 
def get_uesave_path(): 
    return resource_path("uesave.exe") 

# --- Convert SAV to JSON --- 
def convert_sav_to_json(): 
    sav_path = filedialog.askopenfilename(title="Select .sav file", filetypes=[("Save Files", "*.sav")]) 
    if not sav_path: 
        return 
    json_path = os.path.splitext(sav_path)[0] + ".json" 
    try: 
        # Show progress bar immediately after file select 
        def after_progress(): 
            messagebox.showinfo("Success", f"Converted to {json_path}") 
        subprocess.run([get_uesave_path(), "to-json", "-i", sav_path, "-o", json_path], check=True) 
        show_progress(after_progress) 
    except Exception as e: 
        messagebox.showerror("Error", f"Conversion failed:\n{e}") 

# --- Convert JSON to SAV --- 
def convert_json_to_sav(): 
    json_path = filedialog.askopenfilename(title="Select .json file", filetypes=[("JSON Files", "*.json")]) 
    if not json_path: 
        return 
    sav_path = os.path.splitext(json_path)[0] + ".sav" 
    try: 
        def after_progress(): 
            messagebox.showinfo("Success", f"Converted to {sav_path}") 
        subprocess.run([get_uesave_path(), "from-json", "-i", json_path, "-o", sav_path], check=True) 
        show_progress(after_progress) 
    except Exception as e: 
        messagebox.showerror("Error", f"Conversion failed:\n{e}") 

# --- Options window --- 
def build_options_window(): 
    opt_win = tk.Toplevel(root) 
    opt_win.title("Options") 
    opt_win.iconbitmap(default=icon_path) 
    opt_win.geometry("300x120") 
    opt_win.resizable(False, False) 
    # Position near root 
    opt_win.geometry(f"+{root.winfo_x()+30}+{root.winfo_y()+30}") 

    ttk.Checkbutton(opt_win, text="Enable Loading Animation", variable=use_progress).pack(anchor="w", padx=10, pady=10) 

    frame = ttk.Frame(opt_win) 
    frame.pack(pady=5, padx=10, fill="x") 

    ttk.Label(frame, text="Loading Duration (ms):").pack(side="left") 
    ttk.Entry(frame, textvariable=progress_duration, width=8).pack(side="left", padx=(5, 0)) 

# --- Credits window with embedded game --- 
class ZombieGame(tk.Canvas): 
    def __init__(self, parent, width=300, height=300): 
        super().__init__(parent, width=width, height=height, bg='green', highlightthickness=0) 
        self.width = width 
        self.height = height 

        # Player attributes 
        self.player_size = 20 
        self.player_color = 'blue' 
        self.player_x = width // 2 
        self.player_y = height // 2 
        self.player_speed = 5 
        self.health = 5 

        # Controls state 
        self.keys_pressed = set() 

        # Zombies list: dict with keys: x, y, hits_left 
        self.zombies = [] 
        self.zombie_base_hits = 1  # base hits zombies have, increases over respawns

        # Projectiles list: dict with keys: x, y, dx, dy 
        self.projectiles = [] 

        # Score 
        self.score = 0 

        # Blood effects: list of (x, y, radius, lifetime) 
        self.bloods = [] 

        self.game_over = False 

        # Bind keys 
        self.focus_set() 
        self.bind("<KeyPress>", self.on_key_press) 
        self.bind("<KeyRelease>", self.on_key_release) 
        self.bind("<Button-1>", self.shoot) 

        self.spawn_zombies(6) 

        # Set up respawn every 20 seconds
        self.after(20000, self.respawn_zombies)

        self.after(30, self.game_loop) 

    def spawn_zombies(self, count): 
        self.zombies = [] 
        for _ in range(count): 
            x = random.randint(10, self.width - 30) 
            y = random.randint(10, self.height - 30) 
            hits = self.zombie_base_hits  # Use current base hits value 
            self.zombies.append({'x': x, 'y': y, 'hits_left': hits}) 

    def respawn_zombies(self):
        if self.game_over:
            # Don't respawn while dead
            self.after(1, self.respawn_zombies)
            return
        # Increase difficulty by adding 1 to base hits
        self.zombie_base_hits += 1
        # Respawn zombies with increased health
        self.spawn_zombies(6)
        # Schedule next respawn
        self.after(1, self.respawn_zombies)

    def on_key_press(self, event): 
        self.keys_pressed.add(event.keysym.lower()) 

    def on_key_release(self, event): 
        self.keys_pressed.discard(event.keysym.lower()) 

    def shoot(self, event): 
        if self.game_over: 
            return 
        # Projectile speed and direction towards mouse click 
        px, py = self.player_x + self.player_size // 2, self.player_y + self.player_size // 2 
        dx = event.x - px 
        dy = event.y - py 
        dist = (dx ** 2 + dy ** 2) ** 0.5 
        if dist == 0: 
            return 
        dx /= dist 
        dy /= dist 
        speed = 15 
        self.projectiles.append({'x': px, 'y': py, 'dx': dx * speed, 'dy': dy * speed}) 

    def update_player(self): 
        if self.game_over: 
            return 
        dx = dy = 0 
        if 'w' in self.keys_pressed: 
            dy -= self.player_speed 
        if 's' in self.keys_pressed: 
            dy += self.player_speed 
        if 'a' in self.keys_pressed: 
            dx -= self.player_speed 
        if 'd' in self.keys_pressed: 
            dx += self.player_speed 

        # Move player, keep inside canvas 
        self.player_x = max(0, min(self.width - self.player_size, self.player_x + dx)) 
        self.player_y = max(0, min(self.height - self.player_size, self.player_y + dy)) 

    def update_projectiles(self): 
        new_proj = [] 
        for p in self.projectiles: 
            p['x'] += p['dx'] 
            p['y'] += p['dy'] 
            # Remove if out of bounds 
            if 0 <= p['x'] <= self.width and 0 <= p['y'] <= self.height: 
                new_proj.append(p) 
        self.projectiles = new_proj 

    def update_zombies(self): 
        if self.game_over: 
            return 
        for z in self.zombies: 
            # Move zombie towards player slowly 
            zx, zy = z['x'], z['y'] 
            px, py = self.player_x, self.player_y 
            dx = px - zx 
            dy = py - zy 
            dist = (dx ** 2 + dy ** 2) ** 0.5 
            if dist == 0: 
                continue 
            dx /= dist 
            dy /= dist 
            speed = 1.2 
            z['x'] += dx * speed 
            z['y'] += dy * speed 

            # Check collision with player 
            if (abs(z['x'] - px) < 20) and (abs(z['y'] - py) < 20): 
                self.health -= 1 
                # Knockback zombie a bit on hit 
                z['x'] -= dx * 20 
                z['y'] -= dy * 20 
                if self.health <= 0: 
                    self.game_over = True 

    def check_projectile_hits(self): 
        new_zombies = [] 
        for z in self.zombies: 
            zombie_hit = False 
            for p in self.projectiles: 
                # Simple collision circle check (radius 10) 
                if abs(p['x'] - z['x']) < 15 and abs(p['y'] - z['y']) < 15: 
                    z['hits_left'] -= 1 
                    # Add blood effect 
                    self.bloods.append({'x': z['x'], 'y': z['y'], 'radius': 10, 'life': 10}) 
                    # Remove projectile 
                    self.projectiles.remove(p) 
                    if z['hits_left'] <= 0: 
                        self.score += 1 
                        zombie_hit = True 
                    break 
            if not zombie_hit: 
                new_zombies.append(z) 
        self.zombies = new_zombies 

    def update_blood(self): 
        new_bloods = [] 
        for b in self.bloods: 
            b['life'] -= 1 
            b['radius'] = max(0, b['radius'] - 1) 
            if b['life'] > 0: 
                new_bloods.append(b) 
        self.bloods = new_bloods 

    def restart_game(self): 
        self.score = 0 
        self.health = 5 
        self.player_x = self.width // 2 
        self.player_y = self.height // 2 
        self.projectiles.clear() 
        self.bloods.clear() 
        self.zombie_base_hits = 1  # reset zombie hits on restart
        self.spawn_zombies(6) 
        self.game_over = False 

    def draw(self): 
        self.delete("all") 
        # Floor is already green bg 

        # Draw blood splatters 
        for b in self.bloods: 
            alpha = int(255 * (b['life'] / 10)) 
            color = "#%02x0000" % (alpha if alpha > 0 else 0) 
            self.create_oval( 
                b['x'] - b['radius'], b['y'] - b['radius'], 
                b['x'] + b['radius'], b['y'] + b['radius'], 
                fill='red', outline='' 
            ) 

        # Draw player 
        self.create_rectangle(self.player_x, self.player_y, 
                              self.player_x + self.player_size, 
                              self.player_y + self.player_size, 
                              fill=self.player_color) 

        # Draw zombies 
        for z in self.zombies: 
            color = 'red' 
            self.create_rectangle(z['x'], z['y'], 
                                  z['x'] + 20, z['y'] + 20, 
                                  fill=color) 

        # Draw projectiles 
        for p in self.projectiles: 
            self.create_oval(p['x'] - 5, p['y'] - 5, 
                             p['x'] + 5, p['y'] + 5, 
                             fill='black') 

        # Draw score and health top right 
        self.create_text(self.width - 10, 10, anchor='ne',  
                         text=f"Score: {self.score}", fill='white', font=("Arial", 12, "bold")) 
        self.create_text(self.width - 10, 30, anchor='ne',  
                         text=f"Health: {self.health}", fill='white', font=("Arial", 12, "bold")) 

        # Game over text 
        if self.game_over: 
            self.create_text(self.width // 2, self.height // 2, 
                             text="You Died! Restarting...", fill="yellow", 
                             font=("Arial", 16, "bold")) 

    def game_loop(self): 
        if self.game_over: 
            self.draw() 
            # Wait a sec then restart 
            self.after(1500, self.restart_game) 
        else: 
            self.update_player() 
            self.update_projectiles() 
            self.update_zombies() 
            self.check_projectile_hits() 
            self.update_blood() 
            self.draw() 
        self.after(30, self.game_loop) 

def show_credits(): 
    credits_win = tk.Toplevel(root) 
    credits_win.title("Credits & Game") 
    credits_win.geometry("400x450") 
    credits_win.iconbitmap(default=icon_path) 
    credits_win.resizable(False, False) 
    credits_win.geometry(f"+{root.winfo_x()+30}+{root.winfo_y()+30}") 

    frame = ttk.Frame(credits_win) 
    frame.pack(padx=10, pady=5) 

    # Credits label + image 
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

    tk.Label(frame, text="creator: bongoblob. And thanks @sable ", font=("Comic Sans MS", 10, "bold")).pack(side="left") 

    # Add separator 
    ttk.Separator(credits_win, orient='horizontal').pack(fill='x', pady=5) 

    # Add the game canvas 
    game_canvas = ZombieGame(credits_win) 
    game_canvas.pack(padx=10, pady=10) 

# --- Menus --- 
menubar = tk.Menu(root) 

file_menu = tk.Menu(menubar, tearoff=0) 
new_menu = tk.Menu(file_menu, tearoff=0) 
new_menu.add_command(label="Create Blank SAV", command=lambda: None) 
new_menu.add_command(label="Create Blank JSON", command=lambda: None) 
file_menu.add_cascade(label="New", menu=new_menu) 
file_menu.add_separator() 
file_menu.add_command(label="Exit", command=root.quit) 
menubar.add_cascade(label="File", menu=file_menu) 

options_menu = tk.Menu(menubar, tearoff=0) 
options_menu.add_command(label="Settings...", command=build_options_window) 
menubar.add_cascade(label="Options", menu=options_menu) 

credits_menu = tk.Menu(menubar, tearoff=0) 
credits_menu.add_command(label="View Credits & Play Game", command=show_credits) 
menubar.add_cascade(label="Credits", menu=credits_menu) 

root.config(menu=menubar) 

# --- Main UI --- 
ttk.Label(root, text="SAV/JSON Converter", font=("Comic Sans MS", 18, "bold")).pack(pady=15) 
ttk.Button(root, text="Convert SAV → JSON", command=convert_sav_to_json).pack(pady=10) 
ttk.Button(root, text="Convert JSON → SAV", command=convert_json_to_sav).pack(pady=10) 

# Load and show hs.png at the bottom center, resized to 300px width max 
try: 
    hs_img_path = resource_path("hs.png") 
    hs_img_raw = Image.open(hs_img_path) 

    base_width = 300 
    w_percent = (base_width / float(hs_img_raw.size[0])) 
    h_size = int((float(hs_img_raw.size[1]) * float(w_percent))) 
    hs_img_resized = hs_img_raw.resize((base_width, h_size), Image.Resampling.LANCZOS) 

    hs_photo = ImageTk.PhotoImage(hs_img_resized)

    bottom_container = tk.Frame(root)
    bottom_container.pack(side="bottom", fill="x")

    # Padding only below image
    hs_label = tk.Label(bottom_container, image=hs_photo)
    hs_label.pack(pady=(0, 6))  # padding only below image, no padding on top or sides
    hs_label.image = hs_photo  # keep reference

    # Black bar below image, no padding
    bottom_bar = tk.Frame(bottom_container, bg="black")
    bottom_bar.pack(fill="x")

    credit_label = tk.Label(
        bottom_bar,
        text="Created by @bongoblob",
        fg="white",
        bg="black",
        font=("Comic Sans MS", 10)
    )
    credit_label.pack(pady=4)
except Exception as e: 
    print(f"Failed to load hs.png image: {e}") 

root.mainloop()
