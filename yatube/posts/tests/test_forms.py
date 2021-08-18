import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from ..models import Post, Group, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()

class TestFormsSetUpClassMixin:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="DracoMalfoy")
        cls.another_user = User.objects.create(username="Potter")
        cls.group = Group.objects.create(
            title="Slytherin",
            description="We like snakes",
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
        cls.post = Post.objects.create(text="I hate Potter",
                                       author=cls.user)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateEditFormTest(TestFormsSetUpClassMixin, TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_new_post_form_create_database_entry(self):
        post_count = Post.objects.count()
        form_data = {
            "text": "Avada Kedavra",
            "group": self.group.id,
            "image": self.test_image
        }
        response = self.authorized_user.post(
            reverse("posts:new_post"),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertRedirects(response, reverse("posts:index"))
        self.assertTrue(Post.objects.filter(
            text="Avada Kedavra",
            group=self.group.id,
            author=self.user,
            image=f"posts/{self.test_image}"
        ).exists())

    def test_edit_post_form_change_database_entry(self):
        post_count = Post.objects.count()
        expected_reverse = reverse("posts:post",
                                   kwargs={"username": self.user.username,
                                           "post_id": self.post.pk})
        form_data = {
            "text": "I hate Harry Potter and Hermione",
            "group": self.group.id
        }
        response = self.authorized_user.post(
            reverse("posts:post_edit",
                    kwargs={"username": self.user.username,
                            "post_id": self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertRedirects(response, expected_reverse)
        self.assertTrue(Post.objects.filter(
            text="I hate Harry Potter and Hermione",
            group=self.group.id,
            pk=self.post.pk,
            author=self.user
        ).exists())


class CommentFormTest(TestFormsSetUpClassMixin, TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.authorized_user = Client()
        self.authorized_user.force_login(self.another_user)

    def test_comment_form_create_database_entry(self):
        comment_count = Comment.objects.count()
        form_data = {
            "text": "Sectumsempra",
        }
        kwargs = {"username": self.user.username,
                  "post_id": self.post.pk}
        response = self.authorized_user.post(
            reverse("posts:post", kwargs=kwargs),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertRedirects(response, reverse("posts:post",
                                               kwargs=kwargs))
        self.assertTrue(Comment.objects.filter(
            text="Sectumsempra",
            author=self.another_user,
            post=self.post
        ))
