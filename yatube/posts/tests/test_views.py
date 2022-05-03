from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

TESTING_ATTEMPTS = 13


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )
        self.post = Post.objects.create(
            text='Test text',
            author=self.user,
            group=self.group
        )

    def test_pages_uses_correct_template(self):
        """URL-adress using correct HTML."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': self.group.slug})
            ),
            'posts/profile.html': (
                reverse('posts:profile',
                        kwargs={'username': self.user.username})
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': self.post.id})
            ),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_pages_uses_correct_template(self):
        """URL-adress post_edit uses template create_post.html."""
        response = (self.authorized_client.
                    get(reverse('posts:post_edit',
                        kwargs={'post_id': self.post.id})))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_group_list_page_show_correct_context(self):
        """Template group_list gives group list of the posts."""
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                        kwargs={'slug': self.group.slug})))
        group = response.context['group']
        self.assertEqual(group, Group.objects.get(slug=self.group.slug))

    def test_profile_page_show_correct_context(self):
        """Template profile gives list of the author's posts."""
        response = (self.authorized_client.
                    get(reverse('posts:profile',
                        kwargs={'username': self.user.username})))
        author = response.context['author']
        posts_count = response.context['posts_count']
        self.assertEqual(author, User.objects.get(username=self.user.username))
        self.assertEqual(posts_count, Post.objects.filter(
            author__username=self.user.username
        ).count())

    def test_post_detail_pages_show_correct_context(self):
        """Template post_detail gives one post filtered by its id."""
        response = (self.authorized_client.
                    get(reverse('posts:post_detail',
                        kwargs={'post_id': self.post.id})))
        post = response.context['post']
        posts_count = response.context['posts_count']
        self.assertEqual(post, Post.objects.get(id=self.post.id))
        self.assertEqual(posts_count, 1)

    def test_create_post_show_correct_context(self):
        """Template create_post gives form to create post."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_pages_show_correct_context(self):
        """Template create_post gives form to edit post."""
        response = (self.authorized_client.
                    get(reverse('posts:post_edit',
                        kwargs={'post_id': self.post.id})))
        required_post = response.context['required_post']
        self.assertEqual(required_post, Post.objects.get(id=self.post.id))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_show_correct_text(self):
        """Additional check of first post text."""
        templates_pages_names = {
            reverse('posts:index'): self.post.text,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): self.post.text,
            reverse('posts:profile',
                    kwargs={'username': self.user.username}): self.post.text,
        }
        for value, expected in templates_pages_names.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object.text, expected)

    def test_post_show_correct_post_id(self):
        """Checking id of first post."""
        templates_pages_names = {
            reverse('posts:index'): self.post.id,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): self.post.id,
            reverse('posts:profile',
                    kwargs={'username': self.user.username}): self.post.id,
        }
        for value, expected in templates_pages_names.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object.id, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.user = User.objects.create_user(username='TestUser2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Test group_2',
            slug='test-slug2',
            description='Test description_2',
        )
        self.post = Post.objects.bulk_create(
            [
                Post(
                    text='Testing paginator',
                    author=self.user,
                    group=self.group,
                ),
            ] * TESTING_ATTEMPTS
        )

    def test_first_page_contains_ten_records(self):
        templates_pages_names = {
            reverse('posts:index'): settings.POSTS_IN_PAGINATOR,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}):
            settings.POSTS_IN_PAGINATOR,
            reverse('posts:profile',
                    kwargs={'username': self.user.username}):
            settings.POSTS_IN_PAGINATOR,
        }
        for reverse_template, expected in templates_pages_names.items():
            with self.subTest(reverse_template=reverse_template):
                response = self.client.get(reverse_template)
                self.assertEqual(len(response.context['page_obj']), expected)

    def test_second_page_contains_three_records(self):
        all_posts = Post.objects.filter(
            author__username=self.user.username
        ).count()
        second_page_posts = all_posts - settings.POSTS_IN_PAGINATOR
        templates_pages_names = {
            reverse('posts:index'): second_page_posts,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): second_page_posts,
            reverse('posts:profile',
                    kwargs={'username': self.user.username}):
            second_page_posts,
        }
        for reverse_template, expected in templates_pages_names.items():
            with self.subTest(reverse_template=reverse_template):
                response = self.client.get(reverse_template + '?page=2')
                self.assertEqual(len(response.context['page_obj']), expected)
