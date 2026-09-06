from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from .forms import SignUpForm
from .models import UserProfile

def register_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'ลงทะเบียนสำเร็จ! บัญชีของคุณอยู่ในสถานะรอการอนุมัติจากผู้ดูแลระบบ')
            return redirect('accounts:login')
    else:
        form = SignUpForm()
    
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if hasattr(user, 'profile') and not user.is_staff and not user.is_superuser:
                    profile = user.profile
                    if profile.status == 'pending':
                        messages.warning(request, 'บัญชีของคุณยังอยู่ในสถานะรอการอนุมัติจากผู้ดูแลระบบ กรุณารอการติดต่อกลับ')
                        return redirect('accounts:login')
                    elif profile.status == 'rejected':
                        messages.error(request, f'บัญชีของคุณไม่ได้รับการอนุมัติ เนื่องจาก: {profile.rejection_reason or "ไม่มีระบุเหตุผล"}')
                        return redirect('accounts:login')
                    elif profile.status == 'suspended':
                        messages.error(request, 'บัญชีของคุณถูกระงับการใช้งาน กรุณาติดต่อผู้ดูแลระบบ')
                        return redirect('accounts:login')
                
                login(request, user)
                messages.success(request, f'ยินดีต้อนรับคุณ {user.first_name or user.username} เข้าสู่ระบบคลังอะไหล่')
                return redirect('/')
        else:
            messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
    else:
        form = AuthenticationForm()
        
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'ออกจากระบบเรียบร้อยแล้ว')
    return redirect('accounts:login')

@staff_member_required
def admin_approval_list(request):
    profiles = UserProfile.objects.select_related('user', 'approved_by').all().order_by('id')
    return render(request, 'admin_approval.html', {'profiles': profiles})

# ทุก action ในนี้แก้ไขข้อมูลจริง (อนุมัติ/ปฏิเสธ/ระงับ/ให้สิทธิ์/ลบบัญชี)
# จึงบังคับให้เป็น POST เท่านั้น (require_POST) เพื่อปิดช่องโหว่ CSRF ที่เคยเกิดจากการ
# ยิง action ผ่าน GET link ตรง ๆ — ถ้ามีการเรียกด้วย GET จะได้ 405 Method Not Allowed ทันที
@staff_member_required
@require_POST
def update_status(request, profile_id, action):
    profile = get_object_or_404(UserProfile, id=profile_id)
    target_user = profile.user
    admin_name = request.user.get_full_name() or request.user.username

    # 1. อนุมัติการใช้งาน (Member) + ส่งเมลแจ้งเตือน
    if action == 'approve':
        profile.status = 'approved'
        profile.approved_by = request.user
        profile.rejection_reason = ""
        profile.save()

        if target_user.email:
            send_mail(
                subject='[ระบบคลังอะไหล่] บัญชีของคุณได้รับการอนุมัติแล้ว',
                message=f'สวัสดีคุณ {target_user.username},\n\nบัญชีของคุณได้รับการอนุมัติให้เข้าใช้งานระบบเรียบร้อยแล้ว โดยผู้ดูแลระบบ: {admin_name}\nสามารถเข้าสู่ระบบเพื่อใช้งานได้ทันที',
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@stock.com'),
                recipient_list=[target_user.email],
                fail_silently=True
            )
        messages.success(request, f'อนุมัติบัญชีของ {target_user.username} เรียบร้อยแล้ว')

    # 2. ปฏิเสธการสมัคร + ส่งเมลแจ้งเหตุผล
    elif action == 'reject':
        reason = request.POST.get('rejection_reason', 'ไม่ระบุเหตุผล')
        profile.status = 'rejected'
        profile.approved_by = request.user
        profile.rejection_reason = reason
        profile.save()

        if target_user.email:
            send_mail(
                subject='[ระบบคลังอะไหล่] แจ้งผลการพิจารณาบัญชีผู้ใช้',
                message=f'สวัสดีคุณ {target_user.username},\n\nบัญชีของคุณไม่ผ่านการอนุมัติ เนื่องจาก: {reason}\nดำเนินการโดย: {admin_name}',
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@stock.com'),
                recipient_list=[target_user.email],
                fail_silently=True
            )
        messages.error(request, f'ปฏิเสธบัญชีของ {target_user.username} แล้ว')

    # 3. ระงับการใช้งาน
    elif action == 'suspend':
        profile.status = 'suspended'
        profile.approved_by = request.user
        profile.save()
        messages.warning(request, f'ระงับการใช้งานบัญชีของ {target_user.username} แล้ว')

    # 4. เลื่อนขั้นเป็น Admin + ส่งเมลแจ้งเตือน
    elif action == 'make_admin':
        target_user.is_staff = True
        target_user.save()
        profile.approved_by = request.user
        profile.save()

        if target_user.email:
            send_mail(
                subject='[ระบบคลังอะไหล่] ปรับระดับสิทธิ์บัญชีผู้ใช้',
                message=f'สวัสดีคุณ {target_user.username},\n\nคุณได้รับการแต่งตั้งเป็น Admin เรียบร้อยแล้ว โดย: {admin_name}',
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@stock.com'),
                recipient_list=[target_user.email],
                fail_silently=True
            )
        messages.success(request, f'แต่งตั้งคุณ {target_user.username} เป็น Admin สำเร็จ')

    # 5. ปรับลดสิทธิ์กลับมาเป็น Member
    elif action == 'remove_admin':
        if target_user == request.user:
            messages.error(request, 'คุณไม่สามารถปลดสิทธิ์ Admin ของตัวเองได้')
        else:
            target_user.is_staff = False
            target_user.save()
            profile.approved_by = request.user
            profile.save()
            messages.info(request, f'ปรับลดสิทธิ์ {target_user.username} เป็น Member เรียบร้อยแล้ว')

    # 6. ลบบัญชีผู้ใช้ออกจากระบบ (ข้อมูลประวัติการเบิกจะไม่สูญหาย)
    elif action == 'delete_user':
        if target_user == request.user:
            messages.error(request, 'คุณไม่สามารถลบบัญชีของตัวเองได้')
        elif target_user.is_superuser:
            messages.error(request, 'ไม่อนุญาตให้ลบบัญชี Super Admin')
        else:
            deleted_username = target_user.username
            target_user.delete()
            messages.success(request, f'ลบบัญชี {deleted_username} ออกจากระบบเรียบร้อยแล้ว')

    return redirect('accounts:admin_approval')