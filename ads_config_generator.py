#!/usr/bin/env python3
"""
Ads Remote Config JSON Generator
---------------------------------
Desktop app (Tkinter) chạy trên Ubuntu.
Chọn 1 "type" config quảng cáo -> điền thông số -> sinh ra JSON tương ứng.

Chạy:
    python3 ads_config_generator.py

Nếu thiếu tkinter:
    sudo apt install python3-tk
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import font as tkfont

# ---------------------------------------------------------------------------
# Dữ liệu tĩnh: danh sách option cho các trường enum
# ---------------------------------------------------------------------------

TYPE_LAYOUT_OPTIONS = [
    "native_small_cta_bottom",
    "native_small_cta_top",
    "native_small_cta_right",
    "native_medium_cta_bottom",
    "native_medium_cta_top",
    "native_medium_media_left_cta_bottom",
    "native_medium_media_left_cta_right",
    "native_medium_media_left_cta_top",
    "medium_cta_right_bottom",
    "medium_cta_right_top",
    "other",
]

AD_TYPE_OPTIONS = ["inter", "appopen", "native"]

# Loại quảng cáo -> (label, template dựng form/JSON, có phải native full không)
TYPE_CATEGORIES = [
    ("Inter splash", "splash", False),
    ("Inter", "inter", False),
    ("App open / Reward", "ads_list", False),
    ("Banner", "banner", False),
    ("Native", "native", False),
    ("Native full", "native", True),
    ("Close (native full)", "close_config", False),
    ("Screen time (loading/downloading)", "screen_time", False),
    ("Onboarding on/off", "onboarding", False),
    ("Splash timeout", "splash_timeout", False),
    ("Boolean (true/false)", "boolean", False),
    ("Flow language", "flow_language", False),
]

# Native "full" -> type_layout mặc định = "other"
NATIVE_FULL_KEYS = {
    "N106_config_1", "N107_config_1", "N108_config_1",
    "N500_config_1", "N501_config_1", "N502_config_1",
}

# key -> (Tên hiển thị, template)
CONFIG_TYPES = {
    "I101_config_1": ("Splash (I101_config_1)", "splash"),
    "N101_config_1": ("Native splash (N101_config_1)", "native"),
    "N102_config_1": ("Native language loading (N102_config_1)", "native"),
    "N103_config_1": ("Native language (N103_config_1)", "native"),
    "N104_config_1": ("Native language dup (N104_config_1)", "native"),
    "N105_config_1": ("Native onboarding (N105_config_1)", "native"),
    "N106_config_1": ("Native full splash (N106_config_1)", "native"),
    "N107_config_1": ("Native onboarding full 1 (N107_config_1)", "native"),
    "N108_config_1": ("Native onboarding full 2 (N108_config_1)", "native"),
    "N109_config_1": ("Native welcome (N109_config_1)", "native"),
    "N110_config_1": ("Native welcome dup (N110_config_1)", "native"),
    "splash_timeout": ("Native splash timeout", "splash_timeout"),
    "language_loading_config": ("Language loading config", "screen_time"),
    "language_downloading_config": ("Language downloading config", "screen_time"),
    "onboarding_config": ("Onboarding config (on/off từng màn)", "onboarding"),
    "N106_config_2": ("Native full screen splash - close (N106_config_2)", "close_config"),
    "N107_config_2": ("Native onboarding full 1 - close (N107_config_2)", "close_config"),
    "N108_config_2": ("Native onboarding full 2 - close (N108_config_2)", "close_config"),
    "I10x_config_1": ("Inter ad từ home vào (I10x_config_1)", "inter"),
    "B10x_config_1": ("Banner ad từ home vào (B10x_config_1)", "banner"),
    "A101_config_1": ("App open resume (A101_config_1)", "ads_list"),
    "R10x_config_1": ("Reward ads (R10x_config_1)", "ads_list"),
    "N500_config_1": ("Native full sau inter splash (N500_config_1)", "native"),
    "N501_config_1": ("Native full sau inter home (N501_config_1)", "native"),
    "N502_config_1": ("Native full sau màn language cuối (N502_config_1)", "native"),
    "N500_config_2": ("Close - native full sau inter splash (N500_config_2)", "close_config"),
    "N501_config_2": ("Close - native full sau inter home (N501_config_2)", "close_config"),
    "N502_config_2": ("Close - native full sau màn language cuối (N502_config_2)", "close_config"),
    "N503_config_1": ("Native small cta right - đầu màn language (N503_config_1)", "native"),
    "N504_config_1": ("Native màn language downloading (N504_config_1)", "native"),
    "N505_config_1": ("Native màn language dup applying (N505_config_1)", "native"),
    "N506_config_1": ("Native màn language next (N506_config_1)", "native"),
    "N507_config_1": ("Native màn language drop (N507_config_1)", "native"),
    "I500_config_1": ("Inter show sau OB cuối cùng (I500_config_1)", "inter"),
    "I501_config_1": ("Inter show sau màn welcome dup (I501_config_1)", "inter"),
    "reopen_onboarding": ("Reopen onboarding", "boolean"),
    "reopen_language": ("Reopen language", "boolean"),
    "reopen_welcome": ("Reopen welcome", "boolean"),
    "flow_app_language": ("Flow app language", "flow_language"),
}


# ---------------------------------------------------------------------------
# Widget: checkbox tự vẽ (ô vuông bo, tích ✓ trắng trên nền xanh khi bật)
# ---------------------------------------------------------------------------

# màu dùng chung (định nghĩa sớm để widget bên dưới xài)
BG = "#eef1f5"
CARD = "#ffffff"
ACCENT = "#2563eb"
ACCENT_DARK = "#1d4ed8"
TEXT = "#1f2937"
MUTED = "#6b7280"


class ToggleCheck(ttk.Frame):
    """Checkbox tự vẽ trên canvas: ô bo góc, dấu ✓ nét mượt khi bật."""

    S = 22  # cạnh ô tích (px)

    def __init__(self, parent, variable, text=""):
        super().__init__(parent, style="Card.TFrame")
        self.var = variable
        self.fam = tkfont.nametofont("TkDefaultFont").actual("family")
        s = self.S
        self.cv = tk.Canvas(self, width=s + 3, height=s + 3, bg=CARD,
                            highlightthickness=0, cursor="hand2")
        self.cv.pack(side="left")
        self.cv.bind("<Button-1>", self._toggle)
        self.cv.bind("<Enter>", lambda e: self._render(hover=True))
        self.cv.bind("<Leave>", lambda e: self._render(hover=False))
        if text:
            lbl = ttk.Label(self, text=text, style="Card.TLabel", cursor="hand2")
            lbl.pack(side="left", padx=(8, 0))
            lbl.bind("<Button-1>", self._toggle)
        self.var.trace_add("write", lambda *_: self._render())
        self._render()

    def _toggle(self, _=None):
        self.var.set(not self.var.get())

    def _round(self, x1, y1, x2, y2, r, **kw):
        p = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
             x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        return self.cv.create_polygon(p, smooth=True, **kw)

    def _render(self, hover=False):
        c, s, on = self.cv, self.S, bool(self.var.get())
        c.delete("all")
        if on:
            self._round(1, 1, s + 1, s + 1, 6, fill=ACCENT,
                        outline=ACCENT_DARK if hover else ACCENT)
            # dấu ✓ vẽ bằng glyph font (được khử răng cưa) -> nét rõ, không bị rỗ
            c.create_text((s + 3) / 2, (s + 3) / 2, text="✓", fill="white",
                          font=(self.fam, int(s * 0.62), "bold"))
        else:
            self._round(1, 1, s + 1, s + 1, 6, fill="#ffffff",
                        outline=ACCENT if hover else "#c0c7d1")


# ---------------------------------------------------------------------------
# Widget: bảng list_ads có thể thêm/xóa dòng, cột tùy theo template
# ---------------------------------------------------------------------------

class ListAdsEditor(ttk.LabelFrame):
    """columns: list các tuple (key, kind, options)
    kind in {'bool', 'str', 'int', 'enum'}"""

    def __init__(self, parent, columns, title="list_ads", **kwargs):
        super().__init__(parent, text=title, padding=10, style="Card.TLabelframe", **kwargs)
        self.columns = columns
        self.rows = []  # list dict {"widgets":..., "cells":[...], "rm":btn}

        # 1 lưới chung cho header + các dòng -> cột luôn thẳng hàng
        self.grid_host = ttk.Frame(self, style="Card.TFrame")
        self.grid_host.pack(fill="x")
        for i, (key, kind, _) in enumerate(self.columns):
            self.grid_host.columnconfigure(i, weight=(1 if kind == "str" else 0))
            ttk.Label(self.grid_host, text=key, style="Card.TLabel",
                      font=("", 9, "bold")).grid(row=0, column=i, sticky="w",
                                                 padx=4, pady=(0, 4))
        self._rm_col = len(self.columns)

        btn_frame = ttk.Frame(self, style="Card.TFrame")
        btn_frame.pack(fill="x", pady=(8, 0))
        ttk.Button(btn_frame, text="+ Thêm dòng", command=self.add_row).pack(side="left")

    def add_row(self, defaults=None):
        defaults = defaults or {}
        widgets, cells = {}, []
        for key, kind, options in self.columns:
            if kind == "bool":
                var = tk.BooleanVar(value=defaults.get(key, True))
                w = ToggleCheck(self.grid_host, var)
            elif kind == "enum":
                var = tk.StringVar(value=defaults.get(key, options[0]))
                w = ttk.Combobox(self.grid_host, textvariable=var, values=options,
                                 width=12, state="readonly")
            elif kind == "int":
                var = tk.StringVar(value=str(defaults.get(key, 0)))
                w = ttk.Entry(self.grid_host, textvariable=var, width=10)
            else:  # str
                var = tk.StringVar(value=defaults.get(key, ""))
                w = ttk.Entry(self.grid_host, textvariable=var)
            widgets[key] = (kind, var)
            cells.append(w)
        rm = ttk.Button(self.grid_host, text="✕", width=3)
        row = {"widgets": widgets, "cells": cells, "rm": rm}
        rm.configure(command=lambda r=row: self.remove_row(r))
        self.rows.append(row)
        self._regrid()

    def _regrid(self):
        for ri, row in enumerate(self.rows, start=1):
            for ci, w in enumerate(row["cells"]):
                kind = self.columns[ci][1]
                w.grid(row=ri, column=ci, padx=4, pady=3,
                       sticky=("ew" if kind == "str" else "w"))
            row["rm"].grid(row=ri, column=self._rm_col, padx=(6, 0), pady=3)

    def remove_row(self, row):
        for w in row["cells"]:
            w.destroy()
        row["rm"].destroy()
        self.rows.remove(row)
        self._regrid()

    def get_data(self):
        data = []
        for row in self.rows:
            item = {}
            for key, (kind, var) in row["widgets"].items():
                if kind == "bool":
                    item[key] = bool(var.get())
                elif kind == "int":
                    raw = var.get().strip()
                    item[key] = int(raw) if raw else 0
                else:
                    item[key] = var.get()
            data.append(item)
        return data


# ---------------------------------------------------------------------------
# Main App
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Widget: xem trước bố cục native (vẽ mockup theo tên layout)
# ---------------------------------------------------------------------------

class LayoutPreview(ttk.Frame):
    """Vẽ sơ đồ vị trí icon / text / media / nút CTA cho từng type_layout,
    để user hình dung quảng cáo sẽ hiển thị thế nào."""

    W = 300      # bề rộng canvas
    PAD = 14     # lề trong "thẻ" quảng cáo
    GAP = 8      # khoảng cách giữa các block

    # mỗi layout = danh sách block xếp dọc
    SPECS = {
        "native_small_cta_bottom": ["info", "cta"],
        "native_small_cta_top": ["cta", "info"],
        "native_small_cta_right": ["info_r"],
        "native_medium_cta_bottom": ["info", "media", "cta"],
        "native_medium_cta_top": ["cta", "info", "media"],
        "native_medium_media_left_cta_bottom": ["ml", "cta"],
        "native_medium_media_left_cta_right": ["ml_r"],
        "native_medium_media_left_cta_top": ["cta", "ml"],
        "medium_cta_right_bottom": ["txt", "media", "info_r"],
        "medium_cta_right_top": ["info_r", "media", "hl"],
        "banner_small": ["banner"],
        "other": ["media_tall", "info", "cta"],   # full screen (full-CTA-bottom)
    }

    def __init__(self, parent):
        super().__init__(parent, style="Card.TFrame")
        self.fam = tkfont.nametofont("TkDefaultFont").actual("family")
        ttk.Label(self, text="Xem trước bố cục", style="CardMuted.TLabel").pack(anchor="w")
        self.c = tk.Canvas(self, width=self.W, height=200, bg=CARD, highlightthickness=0)
        self.c.pack(anchor="w", pady=(4, 0))

    # ---- helpers vẽ ----
    def _round(self, x1, y1, x2, y2, r, **kw):
        p = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
             x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        return self.c.create_polygon(p, smooth=True, **kw)

    def _icon(self, x, y, s=34):
        # icon app (ô bo góc màu), giống logo trong quảng cáo thật
        self._round(x, y, x + s, y + s, 7, fill="#3b82f6", outline="")
        self.c.create_oval(x + s * 0.3, y + s * 0.24, x + s * 0.7, y + s * 0.52,
                           fill="white", outline="")
        self._round(x + s * 0.22, y + s * 0.58, x + s * 0.78, y + s * 0.8, 2,
                    fill="white", outline="")

    def _badge(self, x, y):
        # nhãn "Ad" nhỏ ở góc trên (mọi native ad đều có)
        self._round(x, y, x + 22, y + 14, 3, fill="#f2c744", outline="")
        self.c.create_text(x + 11, y + 7, text="Ad", fill="#5b4a00",
                           font=(self.fam, 7, "bold"))

    def _text2(self, x, y, w):
        self.c.create_text(x, y, anchor="nw", text="Shopping with Hihi",
                           fill="#374151", font=(self.fam, 9, "bold"), width=max(w, 1))
        self.c.create_text(x, y + 15, anchor="nw",
                           text="Bảo sale hàng tuần. Sale 50% OFF...",
                           fill="#9aa2ad", font=(self.fam, 8), width=max(w, 1))

    def _cta(self, x, y, w, h=32, label="Download"):
        self._round(x, y, x + w, y + h, h / 2, fill=ACCENT, outline="")
        self.c.create_text(x + w / 2, y + h / 2, text=label, fill="white",
                           font=(self.fam, 9, "bold"))
        return h

    def _media(self, x, y, w, h):
        self._round(x, y, x + w, y + h, 8, fill="#cdd3dc", outline="")
        self.c.create_text(x + w / 2, y + h / 2, text="media", fill="#7b8595",
                           font=(self.fam, 9))
        return h

    def _block(self, b, x, y, w):
        if b == "cta":
            return self._cta(x, y, w)
        if b == "media":
            return self._media(x, y, w, 78)
        if b == "media_tall":
            return self._media(x, y, w, 150)
        if b == "hl":
            self.c.create_text(x, y, anchor="nw", text="Shopping with Hihi",
                               fill="#374151", font=(self.fam, 9, "bold"))
            return 18
        if b == "txt":   # tiêu đề + mô tả, không icon
            self._text2(x, y, w)
            return 36
        if b == "banner":   # banner nhỏ: chỉ icon + text, gọn 1 hàng
            self._icon(x, y, 30)
            self._text2(x + 40, y - 1, w - 40)
            return 34
        if b == "info":
            self._icon(x, y)
            self._text2(x + 44, y, w - 44)
            return 40
        if b == "info_r":
            bw = 78
            self._icon(x, y)
            self._text2(x + 44, y, w - 44 - bw - 8)
            self._cta(x + w - bw, y + 4, bw, 28)
            return 40
        if b == "ml":
            s = 66
            self._media(x, y, s, s)
            self._text2(x + s + 10, y, w - s - 10)
            return s
        if b == "ml_r":
            s = 66
            self._media(x, y, s, s)
            tw = w - s - 10
            self._text2(x + s + 10, y, tw)
            self._cta(x + s + 10, y + 40, min(tw, 130), 26)
            return s
        return 0

    def show(self, layout):
        c = self.c
        c.delete("all")
        blocks = self.SPECS.get(layout, self.SPECS["other"])
        self._badge(self.PAD, self.PAD)
        y = self.PAD + 20   # chừa chỗ cho nhãn "Ad"
        inner = self.W - 2 * self.PAD
        for b in blocks:
            y += self._block(b, self.PAD, y, inner) + self.GAP
        total = y - self.GAP + self.PAD
        c.configure(height=total)
        self._round(1, 1, self.W - 1, total - 1, 12, outline="#d5dbe3", width=1, fill="")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ads Remote Config JSON Generator")
        self.geometry("1160x760")
        self.minsize(1000, 640)
        self.configure(bg=BG)

        self.field_widgets = {}   # key -> (kind, var)
        self.list_editors = {}    # key -> ListAdsEditor
        self.batch = {}           # key -> data (bộ config gộp, giữ thứ tự thêm)
        self.batch_labels = {}    # key -> nhãn loại (để hiển thị trong list)
        self._editing_key = None  # key đang sửa (None = đang tạo mới)
        self._template = "splash"
        self._native_full = False
        self._cat_map = {c[0]: (c[1], c[2]) for c in TYPE_CATEGORIES}

        self._setup_style()
        self._build_ui()

        # lần đầu mở app -> tự hiện hướng dẫn (chỉ 1 lần)
        if not os.path.exists(self._guide_marker()):
            self.after(400, self.show_guide)

    @staticmethod
    def _guide_marker():
        return os.path.join(os.path.expanduser("~"), ".ads_config_generator_seen")

    def _keys_for(self, template, full):
        """Gợi ý các key đã biết cho 1 loại (từ CONFIG_TYPES), user vẫn gõ tự do được."""
        out = []
        for k, (_disp, tpl) in CONFIG_TYPES.items():
            if tpl != template:
                continue
            if template == "native" and (k in NATIVE_FULL_KEYS) != full:
                continue
            out.append(k)
        return out

    # ---------------- style ----------------

    def _setup_style(self):
        for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont"):
            try:
                tkfont.nametofont(name).configure(size=10)
            except tk.TclError:
                pass
        fam = tkfont.nametofont("TkDefaultFont").actual("family")

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".", background=BG, foreground=TEXT, font=(fam, 10))
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT)
        style.configure("TCheckbutton", background=BG, foreground=TEXT)
        style.map("TCheckbutton", background=[("active", BG)])
        style.configure("TLabelframe", background=BG, bordercolor="#d5dbe3")
        style.configure("TLabelframe.Label", background=BG,
                        foreground=ACCENT, font=(fam, 10, "bold"))
        style.configure("Title.TLabel", background=ACCENT, foreground="#ffffff",
                        font=(fam, 15, "bold"))
        style.configure("Subtitle.TLabel", background=ACCENT, foreground="#dbe4ff",
                        font=(fam, 10))
        style.configure("Header.TFrame", background=ACCENT)
        style.configure("Header.TButton", background="#ffffff", foreground=ACCENT,
                        font=(fam, 10, "bold"), padding=(14, 7), borderwidth=0)
        style.map("Header.TButton", background=[("active", "#e8eefc")])
        style.configure("Section.TLabel", foreground="#111827", font=(fam, 13, "bold"))
        style.configure("Muted.TLabel", foreground=MUTED)

        # nút phụ: phẳng, hiện đại
        style.configure("TButton", padding=(14, 7), font=(fam, 10),
                        background="#e7ebf1", foreground=TEXT, borderwidth=0)
        style.map("TButton", background=[("active", "#d7dde7"), ("pressed", "#d7dde7")])
        # nút chính
        style.configure("Accent.TButton", padding=(18, 9),
                        font=(fam, 10, "bold"), foreground="#ffffff",
                        background=ACCENT, borderwidth=0)
        style.map("Accent.TButton",
                  background=[("active", ACCENT_DARK), ("pressed", ACCENT_DARK)],
                  foreground=[("disabled", "#e5e7eb")])

        style.configure("TCombobox", padding=5, arrowsize=14,
                        fieldbackground=CARD, background=CARD,
                        bordercolor="#cbd2dc", lightcolor="#cbd2dc",
                        darkcolor="#cbd2dc", arrowcolor=ACCENT)
        style.map("TCombobox",
                  fieldbackground=[("readonly", CARD)],
                  selectbackground=[("readonly", CARD)],
                  selectforeground=[("readonly", TEXT)],
                  bordercolor=[("focus", ACCENT), ("hover", "#9aa6b5")])
        style.configure("TEntry", padding=5, fieldbackground=CARD,
                        bordercolor="#cbd2dc", lightcolor="#cbd2dc", darkcolor="#cbd2dc")
        style.map("TEntry", bordercolor=[("focus", ACCENT)])

        # vùng form dạng "card" trắng
        style.configure("Card.TFrame", background=CARD)
        style.configure("Card.TLabel", background=CARD, foreground=TEXT)
        style.configure("Field.TLabel", background=CARD, foreground="#374151", font=(fam, 10))
        style.configure("CardSection.TLabel", background=CARD, foreground="#111827",
                        font=(fam, 13, "bold"))
        style.configure("CardMuted.TLabel", background=CARD, foreground=MUTED, font=(fam, 9))
        style.configure("Card.TCheckbutton", background=CARD, foreground=TEXT,
                        font=(fam, 10, "bold"), padding=6, indicatorsize=15,
                        focuscolor=CARD)
        style.map("Card.TCheckbutton",
                  background=[("active", CARD)],
                  indicatorcolor=[("selected", ACCENT), ("pressed", ACCENT),
                                  ("!selected", "#ffffff")],
                  bordercolor=[("selected", ACCENT), ("!selected", "#b8c0cc")])
        style.configure("Card.TLabelframe", background=CARD, bordercolor="#e2e6ec")
        style.configure("Card.TLabelframe.Label", background=CARD, foreground=ACCENT,
                        font=(fam, 10, "bold"))

    # ---------------- UI scaffolding ----------------

    def _build_ui(self):
        # --- header ---
        header = ttk.Frame(self, style="Header.TFrame", padding=(20, 14))
        header.pack(fill="x")
        ttk.Button(header, text="❔ Hướng dẫn", style="Header.TButton",
                   command=self.show_guide).pack(side="right")
        titles = ttk.Frame(header, style="Header.TFrame")
        titles.pack(side="left", anchor="w")
        ttk.Label(titles, text="Ads Remote Config Generator",
                  style="Title.TLabel").pack(anchor="w")
        ttk.Label(titles, text="Chọn loại config, điền thông số và sinh JSON.",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(2, 0))

        # --- chọn loại + tự đặt tên key ---
        top = ttk.Frame(self, padding=(20, 14, 20, 6))
        top.pack(fill="x")
        ttk.Label(top, text="Loại quảng cáo", font=("", 10, "bold")).pack(side="left")
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(
            top, textvariable=self.type_var, width=26, state="readonly",
            values=[c[0] for c in TYPE_CATEGORIES],
        )
        self.type_combo.pack(side="left", padx=(8, 20))
        self.type_combo.bind("<<ComboboxSelected>>", self.on_category_changed)

        ttk.Label(top, text="Tên config (key)", font=("", 10, "bold")).pack(side="left")
        self.key_var = tk.StringVar()
        # editable: gõ tên tuỳ ý HOẶC chọn key có sẵn gợi ý theo loại
        self.key_combo = ttk.Combobox(top, textvariable=self.key_var, width=34)
        self.key_combo.pack(side="left", padx=8)

        # --- thanh hành động (pack TRƯỚC vùng co giãn để không bao giờ bị cắt) ---
        ttk.Separator(self, orient="horizontal").pack(side="bottom", fill="x")
        bottom = ttk.Frame(self, padding=(20, 10, 20, 12))
        bottom.pack(side="bottom", fill="x")
        ttk.Button(bottom, text="⚡ Tạo JSON", style="Accent.TButton",
                   command=self.generate_json).pack(side="left")
        # nút đổi giữa "Thêm vào bộ" (tạo mới) và "Cập nhật" (đang sửa)
        self.add_btn = ttk.Button(bottom, text="➕ Thêm vào bộ", command=self.add_to_batch)
        self.add_btn.pack(side="left", padx=8)
        self.cancel_btn = ttk.Button(bottom, text="✕ Huỷ sửa", command=self._exit_edit)
        ttk.Button(bottom, text="↺ Reset form", command=self.reset_form).pack(side="left")
        self.status_var = tk.StringVar(value="Sẵn sàng.")
        ttk.Label(bottom, textvariable=self.status_var, style="Muted.TLabel").pack(side="right")

        paned = ttk.Panedwindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=20, pady=(6, 10))
        # đặt thanh chia ~52% cho form (trái) NGAY KHI paned có kích thước thật
        self._sash_done = False

        def _init_sash(_=None):
            w = paned.winfo_width()
            if not self._sash_done and w > 200:
                paned.sashpos(0, int(w * 0.52))
                self._sash_done = True
        paned.bind("<Configure>", _init_sash)

        # --- left: scrollable form ---
        left_container = ttk.Frame(paned)
        paned.add(left_container, weight=1)

        canvas = tk.Canvas(left_container, borderwidth=0, highlightthickness=0, bg=CARD)
        self._left_canvas = canvas
        vscroll = ttk.Scrollbar(left_container, orient="vertical", command=canvas.yview)
        self.form_frame = ttk.Frame(canvas, padding=18, style="Card.TFrame")
        self.form_frame.bind("<Configure>", lambda e: self._sync_scrollregion())
        self._form_win = canvas.create_window((0, 0), window=self.form_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: (
            canvas.itemconfigure(self._form_win, width=e.width), self._sync_scrollregion()))
        canvas.configure(yscrollcommand=vscroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        vscroll.pack(side="right", fill="y")

        canvas.bind_all("<MouseWheel>", lambda e: self._scroll_left(int(-1 * (e.delta / 120))))
        canvas.bind_all("<Button-4>", lambda e: self._scroll_left(-1))
        canvas.bind_all("<Button-5>", lambda e: self._scroll_left(1))

        # --- right: chia dọc = JSON (trên) + bộ config gộp (dưới) ---
        rpane = ttk.Panedwindow(paned, orient="vertical")
        paned.add(rpane, weight=1)

        # (trên) kết quả JSON
        top_r = ttk.Frame(rpane, padding=(12, 0, 0, 0))
        rpane.add(top_r, weight=3)
        ttk.Label(top_r, text="Kết quả JSON", style="Section.TLabel").pack(anchor="w", pady=(0, 6))
        out_btns = ttk.Frame(top_r)
        out_btns.pack(side="bottom", fill="x", pady=(8, 0))
        ttk.Button(out_btns, text="📋 Copy", command=self.copy_output).pack(side="left")
        ttk.Button(out_btns, text="💾 Lưu file...", command=self.save_output).pack(side="left", padx=8)
        self.output_text = tk.Text(
            top_r, wrap="none", font=("Courier New", 11),
            bg=CARD, fg=TEXT, relief="flat", borderwidth=1,
            highlightthickness=1, highlightbackground="#d5dbe3",
            highlightcolor=ACCENT, insertbackground=ACCENT, padx=10, pady=8,
        )
        self.output_text.pack(side="top", fill="both", expand=True)

        # (dưới) bộ config gộp — bấm 1 dòng để xem lại JSON của nó
        bot_r = ttk.Frame(rpane, padding=(12, 6, 0, 0))
        rpane.add(bot_r, weight=2)
        self.batch_title = tk.StringVar(value="Bộ config gộp (0) — bấm 1 dòng để xem lại")
        ttk.Label(bot_r, textvariable=self.batch_title, style="Section.TLabel").pack(anchor="w", pady=(0, 6))
        bb = ttk.Frame(bot_r)
        bb.pack(side="bottom", fill="x", pady=(8, 0))
        ttk.Button(bb, text="👁 Xem template", command=self.preview_batch).pack(side="left")
        ttk.Button(bb, text="✕ Xóa mục", command=self.remove_batch_selected).pack(side="left", padx=6)
        ttk.Button(bb, text="Xóa hết", command=self.clear_batch).pack(side="left")
        ttk.Button(bb, text="⬇ Export Firebase...", style="Accent.TButton",
                   command=self.export_batch).pack(side="right")
        list_wrap = ttk.Frame(bot_r)
        list_wrap.pack(side="top", fill="both", expand=True)
        blist_scroll = ttk.Scrollbar(list_wrap, orient="vertical")
        self.batch_list = tk.Listbox(
            list_wrap, bg=CARD, fg=TEXT, relief="flat",
            highlightthickness=1, highlightbackground="#d5dbe3",
            highlightcolor=ACCENT, selectbackground=ACCENT,
            selectforeground="#ffffff", activestyle="none",
            font=("Courier New", 10), yscrollcommand=blist_scroll.set,
        )
        blist_scroll.config(command=self.batch_list.yview)
        blist_scroll.pack(side="right", fill="y")
        self.batch_list.pack(side="left", fill="both", expand=True)
        self.batch_list.bind("<<ListboxSelect>>", self.on_batch_select)
        # cuộn list bộ config độc lập với form bên trái ("break" chặn handler global)
        def _blist_wheel(step):
            self.batch_list.yview_scroll(step, "units")
            return "break"
        self.batch_list.bind("<MouseWheel>", lambda e: _blist_wheel(int(-1 * (e.delta / 120))))
        self.batch_list.bind("<Button-4>", lambda e: _blist_wheel(-1))
        self.batch_list.bind("<Button-5>", lambda e: _blist_wheel(1))

        self.type_combo.current(0)
        self.on_category_changed()

    # ---------------- scroll form trái ----------------

    def _content_overflows(self):
        c = self._left_canvas
        bbox = c.bbox("all")
        if not bbox:
            return False
        return (bbox[3] - bbox[1]) > c.winfo_height()

    def _sync_scrollregion(self):
        c = self._left_canvas
        c.configure(scrollregion=c.bbox("all"))
        if not self._content_overflows():
            c.yview_moveto(0)   # vừa khít -> ghim đầu, không để trống

    def _scroll_left(self, step):
        # chỉ cuộn khi nội dung dài hơn khung; ngắn thì không cho cuộn
        if self._content_overflows():
            self._left_canvas.yview_scroll(step, "units")

    # ---------------- form helpers ----------------

    def clear_form(self):
        for w in self.form_frame.winfo_children():
            w.destroy()
        self.field_widgets = {}
        self.list_editors = {}

    def _field_wrap(self, label):
        """Nhãn ở trên, ô nhập full-width bên dưới (gọn cho panel hẹp)."""
        frame = ttk.Frame(self.form_frame, style="Card.TFrame")
        frame.pack(fill="x", pady=(6, 2))
        ttk.Label(frame, text=label, style="Field.TLabel").pack(anchor="w", pady=(0, 3))
        return frame

    def add_bool_field(self, label, key, default=True):
        var = tk.BooleanVar(value=default)
        ToggleCheck(self.form_frame, var, text=label).pack(anchor="w", pady=5)
        self.field_widgets[key] = ("bool", var)

    def add_int_field(self, label, key, default=0):
        frame = self._field_wrap(label)
        var = tk.StringVar(value=str(default))
        ttk.Entry(frame, textvariable=var, width=18).pack(anchor="w")
        self.field_widgets[key] = ("int", var)

    def add_str_field(self, label, key, default=""):
        frame = self._field_wrap(label)
        var = tk.StringVar(value=default)
        ttk.Entry(frame, textvariable=var).pack(fill="x")
        self.field_widgets[key] = ("str", var)

    def add_enum_field(self, label, key, options, default=None):
        frame = self._field_wrap(label)
        var = tk.StringVar(value=default or options[0])
        ttk.Combobox(
            frame, textvariable=var, values=options, state="readonly"
        ).pack(fill="x")
        self.field_widgets[key] = ("enum", var)

    def add_list_editor(self, key, columns, title="list_ads", default_rows=1):
        editor = ListAdsEditor(self.form_frame, columns=columns, title=title)
        editor.pack(fill="x", pady=10)
        for _ in range(default_rows):
            editor.add_row()
        self.list_editors[key] = editor

    def add_note(self, text):
        ttk.Label(self.form_frame, text=text, style="CardMuted.TLabel",
                  wraplength=380, justify="left").pack(anchor="w", pady=(2, 8))

    # ---------------- template builders ----------------

    def build_ads_list(self):
        self.add_bool_field("enable", "enable", True)
        self.add_list_editor(
            "list_ads",
            [("enable_ad", "bool", None), ("adunit", "str", None)],
        )

    def build_banner(self):
        self.add_bool_field("enable", "enable", True)
        self.add_bool_field("is_collapsible", "is_collapsible", False)
        preview = LayoutPreview(self.form_frame)
        preview.pack(anchor="w", fill="x", pady=(2, 12))
        preview.show("banner_small")
        self.add_list_editor(
            "list_ads",
            [("enable_ad", "bool", None), ("adunit", "str", None)],
        )

    def build_inter(self):
        self.add_bool_field("enable", "enable", True)
        self.add_int_field("time_interval_ms", "time_interval_ms", 30000)
        self.add_str_field("time_steps (vd: 1,2,3,4,5,6)", "time_steps", "1,2,3,4,5,6")
        self.add_list_editor(
            "list_ads",
            [("enable_ad", "bool", None), ("adunit", "str", None)],
        )

    def build_native(self):
        self.add_bool_field("enable", "enable", True)
        if self._native_full:
            # native full: chỉ có "other", không đổi layout khác
            options, default_layout = ["other"], "other"
        else:
            options = TYPE_LAYOUT_OPTIONS
            default_layout = "native_medium_media_left_cta_bottom"
        self.add_enum_field("type_layout", "type_layout", options, default=default_layout)
        preview = LayoutPreview(self.form_frame)
        preview.pack(anchor="w", fill="x", pady=(2, 12))
        var = self.field_widgets["type_layout"][1]
        var.trace_add("write", lambda *_: preview.show(var.get()))
        preview.show(default_layout)
        self.add_list_editor(
            "list_ads",
            [("enable_ad", "bool", None), ("adunit", "str", None)],
        )

    def build_close_config(self):
        self.add_bool_field("is_show_close", "is_show_close", True)
        self.add_int_field("delay_show_close_ms", "delay_show_close_ms", 2000)
        self.add_int_field("time_delay_skip_ms", "time_delay_skip_ms", 6000)

    def build_splash(self):
        self.add_bool_field("enable", "enable", True)
        self.add_int_field("total_timeout_ms", "total_timeout_ms", 45000)
        self.add_list_editor(
            "list_ads",
            [
                ("enable_ad", "bool", None),
                ("type", "enum", AD_TYPE_OPTIONS),
                ("timeout_ms", "int", None),
                ("adunit", "str", None),
            ],
        )

    def build_splash_timeout(self):
        self.add_int_field("delay_ms", "delay_ms", 1000)
        self.add_int_field("waiting_ms", "waiting_ms", 5000)

    def build_screen_time(self):
        self.add_bool_field("enable_screen", "enable_screen", True)
        self.add_int_field("show_time_ms", "show_time_ms", 2000)

    def build_onboarding(self):
        for i in range(1, 5):
            self.add_bool_field(f"screen_{i}", f"screen_{i}", True)

    def build_boolean(self):
        self.add_enum_field("value", "value", ["true", "false"], default="false")
        self.add_note("Đây là key dạng giá trị đơn (không phải object).")

    def build_flow_language(self):
        self.add_enum_field("value", "value", ["1", "2", "3"], default="1")
        self.add_note("1: default | 2: flow auto next | 3: flow có màn drop")

    # ---------------- events ----------------

    def on_category_changed(self, event=None):
        self._exit_edit()   # đổi loại = tạo mới, tắt chế độ cập nhật
        self.clear_form()
        label = self.type_var.get()
        template, full = self._cat_map[label]
        self._template = template
        self._native_full = full
        # gợi ý key có sẵn cho loại này (vẫn gõ tên tự do được)
        sugg = self._keys_for(template, full)
        self.key_combo.configure(values=sugg)
        self.key_var.set(sugg[0] if sugg else "")
        ttk.Label(self.form_frame, text=label, style="CardSection.TLabel").pack(
            anchor="w", pady=(0, 12)
        )
        getattr(self, f"build_{template}")()
        self.output_text.delete("1.0", "end")
        self.update_idletasks()
        self._sync_scrollregion()   # cập nhật vùng cuộn + ghim đầu nếu ngắn

    def reset_form(self):
        self.on_category_changed()

    def collect_data(self):
        """Dựng data từ form hiện tại. Trả (key, data) hoặc None nếu lỗi nhập liệu."""
        key = self.key_var.get().strip()
        template = self._template

        def bval(k):
            return bool(self.field_widgets[k][1].get())

        def ival(k):
            raw = self.field_widgets[k][1].get().strip()
            return int(raw) if raw else 0

        def sval(k):
            return self.field_widgets[k][1].get()

        try:
            if template == "ads_list":
                data = {"enable": bval("enable"), "list_ads": self.list_editors["list_ads"].get_data()}
            elif template == "banner":
                data = {
                    "enable": bval("enable"),
                    "is_collapsible": bval("is_collapsible"),
                    "list_ads": self.list_editors["list_ads"].get_data(),
                }
            elif template == "inter":
                raw_steps = sval("time_steps").strip()
                steps = [int(x.strip()) for x in raw_steps.split(",") if x.strip()] if raw_steps else []
                data = {
                    "enable": bval("enable"),
                    "time_interval_ms": ival("time_interval_ms"),
                    "time_steps": steps,
                    "list_ads": self.list_editors["list_ads"].get_data(),
                }
            elif template == "native":
                data = {
                    "enable": bval("enable"),
                    "type_layout": sval("type_layout"),
                    "list_ads": self.list_editors["list_ads"].get_data(),
                }
            elif template == "close_config":
                data = {
                    "is_show_close": bval("is_show_close"),
                    "delay_show_close_ms": ival("delay_show_close_ms"),
                    "time_delay_skip_ms": ival("time_delay_skip_ms"),
                }
            elif template == "splash":
                data = {
                    "enable": bval("enable"),
                    "total_timeout_ms": ival("total_timeout_ms"),
                    "list_ads": self.list_editors["list_ads"].get_data(),
                }
            elif template == "splash_timeout":
                data = {"delay_ms": ival("delay_ms"), "waiting_ms": ival("waiting_ms")}
            elif template == "screen_time":
                data = {"enable_screen": bval("enable_screen"), "show_time_ms": ival("show_time_ms")}
            elif template == "onboarding":
                data = {f"screen_{i}": bval(f"screen_{i}") for i in range(1, 5)}
            elif template == "boolean":
                data = sval("value") == "true"
            elif template == "flow_language":
                data = int(sval("value"))
            else:
                data = {}
        except ValueError as exc:
            messagebox.showerror("Lỗi nhập liệu", f"Giá trị số không hợp lệ: {exc}")
            return None

        return key, data

    def _show_json(self, data):
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", json.dumps(data, indent=2, ensure_ascii=False))

    def generate_json(self):
        result = self.collect_data()
        if result is None:
            return
        key, data = result
        self._show_json(data)
        self.status_var.set(f"✓ Đã tạo JSON cho {key}.")

    # ---------------- bộ config gộp ----------------

    def add_to_batch(self):
        result = self.collect_data()
        if result is None:
            return
        key, data = result
        if not key:
            messagebox.showwarning("Thiếu tên", "Nhập 'Tên config (key)' trước khi thêm vào bộ.")
            return
        overwrite = key in self.batch
        self.batch[key] = data
        self.batch_labels[key] = self.type_var.get()
        self.refresh_batch_list()
        self._show_json(data)   # đồng bộ ô kết quả
        verb = "Cập nhật" if overwrite else "Đã thêm"
        self.status_var.set(f"➕ {verb} {key} (bộ có {len(self.batch)} config).")

    def refresh_batch_list(self):
        self.batch_list.delete(0, "end")
        for key in self.batch:
            lbl = self.batch_labels.get(key, "")
            self.batch_list.insert("end", f"{key}   ({lbl})" if lbl else key)
        self.batch_title.set(
            f"Bộ config gộp ({len(self.batch)}) — bấm 1 dòng để sửa lại"
        )

    def _selected_batch_key(self):
        sel = self.batch_list.curselection()
        if not sel:
            return None
        return list(self.batch.keys())[sel[0]]

    def on_batch_select(self, event=None):
        key = self._selected_batch_key()
        if key is None:
            return
        data = self.batch[key]
        label = self.batch_labels.get(key)
        # dựng lại form đúng loại rồi đổ data vào để sửa
        if label and label in self._cat_map:
            self.type_var.set(label)
            self.on_category_changed()   # sẽ reset về add-mode
        self.key_var.set(key)
        self._load_into_form(data)
        self._enter_edit(key)            # bật chế độ cập nhật
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", json_str)
        self.status_var.set(f"✏️ Đang sửa: {key} — bấm '💾 Cập nhật' để lưu vào bộ.")

    def _enter_edit(self, key):
        self._editing_key = key
        self.add_btn.configure(text="💾 Cập nhật", style="Accent.TButton",
                               command=self.update_batch)
        self.cancel_btn.pack(side="left", padx=(0, 8))

    def _exit_edit(self):
        self._editing_key = None
        self.add_btn.configure(text="➕ Thêm vào bộ", style="TButton",
                               command=self.add_to_batch)
        self.cancel_btn.pack_forget()

    def update_batch(self):
        result = self.collect_data()
        if result is None:
            return
        newkey, data = result
        if not newkey:
            messagebox.showwarning("Thiếu tên", "Nhập 'Tên config (key)' để lưu.")
            return
        oldkey = self._editing_key
        if oldkey and oldkey != newkey and oldkey in self.batch:
            del self.batch[oldkey]          # đổi tên key -> bỏ key cũ
            self.batch_labels.pop(oldkey, None)
        self.batch[newkey] = data
        self.batch_labels[newkey] = self.type_var.get()
        self._editing_key = newkey
        self.refresh_batch_list()
        self._show_json(data)   # đồng bộ ô kết quả với cái vừa lưu
        self.status_var.set(f"💾 Đã cập nhật {newkey} vào bộ ({len(self.batch)} config).")

    def _load_into_form(self, data):
        """Đổ dữ liệu 1 config vào form hiện tại (ngược với collect_data)."""
        fw = self.field_widgets
        tpl = self._template

        def setf(k, v):
            if k not in fw:
                return
            kind, var = fw[k]
            var.set(bool(v) if kind == "bool" else str(v))

        if tpl == "boolean":
            setf("value", "true" if data in (True, "true") else "false")
            return
        if tpl == "flow_language":
            setf("value", str(data))
            return
        if not isinstance(data, dict):
            return

        for k, v in data.items():
            if k == "list_ads":
                continue
            if k == "time_steps" and isinstance(v, list):
                setf("time_steps", ",".join(str(x) for x in v))
            else:
                setf(k, v)

        if "list_ads" in data and "list_ads" in self.list_editors:
            ed = self.list_editors["list_ads"]
            for row in list(ed.rows):      # bỏ dòng mặc định
                ed.remove_row(row)
            for item in data["list_ads"]:  # nạp đúng số dòng đã lưu
                ed.add_row(defaults=item)

    def remove_batch_selected(self):
        key = self._selected_batch_key()
        if key is None:
            self.status_var.set("Chọn 1 mục trong bộ để xóa.")
            return
        del self.batch[key]
        self.batch_labels.pop(key, None)
        self.refresh_batch_list()
        self.status_var.set(f"Đã xóa {key} khỏi bộ ({len(self.batch)} còn lại).")

    def clear_batch(self):
        if not self.batch:
            return
        if not messagebox.askyesno("Xóa hết", "Xóa toàn bộ config đã thêm?"):
            return
        self.batch.clear()
        self.batch_labels.clear()
        self.refresh_batch_list()
        self.status_var.set("Đã xóa hết bộ config.")

    def _firebase_template(self):
        """Bọc bộ config thành template Firebase Remote Config (import thẳng được).
        Giá trị RC luôn là chuỗi + valueType tương ứng."""
        params = {}
        for key, val in self.batch.items():
            if isinstance(val, bool):          # bool phải check trước int
                vtype, sval = "BOOLEAN", ("true" if val else "false")
            elif isinstance(val, int):
                vtype, sval = "NUMBER", str(val)
            elif isinstance(val, float):
                vtype, sval = "NUMBER", repr(val)
            elif isinstance(val, (dict, list)):
                vtype, sval = "JSON", json.dumps(val, ensure_ascii=False)
            else:
                vtype, sval = "STRING", str(val)
            params[key] = {"defaultValue": {"value": sval}, "valueType": vtype}
        return {"parameters": params}

    def preview_batch(self):
        if not self.batch:
            self.status_var.set("Bộ config đang trống.")
            return
        json_str = json.dumps(self._firebase_template(), indent=2, ensure_ascii=False)
        self._show_json_popup(
            "Template Firebase Remote Config", json_str,
            note=f"{len(self.batch)} param — đây là file sẽ export để import thẳng vào RC "
                 "(import sẽ ghi đè toàn bộ parameter hiện có).",
        )
        self.status_var.set(f"Xem template Firebase RC ({len(self.batch)} param).")

    def _show_json_popup(self, title, text, note=""):
        win = getattr(self, "_tpl_win", None)
        if win and win.winfo_exists():
            win.destroy()
        win = tk.Toplevel(self, bg=CARD)
        self._tpl_win = win
        win.title(title)
        win.geometry("680x560")
        win.minsize(480, 360)
        win.transient(self)

        ttk.Label(win, text=title, style="CardSection.TLabel").pack(anchor="w", padx=16, pady=(14, 4))
        if note:
            ttk.Label(win, text=note, style="CardMuted.TLabel", wraplength=640,
                      justify="left").pack(anchor="w", padx=16, pady=(0, 8))

        wrap = ttk.Frame(win, style="Card.TFrame")
        wrap.pack(fill="both", expand=True, padx=16)
        sb = ttk.Scrollbar(wrap, orient="vertical")
        txt = tk.Text(wrap, wrap="none", font=("Courier New", 10), bg=CARD, fg=TEXT,
                      relief="flat", padx=8, pady=6, highlightthickness=1,
                      highlightbackground="#d5dbe3", yscrollcommand=sb.set)
        sb.config(command=txt.yview)
        sb.pack(side="right", fill="y")
        txt.pack(side="left", fill="both", expand=True)
        txt.insert("1.0", text)
        txt.configure(state="disabled")

        btns = ttk.Frame(win, style="Card.TFrame")
        btns.pack(fill="x", padx=16, pady=12)

        def _copy():
            self.clipboard_clear()
            self.clipboard_append(text)
            self.status_var.set("✓ Đã copy template.")
        ttk.Button(btns, text="📋 Copy", command=_copy).pack(side="left")
        ttk.Button(btns, text="Đóng", style="Accent.TButton",
                   command=win.destroy).pack(side="right")

    def export_batch(self):
        if not self.batch:
            messagebox.showinfo("Bộ trống", "Hãy '➕ Thêm vào bộ' vài config trước khi export.")
            return
        json_str = json.dumps(self._firebase_template(), indent=2, ensure_ascii=False)
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile="remoteconfig.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(json_str)
            self.status_var.set(f"✓ Export Firebase RC ({len(self.batch)} param) → {path}")

    def copy_output(self):
        text = self.output_text.get("1.0", "end").strip()
        if not text:
            self.status_var.set("Chưa có JSON để copy.")
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self.status_var.set("✓ Đã copy vào clipboard.")

    def save_output(self):
        text = self.output_text.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo("Chưa có dữ liệu", "Hãy bấm 'Tạo JSON' trước khi lưu.")
            return
        key = self.key_var.get().strip() or "config"
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=f"{key}.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            self.status_var.set(f"✓ Đã lưu: {path}")

    # ---------------- hướng dẫn ----------------

    GUIDE_TEXT = """CÁCH DÙNG NHANH

