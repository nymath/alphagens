import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np


class GradientColor:
    def __init__(self, start_color, end_color, num_levels):
        # 获取预定义颜色的RGB值
        start_color_rgb = mcolors.to_rgb(start_color)
        end_color_rgb = mcolors.to_rgb(end_color)
        # 创建颜色映射
        self.cmap = mcolors.LinearSegmentedColormap.from_list(
            "mycmap", [start_color_rgb, end_color_rgb]
        )
        self.gradient = np.linspace(0, 1, num_levels)
        self.colors = self.cmap(self.gradient)
        self.hex_colors = [mcolors.rgb2hex(color) for color in self.colors]

    def get_hex_colors(self):
        return self.hex_colors

    def print_hex_colors(self):
        for hex_color in self.hex_colors:
            print(hex_color)

    def plot_colors(self):
        fig, ax = plt.subplots(1, 1, figsize=(5, 2),
                                dpi=80, facecolor='w', edgecolor='k')
        for sp in range(len(self.hex_colors)):
            ax.add_patch(
                plt.Rectangle((sp, 0), 1, 1, facecolor=self.hex_colors[sp])
            )
        ax.set_xlim([0, len(self.hex_colors)])
        ax.set_ylim([0, 1])
        ax.set_xticks([])
        ax.set_yticks([])
        plt.show()


class ColorGenerator:
    def __init__(self, n_groups):
        self.n_groups = n_groups
        cmap = plt.get_cmap('coolwarm')
        colors = [cmap(i) for i in np.linspace(0, 1, self.n_groups)]
        self.data = [mcolors.rgb2hex(color) for color in colors]

    def __call__(self):
        return self.data



BASE_COLORS = {'strategy': '#de3633',
            'benchmark': '#80b3f6',
            'excess': '#f4b63f'}




class CICC:
    """
    CICC的配色
    """
    colors = {'red': '#7f2e2a',
              'grey': '#f2f2f2'}

    def __getitem__(self, key):
        return self.colors[key]

    def __repr__(self):
        return self.colors.__repr__()


class LinearAlgebraDoneRight:
    """
    LinearAlgebraDoneRight的配色
    """
    colors = {'darkyellow': '#fdf5a8',
              'lightyellow': '#fefacc',
              'darkblue': '#b7c8e6',
              'lightblue': '#e1e8f5'}

    def __getitem__(self, key):
        return self.colors[key]

    def __repr__(self):
        return self.colors.__repr__()