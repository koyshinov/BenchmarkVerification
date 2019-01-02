from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.shortcuts import redirect


def index(request):
    return redirect("/run")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        next = request.POST.get("next", "/run")

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(next)
        else:
            return render(request, 'login.html', {"next": next, "invalid": True})

    else:
        next = request.GET.get("next", "/run")
        return render(request, 'login.html', {"next": next})


def logout_view(request):
    logout(request)
    return redirect("/login")
