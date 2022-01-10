# breath_apnea
Apnea/Hypopnea detection algoritm

RU: 
Алгоритм обнаружения эпиздодов апноэ и гипапноэ написан по алгоритму из вложенной в репозиторий статьи. Все файлы предоставлены компанией "Инкарт", разработка также проводилась
под их руководством в течение 5 недель. Алгоритм не полон, с сигналом сатурации работает хорошо, с реопневмограммой есть проблемы, в ближайшем будущем планирую всё исправить и доделать. 

Код всех блоков реализован на языке Python. Для запуска понадобится установка следующих библиотек: numpy, pandas, matplotlib, scipy, h5py.
Также для запуска необходимо, чтобы у всех трех файлов (.bin, .hdr, .hdf) по каждой записи было одно название. У файла с именами всех записей должно быть имя “files.txt”. 
Для удобства я переименовал все файлы с референтной разметкой и выгрузил всё на ЯД, включая файл со списком записей: https://disk.yandex.ru/d/IEksBsNea_eP1w

Файл stats_spo2.py рассчитывает статистики по сигналам сатурации, после его запуска в переменную foldpath нужно ввести путь к папке (с двойными бекслешами), в которой лежат все файлы, включая файл со списком записей. Далее программу можно сразу запускать, её работа будет длиться примерно 120 секунд для 7 записей, после чего будет выведена таблица со статистиками по каждой записи, которая также будет сохранена в формате .csv в исходную папку. В терминале также будет выведено время работы программы.

Файл results.py рассчитывает статистики по сигналам реопневмограммы и работает аналогично предыдущей, все результаты также будут выведены в терминале и сохранены в исходной папке 
в формате .csv. 

EN:
The algorithm for detecting episodes of apnea and hypapnea is written according to the algorithm from the article embedded in the repository. All files are provided by "Incart", the development was also carried out under their leadership for 5 weeks. The algorithm is not complete, it works well with the saturation signal, there are problems with the rheopneumogram, I plan to fix and finish everything in the near future.

The code of all blocks is implemented in Python. To run, you will need to install the following libraries: numpy, pandas, matplotlib, scipy, h5py.
Also, to run, it is necessary that all three files (.bin, .hdr, .hdf) have one name for each entry. The file with the names of all entries must have a name “files.txt ”.
For convenience, I renamed all the files with reference markup and uploaded everything to Yandex.Disc, including a file with a list of entries: https://disk.yandex.ru/d/IEksBsNea_eP1w

File stats_spo2.py calculates statistics based on saturation signals, after its launch, the path to the folder (with double backslashes) containing all files, including a file with a list of records, must be entered into the foldpath variable. Then the program can be started immediately, its operation will last approximately 120 seconds for 7 records, after which a table with statistics for each record will be displayed, which will also be saved in the format.csv to the source folder. The terminal will also display the running time of the program.

File results.py calculates statistics based on the signals of the rheopneumogram and works similarly to the previous one, all the results will also be output in the terminal and saved in the source folder in .csv format.
