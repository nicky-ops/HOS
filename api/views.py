from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Driver, Trip, DutyStatus, DailyLog
from .serializers import DriverSerializer, TripSerializer, DutyStatusSerializer, DailyLogSerializer
from .hos_calculator import calculate_hos_compliance
from .services.openroute import OpenRouteService


def calculate_route(start, pickup, dropoff):
    '''
    Calculate route data using OpenRouteService API
    Args:
        start: dict - start location coordinates
        pickup: dict - pickup location coordinates
        dropoff: dict - dropoff location coordinates
    Returns:
        dict - route data
    '''
    ors = OpenRouteService()

    # Convert address to coordinates using ORS geocoding if needed
    if 'lat' not in start:
        start = ors.geocode(start)
    if 'lat' not in pickup:
        pickup = ors.geocode(pickup)
    if 'lat' not in dropoff:
        dropoff = ors.geocode(dropoff)
    start_coords = {'lat': start['lat'], 'lng': start['lng']}
    pickup_coords = {'lat': pickup['lat'], 'lng': pickup['lng']}
    dropoff_coords = {'lat': dropoff['lat'], 'lng': dropoff['lng']}

    try:
        route = ors.get_route(start_coords, pickup_coords, dropoff_coords)
        return {
            'distance': route['distance'],
            'duration': route['duration'],
            'coordinates': decode_polyline(route['geometry']),
            'instructions': route['instructions']
        }

    except Exception as e:
        logger.error(f"Error calculating route: {e}")
        raise


class TripViewSet(viewsets.ModelViewSet):
    '''
    API endpoint that allows trips to be viewed or edited
    '''
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

    def create(self, request):
        '''
        Create a new trip
        '''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Calculate using Mapbox API
        route_data = calculate_route(
            serializer.validated_data['start_location'],
            serializer.validated_data['pickup_location'],
            serializer.validated_data['dropoff_location']
        )

        # Calculate HOS compliance
        hos_data = calculate_hos_compliance(
            driver_id = serializer.validated_data['driver'],
            distance = route_data['distance'],
            duration = route_data['duration']
            current_cycle_used = serializer.validated_data['current_cycle_used']
        )

        trip = serializer.save(
            distance_miles = route_data['distance'],
            estimated_duration_hours = route_data['duration']
        )

        return Response({
            'trip': TripSerializer(trip).data,
            'hos_compliance': hos_data,
            'route': route_data
        }, status=status.HTTP_201_CREATED)


class DailyLogViewSet(viewsets.ModelViewSet):
    '''
    API endpoint that allows daily logs to be viewed or edited
    '''
    queryset = DailyLog.objects.all()
    serializer_class = DailyLogSerializer

    def generate_log(self, request, trip_id):
        '''
        Generate a daily log for a trip
        '''
        trip = Trip.objects.get(pk=trip_id)
        duty_statuses = DutyStatus.objects.filter(trip=trip).order_by('start_time')

        # Generate log grid data
        log_data = generate_log_grid(tip, duty_statuses)
        
        return Response(log_data, status=status.HTTP_200_OK)