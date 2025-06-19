from django.contrib.auth import get_user_model, update_session_auth_hash
from app.forms import *
from app.models import *
import random
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, redirect
from app.models import Course, Enrollment, QuestionPaper
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest, FileResponse, HttpResponse
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.urls import reverse
from app.models import BlogPost
from app.forms import BlogPostForm, BlogCommentForm
from django.http import JsonResponse
from app.models import Course, Message
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models import Q
from django.db.models import F, DecimalField, ExpressionWrapper


# Create your views here.

# ---------------------------------------------------------------------------
# Login view
# ---------------------------------------------------------------------------
def landing_page(request):
    courses = Course.objects.all()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():

            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                # Redirect based on user type
                if user.user_type == 1:
                    return redirect('admin_begin_class_dashboard_container')
                elif user.user_type == 2:
                    return redirect('my_learnings')
                elif user.user_type == 3:
                    return redirect('course_provider/index')
                else:
                    return redirect('landing_page_before_login')
            else:
                messages.error(request, "Invalid login credentials.")
                return redirect('landing_page_before_login')
    else:
        form = LoginForm()

    if request.method == 'POST':
        studnetform = AdminForm(request.POST)
        if studnetform.is_valid():
            user_email = studnetform.cleaned_data['EmailID']

            # Check if the email already exists
            if get_user_model().objects.filter(email=user_email).exists():
                messages.error(request, 'This email is already in use.')
                return redirect('landing_page_before_login')  # Redirect back to the signup page

            # Create a new user instance
            user = get_user_model().objects.create_user(
                email=user_email,
                password=studnetform.cleaned_data['password1'],
                username=user_email,  # You can set username as email if you want
                user_type=2
            )
            # Generate a random OTP and send it to the user's email
            otp = generate_otp()

            # Send the OTP to the user's email
            send_otp(user_email, otp)

            # Save the OTP in the session
            request.session['otp'] = otp
            request.session['email'] = user_email

            return redirect('verify_otp')
    else:
        studnetform = AdminForm()

    return render(request, 'landing_page.html', {'courses': courses, 'form': form, 'studnetform': studnetform})


def landing_page_before_login(request):  # Student login

    if request.user.is_authenticated:
        if request.user.user_type == 1:  # Admin user type
            return redirect('admin_begin_class_dashboard_container')
        elif request.user.user_type == 3:  # Course provider user type
            return redirect('course_provider/index')
        # elif request.user.user_type == 2:  # Student user type
        # return redirect('my_learnings')
    courses = Course.objects.all()
    cousers_9th = Course.objects.filter(category_type='c2').first()
    cousers_10th = Course.objects.filter(category_type='c3').first()
    courses_11th = Course.objects.filter(category_type='c4').first()
    courses_12th = Course.objects.filter(category_type='c5').first()

    bundels = Bundle.objects.all()[0:3]
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():

            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                # Redirect based on user type
                if user.user_type == 1:
                    return redirect('admin_begin_class_dashboard_container')
                elif user.user_type == 2:
                    return redirect('my_learnings')
                elif user.user_type == 3:
                    return redirect('course_provider/index')
                else:
                    messages.error(request, "Invalid login credentials.")
                    return redirect('landing_page_before_login')
            else:
                messages.error(request, "Invalid login credentials.")
                return redirect('landing_page_before_login')
    else:
        form = LoginForm()

    if request.method == 'POST':
        studnetform = AdminForm(request.POST)
        if studnetform.is_valid():
            user_email = studnetform.cleaned_data['EmailID']

            # Check if the email already exists
            if get_user_model().objects.filter(email=user_email).exists():
                messages.error(request, 'This email is already in use.')
                return redirect('landing_page_before_login')  # Redirect back to the signup page

            # Create a new user instance
            user = get_user_model().objects.create_user(
                email=user_email,
                password=studnetform.cleaned_data['password1'],
                username=user_email,  # You can set username as email if you want
                user_type=2
            )
            # Generate a random OTP and send it to the user's email
            otp = generate_otp()

            # Send the OTP to the user's email
            send_otp(user_email, otp)

            # Save the OTP in the session
            request.session['otp'] = otp
            request.session['email'] = user_email

            return redirect('verify_otp')
    else:
        studnetform = AdminForm()

    profile_image = None
    if request.user.is_authenticated:
        profile_data = Profile.objects.filter(user=request.user).first()  # Fetch profile if exists
        if profile_data and profile_data.profile_picture:
            profile_image = profile_data
        else:
            profile_image = None

    return render(request, 'landing_page_before_login.html',
                  {'courses': courses, 'form': form, 'studnetform': studnetform, 'profile': profile_image,'cousers_9th':cousers_9th,'cousers_10th':cousers_10th,'courses_11th':courses_11th,'courses_12th':courses_12th,'bundels':bundels})


def register_CP(request):
    courses = Course.objects.all()  # Fetch courses if needed for context

    # Handle login form submission
    if request.method == 'POST' and 'email' in request.POST and 'password' in request.POST:
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            # Redirect based on user type
            if user.user_type == 2:
                return redirect('my_learnings')
            elif user.user_type == 3:
                return redirect('course_provider/index')
            else:
                return redirect('landing_page_before_login')
        else:
            messages.error(request, "Invalid login credentials.")
            return redirect('landing_page_before_login')

    # Handle registration form submission
    elif request.method == 'POST' and 'EmailID' in request.POST and 'password1' in request.POST:
        user_email = request.POST.get('EmailID')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('provider_register')

        # Check if the email already exists
        if get_user_model().objects.filter(email=user_email).exists():
            messages.error(request, 'This email is already in use.')
            return redirect('provider_register')

        # Create a new user
        user = get_user_model().objects.create_user(
            email=user_email,
            password=password1,
            username=user_email,  # Set username as email if required
            user_type=3  # Assuming user_type 2 is for students
        )

        # Generate and send OTP to the user's email
        otp = generate_otp()
        send_otp(user_email, otp)

        # Save OTP and email in session for verification
        request.session['otp'] = otp
        request.session['email'] = user_email

        messages.success(request, 'Account created successfully! Please verify your email.')
        return redirect('course_provider_verify_otp')

    # Display the profile picture if the user is authenticated
    profile = None
    if request.user.is_authenticated:
        profile_data = get_object_or_404(Profile, user=request.user)
        profile = profile_data if profile_data.profile_picture else None

    return render(request, 'registration/register_cp.html', {
        'courses': courses,  # Pass courses if needed in the template
        'profile': profile,
    })


def about_us(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():

            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('landing_page_before_login')
                # user_type = user.user_type
                # if user_type == 1:  # Assuming user_type is an integer field
                #     return redirect('admin')
                # elif user_type == 2:
                #     return redirect('course_catalog')
                # elif user_type == 3:
                #     return HttpResponse('course provider')
                # else:
                #     messages.error(request, "Invalid Login!")
            else:
                messages.error(request, "Invalid Login!")
    else:
        form = LoginForm()

    if request.method == 'POST':
        studnetform = AdminForm(request.POST)
        if studnetform.is_valid():
            user_email = studnetform.cleaned_data['EmailID']

            # Check if the email already exists
            if get_user_model().objects.filter(email=user_email).exists():
                messages.error(request, 'This email is already in use.')
                return redirect('landing_page_before_login')  # Redirect back to the signup page

            # Create a new user instance
            user = get_user_model().objects.create_user(
                email=user_email,
                password=studnetform.cleaned_data['password1'],
                username=user_email,  # You can set username as email if you want
                user_type=2
            )
            # Generate a random OTP and send it to the user's email
            otp = generate_otp()

            # Send the OTP to the user's email
            send_otp(user_email, otp)

            # Save the OTP in the session
            request.session['otp'] = otp
            request.session['email'] = user_email

            return redirect('verify_otp')
    else:
        studnetform = AdminForm()

    profile_image = []
    if request.user.is_authenticated:
        try:
            profile_data = Profile.objects.get(user=request.user)
            if profile_data.profile_picture:
                profile_image = profile_data.profile_picture.url
            else:
                profile_image = 10  # Default value or placeholder
        except Profile.DoesNotExist:
            profile_image = 10  # Default value if no profile exists
    else:
        profile_image = 10  # Default for unauthenticated users

    return render(request, 'about_us.html', {'form': form, 'studnetform': studnetform, 'profile': profile_image})


def contact_us(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():

            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('landing_page_before_login')
                # user_type = user.user_type
                # if user_type == 1:  # Assuming user_type is an integer field
                #     return redirect('admin')
                # elif user_type == 2:
                #     return redirect('course_catalog')
                # elif user_type == 3:
                #     return HttpResponse('course provider')
                # else:
                #     messages.error(request, "Invalid Login!")
            else:
                messages.error(request, "Invalid Login!")
    else:
        form = LoginForm()

    if request.method == 'POST':
        studnetform = AdminForm(request.POST)
        if studnetform.is_valid():
            user_email = studnetform.cleaned_data['EmailID']

            # Check if the email already exists
            if get_user_model().objects.filter(email=user_email).exists():
                messages.error(request, 'This email is already in use.')
                return redirect('landing_page_before_login')  # Redirect back to the signup page

            # Create a new user instance
            user = get_user_model().objects.create_user(
                email=user_email,
                password=studnetform.cleaned_data['password1'],
                username=user_email,  # You can set username as email if you want
                user_type=2
            )
            # Generate a random OTP and send it to the user's email
            otp = generate_otp()

            # Send the OTP to the user's email
            send_otp(user_email, otp)

            # Save the OTP in the session
            request.session['otp'] = otp
            request.session['email'] = user_email

            return redirect('verify_otp')
    else:
        studnetform = AdminForm()

    profile_image = []
    if request.user.is_authenticated:
        try:
            profile_data = Profile.objects.get(user=request.user)
            if profile_data.profile_picture:
                profile_image = profile_data.profile_picture.url
            else:
                profile_image = 10  # Default value or placeholder
        except Profile.DoesNotExist:
            profile_image = 10  # Default value if no profile exists
    else:
        profile_image = 10  # Default for unauthenticated users

    return render(request, 'contact_us.html', {'form': form, 'studnetform': studnetform, 'profile': profile_image})


def course(request):
    courses = Course.objects.all()
    profile_image = None

    if request.user.is_authenticated:
        profile_data = Profile.objects.filter(user=request.user).first()
        profile_image = profile_data.profile_picture if profile_data and profile_data.profile_picture else None

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():

            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('landing_page_before_login')
                # user_type = user.user_type
                # if user_type == 1:  # Assuming user_type is an integer field
                #     return redirect('admin')
                # elif user_type == 2:
                #     return redirect('course_catalog')
                # elif user_type == 3:
                #     return HttpResponse('course provider')
                # else:
                #     messages.error(request, "Invalid Login!")
            else:
                messages.error(request, "Invalid Login!")
    else:
        form = LoginForm()

    if request.method == 'POST':
        studnetform = AdminForm(request.POST)
        if studnetform.is_valid():
            user_email = studnetform.cleaned_data['EmailID']

            # Check if the email already exists
            if get_user_model().objects.filter(email=user_email).exists():
                messages.error(request, 'This email is already in use.')
                return redirect('landing_page_before_login')  # Redirect back to the signup page

            # Create a new user instance
            user = get_user_model().objects.create_user(
                email=user_email,
                password=studnetform.cleaned_data['password1'],
                username=user_email,  # You can set username as email if you want
                user_type=2
            )
            # Generate a random OTP and send it to the user's email
            otp = generate_otp()

            # Send the OTP to the user's email
            send_otp(user_email, otp)

            # Save the OTP in the session
            request.session['otp'] = otp
            request.session['email'] = user_email

            return redirect('verify_otp')
    else:
        studnetform = AdminForm()

    # profile_image = get_object_or_404(Profile, user=request.user)
    return render(request, 'course.html',
                  {'courses': courses, 'form': form, 'studnetform': studnetform, 'profile': profile_image})


def courses(request, course_id):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():

            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('landing_page_before_login')
                # user_type = user.user_type
                # if user_type == 1:  # Assuming user_type is an integer field
                #     return redirect('admin')
                # elif user_type == 2:
                #     return redirect('course_catalog')
                # elif user_type == 3:
                #     return HttpResponse('course provider')
                # else:
                #     messages.error(request, "Invalid Login!")
            else:
                messages.error(request, "Invalid Login!")
    else:
        form = LoginForm()

    if request.method == 'POST':
        studnetform = AdminForm(request.POST)
        if studnetform.is_valid():
            user_email = studnetform.cleaned_data['EmailID']

            # Check if the email already exists
            if get_user_model().objects.filter(email=user_email).exists():
                messages.error(request, 'This email is already in use.')
                return redirect('landing_page_before_login')  # Redirect back to the signup page

            # Create a new user instance
            user = get_user_model().objects.create_user(
                email=user_email,
                password=studnetform.cleaned_data['password1'],
                username=user_email,  # You can set username as email if you want
                user_type=2
            )
            # Generate a random OTP and send it to the user's email
            otp = generate_otp()

            # Send the OTP to the user's email
            send_otp(user_email, otp)

            # Save the OTP in the session
            request.session['otp'] = otp
            request.session['email'] = user_email

            return redirect('verify_otp')
    else:
        studnetform = AdminForm()

    profile_image = []
    if request.user.is_authenticated:
        try:
            profile_data = Profile.objects.get(user=request.user)
            if profile_data.profile_picture:
                profile_image = profile_data.profile_picture.url
            else:
                profile_image = 10  # Default value or placeholder
        except Profile.DoesNotExist:
            profile_image = 10  # Default value if no profile exists
    else:
        profile_image = 10  # Default for unauthenticated users
    course = Course.objects.get(id=course_id)
    courses = [course]
    return render(request, 'course.html',
                  {'courses': courses, 'form': form, 'studnetform': studnetform, 'profile': profile_image})


def common_discussion_forum(request):
    return render(request, 'common_discussion_forum.html')


def single_post_discussion_forum(request):
    return render(request, 'single_post_discussion_forum.html')


def week_basis_discussion_forum(request):
    return render(request, 'week_basis_discussion_forum.html')


@login_required
def my_learnings(request):
    User = get_user_model()  # Get the custom user model
    student = Student.objects.get(user=request.user)
    enrollments = Enrollment.objects.filter(user=student)

    course_progress_data = []
    has_completed_course = False

    for enrollment in enrollments:
        course = enrollment.course
        total_topics = sum(week.topics.count() for week in course.weeks.all())
        watched_topics = sum(
            topic.watched_by_users.filter(id=student.id).exists() for week in course.weeks.all() for topic in week.topics.all()
        )

        if total_topics > 0:
            progress_percentage = round((watched_topics / total_topics) * 100)
        else:
            progress_percentage = 0

        if progress_percentage == 100:
            has_completed_course = True

        course_progress_data.append({
            'course': course,
            'total_topics': total_topics,
            'watched_topics': watched_topics,
            'progress_percentage': progress_percentage,
        })

    filter_status = request.GET.get('status', 'in_progress')
    if filter_status == 'completed':
        filtered_courses = [data for data in course_progress_data if data['progress_percentage'] == 100]
    else:
        filtered_courses = [data for data in course_progress_data if data['progress_percentage'] < 100]

    if request.user.is_authenticated:
        # Fetch the logged-in student's profile
        student = get_object_or_404(Student, user=request.user)
        std = request.user.student
        # Retrieve wishlist courses
        wishlist_courses = std.wishlist.all()

    else:
        wishlist_courses = []

    profile_image = None
    if request.user.is_authenticated:
        profile_data = Profile.objects.filter(user=request.user).first()  # Fetch profile if exists
        if profile_data and profile_data.profile_picture:
            profile_image = profile_data
        else:
            profile_image = None

    context = {
        'course_progress_data': filtered_courses,
        'filter_status': filter_status,
        'wishlist_courses': wishlist_courses,
        'profile': profile_image,
    }

    return render(request, 'my_learnings.html', context)


def cart(request):
    cart_courses = request.user.student.cart.all()
    user = CustomeUser.objects.get(username=request.user.username)
    profile_image = []
    if request.user.is_authenticated:
        try:
            profile_data = Profile.objects.get(user=request.user)
            if profile_data.profile_picture:
                profile_image = profile_data.profile_picture.url
            else:
                profile_image = 10  # Default value or placeholder
        except Profile.DoesNotExist:
            profile_image = 10  # Default value if no profile exists
    else:
        profile_image = 10  # Default for unauthenticated users
    return render(request, 'cart.html', {'cart_courses': cart_courses, 'profile': profile_image,'user':user})


def search_page(request):
    return render(request, 'search_page.html')


def course_after_login(request):
    return render(request, 'course_after_login.html')


def roadmap_after_pg(request):
    return render(request, 'roadmap_after_pg.html')


def roadmap_after_pg_in_comm(request):
    return render(request, 'roadmap_after_pg_in_comm.html')


def roadmap_after_pg_in_elec(request):
    return render(request, 'roadmap_after_pg_in_elec.html')


def roadmap_after_pg_in_hm(request):
    return render(request, 'roadmap_after_pg_in_hm.html')


def notes(request):
    return render(request, 'notes.html')


def download_pdf(request):
    return render(request, 'download_pdf.html')


def module(request):
    return render(request, 'module.html')


def my_course(request):
    return render(request, 'my_course.html')


def course_material(request, id):
    user = Student.objects.get(user=request.user)
    course = get_object_or_404(Course, id=id)

    weeks = Week.objects.filter(course=course).prefetch_related('topics')

    watched_topics = Topic.objects.filter(watched_by_users=user, week__course=course)
    unlocked_quizzes = Quiz.objects.filter(topic__in=watched_topics)

    quizzes_data = []
    for quiz in unlocked_quizzes:
        quizzes_data.append({
            'quiz_id': quiz.id,
            'video_title': quiz.topic.title,
            'status': 'Unlocked' if user in quiz.topic.watched_by_users.all() else 'Locked',
            'due_date': quiz.due_date,
            'weight': quiz.weight,
            'score': round(quiz.results.get(student=user).score / quiz.results.get(student=user).total_questions * 100,
                           2) if quiz.results.filter(student=user).exists() else 'N/A'
        })

    messages = Message.objects.filter(course=course)
    messages_content = []
    for cont in messages:
        messages_content.append(cont.content)

    course_career_guidance = CareerGuidanceMessage.objects.filter(course=course)

    # selected_grade = request.GET.get('grade')

    profile_image = []
    if request.user.is_authenticated:
        profile_data = get_object_or_404(Profile, user=request.user)
    if request.user.is_authenticated:
        if profile_data.profile_picture:
            profile_image = get_object_or_404(Profile, user=request.user)
        else:
            profile_image = 10

    question_papers = QuestionPaper.objects.all()

    notes = Note.objects.filter(course=course).order_by('-created_at')

    guidance_messages = CareerGuidanceMessage.objects.filter(course=course)
    return render(request, 'course_material.html', {
        'course': course,
        'weeks': weeks,
        'quizzes_data': quizzes_data,
        'quizzes': unlocked_quizzes,
        'messages': messages_content,
        'career_guidance': course_career_guidance,
        'question_papers': question_papers,
        'notes': notes,
        'profile': profile_image,
        'guidance_messages': guidance_messages,
    })


def notes_list(request, course_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        course = get_object_or_404(Course, id=course_id)
        student = get_object_or_404(Student, user=request.user)
        if content:
            Note.objects.create(student=student, course=course, content=content)
        return redirect('my_learnings')  # Redirect to the same page after saving

    # notes = Note.objects.filter(course=course).order_by('-created_at')
    return render(request, 'my_learnings.html')



def reply_to_post(request):
    return render(request, 'reply_to_post.html')


def course_video(request, id):
    # course = get_object_or_404(Course, id=course_id)
    # week = get_object_or_404(Week, id=week_id, course=course)
    # topic = get_object_or_404(Topic, id=topic_id, week=week)
    topic = Topic.objects.get(id=id)

    profile_image = get_object_or_404(Profile, user=request.user)

    # video = get_object_or_404(CourseYouTubeVideo, course=course)


    context = {
        # 'course': course,
        # 'week': week,
        'topic': topic,
        'profile': profile_image,
        # 'video_link':video,
    }

    return render(request, 'course_video.html', context)


def course_overview(request):
    return render(request, 'course_overview.html')


def quiz_page(request, id):
    profile_image = get_object_or_404(Profile, user=request.user)
    course = get_object_or_404(Course, id=id)
    all_quizzes = Quiz.objects.filter(course=course)
    context = {
        'quizzes': all_quizzes,
        'course': course,
        'profile': profile_image
    }
    return render(request, 'quiz_page.html', context)


# ---------------------------------
@login_required
def display_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.quiz_questions.all().order_by('question_no')
    student = Student.objects.get(user=request.user)

    if request.method == 'POST':
        score = 0
        total_questions = questions.count()

        for question in questions:
            selected_option = request.POST.get(f'question_{question.id}')
            if selected_option == question.correct_option:
                score += 1

            # Save or update the selected answers
            selected_answer, created = SelectedAnswer.objects.update_or_create(
                student=student,
                quiz=quiz,
                question=question,
                defaults={'selected_option': selected_option}
            )

        # Save or update the quiz result
        QuizResult.objects.update_or_create(
            student=student,
            quiz=quiz,
            defaults={
                'score': score,
                'total_questions': total_questions,
                'completed_at': timezone.now()
            }
        )

        quiz_id = quiz.id
        success_url = reverse('quiz_results', kwargs={'quiz_id': quiz_id})
        return redirect(success_url)
    profile_image = get_object_or_404(Profile, user=request.user)
    return render(request, 'quiz_questions.html', {
        'quiz': quiz,
        'questions': questions,
        'profile': profile_image
    })


@login_required
def quiz_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    student = Student.objects.get(user=request.user)
    questions = quiz.quiz_questions.all().order_by('question_no')
    quiz_result = get_object_or_404(QuizResult, quiz=quiz, student=student)
    selected_answers = SelectedAnswer.objects.filter(student=student, quiz=quiz).select_related('question')
    profile_image = get_object_or_404(Profile, user=request.user)
    correct_answers_count = sum(
        1 for answer in selected_answers if answer.selected_option == answer.question.correct_option)
    percentage_score = (correct_answers_count / questions.count()) * 100 if questions.count() > 0 else 0

    context = {
        'quiz': quiz,
        'questions': questions,
        'selected_answers': selected_answers,
        'quiz_result': {
            'correct_answers_count': correct_answers_count,
        },
        'percentage_score': percentage_score,
        'profile': profile_image
    }

    return render(request, 'quiz_result.html', context)


# ----------------------------------
# def quiz_questions(request):
#     return render(request, 'quiz_questions.html')

def assessment_questions(request,id):
    assignment = get_object_or_404(AssignmentByProvider, id=id)
    student = Student.objects.get(user=request.user)

    profile_image = []

    if request.user.is_authenticated:
        profile_data = get_object_or_404(Profile, user=request.user)
    if request.user.is_authenticated:
        if profile_data.profile_picture:
            profile_image = get_object_or_404(Profile, user=request.user)
        else:
            profile_image = 10

    return render(request, 'assessment_questions.html',
                  {'profile':profile_image,
                   'course':course,
                   'assignment':assignment,
                  })


def assignment_page(request,id):
    course = get_object_or_404(Course, id=id)
    assignments = AssignmentByProvider.objects.filter(course=course)
    profile_image = []
    if request.user.is_authenticated:
        profile_data = get_object_or_404(Profile, user=request.user)
    if request.user.is_authenticated:
        if profile_data.profile_picture:
            profile_image = get_object_or_404(Profile, user=request.user)
        else:
            profile_image = 10
    return render(request, 'assignment_page.html',
                  {'profile':profile_image,
                  'course':course,
                  'assignments':assignments,
                   })


def result(request):
    profile_image = get_object_or_404(Profile, user=request.user)
    context = {
        'profile': profile_image
    }
    return render(request, 'result.html', context)


def quiz_result(request):
    profile_image = []
    if request.user.is_authenticated:
        profile_data = get_object_or_404(Profile, user=request.user)
    if request.user.is_authenticated:
        if profile_data.profile_picture:
            profile_image = get_object_or_404(Profile, user=request.user)
        else:
            profile_image = 10
    return render(request, 'quiz_result.html',{'profile':profile_image})


def assessment_result(request):
    profile_image = []
    if request.user.is_authenticated:
        profile_data = get_object_or_404(Profile, user=request.user)
    if request.user.is_authenticated:
        if profile_data.profile_picture:
            profile_image = get_object_or_404(Profile, user=request.user)
        else:
            profile_image = 10
    return render(request, 'assessment_result.html',{'profile':profile_image})


def certificate(request):
    user = Student.objects.get(user=request.user)
    profile_image = []
    if request.user.is_authenticated:
        profile_data = get_object_or_404(Profile, user=request.user)
    if request.user.is_authenticated:
        if profile_data.profile_picture:
            profile_image = get_object_or_404(Profile, user=request.user)
        else:
            profile_image = 10
    calculate_grade_for_student(user)

    certificates = Certificate.objects.filter(user=user)
    courses_with_certificates = {}

    # Group certificates by course and include grade
    for certificate in certificates:
        grade = Grade.objects.filter(certificate=certificate).first()
        courses_with_certificates[certificate.course] = {
            'certificate': certificate,
            'grade': grade.grade if grade else 'N/A'
        }

    return render(request, 'certificate.html',
                  {'courses_with_certificates': courses_with_certificates, 'profile': profile_image})


def calculate_grade_for_student(student):
    courses = Course.objects.filter(quizzes__results__student=student).distinct()

    for course in courses:
        quizzes = Quiz.objects.filter(course=course)
        total_weighted_score = 0.0

        for quiz in quizzes:
            quiz_results = QuizResult.objects.filter(student=student, quiz=quiz)
            if quiz_results.exists():
                quiz_result = quiz_results.latest('completed_at')
                weighted_score = (quiz_result.score / quiz_result.total_questions) * quiz.weight
                total_weighted_score += weighted_score

        final_grade = calculate_grade_from_score(total_weighted_score)

        certificate, created = Certificate.objects.get_or_create(user=student, course=course)
        Grade.objects.update_or_create(
            certificate=certificate,
            defaults={'grade': final_grade}
        )


def calculate_grade_from_score(score):
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'


@login_required
def download_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id, user=request.user.student)

    if not certificate.certificate_image:
        raise Http404("Certificate image not found")

    # Open the image file
    file_path = certificate.certificate_image.path
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='image/jpeg')
        response[
            'Content-Disposition'] = f'attachment; filename="{certificate.user.Full_Name} certificate {certificate.course.title}.jpg"'
        return response


def single_certificate(request, course_id):
    profile_image = None
    if request.user.is_authenticated:
        profile_data = Profile.objects.filter(user=request.user).first()  # Fetch profile if exists
        if profile_data and profile_data.profile_picture:
            profile_image = profile_data
        else:
            profile_image = None

    user = Student.objects.get(user=request.user)
    # Calculate grades for the student
    # Assuming calculate_grade_for_student is defined elsewhere
    calculate_grade_for_student(user)
    course_data = Course.objects.get(id=course_id)
    certificates = Certificate.objects.filter(user=user, course=course_data)
    courses_with_certificates = {}

    # Group certificates by course and include grade
    for certificate in certificates:
        grade = Grade.objects.filter(certificate=certificate).first()
        courses_with_certificates[certificate.course] = {
            'certificate': certificate,
            'grade': grade.grade if grade else 'N/A'
        }

    return render(request, 'single_certificate.html',
                  {'profile': profile_image, 'courses_with_certificates': courses_with_certificates})


@login_required
def download_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id, user=request.user.student)

    if not certificate.certificate_image:
        raise Http404("Certificate image not found")

    # Open the image file
    file_path = certificate.certificate_image.path
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='image/jpeg')
        response[
            'Content-Disposition'] = f'attachment; filename="{certificate.user.Full_Name} certificate {certificate.course.title}.jpg"'
        return response


