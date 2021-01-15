from django.shortcuts import render, get_object_or_404
from .models import Measurement
from .forms import MeasurementModelForm
# from geopy.geocoders import Photon, Nominatim
from geopy.distance import geodesic
from .utils import get_geo, get_center_coordinates, get_zoom, get_ip_address, popup_box
import folium
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.api import Api
#import overpy

# Create your views here.


def calculate_distance_view(request):
    # initial values
    location = None
    distance = None
    destination = None

    obj = get_object_or_404(Measurement, id=1)
    form = MeasurementModelForm(request.POST or None)
    locator = Nominatim() #(user_agent='martin_jr8')
    nominatim = Nominatim()
    #cas = geolocator.geocode(query='germany')
    areaId = nominatim.query('germany').areaId()
    overpass = Overpass()


    # country borders query
    # border_query = overpassQueryBuilder(area=areaId, elementType='way', selector="'border_type'='nation'", out='body')
    # border_objects = overpass.query(border_query)
    # border_list = border_objects.elements()
    # border_infos = []
    # for border in border_list:
    #     border_infos.append(border.tags())

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
    # location=[ger_location.lat(), ger_location.lon()],
    m = folium.Map(zoom_start=8)

    for castle_loc in castle_list:
        info_dict = castle_loc.tags()
        # popup_info = info_dict.values()
        castle_id = castle_loc.id()
        folium.Marker([castle_loc.lat(), castle_loc.lon()], tooltip=info_dict.get('name'),
                     popup=folium.Popup(popup_box(info_dict.get('name'), castle_id), max_width=500),
                      icon=folium.Icon(color='purple', icon='fort-awesome', prefix='fa')).add_to(m)

    # location marker
    # folium.Marker([l_lat, l_lon], tooltip='click here for more', popup=city['city'],
    #   icon=folium.Icon(color='purple')).add_to(m)

    if form.is_valid():
        instance = form.save(commit=False)
        location_ = form.cleaned_data.get('location')
        location = geolocator.geocode(location_)
        destination_ = form.cleaned_data.get('destination')
        destination = geolocator.geocode(destination_)

        # location coordinates
        l_lat = location.latitude
        l_lon = location.longitude
        pointA = (l_lat, l_lon)

        # destination coordinates
        d_lat = destination.latitude
        d_lon = destination.longitude
        pointB = (d_lat, d_lon)

        # distance calculation
        distance = round(geodesic(pointA, pointB).km, 2)

        # folium map modification
        m = folium.Map(location=get_center_coordinates(l_lat, l_lon, d_lat, d_lon), zoom_start=get_zoom(distance))
        # location marker
        folium.Marker([l_lat, l_lon], tooltip='click here for more', popup=location,
                      icon=folium.Icon(color='purple')).add_to(m)
        # destination marker
        folium.Marker([d_lat, d_lon], tooltip='click here for more', popup=destination,
                      icon=folium.Icon(color='red', icon='cloud')).add_to(m)

        # the line
        line = folium.PolyLine(locations=[pointA, pointB], weight=2, color='blue')
        m.add_child(line)

        instance.location = location
        instance.distance = distance
        instance.save()

    m = m._repr_html_()

    context = {
        'distance': distance,
        'location': location,
        'destination': destination,
        'form': form,
        'map': m,
        'castles': castle_infos
        # 'ops' : border_objects
    }

    return render(request, 'measurements/main.html', context)
