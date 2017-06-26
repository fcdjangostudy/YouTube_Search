from django import forms

from member.models import User


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['nickname', 'img_profile', ]
