# -*- coding: UTF-8 -*-
from __future__ import print_function
import os
import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from pdf.utils import build_pdf_document


class Command(BaseCommand):
    help = u'Build a test PDF document'

    def add_arguments(self, parser):
        parser.add_argument("filepath", help='ouput file path')

    def handle(self, *args, **kwargs):
        filepath = kwargs['filepath']

        with open(filepath, 'wb') as f:
            build_pdf_document(
                base_url='',
                debug=settings.DEBUG,
                title='test',
                print_date=datetime.datetime.now(),
                extra_context={},
                styles_template_name='pdf/pages/test.css',
                body_template_name='pdf/pages/test.html',
                header_template_name='pdf/header.html',
                footer_template_name='pdf/footer.html',
                output=f,
                #format='pdf',
            )

        print('Result in: "%s"' % os.path.abspath(filepath))
