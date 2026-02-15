import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import font

import subprocess
import threading,queue
import sys,os
import re

class AdvancedToggleApp:
    def __init__(self, root):
        
        self.root = root
        self.root.title('Lag-Switch (pro v0.2.2)')
        #self.root.geometry("400x300")  # 
        self.root.resizable(False, False)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.switch_btn = 'x'
        self.root.bind("<Key>", self.on_key_press)
        self.key_listening = False

        self.is_ip_search_running = False
        self.q=queue.Queue()
        # Main container
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Left side (checkboxes and port input)
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        # Right side 
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.left_left_frame = ttk.Frame(self.left_frame)
        self.left_right_frame = ttk.Frame(self.left_frame)
        self.left_left_left_frame = ttk.Frame(self.left_left_frame)
        self.left_left_right_frame = ttk.Frame(self.left_left_frame)

        self.left_left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.left_right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.left_left_left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.left_left_right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        
        #  протокол
        self.protocol_frame = ttk.LabelFrame(self.left_right_frame, text="Protocol", padding="5")
        self.protocol_frame.pack(pady=5)
        self.tcp_var = tk.BooleanVar(value=False)  # По умолчанию TCP включен
        self.udp_var = tk.BooleanVar(value=True)  # По умолчанию UDP выключен
        self.tcp_checkbox = ttk.Checkbutton(self.protocol_frame, text="TCP", variable=self.tcp_var)
        self.tcp_checkbox.pack(anchor=tk.W)
        self.udp_checkbox = ttk.Checkbutton(self.protocol_frame, text="UDP", variable=self.udp_var)
        self.udp_checkbox.pack(anchor=tk.W)

        # direction
        self.checkbox_frame = ttk.LabelFrame(self.left_frame, text="Direction", padding="5")
        self.checkbox_frame.pack(pady=5)
        self.in_var = tk.BooleanVar()
        self.out_var = tk.BooleanVar(value=True)
        self.in_cb = ttk.Checkbutton( self.checkbox_frame, text="inbound", variable=self.in_var)
        self.in_cb.pack(anchor=tk.W)
        self.out_cb = ttk.Checkbutton(self.checkbox_frame,  text="outbound", variable=self.out_var)
        self.out_cb.pack(anchor=tk.W)


        # Port input with buttons
        self.ip_frame = ttk.Frame(self.left_frame)
        self.ip_frame.pack(pady=10)

        ttk.Label(self.ip_frame, text="IP:").pack(side=tk.LEFT)

        self.ip_var = tk.StringVar()
        # Следим за изменениями порта
        self.ip_var.trace_add('write', lambda *_: self.auto_turn_off())

        # Поле ввода только чисел
        self.ip_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        vcmd = (root.register(self.validate_input), '%P')
        self.ip_entry = ttk.Entry(
            self.ip_frame, 
            textvariable=self.ip_var, 
            width=16,
            validate='key',
            validatecommand=vcmd
        )
        self.ip_entry.pack(side=tk.LEFT)

        self.ipt_button = ttk.Button(
            self.ip_frame, 
            text="sniff IP", 
            command=self.ip_search
        )
        self.ipt_button.pack(side=tk.LEFT, padx=5)

        self.toggle_label = ttk.Label(
            self.right_frame, 
            text="Packet-control:", 
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

        self.switch_btn_label.pack() #side=tk.BOTTOM

        # switch_type (Press/Hold)
        self.switch_type_frame = ttk.LabelFrame(self.right_frame, text="switch type", padding="5")
        self.switch_type_frame.pack(pady=5)
        self.switch_type_var = tk.StringVar()
        self.switch_type_combobox = ttk.Combobox(self.switch_type_frame, textvariable=self.switch_type_var, values=["Press", "Hold"])
        self.switch_type_combobox.set("Hold")  # По умолчанию выбираем Hold
        self.switch_type_combobox.pack(pady=5)


        self.bottom_frame = ttk.Frame(root)
        self.bottom_frame.pack(fill=tk.X, padx=10, pady=10)

        self.text = tk.Text(self.bottom_frame, height=6, width=60, state='normal')
        self.text.pack(fill=tk.BOTH, expand=True)
        self.text.insert(tk.END, 'Press "sniff IP"')
        self.text.config(state='disabled')
        
        self.signature_label = ttk.Label(
            self.bottom_frame,
            text="made by t.me/ponosuchiha",
            font=("Arial", 8)
        )
        self.signature_label.pack(side=tk.RIGHT, anchor=tk.SE)

        # Следим за изменениями 
        self.in_var.trace_add('write', lambda *_: self.auto_turn_off())
        self.out_var.trace_add('write', lambda *_: self.auto_turn_off())
        self.tcp_var.trace_add('write', lambda *_: self.auto_turn_off())
        self.udp_var.trace_add('write', lambda *_: self.auto_turn_off())
        self.switch_type_var.trace_add('write', lambda *_: self.auto_turn_off())



    def validate_ip(self,P):
            # Проверяем, что введенное значение соответствует формату IP-адреса
            if P == "" or re.match(self.ip_pattern, P):
                return True
            return False
    
    def validate_input(self, s):
        """Разрешаем только числа 0-65535"""
        return len(s) <= 15

    def auto_turn_off(self):
        if self.toggle_state:
            self.toggle_switch()  # Вызовет переключение в OFF
    
    def stdout_reader(self):
        for l in iter(self.ip_search_process.stdout.readline,""): 
            self.q.put(l)

    def pump(self):
        while not self.q.empty(): 
            text = self.q.get()
            print(text)
            self._update_text_with_ports(text)
            #t.insert("end",q.get())
        root.after(50,self.pump)
        

    def ip_search(self):

        if self.is_ip_search_running:
            return
        
        self.text.config(state='normal')
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END,"Sniffer started. Scanning...")
        self.text.config(state='disabled')
        
        self.is_ip_search_running = True
        cmd = [sys.executable, "--sniffer"]

        if getattr(sys, "frozen", True):                        # Если мы запустились через py venv
                cmd = cmd[:1] + ["-u", "interface.py",] + cmd[1:]

        try:
            env=os.environ.copy(); env["PYTHONUNBUFFERED"]="1"
            
            self.ip_search_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                text=True,                  # текстовый режим
                bufsize=1,                  # line-buffering на стороне родителя (работает только в text=True)
                encoding="utf-8",
                env=env,
            )
            threading.Thread(target=self.stdout_reader,daemon=True).start()
            # self.ip_search_process = subprocess.run(
            #     cmd,
            #     capture_output=True,
            #     text=True,                  # текстовый режим
            #     bufsize=1,                  # line-buffering на стороне родителя (работает только в text=True)
            #     encoding="utf-8",           # подберите под ваш вывод; см. раздел про кодировки
            # )
            #stdout = self.ip_search_process.stdout
            #print(stdout)
            self.pump()
            

        except Exception as e:
            self.ip_search_process = None
            print("Sniffer error: ", e)

        #self.text.after(0, lambda: self._update_text_with_ports(eval(stdout)))
        #self.is_ip_search_running = False
    
    def _update_text_with_ports(self, stat_list):

        self.is_ip_search_running = False  # ‼️🔥 костыль, адский.
        # В идеале Thread для снифера отслеживать и при заршении  эту переменную занулять. Но мне че-та похуй как-то

        self.text.config(state='normal')
        self.text.delete("1.0", tk.END)

        try:
            stat_list = eval(stat_list)
            if not (type(stat_list) is list):
                raise Exception("stat_list not a list type")
        except:
            self.text.insert(tk.END, f"sniffer ERROR ;( ")
            self.text.config(state='disabled')
            return

        # Настройка жирного шрифта (однократно)
        if not hasattr(self, "bold_font"):
            self.bold_font = font.Font(self.text, self.text.cget("font"))
            self.bold_font.configure(weight="bold", size=12)
            self.text.tag_configure("bold", font=self.bold_font)


        for elem in stat_list:
            ip,percent = elem
    
            self.text.insert(tk.END, f"FROM: ")
            self.text.insert(tk.END, f"{ip} \t", "bold")
            self.text.insert(tk.END, f'trafic: {percent}\n')

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
            elif not (self.udp_var.get() or self.tcp_var.get()):
                messagebox.showwarning("Warning", "Choose protocol (TCP/UDP)")
                self.toggle_state = False
                return
            elif not self.ip_var.get():
                messagebox.showwarning("Warning", "Choose IP address")
                self.toggle_state = False
                return
            elif not self.validate_ip(self.ip_var.get()):
                messagebox.showwarning("Warning", "The IP address is not correct!")
                self.toggle_state = False
                return
            
            self.toggle_button.config(text="ON", bg="green")

            cmd = [sys.executable,
                    "--packet-control",
                    "--target_ip",   str(self.ip_var.get()),
                    "--in",          str(self.in_var.get()),
                    "--out",         str(self.out_var.get()),
                    "--tcp",         str(self.tcp_var.get()),
                    "--udp",         str(self.udp_var.get()),
                    "--key",         str(self.switch_btn),
                    "--switch_type", str(self.switch_type_var.get()),] 
            
            if getattr(sys, "frozen", True):  # Если мы запустились через py venv
                cmd = cmd[:1] + ["interface.py",] + cmd[1:]

            #print(cmd)
            self.lag_switch_process = subprocess.Popen(cmd)

        else:
            self.toggle_button.config(text="OFF", bg="red")
            subprocess.run(f'taskkill /F /T /PID {self.lag_switch_process.pid}', shell=True)
            #self.lag_switch_process.kill()
    
    def on_close(self):
        # Вроде все норм, нормально убивает дочек, но я хз че если будет ошибка, и возможны ли ошибки
        if hasattr(self, 'lag_switch_process') and self.lag_switch_process:
            try:
                subprocess.run(f'taskkill /F /T /PID {self.lag_switch_process.pid}', shell=True)
                #self.lag_switch_process.kill()
            except Exception as e:
                print("Failed to terminate process:", e)
            
            self.root.destroy()

        if hasattr(self, 'ip_search_process') and self.ip_search_process:
            try:
                subprocess.run(f'taskkill /F /T /PID {self.ip_search_process.pid}', shell=True)
            except Exception as e:
                print("Failed to terminate port search process:", e)
        
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


