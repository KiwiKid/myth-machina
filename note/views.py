import random
from time import sleep
from django.http import JsonResponse
from django_htmx.http import push_url
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q
from django.contrib.gis.geos import Point, Polygon

from note.models import Place, Search


def parse_bbox_to_polygon(bbox_string: str) -> Polygon:
    # bbox_string is expected in the format "minx,miny,maxx,maxy"
    minx, miny, maxx, maxy = [float(val) for val in bbox_string.split(",")]
    return Polygon.from_bbox((minx, miny, maxx, maxy))


def get_paginated_query(query, request):
    '''
    helper function to generate paginated query
    '''
    paginator = Paginator(query, 19)
    page = request.GET.get('page', 1)
    try:
        sleep(0.1)
        query = paginator.page(page)
    except EmptyPage:
        messages.add_message(request, messages.ERROR, 'Bad page number...')
        query = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        query = paginator.page(1)
    # add context
    # config pagination
    page_range = paginator.get_elided_page_range(number=query.number,
                                                 on_each_side=3,
                                                 on_ends=1)
    return query, page_range

# TODO: add bounded box filtering


def get_places_in_bbox(bbox_string):

    return Place.objects.all()

# filter(latitude__gte=minLat, latitude__lte=maxLat, longitude__gte=minLng, longitude__lte=maxLng)


def get_map_data(request):
   # places = Place.objects.order_by('-updated_at')
    data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"popupContent": "This is a popup!"},
                "geometry": {
                    "type": "Point",
                    "coordinates": [-0.09, 51.505]
                }
            }
        ]
    }
    return JsonResponse(data)


def map(request):
    print(f"map() request")

    places = Place.objects.order_by('-updated_at')
    context = {}

    context['count'] = len(places)

   # searches = Search.objects.all()
   # context['searches'] = searches

    template_name = 'note/map.html'
  #  print(f"map() request {len(searches)}")
    return render(request, template_name, context)


def map_points(request):
    bbox_string = request.GET.get("bbox")
    print(f"search in {bbox_string}")

    invalid_point = Point(0, 0)
    if bbox_string:
        bbox_polygon = parse_bbox_to_polygon(bbox_string)
        places = Place.objects.filter(
            location__within=bbox_polygon).exclude(location=invalid_point)
        searches = Search.objects.filter(
            location__within=bbox_polygon).exclude(location=invalid_point)[:10]
    else:
        places = Place.objects.all().exclude(location=invalid_point)
        searches = Search.objects.all().exclude(location=invalid_point)
    # TODO: add filter by user

    # places = Place.objects.order_by('-updated_at')
    context = {}

    context['count'] = len(places)
    context['searches'] = searches

    print(f"map_points {bbox_string}")
    print(f"searches has {len(searches)} results")

    template_name = 'note/map_points.html'
    return render(request, template_name, context)

# Create your views here.


def search_note_view(request, search_id):

    searches = Search.objects.filter(id=search_id)
    context = {}

    match = searches.first()
    context['id'] = match.id
    context['lat'] = match.location.x
    context['lng'] = match.location.y

    template_name = 'note/place_search_view.html'
    return render(request, template_name, context)


def place_search(request):
    lng = float(request.POST.get("lng", 0))
    lat = float(request.POST.get("lat", 0))
    print(f"place_search: Point({lat}, {lng})")

   # id = random.randint(0, 999)
    new_search = Search.objects.create(location=Point(lat, lng))

    context = {}
    context['id'] = new_search.id
    context['lng'] = lng
    context['lat'] = lat

    print(f"new place search id ({new_search.id} {lng}/{lat})")

    template_name = 'note/place_search_view.html'
    return render(request, template_name, context)


def home(request):
    '''
    Home page
    '''
    if not request.user.is_authenticated:
        messages.add_message(
            request,
            messages.ERROR,
            'You need to log in first!'
        )
        return redirect('login_view')
    context = {}
    # get all notes for user
    notes = Place.objects.filter(
        author=request.user).order_by('-updated_at')
    # if search param in url
    query = request.GET.get('search', False)
    if query:
        sleep(0.1)
        notes = notes.filter(Q(title__icontains=query) |
                             Q(content__icontains=query))
    # filter by is_completed status
    uncompleted = request.GET.get('uncompleted', False)
    if uncompleted == 'on':
        sleep(0.1)
        notes = notes.filter(completed_at__isnull=True)
    # get pagination
    context['notes'], context['page_range'] = get_paginated_query(
        notes, request)

    context['search'] = query
    context['uncompleted'] = uncompleted
    # template
    template_name = 'note/home.html'
    return render(request, template_name, context)


