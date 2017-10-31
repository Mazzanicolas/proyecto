from django import forms
from .models import IndividuoTiempoCentro
import crispy_forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit

class FooFilterFormHelper(crispy_forms.helper.FormHelper):
    form_method = 'GET'
    layout = Layout(
        'individuo__id',
        'centro__id_centro',
        Submit('submit', 'Apply Filter'),
    )
