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
from MIPLIBing import Status

mip = MIPLIBing(library = Libraries.MIPLIB2017_Collection, verbose = True)
instances = mip.get_instances(with_status = Status.open, max_var=1000)
print()
for instance in instances:
    print(instance)
```

The `library` parameter can be any of:

* `Libraries.MIPLIB2017_Benchmark`
* `Libraries.MIPLIB2017_Collection`
* `Libraries.MINLPLIB`
* `Libraries.QPLIB`

The `with_status` (or `without_status`) parameter can be any of:

* `Status.easy`
* `Status.hard`
* `Status.open`
* `Status.closed`

Here is the complete list of arguments for the 'MIPLIBing' constructor:

Argument | Description | Default value | Observations
--- | --- | --- | ---
library | Problem library to be queried | Libraries.MIPLIB2017_Benchmark | Value should be in Libraries.
update_csv | If CSV file summarizing problem data should be updated, in case one already exists | False  | 
verbose | Prints the steps involved when getting instances | False  | If the chosen file_extension is not available for an instance, you will see the warnings with verbose.
local_directory | Define a local (or global) directory for caching data about the problem library and the instances. | "MIPLIBing_cache" | 
file_extension |  | None | Cannot be used if library is Libraries.MIPLIB2017_Benchmark or Libraries.MIPLIB2017_Collection. When the file format is not available for some instance, a warning if shown if verbose is True and the local path of the instance has value None.


## License

MIPLIBing is distributed under the MIT license.
