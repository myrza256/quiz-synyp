from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.models import User
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from exam.models import *
from hashlib import md5
from uuid import uuid4
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import smtplib
import datetime

from exam.api import *


def send_mail(send_to, subject, text):
    assert isinstance(send_to, list)
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    msg = MIMEMultipart()
    msg['From'] = "toxicman.20041@gmail.com"
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(text, "html"))
    server.login("toxicman.20041@gmail.com", "pussyslayer2004")
    try:
        server.sendmail("toxicman.20041@gmail.com", send_to, msg.as_string())
    except smtplib.SMTPRecipientsRefused:
        return "Адрес электронной почту указан неверно"
    server.close()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def rating(request):
    users = dict()
    for result in ExamResult.objects.all():
        if result.user.id in users.keys():
            users[result.user.id] += result.result
        else:
            users[result.user.id] = result.result
    rating_ = []
    for id_ in users.keys():
        points = users[id_]
        user_ = User.objects.get(id=id_)
        rating_.append({
            "name": user_.first_name,
            "surname": user_.last_name,
            "points": points
        })
    rating_ = sorted(rating_, key=lambda x: x["points"], reverse=True)
    for i in range(len(rating_)):
        rating_[i]["number"] = i + 1
    data = {"rating": rating_}
    return render(request, "rating.html", data)


def exam(request, exam_id):
    # if request.method == "GET":
    #     if len(Exam.objects.filter(id=exam_id)) == 1:
    #         if Exam.objects.get(id=exam_id).user_id != request.user.id:
    #             return HttpResponseRedirect('https://insynyp.online')
    #
    #     else:
    #         return HttpResponseRedirect('https://insynyp.online')
    exam_data = {"exam": get_exam(exam_id)}
    return render(request, "exam.html", exam_data)


@api_view(http_method_names=['GET', 'POST'])
@renderer_classes([TemplateHTMLRenderer])
def new_exam(request):
    if not len(Session.objects.filter(ip=str(get_client_ip(request)))):
        return HttpResponseRedirect("https://test.insynyp.online/authentication")
    if request.method == "GET":
        return Response(template_name="new_exam.html")
    user = Session.objects.get(ip=str(get_client_ip(request))).user
    first_additional = request.COOKIES["first_additional"]
    second_additional = request.COOKIES["second_additional"]
    if "category" in request.GET.keys():
        exam_bd = new_exam_back(first_additional, second_additional, request.user, category=request.GET["category"])
    else:
        exam_bd = new_exam_back(first_additional, second_additional, request.user)
    return HttpResponseRedirect(f"https://test.insynyp.online/{exam_bd.id}/")


def results(request, exam_id):
    exam_ = Exam.objects.get(id=exam_id)
    # if exam_.user_id != request.user.id:
    #     return HttpResponseRedirect('https://insynyp.online')
    if total_seconds(exam_.end_time) + 6 * 3600 > total_seconds(datetime.datetime.now()):
        return HttpResponseRedirect(f"https://test.insynyp.online/{exam_id}/")
    data = get_right(exam_id)
    exam_data = {"variants": data[2], "total": data[1], "points": data[0], "exam_id": exam_id}
    return render(request, "results.html", exam_data)


def apply_results(request):
    for exam_ in Exam.objects.all():
        ExamResult(exam=exam_, user=exam_.user, result=exam_.get_results()[0]).save()
    return HttpResponseRedirect("https://test.insynyp.online/admin/exam/examresult/")


def detail_results(request, exam_id):
    exam_ = Exam.objects.get(id=exam_id)
    # if exam_.user_id != request.user.id:
    #     return HttpResponseRedirect('https://insynyp.online')
    if total_seconds(exam_.end_time) + 6 * 3600 > total_seconds(datetime.datetime.now()):
        return HttpResponseRedirect(f"https://test.insynyp.online/{exam_id}/")
    return render(request, "detail_results.html", {"exam": get_exam(exam_id)})


def admin_user_results(request, username):
    return render(request, "user_exams.html")


def registration(request):
    if Session.objects.filter(ip=str(get_client_ip(request))):
        return HttpResponseRedirect("https://test.insynyp.online/new")
    if request.method == "GET":
        return render(request, "registration.html")
    else:
        first_name = request.POST["first_name"]
        second_name = request.POST["second_name"]
        email = request.POST["email"].lower()
        phone = request.POST["phone"].lower()
        parent_phone = request.POST["parent_phone"].lower()
        password = request.POST["password"]
        password2 = request.POST["password2"]
        if User.objects.filter(email=email):
            return render(request, "registration.html", {"alert": "пользователь с такой почтой уже зарегистрирован"})
        elif password != password2:
            return render(request, "registration.html", {"alert": "пароли не совпадают"})
        elif len(password) < 8:
            return render(request, "registration.html", {"alert": "пароль слишком короткий"})
        user = User(first_name=first_name, last_name=second_name, phone=phone, parent_phone=parent_phone,
                    email=email, password=md5(password.encode()).hexdigest())
        user.save()
        ip = get_client_ip(request)
        Session(ip=ip, user=user).save()
        return HttpResponseRedirect("https://test.insynyp.online/categories")


