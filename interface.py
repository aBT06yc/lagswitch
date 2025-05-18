import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import font

import subprocess
import threading

class AdvancedToggleApp:
    def __init__(self, root):
        
        self.root = root
        self.root.title('Lag-Switch (lite v0.1)')
        #self.root.geometry("400x300")  # Увеличил размер окна
        self.root.resizable(False, False)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.switch_btn = 'x'
        self.root.bind("<Key>", self.on_key_press)
        self.key_listening = False

        self.is_port_search_running = False
        
        # Main container
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Left side (checkboxes and port input)
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Right side 
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Checkboxes
        self.checkbox_frame = ttk.LabelFrame(self.left_frame, text="Direction", padding="5")
        self.checkbox_frame.pack(pady=5)

        self.in_var = tk.BooleanVar()
        self.out_var = tk.BooleanVar(value=True)

        # Следим за изменениями чекбоксов
        self.in_var.trace_add('write', lambda *_: self.auto_turn_off())
        self.out_var.trace_add('write', lambda *_: self.auto_turn_off())

        self.in_cb = ttk.Checkbutton(
            self.checkbox_frame, 
            text="inbound", 
            variable=self.in_var
        )
        self.in_cb.pack(anchor=tk.W)

        self.out_cb = ttk.Checkbutton(
            self.checkbox_frame, 
            text="outbound", 
            variable=self.out_var
        )
        self.out_cb.pack(anchor=tk.W)

        # Port input with buttons
        self.port_frame = ttk.Frame(self.left_frame)
        self.port_frame.pack(pady=10)

        ttk.Label(self.port_frame, text="Port:").pack(side=tk.LEFT)

        self.port_var = tk.StringVar()
        # Следим за изменениями порта
        self.port_var.trace_add('write', lambda *_: self.auto_turn_off())

        # Поле ввода только чисел
        vcmd = (root.register(self.validate_port), '%P')
        self.port_entry = ttk.Entry(
            self.port_frame, 
            textvariable=self.port_var, 
            width=15,
            validate='key',
            validatecommand=vcmd
        )
        self.port_entry.pack(side=tk.LEFT)

        self.port_button = ttk.Button(
            self.port_frame, 
            text="Auto port search", 
            command=self.port_search
        )
        self.port_button.pack(side=tk.LEFT, padx=5)

        self.toggle_label = ttk.Label(
            self.right_frame, 
            text="Lag-Switch:", 
            font=('Arial', 10)
        )
        self.toggle_label.pack()

        self.toggle_state = False
        self.toggle_button = tk.Button(
            self.right_frame,
            text="OFF",
            bg="red",
            fg="white",
            font=("Arial", 12, "bold"),
            width=8,
            height=1,
            command=self.toggle_switch
        )
        self.toggle_button.pack(pady=5)

        self.button_remap = ttk.Button(
            self.right_frame, 
            text="Remap button", 
            command=self.remap_button
        )
        self.button_remap.pack(pady=10)
        self.switch_btn_label = ttk.Label(
            self.right_frame, 
            text=f'now "{self.switch_btn}"', 
            font=('Arial', 10)
        )
        self.switch_btn_label.pack(side=tk.BOTTOM)

        self.bottom_frame = ttk.Frame(root)
        self.bottom_frame.pack(fill=tk.X, padx=10, pady=10)

        self.text = tk.Text(self.bottom_frame, height=6, width=60, state='normal')
        self.text.pack(fill=tk.BOTH, expand=True)
        self.text.insert(tk.END, 'Press "Auto port search"')
        self.text.config(state='disabled')
        
        self.signature_label = ttk.Label(
            self.bottom_frame,
            text="made by t.me/ponosuchiha",
            font=("Arial", 8)
        )
        self.signature_label.pack(side=tk.RIGHT, anchor=tk.SE)

    def validate_port(self, value):
        """Разрешаем только числа 0-65535"""
        if value == "":
            return True  # Пустое поле разрешено
        if not value.isdigit():
            return False
        port = int(value)
        return 0 <= port <= 65535

    def auto_turn_off(self):
        if self.toggle_state:
            self.toggle_switch()  # Вызовет переключение в OFF
 
    def port_search(self):
        if self.is_port_search_running:
            return
        threading.Thread(target=self._run_port_search, daemon=True).start()

    def _run_port_search(self):
        self.is_port_search_running = True
        try:
            self.port_search_process= subprocess.run("py connection.py port_search", capture_output=True, text=True)  #connection.exe
            udp_ports = eval(self.port_search_process.stdout)
        except Exception as e:
            udp_ports = {}
            print("Ошибка при выполнении поиска портов:", e)

        self.text.after(0, lambda: self._update_text_with_ports(udp_ports))
        self.is_port_search_running = False

    def _update_text_with_ports(self, udp_ports):
        self.text.config(state='normal')
        self.text.delete("1.0", tk.END)

        # Настройка жирного шрифта (однократно)
        if not hasattr(self, "bold_font"):
            self.bold_font = font.Font(self.text, self.text.cget("font"))
            self.bold_font.configure(weight="bold", size=12)
            self.text.tag_configure("bold", font=self.bold_font)

        if not udp_ports:
            self.text.insert(tk.END, "Ошибка: нет данных\n")
        else:
            for ip in udp_ports:
                port = udp_ports[ip]["dst_port"]
                count = udp_ports[ip]["packet_count"]
                self.text.insert(tk.END, f"port: ")
                self.text.insert(tk.END, f"{port} \t", "bold")
                self.text.insert(tk.END, f'udp_trafic: {count / 0.5}% \t from: {ip}\n')

        self.text.config(state='disabled')

    
    def remap_button(self):
        self.auto_turn_off()

        mode = self.button_remap["text"]
        if mode != "Cancel":
            self.button_remap["text"] = "Cancel"
            self.switch_btn_label["text"] = "Press key ..."
            self.key_listening = True
        else:
            self.button_remap["text"] = "Remap button"
            self.switch_btn_label["text"] = f'Switch key: "{self.switch_btn}"' if self.switch_btn != -1 else "use other key"
            self.key_listening = False

        #self.switch_btn = "s"
        #self.switch_btn_label["text"] = f'now "{self.switch_btn}"'
    

    def on_key_press(self, event):
        """Обработчик нажатия клавиш"""
        if self.key_listening:
            # Получаем код клавиши
            if event.keycode in keycode_to_keyboard.keys():
                key = keycode_to_keyboard[event.keycode]
            else:
                key = -1
            # Выводим информацию в консоль для отладки
            #print(f"Нажата клавиша: {event.char} (код: {event.keycode})")
            self.switch_btn = key
            self.remap_button()

    def toggle_switch(self):
        """Переключение состояния"""            
        self.toggle_state = not self.toggle_state
                            
        if self.toggle_state:
            # Проверяем, что настройки валидны перед включением
            if not (self.in_var.get() or self.out_var.get()):
                messagebox.showwarning("Warning", "Choose direction (in/out)")
                self.toggle_state = False
                return
            elif not self.port_var.get():
                messagebox.showwarning("Warning", "Choose udp port (0-65535)")
                self.toggle_state = False
                return

            self.toggle_button.config(text="ON", bg="green")
            #print(self.port_var.get(),self.in_var.get(),self.out_var.get(),self.switch_btn)
            #connection.exe    py connection.py
            self.lag_switch_process = subprocess.Popen([
                "py",
                "connection.py",#"connection.exe",
                "lagswitch",
                f"udp_port={self.port_var.get()}",
                f"inbound={self.in_var.get()}",
                f"outbound={self.out_var.get()}",
                f"key={self.switch_btn}"
            ])
        else:
            self.toggle_button.config(text="OFF", bg="red")
            subprocess.run(f'taskkill /F /T /PID {self.lag_switch_process.pid}', shell=True)
            #self.lag_switch_process.kill()
    
    def on_close(self):
        if hasattr(self, 'lag_switch_process') and self.lag_switch_process:
            try:
                subprocess.run(f'taskkill /F /T /PID {self.lag_switch_process.pid}', shell=True)
                #self.lag_switch_process.kill()
            except Exception as e:
                print("Failed to terminate process:", e)
            
            self.root.destroy()

        # connextion.exe еще может работать после закрытия интрефейса если вызван port_search
        # процесс сам завершиться после получения 50 пакетов. 
        # пока что эта проблема не критична  = Т Е Р П И М =
        """
        if hasattr(self, 'port_search_process') and self.port_search_process:
            try:
                subprocess.run(f'taskkill /F /T /PID {self.port_search_process.pid}', shell=True)
            except Exception as e:
                print("Failed to terminate port search process:", e)
        """
        self.root.destroy()

