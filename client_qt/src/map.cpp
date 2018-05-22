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

#include "map.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <cmath>
//#include <QTest>
#include <QOpenGLContext>
#include <QRegularExpression>
#include <QUrlQuery>
#include <QNetworkReply>
#include <QJsonDocument>
#include <QJsonArray>
#include <QJsonObject>
#include <QDir>
#include <QColor>

Map::Map()
{
    // configuration
    initShadingColor("./maps/config/shadingcolor.csv");
    for(std::vector<int>::size_type i = 0; i != mShadingColorIndex.size(); i++) {
        if (mShadingColorIndex[i] == "blue")
        {
            mColorRiver = i;
            break;
        }
    }

    readConfigMap("./maps/");
    mLevelInit = log(float(mSizeBlock))/log(2.);

    mBlock.resize(mNbBlockHeight * mNbBlockWidth);
    mHit.resize(mNbBlockWidth * mSizeBlock);

    std::vector<unsigned short> idMapLocal = returnValidIdMap("./maps/");

    for (unsigned int i = 0; i < idMapLocal.size(); i++)
    {
        addLightId(idMapLocal[i], "./maps/");
        addBoundsId(idMapLocal[i], "./maps/");
        addHitId(idMapLocal[i], "./maps/");
    }
    mMaxId = idMapLocal.size() - 1;

    mPosInQuad.push_back(QPoint(0,0));
    mPosInQuad.push_back(QPoint(1,0));
    mPosInQuad.push_back(QPoint(1,1));
    mPosInQuad.push_back(QPoint(0,1));

    p2.resize(8);
    p2[0] = 1;
    p2[1] = 2;
    p2[2] = 4;
    p2[3] = 8;
    p2[4] = 16;
    p2[5] = 32;
    p2[6] = 64;
    p2[7] = 128;

    mInitGL = false;
    mInit = false;
    mNext = All;
    //mFill = "";

    setFlag(QQuickItem::ItemHasContents, true);
    setAcceptedMouseButtons(Qt::AllButtons);
    mSelectedId = 0;
    mWaitForMove = false;
    mManager = new QNetworkAccessManager(this);
    mProText.resize(65536, "");
    QList<QString> black;
    black << "black" << "black";
    mProColor.resize(65536, black);
    connect(mManager, SIGNAL(finished(QNetworkReply *)), this, SLOT(slotProvinceUpdateReply(QNetworkReply*)));
    connect(this, &QQuickItem::windowChanged, this, &Map::handleWindowChanged);
}

Map::~Map()
{
    delete mFbo;
    delete mProgram;
}

void Map::init(unsigned int width, unsigned int height, QUrl url, bool debug, QString player)
{
    initSize(width, height);
    mUrl = url;
    mDebug = debug;
    mPlayer = player;
    updateDataProvince();
    mInit = true;

    return;
}

void Map::setStripe0(QString stripe)
{
    if (stripe != mStripe0)
    {
        mStripe0 = stripe;
        if (mInit) updateDataProvince();
    }
    return;
}

void Map::setStripe1(QString stripe)
{
    if (stripe != mStripe1)
    {
        mStripe1 = stripe;
        if (mInit) updateDataProvince();
    }
    return;
}

void Map::setT(qreal t)
{
    if (t == mT)
            return;
    mT = t;
    emit tChanged();
    mWindow->update();
}

void Map::handleWindowChanged(QQuickWindow *win)
{
    if (win)
    {
        connect(win, &QQuickWindow::beforeRendering, this, &Map::doJobBeforeRendering, Qt::DirectConnection);
        mWindow = win;
        // If we allow QML to do the clearing, they would clear what we paint
        // and nothing would show.
        win->setClearBeforeRendering(false);
    }
}

void Map::resize(QSize size, QSize oldSize)
{
    if (size != oldSize)
    {
        initSize(size.width(), size.height());
        mInitGL = false;
        mNext = All;
    }
    return;
}

void Map::calculateCoordinate()
{
    mLeftBlock = mTopLeftBlock % mNbBlockWidth;
    mTopBlock = mTopLeftBlock / mNbBlockWidth;
    mLeft = mLeftBlock * mSizeBlock;
    mTop = mTopBlock * mSizeBlock;
    mBlockScreen.setCoords(mLeftBlock, mTopBlock, mLeftBlock + mNbBlockScreenWidth, mTopBlock + mNbBlockScreenHeight);
    return;
}

void Map::updateDataProvince()
{
    QJsonObject postData;
    postData.insert("type", "get_all");
    postData.insert("player", mPlayer);
    postData.insert("cls", "province");
    postData.insert("id", "all");
    postData.insert("atts", QJsonArray({mStripe0, mStripe1}));


    QNetworkRequest request(mUrl);
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    mManager->post(request, QJsonDocument(postData).toJson());
}

void Map::inspectJson(int indexAttibute, QJsonObject obj, int id, QStringList stripe, int indexStripe)
{
    if (obj.contains(stripe.at(indexAttibute)))
    {
        if (obj[stripe.at(indexAttibute)].isObject())
            inspectJson(indexAttibute+1, obj[stripe.at(indexAttibute)].toObject(), id, stripe, indexStripe);
        else if (obj[stripe.at(indexAttibute)].isArray())
        {
            mProColor.at(id)[indexStripe] = obj[stripe.at(indexAttibute)].toArray().at(0).toString();
        }
        else
        {
            mProColor.at(id)[indexStripe] = obj[stripe.at(indexAttibute)].toString();
        }
    }
    else
    {
        mProColor.at(id)[indexStripe] = "black";
    }
}

