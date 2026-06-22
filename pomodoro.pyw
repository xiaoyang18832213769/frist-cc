"""
番茄钟 — 桌面应用版 (.pyw = 双击无控制台窗口)
依赖: Python 3.x (自带 tkinter)
双击 pomodoro.pyw 即可启动

v4.0 — 中国传统鲜艳配色、🍅 番茄图样、圆润可爱风格
"""

import tkinter as tk
import math
import json
import os
import threading
import time
import winsound
from datetime import date

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pomodoro_config.json")

# ═══════════════════════════════════════════
#  中国传统鲜艳配色主题系统 — 4 套 Design Token
# ═══════════════════════════════════════════

THEMES = {
    "cinnabar": {
        "name": "朱砂红",
        "work":       {"main": "#D9332A", "light": "#FFF0EF", "subtle": "#FFD6D2", "text": "#B81A14", "ring_bg": "#FFE0DD"},
        "shortBreak": {"main": "#1CA363", "light": "#EDF9F3", "subtle": "#C8F0DB", "text": "#147A48", "ring_bg": "#D4F0E2"},
        "longBreak":  {"main": "#3B6FF5", "light": "#EEF3FF", "subtle": "#D3DFFF", "text": "#1F4FC8", "ring_bg": "#DDE6FF"},
        "bg":         "#FFF9F8",
        "card":       "#FFFFFF",
        "text":       "#3D1F1A",
        "text_secondary": "#8A6E68",
        "muted":      "#B8958D",
        "border":     "#F0DDD6",
        "surface":    "#FFFCFB",
        "btn_secondary": "#FFF0ED",
        "shadow_light": "#F0DFD8",
        "shadow_deep":  "#E0C8BD",
        "accent":     "#D9332A",
    },
    "crabapple": {
        "name": "海棠红",
        "work":       {"main": "#E8385A", "light": "#FFF0F4", "subtle": "#FFD3DE", "text": "#C41E40", "ring_bg": "#FFDEE6"},
        "shortBreak": {"main": "#20A87A", "light": "#EDF9F5", "subtle": "#C6F0E2", "text": "#15805C", "ring_bg": "#D2F0E5"},
        "longBreak":  {"main": "#5B7FF5", "light": "#EFF3FF", "subtle": "#D6E0FF", "text": "#3A5ED0", "ring_bg": "#E0E7FF"},
        "bg":         "#FFFAFB",
        "card":       "#FFFFFF",
        "text":       "#3D1F28",
        "text_secondary": "#8A6A74",
        "muted":      "#B8959C",
        "border":     "#F0DDE2",
        "surface":    "#FFFCFD",
        "btn_secondary": "#FFF0F3",
        "shadow_light": "#F0E0E5",
        "shadow_deep":  "#E0C8D0",
        "accent":     "#E8385A",
    },
    "jade": {
        "name": "翠微绿",
        "work":       {"main": "#1DA068", "light": "#EDF9F3", "subtle": "#C8F0DD", "text": "#127A4D", "ring_bg": "#D2F0E2"},
        "shortBreak": {"main": "#E8982E", "light": "#FFF7ED", "subtle": "#FFE8CC", "text": "#C07818", "ring_bg": "#FFE8D0"},
        "longBreak":  {"main": "#4B8AF0", "light": "#EEF4FF", "subtle": "#D2E2FF", "text": "#2C68D0", "ring_bg": "#DCE8FF"},
        "bg":         "#F7FCF9",
        "card":       "#FFFFFF",
        "text":       "#1F3D2E",
        "text_secondary": "#6A8A78",
        "muted":      "#95B5A2",
        "border":     "#DDF0E5",
        "surface":    "#F9FDFB",
        "btn_secondary": "#EDF7F1",
        "shadow_light": "#E0F0E8",
        "shadow_deep":  "#C8DED2",
        "accent":     "#1DA068",
    },
    "glaze": {
        "name": "琉璃蓝",
        "work":       {"main": "#4B70F0", "light": "#EEF2FF", "subtle": "#D3DDFF", "text": "#2C50D0", "ring_bg": "#DDE5FF"},
        "shortBreak": {"main": "#20A870", "light": "#EDF9F4", "subtle": "#C6F0DF", "text": "#148058", "ring_bg": "#D2F0E3"},
        "longBreak":  {"main": "#E8783A", "light": "#FFF5EE", "subtle": "#FFE3D0", "text": "#C0581E", "ring_bg": "#FFE5D5"},
        "bg":         "#F7F9FD",
        "card":       "#FFFFFF",
        "text":       "#1F2B3D",
        "text_secondary": "#6A758A",
        "muted":      "#95A0B5",
        "border":     "#DDE3F0",
        "surface":    "#F9FBFE",
        "btn_secondary": "#EDF1F7",
        "shadow_light": "#E0E5F0",
        "shadow_deep":  "#C8D0DE",
        "accent":     "#4B70F0",
    },
}

# ═══════════════════════════════════════════
#  辅助函数
# ═══════════════════════════════════════════

def hex_to_rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

def rgb_to_hex(r, g, b):
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

