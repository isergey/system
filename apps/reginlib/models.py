# encoding: utf-8

from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from participants.models import Library
from django.db.models.signals import post_save
from django.dispatch import receiver


REGISTRATION_STATUSES = (
    (0, u'ожидание обработки'),
    (1, u'обрабатывается'),
    (2, u'готово'),
    (3, u'отклонено'),
    )



# регистрация пользователя в библиотеке
class UserLibRegistation(models.Model):

    user = models.ForeignKey(User, unique=True, null=True)

    recive_library = models.ForeignKey(
        Library,
        verbose_name=u"Библиотека получатель заявки",
        help_text=u'Библиотека, которая получит заявку'
    )

    manage_library = models.ForeignKey(
        Library,
        verbose_name=u"Библиотека обработчик заявки",
        help_text=u'Библиотека, в которой осуществляется регистрация',
        related_name='manage_library'
    )

    status = models.IntegerField(
        choices=REGISTRATION_STATUSES,
        db_index=True,
        verbose_name=u'Статус',
        default=0
    )

    first_name = models.CharField(
        max_length=32,
        verbose_name=u'Имя, отчество'
    )

    last_name = models.CharField(
        max_length=32,
        verbose_name=u'Фамилия'
    )

    email = models.EmailField(
        max_length=256,
        verbose_name=u'Адрес электронной почты'
    )

    phone = models.CharField(
        max_length=16,
        verbose_name=u"Телефон для связи"
    )

    visit_date = models.DateField(
        verbose_name=u'Дата визита',
        help_text=u'Укажите желаемую дату визита в библиотеку'
    )

    create_date = models.DateTimeField(
        auto_now=True, auto_now_add=True
    )


    def next_statuses(self):
        """
        Возвращает список статусов, которые может принять регистрация, в зависимости от текущего статуса
        """
        status_matrix = {
            0: [1, 3],
            1: [2, 3],
            2: [],
            3: [],
            }
        if self.status not in status_matrix:
            raise ValueError(u'Wrong status code')

        return status_matrix[self.status]

    # может быть приянто на обработку
    def can_take_to_process(self):
        action_statuses = [0]
        if self.status in action_statuses:
            return True
        return False

    # может быть отклонено
    def can_reject(self):
        action_statuses = [0, 1]
        if self.status in action_statuses:
            return True
        return False

    # может быть завершено
    def can_complete(self):
        action_statuses = [1]
        if self.status in action_statuses:
            return True
        return False

    def can_delete(self):
        return not (self.can_take_to_process() or self.can_reject() or self.can_complete())

    class Meta:
        unique_together = ('user', 'recive_library')
        verbose_name = u"Пользовательская регистрация"
        verbose_name_plural = u"Пользовательские регистрации"


class RegistrationManager(models.Model):
    user = models.ForeignKey(User)
    library = models.ForeignKey(Library, verbose_name=u"Библиотека")
    notify_email = models.EmailField(max_length=128, verbose_name=u'Email для оповещения менеджера')

    class Meta:
        unique_together = ('user', 'library')
        verbose_name = u"Менеджер записи в библиотеку"
        verbose_name_plural = u"Менеджеры записи в библиотеку"

# фиксация смены статуса
class StatusChange(models.Model):
    registration = models.ForeignKey(UserLibRegistation, verbose_name=u'Регистрация')
    registration_manager = models.ForeignKey(RegistrationManager, verbose_name=u'Менеджер')
    status = models.IntegerField(choices=REGISTRATION_STATUSES, db_index=True, verbose_name=u'Статус')
    change_date = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True) # дата смены статуса
    comments = models.CharField(max_length=1024, blank=True, verbose_name=u'Комментарии')


@receiver(post_save, sender=StatusChange)
def change_registration_status(sender, instance, **kwargs):
    """
    Установка статуса регистрации
    """
    registration = instance.registration
    registration.status = instance.status
    registration.save()
    send_email_to_user(registration)


def send_email_to_user(registration):
    message = u"""\
Состояние вашей заявки на регистрациюв библиотеке %s изменилась.\
Состояние заявки Вы можете посмотреть пройдя по адресу %s.\
            """ % (
        registration.manage_library.name,
        settings.SITE_URL + reverse('reginlib_registration_user_detail', args=[registration.id])
        )
    send_mail(u'Изменение статуса заявки на регистрацию в библиотеке', message, 'robot@system',
        [registration.email])
    pass


