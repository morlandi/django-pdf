import os
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.auth import get_user_model

__author__ = 'Mario Orlandi, <mailto:morlandi@brainstorm.it>'


def trace(message):
    print(message)


################################################################################
# https://stackoverflow.com/questions/8659560/django-template-increment-the-value-of-a-variable#8671715

class Counter:
    count = 0

    def increment(self):
        self.count += 1
        return ''

    def decrement(self):
        self.count -= 1
        return ''

################################################################################
# Adapted from:
# http://ampad.de/blog/generating-pdfs-django/

def url_fetcher(url):

    import weasyprint
    original_url = url
    url = url

    try:
        if url.startswith('assets://'):
            url = url[len('assets://'):]
            with open(os.path.join(settings.ASSETS_ROOT, url), 'rb') as asset:
                contents = asset.read()
            return dict(string=contents)
        elif url.startswith('static://'):
            url = url[len('static://'):]
            with open(finders.find(url, all=False), 'rb') as asset:
                contents = asset.read()
            return dict(string=contents)

        # TODO: untested ! test me !!!
        elif url.startswith('media://'):
            url = url[len('media://'):]
            with open(os.path.join(settings.MEDIA_ROOT, url), 'rb') as asset:
                contents = asset.read()
            return dict(string=contents)

        elif url.startswith('file:///media/'):
            url = url[len('file:///media/'):]
            with open(os.path.join(settings.MEDIA_ROOT, url), 'rb') as asset:
                contents = asset.read()
            return dict(string=contents)
    except Exception as e:
        trace('Error fetching "%s"' % original_url)
        trace(str(e))
        raise

    return weasyprint.default_url_fetcher(url)


################################################################################
# Helpers

def get_pdf_styles(context, styles_template_name):
    """
    Render stylesheet from default template + (optional) custom template
    """
    styles = render_to_string('pdf/styles.css', context)
    if styles_template_name:
        styles += render_to_string(styles_template_name, context)
    return styles


################################################################################
# Main PDF builder

def build_pdf_document(
        base_url, debug, title, print_date, extra_context,
        styles_template_name, body_template_name, header_template_name, footer_template_name,
        output,
        format='pdf'
    ):
    """
    Create a PDF document and save it into <ouput> buffer;
    strategy:

        1) build context with initialial parameters up to <extra_context>
        2) render templates from template names
        3) build PDF content
        4) split PDF content into header, body and footer
        5) rebuild PDF document paginating previous result
    """

    def render_doc(content, base_url, styles):
        import weasyprint
        doc = weasyprint.HTML(
            string=content,
            base_url=base_url,
            url_fetcher=url_fetcher,
        ).render(
            stylesheets=[weasyprint.CSS(string=styles), ]
        )
        return doc

    def get_page_body(boxes):
        for box in boxes:
            if box.element_tag == 'body':
                return box
            return get_page_body(box.all_children())

    def get_page_fragment(template, base_url, context):
        if template:
            content = template.render(context)
            doc = render_doc(content, base_url, context['styles'])
            body = get_page_body(doc.pages[0]._page_box.all_children())
            body = body.copy_with_children(body.all_children())
        else:
            body = None
        return body

    # Build context for template rendering
    context = extra_context or {}
    context.update({
        'debug': debug,
        'format': format,
        'title': title,
        'print_date': print_date,
        'base_url': base_url,
        'MEDIA_ROOT': settings.MEDIA_ROOT,
        'STATIC_ROOT': settings.STATIC_ROOT,
    })

    # Render styles and add to context
    styles = get_pdf_styles(context, styles_template_name)
    context.update({
        'styles': styles,
    })

    # Load templates
    body_template = get_template(body_template_name) if body_template_name else None
    header_template = get_template(header_template_name) if header_template_name else None
    footer_template = get_template(footer_template_name) if footer_template_name else None

    content = body_template.render(context)
    doc = render_doc(content, base_url, context['styles'])

    # Navigate pages and Insert header and footer in main doc
    context['page_total'] = len(doc.pages)
    for i, page in enumerate(doc.pages):

        context['page_counter'] = i + 1
        page_body = get_page_body(page._page_box.all_children())

        header_body = get_page_fragment(header_template, base_url, context)
        if header_body:
            page_body.children += header_body.all_children()
        footer_body = get_page_fragment(footer_template, base_url, context)
        if footer_body:
            page_body.children += footer_body.all_children()

    doc.write_pdf(output)
    return

