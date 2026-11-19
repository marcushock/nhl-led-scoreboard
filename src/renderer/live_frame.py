"""Identity of a live scoreboard frame.

Two overviews that produce the same key draw the same pixels, so the
render loop can leave the panel alone.
"""


def live_frame_key(scoreboard, show_sog):
    """Fields that change the live scoreboard pixels.

    Shots are included only while the shots page is showing. A stopped clock,
    unchanged score, and unchanged power play produce the same key.
    """
    away = scoreboard.away_team
    home = scoreboard.home_team
    return (
        away.goals,
        home.goals,
        scoreboard.periods.ordinal,
        scoreboard.periods.clock,
        bool(away.powerplay),
        bool(home.powerplay),
        away.pp_time_remaining,
        home.pp_time_remaining,
        away.num_skaters,
        home.num_skaters,
        away.shot_on_goal if show_sog else None,
        home.shot_on_goal if show_sog else None,
        bool(show_sog),
        bool(scoreboard.intermission),
    )
