from django.db import models
from django.conf import settings
from datetime import date as dt


# User = settings.AUTH_USER_MODEL


class ExamSubject(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} id - {self.id}"

    class Meta:
        verbose_name = "Предмет ЕНТ"
        verbose_name_plural = "Предметы ЕНТ"


class Variant(models.Model):
    subj = models.ForeignKey(ExamSubject, on_delete=models.CASCADE)
    subject_variant_number = models.IntegerField()

    def __str__(self):
        subject = ExamSubject.objects.get(id=self.subj.id).name
        return f"{subject}: Вариант№{self.subject_variant_number} id-{self.id}"

    class Meta:
        verbose_name = "Вариант ЕНТ"
        verbose_name_plural = "Варианты ЕНТ"


class SelectedAnswer(models.Model):
    answer_id = models.IntegerField()
    is_correct = models.BooleanField()
    # user_id = models.IntegerField()
    exam_id = models.IntegerField()


class Question(models.Model):
    var = models.ForeignKey(Variant, on_delete=models.CASCADE)
    text = models.TextField(default="")
    photo = models.ImageField(null=True, blank=True, upload_to='exam_img')

    def __str__(self):
        subject = ExamSubject.objects.get(id=Variant.objects.get(id=self.var.id).subj.id).name
        return f"вопрос по {subject}: {self.text} id-{self.id}"

    def get_right_answers_count(self):
        right_answers_count = 0
        for answer in Answer.objects.filter(quest=self):
            right_answers_count += int(answer.is_correct)
        return right_answers_count

    def points(self, exam_id):
        right_answers_count = 0
        wrong_selected_answers_count = 0
        right_selected_answers_count = 0
        selected = dict()
        for i in SelectedAnswer.objects.filter(exam_id=exam_id):
            selected[i.answer_id] = i.is_correct
        for answer in Answer.objects.filter(quest=self):
            if answer.is_correct:
                right_answers_count += 1
            if answer.id in selected.keys():
                right_selected_answers_count += int(selected[answer.id])
                wrong_selected_answers_count += int(not selected[answer.id])
        if right_answers_count == 3:
            if right_selected_answers_count == 3 and wrong_selected_answers_count == 0:
                return 2, 2
            elif right_selected_answers_count == 3 and wrong_selected_answers_count == 1 or \
                    right_selected_answers_count == 2 and wrong_selected_answers_count in range(2):
                return 1, 2
            else:
                return 0, 2
        elif right_answers_count == 2:
            if right_selected_answers_count == 2 and wrong_selected_answers_count == 0:
                return 2, 2
            elif right_selected_answers_count == 1 and wrong_selected_answers_count in range(2) or\
                    right_selected_answers_count == 2 and wrong_selected_answers_count == 1:
                return 1, 2
            else:
                return 0, 2
        elif right_answers_count == 1:
            if right_selected_answers_count == 1 and wrong_selected_answers_count == 0:
                return 2, 2
            elif right_selected_answers_count == 1 and wrong_selected_answers_count == 1:
                return 1, 2
            else:
                return 0, 2
        else:
            res = right_selected_answers_count - wrong_selected_answers_count
            if res < 0:
                res = 0
            return res, right_answers_count

    class Meta:
        verbose_name = "Вопрос ЕНТ"
        verbose_name_plural = "Вопросы ЕНТ"


class Answer(models.Model):
    quest = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField(default="")
    photo = models.ImageField(null=True, blank=True, upload_to='exam_img')
    is_correct = models.BooleanField()

    class Meta:
        verbose_name = "Ответ ЕНТ"
        verbose_name_plural = "Ответы ЕНТ"


