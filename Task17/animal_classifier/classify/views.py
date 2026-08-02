import os
from django.conf import settings

from django.shortcuts import render
from .forms import ImageUploadForm
from .ml.model_loader import ImageNetClassifier

# Create your views here.

classifier = ImageNetClassifier()

def upload_view(request):
    form = ImageUploadForm()
    results = None
    image_url = None

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)

        if form.is_valid():
            image = form.cleaned_data['image']

            save_path = os.path.join(settings.MEDIA_ROOT,image.name)
            os.makedirs(settings.MEDIA_ROOT,exist_ok=True)

            with open(save_path,'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            image_url = settings.MEDIA_URL + image.name

            results = classifier.predict(save_path,5)

    context = {
        'form':form,
        'results': results,
        'image_url':image_url
    }
    return render(request,'classify/upload.html',context)

