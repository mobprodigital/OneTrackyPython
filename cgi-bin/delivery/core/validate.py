#!/Users/deel/AppData/Local/Programs/Python/Python37-32/python.exe
import os
import sys
from user_agents import parse
import geoip2.database
import cgitb
cgitb.enable()
from state import getState
from city import getCity

def Max_checkClient_Domain(inputType, compOpt):
	
	HOST 					= os.environ['HTTP_HOST']
	try:
		key					= inputType.find(HOST)
		
		if(key != -1 and compOpt =='=~'):
			return True
		else:
			return False
			
	except Exception:
		return False
	
	
def Max_checkClient_IP(inputType, compOpt):
	IP 						= os.environ['REMOTE_ADDR']
	try:
		key					= inputType.find(IP)
		if(key != -1 and compOpt =='=~'):
			return True
		else:
			return False
			
	except Exception:
		return False
	


def Max_checkMobile_ISP(inputType, compOpt):
	ipaddress 			= os.environ["REMOTE_ADDR"]
	reader 				= geoip2.database.Reader('limitation/GeoLite2-ASN.mmdb')

	try:
		response 			= reader.asn(ipaddress)
		organisation		= response.autonomous_system_organization
		
		OA_Geo_ISP = {
			"Mahanagar Telephone Nigam Limited"					:"MTNL",
			"Reliance Jio Infocomm Limited"						:"JIO" ,
			"Vodafone Idea Ltd"									:"VODAFONE IDEA",
			"Vodafone India Ltd."								:"VODAFONE",
			"Idea Cellular Limited"								:"IDEA",
			"Bharti Airtel Limited"								:"AIRTEL" ,
			"National Internet Backbone"						:"BSNL" ,
			"TATA Communications formerly VSNL is Leading ISP"	:"TATA DOCOMO"
		}
		
		ISPCode				= OA_Geo_ISP.get(organisation)
		key					= inputType.find(ISPCode)
		if(key != -1 and compOpt =='=~'):
			return True
		else:
			return False
			
	except Exception:
		return False
	finally:
		reader.close()

def Max_checkGeo_City(inputType, compOpt):
	GeoArr  			= inputType.split(',')
	countryCode			= GeoArr[0]
	stateCode			= GeoArr[1]
	del GeoArr[0]
	del GeoArr[0]
	
	
	ipaddress 			= os.environ["REMOTE_ADDR"]
	#ipaddress			='103.77.229.62'
	# print(ipaddress)
	# sys.exit()
	reader 				= geoip2.database.Reader('limitation/GeoLite2-City.mmdb')
	try:
		response 				= reader.city(ipaddress)
		userCountryCode			= response.country.iso_code
		
		
		userStateCode			= response.subdivisions.most_specific.iso_code
		stateName				= response.subdivisions.most_specific.name
		
		stateNumCode			= getState(userCountryCode,stateName)
		
		cityName				= response.city.name
		# print(cityName)
		# print(stateName)
		
		city					= getCity(stateName,cityName)
		
		#print(city)
		#sys.exit()
		
		
		
		
		
		if(countryCode	== userCountryCode):

			if(userStateCode):
				
				if(stateCode	== stateNumCode):
					
					
					if(city):
						
						if(stateNumCode and GeoArr.count(str(city)) > 0):
							
							return True
						else:
							return False
					else:
						return True
				else:
					return False
			else:
				return True
		else:
			return False
					
	except Exception:
		
		return False
	finally:
		reader.close()

def Max_checkGeo_Region(inputType, compOpt):
	GeoArr  				= inputType.split(',')
	countryCode				= GeoArr[0]
	del GeoArr[0]
	


	ipaddress 			= os.environ["REMOTE_ADDR"]
	#ipaddress			= '169.149.12.64'
	# print(ipaddress)
	# sys.exit() 	
	reader 				= geoip2.database.Reader('limitation/GeoLite2-City.mmdb')
	try:
		response 				= reader.city(ipaddress)
		userCountryCode			= response.country.iso_code
		stateCode				= response.subdivisions.most_specific.iso_code
		state					= response.subdivisions.most_specific.name
		stateNumCode			= getState(userCountryCode,state)
	
		if(countryCode	== userCountryCode):
			if(stateNumCode and GeoArr.count(stateNumCode) > 0):
				return True
			else:
				return False
			return True
		else:
			return False
		return True
				
	except Exception:
		return False
	finally:
		reader.close()


