#encoding: utf-8
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django. shortcuts import render, HttpResponse, Http404, redirect, get_object_or_404
from models import UserLibRegistation, RegistrationManager, StatusChange
from participants.models import Library
from forms import UserLibRegistationForm, ChangeStatusForm
from django.db import transaction
from django.core.paginator import Paginator, InvalidPage, EmptyPage


def send_email_to_managers(registration):
    message = u"""\
Поступила новая заявка на запись пользователя в библиотеку. Для управления заявкой перейдите по адресу %s.\
            """ % (
        settings.SITE_URL + reverse('reginlib_registration_detail', args=[registration.id]),
        )
    managers = RegistrationManager.objects.filter(library=registration.recive_library_id)
    for manager in managers:
        send_mail(u'Поступила новая заявка на запись в библиотеку', message, 'robot@system',
            [manager.notify_email],fail_silently=True)


def manager_check(user, library):
    try:
        manager = RegistrationManager.objects.get(user=user, library=library)
    except RegistrationManager.DoesNotExist:
        return None
    return manager


@login_required
def index(request):
    registrations = UserLibRegistation.objects.filter(user=request.user)

    return render(request, 'reginlib/list.html', {
        'registrations':registrations
    })



from django.core.mail import send_mail
from django.conf import settings
from django.core.urlresolvers import reverse
@transaction.commit_on_success
def registration(request):
    # проверяем, подавал ли пользователь заявления на регистрацию ранее
    # если да, то перенаправляем его на детальную информацию о регистрации
    if request.user.is_authenticated():
        try:
            registration = UserLibRegistation.objects.get(user=request.user)
            return  redirect('reginlib_registration_user_detail', id=registration.id)
        except UserLibRegistation.DoesNotExist:
            pass

    def get_manager_library(library):
        ancestors = library.get_ancestors()
        for ancestor in ancestors:
            if not ancestor.parent_id:
                return ancestor
        return library


    if request.method == 'POST':
        form = UserLibRegistationForm(request.POST)
        manage_library = request.POST.get('manage_library', None)
        if not request.POST.get('manage_library', None) or manage_library == '0':
            return render(request, 'reginlib/form.html', {
                'form': form,
                'alert': u'Вы не указали библиотеку'
            })
        if form.is_valid():
            user_lib_registration = form.save(commit=False)
            manage_library_id = request.POST.get('manage_library', 0)

            try:
                manage_library = Library.objects.get(id=manage_library_id)
            except Exception:
                return HttpResponse(u'Ошибка в передаче номера библиотеки')
            if request.user.is_authenticated():
                user_lib_registration.user = request.user
            user_lib_registration.manage_library = manage_library
            user_lib_registration.recive_library = manage_library.get_root()
            user_lib_registration.save()

            message = u"""\
Вы подали заявку на запись в библиотеку "%s".\
Состояние заявки Вы можете посмотреть пройдя по адресу %s.\
            """ % (
                    manage_library.name,
                    settings.SITE_URL + reverse('reginlib_registration_user_detail', args=[user_lib_registration.id])
                )
            send_mail(
                u'Регистрация в библиотеке',
                message, 'robot@system',
                [user_lib_registration.email],
                fail_silently=True
            )

            send_email_to_managers(user_lib_registration)

            return render(request, 'reginlib/send_ok.html', {
                'registration': user_lib_registration,
            })
    else:
        if request.user.is_authenticated():
#            form = UserLibRegistationForm(initial={
#                'first_name': request.user.first_name,
#                'last_name': request.user.last_name,
#                'email': request.user.email,
#            })
            form = UserLibRegistationForm()
        else:
            form = UserLibRegistationForm()

    return render(request, 'reginlib/form.html', {
        'form': form,
#        'library': library
    })



def registration_user_detail(request, id):

    try:
        registration = UserLibRegistation.objects.select_related().get(id=id)
    except UserLibRegistation.DoesNotExist:
        raise Http404()

    statuses = StatusChange.objects.filter(registration=registration)

    return render(request, 'reginlib/registration_detail.html', {
        'registration': registration,
        'statuses': statuses

        #'library': library
    })