def password_recovery(request):
    if request.method == "GET":
        if "token" in request.GET.keys():
            try:
                recovery = PasswordRecovery.objects.get(token=request.GET["token"])
                user = User.objects.get(email=recovery.email)
            except PasswordRecovery.DoesNotExist:
                return HttpResponseRedirect("https://test.insynyp.online/authorization")
            return render(request, "passwordReset.html")
        else:
            return render(request, "passwordResetRequest.html")
    else:
        if "token" in request.GET.keys():
            try:
                recovery = PasswordRecovery.objects.get(token=request.GET["token"])
                user = User.objects.get(email=recovery.email)
            except PasswordRecovery.DoesNotExist:
                return HttpResponseRedirect("https://test.insynyp.online/authorization")
            password = request.POST["password"]
            password2 = request.POST["password2"]
            if password != password2:
                return render(request, "passwordReset.html", {"alert": "пароли не совпадают"})
            if len(password) < 8:
                return render(request, "passwordReset.html", {"alert": "пароль должен содержать как минимум 8 символов"})
            user.password = md5(password.encode()).hexdigest()
            user.save()
            Session(ip=get_client_ip(request), user=user).save()
            return render(request, "message.html", {"message": "Пароль успешно изменён!"})
        else:
            email = request.POST["email"]
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return render(request, "passwordResetRequest.html",
                              {"alert": "почта указана неверно или не зарегистрирована в системе"})
            token = uuid4()
            recovery = PasswordRecovery(token=token, email=email)
            recovery.save()
            send_mail([email], "восстановление пароля для synyp test",
                      "<div style='text-align: center'>"
                      "<h5>для восстановления пароля перейдите по ссылке"
                      " или скопируйте текст ниже в адресную строку</h5>"
                      f"<a href='https://test.insynyp.online/passwordrecovery?token={token}'>Восстановить пароль</a><br>"
                      f"https://test.insynyp.online/passwordrecovery?token={token}</div>")
            return render(request, "message.html", {"message": "Для восстановления пароля следуйте инструкциям "
                                                               "из письма, которое мы вам отправили"})


def categories(request):
    categories_ent = []
    for category in Category.objects.all():
        categories_ent.append({
            "id": category.id,
            "name": category.name,
            "url": category.picture.url
        })
    themes = []
    for theme in Theme.objects.all():
        if not len(ThemeRelation.objects.filter(child=theme)):
            themes.append({
                "id": theme.id,
                "name": theme.name,
                "url": theme.picture.url
            })
    return render(request, "categories.html", context={"categories_ent": categories_ent, "themes": themes})


def get_theme(request):
    theme_id = request.GET["theme"]
    themes = []
    for relation in ThemeRelation.objects.filter(parent=Theme.objects.get(id=theme_id)):
        themes.append({
            "id": relation.child.id,
            "name": relation.child.name,
            "url": relation.child.picture.url
        })
    theme = Theme.objects.get(id=theme_id)
    questions = theme.get_questions()
    if request.method == "POST":
        count = 0
        right = 0
        for question in questions:
            count += 1
            if str(question["id"]) in request.POST.keys():
                question["is_correct"] = ThemeQuestionAnswer.objects.get(
                    id=request.POST[str(question["id"])]).is_correct
                question["chosen"] = int(request.POST[str(question["id"])])
            else:
                question["is_correct"] = False
            for answer in ThemeQuestionAnswer.objects.filter(question=ThemeQuestion.objects.get(id=question["id"])):
                if answer.is_correct:
                    question["correct"] = answer.id
                    break
            if question["is_correct"]:
                right += 1
        return render(request, "theme_result.html", {"themes": themes, "title": theme.name, "questions": questions,
                                                     "count": count, "right": right})
    return render(request, "themes.html", {"themes": themes, "title": theme.name, "questions": questions})


def authentication(request):
    if Session.objects.filter(ip=str(get_client_ip(request))):
        return HttpResponseRedirect("https://test.insynyp.online/new")
    if request.method == "GET":
        return render(request, "authentication.html")
    else:
        email = request.POST["email"].lower()
        password = request.POST["password"]
        try:
            user = User.objects.get(email=email, password=md5(password.encode()).hexdigest())
        except User.DoesNotExist:
            return render(request, "authentication.html", {"alert": "Неправильная почта или пароль"})
        ip = get_client_ip(request)
        Session(ip=ip, user=user).save()
        return HttpResponseRedirect("https://test.insynyp.online/categories")


def logout(request):
    try:
        Session.objects.get(ip=get_client_ip(request)).delete()
    finally:
        return HttpResponseRedirect("https://test.insynyp.online/authentication")


@csrf_exempt
def api(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse("JSONDecodeError")

    action = data["action"]

    if action == "upload_answers":
        return HttpResponse(upload_answers(data))

    elif action == "get_questions":
        return HttpResponse(get_questions(data["exam_id"]))

    elif action == "get_subjects":
        return HttpResponse(get_subjects(data))

    elif action == "get_selected":
        return HttpResponse(get_selected(data))

    elif action == "get_right":
        return HttpResponse(get_right(data))

    elif action == "get_answers":
        return HttpResponse(get_answers(data))

    elif action == "get_user_results":
        return HttpResponse(get_user_results(data["user_id"]))


def get_user_id(request, first_name, last_name, email):
    try:
        return HttpResponse(User.objects.get(first_name=first_name,
                                             last_name=last_name,
                                             email=email).id)
    except User.DoesNotExist:
        return HttpResponse("1")
