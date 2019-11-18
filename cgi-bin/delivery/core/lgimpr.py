#!/usr/bin/python
print('Content-type: text/html\r\n\r')
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

now 				= datetime.now();
# tz 				= pytz.localize('Asia/Kolkata')
# your_now 			= now.astimezone(tz)
ip 					= os.environ["REMOTE_ADDR"]
query_string		= os.environ["QUERY_STRING"]
SearchParams 		= [i.split('=') for i in query_string.split('&')]

for key, value in SearchParams:
	if (key == 'bannerid'):
		bannerId = value
	if (key == 'zoneid'):
		zoneId 	= value


#print(ip)

dateTime			= now.strftime('%Y-%m-%d %H:00:00');
#print(requests.GET.get('bannerid'))

myFile				= "../cache/"+"delivery_ad_"+str(bannerId)+".py"
f					= open(myFile,"r")
jsonString			= f.read()
bannerdata  		= json.loads(jsonString)
f.close()

query			= "INSERT INTO rv_data_bkt_m (interval_start, creative_id, zone_id, count) VALUES ('"+dateTime+"', '"+str(bannerId)+"', '"+str(zoneId)+"', '1') ON CONFLICT ON CONSTRAINT rv_data_bkt_m_pkey  DO UPDATE SET count = rv_data_bkt_m.count + 1"

#print(bannerdata)

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



# if(completeArr[1] and completeArr[1]['impression_pixel']):
	# if(completeArr[1]['impression_pixel']):
		# resp = requests.get('https://todolist.example.com/tasks/')

	
	