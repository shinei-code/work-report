from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import LoginForm, CreateForm, UpdateForm, PwChangeForm
from django.contrib import messages

class AccountListView(ListView):
    model = User
    template_name = "account/list.html"
    context_object_name = 'accounts'

class AccountLoginView(LoginView):
    form_class = LoginForm
    template_name = 'account/login.html'

class AccountCreateView(CreateView):
    form_class = CreateForm
    template_name = "account/create.html"
    success_url = reverse_lazy("accounts:account-list")

class AccountUpdateView(UpdateView):
    model = User
    form_class = UpdateForm
    template_name = "account/update.html"
    context_object_name = 'account'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['referer'] = self.request.META.get('HTTP_REFERER')
        return context

    def get_success_url(self):
        referer = self.request.POST.get("next", "")
        if referer:
            return referer
        else:
            return reverse_lazy('report:report-list')

class AccountDeleteView(DeleteView):
    model = User
    template_name = "account/detail.html"
    context_object_name = 'account'
    extra_context = {"delete_confirm": True}
    success_url = reverse_lazy("accounts:account-list")

class AccountPwChangeView(PasswordChangeView):
    form_class = PwChangeForm
    template_name = 'account/password_change.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['referer'] = self.request.META.get('HTTP_REFERER')
        return context

    def get_success_url(self):
        referer = self.request.POST.get("next", "")
        if referer:
            return referer
        else:
            return reverse_lazy('report:report-list')

def reset_password(request, user_id):

    logged_user_id = request.user.id  # ログインユーザ

    user = User.objects.get(pk=user_id)
    random_password = User.objects.make_random_password()
    user.set_password(random_password)
    user.save()

    # ログイン中のユーザーのパスワード変更した場合、再度ログイン処理を実行
    # set_passwordを実行すると、ユーザーセッションが切れるため
    if logged_user_id == user.id:
        user = authenticate(username=user.username, password=random_password)
        if user is not None:
            login(request, user)
        else:
            return HttpResponseRedirect('/')

    messages.success(request, f'ユーザー {user.username} のパスワードを初期化しました。 仮のパスワードは「 <strong>{random_password}</strong> 」です。')

    redirect_url = reverse_lazy('accounts:account-list')
    return HttpResponseRedirect(redirect_url)
