
from sdas.core.LoadSdasData import LoadSdasData
from sdas.core.StartSdas import StartSdas
import numpy
import sys
import time
from pyISTTOK.special_mean_val import special_mean_val
from pyISTTOK.exposure_time import exposure_time
from pyISTTOK.period_counter import period_counter
import xmlrpclib

#####################################################################
##                  GLOBAL VARIABLES                               ##
#####################################################################
iplasma_threshold=0.5e3
dens_threshold=1.e18
marte_threshold=100
#####################################################################


def get_shot_report(*argv):

    #####################################################################
    ##                  IMPORTAN FLAGS                                 ##
    #####################################################################
    iplasma_ok=0
    dens_ok=0
    marte_ok=0

    #####################################################################
    ##                  VARIABLES                                      ##
    #####################################################################
    waited_time = 0
    fluffytron={0: "|", 1: "/", 2: "-", 3: "\\"}

    client = StartSdas()

    if len(argv) < 1 :
        shotnr = client.searchMaxEventNumber('0x0000')
    else :
        shotnr = int(argv[-1])

    plasma_curr_channelID='POST.PROCESSED.IPLASMA'; # Unique Identifier for plasma current
    plasma_dens_channelID='POST.PROCESSED.DENSITY'; # Unique Identifier for plasma density
    marte_power_channelID='MARTE_NODE_IVO3.DataCollection.Channel_105'; #Marte channel for the power supply

    print '\nSHOT #'+str(shotnr)+'\n'
    print '\nLoading data, CTRL-C to interrupt'
    while(True):
        if iplasma_ok==0:
            try:
                [iplasma,iplasma_times] = LoadSdasData(client, plasma_curr_channelID, shotnr);
                iplasma_ok=numpy.all(numpy.isfinite(iplasma))
            except xmlrpclib.Fault:
                iplasma_ok=0
        if dens_ok ==0:
            try:
                [dens,dens_times] = LoadSdasData(client, plasma_dens_channelID, shotnr);
                dens_ok=numpy.all(numpy.isfinite(dens))  # check if all finite
            except xmlrpclib.Fault:
                dens_ok=0
        if marte_ok==0:
            try:
                [marte,marte_times] = LoadSdasData(client, marte_power_channelID, shotnr);
                marte_ok=numpy.all(numpy.isfinite(marte))  # check if all finite
            except xmlrpclib.Fault:
                marte_ok=0
        if dens_ok and iplasma_ok and marte_ok :
            print '\nData loaded\n'
            break

        try:
        	print fluffytron[waited_time % 4]+' '+'{0:02d}'.format(waited_time)+'s',
        	print ' PLASMA CURRENT DATA:',
        	if iplasma_ok : print 'READY',
        	else : print 'NOT READY',
        	print ' DENSITY DATA:',
        	if dens_ok : print 'READY',
        	else : print 'NOT READY',
        	print ' MARTE CONTROL:',
        	if marte_ok : print 'READY',
        	else : print 'NOT READY',
        	print '  \r',
        	sys.stdout.flush()
        	time.sleep(1)
        	waited_time += 1
        except KeyboardInterrupt:
            return -1;


    if iplasma_ok:
        print 'FROM IPLASMA   ( thresh',iplasma_threshold,')'
        iplasma_shot_time = exposure_time(numpy.abs(iplasma),iplasma_times,iplasma_threshold)
        print 'There was '+str(iplasma_shot_time)+' ms of plasma ('+str(int(((iplasma_shot_time)//25)*25))+' ms)'
        iplasma_mean_val = special_mean_val(numpy.abs(iplasma),iplasma_threshold)/1.e3
        print 'Mean current {0:.3f} kA'.format(iplasma_mean_val)
        iplasma_periods = period_counter(numpy.abs(iplasma),iplasma_threshold)
        print 'I counted '+str(iplasma_periods)+' periods ('+str(int((iplasma_shot_time)//25))+')'
    else:
        print 'NO IPLASMA DATA'

    print ''

    if dens_ok:
        print 'FROM DENSITY   ( thresh',dens_threshold,')'
        dens_shot_time = exposure_time(dens,dens_times,dens_threshold)
        print 'There was '+str(dens_shot_time)+' ms of plasma ('+str(int(((dens_shot_time)//25)*25))+' ms)'
        dens_mean_val = special_mean_val(dens,dens_threshold)/1e18;
        print 'Mean density {0:.2e} m'.format(dens_mean_val*1e18)+u'\u207b\u00b3'
        dens_periods = period_counter(dens,dens_threshold)
        print 'I counted '+str(dens_periods)+' periods ('+str(int((dens_shot_time)//25))+')'
    else:
        print 'NO DENSITY DATA'

    print ''

    if marte_ok:
        print 'FROM MARTE'
        marte_periods = period_counter(abs(marte),marte_threshold,numpy.append(numpy.ones(10),numpy.zeros(1)))
        print 'I counted '+str(marte_periods)+' periods'
    else:
        print 'NO MARTE DATA'

    if marte_ok and iplasma_ok and dens_ok:
        print '\nSucess rate was '+str(iplasma_periods)+'/'+str(marte_periods)
        if iplasma_periods==marte_periods:
            print '!!!CONGRATULATIONS!!!'
        elif iplasma_periods <= marte_periods/2:
            print '!!!BOOOOOO!!!'

    print '\n'

    return shotnr,iplasma_mean_val,dens_mean_val,iplasma_shot_time,iplasma_periods,marte_periods;


if __name__ == '__main__':
    if len(sys.argv) < 2 :
        get_shot_report()
    else :
        get_shot_report(int(sys.argv[-1]))
