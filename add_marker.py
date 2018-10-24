import argparse
import os.path
import PyPDF2

scriptdir = os.path.dirname(os.path.abspath(__file__))
marker_filename = scriptdir + "/marker.pdf"

parser = argparse.ArgumentParser(description="Adds alignment markers to a PDF")
parser.add_argument("input", type=str, help="path to the input PDF")
parser.add_argument("output", type=str, help="path to output the marked PDF")
parser.add_argument(
    "--marker-size",
    type=float,
    default=0.35,
    help="size of the markers (in inches). Default 0.35in.",
)
parser.add_argument(
    "--marker-margin",
    type=float,
    default=0.5,
    help="margin of the markers (in inches) Default 0.5in.",
)
args = parser.parse_args()


output = PyPDF2.PdfFileWriter()
base_pdf = PyPDF2.PdfFileReader(open(args.input, "rb"))
marker = PyPDF2.PdfFileReader(open(marker_filename, "rb")).getPage(0)
marker.scaleBy(args.marker_size)
marker_w = float(marker.mediaBox.upperRight[0] - marker.mediaBox.lowerLeft[0])
marker_h = float(marker.mediaBox.upperRight[1] - marker.mediaBox.lowerLeft[1])
margin_x = args.marker_margin * 72
margin_y = args.marker_margin * 72

for i in range(base_pdf.getNumPages()):
    page = base_pdf.getPage(i)
    mediaBox = page.mediaBox
    x0, y0 = mediaBox.lowerLeft
    x1, y1 = mediaBox.upperRight

    page.mergeTranslatedPage(marker, (x0 + margin_x), (y0 + margin_y))
    page.mergeTranslatedPage(marker, (x0 + margin_x), (y1 - margin_y - marker_h))
    page.mergeTranslatedPage(
        marker, (x1 - margin_x - marker_w), (y1 - margin_y - marker_h)
    )
    output.addPage(page)

with open(args.output, "wb") as f:
    output.write(f)
