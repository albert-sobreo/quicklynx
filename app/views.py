from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect, render_to_response
from django.http import JsonResponse
from app.forms import aForm, aFormfromhome, LoginForm, RegisterForm, ClassroomForm, JoinClassroomForm, EditClassroomForm, EditHeaderForm, EditAccountForm, AddLectureForm, SendMessageForm
from app.models import Classroom, Professor, Student, Post, Lecture, Event, Message, Login, Account, Lecture
from passlib.hash import pbkdf2_sha256
from django.contrib.auth import logout
from django.views.decorators.cache import never_cache
import datetime
import random
import string
from django.core.mail import send_mail
from project import settings
import os
from wsgiref.util import FileWrapper
from django.utils.encoding import smart_str
import mimetypes
from django.shortcuts import get_object_or_404

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#VIEW FOR LOGIN PAGE
def login(request):
    if not request.session.is_empty():
        return render(request, 'redir.html', {})
    else:
        return render(request, "index.html", {})

#PROCESS FOR LOGGING IN
def makelogins(request):
    MyLoginForm = LoginForm(request.POST)

    if MyLoginForm.is_valid():
        email = MyLoginForm.clean_message()
        password = MyLoginForm.cleaned_data['password']
        login = Login.objects.get(email=email)

        if not pbkdf2_sha256.verify(password, login.password):
            return HttpResponse('wrong password')
        if login.category == "STUDENT":
            context = {
                'posts': Post.objects.all(),
                'events': Event.objects.all().order_by('date'),
                'account': Student.objects.select_related().get(account__login__email=email),
                'students': Student.objects.all(),
            }
            
        elif login.category == "PROFESSOR":
            context = {
                'posts': Post.objects.all(),
                'events': Event.objects.all().order_by('date'),
                'account': Professor.objects.select_related().get(account__login__email=email),
                'students': Student.objects.all(),
            }

        request.session['start'] = True
        request.session['email'] = email
        request.session['category'] = login.category
        request.session.save()

    else:
        return HttpResponse('form invalid')

    if not login.verified:
        return render(request, 'verification.html', context)

    else:
        return render(request, 'redir.html', {})

#VIEW FOR HOME PAGE
def home(request):
    if request.session.is_empty():
        return redirect('/')

    email_session = request.session.get('email')

    if email_session == None:
        return redirect('/logout/')

    login = Login.objects.get(email=email_session)
    
    if login.category == "STUDENT":
        context = {
            'posts': Post.objects.all(),
            'events': Event.objects.all().order_by('date'),
            'account': Student.objects.select_related().get(account__login__email=email_session),
            'students': Student.objects.all(),
        }
    elif login.category == "PROFESSOR":
        context = {
            'posts': Post.objects.all(),
            'events': Event.objects.all().order_by('date'),
            'account': Professor.objects.select_related().get(account__login__email=email_session),
            'students': Student.objects.all(),
        }

    return render(request, "home.html", context)

#VIEW FOR DASHBOARD PAGE
def dashboard(request):
    if request.session.is_empty():
        return redirect('/')

    email_session = request.session.get('email')

    if email_session == None:
        return redirect('/logout/')

    login = Login.objects.get(email=email_session)
    
    if login.category == "STUDENT":
        context = {
            'posts': Post.objects.all(),
            'events': Event.objects.all().order_by('date'),
            'account': Student.objects.select_related().get(account__login__email=email_session),
            'students': Student.objects.all(),
        }
    elif login.category == "PROFESSOR":
            context = {
                'posts': Post.objects.all(),
                'events': Event.objects.all().order_by('date'),
                'account': Professor.objects.select_related().get(account__login__email=email_session),
                'students': Student.objects.all(),
            }


    return render(request, 'dashboard.html', context)
    
# THIS FUNCTION CREATE POST AND SEND IT TO DATABASE
def help(request):
    myform = aForm(request.POST)
    if myform.is_valid():
        text = myform.cleaned_data['text']
        return HttpResponse(text)

    else:
        return HttpResponse(myform.errors['hello'])

#RANDOM STRING GENERATOR
def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

