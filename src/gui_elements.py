"""
Helper functions and classes for the TK app
"""

from __future__ import annotations
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.image import AxesImage
import numpy as np
from typing import Callable


class Entry(ctk.CTkEntry):
    """
    Entry element, with linked variable
    """

    def __init__(self, *arg, **kwargs):
        """
        The arguments are the same as for `ctk.CTkEntry.__init__()`

        Additional optional arguments:
            - command: function called when the entry text is updated

        The `command` callback should have the following signature:
            `callback(reference: Entry, text: str)`
        where:
            - reference: Reference to this Entry object
            - text: Updated text of the entry
        """
        self.variable = tk.StringVar()  # text variable associated to the entry
        self._user_callback = None  # called when the text is being updated

        if "command" in kwargs:
            self._user_callback = kwargs["command"]
            kwargs.pop("command")

        self.variable.trace_add("write", self._update_cb)

        ctk.CTkEntry.__init__(self, *arg, **kwargs, textvariable=self.variable)

    def set_callback(self, callback: Callable[[Entry, str]]):
        """
        Args:
            - callback: function called when the entry text is updated

        The `callback` function should have the following signature:
            `callback(reference: Entry, text: str)`
        where:
            - reference: Reference to this Entry object
            - text: Updated text of the entry
        """
        self._user_callback = callback

    def _update_cb(self, *_):
        """
        Called when the variable is being called. Calls the user defined callback.
        """
        if self._user_callback is not None:
            self._user_callback(self, self.variable.get())

    def get_value(self) -> str:
        """
        Returns the value stored in the variable
        """
        return self.variable.get()

    def set_value(self, value):
        """
        Updates the displayed value, doesn't trigger the callback
        """
        self.variable.set(str(value))


class TkImage:
    """
    References a Matplotlib image figure in a TK widget
    """

    def __init__(self, master: ctk.CTkBaseClass):
        """
        TODO
        """
        self._fig = Figure(layout="tight")
        self._fig.patch.set_facecolor("xkcd:mint green")
        self._ax: Axes = self._fig.add_subplot(111)
        self._ax.set_axis_off()
        self._tk_canvas = FigureCanvasTkAgg(self._fig, master=master)

        self._img: None | AxesImage = None

    def update(self, img: np.ndarray):
        """
        Updates the image given a raw image (Numpy array)
        """
        if self._img is None:
            self._img = self._ax.imshow(img, aspect="auto")
            self._fig.tight_layout()
            self._fig.subplots_adjust(bottom=0, top=1, left=0, right=1)
        else:
            self._img.set_data(img)

        self._tk_canvas.draw()

    def get_tk_canvas(self) -> tk.Canvas:
        """
        TODO
        """
        return self._tk_canvas.get_tk_widget()


class TkImage2:
    """
    TODO
    """

    def __init__(self, master: ctk.CTkBaseClass):
        """
        TODO
        """
        self._img = None
        self._canvas_img = None
        self._canvas = tk.Canvas(master)

    def update(self, img: np.ndarray):
        """
        Updates the image given a raw image (Numpy array)
        """
        if self._canvas_img is not None:
            self._canvas.delete(self._canvas_img)

        size = (self._canvas.winfo_width(), self._canvas.winfo_height())
        self._img = ImageTk.PhotoImage(Image.fromarray(img).resize(size))
        self._canvas_img = self._canvas.create_image(0, 0, image=self._img, anchor="nw")

    def get_tk_canvas(self) -> tk.Canvas:
        """
        TODO
        """
        return self._canvas


