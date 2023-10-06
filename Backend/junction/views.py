from rest_framework import status
from rest_framework.response import Response
from django.db import IntegrityError
from .models import user, course, child_learner , child_enrolled , adult_enrolled , tasks , videos , Rating , messages , user_interests , Interests
from rest_framework.decorators import api_view , permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group
from .permisions import IsParent, IsInstructor, IsLearner
import json

@api_view(('GET','POST'))
@csrf_exempt
def register(request):
    if request.method == "POST":
        data = json.loads(request.body)
        full_name = data["name"]
        email = data["email"]
        password = data["password"]
        number = data["number"]
        user_type = data["type"]
        
        is_parent = False
        is_learner = False
        is_instructor = True
        if user_type == "Parental Account":
            is_parent = True
            is_instructor = False
        elif user_type == "Personal Account":
            is_instructor = False
            is_learner = True
        
        
        # Attempt to create new user
        try:
            newuser = user.objects.create_user(email , password, full_name = full_name, is_parent=is_parent , is_learner=is_learner, is_instructor=is_instructor , phone_number=number)
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

        interests = request.POST.getlist("interests" , "")
        for interest in interests:
            if not Interests.objects.filter(interest_name=interest).exists():
                newInterest = Interests(interest_name=interest, interest_description="No description")
                newInterest.save()
                newInterest = user_interests(user_id=newuser, interest_id=newInterest)
                newInterest.save()
            else:
                newInterest = Interests.objects.get(interest_name=interest)
                newInterest = user_interests(user_id=newuser, interest_id=newInterest)
                newInterest.save()
        
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


@api_view(('GET','POST'))
@permission_classes([IsAuthenticated])
@csrf_exempt
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
                    "course_rating": course.course_rating,
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
    if request.method == 'GET':
        allTasks = tasks.objects.filter(course_id=course_id)
        tasks_data = []
        for task in allTasks:
            tasks_data.append({
                "task_id": task.id,
                "task_title": task.task_title ,
                "task_description": task.task_description,
                "question": task.question,
                "answer": task.answer
            })
        videoos = videos.objects.filter(course_id=course_id)
        videoos_data = []
        for video in videoos:
            videoos_data.append({
                "video_id": video.id,
                "video_url": video.video_url ,
                "video_title": video.video_title
            })
        allMessages = messages.objects.filter(course_id=course_id , responded=True)
        messages_data = []
        for message in allMessages:
            messages_data.append({
                "message_id": message.id,
                "message_title": message.message_title ,
                "message_body": message.message_body,
                "message_time": message.time
            })
        

        return Response(status=status.HTTP_200_OK, data= {
            "tasks": tasks_data,
            "videos": videoos_data,
            "messages": messages_data
        })
    
    elif request.method == 'POST':
        if IsInstructor(request.user):
            material_type = request.POST["material_type"]
            if material_type == "task":
                task_title = request.POST["task_title"]
                task_description = request.POST["task_description"]
                question = request.POST["question"]
                answer = request.POST["answer"]
                for receiver in adult_enrolled.objects.filter(course_id=course_id):
                    newtask= tasks(course_id=course_id, task_title=task_title, task_description=task_description, question=question, answer=answer , learner_id=receiver.learner_id)
                    newtask.save()
                for receiver in child_enrolled.objects.filter(course_id=course_id):
                    newtask = tasks(course_id=course_id, task_title=task_title, task_description=task_description, question=question, answer=answer , learner_id=receiver.child_id)
                    newtask.save()

                return Response(status=status.HTTP_201_CREATED, data= {
                    "message": "Quiz created successfully."
                })
            elif material_type == "video":
                video_url = request.POST["video_url"]
                video_title = request.POST["video_title"]
                newVideo = videos(course_id=course_id, video_url=video_url, video_title=video_title)
                newVideo.save()
                return Response(status=status.HTTP_201_CREATED, data= {
                    "message": "Video created successfully."
                })
            
        else:
            return Response(status=status.HTTP_403_FORBIDDEN, data= {
                "message": "You are not an instructor."
            })


