import datetime
from exam.models import *
from random import choice
import json
from requests import post


def total_seconds(time):
    return (((time.year * 365 + time.day) * 24 + time.hour) * 60 + time.minute) * 60 + time.second


def new_exam_back(first_additional, second_additional, user, category=None):
    now = datetime.datetime.now()
    duration = datetime.timedelta(seconds=12600)
    exams_end = now + duration
    subjects = [first_additional, second_additional]
    variants = dict()
    if category:
        category_variants = set([relation.variant for relation
                                 in CategoryRelation.objects.filter(category=Category.objects.get(id=category))])
    else:
        category_variants = set(Variant.objects.all())
    variants['subject_1_variant_id'] = choice(
        list(set(Variant.objects.filter(subj=ExamSubject.objects.get(id=1))).intersection(category_variants))).id
    variants['subject_2_variant_id'] = choice(
        list(set(Variant.objects.filter(subj=ExamSubject.objects.get(id=2))).intersection(category_variants))).id
    variants['subject_3_variant_id'] = choice(
        list(set(Variant.objects.filter(subj=ExamSubject.objects.get(id=3))).intersection(category_variants))).id
    variants['subject_4_variant_id'] = choice(
        list(set(Variant.objects.filter(
            subj=ExamSubject.objects.get(id=subjects[0]))).intersection(category_variants))).id
    variants['subject_5_variant_id'] = choice(
        list(set(Variant.objects.filter(
            subj=ExamSubject.objects.get(id=subjects[1]))).intersection(category_variants))).id

    Exam(**variants, end_time=exams_end).save()
    exam = Exam.objects.get(**variants, end_time=exams_end)
    return exam


def get_exam(exam_id):
    exam = Exam.objects.get(id=exam_id)
    time_left = total_seconds(exam.end_time) - total_seconds(datetime.datetime.now()) + 6 * 3600
    if time_left < 0:
        time_left = 0
    variants = [
        exam.subject_1_variant_id,
        exam.subject_2_variant_id,
        exam.subject_3_variant_id,
        exam.subject_4_variant_id,
        exam.subject_5_variant_id
    ]
    subjects = []
    for i in variants:
        subj = ExamSubject.objects.get(id=Variant.objects.get(id=i).subj.id)
        subjects.append({"id": subj.id, "name": subj.name})
    exam = {
        "examId": exam.id,
        "subjects": subjects,
        "subject1VariantId": variants[0],
        "subject2VariantId": variants[1],
        "subject3VariantId": variants[2],
        "subject4VariantId": variants[3],
        "subject5VariantId": variants[4],
        # "userId": exam.user_id,
        "timeLeft": time_left
    }
    return exam


def upload_answers(data):
    answers = data["answers"]
    exam = Exam.objects.get(id=data["exam_id"])
    exam.end_time = datetime.datetime.now() - datetime.timedelta(hours=9)
    exam.save()
    SelectedAnswer.objects.filter(exam_id=data["exam_id"]).delete()
    for answer in answers:
        if not answers[answer]:
            continue
        SelectedAnswer(
            answer_id=answer,
            is_correct=Answer.objects.get(id=answer).is_correct,
            exam_id=data["exam_id"],
            # user_id=data["user_id"]
        ).save()
    ExamResult(exam=exam, result=exam.get_results()[0]).save()
    return json.dumps(["ok"])


def get_selected(data, right=True):
    exam_id = data["exam_id"]
    selected = [{"id": i.answer_id, "is_correct": i.is_correct}
                for i in SelectedAnswer.objects.filter(exam_id=exam_id)]
    exam = Exam.objects.get(id=exam_id)
    variants = list(map(lambda x: Variant.objects.get(id=x), [exam.subject_1_variant_id,
                                                              exam.subject_2_variant_id,
                                                              exam.subject_3_variant_id,
                                                              exam.subject_4_variant_id,
                                                              exam.subject_5_variant_id]))
    if right:
        for variant in variants:
            for question in Question.objects.filter(var=variant):
                for answer in Answer.objects.filter(quest=question):
                    if answer.is_correct:
                        selected.append({"id": answer.id, "is_correct": True})
    return json.dumps(selected)


