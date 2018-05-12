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

#include "view.h"

void View::resizeEvent(QResizeEvent * ev)
{
    mMap->resize(ev->size(), ev->oldSize());
    QQuickItem* rootQml = rootObject();
    rootQml->setProperty("width", ev->size().width());
    rootQml->setProperty("height", ev->size().height());
}

View::View(unsigned int width, unsigned int height, QString ui, QUrl url, bool debug, QString player)
{
    qmlRegisterType<Map>("Histemul", 0,1, "Map");

    setWidth(width);
    setHeight(height);
    setResizeMode(QQuickView::SizeRootObjectToView);
    rootContext()->setContextProperty("url", url);
    rootContext()->setContextProperty("player", player);

    setSource(QUrl::fromLocalFile(ui));

    QQuickItem* rootQml = rootObject();
    mMap = rootQml->findChild<Map *>("map");
    mMap->init(width, height, url, debug, player);
}
