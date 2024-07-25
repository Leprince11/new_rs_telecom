from django import forms

class CompanyForm(forms.Form):
    nom = forms.CharField(label='Nom', max_length=100, widget=forms.TextInput(attrs={'id': 'nom', 'class': 'input-name' , 'name':'nom'}))
    nombre_offres = forms.IntegerField()
    taille = forms.CharField(max_length=100)
    secteur = forms.CharField(max_length=100)
    chiffre_d_affaires = forms.CharField(max_length=100)
    lien_site = forms.URLField()

from .models import Leads
class LeadsForm(forms.ModelForm):
    class Meta:
        model = Leads
        fields = [
            'nom', 'nom_offre', 'localisation_du_lead', 'nombre_offres', 'adresse_mail_de_contact', 'telephone',
            'taille_entreprise', 'secteur_activite', 'chiffre_d_affaires', 'lien_vers_lead', 'porteur_lead', 
            'url_profil_porteur_lead', 'source_lead', 'statut_du_lead', 'date_publication_offre', 'date_maj_lead',
            'remarques', 'priorite', 'description_job'
        ]

    def __init__(self, *args, **kwargs):
        super(LeadsForm, self).__init__(*args, **kwargs)
        # Rendre les quatre premiers champs obligatoires
        required_fields = ['nom', 'nom_offre', 'localisation_du_lead', 'nombre_offres']
        for field in required_fields:
            self.fields[field].required = True

        # rendre les autres champs pas obligatoire 
        for field_name in self.fields:
            if field_name not in required_fields:
                self.fields[field_name].required = False


