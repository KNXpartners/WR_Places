from django.shortcuts import render
from .models import Places, jobsite, PlaceType,Place2Place
from Wires.models import WirePurpose, Wire
from .forms import PlacesForm, jobsiteForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse,reverse_lazy
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.views.generic import (
        ListView,
        DetailView,
        CreateView,
        UpdateView,
        DeleteView,
        base
)
from django.db.models import F, Case, Value, When, Count
from django.http import Http404, HttpResponseNotFound,HttpResponseRedirect
from Devices.forms import chooseDeviceType
from Devices.models import Device2Place, DeviceType, Device
import logging
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from django.utils.text import format_lazy
from django.contrib import messages
from django.db.models import F, Q
# from django.contrib.messages.views import SuccessMessageMixin
from utils import *




logger = logging.getLogger(__name__)
# print(__name__)


# class BreadcrumbMixin:
#     def breadcrumb_list(self, l, pk):
#         if jobsite.objects.filter(pk=pk).exists():
#             d={}
#             d['place_pk'] =pk
#             d['Name'] = jobsite.objects.get(pk=pk)#.Name
#             d['url'] ='place-view'
#             d['type'] = 'jobsite'
#             l.insert(0, d)
#             return l
#         else:
#             d={}
#             d['place_pk'] =pk
#             d['Name'] = Places.objects.get(pk=pk)#.Name
#             d['url'] ='place-view'
#             d['type'] = 'place'
#             l.insert(0, d)
#             p = Places.objects.get(pk=pk)
#             par_pk = Places.objects.get(places_place2places_Parent__Child = p).pk
#             self.breadcrumb_list(l, par_pk)


class jobsiteCreateView(LoginRequiredMixin, CreateView):
    model = jobsite
    form_class  = jobsiteForm
    # extra_context = {'title': _(''), 'submit_button_name' : _('create') + ' ' + _('jobsite'),
    # 'parent_place': _('jobsite') + ' ' + _('list'),
    # 'parent_url' : reverse('jobsite-list')
    # }

    def form_valid(self, form):
        form.instance.Author = self.request.user #fix jobsite to User
        form.instance.Type  = PlaceType.objects.get(pk=1) # fix Place to jobsite type
        _mes = _('jobsite') + ' ' + str(form.instance) + ' ' + _('created')
        messages.success(self.request, _mes)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        user=get_object_or_404(User, pk=self.request.user.pk)
        # print('foo = ', self.request.GET.get('foo', None))
        # print('ttype = ', self.request.GET.get('ttype', None))
        context = super().get_context_data(**kwargs)
        context.update(self.kwargs)
        context['parent_url'] = reverse_lazy('jobsite-list')
        context['title'] = _('create jobsite')
        context['submit_button_name'] = _('create jobsite')
        context['parent_place'] = _('jobsite list')
        print(context)
        return context


# class jobsiteDetailsView(LoginRequiredMixin, ListView):
#     # model = Place2Place
#     # form_class  = jobsiteForm
#     # context_object_name = 'jobsites'
#
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         logger.info(f'jobsiteDetailsView kwargs: {self.kwargs}')
#         context.update(self.kwargs)
#
#         context['action'] = _('jobsite details')
#         context['js'] = jobsite.objects.get(pk=self.kwargs['pk'])
#         print('id=', context['js'].id)
#         # context['title'] = 'places'
#         # context['btn_text'] = 'add place'
#
#         return context
#
#     def get_queryset(self): #list of childs
#         user=get_object_or_404(User, pk=self.request.user.pk)#change to current user
#         # qs = User.objects.get(pk=1)
#         # print(jobsite.objects.filter(Author = user))
#         return Place2Place.objects.filter(Parent = self.kwargs['pk'])


class jobsiteListView(LoginRequiredMixin, ListView):
    # model = jobsite
    context_object_name = 'jobsites'
    ordering = ['-date']
    paginate_by = 2

    def get_queryset(self):
        user=get_object_or_404(User, pk=self.request.user.pk)#change to current user
        # print(user)
        return jobsite.objects.filter(Author = self.request.user)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.user.get_full_name()
        # print(context['username'] )
        return context


