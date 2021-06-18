import admin_thumbnails
from django.contrib import admin
from django.contrib.admin import ModelAdmin

from product.models import Category, Product, Images, Comment, Color, Size, Variants, Promotion


class CategoryAdmin(ModelAdmin):
    list_display = ('title', 'related_products_count')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)

    def related_products_count(self, instance):
        product_qty = Product.objects.filter(category=instance).count()
        return product_qty
    related_products_count.short_description = 'Related products (for this specific category)'


@admin_thumbnails.thumbnail('image')
class ProductImageInline(admin.TabularInline):
    model = Images
    readonly_fields = ('id',)
    extra = 1


class ProductVariantsInline(admin.TabularInline):
    model = Variants
    extra = 1
    show_change_link = True
    
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_staff and not request.user.is_superuser:
            group = request.user.groups.all()[0].name
            if group:
                if group == 'warehouse_staff':
                    return ['image_tag', 'price']
                elif group == 'business_staff':
                    return ['image_tag', 'price_in', 'quantity', 'image_id', 'size', 'color']
        elif request.user.is_superuser:
            return []


@admin_thumbnails.thumbnail('image')
class ImagesAdmin(admin.ModelAdmin):
    list_display = ['image', 'title', 'image_thumbnail']


class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'image_tag']
    list_filter = ['category']
    # readonly_fields = ('image_tag', )
    inlines = [ProductImageInline, ProductVariantsInline]
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)
    actions = ['public_pro', 'hide_pro', ]
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_staff and not request.user.is_superuser:
            group = request.user.groups.all()[0].name
            if group:
                if group == 'warehouse_staff':
                    return ['status', 'price']
                elif group == 'business_staff':
                    return ['image_tag', 'category', 'keywords', 'description', 'image', 'price_in', 'amount', 'minamount', 'variant', 'detail']
        elif request.user.is_superuser:
            return []
    
    @admin.action(description='Public order')
    def public_pro(self, request, queryset):
        for product in queryset:
            if product.status == 'False':
                product.status = 'True'
                product.save()
                
    @admin.action(description='Hide order')
    def hide_pro(self, request, queryset):
        for product in queryset:
            if product.status == 'True':
                product.status = 'False'
                product.save()


class CommentAdmin(admin.ModelAdmin):
    list_display = ['subject', 'comment', 'status', 'create_at']
    list_filter = ['status']
    readonly_fields = ('subject', 'comment', 'ip',
                       'user', 'product', 'rate', 'id')


class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'color_tag']


class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']


class VariantsAdmin(admin.ModelAdmin):
    list_display = ['title', 'product', 'color',
                    'size', 'price_in','price', 'quantity', 'image_tag']
    
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser is False:
            group = request.user.groups.all()[0].name
            if group:
                if group == 'warehouse_staff':
                    return ['image_tag', 'price']
                elif group == 'business_staff':
                    return ['image_tag', 'price_in', 'quantity', 'image_id', 'size', 'color']
        else:
            return []

class PromotionAdmin(admin.ModelAdmin):
    list_display = ['product', 'percent']
    

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Images, ImagesAdmin)
admin.site.register(Color, ColorAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Variants, VariantsAdmin)
admin.site.register(Promotion, PromotionAdmin)
