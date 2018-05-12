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

#include "model.h"
#include <iostream>
#include "message.h"
#include <stdexcept>

#include "define.h"

Model::Model(QString ipServer, quint16 portServer, quint16 controlled)
{
    mHashProvince = hashStr(QString("Province"));
    mHashArmy = hashStr(QString("Army"));
    mInit = false;
    mIpServer = ipServer;
    mPortServer = portServer;
    mControlled = controlled;
}

Model::~Model()
{
    Message message;
    message << quint16(2) << mTcpServer->serverPort(); //player quit
    message.sendTo(mIpServer, mPortServer);

    mTcpServer->close();
    delete mTcpServer;
}

bool Model::isInit()
{
    return(mInit);
}

quint16 Model::controlled()
{
    return(mControlled);
}

void Model::run()
{
    mTcpServer = new QTcpServer();
    if (!mTcpServer->listen())//QHostAddress("127.0.0.1")*/QHostAddress::Any, 4001))
    {
        std::cout << "Unable to start the server: " << mTcpServer->errorString().toStdString() << std::endl;
        //close();
    }
    else
    {
        connect(mTcpServer, &QTcpServer::newConnection, this, &Model::receiveData);
    }

    Message message;
    message << quint16(1) << mTcpServer->serverPort() << mControlled; //LoadAllData
    message.sendTo(mIpServer, mPortServer);
    exec();
}

void Model::sendMessage(QList<QVariant> mess)
{
    Message message;
    QListIterator<QVariant> i(mess);
    while (i.hasNext())
        message << (quint16) i.next().toInt();
    message.sendTo(mIpServer, mPortServer);
    return;
}


void Model::receiveData()
{
    mTcpSocket = new QTcpSocket;
    mTcpSocket = mTcpServer->nextPendingConnection();

    const int Timeout = 10000;


    while (mTcpSocket->bytesAvailable() < (int)sizeof(quint32)) {
        if (!mTcpSocket->waitForReadyRead(Timeout)) {
            return;
        }
    }

    QDataStream in(mTcpSocket);
    quint32 blockSize;
    in >> blockSize;

    while (mTcpSocket->bytesAvailable() < (blockSize))
    {
        if (!mTcpSocket->waitForReadyRead(Timeout)) {
            return;
        }
    }

    mTcpSocket->disconnectFromHost();

    quint32 typeMessage;
    in >> typeMessage;

    if (typeMessage == 0) //data
        changeModel(in);
    else if (typeMessage >= 1) //message
        receiveMessage(in);

    delete mTcpSocket;
    return;
}

void Model::receiveMessage(QDataStream & in)
{
    QList<QVariant> vlist;
    while (in.status() == 0)
    {
        quint16 m;
        in >> m;
        vlist.push_back(m);
    }
    vlist.pop_back();
    mMessage.push_front(vlist);
    emit newMessage();
    return;
}

QList<QVariant> Model::getLastMessage()
{
    if (!mMessage.empty())
        return(mMessage.first());
    else
        return(QList<QVariant>());
}


Model::ProvinceAttribute* Model::getProvincesAttribute(quint32 hash)
{
    ProvinceAttribute* pao = NULL;
    mMutex.lock();
    //mMutexProvinceAttribute.lock();
    pao = &mProvinceAttribute[hash];
    mMutex.unlock();
    //mMutexProvinceAttribute.unlock();
    return (pao);
}

Model::ArrayAttributeVal* Model::getArrayAttributeVal(quint64 hash)
{
    ArrayAttributeVal* aav = NULL;
    //mMutexArrayAttribute.lock();
    mMutex.lock();
    aav = &mArrayAttribute[hash].second;
    mMutex.unlock();
    //mMutexArrayAttribute.unlock();
    return (aav);
}

void Model::lock()
{
    mMutex.lock();
    return;
}

void Model::unlock()
{
    mMutex.unlock();
    return;
}

QVariant Model::getName(quint32 hashCls, quint16 id)
{
    return (QVariant(mNameElementArray[hashCls][id]));
}

QVariant Model::getName(QString cls, quint16 id)
{
    return (getName(hashStr(cls), id));
}

QList<QVariant> Model::get(quint32 hashCls, quint16 id, quint32 hashAttribute, bool withRef)
{
    QList<quint16> list;
    quint16 hashObjectAttribute = 0;

    if (hashCls == mHashProvince)
    {
        list = mProvinceAttribute[hashAttribute].second[id];
        hashObjectAttribute = mProvinceAttribute[hashAttribute].first;
    }
    else
    {
        quint64 hca = hashClassAttribute(hashCls, hashAttribute);
        //list = mArrayAttribute[hca].second[id];
        try{
            list = mArrayAttribute[hca].second.at(id);
        }
        catch (const std::out_of_range){
            list.append(0);
        }

        hashObjectAttribute = mArrayAttribute[hca].first;
    }

    QList<QVariant> vlist;
    if (withRef)
        vlist.push_back(hashObjectAttribute);
    for (int i = 0; i < list.size(); ++i)
        vlist.push_back(list.at(i));

    return (vlist);
}

