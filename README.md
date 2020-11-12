# COVID19_Data_Project
## Summary
this project collects COVID19 case counts by county from a collection of states that have made their data available either by api or pdf. at present, this includes: Florida, Georgia, Illinois, Indiana, Virginia, and Wisconsin. it then formats that data to match specific entry templates for the COVID19 Data Project and writes it to a .csv file. `clean_all.py` runs all scripts, and writes the day's files to the appropriate `cleaned_data/[state]` folder.
## Considerations for using
even within these two formats, each state takes its own approach to hosting/organizing data, so each state gets its own script. at present, the api call/pdf url is pre-loaded, set to gather the most recent full days case counts. api calls are tailored to the state and database that hosts the data.

if scraping requires a reference file (for example, illinois requires querying each county separately) the file is located in `reference_files`. 

generally, scripts take date from the data itself, so if the state reports by date collected, the file will be organized by date collected. if the state reports by date verified, then it'll be dated accordingly.

the scripts assume that they're being run inside `get_n_clean`, with the attendent directories, and with that in mind they should (hopefully) run on any machine. 
## Todo
 
- [x] abstract data collection principles to more general approaches. specifically: can this be done with states that post their data as pdfs? how can I abstract the entry template to speed up the cleaning process? 
- [x] make code more uniform. i tried multiple approaches as I worked through various states, so even with similar data the code can vary.  
- [ ] tackle html scraping for states that do not offer apis or pdfs.  
- [ ] set up hosting, in order to run this project in real-time. 
- [x] add argparse (see: awesome-python)
