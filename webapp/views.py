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
