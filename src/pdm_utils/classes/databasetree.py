""" Module containing various data structure objects for the handling
and mapping of the characteristics and relationships of a MySQL database.
"""

from pdm_utils.classes.mysqlconnectionhandler import MySQLConnectionHandler
import re

def setup_db_tree_leaves(sql_handle, db_node):
    """Function to create structures to mimic a MySQL database.

    :param sql_handle:
        Input a validated MySQLConnectionHandler object.
    :type sql_handle: MySQLConnectionHandler
    :param db_node:
        Input an empty DatabaseNode.
    :type db_node: DatabaseNode
    """
    table_query = (
        "SELECT DISTINCT TABLE_NAME FROM INFORMATION_SCHEMA.COLUMNS "
       f"WHERE TABLE_SCHEMA='{sql_handle.database}'")
    table_dicts = sql_handle.execute_query(table_query)

    for data_dict in table_dicts:
        table_node = TableNode(data_dict["TABLE_NAME"])
        db_node.add_table(table_node)
        
        column_query = f"SHOW columns IN {data_dict['TABLE_NAME']}"
        column_dicts = sql_handle.execute_query(column_query)
        for column_dict in column_dicts:
            if column_dict["Null"] == "YES":
                Null = True
            else:
                Null = False

            column_node = ColumnNode(column_dict["Field"],
                                     type=column_dict["Type"],
                                     Null=Null,
                                     key=column_dict["Key"])
            table_node.add_column(column_node)
            if(column_dict["Key"] == "PRI"):
                table_node.primary_key = column_node

def setup_db_tree_webs(sql_handle, db_node):
    """Function to modify and link structures to mimic a MySQL database.

    :param sql_handle:
        Input a validated MySQLConnectionHandler object.
    :type sql_handle: MySQLConnectionHandler object.
    :param db_node:
        Input a DatabaseNode populated with TableNodes and ColumnNodes.
    """
    for table in db_node.children:
        foreign_key_query = (
              f"SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME, "
               "REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME "
               "FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
              f"WHERE REFERENCED_TABLE_SCHEMA='{sql_handle.database}' AND "
                    f"REFERENCED_TABLE_NAME='{table.id}'")
        foreign_key_results = sql_handle.execute_query(foreign_key_query)
        if foreign_key_results != ():
            for dict in foreign_key_results:
                primary_key_node = table.get_column(
                                             dict["COLUMN_NAME"])
                ref_table = db_node.get_table(
                                             dict["TABLE_NAME"])
                foreign_key_node = ref_table.get_column(
                                             dict["COLUMN_NAME"])

                primary_key_node.add_table(ref_table)
                
                if foreign_key_node == ref_table.primary_key:
                    ref_table.primary_key = primary_key_node

                for parent in foreign_key_node.parents:
                    if parent not in primary_key_node.parents:
                        primary_key_node.add_table(parent)
                        parent.remove_column(foreign_key_node)

                ref_table.remove_column(foreign_key_node)

def setup_grouping_options(sql_handle, db_node):
    """Function to categorize structures to mimic a MySQL database.

    :param sql_handle:
        Input a validated MySQLConnectionHandler object.
    :type sql_handle: MySQLConnectionHandler
    :param db_node:
        Input a DatabaseNode populated with TableNodes and ColumnNodes.
    :type db_node: DatabaseNode
    """
    limited_sets = ["varchar_sm", "enum", "char", "tinyint"]
    str_sets     = ["blob", "mediumblob", "varchar", "varchar_sm"]
    num_sets     = ["int", "decimal", "mediumint", "float", "datetime",
                    "double"]

    for table in db_node.children:
        for column in table.children:
            type = column.parse_type()
            if type == "varchar":
                varchar_size = re.compile("[1234567890]+")
                if int(re.findall(varchar_size, column.type)[0]) <= 15:
                    type = "varchar_sm"


            if type in str_sets:
                column.group = "str_set"

            elif type in num_sets:
                column.group = "num_set"

            if type in limited_sets:
                query = f"SELECT COUNT(DISTINCT {column.id}) FROM {table.id}"
                results_dict = sql_handle.execute_query(query)[0]

                if results_dict[f"COUNT(DISTINCT {column.id})"] < 150:
                    column.group = "limited_set"