def note_view(request):
    '''
    Update single Note
    '''
    context = {}
    template_name = 'note/home.html'
    if request.htmx:
        data = request.POST
        # update Note
        if data['note_action'] == 'update':
            try:
                note = Place.objects.get(id=int(data.get('note_id')))
            except (Place.DoesNotExist, Place.MultipleObjectsReturned):
                messages.add_message(request, messages.ERROR,
                                     'Something went wrong...')
            # if Note exist - update it
            else:
                if note:
                    note.title = data.get('title')
                    note.content = data.get('content')
                    # set completed status
                    if (data.get('completed', None) is not None
                            and data.get('completed')) == 'on':
                        note.completed_at = timezone.now()
                    else:
                        note.completed = None
                    note.save()
                    messages.add_message(request, messages.SUCCESS,
                                         'Your Note updated!')
        # create new Note
        if data['note_action'] == 'create':
            if (
                (data['title'] is None or len(data['title']) < 1)
                and (data['content'] is None or len(data['content']) < 1)
            ):
                messages.add_message(request, messages.ERROR,
                                     'Title or Content is required!')
            # if at least title or content provided - create Note
            else:
                new_note = Place.objects.create(title=data['title'],
                                                content=data['content'],
                                                author=request.user)
                # set completed status
                if (data.get('completed', None) is not None
                        and data.get('completed')) == 'on':
                    new_note.completed_at = timezone.now()
                new_note.save()
                messages.add_message(request, messages.SUCCESS,
                                     'New Note added!')
    # return all notes for user
    notes = Place.objects.filter(
        author=request.user
    ).order_by('-updated_at')
    # get pagination
    context['notes'], context['page_range'] = get_paginated_query(
        notes, request)

    response = render(request, template_name, context)
    return push_url(response, reverse('home_view'))


def delete_note_view(request, note_id):
    '''
    Delete single Note
    '''
    context = {}
    template_name = 'note/home.html'
    # delete Note
    if request.method == 'DELETE':
        try:
            note = Place.objects.get(id=note_id)
            note.delete()
            messages.add_message(request, messages.WARNING,
                                 'Your Note was deleted!')
        except (Place.DoesNotExist, Place.MultipleObjectsReturned):
            messages.add_message(request, messages.ERROR,
                                 'Something went wrong...')
    # return all notes for user
    notes = Place.objects.filter(
        author=request.user
    ).order_by('-updated_at')
    # get pagination
    context['notes'], context['page_range'] = get_paginated_query(
        notes, request)
    response = render(request, template_name, context)
    return push_url(response, reverse('home_view'))


def bulk_notes_view(request):
    '''
    Bulk Notes actions
    '''
    context = {}
    template_name = 'note/home.html'
    if request.htmx:
        # get selected Notes ids
        selected_notes_ids_raw = request.POST.get('selected-notes-ids')
        selected_notes_ids = selected_notes_ids_raw.split(',')
        # get nptes action
        action = request.POST.get('bulk-notes-action')
        # bulk delete Notes
        if action == 'bulk_delete':
            for note_id in selected_notes_ids:
                try:
                    note = Place.objects.get(id=note_id)
                    note.delete()
                except (Place.DoesNotExist, Place.MultipleObjectsReturned):
                    messages.add_message(request, messages.ERROR,
                                         'Something went wrong...')
            messages.add_message(request, messages.WARNING,
                                 'Notes deleted!')
        # bulk change completes status for Notes
        else:
            for note_id in selected_notes_ids:
                try:
                    note = Place.objects.get(id=note_id)
                    if note.is_completed:
                        note.completed_at = None
                    else:
                        note.completed_at = timezone.now()
                    note.save()
                except (Place.DoesNotExist, Place.MultipleObjectsReturned):
                    messages.add_message(request, messages.ERROR,
                                         'Something went wrong...')
            messages.add_message(request, messages.SUCCESS,
                                 'Notes updated!')
    # return all notes for user
    notes = Place.objects.filter(
        author=request.user
    ).order_by('-updated_at')
    # get pagination
    context['notes'], context['page_range'] = get_paginated_query(
        notes, request)
    response = render(request, template_name, context)
    return push_url(response, reverse('home_view'))
