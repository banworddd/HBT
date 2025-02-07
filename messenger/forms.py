from django import forms
from .models import Message, Chats


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text', 'picture']

class GroupChatForm(forms.ModelForm):
    class Meta:
        model = Chats
        fields = ['name','users',]
