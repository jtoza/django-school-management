from django import forms

from .models import AttendanceRegister, AttendanceEntry


class AttendanceRegisterForm(forms.ModelForm):
    class Meta:
        model = AttendanceRegister
        fields = ['date', 'student_class', 'term', 'session', 'notes']


class AttendanceEntryForm(forms.ModelForm):
    class Meta:
        model = AttendanceEntry
        fields = ['status', 'remarks']