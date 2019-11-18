from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
import datetime
from enumchoicefield import ChoiceEnum, EnumChoiceField


# class Banners(models.Model):
# 	bannerid 			= models.AutoField(primary_key=True)
# 	agencyid 			= models.IntegerField(default=0)
	
# class Fruit(ChoiceEnum):
#     apple = "Apple"
#     banana = "Banana"
#     orange = "Orange"

# class Profile(models.Model):
# 	name = models.CharField(max_length=100)
# 	favourite_fruit = EnumChoiceField(Fruit, default=Fruit.banana)

class Status(ChoiceEnum):
	t = 'true'
	f = 'false'
	
# class StatusChoice(ChoiceEnum):
	# '0' = '0'
	# '1' = '1'
	
class Clients(models.Model):
	clientid 			= models.AutoField(primary_key = True)
	#userid 			= models.IntegerField(null = True)
	userid 				= models.IntegerField(default=0,blank=False)

	agencyid 			= models.IntegerField(default = 0,blank=False)
	clientname 			= models.CharField(max_length=255,default='',blank=False)
	contact 			= models.CharField(max_length=255, blank=False)
	email 				= models.CharField(max_length=64, default='',blank=False)
	comments 			= models.TextField(blank=True,null=True)
	
	reportinterval 		= models.IntegerField(default=7,blank=True,null=True)
	#reportlastdate 	= models.DateField(default='2019-09-09')
	#updated 			= models.DateTimeField(default='2019-09-09 ')
	advertiser_limitation =  models.IntegerField(default=0,blank=True,null=True)
	type 				= models.IntegerField(default=0,blank=True,null=True)

	reportdeactivate 	= EnumChoiceField(Status, 	default=Status.t,blank=True,null=True)
	report 				= EnumChoiceField(Status, 	default=Status.t,blank=True,null=True)
	#status 			= EnumChoiceField(StatusChoice, default=StatusChoice.0)

class Campaigns(models.Model):
	campaignid 		             = models.AutoField(primary_key=True)
	#clientid           		 = models.ForeignKey(Clients, on_delete=models.CASCADE, null=True, blank=True)
	clientid					 = models.IntegerField(default=0,blank=False) 

	campaignname       	     	 = models.CharField(max_length=255,default='',blank=False)
	currency       	     	     = models.CharField(max_length=255,default='',blank=True,null=True)
	campaign_type                = models.IntegerField(default='0',blank=True,null=True)
	views                        = models.IntegerField(default='-1',blank=True,null=True)
	clicks                       = models.IntegerField(default='-1',blank=True,null=True)
	conversions                  = models.IntegerField(default='-1',blank=True,null=True)
	priority                     = models.IntegerField(default='0',blank=True,null=True)
	weight                       = models.IntegerField(default='1',blank=True,null=True)
	target_impression            = models.IntegerField(default='0',blank=True,null=True)
	target_click                 = models.IntegerField(default='0',blank=True,null=True)
	target_conversion            = models.IntegerField(default='0',blank=True,null=True)
	companion                    = models.IntegerField(default='1',blank=True,null=True)
	comments       		         = models.TextField(max_length=255,default='',blank=True,null=True)
	revenue                      = models.IntegerField(default='0',blank=True,null=True)
	revenue_type                 = models.IntegerField(default='0',blank=True,null=True)
	updated                      = models.DateTimeField(auto_now_add=True,blank=True,null=True)
	block                        = models.IntegerField(default='0',blank=True,null=True)
	capping                      = models.IntegerField(default='0',blank=True,null=True)
	session_capping              = models.IntegerField(default='0',blank=True,null=True)
	capping_amount               = models.IntegerField(default='0',blank=True,null=True)
	capping_period_value         = models.IntegerField(default='0',blank=True,null=True)
	capping_period_type          = models.CharField(max_length=255,blank=True,null=True)
	status                       = models.IntegerField(default='1',blank=True,null=True)
	hosted_views                 = models.IntegerField(default='0',blank=True,null=True)
	hosted_clicks                = models.IntegerField(default='0',blank=True,null=True)
	viewwindow                   = models.IntegerField(default='0',blank=True,null=True)
	clickwindow                  = models.IntegerField(default='0',blank=True,null=True)
	ecpm                         = models.FloatField(default='0',blank=True,null=True)
	expire_time                  = models.DateField(blank=True,null=True)
	activate_time                = models.DateField(blank=True,null=True)

	min_impressions              = models.IntegerField(default='0',blank=True,null=True)
	ecpm_enabled                 = models.IntegerField(default='0',blank=True,null=True)
	type                         = models.IntegerField(default='0',blank=True,null=True)
	show_capped_no_cookie        = models.IntegerField(default='0',blank=True,null=True)
	tracking_type                = models.CharField(max_length=255,default='',blank=True,null=True)	

