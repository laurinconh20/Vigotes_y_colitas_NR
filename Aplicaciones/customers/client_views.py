from datetime import date

from bson.errors import InvalidId
from bson.objectid import ObjectId
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render

from . import forms
from . import models as customers


def _buscar_cliente(id_cliente):
    try:
        identificador = ObjectId(str(id_cliente))
    except (InvalidId, TypeError):
        raise Http404('El identificador del cliente no es válido')
    try:
        return customers.Cliente.objects.get(pk=identificador)
    except customers.Cliente.DoesNotExist:
        raise Http404('El cliente solicitado no existe')


def _edad(fecha_nacimiento):
    if not fecha_nacimiento:
        return None
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year
    return edad - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))


def _resumen_cliente(cliente):
    mascotas = []
    total_citas = total_vacunas = total_historiales = 0
    for mascota in (cliente.mascotas or []):
        citas = mascota.get('citas') or []
        vacunas = mascota.get('vacunas') or []
        historiales = mascota.get('historia_clinica') or []
        total_citas += len(citas)
        total_vacunas += len(vacunas)
        total_historiales += len(historiales)
        mascotas.append({
            'id': mascota.get('_id'), 'nombre': mascota.get('nombre'),
            'especie': mascota.get('especie'),
            'raza': mascota.get('raza') or 'Sin registrar',
            'edad': _edad(mascota.get('fecha_nacimiento')),
            'total_citas': len(citas),
        })
    return {'mascotas': mascotas, 'total_mascotas': len(mascotas),
            'total_citas': total_citas, 'total_vacunas': total_vacunas,
            'total_historiales': total_historiales}


def listar_clientes(request):
    termino = request.GET.get('q', '').strip().lower()
    todos = list(customers.Cliente.objects.all())
    seleccionados = [c for c in todos if not termino or termino in ' '.join([
        c.nombre, c.apellido, c.numero_documeto, c.email, c.telefono]).lower()]
    seleccionados.sort(key=lambda c: (c.nombre.lower(), c.apellido.lower()))
    registros = []
    for cliente in seleccionados:
        resumen = _resumen_cliente(cliente)
        registros.append({
            'id': cliente.pk, 'nombre': f'{cliente.nombre} {cliente.apellido}',
            'tipo_documento': cliente.get_tipo_documento_display(),
            'numero_documento': cliente.numero_documeto, 'email': cliente.email,
            'telefono': cliente.telefono, 'total_mascotas': resumen['total_mascotas'],
            'total_citas': resumen['total_citas']})
    return render(request, 'clientes-home.html', {
        'clientes': registros, 'total': len(registros), 'total_general': len(todos),
        'con_mascotas': sum(bool(c.mascotas) for c in todos),
        'sin_mascotas': sum(not bool(c.mascotas) for c in todos),
        'total_mascotas': sum(len(c.mascotas or []) for c in todos),
        'termino': request.GET.get('q', ''), 'titlePage': 'Clientes'})


def crear_cliente(request):
    formulario = forms.ClienteForm(request.POST or None)
    if request.method == 'POST' and formulario.is_valid():
        cliente = formulario.save()
        messages.success(request, 'Cliente registrado correctamente.')
        return redirect('customers:detalle_cliente', id_cliente=cliente.pk)
    return render(request, 'cliente-form.html', {
        'formulario': formulario, 'titulo': 'Registrar propietario',
        'boton': 'Guardar cliente', 'cliente': None, 'titlePage': 'Registrar cliente'})


def detalle_cliente(request, id_cliente):
    cliente = _buscar_cliente(id_cliente)
    return render(request, 'cliente-detail.html', {
        'cliente': cliente, 'resumen': _resumen_cliente(cliente),
        'titlePage': f'Cliente | {cliente.nombre}'})


def editar_cliente(request, id_cliente):
    cliente = _buscar_cliente(id_cliente)
    formulario = forms.ClienteForm(request.POST or None, instance=cliente)
    if request.method == 'POST' and formulario.is_valid():
        formulario.save()
        messages.success(request, 'Datos del cliente actualizados.')
        return redirect('customers:detalle_cliente', id_cliente=cliente.pk)
    return render(request, 'cliente-form.html', {
        'formulario': formulario, 'titulo': 'Editar propietario',
        'boton': 'Guardar cambios', 'cliente': cliente, 'titlePage': 'Editar cliente'})


def eliminar_cliente(request, id_cliente):
    cliente = _buscar_cliente(id_cliente)
    resumen = _resumen_cliente(cliente)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado correctamente.')
        return redirect('customers:listado_clientes')
    return render(request, 'cliente-delete.html', {
        'cliente': cliente, 'resumen': resumen, 'titlePage': 'Eliminar cliente'})
