# ExperimentalPenguins
HTML5 Remake of Experimental Penguins out of nostalgia 

To run the server:
```
python3 server.py
```

To run the client you can upload everything in web/ to a webserver or
```
python3 -m http.server 8080
```

![Image of Experimental Penguins running](/epeng_screenshot.png)
200 Penguins running smoothly in one room
![Image of Experimental Penguins running](/epeng_screenshot_2.png)

Problems:
```
- [done]: the redrawing is not smooth if there is too many penguins in the room.
- incorrect penguin positioning on switching rooms mid draw?
- message "bubbles" need to be drawn last or penguins get drawn ontop of them.
- penguin size is injectable thus being changed
- same with position. 
```