def Max_checkGeo_Country(inputType, compOpt):
	ipaddress 			= os.environ["REMOTE_ADDR"]
	
	
	
	reader 				= geoip2.database.Reader('limitation/GeoLite2-Country.mmdb')
	#reader 			= geoip2.database.Reader('C:/xampp/htdocs/django2adserver/delivery/core/limitation/GeoLite2-Country.mmdb')

	try:
		response 			= reader.country(ipaddress)
		
		countryCode			= response.country.iso_code
		
		key					= inputType.find(countryCode)
		# print(ipaddress)
		# print(countryCode)
		# sys.exit()
		if(key != -1 and compOpt =='=~'):
			return True
		else:
			return False
			
	except Exception:
		return False
	finally:
		reader.close()

	
	
def Max_checkDevice_Screen(inputType, compOpt):
	user_agent 	= os.environ["HTTP_USER_AGENT"]
	user_agent 	= parse(user_agent)
	screenType		= ''
	if (user_agent.is_mobile):
		screenType 	= 'mobile'
		
	elif(user_agent.is_tablet):
			screenType 	= 'tablet'

	elif(user_agent.is_pc):
		 screenType 	=  'desktop'
	
	#print(screenType)
	#sys.exit()
	key		= inputType.find(screenType)
	if(key != -1 and compOpt =='=~'):
		return True
	else:
		return False


def Max_checkClient_Os(inputType, compOpt):
	aOsMap = {
		"WINDOWS" : {
		  "95" : "95",
		  "98" : "98",
		  "2000" : "2k",
		  "XP" : "xp",
		  "7" : "w7",
		  "8" : "w8",
		  "10": "w10"
		},
		"OSX" : "osx",
		"LINUX" : "linux",
		"FREEBSD" : "freebsd",
		"SUNOS" : "sun"
	}
	
	
	user_agent 			= os.environ["HTTP_USER_AGENT"]
	user_agent 			= parse(user_agent)
	oSystem				= user_agent.os.family
	oSystem				= oSystem.upper()
	
	osSym				= ''
	if (aOsMap[oSystem]):
		if (isinstance(aOsMap[oSystem],dict)):
			oVersion		= user_agent.os.version_string
			if (aOsMap[oSystem][oVersion]):
				osSym	= aOsMap[oSystem][oVersion]
		else:
			osSym 		= aOsMap[oSystem]
	else:
		osSym 		= 'Unknown'
	
	key		= inputType.find(osSym)
	if(key != -1 and compOpt =='=~'):
		return True
	else:
		return False

def Max_checkClient_Browser(inputType, compOpt):

	aBrowserMap = {
		"EDGE" : "ED",
		"IE" : "IE",
		"CHROME" : "GC",
		"FIREFOX" : "FX",
		"OPERA" : "OP",
		"OPERA_MINI" : "OP",
		"BLACKBERRY" : "BL",
		"NAVIGATOR" : "NS",
		"GALEON" : "GA",
		"PHOENIX" : "PX",
		"FIREBIRD" : "FB",
		"SAFARI" : "SF",
		"MOZILLA" : "MZ",
		"KONQUEROR" : "KQ",
		"ICAB" : "IC",
		"LYNX" : "LX",
		"AMAYA" : "AM",
		"OMNIWEB" : "OW"
	}
	

	user_agent 			= os.environ["HTTP_USER_AGENT"]
	user_agent 			= parse(user_agent)
	browser				= user_agent.browser.family
	mobileKey			= browser.find('Mobile')
	if(mobileKey != -1):
		browser			= browser.replace('Mobile','')
		browser			= browser.strip()
	
	
	#print(browser)
	#sys.exit()
	browserName			= browser.upper()
	browserSym			= ''
	if (aBrowserMap[browserName]):
	   browserSym		= aBrowserMap[browserName]
	
	key		= inputType.find(browserSym)
	if(key != -1 and compOpt =='=~'):
		return True
	else:
		return False
		
		
