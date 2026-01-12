"""
Prank with Sound Pack + Chrome-style fake login popup
File: prank_with_sounds_and_browser.py
Compatible: PyQt6 or PyQt5 (falls back)
Safe: does not modify any files. Always shows 'PRANK' notices.
"""

import sys, os, random, time
from functools import partial

# ---------- PyQt imports (try PyQt6 then PyQt5) ----------
try:
    from PyQt6 import QtWidgets, QtCore, QtGui, QtMultimedia
    QtKey_Escape = QtCore.Qt.Key.Key_Escape
    WindowStaysOnTop = QtCore.Qt.WindowType.WindowStaysOnTopHint
    AlignCenter = QtCore.Qt.AlignmentFlag.AlignCenter
    QtEventKeyPress = QtCore.QEvent.Type.KeyPress
    MEDIA_AVAILABLE = True
except Exception:
    from PyQt5 import QtWidgets, QtCore, QtGui
    try:
        from PyQt5 import QtMultimedia
        MEDIA_AVAILABLE = True
    except Exception:
        MEDIA_AVAILABLE = False
        # QtMultimedia may not exist; avoid referencing it unless MEDIA_AVAILABLE
    QtKey_Escape = QtCore.Qt.Qt.Key_Escape
    WindowStaysOnTop = QtCore.Qt.Qt.WindowStaysOnTopHint
    AlignCenter = QtCore.Qt.Qt.AlignCenter
    QtEventKeyPress = QtCore.QEvent.KeyPress

# ---------- CONFIG ----------
POPUP_COUNT = 14
POPUP_INTERVAL_MS = 300
FULLSCREEN_BSOD_CHANCE = 0.25
AUTO_STOP_SECONDS = 40
USE_RANDOM_POS = True

ASSETS_DIR_NAME = "assets"
SOUNDS_SUBDIR = "sounds"
ICON_FILE = "icon.ico"

FAKE_FILES = [
    "C:\\Users\\victim\\Documents\\taxes_2023.xlsx",
    "C:\\Users\\victim\\Pictures\\vacation.jpg",
    "/home/victim/.ssh/id_rsa",
    "D:\\Work\\presentation.pptx",
]
SCARY_MESSAGES = [
    "Encrypting user files...",
    "Ransomware detected — do not turn off",
    "Critical system failure",
]

POPUP_SIZE = (520, 200)
BSOD_BG = "#001a66"
PRANK_WATERMARK_STYLE = "color: rgba(255,0,0,0.95); font-weight:bold;"
# ------------------------

def resource_path(*path_parts):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *path_parts)

def load_sound_files():
    sounds = []
    snd_dir = resource_path(ASSETS_DIR_NAME, SOUNDS_SUBDIR)
    if os.path.isdir(snd_dir):
        for fname in os.listdir(snd_dir):
            if fname.lower().endswith(('.wav', '.mp3', '.ogg')):
                sounds.append(os.path.join(snd_dir, fname))
    return sounds