void Map::slotProvinceUpdateReply(QNetworkReply* reply)
{
    if (reply->error() == QNetworkReply::NoError)
    {
       QJsonDocument jsonResponse = QJsonDocument::fromJson(reply->readAll());
       QJsonArray json_array = jsonResponse.array();
       QStringList s0 = mStripe0.split('.');
       QStringList s1 = mStripe1.split('.');
       QList<QStringList> stripes;
       stripes << s0 << s1;
       //QStringList f = fill().split('.');
       foreach (const QJsonValue & value, json_array){
            QJsonObject obj = value.toObject();
            int id = obj["_id"].toInt();
            for (int i=0; i<stripes.size(); ++i)
            {
                QStringList stripe = stripes.at(i);
                inspectJson(0, obj, id, stripe, i);
            }
        }
        mNext = All;
    }
    delete reply;
}

void Map::initSize(unsigned int width, unsigned int height)
{
    mWidth = width;
    mHeight = height;
    mScreen.setCoords(0, 0, mWidth, mHeight);

    if (mWidth % mSizeBlock == 0)
    {
        mNbBlockScreenWidth = mWidth / mSizeBlock;
        mWholeWidthBlock = true;
    }
    else
    {
        mNbBlockScreenWidth = mWidth / mSizeBlock + 1;
        mWholeWidthBlock = false;
    }

    if (mHeight % mSizeBlock == 0)
    {
        mNbBlockScreenHeight = mHeight / mSizeBlock;
        mWholeHeightBlock = true;
    }
    else
    {
        mNbBlockScreenHeight = mHeight / mSizeBlock + 1;
        mWholeHeightBlock = false;
    }

    //mQuadVertices.reserve(12*mWidth*mHeight/16);
    //mQuadColors.reserve(18*mWidth*mHeight/16);
    mMatrix.setToIdentity();
    mMatrix.ortho(QRect(0, 0,mWidth, mHeight));
    calculateCoordinate();
}

bool Map::initGL()
{
    initializeOpenGLFunctions();
    mProgram = new QOpenGLShaderProgram();
    mProgram->addShaderFromSourceCode(QOpenGLShader::Vertex,
                                       "attribute highp vec4 vertex;"
                                       "uniform highp mat4 matrix;"
                                       "attribute mediump vec4 color;"
                                       "varying mediump vec4 ex_color;"
                                       "void main() {"
                                       "    gl_Position = matrix * vertex;"
                                       "    ex_color = color;"
                                       "}");
    mProgram->addShaderFromSourceCode(QOpenGLShader::Fragment,
                                       "varying mediump vec4 ex_color;"
                                       "void main()"
                                       "{"
                                       "   gl_FragColor = ex_color;"
                                       "}");

    mProgram->bindAttributeLocation("vertex", 0);
    mProgram->bindAttributeLocation("color", 1);
    mProgram->link();
    mProgram->bind();

    if (!QOpenGLFramebufferObject::hasOpenGLFramebufferObjects())
    {
        std::cout <<"You graphic card doesn't support Framebuffer Object"<< std::endl;
        return (false);
    }
    if (!QOpenGLFramebufferObject::hasOpenGLFramebufferBlit())
    {
        std::cout <<"You graphic card doesn't support Framebuffer Blit operation"<< std::endl;
        return (false);
    }

    mFbo = new QOpenGLFramebufferObject(mWidth, mHeight, GL_TEXTURE_2D);
    glBindFramebuffer(GL_FRAMEBUFFER, 0);

    return (true);
}

void Map::writeFps()
{
    float fps = mFrame/2.0;
    mFrame = 0;
    std::cout << fps << std::endl;
}

void Map::move(EnumDirection d)
{
    mNext = d;
    if (mNext == OnLeft)
    {
        if ((mTopLeftBlock % mNbBlockWidth) <= 0) //left
        {
            mNext = None;
            return;
        }
    }
    else if (mNext == OnRight)
    {
        if (((mTopLeftBlock + mNbBlockScreenWidth) % mNbBlockWidth) <= 0)//right
        {
            mNext = None;
            return;
        }
    }
    else if (mNext == OnTop)
    {
        if ((mTopLeftBlock < mNbBlockWidth))//top
        {
            mNext = None;
            return;
        }

    }
    else if (mNext == OnBottom)
    {
        if (mTopLeftBlock >= (mNbBlockWidth * mNbBlockHeight - mNbBlockWidth * mNbBlockScreenHeight))//bottom
        {
            mNext = None;
            return;
        }
    }
    else if (mNext == OnTopLeft)
    {
        if (((mTopLeftBlock % mNbBlockWidth) <= 0) || (mTopLeftBlock < mNbBlockWidth))
        {
            mNext = None;
            return;
        }
    }
    else if (mNext == OnBottomLeft)
    {
        if (((mTopLeftBlock % mNbBlockWidth) <= 0) || (mTopLeftBlock >= (mNbBlockWidth * mNbBlockHeight - mNbBlockWidth * mNbBlockScreenHeight)))
        {
            mNext = None;
            return;
        }
    }
    else if (mNext == OnTopRight)
    {
        if ((((mTopLeftBlock + mNbBlockScreenWidth) % mNbBlockWidth) <= 0) || (mTopLeftBlock < mNbBlockWidth))
        {
            mNext = None;
            return;
        }
    }
    else if (mNext == OnBottomRight)
    {
        if ((((mTopLeftBlock + mNbBlockScreenWidth) % mNbBlockWidth) <= 0) || (mTopLeftBlock >= (mNbBlockWidth * mNbBlockHeight - mNbBlockWidth * mNbBlockScreenHeight)))
        {
            mNext = None;
            return;
        }
    }
    return;
}

