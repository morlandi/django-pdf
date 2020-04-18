
django-pdf
==========

A Django class-based view helper to generate PDF with WeasyPrint.

Requires: `WeasyPrint <https://github.com/Kozea/WeasyPrint>`_

.. contents::

.. sectnum::

Installation
------------

Install the package by running:

.. code:: bash

    pip install git+https://github.com/morlandi/django-pdf

You will probably build you own app in the project to provide derived Views
and custom templates; for example:

.. code:: bash

    python manage.py startapp reports

In your settings, add:

.. code:: python

    INSTALLED_APPS = [
        ...
        'reports',
        'pdf',
    ]

Note that `reports` is listed before `pdf` to make sure you can possibly
override any template.

In your urls, add:

.. code:: python

    urlpatterns = [
        ...
        path('reports/', include('reports.urls', namespace='reports')),
        ...

A sample report
---------------

file `reports/urls.py`:

.. code:: python

    from django.urls import path
    from . import views

    app_name = 'reports'

    urlpatterns = [
        path('test/print/', views.ReportTestView.as_view(), {'for_download': False, 'lines': 200, }, name="test-print"),
        path('test/download/', views.ReportTestView.as_view(), {'for_download': True, 'lines': 200, }, name="test-download"),
    ]


file `reports/views.py`:

.. code:: python

    from pdf.views import PdfView


    class ReportView(PdfView):

        my_custom_data = None

        def get_context_data(self, **kwargs):
            context = super(ReportView, self).get_context_data(**kwargs)
            self.my_custom_data = context.pop('my_custom_data', None)
            return context


    class ReportTestView(ReportView):
        body_template_name = 'pdf/pages/test.html'
        styles_template_name = 'pdf/pages/test.css'
        # header_template_name = None
        # footer_template_name = None
        title = "Report Test"

You can now download the PDF document at:

    http://127.0.0.1:8000/reports/test/download/

or open it with the browser at:

    http://127.0.0.1:8000/reports/test/print/

.. image:: screenshots/001.png


Source HTML and CSS fine-tuning
-------------------------------

    http://127.0.0.1:8000/reports/test/print/?format=html&debug=1

Default files
-------------

You can copy these sample files in your local folders for any required customization::

    pdf
    ├── static
    │   └── pdf
    │       └── images
    │           └── header_left.png
    └── templates
        └── pdf
            ├── base.html
            ├── base_nomargins.html
            ├── styles.css
            ├── footer.html
            ├── header.html
            └── pages
                ├── test.css
                └── test.html

Management commands
-------------------

- build_test_pdf


Full customization with templates
---------------------------------

In your base view class, override template names:

.. code:: python

    class ReportView(PdfView):

        header_template_name = 'reports/header.html'
        footer_template_name = 'reports/footer.html'
        styles_template_name = 'reports/styles.css'

Then copy the following default templates into **reports/templates/reports** ::

    pdf
    └── templates
        └── pdf
            ├── base.html
            ├── base_nomargins.html
            ├── styles.css
            ├── footer.html
            └── header.html

and add you customizations.

How to insert a page break
--------------------------

.. code:: html

    <p style="page-break-before: always" ></p>


Adding Weasyprint to your project
---------------------------------

Add `weasyprint` to your requirements::

    WeasyPrint==51

and optionally to your LOGGING setting::

    LOGGING = {
        ...
        'loggers': {
            ...
            'weasyprint': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }

Deployment:

1) Install Courier fonts for PDF rendering

::

    # You can verify the available fonts as follows:
    #    # fc-list
    - name: Install Courier font for PDF rendering
        become: true
        become_user: root
        copy:
            src: deployment/project/courier.ttf
            dest: /usr/share/fonts/truetype/courier/

The font file can be downloaded here:

`courier.ttf <resources/fonts/courier.ttf>`_

2) You might also need to install the following packages:

::

    #weasyprint_packages:
    - libffi-dev          # http://weasyprint.readthedocs.io/en/latest/install.html#linux
    - python-cffi         # http://weasyprint.readthedocs.io/en/latest/install.html#linux
    - python-dev          # http://weasyprint.readthedocs.io/en/latest/install.html#linux
    - python-pip          # http://weasyprint.readthedocs.io/en/latest/install.html#linux
    - python-lxml         # http://weasyprint.readthedocs.io/en/latest/install.html#linux
    - libcairo2           # http://weasyprint.readthedocs.io/en/latest/install.html#linux
    - libpango1.0-0       # http://weasyprint.readthedocs.io/en/latest/install.html#linux
    - libgdk-pixbuf2.0-0  # http://weasyprint.readthedocs.io/en/latest/install.html#linux
    - shared-mime-info    # http://weasyprint.readthedocs.io/en/latest/install.html#linux
    - libxml2-dev         # http://stackoverflow.com/questions/6504810/how-to-install-lxml-on-ubuntu#6504860
    - libxslt1-dev        # http://stackoverflow.com/questions/6504810/how-to-install-lxml-on-ubuntu#6504860

For an updated list, check here:

https://weasyprint.readthedocs.io/en/latest/install.html#linux