class RectangleSelectionWindow(ctk.CTkToplevel):
    """
    Used to select a screen area with the mouse
    """

    def __init__(self, screen_img, *args, **kwargs):
        self._screen_img = np.asarray(screen_img)

        # Start new window
        super().__init__(*args, **kwargs)
        self.attributes("-fullscreen", True)  # TODO: bring this back
        self.config(cursor="cross")
        self.bind("<Escape>", lambda _: self.destroy())

        # Display screenshot image here
        self._img = TkImage(self)  # type: ignore
        self._canvas = self._img.get_tk_canvas()
        self._canvas.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._img.update(self._screen_img)

        # Set the logic up
        self._callback = None  # will be called when the selection is complete
        self._is_mouse_pressed = False  # whether the left mouse button is pressed
        self._start_mouse_position = None  # position of the cursor when pressed down
        self._mouse_position = None  # current mouse position
        self._canvas_rect = None  # reference to drawn selection rectangle outline
        self._canvas_rect_fill = None  # reference to drawn selection rectangle fill
        self._fill_img = None  # PIL image used to draw rectangle fill

        self.bind("<Button-1>", self._mouse_down_cb)
        self.bind("<ButtonRelease-1>", self._mouse_up_cb)
        self.bind("<B1-Motion>", self._mouse_motion_cb)

        self.after(10, self._main_loop)

    def attach_cb(self, callback: Callable[[int, int, int, int]]):
        """
        Attaches a function that will be called when the selection has been done

        Args:
            - callback: function with signature `cb(xmin, ymin, xmax, ymax)`
        """
        self._callback = callback

    def _main_loop(self):
        """
        Periodically updates the displayed image if the mouse has moved
        """
        if (
            not self._is_mouse_pressed
            or self._start_mouse_position is None
            or self._mouse_position is None
        ):
            self.after(50, self._main_loop)
            return

        if self._canvas_rect is not None:
            self._canvas.delete(self._canvas_rect)

        if self._canvas_rect_fill is not None:
            self._canvas.delete(self._canvas_rect_fill)

        def __create_rectangle_fill(x1, y1, x2, y2, **kwargs):
            if x1 > x2:
                (x1, x2) = (x2, x1)
            if y1 > y2:
                (y1, y2) = (y2, y1)

            if not "alpha" in kwargs:
                return None, None
            alpha = int(kwargs.pop("alpha") * 255)
            fill = kwargs.pop("fill")
            fill = self.winfo_rgb(fill) + (alpha,)
            image = Image.new("RGBA", (x2 - x1, y2 - y1), fill)

            fill_img = ImageTk.PhotoImage(image)
            canvas_rect = self._canvas.create_image(x1, y1, image=fill_img, anchor="nw")

            return canvas_rect, fill_img

        self._canvas_rect_fill, self._fill_img = __create_rectangle_fill(
            self._start_mouse_position[0],
            self._start_mouse_position[1],
            self._mouse_position[0],
            self._mouse_position[1],
            width=0,
            fill="white",
            alpha=0.5,
        )
        self._canvas_rect = self._canvas.create_rectangle(
            self._start_mouse_position[0],
            self._start_mouse_position[1],
            self._mouse_position[0],
            self._mouse_position[1],
            width=1,
            outline="white",
        )

        self.after(50, self._main_loop)

    def _mouse_down_cb(self, event: tk.Event):
        """
        Called when the left mouse button is pressed down
        """
        self._is_mouse_pressed = True
        self._start_mouse_position = [event.x, event.y]

    def _mouse_up_cb(self, event: tk.Event):
        """
        Called when the left mouse button is pressed up
        Calls the selection callback, and kills the window
        """
        if self._is_mouse_pressed:
            if not self._callback is None and not self._start_mouse_position is None:
                self._callback(
                    min(self._start_mouse_position[1], event.y),
                    min(self._start_mouse_position[0], event.x),
                    max(self._start_mouse_position[1], event.y),
                    max(self._start_mouse_position[0], event.x),
                )  # note: the x and y coordinates are reversed

            self.destroy()

    def _mouse_motion_cb(self, event: tk.Event):
        """
        Called when the mouse is moving while the left button is pressed
        """
        self._mouse_position = [event.x, event.y]
