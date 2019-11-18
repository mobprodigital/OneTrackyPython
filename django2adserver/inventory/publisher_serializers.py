from rest_framework import serializers
from inventory.models import Clients
from inventory.models import Campaigns
from inventory.models import Banners
from inventory.models import Zones
from inventory.models import Affiliates
from inventory.models import Users,LoginToken
from inventory.models import User_assoc
from datetime import datetime

# class Clients(object):
	# def __init__(self, clientname, contact, email, comments):
		# self.clientname = clientname
		# self.contact = contact
		# self.email = email
		# self.comments = comments

class ClientsSerializer(serializers.ModelSerializer):
	# clientname 				= serializers.SerializerMethodField('clientname')
	# contact 				= serializers.SerializerMethodField('contact')
	# email 					= serializers.SerializerMethodField('email')
	# comments 				= serializers.SerializerMethodField('comments')
	# reportinterval 		= serializers.SerializerMethodField('reportinterval')
	# reportlastdate 		= serializers.DateField(default= '0000-00-00')
	# updated 				= serializers.SerializerMethodField('update'),
	# advertiser_limitation =  serializers.IntegerField(default=0)
	# type 				= serializers.IntegerField(default=0)

	# reportdeactivate 	= serializers.EnumChoiceField(Status,default=Status.t)
	# report 				= serializers.EnumChoiceField(Status,default=Status.t)
	
	# def create(self, validated_data):
		# return Clients.objects.create(**validated_data)
	# def update(self, instance, validated_data):
		# instance.clientname 	= validated_data.get('clientname', instance.clientname)
		# instance.contact		= validated_data.get('contact', instance.contact)
		# instance.email 			= validated_data.get('email', instance.email)
		# instance.comments		= validated_data.get('comments', instance.comments)
		# instance.reportinterval = validated_data.get('reportinterval', instance.reportinterval)
		# instance.save()
		# return instance
	

#clients = Clients(clientname='serialize', contact='111111', email='abc@gmail.com', comments='comment')
#serializer = ClientsSerializer(clients)
# serializer = ClientsSerializer(clients,data=data)
	class Meta:
		model = Clients
		fields = '__all__'
	
			
class CampaignsSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Campaigns
		fields = '__all__'
	
class BannersSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Banners
		fields = '__all__'

class ZonesSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Zones
		fields = '__all__'

class AffiliatesSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Affiliates
		fields = '__all__'


class UsersSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Users
		fields = '__all__'		
		
class UsersCustomizeSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Users
		fields = ['user_id','username','firstname','lastname','role','skype','phone','date_created']		

		
class LoginTokenSerializer(serializers.ModelSerializer):
	class Meta:
		model = LoginToken
		fields = ['user_id','token']

class User_assoc(serializers.ModelSerializer):
	
	class Meta:
		model = User_assoc
		fields = '__all__'		