@login_required
def checkout(request):

    def get_new_count(self):
        new_count = getattr(self,'_new_count', None)
        if new_count == None:
            self._new_count = UserLibRegistation.objects.filter(status=0,recive_library=self).count()
        return self._new_count
    Library.get_new_count = get_new_count


    user = request.user

    #извлекаем список библиотек, где пользователья является менеджером
    managers = RegistrationManager.objects.filter(user=user)

    if not len(managers):
        return HttpResponseForbidden(u'У вас нет доступа. Обратитесь к администратору.')

    # получаем список id библиотек, которые обслуживает пользователь
    libraries_ids = []
    for manager in managers:
        libraries_ids.append(manager.library_id)
    # извлекаем регистрации, которые были направлены в библиотеки
    registrations = UserLibRegistation.objects.select_related().filter(recive_library__in=libraries_ids).order_by('-id')
    paginator = Paginator(registrations, 20)
    try:

        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        registrations_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        registrations_list = paginator.page(paginator.num_pages)
    libraries =  Library.objects.filter(pk__in=libraries_ids)
    # получаем список библиотек и количество новых заявок
    #libraries =  Library.objects.filter(userlibregistation__status=0, pk__in=libraries_ids).annotate(num_new_userlibregistations=Count('userlibregistation'))


    return render(request, 'reginlib/administration/checkout.html', {
        'registrations': registrations_list,
        'libraries': libraries,

    })

# отображение заявок на регистрацию в библиотеке
@login_required
def checkout_by_library(request, id):

    try:
        library = RegistrationManager.objects.get(user=request.user, library=id).library
    except RegistrationManager.DoesNotExist:
        return HttpResponseForbidden(u'У вас нет доступа. Обратитесь к администратору.')

    registrations = UserLibRegistation.objects.select_related().filter(recive_library=library).order_by('-id')

    paginator = Paginator(registrations, 20)
    try:

        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        registrations_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        registrations_list = paginator.page(paginator.num_pages)


    return render(request, 'reginlib/administration/checkout_by_library.html', {
        'registrations': registrations_list,
        'library': library
    })

# отображение заявки на регистрацию в библиотеке
@login_required
def registration_detail(request, id):

    try:
        registration = UserLibRegistation.objects.select_related().get(id=id)
    except UserLibRegistation.DoesNotExist:
        raise Http404()

    if not manager_check(request.user, registration.recive_library):
        return HttpResponseForbidden(u'У вас нет доступа. Обратитесь к администратору.')

    form = ChangeStatusForm()

    return render(request, 'reginlib/administration/registration_detail_t_library.html', {
        'registration': registration,
        'forn': form
        #'library': library
    })



def _status_change(request, id, status, comments=u''):
    """
    Изменение статуса заявки.
    Вызывается из других представлений!
    """
    try:
        registration = UserLibRegistation.objects.get(id=id)
    except UserLibRegistation.DoesNotExist:
        raise Http404()
    manager = manager_check(request.user,registration.recive_library_id )
    if not manager:
        return HttpResponseForbidden(u'У вас нет доступа. Обратитесь к администратору.')


    if request.method == 'POST':
        form = ChangeStatusForm(request.POST)
        if form.is_valid():
            status_change = form.save(commit=False)
            status_change.registration = registration
            status_change.registration_manager = manager
            status_change.status = status
            print 'rs', registration.status , registration.next_statuses()
            if status_change.status in  registration.next_statuses():
                status_change.save()
            else:
                raise ValueError(u'Wrong status code')
            return redirect('reginlib_registration_detail', id=id)
    else:
        form = ChangeStatusForm(initial={
            'comments':comments
        })

    return render(request, 'reginlib/administration/change_status.html', {
        'form': form,
        'registration': registration
    })


# принять заявку на обработку
@login_required
@transaction.commit_on_success
def take_to_process(request, id):
    return _status_change(request, id, 1,
        comments=u'Заявка на регистрацию принята к рассмотрению. Ожидайте ответ.'
    )



# принять заявку на обработку
@login_required
@transaction.commit_on_success
def complete(request, id):
    return _status_change(request, id, 2,
        comments=u'Заявка на регистрацию одобрена. Просим Вас явиться в {% место/ время %}.'
    )



# отклонить заявку
@login_required
@transaction.commit_on_success
def reject(request, id):
    return _status_change(request, id, 3,
        comments=u'Заявка на регистрацию отклонена по причиние {% причина %}.'
    )



