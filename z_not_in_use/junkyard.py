




def get_performances_by_day(user_id):
    """Returns the count of 4 or 5 star workouts by day to which days tend to
    yield better performances

    """

    workouts = Workout.query.filter(Workout.user_id == user_id).all()
                                        # ((Workout.performance_rating == 4) |
                                        #  (Workout.performance_rating == 5))).all()

    workouts_by_day = {1: 0,
                       2: 0,
                       3: 0,
                       4: 0,
                       5: 0,
                       6: 0,
                       7: 0,
                       }

    top_performances = {1: 0,
                        2: 0,
                        3: 0,
                        4: 0,
                        5: 0,
                        6: 0,
                        7: 0,
                        }

    top_performance_ratio = {1: 0,
                             2: 0,
                             3: 0,
                             4: 0,
                             5: 0,
                             6: 0,
                             7: 0,
                             }

    for workout in workouts:
        day_of_week = workout.workout_time.isoweekday()

        workouts_by_day[day_of_week] += 1

        if workout.performance_rating >= 4:
            top_performances[day_of_week] += 1

    for day in top_performance_ratio:
        if workouts_by_day[day] > 0:
            top_performance_ratio[day] = float(top_performances[day])/workouts_by_day[day]

    print "workouts_by_day:", workouts_by_day
    print "top_performances:", top_performances
    print "top_performance_ratio:", top_performance_ratio

    return {"workouts_by_day": workouts_by_day,
            "top_performances": top_performances,
            "top_performance_ratio": top_performance_ratio,
            }





# Returns a dictionary of dictionaies:
# {
#  "workouts_by_day" = {1: 0, ..., 7: 0},
#  "top_performances" = {1: 0, ..., 7: 0},
#  "top_performance_ratio" = {1: 0, ..., 7: 0}
#  }
performance_by_day = get_performances_by_day(user_id)