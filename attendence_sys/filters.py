from logging import PlaceHolder
import django_filters
from django.forms.widgets import DateInput
from django import forms
from django.forms import ModelForm
from .models import Attendence

class AttendenceFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(widget=forms.DateInput(attrs={'type':'Date'}))
    class Meta:
        model = Attendence
        fields = '__all__'
        exclude = ['Faculty_Name','status','time','branch','section']