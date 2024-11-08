from django.http import Http404
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count

from .models import Post, Category, Comment
from .forms import CommentForm, PostForm, UserUdateForm
from .utils import posts_query_set


User = get_user_model()

COUNT_POSTS_PER_PAGE = 10


class PaginateListViewMixin(ListView):
    paginate_by = COUNT_POSTS_PER_PAGE


class UserVerification(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return (
            self.request.user.username == obj.author.username
        )

    def handle_no_permission(self):
        raise Http404


class CategoryListView(PaginateListViewMixin):
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


class PostListView(PaginateListViewMixin):
    model = Post
    template_name = 'blog/index.html'

    def get_queryset(self):
        queryset = posts_query_set().filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
        return queryset


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
    form_class = UserUdateForm
    exclude = ('password',)
    password = None
    template_name = 'blog/user.html'

    def get_object(self):
        """Получем объект, поля которого надо изменить."""
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class UserListView(PaginateListViewMixin):
    model = Post
    template_name = 'blog/profile.html'
    slug_url_kwarg, slug_field = 'username', 'username'
    context_object_name = 'page_obj'

    def get_queryset(self):
        if self.request.user.username == self.kwargs['username']:
            queryset = posts_query_set().filter(
                author__username=self.kwargs['username']
            ).annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
        else:
            queryset = posts_query_set().filter(
                author__username=self.kwargs['username'],
                is_published=True
            ).annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
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


class CommentUpdateView(LoginRequiredMixin,
                        UserVerification,
                        UpdateView):
    model = Comment
    fields = ('text',)
    template_name = 'blog/comment.html'


class CommentDeleteView(LoginRequiredMixin,
                        UserVerification,
                        DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_id = get_object_or_404(Post, pk=kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

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


class PostUpdateView(LoginRequiredMixin, UserVerification, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def handle_no_permission(self):
        return redirect('blog:post_detail', pk=self.kwargs['pk'])


class PostDeleteView(LoginRequiredMixin, UserVerification, DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.instance)
        return context

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )
