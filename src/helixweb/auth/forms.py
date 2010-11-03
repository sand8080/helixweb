from django import forms


class LoginForm(forms.Form):
    environment_name = forms.CharField(max_length=32)
    login = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput(render_value=False),
        max_length=32)
    password_confirm = forms.CharField(widget=forms.PasswordInput(render_value=False),
        max_length=32, required=False)