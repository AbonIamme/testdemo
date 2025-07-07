import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class WaveformPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Waveform Plotter")
        self.waveforms = []  # Stores standard waveforms
        self.custom_waveforms = []  # Stores custom (x,y) waveforms
        self.setup_ui()

    def setup_ui(self):
        # Notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Standard Input Tab
        std_frame = ttk.Frame(notebook)
        notebook.add(std_frame, text="Standard Input")

        # Advanced Input Tab
        adv_frame = ttk.Frame(notebook)
        notebook.add(adv_frame, text="Advanced Input")

        # Setup standard input UI
        self.setup_standard_ui(std_frame)
        # Setup advanced input UI
        self.setup_advanced_ui(adv_frame)

        # Plot Frame (shared)
        self.plot_frame = ttk.Frame(self.root)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)

    def setup_standard_ui(self, parent):
        # Standard input widgets (same as before)
        input_frame = ttk.LabelFrame(parent, text="Standard Waveform Parameters", padding="10")
        input_frame.pack(fill=tk.X, pady=5)

        ttk.Label(input_frame, text="Period (ms):").grid(row=0, column=0, sticky=tk.W)
        self.period_entry = ttk.Entry(input_frame)
        self.period_entry.grid(row=0, column=1, sticky=tk.EW)
        self.period_entry.insert(0, "10")

        ttk.Label(input_frame, text="Start Time (ms):").grid(row=1, column=0, sticky=tk.W)
        self.start_entry = ttk.Entry(input_frame)
        self.start_entry.grid(row=1, column=1, sticky=tk.EW)
        self.start_entry.insert(0, "0")

        ttk.Label(input_frame, text="Stop Time (ms):").grid(row=2, column=0, sticky=tk.W)
        self.stop_entry = ttk.Entry(input_frame)
        self.stop_entry.grid(row=2, column=1, sticky=tk.EW)
        self.stop_entry.insert(0, "10")

        ttk.Label(input_frame, text="Delay (ms):").grid(row=3, column=0, sticky=tk.W)
        self.delay_entry = ttk.Entry(input_frame)
        self.delay_entry.grid(row=3, column=1, sticky=tk.EW)
        self.delay_entry.insert(0, "0")

        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Add Standard Waveform", command=self.add_standard_waveform).pack(side=tk.LEFT, padx=5)

    def setup_advanced_ui(self, parent):
        # Advanced input widgets
        adv_input_frame = ttk.LabelFrame(parent, text="Custom Waveform Points", padding="10")
        adv_input_frame.pack(fill=tk.BOTH, expand=True)

        # Points entry frame
        points_frame = ttk.Frame(adv_input_frame)
        points_frame.pack(fill=tk.X, pady=5)

        ttk.Label(points_frame, text="Time (ms):").pack(side=tk.LEFT)
        self.time_entry = ttk.Entry(points_frame, width=10)
        self.time_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(points_frame, text="Value:").pack(side=tk.LEFT)
        self.value_entry = ttk.Entry(points_frame, width=10)
        self.value_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(points_frame, text="Add Point", command=self.add_point).pack(side=tk.LEFT, padx=5)

        # Points list
        self.points_list = tk.Listbox(adv_input_frame, height=6)
        self.points_list.pack(fill=tk.BOTH, expand=True, pady=5)

        # Waveform controls
        ctrl_frame = ttk.Frame(adv_input_frame)
        ctrl_frame.pack(fill=tk.X)

        ttk.Button(ctrl_frame, text="Clear Points", command=self.clear_points).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl_frame, text="Add Custom Waveform", command=self.add_custom_waveform).pack(side=tk.LEFT, padx=5)

    def add_standard_waveform(self):
        try:
            period = float(self.period_entry.get())
            start = float(self.start_entry.get())
            stop = float(self.stop_entry.get())
            delay = float(self.delay_entry.get())

            self.waveforms.append({
                "type": "standard",
                "period": period,
                "start": start,
                "stop": stop,
                "delay": delay
            })
            messagebox.showinfo("Success", "Standard waveform added!")
        except ValueError:
            messagebox.showerror("Error", "Invalid input!")

    def add_point(self):
        try:
            time = float(self.time_entry.get())
            value = float(self.value_entry.get())
            self.points_list.insert(tk.END, f"{time} ms: {value}")
            self.time_entry.delete(0, tk.END)
            self.value_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Invalid time or value!")

    def clear_points(self):
        self.points_list.delete(0, tk.END)

    def add_custom_waveform(self):
        points = []
        for i in range(self.points_list.size()):
            item = self.points_list.get(i)
            time, value = item.split(" ms: ")
            points.append((float(time), float(value)))

        if len(points) < 2:
            messagebox.showerror("Error", "Need at least 2 points!")
            return

        self.custom_waveforms.append({
            "type": "custom",
            "points": sorted(points, key=lambda x: x[0])  # Sort by time
        })
        self.clear_points()
        messagebox.showinfo("Success", "Custom waveform added!")

    def generate_plot(self):
        # Clear previous plot
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        if not self.waveforms and not self.custom_waveforms:
            messagebox.showerror("Error", "No waveforms to plot!")
            return

        # Create figure with subplots
        num_waveforms = len(self.waveforms) + len(self.custom_waveforms)
        fig, axes = plt.subplots(num_waveforms, 1, figsize=(10, 2 * num_waveforms), sharex=True)
        if num_waveforms == 1:
            axes = [axes]

        current_ax = 0

        # Plot standard waveforms
        for i, waveform in enumerate(self.waveforms):
            if waveform["type"] != "standard":
                continue

            period = waveform["period"] * 1e-3
            start = waveform["start"] * 1e-3
            stop = waveform["stop"] * 1e-3
            delay = waveform["delay"] * 1e-3

            t = np.linspace(start, stop, 5000)
            signal = (np.mod(t - delay, period) < period/2).astype(float)

            ax = axes[current_ax]
            ax.plot(t * 1e3, signal, 'b-', linewidth=1.5, drawstyle='steps-pre')
            ax.set_ylabel(f"Standard {i+1}\nVoltage")
            ax.set_yticks([0, 1], ['Low', 'High'])
            ax.grid(True, linestyle='--', alpha=0.5)
            current_ax += 1

        # Plot custom waveforms
        for i, waveform in enumerate(self.custom_waveforms):
            if waveform["type"] != "custom":
                continue

            points = waveform["points"]
            x = [p[0] for p in points]
            y = [p[1] for p in points]

            ax = axes[current_ax]
            ax.step(x, y, 'r-', where='post', linewidth=1.5)
            ax.set_ylabel(f"Custom {i+1}\nValue")
            ax.grid(True, linestyle='--', alpha=0.5)
            current_ax += 1

        # Common X-axis
        axes[-1].set_xlabel('Time (ms)')
        fig.tight_layout()

        # Embed plot
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def clear_all(self):
        self.waveforms = []
        self.custom_waveforms = []
        self.clear_points()
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    
    # Add main control buttons at bottom
    app = WaveformPlotterApp(root)
    
    control_frame = ttk.Frame(root)
    control_frame.pack(fill=tk.X, pady=5)
    
    ttk.Button(control_frame, text="Generate Plot", command=app.generate_plot).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Clear All", command=app.clear_all).pack(side=tk.LEFT, padx=5)
    
    root.mainloop()