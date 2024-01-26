FK-Graph
========

Visualise the graphs hidden within relational databases.

Schemas can sometimes fail to reflect the full complexity of the relationships in a 
populated database, especially when the data has been added manually over a period of time.

This application creates a graph of foreign key relations in a populated database and 
can be used to generate a plotly figure, or interactive dash app, showing these relations.

To install:
-----------

```
pip install fk-graph
```

Development:
------------

Clone the repo and `cd` in to the project directory. Create a virtual env, then install
the requirements with

```
pip install -r requirements.txt
```

Finally, to be able to run tests while developing, install the package as an editable install.

```
pip install --editable .
```
