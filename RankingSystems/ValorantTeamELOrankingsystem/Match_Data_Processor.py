import requests 
import json
import re
from bs4 import BeautifulSoup, Comment

def getMatchPage(matchID): #returns a dictionary of the stats of match given by id
    matchStats = {}
    url = "https://www.vlr.gg/" + str(matchID)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    mainHeader = soup.find('div', class_ = "match-header-vs")
    matchStatus = mainHeader.find('div', class_ = 'match-header-vs-note').getText().strip()

    images = mainHeader.findAll('img', src = True)
    teamAImageLink = images[0]['src']
    teamBImageLink = images[1]['src']
    if('vlr.png' in teamAImageLink):
        teamAImageLink = "https://www.vlr.gg/img/vlr/tmp/vlr.png"
    else:
        teamAImageLink = "https:" + teamAImageLink
    if('vlr.png' in teamBImageLink):
        teamBImageLink = "https://www.vlr.gg/img/vlr/tmp/vlr.png"
    else:
        teamBImageLink = "https:" + teamBImageLink

    teamAName = mainHeader.find('div', class_ = "match-header-link-name mod-1").findAll('div')[0].getText().strip()
    teamBName = mainHeader.find('div', class_ = "match-header-link-name mod-2").findAll('div')[0].getText().strip()
    
    if(('final' in matchStatus) or ('live' in matchStatus)):
        teamAScore = int(mainHeader.find('div', class_ = "js-spoiler").findAll('span')[0].getText().strip())
        teamBScore = int(mainHeader.find('div', class_ = "js-spoiler").findAll('span')[2].getText().strip())

        if(matchStatus != 'live'):
            winner = ""
            if(teamAScore > teamBScore):
                winner = teamAName
                loser = teamBName
            else:
                winner = teamBName
                loser = teamAName
        else:
            winner = 'LiveMatch'
            loser = 'LiveMatch'

    superHeader = soup.find('div', class_ = "match-header-super")
    date = superHeader.findAll('div', class_ = 'moment-tz-convert')[0].getText().strip()
    time = superHeader.findAll('div', class_ = 'moment-tz-convert')[1].getText().strip()
    mainEvent = superHeader.find('a').find('div').findAll('div')[0].getText().strip()
    eventSubtext = superHeader.find('a').find('div').findAll('div')[1].getText().strip()
    eventSubtext = eventSubtext.replace("\t", "")
    eventSubtext = eventSubtext.replace("\n", "")

    toDelete = soup.findAll('div', class_ = 'moment-tz-convert')
    toDelete[0].decompose()
    toDelete[1].decompose()
    patch = soup.find('div', class_ = 'match-header-date').getText().strip()

    mapSection = soup.find('div', class_ = "match-header-note")
    if(mapSection != None):
        mapText = mapSection.getText().strip()
        picksAndBans = mapText.split(";")
        for i in range(0, len(picksAndBans)):
            picksAndBans[i] = picksAndBans[i].strip()
    else:
        picksAndBans = ["None"]

    videos = {}
    #Completed Match
    if(('final' in matchStatus)):        
        if('Not yet available') not in soup.find('div', class_ = 'match-vods').getText().strip():
            vods = {}
            vodList = soup.find('div', class_ = 'match-vods').find('div', class_ = 'match-streams-container').findAll('a', href = True)
            for vod in vodList:
                mapNum = vod.getText().strip()
                vodLink = vod['href']
                vods[mapNum] = vodLink
                videos['Vods'] = vods
        else:
            vods = 'Not Available Yet'
            videos['Vods'] = vods
    #Live or Upcoming match
    else:
        if('No stream available') not in soup.find('div', class_ = 'match-streams').getText().strip():
            streams = {}
            streamList = soup.find('div', class_ = 'match-streams').find('div', class_ = 'match-streams-container').findChildren(recursive = False)
            for stream in streamList:
                streamName = stream.getText().strip()
                if('More Streams' not in streamName):
                    try:
                        streamLink = stream.find('a', href = True)['href']
                    except TypeError:
                        streamLink = stream['href']
                streams[streamName] = streamLink
                videos['Streams'] = streams
        else:
            streams = 'No Stream Available'
            videos['Streams'] = streams

    if((soup.find('div', class_ = 'match-h2h-matches') != None)):
        headToHeadMatches = soup.find('div', class_ = 'match-h2h-matches').findAll('a', href = True)
        i = 0
        headToHead = {}
        for match in headToHeadMatches:
            link = match['href']
            event = match.find('div', class_ = 'match-h2h-matches-event-name text-of').getText().strip()
            matchInEvent = match.find('div', class_ = 'match-h2h-matches-event-series text-of').getText().strip()
            encounterDate = match.find('div', class_ = 'match-h2h-matches-date').getText().strip()
            scoreSection = match.find('div', class_ = 'match-h2h-matches-score')
            scores = scoreSection.getText().strip().split("\n")
            team1Score = scores[0]
            team2Score = scores[1]
            headToHead[i] = {   
                "link" : link,
                "event" : event,
                "matchInEvent" : matchInEvent,
                "encounterDate" : encounterDate,
                "team1Score" : team1Score,
                "team2Score" : team2Score
            }
            i += 1
    else:
        headToHead = {
            "None" : "None"
        }    
    
    matchStats["Status"] = matchStatus
    matchStats["Event"] = mainEvent
    matchStats["eventDetail"] = eventSubtext
    matchStats["Teams"] = teamAName + " vs " + teamBName
    matchStats["TeamA"] = teamAName
    matchStats["TeamB"] = teamBName
    matchStats['TeamAImage'] = teamAImageLink
    matchStats['TeamBImage'] = teamBImageLink
    matchStats["PicksAndBans"] = picksAndBans
    matchStats["Date"] = date
    matchStats["Time"] = time
    matchStats["Patch"] = patch
    matchStats["Videos"] = videos
    matchStats["HeadToHead"] = headToHead

    if(('final' in matchStatus) or ('live' in matchStatus)):
        statsContainer = soup.find('div', class_ = "vm-stats-container").findAll('div', class_ = "vm-stats-game")
        mapDetails = getPlayerDataMatch(statsContainer, teamAName, teamBName)
        matchStats["scoreA"] = teamAScore
        matchStats["scoreB"] = teamBScore
        matchStats["Winner"] = winner
        matchStats["Loser"] = loser
        matchStats["Maps"] = mapDetails
    if('final' in matchStatus):
        matchStats["Economy"] = getEconomyStats(matchID)

    return matchStats

