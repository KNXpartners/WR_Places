from django.forms import modelform_factory
from .models import Places, jobsite
from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext




PlacesForm = modelform_factory(Places,
fields=('Name', 'DesignNumber', 'Description', 'Type'),

)

jobsiteForm = modelform_factory(jobsite,
fields=('Name', 'Description',  'Address', 'Owner'),
)


class WizNormalRoom(forms.Form):
    # qty_of_sockets = forms.BooleanField()
    name_of_the_place = forms.CharField(
        max_length=30,
        min_length=1,
        strip=True,
        empty_value='Room name',
        required=True,
        label ='Name of the place',
        help_text= 'enter name of the room',
        )
    qty_of_sockets = forms.ChoiceField(choices=list(zip(range(2, 13), range(2, 13))), help_text=_('number of sockets'))
    number_of_light = forms.ChoiceField(choices=list(zip(range(2, 13), range(2, 13))), help_text=_('number of light points'))
