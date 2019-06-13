import json 

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, session
)
from werkzeug.exceptions import abort

from .auth import login_required

from .utilities.source_utilities import *
from .utilities.sourceEvents import start
from .utilities.constants import eventTypeMap


bp = Blueprint('event', __name__, url_prefix='/event')


@bp.route('/source/<sourceId>')
def source(sourceId):
    # page = request.args.get('page', 0, type=int)
    allsources = current_app.config['INT2SRC']
    title = allsources[sourceId][0]
    calendars = allsources[sourceId][1]
    return render_template('events/source-events.html', allsources=allsources, sourceId=sourceId, title=title, calendars=calendars, total=0)

@bp.route('/calendar/<calendarId>')
def calendar(calendarId):

    if 'select_status' in session:
        select_status = session['select_status']
    else:
        select_status = []
        session['select_status'] = select_status
    # find source of current calendar
    sourceId = '0'
    sourcetitle = "error: None"
    title = ""
    for key, source in current_app.config['INT2SRC'].items():
        for item in source[1]:
            if calendarId in item:
                title = item[calendarId]
                sourceId = key
                sourcetitle = source[0]
    
    events = get_calendar_events(sourceId, calendarId, select_status)
    print("sourceId: {}, calendarId: {}, number of events: {}".format(sourceId, calendarId, len(list(events))))
    return render_template('events/calendar.html', title=title, source=(sourceId, sourcetitle), posts=events, total=0, calendarId=calendarId,
                            select_status=select_status)


@bp.route('/setting')
@login_required
def setting():
    return render_template('events/setting.html', sources=current_app.config['INT2SRC'])


@bp.route('/download')
@login_required
def download():
    print("downloaded")
    start()
    return redirect(url_for('event.setting'))

@bp.route('/<calendarId>/select', methods=['POST'])
@login_required
def select(calendarId):
    select_status = []
    if request.form.get('approved') == '1':
        select_status.append('approved')
    if request.form.get('disapproved') == '1':
        select_status.append('disapproved')
    if request.form.get('published') == '1':
        select_status.append('published')

    session["select_status"] = select_status
    return "", 200

@bp.route('/approve/<calendarId>')
@login_required
def approveCalendar(calendarId):
    approve_calendar_db(calendarId)
    return "success", 200

@bp.route("/source/<id>/approve")
@login_required
def approveEvent(id):
    approve_event(id)
    return redirect(url_for("event.detail", eventId=id))

@bp.route('/detail/<eventId>')
def detail(eventId):
    event = get_event(eventId)
    # print("event: {}".format(event))
    source = current_app.config['INT2SRC'][event['sourceId']]
    sourceName = source[0]
    calendarName = ''
    for dict in source[1]:
        if event['calendarId'] in dict:
            calendarName = dict[event['calendarId']]
    return render_template("events/event.html", post=event, isUser=False, sourceName=sourceName, calendarName=calendarName)


@bp.route('/edit/<eventId>', methods=('GET', 'POST'))
def edit(eventId):
    post_by_id = get_event(eventId)
    if request.method == 'POST':
        # change the specific event
        post_by_id['titleURL'] = request.form['titleURL']
        post_by_id['startDate'] = request.form['startDate']
        post_by_id['endDate'] = request.form['endDate']
        post_by_id['cost'] = request.form['cost']
        post_by_id['sponsor'] = request.form['sponsor']
        # more parts editable TODO ....

        # insert update_user_event function here later
        update_event(eventId, post_by_id)
    return render_template("events/event-edit.html", post = post_by_id, eventTypeMap = eventTypeMap, isUser=False)
