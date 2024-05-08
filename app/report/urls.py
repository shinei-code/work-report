from django.urls import path
from . import views

app_name = "report"
urlpatterns = [
    path('report/', views.ReportListView.as_view(), name='report-list'),
    path('report/<str:report_month>', views.ReportListView.as_view(), name='report-list-report-month'),
    path('report/create/<str:work_dt>', views.ReportCreateView.as_view(), name="report-create"),
    path('report/copy-create/', views.ReportCopyCreateView.as_view(), name="report-copy-create"),
    path('report/update/<int:pk>', views.ReportUpdateView.as_view(), name="report-update"),
    path('report/delete/<int:pk>', views.ReportDeleteView.as_view(), name="report-delete"),
    path('api/report/detail/<int:pk>', views.ReportApiDetailView.as_view(), name="report-api-detail"),
    path('api/report/list/', views.ReportApiListView.as_view(), name="report-api-list"),

    path('task/create/<int:report_id>', views.TaskCreateView.as_view(), name="task-create"),
    path('task/update/<int:pk>', views.TaskUpdateView.as_view(), name="task-update"),
    path('task/delete/<int:pk>', views.TaskDeleteView.as_view(), name="task-delete"),
]
