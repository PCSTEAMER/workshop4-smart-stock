from django.db import models

class SparePart(models.Model):
    CATEGORY_CHOICES = (
        ('IC', 'ไอซี/แผงวงจร (IC/Board)'),
        ('SENSOR', 'เซ็นเซอร์ (Sensor)'),
        ('SWITCH', 'สวิตช์/เบรกเกอร์ (Switch/Breaker)'),
        ('RELAY', 'รีเลย์ (Relay)'),
        ('CABLE', 'สายไฟ/อุปกรณ์เชื่อมต่อ (Cable/Connector)'),
        ('OTHER', 'อื่นๆ (Others)'),
    )

    part_code = models.CharField(max_length=50, unique=True, verbose_name="รหัสสินค้า (SKU)")
    name = models.CharField(max_length=200, verbose_name="ชื่ออะไหล่")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="หมวดหมู่")
    quantity = models.PositiveIntegerField(default=0, verbose_name="จำนวนคงเหลือ (ชิ้น)")
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name="ตำแหน่งจัดเก็บ (เช่น ตู้ A ชั้น 2)")
    import_date = models.DateField(verbose_name="วันที่นำเข้าล่าสุด")
    specifications = models.TextField(blank=True, verbose_name="สเปกและรายละเอียดทางเทคนิค")
    image = models.ImageField(upload_to='parts/', blank=True, null=True, verbose_name="รูปภาพอะไหล่")

    def __str__(self):
        return f"[{self.part_code}] {self.name}"

class Transaction(models.Model):
    ACTION_CHOICES = (
        ('IN', 'นำเข้า (Stock In)'),
        ('OUT', 'เบิกออก (Stock Out)'),
    )
    
    part = models.ForeignKey(SparePart, on_delete=models.CASCADE, verbose_name="อะไหล่")
    action_type = models.CharField(max_length=3, choices=ACTION_CHOICES, verbose_name="ประเภทรายการ")
    quantity = models.PositiveIntegerField(verbose_name="จำนวน")
    
    # ใช้ CharField รับชื่อคนพิมพ์ไปก่อนชั่วคราวในช่วงที่ยังไม่มีระบบ Login
    action_by = models.CharField(max_length=100, verbose_name="ผู้ทำรายการ/ผู้เบิก")
    
    note = models.TextField(blank=True, verbose_name="หมายเหตุ (เช่น ซ่อมพัดลมให้ลูกค้า)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วัน-เวลาที่ทำรายการ")

    def __str__(self):
        return f"{self.action_type} - {self.part.name} ({self.quantity} ชิ้น)"