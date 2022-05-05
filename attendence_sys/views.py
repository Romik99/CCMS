from django.shortcuts import render, redirect
from django.http import HttpResponse, StreamingHttpResponse
from xlwt import Workbook
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse
from .forms import *
from .models import Student, Attendence
from .filters import AttendenceFilter
from django.core.mail import EmailMessage
from io import BytesIO
# from django.views.decorators import gzip
from django.conf import settings
from django.core.mail import send_mail
from .recognizer import Recognizer
from datetime import date
from django.http import HttpResponse  
from django.shortcuts import render, redirect    
from .forms import NewUserForm 
from django.contrib.sites.shortcuts import get_current_site  
from django.utils.encoding import force_bytes, force_str 
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  
from django.template.loader import render_to_string  
from .tokens import account_activation_token  
from django.contrib.auth.models import User  
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model

@login_required(login_url = 'login')
def home(request):
    studentForm = CreateStudentForm()

    if request.method == 'POST':
        studentForm = CreateStudentForm(data = request.POST, files=request.FILES)
        # print(request.POST)
        stat = False 
        try:
            student = Student.objects.get(registration_id = request.POST['registration_id'])
            stat = True
        except:
            stat = False
        if studentForm.is_valid() and (stat == False):
            studentForm.save()
            name = studentForm.cleaned_data.get('firstname') + " " +studentForm.cleaned_data.get('lastname')
            messages.success(request, 'Student ' + name + ' was successfully added.')
            return redirect('home')
        else:
            messages.error(request, 'Student with Registration Id '+request.POST['registration_id']+' already exists.')
            return redirect('home')

    context = {'studentForm':studentForm}
    return render(request, 'attendence_sys/home.html', context)


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or Password is incorrect')

    context = {}
    return render(request, 'attendence_sys/login.html', context)

@login_required(login_url = 'login')
def logoutUser(request):
    logout(request)
    return redirect('login')

def facultyProfile(request):
    faculty = request.user.faculty
    form = FacultyForm(instance = faculty)
    context = {'form':form}
    return render(request, 'attendence_sys/facultyForm.html', context)

@login_required(login_url = 'login')
def updateFaculty(request):
    if request.method == 'POST':
        context = {}
        try:
            faculty = request.user.faculty
            updateFacultyForm = FacultyForm(data = request.POST, files=request.FILES, instance = faculty)
            if updateFacultyForm.is_valid():
                updateFacultyForm.save()
                messages.success(request, 'Updation Success')
                return redirect('home')
        except:
            messages.error(request, 'Updation Unsucessfull')
            return redirect('home')
    return render(request, 'attendence_sys/facultyForm.html', context)


@login_required(login_url = 'login')
def updateStudentRedirect(request):
    context = {}
    if request.method == 'POST':
        try:
            reg_id = request.POST['reg_id']
            branch = request.POST['branch']
            student = Student.objects.get(registration_id = reg_id, branch = branch)
            updateStudentForm = CreateStudentForm(instance=student)
            context = {'form':updateStudentForm, 'prev_reg_id':reg_id, 'student':student}
        except:
            messages.error(request, 'Student Not Found')
            return redirect('home')
    return render(request, 'attendence_sys/student_update.html', context)

@login_required(login_url = 'login')
def updateStudent(request):
    if request.method == 'POST':
        context = {}
        try:
            student = Student.objects.get(registration_id = request.POST['prev_reg_id'])
            updateStudentForm = CreateStudentForm(data = request.POST, files=request.FILES, instance = student)
            if updateStudentForm.is_valid():
                updateStudentForm.save()
                messages.success(request, 'Updation Success')
                return redirect('home')
        except:
            messages.error(request, 'Updation Unsucessfull')
            return redirect('home')
    return render(request, 'attendence_sys/student_update.html', context)