def getPlayerDataMatch(statsContainer, teamAName, teamBName): #to help with getMatchStats
    matchStats = {}
    tbdCounter = 0
    for game in statsContainer:
        mapDetails = {}
        if(game['data-game-id'] != 'all'):
            mapName = game.find('div', class_ = "map").getText().strip().split()[0] 
            if(mapName != 'TBD'):
                mapDetails["rndsA"] = game.findAll('div', class_ = "score")[0].getText().strip().split()[0]
                mapDetails["rndsB"] = game.findAll('div', class_ = "score")[1].getText().strip().split()[0]
                if((mapDetails["rndsA"] == "0") and (mapDetails["rndsB"] == "0")):
                    matchStats[mapName] = 'None'
                    continue
                mapDetails["TrndsA"] = game.findAll('span', class_ = "mod-t")[0].getText().strip()
                mapDetails["TrndsB"] = game.findAll('span', class_ = "mod-t")[1].getText().strip()
                mapDetails["CTrndsA"] = game.findAll('span', class_ = "mod-ct")[0].getText().strip()
                mapDetails["CTrndsB"] = game.findAll('span', class_ = "mod-ct")[1].getText().strip()
            else:
                matchStats["TBD" + str(tbdCounter)] = 'None'
                tbdCounter += 1
                continue
        else:
            mapName = 'all'
        
        playerTables = game.findAll('tbody')
        mapDetails[teamAName] = loadPlayerData(playerTables[0].findAll('tr'))
        mapDetails[teamBName] = loadPlayerData(playerTables[1].findAll('tr'))

        matchStats[mapName] = mapDetails

    return matchStats

