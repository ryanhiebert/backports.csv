2.0 (TBD)
+++++++++

* Drop support for Python 2.6 and 3.3.
  Python 3.3 is no longer supported by many build tools.
  We are also wanting to use OrderedDict,
  which is not in Python 2.6's stdlib.

1.0.7 (2019-03-10)
++++++++++++++++++

* Add tests to ``MANIFEST.in``.
  - thanks to @jayvdb for the pull request

1.0.6 (2018-05-22)
++++++++++++++++++

* Pass reader error messages along. (#28)
  This should help make errors more transparent.
  - thanks to @mpeteuil for the pull request

1.0.5 (2017-05-29)
++++++++++++++++++

* Fix bug in README example. (#22)
  - thanks to @tantale for the bug report
* Allow ``None`` as quotechar when using ``QUOTE_NONE``. (#23)
  - thanks to @thanatos for the bug report

1.0.4 (2017-02-17)
++++++++++++++++++

* Return write value from writerow. (#20)
  - thanks to @therg

1.0.3 (2017-01-23)
++++++++++++++++++

* Add LICENSE file (#18).

1.0.2 (2016-09-15)
++++++++++++++++++

* Avoid quoting any numeric types when using ``QUOTE_NONNUMERIC``.
  - thanks to @torfsen for the bug report

1.0.1 (2016-02-11)
++++++++++++++++++

* Better error messages for invalid dialects.
  - thanks to @kengruven for the bug report


1.0 (2016-02-11)
++++++++++++++++

* Initial Release
