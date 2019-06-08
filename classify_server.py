

from apps import run_server
from classify import render_gen


def main():
    run_server(render_gen)
    

if __name__ == '__main__':
    main()
