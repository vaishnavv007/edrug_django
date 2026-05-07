from django.contrib import admin
from .models import (
    DrugInformation, RehabilitationCenter, SupportGroup, GroupMembership,
    EducationalResource, NewsArticle, Post, Comment, Like, Report,
    Assessment, RehabilitationGoal, Message, AssessmentTemplate, Question, UserAssessment,
    CommunityGroup, CommunityGroupMembership, ResearchPaper, GroupMessage
)
from .forms import PostForm


@admin.register(DrugInformation)
class DrugInformationAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_at', 'updated_at']
    search_fields = ['name', 'category']
    list_filter = ['category', 'created_at']


@admin.register(RehabilitationCenter)
class RehabilitationCenterAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'verified', 'created_at']
    search_fields = ['name', 'address']
    list_filter = ['verified', 'created_at']


class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 0


@admin.register(SupportGroup)
class SupportGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_online', 'created_by', 'created_at']
    search_fields = ['name', 'location']
    list_filter = ['is_online', 'created_at']
    inlines = [GroupMembershipInline]


@admin.register(EducationalResource)
class EducationalResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'resource_type', 'verified', 'created_at']
    search_fields = ['title', 'author__username']
    list_filter = ['resource_type', 'verified', 'created_at']


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'source', 'is_fake_news', 'confidence_score', 'created_at']
    search_fields = ['title', 'source']
    list_filter = ['is_fake_news', 'created_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'is_fake', 'trust_score', 'verified_content', 'created_at']
    search_fields = ['title', 'user__username', 'content']
    list_filter = ['is_fake', 'verified_content', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    form = PostForm


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    search_fields = ['user__username', 'content']
    list_filter = ['created_at']
    readonly_fields = ['created_at']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    search_fields = ['user__username', 'post__title']
    list_filter = ['created_at']
    readonly_fields = ['created_at']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'reason', 'reviewed', 'created_at']
    search_fields = ['user__username', 'post__title', 'reason']
    list_filter = ['reason', 'reviewed', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'risk_score', 'sentiment', 'created_at']
    search_fields = ['user__username']
    list_filter = ['sentiment', 'created_at']
    readonly_fields = ['created_at']


@admin.register(RehabilitationGoal)
class RehabilitationGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'goal_text', 'progress_percentage', 'completed', 'created_at']
    search_fields = ['user__username', 'goal_text']
    list_filter = ['completed', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'read', 'created_at']
    search_fields = ['sender__username', 'receiver__username', 'content']
    list_filter = ['read', 'created_at']
    readonly_fields = ['created_at']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 3


@admin.register(AssessmentTemplate)
class AssessmentTemplateAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at']
    search_fields = ['title', 'created_by__username']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['assessment', 'text', 'category', 'input_type']
    search_fields = ['text', 'assessment__title']
    list_filter = ['category', 'input_type']


@admin.register(UserAssessment)
class UserAssessmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_id', 'assessment', 'severity_level', 'readiness_level', 'created_at']
    search_fields = ['user__username', 'session_id', 'assessment__title']
    list_filter = ['severity_level', 'readiness_level', 'created_at']
    readonly_fields = ['created_at', 'ai_report', 'mental_state_summary']


class CommunityGroupMembershipInline(admin.TabularInline):
    model = CommunityGroupMembership
    extra = 0


@admin.register(CommunityGroup)
class CommunityGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'member_count', 'is_active', 'created_at']
    search_fields = ['name', 'created_by__username']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CommunityGroupMembershipInline]


@admin.register(CommunityGroupMembership)
class CommunityGroupMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'is_admin', 'joined_at']
    search_fields = ['user__username', 'group__name']
    list_filter = ['is_admin', 'joined_at']
    readonly_fields = ['joined_at']


@admin.register(ResearchPaper)
class ResearchPaperAdmin(admin.ModelAdmin):
    list_display = ['title', 'authors', 'published_by', 'journal', 'is_verified', 'created_at']
    search_fields = ['title', 'authors', 'published_by__username', 'journal']
    list_filter = ['is_verified', 'created_at', 'publication_date']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'authors', 'published_by', 'abstract')
        }),
        ('Publication Details', {
            'fields': ('journal', 'publication_date', 'doi', 'keywords')
        }),
        ('Content', {
            'fields': ('content', 'pdf_file')
        }),
        ('Status', {
            'fields': ('is_verified',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'group', 'content_preview', 'is_pinned', 'created_at']
    search_fields = ['sender__username', 'group__name', 'content']
    list_filter = ['is_pinned', 'created_at', 'group']
    readonly_fields = ['created_at', 'updated_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    fieldsets = (
        ('Message Information', {
            'fields': ('group', 'sender', 'content')
        }),
        ('Options', {
            'fields': ('is_pinned', 'reply_to')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
