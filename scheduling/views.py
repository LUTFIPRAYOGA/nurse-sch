from django.shortcuts import render, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from scheduling.forms import PerawatForm
from scheduling.models import Perawat, Ruangan
from scheduling.pso import main_pso as PSO
from jchart import Chart

# Create your views here.

def create(request):
    if request.method == "POST":
        form = PerawatForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('/suntingperawat')
            except:
                pass
    else:
        form = PerawatForm()
    return render(request, 'index.html', {'form': form})


def edit(request, id):
    employee = Perawat.objects.get(id_perawat=id)
    form = PerawatForm(instance=employee)
    return render(request, 'edit.html', {'form': form, 'id': id})


def update(request, id):
    employee = Perawat.objects.get(id_perawat=id)
    form = PerawatForm(request.POST, instance=employee)
    if form.is_valid():
        form.save()
        return redirect("/pilihruang2")
    return render(request, 'edit.html', {'employee': employee})


def destroy(request, id):
    employee = Perawat.objects.get(id_perawat=id)
    employee.delete()
    return redirect("/suntingperawat")


# -----------------------
def demo(request):
    return render(request, 'demohah/edit.html')


def beranda(request):
    return render(request, 'beranda.html')

def pilihruang(request):
    ruangan = Ruangan.objects.all()
    return render(request, 'pilihruang.html', {'ruangan': ruangan})

def pilihruang1(request):
    ruangan = Ruangan.objects.all()
    return render(request, 'pilihruang1.html', {'ruangan': ruangan})

def pilihruang2(request):
    ruangan = Ruangan.objects.all()
    return render(request, 'pilihruang2.html', {'ruangan': ruangan})


def perawat(request):
    return render(request, 'perawat.html')

def kontak(request):
    return render(request, 'kontak.html')

def suntingperawat(request, ruang):
    ruangan = Ruangan.objects.get(id_ruangan=ruang)
    employees = Perawat.objects.filter(ruangan=ruang)
    return render(request, "suntingperawat.html", {'employees': employees, 'ruang': ruangan})

def dataperawat(request, ruang):
    ruangan = Ruangan.objects.get(id_ruangan=ruang)
    employees = Perawat.objects.filter(ruangan=ruang)
    return render(request, "dataperawat.html", {'employees': employees, 'ruang': ruangan})


# ------------------------
def start_pso(request, ruang, days):
    num_of_employees = Perawat.objects.filter(status="Perawat").count()
    PSO.main(maxIter=100, nurses=num_of_employees, ruang=ruang, days=int(days))
    return redirect('/result/'+ruang)


def continue_pso(request, ruang, days):
    num_of_employees = Perawat.objects.filter(status="Perawat").count()
    PSO.main(maxIter=1000, nurses=num_of_employees, ruang=ruang, days=int(days), state="Continue")
    return redirect('/result/'+ruang)


def result(request, ruang):
    _, gbest, gbest_fitness, last_iter, _ = PSO.get_result(ruang)
    employee = Perawat.objects.filter(status="Perawat", ruangan=ruang).values_list('nama_perawat', flat=True)
    ruangan = Ruangan.objects.get(id_ruangan=ruang)
    schedule = []
    totalDay = 0
    if gbest:
        totalDay = len(gbest[0])
        for i, name in enumerate(employee):
            schedule.append({'nama_perawat': name, 'shift': gbest[i]})
    return render(request, 'result.html',
                  {'schedules': schedule, 'fitness': gbest_fitness, 'last_iter': last_iter,
                   'days': range(totalDay), 'ruang': ruangan, 'numDay': totalDay})


def view_statistic(request, ruang):
    _, all_gbest_constraint = PSO.get_stats(ruang)
    page = request.GET.get('page', 1)
    paginator = Paginator(all_gbest_constraint, 10)
    try:
        gbest_constraint = paginator.page(page)
    except PageNotAnInteger:
        gbest_constraint = paginator.page(1)
    except EmptyPage:
        gbest_constraint = paginator.page(paginator.num_pages)
    return render(request, 'statistic.html', {'constraint': gbest_constraint})


def view_graphic(request, ruang):
    all_gbest_fitness, _ = PSO.get_stats(ruang)
    label = []
    data = []
    for x in sorted(set(all_gbest_fitness)):
        data.append(x)
        label.append(all_gbest_fitness.index(x))

    class LineChart(Chart):
        chart_type = 'line'
        scales = {
            'xAxes': [{
                'scaleLabel': {
                    'display': True,
                    'labelString': 'Iteration'
                }
            }],
            'yAxes': [{
                'scaleLabel': {
                    'display': True,
                    'labelString': 'Fitness'
                }
            }]
        }
        options = {
            'responsive': True,
            'maintainAspectRatio': True,
        }

        def get_labels(self, **kwargs):
            return label

        def get_datasets(self, **kwargs):
            return [{
                'label': "GBest Fitness",
                'data': data,
                'borderColor': 'rgb(75, 192, 192)',
                'lineTension': 0
            }]

    return render(request, 'grafik.html',
                  {'stats': LineChart()})


def generate_pdf(request, ruang):
    _, gbest, _, _, _ = PSO.get_result(ruang)
    employee = Perawat.objects.filter(status="Perawat", ruangan=ruang).values_list('nama_perawat', flat=True)
    schedule = []
    totalDay = len(gbest[0])
    for i, name in enumerate(employee):
        schedule.append({'nama_perawat': name, 'shift': gbest[i]})
    template = 'template_pdf.html'
    params = {
        'schedules': enumerate(schedule),
        'days': range(totalDay)
    }
    return render(request, template, params)