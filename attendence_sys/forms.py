from distutils.command.upload import upload
import profile
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *

class CreateStudentForm(ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(CreateStudentForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    
class FacultyForm(ModelForm):
    class Meta:
        model = Faculty
        fields = '__all__'
        exclude = ['user']
    def __init__(self, *args, **kwargs):
        super(FacultyForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'    

class NewUserForm(UserCreationForm):
    email = forms.EmailField(
        max_length=100,
        required = True,
        
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        )
    first_name = forms.CharField(
        max_length=100,
        required = True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
        )
    last_name = forms.CharField(
        max_length=100,
        required = True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        )
    username = forms.CharField(
        max_length=200,
        required = True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        )
    password1 = forms.CharField(
        required = True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        )
    password2 = forms.CharField(
        required = True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password Again'}),
        )
    class Meta:
        model = User
        fields = ("username", "email","first_name","last_name", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user