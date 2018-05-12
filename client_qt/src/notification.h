#ifndef NOTIFICATION_H
#define NOTIFICATION_H

#include <QObject>

class Notifications : public QObject
{
    Q_OBJECT
public:
    Notifications();
    
signals:
    void newMessage();
    void provinceModelChanged();
    void modelChanged();

public slots:
    void receiveNewMessage();
    void slotProvinceModelChanged();
    void slotModelChanged();
};

#endif // NOTIFICATION_H
