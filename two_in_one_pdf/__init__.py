import os
from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.pdf import PageObject
import fpdf
import progressbar


class TwoInOnePDF():
    _scale_page = 0.5
    _margin_x = 120
    _margin_y = 120
    _margin_inter = 80
    _rotation = 0
    _border = True

    _fileinput = None
    _fileoutput = None

    _tmp_filename = ".tmp.pdf"

    _progress_hook = None
    _pbar = None

    def __init__(self, options, fileinput, fileoutput=None, progress_hook=None):
        try:
            self._scale_page = options["scale_page"]
            self._margin_x = options["margin_x"]
            self._margin_y = options["margin_y"]
            self._margin_inter = options["margin_inter"]
            self._rotation = options["rotation"]
            self._border = int(options["border"])
        except Exception:
            pass

        if self._rotation not in [0, 90, 180, 270]:
            raise ValueError("Invalid rotation value")

        self._fileinput = fileinput
        self._fileoutput = fileoutput

        if progress_hook != None:
            self._progress_hook = progress_hook
        else:
            self._progress_hook = self._default_progress_hook

        # check if file exists
        if fileinput != None and os.path.exists(fileinput) and os.path.isfile(fileinput):
            # if no output name, set it by input
            if fileoutput == None:
                filename = os.path.splitext(fileinput)[0]
                self._fileoutput = filename + "_merged.pdf"
        else:
            raise FileNotFoundError

    # calc page sizes from page and margins
    def _calc_page_size(self, page_w, page_h):
        out_page_w = page_w + self._margin_x * 2
        out_page_h = (
            page_h + self._margin_y) * 2 + self._margin_inter

        return (out_page_w, out_page_h)

    # create temporary file with borders
    def _create_tmp_file(self, page_width, page_height, has_second_page):
        out_page_w, out_page_h = self._calc_page_size(page_width, page_height)

        # setup pdf
        fpdf_tmp = fpdf.FPDF(unit="pt", format=(out_page_w, out_page_h))
        fpdf_tmp.add_page()

        if self._border:
            # print first rectangle
            fpdf_tmp.rect(
                self._margin_x, self._margin_y, page_width, page_height
            )

            # print second rectangle
            if has_second_page:
                fpdf_tmp.rect(
                    self._margin_x,
                    self._margin_y + page_height +
                    self._margin_inter,
                    page_width,
                    page_height,
                )

        # save file
        fpdf_tmp.output(self._tmp_filename)
        fpdf_tmp.close()

    def _default_progress_hook(self, status):
        if status["event"] == "started":
            if self._pbar == None:
                self._pbar = progressbar.ProgressBar(
                    max_value=status["num_pages"])

            print("[INFO] " + status["message"] + "\n")
        elif status["event"] == "update":
            self._pbar.update(status["merged_pages"])
        elif status["event"] == "saving":
            self._pbar.finish()
            self._pbar = None
            print("[INFO] " + status["message"])
        elif status["event"] == "finished":
            print("\n[INFO] " + status["message"])

    def merge_pages(self):
        # open given pdf
        opened_PDF = PdfFileReader(open(self._fileinput, "rb"))
        # setup writer
        writer = PdfFileWriter()

        # calc number of pages
        num_pages = opened_PDF.getNumPages()

        # send notification
        self._progress_hook({"event": "started", "num_pages": num_pages,
                             "message": "Opened PDF, " + str(num_pages) + " pages read. Start merging"})

        i = 0
        # for each page
        while i < num_pages:
            # open first page
            first_page = opened_PDF.getPage(i)
            # send notification
            self._progress_hook(
                {"event": "update", "merged_pages": i + 1, "num_pages": num_pages})

            # open second page (if exists)
            has_second_page = False
            if i + 1 < num_pages:
                second_page = opened_PDF.getPage(i + 1)
                has_second_page = True

                # send notification
                self._progress_hook(
                    {"event": "update", "merged_pages": i + 2, "num_pages": num_pages})
            else:
                second_page = PageObject.createBlankPage(
                    None, page_width, page_height)

            # calc page width (scaled)
            page_width = (
                float(first_page.mediaBox.getWidth()) *
                self._scale_page
            )
            page_height = (
                float(first_page.mediaBox.getHeight()) *
                self._scale_page
            )

            # if rotate switch height and width
            if self._rotation in [90, 270]:
                page_height, page_width = page_width, page_height

            # set up rotation correction
            rotation_correction = {0: (0, 0), 90: (1, 0),
                                   270: (0, 1), 180: (1, 1)}[self._rotation]

            # calc page size with margins
            out_page_w, out_page_h = self._calc_page_size(
                page_width, page_height)

            # create temporary file with border box
            self._create_tmp_file(page_width, page_height, has_second_page)
            open_tmp_pdf = open(self._tmp_filename, "rb")
            tmpPDF = PdfFileReader(open_tmp_pdf)

            # create blank page
            merged_page = PageObject.createBlankPage(
                None,
                out_page_w,
                out_page_h,
            )

            # add first page
            merged_page.mergeRotatedScaledTranslatedPage(
                first_page,
                self._rotation,
                self._scale_page,
                self._margin_x + page_width * rotation_correction[0],
                page_height * (1 + rotation_correction[1]) +
                self._margin_y + self._margin_inter,
            )

            # add second page
            if has_second_page:
                merged_page.mergeRotatedScaledTranslatedPage(
                    second_page,
                    self._rotation,
                    self._scale_page,
                    self._margin_x + page_width * rotation_correction[0],
                    self._margin_y + page_height * rotation_correction[1],
                )

            # add borders
            merged_page.mergePage(tmpPDF.getPage(0))

            # add page to the file
            writer.addPage(merged_page)

            # close tmp file
            try:
                open_tmp_pdf.close()
            except Exception:
                pass

            i += 2

        # save file
        # send notification
        self._progress_hook(
            {"event": "saving", "message": "Saving file"})
        with open(self._fileoutput, "wb") as f:
            writer.write(f)

        try:
            os.remove(self._tmp_filename)
        except Exception:
            pass

        # send notification
        self._progress_hook(
            {"event": "finished", "message": "File saved. Finished"})
