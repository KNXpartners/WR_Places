from django.db import models
from django.utils import timezone
from account.models import Account
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from utils import pr
from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_delete
from django.conf import settings


# @receiver(pre_delete,sender= Places,dispatch_uid = 'delete child places' )
# def my_callback(sender, **kwargs):
#     # print("post_delete :", sender, type(kwargs['instance']), kwargs['instance'], kwargs['instance'].pk)
#     # dev = Device.objects.filter(devices_device2places_Device__Parent = kwargs['instance'])
#     # dev.delete()
#     object = kwargs['instance']
#     # deletable_objects, model_count, protected = get_deleted_objects([object])
#     # print(deletable_objects, model_count, protected)
#     if object.Type.Name == 'jobsite':
#         # print(p)
#         # print(Device.objects.filter(devices_device2places_Device__Parent_id__in = p).count())
#         # print(Device.objects.filter(devices_device2places_Device__jobsite = object).count())
#         p = Places.objects.filter(places_place2places_Child__jobsite = object).values('id')
#         pr('child places :'+str(p.count()), 'info')
#         # pr('count parent :'+ str(Device.objects.filter(devices_device2places_Device__Parent_id__in = p).count(
#         ))+'js:' + str(Device.objects.filter(devices_device2places_Device__jobsite = object).count()), 'debug')
#
#         print(p.delete())
#         # Places.objects.filter(places_place2places_Child__jobsite = object).delete()


# Create your models here.
class Places(models.Model):
    Name = models.CharField(_('Name of the place'), max_length=100, blank=True)
    Description = models.TextField(_('Description'), blank=True, max_length=500, )
    Type = models.ForeignKey(
        'PlaceType',
        on_delete=models.SET_NULL,
        null=True,
        default=1,
        verbose_name=_('place type'),
        related_name='%(app_label)s_%(class)s_related',
        related_query_name="%(app_label)s_%(class)ss",
    )
    Date = models.DateTimeField('Date of creation', auto_now_add=True, editable=False)
    DesignNumber = models.SmallIntegerField(verbose_name=_('number of'),
                                            help_text=_('..building, stage or flat from jobsite design'),
                                            default=None, null=True, blank=True,
                                            )
    
    class Meta:
        verbose_name = _('place')
        verbose_name_plural = _('places')
        ordering = ('-Date',)
    
    def __str__(self):
        if self.DesignNumber:
            return f'{self.Name} #{self.DesignNumber}'
        elif self.DesignNumber == 0:
            return f'{self.Name} #0'
        else:
            return f'{self.Name}'  # ({self.Type})'
    
    def get_absolute_url(self):
        pk = {}
        pk['place_pk'] = self.pk
        return reverse('place-view', kwargs=pk)
    
    # def delete(self, *args, **kwargs):
    # delete devices in this place
    # device_to_delete = Devices.Device.objects.filter(devices_device2places_Device__Place_id=self.pk)
    # print('Delete child Devices :', device_to_delete)
    # delete palces connected to this place
    # pr('DELETE : ' + str(self),'info')
    # pr(Places.objects.filter(places_place2places_Child__Parent_id=self.pk).delete(), 'info')
    # places_to_delete = Places.objects.filter(places_place2places_Child__Parent_id=self.pk)
    # print('Delete child places : ', places_to_delete)
    # for p in places_to_delete:
    #     p.delete()
    
    
    # super().delete(*args, **kwargs)


class jobsite(Places):
    Author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Author'),
        related_name='%(app_label)s_%(class)s_Author',
        related_query_name="%(app_label)s_%(class)ss_Author",
        on_delete=models.CASCADE)
    Address = models.TextField(blank=True)
    Owner = models.CharField(_('Name of the owner'), max_length=100, blank=True)
    
    def __str__(self):
        return f'{self.Name}'
    
    def get_absolute_url(self):
        pk = {}
        pk['place_pk'] = self.pk
        return reverse('place-view', kwargs=pk)


class PlaceType(models.Model):
    Name = models.CharField(verbose_name=_('name'), max_length=50, unique=True)
    Abstract = models.BooleanField(default=True)
    Short = models.CharField(max_length=3)
    
    # View_name = models.CharField(max_length = 100, blank=True, default ='/')
    
    class Meta:
        verbose_name = _('Place type')
        verbose_name_plural = _('Place types')
    
    def __str__(self):
        return self.Name


class Inheritance(models.Model):
    Child = models.ForeignKey(PlaceType, on_delete=models.CASCADE,
                              related_name='%(app_label)s_%(class)s_Child',
                              related_query_name="%(app_label)s_%(class)ss_Child",
                              )
    Parent = models.ForeignKey(PlaceType, on_delete=models.CASCADE,
                               related_name='%(app_label)s_%(class)s_Parent',
                               related_query_name="%(app_label)s_%(class)ss_Parent",
                               )
    
    class Meta:
        ordering = ['Parent__id']
    
    def __str__(self):
        return f'{self.Parent} > {self.Child}'


class Place2PlaceType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return f' {self.name}'


class Place2Place(models.Model):
    Type = models.ForeignKey(
        'Place2PlaceType',
        on_delete=models.SET_NULL,
        null=True,
        default=1,
        verbose_name='Type of the place',
        related_name='%(app_label)s_%(class)s_Type',
        related_query_name="%(app_label)s_%(class)ss_Type",
    )
    
    Child = models.ForeignKey(
        Places,
        on_delete=models.CASCADE,
        null=True,
        default=1,
        verbose_name='Child Places relation',
        related_name='%(app_label)s_%(class)s_Child',
        related_query_name="%(app_label)s_%(class)ss_Child",
    )
    
    Parent = models.ForeignKey(
        Places,
        on_delete=models.CASCADE,
        null=True,
        default=1,
        verbose_name='Parent Device2Places relation',
        related_name='%(app_label)s_%(class)s_Parent',  # property of instance. return set of related notes from Parent
        related_query_name="%(app_label)s_%(class)ss_Parent",
        # inside brackets filter(places_place2places_Child__Parent =
    )
    
    ParentAbstract = models.ForeignKey(
        Places,
        on_delete=models.SET_NULL,
        null=True,
        default=1,
        blank=True,
        verbose_name='Parent abstract place',
        related_name='%(app_label)s_%(class)s_AbstractPlace',
        # property of instance. return set of related notes from Parent
        related_query_name="%(app_label)s_%(class)ss_AbstractPlace",
    )
    
    jobsite = models.ForeignKey(jobsite,
                                verbose_name='jobsite',
                                related_name='%(app_label)s_%(class)s_js',
                                related_query_name="%(app_label)s_%(class)ss_js",
                                on_delete=models.CASCADE)


class TestPlace(models.Model):
    name = models.CharField(max_length=30)


class TestP2P(models.Model):
    Child = models.OneToOneField(TestPlace, on_delete=models.CASCADE, related_name='Places_TestP2P_Child')
    Parent = models.ForeignKey(TestPlace, on_delete=models.CASCADE, related_name='Places_TestP2P_Parent')
