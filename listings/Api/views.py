from django.db.models.query import Prefetch
from django.db.models import Q

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import HotelSerializer, ApartmentSerializer
from ..models import Listing, BookingInfo, Reservation, HotelRoom, HotelRoomType

from decimal import Decimal
import datetime


@api_view(['GET',])
def list_units(request):
    max_price = Decimal(request.query_params.get('max_price'))
    check_in = datetime.datetime.strptime(request.query_params.get('check_in'), "%Y-%m-%d").date()
    check_out = datetime.datetime.strptime(request.query_params.get('check_out'), "%Y-%m-%d").date()

    q1 = BookingInfo.objects.filter(price__lt=max_price, listing__isnull=False).order_by('price') 
    prefetch1 = Prefetch('booking_info', queryset=q1)
    q2 = Reservation.objects.filter(Q(from_date__range=[check_in,check_out]) | Q(to_date__range=[check_in, check_out]) | Q(from_date__lte=check_in, to_date__gte=check_out))
    prefetch2 = Prefetch('reservations', queryset=q2)
    
    units = Listing.objects.prefetch_related(prefetch1, prefetch2)
    cheapest_apartments = units.filter(id__in=q1.values_list('listing'))
    cheapest_apartments = cheapest_apartments.exclude(id__in=q2.values_list('apartment').filter(apartment__isnull=False))
    
    hotel_rooms = HotelRoom.objects.exclude(id__in=q2.values_list('hotel_room').filter(hotel_room__isnull=False)).values_list('hotel_room_type').distinct()
    q3 = BookingInfo.objects.filter(price__lt=max_price, hotel_room_type__in=hotel_rooms).order_by('price').first() 
    cheapest_hotel_price = q3.price
    cheapest_hotel = Listing.objects.get(id=HotelRoomType.objects.get(id=q3.hotel_room_type.pk).hotel.pk)

    serializer1 = ApartmentSerializer(cheapest_apartments, many=True)
    serializer2 = HotelSerializer(cheapest_hotel)

    data = {'items': []} 
    added = False

    for val in serializer1.data:
        if val['price'] < cheapest_hotel_price:
            data['items'].append(val)
        else:
            hotel_data= serializer2.data
            hotel_data['price'] = cheapest_hotel_price
            data['items'].append(hotel_data)
            added = True
            data['items'].append(val)

    if not added:
        hotel_data= serializer2.data
        hotel_data['price'] = cheapest_hotel_price
        data['items'].append(hotel_data)

    return Response(data)


        