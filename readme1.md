## Implementační dokumentace do IPP 2020/2021
## Jméno a příjmení: Ladislav Dokoupil
## Login: xdokou14
### parse.php
#### Abstrakt
Analyzátor IPP kódu je rozdělen do několika spolupracujících částí. Nejprve je načtený text rozdělen na tokeny instrukcí
a argumentů, nad kterými se následně provádí lexikální a sémantické kontroly. Pokud vše proběhne bez chyb, uloží se výsledek
do XML souboru.
#### Rozdělení na tokeny
Vstupní text se načítá po řádcích, které se po odstranění komentářů rozdělí podle výskytu netisknutelných znaků na pole tokenů.
První token zde značí operační kód a ostatní jeho argumenty.
#### Syntaktická a lexikální analýza
Pro syntaktyckou analýzu je vytvořena statická tabulka všech příkazů tvaru:
`"OPCODE" => array( "ARG1", "ARG2", ),`.
Pokud se operační kód v tabulce nevyskytuje, vrací program kód chyby. V opačném případě je zkontrolováno, zda odpovídá 
skutečný počet argumentů se vzorem v tabulce a následně je pro každý argument provedena kontrola.
 Pro každý očekávaný typ argumentu (var, symb ...) je vytvořen regulární výraz, který zjištuje zda daný lexém odpovídá
 očekávanému typu.
#### Výstup
Pro vytvoření XML souboru je využita knihovna DOM, která oproti výpisům na stdout výrazně zlepšila přehlednost kódu. Pro převod
 znaků, které využivá XML k identifikaci elementů (`&<>'"`), bylo nutné vytvořit funkci, která zamění všechny 
výskyty těchto znaků za jejich odpovídající XML entity.