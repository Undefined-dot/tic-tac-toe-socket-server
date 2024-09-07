from typing import List, Tuple
from pydantic import BaseModel
import json

#  class qui represente les données recues par la requete de verification d'un user
class FormData(BaseModel):
    userToken: str
    expireTokenTime: int
    gameId: str
        

# classe qui permet de definir un objet JSON
class JSON_Oject:
    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4)
