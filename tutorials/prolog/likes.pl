likes(sam, Food) :- indian(Food), mild(Food).
likes(sam, Food) :- chinese(Food).
likes(sam, Food) :- italian(Food).
likes(sam, chips).

indian(curry).
indian(dahl).

mild(dahl).
mild(tandoori).

chinese(chow_mein).
chinese(chop_suey).

italian(pizza).
italian(spaghetti).
italian(meatballs).
