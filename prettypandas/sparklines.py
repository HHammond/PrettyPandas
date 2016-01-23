from jinja2 import Template
import numpy as np


def build_sparkline(values, **kwargs):
    return Sparkline(np.array(values), **kwargs)


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

    TEMPLATE = """
        {% macro circle(x, y, fill, class="", r=2) -%}
            <circle cx="{{ x }}"
                    cy="{{ y }}"
                    r="{{ r }}"
                    fill="{{ fill }}"
                    class="{{ class }}"
                    />
        {%- endmacro %}

        <svg width="{{width}}"
             height="{{height}}"
             version="1.1"
             xmlns="http://www.w3.org/2000/svg">

          <polyline points="
            {%- for x, y in points -%}
                {{ x }} {{ y }},
            {%- endfor -%}"

          class="line"
          fill="transparent"
          stroke="{{ line_color }}" />

          {% if not show_max and not show_min %}
            {{ circle(points[-1][0], points[-1][1], line_color, class="end") }}
          {% endif %}

          {% for x, y in maxs %}
            {{ circle(x, y, max_color, class="max", r=2)}}
          {% endfor %}

          {% for x, y in mins -%}
            {{ circle(x, y, min_color, class="min", r=2)}}
          {%- endfor %}

        </svg>
        """

    def __init__(self,
                 data,
                 width=150,
                 height=20,
                 height_offset=2,
                 width_offset=2,
                 show_max=True,
                 show_min=True,
                 min_color="red",
                 max_color="green",
                 line_color="black",
                ):
        self.data = np.array(data)
        self.width = width
        self.height = height
        self.height_offset = height_offset
        self.width_offset = width_offset
        self.show_max = show_max
        self.show_min = show_min

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

    def render(self):
        """Render SVG template."""
        xs, ys = self.xs, self.ys
        points = list(zip(xs, ys))
        template = Template(self.TEMPLATE)

        maxs = self._get_max(xs, ys) if self.show_max else []
        mins = self._get_min(xs, ys) if self.show_min else []

        return template.render(data=self.data,
                               points=points,
                               width=self.width,
                               height=self.height,
                               width_offset=self.width_offset,
                               maxs=maxs,
                               mins=mins,
                               show_max=self.show_max,
                               show_min=self.show_min,
                               min_color=self.min_color,
                               max_color=self.max_color,
                               line_color=self.line_color)

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
        min, max = self.data.min(), self.data.max()
        height = self.height - 2 * self.height_offset
        v = height * self._scale(value, min, max)

        return height - v + self.height_offset
