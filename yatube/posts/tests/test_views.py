import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django import forms
from django.contrib.auth import get_user_model

from ..models import Post, Group, Follow, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class TestViewsSetUpClassMixin:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_user = Client()
        cls.user = User.objects.create(username="DracoMalfoy")
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.follow_user1 = User.objects.create(username="Harry Potter")
        cls.follow_user2 = User.objects.create(username="Voldemort")
        Follow.objects.create(user=cls.follow_user1, author=cls.user)
        cls.first_group = Group.objects.create(
            title="Slytherin",
            description="Draco dormiens nunquam titillandus!",
            slug="slith")
        image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.test_image = SimpleUploadedFile(
            name="test.png",
            content=image,
            content_type="image/png"
        )

        cls.post_in_first_group = Post.objects.create(
            text="Avada Kedavra",
            author=cls.user,
            group=cls.first_group,
            image=cls.test_image)
        cls.comment = Comment.objects.create(
            text="One ticket to Azkaban please",
            post=cls.post_in_first_group,
            author=cls.follow_user1)

        cls.templates_pages_names = {
            "index.html": reverse("posts:index"),
            "follow.html": reverse("posts:follow_index"),
            "newpost.html": reverse("posts:new_post"),
            "group.html": reverse("posts:post_in_group",
                                  kwargs={"slug": cls.first_group.slug}),
            "profile.html": reverse("posts:profile",
                                    kwargs={"username": cls.user.username}),
            "post.html": reverse("posts:post",
                                 kwargs={
                                     "username": cls.user.username,
                                     "post_id": cls.post_in_first_group.pk})
        }


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestViewsSetUpClassMixin, TestCase):
    """Checking whether view classes use the correct templates
    and get right context."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.authorized_user = PostPagesTest.authorized_user
        self.group = PostPagesTest.first_group
        self.user = PostPagesTest.user

    def tearDown(self) -> None:
        cache.clear()

    def test_pages_use_correct_templates(self):
        """Checking templates."""
        template_pages = PostPagesTest.templates_pages_names
        for template, reverse_name in template_pages.items():
            with self.subTest(revercse_name=reverse_name):
                response = self.authorized_user.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_homepage_show_correct_context(self):
        """Checking the transmission of the correct context
        to the main page, also checks the operation
        of the service function for all views
        where pagination is used."""
        response = self.authorized_user.get(reverse("posts:index"))
        post_object = response.context["page"].object_list[0]
        self.assertEqual(post_object.text, "Avada Kedavra")
        self.assertEqual(post_object.image, f"posts/{self.test_image}")

    def test_follow_homepage_show_correct_context(self):
        authorized_user = Client()
        authorized_user.force_login(self.follow_user1)
        response = authorized_user.get(reverse("posts:follow_index"))
        post_object = response.context["page"].object_list[0]
        self.assertEqual(post_object.text, "Avada Kedavra")
        self.assertEqual(post_object.image, f"posts/{self.test_image}")

    def test_homepage_uses_the_cache(self):
        second_post = Post.objects.create(text="Obliviate",
                                          author=self.user,
                                          image=self.test_image)
        # first request
        self.authorized_user.get(reverse("posts:index"))
        second_post.delete()
        # second request
        response = self.authorized_user.get(reverse("posts:index"))
        self.assertEqual(len(response.context["page"].object_list), 2)
        cache.clear()
        # third request
        response = self.authorized_user.get(reverse("posts:index"))
        self.assertEqual(len(response.context["page"].object_list), 1)

    def test_group_page_show_correct_context(self):
        response = self.authorized_user.get(
            reverse("posts:post_in_group", kwargs={"slug": self.group.slug})
        )
        group = response.context["group"]
        post_object = response.context["page"].object_list[0]
        self.assertEqual(group.title, "Slytherin")
        self.assertEqual(group.description, "Draco dormiens nunquam "
                                            "titillandus!")
        self.assertEqual(group.slug, "slith")
        self.assertEqual(post_object.image, f"posts/{self.test_image}")

    def test_new_post_page_show_correct_context(self):
        """Check type of form field and
        inscriptions on new post page."""
        response = self.authorized_user.get(reverse("posts:new_post"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
            "image": forms.fields.ImageField
        }
        inscriptions = {"title": "Добавить запись",
                        "header": "Добавить запись",
                        "button": "Опубликовать"}
        # check fields
        for value, expected_field in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected_field)
        # check inscriptions
        for variable, expected_value in inscriptions.items():
            with self.subTest(value=value):
                value = response.context["inscriptions"][variable]
                self.assertEqual(value, expected_value)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_user.get(
            reverse("posts:profile", kwargs={"username": self.user.username})
        )
        post_object = response.context["page"].object_list[0]
        author = response.context["author"]
        self.assertEqual(post_object.text, "Avada Kedavra")
        self.assertEqual(post_object.image, f"posts/{self.test_image}")
        self.assertEqual(author.username, "DracoMalfoy")

    def test_post_page_show_correct_context(self):
        response = self.authorized_user.get(
            reverse("posts:post",
                    kwargs={"username": self.user.username,
                            "post_id": self.post_in_first_group.pk}, )
        )
        post_object = response.context["post"]
        author = response.context["author"]
        comment = response.context["comments"].first()
        self.assertEqual(post_object.text, "Avada Kedavra")
        self.assertEqual(post_object.image, f"posts/{self.test_image}")
        self.assertEqual(author.username, "DracoMalfoy")
        self.assertEqual(comment.text, "One ticket to Azkaban please")

    def test_edit_post_page_show_correct_context(self):
        """Check type of form field and
        inscriptions on edit post page"""
        response = self.authorized_user.get(
            reverse("posts:post_edit",
                    kwargs={"username": self.user.username,
                            "post_id": self.post_in_first_group.pk})
        )
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
            "image": forms.fields.ImageField
        }
        inscriptions = {"title": "Редактировать запись",
                        "header": "Редактировать запись",
                        "button": "Сохранить"}
        # check fields
        for value, expected_field in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected_field)
        # check inscriptions
        for variable, expected_value in inscriptions.items():
            with self.subTest(value=value):
                value = response.context["inscriptions"][variable]
                self.assertEqual(value, expected_value)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PaginatorViewsTest(TestCase):
    """Checking the operation of the paginator."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="Harry Potter")
        cls.follow_user = User.objects.create(username="Severus Snape")
        Follow.objects.create(user=cls.follow_user, author=cls.user)
        cls.group = Group.objects.create(
            title="Grifindor",
            description="We like Lions",
            slug="griff"
        )
        image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.test_image = SimpleUploadedFile(
            name="test.png",
            content=image,
            content_type="image/png"
        )
        cls.posts_list = Post.objects.bulk_create(
            [Post(text=f"Post №{i}", author=cls.user, pk=i,
                  group=cls.group, image=cls.test_image)
             for i in range(1, 14)]
        )

    def tearDown(self) -> None:
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.guest_user = Client()
        self.group = PaginatorViewsTest.group

    def test_home_page_contains_ten_and_three_records(self):
        num_of_posts_in_page = {10: reverse("posts:index"),
                                3: reverse("posts:index") + "?page=2"}
        for number, reverse_name in num_of_posts_in_page.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_user.get(reverse_name)
                self.assertEqual(
                    len(response.context['page'].object_list), number)

    def test_group_page_contains_ten_and_three_records(self):
        kwargs = {"slug": self.group.slug}
        reverse_name = reverse("posts:post_in_group", kwargs=kwargs)
        num_of_posts_in_page = {10: reverse_name,
                                3: reverse_name + "?page=2"}
        for number, reverse_name in num_of_posts_in_page.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_user.get(reverse_name)
                self.assertEqual(
                    len(response.context['page'].object_list), number)

    def test_profile_page_contains_ten_and_three_records(self):
        kwargs = {"username": PaginatorViewsTest.user.username}
        reverse_name = reverse("posts:profile", kwargs=kwargs)
        num_of_posts_in_page = {10: reverse_name,
                                3: reverse_name + "?page=2"}
        for number, reverse_name in num_of_posts_in_page.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_user.get(reverse_name)
                self.assertEqual(
                    len(response.context['page'].object_list), number)

    def test_profile_follow_page_contains_ten_and_three_records(self):
        authorized_user = Client()
        authorized_user.force_login(self.follow_user)
        reverse_name = reverse("posts:follow_index")
        num_of_posts_in_page = {10: reverse_name,
                                3: reverse_name + "?page=2"}
        for number, reverse_name in num_of_posts_in_page.items():
            with self.subTest(reverse_name=reverse_name):
                response = authorized_user.get(reverse_name)
                self.assertEqual(
                    len(response.context['page'].object_list), number)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CreatePostGroupTest(TestViewsSetUpClassMixin, TestCase):

    def setUp(self) -> None:
        self.first_group = CreatePostGroupTest.first_group
        self.post = CreatePostGroupTest.post_in_first_group
        self.guest_user = Client()
        # new post in second group
        self.second_group = Group.objects.create(
            title="Gryffindor",
            description="We like Lions",
            slug="griff"
        )
        self.post_in_second_group = Post.objects.create(
            text="Patronus",
            author=User.objects.create(username="Potter"),
            group=self.second_group
        )

    def tearDown(self) -> None:
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_located_in_page_of_group(self):
        """Post located in self group page."""
        response = self.guest_user.get(
            reverse("posts:post_in_group",
                    kwargs={"slug": self.second_group.slug})
        )
        self.assertIn(self.post_in_second_group,
                      response.context["page"].object_list)

    def test_post_with_group_located_in_homepage(self):
        """Post located in homepage"""
        response = self.guest_user.get(reverse("posts:index"))
        self.assertIn(self.post_in_second_group,
                      response.context["page"].object_list)

    def test_post_with_group_not_located_in_page_another_group(self):
        """Post not located in page another group."""
        response = self.guest_user.get(
            reverse("posts:post_in_group",
                    kwargs={"slug": self.first_group.slug})
        )
        self.assertNotIn(self.post_in_second_group,
                         response.context["page"].object_list)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CreateFollowTest(TestViewsSetUpClassMixin, TestCase):
    def setUp(self) -> None:
        # have follower follow_user1
        self.post = CreateFollowTest.post_in_first_group
        self.user = CreateFollowTest.user
        self.follow_user1 = CreateFollowTest.follow_user1
        self.follow_user2 = CreateFollowTest.follow_user2

    def tearDown(self) -> None:
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_located_in_page_index_of_follow_user(self):
        authorized_user = Client()
        authorized_user.force_login(self.follow_user1)
        response = authorized_user.get(reverse("posts:follow_index"))
        self.assertIn(self.post,
                      response.context["page"].object_list)

    def test_post_not_located_in_page_index_of_follow_user(self):
        authorized_user = Client()
        authorized_user.force_login(self.follow_user2)
        response = authorized_user.get(reverse("posts:follow_index"))
        self.assertNotIn(self.post,
                         response.context["page"].object_list)

    def test_user_follow_to_another_user(self):
        count_followers = self.user.following.count()
        authorized_user = Client()
        authorized_user.force_login(self.follow_user2)
        authorized_user.get(reverse("posts:profile_follow",
                                    kwargs={"username": self.user.username}))
        self.assertEqual(self.user.following.count(), count_followers + 1)
        self.assertTrue(
            self.user.following.filter(user=self.follow_user2).exists())

    def test_user_unfollow_from_another_user(self):
        count_followers = self.user.following.count()
        authorized_user = Client()
        authorized_user.force_login(self.follow_user1)
        authorized_user.get(reverse("posts:profile_unfollow",
                                    kwargs={"username": self.user.username}))
        self.assertEqual(self.user.following.count(), count_followers - 1)
        self.assertFalse(
            self.user.following.filter(user=self.follow_user1).exists())
