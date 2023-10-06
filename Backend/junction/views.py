
from rest_framework import status
from rest_framework.response import Response
from django.db import IntegrityError
from .models import user, course, learner, chapitres
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(('GET','POST'))
@csrf_exempt
def register(request):
    if request.method == "POST":
        print(request.POST)
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        
        password = request.POST["password"]
        
        user_type = request.POST.get("user_type" , "")
        
        is_parent = False
        is_learner = False
        is_instructor = False
        if user_type == "parent":
            is_parent = True
        elif user_type == "learner":
            is_learner = True
        elif user_type == "instructor":
            is_instructor = True
        

        # Attempt to create new user
        try:
            newuser = user.objects.create_user(email , password, first_name=first_name, last_name=last_name, is_parent=is_parent , is_learner=is_learner, is_instructor=is_instructor)
            newuser.save()
        except IntegrityError as e:
            
            return Response(status=status.HTTP_400_BAD_REQUEST, data= {
                "message": "Email address already taken."
            })
        refresh = RefreshToken.for_user(newuser)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        return Response(status=status.HTTP_201_CREATED, data= {
            "message": "User created successfully.",
            "access_token": access_token,
            "refresh_token": refresh_token
        })
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST , data= {
            "message": "POST request required."
        })


    