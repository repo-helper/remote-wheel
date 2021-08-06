# stdlib
import sys
from typing import Any, List, Tuple, get_type_hints

# 3rd party
from sphinx.application import Sphinx
from sphinx.ext.autodoc import ObjectMembers
from sphinx_toolbox.more_autodoc import autonamedtuple
from sphinx_toolbox.utils import allow_subclass_add


class NamedTupleDocumenter(autonamedtuple.NamedTupleDocumenter):

	def filter_members(
			self,
			members: ObjectMembers,
			want_all: bool,
			) -> List[Tuple[str, Any, bool]]:
		"""
		Filter the list of members to always include ``__new__`` if it has a different signature to the tuple.

		:param members:
		:param want_all:
		"""

		all_hints = get_type_hints(self.object)
		class_hints = {k: all_hints[k] for k in self.object._fields if k in all_hints}

		# TODO: need a better way to partially resolve type hints, and warn about failures
		new_hints = get_type_hints(
				self.object.__new__,
				globalns=sys.modules[self.object.__module__].__dict__,
				localns=self.object.__dict__,
				)

		# Stock NamedTuples don't have these, but customised collections.namedtuple or hand-rolled classes may
		if "cls" in new_hints:
			new_hints.pop("cls")
		if "return" in new_hints:
			new_hints.pop("return")

		if class_hints and new_hints and class_hints != new_hints:
			#: __new__ has a different signature or different annotations

			def unskip_new(app, what, name, obj, skip, options):
				if name == "__new__":
					return False
				return None

			listener_id = self.env.app.connect("autodoc-skip-member", unskip_new)
			members_ = super(autonamedtuple.NamedTupleDocumenter, self).filter_members(members, want_all)
			self.env.app.disconnect(listener_id)
			return members_

		else:
			return super(autonamedtuple.NamedTupleDocumenter, self).filter_members(members, want_all)


def setup(app: Sphinx):
	app.setup_extension("sphinx_toolbox.more_autodoc.autonamedtuple")
	allow_subclass_add(app, NamedTupleDocumenter)
	return {"parallel_read_safe": True}
