# -*- coding: UTF-8 -*-
from __future__ import print_function
import os
import datetime
import json
import pprint
import argparse
from django.core.management.base import BaseCommand
from django.conf import settings
from pdf.utils import build_pdf_document
from pdf.views import PdfTestView
from pdf.plot import build_plot_from_data

        # fonts = sorted(set([f.name for f in matplotlib.font_manager.fontManager.ttflist]))
        # print(fonts)

        # rcParams['font.family'] = 'Tahoma'

class Command(BaseCommand):
    help = "Build a test PDF document (or plot)"
    epilog = """
Sample usages:


python manage.py build_test_pdf test.pdf -o


python manage.py build_test_pdf test.png -o -p '{"labels": ["sin", "cos"], "x": [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5], "columns": [[0.0, 9.09, -7.57, -2.79, 9.89, -5.44, -5.37, 9.91, -2.88, -7.51], [20.0, -13.07, -2.91, 16.88, -19.15, 8.16, 8.48, -19.25, 16.68, -2.56]]}' --plot_font Tahoma


python manage.py build_test_pdf test.png -o --plot_type horizontalBar -p '{"labels": [null], "columns": [[1085, 839, 340, 285, 270, 211, 210, 177, 161, 141, 139, 137, 137, 134, 124, 122, 119, 116, 112, 108]], "colors": [["#f2f6ee", "#353a3a", "#fcfcfc", "#a23c3a", "#ffd100", "#0f6fa8", "#00968f", "#33b3ad", "#c80000", "#a83e3b", "#244f28", "#b8c0c2", "#586062", "#655580", "#6fd3d1", "#d0cd1d", "#cacac5", "#828b88", "#148396", "#bec8d1"]], "x": ["CW051W", "AC144N", "0011/Sugar Dust-EA Semibrillo Sipa Alfa-Sipamundo-Base Master", "AC118R", "AC105Y", "AC079N", "7116A", "7115D", "1109/Party Time-EA Semibrillo Sipa Alfa-Sipamundo-Base Master", "AC111R", "0535/Zen Retreat-EA Semibrillo SipaAlfa-Sioamundo-BaseMaster", "0546/Paternoster-EA Semibrillo Sipa Alfa-Sipamundo-Base Master", "0534/Subtle Shadow-EA Semibrillo Sipa Alfa-Sipamundo-Base Master", "7006N", "7114M", "7216N", "8792W/Monorail Silver CGl -E.A. P. y F. BioTech-Fandex Millennium-Base Blanca", "0533/Techile-EA Semibrillo Sipa Alfa-Sipamundo-Base Master", "0682/Pleasant Stream-EA Semibrillo Sipa Alfa-Sipamundo-Base Master", "0510/Sacred Spring-EA Semibrillo Sipa Alfa-Sipamundo-Base Master"]}'


python manage.py build_test_pdf test.png -o -p '{"labels": ["Total", "Custom", "Stock"], "columns": [[4, 13, 101, 78, 94, 152, 198, 337, 329, 290, 278, 295, 448, 353, 326, 512, 559, 408, 512, 440, 815, 1390, 819, 1562, 2615, 2217, 2352, 1929, 3469, 5791, 6900, 6195], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 25, 0, 0, 14, 36, 67, 8, 46, 67, 519, 585, 559, 433], [4, 13, 101, 78, 94, 152, 198, 337, 329, 290, 278, 295, 448, 353, 326, 512, 559, 408, 512, 415, 815, 1390, 805, 1526, 2548, 2209, 2306, 1862, 2950, 5206, 6341, 5762]], "colors": ["rgba(64, 113, 191, 0.2)", "rgba(191, 64, 64, 0.0)", "rgba(26, 179, 148, 0.0)"], "x": ["03/01/2018", "04/01/2018", "05/01/2018", "06/01/2018", "07/01/2018", "08/01/2018", "09/01/2018", "10/01/2018", "11/01/2018", "12/01/2018", "01/01/2019", "02/01/2019", "03/01/2019", "04/01/2019", "05/01/2019", "06/01/2019", "07/01/2019", "08/01/2019", "09/01/2019", "10/01/2019", "11/01/2019", "12/01/2019", "01/01/2020", "02/01/2020", "03/01/2020", "04/01/2020", "05/01/2020", "06/01/2020", "07/01/2020", "08/01/2020", "09/01/2020", "10/01/2020"]}'


python manage.py build_test_pdf test.png -o --plot_type pie -p '{"labels": [], "columns": [[1498, 1217, 528, 479, 363, 353]], "colors": [["rgb(255, 99, 132)", "rgb(255, 159, 64)", "rgb(255, 205, 86)", "rgb(75, 192, 192)", "rgb(54, 162, 235)", "rgb(153, 102, 255)", "rgb(201, 203, 207)"]], "x": ["255: TOO LOW WATER LEVEL", "210: DOOR OPEN", "211: COVERS NOT AVAILABLE", "2000: Paper end", "1000: Scale not responding", "895: CAN_ABSENT_DURING_DISPENSING"]}'


python manage.py build_test_pdf test.png -o --plot_type doughnut -p '{"labels": [], "columns": [[1498, 1217, 528, 479, 363, 353]], "colors": [["rgb(255, 99, 132)", "rgb(255, 159, 64)", "rgb(255, 205, 86)", "rgb(75, 192, 192)", "rgb(54, 162, 235)", "rgb(153, 102, 255)", "rgb(201, 203, 207)"]], "x": ["255: TOO LOW WATER LEVEL", "210: DOOR OPEN", "211: COVERS NOT AVAILABLE", "2000: Paper end", "1000: Scale not responding", "895: CAN_ABSENT_DURING_DISPENSING"]}'

"""

    def create_parser(self, prog_name, subcommand, **kwargs):
        if self.epilog:
            kwargs.update({
                'epilog': self.epilog,
            })
        parser = super().create_parser(prog_name, subcommand, **kwargs)
        if self.epilog:
            parser.formatter_class =  argparse.RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        parser.add_argument("filepath", help='ouput file path (use .pdf or .png extension as required')
        parser.add_argument('--open', '-o', action='store_true', help="open resulting file")
        parser.add_argument("--plot_data", "-p", help='JSON plot data to build a bitmap (instead of a pdf)')
        parser.add_argument('--plot_type', "-t", choices=['line', 'bar', 'horizontalBar', 'pie', 'doughnut', ], default="line")
        parser.add_argument('--plot_font', )
        parser.add_argument('--list_fonts', "-l", action='store_true', help="list matplotlib fonts and exit")

    def list_fonts(self):
        import matplotlib
        fonts = list(set([f.name for f in matplotlib.font_manager.fontManager.ttflist]))
        sorted_fonts = sorted(fonts, key=str.casefold)
        pprint.pprint(sorted_fonts)

    def select_font(self, font):
        import matplotlib
        matplotlib.rcParams['font.family'] = font

    def handle(self, *args, **kwargs):

        if kwargs['list_fonts']:
            # list fonts and exit
            self.list_fonts()
            return

        if kwargs['plot_font']:
            self.select_font(kwargs['plot_font'])

        # Use either user supplied filepath, or the a default name provided by the view
        expected_file_extension = '.pdf'
        filepath = kwargs['filepath']
        filename, file_extension = os.path.splitext(filepath)

        # Retrieve and deserialized user-supplied plot data
        plot_data = kwargs['plot_data']
        if plot_data is not None:
            plot_data = json.loads(plot_data)
            expected_file_extension = '.png'

        # File cleanup
        assert file_extension.lower() == expected_file_extension, "Wrong extension: %s" % file_extension
        if os.path.isfile(filepath):
            os.remove(filepath)

        with open(filepath, 'wb') as f:
            if plot_data is not None:
                image = build_plot_from_data(
                    plot_data,
                    chart_type=kwargs['plot_type'],
                    as_base64=False,
                    dpi=300,
                    ylabel='test plot',
                )
                f.write(image)
            else:
                # Create a View to work with
                view = PdfTestView()
                context = view.get_context_data()
                view.render_as_pdf_to_stream('', context, f)

        print('Result in: "%s"' % os.path.abspath(filepath))
        if kwargs['open']:
            os.system('open %s' % filepath)