class JobsiteUpdateView(LoginRequiredMixin, UpdateView):
    model = jobsite
    pk_url_kwarg = 'place_pk'
    form_class  = jobsiteForm
    # extra_context = {'title': gettext_lazy('edit') + ' ' + gettext_lazy('jobsite')}

    def get_context_data(self, **kwargs):
        user=get_object_or_404(User, pk=self.request.user.pk)
        # print('foo = ', self.request.GET.get('foo', None))
        # print('ttype = ', self.request.GET.get('ttype', None))
        context = super().get_context_data(**kwargs)
        # pr(context, 'debug')
        # pr(self.kwargs, 'info')
        context.update(self.kwargs)
        # logger.info(f'!!!!!!!!!!  kwargs:{self.kwargs}||| context:{context}' )
        _js_pk = self.kwargs['place_pk']
        _js = Places.objects.get(pk=_js_pk)
        context['title'] = _('edit') + ' ' + _('jobsite')
        context['type'] = _js.Type.Name
        context['submit_button_name'] = _('update') +' '+_('jobsite')
        context['parent_place'] = str(_js)
        context['parent_url'] = self.object.get_absolute_url()
        # pr(context, 'debug')
        return context

    # def form_valid(self, form):
    #     _r = form.save(commit=True)
    #     # print('r:', _r.pk)
    #     _mes = gettext_lazy('jobsite %(p)s updated') % {'p':self.object}
    #     messages.info(self.request, _mes)

        # return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        # pr('self.obj' + str(self.object), 'debug')
        _mes = gettext_lazy('jobsite %(p)s updated') % {'p':self.object}
        messages.info(self.request, _mes)

        return super().form_valid(form)


