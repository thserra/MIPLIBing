import pandas as pd
import urllib.request as url_req
import gzip as gz
import shutil as shu
import os

from selenium import webdriver

class Instance:
    
    def __init__(self, name, path, objective, status, nb_var, nb_bin, nb_int, nb_cont, nb_const, nb_nz):
        self.name = name
        self.path = path
        self.objective = objective
        self.status = status
        self.nb_var = nb_var
        self.nb_bin = nb_bin
        self.nb_int = nb_int
        self.nb_cont = nb_cont
        self.nb_const = nb_const
        self.nb_nz= nb_nz
        
    def __str__(self):
        return ("Instance:   \t" + self.name + "\n" +
                "Local path: \t" + self.path + "\n" +
                "Objective:  \t" + str(self.objective) + "\n" +
                "Status:     \t" + self.status + "\n" +
                "Variables:  \t" + str(self.nb_var) + "\t(" + str(self.nb_bin) + " binary)\t (" + str(self.nb_int) + " integer)\t (" + str(self.nb_cont) + " continuous)" + "\n" + 
                "Constraints:\t" + str(self.nb_const) + "\n" +
                "Non-zeroes: \t" + str(self.nb_nz) + "\n\n")

        
class MIPLIB2017:
    
    def __init__(self, benchmark_only = False, update_csv = False, verbose = False):
        self.verbose = verbose
        
        # Remote location of collection set and CSV file name
        self.collection_url = "http://miplib.zib.de/tag_collection.html"
        self.collection_csv_file = "The Collection Set.csv"
        
        # Remote location of benchmark set and CSV file name
        self.benchmark_url = "http://miplib.zib.de/tag_benchmark.html"
        self.benchmark_csv_file = "The Benchmark Set.csv"
        
        # Location of remote instances and local cache
        self.remote_directory = "http://miplib.zib.de/WebData/instances/"
        self.remote_file_ext = ".mps.gz"
        self.local_directory = "MIPLIBing_cache"
        self.local_file_ext = ".mps"
        
        # Check which type of instances to use
        if benchmark_only:
            self.instances_url = self.benchmark_url
            self.instances_csv_file = self.benchmark_csv_file
        else:
            self.instances_url = self.collection_url
            self.instances_csv_file = self.collection_csv_file
        
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
                print("Downloading CSV file")
            
            # Configure download preferences of a Firefox session
            profile = webdriver.FirefoxProfile()
            profile.set_preference('browser.download.folderList', 2) # Use last download folder
            profile.set_preference('browser.download.manager.showWhenStarting', False)
            profile.set_preference('browser.download.dir', os.path.join(os.getcwd(), self.local_directory)) # Set last download folder
            profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')

            browser = webdriver.Firefox(profile)
            browser.get(self.instances_url)
            
            # Find button to download csv file
            ids = browser.find_elements_by_xpath('//*[@class]')
            for ii in ids:
                if ii.get_attribute('class') == "dt-button buttons-csv buttons-html5":
                    
                    # If local copy exists, remove it before downloading new one
                    if csv_file_exists:
                        if self.verbose:
                            print("Removing existing CSV file first")
                        os.remove(self.instances_cvs_path)
                    
                    # Download csv file
                    ii.click()
                    break

            browser.close()
            
            
    def get_instances(self, min_var = None, max_var = None, min_bin = None, max_bin = None, min_int = None, max_int = None, min_cont = None, max_cont = None, min_cons = None, max_cons = None, min_nz = None, max_nz = None, with_status = None, without_status = None):
        # Status can only be "easy", "hard", or "open"
        
        data = pd.read_csv(self.instances_cvs_path)
        df = pd.DataFrame(data)

        if min_var is not None:
            df = df[df['Variables  Var.'] >= min_var]
        if max_var is not None:
            df = df[df['Variables  Var.'] <= max_var]
            
        if min_bin is not None:
            df = df[df['Binaries  Bin.'] >= min_bin]
        if max_bin is not None:
            df = df[df['Binaries  Bin.'] <= max_bin]
            
        if min_int is not None:
            df = df[df['Integers  Int.'] >= min_int]
        if max_int is not None:
            df = df[df['Integers  Int.'] <= max_int]
            
        if min_cont is not None:
            df = df[df['Continuous  Con.'] >= min_cont]
        if max_cont is not None:
            df = df[df['Continuous  Con.'] <= max_cont]
        
        if min_cons is not None:
            df = df[df['Constraints  Con.'] >= min_cons]
        if max_cons is not None:
            df = df[df['Constraints  Con.'] <= max_cons]

        if min_nz is not None:
            df = df[df['Nonz.  Non.'] >= min_nz]
        if max_nz is not None:
            df = df[df['Nonz.  Non.'] <= max_nz]

        if with_status is not None:
            df = df[df['Status  Sta.'] == with_status]            
        if without_status is not None:
            df = df[df['Status  Sta.'] != without_status]

        instance_list = []
            
        for index, row in df.iterrows():
            instance = row['Instance  Ins.']
            url = self.remote_directory + instance + self.remote_file_ext
            local = instance + self.remote_file_ext
            final = os.path.join(self.local_directory, instance + self.local_file_ext)
            
            objective = row['Objective  Obj.']
            status = row['Status  Sta.']
            nb_var = row['Variables  Var.']
            nb_bin = row['Binaries  Bin.']
            nb_int = row['Integers  Int.']
            nb_cont = row['Continuous  Con.']
            nb_const = row['Constraints  Con.']
            nb_nz= row['Nonz.  Non.']
            
            new_instance = Instance(instance,final,objective,status,nb_var,nb_bin,nb_int,nb_cont,nb_const,nb_nz)
            instance_list.append(new_instance)
            
            if self.verbose:
                print("Instance",instance,end=": ")
    
            if os.path.isfile(final):
                if self.verbose:
                    print("Already downloaded")
            else:
                if self.verbose:
                    print("Downloading from",url)
                url_req.urlretrieve(url, local)
                with gz.open(local, 'rb') as f_in:
                    with open(final, 'wb') as f_out:
                        shu.copyfileobj(f_in, f_out)
                os.remove(local)  # Removes downloaded mps.gz file after unzipping it
                
        return instance_list
        
