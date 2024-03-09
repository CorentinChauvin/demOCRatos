"""
Helper functions and classes for the TK app
"""

from __future__ import annotations
import customtkinter as ctk
import tkinter as tk
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

