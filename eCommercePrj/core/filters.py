import django_filters
from .models import Category, Brand, Product
from taggit.models import Tag
from django.db.models import Q
from django import forms

class ProductFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="search", label="Ara")
    
    category = django_filters.ModelChoiceFilter(to_field_name="cid", queryset=Category.objects.all(), empty_label="Tüm Kategoriler", widget=forms.RadioSelect(attrs={"class": "form-check-input"}))
    brand = django_filters.ModelChoiceFilter(queryset=Brand.objects.all().order_by('title'), empty_label="Tüm Markalar", widget=forms.RadioSelect(attrs={"class": "form-check-input brand_form"}))
    tags = django_filters.ModelChoiceFilter(field_name="tags", to_field_name="slug", queryset=Tag.objects.all().order_by('name'), empty_label="Tüm Etiketler", widget=forms.RadioSelect(attrs={"class": "form-check-input"}))
    
    min_price = django_filters.NumberFilter(widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Min fiyat"}), field_name="price", lookup_expr="gte", label="Min Fiyat")

    max_price = django_filters.NumberFilter(widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Max fiyat"}), field_name="price", lookup_expr="lte", label="Max Fiyat")

    sorting = django_filters.OrderingFilter(
        fields=(("price", "price"), ("title", "title"), ("date", "date")), 
        field_labels={
            "price": "En düşük fiyat", "-price": "En yüksek fiyat",
            "title": "İsim (A-Z)", "-title": "İsim (Z-A)",
            "date": "En eskiler", "-date": "En yeniler",
        },
        label="Sırala",
        empty_label="Önerilen",
        )
    class Meta:
        model = Product
        fields = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # form="filter-form": kutu sayfada formun disinda dursa da filtre formuna ait olsun
        # onchange: secim degisince form kendiliginden gonderilsin
        self.form.fields["sorting"].widget.attrs.update({
            "class": "form-select float-end custom-select",
            "form": "filter-form",
            "onchange": "this.form.submit()",
        })

        # Kullanici bir kategori sectiyse marka listesinde sadece o kategorinin markalari gorunsun
        category_cid = self.data.get("category")
        if category_cid:
            self.form.fields["brand"].queryset = Brand.objects.filter(categories__cid=category_cid).order_by("title")

    def search(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value) | Q(description__icontains=value) | Q(tags__name__icontains=value)).distinct()
    

