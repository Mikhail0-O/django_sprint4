from typing import Any
from django.db.models.query import QuerySet
from django.http import Http404
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Post, Category, Comment
from .forms import CommentForm, PostForm, UserForm
from .utils import posts_query_set


User = get_user_model()

COUNT_POSTS_PER_PAGE = 10


class CategoryListView(ListView):
    paginate_by = COUNT_POSTS_PER_PAGE
    model = Category
    template_name = 'blog/category.html'
    slug_url_kwarg, slug_field = 'slug', 'slug'

    def get_queryset(self):
        queryset = posts_query_set().filter(
            category__slug=self.kwargs['slug'],
            is_published=True,
            pub_date__lte=timezone.now(),
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(
            Category.objects.filter(
                slug=self.kwargs['slug'],
                is_published=True
            )
        )
        context['category'] = category
        return context


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    ordering = '-pub_date'
    paginate_by = COUNT_POSTS_PER_PAGE

    def get_queryset(self):
        queryset = posts_query_set().filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),)
        return queryset

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     page_obj = posts_query_set().filter(
    #         is_published=True,
    #         category__is_published=True,
    #         pub_date__lte=timezone.now(),)
        # paginator = Paginator(page_obj, COUNT_POSTS_PER_PAGE)
        # page_number = self.request.GET.get('page')
        # try:
        #     page_obj = paginator.page(page_number)
        # except PageNotAnInteger:
        #     page_obj = paginator.page(1)
        # except EmptyPage:
        #     page_obj = paginator.page(paginator.num_pages)

        # context['page_obj'] = page_obj
        # return context


class PostDetailView(UserPassesTestMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def test_func(self):
        post = self.get_object()
        return (
            (post.is_published
             and post.category.is_published
             and post.pub_date <= timezone.now())
            or self.request.user == post.author
        )

    def handle_no_permission(self):
        raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self):
        """Получем объект, поля которого надо изменить."""
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class UserListView(ListView):
    model = Post
    paginate_by = COUNT_POSTS_PER_PAGE
    template_name = 'blog/profile.html'
    slug_url_kwarg, slug_field = 'username', 'username'
    context_object_name = 'page_obj'

    def get_queryset(self):
        queryset = posts_query_set().filter(
            author__username=self.kwargs['username']
        )
        print(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User.objects.filter(
                username=self.kwargs['username']
            )
        )
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_id = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.post_id.id
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.post_id.id
        return reverse('blog:post_detail', kwargs={'pk': pk})


class CommentUpdateView(UserPassesTestMixin, UpdateView):
    model = Comment
    fields = ('text',)
    template_name = 'blog/comment.html'

    def test_func(self):
        comment = self.get_object()
        return (
            self.request.user.is_authenticated
            and self.request.user.username == comment.author.username
        )

    def handle_no_permission(self):
        raise Http404


class CommentDeleteView(UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_id = get_object_or_404(Post, pk=kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        comment = self.get_object()
        return (
            self.request.user.is_authenticated
            and self.request.user.username == comment.author.username
        )

    def handle_no_permission(self):
        raise Http404

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post_id.id})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        post = self.get_object()
        if post.author != self.request.user:
            return redirect('blog:post_detail', pk=post.id)
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.request.user == self.instance.author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.instance)
        return context

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )
