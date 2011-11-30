# -*- coding: utf-8 -*-

from django.forms import ModelForm
from models import Feedback
from captcha.fields import CaptchaField
from django.utils.html import strip_tags


class FeedbackForm(ModelForm):
    captcha = CaptchaField(label=u"Введите текст изображенный на картинке*", error_messages={'invalid': u"Введенный текст не совпадает с тексом на картинке"})
    class Meta:
        model = Feedback
        exclude = ["published"]
    
    def clean_message(self):
        return strip_tags(self.cleaned_data['message'])
