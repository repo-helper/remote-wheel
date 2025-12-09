#!/usr/bin/env python3
#
#  __init__.py
"""
Access files from a remote wheel.

.. _HTTP range requests: https://developer.mozilla.org/en-US/docs/Web/HTTP/Range_requests
.. _GET: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/GET
"""
#
#  Copyright © 2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Some documentation from
#  https://github.com/jwodder/pypi-simple
#  Copyright (c) 2018-2020 John Thorvald Wodder II
#  MIT Licensed
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
import csv
import os
import pathlib
import platform
from typing import IO, Any, List, Mapping, Tuple, Type, TypeVar, Union, cast
from urllib.parse import urlparse

# 3rd party
import handy_archives
import remotezip
import requests
import urllib3
from apeye.requests_url import RequestsURL
from apeye.url import URL
from dist_meta import wheel
from dist_meta._utils import _parse_wheel_filename
from dist_meta.distributions import DistributionType, WheelDistribution
from dist_meta.metadata_mapping import MetadataMapping
from dist_meta.record import FileHash, RecordEntry
from packaging.version import Version

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2021 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.2.0"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = ["RemoteWheelDistribution", "RemoteZipFile", "USER_AGENT"]

_RWD = TypeVar("_RWD", bound="RemoteWheelDistribution")

#: The User-Agent header used for requests; not used when the user provides their own session object.
USER_AGENT: str = ' '.join([
		f"remote-wheel/{__version__} (https://github.com/repo-helper/remote-wheel)",
		f"requests/{requests.__version__}",
		f"{platform.python_implementation()}/{platform.python_version()}",
		])


class _WheelFetcher(remotezip.RemoteFetcher):

	def _request(self, kwargs: Mapping) -> Tuple[Any, requests.models.CaseInsensitiveDict]:
		url: RequestsURL = self._url  # type: ignore[attr-defined]
		res: requests.Response = url.get(stream=True, **kwargs)
		res.raise_for_status()

		if "Content-Range" not in res.headers:
			raise remotezip.RangeNotSupported(f"The server at {url.netloc} doesn't support range requests")
		if "Content-Encoding" in res.headers:
			raise NotImplementedError(f"The server at {url.netloc} returned a 'Content-Encoding' header.")

		return res.raw, res.headers["Content-Range"]


class RemoteZipFile(remotezip.RemoteZip, handy_archives.ZipFile):
	"""
	Subclass of :class:`handy_archives.ZipFile` for accessing zip files using `HTTP Range requests`_.

	If necessary, login/authentication details for the repository can be specified
	at initialization by setting the ``auth`` parameter to either a ``(username, password)``
	pair or `another authentication object accepted by requests`_.

	A :class:`~.RemoteZipFile` instance can be used as a context manager
	that will automatically close the underlying session on exit.

	:param url: The URL of the remote zipfile.
	:param auth: Optional login/authentication details for the repository;
		either a ``(username, password)`` pair or `another authentication object accepted by requests`_.
	:param initial_buffer_size: The buffer size to use for the first request.

	Other keyword arguments taken by :class:`zipfile.ZipFile` are accepted, except ``mode``.

	.. _another authentication object accepted by requests: https://requests.readthedocs.io/en/master/user/authentication/

	"""  # noqa: RST306

	def __init__(
			self,
			url: Union[str, URL],
			auth: Any = None,
			initial_buffer_size: int = 500,
			**kwargs,
			):

		if isinstance(url, RequestsURL):
			# Use the session from the RequestsURL object if the argument was not provided
			self.url = url
		else:
			self.url = RequestsURL(url)
			self.url.session = requests.Session()
			self.url.session.headers["User-Agent"] = USER_AGENT

		self.url.session.headers["Accept-Encoding"] = urllib3.util.SKIP_HEADER

		if auth is not None:
			self.url.session.auth = auth

		if "mode" in kwargs:
			raise TypeError("__init__() got an unexpected keyword argument 'mode'")

		fetcher = _WheelFetcher(
				self.url,  # type: ignore[arg-type]
				self.url.session,
				support_suffix_range=False,
				)
		rio: IO[bytes] = cast(IO[bytes], remotezip.RemoteIO(fetcher.fetch, initial_buffer_size))
		handy_archives.ZipFile.__init__(self, rio, **kwargs)
		rio.set_position_to_size(self._get_position_to_size())  # type: ignore[attr-defined]

	def close(self) -> None:  # noqa: D102
		self.url.session.close()
		super().close()


