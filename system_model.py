import json

class system_model:

    def __init__(self,graphx = None):
        if graphx is None:
            self.graph = {"vertexes":{},"edges":[]}
        else:
            self.graph = graphx

    def to_json(self):
        return json.dumps(self.graph)

    def getVertexes(self):
        keys = list(self.graph["vertexes"].keys())
        keys.sort()
        return keys

    def getEdges(self):
        return self.graph["edges"] if "edges" in self.graph else []

    @staticmethod
    def is_edge_of_type(edge, relation_type):
        return "relation_type" in edge and edge["relation_type"] == relation_type

    def get_edges_of_type(self, relation_type):
        return [e for e in self.getEdges() if system_model.is_edge_of_type(e, relation_type)]

    def is_vertex_of_type(self, vertex, type):
        return self.graph["vertexes"][vertex]["type"] == type

    def _isEdgeWithEndVertex(self,edge,vertex):
        return edge["end"] == vertex

    def does_vertex_exists(self,key):
        return key in self.graph["vertexes"]

    def add_vertex(self, key, type):
        if key in self.graph["vertexes"]:
            return
        self.graph["vertexes"][key] = {"type":type}

    def add_edge(self, start, end, relation_type = None):
        edge = {"start":start, "end":end}
        if relation_type is not None:
            edge["relation_type"] = relation_type
        self.graph["edges"].append(edge)

    def get_related_vertex(self, vertex, edge):
        return  edge["start"] if edge["end"]==vertex else edge["end"]


    def get_children(self, parent_vertex, of_type,in_relation_of=None):
        return list(
            filter(lambda child: self.is_vertex_of_type(child,of_type),
            map(lambda edge: self.get_related_vertex(parent_vertex,edge),
            filter(lambda edge: in_relation_of is None or system_model.is_edge_of_type(edge, in_relation_of),
            filter(lambda edge: parent_vertex in (edge["start"], edge["end"]), self.getEdges())))))

    def get_vertexes_of_type(self,type):
        return [v for v in self.getVertexes() if self.is_vertex_of_type(v,type)]


class component_model(system_model):

    def get_calling_relations(self):
        return self.get_edges_of_type("calls")

    def getOrphanApplications(self):
        return [ v for v in self.get_vertexes_of_type("application") if not self._isVertexInEdges(v)]

    def isProduct(self,vertex):
        return self.is_vertex_of_type(vertex, "product")

    def getVertexName(self,vertex):
        return self.graph["vertexes"][vertex]["name"]

    def getApplicationsInProduct(self, product):
        return self.get_children(product,of_type="application",in_relation_of="contains")

    def _isVertexInEdges(self,vertex):
        for edge in self.getEdges():
            if self._isEdgeWithVertex(edge,vertex):
                return True
        return False

    def _isEdgeWithVertex(self,edge,vertex):
        return edge["start"] == vertex or edge["end"] == vertex

    def getProducts(self):
        return self.get_vertexes_of_type("product")


class data_model(system_model):

    def add_schema(self,schema):
        self.add_vertex(schema,"schema")

    def add_column(self,column,table):
        self.add_vertex(column,"column")
        self.add_edge(column,table)

    def add_table(self,table,schema):
        self.add_vertex(table,"table")
        self.add_edge(table,schema)

    def _isTable(self, vertex):
        return self.is_vertex_of_type(vertex, "table")

    def get_table_for_column(self,column):
        column_edges = [edge for edge in self.getEdges() if edge["start"]==column]
        for edge in column_edges:
            vertex = edge["end"]
            if self._isTable(vertex):
                return vertex
        return None

    def getSchemas(self):
        return self.get_vertexes_of_type("schema")

    def get_tables_in_schema(self, schema):
        return self.get_children(schema,"table")

    def get_columns_in_table(self, table):
        return self.get_children(table,"column")

    def get_foreign_keys(self):
        return list(
            map(lambda fk: self._get_foreign_key(fk["start"], fk["end"]),
                self.get_edges_of_type("fk")))

    def _get_foreign_key(self,column1, column2):
        return {
            "start":{
                "column":column1,
                "table":self.get_table_for_column(column1)
            },
            "end": {
                "column":column2,
                "table":self.get_table_for_column(column2)
            }
        }


