"""
setup.py file for experiments on the competition server
"""
from setuptools import setup

install_requirements = (
    [
        "wheel",
        "palaestrai-mosaik==0.5.2",
        #  "palaestrai-mosaik",
        "pandas>=1.2.4,<=1.3.5",
        "numpy>=1.22.0",
        "pysimmods",
        "palaestrai@git+https://gitlab.com/arl2/palaestrai@448-alternative-database-without-python-objects",
        # "palaestrai"
        "xlrd",
        "mosaik-api==3.0.0",
        "palaestrai-agents@git+https://gitlab.com/arl2/harl.git@dc73d8044c6815bbe13ebc20b36f6ecb507d1430",
        "midas-mosaik@git+ssh://git@git.swl.informatik.uni-oldenburg.de:7999/pgasc2122/midas.git@development",
        # "midas-mosaik"
        "mango-library@git+https://gitlab.com/mango-agents/mango-library@Winzent-ethics_module_refactor",
        "pandapower==2.9.0",
	"mango-agents==0.4.0",
	"requests==2.28.1"
    ],
)

setup(
    name="pgasc",
    version="0.0.1",
    install_requires=install_requirements,
    include_package_data=True,
)