class placeView(LoginRequiredMixin, ListView):
    context_object_name = 'places'
    paginate_by = 6
    paginate_orphans = 1

    def get_context_data(self, **kwargs):
        # self.user=get_object_or_404(User, pk=self.request.user.pk)
        # print('foo = ', self.request.GET.get('foo', None))
        # print('ttype = ', self.request.GET.get('ttype', None))
        context = super().get_context_data(**kwargs)
        context.update(self.kwargs)
        logger.info(f'!!!!!!!!!!  kwargs:{self.kwargs}||| context:{context}' )
        pk = self.kwargs['place_pk']
        p = Places.objects.select_related('Type').get(pk=pk)
        context['type'] = p.Type.Name
        context['place'] = p
        # context['btn_text'] = 'add place to '
        context['child_count'] = Places.objects.filter(places_place2places_Child__Parent_id = pk).count()
        context['device_count'] = Device2Place.objects.filter(Parent_id = pk).count()
        if context['device_count'] or context['child_count'] :
            context['delete_button']  = 'disabled'
        # context['form_create'] = chooseDeviceType(initial={'connected_to_place':pk, 'type_of_variant':1})
        ls =[]
        if context['type'] == 'jobsite':
            '''jobsite '''
            js = jobsite.objects.select_related('Author').get(pk=pk)
            self.author = js.Author
            #Places.objects.get(pk=pk).jobsite.Author - variant
            if self.author != self.user:
                context['action'] = 'forbidden'
                raise Http404 #return context
            context['jobsite'] = js
            # self.breadcrumb_list(ls, pk)
            # context['breadcrumb'] = ls

            js_pk= pk
            context['statistic'] = {}
            context['statistic']['places'] = {}
            _places = Places.objects.filter(places_place2places_Child__jobsite_id=js_pk)
            context['statistic']['places']['abstract'] = _places.filter(Type__Abstract = True).count()
            context['statistic']['places']['not_abstract'] = _places.filter(Type__Abstract = False).count()
            context['statistic']['places']['all_places_qty'] = _places.count()
            context['statistic']['places']['type']={}
            for t in PlaceType.objects.all().exclude(Name= 'jobsite'):
                context['statistic']['places']['type'][t.Name] = _places.filter(Type__Name = t.Name).count()

            context['statistic']['wire']={}
            context['statistic']['wire']['WirePurpose']={}
            wpc = WirePurpose.objects.annotate(c = Count(Case(When(wires_wires_Type__jobsite_id = js_pk, then=1))))
            for w in wpc:
                context['statistic']['wire']['WirePurpose'][w.Name] = w.c
            # for w in WirePurpose.objects.all():
            #     context['statistic']['wire']['WirePurpose'][w.Name]= Wire.objects.filter(jobsite_id=js_pk, WirePurpose = w).count()

            context['statistic']['device']={}
            context['statistic']['device']['type']={}
            #Translation

            dtc = DeviceType.objects.annotate(c = Count(Case(When(devices_devices_Type__devices_device2places_Device__jobsite_id = js_pk, then=1))))
            for d in dtc:
                # d.c = Device.objects.filter(Type = d, devices_device2places_Device__jobsite = js).count()
                if d.c != 0:
                    context['statistic']['device']['type'][d.Name.lower()] = d.c
                else:
                    context['statistic']['device']['type'][d.Name.lower()] = None
            # for d in DeviceType.objects.all():
            #     _c = Device.objects.filter(Type = d, devices_device2places_Device__jobsite = js).count()
            #     if _c != 0:
            #         context['statistic']['device']['type'][d.Name.lower()] = _c
            #     else:
            #         context['statistic']['device']['type'][d.Name.lower()] = None
            context['title'] = p.Name
            context['parent_url'] = reverse('jobsite-list')
            context['back_to_button'] = _('jobsite list')
            logger.info(f'context: {context}')
            '''jobsite end'''
        else:
            ''' not jobsite, -plain place'''
            js = Places.objects.get(pk=pk).places_place2place_Child.get().jobsite
            author = js.Author

            # author = jobsite.objects.get(pk=js.pk).Author
            if author != self.user:
                context['action'] = 'forbidden'
                raise Http404 #return context

            context['jobsite'] = js
            context['title'] = p.Name
            context['action'] = context['type'] + ' details'
            context['parent'] = Place2Place.objects.get(Child = p).Parent#doubtful ambiguous
            # query for Devices for this places
            # context['devices'] = Device2Place.objects.filter(Parent__id = pk)
            context['listOfTypes'] = []
            list_of_devices =[]
            context['dev'] ={}
            #collect data for list of devices in this place
            for n in DeviceType.objects.all():
                # print(n, pk)
                # context[n.Name] =[]
                d = Device.objects.filter(devices_device2places_Device__Parent__id = pk,
                                        devices_device2places_Device__Child__Type = n)
                if d.exists():
                    context['dev'][n.Name] = list(d.values())
                    # context['dev'][n.Name] = list(Device.objects.filter(devices_device2places_Device__Parent__id = pk,
                    #                         devices_device2places_Device__Child__Type__Name = n.Name).values())
                    # print(context['dev'][n.Name])

                #     for ld in context['dev'][n.Name]:
                #         # print ('!!!!!!!!!!!!!!ld', ld)
                #         if 'WireTo_id' in ld and ld['WireTo_id'] :
                #             ld['WireTo_Name'] = Device.objects.get(pk = ld['WireTo_id']).Name
                #             ld['placed_at'] = Device2Place.objects.get(Child__id = ld['id']).Parent.Name
                # if n.Name in context['dev']:
                #     list_of_devices.append(n.Name)

            # context['listOfDevice'] = list_of_devices
            # print(context['dev'])
            # print('list_of_devices==', list_of_devices)
            # ls =[]
            #
            #
            # self.breadcrumb_list(ls, pk)
            # # context['place_level'] = len(ls)
            # context['breadcrumb'] = ls
            context['parent_url'] = context['parent'].get_absolute_url()
            context['back_to_button'] = context['parent']
            ''' not jobsite, - plain place end'''
        context['breadcrumb'] = breadcrumb_list(self, place_pk = pk)
        # print('context : ' , context)
        logger.info(f'This is context {self.cls_name }: {context}')
        return context

    @property #get class name
    def cls_name(self):
        return self.__class__.__name__


    def get_queryset(self): #list of childs
        # user=get_object_or_404(User, pk=self.request.user.pk)#change to current user
        # user_jobsites = jobsite.objects.filter(Author = user)
        # p2p_qs_by_user_and_jobsite = Place2Place.objects.filter(jobsite)
        # qs = User.objects.get(pk=1)
        # print(jobsite.objects.filter(Author = user))
        # return Place2Place.objects.all().exclude(Parent = F('Child')).filter(Parent__id = self.kwargs['place_pk'])

        self.user = get_object_or_404(User, pk=self.request.user.pk)
        pk = self.kwargs['place_pk']
        p = Places.objects.get(pk=pk)
        if p.Type.Name == 'jobsite':
            js = jobsite.objects.get(pk=pk)
        else:
            js = Places.objects.get(pk=pk).places_place2place_Child.first().jobsite
        author = js.Author
        # print(pk, p, js, js.pk)
        # print(js.Author, self.user)
        logger.warning(f'user= {self.user}, author = {author}')
        if author != self.user:
            # return Places.objects.none()
            raise Http404('wrong user for this place')
        return Places.objects.filter(places_place2places_Child__Parent_id = pk)


