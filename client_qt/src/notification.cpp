#include "notification.h"

Notifications::Notifications()
{
}

void Notifications::receiveNewMessage()
{
    emit newMessage();
}

void Notifications::slotProvinceModelChanged()
{
    emit provinceModelChanged();
}

void Notifications::slotModelChanged()
{
    emit modelChanged();
}
