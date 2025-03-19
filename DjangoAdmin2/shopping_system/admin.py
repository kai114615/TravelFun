from django.contrib import admin
from .models import Product, CategoryDisplay, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'shipping_name', 'total_amount', 'status', 'payment_method', 'logistics_status', 'created_at']
    list_filter = ['status', 'payment_method', 'logistics_status', 'created_at']
    search_fields = ['order_number', 'shipping_name', 'shipping_phone', 'shipping_address']
    readonly_fields = ['order_number', 'total_amount', 'created_at', 'updated_at']
    fieldsets = (
        ('訂單基本資訊', {
            'fields': ('order_number', 'user', 'total_amount', 'status', 'payment_method')
        }),
        ('物流資訊', {
            'fields': ('shipping_method', 'logistics_id', 'logistics_status', 'logistics_info')
        }),
        ('收件人資訊', {
            'fields': ('shipping_name', 'shipping_phone', 'shipping_address', 'shipping_note')
        }),
        ('時間資訊', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    inlines = [OrderItemInline]
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        # 禁止從管理後台手動新增訂單
        return False
    
    def has_delete_permission(self, request, obj=None):
        # 防止訂單被意外刪除，只能變更狀態為取消
        return False

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock', 'is_active']

@admin.register(CategoryDisplay)
class CategoryDisplayAdmin(admin.ModelAdmin):
    list_display = ['category', 'order', 'is_active', 'description']
    search_fields = ['category', 'description']
    list_editable = ['order', 'is_active'] 