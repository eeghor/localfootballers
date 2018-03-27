import requests
from bs4 import BeautifulSoup
import os
import re


class LocalFootballerScraper:

	def __init__(self, country):

		self.wiki_url = 'https://en.wikipedia.org'

		self.domestic_leagues = {'france': ['https://en.wikipedia.org/wiki/Ligue_1',
											'https://en.wikipedia.org/wiki/Ligue_2'],
								  'china': ['https://en.wikipedia.org/wiki/Chinese_Super_League',
								  			'https://en.wikipedia.org/wiki/China_League_One'],
								  'mexico': ['https://en.wikipedia.org/wiki/Liga_MX',
								  			 'https://en.wikipedia.org/wiki/Ascenso_MX'],
								  'vietnam': ['https://en.wikipedia.org/wiki/V.League_1',
								  			  'https://en.wikipedia.org/wiki/V.League_2'],
								  'japan': ['https://en.wikipedia.org/wiki/J.League',
								  			  'https://en.wikipedia.org/wiki/J2_League']}
		self.COUNTRY = country
		self.team_urls = {}
		self.DATA_DIR = 'collected_data'

		self.players = set()

		if not os.path.exists(self.DATA_DIR):
			os.mkdir(os.path.join(os.path.curdir, self.DATA_DIR))

	def _get_club_urls(self, league_url):

		soup = BeautifulSoup(requests.get(league_url).text, 'lxml')	

		toc = soup.find('div', class_='toc')

		_id = None

		for a in toc.find_all("a"):
			tx = a.text.lower().strip()
			if ('former' not in tx) and ('founding' not in tx):
				if ('current' in tx) or ('clubs' in tx) or ('members' in tx):
					_id = a['href'][1:]
					break
		if not _id:
			return None

		_h2 = soup.find(id=_id).parent

		if _h2:

			try:
				tb = _h2.find_next_sibling('table', 'wikitable')
			except:
				print('can\'t find the table with team names!')
				return self

			rows = tb.find_all('tr')
			
			if not rows:
				print('there are no rows in the current clubs table!')
				return self
			else:
				for row in rows:
			
					td = row.find('td')
			
					if td:
						a = td.find('a')
						if a:
							self.team_urls.update({a.text.lower().strip(): self.wiki_url + a['href']})
					else:
						continue
			return self


	def _get_squad_table(self, url, span_id):


		soup = BeautifulSoup(requests.get(url).text, 'lxml')

		_h2 = None

		right_ids = soup.find_all(id=span_id)

		if right_ids:

			for _ in soup.find_all(id=span_id):
				_h2 = _.parent
				break
	
			if _h2:
	
				tb = _h2.find_next_sibling('table')
				
				if not tb:
					print('found a header but no table!')
					return self

				else:
				
					rows_pl = tb.find_all(class_='vcard agent')
	
					if rows_pl:
	
						for row in rows_pl:
			
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
			
								if (i == 3) and (a['title'].lower() == self.COUNTRY):
									self.players.add(td.text.lower().strip().split('(')[0].strip())
	
		return self

	def get_names(self):

		for league_url in self.domestic_leagues[self.COUNTRY]:
			self._get_club_urls(league_url)

		for team in self.team_urls:

			print(f'{team.upper()}...')

			for span_id in """Current_squad First_team First-team_squad Reserve_team On_loan 
								Out_on_loan Reserve_squad First_team_squad Reserve_teams""".split():
				self._get_squad_table(self.team_urls[team], span_id)

		return self

	def save_to_file(self):

		with open(os.path.join(self.DATA_DIR, f'players_{self.COUNTRY}.txt'),'w') as f:
			for p in self.players:
				f.write(f'{p}\n')
		print(f'saved {len(self.players)} player names')

if __name__ == '__main__':

	c = LocalFootballerScraper('japan').get_names().save_to_file()




