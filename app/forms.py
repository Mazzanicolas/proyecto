from django import forms
from .models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, HTML,Field
from crispy_forms.bootstrap import Tab, TabHolder,InlineCheckboxes,InlineRadios
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

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
    prestadorFiltro = forms.ChoiceField(choices = [(x.id,x.nombre) for x in Prestador.objects.all()],label = '')
    dias = forms.MultipleChoiceField(choices = DIAS,label = '')
    horaInicio = forms.ChoiceField(choices = horas,label = '')
    horaFin = forms.ChoiceField(choices = horas[::-1],label = '')
    idList = forms.CharField(label = '',required = False)
class SimularForm(EjecutarForm):
    prestadorFiltro = forms.ChoiceField(choices = [(-1,"Por defecto"),(-2,"Ignorar")]+ [(x.id,x.nombre) for x in Prestador.objects.all()],label = '')

class EjecutarHelper(FormHelper):
    form_class = 'form-horizontal'
    form_method = 'GET'
    layout = Layout( Div(
        Div(
            Div(
                Div( HTML('<h5> Transporte<h5>', ) ),
                Div(HTML('<div><label class="checkbox-inline"><input type="checkbox" id = "checkTransporte" name = "checkT" value = "-1" checked> Por defecto </label></div>'),
                    Div(InlineCheckboxes('tipoTransporte'),id='transporteDiv', style="display: none;"), css_class ="panel-body"),
                    #css_class = "panel panel-default"
            ),
            Div(
                Div( HTML('<div style="font-size:130%"> Trabaja</div>', ),css_class ="panel-footer" ),
                Div(InlineRadios('trabaja'), css_class = "panel-body"),
                css_class = "panel panel-default"
            ),
            Div(
                Div( HTML('<div style="font-size:130%"> Jardin</div>', ),css_class ="panel-footer" ),
                Div(InlineRadios('asisteJardin'), css_class = "panel-body"),
                css_class = "panel panel-default"
            ),
            Div(
                Div( HTML('<div style="font-size:130%"> Prestadores</div>', ),css_class ="panel-footer" ),
                Div(HTML('<div> <label class="checkbox-inline"><input type="checkbox" id = "checkPrestador" name = "checkPrestador" value = "-1" checked> Por defecto </label></div>'),
                    Div(InlineCheckboxes('prestadorFiltro'),id='prestadorDiv',css_class = "panel-body", style="display: none;"), css_class ="panel-body"),
                    css_class = "panel panel-default"
            ),
            Div(
                Div( HTML('<div style="font-size:130%"> Dias </div>', ),css_class = "panel-footer"),
                Div(HTML('<div> <label class="checkbox-inline"><input type="checkbox" id = "checkDias" name = "checkDias" value = "-1" checked> Todos </label></div>'),
                    Div(InlineCheckboxes('dias'),id='diasDiv',css_class ="panel-body", style="display: none;"), css_class ="panel-body" ),
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
                Div(HTML('<label class="checkbox-inline"><input type="checkbox" id="cbCSV" name="checkRango" value="-1" checked> Descargar como .csv</label></br>'), css_class = "panel-body"),
                css_class = "panel panel-default"
            ),
            Div(
                Div( HTML('<div style="font-size:130%"> Resultados a generar </div>', ),css_class ="panel-footer" ),
                Div(HTML('<label class="checkbox-inline"><input type="checkbox" name="generarIndividual" value="1" checked> Ejecutar </label></br><label class="checkbox-inline"><input type="checkbox"id="cbCSV0" name="generarResumen" value="1"> Resumen</label></br>'), css_class = "panel-body"),
                css_class = "panel panel-default"
            ),
        css_class = "modal-body"
        ),
        Div(Div(Submit('submit', 'Calcular',css_class='btn-primary'),css_class='col-lg-offset-3 col-lg-9',),css_class="panel-footer"),

    css_class = "modal-content"),
        
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