QList<QVariant> Model::get(quint32 hashCls, quint16 id, QString attribute, bool withRef)
{
    return (get(hashCls, id, hashStr(attribute), withRef));
}


QList<QVariant> Model::get(QString cls, quint16 id, QString attribute, bool withRef)
{
    return (get(hashStr(cls), id, hashStr(attribute), withRef));
}

QList<QVariant> Model::getAll(quint32 hashCls, quint32 hashAttribute, bool onlyId)
{
    /*QList<quint16> list;
    quint16 hashObjectAttribute = 0;

    if (hashCls != mHashProvince)
    {
        quint64 hca = hashClassAttribute(hashCls, hashAttribute);
        //mMutexArrayAttribute.lock();
        for (ArrayAttributeVal::iterator it=mArrayAttribute[hca].second.begin(); it!=mArrayAttribute[hca].second.end(); ++it)
        {
            list << it->first;
            if (!onlyId)
            {
                list << (quint16) it->second.size();
                list << it->second;
            }
        }
        hashObjectAttribute = mArrayAttribute[hca].first;
        //mMutexArrayAttribute.unlock();
    }*/

    QList<QVariant> vlist;
    quint64 hca = hashClassAttribute(hashCls, hashAttribute);
    if (!onlyId)
        vlist.push_back(mArrayAttribute[hca].first);
    for (ArrayAttributeVal::iterator it=mArrayAttribute[hca].second.begin(); it!=mArrayAttribute[hca].second.end(); ++it)
    {
        vlist.push_back(it->first);
        if (!onlyId)
        {
            vlist.push_back((quint16) it->second.size());
            QListIterator<quint16> i(it->second);
            while (i.hasNext())
                vlist << i.next();
        }
    }
    /*vlist.push_back(hashObjectAttribute);
    for (int i = 0; i < list.size(); ++i)
        vlist.push_back(list.at(i));*/

    return (vlist);
}

QList<QVariant> Model::getAll(quint32 hashCls, QString attribute, bool onlyId)
{
    return (getAll(hashCls, hashStr(attribute), onlyId));
}

QList<QVariant> Model::getAll(QString cls, QString attribute, bool onlyId)
{
    return (getAll(hashStr(cls), hashStr(attribute), onlyId));
}


Model::ArrayAttributeVal Model::getData (QDataStream & in, Model::ArrayAttributeVal aa, std::bitset<8> typeInfo, bool army, QSet16& armyChanged)
{
    quint16 nbInst;
    in >> nbInst;
    for (quint16 i = 0; i < nbInst; ++i)
    {
        quint16 id;
        in >> id;

        quint16 nbVal = 1;
        if (typeInfo.test(1)) //some values
        {
            in >> nbVal;
        }

        QList<quint16> lval;
        for (quint16 j = 0; j < nbVal; ++j)
        {
            quint16 val;
            in >> val;
            lval.push_front(val);
        }
        aa[id] = lval;
        if (army)
            armyChanged.insert(id);
    }
    return (aa);
}

Model::ProvinceAttributeVal Model::getData (QDataStream & in, quint32 hashAttribute, Model::ProvinceAttributeVal aa, std::bitset<8> typeInfo, QSet16& provinceChanged, QSet16& provinceFillChanged)
{
    quint16 nbInst;
    in >> nbInst;
    for (quint16 i = 0; i < nbInst; ++i)
    {
        quint16 id;
        in >> id;

        quint16 nbVal = 1;
        if (typeInfo.test(1)) //some values
        {
            in >> nbVal;
        }

        QList<quint16> lval;
        for (quint16 j = 0; j < nbVal; ++j)
        {
            quint16 val;
            in >> val;
            lval.push_front(val);
        }
        aa[id] = lval;
        provinceChanged.insert(id);
        if (hashAttribute == mHashFill)
            provinceFillChanged.insert(id);
    }
    return (aa);
}



