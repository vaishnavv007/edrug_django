from django import forms
from .models import Post, Comment, Report, Message, AssessmentTemplate, Question, RehabilitationPlan, DailyProgress, DrugInformation, RehabilitationCenter
from django.contrib.auth import get_user_model

User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter post title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write your post content here...'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add a comment...'}),
        }


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Provide additional details (optional)...'}),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['receiver', 'content']
        widgets = {
            'receiver': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your message here...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['receiver'].queryset = User.objects.all()


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'category', 'input_type']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter the question text...'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'input_type': forms.Select(attrs={'class': 'form-control'}),
        }


class AssessmentTemplateForm(forms.ModelForm):
    class Meta:
        model = AssessmentTemplate
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter assessment title...'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter assessment description...'}),
        }


class RehabilitationPlanForm(forms.ModelForm):
    activities = forms.MultipleChoiceField(
        choices=RehabilitationPlan.ACTIVITY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    class Meta:
        model = RehabilitationPlan
        fields = ['primary_goal', 'short_term_goal', 'long_term_goal', 'hours_per_day', 'activities', 'activity_frequency', 'risk_situations']
        widgets = {
            'primary_goal': forms.Select(attrs={'class': 'form-control'}),
            'short_term_goal': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Goal to achieve in 7 days...'}),
            'long_term_goal': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Goal to achieve in 30-60 days...'}),
            'hours_per_day': forms.NumberInput(attrs={'min': 1, 'max': 24, 'placeholder': '1-24'}),
            'activity_frequency': forms.Select(attrs={'class': 'form-control'}),
            'risk_situations': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Situations that make you want to use again...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['short_term_goal'].required = True
        self.fields['long_term_goal'].required = True
        self.fields['hours_per_day'].required = True
        self.fields['risk_situations'].required = False


class DailyProgressForm(forms.ModelForm):
    class Meta:
        model = DailyProgress
        fields = ['completed_activities', 'mood_rating', 'craving_intensity', 'relapsed', 'triggers', 'confidence_rating', 'cravings_handling', 'risk_level']
        widgets = {
            'completed_activities': forms.CheckboxInput,
            'mood_rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'craving_intensity': forms.Select(attrs={'class': 'form-control'}),
            'relapsed': forms.CheckboxInput,
            'triggers': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What triggered cravings if any...'}),
            'confidence_rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'cravings_handling': forms.Textarea(attrs={'rows': 3, 'placeholder': 'How did you handle cravings today...'}),
            'risk_level': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mood_rating'].required = True
        self.fields['confidence_rating'].required = True
        self.fields['triggers'].required = False
        self.fields['cravings_handling'].required = False


class DrugInformationForm(forms.ModelForm):
    class Meta:
        model = DrugInformation
        fields = ['name', 'description', 'category', 'effects', 'risks', 'health_issues', 'withdrawal_symptoms']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter drug name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter drug description'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter drug category'}),
            'effects': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter effects of the drug'}),
            'risks': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter risks associated with the drug'}),
            'health_issues': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter health issues caused by this drug'}),
            'withdrawal_symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter withdrawal symptoms when stopping use'}),
        }


class RehabilitationCenterForm(forms.ModelForm):
    class Meta:
        model = RehabilitationCenter
        fields = ['name', 'address', 'phone', 'email', 'website', 'description', 'services_offered', 'location_lat', 'location_lng']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter center name'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter full address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter website URL (optional)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter center description'}),
            'services_offered': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter services offered'}),
            'location_lat': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Latitude (optional)'}),
            'location_lng': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Longitude (optional)'}),
        }
