from django.utils import timezone

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView)
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Post, Category, Comment
from .forms import UserForm, CommentForm, PostForm


COUNT_POSTS = 5

User = get_user_model()


def category_posts(request, category_slug):
    template_name = 'blog/category.html'

    one_category = get_object_or_404(
        Category.objects.filter(
            is_published=True,
        ),
        slug=category_slug,
    )

    page_obj = posts_query_set().filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category=one_category,
    )

    context = {'page_obj': page_obj,
               'category': one_category}
    return render(request, template_name, context)


# def posts_ready_for_publication():
#     return (Q(is_published=True)
#             & Q(category__is_published=True)
#             & Q(pub_date__lte=timezone.now()))


def posts_query_set():
    return (Post.objects.select_related(
        'location',
        'category',
        'author',
    ))


# через view-функцию
# def profile(request, username):
#     template_name = 'blog/profile.html'
#     # print(User.objects.get())
#     profile = User.objects.get(username=username)
#     print(profile.email)
#     print(User)
#     print(request.user)
#     context = {'profile': profile}
#     # post_list = posts_query_set().filter(
#     #     posts_ready_for_publication(),
#     # )[:COUNT_POSTS]

#     # context = {'post_list': post_list}
#     return render(request, template_name, context)


class PostListView(ListView):
    model = Post
    queryset = Post.objects.select_related(
        'location',
        'category',
        'author',
    ).filter(Q(is_published=True)
             & Q(category__is_published=True)
             & Q(pub_date__lte=timezone.now()))
    template_name = 'blog/index.html'
    ordering = '-pub_date'
    paginate_by = 10


class PostDetailView(DetailView):
    model = Post
    queryset = Post.objects.select_related(
        'location',
        'category',
        'author',
    )
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Записываем в переменную form пустой объект формы.
        context['form'] = CommentForm()
        # Запрашиваем все поздравления для выбранного дня рождения.
        context['comments'] = (
            # Дополнительно подгружаем авторов комментариев,
            # чтобы избежать множества запросов к БД.
            self.object.comments.select_related('author')
        )
        return context


class UserUpdateView(UpdateView):
    model = User
    fields = ('username', 'first_name', 'last_name', 'email')
    template_name = 'blog/user.html'

    def get_object(self):
        """Получем объект, поля которого надо изменить."""
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class UserDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    slug_url_kwarg, slug_field = 'username', 'username'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_obj = Post.objects.select_related(
            'location',
            'category',
            'author',
        ).filter(author__username=self.request.user.username)
        context['page_obj'] = page_obj
        # context['page_obj'] = (
        #     self.object.posts.select_related('author')
        # )
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


class CommentUpdateView(UpdateView):
    model = Comment
    fields = ('text',)
    template_name = 'blog/comment.html'


class CommentDeleteView(DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_id = get_object_or_404(Post, pk=kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post_id.id})


# class UserDetailView(DetailView):
#     model = Post
#     template_name = 'blog/profile.html'
#     slug_url_kwarg, slug_field = 'author', 'author'
#     context_object_name = 'profile'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['page_obj'] = (
#             self.object.posts.select_related('author')
#         )
#         return context