class Banners(models.Model):
	bannerid           =  models.AutoField(primary_key=True)
	#campaignid         = models.ForeignKey(Campaigns, on_delete=models.CASCADE, null=True, blank=True)
	campaignid         = models.IntegerField(default=0,blank=False)
	contenttype        = models.CharField(choices=(
	('gif','gif'),
	('jpeg','jpeg'),
	('png','png'),
	('html','html'),
	('swf','swf'),
	('dcr','dcr'),
	('rpm','rpm'),
	('mov','mov'),
	('txt','txt'),
	('exscrpt','exscrpt'),
	('html5','html5')
	),max_length=10)
	storagetype        = models.CharField(choices=(
	('sql','sql'),
	('web','web'),
	('url','url'),
	('html','html'),
	('html5','html5')
	
	),max_length=10,default='sql')
	pluginversion      = models.IntegerField(default=0)
	filename           = models.CharField(max_length=255,blank=True,null=True)
	filename2          = models.CharField(max_length=255,blank=True,null=True)
	imageurl           = models.CharField(max_length=255,blank=True,null=True)
	url           		= models.CharField(max_length=255, null=True)

	htmltemplate       = models.CharField(max_length=255,blank=True,null=True)
	rich_media_type    = models.IntegerField(default=0,blank=True,null=True)
	htmlcache          = models.CharField(max_length=255,blank=True,null=True)
	width              = models.IntegerField(default=0,blank=True,null=True)
	height             = models.IntegerField(default=0,blank=True,null=True)
	weight             = models.IntegerField(default=1,blank=True,null=True)
	seq                = models.IntegerField(default=0,blank=True,null=True)
	target             = models.CharField(max_length=255,blank=True,null=True)
	tracking_pixel     = models.CharField(max_length=255,blank=True,null=True)
	url_text           = models.TextField(max_length=255,blank=True,null=True)
	alt                = models.CharField(max_length=255,blank=True,null=True)
	statustext         = models.CharField(max_length=255,blank=True,null=True)
	bannertext         = models.CharField(max_length=255,blank=True,null=True)
	description        = models.CharField(max_length=255,blank=True,null=True)
	adserver           = models.CharField(max_length=255,blank=True,null=True)
	block              = models.IntegerField(default=0,blank=True,null=True)
	capping            = models.IntegerField(default=0,blank=True,null=True)
	session_capping    = models.IntegerField(default=0,blank=True,null=True)
	compiledlimitation = models.CharField(max_length=255,blank=True,null=True)
	acl_plugins        = models.CharField(max_length=255,blank=True,null=True)
	append             = models.CharField(max_length=255,blank=True,null=True)
	bannertype         = models.IntegerField(default=0,blank=True,null=True)
	alt_filename       = models.CharField(max_length=255,blank=True,null=True)
	alt_imageurl       = models.CharField(max_length=255,blank=True,null=True)
	#alt_contenttype alt_contenttypes NOT NULL DEFAULT 'gif'::alt_contenttypes,
	comments           = models.CharField(max_length=255,blank=True,null=True) 
	updated            = models.DateTimeField(auto_now_add=True)
	acls_updated       = models.DateTimeField(auto_now_add=True)
	keyword            = models.CharField(max_length=255,blank=True,null=True)
	transparent        = models.IntegerField(default=0)
	parameters         = models.CharField(max_length=255,blank=True,null=True)
	status             = models.IntegerField(default=0,blank=True,null=True)
	ext_bannertype     = models.CharField(max_length=255,blank=True,null=True)
	prepend            = models.CharField(max_length=255,blank=True,null=True)
	iframe_friendly    = models.IntegerField(default=1)
	extag              = models.CharField(max_length=255,blank=True,null=True) 
	multiple_banner_existence = models.CharField(max_length=255,blank=True,null=True)
	#bannerid bigint NOT NULL DEFAULT nextval('banners_bannerid_seq'::regclass),
		
	
