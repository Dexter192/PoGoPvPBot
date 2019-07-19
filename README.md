# Pokémon Go PvP Bot
Hey there! This is a Telegram bot for Pokemon Go PvP groups. Feel free to clone the repository and host your own version of the bot! If you want to test it first you can find a running version on Telegram @PoGoPvP_bot

## Installation

The bot can run with Python 2 and Python 3. Make sure, that you have Python installed.
You can double check it by entering 
```bash
python --version
>>> Python 2.7.16
```
You may need to install additional packages. Depending on your Python version use either ```pip install PACKAGENAME``` or ```pip3 install PACKAGENAME```
- python-telegram-bot==12.0.0b1
- pandas
- lxml
- requests

Lastly, you have to insert your telegram token in the config.json.example file and rename it to config.json.

## Usage

The bot has four core functions
- /trainername - Allows the user to set a trainername
- /pvp  - Create PvP-polls
- /iv   - Check the rank of a Pokémon for the great league according to [Go Stadium](https://gostadium.club/pvp/iv)
- ~~/rank - Check the [Silph Arena rank](hhttps://sil.ph/) of a player~~ - This will be reactivated once a public API by the TSA is released

### Trainernames
```/trainername``` can be used by players who's telegram username differs from their Pokemon Go username. After setting the trainername, the bot will mention the user with that name

### PvP-polls
With ```/pvp``` a user can create a PvP-poll. Other users can join and leave these polls by clicking the **fight** button below the PvP request. The creator of a poll can additionally customise the poll by providing additional information such as the league or specifying rules ```/pvp Great Mirror Cup```
If the creator of the poll has an open chat with the bot, it will send him a direct message which allows the creator to post the poll and return to the game immediately.

### IV checks
The bot can perform two types of IV-checks. The first one returns the optimal IV distribution for a Pokémon in the grat league which can be performed by ```/iv Shuckle```. 
A player can also check where a specific IV distribution ranks in the great league according to [Go Stadium](https://gostadium.club/pvp/iv). Such a request can be performed by specifying the IVs (A/D/S) ```/iv Shuckle 12 12 12```
To check the rank of alolan pokémon, ```+alolan``` must be appended to the pokémons name.

~~### Silph Ranks
Users can retrieve the current [Silph Arena rank](hhttps://sil.ph/) of any player who's profile is not set to private. ```/rank``` followed by the player name returns the current rank of a player - E.g. ```/rank ValorAsh``` ~~

## License
[MIT](https://choosealicense.com/licenses/mit/)
