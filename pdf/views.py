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
    _print_date = None

    @property
    def print_date(self):
        if self._print_date is None:
            self._print_date = timezone.now()
        return self._print_date

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
        #self.print_date = timezone.now()

        # Remove <view> from context to make sure all templates are generic
        context.pop('view', None)

        return context

    def build_filename(self, extension="pdf"):
        """
        Provide a stardard filename, build using the print datetime
        and the slugified view title;
        For example:
            '2020-04-17_19-14-55__test.pdf'
        """
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
        html = self.render_as_html_to_string(context)
        return HttpResponse(html)

    def render_as_html_to_string(self, context, custom_template=None):
        html = ''
        context.update({
            'debug':self.debug,
            'format':self.format,
            'title':self.title,
            'print_date': self.print_date,
            'page_total': 1,
            'page_counter': 1,
        })
        styles = get_pdf_styles(context, self.styles_template_name)
        context.update({
            'styles': styles,
        })

        if custom_template is not None:
            templates = [custom_template, ]
        else:
            templates = [self.header_template_name, self.body_template_name, self.footer_template_name, ]

        for template_name in templates:
            template = get_template(template_name) if template_name else None
            if template:
                html += template.render(context)

        # Fix unfetched assets
        html = html.replace('static://', '/static/')
        html = html.replace('media://', '/media/')
        return html

    def build_pdf_response(self, context):
        response = HttpResponse(content_type='application/pdf')
        base_url = self.request.build_absolute_uri()
        self.render_as_pdf_to_stream(base_url, context, response)
        return response

    def render_as_pdf_to_stream(self, base_url, extra_context, output):
        """
        Build the PDF document and save in into "ouput" stream.

        Automatically called when the view is invoked via HTTP (unless self.format == 'html'),
        but you can also call it explicitly from a background task:

            view = PdfTestView()
            context = view.get_context_data()
            with open(filepath, 'wb') as f:
                view.render_as_pdf_to_stream('', context, f)

        """
        build_pdf_document(
            base_url=base_url,
            debug=self.debug,
            title=self.title,
            print_date=self.print_date,
            extra_context=extra_context,
            styles_template_name=self.styles_template_name,
            body_template_name=self.body_template_name,
            header_template_name=self.header_template_name,
            footer_template_name=self.footer_template_name,
            output=output,
            format=self.format,
        )


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            from .plot import build_plot_from_data
            plot_image = build_plot_from_data(data=None, chart_type='line', as_base64=True)
            context.update({
                'plot_image': plot_image,
            })
        except:
            pass
        return context
