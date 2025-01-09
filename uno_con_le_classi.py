from flask import Flask, render_template, request
import random

class Card:
    def __init__(self, color: str, value: str):
        self.color = color
        self.value = value

    def __repr__(self):
        return f"{self.value} {self.color}"
    
    def __eq__(self, value: object) -> bool:
        return isinstance(value, Card) and self.color == value.color and self.value == value.value

class Deck:
    def __init__(self, cards: list[Card]):
        self.cards = cards

    @staticmethod
    def create_deck() -> list[Card]:
        deck = []
        for color in ["red", "green", "yellow", "blue"]:
            for value in range(10):
                deck.append(Card(color, str(value)))
            for effect in ["reverse", "skip", "picker"]:
                deck.append(Card(color, effect))
        for effect in ["pick_four"]:
            deck.append(Card("wild", effect))
        random.shuffle(deck)
        return deck

    def shuffle_deck(self):
        random.shuffle(self.cards)

    def draw_card(self) -> Card | None:
        return self.cards.pop() if self.cards else None

    def get_top_card(self) -> Card | None:
        return self.cards[-1] if self.cards else None

class Player:
    def __init__(self, name: str):
        self.name = name
        self.cards = list[Card]()
        self.said_uno = False

    def add_card(self, card: Card):
        self.cards.append(card)

    def remove_card(self, card: Card):
        self.cards.remove(card)

    def has_card(self, card: Card) -> bool:
        return card in self.cards

class Game:
    def __init__(self):
        initial_deck = Deck.create_deck()
        self.deck = Deck(initial_deck[0:-1])
        self.player = Player("player")
        self.opponent = Player("opponent")
        self.played_cards = [initial_deck[-1]]
        self.turn_count = 0
        self.last_player_name = None
        self.last_played_card_turn = 0
        self.turn_player_said_uno = None
        self.setup_players()

    def setup_players(self):
        for _ in range(7):
            self.player.add_card(self.draw_deck_card())
            self.opponent.add_card(self.draw_deck_card())

    def get_last_played_card(self) -> Card | None:
        return self.played_cards[-1] if self.played_cards else None

    def can_execute_turn(self, player_name: str) -> bool:
        if self.last_player_name == player_name or self.last_player_name is None or self.last_played_card_turn < self.turn_count - 1:
            return True
        top_card = self.get_last_played_card()
        if top_card is None:
            return False
        return top_card.value not in ["skip", "reverse", "picker", "pick_four"]

    def can_card_be_played(self, card: Card) -> bool:
        top_card = self.get_last_played_card()
        if top_card is None:
            return False
        return card.color == top_card.color or card.value == top_card.value or card.color == "wild" or top_card.color == "wild"

    def execute_card_effect(self, target_player: Player):
        top_card = self.get_last_played_card()
        if top_card is None:
            return
        if top_card.value == "picker":
            target_player.add_card(self.draw_deck_card())
            target_player.add_card(self.draw_deck_card())
        elif top_card.value == "pick_four":
            for _ in range(4):
                target_player.add_card(self.draw_deck_card())

    def execute_player_turn(self, action: str, played_card: Card | None = None) -> bool:
        if action == "draw":
            self.player.add_card(self.draw_deck_card())
            return True
        elif action == "pass":
            return True
        elif action == "uno":
            self.turn_player_said_uno = self.turn_count
            return True
        elif action == "play" and isinstance(played_card, Card) and self.player.has_card(played_card) and self.can_card_be_played(played_card):
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
        self.opponent.add_card(self.draw_deck_card())

    def get_winner(self) -> str:
        if len(self.player.cards) == 0:
            return "player"
        elif len(self.opponent.cards) == 0:
            return "opponent"
        return ""
    
    def draw_deck_card(self) -> Card:
        card = self.deck.draw_card()
        if isinstance(card, Card):
            return card
        self.deck = Deck(self.played_cards[0:-1])
        self.deck.shuffle_deck()
        self.played_cards = [self.played_cards[-1]]
        return self.draw_deck_card()

# Inizio di Flask
app = Flask(__name__, static_url_path="")
game = Game()

@app.route("/", methods=["GET", "POST"])
def index():
    winner = game.get_winner()
    if winner:
        return render_template("index.html", winner=winner, game=game)

    if game.can_execute_turn("player"):
        if request.method == "POST":
            action = request.form.get("action")
            if isinstance(action, str):
                played_card: Card | None = None
                played_card_name = request.form.get("played_card")
                if isinstance(played_card_name, str): 
                    played_card_data = played_card_name.split(" ")
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
        can_play=any(game.can_card_be_played(card) for card in game.player.cards),
        can_pass=True,
        winner=winner
    )

if __name__ == "__main__":
    app.run(debug=True, port=3000)
