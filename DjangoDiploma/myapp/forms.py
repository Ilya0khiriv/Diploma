from django import forms


class ContactForm(forms.Form):
    question = forms.CharField(max_length=1000, label='Введите запрос:')


class AmountForm(forms.Form):
    amount = forms.IntegerField(label='Введите запрос:')