bool Map::listVisibleProvince()
{
    QSet<quint16> provinceAdded;
    QSet<quint16> visibleProvince;

    for (unsigned int i = 0; i < mBoundsProvince.size(); ++i)
    {
        if (mBoundsProvince[i].intersects(mBlockScreen))
            visibleProvince.insert(i);
    }
    provinceAdded = visibleProvince - mVisibleProvince;
    mVisibleProvince = visibleProvince;
    if (!provinceAdded.empty())
        emit visibleProvinceChanged(provinceAdded);
    return (true);
}

void Map::changeTopLeftBlock(int interval)
{
    mTopLeftBlock += interval;
    calculateCoordinate();
    return;
}

void Map::doJobBeforeRendering()
{
    if (mNext != None)
    {
        if (!mWaitForMove)
        {
            if (mNext == All)
            {
                listVisibleProvince();
            }
            else
            {
                if (mNext == OnLeft)
                    changeTopLeftBlock(-1);
                else if (mNext == OnRight)
                    changeTopLeftBlock(1);
                else if (mNext == OnTop)
                    changeTopLeftBlock(-mNbBlockWidth);
                else if (mNext == OnBottom)
                    changeTopLeftBlock(mNbBlockWidth);
                else if (mNext == OnTopLeft)
                    changeTopLeftBlock(-mNbBlockWidth-1);
                else if (mNext == OnBottomLeft)
                    changeTopLeftBlock(mNbBlockWidth-1);
                else if (mNext == OnTopRight)
                    changeTopLeftBlock(-mNbBlockWidth+1);
                else if (mNext == OnBottomRight)
                    changeTopLeftBlock(mNbBlockWidth+1);
                listVisibleProvince();
                emit moved();
                mWaitForMove = true;
            }
        }
    }
    drawMap();
    return;
}

