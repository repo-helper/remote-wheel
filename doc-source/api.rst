=================
API Reference
=================

.. autosummary-widths:: 53/100

.. automodule:: remote_wheel
	:member-order: bysource
	:no-members:
	:autosummary-members:

.. autonamedtuple:: remote_wheel.RemoteWheelDistribution
	:no-show-inheritance:

.. latex:clearpage::

.. autoclass:: remote_wheel.RemoteZipFile
	:no-show-inheritance:
	:exclude-members: close

.. autovariable:: remote_wheel.USER_AGENT
	:no-value:

	The structure of the User-Agent is:

	.. code-block:: python

		' '.join([
				f"pypi-json/{__version__} (https://github.com/repo-helper/pypi-json)",
				f"requests/{requests.__version__}",
				f"{platform.python_implementation()}/{platform.python_version()}",
				#  ^^^ e.g. CPython                   ^^^ e.g. 3.8.10
				])

	This global attribute should not be changed by other code.