class rv_data_summary_ad_hourly(models.Model):
	data_summary_ad_hourly_id 	= models.AutoField(primary_key = True)
	date_time					= models.DateTimeField()
	ad_id 						= models.IntegerField(default=0,null=True)
	#creative_id 				= models.ForeignKey(Banners, on_delete=models.CASCADE, null=True, blank=True)
	creative_id 				= models.IntegerField()
	zone_id 					= models.IntegerField()
	
	requests 					= models.IntegerField(default=0)
	impressions 				= models.IntegerField(default=0,blank=True)
	clicks 						= models.IntegerField(default=0,blank=True)
	conversions 				= models.IntegerField(default=0,blank=True,null=True)
	
	total_basket_value 			= models.DecimalField(max_digits=20,decimal_places=2, default=0.0,null=True)
	total_num_items 			= models.IntegerField(null = True, default=0)
	total_revenue 				= models.DecimalField(max_digits=20, decimal_places=2,null=True, default=0.0)
	total_cost 					= models.DecimalField(max_digits=20, decimal_places=2,null=True, default=0.0)
	total_techcost 				= models.DecimalField(max_digits=20, decimal_places=2,null=True, default=0.0)
	updated 					= models.DateTimeField(auto_now_add=True,null=True)
	
	
	
class rv_stats_vast(models.Model):
	data_summary_ad_hourly_id 	= models.AutoField(primary_key = True)
	interval_start 				= models.DateTimeField()
	creative_id 				= models.IntegerField()
	zone_id 					= models.IntegerField()
	vast_event_id 				= models.IntegerField()
	count 						= models.IntegerField(default =0)
	
class rv_ad_zone_assoc(models.Model):
	ad_zone_assoc_id 	= models.AutoField(primary_key = True)
	zone_id 			= models.IntegerField(null=True,default='null')
	ad_id 				= models.IntegerField(null=True,default='null')
	priority 			= models.DecimalField(max_digits=20,decimal_places=2,null=True, default=0)
	link_type			= models.IntegerField(default=1,null=True)
	priority_factor 	= models.DecimalField(max_digits=20,decimal_places=2,null=True, default=0)
	to_be_delivered		= models.IntegerField(default=1,null=True)
	date_updated 		= models.DateTimeField(auto_now_add=True,null=True)
	
