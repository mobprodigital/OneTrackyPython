#!/usr/bin/python
print('Content-type: text/html\r\n\r')
import os
import sys
import psycopg2
import cgi,cgitb
cgitb.enable() #for debugging

def dboperation():
	connection = psycopg2.connect(
		user="postgres",
		password="F2X8bXmYYbybnH",
		host="139.59.67.0",
		port="5432",
		database="onetrack_adserver"
	)
	cursor = connection.cursor()



	
############# handle standerd and html5 ad reporting data #################
	# squery 		= "SELECT m.interval_start, m.creative_id , m.zone_id, m.count as mcount, coalesce(c.count,0) as ccount FROM rv_data_bkt_m m LEFT JOIN rv_data_bkt_c c ON (m.creative_id = c.creative_id and m.zone_id=c.zone_id and m.interval_start=c.interval_start)"
	# cursor.execute(squery,)
	# field_names = [item[0] for item in cursor.description]
	
	# rows 		= cursor.fetchall()
	# if rows:
		# for row in rows:
			# objDict = {}
			# for index, value in enumerate(row):
				# objDict[field_names[index]] = value
			
			# iquery	= "INSERT INTO inventory_rv_data_summary_ad_hourly (date_time, creative_id, zone_id, impressions,clicks) VALUES ('"+str(objDict['interval_start'])+"', "+str(objDict['creative_id'])+", "+str(objDict['zone_id'])+", "+str(objDict['mcount'])+", "+str(objDict['ccount'])+")";
			# cursor.execute(iquery)
			# connection.commit()
			
	
	
	
	
	# dquery	= "delete from rv_data_bkt_m"
	# cursor.execute(dquery)
	# connection.commit()
	
	# dquery	= "delete from rv_data_bkt_c"
	# cursor.execute(dquery)
	# connection.commit()
	

	
############# handle vide ad reporting data #################
	svquery = "SELECT interval_start, creative_id , zone_id,vast_event_id, count FROM rv_data_bkt_vast_e";
	cursor.execute(svquery,)
	field_names = [item[0] for item in cursor.description]

	rows 		= cursor.fetchall()
	if rows:
		for row in rows:
			objDict = {}
			for index, value in enumerate(row):
				objDict[field_names[index]] = value
			
			
			iquery	= "INSERT INTO inventory_rv_stats_vast (interval_start, creative_id, zone_id,vast_event_id, count) VALUES ('"+str(objDict['interval_start'])+"', "+str(objDict['creative_id'])+", "+str(objDict['zone_id'])+","+str(objDict['vast_event_id'])+",  "+str(objDict['count'])+")";
			
			cursor.execute(iquery)
			connection.commit()


			
			
	
	dquery	= "delete from rv_data_bkt_vast_e";
	cursor.execute(dquery,)
	connection.commit()	
	
	
	connection.close()
	

dboperation()









