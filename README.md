ckanext-more-facets
===================

Adds faceted search filters from a [tag vocabulary](http://ckan.readthedocs.org/en/latest/maintaining/tag-vocabularies.html)

Installation
=================

Activate virtualenv

```
$ source /usr/lib/ckan/default/bin/activate
```

From your activated virtualenv

```
(pyenv)$ pip install -e  git+https://github.com/mxabierto/ckanext-more-facets.git#egg=ckanext-more-facets
(pyenv)$ cd ckanext-more-facets
(pyenv)$ python setup.py develop
```

Edit your .ini file (usually at /etc/ckan/default/production.ini) with the following parameters

```
ckan.plugins = gov_type

```

Restart server

In your [development environment](http://docs.ckan.org/en/latest/maintaining/installing/install-from-source.html) set *debug = true* in your .ini file and run

```
(pyenv)$ paster serve /etc/ckan/default/development.ini
```

or in production:

```
(pyenv)$ /etc/init.d/httpd restart
