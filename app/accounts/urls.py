from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name ='accounts'
urlpatterns =[
    path('', views.AccountLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('account/', views.AccountListView.as_view(), name="account-list"),
    path('account/create/', views.AccountCreateView.as_view(), name="account-create"),
    path('account/update/<int:pk>', views.AccountUpdateView.as_view(), name="account-update"),
    path('account/delete/<int:pk>', views.AccountDeleteView.as_view(), name="account-delete"),
    path('account/password_change/', views.AccountPwChangeView.as_view(), name='pw-change'),
    path('account/password_reset/<int:user_id>/', views.reset_password, name='pw-reset'),
]