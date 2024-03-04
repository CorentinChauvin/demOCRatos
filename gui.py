"""
TODO
"""

import tkinter
import tkinter.messagebox
import customtkinter as ctk
import tkinter as tk
import sys


ctk.set_appearance_mode(
    "System"
)  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme(
    "blue"
)  # Themes: "blue" (standard), "green", "dark-blue


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

        # Create the frames
        self._pad = 10
        self._create_header_frame()
        self._create_options_frame()

        self._header_frame.grid(row=0, column=0, sticky="nsew")
        self._options_frame.grid(row=1, column=0, sticky="nsew")

        self._header_frame.grid(padx=(self._pad, self._pad), pady=(self._pad, 0))
        self._options_frame.grid(padx=(self._pad, self._pad), pady=(0, self._pad))

        # Configure the grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)

        # Set default values
        self._status_txt.configure(text="10:03 (12 FPS)")
        self._fps_settings_menu.set("1")
        self._ocr_settings_menu.set("Tesseract")

    def _create_header_frame(self):
        """
        Creating the heading frame with main controls
        """
        self._header_frame = ctk.CTkFrame(self, corner_radius=10)

        self._start_btn = ctk.CTkButton(
            master=self._header_frame,
            fg_color="green",
            border_width=2,
            text_color="black",
            hover_color="gray",
            text="Start",
        )
        self._stop_btn = ctk.CTkButton(
            master=self._header_frame,
            fg_color="orange",
            border_width=2,
            text_color="black",
            hover_color="gray",
            text="Stop",
        )
        # self._stop_btn.configure(state="disabled")  # TODO: add logic to disable btn
        # self._stop_btn.configure(fg_color="gray")
        self._status_txt = ctk.CTkLabel(self._header_frame)

        # Grid placement of all children
        self._start_btn.grid(row=0, column=0, sticky="nsew")
        self._stop_btn.grid(row=0, column=1, sticky="nsew")
        self._status_txt.grid(row=0, column=2, sticky="nsew")

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
        self._captures_menu = ctk.CTkOptionMenu(
            self._captures_view,
            values=["New capture with long text"],
            dynamic_resizing=False,
            width=290,
        )
        self._capture_add_btn = ctk.CTkButton(self._captures_view, text="Add", width=80)
        self._capture_remove_btn = ctk.CTkButton(
            self._captures_view, text="Remove", width=80
        )

        # Rectangle settings row
        self._rect_txt = ctk.CTkLabel(self._captures_view, text="Area")
        self._rect_select_frame = ctk.CTkFrame(self._captures_view)
        self._rect_select_btn = ctk.CTkButton(
            self._captures_view, text="Select", width=80
        )

        self._rect_xmin_tbox = ctk.CTkEntry(self._rect_select_frame, width=50)
        self._rect_xmax_tbox = ctk.CTkEntry(self._rect_select_frame, width=50)
        self._rect_ymin_tbox = ctk.CTkEntry(self._rect_select_frame, width=50)
        self._rect_ymax_tbox = ctk.CTkEntry(self._rect_select_frame, width=50)

        self._captures_menu.grid(row=0, column=0, columnspan=2)
        self._capture_add_btn.grid(row=0, column=2)
        self._capture_remove_btn.grid(row=0, column=3)
        self._rect_txt.grid(row=1, column=0)
        self._rect_select_frame.grid(row=1, column=1)
        self._rect_select_btn.grid(row=1, column=2)

        self._rect_xmin_tbox.grid(row=1, column=0)
        self._rect_xmax_tbox.grid(row=1, column=1)
        self._rect_ymin_tbox.grid(row=1, column=2)
        self._rect_ymax_tbox.grid(row=1, column=3)

        self._captures_menu.grid(padx=(self._pad, 0), pady=(0, 0))
        self._capture_add_btn.grid(padx=(self._pad, 0), pady=(0, 0))
        self._capture_remove_btn.grid(padx=(self._pad, self._pad), pady=(0, 0))
        self._rect_txt.grid(padx=(self._pad, 0), pady=(self._pad, 0))
        self._rect_select_frame.grid(padx=(self._pad, 0), pady=(self._pad, 0))
        self._rect_select_btn.grid(padx=(self._pad, 0), pady=(self._pad, 0))

        self._rect_xmin_tbox.grid(padx=(self._pad, 0), pady=(0, 0))
        self._rect_xmax_tbox.grid(padx=(self._pad, 0), pady=(0, 0))
        self._rect_ymin_tbox.grid(padx=(self._pad, 0), pady=(0, 0))
        self._rect_ymax_tbox.grid(padx=(self._pad, 0), pady=(0, 0))

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
        self._unsharp_kernel_label = ctk.CTkLabel(self._unsharp_frame, text="Unsharp kernel")
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
        self._show_output_entry = ctk.CTkCheckBox(self._show_capture_frame, text="Show output")
        self._show_graph_entry = ctk.CTkCheckBox(self._show_capture_frame, text="Show graph")

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

    def _set_padding(self, frame: ctk.CTkBaseClass, padding: int):
        """
        Sets the padding for all children elements of the given frame
        """
        for child in frame.winfo_children():
            child.grid_configure(padx=padding, pady=padding)


if __name__ == "__main__":
    app = App()
    app.mainloop()
