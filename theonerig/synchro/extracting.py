# AUTOGENERATED! DO NOT EDIT! File to edit: 11_synchro.extracting.ipynb (unless otherwise specified).

__all__ = ['get_QDSpy_logs', 'QDSpy_log', 'Stimulus', 'unpack_stim_npy', 'extract_spyking_circus_results']

# Cell
import numpy as np
import datetime
import os, glob
import csv

from .io import *
from ..utils import *

def get_QDSpy_logs(log_dir):
    log_names = glob.glob(os.path.join(log_dir,'[0-9]*.log'))
#     log_names = [os.path.basename(log_name) for log_name in log_names]
    qdspy_logs = [QDSpy_log(log_name) for log_name in log_names]
    for qdspy_log in qdspy_logs:
        qdspy_log.find_stimuli()
    return qdspy_logs

class QDSpy_log:
    def __init__(self, log_path):
        self.log_path = log_path
        self.stimuli = []
        self.comments = []

    def _extract_data(self, data_line):
        data = data_line[data_line.find('{')+1:data_line.find('}')]
        data_splitted = data.split(',')
        data_dict = {}
        for data in data_splitted:
            ind = data.find("'")
            if type(data[data.find(":")+2:]) is str:
                data_dict[data[ind+1:data.find("'",ind+1)]] = data[data.find(":")+2:][1:-1]
            else:
                data_dict[data[ind+1:data.find("'",ind+1)]] = data[data.find(":")+2:]
        return data_dict

    def _extract_time(self,data_line):
        line = '%s' % data_line
        year = int(line[0:4])
        month = int(line[4:6])
        day = int(line[6:8])
        hour =int(line[9:11])
        minute = int(line[11:13])
        second = int(line[13:15])
        result = datetime.datetime(year,month,day,hour,minute,second)
        return result

    def _extract_dropped(self,data_line):
        ind = data_line.find('#')
        index_frame = int(data_line[ind+1:data_line.find(' ',ind)])
        ind = data_line.find('was')
        delay = float(data_line[ind:].split(" ")[1])
        return (index_frame, delay)

    def __repr__(self):
        return "\n".join([str(stim) for stim in self.stimuli])

    @property
    def n_stim(self):
        return len(self.stimuli)

    @property
    def stim_names(self):
        return [stim.name for stim in self.stimuli]

    def find_stimuli(self):
        """Find the stimuli in the log file and return the list of the stimuli
        found by this object."""
        with open(self.log_path, 'r', encoding="ISO-8859-1") as log_file:
            for line in log_file:
                if "DATA" in line:
                    data_juice = self._extract_data(line)
                    if 'stimState' in data_juice.keys():
                        if data_juice['stimState'] == "STARTED" :
                            curr_stim = Stimulus(self._extract_time(line))
                            curr_stim.set_parameters(data_juice)
                            self.stimuli.append(curr_stim)
                            stimulus_ON = True
                        elif data_juice['stimState'] == "FINISHED" or data_juice['stimState'] == "ABORTED":
                            curr_stim.is_aborted = data_juice['stimState'] == "ABORTED"
                            curr_stim.stop_time = self._extract_time(line)
                            stimulus_ON = False

                    elif 'userComment' in data_juice.keys():
                        pass
                        #print("userComment, use it to bind logs to records")
                    elif stimulus_ON: #Information on stimulus parameters
                        curr_stim.set_parameters(data_juice)
    #                elif 'probeX' in data_juice.keys():
            #            print("Probe center not implemented yet")
                if "WARNING" in line and "dt of frame" and stimulus_ON:
                    curr_stim.frame_drop.append(self._extract_dropped(line))
        return self.stimuli

class Stimulus:
    """Stimulus object containing information about it's presentation.
    """
    def __init__(self,start):
        self.start_time = start
        self.stop_time = None
        self.parameters = {}
        self.frame_drop = []
        self.name = "NoName"

        self.is_recorded = False
        self.non_matching = False
        self.is_aborted = False

        self.md5 = None
        #self.compiled_id = None  # ! This is not a reliable value after storage if DB change
        self.barcode = None

        self.first_frame_idx = None

        self.intensity = None
        self.marker    = None
        self.shader    = None
        self.theor_intensity = None
        self.theor_marker    = None
        self.theor_shader    = None

        self.frame_error_idx = [] #The errors detected by comparing the signals

    def set_parameters(self, parameters):
        self.parameters.update(parameters)
        if "_sName" in parameters.keys():
            self.name = parameters["_sName"]
        if "stimMD5" in parameters.keys():
            self.md5 = parameters["stimMD5"]

    def __str__(self):
        return "%s %s at %s" %(self.name+" "*(24-len(self.name)),self.md5,self.start_time)

    def __repr__(self):
        return self.__str__()

# Cell
def unpack_stim_npy(npy_dir, md5_hash):
    inten  = np.load(glob.glob(os.path.join(npy_dir, "*_intensities_"+md5_hash+".npy"))[0])
    marker = np.load(glob.glob(os.path.join(npy_dir, "*_marker_"+md5_hash+".npy"))[0])

    tmp = glob.glob(os.path.join(npy_dir, "*_shader_"+md5_hash+".npy"))
    shader, unpack_shader = None, None
    if len(tmp)!=0:
        shader        = np.load(tmp[0])
        unpack_shader = np.empty((np.sum(marker[:,0]), *shader.shape[1:]))

    unpack_inten  = np.empty((np.sum(marker[:,0]), *inten.shape[1:]))
    unpack_marker = np.empty(np.sum(marker[:,0]))

    cursor = 0
    for i, n_frame in enumerate(marker[:,0]):
        unpack_inten[cursor:cursor+n_frame] = inten[i]
        unpack_marker[cursor:cursor+n_frame] = marker[i, 1]
        if shader is not None:
            unpack_shader[cursor:cursor+n_frame] = shader[i]
        cursor += n_frame

    if shader is not None:
        return unpack_inten, unpack_marker, unpack_shader

    return unpack_inten, unpack_marker

# Cell
def extract_spyking_circus_results(dir_, record_basename):
    phy_dir  = os.path.join(dir_,record_basename+"/"+record_basename+".GUI")
    phy_dict = phy_results_dict(phy_dir)

    good_clusters = []
    with open(os.path.join(phy_dir,'cluster_group.tsv'), 'r') as tsvfile:
        spamreader = csv.reader(tsvfile, delimiter='\t', quotechar='|')
        for i,row in enumerate(spamreader):
            if row[1] == "good":
                good_clusters.append(int(row[0]))
    good_clusters = np.array(good_clusters)

    phy_dict["good_clusters"] = good_clusters

    return phy_dict