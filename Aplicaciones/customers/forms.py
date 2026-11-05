from django import forms

from . import models


class ClienteForm(forms.Form):
    """Datos del propietario, tanto para creación como para edición."""

    nombre = forms.CharField(
        label='Nombres', max_length=15,
        widget=forms.TextInput(attrs={'placeholder': 'Nombres del propietario'}))
    apellido = forms.CharField(
        label='Apellidos', max_length=15,
        widget=forms.TextInput(attrs={'placeholder': 'Apellidos del propietario'}))
    tipo_documento = forms.ChoiceField(
        label='Tipo de documento', choices=models.Cliente.TipoDocumento.choices)
    numero_documento = forms.CharField(
        label='Número de documento', max_length=15,
        widget=forms.TextInput(attrs={'placeholder': 'Número de identificación'}))
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'}))
    telefono = forms.CharField(
        label='Teléfono', max_length=25,
        widget=forms.TextInput(attrs={'placeholder': 'Número de contacto'}))
    direccion = forms.CharField(
        label='Dirección', max_length=200, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Dirección de residencia'}))

    def __init__(self, *args, instance=None, **kwargs):
        self.instance = instance
        if instance and not args and 'initial' not in kwargs:
            kwargs['initial'] = {
                'nombre': instance.nombre,
                'apellido': instance.apellido,
                'tipo_documento': instance.tipo_documento,
                'numero_documento': instance.numero_documeto,
                'email': instance.email,
                'telefono': instance.telefono,
                'direccion': instance.direccion,
            }
        super().__init__(*args, **kwargs)

    def save(self):
        cliente = self.instance or models.Cliente()
        cliente.nombre = self.cleaned_data['nombre'].strip()
        cliente.apellido = self.cleaned_data['apellido'].strip()
        cliente.tipo_documento = self.cleaned_data['tipo_documento']
        cliente.numero_documeto = self.cleaned_data['numero_documento'].strip()
        cliente.email = self.cleaned_data['email'].strip().lower()
        cliente.telefono = self.cleaned_data['telefono'].strip()
        cliente.direccion = self.cleaned_data.get('direccion', '').strip()
        if self.instance is None:
            cliente.mascotas = []
        cliente.save()
        return cliente


'''Formulario para recibir los mensajes de contacto de la página principal'''
class ContactoForm(forms.ModelForm):
    class Meta:
        model = models.Contacto
        fields = ['nombre', 'numero_contacto', 'email', 'mensaje']
        labels = {
            'nombre': 'Nombre',
            'numero_contacto': 'Número de contacto',
            'email': 'Correo electrónico',
            'mensaje': 'Mensaje',
        }
        widgets = {
            'mensaje': forms.Textarea(attrs={'rows': 4}),
        }
