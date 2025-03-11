from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, DetailView, ListView, View
from django.http import HttpResponseRedirect
from django.contrib import messages
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import UserProfile, Questionnaire, Question, Option, Response as ResponseModel, Answer
from .serializers import RegisterSerializer, QuestionnaireSerializer, ResponseSerializer
from django.views.decorators.csrf import csrf_protect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile, Questionnaire

class RegisterView(APIView):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            UserProfile.objects.create(user=user)
            return redirect('login')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def get(self, request):
        next_url = request.GET.get('next', '')
        return render(request, 'login.html', {'next': next_url})

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        next_url = request.POST.get('next', '')

        if user:
            login(request, user)
            if next_url:
                return redirect(next_url)
            return redirect(reverse('home'))

        return render(request, 'login.html', {'error': 'Invalid credentials', 'next': next_url})


@method_decorator(login_required, name='dispatch')
class HomeView(APIView):
    def get(self, request):
        return render(request, 'home.html', {'username': request.user.username})


@method_decorator(login_required, name='dispatch')
class CreateQuestionnaireView(TemplateView):
    template_name = 'create_questionnaire.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.user.username
        return context


class FillQuestionnaireView(DetailView):
    model = Questionnaire
    template_name = 'fill_questionnaire.html'
    context_object_name = 'questionnaire'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.is_public and not request.user.is_authenticated:
            next_url = request.path
            messages.info(request, 'Please login to fill this form')
            login_url = f"{reverse('login')}?next={next_url}"
            return redirect(login_url)
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class SaveQuestionnaireAPIView(APIView):
    def post(self, request):
        data = request.data.copy()
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        data['user'] = user_profile.id
        serializer = QuestionnaireSerializer(data=data)

        if serializer.is_valid():
            questionnaire = serializer.save()
            return Response({
                'id': questionnaire.id,
                'message': 'Questionnaire created successfully',
                'redirect_url': reverse('list_questionnaires')
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubmitResponseAPIView(APIView):
    def post(self, request):
        serializer = ResponseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Response submitted successfully'},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'error': 'Invalid data', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


@method_decorator(login_required, name='dispatch')
class ListQuestionnairesView(ListView):
    model = Questionnaire
    template_name = 'list_questionnaires.html'
    context_object_name = 'questionnaires'

    def get_queryset(self):
        user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return Questionnaire.objects.filter(user=user_profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.user.username
        return context
    


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class DeleteQuestionnaireAPIView(APIView):
    def delete(self, request, pk):
        try:
            print(f"User: {request.user}")
            print(f"Questionnaire ID to delete: {pk}")
            user_profile = UserProfile.objects.get(user=request.user)
            print(f"User Profile: {user_profile}")
            questionnaire = Questionnaire.objects.get(id=pk, user=user_profile)
            print(f"Questionnaire to delete: {questionnaire}")
            questionnaire.delete()
            print("Questionnaire deleted successfully")
            return Response(
                {'message': 'Questionnaire deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except UserProfile.DoesNotExist:
            print("User profile not found")
            return Response(
                {'error': 'User profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Questionnaire.DoesNotExist:
            print("Questionnaire not found or not authorized to delete")
            return Response(
                {'error': 'Questionnaire not found or not authorized to delete'},
                status=status.HTTP_404_NOT_FOUND
            )

class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('login'))
    
@method_decorator(login_required, name='dispatch')
class QuestionnaireResponsesView(DetailView):
    model = Questionnaire
    template_name = 'questionnaire_responses.html'
    context_object_name = 'questionnaire'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        questionnaire = self.object
        responses = ResponseModel.objects.filter(questionnaire=questionnaire)
        response_data = []

        for response in responses:
            respondent = "Anonymous" if questionnaire.is_public and not self.request.user.is_authenticated else self.request.user.username
            answers = Answer.objects.filter(response=response).order_by('question__id')  # Order by question ID
            response_data.append({
                'respondent': respondent,
                'submitted_at': response.submitted_at,
                'answers': answers
            })

        context['responses'] = response_data
        context['username'] = self.request.user.username
        return context
    
    