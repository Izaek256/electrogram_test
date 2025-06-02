import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserActivity

@csrf_exempt
def track_click(request):
    if request.method == "POST":
        data = json.loads(request.body)
        UserActivity.objects.create(
            user=request.user if request.user.is_authenticated else None,
            page_url=data['page_url'],
            click_x=data['click_x'],
            click_y=data['click_y']
        )
    return JsonResponse({"message": "Click tracked"})
