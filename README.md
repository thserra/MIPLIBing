# MIPLIBing

MIPLIBing is a library for downloading MIP benchmark instances on demand.

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

According to the library chosen (see observations below), the `with_status` (or `without_status`) parameter can be any of:

* `Status.easy`
* `Status.hard`
* `Status.open`
* `Status.closed`

When `instance` is printed, all relevant information is displayed for the type of library used. The location of the downloaded instance in your machine is given by `instance.path`.

Here is the complete list of arguments for the `MIPLIBing` constructor:

Argument | Description | Default value | Observations
--- | --- | --- | ---
library | Problem library to be queried | Libraries.MIPLIB2017_Benchmark | Value should be in Libraries.
update_csv | If CSV file summarizing problem data should be updated, in case one already exists | False  | 
verbose | Prints the steps involved when getting instances | False  | If the chosen file_extension is not available for an instance, you will see the warnings with verbose.
local_directory | Define a local (or global) directory for caching data about the problem library and the instances | "MIPLIBing_cache" | 
file_extension |  | None | Cannot be used if library is Libraries.MIPLIB2017_Benchmark or Libraries.MIPLIB2017_Collection. When the file format is not available for some instance, a warning if shown if verbose is True and the local path of the instance has value None.

For the `get_instances` method, every argument has default value None and is only applicable if changed to another value. Here is the complete list of arguments:

Argument | Description | Observations
--- | --- | ---
instance_name | Exact name of instance | 
min_var | Minimum number of decision variables | 
max_var | Maximum number of decision variables | 
min_bin | Minimum number of binary decision variables | 
max_bin | Maximum number of binary decision variables | 
min_int | Minimum number of integer and non-binary decision variables | 
max_int | Maximum number of integer and non-binary decision variables | 
min_cont | Minimum number of continuous variables | 
max_cont | Maximum number of continuous variables | 
min_cons | Minimum number of constraints | 
max_cons | Maximum number of constraints | 
min_nz | Minimum number of nonzeroes | 
max_nz | Maximum number of nonzeroes | 
with_status | Only a specific status is allowed | Value should be in Status. If library is Libraries.MIPLIB2017_Benchmark or Libraries.MIPLIB2017_Collection, with_status can be Status.easy, Status.hard, or Status.open. If library is Libraries.MINLPLIB, with_status can be Status.closed (if 3 solvers found optimal solution or proven infeasibility) or Status.open (othewise). Not supported if library is Libraries.QPLIB.
without_status | Only a specific status is forbidden | Value should be in Status. If library is Libraries.MIPLIB2017_Benchmark or Libraries.MIPLIB2017_Collection, without_status can be Status.easy, Status.hard, or Status.open. If library is Libraries.MINLPLIB, without_status can be Status.closed (if 3 solvers found optimal solution or proven infeasibility) or Status.open (othewise). Not supported if library is Libraries.QPLIB.
min_sos | Minimum number of SOS constraints | Only supported if library is Libraries.MINLPLIB.
max_sos | Maximum number of SOS constraints | Only supported if library is Libraries.MINLPLIB.
min_semi | Minimum number of semicontinuity / semiintegrality constraints | Only supported if library is Libraries.MINLPLIB.
max_semi | Maximum number of semicontinuity / semiintegrality constraints | Only supported if library is Libraries.MINLPLIB.
problem_type | Only one type of problem is allowed | Only supported if library is Libraries.MINLPLIB. The problem type should be given as a string such as "MBNLP", "QP", "MBQP", "NLP", etc.
min_obj_density | Minimum objective density (%) in the quadratic part of the objective matrix  | Only supported if library is Libraries.QPLIB.
max_obj_density | Maximum objective density (%) in the quadratic part of the objective matrix  | Only supported if library is Libraries.QPLIB.
min_problematic_ev_density | Minimum density (%) of problematic eigenvalues in the quadratic part of the objective matrix  | Only supported if library is Libraries.QPLIB.
max_problematic_ev_density | Maximum density (%) of problematic eigenvalues in the quadratic part of the objective matrix  | Only supported if library is Libraries.QPLIB.
min_quadratic_cons | Minimum number of quadratic constraints | Only supported if library is Libraries.QPLIB.
max_quadratic_cons | Maximum number of quadratic constraints | Only supported if library is Libraries.QPLIB.
objective_type | Only one type of objective is allowed | Only supported if library is Libraries.QPLIB. The types should be given as a string among "L", "D", "C", and "Q" as described in the documentation for [QPLIB Problem Type](http://qplib.zib.de/doc.html#probtype).
variables_type | Only one type of variables is allowed | Only supported if library is Libraries.QPLIB. The types should be given as a string among "C", "B", "M", "I", and "G" as described in the documentation for [QPLIB Problem Type](http://qplib.zib.de/doc.html#probtype).
constraints_type | Only one type of constraints is allowed | Only supported if library is Libraries.QPLIB. The types should be given as a string among "N", "B", "L", "D", "C", and "Q" as described in the documentation for [QPLIB Problem Type](http://qplib.zib.de/doc.html#probtype).

## Citation

A manuscript the describes and contextualizes MIPLIBing is currently under review:

```
@unpublished{MIPLIBing,
    author = {Thiago Serra and Ryan J. O'Neil},
    title = {Seamless benchmarking of mathematical optimization problems and metadata extensions},
    year = {2020}
}
```

## License

MIPLIBing is distributed under the MIT license.
