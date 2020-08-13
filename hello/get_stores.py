import pandas as pd
import requests

def get_lat_long(zip_code):
    import pgeocode
    nomi=pgeocode.Nominatim('US')
    z=nomi.query_postal_code(zip_code)
    return [z.latitude, z.longitude]

def fedex_stores(zip_code,lat,long):
    import json

    try:
        params={
                    'callback': 'jQuery172019791580931927433_1596506233863',
                    'projectId': '13284125696592996852',
                    'where': 'ST_DISTANCE(geometry, ST_POINT(%s, %s))<160900' %(long,lat),
                    'version': 'published',
                    'key': 'AIzaSyD5KLv9-3X5egDdfTI24TVzHerD7-IxBiE',
                    'clientId': 'WDRP',
                    'service': 'list',
                    'select': 'geometry, PROMOTION_ID, SEQUENCE_ID,ST_DISTANCE(geometry, ST_POINT(%s, %s))as distance'%(long,lat),
                    'orderBy': 'distance ASC',
                    'limit': '20',
                    'maxResults': '20',
                    '_': '1596501760336'
                }
        
        url="https://6-dot-fedexlocationstaging-1076.appspot.com/rest/search/stores"
        response=requests.get(url, params=params)     
        response=response.text
        response=response[58:-2]
        json_res=json.loads(response)
        df1=pd.json_normalize(json_res['features'])
        df1.drop(df1.columns[[0,2,5,6]], axis=1, inplace=True)
        df1.rename(columns={'geometry.coordinates':'COORDS', 'properties.LOC_ID':'LOC_ID','properties.distance':'DISTANCE'}, inplace=True)
        df1['DISTANCE']=df1['DISTANCE'].astype(float)
        df1['DISTANCE']=df1['DISTANCE']*0.000621371
        df1['DISTANCE']=df1['DISTANCE'].apply(lambda x: round(x,1))
        df1['DISTANCE']=df1['DISTANCE'].apply(lambda x: str(x)+" mi")
        
        where=""
        for store in json_res['features']:
            where += "|LOC_ID=\'"+store['properties']['LOC_ID']+"\'"
            
        params={
                    'callback': 'jQuery172019791580931927433_1596506233864',
                    'projectId': '13284125696592996852',
                    'where': where,
                    'version': 'published',
                    'key': 'AIzaSyD5KLv9-3X5egDdfTI24TVzHerD7-IxBiE',
                    'clientId': 'WDRP',
                    'service': "detail"+where,
                    '_': '1596507426896'
                }

        url="https://6-dot-fedexlocationstaging-1076.appspot.com/rest/search/stores"
        response=requests.get(url, params=params)     
        response=response.text
        response=response[58:-2]
        json_res=json.loads(response)
        
        df2=pd.json_normalize(json_res['features'])
        df2=df2[['properties.LOC_ID','properties.ENG_ADDR_LINE_1','properties.ENG_CITY_NAME','properties.STATE_CODE','properties.POSTAL_CODE',
         'properties.ENG_DISPLAY_NAME','properties.SUN_BUS_HRS_1_OPEN_TIME',
         'properties.SUN_BUS_HRS_1_CLOSE_TIME','properties.MON_BUS_HRS_1_OPEN_TIME','properties.MON_BUS_HRS_1_CLOSE_TIME',
         'properties.TUE_BUS_HRS_1_OPEN_TIME','properties.TUE_BUS_HRS_1_CLOSE_TIME','properties.WED_BUS_HRS_1_OPEN_TIME',
         'properties.WED_BUS_HRS_1_CLOSE_TIME','properties.THU_BUS_HRS_1_OPEN_TIME','properties.THU_BUS_HRS_1_CLOSE_TIME',
         'properties.FRI_BUS_HRS_1_OPEN_TIME','properties.FRI_BUS_HRS_1_CLOSE_TIME','properties.SAT_BUS_HRS_1_OPEN_TIME',
         'properties.SAT_BUS_HRS_1_CLOSE_TIME']]
        df2.rename(columns={'properties.LOC_ID':'LOC_ID','properties.ENG_ADDR_LINE_1':'ADDRESS','properties.ENG_CITY_NAME':'CITY',
                     'properties.STATE_CODE':'STATE','properties.POSTAL_CODE':'POSTAL_CODE','properties.ENG_DISPLAY_NAME':'TYPE',
                     'properties.ENG_COMPANY_NAME':'NAME','properties.SUN_BUS_HRS_1_OPEN_TIME':'SUN_OPEN_TIME',
                     'properties.SUN_BUS_HRS_1_CLOSE_TIME':'SUN_CLOSE_TIME','properties.MON_BUS_HRS_1_OPEN_TIME':'MON_OPEN_TIME',
                     'properties.MON_BUS_HRS_1_CLOSE_TIME':'MON_CLOSE_TIME','properties.TUE_BUS_HRS_1_OPEN_TIME':'TUE_OPEN_TIME',
                     'properties.TUE_BUS_HRS_1_CLOSE_TIME':'TUE_CLOSE_TIME','properties.WED_BUS_HRS_1_OPEN_TIME':'WED_OPEN_TIME',
                     'properties.WED_BUS_HRS_1_CLOSE_TIME':'WED_CLOSE_TIME','properties.THU_BUS_HRS_1_OPEN_TIME':'THU_OPEN_TIME',
                     'properties.THU_BUS_HRS_1_CLOSE_TIME':'THU_CLOSE_TIME','properties.FRI_BUS_HRS_1_OPEN_TIME':'FRI_OPEN_TIME',
                     'properties.FRI_BUS_HRS_1_CLOSE_TIME':'FRI_CLOSE_TIME','properties.SAT_BUS_HRS_1_OPEN_TIME':'SAT_OPEN_TIME',
                     'properties.SAT_BUS_HRS_1_CLOSE_TIME':'SAT_CLOSE_TIME'
                    }, inplace=True)
        df2['ADDRESS']=df2[['ADDRESS', 'CITY', 'STATE', 'POSTAL_CODE']].agg(','.join, axis=1)
        df2.drop(df2.columns[[2,3,4]], axis=1, inplace=True)
        df=pd.merge(left=df1, right=df2, on='LOC_ID')
        df.insert(loc=0, column='CARRIER', value="FEDEX")
        df.drop(df.columns[[2]], axis=1, inplace=True)
        df['COORDS'] = df['COORDS'].apply(lambda x:  (x[1],x[0]))
        df.insert(loc=0, column='POST_CODE', value=zip_code)
        df = df.loc[(df['TYPE']=="FedEx Office Ship Center") | 
                    (df['TYPE']=="FedEx Office Print & Ship Center") |
                    (df['TYPE']=="o	FedEx World Service Center")]
        return df
        
    except Exception as e:
        print ('Error occurred : \n Error Message: ' + str(e))

