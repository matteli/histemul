#-------------------------------------------------
#
# Project created by QtCreator 2012-10-24T15:03:26
#
#-------------------------------------------------

QT       += opengl
QT       += quick
QT       += gui
QT       += testlib
QT       += network



TARGET = histemul_client_qt
TEMPLATE = app
QMAKE_CXXFLAGS += -std=c++11

SOURCES += map.cpp \
    main.cpp \
    message.cpp \
    define.cpp \
    view.cpp \
    notification.cpp

lupdate_only{
SOURCES +=
}

HEADERS  += \
    map.h \
    define.h \
    message.h \
    view.h \
    notification.h

TRANSLATIONS = histemul_fr.ts

QML_IMPORT_PATH =


DISTFILES += \
    ui/Units.qml \
    ui/units.js \
    ui/AnimatedUnits.qml \
    ui/Notification.qml \
    ui/Cities.qml \
    ui/scripts/units.js \
    ui/scripts/text.js \
    ui/fixedSpriteMap.js \
    ui/constantMsg.js \
    ui/Window.qml \
    ui/IconButton.qml \
    configUi/components/Map.qml \
    ui/ui.qml \
    ui/request.js \
    ui/js/fixedSpriteMap.js \
    ui/js/request.js \
    ui/js/text.js \
    ui/js/units.js \
    ui/gfx/cities/catapult.png \
    ui/gfx/cities/euro_city_1.png \
    ui/gfx/cities/euro_city_2.png \
    ui/gfx/cities/euro_city_3.png \
    ui/gfx/cities/euro_city_4.png \
    ui/gfx/cities/fire.png \
    ui/gfx/flags/flag_A0.png \
    ui/gfx/flags/flag_England.png \
    ui/gfx/flags/flag_Exiled.png \
    ui/gfx/flags/flag_Ireland.png \
    ui/gfx/flags/flag_Scotland.png \
    ui/gfx/flags/flag_Wales.png \
    ui/gfx/gui/aban.png \
    ui/gfx/gui/aban_dis.png \
    ui/gfx/gui/background.png \
    ui/gfx/gui/ban.png \
    ui/gfx/gui/ban_dis.png \
    ui/gfx/gui/line.png \
    ui/gfx/gui/peace.png \
    ui/gfx/gui/peace_arrow.png \
    ui/gfx/gui/peace_dis.png \
    ui/gfx/gui/war.png \
    ui/gfx/gui/war_dis.png \
    ui/gfx/gui/windows.png \
    ui/gfx/gui/windows_slim.png \
    ui/gfx/gui/wood_background.png \
    ui/gfx/gui/wood_square.png \
    ui/gfx/shields/shield_A0_1.png \
    ui/gfx/shields/shield_England_1.png \
    ui/gfx/shields/shield_Ireland_1.png \
    ui/gfx/shields/shield_Scotland_1.png \
    ui/gfx/shields/shield_Sea_1.png \
    ui/gfx/shields/shield_Wales_1.png \
    ui/gfx/units/french/FK_ANE.png \
    ui/gfx/units/french/FK_ASW.png \
    ui/gfx/units/french/FK_RE.png \
    ui/gfx/units/french/FK_RN.png \
    ui/gfx/units/french/FK_RNE.png \
    ui/gfx/units/french/FK_RNW.png \
    ui/gfx/units/french/FK_RS.png \
    ui/gfx/units/french/FK_RSE.png \
    ui/gfx/units/french/FK_RSW.png \
    ui/gfx/units/french/FK_RW.png \
    ui/gfx/units/french/FK_ST.png \
    ui/gfx/circle.png \
    ui/components/AnimatedUnits.qml \
    ui/components/Cities.qml \
    ui/components/IconButton.qml \
    ui/components/Map.qml \
    ui/components/Notification.qml \
    ui/components/Units.qml \
    ui/components/Window.qml \
    ui/ui.qml \
    ui/Shield.qml
