# CsvTable
CsvTable is a tool to open any csv-like file and browse it.  
The data is presented in a table and can be sorted and filtered. Columns be ignored too.  
The number of lines to open can be configured (can be quite usefull when opening large files)

## Getting started
##### Prerequisites :   
* Python >= 3.7  
* PySide2  
* Pandas

run `python src/main/python/main.py`

Open a file by dropping it in the app window or with the menu Fichier / Ouvrir un fichier

Settings can be accessed in the menu Fichier / Modifier les paramètres  
(encoding, separator, max number of lines ...)

To filter the data, use the text input with the following syntax:  
`[column name] >|>=|<|<= [number]` (for columns containing numbers only)  
`[column name] : [text]` (wildcards `*` and `?` are supported)  
The filters can be negated with the "Neg" checkbox

## License

This project is licensed under GPL License