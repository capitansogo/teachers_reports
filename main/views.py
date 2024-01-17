import datetime

import requests
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render, redirect

from main.models import *
from main.testing import create_report


def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        # приведение дат к формату 2021-05-01T00:00:00.000Z
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        teacher_id = User.objects.get(id=request.user.id).id_teacher
        fio = User.objects.get(id=request.user.id).last_name + ' ' + User.objects.get(
            id=request.user.id).first_name + ' ' + User.objects.get(id=request.user.id).patronymic
        dolzhnost = User.objects.get(id=request.user.id).post.name
        podrazdelenie = User.objects.get(id=request.user.id).division.name
        url = 'https://parser.ystuty.ru/api/ystu/schedule/teacher/'
        response = requests.get(f'{url}{teacher_id}').json()
        filtered_items = [
            item for item in response['items'] if
            start_date <= item['startAt'] <= end_date and start_date <= item['endAt'] <= end_date
        ]
        data = {}
        for item in filtered_items:
            groups = ''
            for loop in item['groups']:
                groups += str(loop) + ', '
            groups = groups[:-2]
            key = (
                datetime.datetime.strptime(item['startAt'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d.%m'),
                item['lessonName'],
                groups
            )
            duration = item['duration']

            if key in data:
                data[key][0] += duration
            else:
                data[key] = [duration, []]

        result = []
        lessons = []
        for key, value in data.items():
            date, lesson, group = key
            duration, info = value
            if len(info) == 0:
                info = ''
            lessons.append(lesson)
            if duration is not None:
                result.append([date, lesson, group, duration, info])

        # поиск уникальных значений в списке lessons
        lessons = list(set(lessons))
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S.%fZ').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S.%fZ').date()
        docx = create_report(fio, dolzhnost, podrazdelenie, result, start_date, end_date, lessons)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = 'attachment; filename=report.docx'
        docx.save(response)
        return response
    else:
        return render(request, 'index.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'index')
            return redirect(next_url)

    return render(request, 'login.html')
