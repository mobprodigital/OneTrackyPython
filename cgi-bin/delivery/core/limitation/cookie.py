#!/Users/deel/AppData/Local/Programs/Python/Python37-32/python.exe
import time

print("Content-type: text/html\r\nLocation: http://python.org/\r\n\r\n");

print ('Set-Cookie: lastvisit=' + str(time.time()));
print ("Set-Cookie:UserID = XYZ")
print ("Set-Cookie:Password = XYZ123")
print ("Set-Cookie:Expires = Tuesday, 31-Dec-2019 23:12:40 GMT")
print ("Set-Cookie:Domain = www.tutorialspoint.com")
print ("Set-Cookie:Path = /perl")

print('Content-type: text/html\r\n\r')
from cookies import Cookies, Cookie
from cookies import parse_date
import datetime
import os
print("Content-type: text/html\r\nLocation: http://python.org/\r\n\r\n");#working redirection


# cookies = Cookies(rocky='23')
# cookies['rocky'].value = "56"
# cookies['rocky'].path = "/"
# cookies['rocky'].expires = parse_date("Wed, 23-Jan-1992 00:01:02 GMT")


#cookies.render_request()
#cookies.render_response()
# print(cookies['rocky'].name);
# print(cookies['rocky'].value);
# print(cookies['rocky'].expires);
# print(cookies['rocky'].path);
#response 	= cookies.render_response
#print(os.environ)



    







