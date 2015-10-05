import dateutil
import pandas as pd
from bokeh.charts import Line
from bokeh.plotting import gridplot, figure
from bokeh.resources import CDN
from bokeh.models import HoverTool, BoxSelectTool
from bokeh.embed import autoload_static
import os


def plot(newest_changes):
    ra_len = 1 #rolling average lenght

    dox = pd.DataFrame()
    interesante = ['female','male','nonbin']

    for l in ['b', 'd']:
        acro = 'do'+l
        filelist = os.listdir('/home/maximilianklein/snapshot_data/{}/'.format(newest_changes))
        dox_list = [f for f in filelist if f.startswith(acro)]
        dox_file = dox_list[0]
        if newest_changes == 'newest-changes':
            date_range = dox_file.split('{}-index-from-'.format(acro))[1].split('.csv')[0].replace('-',' ')
        csv_to_read = '/home/maximilianklein/snapshot_data/{}/{}'.format(newest_changes,dox_file)
        df = pd.DataFrame.from_csv(csv_to_read)

        del df['nan']
        df = df[list(map(lambda x: not pd.isnull(x), df.index))]

        df['total'] = df.sum(axis=1)
        df['nonbin'] = df['total'] - df['male'] - df['female']
        df['fem_per'] = df['female'] / (df['total'])
        df['nonbin_per'] = df['nonbin'] / df['total']

        for inte in interesante:
            dox['{}-{}'.format(acro, inte)] = df[inte]

    time_range = (1500, 2015)

    dox = dox[time_range[0]: time_range[1]]

    #tups = zip(['Date of Birth']*3 + ['Date of Death']*3, ['Women', 'Men', 'Non-binary']* 2)
    #labs = ['-'.join(x) for x in tups]

    #dox.columns = labs


    title_suffix = 'Changes since {}'.format(date_range) if newest_changes == 'newest-changes' else 'All Time'

    TOOLS = "pan,wheel_zoom,box_zoom,reset,hover,save"
    p = figure(plot_height=500, plot_width=800, tools=TOOLS)

    p.line(dox.index, dox['dob-female'], color="red", line_width=2, legend="DoB (Female)")
    p.line(dox.index, dox['dod-female'], color= "blue", line_width=2, legend="DoD (Female)")
    p.line(dox.index, dox['dob-male'], color="orange", line_width=2, legend="DoB (Male)")
    p.line(dox.index, dox['dod-male'], color="brown", line_width=2, legend="DoD (Male)")

    #p.multi_line(xs=[dox.index]*4,
                 #ys=[dox['dob-female'], dox['dod-female'], dox['dob-male'], dox['dod-male']],
                 #color=['red', 'blue', 'green', 'purple'],
                 #alpha=[0.8, 0.3], line_width=4,
                 #legend="adal")

    p.legend.orientation = 'top_left'
    p.xaxis.axis_label = 'Year'
    p.yaxis.axis_label = 'Number of biographies'

    # setup tools
    hover = p.select(dict(type=HoverTool))
    hover.point_policy = "follow_mouse"
    hover.tooltips = [
        ("index", "$index"),
        ("Year of event", "$x"),
        ("Number of biographies", "$y"),
    ]

    js_filename = "gender_by_dob_{}.js".format(newest_changes)
    script_path = "./assets/js/"
    output_path = "./files/assets/js/"

    # generate javascript plot and corresponding script tag
    js, tag = autoload_static(p, CDN, script_path + js_filename)

    with open(output_path + js_filename, 'w') as js_file:
        js_file.write(js)

    htmltable = dox[['dob-female', 'dod-female', 'dob-male', 'dod-male']]
    htmltable.columns = ['DoB (Female)', 'DoD (Female)', 'DoB (Male)', 'DoD (Male)']
    top_rows = htmltable.head(10).to_html(na_rep="n/a", classes=["table"])
    bottom_rows = htmltable[::-1].head(10).to_html(na_rep="n/a", classes=["table"])

    return {'plot_tag':tag, 'table_html':[top_rows, bottom_rows]}

if __name__ == "__main__":
    print(plot('newest'))
    print(plot('newest-changes'))
