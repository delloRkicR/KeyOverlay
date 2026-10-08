import tkinter as tk
from pynput import keyboard
#config
KEY_SIZE = 46 
KEY_GAP = 6 
ENTER_WIDTH = 3 * KEY_SIZE + 2 * KEY_GAP
BG_TRANSPARENT_COLOR = "#ff00ff"
KEY_IDLE_FILL = "#202020"
KEY_IDLE_OUTLINE = "#666666"
KEY_ACTIVE_FILL = "#39d353"
KEY_ACTIVE_OUTLINE = "#39d353"
TEXT_IDLE_COLOR = "#dddddd"
TEXT_ACTIVE_COLOR = "#0a0a0a"
FONT = ("Segoe UI", 14, "bold")
CLOSE_BTN_COLOR = "#aaaaaa"
CLOSE_BTN_HOVER = "#ff5555"
START_X = 40
START_Y = 40


class KeyOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.geometry(f"+{START_X}+{START_Y}")

        try:
            self.root.attributes("-transparentcolor", BG_TRANSPARENT_COLOR)
            canvas_bg = BG_TRANSPARENT_COLOR
        except tk.TclError:
            self.root.attributes("-alpha", 0.85)
            canvas_bg = "#1a1a1a"

        width = 3 * KEY_SIZE + 2 * KEY_GAP + 40
        height = 2 * KEY_SIZE + KEY_GAP + 40 + 20
        self.canvas = tk.Canvas(
            self.root, width=width, height=height,
            bg=canvas_bg, highlightthickness=0
        )
        self.canvas.pack()

        self.key_shapes = {}
        self._build_layout()
        self._build_close_button()
        self._make_draggable()

        self.listener = keyboard.Listener(
            on_press=self._on_press, on_release=self._on_release
        )
        self.listener.daemon = True
        self.listener.start()

        self.root.bind("<Escape>", lambda e: self.close())
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def _build_layout(self):
        top = 20

        self._draw_key("w", "W", KEY_SIZE + KEY_GAP, top, KEY_SIZE)

        row2_y = top + KEY_SIZE + KEY_GAP
        self._draw_key("a", "A", 0, row2_y, KEY_SIZE)
        self._draw_key("s", "S", KEY_SIZE + KEY_GAP, row2_y, KEY_SIZE)
        self._draw_key("d", "D", 2 * (KEY_SIZE + KEY_GAP), row2_y, KEY_SIZE)

        row3_y = row2_y + KEY_SIZE + KEY_GAP
        rect = self.canvas.create_rectangle(
            0, row3_y, ENTER_WIDTH, row3_y + 30,
            fill=KEY_IDLE_FILL, outline=KEY_IDLE_OUTLINE, width=2,
            tags="draggable"
        )
        text = self.canvas.create_text(
            ENTER_WIDTH / 2, row3_y + 15, text="ENTER",
            fill=TEXT_IDLE_COLOR, font=("Segoe UI", 11, "bold"),
            tags="draggable"
        )
        self.key_shapes["enter"] = (rect, text)

    def _draw_key(self, key, label, x, y, size):
        rect = self.canvas.create_rectangle(
            x, y, x + size, y + size,
            fill=KEY_IDLE_FILL, outline=KEY_IDLE_OUTLINE, width=2,
            tags="draggable"
        )
        text = self.canvas.create_text(
            x + size / 2, y + size / 2, text=label,
            fill=TEXT_IDLE_COLOR, font=FONT, tags="draggable"
        )
        self.key_shapes[key] = (rect, text)

    def _build_close_button(self):
        self.close_id = self.canvas.create_text(
            3 * KEY_SIZE + 2 * KEY_GAP, 8, text="x",
            fill=CLOSE_BTN_COLOR, font=("Segoe UI", 12, "bold"),
            anchor="ne"
        )
        self.canvas.tag_bind(self.close_id, "<Button-1>", lambda e: self.close())
        self.canvas.tag_bind(
            self.close_id, "<Enter>",
            lambda e: self.canvas.itemconfig(self.close_id, fill=CLOSE_BTN_HOVER)
        )
        self.canvas.tag_bind(
            self.close_id, "<Leave>",
            lambda e: self.canvas.itemconfig(self.close_id, fill=CLOSE_BTN_COLOR)
        )

    def _make_draggable(self):
        self._drag_offset = (0, 0)

        def start_drag(event):
            self._drag_offset = (event.x, event.y)

        def do_drag(event):
            x = self.root.winfo_pointerx() - self._drag_offset[0]
            y = self.root.winfo_pointery() - self._drag_offset[1]
            self.root.geometry(f"+{x}+{y}")

        self.canvas.tag_bind("draggable", "<ButtonPress-1>", start_drag)
        self.canvas.tag_bind("draggable", "<B1-Motion>", do_drag)

        self.canvas.bind("<ButtonPress-1>", start_drag)
        self.canvas.bind("<B1-Motion>", do_drag)

    def _key_name(self, key):
        try:
            if key == keyboard.Key.enter:
                return "enter"
            return key.char.lower() if key.char else None
        except AttributeError:
            return None

    def _set_active(self, name, active):
        if name not in self.key_shapes:
            return
        rect, text = self.key_shapes[name]
        if active:
            self.canvas.itemconfig(rect, fill=KEY_ACTIVE_FILL, outline=KEY_ACTIVE_OUTLINE)
            self.canvas.itemconfig(text, fill=TEXT_ACTIVE_COLOR)
        else:
            self.canvas.itemconfig(rect, fill=KEY_IDLE_FILL, outline=KEY_IDLE_OUTLINE)
            self.canvas.itemconfig(text, fill=TEXT_IDLE_COLOR)

    def _on_press(self, key):
        name = self._key_name(key)
        if name:

            self.root.after(0, self._set_active, name, True)

    def _on_release(self, key):
        name = self._key_name(key)
        if name:
            self.root.after(0, self._set_active, name, False)

    def close(self):
        try:
            self.listener.stop()
        except Exception:
            pass
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    KeyOverlay().run()