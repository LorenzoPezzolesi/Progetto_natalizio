from flask import Flask, render_template, request
import random

class Card:
    def __init__(self, color, value):
        self.color = color
        self.value = value

    def __repr__(self):
        return f"{self.value} {self.color}"

class Deck:
    def __init__(self):
        self.cards = self.create_deck()
        self.shuffle_deck()

    def create_deck(self):
        deck = []
        for color in ["red", "green", "yellow", "blue"]:
            for value in range(10):
                deck.append(Card(color, str(value)))
            for effect in ["reverse", "skip", "picker"]:
                deck.append(Card(color, effect))
        for effect in ["pick_four"]:
            deck.append(Card("wild", effect))
        return deck

    def shuffle_deck(self):
        random.shuffle(self.cards)

    def draw_card(self):
        return self.cards.pop() if self.cards else None

    def get_top_card(self):
        return self.cards[-1] if self.cards else None

class Player:
    def __init__(self, name):
        self.name = name
        self.cards = []
        self.said_uno = False

    def add_card(self, card):
        self.cards.append(card)

    def remove_card(self, card):
        self.cards.remove(card)

    def has_card(self, card):
        return card in self.cards

class Game:
    def __init__(self):
        self.deck = Deck()
        self.player = Player("player")
        self.opponent = Player("opponent")
        self.played_cards = [self.deck.draw_card()]
        self.turn_count = 0
        self.last_player_name = None
        self.last_played_card_turn = 0
        self.turn_player_said_uno = None
        self.setup_players()

    def setup_players(self):
        for _ in range(7):
            self.player.add_card(self.deck.draw_card())
            self.opponent.add_card(self.deck.draw_card())

    def get_last_played_card(self):
        return self.played_cards[-1] if self.played_cards else "Nessuna"

    def can_execute_turn(self, player_name):
        if self.last_player_name == player_name or self.last_player_name is None or self.last_played_card_turn < self.turn_count - 1:
            return True
        top_card = self.get_last_played_card()
        return top_card.value not in ["skip", "reverse", "picker", "pick_four"]

    def can_card_be_played(self, card):
        top_card = self.get_last_played_card()
        return card.color == top_card.color or card.value == top_card.value or card.color == "wild" or top_card.color == "wild"

    def execute_card_effect(self, target_player):
        top_card = self.get_last_played_card()
        if top_card.value == "picker":
            target_player.add_card(self.deck.draw_card())
            target_player.add_card(self.deck.draw_card())
        elif top_card.value == "pick_four":
            for _ in range(4):
                target_player.add_card(self.deck.draw_card())

    def execute_player_turn(self, action, played_card=None):
        if action == "draw":
            self.player.add_card(self.deck.draw_card())
            return True
        elif action == "pass":
            return True
        elif action == "uno":
            self.turn_player_said_uno = self.turn_count
            return True
        elif played_card and self.player.has_card(played_card) and self.can_card_be_played(played_card):
            self.played_cards.append(played_card)
            self.player.remove_card(played_card)
            self.last_played_card_turn = self.turn_count
            self.execute_card_effect(self.opponent)
            return True
        return False

    def execute_opponent_turn(self):
        for card in self.opponent.cards:
            if self.can_card_be_played(card):
                self.played_cards.append(card)
                self.opponent.remove_card(card)
                self.last_played_card_turn = self.turn_count
                self.execute_card_effect(self.player)
                return
        self.opponent.add_card(self.deck.draw_card())

    def get_winner(self):
        if len(self.player.cards) == 0:
            return "player"
        elif len(self.opponent.cards) == 0:
            return "opponent"
        return ""

# Inizio di Flask
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    game = Game()

    winner = game.get_winner()
    if winner:
        return render_template("index.html", winner=winner, game=game)

    if game.can_execute_turn("player"):
        action = None
        played_card = None
        if request.method == "POST":
            action = request.form.get("action")
            if action == "play":
                played_card_data = request.form.get("played_card").split(" ")
                played_card = Card(played_card_data[1], played_card_data[0])
            game.execute_player_turn(action, played_card)

    if game.can_execute_turn("opponent"):
        game.execute_opponent_turn()

    return render_template(
        "index.html", 
        enemy_cards_count=len(game.opponent.cards), 
        last_played_card=game.get_last_played_card(), 
        player_cards=game.player.cards,
        player_cards_count=len(game.player.cards),
        can_draw=True, 
        can_play_any_card=any(game.can_card_be_played(card) for card in game.player.cards),
        can_pass=True,
        winner=winner
    )

if __name__ == "__main__":
    app.run(debug=True, port=3000)
