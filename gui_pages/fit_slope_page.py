import tkinter as tk
import ttkbootstrap as ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import utilities.celestial_engine as celestial_engine

class FitSlopePage(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        self.fit_slope_plot()
        self.draw_canvas()
        

    def fit_slope_plot(self):
        #create canvas
        self.canvas_fit_slope = tk.Canvas(self, width=800, height=800)

        # get figure from lop_plot 
        self.fit_slope_scatter_plot = celestial_engine.plt.figure(1)
        self.fit_slope_scatter_plot.set_facecolor('#222222')

        # add figure to canvas
        self.fit_slope_scatter_plot_canvas = FigureCanvasTkAgg(self.fit_slope_scatter_plot, master=self.canvas_fit_slope)
        
        # add toolbar to canvas
        self.fit_slope_scatter_plot_toolbar = NavigationToolbar2Tk(self.fit_slope_scatter_plot_canvas, self.canvas_fit_slope)

        # update
        self.fit_slope_scatter_plot_toolbar.update()

        # packing order is important! 
        self.fit_slope_scatter_plot_toolbar.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.canvas_fit_slope.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.fit_slope_scatter_plot_canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
   
    def draw_canvas(self):
        # draw canvas
        self.fit_slope_scatter_plot_canvas.draw()

    def refresh_figure(self):
        self.draw_canvas()
