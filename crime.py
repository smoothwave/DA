import numpy as np
import pandas as pd
import googlemaps

gmaps_key = "AIzaSyDsFrmLqdWV025lbSDSeBHamftfOfA5PQ8" # 자신의 key를 사용합니다.
gmaps = googlemaps.Client(key=gmaps_key)

crime_anal_police = pd.read_csv('crime_in_Seoul_2022.csv', thousands=',', 
                                encoding='utf-8')

station_name = []

for name in crime_anal_police['자치구별(2)']:
    # print(name)
    station_name.append('서울' + str(name) + '청')
    
station_addreess = []
station_lat = []
station_lng = []

for name in station_name:
    tmp = gmaps.geocode(name, language='ko')
    station_addreess.append(tmp[0].get("formatted_address"))

    tmp_loc = tmp[0].get("geometry")

    station_lat.append(tmp_loc['location']['lat'])
    station_lng.append(tmp_loc['location']['lng'])

    # print(name + '-->' + tmp[0].get("formatted_address"))
    
station_addreess[-7] = '대한민국 서울특별시 영등포구'
crime_anal_police.to_csv('crime_in_Seoul_include_gu_name_2022.csv',
                         sep=',', encoding='utf-8')

crime_anal = pd.read_csv('crime_in_Seoul_include_gu_name_2022.csv', 
                             encoding='utf-8', index_col=1)

crime_anal['강간검거율'] = crime_anal['강간 강제추행 검거']/crime_anal['강간 강제추행 발생']*100
crime_anal['강도검거율'] = crime_anal['강도 검거']/crime_anal['강도 발생']*100
crime_anal['살인검거율'] = crime_anal['살인 검거']/crime_anal['살인 발생']*100
crime_anal['절도검거율'] = crime_anal['절도 검거']/crime_anal['절도 발생']*100
crime_anal['폭력검거율'] = crime_anal['폭력 검거']/crime_anal['폭력 발생']*100

del crime_anal['강간 강제추행 검거']
del crime_anal['강도 검거']
del crime_anal['살인 검거']
del crime_anal['절도 검거']
del crime_anal['폭력 검거']

con_list = ['강간검거율', '강도검거율', '살인검거율', '절도검거율', '폭력검거율']

for column in con_list:
    crime_anal.loc[crime_anal[column] > 100, column] = 100
    
crime_anal.rename(columns = {'강간 강제추행 발생':'강간', 
                             '강도 발생':'강도', 
                             '살인 발생':'살인', 
                             '절도 발생':'절도', 
                             '폭력 발생':'폭력'}, inplace=True)

from sklearn import preprocessing

col = ['강간', '강도', '살인', '절도', '폭력']

x = crime_anal[col].values
min_max_scaler = preprocessing.MinMaxScaler()

x_scaled = min_max_scaler.fit_transform(x.astype(float))
crime_anal_norm = pd.DataFrame(x_scaled, columns = col, index = crime_anal.index)

col2 = ['강간검거율', '강도검거율', '살인검거율', '절도검거율', '폭력검거율']
crime_anal_norm[col2] = crime_anal[col2]

result_CCTV = pd.read_csv('01. CCTV_result.csv', encoding='UTF-8', 
                          index_col='구별')

crime_anal_norm[['인구수', 'CCTV']] = result_CCTV[['인구수', '소계']]

col = ['강간','강도','살인','절도','폭력']
crime_anal_norm['범죄'] = np.sum(crime_anal_norm[col], axis=1)

col = ['강간검거율','강도검거율','살인검거율','절도검거율','폭력검거율']
crime_anal_norm['검거'] = np.sum(crime_anal_norm[col], axis=1)

import matplotlib.pyplot as plt
import seaborn as sns
import platform

path = "c:/Windows/Fonts/malgun.ttf"
from matplotlib import font_manager, rc
if platform.system() == 'Darwin':
    rc('font', family='AppleGothic')
elif platform.system() == 'Windows':
    font_name = font_manager.FontProperties(fname=path).get_name()
    rc('font', family=font_name)
else:
    print('Unknown system... sorry~~~~') 
    

sns.pairplot(crime_anal_norm, vars=["강도", "살인", "폭력"], kind='reg', size=3)
plt.show()


