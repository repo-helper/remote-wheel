# stdlib
import os
import zipfile
from typing import Type, Union

# 3rd party
import handy_archives
import pytest
import remotezip
from apeye import URL
from coincidence.params import param
from coincidence.regressions import AdvancedDataRegressionFixture, AdvancedFileRegressionFixture
from domdf_python_tools.paths import PathPlus
from packaging.version import Version
from shippinglabel.checksum import get_sha256_hash

# this package
from remote_wheel import RemoteWheelDistribution, RemoteZipFile

wheel_urls = PathPlus(__file__).parent.joinpath("wheel_urls.json").load_json()

wheels = pytest.mark.parametrize("url", [param(w[2], id=f"{w[0]}-{w[1]}") for w in wheel_urls])

url_type = pytest.mark.parametrize(
		"url_type",
		[param(str, id="str"), param(URL, id="URL")],
		)


class TestRemoteWheelDistribution:

	@url_type
	@wheels
	def test_distribution(
			self,
			url: str,
			url_type: Type[Union[str, URL]],
			advanced_data_regression: AdvancedDataRegressionFixture,
			):
		wd = RemoteWheelDistribution.from_url(url_type(url))

		advanced_data_regression.check({
				"name": wd.name,
				"url": wd.url,
				"repr": repr(wd),
				"version": str(wd.version),
				"wheel": list(wd.get_wheel().items()),
				"metadata": list(wd.get_metadata().items()),
				"entry_points": wd.get_entry_points(),
				"has_license": wd.has_file("LICENSE"),
				})

		assert isinstance(wd.wheel_zip, zipfile.ZipFile)
		assert isinstance(wd.wheel_zip, handy_archives.ZipFile)
		assert isinstance(wd.wheel_zip, RemoteZipFile)
		assert isinstance(wd.wheel_zip, remotezip.RemoteZip)

	@wheels
	def test_get_record(self, url: str):

		distro = RemoteWheelDistribution.from_url(url)
		record = distro.get_record()
		assert record is not None
		assert len(record)  # pylint: disable=len-as-condition

		for file in record:
			if file.hash is None:
				assert file.name == "RECORD"
			else:
				with distro.wheel_zip.open(os.fspath(file)) as fp:
					assert get_sha256_hash(fp).hexdigest() == file.hash.hexdigest()

			if file.size is not None:
				assert distro.wheel_zip.getinfo(os.fspath(file)).file_size == file.size

			assert file.distro is None

			with pytest.raises(ValueError, match="Cannot read files with 'self.distro = None'"):
				file.read_bytes()

	def test_remotezip(self, advanced_file_regression: AdvancedFileRegressionFixture):
		wd = RemoteWheelDistribution.from_url(
				"https://files.pythonhosted.org/packages/94/e2/"
				"0a5630e43ca0b21ca891ec3a697bdb98a25663e27ebd1079ab55e8c68e72/"
				"domdf_python_tools-2.9.1-py3-none-any.whl"
				"#sha256=ad1058fa0769a68808c2ed44909222508edf6f26ec3a36f91f86b6d654c58474",
				)

		assert isinstance(wd.wheel_zip, zipfile.ZipFile)
		assert isinstance(wd.wheel_zip, handy_archives.ZipFile)
		assert isinstance(wd.wheel_zip, RemoteZipFile)

		advanced_file_regression.check(
				wd.wheel_zip.read("domdf_python_tools/__init__.py").decode("UTF-8"), extension="._py"
				)

		with wd:
			advanced_file_regression.check(
					wd.wheel_zip.read("domdf_python_tools/__init__.py").decode("UTF-8"), extension="._py"
					)

		assert wd.wheel_zip.fp is None

	def test_remotezip_github_pages(self, advanced_file_regression: AdvancedFileRegressionFixture):
		wd = RemoteWheelDistribution.from_url(
				"https://repo-helper.uk/simple503/pydash/pydash-5.0.0-py3-none-any.whl"
				"#sha256=0d87f879a3df4ad9389ab6d63c69eea078517d41541ddd5744cfcff3396e8543",
				)

		assert isinstance(wd.wheel_zip, zipfile.ZipFile)
		assert isinstance(wd.wheel_zip, handy_archives.ZipFile)
		assert isinstance(wd.wheel_zip, RemoteZipFile)

		advanced_file_regression.check(wd.wheel_zip.read("pydash/__init__.py").decode("UTF-8"), extension="._py")

		assert isinstance(wd, RemoteWheelDistribution)

		with wd:
			advanced_file_regression.check(
					wd.wheel_zip.read("pydash/__init__.py").decode("UTF-8"), extension="._py"
					)

		assert wd.wheel_zip.fp is None

	def test_remotezip_ionos(self):

		with pytest.raises(
				remotezip.RangeNotSupported,
				match="The server at remote-wheel-test.repo-helper.uk doesn't support range requests",
				):
			wd = RemoteWheelDistribution.from_url(
					"http://remote-wheel-test.repo-helper.uk/pydash-5.0.0-py3-none-any.whl",
					)

	def test_remotezip_auth(self, advanced_file_regression: AdvancedFileRegressionFixture):

		url = "http://remote-wheel-test.repo-helper.uk/toml-0.10.2-py2.py3-none-any.whl"
		wheel_zip = RemoteZipFile(url, initial_buffer_size=100, auth=("user", "password"))
		wd = RemoteWheelDistribution("toml", Version("0.10.2"), url, wheel_zip)

		assert isinstance(wd.wheel_zip, zipfile.ZipFile)
		assert isinstance(wd.wheel_zip, handy_archives.ZipFile)
		assert isinstance(wd.wheel_zip, RemoteZipFile)

		advanced_file_regression.check(wd.wheel_zip.read("toml/__init__.py").decode("UTF-8"), extension="._py")

		assert isinstance(wd, RemoteWheelDistribution)

		with wd:
			advanced_file_regression.check(wd.wheel_zip.read("toml/__init__.py").decode("UTF-8"), extension="._py")

		assert wd.wheel_zip.fp is None

		# Again to check the auth requirement works
		with pytest.raises(remotezip.RemoteIOError, match=f"^401 Client Error: Unauthorized for url: {url}$"):
			RemoteZipFile(url, initial_buffer_size=100)
