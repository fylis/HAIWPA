"""
Source : https://www.youtube.com/watch?v=utjL-yx2FYU
"""

add(A,B) :-
    Res is A+B, write(A), write(' + '), write(B), write(' = '), writeln(Res). 