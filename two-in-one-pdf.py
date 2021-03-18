import os
import argparse
import configparser
from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.pdf import PageObject
import fpdf
import progressbar

tmpFileName = ".tmp.pdf"

args_parser = argparse.ArgumentParser(description="Create PDF with two pages in one")
args_parser.add_argument("-i", "--input", dest="sourcefile", help="Input PDF")
args_parser.set_defaults(sourcefile=None)
args_parser.add_argument("-o", "--output", dest="outputfile", help="Output PDF name")
args_parser.set_defaults(outputfile=None)
args_parser.add_argument("-c", "--config", dest="configfile", help="Config ini file")
args_parser.set_defaults(configfile="default.ini")

args = args_parser.parse_args()


def get_configs():
    global args
    config = configparser.ConfigParser()

    config["GLOBAL"] = {
        "scale_page": 0.5,
        "margin_x": 120,
        "margin_y": 120,
        "margin_inter": 80,
        "border": True,
    }

    try:
        config.read(args.configfile)
    except Exception:
        pass

    # load config from config file, otherwise use defaults values
    scale_page = float(config["GLOBAL"].get("scale_page"))
    margin_x = float(config["GLOBAL"].get("margin_x"))
    margin_y = float(config["GLOBAL"].get("margin_y"))
    margin_inter = float(config["GLOBAL"].get("margin_inter"))
    border = float(config["GLOBAL"].getboolean("border"))

    global_options = {
        "scale_page": scale_page,
        "margin_x": margin_x,
        "margin_y": margin_y,
        "margin_inter": margin_inter,
        "border": border,
    }

    return global_options


global_options = get_configs()

# calc page sizes from page and margins
def calc_page_size(page_w, page_h):
    global global_options

    out_page_w = page_w + global_options["margin_x"] * 2
    out_page_h = (page_h + global_options["margin_y"]) * 2 + global_options[
        "margin_inter"
    ]

    return (out_page_w, out_page_h)

# create temporary file with borders
def create_tmp_file(page_width, page_height, has_second_page):
    global global_options
    global tmpFileName
    out_page_w, out_page_h = calc_page_size(page_width, page_height)

    # setup pdf
    fpdfTemp = fpdf.FPDF(unit="pt", format=(out_page_w, out_page_h))
    fpdfTemp.add_page()

    if global_options["border"]:
        # print first rectangle
        fpdfTemp.rect(
            global_options["margin_x"], global_options["margin_y"], page_width, page_height
        )

        # print second rectangle
        if has_second_page:
            fpdfTemp.rect(
                global_options["margin_x"],
                global_options["margin_y"] + page_height + global_options["margin_inter"],
                page_width,
                page_height,
            )
    
    # save file
    fpdfTemp.output(tmpFileName)
    fpdfTemp.close()


def main():
    global args
    global global_options

    fileinput = args.sourcefile
    fileoutput = args.outputfile
    
    # check if file exists
    if fileinput != None and os.path.exists(fileinput) and os.path.isfile(fileinput):
        # if no output name, set it by input
        if fileoutput == None:
            filename = os.path.splitext(fileinput)[0]
            fileoutput = filename + "_merged.pdf"
            
        # open given pdf
        opened_PDF = PdfFileReader(open(fileinput, "rb"))
        # setup writer
        writer = PdfFileWriter()

        # calc number of pages
        num_pages = opened_PDF.getNumPages()

        print("[INFO] Opened PDF,", num_pages, "pages read. Start merging")

        # setup progressbar
        pbar = progressbar.ProgressBar(max_value = num_pages)

        i = 0
        # for each page
        while i < num_pages:
            # open first page
            first_page = opened_PDF.getPage(i)
            pbar.update(i + 1)

            # open second page (if exists)
            has_second_page = False
            if i + 1 < num_pages:
                second_page = opened_PDF.getPage(i + 1)
                pbar.update(i + 2)
                has_second_page = True
            else:
                second_page = PageObject.createBlankPage(None, page_width, page_height)

            # calc page width (scaled)
            page_width = (
                float(first_page.mediaBox.getWidth()) * global_options["scale_page"]
            )
            page_height = (
                float(first_page.mediaBox.getHeight()) * global_options["scale_page"]
            )

            # calc page size with margins
            out_page_w, out_page_h = calc_page_size(page_width, page_height)

            # create temporary file with border box
            create_tmp_file(page_width, page_height, has_second_page)
            tmpPDF = PdfFileReader(open(tmpFileName, "rb"))

            # create blank page
            merged_page = PageObject.createBlankPage(
                None,
                out_page_w,
                out_page_h,
            )

            # add first page
            merged_page.mergeScaledTranslatedPage(
                first_page,
                global_options["scale_page"],
                global_options["margin_x"],
                page_height + global_options["margin_y"] + global_options["margin_inter"],
            )

            # add second page
            if has_second_page:
                merged_page.mergeScaledTranslatedPage(
                    second_page,
                    global_options["scale_page"],
                    global_options["margin_x"],
                    global_options["margin_y"],
                )
            
            # add borders
            merged_page.mergePage(tmpPDF.getPage(0))

            # add page to the file
            writer.addPage(merged_page)

            i += 2

        # save file
        print("\n[INFO] Saving file")
        with open(fileoutput, "wb") as f:
            writer.write(f)

        os.remove(tmpFileName)
    else:
        print("[ERROR] Input file does not exists")


if __name__ == "__main__":
    main()