sns.pairplot(crime_anal_norm, x_vars=["인구수", "CCTV"], 
             y_vars=["살인", "강도"], kind='reg', size=3)
plt.show()


sns.pairplot(crime_anal_norm, x_vars=["인구수", "CCTV"], 
             y_vars=["살인검거율", "폭력검거율"], kind='reg', size=3)
plt.show()

sns.pairplot(crime_anal_norm, x_vars=["인구수", "CCTV"], 
             y_vars=["절도검거율", "강도검거율"], kind='reg', size=3)
plt.show()


tmp_max = crime_anal_norm['검거'].max()
crime_anal_norm['검거'] = crime_anal_norm['검거'] / tmp_max * 100
crime_anal_norm_sort = crime_anal_norm.sort_values(by='검거', ascending=False)


target_col = ['강간검거율', '강도검거율', '살인검거율', '절도검거율', '폭력검거율']

crime_anal_norm_sort = crime_anal_norm.sort_values(by='검거', ascending=False)

plt.figure(figsize = (10,10))
sns.heatmap(crime_anal_norm_sort[target_col], annot=True, fmt='f', 
                    linewidths=.5, cmap='RdPu')
plt.title('범죄 검거 비율 (정규화된 검거의 합으로 정렬)')
plt.show()


target_col = ['강간', '강도', '살인', '절도', '폭력', '범죄']

crime_anal_norm['범죄'] = crime_anal_norm['범죄'] / 5
crime_anal_norm_sort = crime_anal_norm.sort_values(by='범죄', ascending=False)

plt.figure(figsize = (10,10))
sns.heatmap(crime_anal_norm_sort[target_col], annot=True, fmt='f', linewidths=.5,
                       cmap='RdPu')
plt.title('범죄비율 (정규화된 발생 건수로 정렬)')
plt.show()


crime_anal_norm.to_csv('02. crime_in_Seoul_final.csv', sep=',', 
                       encoding='utf-8')



import folium
import json
geo_path = '02. skorea_municipalities_geo_simple.json'
geo_str = json.load(open(geo_path, encoding='utf-8'))

tmp_criminal = crime_anal_norm['살인'] / crime_anal_norm['인구수'] * 1000000

map = folium.Map(location = [37.5502, 126.982], zoom_start=11,
                tiles = 'cartodbpositron')

folium.Choropleth(
    geo_data = geo_str,
    data = tmp_criminal,
    columns = [crime_anal.index, tmp_criminal],
    fill_color = 'PuRd', #PuRd, YIGnBu
    key_on = 'feature.id'
).add_to(map)

map


crime_anal_police['lat'] = station_lat
crime_anal_police['lng'] = station_lng

col = ['살인 검거', '강도 검거', '강간 강제추행 검거', '절도 검거', '폭력 검거']
tmp = crime_anal_police[col] / crime_anal_police[col].max()

crime_anal_police['검거'] = np.sum(tmp, axis=1)

map = folium.Map(location=[37.5502, 126.982], zoom_start=11)

for n in crime_anal_police.index:
    folium.Marker([crime_anal_police['lat'][n],
                  crime_anal_police['lng'][n]]).add_to(map)
                   
map


map = folium.Map(location=[37.5502, 126.982], zoom_start=11)

for n in crime_anal_police.index:
    folium.CircleMarker([crime_anal_police['lat'][n], crime_anal_police['lng'][n]],
                       radius = crime_anal_police['검거'][n]*10,
                       color='#3186cc', fill_color='#3186cc').add_to(map)
    
map

map = folium.Map(location=[37.5502, 126.982], zoom_start=11)

folium.Choropleth(
    geo_data=geo_str,
    data=crime_anal_norm['범죄'],
    columns=[crime_anal_norm.index, crime_anal_norm['범죄']],
    fill_color='PuRd',  # PuRd, YIGnBu
    key_on='feature.id'
).add_to(map)

for n in crime_anal_police.index:
    folium.CircleMarker([crime_anal_police['lat'][n], crime_anal_police['lng'][n]],
                        radius = crime_anal_police['검거'][n]*10,
                        color = '#3186cc', fill_color='#3186cc').add_to(map)
    
map

