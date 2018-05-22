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

#ifndef MAP_H
#define MAP_H
#include <list>
#include <vector>
#include <forward_list>
#include <array>
#include <algorithm>
#include <iterator>
#include <string>
#include <QtQuick/QQuickItem>
#include <QtQuick/qquickwindow.h>
#include <QtGui/QOpenGLFramebufferObject>
#include <QtGui/QOpenGLShaderProgram>
#include <QColor>
#include <QPair>
//#include <QQuickItem>
#include <QOpenGLFunctions>
#include <QNetworkAccessManager>



class Map : public QQuickItem, protected QOpenGLFunctions
{
    Q_OBJECT
    Q_PROPERTY(QString stripe0 READ stripe0 WRITE setStripe0 NOTIFY stripe0Changed)
    Q_PROPERTY(QString stripe1 READ stripe1 WRITE setStripe1 NOTIFY stripe1Changed)
    //Q_PROPERTY(quint16 numberVisibleProvince READ numberVisibleProvince)
    //Q_PROPERTY(QList<QVariant> visibleProvince READ visibleProvince NOTIFY visibleProvinceChanged)
    Q_PROPERTY(qreal t READ t WRITE setT NOTIFY tChanged)
    Q_PROPERTY(int top READ top NOTIFY moved)
    Q_PROPERTY(int left READ left NOTIFY moved)
    Q_PROPERTY(int topLeftBlock READ topLeftBlock WRITE setTopLeftBlock)

public:
    Map();
    ~Map();
    Q_ENUMS(EnumDirection)
    enum EnumDirection {
        All,
        OnTopLeft,
        OnTopRight,
        OnBottomLeft,
        OnBottomRight,
        OnLeft,
        OnRight,
        OnTop,
        OnBottom,
        None };

    QString stripe0() const { return mStripe0; }
    void setStripe0(QString stripe);
    QString stripe1() const { return mStripe1; }
    void setStripe1(QString stripe);
    qreal t() const { return mT; }
    void setT(qreal t);
    int top() const { return mTop; }
    int left() const { return mLeft; }
    int topLeftBlock() const { return mTopLeftBlock;}
    void setTopLeftBlock(int topLeftBlock) {mTopLeftBlock = topLeftBlock; calculateCoordinate();}
    //quint16 numberVisibleProvince() const { return mNumberVisibleProvince; }
    Q_INVOKABLE void move(EnumDirection d);
    Q_INVOKABLE unsigned short hitID(unsigned short x, unsigned short y);
    Q_INVOKABLE QVariant selectID(unsigned short x, unsigned short y);
    Q_INVOKABLE void unSelectID();
    void init(unsigned int width, unsigned int height, QUrl url, bool debug, QString player);
    void resize(QSize size, QSize oldSize);


signals:
    void stripe0Changed();
    void stripe1Changed();
    void urlChanged();
    void tChanged();
    void moved();
    void visibleProvinceChanged(QSet<quint16> provinceAdded);
    void provinceModelChanged(QList<QVariant> visibleProvinceChanged);
    void armyModelChanged(QList<QVariant> armyChanged);

public slots:
    void doJobBeforeRendering();
    //void update();


private slots:
    void writeFps();
    void slotProvinceUpdateReply(QNetworkReply* reply);

private:
    //members
    int mNbVertices;
    QString mStripe0;
    QString mStripe1;
    QString mPlayer;
    qreal mT;
    int mWidth, mHeight;
    int mTopLeftBlock;
    int mTopBlock;
    int mLeftBlock;
    int mTop;
    int mLeft;
    int mSizeBorder;
    bool mCircum;
    int mColorRiver;
    QRect mScreen;
    QRect mBlockScreen;
    QOpenGLShaderProgram *mProgram;
    QMatrix4x4 mMatrix;
    QUrl mUrl;
    bool mDebug;
    QQuickWindow *mWindow;

    QSet<quint16> mVisibleProvince;
    quint16 mNumberVisibleProvince;


    struct Light {
        unsigned short id;
        std::vector<unsigned char> tree;
        std::vector<unsigned char> leafGray;
        std::vector<unsigned short> nearId;
    };
    std::vector<std::list<Light> > mBlock;

    std::vector<std::map<unsigned short, unsigned short> > mHit;
    unsigned short mSelectedId;

    std::vector<QRect> mBoundsProvince;

    std::vector<QPoint> mPosInQuad;

    int mNbBlockHeight, mNbBlockWidth, mSizeBlock, mNbBlockScreenWidth, mNbBlockScreenHeight, mLevelInit, mMaxId;
    bool mWholeWidthBlock, mWholeHeightBlock;

    std::vector<int>p2;
    bool mInitGL;
    bool mInit;
    QOpenGLFramebufferObject *mFbo = NULL;
    std::vector<float> mQuadVertices;
    std::vector<float> mQuadColors;

    typedef std::array<QColor, 64> ColorShading;

    std::vector<std::pair<ColorShading, ColorShading> > mShadingColor;
    std::vector<QString> mShadingColorIndex;
    //Model::ProvinceAttribute* mFillProvinceAttribute = NULL;
    //Model::ArrayAttributeVal* mColorFillArrayAttribute = NULL;
    EnumDirection mNext;
    bool mWaitForMove;
    //std::list<unsigned short> mRefreshId;
    QSet<quint16> mRefreshId;
    int mFrame = 0;
    QNetworkAccessManager *mManager = NULL;
    std::vector<QString> mProText;
    std::vector<QList<QString>> mProColor;



    //functions
    bool initGL();
    void initSize(unsigned int width, unsigned int height);
    std::vector<unsigned short> returnValidIdMap(std::string);
    bool addLightId(unsigned short id, std::string dir);
    bool addBoundsId(unsigned short id, std::string dir);
    bool addHitId(unsigned short id, std::string dir);
    bool readConfigMap(std::string dir);
    bool listVisibleProvince();
    bool drawMap();
    void drawVertices();
    void drawBlock(int, int, int);
    QColor getColor(Light & idInBlock, int & posLeafGray, int colorIndex);
    int nextBitFromTree(Light &, int &, int &);
    unsigned char nextLeafGray(Light &, int &);
    void inspectBlock(Light &, int, int, int &, int &, int, int &, int);
    void inspectJson(int indexAttibute, QJsonObject obj, int id, QStringList stripe, int indexStripe);
    inline void drawQuad(int, int, int, QColor);
    inline void drawPoint(int, int, QColor);
    void saveMap();
    bool initShadingColor(std::string fileName);
    void calculateShading(int levelInf, int levelSup, QColor col0, QColor col1, int level0, int level1, ColorShading& cs, ColorShading& cs1);
    void changeTopLeftBlock(int interval);
    void calculateCoordinate();
    void updateDataProvince();
    void handleWindowChanged(QQuickWindow *win);
};

#endif // MAP_H
