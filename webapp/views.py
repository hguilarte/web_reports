from django.shortcuts import render
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.apps import apps
from django.db.models.functions import Cast, TruncYear, TruncMonth
from xhtml2pdf import pisa
from django.views.generic import TemplateView
from .models import CapHistoricReport, CapHistoricReportOneYear
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Value
from django.db.models import IntegerField, DateField
from datetime import datetime, timedelta
import io
import csv
from django.db.models import Count
import json
import calendar
import pandas as pd


# ✅ Main Dashboard Page
@login_required
def home(request):
    today = now().date().replace(day=1)  # ✅ Primer día del mes actual
    twelve_months_ago = today - relativedelta(months=11)  # ✅ Últimos 12 meses

    ### 🔹 1️⃣ OBTENER DATOS DE MEMBERSHIP
    membership_data = (
        CapHistoricReport.objects
        .annotate(capmo_date=Cast('capmo', DateField()))
        .filter(capmo_date__gte=twelve_months_ago)
        .annotate(year=TruncYear('capmo_date'), month=TruncMonth('capmo_date'))
        .values('year', 'month', 'plan')
        .annotate(total_members=Sum('mbshp'))
        .order_by('-year', '-month')
    )

    # ✅ Convertir los datos de MEMBERSHIP al formato correcto (Ej: "Mar 2025")
    membership_dict = {}
    for entry in membership_data:
        year = entry['year'].year
        month_abbr = entry['month'].strftime("%b")
        plan = entry['plan']
        members = entry['total_members']

        date_key = f"{month_abbr} {year}"  # ✅ "Mar 2025"

        if date_key not in membership_dict:
            membership_dict[date_key] = {'plans': {}, 'total': 0}

        membership_dict[date_key]['plans'][plan] = members
        membership_dict[date_key]['total'] += members

    membership_sorted = dict(sorted(membership_dict.items(), key=lambda x: datetime.strptime(x[0], "%b %Y"), reverse=True))

    ### 🔹 2️⃣ OBTENER DATOS DE STATUS
    months_data = {}
    for i in range(12):
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1
        month_date = datetime(year, month, 1)
        month_key = month_date.strftime("%b %Y")  # ✅ "Mar 2025"
        year_month_key = month_date.strftime("%Y-%m")  # ✅ "2025-03"

        # 🔹 Obtener conteo de estatus
        raw_status_counts = list(
            CapHistoricReportOneYear.objects
            .filter(capmo__startswith=year_month_key)
            .values('stat')
            .annotate(count=Count('id'))
        )

        status_dict = {"NEW": 0, "REENROL": 0, "TERM": 0, "TRANSFER": 0, "TRANSFER OUT": 0}
        for item in raw_status_counts:
            status = item.get('stat')
            count = item.get('count', 0)
            if status:
                if status == "TRANSFER IN":
                    status = "TRANSFER"
                if status in status_dict:
                    status_dict[status] = count

        months_data[month_key] = {'statusCounts': status_dict}

    ### 🔹 3️⃣ PASAR AMBOS DATOS A LA PLANTILLA
    context = {
        "user": request.user,
        "membership_data_json": json.dumps(membership_sorted),  # ✅ Membership en JSON
        "status_data_json": json.dumps(months_data),  # ✅ Status en JSON
    }
    return render(request, 'webapp/home.html', context)

# ✅ Export to Excel
def export_to_excel(request, model_name):
    """
    Exporta los datos del reporte a un archivo Excel.
    """
    origin = request.GET.get('origin', 'cap_pivot')

    # Asegurar que se exporta el reporte correcto
    if origin == "cap_pivot":
        pivot_list = request.session.get('pivot_report_data', [])
        field_names = request.session.get('pivot_field_names', [])
    elif origin == "cap_yearly":
        pivot_list = request.session.get('yearly_report_data', [])
        field_names = request.session.get('yearly_field_names', [])
    else:
        pivot_list = []
        field_names = []

    if not pivot_list:
        return HttpResponse("No data available to export", status=400)

    # Convertir los datos de la sesión en un DataFrame de pandas
    df = pd.DataFrame(pivot_list, columns=field_names)

    # Crear la respuesta HTTP con el contenido de Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{model_name}_{origin}_report.xlsx"'

    # Escribir el DataFrame en un archivo Excel
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Report Data")

    return response

# ✅ Detailed Membership Report View
def cap_detail_view(request, plan, capmo):
    try:
        capmo_date = datetime.strptime(capmo, "%b-%Y").strftime("%Y-%m")
    except ValueError:
        return HttpResponse("Invalid date format", status=400)

    if plan == 'TOTAL':
        data = CapHistoricReport.objects.filter(capmo__startswith=capmo_date, mbshp=1)
    else:
        data = CapHistoricReport.objects.filter(plan=plan, capmo__startswith=capmo_date, mbshp=1)

    if not data.exists():
        return HttpResponse(f"No data available for the selected period ({capmo}).", status=404)

    origin = request.GET.get('origin', 'cap_pivot')

    request.session['detail_report_data'] = list(data.values())
    request.session['detail_field_names'] = [
        "center", "plan", "lob", "mbshp", "id", "hic_num", "mcaid_num",
        "membname", "dob", "age", "sex", "address", "city", "st", "zip",
        "county", "phonenumber", "capmo", "pcpname"
    ]

    context = {
        'data': data,
        'plan': plan,
        'capmo': capmo,
        'origin': origin,
        'report_model': 'CapHistoricReport'
    }
    return render(request, 'webapp/cap_detail.html', context)

