from model import (User,
                   GroupUser,
                   GroupPendingUser,
                   Group,
                   GroupAdmin,
                   Goal,
                   Workout,
                   Like,
                   Personal_Goal,
                   db,
                   connect_to_db)

import datetime

import plotly.graph_objs as go

from flask import (Flask,
                   jsonify,
                   render_template,
                   redirect,
                   request,
                   flash,
                   session)

import json

X_LABELS = ['Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday',
            'Sunday',
            ]

X_LABELS_2 = ['Mon',
              'Tues',
              'Wed',
              'Thurs',
              'Fri',
              'Sat',
              'Sun',
              ]

COLOR_SCHEME = ['#B3E9FE', '#73D8FF', '#3AC9FF', '#07BAFF']



by_day_grouped_layout = go.Layout(
    title='Workouts by Day <br> <i>4 and 5 star performances by day</i>',
    barmode='grouped',
    legend=dict(orientation="h",
                font=dict(
                    # family='sans-serif',
                    # size=12,
                    # color='#000',
                    )
                ),
    yaxis=dict(
        title='# of Workouts',
        showgrid=False,
        ticks='outside',
    ),
    yaxis2=dict(
        title="% of Top Workouts",
        showgrid=False,
        ticks='outside',
        range=[0, 110],
        titlefont=dict(
            color='rgb(148, 103, 189)'
        ),
        tickfont=dict(
            color='rgb(148, 103, 189)'
        ),
        overlaying='y',
        side='right'),
    width=1100,
    height=600,
    )

by_hour_grouped_layout = go.Layout(
    title='Workouts by Hour <br> <i>4 and 5 star performances by day</i>',
    barmode='grouped',
    legend=dict(orientation="h",
                font=dict(
                    # family='sans-serif',
                    # size=12,
                    # color='#000',
                    )
                ),
    yaxis=dict(
        title='# of Workouts',
        showgrid=False,
        ticks='outside',
    ),
    yaxis2=dict(
        title="% of Top Workouts",
        showgrid=False,
        ticks='outside',
        range=[0, 110],
        titlefont=dict(
            color='rgb(148, 103, 189)'
        ),
        tickfont=dict(
            color='rgb(148, 103, 189)'
        ),
        overlaying='y',
        side='right'),
    width=1100,
    height=600,
    )


def generate_bar_graph(user_id):
    """"""

    today = datetime.date.today()

    # using regular .weekday() instead of .isoweekday() to get the number of
    # days since monday since monday = 0
    days_from_monday = datetime.timedelta(days=today.weekday())

    nearest_monday = today - days_from_monday

    days_49 = datetime.timedelta(days=49)

    eight_mondays_ago = nearest_monday - days_49

    user_workouts = Workout.query.filter(Workout.user_id == user_id,
                                         Workout.workout_time >= eight_mondays_ago,
                                         # Workout.performance_rating >= 4,
                                         )\
                                 .all()

    eight_mondays = [(eight_mondays_ago + datetime.timedelta(days=7*i))
                     for i in xrange(8)]

    by_day_bar_graph_grouped_data = by_day_bar_graph_grouped(eight_mondays=eight_mondays,
                                                             nearest_monday=nearest_monday,
                                                             user_workouts=user_workouts,
                                                             )

    by_hour_bar_graph_grouped_data = by_hour_bar_graph_grouped(eight_mondays=eight_mondays,
                                                               nearest_monday=nearest_monday,
                                                               user_workouts=user_workouts,
                                                               )

    eight_week_data_by_day = by_day_bar_graph_grouped_data['eight_week_data']
    four_week_data_by_day = by_day_bar_graph_grouped_data['four_week_data']

    eight_week_by_day_fig = go.Figure(data=eight_week_data_by_day, layout=by_day_grouped_layout)
    four_week_by_day_fig = go.Figure(data=four_week_data_by_day, layout=by_day_grouped_layout)

    eight_week_data_by_hour = by_hour_bar_graph_grouped_data['eight_week_data']
    four_week_data_by_hour = by_hour_bar_graph_grouped_data['four_week_data']

    eight_week_by_hour_fig = go.Figure(data=eight_week_data_by_hour, layout=by_hour_grouped_layout)
    four_week_by_hour_fig = go.Figure(data=four_week_data_by_hour, layout=by_hour_grouped_layout)

    return (eight_week_by_day_fig,
            four_week_by_day_fig,
            eight_week_by_hour_fig,
            four_week_by_hour_fig,
            )


