histemul
========

Grand strategic engine game

Introduction : 

This game is composed with two programs:

-First is the server part : it used a python version >= 3.2 and the lib python-yaml >= 3 (in version for python 3)

-Second is the client part : it used C++/Qt5 (>=5.1). The core of the client is an executable and the user interface is defined with QtQuick2 technology.


Building the client part :

- Ubuntu 14.04 :

Install :
build-essential
qt5-qmake
qtdeclarative5-qtquick2-plugin
qtdeclarative5-dev
libqt5opengl5-dev
fonts-linuxlibertine


Go in a terminal in the directory src and launch :
qmake
make

You can clean the directory with :
make clean

For the moment, there isn't make install command.


Launching the game :


Launch the server program with :
python3 histemul_server
or
make histemul_server executable and launch it


after that you can launch the client side, launch histemul_client_qt executable. 



