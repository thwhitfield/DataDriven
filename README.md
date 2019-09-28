# Data Science Portfolio
This repository contains my personal portfolio of data science related projects. These projects contain exploratory data analysis, machine learning/predictive modeling, and data driven conclusions/insights.

## Contents
### [General Aviation Aircraft Accident Analysis](https://github.com/thwhitfield/Data_Science_Portfolio/blob/master/General%20Aviation%20Aircraft%20Accident%20Analysis/General_Aviation_Aircraft_Accident_Analysis.ipynb)

[Jupyter Notebook analysis link](https://github.com/thwhitfield/Data_Science_Portfolio/blob/master/General%20Aviation%20Aircraft%20Accident%20Analysis/General_Aviation_Aircraft_Accident_Analysis.ipynb)

For this independent project, I did exploratory analysis on the aircraft accident database provided by the Federal Aviation Administration (FAA) and the National Transportation Safety Board (NTSB), with the goal of determining the important factors that contribute to an aircraft's accident being fatal. Next, I created a classifier to predict whether a given accident will be fatal based on characteristics of the aircraft, pilot, and general conditions of the flight before the accident.

#### Map of General Aviation Aircraft Accidents
I also created an interactive map of general aviation aircraft accidents. Here is the [script](https://github.com/thwhitfield/Data_Science_Portfolio/blob/master/General%20Aviation%20Aircraft%20Accident%20Analysis/Mapping_General_Aviation_Aircraft_Accidents.ipynb) to produce the map, and here is the [map](https://github.com/thwhitfield/Data_Science_Portfolio/blob/master/General%20Aviation%20Aircraft%20Accident%20Analysis/General_Aviation_Accident_Map_2010_to_present.html) itself.

### [Aircraft Database - Web Scraping and Recommender System](https://github.com/thwhitfield/Data_Science_Portfolio/tree/master/Aircraft%20Database%20-%20Web%20Scraping%20and%20Recommender%20System)
For this independent project, I created a sortable, filterable, and searchable database of all aircraft designs listed on wikipedia. I believe this is the first free database of that type online. To create the database, I scraped the aircraft specifications and wikipedia page content for all the aircraft listed on wikipedia, parsed that data, and created a database with it. I uploaded that database to this github page. I also created a specification based aircraft recommender system, such that given an aircraft the system will return aircraft of similar specifications.

The final database has approximately 10,000 aircraft, and includes specifications like: wingspan, length, height, empty weight, gross weight, maximum speed, cruise speed, and stall speed. The database also includes the manufacturer, aircraft role, number of aircraft built, first flight year, and national origin.

The code is separated into 6 files, and the resulting database has been uploaded to this [website](https://thwhitfield.github.io/Aircraft-Database/index.html).
