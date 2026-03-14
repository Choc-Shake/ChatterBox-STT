import sys
import json
import threading
import requests
import keyboard
import pyaudio
import pyautogui
import pyperclip
import winsound
import numpy as np
import wave
import io
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, 
                             QGraphicsDropShadowEffect, QSystemTrayIcon, QMenu, QDialog,
                             QFormLayout, QLineEdit, QPushButton, QCheckBox, 
                             QTabWidget, QStackedWidget, QFrame, QTextEdit)
from PyQt6.QtCore import (Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, 
                          QEasingCurve, QPoint, QParallelAnimationGroup, pyqtProperty)
from PyQt6.QtGui import QIcon, QPainter, QColor, QFont, QAction, QPixmap, QPainterPath, QPen, QBrush

# Attempt to smooth out DPI issues for Windows
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

# === CONFIG MANAGER ===
class ConfigManager:
    def __init__(self):
        self.filepath = 'config.json'
        self.load()

    def load(self):
        try:
            with open(self.filepath, 'r') as f:
                self.config = json.load(f)
        except Exception:
            self.config = {}
        
        self.hotkey = self.config.get('hotkey', 'ctrl+alt+space')
        self.enabled = self.config.get('enabled', True)
        self.casaos_ip = self.config.get('casaos_ip', '100.124.112.96')
        self.mode = self.config.get('mode', 'POLISHED') # 'FILTERED' or 'POLISHED'
        self.ollama_model = self.config.get('ollama_model', 'qwen2.5:0.5b')
        self.filtered_prompt = self.config.get('filtered_prompt', 'Remove non-lexical fillers (um, ah, stutters). Output ONLY the verbatim text:')
        self.polished_prompt = self.config.get('polished_prompt', 'Fix grammar and remove filler words (um, ah). Output ONLY the corrected text:')

    def save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.config, f, indent=4)
        
    def get_whisper_url(self):
        return f"http://{self.casaos_ip}:8001/v1/audio/transcriptions"
        
    def get_ollama_url(self):
        return f"http://{self.casaos_ip}:11435/api/generate"

    def get_current_prompt(self):
        return self.polished_prompt if self.mode == 'POLISHED' else self.filtered_prompt

    def update(self, key, value):
        self.config[key] = value
        setattr(self, key, value)
        self.save()

APP_CONFIG = ConfigManager()
CHUNK, FORMAT, CHANNELS, RATE = 1024, pyaudio.paInt16, 1, 16000

# === CUSTOM PAINTER WIDGETS ===

class SpinnerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        
    def rotate(self):
        self.angle = (self.angle + 30) % 360
        self.update()

    def start(self): self.timer.start(50)
    def stop(self): self.timer.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(8, 8)
        painter.rotate(self.angle)
        
        pen = QPen(QColor(212, 175, 55, 30), 2)
        painter.setPen(pen)
        painter.drawEllipse(-7, -7, 14, 14)
        
        pen.setColor(QColor("#D4AF37"))
        painter.setPen(pen)
        painter.drawArc(-7, -7, 14, 14, 0 * 16, 90 * 16)

class WaveformWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24)
        self.bars = [4, 4, 4, 4]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_bars)
        
    def update_bars(self):
        self.bars = [np.random.randint(4, 18) for _ in range(4)]
        self.update()

    def start(self): self.timer.start(80)
    def stop(self): 
        self.timer.stop()
        self.bars = [4, 4, 4, 4]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#D4AF37"))
        
        spacing = 4
        bar_width = 2
        for i, h in enumerate(self.bars):
            x = i * (bar_width + spacing)
            y = (self.height() - h) // 2
            painter.drawRoundedRect(x, y, bar_width, h, 1, 1)

