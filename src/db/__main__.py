from .tui import ConsoleInterface

def main():
    """Точка входа."""
    interface = ConsoleInterface()
    interface.run()

if __name__ == "__main__":
    main()