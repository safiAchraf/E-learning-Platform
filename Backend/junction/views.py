from rest_framework import status
from rest_framework.response import Response
from django.db import IntegrityError
from .models import user, course, learner, chapitres , child_learner , child_enrolled , adult_enrolled
from rest_framework.decorators import api_view , permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group
from .permisions import IsParent, IsInstructor, IsLearner

@api_view(('GET','POST'))
@csrf_exempt
def register(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        password = request.POST["password"]
        user_type = request.POST.get("type" , "")
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
        if is_learner:
            Group.objects.get(name='learner').user_set.add(newuser)
        elif is_instructor:
            Group.objects.get(name='instructor').user_set.add(newuser)
        elif is_parent:
            Group.objects.get(name='parent').user_set.add(newuser)
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




@api_view(('GET',))
@permission_classes([IsAuthenticated])
def dashboard(request):
    if IsLearner(request.user):
        if request.method == "GET":
            courses = adult_enrolled.objects.filter(learner_id=request.user)
            courses_data = []
            for course in courses:
                courses_data.append({
                    "course_id": course.course_id.id,
                    "course_name": course.course_id.course_name ,
                    "course_description": course.course_id.course_description,
                    "course_rating": course.course_id.rating,
                    "course_duration": course.course_id.course_duration,
                    "course_price": course.course_id.course_price,
                    "course_acheivement": course.course_id.acheivement
                })

            return Response(status=status.HTTP_200_OK, data= {
                "courses": courses_data
            })
    elif IsParent(request.user):
        childs = child_learner.objects.filter(parent_id=request.user)
        childs_data = []
        for child in childs:
            childs_data.append({
                "child_id": child.id,
                "child_name": child.name ,
                "child_streak": child.streak,
                "child_score": child.score,
                "child_current_course": child.current_course.course_name
            })
        return Response(status=status.HTTP_200_OK, data= {
            "childs": childs_data
        })
    elif IsInstructor(request.user):
        if request.method == "GET":
            courses = course.objects.filter(instructor_id=request.user)
            courses_data = []
            for course in courses:
                courses_data.append({
                    "course_id": course.id,
                    "course_name": course.course_name ,
                    "course_description": course.course_description,
                    "course_rating": course.rating,
                    "course_duration": course.course_duration,
                    "course_price": course.course_price,
                    "course_acheivement": course.acheivement
                })

            return Response(status=status.HTTP_200_OK, data= {
                "courses": courses_data
            })
        elif request.method == "POST":
            course_name = request.POST["course_name"]
            course_description = request.POST["course_description"]
            course_duration = request.POST["course_duration"]
            course_price = request.POST["course_price"]
            course_acheivement = request.POST["course_acheivement"]
            newCourse = course(instructor_id=request.user, course_name=course_name, course_description=course_description, course_duration=course_duration, course_price=course_price, acheivement=course_acheivement)
            newCourse.save()
            return Response(status=status.HTTP_201_CREATED, data= {
                "message": "Course created successfully."
            })

    else:
        return Response(status=status.HTTP_403_FORBIDDEN, data= {
            "message": "You are not a learner, parent or instructor."
        })
    



@api_view(('GET','POST'))
@permission_classes([IsAuthenticated])
@csrf_exempt
def parentDashboard(request):
    if(IsParent(request.user)):
        if request.method == "GET":
            childs = child_learner.objects.filter(parent_id=request.user)
            childs_data = []
            for child in childs:
                childs_data.append({
                    "child_id": child.id,
                    "child_name": child.name ,
                    "child_streak": child.streak,
                    "child_score": child.score,
                    "child_current_course": child.current_course.course_name
                })
            return Response(status=status.HTTP_200_OK, data= {
                "childs": childs_data
            })
        if request.method == "POST":
            child_name = request.POST["name"]
            child_age = request.POST["age"]
            newChild = child_learner(parent_id=request.user, name=child_name, age=child_age)
            newChild.save()
            return Response(status=status.HTTP_201_CREATED, data= {
                "message": "Child created successfully."
            })
            
    else:
        return Response(status=status.HTTP_403_FORBIDDEN, data= {
            "message": "You are not a parent."
        })
    

@api_view(('GET','POST'))
@permission_classes([IsAuthenticated])
def courseView(request , course_id):
    pass


@api_view(('GET','POST'))
@permission_classes([IsAuthenticated])
def childView(request , child_id):
    courses = child_enrolled.objects.filter(child_id=child_id)
    courses_data = []

