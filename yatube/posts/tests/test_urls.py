from http import HTTPStatus
from uuid import uuid4

from django.core.cache import cache
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from ..models import Post, Group


User = get_user_model()


class TestSetUpClassMixin:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="DracoMalfoy")
        cls.group = Group.objects.create(
            title="Some Group",
            description="some description about",
            slug="somegroup"
        )
        cls.post = Post.objects.create(
            text="some text about something, "
                 "and about nothing.",
            author=cls.user
        )
        cls.templates_url_name = {
            "index.html": "/",
            "group.html": f"/group/{cls.group.slug}/",
            "post.html": f"/{cls.post.author.username}/{cls.post.pk}/",
            "newpost.html": "/new/",
            "profile.html": f"/{cls.user.username}/"
        }
        cls.public_urls = (cls.templates_url_name["index.html"],
                           cls.templates_url_name["group.html"],
                           cls.templates_url_name["post.html"],
                           cls.templates_url_name["profile.html"],
                           )


class PostsURLTest(TestSetUpClassMixin, TestCase):
    """Test URLs app Posts"""
    def setUp(self) -> None:
        self.guest_user = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(PostsURLTest.user)
        self.group = PostsURLTest.group
        self.user = PostsURLTest.user
        self.post = PostsURLTest.post

    def tearDown(self) -> None:
        cache.clear()

    def test_not_exists_url_anonymous(self):
        url = f"/{str(uuid4())}/"
        response = self.guest_user.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_url_exists_at_desired_location_anonymous(self):
        """Checking access to the main, group, profile and post
        pages of any user."""
        for url in PostsURLTest.public_urls:
            with self.subTest(url=url):
                response = self.guest_user.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 msg=f"Страница {url} недоступна")

    def test_new_post_url_exists_at_desired_location_autorized(self):
        """Checking access to the page for creating a new post
        only for authorized user."""
        url = "/new/"
        response = self.authorized_user.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         msg=f"Страница {url} недоступна")

    def test_new_post_url_redirect_anonymous(self):
        """Checking redirect on the page for creating a new post
        to page of signup for for an unauthorized user."""
        url = "/new/"
        expected_redirect = f"/auth/login/?next={url}"
        response = self.guest_user.get(url, follow=True)
        self.assertRedirects(response, expected_redirect)

    def test_edit_post_url_exists_at_desired_location_autorized_author(self):
        """Checking access to the page for editing an entry
        only for an authorized user who is the author of the post."""
        url = f"/{self.post.author.username}/{self.post.pk}/edit/"
        response = self.authorized_user.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         msg=f"Страница {url} недоступна")

    def test_edit_post_url_redirect_anonymous(self):
        """Checking redirect on the page for post edit
        to page of signup for an unauthorized user."""
        url = f"/{self.post.author.username}/{self.post.pk}/edit/"
        response = self.guest_user.get(url, follow=True)
        expected_redirect = f"/auth/login/?next={url}"
        self.assertRedirects(response, expected_redirect)

    def test_edit_post_url_redirect_authorized_not_author(self):
        """Checking redirect on the page for post edit
        to author post page for an authorized user but not
        post author."""
        another_user = User.objects.create(username="GarryPotter")
        not_author = Client()
        not_author.force_login(another_user)
        url = f"/{self.post.author.username}/{self.post.pk}/edit/"
        expected_redirect = f"/{self.post.author.username}/{self.post.pk}/"
        response = not_author.get(url, follow=True)
        self.assertRedirects(response, expected_redirect)


class PostsTemplateTest(TestSetUpClassMixin, TestCase):
    """Test templates app Posts."""

    def test_urls_uses_correct_template(self):
        """Checks that the correct template is called
        when accessing a specific URL."""
        cache.clear()
        authorized_user = Client()
        authorized_user.force_login(PostsTemplateTest.user)
        templates_url_name = PostsTemplateTest.templates_url_name
        for template, address in templates_url_name.items():
            with self.subTest(address=address):
                response = authorized_user.get(address)
                self.assertTemplateUsed(response, template)
