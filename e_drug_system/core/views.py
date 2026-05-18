from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import models
import json
import uuid
from .models import (
    DrugInformation, RehabilitationCenter, SupportGroup, EducationalResource,
    Post, Comment, Like, Assessment, Report, Message, RehabilitationGoal,
    AssessmentTemplate, Question, UserAssessment, RehabilitationPlan, DailyProgress,
    CommunityGroup, CommunityGroupMembership, ResearchPaper, GroupMessage
)
from .forms import PostForm, CommentForm, ReportForm, MessageForm, AssessmentTemplateForm, QuestionForm, RehabilitationPlanForm, DailyProgressForm, DrugInformationForm, RehabilitationCenterForm
from users.forms import AdminUserCreationForm
from users.permissions import moderator_required, expert_required, moderator_or_expert_required
from .services import analyze_assessment_with_groq, analyze_rehabilitation_plan, analyze_daily_progress
from ai_services.services import FakeNewsDetector

User = get_user_model()

# Initialize fake news detector
fake_news_detector = FakeNewsDetector()


def home(request):
    return render(request, 'core/home.html')


class DrugListView(ListView):
    model = DrugInformation
    template_name = 'core/drug_list.html'
    context_object_name = 'drugs'
    paginate_by = 12


class DrugDetailView(DetailView):
    model = DrugInformation
    template_name = 'core/drug_detail.html'
    context_object_name = 'drug'


@login_required
def create_drug_information(request):
    """Create drug information - admin and expert only."""
    if not (request.user.is_admin or request.user.is_expert):
        raise PermissionDenied("Only admins and experts can create drug information.")
    
    if request.method == 'POST':
        form = DrugInformationForm(request.POST)
        if form.is_valid():
            drug = form.save(commit=False)
            drug.created_by = request.user
            drug.save()
            messages.success(request, f'Drug information "{drug.name}" has been created successfully.')
            return redirect('drug_detail', pk=drug.pk)
    else:
        form = DrugInformationForm()
    
    context = {
        'form': form,
        'action': 'Create Drug Information',
    }
    return render(request, 'core/drug_form.html', context)


@login_required
def edit_drug_information(request, pk):
    """Edit drug information - admin can edit all, expert can only edit their own."""
    drug = get_object_or_404(DrugInformation, pk=pk)
    
    # Permission check
    if request.user.is_admin:
        pass  # Admin can edit all
    elif request.user.is_expert and drug.created_by == request.user:
        pass  # Expert can edit their own
    else:
        raise PermissionDenied("You don't have permission to edit this drug information.")
    
    if request.method == 'POST':
        form = DrugInformationForm(request.POST, instance=drug)
        if form.is_valid():
            form.save()
            messages.success(request, f'Drug information "{drug.name}" has been updated successfully.')
            return redirect('drug_detail', pk=drug.pk)
    else:
        form = DrugInformationForm(instance=drug)
    
    context = {
        'form': form,
        'action': 'Edit Drug Information',
        'drug': drug,
    }
    return render(request, 'core/drug_form.html', context)


@login_required
def delete_drug_information(request, pk):
    """Delete drug information - admin can delete all, expert can only delete their own."""
    drug = get_object_or_404(DrugInformation, pk=pk)
    
    # Permission check
    if request.user.is_admin:
        pass  # Admin can delete all
    elif request.user.is_expert and drug.created_by == request.user:
        pass  # Expert can delete their own
    else:
        raise PermissionDenied("You don't have permission to delete this drug information.")
    
    if request.method == 'POST':
        drug_name = drug.name
        drug.delete()
        messages.success(request, f'Drug information "{drug_name}" has been deleted successfully.')
        return redirect('drug_list')
    
    context = {
        'drug': drug,
    }
    return render(request, 'core/drug_confirm_delete.html', context)


class RehabilitationCenterListView(ListView):
    model = RehabilitationCenter
    template_name = 'core/rehab_centers.html'
    context_object_name = 'centers'
    paginate_by = 12


class RehabilitationCenterDetailView(DetailView):
    model = RehabilitationCenter
    template_name = 'core/rehab_center_detail.html'
    context_object_name = 'center'


