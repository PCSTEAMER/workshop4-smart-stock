from django import forms
from .models import SparePart, Transaction

class SparePartForm(forms.ModelForm):
    class Meta:
        model = SparePart
        fields = ['part_code', 'name', 'category', 'quantity','location', 'import_date', 'specifications', 'image']
        widgets = {
            'part_code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'เช่น ตู้ A ชั้น 2'}), 
            'import_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'specifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ถ้าระบบตรวจพบว่าเป็นการแก้ไข (มีข้อมูลเดิมอยู่แล้ว) ให้ล็อคช่องจำนวน
        if self.instance.pk: 
            self.fields['quantity'].widget.attrs['readonly'] = 'readonly'
            self.fields['quantity'].widget.attrs['class'] += ' bg-light text-muted'

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['part', 'action_type', 'quantity', 'action_by', 'note']
        widgets = {
            'part': forms.Select(attrs={'class': 'form-select'}),
            'action_type': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'action_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'เช่น นายสมชาย ช่างซ่อมบำรุง'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'เช่น เบิกไปซ่อมแอร์ห้อง 101'}),
        }