def generate_seven_days(start_date):
    """
    >>> generate_seven_days(datetime.date(2017, 2, 27))
    [[datetime.date(2017, 2, 27), 0], [datetime.date(2017, 2, 28), 0], [datetime.date(2017, 3, 1), 0], [datetime.date(2017, 3, 2), 0], [datetime.date(2017, 3, 3), 0], [datetime.date(2017, 3, 4), 0], [datetime.date(2017, 3, 5), 0]]

    """

    seven_days = []

    for i in xrange(7):
        days_to_add = datetime.timedelta(days=i)
        seven_days.append([start_date + days_to_add, 0])

    return seven_days


def by_day_bar_graph(eight_mondays, nearest_monday, user_workouts):
    """"""

    data = []

    color_counter = 0

    for monday in eight_mondays:
        current_week_all = generate_seven_days(monday)
        current_week_top = generate_seven_days(monday)
        current_week_dates = list(zip(*current_week_all)[0])

        for workout in user_workouts:
            workout_date = workout.workout_time.date()
            workout_rating = workout.performance_rating

            if workout_date in current_week_dates:
                index_in_current_week = current_week_dates.index(workout_date)
                current_week_all[index_in_current_week][1] += 1
                if workout_rating >= 4:
                    current_week_top[index_in_current_week][1] += 1

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
                       y=zip(*current_week_top)[1],
                       name=name,
                       hoverinfo="none",
                       marker=dict(color=color,
                                   ),
                       )

        data.append(trace)

        color_counter += 1

    return data


def generate_days_list():
    """
    >>> generate_days_list()
    [[1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0]]
    """

    seven_days = []

    for i in xrange(1, 8):
        seven_days.append([i, 0])

    return seven_days


def by_day_bar_graph_grouped(eight_mondays, nearest_monday, user_workouts):
    """"""

    X_LABELS = ['Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday',
                'Saturday',
                'Sunday',
                ]

    eight_mondays_ago = eight_mondays[0]
    four_mondays_ago = eight_mondays[4]

    eight_weeks_of_workouts_all = generate_days_list()
    eight_weeks_of_workouts_top = generate_days_list()
    four_weeks_of_workouts_all = generate_days_list()
    four_weeks_of_workouts_top = generate_days_list()

    for workout in user_workouts:
        day_of_week = workout.workout_time.isoweekday()
        workout_date = workout.workout_time.date()
        workout_rating = workout.performance_rating

        eight_weeks_of_workouts_all[day_of_week - 1][1] += 1

        if workout_rating >= 4:
            eight_weeks_of_workouts_top[day_of_week - 1][1] += 1

        if workout_date >= four_mondays_ago:
            four_weeks_of_workouts_all[day_of_week - 1][1] += 1
            if workout_rating >= 4:
                four_weeks_of_workouts_top[day_of_week - 1][1] += 1

    TOP_COLOR = '#3AC9FF'
    ALL_COLOR = '#B3E9FE'

    eight_week_trace1 = go.Bar(x=X_LABELS_2,
                               y=zip(*eight_weeks_of_workouts_top)[1],
                               name="Eight Weeks- Top Performances",
                               hoverinfo="none",
                               marker=dict(color=TOP_COLOR,
                                           ),
                               )

    eight_week_trace2 = go.Bar(x=X_LABELS_2,
                               y=zip(*eight_weeks_of_workouts_all)[1],
                               name="Eight Weeks- All Workouts",
                               hoverinfo="none",
                               marker=dict(color=ALL_COLOR,
                                           ),
                               )

    eight_weeks_combined = zip(zip(*eight_weeks_of_workouts_top)[1],
                               zip(*eight_weeks_of_workouts_all)[1],
                               )

    eight_week_percentages = [round(float(top)/total*100, 0)
                              if total > 0
                              else 0
                              for top, total
                              in eight_weeks_combined
                              ]

    eight_week_trace_line = go.Scatter(x=X_LABELS_2,
                                       y=eight_week_percentages,
                                       name="Percentage of Top Performances",
                                       connectgaps=True,
                                       line=dict(shape='spline',
                                                 ),
                                       yaxis='y2',
                                       )

    eight_week_data = [eight_week_trace1,
                       eight_week_trace2,
                       eight_week_trace_line,
                       ]

    four_week_trace1 = go.Bar(x=X_LABELS_2,
                              y=zip(*four_weeks_of_workouts_top)[1],
                              name="Four Weeks- Top Performances",
                              hoverinfo="none",
                              marker=dict(color=TOP_COLOR,
                                          ),
                              )

    four_week_trace2 = go.Bar(x=X_LABELS_2,
                              y=zip(*four_weeks_of_workouts_all)[1],
                              name="Four Weeks- All Workouts",
                              hoverinfo="none",
                              marker=dict(color=ALL_COLOR,
                                          ),
                              )

    four_weeks_combined = zip(zip(*four_weeks_of_workouts_top)[1], zip(*four_weeks_of_workouts_all)[1])

    four_week_percentages = [round(float(top)/total*100, 0)
                             if total > 0
                             else 0
                             for top, total in four_weeks_combined]

    four_week_trace = go.Scatter(x=X_LABELS_2,
                                 y=four_week_percentages,
                                 name="Percentage of Top Performances",
                                 connectgaps=True,
                                 line=dict(shape='spline',
                                           ),
                                 yaxis='y2',
                                 )

    four_week_data = [four_week_trace1,
                      four_week_trace2,
                      four_week_trace,
                      ]

    return {'eight_week_data': eight_week_data,
            'four_week_data': four_week_data,
            }


