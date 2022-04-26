from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post

        fields = ('group', 'text',)

        labels = {
            'group': ('Группа'),
            'text': ('Текст'),
        }

        help_texts = {
            'group': ('Выберите группу для новой записи'),
            'text': ('Добавьте текст для новой записи'),
        }


"""
    def clean_text(self):
        comment = self.cleaned_data['text']
        if not comment:
            raise forms.ValidationError(
                "Нельзя добавить пустой комментарий")
        return comment
."""