def ticket(request):
    if request.method == 'POST':
        reason = request.POST.get('reason')
        description = request.POST.get('description')
        attachment = request.FILES.get('attachment')

        print("POST data received:", reason, description, attachment)
        ticket = Ticket.objects.create(
            user=request.user,
            reason=reason,
            description=description,
            attachment=attachment
        )
        print("Ticket created:", ticket)
        return redirect('ticket')
    profile_image = None
    if request.user.is_authenticated:
        try:
            profile_data = Profile.objects.get(user=request.user)
            profile_image = profile_data.profile_picture if profile_data.profile_picture else 10
        except Profile.DoesNotExist:
            profile_image = 10
    tickets = Ticket.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'ticket.html', {'tickets': tickets, 'profile': profile_image})


@login_required
def support_page(request):
    return render(request, 'support.html')


def get_chat_history(request):
    if request.method == 'GET':
        user = request.user

        if user.is_authenticated:
            if hasattr(user, 'student'):
                student = user.student
                chat_messages = ChatMessage.objects.filter(user=student).order_by('timestamp')
            else:
                chat_messages = ChatMessage.objects.filter(is_admin=True).order_by('timestamp')

            # Serialize the chat messages
            chat_history = []
            for message in chat_messages:
                chat_history.append({
                    'user': message.user.user.email if message.user else 'Admin',
                    'message': message.message,
                    'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'is_admin': message.is_admin,
                })

            return JsonResponse({'status': 'success', 'chat_history': chat_history})

        return JsonResponse({'status': 'error', 'message': 'User not authenticated'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def send_message(request):
    if request.method == 'POST':
        user = request.user

        # Check if the user is authenticated and is a Student
        if user.is_authenticated and hasattr(user, 'student'):
            student = user.student
            message_content = request.POST.get('message')

            if message_content:
                message = ChatMessage(user=student, message=message_content, is_admin=user.user_type == 1)
                message.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Message content is empty'})

        return JsonResponse({'status': 'error', 'message': 'User is not a student or not authenticated'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@login_required
def send_admin_message(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            chat_message = ChatMessage.objects.create(
                message=message,
                is_admin=True
            )
            return JsonResponse({'status': 'success', 'message': 'Message sent'})
        return JsonResponse({'status': 'error', 'message': 'Empty message'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def referral(request):
    profile_image = []
    if request.user.is_authenticated:
        profile_data = get_object_or_404(Profile, user=request.user)
    if request.user.is_authenticated:
        if profile_data.profile_picture:
            profile_image = get_object_or_404(Profile, user=request.user)
        else:
            profile_image = 10
    return render(request, 'referral.html', {'profile': profile_image})


@login_required
def referrals(request):
    if request.method == 'POST':
        referral_form = ReferralForm(request.POST)
        if referral_form.is_valid():
            referral = referral_form.save(commit=False)
            referral.user = request.user
            referral.save()
            return redirect('referral')
    else:
        referral_form = ReferralForm()
    profile_image = []
    if request.user.is_authenticated:
        profile_data = get_object_or_404(Profile, user=request.user)
    if request.user.is_authenticated:
        if profile_data.profile_picture:
            profile_image = get_object_or_404(Profile, user=request.user)
        else:
            profile_image = 10
    return render(request, 'referral.html', {'referral_form': referral_form, 'profile': profile_image})


def payment_history(request):
    payments = PaymentHistory.objects.filter(user=request.user)
    profile_image = []
    if request.user.is_authenticated:
        profile_data = get_object_or_404(Profile, user=request.user)
    if request.user.is_authenticated:
        if profile_data.profile_picture:
            profile_image = get_object_or_404(Profile, user=request.user)
        else:
            profile_image = 10
    return render(request, 'payment_history.html', {'payments': payments, 'profile': profile_image})


@login_required
def profile_page(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile_image = profile if profile.profile_picture else 10

    # Initialize forms
    profileform = ProfileUpdateForm(instance=profile)
    notificationform = NotificationSettingsForm(
    instance=getattr(request.user, 'notificationsettings', None))
    privacyform = PrivacySettingsForm(instance=getattr(request.user, 'privacysettings', None))
    email_form = EmailChangeForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)
    work_experience_form = WorkExperienceForm()
    education_form = EducationForm()
    project_form = ProjectForm()

    payments = PaymentHistory.objects.filter(user=request.user)

    if request.method == 'POST':
        # Identify which form was submitted
        action = request.POST.get('action')

        if action == 'update_profile':
            profileform = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
            if profileform.is_valid():
                profileform.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('profile_page')


        elif action == 'update_email':
            email_form = EmailChangeForm(request.POST, instance=request.user)
            if email_form.is_valid():
                email_form.save()
                messages.success(request, "Email updated successfully.")
                return redirect('profile_page')
            else:
                for error in email_form.errors.values():
                    messages.error(request, error)


        elif action == 'update_password':
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            print("Is valid:", password_form.is_valid())  # Debug
            print("Errors:", password_form.errors)        # Debug

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Prevents logout
                messages.success(request, "Password changed successfully.")
                return redirect('profile_page')
            else:
                for field, errors in password_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")

        elif action == 'add_work_experience':
            work_experience_form = WorkExperienceForm(request.POST)
            if work_experience_form.is_valid():
                work_experience = work_experience_form.save(commit=False)
                work_experience.user = request.user
                work_experience.save()
                messages.success(request, "Work experience added successfully.")
                return redirect('profile_page')

        elif action == 'add_education':
            education_form = EducationForm(request.POST)
            if education_form.is_valid():
                education = education_form.save(commit=False)
                education.user = request.user  # ✅ make sure your model has user = ForeignKey
                education.save()
                messages.success(request, "Education details added successfully.")
                return redirect('profile_page')
            else:
                for field, error_list in education_form.errors.items():
                    for error in error_list:
                        messages.error(request, f"{field}: {error}")

        elif action == 'add_project':
            project_form = ProjectForm(request.POST)
            if project_form.is_valid():
                project = project_form.save(commit=False)
                project.user = request.user
                project.save()
                messages.success(request, "Project added successfully.")
                return redirect('profile_page')
            else:
                for field, errors in project_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")

        elif action == 'update_privacy':
            privacy_instance = getattr(request.user, 'privacysettings', None)

            if privacy_instance:
                privacyform = PrivacySettingsForm(request.POST, instance=privacy_instance)
            else:
                privacyform = PrivacySettingsForm(request.POST)

            if privacyform.is_valid():
                privacy_settings = privacyform.save(commit=False)
                # Assign user manually if it's a new instance
                if not privacy_instance:
                    privacy_settings.user = request.user
                privacy_settings.save()
                messages.success(request, "Privacy settings updated successfully.")
                return redirect('profile_page')

        elif action == 'update_notifications':
            notification_instance = getattr(request.user, 'notificationsettings', None)

            if notification_instance:
                notificationform = NotificationSettingsForm(request.POST, instance=notification_instance)
            else:
                notificationform = NotificationSettingsForm(request.POST)

            if notificationform.is_valid():
                notification_settings = notificationform.save(commit=False)
                if not notification_instance:
                    notification_settings.user = request.user  # ⬅️ Important!
                notification_settings.save()
                messages.success(request, "Notification settings updated successfully.")
                return redirect('profile_page')
    else:
        for field, errors in notificationform.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")

    return render(request, 'profile_page.html', {
        'profileform': profileform,
        'notificationform': notificationform,
        'privacyform': privacyform,
        'payments': payments,
        'project_form': project_form,
        'email_form': email_form,
        'password_form': password_form,
        'work_experience_form': work_experience_form,
        'education_form': education_form,
        'profile': profile_image,
    })


def bundle_detail(request, bundle_id):
    bundle = get_object_or_404(Bundle, id=bundle_id)
    profile_image = None
    if request.user.is_authenticated:
        profile_data = get_object_or_404(Profile, user=request.user)
        profile_image = profile_data if profile_data.profile_picture else None

    return render(request, 'e_learning_plus.html', {'bundle': bundle, 'profile': profile_image})


def referral_progress(request):
    return render(request, 'referral_progress.html')


def tech_courses(request):
    tech_courses = Course.objects.filter(category_type='c1')
    courses = Course.objects.all()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():

            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                # Redirect based on user type
                if user.user_type == 1:
                    return redirect('admin_begin_class_dashboard_container')
                elif user.user_type == 2:
                    return redirect('my_learnings')
                elif user.user_type == 3:
                    return redirect('course_provider/index')
                else:
                    messages.error(request, "Invalid login credentials.")
                    return redirect('landing_page_before_login')
            else:
                messages.error(request, "Invalid Login!")
    else:
        form = LoginForm()

    if request.method == 'POST':
        studnetform = AdminForm(request.POST)
        if studnetform.is_valid():
            user_email = studnetform.cleaned_data['EmailID']

            # Check if the email already exists
            if get_user_model().objects.filter(email=user_email).exists():
                messages.error(request, 'This email is already in use.')
                return redirect('landing_page_before_login')  # Redirect back to the signup page

            # Create a new user instance
            user = get_user_model().objects.create_user(
                email=user_email,
                password=studnetform.cleaned_data['password1'],
                username=user_email,  # You can set username as email if you want
                user_type=2
            )
            # Generate a random OTP and send it to the user's email
            otp = generate_otp()

            # Send the OTP to the user's email
            send_otp(user_email, otp)

            # Save the OTP in the session
            request.session['otp'] = otp
            request.session['email'] = user_email

            return redirect('verify_otp')
    else:
        studnetform = AdminForm()

    return render(request, 'tech_courses.html',
                  {'courses': courses, 'tech_courses': tech_courses, 'form': form, 'studnetform': studnetform})


def ncert_courses(request):
    return render(request, 'ncert_courses.html')


def question_papers(request):
    return render(request, 'question_papers.html')


def grade_wise_courses(request):
    return render(request, 'grade_wise_courses.html')


def roadmap(request):
    return render(request, 'roadmap.html')


def blog_details(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    profile_image = None
    if request.user.is_authenticated:
        profile_data = Profile.objects.filter(user=request.user).first()  # Fetch profile if exists
        if profile_data and profile_data.profile_picture:
            profile_image = profile_data
        else:
            profile_image = None
    comments = post.comments.all().order_by('-created_at')

    if request.method == 'POST':
        comment_form = BlogCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('blog_details', post_id=post.id)
    else:
        comment_form = BlogCommentForm()

    categories = BlogPost.CATEGORY_CHOICES
    posts = BlogPost.objects.all().order_by('-published_at')
    all_tags = set()
    for blog_post in BlogPost.objects.all():
        if blog_post.tags:
            tags_list = [t.strip() for t in blog_post.tags.split(',')]
            all_tags.update(tags_list)

    return render(request, 'blog_details.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'categories': categories,
        'all_posts': posts,
        'all_tags': sorted(all_tags),
        'profile': profile_image,
    })


def blog(request):
    category = request.GET.get('category')
    tag = request.GET.get('tag')

    if category:
        posts = BlogPost.objects.filter(category=category).order_by('-published_at')
    else:
        posts = BlogPost.objects.all().order_by('-published_at')

    if tag:
        posts = posts.filter(tags__icontains=tag)

    # Get all unique tags
    all_tags = set()
    for post in BlogPost.objects.all():
        if post.tags:
            tags_list = [t.strip() for t in post.tags.split(',')]
            all_tags.update(tags_list)

    categories = BlogPost.CATEGORY_CHOICES
    all_posts = BlogPost.objects.all().order_by('-published_at')

    profile_image = None
    if request.user.is_authenticated:
        profile_data = Profile.objects.filter(user=request.user).first()  # Fetch profile if exists
        if profile_data and profile_data.profile_picture:
            profile_image = profile_data
        else:
            profile_image = None

    return render(request, 'blog.html', {
        'posts': posts,
        'categories': categories,
        'all_tags': sorted(all_tags),
        'selected_category': category,
        'selected_tag': tag,
        'all_posts': all_posts,
        'profile': profile_image,
    })


def faq(request):
    courses = Course.objects.all()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():

            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('landing_page_before_login')
                # user_type = user.user_type
                # if user_type == 1:  # Assuming user_type is an integer field
                #     return redirect('admin')
                # elif user_type == 2:
                #     return redirect('course_catalog')
                # elif user_type == 3:
                #     return HttpResponse('course provider')
                # else:
                #     messages.error(request, "Invalid Login!")
            else:
                messages.error(request, "Invalid Login!")
    else:
        form = LoginForm()

    if request.method == 'POST':
        studnetform = AdminForm(request.POST)
        if studnetform.is_valid():
            user_email = studnetform.cleaned_data['EmailID']

            # Check if the email already exists
            if get_user_model().objects.filter(email=user_email).exists():
                messages.error(request, 'This email is already in use.')
                return redirect('landing_page_before_login')  # Redirect back to the signup page

            # Create a new user instance
            user = get_user_model().objects.create_user(
                email=user_email,
                password=studnetform.cleaned_data['password1'],
                username=user_email,  # You can set username as email if you want
                user_type=2
            )
            # Generate a random OTP and send it to the user's email
            otp = generate_otp()

            # Send the OTP to the user's email
            send_otp(user_email, otp)

            # Save the OTP in the session
            request.session['otp'] = otp
            request.session['email'] = user_email

            return redirect('verify_otp')
    else:
        studnetform = AdminForm()

    profile_image = []
    if request.user.is_authenticated:
        profile_data = get_object_or_404(Profile, user=request.user)
    if request.user.is_authenticated:
        if profile_data.profile_picture:
            profile_image = get_object_or_404(Profile, user=request.user)
        else:
            profile_image = 10
    return render(request, 'faq.html',
                  {'courses': courses, 'form': form, 'studnetform': studnetform, 'profile': profile_image})


def chat_box(request):
    if request.method == 'POST':
        reason = request.POST.get('reason')
        description = request.POST.get('description')
        attachment = request.FILES.get('attachment')

        Ticket.objects.create(
            user=request.user,
            reason=reason,
            description=description,
            attachment=attachment
        )
        return redirect('support')

    profile_image = None
    if request.user.is_authenticated:
        profile_data = Profile.objects.filter(user=request.user).first()
        profile_image = profile_data.profile_picture if profile_data and profile_data.profile_picture else None

    tickets = Ticket.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'chat_box.html', {'tickets': tickets, 'profile': profile_image})


def do_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():

            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                user_type = user.user_type
                if user_type == 1:  # Assuming user_type is an integer field
                    return redirect('admin')
                elif user_type == 2:
                    return redirect('course_catalog')
                elif user_type == 3:
                    return HttpResponse('course provider')
                else:
                    messages.error(request, "Invalid Login!")
            else:
                messages.error(request, "Invalid Login!")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


@login_required
def notification_settings(request):
    try:
        settings = NotificationSettings.objects.get(user=request.user)
    except NotificationSettings.DoesNotExist:
        settings = NotificationSettings(user=request.user)

    if request.method == 'POST':
        form = NotificationSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            return redirect('update_profile')
    else:
        form = NotificationSettingsForm(instance=settings)

    return render(request, 'notification_settings.html', {'form': form})


def generate_otp():
    return random.randint(100000, 999999)


def send_otp(email, otp):
    send_mail(
        'Email Verification OTP',
        f'Your OTP is: {otp}',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )


def student_signup(request):
    if request.method == 'POST':
        form = AdminForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['EmailID']

            # Check if the email already exists
            if get_user_model().objects.filter(email=user_email).exists():
                messages.error(request, 'This email is already in use.')
                return redirect('student-signup')  # Redirect back to the signup page

            # Create a new user instance
            user = get_user_model().objects.create_user(
                email=user_email,
                password=form.cleaned_data['password1'],
                username=user_email,  # You can set username as email if you want
                user_type=2
            )
            # Generate a random OTP and send it to the user's email
            otp = generate_otp()

            # Send the OTP to the user's email
            send_otp(user_email, otp)

            # Save the OTP in the session
            request.session['otp'] = otp
            request.session['email'] = user_email

            return redirect('verify_otp')
    else:
        form = AdminForm()

    return render(request, 'student_signup.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('landing_page_before_login')


def watch_topic(request, course_id, topic_id):
    user = request.user.student
    course = get_object_or_404(Course, id=course_id)
    topic = get_object_or_404(Topic, id=topic_id)

    topic.watched_by_users.add(user)

    weeks = Week.objects.filter(course=course).prefetch_related('topics')

    all_topics = Topic.objects.filter(week__course=course)  # Fetch all topics related to the course

    return render(request, 'watch_topic.html', {
        'course': course,
        'weeks': weeks,
        'current_topic': topic,
        'all_topics': all_topics  # Pass all topics to the template
    })


@login_required
def privacy_settings(request):
    try:
        privacy_settings = request.user.privacysettings
    except PrivacySettings.DoesNotExist:
        privacy_settings = PrivacySettings(user=request.user)

    if request.method == 'POST':
        form = PrivacySettingsForm(request.POST, instance=privacy_settings)
        if form.is_valid():
            form.save()
            return redirect('update_profile')
    else:
        form = PrivacySettingsForm(instance=privacy_settings)

    return render(request, 'privacy_settings.html', {'form': form})


@login_required
def view_cart(request):
    cart_courses = request.user.student.cart.all()
    return render(request, 'view_cart.html', {'cart_courses': cart_courses})


@login_required
def add_to_cart(request, course_id):
    course = Course.objects.get(id=course_id)
    # Check if the course is already in the user's cart
    if course in request.user.student.cart.all():
        messages.info(request, "This course is already in your cart.")
    else:
        request.user.student.cart.add(course)
        messages.success(request, "Course added to cart successfully.")
    return redirect('cart')


def remove_from_cart(request, course_id):
    if request.method == 'POST':
        if request.user.is_authenticated:  # Ensure the user is authenticated
            student = request.user.student
            try:
                course = Course.objects.get(pk=course_id)  # Fetch the course by ID
                if student.cart.filter(pk=course_id).exists():
                    student.cart.remove(course)  # Remove the course from the cart
            except Course.DoesNotExist:
                # Handle the case where the course doesn't exist
                return redirect('cart')
            return redirect('cart')  # Redirect to the cart page after removal
    return redirect('cart')


@login_required
def add_to_wishlist(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        student = request.user.student
        student.wishlist.add(course)  # Assuming 'wishlist' is the name of the ManyToManyField in the Student model
        return redirect('courses', course_id=course_id)
    else:
        return redirect('course')  # Redirect to course catalog if not a POST request


def wishlist(request):
    student = request.user.student
    wishlist_courses = student.wishlist.all()
    return render(request, 'wishlist.html', {'wishlist_courses': wishlist_courses})


def remove_from_wishlist(request, course_id):
    student = request.user.student
    course = student.wishlist.get(id=course_id)
    student.wishlist.remove(course)
    return redirect('my_learnings')


def support(request):
    if request.method == 'POST':
        reason = request.POST.get('reason')
        description = request.POST.get('description')
        attachment = request.FILES.get('attachment')

        Ticket.objects.create(
            user=request.user,
            reason=reason,
            description=description,
            attachment=attachment
        )
        return redirect('support')

    tickets = Ticket.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'support.html', {'tickets': tickets})


@login_required
def update_profile(request):
    # Ensure the user has a profile
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('update_profile')  # Redirect to update profile page after successful update
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'update_profile.html', {'form': form})


def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        if entered_otp == str(stored_otp):
            # OTP verification successful
            email = request.session.get('email')
            Full_Name = request.POST.get('Full_Name')

            # Create a student profile
            user = get_user_model().objects.get(email=email)
            student_profile = Student.objects.create(user=user,
                                                     EmailID=user.email)
            # Redirect to a success page
            return redirect('landing_page_before_login')

    # OTP verification failed or GET request
    return render(request, 'verify_otp.html')


def course_catalog(request):
    courses = Course.objects.all()
    return render(request, 'course_catalog.html', {'courses': courses})


def career_roadmap(request):
    courses = Course.objects.all()
    return render(request, 'career_roadmap.html', {'courses': courses})


def view_course_details(request, course_id):
    course = Course.objects.get(id=course_id)
    return render(request, 'view_course_details.html', {'course': course})


def start_course(request, course_id):
    course = Course.objects.get(id=course_id)
    return render(request, 'start_course.html', {'course': course})


def view_question_paper(request, pk):
    question_paper = get_object_or_404(QuestionPaper, pk=pk)
    return FileResponse(question_paper.file.open(), content_type='application/pdf')


@login_required
def all_course_progress(request):
    student = Student.objects.get(user=request.user)
    enrollments = Enrollment.objects.filter(user=student)

    course_progress_data = []

    for enrollment in enrollments:
        course = enrollment.course
        total_topics = sum(week.topics.count() for week in course.weeks.all())
        watched_topics = sum(
            topic.watched_by_users.filter(id=student.id).exists() for week in course.weeks.all() for topic in
            week.topics.all())

        if total_topics > 0:
            progress_percentage = round((watched_topics / total_topics) * 100)
        else:
            progress_percentage = 0

        course_progress_data.append({
            'course': course,
            'total_topics': total_topics,
            'watched_topics': watched_topics,
            'progress_percentage': progress_percentage,
        })

    filter_status = request.GET.get('status', 'in_progress')
    if filter_status == 'completed':
        filtered_courses = [data for data in course_progress_data if data['progress_percentage'] == 100]
    else:
        filtered_courses = [data for data in course_progress_data if data['progress_percentage'] < 100]

    context = {
        'course_progress_data': filtered_courses,
        'filter_status': filter_status,
    }

    return render(request, 'my_courses.html', context)


def download_question_paper(request, pk):
    question_paper = get_object_or_404(QuestionPaper, pk=pk)
    response = FileResponse(question_paper.file.open(), content_type='application/pdf')
    response[
        'Content-Disposition'] = f'attachment; filename="{question_paper.grade}th - {question_paper.subject}({question_paper.year}).pdf"'
    return response


@login_required
def enroll_course(request, course_id):
    if request.method == 'POST':
        # Create a new enrollment record for the current user and course
        Enrollment.objects.create(course_id=course_id, user=request.user)
        # Redirect to the enrolled course page
        return redirect('enrolled_course')
    else:
        # If the request method is not POST, redirect to the course details page
        return redirect('view_course_details', course_id=course_id)


@login_required
def enrolled_course(request):
    try:
        # Retrieve the Admin instance associated with the current user
        admin_user = Student.objects.get(user=request.user)
        # Retrieve enrolled courses for the admin user
        enrolled_courses = Enrollment.objects.filter(user=admin_user)
        enrolled = Enrollment.objects.all()
        print(enrolled)
    except Student.DoesNotExist:
        # Handle the case where the user is not an admin
        enrolled_courses = []

    return render(request, 'enrolled_course.html', {'enrolled_courses': enrolled})


def course_payment(request, course_id):
    currency = 'INR'
    amount = 20000  # Rs. 200

    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='0'))

    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = 'paymenthandler/'

    # we need to pass these details to frontend.
    context = {}
    context['course_id'] = course_id
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url
    return render(request, 'course_payment.html', context)


def previous_question_papers(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    question_paper = QuestionPaper.objects.filter(course=course).first()

    if question_paper:
        # Assuming there's only one question paper per course for simplicity
        file_path = question_paper.file.path
        # Open the file and serve it as a download response
        response = FileResponse(open(file_path, 'rb'))
        # Set the content type header to force the browser to download the file
        response['Content-Disposition'] = f'attachment; filename="{question_paper.title}.pdf"'
        return response
    else:
        # Handle the case where no question paper is found
        return HttpResponse("No question paper found for this course.", status=404)


# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))


def homepage(request):
    currency = 'INR'
    amount = 20000  # Rs. 200

    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='0'))

    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = 'paymenthandler/'

    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url

    return render(request, 'mentorship_page.html', context=context)


def get_discussions(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    discussions = course.discussions.all().order_by('-created_at')
    discussions_data = [{
        'title': discussion.title,
        'content': discussion.content,
        'created_at': discussion.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for discussion in discussions]
    return JsonResponse({'status': 'success', 'discussions': discussions_data})


@login_required
def blog_update(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog_detail', post_id=post.id)
    else:
        form = BlogPostForm(instance=post)
    return render(request, 'blog_form.html', {'form': form})


def blog_list(request):
    posts = BlogPost.objects.all().order_by('-published_at')
    return render(request, 'blog_list.html', {'posts': posts})


@login_required
def blog_create(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect('blog_list')
    else:
        form = BlogPostForm()
    return render(request, 'blog_form.html', {'form': form})


def get_messages(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    course_messages = Message.objects.filter(course=course)
    context = {
        'course': course,
        'course_messages': course_messages,
    }
    return render(request, 'start_course.html', context)


def get_course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    weeks = Week.objects.filter(course=course)
    context = {
        'course': course,
        'weeks': weeks,
    }
    return render(request, 'course_details.html', context)


def get_course_career_guidance_json(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    guidance_messages = CareerGuidanceMessage.objects.filter(course=course).values('content')
    return JsonResponse({'guidance_messages': list(guidance_messages)})


def get_course_messages_json(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    course_messages = Message.objects.filter(course=course).values('content')
    return JsonResponse({'messages': list(course_messages)})


def get_career_guidance(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    course_career_guidance = CareerGuidanceMessage.objects.filter(course=course)
    context = {
        'course': course,
        'career_guidance': course_career_guidance,
    }
    return render(request, 'start_course.html', context)


def get_course_resources_json(request, course_id):
    course = Course.objects.get(pk=course_id)
    weeks = Week.objects.filter(course=course).order_by('number')  # Ensure weeks are ordered correctly
    resources_data = []
    for week in weeks:
        resources = Resource.objects.filter(week=week)
        resources_list = [{'title': resource.title, 'pdf_file': resource.pdf_file.url} for resource in resources]
        resources_data.append({'week_title': week.title, 'resources': resources_list})
    return JsonResponse({'weeks': resources_data})


@login_required
def blog_delete(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    if request.method == 'POST':
        if post.author == request.user:
            post.delete()
        return redirect('blog_list')
    return render(request, 'blog_confirm_delete.html', {'post': post})


@csrf_exempt
@login_required
def add_note(request, course_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        course = get_object_or_404(Course, id=course_id)
        student = get_object_or_404(Student, user=request.user)
        note = Note.objects.create(course=course, student=student, content=content)
        return JsonResponse({'status': 'success', 'note': {'content': note.content, 'created_at': note.created_at}})
    return JsonResponse({'status': 'error'}, status=400)


@csrf_exempt
def add_discussion(request, course_id):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        course = get_object_or_404(Course, id=course_id)
        discussion = Discussion.objects.create(
            course=course,
            title=title,
            content=content,
            created_at=timezone.now()
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


# we need to csrf_exempt this url as
# POST request will be made by Razorpay
# and it won't have the csrf token.
@csrf_exempt
def paymenthandler(request):
    # only accept POST request.
    if request.method == "POST":
        try:

            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is not None:
                amount = 20000  # Rs. 200
                try:

                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)

                    # render success page on successful caputre of payment
                    return render(request, 'paymentsuccess.html')
                except:

                    # if there is an error while capturing payment.
                    return render(request, 'paymentfail.html')
            else:

                # if signature verification fails.
                return render(request, 'paymentfail.html')
        except:

            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
        # if other than POST request is made.
        return HttpResponseBadRequest()


def mentorship_form(request):
    if request.method == 'POST':
        # Retrieve form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        reason = request.POST.get('reason')

        # Perform any necessary validation

        # Assuming you have a MentorshipRequest model
        # Create a new mentorship request object
        mentorship_request = MentorshipRequest.objects.create(
            name=name,
            email=email,
            phone=phone,
            reason=reason
        )

        # Perform any additional actions like sending email notification, etc.

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})


def create_post(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    weeks = Week.objects.filter(course=course).prefetch_related('topics')
    context = {
        'course': course,
        'weeks': weeks,
    }
    return render(request, 'create_post.html', context)


@login_required
def community_platform(request):
    # Retrieve all posts for display
    posts = Post.objects.all()
    profile_image = []
    if request.user.is_authenticated:
        profile_data = get_object_or_404(Profile, user=request.user)
    if request.user.is_authenticated:
        if profile_data.profile_picture:
            profile_image = get_object_or_404(Profile, user=request.user)
        else:
            profile_image = 10
    return render(request, 'community_platform.html', {'posts': posts, 'profile': profile_image})


@login_required
def add_education(request):
    education_form = EducationForm()
    if request.method == 'POST':
        education_form = EducationForm(request.POST)
        if education_form.is_valid():
            education = education_form.save(commit=False)
            education.user = request.user
            education.save()
            return redirect('educational_details')
    return render(request, 'add_education.html', {'education_form': education_form})


@login_required
def account_security(request):
    if request.method == 'POST':
        email_form = EmailChangeForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)
        if email_form.is_valid():
            email_form.save()
            return redirect('update_profile')
        elif password_form.is_valid():
            password_form.save()
            # Update the session to prevent users from being logged out after changing password
            update_session_auth_hash(request, request.user)
            # Redirect to update profile page after successful update
            return redirect('update_profile')
    else:
        email_form = EmailChangeForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)
    return render(request, 'account_security.html', {'email_form': email_form, 'password_form': password_form})


@login_required
def educational_details(request):
    return render(request, 'educational_details.html')


@login_required
def add_work_experience(request):
    work_experience_form = WorkExperienceForm()
    if request.method == 'POST':
        work_experience_form = WorkExperienceForm(request.POST)
        if work_experience_form.is_valid():
            work_experience = work_experience_form.save(commit=False)
            work_experience.user = request.user
            work_experience.save()
            messages.success(request, 'Work experience has been added successfully.')
            return redirect('educational_details')
    return render(request, 'add_work_experience.html', {'work_experience_form': work_experience_form})


@login_required
def add_project(request):
    project_form = ProjectForm()
    if request.method == 'POST':
        project_form = ProjectForm(request.POST)
        if project_form.is_valid():
            project = project_form.save(commit=False)
            project.user = request.user
            project.save()
            return redirect('educational_details')
    return render(request, 'add_project.html', {'project_form': project_form})


@login_required
def add_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        user = request.user.student  # Get the Student instance associated with the logged-in user
        post = Post.objects.create(user=user, content=content)
        return redirect('community_platform')
    return render(request, 'add_post.html')


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        user = request.user.student  # Get the Student instance associated with the logged-in user
        comment = Comment.objects.create(post=post, user=user, content=content)
        return redirect('community_platform')
    return render(request, 'add_comment.html', {'post': post})


def like_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.likes += 1
    post.save()
    return JsonResponse({'likes': post.likes})


def dislike_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.dislikes += 1
    post.save()
    return JsonResponse({'dislikes': post.dislikes})


def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.likes += 1
    comment.save()
    return JsonResponse({'likes': comment.likes})


def dislike_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.dislikes += 1
    comment.save()
    return JsonResponse({'dislikes': comment.dislikes})


@login_required
def get_notes(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    student = get_object_or_404(Student, user=request.user)
    notes = Note.objects.filter(course=course, student=student).values('content', 'created_at')

    # Render the HTML template and pass notes data as context
    return render(request, 'start_course.html', {'notes': notes})


@login_required
def save_note(request, course_id):
    if request.method == 'POST':
        try:
            course = Course.objects.get(id=course_id)
            student = Student.objects.get(user=request.user)
            data = json.loads(request.body)
            content = data.get('content')

            if content:
                note = Note.objects.create(course=course, student=student, content=content)
                return JsonResponse({'status': 'success', 'note_id': note.id})
            else:
                return JsonResponse({'status': 'error', 'message': 'Content is required'})
        except Course.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Course not found'})
        except Student.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Student not found'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@login_required
def weekly_platform(request, week_number):
    week_posts = WeekPost.objects.filter(week_number=week_number)
    profile_image = []
    if request.user.is_authenticated:
        profile_data = get_object_or_404(Profile, user=request.user)
    if request.user.is_authenticated:
        if profile_data.profile_picture:
            profile_image = get_object_or_404(Profile, user=request.user)
        else:
            profile_image = 10
    return render(request, 'weekly_platform.html', {
        'week_posts': week_posts,
        'week_number': week_number,
        'profile': profile_image,
    })


@login_required
def add_week_post(request, week_number):
    if request.method == 'POST':
        content = request.POST.get('content')
        user = request.user.student
        week_post = WeekPost.objects.create(user=user, content=content, week_number=week_number)

        return redirect('weekly_platform', week_number=week_number)
    return render(request, 'weekly_platform..html', {'week_number': week_number})


@login_required
def add_week_comment(request, week_number, week_post_id):
    week_post = get_object_or_404(WeekPost, pk=week_post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        user = request.user.student
        comment = WeekComment.objects.create(week_post=week_post, user=user, content=content)
        return redirect('weekly_platform', week_number=week_number)
    return render(request, 'add_week_comment.html', {'week_post': week_post, 'week_number': week_number})


def like_week_post(request, week_post_id):
    week_post = get_object_or_404(WeekPost, pk=week_post_id)
    week_post.likes += 1
    week_post.save()
    return JsonResponse({'likes': week_post.likes})


def dislike_week_post(request, week_post_id):
    week_post = get_object_or_404(WeekPost, pk=week_post_id)
    week_post.dislikes += 1
    week_post.save()
    return JsonResponse({'dislikes': week_post.dislikes})


def like_week_comment(request, week_comment_id):
    week_comment = get_object_or_404(WeekComment, pk=week_comment_id)
    week_comment.likes += 1
    week_comment.save()
    return JsonResponse({'likes': week_comment.likes})


def dislike_week_comment(request, week_comment_id):
    week_comment = get_object_or_404(WeekComment, pk=week_comment_id)
    week_comment.dislikes += 1
    week_comment.save()
    return JsonResponse({'dislikes': week_comment.dislikes})


##############################################################################################################################################################################################################
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# COURSE PROVIDER VIEWS
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##############################################################################################################################################################################################################


from django.shortcuts import redirect, render, get_object_or_404
from app.forms import *
from app.models import *


def BASE_CP(request):
    uploaded_courses = CourseByProvider.objects.all()
    return render(request, 'base_cp.html', {'uploaded_courses': uploaded_courses})


# def upload_course(request):
#     if request.method == 'POST':
#         # Get form data
#         course_code = request.POST['course_code']
#         course_title = request.POST['course_title']
#         course_description = request.POST['course_description']
#         course_category = request.POST['course_category']
#         course_duration = request.POST['course_duration']
#         course_level = request.POST['course_level']
#         course_price = request.POST['course_price']
#         course_image = request.FILES['course_image']
#         course_video = request.FILES['course_video']
#         course_quizzes = request.FILES.getlist('course_quizzes')
#         course_assignments = request.FILES.getlist('course_assignments')
#         course_materials = request.FILES.getlist('course_materials')

#         # Save course to database
#         course = Course.objects.create(
#             code=course_code,
#             title=course_title,
#             description=course_description,
#             category=course_category,
#             duration=course_duration,
#             level=course_level,
#             price=course_price,
#             image=course_image,
#             video=course_video
#         )
#         for material in course_materials:
#             course.materials.create(file=material)
#         for quiz in course_quizzes:
#             course.quizzes.create(file=quiz)
#         for assignment in course_assignments:
#             course.assignments.create(file=assignment)

#         # Redirect to My Courses page
#         return redirect('base')
#     else:
#         uploaded_courses = Course.objects.all()
#         return render(request, 'upload_course.html', {'uploaded_courses': uploaded_courses})

def upload_course_CP(request):
    if request.method == 'POST':
        # Get form data
        course_code = request.POST['course_code']
        course_title = request.POST['course_title']
        course_description = request.POST['course_description']
        course_category = request.POST['course_category']
        course_duration = request.POST['course_duration']
        course_level = request.POST['course_level']
        course_price = request.POST['course_price']
        course_image = request.FILES['course_image_by_provider']
        course_videos = request.FILES.getlist('course_videos_by_provider')
        course_quizzes = request.FILES.getlist('course_quizzes_by_provider')
        course_assignments = request.FILES.getlist('course_assignments_by_provider')
        course_materials = request.FILES.getlist('course_materials_by_provider')

        # Save course to database
        course = CourseByProvider.objects.create(
            code=course_code,
            title=course_title,
            description=course_description,
            category=course_category,
            duration=course_duration,
            level=course_level,
            price=course_price,
            image=course_image,
        )
        for video in course_videos:
            CourseVideoByProvider.objects.create(course=course, video=video)
        for material in course_materials:
            MaterialByProvider.objects.create(course=course, file=material)
        for quiz in course_quizzes:
            QuizByProvider.objects.create(course=course, file=quiz)
        for assignment in course_assignments:
            AssignmentByProvider.objects.create(course=course, file=assignment)

        # Redirect to My Courses page
        return redirect('base_cp')
    else:
        uploaded_courses = CourseByProvider.objects.all()
        return render(request, 'upload_course_cp.html', {'uploaded_courses': uploaded_courses})


def course_detail_CP(request, pk):
    course = get_object_or_404(CourseByProvider, pk=pk)
    return render(request, 'course_detail_cp.html', {'course': course})


def course_overview_CP(request, pk):
    course = get_object_or_404(CourseByProvider, pk=pk)
    return render(request, 'course_overview_cp.html', {'course': course})


def delete_course_CP(request):
    if request.method == 'POST':
        course_id = request.POST.get('course_id')  # Assuming you pass the course ID via POST request
        course = get_object_or_404(CourseByProvider, pk=course_id)
        course.delete()
        return redirect('base_cp')  # Redirect to base or any other page
    return redirect('base_cp')  # Redirect to base if request method is not POST


def quiz_detail_CP(request, course_id):
    course = CourseByProvider.objects.get(id=course_id)
    student_count = course.students.count()
    quiz_results = QuizResult.objects.filter(quiz__course=course)
    # You can manipulate quiz_results as needed to display
    # the quiz results for each student
    return render(request, 'quiz_detail_cp.html',
                  {'course': course, 'student_count': student_count, 'quiz_results': quiz_results})


def assign_quiz_CP(request):
    if request.method == 'POST':
        form = AssignQuizForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course']
            quiz = form.cleaned_data['quiz']
            students = course.students.all()  # Get all students in the selected course

            # Assign the quiz to each student
            for student in students:
                QuizResult.objects.create(student=student, quiz=quiz, score=0.0)  # Default score is 0.0

            return redirect('quiz_detail_cp', course_id=course.id)
    else:
        form = AssignQuizForm()

    return render(request, 'assign_quiz_cp.html', {'form': form})


def upload_result_CP(request):
    if request.method == 'POST':
        form = ResultForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'upload_success_cp.html')
    else:
        form = ResultForm()
    return render(request, 'upload_result_cp.html', {'form': form})


def upload_assignment_result_CP(request):
    if request.method == 'POST':
        form = AssignmentResultForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'upload_success_cp.html')
    else:
        form = AssignmentResultForm()
    return render(request, 'upload_assignment_result_cp.html', {'form': form})


def view_result_CP(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    results = ResultByProvider.objects.filter(student=student)
    assignment_results = AssignmentResultByProvider.objects.filter(student=student)
    return render(request, 'view_result_cp.html', {'student': student, 'results': results})


def student_results_CP(request):
    results = ResultByProvider.objects.all().select_related('student', 'quiz')
    assignment_results = AssignmentResultByProvider.objects.all().select_related('student', 'assignment')
    return render(request, 'student_results_cp.html', {'results': results, 'assignment_results': assignment_results})


def create_payout_statement_CP(request):
    if request.method == 'POST':
        form = PayoutStatementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('payout_statement_list_cp')
        else:
            print(form.errors)
    else:
        form = PayoutStatementForm()
    return render(request, 'create_payout_statement_cp.html', {'form': form})


def payout_statement_list_CP(request):
    payouts = PayoutStatementByProvider.objects.all()
    return render(request, 'payout_statement_list_cp.html', {'payouts': payouts})

def course_provider_verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        if entered_otp == str(stored_otp):
            # OTP verification successful
            email = request.session.get('email')

            # Create a student profile
            user = get_user_model().objects.get(email=email)
            course_provider = Admin_CourseProvider.objects.create(user=user,
                                                      email=user.email)
            # Redirect to a success page
            return redirect('provider_index')

    # OTP verification failed or GET request
    return render(request, 'registration/otp_cp.html')


def provider_login_CP(request):
    return render(request, 'provider_login_cp.html')


def index_CP(request):
    total_enrollment_count = Enrollment.objects.count()
    this_month_count = Enrollment.objects.filter(enrollment_date__month=now().month).count()
    current_month = Enrollment.objects.filter(enrollment_date__year=now().year,enrollment_date__month=now().month).count()
    total_course = Course.objects.filter(user=request.user).count()

    total_earnings = Admin_Payment.objects.aggregate(
        total=Sum('amount_paid', default=0)
    )['total'] or 0
    this_month_earnings = Admin_Payment.objects.filter(
        date_of_payment__month=now().month
    ).aggregate(total=Sum('amount_paid', default=0))['total'] or 0
    assignment = AssignmentByProvider.objects.all()

    course = Course.objects.filter(user=request.user)
    payment = Admin_Payment.objects.filter(course__in=course)

    profile_image = None  # Default value for profile_image
    if request.user.is_authenticated:
        try:
            profile_data = Profile.objects.get(user=request.user)
            if profile_data.profile_picture:
                profile_image = profile_data
            else:
                profile_image = 10
        except Profile.DoesNotExist:
            profile_image = 10

    return render(request, 'index_cp.html',{'total_enrollment_count' : total_enrollment_count,
                 'this_month_count': this_month_count,
                 'current_month': current_month,
                 'total_course':total_course,
                 'total_earnings':total_earnings,
                 'this_month_earnings':this_month_earnings,
                 'assignment':assignment,
                 'payment_list':payment,
                 'profile':profile_image,})


def profile_CP(request):
    profile_image = None  # Default value for profile_image
    if request.user.is_authenticated:
        try:
            profile_data = Profile.objects.get(user=request.user)
            if profile_data.profile_picture:
                profile_image = profile_data
            else:
                profile_image = 10
        except Profile.DoesNotExist:
            profile_image = 10
    return render(request, 'profile_cp.html',{
        'profile':profile_image,
    })


def course_CP(request):
    uploaded_courses = Course.objects.filter(user=request.user)
    total_enrollment_count = Enrollment.objects.count()
    this_month_count = Enrollment.objects.filter(enrollment_date__month=now().month).count()
    current_month = Enrollment.objects.filter(enrollment_date__year=now().year,enrollment_date__month=now().month).count()
    total_course = Course.objects.filter(user=request.user).count()

    total_earnings = Admin_Payment.objects.aggregate(
        total=Sum('amount_paid', default=0)
    )['total'] or 0
    this_month_earnings = Admin_Payment.objects.filter(
        date_of_payment__month=now().month
    ).aggregate(total=Sum('amount_paid', default=0))['total'] or 0

    profile_image = None  # Default value for profile_image
    if request.user.is_authenticated:
        try:
            profile_data = Profile.objects.get(user=request.user)
            if profile_data.profile_picture:
                profile_image = profile_data
            else:
                profile_image = 10
        except Profile.DoesNotExist:
            profile_image = 10  # Default

    return render(request, 'course_cp.html',{'uploaded_courses': uploaded_courses,
                 'total_enrollment_count' : total_enrollment_count,
                 'this_month_count': this_month_count,
                 'current_month': current_month,
                 'total_course':total_course,
                 'total_earnings':total_earnings,
                 'this_month_earnings':this_month_earnings,
                 'profile':profile_image})


def payout_statement_CP(request):
    data = Admin_Payment.objects.all()
    paid = data.filter(status='completed')
    upaid = data.filter(status='pending')
    profile_image = None  # Default value for profile_image
    if request.user.is_authenticated:
        try:
            profile_data = Profile.objects.get(user=request.user)
            if profile_data.profile_picture:
                profile_image = profile_data
            else:
                profile_image = 10
        except Profile.DoesNotExist:
            profile_image = 10  # Default profile image indicator
    return render(request, 'payout_statement_cp.html',
    { 'paid':paid,
    'unpaid':upaid,
    'profile':profile_image,})


def settings_CP(request):
    profile_image = None  # Default value for profile_image
    if request.user.is_authenticated:
        try:
            profile_data = Profile.objects.get(user=request.user)
            if profile_data.profile_picture:
                profile_image = profile_data
            else:
                profile_image = 10
        except Profile.DoesNotExist:
            profile_image = 10  # Default profile image indicator
    return render(request, 'settings_cp.html',{'profile':profile_image})


def course_detail_sub_CP(request, id):
    course = get_object_or_404(Course, pk=id)
    total_enrollment_count = Enrollment.objects.count()
    this_month_count = Enrollment.objects.filter(enrollment_date__month=now().month).count()
    current_month = Enrollment.objects.filter(enrollment_date__year=now().year,enrollment_date__month=now().month).count()
    total_course = Course.objects.filter(user=request.user).count()

    total_earnings = Admin_Payment.objects.aggregate(
        total=Sum('amount_paid', default=0)
    )['total'] or 0
    this_month_earnings = Admin_Payment.objects.filter(
        date_of_payment__month=now().month
    ).aggregate(total=Sum('amount_paid', default=0))['total'] or 0
    assignment = AssignmentByProvider.objects.all()

    cou = Course.objects.get(course_name=course.course_name)
    earning_list = Admin_Payment.objects.filter(course=cou)

    profile_image = None  # Default value for profile_image
    if request.user.is_authenticated:
        try:
            profile_data = Profile.objects.get(user=request.user)
            if profile_data.profile_picture:
                profile_image = profile_data
            else:
                profile_image = 10
        except Profile.DoesNotExist:
            profile_image = 10
    return render(request, 'course_detail_sub_cp.html',{'course': course,'total_enrollment_count' : total_enrollment_count,
                 'this_month_count': this_month_count,
                 'current_month': current_month,
                 'total_course':total_course,
                 'total_earnings':total_earnings,
                 'this_month_earnings':this_month_earnings,
                 'assignment':assignment,
                 'earning_list':earning_list,
                 'profile':profile_image,
                })


def assignment_result_CP(request,id):
    assignment_results = AssignmentResultByProvider.objects.all().select_related('student', 'assignment')
    course = get_object_or_404(Course, pk=id)
    profile_image = None  # Default value for profile_image
    if request.user.is_authenticated:
        try:
            profile_data = Profile.objects.get(user=request.user)
            if profile_data.profile_picture:
                profile_image = profile_data
            else:
                profile_image = 10
        except Profile.DoesNotExist:
            profile_image = 10  # Default

    return render(request, 'assignment_result_cp.html',
                  {'assignment_results': assignment_results,
                   'profile':profile_image,
                    'course':course,})


def quiz_result_CP(request,id):
    results = QuizResult.objects.all().select_related('student', 'quiz')
    course = get_object_or_404(Course, pk=id)
    profile_image = None  # Default value for profile_image
    if request.user.is_authenticated:
        try:
            profile_data = Profile.objects.get(user=request.user)
            if profile_data.profile_picture:
                profile_image = profile_data
            else:
                profile_image = 10
        except Profile.DoesNotExist:
            profile_image = 10  # Default

    return render(request, 'quiz_result_cp.html',
                   {'results': results,
                    'profile':profile_image,
                    'course':course,
                    })


##############################################################################################################################################################################################################
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ADMIN VIEWS
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##############################################################################################################################################################################################################


from django.db.models import Sum
from django.urls import reverse
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth import get_user_model
from .forms import *
import random
from django.core.mail import send_mail
from django.conf import settings
from .models import *
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
import json
from django.urls import reverse_lazy
from django.forms import modelformset_factory
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError

# Create your views here.

# ---------------------------------------------------------------------------
# Login view
# ---------------------------------------------------------------------------

'''
def admin_do_login(request):
    if request.method == 'POST':
        form = Admin_LoginForm(request.POST)
        if form.is_valid():

            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                user_type = user.user_type
                if user_type == 1:  # Assuming user_type is an integer field
                    return redirect('super-panel')
                elif user_type == 2:
                    return HttpResponse('student')
                elif user_type == 3:
                    return HttpResponse('course provider')
                else:
                    messages.error(request, "Invalid Login!")
            else:
                messages.error(request, "Invalid Login!")
    else:
        form = Admin_LoginForm()

    return render(request, 'admin_login.html', {'form': form})


def generate_otp():
    return random.randint(100000, 999999)


def send_otp(email, otp):
    send_mail(
        'Email Verification OTP',
        f'Your OTP is: {otp}',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )


def admin_admin_signup(request):
    if request.method == 'POST':
        form = Admin_AdminForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['EmailID']

            # Check if the email already exists
            if get_user_model().objects.filter(email=user_email).exists():
                messages.error(request, 'This email is already in use.')
                # Redirect back to the signup page
                return redirect('admin_admin-signup')

            # Create a new user instance
            user = get_user_model().objects.create_user(
                email=user_email,
                password=form.cleaned_data['password1'],
                username=user_email,  # You can set username as email if you want
                user_type=1  # Assuming 1 represents the admin user type
            )
            # Generate a random OTP and send it to the user's email
            otp = generate_otp()

            # Send the OTP to the user's email
            send_otp(user_email, otp)

            # Save the OTP in the session
            request.session['otp'] = otp
            request.session['email'] = user_email

            return redirect('admin_verify_otp')
    else:
        form = Admin_AdminForm()

    return render(request, 'admin_admin_signup.html', {'form': form})

'''
def admin_verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        if entered_otp == str(stored_otp):
            # OTP verification successful
            email = request.session.get('email')
            Full_Name = request.POST.get('Full_Name')

            # Create an admin profile
            user = get_user_model().objects.get(email=email)
            # Customize this as per your Admin model
            admin_profile = Admin_Admin.objects.create(
                user=user, Full_Name=user.email)

            # Redirect to a success page
            return redirect('admin_begin_class_dashboard_container')

    # OTP verification failed or GET request
    return render(request, 'admin_otp.html')



@login_required
def admin_feedback_page(request):
    if request.method == 'POST':
        form = Admin_TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return JsonResponse({'redirect': True, 'url': request.build_absolute_uri('admin_ticket_list')})
    else:
        form = Admin_TicketForm()
    tickets = Ticket.objects.all  # filter(user=request.user)
    chat_form = Admin_ChatMessageForm()
    return render(request, 'admin_feedback.html', {
        'tickets': tickets,
        'form': form,
        'chat_form': chat_form,
    })


# ------------------------------------------------------------------------------
# Course Views
# ------------------------------------------------------------------------------


def admin_create_course(request):
    if request.method == 'POST':
        print(request.FILES)
        form = Admin_CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course_instance = form.save(commit=False)
            if request.user.is_authenticated:
                course_instance.user = request.user
            else:
                return redirect('landing_page_before_login')
            # print(course_instance.image.path)  # Check image path
            # print(course_instance.video.path)  # Check video path

            if not course_instance.mentor:
                course_instance.mentor = Admin_Mentor.objects.first()
            if not course_instance.category:
                course_instance.category = Admin_CourseCategory.objects.first()
            if not course_instance.provider:
                course_instance.provider = Admin_CourseProvider.objects.first()

            try:
                course_instance.save()
                return redirect('admin_course_list')
            except IntegrityError as e:
                print(f"IntegrityError: {e}")
            return redirect('admin_course_list')
    else:
        form = Admin_CourseForm()
    return render(request, 'admin_create_course.html', {'form': form})


def admin_edit_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        form = Admin_CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('admin_course_list')  # Redirect to the list of courses
    else:
        form = Admin_CourseForm(instance=course)
    return render(request, 'admin_edit_course.html', {'form': form, 'course': course})


def admin_view_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, 'admin_course_detail.html', {'course': course})


def admin_course_list(request):
    courses = Course.objects.all()
    category_filter = request.GET.get('category')
    if category_filter:
        courses = courses.filter(category_type=category_filter)
    return render(request, 'admin_course_list.html', {'courses': courses})


def admin_Delete_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully.')
        return redirect('admin_course_list')
    return render(request, 'admin_delete_course.html', {'cours': course})


def admin_Super_panel(request):
    return render(request, 'admin_Super_panel.html')


def admin_content_management(request):
    return render(request, 'admin_content_management.html')


def admin_User_Management(request):
    return render(request, 'admin_user_management.html')


def admin_create_assignment(request, course_id):
    # Get the course object based on the provided course_id
    course = get_object_or_404(Course, pk=course_id)

    if request.method == 'POST':
        # If the request method is POST, process the form data
        form = Admin_AssignmentForm(request.POST)
        if form.is_valid():
            # If the form data is valid, save the assignment associated with the course
            assignment = form.save(commit=False)
            assignment.course = course
            assignment.save()
            # Redirect to the course detail page after successfully creating the assignment
            return redirect('admin_view_course', course_id=course_id)
    else:
        # If the request method is GET, render the assignment creation form
        form = Admin_AssignmentForm()

    # Render the create_assignment template with the form and course objects
    return render(request, 'admin_create_assignment.html', {'form': form, 'course': course})


def admin_edit_assignment(request, assignment_id):
    assignment = get_object_or_404(Admin_Assignment, pk=assignment_id)
    if request.method == 'POST':
        form = Admin_AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment updated successfully.')
            return redirect('admin_assignment_list')
    else:
        form = Admin_AssignmentForm(instance=assignment)
    return render(request, 'admin_edit_assignment.html', {'form': form, 'assignment': assignment})


def admin_assignment_list(request):
    assignments = Admin_Assignment.objects.all()
    return render(request, 'admin_assignment_list.html', {'assignments': assignments})


def admin_delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Admin_Assignment, pk=assignment_id)
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Assignment deleted successfully.')
        return redirect('admin_assignment_list')
    return render(request, 'admin_delete_assignment.html', {'assignment': assignment})


def admin_mark_assignment(request, assignment_id):
    assignment = get_object_or_404(Admin_StudentAssignment, pk=assignment_id)
    if request.method == 'POST':
        form = Admin_AssignmentSubmissionForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            # Redirect or display success message
    else:
        form = Admin_AssignmentSubmissionForm(instance=assignment)
    return render(request, 'admin_mark_assignment.html', {'form': form, 'assignment': assignment})


def admin_view_submissions(request):
    submissions = Admin_StudentAssignment.objects.all()
    return render(request, 'admin_view_submissions.html', {'submissions': submissions})


# --------------------------------------------------------------------------------
# Quiz view
# --------------------------------------------------------------------------------


def admin_create_quiz(request):
    if request.method == 'POST':
        form = Admin_QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save()
            # Redirect to add_question view with the newly created quiz_id
            return redirect(reverse('admin_add-question', kwargs={'quiz_id': quiz.id}))
    else:
        form = Admin_QuizForm()
    return render(request, 'admin_create_quiz.html', {'form': form})


def admin_quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Admin_Quiz, pk=quiz_id)
    questions = quiz.question_set.all()
    return render(request, 'admin_quiz_detail.html', {'quiz': quiz, 'questions': questions})


def admin_add_question(request, quiz_id):
    quiz = get_object_or_404(Admin_Quiz, pk=quiz_id)
    if request.method == 'POST':
        question_form = Admin_QuestionForm(request.POST)
        option_formset = OptionFormSet(request.POST)
        if question_form.is_valid() and option_formset.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz
            question.save()
            option_formset.instance = question
            option_formset.save()
            return redirect('admin_take-quiz', quiz_id=quiz_id)
    else:
        question_form = Admin_QuestionForm()
        option_formset = OptionFormSet()
    return render(request, 'admin_add_question.html',
                  {'quiz': quiz, 'question_form': question_form, 'option_formset': option_formset})


@login_required
def admin_take_quiz(request, quiz_id):
    quiz = get_object_or_404(Admin_Quiz, pk=quiz_id)
    questions = quiz.question_set.all()

    if request.method == 'POST':
        # Process form submissions
        for question in questions:
            form = Admin_AnswerForm(request.POST, prefix=str(
                question.id), instance=Admin_Answer(question=question))
            if form.is_valid():
                # Set the user_id field before saving
                answer = form.save(commit=False)
                answer.user_id = request.user.id
                answer.save()

        # Redirect to the quiz results page or any other appropriate page
        # Redirect to the create_quiz_result view with the quiz_id parameter
        return redirect('admin_create-quiz-result', quiz_id=quiz_id)

    else:
        # Render the quiz form with only the first four choices for each question
        formset = []
        for question in questions:
            choices = Admin_Choice.objects.filter(question=question)[
                      :4]  # Limit choices to first four
            answer_form = Admin_AnswerForm(prefix=str(
                question.id), instance=Admin_Answer(question=question))
            # Set queryset for choice field
            answer_form.fields['choice'].queryset = choices
            formset.append(answer_form)
        return render(request, 'admin_take_quiz.html', {'quiz': quiz, 'formset': formset})


def admin_create_quiz_result(request, quiz_id):
    if request.method == 'POST':
        form = Admin_QuizResultForm(request.POST)
        if form.is_valid():
            # Save the form with the quiz_id
            form.instance.quiz_id = quiz_id
            form.save()
            # Redirect to the quiz results page
            return redirect('admin_quiz-results', quiz_id=quiz_id)
    else:
        form = Admin_QuizResultForm()
    return render(request, 'admin_create_quiz_result.html', {'form': form})


def admin_quiz_list(request):
    quizzes = Admin_Quiz.objects.all()
    quiz_results = Admin_Quiz_Result.objects.filter(quiz__in=quizzes)
    return render(request, 'admin_quiz_list.html', {'quizzes': quizzes, 'quiz_results': quiz_results})


def admin_quiz_results(request, quiz_id):
    selected_quiz = get_object_or_404(Admin_Quiz, pk=quiz_id)
    selected_quiz_results = Admin_Quiz_Result.objects.filter(quiz=selected_quiz)
    return render(request, 'admin_quiz_detail.html',
                  {'selected_quiz': selected_quiz, 'selected_quiz_results': selected_quiz_results})


# View for submitting an assignment


def admin_submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Admin_Assignment, pk=assignment_id)
    if request.method == 'POST':
        form = Admin_AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()
            messages.success(request, 'Assignment submitted successfully.')
            return redirect('admin_assignment_list')
    else:
        form = Admin_AssignmentSubmissionForm()
    return render(request, 'admin_submit_assignment.html', {'form': form, 'assignment': assignment})


def admin_view_assignment_feedback(request, assignment_id):
    assignment = get_object_or_404(Admin_Assignment, pk=assignment_id)
    feedback = assignment.feedback.all()
    return render(request, 'admin_assignment_feedback.html', {'assignment': assignment, 'feedback': feedback})


def admin_list_students(request):
    students = CustomeUser.objects.filter(user_type=2)  # Filter students
    return render(request, 'admin_list_students.html', {'students': students})


def admin_add_student(request):
    if request.method == 'POST':
        # If the form is submitted, process the form data
        form = UserForm(request.POST)  # Unable to understand which form devs tried to link up
        if form.is_valid():
            form.save()
            return redirect('admin_list_students')
    else:
        # If it's a GET request, render the form
        form = UserForm()  # Unable to understand which form devs tried to link up

    return render(request, 'admin_add_student.html', {'form': form})


def admin_edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = Admin_StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully.')
            return redirect('admin_student-list')
    else:
        form = Admin_StudentForm(instance=student)
    return render(request, 'admin_edit_student.html', {'form': form, 'student': student})


def admin_suspend_student(request, student_id):
    # Fetch the student object and suspend the account
    student = CustomeUser.objects.get(pk=student_id)
    student.is_active = False
    student.save()
    return redirect('admin_list_students')


def admin_change_course(request, student_id):
    # Fetch the student object
    student = CustomeUser.objects.get(pk=student_id)
    if request.method == 'POST':
        # Process form data to change the course association
        # Update student.course or relevant field in CustomUser model
        # Redirect to list of students after course change
        return redirect('admin_list_students')
    else:
        # Render form for selecting desired course
        return render(request, 'admin_change_course.html',
                      {'student': student, 'courses': courses})  # courses is not mentioned here


def admin_ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)  # , user=request.user
    messages = Admin_ChatMessage.objects.filter(ticket=ticket)

    if request.method == 'POST':
        message_content = request.POST.get('message')
        if message_content:
            new_message = Admin_ChatMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                message=message_content
            )
            new_message.save()
        return redirect('admin_ticket_detail', ticket_id=ticket_id)

    return render(request, 'admin_ticket_detail.html', {
        'ticket': ticket,
        'messages': messages,
    })

    # ---------------------------------------------------------------------------------------


# Marketing and Promotions View
# ---------------------------------------------------------------------------------------


def admin_marketing_promotions(request):
    # Your logic for the Marketing and Promotions page goes here
    return render(request, 'admin_marketing_promotions.html')


def admin_track_clicks(request):
    # Your logic for the Marketing and Promotions page goes here
    return render(request, 'admin_track_clicks.html')


def admin_course_data(request):
    # Your logic for the Marketing and Promotions page goes here
    return render(request, 'admin_course_data.html')


def admin_referral_program(request):
    # Your logic for the Marketing and Promotions page goes here
    return render(request, 'admin_referral_program.html')


# ---------------------------------------------------------------------------------------
# Offers View
# ---------------------------------------------------------------------------------------

def admin_offers_view(request):
    return render(request, 'admin_offers.html')


def admin_create_voucher_view(request):
    if request.method == 'POST':
        form = Admin_VoucherForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect('admin_vouchers_list')
        else:
            return render(request, 'admin_create_voucher.html', {'form': form})

    else:
        form = Admin_VoucherForm()

        return render(request, 'admin_create_voucher.html', {'form': form})


# from django.db.models import Sum


def admin_affiliate_market_list(request):
    marketers = Admin_AffiliateMarketer.objects.all()
    return render(request, 'admin_affiliate_market_list.html', {'marketers': marketers})


def admin_affiliate_market_detail(request, marketer_id):
    marketer = get_object_or_404(Admin_AffiliateMarketer, pk=marketer_id)
    return render(request, 'admin_affiliate_detail.html', {'marketer': marketer})


def admin_affiliate_market_create(request):
    if request.method == 'POST':
        form = Admin_AffiliateMarketerForm(request.POST)

        if form.is_valid():
            #  Assign the current user to the form's user field
            form.instance.user = request.user
            form.save()
            return redirect('admin_affiliate_marketing_main_page')
        return render(request, 'admin_affiliate_market_create.html', {'form': form})
    else:
        form = Admin_AffiliateMarketerForm()

        return render(request, 'admin_affiliate_market_create.html', {'form': form})


def admin_affiliate_marketer_update(request, marketer_id):
    marketer = get_object_or_404(Admin_AffiliateMarketer, pk=marketer_id)
    if request.method == 'POST':
        form = Admin_AffiliateMarketerForm(request.POST, instance=marketer)
        if form.is_valid():
            form.save()
            marketers_active = Admin_AffiliateMarketer.objects.filter(is_frozen=False)
            marketers_suspend = Admin_AffiliateMarketer.objects.filter(is_frozen=True)
            return redirect('admin_affiliate_marketing_main_page')
    else:
        form = Admin_AffiliateMarketerForm(instance=marketer)
    return render(request, 'admin_affiliate_marketer_form.html', {'form': form})


def admin_affiliate_market_delete(request, marketer_id):
    marketer = get_object_or_404(Admin_AffiliateMarketer, pk=marketer_id)
    if request.method == 'POST':
        marketer.delete()
        marketers_active = Admin_AffiliateMarketer.objects.filter(is_frozen=False)
        marketers_suspend = Admin_AffiliateMarketer.objects.filter(is_frozen=True)
        return redirect('admin_affiliate_marketing_main_page')
    marketers_active = Admin_AffiliateMarketer.objects.filter(is_frozen=False)
    marketers_suspend = Admin_AffiliateMarketer.objects.filter(is_frozen=True)
    return render(request, 'admin_affiliate_marketing_main_page.html', {'marketer':  marketers_active,'marketers_suspend':marketers_suspend})

def admin_affiliate_market_suspend(request, marketer_id):
    marketer = get_object_or_404(Admin_AffiliateMarketer, pk=marketer_id)
    marketer.is_frozen = True
    marketer.save()
    marketers_active = Admin_AffiliateMarketer.objects.filter(is_frozen=False)
    marketers_suspend = Admin_AffiliateMarketer.objects.filter(is_frozen=True)
    return redirect('admin_affiliate_marketing_main_page')


def admin_affiliate_market_active(request, marketer_id):
    marketer = get_object_or_404(Admin_AffiliateMarketer, pk=marketer_id)
    marketer.is_frozen = False
    marketer.save()
    marketers_active = Admin_AffiliateMarketer.objects.filter(is_frozen=False)
    marketers_suspend = Admin_AffiliateMarketer.objects.filter(is_frozen=True)
    return redirect('admin_affiliate_marketing_main_page')



def admin_affiliate_account_list(request):
    accounts = Admin_AffiliateAccount.objects.all()
    return render(request, 'admin_affiliate_account_list.html', {'accounts': accounts})


def admin_affiliate_account_detail(request, account_id):
    account = get_object_or_404(Admin_AffiliateAccount, pk=account_id)
    return render(request, 'admin_affiliate_account_detail.html', {'account': account})


def admin_affiliate_account_create(request):
    if request.method == 'POST':
        form = Admin_AffiliateAccountForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_affiliate_marketing_main_page')
    else:
        form = Admin_AffiliateAccountForm()
    return render(request, 'admin_affiliate_account_form.html', {'form': form})


def admin_affiliate_account_update(request, account_id):
    account = get_object_or_404(Admin_AffiliateAccount, pk=account_id)
    if request.method == 'POST':
        form = Admin_AffiliateAccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            return redirect('admin_affiliate-account-detail', account_id=account_id)
    else:
        form = Admin_AffiliateAccountForm(instance=account)
    return render(request, 'admin_affiliate_account_form.html', {'form': form})


def admin_affiliate_marketer_search(request):
    query = request.GET.get('query')
    marketers = None

    if query:
        marketers = Admin_AffiliateMarketer.objects.filter(name__icontains=query)

    return render(request, 'admin_affiliate_market_search.html', {'marketers': marketers, 'query': query})


def admin_affiliate_marketer_freeze(request, marketer_id):
    marketer = get_object_or_404(Admin_AffiliateMarketer, pk=marketer_id)
    marketer.is_frozen = True
    marketer.save()
    return redirect('admin_affiliate-market-list')


def admin_affiliate_marketer_reset(request, marketer_id):
    marketer = get_object_or_404(Admin_AffiliateMarketer, pk=marketer_id)
    marketer.is_frozen = False
    marketer.save()
    return redirect('admin_affiliate-market-list')


def admin_identify_top_performers(request):
    # Calculate total sales generated by each marketer
    top_performers = Admin_AffiliateMarketer.objects.annotate(
        total_sales=Sum('sales__sale_amount')).order_by('-total_sales')[:5]

    return render(request, 'admin_identify_top_performers.html', {'top_performers': top_performers})


def admin_affiliate_market(request):
    return render(request, 'admin_affiliate_market.html')


def admin_create_course_provider_management(request):
    if request.method == 'POST':
        form = Admin_CourseProviderForm(request.POST, request.FILES)
        if form.is_valid():
            '''# Get the selected courses from the form
            selected_courses = form.cleaned_data.get('course')
            # Create a new CourseProvider instance
            course_provider = form.save(commit=False)
            # Set the user to the currently logged in user
            course_provider.user = request.user
            # If any courses were selected, assign the first one (assuming only one can be selected)
            if selected_courses:
                course_provider.course = selected_courses.first()
            course_provider.save()'''
            form.save()
            return redirect(
                'admin_super-panel')  # Replace 'success_url' with the URL where you want to redirect after successful signup
        else:
            print(form.errors)
    else:
        form = Admin_CourseProviderForm()

    return render(request, 'admin_create_course_provider.html', {'form': form})


def admin_add_payout_detail(request):
    if request.method == 'POST':
        form = Admin_PayoutDetailForm(request.POST)
        if form.is_valid():
            payoutdetails = form.save(commit=False)
            payoutdetails.course_provider = request.user.course_provider

            payoutdetails.save()
            # Redirect to success URL after adding payout detail
            return HttpResponse('success_url')
    else:
        form = Admin_PayoutDetailForm()
    return render(request, 'admin_add_payout_detail.html', {'form': form})


def admin_edit_payout_detail(request, payout_detail_id):
    payout_detail = get_object_or_404(Admin_PayoutDetail, id=payout_detail_id)
    if request.method == 'POST':
        form = Admin_PayoutDetailForm(request.POST, instance=payout_detail)
        if form.is_valid():
            form.save()
            # Redirect to success URL after editing payout detail
            return redirect('success_url')
    else:
        form = Admin_PayoutDetailForm(instance=payout_detail)
    return render(request, 'admin_edit_payout_detail.html', {'form': form, 'payout_detail': payout_detail})


def admin_delete_payout_detail(request, payout_detail_id):
    payout_detail = get_object_or_404(Admin_PayoutDetail, id=payout_detail_id)
    if request.method == 'POST':
        payout_detail.delete()
        # Redirect to success URL after deleting payout detail
        return redirect('success_url')
    return render(request, 'admin_confirm_delete_payout_detail.html', {'payout_detail': payout_detail})


def admin_course_provider_management(request):
    return render(request, 'admin_course_provider_management.html')

def admin_course_provider_create_account(request):
        first_name = request.POST.get('first_name')
        last_name =  request.POST.get('last_name')
        email =  request.POST.get('email')
        phone_number =  request.POST.get('phone_number')
        DOB = request.POST.get('DOB')
        gender = request.POST.get('gender')
        account_name = request.POST.get('account_name')
        account_number = request.POST.get('account_number')
        bank_name = request.POST.get('bank_name')
        ifsc_code = request.POST.get('ifsc_code')
        account_type = request.POST.get('account_type')
        location = request.POST.get('location')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        image =  request.FILES.get('image')

        print(first_name,last_name,email,phone_number,DOB,gender,account_name,account_number,bank_name,account_type,location,password1,password2,image,ifsc_code)
        if password1 != password2:
            return render(request, 'admin_affiliate_marketing_create_account.html', {
                'error': 'Passwords do not match.'
            })


def admin_course_provider_update(request,id):
    course_provider = get_object_or_404(Admin_CourseProvider, pk=id)
    if request.method == 'POST':
        form = Admin_CourseProviderForm1(request.POST, instance=course_provider)
        if form.is_valid():
            form.save()
            return redirect('admin_course_provider_database')
    else:
        form = Admin_CourseProviderForm1(instance=course_provider)
    return render(request, 'admin_course_provider_form.html', {'form': form})


def admin_course_provider_delete(request, id):
    provider = get_object_or_404(Admin_CourseProvider, pk=id)
    if request.method == 'POST':
        provider.delete()
        return redirect('admin_course_provider_database')
    provider_active = Admin_CourseProvider.objects.filter(is_active=True)
    provider_suspend = Admin_CourseProvider.objects.filter(is_active=False)
    return render(request, 'admin_course_provider_database.html', {'provider_active':provider_active,'provider_suspend':provider_suspend})

def admin_course_provider_suspend(request, id):
    provider = get_object_or_404(Admin_CourseProvider, pk=id)
    provider.is_active = True
    provider.save()
    return redirect('admin_course_provider_database')


def admin_course_provider_active(request, id):
    provider = get_object_or_404(Admin_CourseProvider, pk=id)
    provider.is_active = False
    provider.save()
    return redirect('admin_course_provider_database')


# Static frontend pages
def admin_landing_page(request):
    return render(request, 'admin_landing_page.html')



'''
def admin_login_page(request):
    if request.method == 'POST':
        form = Admin_LoginForm(request.POST)
        if form.is_valid():

            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                user_type = user.user_type
                if user_type == 1:  # Assuming user_type is an integer field
                    return redirect('admin_begin_class_dashboard_container')
                elif user_type == 2:
                    return HttpResponse('student')
                elif user_type == 3:
                    return HttpResponse('course provider')
                else:
                    messages.error(request, "Invalid Login!")
            else:
                messages.error(request, "Invalid Login!")
    else:
        form = Admin_LoginForm()

    return render(request, 'admin_login_page.html', {'form': form})
'''


def admin_signup(request):
    if request.method == 'POST':
        form = Admin_AdminForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['EmailID']

            # Check if the email already exists
            if get_user_model().objects.filter(email=user_email).exists():
                messages.error(request, 'This email is already in use.')
                # Redirect back to the signup page
                return redirect('admin-signup')

            # Create a new user instance
            user = get_user_model().objects.create_user(
                email=user_email,
                password=form.cleaned_data['password1'],
                username=user_email,  # You can set username as email if you want
                user_type=1  # Assuming 1 represents the admin user type
            )
            # Generate a random OTP and send it to the user's email
            otp = generate_otp()

            # Send the OTP to the user's email
            send_otp(user_email, otp)

            # Save the OTP in the session
            request.session['otp'] = otp
            request.session['email'] = user_email

            return redirect('admin_verify_otp')
    else:
        form = Admin_AdminForm()

    return render(request, 'admin_signup.html', {'form': form})


def admin_teachers(request):
    return render(request, 'admin_teachers.html')


def admin_begin_class_dashboard_container(request):
    return render(request, 'admin_begin_class_dashboard_container.html')


from django.db.models import F, Sum, Count, DecimalField, ExpressionWrapper
from django.utils.timezone import now
from django.db.models.functions import TruncMonth
from .models import (
    Course,
    Enrollment,
    Admin_Payment,
    Admin_CourseProvider,
    Admin_AffiliateMarketer,
    Ticket,
    Admin_Mentorship,
)


def admin_main_dashboard(request):
    # Total enrollments
    total_enrollment_count = Enrollment.objects.count()
    this_month_count = Enrollment.objects.filter(enrollment_date__month=now().month).count()

    # Total earnings
    total_earnings = Admin_Payment.objects.aggregate(
        total=Sum('amount_paid', default=0)
    )['total'] or 0
    this_month_earnings = Admin_Payment.objects.filter(
        date_of_payment__month=now().month
    ).aggregate(total=Sum('amount_paid', default=0))['total'] or 0

    # COURSE EARNINGS
    course_earnings = Course.objects.annotate(
        enrollments_count=Count('payments'),  # Count related payments as enrollments
        total_earnings=Sum('payments__amount_paid'),  # Sum the amount_paid field in payments
        commission=ExpressionWrapper(
            F('total_earnings') * 0.1,  # Calculate 10% commission
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ),
        net_profit=ExpressionWrapper(
            F('total_earnings') - F('commission'),  # Subtract commission from earnings
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    )

    # 1:1 MENTORSHIP
    mentorship_requests = Admin_Mentorship.objects.select_related('course', 'mentor').values(
        'course__course_name', 'mentor__name', 'request_date', 'status'
    )

    # COURSE PROVIDERS
    course_providers = Admin_CourseProvider.objects.annotate(
        total_courses=Count('courses'),  # Count the total courses provided by the provider
        total_enrollments=Count('courses__payments'),  # Count enrollments via payments
        total_earnings=Sum('courses__payments__amount_paid', default=0),  # Sum earnings from payments
        per_share=ExpressionWrapper(
            F('total_earnings') * 0.05,  # Calculate 5% share for providers
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    )

    # AFFILIATE MARKETERS
    affiliate_marketers = Admin_AffiliateMarketer.objects.annotate(
        total_enrollments=Count('enrolled_users', distinct=True),
        total_amount=Sum('sales__sale_amount', default=0),
        per_share=ExpressionWrapper(
            F('total_amount') * 0.1,  # Assuming 10% commission
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ),
        invoice_id=F('sales__invoice_id'),  # Fetch invoice number
        month=TruncMonth('sales__sale_date')  # Group by month
    ).values('name', 'total_enrollments', 'total_amount', 'per_share', 'invoice_id', 'month')

    # SUPPORT PANEL
    support_tickets = Ticket.objects.select_related('user', 'category', 'subcategory').all()

    # Render context
    context = {
        'total_enrollment_count': total_enrollment_count,
        'this_month_count': this_month_count,
        'total_earnings': total_earnings,
        'this_month_earnings': this_month_earnings,
        'course_earnings': course_earnings,
        'mentorship_requests': mentorship_requests,
        'course_providers': course_providers,
        'affiliate_marketers': affiliate_marketers,
        'support_tickets': support_tickets,
    }

    return render(request, 'admin_main_dashboard.html', context)


'''
def admin_main_dashboard(request):
    # Total and this month's enrollments
    total_enrollment_count = Student.objects.filter(
        Q(ongoing_courses__isnull=False) | Q(completed_courses__isnull=False)
    ).distinct().count()

    current_month = datetime.now().month
    this_month_count = Student.objects.filter(
        Q(ongoing_courses__created_at__month=current_month) | Q(completed_courses__created_at__month=current_month)
    ).distinct().count()

    courses = Course.objects.annotate(
        no_of_enrollments=Count('completed_students', distinct=True) + Count('ongoing_students', distinct=True),
        earnings=ExpressionWrapper(F('price') * total_enrollment_count, output_field=DecimalField()),
        commission=ExpressionWrapper(F('price') * 0.1, output_field=DecimalField()),
        net_profit=ExpressionWrapper(F('price') * total_enrollment_count - (F('price') * 0.1), output_field=DecimalField())
    ).all()

    # Total and this month's earnings
    total_earnings = courses.aggregate(total=Sum('earnings'))['total'] or 0
    this_month_earnings = courses.filter(created_at__month=current_month).aggregate(total=Sum('earnings'))['total'] or 0

    # Fetch mentorship requests
    mentors = MentorshipRequest.objects.all()

    # Fetch course providers
    course_providers = Admin_CourseProvider.objects.all()

    # Fetch affiliate marketers
    affiliate_marketers = Admin_AffiliateMarketer.objects.all()

    # Fetch support tickets
    support_tickets = Ticket.objects.all()

    # Pass data to the template
    context = {
        'total_enrollment_count': total_enrollment_count,
        'this_month_count': this_month_count,
        'total_earnings': total_earnings,
        'this_month_earnings': this_month_earnings,
        'courses': courses,
        'mentors': mentors,
        'course_providers': course_providers,
        'affiliate_marketers': affiliate_marketers,
        'support_tickets': support_tickets,
    }
    return render(request, 'admin_main_dashboard.html', context)
'''


def admin_student_management(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'admin_student_management.html', {'student': student})


def admin_student_management_course_enroll(request):
    return render(request, 'admin_student_management_course_enroll.html')


def admin_student_management_referral_detail(request):
    return render(request, 'admin_student_management_referral_detail.html')


def admin_student_management_payment_details(request):
    return render(request, 'admin_student_management_payment_details.html')


def admin_provider_management(request):
    return render(request, 'admin_provider_management.html')


def admin_provider_management_payment(request):
    payment_paid = Admin_Payment.objects.filter(status="completed")
    payment_pending = Admin_Payment.objects.filter(status="pending")
    return render(request, 'admin_provider_management_payment.html',
                  {'payment_paid':payment_paid,
                    'payment_pendings':payment_pending,})


def admin_provider_management_payment_view(request):
    return render(request, 'admin_provider_management_payment_view.html')


def admin_provider_management_payment_pay(request):
    return render(request, 'admin_provider_management_payment_pay.html')


def admin_dashboard_support_panel_chat(request):
    if request.method == 'POST':
        form = Admin_TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return JsonResponse({'redirect': True, 'url': request.build_absolute_uri('admin_ticket_list')})
    else:
        form = Admin_TicketForm()
    tickets = Ticket.objects.filter(user=request.user)
    chat_form = Admin_ChatMessageForm()

    return render(request, 'admin_dashboard_support_panel_chat.html',
                  {'ticket_form': form, 'tickets': tickets, 'chat_form': chat_form})


def admin_dashboard_analytics(request):
    return render(request, 'admin_dashboard_analytics.html')


def admin_course_manage_add_course(request):
    if request.method == 'POST':
        # Handle form submission with default values
        course_name = request.POST.get('course_name', '')
        description = request.POST.get('description', '')
        price_str = request.POST.get('price', '0.00').strip()
        category_type = request.POST.get('category_type', 'c1')  # Default to 'Tech Courses'
        what_you_will_learn = request.POST.get('what_you_will_learn', 'No details provided')
        skills_you_will_gain = request.POST.get('skills_you_will_gain', 'No details provided')
        mentor_id = request.POST.get('mentor', None)
        category_id = request.POST.get('category', None)
        is_active = request.POST.get('isActive', 'on') == 'on'  # Convert to boolean
        image = request.FILES.get('courseImage')
        requirement = request.POST.get('mentorshipContent')

        message=request.POST.get('messageContent')

        career_content = request.POST.get('careerGuidanceContent')
        career_image = request.FILES.get('careerGuidanceImage')

        question_paper_title = request.POST.get('previousQpTitle')
        question_paper_paper = request.FILES.get('previousQpUpload')
        question_paper_result = request.FILES.get('previousAnsUpload')

        mentor_name = request.POST.get('mentorNames')

        week1_title = request.POST.get('weekTitle1')
        week1_video = request.FILES.get('videoUpload1')
        url1 = request.POST.get('url1')

        week2_title = request.POST.get('weekTitle2')
        week2_video = request.FILES.get('videoUpload2')
        url2 = request.POST.get('url2')

        week3_title = request.POST.get('weekTitle3')
        week3_video = request.FILES.get('videoUpload3')
        url3 = request.POST.get('url3')

        week4_title = request.POST.get('weekTitle4')
        week4_video = request.FILES.get('videoUpload4')
        url4 = request.POST.get('url4')

        week5_title = request.POST.get('weekTitle5')
        week5_video = request.FILES.get('videoUpload5')
        url5 = request.POST.get('url5')

        if not price_str:  # If the string is empty, assign default
            price_str = '0.00'

        try:
            price = Decimal(price_str)
        except InvalidOperation:
            return HttpResponseBadRequest("Invalid price format.")

        try:
            mentor = Admin_Mentor.objects.get(id=mentor_id) if mentor_id else None
            category = Admin_CourseCategory.objects.get(id=category_id) if category_id else None
            provider = Admin_CourseProvider.objects.get(id=1) if Admin_CourseProvider.objects.filter(
                id=1).exists() else None

            # Create the course
            course = Course.objects.create(
                user=request.user,
                course_name=course_name,
                name=course_name,
                title=course_name,
                description=description,
                price=price,
                category_type=category_type,
                what_you_will_learn=what_you_will_learn,
                skills_you_will_gain=skills_you_will_gain,  ###
                mentor=mentor,
                category=category,
                is_active=is_active,  ###
                provider=provider,
                requirement=requirement,
                image=image,
                instructor=mentor_name,
            )

            # CareerGuidance
            CareerGuidanceMessage.objects.create(
                course=course,
                content=career_content,
                image=career_image,
            )
            # QuestionPaper
            QuestionPaper.objects.create(
                course=course,
                title=question_paper_title,
                subject=question_paper_title,
                file=question_paper_paper,
                answer=question_paper_result,
            )

            Message.objects.create(
                course=course,
                content=message,
            )

            def create_week(course,number,title,video,url):
                week = Week.objects.create(
                    course=course,
                    number=number,
                    title=title,
                    description=title,
                )
                Topic.objects.create(
                    week=week,
                    title=title,
                    video_file=video,
                    video_link=url,
                )

            if week1_title and week1_video:
                create_week(course,1,week1_title,week1_video,url1)

            if week2_title and week2_video:
                create_week(course,2,week2_title,week2_video,url2)

            if week3_title and week3_video:
                create_week(course,3,week3_title,week3_video,url3)

            if week4_title and week4_video:
                create_week(course,4,week4_title,week4_video,url4)

            if week5_title and week5_video:
                create_week(course,5,week5_title,week5_video,url5)

            # Handle dynamically added weeks, modules, and their content
            # week_titles = request.POST.getlist('weekTitle[]')
            # for week_title in week_titles:
            #     week = Week.objects.create(course=course, title=week_title)

            #     module_titles = request.POST.getlist('moduleTitle[]')
            #     module_contents = request.POST.getlist('moduleContent[]')

            #     # Ensure that the lengths of module titles and contents are the same
            #     if len(module_titles) != len(module_contents):
            #         return HttpResponseBadRequest("Module titles and contents do not match in length.")

            #     for module_title, module_content in zip(module_titles, module_contents):
            #         module = Admin_Module.objects.create(week=week, title=module_title, content=module_content)

            #         article_titles = request.POST.getlist('articleTitle[]')
            #         article_contents = request.POST.getlist('articleContent[]')

            #         # Ensure that the lengths of article titles and contents are the same
            #         if len(article_titles) != len(article_contents):
            #             return HttpResponseBadRequest("Article titles and contents do not match in length.")

            #         for article_title, article_content in zip(article_titles, article_contents):
            #             Admin_Article.objects.create(module=module, title=article_title, content=article_content)

            #         video_titles = request.POST.getlist('videoTitle[]')
            #         video_urls = request.POST.getlist('videoUrl[]')

            #         # Ensure that the lengths of video titles and URLs are the same
            #         if len(video_titles) != len(video_urls):
            #             return HttpResponseBadRequest("Video titles and URLs do not match in length.")

            #         for video_title, video_url in zip(video_titles, video_urls):
            #             Admin_Video.objects.create(module=module, title=video_title, url=video_url)

            #         assignment_titles = request.POST.getlist('assignmentTitle[]')
            #         assignment_descriptions = request.POST.getlist('assignmentDescription[]')

            #         # Ensure that the lengths of assignment titles and descriptions are the same
            #         if len(assignment_titles) != len(assignment_descriptions):
            #             return HttpResponseBadRequest("Assignment titles and descriptions do not match in length.")

            #         for assignment_title, assignment_description in zip(assignment_titles, assignment_descriptions):
            #             Admin_Assignment.objects.create(module=module, title=assignment_title,
            #                                             description=assignment_description)

            #         quiz_titles = request.POST.getlist('quizTitle[]')
            #         quiz_questions = request.POST.getlist('quizQuestions[]')

            #         # Ensure that the lengths of quiz titles and questions are the same
            #         if len(quiz_titles) != len(quiz_questions):
            #             return HttpResponseBadRequest("Quiz titles and questions do not match in length.")

            #         for quiz_title, quiz_question in zip(quiz_titles, quiz_questions):
            #             Admin_Quiz.objects.create(module=module, title=quiz_title, questions=quiz_question)

            return redirect('admin_course_manage_main_page')

        except Admin_Mentor.DoesNotExist:
            return HttpResponseBadRequest("Mentor does not exist.")
        except Admin_CourseCategory.DoesNotExist:
            return HttpResponseBadRequest("Category does not exist.")

    else:
        mentors = Admin_Mentor.objects.all()
        categories = Admin_CourseCategory.objects.all()
        return render(request, 'admin_course_manage_add_course.html', {'mentors': mentors, 'categories': categories})


def admin_course_provider_database(request):
    provider_active = Admin_CourseProvider.objects.filter(is_active=False)
    provider_suspend = Admin_CourseProvider.objects.filter(is_active=True)
    return render(request, 'admin_course_provider_database.html',
                  {
                      'provider_active':provider_active,
                      'provider_suspend':provider_suspend,
                  })


def admin_course_provider_create_account_form(request):
    return render(request, 'admin_course_provider_create_account_form.html')

def admin_course_provider_create_account_form1(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name =  request.POST.get('last_name')
        email =  request.POST.get('email')
        phone_number =  request.POST.get('phone_number')
        gender = request.POST.get('gender')
        account_name = request.POST.get('account_name')
        account_number = request.POST.get('account_number')
        bank_name = request.POST.get('bank_name')
        ifsc_code = request.POST.get('ifsc_code')
        account_type = request.POST.get('account_type')

        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')


        print(first_name,last_name,email,phone_number,gender,account_name,account_number,bank_name,account_type,password1,password2,ifsc_code)
        if password1 != password2:
            return render(request, 'admin_affiliate_marketing_create_account.html', {
                'error': 'Passwords do not match.'
            })

        try:
            Admin_CourseProvider.objects.create(
                    name=first_name,
                    last_name=last_name,
                    email=email,
                    phone_number=phone_number,
                    gender=gender,
                    account_name=account_name,
                    account_number=account_number,
                    account_type=account_type,
                    bank_name=bank_name,
                    ifsc_code=ifsc_code,
                    # password1=password1,
                    # password2=password2,
                )

            provider_active = Admin_CourseProvider.objects.filter(is_active=False)
            provider_suspend = Admin_CourseProvider.objects.filter(is_active=True)
            return render(request, 'admin_course_provider_database.html', {'provider_active':provider_active,'provider_suspend':provider_suspend})

        except Exception as e:
            print("Error:", e)
            return render(request, 'admin_course_provider_create_account_form.html', {
                'error': 'Something went wrong. Please try again.'
            })

    return render(request, 'admin_course_provider_create_account_form.html', {'form': form})


class dashboard_feedback(ListView):
    model = Admin_FormFeedback
    template_name = 'admin_formfeedback_list.html'
    context_object_name = 'formfeedbacks'

    def get_queryset(self):
        # Fetch all FormFeedback objects and annotate them with the number of questions and responses
        queryset = Admin_FormFeedback.objects.all()
        for form in queryset:
            form.num_questions = form.questions.count()  # Number of questions in the form
            form.num_responses = form.responses.count()  # Number of responses to the form
        return queryset


def admin_dashboard_create_feedback(request):
    return render(request, 'admin_dashboard_create_feedback.html')


def admin_dashboard_feedback_view(request):
    return render(request, 'admin_dashboard_feedback_view.html')


def admin_affiliate_marketing_main_page(request):
    marketers = Admin_AffiliateMarketer.objects.filter(is_frozen=False)
    marketers_suspend = Admin_AffiliateMarketer.objects.filter(is_frozen=True)
    return render(request, 'admin_affiliate_marketing_main_page.html', {'marketers': marketers,'marketers_suspend':marketers_suspend})


from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Admin_ReferralProgram, Admin_ReferralLink


def admin_marketing_promotion_referal(request):
    # Fetch all referral programs
    referrals = Admin_ReferralProgram.objects.all()

    # Sort referrals based on query parameter
    sort_by = request.GET.get('sort', 'default')
    if sort_by == 'referral_code':
        referrals = referrals.order_by('partner_name')  # Replace with the appropriate field if needed
    elif sort_by == 'referral_count':
        referrals = referrals.order_by('-referral_count')

    # Pagination
    paginator = Paginator(referrals, 10)  # Show 10 items per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Context to pass to the template
    context = {
        'page_obj': page_obj,  # Paged referral programs
        'breadcrumb': ['Dashboard', 'Marketing', 'Referral Program'],
        'total_course_enrollments': referrals.aggregate(total=Sum('referral_count'))['total'] or 0,
    }

    return render(request, 'admin_marketing_promotion_referal.html', context)


from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Admin_Voucher, Admin_Enrollment


def admin_marketing_promotion_view_bills(request):
    # Fetch all voucher data
    vouchers = Admin_Voucher.objects.all()

    # Sorting
    sort_by = request.GET.get('sort', 'default')
    if sort_by == 'voucher':
        vouchers = vouchers.order_by('code')  # Sort by voucher code

    # Pagination
    paginator = Paginator(vouchers, 10)  # 10 vouchers per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Context data for rendering the template
    context = {
        'breadcrumb2': ['Dashboard', 'Marketing', 'View Bills'],  # Breadcrumb navigation
        'total_course_enrollments2': Admin_Enrollment.objects.count(),
        'page_obj': page_obj,  # Paged voucher data
        'courses2': list(page_obj.object_list.values()),  # Pass to JavaScript for dynamic rendering
    }

    return render(request, 'admin_marketing_promotion_view_bills.html', context)


class FormFeedbackListView(ListView):
    model = Admin_FormFeedback
    template_name = 'admin_formfeedback_list.html'
    context_object_name = 'formfeedbacks'

    def get_queryset(self):
        # Fetch all FormFeedback objects and annotate them with the number of questions and responses
        queryset = Admin_FormFeedback.objects.all()
        for form in queryset:
            form.num_questions = form.questions.count()  # Number of questions in the form
            form.num_responses = form.responses.count()  # Number of responses to the form
        return queryset


class FormFeedbackCreateView(CreateView):
    model = Admin_FormFeedback
    form_class = Admin_FormFeedbackForm
    template_name = 'admin_formfeedback_form.html'
    success_url = reverse_lazy('admin_formfeedback_list')


class FormFeedbackUpdateView(UpdateView):
    model = Admin_FormFeedback
    form_class = Admin_FormFeedbackForm
    template_name = 'admin_formfeedback_form.html'
    success_url = reverse_lazy('admin_formfeedback_list')


class FormFeedbackDeleteView(DeleteView):
    model = Admin_FormFeedback
    template_name = 'admin_formfeedback_confirm_delete.html'
    success_url = reverse_lazy('admin_formfeedback_list')


def admin_submit_feedback(request, formfeedback_id):
    formfeedback = get_object_or_404(Admin_FormFeedback, pk=formfeedback_id)

    if request.method == 'POST':
        response_form = Admin_FeedbackResponseForm(request.POST, feedback_form=formfeedback)
        if response_form.is_valid():
            response = response_form.save(commit=False)
            response.form = formfeedback
            response.respondent = request.user  # Assuming user is authenticated
            response.save()
            response_form.save_answers(response)
            return redirect('admin_formfeedback_list')
    else:
        response_form = Admin_FeedbackResponseForm(feedback_form=formfeedback)

    context = {
        'formfeedback': formfeedback,
        'response_form': response_form,
    }
    return render(request, 'admin_submit_feedback.html', context)


def admin_offers_voucher(request):
    if request.method == 'POST':
        form = Admin_VoucherForm(request.POST)
        if form.is_valid():
            voucher = form.save(commit=False)
            voucher.created_by = request.user
            voucher.used_count = 0  # Ensure used_count is set to 0 upon creation
            voucher.save()
            form.save_m2m()
            return redirect(reverse('admin_offers_voucher'))  # Redirect to the offers list view
    else:
        form = Admin_VoucherForm()

    courses = Course.objects.all()  # Fetch all courses
    vouchers = Admin_Voucher.objects.filter(is_active=True).order_by('-start_date')
    return render(request, 'admin_offers_voucher.html', {'form': form, 'courses': courses, 'vouchers': vouchers})


def admin_about_us(request):
    return render(request, 'admin_about_us.html')


def admin_provider_management_payment_page(request):
    return render(request, 'admin_provider_management_payment_page.html')


def admin_course_manage_main_page(request):
    courses = Course.objects.filter(user=request.user)
    category_filter = request.GET.get('category')
    if category_filter:
        courses = courses.filter(category_type=category_filter)
    return render(request, 'admin_course_manage_main_page.html', {'courses': courses})


'''
def admin_provider_management_dashboard(request):
    # Fetching data from the backend
    total_enrollment_count = Payment.objects.aggregate(Sum('no_of_enrollments'))['no_of_enrollments__sum'] or 0
    total_earnings = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_payout = Payment.objects.filter(pay_status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0
    total_net_profit = total_earnings - total_payout

    this_month_payments = Payment.objects.filter(month__month=request.GET.get('month', 1))
    this_month_count = this_month_payments.aggregate(Sum('no_of_enrollments'))['no_of_enrollments__sum'] or 0
    this_month_earning = this_month_payments.aggregate(Sum('amount'))['amount__sum'] or 0
    this_month_payout = this_month_payments.filter(pay_status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0
    this_month_net_profit = this_month_earning - this_month_payout

    # Querying the Payment, ProviderEarnings, and CourseEarnings tables
    course_providers = Admin_CourseProvider.objects.all()
    # Fetching and combining data for the PAYMENT table
    payments = list()
    for course_provider in course_providers:
        for_invoice_no = Admin_PayoutDetail.objects.filter(course_provider=course_provider)
        invoice_no = for_invoice_no.transaction_id
        for_name = Admin_CourseProvider.objects.filter(course_provider=course_provider)
        name = for_name.first_name + " " + for_name.last_name

        month = for_invoice_no.first().payout_date.strftime("%B")

        courses = for_name.courses.all()
        course_name = for_name.courses

        course_ids = [course.id for course in courses]

        # Get students in ongoing_courses
        ongoing_students = Student.objects.filter(ongoing_courses__id__in=course_ids)

        # Get students in completed_courses
        completed_students = Student.objects.filter(completed_courses__id__in=course_ids)

        # Combine both sets and remove duplicates
        total_students = ongoing_students.union(completed_students).distinct()

        no_of_enrollments = total_students.count()
        per_share = for_invoice_no.amount * (0.10)
        amount = for_invoice_no.amount

    for course in courses:
        payment_entry = {
            'invoice_no': invoice_no,
            'name': name,
            'month': month,  # Use the month of payout date
            'course_name': course_name,
            'no_of_enrollments': no_of_enrollments,
            'per_share': per_share,
            'amount': amount
        }
        payments.append(payment_entry)

    # Fetching and combining data for the PROVIDER EARNINGS table
    provider_earnings = list()
    additional_provider_earnings =
    for entry in additional_provider_earnings:
        provider_earnings.append(entry)

    # Fetching and combining data for the COURSE EARNINGS table
    course_earnings = list(CourseEarnings.objects.all())
    # Add more data from another model to course_earnings
    extra_course_earnings = SomeOtherModel.objects.filter(type="course")
    for entry in extra_course_earnings:
        course_earnings.append(entry)

    # Rendering the template with context data
    context = {
        'total_enrollment_count': total_enrollment_count,
        'total_earnings': total_earnings,
        'total_payout': total_payout,
        'total_net_profit': total_net_profit,
        'this_month_count': this_month_count,
        'this_month_earning': this_month_earning,
        'this_month_payout': this_month_payout,
        'this_month_net_profit': this_month_net_profit,
        'payments': payments,
        'provider_earnings': provider_earnings,
        'course_earnings': course_earnings,
    }
    return render(request, 'admin_provider_management_dashboard.html', context)
'''

from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from django.utils.timezone import now
from .models import (
    Course,
    Admin_Payment,
    Admin_CourseProvider,
)


def admin_provider_management_dashboard(request):
    # Statistics for the dashboard
    total_enrollment_count = Admin_Payment.objects.count()
    this_month_count = Admin_Payment.objects.filter(
        date_of_payment__month=now().month
    ).count()

    total_earnings = Admin_Payment.objects.aggregate(
        total=Sum('amount_paid', default=0)
    )['total']
    this_month_earnings = Admin_Payment.objects.filter(
        date_of_payment__month=now().month
    ).aggregate(total=Sum('amount_paid', default=0))['total']

    total_payout = 0  # Adjust if you have a payout model or logic
    total_net_profit = total_earnings - total_payout if total_earnings else 0

    this_month_payout = 0  # Adjust logic for monthly payout
    this_month_net_profit = this_month_earnings - this_month_payout if this_month_earnings else 0

    # PAYMENT Table
    payments = Admin_Payment.objects.annotate(
        name=F('student__Full_Name'),
        course_name=F('course__course_name'),
        month=F('date_of_payment__month'),
        no_of_enrollments=Count('enrollment'),
        per_share=ExpressionWrapper(
            F('amount_paid') * 0.05,
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ),
        pay_status=F('status')
    )

    # PROVIDER EARNINGS Table
    provider_earnings = Admin_CourseProvider.objects.annotate(
        provider_name=F('name'),
        no_of_courses=Count('courses'),
        no_of_enrollments=Count('courses__payments'),
        total_earnings=Sum('courses__payments__amount_paid', default=0),
        total_commission=ExpressionWrapper(
            F('total_earnings') * 0.1,
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ),
        net_profit=ExpressionWrapper(
            F('total_earnings') - F('total_commission'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    )

    # COURSE EARNINGS Table
    course_earnings = Course.objects.annotate(
        provider_name=F('provider__name'),
        no_of_enrollments=Count('payments'),
        earnings=Sum('payments__amount_paid', default=0),
        commission=ExpressionWrapper(
            F('earnings') * 0.1,
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ),
        net_profit=ExpressionWrapper(
            F('earnings') - F('commission'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    )

    # Render the template with context
    context = {
        'total_enrollment_count': total_enrollment_count,
        'this_month_count': this_month_count,
        'total_earnings': total_earnings,
        'total_payout': total_payout,
        'total_net_profit': total_net_profit,
        'this_month_earning': this_month_earnings,
        'this_month_payout': this_month_payout,
        'this_month_net_profit': this_month_net_profit,
        'payments': payments,
        'provider_earnings': provider_earnings,
        'course_earnings': course_earnings,
    }
    return render(request, 'admin_provider_management_dashboard.html', context)


def admin_affiliate_marketing_payments(request):
    total_enrollment_count = Enrollment.objects.count()
    this_month_count = Enrollment.objects.filter(enrollment_date__month=now().month).count()

    # Total earnings
    total_earnings = Admin_Payment.objects.aggregate(total=Sum('amount_paid', default=0))['total'] or 0
    payment_paid = Admin_Payment.objects.filter(status="completed")
    payment_pending = Admin_Payment.objects.filter(status="pending")
    return render(request, 'admin_affiliate_marketing_payments.html',
        {'total_enrollment_count': total_enrollment_count,
        'this_month_count': this_month_count,
        'total_earnings': total_earnings,
        'payment_paid':payment_paid,
        'payment_pendings':payment_pending})


def admin_affiliate_marketing_payments_pay(request):
    return render(request, 'admin_affiliate_marketing_payments_pay.html')


def admin_affiliate_marketing_create_account(request):
    # if request.method == 'POST':
    #     form = Admin_AffiliateMarketerForm(request.POST)

    #     if form.is_valid():
    #         #  Assign the current user to the form's user field
    #         form.instance.user = request.user
    #         form.save()
    #         return redirect('admin_affiliate_marketing_main_page')
    #     return render(request, 'admin_affiliate_market_create.html', {'form': form})
    # else:
    #     form = Admin_AffiliateMarketerForm()

    # if request.method == 'POST':
    #     first_name = request.POST.get('first_name')
    #     last_name =  request.POST.get('last_name')
    #     email =  request.POST.get('email')
    #     phone_number =  request.POST.get('phone_number')
    #     DOB = request.POST.get('DOB')
    #     gender = request.POST.get('gender')
    #     account_name = request.POST.get('account_name')
    #     account_number = request.POST.get('account_number')
    #     bank_name = request.POST.get('bank_name')
    #     ifsc_code = request.POST.get('ifsc_code')
    #     account_type = request.POST.get('account_type')
    #     location = request.POST.get('location')
    #     password1 = request.POST.get('password1')
    #     password2 = request.POST.get('password2')
    #     image =  request.FILES.get('image')

    #     try:
    #         Admin_AffiliateMarketer.objects.create(
    #             first_name=first_name,
    #             last_name=last_name,
    #             email=email,
    #             phone_number=phone_number,
    #             DOB=DOB,
    #             image=image,
    #             gender=gender,
    #             account_name=account_name,
    #             account_number=account_number,
    #             account_type=account_type,
    #             bank_name=bank_name,
    #             ifsc_code=ifsc_code,
    #             location=location,
    #             password=password1,
    #             password2=password2,
    #         )
    #     except:
    #         return render(request,'admin_affiliate_marketing_main_page.html')
    # else:
    #     return render(request, 'admin_affiliate_marketing_create_account.html')
    return render(request, 'admin_affiliate_marketing_create_account.html')

def admin_affiliate_marketing_create_account1(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name =  request.POST.get('last_name')
        email =  request.POST.get('email')
        phone_number =  request.POST.get('phone_number')
        DOB = request.POST.get('DOB')
        gender = request.POST.get('gender')
        account_name = request.POST.get('account_name')
        account_number = request.POST.get('account_number')
        bank_name = request.POST.get('bank_name')
        ifsc_code = request.POST.get('ifsc_code')
        account_type = request.POST.get('account_type')
        location = request.POST.get('location')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        image =  request.FILES.get('image')

        print(first_name,last_name,email,phone_number,DOB,gender,account_name,account_number,bank_name,account_type,location,password1,password2,image,ifsc_code)
        if password1 != password2:
            return render(request, 'admin_affiliate_marketing_create_account.html', {
                'error': 'Passwords do not match.'
            })

        try:
            Admin_AffiliateMarketer.objects.create(
                    name=first_name,
                    last_name=last_name,
                    email=email,
                    phone_number=phone_number,
                    DOB=DOB,
                    image=image,
                    gender=gender,
                    account_name=account_name,
                    account_number=account_number,
                    account_type=account_type,
                    bank_name=bank_name,
                    ifsc_code=ifsc_code,
                    location=location,
                    password1=password1,
                    password2=password2,
                )
            marketers = Admin_AffiliateMarketer.objects.all()

            return render(request,'admin_affiliate_marketing_main_page.html',{'marketers':marketers})
        except Exception as e:
            print("Error:", e)
            return render(request, 'admin_affiliate_marketing_create_account.html', {
                'error': 'Something went wrong. Please try again.'
            })

    return render(request, 'admin_affiliate_marketing_create_account.html')

def admin_course_manage_bulk_course(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        common_description = request.POST.get('common_description')
        amount = request.POST.get('amount')
        course_ids = request.POST.getlist('courses')

        if not title or not common_description or not amount:
            return HttpResponseBadRequest("Missing required fields")

        try:
            amount = float(amount)
        except ValueError:
            return HttpResponseBadRequest("Invalid amount format")

        bulk_course = Admin_BulkCourse.objects.create(
            title=title,
            common_description=common_description,
            amount=amount
        )

        # bulk_course.courses.set(Course.objects.filter(id__in=course_ids))

        # Redirect with the bulk_course_id as a parameter
        return redirect('admin_course_manage_main_page')
    else:
        courses = Course.objects.all()
    return render(request, 'admin_course_manage_bulk_course.html', {'courses': courses})


def admin_course_manage_bulk_course_sub(request):
    return render(request, 'admin_course_manage_bulk_course_sub.html')


def admin_one_to_one_Mentorship(request):
    pending_payments = Admin_Mentorship.objects.filter(status="Accepted")
    paid_payments = Admin_Mentorship.objects.filter(status="Pending")
    return render(request, 'admin_1_to_1_Mentorship.html',
                  {
                      'pending_payments':pending_payments,
                      'paid_payments':paid_payments,
                  })


def admin_student_management_database(request):
    if request.method == 'POST':
        form = Admin_StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_student_management_database')
    else:
        form = Admin_StudentForm()
    students = Student.objects.all()
    return render(request, 'admin_student_management_database.html', {'students': students, 'form': form})


def admin_course_details_page(request):
    return render(request, 'admin_course_details_page.html')


def admin_course_details_quiz(request):
    return render(request, 'admin_course_details_quiz.html')


def admin_course_details_assignments(request):
    return render(request, 'admin_course_details_assignments.html')


def admin_course_details_main_quiz(request):
    return render(request, 'admin_course_details_main_quiz.html')


@login_required
def admin_blog(request):
    blogs = BlogPost.objects.all()
    profile_image = None  # Default value for profile_image
    if request.user.is_authenticated:
        try:
            profile_data = Profile.objects.get(user=request.user)
            if profile_data.profile_picture:
                profile_image = profile_data
            else:
                profile_image = 10
        except Profile.DoesNotExist:
            profile_image = 10  # Default profile image indicator
    return render(request, 'admin_blog.html', {'blogs': blogs, 'profile': profile_image})


def admin_create_blog(request):
    if request.method == 'POST':
        form = Admin_BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog_post = form.save(commit=False)
            if not request.FILES.get('image'):
                blog_post.image = 'admin_covers/1.gif'
            blog_post.author = request.user
            blog_post.save()
            form.save_m2m()
            return redirect('admin_blog')
    else:
        form = Admin_BlogForm()
    return render(request, 'admin_create_blog.html', {'form': form})


def admin_edit_blog(request, pk):
    blog = get_object_or_404(Admin_Blog, pk=pk)
    if request.method == 'POST':
        form = Admin_BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('admin_blog')
    else:
        form = Admin_BlogForm(instance=blog)
    return render(request, 'admin_edit_blog.html', {'form': form})


def admin_delete_blog(request, pk):
    blog = get_object_or_404(Admin_Blog, pk=pk)
    if request.method == 'POST':
        blog.delete()
        messages.success(request, 'Blog deleted successfully!')
        return redirect('admin_blog')
    return render(request, 'admin_delete_blog.html', {'blog': blog})


def admin_blog_add(request):
    if request.method == 'POST':
        form = Admin_BlogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_blog_add')
    else:
        form = Admin_BlogForm()
    return render(request, 'admin_blog_add.html', {'form': form})


################################################################################################################################################################################################################
# User Management
def admin_student_list(request):
    students = Student.objects.all()
    return render(request, 'admin_student_list.html', {'students': students})


def admin_add_student(request):
    if request.method == 'POST':
        form = Admin_StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student added successfully.')
            return redirect('admin_student-list')
    else:
        form = Admin_StudentForm()
    return render(request, 'add_student.html', {'form': form})


def admin_edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = Admin_StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully.')
            return redirect('admin_student_management_database')
    else:
        form = Admin_StudentForm(instance=student)
    return render(request, 'admin_edit_student.html', {'form': form, 'student': student})


def admin_delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully.')
        return redirect('admin_student_management_database')
    return render(request, 'admin_delete_student.html', {'student': student})


def admin_suspend_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        # Assume there is a 'suspended' field in the Student model
        student.user.is_active = False
        student.user.save()
        messages.success(request, 'Student suspended successfully.')
        return redirect('admin_student_management_database')
    return render(request, 'admin_suspend_student.html', {'student': student})


def admin_student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'admin_student_detail.html', {'student': student})


# ---------------------------------------------------------------------------------------
# Offers View
# ---------------------------------------------------------------------------------------


def admin_offer_list(request):
    vouchers = Admin_Voucher.objects.filter(is_active=True).order_by('-start_date')
    return render(request, 'admin_offers.html', {'vouchers': vouchers})


def admin_create_voucher(request):
    if request.method == 'POST':
        form = Admin_VoucherForm(request.POST)
        if form.is_valid():
            voucher = form.save(commit=False)
            voucher.created_by = request.user
            voucher.used_count = 0  # Ensure used_count is set to 0 upon creation
            voucher.save()
            form.save_m2m()
            return redirect(reverse('admin_offer_list'))  # Redirect to the offers list view
    else:
        form = Admin_VoucherForm()

    courses = Course.objects.all()  # Fetch all courses
    return render(request, 'admin_create_voucher.html', {'form': form, 'courses': courses})


def admin_edit_voucher(request, voucher_id):
    voucher = get_object_or_404(Admin_Voucher, id=voucher_id)
    courses = Course.objects.all()
    voucher_courses = voucher.courses.values_list('id', flat=True)
    is_started = voucher.start_date <= timezone.now().date()

    if request.method == 'POST':
        end_date = request.POST.get('end_date')
        if not is_started:
            start_date = request.POST.get('start_date')
            voucher.start_date = start_date
        voucher.end_date = end_date
        voucher.save()
        messages.success(request, 'Voucher updated successfully.')
        return redirect('admin_offers_voucher')

    context = {
        'voucher': voucher,
        'courses': courses,
        'voucher_courses': voucher_courses,
        'is_started': is_started
    }
    return render(request, 'admin_edit_voucher.html', context)


def admin_pause_voucher(request, voucher_id):
    voucher = get_object_or_404(Admin_Voucher, id=voucher_id)
    voucher.is_active = False
    voucher.save()
    messages.success(request, 'Voucher has been paused successfully.')
    return redirect('admin_offers_voucher')


def admin_unpause_voucher(request, voucher_id):
    voucher = get_object_or_404(Admin_Voucher, id=voucher_id)
    voucher.is_active = True
    voucher.save()
    messages.success(request, 'Voucher has been unpaused successfully.')
    return redirect('admin_offers_voucher')


def admin_stop_voucher(request, voucher_id):
    voucher = get_object_or_404(Admin_Voucher, id=voucher_id)
    voucher.delete()
    return redirect('admin_offers_voucher')


def admin_use_voucher(request, voucher_code):
    voucher = get_object_or_404(Admin_Voucher, code=voucher_code)

    # Example of additional business logic checks
    if not voucher.is_active:
        messages.error(request, 'Voucher is inactive or expired.')
        return HttpResponseRedirect(reverse('admin_offers_voucher'))  # Redirect to the offers list view

    if voucher.start_date and voucher.start_date > timezone.now().date():
        messages.error(request, 'Voucher is not yet valid.')
        return HttpResponseRedirect(reverse('admin_offers_voucher'))  # Redirect to the offers list view

    if voucher.end_date and voucher.end_date < timezone.now().date():
        messages.error(request, 'Voucher has expired.')
        return HttpResponseRedirect(reverse('admin_offers_voucher'))  # Redirect to the offers list view

    # Increment the used count and save
    voucher.used_count += 1
    voucher.save()

    messages.success(request, 'Voucher applied successfully!')
    return HttpResponseRedirect(reverse('admin_offers_voucher'))  # Redirect to the offers list view


def admin_offers_page(request):
    vouchers = Admin_Voucher.objects.filter(is_active=True).order_by('-start_date')
    return render(request, 'admin_offers_voucher.html', {'vouchers': vouchers})


def admin_offer_list(request):
    vouchers = Admin_Voucher.objects.filter(is_active=True).order_by('-start_date')

    # Debugging: Print context data
    context = {'vouchers': vouchers}
    print("Context:", context)  # Print context data

    # Pass vouchers to the template
    return render(request, 'admin_offers_voucher.html', context)


def test_course_page(request):
    # Just fetch the first course for testing
    course = Course.objects.first()
    if course:
        youtube_videos = course.youtube_videos.all()
    else:
        youtube_videos = []

    return render(request, 'ztest_course_page.html', {
        'course': course,
        'youtube_videos': youtube_videos
    })





def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    return render(request, 'ztopic_detail.html', {'topic': topic})


import razorpay
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST

# You can remove this if not saving to DB
# from .models import Payment

# Razorpay Client Setup
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def payment(request, user_id, course_id):
    order_amount = 100  # in paise (₹1540)
    order_currency = 'INR'
    user = get_object_or_404(CustomeUser, id=user_id)
    course = get_object_or_404(Course, id=course_id)
    request.session['user_id'] = user.id
    request.session['course_id'] = course.id

    order = client.order.create({
        'amount': order_amount,
        'currency': order_currency,
        'payment_capture': '1'
    })

    context = {
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'order_id': order['id'],
        'amount': order_amount,
        'currency': order_currency,
        'user':user,
        'course':course,
    }

    return render(request, 'payment.html', context)

# def payment_page(request):
#     # Create Razorpay Order
#     order_amount = 100  # in paise (₹1540)
#     order_currency = 'INR'
#     order = client.order.create({
#         'amount': order_amount,
#         'currency': order_currency,
#         'payment_capture': '1'
#     })



#     context = {
#         'razorpay_key': settings.RAZORPAY_KEY_ID,
#         'order_id': order['id'],
#         'amount': order_amount,
#         'currency': order_currency
#     }

#     return render(request, 'payment.html', context)


@csrf_exempt
@require_POST
def verify_payment(request):
    try:
        data = request.POST

        params_dict = {
            'razorpay_order_id': data.get('razorpay_order_id'),
            'razorpay_payment_id': data.get('razorpay_payment_id'),
            'razorpay_signature': data.get('razorpay_signature')
        }

        # Verifies payment signature
        client.utility.verify_payment_signature(params_dict)

        # Fetch session data
        user_id = request.session.get('user_id')
        course_id = request.session.get('course_id')

        if not user_id or not course_id:
            return HttpResponseBadRequest("Session expired or missing user/course information.")

        user = get_object_or_404(CustomeUser, id=user_id)
        course = get_object_or_404(Course, id=course_id)
        student = Student.objects.get(user=user)
        # Save payment history
        PaymentHistory.objects.create(
            user=user,
            course_title=course.title,
            total_price=course.price,
            payment_type="Online",
            receipt_invoice=params_dict['razorpay_payment_id'],
            order_id=params_dict['razorpay_order_id'],
            payment_signature=params_dict['razorpay_signature'],
        )
        Enrollment.objects.create(
            user=student,
            course=course,
        )
        # Clear session data
        request.session.pop('user_id', None)
        request.session.pop('course_id', None)

        # Return success and redirect URL
        return JsonResponse({
            'status': 'Payment Verified Successfully',
            'redirect_url': reverse('my_learnings')
        })

    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({'status': 'Payment Verification Failed'}, status=400)

    except Exception as e:
        import traceback
        print(traceback.format_exc())  # Optional: logs detailed error in console
        return HttpResponseBadRequest(f"Error: {str(e)}")