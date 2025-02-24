from django.shortcuts import render
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.apps import apps
from django.db.models.functions import Cast, TruncYear, TruncMonth
from xhtml2pdf import pisa
from django.views.generic import TemplateView
from .models import CapHistoricReport
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Value
from django.db.models.functions import Cast
from django.db.models import IntegerField, DateField
from django.views.generic import TemplateView
from django.db.models import Sum
from datetime import datetime, timedelta
import io
import csv

# ✅ Main Dashboard Page
@login_required
def home(request):
    return render(request, 'webapp/home.html')

#############################################
# ✅ Export to CSV (Handles Both 12-Months and Yearly Reports)
def export_to_csv(request, model_name):
    """ Exports either the last 12 months or the selected year of the report to CSV """

    # Determine the source (cap_pivot or cap_yearly)
    origin = request.GET.get('origin', 'cap_pivot')  # Default to cap_pivot

    # Retrieve the correct filtered data from the session
    if origin == 'cap_yearly':
        pivot_list = request.session.get('yearly_report_data', [])
        field_names = request.session.get('yearly_field_names', [])
    else:
        pivot_list = request.session.get('report_data', [])
        field_names = request.session.get('field_names', [])

    if not pivot_list:
        return HttpResponse("No data available to export", status=400)

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{model_name}_{origin}_report.csv"'

    writer = csv.writer(response)
    writer.writerow(field_names)  # Write headers

    for row in pivot_list:
        writer.writerow([row.get(field, "") for field in field_names])  # Keep empty values as blank

    return response


# ✅ Export to PDF (Handles Both 12-Months and Yearly Reports)
def export_to_pdf(request, model_name):
    """ Exports either the last 12 months or the selected year of the report to PDF """

    # Determine the source (cap_pivot or cap_yearly)
    origin = request.GET.get('origin', 'cap_pivot')  # Default to cap_pivot

    # Retrieve the correct filtered data from the session
    if origin == 'cap_yearly':
        report_data = request.session.get('yearly_report_data', [])
        field_names = request.session.get('yearly_field_names', [])
    else:
        report_data = request.session.get('report_data', [])
        field_names = request.session.get('field_names', [])

    if not report_data:
        return HttpResponse("No data available to export", status=400)

    # Load the PDF template
    template = get_template('webapp/export_generic_pdf.html')
    html_content = template.render({'field_names': field_names, 'report_data': report_data})

    # Generate PDF
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{model_name}_{origin}_report.pdf"'

    return response

#############################################
# ✅ Detailed Membership Report View
def cap_detail_view(request, plan, capmo):
    try:
        capmo_date = datetime.strptime(capmo, "%b-%Y").strftime("%Y-%m-01")
    except ValueError:
        return HttpResponse("Invalid date format", status=400)

    # 🔹 Filtrar los datos de la tabla detallada
    data = CapHistoricReport.objects.filter(plan=plan, capmo=capmo_date)

    # 🔹 Detectar de dónde viene el usuario (cap_pivot o cap_yearly)
    origin = request.GET.get('origin', 'cap_pivot')

    # 🔹 Guardar la data en la sesión para exportación
    request.session['detail_report_data'] = list(data.values())  # Convertir queryset a lista de diccionarios
    request.session['detail_field_names'] = [
        "center", "plan", "lob", "mbshp", "id", "hic_num", "mcaid_num",
        "membname", "dob", "age", "sex", "address", "city", "st", "zip",
        "county", "phonenumber", "capmo", "pcpname"
    ]

    context = {
        'data': data,
        'plan': plan,
        'capmo': capmo,
        'origin': origin,  # Pasar el valor de origen
        'report_model': 'CapHistoricReport' if data.exists() else None  # 🔹 Solo asignar si hay datos
    }

    return render(request, 'webapp/cap_detail.html', context)

