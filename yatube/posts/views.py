import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


PATH_TO_INDEX = os.path.join('posts', 'index.html')
PATH_TO_GROUP_LIST = os.path.join('posts', 'group_list.html')
PATH_TO_PROFILE = os.path.join('posts', 'profile.html')
PATH_TO_POST = os.path.join('posts', 'post_detail.html')
PATH_TO_CREATE_POST = os.path.join('posts', 'create_post.html')


def page_maker(post_list, request):
    """Return paginator."""
    paginator = Paginator(post_list, settings.POSTS_IN_PAGINATOR)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    """Returns main page."""
    template = PATH_TO_INDEX
    post_list = Post.objects.select_related(
        'group', 'author').all()
    title = 'Main page for project Yatube'
    context = {
        'title': title,
        'page_obj': page_maker(request=request, post_list=post_list),
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Returns group page."""
    template = PATH_TO_GROUP_LIST
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('group', 'author').all()
    context = {
        'group': group,
        'page_obj': page_maker(request=request, post_list=post_list)
    }
    return render(request, template, context)


def profile(request, username):
    """Model and the creation of the context dict for user."""
    template = PATH_TO_PROFILE
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group', 'author').all()
    context = {
        'author': author,
        'posts_count': author.posts.count(),
        'page_obj': page_maker(request=request, post_list=post_list)
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Model and the creation of the context dict for posts."""
    template = PATH_TO_POST
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    posts_count = author.posts.count()
    context = {
        'post': post,
        'posts_count': posts_count,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = PATH_TO_CREATE_POST
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user.username)
    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    # groups = Group.objects.all()
    template = PATH_TO_CREATE_POST
    required_post = Post.objects.get(pk=post_id)
    if required_post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(request.POST or None, instance=required_post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {'form': form, 'required_post': required_post, 'is_edit': True}
    return render(request, template, context)
