from django.db import models

"""
TaskItem 作業項目
"""
class TaskItem(models.Model):

    task_cd = models.CharField(
        max_length=30,
        verbose_name="作業コード",
        db_comment="作業コード",
    )

    category = models.CharField(
        max_length=30,
        verbose_name="カテゴリ",
        db_comment="カテゴリ",
        null=True,
        blank=True,
    )

    name = models.CharField(
        max_length=30,
        verbose_name="作業名",
        db_comment="作業名",
        null=True,
        blank=True,
    )

    description = models.CharField(
        max_length=100,
        verbose_name="説明",
        db_comment="説明",
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
        db_table = "task_items"
        db_table_comment = "作業項目"
        verbose_name = "作業項目"
        verbose_name_plural = "作業項目一覧"
        constraints = [
            models.UniqueConstraint(fields=['task_cd'], name='task_cd')
        ]

    def __str__(self):
        return self.name