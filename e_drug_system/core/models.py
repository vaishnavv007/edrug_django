from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class DrugInformation(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    effects = models.TextField()
    risks = models.TextField()
    health_issues = models.TextField(help_text="Health issues caused by this drug", blank=True, null=True)
    withdrawal_symptoms = models.TextField(help_text="Withdrawal symptoms when stopping use", blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_drugs', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class RehabilitationCenter(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    description = models.TextField()
    services_offered = models.TextField()
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    user_ratings = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, help_text="Average user rating (0-5)")
    comments = models.TextField(blank=True, null=True, help_text="User comments about the center")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_centers', null=True, blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SupportGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    meeting_schedule = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    contact_info = models.TextField()
    is_online = models.BooleanField(default=False)
    meeting_link = models.URLField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(User, through='GroupMembership', related_name='support_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class GroupMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(SupportGroup, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_moderator = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'group']


class EducationalResource(models.Model):
    RESOURCE_TYPES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('infographic', 'Infographic'),
        ('guide', 'Guide'),
    ]

    title = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    content = models.TextField()
    url = models.URLField(blank=True)
    thumbnail = models.ImageField(upload_to='resources/thumbnails/', blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class NewsArticle(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    source = models.CharField(max_length=255)
    url = models.URLField()
    is_fake_news = models.BooleanField(default=False)
    confidence_score = models.FloatField(null=True, blank=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_fake = models.BooleanField(default=False)
    potentially_fake = models.BooleanField(default=False)
    trust_score = models.FloatField(default=0.0)
    verified_content = models.BooleanField(default=False)
    fake_confidence = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} on {self.post.title}"


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['post', 'user']

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"


class Report(models.Model):
    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
        ('fake_news', 'Fake News'),
        ('harassment', 'Harassment'),
        ('other', 'Other'),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['post', 'user']

    def __str__(self):
        return f"{self.user.username} reported {self.post.title} - {self.reason}"


class Assessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assessments')
    answers = models.JSONField()
    risk_score = models.FloatField()
    sentiment = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous"
        return f"Assessment by {user_str} - Risk: {self.risk_score}"


class RehabilitationGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rehab_goals')
    goal_text = models.TextField()
    progress_percentage = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.goal_text[:30]}... ({self.progress_percentage}%)"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}"


# Dynamic Assessment System Models
class AssessmentTemplate(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assessments')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Question(models.Model):
    CATEGORY_CHOICES = [
        ('severity', 'Addiction Severity'),
        ('readiness', 'Readiness to Change'),
        ('mental_state', 'Mental & Physical State'),
    ]

    INPUT_TYPE_CHOICES = [
        ('scale', 'Scale (1-5)'),
        ('text', 'Text'),
        ('choice', 'Choice'),
    ]

    assessment = models.ForeignKey(AssessmentTemplate, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    input_type = models.CharField(max_length=10, choices=INPUT_TYPE_CHOICES)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.assessment.title} - {self.text[:50]}"


class UserAssessment(models.Model):
    SEVERITY_CHOICES = [
        ('Low', 'Low'),
        ('Moderate', 'Moderate'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]

    READINESS_CHOICES = [
        ('Not Ready', 'Not Ready'),
        ('Thinking', 'Thinking About Change'),
        ('Preparing', 'Preparing'),
        ('Recovering', 'Actively Recovering'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_assessments', null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    assessment = models.ForeignKey(AssessmentTemplate, on_delete=models.CASCADE, related_name='user_assessments')
    responses = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    ai_report = models.TextField(blank=True)
    severity_level = models.CharField(max_length=20, choices=SEVERITY_CHOICES, null=True, blank=True)
    readiness_level = models.CharField(max_length=30, choices=READINESS_CHOICES, null=True, blank=True)
    mental_state_summary = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.assessment.title}"
        return f"Anonymous ({self.session_id}) - {self.assessment.title}"


class RehabilitationPlan(models.Model):
    PRIMARY_GOAL_CHOICES = [
        ('quit', 'Quit'),
        ('reduce', 'Reduce'),
        ('control', 'Control'),
    ]

    ACTIVITY_CHOICES = [
        ('exercise', 'Exercise'),
        ('meditation', 'Meditation'),
        ('counseling', 'Counseling'),
        ('support_groups', 'Support Groups'),
        ('journaling', 'Journaling'),
    ]

    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rehabilitation_plans')
    primary_goal = models.CharField(max_length=20, choices=PRIMARY_GOAL_CHOICES)
    short_term_goal = models.TextField(help_text="Goal to achieve in 7 days")
    long_term_goal = models.TextField(help_text="Goal to achieve in 30-60 days")
    hours_per_day = models.IntegerField(help_text="Hours per day dedicated to recovery activities")
    activities = models.JSONField(default=list, help_text="List of activities user is willing to do")
    activity_frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    risk_situations = models.TextField(help_text="Situations that make user want to use again", blank=True)
    risk_level = models.IntegerField(default=0, help_text="Risk level 0-100%")
    ai_analysis = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_primary_goal_display()} Plan"


class DailyProgress(models.Model):
    CRAVING_INTENSITY_CHOICES = [
        ('none', 'None'),
        ('mild', 'Mild'),
        ('strong', 'Strong'),
    ]

    RISK_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    rehabilitation_plan = models.ForeignKey(RehabilitationPlan, on_delete=models.CASCADE, related_name='daily_progress')
    date = models.DateField(auto_now_add=True)
    completed_activities = models.BooleanField(default=False)
    mood_rating = models.IntegerField(help_text="Mood rating 1-5")
    craving_intensity = models.CharField(max_length=20, choices=CRAVING_INTENSITY_CHOICES, default='none')
    relapsed = models.BooleanField(default=False)
    triggers = models.TextField(blank=True, help_text="What triggered cravings if any")
    confidence_rating = models.IntegerField(help_text="Confidence rating 1-5")
    cravings_handling = models.TextField(blank=True, help_text="How did you handle cravings today")
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, default='low')
    ai_analysis = models.TextField(blank=True)
    self_harm_detected = models.BooleanField(default=False)
    self_harm_alert_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['rehabilitation_plan', 'date']

    def __str__(self):
        return f"{self.rehabilitation_plan.user.username} - {self.date}"


class CommunityGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_community_groups')
    members = models.ManyToManyField(User, through='CommunityGroupMembership', related_name='joined_community_groups', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.members.count()


class CommunityGroupMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(CommunityGroup, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'group']

    def __str__(self):
        return f"{self.user.username} - {self.group.name}"


class ResearchPaper(models.Model):
    title = models.CharField(max_length=500)
    abstract = models.TextField()
    content = models.TextField()
    authors = models.CharField(max_length=500, help_text="Comma-separated list of authors")
    published_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='published_papers')
    publication_date = models.DateField(null=True, blank=True)
    journal = models.CharField(max_length=255, blank=True)
    doi = models.URLField(blank=True, help_text="Digital Object Identifier")
    keywords = models.CharField(max_length=500, blank=True, help_text="Comma-separated keywords")
    pdf_file = models.FileField(upload_to='research_papers/', blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def author_list(self):
        return [author.strip() for author in self.authors.split(',') if author.strip()]

    @property
    def keyword_list(self):
        return [keyword.strip() for keyword in self.keywords.split(',') if keyword.strip()]


class GroupMessage(models.Model):
    group = models.ForeignKey(CommunityGroup, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_group_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False)
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.username} in {self.group.name}: {self.content[:50]}..."

    @property
    def reply_count(self):
        return self.replies.count()
