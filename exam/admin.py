from django.contrib import admin
from exam.models import *
import nested_admin


class AnswerInline(nested_admin.NestedTabularInline):
    model = Answer


class QuestionInline(nested_admin.NestedTabularInline):
    model = Question
    inlines = [AnswerInline, ]


class CategoryInline(nested_admin.NestedTabularInline):
    model = CategoryRelation


class VariantAdmin(nested_admin.NestedModelAdmin):
    inlines = [QuestionInline, CategoryInline]


class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ('first_name', 'last_name', 'email', 'phone', 'parent_phone', 'id')
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'email', 'phone', 'parent_phone', 'password')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('first_name',
                                                 'last_name', 'email', 'phone', 'parent_phone', 'password')}),
    )
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('first_name',)
    readonly_fields = ('date_created',)
    date_hierarchy = 'date_created'


class ThemeQuestionAnswerInline(nested_admin.NestedTabularInline):
    model = ThemeQuestionAnswer


class ThemeQuestionInline(nested_admin.NestedTabularInline):
    model = ThemeQuestion
    inlines = [ThemeQuestionAnswerInline, ]


class ThemeRelationInline(nested_admin.NestedTabularInline):
    model = ThemeRelation
    fk_name = "child"


class ThemeAdmin(nested_admin.NestedModelAdmin):
    inlines = [ThemeRelationInline, ThemeQuestionInline]


admin.site.register(ExamSubject)
admin.site.register(Variant, VariantAdmin)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Exam)
admin.site.register(Session)
admin.site.register(User, UserAdmin)
admin.site.register(Theme, ThemeAdmin)
admin.site.register(Category)
admin.site.register(AdditionalSubjectsRelation)
