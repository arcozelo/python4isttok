
from sdas.core.LoadSdasData import LoadSdasData
from sdas.core.StartSdas import StartSdas
import numpy
import sys
from special_mean_val import special_mean_val
from exposure_time import exposure_time
from period_counter import period_counter
import xmlrpclib

#####################################################################
densthresh=2.e18
iplthresh=1.e3
martethresh=10
plok=1
deok=1
ivok=1
#####################################################################

client = StartSdas()

if len(sys.argv) < 2 :
    shotnr = client.searchMaxEventNumber('0x0000')	
else :
    shotnr = int(sys.argv[-1])

plasma_curr_channelID='POST.PROCESSED.IPLASMA'; # Unique Identifier for plasma current
plasma_dens_channelID='POST.PROCESSED.DENSITY'; # Unique Identifier for plasma density
marte_power_channelID='MARTE_NODE_IVO3.DataCollection.Channel_105'; #Marte channel for the power supply

print '\nSHOT #'+str(shotnr)+'\n'
print 'Loading data'

try:
    [iplasma,iplasma_times] = LoadSdasData(client, plasma_curr_channelID, shotnr);
    plok=numpy.all(numpy.isfinite(iplasma))
except xmlrpclib.Fault:
    print 'DATA NOT READY'
    plok=0
try:
    [dens,dens_times] =       LoadSdasData(client, plasma_dens_channelID, shotnr);
    deok=numpy.all(numpy.isfinite(dens))  # check if all finite
except xmlrpclib.Fault:
    print 'DATA NOT READY'
    deok=0
try:
    [marte,marte_times] =       LoadSdasData(client, marte_power_channelID, shotnr);
    ivok=numpy.all(numpy.isfinite(marte))  # check if all finite
except xmlrpclib.Fault:
    print 'DATA NOT READY'
    ivok=0


print 'Data loaded\n'


if plok:
    print 'FROM IPLASMA   ( thresh',iplthresh,')'
    exposure_time(numpy.abs(iplasma),iplasma_times,iplthresh)
    print 'Mean current {0:.3f} kA'.format(special_mean_val(numpy.abs(iplasma),iplthresh)/1e3)
    iplasma_periods = period_counter(numpy.abs(iplasma),iplthresh)
    print 'I counted '+str(iplasma_periods)+' periods'
else:
    print 'NO IPLASMA DATA'	

print ''

if deok:
    print 'FROM DENSITY   ( thresh',densthresh,')'
    exposure_time(dens,dens_times,densthresh)
    print 'Mean density {0:.2e} m'.format(special_mean_val(dens,densthresh))+u'\u207b\u00b3'
    dens_periods = period_counter(dens,densthresh)
    print 'I counted '+str(dens_periods)+' periods'
else:
    print 'NO DENSITY DATA'

print ''

if ivok:
    print 'FROM MARTE'
    marte_periods = period_counter(abs(marte),martethresh,numpy.append(numpy.ones(10),numpy.zeros(1)))
    print 'I counted '+str(marte_periods)+' periods'
else:
    print 'NO MARTE DATA'

if ivok and plok and deok:
    print '\nSucess rate was '+str(iplasma_periods)+'/'+str(marte_periods)
    if iplasma_periods==marte_periods:
        print '!!!CONGRATULATIONS!!!'
    elif iplasma_periods <= marte_periods/2:
        print '!!!BOOOOOO!!!'

print '\n'

