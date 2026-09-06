from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
import openpyxl
from .models import SparePart, Transaction
from .forms import SparePartForm, TransactionForm

def is_staff_user(user):
    return user.is_authenticated and user.is_staff

# 1. หน้าแสดงรายการอะไหล่ (เรียงตามลำดับแรก -> ล่าสุดต่อท้าย)
def part_list(request):
    query = request.GET.get('q', '')
    if query:
        parts_list = SparePart.objects.filter(
            Q(part_code__icontains=query) | Q(name__icontains=query)
        ).order_by('id')
    else:
        parts_list = SparePart.objects.all().order_by('id')

    paginator = Paginator(parts_list, 5)
    page_number = request.GET.get('page')
    parts = paginator.get_page(page_number)

    return render(request, 'part_list.html', {'parts': parts, 'query': query})

# 2. หน้าเพิ่มข้อมูล
@login_required(login_url='accounts:login')
@user_passes_test(is_staff_user, login_url='part_list')
def part_create(request):
    if request.method == 'POST':
        form = SparePartForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'เพิ่มอะไหล่สำเร็จ')
            return redirect('part_list')
    else:
        form = SparePartForm()
    return render(request, 'part_form.html', {'form': form})

# 3. หน้าแก้ไขข้อมูล
@login_required(login_url='accounts:login')
@user_passes_test(is_staff_user, login_url='part_list')
def part_update(request, pk):
    part = get_object_or_404(SparePart, pk=pk)
    if request.method == 'POST':
        form = SparePartForm(request.POST, request.FILES, instance=part)
        if form.is_valid():
            form.save()
            messages.success(request, 'แก้ไขข้อมูลสำเร็จ')
            return redirect('part_list')
    else:
        form = SparePartForm(instance=part)
    return render(request, 'part_form.html', {'form': form, 'part': part})

# 4. หน้าลบข้อมูล
@login_required(login_url='accounts:login')
@user_passes_test(is_staff_user, login_url='part_list')
def part_delete(request, pk):
    part = get_object_or_404(SparePart, pk=pk)
    if request.method == 'POST':
        part.delete()
        messages.success(request, 'ลบข้อมูลสำเร็จ')
        return redirect('part_list')
    return render(request, 'part_confirm_delete.html', {'part': part})

# 5. หน้าบันทึกเบิก-จ่าย
@login_required(login_url='accounts:login')
def transaction_create(request):
    part_id = request.GET.get('part_id')
    selected_part = None
    if part_id:
        selected_part = get_object_or_404(SparePart, pk=part_id)

    full_name = request.user.get_full_name().strip()
    user_display = full_name if full_name else request.user.username

    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            part = transaction.part
            
            if transaction.action_type == 'IN':
                part.quantity += transaction.quantity
            elif transaction.action_type == 'OUT':
                if part.quantity >= transaction.quantity:
                    part.quantity -= transaction.quantity
                else:
                    form.add_error('quantity', f'สินค้าไม่พอ! (คงเหลือในคลัง {part.quantity} ชิ้น)')
                    return render(request, 'transaction_form.html', {
                        'form': form,
                        'selected_part': part
                    })
            
            if not transaction.action_by:
                transaction.action_by = user_display

            part.save()
            transaction.save()
            messages.success(request, f'บันทึกรายการ {transaction.get_action_type_display()} เรียบร้อยแล้ว')
            return redirect('transaction_history')
    else:
        initial_data = {
            'action_by': user_display
        }
        if selected_part:
            initial_data['part'] = selected_part
            
        form = TransactionForm(initial=initial_data)

    return render(request, 'transaction_form.html', {
        'form': form, 
        'selected_part': selected_part
    })

# 6. หน้าดูประวัติ (เรียงตามวันเวลาที่ทำรายการ อันแรก -> รายการใหม่ต่อท้าย)
@login_required(login_url='accounts:login')
def transaction_history(request):
    if request.user.is_superuser or request.user.is_staff:
        transactions = Transaction.objects.all().order_by('created_at')
    else:
        full_name = request.user.get_full_name().strip()
        user_names = [request.user.username]
        if full_name:
            user_names.append(full_name)
            
        transactions = Transaction.objects.filter(action_by__in=user_names).order_by('created_at')
        
    return render(request, 'transaction_history.html', {'transactions': transactions})

# 7. ส่งออก Excel (เรียงลำดับตรงกับหน้าเว็บ)
@login_required(login_url='accounts:login')
def export_transactions_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Transaction History"

    headers = ["ID", "ประเภทรายการ", "ชื่ออะไหล่", "รหัส SKU", "จำนวน", "ผู้เบิก", "หมายเหตุ", "วัน-เวลาที่ทำรายการ"]
    ws.append(headers)

    if request.user.is_superuser or request.user.is_staff:
        transactions = Transaction.objects.all().order_by('created_at')
    else:
        full_name = request.user.get_full_name().strip()
        user_names = [request.user.username]
        if full_name:
            user_names.append(full_name)
            
        transactions = Transaction.objects.filter(action_by__in=user_names).order_by('created_at')

    for tx in transactions:
        ws.append([
            tx.id,
            tx.get_action_type_display(),
            tx.part.name,
            tx.part.part_code,
            tx.quantity,
            tx.action_by,
            tx.note,
            tx.created_at.strftime('%d/%m/%Y %H:%M:%S') if tx.created_at else ''
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=transaction_history.xlsx'
    
    wb.save(response)
    return response