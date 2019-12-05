#!/usr/bin/python
print('Content-type: text/html\r\n\r')
import cgi,cgitb
from cgi import parse_qs, escape
cgitb.enable() #for debugging

import json
from urlparse  import urlparse
import hashlib
import time
import os
import sys
from random import randint
from validate import Max_checkClient_Browser,Max_checkClient_Os,Max_checkDevice_Screen,Max_checkGeo_Country,Max_checkGeo_Region
from validate import Max_checkGeo_City,Max_checkMobile_ISP,Max_checkClient_IP,Max_checkClient_Domain
from campaignstatus import checkCampaignStatus



def renderad():
	qs = os.environ['QUERY_STRING']
	d = parse_qs(qs)
	zoneid = d.get('zoneid',[''])[0]
	
	
	protocol			= ''
	dfpClickUrl			= ''
	if not(d.get('adurl',[''])[0] is None):
		Original_url		= qs
		first_index 		= Original_url.find("&click");
		first_string 		= Original_url[first_index:]
		second_index 		= first_string.find("&ord=")
		dfpClickUrl 		= first_string[len("&click")+1:second_index]
		#print(dfpClickUrl)
		#print(len(dfpClickUrl))
		#sys.exit()
		#print(Original_url)
		#print(first_index)
		#print(first_string)
		#print(second_index)
		#print(dfpClickUrl)
		#sys.exit()

		
	#print(dfpClickUrl)
	#sys.exit()
	
	ip					= ''
	iframe				= ''
	
	myFile				= "../cache/"+"delivery_ad_zone_"+str(zoneid)+".py"
	f					= open(myFile,"r")
	jsonString			= f.read()
	zonedata  			= json.loads(jsonString)
	f.close();
	
	adId				= zonedata['ad_id'];
	myFile				= "../cache/"+"delivery_ad_"+str(adId)+".py"
	f					= open(myFile,"r")
	jsonString			= f.read()
	bannerdata  		= json.loads(jsonString)
	f.close();
	
	
	#print(bannerdata)
	#sys.exit()
	result  					= True

	if(result):
		result  					= True
		row							= {}
		row['acl_plugins']			= bannerdata['acl_plugins']
		if(not(row['acl_plugins'] is None) ):
			acl_plugins = bannerdata['compiledlimitation'].split('and')
			for acl_plugin in acl_plugins:
				result 		= eval(acl_plugin.strip())
				#print(acl_plugin)
				if(not result):
					break
	else:
		result  			= False
	
	#print(result)
	#sys.exit()
	
	if result :
		renderdata				= bannerCode(bannerdata,zoneid,protocol,dfpClickUrl,ip,iframe)

	else:
		renderdata 				= ''
	
	
	varString 	= 	hashlib.md5(str(randint(100, 999)).encode())
	var			= varString.hexdigest()
	var			= var[0:8]
	return MAX_javascriptToHTML(renderdata, 'MS_'+var)

	
	
def bannerCode(banner, zoneid, protocol, dfpClickUrl, ip,iframe):
	src			= "https://api.onetracky.com/cgi-bin/delivery/"
	mediaUrl 	= "https://onetracky.com/pydelivery/"
	
	# try:
		# if(os.environ['HTTPS'] == 'on'):
			# src			= "https://api.onetracky.com/cgi-bin/delivery/"
			# mediaUrl 	= "https://onetracky.com/pydelivery/"


	# except:
		# #src			= src.replace('https','http')
		# #mediaUrl	= mediaUrl.replace('https','http')
		# src			= "https://api.onetracky.com/cgi-bin/delivery/"
		# mediaUrl 	= "https://onetracky.com/pydelivery/"
		
		
	# print(os.environ['HTTPS'])
	# print(src)
	# sys.exit()
	

	cbString 	= hashlib.md5(str(randint(100, 999)).encode())
	cb			= cbString.hexdigest()
	cb			= cb[0:8]
	
	
	if banner['url']:
		if dfpClickUrl:
			clickurl					=dfpClickUrl;
		else:
			clickurl					=src+'core/ckvast.py?bannerid='+str(banner['bannerid'])+"&zoneid="+str(zoneid)+"&cb="+cb;
		
	else:
		clickurl					= src()+'core/ckvast.py?bannerid='+str(banner['bannerid'])+"&zoneid="+str(zoneid)+"&cb="+cb;
	
	player	 = "<a href='"+clickurl+"' target='_blank'";
	player	+="><img src='"+mediaUrl+"media/"+banner['filename']+"' width='"+str(banner['width'])+"' height='"+str(banner['height'])+"' /></a>";
	player	+="<img src='"+src+"core/lgimpr.py?bannerid="+str(banner['bannerid'])+"&zoneid="+str(zoneid)+"&cb="+cb+"' width='1' height='1' alt=''>";
	if	banner['tracking_pixel']:
		buster		= cb;
		trackingPixel = banner['tracking_pixel'].replace("{cache}", "buster");
		player	+="<img src='"+trackingPixel+"' width='1' height='1' alt=''>";

	#print(player)
	#sys.exit()
	return player;

	
	
def MAX_javascriptToHTML(string, varName, output = True, localScope = True):
	jsLines = []
	buffer	= ""
	
	string 		= string.replace("\\","\\\\")
	string 		= string.replace("\r",'')
	string 		= string.replace('"','\"')
	string 		= string.replace("'","\\'")
	string 		= string.replace('<','<"+"')
	
	
	lines 		= string.split("\n")
	
	
	for line in lines:
		if(line.strip() != '') :
			jsLines.append(varName + ' += "' + line.strip() + '\\n";')
		
	
	buffer	+= 'var ' if localScope else ''
	buffer	+= varName +" = '';\n"
	
	
	if(jsLines):
		buffer += jsLines[0]
	
	if (output == True):
		buffer += "\ndocument.write("+varName+");\n";
	return buffer;

print(renderad())

