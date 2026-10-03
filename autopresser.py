import tkinter as tk
from tkinter import ttk
import threading
import time
import pyautogui
from pynput import keyboard as pynput_keyboard

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = True

class AutoPresser:
    def __init__(self, root):
        self.root = root
        self.root.title("Maxer AutoPresser")
        self.root.geometry("440x400")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        self.pressing = False
        self.press_count = 0
        self.hotkey = "f6"
        self.target_key = "space"
        self.listening_hotkey = False
        self.listening_target = False
        self.listener = None

        self.build_ui()
        self.start_hotkey_listener()

    def build_ui(self):
        BG = "#1e1e2e"
        SURFACE = "#2a2a3e"
        ACCENT = "#7c3aed"
        TEXT = "#e2e8f0"
        MUTED = "#94a3b8"
        GREEN = "#22c55e"
        RED = "#ef4444"

        # Header
        header = tk.Frame(self.root, bg=SURFACE, pady=10)
        header.pack(fill="x")
        tk.Label(header, text="⌨️ Maxer AutoPresser", font=("Segoe UI", 14, "bold"), bg=SURFACE, fg=TEXT).pack(side="left", padx=14)
        self.status_label = tk.Label(header, text="● Detenido", font=("Segoe UI", 10, "bold"), bg=SURFACE, fg=GREEN)
        self.status_label.pack(side="right", padx=14)

        # Tecla a presionar
        sec1 = tk.LabelFrame(self.root, text=" ⌨ Tecla a presionar ", bg=BG, fg=MUTED, font=("Segoe UI", 9))
        sec1.pack(fill="x", padx=12, pady=(10,4))
        row1 = tk.Frame(sec1, bg=BG)
        row1.pack(fill="x", padx=8, pady=8)
        self.target_btn = tk.Button(row1, text="SPACE", font=("Segoe UI", 12, "bold"),
            bg=SURFACE, fg=ACCENT, relief="flat", padx=20, pady=8, cursor="hand2",
            command=self.start_listen_target)
        self.target_btn.pack(side="left")
        tk.Label(row1, text="  Haz clic para elegir la tecla", bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(side="left")

        # Intervalo
        sec2 = tk.LabelFrame(self.root, text=" ⏱ Intervalo ", bg=BG, fg=MUTED, font=("Segoe UI", 9))
        sec2.pack(fill="x", padx=12, pady=4)
        row2 = tk.Frame(sec2, bg=BG)
        row2.pack(fill="x", padx=8, pady=6)
        self.hours = self._spinbox(row2, "Horas", 0, 23)
        tk.Label(row2, text="h", bg=BG, fg=MUTED).pack(side="left", padx=(0,6))
        self.mins = self._spinbox(row2, "Mins", 0, 59)
        tk.Label(row2, text="m", bg=BG, fg=MUTED).pack(side="left", padx=(0,6))
        self.secs = self._spinbox(row2, "Segs", 0, 59)
        tk.Label(row2, text="s", bg=BG, fg=MUTED).pack(side="left", padx=(0,6))
        self.ms = self._spinbox(row2, "Ms", 1, 9999, width=6, default=100)
        tk.Label(row2, text="ms", bg=BG, fg=MUTED).pack(side="left")

        # Repeticion
        sec3 = tk.LabelFrame(self.root, text=" 🔁 Repetición ", bg=BG, fg=MUTED, font=("Segoe UI", 9))
        sec3.pack(fill="x", padx=12, pady=4)
        self.repeat_mode = tk.StringVar(value="infinite")
        r1 = tk.Frame(sec3, bg=BG); r1.pack(anchor="w", padx=8, pady=(6,2))
        tk.Radiobutton(r1, text="Repetir", variable=self.repeat_mode, value="times",
            bg=BG, fg=TEXT, selectcolor=BG, activebackground=BG).pack(side="left")
        self.repeat_times = tk.Spinbox(r1, from_=1, to=99999, width=6,
            bg=SURFACE, fg=TEXT, insertbackground=TEXT, buttonbackground=SURFACE)
        self.repeat_times.pack(side="left", padx=4)
        self.repeat_times.delete(0,"end"); self.repeat_times.insert(0,"10")
        tk.Label(r1, text="veces", bg=BG, fg=MUTED, font=("Segoe UI",9)).pack(side="left")
        tk.Radiobutton(sec3, text="Hasta detener", variable=self.repeat_mode, value="infinite",
            bg=BG, fg=TEXT, selectcolor=BG, activebackground=BG).pack(anchor="w", padx=8, pady=(0,8))

        # Hotkey
        sec4 = tk.LabelFrame(self.root, text=" 🎮 Tecla de inicio/parada ", bg=BG, fg=MUTED, font=("Segoe UI", 9))
        sec4.pack(fill="x", padx=12, pady=4)
        hrow = tk.Frame(sec4, bg=BG); hrow.pack(fill="x", padx=8, pady=6)
        self.hotkey_btn = tk.Button(hrow, text="F6", font=("Segoe UI", 10, "bold"),
            bg=SURFACE, fg=ACCENT, relief="flat", padx=14, pady=4, cursor="hand2",
            command=self.start_listen_hotkey)
        self.hotkey_btn.pack(side="left")
        tk.Label(hrow, text="  Haz clic para cambiar", bg=BG, fg=MUTED, font=("Segoe UI",9)).pack(side="left")

        # Botones
        brow = tk.Frame(self.root, bg=BG); brow.pack(fill="x", padx=12, pady=6)
        self.btn_start = tk.Button(brow, text="▶ Iniciar (F6)", font=("Segoe UI",12,"bold"),
            bg=GREEN, fg="white", relief="flat", cursor="hand2", pady=10, command=self.start_pressing)
        self.btn_start.pack(side="left", fill="x", expand=True, padx=(0,6))
        self.btn_stop = tk.Button(brow, text="■ Detener (F6)", font=("Segoe UI",12,"bold"),
            bg=RED, fg="white", relief="flat", cursor="hand2", pady=10, command=self.stop_pressing, state="disabled")
        self.btn_stop.pack(side="left", fill="x", expand=True)

        self.counter_label = tk.Label(self.root, text="Pulsaciones: 0", bg=BG, fg=MUTED, font=("Segoe UI",9))
        self.counter_label.pack()
        tk.Label(self.root, text="Maxer AutoPresser v1.0.0 — Maxer Dev", bg=BG, fg="#44445a", font=("Segoe UI",8)).pack(pady=4)

    def _spinbox(self, parent, label, from_, to, width=5, default=0):
        f = tk.Frame(parent, bg="#1e1e2e"); f.pack(side="left", padx=2)
        tk.Label(f, text=label, bg="#1e1e2e", fg="#94a3b8", font=("Segoe UI",8)).pack()
        sb = tk.Spinbox(f, from_=from_, to=to, width=width, bg="#2a2a3e", fg="#e2e8f0",
            insertbackground="#e2e8f0", buttonbackground="#2a2a3e")
        sb.pack(); sb.delete(0,"end"); sb.insert(0, str(default))
        return sb

    def get_interval(self):
        h = int(self.hours.get() or 0)
        m = int(self.mins.get() or 0)
        s = int(self.secs.get() or 0)
        ms = int(self.ms.get() or 1)
        total = h*3600 + m*60 + s + ms/1000
        return max(0.001, total)

    def start_listen_target(self):
        self.listening_target = True
        self.target_btn.config(text="Presiona una tecla...", fg="#ef4444")
        self.root.bind("<Key>", self.capture_target)
        self.root.focus_force()

    def capture_target(self, event):
        if not self.listening_target: return
        self.target_key = event.keysym.lower()
        self.target_btn.config(text=event.keysym.upper(), fg="#7c3aed")
        self.listening_target = False
        self.root.unbind("<Key>")

    def start_listen_hotkey(self):
        self.listening_hotkey = True
        self.hotkey_btn.config(text="Presiona una tecla...", fg="#ef4444")
        self.root.bind("<Key>", self.capture_hotkey)
        self.root.focus_force()

    def capture_hotkey(self, event):
        if not self.listening_hotkey: return
        self.hotkey = event.keysym.lower()
        self.hotkey_btn.config(text=event.keysym.upper(), fg="#7c3aed")
        self.listening_hotkey = False
        self.root.unbind("<Key>")
        self.btn_start.config(text=f"▶ Iniciar ({event.keysym.upper()})")
        self.btn_stop.config(text=f"■ Detener ({event.keysym.upper()})")
        self.restart_hotkey_listener()

    def press_action(self):
        repeat_mode = self.repeat_mode.get()
        max_times = int(self.repeat_times.get() or 1)
        count = 0
        while self.pressing:
            try:
                pyautogui.press(self.target_key)
            except:
                pass
            self.press_count += 1
            count += 1
            self.root.after(0, lambda: self.counter_label.config(text=f"Pulsaciones: {self.press_count}"))
            if repeat_mode == "times" and count >= max_times:
                self.root.after(0, self.stop_pressing)
                break
            time.sleep(self.get_interval())

    def start_pressing(self):
        if self.pressing: return
        self.pressing = True
        self.press_count = 0
        self.update_ui(True)
        threading.Thread(target=self.press_action, daemon=True).start()

    def stop_pressing(self):
        self.pressing = False
        self.update_ui(False)

    def update_ui(self, active):
        if active:
            self.status_label.config(text="● Activo", fg="#ef4444")
            self.btn_start.config(state="disabled")
            self.btn_stop.config(state="normal")
        else:
            self.status_label.config(text="● Detenido", fg="#22c55e")
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")

    def start_hotkey_listener(self):
        def on_press(key):
            try:
                k = key.name if hasattr(key, 'name') else key.char
                if k and k.lower() == self.hotkey.lower():
                    if self.pressing:
                        self.root.after(0, self.stop_pressing)
                    else:
                        self.root.after(0, self.start_pressing)
            except: pass
        self.listener = pynput_keyboard.Listener(on_press=on_press)
        self.listener.start()

    def restart_hotkey_listener(self):
        if self.listener:
            self.listener.stop()
        self.start_hotkey_listener()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoPresser(root)
    root.mainloop()
