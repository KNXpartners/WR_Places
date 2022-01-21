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
from django.db.models import F
from django.http import Http404, HttpResponseNotFound,HttpResponseRedirect
from Devices.forms import chooseDeviceType
from Devices.models import Device2Place, DeviceType, Device
import logging


logger = logging.getLogger(__name__)
# print(__name__)


class BreadcrumbMixin:
    def breadcrumb_list(self, l, pk):
        if jobsite.objects.filter(pk=pk).exists():
            d={}
            d['place_pk'] =pk
            d['Name'] = jobsite.objects.get(pk=pk)#.Name
            d['url'] ='place-view'
            d['type'] = 'jobsite'
            l.insert(0, d)
            return l
        else:
            d={}
            d['place_pk'] =pk
            d['Name'] = Places.objects.get(pk=pk)#.Name
            d['url'] ='place-view'
            d['type'] = 'place'
            l.insert(0, d)
            p = Places.objects.get(pk=pk)
            par_pk = Places.objects.get(places_place2places_Parent__Child = p).pk
            self.breadcrumb_list(l, par_pk)


class jobsiteCreateView(LoginRequiredMixin, CreateView):
    model = jobsite
    form_class  = jobsiteForm

    def form_valid(self, form):
        form.instance.Author = self.request.user #fix jobsite to User
        form.instance.Type  = PlaceType.objects.get(pk=1) # fix Place to jobsite type
        return super().form_valid(form)


class jobsiteDetailsView(LoginRequiredMixin, ListView):
    # model = Place2Place
    # form_class  = jobsiteForm
    # context_object_name = 'jobsites'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.info(f'jobsiteDetailsView kwargs: {self.kwargs}')
        context.update(self.kwargs)

        context['action'] = 'jobsite details (2)'
        context['js'] = jobsite.objects.get(pk=self.kwargs['pk'])
        print('id=', context['js'].id)
        # context['title'] = 'places'
        # context['btn_text'] = 'add place'

        return context

    def get_queryset(self): #list of childs
        user=get_object_or_404(User, pk=self.request.user.pk)#change to current user
        # qs = User.objects.get(pk=1)
        # print(jobsite.objects.filter(Author = user))
        return Place2Place.objects.filter(Parent = self.kwargs['pk'])


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