# ---------- sound playback wrapper ----------
class SoundPlayer:
    def __init__(self):
        self._sfx_cache = []
        self._media_players = []

    def play_once(self, path):
        try:
            if (not MEDIA_AVAILABLE) or (not os.path.exists(path)):
                QtWidgets.QApplication.beep()
                return

            # Prefer QSoundEffect if available (PyQt6 or PyQt5 may have it)
            if MEDIA_AVAILABLE and 'QtMultimedia' in globals() and hasattr(QtMultimedia, "QSoundEffect"):
                try:
                    sfx = QtMultimedia.QSoundEffect()
                    sfx.setSource(QtCore.QUrl.fromLocalFile(path))
                    sfx.setLoopCount(1)
                    sfx.setVolume(0.9)
                    sfx.play()
                    self._sfx_cache.append(sfx)
                    QtCore.QTimer.singleShot(5000, lambda: self._cleanup_sfx(sfx))
                    return
                except Exception:
                    # fall back to media player
                    pass

            # Fallback: QMediaPlayer (if available)
            if MEDIA_AVAILABLE and 'QtMultimedia' in globals() and hasattr(QtMultimedia, "QMediaPlayer"):
                try:
                    player = QtMultimedia.QMediaPlayer()
                    # try both API variants
                    try:
                        content = QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(path))
                        player.setMedia(content)
                    except Exception:
                        try:
                            player.setSource(QtCore.QUrl.fromLocalFile(path))
                        except Exception:
                            pass
                    player.setVolume(80)
                    player.play()
                    self._media_players.append(player)
                    QtCore.QTimer.singleShot(8000, lambda: self._cleanup_player(player))
                    return
                except Exception:
                    pass

            # Final fallback
            QtWidgets.QApplication.beep()
        except Exception:
            try:
                QtWidgets.QApplication.beep()
            except:
                pass

    def _cleanup_sfx(self, sfx):
        try:
            self._sfx_cache.remove(sfx)
        except Exception:
            pass

    def _cleanup_player(self, p):
        try:
            self._media_players.remove(p)
        except Exception:
            pass

GLOBAL_SOUND_PLAYER = SoundPlayer()
SOUND_FILES = load_sound_files()

def play_random_sound():
    if SOUND_FILES:
        GLOBAL_SOUND_PLAYER.play_once(random.choice(SOUND_FILES))
    else:
        QtWidgets.QApplication.beep()