bool Map::drawMap()
{
    if (!mInitGL)
    {
        if (!initGL()) return (false);
        mInitGL = true;
        listVisibleProvince();
    }
    mFrame++;
    //std::cout << mFrame << std::endl;
    glViewport(0, 0, mWidth, mHeight);

    glDisable(GL_DEPTH_TEST);

    glClearColor(0, 0, 0, 1);
    glClear(GL_COLOR_BUFFER_BIT);
    if ((mNext == None))
    {
        QOpenGLFramebufferObject::blitFramebuffer(0, mScreen, mFbo, mScreen, GL_COLOR_BUFFER_BIT, GL_NEAREST);
        if (mRefreshId.empty())
            return (true);
    }
    else if (mNext == OnLeft)
    {
        mQuadVertices.clear();
        mQuadColors.clear();

        QOpenGLFramebufferObject::blitFramebuffer(0, QRect(mSizeBlock, 0, mWidth - mSizeBlock, mHeight), mFbo, QRect(0, 0, mWidth - mSizeBlock, mHeight), GL_COLOR_BUFFER_BIT, GL_NEAREST);

        int numBlock = mTopLeftBlock;

        for (int numBlockY = 0; numBlockY < mNbBlockScreenHeight; numBlockY++)
        {
            drawBlock(numBlock, 0, numBlockY * mSizeBlock);
            numBlock += mNbBlockWidth;
        }
    }
    else if (mNext == OnRight)
    {
        mQuadVertices.clear();
        mQuadColors.clear();

        QOpenGLFramebufferObject::blitFramebuffer(0, QRect(0, 0, mWidth - mSizeBlock, mHeight), mFbo, QRect(mSizeBlock, 0, mWidth - mSizeBlock, mHeight), GL_COLOR_BUFFER_BIT, GL_NEAREST);

        int numBlock = mTopLeftBlock + mNbBlockScreenWidth - 1;

        for (int numBlockY = 0; numBlockY < mNbBlockScreenHeight; numBlockY++)
        {
            drawBlock(numBlock, (mNbBlockScreenWidth - 1) * mSizeBlock, numBlockY * mSizeBlock);
            if (!mWholeWidthBlock) drawBlock(numBlock - 1, (mNbBlockScreenWidth - 2) * mSizeBlock, numBlockY * mSizeBlock);
            numBlock += mNbBlockWidth;
        }
    }
    else if (mNext == OnTop)
    {
        mQuadVertices.clear();
        mQuadColors.clear();

        QOpenGLFramebufferObject::blitFramebuffer(0, QRect(0, 0, mWidth, mHeight - mSizeBlock), mFbo, QRect(0, mSizeBlock, mWidth, mHeight - mSizeBlock), GL_COLOR_BUFFER_BIT, GL_NEAREST);
        int numBlock = mTopLeftBlock;

        for (int numBlockX = 0; numBlockX < mNbBlockScreenWidth; numBlockX++)
        {
            drawBlock(numBlock, numBlockX * mSizeBlock, 0);
            numBlock ++;
        }
    }
    else if (mNext == OnBottom)
    {
        mQuadVertices.clear();
        mQuadColors.clear();

        QOpenGLFramebufferObject::blitFramebuffer(0, QRect(0, mSizeBlock, mWidth, mHeight - mSizeBlock), mFbo, QRect(0, 0, mWidth, mHeight - mSizeBlock), GL_COLOR_BUFFER_BIT);

        int numBlock = mTopLeftBlock + mNbBlockWidth * (mNbBlockScreenHeight - 1);

        for (int numBlockX = 0; numBlockX < mNbBlockScreenWidth; numBlockX++)
        {
            drawBlock(numBlock, numBlockX * mSizeBlock, (mNbBlockScreenHeight - 1) * mSizeBlock);
            if (!mWholeHeightBlock) drawBlock(numBlock - mNbBlockWidth, numBlockX * mSizeBlock, (mNbBlockScreenHeight - 2) * mSizeBlock);
            numBlock ++;
        }
    }
    else if (mNext == OnTopLeft)
    {
        mQuadVertices.clear();
        mQuadColors.clear();

        QOpenGLFramebufferObject::blitFramebuffer(0, QRect(mSizeBlock, 0, mWidth - mSizeBlock, mHeight - mSizeBlock), mFbo, QRect(0, mSizeBlock, mWidth - mSizeBlock, mHeight - mSizeBlock), GL_COLOR_BUFFER_BIT);

        int numBlock = mTopLeftBlock;

        for (int numBlockY = 0; numBlockY < mNbBlockScreenHeight; numBlockY++)
        {
            drawBlock(numBlock, 0, numBlockY * mSizeBlock);
            numBlock += mNbBlockWidth;
        }

        numBlock = mTopLeftBlock + 1;

        for (int numBlockX = 1; numBlockX < mNbBlockScreenWidth; numBlockX++)
        {
            drawBlock(numBlock, numBlockX * mSizeBlock, 0);
            numBlock ++;
        }
    }
    else if (mNext == OnBottomLeft)
    {
        mQuadVertices.clear();
        mQuadColors.clear();

        QOpenGLFramebufferObject::blitFramebuffer(0, QRect(mSizeBlock, mSizeBlock, mWidth - mSizeBlock, mHeight - mSizeBlock), mFbo, QRect(0, 0, mWidth - mSizeBlock, mHeight - mSizeBlock), GL_COLOR_BUFFER_BIT);

        int numBlock = mTopLeftBlock;

        for (int numBlockY = 0; numBlockY < mNbBlockScreenHeight; numBlockY++)
        {
            drawBlock(numBlock, 0, numBlockY * mSizeBlock);
            numBlock += mNbBlockWidth;
        }

        numBlock = mTopLeftBlock + mNbBlockWidth * (mNbBlockScreenHeight - 1) + 1;

        for (int numBlockX = 1; numBlockX < mNbBlockScreenWidth; numBlockX++)
        {
            drawBlock(numBlock, numBlockX * mSizeBlock, (mNbBlockScreenHeight - 1) * mSizeBlock);
            if (!mWholeHeightBlock) drawBlock(numBlock - mNbBlockWidth, numBlockX * mSizeBlock, (mNbBlockScreenHeight - 2) * mSizeBlock);
            numBlock ++;
        }
    }
    else if (mNext == OnTopRight)
    {
        mQuadVertices.clear();
        mQuadColors.clear();

        QOpenGLFramebufferObject::blitFramebuffer(0, QRect(0, 0, mWidth - mSizeBlock, mHeight - mSizeBlock), mFbo, QRect(mSizeBlock, mSizeBlock, mWidth - mSizeBlock, mHeight - mSizeBlock), GL_COLOR_BUFFER_BIT);

        int numBlock = mTopLeftBlock + mNbBlockScreenWidth + mNbBlockWidth - 1;

        for (int numBlockY = 1; numBlockY < mNbBlockScreenHeight; numBlockY++)
        {
            drawBlock(numBlock, (mNbBlockScreenWidth - 1) * mSizeBlock, numBlockY * mSizeBlock);
            if (!mWholeWidthBlock) drawBlock(numBlock - 1, (mNbBlockScreenWidth - 2) * mSizeBlock, numBlockY * mSizeBlock);
            numBlock += mNbBlockWidth;
        }

        numBlock = mTopLeftBlock;

        for (int numBlockX = 0; numBlockX < mNbBlockScreenWidth; numBlockX++)
        {
            drawBlock(numBlock, numBlockX * mSizeBlock, 0);
            numBlock ++;
        }
    }
    else if (mNext == OnBottomRight)
    {
        mQuadVertices.clear();
        mQuadColors.clear();

        QOpenGLFramebufferObject::blitFramebuffer(0, QRect(0, mSizeBlock, mWidth - mSizeBlock, mHeight - mSizeBlock), mFbo, QRect(mSizeBlock, 0, mWidth - mSizeBlock, mHeight - mSizeBlock), GL_COLOR_BUFFER_BIT);

        int numBlock = mTopLeftBlock + mNbBlockScreenWidth - 1;

        for (int numBlockY = 0; numBlockY < mNbBlockScreenHeight; numBlockY++)
        {
            drawBlock(numBlock, (mNbBlockScreenWidth - 1) * mSizeBlock, numBlockY * mSizeBlock);
            if (!mWholeWidthBlock) drawBlock(numBlock - 1, (mNbBlockScreenWidth - 2) * mSizeBlock, numBlockY * mSizeBlock);
            numBlock += mNbBlockWidth;
        }

        numBlock = mTopLeftBlock + mNbBlockWidth * (mNbBlockScreenHeight - 1);

        for (int numBlockX = 0; numBlockX < mNbBlockScreenWidth - 1; numBlockX++)
        {
            drawBlock(numBlock, numBlockX * mSizeBlock, (mNbBlockScreenHeight - 1) * mSizeBlock);
            if (!mWholeHeightBlock) drawBlock(numBlock - mNbBlockWidth, numBlockX * mSizeBlock, (mNbBlockScreenHeight - 2) * mSizeBlock);
            numBlock ++;
        }
    }
    else if (mNext == All)
    {
        mQuadVertices.clear();
        mQuadColors.clear();
        mNbVertices = 0;

        int numBlock = mTopLeftBlock;

        for (int numBlockY = 0; numBlockY < mNbBlockScreenHeight; numBlockY++)
        {
            for (int numBlockX = 0; numBlockX < mNbBlockScreenWidth; numBlockX++)
            {
                drawBlock(numBlock, numBlockX * mSizeBlock, numBlockY * mSizeBlock);
                numBlock++;
            }
            numBlock += (mNbBlockWidth - mNbBlockScreenWidth);
        }
        //std::cout <<  mNbVertices << std::endl;
    }

    QSetIterator<quint16> i(mRefreshId);
    while (i.hasNext())
    {
        unsigned short rid = i.next();
        int numBlock = mBoundsProvince[rid].left() +  mBoundsProvince[rid].top() * mNbBlockWidth;

        for (int numBlockY = mBoundsProvince[rid].top() - mTopBlock; numBlockY <= mBoundsProvince[rid].bottom() - mTopBlock; numBlockY++)
        {
            for (int numBlockX = mBoundsProvince[rid].left() - mLeftBlock; numBlockX <= mBoundsProvince[rid].right() - mLeftBlock; numBlockX++)
            {
                drawBlock(numBlock, numBlockX * mSizeBlock, numBlockY * mSizeBlock);
                numBlock++;
            }
            numBlock += (mNbBlockWidth - (mBoundsProvince[rid].right() - mBoundsProvince[rid].left() + 1));
        }
    }
    mRefreshId.clear();
    drawVertices();
    saveMap();
    mWindow->resetOpenGLState();

    mNext = None;
    mWaitForMove = false;
    return (true);
}

