import json
import urllib3
from collections import defaultdict
from pathlib import Path

http = urllib3.PoolManager()
game_info_file = Path('game_info.json')
correct_order = {'ACE': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'JACK': 11, 'QUEEN': 12, 'KING': 13}
choice = ''

def shuffle_cards(http):
    deck = http.request('GET', 'http://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1')
    data = json.loads(deck.data.decode())

    return data['deck_id']

def new_game(http):
    deck_id = shuffle_cards(http)
    #defaultdict lets us easily iterate the value (count) in running_list
    running_list = defaultdict(int)

    return deck_id, running_list

def draw_card(http, deck_id):
  draw_url = http.request('GET','http://deckofcardsapi.com/api/deck/{}/draw/?count=1'.format(deck_id))
  data = json.loads(draw_url.data.decode())

  return data

def sort_list(running_list, correct_order):
    #convert dictionary to list so we can sort
    list = running_list.items()
    #sort the list by using the correct_order dictionary as a map
    ordered_list = sorted(list, key=lambda x: correct_order[x[0]])

    return ordered_list

def save_game_info(deck_id, running_list):
    with open('game_info.json', 'w') as file:
        json.dump({'id': deck_id, 'totals': running_list}, file)
    file.closed

def read_game_info():
    with open('game_info.json', 'r') as file:
        game_info = json.load(file)
    file.closed

    deck_id = game_info['id']
    running_list = defaultdict(int, game_info['totals'])

    return deck_id, running_list


# Game runtime code starts here
#
# Check for save data
if game_info_file.exists():
    deck_id, running_list = read_game_info()
    print("I've detected an existing deck from a previous game. Continuing with deck ID {}".format(deck_id))
else:
    # No save data, create new game
    deck_id, running_list = new_game()
    print("No game info detected. Starting a new game with deck ID {}".format(deck_id))

# Request user input via while loop and options
print('\nGame time!')
while choice != 'q':
    print('\nWhat do you want to do?')
    print('\n[1] Enter 1 to re-shuffle deck')
    print('[2] Enter 2 to draw a card')
    print('[q] Enter q to quit')

    choice = input("\nWhat would you like to do? ")

    if choice == '1':
        deck_id, running_list = new_game()
        save_game_info(deck_id, running_list)
        print('The deck has been shuffled. Your new deck ID is: {}'.format(deck_id))
    elif choice == '2':
        card = draw_card(http, deck_id)
        card_value = card['cards'][0]['value']
        print('Drew a card! The value is {}'.format(card_value))
        # this operation is why we needed defaultdict
        running_list[card_value] += 1
        print('\nTotals: {}'.format(dict(running_list)))
        print('\nCards remaining: {}'.format(card['remaining']))
        # if we use up all 52 cards, complain, re-shuffle, and end the game
        if card['remaining'] == 0:
            print('IM OUT OF CARDS!! Game over.')
            # if out of cards go ahead and instantiate a new game
            deck_id, running_list = new_game()
            save_game_info(deck_id, running_list)
            choice = 'q'
    elif choice == 'q':
        # quit game but save info
        save_game_info(deck_id, running_list)
        print('\nSmell ya later!')
    else:
        print("No comprende. Pls enter a valid option.")

# print the final tally using the correct_order dictionary as a map
print('Final tally: {}'.format(sort_list(dict(running_list), correct_order)))