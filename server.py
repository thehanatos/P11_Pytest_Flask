import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime


def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()


@app.route('/')
def index():
    return render_template(
        'index.html', clubs=clubs, competitions=competitions)


@app.route('/showSummary', methods=['POST'])
def showSummary():
    clubs_found = [
        club for club in clubs if club['email'] == request.form['email']]
    if clubs_found:
        club = clubs_found[0]
        return render_template('welcome.html',
                               club=club, competitions=competitions,
                               clubs=clubs)
    else:
        error_message = "Sorry, that email wasn't found."
        return render_template('index.html', error=error_message)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next(
        (c for c in competitions if c['name'] == competition), None)

    if not foundClub or not foundCompetition:
        flash("Something went wrong - please try again.")
        return redirect(url_for('index'))

    # Check if the competition is in the past
    competition_date = datetime.strptime(
        foundCompetition['date'], "%Y-%m-%d %H:%M:%S")
    if competition_date < datetime.now():
        flash("You cannot book past competitions.")
        return render_template(
            'welcome.html', club=foundClub, competitions=competitions)

    return render_template('booking.html',
                           club=foundClub, competition=foundCompetition)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = next(
        (c for c in competitions if c['name'] == request.form['competition']), None)
    club = next((c for c in clubs if c['name'] == request.form['club']), None)
    placesRequired = int(request.form['places'])

    if not competition or not club:
        flash('Invalid competition or club.')
        return redirect(url_for('index'))

    # Vérifie si la compétition est passée
    competition_date = datetime.strptime(
        competition['date'], "%Y-%m-%d %H:%M:%S")
    if competition_date < datetime.now():
        flash("You cannot purchase places for past competitions.")
        return render_template(
            'welcome.html', club=club, competitions=competitions)

    if placesRequired > 12:
        flash('You cannot purchase more than 12 places at once.')
        return render_template(
            'welcome.html', club=club, competitions=competitions)

    if placesRequired > int(competition['numberOfPlaces']):
        flash('Not enough places remaining in this competition.')
        return render_template(
            'welcome.html', club=club, competitions=competitions)

    if placesRequired > int(club['points']):
        flash('You do not have enough points to book these places.')
        return render_template(
            'welcome.html', club=club, competitions=competitions)

    # Tout est OK, on met à jour
    competition['numberOfPlaces'] = int(
        competition['numberOfPlaces']) - placesRequired
    club['points'] = int(club['points']) - placesRequired

    flash('Great - booking complete!')
    return render_template(
        'welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
