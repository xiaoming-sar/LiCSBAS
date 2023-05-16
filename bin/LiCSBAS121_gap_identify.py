"""
select the period with the most IFGs and exlude IFGs located in the minor gaps 
Run this in the root folder full of frame folders such as 114A_04994_131313

-create new files: 
bad_gaps_ifg.txt (IFGs), 
gap_info_after12.txt (gap inforamtions)

-crete new figure: 
network121_nobad_nogap_1.png (network with bad IFGs and gaps marked in red)
network121_nobad_nogap.png (clean network)

"""

import os
import numpy as np
import LiCSBAS_io_lib as io_lib
import LiCSBAS_tools_lib as tools_lib
import LiCSBAS_plot_lib as plot_lib
import pandas as pd
import LiCSBAS_inv_lib as inv_lib
from datetime import datetime
import argparse

parser = argparse.ArgumentParser(description='run this under folder full with frame folders like 114A_04994_131313')
args = parser.parse_args()

def main():
    def gap_identify(ifgdir, tsadir):
            
        #%% Read date and network information
        ### Get all ifgdates in ifgdir
        # ifgdir = 'GEOCml_mask'
        # tsadir = 'TS_GEOCml'

        # tsadir = os.path.abspath(tsadir)
        infodir = os.path.join(tsadir, 'info')
        netdir = os.path.join(tsadir, 'network')
        gap_infofile = os.path.join(infodir, 'gap_info_after12.txt')
        bad_gapsfile = os.path.join(infodir, 'bad_gaps_ifg.txt')

        bad_ifg11file = os.path.join(infodir, '11bad_ifg.txt')
        bad_ifg12file = os.path.join(infodir, '12bad_ifg.txt')


        ifgdates_all = tools_lib.get_ifgdates(ifgdir)
        imdates_all = tools_lib.ifgdates2imdates(ifgdates_all)
    

        ### Read bad_ifg11 and 12
        bad_ifg11 = io_lib.read_ifg_list(bad_ifg11file)
        bad_ifg12 = io_lib.read_ifg_list(bad_ifg12file)
        bad_ifg_all = list(set(bad_ifg11+bad_ifg12))
        bad_ifg_all.sort()

        ### Remove bad ifgs and images from list
        ifgdates = list(set(ifgdates_all)-set(bad_ifg_all))
        ifgdates.sort()

        imdates = tools_lib.ifgdates2imdates(ifgdates)

        n_im = len(imdates)

        unw_useful = pd.DataFrame({'ifgdates':ifgdates})
        if len(unw_useful) >=10:
                # Identify gaps over the selected complete ifg 
                G = inv_lib.make_sb_matrix(unw_useful['ifgdates']) #find the gap in the initial selected dates --> unw_useful_dates 
                date_gap = np.where(G.sum(axis=0)==0)[0] #gap index over dates
                
                unw_index = [] ### convert gaps in dates to gaps in ifgs
                for i in range(len(date_gap)):
                    date_position = date_gap[i]
                    gap_initail = unw_useful[unw_useful['ifgdates'].str.contains(imdates[date_position])]
                    ifg_index = unw_useful[unw_useful.ifgdates == gap_initail.ifgdates.iloc[-1]].index.tolist() #label of row index --> loc
                    unw_index.append(ifg_index[0])
                
                unw_useful_start = unw_useful.index[0] #.loc index for the start
                unw_useful_end   = unw_useful.index[-1]#.loc index for the

        #  an list to dinguish gaps over ifgs
        index_gap = np.r_[unw_useful_start, unw_index, unw_useful_end]  #gaps in ifgs,access by using .loc 

        #select the period with the most IFGs 
        if len(index_gap)!=0:
            ifg_gap = []
            # for ix_gap in ixs_inc_gap:
            for i in range(len(index_gap)-1):
                # ifg_gap.append(index_gap[i+1] - index_gap[i]) #num of ifg in each gap period
                ifg_gap.append(len(unw_useful.loc[index_gap[i]:index_gap[i+1],:]))
            index = ifg_gap.index(max(ifg_gap)) #period between gaps with most ifgs
            final_useful_unw = unw_useful.loc[index_gap[index]+1:index_gap[index+1],:]
        else:
            final_useful_unw = unw_useful

        bad_gaps_ifg = list(set(ifgdates)-set(final_useful_unw['ifgdates']))
        #save bad_gaps_ifg to bad_gapsfile
        with open(bad_gapsfile, "w") as f:
            for i in range(len(bad_gaps_ifg)):
                print(bad_gaps_ifg[i], file=f)

        #update the bad_ifg_all list by adding bad_gaps_ifg
        bad_ifg_all = list(set(bad_ifg_all+bad_gaps_ifg))
        bad_ifg_all.sort()

        #the date for used gaps
        final_imdates = tools_lib.ifgdates2imdates(final_useful_unw['ifgdates'])
        date_format = "%Y%m%d"
        period = datetime.strptime(final_imdates[-1], date_format) - datetime.strptime(final_imdates[0], date_format)
        period = period.days/365.25 #used data period

        with open(gap_infofile, "w") as f:
            print('{}-{},{:.2f},{}'.format(final_imdates[0],final_imdates[-1],period,len(final_useful_unw)), file=f) #first/last dates and period [years]
            for i in range(len(ifg_gap)):
                if i > 0:
                    print('gap {} ifgs {}'.format(i,ifg_gap[i]-1), file=f) # if i>0, ifgs -1 (not include first one)
                else:
                    print('gap {} ifgs {}'.format(i,ifg_gap[i]), file=f) #i=0
        
        print('gap_info_after12.txt is created')
        ## Read bperp data or dummy
        bperp_file = os.path.join(ifgdir, 'baselines')LiCSBAS121_gap_identify.pyap.png')
        plot_lib.plot_network(ifgdates_all, bperp_all, bad_ifg_all, pngfile_nogap, plot_bad=False)


    #store all the folders under the current directory start with 1 in a list
    folders =  [i for i in os.listdir(os.getcwd()) if i.startswith('1') and len(i)==17]
    folders = [os.path.abspath(i) for i in folders]

    for folder in folders:

        #print the current folder name for checking
        print('{} will be processed'.format(os.path.basename(folder)))
        ifgdir = os.path.join(folder,'GEOCml_mask')
        tsadir = os.path.join(folder,'TS_GEOCml')
        gap_identify(ifgdir, tsadir)

if __name__ == '__main__':
    main() 