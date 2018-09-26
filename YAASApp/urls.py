from django.urls import path

from . import views

app_name = 'YAASApp'
urlpatterns = (
    path('register/', views.register, name='register'),
    path('login/', views.userlogin, name='login'),
    path('', views.AuctionIndex.as_view(), name='auctionindex'),
    path('profile/', views.userdetail, name='userdetail')
)
