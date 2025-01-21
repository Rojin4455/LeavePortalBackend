from django.urls import path
from .views import *

urlpatterns = [
    path('admin/get-leavetypes/', LeaveView.as_view()),
    path('admin/add-leavetype/', LeaveView.as_view()),
    path('get-user-leavebalance/',UserLeaveBalanceView.as_view()),
    path('user/request-leave/', UserRequestLeaveView.as_view()),
    path('combined-leave-details/', ConbinedLeaveDetails.as_view(),),
    path('manager/leave-requests/', ManagerLeaveRequestView.as_view()),
    path('change-request-status/', ManagerLeaveRequestView.as_view()),
    # path('leave-date-ranges/', LeaveRange.as_view()),
]