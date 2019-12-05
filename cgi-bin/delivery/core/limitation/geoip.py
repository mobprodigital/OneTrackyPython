#!/Users/deel/AppData/Local/Programs/Python/Python37-32/python.exe
print('Content-type: text/html\r\n\r')
import geoip2.database
import sys
import cgitb
cgitb.enable()


################### ISP demo #################
reader 			= geoip2.database.Reader('C:/xampp/htdocs/django2adserver/delivery/core/limitation/GeoLite2-ASN.mmdb')
response 		= reader.asn('139.59.67.0')
print(response.autonomous_system_number)
print(response.autonomous_system_organization)
sys.exit()

################### City demo #################
reader 			= geoip2.database.Reader('C:/xampp/htdocs/django2adserver/delivery/core/limitation/GeoLite2-City.mmdb')
response 		= reader.city('103.240.192.249')
print(response.country.iso_code)
print(response.country.name)
#print(response.country.names['zh-CN'])

print(response.subdivisions.most_specific.name)
print(response.subdivisions.most_specific.iso_code)

print(response.city.name)
print(response.postal.code)
print(response.location.latitude)
print(response.location.longitude)
reader.close()


################### State demo #################
reader 		= geoip2.database.Reader('C:/xampp/htdocs/django2adserver/delivery/core/limitation/GeoLite2-City.mmdb')
response 		= reader.city('103.240.192.249')
print(response.country.iso_code)
print(response.country.name)
#print(response.country.names['zh-CN'])
print(response.subdivisions.most_specific.name)
print(response.subdivisions.most_specific.iso_code)
print(response.city.name)
print(response.postal.code)
print(response.location.latitude)
print(response.location.longitude)
reader.close()


################### Country demo #################
reader 		= geoip2.database.Reader('C:/xampp/htdocs/django2adserver/delivery/core/limitation/GeoLite2-Country.mmdb')
response 	= reader.country('103.240.192.249')
print(response.country.iso_code)
print(response.country.name)

reader.close()