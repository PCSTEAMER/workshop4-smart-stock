from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .forms import ServiceJobForm
from django.contrib.auth.decorators import login_required
from .models import ServiceJob
from django.shortcuts import render, redirect, get_object_or_404 # ดึง get_object_or_404 มาใช้
from .forms import ServiceJobForm, JobSubmitForm # import JobSubmitForm ด้านบน

# หน้าสร้างใบงานซ่อม (เข้าได้เฉพาะแอดมิน)
@staff_member_required(login_url='accounts:login')
def create_service_job(request):
    if request.method == 'POST':
        form = ServiceJobForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'บันทึกใบงานและปักหมุดแผนที่สำเร็จ!')
            return redirect('services:job_list') # เด้งมาหน้าตารางงานซ่อม
    else:
        form = ServiceJobForm()
        
    return render(request, 'services/create_job.html', {'form': form})

@login_required(login_url='accounts:login')
def job_list(request):
    if request.user.is_superuser or request.user.is_staff:
        # แอดมินเห็นงานของทุกคน แต่ซ่อนงานที่เสร็จแล้ว (completed) ออก
        jobs = ServiceJob.objects.exclude(status='completed').order_by('-created_at')
    else:
        # ช่างเห็นเฉพาะงานของตัวเอง และซ่อนงานที่เสร็จแล้วออก
        jobs = ServiceJob.objects.filter(technician=request.user).exclude(status='completed').order_by('-created_at')
        
    return render(request, 'services/job_list.html', {'jobs': jobs})

# หน้าแก้ไขใบงานซ่อม
@staff_member_required(login_url='accounts:login')
def edit_service_job(request, job_id):
    job = get_object_or_404(ServiceJob, id=job_id)
    
    if request.method == 'POST':
        form = ServiceJobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'อัปเดตข้อมูลใบงานสำเร็จ!')
            return redirect('services:job_list')
    else:
        form = ServiceJobForm(instance=job)
        
    return render(request, 'services/edit_job.html', {'form': form, 'job': job})

# หน้าสำหรับช่างกดส่งงาน
@login_required(login_url='accounts:login')
def submit_service_job(request, job_id):
    # ดึงงานมา โดยเช็คให้ช่างที่รับผิดชอบเท่านั้นที่ส่งงานนี้ได้
    job = get_object_or_404(ServiceJob, id=job_id, technician=request.user)
    
    if request.method == 'POST':
        # ใช้ request.FILES เพื่อรับไฟล์รูปภาพ
        form = JobSubmitForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            job_instance = form.save(commit=False)
            job_instance.status = 'pending_approval' # เปลี่ยนสถานะอัตโนมัติ
            job_instance.save()
            messages.success(request, '📸 ส่งงานเรียบร้อยแล้ว รอแอดมินตรวจสอบอนุมัติ!')
            return redirect('services:job_list')
    else:
        form = JobSubmitForm(instance=job)
        
    return render(request, 'services/submit_job.html', {'form': form, 'job': job})

# หน้าประวัติการทำงาน (งานที่เสร็จสิ้นหรือยกเลิกแล้ว)
@login_required(login_url='accounts:login')
def job_history(request):
    if request.user.is_superuser or request.user.is_staff:
        # แอดมินดูประวัติงานทั้งหมดที่เสร็จแล้ว
        jobs = ServiceJob.objects.filter(status__in=['completed', 'cancelled']).order_by('-updated_at')
    else:
        # ช่างดูประวัติเฉพาะงานของตัวเองที่เสร็จแล้ว
        jobs = ServiceJob.objects.filter(technician=request.user, status__in=['completed', 'cancelled']).order_by('-updated_at')
        
    return render(request, 'services/job_history.html', {'jobs': jobs})