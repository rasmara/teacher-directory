from django import forms


class BulkUploadForm(forms.Form):
    csv_file = forms.FileField(label="Upload required .csv file ",
                               widget=forms.FileInput(attrs={'accept': '.csv'}))
    images_archive = forms.FileField(label="Upload required .zip file",
                                     widget=forms.FileInput(
                                         attrs={'accept': '.zip'}))
