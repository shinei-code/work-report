from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
import requests

class HolidaysView(View):

    def get(self, request, *args, **kwargs):
        res = requests.get('https://holidays-jp.github.io/api/v1/date.json')
        if res.status_code == 200:
            holidays = res.json()
            return JsonResponse(holidays)
        else:
            return JsonResponse({'error': '祝日取得失敗'}, status=500)
