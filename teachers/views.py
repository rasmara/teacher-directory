from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import BulkUploadForm
from django.conf import settings
from django.db.models import Q
from .models import *
import csv
import zipfile
import os


def upload_teachers_from_csv(profiles_csv_file, images_zip_file):
    try:
        bytes_csv_content = profiles_csv_file.file.read()
        text_csv_content = bytes_csv_content.decode('UTF-8').splitlines()
        reader = csv.DictReader(text_csv_content)
        if images_zip_file is not None and zipfile.is_zipfile(images_zip_file):
            with zipfile.ZipFile(images_zip_file) as zfile:
                for t in reader:
                    if not t['Email Address']:
                        continue
                    lst_subject_obj = []
                    for data in t['Subjects taught'].upper().split(','):
                        if len(lst_subject_obj) >= 5:
                            continue
                        if not Subjects.objects.filter(subject_name=data.upper().strip()):
                            Subjects(subject_name=data.upper().strip()).save()
                            get_subject = Subjects.objects.filter(subject_name=data.upper().strip()).first()
                            lst_subject_obj.append(get_subject)
                        else:
                            get_subject = Subjects.objects.filter(subject_name=data.upper().strip()).first()
                            lst_subject_obj.append(get_subject)
                    new_teacher = Teachers(
                        first_name=t['First Name'],
                        last_name=t['Last Name'],
                        email_address=t['Email Address'],
                        phone_number=t['Phone Number'],
                        room_number=t['Room Number'],
                    )
                    new_teacher.save()
                    for item in lst_subject_obj:
                        new_teacher.subjects_taught.add(item)

                    if t['Profile picture'] not in zfile.namelist():
                        with open(os.path.join(settings.MEDIA_ROOT,
                                               'profilepic',
                                               'default.png'),
                                  'rb') as profile_picture_file:
                            new_teacher.profile_pic.save('default.png',
                                                         profile_picture_file,
                                                         True)
                    else:
                        with zfile.open(
                                t['Profile picture']) as profile_picture_file:
                            new_teacher.profile_pic.save(t['Profile picture'],
                                                         profile_picture_file,
                                                         True)

                return True
    except Exception as e:
        return False


def base(request):
    return render(request, 'index.html')


def loginview(request):
    return render(request, 'login.html')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        check_user = authenticate(username=username, password=password)
        if check_user is not None:
            auth_login(request, check_user)
            messages.success(request, 'Logged in succesfully')
            return redirect('viewall')
        messages.error(request, 'Invalid login credentials')
        return redirect('loginview')


def signuppage(request):
    return render(request, 'signup.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        get_user = User.objects.filter(username=username)
        if not get_user:
            User.objects.create_user(username=username, password=password).save()
            check_user = authenticate(username=username, password=password)
            if check_user is not None:
                auth_login(request, check_user)
                bulk_upload_form = BulkUploadForm()
                context = {"bulk_upload_form": bulk_upload_form}
                return render(request, 'createrecord.html', context)
            return render(request, 'login.html')
        messages.error(request, "User already exists")
        return redirect('loginview')


def search(request):
    if request.method == 'POST':
        search_query = request.POST.get('search_field')
        subjects_available = Subjects.objects.filter(subject_name=search_query.upper()).first()
        if search_query == "":
            messages.error(request, "Please enter a valid search query")
            return render(request, 'index.html')
        data = Teachers.objects.filter(
            Q(last_name__startswith=search_query) | Q(subjects_taught=subjects_available)).distinct()
        if not data:
            messages.warning(request, "No results found")
            return redirect('base')

        return render(request, 'searchpage.html', {'data': data})


def createrecord(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to use this feature')
        return redirect('loginview')
    bulk_upload_form = BulkUploadForm()
    context = {"bulk_upload_form": bulk_upload_form}
    return render(request, 'createrecord.html', context)


def uploadfile(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to use this feature')
        return redirect('loginview')
    bulk_upload_form = BulkUploadForm()
    if request.method == 'POST':
        bulk_upload_form = BulkUploadForm(request.POST, request.FILES)
        Teachers.objects.all().delete()
        if bulk_upload_form.is_valid():
            if upload_teachers_from_csv(request.FILES['csv_file'],
                                        request.FILES['images_archive']):
                data = Teachers.objects.all()
                messages.success(request, "Data uploaded successfully")
                return render(request, 'viewall.html', {'data': data})
            messages.error(request, "Invalid File, Please Upload the required file")
            return redirect('createrecord')


def getprofile(request, id):
    if request.method == 'GET':
        data = Teachers.objects.get(id=id)
        return render(request, 'viewprofile.html', {'data': data})


def viewall(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to use this feature')
        return redirect('loginview')
    if request.method == 'GET':
        data = Teachers.objects.all()
        return render(request, 'viewall.html', {'data': data})


def addprofileview(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to use this feature')
        return redirect('loginview')
    return render(request, 'home.html')


def addprofile(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to use this feature')
        return redirect('loginview')

    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        phonenumber = request.POST.get('phonenumber')
        roomnumber = request.POST.get('roomnumber')
        subjects = request.POST.get('subjects')
        profile_pic = request.FILES.get('myfile')

        check_teacher = Teachers.objects.filter(email_address=email)
        if check_teacher:
            messages.error(request, "user with same email id already exists")
            return redirect('addprofileview')
        subject_lst = []
        for data in subjects.upper().split(','):
            subject_lst.append(data)
            if len(subject_lst) > 5:
                messages.warning(request, "Max 5 Subjects alloted for teachers")
                return redirect('addprofileview')
        obj_teacher = Teachers(first_name=fname, last_name=lname, email_address=email, phone_number=phonenumber,
                               room_number=roomnumber)
        for data in subject_lst:
            get_subject, created = Subjects.objects.get_or_create(subject_name=data)
            obj_teacher.save()
            obj_teacher.subjects_taught.add(get_subject)
        if profile_pic:
            obj_teacher.profile_pic = profile_pic
        with open(os.path.join(settings.MEDIA_ROOT,
                               'profilepic',
                               'default.png'),
                  'rb') as profile_picture_file:
            obj_teacher.profile_pic.save('default.png',
                                         profile_picture_file,
                                         True)
        obj_teacher.save()
    messages.success(request, "Succesfully uploaded")
    return redirect('addprofileview')


def logout(request):
    auth_logout(request)
    return redirect('base')