class placeView(LoginRequiredMixin, ListView, BreadcrumbMixin):
    #model = Places #have number of Place.ID
    # template  = 'Places_list'
    context_object_name = 'places'
    paginate_by = 6

    # def get(self, request, *args, **kwagrs):
    #     # either
    #     # self.object_list = self.get_queryset()
    #     # self.object_list = self.object_list.filter(lab__acronym=kwargs['lab'])
    #     print(self.kwargs)
    #     context = self.get_context_data()
    #     return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        user=get_object_or_404(User, pk=self.request.user.pk)
        # print('foo = ', self.request.GET.get('foo', None))
        # print('ttype = ', self.request.GET.get('ttype', None))
        context = super().get_context_data(**kwargs)
        context.update(self.kwargs)
        logger.info(f'!!!!!!!!!!  kwargs:{self.kwargs}||| context:{context}' )
        pk = self.kwargs['place_pk']
        p = Places.objects.get(pk=pk)
        context['type'] = p.Type.Name
        context['place'] = p
        context['btn_text'] = 'add place to '
        context['child_count'] = Places.objects.filter(places_place2places_Child__Parent_id = pk).count()
        context['device_count'] = Device2Place.objects.filter(Parent_id = pk).count()
        # context['form_create'] = chooseDeviceType(initial={'connected_to_place':pk, 'type_of_variant':1})
        ls =[]



        if p.Type.Name == 'jobsite':
            '''jobsite '''
            self.author = jobsite.objects.get(pk=pk).Author
            #Places.objects.get(pk=pk).jobsite.Author - variant
            if self.author != user:
                context['action'] = 'forbidden'
                raise Http404 #return context
            js = jobsite.objects.get(pk=pk)
            context['jobsite'] =js
            self.breadcrumb_list(ls, pk)
            context['breadcrumb'] = ls

            js_pk= pk
            context['statistic'] = {}
            context['statistic']['places'] = {}
            context['statistic']['places']['abstract'] = Places.objects.filter(places_place2places_Child__jobsite_id=js_pk, Type__Abstract = True).count()
            context['statistic']['places']['not_abstract'] = Places.objects.filter(places_place2places_Child__jobsite_id=js_pk, Type__Abstract = False).count()
            context['statistic']['places']['all_places_qty'] = Places.objects.filter(places_place2places_Child__jobsite_id=js_pk).count()
            context['statistic']['places']['type']={}
            for t in PlaceType.objects.all().exclude(Name= 'jobsite'):
                context['statistic']['places']['type'][t.Name] = Places.objects.filter(places_place2places_Child__jobsite_id=js_pk, Type__Name = t.Name ).count()

            context['statistic']['wire']={}
            context['statistic']['wire']['WirePurpose']={}
            for w in WirePurpose.objects.all():
                context['statistic']['wire']['WirePurpose'][w.Name]= Wire.objects.filter(jobsite_id=js_pk, WirePurpose = w).count()

            context['statistic']['device']={}
            context['statistic']['device']['type']={}
            for d in DeviceType.objects.all():
                context['statistic']['device']['type'][d.Name] = Device.objects.filter(Type = d, devices_device2places_Device__jobsite = js).count()

            logger.info(f'context: 0x0000026912596460 {context}')
            '''jobsite end'''
        else:
            ''' not jobsite, -plain place'''
            js = Places.objects.get(pk=pk).places_place2place_Child.first().jobsite
            author = jobsite.objects.get(pk=js.pk).Author
            if author != user:
                context['action'] = 'forbidden'
                raise Http404 #return context

            context['jobsite'] = js
            context['title'] = p.Name
            context['action'] = context['type'] + ' details'
            context['parent'] = Place2Place.objects.filter(Child = p).first().Parent#doubtful ambiguous
            # query for Devices for this places
            context['devices'] = Device2Place.objects.select_related('Child').filter(Parent__id = pk)
            context['listOfTypes'] = []
            list_of_devices =[]
            context['dev'] ={}
            #collect data for list of devices in this place
            for n in DeviceType.objects.all():
                print(n, pk)
                # context[n.Name] =[]
                d = Device.objects.filter(devices_device2places_Device__Parent__id = pk,
                                        devices_device2places_Device__Child__Type__Name = n.Name).exists()
                if d:
                    context['dev'][n.Name] = list(Device.objects.filter(devices_device2places_Device__Parent__id = pk,
                                            devices_device2places_Device__Child__Type__Name = n.Name).values())
                    # print(context['dev'][n.Name])
                    for ld in context['dev'][n.Name]:
                        # print ('!!!!!!!!!!!!!!ld', ld)
                        if 'WireTo_id' in ld and ld['WireTo_id'] :
                            ld['WireTo_Name'] = Device.objects.get(pk = ld['WireTo_id']).Name
                            ld['placed_at'] = Device2Place.objects.get(Child__id = ld['id']).Parent.Name
                if n.Name in context['dev']:
                    list_of_devices.append(n.Name)
            # context['listOfDevice'] = list_of_devices
            # print(context['dev'])
            # print('list_of_devices==', list_of_devices)
            ls =[]


            self.breadcrumb_list(ls, pk)
            # context['place_level'] = len(ls)
            context['breadcrumb'] = ls
            ''' not jobsite, - plain place end'''

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

        user=get_object_or_404(User, pk=self.request.user.pk)
        pk = self.kwargs['place_pk']
        p = Places.objects.get(pk=pk)
        if p.Type.Name == 'jobsite':
            js = jobsite.objects.get(pk=pk)
        else:
            js = Places.objects.get(pk=pk).places_place2place_Child.first().jobsite
        author = js.Author
        logger.warning(f'user= {user}, author = {author}')
        if author != user:
            # return Places.objects.none()
            raise Http404('wrong user for this place')
        return Places.objects.filter(places_place2places_Child__Parent_id = pk)


