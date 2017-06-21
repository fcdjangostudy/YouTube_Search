from django import forms

from ..models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            'content',
        ]
        widgets = {
            'content': forms.TextInput(
                attrs={
                    'class': 'input-comment',
                    'placeholder': '댓글달기',
                }
            )
        }

    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content) < 3:
            raise forms.ValidationError(
                '댓글은 최소 3자 이상이어야 합니다.'
            )
        return content
