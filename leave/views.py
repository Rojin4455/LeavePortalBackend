from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from users.models import LeaveType, LeaveBalance, LeaveRequest
from .serializers import LeaveTypeSerializer, UserLeaveBalanceSerializer, LeaveRequestSerializer, CombinedLeaveDetailsSerializer, LeaveRequestDetailsSerializer
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from django.contrib.auth import get_user_model


User = get_user_model()


class LeaveView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        leavetypes = LeaveType.objects.all()
        serializer = LeaveTypeSerializer(leavetypes, many=True)

        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        serializer = LeaveTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserLeaveBalanceView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        leave_balance = LeaveBalance.objects.filter(user=user)
        serializer = UserLeaveBalanceSerializer(leave_balance, many=True)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class UserRequestLeaveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        print("request user: ", request.user.id)
        data['employee'] = request.user.id
        print("data: ", data)
        serializer = LeaveRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Leave request created successfully.", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

class ConbinedLeaveDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        leave_types = LeaveType.objects.all()
        serializer = CombinedLeaveDetailsSerializer(
            leave_types,
            many=True, 
            context={'user': request.user}
        )
        requests = LeaveRequest.objects.filter(employee=request.user)
        leave_request_data = LeaveRequestDetailsSerializer(requests, many=True)
        if serializer:
            return Response({"leaveRequests":leave_request_data.data,"leaveDetails":serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        





class ManagerLeaveRequestView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        employees = User.objects.filter(
                manager=request.user
            ).select_related('department')
        
        leave_requests = LeaveRequest.objects.filter(employee__in=employees)
        
        

        
        serializer = LeaveRequestDetailsSerializer(leave_requests, many=True)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request):
        data = request.data
        leave_request_id = data.get('id')
        action = data.get('action')

        if not leave_request_id or not action:
            return Response(
                {"error": "Leave request ID and action are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            leave_request = LeaveRequest.objects.get(id=leave_request_id)

            if leave_request.employee.manager != request.user:
                return Response(
                    {"error": "You are not authorized to update this leave request."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if action not in ['APPROVED', 'REJECTED']:
                return Response(
                    {"error": "Invalid action. Valid actions are 'approved' or 'rejected'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            print("actions: ", action)
            leave_balance = LeaveBalance.objects.get(user = leave_request.employee, leave_type=leave_request.leave_type)
            leave_balance.used_days += leave_request.num_days
            leave_balance.save()
            leave_request.status = action
            leave_request.save()

            serializer = LeaveRequestDetailsSerializer(leave_request)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except LeaveRequest.DoesNotExist:
            return Response(
                {"error": "Leave request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        

