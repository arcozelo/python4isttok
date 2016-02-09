from sdas.core.LoadSdasData import LoadSdasData
from sdas.core.StartSdas import StartSdas
import numpy
import sys
from pyISTTOK.special_mean_val import special_mean_val
from pyISTTOK.exposure_time import exposure_time
from pyISTTOK.period_counter import period_counter
from get_shot_report import get_shot_report
import xmlrpclib

from pymouse import PyMouse
from pykeyboard import PyKeyboard
import time

#####################################################################
##                  SDAS ACCESS                                    ##
#####################################################################

if len(sys.argv) < 2 :
    relevant_data = get_shot_report()
else :
    relevant_data = get_shot_report(int(sys.argv[-1]))

if relevant_data == -1:
    exit()

[shotnr,iplasma_mean_val,dens_mean_val,iplasma_shot_time,iplasma_periods,marte_periods] = relevant_data;

inputy = raw_input("Press Enter to continue into the auto filler...")
if inputy !='' : exit()
#####################################################################
##                  AUTO FILLER                                    ##
#####################################################################

m = PyMouse()
k = PyKeyboard()

timer_max = 50;

prev_posi = (0,0);
oldr_posi = (0,0);
mouse_ready = False;

for i in range(timer_max):
    curr_posi = m.position()
    print 'Mouse at '+str(curr_posi)+'(timeout in '+str(i+1)+'/'+str(timer_max)+')'
    if curr_posi == prev_posi == oldr_posi:
        mouse_ready = True;
        break
    else:
        oldr_posi = prev_posi;
        prev_posi = curr_posi;
    time.sleep(0.5)

if mouse_ready:
    print "I'm going to click at"+str(curr_posi)
    m.click(m.position()[0],m.position()[1])
    time.sleep(0.5)

    # Shot number
    k.type_string(str(shotnr))
    k.tap_key(k.tab_key)
    #Iplasma in kA
    k.type_string('{0:.2f}'.format(iplasma_mean_val))
    k.tap_key(k.tab_key)
    #density in *1e18m-3
    k.type_string('{0:.2f}'.format(dens_mean_val))
    k.tap_key(k.tab_key)
    #duration in ms
    k.type_string(str(int((iplasma_shot_time//25)*25)))
    k.tap_key(k.tab_key)

    #Shot comments
    k.type_string('Sn-spectra, ')
    k.type_string('Sn cold at a)XXXX cm. ')
    k.type_string('P_ed)XXXX . ')
    tmp_str = str(iplasma_periods)+'&'+str(marte_periods)+' cycles'
    k.type_string(tmp_str)
    k.tap_key(k.tab_key)
    #k.tap_key(k.enter)
