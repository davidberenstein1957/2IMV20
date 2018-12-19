from os.path import dirname, join
import pandas as pd
import numpy as np
import pandas.io.sql as psql
import sqlite3 as sql

from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.models import FactorRange, ColumnDataSource, Div, LinearColorMapper, BasicTicker, PrintfTickFormatter, ColorBar

from bokeh.models.widgets import Slider, Select, TextInput, MultiSelect
from bokeh.io import curdoc

desc = Div(text=open("description.html").read(), width=800)

# Load data
crimes = pd.read_csv('filtered_data_heatmap.csv', parse_dates=['Date'])
crimes = crimes.drop('Unnamed: 0', axis=1).drop('Latitude', axis=1).drop('Longitude', axis=1)
crimes = crimes.dropna(axis='rows')
crimes = crimes[(crimes['Date'].dt.year >= 2014)]
crimes['Primary Type'] = crimes['Primary Type'].str.lower()
crimes['Location Description'] = crimes['Location Description'].str.lower()
crimes = crimes[crimes['Location Description']!='airport building non-terminal - non-secure area']
crimes = crimes[crimes['Location Description']!='airport building non-terminal - secure area']
crimes = crimes[crimes['Location Description']!='vehicle - other ride share service (e.g., uber, lyft)']
crimes = crimes[crimes['Location Description']!='airport terminal lower level - non-secure area']
crimes = crimes[crimes['Location Description']!='airport terminal lower level - secure area']
crimes = crimes[crimes['Location Description']!='airport terminal mezzanine - non-secure area']
crimes = crimes[crimes['Location Description']!='airport terminal upper level - non-secure area']
crimes = crimes[crimes['Location Description']!='airport terminal upper level - secure area']
crimes['Ward'] = crimes['Ward'].astype(int).astype(str)
crimes['Community Area'] = crimes['Community Area'].astype(int).astype(str)
crimes['Arrest'] = crimes['Arrest'].astype(str)
crimes['Domestic'] = crimes['Domestic'].astype(str)
crimes['District'] = crimes['District'].astype(int).astype(str)
crimes['Beat'] = crimes['Beat'].astype(int).astype(str)
crimes = crimes.dropna(how='any', axis='rows')

# Create Input controls
minimum = min(crimes['Date'].dt.year)
maximum = max(crimes['Date'].dt.year)
min_year = Slider(title="Start Year", start=minimum, end=maximum, value=minimum, step=1)
max_year = Slider(title="End Year", start=minimum, end=maximum, value=maximum, step=1)

option_list = sorted(list(crimes['Primary Type'].unique()))
crime = MultiSelect(title="Crime Type", size=11, value=option_list, options=option_list)

option_list = sorted(list(crimes['Location Description'].unique()))
location = MultiSelect(title="Location Type", size=11, value=option_list, options=option_list)

arrest = Select(title="Arrest (yes/no)", value="All",options=['All', 'True', 'False'])
domestic = Select(title="Domestic (yes/no)", value="All",options=['All', 'True', 'False'])

option_list = sorted(list(crimes['Ward'].unique()), key=lambda e: int(e))
ward = MultiSelect(title="Ward", size=9, value=option_list,options=option_list)

option_list = sorted(list(crimes['Community Area'].unique()), key=lambda e: int(e))
community_area = MultiSelect(title="Community Area", size=10, value=option_list,options=option_list)

option_list = sorted(list(crimes['District'].unique()), key=lambda e: int(e))
district = MultiSelect(title="District", size=9, value=option_list,options=option_list)

option_list = sorted(list(crimes['Beat'].unique()), key=lambda e: int(e))
beat = MultiSelect(title="Beat", size=9, value=option_list,options=option_list)

option_list = ['Count', 'Delta percentage average x-axis', 'Delta percentage average y-axis', 'Delta percentage average total']
aggregate = Select(title="Aggregate Info", options=option_list, value="Count")

x_axis = Select(title="X Axis", options=['year', 'month', 'day', 'weekday', 'hour'], value="year")
y_axis = Select(title="Y Axis", options=['year', 'month', 'day', 'weekday', 'hour'], value="month")

#initialize data
df = crimes
df['day'] = df['Date'].dt.day.astype(str)
df['weekday'] = (df['Date'].dt.weekday).astype(str)
df['hour'] = df['Date'].dt.hour.astype(str)
df['month'] = df['Date'].dt.month.astype(str)
df['year'] = df['Date'].dt.year.astype(str)
df = df.groupby(['year', 'month'], as_index=False)['Ward'].size().reset_index(name='counts')
df['x'] = df['year']
df['y'] = df['month']
df.drop('month', axis=1).drop('year', axis=1)

source = ColumnDataSource(df)

# this is the colormap from the original NYTimes plot
colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
mapper = LinearColorMapper(palette=colors, low=df['counts'].min(), high=df['counts'].max())

p = figure(plot_height=750, plot_width=1200, title="Categorical Heatmap", tools="hover", toolbar_location=None,
           x_range=FactorRange(factors=df['year'].astype(str).unique()), y_range=FactorRange(factors=df['month'].astype(str).unique()[::-1]), x_axis_location="above")

