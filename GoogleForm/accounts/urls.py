# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    #path('protected/', views.ProtectedAPIView.as_view(), name='protected'),
    
    # Questionnaire URLs
    path('create/', views.CreateQuestionnaireView.as_view(), name='create_questionnaire'),
    path('save/', views.SaveQuestionnaireAPIView.as_view(), name='save_questionnaire'),
    path('list/', views.ListQuestionnairesView.as_view(), name='list_questionnaires'),
    path('fill/<int:pk>/', views.FillQuestionnaireView.as_view(), name='fill_questionnaire'),
    path('submit/', views.SubmitResponseAPIView.as_view(), name='submit_response'),
    path('delete/<int:pk>/', views.DeleteQuestionnaireAPIView.as_view(), name='delete_questionnaire'),
    path('questionnaire/<int:pk>/responses/', views.QuestionnaireResponsesView.as_view(), name='questionnaire_responses'),
    path('edit/<int:pk>/', views.EditQuestionnaireView.as_view(), name='edit_questionnaire')
]