class DatabaseTree: 
    """Object which stores a DatabaseNode object as the root of a Tree."""
    def __init__(self, sql_handle):
        """Intitializes a DatabaseTree object.

        :param sql_handle:
            Input a validated MySQLConnectionHandler object.
        :type sql_handle: MySQLConnectionHandler
        """
        self.sql_handle = sql_handle 
        self.db_node = DatabaseNode(sql_handle.database)
        
        setup_db_tree_leaves(sql_handle, self.db_node)                
        setup_db_tree_webs(sql_handle, self.db_node) 

        setup_grouping_options(sql_handle, self.db_node)

    def get_table(self, table):
        """Function that returns a TableNode connected to the DatabaseNode.

        :param table:
            Input the name of a TableNode as a string.
        :type table: str
        :returns self.db_node.get_table(table)
            Calls a function of the DatabaseNode to retrieve a TableNode.
        :type self.db_node.get_table(table): TableNode
        """
        return self.db_node.get_table(table)

    def has_table(self, table):
        """Function that returns a boolean of if a TableNode exists.
        
        :param table:
            Input the name of a TableNode as a string.
        :type_ table: str
        :returns self.db_node.has_table(table)
            Calls a function of the DatabaseNode to return a boolean.
        :type self.db_node.has_table(table): Boolean
        """
        return self.db_node.has_table(table)

    def show_tables(self):
        """Function that returns a list representing the TableNodes attatched.

        :returns self.db_node.show_tables()
            Calls a function of the DatabaseNode to return a list of strings.
        :type self.db_node.show_tables(): List[str]
        """
        return self.db_node.show_tables()

    def get_root(self):
        """Function that allows access to the DatabaseNode.

        :returns self.db_node
            Returns the stored DatabaseNode representing a MySQLDB Tree.
        :type self.db_node: DatabaseNode
        """
        return self.db_node

    def find_path(self, curr_table, target_table, current_path=None):
        """Recursive function that finds a path between two TableNodes.

        :param curr_table:
            Input a starting TableNode under a DatabaseNode.
        :type curr_table: TableNode
        :param target_table:
            Input a target TableNode under a DatabaseNode.
        :type target_table: TableNode
        :param current_path:
            Input a 2-D array containing the traversed nodes in a path.
        :returns current_path:
            Returns a 2-D array containing the tables and keys in the path.
        :type current_path: List[List[str]] 
        """
        if current_path == None:
            current_path = []

        previous_tables = []

        for previous in current_path:
            previous_tables.append(previous[0])

        if curr_table == target_table:
            return current_path

        table_links = curr_table.get_foreign_keys()
        if len(curr_table.primary_key.parents) > 1:
            table_links.insert(0, curr_table.primary_key)

        for link in table_links:
            if target_table in link.parents:
                path = current_path.copy()
                path.append([target_table.id, link.id])
                return path
            for table in link.parents:
                if table.id not in previous_tables and table != curr_table:
                    path = current_path.copy()
                    path.append([table.id, link.id])
                    path = self.find_path(table, target_table, path)
                    if path != None:
                        if (path[-1])[0] == target_table.id:
                            return path

    def build_values(self, table, column, values_column=None,
                     queries=[], values=[]):
        """Function to query a MySQL database for a set of primary keys.
        
        :param table:
            Input the name of a TableNode as a string.
        :type table: str
        :param column:
            Input the name of a column of a TableNode as a string.
        :type column: str
        :param values_column:
            Input the name of a column for the intersecting values.
        :type values_column: str
        :param queries:
            Input a list of MySQL comparison statements.
        :type queries: List[str]
        :param values:
            Input a list of existing values as strings.
        :type values: List[str]
        :returns values:
            Returns a list of column values as strings.
        :type values: List[str]
        """
        table_node = self.get_table(table)
        if table_node == None:
            raise ValueError

        if not table_node.has_column(column):
            raise ValueError
        query = f"SELECT {column} FROM {table}"

        if queries or values:
            query = query + " WHERE "

        if queries:
            query = query + " and ".join(queries)
            if values:
                query = query + " and "

        if values and values_column == None:
            query = query +f"{table_node.primary_key.id} IN ('" +\
                              "','".join(values) + "')"
        elif values and values_column != None: 
            query = query +f"{values_column} IN ('" +\
                            "','".join(values) + "')"

        values = []
        for result in self.sql_handle.execute_query(query):
            values.append(result[column])
 
        return values