@login_required
def create_rehabilitation_center(request):
    """Create rehabilitation center - admin and expert only."""
    if not (request.user.is_admin or request.user.is_expert):
        raise PermissionDenied("Only admins and experts can create rehabilitation centers.")
    
    if request.method == 'POST':
        form = RehabilitationCenterForm(request.POST)
        if form.is_valid():
            center = form.save(commit=False)
            center.created_by = request.user
            center.save()
            messages.success(request, f'Rehabilitation center "{center.name}" has been created successfully.')
            return redirect('rehab_center_detail', pk=center.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RehabilitationCenterForm()
    
    context = {
        'form': form,
        'action': 'Create Rehabilitation Center',
    }
    return render(request, 'core/rehab_center_form.html', context)


@login_required
def edit_rehabilitation_center(request, pk):
    """Edit rehabilitation center - admin can edit all, expert can only edit their own."""
    center = get_object_or_404(RehabilitationCenter, pk=pk)
    
    # Permission check
    if request.user.is_admin:
        pass  # Admin can edit all
    elif request.user.is_expert and center.created_by == request.user:
        pass  # Expert can edit their own
    else:
        raise PermissionDenied("You don't have permission to edit this rehabilitation center.")
    
    if request.method == 'POST':
        form = RehabilitationCenterForm(request.POST, instance=center)
        if form.is_valid():
            form.save()
            messages.success(request, f'Rehabilitation center "{center.name}" has been updated successfully.')
            return redirect('rehab_center_detail', pk=center.pk)
    else:
        form = RehabilitationCenterForm(instance=center)
    
    context = {
        'form': form,
        'action': 'Edit Rehabilitation Center',
        'center': center,
    }
    return render(request, 'core/rehab_center_form.html', context)


@login_required
def delete_rehabilitation_center(request, pk):
    """Delete rehabilitation center - admin can delete all, expert can only delete their own."""
    center = get_object_or_404(RehabilitationCenter, pk=pk)
    
    # Permission check
    if request.user.is_admin:
        pass  # Admin can delete all
    elif request.user.is_expert and center.created_by == request.user:
        pass  # Expert can delete their own
    else:
        raise PermissionDenied("You don't have permission to delete this rehabilitation center.")
    
    if request.method == 'POST':
        center_name = center.name
        center.delete()
        messages.success(request, f'Rehabilitation center "{center_name}" has been deleted successfully.')
        return redirect('rehab_centers')
    
    context = {
        'center': center,
    }
    return render(request, 'core/rehab_center_confirm_delete.html', context)


class SupportGroupListView(ListView):
    model = SupportGroup
    template_name = 'core/support_groups.html'
    context_object_name = 'groups'
    paginate_by = 12


class SupportGroupDetailView(DetailView):
    model = SupportGroup
    template_name = 'core/support_group_detail.html'
    context_object_name = 'group'


class EducationalResourceListView(ListView):
    model = EducationalResource
    template_name = 'core/resources.html'
    context_object_name = 'resources'
    paginate_by = 12

    def get_queryset(self):
        return EducationalResource.objects.filter(verified=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        groups = CommunityGroup.objects.filter(is_active=True)
        context['groups'] = groups
        context['research_papers'] = ResearchPaper.objects.all()
        
        # Add membership status for each group
        group_membership_status = {}
        if self.request.user.is_authenticated:
            user_memberships = CommunityGroupMembership.objects.filter(
                user=self.request.user,
                group__in=groups
            ).values_list('group_id', flat=True)
            group_membership_status = {str(group_id): True for group_id in user_memberships}
        
        context['group_membership_status'] = group_membership_status
        return context


@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')


@login_required
def admin_create_user(request):
    """View for admins to create users with specific roles (admin, moderator, expert)."""
    if not request.user.is_admin:
        raise PermissionDenied("Only admins can create users with special roles.")
    
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User "{user.username}" has been created with role "{user.get_role_display()}".')
            return redirect('dashboard')
    else:
        form = AdminUserCreationForm()
    
    context = {
        'form': form,
        'action': 'Create User',
    }
    return render(request, 'core/admin_create_user.html', context)


# Admin Assessment CRUD Views
@login_required
def admin_assessment_list(request):
    """View for admins to list all assessment templates."""
    if not request.user.is_admin:
        raise PermissionDenied("Only admins can view assessment templates.")
    
    assessments = AssessmentTemplate.objects.all().select_related('created_by').order_by('-created_at')
    
    context = {
        'assessments': assessments,
    }
    return render(request, 'core/admin_assessment_list.html', context)


@login_required
def admin_create_assessment(request):
    """View for admins to create assessment templates."""
    if not request.user.is_admin:
        raise PermissionDenied("Only admins can create assessment templates.")
    
    if request.method == 'POST':
        form = AssessmentTemplateForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.created_by = request.user
            assessment.save()
            messages.success(request, f'Assessment "{assessment.title}" has been created.')
            return redirect('admin_assessment_list')
    else:
        form = AssessmentTemplateForm()
    
    context = {
        'form': form,
        'action': 'Create Assessment',
    }
    return render(request, 'core/admin_assessment_form.html', context)


@login_required
def admin_edit_assessment(request, assessment_id):
    """View for admins to edit assessment templates."""
    if not request.user.is_admin:
        raise PermissionDenied("Only admins can edit assessment templates.")
    
    assessment = get_object_or_404(AssessmentTemplate, id=assessment_id)
    
    if request.method == 'POST':
        form = AssessmentTemplateForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            messages.success(request, f'Assessment "{assessment.title}" has been updated.')
            return redirect('admin_assessment_list')
    else:
        form = AssessmentTemplateForm(instance=assessment)
    
    context = {
        'form': form,
        'action': 'Edit Assessment',
        'assessment': assessment,
    }
    return render(request, 'core/admin_assessment_form.html', context)


@login_required
def admin_delete_assessment(request, assessment_id):
    """View for admins to delete assessment templates."""
    if not request.user.is_admin:
        raise PermissionDenied("Only admins can delete assessment templates.")
    
    assessment = get_object_or_404(AssessmentTemplate, id=assessment_id)
    
    if request.method == 'POST':
        title = assessment.title
        assessment.delete()
        messages.success(request, f'Assessment "{title}" has been deleted.')
        return redirect('admin_assessment_list')
    
    context = {
        'assessment': assessment,
    }
    return render(request, 'core/admin_assessment_confirm_delete.html', context)


@login_required
def admin_assessment_questions(request, assessment_id):
    """View for admins to manage questions in an assessment template."""
    if not request.user.is_admin:
        raise PermissionDenied("Only admins can manage assessment questions.")
    
    assessment = get_object_or_404(AssessmentTemplate, id=assessment_id)
    questions = assessment.questions.all().order_by('id')
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.assessment = assessment
            question.save()
            messages.success(request, 'Question has been added to the assessment.')
            return redirect('admin_assessment_questions', assessment_id=assessment_id)
    else:
        form = QuestionForm()
    
    context = {
        'assessment': assessment,
        'questions': questions,
        'form': form,
    }
    return render(request, 'core/admin_assessment_questions.html', context)


@login_required
def admin_delete_question(request, question_id):
    """View for admins to delete questions from assessment templates."""
    if not request.user.is_admin:
        raise PermissionDenied("Only admins can delete assessment questions.")
    
    question = get_object_or_404(Question, id=question_id)
    assessment_id = question.assessment.id
    
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question has been deleted.')
        return redirect('admin_assessment_questions', assessment_id=assessment_id)
    
    context = {
        'question': question,
    }
    return render(request, 'core/admin_question_confirm_delete.html', context)


# Rehabilitation Plan Views
@login_required
def create_rehabilitation_plan(request):
    """View for users to create their rehabilitation plan."""
    # Check if user already has an active plan
    existing_plan = RehabilitationPlan.objects.filter(user=request.user, is_active=True).first()
    if existing_plan:
        messages.info(request, 'You already have an active rehabilitation plan. You can view or update it.')
        return redirect('view_rehabilitation_plan', plan_id=existing_plan.id)
    
    if request.method == 'POST':
        form = RehabilitationPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.user = request.user
            plan.activities = form.cleaned_data['activities']
            
            # Analyze plan with AI
            plan_data = {
                'primary_goal': plan.get_primary_goal_display(),
                'short_term_goal': plan.short_term_goal,
                'long_term_goal': plan.long_term_goal,
                'hours_per_day': plan.hours_per_day,
                'activities': plan.activities,
                'activity_frequency': plan.get_activity_frequency_display(),
                'risk_situations': plan.risk_situations
            }
            
            analysis = analyze_rehabilitation_plan(plan_data)
            plan.risk_level = analysis.get('risk_level', 50)
            plan.ai_analysis = analysis.get('ai_analysis', '')
            
            plan.save()
            messages.success(request, 'Your rehabilitation plan has been created successfully!')
            return redirect('view_rehabilitation_plan', plan_id=plan.id)
    else:
        form = RehabilitationPlanForm()
    
    context = {
        'form': form,
    }
    return render(request, 'core/create_rehabilitation_plan.html', context)


@login_required
def view_rehabilitation_plan(request, plan_id):
    """View for users to see their rehabilitation plan and progress."""
    plan = get_object_or_404(RehabilitationPlan, id=plan_id, user=request.user)
    daily_progress = DailyProgress.objects.filter(rehabilitation_plan=plan).order_by('-date')
    
    context = {
        'plan': plan,
        'daily_progress': daily_progress,
    }
    return render(request, 'core/view_rehabilitation_plan.html', context)


@login_required
def submit_daily_progress(request, plan_id):
    """View for users to submit their daily progress."""
    plan = get_object_or_404(RehabilitationPlan, id=plan_id, user=request.user)
    
    # Check if progress already submitted today
    from datetime import date
    today = date.today()
    existing_progress = DailyProgress.objects.filter(rehabilitation_plan=plan, date=today).first()
    
    if existing_progress:
        messages.info(request, 'You have already submitted your progress for today.')
        return redirect('view_rehabilitation_plan', plan_id=plan.id)
    
    if request.method == 'POST':
        form = DailyProgressForm(request.POST)
        if form.is_valid():
            progress = form.save(commit=False)
            progress.rehabilitation_plan = plan
            
            # Analyze progress with AI
            progress_data = {
                'date': str(today),
                'completed_activities': progress.completed_activities,
                'mood_rating': progress.mood_rating,
                'craving_intensity': progress.get_craving_intensity_display(),
                'relapsed': progress.relapsed,
                'triggers': progress.triggers,
                'confidence_rating': progress.confidence_rating,
                'cravings_handling': progress.cravings_handling,
                'risk_level': progress.get_risk_level_display()
            }
            
            plan_data = {
                'primary_goal': plan.get_primary_goal_display(),
                'short_term_goal': plan.short_term_goal,
                'risk_situations': plan.risk_situations
            }
            
            analysis = analyze_daily_progress(progress_data, plan_data)
            progress.ai_analysis = analysis.get('ai_analysis', '')
            progress.self_harm_detected = analysis.get('self_harm_detected', False)
            
            # Update risk level from analysis if different
            if analysis.get('risk_level'):
                progress.risk_level = analysis['risk_level']
            
            progress.save()
            
            # If self-harm detected, alert experts/admins
            if progress.self_harm_detected:
                # Send alert message to experts/admins
                send_self_harm_alert(plan.user, progress)
                messages.warning(request, 'Your response has been flagged. A support team member will contact you shortly.')
            else:
                messages.success(request, 'Your daily progress has been recorded!')
            
            return redirect('view_rehabilitation_plan', plan_id=plan.id)
    else:
        form = DailyProgressForm()
    
    context = {
        'form': form,
        'plan': plan,
    }
    return render(request, 'core/submit_daily_progress.html', context)


def send_self_harm_alert(user, progress):
    """Send alert to experts/admins when self-harm is detected."""
    experts = User.objects.filter(role='expert', is_verified_expert=True)
    admins = User.objects.filter(role='admin')
    
    alert_message = f"SELF-HARM ALERT: User {user.username} has reported concerning responses in their daily progress on {progress.date}. Immediate attention required."
    
    # Send message to all experts and admins
    for recipient in list(experts) + list(admins):
        Message.objects.create(
            sender=user,
            receiver=recipient,
            content=alert_message
        )


# Admin/Expert Monitoring Views
@login_required
def monitor_user_progress(request):
    """View for admins and experts to monitor user progress."""
    if not (request.user.is_admin or request.user.is_expert):
        raise PermissionDenied("Only admins and experts can access this view.")
    
    users_with_plans = User.objects.filter(rehabilitation_plans__is_active=True).distinct()
    recent_progress = DailyProgress.objects.filter(
        self_harm_detected=True
    ).select_related('rehabilitation_plan', 'rehabilitation_plan__user').order_by('-date')[:10]
    
    context = {
        'users_with_plans': users_with_plans,
        'recent_progress': recent_progress,
    }
    return render(request, 'core/monitor_user_progress.html', context)


@login_required
def view_user_progress_detail(request, user_id):
    """View for admins and experts to see detailed progress for a specific user."""
    if not (request.user.is_admin or request.user.is_expert):
        raise PermissionDenied("Only admins and experts can access this view.")
    
    user = get_object_or_404(User, id=user_id)
    plan = RehabilitationPlan.objects.filter(user=user, is_active=True).first()
    
    if not plan:
        messages.info(request, f'{user.username} does not have an active rehabilitation plan.')
        return redirect('monitor_user_progress')
    
    daily_progress = DailyProgress.objects.filter(rehabilitation_plan=plan).order_by('-date')
    flagged_count = daily_progress.filter(self_harm_detected=True).count()
    
    context = {
        'user': user,
        'plan': plan,
        'daily_progress': daily_progress,
        'flagged_count': flagged_count,
    }
    return render(request, 'core/view_user_progress_detail.html', context)


@login_required
def messages_view(request):
    """View messages for registered users - merged conversations by user."""
    # Get all messages involving the current user
    all_messages = Message.objects.filter(
        models.Q(sender=request.user) | models.Q(receiver=request.user)
    ).select_related('sender', 'receiver').order_by('-created_at')
    
    # Group messages by conversation partner
    conversations = {}
    has_unread = False
    
    for message in all_messages:
        # Determine the other user in the conversation
        if message.sender == request.user:
            partner = message.receiver
            partner_is_sender = False
        else:
            partner = message.sender
            partner_is_sender = True
            # Check for unread messages
            if not message.read:
                has_unread = True
        
        # Create or update conversation
        if partner.id not in conversations:
            conversations[partner.id] = {
                'partner': partner,
                'last_message': message,
                'messages': [],
                'unread_count': 0,
                'partner_is_sender': partner_is_sender
            }
        
        # Add message to conversation
        conversations[partner.id]['messages'].append(message)
        
        # Update last message if this is more recent
        if message.created_at > conversations[partner.id]['last_message'].created_at:
            conversations[partner.id]['last_message'] = message
            conversations[partner.id]['partner_is_sender'] = partner_is_sender
        
        # Count unread messages
        if not message.read and message.receiver == request.user:
            conversations[partner.id]['unread_count'] += 1
    
    # Sort conversations by most recent message
    sorted_conversations = sorted(
        conversations.values(),
        key=lambda x: x['last_message'].created_at,
        reverse=True
    )
    
    # Get all users for compose functionality (excluding current user)
    all_users = get_user_model().objects.exclude(id=request.user.id).order_by('username')
    
    # Mark received messages as read
    Message.objects.filter(receiver=request.user, read=False).update(read=True)
    
    context = {
        'conversations': sorted_conversations,
        'all_users': all_users,
        'has_unread_messages': has_unread,
    }
    return render(request, 'core/messages.html', context)


@login_required
@require_http_methods(["GET"])
def get_conversation_messages(request, user_id):
    """API endpoint to get conversation messages with a specific user."""
    try:
        # Get all messages between current user and the specified user
        messages = Message.objects.filter(
            models.Q(
                models.Q(sender=request.user, receiver_id=user_id) |
                models.Q(sender_id=user_id, receiver=request.user)
            )
        ).select_related('sender', 'receiver').order_by('created_at')
        
        # Mark received messages as read
        messages.filter(receiver=request.user, read=False).update(read=True)
        
        # Format messages for JSON response
        message_list = []
        for message in messages:
            message_list.append({
                'id': message.id,
                'content': message.content,
                'sender_id': message.sender.id,
                'sender_username': message.sender.username,
                'receiver_id': message.receiver.id,
                'receiver_username': message.receiver.username,
                'timestamp': message.created_at.strftime('%b %d, %Y %H:%M'),
                'type': 'sent' if message.sender == request.user else 'received',
                'read': message.read
            })
        
        return JsonResponse({
            'success': True,
            'messages': message_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def send_message_general(request):
    """Send a message to a user (all authenticated users)."""
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver')
        content = request.POST.get('content')

        if receiver_id and content:
            receiver = get_object_or_404(get_user_model(), id=receiver_id)
            
            # Prevent sending message to self
            if receiver.id == request.user.id:
                messages.error(request, 'You cannot send a message to yourself.')
                return redirect('messages')
            
            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content
            )
            messages.success(request, f'Message sent to {receiver.username}.')
            return redirect('messages')

    # If GET request or form validation fails, redirect to messages
    return redirect('messages')


# Post Views - Anonymous users can view posts
class PostListView(ListView):
    model = Post
    template_name = 'core/post_list.html'
    context_object_name = 'posts'
    paginate_by = 12


class PostDetailView(DetailView):
    model = Post
    template_name = 'core/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        context['comments'] = post.comments.all()
        context['likes_count'] = post.likes.count()
        if self.request.user.is_authenticated:
            context['user_liked'] = Like.objects.filter(
                post=post, user=self.request.user
            ).exists()
        return context


# Comment Views - Anonymous users can view comments, authenticated users can add
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
    return redirect('post_detail', pk=post_id)


# CRUD Views for Posts
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            
            # Analyze post with BERT model for fake news detection
            text_to_analyze = f"{post.title} {post.content}"
            detection_result = fake_news_detector.analyze(text_to_analyze)
            
            if detection_result.get('is_fake'):
                post.potentially_fake = True
                post.trust_score = 0.0
                post.fake_confidence = detection_result.get('confidence')
            else:
                post.trust_score = 50.0  # Default trust score for non-fake posts
                post.fake_confidence = detection_result.get('confidence')
            
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'core/post_form.html', {'form': form, 'action': 'Create'})


@login_required
def update_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Permission check: only post owner can update
    if post.user != request.user and not request.user.is_admin:
        raise PermissionDenied("You don't have permission to edit this post.")
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'core/post_form.html', {'form': form, 'action': 'Update', 'post': post})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Permission check: only post owner can delete
    if post.user != request.user and not request.user.is_admin:
        raise PermissionDenied("You don't have permission to delete this post.")
    
    if request.method == 'POST':
        post.delete()
        return redirect('post_list')
    return render(request, 'core/post_confirm_delete.html', {'post': post})


# Report View
@login_required
def report_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Prevent reporting of verified posts
    if post.verified_content:
        messages.error(request, 'This post has been verified and cannot be reported.')
        return redirect('post_detail', pk=post.pk)
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.post = post
            report.user = request.user
            report.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = ReportForm()
    
    return render(request, 'core/report_form.html', {'form': form, 'post': post})


# Like Views - Anonymous users can see trust rating
@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    return redirect('post_detail', pk=post_id)


# Self-Assessment View - Authenticated users can take assessments
@login_required
def assessment_reports(request):
    """View for users to see their assessment reports."""
    user_assessments = UserAssessment.objects.filter(
        user=request.user
    ).select_related('assessment').order_by('-created_at')
    
    context = {
        'user_assessments': user_assessments,
    }
    return render(request, 'core/assessment_reports.html', context)


@login_required
def self_assessment(request):
    if request.method == 'POST':
        answers = request.POST.get('answers')
        if answers:
            answers_data = json.loads(answers)
            
            # Calculate risk score based on answers
            risk_score = calculate_risk_score(answers_data)
            
            # Analyze sentiment
            sentiment = analyze_sentiment(answers_data)
            
            # Save assessment
            if request.user.is_authenticated:
                Assessment.objects.create(
                    user=request.user,
                    answers=answers_data,
                    risk_score=risk_score,
                    sentiment=sentiment
                )
            else:
                # Anonymous assessment
                Assessment.objects.create(
                    user=None,
                    answers=answers_data,
                    risk_score=risk_score,
                    sentiment=sentiment
                )
            
            return render(request, 'core/assessment_result.html', {
                'risk_score': risk_score,
                'sentiment': sentiment
            })
    
    return render(request, 'core/self_assessment.html')


def calculate_risk_score(answers):
    """Simple risk score calculation based on assessment answers."""
    score = 0
    for answer in answers.values():
        if isinstance(answer, int):
            score += answer
    return min(score / len(answers) * 20, 100) if answers else 0


def analyze_sentiment(answers):
    """Simple sentiment analysis based on assessment answers."""
    text_answers = [str(v) for v in answers.values() if isinstance(v, str)]
    if not text_answers:
        return "Neutral"
    
    # Simple keyword-based sentiment analysis
    negative_keywords = ['bad', 'worse', 'terrible', 'helpless', 'hopeless']
    positive_keywords = ['good', 'better', 'hopeful', 'optimistic', 'improving']
    
    text = ' '.join(text_answers).lower()
    negative_count = sum(1 for word in negative_keywords if word in text)
    positive_count = sum(1 for word in positive_keywords if word in text)
    
    if negative_count > positive_count:
        return "Negative"
    elif positive_count > negative_count:
        return "Positive"
    return "Neutral"


# Moderator Views
@moderator_required
def moderator_dashboard(request):
    """Dashboard for moderators to see overview of reported posts and stats."""
    # Stats
    total_reports = Report.objects.count()
    pending_reports = Report.objects.filter(reviewed=False).count()
    fake_posts = Post.objects.filter(is_fake=True).count()
    potentially_fake_count = Post.objects.filter(potentially_fake=True, is_fake=False).count()
    
    # Sections
    bert_flagged_posts = Post.objects.filter(
        potentially_fake=True, is_fake=False
    ).select_related('user').order_by('-created_at')[:10]
    
    user_reports = Report.objects.filter(
        reviewed=False
    ).select_related('post', 'user', 'post__user').order_by('-created_at')[:10]
    
    all_users = User.objects.all().order_by('username')
    
    context = {
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'fake_posts': fake_posts,
        'potentially_fake_count': potentially_fake_count,
        'bert_flagged_posts': bert_flagged_posts,
        'user_reports': user_reports,
        'all_users': all_users,
    }
    return render(request, 'core/moderator_dashboard.html', context)


@moderator_required
def reported_posts(request):
    """View all reported posts."""
    reports = Report.objects.all().select_related('post', 'user', 'post__user').order_by('-created_at')
    
    context = {
        'reports': reports,
    }
    return render(request, 'core/reported_posts.html', context)


@moderator_required
def potentially_fake_posts(request):
    """View all potentially fake posts flagged by BERT model."""
    posts = Post.objects.filter(potentially_fake=True, is_fake=False).select_related('user').order_by('-created_at')
    
    context = {
        'posts': posts,
    }
    return render(request, 'core/potentially_fake_posts.html', context)


@moderator_required
def mark_post_fake(request, post_id):
    """Mark a post as fake."""
    post = get_object_or_404(Post, id=post_id)
    post.is_fake = True
    post.save()
    messages.success(request, f'Post "{post.title}" has been marked as fake.')
    return redirect('reported_posts')


@moderator_required
def confirm_fake_post(request, post_id):
    """Confirm post as fake and delete it."""
    post = get_object_or_404(Post, id=post_id)
    post_title = post.title
    post.delete()
    messages.success(request, f'Post "{post_title}" has been confirmed as fake and deleted.')
    return redirect('potentially_fake_posts')


@moderator_required
def moderator_delete_post(request, post_id):
    """Delete a post as moderator/admin."""
    post = get_object_or_404(Post, id=post_id)
    post_title = post.title
    post.delete()
    messages.success(request, f'Post "{post_title}" has been deleted.')
    return redirect('potentially_fake_posts')


@moderator_required
def view_post_detail(request, post_id):
    """View post details for moderation."""
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'core/post_detail_moderator.html', {'post': post})


