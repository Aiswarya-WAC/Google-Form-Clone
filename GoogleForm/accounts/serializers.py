from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Questionnaire, Question, Option, Response, Answer

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text']

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'options']

class QuestionnaireSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Questionnaire
        fields = ['id', 'title', 'created_at', 'questions', 'user', 'is_public']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        questionnaire = Questionnaire.objects.create(**validated_data)
        for question_data in questions_data:
            options_data = question_data.pop('options', [])
            question = Question.objects.create(questionnaire=questionnaire, **question_data)
            for option_data in options_data:
                Option.objects.create(question=question, **option_data)
        return questionnaire
    
class AnswerSerializer(serializers.ModelSerializer):
    selected_options = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Option.objects.all(), required=False
    )

    class Meta:
        model = Answer
        fields = ['question', 'text', 'selected_options']

    def validate(self, data):
        question = data.get('question')
        question_type = question.question_type
        text = data.get('text')
        selected_options = data.get('selected_options', [])

        # For linear_scale, ensure text is provided and selected_options is empty
        if question_type == 'linear_scale':
            if not text:
                raise serializers.ValidationError("Linear scale requires a text value.")
            if selected_options:
                raise serializers.ValidationError("Linear scale should not have selected options.")
        return data

    def create(self, validated_data):
        selected_options = validated_data.pop('selected_options', [])
        answer = Answer.objects.create(**validated_data)
        answer.selected_options.set(selected_options)
        return answer

class ResponseSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Response
        fields = ['id', 'questionnaire', 'submitted_at', 'answers']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        response = Response.objects.create(**validated_data)

        for answer_data in answers_data:
            selected_options = answer_data.pop('selected_options', [])
            answer = Answer.objects.create(response=response, **answer_data)
            answer.selected_options.set(selected_options)

        return response