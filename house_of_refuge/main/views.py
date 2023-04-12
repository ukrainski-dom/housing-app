import datetime
import json
import logging
from collections import defaultdict
from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_http_methods
from model_utils.models import TimeStampedModel
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from house_of_refuge.main.utils import send_mail
# Create your views here.
from .models import (
    HousingResource, Submission, SubStatus, Coordinator, ObjectChange, END_OF_DAY, SubSource,
    SiteConfiguration, Status, MenuPage, Member, Voivodeship,
)
from .serializers import SubmissionSerializer, HousingResourceSerializer

logger = logging.getLogger(__name__)


@login_required
def housing_list(request):
    coords = defaultdict(list)
    for c in Coordinator.objects.all().order_by("id"):
        coords[c.group].append(c.as_json())

    people_helped = sum([
        sub.people_as_int()
        for sub in Submission.objects.for_happy_message()
    ])

    return render(
        request, "main/housing_list.html", {"props": dict(
            initialResources=[],
            subs=[],
            userData=request.user.as_json(),
            coordinators=coords, helped=people_helped,
        ), "no_nav": True}
    )


@ensure_csrf_cookie
def home(request, **kwargs):
    user = None
    if not request.user.is_anonymous:
        user = request.user
        user = dict(id=user.id, name=str(user))
    return render(request, "main/home.html", {"props": dict(userData=user), "no_nav": True})


@ensure_csrf_cookie
def edit(request):
    return render(request, "main/home.html", {"no_nav": True})


@require_http_methods(["POST"])
def get_form_data(request):
    data = json.loads(request.body)
    token = data.get('token')
    form_data = None
    if token:
        host = get_object_or_404(HousingResource, token=token)
        form_data = host.for_edit()
    return JsonResponse({
        "formData": form_data}
    )


@require_http_methods(["POST"])
@login_required
@transaction.atomic
def resource_match_found(request):
    data = json.loads(request.body)
    resource_id = data["resource"]
    sub_id = data["sub"]
    resource = HousingResource.objects.select_for_update().get(id=resource_id)
    resource.owner = request.user
    resource.will_pick_up_now = data["transport"]
    resource.availability = data["newDate"]
    resource.is_dropped = False
    resource.is_ready = False
    resource.status = "new"
    resource.save()
    sub = Submission.objects.get(id=sub_id)
    if sub.resource is not None and sub.resource == resource:
        # error
        return JsonResponse({
            "status": "error",
            "message": _("This submission already have a diiferent resource"),
            "object": sub.as_prop(),
        }, status=400)
    if sub.matcher != request.user:
        return JsonResponse({
            "status": "error",
            "message": (_("This submission is already processed by {matcher}!")).format(matcher=sub.matcher),
            "object": sub.as_prop(),
        }, status=400)
    sub.resource = resource
    sub.status = SubStatus.SUCCESS
    sub.save()

    ObjectChange.objects.create(
        user=request.user, submission=sub, host=resource,
        change=f"matched host with submission ({data})"
    )

    return JsonResponse({
        "status": "success",
        "message": "Właśnie znalazłeś komuś dom - gratulacje!!",
        "object": sub.as_prop()}
    )


@require_http_methods(["POST"])
@login_required
@transaction.atomic
def update_resource_note(request, resource_id, **kwargs):
    data = json.loads(request.body)
    resource = HousingResource.objects.select_for_update().get(id=resource_id)
    resource.note = data['note']
    ObjectChange.objects.create(
        user=request.user, host=resource,
        change=f"note update: {data}"
    )
    resource.save()
    return JsonResponse({
        "status": "success",
        "message": _("Note updated!"),
        "object": resource.as_prop()}
    )


