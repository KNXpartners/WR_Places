from django.urls import path, include
from .import views
from django.conf import settings
from Places.views import FirstPageView

# app_name = 'Places'

urlpatterns = [
    # path('', views.PlacesListView.as_view(), name='Places-list'),
    # path('<int:pk>/', views.PlaceDetailView.as_view(), name ='Place-details'),
    # path('delete/<int:pk>/', views.PlaceDeleteView.as_view(), name = 'Place-delete'),
    # path('update/<int:pk>/', views.PlaceUpdateView.as_view(), name = 'Place-update'),
    path('dummy_del_me', FirstPageView.as_view(template_name="manual/first-page-objectives.html"), name = 'fp-objectives'),
    path('objectives/', FirstPageView.as_view(template_name="manual/first-page-objectives.html"), name = 'fp-objectives'),
    path('stages/', FirstPageView.as_view(template_name="manual/first-page-stages.html"), name = 'fp-stages'),
    path('manual/', FirstPageView.as_view(template_name="manual/manual.html"), name = "fp-manual"),
    path('feedback/', FirstPageView.as_view(template_name="manual/first-page-feedback.html"), name = "fp-feedback"),

    path('',
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
        views.PlaceCreateView.as_view(),
        name = 'place-create-view'),
    path('copy-js/',
        views.copy_example_js_to_user,
        name = 'copy-js'),
    path('wizard/normal-room/',
        views.WizardNormalRoomCreate.as_view(),
        name = 'wizard-normal-room'),

    # path('<int:place_pk>/device/',
    #     include ('Devices.urls')),

    ]