def get_questions(exam_id):
    exam = Exam.objects.get(id=exam_id)
    variants = list(map(lambda x: Variant.objects.get(id=x), [exam.subject_1_variant_id,
                                                              exam.subject_2_variant_id,
                                                              exam.subject_3_variant_id,
                                                              exam.subject_4_variant_id,
                                                              exam.subject_5_variant_id]))
    res = {}
    for variant in variants:
        res[variant.subj.id] = []
        for question in Question.objects.filter(var=Variant.objects.get(id=variant.id)):
            if question.photo:
                photo = question.photo.url
            else:
                photo = "#"
            res[variant.subj.id].append({
                "subject": variant.id,
                "id": question.id,
                "image": photo,
                "text": question.text,
                "right_answers_count": question.get_right_answers_count(),
                "selected_answers_count": 0,
                "answers": list(map(
                    lambda x: {"text": x.text,
                               "selected": False,
                               "id": x.id,
                               "image": "#" if not x.photo else x.photo.url},
                    list(Answer.objects.filter(quest=Question.objects.get(id=question.id)))
                ))
            })
    return json.dumps(res)


def get_subjects(data):
    subjects = list(ExamSubject.objects.all())
    additional_relations = AdditionalSubjectsRelation.objects
    second_lessons = dict()
    for subject in subjects:
        subject = subject.id
        second_lessons[subject] = []
        for relation in list(additional_relations.filter(first_subject_id=subject)):
            second_lessons[subject].append(relation.second_subject_id)
        for relation in list(additional_relations.filter(second_subject_id=subject)):
            second_lessons[subject].append(relation.first_subject_id)
    subjects_res = []
    for subject in subjects:
        subjects_res.append({"id": subject.id, "name": str(subject.name)})
    res = json.dumps({
        "subjects": subjects_res,
        "second_lessons": second_lessons
    })
    return res


def get_right(exam_id):
    exam = Exam.objects.get(id=exam_id)
    selected = [{"id": i.answer_id, "is_correct": i.is_correct}
                for i in SelectedAnswer.objects.filter(exam_id=exam.id)]
    try:
        variants = list(map(lambda x: Variant.objects.get(id=x), [exam.subject_1_variant_id,
                                                                  exam.subject_2_variant_id,
                                                                  exam.subject_3_variant_id,
                                                                  exam.subject_4_variant_id,
                                                                  exam.subject_5_variant_id]))
    except Variant.DoesNotExist:
        return "broken"
    res = [0, 0, []]
    result = exam.get_results()
    res[0] = result[0]
    res[1] = result[1]
    i = 0
    for variant in variants:
        i += 1
        result = exam.get_results(i)
        res[2].append({"name": variant.subj.name, "points": result[0]/2, "total": result[1]})
        # questions = Question.objects.filter(var=variant)
        # for question in questions:
        #     answers = Answer.objects.filter(quest=question)
        #     flag = True
        #     one_selected = False
        #     res[1] += 1
        #     res[2][i]["total"] += 1
        #     for answer in answers:
        #         if answer.id in list(map(lambda x: x["id"], selected)):
        #             one_selected = True
        #         if answer.is_correct and answer.id not in list(map(lambda x: x["id"], selected)) or\
        #                 not answer.is_correct and answer.id in list(map(lambda x: x["id"], selected)):
        #             flag = False
        #     if flag and one_selected:
        #         res[0] += 1
        #         res[2][i]["points"] += 1
    return res


def get_user_results(user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return json.dumps({"status": "error", "error": "wrong user id"})
    res = []
    for exam in Exam.objects.filter(user=user):
        results = get_right(exam.id)
        if results == "broken":
            pass
        else:
            res.append({
                "exam_id": exam.id,
                "end_time": str(exam.end_time.date()) + " " + str(exam.end_time.hour) + ":" + str(exam.end_time.minute),
                "first_additional": Variant.objects.get(id=exam.subject_4_variant_id).subj.name,
                "second_additional": Variant.objects.get(id=exam.subject_5_variant_id).subj.name,
                "results": results
            })
    return json.dumps(res)