#PROCESS FOR REGISTERING FOR STUDENTS
def registerstudent(request):
    MyRegisterForm = RegisterForm(request.POST)

    if request.method == "POST":
        if MyRegisterForm.is_valid():
            email = MyRegisterForm.cleaned_data['email']
            password = MyRegisterForm.cleaned_data['password']
            category = "STUDENT"
            school_id = MyRegisterForm.cleaned_data['school_id']
            first_name = MyRegisterForm.cleaned_data['first_name']
            last_name = MyRegisterForm.cleaned_data['last_name']


            obj = Login.objects.all()
            for objs in obj:
                if email == objs.email:
                    return HttpResponse("Email already exists")

            login = Login()

            login.category = category
            login.email = email
            login.password = pbkdf2_sha256.encrypt(password, rounds=12000, salt_size=32)
            login.verification_string = randomString(10)
            login.verified = False
            login.save()

            send_mail(
                'Your QuickLynx Verification Code',
                login.verification_string,
                settings.EMAIL_HOST_USER,
                [login.email]
            )

            account = Account()
            
            account.first_name = first_name
            account.last_name = last_name
            account.school_id = school_id
            account.login = login
            account.save()

            student = Student()
            student.account = account
            student.save()

        else:
            return HttpResponse("FORM INVALID")

    return redirect('/')


#PROCESS FOR REGISTERING AS PROFESSOR
def registerprofessor(request):
    MyRegisterForm = RegisterForm(request.POST)

    if request.method == "POST":
        if MyRegisterForm.is_valid():
            email = MyRegisterForm.cleaned_data['email']
            password = MyRegisterForm.cleaned_data['password']
            category = "PROFESSOR"
            school_id = MyRegisterForm.cleaned_data['school_id']
            first_name = MyRegisterForm.cleaned_data['first_name']
            last_name = MyRegisterForm.cleaned_data['last_name']


            obj = Login.objects.all()
            for objs in obj:
                if email == objs.email:
                    return HttpResponse("Email already exists")

            login = Login()

            login.category = category
            login.email = email
            login.password = pbkdf2_sha256.encrypt(password, rounds=12000, salt_size=32)
            login.verification_string = 'eakdkvieoppaldkfklalebdk'
            login.verified = False
            login.save()

            account = Account()
            
            account.first_name = first_name
            account.last_name = last_name
            account.school_id = school_id
            account.login = login
            account.save()

            professor = Professor()
            professor.account = account
            professor.save()

        else:
            return HttpResponse(MyRegisterForm.errors)

    return redirect('/')

#VIEW FOR REGISTER PAGE FOR STUDENTS
def register_as_student(request):
    return render(request, "register-students.html", {})

#VIEW FOR REGISTER PAGE FOR PROFESSORS
def register_as_professor(request):
    return render(request, "register-prof.html", {})

#VIEW FOR VERIFICATION PAGE
def verification(request):
    return render(request, "verification.html", {})

#PROCESS FOR VERFICATIONS
def makeverifications(request):
    email_session = request.session.get('email')
    email = email_session
    login = Login.objects.get(email=email_session)
    login.verified = True
    login.save()

    return render(request, 'redir.html', {})

#PROCESS FOR LOGGING OUT
@never_cache
def logoutview(request):
    logout(request)
    return HttpResponseRedirect('/')

#CLASSROOM VIEW
def classroom(request, room_name, semester, year):
    if request.session.is_empty():
        return redirect('/')

    email_session = request.session.get('email')

    if email_session == None:
        return redirect('/logout/')

    login = Login.objects.get(email=email_session)
    
    if login.category == "STUDENT":
        context = {
            'posts': Post.objects.all(),
            'events': Event.objects.all().order_by('date'),
            'account': Student.objects.select_related().get(account__login__email=email_session),
            'students': Student.objects.filter(classroom__room_name=room_name),
            'classroom': Classroom.objects.get(room_name=room_name, semester=semester, year_start=year),
        }
    elif login.category == "PROFESSOR":
        context = {
            'posts': Post.objects.all(),
            'events': Event.objects.all().order_by('date'),
            'account': Professor.objects.select_related().get(account__login__email=email_session),
            'students': Student.objects.filter(classroom__room_name=room_name),
            'classroom': Classroom.objects.get(room_name=room_name, semester=semester, year_start=year),
        }

    return render(request, 'classroom.html', context)

