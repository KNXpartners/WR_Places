from django.forms import modelform_factory
from .models import Places, jobsite




PlacesForm = modelform_factory(Places,
fields=('Name', 'DesignNumber', 'Description', 'Type'),

)

jobsiteForm = modelform_factory(jobsite,
fields=('Name', 'Description',  'Address', 'Owner'),
)
