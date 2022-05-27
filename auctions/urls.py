from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("all", views.all, name="alllisting"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("accounts/login/", views.notuser, name = "notuser"),
    path("create", views.create, name="create"),
    path("listing/<str:title>", views.listing, name="listing"),
    path("category", views.category, name="category"),
    path("category/<str:category>", views.categorylisting, name='categorylisting'),
    path("watchlist", views.watchlist, name='watchlist'),
    path("close", views.close, name="close"),
    path("bid/<str:title>", views.bid, name='bid'),
    path("comment/<str:title>", views.comment, name='comment')
]