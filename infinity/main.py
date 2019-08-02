import click

@click.option('-c', '--config', default='./infinty.yml', help="Path to the infinity config file")
def cli():
    print("Hello world")