1. Chọn "Loại quảng cáo" (Inter splash, Inter, App open / Reward, Banner,
   Native, Native full, …).

2. Nhập "Tên config (key)" — gõ tuỳ ý, hoặc chọn key gợi ý theo loại.

3. Điền thông số ở form bên trái:
   • Bật/tắt bằng ô tích ✓ (xanh = bật).
   • Native: chọn "type_layout" — bên dưới có bản XEM TRƯỚC bố cục quảng cáo.
     (Native full chỉ có layout "other".)
   • Bảng list_ads: "+ Thêm dòng" để thêm nhiều ad unit id; ✕ để xoá dòng.

TẠO JSON LẺ
• "⚡ Tạo JSON": xem JSON của riêng config đang mở ở khung bên phải.
  Rồi "Copy" hoặc "Lưu file..." nếu cần.

GỘP NHIỀU CONFIG → 1 FILE (import thẳng vào Remote Config)
• "➕ Thêm vào bộ": đưa config hiện tại vào "Bộ config gộp".

SỬA / CẬP NHẬT 1 CONFIG ĐÃ CÓ
• BẤM 1 DÒNG trong danh sách bên phải → toàn bộ thông số của config đó
  được nạp lại vào form để chỉnh.
• Lúc này nút "➕ Thêm vào bộ" đổi thành "💾 Cập nhật":
    - Sửa xong bấm "💾 Cập nhật" → lưu đè lại vào bộ (JSON hiện luôn để đối chiếu).
    - Đổi ô "Tên config (key)" rồi Cập nhật = đổi tên config trong bộ.
    - Bấm "✕ Huỷ sửa" (hoặc đổi Loại quảng cáo) để quay về chế độ thêm mới.
