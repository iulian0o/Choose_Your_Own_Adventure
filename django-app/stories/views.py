import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.db.models import Count
from .models import Play, PlaySession, Rating
from django.contrib.auth import logout as auth_logout, login
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from django.db import models


FLASK_API = settings.FLASK_API_URL


def get_headers():
    """Level 16: Include API key for write operations"""
    return {"X-API-KEY": settings.FLASK_API_KEY}

@login_required
def story_list(request):
    """List all published stories with ratings"""
    search_query = request.GET.get('search', '')
    
    try:
        response = requests.get(f"{FLASK_API}/stories?status=published")
        stories = response.json() if response.status_code == 200 else []
        
        for story in stories:
            ratings = Rating.objects.filter(story_id=story['id'])
            if ratings.exists():
                story['avg_rating'] = round(ratings.aggregate(models.Avg('stars'))['stars__avg'], 1)
            else:
                story['avg_rating'] = None
        
        if search_query:
            stories = [s for s in stories if 
                      search_query.lower() in s['title'].lower() or 
                      search_query.lower() in s.get('description', '').lower()]
    except Exception as e:
        stories = []
        messages.error(request, f"Could not connect to story database")
    
    return render(request, 'stories/list.html', {
        'stories': stories,
        'search_query': search_query
    })

@login_required
def story_detail(request, story_id):
    """View story details with ratings"""
    try:
        response = requests.get(f"{FLASK_API}/stories/{story_id}")
        story = response.json() if response.status_code == 200 else None
    except:
        story = None
        messages.error(request, "Could not load story")
    
    plays = Play.objects.filter(story_id=story_id)
    total_plays = plays.count()
    endings_stats = plays.values('ending_page_id').annotate(count=Count('ending_page_id'))
    
    ratings = Rating.objects.filter(story_id=story_id).order_by('-created_at')
    user_rating = Rating.objects.filter(story_id=story_id, user=request.user).first()
    
    if ratings.exists():
        avg_rating = ratings.aggregate(models.Avg('stars'))['stars__avg']
        avg_rating = round(avg_rating, 1)
    else:
        avg_rating = None
    
    context = {
        'story': story,
        'total_plays': total_plays,
        'endings_stats': endings_stats,
        'ratings': ratings,
        'user_rating': user_rating,
        'avg_rating': avg_rating,
        'total_ratings': ratings.count()
    }
    return render(request, 'stories/detail.html', context)

@login_required
def rate_story(request, story_id):
    """Rate a story"""
    if request.method == 'POST':
        stars = request.POST.get('stars')
        comment = request.POST.get('comment', '')
        
        try:
            stars = int(stars)
            if 1 <= stars <= 5:
                rating, created = Rating.objects.update_or_create(
                    story_id=story_id,
                    user=request.user,
                    defaults={'stars': stars, 'comment': comment}
                )
                if created:
                    messages.success(request, 'Rating submitted!')
                else:
                    messages.success(request, 'Rating updated!')
            else:
                messages.error(request, 'Invalid rating value')
        except:
            messages.error(request, 'Error submitting rating')
    
    return redirect('story_detail', story_id=story_id)

@login_required
def play_story(request, story_id):
    """Start playing a story or resume"""
    session_key = request.session.session_key or request.session.create()
    
    try:
        play_session = PlaySession.objects.get(
            session_key=session_key,
            story_id=story_id
        )
        return redirect('play_page', story_id=story_id, page_id=play_session.current_page_id)
    except PlaySession.DoesNotExist:
        try:
            response = requests.get(f"{FLASK_API}/stories/{story_id}/start")
            if response.status_code == 200:
                page = response.json()
                
                PlaySession.objects.create(
                    session_key=session_key,
                    story_id=story_id,
                    current_page_id=page['id']
                )
                
                return render(request, 'play/page.html', {
                    'story_id': story_id,
                    'page': page
                })
        except:
            messages.error(request, "Could not start story")
    
    return redirect('story_list')

@login_required
def play_page(request, story_id, page_id):
    """Display a specific page during play"""
    session_key = request.session.session_key or request.session.create()
    
    try:
        response = requests.get(f"{FLASK_API}/pages/{page_id}")
        if response.status_code == 200:
            page = response.json()
            
            if not page.get('is_ending'):
                PlaySession.objects.update_or_create(
                    session_key=session_key,
                    story_id=story_id,
                    defaults={'current_page_id': page_id}
                )
            else:
                PlaySession.objects.filter(
                    session_key=session_key,
                    story_id=story_id
                ).delete()
                
                Play.objects.create(
                    story_id=story_id,
                    ending_page_id=page_id
                )
            
            return render(request, 'play/page.html', {
                'story_id': story_id,
                'page': page
            })
    except:
        messages.error(request, "Could not load page")
    
    return redirect('story_list')

