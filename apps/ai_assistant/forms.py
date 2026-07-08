from django import forms


class ChatMessageForm(forms.Form):
    message = forms.CharField(max_length=2000, widget=forms.Textarea)
    conversation_id = forms.IntegerField(required=False)

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if not message:
            raise forms.ValidationError("Message cannot be empty.")
        return message
