from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

SPECIAL_EXERCISES_JOIN_CHARACTER = "|"


# Create your models here.
class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField("Date")
    primary_muscle_group = models.CharField(max_length=50)
    secondary_muscle_group = models.CharField(max_length=50)
    completed = models.BooleanField("Completed", default=False)

    start_time = models.DateTimeField("Start time of Workout", null=True, default=None)
    end_time = models.DateTimeField("End time of Workout", null=True, default=None)

    def primary(self):
        return self.workoutexercise_set.filter(exercise__muscle_group=self.primary_muscle_group)

    def secondary(self):
        return self.workoutexercise_set.filter(exercise__muscle_group=self.secondary_muscle_group)

    def duration(self):
        if not self.start_time:
            return ""
        if not self.end_time:
            # timezone.now() has the TZ of the server, not the client
            # and this doesnt show the correct duration
            return timezone.now() - self.start_time
        return "Duration: " + str(self.end_time - self.start_time)[:7]

    class Meta:
        ordering = ["-date"]


class Exercise(models.Model):
    muscle_group = models.CharField(max_length=200)
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name


class WorkoutExercise(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    # format: "30x12|30x10"
    old_sets = models.TextField(default="")

    def __str__(self):
        return str(self.exercise)

    def sets_string(self):
        sets_string = ""
        for set in self.sets.all():
            sets_string += " {} KG x {} reps\n".format(set.kgs, set.reps)

        # removes the trailing coma
        return sets_string[:-1]

    def sets_js_array(self):
        sets_string = "["
        for set in self.sets.all():
            sets_string += '{{ "kgs": {}, "reps": {} }},'.format(set.kgs, set.reps)

        # removes the trailing coma
        return sets_string + "]"

    def sets_table(self):
        sets_table = """
        <table class="table table-sm">
        <thead>
        <tr>
        <th>Set</th>
        <th>KGs</th>
        <th>Reps</th>
        </tr>
        </thead>
        <tbody>"""

        sets_rows = ""
        for i, set_data in enumerate(self.sets.all(), start=1):
            sets_rows += '<tr><td>{}</td><td>{}</td><td>{}</td></tr>'.format(i, set_data.kgs, set_data.reps)

        return sets_table + sets_rows + "</tbody></table>"


class ExerciseSet(models.Model):
    workout_exercise = models.ForeignKey(WorkoutExercise, on_delete=models.CASCADE, related_name="sets")
    reps = models.IntegerField()
    kgs = models.FloatField()


def split_old_sets(apps, schema_editor):
    WorkoutExercise = apps.get_model('workout', 'WorkoutExercise')
    ExerciseSet = apps.get_model('workout', 'ExerciseSet')

    for w in WorkoutExercise.objects.all():
        if w.old_sets != "":
            for set in w.old_sets.split(SPECIAL_EXERCISES_JOIN_CHARACTER):
                # this gives back a list [<kgs>, <reps>]
                kgs_and_reps = set.split("x")
                ExerciseSet.objects.create(workout_exercise=w, kgs=float(kgs_and_reps[0]), reps=int(kgs_and_reps[1]))
