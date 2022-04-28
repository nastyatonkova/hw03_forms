from django.contrib.auth import get_user_model
from django.db import models

from posts.validators import validate_not_empty

User = get_user_model()


class Post(models.Model):
    """ Class for creating posts."""
    text = models.TextField(validators=[validate_not_empty])
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        'Group',
        null=True,
        blank=True,
        related_name='posts',
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-pub_date']


class Group(models.Model):
    """Class for creating groups."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title
