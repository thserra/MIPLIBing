# MIPLIBing

MIPLIBing is a library for downloading MIP benchmark instances.

## Usage

Install the library using `python`. Python 3 is required.

```bash
$ python setup.py install
```

You can now download MIP benchmark data and instances in Python scripts.

```python
from MIPLIBing import MIPLIBing
from MIPLIBing import Libraries

mip = MIPLIBing(library = Libraries.QPLIB, verbose = True, file_extension="lp")
instances = mip.get_instances(min_var=100, max_var=100)
print()
for instance in instances:
    print(instance)
```

Here is another example using MIPLIB, where the file extension is not required.
```python
from MIPLIBing import MIPLIBing
from MIPLIBing import Libraries

mip = MIPLIBing(library = Libraries.MIPLIB2017_Benchmark)
instances = mip.get_instances(min_var=100, max_var=100)
print()
for instance in instances:
    print(instance)
```

The `library` parameter can be any of:

* `Libraries.MIPLIB2017_Benchmark`
* `Libraries.MIPLIB2017_Collection`
* `Libraries.MINLPLIB`
* `Libraries.QPLIB`

## License

MIPLIBing is distributed under the MIT license.
