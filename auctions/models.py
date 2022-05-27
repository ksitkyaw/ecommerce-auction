from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
	pass
  
class Listing(models.Model):
	title = models.CharField(max_length=64)
	description = models.TextField()
	startingbid = models.IntegerField()
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller")
	active  = models.BooleanField(default=True)
	image = models.URLField(max_length=200, null=True)
	Electronic = "EC"
	Sports = "SP"
	General = "GN"
	Rare = "RE"
	Entertainment = "ET"
	CATEGORY = [
		(Electronic, "Electronic devices"),
		(Sports, "Sports Equipments"),
		(General, "General Items"),
		(Rare, "Rare or limited Items"),
		(Entertainment, "Books, Music etc")
	] 
	category = models.CharField(max_length=2, choices=CATEGORY, default=General,)

class Bid(models.Model):
	amount = models.IntegerField()
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid")
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bid")

class Comment(models.Model):
	text = models.TextField()
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment")
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comment")
