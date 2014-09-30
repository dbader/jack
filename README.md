# jack

A command line tool for time-based queries on log files.

## How to install

    pip install jack
    
To run jack, `cd` to a directory with log files (`.log` or `.log.gz` extension) and run something like this:

    jack 8:15am to 8:20am
    jack 8:15am to 8:20am PDT
    jack 16:30 to 16:45
    jack May 1st 16:30 to May 1st 16:45
    jack 2014-03-01 8:15am to 2014-03-01 8:20am PDT
    jack yesterday to today
    
## How to create and ship a change

* Mark your change in a branch off `master` and submit a pull-request on GitHub. Ping @dbader to review it.

#### Testing
* Test the package locally and make sure it installs cleanly and works via `pip install -e .` (in the project root).

#### Releasing
* Create a git tag for the release: 
    * `git tag 0.0.1 -m "The best release so far"`
    * `git push --tags origin master`
* `python setup.py sdist upload -r pypi`

## Roadmap

* Turn this into a `pip install`able package
* Add usage / nice errors for the CLI
* Add unit tests
* Set up TravisCI continuous integration

## Changelog

* `0.1.0`: First working PyPI release.

## Glossary
(todo)

## Where to get help
Talk to [@dbader](https://twitter.com/dbader).
