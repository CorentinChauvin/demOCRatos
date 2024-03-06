"""
Classes and functions to draw stuff in the app
"""

import tkinter as tk
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
# from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib.image import AxesImage
import numpy as np


class Graph:
    """
    Displays a Matplotlib graph in tk
    """
    def __init__(self):
        pass  # TODO


class TkImage:
    """
    References a Matplotlib image figure in a TK widget
    """
    def __init__(self, master: ctk.CTkBaseClass):
        """
        TODO
        """
        self._fig = Figure(layout="tight")
        self._ax = self._fig.add_subplot(111)
        self._ax.set_axis_off()
        self._tk_canvas = FigureCanvasTkAgg(self._fig, master=master)

        self._img: None | AxesImage = None
        # self._tk_canvas.draw()

    def update(self, img: np.ndarray):
        """
        Updates the image given a raw image (Numpy array)
        """
        if self._img is None:
            self._img = self._ax.imshow(img)
        else:
            self._img.set_data(img)

        self._tk_canvas.draw()

    def get_tk_canvas(self) -> tk.Canvas:
        """
        TODO
        """
        return self._tk_canvas.get_tk_widget()


def create_tk_figure(figure: Figure, master: ctk.CTkBaseClass) -> tk.Canvas:
    """
    Creates a TK widget from a Matplotlib figure
    """
    canvas = FigureCanvasTkAgg(figure, master=master)
    canvas.draw()
    return canvas.get_tk_widget()


def create_the_button(root):
    from PIL import ImageGrab
    from matplotlib import pyplot as plt

    im2 = ImageGrab.grab(bbox =(0, 0, 500, 300))
    im2 = np.asarray(im2)

    # fig = plt.figure()
    # fig.set_size_inches((5, 4))
    # ax = plt.Axes(fig, [0., 0., 1., 1.])
    # ax.set_axis_off()
    # ax.imshow(im2)
    # plt.savefig("test", dpi=100)
    fig = Figure(figsize=(5, 4), dpi=100, layout="tight")
    ax = fig.add_subplot(111)
    ax.imshow(im2)
    ax.set_axis_off()

    canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=0)
    canvas.get_tk_widget().grid(padx=(10, 10), pady=(10, 10))

    # toolbar = NavigationToolbar2Tk(canvas, root)
    # toolbar.update()
    # canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    return canvas



# from PIL import ImageGrab
# from matplotlib import pyplot as plt
#
# im2 = ImageGrab.grab(bbox =(0, 0, 500, 300))
# # im2.show()
# im2 = np.asarray(im2)
# plt.imshow(im2)
# plt.show()
