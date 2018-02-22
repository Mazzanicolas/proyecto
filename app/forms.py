from django import forms
from .models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, HTML,Field
from crispy_forms.bootstrap import Tab, TabHolder,InlineCheckboxes,InlineRadios
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .utils import getPrestadoresNombres,getPrestaresNombresFiltrosSimular

REDIRECT_FIELD_NAME = 'next'
class UserForm(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username','email','password']

class UserRegistryHelper(FormHelper):
    form_method = 'POST'
    layout = Layout(
        Div(
        Div(Field('email')),
        Div(Field('username')),
        Div(Field('password')),
        Div(Div(Submit('submit', 'Crear',css_class='btn-primary')),
        css_class="panel-body")
            )
        )

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
choices = ((0,"Por defecto"),(1,"Si"),(None,"No"))
DIAS = (
    (0, 'L'),
    (1, 'M'),
    (2, 'Mi'),
    (3, 'J'),
    (4, 'V'),
    (5, 'S'),
    (6, 'D'),
    )
horas = [(i,i) for i in range(0,24)]
class EjecutarForm(forms.Form):
    tipoTransporte = forms.ModelMultipleChoiceField(queryset = TipoTransporte.objects.all(),to_field_name = 'id',label = '')
    trabaja = forms.ChoiceField(choices=choices,label = '')
    asisteJardin = forms.ChoiceField(choices= choices, label = '')
    prestadorFiltro = forms.ChoiceField(choices = getPrestadoresNombres,label = '')
    dias = forms.MultipleChoiceField(choices = DIAS,label = '')
    horaInicio = forms.ChoiceField(choices = horas,label = '')
    horaFin = forms.ChoiceField(choices = horas[::-1],label = '')
    idList = forms.CharField(label = '',required = False)
class SimularForm(EjecutarForm):
    prestadorFiltro = forms.ChoiceField(choices = getPrestaresNombresFiltrosSimular,label = '')

class EjecutarHelper(FormHelper):
    form_class = 'form-horizontal'
    form_method = 'GET'
    layout = Layout(
            Div(
                Div(HTML('<h5>Transporte<h5>'), style="margin-left: 40px;"),
                Div(HTML('<div><label class="checkbox-inline"><input type="checkbox" id = "checkTransporte" name = "checkT" value = "-1" checked> Por defecto </label></div>'),
                    Div(InlineCheckboxes('tipoTransporte',style="margin-left: 10px;text-transform:capitalize;"),id='transporteDiv', style="display: none;margin-left: 20px;"),style="margin-left: 80px;")
            ),
            Div(
                Div(HTML('<h5>Trabaja<h5>'), style="margin-left: 40px;"),
                Div(InlineRadios('trabaja',style="margin-left: 10px;"),style="margin-left: 65px;")
            ),
            Div(
                Div(HTML('<h5>Jardin</h5>'), style="margin-left: 40px;"),
                Div(InlineRadios('asisteJardin',style="margin-left: 10px;"),style="margin-left: 65px;")
            ),
            Div(
                Div(HTML('<h5>Prestadores</h5>'), style="margin-left: 40px;"),
                Div(HTML('<div> <label class="checkbox-inline"><input type="checkbox" id = "checkPrestador" name = "checkPrestador" value = "-1" checked> Por defecto </label></div>'),
                    Div(InlineCheckboxes('prestadorFiltro'),id='prestadorDiv', style="display: none;margin-left: 20px;"),style="margin-left: 80px;")
            ),
            Div(
                Div(HTML('<h5>Dias</h5>'), style="margin-left: 40px;"),
                Div(HTML('<div> <label class="checkbox-inline"><input type="checkbox" id = "checkDias" name = "checkDias" value = "-1" checked> Todos </label></div>'),
                    Div(InlineCheckboxes('dias',style="margin-left: 10px;"),id='diasDiv', style="display: none;"),style="margin-left: 80px;")
            ),
            Div(
                Div(HTML('<h5>Rango Horario</h5>'), style="margin-left: 40px;"),
                Div(Div('horaInicio', style="margin-left: 40px;margin-right:40px;"),Div('horaFin', style="margin-left:40px;margin-right:40px;"))
            ),
            Div(
                Div(HTML("<h5>Lista de ID's</h5>"), style="margin-left: 40px;"),
                Div(Field('idList', placeholder="Lista de ID's separadas por coma"), style="margin-left:40px;margin-right:40px;")
            ),
            Div(
                Div(HTML('<h5>¿Como quiere el resultado?</h5>'), style="margin-left: 40px;"),
                Div(HTML('<label class="checkbox-inline"><input type="checkbox" id="cbCSV" name="checkRango" value="-1" checked> Descargar como .csv</label></br>'),style="margin-left: 80px;")
                
            ),
            Div(
                Div(HTML('<h5>Resultados a generar</h5>'), style="margin-left: 40px;"),
                Div(HTML('<label class="checkbox-inline"><input type="checkbox" name="generarIndividual" value="1" checked> Ejecutar </label></br><label class="checkbox-inline"><input type="checkbox"id="cbCSV0" name="generarResumen" value="1"> Resumen</label></br>'),style="margin-left: 80px;")                
            ),
        Div(Div(Submit('submit', 'Calcular',css_class='btn-primary')), style="text-align: center;")
    )
class SimularHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout( Div(
        Div(HTML('<div style="font-size:180%"> Simular </div>', ),css_class = "modal-header" ),
        HTML(' <div hidden><label class="checkbox-inline"><input type="checkbox" name = simular id="simul" value="1" checked> Simular </label></div>'),
        Div(
            Div(HTML("<strong>¡Advertencia!</strong> Esta operacion puede demorar varias horas."),css_class = "alert alert-warning"),
            Div(
                Div( HTML('<div style="font-size:130%"> Transporte</div>', ),css_class ="panel-footer" ),
                Div(InlineRadios('tipoTransporte'),css_class = "panel-body"), 
                css_class = "panel panel-default"
            ),
            Div(
                Div( HTML('<div style="font-size:130%"> Anclas Temporales</div>', ),css_class ="panel-footer" ),
                Div(HTML('<label class="checkbox-inline"><input type="checkbox" name = anclaTra id="inlineCheckbox1" value="1" checked> Trabajo </label>'),
                    HTML('<label class="checkbox-inline"><input type="checkbox" name = anclaJar id="inlineCheckbox2" value="1" checked> Jardin </label></br>'),
                    css_class = "panel-body"),
                css_class = "panel panel-default"
            ),
            Div(
                Div( HTML('<div style="font-size:130%"> Prestadores</div>', ),css_class ="panel-footer" ),
                Div(InlineRadios('prestadorFiltro'),css_class = "panel-body"),
                css_class = "panel panel-default"
            ),
            Div(
                Div( HTML('<div style="font-size:130%"> Dias </div>', ),css_class = "panel-footer"),
                Div(HTML('<div> <label class="checkbox-inline"><input type="checkbox" id = "checkDias2" name = "checkDias" value = "-1" checked> Todos </label></div>'),
                    Div(InlineCheckboxes('dias'),id='diasDiv2',css_class ="panel-body", style="display: none;"), css_class ="panel-body" ),
                    css_class = "panel panel-default"
            ),
            Div(
                Div( HTML('<div style="font-size:130%"> Rango Horario</div>', ),css_class = "panel-footer"),
                Div(Div('horaInicio', css_class = "panel-body"),Div('horaFin', css_class = "panel-body")),
                css_class = "panel panel-default"
            ),
            Div(
                Div( HTML('<div style="font-size:130%">Lista de IDs </div>', ),css_class ="panel-footer" ),
                Div(Field('idList'), css_class = "panel-body"),
                css_class = "panel panel-default"
            ),
            Div(
                Div( HTML('<div style="font-size:130%"> ¿Como quiere el resultado? </div>', ),css_class ="panel-footer" ),
                Div(HTML('<label class="checkbox-inline"><input type="checkbox" id="cbCSV2" name="checkRango" value="-1" checked> Descargar como .csv</label></br>'), css_class = "panel-body"),
                css_class = "panel panel-default"
            ),
            Div(
                Div( HTML('<div style="font-size:130%"> Resultados a generar </div>', ),css_class ="panel-footer" ),
                Div(HTML('<label class="checkbox-inline"><input type="checkbox" name="generarIndividual" value="1" checked> Simulacion </label></br><label class="checkbox-inline"><input type="checkbox"id="cbCSV3" name="generarResumen" value="1"> Resumen</label></br>'), css_class = "panel-body"),
                css_class = "panel panel-default"
            ),
        css_class = "modal-body"
        ),
        Div(Div(Submit('submit', 'Calcular',css_class='btn-primary'),css_class='col-lg-offset-3 col-lg-9',),
        HTML("""
            <br>    <br>
        """),css_class="panel-footer"),

    css_class = "modal-content"),
        
    )
class SuperLogin(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(SuperLogin, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            HTML('<br><br>'),
            Field('username', placeholder="username"),
            Field('password', placeholder="password"),
            Div(Div(Submit('submit', 'Login',css_class='btn-primary btn-block')))
        )

