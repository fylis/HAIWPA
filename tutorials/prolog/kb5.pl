/*
Source : https://lpn.swi-prolog.org/lpnpage.php?pagetype=html&pageid=lpn-htmlse1
*/

loves(vincent,mia).
loves(marsellus,mia).
loves(pumpkin,honey_bunny).
loves(honey_bunny,pumpkin).
jealous(X,Y) :- loves(X, Z), loves(Y, Z).