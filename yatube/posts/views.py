from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

from .utils import _get_pages
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


def index(request):
    post_list = cache.get("index_page")
    if post_list is None:
        post_list = Post.objects.all()
        cache.set("index_page", post_list, timeout=20)
    page = _get_pages(request, post_list)
    return render(request, "posts/index.html", {"page": page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page = _get_pages(request, posts)
    context = {"group": group,
               "page": page}
    return render(request, "posts/group.html", context)


def profile(request, username: str):
    author = get_object_or_404(User, username=username)
    user = request.user
    posts = author.posts.all()
    page = _get_pages(request, posts)
    following = (user.is_authenticated and
                 Follow.objects.filter(user=user, author=author).exists())
    context = {"author": author,
               "page": page,
               "following": following}
    return render(request, 'posts/profile.html', context)


def post_view(request, username: str, post_id: int):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm()
    following = (request.user.is_authenticated and
                 post.author.following.filter(user=request.user).exists())
    context = {"author": post.author,
               "post": post,
               "comments": post.comments.all(),
               "form": form,
               "following": following}
    return render(request, 'posts/post.html', context)


@login_required
def post_edit(request, username: str, post_id: int):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    if post.author != request.user:
        return redirect("posts:post", username=username, post_id=post_id)

    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)

    if form.is_valid():
        form.save()
        return redirect("posts:post", username=username, post_id=post_id)

    context = {"form": form,
               "post": post,
               "inscriptions": {"title": "Редактировать запись",
                                "header": "Редактировать запись",
                                "button": "Сохранить"}
               }
    return render(request, 'posts/newpost.html', context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.save()
            return redirect("posts:index")

    context = {"form": form,
               "inscriptions": {"title": "Добавить запись",
                                "header": "Добавить запись",
                                "button": "Опубликовать"}}
    return render(request, "posts/newpost.html", context)


@login_required
def add_comment(request, username: str, post_id: int):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect("posts:post", username=username, post_id=post_id)
    return render(request, "posts/includes/comments.html",
                  {"form": form,
                   "post": post})


@login_required
def follow_index(request):
    posts_list = Post.objects.filter(author__following__user=request.user)
    posts_list.order_by("-pub_date")
    page = _get_pages(request, posts_list)
    return render(request, "posts/follow.html", {"page": page})


@login_required
def profile_follow(request, username: str):
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username: str):
    user = request.user
    follow = get_object_or_404(Follow, user=user, author__username=username)
    follow.delete()
    return redirect("posts:profile", username=username)
