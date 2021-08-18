from django.core.paginator import Paginator, Page
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from .models import Post, Group, User
from .forms import PostForm, CommentForm


def _get_pages(request, page_list: object, num_page: int) -> Page:
    paginator = Paginator(page_list, num_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


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
    page = _get_pages(request, post_list, 10)
    return render(request, "index.html", {"page": page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page = _get_pages(request, posts, 10)
    context = {"group": group,
               "page": page}
    return render(request, "group.html", context)


def profile(request, username: str):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page = _get_pages(request, posts, 10)
    context = {"author": author,
               "page": page}
    return render(request, 'profile.html', context)


def post_view(request, username: str, post_id: int):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.post = post
        form.save()
        return redirect("posts:post", username=username, post_id=post_id)
    context = {"author": post.author,
               "post": post,
               "comments": post.comments.all(),
               "form": form}
    return render(request, 'post.html', context)


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
               "inscriptions": {"title": "Редактировать запись",
                                "header": "Редактировать запись",
                                "button": "Сохранить"}
               }
    return render(request, 'newpost.html', context)


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
    return render(request, "newpost.html", context)


@login_required
def follow_index(request):
    pass

@login_required
def profile_follow(request):
    pass

@login_required
def profile_unfollow(request):
    pass
