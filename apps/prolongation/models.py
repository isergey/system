# encoding: utf-8

from django.core.exceptions import ValidationError
from django.shortcuts import urlresolvers
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from participants.models import Library
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail

PROLONGATION_STATUSES = (
    (0, u'ожидание обработки'),
    (1, u'обрабатывается'),
    (2, u'запрос выполнен'),
    (3, u'отклонено'),
    )



# регистрация пользователя в библиотеке
class UserProlongation(models.Model):

    user = models.ForeignKey(User, null=True)

    recive_library = models.ForeignKey(
        Library,
        verbose_name=u"Библиотека получатель заявки",
        help_text=u'Библиотека, которая получит заявку'
    )

    manage_library = models.ForeignKey(
        Library,
        verbose_name=u"Библиотека обработчик заявки",
        help_text=u'Библиотека, в которой осуществляется регистрация',
        related_name='prolongation_manage_library'
    )

    status = models.IntegerField(
        choices=PROLONGATION_STATUSES,
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

    library_card_no = models.CharField(
        max_length=32,
        verbose_name=u"Номер читательского билета"
    )

    email = models.EmailField(
        max_length=256,
        verbose_name=u'Адрес электронной почты'
    )

    phone = models.CharField(
        max_length=16,
        verbose_name=u"Телефон для связи",
        blank=True, null=True

    )

    doc_title = models.CharField(
        max_length=512,
        verbose_name=u"Название издания"
    )

    date_of_return = models.DateField(
        verbose_name=u'Срок возврата',
        help_text=u'Укажите дату, когда документ должен быть возвращен в библиотеку'
    )

    new_date_of_return = models.DateField(
        verbose_name=u'Срок продления',
        help_text=u'Укажите дату, до которой хотите продлить срок возврата. Не более, чем 30 дней со дня старого срока возврата'
    )

    create_date = models.DateTimeField(
        auto_now=True, auto_now_add=True
    )


    def next_statuses(self):
        """
        Возвращает список статусов, которые может принять регистрация, в зависимости от текущего статуса
        """

        #матрица переходов между статусами
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
        verbose_name = u"Электронное продление"
        verbose_name_plural = u"Электронные продления"


class ProlongationManager(models.Model):
    user = models.ForeignKey(User)
    library = models.ForeignKey(Library, verbose_name=u"Библиотека")
    notify_email = models.EmailField(max_length=128, verbose_name=u'Email для оповещения менеджера')

    class Meta:
        unique_together = ('user', 'library')
        verbose_name = u"Менеджер продления"
        verbose_name_plural = u"Менеджеры продления"


# фиксация смены статуса
class StatusChange(models.Model):
    prolongation = models.ForeignKey(UserProlongation, verbose_name=u'Заявка на продление')
    prolongation_manager = models.ForeignKey(ProlongationManager, verbose_name=u'Менеджер')
    status = models.IntegerField(choices=PROLONGATION_STATUSES, db_index=True, verbose_name=u'Статус')
    change_date = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True) # дата смены статуса
    comments = models.CharField(max_length=1024, blank=True, verbose_name=u'Комментарии')






@receiver(post_save, sender=StatusChange)
def change_prolongation_status(sender, instance, **kwargs):
    """
    Установка статуса продления
    """
    prolongation = instance.prolongation
    prolongation.status = instance.status
    prolongation.save()
    send_email_to_user(prolongation)



def send_email_to_user(prolongation):
    message = u"""\
Состояние вашей заявки на продление  %s в библиотеке %s изменилось (статус: %s).\
Более подробную информацию о заявке Вы можете посмотреть пройдя по адресу %s.\
            """ % (
            prolongation.doc_title,
            prolongation.manage_library.name,
            prolongation.get_status_display(),
            settings.SITE_URL + urlresolvers.reverse('prolongation_prolongation_user_detail', args=[prolongation.id])
        )
    send_mail(u'Изменение статуса заявки на электронное продление издания', message, 'robot@ksob.spb.ru',
        [prolongation.email])
    pass