class placeCreateView(LoginRequiredMixin,CreateView):
    model = Places
    form_class = PlacesForm
    # success_message = "%(Name)s was created successfully"

    # def get_success_message(self, cleaned_data):
    #     print('object', self.object)
    #     print('cleaned_data :',cleaned_data)
    #
    #     return "%(inst)s was created successfully" % {'inst': self.object}

    def form_valid(self, form):
        self.object = form.save(commit = False)
        # print('place form DN:', self.object.DesignNumber)
        # logger.info(f'form placeCreateView: {form}')
        #collect all DesignNumber to compare
        # print(self.request)
        # print('object pk', self.object.pk)

        _r = form.save(commit=True)
        # print('r:', _r.pk)
        _mes = gettext_lazy('Place %(p)s created') % {'p':self.object}
        messages.success(self.request, _mes)

        parent_place_pk = self.request.GET.get('place', None)
        if not parent_place_pk:
            raise Http404('no parent place pk')
        self.parent = Places.objects.get(pk=parent_place_pk)
        if self.parent.Type.Name == 'jobsite':
            self.js = jobsite.objects.get(pk=parent_place_pk)
        else:
            self.js = self.parent.places_place2place_Child.get().jobsite
            # parent_abstract = self.parent.places_place2place_Child.first().ParentAbstract
        if not self.object.Type.Abstract:
            if self.parent.Type.Abstract:
                parent_abstract = self.parent
            else:
                parent_abstract = self.parent.places_place2place_Child.get().ParentAbstract
            #check DesignNumber
            design_numbers_at_abstract = Places.objects.filter(places_place2places_Child__Parent = parent_abstract).exclude(pk = _r.pk).values_list('DesignNumber', flat=True)
            # print(Places.objects.filter(DesignNumber = self.object.DesignNumber).exclude(pk = _r.pk).exists())
            # print(design_numbers_at_abstract	)
            if Places.objects.filter(DesignNumber = self.object.DesignNumber, places_place2places_Child__Parent = parent_abstract).exclude(pk = _r.pk).exists():
                # _existing_place = []
                # Places.objects.filter(DesignNumber = self.object.DesignNumber, places_place2places_Child__Parent = parent_abstract).exclude(pk = _r.pk):
                _mes = _('you have place with same Design Nimber #')
                _mes +=( f'{self.object.DesignNumber} -- ')
                _mes += (f"{', '.join(str(x) for x in Places.objects.filter(DesignNumber = self.object.DesignNumber, places_place2places_Child__Parent = parent_abstract).exclude(pk = _r.pk) )}")
                    # _mes += (f'- {x}' for x in _existing_place)
                messages.info(self.request, _mes)
                # print('number repeat')
        else:
            # parent_abstract = None
            parent_abstract = self.parent
        # logger.info(f'parent abstract - {parent_abstract}')
        self.new_connection_to_place = Place2Place.objects.create(
            Child = self.object,
            Parent = self.parent,
            jobsite = self.js,
            ParentAbstract = parent_abstract,
            )
        logger.info(f'Add {self.object} to place- {self.new_connection_to_place}')
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('place-view',
        kwargs = {'place_pk':self.object.pk })

    @property #get class name
    def cls_name(self):
        return self.__class__.__name__

    def get_context_data(self, **kwargs):
        user=get_object_or_404(User, pk=self.request.user.pk)
        context = super().get_context_data(**kwargs)
        context.update(self.kwargs)
        # pk = self.kwargs['place_pk']
        # p = Places.objects.get(pk=pk)
        context['title'] = _('create place')
        context['parent_place'] = Places.objects.get(pk=self.request.GET.get('place', None))
        context['parent_url'] = context['parent_place'].get_absolute_url()

        context['form'].fields['Type'].choices = [(k[0],_(k[1])) for k in PlaceType.objects.filter(places_inheritances_Child__Parent__Name = context['parent_place'].Type).values_list('id', 'Name')]
        # context['form'].fields['Type'].queryset = PlaceType.objects.filter(
        # places_inheritances_Child__Parent__Name = context['parent_place'].Type)

        # context['form'].fields['Type'].queryset = PlaceType.objects.all().exclude(Name__in = ['jobsite',])
        # ls =[]
        # self.breadcrumb_list(ls, context['parent_place'].pk)
        # ls.append({'Name':_('create place'),
        #     'place_pk': 1,
        #     'url': 'place-view',
        #     'type' : 'place'})
        # context['breadcrumb'] = ls
        context['breadcrumb'] = breadcrumb_list(self, place_pk = context['parent_place'].pk)
        # pr(context['breadcrumb'], 'debug')
        if context['parent_place']:
            if context['parent_place'].Type.Name == 'jobsite':
                js = jobsite.objects.get(pk=context['parent_place'].pk)
                self.author = js.Author
                if self.author != user:
                    context['action'] = 'forbidden'
                    raise Http404 #return context
                context['jobsite'] =js
            else:
                js = Places.objects.get(pk=context['parent_place'].pk).places_place2place_Child.get().jobsite
                author = js.Author
                if author != user:
                    context['action'] = 'forbidden'
                    raise Http404 #return context
                context['jobsite'] = js

        logger.info(f'context {{self.cls_name}}: {context}')
        self.context = context
        return context


