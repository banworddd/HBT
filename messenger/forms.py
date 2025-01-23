from django import forms
from .models import GroupPosts, Groups
import re

class GroupPostForm(forms.ModelForm):
    class Meta:
        model = GroupPosts
        fields = ['title', 'post','picture1','picture2', 'picture3']


class GroupCreationForm(forms.ModelForm):
    class Meta:
        model = Groups
        fields = ['name','public_name', 'description', 'is_active']
        widgets = {
            'Name': forms.Textarea(attrs={'rows': 2, 'cols': 20}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not re.match(r'^[a-zA-Z0-9]+$', name):
            raise forms.ValidationError("Имя группы может содержать только латинские буквы и цифры ")
        if Groups.objects.filter(name='@' + name.lower()).exists():
            raise forms.ValidationError('Группа с таким именем уже существует')
        return name