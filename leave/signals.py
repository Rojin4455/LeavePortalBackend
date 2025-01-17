from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal
from users.models import LeaveBalance, LeaveType
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def create_leave_balance(sender, instance, created, **kwargs):
    if created and instance.user_type == 'EMPLOYEE':
        current_year = timezone.now().year
        leave_types = LeaveType.objects.all()
        
        leave_balances = []
        for leave_type in leave_types:
            leave_balances.append(
                LeaveBalance(
                    user=instance,
                    leave_type=leave_type,
                    year=current_year,
                )
            )
        
        LeaveBalance.objects.bulk_create(leave_balances)