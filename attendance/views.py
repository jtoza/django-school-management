from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView

from apps.corecode.models import StudentClass
from apps.students.models import Student

from .forms import AttendanceRegisterForm, AttendanceEntryForm
from .models import AttendanceRegister, AttendanceEntry


class AttendanceRegisterListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'attendance.view_attendanceregister'
    model = AttendanceRegister
    template_name = 'attendance/register_list.html'


class AttendanceRegisterCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'attendance.add_attendanceregister'
    model = AttendanceRegister
    form_class = AttendanceRegisterForm
    template_name = 'attendance/register_form.html'
    success_url = reverse_lazy('attendance:register_list')

    def form_valid(self, form):
        form.instance.taken_by = self.request.user
        messages.success(self.request, 'Attendance register created.')
        return super().form_valid(form)


class AttendanceRegisterDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'attendance.view_attendanceregister'
    model = AttendanceRegister
    template_name = 'attendance/register_detail.html'


class AttendanceRegisterUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'attendance.change_attendanceregister'
    model = AttendanceRegister
    form_class = AttendanceRegisterForm
    template_name = 'attendance/register_form.html'
    success_url = reverse_lazy('attendance:register_list')


class AttendanceRegisterDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'attendance.delete_attendanceregister'
    model = AttendanceRegister
    template_name = 'attendance/register_confirm_delete.html'
    success_url = reverse_lazy('attendance:register_list')


@login_required
@permission_required('attendance.change_attendanceentry', raise_exception=True)
def take_attendance(request, pk):
    register = get_object_or_404(AttendanceRegister, pk=pk)
    students = Student.objects.filter(current_class=register.student_class, current_status='active').order_by('surname', 'firstname')

    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f'status_{student.id}', AttendanceEntry.STATUS_PRESENT)
            remarks = request.POST.get(f'remarks_{student.id}', '')
            entry, _ = AttendanceEntry.objects.get_or_create(register=register, student=student)
            entry.status = status
            entry.remarks = remarks
            entry.save()
        messages.success(request, 'Attendance saved.')
        return redirect('attendance:register_detail', pk=register.pk)

    entries = {e.student_id: e for e in AttendanceEntry.objects.filter(register=register)}

    context = {
        'register': register,
        'students': students,
        'entries': entries,
        'status_choices': AttendanceEntry.STATUS_CHOICES,
    }
    return render(request, 'attendance/take_attendance.html', context)