void Map::drawVertices()
{
    mProgram->bind();
    mProgram->enableAttributeArray(0);
    mProgram->enableAttributeArray(1);

    mProgram->setUniformValue("matrix", mMatrix);

    mProgram->setAttributeArray(0, GL_FLOAT, &mQuadVertices[0], 2);
    mProgram->setAttributeArray(1, GL_FLOAT, &mQuadColors[0], 3);
    glDrawArrays(GL_TRIANGLES, 0, mQuadVertices.size()/2);

    mProgram->disableAttributeArray(0);
    mProgram->disableAttributeArray(1);
    mProgram->release();
    return;
}

void Map::saveMap()
{
    QOpenGLFramebufferObject::blitFramebuffer(mFbo, 0, GL_COLOR_BUFFER_BIT, GL_NEAREST);
    return;
}

void Map::drawBlock(int numBlock, int screenX, int screenY)
{
    int stripe =  (numBlock/mNbBlockWidth)%2;
    std::list<Light>::iterator idInBlock;
    for (idInBlock = mBlock[numBlock].begin() ; idInBlock != mBlock[numBlock].end(); idInBlock++ )
    {
        int posTree = 0;
        int posBit = 7;
        int posLeafGray = 0;
        inspectBlock(*idInBlock, screenX, screenY, posTree, posBit, mLevelInit, posLeafGray, stripe);
    }
    return;
}