keycode_to_keyboard = {
    65: 'a',
    66: 'b',
    67: 'c',
    68: 'd',
    69: 'e',
    70: 'f',
    71: 'g',
    72: 'h',
    73: 'i',
    74: 'j',
    75: 'k',
    76: 'l',
    77: 'm',
    78: 'n',
    79: 'o',
    80: 'p',
    81: 'q',
    82: 'r',
    83: 's',
    84: 't',
    85: 'u',
    86: 'v',
    87: 'w',
    88: 'x',
    89: 'y',
    90: 'z',
    49: '1',
    50: '2',
    51: '3',
    52: '4',
    53: '5',
    54: '6',
    55: '7',
    56: '8',
    57: '9',
    48: '0',
    112: 'f1',
    113: 'f2',
    114: 'f3',
    115: 'f4',
    116: 'f5',
    117: 'f6',
    118: 'f7',
    119: 'f8',
    120: 'f9',
    121: 'f10',
    122: 'f11',
    123: 'f12',
    160: 'shift',   # Left Shift
    161: 'shift',   # Right Shift
    162: 'ctrl',    # Left Ctrl
    163: 'ctrl',    # Right Ctrl
    164: 'alt',     # Left Alt
    165: 'alt',     # Right Alt
    13: 'enter',
    8: 'backspace',
    27: 'esc',
    9: 'tab',
    32: 'space',
    37: 'left',
    38: 'up',
    39: 'right',
    40: 'down',
}

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedToggleApp(root)
    root.mainloop()