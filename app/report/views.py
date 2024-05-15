from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Report, Task, ReportTemplate, TaskTemplate
from django.http import JsonResponse
from django.forms.models import model_to_dict
from .forms import ReportMonth, ReportCreateForm, TaskCreateForm
from datetime import date, datetime
from django.contrib import messages

# 日付妥当性チェック
def conv_date(date, format="%Y%m%d"):
    try:
        return datetime.strptime(date, format)
    except ValueError:
        return False

def get_report(id, user):
    return Report.objects.filter(id=id, user=user)

########## 作業報告 ##########
class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = "report/list.html"
    context_object_name = 'reports'

    def dispatch(self, request, *args, **kwargs):
        self.report_month = self.kwargs.get('report_month')

        if self.report_month:
            if not conv_date(self.report_month+'01'):
                messages.error(request, f'パラメータが正しくありません ({self.report_month})')
                return redirect(reverse_lazy('report:report-list'))

            # パラメータのreport_monthと、セッションのreport_idのwork_dt（年月）が
            # 不一致の場合、セッションをクリア
            session_report_id = request.session.get('report_id')
            if session_report_id:
                report = Report.objects.values('work_dt').get(id=session_report_id)
                work_dt = report['work_dt'].strftime('%Y%m')

                if work_dt != self.report_month:
                    request.session['report_id'] = None

        else:
            # report_monthの指定がない場合は当月
            self.report_month = date.today().strftime("%Y%m")
        
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Report.objects.filter(
            user=self.request.user,
            work_dt__year=self.report_month[:4],
            work_dt__month=self.report_month[4:]
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['report_month'] = ReportMonth(
            initial={
                'year_month': self.report_month
            }
        )

        session_report_id = self.request.session.get('report_id')
        context['report_detail_id'] = session_report_id if session_report_id else 'null'

        return context

class ReportApiListView(LoginRequiredMixin, View):
    model = Report

    def add_where(self, columns):
        for column in columns:
            param = self.request.GET.get(column)
            if param:
                self.where[column] = param

    def get(self, request, *args, **kwargs):
        self.where = {'user': self.request.user}
        self.add_where(['work_dt'])

        reports = list(Report.objects.filter(**self.where).values())
        return JsonResponse(reports, safe=False)

class ReportCreateView(LoginRequiredMixin, CreateView):
    model = Report
    form_class = ReportCreateForm
    template_name = "report/create.html"

    def dispatch(self, request, *args, **kwargs):
        param_work_dt = self.kwargs.get('work_dt')
        work_dt = conv_date(param_work_dt)

        # パラメータの日付妥当性チェック
        if not work_dt:
            messages.error(request, f'パラメータが正しくありません ({param_work_dt})')
            return redirect(reverse_lazy('report:report-list'))

        if Report.objects.filter(user=request.user, work_dt=work_dt).exists():
            messages.error(request, f'{work_dt.strftime("%Y/%m/%d")} の作業報告はすでに登録済みです')
            return redirect(reverse_lazy('report:report-list'))

        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        work_dt = conv_date(self.kwargs['work_dt'])
        initial['work_dt'] = work_dt
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['templates'] = ReportTemplate.objects.filter(user=self.request.user)
        context['is_create'] = True
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user  # ユーザーにログインユーザーを設定
        form.instance.save()
        self.request.session['report_id'] = form.instance.id # idをセッションに保存
        
        self.success_url = reverse_lazy(
            'report:report-list-report-month',
            kwargs={'report_month': form.instance.work_dt.strftime("%Y%m")}
        )

        return super().form_valid(form)

class ReportCopyCreateView(LoginRequiredMixin, View):
    model = Report

    def post(self, request, *args, **kwargs):
        report_pk = request.POST.get('base-pk')
        copy_at_work_dt = request.POST.get('copy-at-work-dt')

        base_report = Report.objects.get(pk=report_pk)  # コピー元Report取得
        report = model_to_dict(base_report)
        report['id'] = None
        report['user'] = base_report.user
        report['work_dt'] = datetime.strptime(copy_at_work_dt, "%Y/%m/%d").date()
        new_report = Report.objects.create(**report)  # Report複製保存

        base_tasks = Task.objects.filter(report=report_pk)  # コピー元Reportに紐づくTask
        new_tasks = []
        for base_task in base_tasks:
            new_task = model_to_dict(base_task)
            new_task["id"] = None
            new_task["report"] = new_report
            new_task["task_item"] = base_task.task_item
            new_tasks.append(Task(**new_task))
        
        if new_tasks:
            Task.objects.bulk_create(new_tasks)  # Task複製一括登録

        request.session['report_id'] = new_report.id
        messages.success(
            request, 
            f'{base_report.work_dt.strftime("%Y/%m/%d")}の作業報告を{new_report.work_dt.strftime("%Y/%m/%d")}にコピーしました'
        )
        return redirect(reverse_lazy(
            'report:report-list-report-month',
            kwargs={'report_month': new_report.work_dt.strftime("%Y%m")}
        ))

class ReportApiDetailView(LoginRequiredMixin, DetailView):
    model = Report

    def get(self, request, *args, **kwargs):
        request.session['report_id'] = self.kwargs.get('pk')
        
        report = self.get_object()
        tasks = report.Tasks.all()  # リレーション先のtask取得

        # taskをリスト化
        tasks_list = []
        for task in tasks:
            task_dict = model_to_dict(task)
            task_dict['task_item'] = model_to_dict(task.task_item)
            tasks_list.append(task_dict)

        obj = model_to_dict(report)
        obj['tasks'] = tasks_list
        return JsonResponse(obj)

class ReportUpdateView(LoginRequiredMixin, UpdateView):
    model = Report
    form_class = ReportCreateForm
    template_name = "report/create.html"

    def dispatch(self, request, *args, **kwargs):
        request.session['report_id'] = self.kwargs.get('pk')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.success_url = reverse_lazy(
            'report:report-list-report-month',
            kwargs={'report_month': form.instance.work_dt.strftime("%Y%m")}
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['templates'] = ReportTemplate.objects.filter(user=self.request.user)
        context['is_create'] = False
        return context

class ReportDeleteView(DeleteView):
    model = Report
    success_url = "/report"

    def get_success_url(self):
        delete_item = self.get_object()
        messages.error(self.request, f'{delete_item.work_dt.strftime("%Y/%m/%d")}の作業報告を削除しました')
        success_url = reverse_lazy(
            'report:report-list-report-month',
            kwargs={'report_month': delete_item.work_dt.strftime("%Y%m")}
        )
        self.request.session['report_id'] = None
        return success_url

########## 作業内容 ##########
class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "task/create.html"

    def dispatch(self, request, *args, **kwargs):
        # パラメータのidがログインユーザーのreportであるかチェック
        param_report_id = self.kwargs.get('report_id')
        self.report_queryset = get_report(param_report_id, request.user)
        if not self.report_queryset.exists():
            messages.error(request, f'作業報告が存在しません (id: {param_report_id})')
            return redirect(reverse_lazy('report:report-list'))

        self.request.session['report_id'] = param_report_id

        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['report'] = self.kwargs['report_id']
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report = self.report_queryset.get()
        context['work_dt'] = report.work_dt

        context['templates'] = TaskTemplate.objects.filter()  # 条件 要追加 user=self.request.user
        context['is_create'] = True
        return context

    def form_valid(self, form):

        # report（外部キー）にパラメータのreport_idをセット
        param_report_id = self.kwargs.get('report_id')
        report = get_report(param_report_id, self.request.user).get()
        form.instance.report = report 

        # report.wok_dt(年月)の作業報告一覧へ遷移
        self.success_url = reverse_lazy(
            'report:report-list-report-month',
            kwargs={'report_month': report.work_dt.strftime("%Y%m")}
        )

        return super().form_valid(form)

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "task/create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        task = self.get_object()
        report = get_report(task.report.id, self.request.user).get()
        context['work_dt'] = report.work_dt

        context['templates'] = TaskTemplate.objects.filter()  # 条件 要追加 user=self.request.user
        context['is_create'] = False
        self.request.session['report_id'] = report.id
        return context

    def form_valid(self, form):
        self.success_url = reverse_lazy(
            'report:report-list-report-month',
            kwargs={'report_month': form.instance.report.work_dt.strftime("%Y%m")}
        )
        self.request.session['report_id'] = form.instance.report.id
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        task_item = self.object.task_item
        initial['task_item'] = task_item
        return initial

class TaskDeleteView(DeleteView):
    model = Task

    def get_success_url(self):
        delete_item = self.get_object()
        success_url = reverse_lazy(
            'report:report-list-report-month',
            kwargs={'report_month': delete_item.report.work_dt.strftime("%Y%m")}
        )
        self.request.session['report_id'] = delete_item.report.id
        return success_url
    

