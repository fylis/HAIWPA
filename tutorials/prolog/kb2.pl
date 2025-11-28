/*
Source : https://lpn.swi-prolog.org/lpnpage.php?pagetype=html&pageid=lpn-htmlse1
*/

happy(yolanda).
listens_music(mia).
listens_music(yolanda) :- happy(yolanda).
plays_instrument(mia) :- listens_music(mia).
plays_instrument(yolanda) :- listens_music(yolanda).