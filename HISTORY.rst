=======
History
=======

1.0.4 (2025-07-01)
------------------
* Don't use `six.create_bound_method` to attach `to_dict` to classes.
* Add `set_properties` methods.

1.0.3 (2025-05-25)
------------------

* Add graph/graph_db compatibility mapping.
* Bind 'to_dict' to property classes, so rather than being short and ambiguous
  or long and obnoxious, it can just be called like a normal method.
* Fix 'fields' being removed as a named parameter in NamedTuple.
* Drop Python 2.7 support.

1.0.2 (2020-06-16)
------------------

* Limit 'typing' requirement to Python < 3.3 to not break builds with
  pyproject.toml.

1.0.1 (2018-08-02)
------------------

* Restrict to only supported py2neo versions with environment-based override for
  testing with later versions.

1.0.0 (2018-08-01)
------------------

* First release on PyPI.
