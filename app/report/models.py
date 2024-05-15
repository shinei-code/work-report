from django.db import models
from django.contrib.auth.models import User
from master.models import TaskItem

"""
Report 作業報告
"""
class Report(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="ユーザー",
        db_comment="ユーザー",
        null=True,
        blank=True,
    )

    work_dt = models.DateField(
        verbose_name="作業日",
        db_comment="作業日",
        null=True,
        blank=True,
    )

    start_time = models.TimeField(
        verbose_name="開始時間",
        db_comment="開始時間",
        null=True,
        blank=True,
    )

    end_time = models.TimeField(
        verbose_name="終了時間",
        db_comment="終了時間",
        null=True,
        blank=True,
    )

    break_hours = models.DecimalField(
        verbose_name="休憩時間",
        db_comment="休憩時間",
        decimal_places=1,
        max_digits=3,
        null=True,
        blank=True,
    )

    work_hours = models.DecimalField(
        verbose_name="作業時間",
        db_comment="作業時間",
        decimal_places=1,
        max_digits=3,
        null=True,
        blank=True,
    )

    notes = models.TextField(
        verbose_name="備考",
        db_comment="備考",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="作成日時",
        db_comment="作成日時",
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新日時",
        db_comment="更新日時",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "reports"
        db_table_comment = "作業報告"
        verbose_name = "作業報告"
        verbose_name_plural = "作業報告一覧"
        constraints = [
            models.UniqueConstraint(fields=['user', 'work_dt'], name='unique_key1')  # ユーザーと作業日の組み合わせで重複禁止
        ]

"""
Task 作業内容
"""
class Task(models.Model):

    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name="Tasks",
        verbose_name="作業報告",
        db_comment="作業報告",
        null=True,
        blank=True,
    )

    task_item = models.ForeignKey(
        TaskItem,
        on_delete=models.PROTECT,
        to_field="task_cd",
        verbose_name="作業內容",
        db_comment="作業内容",
        null=True,
        blank=True,
    )

    detail = models.CharField(
        max_length=50,
        verbose_name="詳細",
        db_comment="詳細",
        null=True,
        blank=True,
    )

    task_hours = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        verbose_name="所要時間",
        db_comment="所要時間",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="作成日時",
        db_comment="作成日時",
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新日時",
        db_comment="更新日時",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "tasks"
        db_table_comment = "作業内容"
        verbose_name = "作業内容"
        verbose_name_plural = "作業内容一覧"

"""
ReportTemplate 作業報告テンプレート
"""
class ReportTemplate(models.Model):

    name = models.CharField(
        max_length=30,
        verbose_name="テンプレート名",
        db_comment="テンプレート名",
        null=True,
        blank=True,
    )

    desc = models.CharField(
        max_length=50,
        verbose_name="説明",
        db_comment="説明",
        null=True,
        blank=True,
    )

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="ユーザー",
        db_comment="ユーザー",
        null=True,
        blank=True,
    )

    start_time = models.TimeField(
        verbose_name="開始時間",
        db_comment="開始時間",
        null=True,
        blank=True,
    )

    end_time = models.TimeField(
        verbose_name="終了時間",
        db_comment="終了時間",
        null=True,
        blank=True,
    )

    break_hours = models.DecimalField(
        verbose_name="休憩時間",
        db_comment="休憩時間",
        decimal_places=1,
        max_digits=3,
        null=True,
        blank=True,
    )

    work_hours = models.DecimalField(
        verbose_name="作業時間",
        db_comment="作業時間",
        decimal_places=1,
        max_digits=3,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="作成日時",
        db_comment="作成日時",
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新日時",
        db_comment="更新日時",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "report_templates"
        db_table_comment = "作業報告テンプレート"
        verbose_name = "作業報告テンプレート"
        verbose_name_plural = "作業報告テンプレート一覧"

"""
TaskTemplate 作業内容テンプレート
"""
class TaskTemplate(models.Model):

    name = models.CharField(
        max_length=30,
        verbose_name="テンプレート名",
        db_comment="テンプレート名",
        null=True,
        blank=True,
    )

    desc = models.CharField(
        max_length=50,
        verbose_name="説明",
        db_comment="説明",
        null=True,
        blank=True,
    )

    task_item = models.ForeignKey(
        TaskItem,
        on_delete=models.PROTECT,
        to_field="task_cd",
        verbose_name="作業內容",
        db_comment="作業内容",
        null=True,
        blank=True,
    )

    detail = models.CharField(
        max_length=50,
        verbose_name="詳細",
        db_comment="詳細",
        null=True,
        blank=True,
    )

    task_hours = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        verbose_name="所要時間",
        db_comment="所要時間",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="作成日時",
        db_comment="作成日時",
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新日時",
        db_comment="更新日時",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "task_templates"
        db_table_comment = "作業内容テンプレート"
        verbose_name = "作業内容テンプレート"
        verbose_name_plural = "作業内容テンプレート一覧"