class banner_vast_element(models.Model):
	banner_vast_element_id 	= models.AutoField(primary_key = True)
	banner_id 				= models.IntegerField()
	status 					= models.CharField(max_length=255,default='active')
	vast_element_type 		= models.CharField(max_length=16,null=True,default='')
	vast_video_id 			= models.CharField(max_length=100,null=True,default='')
	
	content_video 			= models.IntegerField(null=True,blank=True),
	skip 					= models.IntegerField(blank=True,null=True)
	skip_time 				= models.IntegerField(blank=True,null=True)
	mute 					= models.IntegerField(blank=True,null=True)
	autoplay 				= models.IntegerField(blank=True,null=True)
	impression_pixel 		= models.CharField(max_length=255,blank=True,null=True)
	start_pixel 			= models.CharField(max_length=255,blank=True,null=True)
	quater_pixel 			= models.CharField(max_length=255,blank=True,null=True)
	mid_pixel 				= models.CharField(max_length=255,blank=True,null=True)
	third_quater_pixel 		= models.CharField(max_length=255,blank=True,null=True)
	end_pixel 				= models.CharField(max_length=255,blank=True,null=True)
	third_party_click 		= models.CharField(max_length=255,blank=True,null=True)
	creative_view 			= models.CharField(max_length=255,blank=True,null=True)
	vast_tag 				= models.TextField(blank=True,null=True)
	vast_video_duration 	= models.IntegerField(blank=True,null=True)
	vast_video_delivery 	= models.CharField(max_length=20,blank=True,null=True)
	vast_video_type 		= models.CharField(max_length=20,blank=True,null=True)
	vast_video_bitrate 		= models.CharField(max_length=20,null=True,default='')
	vast_video_height 		= models.IntegerField(blank=True,null=True)
	vast_video_width 		= models.IntegerField(blank=True,null=True)
	vast_video_outgoing_filename = models.TextField(blank=True,null=True)
	vast_companion_banner_id 	= models.IntegerField(blank=True,null=True)
	vast_overlay_height 		= models.IntegerField(blank=True,null=True)
	vast_overlay_width 			= models.IntegerField(blank=True,null=True)
	vast_video_clickthrough_url = models.TextField(blank=True,null=True)
	vast_overlay_action 		= models.CharField(max_length=20,null=True,default='')
	vast_overlay_format 		= models.CharField(max_length=20,null=True,default='')
	vast_overlay_text_title 	= models.TextField(blank=True,null=True)
	vast_overlay_text_description	= models.TextField(blank=True,null=True)
	vast_overlay_text_call 		= models.TextField(blank=True,null=True)
	vast_creative_type 			= models.CharField(max_length=20,null=True,default='')
	vast_thirdparty_impression 	= models.TextField(blank=True,null=True)
	vast_thirdparty_erorr		= models.TextField(blank=True,null=True)


class Affiliates(models.Model):
	affiliateid 		= models.AutoField(primary_key=True)
	agencyid 			= models.IntegerField(default=0,blank=False)
	name 				= models.CharField(max_length=255,default='',blank=False)
	mnemonic 			= models.CharField(max_length=5,default='',blank=True,null=True)
	comments 			= models.TextField(blank=True,null=True)
	contact 			= models.CharField(max_length=255,blank=True,null=True)
	email 				= models.CharField(max_length=64, default='',blank=False)
	website 			= models.CharField(max_length=255,blank=False)
	updated 			= models.DateTimeField(auto_now_add=True)
	oac_country_code 	= models.CharField(max_length=2,default='',blank=False)
	oac_language_id 	= models.IntegerField(blank=True,null=True)
	oac_category_id 	= models.IntegerField(blank=True,null=True)
	userid 				= models.IntegerField(default=0,blank=False)






class Countries(models.Model):
	countries_id 		= models.AutoField(primary_key=True)
	countries_name 		= models.CharField(max_length=5,default='')
	countries_iso_code 	= models.CharField(max_length=5,default='')

class Currency(models.Model):
	countries_id 		= models.AutoField(primary_key=True)
	currency_name 		= models.CharField(max_length=255,default='')
	currency_symbol 	= models.CharField(max_length=255,default='')

class Device_type(models.Model):
	creative_id 		= models.IntegerField(default=0)
	type 		        = models.CharField(max_length=255,default='')
	
class Notifications(models.Model):
	id 		            = models.AutoField(primary_key=True)
	client_id 		    = models.IntegerField(default=0)
	status       		= models.CharField(max_length=255,default='')
	currency_symbol 	= models.CharField(max_length=255,default='')

class User_roles(models.Model):
	role_id 		    = models.AutoField(primary_key=True)
	rolename       		= models.CharField(max_length=255,default='')
	created_date        = models.DateTimeField(auto_now_add=True)

