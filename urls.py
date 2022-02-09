from django.urls import path, include
from .import views
from django.conf import settings
from django.views.generic import TemplateView

# app_name = 'Places'

urlpatterns = [
    # path('', views.PlacesListView.as_view(), name='Places-list'),
    # path('<int:pk>/', views.PlaceDetailView.as_view(), name ='Place-details'),
    # path('delete/<int:pk>/', views.PlaceDeleteView.as_view(), name = 'Place-delete'),
    # path('update/<int:pk>/', views.PlaceUpdateView.as_view(), name = 'Place-update'),
    path('', TemplateView.as_view(template_name="manual/manual.html")),

    path('jobsitelist/',
    views.jobsiteListView.as_view(),
        name = 'jobsite-list'),
    path('create-jobsite/',
        views.jobsiteCreateView.as_view(),
        name = 'create-jobsite'),
    path('jobsite-structure/',
        views.JobsiteStructure.as_view(),
        name = 'jobsite-structure'),
    path('<int:place_pk>/',
        views.placeView.as_view(),
        name = 'place-view'),
    path('<int:place_pk>/delete/',
        views.placeDeleteView.as_view(),
        name = 'place-delete-view'),
    path('<int:place_pk>/update/',
        views.PlaceUpdateView.as_view(),
        name = 'place-update-view'),
    path('<int:place_pk>/js-update/',
        views.JobsiteUpdateView.as_view(),
        name = 'jobsite-update-view'),
    path('create/',
        views.placeCreateView.as_view(),
        name = 'place-create-view'),
    path('copy-js/',
        views.copy_example_js_to_user,
        name = 'copy-js'),

    # path('<int:place_pk>/device/',
    #     include ('Devices.urls')),

    ]
