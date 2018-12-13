import pandas as pd
dateparser_function = lambda x: pd.datetime.strptime(x, '%m/%d/%Y %I:%M:%S %p').strftime('%d-%m-%y %H:%M:%S')
data = pd.read_csv('Crimes_-_2001_to_present.csv',
                   usecols=['Date','IUCR','Location Description','Arrest','Domestic','Ward','Community Area','Latitude','Longitude']
                   , parse_dates=['Date'], date_parser=dateparser_function)
data = data[(data['Date'].dt.year > 2001) & (data['Date'].dt.year < 2018)]
data.to_csv('filtered_data.csv')