class Zones(models.Model):
	zoneid 		        = models.AutoField(primary_key=True)
	affiliateid 		= models.IntegerField(default=0,blank=False)
	zonename       		= models.CharField(max_length=255,default='',blank=False)
	description       	= models.CharField(max_length=255,default='',blank=True,null=True)
	delivery       		= models.CharField(max_length=255,default='',blank=True,null=True)
	zonetype       		= models.CharField(max_length=255,default='',blank=True,null=True)
	size_flag       	= models.IntegerField(default=0,blank=True,null=True)
	category       		= models.CharField(max_length=255,default='',blank=True,null=True)
	width       		= models.IntegerField(default=0,blank=True,null=True)
	height       		= models.IntegerField(default=0,blank=True,null=True)
	ad_selection       	= models.CharField(max_length=255,default='',blank=True,null=True)
	chain       		= models.CharField(max_length=255,default='',blank=True,null=True)
	prepend       		= models.CharField(max_length=255,default='',blank=True,null=True)
	append       		= models.CharField(max_length=255,default='',blank=True,null=True)
	appendtype       	= models.CharField(max_length=255,default='',blank=True,null=True)
	inventory_forecast_type= models.IntegerField(default=0,blank=True,null=True)
	comments       		= models.CharField(max_length=255,default='',blank=True,null=True)
	cost       		    = models.IntegerField(default=0,blank=True,null=True)
	cost_type       	= models.IntegerField(default=0,blank=True,null=True)
	cost_variable_id    = models.CharField(max_length=255,default='',blank=True,null=True)
	technology_cost       = models.IntegerField(default=0,blank=True,null=True)
	technology_cost_type  = models.IntegerField(default=0,blank=True,null=True)
	updated               = models.DateTimeField(auto_now_add=True)
	block       	      = models.IntegerField(default=0,blank=True,null=True)
	capping       	      = models.IntegerField(default=0,blank=True,null=True)
	session_capping       = models.IntegerField(default=0,blank=True,null=True)
	what                  = models.IntegerField(default=0,blank=True,null=True)
	rate       	          = models.IntegerField(default=0,blank=True,null=True)
	pricing       	      = models.CharField(max_length=255,default='',blank=True,null=True)
	oac_category_id       = models.IntegerField(default=0,blank=True,null=True)
	ext_adselection       = models.CharField(max_length=255,default='',blank=True,null=True)
	show_capped_no_cookie = models.IntegerField(default=0,blank=True,null=True)
	forceappendd          = models.IntegerField(default=0,blank=True,null=True)
	created_date          = models.DateTimeField(auto_now_add=True)        


class Mailer(models.Model):
	id 		                = models.AutoField(primary_key=True)
	campaign       	    	= models.CharField(max_length=255,default='')
	subject       	     	= models.CharField(max_length=255,default='')
	body       		        = models.CharField(max_length=255,default='')
	mailinglist       		= models.CharField(max_length=255,default='')
	description       		= models.CharField(max_length=255,default='')
	status       		    = models.IntegerField(default=0)
	activation_date         = models.DateTimeField(auto_now_add=True)
	expiration_date         = models.DateTimeField(auto_now_add=True)        


# class Targeting(models.Model):
	# targetid 		                = models.AutoField(primary_key=True)
	# campaignid       	    	= models.CharField(max_length=255,default='')
	# type       	     	= models.CharField(max_length=255,default='')
	# browsername       		        = models.CharField(max_length=255,default='')
	# mobiletype       		= models.CharField(max_length=255,default='')
	# countryid       		    = models.IntegerField(default=0)
	# stateid       		    = models.IntegerField(default=0)
	# cityid       		    = models.IntegerField(default=0)
	# datecreated         = models.DateTimeField(auto_now_add=True)
	# dateupdated         = models.DateTimeField(auto_now_add=True)


# class Targeting(models.Model):
# 	id 		                = models.AutoField(primary_key=True)
# 	title       	    	= models.CharField(max_length=255,default='')
# 	name       	     	    = models.CharField(max_length=255,default='')
# 	source       		    = models.CharField(max_length=255,default='')
# 	user_id       		    = models.IntegerField(default=0)
# 	status       		    = models.IntegerField(default=0)      

class Video_ad_request(models.Model):
	id 		                = models.AutoField(primary_key=True)
	client_ip       	    = models.CharField(max_length=255,default='')
	domain       		    = models.CharField(max_length=255,default='')
	bannerid       		    = models.IntegerField(default=0)
	datetime                = models.DateTimeField(auto_now_add=True)


class Client_access(models.Model):
	associd 		        = models.AutoField(primary_key=True)
	userid       	     	= models.IntegerField(default=0)
	clientid       		    = models.IntegerField(default=0)

class Publisher_access(models.Model):
	associd 		        = models.AutoField(primary_key=True)
	userid       	     	= models.IntegerField(default=0)
	affiliateid       		= models.IntegerField(default=0)

