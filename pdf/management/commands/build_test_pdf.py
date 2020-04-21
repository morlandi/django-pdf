# -*- coding: UTF-8 -*-
from __future__ import print_function
import os
import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from pdf.utils import build_pdf_document
from pdf.views import PdfTestView


class Command(BaseCommand):
    help = u'Build a test PDF document'

    def add_arguments(self, parser):
        parser.add_argument("--filepath", "-f", help='ouput file path')

    def handle(self, *args, **kwargs):

        # Create a View to work with
        view = PdfTestView()
        context = view.get_context_data()

        # Use either user supplied filepath, or the a default name provided by the view
        filepath = kwargs['filepath']
        if not filepath:
            filepath = view.build_filename(extension="pdf")

        # File cleanup
        if os.path.isfile(filepath):
            os.remove(filepath)

        with open(filepath, 'wb') as f:
            view.render_as_pdf_to_stream('', context, f)

            # build_pdf_document(
            #     base_url='',
            #     debug=settings.DEBUG,
            #     title='test',
            #     print_date=datetime.datetime.now(),
            #     extra_context={},
            #     styles_template_name='pdf/pages/test.css',
            #     body_template_name='pdf/pages/test.html',
            #     header_template_name='pdf/header.html',
            #     footer_template_name='pdf/footer.html',
            #     output=f,
            #     #format='pdf',
            # )

        print('Result in: "%s"' % os.path.abspath(filepath))