def loadPlayerData(players): #to help with getPlayerDataMatch
    playerStats = {}
    for player in players:
        playerDic = {}
        info = player.findAll('td')
        name = player.find('div', class_ = "text-of").getText().strip().split()[0]
        try:
            playerDic["agent"] = player.find('img')["alt"]
        except TypeError:
            playerDic['agent'] = '0'
        try:
            playerDic["rating"] = info[2].getText().strip().split()[0]
        except IndexError:
            playerDic["rating"] = '0'
        try:
            playerDic["acs"] = info[3].getText().strip().split()[0]
        except IndexError:
            playerDic["acs"] = '0'
        try:
            playerDic["kills"] = info[4].getText().strip().split()[0]
        except IndexError:
            playerDic["kills"] = '0'
        try:
            playerDic["deaths"] = info[5].find('span', class_ = "side mod-both").getText().strip().split()[0]
        except IndexError:
            playerDic["deaths"] = '0'
        try:
            playerDic["assists"] = info[6].getText().strip().split()[0]
        except IndexError:
            playerDic["assists"] = '0'
        try:
            playerDic["kdDiff"] = info[7].getText().strip().split()[0]
        except IndexError:
            playerDic["kdDiff"] = '0'
        try:
            playerDic["kast"] = info[8].getText().strip().split()[0]
        except IndexError:
            playerDic["kast"] = '0'
        try:
            playerDic["adr"] = info[9].getText().strip().split()[0]
        except IndexError:
            playerDic["adr"] = '0'
        try:
            playerDic["hsPercent"] = info[10].getText().strip().split()[0]
        except IndexError:
            playerDic["hsPercent"] = '0'
        try:
            playerDic["firstKills"] = info[11].getText().strip().split()[0]
        except IndexError:
            playerDic["firstKills"] = '0'
        try:
            playerDic["firstDeaths"] = info[12].getText().strip().split()[0]
        except IndexError:
            playerDic["firstDeaths"] = '0'
        try:
            playerDic["fkDiff"] = info[13].getText().strip().split()[0]
        except IndexError:
            playerDic["fkDiff"] = '0'

        playerStats[name] = playerDic

    return playerStats

def getEconomyStats(matchID):
    matchEconStats = {}
    url = "https://www.vlr.gg/" + str(matchID) + "/?game=all&tab=economy"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    soup.find('div', class_ = 'vm-stats-game mod-active').decompose()
    allStats = soup.find('div', class_ = 'vm-stats-container').findAll('div', class_ = 'vm-stats-game')
    allStats = [mapStat for mapStat in allStats if 'not available yet' not in mapStat.getText()]

    i = 1
    for mapStat in allStats:
        mapEconStats = {}
        econStats = mapStat.findAll('table', class_ = 'wf-table-inset mod-econ')[1].findAll('td')
        j = 1
        for stat in econStats:
            if('BANK' not in stat.getText()):
                comments = stat.find_all(string = isComment)
                team1Bank = stat.findAll('div', class_ = 'bank')[0].getText().strip()
                team2Bank = stat.findAll('div', class_ = 'bank')[1].getText().strip()
                team1Loadout = getValue(comments[0])
                team2Loadout = getValue(comments[1])

                winBox = stat.findAll('div', class_ = 'rnd-sq')
                if('mod-win' in str(winBox[0])):
                    team1Win = True
                else:
                    team1Win = False

                mapEconStats[j] = {
                    "Team1Bank" : team1Bank,
                    "Team2Bank" : team2Bank,
                    "Team1Loadout" : team1Loadout,
                    "Team2Loadout" : team2Loadout,
                    "Team1Win" : team1Win
                }
                j += 1
            else:
                continue
        matchEconStats["Map" + str(i)] = mapEconStats
        i += 1

    return matchEconStats

def isComment(input):
    return isinstance(input, Comment)

def getValue(input):
    match = re.search(r'(\d+\.\d+)', input)
    if match:
        return str(match.group(1))
    else:
        return None