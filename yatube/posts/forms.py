from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["text", "group", "image"]
        labels = {"text": "Введите текст",
                  "group": "Выберите группу",
                  "image": "Вставьте свою картинку"}
        help_texts = {"text": "Удивите всех своей историей",
                      "group": "Это всё ...",
                      "image": "Картинка должна быть здесь"}


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        labels = {"text": "Введите текст"}
        help_texts = {"text": "Прокомментруй это..."}
