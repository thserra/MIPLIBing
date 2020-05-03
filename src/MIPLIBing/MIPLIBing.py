from enum import Enum
import pandas as pd
import csv
import math
import numpy as np
import requests
import urllib.request as url_req
from urllib.error import HTTPError
import gzip as gz
import shutil as shu
import os


def Boolean_str(value):
    if value:
        return "Yes"
    elif value is None:
        return "Unknown"
    else:
        return "No"


class Instance:

    def __init__(self, name, problem_type, path, feasible, primal, dual, status, nb_var, nb_bin, nb_int, nb_cont, nb_const, nb_nz, sos = None, semi = None, obj_density=None, problematic_ev_density=None, quadratic_cons=None, objective_type=None, variables_type=None, constraints_type=None):
        self.name = name
        self.problem_type = problem_type
        self.path = path
        self.feasible = feasible
        self.primal = primal
        self.dual = dual
        self.status = status
        self.nb_var = nb_var
        self.nb_bin = nb_bin
        self.nb_int = nb_int
        self.nb_cont = nb_cont
        self.nb_const = nb_const
        self.nb_nz = nb_nz
        self.sos = sos
        self.semi = semi
        self.obj_density = obj_density
        self.problematic_ev_density = problematic_ev_density
        self.quadratic_cons = quadratic_cons
        self.objective_type = objective_type
        self.variables_type = variables_type
        self.constraints_type = constraints_type

    def __str__(self):

        type_str = ""
        if self.obj_density is None:
            type_str = "Type:                  \t" + self.problem_type + "\n"
        else:
            type_str = ("Objective Density:     \t" + str(self.obj_density) + "% \n" +
                        "Problematic EV Density:\t" + str(self.problematic_ev_density) + "% \n" +
                        "Objective Type:        \t" + self.objective_type + "\n" +
                        "Variables Type:        \t" + self.objective_type + "\n" +
                        "Constraints Type:      \t" + self.objective_type + "\n")

        extra_cons_str = ""
        if self.quadratic_cons is not None:
            extra_cons_str = "\t(" + str(self.quadratic_cons) + " quadratic)"
        elif self.sos is not None or self.semi is not None:
            extra_cons_str = "\t(" + str(self.sos) + " SOS)\t (" + str(self.semi) + " semi)"


        return ("Instance:              \t" + self.name + "\n" +
                type_str +
                "Local path:            \t" + str(self.path) + "\n" +
                "Feasible:              \t" + Boolean_str(self.feasible) + "\n" +
                "Primal Bound:          \t" + str(self.primal) + "\n" +
                "Dual Bound:            \t" + str(self.dual) + "\n" +
                "Status:                \t" + str(self.status) + "\n" +
                "Variables:             \t" + str(self.nb_var) + "\t(" + str(self.nb_bin) + " binary)\t (" + str(self.nb_int) + " integer)\t (" + str(self.nb_cont) + " continuous)" + "\n" +
                "Constraints:           \t" + str(self.nb_const) + extra_cons_str + "\n" +
                "Non-zeroes:            \t" + str(self.nb_nz) + "\n\n")


def parse_qplib_format(X):
    return X.split("(")[1].replace(",", "").replace(")", "") # Keep format names between () without ,


def parse_qplib_name(X):
    return X.split(" ")[0]


class Libraries(Enum):
    MIPLIB2017_Benchmark = 1
    MIPLIB2017_Collection = 2
    MINLPLIB = 3
    QPLIB = 4


class Status(Enum):
    easy = 1   # MIPLIB2017 only
    hard = 2   # MIPLIB2017 only
    open = 3   # MIPLIB2017; or MINLP if 3 solvers did not find optimal or proved infeasibility
    closed = 4 # MINLP otherwise


