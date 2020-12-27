# -*- coding: utf-8 -*-
import datetime as dt
from scrapy import Spider, Request
from models import Game, Question, Round


class Jeopardy(Spider):
    name = "jeopardy"

    def start_requests(self):
        yield Request("http://www.j-archive.com/listseasons.php", self.season)
    
    def season(self, response):
        # Follow links to each season
        for a in response.xpath('//a[contains(@href, "showseason.php?season=")]'):
            yield response.follow(a, self.episode)
    
    def episode(self, response):
        # Create record of each game
        for tr in response.xpath('//tr[td[a[contains(@href, "showgame.php?game_id=")]]]'):
            game, created = Game.parse_get_or_create(tr)

            # If the game has not been seen, or not successfully crawled
            if created or not game.crawled:

                # Follow the link to the game
                for a in tr.xpath('.//a'):
                    yield response.follow(a, meta={'game': game})
    
    def parse(self, response):
        # For each game round
        for rnd in Round:

            # Collect a list of all categories
            category_xpath = f'//*[@id="{rnd.name}_round"]//td[@class="category"]'
            categories = [x.xpath('normalize-space(.)').get() for x in response.xpath(category_xpath)]

            # For each clue in the round, create a record
            for td in response.xpath(
                f'//*[@id="{rnd.name}_round"]'
                if rnd.name == "final_jeopardy" else
                f'//*[@id="{rnd.name}_round"]//td[@class="clue"]'
            ):
                Question.parse_create(td, rnd, categories, response.url)
        
        # After parsing all clues, record the game's crawl date
        response.meta['game'].crawled = dt.datetime.now()
        response.meta['game'].save()