class PlaceUpdateView(LoginRequiredMixin, UpdateView):
    model = Places
    fields = ('Name', 'DesignNumber', 'Description')
    # form_class = PlacesForm
    pk_url_kwarg = 'place_pk'
    template_name = 'Places/place_update_form.html'

    def get_context_data(self, **kwargs):
        user=get_object_or_404(User, pk=self.request.user.pk)
        context = super().get_context_data(**kwargs)
        context.update(self.kwargs)
        # pk = self.kwargs['place_pk']
        # p = Places.objects.get(pk=pk)
        context['title'] = _('edit')+ ' ' + _('place')
        context['place'] = Places.objects.get(pk=self.kwargs['place_pk'])
        context['parent_place'] = Place2Place.objects.get(Child = context['place']).Parent
        context['parent_url'] = context['place'].get_absolute_url()
        context['submit_button_name'] = _("update") + ' ' + str(context['place'])
        # context['form'].fields['Type'].queryset = PlaceType.objects.filter(
        # places_inheritances_Child__Parent__Name = context['parent_place'].Type)
        # context['form'].fields['Type'].queryset = PlaceType.objects.all().exclude(Name__in = ['jobsite',])
        # ls =[]
        # self.breadcrumb_list(ls, context['parent_place'].pk)
        context['breadcrumb'] = breadcrumb_list(self, place_pk = context['parent_place'].pk)
        _note = _('update place')
        _note += " "+str(context['place'])
        context['breadcrumb'].append({'Name':_note ,
            'place_pk': self.kwargs['place_pk'],
            'url': 'place-update-view',
            'type' : 'place'})
        # pr(context['breadcrumb'], 'debug')
        # context['breadcrumb'] = ls

        if context['parent_place']:
            if context['parent_place'].Type.Name == 'jobsite':
                js = jobsite.objects.get(pk=context['parent_place'].pk)
                self.author = js.Author
                if self.author != user:
                    context['action'] = 'forbidden'
                    raise Http404 #return context
                context['jobsite'] =js
            else:
                js = Places.objects.get(pk=context['parent_place'].pk).places_place2place_Child.get().jobsite
                author = js.Author
                if author != user:
                    context['action'] = 'forbidden'
                    raise Http404 #return context
                context['jobsite'] = js

        logger.info(f'context : {context}')
        self.context = context
        return context

    def form_valid(self, form):
        # self.object = form.save(commit = False)
        # print('place form DN:', self.object.DesignNumber)
        # logger.info(f'form placeCreateView: {form}')
        #collect all DesignNumber to compare
        # print(self.request)
        # print('object pk', self.object.pk)

        _r = form.save(commit=True)
        # print('r:', _r.pk)
        _mes = gettext_lazy('Place %(p)s updated') % {'p':self.object}
        messages.info(self.request, _mes)

        self.parent = Place2Place.objects.get(Child = self.object).Parent
        if self.parent.Type.Name == 'jobsite':
            self.js = self.parent
        else:
            self.js = self.object.places_place2place_Child.get().jobsite
        # parent_abstract = self.parent.places_place2place_Child.first().ParentAbstract
        if self.object.Type.Abstract:
            _filter = {'DesignNumber':self.object.DesignNumber,
                        'places_place2places_Child__Parent':self.parent,
                        'Type':self.object.Type,
                        }
            if Places.objects.filter(**_filter).exclude(pk = _r.pk).exists():
                _mes = _('you have place with same Design Number #')
                _mes +=( f'{self.object.DesignNumber} @{self.parent} -- ')
                _mes += (f"{', '.join(str(x) for x in Places.objects.filter(**_filter).exclude(pk = _r.pk) )}")
                messages.info(self.request, _mes)
        else:
                #check DesignNumber
            parent_abstract = Place2Place.objects.get(Child = self.object).ParentAbstract
            # design_numbers_at_abstract = Places.objects.filter(places_place2places_Child__Parent = parent_abstract).exclude(pk = _r.pk).values_list('DesignNumber', flat=True)
            # print(Places.objects.filter(DesignNumber = self.object.DesignNumber).exclude(pk = _r.pk).exists())
            # print(design_numbers_at_abstract	)
            _filter = {'DesignNumber':self.object.DesignNumber,
                        'places_place2places_Child__Parent':parent_abstract,
                        'Type__Abstract':False,
                        }
            if Places.objects.filter(**_filter).exclude(pk = _r.pk).exists():
                # _existing_place = []
                # Places.objects.filter(DesignNumber = self.object.DesignNumber, places_place2places_Child__Parent = parent_abstract).exclude(pk = _r.pk):
                _mes = _('you have place with same Design Nimber #')
                _mes +=( f'{self.object.DesignNumber} @{parent_abstract} -- ')
                _mes += (f"{', '.join(str(x) for x in Places.objects.filter(**_filter).exclude(pk = _r.pk) )}")
                    # _mes += (f'- {x}' for x in _existing_place)
                messages.info(self.request, _mes)
                # print('number repeat')
        # logger.info(f'parent abstract - {parent_abstract}')
        # self.new_connection_to_place = Place2Place.objects.create(
        #     Child = self.object,
        #     Parent = self.parent,
        #     jobsite = self.js,
        #     ParentAbstract = parent_abstract,
        #     )
        logger.info(f'Update {self.object}')
        return HttpResponseRedirect(self.get_success_url())


