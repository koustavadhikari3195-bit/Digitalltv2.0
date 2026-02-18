from django import forms


# Known disposable email domains to block
DISPOSABLE_DOMAINS = {
    "guerrillamail.com", "mailinator.com", "tempmail.com", "throwaway.email",
    "yopmail.com", "10minutemail.com", "trashmail.com", "maildrop.cc",
    "dispostable.com", "fakeinbox.com", "sharklasers.com", "guerrillamailblock.com",
    "grr.la", "guerrillamail.info", "guerrillamail.net", "spam4.me",
    "temp-mail.org", "tempail.com", "tmpmail.org", "tmpmail.net",
}


class LeadCaptureForm(forms.Form):
    name = forms.CharField(max_length=100, strip=True)
    email = forms.EmailField(max_length=254)
    website = forms.URLField(max_length=2000, required=False)

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        domain = email.split("@")[-1]
        if domain in DISPOSABLE_DOMAINS:
            raise forms.ValidationError("Please use a real email address, not a disposable one.")
        return email

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if len(name) < 2:
            raise forms.ValidationError("Name must be at least 2 characters.")
        return name
