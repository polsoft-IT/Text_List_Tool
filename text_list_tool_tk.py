"""
Text List Tool / Lista tekstów - polsoft.ITS
Tkinter app: paste text, 15 editable list items, per-item copy button.
EN/PL language switcher, light/dark (Catppuccin Mocha) theme switcher.

Author: Sebastian Januchowski / polsoft.ITS Group
"""

import json
import os
import sys
import tkinter as tk

NUM_ITEMS = 15

# --- Themes -----------------------------------------------------------
# "dark" = Catppuccin Mocha (default), "light" = Visual Studio style
THEMES = {
    "dark": {
        "bg": "#1e1e2e",          # base
        "fg": "#cdd6f4",          # text
        "entry_bg": "#181825",    # mantle
        "entry_border": "#45475a",  # surface1
        "accent": "#89b4fa",      # blue
        "accent_fg": "#1e1e2e",
        "accent_dark": "#74a8f5",
        "success": "#a6e3a1",     # green
        "muted": "#a6adc8",       # subtext0
        "btn_neutral": "#313244",  # surface0
        "btn_neutral_hover": "#45475a",
        "danger": "#f38ba8",      # red
    },
    "light": {
        "bg": "#f3f3f3",
        "fg": "#1e1e1e",
        "entry_bg": "#ffffff",
        "entry_border": "#c8c8c8",
        "accent": "#0078d4",
        "accent_fg": "#ffffff",
        "accent_dark": "#005a9e",
        "success": "#107c10",
        "muted": "#6e6e6e",
        "btn_neutral": "#e1e1e1",
        "btn_neutral_hover": "#cfcfcf",
        "danger": "#c42b1c",
    },
}


def get_app_dir():
    """Return the folder next to the script, or next to the .exe when frozen (PyInstaller)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def resource_path(relative_path):
    """Return path to a bundled resource (icon, etc.), working both in dev
    and inside a PyInstaller onefile .exe (where files are unpacked to _MEIPASS)."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


DATA_PATH = os.path.join(get_app_dir(), "text_list_data.json")
ICON_ICO_PATH = resource_path("icon.ico")
ICON_PNG_PATH = resource_path("icon.png")

ABOUT_INFO = {
    "author": "Sebastian Januchowski",
    "group": "polsoft.ITS\u2122 Group",
    "github": "https://github.com/polsoft-seb07uk",
    "email": "polsoft.its@mail.com",
    "license": "Freeware",
}

STRINGS = {
    "en": {
        "window_title": "Text List Tool - polsoft.ITS",
        "title": "Text List (15 items)",
        "split_btn": "Split into\nlist ⬇",
        "clear_btn": "Clear all",
        "copy_all_btn": "Copy all",
        "copied_all_btn": "Copied all!",
        "copy_btn": "Copy",
        "copied_btn": "Copied!",
        "lang_btn": "PL",
        "theme_btn": "☀",
        "theme_tip_dark": "Switch to light theme",
        "theme_tip_light": "Switch to dark theme",
        "ontop_on": "📌 On top",
        "ontop_off": "📌 Normal",
        "compact_btn": "🗕 Compact",
        "compact_hint": "Double-click icon to restore",
        "about_btn": "ℹ About",
        "about_title": "About",
        "status_filled": "{n}/{total} filled",
        "status_saved": "Saved ✓",
        "menu_cut": "Cut",
        "menu_copy": "Copy",
        "menu_paste": "Paste",
        "menu_selectall": "Select all",
        "menu_clear": "Clear",
        "row_clear_tip": "Clear this item",
    },
    "pl": {
        "window_title": "Lista tekstów - polsoft.ITS",
        "title": "Lista tekstów (15 pozycji)",
        "split_btn": "Podziel\nna listę ⬇",
        "clear_btn": "Wyczyść wszystko",
        "copy_all_btn": "Kopiuj wszystko",
        "copied_all_btn": "Skopiowano!",
        "copy_btn": "Kopiuj",
        "copied_btn": "Skopiowano!",
        "lang_btn": "EN",
        "theme_btn": "☀",
        "theme_tip_dark": "Przełącz na jasny motyw",
        "theme_tip_light": "Przełącz na ciemny motyw",
        "ontop_on": "📌 Na wierzchu",
        "ontop_off": "📌 Normalnie",
        "compact_btn": "🗕 Kompakt",
        "compact_hint": "Kliknij 2x aby przywrócić",
        "about_btn": "ℹ O programie",
        "about_title": "O programie",
        "status_filled": "{n}/{total} wypełnionych",
        "status_saved": "Zapisano ✓",
        "menu_cut": "Wytnij",
        "menu_copy": "Kopiuj",
        "menu_paste": "Wklej",
        "menu_selectall": "Zaznacz wszystko",
        "menu_clear": "Wyczyść",
        "row_clear_tip": "Wyczyść tę pozycję",
    },
}


class TextListApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang = "en"        # English as default language
        self.theme_name = "dark"  # Catppuccin Mocha as default theme
        self.always_on_top = False
        self.compact_window = None
        self.resizable(False, False)

        self.entries = []
        self.copy_buttons = []
        self.row_clear_buttons = []
        self.row_widgets = []      # (row_frame, num_label) pairs, for theme repaint
        self._save_after_id = None
        self._status_after_id = None

        # Load persisted settings (lang/theme/always_on_top) before building UI
        self._load_settings()

        self.configure(bg=self.colors["bg"])
        self._build_ui()
        self._apply_language()
        self._apply_theme()
        self._set_window_icon()
        self.load_data()
        self._update_status()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Auto-size window to fit content exactly (no cutting, no extra space)
        self.update_idletasks()
        req_w = self.winfo_reqwidth()
        req_h = self.winfo_reqheight()
        self.geometry(f"{req_w}x{req_h}")
        self.minsize(req_w, req_h)

    @property
    def colors(self):
        return THEMES[self.theme_name]

    def t(self, key):
        return STRINGS[self.lang][key]

    # ------------------------------------------------------------------
    # Vector logo (mirrors icon.ico artwork) - drawn on a Canvas so it
    # stays crisp at any size and re-themes instantly with the app.
    # ------------------------------------------------------------------
    @staticmethod
    def _rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)

    def _draw_logo(self, canvas, size):
        c = self.colors
        s = size / 64.0
        canvas.delete("all")
        canvas.configure(bg=c["bg"], highlightthickness=0, width=size, height=size)

        # Body (clipboard)
        self._rounded_rect(canvas, 10 * s, 6 * s, 54 * s, 58 * s, 6 * s,
                            fill=c["entry_bg"], outline=c["entry_border"], width=max(1, round(2 * s)))
        # Clip
        self._rounded_rect(canvas, 24 * s, 2 * s, 40 * s, 10 * s, 2 * s, fill=c["danger"], outline="")
        # Text lines
        lw = max(2, round(3 * s))
        canvas.create_line(20 * s, 24 * s, 44 * s, 24 * s, fill=c["fg"], width=lw, capstyle="round")
        canvas.create_line(20 * s, 34 * s, 44 * s, 34 * s, fill=c["fg"], width=lw, capstyle="round")
        canvas.create_line(20 * s, 44 * s, 34 * s, 44 * s, fill=c["muted"], width=lw, capstyle="round")
        # Paste arrow accent
        ax = 46 * s
        canvas.create_polygon(
            ax, 38 * s, ax, 46 * s, ax - 4 * s, 46 * s, ax + 2 * s, 54 * s,
            ax + 8 * s, 46 * s, ax + 4 * s, 46 * s, ax + 4 * s, 38 * s,
            fill=c["success"], outline="",
        )

    def _redraw_logos(self):
        for canvas, size in getattr(self, "_logo_canvases", []):
            if canvas.winfo_exists():
                self._draw_logo(canvas, size)

    def _register_logo(self, canvas, size):
        if not hasattr(self, "_logo_canvases"):
            self._logo_canvases = []
        self._logo_canvases.append((canvas, size))
        self._draw_logo(canvas, size)

    # ------------------------------------------------------------------
    # Hover feedback helpers (dynamic - always reads current theme colors)
    # ------------------------------------------------------------------
    def _hover_neutral(self, widget):
        widget.bind("<Enter>", lambda e: widget.configure(bg=self.colors["btn_neutral_hover"]))
        widget.bind("<Leave>", lambda e: widget.configure(bg=self.colors["btn_neutral"]))

    def _hover_accent(self, widget):
        widget.bind("<Enter>", lambda e: widget.configure(bg=self.colors["accent_dark"]))
        widget.bind("<Leave>", lambda e: widget.configure(bg=self.colors["accent"]))

    def _hover_danger_ghost(self, widget):
        def enter(e):
            c = self.colors
            widget.configure(bg=c["danger"], fg=c["bg"])

        def leave(e):
            c = self.colors
            widget.configure(bg=c["bg"], fg=c["danger"])

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def _hover_ontop(self, widget):
        def enter(e):
            c = self.colors
            widget.configure(bg=c["accent_dark"] if self.always_on_top else c["btn_neutral_hover"])

        def leave(e):
            c = self.colors
            widget.configure(bg=c["accent"] if self.always_on_top else c["btn_neutral"])

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def _set_window_icon(self):
        """Apply the app icon to the taskbar/title bar. Uses .ico on Windows
        (best quality, shows in taskbar/Alt+Tab); falls back to .png elsewhere
        or if the .ico can't be loaded for any reason."""
        try:
            if os.path.exists(ICON_ICO_PATH):
                self.iconbitmap(default=ICON_ICO_PATH)
                return
        except tk.TclError:
            pass
        try:
            if os.path.exists(ICON_PNG_PATH):
                self._icon_photo = tk.PhotoImage(file=ICON_PNG_PATH)
                self.iconphoto(True, self._icon_photo)
        except tk.TclError:
            pass

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        c = self.colors

        # --- Title row (centered, with vector logo) ---
        self.title_frame = tk.Frame(self, bg=c["bg"])
        self.title_frame.pack(fill="x", padx=15, pady=(15, 8))

        title_inner = tk.Frame(self.title_frame, bg=c["bg"])
        title_inner.pack(anchor="center")
        self.title_inner = title_inner

        self.logo_canvas = tk.Canvas(title_inner, width=34, height=34, bd=0, highlightthickness=0)
        self.logo_canvas.pack(side="left", padx=(0, 8))
        self._register_logo(self.logo_canvas, 34)

        self.title_label = tk.Label(
            title_inner, bg=c["bg"], fg=c["accent"], font=("Segoe UI", 14, "bold")
        )
        self.title_label.pack(side="left", anchor="center")

        # --- Buttons row ---
        self.top_bar = tk.Frame(self, bg=c["bg"])
        self.top_bar.pack(fill="x", padx=15, pady=(0, 10))

        self.about_btn = tk.Button(self.top_bar, command=self.show_about, relief="flat",
                                    font=("Segoe UI", 9, "bold"), cursor="hand2")
        self.about_btn.pack(side="left")
        self._hover_neutral(self.about_btn)

        self.theme_btn = tk.Button(self.top_bar, command=self.toggle_theme, width=3,
                                    relief="flat", font=("Segoe UI", 10, "bold"), cursor="hand2")
        self.theme_btn.pack(side="right", padx=(6, 0))
        self._hover_neutral(self.theme_btn)

        self.lang_btn = tk.Button(self.top_bar, command=self.toggle_language, width=4,
                                   relief="flat", font=("Segoe UI", 9, "bold"), cursor="hand2")
        self.lang_btn.pack(side="right")
        self._hover_neutral(self.lang_btn)

        self.compact_btn = tk.Button(self.top_bar, command=self.enter_compact_mode, relief="flat",
                                      font=("Segoe UI", 9, "bold"), cursor="hand2")
        self.compact_btn.pack(side="right", padx=(0, 8))
        self._hover_neutral(self.compact_btn)

        self.ontop_btn = tk.Button(self.top_bar, command=self.toggle_always_on_top, relief="flat",
                                    font=("Segoe UI", 9, "bold"), cursor="hand2")
        self.ontop_btn.pack(side="right", padx=(0, 8))
        self._hover_ontop(self.ontop_btn)

        self.divider1 = tk.Frame(self, height=2, bg=c["accent"])
        self.divider1.pack(fill="x", padx=15, pady=(0, 10))

        # --- Paste area ---
        self.paste_frame = tk.Frame(self, bg=c["bg"])
        self.paste_frame.pack(fill="x", padx=15)

        self.bulk_text = tk.Text(
            self.paste_frame, height=4, width=44, insertbackground=c["fg"],
            relief="solid", borderwidth=1, highlightthickness=1,
            font=("Segoe UI", 10), wrap="word", undo=True
        )
        self.bulk_text.pack(side="left", fill="x", expand=True, ipady=4)
        self.bulk_text.bind("<Control-Return>", lambda e: (self.split_to_list(), "break"))
        self._attach_context_menu(self.bulk_text, is_text=True)

        self.split_btn = tk.Button(
            self.paste_frame, command=self.split_to_list, relief="flat",
            font=("Segoe UI", 9, "bold"), cursor="hand2", width=10
        )
        self.split_btn.pack(side="left", padx=(8, 0), fill="y")
        self._hover_accent(self.split_btn)

        # --- Toolbar ---
        self.toolbar = tk.Frame(self, bg=c["bg"])
        self.toolbar.pack(fill="x", padx=15, pady=(10, 10))

        self.clear_btn = tk.Button(self.toolbar, command=self.clear_all, relief="flat",
                                    font=("Segoe UI", 9), cursor="hand2")
        self.clear_btn.pack(side="left")
        self._hover_neutral(self.clear_btn)

        self.copy_all_btn = tk.Button(self.toolbar, command=self.copy_all, relief="flat",
                                       font=("Segoe UI", 9), cursor="hand2")
        self.copy_all_btn.pack(side="left", padx=(8, 0))
        self._hover_neutral(self.copy_all_btn)

        self.status_label = tk.Label(self.toolbar, text="", font=("Segoe UI", 9))
        self.status_label.pack(side="right")

        self.divider2 = tk.Frame(self, height=1, bg=c["entry_border"])
        self.divider2.pack(fill="x", padx=15, pady=(0, 12))

        # --- 15 item list ---
        self.list_frame = tk.Frame(self, bg=c["bg"])
        self.list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        for i in range(1, NUM_ITEMS + 1):
            row = tk.Frame(self.list_frame, bg=c["bg"])
            row.pack(fill="x", pady=3)

            num_label = tk.Label(row, text=f"{i}.", font=("Segoe UI", 9), width=3, anchor="e")
            num_label.pack(side="left")
            self.row_widgets.append((row, num_label))

            entry = tk.Entry(row, width=30, insertbackground=c["fg"], relief="solid",
                              borderwidth=1, highlightthickness=1, font=("Segoe UI", 10))
            entry.pack(side="left", fill="x", expand=True, ipady=4, padx=(6, 6))
            entry.bind("<KeyRelease>", self._on_entry_change)
            entry.bind("<Return>", self._focus_next_entry)
            self._attach_context_menu(entry, is_text=False)
            self.entries.append(entry)

            row_clear_btn = tk.Button(row, text="✕", width=2, relief="flat",
                                       font=("Segoe UI", 9, "bold"), cursor="hand2",
                                       command=lambda idx=i - 1: self.clear_item(idx))
            row_clear_btn.pack(side="left", padx=(0, 6))
            self._hover_danger_ghost(row_clear_btn)
            self.row_clear_buttons.append(row_clear_btn)

            copy_btn = tk.Button(row, width=8, relief="flat", font=("Segoe UI", 9, "bold"), cursor="hand2")
            copy_btn.configure(command=lambda idx=i - 1, b=copy_btn: self.copy_item(idx, b))
            copy_btn.pack(side="left")
            self._hover_accent(copy_btn)
            self.copy_buttons.append(copy_btn)

    # ------------------------------------------------------------------
    # Context menu (right-click cut/copy/paste/select-all) for entries & text
    # ------------------------------------------------------------------
    def _attach_context_menu(self, widget, is_text):
        menu = tk.Menu(self, tearoff=0)

        def cut():
            widget.event_generate("<<Cut>>")

        def copy():
            widget.event_generate("<<Copy>>")

        def paste():
            widget.event_generate("<<Paste>>")

        def select_all():
            if is_text:
                widget.tag_add("sel", "1.0", "end-1c")
            else:
                widget.selection_range(0, "end")

        menu.add_command(label=self.t("menu_cut"), command=cut)
        menu.add_command(label=self.t("menu_copy"), command=copy)
        menu.add_command(label=self.t("menu_paste"), command=paste)
        menu.add_separator()
        menu.add_command(label=self.t("menu_selectall"), command=select_all)

        def show_menu(event):
            # Rebuild labels each time in case the language changed since attaching
            menu.entryconfigure(0, label=self.t("menu_cut"))
            menu.entryconfigure(1, label=self.t("menu_copy"))
            menu.entryconfigure(2, label=self.t("menu_paste"))
            menu.entryconfigure(4, label=self.t("menu_selectall"))
            menu.tk_popup(event.x_root, event.y_root)

        widget.bind("<Button-3>", show_menu)

    def _focus_next_entry(self, event):
        try:
            idx = self.entries.index(event.widget)
        except ValueError:
            return
        if idx + 1 < NUM_ITEMS:
            self.entries[idx + 1].focus_set()
        return "break"

    # ------------------------------------------------------------------
    # Language / theme
    # ------------------------------------------------------------------
    def _apply_language(self):
        self.title(self.t("window_title"))
        self.title_label.configure(text=self.t("title"))
        self.lang_btn.configure(text=self.t("lang_btn"))
        self.split_btn.configure(text=self.t("split_btn"))
        self.clear_btn.configure(text=self.t("clear_btn"))
        self.copy_all_btn.configure(text=self.t("copy_all_btn"))
        self.ontop_btn.configure(text=self.t("ontop_on") if self.always_on_top else self.t("ontop_off"))
        self.compact_btn.configure(text=self.t("compact_btn"))
        self.about_btn.configure(text=self.t("about_btn"))
        for btn in self.copy_buttons:
            btn.configure(text=self.t("copy_btn"))
        self._update_status()

    def toggle_language(self):
        self.lang = "pl" if self.lang == "en" else "en"
        self._apply_language()
        self.save_data()

    def _apply_theme(self):
        c = self.colors
        self.configure(bg=c["bg"])

        for frame in (self.title_frame, self.title_inner, self.top_bar, self.paste_frame,
                      self.toolbar, self.list_frame):
            frame.configure(bg=c["bg"])
        self.title_label.configure(bg=c["bg"], fg=c["accent"])
        self.status_label.configure(bg=c["bg"], fg=c["muted"])
        self.divider1.configure(bg=c["accent"])
        self.divider2.configure(bg=c["entry_border"])

        neutral_btns = [self.about_btn, self.lang_btn, self.compact_btn, self.clear_btn,
                        self.copy_all_btn, self.theme_btn]
        for btn in neutral_btns:
            btn.configure(bg=c["btn_neutral"], fg=c["fg"], activebackground=c["btn_neutral_hover"],
                          activeforeground=c["fg"])

        accent_btns = [self.split_btn] + self.copy_buttons
        for btn in accent_btns:
            btn.configure(bg=c["accent"], fg=c["accent_fg"], activebackground=c["accent_dark"],
                          activeforeground=c["accent_fg"])

        for btn in self.row_clear_buttons:
            btn.configure(bg=c["bg"], fg=c["danger"], activebackground=c["btn_neutral_hover"],
                          activeforeground=c["danger"])

        self.ontop_btn.configure(
            bg=c["accent"] if self.always_on_top else c["btn_neutral"],
            fg=c["accent_fg"] if self.always_on_top else c["fg"],
            activebackground=c["accent_dark"] if self.always_on_top else c["btn_neutral_hover"],
        )

        self.bulk_text.configure(bg=c["entry_bg"], fg=c["fg"], insertbackground=c["fg"],
                                  highlightbackground=c["entry_border"], highlightcolor=c["accent"])

        for row, num_label in self.row_widgets:
            row.configure(bg=c["bg"])
            num_label.configure(bg=c["bg"], fg=c["muted"])

        for entry in self.entries:
            entry.configure(bg=c["entry_bg"], fg=c["fg"], insertbackground=c["fg"],
                             highlightbackground=c["entry_border"], highlightcolor=c["accent"])

        self.theme_btn.configure(text="☾" if self.theme_name == "dark" else "☀")
        self._redraw_logos()

    def toggle_theme(self):
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self._apply_theme()
        self.save_data()

    def toggle_always_on_top(self):
        self.always_on_top = not self.always_on_top
        self.attributes("-topmost", self.always_on_top)
        self._apply_theme()
        self.ontop_btn.configure(text=self.t("ontop_on") if self.always_on_top else self.t("ontop_off"))
        self.save_data()

    def enter_compact_mode(self):
        c = self.colors
        # Hide main window, show small always-on-top icon window instead
        self.withdraw()

        icon_win = tk.Toplevel(self)
        icon_win.overrideredirect(True)  # no title bar / borders
        icon_win.attributes("-topmost", True)
        icon_win.configure(bg=c["accent"])

        size = 48
        pad = 4
        # Place near top-right corner of the screen by default
        x = self.winfo_screenwidth() - size - pad * 2 - 40
        y = 60
        icon_win.geometry(f"{size + pad * 2}x{size + pad * 2}+{x}+{y}")

        icon_canvas = tk.Canvas(icon_win, width=size, height=size, bd=0, highlightthickness=0)
        icon_canvas.pack(padx=pad, pady=pad)
        self._draw_logo(icon_canvas, size)

        # Restore main window on double-click of the icon
        def restore(event=None):
            icon_win.destroy()
            self.compact_window = None
            self.deiconify()
            self.lift()
            self.focus_force()

        icon_canvas.bind("<Double-Button-1>", restore)
        icon_win.bind("<Double-Button-1>", restore)

        # Allow dragging the compact icon around the screen
        drag_data = {"x": 0, "y": 0}

        def start_drag(event):
            drag_data["x"] = event.x
            drag_data["y"] = event.y

        def do_drag(event):
            new_x = icon_win.winfo_x() + (event.x - drag_data["x"])
            new_y = icon_win.winfo_y() + (event.y - drag_data["y"])
            icon_win.geometry(f"+{new_x}+{new_y}")

        icon_canvas.bind("<Button-1>", start_drag)
        icon_canvas.bind("<B1-Motion>", do_drag)

        self.compact_window = icon_win

    def show_about(self):
        c = self.colors
        about_win = tk.Toplevel(self)
        about_win.title(self.t("about_title"))
        about_win.configure(bg=c["bg"])
        about_win.resizable(False, False)
        about_win.transient(self)
        about_win.grab_set()

        content = tk.Frame(about_win, bg=c["bg"], padx=24, pady=20)
        content.pack()

        about_logo = tk.Canvas(content, width=56, height=56, bd=0, highlightthickness=0)
        about_logo.pack(pady=(0, 8))
        self._draw_logo(about_logo, 56)

        tk.Label(content, text=ABOUT_INFO["author"], bg=c["bg"], fg=c["fg"],
                 font=("Segoe UI", 11, "bold")).pack()

        tk.Label(content, text=ABOUT_INFO["group"], bg=c["bg"], fg=c["muted"],
                 font=("Segoe UI", 9)).pack(pady=(0, 10))

        github_label = tk.Label(content, text=ABOUT_INFO["github"], bg=c["bg"], fg=c["accent"],
                                 font=("Segoe UI", 9, "underline"), cursor="hand2")
        github_label.pack()
        github_label.bind("<Button-1>", lambda e: self._copy_to_clipboard(ABOUT_INFO["github"]))

        email_label = tk.Label(content, text=ABOUT_INFO["email"], bg=c["bg"], fg=c["accent"],
                                font=("Segoe UI", 9, "underline"), cursor="hand2")
        email_label.pack(pady=(2, 10))
        email_label.bind("<Button-1>", lambda e: self._copy_to_clipboard(ABOUT_INFO["email"]))

        tk.Label(content, text=ABOUT_INFO["license"], bg=c["bg"], fg=c["success"],
                 font=("Segoe UI", 9, "bold")).pack(pady=(0, 14))

        close_btn = tk.Button(content, text="OK", command=about_win.destroy, width=10,
                               bg=c["accent"], fg=c["accent_fg"], relief="flat",
                               font=("Segoe UI", 9, "bold"), activebackground=c["accent_dark"], cursor="hand2")
        close_btn.pack()

        about_win.update_idletasks()
        w = about_win.winfo_reqwidth()
        h = about_win.winfo_reqheight()
        x = self.winfo_x() + (self.winfo_width() // 2) - (w // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (h // 2)
        about_win.geometry(f"{w}x{h}+{x}+{y}")

    def _copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()

    # ------------------------------------------------------------------
    # Core actions
    # ------------------------------------------------------------------
    def split_to_list(self):
        text = self.bulk_text.get("1.0", "end-1c")
        lines = [ln.strip() for ln in text.split("\n") if ln.strip() != ""]
        for i in range(NUM_ITEMS):
            self.entries[i].delete(0, "end")
            if i < len(lines):
                self.entries[i].insert(0, lines[i])
        self._update_status()
        self.save_data()

    def copy_item(self, idx, btn):
        value = self.entries[idx].get()
        if not value:
            return
        self.clipboard_clear()
        self.clipboard_append(value)
        self.update()  # keep clipboard content after window closes

        c = self.colors
        btn.configure(text=self.t("copied_btn"), bg=c["success"], fg=c["accent_fg"])
        self.after(1000, lambda: self._restore_copy_btn(btn))

    def _restore_copy_btn(self, btn):
        if not btn.winfo_exists():
            return
        c = self.colors
        btn.configure(text=self.t("copy_btn"), bg=c["accent"], fg=c["accent_fg"])

    def copy_all(self):
        values = [e.get() for e in self.entries if e.get().strip() != ""]
        if not values:
            return
        self.clipboard_clear()
        self.clipboard_append("\n".join(values))
        self.update()

        c = self.colors
        original_text = self.copy_all_btn.cget("text")
        self.copy_all_btn.configure(text=self.t("copied_all_btn"), bg=c["success"], fg=c["accent_fg"])

        def restore():
            if self.copy_all_btn.winfo_exists():
                self.copy_all_btn.configure(text=self.t("copy_all_btn"), bg=c["btn_neutral"], fg=c["fg"])

        self.after(1000, restore)

    def clear_item(self, idx):
        self.entries[idx].delete(0, "end")
        self._update_status()
        self.save_data()

    def clear_all(self):
        self.bulk_text.delete("1.0", "end")
        for entry in self.entries:
            entry.delete(0, "end")
        self._update_status()
        self.save_data()

    def _update_status(self):
        n = sum(1 for e in self.entries if e.get().strip() != "")
        self.status_label.configure(text=self.t("status_filled").format(n=n, total=NUM_ITEMS))

    def _flash_saved_status(self):
        c = self.colors
        n = sum(1 for e in self.entries if e.get().strip() != "")
        self.status_label.configure(text=self.t("status_saved"), fg=c["success"])
        if self._status_after_id is not None:
            self.after_cancel(self._status_after_id)

        def revert():
            self.status_label.configure(
                text=self.t("status_filled").format(n=n, total=NUM_ITEMS), fg=c["muted"]
            )

        self._status_after_id = self.after(1200, revert)

    # ------------------------------------------------------------------
    # Persistence: remember list contents + settings across restarts
    # ------------------------------------------------------------------
    def _load_settings(self):
        """Load lang/theme/always_on_top before the UI is built, so the
        window opens directly in the user's last-used language & theme."""
        if not os.path.exists(DATA_PATH):
            return
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("lang") in STRINGS:
                self.lang = data["lang"]
            if data.get("theme") in THEMES:
                self.theme_name = data["theme"]
            self.always_on_top = bool(data.get("always_on_top", False))
        except (json.JSONDecodeError, OSError, ValueError):
            pass  # corrupted or unreadable file - start fresh, don't crash

    def load_data(self):
        if self.always_on_top:
            self.attributes("-topmost", True)
        if not os.path.exists(DATA_PATH):
            return
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data.get("items", [])
            for i in range(min(NUM_ITEMS, len(items))):
                self.entries[i].delete(0, "end")
                self.entries[i].insert(0, items[i])
        except (json.JSONDecodeError, OSError, ValueError):
            pass  # corrupted or unreadable file - start fresh, don't crash

    def save_data(self):
        items = [entry.get() for entry in self.entries]
        payload = {
            "items": items,
            "lang": self.lang,
            "theme": self.theme_name,
            "always_on_top": self.always_on_top,
        }
        try:
            with open(DATA_PATH, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            self._flash_saved_status()
        except OSError:
            pass  # if the folder isn't writable, silently skip saving

    def _on_entry_change(self, event=None):
        self._update_status()
        # Debounce: wait 400ms after the last keystroke before writing to disk
        if self._save_after_id is not None:
            self.after_cancel(self._save_after_id)
        self._save_after_id = self.after(400, self.save_data)

    def on_close(self):
        self.save_data()
        self.destroy()


if __name__ == "__main__":
    app = TextListApp()
    app.mainloop()