#CLASSROOM MATERIALS VIEW
def classroommaterial(request, room_name, semester, year):
    if request.session.is_empty():
        return redirect('/')

    email_session = request.session.get('email')

    if email_session == None:
        return redirect('/logout/')

    login = Login.objects.get(email=email_session)
    
    if login.category == "STUDENT":
        context = {
            'events': Event.objects.all().order_by('date'),
            'account': Student.objects.select_related().get(account__login__email=email_session),
            'students': Student.objects.filter(classroom__room_name=room_name),
            'classroom': Classroom.objects.get(room_name=room_name, semester=semester, year_start=year),
            'lectures': Lecture.objects.select_related().filter(classroom__room_name=room_name)
        }
    elif login.category == "PROFESSOR":
        context = {
            'events': Event.objects.all().order_by('date'),
            'account': Professor.objects.select_related().get(account__login__email=email_session),
            'students': Student.objects.filter(classroom__room_name=room_name),
            'classroom': Classroom.objects.get(room_name=room_name, semester=semester, year_start=year),
            'lectures': Lecture.objects.select_related().filter(classroom__room_name=room_name)
        }

    return render(request, 'classroommaterial.html', context)

#EDIT CLASSROOM
def editclassroom(request, room_name, semester, year):
    classroom = Classroom.objects.get(room_name=room_name, semester=semester, year_start=year)
    MyEditForm = EditClassroomForm(request.POST)
    if request.method == "POST":
        if MyEditForm.is_valid():
            classroom.room_name = MyEditForm.cleaned_data['room_name']
            classroom.time_start = MyEditForm.cleaned_data['time_start']
            classroom.time_end = MyEditForm.cleaned_data['time_end']
            classroom.days = MyEditForm.cleaned_data['days']
            classroom.date_start = MyEditForm.cleaned_data['date_start']
            classroom.date_end = MyEditForm.cleaned_data['date_end']
            classroom.year_start = MyEditForm.cleaned_data['year_start']
            classroom.semester = MyEditForm.cleaned_data['semester']

            classroom.save()
        else:
            return HttpResponse('form invalid')
    return redirect('/classroom/{}/{}/{}'.format(classroom.room_name,classroom.semester,classroom.year_start))


#PROCESS FOR CREATING ROOMS
def makeclassroom(request):
    email = request.session.get('email')
    category = request.session.get('category')
    if category == 'STUDENT':
        acct = Student.objects.select_related().get(account__login__email=email)
    elif category == 'PROFESSOR':
        acct = Professor.objects.select_related().get(account__login__email=email)

    MyRoomForm = ClassroomForm(request.POST, request.FILES)
    if request.method == "POST":
        if MyRoomForm.is_valid():
            room_name = MyRoomForm.cleaned_data['room_name']
            time_start= MyRoomForm.cleaned_data['time_start']
            time_end =  MyRoomForm.cleaned_data['time_end']
            days     =  MyRoomForm.cleaned_data['days']
            date_start= MyRoomForm.cleaned_data['date_start']
            date_end =  MyRoomForm.cleaned_data['date_end']
            year_start= MyRoomForm.cleaned_data['year_start']
            semester =  MyRoomForm.cleaned_data['semester']
            headerpix = MyRoomForm.cleaned_data['headerpix']

            classroom = Classroom()

            classroom.room_name = room_name
            classroom.time_start = time_start
            classroom.time_end = time_end
            classroom.days = days
            classroom.date_start = date_start
            classroom.date_end = date_end
            classroom.year_start = year_start
            classroom.year_end = year_start
            classroom.semester = semester
            classroom.headerpix = headerpix
            classroom.invite_token = randomString(20)
            classroom.save()
            
            acct.classroom.add(classroom)
        else:
            return HttpResponse(MyRoomForm.errors)

    return redirect('/classroom/'+ room_name + '/' + semester + '/' + year_start)

    

def makepost(request, room_name):
    email = request.session.get('email')
    category = request.session.get('category')
    if category == 'STUDENT':
        acct = Student.objects.select_related().get(account__login__email=email)
    elif category == 'PROFESSOR':
        acct = Professor.objects.select_related().get(account__login__email=email)

    MyPostForm = aForm(request.POST)
    if request.method == "POST":
        if MyPostForm.is_valid():
            text = MyPostForm.cleaned_data['text']

            post = Post()

            post.text = text
            post.date = datetime.datetime.now()
            account = acct.account
            post.account = account
            post.classroom = Classroom.objects.get(room_name=room_name)
            post.save()
    
    return redirect('/classroom/{}'.format(room_name))

