from django.urls import path,include
from django.conf.urls import url
from . import views
from django.conf import settings
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('api',views.MemberViewset)

urlpatterns = [
    path('router/', include(router.urls)),
    path('signup/', views.signup, name='signup'),
    path('test/', views.test, name='test'),
    path('signin/', views.signin, name='signin'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('uploaddocument/', views.uploaddocument, name='uploaddocument'),
    path('filedescription/<str:id>', views.filedescription, name='filedescription'),
    path('publicfiledescription/<str:id>', views.publicfiledescription, name='publicfiledescription'),
    path('newfile/', views.uploadfile, name='newfile'),
    path('changetype/<str:id>', views.changetype, name='changetype'),
    path('delete/<str:id>', views.deletefile, name='delete'),
    path('download/<str:id>', views.download, name='download'),
    path('memberz/', views.member_list),
    path('memberupdate/<int:id>/', views.mygeneric.as_view()),
    path('memberdetail/<int:pk>', views.member_detail),
]