#############################################
# ✅ Main Pivot Table Report View
class CapPivotView(TemplateView):
    template_name = "webapp/cap_pivot.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 🔹 Calcular la fecha de hace 12 meses desde el mes actual
        today = now().date()
        twelve_months_ago = today - relativedelta(months=11)  # 11 para incluir el actual

        # 🔹 Filtrar solo los últimos 12 meses
        pivot_data = (
            CapHistoricReport.objects
            .filter(capmo__gte=twelve_months_ago.strftime("%Y-%m-01"))  # Solo los últimos 12 meses
            .values('plan', 'capmo')
            .annotate(total_mbshp=Sum('mbshp'))
            .order_by('plan', 'capmo')
        )

        pivot_dict = {}
        capmo_labels = set()
        total_by_month = {}

        for row in pivot_data:
            plan = row['plan']
            capmo_date = row['capmo']
            capmo_str = datetime.strptime(str(capmo_date), "%Y-%m-%d").strftime("%b-%Y")

            capmo_labels.add(capmo_str)

            if plan not in pivot_dict:
                pivot_dict[plan] = {}

            pivot_dict[plan][capmo_str] = row['total_mbshp']

            total_by_month[capmo_str] = total_by_month.get(capmo_str, 0) + row['total_mbshp']

        # 🔹 Ordenar los labels cronológicamente
        sorted_capmo_labels = sorted(capmo_labels, key=lambda x: datetime.strptime(x, "%b-%Y"))

        pivot_list = [
            {"plan": plan, **{capmo: pivot_dict[plan].get(capmo, 0) for capmo in sorted_capmo_labels}}
            for plan in pivot_dict
        ]

        # 🔹 Guardamos solo los últimos 12 meses en la sesión para exportación
        field_names = ['plan'] + sorted_capmo_labels
        self.request.session['report_data'] = pivot_list
        self.request.session['field_names'] = field_names

        context.update({
            'pivot_list': pivot_list,
            'capmo_labels': sorted_capmo_labels,
            'total_by_month': total_by_month,
            'report_model': 'CapHistoricReport',
        })

        return context

#############################################
# ✅ API Endpoint: Membership Data for Chart.js Doughnut Chart
def get_membership_data(request):
    """
    Returns membership data in JSON format, grouped by month and year.
    Filters only the last 12 months (including the current month).
    """
    today = now().date().replace(day=1)  # ✅ First day of the current month
    twelve_months_ago = today - relativedelta(months=11)  # ✅ Ensures exactly 12 months

    membership_data = (
        CapHistoricReport.objects
        .annotate(capmo_date=Cast('capmo', DateField()))
        .filter(capmo_date__gte=twelve_months_ago)  # ✅ Now correctly includes 12 months
        .annotate(year=TruncYear('capmo_date'), month=TruncMonth('capmo_date'))
        .values('year', 'month', 'plan')
        .annotate(total_members=Sum('mbshp'))
        .order_by('-year', '-month')
    )

    data = {}
    for entry in membership_data:
        year = entry['year'].year
        month = str(entry['month'].month).zfill(2)
        plan = entry['plan']
        members = entry['total_members']

        date_key = f"{year}-{month}"

        if date_key not in data:
            data[date_key] = {'plans': {}, 'total': 0}

        data[date_key]['plans'][plan] = members
        data[date_key]['total'] += members

    return JsonResponse(data)

##########################################
# ✅ CapYearlyView Report View
class CapYearlyView(TemplateView):
    template_name = "webapp/cap_yearly.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_year = int(self.request.GET.get("year", datetime.today().year))

        # 🔹 Generar una lista de los 12 meses del año seleccionado en formato "MMM-YYYY"
        full_months = [(datetime(selected_year, month, 1).strftime("%b-%Y")) for month in range(1, 13)]

        # 🔹 Convertir capmo a DateField para procesarlo correctamente
        pivot_data = (
            CapHistoricReport.objects
            .annotate(capmo_date=Cast('capmo', DateField()))  # ✅ Convertimos capmo en fecha real
            .filter(capmo_date__year=selected_year)  # ✅ Filtrar por el año seleccionado
            .annotate(membership=Cast('mbshp', IntegerField()))  # ✅ Asegurar que mbshp es numérico
            .values('plan', 'capmo_date')
            .annotate(total_members=Sum('membership'))  # ✅ Sumar membresía correctamente
            .order_by('plan', 'capmo_date')
        )

        pivot_dict = {}
        total_by_month = {month: 0 for month in full_months}  # ✅ Inicializar los totales con 0

        for row in pivot_data:
            plan = row['plan']
            capmo_date = row['capmo_date']  # ✅ Ya es un DateField válido
            capmo_str = capmo_date.strftime("%b-%Y")  # ✅ Convertir a "MMM-YYYY"

            if plan not in pivot_dict:
                pivot_dict[plan] = {month: "" for month in full_months}  # ✅ Asegurar los 12 meses vacíos

            pivot_dict[plan][capmo_str] = row['total_members'] or ""  # ✅ Asignar valor o vacío

            # 🔹 Sumar al total del mes
            if row['total_members']:  # ✅ Solo sumar si hay un valor
                total_by_month[capmo_str] += row['total_members']

        sorted_capmo_labels = full_months  # ✅ Siempre mostrar los 12 meses

        pivot_list = [
            {"plan": plan, **{capmo: pivot_dict[plan].get(capmo, "") for capmo in sorted_capmo_labels}}
            for plan in pivot_dict
        ]

        field_names = ['plan'] + sorted_capmo_labels

        # ✅ Guardar los datos en la sesión para exportaciones
        self.request.session['report_data'] = pivot_list
        self.request.session['field_names'] = field_names

        context.update({
            'pivot_list': pivot_list,
            'capmo_labels': sorted_capmo_labels,
            'total_by_month': {k: (v if v > 0 else "") for k, v in total_by_month.items()},  # ✅ Totales vacíos si son 0
            'selected_year': selected_year,
            'available_years': CapHistoricReport.objects.annotate(
                capmo_date=Cast('capmo', DateField())
            ).dates('capmo_date', 'year', order='DESC'),
            'report_model': 'CapHistoricReport',
        })

        return context
