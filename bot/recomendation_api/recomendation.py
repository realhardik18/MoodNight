import json
import os

valid_files=list(filter(lambda x:x.split('.')[-1]=='wav',os.listdir('audio')))
print(valid_files)