from django.urls import path, include
from exam.views import *
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('results/<int:exam_id>/', results),
    path('detail_results/<int:exam_id>/', detail_results),
    path('<int:exam_id>/', exam),
    path('new', new_exam),
    path('api/', api),
    path("user_exams/<str:username>/", admin_user_results),
    path("get_user_id/<str:first_name>/<str:last_name>/<str:email>/", get_user_id),
    path("rating", rating),
    path("registration", registration),
    path("authentication", authentication),
    path("logout", logout),
    path("categories", categories),
    path("passwordrecovery", password_recovery),
    path("gettheme", get_theme)
]
