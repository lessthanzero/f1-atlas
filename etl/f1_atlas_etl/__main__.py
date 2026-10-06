from .build import app
import sys

if len(sys.argv) == 1:
    sys.argv.append("build")
app()
