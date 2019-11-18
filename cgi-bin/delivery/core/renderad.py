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
from random import randint


def renderad():
	d = parse_qs(os.environ['QUERY_STRING'])
	zoneid = d.get('zoneid',[''])[0]
	
	
	protocol			= ''
	dfpClickUrl			= ''
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
	
	
	#print(zonedata)
	
	renderdata		= bannerCode(bannerdata,zoneid,protocol,dfpClickUrl,ip,iframe)
	
	varString 	= 	hashlib.md5(str(randint(100, 999)).encode())
	var			= varString.hexdigest()
	var			= var[0:8]
	return MAX_javascriptToHTML(renderdata, 'MS_'+var)

	
	
def bannerCode(banner, zoneid, protocol, dfpClickUrl, ip,iframe):
	src			= "https://api.onetracky.com/cgi-bin/delivery/"
	mediaUrl 	= "http://onetracky.com/pydelivery/"
	parsed_uri 	= urlparse('https://stackoverflow.com/questions/1234567/blah-blah-blah-blah')
	

	if(parsed_uri.scheme == 'https'):
		src	= src.replace('https','http')
	

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

	
	return player;

	
	
def MAX_javascriptToHTML(string, varName, output = True, localScope = True):
	jsLines = []
	buffer	= ""
	
	
	string 		= string.replace("\\","\\\\")
	string 		= string.replace("\r",'')
	string 		= string.replace('"','\\"')
	string 		= string.replace("'","\\'")
	string 		= string.replace('<','<"+"')
	
	
	lines 		= string.split("\n")
	
	
	for line in lines:
		if(line.strip() != '') :
			jsLines.append(varName + ' += "' + line.strip() + '\\n";')
		
	
	buffer	+= 'var ' if localScope else ''
	buffer	+= varName +" = '';\n"

	
	buffer += jsLines[0]
	
	
	if (output == True):
		buffer += "\ndocument.write("+varName+");\n";

	return buffer;

print(renderad())

