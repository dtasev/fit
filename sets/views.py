from django import views
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import UpdateView
from workout.models import WorkoutExercise, ExerciseSet


class EditSet(UpdateView):
    model = ExerciseSet
    template_name = 'sets/edit.html'
    fields = ('kgs', 'reps')

    def get_success_url(self):
        return reverse('today:sets:add_set', kwargs={"pk": self.object.workout_exercise.pk})


def repeat_set(request, pk):
    e = WorkoutExercise.objects.get(id=pk)
    if request.method == "POST":
        last = e.sets.last()
        if last:
            last.pk = None
            last.save()
    return redirect(reverse('today:sets:add_set', kwargs={"pk": e.id}))


def del_set(request, pk):
    e = WorkoutExercise.objects.get(id=pk)
    if request.method == "POST":
        e.sets.last().delete()
    return redirect(reverse('today:sets:add_set', kwargs={"pk": e.id}))


def add_set(request, pk):
    e = WorkoutExercise.objects.get(id=pk)
    if request.method == "GET":
        return render(request, 'today/sets.html', {"exercise": e})
    elif request.method == "POST":

        # return error for missing KGs
        if request.POST["kgs"] == "":
            return render(request, 'today/sets.html',
                          {"exercise": e, "kgs_error": "KGs not specified", "prev_reps_value": request.POST["reps"]})
        # return error for missing reps
        elif request.POST["reps"] == "":
            return render(request, 'today/sets.html',
                          {"exercise": e, "reps_error": "Reps not specified", "prev_kgs_value": request.POST["kgs"]})

        e.sets.create(kgs=request.POST["kgs"], reps=request.POST["reps"])
        return render(request, 'today/sets.html', {"exercise": e})