df_wind = pd.read_csv('https://plot.ly/~datasets/2805.csv')

df_known_capacity = df_wind[ df_wind['total_cpcy'] != -99999.000 ]
df_sum = df_known_capacity.groupby('manufac')['total_cpcy'].sum().sort_values(ascending=False).to_frame()

df_farms = pd.read_csv('https://plot.ly/~jackp/17256.csv')
df_farms.set_index('Wind Farm', inplace=True)

wind_farms=list([
    dict(
        args=[ { 
            'mapbox.center.lat':38,
            'mapbox.center.lon':-94,
            'mapbox.zoom':3,
            'annotations[0].text':'All US wind turbines (scroll to zoom)'
        } ],
        label='USA',
        method='relayout'
    )
])

for farm, row in df_farms.iterrows():
    desc = []
    for col in df_farms.columns:
        if col not in ['DegMinSec','Latitude','Longitude']:
            if str(row[col]) not in ['None','nan','']: 
                desc.append( col + ': ' + str(row[col]).strip("'") )
    desc.insert(0, farm)
    wind_farms.append( 
        dict(
            args=[ { 
                'mapbox.center.lat':row['Latitude'], 
                'mapbox.center.lon':float(str(row['Longitude']).strip("'")), 
                'mapbox.zoom':9,
                'annotations[0].text': '<br>'.join(desc)
            } ],
            label=' '.join(farm.split(' ')[0:2]),
            method='relayout'
        )
    )

data = []
for mfr in list(df_sum.index):
    if mfr != 'unknown':
        trace = dict(
            lat = df_wind[ df_wind['manufac'] == mfr ]['lat_DD'],
            lon = df_wind[ df_wind['manufac'] == mfr ]['long_DD'],
            name = mfr,
            marker = dict(size = 4),
            type = 'scattermapbox'
        )
    data.append(trace)

# mapbox_access_token = 'insert mapbox token here'

layout = dict(
    height = 800,
    margin = dict( t=0, b=0, l=0, r=0 ),
    font = dict( color='#FFFFFF', size=11 ),
    paper_bgcolor = '#000000',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=dict(
            lat=38,
            lon=-94
        ),
        pitch=0,
        zoom=3,
        style='dark'
    ),
)

updatemenus=list([
    dict(
        buttons = wind_farms[0:10],
        pad = {'r': 0, 't': 10},
        x = 0.1,
        xanchor = 'left',
        y = 1.0,
        yanchor = 'top',
        bgcolor = '#AAAAAA',
        active = 99,
        bordercolor = '#FFFFFF',
        font = dict(size=11, color='#000000')
    ),
    dict(
        buttons=list([
            dict(
                args=['mapbox.style', 'dark'],
                label='Dark',
                method='relayout'
            ),                    
            dict(
                args=['mapbox.style', 'light'],
                label='Light',
                method='relayout'
            ),
            dict(
                args=['mapbox.style', 'satellite'],
                label='Satellite',
                method='relayout'
            ),
            dict(
                args=['mapbox.style', 'satellite-streets'],
                label='Satellite with Streets',
                method='relayout'
            )                    
        ]),
        direction = 'up',
        x = 0.75,
        xanchor = 'left',
        y = 0.05,
        yanchor = 'bottom',
        bgcolor = '#000000',
        bordercolor = '#FFFFFF',
        font = dict(size=11)
    ),        
])

annotations = list([
    dict(text='All US wind turbines (scroll to zoom)', font=dict(color='magenta',size=14), borderpad=10, 
         x=0.05, y=0.05, xref='paper', yref='paper', align='left', showarrow=False, bgcolor='black'),
    dict(text='Wind<br>Farms', x=0.01, y=0.99, yref='paper', align='left', showarrow=False,font=dict(size=14))
])

layout['updatemenus'] = updatemenus
layout['annotations'] = annotations

figure = dict(data=data, layout=layout)
py.iplot(figure, filename='wind-turbine-territory-dropdown')