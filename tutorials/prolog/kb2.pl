happy(yolanda).
listens_music(mia).
listens_music(yolanda) :- happy(yolanda).
plays_instrument(mia) :- listens_music(mia).
plays_instrument(yolanda) :- listens_music(yolanda).