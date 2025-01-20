from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import LoginSerializer, UserSerializer, ManagerSignupSerializer, EmployeeSignupSerializer, DepartmentSerializer, ManagerSerializer
from .models import Department
from django.contrib.auth import get_user_model


User = get_user_model()

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(username=username, password=password)
            
            if user is not None and not user.user_type == 'Employee':
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'status': 'success',
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    }
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'error',
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'status': 'error',
            'message': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

class AdminLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")

            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Something went wrong during logout"}, status=status.HTTP_400_BAD_REQUEST)
    

class AdminLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        print("reached herererere")
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(username=username, password=password)
            print("user: ",user)
            if user is not None and user.is_superuser:
                
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'status': 'success',
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    }
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'error',
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'status': 'error',
            'message': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

class ManagerLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            
            if user is not None and user.user_type == 'MANAGER':
                
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'status': 'success',
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    }
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'error',
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'status': 'error',
            'message': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    



class BaseSignupView(APIView):
    permission_classes = [AllowAny]
    serializer_class = None
    
    def post(self, request):
        print("request data: ",request.data)
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            try:
                # Create the user
                user = serializer.save()
                
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'status': 'success',
                    'message': 'User created successfully',
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    }
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'status': 'error',
                    'message': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'status': 'error',
            'message': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ManagerSignupView(BaseSignupView):

    serializer_class = ManagerSignupSerializer

class EmployeeSignupView(BaseSignupView):
    
    serializer_class = EmployeeSignupSerializer



class DepartmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetDepartmentView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)

        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ManagerView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        managers = User.objects.filter(user_type="MANAGER")

        serializer = ManagerSerializer(managers, many=True)

        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class ManagerEmployeesView(APIView):
    permission_classes = [IsAuthenticated]
    

    def get(self, request):

        try:
            user_id = request.user.id
            manager = User.objects.get(id=user_id)
            employees = User.objects.filter(manager=manager)

            serializer = UserSerializer(employees, many=True)
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    



class AllUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.filter(is_superuser = False)
        serializer = UserSerializer(users, many=True)
        if serializer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_200_OK)
    


class ManagerInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.manager:
            return Response({"message": "No manager assigned to this user."}, status=404)
        
        manager = user.manager
        serializer = UserSerializer(manager)
        department = Department.objects.get(id = serializer.data['department'])
        
        data = serializer.data
        data['department_name'] = department.name
        return Response(data, status=200)