p.rect(x="x", y="y", width=1, height=1,
       source=source,
       fill_color={'field': 'counts', 'transform': mapper},
       line_color='#FFFFFF')

p.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
p.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
p.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
p.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

p.hover.tooltips = [
    ("count", "@counts")
]

color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="5pt",
                     ticker=BasicTicker(desired_num_ticks=len(colors)),
                     formatter=PrintfTickFormatter(format="%d"),
                     label_standoff=6, border_line_color=None, location=(0, 0))
p.add_layout(color_bar, 'right')

def select_crimes():
    arrest_check = []
    if arrest.value == 'All':
        arrest_check = crimes['Arrest'].unique()
    else:
        arrest_check.append(arrest.value)

    domestic_check = []
    if domestic.value == 'All':
        domestic_check = crimes['Domestic'].unique()
    else:
        domestic_check.append(domestic.value)

    selected = crimes[(
        (crimes['Date'].dt.year >= min_year.value) &
        (crimes['Date'].dt.year <= max_year.value) &
        (crimes['Primary Type'].isin(crime.value)) &
        (crimes['Location Description'].isin(location.value)) &
        (crimes['Arrest'].isin(arrest_check)) &
        (crimes['Domestic'].isin(domestic_check)) &
        (crimes['Community Area'].isin(community_area.value)) &
        (crimes['Ward'].isin(ward.value)) &
        (crimes['Beat'].isin(beat.value)) &
        (crimes['District'].isin(district.value))
    )]
    return selected

def grouper(df):
    df['day'] = df['Date'].dt.day.astype(str)
    df['weekday'] = df['Date'].dt.weekday.astype(str)
    df['hour'] = df['Date'].dt.hour.astype(str)
    df['month'] = df['Date'].dt.month.astype(str)
    df['year'] = df['Date'].dt.year.astype(str)
    df = df.groupby([x_axis.value, y_axis.value], as_index=False)['Ward'].size().reset_index(name='rows')
    df['x'] = df[x_axis.value]
    df['y'] = df[y_axis.value]
    # compute diff total
    df['diff_total'] = ((df['rows'].astype(float) - df['rows'].mean()) / df['rows'].mean() * -100)

    df['count'] = 1
    # compute diff x
    df['diff_x'] = 0
    df['diff_y'] = 0
    for x in df[x_axis.value].unique():
        for y in df[y_axis.value].unique():
            df['diff_x'] = np.where(((df[x_axis.value]==x)&(df[y_axis.value]==y)),
                                    ((df['rows']-df[df[x_axis.value]==x]['rows'].mean())/(df[df[x_axis.value]==x]['rows'].mean()))*-100, df['diff_x'])
            df['diff_y'] = np.where(((df[x_axis.value]==x)&(df[y_axis.value]==y)),
                                    ((df['rows'] - df[df[y_axis.value] == y]['rows'].mean()) / (df[df[y_axis.value]==y]['rows'].mean()))*-100, df['diff_y'])
    df['counts'] = df['rows']
    # if aggregate.value == 'Count':
    #     df['counts'] = df['rows']
    # elif aggregate.value == 'Delta percentage average x-axis' :
    #     df['counts'] = df['diff_x']
    # elif aggregate.value == 'Delta percentage average y-axis':
    #     df['counts'] = df['diff_y']
    # else:
    #     df['counts'] = df['diff_total']
    df.drop(x_axis.value, axis=1).drop(y_axis.value, axis=1)
    return df, df

def update():
    p.hover.tooltips = [
        ("count", "@counts")
    ]

    df = select_crimes()
    df, df_data = grouper(df)
    df_data.drop('rows', axis=1).drop('diff_total', axis=1).drop('diff_x', axis=1).drop('diff_y', axis=1)
    x_name = x_axis.value
    y_name = y_axis.value

    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = y_axis.value
    p.title.text = "%d crimes committed" %df['rows'].sum()

    p.x_range.factors = sorted(df['x'].astype(str).unique(), key=lambda e: int(e))
    p.y_range.factors = sorted(df['y'].astype(str).unique(), key=lambda e: int(e))[::-1]

    source.data = ColumnDataSource(df_data).data
    mapper.low = df['counts'].min()
    mapper.high = df['counts'].max()

    p.hover.tooltips = [
        (x_name, '@x'),
        (y_name, '@y'),
        ("Crimes Commited", "@rows"),
        ('Delta from current '+y_name+' average', "@diff_x"+'%'),
        ('Delta from current '+x_name+' average', "@diff_y"+'%'),
        ('Delta average total', "@diff_total"+'%')
    ]


# controls = [min_year, max_year, arrest, domestic, crime, location, ward, community_area, district, beat, x_axis, y_axis]
controls = [min_year, max_year, x_axis, y_axis, arrest, domestic, crime, location, community_area, ward, district, beat]

for control in controls:
    control.on_change('value', lambda attr, old, new: update())

sizing_mode = 'fixed'  # 'scale_width' also looks nice with this example

inputs1 = widgetbox(controls[:8], sizing_mode=sizing_mode)
inputs2 = widgetbox(controls[8:], sizing_mode=sizing_mode)

l = layout([
    [desc],
    [inputs1, inputs2, p],
], sizing_mode=sizing_mode)

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "Crime Heat Map"