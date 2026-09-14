from django import forms
from django.contrib.auth.models import User
from .models import ServiceJob

class ServiceJobForm(forms.ModelForm):
    class Meta:
        model = ServiceJob
        # เพิ่ม 'status' เข้ามาใน fields
        fields = ['title', 'description', 'customer_name', 'customer_phone', 'technician', 'status', 'latitude', 'longitude']
        widgets = {
            'latitude': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control', 'id': 'id_latitude', 'placeholder': 'รอจิ้มแผนที่...'}),
            'longitude': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control', 'id': 'id_longitude', 'placeholder': 'รอจิ้มแผนที่...'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'เช่น แอร์ไม่เย็น, เครื่องซักผ้าปั่นไม่แห้ง'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'รายละเอียดเพิ่มเติม (ถ้ามี)'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อ-นามสกุล ลูกค้า'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '08X-XXX-XXXX'}),
            'technician': forms.Select(attrs={'class': 'form-select'}),
            # เพิ่ม dropdown สำหรับเปลี่ยนสถานะ
            'status': forms.Select(attrs={'class': 'form-select'}), 
        }

    def __init__(self, *args, **kwargs):
        super(ServiceJobForm, self).__init__(*args, **kwargs)
        # กรองเอาเฉพาะ User ที่ไม่ใช่ Admin (ดึงมาแค่ Member)
        self.fields['technician'].queryset = User.objects.filter(is_staff=False, is_superuser=False)


# ฟอร์มใหม่สำหรับช่างใช้ส่งงาน (อัปโหลดรูปภาพและหมายเหตุ)
class JobSubmitForm(forms.ModelForm):
    class Meta:
        model = ServiceJob
        fields = ['completion_image', 'completion_note']
        widgets = {
            'completion_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'completion_note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'อธิบายรายละเอียดการซ่อม หรืออะไหล่ที่เปลี่ยน...'}),
        }