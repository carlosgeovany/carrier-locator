def map_folium(zip_codes,df):
	import folium
	import pandas as pd

	def get_lat_lon(zip_code):
	    import pgeocode
	    nomi=pgeocode.Nominatim('US')
	    z=nomi.query_postal_code(zip_code)
	    return [z.latitude, z.longitude]

	def color(carrier): 
	    if carrier == "FEDEX": 
	        col = '#4d148c'
	    if carrier == "UPS": 
	        col = '#4c3404'
	    return col


	lat,lon = get_lat_lon(zip_codes[0])
	m = folium.Map(location=[lat,lon], 
	                default_zoom_start=12,
	                tiles="Stamen Toner"
	                )
	for z in zip_codes:
	    folium.Marker(
	        location=get_lat_lon(z),
	        tooltip='Zip Code: {}'.format(z)
	    ).add_to(m)

	 

	for index, row in df.iterrows():
	    tooltip = '{}<br>Distance: {}'.format(row['TYPE'],row['DISTANCE'])
	    folium.Marker(
	        location=[row['COORDS'][0], row['COORDS'][1]],
	        tooltip=tooltip,
	        icon=folium.Icon(color='lightgray',icon_color=color(row['CARRIER']))
	    ).add_to(m)

	m.save("locations.html")