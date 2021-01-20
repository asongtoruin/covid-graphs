from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import plot_styles
import pandas as pd
import seaborn as sns
from uk_covid19 import Cov19API


graph_folder = Path('Graphs')
graph_folder.mkdir(exist_ok=True)

plt.style.use('blog')
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'Lato'
plt.rcParams['font.weight'] = 'regular'

all_nations = [
    'areaType=nation'
]

cases_and_deaths = {
    'Date': 'date',
    'Name': 'areaName',
    'First': 'cumPeopleVaccinatedFirstDoseByPublishDate',
    'Second': 'cumPeopleVaccinatedSecondDoseByPublishDate',
}

api = Cov19API(
    filters=all_nations,
    structure=cases_and_deaths
)

df = api.get_dataframe()

df['Date'] = pd.to_datetime(df['Date'])
long_data = pd.melt(df, id_vars=['Date', 'Name'], var_name='Vaccine Stage', 
                    value_name='Cumulative Vaccine Recipients')\
              .sort_values(by=['Name', 'Date'])

latest_date = long_data['Date'].max()
days_elapsed = (latest_date - long_data['Date'].min()).days

def label_lines(data, col, color, label, formatter=None, *args, **kwargs):
    ax = plt.gca()
    
    last_value = data.iloc[-1][col]
    
    if formatter:
        label = formatter.format_data(last_value)
    else:
        label = f'{last_value:,}'
    
    ax.annotate(
        text=label, c=color, 
        xy=(1, last_value), xycoords=('axes fraction', 'data'), 
        xytext=(0, 5), textcoords='offset pixels',
        ha='right', va='bottom'
    )

g = sns.FacetGrid(
    data=long_data, row='Name', hue='Vaccine Stage', aspect=3, height=2, 
    sharey=False
)
g.map(plt.plot, 'Date', 'Cumulative Vaccine Recipients', zorder=2)

y_fmt = mtick.EngFormatter(sep='', places=None)
x_fmt = mdates.DateFormatter('%d\n%b')

if days_elapsed < 45:
    x_maj = mdates.WeekdayLocator()
    x_min = mdates.DayLocator()
else:
    if days_elapsed < 100:
        x_maj = mdates.MonthLocator()
    else:
        x_maj = mdates.MonthLocator(interval=3)
    x_min = mdates.WeekdayLocator()

for ax in g.axes.flatten():
    ax.spines['left'].set_visible(False)
    ax.grid(axis='both', ls=':', zorder=1, alpha=.3)
    ax.set_ylim(bottom=0)
    ax.tick_params(axis='y', length=0)
    
    ax.xaxis.set_major_formatter(x_fmt)
    ax.yaxis.set_major_formatter(y_fmt)
    
    ax.xaxis.set_major_locator(x_maj)
    ax.xaxis.set_minor_locator(x_min)
    
    ax.margins(x=0)
    
g.map_dataframe(label_lines, col='Cumulative Vaccine Recipients', )

g.fig.suptitle(
    'UK Covid-19 Vaccine Recipients by Country', weight='bold', size='x-large'
)
g.fig.subplots_adjust(top=.92)

plt.legend(
    title='Vaccine Stage', loc='upper right', bbox_to_anchor=(1, -0.3), ncol=2
)

g.set_titles('{row_name}')

g.axes.flatten()[-1].annotate(
    'Source: coronavirus.data.gov.uk\n'
    f'Data up to and including {latest_date.strftime("%Y-%m-%d")}\n'
    'Processing code: github.com/asongtoruin/covid-graphs',
    xy=(0.05, -0.4), xycoords=('figure fraction', 'axes fraction'), 
    ha='left', va='top', size='small'
)

plt.savefig(graph_folder / 'Vaccine count.png', bbox_inches='tight')
