"""
   Copyright 2022 Thomas Reidemeister

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""


import sys
from ..consts import VERSION
from PIL import Image
from .printer import find_printers, BrotherPt
from .cmd import MediaWidthToTapeMargin, MINIMUM_TAPE_POINTS
from .raster import make_fit, select_raster_channel, raster_image

def show_status(serial):
    printers = find_printers(serial)
    if len(printers) == 0:
        print("No supported printers found, make sure the device is switched on", file=sys.stderr)
        return 1
    found_printer = BrotherPt(printers[0].serial_number)
    print("%s %s (%s):" % (printers[0].manufacturer, printers[0].product, printers[0].serial_number))
    print(" + Media width: %dmm" % found_printer.media_width)
    print(" + Media type : %s" % found_printer.media_type.name)
    print(" + Tape color : %s" % found_printer.tape_color.name)
    print(" + Text color : %s" % found_printer.text_color.name)
    print(" + Recommended image height : %dpx" % MediaWidthToTapeMargin.to_print_width(found_printer.media_width))
    print()
    return 0

def do_print( file, printer = None, margin = 0, rotate = '0', dry_run = False):
   return print_all([file], printer, margin, rotate, dry_run)

def print_all(files, printer = None, margin = 0, rotate = '0', dry_run = False):
    printers = find_printers(printer)
    if len(printers) == 0:
        print("No supported printers found, make sure the device is switched on", file=sys.stderr)
        return 1

    found_printer = BrotherPt(printers[0].serial_number)

    rasters = []
    for file in files:
        image = Image.open(file)
        required_height = MediaWidthToTapeMargin.to_print_width(found_printer.media_width)

        # Apply rotation as specified
        if rotate == 'auto':
            adjusted_image = make_fit(image, found_printer.media_width)
            if adjusted_image is None:
                print('Could not auto-rotate image, at least one dimension needs to match the tape width (%i, %i) vs %i',
                    (image.width, image.height, required_height), file=sys.stderr)
                return 1
        elif rotate == '0':
            adjusted_image = image
        elif rotate == '90':
            adjusted_image = image.rotate(90, expand=True)
        elif rotate == '180':
            adjusted_image = image.rotate(180, expand=True)
        elif rotate == '270':
            adjusted_image = image.rotate(270, expand=True)
        else:
            print('Invalid rotation specified %s', file=sys.stderr)
            return 1
        if adjusted_image.height != required_height:
            print('Height of output image does not match tape-width (%i, %i) vs %i',
                (adjusted_image.width, adjusted_image.height, required_height), file=sys.stderr)
            return 1

        image = select_raster_channel(adjusted_image)

        # Margin check
        margin = margin
        if (image.width + margin) < MINIMUM_TAPE_POINTS:
            print("Image (%i) + cut margin (%i) is smaller than minimum tape width (%i) ...\n"
                "cutting length will be extended" % (image.width, margin, MINIMUM_TAPE_POINTS))
            margin = MINIMUM_TAPE_POINTS - image.width

        # Raster image
        data = raster_image(image, found_printer.media_width)
        rasters.append({'data': data, 'margin': margin})

    # Print images
    for i, raster in enumerate(rasters):
        print("Printing raster %i / %i..." % (i+1, len(rasters)))
        if not dry_run:
           found_printer.print_data(raster['data'], raster['margin'], i == len(rasters)-1)

    return 0


def list_printers(serial):
    printers = find_printers(serial)
    if len(printers) == 0:
        print("No supported printers found, make sure the device is switched on", file=sys.stderr)
        return 1
    print("Discovered printers ...")
    print("      Vendor\tModel\t\tSerial")
    for i, found_printer in enumerate(printers):
        print(" (%2i) %s\t%s\t%s" %
              (i+1, found_printer.manufacturer, found_printer.product, found_printer.serial_number))

    return 0
