# Energetic_Nightfall
Multiplayer LAN space fighting game which involves semi-realistic style for space physics and weapon systems

Needed classes:
- Player ship
	- class to be controlled by the players which handles both local player input as well as remote player interactions
	- Handles damage calculations
	- Spawns an explosion on its death
	- Communicates with UI elements for state
	- Controls own color and animations
	- Name tag above ship
- Weapon Manager
	- Handles local and remote player weapon spawns
	- Handles cooldowns for each weapon
	- Communicates with UI elements
	- Display targeting hud depending on weapon
- UI elements
	- Health bar for self
	- Weapon selection and options
	- Handle cooldown for abilities
- Start Menu
	- Connection to server (ip and port)
	- Display Name
	- Lobby for connected ships in game
	- Loads game level based on server direction which scene to load at random or with a vote
	- Game mode selector drop down(maybe vote)