class MIPLIBing:

    def __init__(self, library = Libraries.MIPLIB2017_Benchmark, update_csv = False, verbose = False, local_directory = "MIPLIBing_cache", file_extension = None):
        self.verbose = verbose
        self.library = library

        assert type(library)==Libraries # Library should belong to the enumuration

        assert not ( library in [Libraries.MIPLIB2017_Benchmark, Libraries.MIPLIB2017_Collection] and file_extension != None ) # MIPLIB2017 does not require file extension

        if library == Libraries.MINLPLIB and file_extension == None: # Use default file extension for MINLPLIB
            file_extension = "gms"

        if library == Libraries.QPLIB and file_extension == None: # Use default file extension for QPLIB
            file_extension = "qplib"

        self.local_directory = local_directory+"/"+library.name+"/"

        if library in [Libraries.MIPLIB2017_Benchmark, Libraries.MIPLIB2017_Collection]:

            # Location of remote instances and local cache
            self.remote_directory = "http://miplib.zib.de/WebData/instances/"
            self.remote_file_ext = ".mps.gz"
            self.local_file_prefix = ""
            self.local_file_ext = ".mps"

            if library == Libraries.MIPLIB2017_Benchmark:
                # Remote location of benchmark set and local CSV file name
                self.instances_url = "http://miplib.zib.de/tag_benchmark.html"
                self.instances_csv_file = "MIPLIB2017_Benchmark.csv"
            else:
                # Remote location of collection set and local CSV file name
                self.instances_url = "http://miplib.zib.de/tag_collection.html"
                self.instances_csv_file = "MIPLIB2017_Collection.csv"

        elif library == Libraries.MINLPLIB:

            # Location of remote instances and local cache
            self.remote_directory = "http://www.minlplib.org/"+file_extension+"/"
            self.remote_file_ext = "."+file_extension
            self.local_file_prefix = ""
            self.local_file_ext = "."+file_extension

            # Remote location of MINLPLIB set and local CSV file
            self.instances_url = "http://www.minlplib.org/instances.html"
            self.instances_csv_file = "MINLPLIB.csv"

        elif library == Libraries.QPLIB:

            # Location of remote instances and local cache
            self.remote_directory = "http://qplib.zib.de/"+file_extension+"/QPLIB_"
            self.remote_file_ext = "."+file_extension
            self.local_file_prefix = "QPLIB_"
            self.local_file_ext = "."+file_extension

            # Remote location of QPLIB set and local CSV file
            self.instances_url = "http://qplib.zib.de/instances.html"
            self.solution_values_url = "http://qplib.zib.de/qplib.solu"
            self.instances_csv_file = "QPLIB.csv"


        # Path to local csv file
        self.instances_cvs_path = os.path.join(self.local_directory, self.instances_csv_file)

        # Create local cache directory if it does not exist
        if not os.path.exists(self.local_directory):
            os.makedirs(self.local_directory)

        # Check if local csv file exists
        csv_file_exists = os.path.isfile(self.instances_cvs_path)

        # Download csv file if required
        if update_csv or not csv_file_exists:
            if self.verbose:
                print("Downloading instance data to CSV file")

            df = pd.read_html(self.instances_url)[0]

            if library == Libraries.MIPLIB2017_Benchmark or library == Libraries.MIPLIB2017_Collection:
                df.rename(columns = {"Objective":"Primal"}, inplace = True)

            elif library == Libraries.MINLPLIB:
                df.rename(columns = {
                     df.columns[0]:"Instance",    # Name
                     df.columns[1]:"Formats",     # Formats(i)
                     df.columns[2]:"Type",        # Type(i)
                     df.columns[3]:"Convex",      # C(i)
                     df.columns[4]:"Variables",   # #Vars(i)
                     df.columns[5]:"Binaries",    # #BinVars(i)
                     df.columns[6]:"Integers",    # #IntVars(i)
                     df.columns[7]:"Constraints", # #Vars(i)
                     df.columns[8]:"SOS",         # #SOS(i)
                     df.columns[9]:"Semi",        # #Semi(i)
                     df.columns[10]:"Nonz.",      # #NZ(i)
                     df.columns[11]:"Status",     # S(i)
                     df.columns[12]:"Dual",       # Dual Bound(i)
                     df.columns[13]:"Primal",     # Primal Bound(i)
                     df.columns[14]:"Points"      # Points(i)
                    }, inplace = True)
                df.fillna({"Convex":"-","Binaries":0, "Integers":0, "SOS":0, "Semi":0, "Status":"-"}, inplace=True)
                df["Continuous"] = df["Variables"] - df["Binaries"] - df["Integers"]
                df["Convex"].replace({"-":"No", "✔":"Yes"}, inplace=True)
                df["Status"].replace({"-":"open", "✔":"closed"}, inplace=True)

            elif library == Libraries.QPLIB:
                df.drop(df.tail(1).index, inplace=True) # Removes last row (not an instance)
                df["Format"] = df["Instance"].apply(parse_qplib_format)
                df["Instance"] = df["Instance"].apply(parse_qplib_name)
                df.rename(columns = {
                             "Cvx":"Convex",
                             "O":"Objective type",
                             "V":"Variables type",
                             "C":"Constraints type",
                             "TotalVars.":"Variables",
                             "BinaryVars.":"Binaries",
                             "IntegerVars.":"Integers",
                             "TotalCons.":"Constraints",
                             "Quad.Cons.":"Quadratic constraints",
                             "Non-zeros":"Nonz."
                            }, inplace = True)
                df.fillna({"Binaries":0, "Integers":0}, inplace=True)
                df["Continuous"] = df["Variables"] - df["Binaries"] - df["Integers"]
                df["Convex"].replace({"-":"No", "✔":"Yes"}, inplace=True)
                df["Primal"] = np.nan

                content = requests.get(self.solution_values_url)
                lines = content.text.split("\n")
                for line in lines:
                    pieces = line.split()
                    if len(pieces)>0:
                        if pieces[0]=="=best=":
                            instance = pieces[1].split("_")[1]
                            value = float(pieces[2])
                            df.loc[df['Instance']==instance, 'Primal'] = value

            df.to_csv(self.instances_cvs_path, quoting=csv.QUOTE_NONNUMERIC)


    def get_instances(self, instance_name = None, min_var = None, max_var = None, min_bin = None, max_bin = None, min_int = None, max_int = None, min_cont = None, max_cont = None, min_cons = None, max_cons = None, min_nz = None, max_nz = None, with_status = None, without_status = None, min_sos = None, max_sos = None, min_semi = None, max_semi = None, problem_type = None, min_obj_density = None, max_obj_density = None, min_problematic_ev_density = None, max_problematic_ev_density = None, min_quadratic_cons = None, max_quadratic_cons = None, objective_type = None, variables_type = None, constraints_type = None):
        # Status can only be "easy", "hard", or "open" (MIPLIB) and "open" or "closed" (MINLPLIB)

        data = pd.read_csv(self.instances_cvs_path, dtype={'Instance': str})
        df = pd.DataFrame(data)

        if instance_name is not None:
            df = df[df['Instance'] == instance_name]

        if min_var is not None:
            df = df[df['Variables'] >= min_var]
        if max_var is not None:
            df = df[df['Variables'] <= max_var]

        if min_bin is not None:
            df = df[df['Binaries'] >= min_bin]
        if max_bin is not None:
            df = df[df['Binaries'] <= max_bin]

        if min_int is not None:
            df = df[df['Integers'] >= min_int]
        if max_int is not None:
            df = df[df['Integers'] <= max_int]

        if min_cont is not None:
            df = df[df['Continuous'] >= min_cont]
        if max_cont is not None:
            df = df[df['Continuous'] <= max_cont]

        if min_cons is not None:
            df = df[df['Constraints'] >= min_cons]
        if max_cons is not None:
            df = df[df['Constraints'] <= max_cons]

        if min_nz is not None:
            df = df[df['Nonz.'] >= min_nz]
        if max_nz is not None:
            df = df[df['Nonz.'] <= max_nz]

        if with_status is not None:
            assert self.library != Libraries.QPLIB # Cannot filter QPLIB by status
            assert not ( with_status.name == "closed" and self.library in [Libraries.MIPLIB2017_Benchmark, Libraries.MIPLIB2017_Collection])  # Status closed only applies to MINLPLIB
            assert not ( with_status.name in ["easy","hard"] and self.library == Libraries.MINLPLIB ) # Status easy and hard only applies to MIPLIB2017
            df = df[df['Status'] == with_status.name]
        if without_status is not None:
            assert self.library != Libraries.QPLIB # Cannot filter QPLIB by status
            assert not ( without_status.name == "closed" and self.library in [Libraries.MIPLIB2017_Benchmark, Libraries.MIPLIB2017_Collection])  # Status closed only applies to MINLPLIB
            assert not ( without_status.name in ["easy","hard"] and self.library == Libraries.MINLPLIB ) # Status easy and hard only applies to MIPLIB2017
            df = df[df['Status'] != without_status.name]

        if min_sos is not None:
            assert self.library == Libraries.MINLPLIB # Can only filter by SOS in MINLPLIB
            df = df[df['SOS'] >= min_sos]
        if max_sos is not None:
            assert self.library == Libraries.MINLPLIB # Can only filter by SOS in MINLPLIB
            df = df[df['SOS'] <= max_sos]

        if min_semi is not None:
            assert self.library == Libraries.MINLPLIB # Can only filter by Semi in MINLPLIB
            df = df[df['Semi'] >= min_semi]
        if max_semi is not None:
            assert self.library == Libraries.MINLPLIB # Can only filter by Semi in MINLPLIB
            df = df[df['Semi'] <= max_semi]

        if problem_type is not None:
            assert self.library == Libraries.MINLPLIB # Can only filter by problem type in MINLPLIB
            df = df[df['Type'] == problem_type]

        if min_obj_density is not None:
            assert self.library == Libraries.QPLIB # Can only filter by objective density in QPLIB
            df = df[df['Q0density'] >= min_obj_density]

        if max_obj_density is not None:
            assert self.library == Libraries.QPLIB # Can only filter by objective density in QPLIB
            df = df[df['Q0density'] <= max_obj_density]

        if min_problematic_ev_density is not None:
            assert self.library == Libraries.QPLIB # Can only filter by problematic eigenvalues in QPLIB
            df = df[df['Q0probl.ev'] >= min_problematic_ev_density]

        if max_problematic_ev_density is not None:
            assert self.library == Libraries.QPLIB # Can only filter by problematic eigenvalues in QPLIB
            df = df[df['Q0probl.ev'] <= max_problematic_ev_density]

        if min_quadratic_cons is not None:
            assert self.library == Libraries.QPLIB # Can only filter by quadratic constraints in QPLIB
            df = df[df['Quadratic constraints'] >= min_quadratic_cons]

        if max_quadratic_cons is not None:
            assert self.library == Libraries.QPLIB # Can only filter by quadratic constraints in QPLIB
            df = df[df['Quadratic constraints'] <= max_quadratic_cons]

        if objective_type is not None:
            assert self.library == Libraries.QPLIB # Can only filter by objective type in QPLIB
            df = df[df['Objective type'] == objective_type]

        if variables_type is not None:
            assert self.library == Libraries.QPLIB # Can only filter by variables type in QPLIB
            df = df[df['Variables type'] == variables_type]

        if constraints_type is not None:
            assert self.library == Libraries.QPLIB # Can only filter by constraints type in QPLIB
            df = df[df['Constraints type'] == constraints_type]

        instance_list = []

        for index, row in df.iterrows():
            instance = row['Instance']
            url = self.remote_directory + instance + self.remote_file_ext
            local = instance + self.remote_file_ext
            final = os.path.join(self.local_directory, self.local_file_prefix + instance + self.local_file_ext)

            if self.library != Libraries.QPLIB:
                status = row['Status']
            else:
                status = None

            primal = row['Primal']

            if self.library == Libraries.MINLPLIB:
                primal = float(primal)
                dual = float(row['Dual'])
                sos = int(row['SOS'])
                semi = int(row['Semi'])
                problem_type = row['Type']
            else:
                if self.library in [Libraries.MIPLIB2017_Benchmark, Libraries.MIPLIB2017_Collection]:
                    problem_type = "MILP"
                else:
                    problem_type = None
                dual = None
                sos = None
                semi = None

            if self.library in [Libraries.MIPLIB2017_Benchmark, Libraries.MIPLIB2017_Collection]:

                if primal == "Infeasible":
                    feasible = False
                    primal = None
                elif type(primal)==str: #Any numerical objective comes as a string
                    feasible = True
                    if status == "open": # Open problems have a trailing asterisk in the objective value
                        primal = float(primal[:-1]) # Removes trailing asterisk from objective
                    else: # Other problems have just the numerical value to be converted
                        primal = float(primal)
                elif math.isnan(primal): # Empty cells have a nan
                    feasible = None
                    primal = None
                else:
                    feasible = True
                    assert type(primal)==float

            elif self.library == Libraries.MINLPLIB:
                if math.isnan(primal):
                    primal = None
                    if dual == float("inf"):
                        feasible = False
                    else:
                        feasible = None
                else:
                    feasible = True

            elif self.library == Libraries.QPLIB:
                if math.isnan(primal):
                    primal = None
                    feasible = None
                else:
                    feasible = True

            nb_var = int(row['Variables'])
            nb_bin = int(row['Binaries'])
            nb_int = int(row['Integers'])
            nb_cont = int(row['Continuous'])
            nb_const = int(row['Constraints'])
            nb_nz= int(row['Nonz.'])

            if self.library == Libraries.QPLIB:
                obj_density = float(row['Q0density'])
                problematic_ev_density = float(row['Q0probl.ev'])
                quadratic_cons = int(row['Quadratic constraints'])
                objective_type = row['Objective type']
                variables_type = row['Variables type']
                constraints_type = row['Constraints type']
            else:
                obj_density = None
                problematic_ev_density = None
                quadratic_cons = None
                objective_type = None
                variables_type = None
                constraints_type = None

            new_instance = Instance(instance,problem_type,final,feasible,primal,dual,status,nb_var,nb_bin,nb_int,nb_cont,nb_const,nb_nz,sos=sos,semi=semi,obj_density=obj_density,problematic_ev_density=problematic_ev_density,quadratic_cons=quadratic_cons,objective_type=objective_type,variables_type=variables_type,constraints_type=constraints_type)
            instance_list.append(new_instance)

            if self.verbose:
                print("Instance",instance,end=": ")

            if os.path.isfile(final):
                if self.verbose:
                    print("Already downloaded")
            else:
                if self.verbose:
                    print("Downloading from",url)
                try:
                    url_req.urlretrieve(url, local)
                except HTTPError:
                    if self.verbose:
                        print("File",url,"does not exist, but you can download in the following formats:",row['Formats'])
                    final = None
                    new_instance.path = None

                if self.library in [Libraries.MIPLIB2017_Benchmark,Libraries.MIPLIB2017_Collection]:
                    with gz.open(local, 'rb') as f_in:
                        with open(final, 'wb') as f_out:
                            shu.copyfileobj(f_in, f_out)
                    os.remove(local)  # Removes downloaded mps.gz file after unzipping it

                elif final is not None:
                    shu.move(local, final)

        return instance_list