class Node:
    """Object which can store other Node objects and an id."""

    def __init__(self, id, parents=None, children=None):
        """Initializes a Node object.

        :param id:
            Input a ID for a Node object as a string.
        :type id: str
        :param parents:
            Input parents for a Node object as a list of Node objects.
        :type parents: List[Node]
        :param children:
            Input children for a Node object as a list of Node objects.
        :type children: List[Node]
        """
        if parents == None:
            self.parents = []
        else:
            self.parents = parents

        if children == None:
            self.children = []
        else:
            self.children = children

        self.id = id

    def add_parent(self, parent_node):
        """Function to link an existing Node object as a parent.

        :param parent_node:
            Input a Node object.
        :type parent_node: Node
        """
        parent_node.children.append(self)
        self.parents.append(parent_node)

    def add_child(self, child_node):
        """Function to link an existing Node object as a child.

        :param child_node:
            Input a Node object.
        :type child_node: Node
        """
        child_node.parents.append(self)
        self.children.append(child_node)

    def create_parent(self, parent_id):
        """Function to create and link a new Node object as a parent.

        :param parent_id:
            Input an ID for the new Node object as a string.
        :type parent_id: str
        :returns parent_node:
            Returns the created and linked Node object.
        :type parent_node: Node
        """
        parent_node = Node(parent_id)
        self.add_parent(parent_node)
        return parent_node

    def create_child(self, child_id):
        """Function to create and link a new Node object as a child.
        
        :param child_id:
            Input an ID for the new Node object as a string.
        :type child_id: str
        :returns child_node:
            Returns the created and linked Node object.
        :type child_id: Node
        """
        child_node = Node(child_id)
        self.add_child(child_node)
        return child_node

    def show_parents(self):
        """Function that returns a list representing the all parent Nodes.

        :returns parents:
            Returns a list of IDs representing the parent Nodes.
        :type show_parents: List[str]
        """
        parents = []
        for parent in self.parents:
            parents.append(parent.id)

        return parents

    def show_children(self):
        """Function that returns a list representing all the children Nodes.
        
        :returns children:
            Returns a list of IDs representing the children Nodes.
        :type children: List[str]
        """
        children = []  
        for child in self.children:
            children.append(child.id)

        return children

    def has_parent(self, parent):
        """Function that returns a boolean of if a parent Node exists.

        :param parent:
            Input the name of a parent Node as a string.
        :type parent: str
        :returns (parent in parents)
            Returns a boolean expression of if a ID matches any parent Node.
        :type (parent in parents): Boolean
        """
        parents = self.show_parents()
        return (parent in parents)

    def has_child(self, child):
        """Function that returns a boolean of if a child Node exists.

        :param child:
            Input the name of a child Node as a string.
        :type child: str
        :returns (child in children)
            Returns a boolean expression of if a ID matches any child Node.
        :type (child in children): Boolean
        """
        children = self.show_children()
        return (child in children)

    def get_parent(self, parent_id):
        """Function that returns a connected parent Node.

        :param parent_id:
            Input the ID of a parent Node as a string.
        :type child_id: str
        :returns parent_node
            Returns a parent Node with a matching ID.
        :type parent_node: Node
        """
        parent_node = None
        for parent in self.parents:
            if parent.id == parent_id:
                parent_node = parent

        return parent_node

    def get_child(self, child_id):
        """Function that returns a connected child Node.

        :param child_id:
            Input the ID of a child Node as a string.
        :type child_id: str
        :returns child_node
            Returns a child Node with a matching ID.
        :type child_node: Node
        """
        child_node = None
        for child in self.children:
            if child.id == child_id:
                child_node = child

        return child_node

    def remove_parent(self, parent_node):
        """Function that disconnects a connected parent Node.

        :param parent_node:
            Input the parent Node.
        :type parent_node: Node
        :returns parent_node
            Returns the removed parent_node.
        :type parent_node: Node
        """
        if parent_node != None:
            self.parents.remove(parent_node)
            parent_node.children.remove(self)

        return parent_node

    def remove_child(self, child_node):
        """Function that disconnects a connected child Node.

        :param child_node:
            Input the child Node.
        :type child_node: Node
        :returns child_node
            Returns the removed child_node.
        :type child_node: Node
        """
        if child_node != None:
            self.children.remove(child_node)
            child_node.parents.remove(self)

        return child_node