class placeCreateView(LoginRequiredMixin,CreateView,BreadcrumbMixin):
    model = Places
    form_class = PlacesForm

    def form_valid(self, form):
        self.object = form.save()
        # logger.info(f'form placeCreateView: {form}')

        parent_place_pk = self.request.GET.get('place', None)
        self.parent = Places.objects.get(pk=parent_place_pk)
        if self.parent.Type.Name == 'jobsite':
            self.js = jobsite.objects.get(pk=parent_place_pk)
        else:
            self.js = self.parent.places_place2place_Child.first().jobsite
            # parent_abstract = self.parent.places_place2place_Child.first().ParentAbstract
        if not self.object.Type.Abstract:
            if self.parent.Type.Abstract:
                parent_abstract = self.parent
            else:
                parent_abstract = self.parent.places_place2place_Child.first().ParentAbstract
        else:
            parent_abstract = None
        logger.info(f'parent abstract - {parent_abstract}')
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
        context = super().get_context_data(**kwargs)
        context.update(self.kwargs)
        context['title'] = 'add place'
        context['parent_place'] = Places.objects.get(pk=self.request.GET.get('place', None))
        context['form'].fields['Type'].queryset = PlaceType.objects.filter(
        places_inheritances_Child__Parent__Name = context['parent_place'].Type)
        # context['form'].fields['Type'].queryset = PlaceType.objects.all().exclude(Name__in = ['jobsite',])
        ls =[]
        self.breadcrumb_list(ls, context['parent_place'].pk)
        ls.append({'Name':'create place',
            'place_pk': 1,
            'url': 'place-view',
            'type' : 'place'})
        context['breadcrumb'] = ls

        logger.info(f'context {{self.cls_name}}: {context}')
        self.context = context
        return context


class placeDeleteView(LoginRequiredMixin, DeleteView, BreadcrumbMixin):
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
        ls =[]
        self.breadcrumb_list(ls, self.place_pk)
        context['breadcrumb'] = ls
        context['device_list'] = Device.objects.filter(devices_device2places_Device__Parent_id = self.place_pk)
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


class JobsiteStructure(base.TemplateView, BreadcrumbMixin):
    template_name = 'Places/jobsite_structure.html'

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        js_pk = self.request.GET.get('place', None)
        #breadcrumb
        l =[]
        d={}
        # d['place_pk'] = js_pk
        d['Name'] = 'jobsite structure'
        # d['url'] ='place-view'
        # d['type'] = 'jobsite'
        l.insert(0, d)
        d={}
        d['place_pk'] = js_pk
        d['Name'] = jobsite.objects.get(pk=js_pk)#.Name
        d['url'] ='place-view'
        d['type'] = 'jobsite'
        l.insert(0, d)
        logger.info(f'breadcrumb {l}')
        context['breadcrumb'] = l
        context['jobsite'] = get_object_or_404(jobsite, pk=js_pk)
        # print(context['jobsite'])
        context['title'] = 'jobsite structure'
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
        context['structure'] = gap
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
        context['abstract'] = Places.objects.filter(places_place2places_Child__jobsite_id=js_pk, Type__Abstract = True).count()
        context['not_abstract'] = Places.objects.filter(places_place2places_Child__jobsite_id=js_pk, Type__Abstract = False).count()
        context['all_places_qty'] = Places.objects.filter(places_place2places_Child__jobsite_id=js_pk).count()
        for t in PlaceType.objects.all().exclude(Name= 'jobsite'):
            context['statistic'][t.Name] = Places.objects.filter(places_place2places_Child__jobsite_id=js_pk, Type__Name = t.Name ).count()
        return context
