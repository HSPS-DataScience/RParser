from inspect import cleandoc
import json 
import os


class Template: 
    """Captures the notion of a template by holding the path to the default template
    and maintaining rchunks which need to be inserted into the template with dynamic 
    values. I.e. create_db_rchunk() requires a path to the user's db_credentials.json
    file. This is only possible through Python handling the rchunk as opposed to putting 
    the chunk in template.R
    
    """
    def __init__(self, db_credentials_path=""): 
        try: 
            # create an absolute path to the template, otherwise pathing
            #   is relative to the module base directory and generally fails
            #   to find file
            self.template_path = os.path.join(os.path.dirname(__file__), "R/template.R")
            self.db_creds_path = db_credentials_path 

        except IOError: 
            print("Template not found")

        # final chunks of rmd 
        self.rmd_content = []

    def create_db_rchunk(self): 
        """create database connection r chunk with a filepath to 
        the user's credentials.json file
        """
        content = f'''
                   read_in_data_from_db <- handle_exceptions %decorates% function() {{
                       library(rjson)
                       db_creds <- fromJSON(file = "{self.db_creds_path}")
                       con <- DBI::dbConnect(odbc::odbc(),
                                             Driver = db_creds$driver,
                                             Server = db_creds$server,
                                             Database =  db_creds$db_name,
                                             UID =  db_creds$userID,
                                             PWD =  db_creds$password,
                                             Port = db_creds$port,
                                             Trusted_Connection = "yes")
                       res <- dbSendQuery(con, paste("SELECT * FROM ", db_creds$table_name))
                   }}
                   data <- read_in_data_from_db()
                   '''
        # cleandoc removes extra tab and whitespacing created by multi-line pythong string 
        return cleandoc(content)

    def create_read_data_rchunk(self):
        """create r chunk for reading in generic data from r session """ 
        content = '''
                  read_in_data <- handle_exceptions %decorates% function() {
                      x <- # INSERT YOUR DATA HERE
                  }
                  data <- read_in_data()
                  '''
        # cleandoc removes extra tab and whitespacing created by multi-line pythong string
        return cleandoc(content)
