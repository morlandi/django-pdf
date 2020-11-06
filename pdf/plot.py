import io
import base64
import json
import math
from PIL import Image as PILImage
import datetime


def build_plot_from_data(data, as_base64=False, plot_colors=None, dpi=300):
    """
    Build a plot from given "data";
    Returns: a bitmap of the plot

    Requires:
        matplotlib

    Keyword arguments:
    data -- see sample_plot_data() for an example; if None, uses sample_plot_data()
    as_base64 -- if True, returns the base64 encoding of the bitmap
    plot_colors -- an array of color codes to cycle over; if None, uses default colors
    dpi -- bitmpa resolution
    """


    if data == None:
        data = sample_plot_data()

    if False:
        image_content = build_random_image()
    else:
        image_content = None
        try:
            with io.BytesIO() as buffer:

                _build_plot_image(data, buffer, plot_colors=plot_colors, dpi=dpi)

                #buffer.seek(0)
                pil_image = PILImage.open(buffer)
                with io.BytesIO() as output:
                    pil_image.save(output, format="PNG")
                    image_content = output.getvalue()
        except Exception as e:
            print('ERROR in build_plot_from_data():' + str(e))
            raise

    if as_base64:
        return base64.b64encode(image_content).decode()

    return image_content


def sample_plot_data():
    n = 100
    data = {
        'labels': ["sin", "cos"],
        'x': [0.5 * i for i in range(n)],
        'columns': [
            [10.0 * math.sin(i/2.0) for i in range(n)],
            [20.0 * math.cos(i/4.0) for i in range(n)],
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


def default_plot_colors():
    return [
        # Dygraphs defaults
        #"rgb(0,85,128)", "rgb(85,128,0)", "rgb(0,0,128)", "rgb(0,128,0)", "rgb(85,0,128)", "rgb(0,128,85)", "rgb(128,0,85)", "rgb(128,85,0)"
        #'#97742F', '#015480', '#648B18', '#292894', '#007F01', '#4C0E72', '#008055', '#800055',

        # CanvasJS defaults
        '#369EAD', '#C24642', '#7F6084', '#86B402', '#52514E', '#C8B631', '#6DBCEB', '#52514E',
    ]

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
            tokens = [int(t) for t in content.split(',')]
            color_code = '#%02x%02x%02x' % (tokens[0], tokens[1], tokens[2], )
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


def _build_plot_image(plot_data, output_buffer, plot_colors, dpi):
    """
    Read rectangular data from given "input_filename" CSV file, and build a bitmap with the plot;
    the result is saved in "output_filename"
    """

    # Solve "'NSWindow drag regions should only be invalidated on the Main Thread!' - macos/python"
    # https://github.com/matplotlib/matplotlib/issues/14304#issuecomment-545717061
    import matplotlib
    from matplotlib import pyplot as plt

    matplotlib.use('agg')

    if plot_colors is None:
        plot_colors = default_plot_colors()

    x = plot_data['x']
    num_cols = len(plot_data['columns'])

    # Scan columns
    # for index, y in enumerate(data['columns']):
    #     # add this column to chart
    #     color = _rgb_string_to_color_code(chart_color(index))
    #     plt.plot(x, y, color, linewidth=1)
    formatter = matplotlib.ticker.FuncFormatter(_format_x_time)
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(8,3), dpi=dpi, tight_layout=True)
    axes.xaxis.set_major_formatter(formatter)
    for index, y in enumerate(plot_data['columns']):
        # add this column to chart
        color = _plot_color(plot_colors, index)
        axes.plot(x, y, color, linewidth=1)

    # plt.ylabel('some numbers')
    plt.grid()
    plt.savefig(output_buffer)  # , dpi=600)


