"""
TODO
"""

from src.ocr import BaseOcrEngine
from src.data_recorder import DataRecorder
from src.capture import Captures
from src.gui_elements import Entry, RectangleSelectionWindow
import customtkinter as ctk
import tkinter as tk
import mss
from PIL import Image
import numpy as np
from copy import deepcopy
from time import time
from typing import Callable, Type
import sys


ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue


class App(ctk.CTk):
    """
    TODO
    """

    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Title TODO")
        # self.geometry(f"{1100}x{580}")
        self.bind("<Escape>", lambda _: sys.exit())  # FIXME: for development only
        self.bind("q", lambda _: sys.exit())  # FIXME: for development only

        self._rect_selec_window = None  # reference to the window to select the capture zone

        # Create the frames
        self._pad = 10
        self._create_header_frame()
        self._create_options_frame()
        self._create_output_frame()

        self._header_frame.grid(row=0, column=0, sticky="nsew")
        self._options_frame.grid(row=1, column=0, sticky="nsew")
        self._output_frame.grid(row=2, column=0, sticky="nsew")

        self._header_frame.grid(padx=(self._pad, self._pad), pady=(self._pad, 0))
        self._options_frame.grid(padx=(self._pad, self._pad), pady=(0, self._pad))
        self._output_frame.grid(padx=(self._pad, self._pad), pady=(0, self._pad))

        # Create captures
        self._captures = Captures(self._output_frame)
        self._selected_capture = self._captures.get_first()  # its config is displayed

        self._captures.update_layout()
        self._selected_capture.set_area(0, 0, 420, 420)
        self._sct = mss.mss()  # used to capture the screen

        self._data_recorder = DataRecorder()
        self._data_recorder.add_field(self._selected_capture.name)

        # Configure the grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)

        # Set default values and statuses
        self._stop_btn.configure(state="disabled")  # TODO: change state dynamically

        self._status_txt.configure(text="10:03 (12 FPS)")
        self._status_txt.configure(
            fg_color="green", text_color="white"
        )  # TODO: change the colour depending on the status

        self._fps_settings_menu.set("10")
        self._ocr_settings_menu.set("Tesseract")

        self._update_capture_options()
        self._captures.update_layout()

        # Configure callbacks
        self._fps = 10.0
        self.after(int(1000.0 / self._fps), self._main_loop)

    def _create_header_frame(self):
        """
        Creating the heading frame with main controls
        """
        self._header_frame = ctk.CTkFrame(self, corner_radius=10)

        def __start_btn_cb():
            self._data_recorder.toggle_recording(True)
            self._start_btn.configure(state="disabled")
            self._stop_btn.configure(state="normal")

        def __stop_btn_cb():
            self._data_recorder.toggle_recording(False)
            self._start_btn.configure(state="normal")
            self._stop_btn.configure(state="disabled")

        self._start_btn = ctk.CTkButton(
            master=self._header_frame, height=40, text="Start", command=__start_btn_cb
        )
        self._stop_btn = ctk.CTkButton(
            master=self._header_frame, height=40, text="Stop", command=__stop_btn_cb
        )
        self._status_txt = ctk.CTkLabel(self._header_frame, justify="right")

        # Grid placement of all children
        self._start_btn.grid(row=0, column=0)
        self._stop_btn.grid(row=0, column=1)
        self._status_txt.grid(row=0, column=2, sticky="e")
        self._header_frame.grid_columnconfigure((0, 1), weight=0)
        self._header_frame.grid_columnconfigure(2, weight=1)

        # Padding of all children
        self._start_btn.grid(padx=(self._pad, 0), pady=(self._pad, self._pad))
        self._stop_btn.grid(padx=(self._pad, 0), pady=(self._pad, self._pad))
        self._status_txt.grid(padx=(self._pad, self._pad), pady=(self._pad, self._pad))

    def _create_options_frame(self):
        """
        Creates the frame to configure everything
        """
        self._options_frame = ctk.CTkTabview(self, corner_radius=10, anchor="nw")
        self._captures_view = self._options_frame.add("Captures")
        self._output_view = self._options_frame.add("Output")
        self._settings_view = self._options_frame.add("Settings")
        self._logs_view = self._options_frame.add("Logs")

        self._create_captures_view()
        self._create_output_view()
        self._create_settings_view()
        self._create_logs_view()

    def _create_captures_view(self):
        """
        Creates the view to configure the OCR captures
        """

        # Menu and add/delete buttons row
        def __add_capture():
            self._selected_capture = self._captures.add_capture()
            self._data_recorder.add_field(self._selected_capture.name)
            self._update_capture_options()
            self._captures.update_layout()

        def __rename_capture():
            old_name = self._selected_capture.name
            dialog = ctk.CTkInputDialog(text="New capture name:", title="Renaming")
            name = dialog.get_input()

            if name is not None and self._captures.rename(self._selected_capture, name):
                self._data_recorder.rename_field(old_name, name)
                self._update_capture_options()
            else:
                print("Invalid name!")

        def __remove_capture():
            self._data_recorder.delete_field(self._selected_capture.name)
            self._captures.remove_capture(self._selected_capture.name)
            self._selected_capture = self._captures.get_first()
            self._data_recorder.add_field(
                self._selected_capture.name
            )  # in case a new one was created
            self._update_capture_options()
            self._captures.update_layout()

        self._captures_menu = ctk.CTkOptionMenu(
            self._captures_view,
            dynamic_resizing=False,
            width=290,
            command=lambda name: self._update_capture_options(name),
        )
        self._capture_add_btn = ctk.CTkButton(
            self._captures_view,
            text="Add",
            width=80,
            command=__add_capture,
        )
        self._capture_rename_btn = ctk.CTkButton(
            self._captures_view, text="Rename", width=80, command=__rename_capture
        )
        self._capture_remove_btn = ctk.CTkButton(
            self._captures_view, text="Remove", width=80, command=__remove_capture
        )

        # Rectangle settings row
        def __update_rect_area(*_):
            try:
                self._selected_capture.set_area(
                    int(self._rect_xmin_entry.get_value()),
                    int(self._rect_ymin_entry.get_value()),
                    int(self._rect_xmax_entry.get_value()),
                    int(self._rect_ymax_entry.get_value()),
                )
            except ValueError:
                return

        def __select_react_area_cb(xmin: int, ymin: int, xmax: int, ymax: int):
            self._selected_capture.set_area(xmin, ymin, xmax, ymax)
            self._update_capture_options()

        def __select_rect_area():
            if (
                self._rect_selec_window is None
                or not self._rect_selec_window.winfo_exists()
            ):
                self._rect_selec_window = RectangleSelectionWindow(
                    self
                )  # create window if its None or destroyed
                self._rect_selec_window.attach_cb(__select_react_area_cb)
            else:
                self._rect_selec_window.focus()  # if window exists focus it

        self._rect_txt = ctk.CTkLabel(self._captures_view, text="Area")
        self._rect_select_frame = ctk.CTkFrame(self._captures_view)
        self._rect_select_btn = ctk.CTkButton(
            self._captures_view, text="Select", width=80, command=__select_rect_area
        )

        self._rect_xmin_entry = Entry(
            master=self._rect_select_frame, width=50, command=__update_rect_area
        )
        self._rect_ymin_entry = Entry(
            master=self._rect_select_frame, width=50, command=__update_rect_area
        )
        self._rect_xmax_entry = Entry(
            master=self._rect_select_frame, width=50, command=__update_rect_area
        )
        self._rect_ymax_entry = Entry(
            master=self._rect_select_frame, width=50, command=__update_rect_area
        )

        self._captures_menu.grid(row=0, column=0, columnspan=2)
        self._capture_add_btn.grid(row=0, column=2)
        self._capture_rename_btn.grid(row=0, column=3)
        self._capture_remove_btn.grid(row=0, column=4)
        self._rect_txt.grid(row=1, column=0)
        self._rect_select_frame.grid(row=1, column=1)
        self._rect_select_btn.grid(row=1, column=2)

        self._rect_xmin_entry.grid(row=1, column=0)
        self._rect_ymin_entry.grid(row=1, column=1)
        self._rect_xmax_entry.grid(row=1, column=2)
        self._rect_ymax_entry.grid(row=1, column=3)

        self._captures_menu.grid(padx=(self._pad, 0), pady=(0, 0))
        self._capture_add_btn.grid(padx=(self._pad, 0), pady=(0, 0))
        self._capture_rename_btn.grid(padx=(self._pad, 0), pady=(0, 0))
        self._capture_remove_btn.grid(padx=(self._pad, self._pad), pady=(0, 0))
        self._rect_txt.grid(padx=(self._pad, 0), pady=(self._pad, 0))
        self._rect_select_frame.grid(padx=(self._pad, 0), pady=(self._pad, 0))
        self._rect_select_btn.grid(padx=(self._pad, 0), pady=(self._pad, 0))

        self._rect_xmin_entry.grid(padx=(self._pad, 0), pady=(0, 0))
        self._rect_ymin_entry.grid(padx=(self._pad, 0), pady=(0, 0))
        self._rect_xmax_entry.grid(padx=(self._pad, 0), pady=(0, 0))
        self._rect_ymax_entry.grid(padx=(self._pad, 0), pady=(0, 0))

        # Min/max row
        self._min_max_frame = ctk.CTkFrame(self._captures_view)
        self._min_label = ctk.CTkLabel(self._min_max_frame, text="Min")
        self._min_entry = ctk.CTkEntry(self._min_max_frame, width=100)
        self._max_label = ctk.CTkLabel(self._min_max_frame, text="Max")
        self._max_entry = ctk.CTkEntry(self._min_max_frame, width=100)

        self._min_max_frame.grid(row=2, column=0, columnspan=2, sticky="w")
        self._min_label.grid(row=0, column=0)
        self._min_entry.grid(row=0, column=1)
        self._max_label.grid(row=0, column=2)
        self._max_entry.grid(row=0, column=3)

        self._min_max_frame.grid(padx=(0, 0), pady=(self._pad, 0))
        self._min_label.grid(padx=(self._pad, 0), pady=(0, 0))
        self._min_entry.grid(padx=(self._pad, 0), pady=(0, 0))
        self._max_label.grid(padx=(2 * self._pad, 0), pady=(0, 0))
        self._max_entry.grid(padx=(self._pad, 0), pady=(0, 0))

        # Pre processing configuration
        self._pre_process_config_frame = PreProcessingConfigFrame(
            self._pad, self._captures_view
        )
        self._pre_process_config_frame.grid(row=3, column=0, columnspan=4, sticky="we")
        self._pre_process_config_frame.grid(padx=(0, 0), pady=(self._pad, 0))

        def __pre_process_config_cb(config: BaseOcrEngine.PreProcessConfig):
            self._selected_capture.set_pre_process_config(config)

        self._pre_process_config_frame.attach_update_cb(__pre_process_config_cb)

        # Show options row
        def __enable_capture_cb():
            enabled = bool(self._enable_output_cbox.get())
            self._selected_capture.is_enabled = enabled
            self._captures.update_layout()

        self._show_capture_frame = ctk.CTkFrame(self._captures_view)
        self._enable_output_cbox = ctk.CTkCheckBox(
            self._show_capture_frame, text="Enable output", command=__enable_capture_cb
        )
        self._show_graph_entry = ctk.CTkCheckBox(
            self._show_capture_frame, text="Show on graph"
        )

        self._show_capture_frame.grid(row=4, column=0, columnspan=4)
        self._enable_output_cbox.grid(row=0, column=0)
        self._show_graph_entry.grid(row=0, column=1)

        self._show_capture_frame.grid(padx=(0, 0), pady=(2 * self._pad, 0))
        self._enable_output_cbox.grid(padx=(self._pad, self._pad), pady=(0, 0))
        self._show_graph_entry.grid(padx=(self._pad, self._pad), pady=(0, 0))

    def _create_output_view(self):
        """
        TODO
        """
        pass

    def _create_settings_view(self):
        """
        Creates the view to configure general settings
        """
        def __update_fps(fps: str):
            self._fps = float(fps)

        self._fps_settings_txt = ctk.CTkLabel(self._settings_view, text="FPS")
        self._fps_settings_menu = ctk.CTkOptionMenu(
            self._settings_view,
            values=["0.1", "0.2", "1", "5", "10", "25"],
            command=__update_fps
        )
        self._ocr_settings_txt = ctk.CTkLabel(self._settings_view, text="OCR method")
        self._ocr_settings_menu = ctk.CTkOptionMenu(
            self._settings_view, values=["Tesseract"]
        )
        self._appearance_txt = ctk.CTkLabel(self._settings_view, text="Appearance")
        self._appearance_menu = ctk.CTkOptionMenu(
            self._settings_view,
            values=["System", "Light", "Dark"],
            command=lambda mode: ctk.set_appearance_mode(mode),
        )

        self._fps_settings_txt.grid(row=0, column=0)
        self._fps_settings_menu.grid(row=0, column=1)
        self._ocr_settings_txt.grid(row=1, column=0)
        self._ocr_settings_menu.grid(row=1, column=1)
        self._appearance_txt.grid(row=2, column=0)
        self._appearance_menu.grid(row=2, column=1)

        self._fps_settings_txt.grid(padx=(self._pad, 0), pady=(self._pad, 0))
        self._fps_settings_menu.grid(padx=(self._pad, 0), pady=(self._pad, 0))
        self._ocr_settings_txt.grid(padx=(self._pad, self._pad), pady=(self._pad, 0))
        self._ocr_settings_menu.grid(padx=(self._pad, 0), pady=(self._pad, 0))
        self._appearance_txt.grid(padx=(self._pad, 0), pady=(self._pad, 0))
        self._appearance_menu.grid(padx=(self._pad, 0), pady=(self._pad, 0))

    def _create_logs_view(self):
        """
        Creates the view to display all the app logs
        """
        self._logs_tbox = ctk.CTkTextbox(self._logs_view, state="disabled")
        self._logs_tbox.grid(row=0, column=0, sticky="nesw")
        self._logs_view.grid_columnconfigure(0, weight=1)

    def _main_loop(self):
        """
        Periodically runs OCR and updates graphs and display
        """
        t0 = time()

        def __schedule_next_loop():
            next_wait_time = int(1000.0 / self._fps - (time() - t0) * 1000)
            next_wait_time = max(10, next_wait_time)  # minimum interface refresh time
            self.after(next_wait_time, self._main_loop)

        # Capture the screen
        # screen_img = ImageGrab.grab()
        # screen_img = np.asarray(screen_img)

        monitor = self._sct.monitors[1]
        try:
            screen_img = self._sct.grab(
                (
                    monitor["left"],
                    monitor["top"],
                    monitor["left"] + monitor["width"],
                    monitor["top"] + monitor["height"],
                )
            )
        except mss.exception.ScreenShotError:
            __schedule_next_loop()
            return

        screen_img = Image.frombytes(
            "RGB", screen_img.size, screen_img.bgra, "raw", "BGRX"
        )
        screen_img = np.array(screen_img)[:, :, :3]

        # Run OCR on all active captures and update displayed output
        output = self._captures.update(screen_img)
        self._data_recorder.record(output)

        # Update status text
        fps = self._data_recorder.get_average_fps()

        if self._data_recorder.get_is_recording():
            record_t = self._data_recorder.get_recording_time()
            self._status_txt.configure(
                text=f"{int(record_t // 60):02d}:{int(record_t % 60):02d} ({fps:.1f} fps)"
            )
        else:
            self._status_txt.configure(text=f"--:-- ({fps:.1f} fps)")

        # Schedule the next loop iteration
        __schedule_next_loop()

    def _create_output_frame(self):
        """
        Creates the frame to display all capture outputs
        """
        self._output_frame = ctk.CTkFrame(self, corner_radius=10)

    def _set_padding(self, frame: ctk.CTkBaseClass, padding: int):
        """
        Sets the padding for all children elements of the given frame
        """
        for child in frame.winfo_children():
            child.grid_configure(padx=padding, pady=padding)

    def _update_capture_options(self, selected: None | str = None):
        """
        Updates the capture frame for the currently selected capture

        Args:
            - selected: If provided, will switch the selected capture
        """
        print("Called with selected = ", selected)

        if selected is not None:
            new_capture = self._captures[selected]

            if new_capture is not None:
                self._selected_capture = new_capture

        self._captures_menu.configure(values=self._captures.get_names())
        self._captures_menu.set(self._selected_capture.name)

        def __update_entry_text(entry: ctk.CTkEntry, text):
            entry.delete(0, tk.END)
            entry.insert(0, text)

        self._selected_capture.toggle_edit(False)
        __update_entry_text(self._rect_xmin_entry, self._selected_capture.x_min)
        __update_entry_text(self._rect_xmax_entry, self._selected_capture.x_max)
        __update_entry_text(self._rect_ymin_entry, self._selected_capture.y_min)
        __update_entry_text(self._rect_ymax_entry, self._selected_capture.y_max)
        self._selected_capture.toggle_edit(True)

        self._pre_process_config_frame.update_elements(
            self._selected_capture.get_pre_process_config()
        )

        if self._selected_capture.is_enabled:
            self._enable_output_cbox.select()
        else:
            self._enable_output_cbox.deselect()


