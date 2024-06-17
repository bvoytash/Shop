from django.shortcuts import render

from rest_framework import viewsets, filters
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer
from django_filters.rest_framework import DjangoFilterBackend


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from .models import Order
from datetime import datetime


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['title', 'price']
    ordering_fields = ['title', 'price']
    search_fields = ['title']


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['date']
    ordering_fields = ['date']
    search_fields = ['date']


@api_view(['GET', 'POST'])
def stats_view(request):
    if request.method == 'POST':
        date_start = request.data.get('date_start')
        date_end = request.data.get('date_end')
        metric = request.data.get('metric')
    else:
        date_start = request.GET.get('date_start')
        date_end = request.GET.get('date_end')
        metric = request.GET.get('metric')

    if not date_start or not date_end or not metric:
        return Response({"error": "date_start, date_end, and metric are required parameters."}, status=400)

    try:
        date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
    except ValueError:
        return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    if date_start > date_end:
        return Response({"error": "date_start must be before date_end."}, status=400)

    if metric not in ['price', 'count']:
        return Response({"error": "Invalid metric. Choose either 'price' or 'count'."}, status=400)

    orders = Order.objects.filter(date__range=[date_start, date_end])

    if metric == 'price':
        stats = orders.annotate(month=TruncMonth('date')).values('month').annotate(value=Sum('products__price')).order_by('month')
    elif metric == 'count':
        stats = orders.annotate(month=TruncMonth('date')).values('month').annotate(value=Count('products')).order_by('month')

    result = [{'month': stat['month'].strftime('%Y %b'), 'value': stat['value']} for stat in stats]

    return Response(result)



