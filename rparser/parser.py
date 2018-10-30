from rparser.template import Template
import itertools as it
import os
import re


class Parser:
    """class to parse R scripts into standalone Rmd files

    - Any line in R script which starts with "## " is considered a comment
        block and not an R code chunk in the Rmd
    - Requires Python 3.6.5 >=
    """
    def __init__(self, template, new_filename="test.Rmd"):

        # use a db template which injects data base connection R chunk  
        self.template = template 

        self.delimiter = "## "
        self.new_filename = new_filename

        self.template.rmd_content = self.parse_script()
        self.post_processing() # fix minor formatting problems following initial parsing 

    def create_comment_chunk(self, group):
        """remove delimiter from comments for final Rmd document """
        comments = self.parse_group(group)
        pattern = re.compile(f"^({self.delimiter})", re.MULTILINE)
        return "\n" + re.sub(pattern, "", comments)

    def create_rchunk(self, group):
        """surround code with triple tick marks for Rmd R chunks """
        code = self.parse_group(group)

        return f"\n\n```{{r}}\n{code}\n```\n"

    def parse_group(self, group): 
        """parse quotation marks out of strings to prep for final Rmd document """
        code = ""
        for text in group:
            code += text.strip('\"')
        return code

    def parse_script(self):
        """parse r script based off of delimiter

        There are two groups in the parsed R script we are looking for:
            - Comment Blocks
                + any line which starts with the set delimiter (## )
                + any blank line (newline in a string format)
            - Code Blocks
                + any line which is not a comment block is assumed to be a line of code

        Operations are used on groups to create R chunks or normal comment blocks
            in the final Rmd file. All lines which start with "## " are considered
            comments which will not be included in R chunks.
        """
        with open(self.template.template_path, "r") as f:
            new_rmd = []

            # divide file text into groups of code or comments
            for key, group in it.groupby(f, lambda line: line.startswith(self.delimiter)):
                if key: # comment block
                    comment_chunk = self.create_comment_chunk(list(group))
                    new_rmd.append(comment_chunk)

                    # the type of data depends on the template class: 
                    #   if there is a database_credentials.json file, then create a db_rchunk
                    #   otherwise, just create a generic R data chunk
                    read_data_comment = re.compile("## Read in Data") 
                    if re.search(read_data_comment, comment_chunk) and self.template.db_creds_path:
                        new_rmd.append(self.create_rchunk(
                            list(self.template.create_db_rchunk())
                        ))
                    elif re.search(read_data_comment, comment_chunk):
                        new_rmd.append(self.create_rchunk(
                            list(self.template.create_read_data_rchunk())
                        ))

                if not key: # code block
                    r_chunk = self.create_rchunk(list(group))
                    new_rmd.append(r_chunk)

            return new_rmd
    
    def post_processing(self): 
        """following parsed rscript, there are cases when multiple comment 
        lines can create an empty r chunk represented as: 
        ```{r}

        ```

        The regex matches any amount of new lines or whitespace before the 
          of the rchunk, matches any amount of the same between triple-tick 
          marks, and matches the last set of triple tick marks 
        """
        for i, group in enumerate(self.template.rmd_content):
            # remove empty rchunks from parsed rmd_content  
            pattern = re.compile("^\W*```{r}\n*\W```", re.MULTILINE)
            if re.match(pattern, group): 
                del self.template.rmd_content[i] 

    def write_to_new_rmd(self):
        """write to a new rmd file from an r script  """
        with open(self.new_filename, 'w') as f:
            for line in self.template.rmd_content:
                f.write(line)


def run_parser(new_filename="test.Rmd", db_credentials_path=""):
    t = Template(db_credentials_path=db_credentials_path)
    p = Parser(t, new_filename) 
    p.write_to_new_rmd()  
