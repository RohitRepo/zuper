from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required


def site_main(request):
    if request.user.is_authenticated():
        return redirect('/web')
    else:
        context = RequestContext(request)
        return render_to_response("login.html", context)

@login_required
def orders_portal(request):
    print request.user
    context = RequestContext(request)
    return render_to_response("orders.html", context)