import argparse
import asyncio
import logging
import threading
import tkinter
from tkinter import Tk, ttk, StringVar, BooleanVar
from tkinter.scrolledtext import ScrolledText

import downloader
import main
from captcha import TokiCaptcha
from downloader import TokiDownloader


logger = downloader.logger


class Gui:
    URL_PLACEHOLDER = "https://"

    def __init__(self):
        self.root = Tk()
        self.frame = ttk.Frame(self.root, padding=10)

        self.headless = BooleanVar(value=True)
        self.url = StringVar()

        self.headless_checkbutton = ttk.Checkbutton(self.frame, text="Headless", variable=self.headless)
        self.captcha_button = ttk.Button(self.frame, text="CAPTCHA", command=self.captcha)
        self.url_entry = ttk.Entry(self.frame, width=50, textvariable=self.url)
        self.download_button = ttk.Button(self.frame, text="Download", command=self.download)
        self.log_entry = ScrolledText(self.frame, width=50, state="disabled")

        self.root.title(f"TokiHunter {main.VERSION}")
        self.root.resizable(False, False)
        self.frame.grid()

        self.captcha_button.grid(row=0, column=0, padx=5, pady=5)
        self.headless_checkbutton.grid(row=0, column=1, padx=5, pady=5)
        self.url_entry.grid(row=0, column=2, padx=5, pady=5)
        self.download_button.grid(row=0, column=3, padx=5, pady=5)
        self.log_entry.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5, pady=5)

        self.root.update_idletasks()
        x = self.get_screen_center_x(self.root)
        y = self.get_screen_center_y(self.root)
        self.root.geometry(f"+{x}+{y}")

        self.add_url_placeholder()
        self.url_entry.bind("<FocusIn>", self.clear_url_placeholder)
        self.url_entry.bind("<FocusOut>", self.restore_url_placeholder)

        logger.addHandler(TextHandler(self.log_entry))

    def run(self):
        self.root.mainloop()

    def captcha(self):
        self.captcha_button.config(state="disabled")
        self.download_button.config(state="disabled")
        threading.Thread(target=self.captcha_internal, daemon=True).start()

    def download(self):
        self.captcha_button.config(state="disabled")
        self.download_button.config(state="disabled")
        threading.Thread(target=self.download_internal, daemon=True).start()

    def captcha_internal(self):
        args = argparse.Namespace(
            captcha=True
        )

        asyncio.run(TokiCaptcha(args).run())
        self.captcha_button.config(state="normal")
        self.download_button.config(state="normal")

    def download_internal(self):
        args = argparse.Namespace(
            captcha=False,
            search=False,
            headless=self.headless.get(),
            url=self.url.get(),
        )

        asyncio.run(TokiDownloader(args).run())
        self.captcha_button.config(state="normal")
        self.download_button.config(state="normal")

    def get_screen_center_x(self, tk):
        screen_width = tk.winfo_screenwidth()
        return (screen_width // 2) - (tk.winfo_width() // 2)

    def get_screen_center_y(self, tk):
        screen_height = tk.winfo_screenheight()
        return (screen_height // 2) - (tk.winfo_height() // 2)

    def add_url_placeholder(self):
        self.url_entry.insert(0, Gui.URL_PLACEHOLDER)
        self.url_entry.config(foreground="grey")

    def clear_url_placeholder(self, event):
        if self.url.get() == Gui.URL_PLACEHOLDER:
            self.url_entry.delete(0, tkinter.END)
            self.url_entry.config(foreground="black")

    def restore_url_placeholder(self, event):
        if not self.url.get():
            self.add_url_placeholder()


class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        message = self.format(record)
        self.text_widget.after(0, self.append, message)

    def append(self, message):
        self.text_widget.config(state="normal")
        self.text_widget.insert(tkinter.END, message + "\n")
        self.text_widget.config(state="disabled")
        self.text_widget.see(tkinter.END)


if __name__ == "__main__":
    Gui().run()