from __future__ import print_function
import pandas as pd
from bokeh.charts import Bar
from bokeh.plotting import figure
from bokeh.models import PrintfTickFormatter
from bokeh.resources import CDN
from bokeh.embed import autoload_static
from bokeh.models import LinearAxis, Range1d
import os
from .utils import get_date_range
from .config import data_dir


def plot(newest_changes):
    filelist = os.listdir('{}/{}/'.format(data_dir, newest_changes))
    culture_file = [f for f in filelist if f.startswith('culture')][0]
    date_range = None
    if newest_changes == 'newest-changes':
        start, end = culture_file.split('culture-index-from-')[1].split('.csv')[0].split('-to-')
        date_range = get_date_range(start, end)
    csv_to_read = '{}/{}/{}'.format(data_dir, newest_changes,culture_file)

    df = pd.DataFrame.from_csv(csv_to_read)
    no_gender_perc = df['nan'].sum() / df.sum().sum()

    # remove nan genders and nan rows
    del df['nan']
    df = df[list(map(lambda x: not pd.isnull(x), df.index))]

    df['total'] = df.sum(axis=1)
    df['nonbin'] = df['total'] - df['male'] - df['female']
    df['fem_per'] = df['female'] / (df['total'])
    df['nonbin_per'] = df['nonbin'] / df['total']
    df['fem_per_million'] = df['fem_per'] * 1000000
    df['nonbin_per_million'] = df['nonbin_per'] * 1000000
    dfs = df.sort_values('female')

    interesante = ['female','male','nonbin']

    title_suffix = 'Changes since {}'.format(date_range) if newest_changes == 'newest-changes' else 'All Time'

    p = Bar(dfs[['female', 'male']],
            stack=True,
            xlabel="Culture",
            ylabel="Total gendered biographies",
            width=800,
            height=500,
            legend='top_left')

    #bar.yaxis.formatter = NumeralTickFormatter(format="0.0%")
    p._yaxis.formatter = PrintfTickFormatter(format="%5.1e")

    js_filename = "gender_by_culture_{}.js".format(newest_changes)
    output_path = "./files/assets/js/"
    script_path = "./assets/js/"

    # generate javascript plot and corresponding script tag
    js, tag = autoload_static(p, CDN, script_path + js_filename)

    with open(output_path + js_filename, 'w') as js_file:
        js_file.write(js)

    htmltable = dfs[interesante].sort_values('female', ascending=False)
    htmltable.columns=['Women','Men', 'Non Binary']
    top_rows = htmltable.head(10).to_html(na_rep='n/a', classes=['table'])
    bottom_rows = htmltable[::-1].head(10).to_html(na_rep='n/a', classes=['table'])

    return {'plot_tag':tag, 'table_html':[top_rows, bottom_rows], 'date_range':
            date_range}

if __name__ == "__main__":
    print(plot('newest'))
    print(plot('newest-changes'))