@moderator_required
def delete_user_and_posts(request, user_id):
    """Delete a user and all their posts (admin only)."""
    if not request.user.is_admin:
        raise PermissionDenied("Only admins can delete users.")
    
    user = get_object_or_404(User, id=user_id)
    username = user.username
    
    # Delete all user's posts
    Post.objects.filter(user=user).delete()
    
    # Delete the user
    user.delete()
    
    messages.success(request, f'User "{username}" and all their posts have been deleted.')
    return redirect('potentially_fake_posts')


@moderator_required
def chat_with_post_owner(request, post_id):
    """Chat with the owner of a post."""
    post = get_object_or_404(Post, id=post_id)
    post_owner = post.user
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=post_owner,
                content=content
            )
            messages.success(request, f'Message sent to {post_owner.username}.')
            return redirect('potentially_fake_posts')
    
    # Get conversation history
    sent_messages = Message.objects.filter(
        sender=request.user, receiver=post_owner
    ).order_by('-created_at')[:20]
    received_messages = Message.objects.filter(
        sender=post_owner, receiver=request.user
    ).order_by('-created_at')[:20]
    
    context = {
        'post': post,
        'post_owner': post_owner,
        'sent_messages': sent_messages,
        'received_messages': received_messages,
    }
    return render(request, 'core/chat_with_owner.html', context)


