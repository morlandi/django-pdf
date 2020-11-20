import io
import base64
import json
import math
from PIL import Image as PILImage
import datetime


def build_plot_from_data(data, chart_type='line', as_base64=False, dpi=300, ylabel=''):
    """
    Build a plot from given "data";
    Returns: a bitmap of the plot

    Requires:
        matplotlib

    Keyword arguments:
    data -- see sample_line_plot_data() for an example; if None, uses sample_line_plot_data()
    chart_type -- 'line', 'bar', 'horizontalBar', 'pie', 'line', 'doughnut',
    as_base64 -- if True, returns the base64 encoding of the bitmap
    dpi -- bitmap resolution
    ylabel -- optional label for Y axis

    Data layout
    ===========

    Similar to django-jchart:

    - either (shared values for x)

        {
            "labels": ["A", "B", ...],
            "x" [x1, x2, ...],
            "columns": [
                [ay1, ay2, ...],
                [by1, by2, ...],
            ],
            "colors": [
                "rgba(64, 113, 191, 0.2)",
                "rgba(191, 64, 64, 0.0)",
                "rgba(26, 179, 148, 0.0)"
            ]
        }

    - or

        {
            "labels": ["A", "B", ..., ],
            "columns": [
                [
                    {"x": ax1, "y": ay1 },
                    {"x": ax2, "y": ay2 },
                    {"x": ax3, "y": ay3 },
                ], [
                    {"x": bx1, "y": by1 },
                    {"x": bx2, "y": by2 },
                ], ...
            ],
            "colors": ["transparent", "rgba(121, 0, 0, 0.2)", "rgba(101, 0, 200, 0.2)", ]
        }

    """

    if data == None:
        data = sample_line_plot_data()

    if False:
        image_content = build_random_image()
    else:
        image_content = None
        try:
            with io.BytesIO() as buffer:

                colors = data['colors'] if 'colors' in data else default_plot_colors()
                if len(colors)>0 and type(colors[0]) == list:
                    colors = colors[0]

                if chart_type == 'line':
                    _build_line_plot_image(data, colors, buffer, dpi=dpi, ylabel=ylabel)
                elif chart_type in ['bar', 'horizontalBar', ]:
                    _build_bar_plot_image(data, colors, buffer, dpi=dpi, ylabel=ylabel, horizontal=(chart_type == 'horizontalBar'))
                elif chart_type == 'pie':
                    _build_pie_plot_image(data, colors, buffer, dpi=dpi, ylabel=ylabel)
                elif chart_type == 'doughnut':
                    _build_doughnut_plot_image(data, colors, buffer, dpi=dpi, ylabel=ylabel)
                else:
                    raise Exception('Unknown chart_type "%s"' % chart_type)

                #buffer.seek(0)
                pil_image = PILImage.open(buffer)
                with io.BytesIO() as output:
                    pil_image.save(output, format="PNG")
                    image_content = output.getvalue()
        except Exception as e:
            print('ERROR in build_plot_from_data(): ' + str(e))
            raise

    if as_base64:
        return base64.b64encode(image_content).decode()

    return image_content


def sample_line_plot_data():

    def real_value(value, decimals=2):
        text = '%.*f' % (decimals, value)
        return float(text)

    n = 100
    data = {
        'labels': ["sin", "cos"],
        'x': [0.5 * i for i in range(n)],
        'columns': [
            [real_value(10.0 * math.sin(i/2.0)) for i in range(n)],
            [real_value(20.0 * math.cos(i/4.0)) for i in range(n)],
        ]
    }
    return data


def build_random_image():
    # For test purposes only
    from random import randint
    rgb = (randint(0, 255), randint(0, 255), randint(0, 255))
    image_size = (200, 200)
    image = PILImage.new('RGB', image_size, rgb)
    with io.BytesIO() as output:
        image.save(output, format="PNG")
        image_content = output.getvalue()
    return image_content


