from django import forms
from .models import IndividuoTiempoCentro
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, HTML,Field
from crispy_forms.bootstrap import Tab, TabHolder,InlineCheckboxes,InlineRadios

class IndTieCenHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        TabHolder(
        Tab('Individuo-Centro',
        'individuo','trabajo','jardin',
        Div('centro')
        ),
        Tab('Hora-Dia',
        'hora',InlineCheckboxes('dia')
        ),
        Tab('Prestadores', InlineCheckboxes('prestador')),
        Tab('Transporte', InlineCheckboxes('transporte')),
        ),
        Div(Submit('submit', 'Apply Filter',css_class='btn-primary'),css_class='col-lg-offset-3 col-lg-9',),
        HTML("""
            <br>    <br>
        """),
    )
class IndHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        TabHolder(
        Tab('Individuo',
        'individuo','trabajo','jardin'),
        Tab('Prestadores', InlineCheckboxes('prestador')),
        Tab('Transporte', InlineCheckboxes('transporte')),
        ),
        Div(Submit('submit', 'Apply Filter',css_class='btn-primary'),css_class='col-lg-offset-3 col-lg-9',),
        HTML("""
            <br>    <br>
        """),
    )
