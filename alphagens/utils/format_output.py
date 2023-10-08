import pandas as pd
import sys
import io
import pyperclip

def copy_to_clipboard(func):
    def wrapper(*args, **kwargs):
        # 使用StringIO对象来捕获print输出
        output = func(*args, **kwargs)
        
        # 将捕获的输出复制到剪切板
        pyperclip.copy(output)

    return wrapper

def df_to_latex(df: pd.DataFrame, file, caption=None, label=None):
    result = df.style.to_latex(
        hrules=True,
        position="htbp",
        position_float="centering",
        caption=caption, 
        label=label
    )
    with open(file, "w+") as f:
        f.write(result)

def df_to_html(df, caption=None):
    n_cols = len(df.columns) + 1
    html = df.to_html()
    # 定义前缀和后缀
    prefix = f"""\
<table style="border-collapse: collapse; width: 100%;">
  <caption style="padding: 10px; font-weight: bold;">{caption}</caption>"""

    suffix = """\
  <tfoot>
      <tr style="text-align: right;">
          <td colspan="6" style="border-top: 2px solid black;"></td>
      </tr>
  </tfoot>
</table>
"""

    # 替换原始表格的前缀和后缀
    html = html.replace('<table border="1" class="dataframe">', prefix).replace('</table>', suffix)

    # 为标题行的<th>标签添加上下边框
    html = html.replace('<th>', '<th style="border-top: 2px solid black; border-bottom: 2px solid black; padding: 5px 10px;">', n_cols)  # 只替换前6次，对应标题行的6列

    # 为表体的<tr>标签添加右对齐属性
    html = html.replace('<tr>', '<tr style="text-align: right;">')
    html = html.replace('<th>', '<th style="padding: 5px 10px;">')  # 替换其余的<th>标签，也即是表体中的索引列
    html = html.replace('<td>', '<td style="padding: 5px 10px;">')  # 给<td>标签添加样式

    # 返回转换后的HTML
    return html

@copy_to_clipboard
def df_to_html_to_clipboard(df, caption=None):
    return df_to_html(df, caption)