def default_plot_colors(n = None):
    default_colors = [
        # Dygraphs defaults
        #"rgb(0,85,128)", "rgb(85,128,0)", "rgb(0,0,128)", "rgb(0,128,0)", "rgb(85,0,128)", "rgb(0,128,85)", "rgb(128,0,85)", "rgb(128,85,0)"
        #'#97742F', '#015480', '#648B18', '#292894', '#007F01', '#4C0E72', '#008055', '#800055',

        # CanvasJS defaults
        '#369EAD', '#C24642', '#7F6084', '#86B402', '#52514E', '#C8B631', '#6DBCEB', '#52514E',
    ]

    if n is None:
        colors = default_colors[:]
    else:
        colors = []
        m = len(default_colors)
        for i in range(n):
            colors.append(default_colors[i % m])
    return colors

def _format_x_time(seconds, x):
    text = str(datetime.timedelta(seconds=seconds))
    #remove leading "0:"
    if text.startswith('0:'):
        text = text[2:]
    return text


def _plot_color(plot_colors, index):

    def _rgb_string_to_color_code(rgb_string):
        # Accept either rgb(r,g,b) or #colorcode
        if rgb_string.startswith('#'):
            return rgb_string
        try:
            left_brace_position = rgb_string.find('(')
            right_brace_position = rgb_string.find(')')
            content = rgb_string[left_brace_position + 1:right_brace_position]
            tokens = [t.strip() for t in content.split(',')]
            color_code = '#%02x%02x%02x' % (int(tokens[0]), int(tokens[1]), int(tokens[2]), )
        except:
            color_code = '#000000'
        return color_code

    color_code = '#000000'
    if len(plot_colors) > 0:
        try:
            color = plot_colors[index % len(plot_colors)]
            color_code = _rgb_string_to_color_code(color)
        except:
            color_code = '#000000'
    return color_code


def _build_line_plot_image(plot_data, plot_colors, output_buffer, dpi, ylabel):
    """
    Read rectangular data from given "input_filename" CSV file, and build a bitmap with the plot;
    the result is saved in "output_filename"
    """

    # Solve "'NSWindow drag regions should only be invalidated on the Main Thread!' - macos/python"
    # https://github.com/matplotlib/matplotlib/issues/14304#issuecomment-545717061
    import matplotlib
    from matplotlib import pyplot as plt

    matplotlib.use('agg')

    if 'x' in plot_data:
        x_shared = plot_data['x']
    else:
        x_shared = None

    formatter = matplotlib.ticker.FuncFormatter(_format_x_time)
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(8,3), dpi=dpi, tight_layout=True)
    axes.xaxis.set_major_formatter(formatter)
    for index, values in enumerate(plot_data['columns']):

        if x_shared is not None:
            x = x_shared
            y = values
        else:
            x = [item['x'] for item in values]
            y = [item['y'] for item in values]

        #axes.plot(x, y, color, linewidth=1)
        assert len(x) == len(y)
        color = _plot_color(plot_colors, index)
        axes.plot(x, y, color, linewidth=1)
        # # add this column to chart

    plt.ylabel(ylabel)
    if plot_data.get('labels', []):
        plt.legend(plot_data['labels'])
    plt.grid(axis='y', color='#ccc')

    #plt.grid()
    plt.savefig(output_buffer)  # , dpi=600)


def ellipsis(text, max_length):
    if text is None:
        return ''
    text = str(text)
    if len(text) > max_length:
        text = text[:max_length - 1] + '…'
    return text


