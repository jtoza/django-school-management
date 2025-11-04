from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.corecode.models import StudentClass, AcademicSession, AcademicTerm
from apps.students.models import Student


class AttendanceRegister(models.Model):
    date = models.DateField(default=timezone.now)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name='attendance_registers')
    term = models.ForeignKey(AcademicTerm, on_delete=models.PROTECT)
    session = models.ForeignKey(AcademicSession, on_delete=models.PROTECT)
    taken_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        unique_together = ('date', 'student_class', 'term', 'session')
        ordering = ('-date',)

    def __str__(self):
        return f"Register {self.date} - {self.student_class} ({self.term} {self.session})"


class AttendanceEntry(models.Model):
    STATUS_PRESENT = 'P'
    STATUS_ABSENT = 'A'
    STATUS_LATE = 'L'
    STATUS_EXCUSED = 'E'

    STATUS_CHOICES = [
        (STATUS_PRESENT, 'Present'),
        (STATUS_ABSENT, 'Absent'),
        (STATUS_LATE, 'Late'),
        (STATUS_EXCUSED, 'Excused'),
    ]

    register = models.ForeignKey(AttendanceRegister, on_delete=models.CASCADE, related_name='entries')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_PRESENT)
    remarks = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        unique_together = ('register', 'student')
        ordering = ('student__surname', 'student__firstname')

    def __str__(self):
        return f"{self.student} - {self.get_status_display()}"