def lerp_color(c1, c2, t):
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return rgb_to_hex(
        r1 + (r2 - r1) * t,
        g1 + (g2 - g1) * t,
        b1 + (b2 - b1) * t,
    )

def draw_round_rect(canvas, x1, y1, x2, y2, r, fill="white", outline=None, width=1, tags=None):
    """在 Canvas 上绘制圆角矩形。"""
    kw_fill = {"fill": fill, "outline": ""}
    opts = {"tags": tags} if tags else {}

    # ── 填充层 ──
    canvas.create_arc(x1, y1, x1 + 2*r, y1 + 2*r,
               start=90, extent=90, style="pieslice", **kw_fill, **opts)
    canvas.create_arc(x2 - 2*r, y1, x2, y1 + 2*r,
               start=0, extent=90, style="pieslice", **kw_fill, **opts)
    canvas.create_arc(x1, y2 - 2*r, x1 + 2*r, y2,
               start=180, extent=90, style="pieslice", **kw_fill, **opts)
    canvas.create_arc(x2 - 2*r, y2 - 2*r, x2, y2,
               start=270, extent=90, style="pieslice", **kw_fill, **opts)
    canvas.create_rectangle(x1 + r, y1, x2 - r, y2, **kw_fill, **opts)
    canvas.create_rectangle(x1, y1 + r, x2, y2 - r, **kw_fill, **opts)

    # ── 描边层 ──
    if outline and width > 0:
        kw_line = {"fill": outline, "width": width}
        canvas.create_line(x1 + r, y1, x2 - r, y1, **kw_line, **opts)
        canvas.create_line(x1 + r, y2, x2 - r, y2, **kw_line, **opts)
        canvas.create_line(x1, y1 + r, x1, y2 - r, **kw_line, **opts)
        canvas.create_line(x2, y1 + r, x2, y2 - r, **kw_line, **opts)
        canvas.create_arc(x1, y1, x1 + 2*r, y1 + 2*r,
                   start=90, extent=90, style="arc", outline=outline, width=width, **opts)
        canvas.create_arc(x2 - 2*r, y1, x2, y1 + 2*r,
                   start=0, extent=90, style="arc", outline=outline, width=width, **opts)
        canvas.create_arc(x1, y2 - 2*r, x1 + 2*r, y2,
                   start=180, extent=90, style="arc", outline=outline, width=width, **opts)
        canvas.create_arc(x2 - 2*r, y2 - 2*r, x2, y2,
                   start=270, extent=90, style="arc", outline=outline, width=width, **opts)

# ═══════════════════════════════════════════
#  iOS 风格 Toggle 开关
# ═══════════════════════════════════════════

class ToggleSwitch(tk.Canvas):
    def __init__(self, parent, boolean_var, on_color="#D9332A", **kw):
        bg = kw.pop("bg", parent["bg"] if hasattr(parent, "cget") else "#FFFFFF")
        tk.Canvas.__init__(self, parent, width=44, height=26,
                          bg=bg, highlightthickness=0, cursor="hand2", **kw)
        self.var = boolean_var
        self.on_color = on_color
        self.bind("<Button-1>", self._toggle)
        self._draw()

    def _toggle(self, e=None):
        self.var.set(not self.var.get())
        self._draw()
        self.event_generate("<<ToggleChanged>>")

    def set_on_color(self, color):
        self.on_color = color
        self._draw()

    def _draw(self):
        self.delete("all")
        on = self.var.get()
        track = self.on_color if on else "#CCCCCC"
        self._round_rect(0, 0, 44, 26, 13, fill=track)
        kx = 22 if on else 4
        self.create_oval(kx, 3, kx + 20, 23, fill="#FFFFFF", outline="")

    def _round_rect(self, x1, y1, x2, y2, r, **kw):
        self.create_oval(x1, y1, x1 + 2*r, y1 + 2*r, **kw)
        self.create_oval(x2 - 2*r, y1, x2, y1 + 2*r, **kw)
        self.create_oval(x1, y2 - 2*r, x1 + 2*r, y2, **kw)
        self.create_oval(x2 - 2*r, y2 - 2*r, x2, y2, **kw)
        self.create_rectangle(x1 + r, y1, x2 - r, y2, **kw)
        self.create_rectangle(x1, y1 + r, x2, y2 - r, **kw)

# ═══════════════════════════════════════════
#  主应用
# ═══════════════════════════════════════════

class PomodoroApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("番茄钟")
        self.root.geometry("380x540")
        self.root.resizable(False, False)

        self.cfg = {
            "work": 25, "short": 5, "long": 15, "interval": 4,
            "sound": True, "topmost": True, "theme": "cinnabar",
        }
        self.theme_id = "cinnabar"
        self.mode = "work"
        self.running = False
        self.total_sec = 25 * 60
        self.remain = 25 * 60
        self.cycle = 0
        self.today = 0
        self.timer_id = None
        self._pulse_on = False
        self._pulse_id = None
        self._panel_anim_id = None

        self.load_cfg()
        self.load_today()
        self.root.wm_attributes("-topmost", self.cfg["topmost"])

        self.build_ui()
        self.apply_theme()
        self.update_all()

        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        self.root.geometry(f"+{sw - 400}+40")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind_keys()

    # ── 主题管理 ────────────────────────────────
    def get_theme(self):
        tid = self.theme_id
        if tid not in THEMES:
            tid = "cinnabar"
        return THEMES[tid]

    def apply_theme(self, animate=False):
        th = self.get_theme()
        phase = th[self.mode]

        # 根窗口背景
        self.root.configure(bg=th["bg"])

        # ── 阴影画布：重绘圆角矩形 ──
        for canvas, color in [(self._shadow_cv1, th["shadow_light"]),
                               (self._shadow_cv2, th["shadow_deep"])]:
            canvas.configure(bg=th["bg"])
            canvas.delete("all")
            draw_round_rect(canvas, 1, 1, 359, 519, 28, fill=color)

        # ── 卡片画布：重绘圆角背景 ──
        self.card.delete("card_bg")
        draw_round_rect(self.card, 1, 1, 359, 519, 28,
                       fill=th["card"], outline=th["border"], width=1,
                       tags="card_bg")
        self.card.tag_lower("card_bg")

        # ── 模式标签 ──
        self.lbl_mode.configure(bg=phase["light"], fg=phase["text"])

        # ── 提示 & 统计 ──
        self.lbl_hint.configure(fg=th["text_secondary"], bg=th["card"])
        self.lbl_stats.configure(fg=th["text_secondary"], bg=th["card"])

        # ── 环形画布 ──
        self.ring_cv.configure(bg=th["card"])
        self.ring_cv.itemconfig("time_text", fill=th["text"])
        self.ring_cv.itemconfig("unit_text", fill=th["text_secondary"])

        # ── 番茄进度 Frame ──
        self._tomato_frame.configure(bg=th["card"])
        self._refresh_tomato_labels()

        # ── 主按钮 ──
        self.btn_play.configure(
            bg=phase["main"], fg="white",
            activebackground=phase["text"], activeforeground="white",
            highlightbackground=phase["text"],
        )

        # ── 次要按钮 ──
        for btn in (self.btn_reset, self.btn_skip):
            btn.configure(
                bg=th["btn_secondary"], fg=th["muted"],
                activebackground=th["border"],
                highlightbackground=th["shadow_light"],
            )

        # ── 设置齿轮 ──
        self.btn_cog.configure(
            bg=th["card"], fg=th["muted"],
            activebackground=th["btn_secondary"],
        )

        # ── 设置面板 ──
        self.panel.configure(bg=th["surface"], highlightbackground=th["border"])
        self.panel_content.configure(bg=th["surface"])
        self.panel_canvas.configure(bg=th["surface"])
        for child in self.panel_content.winfo_children():
            if isinstance(child, tk.Label):
                try:
                    font_str = child.cget("font") or ""
                    if "bold" in str(font_str):
                        child.configure(bg=th["surface"], fg=th["text"])
                    else:
                        child.configure(bg=th["surface"], fg=th["text_secondary"])
                except Exception:
                    pass
            elif isinstance(child, tk.Spinbox):
                child.configure(
                    bg=th["card"], fg=th["text"],
                    buttonbackground=th["border"],
                )
            elif isinstance(child, ToggleSwitch):
                child.configure(bg=th["surface"])
                child.set_on_color(th["accent"])

        self._update_theme_swatches()

        # 重绘
        self.draw_ring()
        self._refresh_tomato_labels()

    def set_theme(self, theme_id):
        if theme_id not in THEMES:
            return
        self.theme_id = theme_id
        self.cfg["theme"] = theme_id
        self.save_cfg()
        self.apply_theme()
        self.update_mode()

    def _update_theme_swatches(self):
        th = self.get_theme()
        for tid, (sw_frame, sw_label, _) in self._theme_swatches.items():
            t = THEMES[tid]
            is_sel = (tid == self.theme_id)
            sw_frame.configure(
                bg=th["surface"],
                highlightbackground=t["accent"] if is_sel else th["border"],
                highlightthickness=2 if is_sel else 1,
            )
            sw_label.configure(
                text="✓" if is_sel else "",
                bg=t["work"]["main"], fg="white",
            )

    # ── 持久化 ────────────────────────────────────
    def load_cfg(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.cfg.update(json.load(f))
        except Exception:
            pass
        self.theme_id = self.cfg.get("theme", "cinnabar")
        if self.theme_id not in THEMES:
            self.theme_id = "cinnabar"
        # 兼容旧版 morandi 主题名
        if self.theme_id in ("misty_rose", "celadon", "dusk_blue", "warm_sand"):
            self.theme_id = "cinnabar"

    def save_cfg(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cfg, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def load_today(self):
        key = date.today().isoformat()
        if self.cfg.get("_today_key") != key:
            self.cfg["_today_key"] = key
            self.cfg["_today_count"] = 0
            self.today = 0
            self.save_cfg()
        else:
            self.today = self.cfg.get("_today_count", 0)

    def save_today(self):
        self.cfg["_today_key"] = date.today().isoformat()
        self.cfg["_today_count"] = self.today
        self.save_cfg()

    # ── UI 构建 ────────────────────────────────────
    def build_ui(self):
        th = self.get_theme()
        CW = 360   # 卡片宽度
        CH = 520   # 卡片高度
        CR = 28    # 圆角半径（更圆润）

        # ── 阴影画布（2 层）──
        self._shadow_cv1 = tk.Canvas(self.root, width=CW, height=CH,
                                     bg=th["bg"], highlightthickness=0, bd=0)
        self._shadow_cv1.place(x=17, y=18)
        draw_round_rect(self._shadow_cv1, 1, 1, CW-1, CH-1, CR,
                       fill=th["shadow_light"])

        self._shadow_cv2 = tk.Canvas(self.root, width=CW, height=CH,
                                     bg=th["bg"], highlightthickness=0, bd=0)
        self._shadow_cv2.place(x=13, y=14)
        draw_round_rect(self._shadow_cv2, 1, 1, CW-1, CH-1, CR,
                       fill=th["shadow_deep"])

        # ── 主卡片画布 ──
        self.card = tk.Canvas(self.root, width=CW, height=CH,
                              bg=th["bg"], highlightthickness=0, bd=0)
        self.card.place(x=10, y=10)
        draw_round_rect(self.card, 1, 1, CW-1, CH-1, CR,
                       fill=th["card"], outline=th["border"], width=1,
                       tags="card_bg")

        # ═══ 以下所有控件放置于 card Canvas 上 ═══

        # ── 模式标签（胶囊 Badge）──
        self.lbl_mode = tk.Label(
            self.card, text="● 专注工作",
            font=("Microsoft YaHei UI", 12, "bold"),
            padx=18, pady=5,
            bg=th["work"]["light"], fg=th["work"]["text"],
        )
        self.card.create_window(180, 30, window=self.lbl_mode, anchor="center")

        # ── 进度提示 ──
        self.lbl_hint = tk.Label(
            self.card, text="第 1 / 4 个番茄",
            font=("Microsoft YaHei UI", 10),
            fg=th["text_secondary"], bg=th["card"],
        )
        self.card.create_window(180, 62, window=self.lbl_hint, anchor="center")

        # ── 环形进度画布（230x230）──
        self.ring_cv = tk.Canvas(
            self.card, width=230, height=230,
            bg=th["card"], highlightthickness=0,
        )
        self.card.create_window(180, 196, window=self.ring_cv, anchor="center")
        self.ring_cv.create_text(115, 98, text="25:00",
                                font=("Consolas", 50, "bold"),
                                fill=th["text"], anchor="center", tags="time_text")
        self.ring_cv.create_text(115, 142, text="分钟",
                                font=("Microsoft YaHei UI", 11),
                                fill=th["text_secondary"], anchor="center", tags="unit_text")

        # ── 番茄进度显示（🍅 emoji Frame）──
        self._tomato_frame = tk.Frame(self.card, bg=th["card"])
        self.card.create_window(180, 335, window=self._tomato_frame, anchor="center")
        self._tomato_labels = []
        self._build_tomato_labels()

        # ── 按钮行 ──
        btn_frame = tk.Frame(self.card, bg=th["card"])
        self.card.create_window(180, 390, window=btn_frame, anchor="center")

        # 重置
        self.btn_reset = tk.Button(
            btn_frame, text="↺", font=("Segoe UI", 14),
            width=3, height=1, cursor="hand2",
            relief="flat", bd=0,
            highlightthickness=2, highlightbackground=th["shadow_light"],
            bg=th["btn_secondary"], fg=th["muted"],
            activebackground=th["border"],
            command=self.reset,  # ← 修复：添加 command
        )
        self.btn_reset.pack(side="left", padx=10)

        # 主按钮
        self.btn_play = tk.Button(
            btn_frame, text="▶  开始",
            font=("Microsoft YaHei UI", 14, "bold"),
            relief="flat", bd=0, cursor="hand2",
            padx=30, pady=12,
            highlightthickness=2, highlightbackground=th["work"]["text"],
            bg=th["work"]["main"], fg="white",
            activebackground=th["work"]["text"], activeforeground="white",
            command=self.toggle,  # ← 修复：添加 command
        )
        self.btn_play.pack(side="left", padx=10)

        # 跳过
        self.btn_skip = tk.Button(
            btn_frame, text="⏭", font=("Segoe UI", 14),
            width=3, height=1, cursor="hand2",
            relief="flat", bd=0,
            highlightthickness=2, highlightbackground=th["shadow_light"],
            bg=th["btn_secondary"], fg=th["muted"],
            activebackground=th["border"],
            command=self.skip,  # ← 修复：添加 command
        )
        self.btn_skip.pack(side="left", padx=10)

        # ── 设置齿轮 ──
        self.btn_cog = tk.Button(
            self.card, text="⚙", font=("Segoe UI", 12),
            command=self.toggle_panel,
            relief="flat", bd=0, cursor="hand2",
            bg=th["card"], fg=th["muted"],
            activebackground=th["btn_secondary"],
            padx=8, pady=2,
        )
        self.card.create_window(180, 442, window=self.btn_cog, anchor="center")

        # ── 底部统计 ──
        self.lbl_stats = tk.Label(
            self.card, text="今日完成 0 个番茄",
            font=("Microsoft YaHei UI", 10),
            fg=th["text_secondary"], bg=th["card"],
        )
        self.card.create_window(180, 480, window=self.lbl_stats, anchor="center")

        # ── 工具提示 ──
        self._tooltip = tk.Label(
            self.root, text="", font=("Microsoft YaHei UI", 9),
            bg="#555555", fg="white", padx=8, pady=2,
        )
        self.btn_reset.bind("<Enter>", lambda e: self._show_tooltip(e, "重置 (R)"))
        self.btn_reset.bind("<Leave>", lambda e: self._tooltip.place_forget())
        self.btn_skip.bind("<Enter>", lambda e: self._show_tooltip(e, "跳过 (S)"))
        self.btn_skip.bind("<Leave>", lambda e: self._tooltip.place_forget())

        # ── 设置面板 ──
        self.panel = tk.Frame(
            self.root, bg=th["surface"],
            highlightthickness=1, highlightbackground=th["border"], bd=0,
        )
        self._make_panel()

    def _build_tomato_labels(self):
        """首次创建番茄 emoji Label（仅 build_ui 调用）"""
        th = self.get_theme()
        total = self.cfg["interval"]
        for i in range(total):
            lbl = tk.Label(
                self._tomato_frame,
                text="🍅",
                font=("Segoe UI Emoji", 18),
                bg=th["card"],
                fg=th["work"]["main"] if i < self.cycle else th["border"],
            )
            lbl.pack(side="left", padx=3)
            self._tomato_labels.append(lbl)

    def _refresh_tomato_labels(self):
        """丝滑更新番茄 emoji：仅在数量变化时重建，否则只改颜色"""
        th = self.get_theme()
        total = self.cfg["interval"]
        current = len(self._tomato_labels)

        # 数量变化时才重建
        if total != current:
            for w in self._tomato_labels:
                w.destroy()
            self._tomato_labels.clear()
            for i in range(total):
                lbl = tk.Label(
                    self._tomato_frame,
                    text="🍅",
                    font=("Segoe UI Emoji", 18),
                    bg=th["card"],
                    fg=th["work"]["main"] if i < self.cycle else th["border"],
                )
                lbl.pack(side="left", padx=3)
                self._tomato_labels.append(lbl)
        else:
            # 仅更新颜色（无销毁重建，无闪烁）
            for i, lbl in enumerate(self._tomato_labels):
                lbl.configure(
                    bg=th["card"],
                    fg=th["work"]["main"] if i < self.cycle else th["border"],
                )

    def _show_tooltip(self, event, text):
        self._tooltip.config(text=text)
        self._tooltip.place(x=event.x_root - self.root.winfo_x() + 10,
                           y=event.y_root - self.root.winfo_y() - 28)

    def _make_panel(self):
        th = self.get_theme()

        self.panel.grid_rowconfigure(0, weight=1)
        self.panel.grid_columnconfigure(0, weight=1)

        self.panel_canvas = tk.Canvas(
            self.panel, height=175,
            bg=th["surface"], highlightthickness=0,
        )
        self.panel_canvas.grid(row=0, column=0, sticky="nsew", padx=(4, 0), pady=4)

        self.panel_scrollbar = tk.Scrollbar(
            self.panel, orient="vertical",
            command=self.panel_canvas.yview,
        )
        self.panel_canvas.configure(yscrollcommand=self.panel_scrollbar.set)

        self.panel_content = tk.Frame(self.panel_canvas, bg=th["surface"])
        self.panel_content.bind(
            "<Configure>",
            lambda e: self.panel_canvas.configure(
                scrollregion=self.panel_canvas.bbox("all")),
        )
        self.panel_canvas.create_window((0, 0), window=self.panel_content, anchor="nw")

        def _on_mousewheel(event):
            self.panel_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.panel_canvas.bind("<Enter>",
            lambda e: self.panel_canvas.bind_all("<MouseWheel>", _on_mousewheel))
        self.panel_canvas.bind("<Leave>",
            lambda e: self.panel_canvas.unbind_all("<MouseWheel>"))

        # ── 计时 ──
        self._section_header(self.panel_content, "计时", 0)
        rows = [
            ("工作时间（分）", "work", 1, 120),
            ("短休息（分）", "short", 1, 30),
            ("长休息（分）", "long", 1, 60),
            ("长休间隔（个番茄）", "interval", 2, 10),
        ]
        for i, (label, key, lo, hi) in enumerate(rows):
            r = 1 + i
            tk.Label(self.panel_content, text=label,
                    font=("Microsoft YaHei UI", 10),
                    fg=th["text_secondary"], bg=th["surface"],
                    ).grid(row=r, column=0, sticky="w", padx=(16, 8), pady=4)
            var = tk.IntVar(value=self.cfg[key])
            sb = tk.Spinbox(self.panel_content, from_=lo, to=hi, textvariable=var,
                           width=6, font=("Microsoft YaHei UI", 10), justify="center",
                           relief="flat", bd=1, bg=th["card"],
                           buttonbackground=th["border"])
            sb.grid(row=r, column=1, sticky="e", padx=(8, 16), pady=4)
            sb.bind("<FocusOut>", lambda e, k=key, v=var, l=lo, h=hi: self._on_num(k, v, l, h))
            sb.bind("<Return>", lambda e, k=key, v=var, l=lo, h=hi: self._on_num(k, v, l, h))

        # ── 提醒 ──
        ts = 5
        self._section_header(self.panel_content, "提醒", ts)
        self._toggle_widgets = {}
        for j, (label, key) in enumerate([("提示音", "sound"), ("窗口置顶", "topmost")]):
            r = ts + 1 + j
            tk.Label(self.panel_content, text=label,
                    font=("Microsoft YaHei UI", 10),
                    fg=th["text_secondary"], bg=th["surface"],
                    ).grid(row=r, column=0, sticky="w", padx=(16, 8), pady=4)
            var = tk.BooleanVar(value=self.cfg[key])
            toggle = ToggleSwitch(self.panel_content, var,
                                 on_color=th["accent"], bg=th["surface"])
            toggle.grid(row=r, column=1, sticky="e", padx=(8, 16), pady=4)
            toggle.bind("<<ToggleChanged>>",
                       lambda e, k=key, v=var: self._on_toggle(k, v))
            self._toggle_widgets[key] = (toggle, var)

        # ── 外观 ──
        ath = ts + 3
        self._section_header(self.panel_content, "外观", ath)
        self._theme_swatches = {}
        sf = tk.Frame(self.panel_content, bg=th["surface"])
        sf.grid(row=ath + 1, column=0, columnspan=2, sticky="ew", padx=16, pady=8)
        sf.grid_columnconfigure((0, 1, 2, 3), weight=1)

        theme_ids = ["cinnabar", "crabapple", "jade", "glaze"]
        for idx, tid in enumerate(theme_ids):
            t = THEMES[tid]
            is_sel = (tid == self.theme_id)
            sw_frame = tk.Frame(sf, bg=th["surface"],
                               highlightthickness=2 if is_sel else 1,
                               highlightbackground=t["accent"] if is_sel else th["border"],
                               bd=0, cursor="hand2")
            sw_frame.grid(row=0, column=idx, padx=3, pady=2)
            sw_frame.bind("<Button-1>", lambda e, tid=tid: self.set_theme(tid))

            sw = tk.Label(sw_frame, text="✓" if is_sel else "",
                         font=("Segoe UI", 10, "bold"),
                         bg=t["work"]["main"], fg="white",
                         width=5, height=2, cursor="hand2")
            sw.pack()
            sw.bind("<Button-1>", lambda e, tid=tid: self.set_theme(tid))

            nl = tk.Label(sf, text=t["name"], font=("Microsoft YaHei UI", 8),
                         fg=th["muted"], bg=th["surface"])
            nl.grid(row=1, column=idx, padx=3)
            nl.bind("<Button-1>", lambda e, tid=tid: self.set_theme(tid))

            self._theme_swatches[tid] = (sw_frame, sw, nl)

        self.panel_content.grid_columnconfigure(0, weight=1)
        self.panel_content.grid_columnconfigure(1, weight=0)

    def _section_header(self, parent, text, row):
        th = self.get_theme()
        tk.Label(parent, text=f"  {text}",
                font=("Microsoft YaHei UI", 10, "bold"),
                fg=th["text"], bg=th["surface"], anchor="w",
                ).grid(row=row, column=0, columnspan=2, sticky="ew",
                      padx=16, pady=(10, 2))

    # ── 面板切换 ────────────────────────────────
    def _on_num(self, key, var, lo, hi):
        try:
            v = max(lo, min(hi, int(var.get())))
        except (ValueError, TypeError):
            v = self.cfg[key]
        var.set(v)
        self.cfg[key] = v
        self.save_cfg()
        if not self.running:
            if (key == "work" and self.mode == "work") or \
               (key == "short" and self.mode == "shortBreak") or \
               (key == "long" and self.mode == "longBreak"):
                self.set_phase_duration()
                self.update_all()
        if key == "interval":
            if self.cycle >= self.cfg["interval"]:
                self.cycle = 0
            self._refresh_tomato_labels()

    def _on_toggle(self, key, var):
        self.cfg[key] = var.get()
        self.save_cfg()
        if key == "topmost":
            self.root.wm_attributes("-topmost", self.cfg["topmost"])

    def toggle_panel(self):
        if self.panel.winfo_ismapped():
            self.panel.place_forget()
            self.panel_scrollbar.grid_forget()
            self._animate_height(540, "close")
        else:
            th = self.get_theme()
            self.panel.configure(
                bg=th["surface"], highlightbackground=th["border"])
            self.panel.place(x=10, y=542, width=360, height=175)
            self.panel_scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 4), pady=4)
            self._animate_height(725, "open")

    def _animate_height(self, target_h, direction):
        if self._panel_anim_id:
            self.root.after_cancel(self._panel_anim_id)
        current = int(self.root.geometry().split("x")[1].split("+")[0])
        if abs(current - target_h) < 4:
            self.root.geometry(f"380x{target_h}")
            self._panel_anim_id = None
            return
        new_h = current + (target_h - current) * 0.35
        self.root.geometry(f"380x{int(new_h)}")
        self._panel_anim_id = self.root.after(16,
            lambda: self._animate_height(target_h, direction))

    # ── 键盘 ────────────────────────────────────
    def bind_keys(self):
        self.root.bind("<space>", lambda e: self.toggle())
        self.root.bind("r", lambda e: self.reset())
        self.root.bind("s", lambda e: self.skip())
        self.root.bind("<Escape>", lambda e: self._esc_close())

    def _esc_close(self):
        if self.panel.winfo_ismapped():
            self.panel.place_forget()
            self.panel_scrollbar.grid_forget()
            self._animate_height(540, "close")

    # ── 环形进度绘制 ──────────────────────────────
    def draw_ring(self):
        self.ring_cv.delete("ring")
        th = self.get_theme()
        phase = th[self.mode]
        cx = cy = 115
        r = 94
        w = 10  # 更粗的进度环，更可爱

        pct = self.remain / self.total_sec if self.total_sec > 0 else 0
        extent = -360 * pct

        # 外光晕
        self.ring_cv.create_arc(
            cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4,
            outline=th["shadow_light"], width=w + 8, style="arc",
            start=90, extent=359.9, tags="ring",
        )
        # 背景环
        self.ring_cv.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            outline=phase["ring_bg"], width=w, style="arc",
            start=90, extent=359.9, tags="ring",
        )
        # 进度环（圆角端点）
        if pct > 0.001:
            self.ring_cv.create_arc(
                cx - r, cy - r, cx + r, cy + r,
                outline=phase["main"], width=w, style="arc",
                start=90, extent=extent, tags="ring",
            )

        # 端点指示器（小圆点）
        if 0.005 < pct < 0.995:
            angle_rad = 2 * math.pi * pct
            dot_x = cx + r * math.sin(angle_rad)
            dot_y = cy - r * math.cos(angle_rad)
            pulse_scale = 1.6 if (self._pulse_on and self.running) else 1.0
            dot_r = 6 * pulse_scale
            self.ring_cv.create_oval(
                dot_x - dot_r, dot_y - dot_r,
                dot_x + dot_r, dot_y + dot_r,
                fill=phase["main"], outline="", tags="ring",
            )

        # 确保文字在最上层
        self.ring_cv.tag_raise("time_text")
        self.ring_cv.tag_raise("unit_text")

    # ── 更新方法 ──────────────────────────────────
    def update_all(self):
        self.draw_ring()
        self._refresh_tomato_labels()
        self.update_time()
        self.update_mode()
        self.update_stats()
        self.update_title()

    def update_time(self):
        m, s = divmod(self.remain, 60)
        self.ring_cv.itemconfig("time_text", text=f"{m:02d}:{s:02d}")

    def update_mode(self):
        th = self.get_theme()
        phase = th[self.mode]

        labels = {"work": "● 专注工作", "shortBreak": "● 短休息", "longBreak": "● 长休息"}
        self.lbl_mode.config(text=labels[self.mode],
                            bg=phase["light"], fg=phase["text"])

        if self.mode == "work":
            self.lbl_hint.config(text=f"第 {self.cycle + 1} / {self.cfg['interval']} 个番茄")
        else:
            hints = {"shortBreak": "休息一下 ☕", "longBreak": "享受长休息 🌿"}
            self.lbl_hint.config(text=hints.get(self.mode, ""))

        unit_texts = {"work": "分钟", "shortBreak": "秒", "longBreak": "秒"}
        self.ring_cv.itemconfig("unit_text", text=unit_texts[self.mode])

        try:
            self.btn_play.configure(
                bg=phase["main"],
                activebackground=phase["text"],
                activeforeground="white",
                highlightbackground=phase["text"],
            )
        except Exception:
            pass

        if not self.running:
            self.btn_play.config(text="▶  开始")

    def update_stats(self):
        self.lbl_stats.config(text=f"今日完成 {self.today} 个番茄 🍅")

    def update_title(self):
        m, s = divmod(self.remain, 60)
        t = f"{m:02d}:{s:02d}"
        icon = "▶" if self.running else "⏸"
        lbls = {"work": "专注", "shortBreak": "休息", "longBreak": "长休"}
        self.root.title(f"{icon} {t} - {lbls[self.mode]} | 🍅 番茄钟")

    # ── 计时逻辑 ──────────────────────────────────
    def set_phase_duration(self):
        m = {"work": "work", "shortBreak": "short", "longBreak": "long"}
        self.total_sec = self.cfg[m[self.mode]] * 60
        self.remain = self.total_sec

    def tick(self):
        if self.remain <= 0:
            self.pause()
            self.finish_phase()
            return
        self.remain -= 1
        self.update_all()
        if 1 <= self.remain <= 5:
            self.pulse_ring()

    def play(self):
        if self.running:
            return
        self.running = True
        self.btn_play.config(text="⏸  暂停")
        self.update_title()
        self._tick()

    def pause(self):
        if not self.running:
            return
        self.running = False
        self.btn_play.config(text="▶  继续")
        self.update_title()
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self._stop_pulse()

    def toggle(self):
        self.pause() if self.running else self.play()

    def _tick(self):
        if not self.running:
            return
        self.tick()
        self.timer_id = self.root.after(1000, self._tick)

    def reset(self):
        self.pause()
        self.running = False
        self.remain = self.total_sec
        self.btn_play.config(text="▶  开始")
        self._stop_pulse()
        self.update_all()

    def skip(self):
        self.pause()
        self.remain = 0
        self.finish_phase()

    # ── 最后 5 秒 pulse ──────────────────────────
    def pulse_ring(self):
        if self._pulse_id is not None:
            return
        self._pulse_on = True
        self._do_pulse()

    def _do_pulse(self):
        if not self.running or self.remain > 5 or self.remain <= 0:
            self._stop_pulse()
            return
        self._pulse_on = not self._pulse_on
        self.draw_ring()
        self._pulse_id = self.root.after(500, self._do_pulse)

    def _stop_pulse(self):
        if self._pulse_id:
            self.root.after_cancel(self._pulse_id)
            self._pulse_id = None
        if self._pulse_on:
            self._pulse_on = False
            self.draw_ring()

    # ── 阶段结束 ──────────────────────────────────
    def finish_phase(self):
        self.beep()

        if self.mode == "work":
            self.today += 1
            self.cycle += 1
            self.save_today()
            self.mode = (
                "longBreak" if self.cycle >= self.cfg["interval"]
                else "shortBreak"
            )
        else:
            if self.mode == "longBreak":
                self.cycle = 0
            self.mode = "work"

        self._stop_pulse()
        self.set_phase_duration()
        self.running = False
        self.btn_play.config(text="▶  开始")
        # 丝滑过渡：先更新模式颜色，再重绘圆环
        self.update_mode()
        self.draw_ring()
        self._refresh_tomato_labels()
        self.update_time()
        self.update_stats()
        self.update_title()
        self.notify_window()

    # ── 声音（清脆三连音）──────────────────────────
    def beep(self):
        if not self.cfg["sound"]:
            return
        def _play():
            try:
                # 清脆上行三连音：C6 → E6 → G6，短促干净
                winsound.Beep(1047, 120)
                time.sleep(0.06)
                winsound.Beep(1319, 120)
                time.sleep(0.06)
                winsound.Beep(1568, 220)
            except Exception:
                try:
                    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
                except Exception:
                    pass
        threading.Thread(target=_play, daemon=True).start()

    # ── 丝滑窗口提醒（无闪烁）─────────────────────
    def notify_window(self):
        """温和提醒：卡片边框发光脉冲，不闪窗"""
        try:
            # 仅将窗口带到前台，不做 hide/show
            self.root.deiconify()
            self.root.lift()
            if self.cfg["topmost"]:
                self.root.wm_attributes("-topmost", True)
            self.root.focus_force()
            # 卡片边框发光脉冲
            self._glow_card_border()
        except Exception:
            pass

    def _glow_card_border(self):
        """卡片边框短暂高亮 → 渐隐回原色，替代整窗闪烁"""
        th = self.get_theme()
        phase = th[self.mode]
        highlight_color = phase["main"]

        def _step(steps_remain):
            if steps_remain <= 0:
                # 恢复默认边框
                self.card.delete("card_bg")
                draw_round_rect(self.card, 1, 1, 359, 519, 28,
                               fill=th["card"], outline=th["border"], width=1,
                               tags="card_bg")
                self.card.tag_lower("card_bg")
                return
            t = steps_remain / 6.0  # 0→1
            # 边框色在 highlight 和 border 之间插值
            edge = lerp_color(th["border"], highlight_color, t)
            w = 1 + int(2 * t)  # 1→3 px
            self.card.delete("card_bg")
            draw_round_rect(self.card, 1, 1, 359, 519, 28,
                           fill=th["card"], outline=edge, width=w,
                           tags="card_bg")
            self.card.tag_lower("card_bg")
            self.root.after(60, lambda: _step(steps_remain - 1))

        _step(6)  # 6 steps × 60ms = 360ms 总动画

    def on_close(self):
        self.pause()
        try:
            self.root.destroy()
        except Exception:
            pass


# ═══════════════════════════════════════════
#  入口
# ═══════════════════════════════════════════

if __name__ == "__main__":
    import traceback, sys
    ERR_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pomodoro_error.log")
    try:
        app = PomodoroApp()
        app.root.mainloop()
    except SystemExit:
        pass
    except Exception:
        try:
            with open(ERR_LOG, "w", encoding="utf-8") as f:
                f.write(f"番茄钟启动失败\n{'='*40}\n")
                f.write(traceback.format_exc())
        except Exception:
            pass
        try:
            import tkinter.messagebox as mb
            mb.showerror("番茄钟启动失败",
                        f"错误已写入：\n{ERR_LOG}\n\n"
                        f"请将该文件内容发给开发者。\n\n"
                        f"概要：{traceback.format_exc()[-300:]}")
        except Exception:
            try:
                desktop = os.path.join(os.path.expanduser("~"), "Desktop", "pomodoro_crash.txt")
                with open(desktop, "w", encoding="utf-8") as f:
                    f.write(traceback.format_exc())
            except Exception:
                pass
