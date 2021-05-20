from django.http import request
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .models import *
import bcrypt
import datetime

def index(request):
    return render(request, 'index.html')

def create_user(request):
    if request.method == "POST":
        #See UserManager in models to see all validations. request.POST passes input data to the validator as postData
        errors = User.objects.registration_validator(request.POST)
        if len(errors) > 0:
            for key,value in errors.items():
                messages.error(request, value)
            return redirect('/')

        hash_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        new_user = User.objects.create(
            first_name = request.POST['first_name'],
            last_name = request.POST['last_name'],
            email = request.POST['email'],
            password = hash_pw,
        )
        request.session['logged_user'] = new_user.id

        return redirect('/dashboard')
    return redirect("/")

def login(request):
    if request.method == "POST":
        user = User.objects.filter(email = request.POST['email'])

        if user:
            logged_user = user[0]

            # Validate encrypted password
            if bcrypt.checkpw(request.POST['password'].encode(), logged_user.password.encode()):
                request.session['logged_user'] = logged_user.id
                
                return redirect('/dashboard')
        messages.error(request, "Email or password are incorrect. Please try logging in again.")
    return redirect("/")

def dashboard(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or log in first")
        return redirect('/')
    logged_user = User.objects.get(id=request.session['logged_user'])
    context = {
        'logged_user' : logged_user
    }
    return render(request, 'dashboard.html', context)

def logout(request):
    request.session.flush()
    return redirect('/')

def create_form(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or log in first")
        return redirect('/')
    logged_user = User.objects.get(id=request.session['logged_user'])
    # Need something to keep track of the list order.
    user_set_queue = Song.objects.filter(creator = logged_user, in_queue=True).order_by('list_order_queue')
    saved_user_songs = Song.objects.filter(creator = logged_user, is_copy = False, in_queue = False).order_by('title')
    all_user_songs = Song.objects.filter(creator = logged_user)
    next_order = len(Song.objects.filter(creator = logged_user)) + 1
    
    context = {
        'user_set_queue' : user_set_queue,
        'saved_user_songs' : saved_user_songs,
        'all_user_songs': all_user_songs,
        'next_order' : next_order  
    }

    return render(request, 'create_set.html', context)

def create_song(request):
    if request.method == "POST":
        errors = Song.objects.song_validator(request.POST)
        if len(errors) > 0:
            for key,value in errors.items():
                messages.error(request, value)
            return redirect('/set/create_form')
        logged_user = User.objects.get(id=request.session['logged_user'])
        next_order = len(Song.objects.filter(creator = logged_user, in_queue=True)) + 1
        new_song = Song.objects.create(
            title = request.POST['title'],
            lyrics = request.POST['lyrics'],
            creator = logged_user,
            list_order_queue = next_order
        )
        request.session['new_song'] = new_song.id
        return redirect('/set/create_form')

def delete_song(request, song_id):
    if request.method == "POST":
        to_delete = Song.objects.get(id=song_id)
        to_delete.delete()
        return redirect('/set/create_form')

def delete_song_from_set(request, song_id, set_id):
    if request.method == "POST":
        this_set = Set.objects.get(id=set_id)
        songs_in_set = this_set.songs.all()
        to_delete = Song.objects.get(id=song_id)
        to_delete.delete()
        for song in songs_in_set:
            if(song.list_order_queue > to_delete.list_order_queue):
                song.list_order_queue = song.list_order_queue - 1
                song.save()
        return redirect(f'/set/view/{this_set.id}')

def shift_song_up_in_queue(request, song_id):
    if request.method == "POST":
        print("A post method went through")
        logged_user = User.objects.get(id=request.session['logged_user'])
        this_song = Song.objects.get(id=song_id)
        if(this_song.list_order_queue > 1):
            print(f"This song is {this_song.title}")
            user_set_queue = Song.objects.filter(creator = logged_user, in_queue=True)
            previous_song = user_set_queue.get(list_order_queue = this_song.list_order_queue - 1)
            temp = previous_song.list_order_queue
            previous_song.list_order_queue = this_song.list_order_queue
            this_song.list_order_queue = temp
            previous_song.save()
            this_song.save()
            return redirect('/set/create_form')
    return redirect('/set/create_form')

def shift_song_down_in_queue(request, song_id):
    if request.method == "POST":
        print("A post method went through")
        logged_user = User.objects.get(id=request.session['logged_user'])
        this_song = Song.objects.get(id=song_id)
        user_set_queue = Song.objects.filter(creator = logged_user, in_queue=True)
        if(this_song.list_order_queue < len(user_set_queue)):
            print(f"This song is {this_song.title}")
            next_song = user_set_queue.get(list_order_queue = this_song.list_order_queue + 1)
            temp = next_song.list_order_queue
            next_song.list_order_queue = this_song.list_order_queue
            this_song.list_order_queue = temp
            next_song.save()
            this_song.save()
            return redirect('/set/create_form')
    return redirect('/set/create_form')


def view_song(request, song_id):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or log in first")
        return redirect('/')
    this_song = Song.objects.get(id=song_id)
    new_song_lyrics = this_song.lyrics.split()
    context = {
        'this_song': this_song,
        'lyrics' : new_song_lyrics
    }
    return render(request, 'song_view.html', context)

def edit_song(request, song_id):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or log in first")
        return redirect('/')
    this_song = Song.objects.get(id=song_id)
    new_song_lyrics = this_song.lyrics.split()
    context = {
        'this_song': this_song,
        'lyrics' : new_song_lyrics
    }
    return render(request, 'song_view.html', context)

def remove_from_queue(request, song_id):
    if request.method == "POST":
        logged_user = User.objects.get(id=request.session['logged_user'])
        to_remove = Song.objects.get(id=song_id)
        user_set_queue = Song.objects.filter(creator = logged_user, in_queue=True)
        for song in user_set_queue:
            if(song.list_order_queue > to_remove.list_order_queue):
                song.list_order_queue = song.list_order_queue-1
                song.save()
        to_remove.delete()
        return redirect('/set/create_form')

def push_to_queue(request, song_id):
    if request.method == "POST":
        logged_user = User.objects.get(id=request.session['logged_user'])
        this_song = Song.objects.get(id=song_id)
        list_of_copies = Song.objects.filter(title = this_song.title, creator = logged_user, is_copy = True)
        next_copy_number = 1
        if(len(list_of_copies) > 0):
            next_copy_number = len(list_of_copies) + 1
        this_song_copy = Song.objects.create(
            title = this_song.title,
            creator = this_song.creator,
            lyrics = this_song.lyrics,
            in_queue = True,
            is_copy = True,
            copy_number = next_copy_number
        )
        user_set_queue = Song.objects.filter(creator = logged_user, in_queue=True).order_by('list_order_queue')
        if(user_set_queue):
            last_song = user_set_queue.last()
            this_song_copy.list_order_queue = last_song.list_order_queue + 1
        else:
            this_song_copy.list_order_queue = 1
        this_song_copy.in_queue = True
        this_song_copy.save()
        return redirect('/set/create_form')

def add_song_to_set(request, song_id, set_id):
    if request.method == "POST":
        logged_user = User.objects.get(id=request.session['logged_user'])
        this_song = Song.objects.get(id=song_id)
        this_set = Set.objects.get(id=set_id)
        list_of_copies = Song.objects.filter(title = this_song.title, creator = logged_user, is_copy = True)
        next_copy_number = 1
        songs_in_set = this_set.songs.all()
        if(len(list_of_copies) > 0):
            next_copy_number = len(list_of_copies) + 1
        this_song_copy = Song.objects.create(
            title = this_song.title,
            creator = this_song.creator,
            lyrics = this_song.lyrics,
            in_queue = False,
            is_copy = True,
            copy_number = next_copy_number,
            list_order_queue = len(songs_in_set) + 1,
            display_theme = this_song.display_theme
        )
        #user_set_queue = Song.objects.filter(creator = logged_user, in_queue=True).order_by('list_order_queue')
        this_set.songs.add(this_song_copy)
        this_set.save()
        return redirect(f'/set/view/{this_set.id}')
    return redirect(f'/set/view/{this_set.id}')

def confirm_edit(request):
    pass

def create_set(request):
    if request.method == "POST":
        logged_user = User.objects.get(id=request.session['logged_user'])
        errors = Set.objects.set_validator(request.POST, logged_user)
        if len(errors) > 0:
            for key,value in errors.items():
                messages.error(request, value)
            return redirect('/set/create_form')
        user_set_queue = Song.objects.filter(creator = logged_user, in_queue=True).order_by('list_order_queue')
        new_set = Set.objects.create(
            title = request.POST['title'],
            creator = logged_user,
        )
        for song in user_set_queue:
            song.sets.add(new_set)
            song.in_queue = False
            song.save()
            new_set.save()


        return redirect(f'/set/view/{new_set.id}')
    return redirect('/set/create_form')

def view_set(request, set_id):
    logged_user = User.objects.get(id=request.session['logged_user'])
    this_set = Set.objects.get(id=set_id)
    saved_user_songs = Song.objects.filter(creator = logged_user, is_copy=False)
    songs_in_set = this_set.songs.all()
    context = {
        'this_set': this_set,
        'songs_in_set' : songs_in_set,
        'logged_user': logged_user,
        'saved_user_songs': saved_user_songs
    }
    return render(request, 'set_view.html', context)

def view_user_sets(request):
    logged_user = User.objects.get(id=request.session['logged_user'])
    user_sets = Set.objects.filter(creator = logged_user).order_by('title')
    context = {
        'logged_user': logged_user,
        'user_sets': user_sets
    }
    return render(request, 'user_sets.html', context)

def delete_set(request, set_id):
    if request.method == "POST":
        to_delete = Set.objects.get(id=set_id)
        to_delete.delete()
        return redirect('/set/view_user_sets')
    return redirect('/set/view_user_sets')

def test_route(request):
    return render(request, 'test_route.html')

#Remove this view later
def delete_all_songs(request):
    if request.method == "POST":    
        for song in Song.objects.all():
            print(song.id)
            Song.objects.get(id=song.id).delete()
        return redirect('/dashboard')