from parsing import Parsing


if __name__ == "__main__":
    try:
        parser = Parsing()
        parser.process_file("maps/easy/03_basic_capacity.txt")
        print(parser.zones)
        print(parser.connections)
    except ValueError as e:
        print(e)
    except FileNotFoundError:
        print("Error: the given file does not exist")
    except IsADirectoryError:
        print("Error: the given path is a directory")
    except PermissionError:
        print("Error: file does not have the necessary permission")
