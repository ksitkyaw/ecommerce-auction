from xml.etree.ElementTree import Comment
from django.contrib import admin

from auctions.models import Comment, Bid, Listing, User

# Register your models here.
admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)