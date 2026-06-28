import os
from email.policy import default

from django.conf import settings
from django.db.models import Sum, Avg,F, Count, ExpressionWrapper,DecimalField

from django.shortcuts import render

# Create your views here.
from django.http import FileResponse
from django.shortcuts import render
from . import utils
from .forms import UploadForm, DateFilterForm
from .models import Product


# from .forms import UploadForm,DateFilterForm
# from .models import Product


def dashboard(request):
    kpi=Product.objects.aggregate(
        products=Count('id'),
        total_qty=Sum('quantity'),
        avg_price=Avg('price'),
    )

    revenue_exr=ExpressionWrapper(F('price')*F('quantity'),
                                  output_field=DecimalField(max_digits=12,decimal_places=2))

    top_cats=(Product.objects
              .values("category")
              .annotate(revenue=Sum(revenue_exr),items=Count("id"))
              .order_by("-revenue")[:5]
              )

    return render(request,"products/dashboard.html",{"kpi":kpi,"top_cats":top_cats})

def product_upload(request):
    ctx={"form":UploadForm()}
    if request.method=="POST":
        form=UploadForm(request.POST,request.FILES)
        if form.is_valid():
            up=request.FILES["file"]
            sheet=form.cleaned_data.get("sheet_name") or None
            updir=os.path.join(settings.MEDIA_ROOT,"uploads")
            os.makedirs(updir,exist_ok=True)
            fpath=os.path.join(updir,up.name)
            with open(fpath,"wb+") as dest:
                for ch in up.chunks():
                    dest.write(ch)

            try:
                df=utils.read_any(fpath,sheet)
            except ValueError:
                ctx["error"]="Bele bir sheet tapilmadi. Sheet adini duzgun yazin ve ya bos buraxin."
                return render(request,"products/upload.html",ctx)
            df=utils.normalize_for_product(df)

            rows=df.to_dict("records")
            if len(rows)==1:
                r=rows[0]

                Product.objects.update_or_create(
                    sku=r["sku"],
                    defaults=dict(
                        name=r["name"],
                        price=r["price"],
                        quantity=int(r["quantity"]),
                        category=r.get("category") or "",
                        tx_date=r["tx_date"],
                    )
                )

            elif len(rows)>1:
                for r in rows:
                    Product.objects.update_or_create(
                        sku=r["sku"],
                        defaults=dict(
                            name=r["name"],
                            price=r["price"],
                            quantity=int(r["quantity"]),
                            category=r.get("category") or "",
                            tx_date=r["tx_date"],
                        )
                    )

            ctx["msg"]=f"Uploaded : {len(rows)} rows"

    return render(request,"products/upload.html",ctx)


def product_list(request):
    form=DateFilterForm(request.GET or None)
    qs=Product.objects.all().order_by("-tx_date","-id")

    if form.is_valid():
        nm=form.cleaned_data.get("name")
        qmin=form.cleaned_data.get("quantity_min")
        qmax=form.cleaned_data.get("quantity_max")
        df=form.cleaned_data.get("date_from")
        dt=form.cleaned_data.get("date_to")
        cat=form.cleaned_data.get("category")

        if nm:
            qs=qs.filter(name__icontains=nm)
        if qmin is not None:
            qs=qs.filter(quantity__gte=qmin)
        if qmax is not None:
            qs=qs.filter(quantity__lte=qmax)
        if df:
            qs=qs.filter(tx_date__gte=df)
        if dt:
            qs=qs.filter(tx_date__lte=dt)
        if cat:
            qs=qs.filter(category__icontains=cat)

    return render(request,"products/product_list.html",{"qs":qs,"form":form})

def product_download(request):
    file_path = os.path.join(
        settings.MEDIA_ROOT,
        "products",
        "product_template.xlsx"
    )
    return FileResponse(open(file_path,"rb"),as_attachment=True,filename="product_template.xlsx")