void Model::changeModel(QDataStream & in)
{
    //int a =2;
    QSet16 provinceChanged;
    QSet16 provinceFillChanged;
    QSet16 armyChanged;
    mMutex.lock();
    while (!in.atEnd())
    {
        quint8 ti;
        in >> ti;
        std::bitset<8> typeInfo(ti);

        if (typeInfo.test(4)) //deleteObject
        {
            quint32 hashClass;
            in >> hashClass;
            quint16 nbAttributes;
            in >> nbAttributes;
            for (quint16 i = 0; i < nbAttributes; i++)
            {
                quint32 hashAttribute;
                in >> hashAttribute;
                quint64 hca;
                hca = hashClassAttribute(hashClass, hashAttribute);

                quint16 nbObjects;
                in >> nbObjects;
                for (quint16 j = 0; j < nbObjects; j++)
                {
                    quint16 id;
                    in >> id;
                    mArrayAttribute[hca].second.erase(id);
                    if (hashClass == mHashArmy)
                        //if (!armyChanged.contains(id))
                            //armyChanged.append(id);
                        armyChanged.insert(id);
                }
            }
        }
        else if (typeInfo.test(3)) //name of a instance
        {
            quint32 hashClass;
            in >> hashClass;

            quint16 nbInstances;
            in >> nbInstances;

            NameElementArray nea;
            for (quint16 i = 0; i < nbInstances; i++)
            {
                quint16 id;
                in >> id;
                char* ch;
                in >> ch;
                QString str(ch);
                nea[id] = str;
            }
            //mMutexNameElementArray.lock();
            mNameElementArray[hashClass] = nea;
            //mMutexNameElementArray.unlock();
        }
        else
        {
            quint32 hashClass;
            in >> hashClass;

            quint32 hashAttribute;
            in >> hashAttribute;

            quint64 hca;
            hca = hashClassAttribute(hashClass, hashAttribute);



            /*if (false)
            {
                quint8 ca;
                in >> ca;
                mMutexMonoCarac.lock();
                mMonoCarac[hashAttributeClass] = ca;
                mMutexMonoCarac.unlock();
            }
            else if (false)
            {
                quint16 nbVal;
                in >> nbVal;
                MultiCarac liCa;
                for (quint16 i = 0; i < nbVal; ++i)
                {
                    quint16 val;
                    in >> val;
                    liCa.push_front(val);
                }
                mMutexMultiCarac.lock();
                mMultiCarac[hashAttributeClass] = liCa;
                mMutexMultiCarac.unlock();
            }*/
            if (hashClass != mHashProvince) //array of element
            {
                bool army = false;
                if (hashClass == mHashArmy)
                    army = true;

                if (!typeInfo.test(2)) // value(s)
                {
                    ArrayAttributeVal aav = getData (in, mArrayAttribute[hca].second, typeInfo, army, armyChanged);
                    ArrayAttribute aao(0, aav);
                    //mMutexArrayAttribute.lock();
                    mArrayAttribute[hca] = aao;
                    //mMutexArrayAttribute.unlock();
                }

                else if (typeInfo.test(2)) // object(s)
                {
                    quint32 adressHashTag;
                    in >> adressHashTag;
                    ArrayAttributeVal aav = getData (in, mArrayAttribute[hca].second, typeInfo, army, armyChanged);
                    ArrayAttribute aao(adressHashTag, aav);
                    //mMutexArrayAttribute.lock();
                    mArrayAttribute[hca] = aao;
                    //mMutexArrayAttribute.unlock();
                }
            }

            else //province's array of element
            {
                //quint16 id;
                if (!typeInfo.test(2)) // value(s)
                {
                    ProvinceAttributeVal pav = getData (in, hashAttribute, mProvinceAttribute[hashAttribute].second, typeInfo, provinceChanged, provinceFillChanged);
                    ProvinceAttribute pao(0, pav);
                    //mMutexProvinceAttribute.lock();
                    mProvinceAttribute[hashAttribute] = pao;
                    //mMutexProvinceAttribute.unlock();
                }

                else if (typeInfo.test(2)) // object(s)
                {
                    quint32 adressHashTag;
                    in >> adressHashTag;
                    ProvinceAttributeVal pav = getData (in, hashAttribute, mProvinceAttribute[hashAttribute].second, typeInfo, provinceChanged, provinceFillChanged);
                    ProvinceAttribute pao(adressHashTag, pav);
                    //mMutexProvinceAttribute.lock();
                    mProvinceAttribute[hashAttribute] = pao;
                    //mMutexProvinceAttribute.unlock();
                }
                /*provinceChanged.insert(id);
                if (hashAttribute == mHashFill)
                    provinceFillChanged.insert(id);*/
            }
        }
    }
    mMutex.unlock();
    mInit = true;

    if (!armyChanged.empty())
    {
        /*QList<QVariant> armyChangedVariant;
        for (int i = 0; i < armyChanged.size(); ++i)
            armyChangedVariant.append(armyChanged.at(i));
        emit armyModelChanged(armyChangedVariant);*/
        emit armyModelChanged(armyChanged);
    }

    if (!provinceChanged.empty())
    {
        /*QList<QVariant> provinceChangedVariant;
        for (int i = 0; i < provinceChanged.size(); ++i)
            provinceChangedVariant.append(provinceChanged.at(i));
        emit provinceModelChanged(provinceChangedVariant);*/
        emit provinceModelChanged(provinceChanged);
    }

    if (!provinceFillChanged.empty())
        emit provinceFillModelChanged(provinceFillChanged);

    /*quint64 h = hashClassAttribute(hashStr("Army"), hashStr("province"));
    if (mArrayAttribute[h].second[1].isEmpty())
        std::cout<< "vide" << std::endl;
    else
        //std::cout<< mArrayAttribute[h].second[1].front() << std::endl;*/
    emit modelChanged();
    return;
}