def generate_24hrs():
    """

    >>> graph_functions.generate_24hrs()
    [[1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0], [8, 0], [9, 0], [10, 0], [11, 0], [12, 0], [13, 0], [14, 0], [15, 0], [16, 0], [17, 0], [18, 0], [19, 0], [20, 0], [21, 0], [22, 0], [23, 0], [24, 0]]
    """

    hrs = []

    for i in xrange(1, 25):
        hrs.append([i, 0])

    return hrs


def generate_24hr_Xlabels():
    """
    >>> graph_functions.generate_24hr_Xlabels()
    ['12AM', '1AM', '2AM', '3AM', '4AM', '5AM', '6AM', '7AM', '8AM', '9AM', '10AM', '11AM', '12PM', '1PM', '2PM', '3PM', '4PM', '5PM', '6PM', '7PM', '8PM', '9PM', '10PM', '11PM']
    """

    X_LABELS = []

    for i in xrange(24):

        if i == 0:
            X_LABELS.append("12" + "AM")
        elif i < 12:
            X_LABELS.append(str(i) + "AM")
        elif i == 12:
            X_LABELS.append("12" + "PM")
        else:
            X_LABELS.append(str(i - 12) + "PM")

    return X_LABELS


def by_hour_bar_graph(eight_mondays, nearest_monday, user_workouts):
    """"""

    X_LABELS = generate_24hr_Xlabels()

    data = []

    color_counter = 0

    for monday in eight_mondays:
        current_week = generate_seven_days(monday)
        current_week_dates = list(zip(*current_week)[0])
        hrs = generate_24hrs()
        hrs_top = generate_24hrs()
        hrs_list = zip(*hrs)[0]

        for workout in user_workouts:
            workout_date = workout.workout_time.date()
            workout_hour = workout.workout_time.time().hour
            workout_rating = workout.performance_rating

            if workout_date in current_week_dates:
                index_in_hrs = hrs_list.index(workout_hour)
                hrs[index_in_hrs][1] += 1

                if workout_rating >= 4:
                    hrs_top[index_in_hrs][1] += 1

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
                       y=zip(*hrs_top)[1],
                       name=name,
                       hoverinfo="none",
                       marker=dict(color=color,
                                   ),
                       )

        data.append(trace)

        color_counter += 1

    return data