void Map::inspectBlock(Light & idInBlock, int screenX, int screenY, int & posTree, int & posBit, int level, int & posLeafGray, int stripe)
{
    int colorIndex;
    for(std::vector<int>::size_type i = 0; i != mShadingColorIndex.size(); i++) {
        if (mShadingColorIndex[i] == mProColor.at(idInBlock.id)[stripe])
        {
            colorIndex = i;
            break;
        }
    }
    for (int posInQuad = 0; posInQuad < 4; posInQuad++)
    {
        if ((level == mLevelInit) && (posInQuad > 0)) break;
        if (nextBitFromTree(idInBlock, posTree, posBit) == 0)
        {
            if (nextBitFromTree(idInBlock, posTree, posBit) == 1)
            {
                QColor color = getColor(idInBlock, posLeafGray, colorIndex);
                drawQuad(screenX + mPosInQuad[posInQuad].x() * p2[level], screenY + mPosInQuad[posInQuad].y() * p2[level], p2[level], color);
            }
        }
        else
        {
            if (level == 1)
            {
                if (nextBitFromTree(idInBlock, posTree, posBit) == 1)
                {
                    QColor color = getColor(idInBlock, posLeafGray, colorIndex);
                    drawPoint(screenX + mPosInQuad[posInQuad].x() * 2, screenY + mPosInQuad[posInQuad].y() * 2, color);
                }

                if (nextBitFromTree(idInBlock, posTree, posBit) == 1)
                {
                    QColor color = getColor(idInBlock, posLeafGray, colorIndex);
                    drawPoint(screenX + mPosInQuad[posInQuad].x() * 2 + 1, screenY + mPosInQuad[posInQuad].y() * 2, color);
                }

                if (nextBitFromTree(idInBlock, posTree, posBit) == 1)
                {
                    QColor color = getColor(idInBlock, posLeafGray, colorIndex);
                    drawPoint(screenX + mPosInQuad[posInQuad].x() * 2 + 1, screenY + mPosInQuad[posInQuad].y() * 2 + 1, color);
                }

                if (nextBitFromTree(idInBlock, posTree, posBit) == 1)
                {
                    QColor color = getColor(idInBlock, posLeafGray, colorIndex);
                    drawPoint(screenX + mPosInQuad[posInQuad].x() * 2, screenY + mPosInQuad[posInQuad].y() * 2 + 1, color);
                }
            }
            else
            {
                inspectBlock(idInBlock, screenX + mPosInQuad[posInQuad].x() * p2[level], screenY + mPosInQuad[posInQuad].y() * p2[level], posTree, posBit, level-1, posLeafGray, stripe);
            }
        }
    }
    return;
}

QColor Map::getColor(Light & idInBlock, int & posLeafGray, int colorIndex)
{
    unsigned char leafGray = nextLeafGray(idInBlock, posLeafGray);
    QColor color;
    if (!mDebug)
    {
        if (!(leafGray & (1 << 6)))
        {
            if (mSelectedId == idInBlock.id)
                color = mShadingColor[colorIndex].second[leafGray & 63];
            else
                color = mShadingColor[colorIndex].first[leafGray & 63];
        }
        else
        {
            color = mShadingColor[mColorRiver].first[leafGray & 63];
        }
    }
    else color = mShadingColor[0].first[leafGray & 63];

    return (color);
}

int Map::nextBitFromTree(Light & idInBlock, int & posTree, int & posBit)
{
    int k = ((idInBlock.tree[posTree] & (1 << posBit)) >> posBit);
    posBit--;
    if (posBit < 0)
    {
        posTree++;
        posBit = 7;
    }
    return (k);
}

unsigned char Map::nextLeafGray(Light & idInBlock, int & posLeafGray)
{
    unsigned char leafGray = idInBlock.leafGray[posLeafGray];
    posLeafGray++;
    return (leafGray);
}

inline void Map::drawQuad(int left, int top, int size, QColor color)
{
    mNbVertices = mNbVertices + 2;
    mQuadVertices.push_back(float(left));
    mQuadVertices.push_back(float(top));
    mQuadVertices.push_back(float(left + size));
    mQuadVertices.push_back(float(top));
    mQuadVertices.push_back(float(left));
    mQuadVertices.push_back(float(top + size));
    mQuadVertices.push_back(float(left + size));
    mQuadVertices.push_back(float(top));
    mQuadVertices.push_back(float(left));
    mQuadVertices.push_back(float(top + size));
    mQuadVertices.push_back(float(left + size));
    mQuadVertices.push_back(float(top + size));
    mQuadColors.push_back(float(color.red()/255.0));
    mQuadColors.push_back(float(color.green()/255.0));
    mQuadColors.push_back(float(color.blue()/255.0));
    mQuadColors.push_back(float(color.red()/255.0));
    mQuadColors.push_back(float(color.green()/255.0));
    mQuadColors.push_back(float(color.blue()/255.0));
    mQuadColors.push_back(float(color.red()/255.0));
    mQuadColors.push_back(float(color.green()/255.0));
    mQuadColors.push_back(float(color.blue()/255.0));
    mQuadColors.push_back(float(color.red()/255.0));
    mQuadColors.push_back(float(color.green()/255.0));
    mQuadColors.push_back(float(color.blue()/255.0));
    mQuadColors.push_back(float(color.red()/255.0));
    mQuadColors.push_back(float(color.green()/255.0));
    mQuadColors.push_back(float(color.blue()/255.0));
    mQuadColors.push_back(float(color.red()/255.0));
    mQuadColors.push_back(float(color.green()/255.0));
    mQuadColors.push_back(float(color.blue()/255.0));
}