@api_view(('GET','POST'))
@permission_classes([IsAuthenticated])
def childView(request , child_id):
    courses = child_enrolled.objects.filter(child_id=child_id)
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

@api_view(('GET','POST'))
@permission_classes([IsAuthenticated])
def child_tasks_View(request , child_id):
    if request.method == 'GET':
        allTasks = tasks.objects.filter(learner_id=child_id)
        tasks_data = []
        count = 0
        for task in tasks:
            tasks_data.append({
                "task_id": task.id,
                "task_title": task.task_title ,
                "task_description": task.task_description,
                "question": task.question, 
                "answer": task.answer,
                "done": task.done
            })
            if not task.done:
                count += 1
        return Response(status=status.HTTP_200_OK, data= {
            "tasks": tasks_data,
            "uncompleted_tasks": count
        })



@api_view(('GET','POST'))
@permission_classes([IsAuthenticated])
@csrf_exempt
def task_View(request , task_id):
    if request.method == 'GET':
        task = tasks.objects.get(id=task_id)
        task_data = {
            "task_id": task.id,
            "task_title": task.task_title ,
            "task_description": task.task_description,
            "question": task.question,
            "answer": task.answer,
            "done": task.done
        }
        return Response(status=status.HTTP_200_OK, data= {
            "task": task_data
        })
    elif request.method == 'POST':
        task_id = request.POST["task_id"]
        task = tasks.objects.get(id=task_id)
        task.done = True
        task.save()
        return Response(status=status.HTTP_200_OK, data= {
            "message": "Task done successfully."
        })
    


@api_view(('GET','POST'))
@permission_classes([IsAuthenticated])
@csrf_exempt
def add_rating(request , course_id):
    if request.method == 'POST':
        Course = course.objects.get(id=course_id)
        userRating = request.POST["rating"]
        if Rating.objects.filter(course_id=course_id , user_id=request.user).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST, data= {
                "message": "You already rated this course."
            })
        newRating = Rating(course_id=course_id, user_id=request.user, rating=userRating)
        newRating.save()
        if Course.rating == 0:
            course.rating = userRating
        else:
            course.rating = (course.rating + request.POST["rating"])/2
        course.save()
        return Response(status=status.HTTP_200_OK, data= {
            "message": "Rating added successfully."
        })
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST, data= {
            "message": "POST request required."
        })
    
@api_view(('GET','POST'))
@permission_classes([IsAuthenticated])
@csrf_exempt
def messagesView(request , course_id):
    if request.method == 'GET' and IsInstructor(request.user):
        allMessages = messages.objects.filter(course_id=course_id)
        messages_data = []
        for message in allMessages:
            messages_data.append({
                "message_id": message.id,
                "message_title": message.message_title ,
                "message_description": message.message_description,
                "message_date": message.message_date,
                "message_time": message.message_time
            })
        return Response(status=status.HTTP_200_OK, data= {
            "messages": messages_data
        })
    elif request.method == 'POST':
        message_title = request.POST["message_title"]
        message_description = request.POST["message_body"]
        instructor = course.objects.get(id=course_id).instructor_id
        newMessage = messages(course_id=course_id, message_title=message_title, message=message_description , sender_id=request.user, receiver_id= instructor)
        newMessage.save()
        return Response(status=status.HTTP_201_CREATED, data= {
            "message": "Message created successfully."
        })
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED, data= {
            "message": "Method not allowed."
        })
    

@api_view(('GET','POST'))
@permission_classes([IsAuthenticated])
@csrf_exempt
def message_response(request , message_id):
    if request.method == 'GET':
        message = messages.objects.get(id=message_id)
        message_data = {
            "message_id": message.id,
            "message_title": message.message_title ,
            "message_description": message.message_body,
            "message_time": message.time
        }
        return Response(status=status.HTTP_200_OK, data= {
            "message": message_data
        })
    elif request.method == 'POST':
        oldMessage = messages.objects.get(id=message_id)
        message_description = request.POST["message_body"]
        oldMessage.message_body += "\n" + message_description
        oldMessage.responded = True
        oldMessage.save()



    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED, data= {
            "message": "Method not allowed."
        })


    

