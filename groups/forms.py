from django import forms
from .models import GroupPosts, Groups, GroupPostsComments
import re

class GroupPostForm(forms.ModelForm):
    class Meta:
        model = GroupPosts
        fields = ['title', 'post','picture1','picture2', 'picture3']

class GroupPostCommentForm(forms.ModelForm):
    class Meta:
        model = GroupPostsComments
        fields = ['comment']


class GroupCreationForm(forms.ModelForm):
    class Meta:
        model = Groups
        fields = ['name','public_name', 'description', 'is_active', 'avatar']
        widgets = {
            'Name': forms.Textarea(attrs={'rows': 2, 'cols': 20}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['name'] = self.instance.name.lstrip('@')

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not re.match(r'^[a-zA-Z0-9]+$', name):
            raise forms.ValidationError("Имя группы может содержать только латинские буквы и цифры ")
        if self.instance and self.instance.pk:
            group = Groups.objects.get(name='@' + name.lower())
            if group.name!="@"+name:
                raise forms.ValidationError('Группа с таким именем уже существует')
        else:
            if Groups.objects.filter(name='@' + name.lower()).exists():
                raise forms.ValidationError('Группа с таким именем уже существует')
        return name



