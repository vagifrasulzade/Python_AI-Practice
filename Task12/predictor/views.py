from django.shortcuts import render

from . import ml


def index(request):
    result = None

    if request.method == "POST":
        # Read the values from the simple HTML inputs
        age = int(request.POST["age"])
        bmi = float(request.POST["bmi"])
        glucose = float(request.POST["glucose"])
        bp = float(request.POST["bp"])
        family = int(request.POST["family"])
        exercise = int(request.POST["exercise"])

        result = ml.predict(age, bmi, glucose, bp, family, exercise)

    return render(request, "predictor/index.html", {"result": result})
