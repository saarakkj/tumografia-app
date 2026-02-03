

import serial
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# ===============================
# GRBL CONTROLLER
# ===============================
class GrblController:
    def __init__(self):
        self.ser = None
        self.connected = False

    def connect(self, port, baud=115200):
        self.ser = serial.Serial(port, baud, timeout=1)
        time.sleep(2)
        self.wakeup()
        self.connected = True

    def wakeup(self):
        self.send_raw("\r\n\r\n")
        time.sleep(2)
        self.ser.reset_input_buffer()

    def send_raw(self, cmd):
        if self.ser:
            self.ser.write(cmd.encode())

    def send(self, cmd):
        if not self.connected:
            return
        self.send_raw(cmd + "\n")

    def home(self):
        self.send("$H")

    def move_xy(self, x, y, feed=1000):
        self.send("G90")  # absoluto
        self.send(f"G1 X{x} Y{y} F{feed}")

    def jog(self, dx, dy, feed=1000):
        self.send(f"$J=G91 X{dx} Y{dy} F{feed}")

    def stop(self):
        self.send_raw("!")  # feed hold

    def reset(self):
        self.send_raw("\x18")  # CTRL+X

    def close(self):
        if self.ser:
            self.ser.close()
            self.connected = False


# ===============================
# GUI
# ===============================
class GrblGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini LaserGRBL - Python")
        self.grbl = GrblController()

        self.create_widgets()

    def create_widgets(self):
        # Conexão
        conn = ttk.LabelFrame(self.root, text="Conexão")
        conn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(conn, text="Porta COM:").grid(row=0, column=0)
        self.port_entry = ttk.Entry(conn, width=10)
        self.port_entry.insert(0, "COM3")
        self.port_entry.grid(row=0, column=1)

        ttk.Button(conn, text="Conectar", command=self.connect).grid(row=0, column=2, padx=5)
        ttk.Button(conn, text="Home", command=self.grbl.home).grid(row=0, column=3, padx=5)

        # Jog
        jog = ttk.LabelFrame(self.root, text="Jog Manual")
        jog.grid(row=1, column=0, padx=10, pady=10)

        self.step = tk.DoubleVar(value=1)

        ttk.Label(jog, text="Passo (mm):").grid(row=0, column=1)
        ttk.Entry(jog, textvariable=self.step, width=5).grid(row=0, column=2)

        ttk.Button(jog, text="↑", width=5, command=lambda: self.jog(0, self.step.get())).grid(row=1, column=1)
        ttk.Button(jog, text="↓", width=5, command=lambda: self.jog(0, -self.step.get())).grid(row=3, column=1)
        ttk.Button(jog, text="←", width=5, command=lambda: self.jog(-self.step.get(), 0)).grid(row=2, column=0)
        ttk.Button(jog, text="→", width=5, command=lambda: self.jog(self.step.get(), 0)).grid(row=2, column=2)

        # Move absoluto
        absf = ttk.LabelFrame(self.root, text="Mover Absoluto")
        absf.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(absf, text="X:").grid(row=0, column=0)
        ttk.Label(absf, text="Y:").grid(row=0, column=2)

        self.x_entry = ttk.Entry(absf, width=7)
        self.y_entry = ttk.Entry(absf, width=7)
        self.x_entry.grid(row=0, column=1)
        self.y_entry.grid(row=0, column=3)

        ttk.Button(absf, text="Mover", command=self.move_absolute).grid(row=0, column=4, padx=5)

        # Controle
        ctrl = ttk.LabelFrame(self.root, text="Controle")
        ctrl.grid(row=3, column=0, padx=10, pady=10)

        ttk.Button(ctrl, text="STOP", command=self.grbl.stop).grid(row=0, column=0, padx=5)
        ttk.Button(ctrl, text="RESET", command=self.grbl.reset).grid(row=0, column=1, padx=5)

    def connect(self):
        try:
            self.grbl.connect(self.port_entry.get())
            messagebox.showinfo("Conectado", "GRBL conectado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def jog(self, dx, dy):
        self.grbl.jog(dx, dy)

    def move_absolute(self):
        try:
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            self.grbl.move_xy(x, y)
        except:
            messagebox.showerror("Erro", "X e Y inválidos")


# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    root = tk.Tk()
    app = GrblGUI(root)
    root.mainloop()
