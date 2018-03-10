import requests
from bs4 import BeautifulSoup

wiki_url = 'https://en.wikipedia.org'
main_url = 'https://en.wikipedia.org/wiki/Chinese_Super_League'

players = set()

r = requests.get(main_url) 

soup = BeautifulSoup(r.text, 'lxml')

# find current team names and urls
team_urls = {}

_h2 = None

for _ in soup.find_all(id='Current_clubs'):
	if len({'current', 'clubs'} & set(_.text.strip().lower().split())) == 2:
		_h2 = _.parent
		break

if _h2:

	try:
		tb = _h2.find_next_sibling('table', 'wikitable')
		print('found team name table')
	except:
		print('can\'t find the table with team names!')

	for row in tb.find_all('tr'):

		td = row.find('td')

		if td:
			a = td.find('a')
			team_urls.update({a.text.lower().strip(): wiki_url + a['href']})
		else:
			continue

print(f'total {len(team_urls)} teams')
print(team_urls)

for team in team_urls:

	print(f'scraping {team}...')

	soup = BeautifulSoup(requests.get(team_urls[team]).text, 'lxml')

	_h2 = None

	for _ in soup.find_all(id='Current_squad'):

		_h2 = _.parent
		break

	if _h2:

		try:
			tb = _h2.find_next_sibling('table')
		except:
			print('no table with players')

		for row in tb.find_all(class_='vcard agent'):

			for i, td in enumerate(row.find_all('td')):

				if i == 1:
					try:
						sp = td.find('span')
					except:
						continue
					try:
						a = sp.find('a')
					except:
						continue

				if (i == 3) and (a['title'].lower() == 'china'):
					players.add(td.text.lower().strip().split('(')[0].strip())

	print(f'players so far: {len(players)}')

with open('chinese_players.txt','w') as f:
	for p in players:
		f.write(f'{p}\n')