class placeDeleteView(LoginRequiredMixin, DeleteView):
    model = Places
    pk_url_kwarg = 'place_pk'
    # form_class = PlacesForm
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.place_pk = self.kwargs['place_pk']
        if jobsite.objects.filter(pk = self.place_pk).exists():
            # context['parent'] = jobsite.objects.get(pk = self.place_pk)
            context['parent'] = None
        else:
            context['parent'] = Place2Place.objects.get(Child__id = self.place_pk).Parent
        # pr('PArent :' + str(context['parent']),'debug')
        # ls =[]
        # self.breadcrumb_list(ls, self.place_pk)
        # context['breadcrumb'] = ls
        context['breadcrumb'] = breadcrumb_list(self, self.place_pk)
        context['device_list'] = Device.objects.filter(devices_device2places_Device__Parent_id = self.place_pk)
        context['submit_button_text'] = _("delete") + ' ' + str(self.object)
        logger.info(f'context of placeDeleteView: {context}')
        return context

    @property #get class name
    def cls_name(self):
        return self.__class__.__name__

    def get_success_url(self, **kwargs):
        parent_place = self.get_context_data(**kwargs)['parent']
        logger.info(f'{self.cls_name} context : {parent_place}')
        # parent = Place2Place.objects.get(Child__id = self.kwargs['place_pk']).Parent
        if parent_place:
            return reverse('place-view', kwargs={'place_pk': parent_place.pk})
        else:
            return reverse('jobsite-list')

    def form_valid(self, form):
        # pr('self.obj' + str(self.object), 'debug')
        _mes = str(self.object) + ' ' +  _('deleted')
        messages.info(self.request, _mes)

        return super().form_valid(form)

    # def delete(self, request, *args, **kwargs):
    #     """Call the delete() method on the fetched object and then redirect to the success URL."""
    #     self.object = self.get_object()
    #     success_url = self.get_success_url()
    #     self.object.delete()
    #     return HttpResponseRedirect(success_url)


