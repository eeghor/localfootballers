import requests
from bs4 import BeautifulSoup


class ChineseSLScraper:

	def __init__(self):

		self.wiki_url = 'https://en.wikipedia.org'
		self.main_url = 'https://en.wikipedia.org/wiki/Chinese_Super_League'
		self.team_urls = {}

		self.players = set()

	def _get_club_urls(self):

		soup = BeautifulSoup(requests.get(self.main_url).text, 'lxml')	

		_h2 = None

		for _ in soup.find_all(id='Current_clubs'):
			if not ({'current', 'clubs'} - set(_.text.strip().lower().split())):
				_h2 = _.parent
				break

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
			
								if (i == 3) and (a['title'].lower() == 'china'):
									self.players.add(td.text.lower().strip().split('(')[0].strip())
	
		return self

	def get_names(self):

		self._get_club_urls()

		for team in self.team_urls:

			print(f'{team.upper()}...')

			for span_id in 'Current_squad First_team Reserve_team On_loan Reserve_squad First_team_squad'.split():
				self._get_squad_table(self.team_urls[team], span_id)

		return self

	def save_to_file(self, file_name):

		with open(file_name,'w') as f:
			for p in self.players:
				f.write(f'{p}\n')
		print(f'saved {len(self.players)} player names to {file_name}')

if __name__ == '__main__':

	c = ChineseSLScraper().get_names().save_to_file('chinese_superleague_players.txt')




