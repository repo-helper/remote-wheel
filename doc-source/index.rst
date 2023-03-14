=============
remote-wheel
=============

.. start short_desc

.. documentation-summary::
	:meta:

.. end short_desc

.. start shields

.. only:: html

	.. list-table::
		:stub-columns: 1
		:widths: 10 90

		* - Docs
		  - |docs| |docs_check|
		* - Tests
		  - |actions_linux| |actions_windows| |actions_macos| |coveralls|
		* - PyPI
		  - |pypi-version| |supported-versions| |supported-implementations| |wheel|
		* - Activity
		  - |commits-latest| |commits-since| |maintained| |pypi-downloads|
		* - QA
		  - |codefactor| |actions_flake8| |actions_mypy|
		* - Other
		  - |license| |language| |requires|

	.. |docs| rtfd-shield::
		:project: remote-wheel
		:alt: Documentation Build Status

	.. |docs_check| actions-shield::
		:workflow: Docs Check
		:alt: Docs Check Status

	.. |actions_linux| actions-shield::
		:workflow: Linux
		:alt: Linux Test Status

	.. |actions_windows| actions-shield::
		:workflow: Windows
		:alt: Windows Test Status

	.. |actions_macos| actions-shield::
		:workflow: macOS
		:alt: macOS Test Status

	.. |actions_flake8| actions-shield::
		:workflow: Flake8
		:alt: Flake8 Status

	.. |actions_mypy| actions-shield::
		:workflow: mypy
		:alt: mypy status

	.. |requires| image:: https://dependency-dash.repo-helper.uk/github/repo-helper/remote-wheel/badge.svg
		:target: https://dependency-dash.repo-helper.uk/github/repo-helper/remote-wheel/
		:alt: Requirements Status

	.. |coveralls| coveralls-shield::
		:alt: Coverage

	.. |codefactor| codefactor-shield::
		:alt: CodeFactor Grade

	.. |pypi-version| pypi-shield::
		:project: remote-wheel
		:version:
		:alt: PyPI - Package Version

	.. |supported-versions| pypi-shield::
		:project: remote-wheel
		:py-versions:
		:alt: PyPI - Supported Python Versions

	.. |supported-implementations| pypi-shield::
		:project: remote-wheel
		:implementations:
		:alt: PyPI - Supported Implementations

	.. |wheel| pypi-shield::
		:project: remote-wheel
		:wheel:
		:alt: PyPI - Wheel

	.. |license| github-shield::
		:license:
		:alt: License

	.. |language| github-shield::
		:top-language:
		:alt: GitHub top language

	.. |commits-since| github-shield::
		:commits-since: v0.2.0
		:alt: GitHub commits since tagged version

	.. |commits-latest| github-shield::
		:last-commit:
		:alt: GitHub last commit

	.. |maintained| maintained-shield:: 2023
		:alt: Maintenance

	.. |pypi-downloads| pypi-shield::
		:project: remote-wheel
		:downloads: month
		:alt: PyPI - Downloads

.. end shields

Installation
---------------

.. start installation

.. installation:: remote-wheel
	:pypi:
	:github:

.. end installation


Examples
----------


.. code-block:: pycon

	>>> from shippinglabel.pypi import get_wheel_url
	>>> from remote_wheel import RemoteWheelDistribution
	>>> with RemoteWheelDistribution.from_url(get_wheel_url("whey", "0.0.17", strict=True)) as wheel:
	... 	wheel
	... 	wheel.url
	... 	wheel.get_wheel()
	... 	wheel.get_metadata().keys()[:10]
	<RemoteWheelDistribution('whey', <Version('0.0.17')>)>
	'https://files.pythonhosted.org/packages/e4/40/094399239108e774aa0192e168ba34fab982202db86352b05fc1aeb71444/whey-0.0.17-py3-none-any.whl'
	<MetadataMapping({'Wheel-Version': '1.0', 'Generator': 'bdist_wheel (0.36.2)', 'Root-Is-Purelib': 'true', 'Tag': 'py3-none-any'})>
	['Metadata-Version', 'Name', 'Version', 'Summary', 'Home-page', 'Author', 'Author-email', 'License', 'Project-URL', 'Project-URL']


.. code-block:: pycon

	>>> from pypi_simple import PyPISimple
	>>> from remote_wheel import RemoteWheelDistribution
	>>> with PyPISimple() as client:
	...     requests_page = client.get_project_page('requests')
	>>> pkg = requests_page.packages[-2]
	>>> pkg.url
	'https://files.pythonhosted.org/packages/92/96/144f70b972a9c0eabbd4391ef93ccd49d0f2747f4f6a2a2738e99e5adc65/requests-2.26.0-py2.py3-none-any.whl#sha256=6c1246513ecd5ecd4528a0906f910e8f0f9c6b8ec72030dc9fd154dc1a6efd24'
	>>> with RemoteWheelDistribution.from_url(pkg.url) as wheel:
	... 	wheel
	... 	wheel.get_wheel()
	... 	wheel.get_metadata().keys()[:10]
	<RemoteWheelDistribution('requests', <Version('2.26.0')>)>
	<MetadataMapping({'Wheel-Version': '1.0', 'Generator': 'bdist_wheel (0.36.2)', 'Root-Is-Purelib': 'true', 'Tag': 'py2-none-any', 'Tag': 'py3-none-any'})>
	['Metadata-Version', 'Name', 'Version', 'Summary', 'Home-page', 'Author', 'Author-email', 'License', 'Project-URL', 'Project-URL']



Contents
-----------

.. html-section::


.. toctree::
	:hidden:

	Home<self>

.. toctree::
	:maxdepth: 3

	api
	Source
	license

.. sidebar-links::
	:caption: Links
	:github:
	:pypi: highlight

	Contributing Guide <https://contributing.repo-helper.uk>

.. start links

.. only:: html

	View the :ref:`Function Index <genindex>` or browse the `Source Code <_modules/index.html>`__.

	:github:repo:`Browse the GitHub Repository <repo-helper/remote-wheel>`

.. end links
