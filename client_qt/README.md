Histemul
========
Histemul is the engine of a massive multiple online grand strategy game.
This engine game is completed with a complete set of files to make a complete game.
All this files are distributed under BSD 2 clause license (see Licence file) except files in CREDIT file.

Client
------
The client is the part of the project which have the display of the game. It is encoded in Qt/C++.

For building for linux :

install on Ubuntu :
* build-essential
* qt5-qmake
* qtdeclarative5-qtquick2-plugin
* qtdeclarative5-dev
* libqt5opengl5-dev
* fonts-linuxlibertine

Go in a terminal in the directory src and launch :
qmake
make

You can clean the directory with :
make clean

For the moment, there isn't make install command.

For launching on Ubuntu 18.04, you need :
* libqt5core5a
* libqt5gui5
* libqt5network5
* libqt5qml5
* libqt5quick5
* libqt5widgets5
* fonts-linuxlibertine


