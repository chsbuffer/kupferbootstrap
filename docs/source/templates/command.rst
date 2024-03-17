{% set reduced_name = fullname.split(".", 1)[-1] if fullname.startswith("kupferbootstrap.") else fullname %}
.. title: {{reduced_name}}


.. currentmodule:: {{ fullname }}
.. click:: {% if fullname == 'main' %}kupferbootstrap.main:cli{% else %}{{fullname}}.cli:cmd_{{reduced_name}}{% endif %}
  :prog: kupferbootstrap {{reduced_name}}
  :nested: full

