# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from . import models
#from . import serializers
from rest_framework import permissions
#from . import permissions as my_permissions
#from wmap2017 import settings


from django.contrib.auth import authenticate, login, logout, get_user_model
from rest_framework import permissions, authentication, status, generics
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.shortcuts import get_object_or_404, render, redirect, render_to_response
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry, LineString, Point, Polygon
from rest_framework.authtoken.models import Token
# from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.forms import ValidationError
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView, UpdateView, CreateView, DeleteView


from django.http import JsonResponse
from django.core import serializers
from django.db.models import Q
from itertools import chain

from models import User, Friends
import json
from django.views.decorators.csrf import csrf_exempt

from . import forms


# Users
def user(request):

    def get():
        print(request.GET)
        user_raw = User.objects.get(username=request.GET.get("username"))

        user_js = {"username" : user_raw.username, "location" : user_raw.location, "password" : user_raw.password}
        return JsonResponse(user_js, status=status.HTTP_200_OK)

    def post():

        username = request.POST.get("username")
        password = request.POST.get("password")

        User.objects.get_or_create(username=username,password=password)
        return JsonResponse({"success: ": "username: " + username + " pw:" + password}, status=status.HTTP_200_OK)

    def update():
        # update does NOT work because request.PUT is not a thing in django, could not find a viable fix for this in time

        user_u = User.objects.get(username=request.PUT.get("username"))
        new_username = request.PUT.get("new_username")
        new_location = request.PUT.get("new_location")

        if new_username:
            user_u.username = new_username
        if new_location:
            user_u.location = new_location

        user_u.save()
        return JsonResponse({"success: ": "username: " + user_u.username + " -> " + new_username}, status=status.HTTP_200_OK)

    def delete():
        User.objects.filter(username=request.GET["username"], password=request.GET["password"]).delete()
        return JsonResponse({"User Deleted": request.GET["username"]}, status=status.HTTP_200_OK)

    if request.method == "GET":
        return get()
    if request.method == "POST":
        return post()
    if request.method == "DELETE":
        return delete()
    #update
    if request.method == "PUT":
        return update()

# Friends
def friends(request):

    def get():
        user_check = User.objects.get(username=request.GET["username"])
        try:
            friends_a = Friends.objects.filter(user_a=user_check).only("user_b")

        except Friends.DoesNotExist:
            friends_a = None
        try:
            friends_b = Friends.objects.filter(user_b=user_check).only("user_a")
        except Friends.DoesNotExist:
            friends_b = None

        friends_json = []
        for i in friends_a:
            print(i.user_b.username)
            toApp = {"username" : i.user_b.username, "location": i.user_b.location}
            friends_json.append(toApp)
        for i in friends_b:
            print(i.user_a.username)
            toApp = {"username" : i.user_a.username, "location": i.user_a.location}
            friends_json.append(toApp)

        print(friends_json)

        return JsonResponse(friends_json, status=status.HTTP_200_OK, safe=False)

    def post():
        user_a = User.objects.get(username=request.POST.get("username_a"))
        user_b = User.objects.get(username=request.POST.get("username_b"))

        Friends.objects.get_or_create(user_a=user_a, user_b=user_b)
        return JsonResponse({"Friends_Created ": " success"}, status=status.HTTP_200_OK)

    def delete():

        print(request.GET)

        user_a = User.objects.get(username=request.GET.get("username_a"))
        user_b = User.objects.get(username=request.GET.get("username_b"))

        Friends.objects.filter(user_a=user_a, user_b=user_b).delete()
        Friends.objects.filter(user_a=user_b, user_b=user_a).delete()

        return JsonResponse({"Friend Delete": user_a.username + " ~ " + user_b.username},
                            status=status.HTTP_200_OK)

    if request.method == "GET":
        return get()
    if request.method == "POST":
        return post()
    if request.method=="DELETE":
        return delete()





### LOGIN STUFF

@login_required
def logout_view(request):
    logout(request)
    return redirect(reverse('app:login'))

@login_required
def landing(request):
    return render(request, 'landing.html')


def login_view(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = forms.LoginForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    return redirect(reverse('app:landing'))
                else:
                    form.add_error(None, ValidationError(
                        "Your account is not active."
                    ))
            else:
                form.add_error(None, ValidationError(
                    "Invalid User Id of Password"
                ))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = forms.LoginForm()

    return render(request, 'login.html', {'form': form})


def signup_view(request):
    if request.POST:
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = get_user_model().objects.get(username=username)
                if user:
                    form.add_error(None, ValidationError("This user already exists."))
            except get_user_model().DoesNotExist:
                user = get_user_model().objects.create_user(username=username)

                # Set user fields provided
                user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.save()

                return redirect(reverse('app:login'))
    else:
        form = forms.SignupForm()

    return render(request, 'signup.html', {'form': form})


class UserProfile(UpdateView):
    form_class = forms.UserProfileForm
    template_name = "user_profile.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserProfile, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        return get_user_model().objects.get(pk=self.request.user.pk)