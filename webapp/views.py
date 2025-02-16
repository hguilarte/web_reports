from django.shortcuts import render
from django.db import connection
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    return render(request, 'webapp/home.html')

#############################################
def show_query_result(request):
    context = {}
    if request.method == 'POST':
        with connection.cursor() as cursor:
            query = "select CENTER, PLAN, MEMBNAME from webreports.caphistoric_report_to_use_1year where age BETWEEN 60 and 62 and sex = 'F';"
            cursor.execute(query)
            rows = cursor.fetchall()
        context['rows'] = rows
    return render(request, 'webapp/table_page.html', context)


import csv
from django.http import HttpResponse

#############################################
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="resultados.csv"'

    writer = csv.writer(response)
    # Escribe la cabecera
    writer.writerow(['CENTER', 'PLAN', 'MEMBNAME'])

    with connection.cursor() as cursor:
        query = "select CENTER, PLAN, MEMBNAME from webreports.caphistoric_report_to_use_1year where age BETWEEN 60 and 62 and sex = 'F';"
        cursor.execute(query)
        for row in cursor.fetchall():
            writer.writerow(row)

    return response

from django.template.loader import get_template
from xhtml2pdf import pisa

#############################################
def export_pdf(request):
    # Ejecuta el query para obtener los datos
    with connection.cursor() as cursor:
        query = "select CENTER, PLAN, MEMBNAME from webreports.caphistoric_report_to_use_1year where age BETWEEN 60 and 62 and sex = 'F';"
        cursor.execute(query)
        rows = cursor.fetchall()

    # Prepara el template HTML para el PDF
    template = get_template('webapp/pdf_template.html')
    context = {'rows': rows}
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="resultados.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF')
    return response

############################################
from django.db.models import Sum
from django.shortcuts import render
from .models import CapHistoricReport
def cap_pivot_view(request):
    pivot_data = (
        CapHistoricReport.objects.values('plan', 'capmo')
        .annotate(total_mbshp=Sum('mbshp'))
        .order_by('plan', 'capmo')
    )

    pivot_dict = {}
    capmo_labels = set()

    for row in pivot_data:
        plan = row['plan']
        capmo = row['capmo']
        total_mbshp = row['total_mbshp']

        if plan not in pivot_dict:
            pivot_dict[plan] = {}

        pivot_dict[plan][capmo] = total_mbshp
        capmo_labels.add(capmo)

    pivot_list = []
    for plan, capmo_data in pivot_dict.items():
        row_data = {"plan": plan}
        for capmo in capmo_labels:
            row_data[capmo] = capmo_data.get(capmo, 0)
        pivot_list.append(row_data)

    context = {
        'pivot_list': pivot_list,
        'capmo_labels': sorted(capmo_labels),
    }

    # 🛑 Verifica qué datos se están enviando al template
    print("PIVOT TABLE DATA:", context)

    return render(request, 'webapp/cap_pivot.html', context)

############################################
from webapp.models import CapHistoricReport

def cap_detail_view(request, plan, capmo):
    data = CapHistoricReport.objects.filter(plan=plan, capmo=capmo)

    return render(request, 'webapp/cap_detail.html', {'data': data, 'plan': plan, 'capmo': capmo})

