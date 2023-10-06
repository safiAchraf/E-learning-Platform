from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path
from .views import register , parentDashboard , add_rating , task_View

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', register , name='auth_register'),
    #path('dashboard/',),
    path('dashboard/parent/', parentDashboard , name='parent_dashboard'),
    #path('child/<int:child_id>/', childCourses , name='child_courses'),
    #path('course/<int:course_id>/', courseDetails , name='course_details'),
    path('course/<int:course_id>/rating/', add_rating , name='chapitre_details'),
    path('task/<int:task_id>/', task_View , name='task_details'),
]