# ---------- UI components ----------
class PopupEncrypt(QtWidgets.QWidget):
    closed = QtCore.pyqtSignal(object)

    def __init__(self, idx, style='alert'):
        super().__init__(flags=QtCore.Qt.WindowType.Window)
        self.idx = idx
        self.style = style
        # Initialize timer list BEFORE setup_ui so _setup_animations can append to it
        self._anim_timers = []
        self.setWindowFlags(self.windowFlags() | WindowStaysOnTop)
        self.setup_ui()

    def setup_ui(self):
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        if self.style == 'bsod':
            w, h = screen.width(), screen.height()
            self.setGeometry(0, 0, w, h)
            self.setStyleSheet(f"background-color: {BSOD_BG};")
        else:
            w, h = POPUP_SIZE
            if USE_RANDOM_POS:
                x = random.randint(0, max(0, screen.width()-w))
                y = random.randint(0, max(0, screen.height()-h))
            else:
                x = 100 + (self.idx * 30) % (screen.width()-w)
                y = 100 + (self.idx * 20) % (screen.height()-h)
            self.setGeometry(x, y, w, h)
            self.setFixedSize(w, h)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(12,12,12,12)

        # header flashing label
        self.header = QtWidgets.QLabel(random.choice(SCARY_MESSAGES))
        f = QtGui.QFont("Arial", 14)
        f.setBold(True)
        self.header.setFont(f)
        self.header.setAlignment(AlignCenter)
        layout.addWidget(self.header)

        if self.style == 'bsod':
            big = QtWidgets.QLabel("A critical system error has occurred.\nSystem will attempt to recover.")
            bf = QtGui.QFont("Consolas", 14)
            bf.setBold(True)
            big.setFont(bf)
            big.setAlignment(AlignCenter)
            big.setStyleSheet("color: white;")
            layout.addWidget(big)
            prank = QtWidgets.QLabel("THIS IS A PRANK — NO FILES ARE HARMED")
            prank.setStyleSheet(PRANK_WATERMARK_STYLE)
            prank.setAlignment(AlignCenter)
            pf = QtGui.QFont("Arial", 18)
            pf.setBold(True)
            prank.setFont(pf)
            layout.addWidget(prank)
        else:
            msg = QtWidgets.QLabel("Files being encrypted (simulated):")
            mf = QtGui.QFont("Arial", 10)
            msg.setFont(mf)
            layout.addWidget(msg)

            self.file_list = QtWidgets.QPlainTextEdit()
            self.file_list.setReadOnly(True)
            self.file_list.setMaximumHeight(90)
            layout.addWidget(self.file_list)

            self.progress = QtWidgets.QProgressBar()
            self.progress.setRange(0, 100)
            self.progress.setValue(random.randint(3, 18))
            layout.addWidget(self.progress)

            h = QtWidgets.QHBoxLayout()
            stop_btn = QtWidgets.QPushButton("STOP PRANK")
            stop_btn.clicked.connect(self.close)
            browser_btn = QtWidgets.QPushButton("Open suspicious login")
            browser_btn.clicked.connect(self._open_fake_browser)
            h.addWidget(browser_btn)
            h.addStretch()
            h.addWidget(stop_btn)
            layout.addLayout(h)

            prank = QtWidgets.QLabel("THIS IS A PRANK — NO FILES ARE HARMED")
            prank.setStyleSheet(PRANK_WATERMARK_STYLE)
            prank.setAlignment(AlignCenter)
            layout.addWidget(prank)

        self.setLayout(layout)
        self._setup_animations()

    def _setup_animations(self):
        t1 = QtCore.QTimer(self)
        t1.timeout.connect(self._flash_header)
        t1.start(350 + random.randint(0,150))
        self._anim_timers.append(t1)

        if hasattr(self, 'file_list'):
            self._file_idx = 0
            self._filenames = []
            for _ in range(40):
                base = random.choice(FAKE_FILES)
                name = f"{base}.enc{random.randint(1,999)}"
                self._filenames.append(name)
            t2 = QtCore.QTimer(self)
            t2.timeout.connect(self._add_file_and_step)
            t2.start(220 + random.randint(0,220))
            self._anim_timers.append(t2)

    def _flash_header(self):
        if random.random() < 0.5:
            self.header.setStyleSheet("color: yellow; background: black;")
        else:
            self.header.setStyleSheet("color: red;")

    def _add_file_and_step(self):
        if self._file_idx >= len(self._filenames):
            for t in list(self._anim_timers):
                t.stop()
            return
        fname = self._filenames[self._file_idx]
        self.file_list.appendPlainText(f"[{time.strftime('%H:%M:%S')}] Encrypting: {fname}")
        self._file_idx += 1
        newv = min(100, self.progress.value() + random.randint(1,6))
        self.progress.setValue(newv)
        if newv >= 95:
            for t in self._anim_timers:
                t.setInterval(600 + random.randint(0,500))

    def _open_fake_browser(self):
        cb = ChromeLoginPopup(parent=None)
        cb.show()

    def closeEvent(self, event):
        for t in list(self._anim_timers):
            try: t.stop()
            except: pass
        self.closed.emit(self)
        event.accept()

