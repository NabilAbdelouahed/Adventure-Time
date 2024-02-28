Game description :

    A super-mario like game with levels and different obstacles. The player uses the left and right arrows to move and space key
to jump. The goal is to clear all levels by reaching the gate without getting killed by the obstacles.


Coding steps :
** In addition to this readme file, the code itself is well commented for more explanation **

1) we started with creating the game window with the background and divide it into tiles using a grid which will make placing objects
much easier.

2) Each level (world) is represented with a list of integers in which each integer represents a type of obstacle. We then created
a class called "wolrd" that reads the data list, creates a much useful format of obstacles list and draws the obstacles.

3) We created a class named player that draws the player on the window and updates his position based on the movement-keys pressed. We are going to
add the collisions later.

4) We then worked on the animation to make the game less static by running through the player's images at a certain speed when moving.

5) Next We worked on collision by using the rectangles formed in the background of each obstacle added and the player and making use of the built-in
collision detection in pygame.

6) We created a class for the enemies (blobs) rather than adding them directly with the " if " method like we did with grass and dirt because the
blobs will be moving around unlike the grass and dirt. To do this, we used an already built in class within pygame called "pygame.sprite.Sprite"
that helps manipulating moving objects which will be the blobs in our case. Here is a link for the documentation and functions of this class :
"https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite".

7) We then created a class for lava rather than adding them directly with the " if " method like we did with grass and dirt because the collisions
with lava are special as they indicate whether the game is over or not.

8) We added the conditions and animation for when the game is over.

9) Next we added a restart button for when the game is over that can restart the game and fixed the jumping bug to a one jump instead of multiple
jumps at a time.

10) We then created a main menu where you can either access the game or leave.

11) We created the data for seven levels in total and added the transitions between them as the player reaches the exit which was also added.

12) We added coins that can be collected which represent a score and displayed it with winning and losing texts .

13) Next we added the sound effects and the background music

14) Then we added moving platforms horizontaly and vertically

15) And finally moving platforms collisions were added.

Enjoy the game !