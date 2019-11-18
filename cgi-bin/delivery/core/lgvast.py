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
	if (key == 'event'):
		event 	= value
	


print(bannerId)
print(zoneId)
print(event)

dateTime			= now.strftime('%Y-%m-%d %H:00:00');


myFile				= "../cache/"+"delivery_ad_"+str(bannerId)+".py"
f					= open(myFile,"r")
jsonString			= f.read()
completeArr  		= json.loads(jsonString)
f.close()



aVastEventStrToIdMap = {
	 'start' : 1,
	 'midpoint' : 3,
	 'firstquartile' : 2,
	 'thirdquartile' : 4,
	 'complete' : 5,
	 'skip' : 6,
	 'replay' : 7,
	 'pause_time' : 8,
	 'play_time' : 9,
	 'mute_time' : 10,
	 'resume' : 11,
	 'pause' : 12,
}

vastEventId		= aVastEventStrToIdMap[event];
query			= "INSERT INTO rv_data_bkt_vast_e (interval_start, creative_id, zone_id, vast_event_id,count) VALUES ('"+dateTime+"', '"+str(bannerId)+"','"+str(zoneId)+"', '"+str(vastEventId)+"', '1')  ON CONFLICT ON CONSTRAINT rv_data_bkt_vast_e_pkey  DO UPDATE SET count = rv_data_bkt_vast_e.count + 1";

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

#print(completeArr)

if(completeArr[0]['ext_bannertype'] == 'create_video'):
	vastData					= completeArr[1];
	# if(vastEventId == 1 and vastData['start_pixel']):
	# if(vastEventId == 2 and vastData['quater_pixel']):
	# if(vastEventId == 3 and vastData['mid_pixel']):
	# if(vastEventId == 4 and vastData['third_quater_pixel']):
	# if(vastEventId == 5 and vastData['end_pixel']):
		
	