def ups_stores(zip_code,lat,long):
    from bs4 import BeautifulSoup
    
    try:
        header = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8,th;q=0.7',
                'Content-Length': '667',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Host': 'www.ups.com',
                'Origin': 'https://www.ups.com',
                'Referer': 'https://www.ups.com/dropoff/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'                
        }
        data = {
                'reqType': 'results',
                'loc': 'en_US',
                'geolat': '%s'%(lat),
                'geolong': '%s'%(long),
                'page': '1',
                'tot_number_of_records': '10',
                'refineSearch': '1',
                'isSorting': '0',
                'isFullMapView': '0',
                'fromResultPage': '1',
                'isCountryChange': '0',
                'isRefineSearchBtnClick': '0',
                'isGeoCodeCandidate': '0',
                'userLocationDetailsHidden': 'false',
                'startIndex': '1',
                'isWemEnabled': 'Y',
                'CSRFToken': '6e3b5cbb79d9f4637d969e70933202e9',
                'txtquery': '%s'%(zip_code),
                'country': 'US',
                'loc_type': '002,018,001',
                'closest_loc': '25',
                'trans_mode_dow': '03',
                'trans_mode_pkup_time': '1200',
                'opentime_dow': '03',
                'opentime_from': '1200',
                'opentime_to': '1200',
                'sorttype': '01'
        } 
        
        url = "https://www.ups.com/dropoff/"                
        r = requests.post(url, data=data, headers=header)
        
        soup=BeautifulSoup(r.text, "html.parser")
        ul=soup.find("ul", {"class":"mappedResultList"})
        l=[]
        for li in ul.find_all("li"):
            aux=[]
            for span in li.find_all("span"):
                aux.append(span.get_text().replace('\n','').replace('\t','').replace('\r',''))
            for label in li.find_all("label"):
                aux.append(label.get_text())
            for p in li.find_all("p",{"class":"closeTime"}):
                aux.append(p.get_text().replace('\n','').replace('\t','').replace('\r',''))
            l.append([li['id'],aux])
        
        for e in l:
            try:
                i=e[1][7]
            except IndexError:
                e[1].append("Na")
                pass
        df = pd.DataFrame(l)
        df['DISTANCE'] = [e[1][0]for e in l]
        df['TYPE'] = [e[1][2]for e in l]
        df['ADDRESS'] = [e[1][4]for e in l]
        df['CLOSE_TIME'] = [e[1][7]for e in l]
        df['SERVICE'] = [e[1][6]for e in l]
        df.drop(df.columns[1], axis=1, inplace=True)
        df.rename(columns = {0:"COORDS"}, inplace=True)
        df['COORDS'] = [x.strip('()').split(',') for x in df['COORDS']]
        df.insert(loc=0, column='CARRIER', value="UPS")
        df.insert(loc=0, column='POST_CODE', value=zip_code)
        df['TYPE'] = df['TYPE'].str.encode('ascii', 'ignore').str.decode('ascii')
        df['SERVICE'] = df['SERVICE'].str.encode('ascii', 'ignore').str.decode('ascii')
        return df
        
    except Exception as e:
        print ('Error occurred : \n Error Message: ' + str(e))
        
def get_stores(zip_code):
    lat,long=get_lat_long(zip_code)
    f=fedex_stores(zip_code,lat,long)
    u=ups_stores(zip_code,lat,long)
    df = pd.concat([f,u])
    df.reset_index(drop=True, inplace=True)
    return df