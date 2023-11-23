from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import json
from django.http import JsonResponse


from .models import User, Post, Follow, Like


def index(request):

    # Get all the posts and sort by id. Latest id means latest post
    posts = Post.objects.all().order_by("id").reverse()
    
    
    """Course Specification: On any page that displays posts, posts should only be 
    displayed 10 on a page. If there are more than ten posts, a “Next” button should
    appear to take the user to the next page of posts (which should be older than the 
    current page of posts). If not on the first page, a “Previous” 
    button should appear to take the user to the previous page of posts as well."""

    """In that case we use pagination class and create an object"""
    # Pagination instant(object)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)


    # Work for Like button
    all_likes = Like.objects.all()
    the_user_liked = []
    try:
        for like in all_likes:
            if like.user.id == request.user.id:
                the_user_liked.append(like.post.id)
    except:
        the_user_liked = []


    return render(request, "network/index.html", {
        "posts": posts,
        "posts_of_the_page": posts_of_the_page,
        "the_user_liked": the_user_liked
    })




"""when the user clicks the submit button, then it comes the index.html file and by the url 
it finds its route or path from the urls.py file and trigers the view funtion 'new_post'. 
the function takes reqeust argument and takes the post attributes and save to the database. """
def new_post(request):
    if request.method == 'POST':
        post_content = request.POST['content']
        user = User.objects.get(pk=request.user.id)
        new_post = Post(post_content=post_content, user=user)
        new_post.save()
        return HttpResponseRedirect(reverse(index))








def user_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    posts = Post.objects.filter(user=user).order_by("id").reverse()
    
    user_following = Follow.objects.filter(user_following=user)
    user_follower = Follow.objects.filter(user_follower=user)

    is_following = False
    if request.user.is_authenticated:
        # Check if the current user follows the displayed user
        is_following = user_follower.filter(user_following=request.user).exists()

    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
        "posts": posts,
        "posts_of_the_page": posts_of_the_page,
        "user_name": user.username,
        "user_following": user_following,
        "user_follower": user_follower,
        "is_following": is_following,
        "user_profile": user
    })



def follow(request):
    user_follow = request.POST['user_following']
    current_user = User.objects.get(pk=request.user.id)
    user_data = User.objects.get(username=user_follow)
    f = Follow(user_following=current_user, user_follower=user_data)
    f.save()
    user_id = user_data.id 
    return HttpResponseRedirect(reverse(user_profile, kwargs={'user_id': user_id}))


from django.shortcuts import get_object_or_404, HttpResponseRedirect, reverse
from .models import Follow

def unfollow(request):
    if request.method == 'POST':
        user_unfollowing = request.POST.get('user_unfollowing')
        current_user = request.user
        user_to_unfollow = get_object_or_404(User, username=user_unfollowing)
        
        # Check if the follow relationship exists before attempting to delete it
        follow_to_delete = Follow.objects.filter(user_following=current_user, user_follower=user_to_unfollow)
        if follow_to_delete.exists():
            follow_to_delete.delete()

    return HttpResponseRedirect(reverse('user_profile', kwargs={'user_id': user_to_unfollow.id}))





"""Course Specification: Following: The “Following” link in the navigation bar should take 
the user to a page where they see all posts made by users that the current user follows.
This page should behave just as the “All Posts” page does, just with a more limited set of posts.
This page should only be available to users who are signed in."""
def following(request):
    # Get the user who is sending the request
    current_user = request.user
    # Get users that the current user follows
    following_people = Follow.objects.filter(user_following=current_user)
    # Filter posts made by users that the current user follows
    posts_by_followed_users = Post.objects.filter(user__in=following_people.values('user_follower')).order_by('id').reverse()

     # Pagination instant(object)
    paginator = Paginator(posts_by_followed_users, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)


    return render(request, "network/following.html", {
        "posts_of_the_page": posts_of_the_page
    })
    



def edit(request, post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        edit_post = Post.objects.get(pk=post_id)
        edit_post.post_content = data["content"]
        edit_post.save()
        return JsonResponse({"message": "Changed successfully", "data": data["content"]})



def remove_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    like = Like.objects.filter(user=user, post=post)
    like.delete()
    return JsonResponse({"message": "Like removed!"})


def add_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    new_like = Like(user=user, post=post)
    new_like.save()
    return JsonResponse({"message": "Like added!"})













def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