class Exam(models.Model):
    subject_1_variant_id = models.IntegerField()
    subject_2_variant_id = models.IntegerField()
    subject_3_variant_id = models.IntegerField()
    subject_4_variant_id = models.IntegerField()
    subject_5_variant_id = models.IntegerField()
    end_time = models.DateTimeField()
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def get_results(self, variant=0):
        variants = [self.subject_1_variant_id,
                    self.subject_2_variant_id,
                    self.subject_3_variant_id,
                    self.subject_4_variant_id,
                    self.subject_5_variant_id]
        if variant in range(1, 6):
            variants = [variants[variant - 1]]
        gotten = 0
        total = 0
        for variant in variants:
            try:
                variant = Variant.objects.get(id=variant)
            except Variant.DoesNotExist:
                continue
            for question in Question.objects.filter(var=variant):
                res = list(question.points(self.id))
                gotten += res[0]
                total += res[1]
        return [gotten, total/2]

    class Meta:
        verbose_name = "Экзамен ЕНТ"
        verbose_name_plural = "Экзамены ЕНТ"


class ExamResult(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    result = models.IntegerField()
    # user = models.ForeignKey(User, on_delete=models.CASCADE)


class PasswordRecovery(models.Model):
    token = models.CharField(max_length=256, default="no token")
    email = models.EmailField(default="nomail@mail.com")


class User(models.Model):
    email = models.EmailField(default="nomail@mail.com")
    password = models.CharField(max_length=256, default="12345678")
    phone = models.CharField(max_length=16, default="+700000000")
    parent_phone = models.CharField(max_length=16, default="+700000000")
    first_name = models.CharField(max_length=32, default="Name")
    last_name = models.CharField(max_length=32, default="Surname")
    date_created = models.DateField(default=dt.today())

    def __str__(self):
        return f"{self.first_name} "

    class Meta:
        verbose_name = "Ученик"
        verbose_name_plural = "Ученики"


class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip = models.CharField(max_length=256, default="no_ip")


class Category(models.Model):
    name = models.CharField(max_length=256, default="")
    picture = models.ImageField(blank=True, upload_to='exam_img')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория ЕНТ"
        verbose_name_plural = "Категории ЕНТ"


class CategoryRelation(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)


class Theme(models.Model):
    name = models.CharField(max_length=256, default="")
    picture = models.ImageField(blank=True, upload_to='exam_img')

    def get_questions(self):
        questions = []
        for question in ThemeQuestion.objects.filter(theme=self):
            questions.append(question.serialize())
        for relation in ThemeRelation.objects.filter(parent=self):
            questions += relation.child.get_questions()
        return questions

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"


class ThemeRelation(models.Model):
    parent = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name="a")
    child = models.ForeignKey(Theme, on_delete=models.CASCADE)

    def __str__(self):
        return self.parent.name + "=>" + self.child.name

    class Meta:
        verbose_name = "Зависимость между темами"
        verbose_name_plural = "Зависимости между темами"


class ThemeQuestion(models.Model):
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    text = models.CharField(max_length=256, default="")

    def __str__(self):
        return self.theme.name + "-" + self.text

    def serialize(self):
        answers = []
        for answer in ThemeQuestionAnswer.objects.filter(question=self):
            answers.append({"text": answer.text, "id": answer.id})
        return {"text": self.text, "answers": answers, "id": self.id}

    class Meta:
        verbose_name = "Вопрос по теме"
        verbose_name_plural = "Вопросы по теме"


class ThemeQuestionAnswer(models.Model):
    question = models.ForeignKey(ThemeQuestion, on_delete=models.CASCADE)
    text = models.CharField(max_length=256, default="")
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.question.text + "-" + self.text

    class Meta:
        verbose_name = "Ответ на вопрос по теме"
        verbose_name_plural = "Ответы на опросы по теме"


class AdditionalSubjectsRelation(models.Model):
    subj1 = models.ForeignKey(ExamSubject, related_name="subj1", on_delete=models.CASCADE)
    subj2 = models.ForeignKey(ExamSubject, on_delete=models.CASCADE)
    first_subject_id = models.IntegerField()
    second_subject_id = models.IntegerField()

    class Meta:
        verbose_name = "Зависимость доп. предметов"
        verbose_name_plural = "Зависимости доп. предметов"