@moderator_required
def dismiss_report(request, report_id):
    """Dismiss a report."""
    report = get_object_or_404(Report, id=report_id)
    report.reviewed = True
    report.save()
    messages.success(request, 'Report has been dismissed.')
    return redirect('reported_posts')


@moderator_required
def verify_post(request, post_id):
    """Verify a post as 100% trustworthy."""
    post = get_object_or_404(Post, id=post_id)
    post.verified_content = True
    post.trust_score = 100.0
    post.save()
    messages.success(request, f'Post "{post.title}" has been verified as 100% trustworthy.')
    return redirect('post_detail', pk=post_id)


@moderator_required
def unverify_post(request, post_id):
    """Unverify a post (remove 100% trust status)."""
    post = get_object_or_404(Post, id=post_id)
    post.verified_content = False
    post.trust_score = 50.0
    post.save()
    messages.success(request, f'Post "{post.title}" has been unverified.')
    return redirect('post_detail', pk=post_id)


@moderator_or_expert_required
def send_message(request):
    """Send a message to a user (moderators and experts only)."""
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver')
        content = request.POST.get('content')

        if receiver_id and content:
            receiver = get_object_or_404(User, id=receiver_id)
            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content
            )
            messages.success(request, f'Message sent to {receiver.username}.')
            if request.user.is_moderator:
                return redirect('moderator_dashboard')
            else:
                return redirect('expert_dashboard')

    users = User.objects.all()
    return render(request, 'core/send_message.html', {'users': users})


