# Přehled projektu

VocabPro je lokální desktopová aplikace pro vlastní slovní zásobu, gramatické
otázky a časování. Uživatel si volí vlastní jazyk, jeden nebo dva studované jazyky a jazyk
rozhraní. Dostupnost gramatiky a časování závisí na přítomnosti dat příslušného
kurzu. Soubory zůstávají lokální; nejde o víceuživatelský server.

Slovníkový editor nabízí tabulku, filtrování, číselné a datumové řazení,
vkládání z tabulkových aplikací, vlastní audio, mazání a synonymní vazby.
Procvičování podporuje překlad, kontext a poslech s možnostmi. Gramatika má
otázky se čtyřmi možnostmi, teorie kategorií, filtr i editory. Statistiky
shrnují historii, růst, budoucí opakování, slabší slovíčka a kategorie.

Technologie: Python, Tk/CustomTkinter, tksheet, pandas/numpy, Matplotlib,
Pillow, pygame, PyAudio a requests. Konkrétní ověřené verze jsou v
[requirements.txt](../../requirements.txt). GUI je zaměřené na Windows;
`pywinstyles` a stav zoomed omezují přenositelnost.

Základní pravidla: obsah CSV se nezaměňuje za překlady UI, ID slovíček jsou
stabilní, výukový stav je nejprve v paměti a zápis probíhá na explicitní Save
nebo po potvrzení odchodu. Automatické doplňování údajů používá externí API.
Nezávislá e-mailová záloha posílá pouze neprázdné datové CSV.
