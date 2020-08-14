def map_folium(zip_codes,df):
	import folium
	import pandas as pd

	
	lat,long = get_lat_long(zip_codes[0])
	m = folium.Map(location=[lat,long], 
	                default_zoom_start=12,
	                tiles="Cartodb Positron"
	                )
	for z in zip_codes:
	    folium.Marker(
	        location=get_lat_long(z),
	        tooltip='Zip Code: {}'.format(z)
	    ).add_to(m)

	def color(carrier): 
	    if carrier == "FEDEX": 
	        col = '#4d148c'
	    if carrier == "UPS": 
	        col = '#4c3404'
	    return col 

	for index, row in df.iterrows():
	    tooltip = '{}<br>Distance: {}'.format(row['TYPE'],row['DISTANCE'])
	    folium.Marker(
	        location=[row['COORDS'][0], row['COORDS'][1]],
	        tooltip=tooltip,
	        icon=folium.Icon(color='lightgray',icon_color=color(row['CARRIER']))
	    ).add_to(m)

	return m.save("locations.html")