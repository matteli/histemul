import QtQuick 2.7

Item {
    id: cities
    property var variable: ({})
    //property int province: 0

    function isCurrent(num)
    {
        if (num == 1)
        {
            if (variable['population'] >= 1 && variable['population'] < 1000)
                return true;
            else
                return false;
        }
        else if (num == 2)
        {
            if (variable['population'] >= 1000 && variable['population'] < 5000)
                return true;
            else
                return false;
        }
        else if (num == 3)
        {
            if (variable['population'] >= 5000 && variable['population'] < 25000)
                return true;
            else
                return false;
        }
        else if (num == 4)
        {
            if (variable['population'] >= 25000)
                return true;
            else
                return false;
        }
    }

    AnimatedSprite{
        x: 0
        y: -60
        width: 64
        height: 64
        visible: {
            if (variable['siege'] >= 1)
                return true;
            else
                return false;
        }
        interpolate: false
        antialiasing : false
        running: visible
        source: "./gfx/cities/catapult.png"
        frameCount: 12
        frameRate: 6
    }


    AnimatedSprite{
        x: -40
        y: -115 + variable['morale']   //-45
        width: 41
        height: 100 - variable['morale']
        //running: visible
        interpolate: false
        antialiasing : false
        source: "./gfx/cities/fire.png"
        reverse: true
        frameCount: 20
        frameRate: 10
    }

    Image {
        id: euro_city_1
        visible: isCurrent(1)
        source: "./gfx/cities/euro_city_1.png"
        x: -40
        y: -30

    }
    Image {
        id: euro_city_2
        visible: isCurrent(2)
        source: "./gfx/cities/euro_city_2.png"
        x: -40
        y: -30

    }
    Image {
        id: euro_city_3
        visible: isCurrent(3)
        source: "./gfx/cities/euro_city_3.png"
        x: -40
        y: -30

    }
    Image {
        id: euro_city_4
        visible: isCurrent(4)
        source: "./gfx/cities/euro_city_4.png"
        x: -40
        y: -30
    }
}
