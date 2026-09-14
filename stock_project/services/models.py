from django.db import models
from django.contrib.auth.models import User

class ServiceJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'รอดำเนินการ'),
        ('in_progress', 'กำลังซ่อม'),
        ('pending_approval', 'ส่งงานแล้ว (รอตรวจสอบ)'), # เพิ่มสถานะใหม่
        ('completed', 'เสร็จสิ้น'),
        ('cancelled', 'ยกเลิก'),
    ]

    title = models.CharField(max_length=200, verbose_name="ชื่องาน/อาการเสีย")
    description = models.TextField(blank=True, verbose_name="รายละเอียดเพิ่มเติม")
    customer_name = models.CharField(max_length=100, verbose_name="ชื่อลูกค้า")
    customer_phone = models.CharField(max_length=20, verbose_name="เบอร์ติดต่อ")
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='assigned_jobs', verbose_name="ช่างผู้รับผิดชอบ")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="สถานะงาน")
    latitude = models.FloatField(null=True, blank=True, verbose_name="ละติจูด")
    longitude = models.FloatField(null=True, blank=True, verbose_name="ลองจิจูด")
    
    # เพิ่ม 2 ช่องใหม่สำหรับช่างส่งงาน
    completion_image = models.ImageField(upload_to='service_completions/', null=True, blank=True, verbose_name="รูปภาพส่งงาน")
    completion_note = models.TextField(blank=True, verbose_name="หมายเหตุการส่งงาน")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่รับงาน")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="อัปเดตล่าสุด")

    def __str__(self):
        return f"{self.title} ({self.customer_name})"