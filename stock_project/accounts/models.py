from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # ข้อมูลเสริม
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="เบอร์โทรศัพท์")
    
    # บทบาทสิทธิ์ (Roles)
    ROLE_CHOICES = (
        ('admin', 'ผู้ดูแลระบบ (Admin)'),
        ('member', 'ช่างซ่อม/พนักงาน (Member)'),
        ('guest', 'ผู้เยี่ยมชม (Guest)'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest', verbose_name="บทบาท")
    
    # สถานะการอนุมัติและการจัดการ
    APPROVAL_STATUS = (
        ('pending', 'รออนุมัติ'),
        ('approved', 'อนุมัติแล้ว'),
        ('rejected', 'ไม่อนุมัติ'),
        ('suspended', 'ระงับการใช้งาน'),
    )
    status = models.CharField(max_length=15, choices=APPROVAL_STATUS, default='pending', verbose_name="สถานะบัญชี")
    
    # เก็บเหตุผลกรณีไม่อนุมัติ (Two-way Feedback)
    rejection_reason = models.TextField(blank=True, null=True, verbose_name="เหตุผล/หมายเหตุจากแอดมิน")
    
    # เก็บประวัติ Audit Log เล็กๆ ว่าใครเป็นคนอนุมัติ/จัดการล่าสุด
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approvals_made', verbose_name="ผู้ดำเนินการล่าสุด")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="อัปเดตล่าสุดเมื่อ")

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()}) - [{self.get_status_display()}]"

# --- Signal: สร้าง UserProfile อัตโนมัติเมื่อมีการสมัคร User ใหม่ ---
# superuser (สร้างผ่าน createsuperuser) ต้องได้สถานะ approved ทันที
# ไม่งั้นจะโดนหน้า login เด้งกลับว่า "รออนุมัติ" เหมือนสมาชิกทั่วไปที่เพิ่งสมัคร
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            UserProfile.objects.create(user=instance, status='approved', role='admin')
        else:
            UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()