def _build_bar_plot_image(plot_data, plot_colors, output_buffer, dpi, ylabel, horizontal=False):
    import matplotlib
    from matplotlib import pyplot as plt

    # Solve "'NSWindow drag regions should only be invalidated on the Main Thread!' - macos/python"
    # https://github.com/matplotlib/matplotlib/issues/14304#issuecomment-545717061
    matplotlib.use('agg')

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(8, 6), dpi=dpi, tight_layout=True)

    values = plot_data['columns'][0]
    labels = [ellipsis(l, 20) for l in plot_data['x']]
    assert len(values) == len(labels)

    colors = [_plot_color(plot_colors, index) for index in range(len(values))]
    assert len(values) == len(colors)

    # Higher values at top
    values.reverse()
    labels.reverse()
    colors.reverse()

    if horizontal:
        axes.barh(labels, values, color=colors)
    else:
        axes.bar(labels, values, color=colors)

    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)

    #
    # https://mode.com/example-gallery/python_horizontal_bar/
    #

    # Despine
    axes.spines['right'].set_visible(False)
    axes.spines['top'].set_visible(False)
    axes.spines['left'].set_visible(False)
    axes.spines['bottom'].set_visible(False)

    # Draw vertical axis lines
    vals = axes.get_xticks()
    for tick in vals:
        axes.axvline(x=tick, linestyle='solid', alpha=0.4, color='#eeeeee', zorder=1)

    # # Switch off ticks
    # axes.tick_params(axis="both", which="both", bottom="off", top="off", labelbottom="on", left="off", right="off", labelleft="on")

    # # Format y-axis label
    # axes.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,g}'))


    #plt.legend(plot_data['labels'], fontsize=10, )
    #plt.ylabel(ylabel)
    #plt.grid(axis='y', color='#ccc')
    plt.savefig(output_buffer)  # , dpi=600)


def pct_func(pct, allvals):
    #absolute = int(pct/100.*np.sum(allvals))
    absolute = int(pct/100. * sum(allvals))
    #return "{:.1f}%\n({:d} g)".format(pct, absolute)
    return "{:d}\n({:.1f}%)".format(absolute, pct)


def _build_pie_plot_image(plot_data, plot_colors, output_buffer, dpi, ylabel):

    import matplotlib
    from matplotlib import pyplot as plt

    # Solve "'NSWindow drag regions should only be invalidated on the Main Thread!' - macos/python"
    # https://github.com/matplotlib/matplotlib/issues/14304#issuecomment-545717061
    matplotlib.use('agg')

    # Adapted from:
    # https://matplotlib.org/3.1.1/gallery/pie_and_polar_charts/pie_and_donut_labels.html
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(8, 6), dpi=dpi, tight_layout=True, subplot_kw=dict(aspect="equal"))

    values = plot_data['columns'][0]
    labels = plot_data['x']
    colors = [_plot_color(plot_colors, index) for index in range(len(values))]
    assert len(values) == len(labels)
    assert len(values) == len(colors)
    # values.reverse()
    # labels.reverse()
    # colors.reverse()

    wedges, texts, autotexts = axes.pie(values, autopct=lambda pct: pct_func(pct, values), textprops=dict(color="w"), colors=colors, startangle=90)
    axes.legend(wedges, labels, title="", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    plt.setp(autotexts, size=8, weight="bold")

    if ylabel:
        axes.set_title(ylabel)

    plt.savefig(output_buffer)  # , dpi=600)


def _build_doughnut_plot_image (plot_data, plot_colors, output_buffer, dpi, ylabel):

    import matplotlib
    from matplotlib import pyplot as plt
    import numpy as np

    # Solve "'NSWindow drag regions should only be invalidated on the Main Thread!' - macos/python"
    # https://github.com/matplotlib/matplotlib/issues/14304#issuecomment-545717061
    matplotlib.use('agg')

    # Adapted from:
    # https://matplotlib.org/3.1.1/gallery/pie_and_polar_charts/pie_and_donut_labels.html
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(8, 6), dpi=dpi, tight_layout=True, subplot_kw=dict(aspect="equal"))

    values = plot_data['columns'][0]
    labels = plot_data['x']
    colors = [_plot_color(plot_colors, index) for index in range(len(values))]
    assert len(values) == len(labels)
    assert len(values) == len(colors)
    wedges, texts, autotexts = axes.pie(
        values,
        autopct=lambda pct: pct_func(pct, values),
        pctdistance=0.75,
        #labeldistance=1.2,
        wedgeprops=dict(width=0.5),
        startangle=-40,
        colors=colors
    )

    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"), bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        #axes.annotate(recipe[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y), horizontalalignment=horizontalalignment, **kw)
        axes.annotate(labels[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y), horizontalalignment=horizontalalignment, **kw)

    if ylabel:
        axes.set_title(ylabel)
    plt.savefig(output_buffer)  # , dpi=600)