# Healthcare Expert Views
@expert_required
def expert_dashboard(request):
    """Dashboard for healthcare experts."""
    high_risk_users = User.objects.filter(is_high_risk=True).count()
    total_assessments = Assessment.objects.count()
    high_risk_assessments = Assessment.objects.filter(risk_score__gte=60).count()
    verified_posts = Post.objects.filter(verified_content=True).count()
    
    recent_assessments = Assessment.objects.filter(risk_score__gte=60).select_related('user').order_by('-created_at')[:10]
    
    context = {
        'high_risk_users': high_risk_users,
        'total_assessments': total_assessments,
        'high_risk_assessments': high_risk_assessments,
        'verified_posts': verified_posts,
        'recent_assessments': recent_assessments,
    }
    return render(request, 'core/expert_dashboard.html', context)


@expert_required
def create_verified_post(request):
    """Create a verified educational post."""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.verified_content = True
            post.trust_score = 100.0  # Maximum trust score for verified expert posts
            post.potentially_fake = False
            post.fake_confidence = 0.0  # No fake confidence for verified posts
            post.save()
            messages.success(request, 'Verified educational post created successfully.')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'core/verified_post_form.html', {'form': form, 'action': 'Create Verified Post'})


@expert_required
def high_risk_users(request):
    """View high-risk users."""
    users = User.objects.filter(is_high_risk=True).order_by('-created_at')
    assessments = Assessment.objects.filter(risk_score__gte=60).select_related('user').order_by('-risk_score')
    
    context = {
        'users': users,
        'assessments': assessments,
    }
    return render(request, 'core/high_risk_users.html', context)