class PreProcessingConfigFrame(ctk.CTkFrame):
    """
    Tkinter frame for image pre-processing settings
    """

    def __init__(self, padding: int, *args, **kwargs):
        ctk.CTkFrame.__init__(self, *args, **kwargs)
        self._pad = padding
        self._config = BaseOcrEngine.PreProcessConfig()
        self._callback = None  # Called when an element is updated
        self._updating = False  # whether the frame is currently being updated (disables the callback)

        # Adding all widgets
        self._pre_process_frame = ctk.CTkFrame(self, border_width=2)
        self._pre_process_title = ctk.CTkLabel(
            self, text=" Pre-processing ", anchor="nw", height=0
        )
        self._upscale_ratio_label = ctk.CTkLabel(
            self._pre_process_frame, text="Upscaling ratio"
        )
        self._upscale_ratio_entry = Entry(
            self._pre_process_frame, width=50, command=self._input_cb
        )
        self._unsharp_kernel_label = ctk.CTkLabel(
            self._pre_process_frame, text="Unsharp kernel"
        )
        self._unsharp_kernel_entry = Entry(
            self._pre_process_frame, width=50, command=self._input_cb
        )
        self._unsharp_sigma_label = ctk.CTkLabel(self._pre_process_frame, text="Sigma")
        self._unsharp_sigma_entry = Entry(
            self._pre_process_frame, width=50, command=self._input_cb
        )
        self._unsharp_amount_label = ctk.CTkLabel(
            self._pre_process_frame, text="Amount"
        )
        self._unsharp_amount_entry = Entry(
            self._pre_process_frame, width=50, command=self._input_cb
        )
        self._invert_img_entry = ctk.CTkCheckBox(
            self._pre_process_frame, text="Invert image", command=self._input_cb
        )

        # Placing elements in the frame
        self._pre_process_frame.grid(row=0, column=0, columnspan=4, sticky="we")
        self._pre_process_title.place(x=10, y=0)
        self._upscale_ratio_label.grid(row=0, column=0)
        self._upscale_ratio_entry.grid(row=0, column=1)
        self._unsharp_kernel_label.grid(row=1, column=0)
        self._unsharp_kernel_entry.grid(row=1, column=1)
        self._unsharp_sigma_label.grid(row=1, column=2)
        self._unsharp_sigma_entry.grid(row=1, column=3)
        self._unsharp_amount_label.grid(row=1, column=4)
        self._unsharp_amount_entry.grid(row=1, column=5)
        self._invert_img_entry.grid(row=2, column=0)

        # Settings margin and padding
        self._pre_process_frame.grid(padx=(0, 0), pady=(self._pad, 0))
        self._upscale_ratio_label.grid(padx=(self._pad, 0), pady=(self._pad, self._pad))
        self._upscale_ratio_entry.grid(padx=(self._pad, self._pad), pady=(0, 0))
        self._unsharp_kernel_label.grid(padx=(self._pad, 0), pady=(0, self._pad))
        self._unsharp_kernel_entry.grid(padx=(self._pad, self._pad), pady=(0, 0))
        self._unsharp_sigma_label.grid(padx=(self._pad, 0), pady=(0, 0))
        self._unsharp_sigma_entry.grid(padx=(self._pad, self._pad), pady=(0, 0))
        self._unsharp_amount_label.grid(padx=(self._pad, 0), pady=(0, 0))
        self._unsharp_amount_entry.grid(padx=(self._pad, self._pad), pady=(0, 0))
        self._invert_img_entry.grid(padx=(2* self._pad, self._pad), pady=(0, self._pad))

        # Map between widgets and config parameters, and their type
        self._fields: list[tuple[Type, Entry | ctk.CTkCheckBox, str]] = [
            (float, self._upscale_ratio_entry, "upscale_ratio"),
            (int, self._unsharp_kernel_entry, "unsharp_kernel_size"),
            (float, self._unsharp_sigma_entry, "unsharp_sigma"),
            (float, self._unsharp_amount_entry, "unsharp_amount"),
            (bool, self._invert_img_entry, "invert_img"),
        ]

    def attach_update_cb(
        self, callback: Callable[[BaseOcrEngine.PreProcessConfig], None]
    ):
        """
        Configures a callback function that will be called each time elements
        in the frame are updated

        The callback should have the following signature:
            `callback(pre_processing_config: BaseOcrEngine.PreProcessConfig) -> None`
        """
        self._callback = callback

    def update_elements(self, config: BaseOcrEngine.PreProcessConfig):
        """
        Updates the elements of the frame
        """
        self._updating = True
        self._config = deepcopy(config)

        for _, entry, key in self._fields:
            if type(entry) == Entry:
                entry.set_value(getattr(config, key))
            elif type(entry) == ctk.CTkCheckBox:
                if getattr(config, key):
                    entry.select()
                else:
                    entry.deselect()

        self._updating = False


    def _input_cb(self, *_):
        """
        Called when an input field has been updated
        """
        assert self._callback is not None

        if not self._updating:
            for t, entry, key in self._fields:
                try:
                    if type(entry) == Entry:
                        value = t(entry.get_value())
                    elif type(entry) == ctk.CTkCheckBox:
                        value = bool(entry.get())
                    else:
                        raise ValueError

                except ValueError:
                    continue

                setattr(self._config, key, value)

        self._callback(self._config)


if __name__ == "__main__":
    app = App()
    app.mainloop()
