import helper
module_name = "data_api"
EC_NOT_ERROR=0
EC_END_OF_DATA=100
EC_File_not_exist = 500
errors = {EC_END_OF_DATA: helper.geterrorDescription(module_name, EC_END_OF_DATA, "The end of data file"),\
    EC_File_not_exist: helper.geterrorDescription(module_name, EC_File_not_exist, "data file does not exist"),\
          }

if __name__ == "__main__":
    print(errors)