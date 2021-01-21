from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Locations
from .forms import LocationsModelForm
from geopy.geocoders import Photon as Nom
from geopy.distance import geodesic
from .utils import get_geo, get_center_coordinates, get_zoom, get_ip_address, popup_box
import folium
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.api import Api
from django.views.decorators.csrf import csrf_exempt
import json
#from django import template
from profiles.models import Profile

#register = template.Library()


def calculate_distance_view(request):
    # initial values
    nominatim = Nominatim()
    overpass = Overpass()
    api = Api()
    name = None
    review = None
    state = None
    loc_form = LocationsModelForm(request.POST or None)

    country = nominatim.query('germany')


    # obj = get_object_or_404(Locations, id=1)

    locator = Nom() #(user_agent='martin_jr8')
    areaId = country.areaId()
    names_query = country.toJSON()
    country_details = names_query[0]
    country_coor_lat = country_details["lat"]
    country_coor_lon = country_details["lon"]


    # castles location query
    castle_query = overpassQueryBuilder(area=areaId, elementType='node', selector='castle_type', out='body')
    castle_objects = overpass.query(castle_query)
    castle_list = castle_objects.elements()
    castle_infos = []
    for castle in castle_list:
        castle_infos.append(castle.tags())


    # ip_ = get_ip_address(request)
    # print(ip_)
    # ip = '72.14.207.99'
    # country, city, lat, lon = get_geo(ip)
    # location = geolocator.geocode(city)

    # location coordinates
    # l_lat = lat
    # l_lon = lon
    # pointA = (l_lat, l_lon)

    # initail folium map
    m = folium.Map(location=[country_coor_lat, country_coor_lon], zoom_start=6)

    for castle_loc in castle_list:
        info_dict = castle_loc.tags()
        castle_id = castle_loc.id()
        castle_name = info_dict.get('name')
        if castle_name == None:
            continue
        else:
            folium.Marker([castle_loc.lat(), castle_loc.lon()], tooltip=castle_name,
                           popup=folium.Popup(popup_box(info_dict.get('name'), castle_id), max_width=500),
                           icon=folium.Icon(color='purple', icon='fort-awesome', prefix='fa')).add_to(m)


    if request.user.is_authenticated:
        user = Profile.objects.get(user=request.user)
        loc = user.location
        location = locator.geocode(loc)
        l_lat = location.latitude
        l_lon = location.longitude
        loc_point = (l_lat, l_lon)

        folium.Marker([l_lat, l_lon], tooltip='Your Location', popup=location,
                      icon=folium.Icon(color='blue', icon='home', prefix='fa')).add_to(m)



        # # location coordinates
        # l_lat = location.latitude
        # l_lon = location.longitude
        # pointA = (l_lat, l_lon)

        # # destination coordinates
        # d_lat = destination.latitude
        # d_lon = destination.longitude
        # pointB = (d_lat, d_lon)

        # # distance calculation
        # distance = round(geodesic(pointA, pointB).km, 2)

        # # folium map modification
        # m = folium.Map(location=get_center_coordinates(l_lat, l_lon, d_lat, d_lon), zoom_start=get_zoom(distance))
        # # location marker
        # folium.Marker([l_lat, l_lon], tooltip='click here for more', popup=location,
        #               icon=folium.Icon(color='purple')).add_to(m)
        # # destination marker
        # folium.Marker([d_lat, d_lon], tooltip='click here for more', popup=destination,
        #               icon=folium.Icon(color='red', icon='cloud')).add_to(m)

        # # the line
        # line = folium.PolyLine(locations=[pointA, pointB], weight=2, color='blue')
        # m.add_child(line)



    if request.method == 'GET' and request.is_ajax():
        castle_id = request.GET.get('castle_id')
        castle_data = api.query(f'node/{castle_id}')
        castle_details = castle_data.tags()
        print(castle_details['name'])
        loc_form = LocationsModelForm(instance=request.user, initial={"name": castle_details['name']})
        print(loc_form)


        if request.user.is_authenticated and user.location != None:
            castle_lat = castle_data.lat()
            castle_lon = castle_data.lon()
            castle_point = (castle_lat, castle_lon)
            distance = round(geodesic(loc_point, castle_point).km, 2)
            castle_details["distance"] = distance

            # line = folium.PolyLine(locations=[loc_point, castle_point], weight=2, color='blue')
            # m.add_child(line)
            # m = m._repr_html_()


        return HttpResponse(json.dumps(castle_details), content_type="application/json") 

    if request.user.is_authenticated and loc_form.is_valid():
        instance = loc_form.save(commit=False)
        name = loc_form.cleaned_data.get('name')
        review = loc_form.cleaned_data.get('review')
        state = loc_form.cleaned_data.get('state')

        
        instance.name = name
        instance.review = review
        instance.state = state
        instance.user = request.user
        instance.save()
    

    m = m._repr_html_()

    context = {
        'name': name,
        'review': review,
        'state': state,
        'form': loc_form,
        'map': m,
        'castles': country_coor_lat,
        # 'ops' : border_objects
        # 'name': requested_id
    }
    
    return render(request, 'measurements/main.html', context)
