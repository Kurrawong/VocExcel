# VocExcel

Another Excel-to-RDF converter for SKOS vocabs, but one that:

* uses fixed templates to keep it simple
* meets particular SKOS profile outcomes ([VocPub](https://linked.data.gov.au/def/vocpub))
* is under active development, production use, and is commercially supported

An online version of VocExcel is available at https://tools.kurrawong.ai/tools/vocexcel.

## Creating vocabularies

The process to create an RDF vocabulary from an Excel template is:

1. Fill in a copy of an Excel template
2. Process it
   * Using one of the options, and export an RDF file
   * You can choose to validate the RDF produced while processing

### Templates

The template files in this repository’s **vocexcel/templates/** folder are to be used to create vocabularies. The templates hopefully contain all the information needed to understand how to fill them in.

Use one Excel workbook per vocabulary.

### Latest Template

* ***vocexcel/templates/VocExcel-template-090.xlsx***

Unless you have a good reason to do something different, please use the latest version of the template.

Older templates still convert, so if you’ve used one and like it, keep using it.

### Examples

Example filled-in templates versions are given in the `tests/data/` folder. Just ensure you’re looking at examples prefixed with the same template version you are after, e.g. 0.8.10 = 0812.xlsx.

As per _semantic versioning_, a template of 0.8.5 will work with 0.8.10.

## Processing

To process an Excel template, you will need to either:

* run the VocExcel Python script, or
* use an online tool
  * for example https://tools.kurrawong.ai/tools/vocexcel

The Python script can also run as a Python module, i.e. within a larger Python workflow.

### Installation

VocExcel uses [uv](https://github.com/astral-sh/uv) package manager.

You can install VocExcel from PyPI, the Python package index: https://pypi.org/project/vocexcel

Or you can clone this repository and install VocExcel’s dependencies using `uv` or a similar tool, using the provided _pyproject.toml_ file.

### Running

#### As a command line script

The Python script `convert.py` in the `vocexcel/` directory can be run on Windows/Unix/Linux/Mac systems like this:

```
python convert.py some-excel-file.xlsx
```

If you install this program using a Python packaging tool such as uv, then it will run like this:

```
vocexel some-excel-file.xlsx
```

An example, using one of the test data files to convert from Excel to RDF:

```
python convert.py tests/data/0812.xlsx
```

To convert the other way - RDF to Excel - from with you’ll get a v0.8.x template result:

```
python convert.py tests/data/085_rdf.ttl
```

The command line argument options can be found by typing:

```
python convert.py -h
```

They are:

```
usage: vocexcel [-h] [-i] [-o OUTPUTFILE] [input_file]

positional arguments:
  input_file            The Excel file to convert to a SKOS vocabulary in RDF or an RDF file to convert to an Excel file. (default: None)

options:
  -h, --help            show this help message and exit
  -i, --info            The version and other info of this instance of VocExcel. (default: False)
  -o OUTPUTFILE, --outputfile OUTPUTFILE
                        An optionally-provided output file path. If not provided, output from Excel-> RDF is to standard out and RDF->Excel is input file with .xlsx file ending. (default: None)
```

#### As a Python library

The _convert.py_ file uses the functions `excel_to_rdf()` and `rdf_to_excel()` to do conversions, so you can directly them in other Python programs by importing them like:

```
from vocexcel.convert import excel_to_rdf, rdf_to_excel
from pathlib import Path

rdf_to_excel(Path(".") / "path" / "to" / "vocab-file.xlsx")

# or

excel_to_rdf(Path(".") / "path" / "to" / "vocab-file.ttl")
```

#### Online

[KurrawongAI](https://kurrawong.ai) maintains an online VocExcel tool at https://tools.kurrawong.ai/tools/vocexcel

## License

This code is licensed using the BSD 3-Clause. See the _LICENSE_ for the deed. Note that Excel is property of Microsoft.

## Contact

***Commercial support***:\
https://docs.kurrawong.ai/products/tools/vocexcel/ \
info@kurrawong.ai

**Lead Developer**:\
***Nicholas Car***\
**Data Architect**\
[KurrawongAI](https://kurrawong.ai)\
nick@kurrawong.ai

## Release Procedure

* update version number in pyprojects.toml
* update ref to latest template, if changed, in README.md
* Git commit all changes
  * push to GitHub: `git push`
* add a Git tag matching the version number
  * push tags to GitHub: `git push --tags`
* build: `uv build`
* publish to PyPI: `uv publis -u __token__ -p {TOKEN}`
