from django.contrib import admin

from .models import Post, Category, Location


class PostAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at'
    ]
    
    list_editable = (
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_per_page = 3

    fields = ['title', ('text', 'pub_date'), (
        'author', 'location',
        'category', 'is_published',)]

    class Media:
        css = {
            'all': ('css/custom_changelists.css',)
        }


class PostInline(admin.StackedInline):
    model = Post
    extra = 1


class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
        'created_at'
    )
    list_editable = (
        'description',
        'slug',
        'is_published',
    )
    search_fields = ('title',)
    list_filter = ('created_at',)
    list_per_page = 3


class LocationAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )

    list_display = (
        'name',
        'is_published',
        'created_at'
    )

    list_editable = (
        'is_published',
    )

    search_fields = ('name',)
    list_filter = ('created_at',)


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)

admin.site.empty_value_display = 'Пусто'

admin.site.site_header = 'Администрирование сайта Блогикум'
admin.site.site_title = 'Блогикум'
admin.site.index_title = 'Администрирование'