# фикс под другие расскладки 
# https://ru.stackoverflow.com/questions/722885/%D0%92%D1%81%D1%82%D0%B0%D0%B2%D0%BA%D0%B0-%D0%B8%D0%B7-%D0%B1%D1%83%D1%84%D0%B5%D1%80%D0%B0-%D0%B2-tkinter-%D0%B3%D0%BE%D1%80%D1%8F%D1%87%D0%B8%D0%BC%D0%B8-%D0%BA%D0%BB%D0%B0%D0%B2%D0%B8%D1%88%D0%B0%D0%BC%D0%B8-%D0%B2-%D1%80%D1%83%D1%81%D1%81%D0%BA%D0%BE%D0%B9-%D1%80%D0%B0%D1%81%D0%BA%D0%BB%D0%B0%D0%B4%D0%BA%D0%B5
def CopyPaste(e):
    if e.keycode == 86 and e.keysym != 'v':
        e.widget.event_generate('<<Paste>>')
    elif e.keycode == 67 and e.keysym != 'c':
        e.widget.event_generate('<<Copy>>')
    elif e.keycode == 88 and e.keysym != 'x':
        e.widget.event_generate('<<Cut>>')

def main():
    global root,app

    if "--sniffer" in sys.argv:
        # 
        from connection import ip_sniff
        ip_sniff()
        return
    
    if "--packet-control" in sys.argv:
        # 
        from connection import packet_control
        #print(sys.argv)
        #i = sys.argv.index("--packet-control") 
        try:
            # кому не похуй, сделайте цикл 💩🤝
            target_ip   = sys.argv[sys.argv.index("--target_ip")  + 1]
            inbound     = sys.argv[sys.argv.index("--in")  + 1].lower() == 'true'  # Преобразуем строку в bool
            outbound    = sys.argv[sys.argv.index("--out")  + 1].lower() == 'true'
            tcp         = sys.argv[sys.argv.index("--tcp")  + 1].lower() == 'true'
            udp         = sys.argv[sys.argv.index("--udp")  + 1].lower() == 'true'
            key         = sys.argv[sys.argv.index("--key")  + 1]
            switch_type = sys.argv[sys.argv.index("--switch_type") + 1].lower()
        except IndexError:
            #print("Недостаточно аргументов для запуска packet-control!")
            return

        # Передаем все эти параметры в packet_control
        packet_control(target_ip, inbound, outbound, tcp, udp, key, switch_type)
        return

    
    root = tk.Tk()
    app = AdvancedToggleApp(root)
    root.bind("<Control-Key>", CopyPaste)
    root.mainloop()

if __name__ == "__main__":
    main()
