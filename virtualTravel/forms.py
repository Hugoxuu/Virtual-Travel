from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from virtualTravel.models import *

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length = 20, 
                widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password',max_length = 200, 
                widget = forms.PasswordInput(attrs={'class': 'form-control'}))

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username/password")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

class RegistrationForm(forms.Form):
    username = forms.CharField(label='Username', max_length = 20, 
                widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password',max_length = 200, 
                widget = forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password  = forms.CharField(label='Confirm Password',max_length = 200, 
                widget = forms.PasswordInput(attrs={'class': 'form-control'}))
    email    = forms.EmailField(label='Email', max_length=50,
                                widget = forms.EmailInput(attrs={'class': 'form-control'}))

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(RegistrationForm, self).clean()

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password')
        password2 = cleaned_data.get('confirm_password')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data


    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'picture')
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'picture': forms.FileInput(attrs={'class': 'custom-file-input'}),
        }

    def clean_picture(self):
        picture = self.cleaned_data['picture']
        return picture

class UserUploadForm_quiz(forms.ModelForm):
    quiz_city_name = forms.CharField( max_length = 20)
    class Meta:
        model=Quiz
        fields =('quiz_text','quiz_option_1','quiz_option_2','quiz_option_3','quiz_option_4','quiz_answer')
        widgets = {
            'quiz_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'quiz_option_1': forms.TextInput(attrs={'class': 'form-control'}),
            'quiz_option_2': forms.TextInput(attrs={'class': 'form-control'}),
            'quiz_option_3': forms.TextInput(attrs={'class': 'form-control'}),
            'quiz_option_4': forms.TextInput(attrs={'class': 'form-control'}),
            'quiz_answer': forms.NumberInput(attrs={'size': '10'}),
        }
        

    def clean_quiz_question(self):
        # Confirms that the quiz question is not already present in the
        # Quiz model database.
        quiz_text = self.cleaned_data.get('quiz_text')
        if Quiz.objects.filter(quiz_text__exact=quiz_text):
            raise forms.ValidationError("Quiz question is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return quiz_text

    def clean_quiz_answer(self):
        quiz_answer = self.cleaned_data['quiz_answer']
        if not quiz_answer:
            raise forms.ValidationError('You must provide an answer.')


class UserUploadForm_site(forms.ModelForm):
    city_name=forms.CharField()
    site_picture = forms.FileField()
    class Meta:
        model=Site
        fields=('description','name')
        widgets={'description':forms.Textarea(attrs={'class': 'form-control', 'rows': 3})}

    def clean_picture(self):
        site_picture = self.cleaned_data['city_picture']
        try:
            if not site_picture:
                raise forms.ValidationError('You must upload a picture')
            if not isinstance(site_picture,InMemoryUploadedFile):
                raise forms.ValidationError('You must upload a picture')
            if not site_picture.content_type or not site_picture.content_type.startswith('image'):
                raise forms.ValidationError('File type is not image')
            if site_picture.size > MAX_UPLOAD_SIZE:
                raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        except:
            pass
        return city_picture

