from django.shortcuts import render, redirect
from .models import Tweet
from .forms import TweetForm, UserRegistrationForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm

def homepage(request):
    return render(request, 'homepage.html')

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

# list all tweets
def tweet_list(request):
    tweets = Tweet.objects.all().order_by('-created_at')
    return render(request, 'tweet_list.html', {'tweets': tweets})

@login_required
# create tweets
def tweet_create(request):
    if request.method == "POST":
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect('tweet_list')
    else:
        form = TweetForm()
    return render(request, 'tweet_form.html', {'form': form})

@login_required
# edit your tweet
def tweet_edit(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk = tweet_id, user=request.user)
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES, instance = tweet)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect('tweet_list')
    else:
        form = TweetForm(instance=tweet)
    return render(request, 'tweet_form.html', {'form': form})

@login_required
# Delete your tweet 
def tweet_delete(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    if request.method == 'POST':
        tweet.delete()
        return redirect('tweet_list')
    return render(request, 'tweet_confirm_delete.html', {'tweet': tweet})

# User Resgister
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            return redirect('tweet_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

# Search the Tweet
def tweet_search(request):
    query = request.GET.get('q')
    if query:
        tweets = Tweet.objects.filter(
            Q(text__icontains=query) | Q(user__username__icontains=query)
        ).order_by('-created_at')
    else:
        tweets = Tweet.objects.all().order_by('-created_at')
    return render(request, 'tweet_search.html', {'tweets': tweets})

# user account details
@login_required
def account_view(request):
    # Get the user's tweets count
    tweets_count = Tweet.objects.filter(user=request.user).count()  # Replace with your actual logic
    
    if request.method == 'POST':
        # Handle change username
        if 'change_username' in request.POST:
            new_username = request.POST.get('username')
            if User.objects.filter(username=new_username).exists():
                messages.error(request, "Username already exists.")
            else:
                request.user.username = new_username
                request.user.save()
                messages.success(request, "Username changed successfully.")

        # Handle change password
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                messages.success(request, "Password changed successfully.")
                return redirect('account')  # Redirect to account page after successful change
            else:
                messages.error(request, "Please correct the error below.")
    
    # Create the password change form
    password_form = PasswordChangeForm(request.user)

    return render(request, 'account.html', {
        'username': request.user.username,
        'tweets_count': tweets_count,
        'password_form': password_form,
    })