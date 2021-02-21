
## Implementační dokumentace do IPP 2020/2021
## Jméno a příjmení: Ladislav Dokoupil
## Login: xdokou14
### parse.php
#### Abstrakt
Analyzátor IPP kódu je rozdělen do několika spolupracujících částí. Nejprve si načtený text rozdělím na tokeny instrukcí
a argumentů, nad kterými následně provádím lexikální a sémantickou analýzu. Pokud vše proběhne bez chyb, uložím výsledek
do XML souboru.
#### Rozdělení na tokeny
Vstupní text načítám po řádcích, které si po odstranění komentářů rozdělím podle výskytu netisknutelných znaků na pole tokenů.
První token zde značí operační kód a ostatní jeho argumenty.
#### Syntaktická a lexikální analýza
Pro syntaktyckou analýzu jsem si vytvořil statickou tabulku všech příkazů tvaru:
`"OPCODE" => array( "ARG1", "ARG2", ),`.
Pokud se operační kód v tabulce nevyskytuje, vrací program kód chyby. V opačném případě je zkontrolováno, zda odpovídá 
skutečný počet argumentů se vzorem v tabulce a následně je pro každý argument provedena kontrola.
 Pro každý očekávaný typ argumentu (var, symb ...) je vytvořen regulární výraz, který zjištuje zda lexém na vstupu odpovídá
 očekávanému typu.
#### Výstup
Pro vytvoření XML souboru je využita knihovna DOM, která oproti výpisům na stdout výrazně zlepšila přehlednost kódu. Pro převod
 znaků, které využivá XML k identifikaci elementů (`&<>'"`), bylo nutné vytvořit funkci, která v každém řetezci zamění tyto znaky
 za jejich odpovídající XML entity.

### interpret.py
#### Abstrakt
Interpret se skládá z několika navazujících částí. Nejprve je nutné zpracovat argumenty a načíst vstupní soubory. Poté je
nutné provést nad vstupem další kontroly a následně postupně zpracovávat instrukce. Případný výstup je směrován na stdout.
#### Zpracování argumentů
Pro zpracování argumentů je využita knihovna argparse, která ukládá argumenty do jednoduché struktury slovníku.
#### Syntaktická a lexikální analýza
Pro kontrolu XML souboru je využita knihovna ElementTree. Elementy hlavičky a jejich atributy jsou kontrolovány pomocí
jednoduchých podmínek. K syntaktické/lexikální kontrole je opět využita tabulka s definovanými typy argumentů instrukcí a pro
kontroly typů jsou opět využity regulární výrazy, které jsou zde uloženy v asociativním poli tvaru: 
`'typ': 'regularni_vyraz',`.
#### Interpretace
Interpretace je prováděna voláním v jednoduchém cyklu, který nejprve načte do globálních proměných argumenty a typy
operací. Pro volání funkcí je vytvořena tabulka (ve které 
jsou uloženy i informace pro syntaktickou/lexikální kontrolu) ve tvaru: 
`"OPCODE": {'call':funkce_instrukce, 'types': ["type_arg1", ... ,"typ_argX" ]},`
. Pro jednotnou strukturu přístupu k rámcům je oddělena struktura pro zásobník rámců a přístupné
rámce, kde při volání funkce 'POPFRAME' je pouze přenesen vrchol zásobníku do jiné proměnné
Pro instrukce skoku je navíc zpřístupněna iterační proměnná cyklu průchodu instrukcemi.
 Funkce: `get_val, set_val, get_type` vytváří vhodnou abstrakci pro jednotný přistup k proměnným a konstantám při psaní kódu instrukcí.
 Pro jednoduché určení typů jsou proměnné ukládány v tabulce
tvaru `{'val': HODNOTA, 'type': TYP}`. Implementace rozšíření float byla jednoduchá, jelikož stačilo vytvořit regulární výraz pro kontrolu typu
a přidat možnost typu float do požadovaných instrukcí. Dále je naprogramováno i rozšíření STACK, základ pro něj je vytvořen již z instrukcí
`PUSHS, POPS`, tak jeho rozšíření bylo jednoduché. Případný výstup insturkce write je směrován na stdout a ladící
instrukce `DPRINT, BREAK` je výstup prováděn na stderr.
### test.php
#### Abstrakt
Tento testovací skript je vytvořen pro snadné automatické testovaní funkčnosti projektu. Skript je složen z části zpracování
argumentů, volání testovaných programů, validace výsledků a následné vytvoření uživatelsky přívětivého HTML souboru s výsledky testů.
#### Zpracování argumentů
Kvůli velkému množství argumentů, jejichž manuální zpracovaní by bylo složitější a znepřehlednilo by program, je využíta
knihovna getopt. Dále je nutné zkontrolovat existenci všech souborů zadaných v argumentech a případně skončit s chybou.
#### Testovani a validace 
Pro procházení složek s testy je využita knihovna `RecursiveDirectoryIterator`. Testování je rozděleno na 2 části.
V první části jsou ukládány do pole všechny soubory k průchodu a samotný průchod je oddělen zvlášt. Testy jsou volány pomoci funkce exec, 
která spustí daný argument na příkazové řádce. Ve skriptu jsou využívány dočasné soubory pro ukládání mezivýsledků, které jsou před ukončením programu smazány. 
#### Výstup
Jako výstup programu je vytvořen uživatelsky přívětivý HTML soubor, ve kterém je vloženo i CSS. Pro vytvoření HTML souboru je opět 
využita knihovna DOM. Výstup je vytvořen ve stejné složce, ve které je spuštěn skript, s názvem `tests.html`.
