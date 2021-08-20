from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import Post, Group, Comment, Follow


class PostGroupCommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        cls.user = User.objects.create(username="Obi Van")
        cls.post = Post.objects.create(
            text="some text about something, "
                 "and about nothing.",
            author=cls.user
        )

        cls.group = Group.objects.create(
            title="Some name for some group",
            slug="something123456",
            description="In this place can be your information"
        )
        cls.comment = Comment.objects.create(
            text="This is bullshit, i am darklord.",
            author=User.objects.create(username="Anakin"),
            post=cls.post
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=User.objects.create(username="Yoda")
        )

    def test_object_name_matches_the_expected_one(self):
        post = self.post
        group = self.group
        comment = self.comment
        follow = self.follow
        follow_expected_name = "Подписчик Obi Van, подписан на Yoda"
        objects_expected_name = {post: post.text[:15],
                                 group: group.title,
                                 comment: comment.text[:15],
                                 follow: follow_expected_name}
        for object, expected_object_name in objects_expected_name.items():
            with self.subTest(object=object):
                self.assertEqual(expected_object_name, str(object),
                                 "Wrong name of object, check __str__ method")