def makepostfromhome(request):
    email = request.session.get('email')
    category = request.session.get('category')
    if category == 'STUDENT':
        acct = Student.objects.select_related().get(account__login__email=email)
    elif category == 'PROFESSOR':
        acct = Professor.objects.select_related().get(account__login__email=email)

    MyPostForm = aFormfromhome(request.POST)
    if request.method == "POST":
        if MyPostForm.is_valid():
            print('the form is valid')
            text = MyPostForm.cleaned_data['text']
            classroom = MyPostForm.cleaned_data['classroom']

            post = Post()
            classroom = classroom.split()
            post.text = text
            post.date = datetime.datetime.now()
            account = acct.account
            post.account = account
            post.classroom = Classroom.objects.get(room_name=classroom[0], semester=classroom[1], year_start=classroom[2])
            post.save()
        else:
            return HttpResponse("select a classroom")
    return redirect('/home/')

#PROCESS TO JOIN ROOM
def joinclassroom(request):
    email = request.session.get('email')
    category = request.session.get('category')
    if category == 'STUDENT':
        acct = Student.objects.select_related().get(account__login__email=email)
    elif category == 'PROFESSOR':
        acct = Professor.objects.select_related().get(account__login__email=email)

    MyJoinForm = JoinClassroomForm(request.POST)
    if request.method == "POST":
        if MyJoinForm.is_valid():
            token = MyJoinForm.cleaned_data['token']

            classroom = get_object_or_404(Classroom, invite_token=token)
            acct.classroom.add(classroom)

        else:
            return HttpResponse(MyJoinForm.errors)
    
    return redirect('/dashboard/')

#UPVOTE
def upvote(request, post_id):
    email = request.session.get('email')
    category = request.session.get('category')
    if category == 'STUDENT':
        acct = Student.objects.select_related().get(account__login__email=email)
    elif category == 'PROFESSOR':
        acct = Professor.objects.select_related().get(account__login__email=email)

    post = Post.objects.get(id=post_id)
    if post not in acct.upvoted_post.all():
        acct.upvoted_post.add(post)
        post.upvotes += 1
        post.save()
    
    else:
        acct.upvoted_post.remove(post)
        post.upvotes -= 1
        post.save()
    # if category == "STUDENT":
    #     context = {
    #         'posts': Post.objects.all(),
    #         'events': Event.objects.all(),
    #         'account': Student.objects.select_related().get(account__login__email=email),
    #         'students': Student.objects.all()
    #     }
    # elif category == "PROFESSOR":
    #     context = {
    #         'posts': Post.objects.all(),
    #         'events': Event.objects.all(),
    #         'account': Professor.objects.select_related().get(account__login__email=email),
    #         'students': Student.objects.all()
    #     }
    return JsonResponse({'success': 'true'})

def downvote(request, post_id):
    email = request.session.get('email')
    category = request.session.get('category')
    if category == 'STUDENT':
        acct = Student.objects.select_related().get(account__login__email=email)
    elif category == 'PROFESSOR':
        acct = Professor.objects.select_related().get(account__login__email=email)

    post = Post.objects.get(id=post_id)
    if post not in acct.downvoted_post.all():
        acct.downvoted_post.add(post)
        post.downvotes -= 1
        post.save()
    
    else:
        acct.downvoted_post.remove(post)
        post.downvotes += 1
        post.save()
    if category == "STUDENT":
        context = {
            'posts': Post.objects.all(),
            'events': Event.objects.all(),
            'account': Student.objects.select_related().get(account__login__email=email),
            'students': Student.objects.all()
        }
    elif category == "PROFESSOR":
        context = {
            'posts': Post.objects.all(),
            'events': Event.objects.all(),
            'account': Professor.objects.select_related().get(account__login__email=email),
            'students': Student.objects.all()
        }
    return JsonResponse(context)

#EDIT HEADER
def editheader(request, room_name):
    classroom = Classroom.objects.get(room_name=room_name)
    MyHeaderForm = EditHeaderForm(request.POST, request.FILES)
    if request.method == "POST":
        if MyHeaderForm.is_valid():
            if os.path.isfile(BASE_DIR + str(classroom.headerpix.url)):
                os.remove(BASE_DIR + str(classroom.headerpix.url))
                print("path remove")
            classroom.headerpix = MyHeaderForm.cleaned_data['headerpix']
            classroom.save()
        else:
            return HttpResponse("FORM INVALID")
    return redirect('/classroom/'+room_name)


def editaccount(request):
    email = request.session.get('email')
    account = Account.objects.select_related().get(login__email=email)
    MyAccountForm = EditAccountForm(request.POST)
    if request.method == "POST":
        if MyAccountForm.is_valid():
            account.first_name = MyAccountForm.cleaned_data['first_name']
            account.last_name = MyAccountForm.cleaned_data['last_name']
            account.save()
        else:
            return HttpResponse(MyAccountForm.errors)
    
    return redirect('/home/')