class JobsiteStructure(base.TemplateView):
    template_name = 'Places/jobsite_structure.html'

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        js_pk = self.request.GET.get('place', None)
        _js_str = gettext_lazy('jobsite')
        _structure = gettext_lazy('structure')
        # context['title'] = format_lazy('{_js_str} {_structure}',_js_str=_js_str, _structure=_structure  )
        context['title'] = _('jobsite') + ' ' + _('structure')
        #breadcrumb
        # l =[]
        # d={}
        # d['place_pk'] = js_pk
        # d['Name'] = context['title']
        # d['url'] ='place-view'
        # d['type'] = 'jobsite'
        # l.insert(0, d)
        # d={}
        # d['place_pk'] = js_pk
        # d['Name'] = jobsite.objects.get(pk=js_pk)#.Name
        # d['url'] ='place-view'
        # d['type'] = 'jobsite'
        # l.insert(0, d)
        # logger.info(f'breadcrumb {l}')
        context['breadcrumb'] = breadcrumb_list(self, place_pk = js_pk)
        context['breadcrumb'].append({'Name': _('Structure')})
        context['jobsite'] = get_object_or_404(jobsite, pk=js_pk)
        # print(context['jobsite'])


        logger.info(f'{context}')
        # print(context)
        def take_childs(parent):
            return Places.objects.filter(places_place2places_Child__Parent = parent).order_by('DesignNumber', 'Name')

        def get_all_places(place, d= None):
            if d is None:
                d = {}
            d[place] ={}
            if not Places.objects.filter(places_place2places_Child__Parent = place).exists():
                return d
            else:
                for p in take_childs(place):
                    # print('cycle :',str(p.Name))
                    d[place] =  get_all_places(p, d[place])
                return d
        gap = get_all_places(jobsite.objects.get(pk=js_pk))
        logger.info(f'structure dictionary {gap}')
        # context['structure'] = gap
        def printItems(dictObj, parent, indent, result_str = None):
            if result_str is None:
                result_str = ''
            if len(dictObj):
                # result_str += str('{}<ul>'.format('  ' * indent))
                result_str += (f'{"  " * indent}<ul>')
                for k,v in dictObj.items():
                    print(k, v)
                    print(type(k))
                    # result_str += str('{}<li id="{}-{}"><a href="{}">{}</a></li>'.format(
                    #     '  ' * (indent+1), k, parent, k.get_absolute_url() , k))
                    # if k == 'building':
                    #     result_str += str(f'{"  " * (indent+1)}<li id="{k}-{parent}"><a href="{k.get_absolute_url()}"><b>{k}</b></a></li>')
                    # else:
                    _cabinets = Device.objects.filter(Type__Name = 'Cabinet', devices_device2places_Device__Parent_id = k)
                    _cab_str = ''
                    for _cabinet in _cabinets:
                        _cab_str += '<a class="text-secondary small" href="'+_cabinet.get_absolute_url()+'"><b> ('+str(_cabinet.CabLabel)+')</b></a> '

                    result_str += (f'{"  " * (indent+1)}<li id="{k}-{parent}"><a href="{k.get_absolute_url()}">{k}</a>{_cab_str}</li>')
                    result_str += printItems(v, k, indent+1)
                result_str += (f'{"  " * indent}</ul>')
            else:
                return result_str
            return result_str
        web1=printItems(gap,'root', 0)
        # logger.info(f'html code: {web1}')
        context['html_code'] = web1
        context['statistic'] = {}
        place_all = Places.objects.filter(places_place2places_Child__jobsite_id=js_pk)
        context['abstract'] = place_all.filter(Type__Abstract = True).count()
        context['not_abstract'] = place_all.filter(Type__Abstract = False).count()
        context['all_places_qty'] = place_all.count()

        for t in PlaceType.objects.all().exclude(Name= 'jobsite'):
            context['statistic'][t.Name] = Places.objects.filter(places_place2places_Child__jobsite_id=js_pk, Type__Name = t.Name ).count()
        return context


