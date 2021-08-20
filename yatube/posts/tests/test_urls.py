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
        cls.public_urls = {
            "/": "index.html",
            "/500/": "misc/500.html",
            f"/group/{cls.group.slug}/": "group.html",
            f"/{cls.post.author.username}/{cls.post.pk}/": "post.html",
            f"/{cls.user.username}/": "profile.html",
        }
        cls.private_urls = {
            "/new/": "newpost.html",
            f"/{cls.post.author.username}/{cls.post.pk}/edit/":
                "newpost.html",
            "/follow/": "follow.html",
            f"/{cls.post.author.username}/{cls.post.pk}/comment/":
            "includes/comments.html"
        }
        cls.templates_url_name = {**cls.private_urls, **cls.public_urls}
        follow_urls = [f"/{cls.post.author.username}/follow/",
                       f"/{cls.post.author.username}/unfollow/"]
        private_urls = list(cls.private_urls.keys()) + follow_urls
        cls.redirect_urls_to_auth = {
            url: f"/auth/login/?next={url}" for url in
            private_urls}


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
        code_500 = HTTPStatus.INTERNAL_SERVER_ERROR
        for url in self.public_urls.keys():
            code = code_500 if url == "/500/" else HTTPStatus.OK
            with self.subTest(url=url):
                response = self.guest_user.get(url)
                self.assertEqual(response.status_code, code,
                                 msg=f"Страница {url} недоступна")

    def test_private_url_exists_at_desired_location_autorized(self):
        """Checking access to the private page for authorized user."""
        for url in self.private_urls.keys():
            with self.subTest(url=url):
                response = self.authorized_user.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 msg=f"Страница {url} недоступна")

    def test_private_url_redirect_anonymous(self):
        """Checking redirect on the private page to page
        of signup for for an unauthorized user."""
        for url, expected_redirect in self.redirect_urls_to_auth.items():
            with self.subTest(url=url):
                response = self.guest_user.get(url, follow=True)
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
        templates_url_name = self.templates_url_name
        for address, template in templates_url_name.items():
            with self.subTest(address=address):
                response = authorized_user.get(address)
                self.assertTemplateUsed(response, template)
