## Implementační dokumentace do IPP 2020/2021
## Jméno a příjmení: Ladislav Dokoupil
## Login: xdokou14
### interpret.py
#### Abstrakt
Interpret se skládá z několika navazujících částí. Nejprve je nutné zpracovat argumenty programu a načíst vstupní soubory. Poté je
nutné provést nad vstupem syntaktické kontroly a následně postupně zpracovávat instrukce. Případný výstup je směrován na stdout.
#### Zpracování argumentů
Pro zpracování argumentů je využita knihovna argparse, která ukládá argumenty do jednoduché struktury slovníku.
#### Syntaktická a lexikální analýza
Pro kontrolu XML souboru je využita knihovna ElementTree. Existence elementů hlavičky a jejich atributy jsou kontrolovány pomocí
jednoduchých podmínek. K syntaktické/lexikální kontrole je využita tabulka s definovanými typy argumentů instrukcí a pro
kontroly typů jsou využity regulární výrazy, které jsou zde uloženy v asociativním poli tvaru:
`'typ': 'regularni_vyraz',`.
#### Interpretace
Interpretace je prováděna voláním v jednoduchém cyklu, který nejprve načte do globálních proměnných argumenty a typy
operací. Pro volání funkcí je vytvořena tabulka (ve které
jsou uloženy i informace pro syntaktickou/lexikální kontrolu) ve tvaru:
`"OPCODE": {'call':funkce_instrukce, 'types': ["type_arg1", ... ,"typ_argX" ]},`
. Pro jednotnou strukturu přístupu k rámcům je oddělena struktura pro zásobník rámců a přístupné
rámce, kde při volání funkce 'POPFRAME' je pouze přenesen vrchol zásobníku do jiné proměnné
Pro instrukce skoku je navíc zpřístupněna iterační proměnná cyklu průchodu instrukcemi.
Funkce: `get_val, set_val, get_type` vytváří vhodnou abstrakci pro jednotný přistup k proměnným a konstantám při psaní kódu instrukcí.
Pro jednoduché určení typů jsou proměnné ukládány v tabulce
tvaru `{'val': HODNOTA, 'type': TYP}`. Dále je implementaváno rozšíření FLOAT, pro jehož začlenění stačilo vytvořit regulární výraz pro kontrolu typu
a přidat možnost typu float do požadovaných instrukcí. Případný výstup instrukce write je směrován na stdout a pro ladící
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
Jako výstup programu je vytvořen HTML soubor, ve kterém je vloženo i CSS. Pro jeho vytvoření je
využita knihovna DOM. Kód výstupního soubor je v textové formě směrován na stdout.
