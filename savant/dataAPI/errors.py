import helper
module_name = "data_api"
errors = {100: helper.geterrorDescription(module_name, 100, "data file does not exist")}

if __name__ == "__main__":
    print(errors)