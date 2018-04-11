import requests
from bs4 import BeautifulSoup
import os
import re


class LocalFootballerScraper:

	def __init__(self, country):

		self.wiki_url = 'https://en.wikipedia.org'

		self.domestic_leagues = {'france':  	[f'{self.wiki_url}/wiki/Ligue_1',
												 f'{self.wiki_url}/wiki/Ligue_2'],
								  'china':  	[f'{self.wiki_url}/wiki/Chinese_Super_League',
								  				 f'{self.wiki_url}/wiki/China_League_One'],
								  'mexico': 	[f'{self.wiki_url}/wiki/Liga_MX',
								  				 f'{self.wiki_url}/wiki/Ascenso_MX'],
								  'vietnam':	[f'{self.wiki_url}/wiki/V.League_1',
								  			 	 f'{self.wiki_url}/wiki/V.League_2'],
								  'japan': 		[f'{self.wiki_url}/wiki/J.League',
								  				 f'{self.wiki_url}/wiki/J2_League'],
								  'spain': 		[f'{self.wiki_url}/wiki/La_Liga',
								  				 f'{self.wiki_url}/wiki/Segunda_División'],
								  'croatia': 	[f'{self.wiki_url}/wiki/Croatian_First_Football_League'],
								  'serbia': 	[f'{self.wiki_url}/wiki/Serbian_SuperLiga'],
								  'turkey': 	[f'{self.wiki_url}/wiki/Süper_Lig',
								  			 	 f'{self.wiki_url}/wiki/TFF_First_League'],
								  'india': 		[f'{self.wiki_url}/wiki/I-League',
								  				 f'{self.wiki_url}/wiki/I-League_2nd_Division'],
								  'greece': 	[f'{self.wiki_url}/wiki/Superleague_Greece',
								  				 f'{self.wiki_url}/wiki/Football_League_(Greece)'],
								  'south korea': [f'{self.wiki_url}/wiki/K_League_1',
								  				  f'{self.wiki_url}/wiki/K_League_2'],
								  'italy': 		[f'{self.wiki_url}/wiki/Serie_A',
								  				 f'{self.wiki_url}/wiki/Serie_B'],
								  'slovenia': 	[f'{self.wiki_url}/wiki/Slovenian_PrvaLiga'],
								  'england': 	[f'{self.wiki_url}/wiki/Premier_League',
								  				 f'{self.wiki_url}/wiki/EFL_Championship'],
								  'saudi arabia': [f'{self.wiki_url}/wiki/Saudi_Professional_League'],
								  'united arab emirates': [f'{self.wiki_url}/wiki/UAE_Pro-League'],
								  'qatar': [f'{self.wiki_url}/wiki/Qatar_Stars_League'],
								  'portugal': [f'{self.wiki_url}/wiki/Primeira_Liga',
								  				f'{self.wiki_url}/wiki/LigaPro']}
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
			if ('former' not in tx) and ('founding' not in tx) and ('performance' not in tx):
				if ('current' in tx) or ('clubs' in tx) or ('members' in tx) or ('teams' in tx):
					_id = a['href'][1:]
					break
		if not _id:
			return None

		_h2 = soup.find(id=_id).parent

		if _h2:

			try:
				tbs = _h2.find_next_siblings('table', 'wikitable')
			except:
				print('can\'t find any tables with team names!')
				return self

			tb = None    # team table

			for _tb in tbs:

				_headers = _tb.find_all('th')

				if _headers:

					_ = {h.text.lower().strip() for h in _headers}
					_header_words = {w for h in _ for w in h.split()}

					if {'performance', 'champions', 'wins', 'years', 'winning', 'staff'} & _header_words:
						continue
				
				rows = _tb.find_all('tr')

				first_row = rows[0]

				if 'league' in rows[0].text.lower():
					first_row = rows[1]

				if first_row:
					hdr = first_row.find('th')
					if hdr:
						if hdr.text.lower().strip() in {'club', 'team'}:
							tb = _tb
							break
			if not tb:
				print('can\'t find any tables with team names!')
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

	def _find_flag_player(self, tab):
		"""
		find which columns contain country flags and player names
		"""

		idx_country = idx_player = None

		_first_row = tab.find('tr')

		if not _first_row:
			print('table without rows?')
			return (None, None)
		else:
			td_children = sum([1 for c in _first_row.children if c.name == 'td'])
			if td_children == 3:
				_hs = _first_row.find('td').find_all('th')
			else:
				_hs = _first_row.find_all('th')
			if not _hs:
				print('table has no header!')
				return (None, None)
			else:
				for i, h in enumerate(_hs):
					
					header_text = h.text.lower().strip()
					if 'player' in header_text:
						idx_player = i
					if 'nation' in header_text:
						idx_country = i
		
		if not idx_country:

			player_row = tab.find(class_='vcard agent')

			if not player_row:
				print('table without players?')
				return (None, None)
			else:

				for i, _ in enumerate(player_row.find_all('td')):
					if _.find(class_='flagicon'):
						idx_country = i
						break

		return (idx_country, idx_player)
		

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
					print('headline not followed by a table!!')
					return self

				else:

					if 'staff' in ' '.join([h.text.lower() for h in tb.find_all('th')]):
						return self

					idx_country, idx_player = self._find_flag_player(tb)

					if all([idx_country, idx_player]):
				
						rows_pl = tb.find_all(class_='vcard agent')
		
						if rows_pl:
		
							for row in rows_pl:
	
								_country = _player = None
				
								for i, td in enumerate(row.find_all('td')):		
	
									if i == idx_country:
	
										try:
											_country = td.find('a')['title'].lower()
										except:
											print('can\'t find country!')
	
									if i == idx_player:
	
										_spans = td.find_all('span')
	
										if _spans:
	
											_player = _spans[-1].text.lower().strip().split('(')[0].strip()
											
											if 'on loan' in _player:
												_player = _player.split('on loan')[0].strip()
	
								if _country and _player and (_country == self.COUNTRY):
									self.players.add(_player)
	
		return self

	def get_names(self):

		for league_url in self.domestic_leagues[self.COUNTRY]:
			self._get_club_urls(league_url)

		for team in self.team_urls:

			print(f'{team.upper()}...')

			for span_id in """Current_squad First_team First-team_squad First-Team_Squad First_Team_Squad Reserve_team On_loan 
								Out_on_loan Reserve_squad First_team_squad Senior_team_squad Reserve_teams Players""".split():
				self._get_squad_table(self.team_urls[team], span_id)

		return self

	def save_to_file(self):

		with open(os.path.join(self.DATA_DIR, f'players_{self.COUNTRY}.txt'),'w') as f:
			for p in self.players:
				f.write(f'{p}\n')
		print(f'saved {len(self.players)} player names')

if __name__ == '__main__':

	c = LocalFootballerScraper('portugal').get_names().save_to_file()




