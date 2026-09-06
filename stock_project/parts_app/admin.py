from django.contrib import admin
from .models import SparePart, Transaction

# Register your models here.

# จดทะเบียนตาราง SparePart (แบบจัดหน้าตาสวยงาม)
@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = ('part_code', 'name', 'category', 'quantity', 'import_date') # คอลัมน์ที่จะโชว์
    search_fields = ('part_code', 'name') # ให้มีช่องค้นหาจากรหัสและชื่อ
    list_filter = ('category',) # ให้มีเมนูกรองตามหมวดหมู่ด้านขวา

# จดทะเบียนตาราง Transaction ใหม่!
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('part', 'action_type', 'quantity', 'action_by', 'created_at')
    search_fields = ('part__name', 'action_by') # ค้นหาจากชื่ออะไหล่ และชื่อคนเบิก
    list_filter = ('action_type', 'created_at') # กรองดูเฉพาะ นำเข้า/เบิกออก ได้