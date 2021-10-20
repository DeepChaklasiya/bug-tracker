from django.shortcuts import redirect, render
from .models import *
from django.views.generic import DetailView, UpdateView, CreateView, DeleteView
from projects.forms import ProjectForm, ThreadForm
from django.urls import reverse_lazy
from django.contrib import messages


def getProjectsAsManager(user_id):
    return list(Project.objects.filter(
        manager__id=user_id).order_by('-created'))


def getProjectsAsDeveloper(user_id):
    return list(Project.objects.filter(
        developers__id=user_id).order_by('-created'))


def getProjectsAsReporter(user_id):
    p_ids = set(Thread.objects.filter(
        reporter__id=user_id).values_list('project__id', flat=True))
    return list(set(Project.objects.filter(
        pk__in=p_ids).order_by('-created')))


def projectDashboard(request):
    user = request.user
    user_id = user.id
    pm = getProjectsAsManager(user_id)
    pd = getProjectsAsDeveloper(user_id)
    pr = getProjectsAsReporter(user_id)
    projects = {
        "pm": pm, "pd": pd, "pr": pr
    }
    return render(request, 'dashboard.html', context=projects)


def explore(request):
    return render(request, 'explore.html')


class ProjectDetail(DetailView):
    model = Project
    template_name = 'project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        pr = ctx['project']
        ctx['isManager'] = pr.manager.id == self.request.user.id
        return ctx


def projectDelete(request, pk):
    try:
        Project.objects.get(pk=pk).delete()
        messages.success(request, 'Project Deleted Successfully')
    except Project.DoesNotExist:
        messages.error(
            request, 'Requested project not found! Cannot be deleted')
    except (ValueError, TypeError, OverflowError):
        messages.error(request, 'Some error occurred while deleting!')
    finally:
        return redirect('project:dashboard')


class ProjectCreate(CreateView):
    model = Project
    template_name = 'project_create.html'
    form_class = ProjectForm
    success_url = reverse_lazy('project:dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class ProjectEdit(UpdateView):
    model = Project
    template_name = 'project_edit.html'
    form_class = ProjectForm
    context_object_name = 'project'

    def get_success_url(self):
        project_id = self.kwargs['pk']
        return reverse_lazy('project:project_details', kwargs={'pk': project_id})


def ThreadList(request, projectId):
    # print("entered")
    threads = list(Thread.objects.filter(
        project__id=projectId).order_by('-created'))
    # print(threads)
    project = Project.objects.get(id=projectId)
    return render(request, 'thread_list.html', context={"threads": threads, "project": project})

def threadDelete(request, pk , projectId):
    try:
        Thread.objects.get(pk=pk).delete()
        messages.success(request, 'Thread Deleted Successfully')
    except Thread.DoesNotExist:
        messages.error(
            request, 'Requested thread not found! Cannot be deleted')
    except (ValueError, TypeError, OverflowError):
        messages.error(request, 'Some error occurred while deleting!')
    finally:
        return redirect('project:thread_list',projectId=projectId)


class ThreadCreate(CreateView):
    
       
    model = Thread
    template_name = 'thread_create.html'
    form_class = ThreadForm
    def get_success_url(self):
        projectId = self.kwargs['projectId']
        return reverse_lazy('project:thread_list', kwargs={'projectId': projectId})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'reporter': self.request.user,'projectId': self.kwargs['projectId']})
        return kwargs
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['projectId']=self.kwargs['projectId']
        print(ctx['projectId'])
        return ctx
    



        
class ThreadDetail(DetailView):
    model = Thread
    template_name = 'thread_details.html'
    context_object_name = 'thread'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        project = Project.objects.get(id=self.kwargs['projectId'])
        ctx['project']=project
        ctx['comments'] = list(Comment.objects.filter(
            thread__id=ctx['thread'].id).order_by('-created'))
        return ctx

class ThreadEdit(UpdateView):
    model = Thread
    template_name = 'thread_edit.html'
    form_class = ThreadForm
    context_object_name = 'thread'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'projectId': self.kwargs['projectId']})
        return kwargs

    def get_success_url(self):
        pk= self.kwargs['pk']
        return reverse_lazy('project:thread_details', kwargs={'pk': pk,'projectId': self.kwargs['projectId']})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['projectId']=self.kwargs['projectId']
        self.projectId = self.kwargs['projectId']
        ctx['pk'] = self.kwargs['pk']
        return ctx

def CommentList(request, pk):
    comments = list(Comment.objects.filter(
        thread__id=pk).order_by('-created'))
    print(comments)
    return render(request, 'comment_list.html', context={"comments": comments})
