Ավտոմատի *սահմանումը* այս լեզվով հետևյալ տեսքն ունի․
  
```
 DFA A1 { \
 A1 = DFA { \
    S = 4 \
    A = {'a', 'b', 'c'} \
    T = {(1, 'a', 2), (1, 'b', 3), (2, 'c', 4), (3, 'b', 1) \
 }
```
Հարցնենք ավտոմատին *ճանաչել որևէ տող*․ <br />
```
 Accept "abc" with A1
```
կամ <br />
```
 Accept "abc" with DFA { \
    S = 4 \
    A = {'a', 'b', 'c'} \
    T = {(1, 'a', 2), (1, 'b', 3), (2, 'c', 4), (3, 'b', 1)} \
    F = {2, 4} \
 }
```
Կարելի է նաև *ճանաչել* նույն տողը միաժամանակ *մի քանի ավտոմատներով*․ <br />
```
Accept "abc" with (A1, A2, A3)
```
<br />
Լեզվի քերականությունը․ <br />

```
Program           = {[NewLines] Module}.
Module            = (DefModule | AcceptModule) NewLines.
DefModule         = ID '=' Automaton.
Automaton         = (Recognizer | Modifier)
Recognizer        = 'Recognizer' '{' States Alphabet Transitions FinalStates '}'.
Modifier          = 'Modifier' '{' States Alphabet ExtTransitions FinalStates '}'.
AcceptModule      = 'Accept' STRING 'with' (IDList | Automaton).
States            = 'States'|'S' '=' NUMBER.
Alphabet          = 'Alphabet'|'A' '=' LetterList.
Transitions       = 'Transitions'|'T' '=' TransitionList.
ExtTransitions    = 'Transitions'|'T' '=' ExtTransitionList.
FinalStates       = 'FinalStates'|'F' '=' NumberList.
LetterList        = '{' LETTER {',' LETTER} '}'.
NumberList        = '{' NUMBER {',' NUMBER} '}'.
IDList            = '{' ID {',' ID} '}'.
TransitionList    = '{' Transition {',' Transition} '}'.
ExtTransitionList = '{' ExtTransition {',' ExtTransition} '}'.
Transition        = '(' NUMBER ',' LETTER ',' NUMBER ')'.
ExtTransition     = '(' NUMBER ',' LETTER ',' NUMBER ',' LETTER ')'.
NewLines          = NL {NL}.
```