@expert_required
def send_guidance(request, user_id):
    """Send guidance message to a user (experts only)."""
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=user,
                content=content
            )
            messages.success(request, f'Guidance message sent to {user.username}.')
            return redirect('high_risk_users')

    return render(request, 'core/send_guidance.html', {'user': user})


@expert_required
def rehabilitation_planning(request, user_id):
    """Assist in rehabilitation planning for a user."""
    user = get_object_or_404(User, id=user_id)
    goals = RehabilitationGoal.objects.filter(user=user).order_by('-created_at')
    assessments = Assessment.objects.filter(user=user).order_by('-created_at')
    
    if request.method == 'POST':
        goal_text = request.POST.get('goal_text')
        if goal_text:
            RehabilitationGoal.objects.create(
                user=user,
                goal_text=goal_text,
                progress_percentage=0
            )
            messages.success(request, f'Rehabilitation goal added for {user.username}.')
            return redirect('rehabilitation_planning', user_id=user_id)
    
    context = {
        'user': user,
        'goals': goals,
        'assessments': assessments,
    }
    return render(request, 'core/rehabilitation_planning.html', context)


@expert_required
def update_goal_progress(request, goal_id):
    """Update progress of a rehabilitation goal."""
    goal = get_object_or_404(RehabilitationGoal, id=goal_id)
    
    if request.method == 'POST':
        progress = request.POST.get('progress_percentage')
        if progress:
            goal.progress_percentage = int(progress)
            if goal.progress_percentage >= 100:
                goal.completed = True
                from django.utils import timezone
                goal.completed_at = timezone.now()
            goal.save()
            messages.success(request, 'Goal progress updated.')
    
    return redirect('rehabilitation_planning', user_id=goal.user.id)


