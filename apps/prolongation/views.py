#encoding: utf-8
from django.core.mail import send_mail
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django. shortcuts import render, HttpResponse, Http404, redirect, get_object_or_404
from models import UserProlongation, ProlongationManager, StatusChange
from participants.models import Library
from forms import UserProlongationForm, ChangeStatusForm
from django.db import transaction



def send_email_to_managers(prolongation):
    message = u"""\
Поступила новая заявка на продление. Для управления заявкой перейдите по адресу %s.\
            """ % (
        settings.SITE_URL + reverse('prolongation_prolongation_detail', args=[prolongation.id]),
        )
    managers = ProlongationManager.objects.filter(library=prolongation.recive_library_id)
    for manager in managers:
        send_mail(u'Поступила новая заявка на продление', message, 'robot@system',
            [manager.notify_email],fail_silently=True)




def manager_check(user, library):
    try:
        manager = ProlongationManager.objects.get(user=user, library=library)
    except ProlongationManager.DoesNotExist:
        return None
    return manager


@login_required
def index(request):
    prolongations = UserProlongation.objects.filter(user=request.user)

    return render(request, 'prolongation/list.html', {
        'prolongations':prolongations
    })




@transaction.commit_on_success
def prolongation(request):
#    # проверяем, подавал ли пользователь заявления на продление ранее
#    # если да, то перенаправляем его на детальную информацию о регистрации
#    if request.user.is_authenticated():
#        try:
#            prolongation = UserProlongation.objects.get(user=request.user)
#            return  redirect('prolongation_prolongation_user_detail', id=prolongation.id)
#        except UserProlongation.DoesNotExist:
#            pass

    def get_manager_library(library):
        ancestors = library.get_ancestors()
        for ancestor in ancestors:
            if not ancestor.parent_id:
                return ancestor
        return library


    if request.method == 'POST':
        form = UserProlongationForm(request.POST)

        if form.is_valid():
            user_prolongation = form.save(commit=False)
            manage_library_id = request.POST.get('manage_library', 0)

            try:
                manage_library = Library.objects.get(id=manage_library_id)
            except Exception:
                return HttpResponse(u'Ошибка в передаче номера библиотеки')
            if request.user.is_authenticated():
                user_prolongation.user = request.user
            user_prolongation.manage_library = manage_library
            user_prolongation.recive_library = manage_library.get_root()
            user_prolongation.save()

            message = u"""\
Вы подали заявку на продление в библиотеку %s.\
Состояние заявки Вы можете посмотреть пройдя по адресу %s.\
            """ % (manage_library.name, settings.SITE_URL + reverse('prolongation_prolongation_user_detail', args=[user_prolongation.id]))
            send_mail(u'Заявка на электронное продление издания', message, 'robot@system',
                [user_prolongation.email], fail_silently=True)

            send_email_to_managers(user_prolongation)

            return render(request, 'prolongation/send_ok.html', {
                'prolongation': user_prolongation,
            })
    else:
        if request.user.is_authenticated():
            form = UserProlongationForm(initial={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            })
        else:
            form = UserProlongationForm()

    return render(request, 'prolongation/form.html', {
        'form': form,
#        'library': library
    })



def prolongation_user_detail(request, id):

    try:
        prolongation = UserProlongation.objects.select_related().get(id=id)
    except UserProlongation.DoesNotExist:
        raise Http404()

    statuses = StatusChange.objects.filter(prolongation=prolongation)

    return render(request, 'prolongation/prolongation_detail.html', {
        'prolongation': prolongation,
        'statuses': statuses

        #'library': library
    })





@login_required
def checkout(request):

    def get_new_count(self):
        new_count = getattr(self,'_new_count', None)
        if new_count == None:
            self._new_count = UserProlongation.objects.filter(status=0,recive_library=self).count()
        return self._new_count
    Library.get_new_count = get_new_count


    user = request.user

    #извлекаем список библиотек, где пользователья является менеджером
    managers = ProlongationManager.objects.filter(user=user)

    if not len(managers):
        return HttpResponseForbidden(u'У вас нет доступа. Обратитесь к администратору.')

    # получаем список id библиотек, которые обслуживает пользователь
    libraries_ids = []
    for manager in managers:
        libraries_ids.append(manager.library_id)
    # извлекаем регистрации, которые были направлены в библиотеки
    prolongations = UserProlongation.objects.select_related().filter(recive_library__in=libraries_ids)

    libraries =  Library.objects.filter(pk__in=libraries_ids)
    # получаем список библиотек и количество новых заявок
    #libraries =  Library.objects.filter(userlibregistation__status=0, pk__in=libraries_ids).annotate(num_new_userlibregistations=Count('UserProlongation'))


    return render(request, 'prolongation/administration/checkout.html', {
        'prolongations': prolongations,
        'libraries': libraries,

    })

# отображение заявок на продление в библиотеке
@login_required
def checkout_by_library(request, id):

    try:
        library = ProlongationManager.objects.get(user=request.user, library=id).library
    except ProlongationManager.DoesNotExist:
        return HttpResponseForbidden(u'У вас нет доступа. Обратитесь к администратору.')

    prolongations = UserProlongation.objects.select_related().filter(recive_library=library)


    return render(request, 'prolongation/administration/checkout_by_library.html', {
        'prolongations': prolongations,
        'library': library
    })

# отображение заявки на продление в библиотеке
@login_required
def prolongation_detail(request, id):

    try:
        prolongation = UserProlongation.objects.select_related().get(id=id)
    except UserProlongation.DoesNotExist:
        raise Http404()

    if not manager_check(request.user, prolongation.recive_library):
        return HttpResponseForbidden(u'У вас нет доступа. Обратитесь к администратору.')

    form = ChangeStatusForm()

    return render(request, 'prolongation/administration/prolongation_detail_t_library.html', {
        'prolongation': prolongation,
        'forn': form
        #'library': library
    })



def _status_change(request, id, status, comments=u''):
    """
    Изменение статуса заявки.
    Вызывается из других представлений!
    """
    try:
        prolongation = UserProlongation.objects.get(id=id)
    except UserProlongation.DoesNotExist:
        raise Http404()
    manager = manager_check(request.user,prolongation.recive_library_id )
    if not manager:
        return HttpResponseForbidden(u'У вас нет доступа. Обратитесь к администратору.')


    if request.method == 'POST':
        form = ChangeStatusForm(request.POST)
        if form.is_valid():
            status_change = form.save(commit=False)
            status_change.prolongation = prolongation
            status_change.prolongation_manager = manager
            status_change.status = status
            if status_change.status in  prolongation.next_statuses():
                status_change.save()
            else:
                raise ValueError(u'Wrong status code')
            return redirect('prolongation_prolongation_detail', id=id)
    else:
        form = ChangeStatusForm(initial={
            'comments':comments
        })

    return render(request, 'prolongation/administration/change_status.html', {
        'form': form,
        'prolongation': prolongation
    })


# принять заявку на обработку
@login_required
@transaction.commit_on_success
def take_to_process(request, id):
    return _status_change(request, id, 1,
        comments=u'Заявка на продление принята к рассмотрению. Ожидайте ответ.'
    )



# принять заявку на обработку
@login_required
@transaction.commit_on_success
def complete(request, id):
    return _status_change(request, id, 2,
        comments=u'Заявка на продление одобрена.'
    )



# отклонить заявку
@login_required
@transaction.commit_on_success
def reject(request, id):
    return _status_change(request, id, 3,
        comments=u'Заявка на продление отклонена по причиние {% причина %}.'
    )



