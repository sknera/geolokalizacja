from django.shortcuts import render, get_object_or_404
from .models import Measurement
from .forms import MeasurementModelForm
from geopy.geocoders import Nominatim
from .utils import get_geo, get_center_coordinates, get_zoom, get_ip_address
from geopy.distance import geodesic
import folium


# Create your views here.

def calculate_distance_view(request):
    # initial values
    distance = None
    city_name = None
    destination = None

    obj = get_object_or_404(Measurement, id=1)
    form = MeasurementModelForm(request.POST or None)
    geolocator = Nominatim(user_agent='measurements')

    ip_ = get_ip_address(request)
    print(ip_)
    ip = '109.173.220.158'
    country, city, lat, lon = get_geo(ip)
    location = geolocator.geocode(city)

    # location coordinates
    l_lat = lat
    l_lon = lon
    pointA = (l_lat, l_lon)

    # initial folium map
    m = folium.Map(width=800, height=500, location=get_center_coordinates(l_lat, l_lon), zoom_start=8)
    # location marker
    folium.Marker([l_lat, l_lon], tooltip='twoja lokalizacja',
                  popup="kod pocztowy: " + city['postal_code'] + " miasto: " + city['city'],
                  icon=folium.Icon('green')).add_to(m)

    if form.is_valid():
        instance = form.save(commit=False)
        destination_ = form.cleaned_data.get('destination')
        city_name = form.cleaned_data.get('city')
        destination = geolocator.geocode(destination_)

        # destination coordinates
        d_lat = destination.latitude
        d_lon = destination.longitude
        pointB = (d_lat, d_lon)

        # distance calculation
        distance = round(geodesic(pointA, pointB).km, 2)

        # initial folium map
        m = folium.Map(width=800, height=500,
                       location=get_center_coordinates(l_lat, l_lon, d_lat, d_lon),
                       zoom_start=get_zoom(distance))
        # location marker
        folium.Marker([l_lat, l_lon], tooltip='twoja lokalizacja',
                      popup="kod pocztowy: " + city['postal_code'] + " miasto: " + city['city'],
                      icon=folium.Icon('green')).add_to(m)

        # destination  marker
        folium.Marker([d_lat, d_lon], tooltip='cel podróży',
                      popup=destination,
                      icon=folium.Icon('red', icon="cloud")).add_to(m)

        # draw the line between location and destination
        line = folium.PolyLine(locations=[pointA, pointB], weight=2, color='blue')
        m.add_child(line)

        # folium map modification
        instance.location = location
        instance.distance = distance
        instance.save()

    m = m._repr_html_()
    distance = None

    context = {
        'distance': distance,
        'destination': destination,
        'city': city_name,
        'form': form,
        'map': m,
    }

    return render(request, 'measurements/main.html', context)
