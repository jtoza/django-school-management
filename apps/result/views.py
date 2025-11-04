from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView, View

from apps.corecode.models import StudentClass
from apps.students.models import Student

from attendance.models import AttendanceEntry, AttendanceRegister
from .forms import CreateResults, EditResults
from .models import Result


@login_required
def student_performance(request):
    student = None
    labels = []
    totals = []
    reg = request.GET.get("reg")
    if reg:
        student = Student.objects.filter(registration_number=reg).first()
        if student:
            # Aggregate average total per (session, term)
            data = (
                Result.objects.filter(student=student)
                .values_list("session__name", "term__name")
                .order_by("session__name", "term__name")
            )
            # Build a stable unique ordered list
            seen = set()
            ordered_keys = []
            for s, t in data:
                key = f"{s} {t}"
                if key not in seen:
                    seen.add(key)
                    ordered_keys.append((s, t))
            from django.db.models import Avg, F, FloatField, ExpressionWrapper
            qs = (
                Result.objects.filter(student=student)
                .values("session__name", "term__name")
                .annotate(total=ExpressionWrapper(F("test_score") + F("exam_score"), output_field=FloatField()))
                .values("session__name", "term__name")
                .annotate(avg_total=Avg("total"))
                .order_by("session__name", "term__name")
            )
            agg = {(row["session__name"], row["term__name"]): row["avg_total"] for row in qs}
            labels = [f"{s} {t}" for s, t in ordered_keys]
            totals = [round(agg.get((s, t), 0), 2) for s, t in ordered_keys]
    context = {"student": student, "labels": labels, "totals": totals}
    return render(request, "result/student_performance.html", context)


@login_required
def create_result(request):
    students = Student.objects.all()
    if request.method == "POST":

        # after visiting the second page
        if "finish" in request.POST:
            form = CreateResults(request.POST)
            if form.is_valid():
                subjects = form.cleaned_data["subjects"]
                session = form.cleaned_data["session"]
                term = form.cleaned_data["term"]
                students = request.POST["students"]
                results = []
                for student in students.split(","):
                    stu = Student.objects.get(pk=student)
                    if stu.current_class:
                        for subject in subjects:
                            check = Result.objects.filter(
                                session=session,
                                term=term,
                                current_class=stu.current_class,
                                subject=subject,
                                student=stu,
                            ).first()
                            if not check:
                                results.append(
                                    Result(
                                        session=session,
                                        term=term,
                                        current_class=stu.current_class,
                                        subject=subject,
                                        student=stu,
                                    )
                                )

                Result.objects.bulk_create(results)
                return redirect("edit-results")

        # after choosing students
        id_list = request.POST.getlist("students")
        if id_list:
            form = CreateResults(
                initial={
                    "session": request.current_session,
                    "term": request.current_term,
                }
            )
            studentlist = ",".join(id_list)
            return render(
                request,
                "result/create_result_page2.html",
                {"students": studentlist, "form": form, "count": len(id_list)},
            )
        else:
            messages.warning(request, "You didnt select any student.")
    return render(request, "result/create_result.html", {"students": students})


@login_required
def edit_results(request):
    if request.method == "POST":
        form = EditResults(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Results successfully updated")
            return redirect("edit-results")
    else:
        results = Result.objects.filter(
            session=request.current_session, term=request.current_term
        )
        form = EditResults(queryset=results)
    return render(request, "result/edit_results.html", {"formset": form})


class ResultListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        results = Result.objects.filter(
            session=request.current_session, term=request.current_term
        )
        bulk = {}

        for result in results:
            test_total = 0
            exam_total = 0
            subjects = []
            for subject in results:
                if subject.student == result.student:
                    subjects.append(subject)
                    test_total += subject.test_score
                    exam_total += subject.exam_score

            bulk[result.student.id] = {
                "student": result.student,
                "subjects": subjects,
                "test_total": test_total,
                "exam_total": exam_total,
                "total_total": test_total + exam_total,
            }

        context = {"results": bulk}
        return render(request, "result/all_results.html", context)


@login_required
def report_card(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    session = request.current_session
    term = request.current_term
    results = Result.objects.filter(student=student, session=session, term=term).select_related('subject', 'current_class')
    teacher_comment = next((r.teacher_comment for r in results if r.teacher_comment), "")
    headteacher_comment = next((r.headteacher_comment for r in results if r.headteacher_comment), "")
    current_class = results.first().current_class if results.exists() else student.current_class

    regs = AttendanceRegister.objects.filter(
        session=session,
        term=term,
        student_class=current_class,
    )
    entries = AttendanceEntry.objects.filter(register__in=regs, student=student)
    present = entries.filter(status=AttendanceEntry.STATUS_PRESENT).count()
    absent = entries.filter(status=AttendanceEntry.STATUS_ABSENT).count()
    late = entries.filter(status=AttendanceEntry.STATUS_LATE).count()

    avg = sum(r.total_score() for r in results)/results.count() if results else 0

    context = {
        'student': student,
        'current_class': current_class,
        'session': session,
        'term': term,
        'results': results,
        'average_total': round(avg, 2),
        'attendance': {'present': present, 'absent': absent, 'late': late},
        'teacher_comment': teacher_comment,
        'headteacher_comment': headteacher_comment,
    }
    return render(request, 'result/report_card.html', context)


@login_required
def class_report_sheet(request, class_id):
    student_class = get_object_or_404(StudentClass, pk=class_id)
    session = request.current_session
    term = request.current_term
    students = Student.objects.filter(current_class=student_class, current_status='active')

    rows = []
    regs = AttendanceRegister.objects.filter(session=session, term=term, student_class=student_class)
    for stu in students:
        results = Result.objects.filter(student=stu, session=session, term=term)
        avg = round(sum(r.total_score() for r in results)/results.count(), 2) if results else 0
        entries = AttendanceEntry.objects.filter(register__in=regs, student=stu)
        present = entries.filter(status=AttendanceEntry.STATUS_PRESENT).count()
        absent = entries.filter(status=AttendanceEntry.STATUS_ABSENT).count()
        late = entries.filter(status=AttendanceEntry.STATUS_LATE).count()
        rows.append({
            'student': stu,
            'average_total': avg,
            'attendance': {'present': present, 'absent': absent, 'late': late}
        })

    context = {
        'student_class': student_class,
        'session': session,
        'term': term,
        'rows': rows,
    }
    return render(request, 'result/class_report_sheet.html', context)
