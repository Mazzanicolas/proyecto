from django import forms

class listForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)
    s_id = forms.IntegerField(label = 'sector id')
