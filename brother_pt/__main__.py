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
import argparse

from brother_pt import VERSION, list_printers, show_status, do_print

def cli():
    parser = argparse.ArgumentParser(prog='brother_pt',
                                     description='Command line interface for the brother_pt Python package.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Parameters for actual flashing
    parser.add_argument("-p", "--printer", action='store', default=None, help="Serial number of a connected printer")
    parser.add_argument("-d", "--debug", action='store_true', help="Debugging output")
    parser.add_argument("-v", "--version", action='store_true', help="Show the version and exit.")

    # subparsers for commands
    subparsers = parser.add_subparsers(help="Commands:")

    # Atomic sub-parsers
    discover = subparsers.add_parser('discover', help='Discover supported printers')
    discover.set_defaults(cmd='discover')

    discover = subparsers.add_parser('info', help='List information about a connected printer')
    discover.set_defaults(cmd='info')

    # Complex subparsers
    print_menu = subparsers.add_parser('print')
    print_menu.add_argument("-r", "--rotate", default='auto',
                            choices=['auto', '0', '90', '180', '270'],
                            help='Rotate the image (counter clock-wise) by this amount of degrees. '
                                 '(default: %(default)s)')
    #print_menu.add_argument("-t", "--threshold", type=float, default=0.1,
    #                        help="The threshold value (in percent) to discriminate between black and white pixels.")
    #print_menu.add_argument("-n", "--no-cut", action='store_true', help="Don't cut the tape after printing the label.")
    print_menu.add_argument("-m", "--margin", type=int, default=0,
                            help="Print margin in dots.")
    print_menu.add_argument("-f", "--file", type=str, required=True, nargs='+', help="Image file(s) to print")
    print_menu.set_defaults(cmd='print')

    args = parser.parse_args()

    if args.version:
        print(VERSION)
        return 0

    if args.debug:
        show_status(args.printer)

    elif 'cmd' not in args:
        print('Missing command', file=sys.stderr)
        parser.print_help()
        return 1
    elif args.cmd == 'discover':
        return list_printers(args.printer)
    elif args.cmd == 'info':
        if not args.debug:
            return show_status(args.printer)
        else:
            return 0
    elif args.cmd == 'print':
        return do_print(args)

    return 0


if __name__ == '__main__':
    sys.exit(cli())
