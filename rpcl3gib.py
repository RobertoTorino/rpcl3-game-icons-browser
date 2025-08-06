import io
import os
import sqlite3
import sys
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageDraw, ImageFont, ImageTk

if getattr(sys, 'frozen', False):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

DB_FILE = os.path.join(base_path, 'games.db')

print(f"Using DB file at: {DB_FILE}")
print(f"DB exists? {os.path.exists(DB_FILE)}")

def create_placeholder_image():
    img = Image.new('RGBA', (128, 85), (60, 60, 60, 255))  # reduced height
    draw = ImageDraw.Draw(img)
    text = "No Image"
    try:
        font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((128 - w) / 2, (85 - h) / 2), text, fill="white", font=font)
    except Exception:
        draw.text((32, 32), text, fill="white")
    return ImageTk.PhotoImage(img)


def save_icon(blob, game_id):
    if blob is None:
        messagebox.showinfo("No Image", "No icon available to save for this game.")
        return
    filepath = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Images", "*.png")],
        initialfile=f"{game_id}.png"
    )
    if not filepath:
        return
    try:
        img = Image.open(io.BytesIO(blob))
        img.save(filepath)
        messagebox.showinfo("Saved", f"Icon saved as {filepath}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save icon: {e}")


class GameIconBrowser(tk.Tk):
    def __init__(self):
        super().__init__()
        self.resizable(False, False)
        year = datetime.now().year
        title = f"RPCL3 Game Icon Browser - {chr(169)} {year} - Philip"
        self.title(title)
        self.games = None
        self.conn = sqlite3.connect(DB_FILE)
        self.cursor = self.conn.cursor()
        self.minsize(1000, 700)

        # Dark theme colors
        self.bg_color = "#222222"
        self.fg_color = "#dddddd"
        self.btn_bg = "#444444"
        self.btn_fg = "#eeeeee"
        self.entry_bg = "#333333"
        self.entry_fg = "#ffffff"

        self.configure(bg=self.bg_color)

        # Title label on top, bigger font
        title_label = tk.Label(self, text="Search on game id or game title",
                               font=("Arial", 16, "bold"), bg=self.bg_color, fg=self.fg_color)
        title_label.pack(padx=10, pady=(10, 1), anchor="w")

        # Info label: total or found games count
        self.info_label = tk.Label(self, text="", font=("Arial", 12), bg=self.bg_color, fg=self.fg_color)
        self.info_label.pack(padx=10, pady=(0, 10), anchor="w")

        # Frame for search field and button side by side
        search_frame = tk.Frame(self, bg=self.bg_color)
        search_frame.pack(fill='x', padx=10, pady=(0, 10))

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.entry_fg,
                                font=("Arial", 12))
        search_entry.pack(side='left', fill='x', expand=True, padx=(0, 8), ipady=5)
        search_entry.bind("<Return>", lambda e: self.search())

        search_btn = tk.Button(search_frame, text="Search", command=self.search,
                               bg=self.btn_bg, fg=self.btn_fg, activebackground="#555555", activeforeground="#ffffff",
                               font=("Arial", 12, "bold"), width=12, height=1)
        search_btn.pack(side='right', pady=1, ipady=1)

        clear_btn = tk.Button(search_frame, text="Clear", command=self.clear_search,
                              bg=self.btn_bg, fg=self.btn_fg, activebackground="#555555", activeforeground="#ffffff",
                              font=("Arial", 12), width=8, height=1)
        clear_btn.pack(side='right', padx=(0, 8), pady=1, ipady=1)

        # Canvas for scrollable icons grid
        self.canvas = tk.Canvas(self, bg=self.bg_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        style = ttk.Style()
        style.theme_use('default')
        style.configure("Vertical.TScrollbar", gripcount=0,
                        background=self.btn_bg, darkcolor=self.btn_bg, lightcolor=self.btn_bg,
                        troughcolor=self.bg_color, bordercolor=self.bg_color, arrowcolor=self.btn_fg,
                        width=10)
        self.scrollbar.configure(style="Vertical.TScrollbar")
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_color)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.tk_images = []

        # Filter Frame
        filter_frame = ttk.Frame(search_frame)
        filter_frame.pack(side="left", padx=10)

        # ArcadeGame Checkbox
        self.arcade_var = tk.BooleanVar()
        arcade_check = ttk.Checkbutton(filter_frame, text="Arcade", variable=self.arcade_var,
                                       command=self.apply_filters)
        arcade_check.pack(side="left", padx=5)

        # PSN Checkbox
        self.psn_var = tk.BooleanVar()
        psn_check = ttk.Checkbutton(filter_frame, text="PSN", variable=self.psn_var, command=self.apply_filters)
        psn_check.pack(side="left", padx=5)

        # Region Dropdown
        self.region_var = tk.StringVar()
        self.region_var.set("All")  # Default value
        region_options = ["All", "US", "EU", "JP", "AS", "KO", "CN", "UN"]
        region_menu = ttk.OptionMenu(filter_frame, self.region_var, "All", *region_options,
                                     command=lambda _: self.apply_filters())
        region_menu.pack(side="left", padx=5, pady=3)

    def clear_search(self):
        self.search_var.set("")
        self.arcade_var.set(False)
        self.psn_var.set(False)
        self.region_var.set("All")
        self.apply_filters()

    def update_info_label(self, total=None):
        if total is None:
            self.cursor.execute("SELECT COUNT(*) FROM games")
            total = self.cursor.fetchone()[0]
        self.info_label.config(text=f"Total games found: {total}")

    def search(self):
        query = self.search_var.get().strip()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT GameId, GameTitle, IconBlob
            FROM games
            WHERE GameId LIKE ? OR GameTitle LIKE ?
            ORDER BY GameTitle
        """, (f'%{query}%', f'%{query}%'))
        rows = cursor.fetchall()
        self.display_results(rows)
        self.update_info_label(len(rows))
        return rows

    def display_results(self, rows):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        count = len(rows)
        if count == 0:
            self.info_label.config(text="No games found.")
            return

        self.info_label.config(text=f"Games found: {count}")
        self.tk_images.clear()

        cols = 6
        for idx, (game_id, title, icon_blob) in enumerate(rows):
            frame = tk.Frame(self.scrollable_frame, bd=1, relief="groove",
                             width=140, height=230, bg=self.bg_color, highlightbackground="#444444",
                             highlightcolor="#444444", highlightthickness=1)
            frame.grid(row=idx // cols, column=idx % cols, padx=8, pady=8)
            frame.grid_propagate(False)

            if icon_blob:
                try:
                    img = Image.open(io.BytesIO(icon_blob))
                    img.thumbnail((128, 85))
                    tk_img = ImageTk.PhotoImage(img)
                except Exception:
                    tk_img = create_placeholder_image()
            else:
                tk_img = create_placeholder_image()
            self.tk_images.append(tk_img)

            tk.Label(frame, image=tk_img, width=128, height=85, bg=self.bg_color).pack()
            tk.Label(frame, text=game_id, font=("Arial", 10, "bold"),
                     bg=self.bg_color, fg=self.fg_color).pack()
            tk.Label(frame, text=title, font=("Arial", 9), wraplength=130,
                     justify="center", height=3, bg=self.bg_color, fg=self.fg_color).pack()
            tk.Button(frame, text="Save Icon",
                      command=lambda b=icon_blob, g=game_id: save_icon(b, g),
                      bg=self.btn_bg, fg=self.btn_fg, activebackground="#555555", activeforeground="#ffffff").pack(
                pady=5)

    def apply_filters(self):
        query = "SELECT GameId, GameTitle, IconBlob FROM games WHERE 1==1"
        params = []

        # Apply search filter
        search = self.search_var.get().strip()
        if search:
            query += " AND (GameId LIKE ? OR GameTitle LIKE ?)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term])

        # Apply ArcadeGame filter
        if self.arcade_var.get():
            query += " AND ArcadeGame = 1"

        # Apply PSN filter
        if self.psn_var.get():
            query += " AND PSN = 1"

        # Apply Region filter
        region = self.region_var.get()
        if region != "All":
            query += " AND Region = ?"
            params.append(region)

        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        self.games = rows  # Only fetch once

        self.display_results(rows)
        self.update_info_label(len(rows))

    def refresh_icons(self, rows):
        self.display_results(rows)
        self.update_info_label(len(rows))


if __name__ == "__main__":
    app = GameIconBrowser()
    app.mainloop()