class ChromeLoginPopup(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("– Google Chrome (PRANK)")
        self.setFixedSize(540, 360)
        self.setWindowFlags(self.windowFlags() | WindowStaysOnTop)
        self._setup_ui()

    def _setup_ui(self):
        central = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout()
        top = QtWidgets.QHBoxLayout()
        tab_label = QtWidgets.QLabel("  •  •  •   Suspicious Site — Login")
        tab_label.setStyleSheet("background:#F1F3F4; padding:6px; border-radius:4px;")
        top.addWidget(tab_label)
        top.addStretch()
        v.addLayout(top)

        address = QtWidgets.QLineEdit("https://your-bank.example/login (PRANK)")
        address.setReadOnly(True)
        address.setStyleSheet("background: white; padding:6px;")
        v.addWidget(address)

        page = QtWidgets.QFrame()
        page.setStyleSheet("background: white; border: 1px solid #d0d0d0;")
        pv = QtWidgets.QVBoxLayout()
        pv.setContentsMargins(20,20,20,20)
        title = QtWidgets.QLabel("Sign in to your account")
        tf = QtGui.QFont("Arial", 16); tf.setBold(True)
        title.setFont(tf)
        pv.addWidget(title)
        info = QtWidgets.QLabel("This is a simulated phishing login (PRANK). Do not enter real credentials.")
        info.setWordWrap(True)
        info.setStyleSheet("color: red; font-weight: bold;")
        pv.addWidget(info)

        user = QtWidgets.QLineEdit(); user.setPlaceholderText("Email or phone"); user.setDisabled(True)
        passwd = QtWidgets.QLineEdit(); passwd.setPlaceholderText("Password"); passwd.setDisabled(True)
        pv.addWidget(user); pv.addWidget(passwd)

        btn_layout = QtWidgets.QHBoxLayout()
        signin = QtWidgets.QPushButton("Sign in (disabled - PRANK)"); signin.setDisabled(True)
        btn_layout.addStretch(); btn_layout.addWidget(signin)
        pv.addLayout(btn_layout)

        watermark = QtWidgets.QLabel("THIS IS A PRANK — DO NOT ENTER REAL CREDENTIALS")
        watermark.setStyleSheet("color: rgba(255,0,0,0.9); font-weight:bold;")
        pv.addWidget(watermark)

        page.setLayout(pv)
        v.addWidget(page)
        central.setLayout(v)
        self.setCentralWidget(central)
        self.setStyleSheet("QMainWindow { background: #e9eef6; }")

# ---------------- Tray, Controller, spawn logic ----------------
class ControllerWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prank Controller (Auto)")
        self.setGeometry(600,220,420,170)
        self.setWindowFlags(self.windowFlags() | WindowStaysOnTop)
        self.popups = []
        self._spawn_index = 0
        self.spawn_timer = None
        self.auto_stop_timer = None
        self._setup_ui()
        QtCore.QTimer.singleShot(150, self.start_prank)

    def _setup_ui(self):
        v = QtWidgets.QVBoxLayout()
        v.addWidget(QtWidgets.QLabel("Fake Virus Prank — Auto-starting... (Esc to kill)"))
        self.stat_label = QtWidgets.QLabel("Spawned: 0   Active: 0")
        v.addWidget(self.stat_label)
        h = QtWidgets.QHBoxLayout()
        self.btn_hide = QtWidgets.QPushButton("Hide to Tray (Ctrl+H)")
        self.btn_hide.clicked.connect(self.hide)
        h.addWidget(self.btn_hide)
        self.btn_stop = QtWidgets.QPushButton("Stop Now (Esc)")
        self.btn_stop.clicked.connect(self.stop_prank)
        h.addWidget(self.btn_stop)
        v.addLayout(h)
        v.addWidget(QtWidgets.QLabel("Shortcuts: Esc=Stop, Ctrl+H=Hide, Ctrl+Q=Quit"))
        self.setLayout(v)

    def start_prank(self):
        self._spawn_index = 0
        self.spawn_timer = QtCore.QTimer(self)
        self.spawn_timer.timeout.connect(self._spawn_one)
        self.spawn_timer.start(POPUP_INTERVAL_MS)
        if AUTO_STOP_SECONDS > 0:
            self.auto_stop_timer = QtCore.QTimer(self)
            self.auto_stop_timer.setSingleShot(True)
            self.auto_stop_timer.timeout.connect(self.stop_prank)
            self.auto_stop_timer.start(AUTO_STOP_SECONDS*1000)

    def _spawn_one(self):
        if self._spawn_index >= POPUP_COUNT:
            if self.spawn_timer and self.spawn_timer.isActive():
                self.spawn_timer.stop()
            return
        style = 'bsod' if random.random() < FULLSCREEN_BSOD_CHANCE and self._spawn_index % 3 == 0 else 'alert'
        p = PopupEncrypt(self._spawn_index, style=style)
        p.closed.connect(self._on_popup_closed)
        p.show()
        play_random_sound()
        self.popups.append(p)
        self._spawn_index += 1
        self._update_stats()

    def _on_popup_closed(self, popup):
        try:
            self.popups.remove(popup)
        except ValueError:
            pass
        self._update_stats()

    def _update_stats(self):
        self.stat_label.setText(f"Spawned: {self._spawn_index}   Active: {len(self.popups)}")

    def stop_prank(self):
        for p in list(self.popups):
            try: p.close()
            except: pass
        self.popups.clear()
        if self.spawn_timer and self.spawn_timer.isActive():
            self.spawn_timer.stop()
        if self.auto_stop_timer and self.auto_stop_timer.isActive():
            self.auto_stop_timer.stop()
        self._update_stats()

    def closeEvent(self, event):
        self.stop_prank()
        event.accept()

class TrayController(QtWidgets.QSystemTrayIcon):
    def __init__(self, controller_window):
        icon = None
        icon_path = resource_path(ASSETS_DIR_NAME, ICON_FILE)
        if os.path.exists(icon_path):
            icon = QtGui.QIcon(icon_path)
        else:
            pix = QtGui.QPixmap(64,64)
            pix.fill(QtGui.QColor("transparent"))
            painter = QtGui.QPainter(pix)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            painter.setBrush(QtGui.QBrush(QtGui.QColor("red")))
            painter.setPen(QtGui.QPen(QtGui.QColor("black")))
            painter.drawEllipse(8,8,48,48)
            painter.end()
            icon = QtGui.QIcon(pix)
        super().__init__(icon)
        self.controller_window = controller_window
        self.setToolTip("Fake Virus Prank (running)")
        menu = QtWidgets.QMenu()
        show_action = menu.addAction("Show Controller")
        stop_action = menu.addAction("Stop Prank")
        restore_action = menu.addAction("Run Restore (PRANK)")
        menu.addSeparator()
        exit_action = menu.addAction("Exit")
        self.setContextMenu(menu)
        show_action.triggered.connect(self.show_controller)
        stop_action.triggered.connect(self.controller_window.stop_prank)
        restore_action.triggered.connect(self.controller_window.stop_prank)
        exit_action.triggered.connect(self.exit_all)
        self.activated.connect(self._on_activate)
        self.show()

    def show_controller(self):
        self.controller_window.show()
        self.controller_window.raise_()
        self.controller_window.activateWindow()

    def _on_activate(self, reason):
        if reason in (QtWidgets.QSystemTrayIcon.ActivationReason.Trigger,
                      QtWidgets.QSystemTrayIcon.ActivationReason.DoubleClick):
            self.show_controller()

    def exit_all(self):
        self.controller_window.stop_prank()
        QtWidgets.QApplication.quit()

def global_input_filter(controller):
    class Filter(QtCore.QObject):
        def eventFilter(self, obj, ev):
            if ev.type() == QtEventKeyPress:
                try:
                    key = ev.key()
                except Exception:
                    key = None
                mods = ev.modifiers() if hasattr(ev, "modifiers") else None
                if key == QtKey_Escape:
                    controller.stop_prank()
                    return True
                try:
                    ctrl = QtCore.Qt.KeyboardModifier.ControlModifier
                    key_h = QtCore.Qt.Key.Key_H if hasattr(QtCore.Qt, "Key") else QtCore.Qt.Key_H
                    key_q = QtCore.Qt.Key.Key_Q if hasattr(QtCore.Qt, "Key") else QtCore.Qt.Key_Q
                    if key == key_h and (mods & ctrl):
                        if controller.isVisible(): controller.hide()
                        else: controller.show()
                        return True
                    if key == key_q and (mods & ctrl):
                        controller.stop_prank()
                        QtWidgets.QApplication.quit()
                        return True
                except Exception:
                    pass
            return False
    filt = Filter()
    app = QtWidgets.QApplication.instance()
    app.installEventFilter(filt)

def main():
    app = QtWidgets.QApplication(sys.argv)
    controller = ControllerWindow()
    controller.show()
    tray = TrayController(controller)
    tray.showMessage("Prank Running", "Fake Virus Prank is active (PRANK). Press Esc to stop.", QtWidgets.QSystemTrayIcon.MessageIcon.Information, 3500)
    QtCore.QTimer.singleShot(1500, controller.hide)
    global_input_filter(controller)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
