# stdlib
from typing import List, Tuple

# 3rd party
from domdf_python_tools.paths import PathPlus
from first import first
from pypi_simple import PyPISimple

wheel_urls: List[Tuple[str, str, str]] = []

with PyPISimple() as client:
	for project, version in [
		("alabaster", "0.7.12",),
	("apeye", "1.0.1"),
	("appdirs", "1.4.4",),
	("Babel", "2.9.1",),
	("buildbot_gitea", "1.7.0"),
	("cawdrey", "0.4.2"),
	("certifi", "2021.5.30",),
	("chardet", "4.0.0",),
	("default_values", "0.5.0"),
	("docutils", "0.16",),
	("dom_toml", "0.5.0"),
	("domdf_python_tools", "0.9.2"),
	("domdf_python_tools", "0.10.0"),
	("domdf_python_tools", "1.7.0"),
	("domdf_python_tools", "2.0.0"),
	("domdf_python_tools", "2.1.0"),
	("domdf_python_tools", "2.5.2"),
	("domdf_python_tools", "2.6.1"),
	("domdf_python_tools", "2.9.1"),
	("idna", "2.10",),
	("imagesize", "1.2.0",),
	("importlib_metadata", "4.5.0"),
	("Jinja2", "3.0.1"),
	("MarkupSafe", "2.0.1"),
	("natsort", "7.1.1"),
	("packaging", "20.9",),
	("PyAthena", "2.3.0"),
	("pydash", "5.0.0"),
	("Pygments", "2.9.0"),
	("pyparsing", "2.4.7",),
	("pytz", "2021.1",),
	("requests", "2.25.1",),
	("setuptools", "57.0.0"),
	("shippinglabel", "0.15.0"),
	("snowballstemmer", "2.1.0",),
	("Sphinx", "3.5.4"),
	("sphinxcontrib_applehelp", "1.0.2",),
	("sphinxcontrib_devhelp", "1.0.2",),
	("sphinxcontrib_htmlhelp", "2.0.0",),
	("sphinxcontrib_jsmath", "1.0.1",),
	("sphinxcontrib_qthelp", "1.0.3",),
	("sphinxcontrib_serializinghtml", "1.1.5",),
	("toml", "0.10.2",),
	("trove_classifiers", "2021.4.5"),
	("typing_extensions", "3.10.0.0"),
	("urllib3", "1.26.5",),
	("wheel_filename", "1.3.0"),
	("zipp", "3.4.1"),

		]:
		project_page = client.get_project_page(project)
		pkg = first(project_page.packages, key=lambda p: p.version == version and ".whl" in p.url)
		wheel_urls.append((project, version, pkg.url))

PathPlus("tests/wheel_urls.json").dump_json(wheel_urls, indent=2)
