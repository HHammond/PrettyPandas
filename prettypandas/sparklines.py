from jinja2 import Template
import numpy as np


def build_sparkline(values, **kwargs):
    return Sparkline(np.array(values), **kwargs)


SVG_BASE_TEMPLATE = Template("""
    {% block svg_outer -%}
        <svg width="{{width}}"
             height="{{height}}"
             class="{{ class if class else 'svg' }}"
             version="1.1"
             xmlns="http://www.w3.org/2000/svg"
             >
          {%- block svg_inner -%}
          {%- endblock -%}
        </svg>
    {%- endblock %}
    """)

SVG_MACROS = Template("""
    {% macro circle(x, y, fill, class="", r=2) -%}
        <circle cx="{{ x }}"
                cy="{{ y }}"
                r="{{ r }}"
                fill="{{ fill }}"
                class="{{ class }}"
                />
    {%- endmacro %}
    """)


class Sparkline(object):
    """SVG Sparkline from numpy array.

    :param data:
        Array data to be used for line
    :param width: default 150px
        width of svg
    :param height: default 20px
        height of svg
    :param height_offset:
        offset from top/bottom to line
    :param width_offset:
        offset from sides to lines
    :param show_max:
        show green dot indicating maximums
    :param show_min:
        show red dot indicating minimums
    """

    # flake8: noqa
    TEMPLATE = """
    {% from SVG_MACROS import circle %}

    {% block svg_inner -%}

          <polyline points="{%- for x, y in points -%}
                {{ x }},{{ y }}{{ ' ' }}
            {%- endfor -%} "
          class="line"
          fill="transparent"
          stroke="{{ line_color }}"
          />

          {%- if not show_max and not show_min -%}
            {{ circle(points[-1][0],
                      points[-1][1],
                      line_color,
                      class="end",
                      r=height_offset)
            }}
          {%- endif -%}

          {%- for x, y in maxs -%}
            {{ circle(x, y, max_color, class="max", r=height_offset) }}
          {% endfor %}

          {%- for x, y in mins -%}
            {{ circle(x, y, min_color, class="min", r=height_offset) }}
          {% endfor %}

      {%- endblock %}
    """

    @property
    def OUTER_TEMPLATE(self):
        return "{}{}".format("{% extends SVG_BASE_TEMPLATE %}", self.TEMPLATE)

    def __init__(self,
                 data,
                 width=150,
                 height=20,
                 height_offset=2.5,
                 width_offset=2.5,
                 show_max=True,
                 show_min=True,
                 min_color="#ff0000",
                 max_color="#8ca252",
                 line_color="black",
                 ymin=None,
                 ymax=None):
        self.data = np.array(data)
        self.width = width
        self.height = height
        self.height_offset = height_offset
        self.width_offset = width_offset
        self.show_max = show_max
        self.show_min = show_min
        self.ymin = ymin
        self.ymax = ymax

        self.min_color = min_color
        self.max_color = max_color
        self.line_color = line_color

    def _repr_html_(self):
        return self.render()

    def __repr__(self):
        """Needed to make table display work."""
        return self.render()

    def __str__(self):
        """Needed to make table display work."""
        return self.render()

    def get_context(self):
        xs, ys = self.xs, self.ys
        points = list(zip(xs, ys))

        maxs = self._get_max(xs, ys) if self.show_max else []
        mins = self._get_min(xs, ys) if self.show_min else []

        return {
            "data": self.data,
            "points": points,
            "width": self.width,
            "height": self.height,
            "height_offset": self.height_offset,
            "width_offset": self.width_offset,
            "maxs": maxs,
            "mins": mins,
            "show_max": self.show_max,
            "show_min": self.show_min,
            "min_color": self.min_color,
            "max_color": self.max_color,
            "line_color": self.line_color,
            "SVG_MACROS": SVG_MACROS
        }

    def _render_inner(self):
        """Render SVG template."""
        context = self.get_context()
        context['show_max'] = True
        context['show_min'] = True
        context['maxs'] = []
        context['mins'] = []
        return Template(self.TEMPLATE).render(context)

    def _render_outer(self):
        return Template(self.OUTER_TEMPLATE).render(
            self.get_context(),
            SVG_BASE_TEMPLATE=SVG_BASE_TEMPLATE
        )

    def render(self):
        """Render SVG template."""
        return self._render_outer()

    def _get(self, xs, ys, ixs):
        """Get points based on index."""
        return list(zip(xs[ixs], ys[ixs]))

    def _get_max(self, xs, ys):
        """Get maximum values."""
        return self._get(xs, ys, np.where(self.data == self.data.max()))

    def _get_min(self, xs, ys):
        """Get minimum values."""
        return self._get(xs, ys, np.where(self.data == self.data.min()))

    @property
    def ys(self):
        """Y values for series."""
        return self._scale_y(self.data)

    @property
    def xs(self):
        """X values for series."""
        return np.linspace(self.width_offset,
                           self.width - 2 * self.width_offset,
                           num=self.data.size)

    @staticmethod
    def _scale(value, min, max):
        """Scale value between min and max."""
        return (value - min) / (max - min)

    def _scale_y(self, value):
        """Scale value on Y axis."""
        min = self.ymin if self.ymin is not None else self.data.min()
        max = self.ymax if self.ymax is not None else self.data.max()

        height = self.height - 2 * self.height_offset
        v = height * self._scale(value, min, max)

        return height - v + self.height_offset

    def __add__(self, other):
        if isinstance(other, Sparkline):
            if (self.width, self.height) != (other.width, other.height):
                raise ValueError("Sparklines must have the same size")
            return MultiSparkline([self, other])
        else:
            raise TypeError("Cannot add to Sparkline")


class MultiSparkline(object):

    TEMPLATE = Template("""
    {% extends SVG_BASE_TEMPLATE %}

    {% block svg_inner %}
        {% for sparkline in sparklines -%}
            {{ sparkline }}
        {%- endfor %}
    {% endblock %}
    """)

    def __init__(self, values=None):
        self.values = values or []

    def __add__(self, other):
        if isinstance(other, MultiSparkline):
            return MultiSparkline(self.values + other.values)

        if isinstance(other, Sparkline):
            return MultiSparkline(self.values + [other])

        raise TypeError("Only Sparkline and MultiSparkline objects may be "
                        "added to a MultiSparkline.")

    def get_context(self):
        if self.values:
            width = self.values[0].width
            height = self.values[0].height
        else:
            width, height = 0, 0

        return {
            'width': width,
            'height': height,
            'sparklines': (v._render_inner() for v in self.values)
        }

    def render(self):
        return self.TEMPLATE.render(self.get_context(),
                                    SVG_BASE_TEMPLATE=SVG_BASE_TEMPLATE)

    def _repr_html_(self):
        return self.render()

    def __repr__(self):
        return self.render()

    def __str__(self):
        return self.render()
