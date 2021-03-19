import argparse
import configparser
from two_in_one_pdf import TwoInOnePDF

args_parser = argparse.ArgumentParser(
    description="Create PDF with two pages in one")
args_parser.add_argument("-i", "--input", dest="sourcefile", help="Input PDF")
args_parser.set_defaults(sourcefile=None)
args_parser.add_argument(
    "-o", "--output", dest="outputfile", help="Output PDF name")
args_parser.set_defaults(outputfile=None)
args_parser.add_argument(
    "-c", "--config", dest="configfile", help="Config ini file")
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


def main():
    global args
    global global_options

    fileinput = args.sourcefile
    fileoutput = args.outputfile

    try:
        two_in_one_pdf = TwoInOnePDF(
            options=global_options, fileinput=fileinput, fileoutput=fileoutput)
        two_in_one_pdf.merge_pages()
    except FileNotFoundError:
        print("[ERROR] Input file does not exists")


if __name__ == "__main__":
    main()