class DatabaseNode(Node):
    """Object which can store TableNode objects and an id """
    def __init__(self, id, parents=None, children=None):
        super(DatabaseNode, self).__init__(
                                    id, parents=parents, children=children)
   
    def create_table(self, table):
        """Function to create and link a new TableNode object as a child.
        
        :param table:
            Input an ID for the new TableNode object as a string.
        :type table: str
        :returns child_id:
            Returns the created and linked Node object.
        :type child_id: Node
        """
        return self.create_child(table)

    def add_table(self, table_node):
        """Function to link an existing TableNode object as a child.

        :param table_node:
            Input a Node object.
        :type table_node: Node
        """
        self.add_child(table_node)

    def remove_table(self, table):
        """Function that disconnects a connected TableNode.

        :param table_node:
            Input the TableNode.
        :type table_node: Node
        :returns child_node
            Returns the removed child_node.
        :type child_node: Node
        """

        return self.remove_child(table)

    def show_tables(self):
        """Function that returns a list representing all the TableNodes.
        
        :returns children:
            Returns a list of IDs representing the TableNodes.
        :type children: List[str]
        """
        return self.show_children()

    def has_table(self, table):
        """Function that returns a boolean of if a TableNode exists.

        :param table:
            Input the name of a TableNode as a string.
        :type table: str
        :returns (child in children)
            Returns a boolean expression of if a ID matches any TableNode.
        :type (child in children): Boolean
        """
        return self.has_child(table)

    def get_table(self, table):
        """Function that returns a connected TableNode.

        :param table:
            Input the ID of a TableNode as a string.
        :type table: str
        :returns child_node
            Returns a child Node with a matching ID.
        :type child_node: Node
        """
        return self.get_child(table)

class TableNode(Node):
    """Object which can store ColumnNode objects, an id, and table info."""

    def __init__(self, id, parents=None, children=None):
        super(TableNode, self).__init__(
                                    id, parents=parents, children=children)

        self.primary_key = None

    def create_column(self, column):
        """Function to create and link a ColumnNode object.

        :param column:
            Input an ID for the ColumnNode object as a string.
        :type column: str
        :returns column_node:
            Returns the created and linked ColumnNode object.
        :type column_node: ColumnNode
        """
        column_node = ColumnNode(column)
        column_node.parents.append(self)
        self.children.append(column_node)

        return column_node

    def add_column(self, column_node):
        """Function to link an existing Node object as a child.

        :param column_node:
            Input a Node object.
        :type column_node: ColumnNode
        """
        return self.add_child(column_node)

    def remove_column(self, column_node):
        """Function that disconnects a connected child Node.

        :param column_node:
            Input the ColumnNode.
        :type column_node: ColumnNode
        :returns child_node
            Returns the removed column node.
        :type child_node: ColumnNode
        """
        return self.remove_child(column_node)

    def show_columns(self):
        """Function that returns a list representing all the ColumnNodes.
        
        :returns children:
            Returns a list of IDs representing the ColumnNodes.
        :type children: List[str]
        """
        return self.show_children()

    def show_columns_info(self):
        """Function that returns a list of info of attatched ColumnNodes.

        :returns columns_info:
            Returns a list of lists containing info about the MySQL column.
        :type columns_info: List[List[str]]
        """
        columns_info = []
        for columns in self.children:
            columns_info.append(columns.show_info())

        return columns_info
    
    def print_columns_info(self):
        """"Function that formats and prints a list of Columns' info."""

        print(" " + "_"*61 + " ")
        print("|" + " "*61 + "|")
        print("| %-16s | %-10s | %-12s | %-6s | %s |" % \
                         ("Field", "Type", "Quality", "Null", "Key"))
     
        print("|" + "-"*61 + "|")
        for column in self.show_columns_info():
            key = column[4]
            if key == "":
                key = "   "
            print("| %-16s | %-10s | %-12s | %-6s | %s |" % \
                         (column[0], column[1], column[2], column[3], key))

        print("|" + "_"*61 + "|")

    def has_column(self, column):
        """Function that returns a boolean of if a child Node exists.

        :param column:
            Input the name of a ColumnNode as a string.
        :type column: str
        :returns (child in children)
            Returns a boolean expression of if a ID matches any ColumnNode.
        :type (child in children): Boolean
        """
        return self.has_child(column) 

    def get_column(self, column):
        """Function that returns a connected ColumnNode.

        :param column:
            Input the name of a ColumnNode as a string.
        :type column: str
        :returns child_node
            Returns a child Node with a matching ID.
        :type child_node: Node
        """

        return self.get_child(column)

    def show_foreign_keys(self):
        """Function that returns a list representing Foreign Key ColumnNodes.
        
        :returns foreign_keys:
            Returns a list of Foreign Key ColumnNode names as strings.
        :type foreign_keys: List[str]
        """
        foreign_keys = []
        for column in self.children:
            if column != self.primary_key:
                if len(column.parents) > 1:
                    foreign_keys.append(column.id)

        return foreign_keys

    def get_foreign_keys(self):
        """Function that returns a list of connected Foreign Key ColumnNodes.

        :returns foreign_keys:
            Returns a list of attatched Foreign Key ColumnNodes.
        :type foreign_keys: List[ColumnNode]
        """
        foreign_keys = []
        for column in self.children:
            if column != self.primary_key:
                if len(column.parents) > 1:
                    foreign_keys.append(column)

        return foreign_keys

    def show_primary_key(self):
        """Function that returns the name of the Primary Key ColumnNode.

        :returns id:
            Returns the name of the primary key ColumnNode of the TableNode.
        :type id: str
        """
        return self.primary_key.id

