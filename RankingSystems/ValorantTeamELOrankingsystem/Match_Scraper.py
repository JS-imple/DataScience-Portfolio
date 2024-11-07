import requests
import json
from bs4 import BeautifulSoup, Comment

def getUpcomingAndLive(page):
    upcomingAndLiveMatches = {}
    url = "https://www.vlr.gg/matches/schedule/?page=" + str(page)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    dateSections = soup.findAll('div', class_ = 'wf-card', style = True)
    dates = soup.findAll('div', class_ = 'wf-label mod-large')
    i = 0
    for day in dateSections:
        k = 0
        matches = day.findAll('a', href = True)
        dateMatches = {}
        for match in matches:
            link = match['href']
            time = match.find('div', class_ = 'match-item-time').getText().strip()
            teams = match.findAll('div', class_ = 'match-item-vs-team-name')
            team1 = teams[0].getText().strip()
            team2 = teams[1].getText().strip()
            matchInEvent = match.find('div', class_ = 'match-item-event-series').getText().strip()
            event = match.find('div', class_ = 'match-item-event text-of').getText().replace(matchInEvent, '').strip()
            status = match.find('div', class_ = 'ml-status').getText().strip()
            if(status == "LIVE"):
                scores = match.findAll('div', class_ = 'match-item-vs-team-score')
                dateMatches[k] = {
                    "link": link,
                    "team1": team1,
                    "team2": team2,
                    "time": time,
                    "status": status,
                    "team1Score": scores[0].getText().strip(),
                    "team2Score": scores[1].getText().strip(),
                    "event": event,
                    "matchInEvent": matchInEvent
                }
            else:
                upcoming = match.find('div', class_ = 'ml-eta').getText().strip()
                dateMatches[k] = {
                    "link": link,
                    "team1": team1,
                    "team2": team2,
                    "time": time,
                    "status": status,
                    "event": event,
                    "matchInEvent": matchInEvent,
                    "upcoming": upcoming
                }
            k += 1
        if("Today" in dates[i].getText().strip()):
            upcomingAndLiveMatches["Today"] = dateMatches
        else:
            upcomingAndLiveMatches[dates[i].getText().strip()] = dateMatches
        i += 1
    
    return upcomingAndLiveMatches
            
def getResults(page):
    results = {}
    url = "https://www.vlr.gg/matches/results/?page=" + str(page)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    dateSections = soup.findAll('div', class_ = 'wf-card', style = True)
    dates = soup.findAll('div', class_ = 'wf-label mod-large')
    i = 0
    for day in dateSections:
        k = 0
        matches = day.findAll('a', href = True)
        dateMatches = {}
        for match in matches:
            link = match['href']
            time = match.find('div', class_ = 'match-item-time').getText().strip()
            teams = match.findAll('div', class_ = 'match-item-vs-team-name')
            team1 = teams[0].getText().strip()
            team2 = teams[1].getText().strip()
            matchInEvent = match.find('div', class_ = 'match-item-event-series').getText().strip()
            event = match.find('div', class_ = 'match-item-event text-of').getText().replace(matchInEvent, '').strip()
            completed = match.find('div', class_ = 'ml-eta mod-completed').getText().strip()
            scores = match.findAll('div', class_ = 'match-item-vs-team-score')
            dateMatches[k] = {
                "link": link,
                "team1": team1,
                "team2": team2,
                "time": time,
                "completed": completed,
                "team1Score": scores[0].getText().strip(),
                "team2Score": scores[1].getText().strip(),
                "event": event,
                "matchInEvent": matchInEvent
            }
            k += 1
        if("Today" in dates[i].getText().strip()):
            results["Today"] = dateMatches
        elif("Yesterday" in dates[i].getText().strip()):
            results[dates[i].getText().replace('\n', '').replace('\t', '').replace('Yesterday', '').strip()] = dateMatches
        else:
            results[dates[i].getText().strip()] = dateMatches
        i += 1
    
    return results