from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.translation import gettext_lazy as _
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from markdownx.admin import MarkdownxModelAdmin
from solo.admin import SingletonModelAdmin

from .models import (
    HousingResource, Submission, Coordinator, Status, ObjectChange,
    SiteConfiguration, MenuPage,
)


class ChangeInline(admin.TabularInline):
    model = ObjectChange
    extra = 0
    can_delete = False
    readonly_fields = [
        "user",
        "submission",
        "host",
        "change",
        "created"
    ]


@admin.register(ObjectChange)
class HousingResourceAdmin(ModelAdmin):
    search_fields = ("pk", "change", "user__name", "host__id", "submission__id")
    list_display = ("id", "user", "change", "host", "submission", "created")
    readonly_fields = [
        "user",
        "submission",
        "host",
        "change",
    ]


class HousingRow(resources.ModelResource):

    def skip_row(self, instance, original):
        standard_fields_are_same = all([
            instance.email == original.email,
            instance.people_to_accommodate_raw == original.people_to_accommodate_raw,
            instance.extra == original.extra,
            instance.availability == original.availability,
        ])
        status_change_to_ignore = all([
            original.status == Status.NEW,
            instance.status == Status.IGNORE
        ])

        if standard_fields_are_same and status_change_to_ignore:
            return super().skip_row(instance, original)
        elif standard_fields_are_same:
            return True
        else:
            return super().skip_row(instance, original)

    class Meta:
        model = HousingResource
        exclude = ("token", )
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ["id"]


@admin.action(description=_('Mark for deletion'))
def mark_for_deletion(modeladmin, request, queryset):
    queryset.update(status=Status.SHOULD_DELETE)


@admin.register(HousingResource)
class HousingResourceAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    resource_class = HousingRow
    search_fields = ("pk", "name", "about_info", "city_and_zip_code", "phone_number", "details", "extra", "address", "owner__name")
    list_display = ("id", "name", "email", "resource", "status", "cherry", "verified")
    list_filter = ("status", "cherry", "verified")
    list_editable = ("status", "cherry", "verified",)
    autocomplete_fields = ['owner']
    inlines = [ChangeInline]
    # exclude = ["token"]
    readonly_fields = ["token"]
    actions = [mark_for_deletion]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name in ["owner"]:
            field = form.base_fields[field_name]
            field.widget.can_add_related = False
            field.widget.can_change_related = False
            field.widget.can_delete_related = False
        return form


class SubmissionRow(resources.ModelResource):
    class Meta:
        model = Submission


@admin.register(Submission)
class SubmissionAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin):
    resource_class = SubmissionRow
    search_fields = ("id", "name", "languages", "phone_number","receiver__name", "coordinator__name", "note", "contact_person", "matcher__name")
    list_display = ("id", "name", "people","how_long",
                    "contact_person", "description",
                    "note", "source", "status",)
    list_filter = ("status", "source", "should_be_deleted")
    list_editable = ("status", "source", "note")
    autocomplete_fields = ['resource', 'matcher', 'coordinator', 'receiver']
    inlines = [ChangeInline]
    ordering = ["-pk"]

    def get_form(self, request, obj=None, **kwargs):
        form = super(SubmissionAdmin, self).get_form(request, obj, **kwargs)
        for field_name in ["receiver", "matcher", "coordinator", "resource"]:
            field = form.base_fields[field_name]
            field.widget.can_add_related = False
            field.widget.can_change_related = False
            field.widget.can_delete_related = False
        return form


@admin.register(Coordinator)
class CoordinatorAdmin(ModelAdmin):
    # resource_class = HousingRow
    list_display = ("pk", "user", "group",)
    list_editable = ("user", "group",)
    autocomplete_fields = ['user']


admin.site.register(SiteConfiguration, SingletonModelAdmin)


@admin.register(MenuPage)
class MenuPageAdmin(MarkdownxModelAdmin):
    list_display = ("slug", "menu_title_primary_language", "published")
    list_editable = ('published',)
