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
        Div(Div(Submit('submit', 'Crear',css_class='btn-primary')))
            )
        )

class IndTieCenHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        Div(
            Div(
                Div(
                    Div('individuo','trabajo','jardin','centro','hora',InlineCheckboxes('dia'),InlineCheckboxes('prestador'),Tab('Transporte', InlineCheckboxes('transporte')),
                    Div(Submit('submit', 'Aplicar Filtros',css_class='btn btn-primary'),css_class='col-lg-offset-3 col-lg-9',)
                    ),css_class="card"
                ),id="filters", css_class="collapse"
            )
        )
    )
#    layout = Layout(
#        TabHolder(
#        Tab('Individuo-Centro',
#        'individuo','trabajo','jardin',
#        Div('centro')
#        ),
#        Tab('Hora-Dia',
#        'hora',InlineCheckboxes('dia')
#        ),
#        Tab('Prestadores', InlineCheckboxes('prestador')),
#        Tab('Transporte', InlineCheckboxes('transporte')),
#        ),
#        Div(Submit('submit', 'Apply Filter',css_class='btn-primary'),css_class='col-lg-offset-3 col-lg-9',),
#        HTML("""
#            <br>    <br>
#        """),
#    )
class IndHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        Div(
            Div(
                Div(
                    Div('individuo','trabajo','jardin',InlineCheckboxes('prestador'),InlineCheckboxes('transporte')),
                    Div(Submit('submit', 'Aplicar Filtros',css_class='btn btn-primary'),css_class='col-lg-offset-3 col-lg-9',)
                ),css_class="card"
            ),id="filters", css_class="collapse"
        )
    )

class CenHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        Div(
            Div(
                Div(
                    Div('id_centro',InlineCheckboxes('prestador'),'sector_auto','sector_caminando'),
                    Div(Submit('submit', 'Aplicar Filtros',css_class='btn btn-primary'),css_class='col-lg-offset-3 col-lg-9',)
                ),css_class="card"
            ),id="filters", css_class="collapse"
        )
    )
class AncHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        Div(
            Div(
                Div(#Error prestador
                    Div('id',InlineCheckboxes('prestador'),InlineCheckboxes('tipo'),'sector_auto','sector_caminando','hora_inicio','hora_fin'),
                    Div(Submit('submit', 'Aplicar Filtros',css_class='btn btn-primary'),css_class='col-lg-offset-3 col-lg-9',)
                ),css_class="card"
            ),id="filters", css_class="collapse"
        )
    )
class IndCenHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        Div(
            Div(
                Div(
                    Div('individuo','centro'),
                    Div(Submit('submit', 'Aplicar Filtros',css_class='btn btn-primary'),css_class='col-lg-offset-3 col-lg-9',)
                ),css_class="card"
            ),id="filters", css_class="collapse"
        )
    )
class PedHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        Div(
            Div(
                Div(
                    Div('centro',InlineCheckboxes('dia'),'hora','cantidad_pediatras'),
                    Div(Submit('submit', 'Aplicar Filtros',css_class='btn btn-primary'),css_class='col-lg-offset-3 col-lg-9',)
                ),css_class="card"
            ),id="filters", css_class="collapse"
        )
    )
class PresHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        Div(
            Div(
                Div(
                    Div('prestador'),
                    Div(Submit('submit', 'Aplicar Filtros',css_class='btn btn-primary'),css_class='col-lg-offset-3 col-lg-9',)
                ),css_class="card"
            ),id="filters", css_class="collapse"
        )
    )
class SecAutHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        Div(
            Div(
                Div(
                    Div('shapeid'),
                    Div(Submit('submit', 'Aplicar Filtros',css_class='btn btn-primary'),css_class='col-lg-offset-3 col-lg-9',)
                ),css_class="card"
            ),id="filters", css_class="collapse"
        )
    )
class SecCamHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        Div(
            Div(
                Div(
                    Div('shapeid'),
                    Div(Submit('submit', 'Aplicar Filtros',css_class='btn btn-primary'),css_class='col-lg-offset-3 col-lg-9',)
                ),css_class="card"
            ),id="filters", css_class="collapse"
        )
    )
class SecOmnHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        Div(
            Div(
                Div(
                    Div('shapeid'),
                    Div(Submit('submit', 'Aplicar Filtros',css_class='btn btn-primary'),css_class='col-lg-offset-3 col-lg-9',)
                ),css_class="card"
            ),id="filters", css_class="collapse"
        )
    )
class SecTieAutHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        Div(
            Div(
                Div(
                    Div('sector_1','sector_2'),
                    Div(Submit('submit', 'Aplicar Filtros',css_class='btn btn-primary'),css_class='col-lg-offset-3 col-lg-9',)
                ),css_class="card"
            ),id="filters", css_class="collapse"
        )
    )
class SecTieCamHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        Div(
            Div(
                Div(
                    Div('sector_1','sector_2'),
                    Div(Submit('submit', 'Aplicar Filtros',css_class='btn btn-primary'),css_class='col-lg-offset-3 col-lg-9',)
                ),css_class="card"
            ),id="filters", css_class="collapse"
        )
    )
class SecTieOmnHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-lg-2'
    field_class = 'col-lg-8'
    form_method = 'GET'
    layout = Layout(
        Div(
            Div(
                Div(
                    Div('sectorO_1','sectorO_2'),
                    Div(Submit('submit', 'Aplicar Filtros',css_class='btn btn-primary'),css_class='col-lg-offset-3 col-lg-9',)
                ),css_class="card"
            ),id="filters", css_class="collapse"
        )
    )
choices = ((0,"Por defecto"),(1,"Si"),('',"No"))
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
                Div(HTML('<h5>Transporte</h5>'), style="margin-left: 40px;"),
                Div(HTML('<div><label class="checkbox-inline"><input type="checkbox" id = "checkTransporte" name = "checkT" value = "-1" checked> Por defecto </label></div>'),
                    Div(InlineCheckboxes('tipoTransporte',style="margin-left: 10px;text-transform:capitalize;"),id='transporteDiv', style="display: none;margin-left: 20px;"),style="margin-left: 80px;")
            ),
            Div(
                Div(HTML('<h5>Trabaja</h5>'), style="margin-left: 40px;"),
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
                Div(HTML('<div> <label class="checkbox-inline"><input type="checkbox" id = "checkDiasEjecutar" name = "checkDias" value = "-1" checked> Todos </label></div>'),
                    Div(InlineCheckboxes('dias'),id='diasDivEjecutar', style="display: none;margin-left: 20px;"),style="margin-left: 80px;")
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
    layout = Layout(
            Div(
                Div(HTML('<h5>Transporte</h5>'), style="margin-left: 40px;"),
                Div(InlineRadios('tipoTransporte', style="margin-left: 10px;text-transform:capitalize;"),style="margin-left: 30px;")

            ),
            Div(
                Div(HTML('<h5>Anclas Temporales</h5>'), style="margin-left: 40px;"),
                Div(HTML('<label class="checkbox-inline"><input type="checkbox" name = anclaTra id="inlineCheckbox1" value="1" checked> Trabajo </label>'),
                    HTML('<label class="checkbox-inline" style="margin-left: 10px;"><input type="checkbox" name = anclaJar id="inlineCheckbox2" value="1" checked> Jardin </label>'),style="margin-left: 65px;"
                )

            ),
            Div(
                Div(HTML('<h5>Prestadores</h5>'), style="margin-left: 40px;"),
                Div(InlineRadios('prestadorFiltro'), style="margin-left: 50px;")

            ),
            Div(
                Div(HTML('<h5>Dias</h5>'), style="margin-left: 40px;"),
                Div(HTML('<div> <label class="checkbox-inline"><input type="checkbox" id = "checkDiasSimular" name = "checkDias" value = "-1" checked> Todos </label></div>'),
                    Div(InlineCheckboxes('dias'),id='diasDivSimular', style="display: none;margin-left: 20px;"),style="margin-left: 65px;")
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
                Div(HTML('<label class="checkbox-inline"><input type="checkbox" id="cbCSV1" name="checkRango" value="-1" checked> Descargar como .csv</label></br>'),style="margin-left: 80px;")
                
            ),
            Div(
                Div(HTML('<h5>Resultados a generar</h5>'), style="margin-left: 40px;"),
                Div(HTML('<label class="checkbox-inline"><input type="checkbox" name="generarIndividual" value="1" checked> Simulación </label></br><label class="checkbox-inline"><input type="checkbox"id="cbCSV2" name="generarResumen" value="1"> Resumen</label></br>'),style="margin-left: 80px;")                
            ),
        Div(Div(Submit('submit', 'Calcular',css_class='btn-primary')), style="text-align: center;")
        
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

