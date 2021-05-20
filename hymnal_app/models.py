from django.db import models
import datetime
import re
import random
from django.db.models.fields import CharField

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class UserManager(models.Manager):
    def registration_validator(self, postData):
        errors = {}
        if len(postData['first_name']) < 2:
            errors['first_name'] = "Name must be at least 2 characters"
        if len(postData['last_name']) < 2:
            errors['last_name'] = "Alias must be at least 2 characters"
        #Email needs to be a certain format
        if not EMAIL_REGEX.match(postData['email']):
            errors['email'] = "Invalid email address"
        
        #Duplicate Users check
        users_with_email = User.objects.filter(email = postData['email'])
        if len(users_with_email) >= 1:
            errors['duplicate'] = "Email already exists."

        if len(postData['password']) < 8:
            errors['password'] = "Password must be at least 8 characters"
        if postData['password'] != postData['confirm_password']:
            errors['pw_match'] = "Passwords must match!"
        return errors #errors dictionary is returned to views.create_user

class SongManager(models.Manager):
    def song_validator(self, postData):
        errors = {}
        if len(postData['title']) < 1:
            errors['title'] = "Song must have a title to be created"
        if len(postData['title']) < 1:
            errors['lyrics'] = "Song must have lyrics to be created"
        return errors

class SetManager(models.Manager):
    def set_validator(self, postData, logged_user):
        errors = {}
        user_set_queue = Song.objects.filter(creator = logged_user, in_queue=True).order_by('list_order_queue')
        if len(user_set_queue) < 1:
            errors['songs'] = "There must be songs in queue to create a new set."
        if len(postData['title']) < 1:
            errors['title'] = "Your new set must have a title to be created"
        return errors


class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()
    #sets

class Set(models.Model):
    title = models.CharField(max_length = 50)
    creator = models.ForeignKey(User, related_name='sets', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = SetManager()

class Song(models.Model):
    title = models.CharField(max_length = 50)
    creator = models.ForeignKey(User, related_name='songs', on_delete=models.CASCADE)
    lyrics = models.TextField()
    sets = models.ManyToManyField(Set, related_name="songs")

    class DisplayTheme(models.TextChoices):
        SCROLL = 'Scroll'
        SLIDE = 'Slide'
    
    display_theme = models.CharField(max_length = 50, choices=DisplayTheme.choices, default=DisplayTheme.SCROLL)
    list_order_queue = models.IntegerField(default = 0)
    list_order_saved = models.IntegerField(default = 0)
    in_queue = models.BooleanField(default=False)
    is_copy = models.BooleanField(default=False)
    copy_number = models.IntegerField(default = 0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = SongManager()

class Guest(models.Model):
    rand_id = models.CharField(max_length = 15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Room(models.Model):
    creator = models.ForeignKey(User, related_name='room', on_delete=models.CASCADE)
    access_code = models.CharField(max_length = 5)
    guests = models.ManyToManyField(Guest)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
