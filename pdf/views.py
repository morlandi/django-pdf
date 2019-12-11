from datetime import datetime

from constance import config
from django.views.generic import TemplateView
from django.template.defaultfilters import slugify
from django.template.loader import get_template
from django.http import HttpResponse
from django.utils import timezone
from django.db import connection

from .utils import get_pdf_styles
from .utils import build_pdf_document
from .utils import Counter

################################################################################
# Base PdfView

class PdfView(TemplateView):

    body_template_name = 'pdf/base.html'
    styles_template_name = ''
    header_template_name = 'pdf/header.html'
    footer_template_name = 'pdf/footer.html'
    title = "Title"
    for_download = False

    body_template = None
    header_template = None
    footer_template = None

    debug = False
    format = 'pdf'
    print_date = None

    def get_context_data(self, **kwargs):
        try:
            self.debug = bool(int(self.request.GET.get('debug')))
        except:
            self.debug = False
        try:
            self.format = self.request.GET.get('format')
        except:
            self.format = 'pdf'
        context = super(PdfView, self).get_context_data(**kwargs)
        self.for_download = context.pop('for_download', False)
        self.print_date = timezone.now()

        # Remove <view> from context to make sure all templates are generic
        context.pop('view', None)

        return context

    def build_filename(self, extension="pdf"):
        filename = timezone.localtime(self.print_date).strftime('%Y-%m-%d_%H-%M-%S__') + slugify(self.title)
        if extension:
            filename += '.' + extension
        return filename

    def render_to_response(self, context, **response_kwargs):
        if self.format == 'html':
            response = self.build_html_response(context)
        else:
            response = self.build_pdf_response(context)
        if self.for_download:
            #filename = self.print_date.strftime('%Y-%m-%d_%H-%M-%S__') + slugify(self.title) + '.pdf'
            filename = self.build_filename()
            response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        return response

    def build_html_response(self, context):

        html = ''
        context.update({
            'debug':self.debug,
            'format':self.format,
            'title':self.title,
            'print_date':self.print_date,
            'page_total': 1,
            'page_counter': 1,
        })
        styles = get_pdf_styles(context, self.styles_template_name)
        context.update({
            'styles': styles,
        })
        for template_name in [self.header_template_name, self.body_template_name, self.footer_template_name, ]:
            template = get_template(template_name) if template_name else None
            if template:
                html += template.render(context)

        # Fix unfetched assets
        html = html.replace('static://', '/static/')
        html = html.replace('media://', '/media/')

        return HttpResponse(html)

    def build_pdf_response(self, context):
        response = HttpResponse(content_type='application/pdf')
        build_pdf_document(
            base_url=self.request.build_absolute_uri(),
            debug=self.debug,
            title=self.title,
            print_date=self.print_date,
            extra_context=context,
            styles_template_name=self.styles_template_name,
            body_template_name=self.body_template_name,
            header_template_name=self.header_template_name,
            footer_template_name=self.footer_template_name,
            output=response,
            format=self.format,
        )
        return response


################################################################################
# Pages

class PdfTestView(PdfView):

    """
    Per il fine-tuning del css conviene invocare direttamente la view dal browser
    e selezionando "format=html",
    al fine di ottenere la pagina HTML che verrebbe utilizzata per il rendering
    del documento PDF.

    Esempio:

    http://127.0.0.1:8000/pdf/test/print/?format=html&debug=1

    """

    body_template_name = 'pdf/pages/test.html'
    styles_template_name = 'pdf/pages/test.css'
    # header_template_name = None
    # footer_template_name = None
    title = "Test"