# Dynamic Assessment System Views
def assessment_list(request):
    """List all available assessments - accessible to all users."""
    assessments = AssessmentTemplate.objects.all().select_related('created_by')
    return render(request, 'core/assessment_list.html', {'assessments': assessments})


def assessment_detail(request, assessment_id):
    """Get assessment questions - accessible to all users."""
    assessment = get_object_or_404(AssessmentTemplate, id=assessment_id)
    questions = assessment.questions.all()

    # Group questions by category
    grouped_questions = {
        'severity': questions.filter(category='severity'),
        'readiness': questions.filter(category='readiness'),
        'mental_state': questions.filter(category='mental_state'),
    }

    return render(request, 'core/assessment_detail.html', {
        'assessment': assessment,
        'grouped_questions': grouped_questions,
    })


@csrf_exempt
def assessment_submit(request, assessment_id):
    """Submit assessment responses and get AI analysis - accessible to all users."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    assessment = get_object_or_404(AssessmentTemplate, id=assessment_id)
    
    try:
        responses = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # Determine user or session
    if request.user.is_authenticated:
        user = request.user
        session_id = None
        # Delete existing assessment for this user and assessment template
        UserAssessment.objects.filter(user=user, assessment=assessment).delete()
    else:
        user = None
        session_id = request.session.get('assessment_session_id', str(uuid.uuid4()))
        request.session['assessment_session_id'] = session_id
        # Delete existing assessment for this session and assessment template
        UserAssessment.objects.filter(session_id=session_id, assessment=assessment).delete()
    
    # Create UserAssessment record
    user_assessment = UserAssessment.objects.create(
        user=user,
        session_id=session_id,
        assessment=assessment,
        responses=responses
    )
    
    # Call Groq AI for analysis
    ai_result = analyze_assessment_with_groq(responses)
    
    # Update UserAssessment with AI results
    user_assessment.severity_level = ai_result.get('severity_level')
    user_assessment.readiness_level = ai_result.get('readiness_level')
    user_assessment.mental_state_summary = ai_result.get('mental_state_summary')
    user_assessment.ai_report = ai_result.get('full_report', json.dumps(ai_result))
    user_assessment.save()
    
    # Mark user as high risk if severity is High or Critical
    if user and ai_result.get('severity_level') in ['High', 'Critical']:
        user.is_high_risk = True
        user.save()
    
    return JsonResponse({
        'success': True,
        'assessment_id': user_assessment.id,
        'severity_level': user_assessment.severity_level,
        'readiness_level': user_assessment.readiness_level,
        'mental_state_summary': user_assessment.mental_state_summary,
        'ai_report': user_assessment.ai_report,
        'recommendations': ai_result.get('recommendations')
    })


# Group Views
class GroupListView(ListView):
    model = CommunityGroup
    template_name = 'core/group_list.html'
    context_object_name = 'groups'
    paginate_by = 12

    def get_queryset(self):
        return CommunityGroup.objects.filter(is_active=True)


class GroupDetailView(DetailView):
    model = CommunityGroup
    template_name = 'core/group_detail.html'
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_member'] = CommunityGroupMembership.objects.filter(
                user=self.request.user, group=self.object
            ).exists()
            # Only show messages to members
            if context['is_member']:
                context['messages'] = self.object.messages.filter(reply_to=None).order_by('created_at')
                context['pinned_messages'] = self.object.messages.filter(is_pinned=True, reply_to=None).order_by('created_at')
        else:
            context['messages'] = []
            context['pinned_messages'] = []
        return context


@login_required
def create_group(request):
    """Create a group - admin and expert only."""
    if not (request.user.is_admin or request.user.is_expert):
        raise PermissionDenied("Only admins and experts can create groups.")
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name and description:
            group = CommunityGroup.objects.create(
                name=name,
                description=description,
                created_by=request.user
            )
            # Add creator as admin member
            CommunityGroupMembership.objects.create(
                user=request.user,
                group=group,
                is_admin=True
            )
            messages.success(request, f'Group "{group.name}" has been created successfully.')
            return redirect('group_detail', pk=group.pk)
        else:
            messages.error(request, 'Please provide both name and description.')
    
    return render(request, 'core/create_group.html')


@login_required
def join_group(request, pk):
    """Join a group - any logged-in user can join."""
    group = get_object_or_404(CommunityGroup, pk=pk, is_active=True)
    
    # Check if already a member
    if CommunityGroupMembership.objects.filter(user=request.user, group=group).exists():
        messages.warning(request, 'You are already a member of this group.')
    else:
        CommunityGroupMembership.objects.create(user=request.user, group=group)
        messages.success(request, f'You have successfully joined "{group.name}".')
    
    return redirect('group_detail', pk=group.pk)


@login_required
def leave_group(request, pk):
    """Leave a group."""
    group = get_object_or_404(CommunityGroup, pk=pk)
    membership = get_object_or_404(CommunityGroupMembership, user=request.user, group=group)
    
    # Don't allow creators to leave their own groups
    if group.created_by == request.user:
        messages.error(request, 'Group creators cannot leave their own groups.')
    else:
        membership.delete()
        messages.success(request, f'You have left "{group.name}".')
    
    return redirect('group_detail', pk=group.pk)


# Research Paper Views
class ResearchPaperListView(ListView):
    model = ResearchPaper
    template_name = 'core/research_paper_list.html'
    context_object_name = 'papers'
    paginate_by = 12

    def get_queryset(self):
        return ResearchPaper.objects.all()


class ResearchPaperDetailView(DetailView):
    model = ResearchPaper
    template_name = 'core/research_paper_detail.html'
    context_object_name = 'paper'


@login_required
def create_research_paper(request):
    """Create a research paper - experts only."""
    if not request.user.is_expert:
        raise PermissionDenied("Only experts can publish research papers.")
    
    if request.method == 'POST':
        title = request.POST.get('title')
        abstract = request.POST.get('abstract')
        content = request.POST.get('content')
        authors = request.POST.get('authors')
        publication_date = request.POST.get('publication_date')
        journal = request.POST.get('journal', '')
        doi = request.POST.get('doi', '')
        keywords = request.POST.get('keywords', '')
        pdf_file = request.FILES.get('pdf_file')
        
        if title and abstract and content and authors:
            paper = ResearchPaper.objects.create(
                title=title,
                abstract=abstract,
                content=content,
                authors=authors,
                published_by=request.user,
                publication_date=publication_date or None,
                journal=journal,
                doi=doi,
                keywords=keywords,
                pdf_file=pdf_file
            )
            messages.success(request, f'Research paper "{paper.title}" has been published successfully.')
            return redirect('research_paper_detail', pk=paper.pk)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'core/create_research_paper.html')


@login_required
def edit_research_paper(request, pk):
    """Edit a research paper - expert can edit their own papers."""
    paper = get_object_or_404(ResearchPaper, pk=pk)
    
    # Permission check - only experts can edit, and only their own papers
    if not request.user.is_expert or paper.published_by != request.user:
        raise PermissionDenied("You can only edit your own research papers.")
    
    if request.method == 'POST':
        title = request.POST.get('title')
        abstract = request.POST.get('abstract')
        content = request.POST.get('content')
        authors = request.POST.get('authors')
        publication_date = request.POST.get('publication_date')
        journal = request.POST.get('journal', '')
        doi = request.POST.get('doi', '')
        keywords = request.POST.get('keywords', '')
        pdf_file = request.FILES.get('pdf_file')
        
        if title and abstract and content and authors:
            paper.title = title
            paper.abstract = abstract
            paper.content = content
            paper.authors = authors
            paper.publication_date = publication_date or None
            paper.journal = journal
            paper.doi = doi
            paper.keywords = keywords
            if pdf_file:
                paper.pdf_file = pdf_file
            paper.save()
            messages.success(request, f'Research paper "{paper.title}" has been updated successfully.')
            return redirect('research_paper_detail', pk=paper.pk)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'paper': paper,
    }
    return render(request, 'core/edit_research_paper.html', context)


@login_required
def send_group_message(request, pk):
    """Send a message to a group - all members can send messages."""
    group = get_object_or_404(CommunityGroup, pk=pk)
    
    # Check if user is a member
    if not CommunityGroupMembership.objects.filter(user=request.user, group=group).exists():
        raise PermissionDenied("You must be a member to send messages.")
    
    if request.method == 'POST':
        content = request.POST.get('content')
        reply_to_id = request.POST.get('reply_to')
        
        if content:
            reply_to = None
            if reply_to_id:
                reply_to = get_object_or_404(GroupMessage, pk=reply_to_id, group=group)
            
            message = GroupMessage.objects.create(
                group=group,
                sender=request.user,
                content=content,
                reply_to=reply_to
            )
            messages.success(request, 'Message sent successfully.')
        else:
            messages.error(request, 'Message cannot be empty.')
    
    return redirect('group_detail', pk=group.pk)


@login_required
def pin_group_message(request, pk, message_id):
    """Pin/unpin a group message - group admins and moderators only."""
    group = get_object_or_404(CommunityGroup, pk=pk)
    message = get_object_or_404(GroupMessage, pk=message_id, group=group)
    
    # Check permissions - group creator, system admin, or moderator
    membership = CommunityGroupMembership.objects.filter(user=request.user, group=group, is_admin=True).first()
    if not (request.user.is_admin or request.user.is_moderator or membership):
        raise PermissionDenied("You don't have permission to pin messages.")
    
    message.is_pinned = not message.is_pinned
    message.save()
    
    action = "pinned" if message.is_pinned else "unpinned"
    messages.success(request, f'Message {action} successfully.')
    
    return redirect('group_detail', pk=group.pk)
