
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm, NumberInput, TextInput, Textarea, Select, URLInput
from django.db.models import Max

from .models import Bid, Listing, User, Comment

# Create your views here.
@login_required
def index(request):
	listings = Listing.objects.filter(active=True)
	return render(request, "auctions/index.html", {
		"listings": listings
	})

def all(request):
	listings = Listing.objects.all()
	return render(request, "auctions/index.html", {
		"listings": listings
	})

def notuser(request):
	return render(request, "auctions/notlogin.html")
  	

def login_view(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

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

def listing(request, title):
	item = Listing.objects.get(title=title)
	count = Bid.objects.filter(listing=item).count()
	comments = Comment.objects.filter(listing=item)
	maxbid=Bid.objects.filter(listing=item).aggregate(Max('amount'))
	winner=User.objects.filter(bid__amount=maxbid['amount__max'])
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

def category(request):
	categories = Listing.CATEGORY
	cate = list(Listing.objects.values_list('category'))
	catego = list(map(lambda x: x[0], cate))
	realCategory=[]
	for i in categories:
		if i[0] in catego:
			realCategory.append(i)
	return render(request, "auctions/category.html", {
		'categories': realCategory
	})

def categorylisting(request, category):
	listings = Listing.objects.filter(category=category)
	return render(request, "auctions/index.html", {
		"listings": listings,
		"message": "All Listing that match your category",
	})

def watchlist(request):
	if request.method == 'POST':
		if 'watchlists' not in request.session:
			request.session['watchlists'] = []
		
		watchlisttitle=request.POST['watchlists']
		if watchlisttitle in request.session['watchlists']:
			request.session['watchlists'].pop(request.session['watchlists'].index(watchlisttitle))
			request.session.modified = True
			
		else:
			request.session['watchlists'].append(watchlisttitle)
			request.session.modified = True

		return HttpResponseRedirect(reverse('listing', args=[watchlisttitle,]))
	else:
		items = Listing.objects.filter(title__in = request.session['watchlists'])
		return render(request, "auctions/index.html", {
			"listings": items,
			"message": "Watchlist Items"
		})

def close(request):
	if request.method == 'POST':
		title = request.POST['close']
		Listing.objects.filter(title=title).update(active=False)
		return HttpResponseRedirect(reverse('index'))

def bid(request, title):
	item = Listing.objects.get(title=title)
	maxi = Bid.objects.filter(listing=item).aggregate(Max('amount'))
	if request.method == 'POST':
		amount = request.POST['bid']
		listing = Listing.objects.get(title=title)
		user = request.user
		if maxi['amount__max']:
			if int(amount) > maxi['amount__max']:
				newbid = Bid.objects.create(amount=amount, user=user, listing=listing)
				newbid.save()
				return HttpResponseRedirect(reverse('listing', args=[title,]))
			return render(request, "auctions/biderror.html")
		elif int(amount) > item.startingbid:
			newbid = Bid.objects.create(amount=amount, user=user, listing=listing)
			newbid.save()
			return HttpResponseRedirect(reverse('listing', args=[title,]))
		else: 
			return render(request, "auctions/biderror.html")

def comment(request, title):
	if request.method == 'POST':
		text=request.POST['comment']
		user=request.user
		listing=Listing.objects.get(title=title)
		newcomment=Comment.objects.create(text=text, user=user, listing=listing)
		newcomment.save()
		return HttpResponseRedirect(reverse('listing', args=[title,]))
			
		