class RemoteWheelDistribution(DistributionType, Tuple[str, Version, str, handy_archives.ZipFile]):
	"""
	Represents a Python distribution in :pep:`wheel <427>` form, accessed over HTTP.

	:param name: The name of the distribution.

	A :class:`~.RemoteWheelDistribution` can be used as a contextmanager,
	which will close the underlying :class:`~.RemoteZipFile` when exiting
	the :keyword:`with` block.
	"""  # noqa: RST399

	#: The name of the distribution. No normalization is performed.
	name: str

	#: The version number of the distribution.
	version: Version

	#: The URL of the ``.whl`` file. The remote server MUST support `HTTP range requests`_.
	url: str

	#: The opened zip file.
	wheel_zip: handy_archives.ZipFile

	__slots__ = ()
	_fields = ("name", "version", "url", "wheel_zip")

	def __new__(
			cls: Type[_RWD],
			name: str,
			version: Version,
			url: str,
			wheel_zip: handy_archives.ZipFile,
			) -> _RWD:
		"""
		Construct a new :class:`~.RemoteWheelDistribution` object.

		:rtype: :class:`~.RemoteWheelDistribution`
		"""

		# If this is super().__new__ it breaks on PyPy
		return tuple.__new__(cls, (name, version, url, wheel_zip))

	@classmethod
	def from_url(cls: Type[_RWD], url: Union[str, URL], **kwargs) -> _RWD:
		r"""
		Construct a :class:`~.RemoteWheelDistribution` from a URL to the ``.whl`` file.

		:param url:
		:param \*\*kwargs: Additional keyword arguments passed to :class:`~.RemoteZipFile`.

		.. note::

			The remote server MUST support `HTTP range requests`_.

			If the server lacks support, you should instead download the wheel with a standard GET_
			request and use the :class:`dist_meta.distributions.WheelDistribution` class.

		.. latex:clearpage::

		.. note::

			If the remote server requires authentication (e.g. a private package repository),
			construct a :class:`~.RemoteZipFile` -- passing the authentication information to its constructor --
			then create a :class:`~.RemoteWheelDistribution` manually:

			.. code-block:: python

				from remote_wheel import RemoteZipFile, RemoteWheelDistribution
				url = "https://my.private.repository/wheels/toml-0.10.2-py2.py3-none-any.whl"
				wheel_zip = RemoteZipFile(url, initial_buffer_size=100, auth=("user", "password"))
				wheel = RemoteWheelDistribution("toml", Version("0.10.2"), url, wheel_zip)

		:rtype: :class:`~.RemoteWheelDistribution`
		"""  # noqa: RST306

		url = str(url)

		scheme, netloc, path, params, query, fragment = urlparse(url)

		filename = pathlib.PurePosixPath(os.path.basename(path))
		name, version, *_ = _parse_wheel_filename(filename)
		wheel_zip = RemoteZipFile(url, initial_buffer_size=100, **kwargs)

		return cls(name, version, url, wheel_zip)

	#: Optimiser skips these
	def __enter__(self: _RWD) -> _RWD:  # pragma: no cover
		return self

	#: Optimiser skips these
	def __exit__(self, exc_type, exc_val, exc_tb):  # pragma: no cover
		self.wheel_zip.close()

	def read_file(self, filename: str) -> str:
		"""
		Read a file from the ``*.dist-info`` directory and return its content.

		:param filename:
		"""

		return WheelDistribution.read_file(
				self,  # type: ignore[arg-type]
				filename,
				)

	def has_file(self, filename: str) -> bool:
		"""
		Returns whether the ``*.dist-info`` directory contains a file named ``filename``.

		:param filename:
		"""

		return WheelDistribution.has_file(
				self,  # type: ignore[arg-type]
				filename,
				)

	def get_wheel(self) -> MetadataMapping:
		"""
		Returns the content of the ``*.dist-info/WHEEL`` file.

		:raises FileNotFoundError: if the file does not exist.
		"""

		return wheel.loads(self.read_file("WHEEL"))

	def get_record(self) -> List[RecordEntry]:
		"""
		Returns the parsed content of the ``*.dist-info/RECORD`` file, or :py:obj:`None` if the file does not exist.

		:returns: A :class:`dist_meta.record.RecordEntry` object for each line in the record
			(i.e. each file in the distribution).
			This includes files in the ``*.dist-info`` directory.

		:raises FileNotFoundError: if the file does not exist.
		"""

		content = self.read_file("RECORD").splitlines()
		output = []

		for line in csv.reader(content):
			name, hash_, size_str, *_ = line
			entry = RecordEntry(
					name,
					hash=FileHash.from_string(hash_) if hash_ else None,
					size=int(size_str) if size_str else None,
					)
			output.append(entry)

		return output
