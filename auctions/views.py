
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm, NumberInput, TextInput, Textarea, Select, URLInput
from django.db.models import Max

from .models import Bid, Listing, User, Comment

# This decorator make non-login users to not be able to access the view .The index page simply shows all active listing
#the decorator function redirect to 'accounts/login/' by default.Soo it should be defined in url.py
@login_required
def index(request):
	listings = Listing.objects.filter(active=True)
	allListings=Listing.objects.all()
	# for listing in allListings:
	# 	maxbid=Bid.objects.filter(listing=listing).aggregate(Max('amount'))
	# 	winner=User.objects.filter(bid__amount=maxbid['amount__max'])#this returns query set list but there will be only one object as there is only one maximum bid
	# 	if winner and not listing.active:
	# 		if winner[0].username == request.user.username:
	# 			return render(request, "auctions/index.html", {
	# 				"listings": listings,
	# 				"winner": True
	# 			})
	return render(request, "auctions/index.html", {
		"listings": listings
	})

#This view is called by the above mention default url
def notuser(request):
	return render(request, "auctions/notlogin.html")

#This view show all listing active or not
def all(request):
	listings = Listing.objects.all()
	return render(request, "auctions/index.html", {
		"listings": listings
	})



  	

def login_view(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

#To be able to authenticate by our own model, we have to include (AUTH_USER_MODEL = "auctions.User") inside settings
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return HttpResponseRedirect(reverse('index'))
		else:
			return render(request, "auctions/login.html", {
				"message": "Invalid username or password"
			})

	return render(request, "auctions/login.html")

def logout_view(request):
	logout(request)
	return HttpResponseRedirect(reverse('index'))

def register(request):
	if request.method == "POST":
		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['password']
		confirmation = request.POST['confirmation']

		if password != confirmation:
			return render(request, "auctions/register.html", {
				"message": "Passwords must match"
			})

		try:
			user = User.objects.create_user(username, email, password)
			user.save()
		except IntegrityError:
			return render(request, "auctions/register.html", {
				"message": "Username already taken"
			})
		login(request, user)
		return HttpResponseRedirect(reverse('index'))


	return render(request, "auctions/register.html")

#Model form of Listing
class NewListingForm(ModelForm):
	class Meta:
		model=Listing
		fields = ['title', 'description', 'startingbid', 'image', 'category']
		widgets= {
			'title': TextInput(attrs={
				'class': 'form-control',
			}),
			'description': Textarea(attrs={
				'class': 'form-control',
			}),
			'startingbid': NumberInput(attrs={
				'class': 'form-control',
			}),
			'image': URLInput(attrs={
				'class': 'form-control',
			}),
			'category': Select(attrs={
				'class': 'form-control',
			}),
		}
	
#to get current user (request.user) is used
#for post request, get the post data and create an instance of Listing model
def create(request):
	if request.method == 'POST':
		title = request.POST['title']
		description = request.POST['description']
		startingbid = request.POST['startingbid']
		image = request.POST['image']
		category = request.POST['category']
		user = request.user
		listing = Listing.objects.create(title=title, description=description, startingbid=startingbid, user=user, image=image, category=category )
		listing.save()
		return HttpResponseRedirect(reverse('index'))

	return render(request, "auctions/create.html", {
		"form": NewListingForm()
	})

#if the request is closed(no longer active), best bidder will win.
def listing(request, title):
	item = Listing.objects.get(title=title)
	count = Bid.objects.filter(listing=item).count()
	comments = Comment.objects.filter(listing=item)
	maxbid=Bid.objects.filter(listing=item).aggregate(Max('amount'))
	winner=User.objects.filter(bid__amount=maxbid['amount__max'])#this returns query set list but there will be only one object as there is only one maximum bid
	if winner and not item.active:
		if winner[0].username == request.user.username:
			return render(request, "auctions/winner.html", {
				"message": "You have become the winner"
			})
		elif winner[0].username != request.user.username:
			return render(request, "auctions/winner.html", {
				"message": "The listing has been closed and you are not the winner"
			})

	else:
		return render(request, "auctions/listing.html", {
			"item": item,
			"count":count,
			"max": maxbid,
			"comments": comments
		})
#cate is list of tuples so map the list and get only the first values of each tuple like 'RE' and make a list of these values also.
#realCategory  will be a sub list of 'categories'(variable) only include the same values as cate
def category(request):
	categories = Listing.CATEGORY
	cate = list(Listing.objects.values_list('category'))
	catego = list(map(lambda x: x[0], cate))
	print(cate)
	realCategory=[]
	for i in categories:
		if i[0] in catego:
			realCategory.append(i)
	return render(request, "auctions/category.html", {
		'categories': realCategory
	})

#same front-end as index.so it uses index.html with some message
def categorylisting(request, category):
	listings = Listing.objects.filter(category=category)
	return render(request, "auctions/index.html", {
		"listings": listings,
		"message": "All Listing that match your category",
	})
#a button calls this view.the value of the button is posted and saved as watchlisttitle.if it is in session storage, delete it.if not, append it.
def watchlist(request):
	if request.method == 'POST':
		if 'watchlists' not in request.session:
			request.session['watchlists'] = []
		
		watchlisttitle=request.POST['watchlists']
		
		if watchlisttitle in request.session['watchlists']:
			request.session['watchlists'].pop(request.session['watchlists'].index(watchlisttitle))
			request.session.modified = True #this must include to add or delete from session
			
		else:
			request.session['watchlists'].append(watchlisttitle)
			request.session.modified = True#this must include to add or delete from session

		return HttpResponseRedirect(reverse('listing', args=[watchlisttitle,]))
	else:
		if 'watchlists' not in request.session:
			request.session['watchlists'] = []
		items = Listing.objects.filter(title__in = request.session['watchlists'])
		return render(request, "auctions/index.html", {
			"listings": items,
			"message": "Watchlist Items"
		})
#if close button is clicked, the listing's active property will be set to False
def close(request):
	if request.method == 'POST':
		title = request.POST['close']
		Listing.objects.filter(title=title).update(active=False)#**
		return HttpResponseRedirect(reverse('index'))

def bid(request, title):
	item = Listing.objects.get(title=title)
	maxi = Bid.objects.filter(listing=item).aggregate(Max('amount'))#this gives a dictionary object {'amount__max': **}
	if request.method == 'POST':
		amount = request.POST['bid']
		listing = Listing.objects.get(title=title)
		user = request.user
		if maxi['amount__max']: #if there is no bid, it will cause error.that's why this condition needs
			if int(amount) > maxi['amount__max']:#only if the bid is larger than previous max bid, the bid will be saved
				newbid = Bid.objects.create(amount=amount, user=user, listing=listing)
				newbid.save()
				return HttpResponseRedirect(reverse('listing', args=[title,]))
			return render(request, "auctions/biderror.html")
		elif int(amount) > item.startingbid: #new bid must be greater  than starting bid
			newbid = Bid.objects.create(amount=amount, user=user, listing=listing)
			newbid.save()
			return HttpResponseRedirect(reverse('listing', args=[title,]))
		else: 
			return render(request, "auctions/biderror.html")
#adding new comment
def comment(request, title):
	if request.method == 'POST':
		text=request.POST['comment']
		user=request.user  #request.user is also a user object  though it may print as username
		listing=Listing.objects.get(title=title)
		newcomment=Comment.objects.create(text=text, user=user, listing=listing)
		newcomment.save()
		return HttpResponseRedirect(reverse('listing', args=[title,]))
			
		