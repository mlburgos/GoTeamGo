




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





# Returns a dictionary of dictionaries:
# {
#  "workouts_by_day" = {1: 0, ..., 7: 0},
#  "top_performances" = {1: 0, ..., 7: 0},
#  "top_performance_ratio" = {1: 0, ..., 7: 0}
#  }
performance_by_day = get_performances_by_day(user_id)




################################################################################
# These are incorrect. Since the order in dicts are not guaranteed, the results are inaccurate. 

def generate_seven_day_dict(start_date):
    """"""

    seven_day_dict = {}

    for i in xrange(7):
        days_to_add = datetime.timedelta(days=i)
        seven_day_dict[start_date + days_to_add] = 0

    return seven_day_dict


def by_day_bar_graph(eight_mondays, nearest_monday, user_workouts):
    """"""

    X_LABELS = ['Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday',
                'Saturday',
                'Sunday',
                ]

    data = []

    color_counter = 0

    for monday in eight_mondays:
        current_week_all = generate_seven_day_dict(monday)
        current_week_top = generate_seven_day_dict(monday)

        for workout in user_workouts:
            workout_date = workout.workout_time.date()
            workout_rating = workout.performance_rating

            if workout_date in current_week_all:
                current_week_all[workout_date] += 1
                if workout_rating >= 4:
                    current_week_top[workout_date] += 1

        if monday == nearest_monday:
            name = "Current Week"
        else:
            name = str(monday.month) + "/" + str(monday.day) + "/" + str(monday.year)

        if color_counter < 2:
            color = COLOR_SCHEME[0]
        elif color_counter >= 2 and color_counter < 4:
            color = COLOR_SCHEME[1]
        elif color_counter >= 4 and color_counter < 6:
            color = COLOR_SCHEME[2]
        else:
            color = COLOR_SCHEME[3]

        trace = go.Bar(x=X_LABELS,
                       y=current_week_top.values(),
                       name=name,
                       hoverinfo="none",
                       marker=dict(color=color,
                                   ),
                       )

        data.append(trace)

        color_counter += 1

    return data

################################################################################
