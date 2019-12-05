#!/Users/deel/AppData/Local/Programs/Python/Python37-32/python.exe
print('Content-type: text/html\r\n\r')

from user_agents import parse
import os
user_agent = os.environ["HTTP_USER_AGENT"]
ip = os.environ["REMOTE_ADDR"]

print(user_agent)
user_agent = parse(user_agent)
print(user_agent.is_mobile) # returns True
print(user_agent.is_tablet) # returns False
print(user_agent.is_pc) # returns False
print(str(user_agent)) # returns "BlackBerry 9700 / BlackBerry OS 5 / BlackBerry 9700"

# Accessing user agent's browser attributes
print(user_agent.browser)  # returns Browser(family=u'Mobile Safari', version=(5, 1), version_string='5.1')
print(user_agent.browser.family)  # returns 'Mobile Safari'
print(user_agent.browser.version)  # returns (5, 1)
print(user_agent.browser.version_string)   # returns '5.1'

# Accessing user agent's operating system properties
print(user_agent.os)  # returns OperatingSystem(family=u'iOS', version=(5, 1), version_string='5.1')
print(user_agent.os.family)  # returns 'iOS'
print(user_agent.os.version)  # returns (5, 1)
print(user_agent.os.version_string)  # returns '5.1'

# Accessing user agent's device properties
print(user_agent.device)  # returns Device(family=u'iPhone', brand=u'Apple', model=u'iPhone')
print(user_agent.device.family)  # returns 'iPhone'
print(user_agent.device.brand) # returns 'Apple'
print(user_agent.device.model) # returns 'iPhone'

# Let's start from an old, non touch Blackberry device
ua_string = 'BlackBerry9700/5.0.0.862 Profile/MIDP-2.1 Configuration/CLDC-1.1 VendorID/331 UNTRUSTED/1.0 3gpp-gba'
user_agent = parse(ua_string)
user_agent.is_mobile # returns True
user_agent.is_tablet # returns False
user_agent.is_touch_capable # returns False
user_agent.is_pc # returns False
user_agent.is_bot # returns False
#print(str(user_agent)) # returns "BlackBerry 9700 / BlackBerry OS 5 / BlackBerry 9700"

# Now a Samsung Galaxy S3
ua_string = 'Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'
user_agent = parse(ua_string)
user_agent.is_mobile # returns True
user_agent.is_tablet # returns False
user_agent.is_touch_capable # returns True
user_agent.is_pc # returns False
user_agent.is_bot # returns False
#print(str(user_agent)) # returns "Samsung GT-I9300 / Android 4.0.4 / Android 4.0.4"

# iPad's user agent string
ua_string = 'Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10'
user_agent = parse(ua_string)
user_agent.is_mobile # returns False
user_agent.is_tablet # returns True
user_agent.is_touch_capable # returns True
user_agent.is_pc # returns False
user_agent.is_bot # returns False
#print(str(user_agent)) # returns "iPad / iOS 3.2 / Mobile Safari 4.0.4"

# Kindle Fire's user agent string
ua_string = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_3; en-us; Silk/1.1.0-80) AppleWebKit/533.16 (KHTML, like Gecko) Version/5.0 Safari/533.16 Silk-Accelerated=true'
user_agent = parse(ua_string)
user_agent.is_mobile # returns False
user_agent.is_tablet # returns True
user_agent.is_touch_capable # returns True
user_agent.is_pc # returns False
user_agent.is_bot # returns False
#print(str(user_agent)) # returns "Kindle / Android / Amazon Silk 1.1.0-80"

# Touch capable Windows 8 device
ua_string = 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0; Touch)'
user_agent = parse(ua_string)
user_agent.is_mobile # returns False
user_agent.is_tablet # returns False
user_agent.is_touch_capable # returns True
user_agent.is_pc # returns True
user_agent.is_bot # returns False
#print(str(user_agent)) # returns "PC / Windows 8 / IE 10"




# from device_detector import DeviceDetector
# import os


# ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'

# device = DeviceDetector(ua).parse()


# device.is_bot()      # >>> False

# device.os_name()     # >>> Android
# device.os_version()  # >>> 4.3
# device.engine()      # >>> WebKit

# device.device_brand_name()  # >>> Sony
# device.device_brand()       # >>> SO
# device.device_model()       # >>> Xperia ZR
# device.device_type()        # >>> smartphone


# from device_detector import SoftwareDetector

# ua = 'Mozilla/5.0 (Linux; Android 6.0; 4Good Light A103 Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.83 Mobile Safari/537.36'
# device = SoftwareDetector(ua).parse()

# print(device.client_name())        # >>> Chrome Mobile
# device.client_short_name()  # >>> CM
# device.client_type()        # >>> browser
# device.client_version()     # >>> 58.0.3029.83

# print(device.os_name())     # >>> Android
# device.os_version()  # >>> 6.0
# device.engine()      # >>> WebKit

# print(device.device_brand_name())  # >>> ''
# device.device_brand()       # >>> ''
# device.device_model()       # >>> ''
# device.device_type()        # >>> ''

# ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16D57 EtsyInc/5.22 rv:52200.62.0'
# device = DeviceDetector(ua).parse()

# device.secondary_client_name()     # >>> EtsyInc
# device.secondary_client_type()     # >>> generic
# device.secondary_client_version()  # >>> 5.22