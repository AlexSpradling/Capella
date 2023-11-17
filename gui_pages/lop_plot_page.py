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
        #create canvas, make it large 
        self.canvas_lop = tk.Canvas(self, width=800, height=800)
        
        # get figure from lop_plot 
        self.lop_plot = celestial_engine.plt.figure(2)
        self.lop_plot.set_facecolor('#222222')

        # add figure to canvas
        self.lop_plot_canvas = FigureCanvasTkAgg(self.lop_plot, master=self.canvas_lop)
        
        # add toolbar to canvas
        self.lop_plot_toolbar = NavigationToolbar2Tk(self.lop_plot_canvas, self.canvas_lop)
        self.lop_plot_toolbar.update()

        # packing order is important!
        self.lop_plot_toolbar.pack(side=tk.BOTTOM, fill='both', expand=True)
        self.canvas_lop.pack(side=tk.TOP, fill='both', expand=True)
        self.lop_plot_canvas.get_tk_widget().pack(side=tk.BOTTOM, fill='both', expand=True)

    def draw_canvas(self):
        # draw canvas
        self.lop_plot_canvas.draw()

    def refresh_figure(self):
        self.draw_canvas()


