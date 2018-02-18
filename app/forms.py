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

class CenHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        TabHolder(
        Tab('Centro',
        'id_centro',InlineCheckboxes('prestador'),'sector_auto','sector_caminando'),
        ),
        Div(Submit('submit', 'Apply Filter',css_class='btn-primary'),css_class='col-lg-offset-3 col-lg-9',),
        HTML("""
            <br>    <br>
        """),
    )
class AncHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        TabHolder(
        Tab('Ancla Temporal',
        'id',InlineCheckboxes('prestador'),InlineCheckboxes('tipo'),'sector_auto','sector_caminando'),
        Tab('Hora','hora_inicio','hora_fin')
        ),
        Div(Submit('submit', 'Apply Filter',css_class='btn-primary'),css_class='col-lg-offset-3 col-lg-9',),
        HTML("""
            <br>    <br>
        """),
    )
class IndCenHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        TabHolder(
        Tab('Individuo-Centro',
        'individuo', Div('centro')
        ) ),
        Div(Submit('submit', 'Apply Filter',css_class='btn-primary'),css_class='col-lg-offset-3 col-lg-9',),
        HTML("""
            <br>    <br>
        """),
    )
class PedHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        TabHolder(
        Tab('Pediatra',
            Div('centro'),InlineCheckboxes('dia'),'hora','cantidad_pediatras'
        ) ),
        Div(Submit('submit', 'Apply Filter',css_class='btn-primary'),css_class='col-lg-offset-3 col-lg-9',),
        HTML("""
            <br>    <br>
        """),
    )
class PresHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        TabHolder(
        Tab('Prestador',
            Div('prestador'),
        ) ),
        Div(Submit('submit', 'Apply Filter',css_class='btn-primary'),css_class='col-lg-offset-3 col-lg-9',),
        HTML("""
            <br>    <br>
        """),
    )
class SecAutHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        TabHolder(
        Tab('Sector Auto',
            Div('shapeid'),
        ) ),
        Div(Submit('submit', 'Apply Filter',css_class='btn-primary'),css_class='col-lg-offset-3 col-lg-9',),
        HTML("""
            <br>    <br>
        """),
    )
class SecCamHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        TabHolder(
        Tab('Sector Caminando',
            Div('shapeid'),
        ) ),
        Div(Submit('submit', 'Apply Filter',css_class='btn-primary'),css_class='col-lg-offset-3 col-lg-9',),
        HTML("""
            <br>    <br>
        """),
    )
class SecOmnHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        TabHolder(
        Tab('Sector Omnibus',
            Div('shapeid'),
        ) ),
        Div(Submit('submit', 'Apply Filter',css_class='btn-primary'),css_class='col-lg-offset-3 col-lg-9',),
        HTML("""
            <br>    <br>
        """),
    )
class SecTieAutHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        TabHolder(
        Tab('Tiempos Sectores Auto',
            Div('sector_1'), Div('sector_2')
        ) ),
        Div(Submit('submit', 'Apply Filter',css_class='btn-primary'),css_class='col-lg-offset-3 col-lg-9',),
        HTML("""
            <br>    <br>
        """),
    )
class SecTieCamHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        TabHolder(
        Tab('Tiempos Sectores Caminando',
            Div('sector_1'), Div('sector_2')
        ) ),
        Div(Submit('submit', 'Apply Filter',css_class='btn-primary'),css_class='col-lg-offset-3 col-lg-9',),
        HTML("""
            <br>    <br>
        """),
    )
class SecTieOmnHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        TabHolder(
        Tab('Tiempos Sectores Caminando',
            Div('sectorO_1'), Div('sectorO_2')
        ) ),
        Div(Submit('submit', 'Apply Filter',css_class='btn-primary'),css_class='col-lg-offset-3 col-lg-9',),
        HTML("""
            <br>    <br>
        """),
    )