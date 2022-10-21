class Query:
    def __init__(self,file_location):
        f=open(file_location)
        self.query_string=f.read()
        f.close()

    def getQuery(self,mappings):
        q_string=self.query_string
        for key in mappings:
            q_string=q_string.replace(key,formatInjection(mappings[key]))
        return q_string

def formatInjection(value):
    if type(value)==int:
        return str(value)
    if type(value)==str:
        return f'"{value}"'
    return str(value)