##Dependency
You need to have a command line environment such as Linux, MacOS or Cygwin. However, Cygwin is not tested.


1. python (2.7 preferred)
2. Java (JDK 1.7 or above preferred)
3. ant (optional, this is for building java projects. If you dont use ant, then you might want to create java projects through an IDE such as eclipse or javabean) Install ant is very straightforward. See instruction from apache ant project page. 
4. Required Java libraries are all located in lib folder.

For python, you need to install the following libs:

1. requests
2. xlrd
3. beautifulsoup4
4. sqlalchemy


On MacOS or Linux  you can install these components with pip

check out the `./bin` folder, execute `./bin/savantor -h`  for details

## Fetching data from ActiveTick.com
execute 'python fetcher/fetch_attick get symbol date(yyyymmdd)'
=======

## Before you run
A few items before you run:

1. properly setup the config file (savant/config/default_settings.ini 
2. rename the ignore file gitignore to .gitignore under the project home directory
3. add the following statement to your ~/.bashrc or ~/.bash_profile
      export PYTHONPATH=xxxxx/savant-torrey-ranch
          where xxxxx is the absolute path to your project home

## Run Java components
Fetcher and Streamer are Java components. To run them , change to the component dir and run 
$ant
$ant run

There are a few other ant commands supported, such as clean and jar, but you don't have to use them. 

## Run Python components
Enter the component folder to execute python file

1. database population:  
   enter db folder 
   run "$python admin.py setup-database" dwfirst to initialize the database.
   enter ../scraer
   run "python populate_company"


## Directory structure (in change)
```
--------------------------------------------------------------------
|	git_dir (savant-torrey-ranch)
|	       savant 
|	            fetcher     (history data fetcher component: java)
|	                  src
|	            Streamer    (real time streamer component: java)
|	                  src
|	                  old   (older version of streamer)
|	            viewer      (viewer component: python)
|	            controller  (controller: python)
|	            trigger     (trigger: python)
|	            strategy    (strategy worker: python)
|               scraper 	  
|	            meta        (meta database fetcher)
|	            db		  (define database model)
|	            config 	  (global configuration component: python )
|               log		  (global logging component: python)
|	           data:     all data file: sqlite database, history data 
|	
|	       doc:   code documentation, how to build, lib dependency etc. 
|	       spec:  message specification, database schema, file formate etc.
|	       lib: all java code dependent lib 
--------------------------------------------------------------------
```