def copy_example_js_to_user(request, **kwargs):
    user = get_object_or_404(User, pk=request.user.pk)
    js_pk = request.GET.get('js', None)
    if js_pk is None:
        raise Http404('no js pk')
    lang = request.LANGUAGE_CODE

    # print(user, js, lang)
    # print(reverse('jobsite-list'))

    copy_dict= {}
    copy_dict['place']= {}
    copy_dict['device']= {}
    new_js_pk = ''

    def copy_js(js_pk, user):
        js = jobsite.objects.get(pk= js_pk)
        js.id, js.pk = None, None
        amount = jobsite.objects.filter(Author = user, Name__istartswith = _('example')).count()
        js.Name = _('example')+ ' ' + _('jobsite' )+ ' #' + str(amount+1)
        js.Author = user
        js.save()
        js_new_pk = js.pk
        return js_new_pk

    def copy_entry(entry):
        entry.id, entry.pk = None, None
        entry.save()
        return entry.pk

    for p in Places.objects.filter( Q(places_place2places_Parent__jobsite = js_pk) | Q(places_place2places_Child__jobsite = js_pk) ).distinct().reverse():
        # pr('p_pk :' + str(p.pk)+str(js_pk), 'debug')
        p_copy = p.pk
        copy_dict['place'][p_copy] = {}
        # global new_js_pk
        if p.pk == int(js_pk):
            # pr('js_pk!!!!!!!', 'debug')
            new_js_pk = copy_js(js_pk, user = user)
            # pr('new_js_pk inside :' + str(new_js_pk), 'debug')
            copy_dict['place'][p_copy] = new_js_pk
        else:
            new_pk = copy_entry(p)
            copy_dict['place'][p_copy] = new_pk

    # pr('new_js_pk :' + str(new_js_pk), 'debug')

    for p2p in Place2Place.objects.filter(jobsite = js_pk):
        pr(str(p2p.Child)) 
        # pr(p2p +' ' +str(p2p.Child) +'  '+ str(p2p.Parent) + ' --- ' + p2p.ParentAbstract, 'info')
        if p2p.ParentAbstract:
            ParentAbstract = copy_dict['place'][p2p.ParentAbstract.id]
        else:
            ParentAbstract = None
        pr(ParentAbstract, 'info')
        new_p2p = Place2Place(
            Type = p2p.Type,
            Child_id = copy_dict['place'][p2p.Child.pk], \
            Parent_id = copy_dict['place'][p2p.Parent.pk],
            ParentAbstract_id = ParentAbstract,
            jobsite_id = new_js_pk
        )
        new_p2p.save()

    p = Places.objects.filter(places_place2places_Child__jobsite = js_pk).values('id')
    pr(str(p.count()), 'info')
    pr('count'+ str(Device.objects.filter(devices_device2places_Device__Parent_id__in = p).count()) + str(Device.objects.filter(devices_device2places_Device__jobsite_id = js_pk).count()), 'debug')
    for d in Device.objects.filter(devices_device2places_Device__jobsite_id = js_pk):
        d_copy = d.pk
        copy_dict['device'][d_copy]= copy_entry(d)

    for d2p in Device2Place.objects.filter(Child__in = Device.objects.filter(devices_device2places_Device__Parent_id__in = p)):
        # print(d2p.Child.pk,  '  :  ' , copy_dict['device'][d2p.Child.pk])
        new_d2p = Device2Place(
                Child_id = copy_dict['device'][d2p.Child.pk],
                Parent_id=copy_dict['place'][d2p.Parent.pk],
                jobsite_id = new_js_pk,
                Type= d2p.Type
        )
        new_d2p.save()

    for w in Wire.objects.filter(jobsite = js_pk):
        new_wire = Wire(Child_id = copy_dict['device'][w.Child.pk], Parent_id = copy_dict['device'][w.Parent.pk], WirePurpose = w.WirePurpose, WireVariant = w.WireVariant, jobsite_id = new_js_pk,
                       Length= w.Length, SerialNumber= w.SerialNumber)
        new_wire.save()





    return HttpResponseRedirect(reverse('jobsite-list'))


def delete_example_js(request, **kwargs):
    pass
