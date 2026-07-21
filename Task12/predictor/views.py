import time

from django.shortcuts import render

from . import ml


def index(request):
    result = None
    stamp = None          # cache-buster for the per-user images

    if request.method == "POST":
        age = int(request.POST["age"])
        bmi = float(request.POST["bmi"])
        glucose = float(request.POST["glucose"])
        bp = float(request.POST["bp"])
        family = int(request.POST["family"])
        exercise = int(request.POST["exercise"])

        result = ml.predict(age, bmi, glucose, bp, family, exercise)

        # per-user charts (gauge + personal SHAP)
        ml.make_gauge(result["xgb"])
        ml.make_user_shap(result["row"])
        stamp = int(time.time())

    return render(request, "predictor/index.html",
                  {"result": result, "stamp": stamp})