@login_required
def statistics(request):
    """Show statistics for all stories"""
    story_stats = (
        Play.objects.values("story_id")
        .annotate(play_count=Count("id"))
        .order_by("-play_count")
    )

    stories_data = []
    for stat in story_stats:
        try:
            response = requests.get(f"{FLASK_API}/stories/{stat['story_id']}")
            if response.status_code == 200:
                story = response.json()
                story["play_count"] = stat["play_count"]

                endings = (
                    Play.objects.filter(story_id=stat["story_id"])
                    .values("ending_page_id")
                    .annotate(count=Count("id"))
                )

                story["endings"] = []
                for ending in endings:
                    percentage = (ending["count"] / stat["play_count"]) * 100
                    story["endings"].append(
                        {
                            "page_id": ending["ending_page_id"],
                            "count": ending["count"],
                            "percentage": round(percentage, 1),
                        }
                    )

                stories_data.append(story)
        except:
            pass

    return render(request, "stories/statistics.html", {"stories": stories_data})

@login_required
def author_dashboard(request):
    """Author dashboard - list all stories"""
    try:
        response = requests.get(f"{FLASK_API}/stories?status=published")
        stories = response.json() if response.status_code == 200 else []
    except:
        stories = []

    return render(request, "author/dashboard.html", {"stories": stories})

def story_create(request):
    """Create a new story"""
    if request.method == 'POST':
        data = {
            'title': request.POST.get('title'),
            'description': request.POST.get('description'),
            'status': 'published'
        }
        try:
            response = requests.post(f"{FLASK_API}/stories", json=data)
            if response.status_code == 201:
                story = response.json()
                messages.success(request, 'Story created successfully!')
                return redirect('story_edit', story_id=story['id'])
        except:
            messages.error(request, 'Could not create story')
    
    return render(request, 'author/story_form.html')  


@login_required
def story_edit(request, story_id):
    """Edit a story and manage pages/choices"""
    try:
        response = requests.get(f"{FLASK_API}/stories/{story_id}")
        story = response.json() if response.status_code == 200 else None

        if not story:
            messages.error(request, "Story not found")
            return redirect("author_dashboard")

    except:
        messages.error(request, "Could not load story")
        return redirect("author_dashboard")

    if request.method == "POST":
        data = {
            "title": request.POST.get("title"),
            "description": request.POST.get("description"),
        }
        try:
            response = requests.put(f"{FLASK_API}/stories/{story_id}", json=data)
            if response.status_code == 200:
                messages.success(request, "Story updated!")
                return redirect("story_edit", story_id=story_id)
        except:
            messages.error(request, "Could not update story")

    return render(request, "author/story_edit.html", {"story": story})


def page_create(request, story_id):
    """Create a new page for a story"""
    if request.method == "POST":
        data = {
            "text": request.POST.get("text"),
            "is_ending": request.POST.get("is_ending") == "on",
            "ending_label": request.POST.get("ending_label", ""),
        }
        try:
            response = requests.post(f"{FLASK_API}/stories/{story_id}/pages", json=data)
            if response.status_code == 201:
                messages.success(request, "Page created!")
                return redirect("story_edit", story_id=story_id)
        except:
            messages.error(request, "Could not create page")

    return render(request, "author/page_form.html", {"story_id": story_id})


def choice_create(request, page_id):
    """Create a choice for a page"""
    if request.method == "POST":
        data = {
            "text": request.POST.get("text"),
            "next_page_id": request.POST.get("next_page_id"),
        }
        try:
            response = requests.post(f"{FLASK_API}/pages/{page_id}/choices", json=data)
            if response.status_code == 201:
                messages.success(request, "Choice created!")
        except:
            messages.error(request, "Could not create choice")

    return render(request, "author/choice_form.html", {"page_id": page_id})


def story_delete(request, story_id):
    """Delete a story"""
    if request.method == 'POST':
        try:
            response = requests.delete(f"{FLASK_API}/stories/{story_id}")
            if response.status_code == 204:
                messages.success(request, 'Story deleted!')
            else:
                messages.error(request, f'Delete failed: {response.status_code}')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return redirect('author_dashboard')

