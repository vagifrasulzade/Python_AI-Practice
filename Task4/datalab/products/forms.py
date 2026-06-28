from django import forms

class UploadForm(forms.Form):
    file=forms.FileField(help_text="Excel/CSV (xlsx,xls,csv)")
    sheet_name=forms.CharField(required=False)

class DateFilterForm(forms.Form):
    name=forms.CharField(required=False,label="Name")
    quantity_min=forms.IntegerField(required=False,label="Count (min)",widget=forms.NumberInput(attrs={'min':0}))
    quantity_max=forms.IntegerField(required=False,label="Count (max)",widget=forms.NumberInput(attrs={'min':0}))
    date_from=forms.DateField(required=False,widget=forms.DateInput(attrs={'type':'date'}))
    date_to=forms.DateField(required=False,widget=forms.DateInput(attrs={'type':'date'}))
    category=forms.CharField(required=False)