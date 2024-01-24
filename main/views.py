import datetime
import json

import requests
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from main.models import *
from main.testing import create_report

fio = ""
dolzhnost = ""
podrazdelenie = ""
start_date = ''
end_date = ''
lessons = []
result = []


def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        global fio, dolzhnost, podrazdelenie, result, start_date, end_date, lessons, result
        fio = ""
        dolzhnost = ""
        podrazdelenie = ""
        start_date = ''
        end_date = ''
        lessons = []
        result = []
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        copy_start_date = start_date
        copy_end_date = end_date
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
                # datetime.datetime.strptime(item['startAt'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d.%m'),
                datetime.datetime.strptime(item['startAt'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d'),
                item['lessonName'],
                groups
            )
            duration = item['duration']

            if key in data:
                data[key][0] += duration
            else:
                data[key] = [duration, []]

        for key, value in data.items():
            date, lesson, group = key
            duration, info = value
            if len(info) == 0:
                info = ''
            lessons.append(lesson)
            if duration is not None:
                result.append([date, lesson, group, duration, info])

        lessons = list(set(lessons))

        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S.%fZ').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S.%fZ').date()

        context = {
            'start_date': copy_start_date,
            'end_date': copy_end_date,
            'result': result,
        }
        return render(request, 'draft.html', context)

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


@csrf_exempt
def diploma_lessons(request):
    if request.method == 'POST':
        new_data = json.loads(request.body)

        # Достаем нужные значения
        new_dates = new_data.get('date')
        new_lessons = new_data.get('lesson')
        new_groups = new_data.get('group')
        new_duration = new_data.get('duration')

        global fio, dolzhnost, podrazdelenie, result, start_date, end_date, lessons, result

        if len(new_lessons) != 0:
            for i in range(len(new_lessons)):
                # преобразвание даты в формат 01.01
                # new_dates[i] = datetime.datetime.strptime(new_dates[i], '%Y-%m-%d').strftime('%d.%m')
                new_dates[i] = datetime.datetime.strptime(new_dates[i], '%Y-%m-%d').strftime('%Y-%m-%d')
                result.append([new_dates[i], new_lessons[i], new_groups[i], new_duration[i], ''])

        result.sort(key=lambda x: datetime.datetime.strptime(x[0], '%Y-%m-%d'))

        for i in range(len(result)):
            result[i][0] = datetime.datetime.strptime(result[i][0], '%Y-%m-%d').strftime('%d.%m.%Y')

        # создание отчета
        docx = create_report(fio, dolzhnost, podrazdelenie, result, start_date, end_date, lessons)

        response = HttpResponse(docx,
                                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = 'attachment; filename="report.docx"'
        return response
    else:
        return redirect('index')
