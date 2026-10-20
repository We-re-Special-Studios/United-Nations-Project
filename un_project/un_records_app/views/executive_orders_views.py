from django.shortcuts import render, get_object_or_404
from ..models import ExecutiveOrder

def executive_orders(request):
    executive_orders = ExecutiveOrder.objects.all().order_by('-charter', '-date', '-number')
    return render(request, 'executive_orders.html', {'executive_orders': executive_orders})


def executive_order_detail(request, charter, number):
    executive_order = get_object_or_404(ExecutiveOrder.objects.select_related('ordered_by'), charter=charter, number=number)
    return render(request, 'executive_order_detail.html', {'executive_order': executive_order})