#!/usr/bin/env python3
from planet import create_app

app = create_app('config')

if __name__ == '__main__':
    app.run()
