from typing import Optional
from fastapi import FastAPI,Header, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.structure.io import graphsonV3d0
from gremlin_python.process.graph_traversal import __,union, values, constant, unfold
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.traversal import T, P, Operator, Order, neq
from typing import Optional
from pydantic import BaseModel
import datetime
import uuid
import json

statics.load_statics(globals())

endpoint = 'ws://10.1.0.4:8182/gremlin'

graph = Graph()

connection = DriverRemoteConnection(endpoint,'g')
# The connection should be closed on shut down to close open connections with connection.close()
g = graph.traversal().withRemote(connection)
# Reuse 'g' across the application

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")



@app.get("/")
def read_root():
    return {"Hello": "Word"}

@app.get("/products")
def read_products(token: Optional[str] = Header(None)):
    writer = graphsonV3d0.GraphSONWriter()
 
    #products = writer.toDict(g.V().hasLabel('Product').limit(2).project('Product Id','Product Name').by('productID').by('productName').toList())
    #products = writer.writeObject(g.V().hasLabel('Product').limit(2).project('Product Id','Product Name').by('productID').by('productName').toList())
    products = g.V().hasLabel('Product').limit(2).project('Product Id','Product Name').by('productID').by('productName').toList()
    #pjson = json.dumps(products)
    return products

@app.get("/products/{id}")
def read_products(request: Request, id: str):
    
    ret = {}
 
    product = g.V().has('Product','productID',id).project('Product Id','Product Name').by('productID').by('productName').toList()
    

    return product

@app.get("/suppliers")
def read_products(token: Optional[str] = Header(None)):
    
 
    supplier = g.V().hasLabel('Supplier').valueMap().toList()
    
    return supplier

@app.get("/product-categories")
def read_products(token: Optional[str] = Header(None)):
    
 
    category = g.V().hasLabel('Category').valueMap().toList()
    
    return category


@app.get("/pcs")
def read_products(token: Optional[str] = Header(None)):
    
 
    pcs = g.V().hasLabel("Product").match(as_("c").values("productID").as_("Product ID"),\
                as_("c").values("productName").as_("Product Name"),\
                as_("c").out("PART_OF").values("categoryID").as_("Category ID"),\
                as_("c").out("PART_OF").values("categoryName").as_("Category Name"),\
                as_("c").in_("SUPPLIES").values("supplierID").as_("Supplier ID"),\
                as_("c").in_("SUPPLIES").values("companyName").as_("Company Name"),\
                ).select("Product ID","Product Name","Category ID","Category Name","Supplier ID","Company Name").toList()
    
    return pcs