#############################################
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def status_pivot_view(request):
    """ Renderiza el reporte de Enrollments """
    return render(request, 'webapp/status_pivot.html')

@login_required
def status_pivot_dis_view(request):
    """ Renderiza el reporte de Disenrollments """
    return render(request, 'webapp/status_pivot_dis.html')

def cap_detail_view(request, plan, capmo):
    try:
        capmo_date = datetime.strptime(capmo, "%b-%Y").strftime("%Y-%m-01")
    except ValueError:
        return HttpResponse("Invalid date format", status=400)

    # 🔹 Filtrar los datos de la tabla detallada
    data = CapHistoricReport.objects.filter(plan=plan, capmo=capmo_date)

    # 🔹 Detectar de dónde viene el usuario (cap_pivot o cap_yearly)
    origin = request.GET.get('origin', 'cap_pivot')

    # 🔹 Guardar la data en la sesión para exportación
    request.session['detail_report_data'] = list(data.values())  # Convertir queryset a lista de diccionarios
    request.session['detail_field_names'] = [
        "center", "plan", "lob", "mbshp", "id", "hic_num", "mcaid_num",
        "membname", "dob", "age", "sex", "address", "city", "st", "zip",
        "county", "phonenumber", "capmo", "pcpname"
    ]

    context = {
        'data': data,
        'plan': plan,
        'capmo': capmo,
        'origin': origin,  # Pasar el valor de origen
        'report_model': 'CapHistoricReport' if data.exists() else None  # 🔹 Solo asignar si hay datos
    }

    return render(request, 'webapp/cap_detail.html', context)

# ✅ Export Detail Report to CSV
def export_detail_to_csv(request, plan, capmo):
    """ Exports the detail report to CSV """

    # Obtener los datos de la sesión (para garantizar que sean los mismos del reporte)
    detail_data = request.session.get('detail_report_data', [])
    field_names = request.session.get('detail_field_names', [])

    if not detail_data:
        return HttpResponse("No data available to export", status=400)

    # Crear la respuesta CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{plan}_{capmo}_detail_report.csv"'

    writer = csv.writer(response)
    writer.writerow(field_names)  # Escribir los encabezados

    # Escribir filas de datos
    for row in detail_data:
        writer.writerow([row.get(field, "") for field in field_names])

    return response


# ✅ Export Detail Report to PDF
def export_detail_to_pdf(request, plan, capmo):
    """ Exports the detail report to PDF """

    # Obtener los datos de la sesión
    detail_data = request.session.get('detail_report_data', [])
    field_names = request.session.get('detail_field_names', [])

    if not detail_data:
        return HttpResponse("No data available to export", status=400)

    # Cargar la plantilla PDF
    template = get_template('webapp/export_generic_pdf.html')
    html_content = template.render({'field_names': field_names, 'report_data': detail_data})

    # Generar el PDF
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{plan}_{capmo}_detail_report.pdf"'

    return response
