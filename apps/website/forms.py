from django import forms
import dns.resolver

def check_mx_record(email):
    """Verify that the domain has valid MX records."""
    domain = email.split('@')[-1]
    try:
        dns.resolver.resolve(domain, 'MX')
        return True
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.LifetimeTimeout):
        return False


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
        
        if not check_mx_record(email):
             raise forms.ValidationError("This email domain does not seem to accept emails.")
             
        return email

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if len(name) < 2:
            raise forms.ValidationError("Name must be at least 2 characters.")

class InquiryForm(forms.ModelForm):
    from .models import Inquiry
    
    VALID_SERVICES = {
        "website_management",
        "social_media",
        "seo",
        "content_marketing",
        "graphic_design",
        "full_package",
    }
    
    services = forms.MultipleChoiceField(
        choices=[(v, v) for v in VALID_SERVICES],
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        from .models import Inquiry
        model = Inquiry
        fields = [
            "name",
            "email",
            "company",
            "phone",
            "website",
            "role",
            "services",
            "goals",
            "budget",
            "timeline",
            "source_channel",
            "notes",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        domain = email.split("@")[-1]
        if domain in DISPOSABLE_DOMAINS:
            raise forms.ValidationError("Disposable email addresses are not accepted.")

        if not check_mx_record(email):
             raise forms.ValidationError("Invalid email domain (no MX record found).")

        return email

    def clean_services(self):
        # Strict whitelist — never trust client-sent values
        return [s for s in self.cleaned_data.get("services", []) if s in self.VALID_SERVICES]
