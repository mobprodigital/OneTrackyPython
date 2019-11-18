#!/usr/bin/python
import cgi,cgitb
cgitb.enable() #for debugging
import json
import psycopg2
from urlparse  import urlparse
import requests
import time
from datetime import datetime
import os
import pytz
import webbrowser

#import "../config/delivery_config.py"
#import "../config/connection.py"



now 				= datetime.now();
#tz 				= pytz.timezone('Asia/Kolkata')
#your_now 			= now.astimezone(tz)
dateTime			= now.strftime('%Y-%m-%d %H:00:00');
query_string		= os.environ["QUERY_STRING"]
SearchParams 		= [i.split('=') for i in query_string.split('&')]

for key, value in SearchParams:
	if (key == 'bannerid'):
		bannerId = value
	if (key == 'zoneid'):
		zoneId 	= value


myFile				= "../cache/"+"delivery_ad_"+str(bannerId)+".py"
f					= open(myFile,"r")
jsonString			= f.read()
bannerdata  		= json.loads(jsonString)
f.close();


query			= "INSERT INTO rv_data_bkt_c (interval_start, creative_id, zone_id, count) VALUES ('"+dateTime+"', '"+str(bannerId)+"', '"+str(zoneId)+"', '1') ON CONFLICT ON CONSTRAINT rv_data_bkt_c_pkey  DO UPDATE SET count = rv_data_bkt_c.count + 1";



connection = psycopg2.connect(
	user="postgres",
	password="F2X8bXmYYbybnH",
	host="139.59.67.0",
	port="5432",
	database="onetrack_adserver"
)
cursor = connection.cursor()
cursor.execute(query,)
connection.commit()
   
if not isinstance(bannerdata,list):
	if bannerdata['url']:
		url	= bannerdata['url'].replace('%26', '&')
		print("Content-type: text/html\r\nLocation: "+url+"\r\n\r\n")
else:
	if bannerdata[0]['url']:
		url	= bannerdata[0]['url'].replace('%26', '&')
		print("Content-type: text/html\r\nLocation: "+url+"\r\n\r\n")
	
# elif(not (completeArr[1]['vast_video_clickthrough_url'] is None) and completeArr[1]['vast_video_clickthrough_url']):
	# url	= completeArr[1]['vast_video_clickthrough_url'].replace('%26', '&')
	# print("Content-type: text/html\r\nLocation: "+url+"\r\n\r\n")

	