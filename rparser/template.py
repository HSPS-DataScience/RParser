from inspect import cleandoc
import json 
import os


class Template: 
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
        return cleandoc(content)

    def create_read_data_rchunk(self): 
        content = f'''
                   read_in_data <- handle_exceptions %decorates% function() {{
                       x <- # INSERT YOUR DATA HERE
                   }}
                   data <- read_in_data()
                   '''
        return cleandoc(content)
