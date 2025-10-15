History
=======

2.0.0 (2025-10-08)
------------------

-   Add support for py2neo v2021.2.4.
-   Drop support for py2neo v1.6. Source referring to v1 has been retained for
    reference and are not tested and don't work.
-   Drop support for Python versions other than 3.6 and 3.8; really only v2 on
    3.6 and 3.8 and v2021 on 3.8.
-   Split `py2neo_compat.py2neo_compat` and `py2neo_compat.schema` into
    separate modules for the different versions supported.
-   Remove `Graph.cypher` namespace for `execute` and `stream`. Replace with
    `cypher_execute` and `cypher_stream` the first argument is Graph instead.
-   Modernize build system, partly. We are still using down-revs of
    `setuptools` but at least have moved the data into `pyproject.toml`.

1.0.4 (2025-07-01)
------------------

-   Don\'t use [six.create_bound_method]{.title-ref} to attach
    [to_dict]{.title-ref} to classes.
-   Add [set_properties]{.title-ref} methods.

1.0.3 (2025-05-25)
------------------

-   Add graph/graph_db compatibility mapping.
-   Bind \'to_dict\' to property classes, so rather than being short and
    ambiguous or long and obnoxious, it can just be called like a normal
    method.
-   Fix \'fields\' being removed as a named parameter in NamedTuple.
-   Drop Python 2.7 support.

1.0.2 (2020-06-16)
------------------

-   Limit \'typing\' requirement to Python \< 3.3 to not break builds
    with pyproject.toml.

1.0.1 (2018-08-02)
------------------

-   Restrict to only supported py2neo versions with environment-based
    override for testing with later versions.

1.0.0 (2018-08-01)
------------------

-   First release on PyPI.
