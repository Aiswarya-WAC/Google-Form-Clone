from django.contrib import admin
from .models import Questionnaire, Question, Option, Response, Answer

admin.site.register(Questionnaire)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Response)
admin.site.register(Answer)