inline void Map::drawPoint(int left, int top, QColor color)
{
    mNbVertices = mNbVertices + 1;
    mQuadVertices.push_back(float(left));
    mQuadVertices.push_back(float(top));
    mQuadVertices.push_back(float(left + 2));
    mQuadVertices.push_back(float(top));
    mQuadVertices.push_back(float(left));
    mQuadVertices.push_back(float(top + 2));
    mQuadColors.push_back(float(color.red()/255.0));
    mQuadColors.push_back(float(color.green()/255.0));
    mQuadColors.push_back(float(color.blue()/255.0));
    mQuadColors.push_back(float(color.red()/255.0));
    mQuadColors.push_back(float(color.green()/255.0));
    mQuadColors.push_back(float(color.blue()/255.0));
    mQuadColors.push_back(float(color.red()/255.0));
    mQuadColors.push_back(float(color.green()/255.0));
    mQuadColors.push_back(float(color.blue()/255.0));
}

unsigned short Map::hitID(unsigned short x, unsigned short y)
{
    x += mLeft;
    y += mTop;
    std::map<unsigned short, unsigned short>::iterator it;
    for (it=mHit[x].begin(); it!=mHit[x].end(); ++it)
        if (y <= it->first)
            return (it->second);
    return(0);
}

QVariant Map::selectID(unsigned short x, unsigned short y)
{
    x += mLeft;
    y += mTop;
    std::map<unsigned short, unsigned short>::iterator it;
    for (it=mHit[x].begin(); it!=mHit[x].end(); ++it)
        if (y <= it->first)
        {
            mRefreshId.insert(mSelectedId);
            mSelectedId = it->second;
            mRefreshId.insert(mSelectedId);
            return (QVariant(it->second));
        }
    return(QVariant(0));
}

void Map::unSelectID()
{
    mRefreshId.insert(mSelectedId);
    mSelectedId = 0;
}

void Map::calculateShading(int levelInf, int levelSup, QColor col0, QColor col1, int level0, int level1, ColorShading& cs, ColorShading& cs1)
{
    for (int level = levelInf; level < levelSup; level++)
    {
       int rr = (col1.red()-col0.red()) / ((float)level1 - (float)level0) * level + (col0.red() * level1 - col1.red() * level0) / (level1 - level0);
       int gg = (col1.green()-col0.green()) / ((float)level1 - (float)level0) * level + (col0.green() * level1 - col1.green() * level0) / (level1 - level0);
       int bb = (col1.blue()-col0.blue()) / ((float)level1 - (float)level0) * level + (col0.blue() * level1 - col1.blue() * level0) / (level1 - level0);
       cs[level].setRgb(rr, gg, bb);
       cs1[level].setRgb((rr - 50) < 0 ? 0 : (rr - 50), (gg - 50) < 0 ? 0 : (gg - 50), (bb - 50) < 0 ? 0 : (bb - 50));
    }

}

bool Map::initShadingColor(std::string fileName)
{
    ColorShading cs;
    ColorShading cs1;
    QString fn(fileName.c_str());
    QFile file(fn);
    QString::SectionFlag flag = QString::SectionSkipEmpty;
    QRegularExpression re("\[A-z]+");
    QRegularExpression re2("\\d+,\\d+,\\d+,\\d+");
    QString color;

    if (file.open(QFile::ReadOnly | QIODevice::Text))
    {
        QTextStream buf(&file);
        int numColor = -1;
        bool startNewColor = false;
        while(!buf.atEnd())
        {
            QString line = buf.readLine();
            if (line.contains(re)) //new color
            {
                if (numColor >= 0)
                {
                    mShadingColor.push_back(std::pair<ColorShading, ColorShading>(cs, cs1));
                    mShadingColorIndex.push_back(color);
                }
                color = line;
                numColor++;
                startNewColor = true;
            }
            else if (line.contains(re2))
            {
                int level0 = 0;
                QColor col0;
                if (startNewColor)
                {
                    level0 = line.section(',', 0, 0, flag).toInt();
                    col0.setRed(line.section(',', 1, 1, flag).toInt());
                    col0.setGreen(line.section(',', 2, 2, flag).toInt());
                    col0.setBlue(line.section(',', 3, 3, flag).toInt());
                }
                startNewColor = false;
                int level1 = line.section(',', 0, 0, flag).toInt();
                int r = line.section(',', 1, 1, flag).toInt();
                int g = line.section(',', 2, 2, flag).toInt();
                int b = line.section(',', 3, 3, flag).toInt();
                QColor col1(r, g, b);

                calculateShading(level0, level1, col0, col1, level0, level1, cs, cs1);

                level0 = level1;
                col0 = col1;

            }

        }
        mShadingColor.push_back(std::pair<ColorShading, ColorShading>(cs, cs1));
        mShadingColorIndex.push_back(color);
    }

    file.close();

    return (true);
}

