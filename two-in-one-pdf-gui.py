import os
import configparser
from multiprocessing import Process
import tkinter as tk
from tkinter.constants import BOTTOM, HORIZONTAL, LEFT, RIGHT, TOP, X
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import ttk, messagebox
from two_in_one_pdf import TwoInOnePDF


class TwoInOnePDFApp(tk.Frame):
    _global_options = {"scale_page": 0.5,
                       "margin_x": 120,
                       "margin_y": 120,
                       "margin_inter": 80,
                       "rotation": 0,
                       "border": True,
                       }

    def __init__(self, root=None, options=None):
        super().__init__(root)
        self._global_options.update(options)
        self.root = root

        self.root.title('TwoInOnePDF')
        self.root.style = ttk.Style(self)

        # Gets the requested values of the height and widht
        windowWidth = root.winfo_reqwidth()
        windowHeight = root.winfo_reqheight()

        # Gets both half the screen width/height and window width/height
        positionRight = int(root.winfo_screenwidth()/2 - windowWidth)
        positionDown = int(root.winfo_screenheight()/2 - windowHeight)

        # Positions the window in the center of the page
        root.geometry("+{}+{}".format(positionRight, positionDown))

        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self._create_fileinput()
        self._create_fileoutput()
        self._create_options()
        self._create_status_progress()
        self._create_merge_btn()

    def _create_fileinput(self):
        select_filein_frame = ttk.Frame(self.root)
        select_filein_frame.pack(
            side=TOP, padx=20, pady=10, fill=X)

        tk.Label(select_filein_frame,
                 text="PDF file to elaborate", font=('Helvetica', 9, 'bold')).pack(side=LEFT, padx=(0, 15))

        self.fileinput_var = tk.StringVar(
            self.root, "no file selected")
        selected_filename_in_label = ttk.Label(
            select_filein_frame, textvariable=self.fileinput_var)
        selected_filename_in_label.pack(side=LEFT, padx=(0, 20))

        select_filein_btn = ttk.Button(select_filein_frame, text="...",
                                       command=self._open_file)
        select_filein_btn.pack(side=RIGHT)

    def _create_fileoutput(self):
        select_fileout_frame = ttk.Frame(self.root)
        select_fileout_frame.pack(side=TOP, padx=20, pady=10, fill=X)

        tk.Label(select_fileout_frame,
                 text="Save merged PDF as", font=('Helvetica', 9, 'bold')).pack(side=LEFT, padx=(0, 10))

        self.fileoutput_var = tk.StringVar(
            self.root, "no file selected")
        selected_filename_out_label = ttk.Label(
            select_fileout_frame, textvariable=self.fileoutput_var)
        selected_filename_out_label.pack(side=LEFT, padx=(0, 20))

        select_fileout_btn = ttk.Button(select_fileout_frame, text="...",
                                        command=self._open_save_file)
        select_fileout_btn.pack(side=RIGHT)

    def _create_options(self):
        options_frame_title = ttk.Frame(self.root)
        options_frame_title.pack(side=TOP, padx=20, pady=(10, 5), fill=X)
        tk.Label(options_frame_title,
                 text="Options", font=('Helvetica', 11, 'bold')).pack(side=LEFT, padx=(0, 10))

        # ROW 1
        options_frame_1 = ttk.Frame(self.root)
        options_frame_1.pack(side=TOP, padx=20, pady=(10, 5), fill=X)

        # Scale
        tk.Label(options_frame_1,
                 text="Scale", font=('Helvetica', 9, 'bold')).pack(side=LEFT, padx=(0, 10))
        self.scale_var = tk.StringVar(
            self.root, str(self._global_options["scale_page"]))
        scale_entry = tk.Entry(options_frame_1, textvariable=self.scale_var)
        scale_entry.pack(side=LEFT)

        # Inter margin
        tk.Label(options_frame_1,
                 text="Inter margin", font=('Helvetica', 9, 'bold')).pack(side=LEFT, padx=(20, 10))
        self.margin_inter_var = tk.StringVar(
            self.root, str(self._global_options["margin_inter"]))
        margin_entry = tk.Entry(
            options_frame_1, textvariable=self.margin_inter_var)
        margin_entry.pack(side=LEFT)

        # ROW 2
        options_frame_2 = ttk.Frame(self.root)
        options_frame_2.pack(side=TOP, padx=20, pady=5, fill=X)

        # X margin
        tk.Label(options_frame_2,
                 text="X Margin", font=('Helvetica', 9, 'bold')).pack(side=LEFT, padx=(0, 10))
        self.margin_x_var = tk.StringVar(
            self.root, str(self._global_options["margin_x"]))
        margin_entry = tk.Entry(
            options_frame_2, textvariable=self.margin_x_var)
        margin_entry.pack(side=LEFT)

        # Y margin
        tk.Label(options_frame_2,
                 text="Y margin", font=('Helvetica', 9, 'bold')).pack(side=LEFT, padx=(20, 10))
        self.margin_y_var = tk.StringVar(
            self.root, str(self._global_options["margin_y"]))
        margin_entry = tk.Entry(
            options_frame_2, textvariable=self.margin_y_var)
        margin_entry.pack(side=LEFT)

        # ROW 3
        # Rotation
        options_frame_3 = ttk.Frame(self.root)
        options_frame_3.pack(side=TOP, padx=20, pady=(5, 10), fill=X)

        tk.Label(options_frame_3,
                 text="Rotation (0, 90, 180, 270)", font=('Helvetica', 9, 'bold')).pack(side=LEFT, padx=(0, 10))
        self.rotation_var = tk.IntVar(self.root, str(self._global_options["rotation"]))
        margin_entry = tk.Entry(
            options_frame_3, textvariable=self.rotation_var)
        margin_entry.pack(side=LEFT)

        # Border
        self.border_var = tk.IntVar(
            self.root, int(self._global_options["border"]))
        border_checkbox = ttk.Checkbutton(options_frame_3, text='Draw borders around pages', variable=self.border_var,
                                          onvalue=1, offvalue=0)
        border_checkbox.pack(side=LEFT, padx=(20, 0))

    def _create_merge_btn(self):
        merge_btn_frame = ttk.Frame(self.root)
        merge_btn_frame.pack(side=BOTTOM, padx=20, pady=10, fill=X)

        merge_btn = ttk.Button(merge_btn_frame, text="Merge",
                               command=self._merge_pages, padding=(20, 10))
        merge_btn.pack(side=TOP, pady=(10, 0), fill=X)

    def _create_status_progress(self):
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(side=BOTTOM, padx=20, pady=(0, 10), fill=X)

        tk.Label(progress_frame,
                 text="Status:", font=('Helvetica', 9, 'bold')).pack(side=LEFT, padx=(0, 10))

        self.status_label_var = tk.StringVar(
            self.root, "Click merge to start")
        status_label = ttk.Label(
            progress_frame, textvariable=self.status_label_var)
        status_label.pack(side=LEFT, padx=(0, 20))

        self.progress_bar = ttk.Progressbar(
            progress_frame, orient=HORIZONTAL, length=100, mode='determinate')
        self.progress_bar.pack(side=RIGHT, padx=(20, 0))

    def _open_file(self):
        filename = askopenfilename(
            defaultextension=".pdf", filetypes=[("PDF (Portable Document Format)", "*.pdf")])

        if os.path.exists(filename) and os.path.isfile(filename):
            self.fileinput_var.set(filename)

            filename = os.path.splitext(filename)[0]
            self.fileoutput_var.set(filename + "_merged.pdf")

    def _open_save_file(self):
        filename = asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF (Portable Document Format)", "*.pdf")])
        if filename != None and filename != "":
            self.fileoutput_var.set(filename)

    # Save current configuration
    def _save_configs(self):
        try:
            config = configparser.ConfigParser()
            self._global_options = {"scale_page": float(self.scale_var.get()),
                                    "margin_x": float(self.margin_x_var.get()),
                                    "margin_y": float(self.margin_y_var.get()),
                                    "margin_inter": float(self.margin_inter_var.get()),
                                    "rotation": int(self.rotation_var.get()),
                                    "border": True if self.border_var.get() == 1 else False,
                                    }
            config["GLOBAL"] = self._global_options

            with open('default.ini', 'w') as configfile:
                config.write(configfile)
        except ValueError as e:
            raise e

    def _custom_hook(self, status):
        if status["event"] == "started":
            self.status_label_var.set(status["message"])
        elif status["event"] == "update":
            self.progress_bar["value"] = int(
                status["merged_pages"] / status["num_pages"]) * 100
            self.root.update_idletasks()
        elif status["event"] == "saving":
            self.status_label_var.set(status["message"])
        elif status["event"] == "finished":
            self.progress_bar["value"] = 0
            self.status_label_var.set(status["message"])
            self.root.update_idletasks()
            messagebox.showinfo("Finished", status["message"])

    def _merge_pages(self):
        try:
            self._save_configs()
            two_in_one_pdf = TwoInOnePDF(
                options=self._global_options, fileinput=self.fileinput_var.get(), fileoutput=self.fileoutput_var.get(), progress_hook=self._custom_hook)

            two_in_one_pdf.merge_pages()
        except FileNotFoundError:
            messagebox.showerror("Error", "File not found")
        except ValueError as e:
            messagebox.showerror("Error", "Bad values for options")
        except Exception as e:
            messagebox.showerror("Error", e)


def get_configs():
    global args
    config = configparser.ConfigParser()

    config["GLOBAL"] = {
        "scale_page": 0.5,
        "margin_x": 120,
        "margin_y": 120,
        "margin_inter": 80,
        "rotation": 0,
        "border": True,
    }

    try:
        config.read("default.ini")
    except Exception:
        pass

    # load config from config file, otherwise use defaults values
    scale_page = float(config["GLOBAL"].get("scale_page"))
    margin_x = float(config["GLOBAL"].get("margin_x"))
    margin_y = float(config["GLOBAL"].get("margin_y"))
    margin_inter = float(config["GLOBAL"].get("margin_inter"))
    rotation = float(config["GLOBAL"].get("rotation"))
    border = float(config["GLOBAL"].getboolean("border"))

    global_options = {
        "scale_page": scale_page,
        "margin_x": margin_x,
        "margin_y": margin_y,
        "margin_inter": margin_inter,
        "rotation": rotation,
        "border": border,
    }

    return global_options


global_options = get_configs()

root = tk.Tk()
app = TwoInOnePDFApp(root=root, options=global_options)
app.mainloop()
