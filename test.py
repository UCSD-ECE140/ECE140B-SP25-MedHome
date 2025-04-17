import customtkinter as ctk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import random

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class MedHomeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MedHome - Smart Health Chair")
        self.geometry("1000x600")
        self.resizable(True, True)

        self.login_frame = LoginFrame(self, self.open_dashboard)
        self.login_frame.pack(fill="both", expand=True)

    def open_dashboard(self):
        self.login_frame.pack_forget()
        self.dashboard = DashboardFrame(self)
        self.dashboard.pack(fill="both", expand=True)

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, login_callback):
        super().__init__(master)

        self.login_callback = login_callback

        ctk.CTkLabel(self, text="Welcome to MedHome", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=40)

        self.username = ctk.CTkEntry(self, placeholder_text="Username")
        self.username.pack(pady=10)

        self.password = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password.pack(pady=10)

        self.login_button = ctk.CTkButton(self, text="Login", command=self.login_callback)
        self.login_button.pack(pady=20)

        self.signup_button = ctk.CTkButton(self, text="Create New Account", fg_color="transparent", border_width=1)
        self.signup_button.pack()

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        title = ctk.CTkLabel(self, text="🩺 MedHome Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(20, 10))

        self.vitals_box = ctk.CTkFrame(self, corner_radius=10)
        self.vitals_box.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.vitals_label = ctk.CTkLabel(self.vitals_box, text="Live Vitals", font=ctk.CTkFont(size=18, weight="bold"))
        self.vitals_label.pack(pady=10)

        self.bp_label = ctk.CTkLabel(self.vitals_box, text="Blood Pressure: 120/80 mmHg")
        self.bp_label.pack(pady=5)

        self.ox_label = ctk.CTkLabel(self.vitals_box, text="Oxygen Level: 98%")
        self.ox_label.pack(pady=5)

        self.hr_label = ctk.CTkLabel(self.vitals_box, text="Heart Rate: 72 bpm")
        self.hr_label.pack(pady=5)

        self.weight_label = ctk.CTkLabel(self.vitals_box, text="Weight: 70 kg")
        self.weight_label.pack(pady=5)

        self.refresh_btn = ctk.CTkButton(self.vitals_box, text="🔄 Refresh Vitals", command=self.refresh_vitals)
        self.refresh_btn.pack(pady=10)

        self.graph_frame = ctk.CTkFrame(self, corner_radius=10)
        self.graph_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")

        self.create_graph()

        self.alert_btn = ctk.CTkButton(self, text="⚠️ Check Alerts", command=self.fake_alert)
        self.alert_btn.grid(row=2, column=0, padx=20, pady=20)

        self.doctor_btn = ctk.CTkButton(self, text="👨‍⚕️ Consult Doctor", fg_color="#3498db")
        self.doctor_btn.grid(row=2, column=1, padx=20, pady=20)

    def create_graph(self):
        fig, ax = plt.subplots(figsize=(5, 2))
        ax.plot([random.randint(70, 100) for _ in range(10)], marker='o')
        ax.set_title("Oxygen Level Trend")
        ax.set_ylabel("%")

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=10, pady=10)

    def refresh_vitals(self):
        # Replace with real sensor/database calls
        new_hr = random.randint(65, 95)
        new_ox = random.randint(95, 100)
        new_bp = f"{random.randint(110, 130)}/{random.randint(70, 85)}"
        new_wt = round(random.uniform(60, 80), 1)

        self.hr_label.configure(text=f"Heart Rate: {new_hr} bpm")
        self.ox_label.configure(text=f"Oxygen Level: {new_ox}%")
        self.bp_label.configure(text=f"Blood Pressure: {new_bp} mmHg")
        self.weight_label.configure(text=f"Weight: {new_wt} kg")

    def fake_alert(self):
        ctk.CTkMessagebox.show_info(title="Alert", message="No anomalies detected at this time.")

if __name__ == "__main__":
    app = MedHomeApp()
    app.mainloop()
