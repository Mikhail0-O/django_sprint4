from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Comment, Post


User = get_user_model()

FORMAT_DATE = '%Y-%m-%dT%H:%M'


class UserForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pub_date'].initial = timezone.localtime(
            timezone.now()
        ).strftime(FORMAT_DATE)

    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'pub_date',
            'location',
            'category',
            'image',
        )

        widgets = {
            'pub_date': forms.DateTimeInput(
                format=FORMAT_DATE,
                attrs={'type': 'datetime-local'}
            ),
        }