class ColumnNode(Node):
    def __init__(self, id, parents=None, children=None, 
                 type=None, Null=None, key=None):
        super(ColumnNode, self).__init__(
                                    id, parents=parents, children=children)
        
        self.type = type
        self.null = Null
        self.key = key

        self.group = "Undefined"

    def create_table(self, table):
        """Function to create and link a new TableNode object as a parent.

        :param table:
            Input an ID for the new TableNode object as a string.
        :type table_id: str
        :returns table_node:
            Returns the created and linked TableNode object.
        :type table_node: TableNode
        """
        table_node = TableNode(table)
        table_node.children.append(self)
        self.parents.append(table_node)
    
        return table_node

    def add_table(self, table_node):
        """Function to link an existing TableNode object as a parent.

        :param table_node:
            Input a TableNode object.
        :type table_node: TableNode
        """
        self.add_parent(table_node)

    def remove_table(self, table):
        """Function that disconnects a connected TableNode.

        :param table:
            Input the TableNode to be removed.
        :type table: TableNode
        :returns parent_node:
            Returns the removed parent_node.
        :type parent_node: Node
        """
        return self.remove_parent(table)

    def get_type(self):
        """Function that returns the raw column type.

        :returns type:
            Returns the column type as a string.
        :type type: str
        """
        return self.type
   
    def parse_type(self):
        """Function that returns a truncated version of the column type.

        :returns type:
            Returns the a truncated version of the column type as a string.
        :type type: str
        """
        type = self.type.split("(")
        type = type[0].split(" ")[0]
       
        return type

    def show_info(self):
        """Function that returns a list of the info in the ColumnNode.

        :returns info:
            Returns a list of all the info in the ColumnNode as strings.
        :type info: List[str]
        """
        info = [self.id, self.parse_type(), self.group, self.null, self.key]
        return info

def print_database_tables(db_node):
    """Function to display information about a MySQL DatabaseTree.

    :param db_node:
        Input a DatabaseNode root of a DatabaseTree.
    :type db_node: DatabaseNode
    """
    for table in db_node.children:
        print(table.id + ":")
        table.print_columns_info()
        print("\n")
        

if __name__ == "__main__":
    sql_handle = MySQLConnectionHandler()
    sql_handle.database = input("Please enter database name: ")
    sql_handle.get_credentials()
    sql_handle.validate_credentials()
    db_tree = DatabaseTree(sql_handle)
    db_node = db_tree.get_root()
    print_database_tables(db_node)