class SVGIconWidget(QWidget):
    def __init__(self, mode="CUBE", size=28, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.mode = mode # CUBE, STOP, CHECK
        self._color = QColor(0, 0, 0)

    def set_mode(self, mode, color=None):
        self.mode = mode
        if color: self._color = QColor(color)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        s = self.width() / 24.0 # Base on 24x24 viewBox
        painter.scale(s, s)
        
        if self.mode == "CUBE":
            # <path d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3z"/>
            path = QPainterPath()
            path.moveTo(12, 3)
            path.lineTo(20, 7.5)
            path.lineTo(20, 16.5)
            path.lineTo(12, 21)
            path.lineTo(4, 16.5)
            path.lineTo(4, 7.5)
            path.closeSubpath()
            
            painter.setPen(QPen(self._color, 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawPath(path)
            
            # <line x1="12" y1="9" x2="12" y2="15" /> ...
            painter.drawLine(12, 9, 12, 15)
            painter.drawLine(8, 10, 8, 14) # Rounded integers for cleaner rendering
            painter.drawLine(16, 10, 16, 14)
            
        elif self.mode == "STOP":
            # <rect x="6" y="6" width="12" height="12" rx="1"></rect>
            painter.setBrush(QBrush(self._color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(6, 6, 12, 12, 1, 1)
            
        elif self.mode == "CHECK":
            # <polyline points="20 6 9 17 4 12" />
            painter.setPen(QPen(QColor("#D4AF37"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawLine(4, 12, 9, 17)
            painter.drawLine(9, 17, 20, 6)

# === THREADS ===

class AudioThread(QThread):
    finished = pyqtSignal(str)
    level = pyqtSignal(float)
    def __init__(self):
        super().__init__()
        self.active = False
    def run(self):
        self.active = True
        frames = []
        p = pyaudio.PyAudio()
        try:
            stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            while self.active:
                data = stream.read(CHUNK, False)
                frames.append(data)
            stream.stop_stream(); stream.close(); p.terminate()
            
            wav_io = io.BytesIO()
            with wave.open(wav_io, 'wb') as wf:
                wf.setnchannels(CHANNELS); wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE); wf.writeframes(b''.join(frames))
            
            res = requests.post(APP_CONFIG.get_whisper_url(), files={'file': ('audio.wav', wav_io.getvalue())}, data={'model': 'tiny.en'}, timeout=30)
            self.finished.emit(res.json().get('text', '').strip())
        except: self.finished.emit("ERROR")

class OllamaThread(QThread):
    finished = pyqtSignal(str)
    def __init__(self, text):
        super().__init__(); self.text = text
    def run(self):
        try:
            res = requests.post(APP_CONFIG.get_ollama_url(), json={"model": APP_CONFIG.ollama_model, "prompt": f"{APP_CONFIG.get_current_prompt()} {self.text}", "stream": False}, timeout=15)
            self.finished.emit(res.json().get('response', self.text).strip())
        except: self.finished.emit(self.text)

# === DIALOGS ===

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chatterbox Settings")
        self.setFixedSize(500, 480)
        self.setStyleSheet("""
            QDialog { background-color: #0A0A0A; color: #FFFFFF; font-family: 'Segoe UI'; }
            QTabWidget::pane { border: 1px solid #222; background: #0A0A0A; border-radius: 8px; margin-top: -1px; }
            QTabBar::tab { background: #111; color: #666; padding: 12px 24px; border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 4px; border: 1px solid #222; border-bottom: none; }
            QTabBar::tab:selected { background: #D4AF37; color: #000; font-weight: bold; border-color: #D4AF37; }
            QLabel { color: #888; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; }
            QLineEdit, QTextEdit { background-color: #050505; color: #D4AF37; border: 1px solid #1A1A1A; padding: 10px; border-radius: 6px; font-family: 'Consolas'; }
            QPushButton { background-color: #D4AF37; color: #000; font-weight: bold; border: none; padding: 12px; border-radius: 8px; text-transform: uppercase; letter-spacing: 0.1em; }
            QPushButton:hover { background-color: #E6C252; }
            QCheckBox { color: #FFFFFF; spacing: 12px; font-weight: bold; }
        """)
        
        l = QVBoxLayout(self); l.setContentsMargins(20, 20, 20, 20); l.setSpacing(20)
        self.tabs = QTabWidget(); l.addWidget(self.tabs)
        
        # General
        g_w = QWidget(); g_l = QFormLayout(g_w); g_l.setContentsMargins(25, 25, 25, 25); g_l.setSpacing(15)
        self.en_cb = QCheckBox("Enable Hotkey"); self.en_cb.setChecked(APP_CONFIG.enabled); g_l.addRow(self.en_cb)
        self.hk_i = QLineEdit(APP_CONFIG.hotkey); g_l.addRow("Hotkey", self.hk_i)
        self.ip_i = QLineEdit(APP_CONFIG.casaos_ip); g_l.addRow("CasaOS IP", self.ip_i)
        self.md_btn = QPushButton(APP_CONFIG.mode); self.md_btn.setFixedWidth(120); self.md_btn.clicked.connect(self.t_mode); g_l.addRow("Mode", self.md_btn)
        self.tabs.addTab(g_w, "General")
        
        # Prompts
        p_w = QWidget(); p_l = QVBoxLayout(p_w); p_l.setContentsMargins(20, 20, 20, 20); p_l.setSpacing(10)
        p_l.addWidget(QLabel("Filtered Mode Prompt")); self.f_e = QTextEdit(); self.f_e.setPlainText(APP_CONFIG.filtered_prompt); p_l.addWidget(self.f_e)
        p_l.addWidget(QLabel("Polished Mode Prompt")); self.p_e = QTextEdit(); self.p_e.setPlainText(APP_CONFIG.polished_prompt); p_l.addWidget(self.p_e)
        self.tabs.addTab(p_w, "Prompts")
        
        b = QHBoxLayout(); l.addLayout(b)
        self.st = QLabel("checking..."); b.addWidget(self.st)
        save = QPushButton("Save && Apply"); save.clicked.connect(self.accept); b.addWidget(save)
        
        threading.Thread(target=self.chk, daemon=True).start()

    def t_mode(self):
        APP_CONFIG.mode = "FILTERED" if APP_CONFIG.mode == "POLISHED" else "POLISHED"
        self.md_btn.setText(APP_CONFIG.mode)

    def chk(self):
        try:
            requests.get(f"http://{self.ip_i.text()}:8001/", timeout=2)
            self.st.setText("● Server online"); self.st.setStyleSheet("color: #2E8B57;")
        except: self.st.setText("○ Server offline"); self.st.setStyleSheet("color: #FF5555;")

    def save(self):
        APP_CONFIG.update('enabled', self.en_cb.isChecked())
        APP_CONFIG.update('hotkey', self.hk_i.text().lower())
        APP_CONFIG.update('casaos_ip', self.ip_i.text())
        APP_CONFIG.update('mode', APP_CONFIG.mode)
        APP_CONFIG.update('filtered_prompt', self.f_e.toPlainText())
        APP_CONFIG.update('polished_prompt', self.p_e.toPlainText())

# === MAIN PILL ===

class MorphPill(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("pill")
        self._w = 260
        
        l = QHBoxLayout(self)
        l.setContentsMargins(6, 6, 28, 6) # exact HTML padding
        l.setSpacing(18) # exact HTML gap
        
        self.btn = QFrame()
        self.btn.setFixedSize(52, 52)
        self.btn.setStyleSheet("background-color: #D4AF37; border-radius: 26px;")
        bl = QVBoxLayout(self.btn); bl.setContentsMargins(0, 0, 0, 0); bl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon = SVGIconWidget("CUBE", 28); bl.addWidget(self.icon)
        l.addWidget(self.btn)
        
        self.stack = QStackedWidget()
        
        # States
        def make_st(text, widget=None, icon=None):
            w = QWidget(); hl = QHBoxLayout(w); hl.setContentsMargins(0, 0, 0, 0); hl.setSpacing(12)
            if icon: hl.addWidget(icon)
            if widget: hl.addWidget(widget)
            lbl = QLabel(text.upper())
            lbl.setStyleSheet("color: #D4AF37; font-family: 'Segoe UI'; font-size: 14px; font-weight: 700; letter-spacing: 0.12em;")
            hl.addWidget(lbl)
            return w
        
        self.wave = WaveformWidget()
        self.spin = SpinnerWidget()
        self.check = SVGIconWidget("CHECK", 20)
        
        self.stack.addWidget(make_st("Ready to chatter"))
        self.stack.addWidget(make_st("Listening", self.wave))
        self.stack.addWidget(make_st("Polishing", self.spin))
        self.stack.addWidget(make_st("Polished & Pasted", None, self.check))
        
        l.addWidget(self.stack)
        self.setStyleSheet("QFrame#pill { background-color: #0A0A0A; border: 1.5px solid #33290D; border-radius: 32px; }")

    @pyqtProperty(int)
    def pill_width(self): return self._w
    @pill_width.setter
    def pill_width(self, val):
        self._w = val
        self.setFixedWidth(val)

class Chatterbox(QWidget):
    toggle = pyqtSignal()
    rebind = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.is_rec = False
        self.mt = None
        self.v = None
        self.ani = None
        
        self.hide_timer = QTimer(self); self.hide_timer.setSingleShot(True); self.hide_timer.timeout.connect(self.on_reset)
        self.rst_timer = QTimer(self); self.rst_timer.setSingleShot(True); self.rst_timer.timeout.connect(self._rst)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # Main layout holds the pill to allow the shadow to spill out
        vl = QVBoxLayout(self); vl.setContentsMargins(60, 60, 60, 60) # Increased margin for shadow
        self.p = MorphPill(); vl.addWidget(self.p)
        
        # exact HTML box-shadow approx
        s = QGraphicsDropShadowEffect(self)
        s.setBlurRadius(80); s.setColor(QColor(0, 0, 0, 240)); s.setOffset(0, 25) # Deeper shadow
        self.p.setGraphicsEffect(s)
        
        self.tray = QSystemTrayIcon(self)
        px = QPixmap(24, 24); px.fill(Qt.GlobalColor.transparent)
        ptr = QPainter(px); ptr.setRenderHint(QPainter.RenderHint.Antialiasing); ptr.setBrush(QColor("#D4AF37")); ptr.drawEllipse(4, 4, 16, 16); ptr.end()
        self.tray.setIcon(QIcon(px)); self.tray.show()
        m = QMenu(); m.addAction("Settings", self.opts); m.addAction("Exit", QApplication.quit); self.tray.setContextMenu(m)
        
        self.toggle.connect(self.on_tog); self.rebind.connect(self.on_reb)
        self.on_reb(); self.hide()

    def on_reb(self):
        if hasattr(self, 'h'): 
            try: keyboard.remove_hotkey(self.h)
            except: pass
        if APP_CONFIG.enabled: self.h = keyboard.add_hotkey(APP_CONFIG.hotkey, self.toggle.emit, suppress=False)

    def on_tog(self):
        if not APP_CONFIG.enabled: return
        if not self.is_rec:
            # STOP ALL PENDING TIMERS/ANIMATIONS FIRST
            if self.ani: self.ani.stop()
            if self.mt: self.mt.stop()
            if self.v: self.v.stop()
            self.hide_timer.stop()
            self.rst_timer.stop()
            
            # FORCE RESET BEFORE SHOWING
            self._rst()
            
            self.is_rec = True
            self.p.icon.set_mode("STOP"); self.p.btn.setStyleSheet("background-color: #D4AF37; border-radius: 26px;")
            self.p.stack.setCurrentIndex(1); self.p.pill_width = 240; self.p.wave.start()
            winsound.Beep(1000, 100)
            
            # Show and animate
            self.show(); self.setWindowOpacity(0)
            g = QApplication.primaryScreen().geometry(); cx = (g.width() - self.width()) // 2
            self.move(cx, g.height() - 80)
            
            self.ani = QParallelAnimationGroup()
            f = QPropertyAnimation(self, b"windowOpacity"); f.setDuration(300); f.setEndValue(1)
            s = QPropertyAnimation(self, b"pos"); s.setDuration(500); s.setEndValue(QPoint(cx, g.height() - 200)); s.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.ani.addAnimation(f); self.ani.addAnimation(s); self.ani.start()
            
            self.w = AudioThread(); self.w.finished.connect(self.on_fin); self.w.start()
        else:
            winsound.Beep(800, 80); self.w.active = False
            
            # IMMEDIATE FEEDBACK: Switch to Polishing UI while Whisper processes
            self.p.wave.stop()
            self.p.icon.set_mode("CUBE")
            self.p.spin.start()
            self.trans(2, 220)

    def trans(self, idx, w):
        if self.mt: self.mt.stop()
        self.mt = QPropertyAnimation(self.p, b"pill_width")
        self.mt.setDuration(400); self.mt.setEndValue(w); self.mt.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.mt.valueChanged.connect(lambda: self.move((QApplication.primaryScreen().geometry().width() - self.width()) // 2, self.y()))
        self.mt.finished.connect(lambda: self.p.stack.setCurrentIndex(idx))
        self.mt.start()

    def on_fin(self, t):
        if t == "ERROR": self.on_reset(); return
        
        # We are already transitioning to/in state 2 (Polishing). Just start Ollama.
        self.oll = OllamaThread(t); self.oll.finished.connect(self.on_done); self.oll.start()

    def on_done(self, t):
        pyperclip.copy(t + ' '); pyautogui.hotkey('ctrl', 'v'); self.p.spin.stop()
        self.p.btn.setStyleSheet("background-color: #1A1A1A; border: 1px solid #D4AF37; border-radius: 26px;")
        self.p.icon.set_mode("CUBE", "#D4AF37"); self.trans(3, 330)
        self.hide_timer.start(2500)

    def on_reset(self):
        if self.v: self.v.stop()
        self.v = QPropertyAnimation(self, b"windowOpacity"); self.v.setDuration(400); self.v.setEndValue(0); self.v.finished.connect(self.hide); self.v.start()
        self.is_rec = False
        self.rst_timer.start(500)

    def _rst(self):
        self.p.icon.set_mode("CUBE", "#000"); self.p.btn.setStyleSheet("background-color: #D4AF37; border-radius: 26px;")
        self.p.pill_width = 260; self.p.stack.setCurrentIndex(0)

    def opts(self):
        d = SettingsDialog(self)
        if d.exec(): d.save(); self.on_reb()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Chatterbox()
    sys.exit(app.exec())