@login_required(login_url = 'login')
def takeAttendence(request):
    if request.method == 'POST':
        details = {
            'branch':request.POST['branch'],
            'year': request.POST['year'],
            'section':request.POST['section'],
            'period':request.POST['period'],
            'faculty':request.user.faculty
            }
        if Attendence.objects.filter(date = str(date.today()),branch = details['branch'], year = details['year'], section = details['section'],period = details['period']).count() != 0 :
            messages.error(request, "Attendence already recorded.")
            return redirect('home')
        else:
            wb = Workbook()
            sheet1 = wb.add_sheet("Sheet 1", cell_overwrite_ok=True)
            sheet1.write(0, 0, 'Student ID')
            sheet1.write(0, 1, 'Branch')
            sheet1.write(0, 2, 'Year')
            sheet1.write(0, 3, 'Section')
            sheet1.write(0, 4, 'Period')
            sheet1.write(0, 5, 'Status')
            students = Student.objects.filter(branch = details['branch'], year = details['year'], section = details['section'])
            names = Recognizer(details)
            i=0
            for student in students:
                i=i+1
                if str(student.registration_id) in names:
                    attendence = Attendence(Faculty_Name = request.user.faculty, 
                    Student_ID = str(student.registration_id), 
                    period = details['period'], 
                    branch = details['branch'], 
                    year = details['year'], 
                    section = details['section'],
                    status = 'Present')
                    sheet1.write(i, 0, str(student.registration_id))
                    sheet1.write(i, 1, str(details['branch']))
                    sheet1.write(i, 2, str(details['year']))
                    sheet1.write(i, 3, str(details['section']))
                    sheet1.write(i, 4, str(details['period']))
                    sheet1.write(i, 5, 'Present')
                    attendence.save()
                else:
                    attendence = Attendence(Faculty_Name = request.user.faculty, 
                    Student_ID = str(student.registration_id), 
                    period = details['period'],
                    branch = details['branch'], 
                    year = details['year'], 
                    section = details['section'])
                    sheet1.write(i, 0, str(student.registration_id))
                    sheet1.write(i, 1, str(details['branch']))
                    sheet1.write(i, 2, str(details['year']))
                    sheet1.write(i, 3, str(details['section']))
                    sheet1.write(i, 4, str(details['period']))
                    sheet1.write(i, 5, 'Absent')
                    attendence.save()
            a="Attendance ("+str(date.today())+" "+str(details['year'])+" "+str(details['branch'])+" "+str(details['period'])+").xls"
            wb.save(a) 
            excelfile = BytesIO()
            wb.save(excelfile) 
            subject = 'JIS Attendance'
            message = " Date: "+str(date.today())+" Year: "+str(details['year'])+" Branch: "+str(details['branch'])+" Period: "+str(details['period'])
            recipient_list = [str(request.user.faculty.email)]
            mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, recipient_list)
            mail.attach('test_file.xls', excelfile.getvalue(), 'application/ms-excel')
            mail.send()
            attendences = Attendence.objects.filter(date = str(date.today()),branch = details['branch'], year = details['year'], section = details['section'],period = details['period'])
            context = {"attendences":attendences, "ta":True}
            messages.success(request, "Attendence taking Success")
            return render(request, 'attendence_sys/attendence.html', context)        
    context = {}
       
    return render(request, 'attendence_sys/home.html', context)

def searchAttendence(request):
    attendences = Attendence.objects.all()
    myFilter = AttendenceFilter(request.GET, queryset=attendences)
    attendences = myFilter.qs
    context = {'myFilter':myFilter, 'attendences': attendences, 'ta':False}
    return render(request, 'attendence_sys/attendence.html', context)


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  
            user.is_active = False  
            user.save()  
            # to get the domain of the current site  
            current_site = get_current_site(request)  
            mail_subject = 'Activation link has been sent to your email id'  
            message = render_to_string('attendence_sys/acc_active_email.html', {  
                'user': user,  
                'domain': current_site.domain,  
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),  
                'token':account_activation_token.make_token(user),  
            })  
            to_email = form.cleaned_data.get('email')  
            email = EmailMessage(  
                        mail_subject, message, to=[to_email]  
            )  
            email.send()
            messages.error(request, "Please confirm your email address to complete the registration")
            return redirect('login')
    else:  
        form = NewUserForm()  
    return render (request=request, template_name="attendence_sys/register.html", context={"register_form":form})

def activate(request, uidb64, token):  
    User = get_user_model()  
    try:  
        uid = force_str(urlsafe_base64_decode(uidb64))  
        user = User.objects.get(pk=uid)  
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):  
        user = None  
    if user is not None and account_activation_token.check_token(user, token):  
        user.is_active = True  
        user.save()
        faculty =Faculty.objects.create(user=user,user_id=user.id,firstname=user.first_name,lastname=user.last_name,email=user.email)
        faculty.save()
        return HttpResponse('Thank you for your email confirmation. Now you can login to your account. You may close this window.') 
    else:  
        return HttpResponse('Activation link is invalid!')  

# class VideoCamera(object):
#     def __init__(self):
#         self.video = cv2.VideoCapture(0)
#     def __del__(self):
#         self.video.release()

#     def get_frame(self):
#         ret,image = self.video.read()
#         ret,jpeg = cv2.imencode('.jpg',image)
#         return jpeg.tobytes()


# def gen(camera):
#     while True:
#         frame = camera.get_frame()
#         yield(b'--frame\r\n'
#         b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


# @gzip.gzip_page
# def videoFeed(request):
#     try:
#         return StreamingHttpResponse(gen(VideoCamera()),content_type="multipart/x-mixed-replace;boundary=frame")
#     except:
#         print("aborted")

# def getVideo(request):
#     return render(request, 'attendence_sys/videoFeed.html')