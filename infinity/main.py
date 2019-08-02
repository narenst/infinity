import click


@click.command()
@click.option('-c', '--config', default='./infinty.yml', help="Path to the infinity config file")
def cli(config):
    print(f"Hello world {config}")


if __name__ == '__main__':
    cli()