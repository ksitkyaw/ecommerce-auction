from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.urls import reverse
from django.shortcuts import render

from .models import User

# Create your views here.
def index(request):
  	return render(request, "auctions/index.html")

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
