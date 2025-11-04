from django.urls import path

from .views import (
    ResultListView,
    create_result,
    edit_results,
    student_performance,
    report_card,
    class_report_sheet,
)

urlpatterns = [
    path("create/", create_result, name="create-result"),
    path("edit-results/", edit_results, name="edit-results"),
    path("view/all", ResultListView.as_view(), name="view-results"),
    path("performance/", student_performance, name="student-performance"),
    path("report-card/<int:student_id>/", report_card, name="report-card"),
    path("class-sheet/<int:class_id>/", class_report_sheet, name="class-report-sheet"),
]