std::vector<unsigned short> Map::returnValidIdMap(std::string sDir)
{
    std::vector<unsigned short> idMapLocal;

    QDir dir(QString::fromStdString(sDir));
    if (!dir.exists())
    {
        std::cerr << "Cannot find " << sDir << std::endl;
    }
    QStringList filters;
    filters << "*.bin";
    dir.setNameFilters(filters);
    QStringList list(dir.entryList(QDir::Files|QDir::NoDotAndDotDot));

    struct ValidIdMap
    {
        bool light = false;
        bool hit = false;
        bool bound = false;
    };
    std::vector<ValidIdMap> valIdMap(65536);

    while (!list.isEmpty())
    {
        QString file = list.takeFirst();
        QRegExp rxlen("(light|hit|bound)(\\d+)");
        int pos = rxlen.indexIn(file);
        if (pos > -1) {
            if (rxlen.cap(1)=="light")
            {
                valIdMap[rxlen.cap(2).toUShort()].light = true;
            }
            else if (rxlen.cap(1)=="hit")
            {
                valIdMap[rxlen.cap(2).toUShort()].hit = true;
            }
            else if (rxlen.cap(1)=="bound")
            {
                valIdMap[rxlen.cap(2).toUShort()].bound = true;
            }
        }
    }

    for (unsigned int i = 0; i < valIdMap.size(); i++)
    {
        if ((valIdMap[i].light == true) && (valIdMap[i].hit == true) && (valIdMap[i].bound == true))
        {
            idMapLocal.push_back(i);
        }
    }
    return (idMapLocal);
}

bool Map::addLightId(unsigned short id, std::string dir)
{
    std::ostringstream fileName;
    fileName << dir <<  "light" << id << ".bin";
    std::ifstream file(fileName.str().c_str(), std::ios::in | std::ios::binary);
    if (file.is_open())
    {
        while (true)
        {
            unsigned int numBlock, sizeTree, sizeLeafGray, sizeNearId;
            file.read ((char *)&numBlock, sizeof(int));
            if (file.eof()) break;
            file.read ((char *)&sizeTree, sizeof(int));
            file.read ((char *)&sizeLeafGray, sizeof(int));
            file.read ((char *)&sizeNearId, sizeof(int));

            Light light;
            light.id = id;
            light.tree.resize(sizeTree);
            light.leafGray.resize(sizeLeafGray);
            light.nearId.resize(sizeNearId);

            for (unsigned int i=0; i<sizeTree; ++i)
                file.read ((char *)&light.tree[i], sizeof(char));

            for (unsigned int i=0; i<sizeLeafGray; ++i)
                file.read ((char *)&light.leafGray[i], sizeof(char));

            for (unsigned int i=0; i<sizeNearId; ++i)
                file.read ((char *)&light.nearId[i], sizeof(short));

            mBlock[numBlock].push_back(light);
        }
    }
    else
    {
        std::cerr << "Cannot find " << fileName.str() << std::endl;
        return (false);
    }
    file.close();
    return (true);
}

bool Map::readConfigMap(std::string dir)
{
    std::ostringstream fileName;
    fileName << dir <<  "config.bin";
    std::ifstream file(fileName.str().c_str(), std::ios::in | std::ios::binary);
    if (file.is_open())
    {
        unsigned short sizeBlock, nbBlockWidth, nbBlockHeight, circum;
        file.read ((char *)&sizeBlock, sizeof(short));
        file.read ((char *)&nbBlockWidth, sizeof(short));
        file.read ((char *)&nbBlockHeight, sizeof(short));
        file.read ((char *)&circum, sizeof(short));

        mSizeBlock = (int) sizeBlock;
        mNbBlockWidth = (int) nbBlockWidth;
        mNbBlockHeight = (int) nbBlockHeight;
        if (circum == 1)
            mCircum = true;
        else
            mCircum = false;
    }
    else
    {
        std::cerr << "Cannot find " << fileName.str() << std::endl;
        return (false);
    }

    file.close();
    return (true);
}

bool Map::addHitId(unsigned short id, std::string dir)
{
    std::ostringstream fileName;
    fileName << dir <<  "hit" << id << ".bin";
    std::ifstream file(fileName.str().c_str(), std::ios::in | std::ios::binary);
    if (file.is_open())
    {
        while(true)
        {
            unsigned short posX, begPosY, endPosY;
            file.read ((char *)&posX, sizeof(short));
            file.read ((char *)&begPosY, sizeof(short));
            file.read ((char *)&endPosY, sizeof(short));
            if (file.eof()) break;
            if (begPosY > 0)
                if (mHit[posX].count(begPosY - 1) == 0)
                    mHit[posX][begPosY - 1] = 0;
            mHit[posX][endPosY] = id;
        }
    }
    else
    {
        std::cerr << "Cannot find " << fileName.str() << std::endl;
        return (false);
    }
    file.close();
    return (true);
}

bool Map::addBoundsId(unsigned short id, std::string dir)
{
    std::ostringstream fileName;
    fileName << dir <<  "bound" << id << ".bin";
    std::ifstream file(fileName.str().c_str(), std::ios::in | std::ios::binary);
    if (file.is_open())
    {
        unsigned short left, right, top, bottom;
        file.read ((char *)&left, sizeof(short));
        file.read ((char *)&right, sizeof(short));
        file.read ((char *)&top, sizeof(short));
        file.read ((char *)&bottom, sizeof(short));

        QRect rect;
        rect.setCoords(left, top, right, bottom);

        QRect rect0(0,0,0,0);

        while (mBoundsProvince.size() < id)
        {
            mBoundsProvince.push_back(rect0);
        }
        mBoundsProvince.push_back(rect);
    }
    else
    {
        std::cerr << "Cannot find " << fileName.str() << std::endl;
        return (false);
    }

    file.close();
    return (true);
}
