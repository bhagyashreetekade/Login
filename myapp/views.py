from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail,EmailMessage
from django.contrib import messages
from django.contrib.auth.models import User
from Login import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from . tokens import generate_token
# Create your views here.

def index(request):
    return render(request,'myapp/index.html')


def home(request):
    return render(request,'myapp/home.html')

def signup(request):
    if request.method == "POST":
        username=request.POST.get('username')
        email=request.POST.get('email')
        pass1=request.POST.get('pass1')
        pass2=request.POST.get('pass2')

        #Validations for app like if the user is already exist in database user will create a new account
        if User.objects.filter(username=username):
            messages.error(request,"User name already exist..Please try some other username...")
            return redirect("signup")

        if User.objects.filter(email=email):
            messages.error(request,"Email already exist...")
            return redirect("signup")

        if len(username)>10:
            messages.error(request,"Username must be under 10 characters...")
            return redirect("signup")

        if pass1 != pass2:
            messages.error(request,"Passwords didnt match")
        
        if not username.isalnum():
            messages.error(request,"Username must be alpha numeric")
            return redirect("signup") 

        #create a object of User 
        myuser=User.objects.create_user(username,email,pass1)
        myuser.is_active=False
        #save the user in databse
        myuser.save()
        messages.success(request,"Your account is successfully created.We have send an confirmation email ,please confirm your email in order to activate your account")
        #As soon as the user registered himself they should redirected to the login page

        #send emails
        subject= "Welcome to Code Area"
        message="Hello"+ myuser.username + "!! \n"+ "Welcome to Code Area !!!\n Thank You for visting our website \n We have also send you a confirmation email ,please confirmn your email address in order to activate your account \n\n Thanking You\n XYZ"
        #the email from which the email is to be send
        from_email=settings.EMAIL_HOST_USER
        #to whom the email to be send
        recipient_list=[myuser.email]
        #fail_silently means the email fails to send it will do not the app crash
        send_mail(subject,message,from_email,recipient_list,fail_silently=True)

        #Code for Confirmation Email 
        #take current site which is whether the site is working on the local host or where it is deployed ..it will take the domain of that
        current_site= get_current_site(request)
        email_subject="Confirm your email @ CodeArea -Django Login!!"
        message2=render_to_string('email_confirmation.html',{

            'name':myuser.first_name,
            'domain':current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token':generate_token.make_token(myuser),  #generator a token using myuser and primary key 
        })

        email=EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently=True
        email.send()
        return redirect('signin') 
    return render(request,'myapp/signup.html')

def signin(request):
    if request.method == "POST":
        username=request.POST.get('username')
        pass1=request.POST.get('pass1')

        #authenticate the user so that the django will authenticate the user & check whether the user present in he database or not
        user=authenticate(username=username,password=pass1)

        # it return a none response if the user is not authenticate 
        if user is not None:
            login(request,user)
            username=user.username
            return render(request,"myapp/home.html",{'firstname': username})

        else:
            messages.error(request,"Bad Credentials")
            return redirect('index')

    return render(request,'myapp/index.html')

#new function to activate the account of the user

def activate(request,uidb64,token):
    try:
        #force_str is used to encode the code & check that the code is given to the particular user or not
        uid=force_str(urlsafe_base64_decode(uidb64))
        #fetch the single user whose primary key is particular uid
        myuser=User.objects.get(pk=uid)
    
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser=None
    
    #validate
    if myuser is not None and generate_token.check_token(myuser,token):
        #We activate the user as during sign up we said that myuser.is_active is false..As soon as the user the click on the confirmtion link all the credentials likea user id and token is correct we activate the account
        myuser.is_active=True
        myuser.save()
        login(request,myuser)
        return redirect('home')
    else:
        return render(request,'activation_failed.html')