def by_hour_bar_graph_grouped(eight_mondays, nearest_monday, user_workouts):
    """"""

    X_LABELS = generate_24hr_Xlabels()

    eight_mondays_ago = eight_mondays[0]
    four_mondays_ago = eight_mondays[4]

    eight_weeks_of_workouts_all = generate_24hrs()
    eight_weeks_of_workouts_top = generate_24hrs()
    four_weeks_of_workouts_all = generate_24hrs()
    four_weeks_of_workouts_top = generate_24hrs()

    for workout in user_workouts:
        workout_hour = workout.workout_time.time().hour
        workout_date = workout.workout_time.date()
        workout_rating = workout.performance_rating

        eight_weeks_of_workouts_all[workout_hour - 1][1] += 1

        if workout_rating >= 4:
            eight_weeks_of_workouts_top[workout_hour - 1][1] += 1

        if workout_date >= four_mondays_ago:
            four_weeks_of_workouts_all[workout_hour - 1][1] += 1
            if workout_rating >= 4:
                four_weeks_of_workouts_top[workout_hour - 1][1] += 1

    TOP_COLOR = '#3AC9FF'
    ALL_COLOR = '#B3E9FE'

    eight_week_trace1 = go.Bar(x=X_LABELS,
                               y=zip(*eight_weeks_of_workouts_top)[1],
                               name="Eight Weeks- Top",
                               hoverinfo="none",
                               marker=dict(color=TOP_COLOR,
                                           ),
                               )

    eight_week_trace2 = go.Bar(x=X_LABELS,
                               y=zip(*eight_weeks_of_workouts_all)[1],
                               name="Eight Weeks- All",
                               hoverinfo="none",
                               marker=dict(color=ALL_COLOR,
                                           ),
                               )

    eight_weeks_combined = zip(zip(*eight_weeks_of_workouts_top)[1], zip(*eight_weeks_of_workouts_all)[1])

    eight_week_percentages = [round(float(top)/total*100, 0)
                              if total > 0
                              else 0
                              for top, total
                              in eight_weeks_combined
                              ]

    eight_week_trace_line = go.Scatter(x=X_LABELS,
                                       y=eight_week_percentages,
                                       name="Percentage of Top Performances",
                                       connectgaps=True,
                                       line=dict(shape='spline',
                                                 ),
                                       yaxis='y2',
                                       # marker=dict(color='#000',
                                       #             ),
                                       )

    eight_week_data = [eight_week_trace1,
                       eight_week_trace2,
                       eight_week_trace_line,
                       ]

    four_week_trace1 = go.Bar(x=X_LABELS,
                              y=zip(*four_weeks_of_workouts_top)[1],
                              name="Four Weeks- Top",
                              hoverinfo="none",
                              marker=dict(color=TOP_COLOR,
                                          ),
                              )

    four_week_trace2 = go.Bar(x=X_LABELS,
                              y=zip(*four_weeks_of_workouts_all)[1],
                              name="Four Weeks- All",
                              hoverinfo="none",
                              marker=dict(color=ALL_COLOR,
                                          ),
                              )

    four_weeks_combined = zip(zip(*four_weeks_of_workouts_top)[1], zip(*four_weeks_of_workouts_all)[1])

    four_week_percentages = [round(float(top)/total*100, 0)
                             if total > 0
                             else 0
                             for top, total
                             in four_weeks_combined
                             ]

    four_week_trace_line = go.Scatter(x=X_LABELS,
                                      y=four_week_percentages,
                                      name="Percentage of Top Performances",
                                      connectgaps=True,
                                      line=dict(shape='spline',
                                                ),
                                      yaxis='y2',
                                      )

    four_week_data = [four_week_trace1,
                      four_week_trace2,
                      four_week_trace_line,
                      ]

    return {'eight_week_data': eight_week_data,
            'four_week_data': four_week_data,
            }


def by_day_line_graph(eight_mondays, nearest_monday, user_workouts):
    """"""

    X_LABELS = ['Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday',
                'Saturday',
                'Sunday',
                ]

    eight_mondays_ago = eight_mondays[0]
    four_mondays_ago = eight_mondays[4]

    eight_weeks_of_workouts_all = generate_days_list()
    eight_weeks_of_workouts_top = generate_days_list()
    four_weeks_of_workouts_all = generate_days_list()
    four_weeks_of_workouts_top = generate_days_list()

    for workout in user_workouts:
        day_of_week = workout.workout_time.isoweekday()
        workout_date = workout.workout_time.date()
        workout_rating = workout.performance_rating

        eight_weeks_of_workouts_all[day_of_week - 1][1] += 1

        if workout_rating >= 4:
            eight_weeks_of_workouts_top[day_of_week - 1][1] += 1

        if workout_date >= four_mondays_ago:
            four_weeks_of_workouts_all[day_of_week - 1][1] += 1
            if workout_rating >= 4:
                four_weeks_of_workouts_top[day_of_week - 1][1] += 1

    TOP_COLOR = '#3AC9FF'
    ALL_COLOR = '#B3E9FE'

    eight_weeks_combined = zip(zip(*eight_weeks_of_workouts_top)[1], zip(*eight_weeks_of_workouts_all)[1])

    eight_week_percentages = [round(float(top)/total*100, 0) for top, total in eight_weeks_combined]

    four_weeks_combined = zip(zip(*four_weeks_of_workouts_top)[1], zip(*four_weeks_of_workouts_all)[1])

    four_week_percentages = [round(float(top)/total*100, 0) for top, total in four_weeks_combined]

    eight_week_trace = go.Scatter(x=X_LABELS,
                                  y=eight_week_percentages,
                                  name="Eight Weeks",
                                  # hoverinfo="none",
                                  # marker=dict(color=TOP_COLOR,
                                  #             ),
                                  connectgaps=True,
                                  line=dict(shape='spline',
                                            )
                                  )

    four_week_trace = go.Scatter(x=X_LABELS,
                                 y=four_week_percentages,
                                 name="Four Weeks",
                                 # hoverinfo="none",
                                 # marker=dict(color=TOP_COLOR,
                                 #             ),
                                 connectgaps=True,
                                 )

    data = [eight_week_trace,
            four_week_trace,
            ]

    return data

