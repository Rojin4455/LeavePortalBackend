from rest_framework.serializers import Serializer, ModelSerializer
from users.models import LeaveType, LeaveRequest, LeaveBalance, User
from django.utils import timezone
from rest_framework import serializers
from users.serializers import UserSerializer


class LeaveTypeSerializer(ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ["id","name","description","default_days"]

    def create(self, validated_data):
        leave_type = super().create(validated_data)

        users = User.objects.all()
        current_year = timezone.now().year

        leave_balances = [
            LeaveBalance(user=user, leave_type=leave_type, year=current_year)
            for user in users
        ]
        LeaveBalance.objects.bulk_create(leave_balances)

        return leave_type

class UserLeaveBalanceSerializer(ModelSerializer):
    leave_type = LeaveTypeSerializer()
    class Meta:
        model = LeaveBalance
        fields = ['id', 'leave_type','year','used_days','remaining_days']



class LeaveRequestDetailSerializer(ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = "__all__"


class CombinedLeaveDetailsSerializer(ModelSerializer):
    # leave_requests = serializers.SerializerMethodField()
    leave_balance = serializers.SerializerMethodField()

    class Meta:
        model = LeaveType
        fields = "__all__"

    # def get_leave_requests(self, obj):
    #     user = self.context.get('user')
    #     requests = LeaveRequest.objects.filter(
    #         employee=user,
    #         leave_type=obj
    #     ).order_by('-created_at')
    #     return LeaveRequestDetailSerializer(requests, many=True).data
    
    def get_leave_balance(self, obj):
            user = self.context.get('user')
            current_year = timezone.now().year
            try:
                balance = LeaveBalance.objects.get(
                    user=user,
                    leave_type=obj,
                    year=current_year
                )
                return UserLeaveBalanceSerializer(balance).data
            except LeaveBalance.DoesNotExist:
                return None

class LeaveRequestSerializer(ModelSerializer):

    class Meta:
        model = LeaveRequest
        fields = ['employee', 'leave_type', 'start_date', 'end_date', 'num_days', 'reason']
        extra_kwargs = {
            'employee': {'required': True},
            'leave_type': {'required': True},
            'start_date': {'required': True},
            'end_date': {'required': True},
            'num_days': {'required': True},
            'reason': {'required': True},
        }

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date must be before or equal to the end date.")
        return data
    

class LeaveRequestDetailsSerializer(ModelSerializer):
    employee = UserSerializer()
    class Meta:
        model = LeaveRequest
        fields = '__all__'





class LeaveHistorySerializer(serializers.ModelSerializer):
    period = serializers.SerializerMethodField()
    days = serializers.DecimalField(source='num_days', max_digits=5, decimal_places=1)
    
    class Meta:
        model = LeaveRequest
        fields = ['period', 'days', 'reason']
        
    def get_period(self, obj):
        return obj.start_date.strftime('%b %Y')

class LeaveRequestDetailSerializer(serializers.ModelSerializer):
    leave_history = serializers.SerializerMethodField()
    total_leaves_this_year = serializers.SerializerMethodField()
    remaining_leaves = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'start_date', 'end_date', 'reason', 'status',
            'leave_history', 'total_leaves_this_year', 'remaining_leaves'
        ]

    def get_leave_history(self, obj):
        previous_leaves = LeaveRequest.objects.filter(
            employee=obj.employee,
            start_date__year=obj.start_date.year
        ).exclude(id=obj.id).order_by('-start_date')
        return LeaveHistorySerializer(previous_leaves, many=True).data

    def get_total_leaves_this_year(self, obj):
        return LeaveRequest.objects.filter(
            employee=obj.employee,
            start_date__year=obj.start_date.year,
            status='APPROVED'
        ).count()

    def get_remaining_leaves(self, obj):
        try:
            balance = LeaveBalance.objects.get(
                user=obj.employee,
                leave_type=obj.leave_type,
                year=obj.start_date.year
            )
            return balance.remaining_days
        except LeaveBalance.DoesNotExist:
            return 0