def story_publish(request, story_id):
    """Publish a draft story"""
    if request.method == 'POST':
        try:
            response = requests.put(
                f"{FLASK_API}/stories/{story_id}",
                json={'status': 'published'}
            )
            if response.status_code == 200:
                messages.success(request, 'Story published!')
        except:
            messages.error(request, 'Could not publish story')
    
    return redirect('story_edit', story_id=story_id)

def preview_story(request, story_id):
    """Preview a story without recording stats"""
    try:
        response = requests.get(f"{FLASK_API}/stories/{story_id}/start")
        if response.status_code == 200:
            page = response.json()
            return render(request, 'play/preview_page.html', {
                'story_id': story_id,
                'page': page,
                'preview_mode': True
            })
    except:
        messages.error(request, "Could not start preview")
    
    return redirect('author_dashboard')

def preview_page(request, story_id, page_id):
    """Preview a specific page"""
    try:
        response = requests.get(f"{FLASK_API}/pages/{page_id}")
        if response.status_code == 200:
            page = response.json()
            return render(request, 'play/preview_page.html', {
                'story_id': story_id,
                'page': page,
                'preview_mode': True
            })
    except:
        messages.error(request, "Could not load page")
    
    return redirect('author_dashboard')

def simple_story_create(request):
    """Simple one-page story creator"""
    if request.method == 'POST':
        # Create the story
        story_data = {
            'title': request.POST.get('title'),
            'description': request.POST.get('description'),
            'status': 'published'
        }
        
        try:
            story_response = requests.post(f"{FLASK_API}/stories", json=story_data, headers=get_headers())
            story = story_response.json()
            
            page1_data = {'text': request.POST.get('page1_text'), 'is_ending': False}
            page1_response = requests.post(f"{FLASK_API}/stories/{story['id']}/pages", json=page1_data, headers=get_headers())
            page1 = page1_response.json()
            
            page2_data = {'text': request.POST.get('page2_text'), 'is_ending': False}
            page2_response = requests.post(f"{FLASK_API}/stories/{story['id']}/pages", json=page2_data, headers=get_headers())
            page2 = page2_response.json()
            
            ending1_data = {'text': request.POST.get('ending1_text'), 'is_ending': True, 'ending_label': request.POST.get('ending1_label')}
            ending1_response = requests.post(f"{FLASK_API}/stories/{story['id']}/pages", json=ending1_data, headers=get_headers())
            ending1 = ending1_response.json()
            
            ending2_data = {'text': request.POST.get('ending2_text'), 'is_ending': True, 'ending_label': request.POST.get('ending2_label')}
            ending2_response = requests.post(f"{FLASK_API}/stories/{story['id']}/pages", json=ending2_data, headers=get_headers())
            ending2 = ending2_response.json()
            
            requests.post(f"{FLASK_API}/pages/{page1['id']}/choices", json={'text': request.POST.get('choice1_text'), 'next_page_id': page2['id']}, headers=get_headers())
            requests.post(f"{FLASK_API}/pages/{page1['id']}/choices", json={'text': request.POST.get('choice2_text'), 'next_page_id': ending1['id']}, headers=get_headers())
            requests.post(f"{FLASK_API}/pages/{page2['id']}/choices", json={'text': request.POST.get('choice3_text'), 'next_page_id': ending1['id']}, headers=get_headers())
            requests.post(f"{FLASK_API}/pages/{page2['id']}/choices", json={'text': request.POST.get('choice4_text'), 'next_page_id': ending2['id']}, headers=get_headers())
            
            messages.success(request, 'Story created successfully!')
            return redirect('author_dashboard')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'author/simple_create.html')

@login_required
def author_dashboard(request):
    """Author dashboard - requires login"""
    try:
        response = requests.get(f"{FLASK_API}/stories")
        stories = response.json() if response.status_code == 200 else []
    except:
        stories = []
    
    return render(request, 'author/dashboard.html', {'stories': stories})

@login_required
def simple_story_create(request):
    """Simple story creator - requires login"""

@login_required
def story_delete(request, story_id):
    """Delete story - requires login"""

def register(request):
    """User registration - public"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created.')
            return redirect('story_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
    
    return render(request, 'registration/register.html', {'form': form})

def user_logout(request):
    """Logout user"""
    auth_logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('login')