import tkinter as tk
import ttkbootstrap as ttk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import utilities.celestial_engine as celestial_engine

class LOPPlotPage(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        self.add_lop_plot()
        self.draw_canvas()
        
    def add_lop_plot(self):
        # Create canvas
        self.canvas_lop = tk.Canvas(self)

        # Get figure from lop_plot 
        self.lop_plot = celestial_engine.plt.figure(2)
        self.lop_plot.set_facecolor('#222222')

        # Add figure to canvas
        self.lop_plot_canvas = FigureCanvasTkAgg(self.lop_plot, master=self.canvas_lop)

        # Add toolbar to canvas
        self.lop_plot_toolbar = NavigationToolbar2Tk(self.lop_plot_canvas, self.canvas_lop)
        self.lop_plot_toolbar.update()

        # Grid layout for toolbar, canvas, and plot canvas widget
        self.lop_plot_toolbar.pack(side=tk.TOP, fill=tk.BOTH, expand=1, pady = 0)
        self.canvas_lop.pack(side=tk.TOP, fill=tk.BOTH, expand=1, pady = 0)
        self.lop_plot_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1, pady = 0)

    def draw_canvas(self):
        # draw canvas
        self.lop_plot_canvas.draw()

    def refresh_figure(self):
        self.draw_canvas()