# @csrf_exempt
@api_view(['POST'])
def send_email_with_edit_token(request):
    email = request.data["email"]
    replies = HousingResource.objects.filter(email__iexact=email).order_by('id')
    if replies:
        subject = _("Link for editing the submission")
        email_text_content = get_template("emails/host_edit.txt").render(
            dict(replies=replies, multiple=len(replies) > 1)
        )
        send_mail(
            subject=subject,
            message=email_text_content,
            recipient_list=[email],
        )
    return Response({}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def create_submission(request):
    serializer = SubmissionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST', 'PUT', "DELETE"])
def create_resource(request):
    _path_old_languages_property(request.data)
    if request.method == "POST":
        serializer = HousingResourceSerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            email_text_content = get_template("emails/host_confirmation.txt").render(
                dict(edit_link=obj.get_edit_url())
            )
            try:
                send_mail(
                    subject="Zgłoszenie przyjęte!",
                    message=email_text_content,
                    recipient_list=[obj.email],
                )
            except Exception as e:
                logger.error(f"Mail sending error for id={obj.id}", exc_info=e)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        obj = get_object_or_404(HousingResource, token=request.data['token'])
    except KeyError:
        return Response({"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "PUT":
        serializer = HousingResourceSerializer(instance=obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        obj.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


@csrf_exempt
@api_view(['POST'])
def create_resource_integration(request, uuid):
    request_body_dict = json.loads(request.body)
    _path_old_languages_property(request_body_dict)
    resource = HousingResource(**request_body_dict)
    resource.save()
    return Response(status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@transaction.atomic
def create_resource_integration_v2(request):
    json_body = json.loads(request.body)
    resource = HousingResource(
        name=json_body["name"],
        phone_number=json_body["phoneNumber"],
        email=json_body["email"],
        voivodeship=Voivodeship.objects.get(pk=json_body["voivodeship"]),
        zip_code=json_body["zipCode"],
        resource=json_body["resourceType"],
        resource_other=json_body["resourceTypeOther"],
        availability=datetime.datetime.strptime(json_body["fromDate"], "%Y-%m-%d"),
        how_long=json_body["period"],
        adults_max_count=json_body["adultsMaxCount"],
        children_max_count=json_body["childrenMaxCount"],
        facilities_other=json_body.get("facilitiesOther"),
        animals_other=json_body.get("animalsOther"),
        languages_other=json_body.get("languagesOther"),
        groups_other=json_body.get("groupsOther"),
        details=json_body.get("additionalInfo"),
    )
    resource.save()
    resource.facilities.add(*json_body.get("facilities"))
    resource.animals.add(*json_body.get("animals"))
    resource.languages.add(*json_body.get("languages"))
    resource.groups.add(*json_body.get("groups"))
    resource.save()
    return Response({"id": resource.id}, status=status.HTTP_201_CREATED)

@csrf_exempt
@api_view(['POST'])
def create_submission_integration(request, uuid):
    sub = Submission(**json.loads(request.body))
    super(TimeStampedModel, sub).save()
    sub.refresh_from_db()
    sub.save()
    return Response(status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@transaction.atomic
def create_submission_integration_v2(request):
    json_body = json.loads(request.body)
    sub = Submission(
        name=json_body["name"],
        current_place=json_body["currentPlace"],
        phone_number=json_body["phoneNumber"],
        email=json_body["email"],
        when=datetime.datetime.strptime(json_body["fromDate"], "%Y-%m-%d"),
        how_long=json_body.get("needPeriod"),
        additional_needs_other=json_body.get("additionalNeedsOther"),
        allergies_other=json_body.get("allergiesOther"),
        languages_other=json_body.get("languagesOther"),
        groups_other=json_body.get("groupsOther"),
        plans_other=json_body.get("plansOther"),
        description=json_body.get("additionalInfo"),
        first_submission=json_body.get("firstSubmission")
    )
    sub.save()

    for adult in json_body.get("adults"):
        Member.objects.create(sex=adult['sex'], age_range=adult['ageRange'], submission=sub)

    for child in json_body.get("children"):
        Member.objects.create(sex=child['sex'], age_range=child['ageRange'], submission=sub)

    sub.voivodeships.add(*json_body.get("voivodeships"))
    sub.additional_needs.add(*json_body.get("additionalNeeds"))
    sub.allergies.add(*json_body.get("allergies"))
    sub.languages.add(*json_body.get("languages"))
    sub.groups.add(*json_body.get("groups"))
    sub.plans.add(*json_body.get("plans"))
    sub.save()
    return Response({"id": sub.id}, status=status.HTTP_201_CREATED)


@require_http_methods(["POST"])
@transaction.atomic
def update_sub(request, sub_id):
    data = json.loads(request.body)
    sub = Submission.objects.select_for_update().get(id=sub_id)
    for field, value in data['fields'].items():
        if "matcher" in field and sub.matcher and sub.matcher != request.user:
            if value:
                # someone wants to start working on already taken sub
                return JsonResponse(
                    {"data": None,
                     "message": _("Someone is already searching for this request"),
                     "status": "error"}, status=400)
            else:
                is_coordinator = Coordinator.objects.filter(user=request.user).exists()
                # someone wants to free up a taken sub, only coordinator can do that!
                if not is_coordinator:
                    return JsonResponse(
                        {"data": None,
                         "message": _("Someone is already processing this request"),
                         "status": "error"}, status=400)
                else:
                    setattr(sub, field, value)

        elif field == "status" and value in [SubStatus.GONE, SubStatus.CANCELLED]:
            sub.handle_gone()
        elif field == "status" and value == SubStatus.CONTACT_ATTEMPT:
            sub.handle_contact_attempt()
        elif field == "when":
            date_value = datetime.datetime.strptime(value, "%Y-%m-%d")
            sub.when = date_value
        else:
            setattr(sub, field, value)
    sub.save()
    ObjectChange.objects.create(
        user=request.user, submission=sub,
        change=f"update: {data}"
    )
    return JsonResponse({"data": sub.as_prop(), "message": "Updated", "status": "success", })


@api_view(['POST'])
@transaction.atomic
def update_resource(request, resource_id):
    resource = HousingResource.objects.select_for_update().get(id=resource_id)
    serializer = HousingResourceSerializer(instance=resource, data=request.data['fields'], partial=True)
    if serializer.is_valid():
        serializer.save()
        ObjectChange.objects.create(
            user=request.user, host=resource,
            change=f"update: {request.data['fields']}"
        )
        return JsonResponse({"data": resource.as_prop(), "message": "Updated", "status": "success", })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@require_http_methods(["GET"])
@login_required
def latest_submission(request):
    return JsonResponse({"id": str(Submission.objects.all().latest("modified").modified.timestamp())})


@require_http_methods(["GET"])
@login_required
def latest_resource(request):
    return JsonResponse({"id": str(HousingResource.objects.all().latest("modified").modified.timestamp())})


@require_http_methods(["GET"])
def check_submission_limit(request):
    config = SiteConfiguration.get_solo()
    active = -1
    if config.submission_throttling:
        active = Submission.objects.filter(
            source=SubSource.WEBFORM,
            status__in=[SubStatus.NEW, SubStatus.SEARCHING],
            created__gt=config.throttle_created_after,
        ).count()
    return JsonResponse({"can_add": active < config.submission_throttling})


@require_http_methods(["GET"])
@login_required
def get_resources(request):
    since = request.GET.get("since", "0")
    try:
        updated_after = datetime.datetime.fromtimestamp(float(since)).astimezone(timezone.utc)
    except OSError:
        updated_after = datetime.datetime(year=2010, month=1, day=1)
    resources = [
        r.as_prop()
        for r in HousingResource.objects.select_related(
            "owner"
        ).prefetch_related("languages", "animals", "facilities", "groups").filter(
            modified__gt=updated_after
        )
    ]
    return JsonResponse({"data": resources})


@require_http_methods(["GET"])
@login_required
def get_submissions(request):
    since = request.GET.get("since", "0")
    try:
        updated_after = datetime.datetime.fromtimestamp(float(since)).astimezone(timezone.utc)
    except OSError:
        updated_after = datetime.datetime(year=2010, month=1, day=1)
    subs = [
        s.as_prop()
        for s in Submission.objects.select_related(
            "matcher", "receiver", "coordinator", "resource__owner",
        ).prefetch_related(
            "languages", "additional_needs", "voivodeships", "allergies", "groups", "plans", "member_set"
        ).filter(modified__gt=updated_after)
    ]
    dropped = [hr.as_prop() for hr in HousingResource.objects.select_related("owner").filter(is_dropped=True)]
    return JsonResponse({"data": dict(submissions=subs, dropped=dropped)})


def healthcheck(request):
    HousingResource.objects.first()
    return HttpResponse("", status=200)


def day_iterator(start_date):
    now = timezone.now()
    start_date = start_date.replace(hour=END_OF_DAY, minute=0, second=0, microsecond=0)
    if start_date.hour < END_OF_DAY:
        start_date -= timedelta(days=1)

    end_date = start_date + timedelta(days=1)

    yield start_date, end_date
    while end_date < now:
        start_week = end_date
        end_date += timedelta(days=1)
        yield start_week, end_date


@login_required
def get_stats_data(request):
    props_subs = [s.for_stats() for s in Submission.objects.prefetch_related("changes").all().order_by('created')]
    props_hosts = [h.for_stats() for h in HousingResource.objects.exclude_excels().order_by('created')]
    return JsonResponse({"data": dict(submissions=props_subs, hosts=props_hosts)})


@staff_member_required
def activity_stats_view(request):
    base_start = Submission.objects.earliest("created").created

    all_hosts = HousingResource.objects.all().count()
    cancelled_hosts = HousingResource.objects.filter(status=Status.IGNORE).count()
    active_hosts = HousingResource.objects.filter(status=Status.NEW, availability__lte=timezone.now()).count()
    turtle_hosts = HousingResource.objects.exclude(status=Status.IGNORE).filter(turtle=True).count()
    active_turtle_hosts = HousingResource.objects.exclude(status=Status.IGNORE).filter(
        turtle=True,
        availability__lte=timezone.now()).count()
    all_subs = Submission.objects.all().count()
    all_success = Submission.objects.filter(status=SubStatus.SUCCESS).count()
    all_cancelled = Submission.objects.filter(status=SubStatus.CANCELLED).count()

    terrain_subs = Submission.objects.filter(source=SubSource.TERRAIN).count()
    terrain_success = Submission.objects.filter(source=SubSource.TERRAIN, status=SubStatus.SUCCESS).count()
    terrain_cancelled = Submission.objects.filter(source=SubSource.TERRAIN, status=SubStatus.CANCELLED).count()

    context = dict(
        no_nav=True,
        props=dict(startDate=base_start),
        all_subs=all_subs,
        all_hosts=all_hosts,
        turtle_hosts=turtle_hosts,
        active_turtle_hosts=active_turtle_hosts,
        cancelled_hosts=cancelled_hosts,
        active_hosts=active_hosts,
        all_success=all_success,
        all_cancelled=all_cancelled,
        terrain_subs=terrain_subs,
        terrain_success=terrain_success,
        terrain_cancelled=terrain_cancelled,
        terrain_ratio=f"{terrain_subs / all_subs:.0%}",
        terrain_success_ratio=f"{terrain_success / terrain_subs:.0%}",
        terrain_cancelled_ratio=f"{terrain_cancelled / terrain_subs:.0%}",
        all_success_ratio=f"{all_success / all_subs:.0%}",
        all_cancelled_ratio=f"{all_cancelled / all_subs:.0%}",
    )
    return render(request, "users/stats.html", context=context)


@require_http_methods(["GET"])
@login_required
def get_helped_count(request):
    people_helped = sum([
        sub.people_as_int()
        for sub in Submission.objects.for_happy_message()
    ])
    return JsonResponse({"count": people_helped})


@require_http_methods(["GET"])
def get_menu_pages(reqeust):
    pages = [page.as_json() for page in MenuPage.objects.filter(published=True)]
    return JsonResponse(pages, safe=False)


def _path_old_languages_property(request_body_dict):
    if "languages" in request_body_dict:
        request_body_dict["languages_other"] = request_body_dict["languages"]
        del request_body_dict["languages"]
