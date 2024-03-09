"""
TODO
"""

from src.capture import Captures
from src.gui_elements import Entry
import customtkinter as ctk
import tkinter as tk
from PIL import ImageGrab
import numpy as np
from time import time
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

        # Create captures
        self._captures = Captures()
        self._selected_capture = self._captures.get_first()  # its config is displayed

        self._selected_capture.set_area(0, 0, 420, 420)

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

        # Configure the grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)

        # Set default values and statuses
        self._stop_btn.configure(state="disabled")  # TODO: change state dynamically
        self._status_txt.configure(text="10:03 (12 FPS)")
        self._status_txt.configure(
            fg_color="green"
        )  # TODO: change the colour depending on the status
        self._fps_settings_menu.set("1")
        self._ocr_settings_menu.set("Tesseract")

        self._update_capture_options()

        # Configure callbacks
        from src.graphics import TkImage

        self._test_img = TkImage(self._output_frame)
        self._test_img.get_tk_canvas().grid(row=0, column=0)

        self._fps = 10.0
        self.after(int(1000.0 / self._fps), self._main_loop)

    def _create_header_frame(self):
        """
        Creating the heading frame with main controls
        """
        self._header_frame = ctk.CTkFrame(self, corner_radius=10)

        self._start_btn = ctk.CTkButton(
            master=self._header_frame,
            height=40,
            text="Start",
        )
        self._stop_btn = ctk.CTkButton(
            master=self._header_frame,
            height=40,
            text="Stop",
        )
        # self._stop_btn.configure(state="disabled")  # TODO: add logic to disable btn
        # self._stop_btn.configure(fg_color="gray")
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

        # Callbacks for operations
        def add_capture():
            self._selected_capture = self._captures.add_capture()
            self._update_capture_options()

        def rename_capture():
            dialog = ctk.CTkInputDialog(text="New capture name:", title="Renaming")
            name = dialog.get_input()

            if name is not None and self._captures.rename(self._selected_capture, name):
                self._update_capture_options()
            else:
                print("Invalid name!")

        def remove_capture():
            self._captures.remove_capture(self._selected_capture.name)
            self._selected_capture = self._captures.get_first()
            self._update_capture_options()

        def update_rect_area(*_):
            try:
                self._selected_capture.set_area(
                    int(self._rect_xmin_entry.get_value()),
                    int(self._rect_ymin_entry.get_value()),
                    int(self._rect_xmax_entry.get_value()),
                    int(self._rect_ymax_entry.get_value()),
                )
            except ValueError:
                return

        # Menu and add/delete buttons row
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
            command=add_capture,
        )
        self._capture_rename_btn = ctk.CTkButton(
            self._captures_view, text="Rename", width=80, command=rename_capture
        )
        self._capture_remove_btn = ctk.CTkButton(
            self._captures_view, text="Remove", width=80, command=remove_capture
        )

        # Rectangle settings row
        self._rect_txt = ctk.CTkLabel(self._captures_view, text="Area")
        self._rect_select_frame = ctk.CTkFrame(self._captures_view)
        self._rect_select_btn = ctk.CTkButton(
            self._captures_view, text="Select", width=80
        )

        self._rect_xmin_entry = Entry(
            master=self._rect_select_frame, width=50, command=update_rect_area
        )
        self._rect_ymin_entry = Entry(
            master=self._rect_select_frame, width=50, command=update_rect_area
        )
        self._rect_xmax_entry = Entry(
            master=self._rect_select_frame, width=50, command=update_rect_area
        )
        self._rect_ymax_entry = Entry(
            master=self._rect_select_frame, width=50, command=update_rect_area
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

        # Unsharp mask row
        self._unsharp_frame = ctk.CTkFrame(self._captures_view)
        self._unsharp_kernel_label = ctk.CTkLabel(
            self._unsharp_frame, text="Unsharp kernel"
        )
        self._unsharp_kernel_entry = ctk.CTkEntry(self._unsharp_frame, width=50)
        self._unsharp_sigma_label = ctk.CTkLabel(self._unsharp_frame, text="Sigma")
        self._unsharp_sigma_entry = ctk.CTkEntry(self._unsharp_frame, width=50)
        self._unsharp_amount_label = ctk.CTkLabel(self._unsharp_frame, text="Amount")
        self._unsharp_amount_entry = ctk.CTkEntry(self._unsharp_frame, width=50)

        self._unsharp_frame.grid(row=3, column=0, columnspan=4, sticky="we")
        self._unsharp_kernel_label.grid(row=0, column=0)
        self._unsharp_kernel_entry.grid(row=0, column=1)
        self._unsharp_sigma_label.grid(row=0, column=2)
        self._unsharp_sigma_entry.grid(row=0, column=3)
        self._unsharp_amount_label.grid(row=0, column=4)
        self._unsharp_amount_entry.grid(row=0, column=5)

        self._unsharp_frame.grid(padx=(0, 0), pady=(self._pad, 0))
        self._unsharp_kernel_label.grid(padx=(self._pad, 0), pady=(0, 0))
        self._unsharp_kernel_entry.grid(padx=(self._pad, self._pad), pady=(0, 0))
        self._unsharp_sigma_label.grid(padx=(self._pad, 0), pady=(0, 0))
        self._unsharp_sigma_entry.grid(padx=(self._pad, self._pad), pady=(0, 0))
        self._unsharp_amount_label.grid(padx=(self._pad, 0), pady=(0, 0))
        self._unsharp_amount_entry.grid(padx=(self._pad, self._pad), pady=(0, 0))

        # Show options row
        self._show_capture_frame = ctk.CTkFrame(self._captures_view)
        self._show_output_entry = ctk.CTkCheckBox(
            self._show_capture_frame, text="Show output"
        )
        self._show_graph_entry = ctk.CTkCheckBox(
            self._show_capture_frame, text="Show graph"
        )

        self._show_capture_frame.grid(row=4, column=0, columnspan=4)
        self._show_output_entry.grid(row=0, column=0)
        self._show_graph_entry.grid(row=0, column=1)

        self._show_capture_frame.grid(padx=(0, 0), pady=(2 * self._pad, 0))
        self._show_output_entry.grid(padx=(self._pad, self._pad), pady=(0, 0))
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
        self._fps_settings_txt = ctk.CTkLabel(self._settings_view, text="FPS")
        self._fps_settings_menu = ctk.CTkOptionMenu(
            self._settings_view, values=["1/10", "1/5", "1", "5", "10", "25"]
        )
        self._ocr_settings_txt = ctk.CTkLabel(self._settings_view, text="OCR method")
        self._ocr_settings_menu = ctk.CTkOptionMenu(
            self._settings_view, values=["Tesseract"]
        )

        self._fps_settings_txt.grid(row=0, column=0)
        self._fps_settings_menu.grid(row=0, column=1)
        self._ocr_settings_txt.grid(row=1, column=0)
        self._ocr_settings_menu.grid(row=1, column=1)

        self._fps_settings_txt.grid(padx=(self._pad, 0), pady=(self._pad, 0))
        self._fps_settings_menu.grid(padx=(self._pad, 0), pady=(self._pad, 0))
        self._ocr_settings_txt.grid(padx=(self._pad, self._pad), pady=(self._pad, 0))
        self._ocr_settings_menu.grid(padx=(self._pad, self._pad), pady=(self._pad, 0))

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

        # Capture the screen
        screen_img = ImageGrab.grab()
        screen_img = np.asarray(screen_img)

        # TESTSETESTSETEST
        capture_img = self._selected_capture.slice_area(screen_img)
        self._test_img.update(capture_img)

        # Run OCR on all active captures
        # TODO

        # Update displayed captures
        # TODO

        # Schedule the next loop iteration
        next_wait_time = int(1000.0 / self._fps - (time() - t0) * 1000)
        next_wait_time = max(10, next_wait_time)  # minimum interface refresh time
        self.after(next_wait_time, self._main_loop)

    def _create_output_frame(self):
        """
        Creates the frame to display all capture outputs
        """
        self._output_frame = ctk.CTkFrame(self, corner_radius=10)

        # self._test_label = ctk.CTkLabel(self._output_frame, text="BLETR")
        # self._test_label.grid(row=0, column=0)

        # from src.graphics import create_the_button
        # self._the_button = create_the_button(self._output_frame)

        # self._the_button.grid(row=0, column=0)
        # self._the_button.pack(side=tk.BOTTOM)

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

        def update_entry_text(entry: ctk.CTkEntry, text):
            entry.delete(0, tk.END)
            entry.insert(0, text)

        self._selected_capture.toggle_edit(False)
        update_entry_text(self._rect_xmin_entry, self._selected_capture.x_min)
        update_entry_text(self._rect_xmax_entry, self._selected_capture.x_max)
        update_entry_text(self._rect_ymin_entry, self._selected_capture.y_min)
        update_entry_text(self._rect_ymax_entry, self._selected_capture.y_max)
        self._selected_capture.toggle_edit(True)


if __name__ == "__main__":
    app = App()
    app.mainloop()