# ✅ Pivot Table Report View
class CapPivotView(TemplateView):
    template_name = "webapp/cap_pivot.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = now().date()
        twelve_months_ago = today - relativedelta(months=11)

        pivot_data = (
            CapHistoricReport.objects
            .filter(capmo__gte=twelve_months_ago.strftime("%Y-%m-01"), mbshp=1)
            .values('plan', 'capmo')
            .annotate(total_mbshp=Sum('mbshp'))
            .order_by('plan', 'capmo')
        )

        pivot_dict = {}
        capmo_labels = set()
        total_by_month = {}

        for row in pivot_data:
            capmo_str = datetime.strptime(str(row['capmo']), "%Y-%m-%d").strftime("%b-%Y")
            total_by_month[capmo_str] = total_by_month.get(capmo_str, 0) + row['total_mbshp']
            capmo_labels.add(capmo_str)

            if row['plan'] not in pivot_dict:
                pivot_dict[row['plan']] = {}
            pivot_dict[row['plan']][capmo_str] = row['total_mbshp']

        sorted_capmo_labels = sorted(capmo_labels, key=lambda x: datetime.strptime(x, "%b-%Y"))

        pivot_list = [
            {"plan": plan, **{capmo: pivot_dict[plan].get(capmo, 0) for capmo in sorted_capmo_labels}}
            for plan in pivot_dict
        ]

        # ✅ Limpiar los datos de cap_yearly para evitar que se mezclen
        self.request.session.pop('yearly_report_data', None)
        self.request.session.pop('yearly_field_names', None)

        # ✅ Guardar los datos en la sesión para exportaciones
        field_names = ['plan'] + sorted_capmo_labels  # Asegurar nombres de las columna

        self.request.session['pivot_report_data'] = pivot_list
        self.request.session['pivot_field_names'] = field_names

        context.update({
            'pivot_list': pivot_list,
            'capmo_labels': sorted_capmo_labels,
            'total_by_month': total_by_month,
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
        month_abbr = entry['month'].strftime("%b")  # ✅ Get abbreviated month (e.g., "Mar")
        plan = entry['plan']
        members = entry['total_members']

        date_key = f"{month_abbr} {year}"  # ✅ New format: "Mar 2025"

        if date_key not in data:
            data[date_key] = {'plans': {}, 'total': 0}

        data[date_key]['plans'][plan] = members
        data[date_key]['total'] += members

    # ✅ Order the data by month/year to maintain proper sorting
    sorted_data = dict(sorted(data.items(), key=lambda x: datetime.strptime(x[0], "%b %Y"), reverse=True))

    return JsonResponse(sorted_data)

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

        # ✅ Limpiar los datos de cap_pivot para evitar que se mezclen
        self.request.session.pop('pivot_report_data', None)
        self.request.session.pop('pivot_field_names', None)

        # ✅ Guardar los datos en la sesión para exportaciones
        field_names = ['plan'] + sorted_capmo_labels  # Asegurar nombres de las columna

        self.request.session['yearly_report_data'] = pivot_list
        self.request.session['yearly_field_names'] = field_names

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
@login_required
def status_pivot_view(request):
    """ Renderiza el reporte de Enrollments """
    return render(request, 'webapp/status_pivot.html')

@login_required
def status_pivot_dis_view(request):
    """ Renderiza el reporte de Disenrollments """
    return render(request, 'webapp/status_pivot_dis.html')

# 1. Agregar esta función en views.py (reemplazar la existente)
def status_data(request):
    """
    API endpoint to provide status distribution data for the bar chart
    """
    # Obtener fecha actual
    today = datetime.now()

    # Generar lista de los últimos 12 meses incluyendo el actual
    months_data = {}

    # Procesar los últimos 12 meses (0 = mes actual, 11 = hace 11 meses)
    for i in range(12):
        # Calcular año y mes
        year = today.year
        month = today.month - i

        # Ajustar año si el mes es negativo
        while month <= 0:
            month += 12
            year -= 1

        # Crear la fecha del primer día del mes
        month_date = datetime(year, month, 1)

        # Formato para mostrar y filtrar
        month_key = month_date.strftime("%b %Y")  # Ej: "Mar 2025"
        year_month_key = month_date.strftime("%Y-%m")  # Ej: "2025-03"

        print(f"Processing month {i + 1}/12: {month_key} (filter: {year_month_key})")

        # Consulta a la base de datos
        raw_status_counts = list(
            CapHistoricReportOneYear.objects
            .filter(capmo__startswith=year_month_key)
            .values('stat')
            .annotate(count=Count('id'))
        )

        print(f"Raw data for {month_key}: {raw_status_counts}")

        # Inicializar conteos en cero
        status_dict = {
            "NEW": 0,
            "REENROL": 0,
            "TERM": 0,
            "TRANSFER": 0,
            "TRANSFER OUT": 0
        }

        # Procesar datos de la consulta
        for item in raw_status_counts:
            status = item.get('stat')
            count = item.get('count', 0)

            if status:
                # Mapear "TRANSFER IN" a "TRANSFER"
                if status == "TRANSFER IN":
                    status = "TRANSFER"

                # Guardar conteo
                if status in status_dict:
                    status_dict[status] = count

        # Siempre incluir el mes en la respuesta
        months_data[month_key] = {
            'statusCounts': status_dict
        }

    # Verificación final
    print(f"Final months in response: {sorted(months_data.keys())}")

    return JsonResponse(months_data)

# 2. Agregar estas nuevas vistas para los reportes en views.py
@login_required
def status_all_plans_view(request):
    """
    Vista para el reporte de status agregado por todos los planes.
    """
    today = now().date().replace(day=1)  # Primer día del mes actual
    twelve_months_ago = today - relativedelta(months=11)  # Últimos 12 meses

    pivot_data = (
        CapHistoricReportOneYear.objects
        .filter(capmo__gte=twelve_months_ago.strftime("%Y-%m-01"))
        .values('stat', 'capmo')
        .annotate(total=Count('id'))
        .order_by('stat', 'capmo')
    )

    pivot_dict = {}
    capmo_labels = set()
    total_by_month = {}

    for row in pivot_data:
        capmo_str = datetime.strptime(str(row['capmo']), "%Y-%m-%d").strftime("%b-%Y")
        total_by_month[capmo_str] = total_by_month.get(capmo_str, 0) + row['total']
        capmo_labels.add(capmo_str)

        if row['stat'] not in pivot_dict:
            pivot_dict[row['stat']] = {}
        pivot_dict[row['stat']][capmo_str] = row['total']

    sorted_capmo_labels = sorted(capmo_labels, key=lambda x: datetime.strptime(x, "%b-%Y"))

    pivot_list = [
        {"stat": stat, **{capmo: pivot_dict[stat].get(capmo, 0) for capmo in sorted_capmo_labels}}
        for stat in pivot_dict
    ]

    context = {
        'pivot_list': pivot_list,
        'capmo_labels': sorted_capmo_labels,
        'total_by_month': total_by_month,
    }
    return render(request, 'webapp/status_all_plans.html', context)



@login_required
def status_by_plans_view(request):
    """
    Vista para el reporte de status desglosado por plan
    """
    # Preparar el contexto que enviaremos a la plantilla
    context = {
        'report_model': 'CapHistoricReportOneYear',
        'report_title': 'Member Status by Plan'
    }

    return render(request, 'webapp/status_by_plans.html', context)

# ✅ Export Detail Report to Excel
def export_detail_to_excel(request, plan, capmo):
    """
    Exporta los datos del detalle a un archivo Excel.
    """

    # Obtener los datos de la sesión (para garantizar que sean los mismos del reporte)
    detail_data = request.session.get('detail_report_data', [])
    field_names = request.session.get('detail_field_names', [])

    if not detail_data:
        return HttpResponse("No data available to export", status=400)

    # Convertir los datos en un DataFrame de pandas
    df = pd.DataFrame(detail_data, columns=field_names)

    # Crear la respuesta HTTP con el contenido de Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{plan}_{capmo}_detail_report.xlsx"'

    # Escribir el DataFrame en un archivo Excel
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Detail Report")

    return response

@login_required
def cap_detail_status_view(request, stat, capmo):
    """
    Vista para mostrar el detalle del reporte de estatus desde la tabla caphistoric_report_to_use_1year.
    """
    try:
        capmo_date = datetime.strptime(capmo, "%b-%Y").strftime("%Y-%m")
    except ValueError:
        return HttpResponse("Invalid date format", status=400)

    # Filtrar por STAT y CAPMO en la tabla caphistoric_report_to_use_1year
    data = CapHistoricReportOneYear.objects.filter(stat=stat, capmo__startswith=capmo_date)

    if not data.exists():
        return HttpResponse(f"No data available for the selected period ({capmo}).", status=404)

    # Guardar los datos en la sesión para la exportación
    request.session['detail_report_data'] = list(data.values())
    request.session['detail_field_names'] = [
        "center", "plan", "lob", "mbshp", "id", "hic_num", "mcaid_num",
        "membname", "dob", "age", "sex", "address", "city", "st", "zip",
        "county", "phonenumber", "capmo", "pcpname"
    ]

    context = {
        'data': data,
        'plan': stat,  # Usamos "stat" en lugar de plan
        'capmo': capmo,
        'origin': request.GET.get('origin', 'status_pivot'),
        'report_model': 'CapHistoricReportOneYear'
    }
    return render(request, 'webapp/cap_detail_status.html', context)
