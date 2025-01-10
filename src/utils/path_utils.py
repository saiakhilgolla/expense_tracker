import os
from os import listdir
from os.path import isfile, join



def get_file_list(path:str) -> list[str]:
	file_paths = [join(path, file) for file in listdir(path) if isfile(join(path, file))]
	return(file_paths)

def validate_file_list(file_paths:list[str]) -> list[str]:
	if len(file_paths) == 0:
		raise Warning("No files found in the given directory")
	else:
		return(file_paths)

TODO: # ADD A FUNCTION TO MOVE FILES THAT ARE PROCESSED INTO A DIFFERENT "PROCESSED" DIRECTORY
