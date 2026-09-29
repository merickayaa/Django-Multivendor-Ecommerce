from core.models import Product
from django import forms


class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title',
            'image',
            'description',
            'price',
            'specifications',
            # 'stock_count',
            'category',
            'brand',
            # 'mfd',
            # 'tags',
        ]
    def __init__(self, *args, **kwargs):
        super(AddProductForm, self).__init__(*args, **kwargs)
        
        # Bootstrap sınıflarını form alanlarına ekliyoruz
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control mb-3'
        
        # Textarea için daha geniş alan veriyoruz
        self.fields['description'].widget.attrs['class'] = 'form-control mb-3'
        self.fields['description'].widget.attrs['rows'] = '4'
        
        # DateTime widget için daha iyi stil
        # self.fields['mfd'].widget.attrs['class'] = 'form-control mb-3'