class User_assoc(models.Model):
	associd 		        = models.AutoField(primary_key=True)
	child_id       	     	= models.IntegerField(default=0)
	parent_id       		= models.IntegerField(default=0)

class Email(models.Model):
	id 		                    = models.AutoField(primary_key=True)
	email       	     	    = models.CharField(max_length=255,default='')
	subject       		        = models.CharField(max_length=255,default='')
	message       		        = models.CharField(max_length=255,default='')
	sender_id       		    = models.IntegerField(default=0)
	
class Link(models.Model):
	id 		                    = models.AutoField(primary_key=True)
	link       	     	        = models.CharField(max_length=255,default='')
			


class Location(models.Model):
	location_id 		        = models.AutoField(primary_key=True)
	name       	     	        = models.CharField(max_length=255,default='')
	location_type       		= models.IntegerField(default=0)
	parent_id       		    = models.IntegerField(default=0)
	is_visible       		    = models.IntegerField(default=0)

class Invocation(models.Model):
	tagid 		                = models.AutoField(primary_key=True)
	tagtype       	            = models.CharField(max_length=255,default='')
	code       		            = models.CharField(max_length=255,default='')

class Channel(models.Model):
	channelid 		            = models.AutoField(primary_key=True)
	agencyid       		        = models.IntegerField(default=0)
	affiliateid       		    = models.IntegerField(default=0)
	name       	     	        = models.CharField(max_length=255,default='')
	description       		    = models.CharField(max_length=255,default='')
	compiledlimitation       	= models.TextField(max_length=255,default='')
	comments       		        = models.TextField(max_length=255,default='')
	acl_plugins       		    = models.TextField(max_length=255,default='')
	updated                     = models.DateTimeField(auto_now_add=True)
	acl_updated                 = models.DateTimeField(auto_now_add=True)

class Ci_sessions(models.Model):
	session_id 		                = models.AutoField(primary_key=True)
	ip_address       	     	    = models.CharField(max_length=255,default='')
	user_agent       		        = models.CharField(max_length=255,default='')
	last_activity           		= models.IntegerField(default=0)
	user_data       		        = models.TextField(max_length=255,default='')
class Uploads(models.Model):
	id 		                        = models.AutoField(primary_key=True)
	title       	     	        = models.CharField(max_length=255,default='')
	name       		                = models.CharField(max_length=255,default='')
	source       		            = models.CharField(max_length=255,default='')
	user_id           		        = models.IntegerField(default=0)
	status           		        = models.IntegerField(default=0)




class Users(models.Model):
	status        = models.CharField(choices=(
	('0','0'),
	('1','1')
	),max_length=10,default='1')
	user_id 		             = models.AutoField(primary_key=True)
	username       	     	     = models.CharField(max_length=255,default='')
	password       	     	     = models.CharField(max_length=255,default='')
	firstname       	     	 = models.CharField(max_length=255,default='')
	lastname       	     	     = models.CharField(max_length=255,default='')
	skype       	     	     = models.CharField(max_length=255,default='',null=True,blank=True)
	email 						 = models.CharField(max_length=255,default='')

	company       	     	     = models.CharField(max_length=255,default='',null=True,blank=True)
	currency       	     	     = models.CharField(max_length=255,default='',null=True,blank=True)
	role       	     	         = models.IntegerField(default=1)
	user_type       			 = models.IntegerField(null=True,blank=True)
	change_passwordStatus        = models.IntegerField(default=0,null=True,blank=True)
	phone           		     = models.CharField(max_length=255,default='',null=True,blank=True)
	date_created                 = models.DateTimeField(auto_now_add=True,null=True,blank=True)
	date_updated                 = models.DateTimeField(auto_now_add=True,null=True,blank=True)
	date_last_login              = models.DateTimeField(auto_now_add=True,null=True,blank=True)
	
	
class LoginToken(models.Model):
	token_id 			= models.AutoField(primary_key = True)
	user_id		 		= models.IntegerField()
	token				= models.CharField(max_length=255)
	created_date 		= models.DateTimeField(auto_now_add=True,null=True)
	

	
	
	
	
	


 
	
	

	
	
			
	 




	