• "⬇ Export Firebase...": xuất 1 file template Firebase Remote Config
  (parameters + valueType) để IMPORT THẲNG vào RC. "👁 Xem template" để
  xem trước đúng file sẽ xuất.
  Lưu ý: import template sẽ GHI ĐÈ toàn bộ parameter hiện có trên RC.

MẸO
• "👁 Xem gộp": xem JSON tổng của cả bộ.
• "↺ Reset form": dựng lại form của loại đang chọn.
• Bấm "❔ Hướng dẫn" ở góc phải trên để mở lại bảng này bất cứ lúc nào.
"""

    def show_guide(self):
        # đã mở lần đầu -> ghi marker để lần sau không tự bật
        try:
            open(self._guide_marker(), "w").close()
        except OSError:
            pass
        # đang mở thì đưa lên trước
        if getattr(self, "_guide_win", None) and self._guide_win.winfo_exists():
            self._guide_win.lift()
            return

        win = tk.Toplevel(self, bg=CARD)
        self._guide_win = win
        win.title("Hướng dẫn sử dụng")
        win.geometry("640x580")
        win.minsize(520, 420)
        win.transient(self)

        ttk.Label(win, text="Hướng dẫn sử dụng", style="CardSection.TLabel").pack(
            anchor="w", padx=18, pady=(16, 8))

        wrap = ttk.Frame(win, style="Card.TFrame")
        wrap.pack(fill="both", expand=True, padx=18)
        sb = ttk.Scrollbar(wrap, orient="vertical")
        txt = tk.Text(wrap, wrap="word", font=("", 11), bg=CARD, fg=TEXT,
                      relief="flat", padx=6, pady=4, highlightthickness=0,
                      yscrollcommand=sb.set)
        sb.config(command=txt.yview)
        sb.pack(side="right", fill="y")
        txt.pack(side="left", fill="both", expand=True)
        txt.insert("1.0", self.GUIDE_TEXT)
        txt.configure(state="disabled")

        btns = ttk.Frame(win, style="Card.TFrame")
        btns.pack(fill="x", padx=18, pady=14)
        ttk.Button(btns, text="Đã hiểu", style="Accent.TButton",
                   command=win.destroy).pack(side="right")


if __name__ == "__main__":
    App().mainloop()
