

from apps import run_server
from classify import add_render_gen_args, render_gen


def main():
    run_server(add_render_gen_args, render_gen)
    

if __name__ == '__main__':
    main()
