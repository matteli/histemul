var A = [ 1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1 ],
    R = [ "M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I" ],
    Alength = A.length;

// conversion d'un entier en nombre romain
function a2r( nb ){
    // on s'assure d'avoir un entier entre 1 et 3999.
    var x = parseInt( nb, 10 ) || 1,
        str = "";

    if ( x < 1 ){
        x = 1;
    } else if ( x > 3999 ){
        x = 3999;
    }

    // pour chaque A[ i ],
    // tant que x est supérieur ou égal
    // on déduit A[ i ] de x.
    // arrêt de la boucle si x == 0
    for ( var i = 0; i < Alength; ++i ){
        while ( x >= A[ i ] ){
            x -= A[ i ];
            str += R[ i ];
        }

        if ( x == 0 ){
            break;
        }
    }

    return str;
}

function l2t(level)
{
    if (level == 1)
        return 'Earl';
    if (level == 2)
        return 'Duke';
    if (level == 3)
        return 'King';
}