def download(request, file_name):
    file_path = settings.MEDIA_ROOT + '/media/' + file_name
    file_wrapper = FileWrapper(open(file_path, 'rb'))
    file_mimetype = mimetypes.guess_type(file_path)
    response = HttpResponse(file_wrapper, content_type=file_mimetype)
    response['X-Sendfile'] = file_path
    response['Content-Length'] = os.stat(file_path).st_size
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    return response


def addlecture(request, room_name):
    email = request.session.get('email')
    category = request.session.get('category')
    if category == 'STUDENT':
        acct = Student.objects.select_related().get(account__login__email=email)
    elif category == 'PROFESSOR':
        acct = Professor.objects.select_related().get(account__login__email=email)

    MyLectureForm = AddLectureForm(request.POST, request.FILES)
    if request.method == "POST":
        if MyLectureForm.is_valid():
            lecture = Lecture()

            lecture.no = MyLectureForm.cleaned_data['no']
            lecture.title = MyLectureForm.cleaned_data['title']
            lecture.file_loc = MyLectureForm.cleaned_data['file_loc']
            lecture.date = datetime.datetime.now()
            account = acct.account
            lecture.account = account
            lecture.classroom = Classroom.objects.get(room_name=room_name)
            lecture.save()
        else:
            return HttpResponse("form invalid")
    return redirect('/classroom/'+room_name)
    

def messages(request):
    email_session = request.session['email']
    account = Account.objects.select_related().get(login__email=email_session)
    category = request.session.get('category')
    if category == 'STUDENT':
        context = {
        'account': Student.objects.select_related().get(account__login__email=email_session),
        'messagess': Message.objects.filter(message_to=account),
        'allaccounts': Account.objects.all()
    }
    elif category == "PROFESSOR":
        context = {
            'account': Professor.objects.select_related().get(account__login__email=email_session),
            'messagess': Message.objects.filter(message_to=account),
            'allaccounts': Account.objects.all()
        }
    return render(request, 'messages.html', context)


def messagecontent(request, message_id):
    email_session = request.session['email']
    account = Account.objects.select_related().get(login__email=email_session)
    messagecontent = Message.objects.filter(id=message_id).values()
    for x in messagecontent:
        pass
    context={
        'messagecontent': list(messagecontent)
    }
    return JsonResponse(x)


def outbox(request):
    email_session = request.session['email']
    account = Account.objects.select_related().get(login__email=email_session)
    category = request.session.get('category')
    if category == 'STUDENT':
        context = {
        'account': Student.objects.select_related().get(account__login__email=email_session),
        'messagess': Message.objects.filter(message_from=account),
        'allaccounts': Account.objects.all()
    }
    elif category == "PROFESSOR":
        context = {
            'account': Professor.objects.select_related().get(account__login__email=email_session),
            'messagess': Message.objects.filter(message_from=account),
            'allaccounts': Account.objects.all()
        }
    return render(request, 'outbox.html', context)


def sendmessage(request):
    email_session = request.session.get('email')
    account = Account.objects.select_related().get(login__email=email_session)
    MyMsgForm = SendMessageForm(request.POST)
    if request.method == "POST":
        if MyMsgForm.is_valid():
            message = MyMsgForm.cleaned_data['message']
            to = MyMsgForm.cleaned_data['to']
            subject = MyMsgForm.cleaned_data['subject']

            msg = Message()

            msg.message = message
            msg.subject = subject
            msg.message_from = account
            msg.message_to = Account.objects.select_related().get(login__email=to)
            msg.date = datetime.datetime.now()

            msg.save()

    return redirect('/message/')

def addeventfromdash(request, page):
    email = request.session.get('email')
    category = request.session.get('category')

    if request.method == "POST":
        event = Event()

        classroom = request.POST['classroom']
        classroom = classroom.split()

        event.title = request.POST['title']
        event.date = datetime.datetime.strptime(request.POST['date'], '%Y-%m-%d')
        event.description = request.POST['desc']
        account = Professor.objects.select_related().get(account__login__email=email)
        event.account = account.account
        print(classroom)
        event.classroom = Classroom.objects.get(room_name=classroom[0], semester=classroom[1], year_start=classroom[2])

        event.save()

    else:
        return HttpResponse("invalid")
    if page == "home":
        return redirect('/')
    elif page == "dash":
        return redirect('/dashboard/')
    else:
        page = page.split()
        return redirect('/classroom/' + page[0] + '/' + page[1] + '/' + page[2]) 