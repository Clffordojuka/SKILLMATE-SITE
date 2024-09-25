import cloudinary
import cloudinary.uploader
import cloudinary.api

from django.shortcuts import render, redirect

from django.utils.text import slugify
from .models import Course, Enrollment

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required

from .forms import CourseEditForm

from django.contrib import messages

import pytz

from allauth.account.signals import user_signed_up

from django.dispatch import receiver
from django.conf import settings
from .sendMail import *
# import user
from django.contrib.auth.models import User

def signup_request(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password1']
        
        # Check if the username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose a different one.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
        else:
            try:
                # Create and save the new user
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # Prepare the welcome email
                subject = "Welcome to our platform!"
                message = f"Hi {username},\n\nThank you for signing up!"
                message += "\n\nYou can now access all the courses on our platform."
                message += "\n\nBest regards,\nSkillmate Team"
                
                # Send the email using your EmailClient instance
                email_client.send_email(email, subject, message)

                messages.success(request, "Your account was created successfully, and a welcome email has been sent!")
                # navigate to the login page
                return redirect('account_login')
            
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
    
    return render(request, 'account/signup.html')

def index(request):
    courses = Course.objects.all()[:6]
    return render(request, 'index.html', {'courses': courses})


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def courses(request):
    courses = Course.objects.all()
    return render(request, 'courses.html', {'courses': courses})

# def profile(request):
#     user = request.user
#     if user.is_authenticated:
#         # get first and last name
#         first_name = user.first_name
#         last_name = user.last_name

#         # get username and email
#         username = user.username
#         email = user.email

#         # get profile picture
#         profile_picture = None
#         if hasattr(user, 'profile'):
#             profile_picture = user.profile.picture

#         return render(request, 'account/dashboard/profile.html', {'first_name': first_name, 'last_name': last_name, 'username': username, 'email': email, 'profile_picture': profile_picture})
#     else:
#         return redirect('account_login')


def dashboard_home(request):
    user = request.user
    courses_uploaded = Course.objects.filter(instructor=user)
    print(f'Courses uploaded: {courses_uploaded}')
    num_courses_uploaded = courses_uploaded.count()
    print(f'Number of courses uploaded: {num_courses_uploaded}')
    courses_enrolled = Course.objects.filter(students=user)
    print(f'Courses enrolled: {courses_enrolled}')
    num_courses_enrolled = courses_enrolled.count()
    print(f'Number of courses enrolled: {num_courses_enrolled}')
    num_students = Enrollment.objects.filter(course__in=courses_uploaded).values('student').distinct().count()
    print(f'Number of students: {num_students}')
    instructor = request.user
    courses = Course.objects.filter(instructor=instructor)

    enrollments = []
    ist_tz = pytz.timezone('Asia/Kolkata')

    for course in courses:
        course_enrollments = Enrollment.objects.filter(course=course)
        for enrollment in course_enrollments:
            student = enrollment.student
            enrollment_date_ist = enrollment.enrolled_at.astimezone(ist_tz)
            enrollment_date = enrollment_date_ist.strftime('%d %B %Y %H:%M:%S')
            enrollments.append({'course_title': course.title, 'student_name': student.username, 'enrollment_date': enrollment_date})

    context = {
        'courses_uploaded': courses_uploaded,
        'num_courses_uploaded': num_courses_uploaded,
        'num_courses_enrolled': num_courses_enrolled,
        'num_students': num_students,
        'enrollments': enrollments,
    }
    return render(request, 'dashboard/home.html', context)


def profile(request):
    user = request.user
    email = user.email
    full_name = f"{user.first_name} {user.last_name}"
    username = user.username
    return render(request, 'dashboard/profile.html', {'email': email, 'full_name': full_name, 'username': username})


def courses_enrolled(request):
    user = request.user
    courses = Course.objects.filter(students=user)
    context = {
        'courses': courses
    }
    return render(request, 'dashboard/courses-enrolled.html', context)


def courses_uploaded(request):
    courses = Course.objects.filter(instructor=request.user)
    return render(request, 'dashboard/courses-uploaded.html', {'courses': courses})

@login_required
def upload(request):
    if request.method == 'POST':
        # Get course details from the form
        title = request.POST['title']
        description = request.POST['description']
        thumbnail = request.FILES['thumbnail']
        featured_video = request.FILES['featured_video']
        instructor = request.user
        duration = request.POST['duration']
        level = request.POST['level']
        requirements = request.POST['requirements']
        content = request.POST['content']
        category = request.POST['category']
        price = int(request.POST['price'])
        discount = int(request.POST['discount'])

        lesson_title = request.POST['lesson_title']
        lesson_video = request.FILES['lesson_video']

        discounted_price = (discount/100)*price
        price = price-discounted_price

        # Split requirements and content into lists
        requirements_list = [r.strip() for r in requirements.split(', ')]
        content_list = [c.strip() for c in content.split(', ')]

        # Upload thumbnail and featured video to Cloudinary
        thumbnail_upload = cloudinary.uploader.upload(thumbnail)
        featured_video_upload = cloudinary.uploader.upload(
            featured_video, resource_type="video")

        # Upload lesson videos to Cloudinary
        lesson_video_upload = cloudinary.uploader.upload(
            lesson_video, resource_type="video")

        # Create a new Course object with the given details
        course = Course(
            title=title,
            description=description,
            thumbnail=thumbnail_upload['secure_url'],
            featured_video=featured_video_upload['secure_url'],
            instructor=instructor,
            duration=duration,
            level=level,
            requirements=requirements_list,
            content=content_list,
            category=category,
            price=price,
            discount=discount,
            lesson_title=lesson_title,
            lesson_video=lesson_video_upload['secure_url'],
            )
        course.save()

    return render(request, 'dashboard/upload.html')


# def course_details(request, instructor, slug):
#     instructor_obj = get_object_or_404(User, username=instructor)
#     course = get_object_or_404(Course, slug=slug, instructor=instructor_obj)
#     context = {
#         'course': course
#     }
#     return render(request, 'course.html', context)

def course_details(request, instructor, slug):
    instructor_obj = get_object_or_404(User, username=instructor)
    course = get_object_or_404(Course, slug=slug, instructor=instructor_obj)
    category_courses = Course.objects.filter(category__iexact=course.category).exclude(id=course.id)[:3]

    enrolled = False
    
    if request.user.is_authenticated:
        enrolled = course.students.filter(id=request.user.id).exists()

    if request.method == 'POST' and not enrolled:
        user = request.user
        course.students.add(user)
        enrollment = Enrollment(student=user, course=course)
        enrollment.save()
        messages.success(request, 'You have enrolled in this course!')
        return redirect('course_details', instructor=instructor, slug=slug)

    context = {
        'course': course,
        'enrolled': enrolled,
        'category_courses': category_courses
    }
    return render(request, 'course.html', context)

@login_required
def course_edit(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    if request.method == 'POST':
        form = CourseEditForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
    else:
        form = CourseEditForm(instance=course)
    return render(request, 'dashboard/course-edit.html', {'form': form, 'course': course})

@login_required
def delete_course(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    if request.method == 'POST':
        course.delete()
        return redirect('/dashboard/courses-uploaded')
    context = {
        'course': course,
    }
    return render(request, 'dashboard/course-edit.html', context)

def category(request, category):
    courses = Course.objects.filter(category__iexact=category)
    context = {
        'category': category,
        'courses': courses
    }
    return render(request, 'category.html', context)


import google.generativeai as genai
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
# Configure the API key for authentication
genai.configure(api_key="AIzaSyDmVgtBtEqHyCPhEL4naok1ZjRdRmdB7iI")
model = genai.GenerativeModel('gemini-1.5-flash')


@csrf_exempt  # Use this only for testing; consider proper CSRF handling for production
def generate_text(request):
    if request.method == "POST":
        try:
            # Read the JSON body
            body = json.loads(request.body)
            user_input = body.get('user_input', '')
        except json.JSONDecodeError:
            return JsonResponse({'response_text': 'Invalid JSON'}, status=400)

        prompt = f"You are a helpful assistant for Udemy Academy. Answer the following question: {user_input}"
        print(f"Prompt: {prompt}")

        # Generate content using the AI model
        response = model.generate_content(prompt)

        # Extract the text from the response
        try:
            response_text = response.candidates[0].content.parts[0].text
        except (IndexError, AttributeError):
            response_text = "Sorry, I couldn't generate a response."

        return JsonResponse({'response_text': response_text})

    return JsonResponse({'response_text': ''})