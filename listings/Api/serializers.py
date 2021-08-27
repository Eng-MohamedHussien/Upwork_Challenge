from rest_framework import serializers

from ..models import Listing


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['listing_type', 'title', 'country', 'city']


class ApartmentSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField('get_apartment_price')
    
    class Meta:
        model = Listing
        fields = ['listing_type', 'title', 'country', 'city', 'price']

    def get_apartment_price(self, apartment):
        price = apartment.booking_info.price
        return price

