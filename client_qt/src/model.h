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

#ifndef MODEL_H
#define MODEL_H
#include <forward_list>
#include <list>
#include <vector>
#include <map>
#include <array>
#include <unordered_map>
#include <string>
#include <mutex>
#include <QtNetwork>
#include <bitset>


typedef QSet<quint16> QSet16;



class Model : public QThread
//class Model : public QObject

{

    Q_OBJECT

public:
    Model(QString ipServer, quint16 portServer, quint16 controlled);
    ~Model();

    void run();
    bool isInit();
    //quint16 mMaxID;

    /*typedef quint16 AttributeOneVal;
    typedef std::pair<quint32, quint16> AttributeOneObject;

    typedef std::forward_list<quint16> AttributeListVal;
    typedef std::pair<quint32, std::forward_list<quint16> > AttributeListObject;*/

    typedef std::map<quint16, QString> NameElementArray;

    typedef std::map<quint16, QList<quint16> > ArrayAttributeVal;
    typedef std::pair <quint32, ArrayAttributeVal> ArrayAttribute;

    typedef std::array<QList<quint16>, 65536> ProvinceAttributeVal;
    typedef std::pair <quint32, ProvinceAttributeVal> ProvinceAttribute;


    //methods
    ProvinceAttribute* getProvincesAttribute(quint32 hash);
    ArrayAttributeVal* getArrayAttributeVal(quint64 hash);
    Q_INVOKABLE QList<QVariant> get(quint32 hashCls, quint16 id, quint32 hashAttribute, bool withRef=true);
    Q_INVOKABLE QList<QVariant> get(QString cls, quint16 id, QString attribute, bool withRef=true);
    Q_INVOKABLE QList<QVariant> get(quint32 hashCls, quint16 id, QString attribute, bool withRef=true);

    Q_INVOKABLE QList<QVariant> getAll(quint32 hashCls, quint32 hashAttribute, bool onlyId=false);
    Q_INVOKABLE QList<QVariant> getAll(QString cls, QString attribute, bool onlyId=false);
    Q_INVOKABLE QList<QVariant> getAll(quint32 hashCls, QString attribute, bool onlyId=false);

    Q_INVOKABLE QVariant getName(quint32 hashCls, quint16 id);
    Q_INVOKABLE QVariant getName(QString cls, quint16 id);

    Q_INVOKABLE quint16 controlled();

    Q_INVOKABLE void lock();
    Q_INVOKABLE void unlock();

    Q_INVOKABLE void sendMessage(QList<QVariant> message);
    Q_INVOKABLE QList<QVariant> getLastMessage();

    void changeHashFill(quint32 hashFill) {mHashFill = hashFill;}

signals:
    void provinceModelChanged(QSet16 provinceChanged);
    void provinceFillModelChanged(QSet16 provinceChanged);
    void armyModelChanged(QSet16 armyChanged);
    void modelChanged();
    void newMessage();


private slots:
    void receiveData();


private:
    void changeModel(QDataStream &);
    void receiveMessage(QDataStream &);
    ArrayAttributeVal getData (QDataStream & in, ArrayAttributeVal aa, std::bitset<8> typeInfo, bool army, QSet16& armyChanged);
    ProvinceAttributeVal getData (QDataStream & in, quint32 hashAttribute, ProvinceAttributeVal aa, std::bitset<8> typeInfo, QSet16& provinceChanged, QSet16& provinceFillChanged);

    /*std::map<quint64, AttributeOneVal> mAttributeOneVal;
    std::mutex mMutexAttributeOneVal;
    std::map<quint64, AttributeOneObject> mAttributeOneObject;
    std::mutex mMutexAttributeOneObject;

    std::map<quint64, AttributeListVal> mAttributeListVal;
    std::mutex mMutexAttributeListVal;
    std::map<quint64, AttributeListObject> mAttributeListObject;
    std::mutex mMutexAttributeListObject;*/

    std::map<quint32, NameElementArray> mNameElementArray;
    //std::mutex mMutexNameElementArray;

    //std::map<quint64, ArrayAttributeVal> mArrayAttributeVal;
    //std::mutex mMutexArrayAttributeVal;
    std::map<quint64, ArrayAttribute> mArrayAttribute;
    //std::mutex mMutexArrayAttribute;

    //std::map<quint32, ProvinceAttributeVal> mProvinceAttributeVal;
    //std::mutex mMutexProvinceAttributeVal;
    std::map<quint32, ProvinceAttribute> mProvinceAttribute;
    //std::mutex mMutexProvinceAttribute;
    std::mutex mMutex;

    QTcpServer *mTcpServer;
    QByteArray mData;
    QTcpSocket *mTcpSocket;
    QString mIpServer;
    quint16 mPortServer, mControlled;

    quint32 mHashProvince, mHashArmy, mHashFill;

    QList<QList<QVariant> > mMessage;



    bool mInit;
};

#endif // MODEL_H
