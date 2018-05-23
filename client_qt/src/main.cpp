/*Copyright 2012-2013 Matthieu Nué
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
THE POSSIBILITY OF SUCH DAMAGE.
*/

#include <QApplication>
#include "view.h"
#include <QUrl>
#include <QCommandLineParser>

int main(int argc, char *argv[])
{
    unsigned int width = 1024;
    unsigned int height = 768;
    QString player ("Matthieu");
    QUrl url("http://localhost:80/");
    bool fullScreen = true;


    QApplication app(argc, argv);
    QApplication::setAttribute(Qt::AA_UseDesktopOpenGL);
    QApplication::setApplicationName("histemul_client_qt");
    QApplication::setApplicationVersion("0.1");
    //QTranslator translator;
    //bool a = translator.load("histemul_fr");
    //app.installTranslator(&translator);

    QCommandLineParser parser;
    parser.setApplicationDescription("histemul_client_qt helper");
    parser.addHelpOption();
    parser.addVersionOption();
    parser.addPositionalArgument("url", QApplication::translate("main", "Url of the server."));


    QString ui("ui/ui.qml");
    View view(width, height, ui, url, false, player);
    if (fullScreen)
        view.showFullScreen();
    else
        view.show();
    app.exec();

    return(0);
}
