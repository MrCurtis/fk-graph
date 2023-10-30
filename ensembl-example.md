Ensembl Example
===============

We give a brief example by creating a graph of all the exons and transcripts related to a particular gene.
We do this using the publicly accessible [ensembl database](https://www.ensembl.org/info/data/mysql.html).

First we set up the sql-alchemy engine, to allow us to access the database:
>>> from sqlalchemy import create_engine
>>> engine = create_engine("mysql+mysqldb://anonymous:@ensembldb.ensembl.org:3306/felis_catus_core_110_9?charset=utf8mb4")

Then we create the graph:
>>> from graph import get_graph
>>> g = get_graph(engine=engine, table="gene", primary_key="89891")
