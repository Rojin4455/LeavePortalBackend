from django.urls import path
from .views import *


urlpatterns = [
    path('user/signup/', EmployeeSignupView.as_view(), name='user-signup'),
    path('user/login/', UserLoginView.as_view(), name='user-login'),
    path('admin/login/', AdminLoginView.as_view(), name='admin-login'),
    path('admin/logout/', AdminLogoutView.as_view(), name='user-login'),
    path('manager/signup/', ManagerSignupView.as_view(), name='manager-signup'),
    path('manager/login/', ManagerLoginView.as_view(), name='manager-login'),
    path('manager/logout/', AdminLogoutView.as_view(), name='manager-login'),
    path('admin/add-department/', DepartmentView.as_view()),
    path('admin/get-departments/', GetDepartmentView.as_view()),
    path('user/get-managers/',ManagerView.as_view()),
    path('manager/get-employees/',ManagerEmployeesView.as_view()),
    path('fetch-all-users/', AllUsersView.as_view()),
    path('manager-info/', ManagerInfoAPIView.as_view())
]   