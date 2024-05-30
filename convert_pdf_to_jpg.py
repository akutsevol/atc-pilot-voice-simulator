# online protractor:
# https://www.ginifab.com/feeds/angle_measurement/
#
# https://pypi.org/project/pypdfium2/
#

import pypdfium2 as pdfium
import time
import argparse

parser = argparse.ArgumentParser(
    prog="convert_pdf_to_jpg.py",
    description='Convert PDF to Image',
    epilog='')

parser.add_argument('-i', '--input', required=True, help='PDF file_name')
parser.add_argument('-o', '--output', required=True, default='image.jpg', help='Output image file name')

args = parser.parse_args()

pdf = pdfium.PdfDocument(args.input)
n_pages = len(pdf)
if n_pages > 1:
    for page_number in range(n_pages):
        page = pdf.get_page(page_number)
        pil_image = page.render(
            scale=300/36,
            rotation=0,
            crop=(0, 0, 0, 0)).to_pil()
        pil_image.save("{}-{}".format(page_number+1, args.output))
else:
    page = pdf.get_page(0)
    pil_image = page.render(
        scale=300 / 36,
        rotation=0,
        crop=(0, 0, 0, 0)).to_pil()
    pil_image.save("{}".format(args.output))
