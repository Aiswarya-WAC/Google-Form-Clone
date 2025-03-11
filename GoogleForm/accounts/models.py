from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Questionnaire(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='questionnaires_users')
    is_public = models.BooleanField(default=True)  # Added field for public/private visibility

    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = (
        ('short_answer', 'Short Answer'),
        ('paragraph', 'Paragraph'),
        ('multiple_choice', 'Multiple Choice'),
        ('checkboxes', 'Checkboxes'),
        ('dropdown', 'Dropdown'),
        ('linear_scale', 'Linear Scale'),
    )
    questionnaire = models.ForeignKey(Questionnaire, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)

    def __str__(self):
        return self.text

class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

class Response(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, related_name='responses', on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

class Answer(models.Model):
    response = models.ForeignKey(Response, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    selected_options = models.ManyToManyField(Option, blank=True)

    def __str__(self):
        return f"Answer to {self.question.text}"