from blog.models import Post


def posts_query_set():
    return (Post.objects.select_related(
        'location',
        'category',
        'author',
    ))