import os, sys, getopt
import pickle


def main(argv):
    file = ''
    try:
        opts, args = getopt.getopt(argv, "hf:", ["file="])
    except getopt.GetoptError:
      print('open_pickle.py -f <filename>')
      sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('open_pickle.py -f <filename>')
            sys.exit()
        elif opt in ("-f", "--file"):
            file = arg
    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, file)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            content = pickle.load(f)
            f.close()
        print(content)
    else:
        print("File not found.")


if __name__ == '__main__':
    main(sys.argv[1:])