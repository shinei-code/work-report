from django import forms
from .models import Report, Task
from master.models import TaskItem

def is_05(time):
    return time % 0.5 == 0

class ReportCreateForm(forms.ModelForm):
    work_dt = forms.DateField(
        label='作業日',
        disabled=True,
        widget=forms.DateInput(format='%Y/%m/%d')
    )
    start_time = forms.TimeField(
        label='開始時刻',
        required=False,
        widget=forms.TimeInput(
            format='%H:%M', 
            attrs={
                'type': 'time', 
                'step': 1800,    # 30分単位
                'x-model': 'form.startTime'
            }
        )
    )
    end_time = forms.TimeField(
        label='終了時刻', 
        required=False,
        widget=forms.TimeInput(
            format='%H:%M', 
            attrs={
                'type': 'time', 
                'step': 1800,  # 30分単位
                'x-model': 'form.endTime'
            }
        )
    )
    break_hours = forms.DecimalField(
        label='休憩時間',
        decimal_places=1, 
        widget=forms.NumberInput(
            attrs={
                'step': 0.5,
                'x-model': 'form.breakHours'
            }
        ), 
        required=False
    )
    work_hours = forms.DecimalField(
        label='作業時間',
        decimal_places=1, 
        widget=forms.NumberInput(
            attrs={
                'step': 0.5,
                'x-model': 'form.workHours'
            }
        ), 
        required=False
    )
    notes = forms.CharField(
        label='備考',
        widget=forms.Textarea(attrs={'rows': 2}), 
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        self._end_time = ""

    def clean_work_dt(self):
        work_dt = self.cleaned_data['work_dt']
        if not work_dt:
            raise forms.ValidationError('入力必須です')
        return work_dt

    def clean_start_time(self):
        start_time = self.cleaned_data['start_time']
        if not start_time:
            raise forms.ValidationError('入力必須です')
        return start_time

    def clean_end_time(self):
        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data['end_time']

        # ここでエラーが発生した場合、後続の休憩時間、作業時間のバリデーションで
        # 終了時刻が取得できないので、退避しておく
        self._end_time = end_time

        # 開始時刻と終了時刻の大小チェック
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError('開始時刻より前の時刻になっています')

        return end_time

    def clean_break_hours(self):
        end_time = self.cleaned_data.get('end_time')
        break_hours = self.cleaned_data['break_hours']

        # 終了時刻が入力された場合は必須
        if (end_time or self._end_time)  and not break_hours:
            raise forms.ValidationError('入力必須です')
        
        # 0.5単位か
        if break_hours and not is_05(float(break_hours)):
            raise forms.ValidationError('0.5単位で入力してください')

        return break_hours

    def clean_work_hours(self):
        end_time = self.cleaned_data.get('end_time')
        work_hours = self.cleaned_data['work_hours']

        # 終了時刻が入力された場合は必須
        if (end_time or self._end_time) and not work_hours:
            raise forms.ValidationError('入力必須です')
        
        # 0.5単位か
        if work_hours and not is_05(float(work_hours)):
            raise forms.ValidationError('0.5単位で入力してください')
        
        return work_hours

    def clean(self):
        cleaned_data = super().clean()

        # エラーが発生している場合、is-invalidクラスを追加
        for fieldname, _ in self.fields.items():
            if self.errors.get(fieldname):
                self.fields[fieldname].widget.attrs["class"] += " is-invalid"
        
        return cleaned_data

    class Meta:
        model = Report
        fields = ['work_dt', 'start_time', 'end_time', 'break_hours', 'work_hours', 'notes']

class ReportMonth(forms.Form):
    year_month_choices = []
    for year in range(2010, 2031):
        month_list = []
        for month in range(1, 13):
            if month < 10:
                _year = year
                month += 3
            else:
                month -= 9
                _year = year + 1

            month_list.append(
                (f'{_year}{str(month).zfill(2)}', f'{_year}/{str(month).zfill(2)}')
            )
        year_month_choices.append([f'{year}年度', month_list])

    year_month = forms.ChoiceField(
        choices=year_month_choices,
        widget=forms.Select(attrs={
            'class': 'form-control select-year-month',
            'x-model': 'reportMonth',
            '@change': 'changeReportMonth()',
        })
    )

class TaskCreateForm(forms.ModelForm):
    task_item = forms.ModelChoiceField(
        label='作業項目',
        queryset=TaskItem.objects.all(),
        empty_label="選択してください",
        widget=forms.Select(
            attrs={
                'x-model': 'form.taskItem'
                }
        )
    )
    task_hours = forms.DecimalField(
        label='時間',
        decimal_places=1, 
        widget=forms.NumberInput(
            attrs={
                'step': 0.5,
                'x-model': 'form.taskHours'
            }
        ), 
        required=False
    )
    detail = forms.CharField(
        label='詳細',
        widget=forms.Textarea(
            attrs={
                'rows': 2,
                'x-model': 'form.detail'
            }
        ), 
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_task_item(self):
        task_item = self.cleaned_data['task_item']
        if not task_item:
            raise forms.ValidationError('入力必須です')
        return task_item

    def clean_task_hours(self):
        task_hours = self.cleaned_data['task_hours']

        if not task_hours:
            raise forms.ValidationError('入力必須です')
        
        # 0.5単位か
        if task_hours and not is_05(float(task_hours)):
            raise forms.ValidationError('0.5単位で入力してください')

        return task_hours

    def clean_detail(self):
        detail = self.cleaned_data['detail']

        if len(detail) > 50:
            raise forms.ValidationError('50文字まで入力可能です')

        return detail

    def clean(self):
        cleaned_data = super().clean()

        # エラーが発生している場合、is-invalidクラスを追加
        for fieldname, _ in self.fields.items():
            if self.errors.get(fieldname):
                self.fields[fieldname].widget.attrs["class"] += " is-invalid"
        
        return cleaned_data

    class Meta:
        model = Task
        fields = ['task_item', 'task_hours', 'detail']


