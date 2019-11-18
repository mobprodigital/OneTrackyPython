from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Banners

admin.site.register(Banners)

from .models import Clients

admin.site.register(Clients)

from .models import Campaigns

admin.site.register(Campaigns)

from .models import Zones

admin.site.register(Zones)

from .models import Affiliates

admin.site.register(Affiliates)

from .models import Users

admin.site.register(Users)

from .models import LoginToken

admin.site.register(LoginToken)

from .models import Publisher_access

admin.site.register(Publisher_access)

from .models import Client_access

admin.site.register(Client_access)