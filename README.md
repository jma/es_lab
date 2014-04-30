ES_lab
======

Elasticsearch lab written for HESGE

# Introduction

This is a basic elasticsearch based open repository system to play with a search engine.

## Installation

### Requirements

	- python virtualenvwrapper
	- elasticserach >= 1.0.0 in the path (where elasticsearch)
	- bower (npm install bower)

### Create at new python virutal environement
    mkvirutalenv es_lab

### Colone the project
    git clone https://github.com/jma/es_lab.git

### Install dependencies
    cd es_lab; pip install -r requirements.txt

### Install js/css
	cd es_lab/static; bower install

### Run service
	cd ..
	honcho start

### Check data mapping
	python es_lab/records.py data/data.xml

### Indexing data
	python es_lab/es.py data/data.xml

### See the results in a browser
    http://localhost:5000

